/**
 * DataExplorer — T9 container component, extended at T10.
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
 * T10 additions:
 *   - URL permalink state: on mount, reads ?domain=&models=&#mds via decodePermalink.
 *     If the permalink domain matches the current domain AND all model ids exist in
 *     the domain's mds_coordinates, restores selectedModels from the URL.
 *     Otherwise uses the §3.7 v0.4.2 first-6 default.
 *   - On selectedModels or activeVizTab change, updates the URL via history.replaceState
 *     using encodePermalink (unified scheme: ?domain=...&models=...#mds).
 *     This supersedes T8's bare #mds fragment — handleVizTabChange now calls
 *     writePermalinkState for the full URL update.
 *   - Renders SourceAttribution below the explorer layout.
 *   - Renders DownloadBar below SourceAttribution.
 *
 * No child component (MDSPlot, ModelSelector, Legend) computes its own
 * model color from model_id — all receive modelColors as a prop per §12.4
 * palette ownership rule.
 *
 * Source: DESIGN_SYSTEM.md §3.1, §3.7 (v0.4.2), §12.4, §5
 * Reference: docs/status/2026-05-09-phase5-architect-plan.md §4 T9 + T10
 */

import { useEffect, useState, useMemo } from "react";
import type { DomainResultPublished } from "../data/types";
import { MDSPlot } from "./MDSPlot";
import { ModelSelector } from "./ModelSelector";
import { VizSwitcher, resolveFragmentOnMount } from "./VizSwitcher";
import type { ActiveVizTab } from "./VizSwitcher";
import { SourceAttribution } from "./SourceAttribution";
import { DownloadBar } from "./DownloadBar";
import { encodePermalink, decodePermalink } from "../lib/permalink";

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

// ── URL state helpers ─────────────────────────────────────────────────────────

/**
 * Attempt to read permalink-encoded selectedModels from the current URL.
 * Returns a filtered array of valid model_ids (only those that exist in
 * availableModelIds), or null if no valid permalink is found.
 *
 * Validation: the permalink domain must match currentDomain AND every
 * model_id in the permalink must exist in availableModelIds. This prevents
 * stale URL state (from a previous domain or test run) from corrupting
 * the initial selection.
 */
function readSelectedModelsFromUrl(
  currentDomain: string,
  availableModelIds: Set<string>
): string[] | null {
  try {
    const searchAndHash = window.location.search + window.location.hash;
    const state = decodePermalink(searchAndHash);
    if (state === null) return null;
    if (state.domain !== currentDomain) return null;
    // Filter to only model ids that exist in this domain.
    const valid = state.models.filter((id) => availableModelIds.has(id));
    if (valid.length === 0) return null;
    return valid;
  } catch {
    return null;
  }
}

/**
 * Write the current view state to the URL using history.replaceState.
 * Uses the unified ?domain=&models=#tab scheme (T10 unification of T8's bare #mds).
 */
function writePermalinkState(
  domain: string,
  models: string[],
  vizTab: ActiveVizTab
): void {
  try {
    const encoded = encodePermalink({ domain, models, vizTab });
    window.history.replaceState(null, "", encoded);
  } catch {
    // history API unavailable in some test environments — ignore.
  }
}

// ── Component ─────────────────────────────────────────────────────────────────

/**
 * DataExplorer renders the full interactive explorer area:
 *   VizSwitcher tab bar → MDSPlot (main area) → ModelSelector (right/below)
 *   → Legend (below plot, inside MDSPlot)
 *   → SourceAttribution (below layout)
 *   → DownloadBar (below SourceAttribution)
 *
 * All explorer-internal state lives here. App.tsx provides only domainResult.
 */
export function DataExplorer({ domainResult }: DataExplorerProps) {
  /**
   * selectedModels: which model_ids are currently visible on the plot.
   * §3.7 v0.4.2 binding: initial value = first 6 by §12.4 lexicographic sort,
   * OR restored from URL permalink if domain matches and all model ids are valid.
   * Reset on domain change (domainResult identity changes when domain switches).
   */
  const [selectedModels, setSelectedModels] = useState<string[]>(() => {
    const rawCoords = domainResult.mds_coordinates as unknown as Record<string, [number, number]>;
    const sortedIds = Object.keys(rawCoords).sort();
    const availableSet = new Set(sortedIds);
    // T10: attempt to restore from URL permalink.
    const fromUrl = readSelectedModelsFromUrl(domainResult.domain_slug, availableSet);
    if (fromUrl !== null) return fromUrl;
    // §3.7 v0.4.2 default: first 6 sorted model_ids.
    return sortedIds.slice(0, 6);
  });

  /**
   * activeVizTab: which viz tab is active.
   * Phase 5: only "mds" is activatable.
   * T9: uses resolveFragmentOnMount from VizSwitcher to read URL fragment on mount.
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
   * T10: also attempts to restore from URL permalink for the new domain,
   * but only when all restored model ids are valid for that domain.
   *
   * eslint set-state-in-effect: setting state in a useEffect that responds to
   * a prop/context change is the documented React pattern for derived resets
   * (https://react.dev/reference/react/useState#storing-information-from-previous-renders).
   */
  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    const rawCoords = domainResult.mds_coordinates as unknown as Record<string, [number, number]>;
    // Domain change: always reset to §3.7 v0.4.2 first-6 default.
    // The URL state is written by the writePermalinkState effect immediately after.
    // We do not re-read the URL here because the URL may still contain the
    // previous domain's model selection and would produce stale state.
    setSelectedModels(Object.keys(rawCoords).sort().slice(0, 6));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [domainResult.domain_slug]);
  /* eslint-enable react-hooks/set-state-in-effect */

  /**
   * Sync URL whenever selectedModels or activeVizTab changes.
   * Uses the unified ?domain=&models=#tab scheme (T10).
   * This supersedes T8's bare #mds fragment.
   */
  useEffect(() => {
    writePermalinkState(domainResult.domain_slug, selectedModels, activeVizTab);
  }, [domainResult.domain_slug, selectedModels, activeVizTab]);

  /**
   * Handle VizSwitcher tab activation. Phase 5: only "mds" is activatable.
   * URL update is handled by the effect above via the unified scheme.
   */
  function handleVizTabChange(tab: ActiveVizTab): void {
    setActiveVizTab(tab);
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

      {/* SourceAttribution: source line below the chart per §5 (T10).
          Shows selected model list, domain, prompt v1, analysis version,
          collection month. Surfaces romney_small_n_warning per CDA SME Q2. */}
      <SourceAttribution
        domainResult={domainResult}
        selectedModels={selectedModels}
      />

      {/* DownloadBar: CSV + permalink buttons below SourceAttribution per §5 (T10).
          In embed mode, DownloadBar remains visible per §12.5; Permalink is hidden
          in embed mode — deferred to T12 embed mode spec. */}
      <DownloadBar
        domainResult={domainResult}
        selectedModels={selectedModels}
        activeVizTab={activeVizTab}
      />
    </div>
  );
}
