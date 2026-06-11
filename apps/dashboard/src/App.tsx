/**
 * App — top-level shell: nav + sidebar + content area.
 * Full-viewport, no-scroll layout. Data fetched on domain change.
 */

import { useState, useEffect, useCallback } from 'react';
import './styles/app.css';

import { NavBar } from './components/NavBar';
import type { NavTab } from './components/NavBar';
import { Sidebar } from './components/Sidebar';
import { ContentArea } from './components/ContentArea';
import { MethodologyPage } from './components/MethodologyPage';
import { FailuresFindings } from './components/FailuresFindings';
import { DataPage } from './components/DataPage';
import { AboutPage } from './components/AboutPage';
import { ProvenanceFooter } from './components/ProvenanceFooter';
import type { DomainExtended } from './data/types';
import type { CooccurrenceData } from './components/TermMap';
import type { ActiveVizTab, ActiveFocus } from './components/VizTabs';
import { displayProvider } from './lib/familyUtils';
import { pathToTab, tabToPath, tabToTitle } from './lib/navRouting';

type DomainSlug = 'family' | 'holidays' | 'food';

/** Transient pivot-target state (G7-FOLLOWUP-T1, DESIGN_SYSTEM.md §19.19.5). Default null. */
interface PivotTarget {
  modelId: string;
  domainSlug: DomainSlug;
}

export default function App() {
  const [navTab, setNavTab] = useState<NavTab>(() => pathToTab(window.location.pathname));
  const [activeDomain, setActiveDomain] = useState<DomainSlug>('family');
  /** Transient pivot-target: set by handlePivotToRecords, cleared by FailuresFindings. */
  const [pivotTarget, setPivotTarget] = useState<PivotTarget | null>(null);
  const [domain, setDomain] = useState<DomainExtended | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [selectedModelIds, setSelectedModelIds] = useState<Set<string>>(new Set());
  const [openWeightsOnly, setOpenWeightsOnly] = useState(false);
  const [pinnedProvider, setPinnedProvider] = useState<string | null>(null);
  const [cooccurrenceData, setCooccurrenceData] = useState<CooccurrenceData | null>(null);
  const [lensEnabled, setLensEnabled] = useState(false);

  // Focus-level state (§13.1, §14.1)
  const [activeFocus, setActiveFocus] = useState<ActiveFocus>('focus-3');

  // Active viz tab — tracks separate tabs for each focus level
  const [focus3VizTab, setFocus3VizTab] = useState<ActiveVizTab>('term-map');
  const [focus1VizTab, setFocus1VizTab] = useState<ActiveVizTab>('f1-self-consistency');
  const [focus2VizTab, setFocus2VizTab] = useState<ActiveVizTab>('f2-overview');

  // Single-select model for Focus 1 (§13.2)
  const [selectedModelId, setSelectedModelId] = useState<string | null>(null);

  // Selected provider family for Focus 2 (§14.2)
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);

  // Derived active viz tab from focus
  const activeVizTab: ActiveVizTab =
    activeFocus === 'focus-1' ? focus1VizTab :
    activeFocus === 'focus-2' ? focus2VizTab :
    focus3VizTab;

  const handleVizTabChange = useCallback((tab: ActiveVizTab) => {
    if (activeFocus === 'focus-1') {
      setFocus1VizTab(tab);
    } else if (activeFocus === 'focus-2') {
      setFocus2VizTab(tab);
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
    } else if (focus === 'focus-2') {
      // Auto-set Focus 2 tab to overview
      setFocus2VizTab('f2-overview');
    }
    // When returning to Focus 3, the focus3VizTab already holds the last state
  }, [domain]);


  // Deep-link URL routing (M3): sync NavTab <-> window.location.pathname.
  // handleTabChange updates state, pushes history, and updates document.title.
  // The popstate listener handles browser back/forward.
  const handleTabChange = useCallback((tab: NavTab) => {
    setNavTab(tab);
    const path = tabToPath(tab);
    if (window.location.pathname !== path) {
      window.history.pushState({ tab }, '', path);
    }
    document.title = tabToTitle(tab);
  }, []);

  /**
   * Chart-to-record provenance pivot (G7-FOLLOWUP-T1, DESIGN_SYSTEM.md §19.19.5).
   * Sets transient pivot target (modelId + activeDomain), then navigates to the
   * Collection records tab. FailuresFindings consumes and clears the target after
   * the arrival highlight has been applied via onPivotTargetConsumed.
   */
  const handlePivotToRecords = useCallback((modelId: string) => {
    setPivotTarget({ modelId, domainSlug: activeDomain });
    handleTabChange('collection-records');
  }, [activeDomain, handleTabChange]);

  const handlePivotTargetConsumed = useCallback(() => {
    setPivotTarget(null);
  }, []);

  // Set initial document.title on mount and register popstate listener.
  useEffect(() => {
    document.title = tabToTitle(pathToTab(window.location.pathname));
    const handlePopState = () => {
      setNavTab(pathToTab(window.location.pathname));
      document.title = tabToTitle(pathToTab(window.location.pathname));
    };
    window.addEventListener('popstate', handlePopState);
    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  }, []);

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

  // Non-explore tabs
  if (navTab !== 'explore') {
    return (
      <>
        <NavBar activeTab={navTab} onTabChange={handleTabChange} />
        {navTab === 'methodology' && <MethodologyPage />}
        {navTab === 'collection-records' && (
          <FailuresFindings
            pivotTarget={pivotTarget}
            onPivotTargetConsumed={handlePivotTargetConsumed}
          />
        )}
        {navTab === 'data' && <DataPage />}
        {navTab === 'about' && <AboutPage />}
        {/* Footer on non-explore routes: activeDomain=null → always renders if versions present */}
        <ProvenanceFooter activeDomain={null} />
      </>
    );
  }

  return (
    <>
      <NavBar activeTab={navTab} onTabChange={handleTabChange} />
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
          activeFocus={activeFocus}
          selectedProvider={selectedProvider}
          onSelectProvider={setSelectedProvider}
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
          selectedProvider={selectedProvider}
          onSelectProvider={setSelectedProvider}
          cooccurrenceData={cooccurrenceData}
          lensEnabled={lensEnabled}
          onLensToggle={() => setLensEnabled((v) => !v)}
          activeDomain={activeDomain}
          onPivotToRecords={handlePivotToRecords}
        />
      </div>
      {/* Per-domain conditional footer: renders nothing on food (not in provenance.json) */}
      <ProvenanceFooter activeDomain={activeDomain} />
    </>
  );
}
