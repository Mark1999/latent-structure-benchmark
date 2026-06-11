/**
 * Consensus-type override disclosure strings.
 *
 * These constants are bound by CDA SME round-3 adjudication
 * (F3-R3-C and F3-R3-D) and must ship byte-identical.
 * Source: .claude/agent-memory/cda_sme/project_phase9b_food_guard_trip.md
 *
 * ANY edit to CI_DISCLOSURE_TEXT or SMALL_N_TEXT requires a fresh CDA SME pass.
 * PROMOTE-FOOD-V02 (2026-06-11).
 *
 * Implementation note on numeric sourcing (SME P1 / plan STOP-#5 resolution):
 * The eigenratio value '9.48' and the CI bracket '[4.91, 10.34]' in
 * CI_DISCLOSURE_TEXT are CONSTANTS, not computed from domain.consensus_ci
 * at runtime. There is no romney_eigenratio_ci schema field. These numbers
 * match the SME-bound F3-R3-C string byte-for-byte. The consensus_ci field
 * carries the CI on the consensus score (a different quantity).
 */

/**
 * F3-R3-C (binding, CDA SME verbatim).
 * CI disclosure line shown adjacent to the override badge whenever
 * domain.consensus_type_override is set.
 */
export const CI_DISCLOSURE_TEXT =
  "Romney CCM eigenratio 9.48, 95 percent bootstrap interval [4.91, 10.34], B=500. The interval crosses the 5.0 strong/weak threshold.";

/**
 * F3-R3-D (binding, CDA SME verbatim).
 * Small-n carry-forward line shown whenever domain.romney_small_n_warning is true.
 */
export const SMALL_N_TEXT =
  "The slate is 12 models, below the 15-model floor where Romney CCM eigenratios become statistically reliable. Read the classification with that floor in mind.";
