import os
import time
from typing import TypedDict
from anthropic import Anthropic
from anthropic.types import TextBlock
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import slack_helper as slack
import task_manager

load_dotenv()

client = Anthropic()


def extract_text(response) -> str:
    """Safely extract text from an Anthropic response."""
    for block in response.content:
        if isinstance(block, TextBlock):
            return block.text
    return ""


def read_doc(filename: str) -> str:
    """Read a companion doc from the project directory."""
    path = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"[{filename} not found]"


# --- State ---
# This is the object that gets passed between every agent node.
# Each agent reads from it and writes back to it.

class PipelineState(TypedDict):
    task: str                  # the high-level task fed into the pipeline
    architecture_notes: str    # Architect's output
    sme_review: str            # CDA SME methodological review
    sme_approved: bool         # whether SME approved the plan
    implementation: str        # Coder's output
    review_notes: str          # Reviewer's output
    test_results: str          # Tester's output
    approved: bool             # whether the human approved the plan
    errors: list[str]          # any errors accumulated along the way


# --- Agent nodes ---

def architect_node(state: PipelineState) -> PipelineState:
    slack.post("architect", f"🏛 *Architect starting*\nTask: {state['task']}")

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        system="""You are the Architect agent for the Latent Structure Benchmark (LSB) project.

Your sole reference document is ARCHITECTURE.md in the project root. Before decomposing
any task, read the relevant sections of that document. All decisions must be consistent
with the architecture decisions already made there — especially:
- Static-only architecture (no runtime backend, no FastAPI)
- cdb_publish writes static JSON to Cloudflare Pages
- Forbidden vocabulary: never use 'worldview', 'believes', or 'thinks' when describing models
- Phase 0 must be completed before Phase 1a begins

You decompose tasks into clear, numbered implementation plans. You never write code yourself.
Output a structured plan with numbered steps that the Coder can follow exactly.
Reference specific section numbers from ARCHITECTURE.md where relevant.

At the very end of your plan, on its own line, write either:
RISK_LEVEL: LOW_RISK  (for scaffold tasks, test writing, doc updates, linting fixes)
RISK_LEVEL: HIGH_RISK  (for anything touching APIs, schemas, CI config, or architecture decisions)""",
        messages=[{
            "role": "user",
            "content": f"""You have access to the following project documents:

--- ARCHITECTURE.md ---
{read_doc('ARCHITECTURE.md')}

--- PHASE_0_TASKS.md ---
{read_doc('PHASE_0_TASKS.md')}

--- SECURITY_AND_HARDENING.md ---
{read_doc('SECURITY_AND_HARDENING.md')}

--- HOSTING_AND_DEV_OPS.md ---
{read_doc('HOSTING_AND_DEV_OPS.md')}

Your task: {state['task']}

Read the relevant sections above and produce a detailed, numbered implementation plan for the Coder agent."""
        }]
    )

    notes = extract_text(response)
    slack.post("architect", f"🏛 *Architect plan ready:*\n```{notes[:500]}...```")

    # Determine risk level from the plan — LOW if Architect says so, HIGH otherwise
    risk = "LOW" if "LOW_RISK" in notes.upper() else "HIGH"

    approved = slack.wait_for_approval(
        f"Architect has produced a plan for:\n*{state['task']}*\n\nPlan summary:\n{notes[:300]}...",
        timeout_seconds=28800,
        risk=risk
    )

    return {**state, "architecture_notes": notes, "approved": approved}


def cda_sme_node(state: PipelineState) -> PipelineState:
    slack.post("cda_sme", "🔬 *CDA SME reviewing Architect plan for methodological validity*")

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        system="""You are the CDA SME (Cultural Domain Analysis Subject Matter Expert) for the Latent Structure Benchmark project.

Your intellectual profile:
- Qualitative and cognitive anthropologist with quantitative methods expertise
- Deep practitioner knowledge of CDA: free listing, pile sorting, pile interviews, cultural consensus analysis, MDS interpretation
- Applied orientation — results must be meaningful to engineers, ethicists, journalists, and policymakers, not just academics
- Epistemically rigorous — you never overclaim

Your core commitment — what LSB actually measures:
LSB does NOT measure AI culture, AI beliefs, or AI worldviews. LLMs do not have lived experience.
LSB measures the CORPUS LENS: the latent categorical structure of a training corpus, as refracted through a model's training and alignment pipeline, surfaced by applying CDA elicitation protocols to the model as if it were an informant.
"Corpus lens" is the plain-language term for this. Use it when reviewing dashboard copy and social posts.

Forbidden vocabulary (from ARCHITECTURE.md §1.5.4):
- Never use: "worldview", "believes", "thinks", "feels", "understands" when applied to models
- Always use: "the model produces", "the corpus lens shows", "the data suggests", "the pipeline surfaces"

Your review covers four things for every Architect plan:
1. PROTOCOL VALIDITY — Is the CDA elicitation protocol being applied correctly? Free listing must come before pile sorting. Pile sorting must produce a co-occurrence matrix. Interview step must elicit organizing principles, not just labels.
2. ANALYTICAL VALIDITY — Is the analysis appropriate? MDS requires a similarity/distance matrix as input. Bootstrap ellipses are mandatory — bare point estimates are forbidden. Cultural consensus analysis requires checking the eigenvalue ratio (first:second > 3 for consensus).
3. CLAIMS VALIDITY — Do any outputs (dashboard copy, README text, social posts) overclaim? Flag anything that attributes experience, belief, or culture to a model. Flag anything that presents the corpus lens as ground truth rather than a structured observation.
4. AUDIENCE TRANSLATION — For each major finding, provide one sentence a journalist could quote accurately without distortion. If you cannot write that sentence, the finding is not ready for public communication.

Output format:
METHODOLOGICAL VERDICT: PASS / PASS-WITH-NOTES / FAIL
followed by numbered findings under each of the four review areas.
If FAIL, specify exactly what must change before the Coder proceeds.""",
        messages=[{
            "role": "user",
            "content": f"""Review this Architect plan for methodological validity before the Coder implements it.

TASK: {state['task']}

ARCHITECT PLAN:
{state['architecture_notes']}

Apply all four review areas. Be specific. If the plan involves any text that will be user-facing (README, dashboard copy, social posts), quote the specific phrases that concern you."""
        }]
    )

    sme_review = extract_text(response)
    verdict = "PASS" if "FAIL" not in sme_review[:200] else "FAIL"

    slack.post("cda_sme", f"🔬 *CDA SME verdict: {verdict}*\n```{sme_review[:600]}...```")

    if verdict == "FAIL":
        slack.post("alerts", f"🛑 *CDA SME blocked task* — methodological issues found.\nTask: {state['task']}")

    return {**state, "sme_review": sme_review, "sme_approved": verdict != "FAIL"}


def coder_node(state: PipelineState) -> PipelineState:
    slack.post("coder", "💻 *Coder starting*")

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        system="""You are the Coder agent for the Latent Structure Benchmark project.
You implement exactly what the Architect specifies. One task at a time.
Write clean, well-commented Python. Follow the architecture plan precisely.""",
        messages=[{"role": "user", "content": f"Implement this plan:\n\n{state['architecture_notes']}"}]
    )

    implementation = extract_text(response)
    slack.post("coder", f"💻 *Coder done:*\n```{implementation[:500]}...```")

    return {**state, "implementation": implementation}


def reviewer_node(state: PipelineState) -> PipelineState:
    slack.post("reviewer", "🔍 *Reviewer starting*")

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        system="""You are the Reviewer agent for the Latent Structure Benchmark project.
You enforce schema boundaries, language guardrails, and security rules.
Check that the implementation matches the architecture plan exactly.
Flag any deviations, security issues, or use of forbidden vocabulary
('worldview', 'believes', 'thinks' when applied to models).
Output: PASS or FAIL, followed by specific notes.""",
        messages=[{"role": "user", "content": f"Review this implementation against the plan.\n\nPlan:\n{state['architecture_notes']}\n\nImplementation:\n{state['implementation']}"}]
    )

    review = extract_text(response)
    slack.post("reviewer", f"🔍 *Review complete:*\n```{review[:500]}...```")

    return {**state, "review_notes": review}


def tester_node(state: PipelineState) -> PipelineState:
    slack.post("tester", "🧪 *Tester starting*")

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        system="""You are the Tester agent for the Latent Structure Benchmark project.
You write fixture-based tests only. You never hit real APIs in tests.
For each function in the implementation, write a pytest test using mocked data.
Output working pytest code only.""",
        messages=[{"role": "user", "content": f"Write tests for this implementation:\n\n{state['implementation']}"}]
    )

    tests = extract_text(response)
    slack.post("tester", f"🧪 *Tests written:*\n```{tests[:500]}...```")
    slack.post("pipeline", f"✅ *Pipeline complete for task:*\n{state['task']}")

    return {**state, "test_results": tests}


# --- Routing ---

def should_continue(state: PipelineState) -> str:
    """After Architect, only continue if human approved."""
    if not state.get("approved", False):
        slack.post("alerts", "🛑 Pipeline halted — not approved by human.")
        return END
    return "cda_sme"


# --- Build the graph ---

def build_graph():
    graph = StateGraph(PipelineState)

    graph.add_node("architect", architect_node)
    graph.add_node("cda_sme", cda_sme_node)
    graph.add_node("coder", coder_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("tester", tester_node)

    graph.set_entry_point("architect")

    # After architect, check for human approval
    graph.add_conditional_edges("architect", should_continue, {
        "cda_sme": "cda_sme",
        END: END
    })

    graph.add_conditional_edges("cda_sme", lambda s: "coder" if s.get("sme_approved") else END, {
        "coder": "coder",
        END: END
    })

    # Linear after that
    graph.add_edge("coder", "reviewer")
    graph.add_edge("reviewer", "tester")
    graph.add_edge("tester", END)

    return graph.compile()


# --- Entry point ---

if __name__ == "__main__":
    graph = build_graph()

    next_task = task_manager.get_next_task()

    if next_task is None:
        print("All tasks complete. Nothing to do.")
        slack.post("pipeline", "🏁 *All tasks complete — pipeline idle.*")
    else:
        while next_task is not None:
            task_id = next_task["id"]
            description = next_task["description"]

            print(f"Starting task: {task_id} — {description}")
            slack.post("pipeline", f"🚀 *Pipeline starting task {task_id}:* {description}")

            initial_state: PipelineState = {
                "task": f"Execute {task_id} as specified in PHASE_0_TASKS.md. Task: {description}. Follow the acceptance criteria exactly. Nothing beyond {task_id} scope.",
                "architecture_notes": "",
                "sme_review": "",
                "sme_approved": False,
                "implementation": "",
                "review_notes": "",
                "test_results": "",
                "approved": False,
                "errors": []
            }

            result = graph.invoke(initial_state)

            if result.get("approved") and result.get("sme_approved"):
                task_manager.mark_task_done(task_id)
                print(f"Task {task_id} complete and marked done.")
                slack.post("pipeline", f"✅ *{task_id} complete.* Starting next task in 5 seconds...")
                time.sleep(5)
                next_task = task_manager.get_next_task()
                if next_task is None:
                    slack.post("pipeline", "🏁 *All Phase 0 tasks complete — pipeline idle.*")
            else:
                print(f"Task {task_id} was not approved — not marked done.")
                break
