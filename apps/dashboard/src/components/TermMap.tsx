/**
 * TermMap — hero visualization: convex hulls, cluster labels, colored dots.
 *
 * When cooccurrenceData + selectedModelIds are provided, re-pools the
 * co-occurrence matrices, runs SMACOF, and Procrustes-aligns the result to
 * the reference solution (all-models). Cluster assignments are re-computed
 * with AHC after each MDS update.
 *
 * Falls back to static termCoords/termClusters when cooccurrenceData is null.
 *
 * Magnifying lens: when lensEnabled=true, a circular lens follows the mouse.
 * Terms inside the lens radius are displaced outward using a quadratic falloff
 * repulsion so overlapping labels spread apart and become readable.
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

interface TermEntry {
  term: string;
  x: number;
  y: number;
  cluster: number;
}


// Lens constants — SVG-coordinate units (roughly 1 unit ≈ 1 CSS pixel at typical viewport)
const LENS_RADIUS = 80;
const MAX_DISPLACEMENT = 35;

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
  /** When true, a cursor-following magnifying lens spreads overlapping terms apart */
  lensEnabled?: boolean;
}

export function TermMap({
  termCoords,
  termClusters,
  clusterLabels,
  cooccurrenceData,
  selectedModelIds,
  lensEnabled = false,
}: TermMapProps) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [svgContent, setSvgContent] = useState<string>('');

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

    // Draw cluster labels (no hulls — they produce ugly slivers for small clusters)
    Object.entries(clusters).forEach(([cidStr, clusterTerms]) => {
      const cid = parseInt(cidStr, 10);
      const col = getClusterColor(cid);
      const label = clusterLabels[cid] || `Cluster ${cid + 1}`;
      const cx = clusterTerms.reduce((s, t) => s + sx(t.x), 0) / clusterTerms.length;
      const cy = clusterTerms.reduce((s, t) => s + sy(t.y), 0) / clusterTerms.length;

      // Position label at the cluster's farthest point from plot center, pushed outward
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

    // Term labels — visible, small, positioned right of each dot
    // data-ox / data-oy store the label's original position for lens displacement
    terms.forEach((t) => {
      const px = (sx(t.x) + 6).toFixed(1);
      const py = (sy(t.y) + 3).toFixed(1);
      const col = getClusterColor(t.cluster);
      svgParts.push(
        `<text class="term-label" x="${px}" y="${py}" data-ox="${px}" data-oy="${py}" font-family="var(--font-body)" font-size="9" fill="${col}" opacity=".7" pointer-events="none">${escapeXml(t.term)}</text>`
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

  // ── Magnifying lens interaction ───────────────────────────────────────────
  // rafRef: pending requestAnimationFrame id (used to cancel on cleanup)
  const rafRef = useRef<number | null>(null);
  // lensRingRef: the <circle> element appended to the SVG as a lens outline
  const lensRingRef = useRef<SVGCircleElement | null>(null);

  useEffect(() => {
    const wrap = wrapRef.current;
    if (!wrap) return;

    // Create / remove lens ring element whenever lensEnabled changes
    if (!lensEnabled) {
      // Reset all displaced elements back to their original positions
      const svg = wrap.querySelector<SVGSVGElement>('#term-svg');
      if (svg) {
        svg.querySelectorAll<SVGCircleElement>('.term-dot').forEach((dot) => {
          dot.setAttribute('cx', dot.getAttribute('data-ox') ?? '0');
          dot.setAttribute('cy', dot.getAttribute('data-oy') ?? '0');
        });
        svg.querySelectorAll<SVGTextElement>('.term-label').forEach((lbl) => {
          lbl.setAttribute('x', lbl.getAttribute('data-ox') ?? '0');
          lbl.setAttribute('y', lbl.getAttribute('data-oy') ?? '0');
        });
        if (lensRingRef.current) {
          lensRingRef.current.remove();
          lensRingRef.current = null;
        }
      }
      return;
    }

    function applyLens(svgEl: SVGSVGElement, mouseX: number, mouseY: number) {
      // Ensure lens ring exists
      if (!lensRingRef.current) {
        const ring = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        ring.setAttribute('class', 'lens-ring');
        ring.setAttribute('r', String(LENS_RADIUS));
        ring.setAttribute('fill', 'none');
        ring.setAttribute('stroke', 'rgba(0,0,0,0.15)');
        ring.setAttribute('stroke-width', '1');
        ring.setAttribute('stroke-dasharray', '4 2');
        ring.setAttribute('pointer-events', 'none');
        svgEl.appendChild(ring);
        lensRingRef.current = ring;
      }

      // Move the lens ring to follow the mouse
      lensRingRef.current.setAttribute('cx', String(mouseX));
      lensRingRef.current.setAttribute('cy', String(mouseY));

      // Displace dots
      svgEl.querySelectorAll<SVGCircleElement>('.term-dot').forEach((dot) => {
        const ox = parseFloat(dot.getAttribute('data-ox') ?? '0');
        const oy = parseFloat(dot.getAttribute('data-oy') ?? '0');
        const dx = ox - mouseX;
        const dy = oy - mouseY;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < LENS_RADIUS && dist > 0) {
          const strength = Math.pow(1 - dist / LENS_RADIUS, 2) * MAX_DISPLACEMENT;
          const angle = Math.atan2(dy, dx);
          dot.setAttribute('cx', String(ox + Math.cos(angle) * strength));
          dot.setAttribute('cy', String(oy + Math.sin(angle) * strength));
        } else {
          dot.setAttribute('cx', String(ox));
          dot.setAttribute('cy', String(oy));
        }
      });

      // Displace labels
      svgEl.querySelectorAll<SVGTextElement>('.term-label').forEach((lbl) => {
        const ox = parseFloat(lbl.getAttribute('data-ox') ?? '0');
        const oy = parseFloat(lbl.getAttribute('data-oy') ?? '0');
        const dx = ox - mouseX;
        const dy = oy - mouseY;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < LENS_RADIUS && dist > 0) {
          const strength = Math.pow(1 - dist / LENS_RADIUS, 2) * MAX_DISPLACEMENT;
          const angle = Math.atan2(dy, dx);
          lbl.setAttribute('x', String(ox + Math.cos(angle) * strength));
          lbl.setAttribute('y', String(oy + Math.sin(angle) * strength));
        } else {
          lbl.setAttribute('x', String(ox));
          lbl.setAttribute('y', String(oy));
        }
      });
    }

    function resetLens(svgEl: SVGSVGElement) {
      svgEl.querySelectorAll<SVGCircleElement>('.term-dot').forEach((dot) => {
        dot.setAttribute('cx', dot.getAttribute('data-ox') ?? '0');
        dot.setAttribute('cy', dot.getAttribute('data-oy') ?? '0');
      });
      svgEl.querySelectorAll<SVGTextElement>('.term-label').forEach((lbl) => {
        lbl.setAttribute('x', lbl.getAttribute('data-ox') ?? '0');
        lbl.setAttribute('y', lbl.getAttribute('data-oy') ?? '0');
      });
      if (lensRingRef.current) {
        lensRingRef.current.remove();
        lensRingRef.current = null;
      }
    }

    // `wrap` is const and was narrowed to HTMLDivElement by the guard above;
    // the non-null assertion below is safe since wrap cannot be reassigned.
    const safeWrap: HTMLDivElement = wrap;

    function handleMouseMove(e: MouseEvent) {
      if (rafRef.current !== null) return; // skip if frame already queued
      rafRef.current = requestAnimationFrame(() => {
        rafRef.current = null;
        const svg = safeWrap.querySelector<SVGSVGElement>('#term-svg');
        if (!svg) return;
        const rect = svg.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        applyLens(svg, mouseX, mouseY);
      });
    }

    function handleMouseLeave() {
      if (rafRef.current !== null) {
        cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }
      const svg = safeWrap.querySelector<SVGSVGElement>('#term-svg');
      if (svg) resetLens(svg);
    }

    safeWrap.addEventListener('mousemove', handleMouseMove);
    safeWrap.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      safeWrap.removeEventListener('mousemove', handleMouseMove);
      safeWrap.removeEventListener('mouseleave', handleMouseLeave);
      if (rafRef.current !== null) {
        cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }
      // Clean up the ring if component unmounts while lens active
      if (lensRingRef.current) {
        lensRingRef.current.remove();
        lensRingRef.current = null;
      }
    };
  }, [lensEnabled, svgContent]); // re-attach when SVG re-renders (new data-ox/oy in DOM)


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
      role="img"
      aria-label="Term map visualization showing clusters of related terms"
    >
      <div
        style={{ width: '100%', height: '100%' }}
        dangerouslySetInnerHTML={{ __html: svgContent }}
      />
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
