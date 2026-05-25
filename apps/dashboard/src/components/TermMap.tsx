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
 * Per-model pile label selector: a dropdown above the SVG lets the user
 * choose which model's pile groupings are used to label the clusters. Dot
 * colors still come from the computed AHC clusters. When "None" is selected
 * no cluster labels are rendered.
 *
 * Stress display: Kruskal's stress-1 from the SMACOF solver is shown below
 * the SVG when live MDS is active. For static coordinates, a placeholder
 * note is shown instead.
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

/** Per-model pile structure as stored in centroid_piles in the domain JSON */
export interface ModelPileData {
  piles: string[][];
  labels: string[];
}

// Cluster color palette from tokens.css / DESIGN_SYSTEM.md §1.2
const CLUSTER_COLORS = [
  '#e05c2e', '#2e7d4f', '#b5590a', '#5c3298',
  '#1d6b8f', '#8f1d55', '#4a6e1a', '#6b3a1f',
];

function getClusterColor(idx: number): string {
  return CLUSTER_COLORS[idx % CLUSTER_COLORS.length];
}

/**
 * Convert a raw model_id to a short human-readable display name for the
 * dropdown. Examples:
 *   "claude-opus-4-6"              → "Claude Opus 4.6"
 *   "openai/gpt-5.4"               → "GPT-5.4"
 *   "google/gemini-2.5-pro"        → "Gemini 2.5 Pro"
 *   "meta-llama/llama-4-maverick"  → "Llama 4 Maverick"
 *   "mistralai/mistral-large-2512" → "Mistral Large 2512"
 *   "x-ai/grok-4"                  → "Grok 4"
 *   "deepseek/deepseek-v3.2"       → "DeepSeek V3.2"
 *   "microsoft/phi-4"              → "Phi 4"
 */
function shortModelDisplayName(modelId: string): string {
  // Strip provider prefix (everything up to and including the last '/')
  const base = modelId.includes('/') ? modelId.split('/').pop()! : modelId;

  // Known prefix → brand capitalisations
  const prefixMap: [string, string][] = [
    ['claude-',     'Claude '],
    ['gpt-',        'GPT-'],
    ['gemini-',     'Gemini '],
    ['llama-',      'Llama '],
    ['mistral-',    'Mistral '],
    ['grok-',       'Grok '],
    ['deepseek-',   'DeepSeek '],
    ['phi-',        'Phi '],
  ];

  for (const [prefix, brand] of prefixMap) {
    if (base.startsWith(prefix)) {
      const rest = base.slice(prefix.length);
      // Capitalise each hyphen-separated word in the remainder
      const formatted = rest
        .split('-')
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
        .join(' ');
      // For GPT keep the dash: "GPT-5.4" not "GPT 5.4"
      if (brand === 'GPT-') return `${brand}${formatted}`;
      return `${brand}${formatted}`;
    }
  }

  // Fallback: title-case the base name, replacing hyphens with spaces
  return base.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

interface TermEntry {
  term: string;
  x: number;
  y: number;
  cluster: number;
}


// Lens constants — SVG-coordinate units (roughly 1 unit ≈ 1 CSS pixel at typical viewport)
const LENS_RADIUS = 110;
const MAX_DISPLACEMENT = 65;
const LENS_FONT_SIZE = 13; // larger text inside the lens for readability

interface TermMapProps {
  /** Pre-computed static coordinates — used when cooccurrenceData is not available */
  termCoords: Record<string, [number, number]>;
  /** Pre-computed static cluster assignments — used when cooccurrenceData is not available */
  termClusters: Record<string, number>;
  clusterLabels: string[];
  /** Per-model pile data from centroid_piles in the domain JSON */
  centroidPiles?: Record<string, ModelPileData>;
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
  centroidPiles,
  cooccurrenceData,
  selectedModelIds,
  lensEnabled = false,
}: TermMapProps) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [svgContent, setSvgContent] = useState<string>('');

  // ── Per-model pile label selector state ──────────────────────────────────
  // Sorted list of model keys available for pile label selection
  const pileModelKeys = useMemo(
    () => (centroidPiles ? Object.keys(centroidPiles).sort() : []),
    [centroidPiles]
  );
  // userLabelChoice tracks the user's explicit selection; null means "None".
  // We use an explicit sentinel '__default__' to mean "user hasn't picked yet;
  // fall back to the first model key from centroidPiles."
  const [userLabelChoice, setUserLabelChoice] = useState<string | null | '__default__'>('__default__');

  // Derive the effective label model: when the user hasn't explicitly chosen,
  // or when the previously chosen model is no longer present (domain switch),
  // fall back to the first available key.
  const selectedLabelModel: string | null = useMemo(() => {
    if (userLabelChoice === '__default__') {
      return pileModelKeys[0] ?? null;
    }
    // If user chose null (None), honour that
    if (userLabelChoice === null) return null;
    // If user chose a specific model that still exists, use it;
    // otherwise fall back to the first key (handles domain switches)
    if (centroidPiles && userLabelChoice in centroidPiles) return userLabelChoice;
    return pileModelKeys[0] ?? null;
  }, [userLabelChoice, pileModelKeys, centroidPiles]);

  // ── SMACOF stress display state ───────────────────────────────────────────
  const [liveStress, setLiveStress] = useState<number | null>(null);

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
      const { coordinates, stress } = smacof(distances, 2, 200, 1e-6, warmStart);

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
      setLiveStress(stress);
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

    // Group by AHC cluster (for dot color — always computed)
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

    // ── Cluster label rendering ────────────────────────────────────────────
    // If a model is selected in the dropdown, use that model's pile labels.
    // Otherwise (selectedLabelModel === null), no labels are rendered.
    if (selectedLabelModel && centroidPiles && centroidPiles[selectedLabelModel]) {
      const modelPiles = centroidPiles[selectedLabelModel];

      // Build term → pile label map for the selected model
      const termToPileLabel: Record<string, string> = {};
      modelPiles.piles.forEach((pile, i) => {
        const label = modelPiles.labels[i] || `Pile ${i + 1}`;
        pile.forEach((term) => { termToPileLabel[term] = label; });
      });

      // Group terms (from current coords) by their pile label
      const labelGroups: Record<string, TermEntry[]> = {};
      terms.forEach((t) => {
        const label = termToPileLabel[t.term];
        if (label) {
          if (!labelGroups[label]) labelGroups[label] = [];
          labelGroups[label].push(t);
        }
      });

      // For each group, compute centroid in SVG space and render label
      Object.entries(labelGroups).forEach(([label, groupTerms]) => {
        if (groupTerms.length < 1) return;

        const cx = groupTerms.reduce((s, t) => s + sx(t.x), 0) / groupTerms.length;
        const cy = groupTerms.reduce((s, t) => s + sy(t.y), 0) / groupTerms.length;

        // Position label at the term farthest from plot center, pushed outward
        let bestX = cx, bestY = cy;
        if (groupTerms.length >= 2) {
          let maxDist = 0;
          groupTerms.forEach((t) => {
            const px = sx(t.x), py = sy(t.y);
            const d = Math.sqrt((px - plotCx) ** 2 + (py - plotCy) ** 2);
            if (d > maxDist) { maxDist = d; bestX = px; bestY = py; }
          });
          const dx = bestX - plotCx, dy = bestY - plotCy;
          const dd = Math.sqrt(dx * dx + dy * dy) || 1;
          bestX += (dx / dd) * 28;
          bestY += (dy / dd) * 14;
        }

        // Use the AHC cluster color of the most common cluster in this group
        const clusterCounts: Record<number, number> = {};
        groupTerms.forEach((t) => { clusterCounts[t.cluster] = (clusterCounts[t.cluster] || 0) + 1; });
        const dominantCluster = parseInt(
          Object.entries(clusterCounts).sort((a, b) => b[1] - a[1])[0][0],
          10
        );
        const col = getClusterColor(dominantCluster);

        if (groupTerms.length >= 3) {
          svgParts.push(
            `<text x="${bestX.toFixed(1)}" y="${bestY.toFixed(1)}" text-anchor="middle" dominant-baseline="middle" font-family="var(--font-body)" font-size="13" font-weight="700" fill="${col}" opacity=".75" pointer-events="none">${escapeXml(label)}</text>`
          );
        } else {
          svgParts.push(
            `<text x="${bestX.toFixed(1)}" y="${(bestY + 14).toFixed(1)}" text-anchor="middle" font-family="var(--font-body)" font-size="10" font-weight="600" fill="${col}" opacity=".6" pointer-events="none">${escapeXml(label)}</text>`
          );
        }
      });
    } else if (!centroidPiles && selectedLabelModel !== null) {
      // Fallback: no centroidPiles available — use aggregate clusterLabels
      Object.entries(clusters).forEach(([cidStr, clusterTerms]) => {
        const cid = parseInt(cidStr, 10);
        const col = getClusterColor(cid);
        const label = clusterLabels[cid] || `Cluster ${cid + 1}`;
        const cx = clusterTerms.reduce((s, t) => s + sx(t.x), 0) / clusterTerms.length;
        const cy = clusterTerms.reduce((s, t) => s + sy(t.y), 0) / clusterTerms.length;

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
    }
    // If selectedLabelModel === null: no cluster label text rendered (user chose "None")

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
        `<text class="term-label" x="${px}" y="${py}" data-ox="${px}" data-oy="${py}" data-base-size="11" font-family="var(--font-body)" font-size="11" fill="${col}" opacity=".7" pointer-events="none">${escapeXml(t.term)}</text>`
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
  }, [terms, clusterLabels, centroidPiles, selectedLabelModel, liveCoords, selectedModelIds]);

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
          const baseSize = lbl.getAttribute('data-base-size') ?? '11';
          lbl.setAttribute('font-size', baseSize);
          lbl.setAttribute('opacity', '0.7');
          lbl.setAttribute('font-weight', 'normal');
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

      // Displace labels + enlarge inside lens
      svgEl.querySelectorAll<SVGTextElement>('.term-label').forEach((lbl) => {
        const ox = parseFloat(lbl.getAttribute('data-ox') ?? '0');
        const oy = parseFloat(lbl.getAttribute('data-oy') ?? '0');
        const dx = ox - mouseX;
        const dy = oy - mouseY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const baseSize = parseFloat(lbl.getAttribute('data-base-size') ?? '11');

        if (dist < LENS_RADIUS && dist > 0) {
          const t = 1 - dist / LENS_RADIUS; // 0 at edge, 1 at center
          const strength = (t * t) * MAX_DISPLACEMENT;
          const angle = Math.atan2(dy, dx);
          lbl.setAttribute('x', String(ox + Math.cos(angle) * strength));
          lbl.setAttribute('y', String(oy + Math.sin(angle) * strength));
          // Scale up font inside lens (lerp from baseSize to LENS_FONT_SIZE)
          const fontSize = baseSize + (LENS_FONT_SIZE - baseSize) * t;
          lbl.setAttribute('font-size', String(Math.round(fontSize)));
          lbl.setAttribute('opacity', '1');
          lbl.setAttribute('font-weight', '600');
        } else {
          lbl.setAttribute('x', String(ox));
          lbl.setAttribute('y', String(oy));
          lbl.setAttribute('font-size', String(baseSize));
          lbl.setAttribute('opacity', '0.7');
          lbl.setAttribute('font-weight', 'normal');
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
        const baseSize = lbl.getAttribute('data-base-size') ?? '11';
        lbl.setAttribute('font-size', baseSize);
        lbl.setAttribute('opacity', '0.7');
        lbl.setAttribute('font-weight', 'normal');
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
    <div className="term-map-container">
      {/* Chart controls row: pile label model selector */}
      <div className="term-map-controls">
        <label className="term-map-controls__label" htmlFor="pile-label-select">
          Pile labels from:
        </label>
        <select
          id="pile-label-select"
          className="term-map-controls__select"
          value={selectedLabelModel ?? '__none__'}
          onChange={(e) => {
            const v = e.target.value;
            setUserLabelChoice(v === '__none__' ? null : v);
          }}
          aria-label="Choose which model's pile labels to display on the term map"
        >
          {pileModelKeys.map((key) => (
            <option key={key} value={key}>
              {shortModelDisplayName(key)}
            </option>
          ))}
          <option value="__none__">None</option>
        </select>
      </div>

      {/* SVG term map */}
      <div
        ref={wrapRef}
        className="chart-wrap"
        role="img"
        aria-label="Term map visualization showing clusters of related terms"
        style={{ flex: '1' }}
      >
        <div
          style={{ width: '100%', height: '100%' }}
          dangerouslySetInnerHTML={{ __html: svgContent }}
        />
      </div>

      {/* Stress annotation — always visible */}
      <div className="term-map-stress" aria-label="MDS goodness-of-fit statistic">
        {liveCoords !== null && liveStress !== null
          ? `Kruskal's stress: ${liveStress.toFixed(3)} · Lower = better fit`
          : 'Stress: computed at analysis time'}
      </div>
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
