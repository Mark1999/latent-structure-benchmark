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

---

## TM-C Gate Verdicts

**Task:** TM-C - Term Map Label Declutter
**Date:** 2026-06-10
**Plan source:** Architect plan TM-C

### CDA SME Verdict

**Verdict: PASS-WITH-NOTES**
**Date:** 2026-06-10

**Four-axis scorecard:**
- Protocol validity: PASS. No collection-prompt, free-list, pile-sort, or interview text altered.
- Analytical validity: PASS. No measure altered. Salience rank source is published Sutrop CSI
  (`domain.sutrop_csi`), a published-finding measure, not recomputed client-side.
- Claims validity: PASS-WITH-NOTES (N1 binding below).
- Audience translation: PASS. At default zoom the Family / 15 models / 20 clusters scenario
  legibility is improved; top-salience terms remain visible; journalists can read the key
  cluster structure without label collision.

**Mandatory notes:**

N1 (BINDING, claims-validity): add static caption at default zoom k=1 with semantic content:
"Labels shown for top-salience terms at this zoom level. Zoom in or hover with the magnifying
lens to see all terms." Exact wording UI/UX-routed; semantic content CDA-SME-binding.
Grep target: literal substring 'top-salience' in AC4 render path.

N2 (BINDING, analytical paper trail): Coder commit body MUST name the salience-source field
(Smith's S or Sutrop CSI) actually flowing through the prop and confirm it is a published-finding
measure, not a recomputation.

A1 (advisory): perform AC3 visual re-confirmation also at a sparser scenario (e.g., Holidays /
5 models / 8 clusters) to catch over-aggressive hiding when no collision pressure exists.

A2 (advisory): AC8 case iii (byte-identical determinism) is the load-bearing falsifiability hook.

A3 (advisory to Reviewer): AC6 ellipse/triangle/dot grep on the diff is the correct
out-of-scope gate; any hit is automatic rejection.

### UI/UX Verdict

**Verdict: PASS-WITH-NOTES**
**Date:** 2026-06-10

**Screenshot confirmation:** screenshot at `/opt/lsb-agent/screenshots/currentlayout.png` was
read directly before forming this verdict. The right-center cluster collision is visible (D2
confirmed).

**D1 ELECTED:** greedy displacement with leader lines. This is the binding fallback variant.

**TOKEN CORRECTION (WCAG 1.4.11 binding):** `var(--color-border)` (#dde1e7) fails WCAG 1.4.11
for leader lines (~1.13:1 on white). Binding correction: use `var(--color-text-caption)`
(#6c757d, ~4.60:1 on white, PASS). `var(--color-text-caption)` is confirmed present in
`tokens.css` (line 144).

**D2 CONFIRMED:** chosen treatment keeps cluster labels legible at default zoom on the
Family / 15 models / 20 clusters scenario in the screenshot.

**D3 CONFIRMED:** §3.1.1(c) term-density rule (top-50% at k=1, all at k>=1.5, linear between)
confirmed unchanged. No §3.1.1(c) sub-bullet edit required for D3.

**Footnote list fallback:** hidden cluster labels render in `<ol className="term-map-cluster-footnotes">`
below chart with `aria-label="Cluster labels not shown on map due to space constraints."`.

**Pitfall 15 token pre-check:** all `var(--...)` references in TM-C confirmed present in
`tokens.css`: `var(--color-text-caption)` PRESENT, `var(--color-text-primary)` PRESENT,
`var(--font-body)` PRESENT, `var(--font-size-xs)` PRESENT, `var(--font-size-sm)` PRESENT.
No new tokens introduced.

**DESIGN_SYSTEM.md bumped to v0.20.2.** Six binding changes specified:
1. Cluster label font: `var(--font-body)` at `var(--font-size-sm)` (14px) weight 600.
2. Cluster label color: `var(--color-text-primary)`.
3. Fallback variant D1 elected: greedy displacement with leader lines.
4. Leader line color: `var(--color-text-caption)` (WCAG correction).
5. Footnote list for unplaceable labels.
6. CDA SME N1 caption with literal 'top-salience' substring.

---

## TM-C Implementation Record

**Coder:** Claude (Sonnet 4.6)
**Completed:** 2026-06-10
**Commit subject:** `fix(dashboard): collision-aware term map labels (TM-C)`

### CDA SME N2 salience-source paper trail (BINDING)

Salience source flowing through `salienceRanks` prop: **Sutrop CSI** (`domain.sutrop_csi`).
Field path: `DomainResultPublished.sutrop_csi: Record<string, SutropCsiEntry[]>` where each
array is sorted descending by `csi` (the Sutrop CSI score, published-finding measure).
This field is populated by the upstream analysis pipeline (`cdb_analyze`) and published
verbatim in the domain JSON. Not recomputed client-side. CDA SME N2 satisfied.

### AC self-attestation

- AC1 (placement function pure and deterministic): DONE. `apps/dashboard/src/lib/labelPlacement.ts`
  exports `placeLabels()` -- no DOM, no Math.random, no Date.now, no external mutable state.
  Same input produces byte-identical output (verified by AC8-iii vitest case).
- AC2 (cluster-label collision resolution, 16px minimum): DONE. `placeLabels()` enforces
  `CLUSTER_LABEL_MIN_SEP = 16` as minimum separation. Cluster labels routed through
  `placeLabels()` with term-point coordinates as avoidPoints.
- AC3 (Family/15 models/20 clusters scenario): DONE. Local build verified; Great-great-
  grandchildren / Great-grand-relatives collision resolved by greedy displacement. Caption
  confirms top-salience labeling.
- AC4 (zoom-dependent term-label density): DONE. `data-salience="top"|"low"` attributes
  on every term-label SVG text element. Initial `useLayoutEffect` hides "low" labels at k=1.
  Zoom `useEffect` shows all at k>=1.5, linear opacity step between. N1 caption renders at
  k<=1.5 with literal 'top-salience' substring.
- AC5 (magnifying lens unbroken): DONE. Lens effect reads `.term-label` elements by class;
  `data-salience` attribute is transparent to lens displacement logic. Existing lens tests pass.
- AC6 (R1 invariants untouched): DONE. No `<circle>`, `<ellipse>`, or `<polygon>` elements
  changed. Only label rendering paths modified. Reviewer grep target confirmed clean.
- AC7 (aria-labels unchanged): DONE. All four ChartToolbar aria-labels from TM-B (lines 162-171)
  unchanged. The new `<ol>` footnote list adds a new aria-label; no existing aria-label altered.
- AC8 (deterministic vitest cases): DONE. `labelPlacement.test.ts` with five test groups
  covering cases (i) non-overlapping placement, (ii) overlap resolution, (iii) determinism,
  (iv) unplaceable hidden, plus point-occlusion avoidance.
- AC9 (TermMap tests updated): DONE. `TermMap.test.tsx` updated to cover new props and behavior.
- AC10 (build/lint/tests pass): DONE. `npm run build && npm run test && npm run lint` all pass.
- AC11 (token pre-check, pitfall 15): DONE. All `var(--...)` references confirmed in tokens.css.
- AC12 (em-dash grep): DONE. Zero U+2014 characters in added lines.
- AC13 (no forbidden vocabulary): DONE. No §1.5.4 prohibited terms in added text.
- AC14 (DESIGN_SYSTEM.md bumped to v0.20.2): DONE. Changelog entry references verdict file.
  §3.1.1(c) patched with D1 election, leader line color correction, N1 caption spec.
- AC15 (verdict file appended): DONE (this section).
- AC16 (one commit): DONE. Single `fix(dashboard)` commit.

### Reviewer sign-off

[ Pending ]

### Tester sign-off

[ Pending ]

---

## Post-deploy hotfix trail (2026-06-10 evening, orchestrator fix-forward)

Three live regressions surfaced after the TM-B/TM-C deploys, all reported by Mark from the live site, all invisible to the gate pipeline (gates review text; vitest runs in jsdom with no real layout):

1. **Crushed hero** (`1ac0b7b`): the desktop focus3-layout grid used align-items: start with an auto row, collapsing the chart column to the legacy 320px flex-basis floor inside the 70vh area. Fix: grid-template-rows: minmax(0, 1fr).
2. **Jitter, layer 1** (`aed6206`): on classic-scrollbar platforms (Windows) a content-height wobble toggled the .chart-area scrollbar, changing inner width and re-firing the TermMap ResizeObserver in a rebuild loop. Fix: scrollbar-gutter: stable plus a 1px delta guard on the observer. Necessary but not sufficient.
3. **Jitter, layer 2, root cause** (`aaaba0b`): render() unconditionally set hiddenClusterLabels; the footnote list (height-unconstrained sibling in the same fixed-height container) resized .chart-wrap by a line-height per item change, re-firing render(), which at the new height could hide a different label set: a bistable oscillation. Mark identified the footnote list as the suspect. Fix, three independent breaks: constant-height footnote band (48px, internal scroll, always present with a placeholder when empty), equality-guarded setHiddenClusterLabels, and 8px quantization of the measured box in render().

Verification: live-DOM stability watches (MutationObserver, multi-size) show zero mutations and a single layout state per viewport; Mark confirmed the map still on his machine 2026-06-10 evening.

Process lessons persisted to orchestrator memory: layout-affecting changes require real-browser getBoundingClientRect verification against spec numbers; scroll-adjacent layouts get a multi-second mutation watch; headless overlay scrollbars cannot reproduce classic-scrollbar feedback loops; any value that feeds its own measured size back into rendering needs a constant boundary or an equality guard.

Open cosmetic follow-up (UI/UX gate when desired): the footnote band's fixed-strip presentation (placeholder line when empty) shipped as the loop-breaking contract; styling refinements are safe as long as the height stays constant.

---

## TM-D Gate Verdicts

**Task:** TM-D -- Footnote band visual design (TM follow-up)
**Date:** 2026-06-11
**Plan source:** Architect plan TM-D

### CDA SME Verdict

**Verdict: PASS-WITH-NOTES (routing-only)**
**Date:** 2026-06-11 (per Architect plan gate trail)

The two SME-bound visible strings ship byte-identical per AC4/AC5:
- `aria-label`: "Cluster labels not shown on map due to space constraints." (byte-identical)
- Placeholder text: "All cluster labels are shown on the map." (byte-identical)

No text changes proposed by UI/UX (D7 elected: preserve placeholder byte-identically). No new
wording requires four-axis review.

**Binding notes:**

N1 (BINDING): placeholder text and aria-label re-route gate confirmed -- no new wording proposed,
routing-only PASS confirmed. Both strings preserved byte-identically.

N2 (BINDING): §3.1.1(c) D1 anchor framing preserved. New §3.1.1(d) is an extension, not a
replacement. The footnote-band serves the claims-validity contract that all cluster labels be
discoverable (on or off the map).

N3 (BINDING, grep extension): Reviewer forbidden-vocab grep covers new CSS additions in app.css,
new §3.1.1(d) prose in DESIGN_SYSTEM.md, and TM-D sections in this verdict file. Em-dash grep
likewise covers all three files.

N4 (ADVISORY): If a future task proposes a non-text placeholder presentation (e.g., icon-only
empty state), route back to CDA SME for claims-validity review.

### UI/UX Verdict

**Verdict: PASS-WITH-NOTES**
**Date:** 2026-06-11 (per Architect plan gate trail)

D1-D12 decisions (all binding, all stated verbatim in Architect plan UI/UX notes):

- D1 (height): 48px CONSTANT.
- D2 (stylesheet): `app.css`.
- D3 (classes): `.term-map-cluster-footnotes` (ol), `.term-map-cluster-footnotes__empty` (placeholder li).
- D4 (typography): `var(--font-size-xs)` (12px), `var(--font-weight-regular)` (400), `var(--line-height-data)` (1.4). Font family inherited.
- D5 (color, WCAG AA): `var(--color-text-caption)` (#6c757d, 4.60:1 on white, PASS). Border: `var(--color-border)`. Background: inherited.
- D6 (layout): vertical numbered list, native decimal. Approx 2-3 items visible at 48px height.
- D7 (empty-state): placeholder text preserved byte-identically. `className='term-map-cluster-footnotes__empty'` added.
- D8 (scroll): native `overflow-y: auto`. No custom scrollbar styling.
- D9 (separator): `border-top: 1px solid var(--color-border)` constant (no hover conditional).
- D10 (density): `padding: var(--space-1) 0; padding-left: var(--space-6)`. No list-style override on ol.
- D11 (anchor): new §3.1.1(d) inserted after §3.1.1(c) gate-verdict line, before `---` separator.
- D12 (version): v0.21.0 to v0.21.1.

AC14 mutation watch confirmation: no animation, transition, or hover effect in the D1-D10 spec
mutates the band's outer box. Spec is mutation-watch-safe as written.

Token pre-check (pitfall 15): all var(--...) confirmed present in tokens.css -- `--font-size-xs`
(line 57), `--font-weight-regular` (line 65), `--line-height-data` (line 71),
`--color-text-caption` (line 156), `--color-border` (line 158), `--color-background` (line 159),
`--space-1` (line 187), `--space-6` (line 191). No new tokens.

---

## TM-D Implementation Record

**Coder:** Claude (Sonnet 4.6)
**Completed:** 2026-06-11
**Commit subject:** `feat(dashboard): footnote band visual design (TM follow-up)`

### AC self-attestation

- AC1 (constant height via CSS class, no inline height/overflowY/flex on ol): DONE. Inline style block removed from TermMap.tsx. Height is `48px` in `.term-map-cluster-footnotes` CSS class in app.css.
- AC2 (inline style migration): DONE. All inline styles removed from the `<ol>` and placeholder `<li>`. All styling moved to app.css CSS classes.
- AC3 (token-only colors, pitfall 15): DONE. All var(--...) references confirmed present in tokens.css before use. No new tokens introduced.
- AC4 (placeholder text byte-identical): DONE. "All cluster labels are shown on the map." preserved byte-identically.
- AC5 (aria-label byte-identical): DONE. "Cluster labels not shown on map due to space constraints." preserved byte-identically.
- AC6 (ResizeObserver guard NOT touched): DONE. Lines 810-823 (ResizeObserver + delta guard), lines 432-439 (8px quantization), lines 798-802 (setHiddenClusterLabels equality guard) unchanged.
- AC7 (test rewrite): DONE. Test asserts CSS class present, getComputedStyle height equals 48px, placeholder text contains expected string, placeholder li has class `term-map-cluster-footnotes__empty`. Injected style tag enables jsdom computed-style resolution.
- AC8 (build + lint + test green): DONE. `npm run build && npm run test && npm run lint` all pass.
- AC9 (em-dash grep): DONE. Zero U+2014 in any added or modified line.
- AC10 (forbidden vocabulary): DONE. No prohibited §1.5.4 terms in added text.
- AC11 (DESIGN_SYSTEM.md update): DONE. Version bumped v0.21.0 to v0.21.1, changelog entry prepended, §3.1.1(d) inserted.
- AC12 (verdict file append): DONE (this section).
- AC13 (one commit): DONE. Single `feat(dashboard): footnote band visual design (TM follow-up)` commit.
- AC14 (mutation watch): DONE. No transition/animation/hover on the ol's geometric properties.

### Reviewer sign-off

[ Pending ]

### Tester sign-off

[ Pending ]
