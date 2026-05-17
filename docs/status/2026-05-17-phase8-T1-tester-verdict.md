---
filed: 2026-05-17
tester: LSB Tester agent (Sonnet)
task: Phase 8 T1 — License-coverage audit + repo root verification
commit: 063582a (docs(docs): Phase 8 T1 — license-coverage audit)
reviewer_verdict: PASS (docs/status/2026-05-17-phase8-T1-reviewer-verdict.md)
plan_reference: docs/status/2026-05-17-phase8-architect-kickoff.md §3 T1
verdict: PASS
---

# LSB Tester Verdict — Phase 8 T1: License-Coverage Audit + Repo Root Verification

## TESTER VERDICT: PASS

---

## Checks performed

### 1. Test floor

```
uv run pytest --tb=no -q
1791 passed, 26313 warnings in 89.62s
```

PASS. Baseline of 1791 maintained. No regressions. (T1 is documentation-only; no code change that could break tests.)

### 2. Ruff + mypy

```
uv run ruff check .          → All checks passed!
uv run mypy packages/        → Success: no issues found in 75 source files
```

PASS. Clean on both.

### 3. Four license files at repo root

```
ls -la LICENSE LICENSE-DATA LICENSE-PROMPTS LICENSE-OPENBUNDLE
-rw-r--r-- 1 lsb lsb 11112 Apr 22 11:44 LICENSE
-rw-r--r-- 1 lsb lsb  2229 Apr 22 11:44 LICENSE-DATA
-rw-r--r-- 1 lsb lsb  1908 Apr 22 11:44 LICENSE-OPENBUNDLE
-rw-r--r-- 1 lsb lsb  1821 Apr 22 11:44 LICENSE-PROMPTS
```

All four present. PASS.

### 4. LICENSE_COVERAGE.md structure

Read `/opt/lsb-agent/docs/LICENSE_COVERAGE.md` (168 lines). Verified:

- License files at repo root table: 5 rows (Apache 2.0, CC-BY-4.0, CC0-prompts, CC0-openbundle, SIL OFL 1.1). PASS.
- Coverage by path sections: Apache 2.0, CC-BY-4.0 (data + docs), CC0 prompts, CC0 open bundle, SIL OFL 1.1 — all present and enumerated. PASS.
- NOTICE determination section (`## NOTICE file determination`): present; explicit determination "No NOTICE file is required at repo root" with justification. PASS.
- Notes for Architect review: 6 notes (Note 1 through Note 6) covering `cdb_social` prompts, `scripts/`, Romney et al. attribution, gitignored JSONL files, gitignored dashboard data, and `docs/` CC-BY-4.0 mapping. PASS.

### 5. README.md pointer to LICENSE_COVERAGE.md

```
grep "LICENSE_COVERAGE" README.md
```

Found on line 41: prose sentence + markdown link `[docs/LICENSE_COVERAGE.md](docs/LICENSE_COVERAGE.md)`. PASS.

### 6. Font license

```
ls -la apps/dashboard/public/fonts/LICENSE.txt
-rw-rw-r-- 1 lsb lsb 1195 May 10 11:25 apps/dashboard/public/fonts/LICENSE.txt
```

Present (1,195 bytes, SIL OFL 1.1 with Lato + JetBrains Mono attribution). PASS.

### 7. Forbidden-vocabulary grep

```
grep -iE 'worldview|believes|thinks of|cultural bias|state of cultural alignment|pairwise gap' \
  docs/LICENSE_COVERAGE.md README.md
```

`docs/LICENSE_COVERAGE.md`: zero hits. PASS.

`README.md`: two hits, both in the pre-existing negation disclaimer "LSB does not measure cultural worldview, belief, or cognition." These sentences are the §1.5-required framing disclaimer; they are pre-existing text, not introduced by T1, and the Reviewer confirmed them clean. The T1 commit (commit `063582a`) touched only one character of README.md (appended the `LICENSE_COVERAGE.md` pointer to the existing license section). The negation-context "worldview" uses are not violations. PASS.

### 8. Scope sanity

```
git diff --stat 063582a~1..063582a
 README.md                |   2 +-
 docs/LICENSE_COVERAGE.md | 168 +++++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 169 insertions(+), 1 deletion(-
```

Exactly 2 files as specified in the task. No code, no schema, no additional docs. PASS.

---

## Summary

| Check | Result |
|---|---|
| pytest 1791 floor | PASS |
| ruff clean | PASS |
| mypy clean (75 files) | PASS |
| 4 license files at repo root | PASS |
| LICENSE_COVERAGE.md structure (5-row table, path coverage, NOTICE section, 6 notes) | PASS |
| README.md pointer | PASS |
| Font LICENSE.txt present | PASS |
| Forbidden-vocab grep on new file | PASS (zero hits in LICENSE_COVERAGE.md) |
| Scope: exactly 2 files | PASS |

All nine checks pass. T1 is documentation-only; the test floor is maintained; the new file is structurally complete and vocabulary-clean; scope is tight.

---

*End of Phase 8 T1 Tester verdict.*
