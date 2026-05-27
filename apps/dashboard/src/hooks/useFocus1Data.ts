/**
 * useFocus1Data — lazy-loads {domain}-focus1.json only when called.
 *
 * Caches per domain: does not re-fetch if domain hasn't changed.
 * Returns { data, loading, error }.
 */

import { useState, useEffect, useRef } from 'react';
import type { Focus1Data } from '../data/types';

interface UseFocus1DataResult {
  data: Focus1Data | null;
  loading: boolean;
  error: string | null;
}

/** Per-domain cache so switching domains doesn't re-fetch already-loaded data. */
const cache: Record<string, Focus1Data> = {};

export function useFocus1Data(domainSlug: string): UseFocus1DataResult {
  const [data, setData] = useState<Focus1Data | null>(() => cache[domainSlug] ?? null);
  const [loading, setLoading] = useState<boolean>(() => !(domainSlug in cache));
  const [error, setError] = useState<string | null>(null);

  // Track latest domain to avoid state updates after domain switch
  const latestDomain = useRef(domainSlug);
  latestDomain.current = domainSlug;

  useEffect(() => {
    // Already cached — nothing to do
    if (domainSlug in cache) {
      setData(cache[domainSlug]);
      setLoading(false);
      setError(null);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    fetch(`/data/${domainSlug}-focus1.json`)
      .then(async (resp) => {
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        return resp.json() as Promise<Focus1Data>;
      })
      .then((json) => {
        if (cancelled) return;
        cache[domainSlug] = json;
        if (latestDomain.current === domainSlug) {
          setData(json);
          setLoading(false);
        }
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        if (latestDomain.current === domainSlug) {
          const msg = e instanceof Error ? e.message : 'Failed to load Focus 1 data';
          setError(msg);
          setLoading(false);
        }
      });

    return () => { cancelled = true; };
  }, [domainSlug]);

  return { data, loading, error };
}
