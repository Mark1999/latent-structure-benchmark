# Phase 4b T2 — Tester Verdict

**Task:** phi-4 adaptive max_tokens helper + 5-cell rerun
**Commit under test:** `628497d`
**Reviewer verdict (pre-Tester):** PASS-WITH-NOTES (`2026-05-07-phase4b-t2-reviewer-verdict.md`)
**Tester:** LSB Tester agent
**Date:** 2026-05-07

---

## Commands run and results

### 1. Full pytest suite

```
uv run pytest --tb=short -q
```

Result: **1171 passed, 0 failed** (13.25 s). Matches Coder-reported baseline
exactly (+18 vs. prior baseline of 1153). The 26313 warnings are pre-existing
sklearn/numpy RuntimeWarnings from MDS tests; no new warnings introduced.

### 2. ruff

```
uv run ruff check .
```

Result: **All checks passed.**

### 3. mypy

```
uv run mypy packages/
```

Result: **Success: no issues found in 55 source files.**  
(The `unused section(s): module = ['streamlit']` note is pre-existing and
not a mypy error.)

---

## Adaptive-cap tests in isolation

```
uv run pytest tests/unit/test_adaptive_cap.py -v
```

All **18 / 18 tests passed** (0.70 s):

| # | Test name | Status |
|---|---|---|
| 1 | `test_phi4_typical_prompt` | PASSED |
| 2 | `test_phi4_small_prompt` | PASSED |
| 3 | `test_large_context_returns_config_cap` | PASSED |
| 4 | `test_200k_context_returns_config_cap` | PASSED |
| 5 | `test_163k_context_returns_config_cap` | PASSED |
| 6 | `test_floor_returned_when_budget_below_minimum` | PASSED |
| 7 | `test_floor_returned_when_budget_goes_negative` | PASSED |
| 8 | `test_exact_floor_boundary` | PASSED |
| 9 | `test_approximation_uses_chars_per_token` | PASSED |
| 10 | `test_empty_prompt_uses_zero_input_tokens` | PASSED |
| 11 | `test_idempotent_phi4` | PASSED |
| 12 | `test_idempotent_large_context` | PASSED |
| 13 | `test_idempotent_floor` | PASSED |
| 14 | `test_custom_safety_margin` | PASSED |
| 15 | `test_custom_min_output_tokens` | PASSED |
| 16 | `test_custom_max_output_tokens_config` | PASSED |
| 17 | `test_adapter_context_length_default_is_unconstrained` | PASSED |
| 18 | `test_adapter_phi4_context_length_produces_reduced_cap` | PASSED |

---

## `_context_length` accessibility check (Reviewer-requested)

**File inspected:**
`packages/cdb_collect/cdb_collect/adapters/openrouter.py`, lines 52–54.

The attribute is set unconditionally in `__init__` with a type annotation:

```python
self._context_length: int = context_length if context_length is not None else (
    MAX_OUTPUT_TOKENS_CONFIG * 100  # effectively unconstrained
)
```

Findings:

- `_context_length` is a real instance attribute, not an accidental side-effect.
  It is explicitly typed `int` and always assigned during `__init__` before any
  async method can run.
- The default value (`MAX_OUTPUT_TOKENS_CONFIG * 100` = 1 638 400) is large
  enough that `compute_effective_max_tokens` with any realistic prompt will
  produce exactly `MAX_OUTPUT_TOKENS_CONFIG` (16 384), preserving the Task #16
  large-context behaviour.
- When a caller passes `context_length=16_384` (phi-4), the attribute holds
  16 384, and `_do_call` passes it directly to `compute_effective_max_tokens`.
- The two adapter-wiring tests (`test_adapter_context_length_default_is_unconstrained`
  and `test_adapter_phi4_context_length_produces_reduced_cap`) access
  `adapter._context_length` directly. This is appropriate for white-box unit
  testing of the wiring — no production code reads the private attribute from
  outside the class; only the test layer does.

Conclusion: the attribute access in the tests is intentional and structurally
sound. mypy confirms the attribute is typed correctly (`int`) and no issues
were found.

---

## Verdict

**TESTER VERDICT: PASS**

All 1171 tests pass, ruff is clean, mypy reports zero issues across 55 source
files. The 18 adaptive-cap tests pass in isolation covering all five acceptance-
criteria cases (phi-4 typical, large-context ceiling, floor/borderline,
4-chars/token approximation, idempotence) plus custom-parameter and
adapter-wiring variants. The `_context_length` attribute is a bona-fide
`__init__`-assigned typed instance attribute; its use in the wiring tests is
deliberate white-box coverage with no production-code exposure risk.

T2 closes. T3 (gpt-5.4-mini + mistral-small investigation) is unblocked.
