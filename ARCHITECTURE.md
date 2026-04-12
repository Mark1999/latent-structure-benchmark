# Latent Structure Benchmark (LSB) — System Architecture

**Project name:** Latent Structure Benchmark (LSB)
**Public-facing site:** Cognitive Structure Lab — `cogstructurelab.com`
**Status:** Draft v0.5 — handoff document for the Claude Code development team
**Audience:** Architect / Coder / Reviewer / Tester agents + human reviewer (Mark)
**Companion docs:** `CDB_Briefing_Opus46.docx` (product vision), `CLAUDE.md` (team constitution), `SECURITY_AND_HARDENING.md`, `HOSTING_AND_DEV_OPS.md`, `PHASE_4C_CANDIDATE_SOURCES.md`, `PHASE_0_TASKS.md`

**Changelog:**
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

---

## 1.5 Scientific framing and known limitations

**This section is binding on every other part of the system.** The Reviewer agent must reject any prompt, lede template, dashboard copy, social post, or README text that contradicts it.

### 1.5.1 What CDB measures — the precise claim

CDB does **not** measure cultural worldviews. Worldviews require lived experience, and LLMs do not have lived experience. They synthesize statistical patterns from text corpora.

What CDB measures is:

> **The latent categorical structure of a training corpus, as refracted through a model's training and alignment pipeline, surfaced by applying Cultural Domain Analysis elicitation protocols to the model as if it were an informant.**

Unpack that:

- **Latent categorical structure** — how items within a domain cluster and relate, not what items exist or whether facts about them are correct.
- **Of a training corpus** — the proximate object of study is the text the model learned from, not the humans who produced that text. Cultural signal reaches CDB only through the corpus.
- **As refracted through a model's training and alignment pipeline** — pretraining, RLHF, constitutional fine-tuning, and system prompts all bend the output. CDB sees the sum, not any single stage.
- **Surfaced by applying CDA protocols** — the methodology is imported from cognitive anthropology. That does not import the ontological commitments of cognitive anthropology along with it. We are borrowing a microscope, not claiming the sample is alive.
- **As if it were an informant** — the "as if" is load-bearing. Treating the model as an informant is a methodological move, not a metaphysical one.

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
| "Model X's worldview" | "Model X's categorical structure" |
| "Cultural bias" (standalone) | "Categorical divergence from [baseline]" |
| "What the model understands" | "What the model's outputs pattern as" |

The lede generator (§4.2.4) receives this table as part of its system prompt and must not produce text containing the left-column phrases. The Reviewer agent spot-checks a sample of generated ledes per release.

### 1.5.5 The human grounding requirement

Claims of the form "Model A differs from Model B" are weaker than claims of the form "Model A sits closer to human consensus than Model B." For at least one domain — **family terms** is the obvious choice given the published anthropological literature and the project's Kodak origins — CDB includes a human CDA baseline as a reference point in the model-to-model MDS plot.

This is not optional. See §4.2.5 for the implementation. Without grounding, CDB can only make relative claims between models; with grounding, it can make absolute claims relative to a human reference. The difference determines whether the benchmark is interesting to anthropologists as well as to AI researchers.

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
├── README.md                      # public-facing
├── .claude/
│   └── agents/                    # Architect/Coder/Reviewer/Tester
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
│   │   │   └── huggingface.py     # Hugging Face Inference API (specialist open models)
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
│   ├── cdb_analyze/               # analysis layer
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
│       │   │   └── DriftTracker.tsx
│       │   ├── components/
│       │   └── api/
│       └── package.json
├── data/
│   ├── raw/                       # JSONL lake, append-only, git-ignored
│   ├── processed/                 # Parquet artifacts per run
│   ├── grounding/                 # human CDA baselines, git-tracked
│   │   └── family/
│   │       ├── source.md          # citation + methodology notes
│   │       └── cooccurrence.csv   # published human consensus matrix
│   └── results/                   # canonical processed JSON, source for cdb_publish
├── scripts/                       # CLI entry points
│   ├── collect.py
│   ├── analyze.py
│   ├── publish.py                 # invokes cdb_publish.build
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
- `SECURITY.md` — vulnerability disclosure policy, see `SECURITY_AND_HARDENING.md` §6.5
- `CODEOWNERS` — branch protection enforcement (Mark as sole owner pre-launch)
- `.github/workflows/` — CI pipelines (lint, test, publish, security scans)
- `.github/dependabot.yml` — dependency update automation, see security doc §4
- `.gitleaks.toml` — secret scanning configuration, see security doc §3.4

See §6.6 for the licensing rationale and the file-by-file mapping.

**Why this layout:** each `packages/cdb_*` module has a single responsibility and a clean contract (section 4). The Coder agent can be assigned one package at a time. The Reviewer agent enforces three boundary rules: `cdb_publish` never imports `cdb_collect` (publishing and collection must stay decoupled); the dashboard never imports any `cdb_*` Python package (the dashboard is a separate app that only consumes static JSON); `cdb_social` never writes to `data/raw/` or `data/processed/` (social-pipeline outputs go to a separate `out/social/` directory and never contaminate analysis artifacts).

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
#   was used: Anthropic API, OpenRouter, or Hugging Face Inference API. The
#   same logical model may appear more than once if invoked through different
#   gateways; those rows differ by collection_method and/or model_id string.
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
    grounding: GroundingRef | None        # human baseline if available, §4.2.5
    generated_lede: str                   # the no-friction journalist headline
    generated_at: datetime

class BootstrapEllipse(BaseModel):
    center: tuple[float, float]
    semi_major: float
    semi_minor: float
    rotation_rad: float
    n_bootstrap: int

class GroundingRef(BaseModel):
    """A human CDA baseline treated as a virtual informant in the MDS plot."""
    source_citation: str                  # full bibliographic citation
    source_url: str | None
    collected_year: int
    n_human_informants: int
    mds_coordinate: tuple[float, float]
    distance_to_nearest_model: float
    nearest_model_id: str
```

Notes:
- `DomainResult` is **the only type the frontend ever sees.** Everything upstream is an implementation detail.
- `mds_coordinates` here is **model-to-model** (the signature viz: models as points in cultural space). A second, per-domain **item-to-item** MDS lives in `FreeList`/`CooccurrenceMatrix` for the within-domain cognitive map. Keep these distinct — conflating them is the #1 likely bug.

---

## 4. Layer-by-layer architecture

### 4.1 Data collection layer (`cdb_collect`)

**Responsibility:** turn a `(ModelRef, Domain)` pair into a set of `RawResponse` records on disk. Nothing else.

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

Use structured output / JSON mode where available (Anthropic, OpenAI, Gemini, OpenRouter, Hugging Face Inference for most). For models without JSON mode, use a robust parser + retry-on-parse-failure up to 3 attempts.

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

One adapter per provider. All adapters return a uniform `AdapterResult` containing raw response, latency, cost, and the normalized text. The runner never sees provider-specific types.

**Concurrency:** `asyncio` with per-provider semaphores to respect rate limits. Default 3 concurrent per provider, configurable per adapter.

**Retry policy:** exponential backoff on 429/5xx, max 5 retries. Failed runs are written to `data/raw/failures.jsonl` for inspection — they are *not* silently dropped.

#### 4.1.3 Sampling strategy

The briefing mentions "multiple runs per model per domain to distinguish signal from prompt sensitivity noise." Concretely:

- **Default:** `N=5` runs per `(model, domain, step)` tuple.
- **Temperature:** 0.7 for free listing (we want variance to surface salience distribution), 0.3 for pile sorting (we want the model's modal categorization).
- **Seed variation:** where the provider supports it, use distinct seeds per run. Where it doesn't, variance comes from sampling temperature alone.
- **Prompt-sensitivity study (Phase 4b validation gate):** 8 prompt variants per step on 2 reference models (Claude Opus + GPT flagship) to estimate within-model variance for the G1 gate (§5.3). Cost is bounded — see §6.2 for the spend cap mechanics.
- **Extended sensitivity (optional):** 16–32 prompt variants on selected open-weight models via OpenRouter and/or Hugging Face Inference API within the monthly spend cap — useful for comparing provider-routing variance without any local inference layer.
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

**RESOLVED in v0.4 / v0.5.** Phase 1 collection uses three remote API surfaces only (Anthropic, OpenRouter, Hugging Face Inference API) on project VPS — no Mac Mini and no local Ollama mirror (v0.5). See §7 for the resolved-decisions log; `ModelRef.collection_method` values are `anthropic_api`, `openrouter`, and `huggingface`.

---

### 4.2 Analysis layer (`cdb_analyze`)

**Responsibility:** turn raw responses into `DomainResult` artifacts. Pure functions, no I/O except reading raw JSONL and writing processed Parquet.

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

#### 4.2.4 CLI

```bash
python scripts/analyze.py --domain family --analysis-version 0.1
python scripts/analyze.py --all --analysis-version 0.1
```

Idempotent. Running twice with the same version produces byte-identical output (modulo timestamps).

#### 4.2.5 Human grounding module (`grounding.py`)

**Why this exists:** claims of the form "Model A differs from Model B" are weaker than claims of the form "Model A sits closer to human consensus than Model B." See §1.5.5.

**What it does:** loads a published human CDA co-occurrence matrix from `data/grounding/{domain}/cooccurrence.csv` and injects it into the pipeline as a virtual informant labeled `human_baseline`. It appears in the MDS plot as a distinct marker (suggested: black star, larger than model points) and in the similarity heatmap as a reference row/column.

**Data format:**
```
data/grounding/family/
├── source.md           # citation, methodology, n_informants, year, domain list
├── items.txt           # canonical item set in the human study
└── cooccurrence.csv    # symmetric matrix, header row = items
```

**Item alignment:** the human and model item sets will not match exactly. The grounding loader takes the **intersection** of human items and each model's salient item set and computes similarity on that subset only. The item intersection size is displayed in the UI next to the grounding point, because a small intersection means a weaker comparison.

**Sourcing policy — decided.** CDB uses **licensed, peer-reviewed published human CDA data** as the grounding source. No original human data collection in v1. This is cleaner legally, stronger scientifically, and ties CDB directly into the established CDA literature rather than competing with it.

**v1 acquisition targets** (in priority order):

- **Family / kinship terms.** The primary target. Candidate sources include the D'Andrade American kinship studies (1970s–80s), Romney & D'Andrade's cognitive structure of English kin terms, and Weller & Romney's *Systematic Data Collection* worked examples. Several of these publish full similarity matrices in the articles themselves, which is the cleanest acquisition path — figures and tables in peer-reviewed articles are generally citable and reusable under fair use for non-commercial research purposes. The Architect agent should confirm specific licensing per source before use.
- **Color terms.** Berlin & Kay's *Basic Color Terms* data is widely used in the literature, well-documented, and has been reanalyzed many times. Second priority grounding domain; add in Phase 6 when the color domain is added.
- **Emotion terms.** Published cross-cultural data exists (Shaver, Schwartz, Kirson & O'Connor 1987 is a common reference) but is messier and the item sets vary. Defer to v2.
- **Other domains (holidays, food, justice, etc.).** No obvious published CDA baseline exists. These domains remain **ungrounded in v1** and are displayed without a human baseline marker.

**Acquisition workflow** (Phase 4c, replaces the original survey):

1. Architect agent identifies 2–3 candidate sources for family-terms grounding with full citations.
2. Mark reviews and confirms the preferred source (and confirms the institutional access path — JSTOR, university library, direct author contact).
3. Mark acquires the PDF/data, extracts the published similarity or co-occurrence matrix, and hands it to the Coder agent as a CSV plus a `source.md` file.
4. Coder agent normalizes into the `data/grounding/family/` schema, writes unit tests that verify the loaded matrix round-trips correctly, and validates the item set against the v1 family domain prompt.
5. Architect agent reviews item-set intersection coverage before Phase 4d runs.

**Acquisition is the one part of this project Mark does by hand.** The Coder agent cannot retrieve licensed academic content, and automated scraping of publishers would be both a licensing violation and bad practice. Budget ~2 hours of Mark's time for the literature pull and matrix extraction.

**Graceful degradation:** if the preferred source turns out to be unavailable or unusable (e.g., published aggregate only, no extractable matrix), the fallback is to proceed with an ungrounded family domain in v1 and flag grounding as a v1.1 priority. The Validation Phase gates (§5.3) do not require grounding to pass — grounding strengthens the findings but is not the signal test itself.

**Citation discipline.** Every grounding source is cited in full in two places: `data/grounding/{domain}/source.md` and the public methodology page on the dashboard. The dashboard tooltip on the baseline marker shows the short citation inline. Under no circumstances is grounding data displayed without attribution.

#### 4.2.6 Bootstrap uncertainty module (`bootstrap.py`)

**Why this exists:** the §3.1 review critique of "false precision" is correct unless every visualization shows uncertainty. Point estimates on an MDS plot look like they mean more than they do. Ellipses and confidence intervals prevent that.

**What it does:** for each `(model, domain)` pair with N raw runs, resample with replacement B=500 times and rerun the full analysis pipeline on each bootstrap sample. The outputs are distributions, not points:

- **MDS ellipses:** for each model, the bootstrap distribution of its 2D coordinates defines a 95% confidence ellipse (covariance of bootstrap coordinates, Procrustes-aligned to the reference solution).
- **Similarity heatmap CIs:** each cell carries a 95% CI from the bootstrap distribution.
- **Consensus score CI:** bootstrap distribution of the eigenvalue ratio.
- **Drift score CIs:** bootstrap Procrustes distances.

**Computational cost:** B=500 bootstraps × ~2s per pipeline run = ~15 minutes per domain. Trivial for v1. If this becomes a bottleneck at v2 scale, switch to B=200 and document the reduction.

**Display rule — enforced by the Reviewer agent:** no visualization in `apps/dashboard` may display a point estimate without its associated uncertainty. No exceptions. If the Coder adds a new viz that can't express uncertainty, it doesn't ship.

**Interaction with grounding:** the human baseline point in the MDS plot is also bootstrapped (resampling human informants with replacement) when the human data is available at the informant level. Where only the aggregate matrix is published, the baseline point is shown without an ellipse and labeled "published aggregate, uncertainty unavailable."

---

### 4.3 Storage

No database in v1. Files all the way down.

```
data/
├── raw/
│   ├── {domain}/
│   │   └── {model_family}/
│   │       └── {run_id}.json       # one RawResponse per file
│   └── failures.jsonl
├── processed/
│   └── {domain}/
│       └── {analysis_version}/
│           ├── free_lists.parquet
│           ├── cooccurrence.parquet
│           └── mds.parquet
└── results/
    └── {domain}/
        └── {analysis_version}.json # served directly by the API
```

- `data/raw/` is **append-only and git-ignored**, backed up to the Synology NAS on a nightly cron. This is the research corpus — losing it means losing the benchmark.
- `data/results/` is **git-tracked** (it's small — one JSON per domain per version). This makes the site's current state trivially reproducible and gives us free version history.
- `data/processed/` is **git-ignored and regeneratable** from raw.

**Upgrade path to a real database:** if v2 needs cross-domain queries or realtime collection, move to SQLite → DuckDB → Postgres in that order. Don't skip steps.

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
└── drift/
    └── {model_family}.json                # drift data across versions for one model family
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

**Data access — static JSON only.** The dashboard fetches data exclusively from the static JSON files written by `cdb_publish` (§4.4) at `cogstructurelab.com/data/...`. There are no runtime API calls to a backend, no WebSocket connections, and no third-party data endpoints. All fetch calls are same-origin — the JSON files are served from the same Cloudflare Pages deployment as the app itself.

**Content Security Policy.** The dashboard must ship with a strict CSP header. The `connect-src` directive is `'self'` only — no external hosts. This is enforced in `apps/dashboard/public/_headers` (Cloudflare Pages header file). See `SECURITY_AND_HARDENING.md` §3.1 for the full CSP spec and §3.3 for LLM-output sanitization rules that apply to lede text and any other model-generated content rendered in the dashboard. The Reviewer agent must reject any component that renders model-generated text via `dangerouslySetInnerHTML` or equivalent without the sanitization wrapper specified in §3.3.

**Visualization libraries:**
- **D3** for the MDS plot and free-list comparison (custom layouts, annotations, zoom, confidence ellipses)
- **Plotly** for the heatmap and drift tracker (fast to build, good defaults, built-in error bars)

**Uncertainty display is mandatory, not optional.** Every view renders the bootstrap outputs from §4.2.6:

- **MDSPlot** renders 95% confidence ellipses around each model point, not bare points. Ellipse opacity scales with `n_bootstrap`. The human grounding baseline (when present) appears as a distinct marker — suggested black star — with its own ellipse where available.
- **Heatmap** cells carry tooltips showing `similarity ± 95% CI`. Cells whose CI crosses the null value are shown with reduced saturation to signal "not statistically distinguishable."
- **FreeListCompare** shows per-item inclusion frequency across bootstrap samples as a small bar next to each term.
- **DriftTracker** shows error bars on every drift score, and a shaded "within-noise" band derived from the prompt-sensitivity study (§5.3).

A view that cannot express uncertainty does not ship. This is a Reviewer-enforced rule.

**Component structure:**

```
src/
├── App.tsx
├── views/
│   ├── MDSPlot.tsx              # the signature viz
│   ├── Heatmap.tsx              # cross-model similarity
│   ├── FreeListCompare.tsx      # side-by-side ranked lists
│   └── DriftTracker.tsx         # longitudinal model drift
├── components/
│   ├── DomainPicker.tsx
│   ├── ModelFilter.tsx
│   ├── VizSwitcher.tsx
│   ├── ExplainButton.tsx        # opens a modal with the lede + methodology
│   ├── ExportImageButton.tsx    # one-click watermarked PNG export
│   └── GenerateSummaryButton.tsx
├── api/client.ts                # typed fetch helpers for the static JSON files in public/data/
└── lib/
    └── watermark.ts             # SVG → PNG + watermark
```

**The journalist affordances are first-class components, not afterthoughts.** `ExportImageButton` is on every view. `GenerateSummaryButton` is on every view. The lede shows above every view without a click. This is what turns the benchmark into a distribution engine rather than a hobby site.

**Image export spec:**
- PNG, 1600×900 for social cards, 2000×2000 for high-resolution downloads
- Benchmark logo + URL watermark in bottom-right, ~4% of image height
- Embeds `tEXt` metadata: domain, models, analysis_version, generation timestamp
- Filename: `cdb_{domain}_{viz}_{version}.png`

**Accessibility:** the MDS plot must be interpretable without color — use shape + color together for model origin. Every viz has a "Read as table" toggle that shows the underlying numbers.

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

This is where the architecture meets your existing 4-agent pipeline.

### 5.1 Agent responsibilities on this project

| Agent | Role on CDB |
|---|---|
| **Architect** (Opus) | Owns this document. Decomposes features into Coder-sized tasks. Reviews Open Decisions with Mark before any code is written for an unresolved one. Never writes code. |
| **Coder** (Sonnet) | Implements one package or one feature at a time. Must read the relevant `cdb_core/schemas.py` before touching any other file. |
| **Reviewer** (Sonnet) | Enforces four rules: (1) schemas are only defined in `cdb_core`, (2) layer boundaries are respected (no API imports from collect, no frontend imports from analysis), (3) every new prompt template bumps `prompt_version`, (4) the §1.5.4 language guardrails — no generated text, dashboard copy, or README content may contain forbidden phrases like "worldview," "believes," or "thinks." |
| **Tester** (Sonnet) | Every package ships with fixtures in `tests/fixtures/` (canned model responses) so tests never hit real APIs. Runs pytest on Python packages, vitest on the dashboard. |

### 5.2 CLAUDE.md additions for this project

Your existing `CLAUDE.md` is the team constitution. For CDB, append a project section that says:

1. Read `ARCHITECTURE.md` before starting any task. **§1.5 is binding on all generated text.**
2. Read `SECURITY_AND_HARDENING.md` before touching `apps/dashboard/`, `packages/cdb_collect/`, or any CI/CD configuration. The Reviewer rules table in §9 of that document is enforced on every PR.
3. Read `HOSTING_AND_DEV_OPS.md` before any deployment-related task or any task that touches `.github/workflows/`, Cloudflare Pages config, or environment variables.
4. Read `PHASE_4C_CANDIDATE_SOURCES.md` before any task touching `data/grounding/`, `packages/cdb_analyze/grounding.py`, or the family-domain grounding workflow.
5. Read `PHASE_0_TASKS.md` for the full Phase 0 task list, acceptance criteria, and dependency graph. It is the canonical decomposition for the Coder agent's first session.
6. Never edit `cdb_core/schemas.py` without Architect sign-off. Schema changes ripple everywhere.
7. Prompt templates are versioned. Never edit a published prompt template in place — copy it to a new version directory.
8. No API keys in the repo. Use `.env` + `python-dotenv`; `.env.example` is tracked, `.env` is ignored.
9. No real model calls in tests. Use fixtures.
10. No point estimates without uncertainty in any visualization. See §4.2.6 and §4.5.

### 5.3 Suggested phased build plan

This is sized to be workable across a few focused sessions with your agent pipeline.

**Phase 0 — Skeleton (one session)**
- Repo scaffold, pyproject.toml, CLAUDE.md, this doc
- `cdb_core/schemas.py` with all types from section 3
- Empty package directories with `__init__.py` and docstrings
- CI: ruff + mypy + pytest on push
- See `PHASE_0_TASKS.md` for the full 10-task decomposition (P0-T1 through P0-T10), acceptance criteria, and dependency graph.

**Phase 1 — Collection layer (unified; VPS + remote APIs only)**

All collection runs use **three API endpoints** — no local inference mirror, no Ollama, no Mac-class edge hardware:

1. **Anthropic API** — Claude models (direct first-party integration).
2. **OpenRouter** — frontier closed models and many open-weight models through a single HTTP API (including long-tail and regional routes where applicable).
3. **Hugging Face Inference API** — specialist open models when OpenRouter is not the right fit.

The runner and adapters live on ordinary project VPS / CI infrastructure; scaling is by concurrency limits and the spend cap, not by adding on-prem GPUs.

**Milestone A — smallest vertical slice (one session)**

- Anthropic adapter only (Claude Opus 4.6)
- Family domain only
- Free-list step only
- Raw JSONL write, basic parser
- Test with a fixture so the Coder doesn't burn the API budget
- `scripts/cost_report.py` wired up with basic per-run cost tracking (the full three-tier defense is Phase 1's exit criterion for this milestone — see §6.2)
- Spend cap enforcement: `CDB_MAX_SPEND_USD` env var read by the runner; hard halt at 100%, warning logged at 80%

**Milestone B — full multi-provider collection (follow-on)**

- OpenRouter adapter and Hugging Face Inference adapter wired for the full 12-model slate (exact IDs per §3.2 `ModelRef` and the locked list in §7)
- `collection_method` on each `ModelRef` set to `anthropic_api`, `openrouter`, or `huggingface` according to which integration point served that run
- Per-provider account caps configured on each provider dashboard (~$100–150 each) as the second tier of the three-tier spend defense

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

*4a. Multi-model collection.* Using the Phase 1 adapters (Anthropic, OpenRouter, Hugging Face Inference as needed), run the full family domain across the 12-model slate with N=5 runs each. This produces the first real dataset.

*4b. Prompt-sensitivity study (`sensitivity.py`).* Generate 8 paraphrased variants of the free-list and pile-sort prompts (semantically equivalent, lexically different). Run 2 reference models (Claude Opus 4.6 and the current GPT flagship) across all 8 variants with N=5 each. Compute within-model variance (across prompt variants) and between-model variance (across the 12 models from 4a). Optionally extend to 16 or 32 variants on selected open-weight models via OpenRouter and/or Hugging Face Inference within the monthly spend cap.

*4c. Human baseline acquisition.* Mark acquires a licensed, peer-reviewed human CDA dataset for family terms from the published anthropological literature (see §4.2.5 and `PHASE_4C_CANDIDATE_SOURCES.md` for sourcing policy and candidate sources). Extract the published similarity or co-occurrence matrix into `data/grounding/family/cooccurrence.csv` with full citation in `source.md`. ~3 hours of Mark's hands-on time for the literature pull. If no suitable published source is available, v1 ships without grounding and the benchmark makes relative claims only.

*4d. Bootstrap validation.* Run the full pipeline with B=500 bootstraps. Produce the first real MDS plot with confidence ellipses and the human baseline marker.

**Gate criteria — all three must pass:**

| # | Criterion | Threshold |
|---|---|---|
| G1 | **Stability:** within-model prompt variance must be smaller than between-model variance | ratio < 0.5 (within/between) |
| G2 | **Signal:** model-to-model similarity matrix must be statistically distinguishable from random | permutation test p < 0.01 |
| G3 | **Replication:** cluster structure must replicate across two independent full pipeline runs | Rand index ≥ 0.7 |

**If any gate fails:** pause. Do not proceed to Phase 5. The Architect agent writes a diagnostic report, and Mark decides whether to redesign prompts, add runs, drop models, or shelve the project. This is the real decision point for whether the core idea works.

**If all gates pass:** the benchmark has demonstrated that it measures *something* stable and non-random. The MDS plot from 4d is the first dashboard-ready artifact and the first social-pipeline-worthy finding.

**Phase 5 — Publish layer + minimal dashboard (two sessions)**
- `cdb_publish/build.py` implemented (§4.4): reads `data/results/`, writes static JSON to `apps/dashboard/public/data/`
- React scaffold with MDS plot + domain picker, fetching static JSON from `/data/`
- CSP and security headers deployed via `apps/dashboard/public/_headers`
- Ship to Cloudflare Pages staging URL (auto-deployed from main branch)

**Phase 6 — All domains, all visualizations (iterative)**
- Add domains one at a time
- Add heatmap, free-list compare, drift tracker
- Add journalist affordances (lede, export, summary)
- Methodology page first draft (Mark writes or reviews personally — not Coder-generated)

**Phase 7 — Social pipeline (one session)**
- Triggers, drafters, review CLI
- GitHub Actions cron

**Phase 8 — Public release**
- `LICENSE` (Apache 2.0), `LICENSE-DATA` (CC-BY-4.0), `LICENSE-PROMPTS` (CC0) added to repo root (see §6.6 for the full licensing spec)
- `SECURITY.md` at repo root with responsible disclosure policy and the dedicated ProtonMail security contact address
- HuggingFace dataset release (raw responses + processed results under CC-BY-4.0)
- GitHub repo set to public
- Dashboard launched at `cogstructurelab.com` via Cloudflare Pages production deployment
- Methodology page finalized: names the CDA tradition, cites Romney, D'Andrade, Weller, Borgatti, and Batchelder, links to free-access originals where available, and acknowledges the grounding source (Romney et al. 1996) in full
- First batch of social posts queued and published via the Phase 7 pipeline

Phases 0–4 are the minimum viable benchmark and the scientific validation. If any Phase 4 gate fails, the dashboard is not built. This is the project's single most important design commitment: **we do not ship a pretty visualization layer over data we haven't validated.**

---

## 6. Cross-cutting concerns

### 6.1 Reproducibility

- Every `DomainResult` embeds the exact versions of: prompt templates, domain definitions, analysis code (git SHA), and model IDs.
- `scripts/reproduce.py {result_json}` must be able to re-derive that result from raw data. This is a CI test.

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

### 6.3 Secrets

`.env` with one key per provider. Never in the repo. Never in logs. The adapter base class scrubs keys from any request payload before writing to the raw lake.

**Account hardening requirements** (binding — see `SECURITY_AND_HARDENING.md` §5 for the full enrollment procedure):

- **Two YubiKey 5C NFC keys enrolled** on every critical account: GitHub, Cloudflare, domain registrar, each LLM provider, Backblaze B2, HuggingFace. Both keys enrolled before any account holds live data. One key on the keychain; one key in the fireproof safe with the backup drives.
- **Dedicated ProtonMail address** (`security@cogstructurelab.ai` once the domain is live; a standalone ProtonMail account before that) for security disclosures, provider account registration, and any security-relevant communications. Not connected to Mark's personal email.
- **Password manager** (1Password, Bitwarden, or KeePassXC) for every account credential. Recovery codes for every MFA-protected account stored in the password manager vault and printed to paper in the fireproof safe.
- **`gitleaks` pre-commit hook** (configured in P0-T9) blocks any commit containing an API key pattern. GitHub secret scanning provides a second layer on push.

### 6.4 Observability

v1: structured logging to stdout + rotating files. No Prometheus, no Datadog. If the social agent becomes flaky, add it then.

### 6.5 Ethics and disclosure

The benchmark is making public claims about named commercial products. Two guardrails:
1. Every published finding links to the exact prompts and raw responses that produced it. Providers can audit us.
2. The methodology page explicitly names the limitations: single-language (English) v1, prompt sensitivity, temperature effects, training data staleness.

This is not a throwaway concern — the credibility of the benchmark rests on being auditable by people who don't trust us.

### 6.6 Licensing

LSB uses a split licensing model. The license applied depends on the type of content, not the directory structure. All three licenses are permissive and interoperable; together they mean anyone can reuse any part of the project for any purpose as long as they attribute.

| Content type | License | Files / paths |
|---|---|---|
| Source code | **Apache 2.0** | All `.py`, `.ts`, `.tsx`, `.js`, `.yml`, `.toml` files; `scripts/`; `packages/`; `apps/dashboard/src/`; CI configs |
| Prompts and domain definitions | **CC0 1.0 Universal** (public domain dedication) | `prompts/`; `data/domains/` |
| Raw responses, processed results, grounding data | **CC-BY-4.0** | `data/raw/`; `data/processed/`; `data/results/`; `data/grounding/`; HuggingFace dataset release |
| Documentation and methodology text | **CC-BY-4.0** | `docs/`; `README.md`; `ARCHITECTURE.md`; methodology page on `cogstructurelab.com` |

**Why Apache 2.0 for code, not MIT:** Apache 2.0 includes an explicit patent grant, which matters if the project's methodology is novel enough to attract patent claims from commercial actors. The practical difference for users is negligible; the protection for the project is real.

**Why CC0 for prompts:** prompts are the most re-used part of any benchmark. CC0 removes all ambiguity — no attribution required, no license compatibility question. Anyone can take the prompts and run them on their own models without any obligation. This is a feature: it makes the benchmark more useful and makes independent replication trivially legal.

**Why CC-BY-4.0 for data:** CC-BY is the de-facto standard for research datasets. It allows commercial and non-commercial use, modification, and redistribution as long as the source is attributed. This is what maximizes the data's impact while ensuring the project gets credit for producing it.

**Romney et al. (1996) grounding data — additional attribution requirement.** The human baseline data in `data/grounding/family/` is derived from Romney, A. K., Boyd, J. P., Moore, C. C., Batchelder, W. H., & Brazill, T. J. (1996), *PNAS* 93(10), 4699–4705 (PMC: PMC39344). Any redistribution of `data/grounding/family/` must cite this paper in full. The citation is documented in `data/grounding/family/source.md`. This is not a license restriction imposed by LSB — it is standard scholarly attribution practice for published research data, and the CC-BY license already requires it.

**License files at repo root:**

```
LICENSE               # Apache 2.0 — applies to source code
LICENSE-DATA          # CC-BY-4.0 — applies to data/ and docs/
LICENSE-PROMPTS       # CC0 1.0 — applies to prompts/ and domain definitions
```

The `README.md` license summary section displays all three with the per-category breakdown. The HuggingFace dataset card repeats the CC-BY-4.0 and Romney attribution requirement. Adding or changing any license requires Architect sign-off — license changes are breaking changes for downstream consumers.

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
| 6 | **Licensing.** Code: MIT or Apache 2.0? Data: CC-BY? Prompts: CC0? | **Apache 2.0** (code), **CC-BY-4.0** (data + docs), **CC0** (prompts). Three license files at repo root. Romney 1996 grounding data carries an additional attribution requirement in `data/grounding/family/source.md`. | §6.6 |
| 7 | **Local model inclusion.** Include Ollama models? How labeled? | **Superseded (v0.5).** No Ollama; no on-prem inference. Open-weight models use **OpenRouter** and/or **Hugging Face Inference API** only. `ModelRef.collection_method` is `openrouter` or `huggingface` (or `anthropic_api` for Claude). | §3.2 ModelRef schema, §4.1.3, §5.3 Phase 1 |
| 8 | **ArXiv timing.** When does the paper go up? | **REMOVED (v0.3).** No paper. The dashboard's methodology page is the canonical reference. | §1.5.6 |
| 9 | **Grounding data source for family terms.** | **RESOLVED (v0.2.1).** Licensed, peer-reviewed published data only. Primary source: Romney et al. (1996), PNAS, PMC free full text. See `PHASE_4C_CANDIDATE_SOURCES.md`. | §4.2.5, §6.6 |
| 10 | **Prompt-sensitivity variant count.** 4 variants enough? | **8 variants** at the API gate (Phase 4b). 16–32 variants optionally on open-weight models via OpenRouter/Hugging Face within budget (v0.5 — no local stretch). | §4.1.3, §5.3 Phase 4b |
| 11 | **FastAPI vs. static JSON.** Retain FastAPI for the drift endpoint? | **Static JSON only.** The drift join is done at publish time by `cdb_publish/build.py`. No server. `cdb_api` renamed to `cdb_publish`. | §4.4, §4.4.5 |
| 12 | **Cloudflare Pages build config.** Build command, output directory, branch triggers? | Build: `npm run build`. Output: `apps/dashboard/dist/`. Auto-deploy on push to `main`. | §4.4.3 |
| 13 | **Sensitivity study model selection.** Which 2 reference models for Phase 4b? | **Claude Opus 4.6** and the **current GPT flagship.** Maximizes origin × provider spread for the stability claim. | §5.3 Phase 4b |
| 14 | **Local mirror hardware.** When does local collection start? | **Removed (v0.5).** No local mirror hardware milestone. Collection is VPS + Anthropic / OpenRouter / Hugging Face Inference APIs only. | §5.3 Phase 1 |
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
- **Drift score** — Procrustes distance between MDS coordinates of two versions of the same model.
- **Run** — one execution of one CDA step for one `(model, domain)` pair. There are N runs per tuple.
- **Informant** — in CDA, the person being studied. Here, the model. Each run is treated as an independent informant observation.
- **LSB / Latent Structure Benchmark** — the methodologically precise name for this project. Used in citation contexts, methodology pages, schema fields, and the repository name. The full phrase is canonical; "LSB" is the casual abbreviation. See §1.6.
- **Cognitive Structure Lab** — the public-facing website name and brand, hosted at **`cogstructurelab.com`**. Used in social posts, headlines, and the URL. Not a synonym for "LSB" — the two names have different jobs. See §1.6.
- **cogstructurelab.com** — primary production URL for the dashboard.
- **cogstructurelab.ai** — also owned; parked / redirects to **`cogstructurelab.com`** so legacy links and `.ai`-branded materials still resolve.
- **Validation gate (G1 / G2 / G3)** — the three quantitative pass/fail criteria at the end of Phase 4. G1 = stability (within-model variance < between-model variance); G2 = signal (similarity matrix distinguishable from random, p < 0.01); G3 = replication (cluster structure reproduces across independent runs, Rand index ≥ 0.7). All three must pass before Phase 5 begins. See §5.3.
- **Bootstrap ellipse** — the 95% confidence ellipse drawn around each model's MDS point, derived by resampling runs with replacement B=500 times. Every MDS plot in the dashboard renders these ellipses; bare point estimates are forbidden. See §4.2.6.
- **GroundingRef** — the pydantic schema type that tracks the human CDA baseline injected as a virtual informant into the analysis pipeline. Fields include source citation, year, n_informants, MDS coordinates, and distance to nearest model. See §3.2.
- **Phase 1 (collection)** — unified phase: remote APIs only (Anthropic API, OpenRouter, Hugging Face Inference API) on project VPS; milestones A then B within §5.3. No Phase 1a/1b hardware split.
- **Three-axis filtering** — the model-selection and display filter applied to the 12-model slate: origin (US / EU / China) × openness (closed-weight / open-weight) × collection method (`anthropic_api` / `openrouter` / `huggingface`). The dashboard's `ModelFilter` component exposes all three axes. See §3.2, §4.5.
- **Spend cap three-tier defense** — the layered cost control: (1) `CDB_MAX_SPEND_USD` runtime cap in the collection runner, (2) per-provider account caps set in each provider's billing dashboard, (3) weekly `cost_report.py` run with projected-spend alerting. See §6.2.
- **`cdb_publish`** — the Python package responsible for reading `data/results/` and writing pre-shaped static JSON files to `apps/dashboard/public/data/` at build time. Replaces the former `cdb_api` FastAPI service. See §4.4.

---

*End of architecture document v0.5. Document is complete. Hand off to Architect agent to begin Phase 0.*

---

## v0.4 REVISION — PENDING EDITS CHECKLIST

**Status of this document:** ✅ **v0.5 current;** v0.4 checklist below retained for history. Safe to hand to the Architect agent.

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

**Companion docs to update after the architecture doc is complete:**

- [ ] `PHASE_0_TASKS.md` — add P0-T9 (security scaffolding) and P0-T10 (CSP and security headers); add LICENSE file creation to P0-T2
- [ ] `README.md` — does not yet exist; create stub with project name, one-paragraph description, license summary, link to `cogstructurelab.com`
