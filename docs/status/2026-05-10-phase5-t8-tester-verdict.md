# Phase 5 T8 — VizSwitcher Placeholder — Tester Verdict

**Date:** 2026-05-10
**Task:** Phase 5 T8 — VizSwitcher tab-bar placeholder
**Coder commit:** `774dd44`
**UI/UX PASS-WITH-NOTES:** `f73edcb`
**Reviewer PASS:** `602fde5`
**Tester verdict:** PASS-WITH-NOTES (gap fills committed)

---

## Runs performed

| Suite | Command | Result |
|---|---|---|
| Dashboard vitest (pre-gap-fill) | `cd apps/dashboard && npm run test` | 335 passed, 0 failed |
| Dashboard lint | `npm run lint` | Clean |
| Dashboard build | `npm run build` | Clean, 68.53 KB gzipped (limit: 400 KB) |
| Python pytest | `uv run pytest` | 1258 passed, 0 failed |
| Dashboard vitest (post-gap-fill) | `cd apps/dashboard && npm run test` | 345 passed, 0 failed |
| Dashboard lint (post-gap-fill) | `npm run lint` | Clean |

---

## File inspection findings

### §12.3 binding checks

| Binding | Verified | Method |
|---|---|---|
| `tabIndex={0}` on disabled tabs (NOT `-1`) | PASS | DOM test: tabIndex not -1 (lines 145–165); source assertion (line 535) |
| `aria-disabled="true"` on disabled tabs | PASS | DOM test (lines 114–133) |
| Tooltip text exact `"Coming in a future update"` | PASS | Exact-match DOM test (lines 176–196); source no-"Phase 6" assertion |
| No "Phase 6" / "Phase 5" / "coming soon" in tooltip | PASS | Source assertion (lines 531–532) |
| Active tab `aria-selected="true"`, others `"false"` | PASS | DOM tests (lines 83–110) |
| Click on active tab calls `onTabChange("mds")` | PASS | DOM test (lines 207–219) |
| Click on disabled tab does NOT call `onTabChange` | PASS | DOM tests for all 3 disabled tabs (lines 221–258) |
| ArrowLeft/ArrowRight moves focus between tabs | PASS | DOM tests (lines 317–362) |
| ArrowRight from last tab wraps to first | PASS | DOM test (lines 349–362) |
| Container `role="tablist"` | PASS | DOM test (line 262) |
| Tabs `role="tab"` | PASS | DOM test (lines 274–280) |
| Active visual indicator (class `viz-switcher__tab--active`) | PASS | DOM tests (lines 283–313) |
| Disabled visual indicator (class `viz-switcher__tab--disabled`) | PASS | DOM tests (lines 304–313) |

### N1 cascade stagger (UI/UX non-blocking note)

Confirmed: `VizSwitcher` in `App.tsx` is rendered at line 300, inside
`<div className="content-area">`, with NO surrounding
`<div className="reveal-cascade-item">` wrapper. This matches the UI/UX
PASS-WITH-NOTES N1 finding. The component does not participate in the
`reveal-cascade-item` :nth-child stagger. Deferred to T13 per the Reviewer
PASS verdict.

### No real API calls

`grep` over `viz-switcher.test.tsx` for `fetch`, `XMLHttpRequest`, `axios`,
`openai`, `anthropic`: zero matches. CLAUDE.md §6 rule 10 satisfied.

---

## Coverage gaps identified and filled

### Gap G1 — Space on active tab (HIGH VALUE)

**Finding:** The spec comment at `viz-switcher.test.tsx` line 20 states
"Enter / Space on active tab calls onTabChange". The existing tests covered:
- Enter on active tab (PASS)
- Space on disabled tab (PASS)

Missing: Space on active tab. The `handleKeyDown` implementation in
`VizSwitcher.tsx` handles both `Enter` and `" "` identically via `||`, so
the implementation was correct — the test was absent.

**Gap fill:** Added `describe("VizSwitcher — Gap G1: Space on active tab")` with
one test. Result: PASS.

### Gap G2 — resolveFragmentOnMount with real hash values (HIGH VALUE)

**Finding:** The existing test in `app-state.test.ts` (node environment) calls
`resolveFragmentOnMount()` with `window` absent — the `try/catch` swallows the
`ReferenceError` and always returns `"mds"`. The three code paths in the
function were never exercised:
1. `raw === "mds" || raw === ""` → return "mds" silently
2. `DISABLED_FRAGMENTS.has(raw)` → `console.warn` + return "mds"
3. Fallthrough → return "mds"

The jsdom environment in `viz-switcher.test.tsx` has `window.location`
available.

**Gap fill:** Added `describe("VizSwitcher — Gap G2: resolveFragmentOnMount")` with
8 tests covering:
- Empty hash returns "mds"
- "#mds" hash returns "mds"
- "#freelist", "#similarity", "#drift" each return "mds"
- "#freelist" emits `console.warn` containing "freelist"
- "#mds" does NOT emit `console.warn`
- Empty hash does NOT emit `console.warn`

All 8 pass.

### Gap G3 — ArrowLeft wrap-around from first to last tab (MEDIUM VALUE)

**Finding:** The existing keyboard tests covered:
- ArrowRight from tab 0 → tab 1 (line 317)
- ArrowLeft from tab 1 → tab 0 (line 332)
- ArrowRight from tab 3 (last) → tab 0 (line 349) — wrap test

Missing: ArrowLeft from tab 0 (first) → tab 3 (last). The wrap arithmetic
`(currentIndex + direction + total) % total` handles this symmetrically, but
it was untested.

**Gap fill:** Added `describe("VizSwitcher — Gap G3: ArrowLeft wrap-around")` with
one test. Result: PASS.

### Gap G4 — URL fragment update on click (NOT filled — covered by source assertion)

**Finding:** `handleVizTabChange` in `App.tsx` calls
`window.history.replaceState(null, "", "#mds")`. This is App.tsx-level wiring,
not a VizSwitcher responsibility. The existing `app-state.test.ts` T8
additions include a source assertion confirming `window.history.replaceState`
is present at `App.tsx` line 129. A DOM integration test (render App.tsx,
click VizSwitcher, check `window.location.hash`) would require mocking the
full App.tsx state machine and is disproportionate for this component.
No gap fill written.

### Focus-visible outline (NOT filled — untestable at unit level)

**Finding:** CSS `:focus-visible` pseudo-class behavior is not exercisable via
jsdom's `dispatchEvent`. The `app.css` at line 877 defines
`.viz-switcher__tab:focus-visible { outline: ... }`. This is verifiable only
through visual regression or a browser-based test. No unit test is appropriate.
No gap fill written.

---

## Tests written (gap fills)

| File | Function/describe | What it covers |
|---|---|---|
| `apps/dashboard/src/__tests__/viz-switcher.test.tsx` | `VizSwitcher — Gap G1: Space on active tab` > `Space on MDS Plot tab calls onTabChange('mds')` | Space key activates the active tab — the symmetric case of Enter that was missing |
| `apps/dashboard/src/__tests__/viz-switcher.test.tsx` | `VizSwitcher — Gap G2: resolveFragmentOnMount` > `returns 'mds' when hash is empty` | Empty hash path in resolveFragmentOnMount |
| `apps/dashboard/src/__tests__/viz-switcher.test.tsx` | `VizSwitcher — Gap G2: resolveFragmentOnMount` > `returns 'mds' when hash is '#mds'` | Named active hash path |
| `apps/dashboard/src/__tests__/viz-switcher.test.tsx` | `VizSwitcher — Gap G2: resolveFragmentOnMount` > `returns 'mds' when hash is '#freelist'` | DISABLED_FRAGMENTS fallback path |
| `apps/dashboard/src/__tests__/viz-switcher.test.tsx` | `VizSwitcher — Gap G2: resolveFragmentOnMount` > `returns 'mds' when hash is '#similarity'` | DISABLED_FRAGMENTS fallback path |
| `apps/dashboard/src/__tests__/viz-switcher.test.tsx` | `VizSwitcher — Gap G2: resolveFragmentOnMount` > `returns 'mds' when hash is '#drift'` | DISABLED_FRAGMENTS fallback path |
| `apps/dashboard/src/__tests__/viz-switcher.test.tsx` | `VizSwitcher — Gap G2: resolveFragmentOnMount` > `emits console.warn for DISABLED_FRAGMENTS hash (#freelist)` | Warning emission verified |
| `apps/dashboard/src/__tests__/viz-switcher.test.tsx` | `VizSwitcher — Gap G2: resolveFragmentOnMount` > `does NOT emit console.warn for #mds` | No spurious warning for valid hash |
| `apps/dashboard/src/__tests__/viz-switcher.test.tsx` | `VizSwitcher — Gap G2: resolveFragmentOnMount` > `does NOT emit console.warn for empty hash` | No spurious warning for no hash |
| `apps/dashboard/src/__tests__/viz-switcher.test.tsx` | `VizSwitcher — Gap G3: ArrowLeft wrap-around` > `ArrowLeft from MDS Plot (first tab) wraps to Drift (last tab)` | Symmetric wrap-around to ArrowRight test |

---

## Final test counts

- Dashboard: **345 tests, 0 failed** (was 335 before gap fills; +10 gap fills)
- Python: **1258 tests, 0 failed** (unchanged)
- Lint: clean
- Build: clean, 68.53 KB gzipped

---

## Notes

- The two Reviewer non-blocking notes (N1 cascade stagger, N2 stale comment)
  are confirmed deferred to T13. N1 is verified above. N2 is a comment in
  `VizSwitcher.tsx` and not tested (stale comments are documentation, not
  behavior).
- `resolveFragmentOnMount` is exported from `VizSwitcher.tsx` with an
  intentional `eslint-disable react-refresh/only-export-components` comment.
  The export was added to support direct unit testing — this is the correct
  pattern per the project test philosophy.
