// @vitest-environment jsdom
/**
 * CentralityChart — ranked horizontal bar chart of cultural centrality scores.
 *
 * Phase 9a T10. Implements the UI/UX visual specification from the T10 kickoff.
 *
 * What is displayed:
 *   - One horizontal bar per model, sorted descending by centrality score (highest at top).
 *   - Bar fill: model's assigned color from modelColors prop (same palette as MDSPlot).
 *   - Error bars: rendered when centrality_ci data is present in domainResult.
 *     Gracefully absent when CI data is not yet computed (T4/T5 carry-forward).
 *   - Negative centrality: bar extends left of zero axis. No red/error coloring —
 *     structural information, not a defect (CDA SME M8 binding).
 *   - Zero axis line always rendered.
 *
 * CDA SME M8 binding (verbatim tooltip text per Decision 8):
 *   "Cultural centrality measures how closely a model's categorical structure
 *    aligns with the dominant pattern across all models in this domain. A high
 *    score means this model's pile-sort structure is typical of the group. A low
 *    score means it organizes the domain differently. Neither is better or worse."
 *
 * R10 compliance (CLAUDE.md §6 R10 / ARCHITECTURE.md §4.5):
 *   Error bar code is always present. When CI data exists, error bars render.
 *   When CI data is absent, bars render only with note in SR summary.
 *
 * SVG geometry:
 *   Width: 600 (matches MDSPlot SVG_WIDTH).
 *   Height: dynamic — max(240, n_models * 36 + margin.top + margin.bottom).
 *   Bar slot: 36px (bar 20px + 8px gap above + 8px gap below).
 *   Margins: top 24, right 120, bottom 48, left 160.
 *
 * T8 pattern: ReadAsTableToggle + CentralityTable + ScreenReaderSummary.
 *   readAsTable state: local useState (per-viz, no DataExplorer state pollution).
 *   U1 (BINDING): table container div always in DOM; aria-hidden + display:none when inactive.
 *   ScreenReaderSummary: always present regardless of readAsTable state.
 *
 * Forbidden vocabulary: no "worldview", "believes", "thinks", "competence",
 *   "correctness", "better", "worse" (when applied to centrality as quality) per
 *   CLAUDE.md §7 and ARCHITECTURE.md §1.5.4. CDA SME M8 text is verbatim and exempt.
 *
 * Reference:
 *   docs/status/2026-05-24-phase9a-viz-gap-kickoff.md
 *   docs/status/2026-05-24-phase9a-cda-sme-verdict.md §8 (M8)
 *   DESIGN_SYSTEM.md §1.2, §3.2
 */

import { useState, useMemo, useCallback } from "react";
import type { DomainResultPublished } from "../data/types";
import { modelShortName } from "../lib/modelShortName";
import { ScreenReaderSummary } from "./ScreenReaderSummary";
import { ReadAsTableToggle } from "./ReadAsTableToggle";
import { CentralityTable } from "./CentralityTable";
import {
  READ_AS_TABLE_LABEL_REST,
  READ_AS_TABLE_LABEL_PRESSED,
  centralityScreenReaderSummary,
  mapConsensusType,
} from "../copy/screen_reader_summaries";
import "../styles/centrality-chart.css";

// ── Props ───────────────────────────────────────────────────────────────────

export interface CentralityChartProps {
  domainResult: DomainResultPublished;
  /** model_id → CSS color value. Computed by §12.4 sorted-model_id algorithm. */
  modelColors: Record<string, string>;
  /**
   * T7 pattern: subset of model_ids to display. If empty, renders no bars.
   * Default (undefined or omitted): render all models.
   */
  selectedModels?: string[];
}

// ── Types ───────────────────────────────────────────────────────────────────

/** Bootstrap CI for a single centrality score, if available. */
export interface CentralityCi {
  lo: number;
  hi: number;
  n_bootstrap?: number;
}

/** Shape of the optional centrality_ci field in the domain JSON. */
type CentralityCiRecord = Record<string, { lo: number; hi: number; n_bootstrap?: number } | [number, number] | null>;

// ── SVG geometry constants ──────────────────────────────────────────────────

const SVG_WIDTH = 600;
const MARGIN = { top: 24, right: 120, bottom: 48, left: 160 };
const BAR_SLOT = 36;    // px per bar row (bar 20px + 8px above + 8px below)
const BAR_HEIGHT = 20;  // px
const MIN_SVG_HEIGHT = 240;

// ── CDA SME M8 verbatim tooltip explanation ─────────────────────────────────

/**
 * Verbatim tooltip explanation per CDA SME Decision 8 (M8 binding).
 * Do NOT paraphrase or alter without CDA SME re-approval.
 */
const CENTRALITY_TOOLTIP_EXPLANATION =
  "Cultural centrality measures how closely a model's categorical structure aligns with the dominant pattern across all models in this domain. A high score means this model's pile-sort structure is typical of the group. A low score means it organizes the domain differently. Neither is better or worse.";

// ── Error bar cap size ───────────────────────────────────────────────────────

const ERROR_BAR_CAP_HALF = 3; // half-height of horizontal error bar caps (6px total)

// ── Tooltip state ────────────────────────────────────────────────────────────

interface TooltipState {
  modelId: string;
  screenX: number;
  screenY: number;
}

// ── Helper: truncate for mobile ──────────────────────────────────────────────

function truncateLabel(label: string, maxChars: number): string {
  if (label.length <= maxChars) return label;
  return label.slice(0, maxChars - 1) + "…";
}

// ── Helper: CI extraction ────────────────────────────────────────────────────

/**
 * Extract CentralityCi from the raw JSON value of centrality_ci[modelId].
 * The field may be stored as { lo, hi, n_bootstrap? } or as [lo, hi] tuple.
 */
function extractCi(raw: unknown): CentralityCi | null {
  if (raw === null || raw === undefined) return null;
  if (Array.isArray(raw) && raw.length >= 2) {
    return { lo: raw[0] as number, hi: raw[1] as number };
  }
  if (typeof raw === "object") {
    const obj = raw as Record<string, unknown>;
    if (typeof obj.lo === "number" && typeof obj.hi === "number") {
      return {
        lo: obj.lo,
        hi: obj.hi,
        n_bootstrap: typeof obj.n_bootstrap === "number" ? obj.n_bootstrap : undefined,
      };
    }
  }
  return null;
}

// ── Main component ────────────────────────────────────────────────────────────

const CENTRALITY_TABLE_CONTAINER_ID = "centrality-table-container";

export function CentralityChart({
  domainResult,
  modelColors,
  selectedModels,
}: CentralityChartProps) {
  const [readAsTable, setReadAsTable] = useState<boolean>(false);
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  // Cast cultural_centrality_scores from domain JSON (not in types.ts — same
  // cast-through-unknown pattern as other components per T14 doc-sweep concern).
  const centralityScores = useMemo(
    () =>
      (domainResult as unknown as { cultural_centrality_scores?: Record<string, number> })
        .cultural_centrality_scores ?? {},
    [domainResult]
  );

  // Cast centrality_ci — may be absent (T4/T5 carry-forward).
  const centralityCiRaw = useMemo(
    () =>
      (domainResult as unknown as { centrality_ci?: CentralityCiRecord }).centrality_ci,
    [domainResult]
  );
  const hasCiData = centralityCiRaw !== undefined && centralityCiRaw !== null;

  // Build the set of models to display.
  const allModelIds = useMemo(
    () => Object.keys(centralityScores).sort(),
    [centralityScores]
  );

  const displayedIds: string[] = useMemo(() => {
    if (selectedModels === undefined) return allModelIds;
    if (selectedModels.length === 0) return [];
    return selectedModels.filter((id) => id in centralityScores);
  }, [selectedModels, allModelIds, centralityScores]);

  // Sort displayed models descending by centrality score (highest at top).
  const sortedIds: string[] = useMemo(
    () =>
      [...displayedIds].sort(
        (a, b) => (centralityScores[b] ?? 0) - (centralityScores[a] ?? 0)
      ),
    [displayedIds, centralityScores]
  );

  // Compute SVG height dynamically.
  const nModels = sortedIds.length;
  const plotH = nModels * BAR_SLOT;
  const svgHeight = Math.max(MIN_SVG_HEIGHT, plotH + MARGIN.top + MARGIN.bottom);
  const plotW = SVG_WIDTH - MARGIN.left - MARGIN.right;

  // Determine x-axis domain: pad around [min_score, max_score], always include 0.
  const { xMin, xMax } = useMemo(() => {
    const scores = sortedIds.map((id) => centralityScores[id] ?? 0);
    // Also include CI bounds if present.
    const allValues = [...scores];
    if (hasCiData && centralityCiRaw) {
      for (const id of sortedIds) {
        const ci = extractCi(centralityCiRaw[id]);
        if (ci) {
          allValues.push(ci.lo, ci.hi);
        }
      }
    }
    allValues.push(0); // always include zero axis
    const rawMin = Math.min(...allValues);
    const rawMax = Math.max(...allValues);
    const range = rawMax - rawMin || 0.01;
    const pad = range * 0.12;
    return { xMin: rawMin - pad, xMax: rawMax + pad };
  }, [sortedIds, centralityScores, hasCiData, centralityCiRaw]);

  // Map data value to SVG x coordinate.
  const toSvgX = useCallback(
    (v: number): number =>
      MARGIN.left + ((v - xMin) / (xMax - xMin)) * plotW,
    [xMin, xMax, plotW]
  );

  // Zero axis position.
  const zeroX = toSvgX(0);

  // Bar y-center for a given row index.
  const barCenterY = useCallback(
    (rowIndex: number): number =>
      MARGIN.top + rowIndex * BAR_SLOT + BAR_SLOT / 2,
    []
  );

  // Tooltip handlers.
  const handleMouseEnter = useCallback(
    (modelId: string, e: React.MouseEvent<SVGElement>) => {
      setHoveredId(modelId);
      const rect = (e.currentTarget.ownerSVGElement ?? e.currentTarget).getBoundingClientRect();
      setTooltip({ modelId, screenX: e.clientX - rect.left, screenY: e.clientY - rect.top });
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
      setTooltip({ modelId, screenX: e.clientX - rect.left, screenY: e.clientY - rect.top });
    },
    []
  );

  // Compute aria-label for SVG container.
  const highestId = sortedIds[0] ?? "";
  const highestScore = highestId ? (centralityScores[highestId] ?? 0).toFixed(3) : "0.000";
  const highestShort = highestId ? modelShortName(highestId) : "";
  const ariaLabel =
    sortedIds.length > 0
      ? `Ranked bar chart of cultural centrality scores for ${sortedIds.length} models on the ${domainResult.domain_slug} domain. ${highestShort} has the highest centrality at ${highestScore}.`
      : `Cultural centrality chart for the ${domainResult.domain_slug} domain. No models selected.`;

  // ScreenReaderSummary text.
  const srSummaryText = centralityScreenReaderSummary(
    domainResult,
    sortedIds,
    centralityScores,
    hasCiData
  );

  // Caption text: includes consensus type per M8 binding.
  const consensusPhrase = mapConsensusType(
    domainResult.consensus_type as string | null | undefined
  );
  const eigenratio = (domainResult as unknown as { romney_eigenratio?: number }).romney_eigenratio;
  const eigenratioNote =
    eigenratio !== undefined
      ? ` (eigenratio: ${eigenratio.toFixed(2)})`
      : "";
  const captionText = consensusPhrase !== null
    ? `Cultural centrality scores for models on the ${domainResult.domain_slug} domain. Higher scores indicate closer alignment with the group's dominant categorical pattern. Domain consensus: ${consensusPhrase}${eigenratioNote}.`
    : `Cultural centrality scores for models on the ${domainResult.domain_slug} domain. Higher scores indicate closer alignment with the group's dominant categorical pattern.`;

  if (sortedIds.length === 0) {
    return (
      <div className="centrality-chart">
        <p className="centrality-chart__empty">Select one or more models to see cultural centrality scores.</p>
      </div>
    );
  }

  // Hovered model for tooltip display.
  const hoveredModelId = hoveredId;

  return (
    <div className="centrality-chart">
      {/* ScreenReaderSummary — always present in both viz and table modes */}
      <ScreenReaderSummary text={srSummaryText} />

      {/* ReadAsTableToggle */}
      <ReadAsTableToggle
        pressed={readAsTable}
        onToggle={() => setReadAsTable((v) => !v)}
        tableContainerId={CENTRALITY_TABLE_CONTAINER_ID}
        labels={{ rest: READ_AS_TABLE_LABEL_REST, pressed: READ_AS_TABLE_LABEL_PRESSED }}
      />

      {/* SVG visualization — hidden via aria-hidden + display:none when table is active */}
      <div className="centrality-chart__svg-container">
        <svg
          className="centrality-chart__svg"
          width={SVG_WIDTH}
          height={svgHeight}
          viewBox={`0 0 ${SVG_WIDTH} ${svgHeight}`}
          role="img"
          aria-label={ariaLabel}
          aria-hidden={readAsTable || undefined}
          style={{ overflow: "visible", display: readAsTable ? "none" : undefined }}
        >
          {/* ── Zero axis line ── */}
          <line
            x1={zeroX}
            y1={MARGIN.top}
            x2={zeroX}
            y2={MARGIN.top + plotH}
            stroke="var(--color-border)"
            strokeWidth="1"
            aria-hidden="true"
          />

          {/* ── Bars, error bars, and labels ── */}
          {sortedIds.map((modelId, rowIndex) => {
            const score = centralityScores[modelId] ?? 0;
            const color = modelColors[modelId] ?? "#7f8c8d";
            const shortName = modelShortName(modelId);
            const isNegative = score < 0;
            const isHovered = hoveredModelId === modelId;

            // Bar geometry
            const cy = barCenterY(rowIndex);
            const barTop = cy - BAR_HEIGHT / 2;
            const scoreX = toSvgX(score);
            const barX = Math.min(zeroX, scoreX);
            const barW = Math.abs(scoreX - zeroX);

            // CI data for this model (if available)
            const ciRaw = hasCiData && centralityCiRaw ? centralityCiRaw[modelId] : undefined;
            const ci = ciRaw !== undefined ? extractCi(ciRaw) : null;

            // Score label text
            const scoreLabelText = ci
              ? `${score.toFixed(3)} [${ci.lo.toFixed(2)}–${ci.hi.toFixed(2)}]`
              : score.toFixed(3);

            // Score label x position: right of bar end (or CI hi)
            const scoreLabelX = ci
              ? toSvgX(Math.max(score, ci.hi)) + 6
              : scoreX + 6;

            // Model name y position; if negative, add sub-note
            const labelY = isNegative ? cy - 8 : cy;

            return (
              <g
                key={modelId}
                className="centrality-chart__bar-group"
                onMouseEnter={(e) => handleMouseEnter(modelId, e)}
                onMouseLeave={handleMouseLeave}
                onMouseMove={(e) => handleMouseMove(modelId, e)}
                style={{ cursor: "pointer" }}
                aria-label={`${shortName}: cultural centrality ${score.toFixed(3)}`}
              >
                {/* Model name label */}
                <text
                  x={MARGIN.left - 8}
                  y={labelY}
                  className="centrality-chart__model-label"
                  aria-hidden="true"
                >
                  {truncateLabel(shortName, 20)}
                </text>

                {/* Negative centrality note */}
                {isNegative && (
                  <text
                    x={MARGIN.left - 8}
                    y={cy + 10}
                    className="centrality-chart__negative-note"
                    aria-hidden="true"
                  >
                    (negative centrality)
                  </text>
                )}

                {/* Bar */}
                <rect
                  x={barX}
                  y={barTop}
                  width={barW}
                  height={BAR_HEIGHT}
                  fill={color}
                  opacity={isHovered ? 0.85 : 1}
                  aria-hidden="true"
                />

                {/* Error bars — only when CI data present */}
                {ci !== null && (
                  <g aria-hidden="true" className="centrality-chart__error-bar">
                    {/* Horizontal CI line */}
                    <line
                      x1={toSvgX(ci.lo)}
                      y1={cy}
                      x2={toSvgX(ci.hi)}
                      y2={cy}
                      stroke={color}
                      strokeWidth="1.5"
                      strokeLinecap="round"
                    />
                    {/* Left cap */}
                    <line
                      x1={toSvgX(ci.lo)}
                      y1={cy - ERROR_BAR_CAP_HALF}
                      x2={toSvgX(ci.lo)}
                      y2={cy + ERROR_BAR_CAP_HALF}
                      stroke={color}
                      strokeWidth="1.5"
                      strokeLinecap="round"
                    />
                    {/* Right cap */}
                    <line
                      x1={toSvgX(ci.hi)}
                      y1={cy - ERROR_BAR_CAP_HALF}
                      x2={toSvgX(ci.hi)}
                      y2={cy + ERROR_BAR_CAP_HALF}
                      stroke={color}
                      strokeWidth="1.5"
                      strokeLinecap="round"
                    />
                  </g>
                )}

                {/* Score label */}
                <text
                  x={scoreLabelX}
                  y={cy}
                  className="centrality-chart__score-label"
                  aria-hidden="true"
                >
                  {scoreLabelText}
                </text>

                {/* Invisible hit area for hover */}
                <rect
                  x={MARGIN.left}
                  y={barTop - 4}
                  width={plotW}
                  height={BAR_HEIGHT + 8}
                  fill="transparent"
                  stroke="none"
                />
              </g>
            );
          })}

          {/* ── X-axis label ── */}
          <text
            x={MARGIN.left + plotW / 2}
            y={svgHeight - 10}
            className="centrality-chart__axis-label"
            aria-hidden="true"
          >
            Cultural centrality score
          </text>

          {/* ── X-axis tick labels ── */}
          <g aria-hidden="true">
            {[xMin, (xMin + xMax) / 2, xMax].map((v, i) => (
              <text
                key={i}
                x={toSvgX(v)}
                y={MARGIN.top + plotH + 16}
                textAnchor="middle"
                fontSize="11"
                fontFamily="var(--font-mono)"
                fill="var(--color-text-caption)"
              >
                {v.toFixed(2)}
              </text>
            ))}
          </g>
        </svg>

        {/* Tooltip */}
        {!readAsTable && tooltip !== null && hoveredModelId !== null && (
          <div
            className="centrality-chart__tooltip"
            role="tooltip"
            style={{ left: tooltip.screenX + 12, top: tooltip.screenY - 8 }}
          >
            <div className="centrality-chart__tooltip-name">
              {modelShortName(hoveredModelId)}
            </div>
            <div className="centrality-chart__tooltip-id">{hoveredModelId}</div>
            <div className="centrality-chart__tooltip-score">
              Cultural centrality:{" "}
              {(centralityScores[hoveredModelId] ?? 0).toFixed(3)}
            </div>
            {(() => {
              const ciRaw =
                hasCiData && centralityCiRaw ? centralityCiRaw[hoveredModelId] : undefined;
              const ci = ciRaw !== undefined ? extractCi(ciRaw) : null;
              if (ci) {
                return (
                  <>
                    <div className="centrality-chart__tooltip-ci">
                      95% CI: {ci.lo.toFixed(3)}–{ci.hi.toFixed(3)}
                    </div>
                    {ci.n_bootstrap !== undefined && (
                      <div className="centrality-chart__tooltip-n">
                        Bootstrap samples: {ci.n_bootstrap}
                      </div>
                    )}
                  </>
                );
              }
              return (
                <div className="centrality-chart__tooltip-ci">
                  Bootstrap CIs pending
                </div>
              );
            })()}
            <div className="centrality-chart__tooltip-explanation">
              {CENTRALITY_TOOLTIP_EXPLANATION}
            </div>
          </div>
        )}
      </div>

      {/* Caption */}
      {!readAsTable && (
        <p className="centrality-chart__caption">{captionText}</p>
      )}

      {/* CentralityTable container — U1 Option A: ALWAYS in DOM.
          aria-hidden="true" + display:none when readAsTable = false. */}
      <div
        id={CENTRALITY_TABLE_CONTAINER_ID}
        aria-hidden={readAsTable ? undefined : true}
        style={{ display: readAsTable ? undefined : "none" }}
      >
        <CentralityTable
          domainResult={domainResult}
          sortedIds={sortedIds}
          centralityScores={centralityScores}
          centralityCiRaw={centralityCiRaw ?? null}
          hasCiData={hasCiData}
        />
      </div>
    </div>
  );
}
