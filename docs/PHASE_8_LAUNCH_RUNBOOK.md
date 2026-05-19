# Phase 8 — Final Launch Runbook (Mark-side actions)

**Document name:** `docs/PHASE_8_LAUNCH_RUNBOOK.md`
**Author:** Mark (with Claude orchestrator assistance)
**Date created:** 2026-05-19
**Status:** active — all Block-1 operational items closed; Block-2 Coder tasks (T6, T7, T9, T10, T14) closed; ready to execute this runbook.

> **What this is.** A single ordered list of things only you can do between now and M13 (the first Bluesky launch post). Each step has the exact command or UI path, the expected outcome, what to tell Claude when it's done, and a troubleshooting note. Read in order — the steps form a dependency chain.
>
> **Why ordered:** several steps gate on each other. Zenodo cannot see the repo until it's public (Path A reorder, 2026-05-18). B2 cannot be flipped public until the HF card is uploaded so the download URLs land in the right place. The DOI cannot be minted until the repo is public AND tagged. Order matters.
>
> **Estimated total time:** 60–90 minutes hands-on, spread across a few sessions if you want. The DOI mint at the end takes 5–10 minutes of Zenodo-side wall clock on top of that.

---

## Where you are right now (2026-05-19)

| Phase 8 milestone | State |
|---|---|
| M1 Email Routing | ✅ done |
| M3 Gmail App Password | ✅ done |
| M4 Bluesky app password | ✅ done |
| M5 Cloudflare Worker + custom domain | ✅ done — apex + www both HTTP 200 with full security headers |
| M6 DNS | ✅ done |
| M7 HF slug reservation | ✅ done |
| M8 Zenodo signup (no GitHub link yet) | ✅ done |
| T6 open data bundle | ✅ done — tarball staged at B2 (private), bundle README + DD §14 + build script committed |
| T7 HF dataset card | ✅ committed; **HF push pending (Block A below)** |
| T9 production deploy verification | ✅ PASS |
| T10 methodology placeholder route | ✅ shipped in code; **dashboard deploy verification pending (Block A below)** |
| T14 ARCHITECTURE.md §6.6 alignment | ✅ done |
| **M11 public flip** | ⏳ **this runbook** |
| **M12 dashboard public** | ⏳ **this runbook** |
| **T8 Zenodo DOI mint** | ⏳ **this runbook** (after M11) |
| **M13 first Bluesky post** | ⏳ **this runbook** (last step) |

---

## Block A — Pre-flip housekeeping (do these in any order)

These are local-state items that have nothing to do with the public flip. Do them whenever you have 5–15 minutes.

### A.1 — Push the open data bundle to HuggingFace (~15 min)

**Goal:** the HF dataset page exists, contains the tarball and the card, but stays **private** until M11.

**Steps:**

1. Confirm `hf` CLI is installed:
   ```bash
   hf --version
   ```
   If not installed:
   ```bash
   pip install -U huggingface_hub
   ```
   (You already have it via the `hf-cli` Claude Code skill, but the CLI binary may need to be on PATH.)

2. Authenticate as `AILLM1999`:
   ```bash
   hf auth login
   ```
   Paste your HF write token when prompted. Get it from `huggingface.co/settings/tokens` (the "Write" scope is required).

3. Set your reserved slug as a shell variable (substitute the actual slug from M7 if different):
   ```bash
   SLUG=AILLM1999/latent-structure-benchmark
   ```

4. Push the tarball:
   ```bash
   hf upload "$SLUG" /tmp/lsb_bundle_out/lsb_open_bundle_v1.tar.gz \
     lsb_open_bundle_v1.tar.gz --repo-type dataset
   ```
   Takes a few minutes for 1.55 GB.

5. Push the dataset card as `README.md` (HF renders `README.md` at the dataset root as the page card):
   ```bash
   hf upload "$SLUG" /opt/lsb-agent/data/open_bundle/huggingface_dataset_card.md \
     README.md --repo-type dataset
   ```

6. Open `https://huggingface.co/datasets/AILLM1999/latent-structure-benchmark` (substitute your slug) and verify:
   - The card renders with the title "Latent Structure Benchmark (LSB) Open Data Bundle v1"
   - The YAML front matter parsed into the sidebar (you should see the tags and license fields)
   - The tarball appears under the "Files and versions" tab with size ~1.55 GB
   - Visibility is **private** (Settings → Visibility shows Private)

7. Fix the license field in the HF UI if it shows anything other than `cc0-1.0`. M7 prep may have reserved the slug with `cc-by-4.0`; if so, go to Settings → License → change to **CC0 1.0 Universal** and save. (The YAML front matter in the card is already correct; the HF UI license field is a separate setting.)

**Tell Claude when done:** *"HF push complete, slug is `AILLM1999/<name>`"* (paste the actual slug). Claude will note it for T8 and M13 post copy.

**Troubleshooting:**
- *Auth fails* → your token doesn't have Write scope. Generate a new one at `huggingface.co/settings/tokens` with the "Write" preset.
- *Upload aborts mid-stream* → re-run; `hf upload` resumes from the partial.
- *Tarball appears but card doesn't render* → the second `hf upload` must use the literal filename `README.md` as the second argument (not `huggingface_dataset_card.md`). HF renders the dataset card from a file literally named `README.md` at the repo root.

---

### A.2 — Confirm `/methodology` placeholder is live (~3 min)

**Goal:** `https://cogstructurelab.com/methodology` returns the placeholder page.

**Steps:**

1. Visit `https://cogstructurelab.com/methodology` in a browser. You should see:
   - `<h1>Methodology</h1>`
   - One sentence: "This page is in preparation."
   - A link to `ARCHITECTURE.md` on GitHub
   - Same header/footer chrome as the home page

2. If you instead see a 404, a different page, or the home page contents, the Worker has not redeployed since commit `064eca0`. Force a deploy:
   ```bash
   cd /opt/lsb-agent/apps/dashboard
   npm run build
   npx wrangler deploy
   ```
   Wait 30 seconds, refresh.

**Tell Claude when done:** *"methodology page renders"* or *"methodology page is 404"*.

**Troubleshooting:**
- *`wrangler deploy` asks for authentication* → `npx wrangler login` first (opens a browser to your Cloudflare account).
- *Build fails with a TypeScript error* → unusual since tests passed; tell Claude and we'll debug.

---

### A.3 — (Optional) Rotate the exposed B2 application key (~5 min)

**Goal:** the B2 application key that briefly appeared in chat history is replaced with a fresh one.

**Steps:**

1. Open `https://secure.backblaze.com/app_keys.htm`.
2. Click your existing key (the one currently in `.env`).
3. Generate a new application key with the same capabilities (or scoped to `lsb-open-data` only, which is tighter).
4. Copy the new `keyID` and `applicationKey`.
5. Edit `/opt/lsb-agent/.env` and replace both values. Also rename `B2_KEY_ID` → `B2_APPLICATION_KEY_ID` while you're there (the b2 v4 CLI expects the longer name).
6. Delete the old key in the B2 console.
7. Test:
   ```bash
   export B2_APPLICATION_KEY_ID=$(grep ^B2_APPLICATION_KEY_ID /opt/lsb-agent/.env | cut -d= -f2-)
   export B2_APPLICATION_KEY=$(grep ^B2_APPLICATION_KEY /opt/lsb-agent/.env | cut -d= -f2-)
   b2 account authorize "$B2_APPLICATION_KEY_ID" "$B2_APPLICATION_KEY"
   ```
   Expected: clean JSON response.

**Tell Claude when done:** *"B2 key rotated"* — purely informational.

**Skip if:** you'd rather rotate after launch is done. Not a blocker.

---

## Block B — Pre-flip rescan (within 24h of the M11 flip)

### B.1 — Re-run the pre-release scan

**Goal:** the same scan that ran during T5 re-runs and exits PASS.

**Steps:**

```bash
cd /opt/lsb-agent
uv run python scripts/prerelease_scan.py --report docs/status/2026-05-XX-phase8-prerelease-scan.md
```

(Substitute the actual date for `2026-05-XX`.)

**Expected output:** the script exits 0 with "Overall: PASS" on the final line.

**If FAIL:** stop here, tell Claude what failed (paste the FAIL lines). Do not flip the repo public until the rescan is PASS.

**Tell Claude when done:** *"prerelease scan PASS, dated YYYY-MM-DD"*.

---

## Block C — The public flip (M11 + M12)

This is the actual launch moment from GitHub's perspective. Once Step C.5 completes, the repo is publicly visible at `https://github.com/Mark1999/latent-structure-benchmark`.

### C.1 — GitHub Settings → General

Open `https://github.com/Mark1999/latent-structure-benchmark/settings`.

1. **Description** — paste exactly:
   > Latent Structure Benchmark — applies Cultural Domain Analysis elicitation protocols to large language models as if they were informants. Surfaces the corpus lens — how a model organizes everyday vocabulary, refracted through training and alignment. Open data, reproducible, model-to-model.

2. **Website** — set to `https://cogstructurelab.com`

3. **Topics** — paste these 18 (one at a time, comma-separated, no spaces):
   ```
   llm-benchmark, cultural-domain-analysis, cda, large-language-models, model-comparison, free-list, pile-sort, multidimensional-scaling, mds, cognitive-anthropology, open-data, reproducible-research, corpus-analysis, salience-analysis, consensus-analysis, bootstrap, informant-elicitation, cogstructurelab
   ```

4. **Features** section (lower on the same page):
   - Issues: **ON**
   - Discussions: **OFF**
   - Wiki: **OFF**
   - Projects: **OFF**

5. Click **Save** at the bottom of each section that has a save button.

---
### C.2 — Light branch protection (revised for solo personal-repo + direct-to-master)

> **Why revised:** the original C.2 added a "Require PR before merging" rule that conflicts with CLAUDE.md §8 (this project's default workflow is direct-to-master, no PR ceremony). On a solo personal repo, your existing implicit protections (only you can push, CI runs on every push, forks must PR through CI) already cover the threat model. The lightweight ruleset below adds two cheap wins (force-push protection + deletion protection) without breaking §8.
>
> **Skip this section entirely if you prefer.** Going to C.3 with no branch ruleset is defensible.

If you want the lightweight protections:

1. GitHub Settings → **Rules** → **Rulesets** → **New branch ruleset**
2. Name: `master-protections`
3. **Target branches:** include `master`
4. **Bypass list:** add yourself (`Mark1999`) with bypass mode "Always" — so your direct-to-master workflow keeps working
5. **Rules** (check only these):
   - ✅ **Restrict deletions**
   - ✅ **Block force pushes**
   - ✅ **Require status checks to pass** — add: `lint-and-test`, `cdb-social-boundary`, `gitleaks`. Note: these only apply to incoming PRs (you bypass via step 4).
6. **Do NOT** enable "Require a pull request before merging" — would break direct-to-master.
7. **Enforcement status:** Active
8. Click **Create**.


---

### C.3 — GitHub Settings → Secrets and variables → Actions

Add these three repository secrets:

| Name | Value |
|---|---|
| `LSB_SMTP_USERNAME` | your Gmail address |
| `LSB_SMTP_PASSWORD` | the App Password from M3 |
| `LSB_DIGEST_RECIPIENT` | your email (same as username for now) |

For each: New repository secret → name → value → Add secret.

---

### C.4 — Final pre-flip sanity check

Before pulling the trigger, eyeball the repo from a logged-out browser tab (incognito works). You'll only see the dashboard tab, but confirm:
- `https://cogstructurelab.com/` loads
- `https://cogstructurelab.com/methodology` loads (the placeholder)
- The Cloudflare Worker URL `https://latent-structure-benchmark.markdd2.workers.dev` still loads (backup)

---

### C.5 — Flip the repo to Public

Open `https://github.com/Mark1999/latent-structure-benchmark/settings`. Scroll to the bottom — **Danger Zone**.

1. Click **Change repository visibility**.
2. Choose **Make public**.
3. Type the repo name (`latent-structure-benchmark`) to confirm.
4. Click **I understand, change repository visibility**.

**The repo is now public. ⚠️ This is irreversible in practice — anyone who clones in the next minute keeps a copy forever.**

### C.6 — Immediate post-flip verification (within 60 seconds)

From an incognito tab:

1. `https://github.com/Mark1999/latent-structure-benchmark` — should load.
2. README renders correctly on the repo page.
3. LICENSE badge appears in the right sidebar (Apache 2.0).
4. SECURITY.md appears under the "Security" tab.
5. The 18 topics appear under the description.

**Tell Claude when done:** *"M11 flip complete, repo is public"*. Claude will then guide you through the rest.

**If anything looks wrong:** tell Claude immediately. The repo can technically be flipped private again, but anyone who cloned in the first 60s already has the data — investigate quickly.

---

## Block D — Open the data surfaces

### D.1 — Flip the B2 bucket to public (~2 min)

The tarball has been sitting in a private B2 bucket. Now make it downloadable.

```bash
b2 bucket update lsb-open-data allPublic
```

Verify with a curl from outside the VPS, or from the VPS itself:

```bash
curl -I https://f005.backblazeb2.com/file/lsb-open-data/lsb_open_bundle_v1.tar.gz
```

Expected: `HTTP/1.1 200 OK` with `content-length: 1550226039`.

**Tell Claude when done:** *"B2 bucket public, tarball curlable"*.

---

### D.2 — Flip the HuggingFace dataset to public (~2 min)

In the HF UI:

1. Open `https://huggingface.co/datasets/AILLM1999/latent-structure-benchmark` (your slug).
2. Settings tab → **Visibility** section → **Public**.
3. Confirm.

The dataset is now discoverable via HF search.

**Tell Claude when done:** *"HF dataset public"*.

---

## Block E — Zenodo + DOI minting (T8)

### E.1 — Link Zenodo to GitHub (~5 min)

Now that the repo is public, Zenodo can see it.

1. Open `https://zenodo.org/account/settings/github/`.
2. Click **Connect** under GitHub if not already connected.
3. Authorize Zenodo to read your public repos.
4. The page now lists `Mark1999/latent-structure-benchmark`. Flip the toggle to **On**.

**Tell Claude when done:** *"Zenodo linked, toggle is on"*.

---

### E.2 — Tag v1.0.0 to trigger the DOI mint

This is the actual DOI-minting event. Zenodo watches GitHub releases on linked repos and archives a snapshot when a tag is pushed.

```bash
cd /opt/lsb-agent
git tag v1.0.0
git push origin v1.0.0
```

Within 5–10 minutes, Zenodo archives the tag and mints a DOI.

### E.3 — Get the DOI

1. Open `https://zenodo.org/account/settings/github/` again.
2. Click the **Latent Structure Benchmark** repo entry.
3. The page shows the new release with a DOI badge.
4. Copy the DOI (looks like `10.5281/zenodo.XXXXXXX`).

**Tell Claude when done:** *"v1.0.0 tag pushed, DOI is 10.5281/zenodo.XXXXXXX"*. Claude dispatches the Coder for the T8 follow-up:

- Replace `<TBD-T8-DOI>` placeholder in `data/open_bundle/huggingface_dataset_card.md`
- Re-push the card to HF: `hf upload "$SLUG" data/open_bundle/huggingface_dataset_card.md README.md --repo-type dataset`
- Replace `<TBD-T8-DOI>` placeholder in `data/open_bundle/README.md` (in tarball)
- Optionally rebuild + reupload the tarball with the updated README (~5 min)
- Commit the README badge update on master

---

## Block F — Launch (M13)

### F.1 — Draft + publish the first Bluesky post (~30 min)

Per Phase 7 kickoff §5 Decision 8, M13 is a **hand-written** launch post — not drafter-generated. Draft it manually.

**Steps:**

1. Start the admin console:
   ```bash
   cd /opt/lsb-agent
   uv run python -m cdb_social.admin_console
   ```
   It binds to `http://localhost:8050` (or whatever the config says).

2. Open the admin console in a browser. Navigate to the manual-post composer.

3. Write the launch post (under Bluesky's 300-char limit). A suggested shape:
   > Launching the Latent Structure Benchmark — a public, reproducible benchmark that applies Cultural Domain Analysis to LLMs as if they were informants. Open data, model-to-model, CC0. cogstructurelab.com
   >
   > Methodology: <link>
   > Dataset: huggingface.co/datasets/AILLM1999/...
   > DOI: doi.org/10.5281/zenodo.XXXXXXX

4. Save as draft. Review against §1.5 framing. No "worldview", no "believes", no leaderboard framing.

5. Click **Stage** (first click).

6. Click **Publish** (second click) — this is the two-click human-in-loop requirement per Phase 7 §11.1 B-2.

7. Verify the post appears on `https://bsky.app/profile/lsb.cogstructurelab.com` (or whatever your actual handle is).

**Tell Claude when done:** *"M13 post published, link to it: <URL>"*. **This is the launch moment.** 🚀

---

## Block G — Long-tail follow-ups (post-launch, no urgency)

These are tracked tasks that can wait days or weeks. Listed here so you don't lose them.

| Item | Why | When |
|---|---|---|
| Node.js 20 → 24 GitHub Actions upgrade | Forced by 2026-06-02, removed 2026-09-16. `actions/checkout@v4`, `astral-sh/setup-uv@v5`, `gitleaks/gitleaks-action@v2`. | Before 2026-09-16 |
| Skip-to-content link site-wide | Pre-existing a11y gap; flagged by UI/UX during T10. Not introduced by T10. | When you want |
| Methodology page content (real, not placeholder) | T10 shipped the placeholder; the real methodology page is a Phase 9 task. | Phase 9 |
| Optional: `data/grounding/` historical-banner readability pass | After §1.5.5 amendment, the directory has a banner but the README inside individual subdirs may still reference baseline framing. Check + fix where needed. | When you want |
| Optional: BACKUP cadence verification | Confirm Backblaze backup cron is running per HOSTING_AND_DEV_OPS.md §7.2 | Within first week post-launch |

---

## Quick reference — "what should I tell Claude after each block?"

| Block done | Message to Claude |
|---|---|
| A.1 HF push | "HF push complete, slug is `AILLM1999/<name>`" |
| A.2 methodology page | "methodology page renders" or "methodology page is 404" |
| A.3 B2 key rotation (optional) | "B2 key rotated" |
| B.1 pre-release scan | "prerelease scan PASS, dated YYYY-MM-DD" |
| C M11 flip | "M11 flip complete, repo is public" |
| D.1 B2 public | "B2 bucket public, tarball curlable" |
| D.2 HF public | "HF dataset public" |
| E.1 Zenodo linked | "Zenodo linked, toggle is on" |
| E.2 + E.3 DOI | "v1.0.0 tag pushed, DOI is 10.5281/zenodo.XXXXXXX" |
| F.1 Launch post | "M13 post published, link: <URL>" |

After E.3 (DOI in hand), Claude dispatches the Coder for the T8 follow-up commit (README + HF card DOI substitution). That happens autonomously — no further action on your part until F.

---

*End of `PHASE_8_LAUNCH_RUNBOOK.md`. Read top-to-bottom in order. Skip Block A.3 if you don't want to rotate the B2 key. Everything else is mandatory.*
