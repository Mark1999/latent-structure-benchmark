/**
 * Focus 1 — Individual Model Consistency UI copy strings.
 *
 * All text about models must use Register 1 vocabulary:
 * "output concentration" not "consensus".
 * Source: DESIGN_SYSTEM.md §13.10 and §1.5.4 forbidden vocabulary rules.
 *
 * These strings are CDA SME-approved — do not paraphrase.
 */

// ===== Tab description paragraphs (§13.10) =====

/**
 * Self-Consistency tab description paragraph.
 * @param domainSlug - e.g. "family"
 */
export function selfConsistencyDescription(domainSlug: string): string {
  return (
    `How consistently each model organizes ${domainSlug} vocabulary across independent runs. ` +
    `The Output Concentration Index measures how concentrated the model's output distribution is — ` +
    `higher values mean the model produces nearly the same categorical structure each time.`
  );
}

/**
 * Run Distribution tab description paragraph.
 */
export const RUN_DISTRIBUTION_DESCRIPTION =
  'How similar each pair of runs is for the selected model. The agreement matrix and run map ' +
  'show whether the model produces stable or variable categorical structures across runs.';

/**
 * Term Stability tab description paragraph.
 */
export const TERM_STABILITY_DESCRIPTION =
  'How reliably each term appears in the same structural position across runs for the selected model. ' +
  'Terms that appear in 80% or more of runs in the same position are considered structurally stable.';

// ===== OCI display helpers (§13.5) =====

/**
 * Format OCI value with CI and n_runs context.
 * When oci_ci is provided: "X.XX (95% CI [X.XX, X.XX], N = XX runs)"
 * When null: "X.XX (N = XX runs; confidence interval unavailable at this run count)"
 */
export function formatOciDisplay(
  oci: number,
  ociCi: [number, number] | null,
  nRuns: number,
): string {
  const ociStr = oci.toFixed(2);
  if (ociCi !== null) {
    return `${ociStr} (95% CI [${ociCi[0].toFixed(2)}, ${ociCi[1].toFixed(2)}], N = ${nRuns} runs)`;
  }
  return `${ociStr} (N = ${nRuns} runs; confidence interval unavailable at this run count)`;
}

// ===== Bootstrap caveat text (§13.5) =====

/**
 * Info popover text for the ⓘ button next to OCI values.
 * Source: DESIGN_SYSTEM.md §13.5 referencing BOOTSTRAP_DESIGN.md §2.
 */
export const BOOTSTRAP_CAVEAT_TEXT =
  'Register 1 confidence intervals underestimate uncertainty because runs are correlated draws ' +
  'from the same model. See the methodology page for details.';

// ===== Empty state messages =====

export const EMPTY_NO_MODEL_SELECTED =
  'Select a model from the sidebar to see its run distribution.';

export const EMPTY_RUN_MAP_UNAVAILABLE = (nRuns: number): string =>
  `Run map unavailable: fewer than 5 runs recorded for this model (N = ${nRuns}).`;

export const EMPTY_NO_STABILITY_DATA =
  'Term stability data not available for this model.';

export const EMPTY_NO_FOCUS1_DATA =
  'Individual consistency data is not available for this domain.';
