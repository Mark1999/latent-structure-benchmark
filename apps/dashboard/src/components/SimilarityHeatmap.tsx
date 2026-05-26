/**
 * SimilarityHeatmap — n×n grid heatmap of cross-model similarity scores.
 *
 * Color scale: 5-stop discrete binning from near-white (#eaf0f8) to deep navy
 * (#1a3a5c) per DESIGN_SYSTEM.md §1.2 sequential scale and §12.8.
 * Text color switches at 0.60: dark text on stops 0–2, white text on stops 3–4.
 * Responds to selectedModelIds — only shows rows/columns for selected models.
 */

// 5-stop discrete color scale per tokens.css --color-scale-seq-*
const HEATMAP_COLORS = [
  '#eaf0f8',  // seq-0 — similarity 0.00–0.20
  '#b8cce4',  // seq-1 — similarity 0.20–0.40
  '#6b9dc8',  // seq-2 — similarity 0.40–0.60
  '#2e6da4',  // seq-3 — similarity 0.60–0.80
  '#1a3a5c',  // seq-4 — similarity 0.80–1.00
];

// Per DESIGN_SYSTEM.md §12.8: switch threshold at 0.60
const HEATMAP_TEXT_SWITCH_THRESHOLD = 0.60;

function simToColor(sim: number): string {
  const idx = Math.min(4, Math.floor(sim * 5));
  return HEATMAP_COLORS[idx];
}

function simToTextColor(sim: number): string {
  return sim >= HEATMAP_TEXT_SWITCH_THRESHOLD
    ? '#ffffff'
    : '#000000';
}

function shortName(id: string): string {
  return id.split('/').pop() || id;
}

export interface SimilarityHeatmapProps {
  similarityMatrix: number[][];
  models: Array<{ model_id: string; provider: string; family: string }>;
  selectedModelIds: Set<string>;
}

export function SimilarityHeatmap({
  similarityMatrix,
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
  const HEADER_SIZE = 90;  // space for rotated column headers
  const ROW_LABEL_WIDTH = 110;
  const PADDING = 4;

  const svgWidth = ROW_LABEL_WIDTH + n * CELL_SIZE + PADDING;
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
        {/* Column headers — rotated -45° */}
        {filteredModels.map((colModel, ci) => {
          const cx = ROW_LABEL_WIDTH + ci * CELL_SIZE + CELL_SIZE / 2;
          const cy = HEADER_SIZE - 4;
          const label = shortName(colModel.model_id);
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
          const rowLabel = shortName(rowModel.model_id);

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

                return (
                  <g key={`cell-${rowModel.model_id}-${colModel.model_id}`}>
                    <rect
                      x={cx}
                      y={ry}
                      width={CELL_SIZE}
                      height={CELL_SIZE}
                      fill={cellColor}
                      stroke="var(--color-border)"
                      strokeWidth={0.5}
                      className="similarity-heatmap__cell"
                      aria-label={`${rowLabel} vs ${shortName(colModel.model_id)}: ${sim.toFixed(2)}`}
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
