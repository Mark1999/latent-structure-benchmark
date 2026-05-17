# Latent Structure Benchmark (LSB)

**Cognitive Structure Lab — [cogstructurelab.com](https://cogstructurelab.com)**

LSB measures what frontier LLMs produce when asked to categorize, in a way that's reproducible, comparable across models, and trackable across time. It applies Cultural Domain Analysis (CDA) — a methodology developed by cognitive anthropologists in the 1970s and 80s to study how human informants organize cultural vocabulary — to LLMs as if the models were informants. The result is a comparative map of how different models (Claude, GPT, DeepSeek, Llama, Mistral, Qwen, and others) organize the same set of everyday domain words (family terms, holidays, food, color, emotion). Every domain on the dashboard is, permanently, model-to-model.

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
│   └── DATA_DICTIONARY.md            # Field-by-field schema doc for the open data bundle
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

The `data/grounding/family/romney_1996/` directory contains historical reference data extracted before the 2026-05-07 amendment that removed human baselines from v1 (see `docs/status/2026-05-07-lsb-philosophy-and-framing.md`). Per the existing `data/grounding/family/romney_1996/source.md`, the Romney et al. (1996) attribution requirement applies to anyone reusing that file.

For the full licensing rationale see [`ARCHITECTURE.md`](ARCHITECTURE.md) §6.6 and §6.7. For the canonical path-by-path license mapping see [`docs/LICENSE_COVERAGE.md`](docs/LICENSE_COVERAGE.md).

## Citation

A formal citation will be available with a Zenodo DOI after the LSB Phase 4 validation gates pass and the open data bundle is published. Until then, please cite the dashboard URL and the analysis version visible in the methodology page footer:

```
Cognitive Structure Lab. The Latent Structure Benchmark (LSB), analysis vX.Y.
https://cogstructurelab.com (accessed YYYY-MM-DD).
```

## Status

LSB is in active development. Phase 1 (collection) is the current focus. The dashboard is not yet public; the open data bundle is not yet released. Expect breaking changes to the schema, the directory layout, and the API surface until Phase 4 validation passes. After Phase 4, the dashboard launches and the schema stabilizes — breaking changes to the open data bundle become version bumps with migration notes.

For the phase plan see [`ARCHITECTURE.md`](ARCHITECTURE.md) §5.3.

## Contact

- **General questions:** open a Discussion on this repo
- **Bug reports:** open an Issue
- **Security disclosures:** `security@cogstructurelab.ai` (see [`SECURITY.md`](SECURITY.md))
- **Press / media:** same address; we'll route appropriately
