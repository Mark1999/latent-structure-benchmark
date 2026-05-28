/**
 * Focus1RunDistribution — run agreement heatmap + run MDS scatter.
 *
 * DESIGN_SYSTEM.md §13.6–§13.7
 * Run MDS: compute 2D positions from agreement matrix via classical MDS
 * (eigendecomposition of double-centered distance matrix).
 * Suppressed when n_runs < 5 (CDA SME S3).
 */

import { useMemo } from 'react';
import '../styles/focus1.css';
import { useFocus1Data } from '../hooks/useFocus1Data';
import {
  RUN_DISTRIBUTION_DESCRIPTION,
  EMPTY_NO_MODEL_SELECTED,
  EMPTY_RUN_MAP_UNAVAILABLE,
  EMPTY_NO_FOCUS1_DATA,
} from '../copy/focus1';

// ===== Sequential color scale (same as SimilarityHeatmap, §13.6) =====
const HEATMAP_COLORS = [
  '#eaf0f8',  // seq-0
  '#b8cce4',  // seq-1
  '#6b9dc8',  // seq-2
  '#2e6da4',  // seq-3
  '#1a3a5c',  // seq-4
];

const HEATMAP_TEXT_SWITCH_THRESHOLD = 0.60;

function simToColor(sim: number): string {
  const idx = Math.min(4, Math.floor(sim * 5));
  return HEATMAP_COLORS[idx];
}

function simToTextColor(sim: number): string {
  return sim >= HEATMAP_TEXT_SWITCH_THRESHOLD ? '#ffffff' : '#000000';
}

// ===== Classical MDS (browser-side, small matrix ≤50×50) =====

/** Double-center a squared distance matrix. Modifies in place. */
function doubleCenterInPlace(D2: number[][], n: number): void {
  const rowMeans = D2.map((row) => row.reduce((s, v) => s + v, 0) / n);
  const totalMean = rowMeans.reduce((s, v) => s + v, 0) / n;

  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      D2[i][j] = -0.5 * (D2[i][j] - rowMeans[i] - rowMeans[j] + totalMean);
    }
  }
}

/**
 * Jacobi eigendecomposition for symmetric matrix.
 * Returns { eigenvalues, eigenvectors } sorted descending by eigenvalue.
 * Adequate for n ≤ 50 (our max run count).
 */
function jacobiEigen(
  A: number[][],
  n: number,
  maxIter = 200,
): { eigenvalues: number[]; eigenvectors: number[][] } {
  // Copy A
  const a = A.map((row) => [...row]);

  // Initialise V as identity
  const v: number[][] = Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) => (i === j ? 1 : 0))
  );

  for (let iter = 0; iter < maxIter; iter++) {
    // Find largest off-diagonal element
    let maxVal = 0;
    let p = 0;
    let q = 1;
    for (let i = 0; i < n - 1; i++) {
      for (let j = i + 1; j < n; j++) {
        if (Math.abs(a[i][j]) > maxVal) {
          maxVal = Math.abs(a[i][j]);
          p = i;
          q = j;
        }
      }
    }
    if (maxVal < 1e-10) break;

    // Compute rotation
    const theta =
      Math.abs(a[p][p] - a[q][q]) < 1e-14
        ? Math.PI / 4
        : 0.5 * Math.atan2(2 * a[p][q], a[p][p] - a[q][q]);
    const c = Math.cos(theta);
    const s = Math.sin(theta);

    // Apply rotation to A
    const app = a[p][p];
    const aqq = a[q][q];
    const apq = a[p][q];
    a[p][p] = c * c * app + 2 * c * s * apq + s * s * aqq;
    a[q][q] = s * s * app - 2 * c * s * apq + c * c * aqq;
    a[p][q] = 0;
    a[q][p] = 0;
    for (let i = 0; i < n; i++) {
      if (i !== p && i !== q) {
        const aip = a[i][p];
        const aiq = a[i][q];
        a[i][p] = c * aip + s * aiq;
        a[p][i] = a[i][p];
        a[i][q] = -s * aip + c * aiq;
        a[q][i] = a[i][q];
      }
    }

    // Apply rotation to V
    for (let i = 0; i < n; i++) {
      const vip = v[i][p];
      const viq = v[i][q];
      v[i][p] = c * vip + s * viq;
      v[i][q] = -s * vip + c * viq;
    }
  }

  // Collect eigenvalues and sort descending
  const pairs = Array.from({ length: n }, (_, i) => ({
    eigenvalue: a[i][i],
    eigenvector: v.map((row) => row[i]),
  })).sort((x, y) => y.eigenvalue - x.eigenvalue);

  return {
    eigenvalues: pairs.map((p) => p.eigenvalue),
    eigenvectors: pairs.map((p) => p.eigenvector),
  };
}

/**
 * Classical MDS: given n×n agreement matrix, return n×2 coordinates.
 * Treats 1 - agreement as dissimilarity.
 */
function classicalMds2D(
  agreement: number[][],
): Array<[number, number]> | null {
  const n = agreement.length;
  if (n < 2) return null;

  // Squared dissimilarity matrix
  const D2 = agreement.map((row) =>
    row.map((a) => {
      const d = 1 - a;
      return d * d;
    })
  );

  doubleCenterInPlace(D2, n);

  const { eigenvalues, eigenvectors } = jacobiEigen(D2, n);

  // Take first 2 eigenvectors, scale by sqrt of eigenvalue (clamp negatives)
  const coords: Array<[number, number]> = Array.from({ length: n }, () => [0, 0]);
  for (let dim = 0; dim < 2; dim++) {
    const ev = eigenvalues[dim];
    const scale = ev > 0 ? Math.sqrt(ev) : 0;
    for (let i = 0; i < n; i++) {
      coords[i][dim] = eigenvectors[dim][i] * scale;
    }
  }

  return coords;
}

interface Focus1RunDistributionProps {
  domainSlug: string;
  selectedModelId: string | null;
}

function shortModelName(modelId: string): string {
  return modelId
    .replace(/^claude-/, '')
    .replace(/^gpt-/, 'gpt-')
    .replace(/^gemini-/, 'gemini-')
    .replace(/^meta-llama\//, '')
    .replace(/^mistralai\//, '')
    .split('/').pop() || modelId;
}

export function Focus1RunDistribution({
  domainSlug,
  selectedModelId,
}: Focus1RunDistributionProps) {
  const { data, loading, error } = useFocus1Data(domainSlug);

  const modelData = selectedModelId && data ? data[selectedModelId] : null;

  // Compute run MDS coords (memoized so it doesn't recompute on every render)
  const runCoords = useMemo(() => {
    if (!modelData || modelData.n_runs < 5) return null;
    const mat = modelData.run_agreement_matrix;
    if (!mat || mat.length < 5) return null;
    return classicalMds2D(mat);
  }, [modelData]);

  if (loading) {
    return <div className="f1-loading">Loading run distribution data…</div>;
  }
  if (error || !data) {
    return <div className="f1-empty">{EMPTY_NO_FOCUS1_DATA}</div>;
  }
  if (!selectedModelId) {
    return <div className="f1-empty">{EMPTY_NO_MODEL_SELECTED}</div>;
  }
  if (!modelData) {
    return <div className="f1-empty">No data available for the selected model.</div>;
  }

  const { run_agreement_matrix: mat, run_summaries, n_runs, centroid_run_id } = modelData;

  // Build run index → run_id mapping from summaries
  const runIds: string[] = run_summaries.map((s) => s.run_id);
  const nRuns = runIds.length || n_runs;

  // Run heatmap rendering
  const CELL_SIZE = Math.max(14, Math.min(28, Math.floor(480 / Math.max(nRuns, 1))));
  const HEADER_SIZE = 70;
  const ROW_LABEL_WIDTH = 52;
  const PAD = 2;
  const heatmapW = ROW_LABEL_WIDTH + nRuns * CELL_SIZE + PAD;
  const heatmapH = HEADER_SIZE + nRuns * CELL_SIZE + PAD;

  return (
    <div className="f1-container">
      <h3 className="f1-model-heading">{shortModelName(selectedModelId)}</h3>
      <p className="f1-desc">{RUN_DISTRIBUTION_DESCRIPTION}</p>

      <div className="f1-run-layout">
        {/* Run agreement heatmap */}
        <div>
          <p className="f1-section-heading">Run agreement heatmap</p>
          <div className="f1-heatmap-wrap">
            {mat && mat.length > 0 ? (
              <svg
                width="100%"
                viewBox={`0 0 ${heatmapW} ${heatmapH}`}
                role="img"
                aria-label="Run-by-run agreement heatmap"
                className="similarity-heatmap__svg"
              >
                {/* Column headers */}
                {runIds.map((rid, ci) => {
                  const cx = ROW_LABEL_WIDTH + ci * CELL_SIZE + CELL_SIZE / 2;
                  const cy = HEADER_SIZE - 4;
                  return (
                    <text
                      key={`col-${rid}`}
                      x={cx}
                      y={cy}
                      transform={`rotate(-45, ${cx}, ${cy})`}
                      textAnchor="start"
                      dominantBaseline="auto"
                      className="similarity-heatmap__col-header"
                      fontSize={Math.min(9, CELL_SIZE - 2)}
                    >
                      {`Run ${ci + 1}`}
                    </text>
                  );
                })}

                {/* Rows */}
                {runIds.map((rowRid, ri) => {
                  const ry = HEADER_SIZE + ri * CELL_SIZE;
                  return (
                    <g key={`row-${rowRid}`}>
                      <text
                        x={ROW_LABEL_WIDTH - 3}
                        y={ry + CELL_SIZE / 2}
                        dominantBaseline="middle"
                        textAnchor="end"
                        className="similarity-heatmap__row-label"
                        fontSize={Math.min(9, CELL_SIZE - 2)}
                      >
                        {`Run ${ri + 1}`}
                      </text>
                      {runIds.map((colRid, ci) => {
                        const sim = mat[ri]?.[ci] ?? 0;
                        const cellColor = simToColor(sim);
                        const textColor = simToTextColor(sim);
                        const cx = ROW_LABEL_WIDTH + ci * CELL_SIZE;
                        return (
                          <g key={`cell-${rowRid}-${colRid}`}>
                            <rect
                              x={cx}
                              y={ry}
                              width={CELL_SIZE}
                              height={CELL_SIZE}
                              fill={cellColor}
                              stroke="var(--color-border)"
                              strokeWidth={0.5}
                              aria-label={`Run ${ri + 1} vs Run ${ci + 1}: ${sim.toFixed(2)}`}
                            />
                            {CELL_SIZE >= 14 && (
                              <text
                                x={cx + CELL_SIZE / 2}
                                y={ry + CELL_SIZE / 2}
                                dominantBaseline="middle"
                                textAnchor="middle"
                                fill={textColor}
                                className="similarity-heatmap__cell-value"
                                fontSize={Math.min(9, CELL_SIZE - 7)}
                              >
                                {sim === 1 ? '1.0' : sim.toFixed(2).replace(/^0/, '')}
                              </text>
                            )}
                          </g>
                        );
                      })}
                    </g>
                  );
                })}
              </svg>
            ) : (
              <div className="f1-empty">Run agreement data not available.</div>
            )}
          </div>
        </div>

        {/* Run MDS scatter (§13.7) */}
        {n_runs >= 5 ? (
          <div className="f1-mds-wrap">
            <p className="f1-section-heading">Run map</p>
            {runCoords ? (
              <RunMdsScatter
                coords={runCoords}
                runSummaries={run_summaries}
                centroidRunId={centroid_run_id}
              />
            ) : (
              <div className="f1-suppressed-msg">Run map data unavailable.</div>
            )}
          </div>
        ) : (
          <div className="f1-suppressed-msg">
            {EMPTY_RUN_MAP_UNAVAILABLE(n_runs)}
          </div>
        )}
      </div>
    </div>
  );
}

// ===== Run MDS Scatter sub-component =====

const SCATTER_SEQ_COLORS = [
  '#eaf0f8',
  '#b8cce4',
  '#6b9dc8',
  '#2e6da4',
  '#1a3a5c',
];

function centralityToColor(loading: number, min: number, max: number): string {
  if (max === min) return SCATTER_SEQ_COLORS[2];
  const t = (loading - min) / (max - min);
  const idx = Math.min(4, Math.floor(t * 5));
  return SCATTER_SEQ_COLORS[idx];
}

interface RunMdsScatterProps {
  coords: Array<[number, number]>;
  runSummaries: Array<{
    run_id: string;
    run_index: number;
    centrality_loading: number;
    n_piles: number;
  }>;
  centroidRunId: string;
}

function RunMdsScatter({ coords, runSummaries, centroidRunId }: RunMdsScatterProps) {
  const n = coords.length;
  if (n === 0) return null;

  const xs = coords.map((c) => c[0]);
  const ys = coords.map((c) => c[1]);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);

  const W = 320;
  const H = 280;
  const MARGIN = 32;
  const plotW = W - 2 * MARGIN;
  const plotH = H - 2 * MARGIN;

  const xRange = maxX - minX || 1;
  const yRange = maxY - minY || 1;

  function toSvgX(x: number) {
    return MARGIN + ((x - minX) / xRange) * plotW;
  }
  function toSvgY(y: number) {
    return MARGIN + plotH - ((y - minY) / yRange) * plotH;
  }

  const loadings = runSummaries.map((s) => s.centrality_loading);
  const minLoad = Math.min(...loadings);
  const maxLoad = Math.max(...loadings);

  return (
    <svg
      width={W}
      height={H}
      viewBox={`0 0 ${W} ${H}`}
      role="img"
      aria-label="Run positions in 2D MDS space"
      className="f1-within-mds__svg"
    >
      {/* Axis labels */}
      <text
        x={W / 2}
        y={H - 4}
        textAnchor="middle"
        fontSize={9}
        fill="var(--color-text-caption)"
      >
        MDS Dimension 1
      </text>
      <text
        x={8}
        y={H / 2}
        textAnchor="middle"
        fontSize={9}
        fill="var(--color-text-caption)"
        transform={`rotate(-90, 8, ${H / 2})`}
      >
        MDS Dimension 2
      </text>

      {/* Run points */}
      {runSummaries.map((summary, i) => {
        if (!coords[i]) return null;
        const cx = toSvgX(coords[i][0]);
        const cy = toSvgY(coords[i][1]);
        const color = centralityToColor(summary.centrality_loading, minLoad, maxLoad);
        const isCentroid = summary.run_id === centroidRunId;
        const r = 5;

        return (
          <g key={summary.run_id}>
            <circle
              cx={cx}
              cy={cy}
              r={r}
              fill={color}
              stroke="var(--color-text-primary)"
              strokeWidth={isCentroid ? 2 : 0.5}
              aria-label={`Run ${summary.run_index + 1}${isCentroid ? ' (centroid)' : ''}`}
            />
          </g>
        );
      })}
    </svg>
  );
}
