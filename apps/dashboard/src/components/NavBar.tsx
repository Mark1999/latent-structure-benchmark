/**
 * NavBar — top navigation bar (48px)
 * Brand + Explore / Methodology / Collection records / Data / About tabs
 *
 * Tab order (DESIGN_SYSTEM.md §22.1, §19.2):
 *   [Explore] [Methodology] [Collection records] [Data] [About]
 *
 * "About" is rightmost (least prominent) per §22.1 positioning constraint.
 * Observatory and data presentation remain primary; About must not dominate the nav.
 */

import { FAILURES_TAB_LABEL } from '../copy/failures_findings';

export type NavTab = 'explore' | 'methodology' | 'collection-records' | 'data' | 'about';

interface NavBarProps {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
}

export function NavBar({ activeTab, onTabChange }: NavBarProps) {
  return (
    <nav className="nav" role="navigation" aria-label="Site navigation">
      <div className="nav__brand">
        Cognitive Structure Lab <span>/ Observatory</span>
      </div>
      <div className="nav__right">
        <button
          className={`nav__tab${activeTab === 'explore' ? ' nav__tab--active' : ''}`}
          onClick={() => onTabChange('explore')}
          aria-current={activeTab === 'explore' ? 'page' : undefined}
        >
          Explore
        </button>
        <button
          className={`nav__tab${activeTab === 'methodology' ? ' nav__tab--active' : ''}`}
          onClick={() => onTabChange('methodology')}
          aria-current={activeTab === 'methodology' ? 'page' : undefined}
        >
          Methodology
        </button>
        <button
          className={`nav__tab${activeTab === 'collection-records' ? ' nav__tab--active' : ''}`}
          onClick={() => onTabChange('collection-records')}
          aria-current={activeTab === 'collection-records' ? 'page' : undefined}
        >
          {FAILURES_TAB_LABEL}
        </button>
        <button
          className={`nav__tab${activeTab === 'data' ? ' nav__tab--active' : ''}`}
          onClick={() => onTabChange('data')}
          aria-current={activeTab === 'data' ? 'page' : undefined}
        >
          Data
        </button>
        <button
          className={`nav__tab${activeTab === 'about' ? ' nav__tab--active' : ''}`}
          onClick={() => onTabChange('about')}
          aria-current={activeTab === 'about' ? 'page' : undefined}
        >
          About
        </button>
      </div>
    </nav>
  );
}
