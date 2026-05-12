/**
 * Dashboard analysis configuration constants.
 * Source of truth: DESIGN_SYSTEM.md §3.3.5 item 7 (OCI threshold) and §12.8 (similarity null).
 *
 * These constants are imported by component code. The methodology page
 * reads the corresponding values from the published JSON manifest
 * (manifest.oci_low_concentration_threshold) at build time.
 *
 * No component may reference 3.0 as a numeric literal for the OCI threshold.
 * No component may reference 0.5 as a numeric literal for the similarity null.
 * All threshold comparisons must import from this module.
 */

/**
 * OCI threshold below which a model's Register-2 ellipse is suppressed (R1-b state).
 *
 * A model with OCI < OCI_LOW_CONCENTRATION_THRESHOLD AND deterministic_output == false
 * renders without a confidence ellipse: the point is shown with a dashed 2px stroke
 * at 60% fill opacity (R1-b visual treatment per DESIGN_SYSTEM.md §3.3.5).
 *
 * This value is provisional pending the Phase 4b saturation analysis.
 * The published manifest carries this value as `oci_low_concentration_threshold`.
 * Tuning it after Phase 4b only requires changing the manifest + this constant —
 * no component logic changes needed.
 *
 * Source: DESIGN_SYSTEM.md §3.3.5 item 7.
 */
export const OCI_LOW_CONCENTRATION_THRESHOLD = 3.0;

/**
 * Cross-model similarity null value.
 *
 * The LSB cross-model similarity is a Mantel-style Pearson correlation between
 * two models' co-occurrence vectors on the shared item set, rescaled to [0, 1]
 * via `scaled = (r + 1.0) / 2.0`. Under this rescaling, Pearson r = 0 (linearly
 * uncorrelated, the formal null) maps to exactly 0.5.
 *
 * A cell's CI "crosses null" when `ci_lower < SIMILARITY_NULL_VALUE < ci_upper`.
 * Such cells receive the dashed-border treatment in SimilarityHeatmap (§4.5 binding).
 *
 * CDA SME approved (PASS): docs/status/2026-05-12-phase6-T5-cda-sme-verdict.md §5.1.
 * Source: DESIGN_SYSTEM.md §2.3 (T5 plan), cdb_analyze/mds.py line 74.
 */
export const SIMILARITY_NULL_VALUE = 0.5;
