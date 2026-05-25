/**
 * PileStructure — shows each model's pile-sort groupings:
 * what categories each model created and what terms are in each.
 *
 * Data source: centroid_piles field in domain JSON.
 */

import type { PublishedModel } from '../data/types';
import type { ModelPileData } from './TermMap';

interface PileStructureProps {
  centroidPiles: Record<string, ModelPileData>;
  models: PublishedModel[];
  selectedModelIds: Set<string>;
}

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
  const visibleModels = models.filter((m) => selectedModelIds.has(m.model_id));

  if (visibleModels.length === 0) {
    return (
      <div className="pile-empty">
        No models selected.
      </div>
    );
  }

  return (
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

        const { piles, labels } = pileData;

        // Build pile+label pairs, sort largest pile first
        const pileEntries = piles.map((pile, idx) => ({
          pile,
          label: labels[idx] ?? `Pile ${idx + 1}`,
        }));
        pileEntries.sort((a, b) => b.pile.length - a.pile.length);

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
              {pileEntries.map(({ pile, label }, groupIdx) => (
                <div
                  key={groupIdx}
                  className="pile-group"
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
                    {pile.join(', ')}
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
