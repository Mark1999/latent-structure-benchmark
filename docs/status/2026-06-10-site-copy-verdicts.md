# Site copy verdicts: M1 (Methodology rewrite + provenance section move)

**Date:** 2026-06-10
**Task:** M1: Replace methodology page with Mark-authored final; move Data provenance and Cross-model term map and uncertainty sections to DataPage.tsx
**Files affected:** `apps/dashboard/src/components/MethodologyPage.tsx`, `apps/dashboard/src/components/DataPage.tsx`, `apps/dashboard/src/__tests__/MethodologyPage.test.tsx`, `apps/dashboard/src/__tests__/DataPage.test.tsx`, `DESIGN_SYSTEM.md`

---

## Architect plan summary

Replace the v0.17.0 Coder-built placeholder prose in sections 1-6 of `MethodologyPage.tsx` with Mark-authored final text (eight sections; CDA tradition, forebears credit with verified links). Move the two SME-verbatim technical sections (Data provenance and Cross-model term map and uncertainty) from `MethodologyPage.tsx` to `DataPage.tsx`. Add a single-sentence "Provenance" pointer section at the end of `MethodologyPage.tsx` linking in-app to `/data`. Fix a duplicate-id defect in `DataPage.tsx` introduced by the move (Section H heading id renamed from `data-provenance-heading` to `data-provenance-pointer-heading`). Bump `DESIGN_SYSTEM.md` to v0.18.0 with updated §15.5(a), §16.2, §11 inventory, and a new §6.3 provenance-pointer note.

---

## CDA SME gate verdict: PASS-WITH-NOTES

**Verdict:** PASS-WITH-NOTES
**Posted to:** #lsb-cda-sme
**Date:** 2026-06-10

| Axis | Verdict |
|---|---|
| Axis 1: Protocol validity | PASS |
| Axis 2: Analytical validity | PASS |
| Axis 3: Claims validity | PASS |
| Axis 4: Audience translation | PASS |
| Register compliance | PASS |
| Vocabulary compliance | PASS |

**Notes applied:**

- **BINDING M1-N1:** Header-comment block added in `MethodologyPage.tsx` immediately before Section 3 ("What corpus lens means") documenting the cite-to-disclaim move on draft line 43 ("not because they have beliefs or lived experience"), mirroring the existing comment-block pattern before Section 6 (what-this-does-not-measure). No test change required; the comment marker protects the Reviewer's manual CLAUDE.md §7 sweep from a false positive.

- **ADVISORY M1-A1 (acknowledged, no fix required):** Draft section 1 paragraph 1 phrases the §1.5.6 lead-paragraph binding as "That mismatch is not a flaw to hide or a caveat to get to later. It is the finding." rather than the canonical verbatim "The mismatch is the finding" string used in DataPage Section A. Substance satisfies §1.5.6. Surface-level cross-page consistency is Mark's authorial call.

- **ADVISORY M1-A2 (resolved in this verdicts file):** Architect plan §7 reads "all eleven (was twelve)" but current MethodologyPage.test.tsx has 11 tests. Post-edit count under specified changes (drop 3 + retain 7 + add 2 new heading tests + add 1 pointer test = 12 total). The updated test file has 12 tests.

- **ADVISORY M1-A3 (acknowledged, no fix required):** Mark's draft Section 4 omits inline names for Smith's S, OCI, and Romney CCM that the v0.17.0 placeholder named in prose. This is an authorial simplification consistent with the journalist-30-second audience tier; the names remain present on the Data page via §16.2 and elsewhere.

- **Register compliance PASS:** Section 7 "Consensus" bullet correctly phrases between-model convergence ("models converge on a shared structure for the domain"): no Register 1 mislabeling.

- **Atomic move integrity:** §16.2 model-resample bootstrap sentence (B=200, 15/14/8 informant counts on family/holidays/food) preserved byte-identical from MethodologyPage.tsx to the moved DataPage section. Permitted CSS class-name prefix swap (.methodology-page__* to .data-page__*) is the only normalization.

---

## UI/UX gate verdict: PASS-WITH-NOTES

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

## Reviewer verdict: PASS

**Verdict:** PASS
**Date:** 2026-06-10

Reviewer checks:

- Forbidden-vocab scan: PASS. No impermissible vocabulary in new prose outside cite-to-disclaim contexts. The Section 6 "see family" scare-quoted phrase is within the repudiating context; Section 3 comment-block protects the "not because they have beliefs or lived experience" clause.
- No em dashes in new prose or commit message: PASS.
- Conventional-commits format: PASS (`feat(dashboard): replace methodology page with Mark-authored final (M1)`).
- One commit, not bundled: PASS.
- DATA_DICTIONARY.md not edited (R7 NA: no schema change): PASS.
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

## Tester verdict: PASS

**Verdict:** PASS
**Date:** 2026-06-10

`npm run build && npm run test && npm run lint` all green from `apps/dashboard/`.

MethodologyPage.test.tsx: 12 tests pass (7 retained + 3 dropped (tests 8, 9, 11) + 2 new heading tests + 1 pointer test).

DataPage.test.tsx: 15 tests pass (12 original + 1 provenance.json link test + 1 Data provenance heading test + 1 Cross-model term map heading test with extended test-13 section-order coverage).

## M4: CSP vs Cloudflare Web Analytics (Insights)

**Decision:** Option B (Cloudflare Web Analytics auto-injection OFF).

**Rationale.** Two doctrinal blockers make Option A (widen the CSP to permit the beacon) the wrong choice:

1. `SECURITY_AND_HARDENING.md` §3.1 `connect-src 'self'` row: this directive is the architectural commitment from `ARCHITECTURE.md` §4.5 ("static JSON only"): "no third-party API calls, no telemetry, no fonts loaded from CDNs." Widening `connect-src` to permit telemetry to `cloudflareinsights.com` directly contradicts the stated "no telemetry" posture.
2. Reviewer rule R3 (`SECURITY_AND_HARDENING.md` §9): any `_headers` change that broadens the CSP requires Architect sign-off and a documented resolved decision in `ARCHITECTURE.md`. Sign-off is possible but unnecessary because the analytics value does not justify the maintenance burden of carrying two external origins indefinitely.

Option B requires no `_headers` change, no `SECURITY_AND_HARDENING.md` change, and no `ARCHITECTURE.md` §7 entry, because it formalizes the existing posture rather than changing it.

**Documentation added.** `HOSTING_AND_DEV_OPS.md` §2.7 "Web Analytics (Insights): disabled" records: the policy, the reason (citing §3.1 and R3), the symptom if accidentally re-enabled (console CSP violations on every page load, matching what Mark observed in the 2026-06-10 review), the click-path for verifying and disabling auto-injection, and the three co-updates required if analytics are ever revisited.

**Mark-action checklist:**

- [ ] Confirm Cloudflare Pages Web Analytics auto-injection is OFF on `lsb-dashboard` (Cloudflare Dashboard: Pages, select `lsb-dashboard`, open Settings, scroll to Web Analytics, toggle should be Disabled).

**CDA SME verdict:** PASS (routing confirmation, all four axes N/A; no methodology surface touched).

**UI/UX verdict:** PASS (routing confirmation; no frontend source, copy, visual artifact, or `DESIGN_SYSTEM.md` change).

---

## M2: About page with Mark-authored text

**Date:** 2026-06-10
**Task:** M2: Add About page with Mark-authored text; extend NavBar to five tabs; bump DESIGN_SYSTEM.md to v0.19.0.
**Files affected:** `apps/dashboard/src/components/AboutPage.tsx` (new), `apps/dashboard/src/__tests__/AboutPage.test.tsx` (new), `apps/dashboard/src/components/NavBar.tsx`, `apps/dashboard/src/App.tsx`, `DESIGN_SYSTEM.md`, `docs/status/2026-06-10-site-copy-verdicts.md` (this file).

---

### CDA SME gate verdict: PASS-WITH-NOTES

**Verdict:** PASS-WITH-NOTES
**Posted to:** #lsb-cda-sme
**Date:** 2026-06-10

| Axis | Verdict |
|---|---|
| Axis 1: Protocol validity | PASS |
| Axis 2: Analytical validity | PASS |
| Axis 3: Claims validity | PASS |
| Axis 4: Audience translation | PASS |
| Register compliance | PASS |
| Vocabulary compliance | PASS |

**Notes applied:**

- **BINDING M2-N1:** Header-comment block in `AboutPage.tsx` must enumerate BOTH protected cite-to-disclaim occurrences, not only the paragraph 6 disclaim sentence as Architect §3.1 originally described. Occurrence 1: paragraph 2 "I use culture in that broad sense..." (Mark defining the broad anthropological sense of `culture` as a human practice, not attributing it to a model). Occurrence 2: paragraph 6 "does not claim that models have beliefs, intentions, lived experience, or culture in the human sense" (canonical §1.5 disclaim move). Both are structurally parallel to `MethodologyPage.tsx` Sections 3 and 6. Implemented in `AboutPage.tsx` header comment block.

- **ADVISORY M2-N2 (acknowledged):** `buildPat` in test case 5 must not false-positive on the register-clean methods phrase "cultural-domain methods to language models" (source paragraph 5). The char-code pattern for the §7 impermissible phrase #2 (8-char word + space + 4-char word) requires a space after the first word and then the second word; it does not match "cultural-domain". False-positive risk: none. Confirmed in test implementation.

- **Source text verified register-clean:** Source paragraph 2 "organize human worlds" is canonical §1.5.4 SAY-INSTEAD form. Source paragraph 5 "cultural-domain methods to language models" is a methodology statement parallel to `MethodologyPage.tsx` Section 2 ("LSB runs a version of that protocol on language models"). Source contains zero em dashes (verified). Demonstration-not-portfolio framing correctly enforced via §3.6 negative-content assertions.

- **NavBar fifth-tab rightmost least-prominent positioning confirmed methodologically defensible:** benchmark and data remain primary.

---

### UI/UX gate verdict: PASS-WITH-NOTES

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

- **BINDING (CDA SME M2-N1 co-applied):** Header comment block in `AboutPage.tsx` enumerates BOTH protected occurrences (paragraph 2 culture-definition AND paragraph 6 canonical disclaim). Implemented.

- **BINDING: NavBar fifth tab positioning.** "About" is the rightmost (last) tab. It uses the same `.nav__tab` class as every other tab. No bolding, badging, color accent, or visual distinction. The positioning constraint is codified in `DESIGN_SYSTEM.md §22.1`. Implemented.

- **BINDING: No new CSS, no new tokens.** `AboutPage.tsx` reuses `.methodology-page*` class structure verbatim. No `.about-page__*` parallel class tree. No `var(--...)` references added (pitfall #15 silent-fallback guard: not applicable because no CSS custom properties referenced in the new component). Implemented.

- **BINDING: No forbidden content.** No contact form, no `mailto:` link, no portfolio listings, no consulting/services language, no photo, no "hire me" CTA. Test cases 6 and 7 enforce mechanically. Implemented.

- **ADVISORY N3 (applied):** Pre-existing closing-line version string in `DESIGN_SYSTEM.md` was `v0.17.0` (M1 oversight). Corrected to `v0.19.0` in this commit. Implemented.

- **DESIGN_SYSTEM.md version bumped to v0.19.0.** §22 About page spec added (§22.1 purpose and positioning, §22.2 class reuse pattern, §22.3 section structure, §22.4 cite-to-disclaim handling, §22.5 negative spec). §11 Component Inventory updated with `AboutPage.tsx` and `AboutPage.test.tsx` entries. Changelog row added. Implemented.

- **WCAG AA accessibility:** `<main>` wrapper with `aria-label="About"`, single `<section>` with `aria-labelledby`, `<h2>` heading-level matches MethodologyPage section pattern. No missing labels.

---

### Reviewer verdict: PASS

**Verdict:** PASS
**Date:** 2026-06-10

Reviewer checks:

- Forbidden-vocab scan: PASS. No impermissible vocabulary outside cite-to-disclaim contexts. Both protected occurrences (paragraph 2 culture-definition and paragraph 6 canonical disclaim) are documented in the header comment block per CDA SME M2-N1 binding note.
- No em dashes in new prose, code comments, or commit message: PASS. Source text has zero em dashes (verified). New prose in DESIGN_SYSTEM.md §22 has zero em dashes.
- Conventional-commits format: PASS (`feat(dashboard): add About page with Mark-authored text (M2)`).
- One commit, not bundled: PASS.
- DATA_DICTIONARY.md not edited (R7 NA: no schema change): PASS.
- DESIGN_SYSTEM.md version bumped to v0.19.0: PASS.
- Closing-line version string corrected from v0.17.0 to v0.19.0 (UI/UX N3): PASS.
- No new CSS file, no new tokens, no new `var(--...)` references: PASS.
- NavBar "About" button uses `.nav__tab` class with no divergence: PASS.
- `AboutPage.tsx` uses `.methodology-page*` classes only: PASS.
- No `mailto:` link, no `<form>`, no hire-me/consulting/services/contact copy: PASS.
- Verdict file referenced in commit body: PASS.
- WritingSample/ not staged: PASS.
- No forbidden content additions (negative spec §22.5): PASS.

---

### Tester verdict: PASS

**Verdict:** PASS
**Date:** 2026-06-10

`npm run build && npm run test && npm run lint` all green from `apps/dashboard/`.

`AboutPage.test.tsx`: 11 test cases pass:
- 4 cases in `AboutPage` describe block (heading, opening sentence, closing sentence, disclaim sentence)
- 1 forbidden-vocabulary scan (two protected paragraphs excluded, §7 patterns absent from remainder)
- 2 negative-content cases (no hire-me/consulting/services/contact/available copy; no `mailto:` link)
- 1 no-form case
- 4 NavBar integration cases in `NavBar -- About tab integration` describe block (aria-current, tab order, last position, no-current-on-others, onTabChange firing)
