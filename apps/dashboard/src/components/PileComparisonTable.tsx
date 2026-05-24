/**
 * PileComparisonTable — accessible table for PileComparison ReadAsTableToggle mode.
 *
 * Phase 9a T9. Implements the 4-column accessible table for pile structure data.
 *
 * Columns: Model | Pile label | Term | Stability (%)
 * Sort: model order → pile index → term lexicographic
 * Caption: PILE_COMPARISON_TABLE_CAPTION (from pile_comparison.ts)
 *
 * CDA SME M7 binding: all models listed with equal weight; no model is ground truth.
 *
 * Forbidden vocabulary: no "worldview", "believes", "thinks", "sees", "understands"
 * applied to models per CLAUDE.md §7 and ARCHITECTURE.md §1.5.4.
 *
 * Reference:
 *   docs/status/2026-05-24-phase9a-T9-ui-ux-verdict.md
 *   docs/status/2026-05-24-phase9a-cda-sme-verdict.md §7 (M7)
 *   DESIGN_SYSTEM.md v0.5.0
 */

import { useMemo } from "react";
import { modelShortName } from "../lib/modelShortName";
import {
  PILE_COMPARISON_TABLE_CAPTION,
  PILE_COMPARISON_TABLE_COL_MODEL,
  PILE_COMPARISON_TABLE_COL_PILE,
  PILE_COMPARISON_TABLE_COL_TERM,
  PILE_COMPARISON_TABLE_COL_STABILITY,
  PILE_COMPARISON_TABLE_EMPTY,
  PILE_COMPARISON_NO_LABEL,
} from "../copy/pile_comparison";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface ModelPileData {
  piles: string[][];
  labels: string[];
  term_stability: Record<string, number>;
}

export interface PileComparisonTableProps {
  domainSlug: string;
  selectedModels: string[];
  /** centroid_piles keyed by model_id; may be absent. */
  centroidPiles: Record<string, ModelPileData> | null | undefined;
}

// ── Component ─────────────────────────────────────────────────────────────────

export function PileComparisonTable({
  domainSlug,
  selectedModels,
  centroidPiles,
}: PileComparisonTableProps) {
  const caption = PILE_COMPARISON_TABLE_CAPTION(domainSlug);

  // Build rows: model → pile (by index) → term (lexicographic)
  const rows = useMemo(() => {
    if (!centroidPiles) return [];

    const result: Array<{
      modelId: string;
      modelShort: string;
      pileLabel: string;
      term: string;
      stabilityPct: number | null;
    }> = [];

    for (const modelId of selectedModels) {
      const pileData = centroidPiles[modelId];
      if (!pileData) continue;

      const { piles, labels, term_stability } = pileData;

      piles.forEach((pile, pileIndex) => {
        const label = labels[pileIndex] ?? "";
        const displayLabel = label.trim() === "" ? PILE_COMPARISON_NO_LABEL : label;

        // Sort terms within pile lexicographically
        const sortedTerms = [...pile].sort((a, b) => a.localeCompare(b));

        for (const term of sortedTerms) {
          const stability = term_stability[term];
          const stabilityPct =
            stability !== undefined && stability !== null
              ? Math.round(stability * 100)
              : null;

          result.push({
            modelId,
            modelShort: modelShortName(modelId),
            pileLabel: displayLabel,
            term,
            stabilityPct,
          });
        }
      });
    }

    return result;
  }, [selectedModels, centroidPiles]);

  return (
    <table className="pile-comparison-table">
      <caption className="pile-comparison-table__caption">{caption}</caption>
      <thead>
        <tr>
          <th scope="col">{PILE_COMPARISON_TABLE_COL_MODEL}</th>
          <th scope="col">{PILE_COMPARISON_TABLE_COL_PILE}</th>
          <th scope="col">{PILE_COMPARISON_TABLE_COL_TERM}</th>
          <th scope="col">{PILE_COMPARISON_TABLE_COL_STABILITY}</th>
        </tr>
      </thead>
      <tbody>
        {rows.length === 0 ? (
          <tr>
            <td colSpan={4}>{PILE_COMPARISON_TABLE_EMPTY}</td>
          </tr>
        ) : (
          rows.map((row, i) => (
            <tr key={`${row.modelId}-${i}`}>
              <td>{row.modelShort}</td>
              <td>{row.pileLabel}</td>
              <td>{row.term}</td>
              <td>
                {row.stabilityPct !== null ? `${row.stabilityPct}%` : "—"}
              </td>
            </tr>
          ))
        )}
      </tbody>
    </table>
  );
}
