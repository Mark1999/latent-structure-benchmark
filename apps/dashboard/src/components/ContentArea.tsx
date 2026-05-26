/**
 * ContentArea — wraps viz tabs + selection bar + chart + timeline
 */

import { VizTabs, type ActiveVizTab } from './VizTabs';
import { SelectionBar } from './SelectionBar';
import { TermMap, type CooccurrenceData, type ModelPileData } from './TermMap';
import { MDSPlot } from './MDSPlot';
import { CentralityChart } from './CentralityChart';
import { SimilarityHeatmap } from './SimilarityHeatmap';
import { FreeListCompare, type SutropCsiEntry } from './FreeListCompare';
import { PileStructure } from './PileStructure';
import { ClusterTree } from './ClusterTree';
import { Timeline } from './Timeline';
import type { DomainResultPublished, PublishedModel } from '../data/types';

// Extended domain fields present in published JSON but not yet in DomainResultPublished type
interface DomainExtended extends DomainResultPublished {
  term_mds_coordinates?: Record<string, [number, number]>;
  term_cluster_assignments?: Record<string, number>;
  term_cluster_labels?: string[];
  centroid_piles?: Record<string, ModelPileData>;
  /** Cultural centrality scores: model_id → score (~0.2–0.3). */
  cultural_centrality_scores?: Record<string, number>;
  /** Pairwise similarity matrix as a flat 2D array. Model order matches the models array. */
  similarity_matrix_array?: number[][];
  /** Scipy linkage matrix for hierarchical clustering: rows of [idx1, idx2, distance, count]. */
  term_cluster_linkage?: number[][];
  /** Ordered list of term names corresponding to leaf indices 0..n-1 in the linkage matrix. */
  term_mds_items?: string[];
  /** Bootstrap proportion per internal linkage node (one value per linkage row). */
  term_cluster_bp_values?: number[];
}

// Provider display color map
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

function shortModelName(modelId: string): string {
  return modelId
    .replace(/^claude-/, '')
    .replace(/^gpt-/, 'gpt-')
    .replace(/^gemini-/, 'gemini-')
    .replace(/^meta-llama\//, '')
    .replace(/^mistralai\//, '')
    .split('/').pop() || modelId;
}

interface ContentAreaProps {
  domain: DomainExtended | null;
  loading: boolean;
  error: string | null;
  selectedModelIds: Set<string>;
  onRemoveModel: (id: string) => void;
  activeVizTab: ActiveVizTab;
  onVizTabChange: (tab: ActiveVizTab) => void;
  activeProvider: string | null;
  pinnedProvider: string | null;
  onTogglePin: (provider: string) => void;
  /** Co-occurrence matrices for the active domain (used by TermMap for browser-side MDS) */
  cooccurrenceData?: CooccurrenceData | null;
  /** When true, TermMap shows a cursor-following magnifying lens */
  lensEnabled?: boolean;
}

export function ContentArea({
  domain,
  loading,
  error,
  selectedModelIds,
  onRemoveModel,
  activeVizTab,
  onVizTabChange,
  activeProvider,
  pinnedProvider,
  onTogglePin,
  cooccurrenceData,
  lensEnabled,
}: ContentAreaProps) {
  // Build selection bar chips
  const selectedChips = domain
    ? domain.models
        .filter((m) => selectedModelIds.has(m.model_id))
        .map((m) => ({
          id: m.model_id,
          shortName: shortModelName(m.model_id),
          providerColor: PROVIDER_COLORS[displayProvider(m)] || '#888',
        }))
    : [];

  // Build provider models map for timeline
  const providerModels: Record<string, Array<{ model_id: string; release_date: string }>> = {};
  if (domain) {
    domain.models.forEach((m) => {
      const pid = displayProvider(m);
      if (!providerModels[pid]) providerModels[pid] = [];
      providerModels[pid].push({ model_id: m.model_id, release_date: m.release_date });
    });
  }

  return (
    <div className="content-area">
      <VizTabs active={activeVizTab} onChange={onVizTabChange} />
      <SelectionBar selected={selectedChips} onRemove={onRemoveModel} />

      <div className="chart-area">
        {loading && (
          <div className="chart-lede">
            Loading domain data…
          </div>
        )}
        {error && (
          <div className="chart-lede">
            <strong>Error:</strong> {error}
          </div>
        )}
        {!loading && !error && domain && (
          <>
            <p className="chart-lede" aria-live="polite">
              Across{' '}
              <strong>{selectedModelIds.size} model{selectedModelIds.size !== 1 ? 's' : ''}</strong>
              , {domain.domain_slug} vocabulary is organized around a shared categorical structure
              {domain.consensus_score != null && (
                <>
                  {' '}(<strong>Smith&apos;s S = {domain.consensus_score.toFixed(2)}</strong>
                  {domain.consensus_ci && (
                    <>, 95% CI [{domain.consensus_ci[0].toFixed(2)}, {domain.consensus_ci[1].toFixed(2)}]</>
                  )}
                  )
                </>
              )}.
            </p>

            {activeVizTab === 'term-map' && domain.term_mds_coordinates && (
              <TermMap
                termCoords={domain.term_mds_coordinates}
                termClusters={domain.term_cluster_assignments ?? {}}
                clusterLabels={domain.term_cluster_labels ?? []}
                centroidPiles={domain.centroid_piles}
                cooccurrenceData={cooccurrenceData}
                selectedModelIds={selectedModelIds}
                lensEnabled={lensEnabled}
              />
            )}

            {activeVizTab === 'mds-plot' && domain.mds_coordinates && (
              <MDSPlot
                mdsCoordinates={domain.mds_coordinates as unknown as Record<string, [number, number]>}
                mdsUncertainty={domain.mds_uncertainty as unknown as Record<string, { semi_major: number; semi_minor: number; rotation_rad: number; center: [number, number]; n_bootstrap: number } | null>}
                models={domain.models}
                selectedModelIds={selectedModelIds}
                topTerms={(domain.display as unknown as { top_terms: Record<string, string[]> })?.top_terms ?? {}}
                centralityScores={(domain as unknown as { cultural_centrality_scores: Record<string, number> }).cultural_centrality_scores ?? {}}
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
                  models={domain.models}
                  selectedModelIds={selectedModelIds}
                />
              </div>
            )}

            {activeVizTab === 'similarity' && (
              <div className="chart-wrap">
                <p className="chart-wrap__desc">
                  Pairwise similarity between models based on how they co-organize domain
                  terms. Darker cells indicate models that produce more similar categorical
                  structures.
                </p>
                <SimilarityHeatmap
                  similarityMatrix={
                    (domain as unknown as { similarity_matrix: number[][] }).similarity_matrix ?? []
                  }
                  models={domain.models}
                  selectedModelIds={selectedModelIds}
                />
              </div>
            )}

            {activeVizTab === 'free-lists' && (
              <FreeListCompare
                sutropCsi={domain.sutrop_csi as unknown as Record<string, SutropCsiEntry[]>}
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
          </>
        )}
        {!loading && !error && !domain && (
          <div className="chart-wrap">
            <div className="viz-placeholder">Select a domain to begin.</div>
          </div>
        )}
      </div>

      <Timeline
        activeProvider={activeProvider}
        providerModels={providerModels}
        pinnedProvider={pinnedProvider}
        onTogglePin={onTogglePin}
      />
    </div>
  );
}
