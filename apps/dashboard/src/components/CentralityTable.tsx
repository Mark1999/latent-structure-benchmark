/**
 * CentralityTable — accessible HTML table rendering of cultural centrality scores.
 *
 * When centralityCi is provided, includes 95% CI lower and upper columns.
 * CIs are sourced from the published domain JSON (percentile bootstrap,
 * model-resampling, B=500). No per-model bootstrap N column is included
 * because the published shape is a bare [lo, hi] tuple with no per-model N.
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
  /** Per-model 95% bootstrap CI from published domain JSON. model_id → [lo, hi]. */
  centralityCi?: Record<string, [number, number]>;
}

export function CentralityTable({
  domainSlug,
  consensusType,
  sortedIds,
  centralityScores,
  centralityCi,
}: CentralityTableProps) {
  if (sortedIds.length === 0) {
    return (
      <p className="read-as-table__empty">
        Select one or more models to see the cultural centrality table.
      </p>
    );
  }

  const consensusPhrase = mapConsensusType(consensusType);
  const hasCi = Boolean(centralityCi && Object.keys(centralityCi).length > 0);

  const ciCaption = hasCi
    ? ' 95% CI columns show bootstrap confidence intervals (model-resampling with replacement, B=500, percentile method).'
    : '';
  const tableCaption = `Cultural centrality scores for models on the ${domainSlug} domain. Higher scores indicate closer alignment with the group's dominant categorical pattern. Domain consensus: ${consensusPhrase}.${ciCaption}`;

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
            {hasCi && (
              <>
                <th scope="col" className="read-as-table__th read-as-table__th--numeric">95% CI lower</th>
                <th scope="col" className="read-as-table__th read-as-table__th--numeric">95% CI upper</th>
              </>
            )}
            <th scope="col" className="read-as-table__th">Notes</th>
          </tr>
        </thead>
        <tbody>
          {sortedIds.map((modelId, rowIndex) => {
            const score = centralityScores[modelId] ?? 0;
            const isNegative = score < 0;
            const ci = centralityCi?.[modelId] ?? null;

            return (
              <tr key={modelId} className="read-as-table__tr">
                <td className="read-as-table__td read-as-table__td--numeric">{rowIndex + 1}</td>
                <td className="read-as-table__td">{shortName(modelId)}</td>
                <td className="read-as-table__td read-as-table__td--mono">{modelId}</td>
                <td className="read-as-table__td read-as-table__td--numeric">
                  {score.toFixed(3)}
                </td>
                {hasCi && (
                  <>
                    <td className="read-as-table__td read-as-table__td--numeric">
                      {ci ? ci[0].toFixed(3) : '—'}
                    </td>
                    <td className="read-as-table__td read-as-table__td--numeric">
                      {ci ? ci[1].toFixed(3) : '—'}
                    </td>
                  </>
                )}
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
