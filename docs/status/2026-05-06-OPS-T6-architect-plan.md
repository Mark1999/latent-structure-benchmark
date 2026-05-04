# OPS-T6: QA badge + decline-classification surface — Architect plan

**Task ID:** OPS-T6
**Author:** Architect agent
**Date:** 2026-05-06
**Status:** Awaiting CDA SME light-touch review (same pattern as OPS-T4 / OPS-T5)

## 1. Summary

Elevate the QA pass/fail signal in the OPS-T4 detail view from a tiny boolean buried in a caption (`qa_passed: True`) to a prominent colored badge directly under the section subheader, surface `qa_notes` immediately under the badge when present, and add a compact decline-classification summary block above the existing decline-events section so Mark can see "what's the decline picture for this informant" without expanding every event card. No changes to any data file, no schema changes, no LLM imports, no new directory I/O.

This is the last task in the OPS dashboard track. Pattern matches OPS-T4 and OPS-T5: pure helper(s) in `lib/detail.py`, rendering in `app.py`, unit tests in `tests/test_ops_dashboard_detail.py`, static-text assertions in `tests/test_ops_dashboard_app_static.py`.

## 2. Affected packages and files

| Path | Change |
|---|---|
| `/opt/lsb-agent/apps/ops_dashboard/lib/detail.py` | Add `DeclineSummaryRow` dataclass (small projection over `DeclineDetail`) and pure helper `build_decline_summary(declines: list[DeclineDetail]) -> list[DeclineSummaryRow]`. No new imports beyond `dataclasses`. |
| `/opt/lsb-agent/apps/ops_dashboard/app.py` | (a) Add a colored QA badge block directly under the `st.subheader(f"Detail — ...")` line, above the existing caption. (b) Drop `qa_passed` from the caption (badge replaces it). (c) Render `qa_notes` block when non-empty (loud on FAIL, quiet on PASS). (d) Add new "Decline summary" compact block above the existing "### Decline events" section. (e) Keep existing detail rendering byte-identical below those additions. |
| `/opt/lsb-agent/tests/test_ops_dashboard_detail.py` | Add `TestBuildDeclineSummary` class. Reuse existing `_make_record` / `_make_decline_interview` builders. |
| `/opt/lsb-agent/tests/test_ops_dashboard_app_static.py` | Add `TestOPST6MandatedCopy` class. Verbatim assertions on badge text, `qa_notes` headers, no-declines wording, summary section title, summary column headers. |

No changes to: `cdb_core/schemas.py`, `lib/loader.py`, `lib/picker.py`, `apply_filters`, fixtures, or any data file. `DATA_DICTIONARY.md` is **not** updated (no schema change).

## 3. Ordered task list (single Coder-sized task)

One task, one commit. Internal work order:

1. **Schema confirmation pass (no edits).** Coder reads `packages/cdb_core/cdb_core/schemas.py` to confirm: (a) `qa_notes` is `str = ""` (default empty, not `None`), so `if rec.qa_notes:` is the right guard. (b) `DeclineInterview.originating_step` is `Literal["freelist", "pile_sort", "interview", "pre_session"]` and `originating_outcome_class` is the seven-value Literal already surfaced as raw strings in OPS-T4. No schema changes needed — both fields already flow through `find_decline_events` into `DeclineDetail`. The `DeclineInterview` schema does **not** carry a `decline_taxon` field (the user-facing summary needs the existing `originating_step` + `originating_outcome_class` pair, which is the closest thing the schema has to a taxon).

2. **Helper + dataclass in `lib/detail.py`.**
   - Add `DeclineSummaryRow` dataclass with fields:
     - `decline_interview_id: str`
     - `originating_step: str` (one of `"freelist"`, `"pile_sort"`, `"interview"`, `"pre_session"`)
     - `originating_outcome_class: str` (one of the seven Literal values)
     - `manual_classification: str | None` (the disposition, or None when no manual classification row joined)
     - `safety_attribution_subtype: str | None` (`"k_frame"` / `"k_vocab"` / None)
   - Add `build_decline_summary(declines: list[DeclineDetail]) -> list[DeclineSummaryRow]` that projects each `DeclineDetail` to its summary row, preserving input order. Pure, deterministic, no I/O. Exists as a separate helper rather than expanding `find_decline_events` so the verbose event view remains untouched.

3. **QA badge in `app.py`.** Replace the existing line:

   ```python
   st.subheader(f"Detail — `{_detail_id}`")
   st.caption(
       f"model_id: `{_rec.model_id}` | domain: `{_rec.domain_slug}` | "
       f"run_index: {_rec.run_index} | qa_passed: {_rec.qa_passed}"
   )
   ```

   with:

   ```python
   st.subheader(f"Detail — `{_detail_id}`")

   if _rec.qa_passed:
       st.markdown("**QA:** :green-background[**PASS**]")
   else:
       st.markdown("**QA:** :red-background[**FAIL**]")

   if _rec.qa_notes:
       if _rec.qa_passed:
           # Informational note on a passing record — keep quiet
           with st.expander("QA notes (informational)"):
               st.text(_rec.qa_notes)
       else:
           # Failing record — surface verbatim immediately under the badge
           st.error(f"**QA notes:** {_rec.qa_notes}")

   st.caption(
       f"model_id: `{_rec.model_id}` | domain: `{_rec.domain_slug}` | "
       f"run_index: {_rec.run_index}"
   )
   ```

   Notes: (i) `:green-background[...]` / `:red-background[...]` is a Streamlit colored-text-with-background markdown directive supported in 1.57. If the Coder finds it does not render in the pinned version (smoke test), fall back to plain `:green[**PASS**]` / `:red[**FAIL**]` (1.16+) — both are SME-approved alternatives. (ii) `qa_passed` is removed from the caption (the badge replaces it) — this is the only intentional copy regression in the existing caption. (iii) The expander on PASS-with-notes is a deliberate de-emphasis: passing records with notes are rare and informational; we don't want them to look like failures.

4. **Decline summary block in `app.py`.** Insert directly above the existing `st.markdown("### Decline events")` line:

   ```python
   st.markdown("### Decline summary")
   _summary_rows = build_decline_summary(_declines)
   if not _summary_rows:
       st.success("No decline events recorded for this informant.")
   else:
       st.caption(
           "*One row per decline event for this informant. "
           "Subtype labels (k_frame / k_vocab) are defined in "
           "docs/DECLINE_INTERVIEW_PROTOCOL.md.*"
       )
       _table_rows = [
           {
               "decline_interview_id": r.decline_interview_id,
               "originating_step": r.originating_step,
               "outcome_class": r.originating_outcome_class,
               "manual_classification": r.manual_classification or "—",
               "safety_subtype": r.safety_attribution_subtype or "—",
           }
           for r in _summary_rows
       ]
       st.table(_table_rows)
   ```

   Notes: (i) `st.table` is the right primitive — Mark needs to scan, not interact. (ii) The em-dash (`—`) for absent classifications avoids the empty-string visual collapse and is clearer than `None` in a table cell. (iii) The existing `### Decline events` block stays byte-identical below this.

5. **No-declines case in existing decline-events section.** The current code already renders `st.info("*No decline events recorded for this informant.*")` when `_declines` is empty. Per CDA SME Q4, change this to `st.success(...)` (green) to match the framing in §6. Otherwise byte-identical.

6. **Tests.** New `TestBuildDeclineSummary` class in `test_ops_dashboard_detail.py`. New `TestOPST6MandatedCopy` class in `test_ops_dashboard_app_static.py`. Details in §9.

7. **Local verification.** `uv run pytest tests/ && uv run ruff check . && uv run mypy packages/`. Manual smoke: refresh dashboard, select (a) a `qa_passed=True` informant with empty `qa_notes`, (b) a `qa_passed=True` informant with a non-empty `qa_notes` (if any exist; otherwise note as a fixture-only path), (c) a `qa_passed=False` informant — confirm badge color flips and `qa_notes` surfaces correctly. Select an informant with declines and an informant with no declines to confirm the summary block renders correctly in both states.

### Acceptance criteria

- A1. QA badge renders directly under the `Detail — {informant_id}` subheader, above the metadata caption. PASS shows green, FAIL shows red.
- A2. The metadata caption no longer contains `qa_passed: ...` (the badge replaces it).
- A3. When `qa_passed=False` and `qa_notes` is non-empty, the notes render verbatim in an `st.error` block immediately under the badge.
- A4. When `qa_passed=True` and `qa_notes` is non-empty, the notes render inside a collapsed `st.expander("QA notes (informational)")`.
- A5. When `qa_notes` is the empty string (the schema default), no notes block renders at all.
- A6. `build_decline_summary` is pure, deterministic, returns a list of `DeclineSummaryRow` projections in input order, and reads only from its argument.
- A7. The new `### Decline summary` section appears strictly above the existing `### Decline events` section. The existing decline-events rendering is byte-identical except for the `st.info` → `st.success` change in the no-declines branch (CDA SME Q4 binding).
- A8. The no-declines branch in both the summary block and the events section uses **`st.success`** with the SME-approved verbatim wording: *"No decline events recorded for this informant."*
- A9. The decline summary table has columns: `decline_interview_id`, `originating_step`, `outcome_class`, `manual_classification`, `safety_subtype`. Absent classifications render as `—` (em dash), not empty string, not `None`.
- A10. `lib/detail.py` adds no new imports beyond `dataclasses` (already imported). No LLM client imports. No Streamlit imports in the helper module (it stays pure).
- A11. All existing OPS-T4 / OPS-T5 tests pass unmodified.
- A12. Forbidden-vocabulary regex scan on every literal string added to `lib/detail.py` and `app.py` returns zero hits.
- A13. `ruff check`, `mypy packages/`, and the existing pytest suite all pass.

## 4. Schema changes required

**None.** No edits to `cdb_core/schemas.py`. `qa_passed`, `qa_notes`, `originating_step`, `originating_outcome_class`, and `decline_interview_id` already exist on `InformantRecord` and `DeclineInterview` respectively. Manual classification and safety subtype fields already flow through `find_decline_events` into `DeclineDetail` and need no plumbing changes. **No `DATA_DICTIONARY.md` update required** — Reviewer rule R7 is satisfied by absence of schema diff.

## 5. CDA SME review required: **YES (light-touch, pre-implementation)**

Reason: this task elevates QA pass/fail to a prominent visual badge and introduces new copy on a more-visible surface (decline summary block). §1.5 framing and §7 forbidden vocabulary apply universally — internal-only doesn't relax the rule. Pattern matches OPS-T4 / OPS-T5: a single short verdict resolves all questions and unblocks the Coder.

### Specific questions for the SME (so a single verdict file suffices)

- **Q1 — Badge wording.** Proposed: **`PASS`** (green) and **`FAIL`** (red), bold, prefixed with the literal label `**QA:**`. Three alternatives the SME can pick from:
  - (a) `**QA:** PASS` / `**QA:** FAIL` — recommended (matches the schema field name `qa_passed`, terse, scannable).
  - (b) `**QA:** Passed` / `**QA:** Failed` — more conversational.
  - (c) `**QA passed**` / `**QA failed**` — no separator, less explicit.
  Architect recommends (a). SME to confirm or override.

- **Q2 — `qa_notes` placement when `qa_passed=False`.** Proposed: render verbatim in an `st.error` block directly under the badge, no expander, no truncation. When `qa_passed=True` and notes are present (rare): collapsed `st.expander("QA notes (informational)")`. SME to confirm both renderings, edit the expander label, or specify a different scheme (e.g. always-collapsed, always-visible, etc.).

- **Q3 — Forbidden-vocabulary check on new copy.** New literals introduced: `QA`, `PASS`, `FAIL`, `QA notes`, `QA notes (informational)`, `Decline summary`, `decline_interview_id`, `originating_step`, `outcome_class`, `manual_classification`, `safety_subtype`, `No decline events recorded for this informant.`, the column-header caption text, and `Subtype labels (k_frame / k_vocab) are defined in docs/DECLINE_INTERVIEW_PROTOCOL.md.` Architect's read: none of these touch the §7 forbidden cluster. Confirm the SME concurs.

- **Q4 — No-declines wording.** Proposed verbatim: *"No decline events recorded for this informant."* — already PASS-approved in the OPS-T4 wireframe verdict (Q3 ruling) for the existing `### Decline events` section. OPS-T6 reuses the same wording in the new summary block AND changes the rendering primitive in the existing decline-events block from `st.info` (blue, neutral) to `st.success` (green, positive) to match the "absence is a clear positive state" framing per memory `project_failures_are_findings.md`. Approve, edit, or reject.

- **Q5 — Subtype label gloss.** The summary table renders `safety_attribution_subtype` values raw (`k_frame` / `k_vocab` / `—`). Mark hand-coded these and knows the meaning, but a future researcher reading the dashboard later will not. Proposed mitigation: a single one-line `st.caption` directly under the section title pointing at `docs/DECLINE_INTERVIEW_PROTOCOL.md` for definitions. Verbatim proposed wording: *"One row per decline event for this informant. Subtype labels (k_frame / k_vocab) are defined in docs/DECLINE_INTERVIEW_PROTOCOL.md."* Three alternatives if the SME prefers more or less:
  - (a) Caption pointing at the protocol doc (recommended — minimal, future-proof).
  - (b) Inline gloss in the column itself — e.g. `k_frame (frame-only safety)` — risks overclaim if the gloss drifts from the protocol doc.
  - (c) No gloss — relies on reader knowing.

- **Q6 — §1.5 framing concern from elevating QA pass/fail to a prominent badge.** Architect's read: `qa_passed` is a deterministic property of the run computed by `scripts/qa_check.py` — it is not a claim about the model's cognition, worldview, or quality. The badge is a metadata signal about the run, not about the subject. There is no §1.5 risk because the badge does not say anything about what the model "thinks" or "believes." Confirm the SME concurs that elevating this signal does not create a framing issue.

A single PASS / PASS-WITH-NOTES verdict against these six questions unblocks the Coder. FAIL on any item bounces to the Architect for rewording before dispatch.

## 6. UI/UX agent review required: **NO**

Per `feedback_visual_inspection.md`, the internal ops dashboard is exempt from `DESIGN_SYSTEM.md` gating.

## 7. Dependency order

Depends on OPS-T5 being merged (it is — commit `eb89b27`, 2026-05-02). No other dependencies. This is the final task in the OPS dashboard track.

## 8. Reading list for the Coder

1. `CLAUDE.md` §6 (binding rules), §7 (forbidden vocabulary), §9 pitfalls #2 and #7.
2. `ARCHITECTURE.md` §1.5.4 (forbidden vocabulary), §3.2 (`InformantRecord.qa_passed` / `qa_notes`, `DeclineInterview`).
3. `apps/ops_dashboard/lib/detail.py` (existing `DeclineDetail` dataclass and `find_decline_events` helper — pattern to mirror).
4. `apps/ops_dashboard/app.py` (existing detail view — Sections 1–4, the `_declines` flow, the `qa_passed` line in the caption).
5. `tests/test_ops_dashboard_detail.py` (existing `_make_record` / `_make_decline_interview` builders — reuse, do not duplicate; existing `TestFindDeclineEvents` and `TestBuildStepTranscripts` classes — pattern to mirror).
6. `tests/test_ops_dashboard_app_static.py` (`TestSMEMandatedCopy` and `TestOPST5MandatedCopy` patterns — pattern to mirror).
7. `docs/DECLINE_INTERVIEW_PROTOCOL.md` (referenced by the summary caption — Coder should at minimum confirm the doc exists and the link is correct; if not, the gloss caption text is updated to point at whatever the canonical protocol doc actually is, and the SME is informed).
8. The CDA SME verdict file from this plan, once issued (Coder must reference it in the commit body).

## 9. Test strategy

### Unit tests for `build_decline_summary` (in `tests/test_ops_dashboard_detail.py`)

- `test_empty_input_returns_empty_list`: empty `[]` → `[]`.
- `test_single_decline_no_classifications`: one `DeclineDetail` with both classification fields `None` → one `DeclineSummaryRow` with both fields `None`.
- `test_single_decline_with_manual_classification`: manual classification only → row carries `manual_classification`, `safety_attribution_subtype=None`.
- `test_single_decline_with_both_classifications`: manual + subtype both populated → row carries both.
- `test_multiple_declines_input_order_preserved`: three declines → three rows in input order.
- `test_originating_step_propagated`: each of the four valid `originating_step` literals (`"freelist"`, `"pile_sort"`, `"interview"`, `"pre_session"`) round-trips through the projection.
- `test_outcome_class_propagated`: at least one of the seven `originating_outcome_class` literals round-trips.
- `test_deterministic_output`: two calls on the same input produce equal output.
- `test_forbidden_vocabulary_in_summary_strings`: regex scan on every string field of every returned row using the existing `_FORBIDDEN_PATTERNS` list.

### Static-text assertions (in `tests/test_ops_dashboard_app_static.py`)

`TestOPST6MandatedCopy` class:

- `test_qa_badge_pass_text`: `**QA:** :green-background[**PASS**]` (or fallback `**QA:** :green[**PASS**]`) literal present in `app.py`.
- `test_qa_badge_fail_text`: `**QA:** :red-background[**FAIL**]` (or fallback `**QA:** :red[**FAIL**]`) literal present.
- `test_qa_caption_no_longer_carries_qa_passed`: assert `"qa_passed:"` is **not** present in `app.py` (the badge replaces it; this guards regression).
- `test_qa_notes_block_present`: assert the literals `"QA notes:"` and `"QA notes (informational)"` both present.
- `test_decline_summary_section_title`: `"### Decline summary"` literal present.
- `test_decline_summary_caption_q5_wording`: SME-approved gloss caption fragment present (verbatim once the SME approves Q5).
- `test_no_declines_success_wording`: `"No decline events recorded for this informant."` literal present.
- `test_no_declines_uses_st_success`: assert `st.success("No decline events recorded for this informant.")` literal present (covers the `st.info` → `st.success` change in both the summary block and the existing decline-events block; verifies CDA SME Q4 binding).
- `test_no_declines_does_not_use_st_info`: assert the rejected `st.info("*No decline events recorded for this informant.*")` literal is **not** present (regression guard on the framing change).

### What is **not** tested

- No live Streamlit rendering tests — same rationale as OPS-T4 / OPS-T5: Streamlit cannot be unit-tested by importing.
- No real API calls. All fixtures are synthetic, constructed via the existing builders.

## 10. What Reviewer should verify

- R1. No LLM imports in any new code.
- R2. No new file I/O — `build_decline_summary` reads only from its argument.
- R3. Forbidden-vocabulary scan on the diff returns zero hits.
- R4. Commit message follows Conventional Commits: `feat(ops): add QA badge + decline classification summary (OPS-T6)`.
- R5. Commit body references the CDA SME verdict file path under `docs/status/`.
- R6. No schema change to `cdb_core/schemas.py`.
- R7. `DATA_DICTIONARY.md` is **not** updated (correct — no schema change). Reviewer rule R7 is satisfied by absence.
- R8. OPS-T4 Sections 1, 2, 4 (freelist, pile-sort, raw transcripts) are byte-identical pre/post. Section 3 (decline events) changes only in the no-declines branch (`st.info` → `st.success`) per CDA SME Q4 binding.
- R9. The metadata caption no longer carries `qa_passed: ...` (the badge replaces it) — this is the only intentional caption regression.
- R10. One commit, no bundling.

## 11. What Tester should verify

- All new unit tests pass.
- All OPS-T4 and OPS-T5 tests still pass unmodified.
- Manual smoke (Tester or Mark): refresh the Streamlit dashboard, select (a) a `qa_passed=True` record with empty `qa_notes` — green badge, no notes block, no expander; (b) a `qa_passed=False` record (the project has at least three known FAILs from the empty-freelist propagation bug — see memory `project_phase4a1_empty_freelist_propagation.md`) — red badge, `st.error` qa_notes block visible verbatim; (c) a record with multiple declines — summary table renders with one row per decline, columns aligned with §3 step 4; (d) a record with no declines — both the summary block and the events section show the green `st.success` no-declines line (not blue `st.info`).
