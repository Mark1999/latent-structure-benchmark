/**
 * Consensus-type override disclosure strings.
 *
 * These constants are bound by CDA SME adjudication and must ship byte-identical.
 *
 * _V02 constants (F3-R3-C and F3-R3-D):
 *   Source: .claude/agent-memory/cda_sme/project_phase9b_food_guard_trip.md
 *   PROMOTE-FOOD-V02 (2026-06-11).
 *
 * _V03 constant (F3-V3-C):
 *   Source: docs/status/2026-07-13-batchA-promotion-cda-sme-verdict.md
 *   Batch A promotion (2026-07-13). Successor to CI_DISCLOSURE_TEXT_V02 for
 *   food v0.3 surfaces. ContentArea renders _V03; _V02 is retained for
 *   citation stability (any prior citation to v0.2 disclosure string is preserved).
 *
 * Naming convention (_V{NN} suffix, DESIGN_SYSTEM.md §23.2):
 *   Prior versioned constants are retained verbatim for citation stability.
 *   ContentArea always imports the highest-version constant in active use.
 *   Tests assert byte-identity per versioned constant independently.
 *
 * ANY edit to any constant requires a fresh CDA SME pass.
 *
 * Implementation note on numeric sourcing (SME P1 / STOP-#5 resolution):
 * The eigenratio values and CI brackets in these constants are CONSTANTS in
 * the copy module, not computed from domain.consensus_ci at runtime. There
 * is no romney_eigenratio_ci schema field. These numbers match the SME-bound
 * strings byte-for-byte. The consensus_ci field carries the CI on the
 * consensus score (a different quantity).
 */

/**
 * F3-R3-C (binding, CDA SME verbatim, food v0.2).
 * CI disclosure line for food v0.2 surfaces.
 * Retained verbatim for citation stability (DESIGN_SYSTEM.md §23.2).
 */
export const CI_DISCLOSURE_TEXT_V02 =
  "Romney CCM eigenratio 9.48, 95 percent bootstrap interval [4.91, 10.34], B=500. The interval crosses the 5.0 strong/weak threshold.";

/**
 * F3-V3-C (binding, CDA SME verbatim, food v0.3).
 * CI disclosure line shown adjacent to the override badge on food v0.3 surfaces.
 * Source: docs/status/2026-07-13-batchA-promotion-cda-sme-verdict.md ruling B.
 */
export const CI_DISCLOSURE_TEXT_V03 =
  "Romney CCM eigenratio 5.44, 95 percent bootstrap interval [2.75, 10.25], B=500. The interval crosses the 5.0 strong/weak threshold and the median replicate sits below it.";

/**
 * F3-R3-D (binding, CDA SME verbatim).
 * Small-n carry-forward line shown whenever domain.romney_small_n_warning is true.
 * KEEP DORMANT per SME ruling C: do not retire, do not version-suffix.
 */
export const SMALL_N_TEXT =
  "The slate is 12 models, below the 15-model floor where Romney CCM eigenratios become statistically reliable. Read the classification with that floor in mind.";
