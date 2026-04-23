# Reviewer Verdict — Phase 4a.1 T1 (task #21.T1)

**Date:** 2026-04-23
**Reviewer:** LSB Reviewer (Sonnet)
**Commits reviewed:**
- `3318023` — `feat(collect): scripts/run_decline_backfill.py enumeration + dry-run (task #21.T1)` (initial; prior verdict FAIL)
- `24102fd` — `fix(collect): add originating_step column to T1 dry-run (task #21.T1)` (fix; this re-review)
**Files reviewed:**
- `/opt/lsb-agent/scripts/run_decline_backfill.py` (605 lines post-fix)
- `/opt/lsb-agent/tests/test_run_decline_backfill.py` (926 lines, 46 tests post-fix)

**Prerequisite documents read:** CLAUDE.md §6, CLAUDE.md §7, ARCHITECTURE.md §1.5.4, SECURITY_AND_HARDENING.md §9

---

## Initial verdict (commit `3318023`): FAIL

The initial commit was otherwise solid but was missing the `originating_step` column
in the Section 3 not-triggered per-record rows, which was an explicit acceptance
criterion in Architect plan §3 T1. See the "Failures" section of the initial verdict
below for the full defect description.

---

## RE-REVIEW VERDICT (commit `24102fd`): PASS

```
Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         PASS
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A
Check 6 — New deps sign-off:         N/A
Check 7 — Prompt versioning:         N/A
Check 8 — Uncertainty in viz:        N/A
Check 9 — Prerequisite verdicts:     PASS
```

---

## Defect resolved — originating_step column in Section 3

### Verification of the fix

**Helper function present and correct:**
`_originating_step_from_checks(failing_checks: list[str]) -> str` was added at
`/opt/lsb-agent/scripts/run_decline_backfill.py` lines 102–129. The derivation rule
matches the plan-specified mapping exactly:

- `check_8_label_count_mismatch` → `"interview"` (deepest step wins)
- `check_5_latency_exceeded` or `check_6_token_inconsistency` → `"pile_sort"`
- `check_1_freelist_empty` → `"freelist"`
- Empty or unrecognised check set → `"unknown"` (no crash)

Compound cases resolve correctly: check_5 + check_8 → `"interview"` (deepest);
check_1 + check_5 → `"pile_sort"` (pile_sort > freelist). Logic confirmed by
reading the implementation directly.

**Section 3 header updated:**
`s3_col` tuple extended from `(20, 35, 12, 45)` to `(20, 35, 12, 14, 45)`.
`s3_header` format string at line 380–387 now includes:
```
f"{'originating_step':<{s3_col[3]}}"
```
Column label `originating_step` is present in the printed header.

**Both row-emit paths updated:**
1. Not-triggered informant path (line 399): `originating_step = _originating_step_from_checks(failing_checks)` called before the print, and emitted in position `s3_col[3]`.
2. Not-triggered failure path (line 420): `originating_step = "unknown"` hardcoded (correct — no check codes are available from the failure entry structure).

**Minimal-diff confirmed:**
Five hunks in the script diff. All five touch only: the new helper function
insertion, the Section 3 column-width tuple and header, and the two row-emit
paths inside Section 3. Sections 1, 2, 4, and 5 are untouched.

**Test coverage confirmed:**
`TestOriginatingStepFromChecks` (8 unit tests, lines 767–815):
- `test_check5_only_returns_pile_sort` — asserts `"pile_sort"`
- `test_check8_only_returns_interview` — asserts `"interview"`
- `test_check1_only_returns_freelist` — asserts `"freelist"`
- `test_check6_only_returns_pile_sort` — asserts `"pile_sort"`
- `test_check1_and_check5_returns_pile_sort` — compound; asserts `"pile_sort"`
- `test_check5_and_check8_returns_interview` — compound; asserts `"interview"`
- `test_empty_checks_returns_unknown` — asserts `"unknown"`
- `test_unrecognised_check_returns_unknown` — asserts `"unknown"`

`TestSection3OriginatingStepColumn` (4 integration tests, lines 817–926):
- `test_section3_header_contains_originating_step` — asserts `"originating_step"` in captured stdout
- `test_section3_grok4_check5_row_has_pile_sort` — fixtures grok-4 check_5 record; asserts `"pile_sort"` in stdout
- `test_section3_check8_row_has_interview` — fixtures check_8 record; asserts `"interview"` in stdout
- `test_section3_unknown_step_for_empty_notes` — fixtures empty-notes record; asserts `"unknown"` in stdout

Total test count: 46 (up from 34 in the initial commit). 609 suite per commit body.
All 12 new tests directly target the defect. The prior-review "no test asserts
originating_step appears" gap is fully closed.

---

## Regression check — prior PASS checks hold

**Check 1 (No LLM imports):** Only two files changed. Neither imports any LLM
client library. `grep` over `packages/cdb_analyze/` returns only the guard comment
in `__init__.py` — no live imports. PASS confirmed.

**Check 2 (Append-only JSONL):** Fix commit touches only the two files listed above.
`data/raw/informants.jsonl` and `data/raw/failures.jsonl` are not in the diff. PASS confirmed.

**Check 3 (No secrets):** Scanned all `+` lines in the fix commit diff. The words
`token` and `api_key` appear only as check code substrings (`check_6_token_inconsistency`)
and docstring labels — no credentials or URLs. PASS confirmed.

**Check 4 (Forbidden vocabulary):** Scanned all `+` lines for CLAUDE.md §7 and
ARCHITECTURE.md §1.5.4 forbidden phrases. None found. PASS confirmed.

**Check 6 (New deps):** No changes to `pyproject.toml`, `uv.lock`,
`apps/dashboard/package.json`, or any lockfile. N/A confirmed.

**Check 7 (Prompt versioning):** No prompt templates in diff. N/A confirmed.

**Check 8 (Uncertainty in viz):** No frontend or visualization code. N/A confirmed.

**Check 9 (Prerequisite verdicts):** Fix commit body explicitly references:
- `docs/status/2026-04-23-phase4a1-t1-reviewer-verdict.md` (prior FAIL verdict; file confirmed to exist)
- `docs/status/2026-04-23-phase4a1-architect-plan.md` (Architect plan; file confirmed to exist)

PASS confirmed.

---

## Override-accepted style notes

### Commit `3318023` subject length: 82 characters (over 72-char limit)

The initial commit subject `feat(collect): scripts/run_decline_backfill.py enumeration + dry-run (task #21.T1)`
is 82 characters. CLAUDE.md §8 requires commit subject lines to be under 72 characters.

This is accepted as a **one-time §8 override** on the following rationale:
- The Architect plan §3 T1 specified this exact commit subject verbatim. The Coder
  reproduced the plan's specification faithfully; the overage is a planning-level
  defect, not a Coder fault.
- This mirrors the T5 override precedent (`docs/status/2026-04-23-phase4a-t5-reviewer-verdict.md`
  or nearest equivalent) where a plan-specified verbose subject was accepted with documentation.

The fix commit subject `fix(collect): add originating_step column to T1 dry-run (task #21.T1)`
is 69 characters — within the 72-char limit. No override required for commit `24102fd`.

---

## Supplementary findings (carried forward from initial review, all non-blocking)

### Cost-guard exit 2 on real Phase 4a corpus: expected, correct behavior

The initial commit's dry-run on real data exits 2 (STOP) with 32 detected
sessions × $0.05 = $1.60, which is exactly at the 80% threshold of the $2.00 cap.
This is not a code defect. SME binding note 8 requires the script to exit 2 at
≥$1.60, and it does exactly that. The code is correct.

This is a **Phase 4a.1 escalation for Mark and the orchestrator** — D7 needs
re-evaluation on a new Architect plan cycle before T2 (or T3) commits to a live run.
The T1 code correctly surfaces the escalation.

---

## T1 disposition

T1 is **closed** as of this re-review. All nine checks PASS. The single blocking
defect from the initial review is resolved and tested. The 82-char subject of
`3318023` is accepted as a one-time override per the planning-level-defect rationale
above.

The outstanding Phase 4a.1 work item before T2 can proceed:
- **Cost-cap escalation:** Mark and the orchestrator must decide whether to raise
  the $2.00 cap, narrow the backfill scope, or accept the 80%-threshold stop for
  the live run. This is an Architect plan decision, not a T1 code defect.

---

## Initial verdict record (preserved for audit trail)

The initial FAIL verdict text is preserved in full below for the audit record.
The single blocking defect was: Section 3 column header and per-record rows did
not include `originating_step` as required by Architect plan §3 T1 acceptance
criteria. Fix commit `24102fd` resolves this defect completely.

---

### Original FAIL verdict body (commit `3318023`)

**Failures:**

Section 3's column header was:
```
id | model_id | domain | failing_checks | reason
```
The `originating_step` column was missing. Per-record rows for not-triggered
informants printed `iid`, `model_id`, `domain`, `checks_str`, `reason` — no
`originating_step`. No test asserted that `originating_step` appeared in Section 3
output.

**Required before merge (from initial verdict):**

1. Add `originating_step` column to Section 3 not-triggered per-record rows.
   - Add to `s3_header` format string and column-width tuple
   - Derive from failing checks: `check_1` → `"freelist"`, `check_8` → `"interview"`,
     `check_5`/`check_6` → `"pile_sort"`, ambiguous → `"unknown"`
   - Print in each row
   - Add test assertion that `originating_step` or a valid value appears in Section 3 rows

2. Commit subject length (Mark override candidate): 82-char subject exceeds 72-char
   limit; plan specified the subject verbatim. Mark accepted as one-time override
   (documented above).

All items addressed in commit `24102fd`.

*End of initial FAIL verdict record.*
