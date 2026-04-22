# Handoff to next Claude Code session — VPS pivot + B2 backup layer

**Date:** 2026-04-22
**Context:** Development has moved from the Windows Surface laptop to the new Linode VPS. This doc briefs the next Claude Code session on what's been done, what's still open, and what should be worked on first.

---

## 1. Read first

Before doing anything else, the new Claude Code session must read:

1. `CLAUDE.md` — team constitution. **§8 was updated 2026-04-21: direct commits to master are the default; branch+PR is the exception.**
2. `ARCHITECTURE.md` — binding design. §1.5 framing is binding on all generated text.
3. `docs/status/2026-04-21-shakedown-findings.md` — most recent project-state snapshot. F2 (shakedown-findings-batch-2) is complete; all 8 §8 sanity checks PASSED. Pipeline is ready for Phase 4a pending (a) B2 backup precondition, (b) CDA SME review.
4. `docs/SHAKEDOWN_PROTOCOL.md` — binding for any pre-Phase-4a collection. §10 retention rule still applies.
5. `HOSTING_AND_DEV_OPS.md` — **stale re: which machine is which.** The VPS references in it describe the decommissioned Hetzner box. Treat it as the *target design* for backup layers and systemd timers, but the specifics (paths, IPs, provider) need to be re-examined for this Linode.
6. `docs/INCIDENTS/2026-04-19-test-data-loss.md` — the prior pivot. §5.1 is the "backup-before-collection" precondition that still gates Phase 4a.

---

## 2. Current infrastructure state

### Pivot #2 — Surface to Linode VPS

Development has moved again. Running list of pivots:

| Date | From | To | Why |
|---|---|---|---|
| 2026-04-19 | Hetzner `lsb-agent-01` | Windows Surface Laptop Studio 1964 | Test data loss incident on Hetzner VPS; temporary dev host |
| 2026-04-22 | Windows Surface | Linode VPS (Ubuntu 24.04) | Always-on requirement for backup layer + Phase 4a canonical collection |

### The new VPS

- **Provider:** Linode (Akamai)
- **OS:** Ubuntu 24.04 LTS
- **Repo path:** `/opt/lsb-agent`
- **User:** `lsb` (created; Claude Code runs under this user per `HOSTING_AND_DEV_OPS.md` §3.1)
- **Claude Code:** installed on the VPS
- **SSH as root access:** *(used only for initial setup; target posture per `SECURITY_AND_HARDENING.md` §2 is `PermitRootLogin no` — tighten when convenient)*

### The Surface is now retired for dev

- No more Claude Code sessions on the Surface
- `.ssh/config` still has the `lsb-linode` alias if rollback is ever needed
- Any uncommitted work on the Surface should be checked against the VPS before closing the Surface workflow

### Backblaze account

- Backblaze B2 account created
- API credentials (`B2_KEY_ID`, `B2_APPLICATION_KEY`, `B2_BUCKET_NAME`) are in `/opt/lsb-agent/.env` on the VPS
- **No backup scripts have been written yet** — this is the next working task
- **Not using rclone** per Mark's decision (2026-04-22). See §4 below for the options to evaluate.

---

## 3. F2 status (for context)

F2 (shakedown-findings-batch-2) is **complete**. All 9 tasks landed on master. All 8 §8 sanity checks PASS on the 2026-04-21 re-shakedown.

Relevant commits (all on master):
- `9e687b3` T06 UTF-8 encoding on cdb_collect paths
- `4328f26` T04 truncation_type on elbow + CWE paths
- `5edea40` T07+T09 honest qa_passed + check_8 label-count
- `de6bf73` T03 cultural_centrality_scores wiring
- `60cae7f` T02 Romney eigenratio + `romney_small_n_warning` schema field
- `bcc441c` T01 classify_consensus dispatch
- `55f7a68` T05 split G1 wiring
- `8b8937b` T08 latency ceiling 30s → 60s
- `bca816e` T10 findings report
- Plus three in-flight fixes (`adb4090`, `9b7bfea`, `fd55cde`) — runner sys.path + cdb_analyze UTF-8

Test suite: 430/430 green. No CI failures post-T02.

---

## 4. Next working task: B2 backup layer

This is the single gating task for Phase 4a kickoff.

### What Mark's decided

- **Not rclone.** Mark's preference stands.
- Destination: Backblaze B2 bucket `lsb-backups` (see `.env`)
- Source paths (per `HOSTING_AND_DEV_OPS.md` §4.1): `data/raw/`, `data/processed/`, `data/results/`
- Also during shakedown windows: `data/shakedown/` (keep in sync until protocol §10 deletion)
- Cadence: nightly, 02:00 UTC (per §3.4 timer spec)
- Retention on bucket: 90-day versioned-file retention (Mark may have already set this at bucket creation)

### What's undecided — the Architect must rule before the Coder starts

**Tool choice.** Given "not rclone," the candidates are:

| Option | Pros | Cons |
|---|---|---|
| **b2 CLI** (`pip install b2`) | Official Backblaze tool; direct B2 API; shell-scriptable with systemd; no additional cloud-abstraction layer | Yet another CLI dep; not a Python library call |
| **b2sdk** (Python library, official from Backblaze) | Stays in Python; testable with fixtures; no shell string-handling; integrates cleanly with existing `cdb_collect` patterns | Adds a Python dep; need to write a small sync loop ourselves |
| **boto3 against B2's S3-compatible endpoint** | Standard AWS tooling; if we ever add other S3-likes (e.g., Cloudflare R2) the code transfers | Indirection layer through S3-compat; most LSB devs know boto3 already but it's not "native" B2 |
| **Raw `curl` + B2 HTTP API** | Zero additional deps | Pain; don't |

**Architect's call:** Weigh "stay in Python" (favors b2sdk or boto3) vs "simple shell + systemd" (favors b2 CLI). My lean: **b2sdk** — it's official, Pythonic, unit-testable with fixtures, and fits LSB's existing Python-first stack. But this is an Architect decision, not a Coder decision.

### The script the Coder will write

Wherever the Architect lands, the script needs to:

1. Read `B2_KEY_ID`, `B2_APPLICATION_KEY`, `B2_BUCKET_NAME` from `/opt/lsb-agent/.env` via `python-dotenv`
2. Compute source set: `data/raw/`, `data/processed/`, `data/results/`, optionally `data/shakedown/`
3. Compute destination prefix: `b2://<bucket>/YYYY-MM-DD/` or equivalent timestamped structure
4. Sync only new/changed files (incremental, not full re-upload)
5. Write a structured log to `logs/backup.log` (ISO timestamps, file count, bytes uploaded, exit status)
6. Exit non-zero on any file failure (so systemd/cron can alert)
7. Have a corresponding unit test using a B2 **mock** — per `CLAUDE.md` §6 rule 10 "no real API calls in tests," the test must not actually hit B2 during CI

### systemd units to create

Per `HOSTING_AND_DEV_OPS.md` §3.4 target design:

- `/etc/systemd/system/lsb-backup.service` — one-shot service that runs the backup script
- `/etc/systemd/system/lsb-backup.timer` — daily 02:00 UTC trigger

Existing spec at §3.4 is a template. Adapt for Linode paths.

### Freshness check (incident §5.1 action item)

Per the 2026-04-19 incident report §5.1, `scripts/qa_check.py` must report on the age of the most recent successful backup. Propose adding a `check_9_backup_freshness` to the battery: read `logs/backup.log` mtime, return `QAFailure` if older than 48 hours. Post to `#lsb-alerts` via the existing webhook path.

### Test restore requirement

Per incident §5.1 action item: "At least one off-host backup layer is configured and verified by a **test restore**." Before declaring the layer active:

1. Upload a canary file via the new script
2. Delete local copy
3. Restore from B2
4. Diff against original
5. Document success in `docs/status/YYYY-MM-DD-b2-test-restore.md`

### HOSTING_AND_DEV_OPS.md update

After the test restore passes:

- §4.1 Layer 3 status: "Planned" → "Active"
- §3.4 timer list: `lsb-backup.timer` status from "Planned" to "Active"
- §3.1 VPS identity: update from `lsb-agent-01` → new Linode identity (Architect decides new name — suggested `lsb-agent-02`)
- Retire the superseded-pointer callouts from the 2026-04-19 incident throughout the doc
- Replace the Surface-specific instructions added this week with Linode-specific ones

This is a substantial docs PR; the Architect should scope it alongside the backup-script PR or as a separate cleanup PR immediately after.

---

## 5. Open items *not* in scope for the next session

These are tracked here so they're not lost, but they are *not* the next task:

- **Move `run_qa_checks` into `cdb_collect.qa` module.** Currently in `scripts/qa_check.py` with a `sys.path` defensive-import hack in `runner._assemble_record` (commit `adb4090`). This is a future F-batch cleanup task.
- **Researcher onboarding guide for the open data bundle.** Low-priority, from the 3rd-party reviewer evaluation (`docs/status/2026-04-21-3rdparty-reviews-architect-eval.md`). Schedule post-Phase-4.
- **Exercise `--mode two_pass` in a future shakedown.** Validates T04's `"elbow"` label path on real data. Deferred.
- **Full HOSTING_AND_DEV_OPS.md rewrite.** Beyond the Layer 3 update above, the doc still has Hetzner-era assumptions sprinkled throughout. Schedule a dedicated rewrite PR after the backup layer is active.
- **SSH hardening.** Target posture per `SECURITY_AND_HARDENING.md` §2: `PermitRootLogin no`, SSH as `lsb` user only, passwordless sudo for `lsb`. Do this after backup is live, not before — you need working SSH to configure the changes.
- **Phase 4a kickoff.** Gated on backup layer live + CDA SME review of the 2026-04-21 shakedown findings report. Not the next session's work; the session after.

---

## 6. Workflow reminders for the new session

From the 2026-04-21 CLAUDE.md §8 update:

- **Default: direct commits to `master`.** One commit per task. Agent pipeline (Architect → CDA SME → Coder → Reviewer → Tester) still required; verdicts saved to `docs/status/YYYY-MM-DD-{task-id}-verdicts.md`.
- **Branch+PR exceptions:** experimental / multi-day work, schema changes (co-update with `DATA_DICTIONARY.md` in same commit per `CLAUDE.md` §6 rule 7), dep bumps, or explicit Mark request.
- **Tests run locally before every commit.** `uv run pytest && uv run ruff check . && uv run mypy packages/` is minimum.
- **Third-party reviewer docs** at `docs/3rdpartyreviews/` are *outside perspective, not authority.* Reference for useful framing; never override Mark / CLAUDE.md / CDA SME.

---

## 7. Suggested first-session script

The new Claude Code session, on first boot on the VPS, should:

1. `cd /opt/lsb-agent && git pull` — make sure the repo is at master tip (should include commit `bca816e`)
2. `uv sync` — install Python deps
3. `uv run pytest tests/` — confirm 430/430 green locally on VPS (sanity check the new host matches)
4. Read this doc, `CLAUDE.md`, and `docs/status/2026-04-21-shakedown-findings.md`
5. Spawn the Architect agent to decide the backup-tool question in §4 above (b2sdk vs boto3 vs b2 CLI)
6. After Architect's verdict, route to the Coder to implement the backup script + tests + systemd units
7. Reviewer + Tester, then the test-restore verification, then the HOSTING_AND_DEV_OPS.md updates

---

*End of handoff. File: `docs/status/2026-04-22-vps-handoff.md`. Commit this doc to master before closing the Surface session so the VPS session has it on pull.*
