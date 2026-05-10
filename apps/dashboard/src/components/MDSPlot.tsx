// @vitest-environment jsdom
/**
 * MDSPlot — the headline MDS visualization.
 *
 * Implements DESIGN_SYSTEM.md §3.3 + §3.3.5 (all binding requirements).
 * Hand-rolled SVG; no D3 dependency (Phase 5 per §3.2).
 *
 * R1-state rendering per §3.3.5:
 *   R1-a — filled circle, 10px diameter, model color, white 2px stroke.
 *           Confidence ellipse rendered (semi_major, semi_minor, rotation_rad).
 *   R1-b — dashed-stroke circle. Fill at 60% model-color opacity; stroke at 100%.
 *           No confidence ellipse (binding invariant 1).
 *   R1-c — hollow triangle (△), 3px solid stroke at 100% model-color opacity.
 *           No fill. No confidence ellipse (binding invariant 1).
 *
 * Tooltip copy per §3.3.5 imp. req. 5:
 *   R1-b: verbatim "Position uncertain — ..." copy with actual OCI substituted.
 *   R1-c: verbatim "Deterministic output — ..." copy.
 *   R1-a: OCI value, state badge, top-5 free-list terms.
 *
 * SVG container: role="img", aria-label per §12.6 binding format.
 *
 * OCI threshold: imported from config/analysis.ts (never as a literal).
 * Color assignment: received as modelColors prop (owner is App.tsx for Phase 5;
 *   moves to DataExplorer.tsx at T9 per §12.4).
 */

import { useState, useMemo, useCallback } from "react";
import type { DomainResultPublished, R1State, EllipseParams } from "../data/types";
import { OCI_LOW_CONCENTRATION_THRESHOLD } from "../config/analysis";

// ── Short-name map ──────────────────────────────────────────────────────────

/**
 * Map from canonical model_id to a short display name for chart labels.
 * Models not in this map fall back to the last path segment of the model_id.
 */
const MODEL_SHORT_NAMES: Record<string, string> = {
  "claude-opus-4-6": "Claude Opus 4.6",
  "claude-sonnet-4-6": "Claude Sonnet 4.6",
  "deepseek/deepseek-v3.2": "DeepSeek v3.2",
  "google/gemini-2.5-pro": "Gemini 2.5 Pro",
  "meta-llama/llama-4-maverick": "Llama 4 Maverick",
  "microsoft/phi-4": "Phi-4",
  "mistralai/mistral-large-2512": "Mistral Large",
  "mistralai/mistral-small-2603": "Mistral Small",
  "openai/gpt-5.4": "GPT-5.4",
  "openai/gpt-5.4-mini": "GPT-5.4 mini",
  "x-ai/grok-4": "Grok 4",
};

function modelShortName(modelId: string): string {
  if (MODEL_SHORT_NAMES[modelId]) return MODEL_SHORT_NAMES[modelId];
  // Fallback: last segment after "/" or the full id.
  const parts = modelId.split("/");
  return parts[parts.length - 1];
}

// ── Props ───────────────────────────────────────────────────────────────────

export interface MDSPlotProps {
  domainResult: DomainResultPublished;
  /** model_id → CSS color value. Computed by §12.4 sorted-model_id algorithm. */
  modelColors: Record<string, string>;
}

// ── Internal types ──────────────────────────────────────────────────────────

interface ModelPoint {
  modelId: string;
  x: number;
  y: number;
  r1State: R1State;
  oci: number;
  color: string;
  shortName: string;
  topTerms: string[];
  ellipse: EllipseParams | null;
}

interface TooltipState {
  modelId: string;
  screenX: number;
  screenY: number;
}

// ── Plot constants ──────────────────────────────────────────────────────────

const SVG_WIDTH = 600;
const SVG_HEIGHT = 480;
const MARGIN = { top: 32, right: 40, bottom: 48, left: 60 };

const PLOT_W = SVG_WIDTH - MARGIN.left - MARGIN.right;
const PLOT_H = SVG_HEIGHT - MARGIN.top - MARGIN.bottom;

const POINT_RADIUS = 5; // 10px diameter
const GRID_LINE_COUNT = 5;

// ── Coordinate mapping helpers ───────────────────────────────────────────────

function buildScales(
  coords: Record<string, [number, number]>
): { toSvgX: (v: number) => number; toSvgY: (v: number) => number; domainMinX: number; domainMaxX: number; domainMinY: number; domainMaxY: number } {
  const xs = Object.values(coords).map((c) => c[0]);
  const ys = Object.values(coords).map((c) => c[1]);
  const rawMinX = Math.min(...xs);
  const rawMaxX = Math.max(...xs);
  const rawMinY = Math.min(...ys);
  const rawMaxY = Math.max(...ys);

  // Add 20% padding around the data range.
  const padX = (rawMaxX - rawMinX) * 0.20 + 0.01;
  const padY = (rawMaxY - rawMinY) * 0.20 + 0.01;

  const domainMinX = rawMinX - padX;
  const domainMaxX = rawMaxX + padX;
  const domainMinY = rawMinY - padY;
  const domainMaxY = rawMaxY + padY;

  const toSvgX = (v: number) =>
    MARGIN.left + ((v - domainMinX) / (domainMaxX - domainMinX)) * PLOT_W;

  // SVG y-axis is inverted (0 at top); we want higher data-y to be visually higher.
  const toSvgY = (v: number) =>
    MARGIN.top + ((domainMaxY - v) / (domainMaxY - domainMinY)) * PLOT_H;

  return { toSvgX, toSvgY, domainMinX, domainMaxX, domainMinY, domainMaxY };
}

// ── Ellipse SVG path ─────────────────────────────────────────────────────────

/**
 * Returns SVG path `d` attribute for a rotated ellipse centered at (cx, cy)
 * with semi-axes `a` (major) and `b` (minor), rotated by `angle` radians.
 *
 * The ellipse is approximated using four cubic Bezier curves.
 * This is the standard SVG-ellipse-via-Bezier approach (κ = 0.5522847).
 *
 * Note: We scale semi_major / semi_minor from data units to SVG pixels using
 * the scale factor derived from the x-axis (same for both axes since the scales
 * are symmetric around the data center — MDS coordinates are unitless and we
 * use uniform scaling).
 */
function ellipsePathD(
  cx: number,
  cy: number,
  a: number, // semi_major in SVG pixels
  b: number, // semi_minor in SVG pixels
  angle: number // rotation_rad
): string {
  const K = 0.5522847498;
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);

  // Four control points for the cubic Bezier approximation.
  // We define in local ellipse coordinates and then rotate.
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

// ── Triangle path for R1-c ───────────────────────────────────────────────────

/**
 * Returns SVG path `d` for an upward-pointing equilateral triangle centered at (cx, cy).
 * Size: outer radius r (point-to-center distance).
 * Hollow (no fill); stroke rendered by caller.
 */
function trianglePathD(cx: number, cy: number, r: number): string {
  // Three vertices of an equilateral triangle, apex at top.
  const top: [number, number] = [cx, cy - r];
  const bl: [number, number] = [cx - r * Math.sin(Math.PI * 2 / 3), cy + r * Math.cos(Math.PI * 2 / 3)];
  const br: [number, number] = [cx + r * Math.sin(Math.PI * 2 / 3), cy + r * Math.cos(Math.PI * 2 / 3)];
  const fmt = (n: number) => n.toFixed(2);
  return `M ${fmt(top[0])} ${fmt(top[1])} L ${fmt(br[0])} ${fmt(br[1])} L ${fmt(bl[0])} ${fmt(bl[1])} Z`;
}

// ── Hex color → rgba helper ──────────────────────────────────────────────────

/**
 * Converts a CSS hex color (#rrggbb) to an rgba() string with the given alpha.
 * Falls back to the hex with CSS opacity if parsing fails.
 */
function hexToRgba(hex: string, alpha: number): string {
  const clean = hex.replace("#", "");
  const r = parseInt(clean.substring(0, 2), 16);
  const g = parseInt(clean.substring(2, 4), 16);
  const b = parseInt(clean.substring(4, 6), 16);
  if (isNaN(r) || isNaN(g) || isNaN(b)) return hex;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

// ── Tooltip content ──────────────────────────────────────────────────────────

/**
 * Returns the tooltip JSX content for a model point, keyed by R1 state.
 * All copy verbatim from DESIGN_SYSTEM.md §3.3.5 binding requirements.
 * Schema identifiers (per §3.3.5 imp. req. 5) suppressed from user-facing copy.
 */
function TooltipContent({ point }: { point: ModelPoint }) {
  if (point.r1State === "deterministic") {
    // §3.3.5 implementation requirement 5 — verbatim binding copy.
    return (
      <div className="mds-plot__tooltip-body">
        <div className="mds-plot__tooltip-name">{point.shortName}</div>
        <div className="mds-plot__tooltip-id">{point.modelId}</div>
        <div className="mds-plot__tooltip-text">
          Deterministic output — this model produced the same categorical
          structure on every run. Its position on the map is consistent, but
          there is no uncertainty range to show. See the methodology page for
          why this is the least informative case, not the most.
        </div>
      </div>
    );
  }

  if (point.r1State === "low_concentration") {
    // §3.3.5 R1-b row — verbatim binding copy with OCI value substituted.
    const ociDisplay = point.oci.toFixed(1);
    return (
      <div className="mds-plot__tooltip-body">
        <div className="mds-plot__tooltip-name">{point.shortName}</div>
        <div className="mds-plot__tooltip-id">{point.modelId}</div>
        <div className="mds-plot__tooltip-text">
          Position uncertain — this model&apos;s within-model output
          concentration is low (OCI = {ociDisplay}; higher means runs converge
          on one structure). See model profile for within-model distribution.
        </div>
        <div className="mds-plot__tooltip-threshold">
          Threshold: OCI &lt; {OCI_LOW_CONCENTRATION_THRESHOLD}
        </div>
      </div>
    );
  }

  // R1-a — typical_concentration
  const ociDisplay = point.oci.toFixed(1);
  return (
    <div className="mds-plot__tooltip-body">
      <div className="mds-plot__tooltip-name">{point.shortName}</div>
      <div className="mds-plot__tooltip-id">{point.modelId}</div>
      <div className="mds-plot__tooltip-badge">
        OCI: {ociDisplay}{" "}
        <span className="mds-plot__tooltip-state">typical concentration</span>
      </div>
      {point.topTerms.length > 0 && (
        <div className="mds-plot__tooltip-terms">
          <div className="mds-plot__tooltip-terms-label">Top terms:</div>
          <div className="mds-plot__tooltip-terms-list">
            {point.topTerms.slice(0, 5).map((term) => (
              <span key={term} className="mds-plot__tooltip-term">
                {term}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Legend ───────────────────────────────────────────────────────────────────

/**
 * Inline legend below the plot.
 * Renders actual marker samples per §3.3.5 implementation requirement 4.
 * Each sample passes 3:1 contrast against the legend background (white).
 *
 * Marker sample colors use --color-model-1 as the sample color (DESIGN_SYSTEM.md §3.3.5 binding).
 */
function MDSLegend() {
  // Sample color: --color-model-1 = #3360a9
  const sampleColor = "#3360a9";
  const sampleColorFill60 = hexToRgba(sampleColor, 0.6);

  // R1-a: solid filled circle
  const r1aSvg = (
    <svg width="14" height="14" aria-hidden="true" focusable="false">
      <circle
        cx="7"
        cy="7"
        r="5"
        fill={sampleColor}
        stroke="white"
        strokeWidth="2"
      />
    </svg>
  );

  // R1-b: dashed-stroke circle with lighter fill (60% opacity fill, 100% stroke)
  const r1bSvg = (
    <svg width="14" height="14" aria-hidden="true" focusable="false">
      <circle
        cx="7"
        cy="7"
        r="5"
        fill={sampleColorFill60}
        stroke={sampleColor}
        strokeWidth="2"
        strokeDasharray="3 2"
      />
    </svg>
  );

  // R1-c: hollow triangle, 3px stroke, no fill
  const r1cTriPath = trianglePathD(7, 7, 5.5);
  const r1cSvg = (
    <svg width="14" height="14" aria-hidden="true" focusable="false">
      <path
        d={r1cTriPath}
        fill="none"
        stroke={sampleColor}
        strokeWidth="3"
        strokeLinejoin="round"
      />
    </svg>
  );

  return (
    <div className="mds-plot__legend" role="list" aria-label="Map marker legend">
      <div className="mds-plot__legend-item" role="listitem">
        {r1aSvg}
        <div className="mds-plot__legend-label">
          <span className="mds-plot__legend-primary">Typical concentration</span>
          <span className="mds-plot__legend-secondary">confidence ellipse shown</span>
        </div>
      </div>
      <div className="mds-plot__legend-item" role="listitem">
        {r1bSvg}
        <div className="mds-plot__legend-label">
          <span className="mds-plot__legend-primary">Low output concentration</span>
          <span className="mds-plot__legend-secondary">position uncertain</span>
        </div>
      </div>
      <div className="mds-plot__legend-item" role="listitem">
        {r1cSvg}
        <div className="mds-plot__legend-label">
          <span className="mds-plot__legend-primary">Deterministic output</span>
          <span className="mds-plot__legend-secondary">
            zero variance — the mismatch is the finding
          </span>
        </div>
      </div>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export function MDSPlot({ domainResult, modelColors }: MDSPlotProps) {
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);

  // Build a lookup of OCI + deterministic_output from within_model_results array.
  const withinModelLookup = useMemo(() => {
    const lookup: Record<string, { oci: number; deterministic_output: boolean }> = {};
    for (const wm of domainResult.within_model_results) {
      lookup[wm.model_id] = {
        oci: wm.oci,
        deterministic_output: wm.deterministic_output,
      };
    }
    return lookup;
  }, [domainResult.within_model_results]);

  // Cast mds_coordinates to the actual runtime shape (Record<string, [number, number]>).
  // The types.ts declares [[number, number]] but runtime data is [number, number].
  const rawCoords = domainResult.mds_coordinates as unknown as Record<string, [number, number]>;

  const { toSvgX, toSvgY, domainMinX, domainMaxX, domainMinY, domainMaxY } =
    useMemo(() => buildScales(rawCoords), [rawCoords]);

  // Build model point descriptors.
  const points: ModelPoint[] = useMemo(() => {
    return Object.keys(rawCoords).map((modelId) => {
      const [dx, dy] = rawCoords[modelId];
      const r1State = domainResult.display.r1_states[modelId] ?? "typical_concentration";
      const wmData = withinModelLookup[modelId] ?? { oci: 0, deterministic_output: false };
      const color = modelColors[modelId] ?? "#7f8c8d";
      const topTerms = domainResult.display.top_terms[modelId] ?? [];
      const ellipse =
        r1State === "typical_concentration"
          ? (domainResult.mds_uncertainty[modelId] ?? null)
          : null;

      return {
        modelId,
        x: toSvgX(dx),
        y: toSvgY(dy),
        r1State,
        oci: wmData.oci,
        color,
        shortName: modelShortName(modelId),
        topTerms,
        ellipse,
      };
    });
  }, [rawCoords, domainResult, withinModelLookup, modelColors, toSvgX, toSvgY]);

  // Scale factor from data units to SVG pixels (x-axis).
  const dataRangeX = domainMaxX - domainMinX;
  const svgUnitsPerDataUnit = PLOT_W / dataRangeX;

  // Compute the aria-label per §12.6 binding format.
  // Format: "MDS cognitive map of {n} frontier language models on the {domain} domain. {first sentence of generated_lede}."
  const nModels = points.length;
  const domainLabel = domainResult.domain_slug;
  const firstSentence = domainResult.generated_lede.split(". ")[0] ?? domainResult.generated_lede;
  const ariaLabel = `MDS cognitive map of ${nModels} frontier language models on the ${domainLabel} domain. ${firstSentence}.`;

  const handleMouseEnter = useCallback(
    (modelId: string, e: React.MouseEvent<SVGElement>) => {
      setHoveredId(modelId);
      const rect = (e.currentTarget.ownerSVGElement ?? e.currentTarget).getBoundingClientRect();
      setTooltip({
        modelId,
        screenX: e.clientX - rect.left,
        screenY: e.clientY - rect.top,
      });
    },
    []
  );

  const handleMouseLeave = useCallback(() => {
    setHoveredId(null);
    setTooltip(null);
  }, []);

  const handleMouseMove = useCallback(
    (modelId: string, e: React.MouseEvent<SVGElement>) => {
      const rect = (e.currentTarget.ownerSVGElement ?? e.currentTarget).getBoundingClientRect();
      setTooltip({
        modelId,
        screenX: e.clientX - rect.left,
        screenY: e.clientY - rect.top,
      });
    },
    []
  );

  // Grid line values.
  const gridXValues = useMemo(() => {
    const step = (domainMaxX - domainMinX) / (GRID_LINE_COUNT + 1);
    return Array.from({ length: GRID_LINE_COUNT }, (_, i) => domainMinX + step * (i + 1));
  }, [domainMinX, domainMaxX]);

  const gridYValues = useMemo(() => {
    const step = (domainMaxY - domainMinY) / (GRID_LINE_COUNT + 1);
    return Array.from({ length: GRID_LINE_COUNT }, (_, i) => domainMinY + step * (i + 1));
  }, [domainMinY, domainMaxY]);

  const hoveredPoint = hoveredId ? points.find((p) => p.modelId === hoveredId) ?? null : null;

  return (
    <div className="mds-plot">
      {/* SVG visualization */}
      <svg
        className="mds-plot__svg"
        width={SVG_WIDTH}
        height={SVG_HEIGHT}
        viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}
        role="img"
        aria-label={ariaLabel}
        style={{ overflow: "visible" }}
      >
        {/* ── Plot frame ── */}
        <rect
          x={MARGIN.left}
          y={MARGIN.top}
          width={PLOT_W}
          height={PLOT_H}
          fill="none"
          stroke="var(--color-border)"
          strokeWidth="1"
        />

        {/* ── Grid lines (back layer) ── */}
        <g className="mds-plot__grid" aria-hidden="true">
          {gridXValues.map((v, i) => {
            const sx = toSvgX(v);
            return (
              <line
                key={`gx-${i}`}
                x1={sx}
                y1={MARGIN.top}
                x2={sx}
                y2={MARGIN.top + PLOT_H}
                stroke="var(--color-border)"
                strokeWidth="1"
                strokeOpacity="0.5"
              />
            );
          })}
          {gridYValues.map((v, i) => {
            const sy = toSvgY(v);
            return (
              <line
                key={`gy-${i}`}
                x1={MARGIN.left}
                y1={sy}
                x2={MARGIN.left + PLOT_W}
                y2={sy}
                stroke="var(--color-border)"
                strokeWidth="1"
                strokeOpacity="0.5"
              />
            );
          })}
        </g>

        {/* ── Confidence ellipses (R1-a only, behind points) ── */}
        <g className="mds-plot__ellipses" aria-hidden="true">
          {points.map((point) => {
            if (point.r1State !== "typical_concentration") return null;
            if (!point.ellipse) return null;

            const { semi_major, semi_minor, rotation_rad } = point.ellipse;
            const aSvg = semi_major * svgUnitsPerDataUnit;
            const bSvg = semi_minor * svgUnitsPerDataUnit;

            const isHovered = hoveredId === point.modelId;
            const fillOpacity = 0.08;
            const strokeOpacity = isHovered ? 0.50 : 0.25;

            const d = ellipsePathD(point.x, point.y, aSvg, bSvg, rotation_rad);

            return (
              <path
                key={`ellipse-${point.modelId}`}
                className="mds-plot__ellipse"
                d={d}
                data-model-id={point.modelId}
                fill={hexToRgba(point.color, fillOpacity)}
                stroke={hexToRgba(point.color, strokeOpacity)}
                strokeWidth="1.5"
              />
            );
          })}
        </g>

        {/* ── Model points (front layer) ── */}
        <g className="mds-plot__points">
          {points.map((point) => {
            const isHovered = hoveredId === point.modelId;

            if (point.r1State === "deterministic") {
              // R1-c: hollow triangle, 3px solid stroke at 100% model-color opacity.
              const d = trianglePathD(point.x, point.y, POINT_RADIUS + 2);
              return (
                <g
                  key={point.modelId}
                  className="mds-plot__point mds-plot__point--r1c"
                  data-model-id={point.modelId}
                  onMouseEnter={(e) => handleMouseEnter(point.modelId, e)}
                  onMouseLeave={handleMouseLeave}
                  onMouseMove={(e) => handleMouseMove(point.modelId, e)}
                  style={{ cursor: "pointer" }}
                  aria-label={`${point.shortName} — deterministic output`}
                >
                  <path
                    d={d}
                    fill="none"
                    stroke={point.color}
                    strokeWidth="3"
                    strokeLinejoin="round"
                    opacity={isHovered ? 0.85 : 1}
                  />
                  {/* Larger invisible hit area */}
                  <path
                    d={trianglePathD(point.x, point.y, POINT_RADIUS + 7)}
                    fill="transparent"
                    stroke="none"
                  />
                </g>
              );
            }

            if (point.r1State === "low_concentration") {
              // R1-b: dashed-stroke circle. Fill 60% opacity; stroke 100% opacity.
              return (
                <g
                  key={point.modelId}
                  className="mds-plot__point mds-plot__point--r1b"
                  data-model-id={point.modelId}
                  onMouseEnter={(e) => handleMouseEnter(point.modelId, e)}
                  onMouseLeave={handleMouseLeave}
                  onMouseMove={(e) => handleMouseMove(point.modelId, e)}
                  style={{ cursor: "pointer" }}
                  aria-label={`${point.shortName} — low output concentration`}
                >
                  <circle
                    cx={point.x}
                    cy={point.y}
                    r={POINT_RADIUS}
                    fill={hexToRgba(point.color, 0.6)}
                    stroke={point.color}
                    strokeWidth="2"
                    strokeDasharray="4 3"
                  />
                  {/* Larger invisible hit area */}
                  <circle cx={point.x} cy={point.y} r={POINT_RADIUS + 5} fill="transparent" stroke="none" />
                </g>
              );
            }

            // R1-a: filled circle, 10px diameter, model color, white 2px stroke.
            return (
              <g
                key={point.modelId}
                className="mds-plot__point mds-plot__point--r1a"
                data-model-id={point.modelId}
                onMouseEnter={(e) => handleMouseEnter(point.modelId, e)}
                onMouseLeave={handleMouseLeave}
                onMouseMove={(e) => handleMouseMove(point.modelId, e)}
                style={{ cursor: "pointer" }}
                aria-label={`${point.shortName}`}
              >
                <circle
                  cx={point.x}
                  cy={point.y}
                  r={POINT_RADIUS}
                  fill={point.color}
                  stroke="white"
                  strokeWidth="2"
                />
                {/* Larger invisible hit area */}
                <circle cx={point.x} cy={point.y} r={POINT_RADIUS + 5} fill="transparent" stroke="none" />
              </g>
            );
          })}
        </g>

        {/* ── Model labels ── */}
        <g className="mds-plot__labels" aria-hidden="true">
          {points.map((point) => (
            <text
              key={`label-${point.modelId}`}
              x={point.x + POINT_RADIUS + 4}
              y={point.y + 4}
              fontSize="12"
              fontFamily="var(--font-body)"
              fill="var(--color-text-secondary)"
              style={{ pointerEvents: "none", userSelect: "none" }}
            >
              {point.shortName}
            </text>
          ))}
        </g>

        {/* ── Axis labels ── */}
        {/* X-axis: "MDS Dimension 1 — relative" */}
        <text
          x={MARGIN.left + PLOT_W / 2}
          y={SVG_HEIGHT - 8}
          textAnchor="middle"
          fontSize="12"
          fontFamily="var(--font-body)"
          fill="var(--color-text-secondary)"
          aria-hidden="true"
        >
          MDS Dimension 1 — relative
        </text>

        {/* Y-axis: "MDS Dimension 2 — relative" (rotated −90°) */}
        <text
          x={0}
          y={0}
          textAnchor="middle"
          fontSize="12"
          fontFamily="var(--font-body)"
          fill="var(--color-text-secondary)"
          transform={`translate(14, ${MARGIN.top + PLOT_H / 2}) rotate(-90)`}
          aria-hidden="true"
        >
          MDS Dimension 2 — relative
        </text>
      </svg>

      {/* ── Tooltip (rendered outside SVG for overflow) ── */}
      {tooltip !== null && hoveredPoint !== null && (
        <div
          className="mds-plot__tooltip"
          role="tooltip"
          style={{
            left: tooltip.screenX + 12,
            top: tooltip.screenY - 8,
          }}
        >
          <TooltipContent point={hoveredPoint} />
        </div>
      )}

      {/* ── Legend ── */}
      <MDSLegend />
    </div>
  );
}
