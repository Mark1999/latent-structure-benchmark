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
import { placeLabels } from '../lib/labelPlacement';
import type { LabelSpec } from '../lib/labelPlacement';
// displayModel moved to ChartToolbar (TM-B: overlay selector lifted from TermMap)
import type { EllipseParams, SutropCsiEntry } from '../data/types';

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
  /**
   * Lifted state: the effective pile-label model key (or null for None).
   * Owned by ContentArea and passed to ChartToolbar for the overlay selector.
   * §3.1.1(b)(ii) TM-B.
   */
  overlayPileLabelKey?: string | null;
  /** Called when the overlay selector changes. */
  onOverlayPileLabelKeyChange?: (key: string | null) => void;
  /**
   * Lifted state: whether uncertainty ellipses are shown.
   * Default: true (Show uncertainty ON per §3.1.1(b)(ii)).
   */
  showUncertainty?: boolean;
  /** Called when the Show uncertainty checkbox changes. */
  onShowUncertaintyChange?: (v: boolean) => void;
  /**
   * Lifted state: whether cluster labels are shown.
   * Default: true (Show cluster labels ON per §3.1.1(b)(ii)).
   */
  showClusterLabels?: boolean;
  /** Called when the Show cluster labels checkbox changes. */
  onShowClusterLabelsChange?: (v: boolean) => void;
  /**
   * Called when zoom-level exceeds 1.02 (lens auto-disable threshold).
   * ContentArea uses this to keep ChartToolbar's lens checkbox in sync.
   */
  onLensDisabledByZoomChange?: (disabled: boolean) => void;
  /**
   * Sutrop CSI salience rankings per model_id, as published in the domain JSON.
   * Each array is sorted descending by CSI (Sutrop CSI salience measure).
   * Used for zoom-dependent term-label density gate: top 50% shown at k=1,
   * all shown at k>1.5 (§3.1.1(c) AC4, CDA SME N2).
   * Salience source: Sutrop CSI (published field, not recomputed client-side).
   */
  salienceRanks?: Record<string, SutropCsiEntry[]>;
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
  overlayPileLabelKey,
  showUncertainty: showUncertaintyProp,
  showClusterLabels: showClusterLabelsProp,
  onLensDisabledByZoomChange,
  salienceRanks,
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
  // hiddenClusterLabels: labels that could not be placed due to collision.
  // Rendered in the footnote list below the chart (UI/UX verdict: footnote-list fallback).
  const [hiddenClusterLabels, setHiddenClusterLabels] = useState<string[]>([]);
  // hasSalienceData: true when salienceRanks is populated (used in JSX for caption/gate).
  const hasSalienceData = useMemo(
    () => !!salienceRanks && Object.keys(salienceRanks).length > 0,
    [salienceRanks]
  );
  // svgBaseDims: the un-scaled logical W×H from the most recent render() call.
  // SVG width/height = baseDims × zoomDisplay; updated by render(), never by zoom.
  const [svgBaseDims, setSvgBaseDims] = useState<{ w: number; h: number }>({ w: 0, h: 0 });
  const [zoomDisplay, setZoomDisplay] = useState(1);
  // showUncertainty / showClusterLabels: lifted state, controlled by parent via props.
  // Defaults: ON for uncertainty (§3.1.1(b)(ii) binding), ON for cluster labels.
  // Fall back to true if props are undefined (backwards-compat when rendered standalone).
  const showUncertainty = showUncertaintyProp ?? true;
  const showClusterLabels = showClusterLabelsProp ?? true;

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

  // When overlayPileLabelKey prop is provided (TM-B lifted state), use it directly.
  // When not provided (standalone usage or legacy callers), fall back to internal state.
  // userLabelChoice: internal uncontrolled path (used when overlayPileLabelKey prop is absent).
  // The setter is intentionally not exposed; TM-B lifted state replaces the old controls.
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [userLabelChoice, _setUserLabelChoice] = useState<string | null | '__default__'>('__default__');

  // Derive the effective label model from either prop (lifted state) or internal state.
  const selectedLabelModel: string | null = useMemo(() => {
    if (overlayPileLabelKey !== undefined) {
      // Controlled by parent: use the prop value directly.
      // Map null to null (None), any key to that key if still present, else first.
      if (overlayPileLabelKey === null) return null;
      if (centroidPiles && overlayPileLabelKey in centroidPiles) return overlayPileLabelKey;
      return pileModelKeys[0] ?? null;
    }
    // Uncontrolled (internal) path
    if (userLabelChoice === '__default__') {
      return pileModelKeys[0] ?? null;
    }
    if (userLabelChoice === null) return null;
    if (centroidPiles && userLabelChoice in centroidPiles) return userLabelChoice;
    return pileModelKeys[0] ?? null;
  }, [overlayPileLabelKey, userLabelChoice, pileModelKeys, centroidPiles]);

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
    // Quantize the measured box to 8px steps (2026-06-10 jitter fix): any
    // oscillation source that wobbles the container by a few real pixels
    // (footnote lines, scrollbars, fractional DPR rounding) now resolves to
    // the same bucket and produces a byte-identical layout, which the
    // equality guards then drop instead of re-rendering.
    const QUANT = 8;
    const W = Math.floor(Math.max(rect.width || 600, 600) / QUANT) * QUANT;
    // §17.1 defensive cap: H can never exceed the viewport even if CSS regresses.
    // This breaks the ResizeObserver loop at the source: if overflow leaks and the
    // container reports a height larger than the viewport, we clamp it here so the
    // SVG cannot grow the parent further.
    const H = Math.floor(Math.min(Math.max(rect.height || 400, 400), window.innerHeight) / QUANT) * QUANT;

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

    // ── Term-label layout: compass placement (8-direction penalty search) ────
    // Kept for term labels (small labels near dots).
    // Cluster labels now use placeLabels() from labelPlacement.ts (AC1, AC2).
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

      for (let kk = 0; kk < 8; kk++) {
        const dir = DIRECTIONS[kk];
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
        penalty += kk * 0.5;

        if (penalty < minPenalty) {
          minPenalty = penalty;
          bestDirIdx = kk;
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

    // ── Salience density gate (AC4, §3.1.1(c)) ────────────────────────────
    // Compute per-term salience visibility set: which terms are in the top 50%
    // by Sutrop CSI across all models (salience source: published sutrop_csi field).
    // A term is "top salience" if its max CSI across all selected models ranks it
    // in the top 50% of the union of all terms for that model.
    // Per CDA SME N2: salience source is Sutrop CSI, a published-finding measure.
    // Not recomputed client-side (Decision C binding).
    const topSalienceTerms = new Set<string>();
    if (salienceRanks) {
      const modelsToConsider = selectedModelIds && selectedModelIds.size > 0
        ? Array.from(selectedModelIds)
        : Object.keys(salienceRanks);
      for (const modelId of modelsToConsider) {
        const entries = salienceRanks[modelId];
        if (!entries || entries.length === 0) continue;
        const cutoff = Math.ceil(entries.length / 2); // top 50%
        for (let i = 0; i < cutoff; i++) {
          topSalienceTerms.add(entries[i].item);
        }
      }
    }
    // hasSalienceData derived from prop (also mirrored as component-level useMemo for JSX).
    const localHasSalienceData = !!salienceRanks && Object.keys(salienceRanks).length > 0;

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
      svgParts.push(`<line x1="${pad.l}" y1="${gy.toFixed(1)}" x2="${(pad.l + pw).toFixed(1)}" y2="${gy.toFixed(1)}" stroke="var(--color-svg-grid-line)" stroke-width=".5"/>`);
      svgParts.push(`<line x1="${gx.toFixed(1)}" y1="${pad.t}" x2="${gx.toFixed(1)}" y2="${(pad.t + ph).toFixed(1)}" stroke="var(--color-svg-grid-line)" stroke-width=".5"/>`);
    }

    const plotCx = pad.l + pw / 2;
    const plotCy = pad.t + ph / 2;

    // ── Cluster label rendering (TM-C: collision-aware via placeLabels) ──────
    // §3.1.1(c) binding: cluster labels must not overlap each other or occlude
    // term point markers. Minimum separation 16px. Fallback: footnote list.
    // Leader lines use var(--color-text-caption) per UI/UX token correction.
    // Cluster label font: var(--font-body) at var(--font-size-sm) = 14px,
    // color: var(--color-text-primary) per §3.1.1(c).
    // Decision D token pre-check (pitfall 15): all tokens confirmed present in tokens.css.
    const CLUSTER_LABEL_FONT_SIZE = 14; // --font-size-sm (confirmed in tokens.css)
    const CLUSTER_LABEL_HEIGHT = 16;    // slightly taller than font-size for bbox
    const LEADER_LINE_COLOR = 'var(--color-text-caption)'; // #6c757d ~4.60:1 (UI/UX WCAG fix)
    const CLUSTER_LABEL_COLOR = 'var(--color-text-primary)'; // #2c3e50 body text

    // Collect all term SVG positions for occlusion avoidance.
    const termPoints: [number, number][] = terms.map((t) => [sx(t.x), sy(t.y)]);

    // Chart bounds for placement module.
    const placementBounds = {
      x1: pad.l, y1: pad.t, x2: pad.l + pw, y2: pad.t + ph,
    };

    // Build label specs from group centroids (pushed outward from plot center).
    const clusterLabelSpecs: LabelSpec[] = [];
    const clusterLabelTextMap: Record<string, string> = {}; // key -> display text
    const newHiddenLabels: string[] = [];

    const buildClusterLabelSpecs = (
      labelGroups: Record<string, TermEntry[]>,
    ) => {
      // Process in stable key order for determinism (AC1).
      const sortedLabels = Object.keys(labelGroups).sort();
      for (const label of sortedLabels) {
        const groupTerms = labelGroups[label];
        if (groupTerms.length < 1) continue;

        const cx = groupTerms.reduce((s, t) => s + sx(t.x), 0) / groupTerms.length;
        const cy = groupTerms.reduce((s, t) => s + sy(t.y), 0) / groupTerms.length;

        // Initial anchor: term farthest from plot center, pushed outward.
        let anchorX = cx, anchorY = cy;
        if (groupTerms.length >= 2) {
          let maxDist = 0;
          groupTerms.forEach((t) => {
            const px = sx(t.x), py = sy(t.y);
            const d = Math.sqrt((px - plotCx) ** 2 + (py - plotCy) ** 2);
            if (d > maxDist) { maxDist = d; anchorX = px; anchorY = py; }
          });
          const ddx = anchorX - plotCx, ddy = anchorY - plotCy;
          const dd = Math.sqrt(ddx * ddx + ddy * ddy) || 1;
          anchorX += (ddx / dd) * 28;
          anchorY += (ddy / dd) * 14;
        }

        const estWidth = label.length * 7.5; // approximate at 14px font
        clusterLabelSpecs.push({
          key: label,
          anchorX,
          anchorY,
          width: estWidth,
          height: CLUSTER_LABEL_HEIGHT,
          avoidPoints: termPoints,
        });
        clusterLabelTextMap[label] = label;
      }
    };

    if (showClusterLabels && selectedLabelModel && centroidPiles && centroidPiles[selectedLabelModel]) {
      const modelPiles = centroidPiles[selectedLabelModel];
      const termToPileLabel: Record<string, string> = {};
      modelPiles.piles.forEach((pile, i) => {
        const label = modelPiles.labels[i] || `Pile ${i + 1}`;
        pile.forEach((term) => { termToPileLabel[term] = label; });
      });
      const labelGroups: Record<string, TermEntry[]> = {};
      terms.forEach((t) => {
        const label = termToPileLabel[t.term];
        if (label) {
          if (!labelGroups[label]) labelGroups[label] = [];
          labelGroups[label].push(t);
        }
      });
      buildClusterLabelSpecs(labelGroups);
    } else if (showClusterLabels && !centroidPiles && selectedLabelModel !== null) {
      // Fallback: no centroidPiles available — use aggregate clusterLabels
      const labelGroups: Record<string, TermEntry[]> = {};
      Object.entries(clusters).forEach(([cidStr, clusterTerms]) => {
        const cid = parseInt(cidStr, 10);
        const label = clusterLabels[cid] || `Cluster ${cid + 1}`;
        if (!labelGroups[label]) labelGroups[label] = [];
        labelGroups[label].push(...clusterTerms);
      });
      buildClusterLabelSpecs(labelGroups);
    }

    // Run collision-aware placement (AC2: min 16px separation, point occlusion avoided).
    if (clusterLabelSpecs.length > 0) {
      const { placed, hidden } = placeLabels(clusterLabelSpecs, placementBounds);

      // Render placed cluster labels.
      for (const p of placed) {
        const labelText = clusterLabelTextMap[p.key] ?? p.key;
        // Center X of box for text-anchor="middle".
        const textX = (p.x + p.width / 2).toFixed(1);
        // Baseline: approximately 12px above bottom of bbox.
        const textY = (p.y + CLUSTER_LABEL_HEIGHT - 3).toFixed(1);

        // Leader line: drawn when label was displaced significantly from anchor.
        if (p.hasLeaderLine) {
          svgParts.push(
            `<line x1="${p.leaderFromX.toFixed(1)}" y1="${p.leaderFromY.toFixed(1)}" x2="${p.leaderToX.toFixed(1)}" y2="${p.leaderToY.toFixed(1)}" stroke="${LEADER_LINE_COLOR}" stroke-width="1" pointer-events="none"/>`
          );
        }

        svgParts.push(
          `<text x="${textX}" y="${textY}" text-anchor="middle" font-family="var(--font-body)" font-size="${CLUSTER_LABEL_FONT_SIZE}" font-weight="600" fill="${CLUSTER_LABEL_COLOR}" opacity="1" pointer-events="none">${escapeXml(labelText)}</text>`
        );
      }

      // Collect hidden labels for footnote list (UI/UX D1 binding: greedy + footnote fallback).
      for (const h of hidden) {
        newHiddenLabels.push(clusterLabelTextMap[h.key] ?? h.key);
      }
    }

    // Update hidden labels state (deferred to after render() completes via setSvgContent).
    // We use a local variable and call setHiddenClusterLabels at the end of render().
    // (Stored in a local and set after setSvgContent to batch the React state update.)

    // ── Ellipses rendering ──────────────────────────────────────────────────
    // R1-a degenerate sub-state (semi_major <= 0 but u present): bootstrap converged on near-point.
    // Per DESIGN_SYSTEM.md §3.3.5 impl req 12: render minimum-radius ellipse floor (3px).
    // Disclosure (S3) threads through .term-dot aria-label below, NOT .term-ellipse (pointer-events=none).
    if (showUncertainty && termUncertainty) {
      terms.forEach((t, i) => {
        const u = termUncertainty[t.term];
        if (!u) return;
        const cx = sx(t.x);
        const cy = sy(t.y);
        const isDegenerate = u.semi_major <= 0;
        const rx = isDegenerate ? 3 : (u.semi_major / (xMax - xMin)) * pw;
        const ry = isDegenerate ? 3 : (u.semi_minor / (yMax - yMin)) * ph;
        const deg = -(u.rotation_rad * 180) / Math.PI;
        const col = getClusterColor(t.cluster);
        if (isDegenerate) {
          svgParts.push(
            `<ellipse class="term-ellipse" cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" rx="${rx.toFixed(1)}" ry="${ry.toFixed(1)}" transform="rotate(${deg.toFixed(1)},${cx.toFixed(1)},${cy.toFixed(1)})" fill="${col}" stroke="${col}" fill-opacity="0.08" stroke-opacity="0.25" stroke-width="1" data-idx="${i}" data-ox="${cx.toFixed(1)}" data-oy="${cy.toFixed(1)}" data-deg="${deg.toFixed(1)}" data-degenerate-bootstrap="true" pointer-events="none"/>`
          );
        } else {
          svgParts.push(
            `<ellipse class="term-ellipse" cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" rx="${rx.toFixed(1)}" ry="${ry.toFixed(1)}" transform="rotate(${deg.toFixed(1)},${cx.toFixed(1)},${cy.toFixed(1)})" fill="${col}" stroke="${col}" fill-opacity="0.08" stroke-opacity="0.25" stroke-width="1" data-idx="${i}" data-ox="${cx.toFixed(1)}" data-oy="${cy.toFixed(1)}" data-deg="${deg.toFixed(1)}" pointer-events="none"/>`
          );
        }
      });
    }

    // Term dots: store original coords as data attributes for hover animation.
    // R1-a degenerate sub-state (semi_major <= 0): add aria-label (S3) per §3.3.5 impl req 12.
    // Disclosure threads through .term-dot (pointer-events enabled), NOT .term-ellipse (none).
    terms.forEach((t, i) => {
      const px = sx(t.x).toFixed(1);
      const py = sy(t.y).toFixed(1);
      const col = getClusterColor(t.cluster);
      const uDot = termUncertainty ? termUncertainty[t.term] : null;
      const isDegenerateDot = uDot != null && uDot.semi_major <= 0;
      if (isDegenerateDot) {
        svgParts.push(
          `<circle class="term-dot" cx="${px}" cy="${py}" r="4" fill="${col}" stroke="var(--color-svg-dot-stroke)" stroke-width=".8" data-cluster="${t.cluster}" data-idx="${i}" data-ox="${px}" data-oy="${py}" data-degenerate-bootstrap="true" aria-label="${escapeXml(t.term)}, high positional stability across bootstrap resamples." cursor="pointer"/>`
        );
      } else {
        svgParts.push(
          `<circle class="term-dot" cx="${px}" cy="${py}" r="4" fill="${col}" stroke="var(--color-svg-dot-stroke)" stroke-width=".8" data-cluster="${t.cluster}" data-idx="${i}" data-ox="${px}" data-oy="${py}" cursor="pointer"/>`
        );
      }
    });

    // Term labels: visible, small, positioned using computed layout offsets.
    // data-salience: "top" or "low" for the zoom-dependent density gate (AC4).
    // At k=1 initial render, "low" labels are hidden via JS after DOM commit.
    // At k>1.5 (zoom effect), "low" labels are made visible imperatively.
    terms.forEach((t, i) => {
      const layout = labelLayouts[i];
      const px = layout.x.toFixed(1);
      const py = layout.y.toFixed(1);
      const col = getClusterColor(t.cluster);
      // Salience gate: top-salience if no salience data or if term is in topSalienceTerms.
      const isTopSalience = !localHasSalienceData || topSalienceTerms.has(t.term);
      const salienceAttr = isTopSalience ? 'top' : 'low';
      svgParts.push(
        `<text class="term-label" x="${px}" y="${py}" data-ox="${px}" data-oy="${py}" data-base-size="11" data-salience="${salienceAttr}" font-family="var(--font-body)" font-size="11" fill="${col}" opacity=".7" text-anchor="${layout.anchor}" pointer-events="none">${escapeXml(t.term)}</text>`
      );
    });

    // Footer annotation
    const nTerms = terms.length;
    const nClusters = Object.keys(clusters).length;
    const modelNote = liveCoords && selectedModelIds
      ? `${selectedModelIds.size} model${selectedModelIds.size !== 1 ? 's' : ''} · `
      : '';
    svgParts.push(
      `<text x="${(pad.l + pw / 2).toFixed(1)}" y="${H - 14}" text-anchor="middle" font-family="var(--font-body)" font-size="10" fill="var(--color-svg-axis-caption)">${modelNote}${nTerms} shared terms · ${nClusters} clusters from pile-sort co-occurrence</text>`
    );

    // svgParts is the INNER content of <g id="term-content"> only.
    // The outer <svg> and <g> are rendered as real React elements in JSX.
    setSvgContent(svgParts.join(''));
    // Update base dimensions → drives SVG width/height in JSX (W×k, H×k).
    // Also reset zoom display to 1 since render() always produces a k=1 layout.
    setSvgBaseDims({ w: W, h: H });
    setZoomDisplay(1);
    // Update hidden cluster labels for the footnote list. Equality-guarded
    // (2026-06-10 jitter fix): an unconditional set with a fresh array forced a
    // re-render every pass, which fed the footnote-height feedback loop.
    setHiddenClusterLabels((prev) =>
      prev.length === newHiddenLabels.length && prev.every((v, i) => v === newHiddenLabels[i])
        ? prev
        : newHiddenLabels
    );
  }, [terms, clusterLabels, centroidPiles, selectedLabelModel, liveCoords, selectedModelIds, showUncertainty, showClusterLabels, termUncertainty, salienceRanks]);

  // Re-render on resize or term/coord change.
  // Delta guard (2026-06-10 live jitter fix): render() rebuilds the SVG, which
  // can change the observed box by sub-pixel amounts or toggle a classic
  // scrollbar (Windows), re-firing the observer in a visible refresh loop.
  // Only re-render when the box actually changed by >= 1 CSS px.
  useEffect(() => {
    render();
    let lastW = -1;
    let lastH = -1;
    const observer = new ResizeObserver((entries) => {
      const box = entries[entries.length - 1]?.contentRect;
      if (!box) return;
      if (Math.abs(box.width - lastW) < 1 && Math.abs(box.height - lastH) < 1) return;
      lastW = box.width;
      lastH = box.height;
      render();
    });
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

  // ── AC4: Initial low-salience label hide at k=1 ──────────────────────────
  // After SVG content is committed to DOM, hide "low" salience labels.
  // This runs once per render() cycle (svgContent change).
  // The zoom density effect below re-evaluates when zoomDisplay changes.
  // FREEZE RULE compliance: render() is not called; this effect mutates label
  // visibility imperatively matching the lens/hover pattern already in use.
  useLayoutEffect(() => {
    const panVp = panVpRef.current;
    if (!panVp) return;
    const svg = panVp.querySelector<SVGSVGElement>('#term-svg');
    if (!svg) return;
    // At k=1 (initial render), hide low-salience labels.
    svg.querySelectorAll<SVGTextElement>('.term-label[data-salience="low"]').forEach((lbl) => {
      lbl.setAttribute('opacity', '0');
      lbl.setAttribute('pointer-events', 'none');
      lbl.style.display = 'none';
    });
  }, [svgContent]);

  // ── AC4: Zoom-dependent term-label density effect ─────────────────────────
  // Re-evaluates on every zoomDisplay change.
  // k=1: top-salience only (low hidden).
  // k in (1, 1.5): linear step; show labels proportionally (see below).
  // k >= 1.5: all labels shown.
  // FREEZE RULE: no render() call. Only imperative DOM mutations.
  useEffect(() => {
    const panVp = panVpRef.current;
    if (!panVp) return;
    const svg = panVp.querySelector<SVGSVGElement>('#term-svg');
    if (!svg) return;

    const k = zoomDisplay;
    const showAll = k >= 1.5;
    const showNone = k <= 1.0;

    svg.querySelectorAll<SVGTextElement>('.term-label').forEach((lbl) => {
      const salience = lbl.getAttribute('data-salience');
      if (salience === 'top') {
        // Top-salience labels always shown.
        lbl.setAttribute('opacity', '0.7');
        lbl.removeAttribute('style');
      } else {
        // Low-salience labels: hidden at k=1, shown at k>=1.5, linear step between.
        if (showAll) {
          lbl.setAttribute('opacity', '0.7');
          lbl.removeAttribute('style');
        } else if (showNone) {
          lbl.setAttribute('opacity', '0');
          lbl.style.display = 'none';
        } else {
          // Linear step: opacity from 0 at k=1 to 0.7 at k=1.5.
          const t = (k - 1.0) / (1.5 - 1.0);
          const op = (t * 0.7).toFixed(2);
          lbl.setAttribute('opacity', op);
          lbl.style.display = '';
        }
      }
    });
  }, [zoomDisplay]);

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

  // Notify parent when lens-disabled-by-zoom state changes so ChartToolbar
  // can reflect the disabled state in the lifted control.
  useEffect(() => {
    onLensDisabledByZoomChange?.(lensDisabledByZoom);
  }, [lensDisabledByZoom, onLensDisabledByZoomChange]);

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
      {/* chart-wrap: outer border container — ResizeObserver target.
          Note: the term-map-controls bar was removed (TM-B). The four controls
          (overlay selector, uncertainty, cluster labels, lens) are now in
          ChartToolbar rendered by ContentArea above the chart-area. Zoom buttons
          remain in the term-map-stress footer below.
          Controls bar: OUTSIDE the pan-viewport so it stays fixed when scrolling (DOM order, §17.4).
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

      {/* CDA SME N1 (BINDING): top-salience caption at k=1, hidden at k>=1.5 (AC4).
          Literal substring 'top-salience' required in render path.
          Passes AC13 forbidden-vocab grep: no §1.5.4 prohibited terms. */}
      {hasSalienceData && zoomDisplay <= 1.5 && (
        <p
          className="term-map-salience-caption"
          aria-live="polite"
          style={{
            fontSize: 'var(--font-size-xs)',
            color: 'var(--color-text-caption)',
            margin: '2px 0 0 0',
            padding: '0',
            lineHeight: '1.4',
          }}
        >
          Labels shown for top-salience terms at this zoom level. Zoom in or hover with the magnifying lens to see all terms.
        </p>
      )}

      {/* Footnote list for hidden cluster labels (UI/UX D1 binding: greedy + footnote fallback).
          Renders below chart when one or more cluster labels could not be placed on map.
          2026-06-10 jitter fix: the band is height-CONSTANT (fixed height + internal
          scroll) so item-count changes can never resize .chart-wrap and re-fire the
          ResizeObserver. Item count feeding back into chart height was the live
          oscillation Mark reported (footnote list cycling, chart re-rendering). */}
      {showClusterLabels && (
        <ol
          className="term-map-cluster-footnotes"
          aria-label="Cluster labels not shown on map due to space constraints."
        >
          {hiddenClusterLabels.length > 0 ? (
            hiddenClusterLabels.map((label) => <li key={label}>{label}</li>)
          ) : (
            <li className="term-map-cluster-footnotes__empty">
              All cluster labels are shown on the map.
            </li>
          )}
        </ol>
      )}

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
