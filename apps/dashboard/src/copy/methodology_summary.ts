// apps/dashboard/src/copy/methodology_summary.ts
//
// Single source of truth for the methodology summary block (T13).
// SME-approved on 2026-05-11; do not edit without CDA SME re-review.
// See docs/status/2026-05-11-phase5-T13-cda-sme-verdict.md.

import { TAGLINE } from "./framing";

/**
 * Methodology summary prose — rendered below the data explorer per
 * DESIGN_SYSTEM.md §2.1. Max-width 680px. Present-tense, OWID-style.
 *
 * Sources: ARCHITECTURE.md §1.5.1 (corpus-lens five-link chain),
 * §1.5.4 (language guardrails), §1.5.7 (exploratory framing),
 * §4.2.6 / §4.5 (bootstrap uncertainty).
 */
export const methodologySummary = `Cultural Domain Analysis (CDA) is a family of elicitation protocols developed in cognitive anthropology to recover how informants organize the items in a domain. LSB applies three of those protocols — free-list (what items belong in a domain), pile-sort (which items group together), and rating (how items rank on a given dimension) — to large language models, on identical prompts, as if each model were an informant. What this surfaces is the corpus lens: the categorical structure of the model's training data, refracted through training, alignment, decoding, and the output distribution that the model samples from. The map below positions each model by how its outputs categorize the domain relative to every other model in the slate; closer points indicate more similar categorical structure, and the shaded ellipses show the measurement uncertainty around each position from bootstrap resampling. Comparisons are model-to-model by design — every domain in v1 is a comparison across the model slate, not against a human reference — and the protocol is held fixed so differences in the map reflect differences between models rather than differences in how each was asked. The originating question is exploratory: what comes out when you give a large language model a CDA elicitation? LSB answers that question precisely, reproducibly, and at scale across models and time, and releases the verbatim prompts, the verbatim responses, and the analytical code so others can interpret the results on their own terms.`;

/**
 * Footnote — placeholder for the (Phase 6) full methodology page link.
 * Render conditionally: if the Phase 6 page URL is not yet live,
 * render the "coming in Phase 6" form; once the URL is set in
 * site config, swap to a live link. Use caption-token contrast
 * (--color-text-caption) per T10 precedent.
 */
export const methodologyFootnote = `A full methodology page — covering the CDA protocols in detail, the measures shown on the dashboard (Smith's S, Romney CCM, MDS, Procrustes, OCI), the bootstrap procedure, and academic credit to Romney, D'Andrade, Weller, Borgatti, and Batchelder — is coming in Phase 6.`;

/**
 * The verbatim tagline, re-exported here for inline placement at the
 * head of the methodology summary block. The canonical value lives in
 * copy/framing.ts; this re-export exists only so MethodologySummary.tsx
 * can import a single object. The Coder MUST verify at build time that
 * this string equals framing.TAGLINE (a unit test asserting equality
 * keeps the single-source-of-truth invariant honest).
 */
export const taglineQuote = TAGLINE;
