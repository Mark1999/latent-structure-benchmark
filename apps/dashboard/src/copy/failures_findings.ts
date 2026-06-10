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

// ===== Impact paragraph (v0.15.1, CR-T1, 2026-06-10) =====

/**
 * Impact paragraph for the collection failures surface.
 * Mark-authored, approved verbatim 2026-06-10; CDA SME T1 gate PASS-WITH-NOTES.
 * Do NOT paraphrase. Byte-identity assertion in FailuresFindings.test.tsx enforces this.
 */
export const IMPACT_PARAGRAPH_FAILURES =
  "Some sessions do not produce a usable answer. A model declines, or returns something our pipeline cannot parse, or the request fails on the provider's side. We keep all of it. Which prompts a model will not answer, and how it says no, is as much a part of its behavior as the answers it gives. Deleting these records would make every model look equally cooperative, and that would be misleading. So they are published here, verbatim.";

// ===== Follow-up interviews impact paragraph (v0.19.2, CR-T2, 2026-06-10) =====

/**
 * Impact paragraph for the follow-up interviews surface.
 * Mark-authored, approved verbatim 2026-06-10; CDA SME T2 gate PASS-WITH-NOTES.
 * Renders only when at least one decline_interview record is present in the loaded file.
 * Do NOT paraphrase. Byte-identity assertion in FailuresFindings.test.tsx enforces this.
 */
export const IMPACT_PARAGRAPH_FOLLOWUPS =
  "When a model declines, we ask it one more question: why? Its answer is recorded here word for word. Read these with care. The explanation a model gives for refusing is itself just output, produced the same way as everything else it says. It may be consistent, it may be boilerplate, it may contradict what actually happened. That is exactly why we keep it: how a model accounts for its own refusal is one more observable behavior, not the inside story.";

// ===== Taxonomy block (v0.19.3, CR-T3, 2026-06-10) =====

/**
 * Taxonomy block: CDA SME-approved static disclosure surface naming the three
 * top-level collection outcomes and the seven originating_outcome_class enum
 * values. Structure is a typed object literal so the JSX renderer can map over
 * topLevel and enumValues arrays.
 *
 * All string values are byte-identical to the CDA SME CR-T3 verdict
 * (docs/status/2026-06-10-collection-records-rework-verdicts.md T3 section).
 * The seven id values are byte-identical to cdb_core/schemas.py lines 734-742.
 *
 * Do NOT paraphrase these strings. Byte-identity assertion in
 * FailuresFindings.test.tsx enforces this.
 */
export const TAXONOMY_BLOCK = {
  heading: "What LSB records as a collection outcome",
  bridge:
    "Every category below is a property of how the LSB pipeline classified the session, not a property of what the model decided.",
  topLevel: [
    {
      term: "Successful run",
      description:
        "LSB parsed primary-step output from the session. Surfaced in the per-model summary section below. The per-domain summary artifact is at /data/records/{slug}.json.",
    },
    {
      term: "Collection failure",
      description:
        "The session did not produce a parseable primary-step response. The LSB pipeline recorded the verbatim output and the error context. Rendered on this tab with the badge \"Collection failure\".",
    },
    {
      term: "Follow-up interview",
      description:
        "After an LSB-classified refusal or empty output, the LSB pipeline asked the model one follow-up question and recorded the verbatim exchange. Rendered on this tab with the badge \"Follow-up interview\".",
    },
  ],
  enumSubheading:
    "originating_outcome_class ENUM VALUES (seven, byte-identical to the schema):",
  enumValues: [
    {
      id: "empty_output",
      description: "LSB parsed zero items from the model's primary-step response.",
    },
    {
      id: "refusal_string_match",
      description:
        "LSB matched a refusal-string pattern against the model's response. The match is a pipeline classification, not a model statement of refusal.",
    },
    {
      id: "single_degenerate_pile",
      description:
        "LSB parsed exactly one pile in a pile-sort step, with that pile holding at least 95 percent of the free-list items.",
    },
    {
      id: "parse_failure",
      description:
        "LSB could not parse the model's response into the expected step structure (for example, malformed JSON or a missing required field).",
    },
    {
      id: "http_error",
      description:
        "The provider's HTTP transport returned an error before LSB received a parseable response.",
    },
    {
      id: "timeout",
      description: "The provider's response did not arrive within the LSB request timeout.",
    },
    {
      id: "other",
      description: "A fall-through bucket for outcomes that did not match the rules above.",
    },
  ],
} as const;

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

// ===== Counts caption template (v0.19.5, CR-T6, 2026-06-10) =====

/**
 * Counts caption: shown based on a four-cell empty-state matrix (CDA SME CR-T6 N3).
 *
 * Four-cell matrix (N3 BINDING):
 *   (n_records > 0, nParsedResponses > 0)  -> full three-clause caption
 *   (n_records > 0, nParsedResponses === 0 or undefined) -> failures-only two-clause caption
 *   (n_records === 0, nParsedResponses > 0) -> parsed-responses-only single-clause caption
 *   (n_records === 0, nParsedResponses === 0 or undefined) -> empty string (caption omitted)
 *
 * When nParsedResponses is undefined (records side not ready), renders failures-only
 * caption matching pre-T6 behavior (CDA SME N4 BINDING).
 *
 * No leading total (CDA SME N1 BINDING: Option C, no N_total denominator).
 *
 * Template for all-positive case (CDA SME N2 BINDING, byte-identical):
 *   "{S} parsed primary-step responses, {F} collection {failure|failures},
 *    {D} follow-up {interview|interviews}."
 *
 * @param nRecords - total failure-side record count (n_records from failures JSON)
 * @param nFailure - failure record count
 * @param nDecline - decline interview record count
 * @param nParsedResponses - parsed primary-step response count (n_informants from records JSON);
 *   optional: pass undefined when records side is not yet ready (N5 BINDING)
 */
export function countsCaptionText(
  nRecords: number,
  nFailure: number,
  nDecline: number,
  nParsedResponses?: number,
): string {
  const hasFailures = nRecords > 0;
  const hasParsed = typeof nParsedResponses === "number" && nParsedResponses > 0;

  if (!hasFailures && !hasParsed) {
    // (0, 0): caption omitted (N3 cell 4)
    return "";
  }

  if (!hasFailures && hasParsed) {
    // (0, >0): S clause only (N3 cell 3)
    return `${nParsedResponses} parsed primary-step responses.`;
  }

  const failureClause =
    `${nFailure} collection ${nFailure === 1 ? "failure" : "failures"}, ` +
    `${nDecline} follow-up ${nDecline === 1 ? "interview" : "interviews"}.`;

  if (hasFailures && !hasParsed) {
    // (>0, 0): drop S clause (N3 cell 2)
    return failureClause;
  }

  // (>0, >0): full three-clause caption (N3 cell 1, N2 BINDING byte-identical template)
  return (
    `${nParsedResponses} parsed primary-step responses, ` +
    failureClause
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

// ===== Records summary section (v0.19.4, CR-T5, 2026-06-10) =====

/**
 * Section heading for the per-model records summary section.
 * CDA SME N1 (CR-T5): disambiguates parser-state from quality judgment.
 * Do NOT paraphrase. Byte-identity assertion in FailuresFindings.test.tsx enforces this.
 */
export const RECORDS_SECTION_HEADING =
  "Per-model summary of parsed primary-step responses";

/**
 * Column labels for the per-model records summary table.
 * CDA SME N2 (CR-T5): byte-identical as approved.
 */
export const RECORDS_COL_MODEL = "Model";
export const RECORDS_COL_PROVIDER = "Provider";
export const RECORDS_COL_RUNS = "Runs";
export const RECORDS_COL_QA_PASS = "QA-pass count";
export const RECORDS_COL_VERSION = "Model version returned";

/**
 * Empty-state observation for a domain where by_model is empty.
 * CDA SME N3 (CR-T5): first-class observation, not a defect.
 * Do NOT paraphrase. Byte-identity assertion in FailuresFindings.test.tsx enforces this.
 */
export const RECORDS_EMPTY_OBSERVATION =
  "No collection runs in this domain produced a parseable primary-step response. " +
  "The absence is itself an observation about how this set of models behaved under " +
  "the LSB elicitation prompts for this domain.";

/**
 * Link-out caption below the per-model table (or empty-state observation).
 * CDA SME N4 (CR-T5): byte-identical to the Architect stub as approved.
 * Points to the Data tab, not to external URLs directly.
 */
export const RECORDS_LINK_OUT_CAPTION =
  "The full per-record bytes are published in the open data bundle. " +
  "See the Data tab for the bundle, the Hugging Face dataset, and the Zenodo DOI.";

/**
 * Loading state label for the records summary fetch.
 * CDA SME N5 (CR-T5): mirrors LOADING_TEXT semantics, refers to records summary.
 */
export const RECORDS_LOADING_TEXT = "Loading records summary…";

/**
 * Fetch-failed error label for the records summary fetch.
 * CDA SME N5 (CR-T5): mirrors FETCH_FAILED_TEXT semantics.
 */
export const RECORDS_FETCH_FAILED_TEXT =
  "Could not load the records summary for this domain. Check that the data file is present.";

/**
 * Malformed data label for the records summary fetch.
 * CDA SME N5 (CR-T5): mirrors MALFORMED_TEXT semantics.
 */
export const RECORDS_MALFORMED_TEXT =
  "Records summary data for this domain could not be parsed.";
