---
license: cc0-1.0
pretty_name: Latent Structure Benchmark (LSB) Open Data Bundle v1
language:
  - en
size_categories:
  - 1K<n<10K
task_categories:
  - other
tags:
  - llm-benchmark
  - cultural-domain-analysis
  - cda
  - large-language-models
  - free-list
  - pile-sort
  - multidimensional-scaling
  - open-data
  - reproducible-research
  - corpus-analysis
  - cognitive-anthropology
  - informant-elicitation
---

# Latent Structure Benchmark (LSB) Open Data Bundle v1

## What this dataset is

The Latent Structure Benchmark (LSB) applies Cultural Domain Analysis (CDA) elicitation protocols — free listing, pile sorting, pile interview — to large language models as if they were informants. The originating question is exploratory: *what happens if you give a large language model a CDA free-list and pile-sort? What comes out?* LSB answers that reproducibly across models and time, then releases the data for the community to interpret. We ran the protocol; here is what came out; draw your own conclusions.

**LSB is not a capability benchmark, a leaderboard, or a model-quality ranking.** It does not score models or rank them against one another. It is a reproducible elicitation protocol whose outputs are released for community interpretation. The outputs are bundle objects — informant records, failure logs, decline interviews — not scores. There is no "winner." The mismatch between models is the finding, not a verdict.

LSB measures the corpus lens: the latent categorical structure of a training corpus, refracted through training and alignment, surfaced by structured elicitation. Every domain in v1 is model-to-model. There are no human baselines. Romney (1996), D'Andrade, Weller, Borgatti, and Batchelder are methodological forebears; their data is not in this bundle. For fuller citation and protocol details, see the methodology page at [cogstructurelab.com](https://cogstructurelab.com).

## Dataset statistics

This bundle contains 1,291 informant records produced by 17 models across 3 domains (family, food, holidays). 36 sessions were preserved as failures and 27 as decline interviews.

## Files in the tarball

| File | Description |
|---|---|
| `informants.jsonl` | Canonical raw data. One `InformantRecord` per line. See `DATA_DICTIONARY.md` §1. |
| `failures.jsonl` | Sessions the pipeline could not complete. Verbatim outputs preserved. |
| `decline_interviews.jsonl` | Follow-up elicitations for declined or failed sessions. |
| `lsb.sqlite` | SQLite database built from the JSONL files above. Same data, query-friendly. |
| `build_db.py` | Build script. Reconstruct `lsb.sqlite` from JSONL. Python 3.11+, no external dependencies. |
| `DATA_DICTIONARY.md` | Field-by-field schema docs for every file in this bundle. |
| `prompts/v1/` | Verbatim prompt templates (free_list, pile_sort, pile_interview). CC0. |
| `domains/v1/` | Domain YAML files (family, holidays, food). CC0. |
| `MANIFEST.txt` | SHA256 digest, byte size, and path for every file in this bundle. |
| `LICENSE-OPENBUNDLE` | CC0 1.0 Universal legal text. Governs all data files in this bundle. |

## How to use

The tarball is hosted on Backblaze B2 (URL becomes reachable at the M11 public flip; the bucket is private until then):

```bash
wget https://f005.backblazeb2.com/file/lsb-open-data/lsb_open_bundle_v1.tar.gz
tar xzf lsb_open_bundle_v1.tar.gz
```

Verify integrity before use (SHA256):

```
7064b325a25f90d2555138e7d944b129e78cbc7e18eace663b058166a6cd5983  lsb_open_bundle_v1.tar.gz
```

Optionally rebuild the SQLite database from the canonical JSONL:

```bash
python build_db.py informants.jsonl lsb.sqlite
```

Python 3.11+, no external dependencies. See `DATA_DICTIONARY.md` §6 for the full walkthrough and byte-equivalence verification steps.

## License

The bundle artifact this card describes — `informants.jsonl`, `lsb.sqlite`, `build_db.py`, `DATA_DICTIONARY.md`, prompt templates, domain definitions, and `MANIFEST.txt` — is released under **CC0 1.0 Universal** (public domain dedication). You may use, copy, modify, and redistribute for any purpose without restriction. The in-repo working data (`data/raw/`, `data/processed/`) carries CC-BY-4.0 per the project's split licensing policy (`ARCHITECTURE.md §6.6`) and is a separate distribution.

## Citation

```
Dawson, M. (2026). Latent Structure Benchmark (LSB) Open Data Bundle v1.
Zenodo. https://doi.org/10.5281/zenodo.20293554
```

The Zenodo record at https://zenodo.org/records/20293554 archives this release.

Dashboard and methodology: [cogstructurelab.com](https://cogstructurelab.com)

## Links

- Methodology and framing: [cogstructurelab.com](https://cogstructurelab.com)
- Scientific framing (§1.5, binding on all generated text): [`ARCHITECTURE.md §1.5`](https://github.com/Mark1999/latent-structure-benchmark/blob/master/ARCHITECTURE.md#15-what-lsb-measures-and-does-not-measure) (link becomes resolvable at M11 public flip)
- GitHub repository: [github.com/Mark1999/latent-structure-benchmark](https://github.com/Mark1999/latent-structure-benchmark) (private until M11 public flip)
