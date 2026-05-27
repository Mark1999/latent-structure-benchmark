/**
 * Focus2FamilySalience — term salience rankings for the selected provider family.
 *
 * Reuses FreeListCompare scoped to family models (DESIGN_SYSTEM.md §14.6).
 * Data source: sutrop_csi from domain JSON.
 */

import { useMemo } from 'react';
import { FreeListCompare, type SutropCsiEntry } from './FreeListCompare';
import type { PublishedModel } from '../data/types';
import { groupModelsByProvider } from '../lib/familyUtils';
import {
  FOCUS2_SALIENCE_DESCRIPTION,
  FOCUS2_NO_PROVIDER_SELECTED,
} from '../copy/focus2';

interface Focus2FamilySalienceProps {
  models: PublishedModel[];
  sutropCsi: Record<string, SutropCsiEntry[]>;
  selectedProvider: string | null;
}

export function Focus2FamilySalience({
  models,
  sutropCsi,
  selectedProvider,
}: Focus2FamilySalienceProps) {
  const grouping = useMemo(() => groupModelsByProvider(models), [models]);

  const familyModelIds = useMemo(() => {
    if (!selectedProvider) return new Set<string>();
    return new Set((grouping[selectedProvider] || []).map((m) => m.model_id));
  }, [grouping, selectedProvider]);

  if (!selectedProvider) {
    return (
      <div className="f2-salience">
        <p className="f2-salience__desc">{FOCUS2_SALIENCE_DESCRIPTION}</p>
        <p className="f2-salience__no-selection">{FOCUS2_NO_PROVIDER_SELECTED}</p>
      </div>
    );
  }

  return (
    <div className="f2-salience">
      <p className="f2-salience__desc">{FOCUS2_SALIENCE_DESCRIPTION}</p>
      <FreeListCompare
        sutropCsi={sutropCsi}
        models={models}
        selectedModelIds={familyModelIds}
      />
    </div>
  );
}
