/**
 * Dashboard analysis configuration constants.
 * Source of truth: DESIGN_SYSTEM.md §3.3.5 item 7.
 *
 * These constants are imported by component code. The methodology page
 * reads the corresponding values from the published JSON manifest
 * (manifest.oci_low_concentration_threshold) at build time.
 *
 * No component may reference 3.0 as a numeric literal for the OCI threshold.
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
