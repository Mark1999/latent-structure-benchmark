// apps/dashboard/src/copy/pile_comparison.ts
//
// Single source of truth for all visible UI strings in PileComparison.
//
// CDA SME Decision 7 (M7) binding: no model is ground truth.
// §1.5.4 forbidden vocabulary: all strings have been scanned and are clean.
// No "worldview", "believes", "thinks" (model-applied), "sees", "understands",
// "missing", "placeholder", "no data yet", "pending" per CLAUDE.md §7.
//
// Phase 9a T9.
// Gate verdicts:
//   CDA SME PASS-WITH-NOTES: docs/status/2026-05-24-phase9a-cda-sme-verdict.md
//   UI/UX PASS-WITH-NOTES:   docs/status/2026-05-24-phase9a-T9-ui-ux-verdict.md

/** Description paragraph shown above the column grid (journalist test N2). */
export function PILE_COMPARISON_DESCRIPTION(domain: string): string {
  return `How models organize ${domain} vocabulary into categories: each column shows one model's groupings from its most representative run. Hover any term to see where it appears across models.`;
}

/** Empty state: zero models selected. */
export function PILE_COMPARISON_EMPTY_NO_MODELS(domain: string): string {
  return `Select one or more models to see how they structure ${domain} terms.`;
}

/** Empty state: no pile data for selected models in this domain. */
export const PILE_COMPARISON_EMPTY_NO_DATA =
  "Pile structure data is not available for the selected models in this domain.";

/** Absent-term placeholder pill text (shown on hover only). */
export const PILE_COMPARISON_ABSENT_TERM_LABEL = "(absent)";

/**
 * Tooltip for absent-term placeholder pills.
 * Shown when a term from another column is not present in this model.
 */
export function PILE_COMPARISON_ABSENT_TOOLTIP(modelShortName: string): string {
  return `This term was not produced by ${modelShortName} in this domain.`;
}

/**
 * Stability tooltip on every term pill.
 * N is the percentage (0–100, integer), modelShortName is the model display name.
 */
export function PILE_COMPARISON_STABILITY_TOOLTIP(n: number, modelShortName: string): string {
  return `Placed here in ${n}% of runs for ${modelShortName}.`;
}

/** Pile label fallback when no label was recorded. */
export const PILE_COMPARISON_NO_LABEL = "(no label)";

/** Legend heading text. */
export const PILE_COMPARISON_LEGEND_LABEL = "Term stability:";

/** Legend tier labels. */
export const PILE_COMPARISON_LEGEND_SOLID = "≥80% of runs";
export const PILE_COMPARISON_LEGEND_DASHED_MEDIUM = "60–79%";
export const PILE_COMPARISON_LEGEND_DASHED_LOW = "below 60%";

/** ReadAsTable accessibility table caption. */
export function PILE_COMPARISON_TABLE_CAPTION(domain: string): string {
  return `How models categorize ${domain} terms: pile assignments from each model's centroid run. Stability indicates how often each placement appeared across runs.`;
}

/** Column headers for the accessible table. */
export const PILE_COMPARISON_TABLE_COL_MODEL = "Model";
export const PILE_COMPARISON_TABLE_COL_PILE = "Pile label";
export const PILE_COMPARISON_TABLE_COL_TERM = "Term";
export const PILE_COMPARISON_TABLE_COL_STABILITY = "Stability (%)";

/** Empty row placeholder for accessible table when no data is present. */
export const PILE_COMPARISON_TABLE_EMPTY = "No pile structure data available.";

/** VizSwitcher tab label. */
export const PILE_COMPARISON_TAB_LABEL = "Pile Structure";

/** Screen-reader-only heading for the pile comparison section. */
export const PILE_COMPARISON_SR_HEADING = "Pile structure comparison";

/** Aria-label for the mobile model-switcher radiogroup. */
export const PILE_COMPARISON_MODEL_SWITCHER_ARIA_LABEL = "Select model to view";

/** Tooltip fallback when stability data is not available for a model. */
export function PILE_COMPARISON_STABILITY_TOOLTIP_UNAVAILABLE(modelShortName: string): string {
  return `Stability data not available for ${modelShortName}.`;
}
