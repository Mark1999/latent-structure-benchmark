# OPS-T5: Collapsible raw transcript panel — Architect plan

**Task ID:** OPS-T5
**Author:** Architect agent
**Date:** 2026-05-02
**Status:** Awaiting CDA SME light-touch review (same pattern as OPS-T4 wireframes verdict)

## 1. Summary

Add a fourth section to the OPS-T4 detail view that exposes the verbatim three-step dialog (freelist, pile-sort, interview) for the selected informant. Each step gets its own collapsed-by-default `st.expander` containing prompt, extended-thinking output (when present), response, and a small metadata block (prompt_version, input/output tokens, latency, stop_reason). The section sits below decline events so the existing visual rendering (piles, pile labels) remains the headline and the raw transcript is the drill-down. Read-only, no new file I/O — the three step records are already on the `InformantRecord` returned by `lib/loader.py`.

## 2. Affected packages and files

| Path | Change |
|---|---|
| `/opt/lsb-agent/apps/ops_dashboard/lib/detail.py` | Add `TranscriptStep` dataclass and pure helper `build_step_transcripts(record)` returning `list[TranscriptStep]` of length 3 (freelist, pile_sort, interview). |
| `/opt/lsb-agent/apps/ops_dashboard/app.py` | Add Section 4 ("Raw transcripts") below decline events. Three `st.expander` widgets, collapsed by default. Use `st.code(..., language=None)` or `st.text` for verbatim bodies (no markdown re-interpretation). Render the SME-mandated section disclaimer above the three expanders. |
| `/opt/lsb-agent/tests/test_ops_dashboard_detail.py` | Add `TestBuildStepTranscripts` with cases for: all-three-populated, empty-thinking-on-one-or-more-steps, long-multi-KB body preserved verbatim, deterministic output across two calls, forbidden-vocabulary regex scan on rendered string output. |
| `/opt/lsb-agent/tests/test_ops_dashboard_app_static.py` | Add static-text assertions for the SME-mandated section disclaimer and the three expander labels. |

No changes to: `cdb_core/schemas.py`, `loader.py`, `picker.py`, `apply_filters`, fixtures, or any data file.

## 3. Ordered task list (single Coder-sized task)

This is one task, one commit. Work order inside the task:

1. **Helper + dataclass in `lib/detail.py`.**
   - Add `TranscriptStep` dataclass with fields: `step_name: str` (one of `"freelist"`, `"pile_sort"`, `"interview"`), `step_label: str` (display label for the expander, e.g. `"Step 1 — Freelist"`), `prompt_version: str`, `prompt_verbatim: str`, `thinking_verbatim: str` (empty string when absent), `has_thinking: bool` (computed: `bool(thinking_verbatim.strip())`), `response_verbatim: str`, `input_tokens: int`, `output_tokens: int`, `latency_ms: int`, `stop_reason: str`.
   - Add `build_step_transcripts(record: InformantRecord) -> list[TranscriptStep]` that returns exactly three steps in CDA order. No filtering, no re-summarization. Empty thinking is preserved as empty (not None) — `has_thinking` is the gate the renderer reads.
2. **Section 4 in `app.py`.** Below decline events:
   - `st.markdown("### Raw transcripts")`
   - SME-mandated section disclaimer (proposed wording, subject to SME edit — see §5):
     *"Verbatim model output below — prompts as sent, model output text as returned. Extended-thinking text is the model's literal output, not a claim about internal reasoning."*
   - Three expanders, all `expanded=False`, in CDA order:
     - `"Step 1 — Freelist transcript"`
     - `"Step 2 — Pile-sort transcript"`
     - `"Step 3 — Interview / pile-naming transcript"`
   - Inside each expander, render in this fixed order: prompt header → `st.code(prompt_verbatim, language=None)` → thinking subheader → `st.code(thinking_verbatim, language=None)` if `has_thinking` else `st.caption("No extended-thinking output for this step.")` → response subheader → `st.code(response_verbatim, language=None)` → small metadata footer (single line) showing `prompt_version`, `input_tokens`, `output_tokens`, `latency_ms`, `stop_reason`.
3. **Tests.** New `TestBuildStepTranscripts` class in `test_ops_dashboard_detail.py`. New static-text assertions in `test_ops_dashboard_app_static.py` for the section disclaimer and expander labels.
4. **Local verification.** `uv run pytest tests/test_ops_dashboard_detail.py tests/test_ops_dashboard_app_static.py && uv run ruff check . && uv run mypy packages/`. Manual smoke: refresh the running Streamlit dashboard, select any informant, scroll to Section 4, confirm three expanders render and expand cleanly.

### Acceptance criteria

- A1. `build_step_transcripts(record)` returns exactly three `TranscriptStep` objects in CDA order regardless of input.
- A2. When a step's `thinking_verbatim` is `""` or whitespace-only, `has_thinking` is `False` and the renderer shows the placeholder caption rather than collapsing the subsection away.
- A3. Each expander shows: prompt → thinking (or placeholder) → response → metadata, in that fixed order.
- A4. All three verbatim bodies render through `st.code(..., language=None)` (or `st.text`) — no markdown re-interpretation.
- A5. Section 4 appears strictly below decline events. Sections 1–3 are unchanged.
- A6. Multi-KB bodies (≥10 KB) render without truncation.
- A7. The CDA-SME-approved section disclaimer text appears verbatim in `app.py` (static-text test enforces this).
- A8. `lib/detail.py` adds no new imports outside `cdb_core.schemas` and stdlib `dataclasses`. No LLM client imports, no Streamlit imports (helper stays pure).
- A9. All existing OPS-T4 tests still pass unmodified.
- A10. Forbidden-vocabulary regex scan on every literal string added to `lib/detail.py` and `app.py` returns zero hits.
- A11. `ruff check`, `mypy packages/`, and the existing pytest suite all pass.

## 4. Schema changes required

**None.** No edits to `cdb_core/schemas.py`. No `DATA_DICTIONARY.md` update required. The three step records (`FreelistRecord`, `PileSortRecord`, `InterviewRecord`) already expose every field this task surfaces.

## 5. CDA SME review required: **YES (light-touch, pre-implementation)**

Reason: this task generates new copy referring to "extended-thinking" and renders verbatim model text. The §1.5 framing rules apply to internal ops dashboard text the same way they apply to the public dashboard (CLAUDE.md §7 forbidden vocabulary is universal).

### Specific questions for the SME (so a single verdict file suffices)

- **Q1 — Section disclaimer wording.** Proposed: *"Verbatim model output below — prompts as sent, model output text as returned. Extended-thinking text is the model's literal output, not a claim about internal reasoning."* Approve, edit, or reject.
- **Q2 — Subheader label for thinking trace inside each expander.** Three options:
  - (a) "Thinking trace (verbatim)" — matches the existing OPS-T4 freelist thinking expander label.
  - (b) "Extended-thinking output (verbatim)" — more technically accurate, breaks consistency.
  - (c) "Reasoning tokens (verbatim)" — provider-API-vocabulary, breaks consistency.
  - Architect recommends (a) on consistency grounds; SME to confirm or override.
- **Q3 — Empty-thinking placeholder text.** Proposed: *"No extended-thinking output for this step."* Approve or edit.
- **Q4 — Section title.** Proposed: "Raw transcripts" (matches Mark's verbatim "full dialog"). Acceptable, or prefer "Verbatim transcripts" / "Step-by-step transcripts" / other?
- **Q5 — Sensitive-content concern.** The prompts are versioned templates already destined for the open data bundle; the responses are already in `data/raw/informants.jsonl` (open-bundle source). No PII risk. Confirm SME concurs and no redaction is required for internal-only display.
- **Q6 — Step naming for the third step.** Mark's request named only freelist + pile-sort. Architect recommends including step 3 (interview / pile-naming) — same conversational pattern, produces the pile labels already shown in OPS-T4. Confirm.

A single PASS / PASS-WITH-NOTES verdict against these six questions unblocks the Coder. FAIL on any item bounces to the Architect for rewording before dispatch.

## 6. UI/UX agent review required: **NO**

Per `feedback_visual_inspection.md`, the internal ops dashboard is exempt from `DESIGN_SYSTEM.md` gating.

## 7. Dependency order

Depends on OPS-T4 being merged (it is — commits 087a455, c740292, edf477f). No other dependencies.

## 8. Reading list for the Coder

1. `CLAUDE.md` §6 (binding rules), §7 (forbidden vocabulary), §9 pitfalls #2 and #7.
2. `ARCHITECTURE.md` §1.5.4 (forbidden vocabulary), §3.2 (FreelistRecord, PileSortRecord, InterviewRecord schemas).
3. `apps/ops_dashboard/lib/detail.py` (existing helpers — pattern to follow).
4. `apps/ops_dashboard/app.py` (existing Sections 1–3 — Section 4 mirrors structure).
5. `tests/test_ops_dashboard_detail.py` (existing test patterns and `_freelist_record` / `_pilesort_record` / `_interview_record` builder helpers — reuse, do not duplicate).
6. `tests/test_ops_dashboard_app_static.py` (static-text assertion pattern to follow).
7. The CDA SME verdict file from this plan, once issued (Coder must reference it in the commit body).

## 9. Test strategy

- **Unit tests for `build_step_transcripts`** (in `tests/test_ops_dashboard_detail.py`):
  - Returns length-3 list always.
  - All three steps populated → all three `TranscriptStep` objects carry the right field values from the right step record.
  - Empty `thinking_verbatim` on freelist → `has_thinking=False` for that step, others unaffected.
  - Whitespace-only `thinking_verbatim` → `has_thinking=False` (mirrors OPS-T4 `build_thinking_trace` behavior).
  - Multi-KB prompt and response strings round-trip identically through the helper (verbatim invariant).
  - Determinism: two calls with the same record produce equal output.
  - Forbidden-vocabulary scan on every string field of every returned `TranscriptStep` for synthetic records that don't themselves contain forbidden tokens.
- **Static-text assertions** (in `tests/test_ops_dashboard_app_static.py`):
  - Section disclaimer fragment presence (verbatim, SME-approved wording).
  - Three expander labels present verbatim.
  - Empty-thinking placeholder text present verbatim.
  - Section title "### Raw transcripts" present.
- **No Streamlit live tests.** Same rationale as OPS-T4: Streamlit cannot be unit-tested by importing.
- **No real API calls.** All fixtures synthetic, constructed with the existing `_freelist_record` / `_pilesort_record` / `_interview_record` builders.

## 10. What Reviewer should verify

- R1 No LLM imports in any new code.
- R2 No new file I/O — `build_step_transcripts` reads only from the `InformantRecord` argument.
- R3 Forbidden-vocabulary scan on the diff returns zero hits.
- R4 Commit message follows Conventional Commits: `feat(ops): add raw transcript panel (OPS-T5)`.
- R5 Commit body references the CDA SME verdict file path under `docs/status/`.
- R6 No schema change to `cdb_core/schemas.py`.
- R7 `DATA_DICTIONARY.md` is *not* updated (correct — no schema change).
- R8 OPS-T4 sections 1–3 are byte-identical pre/post.
- R9 One commit, no bundling.

## 11. What Tester should verify

- All new unit tests pass.
- All OPS-T4 tests still pass unmodified.
- Manual smoke (Tester or Mark): refresh the Streamlit dashboard, select a record with non-empty thinking on at least one step, confirm the three expanders render correctly. Select a record with empty thinking on all three steps, confirm the placeholder caption renders.
- Multi-KB record (if present in `data/raw/informants.jsonl`) renders without truncation.
