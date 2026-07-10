# Plan: reasoning-model QA recalibration, batch A follow-up

**Author:** Architect agent (persisted by orchestrator; Architect has no write access)
**Date:** 2026-07-10
**Owning gate:** CDA SME PASS-WITH-NOTES, `docs/status/2026-07-10-batchA-reasoning-qa-cda-sme-verdict.md`. Notes N1-N7 binding; N5 disposition owned by Architect (below).
**Re-review routing:** SME not required for this plan; it executes binding notes verbatim. N4 (methodology footnote) deferred to the next methodology update per SME direction. UI/UX not required; no frontend surface.

**Rule 15 (math freeze) boundary:** No task creates, modifies, or redesigns any statistical computation. `scripts/qa_check.py` is deterministic collection QA. N6 is a mechanical count comparison. N5 changes which records enter the analytical basis (the intent of the SME ruling); no estimator, resampling, or measure code is touched.

**Append-only boundary:** No task mutates `data/raw/informants.jsonl`. Persisted `qa_passed` on the 12 batch-A reasoning records is retained verbatim.

---

## N5 disposition (Architect decision)

**Chosen: option (i), corpus-build re-QA.** Implementation lives in `packages/cdb_analyze/cdb_analyze/pipeline.py::load_records`. When `qa_only=True`, `load_records` recomputes QA on each record by running the current `run_record_checks` against record contents and filters on the recomputed result. Persisted `qa_passed` is retained as an audit artifact but is no longer authoritative for corpus inclusion. This implements the SME's records-as-data, rules-as-code framing, avoids re-collection, and prevents the option-(c) silent-drop failure mode from reproducing through inaction. Every caller of `load_records` (rebaseline_corpus, analyze CLI, validate CLI, cdb_publish.build, tests) inherits the same semantics; that uniformity is the point.

---

## Task list

### T1. Class-conditioned Check 5 latency threshold (N1)
- **File:** `scripts/qa_check.py`.
- **Changes:** add module constant `MAX_LATENCY_MS_REASONING = 600_000` with the SME rationale in a comment ("class-conditioned per CDA SME 2026-07-10 N1; do not raise the base threshold, see N7"). In `check_5_latency`, per step: when `step.thoughts_token_count > 0` use the reasoning ceiling, otherwise the existing `MAX_LATENCY_MS`. Failure text unchanged in shape; the numeric threshold in the message reflects the ceiling applied.
- **Acceptance:**
  - Non-reasoning behavior unchanged (regression test fails at 60_001 ms on a non-reasoning fixture).
  - Reasoning step at 300_000 ms passes; reasoning step at 700_000 ms fails.
  - Per-step branching only; no mixed ceilings within one call.

### T2. Reasoning-aware Check 6 arithmetic (N2)
- **File:** `scripts/qa_check.py`.
- **Changes:** in `check_6_token_consistency`, when `step.thoughts_token_count > 0`, compute `visible_tokens = step.output_tokens - step.thoughts_token_count` and compare `visible_tokens` (in place of `step.output_tokens`) against `len(response_verbatim) / 4`. Retain the existing early-out `if not step.response_verbatim or step.output_tokens == 0: continue`. When `visible_tokens <= 0` the step is not evaluable under the chars/4 heuristic; continue past it.
- **Acceptance:**
  - Non-reasoning behavior unchanged.
  - Batch-A-shaped reasoning fixture (thoughts_token_count > 0, output_tokens includes reasoning, short response_verbatim) passes Check 6.
  - When `output_tokens == thoughts_token_count`, the step is skipped rather than failed.

### T3. Reasoning-class `capacity_note` at collection time (N3)
- **Home decision:** parallel mechanism, not `AdapterResult.forced_default_note`. Rationale: `forced_default_note` is per-adapter-call, set by one adapter for one step. The reasoning-class condition is cross-step (`any(step.thoughts_token_count > 0)` across freelist, pile_sort, interview) and is visible on the assembled step records at record-assembly time. Deriving the note in the runner from the three persisted `thoughts_token_count` values is local and follows the existing `capacity_note` append pattern.
- **File:** `packages/cdb_collect/cdb_collect/runner.py`, `_assemble_record`. After the existing `forced_default_note` append, add a reasoning-class branch: if any step has `thoughts_token_count > 0`, append the verbatim SME N3 text to `capacity_note_value` using the same `"; ".join(note_parts)` composition. Store the verbatim text as module-level `_REASONING_CLASS_NOTE` immediately above `_assemble_record`, with a comment citing the verdict path.
- **Acceptance:**
  - Any step with `thoughts_token_count > 0` produces the verbatim N3 string in `capacity_note`.
  - All-zero `thoughts_token_count` yields no reasoning-class text.
  - When both `forced_default_note` and the reasoning-class condition apply, both notes appear, `; `-joined, in that order.
  - The string matches the SME verdict character-for-character (string constant test).

### T4. Pre-promotion representation check (N6)
- **File (new):** `scripts/preflight_reasoning_class_representation.py`. Standalone, per SME preference not to touch `scripts/rebaseline_corpus.py` internals.
- **Behavior:** takes `--jsonl` (default `data/raw/informants.jsonl`) and `--domains` (comma-separated). Per domain, loads records via `load_records` (T5 semantics apply), counts (a) informants with at least one step at `thoughts_token_count > 0` (reasoning class) and (b) informants with all steps at zero (non-reasoning). If reasoning == 0 AND non-reasoning > 0: print per-model diagnostic, exit 1. If reasoning > 0: PASS, exit 0. If non-reasoning == 0 (single-class corpus): SKIP, exit 0.
- **Rule 15 boundary:** count comparison only. No import from `cdb_analyze.mds`, `.consensus`, `.bootstrap`, `.smiths_s`, `.sutrop` (only `pipeline.load_records`).
- **Acceptance:** three fixture cases: (0 reasoning, >0 non-reasoning) exits 1; mixed exits 0; single-class exits 0.

### T5. Corpus-build re-QA in `load_records` (N5, option i)
- **File:** `packages/cdb_analyze/cdb_analyze/pipeline.py`.
- **Changes to `load_records`:** retain signature (`qa_only` bool, default True). Two-pass: read all domain records unfiltered; then, when `qa_only=True`, run `run_record_checks(record, all_records_in_domain)` on each and filter on empty failure list. Function-scope import of `scripts.qa_check.run_record_checks`, mirroring the pattern at `packages/cdb_collect/cdb_collect/runner.py:281` including the `ModuleNotFoundError` sys.path fallback. Docstring note: persisted `qa_passed` is not the authoritative filter under `qa_only=True`; corpus inclusion is determined by the current qa_check rules against record contents (records-as-data, rules-as-code, per CDA SME 2026-07-10 N5). Log at INFO, once per call, the count of records whose persisted `qa_passed` differs from the recomputed value, with divergence direction (persisted-True-now-False, persisted-False-now-True). That log is the audit trail that rule changes are not silently reshaping the corpus.
- **Rule 11 boundary:** `scripts.qa_check` pulls no LLM client libraries.
- **Rule 15 boundary:** filtering only; no analysis code changes.
- **Append-only:** JSONL is read; persisted `qa_passed` untouched.
- **Acceptance:**
  - A persisted `qa_passed=False` record whose only failures were Checks 5/6 under pre-recalibration rules is included after T1/T2 land.
  - A persisted `qa_passed=True` record that would now fail is excluded, and the divergence is logged.
  - `qa_only=False` returns everything unchanged.
  - No caller code changes; existing test suite green.

### T6. Test bundle
Fixtures only, no real API calls (pitfall 9). Fixture data under `tests/fixtures/reasoning_class/` as JSONL: one non-reasoning record, one reasoning record with realistic `thoughts_token_count` and short `response_verbatim` (batch A shape), one reasoning record at 700_000 ms latency, one reasoning record where `output_tokens == thoughts_token_count`.
- `tests/unit/test_qa_check.py` extended: T1 branching, T2 arithmetic, T2 skip case, non-reasoning regressions for both checks.
- `tests/unit/test_runner_reasoning_note.py` (new): T3 composition, verbatim constant, order-and-join.
- `tests/unit/test_pipeline_load_records_recompute.py` (new): T5 recompute-include, recompute-exclude, `qa_only=False` bypass, divergence log via `caplog`.
- `tests/scripts/test_preflight_reasoning_class_representation.py` (new): T4 exit codes.

---

## Dependency order

1. T1, T2 (one commit)
2. T3
3. T5 (depends on T1/T2: re-QA semantics only recover batch A records once recalibrated rules exist)
4. T4 (depends on T5)
5. T6 lands with each task.

One commit per task per CLAUDE.md §8 (four code commits: T1+T2, T3, T5, T4).

---

## Schema changes

None. `thoughts_token_count`, `capacity_note`, `qa_passed` already exist on the step/record schemas. No `DATA_DICTIONARY.md` update required.

## Out of scope

- N4 methodology-page footnote (next methodology update; separate plan).
- Checks 1-4, 7, 8, 9 unchanged.
- Non-reasoning thresholds unchanged (N7 forbids raising the base ceiling).
- No re-collection of the 12 batch A records; no mutation of persisted `qa_passed`.
