# UI/UX Verdict: Phase 9a T6+T7 — Term MDS Plot + Dendrogram

**Date:** 2026-05-24
**Reviewer:** UI/UX agent (Sonnet)

## UI/UX VERDICT: PASS-WITH-NOTES

| Criterion | Verdict |
|---|---|
| 1 — OWID design fidelity | PASS-WITH-NOTES |
| 2 — 30-second journalist test | PASS-WITH-NOTES |
| 3 — Researcher reproduce-and-cite | PASS |
| 4 — WCAG AA accessibility | PASS-WITH-NOTES |

## Key decisions

### T6 — Term MDS Plot ("Term Map")
- Tab: "Term Map" at index 1, fragment `#term-mds`
- Cluster colors: new 8-color palette (--color-cluster-1..8), NOT model colors
- Ellipses: hover/focus-only default, "Show uncertainty" toggle for all-at-once
- Labels: greedy 8-compass collision avoidance, 12px, hidden at <768px
- Cluster regions: large 24px background text at 20% opacity, show/hide toggle
- Points: POINT_RADIUS=4 (smaller than model MDS for density)
- Tooltips: dark inverted style
- Description: "Where [domain] terms cluster in model output space..."
- Stress value shown below axis labels

### T7 — Dendrogram ("Cluster Tree")
- Tab: "Cluster Tree" at index 2, fragment `#cluster-tree`
- Orientation: left-to-right (horizontal), root left, leaves right
- SVG: 800px wide, height dynamic (n_terms * 20 + margins)
- Branches: cluster-colored, gray for cross-cluster merges
- BP < 70%: dashed branches + numeric "58%" annotation
- Cluster labels at subtree root nodes (WCAG 1.4.1)
- Leaf labels: 12px, hidden at <768px with toggle
- Tooltips: dark inverted style
- Description: "How [domain] terms cluster hierarchically..."

### Both
- VizSwitcher: 8 tabs total, horizontal scroll at <1024px
- ScreenReaderSummary + SourceAttribution required
- No forbidden vocabulary

Full spec in the agent output. DESIGN_SYSTEM.md §12.11 and §12.12 required before Coder begins.
