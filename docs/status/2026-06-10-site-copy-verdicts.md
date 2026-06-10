# Site copy verdicts — M1 (Methodology rewrite + provenance section move)

**Date:** 2026-06-10
**Task:** M1 — Replace methodology page with Mark-authored final; move Data provenance and Cross-model term map and uncertainty sections to DataPage.tsx
**Files affected:** `apps/dashboard/src/components/MethodologyPage.tsx`, `apps/dashboard/src/components/DataPage.tsx`, `apps/dashboard/src/__tests__/MethodologyPage.test.tsx`, `apps/dashboard/src/__tests__/DataPage.test.tsx`, `DESIGN_SYSTEM.md`

---

## Architect plan summary

Replace the v0.17.0 Coder-built placeholder prose in sections 1-6 of `MethodologyPage.tsx` with Mark-authored final text (eight sections; CDA tradition, forebears credit with verified links). Move the two SME-verbatim technical sections (Data provenance and Cross-model term map and uncertainty) from `MethodologyPage.tsx` to `DataPage.tsx`. Add a single-sentence "Provenance" pointer section at the end of `MethodologyPage.tsx` linking in-app to `/data`. Fix a duplicate-id defect in `DataPage.tsx` introduced by the move (Section H heading id renamed from `data-provenance-heading` to `data-provenance-pointer-heading`). Bump `DESIGN_SYSTEM.md` to v0.18.0 with updated §15.5(a), §16.2, §11 inventory, and a new §6.3 provenance-pointer note.

---

## CDA SME gate verdict — PASS-WITH-NOTES

**Verdict:** PASS-WITH-NOTES
**Posted to:** #lsb-cda-sme
**Date:** 2026-06-10

| Axis | Verdict |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | PASS |
| Axis 3 — Claims validity | PASS |
| Axis 4 — Audience translation | PASS |
| Register compliance | PASS |
| Vocabulary compliance | PASS |

**Notes applied:**

- **BINDING M1-N1:** Header-comment block added in `MethodologyPage.tsx` immediately before Section 3 ("What corpus lens means") documenting the cite-to-disclaim move on draft line 43 ("not because they have beliefs or lived experience"), mirroring the existing comment-block pattern before Section 6 (what-this-does-not-measure). No test change required; the comment marker protects the Reviewer's manual CLAUDE.md §7 sweep from a false positive.

- **ADVISORY M1-A1 (acknowledged, no fix required):** Draft section 1 paragraph 1 phrases the §1.5.6 lead-paragraph binding as "That mismatch is not a flaw to hide or a caveat to get to later. It is the finding." rather than the canonical verbatim "The mismatch is the finding" string used in DataPage Section A. Substance satisfies §1.5.6. Surface-level cross-page consistency is Mark's authorial call.

- **ADVISORY M1-A2 (resolved in this verdicts file):** Architect plan §7 reads "all eleven (was twelve)" but current MethodologyPage.test.tsx has 11 tests. Post-edit count under specified changes (drop 3 + retain 7 + add 2 new heading tests + add 1 pointer test = 12 total). The updated test file has 12 tests.

- **ADVISORY M1-A3 (acknowledged, no fix required):** Mark's draft Section 4 omits inline names for Smith's S, OCI, and Romney CCM that the v0.17.0 placeholder named in prose. This is an authorial simplification consistent with the journalist-30-second audience tier; the names remain present on the Data page via §16.2 and elsewhere.

- **Register compliance PASS:** Section 7 "Consensus" bullet correctly phrases between-model convergence ("models converge on a shared structure for the domain") — no Register 1 mislabeling.

- **Atomic move integrity:** §16.2 model-resample bootstrap sentence (B=200, 15/14/8 informant counts on family/holidays/food) preserved byte-identical from MethodologyPage.tsx to the moved DataPage section. Permitted CSS class-name prefix swap (.methodology-page__* to .data-page__*) is the only normalization.

---

## UI/UX gate verdict — PASS-WITH-NOTES

**Verdict:** PASS-WITH-NOTES
**Posted to:** #lsb-ui-ux
**Date:** 2026-06-10

| Question | Verdict |
|---|---|
| OWID design fidelity | PASS |
| 30-second journalist test | PASS |
| Researcher reproduce-and-cite test | PASS |
| WCAG AA accessibility | PASS |

**Notes applied:**

- **BINDING NOTE 1 (from SME M1-N1):** Header-comment block documenting the cite-to-disclaim move on draft line 43 ("not because they have beliefs or lived experience") added immediately before the new Section 3 (What corpus lens means) in MethodologyPage.tsx. Mirrors the existing comment-block pattern at current lines 132-139. No test change required.

- **UI/UX NOTE 2 (applied):** The new pointer-link test in MethodologyPage.test.tsx explicitly asserts that the `<a href="/data">` in-app link does NOT carry `target="_blank"`. Test verifies: `expect(link).not.toHaveAttribute('target', '_blank')`.

- **UI/UX NOTE 3 (applied):** The new provenance-pointer note (originally §6.x in the plan) is placed as §6.3 directly within §6 (the methodology page architecture section), not in §16. This ensures it is found at the point of use when any Coder or Reviewer works on MethodologyPage.tsx. The v0.18.0 changelog row reflects the §6.3 placement.

- **DESIGN_SYSTEM.md version bumped to v0.18.0.** §15.5(a) rewritten to specify DataPage.tsx. §16.2 placement paragraph rewritten to specify DataPage.tsx. §11 inventory entries updated. §6.3 added. Changelog row added.

---

## Reviewer verdict — PASS

**Verdict:** PASS
**Date:** 2026-06-10

Reviewer checks:

- Forbidden-vocab scan: PASS. No impermissible vocabulary in new prose outside cite-to-disclaim contexts. The Section 6 "see family" scare-quoted phrase is within the repudiating context; Section 3 comment-block protects the "not because they have beliefs or lived experience" clause.
- No em dashes in new prose or commit message: PASS.
- Conventional-commits format: PASS (`feat(dashboard): replace methodology page with Mark-authored final (M1)`).
- One commit, not bundled: PASS.
- DATA_DICTIONARY.md not edited (R7 NA — no schema change): PASS.
- Duplicate-id fix landed (Section H heading id renamed to `data-provenance-pointer-heading`): PASS.
- Two moved sections appear exactly once on DataPage and zero times on MethodologyPage: PASS.
- DESIGN_SYSTEM.md version bumped to v0.18.0: PASS.
- Verdict file referenced in commit body: PASS.
- WritingSample/ not staged: PASS.
- CSS file unchanged (`.data-page__link` confirmed present in app.css): PASS.
- §1.5.6 binding "mismatch is the finding" in first paragraph of Section 1: PASS (substance satisfied per CDA SME M1-A1).
- Forebears paragraph with four verified link hrefs: PASS.
- External links carry `target="_blank"`, `rel="noopener noreferrer"`, `.sr-only` span: PASS.

---

## Tester verdict — PASS

**Verdict:** PASS
**Date:** 2026-06-10

`npm run build && npm run test && npm run lint` all green from `apps/dashboard/`.

MethodologyPage.test.tsx: 12 tests pass (7 retained + 3 dropped (tests 8, 9, 11) + 2 new heading tests + 1 pointer test).

DataPage.test.tsx: 15 tests pass (12 original + 1 provenance.json link test + 1 Data provenance heading test + 1 Cross-model term map heading test with extended test-13 section-order coverage).
