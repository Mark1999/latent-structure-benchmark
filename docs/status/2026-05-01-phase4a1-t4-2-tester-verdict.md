# Tester Verdict — Phase 4a.1 T4.2 Note J Cross-tab + K-frame/K-vocab Subtype (task #21.T4.2)

**Filed:** 2026-05-01
**Tester:** LSB Tester (claude-sonnet-4-6)
**Commit under review:** `8a3fe36`
**Augmenting commit:** see §5
**Task:** #21.T4.2 — Note J cross-tab + K-frame/K-vocab subtype (Amendment 2 §3 T4 + Amendment 3 §3.2)
**Gate verdicts cited:**
- Architect Amendment 3: `docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md`
- CDA SME PASS-WITH-NOTES: `docs/status/2026-04-30-phase4a1-amendment-3-cda-sme-verdict.md`
- Reviewer PASS-WITH-NOTES: `docs/status/2026-05-01-phase4a1-t4-2-reviewer-verdict.md`

---

## TESTER VERDICT: AUGMENTED-PASS

37 existing tests all passed on commit `8a3fe36`. 4 gap tests were added (41 total). All 41 pass. Full suite: 780 passed, 0 failures.

---

## 1. Baseline run

```
uv run pytest tests/test_phase4a1_note_j_crosstab.py -v
37 passed in 0.19s
```

All 37 pre-existing tests passed against commit `8a3fe36` without modification.

---

## 2. Coverage mapping — 10 Amendment 3 §3.2 points

| Point | Description | Tests covering | Status |
|---|---|---|---|
| 1 | Synthetic 9-row fixture split 5/4, two providers | `_build_amendment3_9row_fixture` + `test_amendment3_9row_*` (8 tests) | COVERED |
| 2 | All four Note K disposition tiers (5 tiers total) | `test_note_k_confirmed_with_mechanism_two_providers`, `test_note_k_confirmed_single_provider`, `test_note_k_inconclusive_suggestive`, `test_note_k_inconclusive_single_row`, `test_note_k_not_confirmed_no_safety_rows` | COVERED |
| 3 | D21 disposition-arithmetic invariance | `test_cross_provider_subtype_asymmetry_surfaced_not_disposition_shifted` | COVERED |
| 4 | Subtype artifact validation paths | `test_missing_subtype_artifact_raises`, `test_unclassified_subtype_raises`, `test_unclassified_subtype_error_names_row`, `test_subtype_id_not_in_parent_classification_raises`, `test_subtype_non_safety_parent_raises` | COVERED |
| 5 | Subtype column rendering; "n/a" for blocked | `test_blocked_rows_get_na_subtype` | COVERED |
| 6 | "Note K mechanism breakdown" sub-section; two-row minimum | `test_amendment3_9row_note_k_mechanism_breakdown_in_markdown` (header); **`test_note_k_mechanism_breakdown_table_has_both_subtype_rows`** (body, ADDED) | COVERED + AUGMENTED |
| 7 | No-LLM-imports static check | `test_no_llm_imports_in_script`, `test_no_llm_imports_in_imported_modules` | COVERED |
| 8 | Forbidden vocabulary check | `test_no_forbidden_vocabulary_in_markdown` | COVERED |
| 9 | Round-trip determinism (Markdown + JSON) | `test_run_is_deterministic` (Markdown); **`test_run_json_output_is_deterministic`** (JSON, ADDED) | COVERED + AUGMENTED |
| 10 | Empty subtype artifact handling | `test_unclassified_subtype_raises` (one row); the error path is identical for N rows since each UNCLASSIFIED row individually triggers the error | COVERED |

---

## 3. Gaps found and addressed

### Gap A — 1-provider 9-row path (ADDED: `test_nine_row_single_provider_yields_confirmed`)

The Reviewer's "Notes for Tester" item 1 flagged explicitly: "A separate 1-provider 9-row fixture (matching actual production data) would improve coverage." The existing tests only exercised the 2-provider CONFIRMED-with-mechanism branch for 9-row fixtures. The augmenting test constructs 9 safety rows from a single provider (`google`), mixed subtypes (2 k_frame + 7 k_vocab, mirroring the actual production split), and asserts:

- `disposition == "CONFIRMED"` (not `CONFIRMED-with-mechanism`)
- `n_providers == 1`
- `disposition_string == "Note K: CONFIRMED"` (bare tier label, no mechanism fragment in headline per D20)
- The Markdown section heading is still present
- `"Note K: CONFIRMED-with-mechanism"` does not appear in Markdown

This is the path that the actual production run will exercise (all 9 real safety rows are from google per the Reviewer verdict).

### Gap B — JSON output determinism (ADDED: `test_run_json_output_is_deterministic`)

`test_run_is_deterministic` compared `md1 == md2` only. The task brief point 9 specifies "byte-identical Markdown + JSON output." The augmenting test calls `run()` twice on the same fixture and compares `json.dumps(json_out, sort_keys=True)` for both runs.

### Gap C — Note K mechanism breakdown table body (ADDED: `test_note_k_mechanism_breakdown_table_has_both_subtype_rows`)

Amendment 3 §3.2: "Two-row format minimum: one row per subtype." The existing test only verified the section heading string. The augmenting test additionally asserts that both `k_frame` and `k_vocab_without_k_frame` appear as content in the Markdown section below the heading, and that `provider_subtype_counts` in the JSON has both subtype keys populated.

### Gap D — Empty decline_interviews file raises ValueError (ADDED: `test_empty_decline_interviews_file_raises`)

The script raises `ValueError` with "No rows found" when `decline_interviews.jsonl` exists but has zero rows (line 164 of script). No pre-existing test exercised this path. The augmenting test writes an empty (zero-byte) `di.jsonl` file and asserts `ValueError` with the expected message.

---

## 4. Test run output

```
uv run pytest tests/test_phase4a1_note_j_crosstab.py -v
41 passed in 0.27s

uv run pytest tests/ -q
780 passed, 26313 warnings in 11.84s
```

No regressions. `uv run ruff check tests/test_phase4a1_note_j_crosstab.py` → All checks passed.

---

## 5. Augmenting commit

Commit message: `test(scripts): augment T4.2 fixture coverage (task #21.T4.2)`

Tests added (4):
- `tests/test_phase4a1_note_j_crosstab.py::test_nine_row_single_provider_yields_confirmed` — 1-provider 9-row path yields CONFIRMED, addresses Reviewer "Notes for Tester" item 1
- `tests/test_phase4a1_note_j_crosstab.py::test_run_json_output_is_deterministic` — JSON output determinism, closes gap B
- `tests/test_phase4a1_note_j_crosstab.py::test_note_k_mechanism_breakdown_table_has_both_subtype_rows` — two-row minimum in breakdown table, closes gap C
- `tests/test_phase4a1_note_j_crosstab.py::test_empty_decline_interviews_file_raises` — empty decline_interviews file error path, closes gap D

---

## 6. Coverage gaps remaining

None. All 10 Amendment 3 §3.2 coverage points are exercised by the combined 41-test suite. The Reviewer's explicit Tester note (item 1) is addressed by `test_nine_row_single_provider_yields_confirmed`. No functions in the script are left without at least a happy-path and an error-path test.

---

*End of Tester verdict for task #21.T4.2. Filing at `docs/status/2026-05-01-phase4a1-t4-2-tester-verdict.md`.*
