/**
 * TermMap — hero visualization: convex hulls, cluster labels, colored dots.
 *
 * When cooccurrenceData + selectedModelIds are provided, re-pools the
 * co-occurrence matrices, runs SMACOF, and Procrustes-aligns the result to
 * the reference solution (all-models). Cluster assignments are re-computed
 * with AHC after each MDS update.
 *
 * Falls back to static termCoords/termClusters when cooccurrenceData is null.
 */

import { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import { smacof } from '../lib/smacof';
import { procrustesAlign } from '../lib/procrustes';
import { poolCooccurrence, cooccurrenceToDistances } from '../lib/cooccurrence';
import { ahcCluster } from '../lib/ahcCluster';

/** Shape of the family-cooccurrence.json file */
export interface CooccurrenceData {
  items: string[];
  models: Record<string, number[][]>;
}

// Cluster color palette from tokens.css / DESIGN_SYSTEM.md §1.2
const CLUSTER_COLORS = [
  '#e05c2e', '#2e7d4f', '#b5590a', '#5c3298',
  '#1d6b8f', '#8f1d55', '#4a6e1a', '#6b3a1f',
];

function getClusterColor(idx: number): string {
  return CLUSTER_COLORS[idx % CLUSTER_COLORS.length];
}

// ── Convex hull (Graham scan) ──
function cross(O: [number, number], A: [number, number], B: [number, number]): number {
  return (A[0] - O[0]) * (B[1] - O[1]) - (A[1] - O[1]) * (B[0] - O[0]);
}

function convexHull(pts: [number, number][]): [number, number][] {
  const s = pts.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  if (s.length <= 1) return s;
  const lo: [number, number][] = [];
  for (const p of s) {
    while (lo.length >= 2 && cross(lo[lo.length - 2], lo[lo.length - 1], p) <= 0) lo.pop();
    lo.push(p);
  }
  const up: [number, number][] = [];
  for (const p of [...s].reverse()) {
    while (up.length >= 2 && cross(up[up.length - 2], up[up.length - 1], p) <= 0) up.pop();
    up.push(p);
  }
  return lo.slice(0, -1).concat(up.slice(0, -1));
}

// Pad hull outward from centroid by padPx pixels
function padHull(
  hull: [number, number][],
  cx: number,
  cy: number,
  padPx: number
): [number, number][] {
  return hull.map(([px, py]) => {
    const dx = px - cx;
    const dy = py - cy;
    const d = Math.sqrt(dx * dx + dy * dy) || 1;
    return [px + (dx / d) * padPx, py + (dy / d) * padPx];
  });
}

interface TermEntry {
  term: string;
  x: number;
  y: number;
  cluster: number;
}

interface TooltipState {
  visible: boolean;
  x: number;
  y: number;
  term: string;
  clusterLabel: string;
  clusterColor: string;
  coords: [number, number];
}

interface TermMapProps {
  /** Pre-computed static coordinates — used when cooccurrenceData is not available */
  termCoords: Record<string, [number, number]>;
  /** Pre-computed static cluster assignments — used when cooccurrenceData is not available */
  termClusters: Record<string, number>;
  clusterLabels: string[];
  /** Dynamic co-occurrence data for browser-side MDS recomputation */
  cooccurrenceData?: CooccurrenceData | null;
  /** Set of currently selected model IDs — triggers MDS recompute when changed */
  selectedModelIds?: Set<string>;
}

export function TermMap({
  termCoords,
  termClusters,
  clusterLabels,
  cooccurrenceData,
  selectedModelIds,
}: TermMapProps) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [svgContent, setSvgContent] = useState<string>('');
  const [tooltip, setTooltip] = useState<TooltipState>({
    visible: false, x: 0, y: 0, term: '', clusterLabel: '', clusterColor: '', coords: [0, 0],
  });
  const [, setHoveredCluster] = useState<number | null>(null);

  // ── Dynamic MDS state ─────────────────────────────────────────────────────
  // liveCoords: the current (post-Procrustes) coordinate map used for rendering
  const [liveCoords, setLiveCoords] = useState<Record<string, [number, number]> | null>(null);
  // liveClusters: AHC cluster assignments from the current distance matrix
  const [liveClusters, setLiveClusters] = useState<Record<string, number> | null>(null);
  // previousCoords: the last solved coordinate array (indexed to items order)
  // used as warm-start for the next SMACOF run
  const prevCoordsRef = useRef<[number, number][] | null>(null);
  // referenceCoords: the all-models solution used as Procrustes target
  const refCoordsRef = useRef<[number, number][] | null>(null);
  // referenceClusterCount: cluster count from the static domain JSON
  const refClusterCount = useMemo(() => {
    const vals = Object.values(termClusters);
    if (vals.length === 0) return 8;
    return Math.max(...vals) + 1;
  }, [termClusters]);

  // ── Compute all-models reference solution on first cooccurrence data load ──
  useEffect(() => {
    if (!cooccurrenceData) return;
    const { items, models } = cooccurrenceData;
    const n = items.length;
    if (n === 0) return;

    const allModelIds = new Set(Object.keys(models));
    const pooled = poolCooccurrence(models, allModelIds, n);
    const distances = cooccurrenceToDistances(pooled);
    const { coordinates } = smacof(distances, 2, 200, 1e-6);

    refCoordsRef.current = coordinates;
    prevCoordsRef.current = coordinates.map(([x, y]): [number, number] => [x, y]);
  }, [cooccurrenceData]);

  // ── Recompute MDS when selectedModelIds changes ───────────────────────────
  useEffect(() => {
    if (!cooccurrenceData || !selectedModelIds) return;
    const { items, models } = cooccurrenceData;
    const n = items.length;
    if (n === 0) return;

    // Defer to avoid blocking main thread
    const handle = setTimeout(() => {
      const pooled = poolCooccurrence(models, selectedModelIds, n);
      const distances = cooccurrenceToDistances(pooled);

      // Warm-start from previous solution for smoother visual evolution
      const warmStart = prevCoordsRef.current ?? undefined;
      const { coordinates } = smacof(distances, 2, 200, 1e-6, warmStart);

      // Procrustes-align to the reference (all-models) solution
      const aligned = refCoordsRef.current
        ? procrustesAlign(refCoordsRef.current, coordinates)
        : coordinates;

      // AHC re-clustering with same cluster count as reference
      const clusterAssignments = ahcCluster(distances, refClusterCount);

      // Store as warm-start for next run (use aligned coords to prevent drift)
      prevCoordsRef.current = aligned.map(([x, y]): [number, number] => [x, y]);

      // Build named maps
      const coordMap: Record<string, [number, number]> = {};
      const clusterMap: Record<string, number> = {};
      items.forEach((item, i) => {
        coordMap[item] = aligned[i];
        clusterMap[item] = clusterAssignments[i];
      });

      setLiveCoords(coordMap);
      setLiveClusters(clusterMap);
    }, 0);

    return () => clearTimeout(handle);
  }, [cooccurrenceData, selectedModelIds, refClusterCount]);

  // ── Resolve which coordinates/clusters to render ──────────────────────────
  const effectiveCoords = liveCoords ?? termCoords;
  const effectiveClusters = liveClusters ?? termClusters;

  // Build term entries from effective coords
  const terms: TermEntry[] = useMemo(
    () =>
      Object.entries(effectiveCoords).map(([term, [x, y]]) => ({
        term,
        x,
        y,
        cluster: effectiveClusters[term] ?? 0,
      })),
    [effectiveCoords, effectiveClusters]
  );

  const render = useCallback(() => {
    if (!wrapRef.current) return;
    const rect = wrapRef.current.getBoundingClientRect();
    const W = Math.max(rect.width || 600, 600);
    const H = Math.max(rect.height || 400, 400);

    if (terms.length === 0) return;

    const pad = { t: 30, r: 80, b: 40, l: 50 };
    const pw = W - pad.l - pad.r;
    const ph = H - pad.t - pad.b;

    let xMin = Infinity, xMax = -Infinity, yMin = Infinity, yMax = -Infinity;
    terms.forEach(({ x, y }) => {
      xMin = Math.min(xMin, x); xMax = Math.max(xMax, x);
      yMin = Math.min(yMin, y); yMax = Math.max(yMax, y);
    });

    const xP = (xMax - xMin) * 0.08;
    const yP = (yMax - yMin) * 0.08;
    xMin -= xP; xMax += xP; yMin -= yP; yMax += yP;

    const sx = (v: number) => pad.l + ((v - xMin) / (xMax - xMin)) * pw;
    const sy = (v: number) => pad.t + (1 - (v - yMin) / (yMax - yMin)) * ph;

    // Group by cluster
    const clusters: Record<number, TermEntry[]> = {};
    terms.forEach((t) => {
      if (!clusters[t.cluster]) clusters[t.cluster] = [];
      clusters[t.cluster].push(t);
    });

    const svgParts: string[] = [];
    svgParts.push(`<svg width="${W}" height="${H}" id="term-svg">`);

    // Light grid
    for (let i = 0; i <= 4; i++) {
      const gy = pad.t + (ph * i) / 4;
      const gx = pad.l + (pw * i) / 4;
      svgParts.push(`<line x1="${pad.l}" y1="${gy.toFixed(1)}" x2="${(pad.l + pw).toFixed(1)}" y2="${gy.toFixed(1)}" stroke="#f0f0ec" stroke-width=".5"/>`);
      svgParts.push(`<line x1="${gx.toFixed(1)}" y1="${pad.t}" x2="${gx.toFixed(1)}" y2="${(pad.t + ph).toFixed(1)}" stroke="#f0f0ec" stroke-width=".5"/>`);
    }

    const plotCx = pad.l + pw / 2;
    const plotCy = pad.t + ph / 2;

    // Draw hulls and cluster labels
    Object.entries(clusters).forEach(([cidStr, clusterTerms]) => {
      const cid = parseInt(cidStr, 10);
      const col = getClusterColor(cid);
      const label = clusterLabels[cid] || `Cluster ${cid + 1}`;
      const cx = clusterTerms.reduce((s, t) => s + sx(t.x), 0) / clusterTerms.length;
      const cy = clusterTerms.reduce((s, t) => s + sy(t.y), 0) / clusterTerms.length;

      if (clusterTerms.length >= 2) {
        const pts = clusterTerms.map((t): [number, number] => [sx(t.x), sy(t.y)]);
        const hull = convexHull(pts);
        if (hull.length >= 2) {
          const padded = padHull(hull, cx, cy, 18);
          const pathD = padded
            .map((p, i) => `${i === 0 ? 'M' : 'L'}${p[0].toFixed(1)},${p[1].toFixed(1)}`)
            .join(' ') + 'Z';
          svgParts.push(
            `<path d="${pathD}" fill="${col}" fill-opacity=".07" stroke="${col}" stroke-opacity=".25" stroke-width="1.5" data-cluster="${cid}" cursor="pointer"/>`
          );
        }
      } else if (clusterTerms.length === 1) {
        svgParts.push(
          `<circle cx="${sx(clusterTerms[0].x).toFixed(1)}" cy="${sy(clusterTerms[0].y).toFixed(1)}" r="20" fill="${col}" fill-opacity=".07" stroke="${col}" stroke-opacity=".2" stroke-width="1" data-cluster="${cid}" cursor="pointer"/>`
        );
      }

      // Cluster label — find point farthest from plot center, push further out
      let bestX = cx, bestY = cy;
      if (clusterTerms.length >= 2) {
        let maxDist = 0;
        clusterTerms.forEach((t) => {
          const px = sx(t.x), py = sy(t.y);
          const d = Math.sqrt((px - plotCx) ** 2 + (py - plotCy) ** 2);
          if (d > maxDist) { maxDist = d; bestX = px; bestY = py; }
        });
        const dx = bestX - plotCx, dy = bestY - plotCy;
        const dd = Math.sqrt(dx * dx + dy * dy) || 1;
        bestX += (dx / dd) * 28;
        bestY += (dy / dd) * 14;
      }

      if (clusterTerms.length >= 3) {
        svgParts.push(
          `<text x="${bestX.toFixed(1)}" y="${bestY.toFixed(1)}" text-anchor="middle" dominant-baseline="middle" font-family="var(--font-body)" font-size="13" font-weight="700" fill="${col}" opacity=".75" pointer-events="none">${escapeXml(label)}</text>`
        );
      } else if (clusterTerms.length >= 1) {
        svgParts.push(
          `<text x="${bestX.toFixed(1)}" y="${(bestY + 14).toFixed(1)}" text-anchor="middle" font-family="var(--font-body)" font-size="10" font-weight="600" fill="${col}" opacity=".6" pointer-events="none">${escapeXml(label)}</text>`
        );
      }
    });

    // Term dots — store original coords as data attributes for hover animation
    terms.forEach((t, i) => {
      const px = sx(t.x).toFixed(1);
      const py = sy(t.y).toFixed(1);
      const col = getClusterColor(t.cluster);
      svgParts.push(
        `<circle class="term-dot" cx="${px}" cy="${py}" r="4" fill="${col}" stroke="#fff" stroke-width=".8" data-cluster="${t.cluster}" data-idx="${i}" data-ox="${px}" data-oy="${py}" cursor="pointer"/>`
      );
    });

    // Term labels — hidden by default
    terms.forEach((t, i) => {
      const px = (sx(t.x) + 7).toFixed(1);
      const py = (sy(t.y) + 3).toFixed(1);
      svgParts.push(
        `<text class="term-label" x="${px}" y="${py}" font-family="var(--font-body)" font-size="10" fill="#444" data-cluster="${t.cluster}" data-idx="${i}" data-ox="${px}" data-oy="${py}" pointer-events="none" opacity="0">${escapeXml(t.term)}</text>`
      );
    });

    // Footer annotation
    const nTerms = terms.length;
    const nClusters = Object.keys(clusters).length;
    const modelNote = liveCoords && selectedModelIds
      ? `${selectedModelIds.size} model${selectedModelIds.size !== 1 ? 's' : ''} · `
      : '';
    svgParts.push(
      `<text x="${(pad.l + pw / 2).toFixed(1)}" y="${H - 6}" text-anchor="middle" font-family="var(--font-body)" font-size="10" fill="#a0a098">${modelNote}${nTerms} shared terms · ${nClusters} clusters from pile-sort co-occurrence</text>`
    );

    svgParts.push('</svg>');
    setSvgContent(svgParts.join(''));
  }, [terms, clusterLabels, liveCoords, selectedModelIds]);

  // Re-render on resize or term/coord change
  useEffect(() => {
    render();
    const observer = new ResizeObserver(() => render());
    if (wrapRef.current) observer.observe(wrapRef.current);
    return () => observer.disconnect();
  }, [render]);

  // Cluster hover: explode dots + show labels
  const handleClusterHover = useCallback((cid: number) => {
    setHoveredCluster(cid);
    const svg = document.getElementById('term-svg');
    if (!svg) return;

    // Show labels for hovered cluster only
    svg.querySelectorAll<SVGTextElement>('.term-label').forEach((el) => {
      el.setAttribute('opacity', el.dataset.cluster === String(cid) ? '1' : '0');
    });

    // Explode dots outward from cluster centroid
    const dots = svg.querySelectorAll<SVGCircleElement>(`.term-dot[data-cluster="${cid}"]`);
    if (dots.length < 2) return;

    let cx = 0, cy = 0;
    dots.forEach((d) => { cx += parseFloat(d.dataset.ox || '0'); cy += parseFloat(d.dataset.oy || '0'); });
    cx /= dots.length; cy /= dots.length;

    const strength = 25;
    dots.forEach((d) => {
      const ox = parseFloat(d.dataset.ox || '0');
      const oy = parseFloat(d.dataset.oy || '0');
      const dx = ox - cx, dy = oy - cy;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      d.style.transition = 'cx 0.25s ease-out, cy 0.25s ease-out';
      d.setAttribute('cx', String(ox + (dx / dist) * strength));
      d.setAttribute('cy', String(oy + (dy / dist) * strength));
      d.setAttribute('r', '5');
    });

    // Fade non-hovered dots and hulls
    svg.querySelectorAll<SVGCircleElement>('.term-dot').forEach((d) => {
      if (d.dataset.cluster !== String(cid)) d.style.opacity = '0.15';
    });
    svg.querySelectorAll<SVGPathElement | SVGCircleElement>('[data-cluster]').forEach((el) => {
      if (el.dataset.cluster !== String(cid) && !el.classList.contains('term-dot')) {
        (el as SVGElement).style.opacity = '0.08';
      }
    });
  }, []);

  const handleClusterUnhover = useCallback(() => {
    setHoveredCluster(null);
    const svg = document.getElementById('term-svg');
    if (!svg) return;

    svg.querySelectorAll<SVGTextElement>('.term-label').forEach((el) => el.setAttribute('opacity', '0'));
    svg.querySelectorAll<SVGCircleElement>('.term-dot').forEach((d) => {
      d.style.transition = 'cx 0.2s ease-in, cy 0.2s ease-in, opacity 0.2s';
      d.setAttribute('cx', d.dataset.ox || '0');
      d.setAttribute('cy', d.dataset.oy || '0');
      d.setAttribute('r', '4');
      d.style.opacity = '1';
    });
    svg.querySelectorAll<SVGElement>('[data-cluster]').forEach((el) => {
      el.style.opacity = '1';
    });
  }, []);

  // Mouse event delegation on the SVG wrapper
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const target = e.target as HTMLElement;
    const rect = wrapRef.current?.getBoundingClientRect();
    if (!rect) return;

    if (target.classList.contains('term-dot')) {
      const idx = parseInt(target.dataset.idx || '0', 10);
      const t = terms[idx];
      if (!t) return;
      const label = clusterLabels[t.cluster] || `Cluster ${t.cluster + 1}`;
      const col = getClusterColor(t.cluster);
      setTooltip({
        visible: true,
        x: e.clientX - rect.left + 12,
        y: e.clientY - rect.top - 8,
        term: t.term,
        clusterLabel: label,
        clusterColor: col,
        coords: [t.x, t.y],
      });
    } else if (target.dataset.cluster !== undefined && target.tagName === 'path') {
      const cid = parseInt(target.dataset.cluster || '0', 10);
      handleClusterHover(cid);
    }
  }, [terms, clusterLabels, handleClusterHover]);

  const handleMouseLeave = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const target = e.target as HTMLElement;
    if (target.classList.contains('term-dot')) {
      setTooltip((prev) => ({ ...prev, visible: false }));
    } else if (target.tagName === 'path') {
      handleClusterUnhover();
    }
  }, [handleClusterUnhover]);

  if (terms.length === 0) {
    return (
      <div ref={wrapRef} className="chart-wrap">
        <div className="viz-placeholder">No term data available for this domain.</div>
      </div>
    );
  }

  return (
    <div
      ref={wrapRef}
      className="chart-wrap"
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      role="img"
      aria-label="Term map visualization showing clusters of related terms"
    >
      {/* SVG rendered via innerHTML for performance */}
      <div
        style={{ width: '100%', height: '100%' }}
        dangerouslySetInnerHTML={{ __html: svgContent }}
      />
      {tooltip.visible && (
        <div
          className="chart-tooltip visible"
          style={{ left: tooltip.x, top: tooltip.y }}
          aria-hidden="true"
        >
          <span className="chart-tooltip__title">{tooltip.term}</span>
          <div className="chart-tooltip__sub" style={{ color: tooltip.clusterColor }}>
            {tooltip.clusterLabel}
          </div>
          <div>
            Position:{' '}
            <span className="chart-tooltip__mono">
              ({tooltip.coords[0].toFixed(3)}, {tooltip.coords[1].toFixed(3)})
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

function escapeXml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
