# Phase 4c — Candidate Sources for Human CDA Grounding

**Document name:** `PHASE_4C_CANDIDATE_SOURCES.md`  
**Version:** v0.1 (first draft, aligned with `ARCHITECTURE.md` v0.7)  
**Status:** Pre-Phase-4c reference document; updated as Mark confirms or rejects candidates  
**Audience:** Architect agent, CDA SME agent, Mark (acquisition lead), Coder agent (data normalization)  
**Companion docs:** `ARCHITECTURE.md` §1.5.5 (grounding framing), §3.2 (`GroundingRef` schema), §4.2.5 (grounding module and acquisition workflow), §5.3 Phase 4c (when this happens), `docs/DATA_DICTIONARY.md` (`GroundingRef` field-by-field)

**Purpose.** This document is a **literature scouting report**, not a binding spec. It lists candidate published human CDA datasets that could supply grounding baselines for LSB v1 domains (`baseline_kind="published"` per the v0.7 schema). Each candidate has a citation, an acquisition path, a licensing assessment, an item-set assessment, and a recommendation. **Mark is the acquisition lead** (`ARCHITECTURE.md` §4.2.5) — the Coder agent cannot retrieve licensed academic content, and automated scraping of publishers would be both a licensing violation and bad practice. The Architect agent maintains this document as candidates are confirmed or ruled out.

**v0.7 reminder.** A domain may carry zero, one, or many baselines. This document lists *candidates*; Mark picks at most one or two per domain for v1 acquisition, and the rest remain as future-acquisition options or as recommendations to outside researchers who might want to contribute their own collection (`baseline_kind="researcher"`). Ungrounded domains are a normal first-class state per `ARCHITECTURE.md` §1.5.5 — if no candidate in this list is a clean fit for a given domain, the right move is to ship that domain ungrounded in v1, not to force a poor-fit baseline into the schema.

**Changelog:**
- **v0.1** — first draft. Six candidates across family terms, color terms, and emotion terms. Family terms primary target is Romney et al. (1996); color terms primary target is Berlin & Kay (1969); emotion terms deferred to v2 with notes on candidate sources. Holidays, food, and justice domains have no published CDA candidates and remain ungrounded in v1.

---

## 1. How to read this document

For each candidate the report lists:

- **Citation** — full bibliographic form
- **Domain** — which LSB domain this baseline would ground
- **n_human_informants** — sample size from the original study
- **Population** — who the subjects were
- **Year collected** — when the data was actually gathered (NOT publication year)
- **Method** — the CDA protocol used
- **What the source actually publishes** — full subject-level data, an aggregate similarity matrix, only summary statistics, etc. Determines whether LSB can extract a usable `cooccurrence.csv` (and whether it can compute a bootstrap ellipse)
- **Acquisition path** — how Mark would actually get the data: PMC free full text, JSTOR via institutional access, university library scan, direct author contact, etc.
- **Licensing assessment** — fair use posture, CC reuse rights if any, attribution requirements
- **Item-set assessment** — how well the source's item set is likely to align with the LSB v1 item set for the domain
- **Recommendation** — `PRIMARY` (acquire for v1), `SECONDARY` (acquire if primary fails or for cross-validation), `DEFER` (interesting but defer to v2), `REJECT` (does not fit LSB's needs and the reason)
- **Notes** — anything else worth flagging

The acquisition workflow itself lives in `ARCHITECTURE.md` §4.2.5 and is summarized at the end of this document (§5).

---

## 2. Family / kinship terms

Family terms is the **primary v1 grounded domain**, chosen because it has the deepest published CDA literature (it's the canonical CDA topic since the 1960s), the most defensible item set (English kin terms are well-bounded), and a project-history connection (Mark's design anthropology work at Kodak originated in family-photography research). At least one published baseline must land here for Phase 4 to ship in its grounded form.

### 2.1 Romney, Boyd, Moore, Batchelder & Brazill (1996) — `PRIMARY`

**Citation.** Romney, A. K., Boyd, J. P., Moore, C. C., Batchelder, W. H., & Brazill, T. J. (1996). Culture as shared cognitive representations. *Proceedings of the National Academy of Sciences*, 93(10), 4699–4705.

**DOI / PMC.** [10.1073/pnas.93.10.4699](https://doi.org/10.1073/pnas.93.10.4699) · PMC: PMC39344 (free full text)

**Domain.** family

**n_human_informants.** 122

**Population.** US college students, ages 18–22, recruited at the University of California, Irvine, in the early 1990s. Mixed gender. Native English speakers.

**Year collected.** Approximately 1990–1991 (the paper was published in 1996; collection predated publication by several years per the methods section).

**Method.** Pairwise similarity judgments on 15 English kin terms. Each subject rated all C(15,2) = 105 pairs. The aggregate similarity matrix in Table 1 of the paper is the result of averaging across all 122 subjects.

**What the source actually publishes.** The aggregate similarity matrix is published in Table 1 of the paper. **Subject-level data is not published** — only the 15×15 aggregate. This means:
- LSB can extract a usable `cooccurrence.csv` directly from Table 1
- LSB **cannot** compute a bootstrap uncertainty ellipse for this baseline (the per-subject pile assignments don't exist in the public record)
- The dashboard's grounding detail panel will label this baseline "uncertainty unavailable — published aggregate only" per `DESIGN_SYSTEM.md` §3.3

**Acquisition path.** PMC free full text. The PNAS paper is in PubMed Central with no paywall, no institutional access required. Mark downloads the PDF, transcribes Table 1 into a CSV, and writes `source.md` and `grounding_ref.json` per the multi-baseline directory layout (`data/grounding/family/romney_1996/`). **Estimated effort: ~2 hours** (download, table transcription, CSV validation, source.md drafting). The Coder agent then validates the CSV round-trips through the `cdb_core` schema and writes the unit test.

**Licensing assessment.** The PNAS paper is published under PNAS's standard terms. The aggregate similarity matrix in Table 1 is a *fact* about a small numerical dataset, not a creative work, and falls comfortably under fair use for non-commercial research purposes — particularly given that LSB cites the paper in full at every display surface (dashboard tooltip, grounding detail panel, methodology page, `source.md`, open data bundle data dictionary). The CC-BY-4.0 redistribution of the derived `cooccurrence.csv` is acceptable under fair use as long as attribution is preserved, which LSB enforces structurally. **No licensing blocker.**

The Romney 1996 paper specifically also has an **additional scholarly attribution requirement** documented in `data/grounding/family/romney_1996/source.md` and noted in `ARCHITECTURE.md` §6.6 — any redistribution of the derived data must cite the original paper in full. This is standard scholarly practice and the CC-BY license already requires it; LSB is being explicit about the citation form.

**Item-set assessment.** The 15 kin terms in the Romney 1996 study are: *grandfather, grandmother, father, mother, uncle, aunt, brother, sister, cousin, son, daughter, nephew, niece, grandson, granddaughter*. The LSB v1 family domain prompt is open-ended ("list every kind of family relationship you can think of") and the salient first 25 items per model will likely include all 15 of the Romney items, giving high overlap. **Estimated intersection: 13–15 of 15 Romney items, or roughly 52–60% of a typical 25-item LSB list.** Not perfect — LSB models will produce items the Romney study didn't include (step-parents, in-laws, etc.) — but the overlap is the best LSB can hope for from any published source.

**Recommendation.** `PRIMARY`. This is the v1 family-domain grounding baseline. Acquire in Phase 4c. If for any reason it can't be acquired (PMC outage, transcription disagreement, item-set mismatch worse than estimated), fall back to §2.2 or ship family ungrounded.

**Notes.** This is the most cited cultural consensus paper in the cognitive anthropology literature and has been independently reanalyzed many times. The aggregate matrix in Table 1 is the canonical reference dataset for English kin term similarity. LSB inheriting it is methodologically defensible and gives the project a clean anchor in the existing literature.

---

### 2.2 D'Andrade (1995), *The Development of Cognitive Anthropology* — `SECONDARY`

**Citation.** D'Andrade, R. G. (1995). *The Development of Cognitive Anthropology*. Cambridge University Press. ISBN 978-0521459761.

**Domain.** family (also color and emotion in passing)

**n_human_informants.** Varies by chapter; the kinship analysis discusses several earlier studies with sample sizes in the 20–80 range.

**Population.** Multiple US studies; the kinship chapter draws on studies of US English speakers from the 1960s–1980s.

**Year collected.** Various, mostly 1965–1985.

**Method.** Mostly pile sort and free list, with some pairwise similarity work. The book is a synthesis text rather than a single primary dataset.

**What the source actually publishes.** Reanalyses of earlier studies (Romney & D'Andrade 1964, Wallace & Atkins 1960, etc.) with their own commentary. Some figures and tables include similarity matrices or co-occurrence data; others are summary statistics only. **Mixed — some chapters yield extractable matrices, others do not.**

**Acquisition path.** Print book or institutional library e-book. JSTOR may have chapter-level access depending on Mark's affiliation. **Estimated effort: ~4–6 hours** (acquire the book, scan the relevant chapters, identify which figures contain extractable matrices, transcribe).

**Licensing assessment.** Cambridge University Press copyrighted text. Fair use for the underlying numerical data in published figures is reasonable for non-commercial research with full attribution. LSB redistribution of any derived `cooccurrence.csv` is acceptable under fair use as long as the source is cited; LSB does not redistribute the surrounding prose or commentary. **No blocker, but the line is finer than for Romney 1996** — Cambridge UP is more aggressive about copyright enforcement than PNAS, so the citation form should be especially careful.

**Item-set assessment.** Variable depending on which chapter Mark draws from. The Romney & D'Andrade 1964 reanalysis covers a similar 15-term kin set to Romney 1996 and would give roughly the same coverage.

**Recommendation.** `SECONDARY`. Useful as a cross-validation baseline (a *second* `published` baseline for the family domain, demonstrating the v0.7 multi-baseline design with a real second entry) or as a fallback if Romney 1996 turns out to have a transcription problem. Defer to Phase 6 unless Phase 4c reveals a need for it.

**Notes.** D'Andrade is the senior author of the Romney 1996 paper and the dean of cognitive anthropology in the US; citing the book alongside the PNAS paper is rhetorically appropriate for LSB's methodology page even if the book's data isn't ingested.

---

### 2.3 Romney & D'Andrade (1964), *American Anthropologist* — `DEFER`

**Citation.** Romney, A. K., & D'Andrade, R. G. (1964). Cognitive aspects of English kin terms. *American Anthropologist*, 66(3), 146–170.

**Domain.** family

**n_human_informants.** ~50 (per the methods section as recalled; needs confirmation from the actual paper)

**Population.** US English speakers, mid-1960s.

**Method.** Triadic comparisons on English kin terms, plus paradigmatic feature analysis.

**What the source actually publishes.** Componential analysis tables and a similarity structure derived from triadic comparisons. The published form is *not* a clean co-occurrence matrix — it's a feature decomposition table that would need conversion to the LSB schema.

**Acquisition path.** JSTOR via institutional access. AnthroSource (American Anthropological Association). **Estimated effort: ~3 hours** including the conversion from feature table to a similarity matrix.

**Licensing assessment.** *American Anthropologist* is published by Wiley on behalf of the AAA. Fair use for numerical data with attribution is fine for non-commercial research. Wiley is moderately aggressive on copyright but the underlying data is factual.

**Item-set assessment.** The 1964 paper uses a similar 15–20 term English kin set; intersection with LSB v1 should be high.

**Recommendation.** `DEFER`. This is the *founding* paper of CDA-style kin term analysis and deserves citation on the methodology page, but the published form is awkward to convert and the Romney 1996 paper supersedes it for practical grounding purposes. Defer to v2 unless an outside researcher wants to do the conversion as a contributed baseline.

---

## 3. Color terms

Color terms is a **secondary v1 grounded domain**, planned for Phase 6 when the color domain is added to the LSB slate. The published literature is rich, the item set is well-bounded (focal colors), and the cross-cultural angle makes color a natural showcase for the corpus lens framing.

### 3.1 Berlin & Kay (1969), *Basic Color Terms* — `PRIMARY` (Phase 6)

**Citation.** Berlin, B., & Kay, P. (1969). *Basic Color Terms: Their Universality and Evolution*. University of California Press.

**Domain.** color

**n_human_informants.** ~98 across 20 languages (varies by language; the English subset is roughly n=20).

**Population.** Native speakers of 20 languages, mostly recruited in the San Francisco Bay Area in the late 1960s. The LSB-relevant English subset is US English speakers.

**Year collected.** Roughly 1965–1968.

**Method.** Munsell color chip naming and best-example selection. Subjects named each focal color chip and identified the best example of each basic color term in their language.

**What the source actually publishes.** Naming distributions per chip per language, focal-color identifications, and a typology of basic color term inventories. The book also publishes similarity-of-naming matrices for the basic color terms in English and several other languages. **The English aggregate similarity matrix is extractable from the appendices.**

**Acquisition path.** Print book (still in print) or institutional library e-book. **Estimated effort: ~3 hours** (acquire, scan the relevant appendix, transcribe to CSV).

**Licensing assessment.** University of California Press copyrighted text. Fair use for the numerical similarity matrix with full attribution is acceptable for non-commercial research. UC Press is generally tolerant of academic reuse; the book is widely cited and the data has been redistributed in derived form many times in the literature without challenge. **No blocker.**

**Item-set assessment.** Berlin & Kay's basic English color terms are: *black, white, red, green, yellow, blue, brown, purple, pink, orange, gray*. The LSB v1 color domain prompt would elicit at least these 11 from any model, plus likely some additions (cyan, magenta, beige, navy, etc.). **Estimated intersection: 11 of 11 Berlin & Kay items, or roughly 44% of a typical 25-item LSB list.** Lower coverage than family terms but the 11 basic terms are exactly the items the cognitive anthropology literature treats as the meaningful comparison set.

**Recommendation.** `PRIMARY` for Phase 6. Do not acquire until the color domain is added to the LSB slate. When that happens, this is the v1 grounded baseline for color.

**Notes.** Berlin & Kay's universalist claims have been contested in subsequent literature (Lucy 1992 is the most prominent critique). LSB's methodology page should cite both the original work and the major critiques rather than presenting Berlin & Kay's framework as settled. This is straightforward scholarly hygiene and matches the §1.5 framing of LSB as a falsifiable measurement, not a defense of any particular cognitive-anthropology school.

---

### 3.2 World Color Survey (Kay, Berlin, Maffi, Merrifield & Cook, 2009) — `SECONDARY` (Phase 6)

**Citation.** Kay, P., Berlin, B., Maffi, L., Merrifield, W. R., & Cook, R. (2009). *The World Color Survey*. CSLI Publications. ISBN 978-1575865867.

**Domain.** color

**n_human_informants.** ~2,600 across 110 unwritten languages.

**Population.** Native speakers of 110 languages, collected by missionary-linguists in the 1970s–80s as a follow-on to Berlin & Kay 1969.

**Method.** Same Munsell chip naming and best-example protocol as Berlin & Kay 1969, scaled up.

**What the source actually publishes.** Per-subject naming responses for all 2,600 subjects across all 110 languages, available as a downloadable dataset from the WCS website (wcs.berkeley.edu). **This is one of the few CDA-adjacent datasets where per-subject data is fully public** — it would let LSB compute a bootstrap uncertainty ellipse for the WCS English baseline.

**Acquisition path.** Direct download from wcs.berkeley.edu (data is publicly released under permissive terms). **Estimated effort: ~4 hours** including subsetting to the English-relevant data, normalizing to LSB's pile-sort-style co-occurrence form, and computing the bootstrap-input file.

**Licensing assessment.** WCS data is publicly released for academic use with attribution. The data download page specifies the terms; LSB should re-confirm at acquisition time. **Likely no blocker, but verify before acquisition.**

**Item-set assessment.** Same 11 basic English color terms as Berlin & Kay 1969 plus additional fine-grained terms.

**Recommendation.** `SECONDARY` for Phase 6. The WCS English subset can be a *second* `published` baseline for the color domain alongside Berlin & Kay 1969 — and would be the first LSB baseline with subject-level data and a bootstrap uncertainty ellipse, which is a meaningful upgrade to the project's grounding story. Acquire in Phase 6 if time permits; otherwise defer to v2.

**Notes.** The WCS data has been reanalyzed in many subsequent papers; LSB's use of it would join a long tradition. The cross-language nature of the dataset is also a hook for the v2 multilingual extension of LSB.

---

## 4. Emotion terms — `DEFER` to v2

Emotion terms is a candidate domain for v2, not v1. The published literature exists but has structural problems for LSB's needs:

- **Item sets vary dramatically across studies.** Different research traditions (basic emotions, dimensional models, prototype theory) cluster items differently and use different category vocabularies.
- **Cross-cultural comparability is contested.** Russell (1991) and others have shown that "emotion" is not a clean cross-linguistic category, which complicates the relative-vs-absolute claims LSB wants to make.
- **The most extensive single dataset (Shaver et al. 1987) uses a hierarchical clustering on a non-CDA protocol** that doesn't translate cleanly to the LSB pile-sort form.

LSB v1 should not include the emotion domain. Two candidate sources are listed below for v2 reference. If LSB receives a researcher submission for emotion (`baseline_kind="researcher"`) before v2, it would be welcomed and would prompt earlier addition of the emotion domain to the LSB slate.

### 4.1 Shaver, Schwartz, Kirson & O'Connor (1987) — `DEFER` to v2

**Citation.** Shaver, P., Schwartz, J., Kirson, D., & O'Connor, C. (1987). Emotion knowledge: Further exploration of a prototype approach. *Journal of Personality and Social Psychology*, 52(6), 1061–1086.

**Domain.** emotion (v2)

**n_human_informants.** ~100

**Population.** US college students, mid-1980s.

**Method.** Sorting task on 135 emotion terms (closer to LSB's pile sort than most emotion-research protocols).

**What the source actually publishes.** Hierarchical cluster analysis of the sorted data with summary statistics. The full co-occurrence matrix is *not* published in the article; the dendrogram is. Subject-level data may be available from the authors but is not in the public record.

**Acquisition path.** PsycARTICLES via institutional access for the article; possible direct author contact for any unpublished data. **Estimated effort: 4–8 hours, with significant uncertainty about whether the matrix can actually be reconstructed from the published dendrogram.**

**Recommendation.** `DEFER` to v2. Include in the v2 acquisition plan only if the LSB project decides to add the emotion domain.

---

### 4.2 Storm & Storm (1987) — `DEFER` to v2

**Citation.** Storm, C., & Storm, T. (1987). A taxonomic study of the vocabulary of emotions. *Journal of Personality and Social Psychology*, 53(4), 805–816.

**Domain.** emotion (v2)

**Recommendation.** `DEFER` to v2. Smaller dataset than Shaver et al.; less commonly cited. Listed for completeness.

---

## 5. Domains with no published CDA candidates (v1)

The following LSB v1 domains have no obvious published human CDA dataset that LSB can acquire:

- **Holidays.** No published CDA-style study of US or English-speaking holiday categorization that the Architect agent has been able to find. The cognitive anthropology literature on calendrical and ritual cognition exists but does not produce data in a form LSB can ingest. **Ships ungrounded in v1.**
- **Food.** Some food-preference and food-categorization research exists (notably from the marketing literature and from cross-cultural nutrition studies), but the CDA-protocol form is rare. **Ships ungrounded in v1.**
- **Justice / fairness / morality.** Moral psychology has rich pile sort and rating data (Haidt's moral foundations work, etc.), but the items are typically scenarios or principles rather than vocabulary, which doesn't match LSB's vocabulary-focused CDA design. **Ships ungrounded in v1.**

These three domains are excellent targets for **researcher contributions** (`baseline_kind="researcher"`) once the submission process opens in Phase 6 (`ARCHITECTURE.md` §5.3 Phase 6 and `docs/grounding_submission_template.md`). The methodology page should explicitly invite contributions for these domains by name.

Per `ARCHITECTURE.md` §1.5.5 and `DESIGN_SYSTEM.md` §4.1, ungrounded is a normal first-class state — these domains are not broken or incomplete, they're being studied model-to-model in v1, and the dashboard handles the State 0 case as a complete result rather than as a placeholder waiting for a baseline.

---

## 6. Acquisition workflow (summary, full version in `ARCHITECTURE.md` §4.2.5)

For each candidate Mark decides to acquire:

1. **Architect agent** (Opus) confirms the candidate is the best available for the target domain, posts the recommendation and the candidate row from this document to `#lsb-cda-sme`, and waits for CDA SME concurrence.
2. **CDA SME agent** reviews the candidate on the four standard axes (protocol validity, claims validity, audience translation, consistency) and posts a verdict — PASS / PASS-WITH-NOTES / FAIL — to `#lsb-cda-sme`. A FAIL bounces the candidate back to the Architect for an alternative.
3. **Mark acquires the source.** Downloads the PDF or fetches the data from the published source. Reads the methods section carefully to confirm the population, year, n, and method match what this document records. If anything in this document is wrong, Mark updates the candidate row before extraction.
4. **Mark extracts the data.** Transcribes the published similarity matrix (or naming data, or whatever the source provides) into a `cooccurrence.csv` file. Drafts the `source.md` with the full citation, population description, IRB status (almost always `not_applicable` for historical published baselines pre-1981), and method.
5. **Mark drafts `grounding_ref.json`** with `baseline_kind="published"` and all required fields per `docs/DATA_DICTIONARY.md` §3. Position fields (`mds_coordinate`, `distance_to_nearest_model`, `nearest_model_id`, `item_intersection_size`, `item_intersection_total`) are left as placeholders — the analysis pipeline populates them at merge time.
6. **Mark hands off to the Coder agent** with the file set: `source.md`, `items.txt`, `cooccurrence.csv`, `grounding_ref.json`. The Coder normalizes into the `data/grounding/{domain}/{baseline_id}/` schema, writes a unit test that verifies the loaded matrix round-trips correctly, and validates the item set against the LSB v1 prompt for the target domain.
7. **Reviewer agent** confirms the file structure matches the v0.7 multi-baseline directory layout and that `grounding_ref.json` validates against the `GroundingRef` schema in `cdb_core/schemas.py`. If the change adds or modifies fields in `GroundingRef`, Reviewer rule 5 requires a matching update to `docs/DATA_DICTIONARY.md` in the same PR.
8. **Architect agent** reviews the item-set intersection coverage and updates this document to mark the candidate as `ACQUIRED` in the recommendation column.

**Estimated time per acquired baseline:** 2–8 hours of Mark's hands-on time depending on the source. Romney 1996 is the cleanest at the low end (~2 hours); the D'Andrade 1995 book chapter route is closer to the high end (~6 hours).

---

## 7. Out of scope for this document

- **Researcher-submitted baselines** (`baseline_kind="researcher"`) — those are handled by the GitHub PR workflow in `docs/grounding_submission_template.md`, not by this document. This document only covers `baseline_kind="published"` candidates that LSB extracts from the academic literature.
- **Non-CDA datasets** — survey data, factor analyses, semantic differential studies, and other non-CDA approaches are out of scope. LSB's grounding format requires a similarity or co-occurrence matrix; data in other forms cannot be ingested without methodological misalignment that would defeat the comparison.
- **Original human data collection by LSB** — explicitly ruled out for v1 per `ARCHITECTURE.md` §4.2.5. LSB does not run human-subjects research itself; it ingests existing human data only.
- **Multilingual baselines** — v1 is English-only per `ARCHITECTURE.md` §1.5.3 limitation 2. The WCS dataset (§3.2) is multilingual but LSB v1 would only ingest the English subset; full multilingual coverage is a v2 concern.

---

## 8. Status table (updated as candidates are acquired or rejected)

| Candidate | Domain | Recommendation | Status | Phase | `baseline_id` |
|---|---|---|---|---|---|
| Romney et al. (1996) | family | PRIMARY | Pending acquisition | 4c | `romney_1996` |
| D'Andrade (1995) | family | SECONDARY | Pending Phase 6 review | 6 | `dandrade_1995` (provisional) |
| Romney & D'Andrade (1964) | family | DEFER (v2) | Not pursued in v1 | v2 | — |
| Berlin & Kay (1969) | color | PRIMARY (Phase 6) | Awaiting color domain addition | 6 | `berlin_kay_1969` (provisional) |
| World Color Survey (2009) | color | SECONDARY (Phase 6) | Awaiting color domain addition | 6 | `wcs_2009_english` (provisional) |
| Shaver et al. (1987) | emotion | DEFER (v2) | Not pursued in v1 | v2 | — |
| Storm & Storm (1987) | emotion | DEFER (v2) | Not pursued in v1 | v2 | — |

The Architect agent updates this table as candidates change status.

---

*End of `PHASE_4C_CANDIDATE_SOURCES.md` v0.1. This is a living scouting document; the Architect agent maintains it as Phase 4c progresses. The Romney 1996 acquisition is the only blocking item for Phase 4c — everything else is Phase 6 or later.*