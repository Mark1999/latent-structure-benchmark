/**
 * Copy strings for the Collection records tab (FailuresFindings component).
 *
 * All strings are CDA SME-approved (T9 §5.1 + T10 S1-S7, carried forward
 * verbatim under Phase 9a T1 re-affirmation verdict 2026-06-08).
 *
 * IMPORTANT: Do not paraphrase these strings. The byte-identity assertion
 * in FailuresFindings.test.tsx will catch deviations.
 *
 * Forbidden vocabulary (CLAUDE.md §7): worldview / believes / thinks /
 * "model failures" framing / cognition attribution. See M1-M4 (CDA SME verdict).
 */

// ===== Impact paragraph (v0.15.1 — CR-T1, 2026-06-10) =====

/**
 * Impact paragraph for the collection failures surface.
 * Mark-authored, approved verbatim 2026-06-10; CDA SME T1 gate PASS-WITH-NOTES.
 * Do NOT paraphrase. Byte-identity assertion in FailuresFindings.test.tsx enforces this.
 */
export const IMPACT_PARAGRAPH_FAILURES =
  "Some sessions do not produce a usable answer. A model declines, or returns something our pipeline cannot parse, or the request fails on the provider's side. We keep all of it. Which prompts a model will not answer, and how it says no, is as much a part of its behavior as the answers it gives. Deleting these records would make every model look equally cooperative, and that would be misleading. So they are published here, verbatim.";

// ===== NavBar tab label (N1 / CDA SME M1 Option A) =====

/** NavBar tab label — "Collection records" (CDA SME M1 Option A preferred). */
export const FAILURES_TAB_LABEL = "Collection records";

// ===== Page heading (CDA SME M2 / T10 SECTION_HEADING verbatim) =====

/** Primary heading rendered as <h1> inside the Collection records tab. */
export const SECTION_HEADING = "Collection records and follow-up interviews";

// ===== Badge labels (T10 S4a verbatim) =====

/** Badge label for failure records. Names LSB-pipeline outcome category. */
export const BADGE_FAILURE = "Collection failure";

/** Badge label for decline interview records. Names LSB-pipeline outcome category. */
export const BADGE_DECLINE = "Follow-up interview";

// ===== Block labels (T10 S4b + S6 verbatim) =====

/** Block label for the originating context section in expanded failure. */
export const BLOCK_ORIGINATING_CONTEXT = "Originating context";

/** Block label for the prompt LSB sent in a decline interview. */
export const BLOCK_PROMPT = "Follow-up prompt LSB sent";

/** Block label for model output to the follow-up prompt. */
export const BLOCK_RESPONSE = "Model output to the follow-up prompt";

/** Block label for the reasoning trace (shown only if non-empty). */
export const BLOCK_REASONING = "Reasoning trace the provider surfaced";

/** Block label for provenance identifiers. */
export const BLOCK_PROVENANCE = "Provenance IDs";

// ===== Counts caption template (T10 §4 verbatim) =====

/**
 * Counts caption: shown only when n_records > 0.
 * @param nRecords - total record count
 * @param nFailure - failure record count
 * @param nDecline - decline interview record count
 */
export function countsCaptionText(
  nRecords: number,
  nFailure: number,
  nDecline: number,
): string {
  return (
    `${nRecords} records: ${nFailure} collection ${nFailure === 1 ? "failure" : "failures"}, ` +
    `${nDecline} follow-up ${nDecline === 1 ? "interview" : "interviews"}.`
  );
}

// ===== Empty state caption (T10 S2 verbatim) =====

/**
 * Empty state caption for domains with no failure records (e.g. food).
 * First-class state — not a defect or placeholder.
 * Byte-identical to the T10 S2 binding string.
 */
export const EMPTY_CAPTION =
  "This domain's collection run produced no failure records or follow-up interviews. " +
  "The absence is itself an observation about how this set of models responded to this domain's elicitation prompts.";

// ===== Loading / error strings (first-class states) =====

/** Loading state label — shown while fetching failures/{slug}.json. */
export const LOADING_TEXT = "Loading collection records…";

/** Fetch-failed error label — shown on HTTP error. */
export const FETCH_FAILED_TEXT =
  "Could not load collection records for this domain. Check that the data file is present.";

/** Malformed data label — shown if the fetched JSON does not match the expected shape. */
export const MALFORMED_TEXT =
  "Collection records data for this domain could not be parsed.";

// ===== Domain selector label (CDA SME M3) =====

/** Domain selector label — reuses the existing domain picker convention. */
export const DOMAIN_LABEL = "Domain";
