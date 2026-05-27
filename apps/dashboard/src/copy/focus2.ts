/**
 * Focus 2 — Within-Provider Family Comparison UI copy strings.
 *
 * All text about models must use Register 1 vocabulary.
 * Source: DESIGN_SYSTEM.md §14.10 and §14.13 forbidden vocabulary rules.
 * Forbidden: "provider consensus", "family agreement", "cluster of [provider] models".
 *
 * These strings are CDA SME-approved — do not paraphrase.
 */

// ===== Tab description paragraphs (§14.10) =====

/**
 * Overview tab description paragraph.
 */
export const FOCUS2_OVERVIEW_DESCRIPTION =
  'How models from the same provider compare. Within-family similarity shows whether models ' +
  'sharing a training pipeline produce similar categorical structures, or whether model tier ' +
  'and generation shift the output.';

/**
 * Similarity tab description paragraph.
 */
export const FOCUS2_SIMILARITY_DESCRIPTION =
  'Pairwise similarity between models from the selected provider family. The heatmap shows ' +
  'structural agreement between each pair of family members. The model map highlights family ' +
  'members in the full cross-model space.';

/**
 * Salience tab description paragraph.
 */
export const FOCUS2_SALIENCE_DESCRIPTION =
  'Term salience rankings for models from the selected provider family. Compare which terms ' +
  'each family member ranks as most prominent.';

/**
 * Piles tab description paragraph.
 */
export const FOCUS2_PILES_DESCRIPTION =
  'Pile structures from each family member\'s centroid run. Compare how models from the same ' +
  'provider group domain vocabulary.';

// ===== Empty state messages =====

/**
 * Shown when no provider is selected in Similarity/Salience/Piles tabs.
 */
export const FOCUS2_NO_PROVIDER_SELECTED =
  'Select a provider family from the Overview tab or the sidebar to see the comparison.';

/**
 * Shown for single-model families (CDA SME note 1 + §14.12).
 * Not a defect — this is a normal first-class state.
 */
export const FOCUS2_SINGLE_MODEL_NOTE =
  'Within-family comparison requires two or more models from the same provider.';

// ===== Cite path (§14.11) =====

/**
 * Source attribution line for Focus 2.
 * @param domainSlug - e.g. "family"
 * @param analysisVersion - e.g. "0.3"
 */
export function focus2SourceLine(domainSlug: string, analysisVersion: string): string {
  return `Within-family comparison: ${domainSlug}.json · Analysis: v${analysisVersion}`;
}
