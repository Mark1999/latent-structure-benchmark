# Latent Structure Benchmark (LSB)

**Cognitive Structure Lab — [cogstructurelab.com](https://cogstructurelab.com)**

*A categorical-structure map of how frontier LLMs organize everyday vocabulary, built with Cultural Domain Analysis. Open data, reproducible, model-to-model.*

The **Latent Structure Benchmark (LSB)** applies Cultural Domain Analysis (CDA) elicitation protocols to large language models as if the models were informants. It surfaces the **corpus lens** — the categorical structure of a model's training corpus, refracted through training and alignment — by running the same free-list, pile-sort, and pile-interview protocols across many models on the same everyday domains (family terms, holidays, food). The result is a comparative map of how different models organize the same vocabulary, with verbatim prompts, verbatim responses, and reproducible analysis code published openly.

LSB **does not measure** cultural worldview, belief, or cognition. Models do not have lived experience; they synthesize statistical patterns from text corpora. The "as-if-informant" framing is methodological, not metaphysical: we are borrowing a microscope from cognitive anthropology, not claiming the sample is alive. Every dashboard surface, every social post, and every line of README copy is careful about this distinction.

LSB is a website that uses research methods, not a research project that has a website. The interactive dashboard at [cogstructurelab.com](https://cogstructurelab.com) is the primary deliverable; the benchmark, the open data bundle, and the analysis pipeline all exist to make the dashboard credible, useful, and discoverable. The originating question is exploratory — *what happens if you give a large language model a CDA free-list / pile-sort / interview?* — and the answer is the data itself, released for the community to interpret.

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

## Licenses

LSB ships under a split licensing model:

| Content type | License |
|---|---|
| Source code (Python, TypeScript, configs) | **Apache 2.0** |
| Prompts and domain definitions | **CC0 1.0 Universal** |
| Raw responses, processed results, documentation | **CC-BY-4.0** |
| Open data bundle (HuggingFace + Zenodo distribution) | **CC0 1.0 Universal** |

License files at repo root: `LICENSE` (Apache 2.0), `LICENSE-DATA` (CC-BY-4.0), `LICENSE-PROMPTS` (CC0), `LICENSE-OPENBUNDLE` (CC0). For the full file-by-file mapping and the rationale behind each license choice, see [`docs/LICENSE_COVERAGE.md`](docs/LICENSE_COVERAGE.md) and [`ARCHITECTURE.md`](ARCHITECTURE.md) §6.6.

## Quick links

- **Dashboard:** [cogstructurelab.com](https://cogstructurelab.com)
- **Methodology page:** [cogstructurelab.com/methodology](https://cogstructurelab.com/methodology) — full methodology page is in preparation; for the binding framing language (corpus lens, what LSB measures, what it does not), see [`ARCHITECTURE.md`](ARCHITECTURE.md) §1.5
- **Open data bundle:** [HuggingFace](https://huggingface.co/datasets/AILLM1999/lsb) and DOI-minted on [Zenodo](https://zenodo.org/) (see Citation below)
- **Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)
- **Data dictionary:** [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md)
- **Design system:** [`DESIGN_SYSTEM.md`](DESIGN_SYSTEM.md)
- **Team constitution:** [`CLAUDE.md`](CLAUDE.md)

## Repository structure

```
.
├── ARCHITECTURE.md          # System architecture, binding for all work
├── DESIGN_SYSTEM.md         # Frontend design system, binding for all UI work
├── CLAUDE.md                # Team constitution for the Claude Code agent pipeline
├── docs/
│   └── DATA_DICTIONARY.md            # Field-by-field schema doc for the open data bundle
├── packages/                # Python packages (cdb_core, cdb_collect, cdb_analyze, cdb_publish, cdb_social)
├── apps/dashboard/          # React + Vite + TypeScript frontend
├── data/                    # Raw, processed, results, grounding, open bundle
└── scripts/                 # CLI entry points (collect, analyze, publish, qa_check, build_db)
```

## Getting started

LSB is built with [uv](https://docs.astral.sh/uv/) for Python and Vite for the dashboard. From a fresh clone:

```bash
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
```

After `npm run dev` the dashboard runs at `http://localhost:5173` and renders exactly what the public dashboard renders. Every figure on [cogstructurelab.com](https://cogstructurelab.com) is reproducible from `data/raw/informants.jsonl` plus the scripts above.

For the field-by-field schema of `informants.jsonl`, see [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md). For the analysis methods, see the methodology page on the dashboard.

## Methodology ancestry

LSB applies Cultural Domain Analysis, a methodology developed by cognitive anthropologists from the 1960s onward to study how human informants organize cultural vocabulary. LSB stands on the shoulders of:

- **A. Kimball Romney, Susan C. Weller, and William H. Batchelder (1986).** "Culture as Consensus: A Theory of Culture and Informant Accuracy." *American Anthropologist* 88(2): 313–338. The foundational cultural consensus paper. Free access via JSTOR or via Romney's archive at UC Irvine.
- **Roy G. D'Andrade (1995).** *The Development of Cognitive Anthropology.* Cambridge University Press. The standard reference for the cognitive-anthropology tradition LSB inherits.
- **Susan C. Weller and A. Kimball Romney (1988).** *Systematic Data Collection.* Qualitative Research Methods Series, Vol. 10. SAGE Publications. The methodological handbook for free-list, pile-sort, and triad protocols.
- **Stephen P. Borgatti (1996).** *ANTHROPAC 4.0 Methods Guide.* Analytic Technologies. The operational guide that made pile-sort + consensus analysis practical for a generation of fieldworkers. Openly archived at [analytictech.com](https://www.analytictech.com/).
- **William H. Batchelder and A. Kimball Romney (1988).** "Test Theory Without an Answer Key." *Psychometrika* 53(1): 71–92. The statistical foundation for the consensus model LSB uses to evaluate cross-model categorical agreement.

LSB applies these methods to models, not to the humans they were designed for. The methodology page on the dashboard documents the adaptation table — what carries over directly, what required modification, and where the "as-if-informant" framing is load-bearing.

## Citation

If you use LSB in research, please cite:

```
Cognitive Structure Lab. (2026). The Latent Structure Benchmark (LSB), v1.0.
https://cogstructurelab.com (Zenodo DOI: 10.5281/zenodo.<TBD-T8>)
```

The Zenodo DOI resolves to the v1.0 open data bundle and is the canonical citation target. The dashboard URL is the canonical reading target.

## Status

LSB v1 is published. The dashboard at [cogstructurelab.com](https://cogstructurelab.com) covers three domains (family, holidays, food). The open data bundle is available on [HuggingFace](https://huggingface.co/datasets/AILLM1999/lsb) and is DOI-minted on [Zenodo](https://zenodo.org/) (DOI badge above).

The schema (`packages/cdb_core/schemas.py`) and the open data bundle format are version-stable; breaking changes become version bumps with migration notes in `docs/DATA_DICTIONARY.md`. Future collection campaigns add models, domains, and longitudinal snapshots; the v1 corpus is permanent.

For the phase plan see [`ARCHITECTURE.md`](ARCHITECTURE.md) §5.3.

## Contact

- **General questions:** open a Discussion on this repo
- **Bug reports:** open an Issue
- **Security disclosures:** `security@cogstructurelab.com` (see [`SECURITY.md`](SECURITY.md))
- **Press / media:** same address; we'll route appropriately
