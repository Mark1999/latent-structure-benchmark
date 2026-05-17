# Pre-Release Scan Report

**Run at:** 2026-05-17 21:00:07 UTC
**Run by:** `scripts/prerelease_scan.py`
**Repository state:** `4464aa4d617baff974e98d0ae83b691f59a8281d`
**Working tree:** dirty — 2 changed file(s)

**Overall result:** FAIL

---

## Per-check results

### Check 1 — gitleaks full history

**Status:** TOOL_MISSING
**Hits:** 0

**Details:**

- TOOL_MISSING — `gitleaks` is not installed. Install via `apt install gitleaks` or `brew install gitleaks`, then re-run.

**Remediation:** Rotate the credential immediately. Rewrite history with `git filter-repo` to remove the committed secret. Re-run this scan.

### Check 2 — forbidden vocabulary

**Status:** PASS
**Hits:** 0

### Check 3 — leaked internal paths

**Status:** FAIL
**Hits:** 49

**Details:**

- ARCHITECTURE.md:13 — contains `/home/lsb/` — `- **v0.7.1** (patch, 2026-04-15) — Docs and operational alignment only, no schema or architecture changes. PR #2 (`6a21f`
- ARCHITECTURE.md:1693 — contains `lsb-agent-02` — `- **lsb-agent-01** — the original Hetzner project VPS (CPX32, Helsinki) that ran `cdb_collect/runner.py`, `scripts/qa_ch`
- apps/ops_dashboard/README.md:17 — contains `lsb-agent-02` — `On `lsb-agent-02`, from the repo root (`/opt/lsb-agent`):`
- apps/ops_dashboard/README.md:39 — contains `lsb-agent-02` — `ssh -L 8501:localhost:8501 lsb-agent-02`
- apps/ops_dashboard/app.py:16 — contains `lsb-agent-02` — `SSH tunnel: ssh -L 8501:localhost:8501 lsb-agent-02`
- docs/DATA_DICTIONARY.md:1160 — contains `/home/lsb/` — `3. **Local filesystem path patterns:** `/opt/lsb-agent/...`, `/home/lsb/...`, `/home/markd/...`, `data/raw/...`, `data/r`
- docs/status/2026-04-22-b2-backup-architect-verdict.md:53 — contains `lsb-agent-02` — `- §3.1 VPS identity from Hetzner `lsb-agent-01` (decommissioned) to Linode (suggested `lsb-agent-02`, IP `172.238.170.9``
- docs/status/2026-04-22-b2-backup-architect-verdict.md:53 — contains `172.238.170.9` — `- §3.1 VPS identity from Hetzner `lsb-agent-01` (decommissioned) to Linode (suggested `lsb-agent-02`, IP `172.238.170.9``
- docs/status/2026-04-22-b2-backup-task6-reviewer-verdict.md:31 — contains `lsb-agent-02` — `- `lsb-agent-02` name consistent across banner, §3 heading, §3.1, §3.4, §4.1.`
- docs/status/2026-04-22-b2-backup-task6-reviewer-verdict.md:32 — contains `172.238.170.9` — `- IP `172.238.170.9` matches `docs/status/2026-04-22-b2-test-restore.md`.`
- docs/status/2026-04-22-b2-backup-task6-reviewer-verdict.md:33 — contains `lsb-agent-02` — `- `lsb-backup.timer` "Installed and enabled on `lsb-agent-02` on 2026-04-22" — factual: systemd install completed post-t`
- docs/status/2026-04-22-b2-test-restore.md:4 — contains `172.238.170.9` — `**Host:** Linode VPS (`172.238.170.9`), `/opt/lsb-agent`, `lsb` user`
- docs/status/2026-04-22-phase4a-kickoff-architect-verdict.md:4 — contains `lsb-agent-02` — `**Architect:** spawned from Claude Code session on Linode `lsb-agent-02``
- docs/status/2026-04-22-position-c-replay-verdict.md:1 — contains `lsb-agent-02` — `# Position C Replay Verdict — 2026-04-21 Shakedown on Linode `lsb-agent-02``
- docs/status/2026-04-22-position-c-replay-verdict.md:126 — contains `lsb-agent-02` — `The bring-up was same host (`lsb-agent-02`, `172.238.170.9`), same user (`lsb`), same Claude Code version (v2.1.117), sa`
- docs/status/2026-04-22-position-c-replay-verdict.md:126 — contains `172.238.170.9` — `The bring-up was same host (`lsb-agent-02`, `172.238.170.9`), same user (`lsb`), same Claude Code version (v2.1.117), sa`
- docs/status/2026-04-22-vps-handoff.md:42 — contains `172.238.170.9` — `- **IP:** 172.238.170.9`
- docs/status/2026-04-22-vps-handoff.md:159 — contains `lsb-agent-02` — `- §3.1 VPS identity: update from `lsb-agent-01` (Hetzner, decommissioned) → new Linode identity (Architect decides name `
- docs/status/2026-04-22-vps-handoff.md:177 — contains `172.238.170.9` — `- **Cloudflare DNS cutover.** `cogstructurelab.com` A record still points at the decommissioned Hetzner IP (`204.168.243`
- docs/status/2026-04-23-failures-as-findings-architect-verdict.md:4 — contains `lsb-agent-02` — `**Architect:** spawned from Claude Code session on Linode `lsb-agent-02``
- docs/status/2026-04-23-phase4a-completion.md:4 — contains `lsb-agent-02` — `**Author:** Coder (Claude Sonnet 4.6), Linode `lsb-agent-02``
- docs/status/2026-04-23-phase4a-completion.md:217 — contains `172.238.170.9` — `- Cloudflare DNS A-record cutover `cogstructurelab.com` → `172.238.170.9` — TBD, only after web server live`
- docs/status/2026-04-23-phase4a-open-items.md:106 — contains `172.238.170.9` — `- **Cloudflare DNS A-record cutover** `cogstructurelab.com` → `172.238.170.9` — TBD, only after web server live.`
- docs/status/2026-04-23-phase4a-t6-qa-sweep.md:5 — contains `lsb-agent-02` — `**Executor:** Coder (Claude Sonnet 4.6), Linode `lsb-agent-02``
- docs/status/2026-04-23-phase4a1-architect-plan-amendment-1.md:201 — contains `lsb-agent-02` — `**Scope:** Execute `uv run python scripts/run_decline_backfill.py --execute --source informants` on `lsb-agent-02`. Expe`
- docs/status/2026-04-23-phase4a1-architect-plan-amendment-1.md:218 — contains `lsb-agent-02` — `**Scope:** Execute `uv run python scripts/run_decline_backfill.py --execute --source failures` on `lsb-agent-02`. Expect`
- docs/status/2026-04-23-phase4a1-architect-plan.md:87 — contains `lsb-agent-02` — `### T3 — Live batch run on `lsb-agent-02``
- docs/status/2026-04-23-phase4a1-architect-plan.md:89 — contains `lsb-agent-02` — `**Scope:** Execute `scripts/run_decline_backfill.py --execute` on `lsb-agent-02` against the real Phase 4a `informants.j`
- docs/status/2026-04-23-phase4a1-t2-reviewer-verdict.md:314 — contains `lsb-agent-02` — `**Next step:** T3A — live run on lsb-agent-02 against 3 informants-origin records (~$0.15`
- docs/status/2026-04-23-phase4a1-t3a-run-log.md:23 — contains `lsb-agent-02` — `Working directory: `/opt/lsb-agent` on `lsb-agent-02`.`
- docs/status/2026-05-07-phase4b-architect-plan.md:14 — contains `lsb-agent-02` — `- `HOSTING_AND_DEV_OPS.md` (VPS Linode lsb-agent-02; wall-clock context)`
- docs/status/2026-05-07-phase4b-architect-plan.md:252 — contains `lsb-agent-02` — `**Wall-clock estimate.** Phase 4a recovery ran 20 cells in ~60 minutes. Naive scaling: 1,800 cells × 3 minutes/cell = ~9`
- docs/status/2026-05-08-spend-cap-removal-architect-plan.md:57 — contains `/home/lsb/` — ``/home/lsb/.claude/projects/-opt-lsb-agent/memory/feedback_test_budget.md` is rewritten from a "$10 ceiling for asking p`
- docs/status/2026-05-08-spend-cap-removal-architect-plan.md:96 — contains `/home/lsb/` — `| `/home/lsb/.claude/projects/-opt-lsb-agent/memory/feedback_test_budget.md` | Full rewrite (see §1.4 + replacement text`
- docs/status/2026-05-08-spend-cap-removal-architect-plan.md:182 — contains `/home/lsb/` — `Path: `/home/lsb/.claude/projects/-opt-lsb-agent/memory/feedback_test_budget.md``
- docs/status/2026-05-08-spend-cap-removal-architect-plan.md:221 — contains `/home/lsb/` — `| 5 | **SC-T5** | Memory rewrite | `/home/lsb/.claude/projects/-opt-lsb-agent/memory/feedback_test_budget.md` (out-of-tr`
- docs/status/2026-05-08-spend-cap-removal-architect-plan.md:338 — contains `/home/lsb/` — `| **SC-T5** | `/home/lsb/.claude/projects/-opt-lsb-agent/memory/feedback_test_budget.md` (current); `feedback_dispatch_h`
- docs/status/2026-05-08-spend-cap-removal-sc-t5-reviewer-verdict.md:38 — contains `/home/lsb/` — `Reviewed `/home/lsb/.claude/projects/-opt-lsb-agent/memory/feedback_test_budget.md` against plan §3.6.`
- docs/status/2026-05-08-spend-cap-removal-sc-t5-tester-verdict.md:27 — contains `/home/lsb/` — `     /home/lsb/.claude/projects/-opt-lsb-agent/memory/feedback_test_budget.md`
- docs/status/2026-05-08-spend-cap-removal-sc-t5-tester-verdict.md:52 — contains `/home/lsb/` — `grep -n 'test_budget' /home/lsb/.claude/projects/-opt-lsb-agent/memory/MEMORY.md`
- docs/status/2026-05-12-phase6-T9-architect-plan.md:49 — contains `/home/lsb/` — `   - **Local filesystem paths** matching `data/raw/`, `data/results/`, `data/processed/`, `/opt/lsb-agent/`, `/home/lsb/`
- docs/status/2026-05-12-phase6-T9-tester-verdict.md:91 — contains `/home/lsb/` — ``sk-ant-api`, `sk-or-v1-`, `hf_`, `xoxb-`, `/opt/lsb-agent/`, `/home/lsb/`,`
- docs/status/2026-05-17-phase8-architect-kickoff.md:329 — contains `/home/lsb/` — `3. **Leaked-internal-path scan** — `/home/lsb/`, `/home/markdd/`, `/Users/mark`, `/opt/lsb-agent/.env`, `lsb-agent-02`, `
- docs/status/2026-05-17-phase8-architect-kickoff.md:329 — contains `/home/markdd/` — `3. **Leaked-internal-path scan** — `/home/lsb/`, `/home/markdd/`, `/Users/mark`, `/opt/lsb-agent/.env`, `lsb-agent-02`, `
- docs/status/2026-05-17-phase8-architect-kickoff.md:329 — contains `/Users/mark` — `3. **Leaked-internal-path scan** — `/home/lsb/`, `/home/markdd/`, `/Users/mark`, `/opt/lsb-agent/.env`, `lsb-agent-02`, `
- docs/status/2026-05-17-phase8-architect-kickoff.md:329 — contains `lsb-agent-02` — `3. **Leaked-internal-path scan** — `/home/lsb/`, `/home/markdd/`, `/Users/mark`, `/opt/lsb-agent/.env`, `lsb-agent-02`, `
- scripts/run_phase4a_t4.sh:10 — contains `/home/lsb/` — `export PATH="/home/lsb/.local/bin:$PATH"`
- tests/cdb_publish/test_failures.py:110 — contains `/home/lsb/` — `        path = "/home/lsb/.env"`
- tests/cdb_publish/test_failures_gap_fill.py:273 — contains `/home/lsb/` — `        re.compile(r"/home/lsb/"),`

**Remediation:** Remove the path reference from the file. If it is already in git history, use `git filter-repo` to rewrite. Re-run this scan.

### Check 4 — real email addresses

**Status:** PASS
**Hits:** 0

### Check 5 — API key patterns

**Status:** PASS
**Hits:** 0

### Check 6 — public URL validity

**Status:** PASS
**Hits:** 0

### Check 7 — .env and credential-file presence

**Status:** PASS
**Hits:** 0

### Check 8 — license-coverage sanity

**Status:** PASS
**Hits:** 0

---

## Summary

| Check | Result | Hits |
|---|---|---|
| 1 gitleaks full history | TOOL_MISSING | 0 |
| 2 forbidden vocabulary | PASS | 0 |
| 3 leaked internal paths | FAIL | 49 |
| 4 real email addresses | PASS | 0 |
| 5 API key patterns | PASS | 0 |
| 6 public URL validity | PASS | 0 |
| 7 .env and credential-file presence | PASS | 0 |
| 8 license-coverage sanity | PASS | 0 |

---

## Gate status for T11 (the public flip)

**GATE: FAIL** — remediation required before T11 (the public flip). Fix every FAIL above and re-run. The scan must exit 0 within the 24 hours immediately preceding M12.

This report MUST be re-generated within the 24 hours immediately preceding M12 (the actual flip).
