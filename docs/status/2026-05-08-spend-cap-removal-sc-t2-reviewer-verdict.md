# Reviewer Verdict — SC-T2: Strip cap framing from secondary scripts and .env

**Commit reviewed:** `3bfc507`
**Reviewer:** LSB Reviewer agent (Sonnet 4.6)
**Date:** 2026-05-08
**Task ID:** SC-T2
**Plan reference:** `docs/status/2026-05-08-spend-cap-removal-architect-plan.md` §4 (task 2), §6 (SC-T2 Reviewer items)
**Prerequisite:** SC-T1 Reviewer PASS at `docs/status/2026-05-08-spend-cap-removal-sc-t1-reviewer-verdict.md`

---

## REVIEWER VERDICT: PASS

---

## Standard nine-check scorecard

```
Check 1 — No LLM imports in cdb_analyze:   N/A (commit does not touch cdb_analyze)
Check 2 — Append-only informants.jsonl:     N/A (no raw data touched)
Check 3 — No secrets:                       PASS
Check 4 — Forbidden vocabulary:             PASS
Check 5 — Schema + DATA_DICTIONARY:         N/A (no schema changes)
Check 6 — New deps sign-off:                PASS (pyproject.toml and uv.lock unchanged)
Check 7 — Prompt versioning:                N/A (no prompt templates touched)
Check 8 — Uncertainty in viz:               N/A (no frontend changes)
Check 9 — Prerequisite verdicts:            PASS
```

---

## SC-T2-specific Reviewer items

**A. Rerun scripts' docstrings no longer reference CDB_MAX_SPEND_USD:** PASS

- `scripts/rerun_phi4_phase4b_t2.py`: four lines removed from docstring (hard-stop guard block). No functional changes. Confirmed by diff.
- `scripts/rerun_t3_unexplained_phase4b.py`: two lines removed from docstring (hard-stop guard mention + CDB_MAX_SPEND_USD=5 invocation example in Usage block). No functional changes. Confirmed by diff.

**B. run_decline_backfill.py Notes N1 and N2 already correct:** PASS

- N1 (module docstring L27): reads "Section 5 reports both full-count and post-exclusion call-count projections" — correct per plan requirement ("call-count" not "cost"). Confirmed by `git show acc66b9:scripts/run_decline_backfill.py` — already correct before this commit. Coder's report is accurate.
- N2 (Section 3b print header at L730): reads `"(call-count gate + methodology filter)"` — correct. Already present at `acc66b9`. Coder's report is accurate.

**C. run_decline_backfill.py backward-compat shim parameters unchanged:** PASS

- `git diff acc66b9..3bfc507 -- scripts/run_decline_backfill.py` returns empty (zero lines). The script is byte-identical across the two commits. Shim parameters at L468–491 (`spend_cap: float | None = None`) and L1328–1370 preserved verbatim per plan §2 and §10.

**D. .env.example no longer contains CDB_MAX_SPEND_USD or any cost reference:** PASS

- Diff confirms deletion of L21–22 (`# Spend cap (ARCHITECTURE.md §6.2)` and `CDB_MAX_SPEND_USD=300`). `grep -iE "spend|cost|cap" .env.example` returns no matches. Remaining entries are API keys (placeholder values), Slack webhook URLs (placeholder `...` values), and Backblaze credentials — all correct.

**E. Test helper parameter renamed; call sites updated:** PASS (option (a) chosen)

- `_run_dry_run_capture` in `TestDryRunScenarios`: parameter renamed `spend_cap` → `legacy_dollar_threshold`, docstring updated, internal variable reference updated. Confirmed by diff.
- Six call sites cleaned: L618/640 in `TestDryRunScenarios` (renamed parameter), L1191/1204 area in `TestSection3bExcludedAudit` (parameter + call-through deleted), L1307/1318 area in `TestSection3cUnclassified` (parameter + call-through deleted), L1543/1554 area in `TestSourceFlag` (parameter + call-through deleted).
- Note: module-level `_run_execute_capture` at L1725 retains `spend_cap: float = 10.00` parameter. This parameter has zero callers that pass `spend_cap=` (confirmed by grep). It is documented as ignored (L1744: "spend_cap, cost_per_call, and adapter_cost are ignored"). This residual instance is consistent with the preserved shim parameters in `run_decline_backfill.py` — SC-T4 will need to handle both in the CI grep allowlist regardless. SC-T2's acceptance criterion E is met (plan's six named call sites + helper rename all addressed).

**F. git grep -nE 'CDB_MAX_SPEND_USD' -- scripts/ tests/ .env.example returns zero hits:** PASS

- Confirmed: `git grep -nE 'CDB_MAX_SPEND_USD' -- scripts/ tests/ .env.example` returns no output.

**G. Decline-backfill tests pass; call-count gate scenarios intact:** PASS

- `uv run pytest tests/test_run_decline_backfill.py -v` → 131 passed.
- STOP, SURFACE-TO-SME, GO scenarios confirmed via `TestDryRunScenarios::test_dry_run_stop_disposition` and `test_dry_run_go_disposition`.
- Full suite: `uv run pytest` → 1204 passed.

---

## Additional scope expansion assessment

The Coder removed `spend_cap: float = 10.00` parameters from three class-level helper methods (`TestSection3bExcludedAudit._run_dry_run_capture_3b`, `TestSection3cUnclassified._run_dry_run_capture_3c`, `TestSourceFlag._run_source_capture`) beyond the plan's six named call sites. These helpers were thin wrappers that propagated `spend_cap` directly to the underlying main function without transformation. Per the review task framing, this is analogous to the SC-T1 `registry_map` cleanup — orphaned dead-parameter scaffolding removed. The test functions themselves are intact; only the dead parameter propagation is gone. This is a defensible scope expansion consistent with plan intent (remove framing reinforcement). Accepted.

---

## Build health

- `uv run pytest`: 1204 passed, 0 failed
- `uv run ruff check .`: All checks passed
- `uv run mypy packages/`: Success, no issues found in 55 source files

---

## Summary

All SC-T2 acceptance criteria are met. All nine standard checks pass or are N/A. All six SC-T2-specific Reviewer items pass. The Coder's report that N1/N2 were already correct is verified — `run_decline_backfill.py` is unchanged in this commit. The `.env.example` is clean. The test helper rename is consistent and complete across all named call sites. Tests pass.

**PASS. Tester may proceed.**

---

*Reviewer: LSB Reviewer agent (Sonnet 4.6), 2026-05-08*
