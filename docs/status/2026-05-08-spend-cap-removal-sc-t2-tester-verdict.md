# Tester Verdict — SC-T2: Strip cap framing from secondary scripts and .env

**Commit tested:** `3bfc507`
**Tester:** LSB Tester agent (Sonnet 4.6)
**Date:** 2026-05-08
**Task ID:** SC-T2
**Plan reference:** `docs/status/2026-05-08-spend-cap-removal-architect-plan.md` §4 (SC-T2 row)
**Reviewer verdict:** `docs/status/2026-05-08-spend-cap-removal-sc-t2-reviewer-verdict.md` — PASS

---

## TESTER VERDICT: PASS

---

## Checks performed

### 1. Full suite

```
uv run pytest tests/ -q
1204 passed, 26313 warnings in 12.60s
```

Matches the 1,204 baseline established at Reviewer time. Zero failures.

### 2. Targeted decline-backfill suite

```
uv run pytest tests/test_run_decline_backfill.py -v
131 passed in 0.86s
```

All 131 tests green. Call-count gate scenarios (`TestDryRunScenarios::test_dry_run_stop_disposition`, `test_dry_run_go_disposition`) pass.

### 3. Rerun script import + argparse

```
uv run python scripts/rerun_phi4_phase4b_t2.py --help      → prints usage, exit 0
uv run python scripts/rerun_t3_unexplained_phase4b.py --help → prints usage, exit 0
```

Both scripts import cleanly and parse args. No `CDB_MAX_SPEND_USD` reference in either docstring (confirmed by reading the full module source). No cost framing in either help string.

### 4. `.env.example` cost-reference check

```
grep -iE "spend|cost|cap" .env.example
(no output)
```

Clean. Lines 21–22 (`CDB_MAX_SPEND_USD` block) are absent.

### 5. `CDB_MAX_SPEND_USD` sweep

```
grep -rn "CDB_MAX_SPEND_USD" scripts/ tests/ .env.example
(no output)
```

Zero hits. Consistent with Reviewer check F.

### 6. Helper rename call-site audit

`_run_dry_run_capture` in `TestDryRunScenarios` (L235): parameter is `legacy_dollar_threshold: float = 2.00`. Confirmed by reading source.

All call sites inspected:

- `TestDryRunScenarios` L618, L621, L640, L643: pass `legacy_dollar_threshold=2.00` — correct.
- All other `TestDryRunScenarios` call sites (L293, L321, L345, L393, L424, L476, L501, L653, L693, L764, L790) use the default — no `spend_cap=` keyword.
- `TestSection3bExcludedAudit._run_dry_run_capture_3b` (L855): dead `spend_cap` parameter removed per Reviewer scope-expansion note — confirmed absent.
- `TestSection3cUnclassified._run_dry_run_capture_3c` and `TestSourceFlag._run_source_capture`: same cleanup confirmed absent.

`grep -n "spend_cap=" tests/test_run_decline_backfill.py` returns zero hits. No call site passes `spend_cap=`.

### 7. Dead parameter forward-carry confirmation

`_run_execute_capture` at L1725 retains:
- L1735: `spend_cap: float = 10.00` (parameter declaration, documented ignored)
- L1744: docstring note "spend_cap, cost_per_call, and adapter_cost are ignored (cost tracking removed in task #F2-T14)"

Zero callers pass `spend_cap=` as a keyword argument. This is the residual instance noted in the Reviewer verdict (item E forward-carry to SC-T4). It does not cause any test failure. Confirmed.

### 8. Lint and type checks

```
uv run ruff check .       → All checks passed
uv run mypy packages/     → Success, no issues found in 55 source files
```

---

## Tests written

No new tests required for this task. SC-T2 is a doc-and-cleanup commit (docstring stripping, dead-parameter cleanup, `.env.example` line deletion). The existing 1,204-test suite provides full coverage of the affected code paths.

---

## Coverage gaps

None. All acceptance criteria verified by the existing test suite and the targeted checks above.

---

## Forward-carry note (SC-T4)

`_run_execute_capture` at `/opt/lsb-agent/tests/test_run_decline_backfill.py` L1735 retains `spend_cap: float = 10.00` with zero active callers. SC-T4 will need to handle this in the CI grep allowlist (or rename it) alongside the shim parameters in `scripts/run_decline_backfill.py` L468–491. No action required for SC-T2; this is documented here so SC-T4 has a complete inventory.

---

*Tester: LSB Tester agent (Sonnet 4.6), 2026-05-08*
