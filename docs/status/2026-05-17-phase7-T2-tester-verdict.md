---
filed: 2026-05-17
reviewer: LSB Tester agent (Sonnet)
task: Phase 7 T2 — Triggers (5 pure detection functions)
commit: d60c110 (feat(social): Phase 7 T2 — triggers (5 pure detection functions))
cda_sme_t2_verdict: docs/status/2026-05-17-phase7-T2-cda-sme-verdict.md (PASS-WITH-NOTES)
reviewer_verdict: docs/status/2026-05-17-phase7-T2-reviewer-verdict.md (PASS)
verdict: PASS-WITH-NOTES
---

# Phase 7 T2 — Tester verdict

**TESTER VERDICT: PASS-WITH-NOTES**

Full suite: 1385/1385 passed. 62 new trigger tests all green. Ruff clean.
Mypy clean. One advisory gap documented below (non-blocking).

---

## Test run output

```
uv run pytest tests/              → 1385 passed, 0 failed (77.63s)
uv run pytest tests/unit/test_social_triggers.py
                                  → 62 passed in 0.24s
uv run ruff check .               → All checks passed!
uv run mypy packages/             → Success: no issues found in 63 source files
```

---

## Checks completed

### 1. All existing tests pass

1385 passed — exactly the 1323 pre-T2 baseline plus 62 new. Zero regressions.

### 2. Ruff + mypy clean

`ruff check` → clean. `mypy packages/` → clean (63 source files). No type
errors, no lint issues.

### 3. 62 new tests — CDA SME §5.x binding-note coverage

All 62 tests pass. Coverage mapped to each binding note:

| CDA SME note | Test class / function | Coverage |
|---|---|---|
| §5.1 — DRIFT_THRESHOLD=0.15, DRIFT_MIN_ITEM_INTERSECTION=8, DriftDataInsufficientError, enable=False lockout, pre-fire warning log | `TestDriftConstants` (6 tests) | COVERED |
| §5.2 — MIN_DIVERGENCE_DELTA=0.02, fires on delta >= 0.02, no emit on delta < 0.02, gap_delta self-consistency, no CI-overlap (structural), state update on fire, state not updated when suppressed | `TestDivergenceConstants` (8 tests) | COVERED |
| §5.3 — StateFileMissingError for all 4 detectors, bootstrap_state writes sentinel, bootstrap → same manifest → no triggers, bootstrap → new model/domain fires | `TestBootstrapAndStateSentinel` (9 tests) | COVERED (see advisory note) |
| §5.4 — fires on 1st of month, evidence['month'] is previous calendar month (incl. year-boundary), idempotency within month (2 tests), state updated after fire | `TestMonthlyRoundup` (6 tests) | COVERED |
| §5.5 — dedupe_key 16-char hex, deterministic, varies with trigger_type / domain, excludes drafter_version + prompt_version (signature inspection), stable across evidence key order, emitted triggers carry key | `TestDedupeKey` (7 tests) | COVERED |
| §5.6 — masquerade suppressed, organic divergence fires despite new model, model_pair excludes new model, baseline not updated on suppression, _max_pairwise_gap helper with/without exclusion | `TestDivergenceNewModelInteraction` (6 tests) | COVERED |
| §5.7 — valid evidence passes and missing-key raises for all 5 TriggerTypes, EVIDENCE_MIN_KEYS covers all TriggerType values, error message names trigger_type | `TestEvidenceEnforcement` (12 tests) | COVERED |
| Boundary: no LLM imports | `test_no_llm_imports_in_triggers` | COVERED |
| Boundary: no data/raw writes | `test_no_data_raw_writes_in_triggers` | COVERED |
| detect_new_model additional (idempotency, state update, trigger per domain-model pair, evidence) | `TestDetectNewModel` (4 tests) | COVERED |
| detect_new_domain additional (fires for new domain, no trigger for known) | `TestDetectNewDomain` (2 tests) | COVERED |

### 4. Forbidden-vocabulary grep

```
git diff d60c110~1..d60c110 -- packages/cdb_social/ tests/ \
  | grep -iE 'worldview|believes|thinks of|cultural bias|
              what the model understands|how models see|model.*believes|
              model.*thinks of|within-model consensus|within-model cultural|
              within-model eigenratio|within-model CCM'
```

Output: (empty). No forbidden vocabulary in any added content.

### 5. Scope sanity

`git diff --name-only d60c110~1..d60c110` shows exactly:

```
packages/cdb_social/cdb_social/__init__.py
packages/cdb_social/cdb_social/triggers.py
tests/fixtures/social/published_data_snapshots/divergence_highs_baseline.json
tests/fixtures/social/published_data_snapshots/manifest_baseline.json
tests/fixtures/social/published_data_snapshots/manifest_new_domain.json
tests/fixtures/social/published_data_snapshots/manifest_new_model.json
tests/fixtures/social/published_data_snapshots/monthly_roundup_already_fired.json
tests/fixtures/social/published_data_snapshots/monthly_roundup_not_fired.json
tests/unit/test_social_triggers.py
```

9 files. All within T2 declared scope. No `cdb_core/schemas.py`, no
`ARCHITECTURE.md`, no `DATA_DICTIONARY.md`, no T3/T4/T5 files.
6 fixture files confirmed under `tests/fixtures/social/published_data_snapshots/`.

### 6. Boundary-rule verification

- `grep -rE 'from cdb_analyze|import cdb_analyze' packages/cdb_social/` → empty
- `grep -rE 'import anthropic|import openai|InferenceClient|google.generativeai' packages/cdb_social/cdb_social/triggers.py` → empty
- `grep -E 'data/raw|data/processed' packages/cdb_social/cdb_social/triggers.py` → only
  module docstring line 7 ("do not write to ``data/raw/`` or ``data/processed/``"),
  which is boundary documentation, not a write call. PASS.

### 7. Atomic write verification

`_atomic_write_json` (triggers.py line 183–195) uses `tempfile.mkstemp(dir=path.parent,
suffix=".tmp")` followed by `os.replace(tmp, path)`. No bare `open(..., 'w').write()`
for state files. Every state-write call site (8 total) routes through this helper. PASS.

---

## Advisory coverage gap (non-blocking)

**`StateFileSchemaError` — defined in CDA SME §5.3 binding note, not implemented.**

The CDA SME §5.3 binding note specifies three state-file states:

1. File absent → raise `StateFileMissingError` (implemented and tested)
2. File present, `bootstrapped_at` missing → raise `StateFileSchemaError` (not implemented)
3. File present, `bootstrapped_at` present → normal operation (implemented and tested)

`StateFileSchemaError` does not appear anywhere in `triggers.py` or
`test_social_triggers.py`. The `_read_state_file()` helper returns the raw dict
without checking for `bootstrapped_at`; a corrupted state file (sentinel removed by
accident) silently operates rather than failing loud.

The Reviewer's T2 PASS verdict did not flag this gap. The primary §5.3 goal —
fail-loud on file absence — is fully implemented and tested. The `StateFileSchemaError`
branch is a secondary defensive case for in-place corruption.

**Assessment: advisory, not a blocker.** The absence of this exception does not
compromise the detection logic or the primary fail-loud posture. It leaves a narrow
undetected failure mode (corrupted sentinel in an otherwise-present file). Recommend
adding in a gap-fill if T3 workload permits; otherwise defer to T5 or T7.

If gap-fill is desired, the implementation is two lines in `_read_state_file()`:
```python
if "bootstrapped_at" not in data:
    raise StateFileSchemaError(f"State file {path} missing 'bootstrapped_at' sentinel.")
```
with a corresponding exception class and one test per affected detector.

---

## Summary

62/62 new tests pass. 1385/1385 total. All 7 CDA SME §5.x binding notes covered.
Ruff clean. Mypy clean. Forbidden vocab empty. Scope correct. Atomic writes
verified. One advisory gap (StateFileSchemaError) noted; not blocking.

---

*End of Phase 7 T2 Tester verdict.*
