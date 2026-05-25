// @vitest-environment jsdom
/**
 * TermMDSPlot — term-level MDS scatter plot.
 *
 * Phase 9a T6. Implements the UI/UX visual specification from
 * docs/status/2026-05-24-phase9a-T6T7-ui-ux-verdict.md.
 *
 * What is displayed:
 *   - One point per domain term, colored by cluster via --color-cluster-N tokens.
 *   - Greedy 8-compass label placement with collision avoidance.
 *   - Hover/focus confidence ellipses (R10); "Show uncertainty" toggle shows all.
 *   - Cluster region labels (large 24px bold at 20% opacity at cluster centroid).
 *   - Grid lines, axis labels ("MDS Dimension 1 — relative" / "MDS Dimension 2 — relative").
 *   - Dark inverted tooltip with: term name, cluster label, 95% CI details, M4a note.
 *   - Stress value in caption below chart.
 *
 * R10 compliance (CLAUDE.md §6 R10 / ARCHITECTURE.md §4.5):
 *   Ellipses are hover/focus by default. "Show uncertainty" toggle shows all.
 *   No bare numeric finding without its CI range in the tooltip.
 *
 * SVG width: 600px (matches MDSPlot). Height: auto-computed from data range + margins.
 * Mobile (<768px): text labels hidden, cluster region labels hidden, toggles hidden.
 *   SVG scales via viewBox.
 *
 * T8 pattern: ReadAsTableToggle + TermMDSTable + ScreenReaderSummary.
 *   readAsTable state: local useState (per-viz, no DataExplorer state pollution).
 *   U1 (BINDING): table container div always in DOM; aria-hidden + display:none when inactive.
 *
 * Cluster colors: --color-cluster-1 through --color-cluster-8 (tokens.css §1.2).
 *   Clusters > 8 fall back to --color-text-secondary.
 *
 * Forbidden vocabulary: no "worldview", "believes", "thinks" (model-applied),
 *   "competence", "correctness", per CLAUDE.md §7 and ARCHITECTURE.md §1.5.4.
 *
 * Reference:
 *   docs/status/2026-05-24-phase9a-viz-gap-kickoff.md T6
 *   docs/status/2026-05-24-phase9a-T6T7-ui-ux-verdict.md
 *   DESIGN_SYSTEM.md v0.5.2 §11
 */

import { useState, useMemo, useCallback } from "react";
import type { DomainResultPublished } from "../data/types";
import { ScreenReaderSummary } from "./ScreenReaderSummary";
import { ReadAsTableToggle } from "./ReadAsTableToggle";
import { TermMDSTable } from "./TermMDSTable";
import {
  READ_AS_TABLE_LABEL_REST,
  READ_AS_TABLE_LABEL_PRESSED,
  termMdsScreenReaderSummary,
} from "../copy/screen_reader_summaries";
import "../styles/term-mds-plot.css";

// ── Props ───────────────────────────────────────────────────────────────────

export interface TermMDSPlotProps {
  domainResult: DomainResultPublished;
}

// ── Internal types ──────────────────────────────────────────────────────────

interface UncertaintyParams {
  center: [number, number];
  semi_major: number;
  semi_minor: number;
  rotation_rad: number;
  n_bootstrap: number;
}

interface TermPoint {
  term: string;
  x: number;
  y: number;
  clusterId: number;
  clusterLabel: string;
  color: string;
  uncertainty: UncertaintyParams | null;
}

interface LabelPlacement {
  term: string;
  lx: number;
  ly: number;
  width: number;
  height: number;
}

interface TooltipState {
  term: string;
  screenX: number;
  screenY: number;
}

// ── Plot constants ───────────────────────────────────────────────────────────

const SVG_WIDTH = 600;
const MARGIN = { top: 32, right: 40, bottom: 60, left: 60 };
const POINT_RADIUS = 4;
const GRID_LINE_COUNT = 5;

// Label font size (px) — used for text + estimated bounding box
const LABEL_FONT_SIZE = 12;
// Estimated char width for collision avoidance (§ spec: label.length * 6)
const LABEL_CHAR_WIDTH = 6;
const LABEL_HEIGHT = LABEL_FONT_SIZE + 2;
// Padding between point edge and label start
const LABEL_PAD = 4;

// Cluster region label specs
const CLUSTER_LABEL_FONT_SIZE = 24;
const CLUSTER_LABEL_OPACITY = 0.20;

// Cluster color hex values, matching tokens.css §1.2 --color-cluster-1..8
const CLUSTER_COLORS: string[] = [
  "#e05c2e", // cluster 1
  "#2e7d4f", // cluster 2
  "#b5590a", // cluster 3
  "#5c3298", // cluster 4
  "#1d6b8f", // cluster 5
  "#8f1d55", // cluster 6
  "#4a6e1a", // cluster 7
  "#6b3a1f", // cluster 8
];

// Fallback for clusters > 8
const CLUSTER_COLOR_FALLBACK = "var(--color-text-secondary)";

// ── Tooltip note (CDA SME M4a binding verbatim) ──────────────────────────────

const UNCERTAINTY_NOTE =
  "Uncertainty reflects agreement across models, not within-model sampling variance.";

// ── Color helpers ────────────────────────────────────────────────────────────

function clusterColor(clusterId: number): string {
  // clusterId is 0-based or 1-based; normalize to 0-based index
  const idx = Math.max(0, clusterId - 1);
  if (idx < CLUSTER_COLORS.length) {
    return CLUSTER_COLORS[idx];
  }
  return CLUSTER_COLOR_FALLBACK;
}

/**
 * Returns rgba() from a hex color and alpha. Falls back to hex on parse error.
 */
function hexToRgba(hex: string, alpha: number): string {
  if (!hex.startsWith("#")) return hex; // CSS variable — can't parse
  const clean = hex.replace("#", "");
  if (clean.length !== 6) return hex;
  const r = parseInt(clean.substring(0, 2), 16);
  const g = parseInt(clean.substring(2, 4), 16);
  const b = parseInt(clean.substring(4, 6), 16);
  if (isNaN(r) || isNaN(g) || isNaN(b)) return hex;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

// ── Scale builder ────────────────────────────────────────────────────────────

function buildScales(
  coords: Record<string, [number, number]>
): {
  toSvgX: (v: number) => number;
  toSvgY: (v: number) => number;
  plotH: number;
  svgHeight: number;
  domainMinX: number;
  domainMaxX: number;
  domainMinY: number;
  domainMaxY: number;
} {
  const xs = Object.values(coords).map((c) => c[0]);
  const ys = Object.values(coords).map((c) => c[1]);

  if (xs.length === 0) {
    // No data — return minimal scaffold
    const plotH = 200;
    const svgHeight = plotH + MARGIN.top + MARGIN.bottom;
    return {
      toSvgX: () => MARGIN.left,
      toSvgY: () => MARGIN.top,
      plotH,
      svgHeight,
      domainMinX: -1,
      domainMaxX: 1,
      domainMinY: -1,
      domainMaxY: 1,
    };
  }

  const rawMinX = Math.min(...xs);
  const rawMaxX = Math.max(...xs);
  const rawMinY = Math.min(...ys);
  const rawMaxY = Math.max(...ys);

  const padX = (rawMaxX - rawMinX) * 0.2 + 0.01;
  const padY = (rawMaxY - rawMinY) * 0.2 + 0.01;

  const domainMinX = rawMinX - padX;
  const domainMaxX = rawMaxX + padX;
  const domainMinY = rawMinY - padY;
  const domainMaxY = rawMaxY + padY;

  const plotW = SVG_WIDTH - MARGIN.left - MARGIN.right;

  // Auto-compute height to preserve aspect ratio while keeping a reasonable size
  const dataRangeX = domainMaxX - domainMinX;
  const dataRangeY = domainMaxY - domainMinY;
  const naturalH = plotW * (dataRangeY / dataRangeX);
  const plotH = Math.max(200, Math.min(500, naturalH));
  const svgHeight = plotH + MARGIN.top + MARGIN.bottom;

  const toSvgX = (v: number): number =>
    MARGIN.left + ((v - domainMinX) / (domainMaxX - domainMinX)) * plotW;

  const toSvgY = (v: number): number =>
    MARGIN.top + ((domainMaxY - v) / (domainMaxY - domainMinY)) * plotH;

  return {
    toSvgX,
    toSvgY,
    plotH,
    svgHeight,
    domainMinX,
    domainMaxX,
    domainMinY,
    domainMaxY,
  };
}

// ── Ellipse path ─────────────────────────────────────────────────────────────

/**
 * Returns SVG path `d` attribute for a rotated ellipse centered at (cx, cy).
 * Uses four cubic Bezier curves (κ = 0.5522847).
 */
function ellipsePathD(
  cx: number,
  cy: number,
  a: number,
  b: number,
  angle: number
): string {
  const K = 0.5522847498;
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);

  function pt(lx: number, ly: number): [number, number] {
    return [cx + cos * lx - sin * ly, cy + sin * lx + cos * ly];
  }

  const [x0, y0] = pt(a, 0);
  const [x1, y1] = pt(0, -b);
  const [x2, y2] = pt(-a, 0);
  const [x3, y3] = pt(0, b);

  const [cpx0, cpy0] = pt(a, -K * b);
  const [cpx1, cpy1] = pt(K * a, -b);
  const [cpx2, cpy2] = pt(-K * a, -b);
  const [cpx3, cpy3] = pt(-a, -K * b);
  const [cpx4, cpy4] = pt(-a, K * b);
  const [cpx5, cpy5] = pt(-K * a, b);
  const [cpx6, cpy6] = pt(K * a, b);
  const [cpx7, cpy7] = pt(a, K * b);

  const fmt = (n: number) => n.toFixed(3);

  return [
    `M ${fmt(x0)} ${fmt(y0)}`,
    `C ${fmt(cpx0)} ${fmt(cpy0)}, ${fmt(cpx1)} ${fmt(cpy1)}, ${fmt(x1)} ${fmt(y1)}`,
    `C ${fmt(cpx2)} ${fmt(cpy2)}, ${fmt(cpx3)} ${fmt(cpy3)}, ${fmt(x2)} ${fmt(y2)}`,
    `C ${fmt(cpx4)} ${fmt(cpy4)}, ${fmt(cpx5)} ${fmt(cpy5)}, ${fmt(x3)} ${fmt(y3)}`,
    `C ${fmt(cpx6)} ${fmt(cpy6)}, ${fmt(cpx7)} ${fmt(cpy7)}, ${fmt(x0)} ${fmt(y0)}`,
    "Z",
  ].join(" ");
}

// ── Greedy 8-compass label placement ────────────────────────────────────────

/**
 * 8 compass directions in preference order:
 *   0=right, 1=upper-right, 2=upper, 3=upper-left, 4=left,
 *   5=lower-left, 6=lower, 7=lower-right
 * Handled inline in the switch statement inside computeLabelPlacements.
 */

/**
 * Returns true if two axis-aligned bounding boxes overlap.
 */
function boxesOverlap(
  ax: number, ay: number, aw: number, ah: number,
  bx: number, by: number, bw: number, bh: number
): boolean {
  return !(ax + aw < bx || bx + bw < ax || ay + ah < by || by + bh < ay);
}

/**
 * Greedy label placement algorithm.
 * For each point, tries 8 compass positions in preference order.
 * Accepts the first collision-free position; falls back to least-overlapping.
 * Returns array of placed label positions.
 */
function computeLabelPlacements(
  points: TermPoint[]
): LabelPlacement[] {
  const placed: LabelPlacement[] = [];
  const pointBoxes: Array<{ x: number; y: number }> = points.map((p) => ({
    x: p.x - POINT_RADIUS,
    y: p.y - POINT_RADIUS,
  }));

  for (let pi = 0; pi < points.length; pi++) {
    const p = points[pi];
    const w = p.term.length * LABEL_CHAR_WIDTH;
    const h = LABEL_HEIGHT;

    let bestPlacement: LabelPlacement | null = null;
    let bestOverlapCount = Infinity;

    for (let ci = 0; ci < 8; ci++) {
      let tx: number;
      let ty: number;
      let anchor: "start" | "middle" | "end" = "start";

      // Compute candidate position based on compass direction
      switch (ci) {
        case 0: // right
          tx = p.x + POINT_RADIUS + LABEL_PAD;
          ty = p.y + 4;
          anchor = "start";
          break;
        case 1: // upper-right
          tx = p.x + POINT_RADIUS + LABEL_PAD;
          ty = p.y - 6;
          anchor = "start";
          break;
        case 2: // upper
          tx = p.x;
          ty = p.y - (POINT_RADIUS + LABEL_PAD + 2);
          anchor = "middle";
          break;
        case 3: // upper-left
          tx = p.x - (POINT_RADIUS + LABEL_PAD);
          ty = p.y - 6;
          anchor = "end";
          break;
        case 4: // left
          tx = p.x - (POINT_RADIUS + LABEL_PAD);
          ty = p.y + 4;
          anchor = "end";
          break;
        case 5: // lower-left
          tx = p.x - (POINT_RADIUS + LABEL_PAD);
          ty = p.y + POINT_RADIUS + LABEL_PAD + 2;
          anchor = "end";
          break;
        case 6: // lower
          tx = p.x;
          ty = p.y + POINT_RADIUS + LABEL_PAD + 2;
          anchor = "middle";
          break;
        case 7: // lower-right
          tx = p.x + POINT_RADIUS + LABEL_PAD;
          ty = p.y + POINT_RADIUS + LABEL_PAD + 2;
          anchor = "start";
          break;
        default:
          tx = p.x + POINT_RADIUS + LABEL_PAD;
          ty = p.y + 4;
          anchor = "start";
      }

      // Compute bounding box for this candidate label position
      let bx: number;
      const by = ty - LABEL_HEIGHT;
      if (anchor === "start") {
        bx = tx;
      } else if (anchor === "end") {
        bx = tx - w;
      } else {
        bx = tx - w / 2;
      }

      // Count overlaps with already-placed labels and point centers
      let overlapCount = 0;
      for (const prev of placed) {
        if (boxesOverlap(bx, by, w, h, prev.lx, prev.ly - LABEL_HEIGHT, prev.width, LABEL_HEIGHT)) {
          overlapCount++;
        }
      }
      // Also penalize overlap with other point circles
      for (let qi = 0; qi < points.length; qi++) {
        if (qi === pi) continue;
        const pb = pointBoxes[qi];
        if (boxesOverlap(bx, by, w, h, pb.x, pb.y, POINT_RADIUS * 2, POINT_RADIUS * 2)) {
          overlapCount++;
        }
      }

      if (overlapCount < bestOverlapCount) {
        bestOverlapCount = overlapCount;
        bestPlacement = {
          term: p.term,
          lx: anchor === "start" ? bx : anchor === "end" ? bx : bx,
          ly: ty,
          width: w,
          height: h,
        };
      }

      if (overlapCount === 0) break; // Found collision-free position
    }

    if (bestPlacement !== null) {
      placed.push(bestPlacement);
    }
  }

  return placed;
}

// ── Table container id ───────────────────────────────────────────────────────

const TERM_MDS_TABLE_CONTAINER_ID = "term-mds-table-container";

// ── Main component ────────────────────────────────────────────────────────────

export function TermMDSPlot({ domainResult }: TermMDSPlotProps) {
  const [showUncertainty, setShowUncertainty] = useState(false);
  const [showClusterLabels, setShowClusterLabels] = useState(true);
  const [showTermLabels, setShowTermLabels] = useState(false);
  const [hoveredTerm, setHoveredTerm] = useState<string | null>(null);
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);
  const [readAsTable, setReadAsTable] = useState(false);

  // Cast term_mds_coordinates from domain JSON (not in types.ts — cast-through-unknown)
  const rawCoords = useMemo(
    () =>
      (domainResult as unknown as { term_mds_coordinates?: Record<string, [number, number]> })
        .term_mds_coordinates ?? {},
    [domainResult]
  );

  const rawUncertainty = useMemo(
    () =>
      (domainResult as unknown as { term_mds_uncertainty?: Record<string, UncertaintyParams> })
        .term_mds_uncertainty ?? {},
    [domainResult]
  );

  const rawClusterAssignments = useMemo(
    () =>
      (domainResult as unknown as { term_cluster_assignments?: Record<string, number> })
        .term_cluster_assignments ?? {},
    [domainResult]
  );

  const rawClusterLabels = useMemo(
    () =>
      (domainResult as unknown as { term_cluster_labels?: string[] })
        .term_cluster_labels ?? [],
    [domainResult]
  );

  // Stress value if present
  const stressValue = useMemo(
    () =>
      (domainResult as unknown as { term_mds_stress?: number })
        .term_mds_stress,
    [domainResult]
  );

  const hasData = Object.keys(rawCoords).length > 0;

  // Build scale helpers
  const { toSvgX, toSvgY, plotH, svgHeight, domainMinX, domainMaxX, domainMinY, domainMaxY } =
    useMemo(() => buildScales(rawCoords), [rawCoords]);

  const plotW = SVG_WIDTH - MARGIN.left - MARGIN.right;

  // Scale factor for ellipse axes (data units → SVG pixels)
  const dataRangeX = domainMaxX - domainMinX;
  const svgUnitsPerDataUnit = plotW / (dataRangeX || 1);

  // Build term point descriptors
  const points: TermPoint[] = useMemo(() => {
    return Object.entries(rawCoords).map(([term, [dx, dy]]) => {
      const clusterId = rawClusterAssignments[term] ?? 1;
      const clusterIndex = clusterId - 1; // convert 1-based to 0-based
      const clusterLabel = rawClusterLabels[clusterIndex] ?? `Cluster ${clusterId}`;
      const color = clusterColor(clusterId);
      const uncertainty = rawUncertainty[term] ?? null;
      return {
        term,
        x: toSvgX(dx),
        y: toSvgY(dy),
        clusterId,
        clusterLabel,
        color,
        uncertainty,
      };
    });
  }, [rawCoords, rawClusterAssignments, rawClusterLabels, rawUncertainty, toSvgX, toSvgY]);

  // Compute cluster centroids (for cluster region labels)
  const clusterCentroids = useMemo(() => {
    const groups: Record<number, { xs: number[]; ys: number[]; label: string }> = {};
    for (const p of points) {
      if (!groups[p.clusterId]) {
        groups[p.clusterId] = { xs: [], ys: [], label: p.clusterLabel };
      }
      groups[p.clusterId].xs.push(p.x);
      groups[p.clusterId].ys.push(p.y);
    }
    return Object.entries(groups).map(([id, g]) => ({
      clusterId: Number(id),
      cx: g.xs.reduce((a, b) => a + b, 0) / g.xs.length,
      cy: g.ys.reduce((a, b) => a + b, 0) / g.ys.length,
      label: g.label,
      color: clusterColor(Number(id)),
    }));
  }, [points]);

  // Grid line values
  const gridXValues = useMemo(() => {
    const step = (domainMaxX - domainMinX) / (GRID_LINE_COUNT + 1);
    return Array.from({ length: GRID_LINE_COUNT }, (_, i) => domainMinX + step * (i + 1));
  }, [domainMinX, domainMaxX]);

  const gridYValues = useMemo(() => {
    const step = (domainMaxY - domainMinY) / (GRID_LINE_COUNT + 1);
    return Array.from({ length: GRID_LINE_COUNT }, (_, i) => domainMinY + step * (i + 1));
  }, [domainMinY, domainMaxY]);

  // Greedy label placements (computed once, not per render)
  const labelPlacements = useMemo(
    () => computeLabelPlacements(points),
    [points]
  );

  // Build a map from term → label placement for fast lookup
  const labelPlacementMap = useMemo(() => {
    const m = new Map<string, LabelPlacement>();
    for (const lp of labelPlacements) {
      m.set(lp.term, lp);
    }
    return m;
  }, [labelPlacements]);

  // Tooltip handlers
  const handleMouseEnter = useCallback(
    (term: string, e: React.MouseEvent<SVGElement>) => {
      setHoveredTerm(term);
      const rect = (e.currentTarget.ownerSVGElement ?? e.currentTarget).getBoundingClientRect();
      setTooltip({ term, screenX: e.clientX - rect.left, screenY: e.clientY - rect.top });
    },
    []
  );

  const handleMouseLeave = useCallback(() => {
    setHoveredTerm(null);
    setTooltip(null);
  }, []);

  const handleMouseMove = useCallback(
    (term: string, e: React.MouseEvent<SVGElement>) => {
      const rect = (e.currentTarget.ownerSVGElement ?? e.currentTarget).getBoundingClientRect();
      setTooltip({ term, screenX: e.clientX - rect.left, screenY: e.clientY - rect.top });
    },
    []
  );

  // Aria label for SVG container
  const nTerms = points.length;
  const nClusters = clusterCentroids.length;
  const ariaLabel = hasData
    ? `Term map scatter plot of ${nTerms} terms in ${nClusters} clusters on the ${domainResult.domain_slug} domain. Points show individual terms colored by cluster; proximity means models consistently grouped these terms together.`
    : `Term map for the ${domainResult.domain_slug} domain. No term MDS data available.`;

  // SR summary text
  const srSummaryText = termMdsScreenReaderSummary(
    domainResult.domain_slug,
    nTerms,
    nClusters
  );

  // Description paragraph text (spec binding)
  const descriptionText = `Where ${domainResult.domain_slug} terms cluster in model output space: points show individual terms, colored by cluster. Proximity means models consistently grouped these terms together. Hover any term to see its uncertainty range.`;

  // Cluster legend removed — cluster region labels on chart serve this purpose.

  if (!hasData) {
    return (
      <div className="term-mds-plot">
        <ScreenReaderSummary text={srSummaryText} />
        <p className="term-mds-plot__empty">
          Term MDS data is not available for this domain.
        </p>
      </div>
    );
  }

  const hoveredPoint = hoveredTerm ? points.find((p) => p.term === hoveredTerm) ?? null : null;

  return (
    <div className="term-mds-plot">
      {/* ScreenReaderSummary — always present in both viz and table modes */}
      <ScreenReaderSummary text={srSummaryText} />

      {/* Description paragraph */}
      {!readAsTable && (
        <p className="term-mds-plot__description">{descriptionText}</p>
      )}

      {/* Controls row — hidden on mobile per spec */}
      {!readAsTable && (
        <div className="term-mds-plot__controls">
          <label className="term-mds-plot__toggle-label">
            <input
              type="checkbox"
              checked={showUncertainty}
              onChange={(e) => setShowUncertainty(e.target.checked)}
            />
            Show uncertainty
          </label>
          <label className="term-mds-plot__toggle-label">
            <input
              type="checkbox"
              checked={showClusterLabels}
              onChange={(e) => setShowClusterLabels(e.target.checked)}
            />
            Show cluster labels
          </label>
          <label className="term-mds-plot__toggle-label">
            <input
              type="checkbox"
              checked={showTermLabels}
              onChange={(e) => setShowTermLabels(e.target.checked)}
            />
            Show term labels
          </label>
        </div>
      )}

      {/* ReadAsTableToggle */}
      <ReadAsTableToggle
        pressed={readAsTable}
        onToggle={() => setReadAsTable((v) => !v)}
        tableContainerId={TERM_MDS_TABLE_CONTAINER_ID}
        labels={{ rest: READ_AS_TABLE_LABEL_REST, pressed: READ_AS_TABLE_LABEL_PRESSED }}
      />

      {/* SVG visualization */}
      <div className="term-mds-plot__svg-container">
        <svg
          className="term-mds-plot__svg"
          width={SVG_WIDTH}
          height={svgHeight}
          viewBox={`0 0 ${SVG_WIDTH} ${svgHeight}`}
          role="img"
          aria-label={ariaLabel}
          aria-hidden={readAsTable || undefined}
          style={{ overflow: "visible", display: readAsTable ? "none" : undefined }}
        >
          {/* ── Plot frame ── */}
          <rect
            x={MARGIN.left}
            y={MARGIN.top}
            width={plotW}
            height={plotH}
            fill="none"
            stroke="var(--color-border)"
            strokeWidth="1"
          />

          {/* ── Grid lines (back layer) ── */}
          <g aria-hidden="true">
            {gridXValues.map((v, i) => (
              <line
                key={`gx-${i}`}
                x1={toSvgX(v)}
                y1={MARGIN.top}
                x2={toSvgX(v)}
                y2={MARGIN.top + plotH}
                stroke="var(--color-border)"
                strokeWidth="1"
                strokeOpacity="0.5"
              />
            ))}
            {gridYValues.map((v, i) => (
              <line
                key={`gy-${i}`}
                x1={MARGIN.left}
                y1={toSvgY(v)}
                x2={MARGIN.left + plotW}
                y2={toSvgY(v)}
                stroke="var(--color-border)"
                strokeWidth="1"
                strokeOpacity="0.5"
              />
            ))}
          </g>

          {/* ── Cluster region labels (behind points) ── */}
          {showClusterLabels && (
            <g aria-hidden="true">
              {clusterCentroids.map((c) => (
                <text
                  key={`cluster-region-${c.clusterId}`}
                  x={c.cx}
                  y={c.cy}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fontSize={CLUSTER_LABEL_FONT_SIZE}
                  fontFamily="var(--font-body)"
                  fontWeight="var(--font-weight-bold)"
                  fill={c.color}
                  fillOpacity={CLUSTER_LABEL_OPACITY}
                  style={{ pointerEvents: "none", userSelect: "none" }}
                >
                  {c.label}
                </text>
              ))}
            </g>
          )}

          {/* ── Ellipses — "show all" mode (showUncertainty toggle) ── */}
          {showUncertainty && (
            <g aria-hidden="true">
              {points.map((p) => {
                if (!p.uncertainty) return null;
                const { semi_major, semi_minor, rotation_rad } = p.uncertainty;
                const aSvg = semi_major * svgUnitsPerDataUnit;
                const bSvg = semi_minor * svgUnitsPerDataUnit;
                const isHovered = hoveredTerm === p.term;
                const d = ellipsePathD(p.x, p.y, aSvg, bSvg, rotation_rad);
                const fillOpacity = isHovered ? 0.08 : 0.04;
                const strokeOpacity = isHovered ? 0.25 : 0.15;
                return (
                  <path
                    key={`ellipse-all-${p.term}`}
                    d={d}
                    fill={hexToRgba(p.color, fillOpacity)}
                    stroke={hexToRgba(p.color, strokeOpacity)}
                    strokeWidth="1"
                  />
                );
              })}
            </g>
          )}

          {/* ── Individual hover ellipse (shown only when not in show-all mode) ── */}
          {!showUncertainty && hoveredPoint?.uncertainty && (() => {
            const p = hoveredPoint;
            const { semi_major, semi_minor, rotation_rad } = p.uncertainty!;
            const aSvg = semi_major * svgUnitsPerDataUnit;
            const bSvg = semi_minor * svgUnitsPerDataUnit;
            const d = ellipsePathD(p.x, p.y, aSvg, bSvg, rotation_rad);
            return (
              <path
                key={`ellipse-hover-${p.term}`}
                d={d}
                fill={hexToRgba(p.color, 0.08)}
                stroke={hexToRgba(p.color, 0.25)}
                strokeWidth="1"
                aria-hidden="true"
              />
            );
          })()}

          {/* ── Term points ── */}
          <g>
            {points.map((p) => {
              const isHovered = hoveredTerm === p.term;
              return (
                <g
                  key={`point-${p.term}`}
                  onMouseEnter={(e) => handleMouseEnter(p.term, e)}
                  onMouseLeave={handleMouseLeave}
                  onMouseMove={(e) => handleMouseMove(p.term, e)}
                  style={{ cursor: "pointer" }}
                  aria-label={`${p.term} — ${p.clusterLabel}`}
                >
                  <circle
                    cx={p.x}
                    cy={p.y}
                    r={POINT_RADIUS}
                    fill={p.color}
                    stroke="white"
                    strokeWidth={isHovered ? 2 : 1}
                    opacity={isHovered ? 1 : 0.85}
                  />
                  {/* Larger invisible hit area */}
                  <circle
                    cx={p.x}
                    cy={p.y}
                    r={POINT_RADIUS + 5}
                    fill="transparent"
                    stroke="none"
                  />
                </g>
              );
            })}
          </g>

          {/* ── Term labels (greedy placed; hidden by default, shown via toggle) ── */}
          {showTermLabels && (
          <g aria-hidden="true">
            {points.map((p) => {
              const lp = labelPlacementMap.get(p.term);
              if (!lp) return null;
              return (
                <text
                  key={`label-${p.term}`}
                  className="term-mds-plot__term-label"
                  x={lp.lx + lp.width / 2}
                  y={lp.ly}
                  textAnchor="middle"
                  fontSize={LABEL_FONT_SIZE}
                  fontFamily="var(--font-body)"
                  fill="var(--color-text-secondary)"
                  style={{ pointerEvents: "none", userSelect: "none" }}
                >
                  {p.term}
                </text>
              );
            })}
          </g>
          )}

          {/* ── Axis labels ── */}
          <text
            x={MARGIN.left + plotW / 2}
            y={svgHeight - 8}
            textAnchor="middle"
            fontSize="12"
            fontFamily="var(--font-body)"
            fill="var(--color-text-secondary)"
            aria-hidden="true"
          >
            MDS Dimension 1 — relative
          </text>

          <text
            x={0}
            y={0}
            textAnchor="middle"
            fontSize="12"
            fontFamily="var(--font-body)"
            fill="var(--color-text-secondary)"
            transform={`translate(14, ${MARGIN.top + plotH / 2}) rotate(-90)`}
            aria-hidden="true"
          >
            MDS Dimension 2 — relative
          </text>
        </svg>

        {/* Tooltip (dark inverted, rendered outside SVG) */}
        {!readAsTable && tooltip !== null && hoveredPoint !== null && (
          <div
            className="term-mds-plot__tooltip"
            role="tooltip"
            style={{
              left: tooltip.screenX + 12,
              top: tooltip.screenY - 8,
            }}
          >
            <div className="term-mds-plot__tooltip-term">{hoveredPoint.term}</div>
            <div className="term-mds-plot__tooltip-cluster">{hoveredPoint.clusterLabel}</div>
            {hoveredPoint.uncertainty && (
              <>
                <hr className="term-mds-plot__tooltip-divider" />
                <div className="term-mds-plot__tooltip-ci-label">95% CI</div>
                <div className="term-mds-plot__tooltip-ci-row">
                  Semi-major: {hoveredPoint.uncertainty.semi_major.toFixed(4)}
                </div>
                <div className="term-mds-plot__tooltip-ci-row">
                  Semi-minor: {hoveredPoint.uncertainty.semi_minor.toFixed(4)}
                </div>
                <div className="term-mds-plot__tooltip-ci-row">
                  Rotation: {(hoveredPoint.uncertainty.rotation_rad * 180 / Math.PI).toFixed(1)}°
                </div>
                <div className="term-mds-plot__tooltip-ci-row">
                  Bootstrap N: {hoveredPoint.uncertainty.n_bootstrap}
                </div>
              </>
            )}
            <div className="term-mds-plot__tooltip-note">{UNCERTAINTY_NOTE}</div>
          </div>
        )}
      </div>

      {/* Caption with stress value */}
      {!readAsTable && stressValue !== undefined && (
        <p className="term-mds-plot__caption">
          Stress = {stressValue.toFixed(4)}
        </p>
      )}

      {/* Cluster legend removed — cluster region labels on the chart serve
          the same purpose without consuming vertical space. */}

      {/* TermMDSTable container — U1 Option A: ALWAYS in DOM */}
      <div
        id={TERM_MDS_TABLE_CONTAINER_ID}
        aria-hidden={readAsTable ? undefined : true}
        style={{ display: readAsTable ? undefined : "none" }}
      >
        <TermMDSTable
          domainResult={domainResult}
          points={points}
        />
      </div>
    </div>
  );
}
