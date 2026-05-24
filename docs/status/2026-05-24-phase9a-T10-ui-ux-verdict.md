# UI/UX Verdict: Phase 9a T10 — CentralityChart

**Date:** 2026-05-24
**Reviewer:** UI/UX agent (Sonnet)
**Document reviewed:** `docs/status/2026-05-24-phase9a-viz-gap-kickoff.md` T10

---

## UI/UX VERDICT: PASS-WITH-NOTES

| Criterion | Verdict |
|---|---|
| 1 — OWID design fidelity | PASS |
| 2 — 30-second journalist test | PASS-WITH-NOTES |
| 3 — Researcher reproduce-and-cite | PASS |
| 4 — WCAG AA accessibility | PASS-WITH-NOTES |

---

## Specification Summary

### Chart geometry
- SVG width: 600 (matches MDSPlot SVG_WIDTH)
- Height: dynamic — `max(240, n_models * 36 + margin.top + margin.bottom)`
- Bar slot: 36px (bar 20px + 8px gap above + 8px gap below)
- Bar height: 20px
- Margins: top 24, right 120, bottom 48, left 160

### Bar rendering
- Models sorted descending by centrality score (highest at top)
- Bar fill: model's assigned color from `modelColors` prop (same palette as MDSPlot)
- Error bars (when CI data exists): vertical line at bar end with 6px horizontal caps, model color, 1.5px stroke, round linecap
- Zero axis line: `--color-border`, 1px, always rendered

### Labels
- Model name: right-aligned at left margin - 8px, `--font-size-sm` (14px), `--color-text-primary`
- Score label: right of bar/error-bar, `--font-mono`, `--font-size-xs` (12px), `--color-text-caption`
- X-axis label: "Cultural centrality score" at `--font-size-xs`, `--color-text-secondary`, centered below

### Tooltip
- Dark inverted tooltip (background: `--color-text-primary`, text: `--color-background`) is approved as a design-system extension for dense data tooltips. This departs from the existing MDSPlot light tooltip but is acceptable because the CentralityChart tooltip contains 6 lines of content including the CDA SME M8 verbatim paragraph; a light tooltip at that density would compete with the chart behind it.
- Divider line between tooltip sections: use token `--color-tooltip-dark-divider` (new token, value `rgba(255, 255, 255, 0.15)`).

### Negative centrality
- Bar extends left of zero axis. No red/error coloring.
- Italic "(negative centrality)" label in `--color-text-caption`.

### ReadAsTableToggle table columns
Rank | Model | model_id | Centrality score | 95% CI lower | 95% CI upper | Bootstrap N | Notes

### Mobile
- `<768px`: SVG width="100%" with viewBox
- `<480px`: model names truncated to 12 chars, score labels suppressed

### DESIGN_SYSTEM.md update required
- Add CentralityChart to component inventory
- Add `--color-tooltip-dark-divider` token
- Document dark tooltip exception with rationale

---

## Notes

**N1 (30-second journalist):** Chart must have a title, axis label, and one-sentence interpretive affordance. CDA SME M8 provides the approved text. Coder must ensure these are rendered.

**N2 (WCAG AA):** The dark tooltip must maintain WCAG AA contrast. White text on `--color-text-primary` background (dark gray/black) exceeds 7:1 ratio — PASS.

---

*End of verdict. DESIGN_SYSTEM.md update to follow.*
