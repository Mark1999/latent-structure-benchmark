---
name: project-m1-methodology-replace-verdict
description: M1 Architect plan verdict (2026-06-10) — replace MethodologyPage sections 1-6 with Mark-authored final draft, move Data provenance + Cross-model term map sections to DataPage; PASS-WITH-NOTES.
metadata:
  type: project
---

CDA SME verdict on M1 Architect plan (2026-06-10): **PASS-WITH-NOTES**.

**Why:** Plan correctly satisfies the §1.5.6 binding rules (mismatch-is-the-finding in §1 lead paragraph; forebears Romney/Weller/Batchelder/D'Andrade/Borgatti named with four DOI/PDF links in §2). The cross-page move from MethodologyPage to DataPage is atomic-by-design, the duplicate-`id` defect on `data-provenance-heading` was caught by the Architect (Step 2c rename to `data-provenance-pointer-heading`), and the test-10 scanner exclusion is preserved via heading-id continuity at `#what-this-does-not-measure-heading`. The §16.2 model-resample bootstrap sentence (B=200) is preserved byte-identical on its move to DataPage.

**Binding M-notes (must apply before Coder receives plan):**

- **M1-N1.** Section 3 ("What corpus lens means," draft line 43) contains the phrase "not because they have beliefs or lived experience" — this is a cite-to-disclaim construction parallel to Section 6's "see family" pattern. The architect plan currently extends the test-10 forbidden-vocab scanner exclusion only to the `#what-this-does-not-measure-heading` section. Required: add a header-comment block in `MethodologyPage.tsx` immediately before Section 3 documenting the cite-to-disclaim move (mirroring the lines 132-139 comment block before Section 4), so the Reviewer's CLAUDE.md §7 manual sweep does not flag the disclaim. Test 10 does not need to exclude Section 3 (the FORBIDDEN_PATTERNS list scans for the §7 framing-word patterns, not for the "belief" stem); the comment block is the protection.

**Advisory notes (non-blocking):**

- **M1-A1.** Section 1 paragraph 1 expresses the §1.5.6 binding as "That mismatch... It is the finding," not the canonical "The mismatch is the finding" verbatim string used in DataPage Section A. Substance is satisfied. Architect should confirm with Mark that the variant phrasing is intended; if Mark wants surface-level cross-page consistency, the simplest move is to add the canonical sentence as a leading clause to section 1 paragraph 1.
- **M1-A2.** Architect plan §7 says "all eleven (was twelve)" tests pass — current MethodologyPage.test.tsx has 11 tests, not 12. Math reconciles to 9 after drops + 2 retained + 1 new pointer-sentence test = 12, or to 11 if the Architect intends to merge the eight heading assertions into a smaller count. Coder should reconcile the test count in the docs/status verdict file but the test-coverage substance is what matters and is correct.
- **M1-A3.** Mark's draft Section 4 no longer names Smith's S, OCI, or Romney CCM in inline prose (the v0.17.0 placeholder did). This is Mark's authorial choice and is methodologically defensible at the journalist-30-second audience tier. Names appear in §16.2 (model-resample bootstrap) and elsewhere on Data page surfaces.

**Axis scorecard:**
- Axis 1 — Protocol validity: PASS (free-list + textual pile-sort described accurately)
- Axis 2 — Analytical validity: PASS (MDS plain-language description defensible; uncertainty-ellipses framing preserved; §16.2 B=200 bootstrap sentence verbatim on move)
- Axis 3 — Claims validity: PASS (§1.5 limits enumerated; "structure is the finding, inner life is not on the table" closes the section; no overclaim)
- Axis 4 — Audience translation: PASS-WITH-NOTES (M1-N1 cite-to-disclaim documentation required to avoid Reviewer false-positive on Section 3)

**Register compliance:** PASS. "Consensus" bullet in §5 is Register 2 (between-model) by phrasing — "models converge on a shared structure" — no Register 1 mislabeling.

**Vocabulary compliance:** PASS-WITH-NOTES (M1-N1).

**How to apply:** Architect updates plan with M1-N1 comment-block requirement before Coder dispatch. Confirmation of M1-A1/A2/A3 with Mark is non-blocking; UI/UX routing can proceed in parallel.
