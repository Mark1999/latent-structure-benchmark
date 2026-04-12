# Grounding Submission Template

**Document name:** `docs/grounding_submission_template.md`  
**Version:** v0.1  
**Status:** Phase 6 deliverable per `ARCHITECTURE.md` §4.2.5  
**Audience:** External researchers contributing human CDA data to LSB  
**Companion docs:** `ARCHITECTURE.md` §4.2.5 (workflow), `DESIGN_SYSTEM.md` §4 (how your data appears), `docs/DATA_DICTIONARY.md` (`GroundingRef` schema), `.github/PULL_REQUEST_TEMPLATE/grounding_submission.md` (the PR template you'll fill out)

---

## Why this exists

The Latent Structure Benchmark (LSB) studies how large language models organize cultural domain vocabulary, and one of LSB's central comparisons is **model corpus lens vs human consensus**. Where published or contributed human CDA data is available, we put a human reference point on the same map as the models. Many LSB domains will never have published human data, and ungrounded domains are a normal first-class state — but where human data exists or can be collected, it strengthens the project significantly.

**LSB welcomes researcher contributions of human CDA data**, including for domains LSB doesn't yet measure. Your data appears on the dashboard with full attribution. You retain all rights. LSB redistributes under CC-BY-4.0 with attribution, in the open data bundle (`ARCHITECTURE.md` §6.7).

This document walks you through what you'll need to prepare and how to submit it.

---

## What you'll need

A typical submission contains five files in a single new directory under `data/grounding/{domain}/{your_baseline_id}/`:

| File | Required? | Purpose |
|---|---|---|
| `source.md` | Required | Citation, population description, method, IRB status, year — the human-readable summary |
| `items.txt` | Required | The canonical item set you ran the CDA on, one item per line |
| `cooccurrence.csv` | Required | Symmetric similarity or co-occurrence matrix, header row matches `items.txt` |
| `grounding_ref.json` | Required | The `GroundingRef` schema object as JSON — the machine-readable summary |
| `pile_sort_raw.csv` | Optional but encouraged | Per-subject pile assignments. If included, LSB can compute a bootstrap uncertainty ellipse for your baseline on the MDS plot. |

If you have only an aggregate matrix (typical of historical published baselines), submit just the four required files. If you have raw subject-level data (typical of contemporary research), include the optional `pile_sort_raw.csv` — it makes your baseline meaningfully more useful on the dashboard because the bootstrap ellipse communicates how confident the position is.

---

## Choosing a `baseline_id`

Your baseline ID is the directory name and the URL slug. Pick something:

- **Stable** — won't need to change later. No version numbers in the slug unless they're load-bearing.
- **Identifiable** — combines your last name (or first author's), the year of data collection, and one or two distinguishing words about the population or method.
- **ASCII, lowercase, underscores** — no spaces, no slashes, no quotes, no Unicode. Becomes a directory name and a URL.
- **Unique within the target domain** — check `data/grounding/{domain}/` before opening your PR.

Good examples:
- `romney_1996` (canonical published baseline for family terms)
- `tanaka_2026_kyoto_kinship` (hypothetical: Japanese university kinship study from 2026)
- `nakamura_2025_okinawan_food` (hypothetical: Okinawan food terms from 2025)

Bad examples:
- `data` (not identifiable)
- `family-baseline-v2.1` (version number, hyphens, not unique enough)
- `Romney 1996` (spaces, not lowercase)
- `my_pile_sort` (not identifiable)

If you're unsure, propose one in the PR and we'll suggest a better one if needed.

---

## File-by-file requirements

### `source.md`

A human-readable summary of your dataset. Markdown. Used by the dashboard's grounding detail panel and by the methodology page. Required sections:

```markdown
# {Citation form, e.g. "Tanaka et al. (2026), Kyoto Kinship Study"}

**Target domain:** family

**Source URL:** https://doi.org/... or https://your-project-page.example/

**Population:** {one paragraph — who, when, how many, where}

**Method:** {pile sort, free list + pile sort, pairwise similarity, etc.}

**Collection year:** {YYYY — the year the data was collected, NOT publication year}

**IRB / ethics review:** {approved / exempt / not_applicable / unknown — see PR template for definitions}

**Number of human informants:** {n=...}

**Item set:** see `items.txt` ({N} items)

**Submitter:** {Your name, institution, contact}

## Brief methodology summary

{2–4 paragraphs in plain English. A non-anthropologist visiting the dashboard
should be able to understand what you collected and how, without reading the
original paper. Focus on what's distinctive about this population, why the
data is informative, and what the comparison to LLMs might reveal.}

## Citation

{Full bibliographic citation in your preferred format. APA, MLA, Chicago,
or BibTeX are all fine. Include a DOI or stable URL where possible.}

## Notes

{Anything else LSB readers should know — caveats, confounds, intended
follow-up studies, related datasets, etc.}
```

The CDA SME agent reads this file as part of the review. It's also the source the methodology page draws from when citing your baseline, so write it for an audience that includes both anthropologists and curious non-experts.

### `items.txt`

The canonical item set your CDA was conducted on. One item per line. UTF-8. No header. No blank lines. No trailing whitespace.

```
mother
father
sister
brother
daughter
son
grandmother
grandfather
aunt
uncle
cousin
niece
nephew
```

The order does not matter for the matrix, but it must match the header row of `cooccurrence.csv` exactly. The validator will fail your PR if the two are inconsistent.

### `cooccurrence.csv`

A symmetric similarity or co-occurrence matrix. Header row contains the item names; each subsequent row starts with the same item name and contains numeric values.

```csv
,mother,father,sister,brother,...
mother,1.0,0.85,0.71,0.69,...
father,0.85,1.0,0.68,0.72,...
sister,0.71,0.68,1.0,0.91,...
brother,0.69,0.72,0.91,1.0,...
...
```

**Format requirements** (CI will check all of these):

- UTF-8 encoded
- Header row matches `items.txt` exactly (same items, same order)
- Square matrix (same number of rows as columns, minus the header row and label column)
- Symmetric: `matrix[i][j]` equals `matrix[j][i]` for all `i, j`
- Diagonal is `1.0` (an item is maximally similar to itself)
- Off-diagonal values in `[0.0, 1.0]` for similarity matrices, or non-negative for raw co-occurrence counts (LSB will normalize)
- No missing values, no `NaN`, no empty cells

If your published source provides a similarity matrix on a different scale (e.g. `[-1, 1]` correlations, or raw counts), normalize to `[0, 1]` before submission and document the normalization in `source.md`.

### `pile_sort_raw.csv` *(optional but encouraged)*

Per-subject pile assignments. Subject IDs must be **pseudonymized** — no names, no email addresses, no demographic identifiers beyond what you explicitly intend to publish (and even those go in `source.md`, not in this file).

Two acceptable formats:

**Long format** (one row per subject-item pair):

```csv
subject_id,item,pile_id
S001,mother,1
S001,father,1
S001,sister,2
S001,brother,2
S002,mother,1
S002,father,2
...
```

**Wide format** (one row per subject):

```csv
subject_id,mother,father,sister,brother,...
S001,1,1,2,2,...
S002,1,2,2,3,...
...
```

Either format is fine; CI will detect which one you used. Pile IDs are arbitrary integers — they only need to be consistent within a subject. Subject IDs are arbitrary strings but should be pseudonymized.

When this file is present, the LSB analysis pipeline computes a bootstrap uncertainty ellipse for your baseline by resampling subjects with replacement (B=500). The ellipse appears on the MDS plot around your baseline marker. When this file is absent, the marker is rendered without an ellipse and labeled "uncertainty unavailable" in the dashboard's grounding detail panel.

### `grounding_ref.json`

The machine-readable form of your submission. Must validate against the `GroundingRef` schema in `cdb_core/schemas.py` (full field spec in `docs/DATA_DICTIONARY.md`). Required fields and example:

```json
{
  "baseline_id": "tanaka_2026_kyoto_kinship",
  "baseline_kind": "researcher",
  "domain_slug": "family",

  "source_citation": "Tanaka, K., Yamada, S., & Suzuki, H. (2026). Cognitive structure of Japanese kin terms among Kyoto university students. Journal of Cognitive Anthropology, 12(3), 145–168.",
  "source_url": "https://doi.org/10.example/12345",
  "collected_year": 2025,

  "n_human_informants": 87,
  "population_description": "Japanese university students at Kyoto University, ages 19–23, balanced gender, native Japanese speakers, recruited Spring 2025. n=87 after excluding 4 subjects with incomplete pile sorts.",

  "method": "pile sort (Romney protocol), single sort per subject",
  "irb_status": "approved",

  "submitter_name": "Keiko Tanaka",
  "submitter_institution": "Kyoto University, Department of Cognitive Science",
  "submitter_contact": "tanaka@example.kyoto-u.ac.jp",
  "submission_date": "2026-04-12",

  "mds_coordinate": [0.34, -0.21],
  "mds_uncertainty": null,
  "distance_to_nearest_model": 0.18,
  "nearest_model_id": "claude-opus-4-6",

  "item_intersection_size": 11,
  "item_intersection_total": 13
}
```

**Notes on the fields:**

- `baseline_kind` is `"researcher"` for any submission via this template. `"published"` is reserved for baselines extracted by Mark from the academic literature.
- `mds_coordinate`, `mds_uncertainty`, `distance_to_nearest_model`, `nearest_model_id`, `item_intersection_size`, and `item_intersection_total` are computed by the LSB analysis pipeline at merge time. **Leave these as placeholders** (`[0.0, 0.0]`, `null`, `0.0`, `""`, `0`, `0`) — the pipeline will populate them. The CI validator will not reject placeholder values for these fields.
- `submission_date` is the date you opened the PR; LSB updates it to the merge date if they differ.
- `irb_status` must be one of: `"approved"`, `"exempt"`, `"not_applicable"`, `"unknown"`. See the PR template for definitions and when each is appropriate.

---

## Submission process

1. **Read the PR template** at `.github/PULL_REQUEST_TEMPLATE/grounding_submission.md` so you know what you'll be asked.
2. **Fork** the LSB repo on GitHub.
3. **Create a branch** named `grounding/{your_baseline_id}` (e.g. `grounding/tanaka_2026_kyoto_kinship`).
4. **Add your files** at `data/grounding/{domain}/{your_baseline_id}/`. The directory must not already exist.
5. **Open a Pull Request** against `main`. The PR template loads automatically; fill out every section.
6. **Wait for CI** (a few minutes). CI runs schema validation, format checks, an item-intersection coverage report, a `gitleaks` PII scan, and a check that no API keys or secrets have leaked into any submitted file. Address any failures and push fixes to your branch.
7. **Wait for CDA SME review** (same day to next business day). The CDA SME agent reviews the methodological soundness on four axes (protocol, claims, audience translation, consistency) and posts a verdict (PASS / PASS-WITH-NOTES / FAIL) as a PR comment. Address any notes and push fixes if needed.
8. **Wait for Mark's review and merge** (1–2 weeks depending on calendar). Mark reads the CDA SME verdict, asks any clarifying questions on the PR, and merges if PASS or PASS-WITH-NOTES with corrections applied.
9. **Dashboard publication.** The merge triggers an analysis re-run. Your baseline appears on the next dashboard publish, with full attribution in the grounding detail panel and on the methodology page. Inclusion in the open data bundle follows on the next release.

If at any point you get stuck, open a Discussion on the LSB repo or email `security@cogstructurelab.ai` (which doubles as the general project contact).

---

## What happens to your data after merge

- **Dashboard.** Your baseline appears as a marker on the MDS plot for the target domain (gray diamond ◆ for researcher submissions, per `DESIGN_SYSTEM.md` §3.3). Clicking the marker opens the grounding detail panel showing your full attribution, population, method, IRB status, and a download link for the data.
- **Methodology page.** Your baseline is listed in §5 (Human grounding) with full citation. The methodology page is the canonical scholarly reference for LSB; if your data ends up cited, the page is where readers will find it.
- **Open data bundle.** Your data is included in the next release of the LSB open data bundle on Backblaze B2 and Zenodo (`ARCHITECTURE.md` §6.7), under CC-BY-4.0 with full attribution. Each release gets a separate Zenodo DOI; old releases are not retracted, so once your data is included it has a permanent citable form.
- **Re-analysis.** Anyone who downloads the open data bundle can run LSB's analysis pipeline against your data. This is a feature, not a bug — reproducibility is the project's highest priority.

---

## Withdrawal

If circumstances change and you need to withdraw your data, open an issue on the LSB repo with the title `Withdrawal: {baseline_id}` and a one-line reason. LSB will remove the data from the next published bundle, the dashboard, and the in-repo `data/grounding/` directory within one release cycle.

**Limitation:** earlier releases of the open data bundle on Zenodo retain the data, because Zenodo's permanent-versioning policy does not allow unilateral retraction. This is a Zenodo policy, not an LSB choice. If you need a Zenodo retraction, LSB will provide the retraction instructions and support your request to Zenodo, but the final decision rests with Zenodo.

---

## FAQ

**Q: Do I have to use a pile sort? My data is a free list / triadic comparison / pairwise similarity matrix.**

A: Pile sort is the most common CDA protocol and the one LSB itself uses, so the pipeline is best-tested for it. But any CDA protocol that produces an item × item similarity or co-occurrence matrix can be submitted. Document the protocol in `source.md` and `grounding_ref.json` so the CDA SME agent and downstream users know what they're looking at.

**Q: What if my domain isn't on the LSB v1 slate?**

A: Submit anyway. The PR adds a directory under `data/grounding/{your_domain}/` even if LSB doesn't yet measure the domain on the model side. Mark and the Architect agent then decide whether to add the domain to the v1 slate or queue it for v2. Either way, your data is acknowledged.

**Q: Can I submit aggregate-only data (no per-subject pile assignments)?**

A: Yes. Many published baselines are aggregate-only. Your baseline will appear on the dashboard without an uncertainty ellipse and with a "uncertainty unavailable" note in the detail panel. Per-subject data is encouraged but not required.

**Q: How do I cite LSB if I use the open data bundle in my own research?**

A: A formal citation with a Zenodo DOI is available after Phase 4 validation; until then, cite the dashboard URL and the analysis version. See [`README.md`](../README.md) for the current citation form.

**Q: I'm not a developer. Can someone help me through the GitHub PR process?**

A: Yes. Open a Discussion on the LSB repo describing your data, and we'll help you through the PR. Or find a collaborator who's comfortable with GitHub. The contribution mechanism is GitHub-only for v1 because the PR is the audit trail; an in-app submission form is on the v2 roadmap.

**Q: What if my IRB status doesn't fit any of the four options?**

A: Describe the actual situation in the PR comments and pick the closest option. Mark will follow up if anything is unclear. Don't pick `unknown` unless the data genuinely predates current ethics frameworks and the original protocol is unrecoverable.

**Q: Can I submit data on behalf of a colleague who collected it?**

A: Yes, with their permission. Both names should appear in `source.md` and `grounding_ref.json.submitter_name`, and the contact field should reach someone who can answer methodological questions.

**Q: How long does the review usually take?**

A: CI is a few minutes. CDA SME review is same-day to next business day in most cases. Mark's review and merge is 1–2 weeks depending on his calendar. The whole process usually takes 1–2 weeks end to end. If it stalls for more than three weeks, ping the PR.

---

*Thank you for considering a contribution. The whole point of LSB is to put AI corpus-lens findings next to actual human CDA findings. Your data is the human half of that comparison, and the project is meaningfully better with it than without.*
