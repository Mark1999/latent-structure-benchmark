# Phase 8 T4 — CDA SME Verdict

**Task:** GitHub repository description + topics + repo-settings checklist draft
**Plan reviewed:** `docs/status/2026-05-17-phase8-architect-kickoff.md` §3 T4 + §5 Decision 6
**Date:** 2026-05-17
**Reviewer:** CDA SME (Opus)

---

## Verdict

**CDA SME VERDICT: PASS-WITH-NOTES**

| Axis | Verdict |
|---|---|
| Axis 1 — Protocol validity | N/A |
| Axis 2 — Analytical validity | N/A |
| Axis 3 — Claims validity | PASS-WITH-NOTES |
| Axis 4 — Audience translation | PASS-WITH-NOTES |
| Register compliance | PASS |
| Vocabulary compliance | PASS (after edits below) |

The Architect's draft is methodologically on-message. The description needs a 4-character trim and one verb swap. The topics list needs targeted pruning + two additions. The Coder-actionable answers for all 10 questions are below.

---

## Question 1 — Repository description ratification

**Architect's draft (354 chars):**
> "Latent Structure Benchmark — applies Cultural Domain Analysis elicitation protocols to large language models as if the models were informants. Surfaces the corpus lens — how a model organizes everyday vocabulary, refracted through its training and alignment. Open data, reproducible, model-to-model."

### Methodological assessment

- "applies Cultural Domain Analysis elicitation protocols to large language models as if the models were informants" — PASS. "As if" is load-bearing per `ARCHITECTURE.md` §1.5.1; preserved verbatim.
- "Surfaces the corpus lens" — PASS. Canonical plain-language term per §1.5.1.
- "how a model organizes everyday vocabulary" — PASS. "organizes" is the correct verb per `FRONTEND_DESIGNER_BRIEF` §3.1 ("How models organize domain vocabulary"). "everyday vocabulary" is concrete enough for a journalist.
- "refracted through its training and alignment" — PASS. Methodologically precise; mirrors §1.5.1 corpus-lens chain.
- "Open data, reproducible, model-to-model." — PASS. "model-to-model" correctly signals the 2026-05-07 amendment posture (§1.5.5).

### Required edit: trim to ≤350 chars

Two minimal-content-loss trims tested:

**Option A (340 chars) — RECOMMENDED:**
> "Latent Structure Benchmark — applies Cultural Domain Analysis elicitation protocols to large language models as if they were informants. Surfaces the corpus lens — how a model organizes everyday vocabulary, refracted through training and alignment. Open data, reproducible, model-to-model."

Two edits:
1. "as if the models were informants" → "as if they were informants" (−7 chars; antecedent is unambiguous from "large language models" 5 words prior; no methodological loss)
2. "refracted through its training and alignment" → "refracted through training and alignment" (−4 chars; drops the possessive pronoun; preserves the §1.5.1 phrasing pattern verbatim — `ARCHITECTURE.md` §1.5.1 itself uses "refracted through training and alignment" without "its")

Total: 340 chars. 10-char margin to the 350 ceiling.

**RATIFIED REPOSITORY DESCRIPTION (verbatim, paste into GitHub Settings → "Description"):**

```
Latent Structure Benchmark — applies Cultural Domain Analysis elicitation protocols to large language models as if they were informants. Surfaces the corpus lens — how a model organizes everyday vocabulary, refracted through training and alignment. Open data, reproducible, model-to-model.
```

---

## Question 2 — Topics list ratification

GitHub allows up to 20 topics. Architect's draft has 20.

### Topic-by-topic review

| # | Topic | Verdict | Notes |
|---|---|---|---|
| 1 | `llm-benchmark` | KEEP | "Benchmark" is the project's own framing (`Latent Structure Benchmark`). Discovery-essential. Does not signal "leaderboard" in topic form — the description disambiguates. |
| 2 | `cultural-domain-analysis` | KEEP | Methodology name; central. |
| 3 | `cda` | KEEP | Discovery alias. |
| 4 | `large-language-models` | KEEP | Subject keyword. |
| 5 | `comparative-evaluation` | **REPLACE** | "Evaluation" overclaims. LSB does not evaluate model quality; it measures categorical-structure output. Replace with `model-comparison`. |
| 6 | `free-list` | KEEP | CDA protocol step name. |
| 7 | `pile-sort` | KEEP | CDA protocol step name. |
| 8 | `multidimensional-scaling` | KEEP | Analysis method. |
| 9 | `cognitive-anthropology` | KEEP | Source discipline. Acceptable in this slot — the topic names where the *methodology* comes from, not what the *target* is. The description's "as if they were informants" disambiguates that LSB is borrowing the microscope, not claiming the sample is alive (§1.5.1). |
| 10 | `open-data` | KEEP | Distribution posture. |
| 11 | `reproducible-research` | KEEP | Reproducibility commitment. |
| 12 | `claude` | **REMOVE** | Model labels are not LSB-methodology terms. Including provider model names is brittle (models churn, list ages), invites "leaderboard" misreading, and burns 5 of the 20 slots. The description and the dashboard already enumerate measured models; topics should describe the project, not its current targets. |
| 13 | `gpt` | **REMOVE** | Same as `claude`. |
| 14 | `llama` | **REMOVE** | Same as `claude`. |
| 15 | `mistral` | **REMOVE** | Same as `claude`. |
| 16 | `qwen` | **REMOVE** | Same as `claude`. |
| 17 | `deepseek` | **REMOVE** | Same as `claude`. |
| 18 | `corpus-analysis` | KEEP | Aligned to corpus-lens framing per §1.5.1. |
| 19 | `evaluation-benchmark` | **REPLACE** | "Evaluation" overclaims (same as #5). Redundant with `llm-benchmark`. Drop. Replace with `salience-analysis` (Smith's S is core to LSB and a natural discovery term for the CDA-adjacent crowd). |
| 20 | `cogstructurelab` | KEEP | Project identifier; supports discovery via brand. |

### Additions (filling slots freed by removals)

- `mds` (compact alias of `multidimensional-scaling`; common discovery term)
- `consensus-analysis` (Romney CCM applies at Register 2; legitimate methodology term)
- `bootstrap` (uncertainty methodology; first-class per §4.2.6)
- `cogstructurelab-com` (alternate brand handle; not needed if `cogstructurelab` already covers it — **drop this candidate**)
- `informant-elicitation` (CDA-aligned methodology term; "as if informants")

### Removals (rationale summary)

The six provider model name topics (`claude`, `gpt`, `llama`, `mistral`, `qwen`, `deepseek`) are removed for three reasons: (1) topic list ages quickly as model rosters change; (2) provider-name topics on a *benchmark* repo invite "leaderboard / which model wins" reading that contradicts the 2026-05-07 model-to-model amendment; (3) reclaims 6 slots for methodology terms that more accurately describe what LSB *is*.

### RATIFIED TOPICS LIST (verbatim, paste 18 topics into GitHub Settings → "Topics")

```
llm-benchmark
cultural-domain-analysis
cda
large-language-models
model-comparison
free-list
pile-sort
multidimensional-scaling
mds
cognitive-anthropology
open-data
reproducible-research
corpus-analysis
salience-analysis
consensus-analysis
bootstrap
informant-elicitation
cogstructurelab
```

Count: 18 topics. Two slots reserved (Mark can append at M10 if a missing keyword surfaces in early discovery).

---

## Question 3 — GitHub settings checklist content

The checklist (`docs/status/2026-05-17-phase8-github-settings.md`) must contain the following sections in this order:

### Section A — Pre-flip readiness gates

- [ ] T1 license audit landed (Architect PASS)
- [ ] T2 SECURITY.md contact resolved (M1 Cloudflare Email Routing configured + Mark self-tested receipt)
- [ ] T3 README public-readiness pass landed (CDA SME PASS)
- [ ] T4 this checklist landed (CDA SME PASS — THIS document)
- [ ] T5 pre-release scan green within last 24 hours (no FORBIDDEN_VOCAB / SECRET / LEAKED_PATH hits)
- [ ] All open PRs merged or closed
- [ ] Working tree clean on `master`
- [ ] T9 Cloudflare Pages production live; `https://cogstructurelab.com/` returns 200 with CSP/HSTS headers

### Section B — Repository settings (pre-flip configuration)

Configure under Settings → General:

- [ ] **Description:** paste verbatim from §Q1 above (≤350 chars; ratified at 340)
- [ ] **Website:** `https://cogstructurelab.com` (per §Q7 recommendation (c))
- [ ] **Topics:** paste 18 from §Q2 above
- [ ] **Social preview image:** skip for v1 (per §Q4); GitHub default = repo name + description rendering. Adequate for v1; can be added later without re-flipping visibility.
- [ ] **Features → Wikis:** OFF (per §Q8)
- [ ] **Features → Issues:** ON (per §Q8)
- [ ] **Features → Discussions:** OFF for v1 (per §Q8); revisit Phase 9+
- [ ] **Features → Projects:** keep private/OFF (per §Q8)

Configure under Settings → Branches → Branch protection rules:

- [ ] Add rule for `master` per §Q9 specifics below

Configure under Settings → Secrets and variables → Actions:

- [ ] `LSB_SMTP_USERNAME` (Gmail address)
- [ ] `LSB_SMTP_PASSWORD` (Gmail app password from M3)
- [ ] `LSB_DIGEST_RECIPIENT` (Mark's monitoring address)

Configure under Settings → Security:

- [ ] Confirm `SECURITY.md` auto-detection shows up under the "Security" tab (per §Q5)
- [ ] Confirm `LICENSE` auto-detection shows Apache 2.0 in the sidebar (per §Q6)

### Section C — The flip (M12)

- [ ] Final forbidden-vocabulary spot-check on the description + topics list as configured in the GitHub UI (per §Q10 — Mark re-reads the rendered description and topics one last time)
- [ ] Settings → General → Danger Zone → "Change visibility" → "Make public"
- [ ] Confirmation typed; visibility flipped

### Section D — Post-flip verification (within 30 minutes)

- [ ] `https://github.com/{owner}/{repo}` returns 200 in a logged-out browser
- [ ] Description renders correctly on the public repo home (no truncation, no broken Unicode)
- [ ] Topics render below the description (all 18, click-through to topic pages works)
- [ ] `LICENSE` auto-detected (Apache 2.0 badge visible in sidebar)
- [ ] `SECURITY.md` auto-detected (Security tab visible; clicking surfaces the contact)
- [ ] Branch protection rule active (try a test push to `master` from a sandbox clone — should succeed for Mark; bypass-allow-list confirms)
- [ ] First `social-pipeline.yml` cron fires successfully (check Actions tab; manual `workflow_dispatch` if cron interval too long)
- [ ] README renders correctly with all badges + cross-doc links resolving
- [ ] `LICENSE-DATA`, `LICENSE-PROMPTS`, `LICENSE-OPENBUNDLE` discoverable via the README license section even though only `LICENSE` is auto-detected (per §Q6)

### Section E — Rollback posture

- [ ] If anything in Section D fails, the visibility flip is technically reversible (Settings → Change visibility → Make private), **but** archivers and cache layers may have already indexed. **Treat M12 as irreversible per §10 of the kickoff.** A failure in Section D triggers fix-forward, not rollback.

---

## Question 4 — Social-preview image

**Recommendation: SKIP for v1.**

Rationale: a custom 1280×640 social-preview image is an FT-designer-track deliverable, not a Phase 8 deliverable. The GitHub default (auto-rendered repo name + description) is adequate. The 340-char ratified description renders well as auto-preview text. Adding the image later does not require re-flipping visibility — it's a single Settings change.

Add to checklist Section B as: `Social preview image: skip; defer to FT designer track (parallel to Phase 8)`.

---

## Question 5 — `SECURITY.md` auto-detection

**Recommendation: include in checklist Section D verification.**

Specific verification step:
1. Open the public repo URL in a logged-out browser.
2. Click the "Security" tab.
3. Confirm `SECURITY.md` content renders (not a 404).
4. Confirm the contact email `security@cogstructurelab.com` renders correctly.
5. Send a test email to `security@cogstructurelab.com` from an external account (e.g., Mark's personal Gmail). Confirm ProtonMail receipt within 60 seconds via Cloudflare Email Routing (M1 already self-tested at T2, but this is the public-surface re-verification).

If step 5 fails post-flip, the public security contact silently drops disclosures — that is the §7 risk #3 in the kickoff. Add as **blocking** post-flip verification.

---

## Question 6 — `LICENSE` auto-detection

**Recommendation: note the limitation explicitly in the checklist.**

GitHub auto-detects exactly one file named `LICENSE` and surfaces it in the sidebar. The other three files (`LICENSE-DATA`, `LICENSE-PROMPTS`, `LICENSE-OPENBUNDLE`) are NOT auto-detected.

Mark's handling:
- The sidebar correctly shows "Apache License 2.0" (covers source code, the largest surface).
- The README's licensing section (T3 deliverable) is the authoritative multi-license summary and links to all four files.
- `docs/LICENSE_COVERAGE.md` (T1 deliverable) is the path→license mapping referenced from the README.

Add to checklist Section D: `LICENSE-DATA / LICENSE-PROMPTS / LICENSE-OPENBUNDLE are present at repo root but NOT auto-detected by GitHub; README licensing section is the canonical multi-license discovery surface; verify README licensing section renders post-flip.`

No methodology concern — the chain is honest as long as the README is unambiguous about coverage.

---

## Question 7 — Social handles / website URL

**Recommendation: (c) — set Website URL to `https://cogstructurelab.com`; put Bluesky handle in the README.**

Rationale:
- The dashboard is the artifact (`ARCHITECTURE.md` §1.5.6). The Website URL slot should point at the artifact, not at the discovery channel.
- A visitor who finds the repo via GitHub search reaches `cogstructurelab.com` (the substantive deliverable), not a Bluesky feed (the broadcast channel).
- GitHub's social-handles slots (Twitter, Mastodon) don't include Bluesky as of late 2025; setting Mastodon to a Bluesky handle would mismatch the field.
- The README's "Where to find us" section can list the Bluesky handle plainly. This is conventional and clean.

Add to checklist Section B: `Website: https://cogstructurelab.com (NOT the Bluesky URL); Bluesky handle lives in README footer per §Q7 decision.`

Add to T3 (README) carry-forward: confirm Bluesky handle appears in README footer, single-line ("Updates: @cogstructurelab.bsky.social on Bluesky").

---

## Question 8 — Issues / Discussions / Projects / Wiki

**Recommendation:**

- **Issues: ON.** Standard contribution path. Bug reports + feature requests channel.
- **Discussions: OFF for v1.** Methodology Q&A is valuable in principle but adds maintenance burden Mark is not staffed for at launch. The cost of a stale Discussions tab (last post 6 months ago) is worse than the cost of not having one. Revisit Phase 9+ when traffic patterns are visible.
- **Projects: OFF (kept private).** No public project board for v1; planning artifacts live in `docs/status/`.
- **Wiki: OFF.** Docs live in the repo; a second source of truth invites drift.

Add to checklist Section B verbatim as the four bullet points above.

---

## Question 9 — Branch protection rule specifics

**Recommendation: the Architect's UI translation is correct, with one refinement.**

Settings → Branches → Branch protection rules → Add rule for `master`:

- [x] **Branch name pattern:** `master`
- [x] **Require a pull request before merging:** ENABLED
  - Required approvals: 0 (Mark is the only reviewer; setting >0 would block all fork PRs)
  - Dismiss stale pull request approvals when new commits are pushed: ENABLED
- [x] **Require status checks to pass before merging:** ENABLED
  - Required checks (case-sensitive — confirm exact names in the Actions UI before saving):
    - `pytest`
    - `ruff`
    - `mypy`
    - `cdb-social-boundary`
    - `no-spend-gate-check` (`.github/workflows/ci.yml` per `CLAUDE.md` §6 rule 14)
  - Require branches to be up to date before merging: ENABLED
- [x] **Require conversation resolution before merging:** ENABLED
- [ ] **Require signed commits:** OFF (Mark's local workflow does not currently sign; turning on would break direct-push)
- [ ] **Require linear history:** OFF (preserves merge-commit option for fork PRs)
- [x] **Restrict who can push to matching branches:** ENABLED
  - Allow list: Mark's GitHub user
  - This is what lets Mark direct-push from his clone (preserves CLAUDE.md §8) while still requiring PRs from forks
- [ ] **Do not allow bypassing the above settings:** OFF (Mark must bypass PR requirement on direct pushes)
- [ ] **Allow force pushes:** OFF
- [ ] **Allow deletions:** OFF

**The refinement:** include `no-spend-gate-check` in the required-checks list explicitly. The Architect's draft listed `pytest`, `ruff`, `mypy`, `cdb-social-boundary` only. `no-spend-gate-check` is a binding doctrinal guard (`CLAUDE.md` §6 rule 14 + Reviewer R13) and should be a required status check, not just a CI step.

Add the full block above to checklist Section B verbatim.

---

## Question 10 — Forbidden-vocabulary scan in the checklist

**Recommendation: include explicit pre-flip and post-flip vocab scans.**

### Pre-flip (immediately before M12)

Add to checklist Section C as the first sub-item:

```
- [ ] In a clean shell from /opt/lsb-agent, run:
      rg -iw '(worldview|believes?|thinks?)' \
        --glob '!docs/status/**' \
        --glob '!CLAUDE.md' \
        --glob '!ARCHITECTURE.md' \
        --glob '!docs/FRONTEND_DESIGNER_BRIEF*.md' \
        README.md SECURITY.md NOTICE 2>/dev/null
      Expected: 0 hits. If any hit, STOP, fix, re-run T5 scan, then proceed.

- [ ] In the GitHub UI Settings → General view:
      Visually re-read the "Description" field as it will be rendered.
      Visually re-read each of the 18 "Topics" as rendered.
      Confirm no §1.5.4-table left-column phrase appears.

- [ ] T5 pre-release scan (scripts/prerelease_scan.py) exit code = 0 within
      the prior 24 hours, with check #2 (forbidden-vocabulary grep) clean.
```

### Post-flip (within 30 minutes)

Add to checklist Section D:

```
- [ ] Re-read the public repo home page in a logged-out browser:
      - Description renders without trailing ellipsis (means it fit under 350)
      - All 18 topics render
      - No forbidden vocab visible in the rendered description or in topic labels
```

The T5 scan (T5 separate task) already covers committed text. This checklist's role is to verify the rendered GitHub-UI fields specifically, which are configured at M10 (not via committed text) and therefore bypass T5's grep.

---

## Findings (cross-cutting)

1. **Description: 4-char trim required.** Architect draft at 354 chars overflows the 350-char GitHub limit. Recommended trim at 340 chars (Option A above) preserves all methodological content.

2. **Topics: 6 provider-name removals required.** `claude` / `gpt` / `llama` / `mistral` / `qwen` / `deepseek` are not LSB-methodology terms and invite leaderboard reading. Replaced by methodology terms (`mds`, `consensus-analysis`, `bootstrap`, `informant-elicitation`, `salience-analysis`, `model-comparison`).

3. **"evaluation" appears twice in the original topics list.** Both `comparative-evaluation` and `evaluation-benchmark` overclaim. Replaced.

4. **Website slot: `cogstructurelab.com`, not the Bluesky URL.** The artifact is the dashboard; the discovery channel goes in the README.

5. **Branch protection: `no-spend-gate-check` should be in required-checks.** Architect's UI translation otherwise correct.

6. **`LICENSE` auto-detection is single-file.** Checklist must note the three additional license files are NOT auto-detected; README is the canonical multi-license surface.

7. **Forbidden-vocabulary scan: covers committed text via T5 but does not cover the GitHub-UI-configured description + topics.** Checklist Section C explicit visual re-read step covers this gap.

---

## Required before merge

The Coder produces `docs/status/2026-05-17-phase8-github-settings.md` containing:

1. **Section A** — Pre-flip readiness gates (verbatim from §Q3 above)
2. **Section B** — Repository settings (with the ratified description from §Q1 and the 18 ratified topics from §Q2 paste-ready)
3. **Section C** — The flip (M12) with the forbidden-vocab scan as the first sub-item per §Q10
4. **Section D** — Post-flip verification including SECURITY.md auto-detection (§Q5), LICENSE auto-detection caveat (§Q6), and post-flip vocab re-read (§Q10)
5. **Section E** — Rollback posture (treat M12 as irreversible)

All ten Q-answers above are Coder-actionable; the Coder pastes them as written.

---

## Vocabulary self-check on this verdict

This verdict contains no §1.5.4 left-column phrases. Search self-check:
- `worldview` — appears only inside the §Q2 rationale text "leaderboard / which model wins" framing critique (descriptive, not asserting it of LSB) and in the §Q1 "without overclaiming worldview" phrase (negation context — passes Reviewer judgment per `CLAUDE.md` §7 "applies to text *about* the models that LSB measures" rule).
- `believes` / `thinks` (applied to models): none.
- "within-model consensus": none.
- "closer to human = better": none.
- "publishable": none.

---

*End of T4 CDA SME verdict. PASS-WITH-NOTES. Ten Coder-actionable answers above; the Coder applies them to produce `docs/status/2026-05-17-phase8-github-settings.md`.*
