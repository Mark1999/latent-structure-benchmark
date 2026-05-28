/**
 * PileStructure — shows each model's pile-sort groupings:
 * what categories each model created and what terms are in each.
 *
 * Data source: centroid_piles field in domain JSON.
 */

import { useState } from 'react';
import type { PublishedModel } from '../data/types';

interface ExtendedModelPileData {
  piles: string[][];
  labels: string[];
  term_stability?: Record<string, number>;
}

interface PileStructureProps {
  centroidPiles: Record<string, ExtendedModelPileData>;
  models: PublishedModel[];
  selectedModelIds: Set<string>;
}

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

function displayProvider(model: PublishedModel): string {
  if (model.provider === 'openrouter') {
    const map: Record<string, string> = {
      gpt:      'openai',
      llama:    'meta',
      mistral:  'mistral',
      deepseek: 'deepseek',
      phi:      'microsoft',
    };
    return map[model.family] || model.provider;
  }
  return model.provider;
}

function shortModelName(modelId: string): string {
  return modelId
    .replace(/^claude-/, '')
    .replace(/^google\//, '')
    .replace(/^meta-llama\//, '')
    .replace(/^mistralai\//, '')
    .replace(/^microsoft\//, '')
    .split('/').pop() || modelId;
}

export function PileStructure({
  centroidPiles,
  models,
  selectedModelIds,
}: PileStructureProps) {
  const [hoveredTerm, setHoveredTerm] = useState<string | null>(null);
  const visibleModels = models.filter((m) => selectedModelIds.has(m.model_id));

  if (visibleModels.length === 0) {
    return (
      <div className="pile-empty">
        No models selected.
      </div>
    );
  }

  return (
    <div style={{ width: '100%' }}>
      <div
        className="pile-columns"
        role="region"
        aria-label="Pile structure comparison by model"
      >
        {visibleModels.map((model) => {
          const providerKey = displayProvider(model);
          const providerColor = PROVIDER_COLORS[providerKey] || '#888';
          const pileData = centroidPiles[model.model_id];
          const displayName = shortModelName(model.model_id);

          if (!pileData) {
            return (
              <div
                key={model.model_id}
                className="pile-column"
                role="group"
                aria-label={`Pile structure for ${displayName}`}
              >
                <div
                  className="pile-column__header"
                  style={{ borderTopColor: providerColor }}
                >
                  <span
                    className="pile-column__dot"
                    style={{ background: providerColor }}
                    aria-hidden="true"
                  />
                  <span className="pile-column__name" title={model.model_id}>
                    {displayName}
                  </span>
                </div>
                <div className="pile-empty-col">No pile data</div>
              </div>
            );
          }

          const { piles, labels, term_stability } = pileData;

          // Build pile+label pairs, sort largest pile first
          const pileEntries = piles.map((pile, idx) => ({
            pile,
            label: labels[idx] ?? `Pile ${idx + 1}`,
          }));
          pileEntries.sort((a, b) => b.pile.length - a.pile.length);

          const hasHoveredTermAnywhere = hoveredTerm !== null && piles.some((p) => p.includes(hoveredTerm));

          return (
            <div
              key={model.model_id}
              className="pile-column"
              role="group"
              aria-label={`Pile structure for ${displayName}`}
            >
              {/* Column header */}
              <div
                className="pile-column__header"
                style={{ borderTopColor: providerColor }}
              >
                <span
                  className="pile-column__dot"
                  style={{ background: providerColor }}
                  aria-hidden="true"
                />
                <span className="pile-column__name" title={model.model_id}>
                  {displayName}
                </span>
                <span className="pile-column__count">
                  {piles.length} piles
                </span>
              </div>

              {/* Pile groups */}
              <div className="pile-list">
                {pileEntries.map(({ pile, label }, groupIdx) => {
                  const hasHoveredTerm = hoveredTerm !== null && pile.includes(hoveredTerm);
                  const isFirstAndAbsent = groupIdx === 0 && hoveredTerm !== null && !hasHoveredTermAnywhere;

                  return (
                    <div
                      key={groupIdx}
                      className={`pile-group${hasHoveredTerm ? ' pile-group--highlight' : ''}`}
                      role="group"
                      aria-label={`${label}: ${pile.length} terms`}
                    >
                      <div
                        className="pile-group__label"
                        style={{ color: providerColor }}
                      >
                        {label}
                        <span className="pile-group__size">({pile.length})</span>
                      </div>
                      <div className="pile-group__terms">
                        {pile.map((term) => {
                          const stability = term_stability?.[term] ?? 1.0;
                          const pct = Math.round(stability * 100);

                          let stabilityClass = 'pile-comparison__pill--stability-high';
                          if (stability < 0.6) {
                            stabilityClass = 'pile-comparison__pill--stability-low';
                          } else if (stability < 0.8) {
                            stabilityClass = 'pile-comparison__pill--stability-medium';
                          }

                          const isPillHovered = hoveredTerm === term;
                          const highlightClass = isPillHovered ? ' pile-comparison__pill--highlight' : '';

                          return (
                            <span
                              key={term}
                              className={`pile-comparison__pill ${stabilityClass}${highlightClass}`}
                              onMouseEnter={() => setHoveredTerm(term)}
                              onMouseLeave={() => setHoveredTerm(null)}
                              title={`Placed here in ${pct}% of runs for ${displayName}.`}
                              aria-label={`${term}: placed here in ${pct}% of runs for ${displayName}`}
                            >
                              {term}
                            </span>
                          );
                        })}

                        {/* Hover placeholder for absent terms */}
                        {isFirstAndAbsent && (
                          <span
                            className="pile-comparison__pill pile-comparison__pill--absent"
                            title={`This term was not produced by ${displayName} in this domain.`}
                            aria-label={`${hoveredTerm}: not produced by ${displayName}`}
                          >
                            {hoveredTerm} (absent)
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend Row */}
      <div className="pile-legend" aria-hidden="true">
        <span className="pile-legend__title">Term stability:</span>
        <span className="pile-legend__item">
          <span className="pile-comparison__pill pile-comparison__pill--stability-high">Term</span> ≥80% of runs
        </span>
        <span className="pile-legend__item">
          <span className="pile-comparison__pill pile-comparison__pill--stability-medium">Term</span> 60–79% of runs
        </span>
        <span className="pile-legend__item">
          <span className="pile-comparison__pill pile-comparison__pill--stability-low">Term</span> below 60% of runs
        </span>
      </div>
    </div>
  );
}
