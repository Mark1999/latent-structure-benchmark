# UI/UX Verdict — `feature/visualization-fixes`

**Date:** 2026-05-28
**Task:** viz-fixes (external-AI dashboard visualization change set, 8 commits, +1,571/−357)
**Gate:** UI/UX agent
**Diff reviewed:** `feature/visualization-fixes` vs `master` (captured at `/tmp/viz-fixes.diff`)

---

## Verdict: PASS-WITH-NOTES

```
1. OWID design fidelity:      PASS (notes on two sub-issues)
2. 30-second journalist:      PASS
3. Researcher cite path:      PASS
4. WCAG AA:                   PASS (notes on three sub-issues)

DESIGN_SYSTEM.md update:      required
```

Pre-verified before this gate (not re-checked here): `npm run build` + `npm run lint` clean; all `var(--…)` token references resolve against `tokens.css` (Pitfall #15 clear); no forbidden vocabulary; 8 provider colors correctly added to `tokens.css`.

---

## Required before merge

1. **(Code change) TermMap uncertainty ellipses have no assistive-technology exposure.**
   `term-ellipse` SVG elements carry `pointer-events="none"` and no `aria-label`/`role`. When `showUncertainty === true`, the ellipses are invisible to AT while the sighted "Show uncertainty" control is pressed — partial WCAG 1.1.1 failure and a violation of the §4.2.6 display-rule accessibility analog. Fix: when `showUncertainty === true` and ≥1 term has a non-null ellipse, update the TermMap `<svg>` `aria-label` (or SR summary) to state that confidence ellipses are shown and parameters are available in the "Read as table" view; surface ellipse params (CI semi-major / semi-minor / rotation deg / Bootstrap N) in the table path per §11 `TermMDSTable` spec.

2. **(Doc) Add DESIGN_SYSTEM.md §15** documenting the term-ellipse cluster-color choice (`getClusterColor(t.cluster)` for term-level positional uncertainty — defensible since cluster color is already the term's primary encoding; this is a new visual decision not covered by §1.2/§3.3).

3. **(Doc) §15.3 grandfather note** for the `.term-map-controls` inline-style layout pattern: accepted as-is (values map to `--space-*` / `--font-size-xs` / `--font-body` / `--color-text-primary`), but must NOT be extended — future controls use CSS classes + tokens.

4. **(Doc) §15.4 tooltip font-size exception** for `fontSize:'10px'` on the bootstrap-N span inside `.centrality-chart__tooltip-ci` (below the `--font-size-xs: 12px` floor). Accepted only inside the dark-inverted tooltip for supplementary text; document so the Reviewer has a named exception.

Items 2–4 are documentation; the implementation is already correct. Item 1 is a required code change.

---

## Findings by criterion

**1. OWID fidelity — PASS.** Token migration correct and complete across all 7 `PROVIDER_COLORS` maps, `CLUSTER_COLORS`, `HEATMAP_COLORS`, and `simToTextColor()`. Observations: (a) TermMap ellipses use cluster color (acceptable, document in §15); (b) `Focus1RunDistribution` cell-text threshold lowered to `CELL_SIZE >= 14` → 7px text at smallest size — cosmetic regression only, data available via `aria-label` + table path, not a WCAG violation.

**2. 30-second journalist — PASS.** Zero-selection lede ("Consensus baseline (all tested models)") handled; `srSummary` uses compliant phrasing ("cultural centrality score", "dominant categorical pattern"). No forbidden vocabulary.

**3. Researcher reproduce-and-cite — PASS.** No changes to source attribution or cite paths. `CentralityTable` columns match §11 inventory. *(Note: the "Bootstrap N" column labeling is the subject of the CDA SME FAIL — see that verdict; UI/UX assessed table structure, not the statistical claim.)*

**4. WCAG AA — PASS-WITH-NOTES.**
- Note A (required, item 1 above): ellipse AT exposure.
- Note B: stability pill tiers encode via border-style AND text-color, not color alone — WCAG 1.4.1 satisfied; pill `title`/`aria-label` give numeric stability to AT.
- Note C: checkbox `<label>`-wrapping-`<input>` pattern is valid; correct accessible names.
- Note D: `read-as-table-toggle__button` `min-height:32px` desktop is below AAA 2.5.5 (44px) but meets AA 2.5.8 (24px); mobile media query raises to 44px. No AA failure.

---

## DESIGN_SYSTEM.md §15 draft

The UI/UX agent drafted §15.1–§15.4 (stability pill tiers mirroring §12.10; CentralityChart inline read-as-table toggle preserving U1/U2; TermMap inline-style grandfather; tooltip footnote font-size exception). To be added to `DESIGN_SYSTEM.md` and posted to `#lsb-ui-ux` before this diff is treated as normative for future work.

---

*Verdict gates the merge. Once item 1 is implemented and items 2–4 are recorded in DESIGN_SYSTEM.md, this diff is clear from the UI/UX gate. The CDA SME methodology FAIL is a separate, harder blocker — see `2026-05-28-viz-fixes-cda-sme-verdict.md`.*
