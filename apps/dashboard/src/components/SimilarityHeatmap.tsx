/**
 * SimilarityHeatmap — n×n grid heatmap of cross-model similarity scores.
 *
 * Color scale: 5-stop discrete binning from near-white (#eaf0f8) to deep navy
 * (#1a3a5c) per DESIGN_SYSTEM.md §1.2 sequential scale and §12.8.
 * Text color switches at 0.60: dark text on stops 0-2, white text on stops 3-4.
 * Responds to selectedModelIds — only shows rows/columns for selected models.
 *
 * R10 compliance (CLAUDE.md §6 rule 10 — no point estimate without uncertainty):
 *   - Visual: numeric similarity label on every cell (point estimate visible).
 *   - DOM: aria-label on every <rect> encodes similarity + 95% CI (4 variants
 *     per CDA SME T3 §2 binding strings).
 *   - Uncertainty: cells whose CI crosses SIMILARITY_NULL_VALUE get a dashed
 *     border per DESIGN_SYSTEM.md §12.8 T3 restored treatment.
 *
 * Dashed stroke contrast rule (UI/UX T3 verdict — binding):
 *   dashStroke = sim >= HEATMAP_TEXT_SWITCH_THRESHOLD
 *     ? 'var(--color-background)'    // white on seq-3/seq-4 cells: 5.47/11.67:1 PASS
 *     : 'var(--color-text-primary)'  // dark on seq-0/1/2 cells: 8.43/5.82/3.31:1 PASS
 * Non-crossing / diagonal cells always use solid 'var(--color-border)', 0.5px.
 *
 * Reference:
 *   docs/status/2026-06-08-phase9a-T3-heatmap-r10-architect-plan.md
 *   docs/status/2026-06-08-phase9a-T3-cda-sme-verdict.md §2 (aria binding)
 *   docs/status/2026-06-08-phase9a-T3-uiux-verdict.md (dashStroke contrast rule)
 *   DESIGN_SYSTEM.md §12.8 (v0.4.9 T6 + T3 dashed-stroke contrast ruling 2026-06-09)
 */

import { displayModel } from '../lib/familyUtils';
import { SIMILARITY_NULL_VALUE } from '../config/analysis';

// Per DESIGN_SYSTEM.md §12.8 (F-T6-C1 BINDING): switch threshold at 0.60.
// Reused by the dashStroke contrast rule (UI/UX T3 verdict — binding):
// sim >= 0.60 → seq-3/seq-4 → white stroke passes WCAG 1.4.11 3:1.
// sim <  0.60 → seq-0/1/2  → dark stroke passes WCAG 1.4.11 3:1.
const HEATMAP_TEXT_SWITCH_THRESHOLD = 0.60;

// 5-stop discrete color scale per tokens.css --color-scale-seq-*
const HEATMAP_COLORS = [
  'var(--color-scale-seq-0)',
  'var(--color-scale-seq-1)',
  'var(--color-scale-seq-2)',
  'var(--color-scale-seq-3)',
  'var(--color-scale-seq-4)',
];

function simToColor(sim: number): string {
  const idx = Math.min(4, Math.floor(sim * 5));
  return HEATMAP_COLORS[idx];
}

function simToTextColor(sim: number): string {
  return sim >= HEATMAP_TEXT_SWITCH_THRESHOLD
    ? '#ffffff'
    : 'var(--color-heatmap-cell-text-dark)';
}

/**
 * Returns true when a cell's 95% CI crosses the formal similarity null.
 *
 * Strict inequalities on both sides: [0.499, 0.501] → true (CI straddles
 * the null); [0.5, 0.501] → false; [0.499, 0.5] → false; [0.499, 0.499] →
 * false. Closed-boundary cases are not considered "crossing" per test case 6
 * binding (CDA SME T3 §1 + plan §5).
 * Null CI returns false: no CI means uncertainty is undisclosed, not that it
 * crosses the null.
 */
function ciCrossesNull(ci: [number, number] | null): boolean {
  if (ci === null) return false;
  return ci[0] < SIMILARITY_NULL_VALUE && SIMILARITY_NULL_VALUE < ci[1];
}

/**
 * Build the aria-label for a cell (CDA SME T3 §2 — four variants, verbatim binding).
 *
 * Variant D (diagonal):
 *   "{name} self-similarity: 1.00 by construction"
 * Variant A (off-diagonal, CI present, NOT crossing null):
 *   "{a} versus {b}: similarity X.XX, 95 percent confidence interval X.XX to X.XX"
 * Variant B (off-diagonal, CI present, crosses null):
 *   "{a} versus {b}: similarity X.XX, 95 percent confidence interval X.XX to X.XX;
 *    confidence interval includes the no-shared-structure value of 0.50"
 * Variant C (off-diagonal, CI null/missing):
 *   "{a} versus {b}: similarity X.XX, confidence interval not available"
 */
function buildAriaLabel(
  isDiagonal: boolean,
  shortA: string,
  shortB: string,
  sim: number,
  ci: [number, number] | null,
): string {
  if (isDiagonal) {
    return `${shortA} self-similarity: 1.00 by construction`;
  }
  if (ci === null) {
    return `${shortA} versus ${shortB}: similarity ${sim.toFixed(2)}, confidence interval not available`;
  }
  const base = `${shortA} versus ${shortB}: similarity ${sim.toFixed(2)}, 95 percent confidence interval ${ci[0].toFixed(2)} to ${ci[1].toFixed(2)}`;
  if (ciCrossesNull(ci)) {
    return `${base}; confidence interval includes the no-shared-structure value of 0.50`;
  }
  return base;
}

export interface SimilarityHeatmapProps {
  similarityMatrix: number[][];
  /** Per-cell 95% CI from bootstrap, indexed in the same models-array order as similarityMatrix. */
  similarityCi: ([number, number] | null)[][];
  models: Array<{ model_id: string; provider: string; family: string }>;
  selectedModelIds: Set<string>;
}

export function SimilarityHeatmap({
  similarityMatrix,
  similarityCi,
  models,
  selectedModelIds,
}: SimilarityHeatmapProps) {
  // Filter to selected models that have valid matrix indices
  const filteredIndices: number[] = models
    .map((m, i) => ({ model_id: m.model_id, i }))
    .filter(({ model_id }) => selectedModelIds.has(model_id))
    .map(({ i }) => i);

  const filteredModels = filteredIndices.map((i) => models[i]);

  if (filteredModels.length === 0) {
    return (
      <div className="similarity-heatmap similarity-heatmap--empty">
        No models selected.
      </div>
    );
  }

  const n = filteredModels.length;

  const CELL_SIZE = 32;
  const HEADER_SIZE = 110;  // space for rotated column headers (adjusted to prevent truncation)
  const ROW_LABEL_WIDTH = 120; // row label width (adjusted to prevent truncation)
  const PADDING = 4;

  const svgWidth = ROW_LABEL_WIDTH + n * CELL_SIZE + 80; // 80px right padding for rotated label overhang
  const svgHeight = HEADER_SIZE + n * CELL_SIZE + PADDING;

  return (
    <div className="similarity-heatmap">
      <svg
        className="similarity-heatmap__svg"
        width="100%"
        viewBox={`0 0 ${svgWidth} ${svgHeight}`}
        role="img"
        aria-label="Cross-model similarity heatmap"
      >
        {/* Column headers — rotated -45 degrees */}
        {filteredModels.map((colModel, ci) => {
          const cx = ROW_LABEL_WIDTH + ci * CELL_SIZE + CELL_SIZE / 2;
          const cy = HEADER_SIZE - 4;
          const label = displayModel(colModel.model_id);
          return (
            <text
              key={`col-header-${colModel.model_id}`}
              x={cx}
              y={cy}
              transform={`rotate(-45, ${cx}, ${cy})`}
              textAnchor="start"
              dominantBaseline="auto"
              className="similarity-heatmap__col-header"
            >
              {label}
            </text>
          );
        })}

        {/* Rows */}
        {filteredModels.map((rowModel, ri) => {
          const ry = HEADER_SIZE + ri * CELL_SIZE;
          const rowLabel = displayModel(rowModel.model_id);

          return (
            <g key={`row-${rowModel.model_id}`}>
              {/* Row label */}
              <text
                x={ROW_LABEL_WIDTH - 6}
                y={ry + CELL_SIZE / 2}
                dominantBaseline="middle"
                textAnchor="end"
                className="similarity-heatmap__row-label"
              >
                {rowLabel}
              </text>

              {/* Cells */}
              {filteredModels.map((colModel, ci) => {
                const rowIdx = filteredIndices[ri];
                const colIdx = filteredIndices[ci];
                const sim =
                  similarityMatrix[rowIdx]?.[colIdx] ?? 0;
                const cellColor = simToColor(sim);
                const textColor = simToTextColor(sim);
                const cx = ROW_LABEL_WIDTH + ci * CELL_SIZE;

                const isDiagonal = rowIdx === colIdx;

                // Dual-index CI lookup: use the same filteredIndices mapping
                // as the similarity matrix so a filtered cell reads the correct
                // original-index CI (plan §3, test case 7 binding).
                const cellCi: [number, number] | null =
                  similarityCi[rowIdx]?.[colIdx] ?? null;

                // Dashed border: CI crosses null AND not diagonal.
                // Diagonal is a hard short-circuit — self-similarity is an
                // identity fact with no bootstrap variance (CDA SME T3 §4b).
                const crossing = !isDiagonal && ciCrossesNull(cellCi);

                // dashStroke contrast rule (UI/UX T3 verdict — binding):
                // Switch on the EXISTING HEATMAP_TEXT_SWITCH_THRESHOLD = 0.60.
                // White stroke on seq-3/seq-4 cells (sim >= 0.60): 5.47/11.67:1 PASS.
                // Dark stroke on seq-0/1/2 cells (sim < 0.60): 8.43/5.82/3.31:1 PASS.
                // Non-crossing and diagonal: solid --color-border, 0.5px, no dasharray.
                const stroke = crossing
                  ? (sim >= HEATMAP_TEXT_SWITCH_THRESHOLD
                      ? 'var(--color-background)'
                      : 'var(--color-text-primary)')
                  : 'var(--color-border)';
                const strokeWidth = crossing ? 1.5 : 0.5;
                const strokeDasharray = crossing ? '3,2' : undefined;

                const shortA = displayModel(rowModel.model_id);
                const shortB = displayModel(colModel.model_id);
                const ariaLabel = buildAriaLabel(isDiagonal, shortA, shortB, sim, cellCi);

                return (
                  <g key={`cell-${rowModel.model_id}-${colModel.model_id}`}>
                    <rect
                      x={cx}
                      y={ry}
                      width={CELL_SIZE}
                      height={CELL_SIZE}
                      fill={cellColor}
                      stroke={stroke}
                      strokeWidth={strokeWidth}
                      strokeDasharray={strokeDasharray}
                      className="similarity-heatmap__cell"
                      aria-label={ariaLabel}
                    />
                    <text
                      x={cx + CELL_SIZE / 2}
                      y={ry + CELL_SIZE / 2}
                      dominantBaseline="middle"
                      textAnchor="middle"
                      fill={textColor}
                      className="similarity-heatmap__cell-value"
                    >
                      {sim.toFixed(2)}
                    </text>
                  </g>
                );
              })}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
