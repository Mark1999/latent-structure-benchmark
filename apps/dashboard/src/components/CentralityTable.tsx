/**
 * CentralityTable — accessible HTML table rendering of cultural centrality scores.
 *
 * Phase 9a T10. ReadAsTableToggle alternative for CentralityChart.
 *
 * R10 compliance (CLAUDE.md §6 R10 / ARCHITECTURE.md §4.5):
 *   Every row has centrality point estimate adjacent to CI columns.
 *   When CI data is absent, those columns render "—".
 *
 * Columns (T10 spec):
 *   Rank | Model | Centrality score | 95% CI lower | 95% CI upper | Bootstrap N | Notes
 *   All numeric columns: --font-mono, right-aligned.
 *   Notes: "negative centrality" if applicable, empty otherwise.
 *
 * Table caption per CDA SME M8 concepts:
 *   "Cultural centrality scores for models on the [domain] domain. Higher scores
 *    indicate closer alignment with the group's dominant categorical pattern.
 *    Domain consensus: [consensus_type]."
 *
 * Forbidden vocabulary: no "worldview", "believes", "thinks", "competence",
 *   "correctness" per CLAUDE.md §7. CDA SME approved concepts only.
 *
 * Does NOT touch data/types.ts. CLAUDE.md §6 R11: no LLM client imports.
 *
 * Reference:
 *   docs/status/2026-05-24-phase9a-viz-gap-kickoff.md
 *   docs/status/2026-05-24-phase9a-cda-sme-verdict.md §8 (M8)
 */

import type { DomainResultPublished } from "../data/types";
import { modelShortName } from "../lib/modelShortName";
import { mapConsensusType, CENTRALITY_TABLE_CAPTION } from "../copy/screen_reader_summaries";
import "../styles/read-as-table.css";

// ── Types ─────────────────────────────────────────────────────────────────────

type CentralityCiRaw =
  | Record<string, { lo: number; hi: number; n_bootstrap?: number } | [number, number] | null>
  | null;

// ── Helper: CI extraction ────────────────────────────────────────────────────

function extractCi(
  raw: { lo: number; hi: number; n_bootstrap?: number } | [number, number] | null | undefined
): { lo: number; hi: number; n_bootstrap?: number } | null {
  if (raw === null || raw === undefined) return null;
  if (Array.isArray(raw) && raw.length >= 2) {
    return { lo: raw[0] as number, hi: raw[1] as number };
  }
  if (typeof raw === "object" && !Array.isArray(raw)) {
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

// ── Props ─────────────────────────────────────────────────────────────────────

export interface CentralityTableProps {
  domainResult: DomainResultPublished;
  /** Models sorted descending by centrality score (pre-sorted by CentralityChart). */
  sortedIds: string[];
  centralityScores: Record<string, number>;
  centralityCiRaw: CentralityCiRaw;
  hasCiData: boolean;
}

// ── Component ─────────────────────────────────────────────────────────────────

export function CentralityTable({
  domainResult,
  sortedIds,
  centralityScores,
  centralityCiRaw,
  hasCiData,
}: CentralityTableProps) {
  if (sortedIds.length === 0) {
    return (
      <p className="read-as-table__empty">
        Select one or more models to see the cultural centrality table.
      </p>
    );
  }

  // Build caption from CDA SME-approved concepts (M8).
  const consensusPhrase = mapConsensusType(
    domainResult.consensus_type as string | null | undefined
  );
  const tableCaption = CENTRALITY_TABLE_CAPTION(
    domainResult.domain_slug,
    consensusPhrase
  );

  return (
    <div className="read-as-table__container">
      <table className="read-as-table__table">
        <caption className="read-as-table__caption">{tableCaption}</caption>
        <thead>
          <tr>
            <th scope="col" className="read-as-table__th read-as-table__th--numeric">Rank</th>
            <th scope="col" className="read-as-table__th">Model</th>
            <th scope="col" className="read-as-table__th read-as-table__th--mono">model_id</th>
            <th scope="col" className="read-as-table__th read-as-table__th--numeric">Centrality score</th>
            <th scope="col" className="read-as-table__th read-as-table__th--numeric">95% CI lower</th>
            <th scope="col" className="read-as-table__th read-as-table__th--numeric">95% CI upper</th>
            <th scope="col" className="read-as-table__th read-as-table__th--numeric">Bootstrap N</th>
            <th scope="col" className="read-as-table__th">Notes</th>
          </tr>
        </thead>
        <tbody>
          {sortedIds.map((modelId, rowIndex) => {
            const score = centralityScores[modelId] ?? 0;
            const isNegative = score < 0;

            const ciRaw =
              hasCiData && centralityCiRaw ? centralityCiRaw[modelId] : undefined;
            const ci = ciRaw !== undefined ? extractCi(ciRaw) : null;

            return (
              <tr key={modelId} className="read-as-table__tr">
                <td className="read-as-table__td read-as-table__td--numeric">{rowIndex + 1}</td>
                <td className="read-as-table__td">{modelShortName(modelId)}</td>
                <td className="read-as-table__td read-as-table__td--mono">{modelId}</td>
                <td className="read-as-table__td read-as-table__td--numeric">
                  {score.toFixed(3)}
                </td>
                <td className="read-as-table__td read-as-table__td--numeric">
                  {ci !== null ? ci.lo.toFixed(3) : "—"}
                </td>
                <td className="read-as-table__td read-as-table__td--numeric">
                  {ci !== null ? ci.hi.toFixed(3) : "—"}
                </td>
                <td className="read-as-table__td read-as-table__td--numeric">
                  {ci !== null && ci.n_bootstrap !== undefined
                    ? String(ci.n_bootstrap)
                    : "—"}
                </td>
                <td className="read-as-table__td">
                  {isNegative ? "negative centrality" : ""}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
