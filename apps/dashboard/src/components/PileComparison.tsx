/**
 * PileComparison — side-by-side pile structure comparison per DESIGN_SYSTEM.md §3.
 *
 * Phase 9a T9. Shows how different models partition domain terms into categories.
 *
 * Data shape (from centroid_piles field in domain JSON):
 *   centroid_piles: {
 *     [model_id: string]: {
 *       piles: string[][];            // list of piles, each pile is list of terms
 *       labels: string[];             // one label per pile
 *       term_stability: {             // fraction of runs where term is in same pile
 *         [term: string]: number;     // 0.0 to 1.0
 *       }
 *     }
 *   }
 *
 * NOTE: centroid_piles may not be present in published JSON files. The component
 * handles missing/empty data gracefully with an appropriate empty state.
 *
 * CDA SME M7 binding (Decision 7):
 *   - No model is ground truth — all columns equal width/weight
 *   - Divergence is a finding, not a failure
 *   - No "agreement score" displayed (that belongs in SimilarityHeatmap)
 *   - All models treated symmetrically; highlight applies to all columns
 *
 * R10 compliance (CLAUDE.md §6 R10 / ARCHITECTURE.md §4.5):
 *   Term stability tiers render via dashed-border classes, never a bare number.
 *   Tooltip on every pill shows placement percentage.
 *
 * Layout:
 *   - ≥1024px: CSS grid, one column per selected model, minmax(220px, 1fr)
 *   - <1024px: single-column with model-switcher pill row (radio group)
 *   - <480px: pile labels truncated to 28 chars
 *
 * Forbidden vocabulary: no "worldview", "believes", "thinks" (model-applied),
 *   "sees", "understands" per CLAUDE.md §7 and ARCHITECTURE.md §1.5.4.
 *
 * Reference:
 *   docs/status/2026-05-24-phase9a-viz-gap-kickoff.md T9
 *   docs/status/2026-05-24-phase9a-cda-sme-verdict.md §7 (M7)
 *   docs/status/2026-05-24-phase9a-T9-ui-ux-verdict.md
 *   DESIGN_SYSTEM.md v0.5.0
 */

import { useState, useMemo, useCallback, useEffect, useRef } from "react";
import type { DomainResultPublished } from "../data/types";
import { modelShortName } from "../lib/modelShortName";
import { ScreenReaderSummary } from "./ScreenReaderSummary";
import { ReadAsTableToggle } from "./ReadAsTableToggle";
import { PileComparisonTable } from "./PileComparisonTable";
import type { ModelPileData } from "./PileComparisonTable";
import {
  READ_AS_TABLE_LABEL_REST,
  READ_AS_TABLE_LABEL_PRESSED,
  pileComparisonScreenReaderSummary,
} from "../copy/screen_reader_summaries";
import {
  PILE_COMPARISON_DESCRIPTION,
  PILE_COMPARISON_EMPTY_NO_MODELS,
  PILE_COMPARISON_EMPTY_NO_DATA,
  PILE_COMPARISON_ABSENT_TERM_LABEL,
  PILE_COMPARISON_ABSENT_TOOLTIP,
  PILE_COMPARISON_STABILITY_TOOLTIP,
  PILE_COMPARISON_NO_LABEL,
  PILE_COMPARISON_LEGEND_LABEL,
  PILE_COMPARISON_LEGEND_SOLID,
  PILE_COMPARISON_LEGEND_DASHED_MEDIUM,
  PILE_COMPARISON_LEGEND_DASHED_LOW,
  PILE_COMPARISON_SR_HEADING,
  PILE_COMPARISON_MODEL_SWITCHER_ARIA_LABEL,
  PILE_COMPARISON_STABILITY_TOOLTIP_UNAVAILABLE,
} from "../copy/pile_comparison";
import "../styles/pile-comparison.css";

// ── Props ─────────────────────────────────────────────────────────────────────

export interface PileComparisonProps {
  domainResult: DomainResultPublished;
  modelColors: Record<string, string>;
  selectedModels: string[];
}

// ── Constants ─────────────────────────────────────────────────────────────────

const PILE_TABLE_CONTAINER_ID = "pile-comparison-table-container";

/** Max chars for pile labels at <480px (truncation handled in JS per spec). */
const PILE_LABEL_MAX_CHARS_MOBILE = 28;

/** Max chars for pile labels on all breakpoints. */
const PILE_LABEL_MAX_CHARS = 40;

/** Stability tier thresholds (fraction 0–1). */
const STABILITY_HIGH = 0.8;   // >= 0.8: default (solid border)
const STABILITY_MEDIUM = 0.6; // >= 0.6 and < 0.8: dashed faint
// < 0.6: dashed medium + caption text

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Truncate a string to maxChars with ellipsis if necessary. */
function truncate(s: string, maxChars: number): string {
  if (s.length <= maxChars) return s;
  return s.slice(0, maxChars - 1) + "…";
}

/** Determine stability CSS class modifier based on the stability fraction (0–1). */
function stabilityClass(stability: number | undefined): string {
  if (stability === undefined || stability === null) return "";
  if (stability >= STABILITY_HIGH) return "";
  if (stability >= STABILITY_MEDIUM) return "pile-comparison__pill--stability-medium";
  return "pile-comparison__pill--stability-low";
}

// ── Component ─────────────────────────────────────────────────────────────────

export function PileComparison({
  domainResult,
  modelColors,
  selectedModels,
}: PileComparisonProps) {
  // T8 pattern: local per-viz read-as-table state
  const [readAsTable, setReadAsTable] = useState<boolean>(false);

  // Cross-column hover highlight: which term is currently hovered/focused
  const [hoveredTerm, setHoveredTerm] = useState<string | null>(null);

  // Mobile model-switcher: which model is currently shown at <1024px
  const [mobileActiveModel, setMobileActiveModel] = useState<string | null>(null);

  // Detect narrow viewport for pile label truncation
  const [isNarrow, setIsNarrow] = useState<boolean>(false);

  // Ref for resize observer
  const containerRef = useRef<HTMLDivElement>(null);

  // Track narrow viewport via ResizeObserver on the container
  useEffect(() => {
    const el = containerRef.current;
    if (!el || typeof ResizeObserver === "undefined") return;

    const ro = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setIsNarrow(entry.contentRect.width < 480);
      }
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Cast centroid_piles from domain JSON (not in types.ts — same
  // cast-through-unknown pattern as other components per T14 doc-sweep concern).
  const centroidPiles = useMemo(
    () =>
      (domainResult as unknown as { centroid_piles?: Record<string, ModelPileData> })
        .centroid_piles ?? null,
    [domainResult]
  );

  // Determine which models have pile data
  const modelsWithData = useMemo(
    () => selectedModels.filter((id) => centroidPiles?.[id] != null),
    [selectedModels, centroidPiles]
  );

  // Initialize mobile active model to first model with data when selection changes.
  // Setting state in a useEffect that responds to a dependency change is the documented
  // React pattern for derived resets per https://react.dev/reference/react/useState
  // (see DataExplorer.tsx for the same eslint-disable pattern).
  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    if (modelsWithData.length > 0) {
      setMobileActiveModel((prev) => {
        if (prev !== null && modelsWithData.includes(prev)) return prev;
        return modelsWithData[0] ?? null;
      });
    } else {
      setMobileActiveModel(null);
    }
  }, [modelsWithData]);
  /* eslint-enable react-hooks/set-state-in-effect */

  // The set of all terms across all visible models (for cross-column presence check)
  const allTerms = useMemo((): Set<string> => {
    const s = new Set<string>();
    for (const modelId of modelsWithData) {
      const pileData = centroidPiles?.[modelId];
      if (!pileData) continue;
      for (const pile of pileData.piles) {
        for (const term of pile) {
          s.add(term);
        }
      }
    }
    return s;
  }, [modelsWithData, centroidPiles]);

  // Screen reader summary text
  const srSummaryText = pileComparisonScreenReaderSummary(
    domainResult.domain_slug,
    selectedModels.length
  );

  // ── Hover handlers ──────────────────────────────────────────────────────────

  const handleTermHover = useCallback((term: string | null) => {
    setHoveredTerm(term);
  }, []);

  // ── Empty states ────────────────────────────────────────────────────────────

  if (selectedModels.length === 0 && !readAsTable) {
    return (
      <div className="pile-comparison">
        <ScreenReaderSummary text={srSummaryText} />
        <p className="pile-comparison__empty">
          {PILE_COMPARISON_EMPTY_NO_MODELS(domainResult.domain_slug)}
        </p>
      </div>
    );
  }

  const hasAnyPileData = modelsWithData.length > 0;

  // ── Main render ─────────────────────────────────────────────────────────────

  return (
    <div className="pile-comparison" ref={containerRef}>
      {/* SR-only heading for heading hierarchy (same pattern as FreeListCompare) */}
      <h2 className="sr-only">{PILE_COMPARISON_SR_HEADING}</h2>

      {/* ScreenReaderSummary — always present in both viz and table modes */}
      <ScreenReaderSummary text={srSummaryText} />

      {/* ReadAsTableToggle */}
      <ReadAsTableToggle
        pressed={readAsTable}
        onToggle={() => setReadAsTable((v) => !v)}
        tableContainerId={PILE_TABLE_CONTAINER_ID}
        labels={{ rest: READ_AS_TABLE_LABEL_REST, pressed: READ_AS_TABLE_LABEL_PRESSED }}
      />

      {/* Description paragraph — visible, above columns (journalist test N2) */}
      {!readAsTable && selectedModels.length > 0 && (
        <p className="pile-comparison__description">
          {PILE_COMPARISON_DESCRIPTION(domainResult.domain_slug)}
        </p>
      )}

      {/* No pile data state */}
      {!readAsTable && selectedModels.length > 0 && !hasAnyPileData && (
        <p className="pile-comparison__empty">{PILE_COMPARISON_EMPTY_NO_DATA}</p>
      )}

      {/* Mobile model-switcher pill row (<1024px) */}
      {!readAsTable && hasAnyPileData && (
        <div
          className="pile-comparison__model-switcher"
          role="radiogroup"
          aria-label={PILE_COMPARISON_MODEL_SWITCHER_ARIA_LABEL}
        >
          {modelsWithData.map((modelId) => {
            const color = modelColors[modelId] ?? "#888888";
            const isActive = mobileActiveModel === modelId;
            const shortName = modelShortName(modelId);
            return (
              <button
                key={modelId}
                role="radio"
                aria-checked={isActive}
                className={[
                  "pile-comparison__model-pill",
                  isActive ? "pile-comparison__model-pill--active" : "",
                ].filter(Boolean).join(" ")}
                onClick={() => setMobileActiveModel(modelId)}
                type="button"
              >
                <span
                  className="pile-comparison__model-dot"
                  style={{ backgroundColor: isActive ? "#fff" : color }}
                  aria-hidden="true"
                />
                {shortName}
              </button>
            );
          })}
        </div>
      )}

      {/* Visualization columns — hidden via aria-hidden + display:none when table active */}
      {hasAnyPileData && (
        <div
          className="pile-comparison__columns"
          aria-hidden={readAsTable || undefined}
          style={{ display: readAsTable ? "none" : undefined }}
        >
          {modelsWithData.map((modelId) => {
            const pileData = centroidPiles![modelId]!;
            const color = modelColors[modelId] ?? "#888888";
            const shortName = modelShortName(modelId);

            // On mobile, only show the active model column
            // (CSS hides the grid and shows single column, but we still render all —
            //  visibility control is via CSS class on the columns container)

            return (
              <ModelColumn
                key={modelId}
                modelId={modelId}
                modelShortName={shortName}
                modelColor={color}
                pileData={pileData}
                hoveredTerm={hoveredTerm}
                onTermHover={handleTermHover}
                isNarrow={isNarrow}
                allTermsAcrossModels={allTerms}
                isMobileVisible={mobileActiveModel === modelId}
              />
            );
          })}
        </div>
      )}

      {/* Legend row below grid — aria-hidden per spec */}
      {hasAnyPileData && !readAsTable && (
        <div className="pile-comparison__legend" aria-hidden="true">
          <span className="pile-comparison__legend-label">{PILE_COMPARISON_LEGEND_LABEL}</span>
          <span className="pile-comparison__legend-item">
            <span className="pile-comparison__legend-pill pile-comparison__legend-pill--solid">
              term
            </span>
            {" "}{PILE_COMPARISON_LEGEND_SOLID}
          </span>
          <span className="pile-comparison__legend-item">
            <span className="pile-comparison__legend-pill pile-comparison__legend-pill--dashed-medium">
              term
            </span>
            {" "}{PILE_COMPARISON_LEGEND_DASHED_MEDIUM}
          </span>
          <span className="pile-comparison__legend-item">
            <span className="pile-comparison__legend-pill pile-comparison__legend-pill--dashed-low">
              term
            </span>
            {" "}{PILE_COMPARISON_LEGEND_DASHED_LOW}
          </span>
        </div>
      )}

      {/* PileComparisonTable container — U1 Option A: ALWAYS in DOM.
          aria-hidden="true" + display:none when readAsTable = false. */}
      <div
        id={PILE_TABLE_CONTAINER_ID}
        aria-hidden={readAsTable ? undefined : true}
        style={{ display: readAsTable ? undefined : "none" }}
      >
        <PileComparisonTable
          domainSlug={domainResult.domain_slug}
          selectedModels={selectedModels}
          centroidPiles={centroidPiles}
        />
      </div>
    </div>
  );
}

// ── ModelColumn sub-component ─────────────────────────────────────────────────

interface ModelColumnProps {
  modelId: string;
  modelShortName: string;
  modelColor: string;
  pileData: ModelPileData;
  hoveredTerm: string | null;
  onTermHover: (term: string | null) => void;
  isNarrow: boolean;
  allTermsAcrossModels: Set<string>;
  isMobileVisible: boolean;
}

function ModelColumn({
  modelId,
  modelShortName: shortName,
  modelColor,
  pileData,
  hoveredTerm,
  onTermHover,
  isNarrow,
  allTermsAcrossModels,
  isMobileVisible,
}: ModelColumnProps) {
  const { piles, labels, term_stability } = pileData;
  const labelMaxChars = isNarrow ? PILE_LABEL_MAX_CHARS_MOBILE : PILE_LABEL_MAX_CHARS;

  // Sort piles by size descending; alphabetical tiebreak on label
  const sortedPileIndices = useMemo(() => {
    const indices = piles.map((_, i) => i);
    return indices.sort((a, b) => {
      const sizeDiff = piles[b].length - piles[a].length;
      if (sizeDiff !== 0) return sizeDiff;
      const labelA = (labels[a] ?? "").toLowerCase();
      const labelB = (labels[b] ?? "").toLowerCase();
      return labelA.localeCompare(labelB);
    });
  }, [piles, labels]);

  // Determine if this column's card should highlight
  // (because the hovered term appears in it)
  const cardHighlightedPile = useMemo((): Set<number> => {
    if (hoveredTerm === null) return new Set();
    const s = new Set<number>();
    piles.forEach((pile, idx) => {
      if (pile.includes(hoveredTerm)) s.add(idx);
    });
    return s;
  }, [hoveredTerm, piles]);

  // Build the set of terms in THIS model's piles
  const ownTerms = useMemo((): Set<string> => {
    const s = new Set<string>();
    for (const pile of piles) {
      for (const term of pile) {
        s.add(term);
      }
    }
    return s;
  }, [piles]);

  // Mobile: hide column if not the active model (CSS handles desktop grid)
  // We apply a style only in the "mobile" layout context. Since CSS controls
  // the desktop grid but we use a single-column approach on mobile (showing
  // all columns in DOM but hiding via display), we let CSS handle visibility
  // through the .pile-comparison__columns container class.
  // The isMobileVisible flag is used by the mobile switcher CSS approach:
  // we add a data attribute so CSS can target the active column.

  return (
    <div
      className="pile-comparison__column"
      data-model-id={modelId}
      data-mobile-visible={isMobileVisible ? "true" : "false"}
      aria-label={`${shortName} pile structure`}
    >
      {/* Column header: dot + short name */}
      <div className="pile-comparison__column-header">
        <span
          className="pile-comparison__column-dot"
          style={{ backgroundColor: modelColor }}
          aria-hidden="true"
        />
        <span className="pile-comparison__column-name" title={shortName}>
          {shortName}
        </span>
      </div>

      {/* Pile cards */}
      <div className="pile-comparison__pile-list">
        {sortedPileIndices.map((pileIdx) => {
          const pile = piles[pileIdx];
          const rawLabel = labels[pileIdx] ?? "";
          const label = rawLabel.trim() === "" ? "" : rawLabel;
          const displayLabel = label === "" ? null : truncate(label, labelMaxChars);
          const isCardHighlighted = cardHighlightedPile.has(pileIdx);

          return (
            <div
              key={pileIdx}
              className={[
                "pile-comparison__pile-card",
                isCardHighlighted ? "pile-comparison__pile-card--highlight" : "",
              ].filter(Boolean).join(" ")}
            >
              {/* Pile label */}
              <span
                className={[
                  "pile-comparison__pile-label",
                  displayLabel === null ? "pile-comparison__pile-label--empty" : "",
                ].filter(Boolean).join(" ")}
                title={label || PILE_COMPARISON_NO_LABEL}
              >
                {displayLabel ?? PILE_COMPARISON_NO_LABEL}
              </span>

              {/* Term pills */}
              <div className="pile-comparison__terms">
                {pile.map((term) => {
                  const stability = term_stability[term];
                  const sClass = stabilityClass(stability);
                  const isHighlighted = hoveredTerm === term;
                  const stabilityPct =
                    stability !== undefined && stability !== null
                      ? Math.round(stability * 100)
                      : null;
                  const tooltipText =
                    stabilityPct !== null
                      ? PILE_COMPARISON_STABILITY_TOOLTIP(stabilityPct, shortName)
                      : PILE_COMPARISON_STABILITY_TOOLTIP_UNAVAILABLE(shortName);

                  const pillClasses = [
                    "pile-comparison__pill",
                    sClass,
                    isHighlighted ? "pile-comparison__pill--highlight" : "",
                  ].filter(Boolean).join(" ");

                  return (
                    <span
                      key={term}
                      className={pillClasses}
                      tabIndex={0}
                      role="button"
                      title={tooltipText}
                      aria-label={`${term} — ${tooltipText}`}
                      onMouseEnter={() => onTermHover(term)}
                      onMouseLeave={() => onTermHover(null)}
                      onFocus={() => onTermHover(term)}
                      onBlur={() => onTermHover(null)}
                    >
                      {term}
                    </span>
                  );
                })}

                {/* Absent-term placeholder: show in FIRST pile card only
                    (DESIGN_SYSTEM.md §12.10 binding) when hoveredTerm is
                    set, is in allTermsAcrossModels, and NOT in this model */}
                {pileIdx === sortedPileIndices[0] &&
                  hoveredTerm !== null &&
                  allTermsAcrossModels.has(hoveredTerm) &&
                  !ownTerms.has(hoveredTerm) && (
                    <span
                      className="pile-comparison__pill pile-comparison__pill--absent"
                      title={PILE_COMPARISON_ABSENT_TOOLTIP(shortName)}
                      aria-label={PILE_COMPARISON_ABSENT_TOOLTIP(shortName)}
                    >
                      {PILE_COMPARISON_ABSENT_TERM_LABEL}
                    </span>
                  )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
