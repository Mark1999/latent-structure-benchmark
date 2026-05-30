/**
 * ProvenanceFooter — global <footer> landmark.
 *
 * Renders on every route, outside <main>.
 * Fetches numpy_version and scipy_version from /data/provenance.json.
 * Render-nothing fallback: if fetch fails or fields are absent, renders null.
 *
 * Design tokens: --font-size-xs + --color-text-caption (4.60:1 on white — WCAG AA).
 * Top border via --color-border. No new tokens introduced.
 *
 * DESIGN_SYSTEM.md §15.5(b) — global env footer landmark.
 * Gate: UI/UX PASS-WITH-NOTES (docs/status/2026-05-30-promote-ui-ux-verdict.md).
 */

import { useState, useEffect } from 'react';

interface ProvenanceData {
  numpy_version?: string;
  scipy_version?: string;
}

export function ProvenanceFooter() {
  const [data, setData] = useState<ProvenanceData | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch('/data/provenance.json')
      .then((r) => {
        if (!r.ok) return null;
        return r.json() as Promise<ProvenanceData>;
      })
      .then((json) => {
        if (!cancelled) setData(json);
      })
      .catch(() => {
        // render-nothing fallback: leave data null
      });
    return () => { cancelled = true; };
  }, []);

  // Render nothing if fetch failed or fields absent
  if (
    !data ||
    typeof data.numpy_version !== 'string' ||
    !data.numpy_version ||
    typeof data.scipy_version !== 'string' ||
    !data.scipy_version
  ) {
    return null;
  }

  return (
    <footer className="provenance-footer" aria-label="Analysis provenance">
      <a
        href="/data/provenance.json"
        target="_blank"
        rel="noopener noreferrer"
        className="provenance-footer__link"
      >
        Calculated with NumPy {data.numpy_version} and SciPy {data.scipy_version}
        <span className="sr-only"> (opens provenance JSON in new tab)</span>
      </a>
      <span className="provenance-footer__date" aria-hidden="true">
        {' · baseline 2026-05-30'}
      </span>
    </footer>
  );
}
