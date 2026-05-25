/**
 * cooccurrence.ts — per-model co-occurrence matrix pooling.
 *
 * Averages selected models' n×n co-occurrence matrices element-wise.
 * Equal weight per model (CDA SME M1 posture).
 */

/**
 * Pool co-occurrence matrices for a subset of models.
 *
 * @param allMatrices    Map of model_id → n×n co-occurrence matrix.
 * @param selectedModelIds Set of model IDs to include.
 * @param n              Matrix dimension (number of items).
 * @returns Averaged n×n matrix. Returns zero matrix if no models are selected.
 */
export function poolCooccurrence(
  allMatrices: Record<string, number[][]>,
  selectedModelIds: Set<string>,
  n: number
): number[][] {
  // Find the intersection of selectedModelIds and available matrices
  const available = Object.keys(allMatrices).filter((id) => selectedModelIds.has(id));

  // Initialise result matrix with zeros
  const result: number[][] = Array.from({ length: n }, () => new Array<number>(n).fill(0));

  if (available.length === 0) {
    return result;
  }

  // Accumulate
  for (const modelId of available) {
    const mat = allMatrices[modelId];
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        result[i][j] += mat[i][j];
      }
    }
  }

  // Divide by count (equal weight per CDA SME M1)
  const k = available.length;
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      result[i][j] /= k;
    }
  }

  return result;
}

/**
 * Convert a co-occurrence matrix to a dissimilarity matrix.
 * dissimilarity[i][j] = 1 - cooccurrence[i][j]
 *
 * Diagonal is set to 0 (each item is perfectly similar to itself).
 */
export function cooccurrenceToDistances(cooccurrence: number[][]): number[][] {
  const n = cooccurrence.length;
  return Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) =>
      i === j ? 0 : 1 - cooccurrence[i][j]
    )
  );
}
