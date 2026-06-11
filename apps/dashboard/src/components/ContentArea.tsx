/**
 * ContentArea: wraps focus selector + viz tabs + chart area.
 *
 * TM-B changes (DESIGN_SYSTEM.md §3.1.1, v0.20.1):
 *   - SelectionBar (SHOWING chips) removed unconditionally for all VizTabs (§3.1.1(b)(i)).
 *   - Four TermMap controls lifted here from TermMap.tsx; ChartToolbar renders them
 *     above the chart when activeVizTab === 'term-map' (§3.1.1(b)(ii)).
 *   - Focus 3 chart area restructured into two-column desktop / one-column mobile flex
 *     layout: lede (280px left) beside chart (right) on desktop; chart first / lede
 *     below on mobile (§3.1.1(b)(iii)).
 *   - chart-area gets min-height: 70vh on desktop via app.css media query (§3.1.1(a)).
 */

import { useState, useMemo, useCallback } from 'react';
import { VizTabs, type ActiveVizTab, type ActiveFocus } from './VizTabs';
import { FocusSelector } from './FocusSelector';
import { ChartToolbar } from './ChartToolbar';
import { TermMap, type CooccurrenceData } from './TermMap';
import { MDSPlot } from './MDSPlot';
import { CentralityChart } from './CentralityChart';
import { SimilarityHeatmap } from './SimilarityHeatmap';
import { FreeListCompare } from './FreeListCompare';
import { PileStructure } from './PileStructure';
import { ClusterTree } from './ClusterTree';
import { Focus1SelfConsistencyOverview } from './Focus1SelfConsistencyOverview';
import { Focus1RunDistribution } from './Focus1RunDistribution';
import { Focus1TermStability } from './Focus1TermStability';
import { Focus2FamilyOverview } from './Focus2FamilyOverview';
import { Focus2FamilySimilarity } from './Focus2FamilySimilarity';
import { Focus2FamilySalience } from './Focus2FamilySalience';
import { Focus2FamilyPiles } from './Focus2FamilyPiles';
import type { DomainExtended } from '../data/types';
import { displayModel } from '../lib/familyUtils';
import { CI_DISCLOSURE_TEXT, SMALL_N_TEXT } from '../copy/consensus_disclosure';

// Provider display color map
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


interface ContentAreaProps {
  domain: DomainExtended | null;
  loading: boolean;
  error: string | null;
  selectedModelIds: Set<string>;
  onRemoveModel: (id: string) => void;
  activeVizTab: ActiveVizTab;
  onVizTabChange: (tab: ActiveVizTab) => void;
  activeFocus: ActiveFocus;
  onFocusChange: (focus: ActiveFocus) => void;
  /** Single-selected model for Focus 1 views */
  selectedModelId: string | null;
  onSelectModel: (id: string) => void;
  /** Selected provider family for Focus 2 views */
  selectedProvider?: string | null;
  onSelectProvider?: (provider: string | null) => void;
  /** Co-occurrence matrices for the active domain (used by TermMap for browser-side MDS) */
  cooccurrenceData?: CooccurrenceData | null;
  /** When true, TermMap shows a cursor-following magnifying lens */
  lensEnabled?: boolean;
  /** Callback to toggle magnifying lens */
  onLensToggle?: () => void;
  /** Active domain slug (needed for Focus 1 data loading) */
  activeDomain: string;
  /** Callback to pivot to the Collection records tab for a given model (G7-FOLLOWUP-T1). */
  onPivotToRecords?: (modelId: string) => void;
}

export { PROVIDER_COLORS };

export function ContentArea({
  domain,
  loading,
  error,
  selectedModelIds,
  // onRemoveModel: kept in interface for API compatibility; not used after SelectionBar removal (TM-B)
  activeVizTab,
  onVizTabChange,
  activeFocus,
  onFocusChange,
  selectedModelId,
  onSelectModel,
  selectedProvider = null,
  onSelectProvider,
  cooccurrenceData,
  lensEnabled,
  onLensToggle,
  activeDomain,
  onPivotToRecords,
}: ContentAreaProps) {
  const isFocus1 = activeFocus === 'focus-1';
  const isFocus2 = activeFocus === 'focus-2';

  // ── Lifted TermMap toolbar state (§3.1.1(b)(ii)) ──────────────────────────
  // overlayPileLabelKey: the effective pile-label model key (or null for None).
  // '__default__' sentinel means "user hasn't picked; fall back to first key."
  const [overlayPileLabelChoice, setOverlayPileLabelChoice] = useState<string | null | '__default__'>('__default__');

  // showUncertainty: default ON per §3.1.1(b)(ii) binding.
  const [showUncertainty, setShowUncertainty] = useState(true);
  // showClusterLabels: default ON per §3.1.1(b)(ii) binding.
  const [showClusterLabels, setShowClusterLabels] = useState(true);
  // lensDisabledByZoom: notified by TermMap when zoom exceeds 1.02 (Q2 LOCKED).
  const [lensDisabledByZoom, setLensDisabledByZoom] = useState(false);

  // Sorted pile model keys; computed from domain.centroid_piles.
  const pileModelKeys = useMemo(
    () => (domain?.centroid_piles ? Object.keys(domain.centroid_piles).sort() : []),
    [domain]
  );

  // Derive the effective overlay key from the user's choice + available keys.
  const effectiveOverlayKey: string | null = useMemo(() => {
    if (overlayPileLabelChoice === '__default__') return pileModelKeys[0] ?? null;
    if (overlayPileLabelChoice === null) return null;
    if (domain?.centroid_piles && overlayPileLabelChoice in domain.centroid_piles) return overlayPileLabelChoice;
    return pileModelKeys[0] ?? null;
  }, [overlayPileLabelChoice, pileModelKeys, domain]);

  const handleOverlayChange = useCallback((key: string | null) => {
    setOverlayPileLabelChoice(key);
  }, []);

  const handleLensDisabledByZoomChange = useCallback((disabled: boolean) => {
    setLensDisabledByZoom(disabled);
  }, []);

  // When a card is clicked in Focus 1 Self-Consistency, select model and
  // auto-navigate to Run Distribution so the user sees immediate results.
  function handleSelectModelAndNavigate(id: string) {
    onSelectModel(id);
    onVizTabChange('f1-run-distribution');
  }

  return (
    <div className="content-area">
      <FocusSelector active={activeFocus} onChange={onFocusChange} />
      <VizTabs active={activeVizTab} onChange={onVizTabChange} activeFocus={activeFocus} />
      {/* SelectionBar (SHOWING chips) removed unconditionally per §3.1.1(b)(i). */}

      {/* ChartToolbar: renders only on Focus 3 term-map tab (§3.1.1(b)(ii)) */}
      {!isFocus1 && !isFocus2 && activeVizTab === 'term-map' && (
        <ChartToolbar
          pileModelKeys={pileModelKeys}
          overlayPileLabelKey={effectiveOverlayKey}
          onOverlayPileLabelKeyChange={handleOverlayChange}
          showUncertainty={showUncertainty}
          onShowUncertaintyChange={setShowUncertainty}
          showClusterLabels={showClusterLabels}
          onShowClusterLabelsChange={setShowClusterLabels}
          lensEnabled={lensEnabled ?? false}
          onLensToggle={onLensToggle ?? (() => {})}
          lensDisabledByZoom={lensDisabledByZoom}
        />
      )}

      <div className="chart-area">
        {loading && (
          <div className="chart-lede">
            Loading domain data...
          </div>
        )}
        {error && (
          <div className="chart-lede">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* ===== Focus 2 tabs ===== */}
        {!loading && !error && isFocus2 && domain && (
          <>
            {activeVizTab === 'f2-overview' && (
              <Focus2FamilyOverview
                models={domain.models}
                similarityMatrix={domain.similarity_matrix ?? []}
                similarityCi={domain.similarity_ci ?? []}
                onSelectProvider={(provider) => {
                  onSelectProvider?.(provider);
                  onVizTabChange('f2-similarity');
                }}
              />
            )}
            {activeVizTab === 'f2-similarity' && (
              <Focus2FamilySimilarity
                models={domain.models}
                similarityMatrix={domain.similarity_matrix ?? []}
                similarityCi={domain.similarity_ci ?? []}
                mdsCoordinates={domain.mds_coordinates}
                mdsUncertainty={domain.mds_uncertainty}
                selectedProvider={selectedProvider}
              />
            )}
            {activeVizTab === 'f2-salience' && (
              <Focus2FamilySalience
                models={domain.models}
                sutropCsi={domain.sutrop_csi}
                selectedProvider={selectedProvider}
              />
            )}
            {activeVizTab === 'f2-piles' && (
              <Focus2FamilyPiles
                models={domain.models}
                centroidPiles={domain.centroid_piles}
                selectedProvider={selectedProvider}
              />
            )}
          </>
        )}

        {!loading && !error && isFocus2 && !domain && (
          <div className="chart-wrap">
            <div className="viz-placeholder">Select a domain to begin.</div>
          </div>
        )}

        {/* ===== Focus 1 tabs ===== */}
        {!loading && !error && isFocus1 && (
          <>
            {activeVizTab === 'f1-self-consistency' && (
              <Focus1SelfConsistencyOverview
                domainSlug={activeDomain}
                models={domain?.models ?? []}
                selectedModelId={selectedModelId}
                onSelectModel={handleSelectModelAndNavigate}
                onPivotToRecords={onPivotToRecords}
              />
            )}
            {activeVizTab === 'f1-run-distribution' && (
              <Focus1RunDistribution
                domainSlug={activeDomain}
                selectedModelId={selectedModelId}
              />
            )}
            {activeVizTab === 'f1-term-stability' && (
              <Focus1TermStability
                domainSlug={activeDomain}
                selectedModelId={selectedModelId}
              />
            )}
          </>
        )}

        {/* ===== Focus 3 tabs ===== */}
        {!loading && !error && !isFocus1 && !isFocus2 && domain && (
          <>
            {/*
              Two-column desktop / one-column mobile layout (§3.1.1(b)(iii)).
              DOM source order: chart column FIRST, lede column SECOND.
              This matches the mobile single-column layout (chart first visually)
              and the UI/UX gate TM-B requirement that DOM source order is correct
              for each breakpoint without CSS order or flex-direction: row-reverse.

              On desktop (>=768px): CSS grid with grid-template-areas places the lede
              column on the LEFT and the chart column on the RIGHT, using explicit
              grid-area placement. This achieves the correct visual layout without
              reordering DOM elements via CSS `order` property.

              Lede column: 280px fixed (hardcoded per UI/UX TM-A verdict, not a token).
              Chart column: min(calc(100% - 280px), var(--max-chart-width)).
              Lede column overflow-y: auto (§3.1.1(b)(iii) lede-column scroll, v0.20.1).

              The layout classes are defined in app.css.
            */}
            <div className="focus3-layout">
              <div className="focus3-layout__chart-col">
                {activeVizTab === 'term-map' && domain.term_mds_coordinates && (
                  <TermMap
                    termCoords={domain.term_mds_coordinates}
                    termClusters={domain.term_cluster_assignments ?? {}}
                    clusterLabels={domain.term_cluster_labels ?? []}
                    centroidPiles={domain.centroid_piles}
                    cooccurrenceData={cooccurrenceData}
                    selectedModelIds={selectedModelIds}
                    lensEnabled={lensEnabled}
                    onLensToggle={onLensToggle}
                    termUncertainty={domain.term_mds_uncertainty}
                    overlayPileLabelKey={effectiveOverlayKey}
                    showUncertainty={showUncertainty}
                    showClusterLabels={showClusterLabels}
                    onLensDisabledByZoomChange={handleLensDisabledByZoomChange}
                    salienceRanks={domain.sutrop_csi}
                  />
                )}

                {activeVizTab === 'mds-plot' && domain.mds_coordinates && (
                  <MDSPlot
                    mdsCoordinates={domain.mds_coordinates}
                    mdsUncertainty={domain.mds_uncertainty}
                    models={domain.models}
                    selectedModelIds={selectedModelIds}
                    topTerms={domain.display?.top_terms ?? {}}
                    centralityScores={domain.cultural_centrality_scores ?? {}}
                    r1States={domain.display?.r1_states ?? {}}
                    ociValues={Object.fromEntries((domain.within_model_results ?? []).map(r => [r.model_id, r.oci]))}
                    onPivotToRecords={onPivotToRecords}
                    activeDomain={activeDomain}
                  />
                )}

                {activeVizTab === 'centrality' && (
                  <div className="chart-wrap">
                    <p className="chart-wrap__desc">
                      Cultural centrality measures how typical each model&apos;s categorical
                      structure is relative to the group. Higher scores mean the model organizes
                      vocabulary more like the consensus.
                    </p>
                    <CentralityChart
                      centralityScores={domain.cultural_centrality_scores ?? {}}
                      centralityCi={domain.centrality_ci}
                      models={domain.models}
                      selectedModelIds={selectedModelIds}
                      consensusType={domain.consensus_type}
                      domainSlug={domain.domain_slug}
                    />
                  </div>
                )}

                {activeVizTab === 'similarity' && (
                  <div className="chart-wrap">
                    {/*
                      Two-sentence caption: CDA SME T3 §3 binding (verbatim).
                      Source: docs/status/2026-06-08-phase9a-T3-cda-sme-verdict.md §3.
                      Do NOT render this caption inside SimilarityHeatmap.tsx (no duplication).
                    */}
                    <p className="chart-wrap__desc">
                      Each cell shows how similarly two models organize this domain (1.00 = identical
                      organization; 0.50 = no shared structure). Dashed cells: 95% confidence interval
                      includes the no-shared-structure value of 0.50.
                    </p>
                    <SimilarityHeatmap
                      similarityMatrix={domain.similarity_matrix ?? []}
                      similarityCi={domain.similarity_ci ?? []}
                      models={domain.models}
                      selectedModelIds={selectedModelIds}
                    />
                    {/*
                      §23.3 Heatmap model-exclusion caption (PROMOTE-FOOD-V02).
                      Excluded models = models in domain.models not in domain.mds_coordinates.
                      One <p className="heatmap-exclusion-caption"> per excluded model.
                      Visible text uses displayModel(); aria-label uses full model_id (§18.5).
                      Caption renders in ContentArea.tsx, NOT inside SimilarityHeatmap.tsx.
                    */}
                    {(() => {
                      const mdsIds = new Set(Object.keys(domain.mds_coordinates ?? {}));
                      const excludedModels = domain.models.filter(
                        (m) => !mdsIds.has(m.model_id)
                      );
                      return excludedModels.map((m) => (
                        <p
                          key={`heatmap-exclusion-${m.model_id}`}
                          className="heatmap-exclusion-caption"
                          aria-label={`Similarity matrix exclusion: ${m.model_id} is not shown because it has no single-pass collection records for this domain.`}
                        >
                          {displayModel(m.model_id)} is not shown in the similarity matrix because it has no single-pass collection records for this domain.
                        </p>
                      ));
                    })()}
                  </div>
                )}

                {activeVizTab === 'free-lists' && (
                  <FreeListCompare
                    sutropCsi={domain.sutrop_csi}
                    models={domain.models}
                    selectedModelIds={selectedModelIds}
                  />
                )}

                {activeVizTab === 'pile-structure' && domain.centroid_piles && (
                  <PileStructure
                    centroidPiles={domain.centroid_piles}
                    models={domain.models}
                    selectedModelIds={selectedModelIds}
                  />
                )}

                {activeVizTab === 'pile-structure' && !domain.centroid_piles && (
                  <div className="chart-wrap">
                    <div className="viz-placeholder">Pile structure data not available for this domain.</div>
                  </div>
                )}

                {activeVizTab === 'cluster-tree' && domain.term_cluster_linkage && domain.term_mds_items && (
                  <div className="chart-wrap">
                    <ClusterTree
                      linkage={domain.term_cluster_linkage}
                      items={domain.term_mds_items}
                      clusterAssignments={domain.term_cluster_assignments ?? {}}
                      bpValues={domain.term_cluster_bp_values}
                    />
                  </div>
                )}

                {activeVizTab === 'cluster-tree' && (!domain.term_cluster_linkage || !domain.term_mds_items) && (
                  <div className="chart-wrap">
                    <div className="viz-placeholder">Cluster tree data not available for this domain.</div>
                  </div>
                )}
              </div>

              {/* Lede column: second in DOM (chart-first mobile), grid-placed left on desktop.
                  §3.1.1(b)(iii): lede beside chart on desktop, below on mobile.
                  §21 rules + M1 six sub-points all carried forward at this new position.
                  Single <p>, verbatim, no splitting, aria-live="polite", class="chart-lede".
                  PROMOTE-FOOD-V02: override badge (§23.1), CI disclosure (§23.2), small-n (§23.2). */}
              <div className="focus3-layout__lede-col">
                <p className="chart-lede" aria-live="polite">{domain.generated_lede}</p>
                {/* §23.1 Override badge: visible whenever consensus_type_override differs from
                    consensus_type. Co-located with the lede (the classification surface). */}
                {domain.consensus_type_override != null && domain.consensus_type_override !== domain.consensus_type && (
                  <>
                    <span
                      className="content-area__override-badge"
                      aria-label={`Classification override: ${domain.consensus_type_override}`}
                    >
                      {domain.consensus_type_override}
                    </span>
                    {/* U3 methodology link: one click from badge to food-v02-footnote (§23.1) */}
                    <a
                      href="/methodology#food-v02-footnote"
                      className="content-area__methodology-link"
                      aria-label="See methodology footnote for food v0.2 classification"
                    >
                      See methodology note
                    </a>
                  </>
                )}
                {/* §23.2 CI disclosure line: F3-R3-C verbatim, shown when override is set. */}
                {domain.consensus_type_override != null && (
                  <p className="content-area__ci-disclosure">
                    {CI_DISCLOSURE_TEXT}
                  </p>
                )}
                {/* §23.2 Small-n line: F3-R3-D verbatim, shown when romney_small_n_warning is true. */}
                {domain.romney_small_n_warning && (
                  <p className="content-area__small-n-line">
                    {SMALL_N_TEXT}
                  </p>
                )}
              </div>
            </div>
          </>
        )}

        {!loading && !error && !isFocus1 && !isFocus2 && !domain && (
          <div className="chart-wrap">
            <div className="viz-placeholder">Select a domain to begin.</div>
          </div>
        )}
      </div>

    </div>
  );
}
