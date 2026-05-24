# UI/UX Verdict: Phase 9a T9 — PileComparison

**Date:** 2026-05-24
**Reviewer:** UI/UX agent (Sonnet)
**Document reviewed:** `docs/status/2026-05-24-phase9a-viz-gap-kickoff.md` T9

---

## UI/UX VERDICT: PASS-WITH-NOTES

| Criterion | Verdict |
|---|---|
| 1 — OWID design fidelity | PASS-WITH-NOTES |
| 2 — 30-second journalist test | PASS-WITH-NOTES |
| 3 — Researcher reproduce-and-cite | PASS |
| 4 — WCAG AA accessibility | PASS-WITH-NOTES |

---

## Specification Summary

### Layout
- Horizontally-scrollable column grid, one column per selected model
- All columns equal width/weight (M7: no model is ground truth)
- Column width: `minmax(220px, 1fr)` CSS grid
- At `<1024px`: single-column with model-switcher pill row (not horizontal scroll)
- At `<480px`: pile labels truncated to 28 chars

### Column anatomy
1. Header: model color dot + short name (same style as FreeListColumn)
2. Pile cards: labeled cards containing term pills, sorted by pile size descending

### Pile cards
- Background: `--color-surface`, border: `--color-border`, radius: `--border-radius-md`
- Pile label: `--font-size-sm`, `--font-weight-medium`, truncated at 40 chars
- Term pills: white background, border, `--font-size-xs`, `white-space: nowrap`

### Cross-column hover highlight (the key interaction)
- Hover/focus a term pill → all instances of that term across columns highlight simultaneously
- Highlight: `--color-surface-hover` background, `--color-text-secondary` border, card `--shadow-sm`
- Absent terms shown as dashed muted placeholder on hover only

### Term stability (R10 uncertainty)
- `≥80%`: default pill (no indicator)
- `60-79%`: `1px dashed var(--color-border)` border
- `<60%`: `1px dashed var(--color-text-secondary)` border, `--color-text-caption` text
- Tooltip on all pills: "Placed here in [N]% of runs for [model short name]"
- Legend row below grid showing three tiers

### VizSwitcher tab
- Label: "Pile Structure"

### ReadAsTableToggle
| Model | Pile label | Term | Stability (%) |

### Copy
All visible copy in `apps/dashboard/src/copy/pile_comparison.ts`.
All sr-only prose in `screen_reader_summaries.ts`.

### Binding notes
- N1: term_stability must be in data before shipping (R10 — no bare point estimates)
- N2: visible description paragraph required above columns (journalist test)
- N3: CSV export for "Pile Structure" tab must produce 4-column table
- N4: term pills require `tabindex="0"` with focus-triggered tooltip (WCAG AA)
- N5: at `<1024px` use single-column model-switcher, not horizontal scroll
- N6: no Sankey diagram (imports directionality framing, violates M7 symmetry)

### No new tokens required
All visual decisions use existing tokens from `tokens.css`.

---

*End of verdict. DESIGN_SYSTEM.md §12.10 update will be committed with T9.*
