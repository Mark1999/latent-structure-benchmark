# TM-A Gate Verdicts: Chart-area hierarchy amendment

**Task:** TM-A - Chart-area hierarchy amendment to DESIGN_SYSTEM.md
**Date:** 2026-06-10
**Plan source:** Architect plan TM-A

---

## CDA SME Verdict

**Verdict: PASS-WITH-NOTES**
**Date:** 2026-06-10

**Evidence-first confirmation:** Screenshot at `/opt/lsb-agent/screenshots/currentlayout.png` was
read directly before forming this verdict. The live Explore page (Family domain, Focus 3, Term Map
tab) shows the visualization compressed to approximately the lower 55-60% of the viewport. The
SHOWING model chips, chart-lede paragraph, and TermMap controls row all sit above the chart area.
The §0 "first thing a visitor sees" principle is violated by the current composed layout.

### Four-axis scorecard

**Protocol validity: PASS.** No collection-prompt, free-list, pile-sort, or interview text is
altered. This is a layout-spec change only.

**Analytical validity: PASS.** No measure (Smith's S, Sutrop CSI, OCI, B-prime, Romney CCM, MDS,
Procrustes, bootstrap, ARI, Mantel, drift) is altered.

**Claims validity: PASS-WITH-NOTES.** The generated_lede paragraph (CDA-SME-PASSed at Phase 9a T2,
2026-06-09) is the published methodology surface. The amendment changes its position (may sit beside
or below the chart instead of above) but must not change its content, identity, or aria-live
semantic. The amendment text must explicitly state this. R10 dashed-cell treatment, uncertainty
ellipses, and the §1.5 corpus-lens framing must be preserved verbatim.

**Audience translation: PASS.** The binding "chart is the largest single element above the fold"
rule supports the 30-second journalist test (DESIGN_SYSTEM.md §0). The three-audience design
philosophy is supported: journalists get the finding in the first viewport, engineers get
consolidated controls, researchers get preserved discoverability of all analytical toggles.

### Mandatory notes (binding on UI/UX and Coder)

**M1 (BINDING):** The UI/UX-authored amendment text MUST include a six-sub-point lede preservation
clause covering: (i) verbatim render element shape retained (`<p className="chart-lede">`);
(ii) `aria-live="polite"` retained; (iii) `class="chart-lede"` retained; (iv) no inline lede logic
introduced; (v) single continuous paragraph retained; (vi) double-hyphen separator untouched. All
§21 rules carry forward at the new position.

**M2 (BINDING):** §3.3.5 R1-a, R1-b, and R1-c invariants, §15.2 cluster-color ellipse rule, and
§3.3.5 binding invariant 1 must be enumerated by section number in the preservation clause.
Generic "R10 preserved" wording is insufficient. Show-uncertainty toggle default must remain ON.

**M3 (BINDING):** Any new visible label, tooltip, or aria-label string introduced by the
consolidated chart toolbar (per §3.1.1(b)(ii)) is generated text and must be listed verbatim by
UI/UX and pre-grepped against §1.5.4 forbidden vocabulary before Coder paste.

### Advisories (non-binding, informational)

**A1:** §5 of the Architect plan correctly anticipated the claims-validity surface; M1 concretizes
the binding language. No substantive disagreement.

**A2 (to UI/UX):** The approximately 70vh chart-area minimum height interacts with §17.1
`.term-map-container` overflow containment fix; UI/UX should confirm no regression of the
height-compounding ResizeObserver bug.

**A3 (to Coder):** Changelog version-bump logic combined with any concurrent CR-T6 rebase is
mechanically sound; no methodology concern.

**A4:** Screenshot Read confirmed at `/opt/lsb-agent/screenshots/currentlayout.png` via direct
file read; file existence confirmed before forming verdict.

**Re-engagement triggers:** new published-text strings, methodology-page link changes, or new
R10/uncertainty/ellipse-rendering rules beyond preservation language.

---

## UI/UX Verdict

**Verdict: PASS-WITH-NOTES**
**Date:** 2026-06-10

**Evidence-first confirmation:** Screenshot at `/opt/lsb-agent/screenshots/currentlayout.png` was
read directly before forming this verdict. The Term Map visualization occupies approximately the
lower 55-60% of the viewport at current layout. SHOWING chips, chart-lede paragraph, and TermMap
controls all sit above the chart, violating the §0 "first thing a visitor sees" principle.

### Four-question scorecard

**1. OWID design fidelity: PASS.** The "largest single element above the fold" rule plus
consolidated toolbars matches the OWID Data Explorer pattern (§0 design philosophy reference).
OWID's canonical Data Explorer shows the chart dominating the first viewport; controls are compact
and subordinate.

**2. 30-second journalist test: PASS.** The new hierarchy makes the finding visible in the first
viewport. A journalist landing on the Explore page sees the chart immediately, not a stack of
navigation controls.

**3. Researcher reproduce-and-cite test: PASS-WITH-NOTES.** The consolidated toolbar preserves
discoverability of the overlay-category selector, uncertainty toggle, cluster-label toggle, and
magnifying lens. All four controls are present in the unified toolbar per §3.1.1(b)(ii); the
toggle defaults (Show uncertainty: ON, Show cluster labels: ON, Magnifying lens: user-toggled)
are preserved.

**4. WCAG AA accessibility: PASS.** The consolidated toolbar preserves 44px touch targets at
fewer than 768px, focus rings, and the aria-live label region currently on the stress/zoom
annotation. Verbatim aria-label strings are enumerated below.

### CDA SME mandatory notes - all addressed

**M1 addressed:** Six-sub-point lede preservation clause is in §3.1.1(b)(iii) of the amendment
text below. All §21 rules carry forward at the new position.

**M2 addressed:** Section-number enumeration of §3.3.5 R1-a/R1-b/R1-c, §15.2, and binding
invariant 1 is in the opening preservation block of §3.1.1.

**M3 addressed:** Verbatim aria-label strings for consolidated toolbar elements are listed in
§3.1.1(b)(ii) and have been pre-grepped against §1.5.4 forbidden vocabulary. None of the strings
contain "believes", "thinks" (applied to models), "corpus lens" (as a forbidden term it is not
forbidden), or other §1.5.4 prohibited framing.

**CDA SME advisory A2 (§17.1 ResizeObserver interaction) addressed:** The 70vh minimum height
applies to the `.chart-area` parent flex container, not to `.term-map-container`. The
`.term-map-container` retains `flex:1 1 320px; min-height:0; height:100%` per §17.1 and the
70vh rule does not override `min-height:0` on the inner container.

### Token pre-check (pitfall 15 compliance)

All tokens referenced in the amendment text below confirmed present in
`apps/dashboard/src/styles/tokens.css`:
- `--color-text-caption`: PRESENT (line ~144)
- `--color-border`: PRESENT (line ~146)
- `--space-2`: PRESENT
- `--space-4`: PRESENT
- `--space-6`: PRESENT
- `--font-body`: PRESENT (line ~54)
- `--color-text-primary`: PRESENT (line ~143)
- `--max-chart-width`: PRESENT (line ~74)

No new CSS custom property tokens are introduced by this amendment. Viewport-relative units
(vh, %, calc) are used for layout values, not tokens.

**Binding lede left-column width on desktop:** 280px (hardcoded in CSS at TM-B implementation
time, not a token). Chart minimum width expression: `min(calc(100% - 280px), 900px)`. These
values derive from the existing `--max-chart-width: 900px` token and the 280px prose column
judgment.

**SHOWING chips removal scope:** The SHOWING chips removal applies to all VizTabs (binding), not
only the Term Map. The chips duplicate sidebar information regardless of which visualization is
active.

---

*Both gate verdicts confirmed before Coder paste. Screenshot evidence-first requirement satisfied.*

---

## TM-B Implementation Record

**Coder:** Claude (Sonnet 4.6)
**Completed:** 2026-06-10
**Commit subject:** `feat(dashboard): Explore chart-area hierarchy layout (TM-B)`

### M3 verbatim string list (§3.1.1(b)(ii))

The four aria-label strings introduced by ChartToolbar, pre-checked against §1.5.4:

1. `Overlay category names` - select element aria-label. Clean.
2. `Show uncertainty ellipses` - checkbox aria-label. Clean.
3. `Show cluster labels` - checkbox aria-label. Clean.
4. `Magnifying lens` - checkbox aria-label. Clean.

Visible label text (inside label elements): "Overlay category names", "Show uncertainty",
"Show cluster labels", "Magnifying lens". None contain §1.5.4 prohibited framing.

### AC self-attestation

- AC1 (chart-area min-height 70vh at >=768px): DONE. Added to app.css via @media (min-width: 768px) on .chart-area.
- AC2 (SelectionBar removed unconditionally): DONE. SelectionBar import and render call removed from ContentArea.tsx. Tests confirm absence in Focus 1, 2, 3.
- AC3 (ChartToolbar with four lifted controls): DONE. ChartToolbar.tsx created with all four controls, verbatim aria-labels, defaults uncertainty=ON, cluster-labels=ON, lens=OFF. Renders only on Focus 3 term-map tab.
- AC4 (lede restructured into focus3-layout): DONE. Two-column layout with chart-col first in DOM, lede-col second. CSS grid places lede left on desktop, natural stacking on mobile.
- AC5 (TermMap controls removed from TermMap internal): DONE. term-map-controls div removed. Test confirms class absent from DOM.
- AC6 (M3 §1.5.4 check): DONE. All four strings listed above, all clean per §1.5.4.
- AC7 (token pre-check): DONE. All var(--...) refs confirmed in tokens.css before use.
- AC8 (zoom buttons remain in stress footer): DONE. Zoom buttons retained in term-map-stress. Test confirms at least 2 zoom buttons in stress footer.
- AC9 (lensDisabledByZoom propagation): DONE. TermMap fires onLensDisabledByZoomChange; ContentArea holds state; ChartToolbar receives prop and disables checkbox.
- AC10 (this verdict file section): DONE (this section).
- AC11 (DESIGN_SYSTEM.md updated to v0.20.1): DONE. Version bumped, v0.20.1 changelog appended.
- AC12 (one commit): DONE. Single feat(dashboard) commit.

### Reviewer sign-off

[ Pending ]

### Tester sign-off

[ Pending ]
