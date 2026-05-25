/**
 * Analysis configuration constants.
 *
 * These constants are the single source of truth for threshold values used
 * across visualization components. Component code must import from here;
 * never hardcode numeric literals that match these values.
 */

/** OCI low-concentration threshold. R1-b applies when oci < this value. */
export const OCI_LOW_CONCENTRATION_THRESHOLD = 3.0;

/**
 * Dendrogram bootstrap support threshold.
 * Internal nodes with BP below this value get dashed branches and a numeric
 * annotation. Value 0.70 = 70% bootstrap proportion.
 * Reference: Reviewer verdict docs/status/2026-05-24-phase9a-T6T7-reviewer-verdict.md
 */
export const DENDROGRAM_SUPPORT_THRESHOLD = 0.70;
