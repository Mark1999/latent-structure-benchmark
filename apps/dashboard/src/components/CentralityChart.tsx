/**
 * CentralityChart — ranked horizontal bar chart of per-model cultural centrality scores.
 *
 * Bars are sorted descending by score (highest at top). Bar fill uses the
 * PROVIDER_COLORS map. Responds to selectedModelIds — only shows bars for
 * selected models.
 */

// Provider display color map (mirrors ContentArea)
const PROVIDER_COLORS: Record<string, string> = {
  anthropic:  '#d97706',
  openai:     '#10a37f',
  google:     '#4285f4',
  meta:       '#0668e1',
  xai:        '#1d1d1f',
  mistral:    '#f97316',
  deepseek:   '#0ea5e9',
  microsoft:  '#00a4ef',
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
}

export function CentralityChart({
  centralityScores,
  models,
  selectedModelIds,
}: CentralityChartProps) {
  // Filter to selected models that have a score, then sort descending
  const entries = models
    .filter((m) => selectedModelIds.has(m.model_id) && centralityScores[m.model_id] != null)
    .map((m) => ({
      model_id: m.model_id,
      score: centralityScores[m.model_id],
      color: PROVIDER_COLORS[resolveProvider(m)] || '#888888',
    }))
    .sort((a, b) => b.score - a.score);

  if (entries.length === 0) {
    return (
      <div className="centrality-chart centrality-chart--empty">
        No models selected.
      </div>
    );
  }

  const BAR_HEIGHT = 20;
  const BAR_GAP = 8;
  const LABEL_WIDTH = 140;
  const SCORE_WIDTH = 48;
  const BAR_AREA = 260;
  const PADDING_TOP = 4;
  const PADDING_BOTTOM = 4;

  const maxScore = Math.max(...entries.map((e) => e.score));

  const svgHeight = PADDING_TOP + entries.length * (BAR_HEIGHT + BAR_GAP) - BAR_GAP + PADDING_BOTTOM;
  const svgWidth = LABEL_WIDTH + BAR_AREA + SCORE_WIDTH;

  return (
    <div className="centrality-chart">
      <svg
        className="centrality-chart__svg"
        width="100%"
        viewBox={`0 0 ${svgWidth} ${svgHeight}`}
        role="img"
        aria-label="Cultural centrality scores ranked bar chart"
      >
        {entries.map((entry, i) => {
          const y = PADDING_TOP + i * (BAR_HEIGHT + BAR_GAP);
          const barWidth = maxScore > 0 ? (entry.score / maxScore) * BAR_AREA : 0;
          const label = shortName(entry.model_id);

          return (
            <g key={entry.model_id} className="centrality-chart__row">
              {/* Model name label */}
              <text
                x={LABEL_WIDTH - 6}
                y={y + BAR_HEIGHT / 2}
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
                x={LABEL_WIDTH}
                y={y}
                width={barWidth}
                height={BAR_HEIGHT}
                fill={entry.color}
                className="centrality-chart__bar"
                aria-label={`${label}: ${entry.score.toFixed(3)}`}
              />

              {/* Score value */}
              <text
                x={LABEL_WIDTH + BAR_AREA + 6}
                y={y + BAR_HEIGHT / 2}
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
  );
}
