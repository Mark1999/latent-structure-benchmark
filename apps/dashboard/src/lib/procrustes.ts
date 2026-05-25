/**
 * procrustes.ts — Orthogonal Procrustes alignment for 2-D point sets.
 *
 * Prevents the Term Map from flipping or rotating when models are toggled:
 * each new MDS solution is aligned to the reference (all-models) solution
 * before rendering.
 *
 * Algorithm: optimal 2-D rotation (Umeyama / Kabsch adapted to 2D).
 *   1. Center both point sets.
 *   2. Compute optimal rotation angle θ:
 *        θ = atan2( Σ (sc[i]·× tc[i]), Σ (sc[i]·· tc[i]) )
 *      where ·× is the 2D cross product and ·· is the 2D dot product.
 *   3. Apply rotation R(θ) to centered source.
 *   4. Translate result to target centroid.
 *
 * This minimises Σ ||R·sc[i] - tc[i]||² over all 2-D rotation matrices R,
 * without scaling (pure rotation + translation).
 *
 * No external dependencies.
 */

/** Align source coordinates to match target as closely as possible (rotation + translation). */
export function procrustesAlign(
  target: [number, number][],
  source: [number, number][]
): [number, number][] {
  const n = target.length;
  if (n === 0 || source.length !== n) return source.map(([x, y]): [number, number] => [x, y]);
  if (n === 1) return [[target[0][0], target[0][1]]];

  // ── 1. Center both sets ───────────────────────────────────────────────────
  let txSum = 0, tySum = 0, sxSum = 0, sySum = 0;
  for (let i = 0; i < n; i++) {
    txSum += target[i][0]; tySum += target[i][1];
    sxSum += source[i][0]; sySum += source[i][1];
  }
  const txMean = txSum / n, tyMean = tySum / n;
  const sxMean = sxSum / n, syMean = sySum / n;

  const tc: [number, number][] = target.map(([x, y]): [number, number] => [x - txMean, y - tyMean]);
  const sc: [number, number][] = source.map(([x, y]): [number, number] => [x - sxMean, y - syMean]);

  // ── 2. Optimal rotation angle ─────────────────────────────────────────────
  // θ = atan2( Σ (s×t), Σ (s·t) )
  // where s×t = sc[i][0]*tc[i][1] - sc[i][1]*tc[i][0]  (2D cross product)
  //       s·t = sc[i][0]*tc[i][0] + sc[i][1]*tc[i][1]  (2D dot product)
  let crossSum = 0, dotSum = 0;
  for (let i = 0; i < n; i++) {
    crossSum += sc[i][0] * tc[i][1] - sc[i][1] * tc[i][0];
    dotSum   += sc[i][0] * tc[i][0] + sc[i][1] * tc[i][1];
  }
  const theta = Math.atan2(crossSum, dotSum);
  const cosT = Math.cos(theta);
  const sinT = Math.sin(theta);

  // ── 3. Apply rotation and translate to target centroid ───────────────────
  // R = [[cosT, -sinT], [sinT, cosT]]
  // result[i] = R * sc[i] + target_centroid
  return sc.map(([x, y]): [number, number] => [
    cosT * x - sinT * y + txMean,
    sinT * x + cosT * y + tyMean,
  ]);
}
