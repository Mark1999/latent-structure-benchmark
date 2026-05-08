# Tester Verdict — Preflight 429-Detection Fix

**Commit:** `6f88f68`  
**Task:** Preflight 429-detection fix (chained exception chain walk for `PartialSessionError` wrapping `RuntimeError("...after N retries")` from `RuntimeError("HTTP 429: ...")`)  
**Date:** 2026-05-08  
**Tester:** LSB Tester agent (claude-sonnet-4-6)

---

## TESTER VERDICT: PASS

---

## Tests written

None added. This is a validation run of tests the Coder wrote (commit `6f88f68`,
Reviewer PASS at `docs/status/2026-05-08-preflight-429-fix-reviewer-verdict.md`).

---

## Test run output

### Targeted file

```
uv run pytest tests/unit/test_run_phase4b_variance.py -v
37 passed in 0.83s
```

All 37 tests passed. Test names confirmed in verbose output:

- `test_run_plan_full_size` through `test_run_plan_v2_soft1_included` (6 tests)
- `test_resume_skips_complete_triple` through `test_resume_skips_triple_saturated_by_failures` (5 tests)
- `test_preflight_excludes_all_models_of_quota_exhausted_provider` through `test_preflight_openai_quota_exhausted` (4 tests)
- `test_exc_chain_str_single_exception` (new)
- `test_exc_chain_str_chained_exception` (new)
- `test_is_quota_exhausted_detects_direct_429` (new)
- `test_is_quota_exhausted_detects_chained_429` (new)
- `test_is_quota_exhausted_returns_false_for_unrelated_error` (new)
- `test_is_quota_exhausted_returns_false_for_network_timeout` (new)
- `test_check_provider_available_detects_chained_429_error` (new — regression test)
- `test_check_provider_available_returns_true_for_transient_parse_error` (new)
- `test_success_rate_*` (6 tests)
- `test_20_model_ids` through `test_n_runs_per_cell_is_5` (4 tests)
- `test_run_cell_retry_first_fail_second_pass` (new)
- `test_run_cell_retry_both_fail` (new)
- `test_append_success_rates_*` (2 tests)

Count reconciliation: Reviewer reported 37 total. Verified: 28 pre-existing + 9 new = 37.

### Full suite

```
uv run pytest
1212 passed, 26313 warnings in 13.26s
```

Matches Reviewer's reported count exactly.

### Linting

```
uv run ruff check .
All checks passed.

uv run mypy packages/
Success: no issues found in 55 source files
```

---

## Regression test validation

`test_check_provider_available_detects_chained_429_error` was read and verified
to correctly reproduce the bug scenario:

1. Constructs a three-level chained exception: `Exception("openai API call failed
   after 5 retries")` (PartialSessionError-shaped outer) → `RuntimeError("openai
   API call failed after 5 retries")` (retry exhaustion wrapper) → `RuntimeError(
   'HTTP 429: {"error":{"type":"insufficient_quota",...}}')` (the original adapter
   error). The `__cause__` links are explicit.

2. Asserts `"429" not in str(outer).lower()` to confirm the bug scenario
   (outer `str()` contains no quota marker — this is what the old code checked and
   missed).

3. Patches `asyncio.run`, `MODEL_REGISTRY`, `_create_adapter`, and `load_domain`
   so no real async infrastructure or provider adapter is invoked. No live API
   calls.

4. Asserts `result is False` from `_check_provider_available(...)`, proving the
   fix correctly detects the quota signal buried two levels down in the `__cause__`
   chain.

---

## Marker coverage smoke test

`_is_quota_exhausted()` called directly against nine synthetic exception shapes
covering all known provider 429/quota surfaces:

| Case | Expected | Result |
|---|---|---|
| OpenAI `insufficient_quota` direct | True | True |
| OpenAI `rate_limit_exceeded` direct | True | True |
| Anthropic `overloaded` (529→overloaded_error) | True | True |
| Google `RESOURCE_EXHAUSTED` direct | True | True |
| xAI / OpenRouter `too many requests` direct | True | True |
| Generic `rate_limit_exceeded` token | True | True |
| Chained: outer has no marker, inner has `insufficient_quota` | True | True |
| Unrelated error (timeout) | False | False |
| Parse error (JSON parse failure) | False | False |

All 9 smoke cases passed.

---

## Campaign status

Running campaign confirmed undisturbed:

```
lsb  1285886  0 15:39 pts/5  /opt/lsb-agent/.venv/bin/python3 scripts/run_phase4b_variance.py
```

PID 1285886 is still running. The source-file edit applies only at import time;
the already-loaded module in the running process is unaffected. No disruption.

---

## Coverage gaps

None. All 9 new public helpers (`_QUOTA_MARKERS`, `_exc_chain_str`,
`_is_quota_exhausted`, and the refactored `_check_provider_available`) have
happy-path and error-path tests. The marker tuple itself is smoke-tested against
real provider 429 message shapes.

---

## Failures

None.
