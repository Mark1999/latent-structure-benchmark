# UI/UX Verdict — Remedy B T4 (centrality_ci consumption)

**Date:** 2026-05-28
**Task:** Remedy B T4 — frontend consumption of published `centrality_ci` (commit `9cfa677`)
**Gate:** UI/UX agent

---

## Verdict: PASS-WITH-NOTES

```
1. OWID design fidelity:      PASS (one noted item)
2. 30-second journalist:      PASS
3. Researcher cite path:      PASS
4. WCAG AA:                   PASS (one noted item)

DESIGN_SYSTEM.md update:      not required (by UI/UX) — but see Reviewer Item 3
```

No required corrections before merge. The notes below are observations.

---

## Findings

**1. OWID fidelity — PASS.** Whiskers (span line + capped verticals) sourced from published `centrality_ci`; no client-side compute. x-domain expands to include CI bounds (no clipping). 0.7 opacity / 1.5px stroke read as uncertainty, not as visual equals of the bars. The visible SVG score text shows the point estimate while the full `[lo–hi]` lives in the bar `aria-label` + tooltip — acceptable density tradeoff because the whisker renders the uncertainty visually on the same row (parallels MDS tooltip-coords + ellipse). R10 satisfied on both chart and table paths.

**2. 30-second journalist — PASS.** Plain-language description above the chart; SR summary usable; tooltip "(model-resampled, B=500)" is the permitted §15.4 supplementary footnote (dark tooltip, supplementary to the 12px CI line, with accessible counterparts in table + aria-label). No forbidden vocabulary in visible strings.

**3. Researcher reproduce-and-cite — PASS.** Table caption: "95% CI columns show bootstrap confidence intervals (model-resampling with replacement, B=500, percentile method)." Sufficient to cite. No per-model Bootstrap N column is correct — the published shape is a bare `[lo, hi]` tuple by design; B=500 is domain-wide and stated in the caption.

**4. WCAG AA — PASS.** U1 (table container always in DOM, `aria-controls` resolves) and U2 (pressed-state border) satisfied by reuse. Error-bar `<g>` is `aria-hidden`; CI conveyed via bar `aria-label` + SR summary (not color-alone). Table `<th scope="col">` correct; CI columns rendered consistently (both cells or neither). §15.4 10px exception conditions all met.

## Observations (non-blocking)
- The `hasCi === false` path (no CI, <3 models) is handled correctly — whiskers suppressed, honest SR + caption text. Verify at integration that 3+-model domains always publish a non-empty `centrality_ci` so the false branch is only reachable on genuinely under-populated domains (data-pipeline concern, not component).
- SourceAttribution is domain-level, not per-tab (pre-existing pattern); not a deficiency of this PR.

---

*Verdict gates the merge alongside the CDA SME T4 verdict (`2026-05-28-remedy-b-t4-cda-sme-verdict.md`, PASS-WITH-NOTES) and the Reviewer (PASS-WITH-NOTES). All three PASS; the centrality-CI remediation chain is closed pending application of the mandatory notes (Reviewer Item 3 + CDA SME M1/M2).*
