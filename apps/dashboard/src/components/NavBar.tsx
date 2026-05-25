/**
 * NavBar — top navigation bar (48px)
 * Brand + Explore / Methodology / Data tabs
 */

interface NavBarProps {
  activeTab: 'explore' | 'methodology' | 'data';
  onTabChange: (tab: 'explore' | 'methodology' | 'data') => void;
}

export function NavBar({ activeTab, onTabChange }: NavBarProps) {
  return (
    <nav className="nav" role="navigation" aria-label="Site navigation">
      <div className="nav__brand">
        Cognitive Structure Lab <span>/ LSB</span>
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
          className={`nav__tab${activeTab === 'data' ? ' nav__tab--active' : ''}`}
          onClick={() => onTabChange('data')}
          aria-current={activeTab === 'data' ? 'page' : undefined}
        >
          Data
        </button>
      </div>
    </nav>
  );
}
