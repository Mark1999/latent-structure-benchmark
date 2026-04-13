"""
LSB Orchestrator — LangGraph pipeline for the agent team.

This file is the runtime expression of ARCHITECTURE.md §5.1 (agent
responsibilities) and §5.4 (Slack channels). It runs the
Architect → CDA SME → (UI/UX if frontend) → Coder → Reviewer → Tester
pipeline against tasks pulled from task_manager.

Key architectural commitments this file honors:
  - Anthropic prompt caching on every static doc (ARCHITECTURE.md §6.2,
    binding cost-control rule). Each agent passes the docs it needs as
    cached content blocks; the per-task instructions come AFTER the
    cache breakpoint and are not cached.
  - Per-agent doc loading: each agent gets the binding docs relevant to
    its role, not just the Architect. Without this, the CDA SME, Coder,
    Reviewer, and Tester are all operating on system-prompt summaries
    of rules they cannot see.
  - The UI/UX agent (ARCHITECTURE.md v0.7 §5.1) is a frontend-only gate
    sitting between the CDA SME and the Coder.
  - Verdicts are parsed via regex against the structured verdict line
    each agent is asked to produce, not via substring search.
  - PASS-WITH-NOTES is a real verdict — notes are captured and passed
    forward to the next agent, not silently dropped.
  - Reviewer FAIL is enforced. The graph routes around the Tester on a
    Reviewer FAIL.

What this file deliberately does NOT do:
  - File-based approval workflow (currently still inline via Slack)
  - Tester→Coder loopback on test failures (still terminates the graph)
  - Static cache-control enforcement check (lives in a separate
    scripts/check_orchestrator_caching.py CI script, not in this file)

For the full pipeline shape, see CLAUDE.md §3 and ARCHITECTURE.md §5.1.
"""

import os
import re
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


# ─────────────────────────────────────────────────────────────────────
# Model assignments
# ─────────────────────────────────────────────────────────────────────
# Per ARCHITECTURE.md §5.1. Pulled into module-level constants so the
# version bump is one place, not five. The 4.6 strings are current as
# of April 2026; the orchestrator's billing dashboard confirms these
# are the latest available.

ARCHITECT_MODEL = "claude-opus-4-6"
CDA_SME_MODEL = "claude-opus-4-6"
UI_UX_MODEL = "claude-sonnet-4-6"
CODER_MODEL = "claude-sonnet-4-6"
REVIEWER_MODEL = "claude-sonnet-4-6"
TESTER_MODEL = "claude-sonnet-4-6"


# ─────────────────────────────────────────────────────────────────────
# Per-agent doc loading matrix
# ─────────────────────────────────────────────────────────────────────
# Each agent gets the binding docs relevant to its role. The order is
# stable across calls so the cache breakpoint creates a consistent
# prefix. CLAUDE.md and ARCHITECTURE.md come first because they're the
# most-cached documents in the project — every agent reads them.
#
# IMPORTANT: changing the order of these lists invalidates the cache
# for that agent. Don't reorder casually.

ARCHITECT_DOCS = [
    "CLAUDE.md",
    "ARCHITECTURE.md",
    "PHASE_0_TASKS.md",
    "docs/DATA_DICTIONARY.md",
    "SECURITY_AND_HARDENING.md",
    "HOSTING_AND_DEV_OPS.md",
    "PHASE_4C_CANDIDATE_SOURCES.md",
]

CDA_SME_DOCS = [
    "CLAUDE.md",
    "ARCHITECTURE.md",
    "docs/DATA_DICTIONARY.md",
    "PHASE_4C_CANDIDATE_SOURCES.md",
]

UI_UX_DOCS = [
    "CLAUDE.md",
    "ARCHITECTURE.md",
    "DESIGN_SYSTEM.md",
]

CODER_DOCS_BASE = [
    "CLAUDE.md",
    "ARCHITECTURE.md",
    "docs/DATA_DICTIONARY.md",
]

CODER_DOCS_FRONTEND = CODER_DOCS_BASE + ["DESIGN_SYSTEM.md"]

REVIEWER_DOCS_BASE = [
    "CLAUDE.md",
    "ARCHITECTURE.md",
    "SECURITY_AND_HARDENING.md",
    "docs/DATA_DICTIONARY.md",
]

REVIEWER_DOCS_FRONTEND = REVIEWER_DOCS_BASE + ["DESIGN_SYSTEM.md"]

TESTER_DOCS = [
    "CLAUDE.md",
    "ARCHITECTURE.md",
    "docs/DATA_DICTIONARY.md",
]


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────

def read_doc(filename: str) -> str:
    """
    Read a companion doc from the project directory.

    Hard-fails on missing files via Slack alert + raise. The previous
    behavior of returning a "[file not found]" placeholder string was a
    silent failure mode — the agent would proceed with hallucinated
    output. Better to crash loudly.
    """
    path = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        slack.post(
            "alerts",
            f"🛑 *Required doc missing:* `{filename}` — orchestrator cannot proceed. "
            f"Check that the file exists at `{path}`."
        )
        raise


def build_cached_content(static_docs: list[str], task_text: str) -> list[dict]:
    """
    Build a message content list with prompt caching on static docs.

    Each doc becomes a text content block. The LAST static doc carries
    the `cache_control={"type": "ephemeral"}` marker, which creates a
    single cache breakpoint covering all preceding docs as one stable
    prefix. The per-task instructions come AFTER the breakpoint and are
    not cached (they vary per call).

    Anthropic supports up to 4 cache breakpoints per request. We use 1
    because all the static docs are equally stable for any given agent
    role and there's no benefit to splitting them. If a doc-loading
    matrix grows past the point where one breakpoint is the right
    granularity, split this helper into a multi-breakpoint version.

    Per ARCHITECTURE.md §6.2 binding cost-control rule.
    """
    content = []
    for i, doc_path in enumerate(static_docs):
        block = {
            "type": "text",
            "text": f"<{doc_path}>\n{read_doc(doc_path)}\n</{doc_path}>",
        }
        # Mark only the LAST static doc — single breakpoint covers all
        # preceding blocks as one cached prefix.
        if i == len(static_docs) - 1:
            block["cache_control"] = {"type": "ephemeral"}
        content.append(block)

    # Per-task instructions come after the cache breakpoint. NOT cached.
    content.append({
        "type": "text",
        "text": task_text,
    })

    return content


def parse_verdict(text: str, label: str) -> tuple[str, str]:
    """
    Parse a structured verdict line from agent output.

    Looks for the literal `{label}: PASS|PASS-WITH-NOTES|FAIL` pattern
    anywhere in the text (not just the first 200 chars). Returns the
    verdict plus the trailing notes (everything after the verdict line),
    which are mandatory for PASS-WITH-NOTES per ARCHITECTURE.md §5.1.

    Verdict order matters in the regex: PASS-WITH-NOTES must be checked
    before PASS, otherwise PASS would match the prefix of PASS-WITH-NOTES.

    Returns ("UNKNOWN", "") if no verdict line is found. Callers should
    treat UNKNOWN as a hard failure — it means the agent didn't produce
    the expected output structure, which is itself a failure mode.
    """
    pattern = rf"{re.escape(label)}:\s*(PASS-WITH-NOTES|PASS|FAIL)"
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return ("UNKNOWN", "")

    verdict = match.group(1).upper()
    notes = ""

    if verdict == "PASS-WITH-NOTES":
        # Capture everything after the verdict line as the notes the
        # next agent must apply.
        notes = text[match.end():].strip()

    return (verdict, notes)


def parse_risk_level(notes: str) -> str:
    """
    Parse the Architect's RISK_LEVEL declaration via regex.

    Defaults to HIGH on any parse failure — when in doubt, require
    human approval. This matches the previous behavior but uses a
    proper regex instead of substring matching.
    """
    match = re.search(r"RISK_LEVEL:\s*(LOW_RISK|HIGH_RISK)", notes, re.IGNORECASE)
    if match and match.group(1).upper() == "LOW_RISK":
        return "LOW"
    return "HIGH"


def parse_task_type(notes: str) -> str:
    """
    Parse the Architect's TASK_TYPE declaration.

    Returns "FRONTEND" or "BACKEND". Defaults to BACKEND on parse
    failure — frontend tasks are the exception, not the rule, so the
    safer default is to skip the UI/UX gate when in doubt. The keyword
    fallback in `route_after_sme` catches frontend tasks the Architect
    forgets to label.
    """
    match = re.search(r"TASK_TYPE:\s*(FRONTEND|BACKEND)", notes, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return "BACKEND"


def safe_create(agent_name: str, **kwargs):
    """
    Wrap client.messages.create with Slack alerting on failure.

    The Anthropic SDK has built-in retry logic for transient errors;
    this wrapper handles the case where retries are exhausted or where
    the failure is non-transient (e.g., authentication, malformed
    request). Posts to #lsb-alerts before re-raising so the failure is
    visible in real time, not just in the orchestrator process logs.
    """
    try:
        return client.messages.create(**kwargs)
    except Exception as e:
        slack.post(
            "alerts",
            f"🛑 *{agent_name} API call failed* — `{type(e).__name__}`: {str(e)[:300]}"
        )
        raise


def extract_text(response) -> str:
    """Safely extract text from an Anthropic response."""
    for block in response.content:
        if isinstance(block, TextBlock):
            return block.text
    return ""


# ─────────────────────────────────────────────────────────────────────
# State
# ─────────────────────────────────────────────────────────────────────
# This is the object that gets passed between every agent node.
# Each agent reads from it and writes back to it.

class PipelineState(TypedDict):
    task: str                          # the high-level task fed into the pipeline
    task_type: str                     # FRONTEND or BACKEND, parsed from Architect output

    # Architect
    architecture_notes: str            # Architect's full output
    approved: bool                     # whether the human approved the plan

    # CDA SME
    sme_review: str                    # full SME output
    sme_verdict: str                   # PASS / PASS-WITH-NOTES / FAIL / UNKNOWN
    sme_approved: bool                 # convenience flag — True for PASS or PASS-WITH-NOTES
    sme_notes: str                     # mandatory notes from PASS-WITH-NOTES; empty otherwise

    # UI/UX (frontend tasks only)
    ui_ux_review: str
    ui_ux_verdict: str
    ui_ux_approved: bool
    ui_ux_notes: str

    # Coder
    implementation: str

    # Reviewer
    review_notes: str                  # full Reviewer output
    reviewer_verdict: str
    reviewer_approved: bool
    reviewer_notes: str

    # Tester
    test_results: str
    tester_verdict: str
    tester_approved: bool

    errors: list[str]                  # accumulated non-fatal errors


# ─────────────────────────────────────────────────────────────────────
# Agent nodes
# ─────────────────────────────────────────────────────────────────────

def architect_node(state: PipelineState) -> PipelineState:
    slack.post("architect", f"🏛 *Architect starting*\nTask: {state['task']}")

    task_text = f"""Your task: {state['task']}

Read the binding docs above and produce a detailed numbered implementation plan
for the next agent in the pipeline (CDA SME first, then UI/UX if frontend, then Coder).
Reference specific section numbers from ARCHITECTURE.md where relevant.

At the very end of your plan, on their own lines, write:
RISK_LEVEL: LOW_RISK or HIGH_RISK
TASK_TYPE: FRONTEND or BACKEND

LOW_RISK is for scaffold tasks, test writing, doc updates, linting fixes.
HIGH_RISK is for anything touching APIs, schemas, CI config, or architecture decisions.

FRONTEND is for any task touching apps/dashboard/, DESIGN_SYSTEM.md, components, or visual artifacts.
BACKEND is everything else."""

    response = safe_create(
        "Architect",
        model=ARCHITECT_MODEL,
        max_tokens=2000,
        system="""You are the Architect agent for the Latent Structure Benchmark (LSB) project.

Your sole reference documents are CLAUDE.md and ARCHITECTURE.md, plus the companion
docs loaded into your context. Before decomposing any task, read the relevant sections.
All decisions must be consistent with the architecture decisions already made there.

You decompose tasks into clear, numbered implementation plans. You never write code
yourself. Output a structured plan with numbered steps that the next agent can follow
exactly.

End every plan with RISK_LEVEL and TASK_TYPE declaration lines per the user instructions.""",
        messages=[{
            "role": "user",
            "content": build_cached_content(ARCHITECT_DOCS, task_text),
        }],
    )

    notes = extract_text(response)
    risk = parse_risk_level(notes)
    task_type = parse_task_type(notes)

    slack.post("architect", f"🏛 *Architect plan ready* (risk={risk}, type={task_type})\n```{notes[:500]}...```")

    approved = slack.wait_for_approval(
        f"Architect has produced a plan for:\n*{state['task']}*\n\n"
        f"Risk: {risk} · Type: {task_type}\n\nPlan summary:\n{notes[:300]}...",
        timeout_seconds=28800,
        risk=risk,
    )

    return {
        **state,
        "architecture_notes": notes,
        "approved": approved,
        "task_type": task_type,
    }


def cda_sme_node(state: PipelineState) -> PipelineState:
    slack.post("cda_sme", "🔬 *CDA SME reviewing Architect plan for methodological validity*")

    task_text = f"""Review this Architect plan for methodological validity before
the next agent in the pipeline implements it.

TASK: {state['task']}

ARCHITECT PLAN:
{state['architecture_notes']}

Apply all four review areas (protocol validity, analytical validity, claims validity,
audience translation). Be specific. If the plan involves any text that will be
user-facing (README, dashboard copy, social posts), quote the specific phrases that
concern you.

Output format — the verdict line MUST be on its own line, exactly as shown:
METHODOLOGICAL VERDICT: PASS
or
METHODOLOGICAL VERDICT: PASS-WITH-NOTES
or
METHODOLOGICAL VERDICT: FAIL

If PASS-WITH-NOTES, the notes that follow the verdict line are mandatory — the next
agent in the pipeline will be required to apply them."""

    response = safe_create(
        "CDA SME",
        model=CDA_SME_MODEL,
        max_tokens=2000,
        system="""You are the CDA SME (Cultural Domain Analysis Subject Matter Expert)
for the Latent Structure Benchmark project. You are the methodological gatekeeper
between the Architect and the Coder per ARCHITECTURE.md §5.1.

Your intellectual profile: qualitative and cognitive anthropologist with quantitative
methods expertise. Deep practitioner knowledge of CDA. Applied orientation. Epistemically
rigorous — you never overclaim.

Your core commitment — what LSB actually measures: LSB does NOT measure AI culture, AI
beliefs, or AI worldviews. LSB measures the CORPUS LENS as defined in ARCHITECTURE.md
§1.5.1. The §1.5.4 forbidden vocabulary table is binding on every piece of generated
text in this project.

Your review covers four areas for every Architect plan: PROTOCOL VALIDITY, ANALYTICAL
VALIDITY, CLAIMS VALIDITY, AUDIENCE TRANSLATION. The full definitions of these are in
ARCHITECTURE.md §5.1 — read them in your loaded context before reviewing.

Your verdict must be one of: PASS / PASS-WITH-NOTES / FAIL. PASS-WITH-NOTES is acceptable
but the notes you write are mandatory for the next agent to apply. FAIL bounces the plan
back to the Architect for rework.""",
        messages=[{
            "role": "user",
            "content": build_cached_content(CDA_SME_DOCS, task_text),
        }],
    )

    sme_review = extract_text(response)
    verdict, notes = parse_verdict(sme_review, "METHODOLOGICAL VERDICT")
    approved = verdict in ("PASS", "PASS-WITH-NOTES")

    slack.post("cda_sme", f"🔬 *CDA SME verdict: {verdict}*\n```{sme_review[:600]}...```")

    if verdict == "FAIL":
        slack.post("alerts", f"🛑 *CDA SME blocked task* — methodological issues found.\nTask: {state['task']}")
    elif verdict == "UNKNOWN":
        slack.post(
            "alerts",
            f"🛑 *CDA SME produced no parseable verdict* — treating as FAIL.\n"
            f"Task: {state['task']}\nFirst 300 chars: {sme_review[:300]}"
        )

    return {
        **state,
        "sme_review": sme_review,
        "sme_verdict": verdict,
        "sme_approved": approved,
        "sme_notes": notes,
    }


def ui_ux_node(state: PipelineState) -> PipelineState:
    """
    UI/UX agent — design conscience for frontend tasks only.

    Sits between the CDA SME and the Coder per ARCHITECTURE.md v0.7 §5.1.
    Owns DESIGN_SYSTEM.md. Reviews every frontend plan on four questions:
    OWID design fidelity, the 30-second journalist test, the researcher
    reproduce-and-cite test, and WCAG AA accessibility.
    """
    slack.post("ui_ux", "🎨 *UI/UX agent reviewing frontend plan*")

    sme_notes_section = (
        f"\n\nCDA SME NOTES (must be applied):\n{state['sme_notes']}\n"
        if state.get("sme_notes")
        else ""
    )

    task_text = f"""Review this Architect plan for design fidelity. The CDA SME has
already reviewed and approved it methodologically; your job is the visual and
accessibility layer.

TASK: {state['task']}

ARCHITECT PLAN:
{state['architecture_notes']}
{sme_notes_section}
Apply all four review questions. Be specific about which DESIGN_SYSTEM.md sections
apply. If the plan needs a visual decision the design system does not yet cover, your
verdict is FAIL — return the plan to the Architect with a note about which design
system section needs to be extended first.

Output format — the verdict line MUST be on its own line, exactly as shown:
DESIGN VERDICT: PASS
or
DESIGN VERDICT: PASS-WITH-NOTES
or
DESIGN VERDICT: FAIL

If PASS-WITH-NOTES, the notes that follow the verdict line are mandatory — the Coder
will be required to apply them."""

    response = safe_create(
        "UI/UX",
        model=UI_UX_MODEL,
        max_tokens=2000,
        system="""You are the UI/UX agent for the LSB project — the design conscience
of the frontend per ARCHITECTURE.md v0.7 §5.1. You sit between the CDA SME and the
Coder for FRONTEND tasks only. You own DESIGN_SYSTEM.md.

Review every frontend plan on four questions, all rooted in DESIGN_SYSTEM.md:
1. OWID design fidelity — does the plan match the design language, the design tokens,
   the typographic scale, and the article-with-embedded-explorer page model?
2. The 30-second journalist test — can a journalist arriving cold understand the
   finding within 30 seconds without reading the methodology page?
3. The researcher reproduce-and-cite test — does the researcher have everything they
   need to reproduce the finding (download CSV, get the citation, find the raw data,
   contribute their own grounding)?
4. WCAG AA accessibility — color + shape together, "Read as table" toggle, keyboard
   navigation, ARIA labels, focus indicators, screen reader summary.

Your verdict must be one of: PASS / PASS-WITH-NOTES / FAIL. PASS-WITH-NOTES is acceptable
but the notes you write are mandatory for the Coder to apply. FAIL bounces the plan
back to the Architect for rework — typically because the design system needs to be
extended before the plan can proceed.""",
        messages=[{
            "role": "user",
            "content": build_cached_content(UI_UX_DOCS, task_text),
        }],
    )

    review = extract_text(response)
    verdict, notes = parse_verdict(review, "DESIGN VERDICT")
    approved = verdict in ("PASS", "PASS-WITH-NOTES")

    slack.post("ui_ux", f"🎨 *UI/UX verdict: {verdict}*\n```{review[:600]}...```")

    if verdict == "FAIL":
        slack.post("alerts", f"🛑 *UI/UX agent blocked task* — design issues found.\nTask: {state['task']}")
    elif verdict == "UNKNOWN":
        slack.post(
            "alerts",
            f"🛑 *UI/UX agent produced no parseable verdict* — treating as FAIL.\n"
            f"Task: {state['task']}\nFirst 300 chars: {review[:300]}"
        )

    return {
        **state,
        "ui_ux_review": review,
        "ui_ux_verdict": verdict,
        "ui_ux_approved": approved,
        "ui_ux_notes": notes,
    }


def coder_node(state: PipelineState) -> PipelineState:
    slack.post("coder", "💻 *Coder starting*")

    is_frontend = state.get("task_type") == "FRONTEND"
    docs = CODER_DOCS_FRONTEND if is_frontend else CODER_DOCS_BASE

    # Aggregate any PASS-WITH-NOTES from upstream gates. The Coder is required
    # to apply these per ARCHITECTURE.md §5.1.
    notes_section = ""
    if state.get("sme_notes"):
        notes_section += f"\n\nCDA SME NOTES (mandatory):\n{state['sme_notes']}"
    if state.get("ui_ux_notes"):
        notes_section += f"\n\nUI/UX NOTES (mandatory):\n{state['ui_ux_notes']}"

    task_text = f"""Implement the following plan exactly as specified. One task at a
time. Do not exceed the task scope. If you find yourself wanting to fix something
outside the plan, stop and surface the question — do not improvise.

TASK: {state['task']}

ARCHITECT PLAN:
{state['architecture_notes']}
{notes_section}

Write clean, well-commented Python (or TypeScript for frontend tasks). Follow the
schemas in cdb_core/schemas.py exactly — never redefine types elsewhere. Reference
ARCHITECTURE.md and DATA_DICTIONARY.md from your loaded context as needed."""

    response = safe_create(
        "Coder",
        model=CODER_MODEL,
        max_tokens=4000,
        system="""You are the Coder agent for the Latent Structure Benchmark project.
You implement exactly what the Architect specifies. One task at a time.

You are bound by the 15 rules in CLAUDE.md §6. Read CLAUDE.md before starting any
task. Read cdb_core/schemas.py before touching any other file. For frontend tasks,
read DESIGN_SYSTEM.md and never invent visual decisions outside of it — if the
design system does not cover a question that comes up, stop and route the question
back to the UI/UX agent rather than guessing.

You write clean, well-commented code. You follow Conventional Commits format for
commit messages (feat/fix/chore/docs/test/refactor/ci/perf scoped to the affected
package). You never bundle multiple tasks into one PR.""",
        messages=[{
            "role": "user",
            "content": build_cached_content(docs, task_text),
        }],
    )

    implementation = extract_text(response)
    slack.post("coder", f"💻 *Coder done:*\n```{implementation[:500]}...```")

    return {**state, "implementation": implementation}


def reviewer_node(state: PipelineState) -> PipelineState:
    slack.post("reviewer", "🔍 *Reviewer starting*")

    is_frontend = state.get("task_type") == "FRONTEND"
    docs = REVIEWER_DOCS_FRONTEND if is_frontend else REVIEWER_DOCS_BASE

    task_text = f"""Review this implementation against the plan. Enforce the rules in
CLAUDE.md §6 and the Reviewer rules table in SECURITY_AND_HARDENING.md §9. Flag any
deviations, security issues, schema violations, or use of forbidden vocabulary from
ARCHITECTURE.md §1.5.4.

TASK: {state['task']}

PLAN:
{state['architecture_notes']}

IMPLEMENTATION:
{state['implementation']}

Output format — the verdict line MUST be on its own line, exactly as shown:
REVIEWER VERDICT: PASS
or
REVIEWER VERDICT: PASS-WITH-NOTES
or
REVIEWER VERDICT: FAIL

If PASS-WITH-NOTES, the notes that follow the verdict line are mandatory — they will
be passed to the Tester. FAIL blocks the implementation from proceeding to the
Tester at all."""

    response = safe_create(
        "Reviewer",
        model=REVIEWER_MODEL,
        max_tokens=2000,
        system="""You are the Reviewer agent for the Latent Structure Benchmark project.
You enforce the rules in CLAUDE.md §6 and the Reviewer rules table in
SECURITY_AND_HARDENING.md §9. Read both before reviewing any implementation.

The non-negotiable rules:
- Schemas only defined in cdb_core/schemas.py
- Layer boundaries respected (cdb_publish never imports cdb_collect; the dashboard
  never imports any cdb_* Python package; cdb_analyze never imports any LLM client)
- Prompt templates are versioned (never edit a published template in place)
- The §1.5.4 language guardrails — no "worldview", "believes", "thinks" applied to models
- InformantRecord and GroundingRef changes co-update DATA_DICTIONARY.md
- Frontend PRs carry a UI/UX agent verdict
- No secrets in committed files
- No dangerouslySetInnerHTML in the dashboard
- No CSP weakening without Architect sign-off
- No new dependency without Architect sign-off
- No edits to existing lines in data/raw/informants.jsonl

You issue a verdict: PASS / PASS-WITH-NOTES / FAIL. FAIL blocks the implementation.""",
        messages=[{
            "role": "user",
            "content": build_cached_content(docs, task_text),
        }],
    )

    review = extract_text(response)
    verdict, notes = parse_verdict(review, "REVIEWER VERDICT")
    approved = verdict in ("PASS", "PASS-WITH-NOTES")

    slack.post("reviewer", f"🔍 *Reviewer verdict: {verdict}*\n```{review[:600]}...```")

    if verdict == "FAIL":
        slack.post("alerts", f"🛑 *Reviewer blocked task* — implementation rejected.\nTask: {state['task']}")
    elif verdict == "UNKNOWN":
        slack.post(
            "alerts",
            f"🛑 *Reviewer produced no parseable verdict* — treating as FAIL.\n"
            f"Task: {state['task']}\nFirst 300 chars: {review[:300]}"
        )

    return {
        **state,
        "review_notes": review,
        "reviewer_verdict": verdict,
        "reviewer_approved": approved,
        "reviewer_notes": notes,
    }


def tester_node(state: PipelineState) -> PipelineState:
    slack.post("tester", "🧪 *Tester starting*")

    reviewer_notes_section = (
        f"\n\nREVIEWER NOTES (must be addressed in test coverage):\n{state['reviewer_notes']}\n"
        if state.get("reviewer_notes")
        else ""
    )

    task_text = f"""Write fixture-based tests for this implementation. Never hit real
APIs in tests. For each function in the implementation, write a pytest test using
mocked data from tests/fixtures/ following the conventions in tests/fixtures/README.md.

TASK: {state['task']}

IMPLEMENTATION:
{state['implementation']}
{reviewer_notes_section}

Output working pytest code only. End your output with:
TESTER VERDICT: PASS
or
TESTER VERDICT: FAIL

PASS means the tests are complete, runnable, and cover the implementation. FAIL means
something prevented you from writing adequate test coverage (the implementation has
no testable surface, the fixtures don't exist, etc.)."""

    response = safe_create(
        "Tester",
        model=TESTER_MODEL,
        max_tokens=2000,
        system="""You are the Tester agent for the Latent Structure Benchmark project.
You write fixture-based tests only. You never hit real APIs in tests.

You are bound by CLAUDE.md rule 10: no real model calls in tests. Use fixtures from
tests/fixtures/. The fixture convention is documented in tests/fixtures/README.md.

For Python packages you write pytest tests. For the dashboard you write vitest tests.

End every test output with a TESTER VERDICT line per the user instructions.""",
        messages=[{
            "role": "user",
            "content": build_cached_content(TESTER_DOCS, task_text),
        }],
    )

    tests = extract_text(response)
    verdict, _ = parse_verdict(tests, "TESTER VERDICT")
    approved = verdict in ("PASS", "PASS-WITH-NOTES")

    slack.post("tester", f"🧪 *Tester verdict: {verdict}*\n```{tests[:500]}...```")

    if verdict == "FAIL":
        slack.post(
            "alerts",
            f"🛑 *Tester could not produce adequate test coverage* — task incomplete.\n"
            f"Task: {state['task']}"
        )
    elif verdict == "UNKNOWN":
        # Tester verdict parsing failure is less severe than CDA SME / UI/UX / Reviewer
        # because the test code itself is the deliverable. Default to PASS but log it.
        slack.post(
            "tester",
            "⚠️ *Tester produced no parseable verdict* — defaulting to PASS. Mark should review."
        )
        approved = True

    if approved:
        slack.post("pipeline", f"✅ *Pipeline complete for task:*\n{state['task']}")

    return {
        **state,
        "test_results": tests,
        "tester_verdict": verdict,
        "tester_approved": approved,
    }


# ─────────────────────────────────────────────────────────────────────
# Routing
# ─────────────────────────────────────────────────────────────────────

# Frontend keyword fallback for the case where the Architect forgets to
# declare TASK_TYPE explicitly. Belt and suspenders alongside the
# parsed task_type from the Architect's plan.
_FRONTEND_KEYWORDS = (
    "apps/dashboard",
    "frontend",
    "design_system",
    "design system",
    "component",
    ".tsx",
    "react",
    "tailwind",
    "viz",
    "visualization",
    "chart",
    "p0-t10",  # P0-T10 is the dashboard scaffold task
)


def route_after_architect(state: PipelineState) -> str:
    """After Architect, only continue if human approved."""
    if not state.get("approved", False):
        slack.post("alerts", "🛑 Pipeline halted — Architect plan not approved by human.")
        return END
    return "cda_sme"


def route_after_sme(state: PipelineState) -> str:
    """
    After CDA SME, route to UI/UX for frontend tasks or Coder otherwise.

    Frontend detection: prefer the Architect's declared TASK_TYPE; fall
    back to keyword matching against the task description if the
    declaration is missing or unrecognized.
    """
    if not state.get("sme_approved"):
        return END

    declared_type = state.get("task_type", "BACKEND")
    if declared_type == "FRONTEND":
        return "ui_ux"

    # Keyword fallback
    task_lower = state.get("task", "").lower()
    if any(signal in task_lower for signal in _FRONTEND_KEYWORDS):
        slack.post(
            "ui_ux",
            "⚠️ Architect did not declare TASK_TYPE: FRONTEND, but task description "
            "suggests it's a frontend task. Routing through UI/UX gate as a precaution."
        )
        return "ui_ux"

    return "coder"


def route_after_ui_ux(state: PipelineState) -> str:
    """After UI/UX, only continue if approved."""
    if not state.get("ui_ux_approved"):
        return END
    return "coder"


def route_after_reviewer(state: PipelineState) -> str:
    """
    After Reviewer, only continue to Tester if Reviewer approved.

    A Reviewer FAIL terminates the graph. The previous version of this
    file unconditionally went from Reviewer to Tester regardless of
    verdict — that bug silently allowed rejected implementations to
    proceed. See the orchestrator review notes for the full discussion.
    """
    if not state.get("reviewer_approved"):
        return END
    return "tester"


# ─────────────────────────────────────────────────────────────────────
# Build the graph
# ─────────────────────────────────────────────────────────────────────

def build_graph():
    graph = StateGraph(PipelineState)

    graph.add_node("architect", architect_node)
    graph.add_node("cda_sme", cda_sme_node)
    graph.add_node("ui_ux", ui_ux_node)
    graph.add_node("coder", coder_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("tester", tester_node)

    graph.set_entry_point("architect")

    graph.add_conditional_edges("architect", route_after_architect, {
        "cda_sme": "cda_sme",
        END: END,
    })

    graph.add_conditional_edges("cda_sme", route_after_sme, {
        "ui_ux": "ui_ux",
        "coder": "coder",
        END: END,
    })

    graph.add_conditional_edges("ui_ux", route_after_ui_ux, {
        "coder": "coder",
        END: END,
    })

    graph.add_edge("coder", "reviewer")

    graph.add_conditional_edges("reviewer", route_after_reviewer, {
        "tester": "tester",
        END: END,
    })

    graph.add_edge("tester", END)

    return graph.compile()


# ─────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────

def make_initial_state(task_id: str, description: str) -> PipelineState:
    """Construct a fresh PipelineState for a new task."""
    return {
        "task": (
            f"Execute {task_id} as specified in PHASE_0_TASKS.md. "
            f"Task: {description}. Follow the acceptance criteria exactly. "
            f"Do not modify any file outside the {task_id} scope. If you find "
            f"yourself wanting to fix something else, stop and surface the question."
        ),
        "task_type": "BACKEND",  # default; Architect overrides via parsed declaration
        "architecture_notes": "",
        "approved": False,
        "sme_review": "",
        "sme_verdict": "",
        "sme_approved": False,
        "sme_notes": "",
        "ui_ux_review": "",
        "ui_ux_verdict": "",
        "ui_ux_approved": False,
        "ui_ux_notes": "",
        "implementation": "",
        "review_notes": "",
        "reviewer_verdict": "",
        "reviewer_approved": False,
        "reviewer_notes": "",
        "test_results": "",
        "tester_verdict": "",
        "tester_approved": False,
        "errors": [],
    }


def task_complete(result: PipelineState) -> bool:
    """
    A task is complete only when every gate it passed through approved.

    The Tester gate is the final word — if Tester approved, all upstream
    gates must have approved too (the graph terminates early on any
    upstream FAIL). Checking tester_approved is therefore sufficient.
    Belt-and-suspenders: also verify the upstream flags as a sanity
    check, in case future graph changes break the early-termination
    invariant.
    """
    return (
        result.get("approved", False)
        and result.get("sme_approved", False)
        and result.get("reviewer_approved", False)
        and result.get("tester_approved", False)
        # ui_ux_approved is only required for frontend tasks
        and (
            result.get("task_type") != "FRONTEND"
            or result.get("ui_ux_approved", False)
        )
    )


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

            initial_state = make_initial_state(task_id, description)
            result = graph.invoke(initial_state)

            if task_complete(result):
                task_manager.mark_task_done(task_id)
                print(f"Task {task_id} complete and marked done.")
                slack.post("pipeline", f"✅ *{task_id} complete.* Starting next task in 5 seconds...")
                time.sleep(5)
                next_task = task_manager.get_next_task()
                if next_task is None:
                    slack.post("pipeline", "🏁 *All Phase 0 tasks complete — pipeline idle.*")
            else:
                # Surface which gate(s) failed for the operator's benefit.
                gate_status = (
                    f"approved={result.get('approved')} "
                    f"sme={result.get('sme_verdict')} "
                    f"ui_ux={result.get('ui_ux_verdict', 'skipped')} "
                    f"reviewer={result.get('reviewer_verdict')} "
                    f"tester={result.get('tester_verdict')}"
                )
                print(f"Task {task_id} did not complete: {gate_status}")
                slack.post(
                    "pipeline",
                    f"❌ *{task_id} did not complete.* Gate status: {gate_status}"
                )
                break