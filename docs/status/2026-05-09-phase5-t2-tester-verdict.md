# Phase 5 T2 — Tester Verdict

**Task:** T2 template-based lede generator  
**Commit under test:** `9e5a138` (feat(publish): T2 template-based lede generator)  
**Gate verdicts referenced:** CDA SME PASS-WITH-NOTES `1868fca`; Reviewer PASS `4e24fa2`  
**Tester verdict commit:** `f739799`  
**Date:** 2026-05-09  
**Verdict:** PASS-WITH-NOTES

---

## Test runs

### 1. Targeted file: `tests/cdb_publish/test_lede.py`

```
uv run pytest tests/cdb_publish/test_lede.py -v
12 passed in 0.16s
```

All 12 Coder-authored tests pass.

### 2. Package suite: `tests/cdb_publish/`

```
uv run pytest tests/cdb_publish/ -v
20 passed in 0.52s
```

8 T1 tests + 12 T2 tests. All pass.

### 3. Full suite

```
uv run pytest --tb=short -q
1235 passed, 26313 warnings in 13.32s
```

No regressions from prior state.

### 4. Static analysis

```
uv run ruff check .       → All checks passed!
uv run mypy packages/     → Success: no issues found in 59 source files
```

---

## Binding behavior inspection (12 Coder tests)

| Test | Pattern | What it covers | Verdict |
|------|---------|----------------|---------|
| 1 | `strong_consensus_homogeneous` | Family real corpus, n=11, S=0.71, CI=[0.50,0.91], no R1-b | PASS |
| 2 | `strong_consensus_with_low_oci` | Holidays real corpus, n=9, 2 R1-b (Q5 binding) | PASS |
| 3 | `strong_consensus_majority_low_oci` | Synthetic 3/4 R1-b majority | PASS |
| 4 | `weak_consensus` | Synthetic WEAK_CONSENSUS with S and CI formatting | PASS |
| 5 | `subcultural` | Synthetic SUBCULTURAL, negative centrality language | PASS |
| 6 | `turbulent` | Synthetic TURBULENT, S and CI formatting | PASS |
| 7 | `contested` | Synthetic CONTESTED, active divergence language | PASS |
| 8 | `all_deterministic` | All-det fixture → byte-identical DS §3.3.5 item 6 copy | PASS |
| 9 | `all_deterministic` | DETERMINISTIC consensus_type → same verbatim copy | PASS |
| 10 | vocabulary | All 8+ §1.5.4/T9/T14/B6 forbidden phrases absent across all 9 patterns | PASS |
| 11 | determinism | Same fixture → byte-identical on two calls | PASS |
| 12 | no-LLM-imports | AST check: no forbidden library imports in lede.py | PASS |

Real-corpus fixture values verified:
- family: n=11, S=0.7106→"0.71", CI=[0.5049,0.9092]→"[0.50, 0.91]", all OCI >> 3.0
- holidays: n=9, 2 models with OCI < 3.0 (mistral-small-2603: 0.0, gpt-5.4-mini: 2.55)

No real API calls. No live network requests. All tests use data/results/ fixtures or synthetic `DomainResult` objects.

---

## Coverage gap assessment

Six gaps evaluated:

| Gap | Assessment | Action |
|-----|------------|--------|
| WEAK_CONSENSUS + R1-b sub-branch interaction | Real gap — _select_pattern does not sub-branch WEAK_CONSENSUS; no test confirmed this routing | Gap-fill test written (T13) |
| n_low_oci=1 (singular) count in lede string | Real gap — test 2 uses n_low_oci=2; test 10 creates 1-R1b scenario but checks vocab only; "1 of these N" phrase never explicitly asserted | Gap-fill test written (T14) |
| Non-empty output for every valid input | Not a gap — all tests assert specific substrings, implying non-empty; no dedicated assertion needed | None |
| Smith's S 2-decimal formatting precision | Not a gap — tests 1,2,4,6,7 assert exact strings including decimal places | None |
| CI bounds 2-decimal formatting precision | Not a gap — tests 1,4,6 assert exact bracket strings | None |
| consensus_ci=None defensive edge case | Not a meaningful gap — schema defines `consensus_ci: tuple[float, float]` (non-optional); Pydantic rejects None before generate_lede is called | None |

---

## Gap-fill tests written

Gap-fill commit: `f739799`

- `/opt/lsb-agent/tests/cdb_publish/test_lede.py`: `test_weak_consensus_with_r1b_models_no_subbranch` (T13) — WEAK_CONSENSUS + 2 R1-b models routes to `weak_consensus` pattern; "low output concentration" absent from lede; regression guard against accidental sub-branch introduction
- `/opt/lsb-agent/tests/cdb_publish/test_lede.py`: `test_strong_consensus_with_low_oci_singular_count` (T14) — n_low_oci=1 with n=5 explicitly asserts "1 of these 5 models produced low output concentration" appears verbatim; verifies singular format string substitution path

Full suite after gap-fills: **1237 passed**.

---

## Notes

- The `strong_consensus_with_low_oci` template uses the pronoun "their" for both singular (n_low_oci=1) and plural cases ("1 of these N models produced... their position"). This is grammatically imprecise for the singular case. It is a template language quality issue, not a code defect. No production test fails because of it; it is noted here for the Architect's awareness. Resolving it would require lede_v2.py per CLAUDE.md §6 R7.
- 26,313 warnings in the full suite are pre-existing sklearn/numpy RuntimeWarnings from MDS tests; not introduced by T2.
