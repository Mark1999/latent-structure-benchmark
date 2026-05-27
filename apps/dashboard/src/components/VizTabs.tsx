/**
 * VizTabs — horizontal tab bar for visualization types.
 *
 * Renders Focus 3 (cross-model) tabs when activeFocus === 'focus-3',
 * or Focus 1 (individual model) tabs when activeFocus === 'focus-1'.
 * DESIGN_SYSTEM.md §13.9
 */

export type ActiveVizTab =
  | 'term-map'
  | 'mds-plot'
  | 'cluster-tree'
  | 'free-lists'
  | 'similarity'
  | 'centrality'
  | 'pile-structure'
  | 'f1-self-consistency'
  | 'f1-run-distribution'
  | 'f1-term-stability'
  | 'f2-overview'
  | 'f2-similarity'
  | 'f2-salience'
  | 'f2-piles';

export type ActiveFocus = 'focus-3' | 'focus-1' | 'focus-2';

const FOCUS3_TABS: Array<{ id: ActiveVizTab; label: string }> = [
  { id: 'term-map',       label: 'Term Map' },
  { id: 'mds-plot',       label: 'Model Map' },
  { id: 'cluster-tree',   label: 'Cluster Tree' },
  { id: 'free-lists',     label: 'Free Lists' },
  { id: 'similarity',     label: 'Similarity' },
  { id: 'centrality',     label: 'Centrality' },
  { id: 'pile-structure', label: 'Pile Structure' },
];

const FOCUS1_TABS: Array<{ id: ActiveVizTab; label: string }> = [
  { id: 'f1-self-consistency', label: 'Self-Consistency' },
  { id: 'f1-run-distribution', label: 'Run Distribution' },
  { id: 'f1-term-stability',   label: 'Term Stability' },
];

const FOCUS2_TABS: Array<{ id: ActiveVizTab; label: string }> = [
  { id: 'f2-overview',   label: 'Overview' },
  { id: 'f2-similarity', label: 'Similarity' },
  { id: 'f2-salience',   label: 'Salience' },
  { id: 'f2-piles',      label: 'Piles' },
];

interface VizTabsProps {
  active: ActiveVizTab;
  onChange: (tab: ActiveVizTab) => void;
  activeFocus: ActiveFocus;
}

export function VizTabs({ active, onChange, activeFocus }: VizTabsProps) {
  const tabs =
    activeFocus === 'focus-1' ? FOCUS1_TABS :
    activeFocus === 'focus-2' ? FOCUS2_TABS :
    FOCUS3_TABS;

  return (
    <div className="viz-tabs" role="tablist" aria-label="Visualization type">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          role="tab"
          aria-selected={active === tab.id}
          className={`viz-tab${active === tab.id ? ' viz-tab--active' : ''}`}
          onClick={() => onChange(tab.id)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
