# Tester Verdict — max_tokens metadata fix (commit 75917d0)

**Date:** 2026-05-07
**Task:** Regression-only check + new-test isolation + adapter spot-check
**Scope:** `AdapterResult.max_tokens_used` threaded through 5 adapters + runner; DATA_DICTIONARY.md v0.1.13 bump

---

## Commands run and results

### 1. Full test suite

```
uv run pytest
```

Result: **1175 passed, 0 failed** in 13.60s (26313 warnings — pre-existing sklearn/numpy RuntimeWarnings, unrelated to this change). Matches Coder's reported baseline + 4 new tests (1171 → 1175).

### 2. Linter

```
uv run ruff check .
```

Result: **All checks passed!** (clean)

### 3. Type checker

```
uv run mypy packages/
```

Result: **Success: no issues found in 55 source files** (one unused-section note in pyproject.toml for streamlit — pre-existing, not introduced by this change)

---

## 4 new tests in isolation

```
uv run pytest tests/unit/test_runner_max_tokens.py -v
```

```
tests/unit/test_runner_max_tokens.py::test_run_informant_records_actual_max_tokens_not_hardcoded_4096  PASSED
tests/unit/test_runner_max_tokens.py::test_run_informant_records_adaptive_max_tokens_phi4_style        PASSED
tests/unit/test_runner_max_tokens.py::test_run_informant_default_adapter_result_preserves_4096         PASSED
tests/unit/test_runner_max_tokens.py::test_baseline_sort_records_actual_max_tokens                     PASSED

4 passed in 0.79s
```

All 4 pass.

---

## Adapter test spot-check

```
uv run pytest tests/ -k adapter -v --no-header | tail -20
```

53 adapter tests collected across `test_huggingface_adapter.py`, `test_openrouter_adapter.py`, `test_runner.py`, `test_runner_max_tokens.py`, and `test_xai_adapter.py`. **53 passed, 0 failed.** No existing adapter test broke from the new `AdapterResult.max_tokens_used` field — confirming that all `AdapterResult` constructions in the test suite use keyword arguments (not positional), so the new field was a clean addition.

---

## Verdict: PASS

All acceptance criteria met:

- Full suite: 1175/1175 (0 regressions; +4 from baseline 1171 confirms exactly the 4 new tests)
- 4 new tests in isolation: 4/4
- Adapter spot-check: 53/53
- ruff: clean
- mypy: clean (55 source files, 0 issues)

The `AdapterResult.max_tokens_used` field is correctly threaded through all 5 adapter implementations and the runner. No existing test was broken by the new field. The fix is complete and the max_tokens metadata is now captured in `InformantRecord`.

**T3 (Phase 4b gpt-5.4-mini + mistral-small investigation) is unblocked.**
