# UI/UX Verdict — TermMap Stage 2 scrollbar zoom-model re-spec (2026-05-31)

**Verdict: PASS-WITH-NOTES.** OWID PASS / journalist PASS / researcher PASS / WCAG PASS-WITH-NOTES. DESIGN_SYSTEM §17.4 (replace placeholder) + §17.8 + §17.9, bump to v0.11.0. No new tokens.

This re-specs the scrollbar model the gate previously declined (§17.4 reserved); Mark overrode → scrollbars required. Q1 locked = everything-scales (OWID). Full §17.4/17.8/17.9 text is in the dispatch transcript (Coder applies verbatim).

## Spec highlights (binding for Stage 2 Coder)
- DOM: `.chart-wrap > .term-map-pan-viewport > svg > g[transform=scale(k)]`. Controls bar + stress footer stay OUTSIDE the pan-viewport (DOM order keeps them fixed; no position:sticky).
- Scrollbars: thin `::-webkit-scrollbar` 4px + `--color-border` thumb (mirrors .sidebar precedent) + Firefox `scrollbar-width:thin`. At k=1: `overflow:hidden`, pixel-identical to Stage 1. k>1: `.term-map-pan-viewport--scrollable` → `overflow:auto`.
- Scroll-shadow inset box-shadow (0.06 opacity) on the scrollable modifier.
- **Freeze rule (binding):** label layout computed once at k=1 and frozen; zoom changes ONLY the `<g transform>` scale, never re-runs render()/compass algorithm.
- Drag-pan REMOVED (handlers + grab cursor); native scroll is the pan. Double-click reset retained (+ scrollTo(0,0) before removing modifier).
- reduced-motion forward-guard; MAX_ZOOM stays 8 (no size caps — bigger is more accessible).
- "Ctrl+scroll to zoom" hint copy unchanged.

## OPEN — Mark to confirm before Coder starts
- **Q2 (lens at high zoom):** UI/UX RECOMMENDS **auto-disable lens when k>1.02** (disable checkbox w/ tooltip). Rationale: lens is redundant when zoomed; keeping it requires inverting the /z compensation (TermMap.tsx ~775-777) with a real "lens collapse / explosion" hazard (WCAG 2.3.1 motion). vs. keep+tune (not recommended).
- **Q3 (touch):** UI/UX RECOMMENDS **native-pinch** (§17.9 — pinch→ctrlKey wheel→zoom, two-finger→scroll, keyboard buttons as the a11y path). Zero extra handlers. vs. buttons-only (more restrictive, no a11y gain).

## WCAG note
Native scrollbars + keyboard arrow scroll + keyboard zoom buttons satisfy keyboard access. Lens auto-disable (Q2) removes the high-zoom motion hazard. Scrollbar thumb contrast is exempt (native UI affordance).
