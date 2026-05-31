# Architect Plan — TermMap layout fix + zoom-model redesign (2026-05-31)

Two-stage. Companion: UI/UX verdict `2026-05-31-termmap-layout-zoom-uiux-verdict.md` (PASS-WITH-NOTES + Mark scrollbar override). No CDA SME (viz mechanics + a11y, not methodology). No schema.

## Stage 1 — LAYOUT FIX (low risk, ships first, stops the LIVE bug)
Retains current viewBox-zoom/drag-pan/lens; only fixes the growth loop + scroll-trap + a11y.
- **1.1** Bound container height (CSS: `.chart-area`/`.chart-wrap` overflow:hidden, `.term-map-container` flex:1 1 320px) + `render()` reads stable bounded height (defensive cap vs innerHeight). Kills the runaway loop. Map fills viewport.
- **1.2** Ctrl-gate the wheel zoom (preventDefault only on e.ctrlKey) — fixes WCAG Level-A scroll-trap; plain wheel scrolls page.
- **1.3** Keyboard +/- zoom buttons + Reset button + "Ctrl+scroll to zoom" hint + aria-live (CSS classes, not inline).
- **1.4** DESIGN_SYSTEM §17 (UI/UX text).
- **1.5** Regression tests (layout no-grow, ctrl-wheel gate, keyboard zoom). [needs vitest harness — T7 dependency]
Gates: UI/UX (already PASS, re-verify after) + Reviewer + Tester. Sequential, one commit each, no parallel writes to TermMap.tsx.

## Stage 2 — ZOOM-MODEL REDESIGN (high risk; Mark's scrollbar override)
viewBox-zoom → content-scale + container overflow:auto (native scrollbars when zoomed). Drag-pan REMOVED (scrollbar replaces it).
- **PRE:** fresh UI/UX re-spec REQUIRED before any Coder work (gate declined to spec scrollbar visuals; Mark overrode). New verdict file + §17.4.
- **2.1** Restructure: fixed SVG + content `<g transform=scale(k)>` inside `.term-map-pan-viewport` (overflow:auto). Pixel-identical at k=1.
- **2.2** New zoom math (ctrl-wheel + buttons drive scale, scroll-anchored to cursor); remove drag-pan handlers.
- **2.3** LENS REWORK (the hard part): invert the /z compensation for content-scale; risk of "lens explosion" at high zoom.
- **2.4** Verify hover/ellipses/labels; freeze label layout at k=1 (no reflow on zoom).
- **2.5** §17.4 + zoom tests.
Gates: UI/UX re-spec (before) + UI/UX re-verify (after) + Reviewer + Tester.

## Coordinate-rework summary (Stage 2)
Labels/ellipses/hover live inside the scaled `<g>` → mostly NO rework (they scale with content). Drag-pan → removed. Wheel-zoom math → reworked (scroll-anchor). **Lens → real rework** (the gate-flagged hard part).

## Stop-conditions for Mark (Stage 2 kickoff)
- Q1: at zoom>1 does everything scale (labels/strokes grow — OWID style) OR positions-only (text/stroke constant on screen — scatterplot best practice)?
- Q2: lens at high zoom — keep+tune / auto-disable when zoomed / drop? Architect rec: auto-disable when k>1.
- Q3: touch/pinch behaviour.

## MARK'S DECISIONS (2026-05-31)
- Staging: **ship Stage 1 now**; Stage 2 after its UI/UX re-spec.
- Stage 1 tests: **manual browser-verify now**, automated vitest deferred to T7 (no harness yet). Task 1.5 deferred.
- Q1 (Stage 2 zoom scaling): **everything scales (OWID-style)** — at 2x, labels/dots/strokes all 2x. (Q2 lens, Q3 touch still open for Stage 2 kickoff.)
