# Tester Verdict — OPS-T3 Picker Helpers

**Date:** 2026-05-01
**Task:** OPS-T3 — four picker helper functions in `apps/ops_dashboard/lib/picker.py`
**Verdict:** AUGMENTED-PASS

---

## Initial run (25 tests from commit 92bb163)

All 25 tests passed: `25 passed in 0.14s`.

---

## Coverage gap analysis

Mapped the 12 required coverage points against the 25 shipped tests:

| # | Coverage point | Status before augmentation |
|---|---|---|
| 1 | `available_model_ids` sorted + deduplicated | COVERED (3 tests) |
| 2 | `available_domains` sorted + deduplicated | COVERED (3 tests; missing single-record shape) |
| 3 | `apply_filters([], [])` returns all | COVERED |
| 4 | `apply_filters([model], [])` single model | COVERED |
| 5 | `apply_filters([], [domain])` single domain | COVERED |
| 6 | `apply_filters([model], [domain])` AND/intersection | COVERED |
| 7 | `apply_filters([m1, m2], [])` OR within model axis | PARTIALLY COVERED — no test for OR-with-phantom (one real, one nonexistent model) |
| 8 | `apply_filters([], [d1, d2])` OR within domain axis | PARTIALLY COVERED — no test for OR-with-phantom |
| 9 | `apply_filters([m1,m2],[d1,d2])` multi-value both | COVERED |
| 10 | `available_informant_ids` sorted unique IDs | COVERED (4 tests) |
| 11 | Empty record list across all functions | COVERED |
| 12 | No real file I/O | CONFIRMED — all tests use in-memory `_make_record()` factory |

**Gaps found:**

- **#7:** No test for OR-within-model-axis with a partial match (one real model + one phantom model in `model_ids`). The spec explicitly flags this as "important: confirm empty list = all semantics distinct from no records match." The existing `test_filter_multi_model_ids` used both known models so all 5 records returned, but did not prove that a phantom entry is silently ignored rather than suppressing results.
- **#8:** Same gap on the domain axis — no phantom-entry test.
- **#2:** Missing `test_single_record` in `TestAvailableDomains` to match the shape of `TestAvailableModelIds`.

---

## Augmentation

Three tests added in `/opt/lsb-agent/tests/test_ops_dashboard_app.py`:

1. `TestApplyFilters::test_filter_multi_model_ids_or_semantics_with_phantom` — `apply_filters(records, model_ids=["gpt-4o", "nonexistent-model"], domains=[])` must return exactly the 2 gpt-4o records; proves OR, not AND, and proves phantom entries are ignored.
2. `TestApplyFilters::test_filter_multi_domains_or_semantics_with_phantom` — mirrors above for domain axis; `["food", "nonexistent-domain"]` returns 2 food records.
3. `TestAvailableDomains::test_single_record` — single record returns a one-element list; matches shape of existing `TestAvailableModelIds::test_single_record`.

---

## Final run (28 tests)

```
28 passed in 0.16s
ruff: All checks passed!
mypy: Success: no issues found in 1 source file
```

---

## Constraints verified

- R10 (no real API calls): confirmed — no live model calls anywhere in the test file.
- No reads from `data/raw/informants.jsonl`: confirmed — all records built via `_make_record()` factory.
- No forbidden vocabulary in committed text.
- One commit for this augmentation task.
