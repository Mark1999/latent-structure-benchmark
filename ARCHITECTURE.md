# Latent Structure Benchmark (LSB) — System Architecture

**Project name:** Latent Structure Benchmark (LSB)
**Public-facing site:** Cognitive Structure Lab — `cogstructurelab.com`
**Status:** Draft v0.7.1 — handoff document for the Claude Code development team
**Audience:** Architect / CDA SME / UI/UX / Coder / Reviewer / Tester agents + human reviewer (Mark)
**Companion docs:** `CDB_Briefing_Opus46.docx` (product vision), `CLAUDE.md` (team constitution), `DESIGN_SYSTEM.md` (binding for all frontend work), `SECURITY_AND_HARDENING.md`, `HOSTING_AND_DEV_OPS.md`, `PHASE_4C_CANDIDATE_SOURCES.md`, `PHASE_0_TASKS.md`, `docs/DATA_DICTIONARY.md` (Phase 1 deliverable)

**Changelog:**
- **v0.7.1** (patch, 2026-04-15) — Docs and operational alignment only, no schema or architecture changes. PR #2 (`6a21f69`) applied the F4–F8 docs/CI consistency pass: corrected VPS paths from `/home/lsb/lsb/` to `/opt/lsb-agent/`, renamed `GEMINI_API_KEY` to `GOOGLE_API_KEY` in discovery config and `.env.example`, regenerated the model registry. F1 VPS hardening completed outside git: dedicated `lsb` user created (uid 999), entire `/opt/lsb-agent/` tree chowned to `lsb:lsb`, `lsb-agent.service` updated to `User=lsb` with `ExecStart=/bin/false` (parked), root SSH login and password authentication disabled. Claude Code reinstalled under the `lsb` user at `/home/lsb/.local/bin/claude`. Companion docs (`HOSTING_AND_DEV_OPS.md`, `SECURITY_AND_HARDENING.md`) updated to reflect the new operational reality.
- **v0.7** reframes human grounding as a **per-domain optional slot that supports multiple baselines**, not a single-baseline-or-nothing fallback. Updates §1.5.5 and §4.2.5 so that "ungrounded" is a normal first-class state for any domain rather than a degraded mode. Generalizes `GroundingRef` in §3.2: adds `baseline_id`, `baseline_kind` (`published` | `researcher`), submitter fields, IRB status, and population description; changes `DomainResult.grounding` from a singleton to `list[GroundingRef]` with a `selected_baseline_id` for the default display. Restructures `data/grounding/{domain}/` into `data/grounding/{domain}/{baseline_id}/` to support multiple baselines per domain. Adds a v1 **researcher grounding submission workflow** via GitHub PR with a submission template — researchers contribute pile sort or free list data from human subjects via PR, LSB validates format and merges, the new baseline appears on the dashboard with full attribution (the researcher retains all rights). Adds a v2 design hook for an in-app submission form. Brings the architecture doc into alignment with `DESIGN_SYSTEM.md` v0.1: renames `TemporalView.tsx` → `DriftTracker.tsx` with a date slider (the design system collapses cross-version drift and longitudinal scrubbing into one component); adds `DomainSlider.tsx` as a distinct component from `DomainPicker.tsx` (pill buttons for navigation; slider for animated explorer transitions); aligns the §4.5 frontend section with the four grounding-display states from `DESIGN_SYSTEM.md` §4.1. Adds the **UI/UX agent** (Sonnet) to §5.1 as a new pipeline member sitting between CDA SME and Coder for frontend tasks only, with verdicts posted to `#lsb-ui-ux`. Adds new **§5.4 Agent Slack channels** documenting the three operational channels: `#lsb-alerts` (QA_Runner direct alerts, bypasses agent team), `#lsb-cda-sme` (CDA SME verdicts), `#lsb-ui-ux` (UI/UX agent verdicts). Adds `DESIGN_SYSTEM.md` to the CLAUDE.md reading list as item 14 — required reading before any frontend task. Glossary additions: baseline kinds (published / researcher), researcher grounding, DESIGN_SYSTEM.md, UI/UX agent, `#lsb-alerts` / `#lsb-cda-sme` / `#lsb-ui-ux`. The `TemporalView` glossary entry is replaced by an updated `DriftTracker` entry. Phase 6 plan now explicitly includes opening the researcher grounding submission process and merging the first external baseline if one is offered.
- **v0.6** introduces the **corpus lens** as the plain-language term for what LSB measures and adds it to §1.5.1 and the glossary. Adds five new binding commitments (#6–#10) to §1: no LLM in the analysis pipeline (LLMs are informants only, never analysts); cryptographic provenance on every collection run (provider request ID + SHA256 manifest); software-only QA with direct human alerting to `#lsb-alerts` that bypasses the agent team; open data for researchers (JSONL + SQLite + build script on Backblaze B2 under CC0); longitudinal model tracking with exact version strings, all runs retained, and a temporal dashboard view. Adds the **`InformantRecord`** Pydantic schema to §3.2 — the full subject record per collection run, including model identity, collection conditions, three CDA step records (`FreelistRecord`, `PileSortRecord`, `InterviewRecord`) with verbatim prompts and responses, SHA256 manifest, and QA verdict. Adds the **QA_Runner** (`scripts/qa_check.py`) as new §4.1.6 — a deterministic Python script that posts directly to `#lsb-alerts` on any failure, bypassing the agent team entirely. Adds a binding constraint at the top of §4.2: **no LLM calls permitted in `cdb_analyze`**, Reviewer must reject any PR introducing one. Updates §4.3 to describe three parallel result representations (JSONL canonical, SQLite researcher-friendly, Parquet analysis) with both JSONL and SQLite published as open data. Adds a **temporal view** to §4.5 — the longitudinal dashboard showing corpus lens shift across collection dates per model, using Procrustes drift score as the change metric. Adds an **Anthropic prompt caching** requirement to §6.2 for all static documents passed to agent API calls (~80% per-task cost reduction). Adds new **§6.7 Open Data Policy** describing what is and is not published, hosting on Backblaze B2, Zenodo DOI post-Phase-4 validation, and the researcher reproducibility guarantee. Adds the **CDA SME** agent (Opus) to §5.1 as the methodological gatekeeper between Architect and Coder, posting to `#lsb-cda-sme`. Glossary additions: corpus lens, InformantRecord, QA_Runner, temporal view, HuggingFace Inference Providers, open data, lsb-agent-01.
- **v0.5** removes Mac Mini / local mirror architecture. Phase 1a/1b split collapsed into unified Phase 1 using three API endpoints: Anthropic, OpenRouter, HuggingFace. Production URL corrected to cogstructurelab.com (.ai owned, will redirect). `collection_method` values updated accordingly.
- **v0.4** is the major revision following the 24-decision pass. Resolves all Open Decisions in §7. Renames the project from "CDB" to "Latent Structure Benchmark (LSB)" and introduces the website name "Cognitive Structure Lab" at `cogstructurelab.ai` (new §1.6). Collapses the FastAPI layer to static JSON files served by Cloudflare Pages — `cdb_api` is renamed to `cdb_publish` (new §4.4, repo layout §2 updated). Locks in the 12-model slate with three-axis filtering (origin, openness, collection method) and adds local mirror collection for open-weight models via the Mac Mini M5 Max post-June 2026 (§3.2 ModelRef schema, §4.1 collection layer, §5.3 Phase 1 split). Locks in family→holidays→food domain order, $300/mo spend cap with three-tier defense, 8-variant sensitivity study, Apache 2.0 / CC-BY-4.0 / CC0 licensing, Cloudflare Pages hosting, Backblaze B2 + fireproof safe backup, dedicated ProtonMail security contact, two YubiKey 5C NFC enrollment, friendly review pre-launch (no paid pentest). Adds Phase 0 tasks P0-T9 (security scaffolding) and P0-T10 (CSP and headers) per `SECURITY_AND_HARDENING.md`. The `LSB` abbreviation is used informally; the Least Significant Bit collision is acknowledged and accepted — full name "Latent Structure Benchmark" is canonical in citation contexts.
- v0.3.1 reframes §1.5.6 to lead with "the website is the artifact" positively rather than defining the project by what it doesn't ship. Adds explicit guidance on acknowledging academic forebears on the methodology page and elevates the methodology page to a first-class Phase 5/6 deliverable.
- v0.3 removes academic publication framing throughout. The project ships as a benchmark + dashboard + social pipeline + open data/code only. No ArXiv preprint, no methods paper, no journal submission. Phase 8 renamed and rescoped.
- v0.2.1 resolves grounding sourcing: licensed published data only, no original human collection in v1. Updates §4.2.5 and Phase 4c accordingly.
- v0.2 reframes the object of study (new §1.5), promotes Phase 4 to a quantitative Validation Phase (§5.3), adds a Human Grounding module to the analysis layer (§4.2.5), and requires bootstrap uncertainty in all visualizations (§4.5).

---

## 0. How to read this document

This is an **end-to-end architecture sketch**, not a final spec. Every section ends with either (a) concrete contracts the Coder agent can implement directly, or (b) an **Open Decisions** block that must be resolved with Mark before implementation. The Architect agent should walk section-by-section, not jump to code.

The guiding principle: **the benchmark is a data pipeline with a pretty face and a megaphone.** Data collection → analysis → storage → publish → visualization → distribution. Every layer is independently testable and independently replaceable.

---

## 1. System overview

```
┌──────────────────────────────────────────────────────────────────────┐
│              LATENT STRUCTURE BENCHMARK (LSB)                        │
│              served at cogstructurelab.com                           │
│                                                                      │
│  ┌───────────────┐    ┌──────────────┐    ┌─────────────────────┐    │
│  │  COLLECTION   │───▶│   ANALYSIS   │───▶│   RESULTS STORE     │    │
│  │ (Anthropic /  │    │ (MDS/clust./ │    │ (versioned JSON +   │    │
│  │ OpenRouter/HF)│    │  bootstrap)  │    │  Parquet + SQLite)  │    │
│  └───────┬───────┘    └──────────────┘    └──────────┬──────────┘    │
│          │                                           │               │
│          ▼                                           ▼               │
│  ┌───────────────┐                         ┌─────────────────────┐   │
│  │  RAW RESPONSE │                         │  PUBLISH LAYER      │   │
│  │  LAKE (JSONL) │                         │  (cdb_publish)      │   │
│  └───────────────┘                         │  static JSON build  │   │
│                                            └──────────┬──────────┘   │
│                                                       │              │
│                                                       ▼              │
│                                            ┌─────────────────────┐   │
│                                            │  REACT DASHBOARD    │   │
│                                            │  (D3 / Plotly)      │   │
│                                            │  Cloudflare Pages   │   │
│                                            └──────────┬──────────┘   │
│                                                       │              │
│                                                       ▼              │
│                                            ┌─────────────────────┐   │
│                                            │  SOCIAL AGENT       │   │
│                                            │  (Claude Code)      │   │
│                                            └─────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

**Core design commitments:**

1. **Raw-first, analysis-second.** Every model response is stored verbatim in an append-only JSONL lake before any analysis touches it. Analysis is always reproducible from raw data. Never overwrite raw.
2. **Content-addressable runs.** Every `(model, domain, protocol_step, prompt_version, run_index)` tuple produces a deterministic run ID. Re-running is cheap; cache hits are obvious.
3. **Offline analysis, static serving.** Analysis is a batch job that produces precomputed JSON artifacts. The dashboard fetches these JSON files directly from Cloudflare Pages — there is no runtime backend, no server-side LLM calls, no API to maintain. This keeps the public dashboard fast, free to host (Cloudflare Pages free tier), and immune to LLM rate limits and runtime failures.
4. **Versioned everything.** Prompts, analysis code, and results all carry semantic versions. A result from `prompt_v1.2 + analysis_v0.3` is a different object than `prompt_v1.2 + analysis_v0.4`.
5. **Small surface area.** The v1 LSB ships as a static React site fetching static JSON files. No database server, no auth, no user accounts, no runtime backend. Complexity earns its way in.
6. **No LLM in the analysis pipeline.** LLMs participate in this project as **informants only, never as analysts.** `cdb_analyze` is pure deterministic Python — sklearn, numpy, scipy, networkx. No model calls, no embeddings APIs, no "use Claude to summarize the matrix." The single exception is the lede generator in §4.2.3, which is an output formatter, not an analytical step, and which receives only already-computed numeric findings. The Reviewer agent must reject any PR that introduces an LLM call into `cdb_analyze`. Rationale: an analysis pipeline that depends on a black-box statistical artifact to interpret another black-box statistical artifact is not falsifiable. The whole point of LSB is to apply a transparent, auditable methodology to opaque models. Putting an opaque model inside the audit destroys the audit.
7. **Cryptographic provenance for every collection run.** Every `RawResponse` and every `InformantRecord` (§3.2) carries (a) the provider's request ID returned by the API, and (b) a SHA256 manifest covering the verbatim prompt, the verbatim response, and the request parameters. The manifest is computed at write time and stored alongside the raw record. Any later challenge to the data ("did you really get that response from that model on that date?") is answered by recomputing the SHA256 and comparing to the stored manifest. The provider request ID gives a second, independent audit path through the provider's own logs.
8. **Software-only QA with direct human alerting.** Quality control on collection runs is performed by `scripts/qa_check.py` (§4.1.6), a deterministic Python script with hardcoded thresholds. **The agent team is not in the QA loop.** When QA fails, the script posts directly to the `#lsb-alerts` Slack channel (which Mark monitors) and writes `qa_passed=False` on the affected `InformantRecord`. The agent team is bypassed entirely on the alert path because (a) QA failures are time-sensitive — a broken provider, a model that has been quietly deprecated, a sudden latency spike — and need a human in the loop within minutes, not whenever the next agent task happens to run, and (b) the agent team's job is to build the system, not to babysit it in production.
9. **Open data for researchers.** LSB publishes its full result set as open data under CC0. The published bundle contains: the canonical JSONL stream of `InformantRecord` objects, a SQLite database generated from that stream by `scripts/build_db.py`, the build script itself, the data dictionary (`docs/DATA_DICTIONARY.md`), and the prompt templates (already CC0 under §6.6). The bundle is hosted on Backblaze B2 and DOI-minted via Zenodo after the Phase 4 validation gates pass. See §6.7. The reproducibility guarantee is concrete: any researcher with the bundle and a Python environment can rebuild the SQLite database, re-run the analysis pipeline, and reproduce every figure on the dashboard.
10. **Longitudinal model tracking.** Models change. Anthropic ships `claude-opus-4-6` today and `claude-opus-4-7` next quarter; OpenAI silently rolls a new snapshot under the same alias; an open-weight model gets re-quantized. LSB tracks this explicitly. Every `InformantRecord` carries the **exact** provider model version string returned in the API response, not the user-supplied alias. **All historical runs are retained forever** — nothing is overwritten when a new version of a model is added. The dashboard exposes a **temporal view** (§4.5) showing how each model family's corpus lens shifts across collection dates, with Procrustes drift score as the change metric. This is a Phase 6 deliverable, but the data structure must support it from Phase 1, which is why the `InformantRecord` schema (§3.2) stores model version strings verbatim and the storage layout (§4.3) is append-only by collection date.

---

## 1.5 Scientific framing and known limitations

**This section is binding on every other part of the system.** The Reviewer agent must reject any prompt, lede template, dashboard copy, social post, or README text that contradicts it.

### 1.5.1 What CDB measures — the precise claim

CDB does **not** measure cultural worldviews. Worldviews require lived experience, and LLMs do not have lived experience. They synthesize statistical patterns from text corpora.

What CDB measures is:

> **The latent categorical structure of a training corpus, as refracted through a model's training and alignment pipeline, surfaced by applying Cultural Domain Analysis elicitation protocols to the model as if it were an informant.**

The plain-language term for this — the term used in social posts, headlines, dashboard copy aimed at non-specialists, and the methodology page's opening paragraph — is the **corpus lens**: the shape a model imposes on a domain, inherited from its training data. The corpus lens is what LSB measures. "Latent categorical structure of a training corpus, refracted through a model's training and alignment pipeline" is the methodologically precise version of the same idea; "corpus lens" is the version a journalist can put in a headline. Both are correct; they are not in tension.

The two phrasings have different jobs and different audiences:

| Audience | Use | Why |
|---|---|---|
| Methodology page, schema docs, citations | "latent categorical structure of a training corpus, refracted through training and alignment" | Defensible to a skeptical anthropologist or AI researcher; names the construct without overclaim |
| Headlines, social posts, dashboard copy, the lede on every visualization | "corpus lens" | Memorable, concrete, gets the idea across in two words to a journalist with five seconds |

The Reviewer agent enforces consistency: methodology contexts use the long form (or define the short form on first use); public-facing copy uses "corpus lens." Mixing — e.g., a methodology page that opens with "Models have a corpus lens" without the long-form anchor, or a social post that leads with "latent categorical structure" — is rejected.

Unpack the long form:

- **Latent categorical structure** — how items within a domain cluster and relate, not what items exist or whether facts about them are correct.
- **Of a training corpus** — the proximate object of study is the text the model learned from, not the humans who produced that text. Cultural signal reaches CDB only through the corpus.
- **As refracted through a model's training and alignment pipeline** — pretraining, RLHF, constitutional fine-tuning, and system prompts all bend the output. CDB sees the sum, not any single stage.
- **Surfaced by applying CDA protocols** — the methodology is imported from cognitive anthropology. That does not import the ontological commitments of cognitive anthropology along with it. We are borrowing a microscope, not claiming the sample is alive.
- **As if it were an informant** — the "as if" is load-bearing. Treating the model as an informant is a methodological move, not a metaphysical one.

**Four-layer breakdown of the corpus lens (added post-F1 SME review).** The "corpus lens" phrase compresses four distinct transformations. Naming them explicitly makes the construct operationally legible and clarifies what LSB does and does not observe:

1. **Co-occurrence patterns in the training corpus.** The substrate. Not directly observed by LSB; mostly opaque for frontier models.
2. **Compression and abstraction by pretraining** (next-token prediction). Reshapes raw co-occurrence into representations that serve sequence prediction. Not directly observed.
3. **Behavioral shaping by RLHF and constitutional fine-tuning.** Inserts preferences, safety training, and alignment objectives over the pretraining representation. Not directly observed.
4. **Surface expression through temperature-sampled token generation.** The only layer LSB actually observes. Every claim LSB makes about Layers 1–3 is inferential, not direct.

LSB elicitation operates on Layer 4. What it reveals about Layers 1–3 is a composed inference, not a measurement. This does not weaken the construct; it clarifies what it claims.

### 1.5.2 Why the reframe is stronger, not weaker

This framing is **more** defensible than "measures cultural worldview," not less. Three reasons:

1. **It is falsifiable.** Anyone can inspect the training corpus description, the prompts, and the raw responses. The chain of custody is auditable end to end.
2. **It is distinctive.** No other benchmark produces relational maps of training-corpus categorical structure. The novelty claim moves from contested ("measuring worldview") to uncontested (applying CDA to LLMs).
3. **It makes the interesting research question explicit.** The intellectual contribution is precisely: *what happens when you apply a methodology designed for cultural informants to a system that encodes culture without experiencing it?* The mismatch is the finding, not a flaw to hide.

### 1.5.3 Known limitations — surfaced, not buried

Every limitation below must appear on the public methodology page. The dashboard must link to it from every visualization.

1. **Prompt sensitivity.** Outputs vary with prompt wording. CDB addresses this by holding prompts fixed across models within a run and by running a formal sensitivity study (§5.3) before the dashboard goes public. Residual variance is quantified and displayed as uncertainty in every visualization (§4.5).
2. **English-only in v1.** The benchmark operates in English. Any cross-cultural claim is a claim about how the English-language training corpus represents other cultures, not about those cultures. v2 extends to other languages.
3. **Corpus opacity.** Training corpora for most frontier models are not public. CDB cannot attribute findings to specific data sources.
4. **Alignment confound.** Post-training (RLHF, constitutional AI, system prompts) reshapes model outputs. CDB cannot separate pretraining corpus structure from alignment-induced structure. Both are part of what the deployed model encodes, so this is a feature for product-level claims and a limitation for corpus-level claims.
5. **Temperature and sampling effects.** Stochastic decoding introduces run-to-run variance separate from prompt sensitivity. CDB controls this with fixed temperature per step (§4.1.3) and multi-run aggregation.
6. **Informant metaphor is metaphor.** The "as-if-informant" framing is methodological, not ontological. CDB does not claim models have cognition, culture, or experience.

### 1.5.4 Language guardrails

The following substitutions are enforced in all generated text (ledes, social posts, dashboard copy):

| Don't say | Say instead |
|---|---|
| "Model X believes..." | "Model X's output treats..." |
| "Model X thinks of family as..." | "Model X categorizes family terms as..." |
| "How models see the world" | "How models organize domain vocabulary" |
| "Model X's worldview" | "Model X's categorical structure" / "Model X's corpus lens" |
| "Cultural bias" (standalone) | "Categorical divergence from [baseline]" |
| "What the model understands" | "What the model's outputs pattern as" |
| "Within-model consensus" | "Representational coherence" / "Output Concentration Index (OCI)" |
| "Within-model cultural consensus" | "Output distribution analysis" |
| "Within-model eigenratio" | "Output Concentration Index (OCI)" |
| "Within-model CCM" | "Output distribution analysis" |

The last four rows (added post-F1 SME review) guard the boundary between **Register 1 (output distribution analysis)** and **Register 2 (cultural consensus analysis)** — see §4.2 for the register framework. Running the eigenratio machinery on N runs of a single model at fixed prompt does not produce a cultural consensus statistic; the rows of that agreement matrix are iid samples from one stochastic process, not distinct cultural agents, and the RWB assumptions do not hold. The measure (concentration of the model's output distribution on a domain) is real and useful; the name is what matters. Calling it "within-model consensus" imports assumptions that do not apply and will be rejected by the Reviewer.

The lede generator (§4.2.4) receives this table as part of its system prompt and must not produce text containing the left-column phrases. The Reviewer agent spot-checks a sample of generated ledes per release.

### 1.5.5 Human grounding — reference point, not target of measurement

**Framing reversal (post-F1 SME review).** An earlier version of this section framed human baselines as the *ceiling* for claim strength — treating "Model A sits closer to the 1996 Romney US human consensus than Model B" as a stronger claim than "Model A and Model B organize family terms differently from each other." That hierarchy imports an assumption from classical CDA that does not hold for LSB's research question. In classical CDA, human consensus is the ground truth because the object of measurement *is* human cultural knowledge. LSB is not measuring human cultural knowledge. It is measuring architectural differences between language models. Treating human consensus as the ceiling implicitly suggests that "closer to human = better," which is a claim LSB cannot and should not make.

**LSB's primary scientific claim is comparative across model architectures and across time.** Human baselines are **contextual reference points**, not the target of measurement. They participate in the cross-model analysis as a reference informant with a distinct visual marker, and they support an additional kind of claim (locating model outputs relative to a specific human cultural consensus), but they do not constitute the benchmark's success criterion. A domain with no human baseline is not a degraded domain; it is a normal, first-class state.

**Floor and ceiling claims, re-stated.**

> **Floor claim (no human baseline needed).** Model A and Model B organize this domain differently from each other.
>
> **Ceiling claim (human baseline present).** Model A sits closer to the 1996 Romney human consensus than Model B.
>
> The ceiling claim is valid and interesting — humans like to compare machines to themselves, and that comparison will be one output of the project. It is just not the primary research question. The primary question is cross-architecture comparison.

This phrasing appears verbatim on the public methodology page and is binding on any generated text that attempts to rank claim strength by grounding presence.

**What follows from this framing:**

1. **Grounding is a per-domain slot, not a project-wide property.** Some domains have published human CDA data (family terms — Romney et al. 1996); some domains have no published data anyone can find (holidays, food, justice, in v1); some domains will accumulate researcher-submitted data over time. Each of these is fine. The dashboard must handle all states gracefully — without empty states, broken layouts, or copy that treats ungrounded as broken. The four display states are specified in `DESIGN_SYSTEM.md` §4.1.

2. **A domain can have more than one baseline.** Family terms might have Romney 1996 (US college students, early 1990s) and a hypothetical Tanaka 2026 (Japanese university students, contemporary) at the same time. These are not in tension — they are two different human populations whose categorical structure is itself an interesting comparison. Both should be visible on the same MDS plot (with different markers) and the user should be able to toggle between them. The schema (§3.2) and storage layout (§4.2.5) are designed for this from the start, even though v1 will likely ship with only the Romney baseline.

3. **Researcher-contributed grounding is a v1 feature, not a v2 feature.** LSB exists in part to *connect to* the broader CDA research community — anthropologists and linguists running pile sort or free list studies on human subjects today should be able to drop their data into LSB and see it on the dashboard alongside the model results. The v1 contribution path is a GitHub PR with a submission template (§4.2.5); the in-app submission form is the v2 hook. Researchers retain all rights to their data; LSB validates format and provides attribution.

4. **Human baselines are Register-2 reference informants** (see §4.2 Three analytical registers). They enter the cross-model MDS with a distinct marker; they are not targets against which models are scored. Where a researcher submission includes per-subject raw data (`pile_sort_raw.csv`), the baseline can additionally be analyzed at Register 1 to produce a human Output Concentration Index (OCI) for cross-architecture comparison of human subject pools against models — a genuinely new cross-species claim of the form "this model's output concentration on kinship terms is within the range we observe across human subject pools." The `GroundingRef` schema carries a `human_oci` field for this purpose; it is populated when raw subject-level data is available and left null otherwise.

See §4.2.5 for the implementation and `DESIGN_SYSTEM.md` §4 for the visual treatment.

### 1.5.6 The website is the artifact

**The interactive dashboard is the primary deliverable of this project.** Everything else — the data collection pipeline, the analysis layer, the social-publishing agent, the open dataset, the methodology page — exists to make the website credible, useful, and discoverable. CDB is not a research project that happens to have a website; it is a website that happens to use research methods.

This shapes every other design decision:

- **The dashboard must be self-contained.** Visitors will not have read a paper before they arrive. The methodology page, the lede on each visualization, and the "explain this view" affordances together have to convey what CDB measures, how, and why it should be trusted — to a journalist, an AI engineer, or a curious researcher with five minutes.
- **Methodological rigor still matters, but the bar is "credible to a skeptical reader" not "publishable in *Nature*."** The §1.5 framing, the §5.3 validation gates, the §4.2.5 human grounding, and the §4.2.6 bootstrap uncertainty all exist so that a careful reader cannot easily knock the project over. They do not exist to clear peer review.
- **Academic forebears must be acknowledged on the website.** The methodology page names the CDA tradition explicitly, cites Romney, D'Andrade, Weller, Borgatti, and Batchelder by name, and links to the original papers (free where possible). This is not posturing — it is the project being honest about where its methods come from and giving readers a path back to the literature. CDB stands on the shoulders of cognitive anthropology; the website should say so plainly.
- **No paper, no preprint, no journal submission.** CDB does not ship to ArXiv, *Cognition*, *American Anthropologist*, or anywhere else. The Reviewer agent must reject any text — generated lede, social post, dashboard copy, README — that promises or implies a forthcoming paper.

**Implications for the build plan:**

- The methodology page is a Phase 5/6 deliverable in its own right, not an afterthought. It deserves a dedicated session with Mark personally writing or reviewing the prose. The Coder agent should not generate the methodology page from a template.
- Visual polish, copy quality, and load performance on the dashboard are first-class concerns, not nice-to-haves. The site is competing for attention against every other thing on the internet. If it looks like a research demo, it will be treated like one.
- The social pipeline (§4.6) is the dashboard's primary discovery mechanism. Without a paper to drive citation traffic, social posts are how people find the site. This is why the journalist affordances in §4.5 and the social pipeline in §4.6 are first-class features and not optional polish.

**"The mismatch is the finding" is the lead paragraph of the public methods page (binding, added post-F1 SME review).** §1.5.2 point 3 is the most intellectually honest framing of the project: *what happens when you apply a methodology designed for cultural informants to a system that encodes culture without experiencing it? The mismatch is the finding, not a flaw to hide.* Researchers who understand CDA will grasp what LSB is doing immediately; researchers who don't will be oriented by this framing. It is load-bearing for the project's defensibility and must not be buried in a late paragraph, a footnote, or a methods page's "limitations" section. Placement: the first paragraph of the public methods page, before any description of specific measures. The Reviewer agent rejects any methods-page draft that does not open with this framing.

## 1.6 Project naming

The project intentionally uses **two distinct names** for two distinct jobs. This is the standard pattern in the AI research space (LMSYS / Chatbot Arena / chat.lmsys.org; Stanford CRFM / HELM / crfm.stanford.edu/helm) and exists because the benchmark name and the website name have different optimization targets.

**Benchmark name: Latent Structure Benchmark (LSB).** This is the methodologically descriptive name used in citation contexts, methodology pages, schema fields, repository identifiers, and academic-style references. It is precise, defensible, and on-message with §1.5: it names what is actually measured (latent categorical structure) without overclaiming worldview, belief, or cognition. The full phrase "Latent Structure Benchmark" is canonical; "LSB" is the casual abbreviation. The Least Significant Bit / Linux Standard Base namespace collision on "LSB" is acknowledged and accepted — anyone confused by the abbreviation can disambiguate via the full name in two seconds, and the full name has no competing AI/ML benchmark currently using it.

**Website name: Cognitive Structure Lab.** This is the brandable, evocative name used on the public-facing site, in social posts, in headlines, and as the URL. It signals research seriousness ("Lab") while staying consistent with §1.5 vocabulary ("Cognitive Structure" rather than "Cognitive Worldview" or "Cognitive Belief"). The public site is served at **`cogstructurelab.com`**. The project also owns **`cogstructurelab.ai`**; that domain will redirect to **`cogstructurelab.com`** so legacy links and email-adjacent branding still resolve cleanly.

**Why the split:**

| Job | Benchmark name does it well | Website name does it well |
|---|---|---|
| Citation in academic-style references | ✓ "the Latent Structure Benchmark (LSB)" | ✗ "Cognitive Structure Lab" reads as an institution, not a measurement |
| Headline on a dashboard for casual visitors | ✗ "Latent Structure Benchmark" reads as dry | ✓ "Cognitive Structure Lab" reads as a place of inquiry |
| Methodology defense | ✓ Names the construct precisely | ✗ Brand names defend nothing |
| Memorability for journalists | ✗ Hard to remember as a phrase | ✓ Three short words, easy to type |
| URL discoverability | ✗ Long, ugly URL | ✓ Short, brandable `.com` (with `.ai` owned and redirecting) |

Forcing one name to do both jobs was the cause of multiple failed naming attempts during the v0.4 decision pass. The split unlocks both decisions simultaneously by letting each name optimize for its actual purpose.

**Binding implications for generated content:**

- The methodology page leads with "**Cognitive Structure Lab** publishes the **Latent Structure Benchmark (LSB)**, an evaluation that..." and uses both names appropriately throughout.
- Social posts use "Cognitive Structure Lab" for brand recognition and "Latent Structure Benchmark" or "LSB" when describing methodology specifics.
- Repository identifiers, package names, schema field names, and code-level references use `lsb_*` or descriptive English (not the website name). For backward compatibility with this document and prior planning, the `cdb_*` package prefixes from earlier drafts are retained — renaming packages is a future cleanup, not a v1 priority.
- The Reviewer agent enforces consistency: the website name appears on the site and in distribution; the benchmark name appears in methodology and citation contexts. Mixing them in inappropriate contexts (e.g., a methodology page that talks about "the Cognitive Structure Lab measurement of...") is rejected.

---

## 2. Repository layout

Monorepo. One repo, clear top-level separation. Designed so the Coder agent can work one directory at a time without cross-contamination.

```
cdb/
├── CLAUDE.md                      # team constitution (existing)
├── ARCHITECTURE.md                # this document
├── DESIGN_SYSTEM.md               # binding spec for all frontend work; UI/UX agent owns this
├── README.md                      # public-facing
├── docs/
│   ├── DATA_DICTIONARY.md         # field-by-field schema doc for the open data bundle (§6.7)
│   └── grounding_submission_template.md  # researcher submission template, §4.2.5 (Phase 6)
├── .claude/
│   └── agents/                    # Architect/CDA SME/UI-UX/Coder/Reviewer/Tester
├── .github/
│   └── PULL_REQUEST_TEMPLATE/
│       └── grounding_submission.md  # PR template for researcher grounding submissions, §4.2.5
├── pyproject.toml                 # uv-managed Python project
├── packages/
│   ├── cdb_core/                  # shared types, IDs, schemas
│   │   ├── ids.py                 # run_id hashing
│   │   ├── schemas.py             # pydantic models (contracts!)
│   │   └── versioning.py
│   ├── cdb_collect/               # data collection layer
│   │   ├── adapters/              # one file per provider
│   │   │   ├── base.py
│   │   │   ├── anthropic.py
│   │   │   ├── openai.py
│   │   │   ├── google.py
│   │   │   ├── openrouter.py      # frontier + open-weight via OpenRouter
│   │   │   └── huggingface.py     # Hugging Face Inference Providers (specialist open models)
│   │   ├── protocol/              # the CDA pipeline as code
│   │   │   ├── free_list.py
│   │   │   ├── pile_sort.py
│   │   │   └── pile_interview.py
│   │   ├── prompts/               # versioned prompt templates
│   │   │   └── v1/
│   │   │       ├── free_list.md
│   │   │       ├── pile_sort.md
│   │   │       └── interview.md
│   │   ├── domains/               # domain definitions
│   │   │   └── v1/
│   │   │       ├── family.yaml
│   │   │       ├── holidays.yaml
│   │   │       └── ...
│   │   └── runner.py              # orchestrator
│   ├── cdb_analyze/               # analysis layer (NO LLM CALLS — see §4.2)
│   │   ├── parse.py               # response → structured data
│   │   ├── cooccurrence.py        # pile sort → matrix
│   │   ├── mds.py                 # sklearn MDS
│   │   ├── cluster.py             # hierarchical clustering
│   │   ├── consensus.py           # cultural consensus analysis
│   │   ├── drift.py               # cross-version drift scoring
│   │   ├── grounding.py           # human CDA baseline loader (§4.2.5)
│   │   ├── bootstrap.py           # uncertainty via resampling (§4.2.6)
│   │   ├── sensitivity.py         # prompt-sensitivity study (§5.3)
│   │   └── pipeline.py            # end-to-end
│   ├── cdb_publish/                # static JSON build for the dashboard
│   │   ├── build.py                # writes JSON files to apps/dashboard/public/data/
│   │   ├── schemas/                # JSON Schema for dashboard contracts
│   │   └── README.md               # what each output file contains
│   └── cdb_social/                # social publishing pipeline
│       ├── triggers.py
│       ├── drafters/
│       └── queue.py
├── apps/
│   └── dashboard/                 # React + Vite frontend
│       ├── src/
│       │   ├── views/             # one file per viz type
│       │   │   ├── MDSPlot.tsx
│       │   │   ├── Heatmap.tsx
│       │   │   ├── FreeListCompare.tsx
│       │   │   ├── DriftTracker.tsx     # cross-version drift + longitudinal date-slider scrubbing (§4.5)
│       │   ├── components/
│       │   └── api/
│       └── package.json
├── data/
│   ├── raw/                       # JSONL lake, append-only, git-ignored
│   ├── processed/                 # Parquet artifacts per run
│   ├── grounding/                 # human CDA baselines, multi-baseline per domain, git-tracked
│   │   └── family/
│   │       └── romney_1996/       # one directory per baseline_id
│   │           ├── source.md      # citation, methodology, IRB status, year
│   │           ├── items.txt      # canonical item set
│   │           ├── cooccurrence.csv  # symmetric matrix
│   │           └── grounding_ref.json  # the GroundingRef as JSON
│   ├── results/                   # canonical processed JSON, source for cdb_publish
│   └── open_bundle/               # built by scripts/build_db.py — JSONL + SQLite for §6.7
├── scripts/                       # CLI entry points
│   ├── collect.py
│   ├── analyze.py
│   ├── publish.py                 # invokes cdb_publish.build
│   ├── qa_check.py                # deterministic QA, §4.1.6
│   ├── build_db.py                # JSONL → SQLite for the open data bundle, §6.7
│   └── cost_report.py             # weekly spend summary, see §6.2
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/                  # canned model responses
```

**Repository root files (not shown above for brevity):**

- `LICENSE` — Apache 2.0 (covers all source code)
- `LICENSE-DATA` — CC-BY-4.0 (covers everything in `data/`)
- `LICENSE-PROMPTS` — CC0 1.0 (covers `packages/cdb_collect/prompts/` and `domains/`)
- `LICENSE-OPENBUNDLE` — CC0 1.0 (covers the open data bundle in `data/open_bundle/`, see §6.7)
- `SECURITY.md` — vulnerability disclosure policy, see `SECURITY_AND_HARDENING.md` §6.5
- `CODEOWNERS` — branch protection enforcement (Mark as sole owner pre-launch)
- `.github/workflows/` — CI pipelines (lint, test, publish, security scans)
- `.github/dependabot.yml` — dependency update automation, see security doc §4
- `.gitleaks.toml` — secret scanning configuration, see security doc §3.4

See §6.6 for the licensing rationale and the file-by-file mapping, and §6.7 for the open data bundle details.

**Why this layout:** each `packages/cdb_*` module has a single responsibility and a clean contract (section 4). The Coder agent can be assigned one package at a time. The Reviewer agent enforces three boundary rules: `cdb_publish` never imports `cdb_collect` (publishing and collection must stay decoupled); the dashboard never imports any `cdb_*` Python package (the dashboard is a separate app that only consumes static JSON); `cdb_social` never writes to `data/raw/` or `data/processed/` (social-pipeline outputs go to a separate `out/social/` directory and never contaminate analysis artifacts). A fourth boundary rule was added in v0.6: **`cdb_analyze` may not import any LLM client library** (`anthropic`, `openai`, `google.generativeai`, `huggingface_hub.InferenceClient`, etc.). The Reviewer agent enforces this with a static import check on every PR. See §4.2 for the rationale.

---

## 3. Core data model

Defined once in `cdb_core/schemas.py` as pydantic models. Every other package imports from here. **The Reviewer agent should reject any PR that redefines these types elsewhere.**

### 3.1 Identifiers

```python
# cdb_core/ids.py
def run_id(model: str, domain: str, step: str,
           prompt_version: str, run_index: int) -> str:
    """Deterministic SHA256[:16] of the tuple. Stable across machines."""
```

### 3.2 Primary entities

```python
class ModelRef(BaseModel):
    provider: Literal["anthropic","openai","google","xai","cohere",
                       "openrouter","huggingface"]
    model_id: str             # exact API string, e.g. "claude-opus-4-6"
    family: str               # e.g. "claude", "gpt", "qwen", "llama"
    origin: Literal["us","eu","ca","cn","other"]  # ca = Canada (Cohere)
    open_weights: bool        # True if weights are publicly downloadable
    collection_method: Literal["anthropic_api","openrouter","huggingface"]  # which API surface collected this run
    quantization: str | None  # e.g. "q8_0", "q4_K_M", None for API
    release_date: date
    version_label: str        # for drift analysis, e.g. "4.6"
    source_notes: str = ""    # license nuances, mixed-openness cases, etc.

# Schema notes (binding for Coder and Reviewer agents):
# - collection_method records which of the three remote integration points
#   was used: Anthropic API, OpenRouter, or Hugging Face Inference Providers.
#   The same logical model may appear more than once if invoked through
#   different gateways; those rows differ by collection_method and/or
#   model_id string.
# - The open_weights field is a strict Boolean. License nuances (Llama's
#   commercial restrictions, Mistral's mixed open/closed model line, etc.)
#   are handled via source_notes rather than expanding the field into an
#   enum. If a model's openness is genuinely ambiguous, set open_weights
#   True if the weights are downloadable at all and document restrictions
#   in source_notes.
# - The quantization field is None when the provider does not expose a
#   meaningful quant label in the API response; set when HF or another path
#   returns an explicit precision tag useful for provenance.
# - origin covers four production regions plus "other"; the four regions
#   correspond to populated clusters in the v1 model slate (US, EU, Canada,
#   China). New origin values require an architecture decision, not an
#   ad-hoc schema bump.

class Domain(BaseModel):
    slug: str                 # "family", "holidays", ...
    version: str              # "v1"
    display_name: str
    prompt_seed: str          # the exact domain phrasing given to models
    truncation_k: int = 25    # free-list cutoff

class RawResponse(BaseModel):
    run_id: str
    model: ModelRef
    domain_slug: str
    step: Literal["free_list","pile_sort","pile_interview"]
    prompt_version: str
    run_index: int            # 0..N-1 for multi-run sampling
    timestamp: datetime
    request: dict             # full request payload
    response: dict            # full response payload
    latency_ms: int
    cost_usd: float | None

class FreeList(BaseModel):
    run_id: str
    model: ModelRef
    domain_slug: str
    items: list[str]          # parsed, normalized, deduped
    raw_order: list[str]      # preserves original order for salience

class PileSort(BaseModel):
    run_id: str
    model: ModelRef
    domain_slug: str
    items: list[str]
    piles: list[list[str]]    # each inner list = one pile
    pile_labels: list[str]    # from the interview step

class CooccurrenceMatrix(BaseModel):
    domain_slug: str
    model: ModelRef
    items: list[str]
    matrix: list[list[float]] # symmetric, diagonal = 1.0

class DomainResult(BaseModel):
    """The thing the API serves. One per (domain, analysis_version)."""
    domain_slug: str
    analysis_version: str
    models: list[ModelRef]
    free_lists: dict[str, FreeList]       # keyed by model_id
    mds_coordinates: dict[str, tuple[float,float]]
    mds_uncertainty: dict[str, BootstrapEllipse]  # per-model 95% ellipse, §4.2.6
    similarity_matrix: list[list[float]]  # model-to-model, ordered by models
    similarity_ci: list[list[tuple[float,float]]] # per-cell 95% CI, §4.2.6
    consensus_score: float
    consensus_ci: tuple[float, float]     # 95% CI from bootstrap
    groundings: list[GroundingRef] = []   # zero or more human baselines, §4.2.5.
                                          # An empty list means the domain is ungrounded —
                                          # this is a normal first-class state, not a fallback.
    selected_baseline_id: str | None = None  # which baseline the dashboard displays by
                                              # default. None when groundings is empty.
                                              # The user can toggle to any baseline in
                                              # the list via the UI (DESIGN_SYSTEM.md §3.7).
    generated_lede: str                   # the no-friction journalist headline
    generated_at: datetime

class BootstrapEllipse(BaseModel):
    center: tuple[float, float]
    semi_major: float
    semi_minor: float
    rotation_rad: float
    n_bootstrap: int

class GroundingRef(BaseModel):
    """
    A human CDA baseline treated as a virtual informant in the MDS plot.

    A domain can have zero, one, or many GroundingRef instances. Each instance
    represents one human population studied with the CDA protocol. The
    distinction between baseline kinds (published vs researcher-submitted) is
    encoded in `baseline_kind` and drives the visual treatment in
    DESIGN_SYSTEM.md §3.3 and §4.1 — published baselines render as black
    stars, researcher baselines as gray diamonds.
    """

    # ──────────── Identity ────────────
    baseline_id: str                      # stable slug, e.g. "romney_1996" or
                                          # "tanaka_2026_kyoto_kinship". Used in URLs,
                                          # filenames, and DomainResult.selected_baseline_id.
    baseline_kind: Literal["published", "researcher"]
    domain_slug: str                      # which LSB domain this baseline belongs to

    # ──────────── Source ────────────
    source_citation: str                  # full bibliographic citation (published)
                                          # or researcher attribution string
    source_url: str | None                # DOI, PMC link, or researcher project URL
    collected_year: int                   # year the human data was collected,
                                          # NOT the year of publication

    # ──────────── Population ────────────
    n_human_informants: int
    population_description: str           # free text, e.g. "US college students,
                                          # ages 18–22, n=122, recruited 1990–1991"

    # ──────────── Method ────────────
    method: str                           # e.g. "pairwise similarity judgments",
                                          # "pile sort (Romney protocol)", "free list + pile sort"
    irb_status: Literal["approved", "exempt", "not_applicable", "unknown"] = "unknown"
                                          # "approved" for contemporary research;
                                          # "not_applicable" for historical published data
                                          # whose ethics framework predates IRB review;
                                          # "unknown" only as a temporary state during PR review

    # ──────────── Submitter (researcher baselines only) ────────────
    submitter_name: str | None = None     # None for published baselines
    submitter_institution: str | None = None
    submitter_contact: str | None = None  # email or ORCID
    submission_date: date | None = None   # date the PR was merged into LSB

    # ──────────── Position in cultural space ────────────
    mds_coordinate: tuple[float, float]
    mds_uncertainty: BootstrapEllipse | None = None
                                          # set only when raw subject-level data is
                                          # available (most published baselines provide
                                          # only the aggregate matrix and so have None;
                                          # researcher submissions that include per-subject
                                          # pile assignments do get a bootstrap ellipse)
    distance_to_nearest_model: float
    nearest_model_id: str

    # ──────────── Item-set alignment ────────────
    item_intersection_size: int           # number of items shared between this human
                                          # baseline and the LSB v1 item set for the domain
    item_intersection_total: int          # size of the LSB v1 item set
                                          # (intersection_size / total = coverage ratio,
                                          # displayed in DESIGN_SYSTEM.md §4.2 grounding panel)
```

#### InformantRecord — the per-run subject record (added v0.6)

`InformantRecord` is the **canonical full record** of a single LLM-as-informant run. It captures everything an outside researcher would need to reproduce, audit, or challenge that run: who the informant was, under what conditions it was queried, the verbatim prompts and responses for all three CDA steps, the parsed outputs, the cryptographic provenance, and the QA verdict. One `InformantRecord` per `(model, domain, run_index)` tuple. The append-only JSONL stream of `InformantRecord` objects is the canonical raw data of LSB and the primary content of the open data bundle (§6.7).

`InformantRecord` is a *richer* object than `RawResponse`. `RawResponse` is the per-API-call atom; `InformantRecord` is the per-informant aggregation across all three CDA steps for one `(model, domain, run_index)`. Both are kept — `RawResponse` for low-level debugging and replay, `InformantRecord` for analysis and publication.

```python
class FreelistRecord(BaseModel):
    """CDA Step 1 record — free listing."""
    prompt_verbatim: str          # the exact text sent to the model, post-template substitution
    prompt_version: str           # e.g. "v1"
    response_verbatim: str        # the exact text returned by the model
    response_object_json: dict    # full provider response object, including all metadata fields
    input_tokens: int
    output_tokens: int
    latency_ms: int
    stop_reason: str              # provider-reported stop reason (end_turn, max_tokens, etc.)
    parsed_items: list[str]       # post-parser, post-normalization
    parsed_raw_order: list[str]   # pre-truncation order, for salience analysis

class PileSortRecord(BaseModel):
    """CDA Step 2 record — pile sorting."""
    prompt_verbatim: str
    prompt_version: str
    response_verbatim: str
    response_object_json: dict
    input_tokens: int
    output_tokens: int
    latency_ms: int
    stop_reason: str
    parsed_piles: list[list[str]]         # each inner list is one pile
    parsed_matrix: list[list[int]]        # binary item×item co-occurrence (symmetric, 0/1)

class InterviewRecord(BaseModel):
    """CDA Step 3 record — pile interview / naming."""
    prompt_verbatim: str
    prompt_version: str
    response_verbatim: str
    response_object_json: dict
    input_tokens: int
    output_tokens: int
    latency_ms: int
    stop_reason: str
    parsed_pile_labels: list[str]         # one label per pile, in pile order

class InformantRecord(BaseModel):
    """
    Full subject record for one LLM-as-informant run on one domain.

    One InformantRecord per (model, domain, run_index). Append-only — never
    overwritten. This is the canonical raw data of LSB and the primary
    content of the open data bundle (see §6.7).

    Provenance: every InformantRecord carries the provider's request ID
    (independent audit path through the provider's logs) and a SHA256
    manifest covering the verbatim prompts and verbatim responses
    (cryptographic audit path through the local data). See §1 commitment 7.
    """

    # ──────────── Identity ────────────
    informant_id: str                     # SHA256[:16] of (model_id, domain, run_index, collection_date)
    domain_slug: str
    run_index: int                        # 0..N-1
    collection_date: datetime

    # ──────────── Model identity ────────────
    model_id: str                         # the exact API model string (provider-canonical, e.g. "claude-opus-4-6")
    model_version_returned: str           # the EXACT version string returned by the API in the response
                                          # (may differ from model_id when providers silently roll snapshots)
    family: str
    provider: Literal["anthropic","openai","google","xai","cohere",
                       "openrouter","huggingface"]
    provider_request_id: str              # provider-issued request ID (Anthropic: x-request-id; OpenAI: id; etc.)
    knowledge_cutoff: date | None         # provider-declared training cutoff, if known
    open_weights: bool
    origin_country: Literal["us","eu","ca","cn","other"]
    alignment_method: str | None          # free text — "RLHF", "Constitutional AI", "DPO", "unknown", etc.

    # ──────────── Collection conditions ────────────
    collection_method: Literal["anthropic_api","openrouter","huggingface"]
    api_endpoint: str                     # full URL of the endpoint actually called
    api_version: str                      # provider API version header (e.g. "2023-06-01" for Anthropic)
    temperature: float
    top_p: float | None
    max_tokens: int
    system_prompt: str                    # verbatim system prompt used for ALL three steps in this run

    # ──────────── CDA step records ────────────
    freelist: FreelistRecord
    pile_sort: PileSortRecord
    interview: InterviewRecord

    # ──────────── Provenance ────────────
    sha256_manifest: dict[str, str]       # keys: "freelist_prompt", "freelist_response",
                                          #       "pilesort_prompt", "pilesort_response",
                                          #       "interview_prompt", "interview_response",
                                          #       "request_params", "informant_record_total"
                                          # values: hex SHA256 digests

    # ──────────── QA ────────────
    qa_passed: bool                       # set by scripts/qa_check.py (§4.1.6)
    qa_notes: str = ""                    # free text — failure reasons, threshold values, manual overrides
```

Notes:
- `DomainResult` is **the only type the frontend ever sees.** Everything upstream is an implementation detail.
- `mds_coordinates` here is **model-to-model** (the signature viz: models as points in cultural space). A second, per-domain **item-to-item** MDS lives in `FreeList`/`CooccurrenceMatrix` for the within-domain cognitive map. Keep these distinct — conflating them is the #1 likely bug.
- `InformantRecord` is the open-data atom. The Reviewer agent must reject any change to `InformantRecord` that drops a field, renames an existing field, or weakens a verbatim-storage requirement — these are breaking changes for downstream researchers and the published data dictionary (`docs/DATA_DICTIONARY.md`). Adding new optional fields is fine.
- `model_version_returned` exists because the user-supplied `model_id` (e.g., `gpt-4o`) is sometimes a moving alias under which the provider silently rolls a new snapshot. The version string the provider includes in its response is the only reliable longitudinal anchor. The temporal view (§4.5) uses this field, not `model_id`, as the unit of analysis when computing per-model drift over time.

---

## 4. Layer-by-layer architecture

### 4.1 Data collection layer (`cdb_collect`)

**Responsibility:** turn a `(ModelRef, Domain)` pair into a set of `RawResponse` records on disk, plus one `InformantRecord` per `(model, domain, run_index)` tuple. Nothing else.

#### 4.1.1 The CDA protocol as code

The three-step pipeline from the briefing is implemented as three executable modules with strict output contracts.

**Step 1: Free listing** (`protocol/free_list.py`)

```
Input:  ModelRef, Domain, run_index
Prompt: prompts/v1/free_list.md with {{domain_seed}} substituted
Output: RawResponse + parsed FreeList
```

Example prompt template (`prompts/v1/free_list.md`):
```
You are participating in a cognitive anthropology study. Please list every
{{domain_seed}} you can think of. Do not stop early. Do not explain or
categorize. Just produce a numbered list, one item per line. Aim for at
least 30 items if you can.
```

Parser normalizes: lowercase, strip punctuation, collapse whitespace, dedupe preserving first-occurrence order. Truncate to `domain.truncation_k` most salient (first-mentioned) items before moving to Step 2.

**Step 2: Pile sorting** (`protocol/pile_sort.py`)

The model receives the truncated salient list from Step 1 **from the same run** and is asked to sort it.

```
Prompt: prompts/v1/pile_sort.md with {{items}} substituted
Constraint: response must be valid JSON matching {piles: [[str, ...], ...]}
```

Use structured output / JSON mode where available (Anthropic, OpenAI, Gemini, OpenRouter, Hugging Face Inference Providers for most). For models without JSON mode, use a robust parser + retry-on-parse-failure up to 3 attempts.

**Step 3: Pile interview** (`protocol/pile_interview.py`)

For each pile from Step 2, ask the model to name it. This is the step that distinguishes CDB from naive similarity benchmarks — the label reveals the *organizing principle*.

#### 4.1.2 Adapter pattern

```python
# cdb_collect/adapters/base.py
class ModelAdapter(Protocol):
    model: ModelRef
    async def complete(self, prompt: str, *,
                       json_schema: dict | None = None,
                       temperature: float = 0.7) -> AdapterResult: ...
```

One adapter per provider. All adapters return a uniform `AdapterResult` containing raw response, latency, cost, and the normalized text. The runner never sees provider-specific types. Adapters are also responsible for surfacing the provider-issued request ID and the verbatim response object so that the runner can populate `InformantRecord.provider_request_id` and the per-step `response_object_json` fields.

**Concurrency:** `asyncio` with per-provider semaphores to respect rate limits. Default 3 concurrent per provider, configurable per adapter.

**Retry policy:** exponential backoff on 429/5xx, max 5 retries. Failed runs are written to `data/raw/failures.jsonl` for inspection — they are *not* silently dropped.

#### 4.1.3 Sampling strategy

The briefing mentions "multiple runs per model per domain to distinguish signal from prompt sensitivity noise." Concretely:

- **Default:** `N=5` runs per `(model, domain, step)` tuple.
- **Temperature:** 0.7 for free listing (we want variance to surface salience distribution), 0.3 for pile sorting (we want the model's modal categorization).
- **Seed variation:** where the provider supports it, use distinct seeds per run. Where it doesn't, variance comes from sampling temperature alone.
- **Prompt-sensitivity study (Phase 4b validation gate):** 8 prompt variants per step on 2 reference models (Claude Opus + GPT flagship) to estimate within-model variance for the G1 gate (§5.3). Cost is bounded — see §6.2 for the spend cap mechanics.
- **Extended sensitivity (optional):** 16–32 prompt variants on selected open-weight models via OpenRouter and/or Hugging Face Inference Providers within the monthly spend cap — useful for comparing provider-routing variance without any local inference layer.
- **Spend cap.** Collection runs honor a hard monthly cap (default `CDB_MAX_SPEND_USD=300`) and halt cleanly when reached. See §6.2 for the three-tier defense (runtime cap, per-provider account caps, weekly cost reports).

At analysis time, per-run data is aggregated into a consensus free list and a consensus co-occurrence matrix per `(model, domain)`. This is the standard CDA move when multiple informants (here, runs) represent the same "culture" (here, the model).

#### 4.1.4 CLI

```bash
# run full collection for one domain across all configured models
python scripts/collect.py --domain family --runs 5

# run one model only (for debugging or adding a new model)
python scripts/collect.py --model claude-opus-4-6 --domain family

# dry-run — prints what would be called, no API hits
python scripts/collect.py --domain family --dry-run

# show current month's spend without collecting
python scripts/cost_report.py --month current
```

#### 4.1.5 Open decisions

**RESOLVED in v0.4 / v0.5.** Phase 1 collection uses three remote API surfaces only (Anthropic, OpenRouter, Hugging Face Inference Providers) on project VPS — no Mac Mini and no local Ollama mirror (v0.5). See §7 for the resolved-decisions log; `ModelRef.collection_method` values are `anthropic_api`, `openrouter`, and `huggingface`.

#### 4.1.6 QA_Runner (`scripts/qa_check.py`) — added v0.6

**Responsibility:** validate every freshly collected `InformantRecord` against a fixed set of deterministic checks. Set `qa_passed=False` and post directly to `#lsb-alerts` on any failure. **The agent team is bypassed entirely on the alert path** — see commitment #8 in §1. The QA_Runner is the operational watchdog; the agent team is the development team. Mixing them would slow down both.

**Implementation profile:**

- A single Python script: `scripts/qa_check.py`. Pure stdlib + `requests` for the Slack webhook + `pydantic` for record validation. No async, no Celery, no LLM calls.
- Invoked automatically by `scripts/collect.py` after each `InformantRecord` is written, and invokable manually for backfills (`python scripts/qa_check.py --since 2026-04-01`).
- Hardcoded thresholds at the top of the file with comments explaining each one. Tuning the thresholds is an architecture decision, not a config change.
- Slack webhook URL read from `LSB_ALERTS_WEBHOOK_URL` in `.env`. Never committed.

**Deterministic checks (all six must pass for `qa_passed=True`):**

| # | Check | Threshold | Failure mode |
|---|---|---|---|
| 1 | Free-list item count | `len(freelist.parsed_items) >= 10` | Model produced too few items — likely truncation or refusal |
| 2 | Free-list uniqueness across runs | Across the N runs for `(model, domain)`, the union of all parsed item lists must contain at least 60% of the items as unique (i.e., < 40% perfect overlap). Below that, the model is producing rote output and the variance estimate is invalid. | Model is regurgitating a memorized list rather than generating |
| 3 | Pile-sort matrix is binary | Every cell in `pile_sort.parsed_matrix` is exactly `0` or `1` | Parser bug or model produced fractional similarity by mistake |
| 4 | Pile-sort matrix is symmetric | `matrix[i][j] == matrix[j][i]` for all `i, j` | Parser bug — pile assignments are inherently symmetric, so asymmetry means broken parse |
| 5 | Latency sane | `freelist.latency_ms < 30000` and same for pile_sort and interview | Provider is degraded; data is still kept but flagged for review |
| 6 | Output token count consistent with response length | `output_tokens` reported by the provider should be within ±10% of `len(response_verbatim) / 4` (rough chars-per-token heuristic). | Provider is misreporting usage; downstream cost tracking is unreliable |
| 7 | Provider request ID present | `provider_request_id` is non-empty | Adapter failed to surface the provider's request ID — provenance is broken |

Any failure sets `qa_passed=False`, writes the failure reason to `qa_notes`, and posts a structured message to `#lsb-alerts` containing: `informant_id`, `model_id`, `model_version_returned`, the failed check number, the threshold, the actual value, and a link to the raw record in `data/raw/`. **The post goes directly to Slack — it does not enqueue an agent task, does not file a GitHub issue, and does not block the collection run.** Collection continues; the bad record is retained (with `qa_passed=False`) so that the failure itself is part of the audit trail.

**Why this is software-only and bypasses the agents.** A QA system that depends on an LLM to interpret the output of an LLM is not really a QA system. The whole point of QA on a benchmark like LSB is to have a layer of the pipeline that is *boring*, *deterministic*, and *fast*. Hardcoding the thresholds in a Python script means anyone — Mark, a future researcher, an auditor — can read the file in five minutes and know exactly what passes and what doesn't. Routing alerts directly to a human channel means QA failures get attention in minutes, not whenever the next agent session happens to run. The agents build the system; QA watches the system.

**Why the alerts bypass the agent team specifically.** QA failures are a different category from development tasks. A development task takes hours to days and is appropriate for the Architect→CDA SME→Coder→Reviewer→Tester flow. A QA failure ("the new GPT-5 snapshot is producing 6-item free lists, every run, since this morning") needs Mark to look at it now and decide whether to pause collection, switch models, or open a ticket with the provider. Routing it through the agent team adds latency and indirection without adding value. The agent team's pull-from-Slack pattern is for project work; the QA bypass is for operational firefighting.

---

### 4.2 Analysis layer (`cdb_analyze`)

**Binding constraint (added v0.6): no LLM calls permitted in `cdb_analyze`.** The analysis layer is pure deterministic Python — sklearn, numpy, scipy, pandas, networkx. No `anthropic` client, no `openai` client, no `google.generativeai`, no `huggingface_hub.InferenceClient`, no embeddings APIs, no "use Claude to summarize the cluster structure," no "use a small model to label the piles." LLMs participate in LSB as informants in `cdb_collect`; they do not participate as analysts in `cdb_analyze`. This is design commitment #6 in §1, and the Reviewer agent **must reject any PR introducing such a call**, including PRs that wrap an LLM call inside a helper function, a utility module, or a "just for the lede" exception. The lede generator (§4.2.3) is the only LLM call in the entire pipeline downstream of collection, and it lives in `cdb_publish` — *not* in `cdb_analyze` — precisely to keep this boundary visible. The Reviewer's static check on `cdb_analyze` imports (per §2 boundary rule four) is the enforcement mechanism.

**Responsibility:** turn raw responses into `DomainResult` artifacts. Pure functions, no I/O except reading raw JSONL and writing processed Parquet.

#### 4.2.0 Three analytical registers (added post-F1 SME review)

LSB operates three distinct analytical registers, each with different statistical assumptions. Keeping these registers distinct — in code, documentation, and dashboard copy — is what prevents the methodological confusion of importing classical CDA assumptions into settings where they do not apply. Each register has its own measures, its own assumptions, its own vocabulary, and its own claims. They inform each other; they are not the same analysis.

**Register 1 — Output distribution analysis (within-model):**

- **R1a: Sampling concentration (OCI)** — N runs, fixed prompt, temperature-driven variance.
- **R1b: Prompt robustness** — fixed model, 8+ prompt variants, G1 diagnostics (§5.3).
- **Statistical framework:** output concentration statistics. **RWB assumptions do not apply.** The rows of a run × item agreement matrix at R1a are iid samples from one stochastic process, not distinct cultural agents; therefore the eigenratio on such a matrix is a concentration statistic, not a cultural consensus statistic. The canonical name for the R1a eigenratio is the **Output Concentration Index (OCI)**. See §1.5.4 for the forbidden vocabulary that guards this boundary.

**Register 2 — Categorical structure analysis (between-model):**

- **Informants:** each model contributes equal voice via the consensus free list produced from its Level 1 (Option A input — see §4.2.7 two-level pipeline). All models contribute equally regardless of their OCI.
- **Human grounding:** injected as a **reference informant** with a distinct visual marker (per `DESIGN_SYSTEM.md` §3.3), consistent with §4.2.5. Humans participate in the cross-model analysis; they are not the target of measurement (§1.5.5).
- **Statistical framework:** RWB cultural consensus analysis with the LSB caveats from `docs/SME_REVIEW.md` (small-n regime, non-human informants, dual threshold λ₁/λ₂ > 5.0 operational / 3.0 reported).
- **Dashboard display representation:** Option B (centroid run) for tooltips and model profile pages — a concrete, human-readable free list drawn from the single run closest to the model's central tendency. Option A (pooled consensus) is the analytical input; Option B is the display.

**Register 3 — Longitudinal drift analysis (cross-version):**

- Procrustes distance across model versions on shared item sets (`drift.py`).
- No classical CDA equivalent — this is a new analytical framework enabled by the fact that LLM "informants" can be re-queried indefinitely in ways human informants cannot.

**Methods adaptation table (public methodology page — binding).** Add to the public methods page and keep in lockstep with this section. This table is the clearest statement of what LSB is doing and why it is methodologically legitimate rather than a naive application of human methods to a non-human subject:

| Human CDA assumption | LLM reality | LSB adaptation |
|---|---|---|
| List length bounded by memory fatigue | Unbounded; limited by context window | Protocol ceiling with capacity-truncation as a named finding type (§3.2 `InformantRecord`) |
| N informants are independent agents | N runs are draws from the same stochastic process | Prompt/temperature variation as variance source; RWB CCM applied at Register 2 only, as a convergence test rather than an assumption |
| Card deck independent of informants | Same entity class generates deck and sorts | Cross-model pooled deck (`consensus.compute_cross_model_consensus`); reflexivity treated as signal to scrutinize, not a confound to hide |
| Pile sort is physical manipulation | JSON output only | Pile count variance and pile-label consistency as structural proxies |
| Pile interview captures indigenous reasoning | Model labels its own piles | Pile labels as first-class architectural discriminator |
| Longitudinal = cross-cohort human study | Longitudinal = version drift within model family | Procrustes drift as new temporal measure (Register 3) |
| Consensus = shared cultural knowledge | Consensus = convergent representation across training corpora | RWB applied as an architectural test at Register 2, not as cultural validation |
| Single-level analysis (informants as units) | N runs per model *and* N models per benchmark available cheaply | Two-level design: Register 1 within-model + Register 2 between-model (§4.2.7) |

**"The mismatch is the finding."** Both §1.5.2 point 3 and §1.5.6 make this point; it is restated here because it is the single most important framing for the public methods page and for generated text that accompanies any visualization. The intellectual contribution of LSB is precisely that importing a methodology designed for cultural informants into a system that encodes culture without experiencing it *is* the research question. The three-register framework above is how that question is operationalized without methodological confusion.

#### 4.2.1 Pipeline stages

```
raw JSONL
   │
   ▼
parse.py          # text → FreeList / PileSort (per run)
   │
   ▼
aggregate.py      # N runs per model → consensus free list + consensus piles
   │
   ▼
cooccurrence.py   # piles → item×item matrix (per model)
   │
   ▼
mds.py            # two separate MDS computations:
   │                (a) item×item per model → within-domain cognitive map
   │                (b) model×model → cross-model cultural space
   ▼
cluster.py        # hierarchical clustering on (b) for the dendrogram
   │
   ▼
consensus.py      # cultural consensus score (Romney/Weller/Batchelder)
   │
   ▼
drift.py          # compare to prior model versions
   │
   ▼
DomainResult → data/results/{domain}/{analysis_version}.json
```

#### 4.2.2 Key algorithms

- **Co-occurrence matrix:** for each pair of items, count the fraction of runs in which they appear in the same pile. Diagonal = 1.0. Symmetric.
- **Cross-model similarity:** Mantel-style correlation between two models' co-occurrence matrices on the shared item set. Range [-1, 1], displayed as [0, 1] after rescaling.
- **MDS:** `sklearn.manifold.MDS(n_components=2, dissimilarity='precomputed')`. Use `1 - similarity` as dissimilarity.
- **Consensus analysis:** minimum residual factor analysis on the informant×item agreement matrix. Ratio of first to second eigenvalue > 3 indicates a single shared culture. Below 3 suggests sub-cultures (i.e., the models don't agree on one worldview — which is itself a finding).
- **Drift:** Procrustes distance between MDS coordinates of two versions of the same model family, after aligning their shared item sets.

#### 4.2.3 Lede generation

The "no-friction journalist" feature: every `DomainResult` carries a pre-written one-sentence lede. This is generated by calling Claude (Opus 4.6, the most capable available) with the numeric findings and asking for a single declarative sentence. Cache by `(domain, analysis_version)` — regenerate only on version bump.

The prompt template lives in `prompts/v1/lede.md` and is versioned along with everything else. **The lede generator receives the §1.5.4 language guardrails table as part of its system prompt and must not produce text containing the forbidden phrases.** Reviewer agent spot-checks a sample per release.

**Note on the §4.2 binding constraint:** the lede generator is the *only* LLM call downstream of collection in the entire LSB pipeline, and it deliberately lives in `cdb_publish`, not in `cdb_analyze`. It receives only already-computed numeric findings — never raw responses, never piles, never matrices the model could re-interpret. It is an output formatter, not an analytical step. The Reviewer must reject any attempt to relocate the lede generator into `cdb_analyze`, or to broaden its inputs to include analytic intermediates.

#### 4.2.4 CLI

```bash
python scripts/analyze.py --domain family --analysis-version 0.1
python scripts/analyze.py --all --analysis-version 0.1
```

Idempotent. Running twice with the same version produces byte-identical output (modulo timestamps).

#### 4.2.5 Human grounding module (`grounding.py`)

**Why this exists:** human CDA baselines are **reference points** in the Register 2 (between-model) analysis — not the target of measurement. The primary scientific claim of LSB is comparative across model architectures and across time (§1.5.5); human comparison is secondary. Where human CDA data is available, a baseline enters the cross-model MDS as a reference informant with a distinct visual marker, which enables an additional kind of claim (locating model outputs relative to a specific human cultural consensus) without redefining the benchmark's success criterion. Where no baseline is available, the benchmark makes model-to-model comparative claims only — a normal first-class state, not a degraded one.

**What it does:** loads zero or more published or researcher-submitted human CDA datasets from `data/grounding/{domain}/{baseline_id}/` and injects each as a reference informant labeled by `baseline_id`. Each baseline appears in the MDS plot as a distinct marker — published baselines as black stars (★), researcher baselines as gray diamonds (◆), per `DESIGN_SYSTEM.md` §3.3 — and in the similarity heatmap as reference rows/columns. **A domain may have zero, one, or many baselines, and zero is a normal state.**

**Human OCI (post-F1 SME review).** Where a researcher submission includes per-subject raw pile-sort data (`pile_sort_raw.csv`), the baseline can additionally be analyzed at Register 1 (§4.2.0) to produce a **human Output Concentration Index** — a measure of how concentrated that specific human subject pool's output distribution is on the domain. The `GroundingRef.human_oci` field carries this value (nullable; populated only when raw subject-level data is present). The comparison "this model's OCI on kinship terms is within the range we observe across human subject pools" is a genuinely new cross-species claim enabled by this field; it is a claim about *output concentration*, not about proximity to any single human consensus.

**Data layout — multi-baseline (v0.7):**

```
data/grounding/
├── family/
│   ├── romney_1996/                    # baseline_id (kind: published)
│   │   ├── source.md                   # citation, methodology, IRB status, year
│   │   ├── items.txt                   # canonical item set
│   │   ├── cooccurrence.csv            # symmetric matrix, header row = items
│   │   └── grounding_ref.json          # the GroundingRef as JSON; human-editable
│   └── tanaka_2026_kyoto_kinship/      # hypothetical second baseline (kind: researcher)
│       ├── source.md
│       ├── items.txt
│       ├── pile_sort_raw.csv           # subject × pile assignments (researcher submission)
│       ├── cooccurrence.csv            # derived from pile_sort_raw.csv at submission time
│       └── grounding_ref.json
├── holidays/                            # ungrounded in v1 — directory may not exist at all
└── color/                               # added Phase 6 with the Berlin & Kay baseline
    └── berlin_kay_1969/
        ├── source.md
        ├── items.txt
        ├── cooccurrence.csv
        └── grounding_ref.json
```

**Per-baseline contents:**

- `source.md` — full bibliographic citation (for published baselines) or full researcher attribution (for researcher submissions). Includes population description, collection year, IRB status, and method. Mandatory.
- `items.txt` — the canonical item set for this baseline, one item per line. Used to compute item intersection with the LSB v1 item set for the domain.
- `cooccurrence.csv` — symmetric similarity matrix, header row = items. Mandatory for both kinds.
- `pile_sort_raw.csv` — *only* for researcher submissions that include per-subject pile assignments. When present, the analysis pipeline can compute a bootstrap ellipse for the baseline (resampling subjects with replacement) and the marker is rendered with an uncertainty ellipse on the MDS plot. When absent (typical of published baselines that ship aggregate matrices only), the marker is rendered without an ellipse and labeled "published aggregate, uncertainty unavailable" per the DESIGN_SYSTEM.md grounding detail panel spec.
- `grounding_ref.json` — the `GroundingRef` (§3.2) as JSON, human-editable. The grounding loader reads this directly rather than reconstructing from `source.md` text. Required fields per the schema.

**Item alignment:** each baseline's item set will not exactly match the LSB v1 item set for the domain. The grounding loader takes the **intersection** of human items and the LSB salient item set per model and computes similarity on that subset. The intersection size is stored in `GroundingRef.item_intersection_size` and displayed in the dashboard's grounding detail panel (`DESIGN_SYSTEM.md` §4.2). A small intersection means a weaker comparison and the UI flags it.

**Sourcing policy.** LSB accepts two kinds of grounding:

1. **Published baselines** (`baseline_kind="published"`). Licensed, peer-reviewed published human CDA data extracted by Mark from the literature. v1 primary target: Romney et al. (1996) for family terms. See `PHASE_4C_CANDIDATE_SOURCES.md` for the candidate source list and licensing notes. No original human data collection by LSB itself in v1.
2. **Researcher submissions** (`baseline_kind="researcher"`). Human CDA data collected by external researchers and contributed to LSB via the submission workflow below. Researchers retain all rights to their data; LSB validates format and provides attribution. The contribution path is open from v1 (Phase 6 deliverable to actually open it publicly), but the schema, directory layout, and dashboard rendering are designed for it from Phase 1.

**v1 acquisition targets** (in priority order, all `baseline_kind="published"`):

- **Family / kinship terms.** The primary target. Candidate sources include the Romney, Boyd, Moore, Batchelder & Brazill (1996) PNAS paper, the D'Andrade American kinship studies (1970s–80s), and Weller & Romney's *Systematic Data Collection* worked examples. Several of these publish full similarity matrices in the articles themselves, which is the cleanest acquisition path — figures and tables in peer-reviewed articles are generally citable and reusable under fair use for non-commercial research purposes. The Architect agent should confirm specific licensing per source before use.
- **Color terms.** Berlin & Kay's *Basic Color Terms* data is widely used in the literature, well-documented, and has been reanalyzed many times. Second priority grounding domain; add in Phase 6 when the color domain is added.
- **Emotion terms.** Published cross-cultural data exists (Shaver, Schwartz, Kirson & O'Connor 1987 is a common reference) but is messier and the item sets vary. Defer to v2.
- **Other domains (holidays, food, justice, etc.).** No obvious published CDA baseline exists. These domains remain **ungrounded in v1** and are displayed without a human baseline marker — a normal first-class state per §1.5.5. They become eligible for researcher-submitted grounding the moment the submission process opens.

**Acquisition workflow for published baselines** (Phase 4c):

1. Architect agent identifies 2–3 candidate sources for the target domain with full citations.
2. Mark reviews and confirms the preferred source (and confirms the institutional access path — JSTOR, university library, direct author contact).
3. Mark acquires the PDF/data, extracts the published similarity or co-occurrence matrix, and hands it to the Coder agent as a CSV plus a `source.md` file plus a draft `grounding_ref.json` with `baseline_kind="published"`.
4. Coder agent normalizes into the `data/grounding/{domain}/{baseline_id}/` schema, writes unit tests that verify the loaded matrix round-trips correctly, and validates the item set against the v1 domain prompt.
5. Architect agent reviews item-set intersection coverage before downstream phases run.

**Researcher submission workflow** (added v0.7, v1 implementation via GitHub PR):

LSB exists in part to connect to the broader CDA research community. Anthropologists, linguists, and cognitive scientists running pile sort or free list studies on human subjects today can drop their data into LSB and see it on the dashboard alongside the model results. The v1 contribution path is a GitHub Pull Request following a submission template; the v2 hook is an in-app submission form (deferred — see "Out of scope" note below). The dashboard's "Submit your data" entry point (`DESIGN_SYSTEM.md` §4.3) opens the GitHub submission template directly.

**v1 submission process:**

1. **Researcher reads the submission template** at `docs/grounding_submission_template.md` (Phase 6 deliverable). The template specifies the required files: `source.md`, `items.txt`, `cooccurrence.csv`, optionally `pile_sort_raw.csv`, and a draft `grounding_ref.json` with `baseline_kind="researcher"` and submitter fields filled in.
2. **Researcher opens a Pull Request** against the LSB repo, adding the new directory under `data/grounding/{domain}/{baseline_id}/`. The PR template (`.github/PULL_REQUEST_TEMPLATE/grounding_submission.md`, Phase 6 deliverable) prompts for confirmation that the researcher holds the rights to share the data, that any required IRB approval is in place, and that the submission is intended for CC-BY-4.0 redistribution with full attribution.
3. **Automated validation** runs in CI: schema check on `grounding_ref.json`, format check on `cooccurrence.csv` (symmetric, header row matches `items.txt`), item-intersection coverage report, and a `gitleaks` scan to confirm no PII has leaked into any submitted file.
4. **CDA SME agent reviews** the PR for protocol validity (was the data actually collected with a recognizable CDA protocol?), claims validity (does the population description support the claims the baseline implicitly makes?), and audience translation (is the source.md legible to a non-anthropologist visiting the dashboard?). Verdict per §5.1: PASS / PASS-WITH-NOTES / FAIL.
5. **Mark approves and merges** if the CDA SME verdict is PASS or PASS-WITH-NOTES with corrections applied. The merge triggers an analysis re-run, which writes the updated `DomainResult` with the new baseline included in `groundings`. The dashboard picks up the new baseline on the next publish.
6. **Citation and attribution.** The merged baseline appears with full attribution in the dashboard's grounding detail panel (`DESIGN_SYSTEM.md` §4.2), in the methodology page's grounding section, and in the open data bundle's data dictionary. The researcher's name, institution, year, and contact (if provided) are listed alongside the data wherever the data is shown. The researcher retains all rights to their data; LSB redistributes under CC-BY-4.0 with attribution.

**What is *not* in v1 (deferred to v2):**

- **In-app submission form.** v1 routes contributors to GitHub. v2 may add a web form on the dashboard that walks through the same submission template and opens the PR programmatically.
- **Anonymous submissions.** Every v1 submission must be tied to a named researcher and an institution. We are willing to revisit this policy if the research community asks for it, but the default is named attribution.
- **Submission via email or non-GitHub channels.** Same reason — auditability. The PR is the audit trail.
- **Automatic IRB verification.** LSB takes the researcher's word on `irb_status` for v1. False statements would be a research ethics issue for the submitter, not an LSB system failure. The CDA SME flags any submission where the population description and the IRB status appear inconsistent (e.g., contemporary US adult subjects with `irb_status="not_applicable"`).

**Acquisition is the one part of grounding Mark does by hand for published baselines.** The Coder agent cannot retrieve licensed academic content, and automated scraping of publishers would be both a licensing violation and bad practice. Budget ~2 hours of Mark's time per published baseline for the literature pull and matrix extraction. Researcher submissions, by contrast, arrive ready-to-merge — Mark's role on those is review and approval, not extraction.

**Graceful degradation:** if no preferred published source is available for a domain and no researcher submission has arrived, the domain ships ungrounded. The Validation Phase gates (§5.3) do not require grounding to pass — grounding strengthens the findings but is not the signal test itself. The dashboard handles ungrounded domains as a first-class state per `DESIGN_SYSTEM.md` §4.1 State 0.

**Citation discipline.** Every grounding source — published or researcher — is cited in full in three places: `data/grounding/{domain}/{baseline_id}/source.md`, the public methodology page on the dashboard, and the open data bundle's `DATA_DICTIONARY.md`. The dashboard tooltip on each baseline marker shows the short citation inline. Under no circumstances is grounding data displayed without attribution. The Reviewer agent must reject any PR that adds a baseline without all three citation surfaces populated.

#### 4.2.6 Bootstrap uncertainty module (`bootstrap.py`)

**Why this exists:** the §3.1 review critique of "false precision" is correct unless every visualization shows uncertainty. Point estimates on an MDS plot look like they mean more than they do. Ellipses and confidence intervals prevent that.

**What it does:** for each `(model, domain)` pair with N raw runs, resample with replacement B=500 times and rerun the full analysis pipeline on each bootstrap sample. The outputs are distributions, not points:

- **MDS ellipses:** for each model, the bootstrap distribution of its 2D coordinates defines a 95% confidence ellipse (covariance of bootstrap coordinates, Procrustes-aligned to the reference solution).
- **Similarity heatmap CIs:** each cell carries a 95% CI from the bootstrap distribution.
- **Consensus score CI:** bootstrap distribution of the eigenvalue ratio.
- **Drift score CIs:** bootstrap Procrustes distances.

**Computational cost:** B=500 bootstraps × ~2s per pipeline run = ~15 minutes per domain. Trivial for v1. If this becomes a bottleneck at v2 scale, switch to B=200 and document the reduction.

**Display rule — enforced by the Reviewer agent:** no visualization in `apps/dashboard` may display a point estimate without its associated uncertainty. No exceptions. If the Coder adds a new viz that can't express uncertainty, it doesn't ship.

**Interaction with grounding:** every baseline in a domain's `groundings` list is bootstrapped independently when raw subject-level data is available (resampling human informants with replacement). Researcher submissions that include `pile_sort_raw.csv` get a bootstrap ellipse on the MDS plot; published baselines that ship aggregate matrices only are shown without an ellipse and labeled "published aggregate, uncertainty unavailable" per `DESIGN_SYSTEM.md` §3.3 conditional rendering rules. When a domain has multiple baselines, each gets its own ellipse computed independently — the bootstrap does not pool across baselines, since they represent different human populations and pooling would smear them.

---

### 4.3 Storage

No database server in v1. Files all the way down. v0.6 formalizes the **three parallel result representations** that the project has been quietly converging on, and makes both JSONL and SQLite first-class published artifacts.

**The three representations:**

| Format | Role | Generated by | Published? | Audience |
|---|---|---|---|---|
| **JSONL** (one `InformantRecord` per line, append-only) | **Canonical raw data.** This is the source of truth. All other representations are derived. Append-only by design — never overwritten, never edited in place. New runs append; nothing else changes. | `cdb_collect/runner.py` writes one line per completed `InformantRecord`. | **Yes — open data bundle (§6.7), CC0.** | Researchers reproducing the pipeline; auditors verifying provenance; LSB itself reading raw on every analysis run. |
| **SQLite** (single-file database, generated artifact) | **Researcher-friendly query layer.** Same data as the JSONL, denormalized into tables that a researcher can query with `SELECT` instead of writing JSONL parsers. Flat tables for `informants`, `freelist_items`, `pilesort_cells`, `interview_labels`. Indexed on `model_id`, `domain_slug`, `collection_date`, `model_version_returned`. | `scripts/build_db.py` reads the canonical JSONL and writes a fresh `lsb.sqlite`. Idempotent. Re-run produces a byte-identical file given the same JSONL inputs. | **Yes — open data bundle (§6.7), CC0.** | Researchers who want to ask questions like "which models on family terms produced fewer than 15 free-list items in Q2 2026" without writing code. |
| **Parquet** (per-domain, per-analysis-version) | **Analysis intermediates.** Outputs of `cdb_analyze` — co-occurrence matrices, MDS coordinates, bootstrap samples. Columnar format optimized for `pandas.read_parquet`. Regeneratable from JSONL via `cdb_analyze`. | `cdb_analyze/pipeline.py`. | **No** — regeneratable, and the canonical JSONL is the citable artifact. Published only inside the LSB repo for build-time use. | Internal analysis pipeline; not part of the public open data contract. |

```
data/
├── raw/
│   ├── informants.jsonl              # canonical InformantRecord stream, append-only, git-ignored, the source of truth
│   ├── {domain}/
│   │   └── {model_family}/
│   │       └── {run_id}.json         # one RawResponse per file (per-API-call atom, lower-level than InformantRecord)
│   └── failures.jsonl
├── processed/
│   └── {domain}/
│       └── {analysis_version}/
│           ├── free_lists.parquet
│           ├── cooccurrence.parquet
│           └── mds.parquet
├── results/
│   └── {domain}/
│       └── {analysis_version}.json   # served directly by the dashboard via cdb_publish
└── open_bundle/                      # built by scripts/build_db.py — published per §6.7
    ├── informants.jsonl              # copy of data/raw/informants.jsonl
    ├── lsb.sqlite                    # generated SQLite, built from informants.jsonl
    ├── build_db.py                   # the build script itself, included so the bundle is self-rebuilding
    └── DATA_DICTIONARY.md            # copy of docs/DATA_DICTIONARY.md
```

- `data/raw/informants.jsonl` is **append-only and git-ignored**, backed up to the Synology NAS *and* Backblaze B2 on a nightly cron. This is the research corpus — losing it means losing the benchmark.
- `data/raw/{domain}/{model_family}/{run_id}.json` files are the per-call `RawResponse` atoms used for low-level debugging and replay. They are also git-ignored and nightly-backed-up.
- `data/results/` is **git-tracked** (it's small — one JSON per domain per version). This makes the site's current state trivially reproducible and gives us free version history.
- `data/processed/` is **git-ignored and regeneratable** from raw.
- `data/open_bundle/` is the built artifact of the open data publication pipeline (§6.7). Built on every release, uploaded to Backblaze B2, DOI-minted via Zenodo after Phase 4 validation.

**`docs/DATA_DICTIONARY.md` is a required Phase 1 deliverable.** It documents every field in `InformantRecord`, every table and column in `lsb.sqlite`, the provenance fields, the QA fields, and the relationship between the JSONL and SQLite representations. Without it, the open data bundle is inert. The Reviewer agent must reject any PR that adds a field to `InformantRecord` without a matching update to `DATA_DICTIONARY.md` in the same PR.

**Upgrade path beyond SQLite:** if v2 needs cross-domain queries at scale, realtime collection, or multi-writer concurrency, move SQLite → DuckDB → Postgres in that order. Don't skip steps. The JSONL canonical layer is invariant across that path — only the derived database changes.

---

### 4.4 Publish layer (`cdb_publish`)

**Responsibility:** read `data/results/` and write static JSON files into `apps/dashboard/public/data/` so the dashboard can fetch them at runtime without any server-side backend. Nothing else. No HTTP server, no routes, no auth.

#### 4.4.1 How it works

`cdb_publish/build.py` is a pure Python script that:

1. Reads every `data/results/{domain}/{analysis_version}.json` (one `DomainResult` per file).
2. Writes a set of pre-shaped JSON files into `apps/dashboard/public/data/` according to the naming convention below.
3. Writes an `apps/dashboard/public/data/manifest.json` listing every available domain + version, so the dashboard can discover what data exists without scanning.

No server starts. No HTTP calls are made. The script runs in seconds and is safe to re-run — all outputs are deterministic given the same inputs.

#### 4.4.2 Output file naming convention

```
apps/dashboard/public/data/
├── manifest.json                          # { domains: [...], models: [...], built_at: "..." }
├── domains/
│   ├── {domain}.json                      # DomainResult at latest analysis_version
│   └── {domain}.v{analysis_version}.json  # DomainResult at a specific version
├── models/
│   └── index.json                         # list of all ModelRef objects across all results
├── drift/
│   └── {model_family}.json                # cross-version drift + longitudinal scrubbing data
                                            # (DriftTracker reads this for both modes per §4.5)
```

**Why `{domain}.json` and `{domain}.v{version}.json` both exist:** the dashboard's default fetch uses the unversioned file (always the current release). Permalinks and the reproducibility workflow use the versioned file. The manifest records which version is "current" so the build can update the unversioned file atomically.

#### 4.4.3 Build trigger and deployment flow

**Manual trigger (primary, for v1):**
```bash
python scripts/analyze.py --all --analysis-version 0.1
python scripts/publish.py
# → writes static JSON files to apps/dashboard/public/data/
git add apps/dashboard/public/data/
git commit -m "chore: publish results v0.1"
git push
# → Cloudflare Pages auto-deploys from main branch within ~30 seconds
```

**CI trigger (Phase 6+):** a GitHub Actions workflow fires `publish.py` automatically whenever a new `data/results/` file is committed to main. The dashboard update is fully automated after analysis runs.

**Cloudflare Pages deployment:** Cloudflare Pages is configured to build from the `apps/dashboard/` directory. The build command is `npm run build`; the output directory is `apps/dashboard/dist/`. Because `public/data/` is inside the Vite build root, all JSON files are included verbatim in the dist bundle and served at `cogstructurelab.com/data/...` with Cloudflare's global CDN caching automatically applied.

#### 4.4.4 Caching

Cloudflare Pages applies `Cache-Control: public, max-age=31536000, immutable` to versioned files (`*.v0.1.json`) and `Cache-Control: public, max-age=3600` to unversioned files (`{domain}.json`, `manifest.json`). No cache configuration is required in the codebase — Cloudflare's default behavior is correct for this pattern.

#### 4.4.5 Why no FastAPI

The v0.3.1 design retained FastAPI for the drift endpoint, which needed light on-the-fly joining across domain files. That join is now done at publish time by `build.py` and written to `drift/{model_family}.json`. The result is: zero server to deploy, zero server to maintain, zero server to be rate-limited or DDoSed, and free hosting on Cloudflare Pages' free tier — indefinitely.

If v2 needs realtime collection status, a write path, or user accounts, re-introduce a backend at that point. Until then, no server.

---

### 4.5 Frontend (`apps/dashboard`)

React + Vite + TypeScript. Tailwind for styling. No Next.js — the app is a pure SPA served as static files.

**`DESIGN_SYSTEM.md` is binding on every part of this section.** The visual treatment of every component, the color tokens, the typography, the OWID-style article layout, the grounding-state rendering matrix, the four-grounding-state spec, the journalist/engineer/researcher three-audience test, and the accessibility requirements all live in `DESIGN_SYSTEM.md` and are owned by the UI/UX agent (§5.1). This section describes the *architectural* contract — what the dashboard fetches, where it fetches from, what the components are named, and how the data flows. It does not duplicate the visual spec. Where the two documents disagree, `DESIGN_SYSTEM.md` is authoritative for visual decisions and `ARCHITECTURE.md` is authoritative for data and component structure decisions; neither one has the right to silently override the other, and any conflict should be flagged on the next architecture pass.

**Data access — static JSON only.** The dashboard fetches data exclusively from the static JSON files written by `cdb_publish` (§4.4) at `cogstructurelab.com/data/...`. There are no runtime API calls to a backend, no WebSocket connections, and no third-party data endpoints. All fetch calls are same-origin — the JSON files are served from the same Cloudflare Pages deployment as the app itself.

**Content Security Policy.** The dashboard must ship with a strict CSP header. The `connect-src` directive is `'self'` only — no external hosts. This is enforced in `apps/dashboard/public/_headers` (Cloudflare Pages header file). See `SECURITY_AND_HARDENING.md` §3.1 for the full CSP spec and §3.3 for LLM-output sanitization rules that apply to lede text and any other model-generated content rendered in the dashboard. The Reviewer agent must reject any component that renders model-generated text via `dangerouslySetInnerHTML` or equivalent without the sanitization wrapper specified in §3.3.

**Visualization libraries:**
- **D3** for the MDS plot, free-list comparison, and the drift tracker (custom layouts, annotations, zoom, confidence ellipses, date-slider scrubbing animations)
- **Plotly** for the similarity heatmap (fast to build, good defaults, built-in error bars)

**Uncertainty display is mandatory, not optional.** Every view renders the bootstrap outputs from §4.2.6:

- **MDSPlot** renders 95% confidence ellipses around each model point, not bare points. Ellipse opacity scales with `n_bootstrap`. Human grounding baselines appear as distinct markers with their own ellipses where raw subject data is available — visual treatment per `DESIGN_SYSTEM.md` §3.3.
- **Heatmap** cells carry tooltips showing `similarity ± 95% CI`. Cells whose CI crosses the null value are shown with reduced saturation to signal "not statistically distinguishable."
- **FreeListCompare** shows per-item inclusion frequency across bootstrap samples as a small bar next to each term.
- **DriftTracker** shows error bars on every drift score, and a shaded "within-noise" band derived from the prompt-sensitivity study (§5.3).

A view that cannot express uncertainty does not ship. This is a Reviewer-enforced rule.

**Grounding display states.** The dashboard handles four grounding states for any given `(domain)`, defined in `DESIGN_SYSTEM.md` §4.1: **State 0 — none** (no human baselines available; key finding is comparative only), **State 1 — published only** (e.g., Romney 1996 family terms), **State 2 — researcher only** (a researcher submission with no published baseline), **State 3 — multiple baselines** (published + one or more researcher submissions, or multiple researcher submissions). State 0 is a normal first-class state per §1.5.5, not a degraded mode. The four states are driven directly by the contents of `DomainResult.groundings` (§3.2): empty list = State 0; one entry = State 1 or 2 depending on `baseline_kind`; two or more entries = State 3. The architecture contract is that every `DomainResult` carries enough information to render any of the four states without an extra fetch — `groundings` is fully populated in the static JSON written by `cdb_publish`.

**DriftTracker — cross-version drift and longitudinal date-slider scrubbing (consolidated from v0.6 TemporalView in v0.7).** `DriftTracker.tsx` is the dashboard's expression of design commitment #10 (longitudinal model tracking) in §1. v0.6 introduced this functionality as a separate `TemporalView.tsx` component; v0.7 consolidates it into `DriftTracker.tsx` to align with `DESIGN_SYSTEM.md` §3.2 and §3.6, which spec a single drift component with a date slider rather than two parallel components. The functionality and the data layer are unchanged; only the component name and file structure change.

- **Unit of analysis:** `model_version_returned` × `collection_date`. Not `model_id` — providers silently roll snapshots, and the version string returned in the API response is the only reliable temporal anchor. See §3.2 `InformantRecord`.
- **Change metric:** **Procrustes distance** between MDS coordinates of consecutive collection dates for the same model family on the same domain. Same drift score used in `cdb_analyze/drift.py`; the date-slider view applies it across time within a single declared model identity.
- **Visualization:** for each `(model_family, domain)` pair, a longitudinal D3 chart with collection date on the x-axis and Procrustes drift score (vs. the first observation) on the y-axis. Bootstrap confidence bands on every point. A divergence event flags any consecutive-date drift score above a tunable threshold (start at 0.15 to mirror the social-pipeline drift trigger in §4.6). The date slider (`DESIGN_SYSTEM.md` §3.6) lets users scrub through collection dates and watch the MDS plot's model points animate to their position at each date — human baseline markers stay anchored as fixed reference points while model points move around them.
- **Data source:** `apps/dashboard/public/data/drift/{model_family}.json`, written by `cdb_publish/build.py`. Each file contains, per `(domain, model_version_returned, collection_date)`, the MDS coordinates, the Procrustes drift score versus the first observation for that family, and the bootstrap CI.
- **Phase ordering:** the date-slider view is a Phase 6 deliverable, but **the data structure must support it from Phase 1**. This is why `InformantRecord.model_version_returned` and `InformantRecord.collection_date` are mandatory fields, why `data/raw/informants.jsonl` is partitioned by collection date, and why old runs are never overwritten. Building the visualization in Phase 6 should be a frontend-only task — no backfill of the data layer required.
- **Why this matters now (Phase 1 implication):** if the schema does not capture exact version strings and exact collection dates from day one, the longitudinal view is impossible without re-collection. Re-collection is not possible — the prior versions of the models will no longer exist. The longitudinal view is therefore retroactively unbuildable if Phase 1 misses the schema, which is why §3.2 makes these fields mandatory.

**Component structure:**

```
src/
├── App.tsx
├── views/
│   ├── MDSPlot.tsx              # the signature viz
│   ├── Heatmap.tsx              # cross-model similarity (Plotly)
│   ├── FreeListCompare.tsx      # side-by-side ranked lists
│   └── DriftTracker.tsx         # cross-version drift + date-slider scrubbing (DESIGN_SYSTEM.md §3.6)
├── components/
│   ├── DomainPicker.tsx         # horizontal pill buttons for cross-domain navigation (DESIGN_SYSTEM.md §2.3)
│   ├── DomainSlider.tsx         # animated explorer-internal domain transitions (DESIGN_SYSTEM.md §3.5)
│   ├── DateSlider.tsx           # temporal scrubbing inside DriftTracker (DESIGN_SYSTEM.md §3.6)
│   ├── ModelSelector.tsx        # checkbox panel with origin badges (DESIGN_SYSTEM.md §3.7)
│   ├── ModelFilter.tsx          # three-axis filter — origin × openness × collection_method
│   ├── VizSwitcher.tsx          # tab bar for switching visualizations
│   ├── KeyFinding.tsx           # the lede sentence strip above the explorer
│   ├── GroundingSelector.tsx    # human baseline checkboxes + "Submit your data" link
│   ├── GroundingDetailPanel.tsx # slide-in panel for baseline detail (DESIGN_SYSTEM.md §4.2)
│   ├── SubmitGroundingModal.tsx # modal pointing to GitHub PR template (DESIGN_SYSTEM.md §4.3)
│   ├── ExplainButton.tsx        # opens a modal with the lede + methodology
│   ├── ExportImageButton.tsx    # one-click watermarked PNG export
│   ├── GenerateSummaryButton.tsx
│   ├── CiteModal.tsx            # citation formats modal (APA / MLA / Chicago / BibTeX)
│   └── EmbedModal.tsx           # iframe embed snippet
├── api/client.ts                # typed fetch helpers for the static JSON files in public/data/
└── lib/
    └── watermark.ts             # SVG → PNG + watermark
```

**The journalist affordances are first-class components, not afterthoughts.** `ExportImageButton` is on every view. `GenerateSummaryButton` is on every view. The lede shows above every view without a click. This is what turns the benchmark into a distribution engine rather than a hobby site. The full component inventory and implementation order live in `DESIGN_SYSTEM.md` §11.

**Image export spec:**
- PNG, 1600×900 for social cards, 2000×2000 for high-resolution downloads
- Benchmark logo + URL watermark in bottom-right, ~4% of image height
- Embeds `tEXt` metadata: domain, models, analysis_version, generation timestamp
- Filename: `cdb_{domain}_{viz}_{version}.png`

**Accessibility:** the MDS plot must be interpretable without color — use shape + color together for model origin. Every viz has a "Read as table" toggle that shows the underlying numbers. The full WCAG AA accessibility checklist lives in `DESIGN_SYSTEM.md` §7 and is enforced by both the UI/UX agent and the Reviewer agent.

---

### 4.6 Social publishing pipeline (`cdb_social`)

The Claude Code agent described in the briefing. Runs on a cron (GitHub Actions is fine for v1).

**Architecture:**

```
triggers.py       # detects "post-worthy" events
   │
   ▼
drafters/         # one drafter per platform
   ├── x.py       # thread format
   ├── linkedin.py
   └── bluesky.py
   │
   ▼
queue.py          # writes drafts to data/social_queue/pending/
   │
   ▼
[human review]    # Mark approves via a minimal review UI or a CLI
   │
   ▼
publisher.py      # posts via platform APIs from data/social_queue/approved/
```

**Triggers (implemented as pure functions over the results store):**
1. New model added → "We added {model} to the benchmark. Here's where it sits."
2. New domain analyzed → "We now measure how models categorize {domain}. First finding: ..."
3. Drift event → fires when Procrustes distance between two versions of the same model family exceeds a threshold (start at 0.15, tune later).
4. Divergence event → fires when the gap between the two most-different models on a domain hits a new high.
5. Scheduled: monthly "state of cultural alignment" roundup.

**Drafting:** each drafter is a Claude Code subagent with a short system prompt specific to the platform. Input is a trigger event + the relevant `DomainResult`. Output is a JSON file containing: draft text, image filename (generated via the same export pipeline the dashboard uses), suggested posting time, confidence score.

**Human-in-the-loop:** the review step is non-negotiable. v1 can be as simple as `python scripts/social_review.py` showing drafts one at a time with y/n/edit. v2 can build a web UI if the volume justifies it.

---

## 5. The Claude Code development workflow

This is where the architecture meets your existing agent pipeline.

### 5.1 Agent responsibilities on this project

| Agent | Role on LSB |
|---|---|
| **Architect** (Opus) | Owns this document. Decomposes features into Coder-sized tasks. Reviews Open Decisions with Mark before any code is written for an unresolved one. Never writes code. Hands every plan to the CDA SME for methodological gating before it reaches the Coder; for frontend tasks, the post-SME plan additionally passes through the UI/UX agent before the Coder sees it. |
| **CDA SME** (Opus) | **Methodological gatekeeper between the Architect and the Coder. Added v0.6.** Reviews every plan from the Architect on four axes before the Coder is allowed to start work: (1) **protocol validity** — does the plan correctly implement free list / pile sort / pile interview as defined in the CDA literature; are prompts, item handling, and aggregation faithful to the methodology; (2) **analytical validity** — are the chosen statistics (co-occurrence, MDS, consensus analysis, Procrustes drift, bootstrap) appropriate for the data and the claims being made; do error bars and uncertainty propagate correctly; (3) **claims validity** — does the resulting visualization or generated text overclaim relative to §1.5; is the language guardrails table (§1.5.4) respected; is the corpus-lens framing used correctly; (4) **audience translation** — is the methodology defensible to a skeptical anthropologist *and* legible to a journalist; does the plan reach both audiences simultaneously without compromising either. The CDA SME issues one of three verdicts: **PASS** (plan moves on), **PASS-WITH-NOTES** (plan moves on with annotated changes the next agent must apply), or **FAIL** (plan returned to Architect for rework). Verdicts are posted to the `#lsb-cda-sme` Slack channel with the verdict, a one-paragraph rationale, and the four-axis scorecard. The CDA SME is the methodological conscience of the project; pure engineering teams (Architect/Coder/Reviewer/Tester) lack domain knowledge validation, and shipping CDA work without an SME in the loop is the single most likely failure mode for a project that exists to apply a 50-year-old anthropological methodology to a brand-new substrate. **The CDA SME also reviews researcher grounding submission PRs** (§4.2.5) before Mark merges them. |
| **UI/UX agent** (Sonnet) | **Design conscience of the frontend. Added v0.7.** Sits between the CDA SME and the Coder for frontend tasks only — for collection, analysis, schema, or backend tasks, the UI/UX agent is skipped and plans flow directly from the CDA SME to the Coder. Reviews every frontend plan and every frontend component PR against four questions, all of them rooted in `DESIGN_SYSTEM.md`: (1) **OWID design fidelity** — does the component match the design language, the design tokens, the typographic scale, and the article-with-embedded-explorer page model in `DESIGN_SYSTEM.md` §1 and §2; (2) **journalist 30-second test** — can a journalist arriving cold understand the finding within 30 seconds without reading the methodology page; (3) **researcher reproduce-and-cite test** — does the researcher have everything they need to reproduce the finding (download CSV, get the citation, find the raw data, contribute their own grounding); (4) **WCAG AA accessibility** — color + shape together, "Read as table" toggle, keyboard navigation, ARIA labels, focus indicators, screen reader summary. Verdict format matches the CDA SME: **PASS** / **PASS-WITH-NOTES** / **FAIL**. Verdicts are posted to `#lsb-ui-ux` with a one-paragraph rationale and the four-question scorecard. The UI/UX agent is the owner of `DESIGN_SYSTEM.md` — if a frontend plan needs a visual decision the design system does not cover, the UI/UX agent updates the design system *first*, posts the update for Mark's awareness, and only then passes the plan through to the Coder. The Coder is never permitted to invent visual decisions on the fly. |
| **Coder** (Sonnet) | Implements one package or one feature at a time. Must read the relevant `cdb_core/schemas.py` before touching any other file. **Receives only plans that have a CDA SME PASS or PASS-WITH-NOTES verdict, plus — for frontend tasks — a UI/UX agent PASS or PASS-WITH-NOTES verdict.** Never starts work directly from an Architect plan. Never invents visual decisions; if the UI/UX agent's approved plan does not cover a visual question that comes up mid-implementation, the Coder pauses and routes the question back to the UI/UX agent rather than guessing. |
| **Reviewer** (Sonnet) | Enforces six rules: (1) schemas are only defined in `cdb_core`; (2) layer boundaries are respected, including the **`cdb_analyze` no-LLM-imports rule** (§4.2 binding constraint, §2 boundary rule four); (3) every new prompt template bumps `prompt_version`; (4) the §1.5.4 language guardrails — no generated text, dashboard copy, or README content may contain forbidden phrases like "worldview," "believes," or "thinks"; (5) any change to `InformantRecord` (§3.2) is accompanied by a matching update to `docs/DATA_DICTIONARY.md` in the same PR; (6) **frontend PRs carry a UI/UX agent PASS or PASS-WITH-NOTES verdict** (§5.1 UI/UX row) — no frontend component lands without the design conscience having reviewed it, and any visual decision visible in the diff that is not covered by `DESIGN_SYSTEM.md` is grounds for rejection regardless of how the rest of the PR looks. |
| **Tester** (Sonnet) | Every package ships with fixtures in `tests/fixtures/` (canned model responses) so tests never hit real APIs. Runs pytest on Python packages, vitest on the dashboard. |

**Pipeline shape:**

```
Architect → CDA SME → ┬─ (frontend tasks) → UI/UX agent → Coder → Reviewer → Tester
                      └─ (other tasks)    ─────────────→  Coder → Reviewer → Tester
```

The CDA SME and the UI/UX agent are both gates, not advisors. A FAIL verdict from either one stops the plan and bounces it back to the Architect. PASS-WITH-NOTES is acceptable but the notes are mandatory; the next agent in the pipeline must apply them. PASS is the only verdict that allows the plan through unmodified. The QA_Runner (§4.1.6) is *outside* this pipeline — it watches collection runs in production and posts directly to `#lsb-alerts`, bypassing the agent team entirely (commitment #8 in §1).

### 5.2 CLAUDE.md additions for this project

Your existing `CLAUDE.md` is the team constitution. For LSB, append a project section that says:

1. Read `ARCHITECTURE.md` before starting any task. **§1.5 is binding on all generated text.**
2. Read `SECURITY_AND_HARDENING.md` before touching `apps/dashboard/`, `packages/cdb_collect/`, or any CI/CD configuration. The Reviewer rules table in §9 of that document is enforced on every PR.
3. Read `HOSTING_AND_DEV_OPS.md` before any deployment-related task or any task that touches `.github/workflows/`, Cloudflare Pages config, or environment variables.
4. Read `PHASE_4C_CANDIDATE_SOURCES.md` before any task touching `data/grounding/`, `packages/cdb_analyze/grounding.py`, or the family-domain grounding workflow.
5. Read `PHASE_0_TASKS.md` for the full Phase 0 task list, acceptance criteria, and dependency graph. It is the canonical decomposition for the Coder agent's first session.
6. Read `docs/DATA_DICTIONARY.md` before touching `cdb_core/schemas.py` (specifically `InformantRecord`) or `scripts/build_db.py`.
7. Never edit `cdb_core/schemas.py` without Architect sign-off. Schema changes ripple everywhere. Changes to `InformantRecord` require a matching `DATA_DICTIONARY.md` update in the same PR.
8. Prompt templates are versioned. Never edit a published prompt template in place — copy it to a new version directory.
9. No API keys in the repo. Use `.env` + `python-dotenv`; `.env.example` is tracked, `.env` is ignored.
10. No real model calls in tests. Use fixtures.
11. No point estimates without uncertainty in any visualization. See §4.2.6 and §4.5.
12. **No LLM calls in `cdb_analyze`.** See §4.2 binding constraint and §1 commitment 6. The Reviewer's static import check enforces this.
13. **Architect plans must be CDA-SME-approved before reaching the Coder.** See §5.1. For frontend tasks, plans must additionally carry a UI/UX agent PASS or PASS-WITH-NOTES verdict before reaching the Coder.
14. **Read `DESIGN_SYSTEM.md` before any frontend task.** Required for any work touching `apps/dashboard/`, any new component, any visual change to an existing component, any new color or font or spacing decision, and any update to the dashboard's article-with-explorer page model. The UI/UX agent owns this document; the Coder may not invent visual decisions outside of it. If a frontend task needs a visual decision the design system does not cover, the Coder pauses, surfaces the question to the UI/UX agent, and only resumes once the design system has been updated.
15. **Researcher grounding submission PRs** (added v0.7) follow the workflow in §4.2.5. Validation runs in CI (schema check, format check, item-intersection report, gitleaks PII scan); CDA SME reviews; Mark merges. The PR template is at `.github/PULL_REQUEST_TEMPLATE/grounding_submission.md`.

### 5.3 Suggested phased build plan

This is sized to be workable across a few focused sessions with your agent pipeline.

**Phase 0 — Skeleton (one session)**
- Repo scaffold, pyproject.toml, CLAUDE.md, this doc
- `cdb_core/schemas.py` with all types from section 3, **including `InformantRecord` and the three step records**
- `docs/DATA_DICTIONARY.md` first draft covering `InformantRecord`
- Empty package directories with `__init__.py` and docstrings
- CI: ruff + mypy + pytest on push, plus the `cdb_analyze` no-LLM-imports static check
- See `PHASE_0_TASKS.md` for the full 10-task decomposition (P0-T1 through P0-T10), acceptance criteria, and dependency graph.

**Phase 1 — Collection layer (unified; VPS + remote APIs only)**

All collection runs use **three API endpoints** — no local inference mirror, no Ollama, no Mac-class edge hardware:

1. **Anthropic API** — Claude models (direct first-party integration).
2. **OpenRouter** — frontier closed models and many open-weight models through a single HTTP API (including long-tail and regional routes where applicable).
3. **Hugging Face Inference Providers** — specialist open models when OpenRouter is not the right fit.

The runner and adapters live on ordinary project VPS (`lsb-agent-01`) / CI infrastructure; scaling is by concurrency limits and the spend cap, not by adding on-prem GPUs.

**Milestone A — smallest vertical slice (one session)**

- Anthropic adapter only (Claude Opus 4.6)
- Family domain only
- Free-list step only
- Raw JSONL write, basic parser
- **`InformantRecord` written to `data/raw/informants.jsonl` with full provenance (provider request ID + SHA256 manifest)**
- **`scripts/qa_check.py` (§4.1.6) wired up and posting to `#lsb-alerts` on failure**
- Test with a fixture so the Coder doesn't burn the API budget
- `scripts/cost_report.py` wired up with basic per-run cost tracking (the full three-tier defense is Phase 1's exit criterion for this milestone — see §6.2)
- Spend cap enforcement: `CDB_MAX_SPEND_USD` env var read by the runner; hard halt at 100%, warning logged at 80%

**Milestone B — full multi-provider collection (follow-on)**

- OpenRouter adapter and Hugging Face Inference Providers adapter wired for the full 12-model slate (exact IDs per §3.2 `ModelRef` and the locked list in §7)
- `collection_method` on each `ModelRef` set to `anthropic_api`, `openrouter`, or `huggingface` according to which integration point served that run
- Per-provider account caps configured on each provider dashboard (~$100–150 each) as the second tier of the three-tier spend defense
- `scripts/build_db.py` first cut: read `informants.jsonl`, write `lsb.sqlite`. Enables the Phase 6+ open data bundle (§6.7).

**Phase 2 — Full protocol for one model (one session)**
- Add pile sort and pile interview steps
- Add aggregation across N runs
- Produce a consensus free list + co-occurrence matrix for Claude Opus on family

**Phase 3 — Analysis for one domain (one session)**
- MDS, clustering, consensus analysis
- Write first `DomainResult` to `data/results/family/0.1.json`
- Unit tests on synthetic matrices with known structure

**Phase 4 — Validation Phase (go/no-go, two sessions)**

This phase is a formal scientific gate, not a build step. Nothing downstream ships until Phase 4 passes. The gate has three quantitative criteria, each of which must be met before Phase 5 begins.

*4a. Multi-model collection.* Using the Phase 1 adapters (Anthropic, OpenRouter, Hugging Face Inference Providers as needed), run the full family domain across the 12-model slate with N=5 runs each. This produces the first real dataset.

*4b. Prompt-sensitivity study (`sensitivity.py`).* Generate 8 paraphrased variants of the free-list and pile-sort prompts (semantically equivalent, lexically different). Run 2 reference models (Claude Opus 4.6 and the current GPT flagship) across all 8 variants with N=5 each. Compute within-model variance (across prompt variants) and between-model variance (across the 12 models from 4a). Optionally extend to 16 or 32 variants on selected open-weight models via OpenRouter and/or Hugging Face Inference Providers within the monthly spend cap.

**Reframe (post-F1 SME review).** The sensitivity study is not only a validity check for prompt stability — it is the **primary variance-generation mechanism** for the Register 2 cultural consensus analysis and, more importantly, will be the *only* variance mechanism available for deterministic future architectures (neurosymbolic systems, zero-temperature models). The gate semantics of G1 (below) are unchanged; the explanatory framing is updated throughout the docs and the generated text.

**Phase 4b runbook — G1 failure response (binding, added post-F1 SME review).** If G1 fails in Phase 4b with a ratio in the borderline range (0.4–0.6), the correct response is to **add prompt variants** (expand beyond the default 8 toward 16–32) on the affected model pair, not to disqualify the domain. The reasoning: a borderline G1 in a small variant set often reflects insufficient variance coverage rather than genuine instability. Domain disqualification requires G1 failure *after* prompt-variant expansion has been attempted, plus an explicit Architect diagnostic. This line is load-bearing and must be read before the Phase 4b analysis begins, not discovered after a wrong-direction response to the first G1 failure.

*4b also includes the two-level saturation analysis* (§4.2.7): on the same two reference models plus one open-weight reference (Llama 3.1 70B), run the within-model Register 1 analysis at N = 5, 10, 15, 20, 25, 30 across family and holidays. Identify the empirical knee in each saturation curve (Spearman salience stability, OCI convergence, elbow-position stability, MDS Procrustes RMSE at N vs N+5). Set operational N at the knee plus a 20% safety margin. The saturation analysis piggybacks on the Phase 4b budget envelope and produces content surfaced on the public methodology page as a named methods contribution — **not** framed as publishable (per §1.5.6).

*4c. Human baseline acquisition.* Mark acquires a licensed, peer-reviewed human CDA dataset for family terms from the published anthropological literature (see §4.2.5 and `PHASE_4C_CANDIDATE_SOURCES.md` for sourcing policy and candidate sources). Extract the published similarity or co-occurrence matrix into `data/grounding/family/cooccurrence.csv` with full citation in `source.md`. ~3 hours of Mark's hands-on time for the literature pull. If no suitable published source is available, v1 ships without grounding and the benchmark makes relative claims only.

*4d. Bootstrap validation.* Run the full pipeline with B=500 bootstraps. Produce the first real MDS plot with confidence ellipses and the human baseline marker.

**Gate criteria — all three must pass:**

| # | Criterion | Threshold |
|---|---|---|
| G1 | **Stability:** within-model prompt variance must be smaller than between-model variance | ratio < 0.5 (within/between) |
| G2 | **Signal:** model-to-model similarity matrix must be statistically distinguishable from random | permutation test p < 0.01 |
| G3 | **Replication:** cluster structure must replicate across two independent full pipeline runs | Rand index ≥ 0.7 |

**If any gate fails:** pause. Do not proceed to Phase 5. The Architect agent writes a diagnostic report, and Mark decides whether to redesign prompts, add runs, drop models, or shelve the project. This is the real decision point for whether the core idea works.

**If all gates pass:** the benchmark has demonstrated that it measures *something* stable and non-random. The MDS plot from 4d is the first dashboard-ready artifact and the first social-pipeline-worthy finding. **Open data DOI minting via Zenodo (§6.7) is also unlocked at this point** — pre-validation, the bundle is hosted on Backblaze B2 without a DOI; post-validation, Zenodo issues a citable DOI for the v1 release.

**Phase 5 — Publish layer + minimal dashboard (two sessions)**
- `cdb_publish/build.py` implemented (§4.4): reads `data/results/`, writes static JSON to `apps/dashboard/public/data/`
- React scaffold with MDS plot + domain picker, fetching static JSON from `/data/`
- CSP and security headers deployed via `apps/dashboard/public/_headers`
- Ship to Cloudflare Pages staging URL (auto-deployed from main branch)

**Phase 6 — All domains, all visualizations (iterative)**
- Add domains one at a time
- Add heatmap, free-list compare
- **Add `DriftTracker` (§4.5) — cross-version drift plus the longitudinal date-slider scrubbing view of corpus-lens shift across collection dates** (consolidates the v0.6 TemporalView; same data layer, single component)
- **Open the researcher grounding submission process** (§4.2.5): publish `docs/grounding_submission_template.md`, the `.github/PULL_REQUEST_TEMPLATE/grounding_submission.md` PR template, the dashboard's "Submit your data" entry points (per `DESIGN_SYSTEM.md` §4.3), and the CI validation pipeline (schema check, format check, intersection report, gitleaks PII scan). If a researcher submission arrives during Phase 6, the CDA SME reviews and Mark merges, producing the first multi-baseline domain on the dashboard.
- Add journalist affordances (lede, export, summary, citation modal, embed modal)
- First public release of the open data bundle to Backblaze B2 + Zenodo DOI (§6.7)
- Methodology page first draft (Mark writes or reviews personally — not Coder-generated). The methodology page's "Human grounding" section (per `DESIGN_SYSTEM.md` §6.1 outline item 5) explicitly invites researcher contributions and links to the submission template.

**Phase 7 — Social pipeline (one session)**
- Triggers, drafters, review CLI
- GitHub Actions cron

**Phase 8 — Public release**
- `LICENSE` (Apache 2.0), `LICENSE-DATA` (CC-BY-4.0), `LICENSE-PROMPTS` (CC0), `LICENSE-OPENBUNDLE` (CC0) added to repo root (see §6.6 for the full licensing spec and §6.7 for the open bundle)
- `SECURITY.md` at repo root with responsible disclosure policy and the dedicated ProtonMail security contact address
- HuggingFace dataset release (raw responses + processed results under CC-BY-4.0)
- GitHub repo set to public
- Dashboard launched at `cogstructurelab.com` via Cloudflare Pages production deployment
- Methodology page finalized: names the CDA tradition, cites Romney, D'Andrade, Weller, Borgatti, and Batchelder, links to free-access originals where available, and acknowledges the grounding source (Romney et al. 1996) in full
- First batch of social posts queued and published via the Phase 7 pipeline

Phases 0–4 are the minimum viable benchmark and the scientific validation. If any Phase 4 gate fails, the dashboard is not built. This is the project's single most important design commitment: **we do not ship a pretty visualization layer over data we haven't validated.**

### 5.4 Agent Slack channels (added v0.7)

Three operational Slack channels carry agent and watchdog output. Each one has a different audience, a different latency expectation, and a different routing rule. Mark monitors all three; the agents post to the channels they own and read only their own.

| Channel | Posted by | Read by | Latency expectation | Routing rule |
|---|---|---|---|---|
| `#lsb-alerts` | `scripts/qa_check.py` (the QA_Runner, §4.1.6) | Mark, in real time | Minutes — this is the operational firefighting channel | **Bypasses the agent team entirely.** When QA fails on a freshly collected `InformantRecord`, the runner posts a structured failure message directly here. No agent task is enqueued, no GitHub issue is filed, the collection run continues. Mark looks at it, decides whether to pause collection / switch models / open a provider ticket, and acts. This is commitment #8 in §1 — software-only QA with direct human alerting. The agents do not subscribe to this channel and are not expected to. |
| `#lsb-cda-sme` | The CDA SME agent (§5.1) | Mark; the next agent in the pipeline (Coder for non-frontend, UI/UX agent for frontend) | Hours to a day — this is the development pipeline gating channel | Every CDA SME verdict goes here as a structured message: PASS / PASS-WITH-NOTES / FAIL, one-paragraph rationale, and the four-axis scorecard (protocol validity / analytical validity / claims validity / audience translation). PASS and PASS-WITH-NOTES allow the plan to flow forward; FAIL bounces it back to the Architect. Researcher grounding submission PR reviews (§4.2.5) also post here. |
| `#lsb-ui-ux` | The UI/UX agent (§5.1) | Mark; the Coder agent | Hours to a day — frontend development pipeline gating | Every UI/UX agent verdict goes here as a structured message: PASS / PASS-WITH-NOTES / FAIL, one-paragraph rationale, and the four-question scorecard (OWID design fidelity / 30-second journalist test / researcher reproduce-and-cite test / WCAG AA accessibility). Frontend plans only. The UI/UX agent also posts `DESIGN_SYSTEM.md` updates here when it has to extend the design system to cover a new visual question — Mark sees those updates as they happen rather than discovering them later in a diff. |

**Why three channels rather than one.** Mixing operational alerts with development verdicts means either the alerts get lost in the development noise or Mark trains himself to ignore the channel he's supposed to be watching most closely. Splitting them keeps the QA_Runner's "drop everything" signal distinct from the agents' "ready for review" signal. The two flavors of agent verdict (CDA SME and UI/UX) are split because frontend and methodology are different review surfaces with different reviewers — collapsing them would force the Coder to filter every message to figure out which ones apply to the current task.

**Webhook configuration.** Each channel has its own webhook URL stored in `.env` as `LSB_ALERTS_WEBHOOK_URL`, `LSB_CDA_SME_WEBHOOK_URL`, and `LSB_UI_UX_WEBHOOK_URL`. Never committed. The QA_Runner reads the alerts URL directly; the agent runtime reads the other two from the agent task environment. See `SECURITY_AND_HARDENING.md` §5 for the secrets handling around these.

---

## 6. Cross-cutting concerns

### 6.1 Reproducibility

- Every `DomainResult` embeds the exact versions of: prompt templates, domain definitions, analysis code (git SHA), and model IDs.
- `scripts/reproduce.py {result_json}` must be able to re-derive that result from raw data. This is a CI test.
- The published open data bundle (§6.7) provides the same guarantee to outside researchers: given the bundle and a Python environment, any researcher can rebuild `lsb.sqlite` from `informants.jsonl`, re-run the analysis pipeline, and reproduce every figure on the dashboard.

### 6.2 Cost tracking

Every `RawResponse` carries `cost_usd`. The spend cap is enforced via three independent tiers — each tier catches failures the others miss.

**Tier 1 — Runtime cap (in-process).** The collection runner reads `CDB_MAX_SPEND_USD` from the environment (default: `300`). Before each API call it checks cumulative spend for the current calendar month against this value. At 80% it logs a warning. At 100% it halts cleanly — writes the current run to the raw lake, flushes any in-flight state, and exits with a non-zero code and a clear message. No API call is made after the cap is reached. The cap value is set in `.env` and must never be committed.

**Tier 2 — Per-provider account caps.** Each provider dashboard (Anthropic, OpenAI, Google AI Studio, OpenRouter) has a hard monthly spending limit set to approximately $100–150. These are configured directly in each provider's billing settings, independent of the codebase. If Tier 1 fails (e.g., due to a bug in the runner, a parallel process, or a different project using the same key), Tier 2 catches runaway spend before it reaches the monthly ceiling. Tier 2 caps should sum to approximately the Tier 1 cap — if `CDB_MAX_SPEND_USD=300`, set individual caps so no single provider exceeds $150.

**Tier 3 — Weekly cost reports.** `scripts/cost_report.py` aggregates spend from the raw lake by model, domain, and time range and prints a summary. Running it weekly gives Mark visibility into burn rate before problems compound. In Phase 6+, a GitHub Actions cron job runs `cost_report.py --month current` every Monday and writes the output to `data/cost_reports/{YYYY-MM-DD}.txt` (git-tracked, small). Any week where projected monthly spend exceeds 80% of the cap triggers a Slack/email alert (implementation: a simple threshold check in the cron job).

```bash
# view current month's spend by model
python scripts/cost_report.py --month current

# view a specific month
python scripts/cost_report.py --month 2026-03

# view all time, grouped by domain
python scripts/cost_report.py --all --group-by domain
```

**Anthropic prompt caching for orchestrator calls (added v0.6).** All static documents passed into agent API calls — `ARCHITECTURE.md`, `CLAUDE.md`, `SECURITY_AND_HARDENING.md`, `HOSTING_AND_DEV_OPS.md`, `PHASE_4C_CANDIDATE_SOURCES.md`, `PHASE_0_TASKS.md`, `docs/DATA_DICTIONARY.md`, the §1.5.4 language guardrails table, and any other long-lived context the orchestrator passes into Claude — **must use Anthropic prompt caching**. These documents are large, change rarely, and are passed into nearly every agent task. Without caching, every task pays the full input-token cost on every invocation. With caching, the per-task orchestrator cost drops by approximately 80%. Implementation: pass `cache_control={"type": "ephemeral"}` on the relevant content blocks per the Anthropic API docs. The Reviewer agent must reject any orchestrator call that passes one of the listed static documents without prompt caching enabled — this is a binding cost-control rule, not a stylistic preference. Per-document caching keys should be derived from the file's git SHA so that an updated document invalidates its own cache without forcing a full rebuild.

### 6.3 Secrets

`.env` with one key per provider. Never in the repo. Never in logs. The adapter base class scrubs keys from any request payload before writing to the raw lake.

**Account hardening requirements** (binding — see `SECURITY_AND_HARDENING.md` §5 for the full enrollment procedure):

- **Two YubiKey 5C NFC keys enrolled** on every critical account: GitHub, Cloudflare, domain registrar, each LLM provider, Backblaze B2, HuggingFace. Both keys enrolled before any account holds live data. One key on the keychain; one key in the fireproof safe with the backup drives.
- **Dedicated ProtonMail address** (`security@cogstructurelab.ai` once the domain is live; a standalone ProtonMail account before that) for security disclosures, provider account registration, and any security-relevant communications. Not connected to Mark's personal email.
- **Password manager** (1Password, Bitwarden, or KeePassXC) for every account credential. Recovery codes for every MFA-protected account stored in the password manager vault and printed to paper in the fireproof safe.
- **`gitleaks` pre-commit hook** (configured in P0-T9) blocks any commit containing an API key pattern. GitHub secret scanning provides a second layer on push.

### 6.4 Observability

v1: structured logging to stdout + rotating files. No Prometheus, no Datadog. If the social agent becomes flaky, add it then. The QA_Runner alert path to `#lsb-alerts` (§4.1.6) is the closest thing to monitoring v1 has, and it is intentional that the alert path is operational rather than metric-based — Mark wants to know about specific bad runs, not aggregate dashboards.

### 6.5 Ethics and disclosure

The benchmark is making public claims about named commercial products. Two guardrails:
1. Every published finding links to the exact prompts and raw responses that produced it. Providers can audit us. The open data bundle (§6.7) makes this auditing trivial: the verbatim prompts and verbatim responses are in `informants.jsonl`, indexed by `provider_request_id`, downloadable under CC0.
2. The methodology page explicitly names the limitations: single-language (English) v1, prompt sensitivity, temperature effects, training data staleness.

This is not a throwaway concern — the credibility of the benchmark rests on being auditable by people who don't trust us.

### 6.6 Licensing

LSB uses a split licensing model. The license applied depends on the type of content, not the directory structure. All four licenses are permissive and interoperable; together they mean anyone can reuse any part of the project for any purpose as long as they attribute (where required).

| Content type | License | Files / paths |
|---|---|---|
| Source code | **Apache 2.0** | All `.py`, `.ts`, `.tsx`, `.js`, `.yml`, `.toml` files; `scripts/`; `packages/`; `apps/dashboard/src/`; CI configs |
| Prompts and domain definitions | **CC0 1.0 Universal** (public domain dedication) | `prompts/`; `data/domains/` |
| Raw responses, processed results, grounding data | **CC-BY-4.0** | `data/raw/`; `data/processed/`; `data/results/`; `data/grounding/`; HuggingFace dataset release |
| **Open data bundle** (added v0.6) | **CC0 1.0 Universal** | `data/open_bundle/` (`informants.jsonl`, `lsb.sqlite`, `build_db.py`, `DATA_DICTIONARY.md`) and the Backblaze B2 / Zenodo distribution. See §6.7. |
| Documentation and methodology text | **CC-BY-4.0** | `docs/`; `README.md`; `ARCHITECTURE.md`; methodology page on `cogstructurelab.com` |

**Why Apache 2.0 for code, not MIT:** Apache 2.0 includes an explicit patent grant, which matters if the project's methodology is novel enough to attract patent claims from commercial actors. The practical difference for users is negligible; the protection for the project is real.

**Why CC0 for prompts:** prompts are the most re-used part of any benchmark. CC0 removes all ambiguity — no attribution required, no license compatibility question. Anyone can take the prompts and run them on their own models without any obligation. This is a feature: it makes the benchmark more useful and makes independent replication trivially legal.

**Why CC0 for the open data bundle, not CC-BY:** the bundle is the researcher reproducibility artifact. The whole point is that any researcher can pick it up, rebuild the database, re-run the analysis, and republish derivative work without legal friction. CC0 removes the attribution requirement entirely and makes downstream reuse maximally frictionless. Attribution is still strongly encouraged via the data dictionary and the Zenodo DOI, but not legally required. The CC-BY license still applies to the in-repo `data/raw/` and `data/processed/` artifacts because those are the working set, not the published distribution.

**Why CC-BY-4.0 for data:** CC-BY is the de-facto standard for research datasets. It allows commercial and non-commercial use, modification, and redistribution as long as the source is attributed. This is what maximizes the data's impact while ensuring the project gets credit for producing it.

**Romney et al. (1996) grounding data — additional attribution requirement.** The human baseline data in `data/grounding/family/` is derived from Romney, A. K., Boyd, J. P., Moore, C. C., Batchelder, W. H., & Brazill, T. J. (1996), *PNAS* 93(10), 4699–4705 (PMC: PMC39344). Any redistribution of `data/grounding/family/` must cite this paper in full. The citation is documented in `data/grounding/family/source.md`. This is not a license restriction imposed by LSB — it is standard scholarly attribution practice for published research data, and the CC-BY license already requires it.

**License files at repo root:**

```
LICENSE               # Apache 2.0 — applies to source code
LICENSE-DATA          # CC-BY-4.0 — applies to data/raw/, data/processed/, data/results/, data/grounding/, docs/
LICENSE-PROMPTS       # CC0 1.0 — applies to prompts/ and domain definitions
LICENSE-OPENBUNDLE    # CC0 1.0 — applies to data/open_bundle/ and the Backblaze B2 distribution (§6.7)
```

The `README.md` license summary section displays all four with the per-category breakdown. The HuggingFace dataset card repeats the CC-BY-4.0 and Romney attribution requirement. The Backblaze B2 and Zenodo distributions repeat the CC0 dedication for the open bundle. Adding or changing any license requires Architect sign-off — license changes are breaking changes for downstream consumers.

### 6.7 Open Data Policy (added v0.6)

LSB publishes its full result set as open data. This section is the contract.

**What is published:**

| Artifact | Format | License | Notes |
|---|---|---|---|
| `informants.jsonl` | One `InformantRecord` (§3.2) per line, append-only, UTF-8 | **CC0** | The canonical raw data of LSB. Includes verbatim prompts, verbatim responses, full provider response objects, provider request IDs, and SHA256 manifests. |
| `lsb.sqlite` | SQLite database, single file | **CC0** | Generated from `informants.jsonl` by `build_db.py`. Tables for `informants`, `freelist_items`, `pilesort_cells`, `interview_labels`. Indexed for typical research queries. |
| `build_db.py` | Python script | Apache 2.0 (code) | The build script itself, included in the bundle so the bundle is self-rebuilding. Pure stdlib + `sqlite3` + `pydantic`. |
| `DATA_DICTIONARY.md` | Markdown | CC-BY-4.0 | Field-by-field documentation of `InformantRecord` and the SQLite schema. Required deliverable per §4.3. |
| Prompt templates | Markdown | **CC0** (already, per §6.6) | Copy of `packages/cdb_collect/prompts/v1/` included for full reproducibility without cloning the repo. |

**What is *not* published:**

- **API keys** — never. Anywhere. The bundle build script verifies that no `.env` file or key-shaped string is present in the bundle directory before upload.
- **Cost reports** (`data/cost_reports/`) — internal financial information. Spend totals and per-provider breakdowns are LSB's internal accounting and not relevant to the research artifact.
- **Backup snapshots, security logs, or anything from `SECURITY_AND_HARDENING.md` workflows.**
- **Pre-Phase-4 data.** The bundle is published only after the Phase 4 validation gates have passed. Pre-validation collection runs are kept locally for the historical record but are not part of the public distribution — releasing data the project itself has not validated would undermine the validation gate's purpose.

**Hosting:**

- **Primary distribution: Backblaze B2.** A public bucket at a stable URL (the URL is documented in the bundle's `README.md` and in the methodology page). Backblaze is chosen for cost (~$5/month for the expected data volume), egress economics (B2 has a free egress allowance to Cloudflare's CDN that the project can use if traffic grows), and operational simplicity (single-tenant, no auth required for public reads).
- **DOI minting: Zenodo.** After the Phase 4 validation gates pass, the bundle is uploaded to Zenodo, which mints a DOI and provides versioned permanent storage. The DOI is the canonical citation for any researcher referencing LSB data. Pre-validation, the bundle exists on Backblaze B2 without a DOI — researchers using pre-validation data are explicitly told it is preliminary.
- **Mirror: HuggingFace Datasets.** The same bundle is also published as a HuggingFace dataset, retaining the CC-BY-4.0 designation on the working data and CC0 on the bundle artifacts. HuggingFace is the discovery surface for ML researchers; Backblaze + Zenodo is the citation surface for academic researchers.

**Update cadence:** the bundle is rebuilt on every release (a release = a new analysis version published to the dashboard). Each release is a new Zenodo version (Zenodo's versioning model preserves prior DOIs). Old versions are never deleted.

**Researcher reproducibility guarantee:** any researcher who downloads the bundle, installs Python ≥ 3.11, and runs `python build_db.py informants.jsonl lsb.sqlite` will end up with a SQLite database byte-identical (modulo timestamps) to the one LSB itself uses internally. Combined with the prompt templates (also in the bundle, also CC0) and the published code (Apache 2.0 on the LSB GitHub repo), any figure on the LSB dashboard can be reproduced from open inputs without any LSB-specific tooling beyond standard Python. The Reviewer agent must reject any change that breaks this guarantee — for example, a refactor of `build_db.py` that depends on a non-stdlib package without bumping the bundle's documented requirements, or a schema change that doesn't propagate into the bundle's `DATA_DICTIONARY.md`.

**What this is *not*:** the open data bundle is not a "data product" with a SLA, a query interface, or a maintained API. It is a static research artifact — a snapshot of the raw data with the tools needed to use it. Researchers wanting more than that are pointed to the LSB GitHub repository and the Cognitive Structure Lab dashboard.

---

## 7. Resolved decisions log

All open decisions from §7 of v0.3.1 are resolved as of v0.4. The table below records each decision, its resolution, and where the implementation lives in this document. This section is a changelog for architectural decisions; it is not a task list and does not block any phase.

| # | Decision | Resolution | Implemented in |
|---|---|---|---|
| 1 | **Hosting.** Cloudflare Pages vs. Vercel vs. self-host. | **Cloudflare Pages.** Free tier, global CDN, auto-deploy from main branch, `_headers` file for CSP enforcement. No Cloudflare Workers needed — the static publish architecture eliminates any server-side compute requirement. | §4.4, §4.4.3, §4.4.4 |
| 2 | **Budget cap for collection runs.** What's the monthly ceiling? | **$300/month** with three-tier defense: (1) `CDB_MAX_SPEND_USD=300` runtime cap with hard halt at 100% and warning at 80%, (2) per-provider account caps of ~$100–150 each on every provider dashboard, (3) weekly `cost_report.py` run with projected-spend alerting. | §4.1.3, §6.2 |
| 3 | **Model inclusion list for v1.** How many models, which ones? | **12-model slate** filtered on three axes: origin (US, EU, China), openness (closed-weight, open-weight), and collection method (`anthropic_api`, `openrouter`, `huggingface`). Models are reached only via the three remote APIs in §5.3 Phase 1 — no local mirror. Exact model IDs per §3.2 and the locked list in this table's era. | §3.2 ModelRef schema, §4.1.3, §5.3 Phase 1 |
| 4 | **Domain order.** Which domains ship in v1, in what order? | **family → holidays → food.** Family is the most interpretable and is grounded (Romney 1996). Holidays has the most visually obvious finding for a journalist. Food produces strong cross-model divergence. These three constitute a credible v1. | §5.3 Phase 4a, Phase 6 |
| 5 | **Benchmark name.** "Cultural Domain Benchmark" is unmemorable. | **Latent Structure Benchmark (LSB)** for the benchmark; **Cognitive Structure Lab** for the website at `cogstructurelab.com` (with `cogstructurelab.ai` owned and redirecting — v0.5). Two-name split intentional — each name optimizes for its job. | §1.6 |
| 6 | **Licensing.** Code: MIT or Apache 2.0? Data: CC-BY? Prompts: CC0? | **Apache 2.0** (code), **CC-BY-4.0** (data + docs), **CC0** (prompts), **CC0** (open data bundle, added v0.6). Four license files at repo root. Romney 1996 grounding data carries an additional attribution requirement in `data/grounding/family/source.md`. | §6.6, §6.7 |
| 7 | **Local model inclusion.** Include Ollama models? How labeled? | **Superseded (v0.5).** No Ollama; no on-prem inference. Open-weight models use **OpenRouter** and/or **Hugging Face Inference Providers** only. `ModelRef.collection_method` is `openrouter` or `huggingface` (or `anthropic_api` for Claude). | §3.2 ModelRef schema, §4.1.3, §5.3 Phase 1 |
| 8 | **ArXiv timing.** When does the paper go up? | **REMOVED (v0.3).** No paper. The dashboard's methodology page is the canonical reference. | §1.5.6 |
| 9 | **Grounding data source for family terms.** | **RESOLVED (v0.2.1).** Licensed, peer-reviewed published data only. Primary source: Romney et al. (1996), PNAS, PMC free full text. See `PHASE_4C_CANDIDATE_SOURCES.md`. | §4.2.5, §6.6 |
| 10 | **Prompt-sensitivity variant count.** 4 variants enough? | **8 variants** at the API gate (Phase 4b). 16–32 variants optionally on open-weight models via OpenRouter/Hugging Face within budget (v0.5 — no local stretch). | §4.1.3, §5.3 Phase 4b |
| 11 | **FastAPI vs. static JSON.** Retain FastAPI for the drift endpoint? | **Static JSON only.** The drift join is done at publish time by `cdb_publish/build.py`. No server. `cdb_api` renamed to `cdb_publish`. | §4.4, §4.4.5 |
| 12 | **Cloudflare Pages build config.** Build command, output directory, branch triggers? | Build: `npm run build`. Output: `apps/dashboard/dist/`. Auto-deploy on push to `main`. | §4.4.3 |
| 13 | **Sensitivity study model selection.** Which 2 reference models for Phase 4b? | **Claude Opus 4.6** and the **current GPT flagship.** Maximizes origin × provider spread for the stability claim. | §5.3 Phase 4b |
| 14 | **Local mirror hardware.** When does local collection start? | **Removed (v0.5).** No local mirror hardware milestone. Collection is VPS + Anthropic / OpenRouter / Hugging Face Inference Providers APIs only. | §5.3 Phase 1 |
| 15 | **`cdb_api` package rename.** | Renamed to `cdb_publish`. Repo layout, CLAUDE.md, P0-T4, and all internal references updated. | §2, §4.4, §5.2 |
| 16 | **Security contact email.** What email goes in `SECURITY.md` before the domain is live? | **Dedicated standalone ProtonMail account** pre-launch; replaced by `security@cogstructurelab.ai` once the domain is live. | §6.3, `SECURITY_AND_HARDENING.md` §5 |
| 17 | **YubiKey purchase.** Two YubiKey 5C NFC, worth it? | **Yes.** Two keys enrolled on every critical account before any live data is stored. | §6.3 |
| 18 | **Backup destination.** Synology only, or add offsite? | **Both.** Backblaze B2 (~$5/month) + fireproof safe. They fail differently. | `HOSTING_AND_DEV_OPS.md` |
| 19 | **Penetration test before launch.** Paid pentest or friendly review? | **Friendly review only for v1.** Paid pentest deferred unless the project gets significant traction. | `SECURITY_AND_HARDENING.md` §10 |
| 20 | **Bug bounty.** Run one for v1? | **Parked for v1.** Revisit if traffic grows meaningfully. | `SECURITY_AND_HARDENING.md` §10 |
| 21 | **Cloudflare paid tier.** Upgrade for WAF/bot management? | **Free tier for v1.** Pro tier deferred until reputational attackers become a real pattern. | `SECURITY_AND_HARDENING.md` §10 |
| 22 | **`unsafe-inline` in CSP.** Tailwind forces it for styles — accept or eliminate? | **Accept for v1** with Reviewer tracking. Drop `'unsafe-inline'` if build moves to fully external stylesheets. | `SECURITY_AND_HARDENING.md` §3.1 |
| 23 | **Phase 0 scope.** Add security tasks to Phase 0 or defer? | **Add to Phase 0.** P0-T9 (security scaffolding) and P0-T10 (CSP + `_headers`) are Phase 0 deliverables. Phase 0 is now 10 tasks. | `PHASE_0_TASKS.md` P0-T9, P0-T10 |
| 24 | **`data/cost_reports/` tracking.** Git-tracked or git-ignored? | **Git-tracked.** Small text files; free audit trail of spend over time. Written by the weekly cron. | §6.2 |

---

## 8. What's explicitly out of scope for v1

Listing these to keep the Coder agent from scope-creep:

- User accounts, saved views, API keys for third parties
- Realtime collection (everything is batch)
- Any domain not in English (v2)
- Multi-turn CDA protocols (e.g., triadic comparisons) — only free list + pile sort + interview for v1
- Fine-grained cost prediction / budgeting UI
- A mobile-optimized dashboard (desktop-first is fine; mobile-readable is the bar)
- Comments, voting, community submission of domains

---

## 9. Glossary

- **CDA** — Cultural Domain Analysis. The methodology described in Briefing §2.
- **Free list** — unordered enumeration task; the first CDA step.
- **Pile sort** — similarity-based grouping task; the second CDA step.
- **Pile interview** — naming task over the groups from the sort; the third CDA step.
- **Cognitive map** — an MDS plot where proximity = cognitive similarity.
- **Consensus score** — ratio of first to second eigenvalue in cultural consensus analysis. >3 means single shared culture.
- **Drift score** — Procrustes distance between MDS coordinates of two versions of the same model. Used both for cross-version drift across model releases and for the longitudinal date-slider scrubbing view inside `DriftTracker.tsx` (§4.5). v0.7 consolidated both modes into the single `DriftTracker` component to align with `DESIGN_SYSTEM.md` §3.2 / §3.6.
- **Run** — one execution of one CDA step for one `(model, domain)` pair. There are N runs per tuple.
- **Informant** — in CDA, the person being studied. Here, the model. Each run is treated as an independent informant observation.
- **Corpus lens** — the plain-language term for what LSB measures: the shape a model imposes on a domain, inherited from its training data. The methodologically precise version is "the latent categorical structure of a training corpus, refracted through a model's training and alignment pipeline." See §1.5.1. "Corpus lens" is for headlines, social posts, dashboard copy, and any audience that does not need the long form; the long form is for methodology pages and citations. The two are equivalent in meaning, not in audience.
- **InformantRecord** — the canonical full per-run subject record, defined in §3.2. One per `(model, domain, run_index)`. Captures model identity (including the exact version string returned by the API), collection conditions (endpoint, API version, temperature, top_p, max_tokens, system prompt verbatim), all three CDA step records (`FreelistRecord`, `PileSortRecord`, `InterviewRecord` — each with verbatim prompts, verbatim responses, full provider response objects, parsed outputs, token counts, latency, stop reason), a SHA256 manifest covering every verbatim field, and the QA verdict from `qa_check.py`. The append-only stream of `InformantRecord` objects in `data/raw/informants.jsonl` is the canonical raw data of LSB and the primary content of the open data bundle (§6.7).
- **QA_Runner** — `scripts/qa_check.py`. Deterministic Python script that validates every freshly collected `InformantRecord` against six hardcoded checks (free-list count ≥10, run-to-run uniqueness ≥60%, binary-and-symmetric pile-sort matrix, latency <30s, output-token consistency, provider request ID present). Failures set `qa_passed=False` and post directly to `#lsb-alerts`. **Bypasses the agent team entirely** — the alert path is operational, not developmental. See §4.1.6 and §1 commitment 8.
- **DriftTracker** — the dashboard component (§4.5 `DriftTracker.tsx`) that visualizes both cross-version drift across model releases and longitudinal corpus-lens shift across collection dates per model family. Date-slider scrubbing (`DESIGN_SYSTEM.md` §3.6) lets users watch model points animate to their position at each historical collection date while human baseline markers stay anchored as fixed reference points. Unit of analysis is `model_version_returned` × `collection_date`, not `model_id` (because providers silently roll snapshots). Change metric is Procrustes drift score versus the first observation. Phase 6 deliverable; the data structure (verbatim version strings, append-only by collection date, all historical runs retained) must be in place from Phase 1 because the longitudinal view is retroactively unbuildable if early runs are missing or overwritten. v0.7 consolidates the v0.6 `TemporalView.tsx` into this single component to align with `DESIGN_SYSTEM.md`.
- **Baseline kind** — the `baseline_kind` field on `GroundingRef` (§3.2). Two values: `published` (extracted by Mark from peer-reviewed academic literature, e.g., Romney et al. 1996) and `researcher` (submitted by an external researcher via the GitHub PR workflow in §4.2.5). Renders differently on the MDS plot — published baselines as black stars (★), researcher baselines as gray diamonds (◆) — per `DESIGN_SYSTEM.md` §3.3.
- **Researcher grounding** — human CDA data contributed to LSB by an external researcher (anthropologist, linguist, cognitive scientist) via the GitHub PR workflow in §4.2.5. The researcher retains all rights to their data; LSB validates format, runs schema and PII checks in CI, the CDA SME reviews the methodology, Mark merges, and the new baseline appears on the dashboard with full attribution. v1 uses GitHub PR submission; v2 may add an in-app submission form. A domain may have zero, one, or many researcher baselines, alongside zero, one, or many published baselines.
- **Grounding states (0 / 1 / 2 / 3)** — the four display states defined in `DESIGN_SYSTEM.md` §4.1: State 0 (no human baselines available — a normal first-class state per §1.5.5), State 1 (published baseline only), State 2 (researcher baseline only), State 3 (multiple baselines, published + researcher or multiple researcher). Driven directly by the contents of `DomainResult.groundings` (§3.2): empty list = State 0, one entry = State 1 or 2 by `baseline_kind`, two or more entries = State 3.
- **DESIGN_SYSTEM.md** — the binding visual specification document for all frontend work on LSB. Owned by the UI/UX agent. Specifies design tokens, page architecture, the OWID-style article-with-explorer layout, the data explorer pattern, the four grounding-display states, the researcher submission UI, the methodology page structure, accessibility requirements, mobile behavior, and the component inventory. Required reading before any frontend task per CLAUDE.md item 14 (§5.2).
- **UI/UX agent** — Sonnet-class agent added in v0.7. Sits between the CDA SME and the Coder for frontend tasks only. The design conscience of the project. Reviews every frontend plan against four questions rooted in `DESIGN_SYSTEM.md`: OWID design fidelity, the 30-second journalist test, the researcher reproduce-and-cite test, and WCAG AA accessibility. Verdicts (PASS / PASS-WITH-NOTES / FAIL) post to `#lsb-ui-ux`. Owns `DESIGN_SYSTEM.md` and updates it before passing any plan through that requires a visual decision the design system does not yet cover. See §5.1.
- **`#lsb-alerts`** — the operational firefighting Slack channel where `scripts/qa_check.py` posts QA failures directly. Bypasses the agent team entirely (commitment #8 in §1). Mark monitors in real time. See §4.1.6, §5.4.
- **`#lsb-cda-sme`** — the development pipeline gating Slack channel where the CDA SME agent posts methodological verdicts (PASS / PASS-WITH-NOTES / FAIL with four-axis scorecard). Read by Mark and by the next agent in the pipeline. Also receives researcher grounding submission PR review verdicts. See §5.1, §5.4.
- **`#lsb-ui-ux`** — the frontend pipeline gating Slack channel where the UI/UX agent posts design verdicts (PASS / PASS-WITH-NOTES / FAIL with four-question scorecard) and `DESIGN_SYSTEM.md` updates. Read by Mark and the Coder. See §5.1, §5.4.
- **LSB / Latent Structure Benchmark** — the methodologically precise name for this project. Used in citation contexts, methodology pages, schema fields, and the repository name. The full phrase is canonical; "LSB" is the casual abbreviation. See §1.6.
- **Cognitive Structure Lab** — the public-facing website name and brand, hosted at **`cogstructurelab.com`**. Used in social posts, headlines, and the URL. Not a synonym for "LSB" — the two names have different jobs. See §1.6.
- **cogstructurelab.com** — primary production URL for the dashboard.
- **cogstructurelab.ai** — also owned; parked / redirects to **`cogstructurelab.com`** so legacy links and `.ai`-branded materials still resolve.
- **HuggingFace Inference Providers** — the Hugging Face hosted-inference surface used by LSB as one of three collection methods (alongside the Anthropic API and OpenRouter). Used for specialist open-weight models that are not well-routed through OpenRouter. `ModelRef.collection_method` value is `huggingface`. Replaces older references to "Hugging Face Inference API" — same surface, current product name.
- **Open data** — the LSB publication contract defined in §6.7. The published bundle (`informants.jsonl` + `lsb.sqlite` + `build_db.py` + `DATA_DICTIONARY.md` + prompt templates) is licensed CC0, hosted on Backblaze B2, mirrored to HuggingFace Datasets, and DOI-minted via Zenodo after the Phase 4 validation gates pass. Any researcher with the bundle can rebuild the SQLite database, re-run the analysis pipeline, and reproduce every figure on the dashboard without LSB-specific tooling.
- **lsb-agent-01** — the project VPS that runs `cdb_collect/runner.py`, `scripts/qa_check.py`, the cron jobs in `.github/workflows/`, and the social pipeline. Ordinary cloud infrastructure; not a special-purpose machine. No on-prem GPU, no local inference layer (per §5.3 Phase 1 and resolved decision #14).
- **Validation gate (G1 / G2 / G3)** — the three quantitative pass/fail criteria at the end of Phase 4. G1 = stability (within-model variance < between-model variance); G2 = signal (similarity matrix distinguishable from random, p < 0.01); G3 = replication (cluster structure reproduces across independent runs, Rand index ≥ 0.7). All three must pass before Phase 5 begins. See §5.3.
- **Bootstrap ellipse** — the 95% confidence ellipse drawn around each model's MDS point, derived by resampling runs with replacement B=500 times. Every MDS plot in the dashboard renders these ellipses; bare point estimates are forbidden. See §4.2.6.
- **GroundingRef** — the pydantic schema type that tracks the human CDA baseline injected as a virtual informant into the analysis pipeline. Fields include source citation, year, n_informants, MDS coordinates, and distance to nearest model. See §3.2.
- **Phase 1 (collection)** — unified phase: remote APIs only (Anthropic API, OpenRouter, Hugging Face Inference Providers) on project VPS; milestones A then B within §5.3. No Phase 1a/1b hardware split.
- **Three-axis filtering** — the model-selection and display filter applied to the 12-model slate: origin (US / EU / China) × openness (closed-weight / open-weight) × collection method (`anthropic_api` / `openrouter` / `huggingface`). The dashboard's `ModelFilter` component exposes all three axes. See §3.2, §4.5.
- **Spend cap three-tier defense** — the layered cost control: (1) `CDB_MAX_SPEND_USD` runtime cap in the collection runner, (2) per-provider account caps set in each provider's billing dashboard, (3) weekly `cost_report.py` run with projected-spend alerting. See §6.2.
- **`cdb_publish`** — the Python package responsible for reading `data/results/` and writing pre-shaped static JSON files to `apps/dashboard/public/data/` at build time. Replaces the former `cdb_api` FastAPI service. See §4.4.

---

*End of architecture document v0.7. Document is complete. Hand off to Architect agent — Architect to CDA SME, then (for frontend tasks) to UI/UX agent — to begin Phase 0.*

---

## v0.4 REVISION — PENDING EDITS CHECKLIST

**Status of this document:** ✅ **v0.7 current;** v0.4 checklist below retained for history. Safe to hand to the Architect agent.

**Completed in the partial revision (already in this file when this session began):**

- [x] Title, status block, changelog updated to v0.4
- [x] §0 guiding principle — removed API mention
- [x] §1 system overview diagram — FastAPI box → Publish layer
- [x] §1 core design commitments 3 and 5 — static-only architecture
- [x] NEW §1.6 — Project naming (LSB benchmark / Cognitive Structure Lab website split)
- [x] §2 Repository layout — `cdb_api` → `cdb_publish`, LICENSE files, SECURITY.md, CODEOWNERS, .github/, footer paragraph
- [x] §3.2 ModelRef schema — added `collection_method`, `quantization`, `open_weights`, `ca` origin, `source_notes`, schema notes block
- [x] §4.1.3 Sampling strategy — 8-variant sensitivity, spend cap reference
- [x] §4.1.5 Open decisions — marked RESOLVED with §7 pointer

**Completed in this session:**

- [x] §4.4 — full rewrite of "API layer (`cdb_api`)" → "Publish layer (`cdb_publish`)"
- [x] §4.5 Frontend — static JSON fetch note, CSP requirement (`connect-src 'self'`), reference to `SECURITY_AND_HARDENING.md` §3.1 and §3.3
- [x] §5.2 CLAUDE.md additions — references to all five companion docs added
- [x] §5.3 Phase plan — Phase 1 unified (v0.5: Anthropic / OpenRouter / HF APIs); Phase 5 FastAPI reference replaced with publish-layer + CSP; Phase 8 deliverables updated with license files, SECURITY.md, methodology page, cogstructurelab.com deployment
- [x] §6.2 Cost tracking — three-tier defense described in full
- [x] §6.3 Secrets — YubiKey 5C NFC enrollment, ProtonMail security contact, password manager + recovery codes in fireproof safe
- [x] NEW §6.6 — Licensing section with file-by-file table, Romney attribution requirement, three license files at repo root
- [x] §7 — converted to Resolved decisions log; all 24 decisions marked resolved with resolution and implementation pointer
- [x] §9 Glossary — added: LSB / Latent Structure Benchmark, Cognitive Structure Lab, cogstructurelab.com / .ai redirect, Validation Gate (G1/G2/G3), Bootstrap ellipse, GroundingRef, Phase 1 (unified collection), Three-axis filtering, Spend cap three-tier defense, `cdb_publish`

**Completed in v0.6 (this session):**

- [x] Title, status block, changelog updated to v0.6
- [x] §1 — added commitments 6–10 (no LLM in analysis; cryptographic provenance; software-only QA with direct alerting; open data; longitudinal model tracking)
- [x] §1.5.1 — added the **corpus lens** plain-language term, with audience-mapping table and Reviewer enforcement
- [x] §2 — added `docs/DATA_DICTIONARY.md`, `data/open_bundle/`, `scripts/qa_check.py`, `scripts/build_db.py`, `TemporalView.tsx`, `LICENSE-OPENBUNDLE`, fourth boundary rule (`cdb_analyze` no-LLM-imports)
- [x] §3.2 — added `FreelistRecord`, `PileSortRecord`, `InterviewRecord`, and the full `InformantRecord` schema with model identity, collection conditions, three CDA step records, SHA256 manifest, and QA verdict
- [x] §4.1.6 — new QA_Runner subsection with the six deterministic checks and the direct-to-`#lsb-alerts` bypass
- [x] §4.2 — added the binding **no-LLM-in-`cdb_analyze`** constraint at the top of the section
- [x] §4.2.3 — added a cross-reference noting the lede generator lives in `cdb_publish`, not `cdb_analyze`
- [x] §4.3 — rewritten to formalize the three parallel result representations (JSONL canonical / SQLite researcher-friendly / Parquet analysis); added `data/raw/informants.jsonl` and `data/open_bundle/`; named `docs/DATA_DICTIONARY.md` as a Phase 1 required deliverable
- [x] §4.5 — added the **TemporalView** component with Procrustes drift across collection dates, the Phase 6 / Phase 1 schema dependency, and the unit-of-analysis = `model_version_returned` × `collection_date` rule
- [x] §5.1 — added the **CDA SME** agent (Opus) row with the four-axis verdict (PASS / PASS-WITH-NOTES / FAIL) posted to `#lsb-cda-sme`
- [x] §5.1 Reviewer — added rules for `cdb_analyze` no-LLM-imports and `InformantRecord`/`DATA_DICTIONARY.md` co-update
- [x] §5.2 — added CLAUDE.md items 6, 12, 13 (data dictionary read; no LLM in cdb_analyze; CDA SME gating)
- [x] §5.3 — Phase 0 includes `InformantRecord` and `DATA_DICTIONARY.md`; Milestone A includes `qa_check.py` and `informants.jsonl`; Milestone B includes `build_db.py`; Phase 4 unlocks Zenodo DOI minting; Phase 6 includes TemporalView and the open bundle release
- [x] §6.2 — added the Anthropic prompt caching binding requirement for orchestrator calls
- [x] §6.6 — added the open data bundle row to the licensing table (CC0); added `LICENSE-OPENBUNDLE` to the file list; added the rationale for CC0 on the bundle vs CC-BY on the working data
- [x] NEW §6.7 — Open Data Policy: what is published, what is not, hosting on Backblaze B2, Zenodo DOI post-Phase-4, HuggingFace mirror, researcher reproducibility guarantee
- [x] §9 Glossary — added: corpus lens, InformantRecord, QA_Runner, temporal view, HuggingFace Inference Providers, open data, lsb-agent-01

**Completed in v0.7 (this session):**

- [x] Title, status block, audience, companion docs, changelog updated to v0.7
- [x] §1.5.5 — fully reframed: grounding is per-domain optional, multi-baseline supported, ungrounded is a normal first-class state, researcher submissions are a v1 feature (not v2)
- [x] §2 — added `DESIGN_SYSTEM.md` to repo root, restructured `data/grounding/{domain}/` → `data/grounding/{domain}/{baseline_id}/`, added `docs/grounding_submission_template.md`, added `.github/PULL_REQUEST_TEMPLATE/grounding_submission.md`, added UI/UX subagent slot
- [x] §3.2 — `DomainResult.grounding: GroundingRef | None` → `DomainResult.groundings: list[GroundingRef]` + `selected_baseline_id: str | None`
- [x] §3.2 — `GroundingRef` rewritten with `baseline_id`, `baseline_kind` (`published` | `researcher`), source fields, population description, method, IRB status, submitter fields (researcher only), MDS coordinate, optional bootstrap ellipse, item-set alignment fields
- [x] §4.2.5 — full rewrite supporting multi-baseline, both kinds, full v1 GitHub-PR researcher submission workflow with CI validation and CDA SME review, what's deferred to v2, citation discipline updated to three surfaces
- [x] §4.2.6 — bootstrap-grounding interaction updated for per-baseline ellipses
- [x] §4.4 — removed separate `temporal/` subdirectory; `drift/{model_family}.json` now serves both cross-version drift and longitudinal scrubbing
- [x] §4.5 — full rewrite: explicit `DESIGN_SYSTEM.md` cross-references and authority rule, four grounding-state architecture contract, `TemporalView.tsx` collapsed into `DriftTracker.tsx`, `DomainSlider.tsx` and `DateSlider.tsx` added, `ModelSelector.tsx` / `GroundingSelector.tsx` / `GroundingDetailPanel.tsx` / `SubmitGroundingModal.tsx` / `KeyFinding.tsx` / `CiteModal.tsx` / `EmbedModal.tsx` added to component inventory aligned with `DESIGN_SYSTEM.md` §11
- [x] §5.1 — added the **UI/UX agent** (Sonnet) row with the four-question scorecard (OWID design fidelity / 30-second journalist test / researcher reproduce-and-cite test / WCAG AA), positioned between CDA SME and Coder for frontend tasks only, ownership of `DESIGN_SYSTEM.md`, verdicts to `#lsb-ui-ux`
- [x] §5.1 — Architect, CDA SME, Coder, and Reviewer rows updated to reference the UI/UX gate; Coder explicitly forbidden from inventing visual decisions; Reviewer rule 6 added (frontend PRs require UI/UX verdict)
- [x] §5.1 — added the agent pipeline diagram showing the conditional UI/UX branch
- [x] §5.2 — added CLAUDE.md items 14 (read `DESIGN_SYSTEM.md` before any frontend task) and 15 (researcher grounding submission workflow); item 13 expanded to require UI/UX verdict for frontend tasks
- [x] §5.3 — Phase 6 plan rewritten: `DriftTracker` consolidates the v0.6 TemporalView; researcher grounding submission process opens in Phase 6 with PR template, dashboard entry points, CI validation, and a methodology page that explicitly invites contributions
- [x] NEW §5.4 — Agent Slack channels reference: `#lsb-alerts` (QA_Runner direct, bypasses agents), `#lsb-cda-sme` (CDA SME verdicts), `#lsb-ui-ux` (UI/UX agent verdicts and design system updates); webhook configuration noted
- [x] §9 Glossary — `Drift score` updated to reference the consolidated DriftTracker; `Temporal view` entry replaced with updated `DriftTracker` entry; added `Baseline kind`, `Researcher grounding`, `Grounding states (0/1/2/3)`, `DESIGN_SYSTEM.md`, `UI/UX agent`, `#lsb-alerts`, `#lsb-cda-sme`, `#lsb-ui-ux`

**Companion docs to update after the architecture doc is complete:**

- [ ] `PHASE_0_TASKS.md` — add P0-T9 (security scaffolding) and P0-T10 (CSP and security headers); add LICENSE file creation to P0-T2; add `InformantRecord` and `docs/DATA_DICTIONARY.md` to P0 deliverables; add `LICENSE-OPENBUNDLE` to the LICENSE task; **add the multi-baseline grounding directory layout to P0 schema work** (v0.7); **add the UI/UX agent definition and `#lsb-ui-ux` webhook setup to P0 agent scaffolding** (v0.7)
- [ ] `README.md` — does not yet exist; create stub with project name, one-paragraph description, license summary (now four licenses), link to `cogstructurelab.com`, link to the Backblaze B2 / Zenodo open data bundle once Phase 4 validation passes, and a short paragraph inviting researcher grounding submissions with a link to the submission template (v0.7)
- [ ] `docs/DATA_DICTIONARY.md` — does not yet exist; create as a Phase 0 / Phase 1 deliverable per §4.3. **Must document the new `groundings: list[GroundingRef]` field on `DomainResult` and every field on the expanded `GroundingRef` schema** (v0.7)
- [ ] `docs/grounding_submission_template.md` — does not yet exist; Phase 6 deliverable per §4.2.5. Specifies the required files (`source.md`, `items.txt`, `cooccurrence.csv`, optional `pile_sort_raw.csv`, `grounding_ref.json`), the format requirements, and the submission process (v0.7)
- [ ] `.github/PULL_REQUEST_TEMPLATE/grounding_submission.md` — does not yet exist; Phase 6 deliverable per §4.2.5. PR template prompting for rights confirmation, IRB status, CC-BY-4.0 redistribution intent, and submitter contact (v0.7)
- [ ] `CLAUDE.md` — append items 6, 12, 13 from §5.2 (data dictionary read; no LLM in cdb_analyze; CDA SME gating); **add items 14 (read `DESIGN_SYSTEM.md` before frontend) and 15 (researcher grounding submission workflow)** (v0.7); add `#lsb-alerts`, `#lsb-cda-sme`, `#lsb-ui-ux` to the Slack channel reference table
