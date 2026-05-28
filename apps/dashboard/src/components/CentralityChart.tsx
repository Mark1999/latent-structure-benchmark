/**
 * CentralityChart — ranked horizontal bar chart of per-model cultural centrality scores.
 */

import { useState, useMemo, useCallback, useRef } from 'react';
import { CentralityTable } from './CentralityTable';

const PROVIDER_COLORS: Record<string, string> = {
  anthropic:  'var(--color-provider-anthropic)',
  openai:     'var(--color-provider-openai)',
  google:     'var(--color-provider-google)',
  meta:       'var(--color-provider-meta)',
  xai:        'var(--color-provider-xai)',
  mistral:    'var(--color-provider-mistral)',
  deepseek:   'var(--color-provider-deepseek)',
  microsoft:  'var(--color-provider-microsoft)',
};

const FAMILY_TO_PROVIDER: Record<string, string> = {
  gpt:       'openai',
  llama:     'meta',
  mistral:   'mistral',
  deepseek:  'deepseek',
  phi:       'microsoft',
};

interface ModelRef {
  model_id: string;
  provider: string;
  family: string;
}

function resolveProvider(model: ModelRef): string {
  if (model.provider === 'openrouter') {
    return FAMILY_TO_PROVIDER[model.family] || model.provider;
  }
  return model.provider;
}

function shortName(id: string): string {
  return id.split('/').pop() || id;
}

export interface CentralityChartProps {
  centralityScores: Record<string, number>;
  models: Array<{ model_id: string; provider: string; family: string }>;
  selectedModelIds: Set<string>;
  consensusType?: string;
  domainSlug?: string;
}

interface TooltipState {
  modelId: string;
  screenX: number;
  screenY: number;
}

const BAR_HEIGHT = 20;
const BAR_GAP = 12;
const BAR_SLOT = BAR_HEIGHT + BAR_GAP; // 32px per bar
const LABEL_WIDTH = 140;
const SCORE_WIDTH = 110;
const BAR_AREA = 260;
const PADDING_TOP = 10;
const PADDING_BOTTOM = 20;

export function CentralityChart({
  centralityScores,
  models,
  selectedModelIds,
  consensusType = 'UNKNOWN',
  domainSlug = 'domain',
}: CentralityChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [readAsTable, setReadAsTable] = useState<boolean>(false);
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);

  // Filter and sort entries
  const entries = useMemo(() => {
    return models
      .filter((m) => selectedModelIds.has(m.model_id) && centralityScores[m.model_id] != null)
      .map((m) => ({
        model_id: m.model_id,
        score: centralityScores[m.model_id],
        color: PROVIDER_COLORS[resolveProvider(m)] || 'var(--color-text-secondary)',
      }))
      .sort((a, b) => b.score - a.score);
  }, [models, selectedModelIds, centralityScores]);

  // SVG dimensions
  const svgHeight = PADDING_TOP + entries.length * BAR_SLOT - BAR_GAP + PADDING_BOTTOM;
  const svgWidth = LABEL_WIDTH + BAR_AREA + SCORE_WIDTH;

  // Determine x domain: always include 0 and score values
  const { xMin, xMax } = useMemo(() => {
    const allValues = [0, ...entries.map((e) => e.score)];
    const minVal = Math.min(...allValues);
    const maxVal = Math.max(...allValues);
    const range = maxVal - minVal || 0.01;
    const padding = range * 0.1;
    return { xMin: minVal - padding, xMax: maxVal + padding };
  }, [entries]);

  // Scale functions
  const toSvgX = useCallback((v: number) => {
    return LABEL_WIDTH + ((v - xMin) / (xMax - xMin)) * BAR_AREA;
  }, [xMin, xMax]);

  const zeroX = toSvgX(0);

  const handleMouseMove = useCallback((modelId: string, e: React.MouseEvent) => {
    const rect = containerRef.current?.getBoundingClientRect();
    if (rect) {
      setTooltip({
        modelId,
        screenX: e.clientX - rect.left,
        screenY: e.clientY - rect.top,
      });
    }
  }, []);

  const handleMouseLeave = useCallback(() => {
    setTooltip(null);
  }, []);

  if (entries.length === 0) {
    return (
      <div className="centrality-chart centrality-chart--empty">
        No models selected.
      </div>
    );
  }

  // Visual text summary for screen readers
  const highestEntry = entries[0];
  const lowestEntry = entries[entries.length - 1];
  // TODO(Remedy B T4): remove the uncertainty-interval caveat when centrality_ci is consumed
  const srSummary = `This chart ranks ${entries.length} models by cultural centrality score on the ${domainSlug} domain. Higher scores indicate closer alignment with the group's dominant categorical pattern. ${shortName(highestEntry.model_id)} has the highest centrality at ${highestEntry.score.toFixed(3)}, and ${shortName(lowestEntry.model_id)} has the lowest at ${lowestEntry.score.toFixed(3)}. Note: no uncertainty interval is currently shown for these scores — see methodology.`;

  return (
    <div className="centrality-chart" ref={containerRef} style={{ position: 'relative' }}>
      {/* Screen Reader summary */}
      <p className="sr-only screen-reader-summary">{srSummary}</p>

      {/* Accessible table toggle */}
      <div className="read-as-table-toggle">
        <button
          type="button"
          className="read-as-table-toggle__button"
          aria-pressed={readAsTable}
          aria-controls="centrality-table-container"
          onClick={() => setReadAsTable(!readAsTable)}
        >
          {readAsTable ? 'Show visualization' : 'Read as table'}
        </button>
      </div>

      {/* Interim uncertainty annotation — TODO(Remedy B T4): remove when centrality_ci is consumed */}
      <p className="centrality-chart__interim-note" aria-hidden="true">
        No uncertainty interval currently shown — see methodology.
      </p>

      {/* SVG Bar Chart */}
      <div
        className="centrality-chart__svg-container"
        style={{ display: readAsTable ? 'none' : 'block' }}
        aria-hidden={readAsTable}
      >
        <svg
          className="centrality-chart__svg"
          width="100%"
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          role="img"
          aria-label={`Ranked bar chart of cultural centrality scores for selected models on the ${domainSlug} domain`}
        >
          {/* Zero Axis Line */}
          <line
            x1={zeroX}
            y1={0}
            x2={zeroX}
            y2={svgHeight - PADDING_BOTTOM}
            stroke="var(--color-border)"
            strokeWidth="1"
            aria-hidden="true"
          />

          {entries.map((entry, i) => {
            const y = PADDING_TOP + i * BAR_SLOT;
            const barCenter = y + BAR_HEIGHT / 2;
            const scoreX = toSvgX(entry.score);
            const barX = Math.min(zeroX, scoreX);
            const barW = Math.abs(scoreX - zeroX);
            const label = shortName(entry.model_id);

            return (
              <g
                key={entry.model_id}
                className="centrality-chart__row"
                onMouseMove={(e) => handleMouseMove(entry.model_id, e)}
                onMouseLeave={handleMouseLeave}
                style={{ cursor: 'pointer' }}
              >
                {/* Model name label */}
                <text
                  x={LABEL_WIDTH - 8}
                  y={barCenter}
                  dominantBaseline="middle"
                  textAnchor="end"
                  className="centrality-chart__label"
                >
                  {label}
                </text>

                {/* Bar background track */}
                <rect
                  x={LABEL_WIDTH}
                  y={y}
                  width={BAR_AREA}
                  height={BAR_HEIGHT}
                  className="centrality-chart__track"
                />

                {/* Filled bar */}
                <rect
                  x={barX}
                  y={y}
                  width={barW}
                  height={BAR_HEIGHT}
                  fill={entry.color}
                  className="centrality-chart__bar"
                  aria-label={`${label}: ${entry.score.toFixed(3)}`}
                />

                {/* Score value */}
                <text
                  x={scoreX + 6}
                  y={barCenter}
                  dominantBaseline="middle"
                  textAnchor="start"
                  className="centrality-chart__score"
                >
                  {entry.score.toFixed(3)}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Accessible Table */}
      <div
        id="centrality-table-container"
        style={{ display: readAsTable ? 'block' : 'none' }}
        aria-hidden={!readAsTable}
      >
        <CentralityTable
          domainSlug={domainSlug}
          consensusType={consensusType}
          sortedIds={entries.map((e) => e.model_id)}
          centralityScores={centralityScores}
        />
      </div>

      {/* Tooltip */}
      {!readAsTable && tooltip && (
        <div
          className="centrality-chart__tooltip"
          style={{
            position: 'absolute',
            left: tooltip.screenX + 12,
            top: tooltip.screenY - 10,
          }}
        >
          <div className="centrality-chart__tooltip-name">{shortName(tooltip.modelId)}</div>
          <div className="centrality-chart__tooltip-id">{tooltip.modelId}</div>
          <div className="centrality-chart__tooltip-score">
            Cultural Centrality: <strong>{centralityScores[tooltip.modelId]?.toFixed(3)}</strong>
          </div>
          <div className="centrality-chart__tooltip-explanation">
            Cultural centrality measures how closely a model&apos;s categorical structure aligns with the dominant pattern across all models in this domain. Higher scores indicate closer alignment.
          </div>
        </div>
      )}
    </div>
  );
}
