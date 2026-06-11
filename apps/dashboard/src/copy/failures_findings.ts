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

// ===== Per-record detail surface (v0.20.1, CR-T7, 2026-06-10) =====
// All strings below are byte-identical to the CDA SME bound strings in
// .claude/agent-memory/cda_sme/project_cr_t7_sme_bound_strings.md.
// Do NOT paraphrase. Byte-identity assertions in FailuresFindings.test.tsx
// enforce this.
// NOTE-7-SUPERSEDED-BY-N4: The nine BLOCK_FREELIST_*/BLOCK_PILESORT_*/
// BLOCK_PILE_INTERVIEW_* constants below are the per-step sub-labels per
// CDA SME N4 (parser-state register per step). Existing BLOCK_PROMPT,
// BLOCK_RESPONSE, BLOCK_REASONING constants (from the follow-up surface,
// failures_findings.ts) are scoped to the follow-up interview and are not
// reused here. N4 cognition-attribution axis supersedes UI/UX NOTE-7
// convenience axis. See docs/status/2026-06-10-collection-records-rework-verdicts.md
// CR-T7 section and .claude/agent-memory/cda_sme/project_cr_t7_plan_verdict.md N4.

/**
 * In-page caption rendered above the expanded detail body.
 * CDA SME-bound (byte-identical). Distinct from framing_note_detail (N8).
 */
export const RECORDS_DETAIL_FRAMING =
  "The blocks below show the verbatim bytes exchanged for this collection session, step by step. " +
  "Each of the three CDA elicitation steps (free list, pile sort, pile interview) is shown as the " +
  "prompt LSB sent, the response the provider returned, and any reasoning trace the provider surfaced. " +
  "These are LSB pipeline I/O records, not a window into model cognition.";

/**
 * Expand affordance button copy. CDA SME N6: no "answer", no quality-framed verb.
 */
export const RECORDS_DETAIL_EXPAND_LABEL = "Show parsed-step exchange";

/** Loading state for the per-record detail fetch. */
export const RECORDS_DETAIL_LOADING = "Loading per-record exchange…";

/** Fetch-failed state for the per-record detail fetch. */
export const RECORDS_DETAIL_FETCH_FAILED =
  "Could not load the per-record exchange for this session. Check that the data file is present.";

/** Malformed state for the per-record detail fetch. */
export const RECORDS_DETAIL_MALFORMED =
  "Per-record exchange data for this session could not be parsed.";

// -- Step heading labels (CDA SME N1: PILE_INTERVIEW prefix avoids collision with follow-up surface) --

/** Outer heading for the free-list step section. */
export const BLOCK_FREELIST_EXCHANGE = "Free-list step";

/** Outer heading for the pile-sort step section. */
export const BLOCK_PILESORT_EXCHANGE = "Pile-sort step";

/**
 * Outer heading for the pile-interview step section.
 * CDA SME N1 rename: "pile-interview" avoids collision with the follow-up
 * "interview" record kind (DeclineInterview / BADGE_DECLINE).
 */
export const BLOCK_PILE_INTERVIEW_EXCHANGE = "Pile-interview step";

// -- Free-list step sub-labels (CDA SME N4 / bound strings §5) --

/** Free-list step: prompt sub-label. */
export const BLOCK_FREELIST_PROMPT = "Free-list prompt LSB sent";

/** Free-list step: response sub-label. */
export const BLOCK_FREELIST_RESPONSE = "Provider response to the free-list prompt";

/** Free-list step: reasoning trace sub-label. */
export const BLOCK_FREELIST_REASONING =
  "Reasoning trace the provider surfaced on the free-list step";

// -- Pile-sort step sub-labels (CDA SME N4 / bound strings §5) --

/** Pile-sort step: prompt sub-label. */
export const BLOCK_PILESORT_PROMPT = "Pile-sort prompt LSB sent";

/** Pile-sort step: response sub-label. */
export const BLOCK_PILESORT_RESPONSE = "Provider response to the pile-sort prompt";

/** Pile-sort step: reasoning trace sub-label. */
export const BLOCK_PILESORT_REASONING =
  "Reasoning trace the provider surfaced on the pile-sort step";

// -- Pile-interview step sub-labels (CDA SME N1 rename + N4 / bound strings §5) --

/** Pile-interview step: prompt sub-label. */
export const BLOCK_PILE_INTERVIEW_PROMPT = "Pile-interview prompt LSB sent";

/** Pile-interview step: response sub-label. */
export const BLOCK_PILE_INTERVIEW_RESPONSE = "Provider response to the pile-interview prompt";

/** Pile-interview step: reasoning trace sub-label. */
export const BLOCK_PILE_INTERVIEW_REASONING =
  "Reasoning trace the provider surfaced on the pile-interview step";

// -- Provenance block labels (CDA SME bound strings §6) --

/** Heading for the provenance block. */
export const BLOCK_DETAIL_PROVENANCE = "Provenance and pipeline identifiers";

// ===== Per-attempt retry-transcript block (v0.20.3, CR-T8, 2026-06-10) =====
// All strings below are CDA SME-approved (CR-T8 gate, 2026-06-10).
// Do NOT paraphrase. Byte-identity assertions in FailuresFindings.test.tsx enforce this.
// Register constraints (CDA SME N3 BINDING):
//   1. PIPELINE retry not model retry.
//   2. Parser-state language only.
//   3. No bare "refusal" (T3 N4 carry-forward).
//   4. No "cooperative" outside CR-T1 counterfactual frame (T1 N1 carry-forward).
//   5. No cognition attribution.
//   6. Shared-prompt register preserved by AC11 (parent prompt rendered once, not per attempt).
// N1 BINDING: attempt_index value shown 0-indexed (byte-aligned with published JSON for audit trail).
// N2 BINDING: parse_error_message label frames the field as an LSB parser-state classifier output.

/**
 * Block heading for the pipeline retry attempts surface.
 * CDA SME-approved (CR-T8 gate, 2026-06-10); byte-identical.
 * Do NOT paraphrase.
 */
export const BLOCK_ATTEMPTS = "Pipeline retry attempts";

/**
 * Framing paragraph for the pipeline retry attempts block.
 * CDA SME-approved (CR-T8 gate, 2026-06-10); byte-identical.
 * Frames these as LSB-pipeline retries of the same prompt after a parser-state failure.
 * Do NOT paraphrase.
 */
export const ATTEMPTS_FRAMING =
  "After a parser-state failure the LSB pipeline re-issued the same prompt. " +
  "Each attempt below shows the response the provider returned and the parser-state outcome " +
  "the LSB pipeline recorded. The prompt is shared across all attempts and is shown once above.";

/**
 * Sub-label for the parse_error_message field in an attempt.
 * CDA SME N2 BINDING: frames the field as an LSB parser-state classifier output,
 * not a model-side finding. Mirrors originating_outcome_class framing precedent.
 */
export const ATTEMPTS_PARSE_ERROR_LABEL = "LSB parser-state diagnosis";

/**
 * Anti-attribution note rendered below the provenance heading.
 * CDA SME-bound (byte-identical).
 */
export const BLOCK_DETAIL_PROVENANCE_NOTE =
  "The identifiers below name the LSB collection session, the prompt-template version, " +
  "and the provider-returned model-version string. They are properties of the LSB pipeline run, " +
  "not of the model's intent.";

// ===== Chart-to-record provenance pivot (G7-FOLLOWUP-T1, 2026-06-11) =====
// All four constants below are byte-identical to the CDA SME bound strings
// delivered in .claude/agent-memory/cda_sme/project_g7_followup_t1_sme_bound_strings.md.
// Do NOT paraphrase. Both MDSPlot.tsx and Focus1SelfConsistencyOverview.tsx import
// these constants. No inline string literals of these strings in component files.
// Parser-state register: records are LSB-pipeline output for the domain, model as informant.
// Register authority: CDA SME G7-FOLLOWUP-T1 verdict (2026-06-11), Axis 3 PASS.

/**
 * Affordance button label for the chart-to-record pivot.
 * Used on both the MDSPlot tooltip pivot control and the Focus 1 individual-model
 * view header pivot control.
 * CDA SME-bound (byte-identical). Do NOT paraphrase.
 * "for this model" is the model-as-informant register: the records are LSB pipeline
 * output produced with this model as the informant on the currently selected domain.
 */
export const PIVOT_TO_RECORDS_LABEL = "See the collection records for this model";

/**
 * aria-label template for the chart-to-record pivot affordance.
 * Takes (modelLabel, domainLabel) at call site. SR users need both model and domain context
 * because both surfaces are domain-scoped views.
 * CDA SME-bound (byte-identical template). Do NOT paraphrase connective words.
 */
export function pivotToRecordsAriaLabel(modelLabel: string, domainLabel: string): string {
  return `See the collection records for ${modelLabel} on the ${domainLabel} domain`;
}

/**
 * Arrival caption template for when the pivot lands and the per-model summary row
 * is highlighted. Takes (modelLabel, domainLabel) at call site.
 * CDA SME-bound (byte-identical template). Do NOT paraphrase.
 * Places LSB as the producing agent and the model as the informant.
 * "as the informant" is binding; do not substitute "as the subject" etc.
 */
export function pivotToRecordsArrivalCaption(modelLabel: string, domainLabel: string): string {
  return `Showing the collection records LSB produced when running the ${domainLabel} protocol with ${modelLabel} as the informant.`;
}

/**
 * No-match notice template when the pivot target model has no successful-run summary
 * in the requested domain. Takes (modelLabel, domainLabel) at call site.
 * CDA SME-bound (byte-identical template). Do NOT paraphrase.
 * Does not say the model "failed" or that records "are missing". States the
 * table does not list it, with the inclusion criterion stated.
 */
export function pivotToRecordsNoMatchNotice(modelLabel: string, domainLabel: string): string {
  return `The Collection records tab has no successful-run summary for ${modelLabel} on the ${domainLabel} domain. The per-model summary table only lists models that produced a parseable session in this domain.`;
}
