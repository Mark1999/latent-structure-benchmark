# OPS-T7: QA-notes interpreter + decline banner + pile-sort source caption — Architect plan

**Task ID:** OPS-T7
**Author:** Architect agent
**Date:** 2026-05-06
**Predecessors:** OPS-T4 (detail view), OPS-T5 (raw transcripts), OPS-T6 (decline summary)
**Affected packages:** `apps/ops_dashboard/` only — no `cdb_core`/`cdb_collect`/`cdb_analyze`/`cdb_publish` changes
**Schema changes:** None. `cdb_core/schemas.py` and `DATA_DICTIONARY.md` are not touched.
**UI/UX gating:** Not applicable — internal ops dashboard, exempt from `DESIGN_SYSTEM.md` per memory `feedback_visual_inspection.md`.
**CDA SME gating:** Required (light touch). New copy + the qa-notes interpretation table are methodologically charged; questions Q1–Q6 below are for the SME's verdict file.
**Out of scope (recorded in memory):** Future cross-cuts across models × freelists × runs (memory `project_future_slicing.md`). Per-informant additions only.

---

## 1. Summary

Three Mark-requested UX additions to the LSB internal ops dashboard, all on the per-informant detail view:

1. **QA-notes interpreter.** Below the existing red `st.error` `qa_notes` block, render one yellow `st.warning` per parsed failure shorthand explaining (a) why the check failed in plain language and (b) the analysis impact.
2. **Decline-events banner at top.** When the selected informant has ≥1 decline event, render a top-of-detail-section banner directing the operator to the existing `Decline summary` and `Decline events` sections below.
3. **Pile-sort source caption.** Under the `### Pile-sort` subheader, add a one-line caption identifying whether the items being sorted came from this informant's own freelist or an external source.

Trigger conditions, locations, and wording are pinned below for SME verbatim review.

---

## 2. Background research already settled

- **qa_notes format** (from `packages/cdb_collect/cdb_collect/runner.py:278–280`): `"; ".join(f.actual for f in failures)` plus an optional trailing `; {campaign_id_tag}` segment. The campaign-id-tag is a bare integer when present (e.g. `4779`, `171`).
- **qa_notes shorthand catalogue** enumerated from `scripts/qa_check.py:run_record_checks`:

  | Check | Failure description | `actual` shorthand pattern | Example |
  |---|---|---|---|
  | 1 | Freelist item count too low | bare integer (count) | `0`, `7`, `9` |
  | 2 | Cross-run uniqueness too low | percentage | `12.3%` |
  | 3 | Pile-sort matrix non-binary | `found {cell}` | `found 2`, `found -1` |
  | 4 | Pile-sort matrix asymmetric | `{a} != {b}` | `0 != 1` |
  | 5 | Step latency exceeded | `{N}ms` | `60124ms`, `247348ms` |
  | 6 | Output token count inconsistent | bare integer (count) | `4779` |
  | 7 | Empty provider_request_id | literal `empty` | `empty` |
  | 8 | Pile-label count mismatch | `label_count_mismatch:N/M` | `label_count_mismatch:20/9` |
  | — | Trailing campaign_id_tag (NOT a failure) | bare integer | `4779`, `171` |

  **Disambiguation problem:** check 1, check 6, and the campaign-id tag all emit bare integers. Heuristic for the interpreter (subject to SME approval, Q1):
  - If the segment is the **last** segment AND prior segments include a `Nms` or `label_count_mismatch:` or `X.X%` segment, the trailing bare integer could be either check 6 (token inconsistency) OR a campaign tag — both cases occur in real data.
  - The interpreter cannot reliably separate check 6 from campaign tag from the string alone. Resolution options for the SME (Q1):
    - (i) Render both possibilities in the warning ("either token inconsistency or campaign tag").
    - (ii) Treat the trailing bare integer as ambiguous and label it generically.
    - (iii) Prefer one interpretation by position (e.g. trailing-bare-integer-after-other-failures = campaign tag; bare-integer-as-only-segment = check 1).
  - Cleaner alternative for the SME to consider for a follow-up architect task: have the runner prefix every shorthand with the check number (e.g. `check5:60124ms`). That solves disambiguation at the source. **Out of scope for OPS-T7** — flagged as a follow-up item.

- **Decline trigger field**: `len(_declines) > 0` for the selected informant. Already computed at `apps/ops_dashboard/app.py:308` via `find_decline_events(...)`. The banner can be rendered after that line is moved/duplicated above the QA badge — see §4.1.
- **Pile-sort source field**: `PileSortRecord.item_source: str` — defaults to `"own_freelist"` (`packages/cdb_core/cdb_core/schemas.py:436`). All current data is `"own_freelist"`. Future cross-collection runs will populate other values; the dashboard reads the field as-is.

---

## 3. Boundary check

| Boundary | Compliance |
|---|---|
| `cdb_publish` never imports `cdb_collect` | N/A — neither touched |
| Dashboard never imports `cdb_*` | N/A — `apps/ops_dashboard/` is an ops tool, allowed to import `cdb_core` (already does at `app.py:32`) |
| `cdb_social` never writes to `data/raw/` / `data/processed/` | N/A |
| `cdb_analyze` may not import LLM client | N/A |
| Read-only invariant of ops dashboard (`app.py:8–11`) | **Preserved.** Plan adds rendering only; no writes. |

---

## 4. Single Coder-sized task

OPS-T7 is one task, one commit. Three distinct rendering additions but they share scope (per-informant detail view), share fixtures, share test files, and Mark requested them as a bundle.

### 4.1 File touchlist

**New:**
- `apps/ops_dashboard/lib/qa_interpreter.py` — pure helper module. Contains:
  - `@dataclass QaInterpretation { code: str, why: str, impact: str, raw_segment: str }`
  - `def interpret_qa_notes(qa_notes: str) -> list[QaInterpretation]`
  - Module-level `_INTERPRETATION_TABLE` mapping each pattern (regex or literal-prefix) to a `(code, why, impact)` triple. Verbatim text approved by CDA SME (Q1).
  - Trailing-bare-integer handling per Q1 resolution.
- `tests/test_ops_dashboard_qa_interpreter.py` — exhaustive coverage of the interpretation table and edge cases.

**Edited:**
- `apps/ops_dashboard/app.py` — three insertion points:
  1. **Decline banner**: hoist the `_load_decline_interviews()` / `_load_manual_classifications()` / `_load_safety_subtypes()` / `find_decline_events(...)` calls from their current position (`app.py:304–313`) up above the QA badge so `_declines` is available immediately after `_rec` is resolved. Render the banner directly under `st.subheader(f"Detail — ...")` and ABOVE the QA badge when `len(_declines) > 0`.
  2. **QA-notes interpreter**: under the existing `st.error(f"**QA notes:** {_rec.qa_notes}")` block (around `app.py:242`), add a loop over `interpret_qa_notes(_rec.qa_notes)` rendering one `st.warning` per interpretation with the `why` and `impact` fields. Render only on the failing branch — passing-record `qa_notes` are already in an expander and don't need interpretation surfaced.
  3. **Pile-sort source caption**: under `st.markdown("### Pile-sort")` (around `app.py:277`), BEFORE the existing italic provenance caption. New caption uses the verbatim wording approved by SME (Q4). Item-count basis per Q5.
- `apps/ops_dashboard/lib/detail.py` — add `def pile_sort_item_count(record: InformantRecord) -> int` returning the count basis chosen by SME (Q5). Pure, no I/O.
- `tests/test_ops_dashboard_detail.py` — add tests for `pile_sort_item_count`.
- `tests/test_ops_dashboard_app_static.py` — add static-shape assertions for the three new rendering blocks.

### 4.2 Acceptance criteria

**A1 — QA-notes interpreter.**
- A1.1 Pure helper `interpret_qa_notes(qa_notes: str) -> list[QaInterpretation]` exists in `apps/ops_dashboard/lib/qa_interpreter.py`. No I/O, no imports of `cdb_collect`, no imports of any LLM client.
- A1.2 The interpretation table covers, at minimum: latency-exceeded (`{N}ms`), label-count-mismatch (`label_count_mismatch:N/M`), freelist-too-low (bare integer per Q1 resolution), cross-run-uniqueness-too-low (`X.X%`), non-binary-matrix (`found N`), asymmetric-matrix (`A != B`), empty-request-id (`empty`), token-inconsistency (bare integer per Q1 resolution).
- A1.3 The interpreter splits on `; `, classifies each segment, and the trailing-bare-integer ambiguity is handled per the SME-approved Q1 resolution.
- A1.4 An empty `qa_notes` string returns `[]`. A `qa_notes` containing only the campaign tag returns `[]` or a single non-failure interpretation per Q1 resolution.
- A1.5 In `app.py`, on the failing-record branch only, each interpretation renders as a `st.warning` containing `**Why:** {why}` and `**Impact on analysis:** {impact}` with `(raw segment: \`{raw_segment}\`)` for traceability.
- A1.6 Forbidden-vocabulary scan: no warnings text contains `believes`, `thinks`, `worldview`, `understands`, `sees the world`, or any other §7 forbidden phrase.

**A2 — Decline-events banner.**
- A2.1 The decline-events lookup (currently at `app.py:304–313`) is hoisted to before the QA badge so `_declines` is available immediately after `_rec` is resolved.
- A2.2 When `len(_declines) > 0`, a single `st.warning` (or `st.error`, per SME Q2 placement decision) banner renders directly under `st.subheader(f"Detail — ...")` and ABOVE the QA badge. Wording per Q3.
- A2.3 When `len(_declines) == 0`, no banner renders, no extra blank space, no placeholder.
- A2.4 The banner text uses neutral framing — no `refused`, no `declined` (verb), no `believes`. Specifically: *"This run produced N decline event(s). See **Decline summary** and **Decline events** sections below for details."* — verbatim subject to Q3.
- A2.5 The downstream `### Decline summary` and `### Decline events` blocks continue to render unchanged using the same `_declines` value (no double-fetch, no recomputation).

**A3 — Pile-sort source caption.**
- A3.1 A new helper `pile_sort_item_count(record) -> int` exists in `lib/detail.py`. Basis is the one approved in Q5.
- A3.2 In `app.py`, directly under `st.markdown("### Pile-sort")` and BEFORE the existing `*Pile labels and member ordering...*` caption, a new `st.caption` renders one of two strings depending on `_rec.pile_sort.item_source`:
  - `item_source == "own_freelist"`: *"Items sorted: this informant's own freelist (Step 1, N items)."*
  - `item_source != "own_freelist"`: *"Items sorted: external freelist source `{item_source}` (N items)."*
  - Verbatim subject to Q4.
- A3.3 When `_piles` is empty (no pile-sort data), the caption is suppressed (the existing "*This informant returned no pile-sort data.*" `st.info` already handles that case; no double surfacing).

**A4 — Cross-cutting.**
- A4.1 `uv run pytest`, `uv run ruff check .`, `uv run mypy packages/` all pass locally.
- A4.2 No edits to `cdb_core/schemas.py`. No edits to `docs/DATA_DICTIONARY.md`. No edits to `DESIGN_SYSTEM.md`.
- A4.3 No new dependencies in `pyproject.toml`.
- A4.4 Read-only invariant preserved. The new module imports nothing from `cdb_collect`.
- A4.5 One commit, conventional commits scope `ops`. Body references `OPS-T7` and the SME verdict file path.

### 4.3 Test strategy

**Unit tests in `tests/test_ops_dashboard_qa_interpreter.py`:**

| Test ID | qa_notes input | Expected interpretation count | Expected codes |
|---|---|---|---|
| QI-T1 | `""` | 0 | — |
| QI-T2 | `"60124ms"` | 1 | `[latency_exceeded]` |
| QI-T3 | `"label_count_mismatch:20/9"` | 1 | `[label_count_mismatch]` |
| QI-T4 | `"60124ms; label_count_mismatch:16/81"` | 2 | `[latency_exceeded, label_count_mismatch]` |
| QI-T5 | `"247348ms; 4779"` (latency + campaign tag) | 1 or 2 per Q1 resolution | per Q1 |
| QI-T6 | `"0; 71000ms; 171"` (zero items + latency + campaign tag) | 2 or 3 per Q1 resolution | per Q1 |
| QI-T7 | `"label_count_mismatch:64/63"` | 1 | `[label_count_mismatch]` |
| QI-T8 | `"empty"` | 1 | `[empty_request_id]` |
| QI-T9 | `"12.3%"` | 1 | `[uniqueness_too_low]` |
| QI-T10 | `"found 2"` | 1 | `[matrix_non_binary]` |
| QI-T11 | `"0 != 1"` | 1 | `[matrix_asymmetric]` |
| QI-T12 | `"4779"` (campaign tag alone) | 0 or 1 per Q1 resolution | per Q1 |
| QI-T13 | `"some unknown shorthand xyz"` | 1 with `code="unknown"` | `[unknown]` |
| QI-T14 | Forbidden-vocab regex scan over every `why`/`impact` string in the table | n/a | scan passes |
| QI-T15 | Determinism: calling `interpret_qa_notes` twice on the same input returns equal lists | n/a | equality |

**Helper tests in `tests/test_ops_dashboard_detail.py`:**
- PSC-T1: `pile_sort_item_count` returns the count basis chosen in Q5 for a normal multi-pile record.
- PSC-T2: returns 0 when `parsed_piles` is empty.
- PSC-T3: handles a pile_sort record with a non-default `item_source` value.

**Static-shape tests in `tests/test_ops_dashboard_app_static.py`:**
- AST-T1: `app.py` source contains the literal banner template substring (per Q3).
- AST-T2: `app.py` imports `interpret_qa_notes` from `apps.ops_dashboard.lib.qa_interpreter`.
- AST-T3: `app.py` imports `pile_sort_item_count` from `apps.ops_dashboard.lib.detail` (or computes equivalent inline).
- AST-T4: source-grep that the pile-sort caption strings for both `own_freelist` and `external` branches are present.
- AST-T5: forbidden-vocabulary regex scan over `app.py`, `lib/qa_interpreter.py`, `lib/detail.py` — fails on any §7 phrase.

### 4.4 Schema check

Confirmed: **no `cdb_core/schemas.py` change**. `PileSortRecord.item_source` already exists. `DeclineInterview.originating_outcome_class` already exists. `InformantRecord.qa_notes` already exists. No `DATA_DICTIONARY.md` update required. Reviewer rule R7 not triggered.

---

## 5. CDA SME questions (single light-touch verdict file)

Verdict file expected at `docs/status/2026-05-06-OPS-T7-cda-sme-verdict.md`.

**Q1 — QA-notes interpretation table.** Approve verbatim `(why, impact)` strings for each shorthand. Drafted below for SME blue-pencil:

| code | matches | why (operator-facing) | impact on analysis |
|---|---|---|---|
| `latency_exceeded` | `^\d+ms$` | "Step latency exceeded the 60-second ceiling." | "Run is usable for raw inspection. Aggregate latency-sensitive analyses (per-step timing distributions) should exclude or flag this run." |
| `label_count_mismatch` | `^label_count_mismatch:\d+/\d+$` | "The model returned N piles in Step 2 but M pile labels in Step 3 (N ≠ M)." | "Pile-naming alignment is broken for this run. Co-occurrence matrix is still well-formed and usable for MDS/clustering. Pile-label-dependent visualizations and any downstream label-keyed analysis must skip this run." |
| `freelist_too_low` | bare integer (per Q1 resolution) | "Freelist returned fewer than 10 items." | "Salience measures (Smith's S, Sutrop CSI) computed on this run are unreliable. Excluded from grouped salience aggregates." |
| `uniqueness_too_low` | `^\d+(\.\d+)?%$` | "Cross-run vocabulary uniqueness for this (model, domain) pair fell below 15%." | "Aggregate concern, not run-specific. The (model, domain) group's salience may reflect rote output rather than informed elicitation." |
| `matrix_non_binary` | `^found .+$` | "Pile-sort matrix contains a non-binary cell value." | "Co-occurrence matrix is malformed; this run is unsafe for any pile-sort-derived analysis." |
| `matrix_asymmetric` | `^\d+ != \d+$` | "Pile-sort matrix is asymmetric." | "Co-occurrence matrix is malformed; this run is unsafe for any pile-sort-derived analysis." |
| `empty_request_id` | literal `empty` | "Provider did not return a request_id." | "Provenance audit path through the provider's logs is unavailable for this run. Local SHA256 manifest still anchors the data." |
| `token_inconsistency` | bare integer (per Q1 resolution) | "Output token count from the provider deviates more than 100% from the chars/4 heuristic." | "Heuristic-only flag; the run is usable. Indicates either heavy non-ASCII content or a provider-side token-count anomaly." |
| `unknown` | otherwise | "Unrecognized QA-failure shorthand. See `scripts/qa_check.py`." | "Operator must read the source to resolve." |

**Bare-integer disambiguation (sub-question of Q1):** check 1, check 6, and the campaign-id-tag all emit bare integers. Pick a resolution:
- (i) Render both possibilities in the warning ("either token inconsistency or campaign tag").
- (ii) Treat the trailing bare integer as ambiguous and label it generically.
- (iii) Position-based heuristic: bare integer as the *only* segment → check 1 (`freelist_too_low`); bare integer as the *trailing* segment after other shorthands → label as ambiguous (could be check 6 or campaign tag).
- (iv) Add a follow-up architect task to prefix shorthands at the runner level (`check5:60124ms`) — out of scope for OPS-T7.

**Q2 — Decline banner placement.** Three options:
- (a) Top-of-detail-section, ABOVE the QA badge (Architect recommendation — declines indicate the run did not behave as a complying informant; this is the loudest signal).
- (b) BELOW the QA badge but above the divider preceding `### Freelist`.
- (c) Sticky at the very top of the page (above `Detail —`).

**Q3 — Decline banner wording.** Architect recommendation, verbatim:

> "This run produced N decline event(s). See **Decline summary** and **Decline events** sections below for details."

Singular form when N=1. SME approves verbatim or rewords.

**Q4 — Pile-sort source caption wording.** Architect recommendation, verbatim:

- own_freelist: *"Items sorted: this informant's own freelist (Step 1, N items)."*
- external: *"Items sorted: external freelist source `{item_source}` (N items)."*

SME approves verbatim or rewords. Particular concern: should the `external` caption clarify whether the items are a consensus list, a single foreign informant's list, or something else? The dashboard cannot answer that from the schema alone. Architect's view: leave the caption neutral and let the operator chase the `item_source` token.

**Q5 — Pile-sort item count basis.** Three candidates:
- (a) `len(record.pile_sort.parsed_piles)` flattened — "items actually placed in piles."
- (b) `len(record.freelist.parsed_items)` — "items the freelist step produced." (Misleading when `item_source != own_freelist`.)
- (c) Distinct count across `parsed_piles` flattened.

Architect recommendation: **(a) flattened total of `parsed_piles`** — it is the count of items the model was asked to sort, observed at sort time.

**Q6 — Forbidden-vocabulary clearance.** Confirm none of the literals proposed in Q1–Q4 contain §7 vocabulary. Architect's pre-scan: clean. SME confirms.

---

## 6. Reading list for the Coder

Mandatory before starting:
1. `CLAUDE.md` — §6 binding rules, §7 forbidden vocabulary, §9 common pitfalls.
2. `ARCHITECTURE.md` §1.5 (framing — binding on all rendered text), §3.2 (`InformantRecord`, `PileSortRecord.item_source`, `DeclineInterview` schemas).
3. `apps/ops_dashboard/app.py` (current detail view).
4. `apps/ops_dashboard/lib/detail.py` (existing pure helpers and patterns).
5. `scripts/qa_check.py` — full file. The interpretation table in Q1 must match every `QAFailure` constructor's `actual` argument.
6. `packages/cdb_collect/cdb_collect/runner.py:266–285` — qa_notes assembly logic.
7. `tests/test_ops_dashboard_detail.py` and `tests/test_ops_dashboard_app_static.py` — test conventions.
8. `docs/status/2026-05-06-OPS-T7-cda-sme-verdict.md` — once posted, all PASS-WITH-NOTES items are mandatory.

Conditional reads: none. No `DESIGN_SYSTEM.md` (ops dashboard is exempt). No `DATA_DICTIONARY.md` (no schema changes). No `SECURITY_AND_HARDENING.md` (no collection-layer or CI/CD changes).

---

## 7. Reviewer + Tester instructions

**Reviewer must verify:**
- R1: No edits to `cdb_core/schemas.py`.
- R2: No new entries in `pyproject.toml` dependencies.
- R3: `apps/ops_dashboard/lib/qa_interpreter.py` imports nothing from `cdb_collect`, `cdb_analyze`, `cdb_publish`, `cdb_social`, or any LLM client.
- R4: Read-only invariant preserved — grep for `open(`, `write`, `dump` in the new module returns nothing concerning.
- R5: Forbidden-vocabulary scan on the diff passes.
- R6: Commit message conventional-commits compliant with scope `ops`, references `OPS-T7` and the verdict file path.
- R7: One commit, no bundled work.
- R8: All four CDA SME PASS-WITH-NOTES items (if any) addressed.

**Tester must verify:**
- T1–T3: New test files pass.
- T4–T5: ruff and mypy clean.
- T6: Manual smoke (Mark, post-merge, via SSH tunnel) — load a known qa_passed=False record, confirm the warning interpretations render. Load a known record with declines, confirm the banner appears at top. Load a normal pile-sort record, confirm the source caption reads correctly.

---

## 8. Routing

- [x] Plan complete.
- [ ] **NEXT — Route to CDA SME** for light-touch review on Q1–Q6.
- [ ] On SME PASS or PASS-WITH-NOTES (notes applied to plan in place), hand to Coder.
- [ ] No UI/UX gating — internal ops tool.
