# Phase 4a.1 T4.2-followup — Tester Verdict

**Date:** 2026-05-01
**Tester:** LSB Tester agent
**Task:** #21.T4.2-followup
**Commit reviewed:** `072fcbd` (Coder D24/D25 changes)
**Augmenting commit:** `dad1d15`
**Verdict:** AUGMENTED-PASS

---

## Test run (post-augmentation)

```
46 passed in 0.27s
```

`uv run ruff check tests/test_phase4a1_note_j_crosstab.py` — clean.

---

## Coverage point mapping

| # | Point | Test(s) | Status |
|---|---|---|---|
| 1 | D24 single-provider mechanism wording | `test_d24_single_provider_mechanism_wording` | PRESENT (072fcbd) |
| 2 | D24 multi-provider mechanism wording | `test_d24_multi_provider_mechanism_wording` | PRESENT (072fcbd) |
| 3 | D25 plain-CONFIRMED guardrail in markdown | `test_d25_plain_confirmed_guardrail_in_markdown` | PRESENT (072fcbd) |
| 4 | `n_providers == 0` error path | `test_n_providers_zero_with_confirmed_threshold_raises` | **ADDED** (dad1d15) |
| 5 | Symmetric guardrail in CONFIRMED-with-mechanism | `test_d25_confirmed_with_mechanism_branch_also_has_guardrail` | **ADDED** (dad1d15) |
| 6 | D27 regression — "not what the model believes" absent | `test_no_forbidden_vocabulary_in_markdown` (asserts `"the model believes" not in md_lower`, which subsumes "not what the model believes") | PRESENT (pre-existing) |
| 7 | Round-trip determinism | `test_run_is_deterministic` (Markdown), `test_run_json_output_is_deterministic` (JSON) | PRESENT (prior augmentation) |

---

## Gaps found

**Gap #4 — `n_providers == 0` error path.**
The script raises `ValueError` at line ~549 when `n_providers == 0` and
`total_safety_blocked >= NOTE_K_CONFIRMED_THRESHOLD`. No existing test called
`compute_note_k_disposition` in that state. Added
`test_n_providers_zero_with_confirmed_threshold_raises`: constructs 5
`safety_event_attribution` manual classifications and passes an empty
`secondary_view_a["cross_provider_table"]` directly to the function; asserts
`ValueError` matching `"n_providers == 0"`.

**Gap #5 — D25 symmetric guardrail in CONFIRMED-with-mechanism branch.**
`test_d25_plain_confirmed_guardrail_in_markdown` (Coder, 072fcbd) proved the
guardrail fires in the plain-CONFIRMED branch only. D25 option (b) binds both
branches. Added `test_d25_confirmed_with_mechanism_branch_also_has_guardrail`:
runs the 2-provider 9-row fixture (disposition = CONFIRMED-with-mechanism),
asserts the substring `"a mechanism description, not a claim about the model's
internal state"` appears in normalised Markdown.

**Gap #6 — evaluated and closed without a new test.**
The coverage-point spec asks for a regex assertion that output never contains
`"not what the model believes"` (the deprecated wording). The existing
`test_no_forbidden_vocabulary_in_markdown` asserts `"the model believes" not in
md_lower`, which is a strict superset — it would catch `"not what the model
believes"` as a substring. No additional test needed.

---

## Constraints verified

- R10: no real API calls. All tests use in-memory synthetic fixtures.
- One commit for augmenting tests (`dad1d15`), separate from Coder commit (`072fcbd`).
- Lint clean (ruff).
- No forbidden vocabulary in test fixtures or comments.

---

## Total test count

46 (up from 44 at Coder commit `072fcbd`).

---

*End of Tester verdict. AUGMENTED-PASS. Two gaps closed in commit `dad1d15`.*
