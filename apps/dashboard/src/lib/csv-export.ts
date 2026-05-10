/**
 * CSV export — pure function for domain result data.
 *
 * Columns (§5 binding, DESIGN_SYSTEM.md v0.3 / v0.4.2):
 *   model_id, family, origin, mds_x, mds_y,
 *   semi_major, semi_minor, rotation_rad, n_bootstrap,
 *   oci, deterministic_output, r1_state
 *
 * Null-handling per §5: ellipse params (semi_major, semi_minor,
 * rotation_rad, n_bootstrap) are EMPTY STRING for R1-b and R1-c rows
 * (low_concentration or deterministic). The column headers document this
 * via the comment row at the top of the CSV.
 *
 * Source: docs/status/2026-05-09-phase5-architect-plan.md §4 T10
 *         DESIGN_SYSTEM.md §5 CSV export spec
 */

import type { DomainResultPublished } from "../data/types";

/** The 12 binding CSV columns in order. */
const CSV_HEADERS = [
  "model_id",
  "family",
  "origin",
  "mds_x",
  "mds_y",
  "semi_major",
  "semi_minor",
  "rotation_rad",
  "n_bootstrap",
  "oci",
  "deterministic_output",
  "r1_state",
] as const;

/**
 * Escape a value for CSV: wrap in double quotes if it contains
 * a comma, double quote, or newline. Escape internal double quotes
 * by doubling them (RFC 4180).
 */
function csvEscape(value: string): string {
  if (value.includes('"') || value.includes(",") || value.includes("\n") || value.includes("\r")) {
    return '"' + value.replace(/"/g, '""') + '"';
  }
  return value;
}

/**
 * Generate a CSV string for the current view.
 *
 * @param domainResult - The published domain result object.
 * @param selectedModels - The model_ids to include (one row each).
 * @returns CSV string with header row + one data row per selected model.
 */
export function domainResultToCsv(
  domainResult: DomainResultPublished,
  selectedModels: string[]
): string {
  const lines: string[] = [];

  // Comment row documenting null semantics (appears before the header).
  lines.push(
    "# semi_major/semi_minor/rotation_rad/n_bootstrap are empty for r1_state=low_concentration and r1_state=deterministic (no ellipse computed)"
  );

  // Header row.
  lines.push(CSV_HEADERS.map(csvEscape).join(","));

  // Build lookup maps.
  const modelMeta = new Map(domainResult.models.map((m) => [m.model_id, m]));
  const coords = domainResult.mds_coordinates as unknown as Record<string, [number, number]>;
  const uncertainty = domainResult.mds_uncertainty;
  const r1States = domainResult.display.r1_states;
  const withinModelMap = new Map(
    domainResult.within_model_results.map((w) => [w.model_id, w])
  );

  for (const modelId of selectedModels) {
    const meta = modelMeta.get(modelId);
    const coord = coords[modelId];
    const r1State = r1States[modelId] ?? "";
    const ellipse = uncertainty[modelId];
    const wmr = withinModelMap.get(modelId);

    // mds_x, mds_y
    const mds_x = coord !== undefined ? String(coord[0]) : "";
    const mds_y = coord !== undefined ? String(coord[1]) : "";

    // Ellipse params: empty string for R1-b (low_concentration) and R1-c (deterministic).
    const hasEllipse =
      r1State === "typical_concentration" && ellipse !== null && ellipse !== undefined;
    const semi_major = hasEllipse ? String(ellipse!.semi_major) : "";
    const semi_minor = hasEllipse ? String(ellipse!.semi_minor) : "";
    const rotation_rad = hasEllipse ? String(ellipse!.rotation_rad) : "";
    const n_bootstrap = hasEllipse ? String(ellipse!.n_bootstrap) : "";

    // OCI and deterministic_output from within_model_results.
    const oci = wmr !== undefined ? String(wmr.oci) : "";
    const deterministic_output =
      wmr !== undefined ? String(wmr.deterministic_output) : "";

    const row = [
      csvEscape(modelId),
      csvEscape(meta?.family ?? ""),
      csvEscape(meta?.origin ?? ""),
      mds_x,
      mds_y,
      semi_major,
      semi_minor,
      rotation_rad,
      n_bootstrap,
      oci,
      deterministic_output,
      csvEscape(r1State),
    ];

    lines.push(row.join(","));
  }

  return lines.join("\n");
}

/**
 * Trigger a CSV file download in the browser.
 *
 * @param csvString - The CSV content.
 * @param filename - Suggested filename (e.g. "lsb-family-0.2.csv").
 */
export function downloadCsv(csvString: string, filename: string): void {
  const blob = new Blob([csvString], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.style.display = "none";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
