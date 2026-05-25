/**
 * FreeListCompare — side-by-side ranked term lists per model,
 * showing what terms each model produced and how salient they are.
 *
 * Data source: sutrop_csi field in domain JSON.
 */

import type { PublishedModel } from '../data/types';

export interface SutropCsiEntry {
  item: string;
  csi: number;
  f_mentions: number;
  n_runs: number;
  mean_position?: number;
}

interface FreeListCompareProps {
  sutropCsi: Record<string, SutropCsiEntry[]>;
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

const MAX_TERMS = 20;

export function FreeListCompare({
  sutropCsi,
  models,
  selectedModelIds,
}: FreeListCompareProps) {
  const visibleModels = models.filter((m) => selectedModelIds.has(m.model_id));

  if (visibleModels.length === 0) {
    return (
      <div className="freelist-empty">
        No models selected.
      </div>
    );
  }

  return (
    <div
      className="freelist-columns"
      role="region"
      aria-label="Free list comparison by model"
    >
      {visibleModels.map((model) => {
        const providerKey = displayProvider(model);
        const providerColor = PROVIDER_COLORS[providerKey] || '#888';
        const entries: SutropCsiEntry[] = sutropCsi[model.model_id] ?? [];
        const sorted = [...entries].sort((a, b) => b.csi - a.csi).slice(0, MAX_TERMS);
        const displayName = shortModelName(model.model_id);

        return (
          <div
            key={model.model_id}
            className="freelist-column"
            role="group"
            aria-label={`Free list for ${displayName}`}
          >
            {/* Column header */}
            <div
              className="freelist-column__header"
              style={{ borderTopColor: providerColor }}
            >
              <span
                className="freelist-column__dot"
                style={{ background: providerColor }}
                aria-hidden="true"
              />
              <span className="freelist-column__name" title={model.model_id}>
                {displayName}
              </span>
            </div>

            {/* Term list */}
            {sorted.length === 0 ? (
              <div className="freelist-empty-col">No data</div>
            ) : (
              <ol className="freelist-list" aria-label={`${displayName} terms by salience`}>
                {sorted.map((entry, idx) => (
                  <li key={entry.item} className="freelist-item">
                    <span className="freelist-item__rank" aria-hidden="true">
                      {idx + 1}
                    </span>
                    <span className="freelist-item__term">
                      {entry.item}
                    </span>
                    <div
                      className="freelist-item__bar-wrap"
                      aria-label={`CSI ${entry.csi.toFixed(2)}`}
                    >
                      <div
                        className="freelist-item__bar"
                        style={{
                          width: `${(entry.csi * 100).toFixed(1)}%`,
                          background: providerColor,
                          opacity: 0.3,
                        }}
                      />
                    </div>
                    <span className="freelist-item__count">
                      {entry.f_mentions}/{entry.n_runs}
                    </span>
                  </li>
                ))}
              </ol>
            )}
          </div>
        );
      })}
    </div>
  );
}
