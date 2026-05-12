/**
 * FreeListTable — per-model accessible HTML tables for the FreeList view.
 *
 * Phase 6 T8. Renders one <table> per selected model, stacked vertically.
 * Each table shows terms sorted by Sutrop CSI descending (same sort as FreeListColumn).
 *
 * R10 compliance (CLAUDE.md §6 R10 / ARCHITECTURE.md §4.5):
 *   Each term's CSI (point estimate) is adjacent to its inclusion-frequency
 *   column (the same uncertainty the bar chart encodes).
 *
 * Table caption per CDA SME §4.2 binding (cross-surface with T7 N5.1):
 *   "${modelShortName}'s ranked terms for this domain, ordered by Sutrop salience score.
 *   The inclusion-frequency column shows the fraction of this model's collection runs
 *   that produced each term."
 *
 * Empty cases:
 *   Case A (no models selected): FREELIST_TABLE_EMPTY_NO_MODELS caption.
 *   Case B (no sutrop_csi for model): FREELIST_CASE_B_CAPTION below sub-table heading.
 *   Case C (empty sutrop_csi): FREELIST_CASE_C_CAPTION below sub-table heading.
 *
 * Heading hierarchy: h2 (sr-only, parent) → h3 (existing, parent) → h4 (per-model sub-table).
 * A2 (advisory): FreeListTable's <h4> per-model headings require <h3> parent. Verified:
 *   FreeListCompare already has sr-only h2; FreeListColumn uses h3; FreeListTable uses h4.
 *
 * Type note: data/types.ts disagrees with live JSON — uses cast-through-unknown.
 *   T14 doc-sweep will reconcile types.ts.
 *
 * Does NOT touch data/types.ts (AC #19).
 * Does NOT import any LLM client (CLAUDE.md §6 R11).
 *
 * Reference:
 *   docs/status/2026-05-12-phase6-T8-architect-plan.md §2.3.2
 *   docs/status/2026-05-12-phase6-T8-cda-sme-verdict.md §4.2, S5
 */

import { useMemo } from "react";
import type { DomainResultPublished } from "../data/types";
import { modelShortName } from "../lib/modelShortName";
import {
  freeListTableCaption,
  FREELIST_TABLE_EMPTY_NO_MODELS,
  FREELIST_CASE_B_CAPTION,
  FREELIST_CASE_C_CAPTION,
} from "../copy/screen_reader_summaries";
import "../styles/read-as-table.css";

// Cast-through-unknown types matching actual JSON (T14 doc-sweep concern)
interface SutropCsiItemActual {
  item: string;
  csi: number;
  f_mentions: number;
  n_runs: number;
  mean_position: number;
}

export interface FreeListTableProps {
  domainResult: DomainResultPublished;
  selectedModels: string[];
  /** model_id → CSS color value from DataExplorer §12.4 */
  modelColors: Record<string, string>;
}

export function FreeListTable({
  domainResult,
  selectedModels,
  modelColors,
}: FreeListTableProps) {
  // Cast-through-unknown: types.ts disagrees with actual JSON shape (T14 doc-sweep)
  const rawSutropCsi = domainResult.sutrop_csi as unknown as Record<
    string,
    Array<SutropCsiItemActual>
  >;

  /**
   * Per-model sorted term records.
   * null = Case B (no sutrop_csi data for this model)
   * [] = Case C (empty array)
   * populated = normal case
   *
   * Sort order per plan §2.3.2 (matches FreeListCompare):
   *   primary: csi descending
   *   tiebreak 1: mean_position ascending
   *   tiebreak 2: item lexicographic ascending (stable)
   */
  const termsByModel = useMemo((): Record<string, SutropCsiItemActual[] | null> => {
    const result: Record<string, SutropCsiItemActual[] | null> = {};
    for (const modelId of selectedModels) {
      const raw = rawSutropCsi?.[modelId];
      if (raw === undefined || raw === null) {
        result[modelId] = null; // Case B
      } else {
        const sorted = [...raw].sort((a, b) => {
          if (b.csi !== a.csi) return b.csi - a.csi;
          if (a.mean_position !== b.mean_position)
            return a.mean_position - b.mean_position;
          return a.item.localeCompare(b.item);
        });
        result[modelId] = sorted; // Case C (empty) or normal
      }
    }
    return result;
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [domainResult, selectedModels]);

  /**
   * Shared-terms set: terms that appear in ALL selected models with non-empty data.
   * Matches FreeListCompare's sharedTerms computation exactly.
   */
  const sharedTerms = useMemo((): Set<string> => {
    if (selectedModels.length < 2) return new Set();
    const termSets = selectedModels
      .map((id) => {
        const terms = termsByModel[id];
        if (!terms || terms.length === 0) return null;
        return new Set(terms.map((t) => t.item));
      })
      .filter((s): s is Set<string> => s !== null);

    if (termSets.length < 2) return new Set();

    const [first, ...rest] = termSets;
    const intersection = new Set<string>();
    for (const item of first) {
      if (rest.every((s) => s.has(item))) {
        intersection.add(item);
      }
    }
    return intersection;
  }, [termsByModel, selectedModels]);

  if (selectedModels.length === 0) {
    return (
      <p className="read-as-table__empty">{FREELIST_TABLE_EMPTY_NO_MODELS}</p>
    );
  }

  return (
    <div className="read-as-table__container">
      {selectedModels.map((modelId) => {
        const terms = termsByModel[modelId];
        const shortName = modelShortName(modelId);
        const color = modelColors[modelId] ?? "#888888";

        const isNoSalienceData = terms === null;
        const isNoTermsProduced = !isNoSalienceData && terms.length === 0;
        const hasTerms = !isNoSalienceData && terms.length > 0;

        return (
          <div key={modelId} className="read-as-table__model-section">
            {/* h4 sub-table heading: color dot + model name.
                Heading hierarchy: (h2 sr-only in FreeListCompare) → (h3 in FreeListColumn)
                T8 adds a parallel h4 here for the table sub-section.
                Plan §2.3.2: h4 with model-color dot + short name. */}
            <h4 className="read-as-table__model-heading">
              <span
                className="read-as-table__color-dot"
                style={{ backgroundColor: color }}
                aria-hidden="true"
              />
              {shortName}
            </h4>

            {/* Case B: no salience data */}
            {isNoSalienceData && (
              <p className="read-as-table__empty-inline">{FREELIST_CASE_B_CAPTION}</p>
            )}

            {/* Case C: no terms produced */}
            {isNoTermsProduced && (
              <p className="read-as-table__empty-inline">{FREELIST_CASE_C_CAPTION}</p>
            )}

            {/* Normal: render the table */}
            {hasTerms && (
              <table className="read-as-table__table">
                <caption className="read-as-table__caption">
                  {freeListTableCaption(shortName)}
                </caption>
                <thead>
                  <tr>
                    {/* CDA SME S9: approved as proposed */}
                    <th scope="col" className="read-as-table__th read-as-table__th--numeric">Rank</th>
                    <th scope="col" className="read-as-table__th">Term</th>
                    {/* Point estimate */}
                    <th scope="col" className="read-as-table__th read-as-table__th--numeric">Salience (CSI)</th>
                    {/* R10 pairing — inclusion-frequency adjacent to CSI */}
                    <th scope="col" className="read-as-table__th">Inclusion frequency</th>
                  </tr>
                </thead>
                <tbody>
                  {terms.map((record, index) => {
                    const isShared = sharedTerms.has(record.item);
                    const inclFreq = record.n_runs > 0
                      ? `${record.f_mentions} of ${record.n_runs} runs`
                      : "—";

                    return (
                      <tr key={record.item} className="read-as-table__tr">
                        <td className="read-as-table__td read-as-table__td--numeric">{index + 1}</td>
                        <td className="read-as-table__td">
                          {record.item}
                          {/* Shared-term glyph — matches FreeListCompare's ★ */}
                          {isShared && (
                            <span
                              className="read-as-table__shared-star"
                              aria-hidden="true"
                            >
                              {" "}★
                            </span>
                          )}
                        </td>
                        <td className="read-as-table__td read-as-table__td--numeric">
                          {record.csi.toFixed(2)}
                        </td>
                        <td className="read-as-table__td">{inclFreq}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        );
      })}
    </div>
  );
}
