---
name: project-m2-about-page-verdict
description: M2 About page plan verdict 2026-06-10 PASS-WITH-NOTES; source register-clean; two protected occurrences (broad-sense culture definition + canonical disclaim sentence); header-comment must enumerate BOTH
metadata:
  type: project
---

M2 About page Architect plan — CDA SME PASS-WITH-NOTES verdict on 2026-06-10.

**Why:** Static AboutPage component renders Mark-authored `/opt/lsb-agent/WritingSample/mark-dawson-about.md` text verbatim; adds fifth NavBar tab "About" rightmost; reuses .methodology-page* classes; no schema, no backend. Two source sentences need cite-to-disclaim protection: source paragraph 3 sentence "I use culture in that broad sense..." (human-anthropological definition, not model-facing) and source paragraph 6 sentence "does not claim that models have beliefs, intentions, lived experience, or culture in the human sense" (canonical §1.5 disclaim, parallel to MethodologyPage line 154 and Section 6 scare-quote pattern).

**How to apply:**

- Source paragraph 2 phrase "how AI systems organize human worlds" is register-clean: "organize" is the canonical §1.5.4 SAY-INSTEAD form; not a forbidden phrase.
- Two binding M2 carry-forward notes:
  - **M2-N1 (binding):** Header-comment block above the single `<section>` must enumerate BOTH protected occurrences (broad-sense culture definition + canonical disclaim sentence), not only the disclaim as the Architect's §3.1 currently describes. Mirror MethodologyPage.tsx lines 134-141 (Section 3 cite-to-disclaim block) and 217-223 (Section 6 scare-quote block). One comment block listing both is acceptable; two adjacent comment blocks are also acceptable.
  - **M2-N2 (advisory):** Test case 5 forbidden-vocab buildPat must use the §7 standalone patterns that actually apply (model-facing cognition-attribution words plus the canonical "how-models-see" pattern). Do NOT add a too-loose `cultural` regex that would false-positive on source paragraph 6 "cultural-domain methods to language models" (a register-clean methods phrase). The literal standalone categorical-bias phrase does not appear in source; the test as planned will pass.
- The plan correctly forbids: hire-me CTA, contact form, mailto, portrait, services/consulting language. Reviewer rejects on detection per [[reference-mark-writing-voice]] demonstration-not-portfolio framing.
- Plan correctly preserves: verbatim prose, h1 → h2 normalization only, no copyediting, no paragraph reordering.
- All four axes PASS (protocol N/A, analytical N/A, claims PASS, audience translation PASS).
- Register compliance PASS, vocabulary compliance PASS (with M2-N1 header-comment protection applied).
- WritingSample/ remains untracked per [[feedback-hardware-md-local]] precedent (operator-local files not committed).
