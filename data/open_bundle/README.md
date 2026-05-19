# LSB Open Data Bundle v1

**License:** CC0 1.0 Universal (public domain dedication). You may use, copy,
modify, and redistribute this bundle for any purpose without restriction.
Attribution via the Zenodo DOI is encouraged for citation but not legally required.

---

## What this bundle is

The Latent Structure Benchmark (LSB) applies Cultural Domain Analysis (CDA)
elicitation protocols — free listing, pile sorting, pile interview — to large
language models as if they were informants. The originating question is
exploratory: *what happens if you give a large language model a CDA free-list
and pile-sort? What comes out?* LSB answers that reproducibly across models
and time, then releases the data for the community to interpret. We ran the
protocol; here is what came out; draw your own conclusions.

The mismatch is the finding. Importing a methodology designed for cultural
informants into a system that encodes culture without experiencing it is the
research question, not a limitation. LSB measures the corpus lens: the latent
categorical structure of a training corpus, refracted through training and
alignment, surfaced by structured elicitation. Every domain in v1 is
model-to-model. There are no human baselines. Romney (1996), D'Andrade,
Weller, Borgatti, and Batchelder are methodological forebears; their data is
not in this bundle.

---

## Files

| File | Description |
|---|---|
| `informants.jsonl` | Canonical raw data. One `InformantRecord` per line. `DATA_DICTIONARY.md` §1. |
| `failures.jsonl` | Sessions the pipeline could not complete. Verbatim outputs preserved. §9. |
| `decline_interviews.jsonl` | Follow-up elicitations for declined or failed sessions. §10. |
| `lsb.sqlite` | SQLite database built from the JSONL files above. Same data, query-friendly. |
| `build_db.py` | Build script. Reconstruct `lsb.sqlite` from JSONL. See reproducibility below. |
| `DATA_DICTIONARY.md` | Field-by-field schema docs for every file in this bundle. |
| `prompts/v1/` | Verbatim prompt templates (free_list, pile_sort, pile_interview). CC0. |
| `domains/v1/` | Domain YAML files (family, holidays, food). CC0. |
| `MANIFEST.txt` | SHA256 digest, byte size, and path for every file in this bundle. |
| `LICENSE-OPENBUNDLE` | CC0 1.0 Universal legal text. Governs all data files in this bundle. |

---

## Reproducibility

```bash
python build_db.py informants.jsonl lsb.sqlite
```

Python 3.11+, no external dependencies. See `DATA_DICTIONARY.md` §6 for the
full walkthrough and byte-equivalence verification steps.

---

## Cite this bundle

```
Dawson, M. (2026). Latent Structure Benchmark (LSB) Open Data Bundle v1.
Zenodo. https://doi.org/<TBD-T8-DOI>
```

(DOI assignment pending Zenodo deposit; this README will be updated in a
follow-up release once the Zenodo record is published.)

Dashboard and methodology: [cogstructurelab.com](https://cogstructurelab.com)
