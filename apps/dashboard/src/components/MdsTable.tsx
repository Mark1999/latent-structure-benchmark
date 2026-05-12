/**
 * MdsTable — accessible HTML table rendering of MDS coordinates + uncertainty.
 *
 * Phase 6 T8. Renders one row per selected model with R10-paired columns:
 * (x, y) point estimates adjacent to (semi-major, semi-minor, rotation, n_bootstrap).
 *
 * R10 compliance (CLAUDE.md §6 R10 / ARCHITECTURE.md §4.5):
 *   Every (x, y) row has uncertainty columns in the same row.
 *   R1-b / R1-c models render — in the ellipse columns (first-class state per §1.5.5).
 *
 * Column headers per CDA SME S9 binding revisions:
 *   "Uncertainty mode" → "Output concentration"
 *   "n_bootstrap" → "Bootstrap samples"
 *   "Rotation (rad)" → "Rotation angle"
 *   All other headers approved as proposed.
 *
 * Type note: data/types.ts disagrees with live JSON — uses cast-through-unknown.
 *   T14 doc-sweep will reconcile types.ts.
 *
 * Forbidden vocabulary: no "worldview", "believes", "thinks", "missing",
 *   "placeholder", "no data yet", "pending" per CLAUDE.md §7.
 *
 * Does NOT touch data/types.ts (AC #19).
 * Does NOT import any LLM client (CLAUDE.md §6 R11).
 *
 * Reference:
 *   docs/status/2026-05-12-phase6-T8-architect-plan.md §2.3.1
 *   docs/status/2026-05-12-phase6-T8-cda-sme-verdict.md §4.1, S6, S9
 */

import type { DomainResultPublished } from "../data/types";
import { modelShortName } from "../lib/modelShortName";
import {
  MDS_TABLE_CAPTION,
  MDS_TABLE_EMPTY_NO_MODELS,
} from "../copy/screen_reader_summaries";
import "../styles/read-as-table.css";

// Cast-through-unknown types matching actual JSON (T14 doc-sweep concern)

interface MdsUncertaintyActual {
  center?: [number, number];
  semi_major: number | null;
  semi_minor: number | null;
  rotation_rad: number | null;
  n_bootstrap: number | null;
  ci_level?: number | null;
}

export interface MdsTableProps {
  domainResult: DomainResultPublished;
  selectedModels: string[];
  /** model_id → CSS color value from DataExplorer §12.4 */
  modelColors: Record<string, string>;
}

export function MdsTable({
  domainResult,
  selectedModels,
}: MdsTableProps) {
  if (selectedModels.length === 0) {
    return (
      <p className="read-as-table__empty">{MDS_TABLE_EMPTY_NO_MODELS}</p>
    );
  }

  // Cast-through-unknown: types.ts disagrees with actual JSON (T14 doc-sweep)
  const rawCoords = domainResult.mds_coordinates as unknown as Record<
    string,
    [number, number]
  >;
  const rawUncertainty = domainResult.mds_uncertainty as unknown as Record<
    string,
    MdsUncertaintyActual | null
  >;
  const r1States =
    (domainResult.display?.r1_states as Record<string, string> | undefined) ?? {};

  // Sort order: lexicographic by model_id (stable, deterministic — per plan §2.3.1)
  const sortedModels = [...selectedModels].sort();

  // Map R1 state to "Output concentration" column cell value (CDA SME S9)
  function outputConcentrationLabel(r1State: string | undefined): string {
    switch (r1State) {
      case "typical_concentration":
        return "typical";
      case "low_concentration":
        return "low";
      case "deterministic":
        return "deterministic";
      default:
        return "typical";
    }
  }

  // Determine if a model has an ellipse (R1-a only)
  function hasEllipse(modelId: string): boolean {
    const state = r1States[modelId];
    return state === "typical_concentration" || state === undefined;
  }

  return (
    <div className="read-as-table__container">
      <table className="read-as-table__table">
        <caption className="read-as-table__caption">{MDS_TABLE_CAPTION}</caption>
        <thead>
          <tr>
            {/* CDA SME S9: all headers approved; "model_id" kept as-is (exempt per plan §1 dir 4) */}
            <th scope="col" className="read-as-table__th">Model</th>
            <th scope="col" className="read-as-table__th read-as-table__th--mono">model_id</th>
            <th scope="col" className="read-as-table__th read-as-table__th--numeric">x</th>
            <th scope="col" className="read-as-table__th read-as-table__th--numeric">y</th>
            {/* CDA SME S9: "Uncertainty mode" → "Output concentration" */}
            <th scope="col" className="read-as-table__th">Output concentration</th>
            {/* R10 pairing — ellipse columns adjacent to x/y */}
            <th scope="col" className="read-as-table__th read-as-table__th--numeric">Semi-major</th>
            <th scope="col" className="read-as-table__th read-as-table__th--numeric">Semi-minor</th>
            {/* CDA SME S9: "Rotation (rad)" → "Rotation angle" */}
            <th scope="col" className="read-as-table__th read-as-table__th--numeric">Rotation angle</th>
            {/* CDA SME S9: "n_bootstrap" → "Bootstrap samples" */}
            <th scope="col" className="read-as-table__th read-as-table__th--numeric">Bootstrap samples</th>
          </tr>
        </thead>
        <tbody>
          {sortedModels.map((modelId) => {
            const coords = rawCoords[modelId];
            const x = coords ? coords[0].toFixed(3) : "—";
            const y = coords ? coords[1].toFixed(3) : "—";
            const r1State = r1States[modelId];
            const concLabel = outputConcentrationLabel(r1State);
            const ellipse = rawUncertainty?.[modelId];
            const showEllipse = hasEllipse(modelId) && ellipse != null;

            const semiMajor = showEllipse && ellipse.semi_major != null
              ? ellipse.semi_major.toFixed(3)
              : "—";
            const semiMinor = showEllipse && ellipse.semi_minor != null
              ? ellipse.semi_minor.toFixed(3)
              : "—";
            const rotationAngle = showEllipse && ellipse.rotation_rad != null
              ? ellipse.rotation_rad.toFixed(3)
              : "—";
            const nBootstrap = showEllipse && ellipse.n_bootstrap != null
              ? String(ellipse.n_bootstrap)
              : "—";

            return (
              <tr key={modelId} className="read-as-table__tr">
                <td className="read-as-table__td">{modelShortName(modelId)}</td>
                <td className="read-as-table__td read-as-table__td--mono">{modelId}</td>
                <td className="read-as-table__td read-as-table__td--numeric">{x}</td>
                <td className="read-as-table__td read-as-table__td--numeric">{y}</td>
                <td className="read-as-table__td">{concLabel}</td>
                <td className="read-as-table__td read-as-table__td--numeric">{semiMajor}</td>
                <td className="read-as-table__td read-as-table__td--numeric">{semiMinor}</td>
                <td className="read-as-table__td read-as-table__td--numeric">{rotationAngle}</td>
                <td className="read-as-table__td read-as-table__td--numeric">{nBootstrap}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
