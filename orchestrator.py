import os
from typing import TypedDict, Annotated
from anthropic import Anthropic
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import slack_helper as slack

load_dotenv()

client = Anthropic()

# --- State ---
# This is the object that gets passed between every agent node.
# Each agent reads from it and writes back to it.

class PipelineState(TypedDict):
    task: str                  # the high-level task fed into the pipeline
    architecture_notes: str    # Architect's output
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
        system="""You are the Architect agent for the Latent Structure Benchmark project.
You decompose tasks into clear implementation plans. You never write code yourself.
Output a structured plan with numbered steps that the Coder can follow exactly.""",
        messages=[{"role": "user", "content": f"Decompose this task into an implementation plan:\n\n{state['task']}"}]
    )

    notes = response.content[0].text
    slack.post("architect", f"🏛 *Architect plan ready:*\n```{notes[:500]}...```")

    # Ask for human approval before handing off to Coder
    approved = slack.wait_for_approval(
        f"Architect has produced a plan for:\n*{state['task']}*\n\nPlan summary:\n{notes[:300]}..."
    )

    return {**state, "architecture_notes": notes, "approved": approved}


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

    implementation = response.content[0].text
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

    review = response.content[0].text
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

    tests = response.content[0].text
    slack.post("tester", f"🧪 *Tests written:*\n```{tests[:500]}...```")
    slack.post("pipeline", f"✅ *Pipeline complete for task:*\n{state['task']}")

    return {**state, "test_results": tests}


# --- Routing ---

def should_continue(state: PipelineState) -> str:
    """After Architect, only continue if human approved."""
    if not state.get("approved", False):
        slack.post("alerts", "🛑 Pipeline halted — not approved by human.")
        return END
    return "coder"


# --- Build the graph ---

def build_graph():
    graph = StateGraph(PipelineState)

    graph.add_node("architect", architect_node)
    graph.add_node("coder", coder_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("tester", tester_node)

    graph.set_entry_point("architect")

    # After architect, check for human approval
    graph.add_conditional_edges("architect", should_continue, {
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

    initial_state: PipelineState = {
        "task": "Create a hello_world.py file that prints 'LSB pipeline is operational'",
        "architecture_notes": "",
        "implementation": "",
        "review_notes": "",
        "test_results": "",
        "approved": False,
        "errors": []
    }

    print("Starting LSB pipeline...")
    slack.post("pipeline", "🚀 *LSB pipeline starting* — smoke test task running.")

    result = graph.invoke(initial_state)

    print("\n--- Pipeline complete ---")
    print(f"Task: {result['task']}")
    print(f"Approved: {result['approved']}")