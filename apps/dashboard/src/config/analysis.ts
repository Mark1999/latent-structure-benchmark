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
 * Similarity null value for the Mantel-style cross-model correlation.
 *
 * Derivation: cdb_analyze/mds.py L74 rescales Pearson r to [0,1] via
 * scaled = (r + 1.0) / 2.0.  Pearson r = 0 (linearly uncorrelated, i.e. no
 * shared co-occurrence structure) maps to exactly 0.5 after rescaling.
 * This is the formal Mantel null, not a midpoint heuristic.
 * Reference: ARCHITECTURE.md §4.2.2 (cross-model similarity statistic).
 *
 * A cell whose 95% bootstrap CI crosses this value (ci[0] < 0.5 < ci[1],
 * strict inequalities) is rendered with a dashed border per DESIGN_SYSTEM.md
 * §12.8 and CLAUDE.md §6 rule 10 (R10 uncertainty disclosure).
 */
export const SIMILARITY_NULL_VALUE = 0.5;

/**
 * Dendrogram bootstrap support threshold.
 * Internal nodes with BP below this value get dashed branches and a numeric
 * annotation. Value 0.70 = 70% bootstrap proportion.
 * Reference: Reviewer verdict docs/status/2026-05-24-phase9a-T6T7-reviewer-verdict.md
 */
export const DENDROGRAM_SUPPORT_THRESHOLD = 0.70;

/**
 * Focus 1 — Output Concentration Index tier thresholds.
 * OCI >= OCI_CONCENTRATED_THRESHOLD → "concentrated" tier badge.
 * OCI >= OCI_MODERATE_THRESHOLD (and < concentrated) → "moderate" tier badge.
 * OCI < OCI_MODERATE_THRESHOLD → "diffuse" tier badge.
 * Source: DESIGN_SYSTEM.md §13.4
 */
export const OCI_CONCENTRATED_THRESHOLD = 50;
export const OCI_MODERATE_THRESHOLD = 10;
