/**
 * FailuresFindingsSection — public-facing UI surface for failures-as-findings.
 *
 * This is the public surface; <details>/<summary> is the chosen accordion
 * mechanism per T10 plan §2.6, distinct from InspectRoot's flat-table posture.
 * InspectRoot's "no <details>" scope constraint applies to InspectRoot only.
 *
 * Source:
 *   Architect plan:  docs/status/2026-05-12-phase6-T10-architect-plan.md
 *   CDA SME verdict: docs/status/2026-05-12-phase6-T10-cda-sme-verdict.md
 *   UI/UX verdict:   docs/status/2026-05-12-phase6-T10-uiux-plan-verdict.md
 *
 * Key binding notes applied here:
 *   S1 (CDA SME LOAD-BEARING): No verbatim preview in summary row.
 *       field-shape descriptor for failure records: "error_message: N chars"
 *       decline_interview: trailing originating_outcome_class enum only.
 *   S2: EMPTY_CAPTION verbatim from copy module.
 *   S4a: badge label "Follow-up interview".
 *   S4b: block label "Model output to the follow-up prompt".
 *   S5: explicit aria-label on every <summary>.
 *   S6: "Reasoning trace the provider surfaced".
 *   S7: no methodology-page hyperlink (T14 wires).
 *   F-T10-T1 (UI/UX BINDING): var(--font-mono) / var(--font-body).
 *   F-T10-C1 (UI/UX BINDING): var(--color-text-caption) for 12px regular.
 *   F-T10-A1 (UI/UX ADVISORY): confirmed in failures-findings.css.
 *
 * CLAUDE.md §6 R2: No dangerouslySetInnerHTML. All text via React text nodes.
 * CLAUDE.md §6 R13: No cost aggregation / spend-gate framing.
 * Types: local interfaces only, no shared types file (T14 doc-sweep concern). Cast through unknown.
 */

import { useEffect, useState } from "react";
import { fetchFailures } from "../api/client";
import "../styles/failures-findings.css";

import {
  SECTION_HEADING,
  RECORD_TYPE_LABEL,
  COUNTS_CAPTION_TEMPLATE,
  EMPTY_CAPTION,
  ERROR_FRAMING_MISSING,
  ERROR_FETCH_FAILED,
  LABEL_MODEL,
  LABEL_MODEL_VERSION,
  LABEL_PROVIDER,
  LABEL_COLLECTED_AT,
  LABEL_PROMPT_VERSION,
  LABEL_ORIGINATING_STEP,
  LABEL_OUTCOME_CLASS,
  LABEL_ERROR_TYPE,
  LABEL_RUN_INDEX,
  LABEL_ERROR_MESSAGE,
  LABEL_FOLLOW_UP_PROMPT,
  LABEL_MODEL_OUTPUT,
  LABEL_MODEL_OUTPUT_FOLLOWUP,
  LABEL_REASONING_TRACE,
  LABEL_PARTIAL_SESSION,
  LABEL_RETRY_ATTEMPTS,
  LABEL_PROVENANCE_IDS,
} from "../copy/failures_findings";

// ── Local interfaces — the types file is intentionally not modified (T14 concern) ──
// Cast through unknown at fetchFailures boundary per T0/T7 precedent.

export interface FailuresPublishedFile {
  domain_slug: string;
  generated_at: string;
  n_records: number;
  n_failure_records: number;
  n_decline_interview_records: number;
  framing_note: string;
  records: FailureRecord[];
}

export interface FailureRecord {
  record_type: "failure" | "decline_interview";
  collection_date: string;
  model_id: string;
  domain_slug: string;
  originating_outcome_class: string | null;
  // Failure-only:
  error_type?: string;
  error_message?: string;
  run_index?: number;
  retry_attempts?: unknown[];
  partial_session?: Record<string, unknown>;
  // Decline-interview-only:
  decline_interview_id?: string;
  originating_informant_id?: string | null;
  originating_failure_id?: string | null;
  originating_step?: string;
  detection_rule_version?: string;
  model_version_returned?: string;
  provider?: string;
  api_endpoint?: string;
  prompt_version?: string;
  sha256_manifest?: string;
  prompt_verbatim?: string;
  response_verbatim?: string;
  thinking_verbatim?: string;
  input_tokens?: number;
  output_tokens?: number;
  latency_ms?: number;
  stop_reason?: string;
  qa_notes?: string;
  version_drift_flag?: boolean;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Truncate ISO timestamp to date-only prefix for display. */
function isoToDate(iso: string): string {
  return iso.slice(0, 10);
}

/**
 * Format ISO date string as human-readable date for ARIA labels.
 * e.g. "2026-04-22T18:19:57" → "April 22, 2026"
 * Defensive: if parsing fails, falls back to the raw 10-char prefix.
 */
function isoToHumanDate(iso: string): string {
  try {
    const d = new Date(iso.slice(0, 10));
    return d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  } catch {
    return isoToDate(iso);
  }
}

/** Build counts caption from the template. */
function buildCountsCaption(
  n_records: number,
  n_failure_records: number,
  n_decline_interview_records: number
): string {
  return COUNTS_CAPTION_TEMPLATE.replace("{n_records}", String(n_records))
    .replace("{n_failure_records}", String(n_failure_records))
    .replace(
      "{n_decline_interview_records}",
      String(n_decline_interview_records)
    );
}

/**
 * Build the aria-label for a <summary> element.
 * Templates per CDA SME S5.
 */
function buildAriaLabel(record: FailureRecord): string {
  const humanDate = isoToHumanDate(record.collection_date);
  if (record.record_type === "decline_interview") {
    const outcome = record.originating_outcome_class ?? "unknown";
    return `Follow-up interview record. Model: ${record.model_id}. Collected: ${humanDate}. Outcome class: ${outcome}. Press Enter or Space to expand.`;
  } else {
    // failure record
    const errType = record.error_type ?? "unknown";
    const msgLen =
      record.error_message !== undefined ? record.error_message.length : 0;
    return `Collection failure record. Model: ${record.model_id}. Collected: ${humanDate}. Error type: ${errType}. Message length: ${msgLen} characters. Press Enter or Space to expand.`;
  }
}

/**
 * Stable React key for a failure record.
 * decline_interview: use decline_interview_id.
 * failure: composite key per T10 plan §10 risk 8.
 */
function recordKey(record: FailureRecord, index: number): string {
  if (record.record_type === "decline_interview" && record.decline_interview_id) {
    return `di|${record.decline_interview_id}`;
  }
  // Composite key for failure records
  return `failure|${record.model_id}|${record.run_index ?? index}|${record.collection_date}|${index}`;
}

// ── Sub-component: a single labeled block in the expanded view ────────────────

function BlockField({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="failure-record__block">
      <span className="failure-record__block-label">{label}</span>
      {children}
    </div>
  );
}

// ── Sub-component: verbatim <pre> block ───────────────────────────────────────

function PreBlock({ value }: { value: string }) {
  return <pre className="failure-record__pre">{value}</pre>;
}

// ── FailureRecord component ────────────────────────────────────────────────────

/**
 * Renders a single failure or decline_interview record as a native
 * <details>/<summary> accordion.
 *
 * CDA SME S1 (LOAD-BEARING): summary row shows field-shape metadata only —
 * no verbatim bytes from response_verbatim or error_message.
 */
export function FailureRecordRow({ record }: { record: FailureRecord }) {
  const badge =
    RECORD_TYPE_LABEL[record.record_type] ?? record.record_type;
  const dateDisplay = isoToDate(record.collection_date);
  const ariaLabel = buildAriaLabel(record);

  // S1: field-shape descriptor for failure records
  const fieldShapeDescriptor =
    record.record_type === "failure" && record.error_message !== undefined
      ? `error_message: ${record.error_message.length} chars`
      : null;

  return (
    <li>
      <details className="failure-record">
        <summary
          className="failure-record__summary"
          aria-label={ariaLabel}
        >
          <span className="failure-record__badge">{badge}</span>
          <span className="failure-record__model">{record.model_id}</span>
          <span className="failure-record__date">{dateDisplay}</span>
          {/* S1: for decline_interview, show originating_outcome_class enum verbatim in mono */}
          {record.record_type === "decline_interview" &&
            record.originating_outcome_class !== null &&
            record.originating_outcome_class !== undefined && (
              <span className="failure-record__outcome-class">
                {record.originating_outcome_class}
              </span>
            )}
          {/* S1: for failure records, show field-shape descriptor in body font + caption color */}
          {fieldShapeDescriptor !== null && (
            <span className="failure-record__field-shape">
              {fieldShapeDescriptor}
            </span>
          )}
        </summary>

        <div className="failure-record__body">
          {/* ── Basic identity ─────────────────────────────────────────────── */}

          <BlockField label={LABEL_MODEL}>
            <span className="failure-record__block-value--mono">
              {record.model_id}
            </span>
          </BlockField>

          {/* model_version_returned: decline_interview only */}
          {record.record_type === "decline_interview" &&
            record.model_version_returned !== undefined && (
              <BlockField label={LABEL_MODEL_VERSION}>
                <span className="failure-record__block-value--mono">
                  {record.model_version_returned}
                </span>
              </BlockField>
            )}

          {/* provider: decline_interview only */}
          {record.record_type === "decline_interview" &&
            record.provider !== undefined && (
              <BlockField label={LABEL_PROVIDER}>
                <span className="failure-record__block-value">
                  {record.provider}
                </span>
              </BlockField>
            )}

          <BlockField label={LABEL_COLLECTED_AT}>
            <span className="failure-record__block-value">
              {record.collection_date}
            </span>
          </BlockField>

          {/* prompt_version: decline_interview only */}
          {record.record_type === "decline_interview" &&
            record.prompt_version !== undefined && (
              <BlockField label={LABEL_PROMPT_VERSION}>
                <span className="failure-record__block-value--mono">
                  {record.prompt_version}
                </span>
              </BlockField>
            )}

          {/* originating_step: decline_interview only */}
          {record.record_type === "decline_interview" &&
            record.originating_step !== undefined && (
              <BlockField label={LABEL_ORIGINATING_STEP}>
                <span className="failure-record__block-value--mono">
                  {record.originating_step}
                </span>
              </BlockField>
            )}

          {/* Outcome class: decline_interview only (null on failure records) */}
          {record.record_type === "decline_interview" &&
            record.originating_outcome_class !== null &&
            record.originating_outcome_class !== undefined && (
              <BlockField label={LABEL_OUTCOME_CLASS}>
                <span className="failure-record__block-value--mono">
                  {record.originating_outcome_class}
                </span>
              </BlockField>
            )}

          {/* ── Failure-only fields ───────────────────────────────────────── */}

          {record.record_type === "failure" &&
            record.error_type !== undefined && (
              <BlockField label={LABEL_ERROR_TYPE}>
                <span className="failure-record__block-value--mono">
                  {record.error_type}
                </span>
              </BlockField>
            )}

          {record.record_type === "failure" &&
            record.run_index !== undefined && (
              <BlockField label={LABEL_RUN_INDEX}>
                <span className="failure-record__block-value">
                  {record.run_index}
                </span>
              </BlockField>
            )}

          {record.record_type === "failure" &&
            record.error_message !== undefined && (
              <BlockField label={LABEL_ERROR_MESSAGE}>
                <PreBlock value={record.error_message} />
              </BlockField>
            )}

          {/* ── Follow-up prompt ─────────────────────────────────────────── */}

          {record.prompt_verbatim !== undefined && (
            <BlockField label={LABEL_FOLLOW_UP_PROMPT}>
              <PreBlock value={record.prompt_verbatim} />
            </BlockField>
          )}

          {/* ── Model output — S4b label applied per record_type ─────────── */}

          {record.response_verbatim !== undefined && (
            <BlockField
              label={
                record.record_type === "decline_interview"
                  ? LABEL_MODEL_OUTPUT_FOLLOWUP
                  : LABEL_MODEL_OUTPUT
              }
            >
              <PreBlock value={record.response_verbatim} />
            </BlockField>
          )}

          {/* ── Reasoning trace — S6 label ───────────────────────────────── */}

          {record.thinking_verbatim !== undefined &&
            record.thinking_verbatim.length > 0 && (
              <BlockField label={LABEL_REASONING_TRACE}>
                <PreBlock value={record.thinking_verbatim} />
              </BlockField>
            )}

          {/* ── Failure-only: partial session ────────────────────────────── */}

          {record.record_type === "failure" &&
            record.partial_session !== undefined && (
              <BlockField label={LABEL_PARTIAL_SESSION}>
                <PreBlock value={JSON.stringify(record.partial_session, null, 2)} />
              </BlockField>
            )}

          {/* ── Failure-only: retry attempts (suppress when empty) ──────── */}

          {record.record_type === "failure" &&
            Array.isArray(record.retry_attempts) &&
            record.retry_attempts.length > 0 && (
              <BlockField label={LABEL_RETRY_ATTEMPTS}>
                <PreBlock
                  value={JSON.stringify(record.retry_attempts, null, 2)}
                />
              </BlockField>
            )}

          {/* ── Provenance IDs — researcher reproducibility ───────────────
              Plan §2.4: opaque IDs + SHA hash in mono at font-size-xs.
              F-T10-C1: --color-text-caption for xs-size.               */}

          <BlockField label={LABEL_PROVENANCE_IDS}>
            <div className="failure-record__block-value--provenance">
              {record.record_type === "decline_interview" && (
                <>
                  {record.decline_interview_id !== undefined && (
                    <div>decline_interview_id: {record.decline_interview_id}</div>
                  )}
                  {record.originating_informant_id !== undefined && (
                    <div>
                      originating_informant_id:{" "}
                      {record.originating_informant_id ?? "null"}
                    </div>
                  )}
                  {record.originating_failure_id !== undefined && (
                    <div>
                      originating_failure_id:{" "}
                      {record.originating_failure_id ?? "null"}
                    </div>
                  )}
                  {record.sha256_manifest !== undefined && (
                    <div>sha256_manifest: {record.sha256_manifest}</div>
                  )}
                </>
              )}
              {record.record_type === "failure" && (
                <div>
                  domain_slug: {record.domain_slug} | run_index:{" "}
                  {record.run_index ?? "—"} | collection_date:{" "}
                  {record.collection_date}
                </div>
              )}
            </div>
          </BlockField>
        </div>
      </details>
    </li>
  );
}

// ── FailuresFindingsSection ────────────────────────────────────────────────────

export interface FailuresFindingsSectionProps {
  /** Domain slug for which to fetch and display failure records. */
  domainSlug: string;
}

type SectionState = "loading" | "loaded" | "error";

/**
 * FailuresFindingsSection — renders below MethodologySummary in App.tsx.
 *
 * Per DESIGN_SYSTEM.md §2.1 page architecture (T10 extension):
 *   - <section aria-labelledby="failures-findings-heading">
 *   - <h2> sibling of MethodologySummary's <h2> (H2 sibling per CDA SME §2.4)
 *   - framing_note rendered verbatim (CDA SME §5.1 binding from T9)
 *   - records as native <details>/<summary> accordions
 *   - empty-state: EMPTY_CAPTION per CDA SME S2
 *
 * Excluded in embed mode per §12.5 (guard at App.tsx level, not here).
 * No dangerouslySetInnerHTML (R2 compliant).
 */
export function FailuresFindingsSection({
  domainSlug,
}: FailuresFindingsSectionProps) {
  const [state, setState] = useState<SectionState>("loading");
  const [data, setData] = useState<FailuresPublishedFile | null>(null);

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    let cancelled = false;
    setState("loading");
    setData(null);

    fetchFailures(domainSlug)
      .then((result) => {
        if (!cancelled) {
          // Cast through unknown at the fetch boundary (T14 doc-sweep: no shared types file modified).
          setData(result as unknown as FailuresPublishedFile);
          setState("loaded");
        }
      })
      .catch(() => {
        if (!cancelled) {
          setState("error");
        }
      });

    return () => {
      cancelled = true;
    };
  }, [domainSlug]);
  /* eslint-enable react-hooks/set-state-in-effect */

  return (
    <section
      className="failures-findings"
      aria-labelledby="failures-findings-heading"
    >
      <h2
        id="failures-findings-heading"
        className="failures-findings__heading"
      >
        {SECTION_HEADING}
      </h2>

      {/* Error state: fetch failed */}
      {state === "error" && (
        <p className="failures-findings__error">{ERROR_FETCH_FAILED}</p>
      )}

      {/* Loading state */}
      {state === "loading" && null}

      {/* Loaded state */}
      {state === "loaded" && data !== null && (
        <>
          {/* Defensive: framing_note missing / empty / non-string */}
          {typeof data.framing_note !== "string" || data.framing_note.trim() === "" ? (
            <p className="failures-findings__error">{ERROR_FRAMING_MISSING}</p>
          ) : (
            <>
              {/* framing_note rendered verbatim — byte-identical per CDA SME §5.1 */}
              <p className="failures-findings__framing">{data.framing_note}</p>

              {/* Counts caption */}
              <p className="failures-findings__counts" aria-live="polite">
                {buildCountsCaption(
                  data.n_records,
                  data.n_failure_records,
                  data.n_decline_interview_records
                )}
              </p>

              {/* Empty state — S2 verbatim */}
              {data.records.length === 0 ? (
                <p className="failures-findings__empty">{EMPTY_CAPTION}</p>
              ) : (
                /* Records list — never renders an empty <ol> */
                <ol className="failures-findings__list">
                  {data.records.map((record, index) => (
                    <FailureRecordRow
                      key={recordKey(record, index)}
                      record={record}
                    />
                  ))}
                </ol>
              )}
            </>
          )}
        </>
      )}
    </section>
  );
}
