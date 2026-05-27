/**
 * familyUtils.ts — provider grouping and within-family similarity utilities
 * for Focus 2 (Within-Provider Family Comparison).
 *
 * DESIGN_SYSTEM.md §14
 */

import type { PublishedModel } from '../data/types';

// Provider display colors — shared across Focus 2 components
// Matches PROVIDER_COLORS in ContentArea, MDSPlot, FreeListCompare, PileStructure
export const PROVIDER_DISPLAY_COLORS: Record<string, string> = {
  anthropic:  '#d97706',
  openai:     '#10a37f',
  google:     '#4285f4',
  meta:       '#0668e1',
  xai:        '#1d1d1f',
  mistral:    '#f97316',
  deepseek:   '#0ea5e9',
  microsoft:  '#00a4ef',
};

const PROVIDER_ORDER = [
  'anthropic', 'openai', 'google', 'meta', 'xai', 'mistral', 'deepseek', 'microsoft',
];

/**
 * Map OpenRouter models to their logical provider (mirrors App.tsx displayProvider).
 */
export function displayProvider(model: PublishedModel): string {
  if (model.provider === 'openrouter') {
    const map: Record<string, string> = {
      gpt:      'openai',
      llama:    'meta',
      mistral:  'mistral',
      deepseek: 'deepseek',
      phi:      'microsoft',
    };
    return map[model.family] || model.provider;
  }
  return model.provider;
}

/**
 * Group all models by their logical provider.
 * Returns a Record<providerKey, PublishedModel[]>.
 * Provider order follows PROVIDER_ORDER where known; unknown providers appended alphabetically.
 */
export function groupModelsByProvider(
  models: PublishedModel[],
): Record<string, PublishedModel[]> {
  const groups: Record<string, PublishedModel[]> = {};
  for (const model of models) {
    const provider = displayProvider(model);
    if (!groups[provider]) groups[provider] = [];
    groups[provider].push(model);
  }
  return groups;
}

/**
 * Returns providers with 2 or more models, sorted by PROVIDER_ORDER then alphabetically.
 */
export function getMultiModelFamilies(
  grouping: Record<string, PublishedModel[]>,
): string[] {
  const providers = Object.keys(grouping).filter((p) => grouping[p].length >= 2);
  return sortProviders(providers);
}

/**
 * Returns providers with exactly 1 model, sorted by PROVIDER_ORDER then alphabetically.
 */
export function getSingleModelFamilies(
  grouping: Record<string, PublishedModel[]>,
): string[] {
  const providers = Object.keys(grouping).filter((p) => grouping[p].length === 1);
  return sortProviders(providers);
}

function sortProviders(providers: string[]): string[] {
  return [...providers].sort((a, b) => {
    const ai = PROVIDER_ORDER.indexOf(a);
    const bi = PROVIDER_ORDER.indexOf(b);
    if (ai !== -1 && bi !== -1) return ai - bi;
    if (ai !== -1) return -1;
    if (bi !== -1) return 1;
    return a.localeCompare(b);
  });
}

/**
 * Get all pairwise combinations from an array of IDs.
 * For N items returns N*(N-1)/2 pairs.
 */
export function getPairs(ids: string[]): Array<[string, string]> {
  const pairs: Array<[string, string]> = [];
  for (let i = 0; i < ids.length; i++) {
    for (let j = i + 1; j < ids.length; j++) {
      pairs.push([ids[i], ids[j]]);
    }
  }
  return pairs;
}

/**
 * Compute mean of pairwise similarity scores for a set of model IDs.
 * similarityMatrix is indexed positionally (models array order).
 * Returns null if fewer than 2 models provided or matrix is unavailable.
 *
 * CDA SME note 2: N=2 → single pair (not "mean"), N=3 → mean of 3 pairs.
 */
export function computeWithinFamilySimilarity(
  familyModelIds: string[],
  allModels: PublishedModel[],
  similarityMatrix: number[][],
): number | null {
  if (familyModelIds.length < 2) return null;
  if (!similarityMatrix || similarityMatrix.length === 0) return null;

  const idToIdx: Record<string, number> = {};
  allModels.forEach((m, i) => { idToIdx[m.model_id] = i; });

  const pairs = getPairs(familyModelIds);
  let sum = 0;
  let count = 0;
  for (const [a, b] of pairs) {
    const ai = idToIdx[a];
    const bi = idToIdx[b];
    if (ai === undefined || bi === undefined) continue;
    const val = similarityMatrix[ai]?.[bi];
    if (val !== undefined && val !== null) {
      sum += val;
      count++;
    }
  }
  if (count === 0) return null;
  return sum / count;
}

/**
 * Get CI for a single pair from the similarity_ci array.
 * Returns null if not available.
 */
export function getPairCI(
  modelA: string,
  modelB: string,
  allModels: PublishedModel[],
  similarityCi: Array<Array<[number, number] | null>>,
): [number, number] | null {
  if (!similarityCi || similarityCi.length === 0) return null;
  const idToIdx: Record<string, number> = {};
  allModels.forEach((m, i) => { idToIdx[m.model_id] = i; });
  const ai = idToIdx[modelA];
  const bi = idToIdx[modelB];
  if (ai === undefined || bi === undefined) return null;
  return similarityCi[ai]?.[bi] ?? null;
}
