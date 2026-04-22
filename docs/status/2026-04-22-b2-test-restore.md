# B2 Backup Layer — Test-Restore Verification (Task #5)

**Date:** 2026-04-22
**Host:** Linode VPS (`172.238.170.9`), `/opt/lsb-agent`, `lsb` user
**Executor:** Claude Code session (Opus 4.7), acting as orchestrator (no Coder agent spawned for this operational step)
**Preceding gates:** Task #2 Reviewer PASS (`0f435bb`), Task #3 Reviewer PASS (`93331ea`), Task #4 Reviewer PASS-WITH-NOTES (`0f69c85`)
**Architect spec:** `docs/status/2026-04-22-b2-backup-architect-verdict.md` §4.5
**Incident gating:** `docs/INCIDENTS/2026-04-19-test-data-loss.md` §5.1 action item ("At least one off-host backup layer is configured and verified by a **test restore**.")

---

## Verdict: **PASS**

Byte-identical round-trip confirmed. The B2 backup layer is **live** as of this doc. Phase 4a kickoff is no longer gated on backup verification (remaining gate: CDA SME review of `docs/status/2026-04-21-shakedown-findings.md`).

---

## 1. Preflight finding — `B2_BUCKET_NAME` config fix

On the first authorize + `get_bucket_by_name` call, B2 returned `NonExistentBucket: No such bucket: LSB`. Cause: `.env` on this VPS had `B2_BUCKET_NAME=LSB` while the actual bucket is `lsb-backups-mark1999` (Backblaze bucket names are globally unique; plain `lsb-backups` was unavailable, Mark registered the suffixed variant). The key ID and application key authorized correctly and revealed the real bucket via `api.list_buckets()`.

**Fix applied (local only, not committed — `.env` is gitignored):**

```
B2_BUCKET_NAME=lsb-backups-mark1999
```

**Documentation note:** `docs/status/2026-04-22-vps-handoff.md` §4 and the Architect verdict §1 both describe the destination as bucket `lsb-backups`. That's the conceptual name; the literal bucket name includes the `-mark1999` suffix. `.env.example` still carries the generic `lsb-backups` placeholder, which is acceptable as a template value (every operator will substitute their own globally-unique name).

---

## 2. Canary round-trip

### Canary file

| Field | Value |
|---|---|
| Local path | `data/raw/.canary-2026-04-22.txt` |
| Payload UUID | `aa09383f-b421-4a35-a605-e40e2b5f59ea` |
| Created at | `2026-04-22T16:05:32Z` |
| Size | 138 bytes |
| Local SHA-256 (original) | `08eb3a42024eb257b09d868c219a2ae678a9dc8465e5cc4f8ba96be46e240bdc` |

Note: `data/raw/` was created ad hoc for this test (the directory did not exist on this fresh VPS). It was removed after cleanup to restore pre-test state.

### Upload via `scripts/backup.py`

Run started `2026-04-22T16:05:47Z`, completed `2026-04-22T16:05:49Z`. Exit code 0.

```
2026-04-22T16:05:47Z INFO Backup run started (dry_run=False, date_prefix=2026-04-22)
2026-04-22T16:05:47Z INFO Files enumerated: 4
2026-04-22T16:05:47Z INFO UPLOADED .canary-2026-04-22.txt (138 bytes) -> 2026-04-22/data/raw/.canary-2026-04-22.txt
2026-04-22T16:05:47Z INFO UPLOADED .gitkeep (0 bytes) -> 2026-04-22/data/results/.gitkeep
2026-04-22T16:05:48Z INFO UPLOADED 0.1.json (15891 bytes) -> 2026-04-22/data/results/family/0.1.json
2026-04-22T16:05:49Z INFO UPLOADED 0.2.json (29440 bytes) -> 2026-04-22/data/results/family/0.2.json
2026-04-22T16:05:49Z INFO SUMMARY considered=4 uploaded=4 skipped=0 bytes_uploaded=45469 exit_code=0
```

Four files were enumerated and uploaded: the canary plus three pre-existing project files in `data/results/`. `data/processed/` and `data/shakedown/` are absent on this VPS; both were correctly skipped as first-class normal state (no warning, no error).

### B2 file info (post-upload)

| Field | Value |
|---|---|
| B2 key | `2026-04-22/data/raw/.canary-2026-04-22.txt` |
| B2 file ID | `4_zf6e99facb8a5b42e9dd50e1a_f118f45fde3b53bb2_d20260422_m160547_c005_v0501041_t0031_u01776873947584` |
| B2 upload timestamp (ms since epoch) | `1776873947584` (= `2026-04-22T16:05:47.584Z`) |
| B2 content SHA-1 | `edd46f76bab183eb8433044449172d9b1024136a` |
| Reported size | 138 bytes |

### Restore

1. Local canary deleted: `data/raw/.canary-2026-04-22.txt` → removed (confirmed `exists() == False`).
2. Downloaded from B2 via `b2sdk` `bucket.download_file_by_id(...)` + `.save_to("data/raw/.canary-restored.txt")`.
3. Restored file size: 138 bytes.
4. Restored SHA-256: `08eb3a42024eb257b09d868c219a2ae678a9dc8465e5cc4f8ba96be46e240bdc`.

### Diff

| Check | Result |
|---|---|
| Size match | ✓ (138 == 138) |
| Raw bytes match | ✓ |
| SHA-256 match | ✓ |

**Byte-identical restore confirmed.**

---

## 3. Cleanup

All test artifacts removed; no spill-over:

- `data/raw/.canary-2026-04-22.txt` — deleted (pre-restore step).
- `data/raw/.canary-restored.txt` — deleted.
- `data/raw/` empty directory — removed (pre-test state restored).
- B2 canary file (all versions) — deleted via `bucket.delete_file_version(id, name)`. `bucket.get_file_info_by_name(...)` subsequently raised `FileNotPresent`, confirming removal. Only one version existed (90-day retention did not retain a hidden copy for this run).
- `/tmp/test_restore.py`, `/tmp/test_cleanup*.py` — deleted.

### Remaining B2 bucket contents at `2026-04-22/` prefix (real project files, retained per design)

```
2026-04-22/data/results/.gitkeep          (0 bytes)
2026-04-22/data/results/family/0.1.json   (15891 bytes)
2026-04-22/data/results/family/0.2.json   (29440 bytes)
```

These are the actual pre-existing LSB project files that the backup script legitimately uploaded as part of its normal operation. They were not created or modified during this test — they were in `data/results/` before the run and remain in B2 after cleanup. This is the expected first successful off-host backup of LSB data on this host.

---

## 4. Layer status

| Layer | Status before this test | Status after this test |
|---|---|---|
| Host disk | Active (primary data on VPS at `/opt/lsb-agent/data/`) | Active |
| Local backup (if any) | N/A | N/A |
| B2 off-host (`HOSTING_AND_DEV_OPS.md` §4.1 Layer 3) | Planned | **Active** |

`HOSTING_AND_DEV_OPS.md` still reflects the Hetzner-era framing and calls Layer 3 "Planned." Updating that doc is task #6 (unblocked by this verdict).

---

## 5. Known follow-ups surfaced by this task

1. **`.env.example` bucket placeholder.** Currently `B2_BUCKET_NAME=lsb-backups`. Consider either (a) adding a `# replace with your globally-unique bucket name` comment, or (b) leaving as-is and trusting operators to substitute. Cosmetic — defer.
2. **systemd timer not yet installed on VPS.** The unit files at `deploy/systemd/lsb-backup.{service,timer}` exist in the repo but have not been copied to `/etc/systemd/system/` or enabled. The install commands in the file headers are ready to run. This is a VPS-side operator step, not a code commit; can be done immediately after this verdict is committed.
3. **`check_9_backup_freshness` will now start returning PASS** on the VPS because `logs/backup.log` exists and has a recent entry. It remains unregistered with `#lsb-alerts` until a QA battery run on the VPS includes it — no action required.
4. **Forwarded from task #4 Reviewer verdict:** `check_9` sits in a per-record battery but is an infrastructure check. Architect knowingly placed it for clean migration when `run_qa_checks → cdb_collect.qa` refactor lands. No action now.

---

## 6. Incident §5.1 action item closure

Incident `docs/INCIDENTS/2026-04-19-test-data-loss.md` §5.1 required: **"At least one off-host backup layer is configured and verified by a test restore."**

✓ **Off-host backup layer configured:** `scripts/backup.py` + `deploy/systemd/lsb-backup.{service,timer}` + `check_9_backup_freshness`, all merged on master.
✓ **Verified by test restore:** this document. Byte-identical round-trip of a canary file with full audit trail above.

The precondition for Phase 4a collection is now satisfied with respect to backup. The remaining Phase 4a gate is the CDA SME review of `docs/status/2026-04-21-shakedown-findings.md`.

---

*End of verdict. Task #5 complete. Next: task #6 (HOSTING_AND_DEV_OPS.md updates), then systemd install on VPS as an ops step.*
