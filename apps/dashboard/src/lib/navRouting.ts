/**
 * navRouting.ts: pure path-to-tab mapping functions for top-level NavBar routing.
 *
 * No React imports, no DOM access, no window/document/history references.
 * Fully jsdom-free unit-testable.
 *
 * Architect-pinned path table (M3, docs/status/2026-06-10-site-copy-verdicts.md):
 *
 *   /                  -> explore    (canonical home URL)
 *   /explore           -> explore
 *   /methodology       -> methodology
 *   /collection-records -> collection-records
 *   /data              -> data
 *   /about             -> about
 *   (anything else)    -> explore    (fallback; no URL rewrite on unknown paths)
 *
 * Title spacer: ASCII hyphen-minus (U+002D), e.g. "Cognitive Structure Lab - Explore".
 * This avoids both em-dash and en-dash ambiguity (CLAUDE.md feedback_no_em_dashes,
 * Architect M3 §3 pin, CDA SME M3-A1, UI/UX N1).
 *
 * FAILURES_TAB_LABEL ("Collection records") is imported here to keep the tab
 * label in sync with NavBar.tsx and copy/failures_findings.ts.
 */

import type { NavTab } from '../components/NavBar';
import { FAILURES_TAB_LABEL } from '../copy/failures_findings';

/**
 * Map a pathname string to a NavTab.
 *
 * Normalizes trailing slashes and lowercases the pathname segment before
 * matching. Trailing query strings and hash fragments are ignored (caller
 * should pass window.location.pathname, which never includes them).
 *
 * Unknown pathnames fall back to 'explore' without rewriting the URL.
 */
export function pathToTab(pathname: string): NavTab {
  // Strip trailing slash (normalize /methodology/ === /methodology)
  const normalized = pathname.replace(/\/+$/, '') || '/';
  const lower = normalized.toLowerCase();

  switch (lower) {
    case '/':
    case '/explore':
      return 'explore';
    case '/methodology':
      return 'methodology';
    case '/collection-records':
      return 'collection-records';
    case '/data':
      return 'data';
    case '/about':
      return 'about';
    default:
      return 'explore';
  }
}

/**
 * Map a NavTab to its canonical URL path.
 *
 * 'explore' -> '/'  (canonical home URL; direct visits to /explore also resolve
 *                    to explore, but clicks from any tab navigate to '/')
 * All others -> '/' + tab
 */
export function tabToPath(tab: NavTab): string {
  if (tab === 'explore') return '/';
  return '/' + tab;
}

/**
 * Map a NavTab to the document.title string.
 *
 * Format: "Cognitive Structure Lab - <Label>"
 * Spacer: ASCII hyphen-minus (U+002D).
 * Label vocabulary matches NavBar.tsx button text and FAILURES_TAB_LABEL.
 */
export function tabToTitle(tab: NavTab): string {
  const labels: Record<NavTab, string> = {
    explore: 'Explore',
    methodology: 'Methodology',
    'collection-records': FAILURES_TAB_LABEL,
    data: 'Data',
    about: 'About',
  };
  return `Cognitive Structure Lab - ${labels[tab]}`;
}
