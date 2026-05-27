/**
 * Focus2FamilyPiles — pile structures for the selected provider family.
 *
 * Reuses PileStructure scoped to family models (DESIGN_SYSTEM.md §14.6).
 * Data source: centroid_piles from domain JSON.
 */

import { useMemo } from 'react';
import { PileStructure } from './PileStructure';
import type { PublishedModel } from '../data/types';
import type { ModelPileData } from './TermMap';
import { groupModelsByProvider } from '../lib/familyUtils';
import {
  FOCUS2_PILES_DESCRIPTION,
  FOCUS2_NO_PROVIDER_SELECTED,
} from '../copy/focus2';

interface Focus2FamilyPilesProps {
  models: PublishedModel[];
  centroidPiles: Record<string, ModelPileData> | undefined;
  selectedProvider: string | null;
}

export function Focus2FamilyPiles({
  models,
  centroidPiles,
  selectedProvider,
}: Focus2FamilyPilesProps) {
  const grouping = useMemo(() => groupModelsByProvider(models), [models]);

  const familyModelIds = useMemo(() => {
    if (!selectedProvider) return new Set<string>();
    return new Set((grouping[selectedProvider] || []).map((m) => m.model_id));
  }, [grouping, selectedProvider]);

  if (!selectedProvider) {
    return (
      <div className="f2-piles">
        <p className="f2-piles__desc">{FOCUS2_PILES_DESCRIPTION}</p>
        <p className="f2-piles__no-selection">{FOCUS2_NO_PROVIDER_SELECTED}</p>
      </div>
    );
  }

  if (!centroidPiles) {
    return (
      <div className="f2-piles">
        <p className="f2-piles__desc">{FOCUS2_PILES_DESCRIPTION}</p>
        <p className="f2-piles__no-selection">Pile structure data not available for this domain.</p>
      </div>
    );
  }

  return (
    <div className="f2-piles">
      <p className="f2-piles__desc">{FOCUS2_PILES_DESCRIPTION}</p>
      <PileStructure
        centroidPiles={centroidPiles}
        models={models}
        selectedModelIds={familyModelIds}
      />
    </div>
  );
}
