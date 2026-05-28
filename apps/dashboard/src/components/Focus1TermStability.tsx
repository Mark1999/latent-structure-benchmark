/**
 * Focus1TermStability — term stability list + within-model term MDS.
 *
 * DESIGN_SYSTEM.md §13.8
 * Dashed-border tier treatment mirrors §12.10 PileComparison.
 */

import '../styles/focus1.css';
import { useFocus1Data } from '../hooks/useFocus1Data';
import {
  TERM_STABILITY_DESCRIPTION,
  EMPTY_NO_MODEL_SELECTED,
  EMPTY_NO_STABILITY_DATA,
  EMPTY_NO_FOCUS1_DATA,
} from '../copy/focus1';
import type { WithinModelMdsItem } from '../data/types';

function shortModelName(modelId: string): string {
  return modelId
    .replace(/^claude-/, '')
    .replace(/^gpt-/, 'gpt-')
    .replace(/^gemini-/, 'gemini-')
    .replace(/^meta-llama\//, '')
    .replace(/^mistralai\//, '')
    .split('/').pop() || modelId;
}

interface Focus1TermStabilityProps {
  domainSlug: string;
  selectedModelId: string | null;
}

/**
 * Map stability score to CSS tier class name (§13.8).
 */
function stabilityTierClass(stability: number): string {
  if (stability >= 0.80) return 'f1-term-item--stable';
  if (stability >= 0.60) return 'f1-term-item--medium';
  return 'f1-term-item--low';
}

export function Focus1TermStability({
  domainSlug,
  selectedModelId,
}: Focus1TermStabilityProps) {
  const { data, loading, error } = useFocus1Data(domainSlug);

  if (loading) {
    return <div className="f1-loading">Loading term stability data…</div>;
  }
  if (error || !data) {
    return <div className="f1-empty">{EMPTY_NO_FOCUS1_DATA}</div>;
  }
  if (!selectedModelId) {
    return <div className="f1-empty">{EMPTY_NO_MODEL_SELECTED}</div>;
  }

  const modelData = data[selectedModelId];
  if (!modelData) {
    return <div className="f1-empty">No data available for the selected model.</div>;
  }

  const { centroid_piles, mds_within_model, n_runs } = modelData;

  if (!centroid_piles || !centroid_piles.term_stability) {
    return <div className="f1-empty">{EMPTY_NO_STABILITY_DATA}</div>;
  }

  // Sort terms by stability descending
  const termStability = centroid_piles.term_stability;
  const sorted = Object.entries(termStability).sort(([, a], [, b]) => b - a);

  return (
    <div className="f1-container">
      <h3 className="f1-model-heading">{shortModelName(selectedModelId)}</h3>
      <p className="f1-desc">{TERM_STABILITY_DESCRIPTION}</p>

      <div className="f1-term-layout">
        {/* Stability list */}
        <div className="f1-stability-list">
          <div className="f1-stability-list__header">
            <span className="f1-section-heading">Term stability</span>
          </div>

          <ul className="f1-term-list" aria-label="Terms sorted by stability descending">
            {sorted.map(([term, stability]) => {
              const runsCount = Math.round(stability * n_runs);
              const tierClass = stabilityTierClass(stability);

              return (
                <li
                  key={term}
                  className={`f1-term-item ${tierClass}`}
                  title={`${term}: stable in ${runsCount} of ${n_runs} runs (${(stability * 100).toFixed(0)}%)`}
                >
                  <span className="f1-term-item__name">{term}</span>
                  <span
                    className="f1-term-item__runs"
                    aria-label={`stable in ${runsCount} of ${n_runs} runs`}
                  >
                    {runsCount} of {n_runs} runs
                  </span>
                </li>
              );
            })}
          </ul>

          {/* Stability legend */}
          <div className="f1-stability-legend" aria-hidden="true">
            <div className="f1-stability-legend__item">
              <span
                className="f1-stability-legend__swatch"
                style={{ border: '1px solid var(--color-border)' }}
              />
              <span>≥80% of runs</span>
            </div>
            <div className="f1-stability-legend__item">
              <span
                className="f1-stability-legend__swatch"
                style={{ border: '1px dashed var(--color-border)' }}
              />
              <span>60–79%</span>
            </div>
            <div className="f1-stability-legend__item">
              <span
                className="f1-stability-legend__swatch"
                style={{ border: '1px dashed var(--color-text-secondary)' }}
              />
              <span>below 60%</span>
            </div>
          </div>
        </div>

        {/* Within-model term MDS (§13.8: display alongside stability list) */}
        {mds_within_model && mds_within_model.length > 0 && (
          <div className="f1-within-mds">
            <p className="f1-section-heading">Within-model term positions</p>
            <WithinModelTermMds
              items={mds_within_model}
              termStability={termStability}
            />
            <p className="f1-mds-footnote">
              Term positions from MDS of within-model co-occurrence across runs.
              Color intensity reflects term stability.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

// ===== Within-model term MDS sub-component =====

interface WithinModelTermMdsProps {
  items: WithinModelMdsItem[];
  termStability: Record<string, number>;
}

function WithinModelTermMds({ items, termStability }: WithinModelTermMdsProps) {
  if (items.length === 0) return null;

  const xs = items.map((t) => t.x);
  const ys = items.map((t) => t.y);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);

  const W = 400;
  const H = 340;
  const MARGIN = 24;
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

  // Only show top-stability terms with labels (too many to label all)
  const TOP_LABELED = 30;
  const sortedByStability = [...items].sort(
    (a, b) => (termStability[b.item] ?? 0) - (termStability[a.item] ?? 0)
  );
  const labeledTerms = new Set(sortedByStability.slice(0, TOP_LABELED).map((t) => t.item));

  const positionedItems = items.map((item) => ({
    item: item.item,
    cx: toSvgX(item.x),
    cy: toSvgY(item.y),
    stability: termStability[item.item] ?? 0,
    showLabel: labeledTerms.has(item.item),
  }));

  // Greedy compass label offset algorithm to prevent overlaps
  const labelLayouts: Record<string, { x: number; y: number; anchor: 'start' | 'middle' | 'end' }> = {};
  const placedBoxes: { x1: number; x2: number; y1: number; y2: number }[] = [];

  const DIRECTIONS: {
    anchor: 'start' | 'middle' | 'end';
    dx: number;
    dy: number;
    bx: (cx: number, w: number) => number;
    by: (cy: number, h: number) => number;
  }[] = [
    { anchor: 'start',  dx: 5,   dy: 2,   bx: (cx) => cx + 5,      by: (cy) => cy - 4 },    // E
    { anchor: 'start',  dx: 4,   dy: 6,   bx: (cx) => cx + 4,      by: (cy) => cy },        // SE
    { anchor: 'middle', dx: 0,   dy: 8,   bx: (cx, w) => cx - w / 2,   by: (cy) => cy + 2 },    // S
    { anchor: 'end',    dx: -4,  dy: 6,   bx: (cx, w) => cx - 4 - w,   by: (cy) => cy },        // SW
    { anchor: 'end',    dx: -5,  dy: 2,   bx: (cx, w) => cx - 5 - w,   by: (cy) => cy - 4 },    // W
    { anchor: 'end',    dx: -4,  dy: -2,  bx: (cx, w) => cx - 4 - w,   by: (cy) => cy - 8 },    // NW
    { anchor: 'middle', dx: 0,   dy: -5,  bx: (cx, w) => cx - w / 2,   by: (cy) => cy - 11 },   // N
    { anchor: 'start',  dx: 4,   dy: -2,  bx: (cx) => cx + 4,      by: (cy) => cy - 8 },    // NE
  ];

  // Sort labeled terms by stability descending to place most stable labels first
  const sortedLabeledItems = positionedItems
    .filter((pi) => pi.showLabel)
    .sort((a, b) => b.stability - a.stability);

  sortedLabeledItems.forEach((pi) => {
    const { cx, cy, item: name } = pi;
    const fontSize = 7;
    const w = name.length * 3.8; // approx char width
    const h = fontSize;

    let bestDirIdx = 0;
    let minPenalty = Infinity;

    for (let k = 0; k < DIRECTIONS.length; k++) {
      const dir = DIRECTIONS[k];
      const bx1 = dir.bx(cx, w);
      const bx2 = bx1 + w;
      const by1 = dir.by(cy, h);
      const by2 = by1 + h;

      let penalty = 0;

      // Penalty 1: overlap with already placed label boxes
      for (let j = 0; j < placedBoxes.length; j++) {
        const pb = placedBoxes[j];
        const xOverlap = Math.max(0, Math.min(bx2, pb.x2) - Math.max(bx1, pb.x1));
        const yOverlap = Math.max(0, Math.min(by2, pb.y2) - Math.max(by1, pb.y1));
        if (xOverlap > 0 && yOverlap > 0) {
          penalty += xOverlap * yOverlap * 10;
        }
      }

      // Penalty 2: overlap with any other dots
      positionedItems.forEach((other) => {
        if (other.item === name) return;
        if (
          other.cx >= bx1 - 3 &&
          other.cx <= bx2 + 3 &&
          other.cy >= by1 - 3 &&
          other.cy <= by2 + 3
        ) {
          penalty += 150;
        }
      });

      // Penalty 3: out of bounds
      if (bx1 < 4 || bx2 > W - 4 || by1 < 4 || by2 > H - 4) {
        penalty += 200;
      }

      // Slight preference for first directions
      penalty += k * 0.5;

      if (penalty < minPenalty) {
        minPenalty = penalty;
        bestDirIdx = k;
      }
    }

    const bestDir = DIRECTIONS[bestDirIdx];
    const lx = cx + bestDir.dx;
    const ly = cy + bestDir.dy;

    labelLayouts[name] = { x: lx, y: ly, anchor: bestDir.anchor };
    placedBoxes.push({
      x1: bestDir.bx(cx, w),
      x2: bestDir.bx(cx, w) + w,
      y1: bestDir.by(cy, h),
      y2: bestDir.by(cy, h) + h,
    });
  });

  return (
    <svg
      width={W}
      height={H}
      viewBox={`0 0 ${W} ${H}`}
      role="img"
      aria-label="Within-model term MDS positions"
      className="f1-within-mds__svg"
    >
      {positionedItems.map((item) => {
        const layout = labelLayouts[item.item];
        const opacity = 0.3 + item.stability * 0.7;

        return (
          <g key={item.item}>
            <circle
              cx={item.cx}
              cy={item.cy}
              r={3}
              fill="var(--color-info)"
              fillOpacity={opacity}
              stroke="none"
              aria-label={`${item.item}: stability ${(item.stability * 100).toFixed(0)}%`}
            />
            {item.showLabel && layout && (
              <text
                x={layout.x.toFixed(1)}
                y={layout.y.toFixed(1)}
                textAnchor={layout.anchor}
                fontSize={7}
                fill="var(--color-text-secondary)"
                fillOpacity={opacity}
                style={{ pointerEvents: 'none' }}
              >
                {item.item}
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}
