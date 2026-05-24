/**
 * TermMDSTable — read-as-table rendering for TermMDSPlot.
 *
 * Phase 9a T6. Implements the ReadAsTableToggle table pattern (T8 §12.9).
 *
 * Columns: Term | Cluster | MDS X | MDS Y | CI semi-major | CI semi-minor |
 *          CI rotation (deg) | Bootstrap N
 *
 * Sort: cluster → term lexicographic (per spec).
 *
 * Caption: CDA SME-approved; do not alter without CDA SME re-approval.
 *
 * Reference:
 *   docs/status/2026-05-24-phase9a-viz-gap-kickoff.md T6
 *   DESIGN_SYSTEM.md v0.5.2 §11
 */

import type { DomainResultPublished } from "../data/types";
import { TERM_MDS_TABLE_CAPTION } from "../copy/screen_reader_summaries";

// ── Internal types shared with TermMDSPlot ──────────────────────────────────

interface UncertaintyParams {
  center: [number, number];
  semi_major: number;
  semi_minor: number;
  rotation_rad: number;
  n_bootstrap: number;
}

export interface TermPointData {
  term: string;
  x: number;
  y: number;
  clusterId: number;
  clusterLabel: string;
  color: string;
  uncertainty: UncertaintyParams | null;
}

// ── Props ───────────────────────────────────────────────────────────────────

export interface TermMDSTableProps {
  domainResult: DomainResultPublished;
  points: TermPointData[];
}

// ── Component ────────────────────────────────────────────────────────────────

export function TermMDSTable({ domainResult, points }: TermMDSTableProps) {
  if (points.length === 0) {
    return (
      <table>
        <caption>{TERM_MDS_TABLE_CAPTION(domainResult.domain_slug)}</caption>
        <thead>
          <tr>
            <th scope="col">Term</th>
            <th scope="col">Cluster</th>
            <th scope="col">MDS X</th>
            <th scope="col">MDS Y</th>
            <th scope="col">CI semi-major</th>
            <th scope="col">CI semi-minor</th>
            <th scope="col">CI rotation (deg)</th>
            <th scope="col">Bootstrap N</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td colSpan={8}>No term MDS data available for this domain.</td>
          </tr>
        </tbody>
      </table>
    );
  }

  // Sort: cluster id → term lexicographic
  const sortedPoints = [...points].sort((a, b) => {
    if (a.clusterId !== b.clusterId) return a.clusterId - b.clusterId;
    return a.term.localeCompare(b.term);
  });

  // Raw coordinates from domain JSON (for MDS X / MDS Y display)
  const rawCoords =
    (domainResult as unknown as { term_mds_coordinates?: Record<string, [number, number]> })
      .term_mds_coordinates ?? {};

  return (
    <table>
      <caption>{TERM_MDS_TABLE_CAPTION(domainResult.domain_slug)}</caption>
      <thead>
        <tr>
          <th scope="col">Term</th>
          <th scope="col">Cluster</th>
          <th scope="col">MDS X</th>
          <th scope="col">MDS Y</th>
          <th scope="col">CI semi-major</th>
          <th scope="col">CI semi-minor</th>
          <th scope="col">CI rotation (deg)</th>
          <th scope="col">Bootstrap N</th>
        </tr>
      </thead>
      <tbody>
        {sortedPoints.map((p) => {
          const raw = rawCoords[p.term];
          const rawX = raw ? raw[0] : null;
          const rawY = raw ? raw[1] : null;
          const u = p.uncertainty;
          return (
            <tr key={p.term}>
              <td>{p.term}</td>
              <td>{p.clusterLabel}</td>
              <td>{rawX !== null ? rawX.toFixed(4) : "—"}</td>
              <td>{rawY !== null ? rawY.toFixed(4) : "—"}</td>
              <td>{u ? u.semi_major.toFixed(4) : "—"}</td>
              <td>{u ? u.semi_minor.toFixed(4) : "—"}</td>
              <td>{u ? (u.rotation_rad * 180 / Math.PI).toFixed(1) : "—"}</td>
              <td>{u ? u.n_bootstrap : "—"}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
