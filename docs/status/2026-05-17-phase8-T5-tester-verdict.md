# Phase 8 T5 — Pre-Release Scan Implementation — Tester Verdict

**Task:** Phase 8 T5 — `scripts/prerelease_scan.py` (8 checks gating M12)
**Commits under test:** `4ebb66b` (initial implementation) + `ea8130d` (allow-list fix)
**Verdict:** PASS
**Date:** 2026-05-17

---

## Verification steps and results

### 1. Test floor maintained

```
uv run pytest tests/ -q --tb=no
```

Result: **1791 passed, 26313 warnings** — floor unchanged.

### 2. Ruff + mypy clean

```
uv run ruff check .        → All checks passed!
uv run mypy packages/      → Success: no issues found in 75 source files
```

Both tools clean.

### 3. Independent scan run — exit 0, all 8 PASS

```
uv run python scripts/prerelease_scan.py --report /tmp/scan-tester-verification.md
echo "Exit: $?"
```

Output:
```
LSB pre-release scan — 2026-05-17 21:25:00 UTC
HEAD: ea8130d6bba2b70a424f97ffa551f2ab3c5f02bd
Working tree: clean

Running check 1 — gitleaks ... PASS (0 hit(s))
Running check 2 — forbidden vocab ... PASS (0 hit(s))
Running check 3 — internal paths ... PASS (0 hit(s))
Running check 4 — email addresses ... PASS (0 hit(s))
Running check 5 — API key patterns ... PASS (0 hit(s))
Running check 6 — public URL validity ... PASS (0 hit(s))
Running check 7 — .env/credential files ... PASS (0 hit(s))
Running check 8 — license coverage ... PASS (0 hit(s))

Overall: PASS
Exit: 0
```

Confirmed: exit 0, "Overall: PASS", all 8 checks PASS.

### 4. Committed report structure verified

`docs/status/2026-05-17-phase8-prerelease-scan.md` contains:

- Header with run metadata (run-at, runner, repo state, working tree)
- Per-check sections (### Check 1 through ### Check 8)
- Summary table with 8 rows (Check | Result | Hits)
- T11 gate-status footer: "**GATE: PASS**"

Structure matches spec.

### 5. Deleted script confirmed absent

```
ls scripts/ | grep run_phase4a_t4
```

`scripts/run_phase4a_t4.sh` is not present. Confirmed absent.

### 6. Reproducibility — second run diff

```
uv run python scripts/prerelease_scan.py --report /tmp/scan-tester-verification-2.md
diff /tmp/scan-tester-verification.md /tmp/scan-tester-verification-2.md \
  | grep -v "Run at:" | grep -v "Working tree:"
```

Diff output:
```
3c3
---
```

Line 3 is the "Run at:" timestamp line. The diff matches only that line — which the grep filter collapses to the bare `---` separator artifact. Substantive content is identical across both runs. Reproducibility confirmed.

### 7. JSON output mode

```
uv run python scripts/prerelease_scan.py --json /tmp/scan-tester.json
uv run python -c "import json; data = json.load(open('/tmp/scan-tester.json')); ..."
```

Output:
```
JSON valid. Keys: ['run_at', 'head', 'working_tree', 'overall', 'checks']
Checks count: 8
Overall: PASS
```

JSON parses cleanly; correct structure.

### 8. `--report -` stdout mode

```
uv run python scripts/prerelease_scan.py --report - | head -10
```

First 10 lines include the run timestamp, HEAD, working-tree status, and per-check progress lines. Report header confirmed.

---

## Coverage gaps

None. This is operator tooling (a standalone scan script). The task spec calls for light verification via direct re-running, not a new pytest suite. All 8 specification points verified by direct execution.

---

## Summary

| Step | Result |
|---|---|
| pytest floor (1791) | PASS |
| ruff clean | PASS |
| mypy clean | PASS |
| scan runs exit 0, all 8 checks PASS | PASS |
| committed report structure matches spec | PASS |
| `run_phase4a_t4.sh` absent | PASS |
| reproducibility (diff timestamp-only) | PASS |
| JSON mode parses cleanly | PASS |
| `--report -` stdout mode works | PASS |

**TESTER VERDICT: PASS**

No failures, no coverage gaps, no regressions.
