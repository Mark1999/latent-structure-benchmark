/**
 * Timeline — version history for the active provider, with pin-for-comparison.
 */

import { useState } from 'react';

// Provider color map (matches ProviderTree)
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

const PROVIDER_NAMES: Record<string, string> = {
  anthropic:  'Claude',
  openai:     'GPT',
  google:     'Gemini',
  meta:       'Llama',
  xai:        'Grok',
  mistral:    'Mistral',
  deepseek:   'DeepSeek',
  microsoft:  'Phi',
};

// Derive timeline stops from model list
// Each model is a "stop" in that provider's version history
interface TimelineStop {
  name: string;
  date: string;
  position: string; // percentage left
  isLatest: boolean;
}

function buildStops(
  modelIds: string[],
  releaseDates: Record<string, string>
): TimelineStop[] {
  if (modelIds.length === 0) return [];
  if (modelIds.length === 1) {
    return [{
      name: modelIds[0].replace(/^[a-z]+-/, ''),
      date: releaseDates[modelIds[0]] || '',
      position: '50%',
      isLatest: true,
    }];
  }

  // Sort by release date
  const sorted = [...modelIds].sort((a, b) => {
    const da = releaseDates[a] || '1970-01-01';
    const db = releaseDates[b] || '1970-01-01';
    return da.localeCompare(db);
  });

  const n = sorted.length;
  return sorted.map((id, i) => ({
    name: id.split('/').pop()?.replace(/^[a-z]+-/, '') || id,
    date: releaseDates[id] || '',
    position: n === 1 ? '50%' : `${(i / (n - 1)) * 80 + 10}%`,
    isLatest: i === n - 1,
  }));
}

interface TimelineProps {
  activeProvider: string | null;
  providerModels: Record<string, Array<{ model_id: string; release_date: string }>>;
  pinnedProvider?: string | null;
  onTogglePin?: (provider: string) => void;
}

export function Timeline({
  activeProvider,
  providerModels,
}: TimelineProps) {
  const [selectedStops, setSelectedStops] = useState<Set<string>>(new Set());

  const toggleStop = (name: string) => {
    setSelectedStops((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  };

  const hasActive = activeProvider && providerModels[activeProvider]?.length > 0;

  return (
    <div className="timeline" aria-label="Version history timeline">
      <div className="timeline__header">
        <span className="timeline__label">Version History</span>
        {hasActive && activeProvider && (
          <div className="timeline__family">
            <span
              className="timeline__family-dot"
              style={{ background: PROVIDER_COLORS[activeProvider] || '#888' }}
              aria-hidden="true"
            />
            {PROVIDER_NAMES[activeProvider] || activeProvider}
          </div>
        )}
        {!hasActive && (
          <span className="timeline__hint">Expand a provider to see its history</span>
        )}
      </div>

      {hasActive && activeProvider && (() => {
        const models = providerModels[activeProvider] || [];
        const releaseDates: Record<string, string> = {};
        models.forEach((m) => { releaseDates[m.model_id] = m.release_date; });
        const stops = buildStops(models.map((m) => m.model_id), releaseDates);
        const color = PROVIDER_COLORS[activeProvider] || '#888';

        if (stops.length === 0) return null;

        const firstPos = stops[0].position;
        const lastPos = stops[stops.length - 1].position;

        return (
          <div className="timeline__track">
            <div className="timeline__rail" />
            <div
              className="timeline__fill"
              style={{
                left: firstPos,
                width: `calc(${lastPos} - ${firstPos})`,
                background: color,
                opacity: 0.25,
              }}
            />
            {stops.map((stop) => {
              const isSel = selectedStops.has(stop.name);
              return (
                <div
                  key={stop.name}
                  className={`timeline__stop${isSel ? ' timeline__stop--selected' : ''}`}
                  style={{ left: stop.position }}
                  onClick={() => toggleStop(stop.name)}
                  role="button"
                  aria-pressed={isSel}
                  aria-label={`${stop.name} — ${stop.date}`}
                >
                  <span className="timeline__stop-name">{stop.name}</span>
                  <div className="timeline__stop-dot" />
                  <span className="timeline__stop-date">{stop.date}</span>
                </div>
              );
            })}
          </div>
        );
      })()}
    </div>
  );
}
