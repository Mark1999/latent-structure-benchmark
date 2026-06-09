# Phase 9a — Data download tab — Architect plan (2026-06-08)

**Task:** kickoff §6.1 task 6. Replace the `navTab === 'data'` placeholder (`App.tsx:192-205`,
"Data download page — coming soon") with a real `<DataPage>`. Mark flagged urgent ("we made a
promise to make the data downloadable, sooner than later"). **Gate path:** Architect → CDA SME
(LIGHT — all copy verbatim from launch-vetted artifacts) → UI/UX → Coder → Reviewer → Tester.

## 1. Approach
Static `<DataPage>` (no fetch; URLs fixed; provenance handled by the already-mounted
ProvenanceFooter). Mirror `MethodologyPage.tsx` structure + the `.methodology-page*` CSS idiom
(append `.data-page*` to `app.css`, reuse existing tokens, no new tokens without UI/UX). ALL prose
lifted verbatim from `data/open_bundle/README.md` + `huggingface_dataset_card.md` + ARCHITECTURE
§6.6/§6.7 — Coder writes NO new framing prose, only assembles.

## 2. Canonical URLs (verified)
- HF dataset: `https://huggingface.co/datasets/AILLM1999/latent-structure-benchmark`
- DOI: `https://doi.org/10.5281/zenodo.20293554` (Zenodo record `https://zenodo.org/records/20293554`)
- Tarball (~1.55 GB): `https://f005.backblazeb2.com/file/lsb-open-data/lsb_open_bundle_v1.tar.gz`
- GitHub: `https://github.com/Mark1999/latent-structure-benchmark`
- SHA256: `7064b325a25f90d2555138e7d944b129e78cbc7e18eace663b058166a6cd5983  lsb_open_bundle_v1.tar.gz`
  (verbatim from huggingface_dataset_card.md:66)

## 3. Sections (A-H), each verbatim-sourced
- **A Header** "Data" + the corpus-lens subhead lifted verbatim from open_bundle/README.md (already §1.5-vetted).
- **B Get the data** → HF dataset card (primary CTA).
- **C Download the tarball** → B2 link, with a binding SIZE WARNING ("Approx. 1.55 GB. Direct download starts when you click.") rendered BEFORE the anchor in reading order + the SHA256 in a `<code>` block for copy-verify.
- **D Cite this dataset** → DOI link + Zenodo record link + the citation block verbatim ("Dawson, M. (2026). Latent Structure Benchmark (LSB) Open Data Bundle v1. Zenodo. https://doi.org/10.5281/zenodo.20293554") in `<pre><code>`. Copy-button DEFERRED (out of size).
- **E Source code** → GitHub link + reproduce.py one-liner.
- **F What's in the bundle** → the file-by-file `<dl>` lifted verbatim from open_bundle/README.md (informants.jsonl, failures.jsonl, decline_interviews.jsonl, lsb.sqlite, build_db.py, DATA_DICTIONARY.md, prompts/v1/, domains/v1/, MANIFEST.txt, LICENSE-OPENBUNDLE) + the reproduce one-liner + the bundle-stats sentence ("1,291 informant records produced by 17 models across 3 domains...") verbatim from the HF card.
- **G Licenses** → ARCHITECTURE §6.6: code Apache-2.0; open bundle CC0; in-repo working data CC-BY-4.0; docs CC-BY-4.0; + the split-licensing closing sentence verbatim.
- **H Provenance pointer** → one line pointing to the footer (no new fetch).

## 4. External-link contract (binding, every external anchor)
`target="_blank"` + `rel="noopener noreferrer"` + nested `<span class="sr-only"> (opens <dest> in new tab)`.
The B2 anchor's sr-only also conveys size: "(starts 1.55 GB download in new tab)". Precedent:
ProvenanceFooter.tsx:96-101, MethodologyPage.tsx:50-58. `<main aria-label="Data download">`. `<h2>`
per section, no `<h1>` (NavBar is the landmark).

## 5. Gates
- **CDA SME — LIGHT.** All prose verbatim from launch-vetted artifacts; only the header subhead is
  methodology-adjacent (must read as a positive claim, not an absence framing per pitfall #4). Expected
  PASS / PASS-WITH-NOTES. Verdict `docs/status/2026-06-08-phase9a-data-tab-cda-sme-verdict.md`.
- **UI/UX — required.** Card layout (Architect recommends bare sections like the methodology page, no card
  chrome), SHA256 `<code>` block, size-warning treatment (recommend `role="note"`), the 4 standard
  questions, external-link a11y. Open visual Qs in plan §6.2. Verdict `…-data-tab-ui-ux-verdict.md`.
- **Reviewer:** §7 vocab, pitfall #4 (no absence framing), pitfall #15 (tokens exist), external-link
  contract on every anchor, byte-fidelity of lifted copy (spot-grep vs sources).

## 6. Test plan (vitest, no fetch) — `__tests__/DataPage.test.tsx`
(1) renders + `<main aria-label="Data download">`; (2-4,7) HF/DOI/B2/GitHub links present with exact
hrefs + target=_blank + rel=noopener; (5) "1.55 GB" warning before the tarball anchor; (6) SHA256
verbatim in `<code>`; (8) citation first line in `<pre><code>`; (9) every external `<a>` has
target+rel (loop); (10) every external `<a>` has an "opens" sr-only; (11) no forbidden vocab; (12)
all four licenses enumerated. build+test+lint green.

## 7. Files + scope
ADD `components/DataPage.tsx` + `__tests__/DataPage.test.tsx`; EDIT `App.tsx` (one-line swap, add
import) + append `.data-page*` to `styles/app.css`. NO schema/packages/DATA_DICTIONARY/new-deps. One
commit `feat(dashboard): build Data download tab (Phase 9a §6.1 task 6)`. **Coder stages ONLY its own
files (targeted `git add` paths); Mark has uncommitted methodology-scaffold edits + unpushed commits in
the tree — do NOT `git add -A`.**

## 8. Acceptance criteria
Eight sections present + verbatim-sourced; four URLs as anchors with the link contract; SHA256 exact;
citation byte-matches; size warning before the anchor + sr-only; no forbidden vocab; tokens all exist;
no real fetch in tests; 12 tests pass; build+test+lint green; CDA SME + UI/UX + Reviewer verdicts in
docs/status/; one commit referencing them.
