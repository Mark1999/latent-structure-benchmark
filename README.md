# Latent Structure Benchmark (LSB)

**Cognitive Structure Lab — [cogstructurelab.com](https://cogstructurelab.com)**

LSB is a benchmark for the **corpus lens** of large language models — the shape a model imposes on a domain, inherited from its training data. We apply Cultural Domain Analysis (CDA), a methodology developed by cognitive anthropologists in the 1970s and 80s to study how human informants organize cultural vocabulary, and we apply it to LLMs as if the models were informants. The result is a comparative map of how different models — Claude, GPT, DeepSeek, Llama, Mistral, Qwen, and others — organize the same set of everyday domain words (family terms, holidays, food, color, emotion). Where published or contributed human CDA data is available, we put a human reference point on the same map.

The **dashboard** is the primary deliverable: an interactive comparative explorer at [cogstructurelab.com](https://cogstructurelab.com), with downloadable images, citations, and the underlying numbers behind every figure. The benchmark, the open data, and the social pipeline all exist to make the dashboard credible, useful, and discoverable.

## What LSB is and isn't

LSB **is** a benchmark for the categorical structure of model training corpora, surfaced through CDA elicitation protocols.

LSB **is not** a measure of cultural worldview, belief, or cognition. Models do not have lived experience; they synthesize statistical patterns from text corpora. LSB is careful about this distinction in every visualization, every social post, and every line of dashboard copy. The methodology page on the dashboard goes into depth on what we measure, what we don't, and why the distinction matters.

For the full scientific framing, see [`ARCHITECTURE.md`](ARCHITECTURE.md) §1.5.

## Repository structure

```
.
├── ARCHITECTURE.md          # System architecture, binding for all work
├── DESIGN_SYSTEM.md         # Frontend design system, binding for all UI work
├── CLAUDE.md                # Team constitution for the Claude Code agent pipeline
├── docs/
│   ├── DATA_DICTIONARY.md            # Field-by-field schema doc for the open data bundle
│   └── grounding_submission_template.md  # Researcher submission walkthrough
├── packages/                # Python packages (cdb_core, cdb_collect, cdb_analyze, cdb_publish, cdb_social)
├── apps/dashboard/          # React + Vite + TypeScript frontend
├── data/                    # Raw, processed, results, grounding, open bundle
└── scripts/                 # CLI entry points (collect, analyze, publish, qa_check, build_db, cost_report)
```

## Quick links

- **Dashboard:** [cogstructurelab.com](https://cogstructurelab.com)
- **Methodology page:** [cogstructurelab.com/methodology](https://cogstructurelab.com/methodology)
- **Open data bundle** *(post Phase 4 validation)*: published on Backblaze B2 and DOI-minted via Zenodo
- **Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)
- **Design system:** [`DESIGN_SYSTEM.md`](DESIGN_SYSTEM.md)
- **Team constitution:** [`CLAUDE.md`](CLAUDE.md)
- **Researcher contributions:** [`docs/grounding_submission_template.md`](docs/grounding_submission_template.md)

## Licenses

LSB uses a split licensing model. The license depends on the type of content, not the directory.

| Content type | License | Files / paths |
|---|---|---|
| Source code | **Apache 2.0** | All `.py`, `.ts`, `.tsx`, `.js`, `.yml`, `.toml` files; `scripts/`; `packages/`; `apps/dashboard/src/`; CI configs |
| Prompts and domain definitions | **CC0 1.0 Universal** | `packages/cdb_collect/prompts/`; `data/domains/` |
| Raw responses, processed results, grounding data | **CC-BY-4.0** | `data/raw/`; `data/processed/`; `data/results/`; `data/grounding/` |
| **Open data bundle** | **CC0 1.0 Universal** | `data/open_bundle/` and the Backblaze B2 / Zenodo distribution |
| Documentation | **CC-BY-4.0** | `docs/`; `README.md`; `ARCHITECTURE.md`; `DESIGN_SYSTEM.md`; methodology page |

License files at the repo root: `LICENSE` (Apache 2.0), `LICENSE-DATA` (CC-BY-4.0), `LICENSE-PROMPTS` (CC0), `LICENSE-OPENBUNDLE` (CC0).

The Romney et al. (1996) family-terms grounding data carries an additional scholarly attribution requirement documented in `data/grounding/family/romney_1996/source.md`. CC-BY-4.0 already requires attribution; we're being explicit about the citation form.

For the full licensing rationale see [`ARCHITECTURE.md`](ARCHITECTURE.md) §6.6 and §6.7.

## Contributing human CDA data

**LSB exists in part to connect to the broader CDA research community.** If you have collected pile sort or free list data from human subjects for any domain LSB measures — *or any domain LSB doesn't measure yet* — you can contribute it for display on the dashboard alongside the model results.

The contribution path is a GitHub Pull Request:

1. Read [`docs/grounding_submission_template.md`](docs/grounding_submission_template.md) for the file format and data requirements.
2. Fork this repo, add your files at `data/grounding/{domain}/{your_baseline_id}/`, and open a PR. The PR template walks through everything LSB needs to merge your submission.
3. CI validates the format. The CDA SME agent reviews the methodology. Mark merges. Your data appears on the dashboard with full attribution; you retain all rights.

You don't need to be a developer to contribute. If GitHub is unfamiliar, find a collaborator who can drive the PR, or open a Discussion on this repo and we'll help.

The whole point of the project is to put AI corpus-lens findings next to actual human CDA findings. Your data is the human half of that comparison.

## Citation

A formal citation will be available with a Zenodo DOI after the LSB Phase 4 validation gates pass and the open data bundle is published. Until then, please cite the dashboard URL and the analysis version visible in the methodology page footer:

```
Cognitive Structure Lab. The Latent Structure Benchmark (LSB), analysis vX.Y.
https://cogstructurelab.com (accessed YYYY-MM-DD).
```

If you cite a specific finding that depends on a particular human grounding baseline, please *also* cite the original source of that baseline. The dashboard's grounding detail panel shows the citation inline, and the methodology page lists every baseline with its full reference.

## Status

LSB is in active development. Phase 1 (collection) is the current focus. The dashboard is not yet public; the open data bundle is not yet released. Expect breaking changes to the schema, the directory layout, and the API surface until Phase 4 validation passes. After Phase 4, the dashboard launches and the schema stabilizes — breaking changes to the open data bundle become version bumps with migration notes.

For the phase plan see [`ARCHITECTURE.md`](ARCHITECTURE.md) §5.3.

## Contact

- **General questions:** open a Discussion on this repo
- **Bug reports:** open an Issue
- **Security disclosures:** `security@cogstructurelab.ai` (see [`SECURITY.md`](SECURITY.md))
- **Press / media:** same address; we'll route appropriately
