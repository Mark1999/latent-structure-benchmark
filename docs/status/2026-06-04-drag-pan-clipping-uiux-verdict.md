# UI/UX Verdict — term-map drag-pan re-add + bottom-clipping fix (2026-06-04)

**Source:** live-site reviewer feedback, annotated `screenshots/comments.png` (Term Map, Family domain): "Plot is static, should be able to move it with the mouse" + "Information is cut off at the bottom."

**Verdict: PASS-WITH-NOTES.** OWID PASS / journalist PASS / researcher PASS / WCAG PASS-WITH-NOTES (drag-pan must not be the sole path to content — keyboard scroll + zoom buttons must reach it; satisfied). DESIGN_SYSTEM §17 → v0.13.0 (§17.4 replaced, §17.11 + §17.12 added). No new tokens. Full §17 text in the dispatch transcript — Coder applies verbatim.

## Root cause (both comments, one cause)
At k=1 `.term-map-pan-viewport` is `overflow:hidden` AND Stage 2 removed drag-pan → content below the viewport bottom is unreachable (no scroll, no drag) → looks static + bottom labels ("Foster family", "Step-family relations", SVG footer at y=H-6) clipped. The `.term-map-stress` footer is a sibling (DOM order) and does NOT overlap — not the cause.

## Decided changes (Mark: re-add drag-pan; scrollbars STAY — additive, not a reversal)
1. **Drag-pan re-added, coexists with native scrollbars.** Active only when `--scrollable` present (k>1.02 OR k=1-overflow). `window` listeners for mousemove/mouseup; `term-dot` guard (don't drag from a dot); `e.preventDefault()` to suppress text-select; cleanup in useEffect return. Lens (auto-disabled at k>1) and drag-pan operate on independent props — no conflict.
2. **Bottom-clipping fix:** `pad.b` 40→52; SVG footer annotation `y=H-6`→`y=H-14`; replace `applyScale` class-toggle with `updateScrollableModifier(k)` that adds `--scrollable` at k=1 when `svg.scrollW/H > panVp.clientW/H`; add a `useLayoutEffect` to re-check after `svgContent` commits. Enabling `--scrollable` at k=1-overflow is what makes the clipped content reachable (and activates drag-pan there).
3. **Cursor:** `.term-map-pan-viewport--scrollable { cursor: grab }`; new `.term-map-pan-viewport--dragging { cursor: grabbing; user-select: none }` + reduced-motion guard.

## Required before merge (7 items — full detail in transcript §"Required before merge")
drag-pan handlers (§17.4 block), updateScrollableModifier + useLayoutEffect (§17.11 Fix B), pad.b=52, footer y=H-14, cursor CSS (§17.12), window-listener cleanup, manual browser verify (Foster family/Step-family reachable at k=1; grab/grabbing cursor; click-dot doesn't drag; lens+pan coexist; dblclick reset incl scrollTo(0,0)).

## WCAG
Keyboard path (arrow-key scroll on focused pan-viewport + existing +/−/Reset zoom buttons) reaches all content independently of drag-pan → drag-pan is enhancement, not sole path. PASS.
