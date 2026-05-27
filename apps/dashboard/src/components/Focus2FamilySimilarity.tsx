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
    svg += `<g opacity="0.45">`;
    svg += `<circle cx="${cx}" cy="${cy}" r="6" fill="${color}" stroke="#fff" stroke-width="1.5"/>`;
    svg += `<text x="${cx + 9}" y="${cy + 4}" font-family="var(--font-body)" font-size="11" fill="#4a4a4a" style="pointer-events:none">${name}</text>`;
    svg += `</g>`;
  });

  // Family member points — filled circle + outer ring (§14.5: r=9, fill:none, stroke at 35% opacity)
  visibleModels.filter((m) => familyIds.has(m.model_id)).forEach((m) => {
    const [x, y] = mdsCoordinates[m.model_id];
    const cx = sx(x), cy = sy(y);
    const color = PROVIDER_DISPLAY_COLORS[displayProvider(m)] || '#888';
    const name = shortName(m.model_id);
    // Inner filled circle
    svg += `<circle cx="${cx}" cy="${cy}" r="6" fill="${color}" stroke="#fff" stroke-width="1.5"/>`;
    // Outer ring — §14.5: r=9, fill:none, stroke: 2px var(--color-text-primary) at 35% opacity
    svg += `<circle cx="${cx}" cy="${cy}" r="9" fill="none" stroke="rgba(44,62,80,0.35)" stroke-width="2"/>`;
    // Label
    svg += `<text x="${cx + 11}" y="${cy + 4}" font-family="var(--font-body)" font-size="12" fill="#2c3e50" font-weight="500" style="pointer-events:none">${name}</text>`;
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
