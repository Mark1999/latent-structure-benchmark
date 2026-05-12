/**
 * SimilarityTable — flat 3-column tuple table for pairwise similarity data.
 *
 * Phase 6 T8. One row per unique unordered pair of selected models (N*(N-1)/2 rows).
 * Self-similarity diagonal rows excluded.
 *
 * R10 compliance (CLAUDE.md §6 R10 / ARCHITECTURE.md §4.5):
 *   Every similarity value (point estimate) has adjacent 95% CI columns.
 *   Null-CI cells render — (first-class state per §1.5.5).
 *
 * Table caption per CDA SME §4.3 binding (cross-surface with T5 "no shared structure"):
 *   "Each row compares two models in the current selection. The similarity column shows
 *   how similarly the two models organize this domain (1.00 = identical organization;
 *   0.50 = no shared structure); the 95% confidence interval columns show the bootstrap
 *   range around that value. Rows showing — under the confidence interval columns have
 *   no bootstrap interval available."
 *
 * Sort order: Model A short-name ascending, then Model B short-name ascending.
 * Index translation: uses modelIndexMap (same as SimilarityHeatmap §2.8).
 *
 * FORBIDDEN: "agree", "agrees with", "thinks like" per CDA SME S3.
 *
 * Type note: data/types.ts disagrees with live JSON — uses cast-through-unknown.
 *   T14 doc-sweep will reconcile types.ts.
 *
 * Does NOT touch data/types.ts (AC #19).
 * Does NOT import any LLM client (CLAUDE.md §6 R11).
 *
 * Reference:
 *   docs/status/2026-05-12-phase6-T8-architect-plan.md §2.3.3
 *   docs/status/2026-05-12-phase6-T8-cda-sme-verdict.md §4.3, S3, S5, S7
 */

import { useMemo } from "react";
import type { DomainResultPublished } from "../data/types";
import { modelShortName } from "../lib/modelShortName";
import {
  SIMILARITY_TABLE_CAPTION,
  SIMILARITY_TABLE_EMPTY_LT_2_MODELS,
} from "../copy/screen_reader_summaries";
import "../styles/read-as-table.css";

// Cast-through-unknown types matching actual JSON (T14 doc-sweep concern)
type SimilarityMatrix = number[][];
type SimilarityCiMatrix = Array<Array<[number, number] | null>>;

export interface SimilarityTableProps {
  domainResult: DomainResultPublished;
  selectedModels: string[];
}

export function SimilarityTable({
  domainResult,
  selectedModels,
}: SimilarityTableProps) {
  // Cast-through-unknown: types.ts disagrees with actual JSON (T14 doc-sweep)
  const rawSimilarityMatrix = domainResult.similarity_matrix as unknown as SimilarityMatrix;
  const rawSimilarityCi = domainResult.similarity_ci as unknown as SimilarityCiMatrix;

  // Build modelIndexMap: model_id → index in domainResult.models array
  // (same pattern as SimilarityHeatmap plan §2.8).
  // All hooks must be called before any early returns (React rules-of-hooks).
  const modelIndexMap = useMemo((): Map<string, number> => {
    const map = new Map<string, number>();
    domainResult.models.forEach((m, i) => {
      map.set(m.model_id, i);
    });
    return map;
  }, [domainResult.models]);

  // displayedIds: selectedModels sorted lexicographically (matches SimilarityHeatmap)
  const displayedIds = useMemo((): string[] => {
    return [...selectedModels].sort();
  }, [selectedModels]);

  // Build all unique unordered pairs (i < j, no diagonal)
  // Sort order: by Model A short-name ascending, then Model B short-name ascending.
  // Empty when selectedModels.length < 2 (guarded by early return below).
  const pairs = useMemo(() => {
    if (selectedModels.length < 2) return [];

    const result: Array<{
      idA: string;
      idB: string;
      shortNameA: string;
      shortNameB: string;
      similarity: number;
      ciLow: string;
      ciHigh: string;
    }> = [];

    for (let i = 0; i < displayedIds.length; i++) {
      for (let j = i + 1; j < displayedIds.length; j++) {
        const idA = displayedIds[i];
        const idB = displayedIds[j];
        const matI = modelIndexMap.get(idA) ?? 0;
        const matJ = modelIndexMap.get(idB) ?? 0;
        const sim = rawSimilarityMatrix[matI]?.[matJ] ?? 0;
        const ci: [number, number] | null = rawSimilarityCi?.[matI]?.[matJ] ?? null;

        result.push({
          idA,
          idB,
          shortNameA: modelShortName(idA),
          shortNameB: modelShortName(idB),
          similarity: sim,
          ciLow: ci !== null ? ci[0].toFixed(3) : "—",
          ciHigh: ci !== null ? ci[1].toFixed(3) : "—",
        });
      }
    }

    // Sort by Model A short-name ascending, then Model B short-name ascending
    result.sort((a, b) => {
      const cmpA = a.shortNameA.localeCompare(b.shortNameA);
      if (cmpA !== 0) return cmpA;
      return a.shortNameB.localeCompare(b.shortNameB);
    });

    return result;
  }, [displayedIds, modelIndexMap, rawSimilarityMatrix, rawSimilarityCi, selectedModels.length]);

  // Early return after all hooks — React rules-of-hooks compliance
  if (selectedModels.length < 2) {
    return (
      <p className="read-as-table__empty">{SIMILARITY_TABLE_EMPTY_LT_2_MODELS}</p>
    );
  }

  return (
    <div className="read-as-table__container">
      <table className="read-as-table__table">
        <caption className="read-as-table__caption">{SIMILARITY_TABLE_CAPTION}</caption>
        <thead>
          <tr>
            {/* CDA SME S9: all headers approved as proposed */}
            <th scope="col" className="read-as-table__th">Model A</th>
            <th scope="col" className="read-as-table__th">Model B</th>
            {/* Point estimate */}
            <th scope="col" className="read-as-table__th read-as-table__th--numeric">Similarity</th>
            {/* R10 pairing — CI columns adjacent to similarity */}
            <th scope="col" className="read-as-table__th read-as-table__th--numeric">95% CI low</th>
            <th scope="col" className="read-as-table__th read-as-table__th--numeric">95% CI high</th>
          </tr>
        </thead>
        <tbody>
          {pairs.map(({ idA, idB, shortNameA, shortNameB, similarity, ciLow, ciHigh }) => (
            <tr key={`${idA}-${idB}`} className="read-as-table__tr">
              <td className="read-as-table__td">{shortNameA}</td>
              <td className="read-as-table__td">{shortNameB}</td>
              <td className="read-as-table__td read-as-table__td--numeric">
                {similarity.toFixed(3)}
              </td>
              <td className="read-as-table__td read-as-table__td--numeric">{ciLow}</td>
              <td className="read-as-table__td read-as-table__td--numeric">{ciHigh}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
