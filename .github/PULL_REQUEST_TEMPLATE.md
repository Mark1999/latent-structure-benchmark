<!--
Latent Structure Benchmark — Human CDA Grounding Submission
============================================================

Thank you for contributing human CDA data to LSB. This PR template walks
you through everything the project needs to merge your submission and
display your data on the dashboard with full attribution.

Before you open this PR, please make sure you have read:
  • docs/grounding_submission_template.md  (file format requirements)
  • ARCHITECTURE.md §4.2.5                  (the workflow)
  • DESIGN_SYSTEM.md §4                     (how your data will appear)

The CDA SME agent will review the methodology of your submission. Mark
will merge it. The whole process typically takes 1–2 weeks.

Questions? Open a Discussion on GitHub or email security@cogstructurelab.ai.
-->

## Submission summary

**Baseline ID** (slug, e.g. `tanaka_2026_kyoto_kinship`):
<!-- Lowercase, ASCII, underscores only. Becomes the directory name and the URL slug. -->

**LSB domain this baseline belongs to** (e.g. `family`, `holidays`, `food`, `color`):

**Is this domain currently in the LSB v1 slate?**
- [ ] Yes — this is an additional baseline for an existing LSB domain
- [ ] No — this is a baseline for a domain LSB does not yet measure (LSB will queue the domain for consideration; your data is welcome either way)

**One-sentence description of the dataset** (will appear in the dashboard's grounding detail panel):

---

## Population and method

**Population description** (free text — who, when, how many, where; e.g. "US college students, ages 18–22, n=122, recruited 1990–1991, University of California, Irvine"):

**Number of human informants (n):**

**Year the data was collected** (NOT the year of publication):

**CDA method used:**
- [ ] Pile sort (Romney protocol)
- [ ] Free list + pile sort
- [ ] Pairwise similarity judgments
- [ ] Triadic comparisons
- [ ] Other (describe below):

**If "other," please describe the protocol:**

---

## Ethics

**IRB status:**
- [ ] **Approved** — IRB or equivalent ethics board reviewed and approved this study (please paste protocol number or IRB name below)
- [ ] **Exempt** — IRB review was sought and the study was determined exempt from full review
- [ ] **Not applicable** — the data predates current IRB frameworks (typical for historical published data) or was collected in a jurisdiction without IRB-equivalent oversight
- [ ] **Unknown** — please do not select this option for new submissions; "unknown" is reserved for historical published data whose ethics framework cannot be reconstructed

**IRB protocol number / approving institution** (if applicable):

**Was informed consent obtained from all subjects?**
- [ ] Yes
- [ ] Not applicable (historical data)
- [ ] Other — please explain below

---

## Rights and licensing

By submitting this PR, you confirm the following. Each box is a hard requirement; LSB cannot merge submissions where any of these are unchecked or where the answers are inconsistent with the rest of the submission.

- [ ] **I hold the rights to this data**, or I am authorized by the rights-holder to submit it for redistribution.
- [ ] **I understand and agree that LSB will redistribute this data under CC-BY-4.0** as part of the open data bundle (`ARCHITECTURE.md` §6.7), with full attribution to me / my institution / the original publication.
- [ ] **I retain all rights to my data.** LSB redistribution does not transfer copyright; I can withdraw the data later if circumstances change (a withdrawal request triggers removal from the next published bundle, but earlier published versions on Zenodo retain the data per Zenodo's permanent-versioning policy).
- [ ] **No personally identifiable information about subjects is included** in any submitted file. Subject IDs in `pile_sort_raw.csv` (if submitted) are pseudonymized.
- [ ] **I am willing to be contacted** by LSB staff during PR review and by readers of the dashboard who have questions about the methodology.

---

## Submitter

**Name:**

**Institution / affiliation:**

**Contact** (email or ORCID — will appear on the dashboard's grounding detail panel):

**Project URL or homepage** (optional):

---

## Files included in this PR

The PR should add a new directory at `data/grounding/{domain}/{baseline_id}/` containing:

- [ ] `source.md` — full citation, population description, method, IRB status, year (per `docs/grounding_submission_template.md`)
- [ ] `items.txt` — canonical item set, one item per line
- [ ] `cooccurrence.csv` — symmetric similarity matrix, header row matches `items.txt`
- [ ] `grounding_ref.json` — the `GroundingRef` object as JSON, all required fields populated (per `docs/DATA_DICTIONARY.md`)
- [ ] `pile_sort_raw.csv` — *optional but encouraged*; if included, LSB can compute a bootstrap uncertainty ellipse for your baseline on the MDS plot. Subject × pile assignments. Subject IDs must be pseudonymized.

---

## Pre-flight checks

Please run these locally before requesting review. CI will run them again on the PR.

- [ ] `cooccurrence.csv` is symmetric (every cell `[i][j]` equals cell `[j][i]`)
- [ ] `cooccurrence.csv` header row matches the contents of `items.txt` exactly (same items, same order)
- [ ] `grounding_ref.json` validates against the `GroundingRef` schema in `cdb_core/schemas.py`
- [ ] No API keys, no PII, no personal email addresses other than your contact field appear in any file (CI runs `gitleaks` and a PII scan; please double-check)
- [ ] `baseline_id` is unique within the target domain (no existing directory at `data/grounding/{domain}/{baseline_id}/`)

---

## Review process

After this PR is opened, the following happens automatically and in sequence:

1. **CI validation** — schema check on `grounding_ref.json`, format check on `cooccurrence.csv`, item-intersection coverage report against the LSB v1 item set for the target domain, `gitleaks` scan, and PII scan. CI failures block review; you'll see the failures inline and can push fixes. *Estimated wall time: 2–5 minutes.*
2. **CDA SME agent review** — the LSB CDA SME agent reviews the methodological soundness of the submission on four axes: protocol validity, claims validity (does the population description support the claims the baseline implicitly makes), audience translation (is `source.md` legible to a non-anthropologist), and consistency (does the IRB status match the population). The verdict (PASS / PASS-WITH-NOTES / FAIL) posts to `#lsb-cda-sme` and to this PR as a review comment. *Estimated wall time: same day to next business day.*
3. **Mark's review and merge** — Mark reviews the CDA SME verdict, asks any clarifying questions on the PR, and merges if PASS or PASS-WITH-NOTES with corrections applied. *Estimated wall time: 1–2 weeks depending on Mark's calendar.*
4. **Dashboard publication** — the merge triggers an analysis re-run, which writes an updated `DomainResult` with your baseline included in `groundings`. The dashboard picks up your baseline on the next publish. Your name, institution, year, and contact appear in the dashboard's grounding detail panel and on the methodology page.
5. **Inclusion in the open data bundle** — your data is included in the next release of the LSB open data bundle on Backblaze B2 and Zenodo (`ARCHITECTURE.md` §6.7), under CC-BY-4.0 with full attribution.

## How to withdraw

If circumstances change and you need to withdraw your data, open an issue on this repo with the title "Withdrawal: {baseline_id}" and a one-line reason. LSB will remove the data from the next published bundle. Earlier versions on Zenodo retain the data per Zenodo's permanent-versioning policy and cannot be retracted unilaterally; this is a Zenodo policy, not an LSB choice, and LSB will provide the Zenodo retraction instructions on request.

---

*Thank you for connecting your work to LSB. The whole point of the project is to put AI corpus-lens findings next to actual human CDA findings. Your contribution is the human half of that comparison.*
