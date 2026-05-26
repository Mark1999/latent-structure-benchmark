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
  anthropic: '#d97706', openai: '#10a37f', google: '#4285f4',
  meta: '#0668e1', xai: '#1d1d1f', mistral: '#f97316',
  deepseek: '#0ea5e9', microsoft: '#00a4ef',
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
    visibleModels.forEach((m) => {
      const [x, y] = mdsCoordinates[m.model_id];
      const cx = sx(x), cy = sy(y);
      const color = PROVIDER_COLORS[displayProvider(m)] || '#888';
      const name = shortName(m.model_id);
      svg += `<circle cx="${cx}" cy="${cy}" r="6" fill="${color}" stroke="#fff" stroke-width="1.5" data-model="${m.model_id}" style="cursor:pointer"/>`;
      svg += `<text x="${cx + 9}" y="${cy + 4}" font-family="var(--font-body)" font-size="12" fill="#4a4a4a" style="pointer-events:none">${name}</text>`;
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
