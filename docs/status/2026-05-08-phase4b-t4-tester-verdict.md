# Tester Verdict — Phase 4b T4 (Variance-Arm Campaign Driver)

**Date:** 2026-05-08
**Tester:** LSB Tester agent (Sonnet 4.6)
**Commit under test:** `e3da1c6`
**Commit subject:** `feat(collect): Phase 4b T4 variance-arm campaign driver`
**Scope:** `scripts/run_phase4b_variance.py` + `tests/unit/test_run_phase4b_variance.py`
**Reviewer verdict on file:** `docs/status/2026-05-08-phase4b-t4-reviewer-verdict.md` — PASS

---

## TESTER VERDICT: PASS-WITH-NOTES

The original 27 tests all pass. Five additional tests were written and committed
to close the three critical gaps identified during coverage assessment.
The extended suite (32 tests) passes. All gap tests are committed as
`test(collect): Phase 4b T4 — retry budget, spend cap, and log append-only tests`.

---

## 1. Test suite run — original 27 tests

```
uv run pytest tests/unit/test_run_phase4b_variance.py -v --no-header
```

Result: **27 passed in 0.83s** — all original tests pass, exactly as the
Reviewer recorded.

---

## 2. Coverage assessment — 7 concerns

### Concern 1 — `MAX_ATTEMPTS_PER_CELL = 2` retry budget
**Status: GAP (now closed)**

Zero coverage in the original 27 tests. `run_cell()` — the function containing
the two-attempt retry loop — was entirely untested.

Two new tests were written:
- `test_run_cell_retry_first_fail_second_pass`: mocks `_run_one_informant` to
  fail on attempt 1, succeed on attempt 2. Asserts `append_record` called once,
  `append_failure` not called, return value is `"PASS"`, and
  `stats.n_pass == 1`.
- `test_run_cell_retry_both_fail`: both attempts raise `ValueError`. Asserts
  `append_record` not called, `append_failure` called once with `failure_context`
  containing the correct `model_id` and `campaign_id`, return value is
  `"FAILED"`, and `stats.n_failed == 1`.

All provider adapter calls are mocked. No live API calls.

### Concern 2 — `CDB_MAX_SPEND_USD` spend cap
**Status: GAP (now closed)**

Zero coverage in the original 27 tests. The `provider_worker` spend-cap check
at lines 664–675 of the script was untested.

New test: `test_provider_worker_exits_when_spend_cap_reached` — pre-seeds
`CampaignStats.total_spend_usd` at the cap value before calling
`provider_worker` directly. Asserts `run_cell` is never invoked and the
cell counter is not incremented. The cell is placed back on the queue as the
production code requires.

### Concern 3 — `append_success_rates_to_log` append-only invariant
**Status: GAP (now closed)**

Zero coverage in the original 27 tests. The `append_success_rates_to_log`
function (lines 810–883) modifies `PROMPT_EVOLUTION_LOG.md` in place and
needed verification that pre-existing rows survive unchanged.

Two new tests were written:
- `test_append_success_rates_preserves_preexisting_rows`: a log with one
  pre-existing campaign row and the pending placeholder is written to
  `tmp_path`. After calling `append_success_rates_to_log`, the prior row
  is present verbatim, the placeholder is present, and the new row is present.
- `test_append_success_rates_new_row_after_placeholder`: confirms new rows
  are inserted *after* the placeholder line (not before), enforcing the
  log's append-only semantics.

### Concern 4 — SIGINT handler
**Status: Forward-carry (acceptable)**

The `_handle_sigint` function (lines 186–195) sets a module-level flag.
Testing SIGINT handlers in unit tests requires sending OS signals to the
test process, which is not reliable in pytest without process isolation.
The SIGINT concern is a forward-carry to a future integration test suite
if campaign-driver integration tests are added. This is not a critical-path
gap for CI.

### Concern 5 — `model_id` vs `model_version_returned` (CLAUDE.md §9 pitfall 1)
**Status: Adequately covered by existing tests**

The fixture helper `_make_informant_jsonl_line` (line 54–112) includes both
`model_id` and `model_version_returned` fields in every synthetic record. The
`count_completed_cells` tests (`test_count_completed_cells_informants`,
`test_count_completed_cells_failures`) assert that grouping uses `model_id`
as the key — records from a different campaign with the same `model_id` are
correctly counted or excluded. The `test_resume_skips_complete_triple` test
confirms skipping is keyed on `model_id`, not on `model_version_returned`.
The new `test_run_cell_retry_both_fail` test additionally asserts that the
`failure_context` dict written to `failures.jsonl` contains `model_id`
(the correct key per pitfall 1). The dual-recording behaviour for
`model_version_returned` happens inside `run_informant()` in
`cdb_collect.runner` (covered by `tests/unit/test_runner.py`), not in the
campaign driver itself.

### Concern 6 — `campaign_id` substring in `qa_notes`
**Status: Adequately covered by existing tests**

The fixture helper writes `qa_notes = f"campaign_id={campaign_id}"` at line 53.
`test_count_completed_cells_informants` explicitly tests that records from
`"other-campaign"` are not counted toward the target campaign, confirming the
substring-match filter. `test_success_rate_excludes_other_campaigns` makes the
same assertion for the `compute_success_rates` path. The new
`test_run_cell_retry_both_fail` test asserts `failure_context["campaign_id"]`
is the correct string, confirming the campaign_id is embedded in the failure
context dict that becomes the `qa_notes` equivalent for failure rows.

### Concern 7 — phi-4 adaptive max_tokens path
**Status: Covered by existing tests in the correct location**

The `run_phase4b_variance.py` script has zero phi-4-specific code. The
campaign driver calls `run_informant()`, which delegates to the OpenRouter
adapter, which calls `compute_effective_max_tokens()`. The adaptive cap is
fully covered by:
- `tests/unit/test_adaptive_cap.py`: 9 tests including `test_phi4_typical_prompt`
  and `test_phi4_small_prompt`
- `tests/unit/test_runner_max_tokens.py`: `test_run_informant_records_adaptive_max_tokens_phi4_style`

Adding a duplicate test in `test_run_phase4b_variance.py` would test the
OpenRouter adapter layer, not the campaign driver. The concern is satisfied
at the correct abstraction level.

---

## 3. No real API calls confirmation

```
grep -n "anthropic\.Anthropic\|openai\.OpenAI\|google\.generativeai\|xai\.\|openrouter\.OpenRouter\|httpx\.\(Client\|AsyncClient\)\|aiohttp\.ClientSession\|requests\.get\|requests\.post" tests/unit/test_run_phase4b_variance.py
```

Zero hits. The test file uses `model_id` strings like `"anthropic/claude-opus-4.6"`
only as data values in synthetic fixture dicts — not as constructor arguments
for any provider SDK. All four preflight tests mock `_check_provider_available`
via `unittest.mock.patch` and confirm the mock is invoked (or assertably not
invoked) rather than calling through to a real provider. All new `run_cell` and
`provider_worker` tests mock `_run_one_informant`, `append_record`, `append_failure`,
and `run_cell` at the module level. CLAUDE.md §6 R9 satisfied.

---

## 4. Fixture verification

All fixtures are synthetic inline dicts constructed in `_make_informant_jsonl_line()`
and `_make_failure_jsonl_line()` within the test module itself. No fixtures were
created under `tests/fixtures/` because the test data is simple enough to construct
inline and does not represent canned model responses. The fixture README convention
(`tests/fixtures/README.md` does not exist as a separate file but the pattern
requires no fixtures directory for synthetic data) is satisfied. CLAUDE.md §6 R9
(pitfall 9) satisfied.

---

## 5. Full suite regression

```
uv run pytest --no-header -q
```

Before new tests: **1202 passed** (established baseline from T3 tester verdict + 27
phase4b tests).
After new tests: **1207 passed** — 5 new tests added, no regressions.

```
uv run ruff check tests/unit/test_run_phase4b_variance.py
```
Result: **All checks passed.**

```
uv run mypy packages/
```
Result: **Success: no issues found in 55 source files.**

---

## 6. Tests written (this session)

| File | Function | Covers |
|---|---|---|
| `tests/unit/test_run_phase4b_variance.py` | `test_run_cell_retry_first_fail_second_pass` | Retry budget: attempt-1-fail / attempt-2-pass → 1 informant appended, 0 failures |
| `tests/unit/test_run_phase4b_variance.py` | `test_run_cell_retry_both_fail` | Retry budget: both-fail → 0 informants, 1 failure row with correct context fields |
| `tests/unit/test_run_phase4b_variance.py` | `test_provider_worker_exits_when_spend_cap_reached` | Spend cap: worker exits without calling run_cell when cap already met |
| `tests/unit/test_run_phase4b_variance.py` | `test_append_success_rates_preserves_preexisting_rows` | PROMPT_EVOLUTION_LOG append-only: prior row survives, placeholder survives, new row present |
| `tests/unit/test_run_phase4b_variance.py` | `test_append_success_rates_new_row_after_placeholder` | PROMPT_EVOLUTION_LOG: new rows inserted after the pending placeholder, not before |

---

## Notes (forward-carry)

1. **SIGINT handler** — `_handle_sigint` sets `_shutdown_requested = True` and
   prints a hint. Testing this in CI unit tests requires OS-level signal delivery
   to the test process, which is fragile without process isolation. If a
   campaign-driver integration test harness is added in Phase 5+, the SIGINT
   path should be included. Not a blocking gap for this PR.

2. **`run_cell` does not return `"SPEND_CAP"`** — the docstring at line 499 lists
   `"PASS" | "FAILED" | "SPEND_CAP"` as return values, but the spend-cap check
   happens in `provider_worker` (not `run_cell`). `run_cell` itself only returns
   `"PASS"` or `"FAILED"`. The docstring is slightly misleading but the
   behaviour is correct. No code change required; this is a documentation issue
   for the Coder to address in a follow-up.

---

*Verdict filed by LSB Tester agent (Sonnet 4.6). Only Mark can override a FAIL.*
