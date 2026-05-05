# Phase 4a Recovery R1 — Reviewer Verdict

**Date:** 2026-05-05
**Reviewer:** LSB Reviewer agent (Sonnet 4.6)
**Commit:** `50b70b6`
**Subject:** `feat(scripts): Phase 4a recovery script with retry + idempotence (R1)`
**Files changed:** 4 (all new — script, test file, 2 fixtures)

---

## VERDICT: FAIL

One specification deviation blocks merge: the `tests/fixtures/phase4a_failures_sample.jsonl` fixture does not contain an actual duplicate row, despite the Architect plan §2 Task R1 ("Test coverage") explicitly requiring "a synthetic `failures.jsonl` fixture covering all three in-scope models, the three out-of-scope models, and a **duplicate row** (asserts dedup)." The deduplication test (`test_deduplication`) passes vacuously — it cannot exercise the dedup code path on a fixture that has no duplicates.

The script behavior is otherwise fully correct. All nine binding checks and 46 of 47 line items pass. Only item 23 fails.

---

## Nine binding checks

```
Check 1 — No LLM imports in cdb_analyze/:         PASS
Check 2 — Append-only JSONL:                       PASS
Check 3 — No secrets:                              PASS
Check 4 — Forbidden vocabulary:                    PASS
Check 5 — Schema + DATA_DICTIONARY:                N/A
Check 6 — New deps sign-off:                       N/A
Check 7 — Prompt versioning:                       N/A
Check 8 — Uncertainty in viz:                      N/A
Check 9 — Prerequisite verdicts:                   PASS
```

---

## Line-item checklist

**Spec compliance (plan §2 Task R1):**

1. Hard-coded `IN_SCOPE_MODELS = frozenset({"google/gemini-2.5-pro", "z-ai/glm-5.1", "meta-llama/llama-4-maverick"})` at module level. **PASS** — present at `/opt/lsb-agent/scripts/recover_phase4a_failures.py` line 81.

2. `CAMPAIGN_ID = "phase4a-recovery-2026-05-05"`. **PASS** — present at line 62.

3. Target-list extractor: reads `failures.jsonl`, filters in-scope, dedupes on `(model_id, domain, run_index)`, asserts `len(targets) == 20`. **PASS** — `build_target_list()` implements all four requirements. Dry-run confirms exactly 20 cells.

4. Sort is deterministic — `(model_id, domain, run_index)` order. **PASS** — `RecoveryTarget(frozen=True, order=True)` fields are `model_id, domain, run_index, original_failure_timestamp`; `targets.sort()` sorts by that field order; `original_failure_timestamp` is a tiebreaker on duplicates (all unique post-dedup).

5. Idempotence check (SME R4): substring match `CAMPAIGN_MARKER in qa_notes` — NOT regex, NOT anchored. **PASS** — `load_already_recovered()` line 230: `if CAMPAIGN_MARKER in qa_notes:`. Docstring explicitly notes "substring match, not anchored regex, per SME R4."

6. Retry budget: 2 attempts max with 5-second inter-attempt delay. **PASS** — `for attempt in range(1, 3)` with `time.sleep(INTER_ATTEMPT_DELAY_S)` (5 s) on attempt 1 failure.

7. On both attempts failing, `append_failure` called with exception and context dict containing `model_id`, `domain`, `run_index`, `campaign_id`, `recovery_failed=true`, `original_failure_timestamp`. **PASS** — `failure_context` dict contains all six required keys.

8. SME R2 binding: verbatim final-response capture — `prompt_verbatim`, `response_verbatim`, `thinking_verbatim`, `stop_reason`, `partial_session`, `retry_attempts` passed from `PartialSessionError` to `append_failure`. **PASS** — all six kwargs passed when `last_pse is not None`; conditional `if last_pse.partial_session else None` is defensively correct (empty dict is falsy but not `None`; the conditional coerces empty collection to `None` which suppresses the field — this is acceptable per the `append_failure` spec which writes partial_session only when not None).

9. Inter-cell delay: none (sequential calls only). **PASS** — no sleep between cells; only the inter-attempt 5-s delay exists.

10. `--dry-run` flag prints target list (20 cells), validates registry hits, exits without API calls. **PASS** — confirmed by smoke test: exact 20 cells printed matching §1 disposition table; `DRY RUN complete. No API calls made.`

11. Logging format per cell: `[N/20] model=X domain=Y run=Z attempt=A/2 -> {PASS|RETRY|RECOVERY_FAILED|ALREADY_RECOVERED}`. **PASS** — format matches spec exactly; `ALREADY_RECOVERED` is emitted in the main loop (not in `recover_cell`).

12. Final summary line includes: Recovered, Recovery-failed, Already-recovered, Out-of-scope skipped, Total cells. **PASS** — all five summary fields present.

13. Reuses `MODEL_REGISTRY` and `_create_adapter` from `scripts.collect`. **PASS** — `from collect import MODEL_REGISTRY, _create_adapter`.

14. Argparse has `--dry-run` flag. **PASS** — `parser.add_argument("--dry-run", ...)`.

15. Exit code 0 on clean run, 1 on configuration errors, 2 if recovery rate < 80%. **PASS** — three exit paths confirmed: `return 0` (dry-run and successful live run), `return 1` (registry errors), `return 2` (recovery rate < 80%).

**Untouched-state verification:**

16. `scripts/collect.py` — not in diff. **PASS** — confirmed: `git diff 50b70b6^..50b70b6 -- scripts/collect.py` produces no output.

17. Adapters under `packages/cdb_collect/cdb_collect/adapters/` — not in diff. **PASS** — diff confirms only 4 files changed, all new.

18. `cdb_core/schemas.py` — not in diff. **PASS**.

19. `docs/DATA_DICTIONARY.md` — not in diff. **PASS** — correctly N/A (no schema change).

20. `data/raw/*.jsonl` files — not in diff. **PASS** — canonical data files untouched.

21. Any prompt template — not in diff. **PASS**.

**Test coverage:**

22. Target-list extractor test (in-scope + out-of-scope + dedup) — present. **PASS** — `TestBuildTargetList` with 9 test methods covering correct count, in-scope only, dedup, out-of-scope excluded, sorted, Gemini/glm/llama per-model counts, wrong-count exit, wrong-count error message.

23. Idempotence check test (already-recovered cell skipped) — present. **PASS** — `TestLoadAlreadyRecovered.test_recovered_cell_detected` and `test_untagged_record_not_detected`.

24. SME R4 substring-match test — present. **PASS** — `test_substring_match_in_concatenated_qa_notes`, `test_substring_match_does_not_use_anchored_regex` (tests leading / middle / trailing formats), `test_non_campaign_substring_not_matched`.

25. Retry budget test (adapter raises twice → 1 failures.jsonl row + 0 informants.jsonl rows). **PASS** — `TestRetryBudgetBothFail.test_failure_row_written_on_exhausted_budget` asserts exactly.

26. First-attempt success test. **PASS** — `TestFirstAttemptSuccess.test_record_written_on_first_attempt` asserts `call_count["n"] == 1` and one informants row.

27. Second-attempt success test. **PASS** — `TestSecondAttemptSuccess.test_record_written_on_second_attempt` asserts `call_count["n"] == 2` and one informants row with no failures row.

28. Dry-run mode test (no API calls, no writes, correct list printed). **PASS** — `TestDryRun` with three test methods covering no-API-calls, correct target list output, and recover_cell never called.

29. Target-count assertion test (wrong count → exit code 1). **PASS** — `TestTargetCountAssertion` with tests for fewer-than-20 and more-than-20.

30. SME R2 verbatim-capture test — verifies `response_verbatim`, `thinking_verbatim`, etc. propagated on failed rows. **PASS** (partial) — `test_failure_row_contains_verbatim_response` asserts `response_verbatim`; `test_failure_row_stop_reason_captured` asserts `stop_reason`. `thinking_verbatim` and `prompt_verbatim` are not directly asserted in output rows but are set in the fixture `PartialSessionError` and passed to `append_failure`. Acceptable given the plan's "etc." language.

31. No real API calls in tests. **PASS** — all `_run_one_informant` calls are patched via `monkeypatch.setattr`; `pytest` run completes in 0.88 s with no network activity.

32. No reading of `data/raw/*.jsonl` from tests. **PASS** — all file I/O uses `tmp_path` (pytest tmpdir) or `tests/fixtures/` paths.

**CLAUDE.md §6 binding rules:**

33. R10 — No real model calls in tests. **PASS** — same as item 31.

34. R12 — No LLM imports in `cdb_analyze`. **PASS** — `uv run python scripts/check_no_llm_imports.py` returns `OK`. The matches in `cdb_analyze/__init__.py` are in a comment, not an import statement.

35. R7 — Schema co-update N/A. **N/A** — no schema change in this commit.

36. R9 — No `.env`/secrets in diff. **PASS** — pattern scan for API key shapes, webhook URLs, and placeholder-vs-real values found nothing.

37. R11 — No new visualizations. **N/A** — no frontend changes.

**Forbidden vocabulary (CLAUDE.md §7 and ARCHITECTURE.md §1.5.4):**

38. No `worldview`, `believes`, `thinks` (applied to models), `what the model understands`, `cultural bias`, `how models see the world` in any new file. **PASS** — grep of all four new files found no matches.

39. Recovery operation framed as instrument event / cap-exhausted reasoning. **PASS** — docstring and comments use "cap-exhausted reasoning," "instrument configuration," "recovery," and "campaign." No model-attributive framing found.

**Commit format (CLAUDE.md §8):**

40. Conventional Commits format. **PASS** — `feat(scripts):`.

41. Subject ≤ 72 chars. **PASS** — 69 characters (including newline: 70 bytes per `wc -c`).

42. Body references task `Phase 4a recovery R1`. **PASS** — `Task: Phase 4a recovery R1`.

43. Body cites Architect plan path. **PASS** — `Architect plan: docs/status/2026-05-05-phase4a-recovery-architect-plan.md §2 Task R1`.

44. Body cites SME verdict path. **PASS** — `SME verdict: docs/status/2026-05-05-phase4a-recovery-cda-sme-verdict.md (PASS-WITH-NOTES)`.

45. Body explicitly mentions R2 and R4 application. **PASS** — both noted by name with specific implementation description.

46. Body cites predecessor commits `7f8f7f7` and `de3dd7e`. **PASS** — `Predecessor: Task 16 commits 7f8f7f7, de3dd7e`.

47. One commit, no bundled work. **PASS** — commit contains only the recovery script, test file, and two fixtures. No recovery report, no schema changes, no live execution artifacts.

**Validation gates:**

- `uv run pytest -q`: **1097 passed** (includes 30 new tests in this commit). 26313 warnings (pre-existing). PASS.
- `uv run ruff check scripts/recover_phase4a_failures.py tests/scripts/test_recover_phase4a_failures.py`: **All checks passed**. PASS.
- `uv run mypy packages/`: **Success: no issues found in 53 source files**. PASS.
- `uv run python scripts/check_no_llm_imports.py`: **OK: no LLM client imports found**. PASS.
- `--dry-run` smoke test: **20 cells printed, matching §1 disposition table exactly, exit 0**. PASS.

---

## Failures

**Item 23 (fixture missing required duplicate row) — FAIL**

File: `/opt/lsb-agent/tests/fixtures/phase4a_failures_sample.jsonl`

The Architect plan §2 Task R1 "Test coverage" explicitly requires:

> "Unit test on the target-list extractor with a synthetic `failures.jsonl` fixture covering all three in-scope models, the three out-of-scope models, and **a duplicate row** (asserts dedup). Use `tests/fixtures/phase4a_failures_sample.jsonl`."

The fixture has 24 lines with 24 unique `(model_id, domain, run_index)` tuples — no duplicate. The test `TestBuildTargetList.test_deduplication` passes vacuously because `len(cell_keys) == len(set(cell_keys))` when all keys are already unique.

The test comment at line 222–223 falsely claims "The fixture has glm-5.1 holidays run_index=4 duplicated (lines 15 and 16)." Lines 15 and 16 of the fixture are `z-ai/glm-5.1 holidays run_index=3` and `z-ai/glm-5.1 holidays run_index=4` respectively — different cells, not duplicates.

The dedup code path in `build_target_list()` is correct and verified to work when given a fixture that actually contains a duplicate (confirmed via `uv run python` with an injected duplicate). The failure is in fixture completeness, not in the script behavior. However, the plan specification is explicit and the test never exercises the deduplicated code path.

---

## Required before merge

1. Add a true duplicate row to `/opt/lsb-agent/tests/fixtures/phase4a_failures_sample.jsonl`. The simplest fix: append a second copy of the `z-ai/glm-5.1 holidays run_index=4` row (same `model_id`, `domain`, `run_index`, different or same timestamp — both are valid duplicate patterns). Update the test comment at line 222–223 to correctly describe which lines are the duplicate pair. Verify `test_deduplication` still passes (it will, and now exercises the code path for real).

---

## Notes (PASS-WITH-NOTES level, not blocking)

None. The single finding above is FAIL-level. All other items pass.

---

*End of Reviewer verdict. Only Mark can override this FAIL. Coder must fix item 23 and re-submit for re-review.*

---

## Re-review of commit 11085f8

**RE-REVIEW VERDICT: PASS — original FAIL on item 23 resolved by 11085f8**

**Date:** 2026-05-05
**Reviewer:** LSB Reviewer agent (Sonnet 4.6)
**Commit:** `11085f8`
**Subject:** `fix(tests): add real duplicate row to phase4a recovery fixture`

---

### Item 23 — now PASS

The fixture at `/opt/lsb-agent/tests/fixtures/phase4a_failures_sample.jsonl` now has 25 lines. Line 16 and line 25 are both `z-ai/glm-5.1 holidays run_index=4`; they differ only in timestamp (`2026-04-22T22:57:29.951184` vs. `2026-04-22T23:01:05.000000`). The `(model_id, domain, run_index)` key is identical — a genuine duplicate.

The test comment at line 175 of `/opt/lsb-agent/tests/scripts/test_recover_phase4a_failures.py` now correctly reads "lines 16 and 25" (previously and incorrectly stated "lines 15 and 16").

`test_deduplication` now exercises the dedup code path for real. The fixture gives `build_target_list()` 25 rows, of which 21 are in-scope (4 out-of-scope rows excluded), of which 20 are unique cells after dedup. The assertion `len(cell_keys) == len(set(cell_keys))` now fails if the dedup logic is disabled — confirmed by Coder and corroborated by the test logic (21 in-scope rows with one duplicate pair would yield 21 keys but only 20 unique keys, so the assertion `len(cell_keys) == len(set(cell_keys))` would correctly detect the residual duplicate).

---

### Scope of fix — no new issues introduced

Commit `11085f8` touches exactly two files:

- `tests/fixtures/phase4a_failures_sample.jsonl` — one line appended (line 25). No existing line modified. Append-only property preserved (Check 2 continues to hold).
- `tests/scripts/test_recover_phase4a_failures.py` — one comment line updated (line 175). No logic change.

No production code modified. No new dependencies. No schema changes. No forbidden vocabulary introduced. No secrets introduced. All nine binding checks continue to hold unchanged from the original R1 verdict.

---

### Validation gates

- `uv run pytest tests/scripts/test_recover_phase4a_failures.py -v`: **30 passed** in 0.75 s. All 30 pass including `test_deduplication`.
- `uv run pytest -q`: **1097 passed**, 26313 warnings (pre-existing). No regressions.
- `uv run ruff check .`: **All checks passed**.

---

### Commit message verification

- Format: `fix(tests):` — Conventional Commits compliant.
- Subject length: 62 characters — under 72-character limit.
- Body references original commit `50b70b6`: present.
- Body references Reviewer verdict file `docs/status/2026-05-05-phase4a-recovery-r1-reviewer-verdict.md`: present.

---

### Final disposition

Item 23 is now PASS. No new issues were introduced. The fix is minimal and targeted exactly as instructed.

**Coder may proceed to the Tester gate.**

*End of re-review. LSB Reviewer agent (Sonnet 4.6), 2026-05-05.*
