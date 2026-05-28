/**
 * ModelMap — model-level MDS scatter plot.
 * Shows model positions in 2D MDS space with confidence ellipses.
 * Responds to model selection — only selected models are shown.
 */

import { useMemo, useState, useCallback, useRef } from 'react';

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

function displayProvider(model: { provider: string; family: string }): string {
  if (model.provider === 'openrouter') {
    const map: Record<string, string> = { gpt: 'openai', llama: 'meta', mistral: 'mistral', deepseek: 'deepseek', phi: 'microsoft' };
    return map[model.family] || model.provider;
  }
  return model.provider;
}

function shortName(id: string): string {
  return id.split('/').pop() || id;
}

export function MDSPlot({
  mdsCoordinates,
  mdsUncertainty,
  models,
  selectedModelIds,
  topTerms,
  centralityScores,
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
      const name = shortName(m.model_id);
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
      svg += `<line x1="${pad.l}" y1="${gy}" x2="${pad.l + pw}" y2="${gy}" stroke="#eee" stroke-width="0.5"/>`;
      svg += `<line x1="${gx}" y1="${pad.t}" x2="${gx}" y2="${pad.t + ph}" stroke="#eee" stroke-width="0.5"/>`;
    }

    // Ellipses
    visibleModels.forEach((m) => {
      const [x, y] = mdsCoordinates[m.model_id];
      const u = mdsUncertainty[m.model_id];
      if (!u || u.semi_major <= 0) return;
      const cx = sx(x), cy = sy(y);
      const rx = (u.semi_major / (xMax - xMin)) * pw;
      const ry = (u.semi_minor / (yMax - yMin)) * ph;
      const deg = -(u.rotation_rad * 180) / Math.PI;
      const color = PROVIDER_COLORS[displayProvider(m)] || '#888';
      svg += `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" transform="rotate(${deg},${cx},${cy})" fill="${color}" stroke="${color}" fill-opacity="0.07" stroke-opacity="0.2" stroke-width="1"/>`;
    });

    // Points + labels
    visibleModels.forEach((m, idx) => {
      const [x, y] = mdsCoordinates[m.model_id];
      const cx = sx(x), cy = sy(y);
      const color = PROVIDER_COLORS[displayProvider(m)] || '#888';
      const name = shortName(m.model_id);
      const layout = labelLayouts[idx];
      svg += `<circle cx="${cx}" cy="${cy}" r="6" fill="${color}" stroke="#fff" stroke-width="1.5" data-model="${m.model_id}" style="cursor:pointer"/>`;
      svg += `<text x="${layout.x.toFixed(1)}" y="${layout.y.toFixed(1)}" text-anchor="${layout.anchor}" font-family="var(--font-body)" font-size="12" fill="#4a4a4a" style="pointer-events:none">${name}</text>`;
    });

    // Axis labels
    svg += `<text x="${pad.l + pw / 2}" y="${H - 6}" text-anchor="middle" font-family="var(--font-body)" font-size="11" fill="#a0a098">MDS Dimension 1 — relative</text>`;
    svg += `<text x="12" y="${pad.t + ph / 2}" text-anchor="middle" font-family="var(--font-body)" font-size="11" fill="#a0a098" transform="rotate(-90,12,${pad.t + ph / 2})">Dimension 2</text>`;

    return { svgContent: svg, width: W, height: H };
  }, [visibleModels, mdsCoordinates, mdsUncertainty]);

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
        resampling — smaller ellipses mean more stable positions.
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
          <div className="chart-tooltip__name">{shortName(tooltip.id)}</div>
          <div className="chart-tooltip__sub">{tooltip.id}</div>
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
        </div>
      )}
    </div>
  );
}
