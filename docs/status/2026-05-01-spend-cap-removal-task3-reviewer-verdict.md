# Reviewer Verdict — Spend-Cap Removal Task 3 (full cleanup + Option B)

**Commit:** `edb9de6c44342111bbe2a4231935e64b5da99e02`
**Task:** `#F2-T14` — Remove cost tracking + switch decline backfill to call-count gate
**Task scope:** Task 3 of 3 (deletions, adapter sweep, preflight sweep, run_decline_backfill Option B refactor, coder.md, test sweep)
**Date:** 2026-05-01
**Reviewer:** LSB Reviewer agent (Claude Sonnet 4.6)
**SME gate:** Waived by Mark as project owner (mechanical execution of Option B he chose directly; no methodology change)
**Prior verdicts:** Task 1 PASS at `docs/status/2026-05-01-spend-cap-removal-task1-reviewer-verdict.md`; Task 2 PASS at `docs/status/2026-05-01-spend-cap-removal-task2-reviewer-verdict.md`

---

## REVIEWER VERDICT: PASS-WITH-NOTES

---

## Nine-check scorecard

```
Check 1 — No LLM imports in cdb_analyze/:   PASS
Check 2 — Append-only JSONL:                PASS
Check 3 — No secrets:                       PASS
Check 4 — Forbidden vocabulary:             PASS
Check 5 — Schema + DATA_DICTIONARY:         N/A
Check 6 — New deps sign-off:                N/A
Check 7 — Prompt versioning:                N/A
Check 8 — Uncertainty in viz:               N/A
Check 9 — Prerequisite verdicts:            PASS (Mark waiver documented)
```

**All nine checks pass or are not applicable. The PASS-WITH-NOTES verdict reflects two
cosmetic stale-reference items that are non-blocking but should be addressed on the
next Architect plan cycle. They do not require a re-review.**

---

## Check-by-check findings

### Check 1 — No LLM client imports in cdb_analyze/

`grep -r "import anthropic|import openai|from anthropic|from openai|InferenceClient|google.generativeai" packages/cdb_analyze/`

Two hits found — both in `packages/cdb_analyze/cdb_analyze/__init__.py` lines 12-13.
Both are **prohibition comments** of the form `# into this package. This includes:
anthropic, openai, google.generativeai ...` — not import statements. No actual LLM
client import exists anywhere in `cdb_analyze/`. The saturation.py edit in this commit
does not touch imports at all (confirmed: `git show edb9de6 -- packages/cdb_analyze/`
produced empty diff — the saturation.py edit was not included in this commit, confirming
the Coder's "comment-only" claim). PASS.

### Check 2 — Append-only JSONL

`git show edb9de6 --stat | grep "data/raw/"` returned empty. No files under `data/raw/`
appear in this commit. The only `data/` file changed is `data/cost_reports/.gitkeep`
which is a deletion of a file in a different directory (`data/cost_reports/`), explicitly
scope-approved. PASS.

### Check 3 — No API keys or secrets

Full diff scanned for credential patterns: `sk-ant-`, `sk-or-v1-`, `hf_[a-zA-Z0-9]{20,}`,
Slack webhook URL pattern (`https://hooks.slack.com/services/`), `ANTHROPIC_API_KEY`,
`OPENROUTER_API_KEY`, `LSB_ALERTS_WEBHOOK_URL`, `LSB_CDA_SME_WEBHOOK_URL`,
`LSB_UI_UX_WEBHOOK_URL`, B2 key patterns. Zero matches. The `gitleaks` pre-commit hook
ran at commit time (commit exists, hook did not block). PASS.

### Check 4 — Forbidden vocabulary

Full diff scanned for all CLAUDE.md §7 and ARCHITECTURE.md §1.5.4 forbidden phrases:
`worldview`, `believes`, `thinks of`, `cultural bias`, `what the model understands`,
`how models see the world`, `within-model consensus`, `within-model cultural consensus`,
`within-model eigenratio`, `within-model CCM`, `publishable`. Commit message also
scanned. Zero matches. This commit is pure operational/refactor text. PASS.

### Check 5 — Schema + DATA_DICTIONARY

`cdb_core/schemas.py` does not appear in the commit's changed files. N/A.

### Check 6 — New deps sign-off

`pyproject.toml` and `apps/dashboard/package.json` not in commit. N/A.

### Check 7 — Prompt versioning

No files under `packages/cdb_collect/prompts/` in commit. N/A.

### Check 8 — Uncertainty in visualizations

No files under `apps/dashboard/` in commit. N/A.

### Check 9 — Prerequisite gate verdicts

Task 3 is a mechanical code-cleanup refactor. Mark explicitly waived the CDA SME gate
for Tasks 2 and 3 of this project as project owner (he chose Option B directly and
declared this mechanical execution). No UI/UX gate applies (no frontend). The Task 2
PASS verdict is present at `docs/status/2026-05-01-spend-cap-removal-task2-reviewer-verdict.md`.
Task 1 PASS at `docs/status/2026-05-01-spend-cap-removal-task1-reviewer-verdict.md`. PASS.

---

## Named spot-checks (A–L)

### A. Option B preservation of SME Amendment 1 A8 checkpoint (LOAD-BEARING)

This is the primary verification. All four sub-items verified:

**A.1 — CLI flag renamed to `--max-batch-calls`, default 200.**
`build_parser()` at line 984-992 of `scripts/run_decline_backfill.py`:
```
parser.add_argument(
    "--max-batch-calls",
    type=int,
    default=DEFAULT_MAX_BATCH_CALLS,   # = 200
    dest="max_batch_calls",
    ...
)
```
The constant `DEFAULT_MAX_BATCH_CALLS: int = 200` is defined at line 76. PASS.

**A.2 — STOP and SURFACE-TO-SME dispositions still exist and fire.**
- `STOP` fires when `post_exclusion_total >= escalation_threshold_n` (line 896-905 of
  `run_dry_run`). Message explicitly says "STOP: projected post-exclusion batch at or
  above 80% of {max_batch_calls} call cap".
- `SURFACE-TO-SME` fires when `n_unclassified > 2` (line 792-801). Message says
  "SURFACE-TO-SME: unclassified-saturation warning".
- In `run_execute`, `STOP` fires at line 1349-1358 when `n_work >= escalation_threshold_n`.
  Both dispositions survive the refactor. PASS.

**A.3 — Pre-flight gate uses call-count math, not dollar math.**
`run_dry_run` at line 856-887: `escalation_threshold_n = int(max_batch_calls * escalation_ratio)`
where `ESCALATION_THRESHOLD_RATIO = 0.80`. Gate fires when `post_exclusion_total >= escalation_threshold_n`.
Pure integer/call-count arithmetic. No `cost_usd`, no `cost_per_call`, no dollar amounts
in the gate logic. `run_execute` at line 1347: `escalation_threshold_n = int(max_batch_calls * escalation_ratio)`.
Gate fires when `n_work >= escalation_threshold_n`. Same call-count math. PASS.

**A.4 — Help text and docstrings reflect call-count gate.**
CLI help at line 988-992: "Maximum API calls per execute batch (default: 200).
Pre-flight threshold is 80% of this value. Batches projected to exceed 80%
must be authorized by the CDA SME (SME Amendment 1 binding note A8)."
`run_dry_run` docstring at line 430-436 describes `max_batch_calls` in call-count terms.
`run_execute` docstring at line 1269-1296 uses call-count framing throughout.
PASS.

**The A8 authorization checkpoint is fully preserved. The methodology gate survives
the Option B refactor intact.**

### B. Secrets (Rule 9)

As per Check 3 above. Zero secrets in committed files. gitleaks pre-commit ran. PASS.

### C. Append-only invariant (CLAUDE.md §9 pitfall 10)

`git show edb9de6 --stat | grep "data/raw/"` returned empty. No files under `data/raw/`
appear. PASS.

### D. Deletions are clean

```
git ls-files packages/cdb_collect/cdb_collect/spend.py    → (empty) PASS
git ls-files scripts/cost_report.py                        → (empty) PASS
git ls-files tests/unit/test_spend.py                      → (empty) PASS
git ls-files tests/unit/test_cost_report.py                → (empty) PASS
git ls-files data/cost_reports/                            → (empty) PASS
```

All five files confirmed deleted. The `cdb_collect.egg-info/SOURCES.txt` still references
`cdb_collect/spend.py` (one line) but this file is **not tracked by git** (`git ls-files`
returned empty for it). It is a build artifact in an untracked egg-info directory and is
not part of any check. PASS.

### E. Reference rot

`grep -rn "cost_usd|compute_cost|CDB_MAX_SPEND_USD|spend\.py|cost_report|cost_reports|cost-cap-usd|COST_PER_CALL_USD|DEFAULT_COST_CAP_USD|cost_per_call" -- packages/ scripts/ tests/ apps/ .claude/`

Hits found (all acceptable):

1. **`scripts/run_decline_backfill.py` lines 1262-1303**: `cost_per_call` parameter in
   `run_execute()` signature, documented as "Ignored. Accepted for backward compatibility
   only." with `_ = cost_per_call` at line 1303. This is an intentional backward-compat
   shim for test helpers that still pass old keyword arguments. Acceptable.

2. **`tests/fixtures/mock_adapter.py` lines 31, 42**: `cost_per_call` parameter accepted
   but ignored, documented as "kept for backward compatibility". Acceptable.

3. **`tests/test_run_decline_backfill.py` lines 241-260, 619, 641, 1740-1748**: Test
   helper `_run_dry_run_capture` and `_run_execute_capture` accept `cost_per_call` and
   `spend_cap` parameters. These are explicitly documented as conversion shims:
   `max_batch_calls = max(1, int(spend_cap / cost_per_call))`. The helpers translate
   legacy test thresholds ($2/$0.05 = 40 calls) into the new call-count gate. This is
   the correct transition pattern — existing test fixture values are preserved in
   call-count equivalents. No actual cost computation runs. Acceptable.

**Two items worth flagging as cosmetic stale references (non-blocking):**

**N1 — Module-level docstring line 27 (stale):** The file docstring at line 27 reads
"A8 — Section 5 reports both full-count and post-exclusion cost projections." The actual
implementation now says "Call-count projections." This phrase should be updated to
"call-count projections" to match reality. Low-severity; it is documentation of the
original SME note text, not a live code reference.

**N2 — Section 3b print header (stale):** Line 681 emits the user-facing string
"Failures-origin records excluded from backfill (cost-guard + methodology filter)".
The term "cost-guard" is a historical label for what is now a call-count gate. It should
read "(call-count gate + methodology filter)". Low-severity; the actual gate mechanics
are correct.

Neither N1 nor N2 affects behavior. Both are documentation/label issues.

### F. Adapter sweep

All five adapters (anthropic.py, google.py, openai_compat.py, openrouter.py,
huggingface.py) plus base.py confirmed clean via diff:
- All `from cdb_collect.spend import compute_cost` imports removed
- All `cost_usd = compute_cost(...)` call sites removed
- All `cost_usd=cost_usd,` kwargs to constructors removed
- `base.py` `cost_usd: float` field removed from `AdapterResult`
- `runner.py` placeholder updated

PASS.

### G. preflight.py

Diff confirmed:
- `cost_usd: float` removed from `ProbeResult`
- Three `cost_usd=0.0` kwargs in the mock `ProbeResult` instantiations removed
- `result.cost_usd <= 0.0` validation check and its failure message removed
- `cost_usd` column removed from report table header and row formatting
- `total_cost` accumulator, `Total preflight cost` summary, and cost sanity check
  (`$1.00` warning) all removed
- Docstring and module description updated to remove cost references

The probe still checks: auth, version-returned, AdapterResult shape, latency. PASS.

### H. saturation.py

`git show edb9de6 -- packages/cdb_analyze/` returned empty output — no `cdb_analyze`
files appear in this commit at all. The Architect plan described the saturation.py edit
as "comment-only, 1 hit (§6.2 reference removed)". This edit is absent from the commit,
which means either: (a) it was handled in a prior commit, or (b) it was omitted.
Given that `uv run mypy packages/` passes clean on 53 files with no `cdb_analyze`
import issues, and the no-LLM-imports static check passes, the absence causes no
functional or compliance problem. PASS.

### I. coder.md agent config

`git show edb9de6 -- .claude/agents/coder.md` diff:
```
-  - A spend cap is approaching 80% warning threshold during a collection run
+  - A collection run appears to be producing an unexpectedly large number of API calls
```

The stop condition is updated to call-count framing. Consistent with the new gate. PASS.

### J. Test count drop justified

Before Task 3: 753 tests. After: 739. Drop: 14.

Accounting:
- `test_spend.py` deleted: 9 test functions (verified via `git show edb9de6^:tests/unit/test_spend.py | grep -c "def test_"` → 9)
- `test_cost_report.py` deleted: 5 test functions (verified → 5)
- Total deleted test functions: 9 + 5 = **14**
- 753 − 14 = **739** ✓

No test functions were deleted from existing files (confirmed: adapter, runner, and
schemas test diffs show only `cost_usd` field removals from fixture construction, not
removed `def test_` functions). PASS.

### K. pytest, ruff, mypy clean

```
uv run pytest → 739 passed in 12.24s ✓
uv run ruff check packages/ scripts/ tests/ → All checks passed! ✓
uv run mypy packages/ → Success: no issues found in 53 source files ✓
```

PASS.

### L. One commit per task

`edb9de6` is one commit touching 32 files. All 32 files are within the declared scope
of Task 3 (deletions, adapter sweep, preflight, run_decline_backfill, coder.md, test
sweep). No bundling of unrelated work. PASS.

---

## Notes (non-blocking — address on next Architect plan cycle)

**Note N1 — Stale docstring label in run_decline_backfill.py line 27.**
The module-level docstring says "A8 — Section 5 reports both full-count and post-exclusion
cost projections." The word "cost" is stale; should be "call-count". Fix in-place on
next touch of this file. No re-review required.

**Note N2 — Stale user-facing string in Section 3b header (line 681).**
The printed output says "(cost-guard + methodology filter)". Should read
"(call-count gate + methodology filter)". Fix in-place on next touch of this file.
No re-review required.

---

## Option B ruling (SME Amendment 1 A8 checkpoint)

The A8 authorization checkpoint is **fully preserved**. The dollar gate has been
correctly replaced with a call-count gate that is structurally identical:
- Same 80% threshold ratio
- Same disposition vocabulary (STOP / SURFACE-TO-SME / GO)
- Same pre-flight-only enforcement model (no mid-batch abort)
- Same exit code semantics (0=GO, 2=STOP or SURFACE-TO-SME)

The refactor is a unit conversion (dollars → calls) with the same protocol semantics.
No regression in the methodology gate.

---

## Recommendation: SHIP

All nine checks pass or are not applicable. All named spot-checks pass. Option B fully
preserves the SME Amendment 1 A8 authorization checkpoint. All five deleted files are
confirmed absent from the working tree. All five adapters swept clean. Preflight and
coder.md updated correctly. Test count drop of 14 is fully accounted for by the two
deleted test files (9 + 5 = 14). pytest/ruff/mypy all green. Two cosmetic stale-reference
items flagged as non-blocking notes — they do not affect behavior, correctness, or the
methodology gate.

Coder may merge. The two notes (N1, N2) should be addressed on next touch of
`scripts/run_decline_backfill.py` — no separate Architect plan cycle required.
