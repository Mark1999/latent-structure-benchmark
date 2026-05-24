/**
 * DendrogramTable — accessible table representation of dendrogram cluster data.
 *
 * Phase 9a T7. Implements the ReadAsTableToggle U1 pattern (table always in DOM,
 * aria-hidden + display:none when inactive).
 *
 * Column spec (from UI/UX verdict):
 *   Cluster | Term | Subtree depth | Bootstrap support (%)
 *
 * Sort: cluster → term lexicographic (ascending).
 *
 * Forbidden vocabulary: no "worldview", "believes", "thinks", "understands"
 * applied to models per CLAUDE.md §7 and ARCHITECTURE.md §1.5.4.
 *
 * Reference:
 *   DESIGN_SYSTEM.md v0.5.2 (Phase 9a T7 visual spec)
 *   docs/status/2026-05-24-phase9a-T6T7-ui-ux-verdict.md
 */

// ── Types ────────────────────────────────────────────────────────────────────

export interface DendrogramTableRow {
  cluster: string;
  term: string;
  subtreeDepth: number;
  bpSupport: number | null;
}

export interface DendrogramTableProps {
  rows: DendrogramTableRow[];
  domainSlug: string;
}

// ── Caption ──────────────────────────────────────────────────────────────────

function tableCaption(domainSlug: string): string {
  return `Hierarchical cluster assignments for ${domainSlug} domain terms. Each row shows a term, its cluster, its depth in the tree, and the bootstrap support (percentage of resamples where this grouping was stable). Lower bootstrap support means a less stable grouping.`;
}

// ── Component ─────────────────────────────────────────────────────────────────

export function DendrogramTable({ rows, domainSlug }: DendrogramTableProps) {
  if (rows.length === 0) {
    return (
      <p style={{ color: "var(--color-text-caption)", fontSize: "var(--font-size-xs)" }}>
        No cluster data available for this domain.
      </p>
    );
  }

  // Sort: cluster label lexicographic, then term lexicographic within cluster.
  const sorted = [...rows].sort((a, b) => {
    const cmp = a.cluster.localeCompare(b.cluster);
    if (cmp !== 0) return cmp;
    return a.term.localeCompare(b.term);
  });

  return (
    <table
      style={{ borderCollapse: "collapse", fontSize: "var(--font-size-xs)", width: "100%", maxWidth: "var(--max-chart-width)" }}
      aria-label={`Hierarchical cluster table for ${domainSlug}`}
    >
      <caption
        style={{
          textAlign: "left",
          fontSize: "var(--font-size-xs)",
          color: "var(--color-text-caption)",
          paddingBottom: "var(--space-2)",
          captionSide: "top",
        }}
      >
        {tableCaption(domainSlug)}
      </caption>
      <thead>
        <tr>
          {(["Cluster", "Term", "Subtree depth", "Bootstrap support (%)"] as const).map((header) => (
            <th
              key={header}
              scope="col"
              style={{
                padding: "4px 8px",
                border: "1px solid var(--color-border)",
                background: "var(--color-surface)",
                fontWeight: "var(--font-weight-medium)",
                textAlign: "left",
                color: "var(--color-text-primary)",
              }}
            >
              {header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {sorted.map((row, i) => (
          <tr key={`${row.cluster}-${row.term}-${i}`}>
            <td style={{ padding: "4px 8px", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}>
              {row.cluster}
            </td>
            <td style={{ padding: "4px 8px", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}>
              {row.term}
            </td>
            <td style={{ padding: "4px 8px", border: "1px solid var(--color-border)", color: "var(--color-text-primary)", textAlign: "right" }}>
              {row.subtreeDepth}
            </td>
            <td style={{ padding: "4px 8px", border: "1px solid var(--color-border)", color: "var(--color-text-primary)", textAlign: "right" }}>
              {row.bpSupport !== null ? `${(row.bpSupport * 100).toFixed(0)}%` : "—"}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
