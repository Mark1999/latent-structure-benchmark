/**
 * Focus2FamilyOverview — ranked family cards sorted by within-family similarity.
 *
 * DESIGN_SYSTEM.md §14.3, §14.12
 * CDA SME binding notes applied:
 *   Note 1: Single-model families — show note, no similarity computed.
 *   Note 2: N=2 → "Pairwise similarity (1 pair)"; not "mean".
 *   Note 3: N=3 → "Mean pairwise similarity (3 pairs)".
 *   Note 7: Individual pairwise scores always visible (not collapsed).
 *
 * Forbidden vocabulary: no "provider consensus", no "family agreement".
 */

import type { PublishedModel } from '../data/types';
import {
  groupModelsByProvider,
  getMultiModelFamilies,
  getSingleModelFamilies,
  computeWithinFamilySimilarity,
  getPairs,
  getPairCI,
  PROVIDER_DISPLAY_COLORS,
} from '../lib/familyUtils';
import {
  FOCUS2_OVERVIEW_DESCRIPTION,
  FOCUS2_SINGLE_MODEL_NOTE,
} from '../copy/focus2';

interface Focus2FamilyOverviewProps {
  models: PublishedModel[];
  similarityMatrix: number[][];
  similarityCi: Array<Array<[number, number] | null>>;
  onSelectProvider: (provider: string) => void;
}

function shortModelName(modelId: string): string {
  return modelId.split('/').pop() || modelId;
}

export function Focus2FamilyOverview({
  models,
  similarityMatrix,
  similarityCi,
  onSelectProvider,
}: Focus2FamilyOverviewProps) {
  const grouping = groupModelsByProvider(models);
  const multiModelFamilies = getMultiModelFamilies(grouping);
  const singleModelFamilies = getSingleModelFamilies(grouping);

  // Build ranked cards for multi-model families (sorted by mean similarity desc)
  type FamilyCard = {
    provider: string;
    models: PublishedModel[];
    meanSimilarity: number | null;
    pairs: Array<{
      a: string;
      b: string;
      similarity: number | null;
      ci: [number, number] | null;
    }>;
  };

  const familyCards: FamilyCard[] = multiModelFamilies.map((provider) => {
    const familyModels = grouping[provider] || [];
    const familyIds = familyModels.map((m) => m.model_id);
    const meanSim = computeWithinFamilySimilarity(familyIds, models, similarityMatrix);

    const idToIdx: Record<string, number> = {};
    models.forEach((m, i) => { idToIdx[m.model_id] = i; });

    const pairs = getPairs(familyIds).map(([a, b]) => {
      const ai = idToIdx[a];
      const bi = idToIdx[b];
      const sim = (ai !== undefined && bi !== undefined)
        ? (similarityMatrix[ai]?.[bi] ?? null)
        : null;
      const ci = getPairCI(a, b, models, similarityCi);
      return { a, b, similarity: sim, ci };
    });

    return {
      provider,
      models: familyModels,
      meanSimilarity: meanSim,
      pairs,
    };
  });

  // Sort by mean similarity descending (null goes last)
  familyCards.sort((a, b) => {
    if (a.meanSimilarity === null && b.meanSimilarity === null) return 0;
    if (a.meanSimilarity === null) return 1;
    if (b.meanSimilarity === null) return -1;
    return b.meanSimilarity - a.meanSimilarity;
  });

  function formatSimilarityLabel(nModels: number): string {
    if (nModels === 2) {
      return 'Pairwise similarity (1 pair):';
    }
    // For N models, pairs = N*(N-1)/2
    const nPairs = (nModels * (nModels - 1)) / 2;
    return `Mean pairwise similarity (${nPairs} pair${nPairs !== 1 ? 's' : ''}):`;
  }

  return (
    <div className="f2-overview">
      <p className="f2-overview__desc">{FOCUS2_OVERVIEW_DESCRIPTION}</p>

      {familyCards.map((card) => {
        const dotColor = PROVIDER_DISPLAY_COLORS[card.provider] || '#888';
        const nModels = card.models.length;

        return (
          <div
            key={card.provider}
            className="f2-card"
            role="button"
            tabIndex={0}
            onClick={() => onSelectProvider(card.provider)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onSelectProvider(card.provider);
              }
            }}
            aria-label={`View ${card.provider} family similarity`}
          >
            <div className="f2-card__header">
              <span className="f2-card__dot" style={{ backgroundColor: dotColor }} />
              <span className="f2-card__name">
                {card.provider.charAt(0).toUpperCase() + card.provider.slice(1)}
              </span>
              <span className="f2-card__count">{nModels} models</span>
            </div>

            {card.meanSimilarity !== null && (
              <div className="f2-card__similarity">
                <span className="f2-card__similarity-label">
                  {formatSimilarityLabel(nModels)}{' '}
                </span>
                {card.meanSimilarity.toFixed(2)}
                {/* For N=2, show CI inline if available */}
                {nModels === 2 && card.pairs[0]?.ci && (
                  <span className="f2-card__pair-ci">
                    {' '}(95% CI [{card.pairs[0].ci[0].toFixed(2)}, {card.pairs[0].ci[1].toFixed(2)}])
                  </span>
                )}
              </div>
            )}

            {/* Individual pairs always visible (CDA SME note 7) */}
            {card.pairs.length > 0 && (
              <div className="f2-card__pairs">
                {card.pairs.map(({ a, b, similarity, ci }) => (
                  <div key={`${a}--${b}`} className="f2-card__pair-row">
                    <span className="f2-card__pair-names">
                      {shortModelName(a)} × {shortModelName(b)}
                    </span>
                    <span className="f2-card__pair-value">
                      {similarity !== null ? similarity.toFixed(3) : '—'}
                    </span>
                    {ci && (
                      <span className="f2-card__pair-ci">
                        [{ci[0].toFixed(3)}, {ci[1].toFixed(3)}]
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}

      {/* Single-model families — §14.12 normal first-class state */}
      {singleModelFamilies.length > 0 && (
        <>
          <p className="f2-overview__section-heading">Single-model providers</p>
          {singleModelFamilies.map((provider) => {
            const familyModels = grouping[provider] || [];
            const dotColor = PROVIDER_DISPLAY_COLORS[provider] || '#888';
            return (
              <div
                key={provider}
                className="f2-card f2-card--single"
                aria-label={`${provider} — single-model provider`}
              >
                <div className="f2-card__header">
                  <span className="f2-card__dot" style={{ backgroundColor: dotColor }} />
                  <span className="f2-card__name">
                    {provider.charAt(0).toUpperCase() + provider.slice(1)}
                  </span>
                  <span className="f2-card__count">1 model</span>
                </div>
                <p className="f2-card__single-note">
                  {familyModels[0]?.model_id && (
                    <span>{shortModelName(familyModels[0].model_id)} — </span>
                  )}
                  {FOCUS2_SINGLE_MODEL_NOTE}
                </p>
              </div>
            );
          })}
        </>
      )}
    </div>
  );
}
