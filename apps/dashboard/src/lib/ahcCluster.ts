/**
 * ahcCluster.ts — Agglomerative Hierarchical Clustering (average linkage).
 *
 * Used to re-assign cluster labels when MDS coordinates update after a
 * model toggle. Cluster count is fixed at the reference count so labels
 * remain comparable to the pre-computed clusters in the domain JSON.
 *
 * No external dependencies.
 */

/**
 * Run AHC with average linkage on a distance matrix.
 *
 * @param distances n×n dissimilarity matrix.
 * @param nClusters Target number of clusters (≥ 1).
 * @returns Array of length n, where result[i] is the 0-based cluster index
 *          for item i.
 */
export function ahcCluster(distances: number[][], nClusters: number): number[] {
  const n = distances.length;
  if (n === 0) return [];
  if (nClusters <= 0) return new Array<number>(n).fill(0);
  const k = Math.min(nClusters, n);

  // ── Initialise: each item is its own cluster ──────────────────────────────
  // cluster[i] = Set of original item indices in cluster i
  const clusters: Set<number>[] = Array.from({ length: n }, (_, i) => new Set([i]));
  // alive[i] = true while cluster i has not been merged away
  const alive: boolean[] = new Array<boolean>(n).fill(true);

  // Current number of clusters
  let numClusters = n;

  // ── Average-linkage distance between two clusters ─────────────────────────
  function clusterDist(a: Set<number>, b: Set<number>): number {
    let sum = 0;
    let count = 0;
    for (const i of a) {
      for (const j of b) {
        sum += distances[i][j];
        count++;
      }
    }
    return count > 0 ? sum / count : Infinity;
  }

  // ── Merge until target cluster count reached ───────────────────────────────
  while (numClusters > k) {
    let bestDist = Infinity;
    let bestA = -1;
    let bestB = -1;

    // Find the pair of alive clusters with minimum average-linkage distance
    const aliveIndices: number[] = [];
    for (let i = 0; i < n; i++) {
      if (alive[i]) aliveIndices.push(i);
    }

    for (let ai = 0; ai < aliveIndices.length; ai++) {
      for (let bi = ai + 1; bi < aliveIndices.length; bi++) {
        const i = aliveIndices[ai];
        const j = aliveIndices[bi];
        const d = clusterDist(clusters[i], clusters[j]);
        if (d < bestDist) {
          bestDist = d;
          bestA = i;
          bestB = j;
        }
      }
    }

    if (bestA === -1) break; // shouldn't happen

    // Merge bestB into bestA; mark bestB dead
    for (const idx of clusters[bestB]) {
      clusters[bestA].add(idx);
    }
    clusters[bestB].clear();
    alive[bestB] = false;
    numClusters--;
  }

  // ── Build result array: map each item index to its cluster label ──────────
  const result = new Array<number>(n).fill(0);
  let label = 0;
  for (let i = 0; i < n; i++) {
    if (!alive[i]) continue;
    for (const itemIdx of clusters[i]) {
      result[itemIdx] = label;
    }
    label++;
  }

  return result;
}
