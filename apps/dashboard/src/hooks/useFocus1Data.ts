/**
 * useFocus1Data — lazy-loads {domain}-focus1.json only when called.
 *
 * Caches per domain: does not re-fetch if domain hasn't changed.
 * Returns { data, loading, error }.
 */

import { useState, useEffect } from 'react';
import type { Focus1Data } from '../data/types';

interface UseFocus1DataResult {
  data: Focus1Data | null;
  loading: boolean;
  error: string | null;
}

/** Per-domain cache so switching domains doesn't re-fetch already-loaded data. */
const cache: Record<string, Focus1Data> = {};

export function useFocus1Data(domainSlug: string): UseFocus1DataResult {
  // Initialize directly from cache if available
  const [data, setData] = useState<Focus1Data | null>(() => cache[domainSlug] ?? null);
  const [loading, setLoading] = useState<boolean>(() => !(domainSlug in cache));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Already cached — no fetch needed
    if (domainSlug in cache) return;

    let cancelled = false;

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const resp = await fetch(`/data/${domainSlug}-focus1.json`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const json = (await resp.json()) as Focus1Data;
        if (cancelled) return;
        cache[domainSlug] = json;
        setData(json);
        setLoading(false);
      } catch (e: unknown) {
        if (cancelled) return;
        const msg = e instanceof Error ? e.message : 'Failed to load Focus 1 data';
        setError(msg);
        setLoading(false);
      }
    };

    void load();
    return () => { cancelled = true; };
  }, [domainSlug]);

  return { data, loading, error };
}
