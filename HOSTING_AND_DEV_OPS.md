# LSB Hosting and DevOps

**Document name:** `HOSTING_AND_DEV_OPS.md`  
**Version:** v0.2 (local-first development, VPS deferred, Slack optional)  
**Status:** Operational reference for the Coder agent and Mark  
**Audience:** Coder agent, Mark, anyone who needs to understand how LSB is deployed and where its data lives  
**Companion docs:** `ARCHITECTURE.md` (especially §4.4 publish layer, §4.3 storage, §6.7 open data, §7 resolved decisions), `SECURITY_AND_HARDENING.md` (account hardening, secret management), `PHASE_0_TASKS.md` (P0-T10 dashboard scaffold)

**Purpose.** This document is the **single operational reference** for everything related to where LSB runs, where its data lives, what infrastructure costs money, and how deployments work. It is read by the Coder agent before any task touching `.github/workflows/`, Cloudflare Pages config, or environment variables. It is read by Mark before any operational change. Architectural decisions about hosting live in `ARCHITECTURE.md`; this document is the *operational* expression of those decisions — exact commands, exact account names, exact paths.

**Stability.** Changes to this document require Architect sign-off if they affect cost, latency, availability, or backup integrity. Cosmetic or clarifying changes do not.

**Changelog:**
- **v0.2** (2026-04-18) — Local-first development mode. The Hetzner VPS has been decommissioned and LSB now runs from Mark's local workstation. §1: added §1.1 "Current operating mode" callout; hosting table reflects "VPS deferred" state. §3: retitled "Future project VPS — deferred"; whole section kept as forward-looking spec, with a banner noting it is not currently provisioned. §3.6 (new): "Local development mode" — documents where `.env`, `data/raw/`, and the runner actually live today. §6: Slack channels reframed as **optional** notification surfaces — when a webhook env var is unset, `qa_check.py` and the agent runtime fall back to stdout plus a rotating log file at `logs/`. §8: Slack webhooks marked optional; key-location rows updated to show local-dev vs. VPS-deployed splits. §11: added "VPS-hosted operation is deferred, not cancelled" so the Coder doesn't drift into building VPS-only code paths. **Trigger for VPS provisioning:** Claude Code flags it when unattended long-running collection, scheduled crons, or the four-layer backup chain become load-bearing — i.e., when local-only operation starts blocking the research. Until that flag is raised, local dev is the supported mode.
- **v0.1.1** (2026-04-15) — Reality alignment pass. §3.1: SSH alias connects as `lsb` user. §3.2: note that processes run as `lsb`, note planned-vs-active services. §3.3: removed aspirational `backups/` directory, added `lsb:lsb` ownership. §3.4: documented parked `lsb-agent.service` (`ExecStart=/bin/false`), marked all systemd timers as planned. §3.5: documented SSH hardening (root login disabled, password auth disabled, key-only as `lsb` user), verified ufw active state. §4.1: added Status column — only layer 1 (working copy) is active; layers 2–4 are planned.
- **v0.1** — first draft. Documents Cloudflare Pages hosting, the `lsb-agent-01` Hetzner VPS, the four-layer backup strategy (Synology + Backblaze B2 + fireproof safe + Zenodo), the GitHub Actions CI/CD pipeline, the three Slack webhooks, and the cost summary. Aligned with `ARCHITECTURE.md` v0.7 — no Mac Mini, no on-prem GPU, no local inference layer.

---

## 1. Hosting overview

### 1.1 Current operating mode — local-first development

**As of 2026-04-18, LSB runs entirely from Mark's local workstation.** The Hetzner VPS (`lsb-agent-01`) has been decommissioned. Collection, QA, analysis, and dashboard builds all execute locally; the public dashboard is still served by Cloudflare Pages from GitHub. The VPS spec in §3 below is preserved as **forward-looking** infrastructure — it will be re-provisioned when local-only operation starts blocking the research.

**Trigger for re-provisioning the VPS.** Claude Code is responsible for flagging when the project outgrows local-only operation. The trigger conditions are any of:

- An unattended collection campaign needs to run for more than a working day without Mark's laptop being awake.
- The four-layer backup chain (§4) becomes load-bearing — i.e., the raw data set is large enough or valuable enough that losing the local copy would be a project-ending event.
- A scheduled cron (cost report, social runner, backup sync) becomes part of the routine operating cadence rather than an ad-hoc manual step.
- Public visitors start depending on freshness cadence that a human-in-the-loop cron can't deliver.

Until one of those is true, local-first is the supported mode and the Coder should not build VPS-only code paths. Collection, QA, analysis, and publish scripts must all run unmodified on a laptop.

### 1.2 Hosted surfaces

LSB has **two active hosted surfaces** today, plus one deferred and one conditional:

| Surface | Provider | Cost | Status | Purpose |
|---|---|---|---|---|
| **Dashboard** | Cloudflare Pages (free tier) | $0 / month | **Active** | Public dashboard at `cogstructurelab.com`, served as static files from a Cloudflare global CDN |
| **Domain registration** | Cloudflare Registrar | ~$10–20 / year for `.com`, ~$50–70 / year for `.ai` | **Active** | Both `cogstructurelab.com` and `cogstructurelab.ai` are owned; `.ai` redirects to `.com` |
| **Project VPS** | Hetzner Cloud (Helsinki region) | ~$12 / month | **Deferred** (decommissioned 2026-04) | Will run the collection runner, the QA_Runner, the cron jobs, and the social pipeline when re-provisioned. Spec: CPX32 — 4 vCPU, 8 GB RAM, 160 GB SSD. See §3. |
| **Open data bundle** | Backblaze B2 + Zenodo | ~$5 / month + free | **Planned** (post Phase 4 validation) | Backblaze B2 hosts the bundle; Zenodo mints DOIs after Phase 4 validation. CC0 distribution per `ARCHITECTURE.md` §6.7 |

**Current recurring cost:** approximately $0 / month for hosting + $50–90 / year for domains. This goes up by ~$12/month when the VPS is re-provisioned and by ~$5/month once the open data bundle goes live. LLM API spend (capped at $300/month per `ARCHITECTURE.md` §6.2 three-tier defense) is tracked separately as operational expense, not hosting infrastructure.

The architecture is deliberately **server-light**. There is no API server to maintain, no database server to maintain, no realtime backend, no auth system. The dashboard is static files; the analysis is batch; the collection runner is a script that runs interactively. v0.4 design decisions explicitly committed to this; see `ARCHITECTURE.md` §4.4.5 ("Why no FastAPI") and §1 commitment 5 ("Small surface area"). That server-light posture is exactly what makes local-first development viable — there is no background service that *has* to be up.

---

## 2. Cloudflare Pages — dashboard hosting

### 2.1 Account and project

- **Cloudflare account:** Mark's primary Cloudflare account, secured with two YubiKey 5C NFC keys per `SECURITY_AND_HARDENING.md` §5
- **Project name in Cloudflare Pages:** `lsb-dashboard` (informal; the production hostname is `cogstructurelab.com`)
- **Connected GitHub repository:** the LSB monorepo (set up in P0-T10 per `PHASE_0_TASKS.md`)
- **Build branch:** `main`. PRs against `main` get preview deployments at automatic preview URLs; merging to `main` triggers the production deployment.

### 2.2 Build configuration

| Setting | Value |
|---|---|
| Framework preset | Vite |
| Build command | `npm run build` |
| Build output directory | `apps/dashboard/dist` |
| Root directory | `apps/dashboard` |
| Node version | 20.x (latest LTS at deployment time) |
| Environment variables | None required for build (the dashboard is fully static and reads no secrets) |

The build command runs from `apps/dashboard/`, which is set as the root directory in the Cloudflare Pages project configuration. Vite produces the `dist/` output, and Cloudflare Pages serves it directly. Because `apps/dashboard/public/data/` is inside the Vite build root, all JSON files written there by `cdb_publish/build.py` are included verbatim in the dist bundle and served at `cogstructurelab.com/data/...` with Cloudflare's global CDN caching automatically applied (per `ARCHITECTURE.md` §4.4.3).

### 2.3 Headers and CSP

Headers are configured via `apps/dashboard/public/_headers` (Cloudflare Pages reads this file at deploy time). The full CSP and security headers spec lives in `SECURITY_AND_HARDENING.md` §3.1 and §3.2; this section just confirms that the file is in the right place and that Cloudflare picks it up.

To verify after deployment:

```bash
curl -I https://cogstructurelab.com/ | grep -E "(Content-Security-Policy|X-Frame-Options|Strict-Transport-Security)"
```

All three should be present. If they aren't, the `_headers` file is in the wrong location or the build didn't include it.

### 2.4 Caching strategy

Cloudflare Pages applies the following cache behavior automatically (no codebase configuration needed):

| Path pattern | Cache-Control | Why |
|---|---|---|
| `/data/*.v*.json` (versioned files) | `public, max-age=31536000, immutable` | Versioned files never change; cache forever |
| `/data/{domain}.json`, `/data/manifest.json` | `public, max-age=3600` | Unversioned files update on each release; one-hour cache balances freshness and CDN efficiency |
| `/assets/*` (Vite-built JS/CSS with content hashes) | `public, max-age=31536000, immutable` | Content-hashed filenames; cache forever |
| `/index.html` | `public, max-age=300` | Index page; five-minute cache |

This pattern is `ARCHITECTURE.md` §4.4.4 in operational form. No cache rules need to be set in code; Cloudflare's defaults are correct.

### 2.5 Custom domain configuration

- **Primary:** `cogstructurelab.com` configured in the Cloudflare Pages project as the custom domain
- **Secondary:** `cogstructurelab.ai` configured with a 301 redirect rule pointing to `https://cogstructurelab.com/$1`
- **HTTPS:** Cloudflare's automatic SSL/TLS certificate (free tier handles this; cert renews automatically)
- **SSL/TLS mode:** Full (strict) — Cloudflare validates the origin certificate even though the origin is Cloudflare Pages itself
- **DNS:** Cloudflare DNS (LSB uses Cloudflare as registrar, so DNS lives in the same account)

### 2.6 Preview deployments

Every PR against `main` gets an automatic preview deployment at a Cloudflare-generated URL. The UI/UX agent uses preview URLs to verify visual changes before approving frontend PRs (per `ARCHITECTURE.md` §5.1 UI/UX agent row). The Reviewer agent's frontend rule (rule 6) requires that any PR touching `apps/dashboard/` link the preview URL in the PR description so it can be reviewed visually, not just code-reviewed.

---

## 3. `lsb-agent-01` — the project VPS (deferred)

> **Status as of 2026-04-18: this VPS is not currently provisioned.** The Hetzner instance was decommissioned in April 2026 and the project now runs locally on Mark's workstation (see §3.6). The spec below is preserved as the target state for re-provisioning once any of the trigger conditions in §1.1 is met. When that happens, this section becomes live reality again and the changelog entry for the next version of this document records the date.

### 3.1 Provisioning

- **Provider:** Hetzner Cloud
- **Region:** Helsinki (Finland) — chosen for low cost, EU jurisdiction, and proximity to most LLM provider edge points
- **Instance type:** CPX32 — 4 vCPU (AMD), 8 GB RAM, 160 GB NVMe SSD, 20 TB included egress
- **OS:** Ubuntu 24.04 LTS
- **Cost:** approximately €11.90 / month at the time of writing (~$12 USD), billed by the hour
- **SSH alias:** `ssh lsb` (resolves to the `lsb` user on `lsb-agent-01` in Mark's local `~/.ssh/config`)
- **Cursor Remote-SSH:** the host is accessible from Cursor via Remote-SSH, connecting as the `lsb` user (see Mark's Cursor configuration)

### 3.2 What runs on the VPS

| Service | What it does | When it runs |
|---|---|---|
| `cdb_collect/runner.py` | Pulls from the collection queue, makes API calls to Anthropic / OpenRouter / Hugging Face Inference Providers, writes `RawResponse` and `InformantRecord` records | Manually triggered by Mark via `python scripts/collect.py`, or via a cron during structured collection campaigns |
| `scripts/qa_check.py` (the QA_Runner) | Validates each freshly written `InformantRecord` against the six deterministic checks; posts failures directly to `#lsb-alerts` | Automatically invoked by `runner.py` after each record, also invokable manually for backfills |
| `scripts/cost_report.py` | Aggregates spend from the raw lake and posts a weekly summary | Cron, every Monday morning UTC |
| `cdb_social/runner.py` | Drafts social posts from new findings and writes them to `data/social_queue/pending/` for Mark to review | Cron, post-publish only |
| Backup sync | Pushes new content from `data/raw/`, `data/processed/`, and `data/results/` to Backblaze B2 | Cron, nightly at 02:00 UTC |

All VPS processes run as the `lsb` user (uid 999), not root. The `lsb-agent.service` systemd unit enforces `User=lsb`, `Group=lsb`. Claude Code runs from `/home/lsb/.local/bin/claude` under the `lsb` user.

**Note:** The cost report cron, social runner cron, and backup sync listed above are the target design. As of 2026-04-15, only `runner.py` and `qa_check.py` are active; the others are planned (see §3.4 and §4.1 for status).

The VPS is **not** an inference host. There is no Ollama, no llama.cpp, no on-prem GPU. All model inference happens via the three remote API surfaces. The VPS just orchestrates calls and stores results.

### 3.3 Filesystem layout

```
/opt/lsb-agent/                     # the LSB monorepo, cloned from GitHub; owned lsb:lsb
├── packages/
├── scripts/
├── data/
│   ├── raw/                        # the canonical informants.jsonl + per-call atoms
│   ├── processed/
│   └── results/
├── .env                            # secrets, never committed, mode 600, owned lsb:lsb
└── logs/                           # systemd journal output, log rotation via journald
```

**Note:** The `backups/` directory shown in earlier drafts of this document does not exist yet. It will be created when the four-layer backup chain (§4) is implemented. See the status notes in §4.1 for what is currently active vs. planned.

The data lives on the VPS local SSD. The 160 GB allocation is enough for several years of LSB collection at expected volumes; if it fills, Hetzner allows live volume expansion without downtime.

### 3.4 systemd services

**`lsb-agent.service`** exists as a systemd unit but is currently **parked**:

- `User=lsb`, `Group=lsb`
- `WorkingDirectory=/opt/lsb-agent`
- `EnvironmentFile=/opt/lsb-agent/.env`
- `ExecStart=/bin/false` (placeholder — the previous `orchestrator.py` was deleted in commit 16a0be4 on 2026-04-14; there is nothing for the service to run yet)
- Status: `disabled` (won't auto-start) and `inactive (dead)`

When an orchestrator is reintroduced, only the `ExecStart=` line needs editing.

**Planned systemd timers (not yet implemented):**

The following timers are the target design but do not exist yet. They will be created as part of the backup and automation implementation work:

```
lsb-cost-report.timer          # Planned: Mondays 09:00 UTC, runs scripts/cost_report.py
lsb-backup.timer               # Planned: Daily 02:00 UTC, runs the backup sync to Backblaze B2
lsb-social-runner.timer        # Planned: Triggered post-publish via a hook, not a fixed schedule
```

**Collection runner.** `cdb_collect/runner.py` is **not** a systemd service — it runs interactively (via `tmux`) when Mark is conducting a collection campaign. This is deliberate: collection runs are bounded, expensive, and need a human in the loop, so they shouldn't be wired to fire automatically.

### 3.5 Access and operations

- **SSH access:** Mark only, key-based authentication only. Root SSH login is disabled (`PermitRootLogin no`). Password authentication is disabled (`PasswordAuthentication no`). Mark connects as the `lsb` user and uses `sudo` when root is needed (`/etc/sudoers.d/lsb` grants passwordless sudo to `lsb`).
- **Firewall:** Hetzner Cloud Firewall + ufw on the host. ufw is active with inbound rules for OpenSSH, port 80, and port 443. Outbound: unrestricted (the runner needs to reach all three LLM providers + Backblaze B2 + GitHub).
- **Updates:** unattended-upgrades enabled for security patches; major OS upgrades are manual

### 3.6 Local development mode (current)

Until the VPS is re-provisioned, LSB runs from Mark's local workstation. The layout:

- **Repo location:** the LSB monorepo is cloned to Mark's local filesystem (path is workstation-specific; `/home/user/latent-structure-benchmark/` in CI-managed agent worktrees).
- **`.env` location:** lives at the repo root, mode 600, never committed. `.gitignore` and `gitleaks` are both lines of defense. The real `.env` replaces the `lsb-agent-01:/opt/lsb-agent/.env` location referenced throughout this document.
- **Data location:** `data/raw/`, `data/processed/`, `data/results/` live inside the repo tree. The canonical `data/raw/informants.jsonl` is append-only by convention and by the CI check (unchanged from VPS operation).
- **Collection runner:** `python scripts/collect.py` runs interactively in a terminal. No systemd, no tmux session on a remote box. For long runs, Mark uses `tmux` or `screen` locally, or runs the script in a terminal that he leaves open.
- **QA_Runner:** `scripts/qa_check.py` runs automatically after each collection record. If `LSB_ALERTS_WEBHOOK_URL` is set, it posts to Slack; if unset, it writes to stdout and to `logs/qa_alerts.log` (see §6 for the fallback behavior).
- **Analysis:** `python scripts/analyze.py` runs locally, writes to `data/results/`.
- **Dashboard build:** `cd apps/dashboard && npm run build` runs locally; Cloudflare Pages picks up the build from `main` via GitHub (unchanged from VPS operation — CI was never on the VPS in the first place).
- **Backups:** there is currently no automated backup chain. Mark relies on git (code + schemas are pushed to GitHub) plus whatever disk-level backup his workstation already has. The raw data set is small enough that this is acceptable during development, but one of the trigger conditions in §1.1 is "raw data valuable enough to need real backups" — when that fires, the VPS and the four-layer chain (§4) come online together.
- **Cron jobs (planned):** `cost_report.py`, `social_runner.py`, and the nightly backup sync are **not run locally** during the development phase. They activate when the VPS returns.

**What changed vs. VPS operation:**

| Thing | VPS mode | Local-dev mode |
|---|---|---|
| `.env` file | `lsb-agent-01:/opt/lsb-agent/.env` | Repo-root `.env` on Mark's workstation |
| LLM API keys | Only on VPS, never on Mark's machine | On Mark's workstation (by necessity) |
| Collection runner | Interactive tmux on VPS | Interactive terminal on workstation |
| QA_Runner alerts | Always posted to `#lsb-alerts` | Posted to `#lsb-alerts` if webhook is set, else stdout + `logs/qa_alerts.log` |
| Scheduled crons | Planned on VPS | Disabled (run by hand when needed) |
| Backups | Four-layer chain (planned) | git + workstation disk backup only |
| Dashboard build | Via Cloudflare Pages (unchanged) | Via Cloudflare Pages (unchanged) |
| CI (ruff, mypy, pytest) | GitHub Actions (unchanged) | GitHub Actions (unchanged) |

Local-dev mode is **not** a feature branch of the architecture — it is the same codebase running in a different environment. No code paths are local-only. When the VPS returns, the only changes are where `.env` lives and which scheduler invokes the scripts.

---

## 4. Storage and backup

LSB takes the backup story seriously because losing the raw data means losing the benchmark. Per `ARCHITECTURE.md` §4.3, `data/raw/informants.jsonl` is the canonical research corpus and is irreplaceable — re-collection is impossible because the prior versions of the models will no longer exist by the time you'd want to re-collect them.

### 4.1 The four backup layers

| Layer | Lives where | Cadence | Failure mode this layer catches | **Status** |
|---|---|---|---|---|
| **1 — Local on VPS** | `lsb-agent-01:/opt/lsb-agent/data/raw/` | Continuous (this is the working copy) | Nothing — this is the primary, not a backup | **Active** |
| **2 — Synology DS1522+ NAS** | Mark's home network, NAS pull via rsync over SSH | Nightly 03:00 local time (after the VPS-to-B2 push completes) | VPS hardware failure, accidental `rm`, ransomware on the VPS | **Planned** — rsync job and NAS share not yet configured |
| **3 — Backblaze B2** | Backblaze B2 bucket `lsb-backups`, region US-West | Nightly 02:00 UTC, push from VPS | Hetzner regional outage, full home network loss, theft of the NAS | **Planned** — `lsb-backup.timer` not yet created, B2 sync not yet configured |
| **4 — Fireproof safe** | USB SSD physically stored in Mark's fireproof safe at home | Manually refreshed every 90 days | Backblaze account compromise, US-wide cloud provider outage, "everything is on fire" scenarios | **Planned** — no initial snapshot taken yet |

The four layers fail differently. Layer 2 catches the most common failure (VPS misconfiguration); layer 3 catches geographic correlated failures; layer 4 catches account-level adversarial failures. Layer 1 is not a backup, it's the working copy — it's listed here only to make the ordering clear.

**Current reality (2026-04-15):** Only layer 1 (the working copy on the VPS) is active. Layers 2–4 are the target design and should be implemented before collection campaigns begin in earnest. A Hetzner snapshot (`pre-lsb-chown-2026-04-15`) exists as temporary rollback protection for the recent lsb user migration but is not a substitute for the four-layer chain.

### 4.2 Backblaze B2 configuration

- **Account:** dedicated LSB account, secured with two YubiKey 5C NFC keys per `SECURITY_AND_HARDENING.md` §5
- **Bucket name:** `lsb-backups` (private, not public)
- **Bucket name for open data:** `lsb-open-data` (public, for the open bundle distribution per `ARCHITECTURE.md` §6.7)
- **Lifecycle policy on `lsb-backups`:** versioned files retained for 90 days; older versions removed automatically
- **Lifecycle policy on `lsb-open-data`:** no automatic deletion (open data is never retracted)
- **Application key:** scoped to read+write on `lsb-backups` only, stored in `lsb-agent-01:/opt/lsb-agent/.env` as `B2_KEY_ID` and `B2_APPLICATION_KEY`. Never committed.
- **Cost:** $0.005/GB/month storage + $0.01/GB egress over the free 1GB/day allowance. Expected v1 monthly cost: ~$5 for backups + ~$0–2 for open data egress depending on traffic.

### 4.3 Synology NAS configuration

- **Device:** Synology DS1522+ in Mark's home network
- **Share:** dedicated `lsb-backups` share, accessible only by a service account
- **Access:** rsync over SSH from `lsb-agent-01` using a dedicated SSH key (NOT the main lsb key; this one is scoped to the rsync user on the NAS only)
- **Retention:** rolling 30 days of nightly snapshots
- **Hardware redundancy:** the NAS itself has RAID redundancy across its drives, so the layer-2 backup itself has internal redundancy

### 4.4 The fireproof safe layer

- **Drive:** USB SSD (model and capacity vary; currently a 2 TB Samsung T7)
- **Encryption:** full-disk encryption (LUKS or VeraCrypt)
- **Refresh cadence:** every 90 days, Mark removes the drive from the safe, plugs it into his Surface Studio, mounts it, runs an rsync from the latest Backblaze B2 snapshot, unmounts, and returns it to the safe
- **What goes on it:** `data/raw/informants.jsonl`, `data/results/`, `data/grounding/`, the latest released open bundle, and a copy of the current `.env.example` (NOT `.env`) for reference. Total volume is small (low single-digit GB).
- **What does not go on it:** anything from the LSB GitHub repo (which is itself a backup of the code), anything containing real API keys, anything with PII

### 4.5 Restore procedures

The restore procedures live in `docs/RUNBOOKS/restore.md` (Phase 1 deliverable, not yet written). When that file exists, this section will link to it and stop duplicating the procedures. For now, the high-level outline:

1. **VPS rebuild from scratch.** Provision a fresh CPX32, SSH in, install Python 3.11+, clone the LSB repo from GitHub, restore `.env` from the password manager, restore `data/raw/`, `data/processed/`, and `data/results/` from the most recent Backblaze B2 snapshot. Expected wall-clock time: ~2 hours.
2. **Single-file restore.** rsync the file from the most recent Backblaze B2 snapshot. Expected wall-clock time: ~5 minutes.
3. **Backblaze account loss.** Restore from the Synology NAS snapshot. Expected wall-clock time: ~30 minutes (depending on whether the VPS needs to be rebuilt at the same time).
4. **Synology NAS loss.** Restore from Backblaze. Then re-establish the layer-2 NAS-pull cron job.
5. **Total disaster (everything except the fireproof safe).** Restore from the USB SSD. Re-establish all upstream backup layers from the restored data. Acknowledge that the restored data is up to 90 days stale per the safe-refresh cadence.

---

## 5. CI/CD pipeline

### 5.1 GitHub Actions workflows

All workflows live in `.github/workflows/`. Each is a single YAML file scoped to one job.

| Workflow | Trigger | What it runs | Phase added |
|---|---|---|---|
| `ci.yml` | Push to any branch, PR against `main` | ruff check, mypy on `packages/`, pytest on `tests/`, the `cdb_analyze` no-LLM-imports static check (per `ARCHITECTURE.md` §1 commitment 6 and §4.2 binding constraint) | P0-T6 |
| `publish.yml` | Push to `main` that touches `data/results/` | Runs `python scripts/publish.py`, commits the resulting JSON files to `apps/dashboard/public/data/`, pushes back to `main` (which triggers the Cloudflare Pages auto-deploy) | Phase 6 (manual until then) |
| `weekly-cost-report.yml` | Cron, every Monday 09:00 UTC | Runs `scripts/cost_report.py --month current` and writes to `data/cost_reports/{YYYY-MM-DD}.txt`, commits and pushes | Phase 6 |
| `weekly-cost-alert.yml` | Cron, every Monday 10:00 UTC (after the cost report) | Reads the latest cost report, checks if projected monthly spend exceeds 80% of `CDB_MAX_SPEND_USD`, if so posts an alert to `#lsb-alerts` | Phase 6 |

The `weekly-cost-alert.yml` job is the third tier of the spend-cap defense per `ARCHITECTURE.md` §6.2 (tier 1 is the in-process runtime cap, tier 2 is the per-provider account caps, tier 3 is this weekly check). It posts to `#lsb-alerts` rather than to `#lsb-cda-sme` because it's an operational alert, not a development decision — see `ARCHITECTURE.md` §5.4 for the channel routing rules.

### 5.2 GitHub Actions secrets

The following secrets must be configured in the GitHub repository settings (Settings → Secrets and variables → Actions):

| Secret | Used by | Sourced from |
|---|---|---|
| `LSB_ALERTS_WEBHOOK_URL` | `weekly-cost-alert.yml` | The Slack webhook for `#lsb-alerts` |
| `B2_KEY_ID` | (none in v1; Phase 6 if open bundle publishing moves to GitHub Actions) | Backblaze B2 |
| `B2_APPLICATION_KEY` | (none in v1; Phase 6) | Backblaze B2 |
| `CLOUDFLARE_API_TOKEN` | (none in v1; Cloudflare Pages auto-deploys without an API token) | — |

GitHub Actions does **not** need any LLM API keys, because no GitHub Actions job ever calls an LLM directly. The collection runner only runs on the active collection host — Mark's workstation in local-first development mode, and `lsb-agent-01` when the VPS is re-provisioned (never on GitHub Actions). This is a deliberate security simplification: the LLM API keys live in one active `.env` file at a time and never travel into CI.

### 5.3 Branch protection on `main`

Configured in GitHub repository settings (Settings → Branches → Branch protection rules):

- **Require pull request reviews before merging:** yes, 1 reviewer (Mark, since `CODEOWNERS` lists Mark as the sole owner pre-launch)
- **Dismiss stale pull request approvals when new commits are pushed:** yes
- **Require status checks to pass before merging:** yes — `ci.yml` is the required check
- **Require conversation resolution before merging:** yes
- **Restrict who can push to matching branches:** yes, Mark only
- **Do not allow bypassing the above settings:** yes, including for repository administrators

This is enforced from the moment the repo is created in P0-T1; the Phase 0 task list includes a checklist line for Mark to confirm.

### 5.4 Dependabot

Configuration lives at `.github/dependabot.yml` (created in P0-T9). Two ecosystems:

- **`uv` / Python** — checks `pyproject.toml` weekly, opens PRs for security updates and minor version bumps with the `dependencies` and `python` labels
- **`npm`** — checks `apps/dashboard/package.json` weekly, opens PRs for security updates and minor version bumps with the `dependencies` and `npm` labels

Dependabot PRs go through the same `ci.yml` pipeline as any other PR. The Reviewer agent reviews them (Reviewer rules apply); Mark merges or closes them.

---

## 6. Slack channels (optional notification surfaces)

LSB defines three operational Slack channels per `ARCHITECTURE.md` §5.4. All three live in the same Slack workspace ("Cognitive Structure Lab"); they are not separate workspaces. **All three are optional.** When the corresponding webhook env var is unset, the code that would have posted to Slack falls back to stdout plus a rotating log file under `logs/`. The fallback is not degraded operation — it is a supported mode for local development, where Mark is at the terminal and does not need a cross-device ping.

| Channel | Posted by | Webhook env var | Fallback when unset |
|---|---|---|---|
| `#lsb-alerts` | `scripts/qa_check.py`; `weekly-cost-alert.yml` on GitHub Actions | `LSB_ALERTS_WEBHOOK_URL` | stdout + `logs/qa_alerts.log`; GitHub Actions job still succeeds |
| `#lsb-cda-sme` | The CDA SME agent (Opus) in the Claude Code agent runtime | `LSB_CDA_SME_WEBHOOK_URL` | Verdict printed in the agent's turn output and written to `docs/verdicts/<date>-cda-sme-<task>.md` |
| `#lsb-ui-ux` | The UI/UX agent (Sonnet) in the Claude Code agent runtime | `LSB_UI_UX_WEBHOOK_URL` | Verdict printed in the agent's turn output and written to `docs/verdicts/<date>-ui-ux-<task>.md` |

**When webhooks are set** (VPS or any mode where cross-device notifications matter), they are created in Slack via Slack App configuration (one Slack app with three Incoming Webhook integrations, one per channel), stored in 1Password, and copied into the relevant `.env` files. They are never committed.

**Why webhooks rather than the Slack API.** When used, webhooks are the simplest possible posting mechanism — a single POST with a JSON body, no auth flow, no token refresh. LSB does not need to read from Slack, only post; the Slack API would be overkill. The downside is that webhook URLs are themselves credentials (anyone with the URL can post to the channel), which is why they're in `.env` and the password manager rather than in code. Reviewer rule R10 in `SECURITY_AND_HARDENING.md` §9 still applies: a webhook URL that does exist must never be committed, regardless of whether it's currently wired up.

**Local-dev default.** During the local-first development phase, the recommended setup is to leave `LSB_CDA_SME_WEBHOOK_URL` and `LSB_UI_UX_WEBHOOK_URL` unset and let the verdict files accumulate under `docs/verdicts/` — they're durable, greppable, and reviewable in PRs. `LSB_ALERTS_WEBHOOK_URL` is useful to set if Mark wants phone notifications for long collection runs, but is not required.

---

## 7. Open data publication

Per `ARCHITECTURE.md` §6.7, LSB publishes its full result set as open data after the Phase 4 validation gates pass. Pre-validation, the bundle exists on Backblaze B2 in a private state for testing; post-validation, it goes public.

### 7.1 Backblaze B2 distribution

- **Bucket:** `lsb-open-data` (separate from `lsb-backups`)
- **Visibility:** public after Phase 4 validation; private before
- **Bucket URL pattern:** `https://f000.backblazeb2.com/file/lsb-open-data/{filename}` (or a friendlier custom domain post-launch — TBD)
- **Egress economics:** Backblaze B2 has a free egress allowance to Cloudflare's CDN via the Bandwidth Alliance. If traffic grows enough to be expensive, LSB routes the bundle through Cloudflare's CDN as a free pass-through.
- **Build process:** `scripts/build_db.py` reads `data/raw/informants.jsonl` and writes `lsb.sqlite`; both files plus `build_db.py`, `DATA_DICTIONARY.md`, and the prompt templates are tarred into `lsb_open_bundle_v{N}.tar.gz` and uploaded via the B2 CLI

### 7.2 Zenodo DOI minting

- **Account:** Mark's Zenodo account, secured with the same YubiKey hardware
- **Process per release:** upload the tarred bundle, fill out the metadata form (title, authors, description, keywords, CC0 license, related identifiers including the GitHub repo URL and the dashboard URL), publish. Zenodo mints a DOI immediately and a versioned DOI for that specific release plus a "latest" DOI that always points at the most recent.
- **Cadence:** one Zenodo release per LSB release (a release = a new analysis version published to the dashboard)
- **Old versions:** never deleted. Zenodo's permanent-versioning policy means earlier releases retain their DOIs and remain citable forever. This is why the §6.7 withdrawal policy explicitly notes that Zenodo retraction is not unilateral.

### 7.3 HuggingFace Datasets mirror

- **Account:** Mark's HuggingFace account, currently `AILLM1999`, secured with the same YubiKey hardware
- **Dataset card:** describes the bundle, links back to the dashboard and the Zenodo DOI, repeats the CC0 / CC-BY-4.0 license breakdown from `ARCHITECTURE.md` §6.6
- **Cadence:** updated on each release in lockstep with the Backblaze B2 distribution
- **Why it exists:** HuggingFace is the discovery surface for ML researchers; Backblaze + Zenodo is the citation surface for academic researchers. The two audiences overlap but not fully, and the cost of mirroring is essentially zero.

---

## 8. Environment variables

The full list of environment variables LSB reads, where each one is set, and what it's for. **Variables in bold are required**; others are optional. The "Where set" column shows the local-dev location first, with the VPS location in parentheses for when the VPS is re-provisioned.

| Variable | Required? | Where set | Used by | Purpose |
|---|---|---|---|---|
| **`ANTHROPIC_API_KEY`** | Yes | Workstation `.env` (→ `lsb-agent-01:.env` when VPS returns) | `cdb_collect/adapters/anthropic.py` | Anthropic API auth |
| **`OPENROUTER_API_KEY`** | Yes | Workstation `.env` (→ `lsb-agent-01:.env`) | `cdb_collect/adapters/openrouter.py` | OpenRouter API auth |
| **`HUGGINGFACE_API_KEY`** | Yes | Workstation `.env` (→ `lsb-agent-01:.env`) | `cdb_collect/adapters/huggingface.py` | Hugging Face Inference Providers auth |
| **`CDB_MAX_SPEND_USD`** | Yes (default `300`) | Workstation `.env` (→ `lsb-agent-01:.env`) | `cdb_collect/runner.py` (tier 1 of the three-tier spend defense) | Hard runtime spend cap per `ARCHITECTURE.md` §6.2 |
| `B2_KEY_ID` | No (required once backup/open-bundle publishing is live) | Workstation `.env` (→ `lsb-agent-01:.env`) | Future backup script, `scripts/build_db.py` | Backblaze B2 API auth |
| `B2_APPLICATION_KEY` | No (same) | Same | Same | Backblaze B2 API auth |
| `LSB_ALERTS_WEBHOOK_URL` | No (optional; stdout + `logs/qa_alerts.log` fallback) | Workstation `.env` and/or GitHub Actions secrets | `scripts/qa_check.py`, `weekly-cost-alert.yml` | Slack `#lsb-alerts` posting |
| `LSB_CDA_SME_WEBHOOK_URL` | No (optional; `docs/verdicts/` fallback) | Workstation Claude Code env | CDA SME agent | Slack `#lsb-cda-sme` posting |
| `LSB_UI_UX_WEBHOOK_URL` | No (optional; `docs/verdicts/` fallback) | Workstation Claude Code env | UI/UX agent | Slack `#lsb-ui-ux` posting |
| `OPENAI_API_KEY` | No | Workstation `.env` (if used) | `cdb_collect/adapters/openai.py` / `openai_compat.py` | Direct OpenAI API auth |
| `GOOGLE_API_KEY` | No | Same | `cdb_collect/adapters/google.py` | Direct Google Gemini auth |
| `XAI_API_KEY` | No | Same | `cdb_collect/adapters/xai.py` | Direct xAI auth |

`.env.example` at the repo root tracks the full list with placeholder values. The real `.env` is never committed; `.gitignore` enforces this and `gitleaks` is the second line of defense.

**On the change from v0.1.** The three Slack webhook URLs were "Required" in v0.1 because they were load-bearing for the operational alerting and pipeline gating. In v0.2 they are optional: the QA_Runner and the two gating agents both degrade gracefully to local output when the webhook is unset. This reflects the local-first development mode — when Mark is at the terminal, Slack is a convenience, not a requirement. When the VPS returns and collection starts running unattended, setting `LSB_ALERTS_WEBHOOK_URL` becomes strongly recommended (and in practice required for any multi-hour campaign) so that QA failures don't sit unnoticed.

---

## 9. Cost summary

| Item | Cost | Cadence | Status | Notes |
|---|---|---|---|---|
| Cloudflare Pages | $0 | monthly | Active | Free tier covers v1 traffic comfortably |
| Cloudflare Registrar (`cogstructurelab.com`) | ~$10–12 | yearly | Active | At-cost domain registration |
| Cloudflare Registrar (`cogstructurelab.ai`) | ~$50–70 | yearly | Active | `.ai` is more expensive; LSB owns it for redirect purposes |
| Hetzner Cloud CPX32 (`lsb-agent-01`) | ~$12 (€11.90) | monthly | **Deferred** | Decommissioned 2026-04; re-provisioned when §1.1 triggers fire |
| Backblaze B2 storage (`lsb-backups`) | ~$5 | monthly | Deferred | Comes online with the VPS and the four-layer backup chain |
| Backblaze B2 storage (`lsb-open-data`) | <$1 | monthly | Planned (post Phase 4) | Bundle is small |
| Backblaze B2 egress | $0–2 | monthly | Planned | Highly variable; free up to ~30 GB/day via Bandwidth Alliance |
| Synology NAS | $0 incremental | — | Deferred | Existing hardware Mark already owns; layer 2 of the backup chain |
| USB SSD for fireproof safe | $0 incremental | — | Deferred | Existing hardware; layer 4 of the backup chain |
| Zenodo | $0 | — | Planned | Free for open science |
| HuggingFace Datasets | $0 | — | Planned | Free for public datasets |
| ProtonMail security contact | ~$5 | monthly | Active | Existing personal Proton account; LSB pays for the dedicated `security@cogstructurelab.ai` address as part of the existing plan |
| **Current infrastructure total** | **~$5 / month + ~$60–80 / year** | | | Local-dev mode, Phase 0/1 |
| **Projected infrastructure total when VPS returns** | **~$23 / month + ~$80 / year** | | | Excluding LLM API spend |
| LLM API spend (variable) | Up to $300 | monthly | Active | Capped via the three-tier defense per `ARCHITECTURE.md` §6.2 |

The infrastructure cost is small enough to be a personal expense for Mark and does not require external funding or grant support to sustain. The LLM API spend is the largest variable and is what the spend cap exists to control.

---

## 10. Disaster recovery and incident response

The full incident response runbook lives in `docs/RUNBOOKS/incident_response.md` (Phase 6 deliverable, not yet written). Until that file exists, the high-level posture is:

- **Operational incidents** (QA failure, provider outage, runner crash, cost spike): post to `#lsb-alerts` if the webhook is configured, or surface in `logs/qa_alerts.log` / stdout if not. Mark investigates within hours, decides whether to pause collection / switch providers / open a provider ticket.
- **Security incidents** (suspected key compromise, suspected unauthorized access, suspected data tampering): rotate the affected credential immediately, document in a private incident log, notify the security contact email, and pull the affected data from any public distribution if confirmed. The full procedure lives in `SECURITY_AND_HARDENING.md` §6.
- **Data integrity incidents** (suspected corruption of `informants.jsonl`, SHA256 manifest verification failures, restored backup looks wrong): pause all collection. In VPS mode, snapshot the current state of `data/raw/` to a separate B2 bucket for forensics and verify the four-layer backup chain to identify which layer is the last known good. In local-dev mode, copy `data/raw/` to a timestamped sibling directory for forensics and rely on git history plus workstation disk backups; acknowledge that the weaker chain is one of the reasons local-dev mode only runs during early development.
- **Total infrastructure loss** (all hosting providers down simultaneously): worst-case scenario. In VPS mode, restore from the fireproof safe USB SSD. In local-dev mode, rely on the GitHub remote for code and on whatever workstation disk backup Mark has. This has never happened to anyone, but it's one of the reasons the VPS + four-layer chain comes back online before any high-value collection campaign.

The pattern in all four cases is the same: stop the bleeding first, document the state, restore from the last known good source, verify integrity end to end before resuming normal operations. LSB does not have a 24/7 on-call rotation — incident response is best-effort during Mark's working hours. This is appropriate for a research project at v1 scale.

---

## 11. What's deliberately not in v1

Listing these so the Coder agent doesn't drift into building them:

- **VPS-hosted operation is deferred, not cancelled.** The VPS spec in §3 is forward-looking and will come back online when any of the §1.1 trigger conditions fires. The Coder must not build code paths that only work on the VPS or only work locally — the same scripts must run in both modes, controlled by `.env` location and scheduler choice.
- **No realtime collection.** Everything is batch.
- **No multi-region hosting.** A single VPS (when re-provisioned) is fine for v1.
- **No automatic failover.** If the collection host (local workstation or VPS) is down, collection pauses until Mark resumes it.
- **No metric dashboards (Prometheus, Grafana, Datadog).** Structured logs to stdout + journald + the QA_Runner alert path are sufficient for v1 observability per `ARCHITECTURE.md` §6.4.
- **No automated rollback.** If a bad publish corrupts the dashboard, Mark git-reverts the offending commit and re-publishes manually.
- **No automated dependency upgrades** (beyond Dependabot opening PRs that still go through review).
- **No paid Cloudflare features** (WAF, bot management, image optimization). v1 ships on Cloudflare's free tier per resolved decision #21 in `ARCHITECTURE.md` §7.

These are all defensible deferrals for a v1 research project. They become real questions if LSB grows into a higher-traffic or higher-stakes deployment.

---

*End of `HOSTING_AND_DEV_OPS.md` v0.1. This is a living operational reference; update it before any change to hosting, backup, CI/CD, or env var configuration. Architectural decisions about hosting still live in `ARCHITECTURE.md`; this document is the operational expression of those decisions.*