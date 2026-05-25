/**
 * smacof.ts — SMACOF (Scaling by Majorizing a Complicated Function) MDS solver.
 *
 * Implements classic SMACOF for 2-D metric MDS. No external dependencies.
 * Input: n×n dissimilarity matrix. Output: n×2 coordinates + final stress.
 *
 * Reference: Borg & Groenen (2005) "Modern Multidimensional Scaling", §8.
 */

export interface MDSResult {
  /** One [x, y] per item, in the same order as the input distance matrix rows. */
  coordinates: [number, number][];
  /** Normalized stress-1 at convergence. */
  stress: number;
}

/**
 * Compute 2-D Euclidean distance between two points.
 */
function dist2d(a: [number, number], b: [number, number]): number {
  const dx = a[0] - b[0];
  const dy = a[1] - b[1];
  return Math.sqrt(dx * dx + dy * dy);
}

/**
 * Compute normalized stress-1:
 *   sqrt( sum_ij (delta_ij - d_ij)^2 / sum_ij delta_ij^2 )
 * where delta = target dissimilarity, d = current embedding distance.
 */
function computeStress(
  delta: number[][],
  coords: [number, number][],
  n: number
): number {
  let num = 0;
  let den = 0;
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      const d = dist2d(coords[i], coords[j]);
      const diff = delta[i][j] - d;
      num += diff * diff;
      den += delta[i][j] * delta[i][j];
    }
  }
  return den > 0 ? Math.sqrt(num / den) : 0;
}

/**
 * Seeded pseudo-random number generator (xorshift32) for deterministic init.
 * Produces values in [0, 1).
 */
function makeRng(seed: number): () => number {
  let s = seed >>> 0;
  if (s === 0) s = 1;
  return () => {
    s ^= s << 13;
    s ^= s >> 17;
    s ^= s << 5;
    return (s >>> 0) / 4294967296;
  };
}

/**
 * SMACOF MDS solver.
 *
 * @param distances    n×n dissimilarity matrix (values in [0, 1] for co-occurrence derived dissimilarities).
 * @param dimensions   Number of output dimensions (must be 2 for this implementation).
 * @param maxIterations Maximum SMACOF iterations before stopping.
 * @param epsilon      Convergence threshold: stop when stress improvement < epsilon.
 * @param initialCoords Optional starting coordinates (length must equal n). When provided the
 *                     first iteration starts from these positions (enables warm restarts for
 *                     smooth animation as models are toggled).
 * @returns MDSResult with final coordinates and stress value.
 */
export function smacof(
  distances: number[][],
  dimensions: number,
  maxIterations: number,
  epsilon: number,
  initialCoords?: [number, number][]
): MDSResult {
  // This implementation is always 2D. Accept the dimensions param for API
  // symmetry with standard MDS callers; validate it here.
  if (dimensions !== 2) throw new Error('smacof: only 2D output is supported');

  const n = distances.length;

  if (n === 0) {
    return { coordinates: [], stress: 0 };
  }

  if (n === 1) {
    return { coordinates: [[0, 0]], stress: 0 };
  }

  // ── 1. Initialise coordinates ──────────────────────────────────────────────
  let coords: [number, number][];
  if (initialCoords && initialCoords.length === n) {
    // Deep copy so we don't mutate the caller's array
    coords = initialCoords.map(([x, y]): [number, number] => [x, y]);
  } else {
    const rng = makeRng(42);
    coords = Array.from({ length: n }, (): [number, number] => [
      rng() * 2 - 1,
      rng() * 2 - 1,
    ]);
  }

  // ── 2. Precompute denominator for stress (sum of squared dissimilarities) ──
  // This is invariant across iterations.
  let deltaSquaredSum = 0;
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      deltaSquaredSum += distances[i][j] * distances[i][j];
    }
  }

  // If all dissimilarities are 0, return current coords (already trivial solution)
  if (deltaSquaredSum === 0) {
    return { coordinates: coords, stress: 0 };
  }

  // ── 3. Initial stress ─────────────────────────────────────────────────────
  let prevStress = computeStress(distances, coords, n);

  // ── 4. SMACOF main loop ───────────────────────────────────────────────────
  // Pre-allocate B matrix and updated coords arrays for performance
  const B: number[][] = Array.from({ length: n }, () => new Array<number>(n).fill(0));
  const newCoords: [number, number][] = Array.from({ length: n }, (): [number, number] => [0, 0]);

  for (let iter = 0; iter < maxIterations; iter++) {
    // ── 4a. Compute current embedding distances and B matrix ─────────────
    for (let i = 0; i < n; i++) {
      B[i].fill(0);
    }

    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {
        const d = dist2d(coords[i], coords[j]);
        let bij = 0;
        if (d > 0) {
          bij = -distances[i][j] / d;
        }
        B[i][j] = bij;
        B[j][i] = bij;
      }
    }

    // Fill diagonal: B[i][i] = -sum of off-diagonal row i
    for (let i = 0; i < n; i++) {
      let diagVal = 0;
      for (let j = 0; j < n; j++) {
        if (j !== i) diagVal += B[i][j];
      }
      B[i][i] = -diagVal;
    }

    // ── 4b. Guttman transform: X_new = (1/n) * B * X ─────────────────────
    for (let i = 0; i < n; i++) {
      let sx = 0;
      let sy = 0;
      for (let j = 0; j < n; j++) {
        sx += B[i][j] * coords[j][0];
        sy += B[i][j] * coords[j][1];
      }
      newCoords[i][0] = sx / n;
      newCoords[i][1] = sy / n;
    }

    // Copy newCoords → coords
    for (let i = 0; i < n; i++) {
      coords[i][0] = newCoords[i][0];
      coords[i][1] = newCoords[i][1];
    }

    // ── 4c. Recompute stress and check convergence ─────────────────────────
    const currentStress = computeStress(distances, coords, n);
    const improvement = prevStress - currentStress;

    if (improvement < epsilon && iter > 0) {
      break;
    }

    prevStress = currentStress;
  }

  return { coordinates: coords, stress: prevStress };
}

