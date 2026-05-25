/**
 * VizTabs — horizontal tab bar for visualization types
 */

export type ActiveVizTab =
  | 'term-map'
  | 'mds-plot'
  | 'cluster-tree'
  | 'free-lists'
  | 'similarity'
  | 'centrality'
  | 'pile-structure';

const TABS: Array<{ id: ActiveVizTab; label: string }> = [
  { id: 'term-map',      label: 'Term Map' },
  { id: 'mds-plot',      label: 'MDS Plot' },
  { id: 'cluster-tree',  label: 'Cluster Tree' },
  { id: 'free-lists',    label: 'Free Lists' },
  { id: 'similarity',    label: 'Similarity' },
  { id: 'centrality',    label: 'Centrality' },
  { id: 'pile-structure', label: 'Pile Structure' },
];

interface VizTabsProps {
  active: ActiveVizTab;
  onChange: (tab: ActiveVizTab) => void;
}

export function VizTabs({ active, onChange }: VizTabsProps) {
  return (
    <div className="viz-tabs" role="tablist" aria-label="Visualization type">
      {TABS.map((tab) => (
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
