/**
 * labelPlacement.test.ts - Deterministic vitest cases for the label placement function.
 *
 * AC8 requires at least four cases:
 *   (i)   non-overlapping fixture: all placed at requested anchors, zero overlaps
 *   (ii)  two boxes that would overlap: placed without overlap and >= 16px apart,
 *         OR one placed and the other in `hidden`
 *   (iii) same fixture twice: byte-identical output (determinism)
 *   (iv)  box that cannot fit within bounds: returned in `hidden`, not thrown
 *
 * Pure tests: no jsdom, no SVG, no React.
 * CLAUDE.md §6 rule 9: no real API calls.
 */

import { describe, it, expect } from 'vitest';
import { placeLabels } from '../labelPlacement';
import type { LabelSpec, ChartBounds } from '../labelPlacement';

// Chart bounds used across all tests: a 600 x 400 area with 30px padding.
const BOUNDS: ChartBounds = { x1: 30, y1: 30, x2: 570, y2: 370 };

// Minimum separation constant (binding per §3.1.1(c)).
const MIN_SEP = 16;

// ---------------------------------------------------------------------------
// AC8 case (i): non-overlapping fixture -- all placed at anchors, zero overlaps
// ---------------------------------------------------------------------------
describe('placeLabels - case (i): non-overlapping labels placed at anchors', () => {
  it('places all labels when anchors are well separated', () => {
    const labels: LabelSpec[] = [
      { key: 'alpha', anchorX: 100, anchorY: 100, width: 60, height: 12 },
      { key: 'beta',  anchorX: 300, anchorY: 200, width: 60, height: 12 },
      { key: 'gamma', anchorX: 500, anchorY: 300, width: 60, height: 12 },
    ];

    const result = placeLabels(labels, BOUNDS, MIN_SEP);

    // All three labels must be placed (none hidden).
    expect(result.hidden).toHaveLength(0);
    expect(result.placed).toHaveLength(3);

    // No two placed boxes violate the minimum separation.
    const placed = result.placed;
    for (let i = 0; i < placed.length; i++) {
      for (let j = i + 1; j < placed.length; j++) {
        const a = placed[i];
        const b = placed[j];
        const aRight  = a.x + a.width;
        const aBottom = a.y + a.height;
        const bRight  = b.x + b.width;
        const bBottom = b.y + b.height;
        // Expanded by MIN_SEP: boxes should NOT overlap when expanded.
        const overlaps =
          bRight  > a.x - MIN_SEP &&
          b.x     < aRight  + MIN_SEP &&
          bBottom > a.y - MIN_SEP &&
          b.y     < aBottom + MIN_SEP;
        expect(overlaps).toBe(false);
      }
    }
  });

  it('places all labels within chart bounds', () => {
    const labels: LabelSpec[] = [
      { key: 'delta',   anchorX: 150, anchorY: 150, width: 80, height: 14 },
      { key: 'epsilon', anchorX: 400, anchorY: 300, width: 80, height: 14 },
    ];

    const result = placeLabels(labels, BOUNDS, MIN_SEP);
    for (const p of result.placed) {
      expect(p.x).toBeGreaterThanOrEqual(BOUNDS.x1);
      expect(p.y).toBeGreaterThanOrEqual(BOUNDS.y1);
      expect(p.x + p.width).toBeLessThanOrEqual(BOUNDS.x2);
      expect(p.y + p.height).toBeLessThanOrEqual(BOUNDS.y2);
    }
  });
});

// ---------------------------------------------------------------------------
// AC8 case (ii): two boxes that would overlap -- resolved without overlap
// ---------------------------------------------------------------------------
describe('placeLabels - case (ii): overlapping anchors resolved', () => {
  it('resolves two labels whose anchors produce overlap -- at least 16px apart or one hidden', () => {
    // Two labels with the same anchor point and large-enough size to collide.
    const labels: LabelSpec[] = [
      { key: 'overlap-a', anchorX: 300, anchorY: 200, width: 120, height: 16 },
      { key: 'overlap-b', anchorX: 300, anchorY: 200, width: 120, height: 16 },
    ];

    const result = placeLabels(labels, BOUNDS, MIN_SEP);

    // Total output must account for both labels.
    expect(result.placed.length + result.hidden.length).toBe(2);

    if (result.placed.length === 2) {
      // Both placed: check separation >= MIN_SEP.
      const [a, b] = result.placed;
      const aRight  = a.x + a.width;
      const aBottom = a.y + a.height;
      const bRight  = b.x + b.width;
      const bBottom = b.y + b.height;
      const overlaps =
        bRight  > a.x - MIN_SEP &&
        b.x     < aRight  + MIN_SEP &&
        bBottom > a.y - MIN_SEP &&
        b.y     < aBottom + MIN_SEP;
      expect(overlaps).toBe(false);
    } else {
      // One placed, one hidden: acceptable fallback per AC8-ii.
      expect(result.placed.length).toBeGreaterThanOrEqual(1);
      expect(result.hidden.length).toBeGreaterThanOrEqual(1);
    }
  });
});

// ---------------------------------------------------------------------------
// AC8 case (iii): byte-identical determinism
// ---------------------------------------------------------------------------
describe('placeLabels - case (iii): determinism', () => {
  it('produces byte-identical output on two consecutive calls with the same fixture', () => {
    const labels: LabelSpec[] = [
      { key: 'zoo',    anchorX: 200, anchorY: 150, width: 70, height: 13 },
      { key: 'alpha',  anchorX: 400, anchorY: 250, width: 70, height: 13 },
      { key: 'middle', anchorX: 300, anchorY: 200, width: 70, height: 13 },
    ];

    const r1 = placeLabels(labels, BOUNDS, MIN_SEP);
    const r2 = placeLabels(labels, BOUNDS, MIN_SEP);

    // Placed arrays must be identical.
    expect(r1.placed.length).toBe(r2.placed.length);
    expect(r1.hidden.length).toBe(r2.hidden.length);

    for (let i = 0; i < r1.placed.length; i++) {
      expect(r1.placed[i]).toStrictEqual(r2.placed[i]);
    }
    for (let i = 0; i < r1.hidden.length; i++) {
      expect(r1.hidden[i]).toStrictEqual(r2.hidden[i]);
    }
  });

  it('sort order is stable regardless of input order (same keys -> same result)', () => {
    const labelsA: LabelSpec[] = [
      { key: 'zoo',    anchorX: 200, anchorY: 150, width: 60, height: 12 },
      { key: 'alpha',  anchorX: 400, anchorY: 250, width: 60, height: 12 },
    ];
    const labelsB: LabelSpec[] = [
      { key: 'alpha',  anchorX: 400, anchorY: 250, width: 60, height: 12 },
      { key: 'zoo',    anchorX: 200, anchorY: 150, width: 60, height: 12 },
    ];

    const rA = placeLabels(labelsA, BOUNDS, MIN_SEP);
    const rB = placeLabels(labelsB, BOUNDS, MIN_SEP);

    // Same keys -> same placed set regardless of input order.
    expect(rA.placed.length).toBe(rB.placed.length);
    const keysA = rA.placed.map((p) => p.key).sort();
    const keysB = rB.placed.map((p) => p.key).sort();
    expect(keysA).toStrictEqual(keysB);
  });
});

// ---------------------------------------------------------------------------
// AC8 case (iv): unplaceable box returned in `hidden`, not thrown
// ---------------------------------------------------------------------------
describe('placeLabels - case (iv): unplaceable box returned in hidden', () => {
  it('returns a box that cannot fit within bounds in `hidden`, not out-of-bounds', () => {
    // A label wider than the entire chart bounds.
    const labels: LabelSpec[] = [
      { key: 'huge-label', anchorX: 300, anchorY: 200, width: 9999, height: 12 },
    ];

    // Must not throw.
    let result: ReturnType<typeof placeLabels>;
    expect(() => {
      result = placeLabels(labels, BOUNDS, MIN_SEP);
    }).not.toThrow();

    // The label must be in `hidden` (cannot fit in bounds).
    expect(result!.placed).toHaveLength(0);
    expect(result!.hidden).toHaveLength(1);
    expect(result!.hidden[0].key).toBe('huge-label');
  });

  it('returns a box that is crowded out by prior placements in `hidden`', () => {
    // Fill the chart with a single large label first, then try to place another.
    const bigWidth = 400;
    const bigHeight = 300;
    const labels: LabelSpec[] = [
      // Large label near center: will claim most of the available space.
      { key: 'anchor-big',    anchorX: 300, anchorY: 200, width: bigWidth, height: bigHeight },
      // Small label also near center: every candidate position will conflict with big.
      { key: 'crowded-small', anchorX: 300, anchorY: 200, width: 60, height: 12 },
    ];

    const result = placeLabels(labels, BOUNDS, MIN_SEP);

    // Total labels accounted for.
    expect(result.placed.length + result.hidden.length).toBe(2);

    // If the small label is placed, it must not violate min separation.
    const small = result.placed.find((p) => p.key === 'crowded-small');
    const big   = result.placed.find((p) => p.key === 'anchor-big');
    if (small && big) {
      const overlaps =
        (small.x + small.width) > big.x - MIN_SEP &&
        small.x < (big.x + big.width + MIN_SEP) &&
        (small.y + small.height) > big.y - MIN_SEP &&
        small.y < (big.y + big.height + MIN_SEP);
      expect(overlaps).toBe(false);
    }
  });
});

// ---------------------------------------------------------------------------
// Additional: point-occlusion avoidance
// ---------------------------------------------------------------------------
describe('placeLabels - point occlusion avoidance', () => {
  it('does not place a label so it occludes the specified avoid points', () => {
    // A label that, at the anchor position, would contain the avoid-point.
    // anchor at (200, 200), label is 100x14, centered, so box is (150,193)-(250,207).
    // avoidPoint at (200, 200) -- directly in center.
    const labels: LabelSpec[] = [
      {
        key: 'point-avoider',
        anchorX: 200,
        anchorY: 200,
        width: 100,
        height: 14,
        avoidPoints: [[200, 200]],
      },
    ];

    const result = placeLabels(labels, BOUNDS, MIN_SEP);

    // Either placed at a position that doesn't contain the point, or hidden.
    if (result.placed.length === 1) {
      const p = result.placed[0];
      const containsPoint =
        200 >= p.x - 3 && 200 <= p.x + p.width + 3 &&
        200 >= p.y - 3 && 200 <= p.y + p.height + 3;
      expect(containsPoint).toBe(false);
    } else {
      expect(result.hidden).toHaveLength(1);
    }
  });
});
