/**
 * Focus2FamilySimilarity — mini heatmap + MDS with family ring highlight.
 *
 * DESIGN_SYSTEM.md §14.4 (mini heatmap), §14.5 (MDS ring highlight)
 * CDA SME note 4: ring is a visual aid, not a cluster boundary.
 * No convex hull. Legend note per §14.5.
 * Forbidden: "cluster of [provider] models".
 */

import { useMemo } from 'react';
import { SimilarityHeatmap } from './SimilarityHeatmap';
import type { PublishedModel, EllipseParams } from '../data/types';
import {
  groupModelsByProvider,
  PROVIDER_DISPLAY_COLORS,
  displayProvider,
} from '../lib/familyUtils';
import {
  FOCUS2_SIMILARITY_DESCRIPTION,
  FOCUS2_NO_PROVIDER_SELECTED,
} from '../copy/focus2';

interface Focus2FamilySimilarityProps {
  models: PublishedModel[];
  similarityMatrix: number[][];
  mdsCoordinates: Record<string, [number, number]>;
  mdsUncertainty: Record<string, EllipseParams | null>;
  selectedProvider: string | null;
}

function shortName(id: string): string {
  return id.split('/').pop() || id;
}

// Build inline SVG for MDS with family highlight (§14.5)
function buildMdsSvg(
  models: PublishedModel[],
  mdsCoordinates: Record<string, [number, number]>,
  mdsUncertainty: Record<string, EllipseParams | null>,
  familyIds: Set<string>,
): { svgContent: string; width: number; height: number } {
  const W = 500;
  const pad = { t: 30, r: 30, b: 45, l: 50 };
  const pw = W - pad.l - pad.r;

  const visibleModels = models.filter((m) => mdsCoordinates[m.model_id]);

  if (visibleModels.length === 0) {
    return { svgContent: '', width: W, height: 400 };
  }

  let xMin = Infinity, xMax = -Infinity, yMin = Infinity, yMax = -Infinity;
  visibleModels.forEach((m) => {
    const [x, y] = mdsCoordinates[m.model_id];
    const u = mdsUncertainty[m.model_id];
    const smaj = u?.semi_major || 0;
    const smin = u?.semi_minor || 0;
    xMin = Math.min(xMin, x - smaj); xMax = Math.max(xMax, x + smaj);
    yMin = Math.min(yMin, y - smin); yMax = Math.max(yMax, y + smin);
  });

  const xPad = (xMax - xMin) * 0.1 || 0.1;
  const yPad = (yMax - yMin) * 0.1 || 0.1;
  xMin -= xPad; xMax += xPad; yMin -= yPad; yMax += yPad;

  const aspect = (yMax - yMin) / (xMax - xMin) || 1;
  const ph = pw * aspect;
  const H = ph + pad.t + pad.b;

  const sx = (v: number) => pad.l + ((v - xMin) / (xMax - xMin)) * pw;
  const sy = (v: number) => pad.t + (1 - (v - yMin) / (yMax - yMin)) * ph;

    // Greedy compass label offset algorithm to prevent overlaps
    const labelLayouts: { model_id: string; x: number; y: number; anchor: string }[] = [];
    const placedBoxes: { x1: number; x2: number; y1: number; y2: number }[] = [];

    const DIRECTIONS: {
      anchor: string;
      dx: number;
      dy: number;
      bx: (cx: number, w: number) => number;
      by: (cy: number, h: number) => number;
    }[] = [
      { anchor: 'start',  dx: 9,   dy: 4,   bx: (cx) => cx + 9,          by: (cy) => cy - 6 },      // E
      { anchor: 'start',  dx: 7,   dy: 10,  bx: (cx) => cx + 7,          by: (cy) => cy },          // SE
      { anchor: 'middle', dx: 0,   dy: 14,  bx: (cx, w) => cx - w / 2,   by: (cy) => cy + 4 },      // S
      { anchor: 'end',    dx: -7,  dy: 10,  bx: (cx, w) => cx - 7 - w,   by: (cy) => cy },          // SW
      { anchor: 'end',    dx: -9,  dy: 4,   bx: (cx, w) => cx - 9 - w,   by: (cy) => cy - 6 },      // W
      { anchor: 'end',    dx: -7,  dy: -2,  bx: (cx, w) => cx - 7 - w,   by: (cy) => cy - 12 },     // NW
      { anchor: 'middle', dx: 0,   dy: -8,  bx: (cx, w) => cx - w / 2,   by: (cy) => cy - 18 },     // N
      { anchor: 'start',  dx: 7,   dy: -2,  bx: (cx) => cx + 7,          by: (cy) => cy - 12 },     // NE
    ];

    visibleModels.forEach((m) => {
      const [x, y] = mdsCoordinates[m.model_id];
      const cx = sx(x);
      const cy = sy(y);
      const name = shortName(m.model_id);
      const isFamily = familyIds.has(m.model_id);
      const fontSize = isFamily ? 12 : 11;
      const w = name.length * (fontSize * 0.52); // approx char width
      const h = fontSize; // label height

      let bestDirIdx = 0;
      let minPenalty = Infinity;

      for (let k = 0; k < 8; k++) {
        const dir = DIRECTIONS[k];
        const bx1 = dir.bx(cx, w);
        const bx2 = bx1 + w;
        const by1 = dir.by(cy, h);
        const by2 = by1 + h;

        let penalty = 0;

        // Penalty 1: overlap with already placed label boxes
        for (let j = 0; j < placedBoxes.length; j++) {
          const pb = placedBoxes[j];
          const xOverlap = Math.max(0, Math.min(bx2, pb.x2) - Math.max(bx1, pb.x1));
          const yOverlap = Math.max(0, Math.min(by2, pb.y2) - Math.max(by1, pb.y1));
          if (xOverlap > 0 && yOverlap > 0) {
            penalty += xOverlap * yOverlap * 8;
          }
        }

        // Penalty 2: overlap with other dots
        visibleModels.forEach((otherM) => {
          if (otherM.model_id === m.model_id) return;
          const [ox, oy] = mdsCoordinates[otherM.model_id];
          const ocx = sx(ox);
          const ocy = sy(oy);
          if (ocx >= bx1 - 5 && ocx <= bx2 + 5 && ocy >= by1 - 5 && ocy <= by2 + 5) {
            penalty += 200;
          }
        });

        // Penalty 3: out of bounds
        if (bx1 < pad.l || bx2 > W - pad.r || by1 < pad.t || by2 > H - pad.b) {
          penalty += 300;
        }

        // Slight preference for East (original standard)
        penalty += k * 0.5;

        if (penalty < minPenalty) {
          minPenalty = penalty;
          bestDirIdx = k;
        }
      }

      const bestDir = DIRECTIONS[bestDirIdx];
      let lx = cx + bestDir.dx;
      const ly = cy + bestDir.dy;
      // Ring highlight overhang compensation
      if (isFamily) {
        if (bestDir.dx > 0) lx += 2;
        if (bestDir.dx < 0) lx -= 2;
      }
      labelLayouts.push({ model_id: m.model_id, x: lx, y: ly, anchor: bestDir.anchor });
      placedBoxes.push({
        x1: bestDir.bx(cx, w),
        x2: bestDir.bx(cx, w) + w,
        y1: bestDir.by(cy, h),
        y2: bestDir.by(cy, h) + h,
      });
    });

    let svg = '';

    // Grid
    for (let i = 0; i <= 4; i++) {
      const gy = pad.t + (ph * i) / 4;
      const gx = pad.l + (pw * i) / 4;
      svg += `<line x1="${pad.l}" y1="${gy}" x2="${pad.l + pw}" y2="${gy}" stroke="#eee" stroke-width="0.5"/>`;
      svg += `<line x1="${gx}" y1="${pad.t}" x2="${gx}" y2="${pad.t + ph}" stroke="#eee" stroke-width="0.5"/>`;
    }

    // Ellipses (only for family members shown at full opacity)
    visibleModels.forEach((m) => {
      if (!familyIds.has(m.model_id)) return;
      const [x, y] = mdsCoordinates[m.model_id];
      const u = mdsUncertainty[m.model_id];
      if (!u || u.semi_major <= 0) return;
      const cx = sx(x), cy = sy(y);
      const rx = (u.semi_major / (xMax - xMin)) * pw;
      const ry = (u.semi_minor / (yMax - yMin)) * ph;
      const deg = -(u.rotation_rad * 180) / Math.PI;
      const color = PROVIDER_DISPLAY_COLORS[displayProvider(m)] || '#888';
      svg += `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" transform="rotate(${deg},${cx},${cy})" fill="${color}" stroke="${color}" fill-opacity="0.07" stroke-opacity="0.2" stroke-width="1"/>`;
    });

    // Non-family points (dimmed to opacity 0.45, §14.5)
    visibleModels.filter((m) => !familyIds.has(m.model_id)).forEach((m) => {
      const [x, y] = mdsCoordinates[m.model_id];
      const cx = sx(x), cy = sy(y);
      const color = PROVIDER_DISPLAY_COLORS[displayProvider(m)] || '#888';
      const name = shortName(m.model_id);
      const layout = labelLayouts.find((l) => l.model_id === m.model_id)!;
      svg += `<g opacity="0.45">`;
      svg += `<circle cx="${cx}" cy="${cy}" r="6" fill="${color}" stroke="#fff" stroke-width="1.5"/>`;
      svg += `<text x="${layout.x.toFixed(1)}" y="${layout.y.toFixed(1)}" text-anchor="${layout.anchor}" font-family="var(--font-body)" font-size="11" fill="#4a4a4a" style="pointer-events:none">${name}</text>`;
      svg += `</g>`;
    });

    // Family member points — filled circle + outer ring (§14.5: r=9, fill:none, stroke at 35% opacity)
    visibleModels.filter((m) => familyIds.has(m.model_id)).forEach((m) => {
      const [x, y] = mdsCoordinates[m.model_id];
      const cx = sx(x), cy = sy(y);
      const color = PROVIDER_DISPLAY_COLORS[displayProvider(m)] || '#888';
      const name = shortName(m.model_id);
      const layout = labelLayouts.find((l) => l.model_id === m.model_id)!;
      // Inner filled circle
      svg += `<circle cx="${cx}" cy="${cy}" r="6" fill="${color}" stroke="#fff" stroke-width="1.5"/>`;
      // Outer ring — §14.5: r=9, fill:none, stroke: 2px var(--color-text-primary) at 35% opacity
      svg += `<circle cx="${cx}" cy="${cy}" r="9" fill="none" stroke="rgba(44,62,80,0.35)" stroke-width="2"/>`;
      // Label
      svg += `<text x="${layout.x.toFixed(1)}" y="${layout.y.toFixed(1)}" text-anchor="${layout.anchor}" font-family="var(--font-body)" font-size="12" fill="#2c3e50" font-weight="500" style="pointer-events:none">${name}</text>`;
    });

    // Axis labels
    svg += `<text x="${pad.l + pw / 2}" y="${H - 6}" text-anchor="middle" font-family="var(--font-body)" font-size="11" fill="#a0a098">MDS Dimension 1 — relative</text>`;
    svg += `<text x="12" y="${pad.t + ph / 2}" text-anchor="middle" font-family="var(--font-body)" font-size="11" fill="#a0a098" transform="rotate(-90,12,${pad.t + ph / 2})">Dimension 2</text>`;

    return { svgContent: svg, width: W, height: H };
  }

export function Focus2FamilySimilarity({
  models,
  similarityMatrix,
  mdsCoordinates,
  mdsUncertainty,
  selectedProvider,
}: Focus2FamilySimilarityProps) {
  const grouping = useMemo(() => groupModelsByProvider(models), [models]);

  const familyModels = useMemo(() => {
    if (!selectedProvider) return [];
    return grouping[selectedProvider] || [];
  }, [grouping, selectedProvider]);

  const familyIds = useMemo(
    () => new Set(familyModels.map((m) => m.model_id)),
    [familyModels],
  );

  const { svgContent, width, height } = useMemo(() => {
    if (models.length === 0) return { svgContent: '', width: 500, height: 400 };
    return buildMdsSvg(models, mdsCoordinates, mdsUncertainty, familyIds);
  }, [models, mdsCoordinates, mdsUncertainty, familyIds]);

  if (!selectedProvider) {
    return (
      <div className="f2-similarity">
        <p className="f2-similarity__desc">{FOCUS2_SIMILARITY_DESCRIPTION}</p>
        <p className="f2-similarity__no-selection">{FOCUS2_NO_PROVIDER_SELECTED}</p>
      </div>
    );
  }

  return (
    <div className="f2-similarity">
      <p className="f2-similarity__desc">{FOCUS2_SIMILARITY_DESCRIPTION}</p>

      {/* Mini heatmap — reuse SimilarityHeatmap scoped to family models (§14.4) */}
      <div className="f2-similarity__section">
        <h3 className="f2-similarity__section-heading">
          Within-family similarity —{' '}
          {selectedProvider.charAt(0).toUpperCase() + selectedProvider.slice(1)}{' '}
          ({familyModels.length} models)
        </h3>
        <div className="f2-similarity__heatmap-wrap">
          <SimilarityHeatmap
            similarityMatrix={similarityMatrix}
            models={models}
            selectedModelIds={familyIds}
          />
        </div>
      </div>

      {/* MDS with family highlight (§14.5) */}
      <div className="f2-similarity__section">
        <h3 className="f2-similarity__section-heading">
          {selectedProvider.charAt(0).toUpperCase() + selectedProvider.slice(1)} models in the full model map
        </h3>
        <div className="f2-similarity__mds-wrap f2-mds-plot">
          {svgContent ? (
            <>
              <svg
                width="100%"
                viewBox={`0 0 ${width} ${height}`}
                role="img"
                aria-label={`Model map with ${selectedProvider} models highlighted`}
                dangerouslySetInnerHTML={{ __html: svgContent }}
              />
              {/* Legend note §14.5 — no convex hull */}
              <p className="f2-similarity__legend-note">
                Ring indicates selected provider family. Non-family models dimmed.
              </p>
            </>
          ) : (
            <p className="f2-similarity__no-selection">Model map data not available.</p>
          )}
        </div>
      </div>
    </div>
  );
}
