/**
 * labelPlacement.ts - Deterministic collision-aware label placement.
 *
 * Pure function: no DOM access, no Math.random, no Date.now, no closure over
 * external state. Same input produces byte-identical output (AC1, AC8-iii).
 *
 * AC1 contract:
 *   - accepts label specs (text, anchor coordinate, estimated width) + chart bounds
 *   - returns placed boxes + a `hidden` array for fallback items
 *   - deterministic: ties broken by stable lexicographic label key
 *   - minimum separation between any two cluster-label bounding boxes: 16px (AC2)
 *
 * Fallback path: items that cannot be placed without violating minSeparation
 * or going out-of-bounds are returned in the `hidden` array (AC8-iv).
 *
 * TM-C: DESIGN_SYSTEM.md §3.1.1(c) compliance.
 * Gate verdicts: CDA SME PASS-WITH-NOTES; UI/UX PASS-WITH-NOTES
 * (docs/status/2026-06-10-termmap-layout-verdicts.md, TM-C section).
 */

export interface LabelSpec {
  /** Stable string key used for deterministic tie-breaking. */
  key: string;
  /** Requested anchor X coordinate in SVG space. */
  anchorX: number;
  /** Requested anchor Y coordinate in SVG space. */
  anchorY: number;
  /** Estimated width of the label in pixels. */
  width: number;
  /** Estimated height of the label in pixels. */
  height: number;
  /**
   * Optional: list of point coordinates this label must not occlude.
   * Each entry is [x, y] in SVG space. The label box must not contain any point.
   */
  avoidPoints?: [number, number][];
}

export interface ChartBounds {
  /** Left edge (minimum X, e.g. pad.l). */
  x1: number;
  /** Top edge (minimum Y, e.g. pad.t). */
  y1: number;
  /** Right edge (maximum X, e.g. W - pad.r). */
  x2: number;
  /** Bottom edge (maximum Y, e.g. H - pad.b). */
  y2: number;
}

export interface PlacedLabel {
  key: string;
  /** Final placed X position (left edge of the label box). */
  x: number;
  /** Final placed Y position (top edge of the label box). */
  y: number;
  /** Width of the placed label. */
  width: number;
  /** Height of the placed label. */
  height: number;
  /** Whether a leader line was drawn (true when displaced from anchor). */
  hasLeaderLine: boolean;
  /** Leader line start (anchor point for leader). */
  leaderFromX: number;
  leaderFromY: number;
  /** Leader line end (edge of label box nearest to anchor). */
  leaderToX: number;
  leaderToY: number;
}

export interface PlacementResult {
  placed: PlacedLabel[];
  /** Labels that could not be placed within bounds or without violating minSeparation. */
  hidden: LabelSpec[];
}

/**
 * LEADER_LINE_THRESHOLD: displacement (px) beyond which a leader line is drawn.
 * Below this value the label is close enough to its anchor that no line is needed.
 */
const LEADER_LINE_THRESHOLD = 12;

/**
 * CLUSTER_LABEL_MIN_SEP: minimum gap (px) between any two placed cluster-label bounding boxes.
 * Binding per §3.1.1(c) and AC2.
 */
const CLUSTER_LABEL_MIN_SEP = 16;

/**
 * POINT_OCCLUSION_MARGIN: a label box must not have any term-dot position inside this
 * margin of the label box (in px). This catches near-misses as well as exact containment.
 */
const POINT_OCCLUSION_MARGIN = 3;

/**
 * Candidate displacement offsets (dx, dy) tried in order when the initial anchor
 * position is blocked. Ordered from small to large displacement to prefer minimal
 * movement. Deterministic iteration order.
 */
const DISPLACEMENT_CANDIDATES: [number, number][] = [
  [  0,  -28 ],   // N
  [  0,   28 ],   // S
  [ -28,   0 ],   // W
  [  28,   0 ],   // E
  [ -20,  -20 ],  // NW
  [  20,  -20 ],  // NE
  [ -20,   20 ],  // SW
  [  20,   20 ],  // SE
  [  0,  -52 ],   // N-far
  [  0,   52 ],   // S-far
  [ -52,   0 ],   // W-far
  [  52,   0 ],   // E-far
  [ -40,  -40 ],  // NW-far
  [  40,  -40 ],  // NE-far
  [ -40,   40 ],  // SW-far
  [  40,   40 ],  // SE-far
];

/**
 * Check whether two axis-aligned boxes overlap within a given minimum separation.
 * Returns true if the boxes are closer than `minSep` pixels in either axis, i.e.
 * they violate the minimum-separation rule.
 */
function boxesViolateSeparation(
  ax1: number, ay1: number, ax2: number, ay2: number,
  bx1: number, by1: number, bx2: number, by2: number,
  minSep: number,
): boolean {
  // Expand box A by minSep on all sides, then check overlap with box B.
  const aEx1 = ax1 - minSep;
  const aEy1 = ay1 - minSep;
  const aEx2 = ax2 + minSep;
  const aEy2 = ay2 + minSep;
  return !(bx2 < aEx1 || bx1 > aEx2 || by2 < aEy1 || by1 > aEy2);
}

/**
 * Check whether a box contains a point (with margin).
 */
function boxContainsPoint(
  bx1: number, by1: number, bx2: number, by2: number,
  px: number, py: number,
  margin: number,
): boolean {
  return (
    px >= bx1 - margin && px <= bx2 + margin &&
    py >= by1 - margin && py <= by2 + margin
  );
}

/**
 * Check whether a box fits within chart bounds.
 */
function boxInBounds(
  bx1: number, by1: number, bx2: number, by2: number,
  bounds: ChartBounds,
): boolean {
  return bx1 >= bounds.x1 && bx2 <= bounds.x2 && by1 >= bounds.y1 && by2 <= bounds.y2;
}

/**
 * Compute the nearest-edge leader line endpoint from the anchor to the label box.
 * Returns the point on the label box edge nearest to the anchor.
 */
function nearestEdgePoint(
  anchorX: number, anchorY: number,
  bx1: number, by1: number, bx2: number, by2: number,
): [number, number] {
  const cx = (bx1 + bx2) / 2;
  const cy = (by1 + by2) / 2;
  const dx = anchorX - cx;
  const dy = anchorY - cy;
  const halfW = (bx2 - bx1) / 2;
  const halfH = (by2 - by1) / 2;
  // Scale to box edge
  const scaleX = halfW / (Math.abs(dx) || 1);
  const scaleY = halfH / (Math.abs(dy) || 1);
  const scale = Math.min(scaleX, scaleY);
  return [cx + dx * scale, cy + dy * scale];
}

/**
 * placeLabels - deterministic greedy collision-aware label placement.
 *
 * Processes labels in stable sorted order (by `key`). For each label, tries the
 * anchor position first; if blocked (collision with already-placed labels or
 * point occlusion), iterates through DISPLACEMENT_CANDIDATES in order.
 * Falls back to `hidden` if no candidate satisfies bounds + separation.
 *
 * minSeparation defaults to CLUSTER_LABEL_MIN_SEP (16px) per §3.1.1(c) AC2.
 *
 * AC1 PURE FUNCTION CONTRACT:
 *   - no DOM access
 *   - no Math.random
 *   - no Date.now
 *   - no closure over external mutable state
 *   - same input -> byte-identical output
 */
export function placeLabels(
  labels: LabelSpec[],
  bounds: ChartBounds,
  minSeparation: number = CLUSTER_LABEL_MIN_SEP,
): PlacementResult {
  // Sort by key for deterministic processing order (AC1, AC8-iii).
  const sorted = [...labels].sort((a, b) =>
    a.key < b.key ? -1 : a.key > b.key ? 1 : 0
  );

  const placed: PlacedLabel[] = [];
  const hidden: LabelSpec[] = [];

  for (const spec of sorted) {
    const { key, anchorX, anchorY, width, height, avoidPoints } = spec;

    // Try anchor position first (displacement = [0, 0]), then displacement candidates.
    const candidates: [number, number][] = [[0, 0], ...DISPLACEMENT_CANDIDATES];
    let resolved = false;

    for (const [dx, dy] of candidates) {
      // Label box: top-left corner is (anchorX + dx - width/2, anchorY + dy - height/2)
      // using center-anchor convention.
      const bx1 = anchorX + dx - width / 2;
      const by1 = anchorY + dy - height / 2;
      const bx2 = bx1 + width;
      const by2 = by1 + height;

      // Check bounds.
      if (!boxInBounds(bx1, by1, bx2, by2, bounds)) continue;

      // Check collision with already-placed labels (minimum separation rule).
      let blocked = false;
      for (const p of placed) {
        if (boxesViolateSeparation(bx1, by1, bx2, by2, p.x, p.y, p.x + p.width, p.y + p.height, minSeparation)) {
          blocked = true;
          break;
        }
      }
      if (blocked) continue;

      // Check point occlusion.
      if (avoidPoints) {
        for (const [px, py] of avoidPoints) {
          if (boxContainsPoint(bx1, by1, bx2, by2, px, py, POINT_OCCLUSION_MARGIN)) {
            blocked = true;
            break;
          }
        }
      }
      if (blocked) continue;

      // Accepted: compute leader line.
      const displacement = Math.sqrt(dx * dx + dy * dy);
      const hasLeaderLine = displacement > LEADER_LINE_THRESHOLD;
      const [leaderToX, leaderToY] = hasLeaderLine
        ? nearestEdgePoint(anchorX, anchorY, bx1, by1, bx2, by2)
        : [anchorX, anchorY];

      placed.push({
        key,
        x: bx1,
        y: by1,
        width,
        height,
        hasLeaderLine,
        leaderFromX: anchorX,
        leaderFromY: anchorY,
        leaderToX,
        leaderToY,
      });
      resolved = true;
      break;
    }

    if (!resolved) {
      hidden.push(spec);
    }
  }

  return { placed, hidden };
}
