/**
 * ProvenanceFooter — global <footer> landmark.
 *
 * Renders on every route, outside <main>, once in the global shell.
 * Fetches numpy_version, scipy_version, and domains from /data/provenance.json.
 *
 * Per-domain conditional behavior (DESIGN_SYSTEM.md §15.5(b); CDA SME PROMOTE-2 B5b):
 *   - Renders the "Calculated with NumPy X and SciPy Y" line only when:
 *     (a) the active domain is absent (i.e., we are on a non-domain view like
 *         methodology), OR
 *     (b) the active domain slug is present in provenance.json's `domains` block.
 *   - Renders nothing on domain views whose slug is NOT in provenance.json
 *     (e.g., food, which has not yet been rebaselined under the pinned toolchain).
 *   - Render-nothing fallback: if fetch fails or required fields are absent,
 *     renders null. Never renders "NaN" or stale strings.
 *
 * Design tokens: --font-size-xs + --color-text-caption (~4.60:1 on white — WCAG AA).
 * Top border via --color-border. No new tokens introduced.
 *
 * DESIGN_SYSTEM.md §11 inventory + §15.5(b).
 * Gate: UI/UX PASS-WITH-NOTES (docs/status/2026-05-30-promote-ui-ux-verdict.md).
 * SME: CDA SME PROMOTE-2 PASS-WITH-NOTES (docs/status/2026-05-30-promote2-cda-sme-verdict.md).
 */

import { useState, useEffect } from 'react';

interface ProvenanceDomainEntry {
  version: string;
  model_count: number;
  sha256: string;
  guard: string;
}

interface ProvenanceData {
  numpy_version?: string;
  scipy_version?: string;
  domains?: Record<string, ProvenanceDomainEntry>;
}

interface ProvenanceFooterProps {
  /** The currently active domain slug (e.g. 'family', 'food', 'holidays').
   *  Pass undefined / null when on a non-domain route (methodology, data, etc.) —
   *  in that case the footer always renders if versions are available. */
  activeDomain?: string | null;
}

export function ProvenanceFooter({ activeDomain }: ProvenanceFooterProps) {
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

  // Render nothing if fetch failed or version fields absent
  if (
    !data ||
    typeof data.numpy_version !== 'string' ||
    !data.numpy_version ||
    typeof data.scipy_version !== 'string' ||
    !data.scipy_version
  ) {
    return null;
  }

  // Per-domain conditional: if an active domain is set and it is NOT listed in
  // provenance.json's domains block, render nothing (no false provenance claim).
  if (
    activeDomain &&
    (!data.domains || !(activeDomain in data.domains))
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
