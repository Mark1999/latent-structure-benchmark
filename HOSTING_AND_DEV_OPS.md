# LSB Hosting and DevOps

**Document name:** `HOSTING_AND_DEV_OPS.md`  
**Version:** v0.1.4 (Linode is sole dev + production host — see banner below)  
**Status:** Operational reference for the Coder agent and Mark  
**Audience:** Coder agent, Mark, anyone who needs to understand how LSB is deployed and where its data lives  
**Companion docs:** `ARCHITECTURE.md` (especially §4.4 publish layer, §4.3 storage, §6.7 open data, §7 resolved decisions), `SECURITY_AND_HARDENING.md` (account hardening, secret management), `PHASE_0_TASKS.md` (P0-T10 dashboard scaffold), `docs/INCIDENTS/2026-04-19-test-data-loss.md`, `docs/status/2026-04-22-vps-handoff.md`

> **Status banner (2026-04-23).** The project VPS is Linode `lsb-agent-02` (Shared 4GB, Ubuntu 24.04, `172.238.170.9`), with the repo at `/opt/lsb-agent` owned by the `lsb` user. The prior Hetzner `lsb-agent-01` was decommissioned on 2026-04-19 following the test-data loss incident. **Backup Layer 3 (Backblaze B2) is Active** as of 2026-04-22 — nightly at 02:00 UTC via `lsb-backup.timer`, verified by canary test-restore in `docs/status/2026-04-22-b2-test-restore.md`. This satisfies the `docs/INCIDENTS/2026-04-19-test-data-loss.md` §5.1 precondition for Phase 4a. **Dev posture (2026-04-23):** the Linode is now the **sole** development and production host. All Claude Code agent sessions, code authoring, direct-to-master commits, backups, and collection runs happen on the Linode. Mark reviews work via Cursor over SSH. The Surface Laptop Studio is no longer used for LSB work. Sections §3.1, §3.4, and §4.1 below are updated to reflect the Linode reality; other sections still carry Hetzner-era framing and will be rewritten in a dedicated pass (see the deferred items in `docs/status/2026-04-22-vps-handoff.md` §5).

**Purpose.** This document is the **single operational reference** for everything related to where LSB runs, where its data lives, what infrastructure costs money, and how deployments work. It is read by the Coder agent before any task touching `.github/workflows/`, Cloudflare Pages config, or environment variables. It is read by Mark before any operational change. Architectural decisions about hosting live in `ARCHITECTURE.md`; this document is the *operational* expression of those decisions — exact commands, exact account names, exact paths.

**Stability.** Changes to this document require Architect sign-off if they affect cost, latency, availability, or backup integrity. Cosmetic or clarifying changes do not.

**Changelog:**
- **v0.1.4** (2026-04-23) — Dev posture correction: Linode is the sole dev + production host. Surface Laptop Studio is no longer used for LSB work. Mark reviews via Cursor over SSH into the Linode. §3.1 "Dev posture" paragraph and the top-of-doc status banner updated; prior "Surface = primary dev" language in `docs/status/2026-04-22-vps-handoff.md` §2 and `docs/status/2026-04-22-b2-backup-architect-verdict.md` is historical and superseded.
- **v0.1.3** (2026-04-22) — Linode production VPS brought up as `lsb-agent-02` (`172.238.170.9`, Ubuntu 24.04, Shared 4GB). B2 backup layer implemented and verified: `scripts/backup.py` using `b2sdk`, `deploy/systemd/lsb-backup.{service,timer}` installed and enabled on the VPS, `check_9_backup_freshness` added to `scripts/qa_check.py`, canary test-restore PASS (`docs/status/2026-04-22-b2-test-restore.md`). §3.1, §3.4, and §4.1 updated; remaining Hetzner-era framing in other sections is deferred to a dedicated rewrite pass.
- **v0.1.2** (2026-04-19) — Infra pivot. `lsb-agent-01` decommissioned following a test-data loss on the VPS working copy (see `docs/INCIDENTS/2026-04-19-test-data-loss.md`). Development moved to Mark's local Surface Laptop Studio. New VPS TBD. Added top-of-doc status banner; VPS-specific sections carry the historical framing until rewritten. Tightened backup posture to a precondition, not a parallel deliverable.
- **v0.1.1** (2026-04-15) — Reality alignment pass. §3.1: SSH alias connects as `lsb` user. §3.2: note that processes run as `lsb`, note planned-vs-active services. §3.3: removed aspirational `backups/` directory, added `lsb:lsb` ownership. §3.4: documented parked `lsb-agent.service` (`ExecStart=/bin/false`), marked all systemd timers as planned. §3.5: documented SSH hardening (root login disabled, password auth disabled, key-only as `lsb` user), verified ufw active state. §4.1: added Status column — only layer 1 (working copy) is active; layers 2–4 are planned.
- **v0.1** — first draft. Documents Cloudflare Pages hosting, the `lsb-agent-01` Hetzner VPS, the four-layer backup strategy (Synology + Backblaze B2 + fireproof safe + Zenodo), the GitHub Actions CI/CD pipeline, the three Slack webhooks, and the cost summary. Aligned with `ARCHITECTURE.md` v0.7 — no Mac Mini, no on-prem GPU, no local inference layer.

---

## 1. Hosting overview

LSB has **four hosted surfaces** in v1, all small and most of them free or near-free:

| Surface | Provider | Cost | Purpose |
|---|---|---|---|
| **Dashboard** | Cloudflare Pages (free tier) | $0 / month | Public dashboard at `cogstructurelab.com`, served as static files from a Cloudflare global CDN |
| **Domain registration** | Cloudflare Registrar | ~$10–20 / year for `.com`, ~$50–70 / year for `.ai` | Both `cogstructurelab.com` and `cogstructurelab.ai` are owned; `.ai` redirects to `.com` |
| **Project VPS** | Hetzner Cloud (Helsinki region) | ~$12 / month | `lsb-agent-01` runs the collection runner, the QA_Runner, the cron jobs, and the social pipeline. CPX32 instance: 4 vCPU, 8 GB RAM, 160 GB SSD |
| **Open data bundle** | Backblaze B2 + Zenodo | ~$5 / month + free | Backblaze B2 hosts the bundle; Zenodo mints DOIs after Phase 4 validation. CC0 distribution per `ARCHITECTURE.md` §6.7 |

**Total recurring cost:** approximately $17 / month for hosting + $50–90 / year for domains. This excludes LLM API spend, which is the largest variable cost in the project but is *operational expense*, not hosting infrastructure.

The architecture is deliberately **server-light**. There is no API server to maintain, no database server to maintain, no realtime backend, no auth system. The dashboard is static files; the analysis is batch; the collection runner is a cron job on a single VPS. v0.4 design decisions explicitly committed to this; see `ARCHITECTURE.md` §4.4.5 ("Why no FastAPI") and §1 commitment 5 ("Small surface area").

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
curl -I https://cogstructurelab.com/ | grep -E "(Content-Security-Policy|Strict-Transport-Security|Referrer-Policy)"
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

## 3. `lsb-agent-02` — the project VPS (Linode)

### 3.1 Provisioning

- **Provider:** Linode (Akamai)
- **Plan:** Shared 4GB — 2 vCPU, 4 GB RAM, 80 GB SSD
- **Region:** Chicago, IL (US)
- **IP:** `172.238.170.9`
- **OS:** Ubuntu 24.04 LTS
- **SSH alias:** `ssh lsb-linode` (resolves to the `lsb` user on `lsb-agent-02`)
- **Repo path:** `/opt/lsb-agent`, owned `lsb:lsb`
- **Non-root user:** `lsb` (created 2026-04-22; Claude Code, the backup timer, and all LSB processes run under this user)
- **Claude Code on VPS:** installed (v2.1.117 at bring-up), authenticated to Mark's Max account, headless-capable
- **uv:** installed at `/home/lsb/.local/bin/uv` (v0.11.7 at bring-up); PATH persisted via `.bashrc` and `.profile`

**Dev posture (updated 2026-04-23).** The Linode `lsb-agent-02` is now the **sole** development and production host. All Claude Code agent sessions, code authoring, direct-to-master commits, backups, and collection runs happen on the Linode. Mark reviews the work via Cursor over SSH into the Linode. The Surface Laptop Studio is **no longer used** for LSB work — treat any prior "Surface = primary dev" language in companion docs as historical. There is one host; the `local-dev-host` vs `production-host` distinction the earlier plan assumed no longer applies.

**Prior VPS.** Hetzner `lsb-agent-01` (CPX32, Helsinki) was decommissioned on 2026-04-19 following the test-data loss incident. See `docs/INCIDENTS/2026-04-19-test-data-loss.md` for the incident report and `docs/status/2026-04-22-vps-handoff.md` §2 for the infrastructure timeline.

### 3.2 What runs on the VPS

| Service | What it does | When it runs |
|---|---|---|
| `cdb_collect/runner.py` | Pulls from the collection queue, makes API calls to Anthropic / OpenRouter / Hugging Face Inference Providers, writes `RawResponse` and `InformantRecord` records | Manually triggered by Mark via `python scripts/collect.py`, or via a cron during structured collection campaigns |
| `scripts/qa_check.py` (the QA_Runner) | Validates each freshly written `InformantRecord` against the six deterministic checks; posts failures directly to `#lsb-alerts` | Automatically invoked by `runner.py` after each record, also invokable manually for backfills |
| `cdb_social/runner.py` | Drafts social posts from new findings and writes them to `data/social_queue/pending/` for Mark to review | Cron, post-publish only |
| Backup sync | Pushes new content from `data/raw/`, `data/processed/`, and `data/results/` to Backblaze B2 | Cron, nightly at 02:00 UTC |
| `apps/ops_dashboard/app.py` (Streamlit) | Internal read-only inspection of collection results (freelist / pile-sort / decline interviews); bound to `127.0.0.1:8501`, accessible via `ssh -L 8501:localhost:8501 lsb-agent-02`; run on-demand in tmux with `uv run --with streamlit streamlit run apps/ops_dashboard/app.py --server.address=127.0.0.1` | On-demand in tmux |

All VPS processes run as the `lsb` user (uid 999), not root. The `lsb-agent.service` systemd unit enforces `User=lsb`, `Group=lsb`. Claude Code runs from `/home/lsb/.local/bin/claude` under the `lsb` user.

**Note:** The social runner cron and backup sync listed above are the target design. As of 2026-04-15, only `runner.py` and `qa_check.py` are active; the others are planned (see §3.4 and §4.1 for status).

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

**Active systemd timers:**

`lsb-backup.timer` — daily at 02:00 UTC, triggers `lsb-backup.service` which runs `scripts/backup.py` as the `lsb` user. **Installed and enabled on `lsb-agent-02` on 2026-04-22.** Unit files are repo-tracked at `deploy/systemd/lsb-backup.{service,timer}`; installation procedure (four `sudo` commands) is documented in each unit file's header comment. Freshness monitored by `check_9_backup_freshness` in `scripts/qa_check.py` — fails when `logs/backup.log` mtime is ≥ 48 hours old or the log is missing. Verified by canary test-restore on 2026-04-22 (see `docs/status/2026-04-22-b2-test-restore.md`).

**Planned systemd timers (not yet implemented):**

The following timers are the target design but do not exist yet. They will be created as part of the automation implementation work:

```
lsb-social-runner.timer        # Planned: Triggered post-publish via a hook, not a fixed schedule
```

**Collection runner.** `cdb_collect/runner.py` is **not** a systemd service — it runs interactively (via `tmux`) when Mark is conducting a collection campaign. This is deliberate: collection runs are bounded, expensive, and need a human in the loop, so they shouldn't be wired to fire automatically.

### 3.5 Access and operations

- **SSH access:** Mark only, key-based authentication only. Root SSH login is disabled (`PermitRootLogin no`). Password authentication is disabled (`PasswordAuthentication no`). Mark connects as the `lsb` user and uses `sudo` when root is needed (`/etc/sudoers.d/lsb` grants passwordless sudo to `lsb`).
- **Firewall:** Hetzner Cloud Firewall + ufw on the host. ufw is active with inbound rules for OpenSSH, port 80, and port 443. Outbound: unrestricted (the runner needs to reach all three LLM providers + Backblaze B2 + GitHub).
- **Updates:** unattended-upgrades enabled for security patches; major OS upgrades are manual

---

## 4. Storage and backup

LSB takes the backup story seriously because losing the raw data means losing the benchmark. Per `ARCHITECTURE.md` §4.3, `data/raw/informants.jsonl` is the canonical research corpus and is irreplaceable — re-collection is impossible because the prior versions of the models will no longer exist by the time you'd want to re-collect them.

### 4.1 The four backup layers

| Layer | Lives where | Cadence | Failure mode this layer catches | **Status** |
|---|---|---|---|---|
| **1 — Local on VPS** | `lsb-agent-02:/opt/lsb-agent/data/` | Continuous (this is the working copy) | Nothing — this is the primary, not a backup | **Active** on Linode `lsb-agent-02` since 2026-04-22 |
| **2 — Synology DS1522+ NAS** | Mark's home network, NAS pull via rsync over SSH | Nightly 03:00 local time (after the VPS-to-B2 push completes) | VPS hardware failure, accidental `rm`, ransomware on the VPS | **Planned** — rsync job and NAS share not yet configured |
| **3 — Backblaze B2** | Backblaze B2 bucket `lsb-backups` (private), nightly push from Linode | Nightly 02:00 UTC via `lsb-backup.timer` → `scripts/backup.py` (using `b2sdk`) | VPS regional outage, full home network loss, theft of the NAS | **Active** since 2026-04-22 — verified by canary test-restore (`docs/status/2026-04-22-b2-test-restore.md`) |
| **4 — Fireproof safe** | USB SSD physically stored in Mark's fireproof safe at home | Manually refreshed every 90 days | Backblaze account compromise, US-wide cloud provider outage, "everything is on fire" scenarios | **Planned** — no initial snapshot taken yet |

The four layers fail differently. Layer 2 catches the most common failure (VPS misconfiguration); layer 3 catches geographic correlated failures; layer 4 catches account-level adversarial failures. Layer 1 is not a backup, it's the working copy — it's listed here only to make the ordering clear.

**Current reality (2026-04-22):** Layer 1 (local working copy on `lsb-agent-02`) and Layer 3 (Backblaze B2, nightly at 02:00 UTC) are **Active**. Layers 2 (Synology NAS) and 4 (fireproof safe) remain **Planned** — they remain the target design but are not preconditions for Phase 4a. The Phase 4a precondition from `docs/INCIDENTS/2026-04-19-test-data-loss.md` §5.1 — "at least one off-host backup layer is configured and verified by a test restore" — is **satisfied** as of the 2026-04-22 canary round-trip.

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

### 5.2 GitHub Actions secrets

The following secrets must be configured in the GitHub repository settings (Settings → Secrets and variables → Actions):

| Secret | Used by | Sourced from |
|---|---|---|
| `LSB_ALERTS_WEBHOOK_URL` | (none in v1; used when cron-based alerting is added) | The Slack webhook for `#lsb-alerts` |
| `B2_KEY_ID` | (none in v1; Phase 6 if open bundle publishing moves to GitHub Actions) | Backblaze B2 |
| `B2_APPLICATION_KEY` | (none in v1; Phase 6) | Backblaze B2 |
| `CLOUDFLARE_API_TOKEN` | (none in v1; Cloudflare Pages auto-deploys without an API token) | — |

GitHub Actions does **not** need any LLM API keys, because no GitHub Actions job ever calls an LLM directly. The collection runner only ever runs on `lsb-agent-01`. This is a deliberate security simplification: the LLM API keys live in exactly one place (`lsb-agent-01:/opt/lsb-agent/.env`) and never travel.

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

## 6. The three Slack workspaces and channels

LSB has three operational Slack channels per `ARCHITECTURE.md` §5.4. All three live in the same Slack workspace ("Cognitive Structure Lab"); they are not separate workspaces.

| Channel | Posted by | Webhook env var | Where the env var is configured |
|---|---|---|---|
| `#lsb-alerts` | `scripts/qa_check.py` running on `lsb-agent-01`; `weekly-cost-alert.yml` running on GitHub Actions | `LSB_ALERTS_WEBHOOK_URL` | Both `lsb-agent-01:/opt/lsb-agent/.env` and GitHub Actions secrets |
| `#lsb-cda-sme` | The CDA SME agent (Opus) running in the Claude Code agent runtime | `LSB_CDA_SME_WEBHOOK_URL` | Mark's local Claude Code environment |
| `#lsb-ui-ux` | The UI/UX agent (Sonnet) running in the Claude Code agent runtime | `LSB_UI_UX_WEBHOOK_URL` | Mark's local Claude Code environment |

The webhook URLs are created in Slack via Slack App configuration (one Slack app with three Incoming Webhook integrations, one per channel). They are stored in 1Password and copied into the relevant `.env` files. They are never committed.

**Why webhooks rather than the Slack API.** Webhooks are the simplest possible posting mechanism — a single POST with a JSON body, no auth flow, no token refresh. LSB does not need to read from Slack, only post; the Slack API would be overkill. The downside is that webhook URLs are themselves credentials (anyone with the URL can post to the channel), which is why they're in `.env` and the password manager rather than in code.

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

The full list of environment variables LSB reads, where each one is set, and what it's for. **Variables in bold are required**; others are optional.

| Variable | Required? | Where set | Used by | Purpose |
|---|---|---|---|---|
| **`ANTHROPIC_API_KEY`** | Yes | `lsb-agent-01:.env` | `cdb_collect/adapters/anthropic.py` | Anthropic API auth |
| **`OPENROUTER_API_KEY`** | Yes | `lsb-agent-01:.env` | `cdb_collect/adapters/openrouter.py` | OpenRouter API auth |
| **`HUGGINGFACE_API_KEY`** | Yes | `lsb-agent-01:.env` | `cdb_collect/adapters/huggingface.py` | Hugging Face Inference Providers auth |
| **`B2_KEY_ID`** | Yes (for backups and open bundle publishing) | `lsb-agent-01:.env` | Nightly backup script, `scripts/build_db.py` | Backblaze B2 API auth |
| **`B2_APPLICATION_KEY`** | Yes | `lsb-agent-01:.env` | Same | Backblaze B2 API auth |
| **`LSB_ALERTS_WEBHOOK_URL`** | Yes | `lsb-agent-01:.env` | `scripts/qa_check.py` | Slack `#lsb-alerts` posting |
| **`LSB_CDA_SME_WEBHOOK_URL`** | Yes | Mark's local Claude Code env | CDA SME agent | Slack `#lsb-cda-sme` posting |
| **`LSB_UI_UX_WEBHOOK_URL`** | Yes | Mark's local Claude Code env | UI/UX agent | Slack `#lsb-ui-ux` posting |
| `OPENAI_API_KEY` | No | `lsb-agent-01:.env` (if used) | `cdb_collect/adapters/openai.py` (currently routed via OpenRouter; direct OpenAI is a future option) | Direct OpenAI API auth, not v1 |
| `GOOGLE_API_KEY` | No | Same | Same for Google | Same for Google |

`.env.example` at the repo root tracks the full list with placeholder values. The real `.env` is never committed; `.gitignore` enforces this and `gitleaks` is the second line of defense.

---

## 9. Cost summary

| Item | Cost | Cadence | Notes |
|---|---|---|---|
| Cloudflare Pages | $0 | monthly | Free tier covers v1 traffic comfortably |
| Cloudflare Registrar (`cogstructurelab.com`) | ~$10–12 | yearly | At-cost domain registration |
| Cloudflare Registrar (`cogstructurelab.ai`) | ~$50–70 | yearly | `.ai` is more expensive; LSB owns it for redirect purposes |
| Hetzner Cloud CPX32 (`lsb-agent-01`) | ~$12 (€11.90) | monthly | Helsinki region |
| Backblaze B2 storage (`lsb-backups`) | ~$5 | monthly | Estimated for v1 data volumes |
| Backblaze B2 storage (`lsb-open-data`) | <$1 | monthly | Bundle is small |
| Backblaze B2 egress | $0–2 | monthly | Highly variable; free up to ~30 GB/day via Bandwidth Alliance |
| Synology NAS | $0 incremental | — | Existing hardware Mark already owns |
| USB SSD for fireproof safe | $0 incremental | — | Existing hardware |
| Zenodo | $0 | — | Free for open science |
| HuggingFace Datasets | $0 | — | Free for public datasets |
| Cloudflare Email Routing (security contact) | $0 | monthly | Forwards `security@cogstructurelab.com` → Mark's ProtonMail. Setup: Mark-action M1 (one-time DNS + routing rule). Free Cloudflare feature; no subscription required. |
| **Total infrastructure** | **~$23 / month + ~$80 / year** | | Excluding LLM API spend |

The infrastructure cost is small enough to be a personal expense for Mark and does not require external funding or grant support to sustain.

---

## 10. Disaster recovery and incident response

The full incident response runbook lives in `docs/RUNBOOKS/incident_response.md` (Phase 6 deliverable, not yet written). Until that file exists, the high-level posture is:

- **Operational incidents** (QA failure, provider outage, runner crash, cost spike): post to `#lsb-alerts` if not already alerted there, Mark investigates within hours, decides whether to pause collection / switch providers / open a provider ticket.
- **Security incidents** (suspected key compromise, suspected unauthorized access, suspected data tampering): rotate the affected credential immediately, document in a private incident log, notify the security contact email, and pull the affected data from any public distribution if confirmed. The full procedure lives in `SECURITY_AND_HARDENING.md` §6.
- **Data integrity incidents** (suspected corruption of `informants.jsonl`, SHA256 manifest verification failures, restored backup looks wrong): pause all collection, snapshot the current state of `data/raw/` to a separate B2 bucket for forensics, verify the four-layer backup chain to identify which layer is the last known good, restore from the last known good layer, document the gap.
- **Total infrastructure loss** (Hetzner outage + Backblaze outage simultaneously): worst-case scenario. Restore from the fireproof safe USB SSD. Acknowledge data loss for any runs collected since the last 90-day refresh. This has never happened to anyone, but the layered backup design assumes it might.

The pattern in all four cases is the same: stop the bleeding first, document the state, restore from the last known good source, verify integrity end to end before resuming normal operations. LSB does not have a 24/7 on-call rotation — incident response is best-effort during Mark's working hours. This is appropriate for a research project at v1 scale.

---

## 11. What's deliberately not in v1

Listing these so the Coder agent doesn't drift into building them:

- **No realtime collection.** Everything is batch.
- **No multi-region hosting.** The single Helsinki VPS is fine for v1.
- **No automatic failover.** If `lsb-agent-01` is down, collection pauses until Mark fixes it.
- **No metric dashboards (Prometheus, Grafana, Datadog).** Structured logs to journald + the QA_Runner alert path are sufficient for v1 observability per `ARCHITECTURE.md` §6.4.
- **No automated rollback.** If a bad publish corrupts the dashboard, Mark git-reverts the offending commit and re-publishes manually.
- **No automated dependency upgrades** (beyond Dependabot opening PRs that still go through review).
- **No paid Cloudflare features** (WAF, bot management, image optimization). v1 ships on Cloudflare's free tier per resolved decision #21 in `ARCHITECTURE.md` §7.

These are all defensible deferrals for a v1 research project. They become real questions if LSB grows into a higher-traffic or higher-stakes deployment.

---

*End of `HOSTING_AND_DEV_OPS.md` v0.1. This is a living operational reference; update it before any change to hosting, backup, CI/CD, or env var configuration. Architectural decisions about hosting still live in `ARCHITECTURE.md`; this document is the operational expression of those decisions.*