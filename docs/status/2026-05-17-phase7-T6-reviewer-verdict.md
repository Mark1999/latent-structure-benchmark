---
filed: 2026-05-17
reviewer: LSB Reviewer agent (Sonnet)
task: Phase 7 T6 — Bluesky publisher + cron orchestrator CLI
commit: 2da616f (feat(social): Phase 7 T6 — Bluesky publisher + cron orchestrator CLI)
plan_reference: docs/status/2026-05-17-phase7-architect-kickoff.md §3 T6
dep_ratification: Mark's 2026-05-17 "atproto approved" message + kickoff §10
verdict: FAIL
---

# Phase 7 T6 — Reviewer Verdict

## Nine-check matrix

| Check | Result |
|---|---|
| Check 1 — No LLM imports in cdb_analyze | PASS |
| Check 2 — Append-only JSONL | PASS |
| Check 3 — No secrets / credential handling | **FAIL** |
| Check 4 — Forbidden vocabulary | PASS |
| Check 5 — Schema + DATA_DICTIONARY | N/A |
| Check 6 — New deps sign-off | PASS |
| Check 7 — Prompt versioning | N/A |
| Check 8 — Uncertainty in viz | N/A |
| Check 9 — Prerequisite verdicts | PASS |

---

## Failure detail

### Check 3 — Hardcoded credential fallback in dry-run path

**File:** `packages/cdb_social/cdb_social/publisher.py`
**Line:** 223

```python
handle = os.environ.get("BLUESKY_HANDLE", "dry-run.bsky.social")
```

The task spec is categorical: "no hardcoded fallback values. `os.environ.get(...)` reads must never have hardcoded fallback values."

The live path (`_publish_bluesky`, lines 103–107) correctly uses `""` as the env-get default, then raises `PublisherTerminalError("credentials missing")` if empty. The dry-run path deviates by substituting `"dry-run.bsky.social"` when `BLUESKY_HANDLE` is absent.

While the dry-run path makes no real API call, the hardcoded fallback masks the absence of credentials and sets an inconsistent precedent.

---

## Required correction before re-submit

Change line 223 to one of these equivalent correct forms:

**Form A** (preserves the `dry-run.bsky.social` sentinel for URL readability, but uses `""` as env-get default):
```python
handle = os.environ.get("BLUESKY_HANDLE", "") or "dry-run.bsky.social"
```

**Form B** (omits handle from the synthetic URL entirely):
```python
synthetic_url = f"https://bsky.app/profile/dry-run/post/{draft.draft_id}"
```
and remove the `handle =` line.

Either form is acceptable. Form A requires no other change. Form B requires removing the `handle` variable from the dry-run branch.

---

## Passing checks — notes

**Check 1:** `check_no_llm_imports.py` AST scan passes clean.

**Check 4:** `test_social_cli.py` line 219 uses `"worldview detected"` as a `DrafterRejectedException` argument — a test asserting the system rejects drafts containing forbidden vocab. CLAUDE.md §7 judgment exemption applies (the rule governs how LSB talks about its subjects, not whether the word can appear in test code exercising the rejection path).

**Check 6:** `atproto>=0.0.46` added only to `packages/cdb_social/pyproject.toml`. Mypy override (`module = "atproto"` `ignore_missing_imports = true`) is in root `pyproject.toml`. Mark's 2026-05-17 ratification documented in commit body.

**Check 9:** Kickoff §3 T6 explicitly waives CDA SME and UI/UX gates. Commit body references kickoff and Mark's dep ratification.

---

## T6-specific verifications — all pass except line 223

- Platform dispatch: Bluesky live; X/LinkedIn raise `PublisherNotEnabled`. Correct.
- Failure classification: transient (5xx/timeout/429) → `RETRY_PENDING`; terminal (4xx/unknown) → `FAILED`; missing creds → terminal. Correct.
- Dry-run: `atproto.Client` never instantiated when `dry_run=True`. Confirmed.
- No credential logging: confirmed by grep.
- AT URI → bsky.app URL: `https://bsky.app/profile/{handle}/post/{rkey}` format correct.
- Four subcommands wired: `run-once`, `review`, `publish`, `status`.
- `detect_drift(..., enable=False)`: literal at cli.py lines 237–239. Test `TestRunOnceDriftDisabled` verifies.
- `detect_divergence` receives `new_models_this_run`. Confirmed lines 241–254.
- All five detectors invoked in `cmd_run_once`.
- `cmd_run_once` makes no call to `publisher.publish()`.
- `DrafterRejectedException` caught per-draft (lines 329–337).
- Dedupe check before drafting (lines 271–276).
- Publish subcommand: all four error branches handled with correct queue moves.
- `--quiet` flag on all four subcommands.
- No changes to schemas, ARCHITECTURE.md, DATA_DICTIONARY.md, CLAUDE.md, prompts.
- Scope: 12 expected files; no out-of-scope changes.
- Tests: 1679 passed (baseline 1616 + 63 new); ruff clean; mypy clean (69 source files).

---

## Re-submit

After applying one of the two corrections above, re-submit. The correction is a single line; re-review will be fast.

---

*One-line summary: FAIL — publisher.py line 223 uses a hardcoded env-get fallback (`"dry-run.bsky.social"`) in the dry-run credential path, violating the binding rule that `os.environ.get()` reads must never have hardcoded fallback values; fix is one line, then resubmit.*
