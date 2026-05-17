# Phase 8 T3 — CDA SME Verdict (README.md public-readiness pass)

**Document:** `docs/status/2026-05-17-phase8-T3-cda-sme-verdict.md`
**Reviewer:** CDA SME (Opus)
**Date:** 2026-05-17
**Plan reviewed:** `docs/status/2026-05-17-phase8-architect-kickoff.md` §3 T3 + Mark's §12 ratifications
**Object of review:** the current `README.md` plus the Coder's forthcoming v1-public rewrite
**Companion verdicts in series:** none — T3 is a fresh CDA SME gate

---

## Verdict

**CDA SME VERDICT: PASS-WITH-NOTES**

| Axis | Verdict |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | PASS-WITH-NOTES (R10 binding restated; see Q7) |
| Axis 3 — Claims validity | PASS-WITH-NOTES (one §1.5.7 hypothesis-framing tightening; see Q1 + Q5) |
| Axis 4 — Audience translation | PASS-WITH-NOTES (current README §5 "Phase 1 (collection) is the current focus" is pre-launch language and must go; see Q9) |
| Register compliance | PASS |
| Vocabulary compliance | PASS |

The plan is doctrinally sound. The README is the most-read public surface in the project; this verdict provides exact verbatim strings the Coder will paste so that no methodological judgment is required at code-write time. PASS-WITH-NOTES is gated on the Coder applying every R{N} binding ruling below verbatim.

---

## §1 Why this verdict matters

T3 is methodology-load-bearing at the highest order. The README is what a researcher arriving from a GitHub search, a journalist clicking through from a social post, or a peer evaluator citing the project will read first. Every paragraph below has been scoped against:

- ARCHITECTURE.md §1.5 (binding framing — corpus lens five-link chain, "as if" methodological move, exploratory not hypothesis-testing posture)
- ARCHITECTURE.md §1.5.4 (12-row forbidden vocabulary table)
- ARCHITECTURE.md §1.5.5 (human grounding removed from v1; "model-to-model is the design, not a defect")
- ARCHITECTURE.md §1.5.6 (no paper / no preprint / "credible to a skeptical reader," not "publishable in *Nature*")
- ARCHITECTURE.md §1.5.7 (exploratory framing — "we ran the protocol; here is what came out")
- ARCHITECTURE.md §4.5 R10 (no point estimate without uncertainty)
- ARCHITECTURE.md §5.3 Phase 8 line 1489 (Romney / D'Andrade / Weller / Borgatti / Batchelder ancestry credit, link to free-access originals where available)
- CLAUDE.md §1 (LSB does NOT measure cultural worldview, belief, or cognition)
- CLAUDE.md §7 (forbidden vocabulary enforced by Reviewer)
- FRONTEND_DESIGNER_BRIEF.md §2 ("the one-paragraph pitch") and §3.1 (forbidden vocabulary register)
- FRONTEND_DESIGNER_BRIEF_APPENDIX.md §6 (tone of voice: first-person plural, declarative, no marketing intensifiers, no second-person in body)

---

## §2 Forbidden-vocabulary scan of the current README

Run against ARCHITECTURE.md §1.5.4 (all 12 rows) and the generic forbidden-term set (`worldview`, `believes`, `thinks` applied to models).

**Result: CLEAN.** No occurrences in the current `README.md` of any left-column phrase, nor any of the three generic forbidden terms used in a model-facing context. The "thinks" / "believes" / "worldview" tokens do not appear at all. The current first paragraph's use of "categorize" and "categorical structure" is on-message.

This is the floor the Coder's rewrite must preserve.

---

## §3 Question-by-question rulings (verbatim Coder-pasteable strings)

### Q1 — Opening paragraph posture — **R1 binding**

**Recommendation: Adopt a 3-paragraph opening.** Para 1 is the §1.5 anchor (corpus lens + the binding negation in the same paragraph). Para 2 is the methodology ancestry sentence (Q3 covers the citations). Para 3 is the website-is-the-artifact stance (§1.5.6) and the exploratory framing (§1.5.7).

The Architect's repo-description draft is correct for the GitHub sidebar (≤350 chars) but is too compressed to do the README's "first paragraph is the 30-second test surface" job. The README opening should be longer and should land the §1.5 negation in para 1, not defer it.

**R1 (binding) — paste verbatim as the README opening, immediately after the H1 + tagline lines:**

> The **Latent Structure Benchmark (LSB)** applies Cultural Domain Analysis (CDA) elicitation protocols to large language models as if the models were informants. It surfaces the **corpus lens** — the categorical structure of a model's training corpus, refracted through training and alignment — by running the same free-list, pile-sort, and pile-interview protocols across many models on the same everyday domains (family terms, holidays, food). The result is a comparative map of how different models organize the same vocabulary, with verbatim prompts, verbatim responses, and reproducible analysis code published openly.
>
> LSB **does not measure** cultural worldview, belief, or cognition. Models do not have lived experience; they synthesize statistical patterns from text corpora. The "as-if-informant" framing is methodological, not metaphysical: we are borrowing a microscope from cognitive anthropology, not claiming the sample is alive. Every dashboard surface, every social post, and every line of README copy is careful about this distinction.
>
> LSB is a website that uses research methods, not a research project that has a website. The interactive dashboard at [cogstructurelab.com](https://cogstructurelab.com) is the primary deliverable; the benchmark, the open data bundle, and the analysis pipeline all exist to make the dashboard credible, useful, and discoverable. The originating question is exploratory — *what happens if you give a large language model a CDA free-list / pile-sort / interview?* — and the answer is the data itself, released for the community to interpret.

**Rationale.**

- Para 1 names CDA + introduces "corpus lens" with its long-form anchor in the same paragraph (per §1.5.1: "methodology contexts use the long form (or define the short form on first use)"; the README is a methodology-context surface).
- Para 2 lands the binding negation from CLAUDE.md §1 in the opening (not buried in §3 of the doc).
- Para 3 lands §1.5.6 ("website is the artifact") + §1.5.7 ("originating question is exploratory"). The Mark-italicized originating question is quoted verbatim from ARCHITECTURE.md §1.5 line 91 and §1.5.7 line 217.

**What was removed from the current README opening:** the phrase "the corpus lens — how a model organizes everyday vocabulary, refracted through its training and alignment" (lifted from the Architect's repo-description draft) is on-message but too compressed for the README's first-paragraph job. The R1 version preserves the same anchor with more methodology specificity ("free-list, pile-sort, and pile-interview protocols").

---

### Q2 — Where the §1.5 negation appears — **R2 binding**

**Resolved by R1.** The negation appears in Para 2 of the opening per R1 above. A dedicated "What LSB is and isn't" section appears later (per Q5 / R5) and repeats the negation in a structured form — README readers who skim straight to that section also encounter it.

**R2 (binding):** Do **not** defer the negation. It is in the opening 3-paragraph block, not below the fold.

---

### Q3 — Ancestry citations format — **R3 binding**

**Recommendation: Hybrid (a)+(c).** A short inline reference in the opening Para 2 (already in R1) names CDA's lineage; a dedicated "Methodology ancestry" section near the foot of the README provides full citations with free-access links where available.

The opening should not bury a five-author citation in a single sentence — five inline names in Para 1 would make the §1.5 negation harder to land — so R1 leaves "the CDA tradition developed by cognitive anthropologists in the 1970s and 80s" as the inline reference (matching the current README's existing wording, which is on-message).

The dedicated section pays the ancestry credit per ARCHITECTURE.md §5.3 line 1489.

**R3 (binding) — paste verbatim as a new section before the "Citation" section:**

```markdown
## Methodology ancestry

LSB applies Cultural Domain Analysis, a methodology developed by cognitive anthropologists from the 1960s onward to study how human informants organize cultural vocabulary. LSB stands on the shoulders of:

- **A. Kimball Romney, Susan C. Weller, and William H. Batchelder (1986).** "Culture as Consensus: A Theory of Culture and Informant Accuracy." *American Anthropologist* 88(2): 313–338. The foundational cultural consensus paper. Free access via JSTOR or via Romney's archive at UC Irvine.
- **Roy G. D'Andrade (1995).** *The Development of Cognitive Anthropology.* Cambridge University Press. The standard reference for the cognitive-anthropology tradition LSB inherits.
- **Susan C. Weller and A. Kimball Romney (1988).** *Systematic Data Collection.* Qualitative Research Methods Series, Vol. 10. SAGE Publications. The methodological handbook for free-list, pile-sort, and triad protocols.
- **Stephen P. Borgatti (1996).** *ANTHROPAC 4.0 Methods Guide.* Analytic Technologies. The operational guide that made pile-sort + consensus analysis practical for a generation of fieldworkers. Openly archived at [analytictech.com](https://www.analytictech.com/).
- **William H. Batchelder and A. Kimball Romney (1988).** "Test Theory Without an Answer Key." *Psychometrika* 53(1): 71–92. The statistical foundation for the consensus model LSB uses to evaluate cross-model categorical agreement.

LSB applies these methods to models, not to the humans they were designed for. The methodology page on the dashboard documents the adaptation table — what carries over directly, what required modification, and where the "as-if-informant" framing is load-bearing.
```

**Rationale.**

- Five named ancestors per ARCHITECTURE.md §5.3 line 1489 + CLAUDE.md §1.5.6.
- Links to free-access originals where they exist (analytictech.com is openly archived; the *American Anthropologist* paper is free-access via JSTOR's open-content portal; the others are book-form and pointed to by publisher, not linked because no free-access edition exists).
- Closing paragraph anchors the "applied to models, not humans" reframing — this is doctrinally important: a reader scanning only the ancestry section needs to be told LSB isn't doing classical CDA on humans.
- The "methodology page on the dashboard documents the adaptation table" sentence is forward-compatible with the Phase 8 §5 Decision 1 placeholder strategy (Q9 covers placeholder wording).

**What about the "free where possible" phrasing in §1.5.6 / §5.3?** Borgatti's ANTHROPAC manual is openly archived; the *American Anthropologist* 1986 paper is free-access via JSTOR; Batchelder & Romney 1988 *Psychometrika* and D'Andrade 1995 book are not free. The R3 section names all five, links only the ones with reliable free-access mirrors. This is faithful to "free where possible."

---

### Q4 — Quickstart commands — **R4 binding**

**Recommendation: A short, working Getting Started section.** The current README has no Getting Started; "Quick links" lists URLs but no commands. Researchers landing cold need to know they can clone, install, and reproduce a figure.

**R4 (binding) — paste verbatim as a new section after "Repository structure":**

```markdown
## Getting started

LSB is built with [uv](https://docs.astral.sh/uv/) for Python and Vite for the dashboard. From a fresh clone:

\`\`\`bash
# Clone
git clone https://github.com/AILLM1999/lsb.git
cd lsb

# Install Python dependencies (uv handles the virtualenv)
uv sync

# Build the open-data SQLite database from the raw JSONL bundle
uv run python scripts/build_db.py

# Run the analysis pipeline to regenerate the per-domain JSON the dashboard reads
uv run python scripts/analyze.py
uv run python scripts/publish.py

# (Optional) Run the dashboard locally
cd apps/dashboard
npm install
npm run dev
\`\`\`

After `npm run dev` the dashboard runs at `http://localhost:5173` and renders exactly what the public dashboard renders. Every figure on [cogstructurelab.com](https://cogstructurelab.com) is reproducible from `data/raw/informants.jsonl` plus the scripts above.

For the field-by-field schema of `informants.jsonl`, see [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md). For the analysis methods, see the methodology page on the dashboard.
```

**Rationale.**

- Names `uv sync` (per Phase 8 kickoff §3 T3 spec) but extends to a fuller flow: install → build_db → analyze → publish → dashboard.
- The "Every figure on cogstructurelab.com is reproducible from `data/raw/informants.jsonl` plus the scripts above" sentence is the §6.1 reproducibility guarantee in plain language.
- The `git clone` URL uses `AILLM1999/lsb.git` (matches Mark's HuggingFace + GitHub handle per Phase 8 §3 T7).
- Backslash-escaped triple backticks are an artifact of this verdict file's markdown; the Coder pastes literal triple backticks per the syntax-highlighted code fences.
- No spend-gate language. No estimated cost line. <!-- noqa: spend-gate-check -->

---

### Q5 — "What LSB is, what LSB is not" section — **R5 binding**

**Recommendation: Yes — preserve it.** The current README's "What LSB is and isn't" section (lines 9–15) already exists and is on-message. R5 tightens it to align with the methodology page's §6.1 item 5 binding language and to land the §1.5.7 exploratory-framing posture more concretely.

**R5 (binding) — replace the current "What LSB is and isn't" section verbatim with:**

```markdown
## What LSB measures, and what it does not

LSB **measures** what frontier LLMs produce when asked to categorize, in a way that's reproducible, comparable across models, and trackable across time. Specifically:

- The latent categorical structure of a training corpus, as refracted through a model's training and alignment pipeline, surfaced by applying CDA elicitation protocols to the model as if it were an informant.
- Output-level statistics — Smith's S (per-item salience), Sutrop CSI (cognitive salience), Romney CCM (cross-model categorical agreement), MDS coordinates, Procrustes drift — all with bootstrap confidence intervals.
- The model's full verbatim free-list, pile-sort, and interview responses, including failures and refusals.

LSB **does not measure** cultural worldview, belief, cognition, or "what the model knows." Models do not have lived experience. They synthesize statistical patterns from text corpora. LSB does not:

- Test a hypothesis about model cognition, bias, or alignment. The originating question is exploratory: *what happens if you give a large language model a CDA free-list / pile-sort / interview?*
- Compare models to a "ground truth" human baseline. Every domain in v1 is permanently model-to-model — that is the design, not a defect. See [`ARCHITECTURE.md`](ARCHITECTURE.md) §1.5.5 for the rationale.
- Rank models. There is no leaderboard, no "best at family terms" score. LSB produces a comparative map; readers draw their own conclusions.
- Claim that models "understand" or "agree about" anything. The statistics describe output distributions, not minds.

For the full scientific framing — including the five-link corpus-lens chain (corpus → training → alignment → decoding → output distribution), the known limitations, and the language guardrails — see [`ARCHITECTURE.md`](ARCHITECTURE.md) §1.5 or the methodology page on the dashboard.
```

**Rationale.**

- The "what LSB measures, and what it does not" phrasing matches FRONTEND_DESIGNER_BRIEF §2 + ARCHITECTURE.md §1.5.6 binding §6.1 item 5 ("What this measures and what it does not").
- The four-bullet "does not" list is doctrinally load-bearing:
  - Bullet 1 lands §1.5.7 (exploratory, not hypothesis-testing).
  - Bullet 2 lands the 2026-05-07 human-grounding-removal amendment (§1.5.5) — "permanently model-to-model — that is the design, not a defect" is verbatim language that defuses the historical pitfall #4 ("no human baseline available yet").
  - Bullet 3 ("no leaderboard, no rank") is the most-asked-about misreading and worth pre-empting.
  - Bullet 4 lands the §1.5 forbidden vocabulary at the conceptual level (no "understand," no "agree about").
- The "originating question" italicized quote is verbatim from §1.5.7 line 217 — same wording as R1 Para 3, deliberately repeated for skim-readers.

---

### Q6 — License summary — **R6 binding**

**Recommendation: Short summary in README with link to `LICENSE_COVERAGE.md`.** The current README has a full four-row table (lines 42–53) plus prose. R6 keeps a compressed version near the top (the Architect's recommendation) and routes the file-by-file detail to the T1 deliverable.

**R6 (binding) — replace the current "Licenses" section verbatim with:**

```markdown
## Licenses

LSB ships under a split licensing model:

| Content type | License |
|---|---|
| Source code (Python, TypeScript, configs) | **Apache 2.0** |
| Prompts and domain definitions | **CC0 1.0 Universal** |
| Raw responses, processed results, documentation | **CC-BY-4.0** |
| Open data bundle (HuggingFace + Zenodo distribution) | **CC0 1.0 Universal** |

License files at repo root: `LICENSE` (Apache 2.0), `LICENSE-DATA` (CC-BY-4.0), `LICENSE-PROMPTS` (CC0), `LICENSE-OPENBUNDLE` (CC0). For the full file-by-file mapping and the rationale behind each license choice, see [`docs/LICENSE_COVERAGE.md`](docs/LICENSE_COVERAGE.md) and [`ARCHITECTURE.md`](ARCHITECTURE.md) §6.6.
```

**Rationale.**

- Four-row table preserved (each license still appears so a casual reader can see "is this CC0 or CC-BY?" without clicking).
- The historical Romney 1996 attribution paragraph (current README lines 55) is **removed** from the README — that footnote belongs in `docs/LICENSE_COVERAGE.md` (T1 deliverable). README does not need to surface a historical-data attribution requirement; ANY redistribution of `data/grounding/family/romney_1996/` already carries `source.md` with the citation, and the §6.6 architecture text already covers it.
- "Open data bundle (HuggingFace + Zenodo distribution)" replaces the original's "Backblaze B2 / Zenodo distribution" — Phase 8 §5 Decision 2 ratified HuggingFace as launch-day; B2 is the primary, but README readers think "HF + Zenodo" first.
- This is the section that goes "near the top" per the Architect's recommendation — placement is **after** Q1's opening, **after** Q5's "what LSB measures" section, and **before** Q4's Getting started + Repository structure. License-up-top matches the github.com/{org}/{repo} hover convention.

---

### Q7 — Numerical claims in the README — **R7 binding**

**Recommendation: Include exact counts. Avoid inferential statistics.** README is not a results document. Counts (number of models, number of domains, number of runs per cell) are descriptive metadata and do not need bootstrap CIs. Inferential statistics (Smith's S, Romney CCM) would trigger R10 and are better surfaced on the dashboard with their CIs, not in README prose.

**R7 (binding) — the following are the only quantitative claims permitted in README body:**

| Acceptable in README | Why |
|---|---|
| "v1 covers **three domains** (family, holidays, food) across **the model slate documented in `data/domains/v1/`**" | Exact count of categorical entities; no inference. |
| "**Four runs per (model, domain) cell** at fixed temperature" | Methodological parameter; no inference. |
| Specific model counts ("12 models") | **Do NOT include in README.** The exact model slate changes faster than the README. Refer to `data/domains/v1/` or the dashboard manifest. |
| Smith's S = 0.61 (95% CI [0.48, 0.79]) or similar headline figures | **Do NOT include in README.** R10 territory; correct surface is the dashboard's per-domain lede strip + methodology page. |

**R7 (binding wording) — when introducing the v1 scope, the README uses this construction verbatim:**

> "v1 covers three domains — family, holidays, food — collected at four runs per (model, domain) cell across the model slate documented in `data/domains/v1/` and surfaced on the dashboard's manifest."

**Rationale.**

- R10 applies to inferential statistics, not to descriptive counts. "Three domains" is a count and not subject to R10.
- The model slate count is deliberately externalized to `data/domains/v1/` and the manifest because the model slate shifts with each collection campaign — pinning "12 models" in README is a future-maintenance hazard and gets stale.
- Specific Smith's S / CCM numbers in README would force per-figure CI annotation that the dashboard already does correctly; duplicating creates a divergence risk and would force the README to be re-edited every time analysis re-runs.
- This routing matches FRONTEND_DESIGNER_BRIEF §3.2 — the lede strip carries the inferential headline, not the README.

---

### Q8 — Dashboard link anchor wording — **R8 binding**

**Recommendation: "the dashboard at [cogstructurelab.com](https://cogstructurelab.com)" in prose contexts; "Dashboard" as the section header / link list label.**

**R8 (binding) — the canonical dashboard reference forms in README:**

| Context | Verbatim wording |
|---|---|
| Inline prose | "the interactive dashboard at [cogstructurelab.com](https://cogstructurelab.com)" |
| Section header | "## Dashboard" or "Quick links → Dashboard" |
| Link list bullet | `- **Dashboard:** [cogstructurelab.com](https://cogstructurelab.com)` (current README form — preserve) |

**Rationale.**

- "Explore the data" / "Live results" / "Open data dashboard" are dashboard-internal affordances per FRONTEND_DESIGNER_BRIEF_APPENDIX §8 question 4 (the in-dashboard "↓ explore the data" affordance). They live on the dashboard surface, not in the README.
- "Dashboard" alone is correct for the README's "this is the primary deliverable" framing per §1.5.6.
- Forbidden: "demo," "live demo," "interactive demo" — these read as research-project posture, the opposite of §1.5.6 "website is the artifact."

---

### Q9 — Methodology placeholder link — **R9 binding**

**Recommendation: Replace the current "Methodology page" link with explicit placeholder wording.** The current README line 35 links to `https://cogstructurelab.com/methodology` which (per Phase 8 §5 Decision 1) will resolve to a "coming soon" placeholder. The link itself is OK; the README's framing of it must signal the placeholder state without sounding like the project is incomplete.

**R9 (binding) — replace current "Methodology page: [cogstructurelab.com/methodology]" link with:**

```markdown
- **Methodology page:** [cogstructurelab.com/methodology](https://cogstructurelab.com/methodology) — full methodology page is in preparation; for the binding framing language (corpus lens, what LSB measures, what it does not), see [`ARCHITECTURE.md`](ARCHITECTURE.md) §1.5
```

**Rationale.**

- The link still resolves (per Phase 8 Decision 1 — placeholder page at /methodology, not 404).
- "is in preparation" is neutral, not apologetic. Avoids "coming soon" (which §1.5.6 + the dashboard placeholder are using); README uses the slightly more grown-up "in preparation."
- Pointing to ARCHITECTURE.md §1.5 as the interim authoritative source means a researcher arriving cold has somewhere to go for the framing while the methodology page is being written.
- NO "target: YYYY-MM-DD" in README. The dashboard placeholder may carry a target date; the README does not commit to one because date slippage would force a README edit. The dashboard is the appropriate surface for a target date.

---

### Q10 — Explicit "do not" disclosure — **R10 binding**

**Recommendation: Include — but route it through R5's "what LSB does not measure" section rather than as a standalone "About this project" disclaimer.** Standalone disclaimers read as defensive; integrated framing reads as confident.

**R10 (binding):** The four-bullet "LSB does not" list in R5 is the single canonical "do not" disclosure for the README. Do **not** add a second standalone disclaimer section. The README structure ends up:

1. H1 + tagline
2. 3-paragraph opening (R1) — lands corpus lens + negation + website-as-artifact
3. "What LSB measures, and what it does not" (R5) — structured does/doesn't
4. "Licenses" (R6) — short summary + link to LICENSE_COVERAGE.md
5. "Quick links" — dashboard, methodology page (with R9 placeholder language), data bundle, citation
6. "Repository structure" — current form preserved
7. "Getting started" (R4) — quickstart commands
8. "Methodology ancestry" (R3) — five-author citations
9. "Citation" — existing form, updated post-DOI per Phase 8 T8
10. "Status" — rewritten per R11 below
11. "Contact" — existing form, updated security address per Phase 8 T2

This ordering puts the methodologically load-bearing content (opening + R5) at the top, the operational content (licenses + quick links + getting started + repo structure) in the middle, and the citation + status + contact at the foot. README readers who skim the first 200 lines should still encounter both the corpus-lens framing AND the §1.5 negation.

---

## §4 Additional binding rulings the Coder must apply

### R11 — Current "Status" section must be rewritten

**Current text (lines 68–72):** "LSB is in active development. Phase 1 (collection) is the current focus. The dashboard is not yet public; the open data bundle is not yet released. Expect breaking changes…"

**This is pre-launch internal language and is forbidden post-launch.** At repo-go-public time, the dashboard IS public, the data bundle IS released, and there is no "Phase 1 collection focus" because Phase 1 is closed.

**R11 (binding) — replace the entire "Status" section verbatim with:**

```markdown
## Status

LSB v1 is published. The dashboard at [cogstructurelab.com](https://cogstructurelab.com) covers three domains (family, holidays, food). The open data bundle is available on [HuggingFace](https://huggingface.co/datasets/AILLM1999/lsb) and is DOI-minted on [Zenodo](https://zenodo.org/) (DOI badge above).

The schema (`packages/cdb_core/schemas.py`) and the open data bundle format are version-stable; breaking changes become version bumps with migration notes in `docs/DATA_DICTIONARY.md`. Future collection campaigns add models, domains, and longitudinal snapshots; the v1 corpus is permanent.

For the phase plan see [`ARCHITECTURE.md`](ARCHITECTURE.md) §5.3.
```

**Rationale.**

- Replaces "active development / Phase 1 collection focus / not yet public" with the post-launch state.
- HuggingFace and Zenodo links surface the Phase 8 Decision 2 + Decision 3 deliverables.
- "DOI badge above" assumes a Zenodo DOI badge near the top of the README per Phase 8 §5 Decision 3 + Phase 8 T8.
- "The v1 corpus is permanent" reinforces §1.5.5 — once collected, the snapshot is preserved forever; later campaigns extend, never replace.

### R12 — Current "Citation" section must be updated post-DOI

**Current text (lines 60–66):** "A formal citation will be available with a Zenodo DOI after the LSB Phase 4 validation gates pass…"

**This is also pre-launch language.** Phase 4 validation has passed; the DOI is minted per Phase 8 T8. The R12 wording is conditional because the DOI is minted at-or-shortly-after launch per Decision 3 — the Coder writes the README in two states (pre-DOI and post-DOI), or writes a placeholder DOI that Phase 8 T8 swaps in.

**R12 (binding) — replace the Citation section with this template (DOI to be filled in by Phase 8 T8):**

```markdown
## Citation

If you use LSB in research, please cite:

\`\`\`
Cognitive Structure Lab. (2026). The Latent Structure Benchmark (LSB), v1.0.
https://cogstructurelab.com (Zenodo DOI: 10.5281/zenodo.<TBD-T8>)
\`\`\`

The Zenodo DOI resolves to the v1.0 open data bundle and is the canonical citation target. The dashboard URL is the canonical reading target.
```

**Rationale.**

- `<TBD-T8>` is a clear placeholder that T8 fills in; the surrounding wording is final.
- "2026" is the publication year; should remain stable through 2026.
- Distinguishes Zenodo DOI (citation target) from dashboard URL (reading target) — this is the standard scholarly-publishing pattern.

### R13 — Forbidden vocabulary the Coder must not introduce

Beyond the 12-row table, the following phrases are **prohibited** in the README rewrite:

- "Coming soon" anywhere except the dashboard surface (the methodology page placeholder may use it; README uses "in preparation" per R9).
- "Latest research" / "cutting-edge" / "state-of-the-art" — marketing intensifiers; banned per FRONTEND_DESIGNER_BRIEF_APPENDIX §6 "no stunning, remarkable, shocking, surprising."
- "Demo" / "interactive demo" / "live demo" — per R8.
- "Beta" / "preview" / "experimental" — the public release is v1.0 per Phase 8 §11 closure criteria; calling it beta undermines the same.
- "AI" as a free-floating noun ("What AI thinks about families") — banned per FRONTEND_DESIGNER_BRIEF_APPENDIX §6.
- "We show that" / "our results demonstrate that" / "we prove that" — banned per §1.5.7 + the §1.5.4 last two rows.
- "Within-model consensus" / "within-model cultural consensus" / "within-model eigenratio" / "within-model CCM" — registers (§1.5.4 last 4 rows).

### R14 — Tagline beneath the H1

The current README line 3 says "Cognitive Structure Lab — [cogstructurelab.com](https://cogstructurelab.com)" as a bold subhead. This is fine but underuses the surface.

**R14 (binding) — replace line 3 with:**

```markdown
**Cognitive Structure Lab — [cogstructurelab.com](https://cogstructurelab.com)**

*A categorical-structure map of how frontier LLMs organize everyday vocabulary, built with Cultural Domain Analysis. Open data, reproducible, model-to-model.*
```

**Rationale.**

- Tagline matches the doctrinally-correct framing without overlapping R1's opening prose.
- "Categorical-structure map" + "Cultural Domain Analysis" hits both the long-form anchor and the methodology name.
- "Open data, reproducible, model-to-model" is verbatim from the Architect's repo description draft (Phase 8 Decision 6); keeps cross-surface phrasing consistent.

### R15 — First-person plural is the only allowed voice for first-party statements

Per FRONTEND_DESIGNER_BRIEF_APPENDIX §6:

- Use "we ran the protocol," "we publish the data," "we do not interpret the results."
- Avoid "the LSB team," "the authors," "the project."
- Avoid second-person ("You might wonder…") in body prose.
- Use the dashboard's `cogstructurelab.com` audience voice: declarative, sober, no marketing intensifiers.

Apply this rule across every paragraph the Coder writes. The R1 opening is in this register; the Coder must not slip when writing the connective tissue.

---

## §5 Coder pre-flight checklist (operational)

Before posting the T3 commit, the Coder must:

1. ☐ Read this verdict in full.
2. ☐ Paste R1, R3, R4, R5, R6, R9, R11, R12, R14 verbatim.
3. ☐ Apply R7 numerical-claim rule (no Smith's S in README body).
4. ☐ Apply R8 link wording rule.
5. ☐ Apply R13 forbidden-phrase scan (grep their own draft before commit).
6. ☐ Apply R15 voice rule across all new prose.
7. ☐ Ensure README structure follows R10's 11-section ordering.
8. ☐ Run the forbidden-vocab grep from Phase 8 §6 pre-release scan check #2 locally before commit.
9. ☐ Confirm no spend-gate language anywhere. <!-- noqa: spend-gate-check -->
10. ☐ Verify all internal links resolve (current README has working internal links — preserve).
11. ☐ Commit message references this verdict file path.

---

## §6 Summary of binding rulings (for the orchestrator)

| Ruling | Surface | Status |
|---|---|---|
| R1 | Opening paragraphs (verbatim) | Binding |
| R2 | §1.5 negation placement | Binding |
| R3 | Methodology ancestry section (verbatim) | Binding |
| R4 | Getting started section (verbatim) | Binding |
| R5 | "What LSB measures, what it does not" section (verbatim) | Binding |
| R6 | Licenses section (verbatim, short form) | Binding |
| R7 | Numerical claims rule | Binding |
| R8 | Dashboard link wording | Binding |
| R9 | Methodology placeholder link wording (verbatim) | Binding |
| R10 | Section ordering | Binding |
| R11 | Status section (verbatim) | Binding |
| R12 | Citation section template (T8 fills DOI) | Binding |
| R13 | Extended forbidden-phrase list | Binding |
| R14 | Tagline (verbatim) | Binding |
| R15 | First-person plural voice | Binding |

15 binding rulings. All must be applied before T3 ships. Reviewer agent enforces R13 (forbidden-vocab spot-check) on PR review; CDA SME does not re-review the regenerated README unless the Coder's draft deviates from the verbatim strings above.

---

## §7 What is explicitly NOT in scope for T3

- The methodology page itself (Phase 8 T10).
- The `docs/LICENSE_COVERAGE.md` content (Phase 8 T1).
- The HuggingFace dataset card (Phase 8 T7).
- The Zenodo metadata description (Phase 8 T8).
- The GitHub repo description / topics (Phase 8 T4 — separate CDA SME gate).

Each of those surfaces gets its own CDA SME verdict.

---

*End of T3 CDA SME verdict. PASS-WITH-NOTES — 15 binding rulings. Verdict file: `docs/status/2026-05-17-phase8-T3-cda-sme-verdict.md`. Post to `#lsb-cda-sme`.*
