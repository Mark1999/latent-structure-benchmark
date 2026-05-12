# Phase 6 T5 — SimilarityHeatmap — Architect Plan

**Date:** 2026-05-12
**Planner:** Architect agent (Opus)
**Phase scope:** Phase 6 T5 only (defined in `/opt/lsb-agent/docs/status/2026-05-12-phase6-architect-kickoff.md` §2 T5 as "hand-rolled SVG heatmap viz tab; cells show similarity from `similarity_matrix`; hover tooltip shows `similarity ± 95% CI` from `similarity_ci`; cells whose CI crosses null shown with reduced saturation per ARCHITECTURE.md §4.5; `VizSwitcher` enables the 'Similarity' tab.").
**Status:** Awaiting CDA SME dispatch (REQUIRED — see §6); then UI/UX light-touch (§6); then Coder dispatch on PASS.

---

## §0. Reading list (mandatory before Coder dispatch)

1. `/opt/lsb-agent/CLAUDE.md` §6 (binding rules — especially R10), §7 (forbidden vocabulary), §9 (pitfalls 4, 5, 7, 8).
2. `/opt/lsb-agent/ARCHITECTURE.md` §1.5 (binding on every text artifact), §1.5.4 forbidden vocabulary, §4.5 (R10 binding).
3. `/opt/lsb-agent/DESIGN_SYSTEM.md` §3.3 (note: live §3.3 is MDSPlot detailed spec; §3.2 inventory says SimilarityHeatmap is "Plotly" — Architect overrides per §2.1), §1 (tokens), §7 accessibility floor, §12.4 model color assignment.
4. `/opt/lsb-agent/docs/status/2026-05-12-phase6-architect-kickoff.md` §2 T5, §2 T6 (T6 deferred to FT designer per `feedback_ui_polish_scope.md`).
5. `/opt/lsb-agent/docs/status/2026-05-12-phase6-T0-architect-plan.md` §4 (shape disagreements; cast-through-unknown pattern), `/opt/lsb-agent/docs/status/2026-05-12-phase6-T7-architect-plan.md` (structural precedent), `/opt/lsb-agent/docs/status/2026-05-12-phase6-T7-cda-sme-verdict.md` and `/opt/lsb-agent/docs/status/2026-05-12-phase6-T7-uiux-plan-verdict.md` (verdict format precedents).
6. Memory: `feedback_ui_polish_scope.md` (minimum-viable functional surface; **T5 uses EXISTING color tokens only**), `feedback_visual_inspection.md`, `feedback_inspection.md`.
7. `/opt/lsb-agent/apps/dashboard/public/data/family.json` and `holidays.json`:
   - `similarity_matrix`: `number[][]`, row/col indexed by `models[i].model_id` order.
   - `similarity_ci`: `[number, number][][]` paired with similarity_matrix, possibly null.
   - Diagonal = `1.0`.
8. `/opt/lsb-agent/apps/dashboard/src/components/{VizSwitcher.tsx, DataExplorer.tsx, MDSPlot.tsx, FreeListCompare.tsx}`.
9. `/opt/lsb-agent/apps/dashboard/src/lib/modelShortName.ts`.
10. `/opt/lsb-agent/apps/dashboard/src/styles/tokens.css`.

---

## §1. Mark's binding directives + Phase 6 functional-surface framing

1. Phase 6 minimum-viable functional surface. **T5 uses EXISTING design tokens only; no new color tokens.** T6 deferred.
2. R10 binding non-negotiable. Cell = point estimate, CI = uncertainty. R10 satisfied on visual (numeric label) + DOM (aria-label) axes.
3. Visual evaluation is the goal — a heatmap surfaces patterns the inspect table cannot.
4. Empty cells (null CI) are first-class states per §1.5 — no "missing"/"placeholder" framing.
5. Forbidden vocabulary (§1.5.4) applies to caption, tooltip, aria-labels, empty-state captions.
6. No new dependencies. Hand-rolled SVG per MDSPlot precedent.
7. `?inspect=...` operator surface (T0) untouched.
8. No software-side spend gates (R14).
9. Bundle budget: T5 adds ≤ 8 KB gzipped.

---

## §2. Decisions

### §2.1. Hand-rolled SVG vs. Plotly — **hand-rolled SVG.**

Kickoff Open Question 4 resolved: hand-rolled. Rationale:
1. Bundle headroom — Plotly at 80 KB consumes 20% of cap for one viz.
2. Phase 5 (MDSPlot) and Phase 6 T7 established hand-rolled SVG as fully accessible at this scale.
3. Plotly's "convenience" is canceled by accessibility configuration overhead.
4. ≤ 11×11 = 121 cells worst-case; bounded DOM, no virtualization needed.

DESIGN_SYSTEM.md §3.2 inventory line "Plotly" is inconsistent with this decision. **T14 follow-up replacement text:** `"Similarity | SimilarityHeatmap.tsx | Custom (hand-rolled SVG) | Model×model similarity matrix with per-cell bootstrap CIs"`. The Coder includes this in the T5 commit body.

### §2.2. Color encoding — **alpha-blend on `--color-text-primary` (no new tokens).**

Each cell's background:
```
cellBackground = `rgba(44, 62, 80, ${similarity})`
```

The hex `#2c3e50` (value of `--color-text-primary`) decomposes to RGB `44, 62, 80`. Coder uses a documented constant `HEATMAP_BASE_RGB = "44, 62, 80"` with a comment naming the source token.

Visual semantics: similarity=1.0 → opaque dark; 0.5 → mid-tone (ambiguity visible); 0.0 → transparent/white.

**Cell text contrast switch:**
- `similarity > 0.5` → text fill `var(--color-background)` (white)
- `similarity ≤ 0.5` → text fill `var(--color-text-primary)` (dark)

The boundary at 0.5 is contrast-critical. Coder empirically verifies WCAG AA 4.5:1 against every actual cell value in family.json and holidays.json. **Binding fallback if boundary fails:** raise threshold to 0.55 and re-verify.

### §2.3. The "null threshold" for CI-crosses-null — **`SIMILARITY_NULL_VALUE = 0.5`.** (CDA SME approves or revises.)

For Smith's S cross-model similarity statistic, `0.5` = "no agreement" (0 = perfect anti-agreement; 1 = perfect agreement).

**Rule:** cell's CI "crosses null" when `ci_lower < SIMILARITY_NULL_VALUE < ci_upper`. Such cells get a **dashed border** (1.5px, `var(--color-text-primary)`, dasharray `3,2`) instead of the standard solid border (1px, `var(--color-border)`).

The dashed treatment is the "reduced saturation per §4.5" — visual weight reduction within existing tokens. Color-saturation changes would require new sequential palette (T6, deferred).

**Configuration:** `SIMILARITY_NULL_VALUE` defined at `apps/dashboard/src/config/analysis.ts` (parallel to existing `OCI_LOW_CONCENTRATION_THRESHOLD`). No component references `0.5` literally for this purpose.

**CDA SME binding scope:** approve `0.5` or specify alternative. PASS → proceed. PASS-WITH-NOTES → adjust constant. FAIL → re-plan.

### §2.4. Hover tooltip + DOM-paired aria-label.

**Hover (desktop):** tooltip shows
```
<short model name A> vs <short model name B>
similarity: 0.73, 95% CI [0.65, 0.81]
```
Null-CI cells: `95% CI: —`.

**Aria-label (touch / keyboard / screen reader):**
```
${shortNameA} versus ${shortNameB}: similarity ${similarity.toFixed(2)}, 95 percent confidence interval ${ciLow.toFixed(2)} to ${ciHigh.toFixed(2)}
```
Null-CI: `confidence interval not available`.
Diagonal: `${shortName} self-similarity: 1.00 by construction`.

**Forbidden-vocab compliance:** "versus" is data-relation language. No "agrees with," "thinks like," "sees similarly to," "perceives," "understands," "believes."

### §2.5. Cell labels — numeric similarity in mono font.

`similarity.toFixed(2)` (e.g., `"0.73"`), `var(--font-mono)` at `var(--font-size-xs)`, centered. Contrast-switch per §2.2.

Implementation helper:
```ts
const HEATMAP_BASE_RGB = "44, 62, 80"; // RGB of --color-text-primary; kept in sync via this comment
function cellBackground(similarity: number): string {
  return `rgba(${HEATMAP_BASE_RGB}, ${similarity})`;
}
```

### §2.6. Diagonal cells — visible but de-emphasized.

`similarity_matrix[i][i] === 1.0` always. Render with alpha-blend (fully opaque dark), white text, standard solid border. Aria-label uses self-similarity phrasing per §2.4.

### §2.7. Null-CI cell handling — first-class state per §1.5.

- Cell background alpha-blended per §2.2 (visible like any other cell).
- Solid border (NO dashed treatment — CI cannot be evaluated when absent).
- Tooltip CI: `—`. Aria-label: `confidence interval not available`.
- No "missing"/"placeholder"/"no data yet"/"pending" framing.

### §2.8. Column/row ordering — `model_id` lexicographic, filtered to `selectedModels`.

**Dual-index translation** is the highest-risk unit-test target:
1. Build `modelIndexMap: Map<string, number>` from `domainResult.models.map((m, i) => [m.model_id, i])`.
2. Sort `selectedModels` lexicographically: `displayedIds = [...selectedModels].sort()`.
3. For displayed pair `(i, j)`: `matrixI = modelIndexMap.get(displayedIds[i])`, `matrixJ = modelIndexMap.get(displayedIds[j])`.
4. Read `similarity_matrix[matrixI][matrixJ]` and `similarity_ci[matrixI][matrixJ]`.

---

## §3. Acceptance criteria

1. `cd apps/dashboard && npm run build && npm run test && npm run lint` passes.
2. `similarity` tab no longer disabled; `aria-disabled` absent.
3. `<dev-server>/#similarity` mounts SimilarityHeatmap on first paint without flicker.
4. With 6 default-selected models on family: 6×6 grid with numeric values, alpha-blended backgrounds, contrast-switched text, visible diagonal per §2.6.
5. Hover on desktop displays tooltip per §2.4.
6. Each `<rect>` has aria-label per §2.4. Diagonal uses self-similarity phrasing.
7. Cells where `ci_lower < SIMILARITY_NULL_VALUE < ci_upper` get dashed border. Others solid. Null-CI cells solid (§2.7).
8. Column header row above + row header column to left in `var(--font-mono)` at `var(--font-size-xs)`. Rotated 45° if needed at narrow viewports.
9. Caption below heatmap: **"Each cell shows how similarly two models organize this domain (1.00 = identical organization; 0.50 = no agreement). Dashed cells span the no-agreement value within their 95% confidence interval."** Forbidden-vocab clean. Token: `var(--color-text-caption)` at `var(--font-size-sm)`.
10. `selectedModels.length === 0` renders: **"Select one or more models to see the similarity heatmap."**
11. `selectedModels.length === 1` renders 1×1 grid (just the diagonal).
12. WCAG AA: SVG `role="img"`, `aria-label="Cross-model similarity heatmap; N models displayed of M total"`. sr-only `<h2>` bridge ("Similarity heatmap") as first child per F-T7-A1 precedent. Heading order intact. Worst-case cell text contrast ≥ 4.5:1.
13. `<meta name="robots">` unaffected.
14. Bundle delta ≤ 8 KB gzipped against post-T7 baseline. Coder reports in commit body.
15. No new dependencies. Reuse `modelShortName` and `modelColors`.
16. No forbidden vocabulary in caption, tooltip, aria-labels, empty-state. Statistical field names exempt.
17. R6 not triggered — no schema changes.
18. Coder does NOT touch `data/types.ts`. (T14 concern.)
19. Coder does NOT touch `MDSPlot.tsx`, `FreeListCompare.tsx`, `ModelSelector.tsx`, `Legend.tsx`, or T4-territory files.
20. Mobile `<768px`: SVG `viewBox` + `preserveAspectRatio="xMidYMid meet"` for responsive scaling. Touch tooltip via `focus`/`focusin` with `tabIndex={0}`.
21. `SIMILARITY_NULL_VALUE` defined at `apps/dashboard/src/config/analysis.ts`; no T5 component references `0.5` literally.

---

## §4. Known shape disagreements (Coder note)

T5 inherits the T0/T7 shape mismatches (`similarity_matrix`, `similarity_ci`, `mds_coordinates`). Cast through unknown:
```ts
const rawSimilarityMatrix = domainResult.similarity_matrix as unknown as number[][];
const rawSimilarityCi = domainResult.similarity_ci as unknown as Array<Array<[number, number] | null>>;
```

**Coder MUST NOT "fix" `data/types.ts` in T5.** T14 doc-sweep concern. Surface in commit body for T14.

---

## §5. Out of scope

- T6 (heatmap color tokens) — deferred to FT designer.
- Plotly, d3, any chart library.
- DriftTracker (T4) — tab remains disabled.
- Methodology page link.
- T8 (Read-as-table) — inspect surface is the table fallback.
- Mobile bottom-drawer (T12), hamburger (T11).
- Cell click → drill-down.
- Animation.
- Dark mode.
- Hierarchical clustering reorder.
- Touching `data/types.ts`, `MDSPlot.tsx`, `FreeListCompare.tsx`, `ModelSelector.tsx`, `Legend.tsx`.
- `react-router-dom`, second Vite entry.
- CSV/JSON export.

---

## §6. Gate routing

- **Architect:** this plan.
- **CDA SME: REQUIRED.** Four-axis review of §2.3:
  1. Protocol validity — `0.5` correct null for Smith's S?
  2. Analytical validity — "CI crosses null" the right operationalization of §4.5 reduced-saturation?
  3. Claims validity — caption text and tooltip language accurate, non-overclaiming?
  4. Audience translation — journalist/AI engineer understands "dashed = statistically ambiguous"? §1.5 framing intact?
  - PASS → proceed with 0.5.
  - PASS-WITH-NOTES → Coder updates constant per SME.
  - FAIL → re-plan.
- **UI/UX: light-touch only.** Five checks:
  1. SVG `role="img"`, sr-only h2 bridge, heading order.
  2. **Cell text contrast switch at boundary — verify against actual family.json/holidays.json values.** (Single biggest UI/UX risk.)
  3. R10 pairing: numeric label visual + aria-label DOM CI disclosure. Dashed border = §4.5 reduced-saturation.
  4. Tokens only (literal `HEATMAP_BASE_RGB` is documented token-extraction shortcut, not a violation).
  5. Mobile: `viewBox` scales 320–768px; touch tooltip via `focus`/`focusin`.
  - No design critique beyond these. §3.2 inventory line "Plotly" → T14 follow-up, not a T5 block.
- **Coder:** implements after both PASS or PASS-WITH-NOTES.
- **Reviewer:** standard 9-check sweep. Includes §7 forbidden-vocab spot check, R10 binding validation, SIMILARITY_NULL_VALUE constant check.
- **Tester:** vitest. Surface includes tab activation, dual-index translation correctness, dashed-border CI-crosses-null logic, null-CI cell handling, diagonal self-similarity aria-label, empty-state, contrast switch fires at boundary.

---

## §7. Schema impact

| Touch point | Touched? | Co-update? |
|---|---|---|
| `cdb_core/schemas.py` | No | No |
| `docs/DATA_DICTIONARY.md` | No | No |
| `ARCHITECTURE.md` | No (T14 may sharpen §4.5 with SIMILARITY_NULL_VALUE rule) | No |
| `DESIGN_SYSTEM.md` | No (T14 §3.2 reconciliation) | No |
| `data/types.ts` | **No** (T14) | No |
| `apps/dashboard/src/config/analysis.ts` | **Yes** — adds `SIMILARITY_NULL_VALUE = 0.5` | No |

Architect sign-off needed: none.

---

## §8. Bundle budget

Post-T7 baseline: ~85 KB. T5 estimate:
- `SimilarityHeatmap.tsx`: ~5–6 KB gzipped.
- `similarity-heatmap.css`: ~1 KB.
- `VizSwitcher.tsx`, `DataExplorer.tsx`, `config/analysis.ts` edits: ~0.1 KB total.

**Expected delta: ~6–7 KB gzipped.** Under 8 KB ceiling.

Phase 6 cumulative after T0+T7+T5: ~91–93 KB (~23% of cap).

---

## §9. Dependency order

**Upstream:** None strict. T0 + T7 patterns referenced.

**Downstream:**
- T8 (AccessibilityTableToggle) — adds HTML-table alternative.
- T14 — DESIGN_SYSTEM.md §3.2 reconciliation, ARCHITECTURE.md §4.5 sharpening.

**Parallel:** T3, T4, T9, T11, T12.

**Component breakdown final:** Two files — `SimilarityHeatmap.tsx` (single component, inline cell render — no separate `SimilarityCell.tsx`) + `similarity-heatmap.css`. Rationale: at ≤ 121 cells, splitting adds reconciliation overhead with no architectural benefit. ~280–340 LoC total.

---

## §10. Risks and watch-items

1. **Cell text contrast at boundary.** §2.2 binary switch at 0.5; computed contrast ~4.4:1 at the seam. Binding fallback: raise to 0.55 if any cell value fails. Coder verifies all 121 × 2 domain cells empirically.
2. **CDA SME rejects `0.5` as null.** Probability: low-to-moderate. If SME specifies different null, Coder updates `SIMILARITY_NULL_VALUE` in config; re-verifies risk #1 at new threshold.
3. **`data/types.ts` fix temptation.** Reviewer rejects T5 commits that touch it.
4. **Mobile rendering of 11×11.** SVG `viewBox` scales. If 320px viewport with 11 models makes labels unreadable, Coder may CSS-suppress labels below width threshold; report in commit body.
5. **Top-left header corner.** Empty cell to avoid label collision.
6. **Touch hover.** `focus`/`focusin` with `tabIndex={0}` per FreeListCompare precedent.
7. **Bundle creep from "just one more interaction."** Resist.
8. **§3.2 "Plotly" inventory line** — T14 replacement text in commit body.
9. **Re-render cost.** `useCallback`/`useMemo` per MDSPlot precedent. ≤ 121 cells bounded.
10. **`HEATMAP_BASE_RGB` literal looks like token violation.** It is a documented token-extraction shortcut; comment names source token; T14 may migrate to `--heatmap-base-rgb` CSS custom property.

---

*End of T5 plan.*
