/**
 * Canonical framing constants for the LSB dashboard.
 * Source of truth: ARCHITECTURE.md §1.5
 *
 * IMPORTANT: Do not paraphrase these strings. They are the canonical
 * public-facing descriptions of what LSB measures, agreed to by the
 * CDA SME (plan-level PASS-WITH-NOTES, binding Q8 correction: US English
 * "categorize", not "categorise").
 *
 * Forbidden vocabulary (CLAUDE.md §7 / ARCHITECTURE.md §1.5.4):
 *   - Do not say "believes", "thinks", "worldview" about models.
 *   - Do not say "cultural bias" without a specified baseline.
 *   - Do not say "what the model understands".
 */

/**
 * The honest tagline — short form.
 * Used in: ArticleHeader subtitle, MethodologySummary, social posts, README first paragraph.
 * Source: ARCHITECTURE.md §1.5 (US English "categorize" per CDA SME plan-level Q8).
 */
export const TAGLINE =
  "LSB measures what frontier LLMs produce when asked to categorize, in a way that's reproducible, comparable across models, and trackable across time.";

/**
 * Long-form tagline for the methodology summary block.
 * Source: ARCHITECTURE.md §1.5.1 precise claim.
 */
export const TAGLINE_LONG =
  "The Latent Structure Benchmark applies Cultural Domain Analysis elicitation protocols to large language models as if they were informants, surfacing the corpus lens — the categorical structure a model's training data imposes on a domain, refracted through training and alignment. The originating question is exploratory: what happens if you give a large language model a CDA free-list or pile-sort? LSB answers that question precisely, reproducibly, and at scale across models and time, and releases the data for the community to interpret.";

/**
 * The plain-language term for what LSB measures.
 * Source: ARCHITECTURE.md §1.5.1.
 * Use in headlines, social posts, dashboard copy aimed at non-specialists.
 */
export const CORPUS_LENS_TERM = "corpus lens";

/**
 * Site name, for attribution and citation contexts.
 */
export const SITE_NAME = "Cognitive Structure Lab";

/**
 * Site URL.
 */
export const SITE_URL = "https://cogstructurelab.com";

/**
 * GitHub repository URL.
 */
export const GITHUB_URL = "https://github.com/cogstructurelab/lsb";

/**
 * Contact email.
 */
export const CONTACT_EMAIL = "contact@cogstructurelab.com";

/**
 * Data license.
 */
export const DATA_LICENSE = "CC BY 4.0";

/**
 * Code license.
 */
export const CODE_LICENSE = "Apache 2.0";
