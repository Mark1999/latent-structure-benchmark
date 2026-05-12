/**
 * SimilarityHeatmap — Phase 6 T5.
 *
 * Hand-rolled SVG heatmap showing pairwise cross-model similarity for the
 * currently selected models. Each cell encodes similarity as an alpha-blended
 * background, shows the numeric value, and provides a per-cell aria-label
 * with CI disclosure.
 *
 * R10 compliance:
 *   - Visual: numeric similarity label on every cell (var(--font-mono),
 *     var(--font-size-xs)) — point estimate visible.
 *   - DOM: aria-label on every <rect> encodes similarity + 95% CI.
 *   - Uncertainty: cells whose CI crosses SIMILARITY_NULL_VALUE get a
 *     dashed border (§4.5 reduced-saturation substitution per plan §2.3).
 *
 * F-T5-A1 (BINDING): <h2 className="sr-only"> as first child of root <div>.
 * F-T5-C1 (BINDING): HEATMAP_TEXT_SWITCH_THRESHOLD = 0.73; new token
 *   --color-heatmap-cell-text-dark used in dark-text arm. Plan §2.2 switch
 *   at 0.5 / fallback 0.55 NOT implemented (superseded by UI/UX verdict).
 * F-T5-M1 (ADVISORY): CSS label-suppression targets <text> only; aria-label
 *   on <rect> cells remains in DOM unaffected at all viewport widths.
 *
 * Type-safety note (deferred to T14 doc-sweep):
 *   data/types.ts types similarity_matrix and similarity_ci as nested objects
 *   (Record<string, Record<string, ...>>), but the live JSON is number[][] and
 *   [number,number][][]. T5 accesses both fields via cast-through-unknown.
 *   See §4 in the T5 plan for the T14 reconciliation note.
 *
 * Forbidden vocabulary compliance: no "worldview", "believes", "thinks",
 *   "agrees", "perceives", "understands", "missing", "placeholder", "pending"
 *   in any user-visible string per CLAUDE.md §7 and ARCHITECTURE.md §1.5.4.
 *
 * Reference:
 *   docs/status/2026-05-12-phase6-T5-architect-plan.md
 *   docs/status/2026-05-12-phase6-T5-cda-sme-verdict.md §5.1–§5.4
 *   docs/status/2026-05-12-phase6-T5-uiux-plan-verdict.md F-T5-A1, F-T5-C1, F-T5-M1
 *   DESIGN_SYSTEM.md §12.8 (v0.4.5)
 */

import { useMemo, useState, useCallback } from "react";
import type { DomainResultPublished } from "../data/types";
import { modelShortName } from "../lib/modelShortName";
import { SIMILARITY_NULL_VALUE } from "../config/analysis";
import "../styles/similarity-heatmap.css";

// ── Shape interfaces matching actual JSON (NOT data/types.ts — T14 concern) ──

/** JSON shape: number[][] (row × col, model-indexed by models array order) */
type SimilarityMatrix = number[][];

/** JSON shape: ([number, number] | null)[][] (row × col) */
type SimilarityCiMatrix = Array<Array<[number, number] | null>>;

// ── Constants ──────────────────────────────────────────────────────────────────

/**
 * RGB components of --color-text-primary (#2c3e50).
 * Used to compute alpha-blended cell backgrounds.
 * Kept in sync with tokens.css via this comment naming the source token.
 */
const HEATMAP_BASE_RGB = "44, 62, 80"; // --color-text-primary

/**
 * Contrast-switch threshold per DESIGN_SYSTEM.md §12.8 (F-T5-C1 BINDING).
 * Above this value: white text (var(--color-background), ≥4.5:1 at sim > 0.73).
 * At or below: black text (var(--color-heatmap-cell-text-dark), ≥4.66:1 at sim ≤ 0.73).
 *
 * The plan §2.2 switch at 0.5 and fallback at 0.55 are NOT implemented —
 * both fail WCAG AA 4.5:1 across the observed data range (holidays.json min ≈ 0.45).
 * See docs/status/2026-05-12-phase6-T5-uiux-plan-verdict.md §2 for full analysis.
 */
const HEATMAP_TEXT_SWITCH_THRESHOLD = 0.73;
// WCAG AA rationale:
//   sim=0.51 → L≈0.356 → white text 2.59:1 FAIL
//   sim=0.55 → L≈0.322 → white text 2.82:1 FAIL
//   sim=0.73 → L≈0.183 → white text 4.50:1 PASS (threshold)
//   sim=0.73 → L≈0.183 → black text 4.66:1 PASS (threshold)

// ── Layout constants ────────────────────────────────────────────────────────────

const CELL_SIZE = 52;         // px — cell width and height
const HEADER_SIZE = 72;       // px — row/col header zone (label + rotation)
const CELL_PADDING = 2;       // px — gap between cells
const SVG_PADDING = 8;        // px — outer SVG padding

// ── Helpers ──────────────────────────────────────────────────────────────────────

/**
 * Alpha-blended cell background using --color-text-primary RGB.
 */
function cellBackground(similarity: number): string {
  return `rgba(${HEATMAP_BASE_RGB}, ${similarity})`;
}

/**
 * Returns white or black text fill per DESIGN_SYSTEM.md §12.8 contrast rule.
 */
function cellTextFill(similarity: number): string {
  return similarity > HEATMAP_TEXT_SWITCH_THRESHOLD
    ? "var(--color-background)"             // white ≥4.5:1 at sim > 0.73
    : "var(--color-heatmap-cell-text-dark)"; // black ≥4.66:1 at sim ≤ 0.73
}

/**
 * Checks whether a cell's CI crosses the formal similarity null (SIMILARITY_NULL_VALUE).
 * Null CIs cannot cross null by definition — they return false.
 */
function ciCrossesNull(ci: [number, number] | null): boolean {
  if (!ci) return false;
  return ci[0] < SIMILARITY_NULL_VALUE && SIMILARITY_NULL_VALUE < ci[1];
}

// ── aria-label builders ────────────────────────────────────────────────────────

/**
 * Build the aria-label for a diagonal (self-similarity) cell.
 * Plan §2.4: "${shortName} self-similarity: 1.00 by construction".
 */
function diagonalAriaLabel(shortName: string): string {
  return `${shortName} self-similarity: 1.00 by construction`;
}

/**
 * Build the aria-label for an off-diagonal cell.
 * Base template from plan §2.4.
 * CDA SME N2 (BINDING): append "; confidence interval includes the
 *   no-shared-structure value of 0.50" when CI crosses null.
 */
function cellAriaLabel(
  shortNameA: string,
  shortNameB: string,
  similarity: number,
  ci: [number, number] | null
): string {
  if (ci === null) {
    return `${shortNameA} versus ${shortNameB}: similarity ${similarity.toFixed(2)}, confidence interval not available`;
  }
  const base = `${shortNameA} versus ${shortNameB}: similarity ${similarity.toFixed(2)}, 95 percent confidence interval ${ci[0].toFixed(2)} to ${ci[1].toFixed(2)}`;
  if (ciCrossesNull(ci)) {
    // CDA SME N2 binding augmentation.
    return `${base}; confidence interval includes the no-shared-structure value of 0.50`;
  }
  return base;
}

// ── Tooltip state ───────────────────────────────────────────────────────────────

interface TooltipState {
  visible: boolean;
  x: number;
  y: number;
  shortNameA: string;
  shortNameB: string;
  similarity: number;
  ci: [number, number] | null;
  isDiagonal: boolean;
}

const TOOLTIP_HIDDEN: TooltipState = {
  visible: false,
  x: 0,
  y: 0,
  shortNameA: "",
  shortNameB: "",
  similarity: 0,
  ci: null,
  isDiagonal: false,
};

// ── Props ─────────────────────────────────────────────────────────────────────

export interface SimilarityHeatmapProps {
  domainResult: DomainResultPublished;
  selectedModels: string[];
}

// ── Component ──────────────────────────────────────────────────────────────────

/**
 * SimilarityHeatmap renders a grid of cells indexed by selectedModels × selectedModels.
 *
 * Layout (plan §2.5, §2.8):
 *   - Column headers above, row headers to left.
 *   - Display order: selectedModels sorted lexicographically.
 *   - Dual-index translation: display index → models[] array index via modelIndexMap.
 *
 * Accessibility (F-T5-A1 binding):
 *   - sr-only <h2> as first child of root <div> (NOT inside <svg>).
 *   - SVG role="img" with aria-label counting displayed/total models.
 *   - Per-cell aria-label on <rect> per §2.4 + CDA SME N2.
 *
 * Mobile (plan §2.0, §3.20):
 *   - SVG viewBox + preserveAspectRatio="xMidYMid meet" for responsive scaling.
 *   - Touch tooltip via focusin with tabIndex={0} per FreeListCompare precedent.
 *   - CSS suppresses <text> cell labels below 480px; aria-labels unaffected (F-T5-M1).
 */
export function SimilarityHeatmap({
  domainResult,
  selectedModels,
}: SimilarityHeatmapProps) {
  // ── Cast-through-unknown for shape mismatches (T14 concern) ────────────────
  const rawSimilarityMatrix = domainResult.similarity_matrix as unknown as SimilarityMatrix;
  const rawSimilarityCi = domainResult.similarity_ci as unknown as SimilarityCiMatrix;

  // ── Tooltip state ──────────────────────────────────────────────────────────
  const [tooltip, setTooltip] = useState<TooltipState>(TOOLTIP_HIDDEN);

  // ── Dual-index translation (plan §2.8) ────────────────────────────────────
  /**
   * Build modelIndexMap: model_id → index in domainResult.models array.
   * This maps display model_ids to the row/col indices in similarity_matrix.
   */
  const modelIndexMap = useMemo((): Map<string, number> => {
    const map = new Map<string, number>();
    domainResult.models.forEach((m, i) => {
      map.set(m.model_id, i);
    });
    return map;
  }, [domainResult.models]);

  /**
   * displayedIds: selectedModels sorted lexicographically.
   * Plan §2.8: "Sort selectedModels lexicographically: displayedIds = [...selectedModels].sort()".
   */
  const displayedIds = useMemo((): string[] => {
    return [...selectedModels].sort();
  }, [selectedModels]);

  const n = displayedIds.length;
  const totalModels = domainResult.models.length;

  // ── SVG geometry ────────────────────────────────────────────────────────────
  const gridWidth = n * (CELL_SIZE + CELL_PADDING) - CELL_PADDING;
  const gridHeight = n * (CELL_SIZE + CELL_PADDING) - CELL_PADDING;
  const svgWidth = HEADER_SIZE + gridWidth + SVG_PADDING * 2;
  const svgHeight = HEADER_SIZE + gridHeight + SVG_PADDING * 2;

  // ── Tooltip handlers ────────────────────────────────────────────────────────
  const showTooltip = useCallback((
    e: React.MouseEvent<SVGRectElement> | React.FocusEvent<SVGRectElement>,
    dispI: number,
    dispJ: number
  ) => {
    const idA = displayedIds[dispI];
    const idB = displayedIds[dispJ];
    const matI = modelIndexMap.get(idA) ?? 0;
    const matJ = modelIndexMap.get(idB) ?? 0;

    const similarity = rawSimilarityMatrix[matI]?.[matJ] ?? 1.0;
    const ci = rawSimilarityCi?.[matI]?.[matJ] ?? null;
    const isDiagonal = dispI === dispJ;

    // Use SVG container bounding rect for tooltip positioning.
    const svgEl = (e.currentTarget as SVGRectElement).closest("svg");
    const rect = svgEl?.getBoundingClientRect();
    const cellRect = (e.currentTarget as SVGRectElement).getBoundingClientRect();

    const x = rect ? cellRect.left - rect.left + CELL_SIZE / 2 : 0;
    const y = rect ? cellRect.top - rect.top : 0;

    setTooltip({
      visible: true,
      x,
      y,
      shortNameA: modelShortName(idA),
      shortNameB: modelShortName(idB),
      similarity,
      ci,
      isDiagonal,
    });
  }, [displayedIds, modelIndexMap, rawSimilarityMatrix, rawSimilarityCi]);

  const hideTooltip = useCallback(() => {
    setTooltip(TOOLTIP_HIDDEN);
  }, []);

  // ── Tooltip text builders ───────────────────────────────────────────────────
  /**
   * Build tooltip line 1: model pair label.
   * Plan §2.4: "<short model name A> vs <short model name B>".
   */
  function tooltipLine1(isDiagonal: boolean, nameA: string, nameB: string): string {
    if (isDiagonal) return `${nameA} (self)`;
    return `${nameA} vs ${nameB}`;
  }

  /**
   * Build tooltip line 2: similarity value + CI.
   * Plan §2.4: "similarity: 0.73, 95% CI [0.65, 0.81]". Null CI: "95% CI: —".
   */
  function tooltipLine2(sim: number, ci: [number, number] | null): string {
    const simStr = `similarity: ${sim.toFixed(2)}`;
    if (ci === null) return `${simStr}, 95% CI: —`;
    return `${simStr}, 95% CI [${ci[0].toFixed(2)}, ${ci[1].toFixed(2)}]`;
  }

  // ── Render ─────────────────────────────────────────────────────────────────

  // Empty state: no models selected.
  if (n === 0) {
    return (
      <div className="similarity-heatmap">
        {/* F-T5-A1 binding: sr-only h2 as first child of root div */}
        <h2 className="sr-only">Similarity heatmap</h2>
        <p className="similarity-heatmap__empty">
          Select one or more models to see the similarity heatmap.
        </p>
      </div>
    );
  }

  return (
    <div className="similarity-heatmap">
      {/* F-T5-A1 (BINDING): sr-only h2 as first child of root <div>, NOT inside <svg>.
          HTML <h2> inside <svg> is non-conformant. Match FreeListCompare.tsx line 157 pattern.
          Heading hierarchy: page h1 → this h2 → column/row header elements. */}
      <h2 className="sr-only">Similarity heatmap</h2>

      {/* SVG container — positioned relative for tooltip overlay */}
      <div className="similarity-heatmap__svg-container">
        <svg
          className="similarity-heatmap__svg"
          role="img"
          aria-label={`Cross-model similarity heatmap; ${n} model${n === 1 ? "" : "s"} displayed of ${totalModels} total`}
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          preserveAspectRatio="xMidYMid meet"
          style={{ width: "100%", maxWidth: `${svgWidth}px`, display: "block" }}
        >
          {/* ── Column header labels (rotated 45°) ────────────────────────── */}
          {displayedIds.map((modelId, dispJ) => {
            const cx = SVG_PADDING + HEADER_SIZE + dispJ * (CELL_SIZE + CELL_PADDING) + CELL_SIZE / 2;
            const cy = SVG_PADDING + HEADER_SIZE - 8;
            const shortName = modelShortName(modelId);

            return (
              <text
                key={`col-header-${modelId}`}
                className="similarity-heatmap__header-label"
                x={cx}
                y={cy}
                textAnchor="start"
                dominantBaseline="middle"
                transform={`rotate(-45, ${cx}, ${cy})`}
                fontSize="var(--font-size-xs)"
                fontFamily="var(--font-mono)"
                fill="var(--color-text-primary)"
                aria-hidden="true"
              >
                {shortName}
              </text>
            );
          })}

          {/* ── Row header labels ──────────────────────────────────────────── */}
          {displayedIds.map((modelId, dispI) => {
            const cy =
              SVG_PADDING + HEADER_SIZE + dispI * (CELL_SIZE + CELL_PADDING) + CELL_SIZE / 2;
            const cx = SVG_PADDING + HEADER_SIZE - 8;
            const shortName = modelShortName(modelId);

            return (
              <text
                key={`row-header-${modelId}`}
                className="similarity-heatmap__header-label"
                x={cx}
                y={cy}
                textAnchor="end"
                dominantBaseline="middle"
                fontSize="var(--font-size-xs)"
                fontFamily="var(--font-mono)"
                fill="var(--color-text-primary)"
                aria-hidden="true"
              >
                {shortName}
              </text>
            );
          })}

          {/* ── Cells ─────────────────────────────────────────────────────── */}
          {displayedIds.map((rowId, dispI) => {
            const matI = modelIndexMap.get(rowId) ?? 0;
            return displayedIds.map((colId, dispJ) => {
              const matJ = modelIndexMap.get(colId) ?? 0;
              const similarity = rawSimilarityMatrix[matI]?.[matJ] ?? 1.0;
              const ci: [number, number] | null = rawSimilarityCi?.[matI]?.[matJ] ?? null;
              const isDiagonal = dispI === dispJ;
              const crossesNull = !isDiagonal && ciCrossesNull(ci);

              const cellX =
                SVG_PADDING + HEADER_SIZE + dispJ * (CELL_SIZE + CELL_PADDING);
              const cellY =
                SVG_PADDING + HEADER_SIZE + dispI * (CELL_SIZE + CELL_PADDING);

              const bg = cellBackground(similarity);
              const textFill = cellTextFill(similarity);

              // Dashed border: CI crosses null (§2.3 binding).
              // Null CI cells and diagonal: solid border (§2.7 and §2.6).
              const strokeDasharray = crossesNull ? "3,2" : undefined;
              const strokeWidth = crossesNull ? 1.5 : 1;
              const stroke = crossesNull
                ? "var(--color-text-primary)"
                : "var(--color-border)";

              // Aria-label per §2.4 + CDA SME N2.
              const ariaLabelValue = isDiagonal
                ? diagonalAriaLabel(modelShortName(rowId))
                : cellAriaLabel(
                    modelShortName(rowId),
                    modelShortName(colId),
                    similarity,
                    ci
                  );

              return (
                <g key={`cell-${rowId}-${colId}`}>
                  {/* Cell background rect — carries aria-label, tabIndex, event handlers */}
                  <rect
                    x={cellX}
                    y={cellY}
                    width={CELL_SIZE}
                    height={CELL_SIZE}
                    fill={bg}
                    stroke={stroke}
                    strokeWidth={strokeWidth}
                    strokeDasharray={strokeDasharray}
                    rx={2}
                    ry={2}
                    tabIndex={0}
                    aria-label={ariaLabelValue}
                    role="img"
                    onMouseEnter={(e) => showTooltip(e, dispI, dispJ)}
                    onMouseLeave={hideTooltip}
                    onFocus={(e) => showTooltip(e, dispI, dispJ)}
                    onBlur={hideTooltip}
                    style={{ cursor: "default", outline: "none" }}
                  />
                  {/* Cell label — numeric similarity value.
                      CSS class targets this <text> for narrow-viewport suppression.
                      The aria-label on the <rect> above is UNAFFECTED by label
                      suppression — F-T5-M1 confirmed: suppression targets <text>
                      elements only, aria-labels remain in DOM. */}
                  <text
                    className="similarity-heatmap__cell-label"
                    x={cellX + CELL_SIZE / 2}
                    y={cellY + CELL_SIZE / 2}
                    textAnchor="middle"
                    dominantBaseline="central"
                    fontSize="var(--font-size-xs)"
                    fontFamily="var(--font-mono)"
                    fill={textFill}
                    aria-hidden="true"
                    style={{ pointerEvents: "none", userSelect: "none" }}
                  >
                    {similarity.toFixed(2)}
                  </text>
                </g>
              );
            });
          })}
        </svg>

        {/* ── Tooltip overlay (plan §2.4) ─────────────────────────────────── */}
        {tooltip.visible && (
          <div
            className="similarity-heatmap__tooltip"
            role="tooltip"
            style={{
              position: "absolute",
              left: tooltip.x,
              top: tooltip.y - 4,
              transform: "translate(-50%, -100%)",
              pointerEvents: "none",
            }}
          >
            <div className="similarity-heatmap__tooltip-line1">
              {tooltipLine1(tooltip.isDiagonal, tooltip.shortNameA, tooltip.shortNameB)}
            </div>
            <div className="similarity-heatmap__tooltip-line2">
              {tooltipLine2(tooltip.similarity, tooltip.ci)}
            </div>
          </div>
        )}
      </div>

      {/* ── Caption (CDA SME N1 — verbatim binding text) ───────────────────── */}
      {/*
        Verbatim caption per CDA SME N5.1 and plan §3 AC#9.
        Source: docs/status/2026-05-12-phase6-T5-cda-sme-verdict.md §5.1.
        Do NOT paraphrase or alter this text without CDA SME re-approval.
      */}
      <p className="similarity-heatmap__caption">
        Each cell shows how similarly two models organize this domain (1.00 ={" "}
        identical organization; 0.50 = no shared structure). Dashed cells: 95%
        confidence interval includes the no-shared-structure value.
      </p>
    </div>
  );
}
