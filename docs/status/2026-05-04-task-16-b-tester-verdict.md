# Task 16.B — Tester Verdict

**Date:** 2026-05-04
**Reviewer:** Tester agent (Sonnet)
**Commit under review:** `de3dd7e`
**Gap-coverage commit:** `f17b47f`
**Task:** Task 16.B — schemas + DATA_DICTIONARY + runner wiring + build_db DDL for `thoughts_token_count`
**Plan:** `docs/status/2026-05-04-task-16-architect-plan.md` §2 Task 16.B
**SME verdict:** `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (PASS-WITH-NOTES; S1–S5)
**Reviewer verdict:** `docs/status/2026-05-04-task-16-b-reviewer-verdict.md` (PASS-WITH-NOTES; N1 cosmetic)

---

## VERDICT: PASS

All 11 items from the task brief are satisfied. Two gap-coverage tests were added in commit `f17b47f`; the full suite rises to 1067 passed.

---

## Item-by-item assessment

**Item 1 — Schema default test (backward compat, all three step records)**

PASS. Three tests present in `tests/unit/test_schemas.py`:
- `test_freelist_record_missing_thoughts_token_count_loads_as_zero`
- `test_pilesort_record_missing_thoughts_token_count_loads_as_zero`
- `test_interview_record_missing_thoughts_token_count_loads_as_zero`

Each constructs a record, serialises to JSON, removes the `thoughts_token_count` key to simulate a pre-v0.1.11 legacy line, then validates and asserts the value is `0`. All three step records covered.

**Item 2 — Round-trip test (non-zero thoughts_token_count on all three step records)**

PASS. `test_informant_record_with_nonzero_thoughts_token_count_round_trips` in `tests/unit/test_schemas.py` constructs an `InformantRecord` with `thoughts_token_count=128` on the freelist, `256` on pile sort, `64` on interview, runs `model_dump_json` → `model_validate_json`, and asserts all three values survive round-trip. Acceptance criterion 16.B.7 satisfied.

**Item 3 — `append_failure` test with `thoughts_token_count` set (field present, position after `stop_reason`)**

PASS. `test_append_failure_thoughts_token_count_written` in `tests/unit/test_jsonl.py` sets `stop_reason="MAX_TOKENS"` and `thoughts_token_count=512`, then asserts the field is written and that `keys.index("stop_reason") < keys.index("thoughts_token_count")`.

**Item 4 — `append_failure` test — None case (field absent when not set)**

PASS. `test_append_failure_thoughts_token_count_none_omitted` asserts `"thoughts_token_count" not in entry` when the parameter is omitted (defaults to `None`).

**Item 5 — `build_db.py` test — backward compat (legacy records default to 0)**

PASS. `test_build_db_thoughts_token_count_legacy_record_defaults_to_zero` in `tests/unit/test_build_db.py` builds from a JSONL where `thoughts_token_count` is absent on all three step sub-dicts, then queries SQLite and asserts all three columns are `0`.

**Item 6 — `build_db.py` test — new records (non-zero values stored correctly)**

PASS. `test_build_db_thoughts_token_count_nonzero_values` inserts a record with `freelist_ttc=128, pilesort_ttc=256, interview_ttc=64` and asserts the three columns (`freelist_thoughts_token_count`, `pilesort_thoughts_token_count`, `interview_thoughts_token_count`) match.

**Item 7 — `build_db.py` test — mixed (old and new records both populate correctly)**

PASS. `test_build_db_thoughts_token_count_mixed_old_and_new` builds from a two-line JSONL (one legacy, one new) and asserts `old_row == (0, 0, 0)` and `new_row == (99, 77, 33)`. Informant count is also verified as 2.

**Item 8 — DDL column existence test (all three column names present in schema)**

PASS. `test_build_db_thoughts_token_count_column_exists` calls `PRAGMA table_info(informants)` and asserts `freelist_thoughts_token_count`, `pilesort_thoughts_token_count`, and `interview_thoughts_token_count` are all present.

**Item 9 — No real API calls; no reading from `data/raw/*.jsonl`**

PASS. All new tests use `tmp_path`, string literals, and dict construction. No `data/raw/` reads. No adapter calls hit live endpoints. The `_make_record_without_thoughts` and `_make_record_with_thoughts` helpers are synthetic derivations of the in-file `_make_record()` fixture, not extractions from real runs.

**Item 10 — No reading of `data/raw/*.jsonl` in tests**

PASS. Confirmed by inspection. No test file in `tests/` opens a path under `data/`.

**Item 11 — New fixtures (if any) are synthesised, not extracted from real runs**

PASS. No new fixture files were added. The build_db tests construct dicts inline using `_make_record()` as a base. The schemas tests construct `FreelistRecord` / `PileSortRecord` / `InterviewRecord` instances inline. Fixture names and IDs (`ttc_test_001`, `ttc_new`, `legacy`, `old_rec`, `new_rec`) do not resemble real collection IDs and do not contain plausible SHA256 manifests or real-looking model version strings.

---

## Gap coverage added

**Gap identified:** The plan's test coverage requirements and the task brief's "Gaps to potentially add" section both flag the protocol-layer wiring path. No test in commit `de3dd7e` verified that a non-zero `thoughts_token_count` value on an `AdapterResult` propagates through the protocol modules (`protocol/free_list.py`, `protocol/pile_sort.py`, `protocol/pile_interview.py`) to the corresponding fields on the constructed `InformantRecord` step records. The schema and build_db tests confirm persistence; they do not confirm the collection path.

**Tests added in gap-coverage commit `f17b47f` (`tests/unit/test_runner.py`):**

- `test_run_informant_propagates_thoughts_token_count_to_step_records` — uses a mock adapter that returns `thoughts_token_count=128/256/64` on freelist/pilesort/interview steps respectively; calls `run_informant` end-to-end and asserts all three step records carry the correct value. This is the happy-path end-to-end test for acceptance criterion 16.B.2.
- `test_run_informant_thoughts_token_count_zero_by_default` — confirms that the default `AdapterResult` (all zeros) produces zero on all three step records, establishing that the diagnostic invariant `output_tokens == 0 AND thoughts_token_count > 0` cannot false-positive on providers that do not surface reasoning tokens.

No real API calls. The mock adapter is an async `MagicMock` returning fixture `AdapterResult` objects constructed inline. The mock dispatches by prompt text (same strategy as the existing `_mock_adapter()`).

**Gaps NOT added (with reasoning):**

- Field-order test for JSONL serialization: the plan asked whether `thoughts_token_count` appears immediately after `output_tokens` in the serialized record. Manual verification confirms it does (Pydantic serializes fields in declaration order; the field is declared after `output_tokens` in all three step schemas). A test was not added because (a) the existing round-trip tests implicitly confirm field presence and (b) field-order is not a functional contract — if pydantic's serialization order changes in a dependency bump, breaking the test would be a false negative requiring maintenance. The schema-level backward-compat tests are the right guard here.

- SQLite migration path test: `build_db.py` always rebuilds from scratch (confirmed by `test_build_db_replaces_existing`). There is no migration path to test. The rebuild-from-scratch behavior is already tested.

---

## Test run results

**Three target files, verbose:**

```
tests/unit/test_schemas.py — 27 collected, 27 passed
tests/unit/test_jsonl.py   — 21 collected, 21 passed
tests/unit/test_build_db.py — 14 collected, 14 passed
Total: 62 passed in 0.56s
```

**thoughts_token_count keyword filter (all files):**

```
21 selected, 21 passed in 3.64s
(files: test_adapter_base.py ×2, test_build_db.py ×4, test_google_adapter.py ×3,
 test_jsonl.py ×4, test_openrouter_adapter.py ×3, test_schemas.py ×5)
```

**Full suite after gap-coverage commit `f17b47f`:**

```
1067 passed, 26313 warnings in 13.64s
```
(Was 1065 before gap-coverage commit.)

**ruff:** clean on `tests/unit/test_runner.py`.
**mypy:** clean (53 source files, 0 issues).

---

## Final disposition

**VERDICT: PASS**

All eight items from the plan's test coverage requirements are present and passing. All eleven items from the task brief checklist are satisfied. Two gap-coverage tests were added in commit `f17b47f` to cover the protocol-layer wiring path (acceptance criterion 16.B.2 end-to-end). No production code was modified. No real API calls in any test. Full suite is green at 1067.

*End of verdict.*
