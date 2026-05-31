# UI/UX Verdict — TermMap viewport-fill + zoom redesign (2026-05-31)

**Verdict: PASS-WITH-NOTES** (4-criteria: OWID PASS-WITH-NOTES, journalist PASS, researcher PASS, WCAG PASS-WITH-NOTES). DESIGN_SYSTEM §17 required.

## KEY CONFLICT WITH MARK'S SPEC (surfaced to Mark 2026-05-31)
Mark's spec: "when zoomed in, if objects are outside the view, there should be scroll bars."
UI/UX §17.4 DECLINED scrollbars — substituted retaining drag-to-pan. Reason given: native scrollbars in a chart container are OWID-inconsistent, and the scale-content+overflow model would require rewriting the viewBox-based lens/label-layout/ellipse-transform code (full redesign, not a bug fix). **Pending Mark's decision — do NOT implement until resolved.**

## Agreed regardless of the scrollbar decision (A+B layout fix + ctrl-wheel)
- A+B: bound container height (`.chart-area`/`.chart-wrap` overflow:hidden, `.term-map-container` flex:1 1 320px), `render()` reads stable wrapRef height → kills the growth loop. Map fills remaining viewport.
- Ctrl+wheel zoom only; plain wheel scrolls the page (gate preventDefault on e.ctrlKey) — WCAG Level A scroll-trap fix, blocker.
- WCAG: add keyboard +/- zoom buttons, a keyboard "Reset zoom" button, "Ctrl + scroll to zoom" hint, aria-live on the controls bar.
- DESIGN_SYSTEM §17 (full text in the dispatch transcript / to be placed by Coder).

## Required-before-merge: items 1-10 in the verdict body (layout CSS, ctrl-key gate, zoom buttons, reset button, hint, aria-live, CSS classes not inline, manual verify).

## MARK'S OVERRIDE (2026-05-31)
Mark overrode UI/UX §17.4: **scrollbars ARE required** (the original spec). Navigate-when-zoomed = native scrollbars (scale-content + container overflow:auto), NOT the drag-pan substitute the gate recommended. This is a redesign of the zoom model (away from viewBox) and requires reworking the lens/label/ellipse coordinate math the gate flagged. Per CLAUDE.md only Mark can override a gate; he has. Routed to Architect to decompose the redesign. UI/UX to re-spec the scrollbar/zoom-model visual details it previously declined, as part of that plan.
