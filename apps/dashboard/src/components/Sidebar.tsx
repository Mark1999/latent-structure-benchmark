/**
 * Sidebar — domain dropdown + ProviderTree + filters.
 * In Focus 1, the model-selection section is hidden (model selection
 * happens via the ranked card list inside Focus1SelfConsistencyOverview).
 * In Focus 2, the provider family list is shown instead (§14.2).
 */

import { ProviderTree } from './ProviderTree';
import type { PublishedModel } from '../data/types';
import type { ActiveFocus } from './VizTabs';
import { groupModelsByProvider, getMultiModelFamilies, getSingleModelFamilies } from '../lib/familyUtils';

type DomainSlug = 'family' | 'holidays' | 'food';

const DOMAINS: Array<{ slug: DomainSlug; label: string }> = [
  { slug: 'family',   label: 'Family' },
  { slug: 'holidays', label: 'Holidays' },
  { slug: 'food',     label: 'Food' },
];

// Provider display colors — matches PROVIDER_COLORS in ContentArea and MDSPlot
const PROVIDER_DOT_COLORS: Record<string, string> = {
  anthropic:  '#d97706',
  openai:     '#10a37f',
  google:     '#4285f4',
  meta:       '#0668e1',
  xai:        '#1d1d1f',
  mistral:    '#f97316',
  deepseek:   '#0ea5e9',
  microsoft:  '#00a4ef',
};

interface SidebarProps {
  activeDomain: DomainSlug;
  onDomainChange: (slug: DomainSlug) => void;
  models: PublishedModel[];
  selected: Set<string>;
  onToggleModel: (id: string) => void;
  onToggleProvider: (provider: string) => void;
  onSelectAll: () => void;
  onSelectNone: () => void;
  pinnedProvider: string | null;
  onTogglePin: (provider: string) => void;
  openWeightsOnly: boolean;
  onOpenWeightsToggle: () => void;
  lensEnabled: boolean;
  onLensToggle: () => void;
  /** Current focus level — used to hide model selection in Focus 1/2 */
  activeFocus?: ActiveFocus;
  /** Selected provider family for Focus 2 */
  selectedProvider?: string | null;
  onSelectProvider?: (provider: string | null) => void;
}

export function Sidebar({
  activeDomain,
  onDomainChange,
  models,
  selected,
  onToggleModel,
  onToggleProvider,
  onSelectAll,
  onSelectNone,
  pinnedProvider,
  onTogglePin,
  openWeightsOnly,
  onOpenWeightsToggle,
  lensEnabled,
  onLensToggle,
  activeFocus,
  selectedProvider,
  onSelectProvider,
}: SidebarProps) {
  const isFocus1 = activeFocus === 'focus-1';
  const isFocus2 = activeFocus === 'focus-2';
  const hideModelControls = isFocus1 || isFocus2;

  // Focus 2: build provider groupings
  const grouping = isFocus2 ? groupModelsByProvider(models) : {};
  const multiModelFamilies = isFocus2 ? getMultiModelFamilies(grouping) : [];
  const singleModelFamilies = isFocus2 ? getSingleModelFamilies(grouping) : [];

  return (
    <aside className="sidebar" role="complementary" aria-label="Domain and model selection">
      {/* Domain section */}
      <div className="sidebar__domain">
        <label className="sidebar__section-label" htmlFor="domain-select">
          Domain
        </label>
        <select
          id="domain-select"
          className="domain-select"
          value={activeDomain}
          onChange={(e) => onDomainChange(e.target.value as DomainSlug)}
        >
          <optgroup label="Everyday">
            {DOMAINS.map(({ slug, label }) => (
              <option key={slug} value={slug}>{label}</option>
            ))}
          </optgroup>
          <optgroup label="Professional (soon)" disabled>
            <option disabled>Medical</option>
          </optgroup>
        </select>
      </div>

      {/* Focus 2: Provider family list */}
      {isFocus2 && (
        <div className="sidebar__models">
          <div className="sidebar__models-header">
            <span>Provider Families</span>
          </div>
          {selectedProvider ? (
            /* Detail mode: show selected family + back link */
            <div className="sidebar__f2-detail">
              <button
                className="sidebar__f2-back"
                onClick={() => onSelectProvider?.(null)}
              >
                ← All families
              </button>
              <div className="sidebar__f2-selected-name">
                <span
                  className="sidebar__f2-dot"
                  style={{ backgroundColor: PROVIDER_DOT_COLORS[selectedProvider] || '#888' }}
                />
                {selectedProvider.charAt(0).toUpperCase() + selectedProvider.slice(1)}
              </div>
              <div className="sidebar__f2-model-list">
                {(grouping[selectedProvider] || []).map((m) => (
                  <div key={m.model_id} className="sidebar__f2-model-item">
                    {m.model_id.split('/').pop() || m.model_id}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            /* List mode: all families */
            <div className="sidebar__f2-family-list">
              {multiModelFamilies.map((provider) => (
                <button
                  key={provider}
                  className={`sidebar__f2-family-row${selectedProvider === provider ? ' sidebar__f2-family-row--active' : ''}`}
                  onClick={() => onSelectProvider?.(provider)}
                >
                  <span
                    className="sidebar__f2-dot"
                    style={{ backgroundColor: PROVIDER_DOT_COLORS[provider] || '#888' }}
                  />
                  <span className="sidebar__f2-family-name">
                    {provider.charAt(0).toUpperCase() + provider.slice(1)}
                  </span>
                  <span className="sidebar__f2-count">
                    {grouping[provider]?.length ?? 0}
                  </span>
                </button>
              ))}
              {singleModelFamilies.length > 0 && (
                <>
                  <div className="sidebar__f2-section-divider">Single-model providers</div>
                  {singleModelFamilies.map((provider) => (
                    <div key={provider} className="sidebar__f2-family-row sidebar__f2-family-row--single">
                      <span
                        className="sidebar__f2-dot sidebar__f2-dot--muted"
                        style={{ backgroundColor: PROVIDER_DOT_COLORS[provider] || '#888' }}
                      />
                      <span className="sidebar__f2-family-name sidebar__f2-family-name--muted">
                        {provider.charAt(0).toUpperCase() + provider.slice(1)}
                      </span>
                      <span className="sidebar__f2-count sidebar__f2-count--muted">1</span>
                    </div>
                  ))}
                </>
              )}
            </div>
          )}
        </div>
      )}

      {/* Providers & Models section — hidden in Focus 1/2 */}
      {!hideModelControls && (
        <div className="sidebar__models">
          <div className="sidebar__models-header">
            <span>Providers &amp; Models</span>
            <span className="sidebar__models-count">
              {selected.size} of {models.length}
            </span>
          </div>
          <div className="sidebar__actions">
            <button className="sidebar__action-btn" onClick={onSelectAll}>
              Select all
            </button>
            <button className="sidebar__action-btn" onClick={onSelectNone}>
              Clear
            </button>
          </div>
          <ProviderTree
            models={models}
            selected={selected}
            onToggleModel={onToggleModel}
            onToggleProvider={onToggleProvider}
            pinnedProvider={pinnedProvider}
            onTogglePin={onTogglePin}
            openWeightsOnly={openWeightsOnly}
          />
        </div>
      )}

      <div className="sidebar__divider" aria-hidden="true" />

      {/* Filters section — only show controls in Focus 3 (lens applies to Term Map) */}
      <div className="sidebar__filters">
        <div className="sidebar__models-header">
          <span>Filters</span>
        </div>
        {!hideModelControls && (
          <>
            <div className="toggle-row">
              <span className="toggle-label" id="open-weights-label">
                Open weights only
              </span>
              <button
                className={`toggle${openWeightsOnly ? ' toggle--on' : ''}`}
                onClick={onOpenWeightsToggle}
                role="switch"
                aria-checked={openWeightsOnly}
                aria-labelledby="open-weights-label"
              >
                <span className="toggle__thumb" />
              </button>
            </div>
            <div className="toggle-row">
              <span className="toggle-label" id="lens-label">
                Magnifying lens
              </span>
              <button
                className={`toggle${lensEnabled ? ' toggle--on' : ''}`}
                onClick={onLensToggle}
                role="switch"
                aria-checked={lensEnabled}
                aria-labelledby="lens-label"
              >
                <span className="toggle__thumb" />
              </button>
            </div>
          </>
        )}
        {isFocus1 && (
          <p className="sidebar__focus1-hint">
            Select a model from the ranked list to explore its runs.
          </p>
        )}
        {isFocus2 && (
          <p className="sidebar__focus1-hint">
            Select a provider family from the list to compare its models.
          </p>
        )}
      </div>
    </aside>
  );
}
