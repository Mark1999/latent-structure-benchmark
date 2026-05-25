/**
 * ProviderTree — cascading provider/family/model checkboxes in the sidebar.
 */

import { useState } from 'react';
import type { PublishedModel } from '../data/types';

// Provider display mapping
const PROVIDER_META: Record<string, { name: string; color: string }> = {
  anthropic:  { name: 'Anthropic',  color: '#d97706' },
  openai:     { name: 'OpenAI',     color: '#10a37f' },
  google:     { name: 'Google',     color: '#4285f4' },
  meta:       { name: 'Meta',       color: '#0668e1' },
  xai:        { name: 'xAI',        color: '#1d1d1f' },
  mistral:    { name: 'Mistral',    color: '#f97316' },
  deepseek:   { name: 'DeepSeek',   color: '#0ea5e9' },
  microsoft:  { name: 'Microsoft',  color: '#00a4ef' },
};

const PROVIDER_ORDER = [
  'anthropic', 'openai', 'google', 'meta', 'xai', 'mistral', 'deepseek', 'microsoft',
];

// Map OpenRouter models to their display provider
function displayProvider(model: PublishedModel): string {
  if (model.provider === 'openrouter') {
    const map: Record<string, string> = {
      gpt:       'openai',
      llama:     'meta',
      mistral:   'mistral',
      deepseek:  'deepseek',
      phi:       'microsoft',
    };
    return map[model.family] || model.provider;
  }
  return model.provider;
}

function shortDate(d: string): string {
  if (!d) return '';
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const parts = d.split('-');
  return `${months[parseInt(parts[1], 10) - 1]} '${parts[0].slice(2)}`;
}

function shortModelName(modelId: string): string {
  // Strip common provider prefixes for display
  return modelId
    .replace(/^claude-/, '')
    .replace(/^gpt-/, 'gpt-')
    .replace(/^gemini-/, 'gemini-')
    .replace(/^llama-/, 'llama-')
    .replace(/^grok-/, 'grok-')
    .replace(/^mistral-/, '')
    .replace(/^deepseek-/, 'ds-')
    .replace(/^phi-/, 'phi-')
    .replace(/^meta-llama\//, '')
    .replace(/^mistralai\//, '');
}

// SVG icons
const CHEVRON_SVG = (
  <svg className="provider-group__chevron" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
    <path d="M6 4l4 4-4 4"/>
  </svg>
);

const CHECK_SVG = (
  <svg viewBox="0 0 12 12" fill="none" stroke="white" strokeWidth="2" aria-hidden="true" style={{ width: 9, height: 9 }}>
    <path d="M2 6l3 3 5-5"/>
  </svg>
);

interface ProviderTreeProps {
  models: PublishedModel[];
  selected: Set<string>;
  onToggleModel: (id: string) => void;
  onToggleProvider: (provider: string) => void;
  pinnedProvider: string | null;
  onTogglePin: (provider: string) => void;
  openWeightsOnly: boolean;
}

export function ProviderTree({
  models,
  selected,
  onToggleModel,
  onToggleProvider,
  pinnedProvider,
  onTogglePin,
  openWeightsOnly,
}: ProviderTreeProps) {
  // Track which providers are expanded; default open first provider
  const [expanded, setExpanded] = useState<Set<string>>(() => {
    const firstProvider = models.length > 0 ? displayProvider(models[0]) : '';
    return new Set([firstProvider]);
  });

  const toggleExpand = (pid: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(pid)) next.delete(pid);
      else next.add(pid);
      return next;
    });
  };

  // Group models by display provider, then by family
  const providerMap: Record<string, Record<string, PublishedModel[]>> = {};
  models.forEach((m) => {
    const pid = displayProvider(m);
    if (!providerMap[pid]) providerMap[pid] = {};
    if (!providerMap[pid][m.family]) providerMap[pid][m.family] = [];
    providerMap[pid][m.family].push(m);
  });

  // Filter by openWeightsOnly if set
  const filteredProviderMap: Record<string, Record<string, PublishedModel[]>> = {};
  Object.entries(providerMap).forEach(([pid, families]) => {
    const filteredFamilies: Record<string, PublishedModel[]> = {};
    Object.entries(families).forEach(([fam, ms]) => {
      const filtered = openWeightsOnly ? ms.filter((m) => m.open_weights) : ms;
      if (filtered.length > 0) filteredFamilies[fam] = filtered;
    });
    if (Object.keys(filteredFamilies).length > 0) filteredProviderMap[pid] = filteredFamilies;
  });

  return (
    <>
      {PROVIDER_ORDER.filter((pid) => filteredProviderMap[pid]).map((pid) => {
        const meta = PROVIDER_META[pid] || { name: pid, color: '#888' };
        const allModels = Object.values(filteredProviderMap[pid]).flat();
        const isOpen = expanded.has(pid);
        const allSelected = allModels.every((m) => selected.has(m.model_id));
        const isPinned = pinnedProvider === pid;

        return (
          <div
            key={pid}
            className={`provider-group${isOpen ? ' provider-group--open' : ''}`}
          >
            <button
              className="provider-group__header"
              onClick={() => toggleExpand(pid)}
              aria-expanded={isOpen}
              aria-label={`${meta.name} models`}
            >
              {CHEVRON_SVG}
              <span
                className="provider-group__dot"
                style={{ background: meta.color }}
                aria-hidden="true"
              />
              <span className="provider-group__name">{meta.name}</span>
              <span className="provider-group__count">{allModels.length}</span>
              <button
                className={`provider-group__pin${isPinned ? ' provider-group__pin--on' : ''}`}
                title="Pin for comparison"
                aria-label={`${isPinned ? 'Unpin' : 'Pin'} ${meta.name} for comparison`}
                onClick={(e) => { e.stopPropagation(); onTogglePin(pid); }}
              >
                <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ width: 11, height: 11 }} aria-hidden="true">
                  <path d="M8 2v8M5 4l3-2 3 2M6 10h4M8 10v4"/>
                </svg>
              </button>
              <div
                className={`provider-group__checkbox${allSelected ? ' provider-group__checkbox--on' : ''}`}
                role="checkbox"
                aria-checked={allSelected}
                aria-label={`${allSelected ? 'Deselect' : 'Select'} all ${meta.name} models`}
                tabIndex={0}
                onClick={(e) => { e.stopPropagation(); onToggleProvider(pid); }}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.stopPropagation(); onToggleProvider(pid); } }}
              >
                {allSelected && CHECK_SVG}
              </div>
            </button>

            <div className="provider-group__models" aria-hidden={!isOpen}>
              {Object.entries(filteredProviderMap[pid]).map(([fam, ms]) => (
                <div key={fam}>
                  <div className="model-family-label">{fam}</div>
                  {ms.map((m) => {
                    const isSel = selected.has(m.model_id);
                    return (
                      <div
                        key={m.model_id}
                        className={`model-row${isSel ? ' model-row--selected' : ''}`}
                        onClick={() => onToggleModel(m.model_id)}
                        role="checkbox"
                        aria-checked={isSel}
                        aria-label={m.model_id}
                        tabIndex={0}
                        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') onToggleModel(m.model_id); }}
                      >
                        <div className={`model-row__checkbox${isSel ? ' model-row--selected' : ''}`} aria-hidden="true">
                          {isSel && CHECK_SVG}
                        </div>
                        <span className="model-row__name" title={m.model_id}>
                          {shortModelName(m.model_id)}
                        </span>
                        {m.open_weights && (
                          <span className="model-row__badge">Open</span>
                        )}
                        <span className="model-row__date">{shortDate(m.release_date)}</span>
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </>
  );
}
