/**
 * ModelMap: model-level MDS scatter plot.
 * Shows model positions in 2D MDS space with confidence ellipses.
 * Responds to model selection; only selected models are shown.
 */

import { useMemo, useState, useCallback, useRef } from 'react';
import { displayModel, displayProvider } from '../lib/familyUtils';
import type { R1State } from '../data/types';
import {
  PIVOT_TO_RECORDS_LABEL,
  pivotToRecordsAriaLabel,
} from '../copy/failures_findings';

interface MDSPlotProps {
  mdsCoordinates: Record<string, [number, number]>;
  mdsUncertainty: Record<string, {
    semi_major: number;
    semi_minor: number;
    rotation_rad: number;
    center: [number, number];
    n_bootstrap: number;
  } | null>;
  models: Array<{ model_id: string; provider: string; family: string; open_weights: boolean }>;
  selectedModelIds: Set<string>;
  topTerms: Record<string, string[]>;
  centralityScores: Record<string, number>;
  /** R1 state per model_id -- drives ellipse suppression and marker shape. See DESIGN_SYSTEM.md §3.3.5. */
  r1States: Record<string, R1State>;
  /** OCI value per model_id -- display-only for R1-b tooltip. MUST NOT be used for classification. See DESIGN_SYSTEM.md §3.3.5 impl req 11 and A5. */
  ociValues: Record<string, number>;
  /**
   * Optional callback to pivot to the Collection records tab for the hovered model.
   * When non-null, the tooltip renders a pivot affordance button (pointer-enhancement-only,
   * per DESIGN_SYSTEM.md §19.19.8 N4 keyboard/SR ruling). See §19.19.3 for placement spec.
   */
  onPivotToRecords?: (modelId: string) => void;
  /** Active domain slug -- used to build aria-label for the pivot affordance. */
  activeDomain?: string;
}

const PROVIDER_COLORS: Record<string, string> = {
  anthropic: 'var(--color-provider-anthropic)',
  openai: 'var(--color-provider-openai)',
  google: 'var(--color-provider-google)',
  meta: 'var(--color-provider-meta)',
  xai: 'var(--color-provider-xai)',
  mistral: 'var(--color-provider-mistral)',
  deepseek: 'var(--color-provider-deepseek)',
  microsoft: 'var(--color-provider-microsoft)',
};


export function MDSPlot({
  mdsCoordinates,
  mdsUncertainty,
  models,
  selectedModelIds,
  topTerms,
  centralityScores,
  r1States,
  ociValues,
  onPivotToRecords,
  activeDomain = '',
}: MDSPlotProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [tooltip, setTooltip] = useState<{ id: string; x: number; y: number } | null>(null);

  const visibleModels = useMemo(() => {
    return models.filter((m) => selectedModelIds.has(m.model_id) && mdsCoordinates[m.model_id]);
  }, [models, selectedModelIds, mdsCoordinates]);

  const { svgContent, width, height } = useMemo(() => {
    const W = 500, pad = { t: 30, r: 30, b: 45, l: 50 };
    const pw = W - pad.l - pad.r;

    if (visibleModels.length === 0) {
      return { svgContent: '', width: W, height: 400 };
    }

    // Compute range including ellipses
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
    const labelLayouts: { x: number; y: number; anchor: string }[] = [];
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
      const name = displayModel(m.model_id);
      const w = name.length * 6.2; // approx char width for 12px font
      const h = 12; // label height

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
      const lx = cx + bestDir.dx;
      const ly = cy + bestDir.dy;
      labelLayouts.push({ x: lx, y: ly, anchor: bestDir.anchor });
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
      svg += `<line x1="${pad.l}" y1="${gy}" x2="${pad.l + pw}" y2="${gy}" stroke="var(--color-svg-grid-line-neutral)" stroke-width="0.5"/>`;
      svg += `<line x1="${gx}" y1="${pad.t}" x2="${gx}" y2="${pad.t + ph}" stroke="var(--color-svg-grid-line-neutral)" stroke-width="0.5"/>`;
    }

    // Ellipses: R1-a only (models with typical_concentration and valid uncertainty).
    // R1-a degenerate sub-state (semi_major <= 0 but u present): bootstrap converged on a near-point.
    // Per DESIGN_SYSTEM.md §3.3.5 impl req 12 and CDA SME T-MDS-R1 F2: this is the LIMIT case of
    // a high-stability R1-a sample, NOT a missing-uncertainty case. Render minimum-radius ellipse floor.
    visibleModels.forEach((m) => {
      const [x, y] = mdsCoordinates[m.model_id];
      const u = mdsUncertainty[m.model_id];
      if (!u) return;
      // Only emit ellipse for R1-a (typical_concentration). R1-b and R1-c suppress the ellipse.
      const r1 = r1States[m.model_id];
      if (r1 === 'low_concentration' || r1 === 'deterministic') return;
      const cx = sx(x), cy = sy(y);
      const isDegenerate = u.semi_major <= 0;
      // Minimum-radius ellipse floor (3px) per §3.3.5 impl req 12: converged-state insurance.
      const rx = isDegenerate ? 3 : (u.semi_major / (xMax - xMin)) * pw;
      const ry = isDegenerate ? 3 : (u.semi_minor / (yMax - yMin)) * ph;
      const deg = -(u.rotation_rad * 180) / Math.PI;
      const color = PROVIDER_COLORS[displayProvider(m)] || 'var(--color-svg-marker-stroke)';
      if (isDegenerate) {
        svg += `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" transform="rotate(${deg},${cx},${cy})" fill="${color}" stroke="${color}" fill-opacity="0.07" stroke-opacity="0.2" stroke-width="1" data-degenerate-bootstrap="true"/>`;
      } else {
        svg += `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" transform="rotate(${deg},${cx},${cy})" fill="${color}" stroke="${color}" fill-opacity="0.07" stroke-opacity="0.2" stroke-width="1"/>`;
      }
    });

    // Points + labels
    visibleModels.forEach((m, idx) => {
      const [x, y] = mdsCoordinates[m.model_id];
      const cx = sx(x), cy = sy(y);
      const color = PROVIDER_COLORS[displayProvider(m)] || 'var(--color-svg-marker-stroke)';
      const name = displayModel(m.model_id);
      const layout = labelLayouts[idx];
      const r1 = r1States[m.model_id];

      if (r1 === 'low_concentration') {
        // R1-b: dashed-stroke circle, no ellipse (DESIGN_SYSTEM.md §3.3.5 impl req 9)
        svg += `<circle cx="${cx}" cy="${cy}" r="6" fill="${color}" fill-opacity="0.6" stroke="${color}" stroke-width="2" stroke-dasharray="4 2" stroke-opacity="1" data-model="${m.model_id}" data-r1-state="low_concentration" aria-label="${name}, low output concentration. Position shown without confidence ellipse." style="cursor:pointer"/>`;
      } else if (r1 === 'deterministic') {
        // R1-c: hollow triangle polygon, apex-up, circumradius 8px (DESIGN_SYSTEM.md §3.3.5 impl req 10)
        const ptTop = `${cx.toFixed(2)},${(cy - 8).toFixed(2)}`;
        const ptBL  = `${(cx - 6.93).toFixed(2)},${(cy + 4).toFixed(2)}`;
        const ptBR  = `${(cx + 6.93).toFixed(2)},${(cy + 4).toFixed(2)}`;
        svg += `<polygon points="${ptTop} ${ptBL} ${ptBR}" fill="none" stroke="${color}" stroke-width="3" stroke-opacity="1" data-model="${m.model_id}" data-r1-state="deterministic" aria-label="${name}, deterministic output. Same categorical structure on every run." style="cursor:pointer"/>`;
      } else {
        // R1-a: standard filled circle with dot stroke (byte-identical to pre-change output for non-degenerate).
        // R1-a degenerate sub-state: same circle but with data-r1-state + data-degenerate-bootstrap + aria-label (S2).
        // The degenerate path is the LIMIT case of high-stability R1-a per DESIGN_SYSTEM.md §3.3.5 impl req 12.
        const uDot = mdsUncertainty[m.model_id];
        const isDegenerateDot = uDot != null && uDot.semi_major <= 0;
        if (isDegenerateDot) {
          svg += `<circle cx="${cx}" cy="${cy}" r="6" fill="${color}" stroke="var(--color-svg-dot-stroke)" stroke-width="1.5" data-model="${m.model_id}" data-r1-state="typical_concentration" data-degenerate-bootstrap="true" aria-label="${name}, high positional stability. Bootstrap resamples converged on a near-point; confidence region is too small to display." style="cursor:pointer"/>`;
        } else {
          svg += `<circle cx="${cx}" cy="${cy}" r="6" fill="${color}" stroke="var(--color-svg-dot-stroke)" stroke-width="1.5" data-model="${m.model_id}" style="cursor:pointer"/>`;
        }
      }
      svg += `<text x="${layout.x.toFixed(1)}" y="${layout.y.toFixed(1)}" text-anchor="${layout.anchor}" font-family="var(--font-body)" font-size="12" fill="var(--color-svg-label-secondary)" style="pointer-events:none">${name}</text>`;
    });

    // Axis labels
    svg += `<text x="${pad.l + pw / 2}" y="${H - 6}" text-anchor="middle" font-family="var(--font-body)" font-size="11" fill="var(--color-svg-axis-caption)">MDS Dimension 1 (relative)</text>`;
    svg += `<text x="12" y="${pad.t + ph / 2}" text-anchor="middle" font-family="var(--font-body)" font-size="11" fill="var(--color-svg-axis-caption)" transform="rotate(-90,12,${pad.t + ph / 2})">Dimension 2</text>`;

    return { svgContent: svg, width: W, height: H };
  }, [visibleModels, mdsCoordinates, mdsUncertainty, r1States]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    const target = e.target as SVGElement;
    const modelId = target.getAttribute('data-model');
    if (modelId) {
      const rect = containerRef.current?.getBoundingClientRect();
      if (rect) {
        setTooltip({ id: modelId, x: e.clientX - rect.left + 12, y: e.clientY - rect.top - 10 });
      }
    }
  }, []);

  const handleMouseLeave = useCallback(() => setTooltip(null), []);

  const tooltipModel = tooltip ? models.find((m) => m.model_id === tooltip.id) : null;
  const tooltipCoords = tooltip ? mdsCoordinates[tooltip.id] : null;
  const tooltipTerms = tooltip ? (topTerms[tooltip.id] || []).slice(0, 5) : [];
  const tooltipCentrality = tooltip ? centralityScores[tooltip.id] : null;

  if (visibleModels.length === 0) {
    return (
      <div className="chart-wrap">
        <div className="viz-placeholder">Select models to see the model map.</div>
      </div>
    );
  }

  return (
    <div className="chart-wrap" ref={containerRef} style={{ position: 'relative' }}>
      <p className="model-map__desc">
        Each dot is one AI model. Models placed close together organize vocabulary
        in similar ways. Ellipses show 95% confidence regions from bootstrap
        resampling. Smaller ellipses mean more stable positions.
        Models without ellipses are flagged with a different marker shape indicating
        low output concentration or deterministic output.
      </p>
      <div className="model-map__svg-container">
        <svg
          width="100%"
          viewBox={`0 0 ${width} ${height}`}
          style={{ display: 'block' }}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          dangerouslySetInnerHTML={{ __html: svgContent }}
        />
      </div>
      {tooltip && tooltipModel && (
        <div className="chart-tooltip" style={{ left: tooltip.x, top: tooltip.y }}>
          <div className="chart-tooltip__name">{displayModel(tooltip.id)}</div>
          <div className="chart-tooltip__sub">{tooltip.id}</div>
          {r1States[tooltip.id] === 'low_concentration' && (
            <div>Position uncertain. This model&apos;s within-model output concentration is low (OCI = {ociValues[tooltip.id] != null ? ociValues[tooltip.id].toFixed(1) : 'n/a'}; higher means runs converge on one structure). See model profile for within-model distribution.</div>
          )}
          {r1States[tooltip.id] === 'deterministic' && (
            <div>Deterministic output. This model produced the same categorical structure on every run. Its position on the map is consistent, but there is no uncertainty range to show. See the methodology page for why this is the least informative case, not the most.</div>
          )}
          {/* R1-a degenerate sub-state: bootstrap converged on a near-point (§3.3.5 impl req 12, CDA SME F2).
              Tooltip body S1 (UI/UX-corrected: "R1-a sample" -> "sample" per §3.3.5 impl req 5). */}
          {r1States[tooltip.id] !== 'low_concentration' && r1States[tooltip.id] !== 'deterministic' &&
           mdsUncertainty[tooltip.id] != null && (mdsUncertainty[tooltip.id] as { semi_major: number }).semi_major <= 0 && (
            <div>Position highly stable. Bootstrap resamples converged on a near-point, so the confidence region is too small to show as an ellipse. This is the limit case of a high-stability sample, not missing uncertainty.</div>
          )}
          {tooltipCentrality != null && (
            <div>Centrality: <span className="chart-tooltip__mono">{tooltipCentrality.toFixed(3)}</span></div>
          )}
          {tooltipCoords && (
            <div>Position: <span className="chart-tooltip__mono">({tooltipCoords[0].toFixed(3)}, {tooltipCoords[1].toFixed(3)})</span></div>
          )}
          {tooltipTerms.length > 0 && (
            <>
              <div className="chart-tooltip__sep" />
              <div className="chart-tooltip__terms">Top terms: {tooltipTerms.join(', ')}</div>
            </>
          )}
          {/* Pivot affordance: pointer-enhancement-only per DESIGN_SYSTEM.md §19.19.3 / §19.19.8.
              Renders only when onPivotToRecords is non-null. DOM placement: after .chart-tooltip__terms,
              preceded by a second .chart-tooltip__sep separator (SME G1 anti-coupling: not adjacent
              to Centrality or OCI explainer lines). pointer-events: auto overrides the parent
              .chart-tooltip { pointer-events: none } CSS rule so clicks register on the button. */}
          {onPivotToRecords != null && (
            <>
              <div className="chart-tooltip__sep" />
              <button
                className="chart-tooltip__pivot-btn"
                style={{ pointerEvents: 'auto' }}
                aria-label={pivotToRecordsAriaLabel(
                  displayModel(tooltip.id),
                  activeDomain,
                )}
                onClick={(e) => {
                  e.stopPropagation();
                  onPivotToRecords(tooltip.id);
                }}
              >
                {PIVOT_TO_RECORDS_LABEL}
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}
