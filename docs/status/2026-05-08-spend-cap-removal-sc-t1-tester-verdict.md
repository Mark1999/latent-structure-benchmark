# Tester Verdict — SC-T1 (Strip Spend-Cap Mechanism from Variance Driver)

**Date:** 2026-05-08
**Tester:** LSB Tester agent (Sonnet 4.6)
**Commit validated:** `cf555b1`
**Commit subject:** `fix(collect): SC-T1 strip spend-cap mechanism from variance driver`
**Scope:** `scripts/run_phase4b_variance.py` and `tests/unit/test_run_phase4b_variance.py`
**Reviewer PASS prerequisite:** `docs/status/2026-05-08-spend-cap-removal-sc-t1-reviewer-verdict.md`

---

## TESTER VERDICT: PASS

---

## Validation Checklist

| # | Item | Result |
|---|---|---|
| 1 | 29 unit tests pass (`tests/unit/test_run_phase4b_variance.py -v`) | PASS — 29 passed in 0.77 s |
| 2 | Full repo suite still green | PASS — 1,204 passed in 13.49 s |
| 3 | ruff clean on both in-scope files | PASS — All checks passed |
| 4 | mypy clean on `packages/` | PASS — 55 files, 0 issues |
| 5 | `--dry-run` produces sensible plan summary with no cost lines | PASS — see detail below |
| 6 | No test name references spend / cap / cost | PASS — zero grep matches |
| 7 | Zero spend-cap tokens remaining in either file | PASS — grep exit 1 (zero matches) |

---

## Detail

### Check 1 — Unit tests (29)

```
uv run pytest tests/unit/test_run_phase4b_variance.py -v
```

All 29 tests passed. Full enumeration confirmed:

- `test_run_plan_full_size`
- `test_run_plan_correct_models`
- `test_run_plan_correct_variants`
- `test_run_plan_correct_domains`
- `test_run_plan_correct_run_indices`
- `test_run_plan_v2_soft1_included`
- `test_resume_skips_complete_triple`
- `test_resume_partial_triple_runs_remaining`
- `test_count_completed_cells_informants`
- `test_count_completed_cells_failures`
- `test_resume_skips_triple_saturated_by_failures`
- `test_preflight_excludes_all_models_of_quota_exhausted_provider`
- `test_preflight_dry_run_returns_all_models`
- `test_preflight_all_providers_healthy`
- `test_preflight_openai_quota_exhausted`
- `test_success_rate_all_pass`
- `test_success_rate_all_failed`
- `test_success_rate_mixed`
- `test_success_rate_qa_failed_informant_counted_as_failed`
- `test_success_rate_excludes_other_campaigns`
- `test_success_rate_empty_corpus`
- `test_20_model_ids`
- `test_9_prompt_versions`
- `test_2_domains`
- `test_n_runs_per_cell_is_5`
- `test_run_cell_retry_first_fail_second_pass`
- `test_run_cell_retry_both_fail`
- `test_append_success_rates_preserves_preexisting_rows`
- `test_append_success_rates_new_row_after_placeholder`

No test name contains the words "spend", "cap", or "cost" (confirmed by grep).

### Check 2 — Full suite

```
uv run pytest
```

Result: 1,204 passed, 26,313 warnings (pre-existing sklearn/numpy RuntimeWarnings —
not regressions), in 13.49 s. No new failures.

### Check 3 — Ruff

```
uv run ruff check scripts/run_phase4b_variance.py tests/unit/test_run_phase4b_variance.py
```

Result: `All checks passed!`

### Check 4 — mypy

```
uv run mypy packages/
```

Result: `Success: no issues found in 55 source files`

Note: running mypy directly against `scripts/run_phase4b_variance.py` produces a
pre-existing path-resolution error (`Cannot find implementation or library stub for
module named "collect"`) that also existed pre-SC-T1. The standard LSB mypy target
is `packages/` per CLAUDE.md §11. Clean.

### Check 5 — Dry-run output

```
uv run python scripts/run_phase4b_variance.py --dry-run
```

Output confirms:
- Campaign ID printed: `phase4b-real-2026-05-08`
- Total target cells: `20 models × 9 variants × 5 runs × 2 domains = 1800`
- All 20 models validated OK via `MODEL_REGISTRY`
- All 9 variant directories validated OK
- Sample of first 10 cells shown
- Terminates with: `DRY RUN complete. No API calls made.`
- Zero lines containing "Spend", "cost", "cap", or "$N.NN" dollar amounts

Grep confirmation:
```
grep -iE "spend|cost|cap|\$[0-9]"  → NO COST/SPEND LINES — clean
```

### Check 6 — No spend/cap/cost test names

```
grep -n "def test_" tests/unit/test_run_phase4b_variance.py | grep -iE "spend|cap|cost"
```

Result: `NO MATCHES — clean`

### Check 7 — Zero spend-cap tokens in both files

```
git grep -nE 'CDB_MAX_SPEND_USD|MAX_SPEND_USD|DEFAULT_MAX_SPEND|spend_cap|cost_cap|
  cost-cap-usd|--max-spend|estimate_cell_cost_usd|total_spend_usd|add_spend' \
  -- scripts/run_phase4b_variance.py tests/unit/test_run_phase4b_variance.py
```

Result: exit code 1 (zero matches). All spend-cap tokens fully removed from both files.

---

## Coverage Gap Assessment

SC-T1 is a pure removal task. The three deleted tests
(`test_provider_worker_exits_when_spend_cap_reached`,
`test_estimate_cell_cost_usd_known_model`,
`test_estimate_cell_cost_usd_missing_model`) covered code that no longer exists.
Their absence is correct, not a gap.

All surviving code paths through the variance driver — run-plan generation, resume
logic, preflight, success-rate computation, retry budget, append-only log writes —
remain covered by the 29 retained tests. No forward-carry gaps identified.

---

## No Commits Made

Working tree was clean at `6959b67` before validation and remains clean. No files
modified outside SC-T1 testing scope.

---

*Verdict filed by LSB Tester agent (Sonnet 4.6). Only Mark can override a FAIL.*
