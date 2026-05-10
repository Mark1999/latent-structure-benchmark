# Phase 5 T9 — Tester Verdict

**Task:** T9 — DataExplorer composition refactor (state moved from App.tsx)
**Coder commit:** 77eec55
**UI/UX PASS:** ed2f08d
**Reviewer PASS:** b2fc8f7
**Date:** 2026-05-10
**Tester:** Claude Sonnet (LSB Tester agent)

---

## Verdict: PASS-WITH-NOTES

All required tests pass. One gap-fill test added (see Notes).

---

## Test run results

### vitest (apps/dashboard)

| Run | Tests | Result |
|-----|-------|--------|
| Before gap fill | 414 passed (13 files) | PASS |
| After gap fill | 415 passed (13 files) | PASS |

### pytest (Python suite)

| Run | Tests | Result |
|-----|-------|--------|
| Full suite | 1258 passed | PASS |

### Lint

`npm run lint` — clean (no output = no errors).

### Build

`npm run build` — clean.
Bundle size: **68.53 kB gzipped** (T9 budget: 350 kB gzipped — well within budget).

---

## Inspection findings

### Confirmed coverage (task brief checklist)

1. **DataExplorer renders all four sub-components** — 6 tests in AC 1 block. DOM assertions on `.viz-switcher`, `.mds-plot__svg`, `.model-selector`, `.mds-plot__legend`. Pass.

2. **Initial selectedModels = first-6 by §12.4 sorted slice** — 6 tests in AC 3 block including lexicographic-first-6 assertion (`data-model-id` on rendered points), source-text assertion for `Object.keys(rawCoords).sort().slice(0, 6)`, and small-corpus edge case (3 models: all 3 selected). Pass.

3. **modelColors computed correctly** — 8 tests in AC 4 block. Functional algorithm test for 3-model and 11-model cases. Source assertions for `MODEL_PALETTE_SLOTS` presence in DataExplorer and absence from App.tsx. `#9a7d0a` slot 11 v0.4.1 correction verified. Pass.

4. **selectedModels changes propagate to MDSPlot** — 5 tests in AC 5 block. "Clear all" and "Select all" click interactions verified via DOM point counts. Checkbox deselect interaction tested. Source assertions for prop wiring. Pass.

5. **activeVizTab default "mds"** — 4 tests in AC 6 block. DOM `.viz-switcher__tab--active` assertion, source assertions for `resolveFragmentOnMount`. Pass.

6. **Layout structure (CSS grid)** — 7 tests. `.data-explorer`, `.explorer-layout`, `.explorer-layout__viz`, `.explorer-layout__selector` all verified in DOM. VizSwitcher source-position-before-explorer-layout test. MDSPlot inside `.explorer-layout__viz` and ModelSelector inside `.explorer-layout__selector` verified in DOM. Pass.

7. **Domain switch resets selectedModels** — 3 tests. Source assertion for `domain_slug` useEffect dependency. Interactive re-render test (select-all then swap fixture, confirm 4 points from new 4-model domain). Pass.

8. **App.tsx palette-ownership migration regression guard** — 13 tests in palette-ownership migration block. Confirms App.tsx no longer holds `MODEL_PALETTE_SLOTS`, `modelColors = useMemo`, `setSelectedModels`, `setActiveVizTab`, `handleVizTabChange`, and direct imports of MDSPlot/ModelSelector/VizSwitcher. Pass.

9. **VizSwitcher at top of DataExplorer (§3.1 layout order)** — Source-position test: `DE_SRC.indexOf("VizSwitcher") < DE_SRC.indexOf("explorer-layout")`. Pass.

10. **ModelSelector receives modelColors prop (not deriving its own)** — Source assertion: `DE_SRC` contains `modelColors={modelColors}` in ModelSelector JSX. Pass.

11. **Embed mode rendering DataExplorer** — Covered in `app-state.test.ts` (T9-updated block): `embed-root` block contains `DataExplorer` and does not contain `<DomainPicker`, `<KeyFinding`, `<Header`, `<Footer`, `<ArticleHeader`. Pass.

12. **No real fetch/API calls in data-explorer.test.tsx** — Grep confirmed: no `fetch`, `XMLHttpRequest`, `axios`, `got`, or live URL patterns. All API calls in `app-state.test.ts` are mocked via `vi.mock("../api/client")`. Pass.

13. **Forbidden vocabulary** — 4 forEach-generated tests cover `worldview`, `cultural bias`, `believes`, `thinks` against DataExplorer.tsx source. Pass.

---

## Notes (gap fill)

### Gap filled: modulo wrap-around regression guard for >11 models

**Status:** Added 1 new test.

The existing test "§12.4 algorithm: first 11 family models by sort get slots 1–11 (no wrapping)" verified only the no-wrap case. `DataExplorer.tsx` uses `i % MODEL_PALETTE_SLOTS.length` in the `modelColors` useMemo, which means a 12th model (index 11) wraps to `MODEL_PALETTE_SLOTS[0]` (`#3360a9`). No test verified this wrap behavior or that no `undefined` slot assignment occurs.

Test added to `apps/dashboard/src/__tests__/data-explorer.test.tsx` in the AC 4 block:
- Uses a synthetic 12-model fixture (`a-model` through `l-model`)
- Verifies `l-model` (12th) receives `MODEL_PALETTE_SLOTS[11 % 11]` = slot 0 (`#3360a9`)
- Verifies no slot assignment is `undefined` (all 12 entries are valid hex strings)
- Test passes with the current DataExplorer.tsx implementation

This guards against a future regression where the modulo is removed or the array length shrinks, which would produce `undefined` color values and break all 12+ model rendering.

### Gaps not actioned (carried forward)

- **T9 test count:** The brief states "63 new data-explorer tests." Actual count: 63 test instances (60 `it()` definitions + 4 from `FORBIDDEN.forEach` = the 60th `it()` is inside the loop producing 4 instances). After gap fill: 64 instances. The count difference from the brief was measurement artifact (forEach instances counted or not). No action required.

---

## Files written

- `/opt/lsb-agent/docs/status/2026-05-10-phase5-t9-tester-verdict.md` (this file)

## Files modified

- `/opt/lsb-agent/apps/dashboard/src/__tests__/data-explorer.test.tsx` — 1 test added (12-model wrap-around regression guard, AC 4 block)
