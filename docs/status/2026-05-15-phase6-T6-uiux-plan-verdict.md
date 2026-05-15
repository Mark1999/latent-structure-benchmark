---
filed: 2026-05-15
reviewer: UI/UX agent (Sonnet)
task: Phase 6 T6 — Heatmap color scale design system update
plan_reviewed: docs/status/2026-05-15-phase6-T6-architect-plan.md
posture: B (Mark's locked-in choice — OWID-style sequential blue, 5 stops, no diverging scale)
slack_channel: "#lsb-ui-ux"
design_system_version: v0.4.9 (UPDATE APPLIED — introduces §1.2 sequential scale tokens; rewrites §12.8 for new palette; bumps version header, footer, changelog)
verdict: PASS-WITH-NOTES
---

# Phase 6 T6 — UI/UX Plan Verdict (Heatmap Color Scale)

**UI/UX VERDICT: PASS-WITH-NOTES**

```
UI/UX VERDICT: PASS-WITH-NOTES

1. OWID design fidelity:      PASS
2. 30-second journalist:      PASS
3. Researcher cite path:      PASS
4. WCAG AA:                   PASS-WITH-NOTES (M1 — stops 0–2 compositional-only; documented)

DESIGN_SYSTEM.md update:      required — APPLIED (v0.4.8 → v0.4.9)
```

T6 is approved for Coder dispatch with one M-note (M1, non-blocking, documented in §12.8). DESIGN_SYSTEM.md v0.4.9 update is applied and required in the same commit.

---

## Posture and mandate

Mark's decision: **Posture B** — introduce a new OWID-style sequential blue palette (5 stops, single-hue, light gray-blue to deep navy). The Architect plan correctly notes that Posture B requires UI/UX to: (a) select palette stops, (b) redo the WCAG AA contrast table, (c) run the model-palette collision check, (d) specify the Coder back-port, and (e) choose discrete binning vs. continuous interpolation.

Diverging scale: deferred to T4 DriftTracker (Mark's decision, per task brief).

---

## 1. OWID design fidelity — PASS

The palette follows OWID single-hue sequential conventions: a single blue hue family with luminance varying from near-white (low similarity) to deep navy (high similarity). This matches OWID's sequential scales for continuous quantitative variables (e.g., their population-density maps, their sequential temperature scales). The scale reads perceptually in the correct direction: darker = more similar, lighter = less similar. No hue shift across the ramp (pure luminance variation within the blue family). The WCAG AA cell-text rule is satisfied at all five stops.

---

## 2. 30-second journalist test — PASS

The heatmap's visual encoding is self-explanatory: darker cells = more similar categorical structure. The caption ("Each cell shows how similarly two models organize this domain...") is retained verbatim from T5 (CDA SME T5 §5.1 binding). The new palette does not change the caption. A journalist can land, see the darkest cells, read the similarity value, and have a quotable observation within 30 seconds. No regression from T5.

---

## 3. Researcher cite path — PASS

No change to data paths, methodology page links, open-data bundle, or citation inline from T5. This verdict is N/A in substance — T6 changes the color encoding only, not the data model or citation infrastructure.

---

## 4. WCAG AA accessibility — PASS-WITH-NOTES

**M1 (NON-BLOCKING — documented in §12.8):** Stops 0, 1, and 2 do not pass WCAG AA 3:1 graphical-object contrast on white (#ffffff) as standalone swatches:

| Stop | Contrast on white |
|---|---|
| seq-0 (#eaf0f8) | 1.13:1 FAIL |
| seq-1 (#b8cce4) | 1.64:1 FAIL |
| seq-2 (#6b9dc8) | 2.89:1 FAIL |

These stops are used only as 52×52 px heatmap cell fills. In the heatmap context, the adjacent cell border (`--color-border`, #dde1e7) and the printed similarity value (mono font, `--color-heatmap-cell-text-dark` on stops 0–2) provide boundary discrimination for each cell. The cell as a whole is graphically bounded and textually labeled; the fill color alone does not carry the full graphical meaning. This is the same posture as the T5 alpha-blend stops at low similarity values (which also produced near-white fills indistinguishable from background without the border).

**Binding constraint from M1:** Stops 0–2 must NOT be used as standalone swatches (legend, downloadable PNG, print) without a 1px `--color-border` outline. This is documented in §12.8.

**Cell text contrast — both arms PASS WCAG AA 4.5:1 at all five stops:**

| Stop | Hex | L_bg | White text contrast | Dark text contrast | Text arm |
|---|---|---|---|---|---|
| seq-0 | #eaf0f8 | 0.877 | 1.13:1 FAIL | 18.54:1 PASS | Dark |
| seq-1 | #b8cce4 | 0.590 | 1.64:1 FAIL | 12.79:1 PASS | Dark |
| seq-2 | #6b9dc8 | 0.314 | 2.89:1 FAIL | 7.27:1 PASS | Dark |
| seq-3 | #2e6da4 | 0.142 | 5.47:1 PASS | 3.84:1 FAIL | White |
| seq-4 | #1a3a5c | 0.040 | 11.65:1 PASS | 1.80:1 FAIL | White |

The switch threshold is **`HEATMAP_TEXT_SWITCH_THRESHOLD = 0.60`**. Rationale: with discrete binning, the [0.40, 0.60) bin maps to stop 2 (dark text 7.27:1 PASS, white text 2.89:1 FAIL) and the [0.60, 0.80) bin maps to stop 3 (white text 5.47:1 PASS, dark text 3.84:1 FAIL). The threshold 0.60 is the exact bin boundary — the switch is architecturally clean: at 0.60 the cell moves to stop 3 and white text applies.

The T5 threshold of 0.73 is **superseded**. The Coder must update `HEATMAP_TEXT_SWITCH_THRESHOLD`.

---

## Palette specification — F-T6-PALETTE (BINDING)

**Five hex stops (binding — Coder must implement exactly these values):**

| Token | Hex | L (sRGB) | Similarity reference | Standalone WCAG 3:1? |
|---|---|---|---|---|
| `--color-scale-seq-0` | `#eaf0f8` | 0.877 | 0.00 | NO — compositional only |
| `--color-scale-seq-1` | `#b8cce4` | 0.590 | 0.25 | NO — compositional only |
| `--color-scale-seq-2` | `#6b9dc8` | 0.314 | 0.50 | NO — compositional only |
| `--color-scale-seq-3` | `#2e6da4` | 0.142 | 0.75 | YES — 5.47:1 on white |
| `--color-scale-seq-4` | `#1a3a5c` | 0.040 | 1.00 | YES — 11.65:1 on white |

**Luminance computation method:** WCAG 2.1 sRGB relative luminance. For each channel c = R,G,B in [0,1]: linearized = c/12.92 if c ≤ 0.04045, else ((c+0.055)/1.055)^2.4. L = 0.2126·R_lin + 0.7152·G_lin + 0.0722·B_lin.

**Perceptual ramp check:** Luminance steps between adjacent stops:
- seq-0 → seq-1: ΔL = 0.877 - 0.590 = 0.287
- seq-1 → seq-2: ΔL = 0.590 - 0.314 = 0.276
- seq-2 → seq-3: ΔL = 0.314 - 0.142 = 0.172
- seq-3 → seq-4: ΔL = 0.142 - 0.040 = 0.102

Steps are monotonically decreasing — the ramp is perceptually compressed at the dark end, which is typical of perceptual (CIELAB-informed) blue palettes and matches OWID practice. The lighter end has larger ΔL steps to provide adequate discrimination at low-similarity cells. Acceptable.

---

## Cell color mapping — discrete binning (BINDING)

The Coder implements **discrete binning**, not continuous interpolation. Override of the Architect's lean toward continuous interpolation. Rationale: the 5 named tokens are the design system record of the palette; any interpolated color between stops is undocumented in the design system and cannot be inspected or audited against §12.8. Discrete binning keeps every rendered color identical to a named token. The visual cost (slight step-band appearance in transitions) is acceptable given the Phase 6 minimum-viable posture and the existing T5 step pattern in the alpha-blend (which also produces visible banding at low-similarity ranges).

**Bin boundaries (binding):**
```
[0.00, 0.20) → seq-0  (#eaf0f8)
[0.20, 0.40) → seq-1  (#b8cce4)
[0.40, 0.60) → seq-2  (#6b9dc8)
[0.60, 0.80) → seq-3  (#2e6da4)
[0.80, 1.00] → seq-4  (#1a3a5c)
```
Diagonal cells (similarity = 1.00 by construction) always land in seq-4 by the `[0.80, 1.00]` inclusive upper bound.

The Coder implements this as a simple conditional lookup with no library dependency. No `d3-scale`, `chroma-js`, or `color-mix()` required.

---

## New switch threshold — F-T6-C1 (BINDING)

**`HEATMAP_TEXT_SWITCH_THRESHOLD = 0.60`**

Replaces the T5 value of 0.73. Coder MUST update the constant and its WCAG comment block.

```ts
const HEATMAP_TEXT_SWITCH_THRESHOLD = 0.60;
// WCAG AA rationale (2026-05-15 UI/UX verdict — F-T6-C1 BINDING):
// Discrete-binning model. Threshold is the [0.40,0.60)→[0.60,0.80) bin boundary.
//   sim < 0.60 → stop 0/1/2 → dark text (#000000):
//     stop 2 (darkest dark-text stop): dark text 7.27:1 PASS, white text 2.89:1 FAIL
//   sim >= 0.60 → stop 3/4 → white text (#ffffff):
//     stop 3 (lightest white-text stop): white text 5.47:1 PASS, dark text 3.84:1 FAIL
// T5 threshold of 0.73 is SUPERSEDED. Do not use.
```

Text color rule:
```ts
textFill = similarity >= HEATMAP_TEXT_SWITCH_THRESHOLD
  ? "var(--color-background)"                  // white, ≥5.47:1 at stop 3/4
  : "var(--color-heatmap-cell-text-dark)"      // black, ≥7.27:1 at stop 0/1/2
```

Note: the threshold uses `>=` (inclusive) because at exactly 0.60, the cell is in the [0.60, 0.80) bin (stop 3, white text). The `cellBackground()` function uses `similarity < 0.60` for the last dark-text bin.

---

## R1-marker collision check — result

**Result: ACCEPTABLE WITH DOCUMENTATION**

Blue model palette colors:

| Token | Hex | L | Nearest seq stop | Contrast between token and stop |
|---|---|---|---|---|
| --color-model-1 | #3360a9 | 0.119 | seq-3 (#2e6da4, L=0.142) | 1.15:1 |
| --color-model-8 | #1a5276 | 0.076 | seq-4 (#1a3a5c, L=0.040) | 1.47:1 |

The 1.15:1 ratio between seq-3 and model-1 is below the WCAG 3:1 graphical-object threshold. In same-size swatch-adjacent contexts, these two colors would be difficult to distinguish. This is documented as an operational acceptability determination, not a WCAG violation:

1. SimilarityHeatmap and MDSPlot are on separate VizSwitcher tabs — never simultaneously visible in the same viewport.
2. Heatmap cells (52×52 px filled rectangles) vs. legend dots (~10–12 px circles) differ in shape and size — shape encoding provides primary discrimination beyond hue.
3. Each cell carries a printed similarity value that is the primary information carrier; the fill color is a redundant secondary encoding.
4. WCAG 1.4.1 (Use of Color): "Color is not used as the only visual means of conveying information." The similarity text and cell position satisfy this independently of stop color.

Non-blue model palette slots (model-2 red, model-3 orange, model-4 green, model-5 purple, model-6 teal, model-7 dark orange, model-9 dark purple, model-10 dark teal, model-11 dark gold) are in entirely distinct hue families. No collision with any sequential stop.

**The CDA SME's notes-only concern ("sequential scale must not color-confuse R1-state markers") is satisfied** because R1 markers carry shape encoding (filled circle / dashed circle / hollow triangle per §3.3.5) as their primary semantic signal, not color alone.

---

## CI-crosses-null treatment — DEFERRED to T14

Dashed-border treatment from T5 is retained verbatim. No code change to the CI-crosses-null rendering in this task. The §4.5 doc-text refinement (CDA SME T5 §5.4 suggested replacement sentence) remains a T14 follow-up. §12.8 documents the retention.

---

## `--color-heatmap-cell-text-dark` policy — RETAINED AS #000000

`--color-text-primary` (#2c3e50, L≈0.060) fails WCAG AA 4.5:1 at stop 2: (0.314+0.05)/(0.060+0.05) = 0.364/0.110 = 3.31:1. Pure black retained. Token remains component-scoped to `SimilarityHeatmap.tsx`.

---

## DESIGN_SYSTEM.md update — APPLIED (v0.4.8 → v0.4.9)

Five changes applied:
1. Version header: `v0.4.8` → `v0.4.9`.
2. Changelog bullet prepended (before v0.4.8 bullet).
3. §1.2: five new sequential scale tokens + prose note on usage rules.
4. §12.8: full rewrite for new palette (F-T6-C1 contrast table, new threshold 0.60, standalone-swatch constraint, collision check summary, CI-crosses-null deferral note).
5. Footer: `v0.4.8` → `v0.4.9`.

Plus `apps/dashboard/src/styles/tokens.css` runtime token additions for `--color-scale-seq-0` through `--color-scale-seq-4`.

---

## Findings table

| ID | Severity | File | Issue | Required correction |
|---|---|---|---|---|
| F-T6-PALETTE | BINDING | `tokens.css` + `SimilarityHeatmap.tsx` | New 5-stop sequential blue palette replaces T5 alpha-blend | Implement hex values exactly as specified; discrete binning per bin boundaries above |
| F-T6-C1 | BINDING | `SimilarityHeatmap.tsx` | Switch threshold changes from 0.73 to 0.60 | Update `HEATMAP_TEXT_SWITCH_THRESHOLD`; update WCAG comment block; update `cellBackground()` and `cellTextFill()` |
| M1 | NON-BLOCKING | `tokens.css` comment | Stops 0–2 compositional-only | Document in token comment (done); no runtime change required; constraint is on future standalone-swatch use |

---

## Required before merge (Coder)

1. F-T6-PALETTE applied — five hex values in `SimilarityHeatmap.tsx` `HEATMAP_SEQ_STOPS` array exactly as specified.
2. F-T6-C1 applied — `HEATMAP_TEXT_SWITCH_THRESHOLD` changed to 0.60; `cellBackground()` implements discrete binning; `cellTextFill()` uses `>= 0.60` comparison; WCAG comment block updated.
3. DESIGN_SYSTEM.md v0.4.9 changes already committed in the UI/UX verdict commit. Coder commit references DESIGN_SYSTEM.md §12.8 in the `SimilarityHeatmap.tsx` comment header.
4. `npm run build && npm run test && npm run lint` passes locally. T5 vitest assertions on `cellTextFill` / `cellBackground` behavior MAY need updating for the new threshold and the new return-type (hex string vs. rgba string) — the Coder updates those assertions (this is expected behavior change, not a regression).

Non-blocking (confirm in commit body):
- M1: comment in `tokens.css` tokens seq-0 through seq-2 confirms compositional-only constraint.
- Bundle delta measured and reported in commit body (expected ≤ 1 KB gzipped: five CSS custom properties + TSX function rewrite).

---

## Coder back-port instructions (verbatim)

**File:** `/opt/lsb-agent/apps/dashboard/src/components/SimilarityHeatmap.tsx`
**Lines to replace:** approximately 70–127 (the constants block and the three helper functions; line numbers may shift after the T5 edits — locate by name)

### Change 1: Replace `HEATMAP_BASE_RGB` with sequential stop lookup

Replace the `HEATMAP_BASE_RGB` constant and the `cellBackground()` function with:

```ts
/**
 * Sequential color scale — heatmap stops (v0.4.9 — T6).
 * See DESIGN_SYSTEM.md §1.2 sequential scale and §12.8 (F-T6-PALETTE BINDING).
 * Five named stops from --color-scale-seq-0 (lightest) to --color-scale-seq-4 (darkest).
 * Discrete binning: each similarity value maps to one stop via equal-width 0.20 bins.
 */
const HEATMAP_SEQ_STOPS: readonly string[] = [
  "#eaf0f8",  // --color-scale-seq-0  sim ∈ [0.00, 0.20)
  "#b8cce4",  // --color-scale-seq-1  sim ∈ [0.20, 0.40)
  "#6b9dc8",  // --color-scale-seq-2  sim ∈ [0.40, 0.60)
  "#2e6da4",  // --color-scale-seq-3  sim ∈ [0.60, 0.80)
  "#1a3a5c",  // --color-scale-seq-4  sim ∈ [0.80, 1.00]
];
```

### Change 2: Replace `HEATMAP_TEXT_SWITCH_THRESHOLD`

```ts
/**
 * Contrast-switch threshold per DESIGN_SYSTEM.md §12.8 (F-T6-C1 BINDING).
 * At or above this value: white text (var(--color-background), ≥5.47:1 at stop 3/4).
 * Below: black text (var(--color-heatmap-cell-text-dark), ≥7.27:1 at stop 0/1/2).
 *
 * The T5 threshold of 0.73 is SUPERSEDED by T6 (2026-05-15).
 * See docs/status/2026-05-15-phase6-T6-uiux-plan-verdict.md.
 */
const HEATMAP_TEXT_SWITCH_THRESHOLD = 0.60;
```

### Change 3: Replace `cellBackground()` function

```ts
/**
 * Returns the hex fill for a heatmap cell via discrete binning into 5 stops.
 * See DESIGN_SYSTEM.md §12.8 (F-T6-PALETTE BINDING).
 */
function cellBackground(similarity: number): string {
  const idx = Math.min(Math.floor(similarity / 0.20), 4);
  return HEATMAP_SEQ_STOPS[idx];
}
```

`Math.floor(similarity / 0.20)` maps [0.00,0.20)→0, [0.20,0.40)→1, [0.40,0.60)→2, [0.60,0.80)→3. For similarity=1.0 exactly: Math.floor(1.0/0.20)=5, clamped by `Math.min(..., 4)` to index 4. This correctly handles the diagonal cell (similarity=1.0) case.

### Change 4: Update `cellTextFill()` switch comparison

Change `similarity > HEATMAP_TEXT_SWITCH_THRESHOLD` to `similarity >= HEATMAP_TEXT_SWITCH_THRESHOLD`:

```ts
function cellTextFill(similarity: number): string {
  return similarity >= HEATMAP_TEXT_SWITCH_THRESHOLD
    ? "var(--color-background)"             // white ≥5.47:1 at sim >= 0.60 (stop 3/4)
    : "var(--color-heatmap-cell-text-dark)"; // black ≥7.27:1 at sim < 0.60 (stop 0/1/2)
}
```

### Change 5: Update T5 vitest assertions

Any existing test in the T5 suite that asserts `cellTextFill(similarity)` for values in [0.60, 0.73] will need updating: those cells now return white text (previously returned black text under T5's threshold of 0.73). The Coder locates these tests and updates the expected values. This is an expected behavior change, not a regression.

Any test that asserts `cellBackground()` returns an `rgba()` string will need updating to assert a hex string instead. Coder updates all affected assertions.

### No other changes

- `ciCrossesNull()`: **unchanged**.
- The dashed-border CI-crosses-null rendering: **unchanged**.
- `SIMILARITY_NULL_VALUE`: **unchanged**.
- The caption text: **unchanged** (CDA SME T5 §5.1 binding).
- The dashed-cell aria-label augmentation: **unchanged** (CDA SME T5 §5.2 binding).
- `apps/dashboard/src/styles/similarity-heatmap.css`: **unchanged**.
- `apps/dashboard/src/data/types.ts`: **unchanged**.

---

## Escalation items for Mark

**Five hex values confirmed:** `#eaf0f8`, `#b8cce4`, `#6b9dc8`, `#2e6da4`, `#1a3a5c`.

**New threshold:** `HEATMAP_TEXT_SWITCH_THRESHOLD = 0.60` (was 0.73 under T5). This is a behavior change — cells in the similarity range [0.60, 0.73) now use white text (previously used black text). The WCAG AA math confirms both arms pass at all stops.

**Collision concern documented, not blocking:** Stop 3 (#2e6da4) is visually similar to model-1 (#3360a9) in the blue hue family. Operational separation (separate VizSwitcher tabs, shape encoding, cell text) is sufficient. No palette change required.

---

*Posted to #lsb-ui-ux. Coder may proceed on receipt of this verdict with all BINDING findings applied; DESIGN_SYSTEM.md v0.4.9 update is in this same commit.*
