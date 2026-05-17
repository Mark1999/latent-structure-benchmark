---
filed: 2026-05-17
tester: LSB Tester agent (Sonnet)
task: Phase 7 T6 — Bluesky publisher + cron orchestrator CLI
commits: 2da616f (main implementation), 4180e65 (Reviewer FAIL fix)
reviewer_pass: docs/status/2026-05-17-phase7-T6-reviewer-pass-addendum.md
verdict: PASS
---

# Phase 7 T6 — Tester Verdict

## Checkpoint matrix

| # | Checkpoint | Result |
|---|---|---|
| 1 | All tests pass (1679) | PASS |
| 2 | Ruff clean | PASS |
| 3 | Mypy clean (69 source files) | PASS |
| 4 | 63 new tests — correct count (39 publisher + 24 CLI) | PASS |
| 5 | No real Bluesky API calls in tests | PASS |
| 6 | Line 223 fix confirmed (Form A) | PASS |
| 7 | No credential logging in publisher.py or cli.py | PASS |
| 8 | Forbidden vocab grep — single hit, in rejection-path test | PASS |
| 9 | Scope sanity — main 12 files, fix 1 file, no out-of-scope changes | PASS |
| 10 | Boundary rules — no cdb_analyze imports; atproto only in publisher.py | PASS |
| 11 | Drift lockout — detect_drift called with enable=False (lines 237-239) | PASS |
| 12 | run-once no auto-publish — publish() only in cmd_publish | PASS |

---

## Test run output

```
tests/unit/test_social_publisher.py  39 passed
tests/unit/test_social_cli.py        24 passed

Full suite: 1679 passed in 73.66s
ruff: All checks passed
mypy: Success: no issues found in 69 source files
```

---

## Detailed checkpoint notes

**Checkpoint 1 — Test count:** 1679 total, matching the Reviewer PASS addendum baseline.
No regressions from the pre-T6 run.

**Checkpoint 4 — 63 new tests by class:**
- `TestAtprotoUriToUrl` (2) — URI parsing helper
- `TestPublisherPlatformDispatch` (5) — Bluesky dispatches; X + LinkedIn raise PublisherNotEnabled
- `TestPublisherCredentials` (5) — missing handle, missing password, empty handle, empty password, mock not called
- `TestPublisherDryRun` (5) — DRY_RUN status, atproto client never invoked, synthetic URL, draft_id preserved, X still raises
- `TestPublisherSuccess` (10) — PUBLISHED status, AT URI, bsky.app URL, handle in URL, draft_id preserved, published_at set, login called, send_post called, no error_message
- `TestPublisherTransientError` (6) — 503, 502, 429, timeout, network, rate_limit keyword
- `TestPublisherTerminalError` (7) — 401, 401 on login, 403, 400, unknown exception, unauthorized keyword, verbatim message
- `TestRunOnceSubcommand` (4) — draft written, summary printed, rejection logged not crashed, zero triggers
- `TestRunOnceDriftDisabled` (1) — enable=False keyword argument verified via call_args.kwargs
- `TestRunOnceDedupe` (2) — known key skipped, new key drafted
- `TestPublishSubcommand` (6) — moves to published, sidecar written, NotEnabled to failed, terminal to failed, summary, empty queue
- `TestPublishDryRun` (2) — dry_run=True passed to publisher, DRY_RUN record moves to published
- `TestPublishTransientRetained` (3) — draft stays in approved, retries.jsonl written, summary shows retry count
- `TestStatusSubcommand` (6) — empty queue, pending count, approved count, published total+this-month, record sidecars excluded, returns 0

**Checkpoint 5 — No real API calls:**
`atproto.Client` is never constructed in test code. All publisher tests inject a
`_make_mock_atproto_client()` MagicMock via the `atproto_client=` parameter.
CLI tests patch `cdb_social.cli.publish` directly (no atproto import path reached).

**Checkpoint 6 — Credential fix confirmed:**
`packages/cdb_social/cdb_social/publisher.py` line 223:
```python
handle = os.environ.get("BLUESKY_HANDLE", "") or "dry-run.bsky.social"
```
Live path (lines 103-107) reads with `""` default and raises `PublisherTerminalError("credentials missing")`
when either variable is empty. Consistent posture across dry-run and live paths.

**Checkpoint 7 — No credential logging:**
`BLUESKY_APP_PASSWORD` appears in: module docstring (env-var name reference),
`os.environ.get("BLUESKY_APP_PASSWORD", "")` (read), `client.login(handle, app_password)`
(used). Never passed to `logger.*` or `print()`. cli.py has no password references at all.

**Checkpoint 8 — Forbidden vocab:**
One hit:
```
+                raise DrafterRejectedException("worldview detected", draft_text="bad text")
```
Located at `tests/unit/test_social_cli.py` line 219 inside a test that asserts the
system *rejects* a draft containing forbidden vocabulary. CLAUDE.md §7 judgment
exemption applies: the rule governs how LSB talks about its subjects, not whether
the word can appear in test code exercising the rejection path.
No hits in any production code path.

**Checkpoint 9 — Scope:**
Main commit (2da616f): 12 files — cli.py, publisher.py, queue.py additions/modifications,
two pyproject.toml, .env.example, 2 test files, 3 fixture JSONs, uv.lock.
Fix commit (4180e65): exactly 1 file (publisher.py, 1 insertion + 1 deletion).
No changes to cdb_core/schemas.py, ARCHITECTURE.md, DATA_DICTIONARY.md, CLAUDE.md,
prompt files, or drafter files.

**Checkpoint 10 — Boundary rules:**
`grep -rE 'from cdb_analyze|import cdb_analyze' packages/cdb_social/` → empty.
`atproto` imported only at `packages/cdb_social/cdb_social/publisher.py` line 113
(inside the live-path branch, deferred import). Not in cli.py, queue.py, or any drafter.

**Checkpoint 11 — Drift lockout:**
```python
drift_triggers: list[SocialTrigger] = detect_drift(
    domain_results, state_dir, enable=False
)
```
`TestRunOnceDriftDisabled.test_detect_drift_called_with_enable_false` patches
`detect_drift`, calls `main(["run-once"])`, and asserts `call_args.kwargs.get("enable") is False`.

**Checkpoint 12 — run-once no auto-publish:**
`publish(...)` appears only inside `cmd_publish` (line 476). The `cmd_run_once` function
(lines 201-370) contains no reference to `publisher.publish`. The design invariant in
the cli.py module docstring explicitly states: "run-once does NOT auto-publish."

---

## Coverage gaps

None identified. All acceptance criteria from kickoff §3 T6 are covered by the 63 tests.
The test classes map directly to the spec's acceptance sketch:
- Platform dispatch ✓
- Credentials missing ✓
- Dry-run path ✓
- Success ✓
- Transient errors ✓
- Terminal errors ✓
- Each CLI subcommand (run-once, review delegate, publish, status) ✓
- Drift lockout (enable=False) ✓
- Dedupe before drafting ✓

---

*End of Phase 7 T6 Tester verdict. T7 (cron + docs) unblocked.*
