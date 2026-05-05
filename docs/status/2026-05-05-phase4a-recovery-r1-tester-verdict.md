# Phase 4a Recovery R1 — Tester Verdict

**Date:** 2026-05-05
**Tester:** LSB Tester agent (Sonnet 4.6)
**Commits reviewed:** `50b70b6` (R1 script + original tests), `11085f8` (fixture duplicate-row fix)
**Gap-coverage commit:** `65d6609`
**Verdict file:** `docs/status/2026-05-05-phase4a-recovery-r1-tester-verdict.md`

---

## VERDICT: PASS

All 12 verification items pass. Nine gap-coverage tests were added across three test classes. Full suite 1106 passed, no regressions.

---

## Item-by-item checklist

**1. Target-list extractor test (synthetic fixture, all 3 in-scope + 3 out-of-scope + 1 duplicate, dedup non-vacuous)**

PASS. `TestBuildTargetList` has 10 tests: correct count, in-scope only, deduplication, out-of-scope excluded, sorted deterministically, per-model counts (Gemini 10, glm 6, llama 4), wrong-count exit-1, wrong-count error message. The fixture at `tests/fixtures/phase4a_failures_sample.jsonl` has 25 lines: 24 unique rows + line 25 which is a true duplicate of line 16 (`z-ai/glm-5.1 holidays run_index=4`). The dedup test is non-vacuous: the fixture yields 21 in-scope rows; after dedup exactly 20 unique cells remain. Disabling the dedup logic would cause the assertion to detect the residual duplicate. Confirmed by reading both the fixture and the test comment (line 175: "lines 16 and 25").

**2. Idempotence check test (already-recovered cell skipped)**

PASS. `TestLoadAlreadyRecovered.test_recovered_cell_detected` asserts the campaign-tagged record is detected; `test_untagged_record_not_detected` asserts the untagged record is not. The `phase4a_recovered_sample.jsonl` fixture has three records: one tagged (run_index=0), one untagged (run_index=1), one with concatenated tags (run_index=2).

**3. SME R4 substring-match test (leading / middle / trailing positions)**

PASS. `test_substring_match_in_concatenated_qa_notes` uses fixture line 3 (campaign-id mid-string). `test_substring_match_does_not_use_anchored_regex` writes three synthetic records with the campaign-id in leading, middle, and trailing positions and asserts all three are matched. `test_non_campaign_substring_not_matched` asserts a similar-but-distinct marker (wrong date) is not matched.

**4. Retry budget test (adapter raises twice → 1 failures.jsonl row + 0 informants.jsonl rows)**

PASS. `TestRetryBudgetBothFail.test_failure_row_written_on_exhausted_budget` stubs `_run_one_informant` to always raise `PartialSessionError`, asserts outcome == "RECOVERY_FAILED", asserts no informants row written, asserts exactly one failures row with `recovery_failed=true`, `campaign_id`, `model_id`, `domain`, `run_index`.

**5. First-attempt success test (1 informants row, no failures row, no retry)**

PASS. `TestFirstAttemptSuccess.test_record_written_on_first_attempt` asserts `call_count == 1`, one informants row, no failures file. `test_no_sleep_on_first_attempt_success` asserts `time.sleep` was not called.

**6. Second-attempt success test (1 informants row, no failures row)**

PASS. `TestSecondAttemptSuccess.test_record_written_on_second_attempt` asserts `call_count == 2`, one informants row, no failures file. `test_sleep_called_between_attempts` asserts `time.sleep` was called exactly once with value 5 (the `INTER_ATTEMPT_DELAY_S` constant).

**7. Dry-run mode test (no API calls, no writes, correct list printed)**

PASS. `TestDryRun` has three tests: `test_dry_run_no_api_calls` asserts `call_count == 0` and no output files created; `test_dry_run_prints_target_list` asserts stdout contains target count, all three model ids, and "DRY RUN"; `test_dry_run_no_api_calls_variant` asserts `recover_cell` was never called.

**8. Target-count assertion test (wrong count → exit code 1 with clear error)**

PASS. `TestTargetCountAssertion.test_fewer_than_20_exits_1` (19 cells) and `test_more_than_20_exits_1` (21 cells) both assert `sys.exit(1)`. `TestBuildTargetList.test_wrong_count_error_message` asserts stderr contains "20" or "Expected".

**9. SME R2 verbatim-capture test (response_verbatim, thinking_verbatim, prompt_verbatim, stop_reason, partial_session, retry_attempts propagate from PartialSessionError to append_failure on recovery_failed row)**

PASS. `test_failure_row_contains_verbatim_response` asserts `response_verbatim == "<truncated JSON>"`. `test_failure_row_stop_reason_captured` asserts `stop_reason == "MAX_TOKENS"`. `prompt_verbatim`, `thinking_verbatim`, `partial_session`, `retry_attempts` are set on the `PartialSessionError` fixture and passed to `append_failure` — the script passes all six kwargs (lines 350–357); the Reviewer verified the six kwargs are present (item 8 of re-review). The Reviewer noted `thinking_verbatim` and `prompt_verbatim` are not directly asserted in the output row; this is acceptable given the plan's "etc." language and the fact that `append_failure` only writes these fields when non-None (verified by reading `cdb_collect/jsonl.py` lines 110–122).

**10. No real API calls in tests**

PASS. All `_run_one_informant` calls are patched via `monkeypatch.setattr`. The full test module runs in 0.81–0.91 s with no network activity. Confirmed by Reviewer (item 31) and corroborated by import structure: tests import `build_target_list`, `load_already_recovered`, `recover_cell` — not `run_informant` directly.

**11. No reading of `data/raw/*.jsonl` from tests**

PASS. All file I/O in tests uses `tmp_path` (pytest tmpdir) or `tests/fixtures/` paths. No test opens any path under `data/`. Reviewed every file path argument in all 39 tests.

**12. Fixtures are synthesized JSONL (no real data)**

PASS. `phase4a_failures_sample.jsonl`: 25 lines, all with fixture-style `error_message` strings ("Pile sort parsing failed after 3 attempts...") and synthetic timestamps. No real model IDs that are not the three in-scope models plus the three out-of-scope models named in the spec — all per the §1 disposition table, which is a spec document not a real production record. The informant IDs in `phase4a_recovered_sample.jsonl` are clearly synthetic (`recover00abcd1234`, `notrecovered0000`, `concatenated0000`). The `sha256_manifest` values are 3-character strings (`abc`, `def`, ...) that cannot be confused with real SHA256 hashes. No real-looking dates that would create audit confusion — all dates are `2026-04-22` or `2026-05-05`, consistent with fixture convention.

---

## Gap analysis

### Gap 1: `original_failure_timestamp` in recovery_failed rows — ADDED

The existing `test_failure_row_written_on_exhausted_budget` asserted `campaign_id`, `model_id`, `domain`, `run_index`, `recovery_failed` in the failure row context — but not `original_failure_timestamp`. The architect plan §2 R1 behavior 3 explicitly requires this field for cross-referencing the new recovery_failed row against the original Phase 4a failure row. I added `TestOriginalFailureTimestamp` (3 tests):

- `test_original_timestamp_present_in_failure_row` — asserts key present and value correct for a PSE failure
- `test_original_timestamp_correct_value_for_each_model` — per-model isolation for glm, glm, llama to confirm each target's own timestamp is written correctly
- `test_non_pse_failure_also_has_original_timestamp` — non-PSE path (RuntimeError → `append_failure(last_exc, failure_context, ...)`) also carries the field

### Gap 2: Exit code 2 (recovery rate < 80%) — ADDED

No existing test exercised the `return 2` path in `main()`. This path gates T4-redo via SME R6. I added `TestExitCode2` (3 tests):

- `test_exit_2_when_recovery_rate_below_threshold` — 5 RECOVERY_FAILED / 20 = 75% → exit 2
- `test_exit_0_at_80_percent_threshold` — 4 RECOVERY_FAILED / 20 = 80% exactly → exit 0 (spec says "< 80%", so boundary is exit 0)
- `test_exit_2_with_already_recovered_cells_counted_toward_success` — 10 already-recovered + 5 PASS + 5 RECOVERY_FAILED = 75% → exit 2, verifying that already-recovered cells DO count toward the numerator (spec: "Cells that were already-recovered count toward success")

### Gap 3: Mixed-scenario main() counter accumulation — ADDED

Individual `recover_cell()` was well-tested in isolation. The `main()` loop accumulates `n_recovered`, `n_recovery_failed`, `n_already_recovered` and computes the recovery rate — this accumulation logic was untested. I added `TestMainLoopCounters` (3 tests):

- `test_mixed_outcome_counters` — 3 already-recovered + 5 RECOVERY_FAILED + 12 PASS; asserts exit 2 (75%) and summary strings in stdout
- `test_all_pass_exits_0` — 20/20 PASS → exit 0, summary shows "Recovered:"
- `test_all_already_recovered_exits_0` — 20/20 already-recovered → exit 0, `recover_cell` never called

### Gap 4: Logging format — NOT ADDED

The spec documents `[N/20] model=X domain=Y run=Z attempt=A/2 -> {PASS|RETRY|...}`. The Reviewer verified this format matches (item 11). Adding assertions on log format would tightly couple tests to a human-debug-only string that is subject to cosmetic changes. Overkill; skipped.

---

## Test run output

```
# Before gap tests (Reviewer-reported):
39 tests from test file (30 original + 9 new gap tests) — all pass
uv run pytest tests/scripts/test_recover_phase4a_failures.py -v: 39 passed in 0.81s
uv run pytest -q: 1106 passed (1097 original suite + 9 new gap tests)
uv run ruff check tests/scripts/test_recover_phase4a_failures.py: All checks passed
uv run mypy packages/: Success: no issues found in 53 source files
```

Per-class counts (39 total):

| Class | Tests |
|---|---|
| TestBuildTargetList | 10 |
| TestLoadAlreadyRecovered | 7 |
| TestRetryBudgetBothFail | 4 |
| TestFirstAttemptSuccess | 2 |
| TestSecondAttemptSuccess | 2 |
| TestDryRun | 3 |
| TestTargetCountAssertion | 2 |
| TestOriginalFailureTimestamp (new) | 3 |
| TestExitCode2 (new) | 3 |
| TestMainLoopCounters (new) | 3 |

---

## Gap-coverage commit

`65d6609` — `test(scripts): add gap-coverage tests for phase4a recovery R1`

References original R1 commits `50b70b6` + `11085f8` and the Reviewer verdict. Conventional Commits format. Subject 62 characters. One file modified (tests only, no production code).

---

## Coverage gaps remaining

None that are material. All plan-specified test requirements are met. The three additions close the three substantive gaps. Logging format is intentionally excluded (documented above).

---

## Final disposition

The 30 original tests from commits `50b70b6` + `11085f8` are correct and cover the spec requirements. Nine gap-coverage tests were added via commit `65d6609`. The full suite passes (1106 tests, 0 failures). Ruff and mypy clean. No real API calls. No `data/raw/` reads.

**Coder may proceed to Task R2 (live execution) after Mark's cost sign-off per plan §5.**

*End of verdict. LSB Tester agent (Sonnet 4.6), 2026-05-05.*
