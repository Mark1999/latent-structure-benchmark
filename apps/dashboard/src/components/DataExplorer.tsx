/**
 * DataExplorer — T9 container component.
 *
 * Composes VizSwitcher + MDSPlot + ModelSelector + Legend into the full
 * explorer layout per DESIGN_SYSTEM.md §3.1.
 *
 * Ownership per §12.4 and UI/UX F-T6-2 carry-forward:
 *   - MODEL_PALETTE_SLOTS constant (moved here from App.tsx)
 *   - modelColors useMemo (moved here from App.tsx)
 *   - selectedModels state + domain-change reset effect (moved here from App.tsx)
 *   - activeVizTab state + handleVizTabChange (moved here from App.tsx)
 *
 * App.tsx passes only `domainResult`. DataExplorer manages all explorer-internal
 * state and distributes modelColors to MDSPlot, ModelSelector, and Legend.
 *
 * §3.7 v0.4.2 binding: initial selectedModels = first 6 model_ids by §12.4
 * lexicographic sort. Resets on domain change (i.e., whenever domainResult changes).
 *
 * No child component (MDSPlot, ModelSelector, Legend) computes its own
 * model color from model_id — all receive modelColors as a prop per §12.4
 * palette ownership rule.
 *
 * Source: DESIGN_SYSTEM.md §3.1, §3.7 (v0.4.2), §12.4
 * Reference: docs/status/2026-05-09-phase5-architect-plan.md §4 T9
 */

import { useEffect, useState, useMemo } from "react";
import type { DomainResultPublished } from "../data/types";
import { MDSPlot } from "./MDSPlot";
import { ModelSelector } from "./ModelSelector";
import { VizSwitcher, resolveFragmentOnMount } from "./VizSwitcher";
import type { ActiveVizTab } from "./VizSwitcher";

// ── Props ─────────────────────────────────────────────────────────────────────

export interface DataExplorerProps {
  domainResult: DomainResultPublished;
}

// ── Palette ───────────────────────────────────────────────────────────────────

/**
 * Model palette slot hex values, matching tokens.css §1.2 (v0.4.1).
 * Moved here from App.tsx at T9 per §12.4 palette ownership.
 * Assignment algorithm: §12.4 — sort model_ids ascending, assign slot 1…11.
 */
const MODEL_PALETTE_SLOTS: string[] = [
  "#3360a9", // --color-model-1
  "#c0392b", // --color-model-2
  "#e67e22", // --color-model-3
  "#27ae60", // --color-model-4
  "#8e44ad", // --color-model-5
  "#16a085", // --color-model-6
  "#d35400", // --color-model-7
  "#1a5276", // --color-model-8
  "#7d3c98", // --color-model-9
  "#148f77", // --color-model-10
  "#9a7d0a", // --color-model-11 (v0.4.1 corrected from #b7950b)
];

// ── Component ─────────────────────────────────────────────────────────────────

/**
 * DataExplorer renders the full interactive explorer area:
 *   VizSwitcher tab bar → MDSPlot (main area) → ModelSelector (right/below)
 *   → Legend (below plot, inside MDSPlot)
 *
 * All explorer-internal state lives here. App.tsx provides only domainResult.
 */
export function DataExplorer({ domainResult }: DataExplorerProps) {
  /**
   * selectedModels: which model_ids are currently visible on the plot.
   * §3.7 v0.4.2 binding: initial value = first 6 by §12.4 lexicographic sort.
   * Reset on domain change (domainResult identity changes when domain switches).
   */
  const [selectedModels, setSelectedModels] = useState<string[]>(() => {
    const rawCoords = domainResult.mds_coordinates as unknown as Record<string, [number, number]>;
    return Object.keys(rawCoords).sort().slice(0, 6);
  });

  /**
   * activeVizTab: which viz tab is active.
   * Phase 5: only "mds" is activatable. Reads URL fragment on mount.
   */
  const [activeVizTab, setActiveVizTab] = useState<ActiveVizTab>(
    () => resolveFragmentOnMount()
  );

  /**
   * Reset selectedModels to first-6 sorted whenever the domain changes.
   * §3.7 v0.4.2 initial-state binding: first 6 model_ids by §12.4 sort.
   * domainResult.domain_slug used as the dependency so the effect fires
   * on each domain switch.
   *
   * eslint set-state-in-effect: setting state in a useEffect that responds to
   * a prop/context change is the documented React pattern for derived resets
   * (https://react.dev/reference/react/useState#storing-information-from-previous-renders).
   * The alternative (calling setState in render) triggers an infinite loop here
   * because rawCoords reference changes on every render when domain data is fetched.
   */
  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    const rawCoords = domainResult.mds_coordinates as unknown as Record<string, [number, number]>;
    setSelectedModels(Object.keys(rawCoords).sort().slice(0, 6));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [domainResult.domain_slug]);
  /* eslint-enable react-hooks/set-state-in-effect */

  /**
   * Handle VizSwitcher tab activation. Phase 5: only "mds" is activatable.
   * Updates URL fragment to #mds and keeps local state in sync.
   */
  function handleVizTabChange(tab: ActiveVizTab): void {
    setActiveVizTab(tab);
    try {
      window.history.replaceState(null, "", `#${tab}`);
    } catch {
      // history API unavailable in some test environments — ignore.
    }
  }

  /**
   * Build modelColors per §12.4 algorithm:
   * Sort all model_ids ascending (lexicographic), assign palette slot 1…11.
   * Assignment is stable: same model_id always gets the same slot.
   * Ownership moved from App.tsx to DataExplorer.tsx at T9 per §12.4.
   *
   * Produces Record<model_id, cssColorValue> passed to MDSPlot, ModelSelector,
   * and Legend. No child computes its own color from model_id directly.
   */
  const modelColors = useMemo((): Record<string, string> => {
    const rawCoords = domainResult.mds_coordinates as unknown as Record<string, [number, number]>;
    const sortedIds = [...Object.keys(rawCoords)].sort();
    const colors: Record<string, string> = {};
    sortedIds.forEach((id, i) => {
      colors[id] = MODEL_PALETTE_SLOTS[i % MODEL_PALETTE_SLOTS.length];
    });
    return colors;
  }, [domainResult]);

  return (
    <div className="data-explorer">
      {/* VizSwitcher: tab bar at top of explorer per §3.1.
          §12.3: disabled tabs focusable, tooltip "Coming in a future update". */}
      <VizSwitcher
        activeTab={activeVizTab}
        onTabChange={handleVizTabChange}
      />

      {/* Explorer grid: MDSPlot left/center, ModelSelector right (desktop)
          or below (mobile) per §3.1 layout and app.css .explorer-layout. */}
      <div className="explorer-layout">
        <div className="explorer-layout__viz">
          {/* MDSPlot receives modelColors from DataExplorer — §12.4 palette
              ownership. Legend is rendered inside MDSPlot per T6/T7 design. */}
          <MDSPlot
            domainResult={domainResult}
            modelColors={modelColors}
            selectedModels={selectedModels}
          />
        </div>
        <div className="explorer-layout__selector">
          {/* ModelSelector receives modelColors from DataExplorer — §12.4. */}
          <ModelSelector
            domainResult={domainResult}
            selectedModels={selectedModels}
            onSelectionChange={setSelectedModels}
            modelColors={modelColors}
          />
        </div>
      </div>
    </div>
  );
}
