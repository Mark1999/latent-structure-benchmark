# B2 Backup Task #4 — Reviewer Verdict

**Date:** 2026-04-22
**Commit reviewed:** `45206cb feat(scripts): add check_9_backup_freshness to qa_check (task #4)`
**Reviewer agent:** spawned from Claude Code session on Linode VPS
**Architect verdict:** `docs/status/2026-04-22-b2-backup-architect-verdict.md` §4.4 (placement rationale in §3)
**Preceding gates:** No CDA SME gate required (verdict §5). No UI/UX gate required (verdict §5).

---

## Verdict: **PASS-WITH-NOTES**

Two non-blocking notes. Both are flagged forward for the deferred `run_qa_checks → cdb_collect.qa` refactor (handoff §5).

---

## Logic findings

| Item | Result |
|---|---|
| `MAX_BACKUP_AGE_HOURS = 48` constant, commented in threshold style | PASS |
| Function signature `check_9_backup_freshness(log_path=None) -> QAFailure \| None` | PASS |
| Missing log file → `QAFailure` with "missing" in `actual` | PASS |
| Log age ≥ 48h → `QAFailure` with `{age_hours:.1f}h` in message | PASS |
| Log age < 48h → `None` (PASS) | PASS |
| Boundary exactly 48h → `QAFailure` (`>=`, not `>`) | PASS |
| UTC computation via `datetime.now(UTC).timestamp()` (not deprecated `utcnow()`) | PASS |
| Log path resolution: `Path(__file__).resolve().parent.parent / "logs" / "backup.log"` | PASS |

## Stop-condition findings (Architect verdict §6)

- **No new Python dependency:** PASS — `pyproject.toml` / `uv.lock` absent from diff. Uses `tmp_path` + `os.utime` as the Architect recommended.
- **No `cdb_core/schemas.py` change:** PASS.
- **No touch to `deploy/systemd/` (task #3 scope):** PASS.
- **No touch to `HOSTING_AND_DEV_OPS.md` (task #6 scope):** PASS.

## Test findings

- 4 test functions: `test_check9_log_missing_returns_failure`, `test_check9_log_49h_old_returns_failure`, `test_check9_log_1h_old_passes`, `test_check9_log_exactly_48h_returns_failure`.
- Uses `tmp_path` + `os.utime` for deterministic mtime.
- No real API calls; `check_9_backup_freshness` is called directly.
- 49h test asserts `"49.0"` substring in `failure.actual`.

## CLAUDE.md §6 findings

- Rule 9 (no secrets): PASS — no webhook URL literal, no API key.
- Rule 10 (no real API calls): PASS — no `requests.post`.
- Rule 12 (no LLM imports in `cdb_analyze`): N/A.
- Rule 4 (forbidden vocabulary): PASS.
- Rule 7 (schema + dictionary): N/A.
- Rule 6 (new deps sign-off): PASS — none added.
- Prerequisite gates: Architect verdict §5 waives CDA SME + UI/UX.
- Commit message: `feat(scripts):` Conventional Commits; references Architect verdict; under 72 chars.

## Notes (non-blocking, flagged forward)

**Note 1 (architectural misfit).** `check_9` is wired into `run_qa_checks(record, ...)` and fires once per `InformantRecord` processed. It is an infrastructure check that does not depend on the record. In a 10,000-record QA run, this re-stats `logs/backup.log` 10,000 times and can emit up to 10,000 identical `QAFailure` objects if the log is stale.

- **Impact:** cosmetic performance issue at current data volumes; no binding rule violated.
- **Architect's stated rationale (verdict §3):** placed in `scripts/qa_check.py` now so it migrates as a unit when `run_qa_checks → cdb_collect.qa` refactor lands (handoff §5 deferred item).
- **Action:** note forwarded to the Architect for the refactor pass. When that pass lands, `check_9` should be promoted to a once-per-run infrastructure check rather than a per-record check.

**Note 2 (minor test precision).** The boundary tests use `time.time()` to compute `os.utime` timestamps while the implementation uses `datetime.now(UTC).timestamp()`. Numerically equivalent in practice, but the sub-second delta between the two calls means the 48h-exact test can theoretically land at 47.9999…h and produce a false pass in an extremely slow CI environment.

- **Impact:** never observed in practice; gap is ~microseconds.
- **Action:** future cleanup — align both sides on the same clock source (e.g., use `datetime.now(UTC).timestamp() - age_seconds` on the test side to match the implementation). Not worth a commit today.

---

*End of verdict. Task #4 complete (PASS-WITH-NOTES). Combined with task #3 PASS, task #5 (test-restore verification) is unblocked.*
