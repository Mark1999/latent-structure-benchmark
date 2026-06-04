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
 * The lens is only active at k=1 (auto-disabled when zoomed — §17 Stage 2
 * Q2 LOCKED decision).
 *
 * Stage 2 zoom model (§17.4): SVG content is wrapped in a
 * <g id="term-content" transform="scale(k)"> inside a .term-map-pan-viewport
 * div. The SVG viewBox is frozen at "0 0 W H" and never mutated. When k>1.02
 * OR at k=1 when SVG overflows the viewport, the pan-viewport gains
 * .term-map-pan-viewport--scrollable (overflow:auto) and native scrollbars
 * appear. Drag-pan is re-added (§17.11 — 2026-06-04) coexisting with native
 * scrollbars; active only when --scrollable is present; term-dot guard keeps
 * click/hover on dots working.
 * FREEZE RULE: label layout is computed once at k=1 and frozen; zoom only
 * mutates the <g transform> and the SVG width/height attrs — render() is
 * never called from the zoom path.
 */

import { useRef, useEffect, useLayoutEffect, useState, useCallback, useMemo } from 'react';
import { smacof } from '../lib/smacof';
import { procrustesAlign } from '../lib/procrustes';
import { poolCooccurrence, cooccurrenceToDistances } from '../lib/cooccurrence';
import { ahcCluster } from '../lib/ahcCluster';
import type { EllipseParams } from '../data/types';

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
  'var(--color-cluster-1)',
  'var(--color-cluster-2)',
  'var(--color-cluster-3)',
  'var(--color-cluster-4)',
  'var(--color-cluster-5)',
  'var(--color-cluster-6)',
  'var(--color-cluster-7)',
  'var(--color-cluster-8)',
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


// Lens constants — SVG-coordinate units at zoom=1
const LENS_RADIUS = 110;
const MAX_DISPLACEMENT = 65;
const LENS_FONT_SIZE = 13;

// Zoom constants
const MIN_ZOOM = 1;
const MAX_ZOOM = 8;
const ZOOM_STEP = 1.25;       // multiplicative step for +/- keyboard buttons (§17.3)
const ZOOM_SENSITIVITY = 0.0015;

/**
 * clientToSVGCoords — used exclusively by the lens (only active at k=1).
 * At k=1 the SVG viewBox is "0 0 W H" with no content-group scale in play
 * for the CTM, so getScreenCTM gives correct SVG-space coordinates.
 */
function clientToSVGCoords(svg: SVGSVGElement, clientX: number, clientY: number): { x: number; y: number } {
  const pt = svg.createSVGPoint();
  pt.x = clientX;
  pt.y = clientY;
  const ctm = svg.getScreenCTM();
  if (!ctm) return { x: clientX, y: clientY };
  const svgPt = pt.matrixTransform(ctm.inverse());
  return { x: svgPt.x, y: svgPt.y };
}

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
  /** Callback to toggle magnifying lens */
  onLensToggle?: () => void;
  /** 95% bootstrap confidence ellipses for each term */
  termUncertainty?: Record<string, EllipseParams | null>;
}

export function TermMap({
  termCoords,
  termClusters,
  clusterLabels,
  centroidPiles,
  cooccurrenceData,
  selectedModelIds,
  lensEnabled = false,
  onLensToggle,
  termUncertainty,
}: TermMapProps) {
  // wrapRef: the .chart-wrap div — ResizeObserver target and render() W×H source.
  const wrapRef = useRef<HTMLDivElement>(null);
  // panVpRef: the .term-map-pan-viewport div inside .chart-wrap — scroll/zoom target.
  const panVpRef = useRef<HTMLDivElement>(null);
  // svgContent: INNER content of the <g id="term-content"> only — no <svg> or <g> wrapper.
  // The <svg> and <g> are real React elements whose attributes are bound to state,
  // so re-renders driven by setZoomDisplay() re-assert the correct transform instead
  // of wiping it (fixes the dangerouslySetInnerHTML-rebuild/imperative-reset race).
  const [svgContent, setSvgContent] = useState<string>('');
  // svgBaseDims: the un-scaled logical W×H from the most recent render() call.
  // SVG width/height = baseDims × zoomDisplay; updated by render(), never by zoom.
  const [svgBaseDims, setSvgBaseDims] = useState<{ w: number; h: number }>({ w: 0, h: 0 });
  const [zoomDisplay, setZoomDisplay] = useState(1);
  const [showUncertainty, setShowUncertainty] = useState(false);
  const [showClusterLabels, setShowClusterLabels] = useState(true);

  // Stage 2 zoom state: k = content scale factor.
  // viewBox is ALWAYS frozen at "0 0 W H" — never mutated.
  // FREEZE RULE: zoom path must never call render() or touch label layout.
  const kRef = useRef<number>(1);
  const baseVBRef = useRef({ w: 0, h: 0 });
  // pendingScrollRef: deferred scroll-anchor target for keyboard zoom (+/−).
  // After setZoomDisplay(k) the SVG grows asynchronously via React re-render;
  // scroll must be applied AFTER the new SVG dimensions are committed to the DOM
  // or the browser will clamp scrollLeft/Top to the old (smaller) range.
  // handleWheel sets scroll synchronously (SVG already sized by applyScale in
  // old code) — but with Option A, handleWheel also needs deferred scroll.
  const pendingScrollRef = useRef<{ left: number; top: number } | null>(null);

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

  // ── Stage 2: manage pan-viewport scroll class (FREEZE RULE) ─────────────
  // Replaces the old applyScale class-toggle. In addition to the k>1.02 check,
  // also adds --scrollable at k=1 when the SVG overflows the viewport (§17.11 Fix B).
  // This makes bottom-clipped content reachable via scroll + drag-pan at k=1.
  // FREEZE RULE: this helper must NOT call render() or re-run label layout.
  const updateScrollableModifier = useCallback((k: number) => {
    const panVp = panVpRef.current;
    if (!panVp) return;

    // k>1.02: always scrollable
    if (k > 1.02) {
      panVp.classList.add('term-map-pan-viewport--scrollable');
      return;
    }

    // k=1: scrollable only if SVG actually overflows the viewport (bottom-clipping fix)
    const svg = panVp.querySelector<SVGSVGElement>('#term-svg');
    if (svg && (svg.scrollWidth > panVp.clientWidth || svg.scrollHeight > panVp.clientHeight)) {
      panVp.classList.add('term-map-pan-viewport--scrollable');
    } else {
      panVp.classList.remove('term-map-pan-viewport--scrollable');
    }
  }, []);

  // Keep applyScale as an alias so existing call sites (zoomByStep, resetZoom,
  // handleWheel) continue to work without renaming them all.
  const applyScale = updateScrollableModifier;

  // ── Keyboard zoom helpers (§17.3) ────────────────────────────────────────
  // Zoom toward the viewport center (keyboard users have no cursor anchor).
  const zoomByStep = useCallback((factor: number) => {
    const panVp = panVpRef.current;
    if (!panVp) return;
    // Guard: don't zoom if there is no SVG in the pan-viewport yet.
    if (!panVp.querySelector('#term-svg')) return;

    const oldK = kRef.current;
    const newK = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, oldK * factor));
    if (newK === oldK) return;

    // Anchor to viewport center: the content point currently at center stays centered
    const vpW = panVp.clientWidth;
    const vpH = panVp.clientHeight;
    const centerContentX = (panVp.scrollLeft + vpW / 2);
    const centerContentY = (panVp.scrollTop + vpH / 2);
    // Content coordinate (in logical SVG units) at center
    const logicalX = centerContentX / oldK;
    const logicalY = centerContentY / oldK;

    kRef.current = newK;
    applyScale(newK);

    // Defer scroll until after the React re-render expands the SVG to W×newK.
    // Setting scrollLeft before the SVG is sized would be clamped by the browser.
    pendingScrollRef.current = {
      left: logicalX * newK - vpW / 2,
      top:  logicalY * newK - vpH / 2,
    };

    setZoomDisplay(newK);
  }, [applyScale]);

  const resetZoom = useCallback(() => {
    const panVp = panVpRef.current;
    if (!panVp) return;
    // Cancel any pending deferred scroll (we're going back to origin).
    pendingScrollRef.current = null;
    // §17.4 binding: scrollTo(0,0) BEFORE removing --scrollable modifier
    // so the stale scroll offset cannot hide under overflow:hidden.
    panVp.scrollTo(0, 0);
    kRef.current = 1;
    applyScale(1);
    setZoomDisplay(1);
  }, [applyScale]);

  const render = useCallback(() => {
    if (!wrapRef.current) return;
    const rect = wrapRef.current.getBoundingClientRect();
    const W = Math.max(rect.width || 600, 600);
    // §17.1 defensive cap: H can never exceed the viewport even if CSS regresses.
    // This breaks the ResizeObserver loop at the source: if overflow leaks and the
    // container reports a height larger than the viewport, we clamp it here so the
    // SVG cannot grow the parent further.
    const H = Math.min(Math.max(rect.height || 400, 400), window.innerHeight);

    if (terms.length === 0) return;

    const pad = { t: 30, r: 80, b: 52, l: 50 };
    const pw = W - pad.l - pad.r;
    const ph = H - pad.t - pad.b;

    let xMin = Infinity, xMax = -Infinity, yMin = Infinity, yMax = -Infinity;
    terms.forEach(({ x, y, term }) => {
      const u = (showUncertainty && termUncertainty) ? termUncertainty[term] : null;
      const smaj = u?.semi_major || 0;
      const smin = u?.semi_minor || 0;
      xMin = Math.min(xMin, x - smaj); xMax = Math.max(xMax, x + smaj);
      yMin = Math.min(yMin, y - smin); yMax = Math.max(yMax, y + smin);
    });

    const xP = (xMax - xMin) * 0.08 || 0.08;
    const yP = (yMax - yMin) * 0.08 || 0.08;
    xMin -= xP; xMax += xP; yMin -= yP; yMax += yP;

    const sx = (v: number) => pad.l + ((v - xMin) / (xMax - xMin)) * pw;
    const sy = (v: number) => pad.t + (1 - (v - yMin) / (yMax - yMin)) * ph;

    // Compass label offset algorithm to prevent overlaps
    const labelLayouts: { x: number; y: number; anchor: string }[] = [];
    const placedBoxes: { x1: number; x2: number; y1: number; y2: number }[] = [];

    const DIRECTIONS: {
      anchor: string;
      dx: number;
      dy: number;
      bx: (cx: number, w: number) => number;
      by: (cy: number, h: number) => number;
    }[] = [
      { anchor: 'start',  dx: 6,   dy: 3,   bx: (cx) => cx + 6,          by: (cy) => cy - 7 },      // E
      { anchor: 'start',  dx: 5,   dy: 9,   bx: (cx) => cx + 5,          by: (cy) => cy - 1 },      // SE
      { anchor: 'middle', dx: 0,   dy: 12,  bx: (cx, w) => cx - w / 2,   by: (cy) => cy + 2 },      // S
      { anchor: 'end',    dx: -5,  dy: 9,   bx: (cx, w) => cx - 5 - w,   by: (cy) => cy - 1 },      // SW
      { anchor: 'end',    dx: -6,  dy: 3,   bx: (cx, w) => cx - 6 - w,   by: (cy) => cy - 7 },      // W
      { anchor: 'end',    dx: -5,  dy: -3,  bx: (cx, w) => cx - 5 - w,   by: (cy) => cy - 13 },     // NW
      { anchor: 'middle', dx: 0,   dy: -7,  bx: (cx, w) => cx - w / 2,   by: (cy) => cy - 17 },     // N
      { anchor: 'start',  dx: 5,   dy: -3,  bx: (cx) => cx + 5,          by: (cy) => cy - 13 },     // NE
    ];

    terms.forEach((t) => {
      const cx = sx(t.x);
      const cy = sy(t.y);
      const w = t.term.length * 5.8; // approximate character width
      const h = 10;                  // label height

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

        // Penalty 2: overlap with any other dots
        terms.forEach((otherT) => {
          if (otherT.term === t.term) return;
          const ocx = sx(otherT.x);
          const ocy = sy(otherT.y);
          if (ocx >= bx1 - 3 && ocx <= bx2 + 3 && ocy >= by1 - 3 && ocy <= by2 + 3) {
            penalty += 150;
          }
        });

        // Penalty 3: out of bounds
        if (bx1 < pad.l || bx2 > W - pad.r || by1 < pad.t || by2 > H - pad.b) {
          penalty += 250;
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

    // Group by AHC cluster (for dot color — always computed)
    const clusters: Record<number, TermEntry[]> = {};
    terms.forEach((t) => {
      if (!clusters[t.cluster]) clusters[t.cluster] = [];
      clusters[t.cluster].push(t);
    });

    // Store base logical dimensions so zoom math works even if baseDims state
    // hasn't updated yet (e.g., applyScale called mid-render).
    // kRef.current stays at its current value; render() may be called on resize
    // (which resets zoom to 1 implicitly via setSvgBaseDims + setZoomDisplay).
    baseVBRef.current = { w: W, h: H };
    // Reset zoom to 1 on every render (re-layout).
    kRef.current = 1;

    // svgParts: INNER content of the <g id="term-content"> only.
    // The <svg> and <g> are emitted as real React elements in JSX — their
    // transform/width/height attributes are bound to zoomDisplay/svgBaseDims
    // state, so React re-renders driven by setZoomDisplay() will RE-ASSERT
    // the correct scale(k) instead of resetting to scale(1).
    const svgParts: string[] = [];

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
    if (showClusterLabels && selectedLabelModel && centroidPiles && centroidPiles[selectedLabelModel]) {
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

        if (groupTerms.length >= 3) {
          svgParts.push(
            `<text x="${bestX.toFixed(1)}" y="${bestY.toFixed(1)}" text-anchor="middle" dominant-baseline="middle" font-family="var(--font-body)" font-size="26" font-weight="700" fill="#000000" opacity="1" pointer-events="none">${escapeXml(label)}</text>`
          );
        } else {
          svgParts.push(
            `<text x="${bestX.toFixed(1)}" y="${(bestY + 14).toFixed(1)}" text-anchor="middle" font-family="var(--font-body)" font-size="20" font-weight="600" fill="#000000" opacity="1" pointer-events="none">${escapeXml(label)}</text>`
          );
        }
      });
    } else if (showClusterLabels && !centroidPiles && selectedLabelModel !== null) {
      // Fallback: no centroidPiles available — use aggregate clusterLabels
      Object.entries(clusters).forEach(([cidStr, clusterTerms]) => {
        const cid = parseInt(cidStr, 10);
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
            `<text x="${bestX.toFixed(1)}" y="${bestY.toFixed(1)}" text-anchor="middle" dominant-baseline="middle" font-family="var(--font-body)" font-size="26" font-weight="700" fill="#000000" opacity="1" pointer-events="none">${escapeXml(label)}</text>`
          );
        } else if (clusterTerms.length >= 1) {
          svgParts.push(
            `<text x="${bestX.toFixed(1)}" y="${(bestY + 14).toFixed(1)}" text-anchor="middle" font-family="var(--font-body)" font-size="20" font-weight="600" fill="#000000" opacity="1" pointer-events="none">${escapeXml(label)}</text>`
          );
        }
      });
    }

    // ── Ellipses rendering ──────────────────────────────────────────────────
    if (showUncertainty && termUncertainty) {
      terms.forEach((t, i) => {
        const u = termUncertainty[t.term];
        if (!u || u.semi_major <= 0) return;
        const cx = sx(t.x);
        const cy = sy(t.y);
        const rx = (u.semi_major / (xMax - xMin)) * pw;
        const ry = (u.semi_minor / (yMax - yMin)) * ph;
        const deg = -(u.rotation_rad * 180) / Math.PI;
        const col = getClusterColor(t.cluster);
        svgParts.push(
          `<ellipse class="term-ellipse" cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" rx="${rx.toFixed(1)}" ry="${ry.toFixed(1)}" transform="rotate(${deg.toFixed(1)},${cx.toFixed(1)},${cy.toFixed(1)})" fill="${col}" stroke="${col}" fill-opacity="0.08" stroke-opacity="0.25" stroke-width="1" data-idx="${i}" data-ox="${cx.toFixed(1)}" data-oy="${cy.toFixed(1)}" data-deg="${deg.toFixed(1)}" pointer-events="none"/>`
        );
      });
    }

    // Term dots — store original coords as data attributes for hover animation
    terms.forEach((t, i) => {
      const px = sx(t.x).toFixed(1);
      const py = sy(t.y).toFixed(1);
      const col = getClusterColor(t.cluster);
      svgParts.push(
        `<circle class="term-dot" cx="${px}" cy="${py}" r="4" fill="${col}" stroke="#fff" stroke-width=".8" data-cluster="${t.cluster}" data-idx="${i}" data-ox="${px}" data-oy="${py}" cursor="pointer"/>`
      );
    });

    // Term labels — visible, small, positioned using computed layout offsets
    terms.forEach((t, i) => {
      const layout = labelLayouts[i];
      const px = layout.x.toFixed(1);
      const py = layout.y.toFixed(1);
      const col = getClusterColor(t.cluster);
      svgParts.push(
        `<text class="term-label" x="${px}" y="${py}" data-ox="${px}" data-oy="${py}" data-base-size="11" font-family="var(--font-body)" font-size="11" fill="${col}" opacity=".7" text-anchor="${layout.anchor}" pointer-events="none">${escapeXml(t.term)}</text>`
      );
    });

    // Footer annotation
    const nTerms = terms.length;
    const nClusters = Object.keys(clusters).length;
    const modelNote = liveCoords && selectedModelIds
      ? `${selectedModelIds.size} model${selectedModelIds.size !== 1 ? 's' : ''} · `
      : '';
    svgParts.push(
      `<text x="${(pad.l + pw / 2).toFixed(1)}" y="${H - 14}" text-anchor="middle" font-family="var(--font-body)" font-size="10" fill="#a0a098">${modelNote}${nTerms} shared terms · ${nClusters} clusters from pile-sort co-occurrence</text>`
    );

    // svgParts is the INNER content of <g id="term-content"> only.
    // The outer <svg> and <g> are rendered as real React elements in JSX.
    setSvgContent(svgParts.join(''));
    // Update base dimensions → drives SVG width/height in JSX (W×k, H×k).
    // Also reset zoom display to 1 since render() always produces a k=1 layout.
    setSvgBaseDims({ w: W, h: H });
    setZoomDisplay(1);
  }, [terms, clusterLabels, centroidPiles, selectedLabelModel, liveCoords, selectedModelIds, showUncertainty, showClusterLabels, termUncertainty]);

  // Re-render on resize or term/coord change
  useEffect(() => {
    render();
    const observer = new ResizeObserver(() => render());
    if (wrapRef.current) observer.observe(wrapRef.current);
    return () => observer.disconnect();
  }, [render]);

  // Note: the post-injection applyScale effect is intentionally removed.
  // The <g id="term-content"> transform and SVG width/height are now React-state-
  // driven (zoomDisplay, svgBaseDims), so no imperative DOM patch is needed after
  // React reconciles svgContent. render() calls setZoomDisplay(1) + setSvgBaseDims
  // to reset the zoom state atomically with the new inner content.
  // §17.11: the svgContent useLayoutEffect below re-checks for k=1 overflow
  // (bottom-clipping fix) after React commits the new SVG.

  // ── Zoom & pan interaction (Stage 2) ─────────────────────────────────────
  // viewBox is never mutated. Zoom changes k → scales <g> → scrollbars pan.
  // Drag-pan re-added per §17.11 (UI/UX verdict 2026-06-04):
  //   - Active only when --scrollable class is present on the pan-viewport.
  //   - Left button only; term-dot guard preserves click/hover on dots.
  //   - window listeners for mousemove/mouseup so fast drags outside the
  //     viewport don't leave drag state stuck.
  //   - Cleanup removes all new listeners (including window ones).
  useEffect(() => {
    const panVp = panVpRef.current;
    if (!panVp) return;

    function handleWheel(e: WheelEvent) {
      // §17.2 WCAG Level-A scroll-trap fix: only zoom on Ctrl+wheel (or trackpad
      // pinch, which browsers also report as ctrlKey=true). Plain wheel scroll
      // passes through to native page/viewport scrolling when k=1, and to native
      // pan-viewport scrolling when k>1 — no preventDefault on plain scroll.
      if (!e.ctrlKey) return;
      e.preventDefault();

      // Guard: don't zoom if there is no SVG in the pan-viewport yet.
      if (!panVp!.querySelector('#term-svg')) return;

      const oldK = kRef.current;
      const delta = -e.deltaY * ZOOM_SENSITIVITY;
      const newK = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, oldK * (1 + delta)));
      if (newK === oldK) return;

      // Scroll-anchor: keep the content point under the cursor fixed.
      // viewportOffsetX/Y: cursor position relative to the pan-viewport's top-left.
      const vpRect = panVp!.getBoundingClientRect();
      const vpOffsetX = e.clientX - vpRect.left;
      const vpOffsetY = e.clientY - vpRect.top;

      // Content pixel position under cursor (in scaled-px coords at oldK)
      const contentPxX = panVp!.scrollLeft + vpOffsetX;
      const contentPxY = panVp!.scrollTop  + vpOffsetY;

      // Logical SVG coordinate under cursor (invariant to k)
      const logicalX = contentPxX / oldK;
      const logicalY = contentPxY / oldK;

      kRef.current = newK;
      applyScale(newK);

      // Defer scroll until after the React re-render expands the SVG to W×newK.
      // Setting scrollLeft synchronously would be clamped to the old smaller range.
      pendingScrollRef.current = {
        left: logicalX * newK - vpOffsetX,
        top:  logicalY * newK - vpOffsetY,
      };

      setZoomDisplay(newK);
    }

    function handleDblClick() {
      resetZoom();
    }

    // ── Drag-pan handlers (§17.11) ────────────────────────────────────────
    // State for drag-pan: start scroll position and start mouse position.
    let isDragging = false;
    let dragStartScrollLeft = 0;
    let dragStartScrollTop = 0;
    let dragStartMouseX = 0;
    let dragStartMouseY = 0;

    function handleMouseDown(e: MouseEvent) {
      // Only when --scrollable is present (k>1.02 or k=1-overflow)
      if (!panVp!.classList.contains('term-map-pan-viewport--scrollable')) return;
      // Left button only
      if (e.button !== 0) return;
      // Don't drag from a dot — preserves click/hover on term dots
      const target = e.target as Element;
      if (target.classList.contains('term-dot')) return;

      e.preventDefault();
      isDragging = true;
      dragStartScrollLeft = panVp!.scrollLeft;
      dragStartScrollTop = panVp!.scrollTop;
      dragStartMouseX = e.clientX;
      dragStartMouseY = e.clientY;
      panVp!.classList.add('term-map-pan-viewport--dragging');
    }

    function handleMouseMovePan(e: MouseEvent) {
      if (!isDragging) return;
      const dx = e.clientX - dragStartMouseX;
      const dy = e.clientY - dragStartMouseY;
      panVp!.scrollLeft = dragStartScrollLeft - dx;
      panVp!.scrollTop = dragStartScrollTop - dy;
    }

    function handleMouseUpPan() {
      if (!isDragging) return;
      isDragging = false;
      panVp!.classList.remove('term-map-pan-viewport--dragging');
    }

    function handleMouseLeavePan() {
      // mouseleave on panVp: cancel drag so a slow leave doesn't leave stuck state.
      // Fast drags are caught by window mouseup; this handles the slow/keyboard case.
      if (isDragging) {
        isDragging = false;
        panVp!.classList.remove('term-map-pan-viewport--dragging');
      }
    }

    panVp.addEventListener('wheel', handleWheel, { passive: false });
    panVp.addEventListener('dblclick', handleDblClick);
    panVp.addEventListener('mousedown', handleMouseDown);
    panVp.addEventListener('mouseleave', handleMouseLeavePan);
    // window listeners so fast drags outside the viewport don't stick
    window.addEventListener('mousemove', handleMouseMovePan);
    window.addEventListener('mouseup', handleMouseUpPan);

    return () => {
      panVp.removeEventListener('wheel', handleWheel);
      panVp.removeEventListener('dblclick', handleDblClick);
      panVp.removeEventListener('mousedown', handleMouseDown);
      panVp.removeEventListener('mouseleave', handleMouseLeavePan);
      window.removeEventListener('mousemove', handleMouseMovePan);
      window.removeEventListener('mouseup', handleMouseUpPan);
    };
  }, [svgContent, applyScale, resetZoom]);

  // ── Deferred scroll-anchor flush (Option A companion) ───────────────────
  // After React commits the SVG at W×zoomDisplay, apply the pending scroll
  // target so the anchor point (cursor or viewport-center) stays fixed.
  // useLayoutEffect fires synchronously after DOM mutations, before paint —
  // the SVG is at its new size when this runs, so scrollLeft is not clamped.
  useLayoutEffect(() => {
    const pending = pendingScrollRef.current;
    if (!pending) return;
    pendingScrollRef.current = null;
    const panVp = panVpRef.current;
    if (!panVp) return;
    panVp.scrollLeft = pending.left;
    panVp.scrollTop  = pending.top;
  }, [zoomDisplay]);

  // ── §17.11 Fix B: re-check scrollable modifier after SVG content commits ──
  // When svgContent changes (new render), the SVG may overflow at k=1 — call
  // updateScrollableModifier so the --scrollable class is added if needed.
  // This makes bottom-clipped content reachable at k=1 without zooming in.
  // Must run after DOM paint so svg.scrollWidth/scrollHeight are available.
  useLayoutEffect(() => {
    updateScrollableModifier(kRef.current);
  }, [svgContent, updateScrollableModifier]);

  // ── Q2 LOCKED: auto-disable lens when k > 1.02 ───────────────────────────
  // When the user zooms in, deactivate the lens immediately.
  // The lens only runs its coordinate math at k=1 where clientToSVGCoords
  // via getScreenCTM is correct. At k>1 the lens checkbox is rendered
  // disabled with a tooltip explaining why.
  const lensDisabledByZoom = zoomDisplay > 1.02;

  useEffect(() => {
    // If lens was on and user zoomed in, trigger the parent's onLensToggle
    // to deactivate it (parent owns the lensEnabled state).
    if (lensDisabledByZoom && lensEnabled && onLensToggle) {
      onLensToggle();
    }
  }, [lensDisabledByZoom, lensEnabled, onLensToggle]);

  // ── Magnifying lens interaction ───────────────────────────────────────────
  // rafRef: pending requestAnimationFrame id (used to cancel on cleanup)
  const rafRef = useRef<number | null>(null);
  // lensRingRef: the <circle> element appended to the SVG as a lens outline
  const lensRingRef = useRef<SVGCircleElement | null>(null);

  useEffect(() => {
    const panVp = panVpRef.current;
    if (!panVp) return;

    // Create / remove lens ring element whenever lensEnabled changes
    if (!lensEnabled) {
      // Reset all displaced elements back to their original positions
      const svg = panVp.querySelector<SVGSVGElement>('#term-svg');
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
        svg.querySelectorAll<SVGEllipseElement>('.term-ellipse').forEach((ell) => {
          const ox = ell.getAttribute('data-ox') ?? '0';
          const oy = ell.getAttribute('data-oy') ?? '0';
          ell.setAttribute('cx', ox);
          ell.setAttribute('cy', oy);
          const deg = ell.getAttribute('data-deg') ?? '0';
          ell.setAttribute('transform', `rotate(${deg},${ox},${oy})`);
        });
        if (lensRingRef.current) {
          lensRingRef.current.remove();
          lensRingRef.current = null;
        }
      }
      return;
    }

    // Lens only runs at k=1 (Q2 LOCKED). The lensDisabledByZoom guard above
    // ensures lensEnabled becomes false before k>1 takes effect. We add a
    // defensive early-return here in case the disable callback is async.
    function applyLens(svgEl: SVGSVGElement, clientX: number, clientY: number) {
      // Q2 safety guard: skip lens math if k > 1 (should not happen given the
      // auto-disable above, but defensive against race conditions)
      if (kRef.current > 1.02) return;

      const svgPt = clientToSVGCoords(svgEl, clientX, clientY);
      const mouseX = svgPt.x;
      const mouseY = svgPt.y;

      // At k=1 the lens radius/displacement are in unscaled SVG units.
      const effectiveRadius = LENS_RADIUS;
      const effectiveDisplacement = MAX_DISPLACEMENT;

      // Ensure lens ring exists
      if (!lensRingRef.current) {
        const ring = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        ring.setAttribute('class', 'lens-ring');
        ring.setAttribute('fill', 'none');
        ring.setAttribute('stroke', 'rgba(0,0,0,0.15)');
        ring.setAttribute('stroke-width', '1');
        ring.setAttribute('stroke-dasharray', '4 2');
        ring.setAttribute('pointer-events', 'none');
        // Append to the content group so it scales with the rest (at k=1 this is a no-op)
        const contentG = svgEl.querySelector<SVGGElement>('#term-content');
        (contentG ?? svgEl).appendChild(ring);
        lensRingRef.current = ring;
      }

      lensRingRef.current.setAttribute('cx', String(mouseX));
      lensRingRef.current.setAttribute('cy', String(mouseY));
      lensRingRef.current.setAttribute('r', String(effectiveRadius));

      // Displace dots
      svgEl.querySelectorAll<SVGCircleElement>('.term-dot').forEach((dot) => {
        const ox = parseFloat(dot.getAttribute('data-ox') ?? '0');
        const oy = parseFloat(dot.getAttribute('data-oy') ?? '0');
        const dx = ox - mouseX;
        const dy = oy - mouseY;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < effectiveRadius && dist > 0) {
          const strength = Math.pow(1 - dist / effectiveRadius, 2) * effectiveDisplacement;
          const angle = Math.atan2(dy, dx);
          dot.setAttribute('cx', String(ox + Math.cos(angle) * strength));
          dot.setAttribute('cy', String(oy + Math.sin(angle) * strength));
        } else {
          dot.setAttribute('cx', String(ox));
          dot.setAttribute('cy', String(oy));
        }
      });

      // Displace ellipses
      svgEl.querySelectorAll<SVGEllipseElement>('.term-ellipse').forEach((ell) => {
        const ox = parseFloat(ell.getAttribute('data-ox') ?? '0');
        const oy = parseFloat(ell.getAttribute('data-oy') ?? '0');
        const dx = ox - mouseX;
        const dy = oy - mouseY;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < effectiveRadius && dist > 0) {
          const strength = Math.pow(1 - dist / effectiveRadius, 2) * effectiveDisplacement;
          const angle = Math.atan2(dy, dx);
          const nx = ox + Math.cos(angle) * strength;
          const ny = oy + Math.sin(angle) * strength;
          ell.setAttribute('cx', String(nx));
          ell.setAttribute('cy', String(ny));
          const deg = ell.getAttribute('data-deg') ?? '0';
          ell.setAttribute('transform', `rotate(${deg},${nx},${ny})`);
        } else {
          ell.setAttribute('cx', String(ox));
          ell.setAttribute('cy', String(oy));
          const deg = ell.getAttribute('data-deg') ?? '0';
          ell.setAttribute('transform', `rotate(${deg},${ox},${oy})`);
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

        if (dist < effectiveRadius && dist > 0) {
          const t = 1 - dist / effectiveRadius;
          const strength = (t * t) * effectiveDisplacement;
          const angle = Math.atan2(dy, dx);
          lbl.setAttribute('x', String(ox + Math.cos(angle) * strength));
          lbl.setAttribute('y', String(oy + Math.sin(angle) * strength));
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
      svgEl.querySelectorAll<SVGEllipseElement>('.term-ellipse').forEach((ell) => {
        const ox = ell.getAttribute('data-ox') ?? '0';
        const oy = ell.getAttribute('data-oy') ?? '0';
        ell.setAttribute('cx', ox);
        ell.setAttribute('cy', oy);
        const deg = ell.getAttribute('data-deg') ?? '0';
        ell.setAttribute('transform', `rotate(${deg},${ox},${oy})`);
      });
      if (lensRingRef.current) {
        lensRingRef.current.remove();
        lensRingRef.current = null;
      }
    }

    // `panVp` is const and was narrowed to HTMLDivElement by the guard above;
    // the non-null assertion below is safe since panVp cannot be reassigned.
    const safePanVp: HTMLDivElement = panVp;

    function handleMouseMove(e: MouseEvent) {
      if (rafRef.current !== null) return;
      rafRef.current = requestAnimationFrame(() => {
        rafRef.current = null;
        const svg = safePanVp.querySelector<SVGSVGElement>('#term-svg');
        if (!svg) return;
        applyLens(svg, e.clientX, e.clientY);
      });
    }

    function handleMouseLeave() {
      if (rafRef.current !== null) {
        cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }
      const svg = safePanVp.querySelector<SVGSVGElement>('#term-svg');
      if (svg) resetLens(svg);
    }

    safePanVp.addEventListener('mousemove', handleMouseMove);
    safePanVp.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      safePanVp.removeEventListener('mousemove', handleMouseMove);
      safePanVp.removeEventListener('mouseleave', handleMouseLeave);
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
  }, [lensEnabled, svgContent, showUncertainty]);

  // ── Hover highlight interaction ───────────────────────────────────────────
  useEffect(() => {
    const panVp = panVpRef.current;
    if (!panVp) return;

    const svg = panVp.querySelector<SVGSVGElement>('#term-svg');
    if (!svg) return;

    function handleMouseOver(e: MouseEvent) {
      const target = e.target as SVGElement;
      if (target.classList.contains('term-dot')) {
        const idx = target.getAttribute('data-idx');
        if (idx !== null) {
          const ell = svg!.querySelector(`.term-ellipse[data-idx="${idx}"]`);
          if (ell) {
            ell.setAttribute('fill-opacity', '0.22');
            ell.setAttribute('stroke-opacity', '0.7');
            ell.setAttribute('stroke-width', '1.5');
          }
          const lbl = svg!.querySelector(`.term-label[data-idx="${idx}"]`);
          if (lbl) {
            lbl.setAttribute('opacity', '1');
            lbl.setAttribute('font-weight', '700');
          }
        }
      }
    }

    function handleMouseOut(e: MouseEvent) {
      const target = e.target as SVGElement;
      if (target.classList.contains('term-dot')) {
        const idx = target.getAttribute('data-idx');
        if (idx !== null) {
          const ell = svg!.querySelector(`.term-ellipse[data-idx="${idx}"]`);
          if (ell) {
            ell.setAttribute('fill-opacity', '0.08');
            ell.setAttribute('stroke-opacity', '0.25');
            ell.setAttribute('stroke-width', '1');
          }
          const lbl = svg!.querySelector(`.term-label[data-idx="${idx}"]`);
          if (lbl) {
            lbl.setAttribute('opacity', '0.7');
            lbl.setAttribute('font-weight', 'normal');
          }
        }
      }
    }

    panVp.addEventListener('mouseover', handleMouseOver);
    panVp.addEventListener('mouseout', handleMouseOut);

    return () => {
      panVp.removeEventListener('mouseover', handleMouseOver);
      panVp.removeEventListener('mouseout', handleMouseOut);
    };
  }, [svgContent]);


  if (terms.length === 0) {
    return (
      <div ref={wrapRef} className="chart-wrap">
        <div className="viz-placeholder">No term data available for this domain.</div>
      </div>
    );
  }

  // Dynamic aria-label: when uncertainty ellipses are visible, inform AT users
  const hasEllipses =
    showUncertainty &&
    termUncertainty != null &&
    Object.values(termUncertainty).some((v) => v != null);
  const termMapAriaLabel = hasEllipses
    ? 'Term map visualization showing clusters of related terms with confidence ellipses displayed. Ellipse parameters (semi-major axis, semi-minor axis, rotation, and bootstrap sample count) are available in the Read as table view.'
    : 'Term map visualization showing clusters of related terms';

  return (
    <div className="term-map-container">
      {/* Controls bar — OUTSIDE the pan-viewport so it stays fixed when scrolling (DOM order, §17.4) */}
      <div className="term-map-controls" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label className="term-map-controls__label" htmlFor="pile-label-select">
            Overlay category names from:
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

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', fontSize: '12px', fontFamily: 'var(--font-body)', color: 'var(--color-text-primary)', userSelect: 'none' }}>
            <input
              type="checkbox"
              checked={showUncertainty}
              onChange={(e) => setShowUncertainty(e.target.checked)}
              style={{ cursor: 'pointer' }}
            />
            Show uncertainty
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', fontSize: '12px', fontFamily: 'var(--font-body)', color: 'var(--color-text-primary)', userSelect: 'none' }}>
            <input
              type="checkbox"
              checked={showClusterLabels}
              onChange={(e) => setShowClusterLabels(e.target.checked)}
              style={{ cursor: 'pointer' }}
            />
            Show cluster labels
          </label>
          {/* Q2 LOCKED: lens checkbox disabled when zoomed in (§17 Stage 2) */}
          <label
            style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: lensDisabledByZoom ? 'default' : 'pointer', fontSize: '12px', fontFamily: 'var(--font-body)', color: lensDisabledByZoom ? 'var(--color-text-caption)' : 'var(--color-text-primary)', userSelect: 'none' }}
            title={lensDisabledByZoom ? 'Zoom out to 100% to use the magnifying lens' : 'Hover to magnify and separate crowded term labels'}
          >
            <input
              type="checkbox"
              checked={lensEnabled && !lensDisabledByZoom}
              onChange={onLensToggle}
              disabled={lensDisabledByZoom}
              style={{ cursor: lensDisabledByZoom ? 'default' : 'pointer' }}
            />
            Magnifying lens
          </label>
        </div>
      </div>

      {/* chart-wrap: outer border container — ResizeObserver target.
          Overflow hidden (scoped via .term-map-container > .chart-wrap in CSS).
          This is the stable bounding box that render() measures W×H from. */}
      <div
        ref={wrapRef}
        className="chart-wrap"
        role="img"
        aria-label={termMapAriaLabel}
      >
        {/* Pan-viewport: clips and scrolls the scaled SVG (§17.4 Stage 2).
            At k=1: overflow:hidden (base class) — pixel-identical to Stage 1.
            At k>1: .term-map-pan-viewport--scrollable adds overflow:auto.
            Controls bar + stress footer are OUTSIDE chart-wrap in DOM order
            so they stay fixed regardless of scroll state.

            Option A (architectural fix for zoom-wipe bug):
            - <svg> and <g id="term-content"> are real React elements.
            - transform on <g> is bound to `zoomDisplay` state.
            - SVG width/height are bound to svgBaseDims × zoomDisplay state.
            - Only the children of <g> come from the svgContent string.
            - A setZoomDisplay() re-render now RE-ASSERTS scale(k) instead
              of rebuilding from the hardcoded "scale(1)" string. */}
        <div
          ref={panVpRef}
          className="term-map-pan-viewport"
        >
          {svgBaseDims.w > 0 && (
            <svg
              id="term-svg"
              width={Math.round(svgBaseDims.w * zoomDisplay)}
              height={Math.round(svgBaseDims.h * zoomDisplay)}
              viewBox={`0 0 ${svgBaseDims.w} ${svgBaseDims.h}`}
            >
              <g
                id="term-content"
                transform={`scale(${zoomDisplay})`}
                dangerouslySetInnerHTML={{ __html: svgContent }}
              />
            </svg>
          )}
        </div>
      </div>

      {/* Stress + zoom annotation — OUTSIDE pan-viewport (DOM order keeps it fixed, §17.4) */}
      <div
        className="term-map-stress"
        aria-live="polite"
        aria-label="Map controls: stress statistic and zoom level"
      >
        <span>
          {liveCoords !== null && liveStress !== null
            ? `Kruskal's stress: ${liveStress.toFixed(3)} · Lower = better fit`
            : 'Stress: computed at analysis time'}
          {' '}
          <span style={{ color: 'var(--color-text-caption)', fontSize: 'var(--font-size-xs)' }}>
            Ctrl + scroll to zoom
          </span>
        </span>
        <span className="term-map-controls__zoom-group">
          {/* §17.3: keyboard −/+ zoom buttons */}
          <button
            type="button"
            className="term-map-controls__zoom-btn"
            onClick={() => zoomByStep(1 / ZOOM_STEP)}
            disabled={zoomDisplay <= MIN_ZOOM + 0.01}
            aria-label="Zoom out"
          >
            −
          </button>
          <button
            type="button"
            className="term-map-controls__zoom-btn"
            onClick={() => zoomByStep(ZOOM_STEP)}
            disabled={zoomDisplay >= MAX_ZOOM - 0.01}
            aria-label="Zoom in"
          >
            +
          </button>
          {/* §17.3: Reset zoom — shown only when zoomed in */}
          {zoomDisplay > 1.02 && (
            <button
              type="button"
              className="term-map-controls__zoom-reset"
              onClick={resetZoom}
              aria-label="Reset zoom to 100%"
            >
              Reset zoom
            </button>
          )}
          {zoomDisplay > 1.02 && (
            <span className="term-map-stress__zoom">
              {Math.round(zoomDisplay * 100)}%
            </span>
          )}
        </span>
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
