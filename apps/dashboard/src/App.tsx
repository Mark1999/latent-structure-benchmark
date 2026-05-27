/**
 * App — top-level shell: nav + sidebar + content area.
 * Full-viewport, no-scroll layout. Data fetched on domain change.
 */

import { useState, useEffect, useCallback } from 'react';
import './styles/app.css';

import { NavBar } from './components/NavBar';
import { Sidebar } from './components/Sidebar';
import { ContentArea } from './components/ContentArea';
import type { PublishedModel } from './data/types';
import type { CooccurrenceData } from './components/TermMap';
import type { ActiveVizTab, ActiveFocus } from './components/VizTabs';

// Extended type for fields present in published JSON beyond base DomainResultPublished
interface DomainExtended {
  domain_slug: string;
  analysis_version: string;
  models: PublishedModel[];
  free_lists: Record<string, string[]>;
  mds_coordinates: Record<string, [[number, number]]>;
  mds_uncertainty: Record<string, import('./data/types').EllipseParams | null>;
  similarity_matrix: Record<string, Record<string, number>>;
  similarity_ci: Record<string, Record<string, [number, number] | null>>;
  consensus_score: number;
  consensus_ci: [number, number];
  consensus_type: import('./data/types').ConsensusType;
  sutrop_csi: Record<string, Record<string, number>>;
  within_model_results: import('./data/types').WithinModelResult[];
  groundings: unknown[];
  generated_lede: string;
  generated_at: string;
  romney_small_n_warning: boolean;
  display: import('./data/types').DisplayBlock;
  term_mds_coordinates?: Record<string, [number, number]>;
  term_cluster_assignments?: Record<string, number>;
  term_cluster_labels?: string[];
}

type NavTab = 'explore' | 'methodology' | 'data';
type DomainSlug = 'family' | 'holidays' | 'food';

// Provider display mapping (mirrors ProviderTree)
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

export default function App() {
  const [navTab, setNavTab] = useState<NavTab>('explore');
  const [activeDomain, setActiveDomain] = useState<DomainSlug>('family');
  const [domain, setDomain] = useState<DomainExtended | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [selectedModelIds, setSelectedModelIds] = useState<Set<string>>(new Set());
  const [openWeightsOnly, setOpenWeightsOnly] = useState(false);
  const [pinnedProvider, setPinnedProvider] = useState<string | null>(null);
  const [activeProvider, setActiveProvider] = useState<string | null>(null);
  const [cooccurrenceData, setCooccurrenceData] = useState<CooccurrenceData | null>(null);
  const [lensEnabled, setLensEnabled] = useState(false);

  // Focus-level state (§13.1)
  const [activeFocus, setActiveFocus] = useState<ActiveFocus>('focus-3');

  // Active viz tab — tracks separate tabs for each focus level
  const [focus3VizTab, setFocus3VizTab] = useState<ActiveVizTab>('term-map');
  const [focus1VizTab, setFocus1VizTab] = useState<ActiveVizTab>('f1-self-consistency');

  // Single-select model for Focus 1 (§13.2)
  const [selectedModelId, setSelectedModelId] = useState<string | null>(null);

  // Derived active viz tab from focus
  const activeVizTab: ActiveVizTab = activeFocus === 'focus-1' ? focus1VizTab : focus3VizTab;

  const handleVizTabChange = useCallback((tab: ActiveVizTab) => {
    if (activeFocus === 'focus-1') {
      setFocus1VizTab(tab);
    } else {
      setFocus3VizTab(tab);
    }
  }, [activeFocus]);

  const handleFocusChange = useCallback((focus: ActiveFocus) => {
    setActiveFocus(focus);
    if (focus === 'focus-1') {
      // Auto-set Focus 1 tab to self-consistency
      setFocus1VizTab('f1-self-consistency');
      // Auto-select first model lexicographically if none selected
      setSelectedModelId((prev) => {
        if (prev) return prev;
        if (domain && domain.models.length > 0) {
          const sorted = [...domain.models].sort((a, b) =>
            a.model_id.localeCompare(b.model_id)
          );
          return sorted[0].model_id;
        }
        return null;
      });
    }
    // When returning to Focus 3, the focus3VizTab already holds the last state
  }, [domain]);


  // Fetch domain data and co-occurrence matrices on domain change
  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setLoading(true);
      setError(null);
      // Reset co-occurrence data immediately so TermMap falls back to static coords
      setCooccurrenceData(null);
      try {
        // Fetch domain JSON and co-occurrence JSON in parallel; co-occurrence
        // is best-effort (not all domains have one yet).
        const [domainResp, cooccResp] = await Promise.all([
          fetch(`/data/${activeDomain}.json`),
          fetch(`/data/${activeDomain}-cooccurrence.json`).catch(() => null),
        ]);

        if (!domainResp.ok) throw new Error(`HTTP ${domainResp.status}`);
        const data = (await domainResp.json()) as DomainExtended;
        if (cancelled) return;

        setDomain(data);
        setSelectedModelIds(new Set(data.models.map((m) => m.model_id)));
        if (data.models.length > 0) {
          setActiveProvider(displayProvider(data.models[0]));
        }

        // Auto-select first model lexicographically for Focus 1
        if (data.models.length > 0) {
          const sorted = [...data.models].sort((a, b) =>
            a.model_id.localeCompare(b.model_id)
          );
          setSelectedModelId(sorted[0].model_id);
        }

        // Load co-occurrence data if available
        if (cooccResp && cooccResp.ok) {
          const cooccData = (await cooccResp.json()) as CooccurrenceData;
          if (!cancelled) setCooccurrenceData(cooccData);
        }

        if (!cancelled) setLoading(false);
      } catch (e) {
        if (cancelled) return;
        const msg = e instanceof Error ? e.message : 'Failed to load domain data';
        setError(msg);
        setLoading(false);
      }
    };

    void load();
    return () => { cancelled = true; };
  }, [activeDomain]);

  const handleToggleModel = useCallback((id: string) => {
    setSelectedModelIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  const handleToggleProvider = useCallback((pid: string) => {
    if (!domain) return;
    const providerModels = domain.models.filter(
      (m) => displayProvider(m) === pid
    );
    const allSelected = providerModels.every((m) => selectedModelIds.has(m.model_id));
    setSelectedModelIds((prev) => {
      const next = new Set(prev);
      providerModels.forEach((m) => {
        if (allSelected) next.delete(m.model_id);
        else next.add(m.model_id);
      });
      return next;
    });
    setActiveProvider(pid);
  }, [domain, selectedModelIds]);

  const handleSelectAll = useCallback(() => {
    if (!domain) return;
    setSelectedModelIds(new Set(domain.models.map((m) => m.model_id)));
  }, [domain]);

  const handleSelectNone = useCallback(() => {
    setSelectedModelIds(new Set());
  }, []);

  const handleTogglePin = useCallback((pid: string) => {
    setPinnedProvider((prev) => (prev === pid ? null : pid));
  }, []);

  const handleRemoveModel = useCallback((id: string) => {
    setSelectedModelIds((prev) => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
  }, []);

  // Non-explore tabs: simple placeholder
  if (navTab !== 'explore') {
    return (
      <>
        <NavBar activeTab={navTab} onTabChange={setNavTab} />
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: 'calc(100vh - 48px)',
          color: 'var(--color-text-secondary)',
          fontSize: 'var(--font-size-sm)',
          fontStyle: 'italic',
        }}>
          {navTab === 'methodology' && 'Methodology page — coming soon'}
          {navTab === 'data' && 'Data download page — coming soon'}
        </div>
      </>
    );
  }

  return (
    <>
      <NavBar activeTab={navTab} onTabChange={setNavTab} />
      <div className="app-main">
        <Sidebar
          activeDomain={activeDomain}
          onDomainChange={(slug) => setActiveDomain(slug as DomainSlug)}
          models={domain?.models ?? []}
          selected={selectedModelIds}
          onToggleModel={handleToggleModel}
          onToggleProvider={handleToggleProvider}
          onSelectAll={handleSelectAll}
          onSelectNone={handleSelectNone}
          pinnedProvider={pinnedProvider}
          onTogglePin={handleTogglePin}
          openWeightsOnly={openWeightsOnly}
          onOpenWeightsToggle={() => setOpenWeightsOnly((v) => !v)}
          lensEnabled={lensEnabled}
          onLensToggle={() => setLensEnabled((v) => !v)}
        />
        <ContentArea
          domain={domain}
          loading={loading}
          error={error}
          selectedModelIds={selectedModelIds}
          onRemoveModel={handleRemoveModel}
          activeVizTab={activeVizTab}
          onVizTabChange={handleVizTabChange}
          activeFocus={activeFocus}
          onFocusChange={handleFocusChange}
          selectedModelId={selectedModelId}
          onSelectModel={setSelectedModelId}
          activeProvider={activeProvider}
          pinnedProvider={pinnedProvider}
          onTogglePin={handleTogglePin}
          cooccurrenceData={cooccurrenceData}
          lensEnabled={lensEnabled}
          activeDomain={activeDomain}
        />
      </div>
    </>
  );
}
