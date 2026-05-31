# UI/UX Verdict — food promotion (2026-05-31)

**Verdict: PASS-WITH-NOTES.** OWID PASS / journalist PASS-WITH-NOTES (F2) / researcher FAIL-on-one-item (F3a, fixable by Coder, no design gap) / WCAG PASS. DESIGN_SYSTEM §16.2 + §15.5(b) date-source amendment → v0.12.0.

Copy is CDA-SME-locked (`docs/status/2026-05-31-food-promote-cda-sme-verdict.md` C1–C5). UI/UX gated layout/placement/WCAG only.

## Findings
- **F1 CLEAR:** food term-map empty→populated needs no empty-state cruft removal; TermMap early-returns a placeholder when `terms.length===0`, renders full map when populated. Food inherits today's Stage 1+2 (viewport-fill + scrollbar zoom) automatically — no food-specific path.
- **F2 (PASS-WITH-NOTES → fix required):** `ProvenanceFooter.tsx` ~L98 hardcodes `· baseline 2026-05-30`. Once food's footer enables it'd show the wrong/stale date on food. FIX: source from provenance.json top-level `generated_at_utc` (display `.slice(0,10)`); add `generated_at_utc?: string` to `ProvenanceData`; render-nothing on absent (no "baseline undefined"). Mobile already hides the suffix.
- **F3a (researcher cite — fix required, CDA C3/C4 binding):** methodology page is still a "coming soon" placeholder, so the required n-count + M4a disclosure has nowhere to live. FIX: add a stub `<section>` "Cross-model term map and uncertainty" with the M4a sentence + the C3 informant-count sentence (verbatim from SME C3), reusing existing `.methodology-page__*` classes. Minimum viable cite-path disclosure required when food's term-MDS ships.
- **F4 WCAG: no new concerns.**

## Required before merge (atomic commit, CDA C6)
1. Footer date sourced from provenance.json `generated_at_utc` (not hardcoded). [DESIGN_SYSTEM §15.5(b)/§16 amendment v0.12.0]
2. MethodologyPage term-MDS stub section with M4a + C3 n=15/n=14/n=8 disclosure. [§16.2]
3. C1 paragraph amendment ("family, holidays, and food") — verbatim per SME C1 option.
4. provenance.json food entry (auto-enables footer via existing B5b conditional — no component change beyond #1).
5. All in ONE commit (data + provenance.json + C1 + C3/C4 stub + footer date).
