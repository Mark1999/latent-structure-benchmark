// apps/dashboard/src/copy/failures_findings.ts
//
// Single source of truth for all LSB-authored strings in the FailuresFindingsSection.
//
// CDA SME verdict: PASS-WITH-NOTES (2026-05-12-phase6-T10-cda-sme-verdict.md)
//   S1: summary row — field-shape descriptor only, no verbatim preview.
//   S2: EMPTY_CAPTION verbatim.
//   S4a: badge label "Follow-up interview" (CDA SME approved).
//   S4b: block label "Model output" (names artifact, not state).
//   S5: explicit aria-label templates.
//   S6: "Reasoning trace the provider surfaced".
//   S7: no methodology-page hyperlink at T10.
//
// UI/UX verdict: PASS-WITH-NOTES (2026-05-12-phase6-T10-uiux-plan-verdict.md)
//   F-T10-T1: use var(--font-mono) and var(--font-body), not phantom names.
//   F-T10-C1: use var(--color-text-caption) for 12px regular-weight text.
//
// §1.5.4 vocabulary check: no forbidden vocabulary in any string below.
// Do not edit without CDA SME re-review.

/**
 * Section heading — H2 sibling of MethodologySummary's "About this measurement".
 * Approved verbatim by CDA SME (§2.1 of verdict).
 */
export const SECTION_HEADING = "Collection records and follow-up interviews";

/**
 * record_type badge labels.
 * S4a: "Follow-up interview" (approved per CDA SME verdict).
 * "Collection failure" approved as proposed.
 */
export const RECORD_TYPE_LABEL: Record<string, string> = {
  failure: "Collection failure",
  decline_interview: "Follow-up interview",
};

/**
 * Counts caption template.
 * Callers interpolate {n_records}, {n_failure_records}, {n_decline_interview_records}.
 */
export const COUNTS_CAPTION_TEMPLATE =
  "{n_records} records published for this domain — {n_failure_records} collection failures and {n_decline_interview_records} follow-up interviews.";

/**
 * No-records caption — verbatim per CDA SME S2.
 * Two-sentence form: positive observation framing. No temporariness or absence-as-defect language.
 */
export const EMPTY_CAPTION =
  "This domain's collection run produced no failure records or follow-up interviews. The absence is itself an observation about how this set of models responded to this domain's elicitation prompts.";

/**
 * Defensive error caption — missing or malformed framing_note.
 * Approved per plan §2.5.
 */
export const ERROR_FRAMING_MISSING =
  "Collection records are unavailable for this domain.";

/**
 * Defensive error caption — fetch failure.
 * Approved per plan §2.5.
 */
export const ERROR_FETCH_FAILED =
  "Collection records could not be loaded for this domain.";

// ── Expanded-view block labels ─────────────────────────────────────────────────
// All approved per CDA SME §3 (S4b, S6 carry-forward notes applied).

export const LABEL_MODEL = "Model";
export const LABEL_MODEL_VERSION = "Model version returned";
export const LABEL_PROVIDER = "Provider";
export const LABEL_COLLECTED_AT = "Collected at";
export const LABEL_PROMPT_VERSION = "Prompt version";
export const LABEL_ORIGINATING_STEP = "Originating step";
export const LABEL_OUTCOME_CLASS = "Outcome class";
export const LABEL_ERROR_TYPE = "Error type";
export const LABEL_RUN_INDEX = "Run index";
export const LABEL_ERROR_MESSAGE = "Error message";
export const LABEL_FOLLOW_UP_PROMPT = "Follow-up prompt LSB sent";
// S4b: "Model output" names the artifact, not the state.
// The " to the follow-up prompt" qualifier is applied at render for decline_interview records.
export const LABEL_MODEL_OUTPUT = "Model output";
export const LABEL_MODEL_OUTPUT_FOLLOWUP = "Model output to the follow-up prompt";
// S6: approved verbatim.
export const LABEL_REASONING_TRACE = "Reasoning trace the provider surfaced";
export const LABEL_PARTIAL_SESSION = "Partial session";
export const LABEL_RETRY_ATTEMPTS = "Retry attempts";
export const LABEL_PROVENANCE_IDS = "Provenance IDs";
