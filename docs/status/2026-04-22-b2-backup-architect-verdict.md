# B2 Backup Layer — Architect Verdict

**Date:** 2026-04-22
**Architect agent:** spawned from Claude Code session on Linode VPS
**Preceding context:** `docs/status/2026-04-22-vps-handoff.md` §4; `docs/INCIDENTS/2026-04-19-test-data-loss.md` §5.1
**Gating task for:** Phase 4a kickoff

---

## 1. Tool choice — **b2sdk** (PASS)

LSB is a Python-first stack with strict "no real API calls in tests" per `CLAUDE.md` §6 rule 10. `b2sdk` is the official Backblaze Python library, exposes a documented `InMemoryAccountInfo` + `B2Api` pair that mirrors the fixture-based testing pattern `cdb_collect` adapters already use, and avoids shell-string handling / subprocess error semantics. `boto3` adds an S3-compatibility indirection layer we don't need (we are not portability-chasing; if we ever add R2, we can refactor then — YAGNI). The `b2` CLI would force us into subprocess-wrapping and shell-quoted paths for the sake of saving one `pyproject.toml` line. `b2sdk` is the least-indirection option that stays testable. **Architect sign-off granted** per `CLAUDE.md` §11 for adding `b2sdk` to `pyproject.toml` dependencies.

## 2. Code location — **`scripts/backup.py`** (CLI-only, outside the package tree)

The backup layer is a host-level operational concern, not a library consumed by other packages. It has no callers inside `cdb_core`, `cdb_collect`, `cdb_analyze`, `cdb_publish`, or `cdb_social`. Creating `packages/cdb_backup/` would imply a reusable library surface that doesn't exist and adds a workspace member, `__init__.py`, type stubs, and import-boundary rules for a script that runs once per day from systemd. Nesting under `cdb_collect` would violate layer boundaries (collection code must not own host-operational concerns). `scripts/backup.py` sits alongside `scripts/qa_check.py` — same operational tier, same invocation pattern (systemd timer or CLI), same testing convention. If a second cloud destination ever emerges, *then* promote to `packages/cdb_backup/`.

## 3. `check_9_backup_freshness` placement — **`scripts/qa_check.py` now**

The `run_qa_checks → cdb_collect.qa` refactor is explicitly deferred per handoff §5. Adding `check_9` to `scripts/qa_check.py` today puts it where checks 1–8 already live, follows the existing `QAFailure` pattern, and when the refactor lands later it migrates as a unit with the rest. Doing it the other way — creating `cdb_collect/qa.py` now for one check — would fork the battery and force two migration touchpoints. One commit per task per `CLAUDE.md` §8: adding `check_9` next to `check_8` is the minimum coherent change.

---

## 4. Refined task descriptions

### Task #2 — Coder: implement B2 backup script + tests

Implement `scripts/backup.py` using `b2sdk` v2.x. Read `B2_KEY_ID`/`B2_APPLICATION_KEY`/`B2_BUCKET_NAME` via `python-dotenv` from `/opt/lsb-agent/.env`. Incremental sync of `data/raw/`, `data/processed/`, `data/results/`, and `data/shakedown/` (include the last only if directory exists and is non-empty — gated by existence, not a flag). Destination key prefix: `YYYY-MM-DD/<relative-path>`. Structured log to `logs/backup.log` (ISO8601 UTC timestamps, per-file status line, end-of-run summary with file count, bytes uploaded, exit code). Non-zero exit on any upload failure. Unit tests under `tests/scripts/test_backup.py` using `b2sdk.v2.InMemoryAccountInfo` or fixture-based mocks — no real B2 calls. Add `b2sdk` to `pyproject.toml`. Acceptance: tests green, `uv run python scripts/backup.py --dry-run` prints planned uploads without hitting B2.

### Task #3 — Coder: systemd unit + timer

Create `deploy/systemd/lsb-backup.service` and `deploy/systemd/lsb-backup.timer` in-repo (tracked under a new `deploy/systemd/` directory, not `/etc/systemd/system/` directly — the install step symlinks or copies to `/etc/`).

- **Service:** `Type=oneshot`, `User=lsb`, `WorkingDirectory=/opt/lsb-agent`, `ExecStart=/opt/lsb-agent/.venv/bin/python scripts/backup.py`, `StandardOutput=append:/opt/lsb-agent/logs/backup.log`, `StandardError=append:/opt/lsb-agent/logs/backup.log`.
- **Timer:** `OnCalendar=*-*-* 02:00:00 UTC`, `Persistent=true`.

Document install commands in the unit-file header comments. Acceptance: files present, `systemd-analyze verify` passes on the VPS.

### Task #4 — Coder: `check_9_backup_freshness`

Add `check_9_backup_freshness` to `scripts/qa_check.py` (adjacent to checks 1–8). Read mtime of `logs/backup.log`; return `QAFailure` if age ≥ 48h or file missing. Threshold constant `MAX_BACKUP_AGE_HOURS = 48` at top of file matching the style of the existing thresholds. Register in the battery dispatcher. Unit test with `freezegun` or a tmp-path fixture. Acceptance: fresh log → PASS; 49h-old log → QAFailure posted to `#lsb-alerts` via existing webhook path.

### Task #5 — Coder (on VPS): test-restore verification

Create a canary file in `data/raw/` (e.g., `data/raw/.canary-YYYY-MM-DD.txt` with a known UUID payload), run `scripts/backup.py`, confirm upload in B2 web UI or via `b2sdk` list call, delete the local canary, restore from B2 via a companion `scripts/restore.py` (or an ad-hoc `b2sdk` snippet documented in the verdict file), `diff` original vs restored, document in `docs/status/2026-04-22-b2-test-restore.md` with timestamps, bytes, and B2 file IDs.

If a `scripts/restore.py` is needed beyond ad-hoc, flag back to Architect before writing — that's a new task, not a scope expansion of #5.

### Task #6 — Coder: update `HOSTING_AND_DEV_OPS.md`

- §4.1 Layer 3 status Planned → Active
- §3.4 `lsb-backup.timer` Planned → Active
- §3.1 VPS identity from Hetzner `lsb-agent-01` (decommissioned) to Linode (suggested `lsb-agent-02`, IP `172.238.170.9`)
- §3.1 dev posture corrected (Surface = dev, Linode = production per handoff §2)
- Retire the 2026-04-19 superseded-pointer callouts throughout

Scope is bounded to those three sections plus callout retirement — full Hetzner-era rewrite is explicitly deferred per handoff §5.

---

## 5. Gate confirmation

- **No CDA SME gate** required for tasks #2–#6. The backup layer touches no CDA measure, no gate threshold, no ConsensusType enum, no methodology schema field, no §1.5 framing, no lede template, and no researcher grounding workflow — it is purely host-operational plumbing.
- **No UI/UX gate** — nothing visual, no `apps/dashboard/` touch, no `DESIGN_SYSTEM.md` touch.
- **No `cdb_core/schemas.py` change** required.
- **Reviewer is the sole required gate per task**, enforcing `CLAUDE.md` §6 binding rules (notably rule 9 on secrets and rule 10 on no-real-API-in-tests).

---

## 6. Stop conditions for the Coder

- **Secrets.** Before commit, confirm `.env` is in `.gitignore` and no B2 key or key-ID appears in any tracked file including log fixtures, test assertions, or unit file headers. `gitleaks` must pass locally (`CLAUDE.md` §6 rule 9).
- **Log path creation.** `logs/` must exist at `/opt/lsb-agent/logs/` on the VPS. If not present in the repo, create with `.gitkeep` in task #2 and add `logs/` to `.gitignore` (log content is not git-tracked).
- **`data/shakedown/` gating.** Do not hard-require the path; the shakedown directory exists only during shakedown windows per `SHAKEDOWN_PROTOCOL.md` §10. Handle missing/empty directories as first-class normal state (cf. `CLAUDE.md` §9 pitfall 4 on framing absence).
- **systemd unit location.** Do not write unit files to `/etc/systemd/system/` from within a commit. Tracked copies live in `deploy/systemd/` under the repo; installation to `/etc/` is a documented VPS step, not a git operation.
- **Retention rule.** Mark confirmed 90-day versioned-file retention is already set at the bucket. Do not add a retention policy in `scripts/backup.py` — that's bucket-side configuration, not script-side. If the script tries to enforce retention, stop and surface.
- **Credential rotation.** Handoff §2 notes `B2_APPLICATION_KEY` and `ANTHROPIC_API_KEY` were rotated 2026-04-22. Before task #2, verify `.env` on the VPS has post-rotation values by making one successful `b2sdk` authorize call in a throwaway REPL session; stop if auth fails.

---

## 7. Commit-reference requirement

Commits for tasks #2 through #6 must reference this verdict file path (`docs/status/2026-04-22-b2-backup-architect-verdict.md`) in their commit bodies per `CLAUDE.md` §8.

---

*End of verdict. Task #1 complete.*
