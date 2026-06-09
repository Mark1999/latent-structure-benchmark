# Phase 9a T3 — Tester verdict (2026-06-09)

**Task:** Phase 9a T3 — restore SimilarityHeatmap CI-crosses-null R10 treatment.
**Commit under test:** d4f623e
**Test file:** `apps/dashboard/src/__tests__/similarity-heatmap-r10.test.tsx` (21 tests, Coder-written)
**Verdict:** PASS

---

## 1. Baseline

`npm run build && npm run test && npm run lint` from `apps/dashboard/`:

- Build: green (vite 6.4.2, 68 modules, no TypeScript errors)
- Tests: 148 passed (12 test files)
- Lint: clean (no ESLint warnings or errors)

---

## 2. Revert-and-confirm-fail results

### #1 — dashed-border / CI-crosses-null rule

Temporarily replaced `ciCrossesNull` body with `return false`. Tests run:

- **5 FAILED** (in `similarity-heatmap-r10.test.tsx`):
  - "renders a dashed-border rect for a cell whose CI crosses SIMILARITY_NULL_VALUE" (case 1)
  - "includes the CI values in the aria-label of a crossing cell (Variant B)" (case 1)
  - "[0.499, 0.501] crosses null -> dashed" (case 6)
  - "a filtered selection reads the correct original-model-order CI" (case 7)
  - "food.json: dashed cells render correctly (smoke render, no crash)" (case 10)
- 143 passed | 5 failed

Restored via Edit -> 148 passed.

### #2 — R10 binding guard

Temporarily replaced `buildAriaLabel` with a bare-point-estimate form:
`"${shortA} versus ${shortB}: ${sim.toFixed(2)}"` (no CI phrase). Tests run:

- **7 FAILED** (in `similarity-heatmap-r10.test.tsx`):
  - "includes the CI values in the aria-label of a crossing cell (Variant B)" (case 1)
  - "includes CI values in aria-label of a non-crossing cell but NOT the suffix (Variant A)" (cases 2-3)
  - "renders solid border and 'confidence interval not available' for null-CI cell (Variant C)" (case 4)
  - "[0.499, 0.501] crosses null -> dashed" (case 6)
  - "a filtered selection reads the correct original-model-order CI" (case 7)
  - **"all off-diagonal rects have an aria-label containing at least one of the 3 CI phrases"** (case 8 guard)
  - **"no off-diagonal rect has a bare-point-estimate aria-label"** (case 8 guard)
- 141 passed | 7 failed

The R10 binding guard (test case 8, both tests) fires on the exact pre-fix regression form. Restored -> 148 passed.

---

## 3. Coverage verdict

All 10 plan §5 cases covered. Mapping:

| Plan §5 case | Tests | Count |
|---|---|---|
| 1. crossing -> dashed + aria CI + suffix | tests 1,2 | 2 |
| 2-3. non-crossing -> solid, CI in aria, no suffix | tests 3,4 | 2 |
| 4. null-CI -> solid + "not available" | test 5 | 1 |
| 5. diagonal -> solid + "by construction" (+ pathological short-circuit) | tests 6,7 | 2 |
| 6. boundary arithmetic strict-< (constant + 4 boundary pairs) | tests 8-12 | 5 |
| 7. selection dual-index alignment | test 13 | 1 |
| 8. R10 binding guard (two guards) | tests 14,15 | 2 |
| 9. forbidden-vocab guard (aria + caption string) | tests 16,17 | 2 |
| 10. food >= 30 dashed (data + render); family 0 dashed (data + render) | tests 18-21 | 4 |

**Total: 21 tests. No gaps. No additions needed.**

---

## 4. WCAG dashStroke spot-check

Confirmed by reading `SimilarityHeatmap.tsx` lines 221-225:

```tsx
const stroke = crossing
  ? (sim >= HEATMAP_TEXT_SWITCH_THRESHOLD
      ? 'var(--color-background)'    // white stroke: seq-3/seq-4, >= 0.60
      : 'var(--color-text-primary)') // dark stroke: seq-0/1/2, < 0.60
  : 'var(--color-border)';
```

- `sim >= 0.60` (crossing): `var(--color-background)` = white on dark cells (seq-3/seq-4). Component header documents contrast ratios: 5.47:1 and 11.67:1, both WCAG 1.4.11 PASS.
- `sim < 0.60` (crossing): `var(--color-text-primary)` = dark on light cells (seq-0/1/2). Contrast ratios: 8.43:1, 5.82:1, 3.31:1, all WCAG 1.4.11 PASS.
- Non-crossing / diagonal: `var(--color-border)` 0.5px solid. No R10 dash needed.

`HEATMAP_TEXT_SWITCH_THRESHOLD = 0.60` reuses the same threshold as the text-color switch, which is correct. The fixture A-B cell (sim=0.45, crossing) uses dark stroke; this is consistent.

---

## 5. Focus2 fix confirmed

`ContentArea.tsx` line 144:

```tsx
similarityCi={domain.similarity_ci ?? []}
```

passed to `<Focus2FamilySimilarity>`, which forwards it to `<SimilarityHeatmap similarityCi={similarityCi ?? []} ...>` (line 274 of Focus2FamilySimilarity.tsx). The `?? []` degrades correctly when `similarity_ci` is absent. The re-review fix is in place.

---

## 6. Commit

No tests were added or modified. No commit for this gate.

---

## 7. Tree state

`git status --short` after all scratch edits restored:

- `M .claude/agent-memory/cda_sme/MEMORY.md` — pre-existing memory file from prior agent, not this task
- `?? docs/status/2026-06-08-phase9a-T3-cda-sme-verdict.md` — untracked, not part of this task
- `?? docs/status/2026-06-08-phase9a-T3-uiux-verdict.md` — untracked, not part of this task
- `?? docs/status/2026-06-08-phase9a-T3-heatmap-r10-architect-plan.md` — untracked, not part of this task
- `?? WritingSample/` — pre-existing, instructed to leave untouched
- `?? out/rebaseline/` — pre-existing, instructed to leave untouched

No scratch edits outstanding on any tracked source file. Tree at HEAD `d4f623e`.
