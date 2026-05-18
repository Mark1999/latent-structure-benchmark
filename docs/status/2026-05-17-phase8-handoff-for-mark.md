# Phase 8 Handoff — Pick up tomorrow

**Filed:** 2026-05-17 (end of session)
**For:** Mark, picking up Phase 8 on 2026-05-18 or later
**Master commit at handoff:** `3813a71`
**GitHub sync:** clean. 165 commits pushed to `origin/master`.
**Test floor:** 1791 pytest pass, ruff + mypy clean.

---

## Order amendment (2026-05-18)

**The original sequence had M8/T8 (Zenodo) before M11/T11 (public flip). This is impossible:** Zenodo's GitHub OAuth integration requests `public_repo` scope, so it cannot see private repos in the linked-accounts list. The M8 prep step "find `Mark1999/latent-structure-benchmark`" literally won't show the repo while it's private.

**New order — flip public first, then Zenodo:**
1. Block 1 operational (M1, M3, M4, M5/M6, M7) — unchanged
2. Coder tasks T6, T7, T9, T10 — dispatched while the repo is still private
3. Re-run pre-release scan (must PASS, ≤24h before flip)
4. **M10 + M11 + M12 — Public flip** (originally last; now happens here)
5. **M8 prep + T8 — Zenodo** (originally before flip; now after, since repo is now visible)
6. M9 — Tag `v1.0.0` → Zenodo auto-archives → DOI minted
7. M13 — First social post (the actual launch moment)

Why this works: the dramatic "launch moment" is the first Bluesky post (M13), not the GitHub flip. The repo can sit publicly visible with zero traffic in the gap between M11 and M13 — nobody is watching the repo URL until you announce it. The pre-release scan already passed (`ea8130d` + `cc50dca` re-confirmed), so the audit work that justifies the flip is done.

---

## Where you left off

**Phase 8 progress: 5 of 11 tasks closed.**

| Task | State |
|---|---|
| T1 license-coverage audit | ✓ closed |
| T2 SECURITY.md contact finalization | ✓ closed |
| T3 README public-readiness rewrite | ✓ closed (FAIL → fix → PASS) |
| T4 GitHub settings runbook | ✓ closed |
| T5 pre-release scan | ✓ closed (FAIL → remediation → PASS, all 8 checks green) |
| **T6 open data bundle build** | **next, blocked on M7 partial** |
| T7 HuggingFace dataset + card | blocked on T6 |
| T9 Cloudflare custom-domain production | blocked on M5 + M6 |
| T10 methodology placeholder | unblocked |
| **T11 / M11 repo go-public** | gated by T5 scan green ≤24h old (now runs *before* T8 — see order amendment above) |
| T8 Zenodo DOI minting | gated by T6 + M11 public flip (Zenodo needs public repo) |

---

## Your todo list for tomorrow

The pre-release scan landed all-green today. The remaining work is **mostly operational** — you setting up external services. The Coder tasks (T6, T7, T8, T9, T10, T11) are quick once your operational actions complete.

### Block 1 — Set up external services (do these first, in any order)

These unblock multiple downstream Coder tasks. Estimated total time: **60–90 minutes**.

#### M1 — Cloudflare Email Routing for `security@cogstructurelab.com`

**Why:** Phase 8 T2 set `security@cogstructurelab.com` as the security contact in `SECURITY.md`, but the email forwarding doesn't actually work until you configure it.

**Steps:**
1. Open Cloudflare dashboard → `cogstructurelab.com` → Email → Email Routing.
2. Enable Email Routing if not already (free; will add DNS MX + TXT records automatically).
3. Add destination address: your ProtonMail email. Verify it (Cloudflare sends a confirmation link).
4. Add custom address: `security@cogstructurelab.com` → forwards to your ProtonMail.
5. Self-test: send an email from any other account to `security@cogstructurelab.com`. Confirm it arrives in ProtonMail within 60 seconds.

**Done when:** test email arrives.

---

#### M3 — Gmail SMTP app password (for daily digest cron)

**Why:** The Phase 7 social pipeline cron sends a daily digest email at 14:00 UTC. It needs Gmail SMTP credentials.

**Steps:**
1. Go to https://myaccount.google.com/apppasswords (sign in if prompted).
2. Generate a new app password named "LSB daily digest". You'll get a 16-char password.
3. **Save it somewhere durable** (1Password or equivalent — Gmail does not show it again).
4. Add to `.env` on the VPS:
   ```
   LSB_SMTP_USERNAME=your-gmail@gmail.com
   LSB_SMTP_PASSWORD=the-16-char-app-password
   LSB_DIGEST_RECIPIENT=your-email@whatever-domain.com
   ```
5. Self-test from VPS:
   ```
   uv run python -m cdb_social.cli detect --dry-run
   ```
   Should print the (empty) digest to stdout without error.

**Done when:** `--dry-run` exits 0.

---

#### M4 — Bluesky app password (for publishing)

**Why:** Phase 7 admin console publishes to Bluesky via atproto. Needs an app password (NOT your main Bluesky password).

**Steps:**
1. Open https://bsky.app/settings/app-passwords.
2. Generate a new app password named "LSB publisher". You'll get a string like `xxxx-xxxx-xxxx-xxxx`.
3. **Save it somewhere durable.**
4. Add to `.env` on the VPS:
   ```
   LSB_BLUESKY_HANDLE=your-handle.bsky.social
   LSB_BLUESKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
   ```
5. Self-test from VPS:
   ```
   uv run python -m cdb_social.admin_console
   ```
   Console should start on `127.0.0.1:8000`. You don't need to publish anything yet — just confirm the server starts.
6. Ctrl-C to stop.

**Done when:** admin console starts and binds loopback.

---

#### M5 + M6 — Cloudflare deployment + DNS for `cogstructurelab.com`

**Why:** Unblocks T9 (production deployment).

**Reality check on the 2026 Cloudflare dashboard.** The old standalone "Pages" product UI has been fully subsumed into **Workers & Pages**. On this account the only "Create" entry point is **Workers & Pages → Create application**, which produces a *Worker* — there is no longer a separate "Pages" tab in the create flow. Workers now serve static assets natively via an `[assets]` binding in `wrangler.toml`, which is the path we use. The previous version of this section described a Pages-only flow that no longer exists in the UI.

The dashboard already has a Worker named `latent-strucure-benchmark` (note the typo — missing a `t`). We have two options. The repo already contains `apps/dashboard/wrangler.toml` with the correctly-spelled name `latent-structure-benchmark`. **Pick one:**

- **Option A (recommended) — recreate with the correct name.** Cleaner slug, only 2 extra clicks. Delete the typo'd Worker first (Workers & Pages → click the project → Settings → scroll to bottom → Delete). Then proceed with steps 2–6 below.
- **Option B — keep the typo'd Worker.** Edit `apps/dashboard/wrangler.toml` and change `name = "latent-structure-benchmark"` to `name = "latent-strucure-benchmark"` (match the typo). Skip step 2; jump to step 3.

**Steps:**

1. *(If you picked Option A and haven't deleted the typo'd Worker yet)* Delete it now.

2. **Create the Worker via Git integration.**
   - Workers & Pages → **Create application** (blue button, top-right).
   - On the create screen → **Import a repository** (Git) → authorize GitHub if not already → pick your `lsb-agent` repo.
   - Project name will auto-fill from `wrangler.toml` once the build config is set. If prompted manually, enter `latent-structure-benchmark`.
   - Production branch: `master`.
   - Click **Save and Deploy** (or "Continue"). The first build will likely succeed because `wrangler.toml` declares the assets directory.

3. **Set the build configuration.** On the project page → **Settings** → **Build** → **Edit** (or, in your current screenshot, the right-side "Build configuration" panel). Fill in:
   - **Build command:** `npm install && npm run build`
   - **Deploy command:** `npx wrangler deploy` *(this is the default; leave it)*
   - **Non-production branch deploy command:** `npx wrangler versions upload` *(default; leave it)*
   - **Build watch paths:** leave blank
   - **Path:** `apps/dashboard` *(this is the equivalent of the old "Root directory" — it tells Cloudflare which subdirectory of the repo to `cd` into before running the build/deploy commands. Critical: without this, the runner stays at repo root, finds no `package.json`, and fails with `ENOENT`.)*
   - **Environment variables → Production:** add `NODE_VERSION` = `20`.

4. **Trigger a fresh deployment.** On the Deployments tab → **Retry deployment** on the latest failed one, or push any commit to `master`. The build log should now show `npm run build` succeeding inside `/opt/buildhome/repo/apps/dashboard/` and `wrangler deploy` uploading the `dist/` directory as static assets.

5. **Custom domains.** Once a deployment is green, in the project → **Custom domains** tab → **Set up a domain** → add `cogstructurelab.com`. Repeat for `www.cogstructurelab.com` if you want both. Cloudflare auto-adds the DNS records (assuming the `cogstructurelab.com` zone lives in the same Cloudflare account). Wait 1–5 min for the SSL cert to provision; the row will flip to "Active".

6. **`cogstructurelab.ai` (secondary domain → 301 to `.com`).** Open the `cogstructurelab.ai` zone (sidebar → **Domains** → `cogstructurelab.ai`) → **Rules** → **Redirect Rules** → **Create rule**:
   - Name: `ai-to-com-redirect`
   - When incoming requests match: **Custom filter expression** → `(http.host eq "cogstructurelab.ai") or (http.host eq "www.cogstructurelab.ai")`
   - Then: **Dynamic** redirect.
     - Expression: `concat("https://cogstructurelab.com", http.request.uri.path)`
     - Status code: `301`
     - Preserve query string: ON
   - Deploy.

7. **Verify from your terminal:**
   - `curl -I https://cogstructurelab.com/` → `HTTP/2 200` with HSTS / CSP headers.
   - `curl -I https://cogstructurelab.ai/some/path` → `HTTP/2 301` with `location: https://cogstructurelab.com/some/path`.

**Done when:** Both URLs respond correctly per the curl test, and the deployments tab shows at least one green production build.

---

#### M7 prep — HuggingFace dataset slug reservation

**Why:** T7 will push the LSB bundle to HuggingFace Datasets under your `AILLM1999` account.

**Steps:**
1. Open https://huggingface.co/datasets → New dataset.
2. Owner: `AILLM1999`. Name: `latent-structure-benchmark` (or whatever you prefer; this will be the slug).
3. License: `cc-by-4.0`.
4. Private during setup; flip to public at T11.
5. Save the slug for use in T7.

**Done when:** Dataset slug exists (private placeholder is fine).

---

#### M8 prep — Zenodo account (account-only setup; GitHub link happens *after* the public flip)

**Why:** T8 mints the v1.0.0 DOI via Zenodo's GitHub integration. Zenodo's OAuth scope is `public_repo`, so the repo must be public before it appears in the linked-accounts list.

**Steps now (pre-flip):**
1. Sign up at https://zenodo.org if you don't have an account.
2. *(Do NOT link GitHub yet — wait until after the public flip at M11. If you link now, the repo won't appear, and you'll just have to re-link later.)*

**Done when:** Zenodo account exists.

**Steps after the public flip (M11):** see the post-flip section below.

---

### Block 2 — Coder tasks to dispatch (after Block 1 is done)

Once you've done the Block 1 actions, the Coder tasks below can be dispatched. They're mostly short. Tell me which to dispatch when you're back.

#### T6 — Open data bundle build + B2 upload (~1–2 Coder hours + 15 min Mark)

What it does: builds `data/open_bundle/lsb_open_bundle_v1.tar.gz` from the canonical `data/raw/informants.jsonl`, uploads to Backblaze B2 (you'd run the B2 upload command at the end since I don't have B2 credentials), produces the bundle README. CDA SME gate on the bundle README.

**Dispatch trigger:** just say "dispatch T6".

#### T7 — HuggingFace dataset release + dataset card (~1–2 Coder hours + 30 min Mark)

What it does: writes the dataset card at `data/open_bundle/huggingface_dataset_card.md` (CDA SME-gated, full §1.5 framing review). You then push the bundle + card to the HuggingFace dataset slug from M7.

**Dispatch trigger:** "dispatch T7" (after T6 closed).

#### T8 — Zenodo DOI minting (~30 min Coder + 30 min Mark) — **runs AFTER M11 public flip**

What it does: prepares the Zenodo metadata blurb (CDA SME-gated). You then complete the post-flip Zenodo flow:
1. Zenodo → Settings → **Linked accounts** → **GitHub** → connect your GitHub account (now that the repo is public, Zenodo can see it).
2. Zenodo's GitHub page now lists `Mark1999/latent-structure-benchmark` → flip the integration toggle **ON** for this repo.
3. On the VPS (or anywhere with `git` access to the repo):
   ```
   git tag v1.0.0
   git push origin v1.0.0
   ```
4. Zenodo auto-archives within 5–10 minutes; DOI appears in your Zenodo dashboard.
5. The Coder follow-up commits the resulting DOI into the README badge + HF dataset card + bundle README (replacing the `<TBD-T8>` placeholder).

**Dispatch trigger:** "dispatch T8" (after T6 closed AND after M11 public flip AND after you've linked GitHub in Zenodo settings).

#### T9 — Cloudflare Pages production deployment verification (~30 min total)

What it does: I curl-verify the headers post-deployment, document the deployment state, and confirm `_headers` CSP is being served end-to-end. Mostly Mark-action (M5 + M6 above).

**Dispatch trigger:** "dispatch T9" (after M5 + M6 done).

#### T10 — Methodology page placeholder (~30 min Coder)

What it does: ships a placeholder page at `cogstructurelab.com/methodology` saying "Methodology — in preparation" with a link back to `ARCHITECTURE.md §1.5`. Unblocks the README's methodology link.

**Dispatch trigger:** "dispatch T10".

#### T11 — Repo go-public (the flip) — operational, with checklist

The runbook is already at `docs/status/2026-05-17-phase8-github-settings.md`. The actual flip is **your** action via the GitHub UI. The sequence:

1. **24-hour pre-flip:** re-run the pre-release scan:
   ```
   uv run python scripts/prerelease_scan.py --report docs/status/2026-05-XX-phase8-prerelease-scan.md
   ```
   Must exit 0 with "Overall: PASS". If FAIL, remediate before flipping.

2. **GitHub Settings → General:**
   - Description (paste from runbook §A — 340 chars):
     > Latent Structure Benchmark — applies Cultural Domain Analysis elicitation protocols to large language models as if they were informants. Surfaces the corpus lens — how a model organizes everyday vocabulary, refracted through training and alignment. Open data, reproducible, model-to-model.
   - Topics (paste 18 from runbook §A): `llm-benchmark`, `cultural-domain-analysis`, `cda`, `large-language-models`, `model-comparison`, `free-list`, `pile-sort`, `multidimensional-scaling`, `mds`, `cognitive-anthropology`, `open-data`, `reproducible-research`, `corpus-analysis`, `salience-analysis`, `consensus-analysis`, `bootstrap`, `informant-elicitation`, `cogstructurelab`.
   - Website: `https://cogstructurelab.com`.
   - Features: Issues ON; Discussions OFF; Wiki OFF; Projects OFF.

3. **GitHub Settings → Branches → Add rule:**
   - Pattern: `master`
   - Require PR before merging: YES
   - Required status checks: `pytest`, `ruff`, `mypy`, `cdb-social-boundary`, `no-spend-gate-check`
   - Restrict who can push: YES, with `Mark1999` on the allow list
   - Do not allow bypassing: NO

4. **GitHub Settings → Secrets and variables → Actions** (add the Phase 7 secrets):
   - `LSB_SMTP_USERNAME` = your Gmail address
   - `LSB_SMTP_PASSWORD` = the app password from M3
   - `LSB_DIGEST_RECIPIENT` = your email

5. **GitHub Settings → General → Danger Zone → Change repository visibility → Public.** Type the repo name to confirm.

6. **Verify immediately after flip:**
   - Public URL works: `https://github.com/Mark1999/latent-structure-benchmark`
   - LICENSE badge renders (Apache 2.0 in sidebar)
   - SECURITY.md surfaces under the "Security" tab
   - README renders correctly
   - First scheduled cron at 14:00 UTC tomorrow runs successfully

**Dispatch trigger after the flip:** "T11 done, what's next" — I'll close Phase 8.

---

### Block 3 — Post-flip operational items

#### M13 — First manual post (~30 min)

Per kickoff §5 Decision 8 (a), draft a hand-written launch-day post via the admin console:

```
ssh -L 8000:127.0.0.1:8000 lsb-agent-02   # or whatever your VPS hostname is
# Then on the VPS:
uv run python -m cdb_social.admin_console
```

Open `http://localhost:8000` in your browser (the SSH tunnel forwards the loopback bind to your local browser). Click through:
1. Triggers → find a trigger from the digest (or wait for one) → click "Draft via LLM"
2. Review the draft → "Approve"
3. "Publish" (the second click) → confirmation page → "Yes, publish to Bluesky"

If you want a pure launch-day post (not tied to a detector trigger), the cleanest path is to manually draft text + post directly to Bluesky outside the LSB pipeline. The pipeline is for organic detector-triggered posts.

---

## Summary of operational checklist

| # | Action | Time | Blocks |
|---|---|---|---|
| **M1** | Cloudflare Email Routing for security@ | 15–30 min | T2 acceptance complete |
| **M3** | Gmail SMTP app password + .env | 10 min | Phase 7 cron working |
| **M4** | Bluesky app password + .env | 10 min | M13 first post |
| **M5+M6** | Cloudflare custom domain + DNS | 30–60 min | T9, M11 |
| **M7 prep** | Reserve HuggingFace dataset slug | 5–10 min | T7 |
| **M8 prep (pre-flip part)** | Create Zenodo account (don't link GitHub yet) | 5 min | T8 |
| **24h before flip** | Re-run pre-release scan, must PASS | 5 min | M11 |
| **M10 + M11 + M12** | GitHub settings + branch protection + public flip | 15–30 min | T8 (Zenodo can now see repo) |
| **M8 (post-flip)** | Link GitHub in Zenodo → repo now appears → toggle ON | 5 min | T8 dispatch |
| **T8 + M9** | Dispatch T8 → tag v1.0.0 → Zenodo auto-archives DOI | 30 min | Phase 8 closure |
| **M13** | First social post (Bluesky launch announcement) | 30 min | Phase 8 deliverable |

**Recommended sequence (Path A, reordered 2026-05-18):** Block 1 in parallel (M1 + M3 + M4 + M5/M6 + M7 prep + Zenodo signup only). Then "dispatch T6" → T7 → T9 → T10 → re-run pre-release scan → **M10 + M11 + M12 public flip** → link Zenodo to GitHub → "dispatch T8" → tag v1.0.0 → DOI mints → M13 first social post.

---

## Reference docs to read at pickup

- **This file** — your starting point
- `docs/status/2026-05-17-phase8-architect-kickoff.md` — the full Phase 8 plan + ratified decisions + Mark-action enumeration
- `docs/status/2026-05-17-phase8-github-settings.md` — operational runbook for the GitHub flip
- `docs/status/2026-05-17-phase8-prerelease-scan.md` — current scan state (all 8 PASS at handoff)

---

## Quick sanity checks at pickup

```
# Verify GitHub sync
git status
git log --oneline @{u}..HEAD  # should be empty (or however many new commits you've made)

# Verify tests still pass
uv run pytest --tb=no -q
uv run ruff check .
uv run mypy packages/

# Verify pre-release scan still PASSes (if more than 24h old, re-run it)
uv run python scripts/prerelease_scan.py --report /tmp/scan-pickup-check.md
echo "Exit: $?"

# Verify Phase 7 social pipeline detect mode (should produce empty digest gracefully)
uv run python -m cdb_social.cli detect --dry-run
```

---

## What to message me when you pick up

Either:
- "dispatch T6" (most likely starting point if Block 1 done)
- "dispatch T10" (if you want methodology placeholder first; T10 is independent)
- "skip to T11" (if you want to flip the repo public without ever running T6-T10 — minimal launch, dataset and DOI follow as Phase 8.5)
- Any override on the §5 decisions if you've changed your mind

---

*End of handoff. See you tomorrow.*
