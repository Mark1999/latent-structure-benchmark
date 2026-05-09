# Tester Verdict — OpenRouter Parallel-Worker Fix

**Task:** Validate commit `fc1ccd1` — OpenRouter parallelism fix  
**Verdict file:** `docs/status/2026-05-09-openrouter-parallel-fix-tester-verdict.md`  
**Reviewer PASS reference:** `docs/status/2026-05-09-openrouter-parallel-fix-reviewer-verdict.md`  
**Date:** 2026-05-09  
**Tester agent:** Sonnet 4.6

---

## TESTER VERDICT: PASS

---

## Test run results

### Targeted file: `tests/unit/test_run_phase4b_variance.py`

```
40 passed in 0.84s
```

All 40 tests pass (was 37 before this commit; 3 new tests added).

### Full suite

```
1215 passed, 26313 warnings in 12.67s
```

No regressions. The warnings are pre-existing sklearn/numpy RuntimeWarnings
from MDS tests unrelated to this change.

### Ruff

```
All checks passed!
```

### mypy

```
Success: no issues found in 55 source files
```

---

## New test validation

### `test_provider_workers_constant_defined`

Checked `PROVIDER_WORKERS` is a dict, contains every key in `PROVIDER_RPM`
(all 5 providers), `openrouter == 4`, and all others (`anthropic_api`,
`openai_api`, `google_ai`, `xai_api`) equal `1`. Not a shallow existence
check — it asserts specific values per provider. Shape is correct.

### `test_provider_sleep_accounts_for_worker_count`

Iterates all 5 providers and asserts `PROVIDER_SLEEP_S[method]` equals
`(60.0 / RPM) * N_workers + 0.1` to within `1e-9`. Then spot-checks
OpenRouter explicitly: `(60/200) * 4 + 0.1 = 1.3 s`. Covers the full
formula, not just a constant check. Math is verified correctly.

### `test_main_spawns_multiple_threads_for_openrouter`

Patches `run_phase4b_variance.threading.Thread` with a fake class that
records thread names. Reproduces only the thread-spawning loop from the
production runner (not the campaign execution itself). Asserts that for
each provider the count of threads with the prefix `provider-{method}-`
equals `PROVIDER_WORKERS[method]`. The test contains `provider_worker` in its
imports (imported but not called — it is passed as the `target` arg to the
fake Thread, which never calls it). No API calls, no live threads started.
The production `provider_worker` function is referenced by name only; no
actual execution path through it occurs. CLAUDE.md §6 R9 is satisfied.

---

## Running campaign status

`pgrep -f run_phase4b_variance` returned PIDs `1249477 1466024 1473168` —
drain is still in progress. The fix does not disturb already-loaded modules;
the running campaign is unaffected.

---

## Dry-run smoke test

`uv run python scripts/run_phase4b_variance.py --dry-run` output:

- 1800 cells (20 models × 9 variants × 5 runs × 2 domains)
- All 20 models resolved in registry
- All 9 variant directories confirmed present
- Plan sample shows correct cell structure
- "DRY RUN complete. No API calls made."

Output is sensible and matches the expected shape.

---

## Coverage gaps

None. All three new public constants (`PROVIDER_WORKERS`, the
`PROVIDER_SLEEP_S` formula, and the multi-thread spawning logic) are covered
by dedicated happy-path tests. No error-path tests are required for pure
constant definitions or deterministic arithmetic.
