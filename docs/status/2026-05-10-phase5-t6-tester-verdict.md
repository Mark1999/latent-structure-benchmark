# Phase 5 T6 — MDSPlot — Tester Verdict

**Date:** 2026-05-10
**Task:** Phase 5 T6 — MDSPlot headline visualization
**Coder commit:** f3b7b43
**UI/UX verdict file:** docs/status/2026-05-10-phase5-T6-uiux-verdict.md (PASS-WITH-NOTES, carry-forward F-T6-1 noted)
**Reviewer verdict file:** docs/status/2026-05-10-phase5-t6-reviewer-verdict.md (PASS)
**Tester verdict:** PASS-WITH-NOTES

---

## Test run results

### vitest (dashboard)

```
Test Files  9 passed (9)
     Tests  213 passed (213)   [was 193 before gap-fill; 20 new tests added]
  Start at  13:08:26
  Duration  5.95s
```

- T1-T5 legacy tests: 126 passed (unchanged)
- T6 Coder-written tests: 67 passed
- T6 Tester gap-fill tests: 20 passed (new, this verdict)

### ESLint

Clean. Zero warnings or errors.

### Build

```
dist/assets/index-LZU0HLdx.css   12.57 kB | gzip: 2.63 kB
dist/assets/index-Du78hSIT.js   214.20 kB | gzip: 66.96 kB
```

Bundle gzip total: ~69.6 KB. Well under 400 KB cap. T6 added 722 lines of
component + CSS; the delta from previous build is in the normal range (~5-10 KB
gzipped).

### Preview smoke

`curl http://localhost:4173/` returns valid HTML with correct `<title>` and
asset references. No server-side errors.

### Python suite

```
1258 passed, 26313 warnings in 13.99s
```

No regressions in the Python packages. All warnings are pre-existing
sklearn/numpy `RuntimeWarning` for degenerate MDS inputs (expected).

---

## Coder tests inspection (67 tests)

All 67 T6 tests were read and verified against the acceptance criteria:

| AC | Coverage | Verdict |
|----|----------|---------|
| AC 1: family=11, holidays=9 model points | `.mds-plot__point` count assertions | PASS |
| AC 2: all-deterministic synthetic fixture | 4 tests: R1-c count, no ellipses, path elements, no circles | PASS |
| AC 3: tooltip content (source assertions) | 3 source assertions: names, OCI, top-5 terms | PASS |
| AC 4: R1-b/R1-c no ellipses | 6 tests: family=11 ellipses, holidays=7, all-det=0, mixed=1, negative id checks | PASS |
| AC 5: R1-c hollow triangle 3px stroke | 5 tests: class, path elements, fill=none, stroke set, stroke-width=3 DOM | PASS |
| AC 6: WCAG AA 3px stroke | 2 tests: source `strokeWidth="3"`, DOM stroke-width=3 | PASS |
| AC 7: shape encoding (R1-a circle, R1-b dashed, R1-c triangle) | 7 tests: class counts, circle elements, dasharray, no dasharray on R1-a, no circles in R1-c | PASS |
| AC 8: CSP compliance | 4 tests: no dangerouslySetInnerHTML, no eval, no OCI sentinel text, no DETERMINISTIC user text | PASS |
| AC 9: SVG aria-label format | 8 tests: role=img, non-empty, starts with "MDS cognitive map of", contains n and domain, format regex, first sentence | PASS |
| AC 10: legend 3 marker samples | 9 tests: container, 3 items, solid circle, dashed circle, hollow triangle path, label text | PASS |
| AC 11: R1-c tooltip verbatim copy | 4 source assertions: all three verbatim fragments, no OCI sentinel in JSX | PASS |
| AC 12: R1-b tooltip verbatim copy | 5 source assertions: binding copy fragments, OCI substitution, threshold constant | PASS |
| AC 13: R1-a tooltip content | 4 source assertions: OCI label, state badge, top terms header, slice(0,5) | PASS |
| Axis labels | 2 render tests: x and y label text content | PASS |
| Forbidden vocabulary | 3 tests: worldview, cultural bias, believes | PASS |

Model count fixture data verified against `FAMILY_MODEL_IDS` (11 entries) and
`HOLIDAYS_MODELS` (9 entries) in the test file. These are synthetic test
fixtures — they do not resemble real provenance data per CLAUDE.md §9 pitfall 9.

---

## No real API calls

`grep -n "fetch(" tests` returned no hits in `mds-plot.test.tsx`. The test file
uses `readFileSync` (source assertions) and `createRoot`/`act` DOM rendering
with fixture `DomainResultPublished` objects built inline. Zero live API calls.
CLAUDE.md rule 10 satisfied.

---

## Coverage gaps identified and filled

### Gap 1: R1-a with null mds_uncertainty (defensive path)

The component guards `if (!point.ellipse) return null` at line 540 of
`MDSPlot.tsx`, but no Coder test exercised this path. An R1-a model whose
`mds_uncertainty` entry is explicitly `null` is a valid data-pipeline edge case
(e.g., bootstrap failed for one model but the domain result was still published).

**Gap-fill tests added:**
- `R1-a model with null mds_uncertainty renders without ellipse (no crash)`
- `R1-a model with null mds_uncertainty still renders its model point`

### Gap 2: Tooltip hover — mouseenter/mouseleave state

React 19's synthetic event delegation does not fire from raw DOM `dispatchEvent`
in jsdom (documented in the test file header, lines 24-28). The Coder correctly
documented this limitation and used source assertions for copy compliance.
However, no test verified the structural invariants of the hover state machine:
tooltip absent on initial render, `handleMouseLeave` clearing both state
variables, `role="tooltip"` present, `onMouseEnter`/`onMouseLeave` wired on all
three R1 state branches.

**Gap-fill tests added:**
- `tooltip container is NOT present in initial render (no hover)`
- `source guards tooltip render on tooltip !== null && hoveredPoint !== null`
- `source contains handleMouseLeave that clears both hoveredId and tooltip state`
- `tooltip div has role='tooltip'`
- `each model point group has onMouseEnter and onMouseLeave handlers wired`

### Gap 3: Model label font (12px Lato / var(--font-body))

DESIGN_SYSTEM.md §3.3 item 5 binds model labels to 12px Lato. No Coder test
verified this. The component uses `fontSize="12"` and `fontFamily="var(--font-body)"`
on all three SVG text groups (model labels, x-axis, y-axis) — both source and
DOM attributes are now tested.

**Gap-fill tests added:**
- `source specifies fontSize='12' for model labels` (source assertion)
- `source specifies fontFamily='var(--font-body)' for model labels` (source assertion)
- `rendered model label text elements have font-size='12' in DOM`
- `rendered model label text elements use --font-body CSS var for fontFamily`

### Gap 4: Ellipse parameter application

No Coder test verified that `semi_major`, `semi_minor`, and `rotation_rad` are
actually used and scaled by `svgUnitsPerDataUnit`. The component source was
correct but untested at this level of specificity.

**Gap-fill tests added:**
- `source destructures semi_major, semi_minor, rotation_rad from ellipse params`
- `source scales semi_major and semi_minor by svgUnitsPerDataUnit`
- `ellipse <path> element has a non-trivial 'd' attribute (not empty string)`
- `ellipse path uses a Bezier approximation (contains 'C' curve command)`
- `ellipse data-model-id matches the model's id for all R1-a points in family fixture`

### Gap 5: Empty top_terms defensive path

When `display.top_terms[modelId]` is `undefined` or `[]`, the tooltip must not
crash. The component uses `?? []` as a fallback and guards the terms section with
`point.topTerms.length > 0`. No Coder test exercised this path with an empty or
absent record.

**Gap-fill tests added:**
- `R1-a model with empty top_terms[] renders without crashing`
- `source guards top_terms section with topTerms.length > 0`
- `R1-a model with missing top_terms key (undefined in record) renders without crashing`
- `source uses fallback '?? []' for missing top_terms entry`

---

## Carry-forward from UI/UX PASS-WITH-NOTES

F-T6-1 (em-dash in lede string) is a data pipeline issue, not a component
issue. The MDSPlot component renders whatever `generated_lede` it receives.
No component test action required. Noted for awareness.

---

## Notes

- The Coder noted tooltip hover firing limitation in the file header (lines
  24-28). This is an accepted limitation of jsdom + React 19 event delegation.
  The gap-fill addresses it with structural state-machine assertions rather than
  synthetic event firing.
- Bundle size (66.96 KB gzipped JS, 2.63 KB CSS) is well within the 400 KB cap.
  The T6 component adds no external dependencies; hand-rolled SVG was the
  correct call per the §3.2 design system note.
- All 20 gap-fill tests pass cleanly. No regressions to existing 193 tests.

---

## Verdict

**TESTER VERDICT: PASS-WITH-NOTES**

Notes:
1. Gap-fill tests written and committed (20 tests, `test(dashboard):` commit).
   Suite now at 213 passed across 9 test files.
2. Hover tooltip interaction is verified structurally (state machine + source
   assertions) but not via synthetic event fire due to jsdom/React 19 limitation.
   This is the same limitation acknowledged by the Coder and is acceptable per
   the test file header documentation.
3. F-T6-1 carry-forward (em-dash in lede) is a data pipeline note, not a
   component failure. No action on this task.
