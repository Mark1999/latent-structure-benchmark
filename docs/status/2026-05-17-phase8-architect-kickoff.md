# Phase 8 Architect Kickoff — Public Release

**Status:** Draft for Mark's review. Pre-CDA-SME, pre-Coder.
**Date:** 2026-05-17
**Architect:** Opus
**Companion specs:** ARCHITECTURE.md §5.3 (Phase 8), §6.6 (licensing), §6.7 (open bundle), §1.5 (framing), SECURITY_AND_HARDENING.md §6.5 + §9, HOSTING_AND_DEV_OPS.md §2 (Cloudflare Pages), §4 (B2), §7 (open data), CLAUDE.md §6/§7/§9.
**Phase 8 spec source:** ARCHITECTURE.md §5.3 lines 1483–1490.
**Inherits from:** Phase 6 closure 2026-05-16 (10/14 tasks landed; T1+T2 methodology + T3+T4 DriftTracker blocked) and Phase 7 closure 2026-05-17 (social pipeline live with strict human-in-the-loop architecture per §11.1 B-1/B-2).
**Master commit at kickoff:** `62fffcb`. Test floor: 1791 pytest pass; ruff + mypy clean; working tree clean.

---

## §1 Goal

Phase 8 is the **final phase of the original phase plan**. Success condition: the GitHub repo is public, the dashboard is live at `https://cogstructurelab.com` via Cloudflare Pages production deployment, the open data bundle is on HuggingFace Datasets and on Zenodo with a DOI, the licensing/security/disclosure posture is publicly correct, and the project is in a state where an unannounced researcher arriving cold can read the methodology page, click through the dashboard, download the bundle, and reproduce a figure. Nothing in this phase invents new methodology or new components; this phase ratifies, packages, scans, and releases what Phases 0–7 already built.

A non-goal worth naming up front: Phase 8 does not promise polish. The FT designer's dashboard polish work is a parallel track. Phase 8 ships the project as it stands.

---

## §2 Out of scope

Each of the following is **not** in Phase 8 and is excluded by name to keep the Coder from scope-drift.

1. **FT designer dashboard polish work.** A parallel track started 2026-05-17 with `docs/FRONTEND_DESIGNER_BRIEF.md` v0.2 (CDA-SME-approved). The FT designer's restyling does not gate Phase 8 and Phase 8 does not gate the FT designer's restyling.
2. **Phase 6 T3 + T4 DriftTracker.** Still data-blocked (one collection date per `model_version_returned` in the 0.2 corpus). Ships when multi-date data exists, i.e. Phase 9+.
3. **Additional collection campaigns.** No new corpus runs in Phase 8. The open bundle published in Phase 8 is the 0.2 snapshot.
4. **Additional domains beyond family / holidays / food.** Three domains constitute v1.
5. **Any autonomous social posting.** Per Phase 7 §11.1 B-1 (binding), the system never autonomously drafts or publishes. The Phase 8 "first batch of social posts" §5.3 deliverable is operational, not code: Mark generates each post via the admin console manually.
6. **Branch protection rule rework that breaks Mark's direct-to-master workflow** per CLAUDE.md §8. Phase 8 must respect Mark's established workflow; see §5 decision 5.
7. **Re-introducing human grounding to the dashboard.** The 2026-05-07 amendment is binding; all v1 domains are model-to-model.
8. **`apps/ops_dashboard/` (Streamlit) and the loopback admin console.** Both are internal-only surfaces. They stay on `127.0.0.1`; nothing in Phase 8 exposes them.

---

## §3 Decomposition into Coder-sized tasks

Eleven tasks. Each is sized to fit in 1–3 Coder hours per Mark's "tasks run in hours" memory and his "this is going long" feedback.

### T1 — License-coverage audit + repo root verification

**One-line goal:** Verify the four license files at repo root match `ARCHITECTURE.md` §6.6 byte-for-byte coverage, audit which files in the repo fall under which license, and add an inline `NOTICE` file at repo root if Apache 2.0 requires one.

**Scope:** ~50 LoC of doc + audit script; no schema or code changes.

**Files touched:** `NOTICE` (new, optional), `docs/LICENSE_COVERAGE.md` (new), README.md (verify only).

**Dependencies:** none.

**Gates:** Architect sign-off. No CDA SME. No UI/UX.

**Acceptance:** Four license files exist + match §6.6; `LICENSE_COVERAGE.md` enumerates path→license mapping; NOTICE determination documented.

**Blocks repo-go-public?** Yes.

---

### T2 — `SECURITY.md` contact decision + finalization

**One-line goal:** Ratify the security contact email decision (§5 decision 4) and update `SECURITY.md` + `SECURITY_AND_HARDENING.md` §6.5 to match.

**Scope:** ~10 LoC across two files.

**Files touched:** `SECURITY.md`, `SECURITY_AND_HARDENING.md` §6.5, `HOSTING_AND_DEV_OPS.md` §9.

**Dependencies:** Mark's §5 decision 4 (ProtonMail vs. domain-forwarded alias).

**Gates:** Architect sign-off. No CDA SME. No UI/UX.

**Acceptance:** `SECURITY.md` contact email matches `SECURITY_AND_HARDENING.md` §6.5; the chosen address actually receives mail (Mark verifies).

**Blocks repo-go-public?** Yes.

---

### T3 — README.md public-readiness pass

**One-line goal:** Tighten `README.md` for a cold-reader public audience: §1.5 framing-correct opening paragraphs, one-paragraph quickstart, valid links, clear data-license summary, removal of pre-launch internal language.

**Scope:** ~100 LoC of prose changes.

**Files touched:** `README.md`.

**Dependencies:** §5 decision 1 (methodology page strategy — affects whether README links to `/methodology` or omits).

**Gates:** **CDA SME required** — README §1.5 framing is the most public-facing surface. No UI/UX.

**Acceptance:** §1.5-compliant pitch; quickstart works end-to-end; all cross-doc links resolve; forbidden-vocab grep clean.

**Blocks repo-go-public?** Yes.

---

### T4 — GitHub repository description + topics + repository-settings draft

**One-line goal:** Produce a Mark-approvable draft of the GitHub repo description (≤350 chars), the topics list (up to 20), and a one-page checklist of GitHub settings Mark configures at go-public time.

**Scope:** ~40 LoC of doc.

**Files touched:** `docs/status/2026-05-17-phase8-github-settings.md` (new).

**Dependencies:** §5 decision 5 (branch protection), §5 decision 7 (social handles).

**Gates:** **CDA SME required.** No UI/UX.

**Acceptance:** Description passes §1.5 framing; topics list clean; checklist enumerates every GitHub UI step.

**Blocks repo-go-public?** Yes.

---

### T5 — Pre-release scan implementation

**One-line goal:** Implement (and run) the pre-public-release scan specified in §6. Produces a single pass/fail report.

**Scope:** ~200 LoC across one orchestration script + several small grep scripts; one report file.

**Files touched:** `scripts/prerelease_scan.py` (new), `docs/status/2026-05-17-phase8-prerelease-scan.md` (new).

**Dependencies:** T1, T2, T3, T4 must be merged first.

**Gates:** Architect sign-off on scan spec. No CDA SME. No UI/UX.

**Acceptance:** Scan exits 0 only if every §6 check passes. Re-runnable; go-public conditioned on a green scan <24 hours old.

**Blocks repo-go-public?** **This is the gate.**

---

### T6 — Open data bundle build + B2 upload

**One-line goal:** Build `data/open_bundle/lsb_open_bundle_v1.tar.gz` from `data/raw/informants.jsonl`, upload to Backblaze B2 bucket `lsb-open-data`, verify researcher-rebuild byte-reproducibility.

**Scope:** ~150 LoC of build orchestration + verification + bundle README.

**Files touched:** `scripts/build_open_bundle.py` (new), `data/open_bundle/README.md` (new).

**Dependencies:** §5 decision 2 (timing).

**Gates:** **CDA SME required** — bundle README is public-facing §1.5-bound text. No UI/UX.

**Acceptance:** Bundle builds reproducibly; researcher-rebuild test passes; B2 URL works.

**Blocks repo-go-public?** No if §5 decision 2 chooses (b); yes if (a).

---

### T7 — HuggingFace Datasets release + dataset card

**One-line goal:** Push the v1 bundle to HuggingFace Datasets under `AILLM1999` with a complete §1.5-bound dataset card.

**Scope:** ~120 LoC dataset config + ~200 LoC dataset card prose.

**Files touched:** `data/open_bundle/huggingface_dataset_card.md` (new) — source of truth mirrored to HF.

**Dependencies:** T6.

**Gates:** **CDA SME required** — card is binding §1.5 text indexed by ML researchers. No UI/UX.

**Acceptance:** Dataset card passes CDA SME four-axis review; HF page renders; bundle file downloadable.

**Blocks repo-go-public?** No if §5 decision 2 chooses (b); yes if (a).

---

### T8 — Zenodo DOI minting

**One-line goal:** Upload the v1 bundle to Zenodo, mint the v1.0.0 DOI, propagate the DOI back into README + methodology + HF dataset card.

**Scope:** Mark-action heavy. ~30 LoC of doc updates post-mint.

**Files touched:** `README.md`, `data/open_bundle/README.md`, `data/open_bundle/huggingface_dataset_card.md`, `docs/status/2026-05-17-phase8-zenodo-release.md` (new).

**Dependencies:** T6, §5 decision 3.

**Gates:** CDA SME on Zenodo metadata description. No UI/UX.

**Acceptance:** Bundle uploaded; DOI minted and resolves; cross-references updated.

**Blocks repo-go-public?** No (can be added same-day post-launch).

---

### T9 — Cloudflare Pages production deployment + DNS

**One-line goal:** Promote Cloudflare Pages from preview-only to production, attach `cogstructurelab.com` per HOSTING_AND_DEV_OPS.md §2.5, verify HTTPS + CSP end-to-end.

**Scope:** Mark-action heavy. ~20 LoC of doc update.

**Files touched:** `docs/status/2026-05-17-phase8-cloudflare-deploy.md` (new).

**Dependencies:** T3 (README links). Mark-actions M5 + M6.

**Gates:** No CDA SME. **UI/UX recommended** (preview-vs-production spot check). Reviewer R3 (CSP).

**Acceptance:** `https://cogstructurelab.com/` returns 200; `.ai` 301-redirects; CSP/HSTS/Referrer-Policy headers present.

**Blocks repo-go-public?** No (independent), but recommended order: dashboard live → repo public.

---

### T10 — Methodology page resolution

**One-line goal:** Resolve Phase 6 T1+T2 blockage per §5 decision 1. Three paths land different sub-tasks: (a) Mark prose now; (b) placeholder page; (c) defer to FT designer.

**Scope:** Variable (30 min – 3 Coder hours depending on path).

**Files touched:** Variable.

**Dependencies:** §5 decision 1.

**Gates:** **CDA SME required** (any path). **UI/UX required for (a) and (b)** (public dashboard surface).

**Acceptance:** Whatever success looks like under chosen path.

**Blocks repo-go-public?** No, but README must be consistent with chosen path.

---

### T11 — Repository go-public + first-publish operational checklist

**One-line goal:** Mark flips the repo public per the T4 checklist. Operational task with code touch only if follow-up fix needed.

**Scope:** Mostly Mark-checklist. ~30 LoC doc.

**Files touched:** `docs/status/2026-05-17-phase8-go-public.md` (new).

**Dependencies:** T1–T9 complete (T10 path-dependent). **Pre-release scan (T5) green <24 hours.**

**Gates:** Architect sign-off on readiness checklist. No CDA SME. No UI/UX.

**Acceptance:** Repo publicly visible; branch protection per §5 decision 5; `social-pipeline.yml` cron runs successfully post-flip.

**Blocks repo-go-public?** This **is** repo-go-public.

---

## §4 Mark-action dependencies

| # | Mark-action | Approximate work | Gates which task |
|---|---|---|---|
| M1 | Decide ProtonMail-direct vs. `security@cogstructurelab.com` forwarding alias; configure; self-test | 15–30 min | T2 |
| M2 | Configure GitHub Actions secrets (LSB_SMTP_*, LSB_BLUESKY_*) | 15 min | T11 |
| M3 | Generate Gmail SMTP app password | 10 min | T11 |
| M4 | Generate Bluesky app password | 10 min | T11 (operational) |
| M5 | Configure Cloudflare Pages production: custom domain, `.ai` redirect, SSL Full strict, cert | 30–60 min | T9 |
| M6 | Configure DNS for `cogstructurelab.com` + `.ai` | 15 min | T9 |
| M7 | Create HuggingFace dataset repo; upload bundle; publish card | 30–45 min | T7 |
| M8 | Create Zenodo upload; mint v1.0.0 DOI | 30 min | T8 |
| M9 | Tag git release `v1.0.0` | 5 min | T8 |
| M10 | Configure GitHub repo description + topics per T4 draft | 5 min | T11 |
| M11 | Apply branch protection rules per §5 decision 5 | 5 min | T11 |
| M12 | **The flip:** GitHub → Public | 30 seconds + verification | T11 |
| M13 | Mark drafts first social post manually via admin console | 30 min | §5.3 deliverable |

---

## §5 Decision points for Mark

Eight binding decisions with Architect recommendations.

### Decision 1 — Methodology page strategy

- **(a)** Mark writes methodology page now, before launch.
- **(b)** Launch with placeholder "Methodology — coming soon (target: YYYY-MM-DD)".
- **(c)** FT designer takes over methodology page.

**Architect recommendation: (b)** — placeholder. Faster launch; preserves upgrade path to (a) or (c).

### Decision 2 — HuggingFace dataset release timing

- **(a)** Ship with public repo go-live.
- **(b)** Ship later (Phase 8.5).

**Architect recommendation: (a)** — fully-released artifact on launch day.

### Decision 3 — Zenodo DOI timing + git release tag

**Architect recommendation:** Single `v1.0.0` tag; DOI minted at or shortly after go-public. Sequence: tag → Zenodo → README DOI update → go-public.

### Decision 4 — `SECURITY.md` contact address

**Current state:** `SECURITY.md` says `security@cogstructurelab.com`; `SECURITY_AND_HARDENING.md` §6.5 says `security@cogstructurelab.ai`. **Mismatch must be resolved.**

- **(a)** Standalone ProtonMail (e.g., `lsb-security@protonmail.com`).
- **(b)** `security@cogstructurelab.com` with Cloudflare Email Routing forwarding to ProtonMail.
- **(c)** `security@cogstructurelab.ai` with email forwarding.

**Architect recommendation: (b)** — matches primary domain; Cloudflare Email Routing is free; SECURITY_AND_HARDENING.md §6.5 updated to match.

### Decision 5 — Branch protection rules after go-public

- **(a)** None.
- **(b)** Soft: PR required from forks; Mark direct-pushes from his clone.
- **(c)** Full PR requirement.

**Architect recommendation: (b)** — preserves CLAUDE.md §8 direct-to-master workflow; standard for forked-PR contributions.

### Decision 6 — GitHub repository description and topics

**Architect draft (Mark approves or edits):**

- **Description:** "Latent Structure Benchmark — applies Cultural Domain Analysis elicitation protocols to large language models as if the models were informants. Surfaces the corpus lens — how a model organizes everyday vocabulary, refracted through its training and alignment. Open data, reproducible, model-to-model."
- **Topics:** `llm-benchmark`, `cultural-domain-analysis`, `cda`, `large-language-models`, `comparative-evaluation`, `free-list`, `pile-sort`, `multidimensional-scaling`, `cognitive-anthropology`, `open-data`, `reproducible-research`, `claude`, `gpt`, `llama`, `mistral`, `qwen`, `deepseek`, `corpus-analysis`, `evaluation-benchmark`, `cogstructurelab`.

### Decision 7 — Bluesky / X handle in repo "links"

**Architect recommendation: Bluesky only.** Phase 7 first-publish target; X is draft-only in v1.

### Decision 8 — First post target

- **(a)** Hand-drafted launch-day post via admin console.
- **(b)** Wait for first organic trigger.

**Architect recommendation: (a)** — exercises Phase 7 end-to-end; gives launch a social presence; manual initiation respects §11.1 B-1. Affects M13 only; doesn't gate any Coder task.

---

## §6 Pre-release scan spec (gates T11)

The scan runs as `scripts/prerelease_scan.py` (T5) and must exit 0 within the 24 hours immediately preceding M12.

Eight checks:

1. **`gitleaks` on full history** — `gitleaks detect --source . --redact --report-path scan-gitleaks.json`. Custom rules include Slack webhook patterns (CLAUDE.md §9 pitfall #11). Any hit = FAIL.

2. **Forbidden-vocabulary grep across all committed text** — §1.5.4 left-column phrases plus case variants. Every hit reviewed; legitimate-context exceptions allow-listed explicitly.

3. **Leaked-internal-path scan** — `/home/lsb/`, `/home/markdd/`, `/Users/mark`, `/opt/lsb-agent/.env`, `lsb-agent-02`, Hetzner IPs from decommissioned VPS. Hits outside `docs/INCIDENTS/` and `HOSTING_AND_DEV_OPS.md` = FAIL.

4. **Real-email-address scan** — any address other than the chosen security alias or historical citation refs. PII removed (rewriting history if needed).

5. **API-key-pattern scan** — `sk-`, `hf_`, `xai-`, AWS access keys, GitHub PATs. Backstop to gitleaks.

6. **Public-URL-validity check** — every URL in README, SECURITY.md, dataset card, bundle README, methodology page must resolve or be marked as pre-launch placeholder.

7. **`.env` and credential-file presence check** — `.env` (not `.env.example`) tracked = FAIL.

8. **License-coverage sanity check** — four license files present, SPDX content correct, `LICENSE_COVERAGE.md` consistent.

---

## §7 Top-5 risks for Phase 8

1. **Forbidden-vocabulary leak in public README / dataset card / methodology placeholder.** Mitigation: CDA SME review on every public-facing doc; T5 scan #2.

2. **Production deployment regression** — dev/preview works, production breaks due to DNS/cert/CSP. Mitigation: T9 `curl -I` CSP-end-to-end check; UI/UX spot check on production URL.

3. **SECURITY.md contact address breaks before first report.** Misconfigured forwarding silently drops disclosures. Mitigation: T2 includes Mark's self-test.

4. **HuggingFace dataset card §1.5 framing violation.** Card is indexed by ML researchers; framing the bundle as "what models believe" is credibility-destroying. Mitigation: CDA SME gate on T7.

5. **DNS misconfiguration leaves dashboard inaccessible at go-public.** Mitigation: T9 end-to-end verification; M5 + M6 are pre-flip.

---

## §8 Suggested dispatch ordering

```
T1 (license audit)              ─┐
T2 (SECURITY.md contact)        ─┤
T3 (README pass)                ─┼─→ T5 (pre-release scan) ─→ T11 (go-public)
T4 (GitHub settings draft)      ─┘                              ↑
                                                                │
T6 (bundle build) ─→ T7 (HF dataset) ─→ T8 (Zenodo DOI) ────────┤
                                                                │
T9 (Cloudflare Pages production) ───────────────────────────────┤
                                                                │
T10 (methodology page resolution) ──────────────────────────────┘
```

Parallelism:
- T1, T2, T3, T4 parallelizable after Mark's §5 decisions.
- T6, T7, T8 serial chain; parallel to T1–T4 and T9–T10.
- T9 independent (needs M5, M6 only).
- T10 path-dependent.

**Critical path:** T1+T2+T3+T4 → T5 → T11.

---

## §9 Estimated timing

| Task | Coder time | Reviewer time | Gate verdicts | Mark-action time |
|---|---|---|---|---|
| T1 | 1–2 hours | 30 min | Architect | none |
| T2 | 30 min | 15 min | Architect | M1 (15–30 min) |
| T3 | 2–3 hours | 30 min | CDA SME | none |
| T4 | 1 hour | 15 min | CDA SME | none |
| T5 | 2–3 hours | 45 min | Architect | none (re-runnable) |
| T6 | 1–2 hours | 30 min | CDA SME | M7 partial (~15 min B2) |
| T7 | 1–2 hours | 30 min | CDA SME | M7 (30–45 min) |
| T8 | 30 min | 15 min | CDA SME | M8 + M9 (35 min) |
| T9 | 30 min | 30 min | UI/UX (light) | M5 + M6 (45–75 min) |
| T10 | 30 min – 3 hours | 15–45 min | CDA SME + UI/UX | varies |
| T11 | 15 min doc | 15 min | Architect | M2, M3, M4, M10, M11, M12 (~60 min) |

**Total Coder:** ~12–18 hours plus gate overhead.
**Total Mark-action:** ~3–4 hours.
**Realistic calendar:** 2–4 working days.

---

## §10 What's irreversible vs. reversible

| Action | Irreversibility | Notes |
|---|---|---|
| **M12 — flipping repo public** | **Irreversible** | Indexed by GitHub/Google/archive.org; cannot un-publish what archivers cached. **T5 scan is the gate.** |
| **M8 — minting Zenodo DOI** | **Irreversible** | Zenodo's permanent-versioning policy; retraction marks as withdrawn but DOI stays. |
| **M9 — git tag `v1.0.0`** | Effectively irreversible | Tag deletion possible but external mirrors preserve. |
| License decisions | Irreversible for released versions | Future versions can change; prior stays. |
| HuggingFace dataset publishing | Reversible (deletion); mirrors persist | |
| Cloudflare Pages production | Reversible (one-click rollback) | |
| Branch protection rules | Reversible any time | |
| Repository description + topics | Reversible any time | |
| `SECURITY.md` contact address | Reversible; transition-forwarding wise | |
| First social post | Reversible at platform; caches persist | |

---

## §11 What Phase 8 closure means

Phase 8 closes when:
- GitHub repo is public.
- `https://cogstructurelab.com` live, all security headers per HOSTING_AND_DEV_OPS.md §2.3.
- Open data bundle on B2 + HuggingFace + Zenodo with minted DOI.
- Methodology page finalized (path (a)) or has placeholder (path (b)).
- First social post published manually by Mark via admin console.
- Phase 8 closure status doc filed.

**Phase 9+ (out of scope, listed for reference):** additional collection campaigns, additional domains/models, drift visualization, FT designer polish completion, ongoing operation.

---

*End of Phase 8 kickoff. Next action: Mark resolves §5 decisions 1–8; orchestrator dispatches T1, T2, T3, T4 in parallel after answers land.*

---

## §12 Mark's §5 ratifications (2026-05-17)

All eight Architect recommendations accepted as-stated.

- **§5 Decision 1 (Methodology page):** APPROVED (b) — launch with placeholder "Methodology — coming soon (target: YYYY-MM-DD)".
- **§5 Decision 2 (HF dataset timing):** APPROVED (a) — ship with public repo go-live.
- **§5 Decision 3 (Zenodo DOI + tag):** APPROVED — single `v1.0.0` tag; DOI minted at or shortly after go-public.
- **§5 Decision 4 (SECURITY.md contact):** APPROVED (b) — `security@cogstructurelab.com` via Cloudflare Email Routing → ProtonMail. SECURITY_AND_HARDENING.md §6.5 updated to match.
- **§5 Decision 5 (Branch protection):** APPROVED (b) — soft: PR required from forks; Mark direct-pushes from local clone (preserves CLAUDE.md §8).
- **§5 Decision 6 (Repo description + topics):** APPROVED — Architect drafts in §5 decision 6 of this kickoff used verbatim; Mark may edit at M10.
- **§5 Decision 7 (Bluesky / X handle):** APPROVED (b) — Bluesky only in repo links.
- **§5 Decision 8 (First post target):** APPROVED (a) — hand-drafted launch-day post via admin console.

Phase 8 dispatch resumes. T1 + T3 + T4 dispatch in parallel (T1 Coder direct; T3 and T4 CDA SME first). T2 documentation update dispatches in parallel; Mark sets up Cloudflare Email Routing (M1) asynchronously and self-tests at his convenience.

Mark-action parallelism: Mark may begin M1 (Cloudflare Email Routing), M3 (Gmail SMTP app password), M4 (Bluesky app password), M5+M6 (Cloudflare Pages production + DNS) at any time; these unblock T2 acceptance and T9 + T11.

