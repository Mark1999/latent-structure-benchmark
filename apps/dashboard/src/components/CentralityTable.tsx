/**
 * CentralityTable — accessible HTML table rendering of cultural centrality scores.
 */

function shortName(id: string): string {
  return id.split('/').pop() || id;
}

function mapConsensusType(type: string | undefined): string {
  if (!type) return 'no consensus data';
  return type.replace(/_/g, ' ').toLowerCase();
}

export interface CentralityTableProps {
  domainSlug: string;
  consensusType?: string;
  sortedIds: string[];
  centralityScores: Record<string, number>;
  centralityCis: Record<string, { lo: number; hi: number; n_bootstrap: number } | null>;
  hasCiData: boolean;
}

export function CentralityTable({
  domainSlug,
  consensusType,
  sortedIds,
  centralityScores,
  centralityCis,
  hasCiData,
}: CentralityTableProps) {
  if (sortedIds.length === 0) {
    return (
      <p className="read-as-table__empty">
        Select one or more models to see the cultural centrality table.
      </p>
    );
  }

  const consensusPhrase = mapConsensusType(consensusType);
  const tableCaption = `Cultural centrality scores for models on the ${domainSlug} domain. Higher scores indicate closer alignment with the group's dominant categorical pattern. Domain consensus: ${consensusPhrase}.`;

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
            const ci = hasCiData ? centralityCis[modelId] : null;

            return (
              <tr key={modelId} className="read-as-table__tr">
                <td className="read-as-table__td read-as-table__td--numeric">{rowIndex + 1}</td>
                <td className="read-as-table__td">{shortName(modelId)}</td>
                <td className="read-as-table__td read-as-table__td--mono">{modelId}</td>
                <td className="read-as-table__td read-as-table__td--numeric">
                  {score.toFixed(3)}
                </td>
                <td className="read-as-table__td read-as-table__td--numeric">
                  {ci !== null && ci !== undefined ? ci.lo.toFixed(3) : "—"}
                </td>
                <td className="read-as-table__td read-as-table__td--numeric">
                  {ci !== null && ci !== undefined ? ci.hi.toFixed(3) : "—"}
                </td>
                <td className="read-as-table__td read-as-table__td--numeric">
                  {ci !== null && ci !== undefined && ci.n_bootstrap !== undefined
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
