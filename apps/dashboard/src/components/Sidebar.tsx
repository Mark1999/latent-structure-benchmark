/**
 * Sidebar — domain dropdown + ProviderTree + filters.
 * In Focus 1, the model-selection section is hidden (model selection
 * happens via the ranked card list inside Focus1SelfConsistencyOverview).
 */

import { ProviderTree } from './ProviderTree';
import type { PublishedModel } from '../data/types';
import type { ActiveFocus } from './VizTabs';

type DomainSlug = 'family' | 'holidays' | 'food';

const DOMAINS: Array<{ slug: DomainSlug; label: string }> = [
  { slug: 'family',   label: 'Family' },
  { slug: 'holidays', label: 'Holidays' },
  { slug: 'food',     label: 'Food' },
];

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
  /** Current focus level — used to hide model selection in Focus 1 */
  activeFocus?: ActiveFocus;
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
}: SidebarProps) {
  const isFocus1 = activeFocus === 'focus-1';

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

      {/* Providers & Models section — hidden in Focus 1 (model is selected via ranked card list) */}
      {!isFocus1 && (
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

      {/* Filters section — only show lens toggle in non-Focus-1 (lens applies to Term Map) */}
      <div className="sidebar__filters">
        <div className="sidebar__models-header">
          <span>Filters</span>
        </div>
        {!isFocus1 && (
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
      </div>
    </aside>
  );
}
