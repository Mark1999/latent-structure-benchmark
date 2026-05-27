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

  return (
    <svg
      width={W}
      height={H}
      viewBox={`0 0 ${W} ${H}`}
      role="img"
      aria-label="Within-model term MDS positions"
      className="f1-within-mds__svg"
    >
      {items.map((item) => {
        const cx = toSvgX(item.x);
        const cy = toSvgY(item.y);
        const stability = termStability[item.item] ?? 0;
        // Opacity scales with stability
        const opacity = 0.3 + stability * 0.7;
        const showLabel = labeledTerms.has(item.item);

        return (
          <g key={item.item}>
            <circle
              cx={cx}
              cy={cy}
              r={3}
              fill="var(--color-info)"
              fillOpacity={opacity}
              stroke="none"
              aria-label={`${item.item}: stability ${(stability * 100).toFixed(0)}%`}
            />
            {showLabel && (
              <text
                x={cx + 4}
                y={cy + 3}
                fontSize={7}
                fill="var(--color-text-secondary)"
                fillOpacity={opacity}
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
