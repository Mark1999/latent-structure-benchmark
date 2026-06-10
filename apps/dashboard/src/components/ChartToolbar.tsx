/**
 * ChartToolbar — unified compact toolbar for the Term Map VizTab.
 *
 * Renders the four consolidated controls specified in DESIGN_SYSTEM.md §3.1.1(b)(ii):
 *   1. Overlay category names selector (select)
 *   2. Show uncertainty ellipses toggle (checkbox, default: checked/ON)
 *   3. Show cluster labels toggle (checkbox, default: checked/ON)
 *   4. Magnifying lens toggle (checkbox, default: unchecked/OFF)
 *
 * Aria-label strings are verbatim from §3.1.1(b)(ii) — do NOT reword.
 * Visual chrome: background var(--color-surface), border-bottom 1px solid var(--color-border),
 * no top border, no box-shadow (DESIGN_SYSTEM.md v0.20.1, UI/UX gate TM-B).
 *
 * No internal state. All control values and change handlers are props.
 * Touch targets: min 44px height at <768px per WCAG 2.5.5 (enforced in chart-toolbar.css).
 *
 * Tokens used (all confirmed present in tokens.css — CLAUDE.md pitfall 15):
 *   --space-2, --space-4, --color-surface, --color-border, --color-text-primary,
 *   --font-body, --font-size-sm, --max-chart-width
 */

import '../styles/chart-toolbar.css';
import { displayModel } from '../lib/familyUtils';

interface ChartToolbarProps {
  /** Sorted list of model keys available for pile-label overlay */
  pileModelKeys: string[];
  /** Currently selected overlay model key (null = None) */
  overlayPileLabelKey: string | null;
  /** Called when the overlay selector changes */
  onOverlayPileLabelKeyChange: (key: string | null) => void;
  /** Whether uncertainty ellipses are shown (default: true) */
  showUncertainty: boolean;
  /** Called when the Show uncertainty checkbox changes */
  onShowUncertaintyChange: (v: boolean) => void;
  /** Whether cluster labels are shown (default: true) */
  showClusterLabels: boolean;
  /** Called when the Show cluster labels checkbox changes */
  onShowClusterLabelsChange: (v: boolean) => void;
  /** Whether the magnifying lens is enabled (default: false) */
  lensEnabled: boolean;
  /** Called to toggle the magnifying lens */
  onLensToggle: () => void;
  /** When true, the lens checkbox is disabled (zoomed in beyond k=1.02) */
  lensDisabledByZoom: boolean;
}

export function ChartToolbar({
  pileModelKeys,
  overlayPileLabelKey,
  onOverlayPileLabelKeyChange,
  showUncertainty,
  onShowUncertaintyChange,
  showClusterLabels,
  onShowClusterLabelsChange,
  lensEnabled,
  onLensToggle,
  lensDisabledByZoom,
}: ChartToolbarProps) {
  return (
    <div className="chart-toolbar">
      {/* Overlay category names selector */}
      <div className="chart-toolbar__group">
        <label className="chart-toolbar__label" htmlFor="chart-toolbar-overlay-select">
          Overlay category names
        </label>
        <select
          id="chart-toolbar-overlay-select"
          className="chart-toolbar__select"
          value={overlayPileLabelKey ?? '__none__'}
          onChange={(e) => {
            const v = e.target.value;
            onOverlayPileLabelKeyChange(v === '__none__' ? null : v);
          }}
          aria-label="Overlay category names"
        >
          {pileModelKeys.map((key) => (
            <option key={key} value={key}>
              {displayModel(key)}
            </option>
          ))}
          <option value="__none__">None</option>
        </select>
      </div>

      {/* Show uncertainty ellipses toggle */}
      <label className="chart-toolbar__checkbox-label">
        <input
          type="checkbox"
          className="chart-toolbar__checkbox"
          checked={showUncertainty}
          onChange={(e) => onShowUncertaintyChange(e.target.checked)}
          aria-label="Show uncertainty ellipses"
        />
        Show uncertainty
      </label>

      {/* Show cluster labels toggle */}
      <label className="chart-toolbar__checkbox-label">
        <input
          type="checkbox"
          className="chart-toolbar__checkbox"
          checked={showClusterLabels}
          onChange={(e) => onShowClusterLabelsChange(e.target.checked)}
          aria-label="Show cluster labels"
        />
        Show cluster labels
      </label>

      {/* Magnifying lens toggle — disabled when zoomed in (Q2 LOCKED §17) */}
      <label
        className={`chart-toolbar__checkbox-label${lensDisabledByZoom ? ' chart-toolbar__checkbox-label--disabled' : ''}`}
        title={lensDisabledByZoom ? 'Zoom out to 100% to use the magnifying lens' : 'Hover to magnify and separate crowded term labels'}
      >
        <input
          type="checkbox"
          className="chart-toolbar__checkbox"
          checked={lensEnabled && !lensDisabledByZoom}
          onChange={onLensToggle}
          disabled={lensDisabledByZoom}
          aria-label="Magnifying lens"
        />
        Magnifying lens
      </label>
    </div>
  );
}
