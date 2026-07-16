/**
 * FailuresFindings — Collection records tab component.
 *
 * Renders the failures-as-findings surface as a top-level tab.
 * Self-fetches /data/failures/{domain}.json and /data/records/{domain}.json
 * in parallel on mount + domain change. OWN domain state (default 'family') --
 * NOT inherited from Explore.
 *
 * Framing: these records are LSB pipeline output properties, not
 * claims about model intent or state-of-mind. See ARCHITECTURE.md §1.5.6.
 *
 * Design bindings: DESIGN_SYSTEM.md §19 (v0.20.1).
 * CDA SME: Phase 9a T1 verdict (2026-06-08), M1-M4 applied;
 *           CR-T1 (2026-06-10); CR-T2 (2026-06-10); CR-T3 (2026-06-10);
 *           CR-T5 (2026-06-10), N1-N6 applied;
 *           CR-T6 (2026-06-10), N1-N10 applied;
 *           CR-T7 (2026-06-10), N1-N8 applied.
 *           G7-FOLLOWUP-T1 (2026-06-11) arrival highlight + no-match notice applied.
 * UI/UX: Phase 9a T1 verdict (2026-06-08), N1-N7 applied;
 *         CR-T1 through CR-T7 verdicts (2026-06-10) applied;
 *         G7-FOLLOWUP-T1 (2026-06-11) §19.19 applied.
 *
 * NO Explore chrome: no chart-lede, no Smith's S, no SelectionBar,
 * no VizTabs, no consensus strings (M4 / N7).
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import type {
  FailuresFile,
  FailuresRecord,
  FailureRecord,
  DeclineInterviewRecord,
  RecordsSummaryFile,
  RecordsModelRow,
  PublishedRecordDetail,
  RetryAttempt,
} from '../data/types';
import { isPublishedRecordDetail } from '../data/types';
import {
  IMPACT_PARAGRAPH_FAILURES,
  IMPACT_PARAGRAPH_FOLLOWUPS,
  TAXONOMY_BLOCK,
  FABLE_DISCLOSURE_FRAMING,
  FABLE_DISCLOSURE_BOUND,
  SECTION_HEADING,
  BADGE_FAILURE,
  BADGE_DECLINE,
  BLOCK_ORIGINATING_CONTEXT,
  BLOCK_PROMPT,
  BLOCK_RESPONSE,
  BLOCK_REASONING,
  BLOCK_PROVENANCE,
  countsCaptionText,
  EMPTY_CAPTION,
  LOADING_TEXT,
  FETCH_FAILED_TEXT,
  MALFORMED_TEXT,
  DOMAIN_LABEL,
  RECORDS_SECTION_HEADING,
  RECORDS_COL_MODEL,
  RECORDS_COL_PROVIDER,
  RECORDS_COL_RUNS,
  RECORDS_COL_QA_PASS,
  RECORDS_COL_VERSION,
  RECORDS_EMPTY_OBSERVATION,
  RECORDS_LINK_OUT_CAPTION,
  RECORDS_LOADING_TEXT,
  RECORDS_FETCH_FAILED_TEXT,
  RECORDS_MALFORMED_TEXT,
  RECORDS_DETAIL_FRAMING,
  RECORDS_DETAIL_EXPAND_LABEL,
  RECORDS_DETAIL_LOADING,
  RECORDS_DETAIL_FETCH_FAILED,
  RECORDS_DETAIL_MALFORMED,
  BLOCK_FREELIST_EXCHANGE,
  BLOCK_FREELIST_PROMPT,
  BLOCK_FREELIST_RESPONSE,
  BLOCK_FREELIST_REASONING,
  BLOCK_PILESORT_EXCHANGE,
  BLOCK_PILESORT_PROMPT,
  BLOCK_PILESORT_RESPONSE,
  BLOCK_PILESORT_REASONING,
  BLOCK_PILE_INTERVIEW_EXCHANGE,
  BLOCK_PILE_INTERVIEW_PROMPT,
  BLOCK_PILE_INTERVIEW_RESPONSE,
  BLOCK_PILE_INTERVIEW_REASONING,
  BLOCK_DETAIL_PROVENANCE,
  BLOCK_DETAIL_PROVENANCE_NOTE,
  BLOCK_ATTEMPTS,
  ATTEMPTS_FRAMING,
  ATTEMPTS_PARSE_ERROR_LABEL,
  pivotToRecordsArrivalCaption,
  pivotToRecordsNoMatchNotice,
} from '../copy/failures_findings';
import '../styles/failures-findings.css';

type DomainSlug = 'family' | 'holidays' | 'food';

type FetchState =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'fetch-failed'; message: string }
  | { kind: 'malformed' }
  | { kind: 'ready'; data: FailuresFile };

/** Independent fetch state for the records summary side (AC3). */
type RecordsFetchState =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'fetch-failed'; message: string }
  | { kind: 'malformed' }
  | { kind: 'ready'; data: RecordsSummaryFile };

/** Type-guard: is the fetched value a valid FailuresFile? */
function isFailuresFile(val: unknown): val is FailuresFile {
  if (typeof val !== 'object' || val === null) return false;
  const v = val as Record<string, unknown>;
  return (
    typeof v.domain_slug === 'string' &&
    typeof v.framing_note === 'string' &&
    typeof v.n_records === 'number' &&
    typeof v.n_failure_records === 'number' &&
    typeof v.n_decline_interview_records === 'number' &&
    Array.isArray(v.records)
  );
}

/** Type-guard: is the fetched value a valid RecordsSummaryFile? (AC4) */
function isRecordsSummaryFile(val: unknown): val is RecordsSummaryFile {
  if (typeof val !== 'object' || val === null) return false;
  const v = val as Record<string, unknown>;
  if (
    typeof v.domain_slug !== 'string' ||
    typeof v.generated_at !== 'string' ||
    typeof v.n_informants !== 'number' ||
    typeof v.framing_note !== 'string' ||
    !Array.isArray(v.by_model)
  ) return false;
  // Validate each row in by_model
  for (const row of v.by_model as unknown[]) {
    if (typeof row !== 'object' || row === null) return false;
    const r = row as Record<string, unknown>;
    if (
      typeof r.model_id !== 'string' ||
      typeof r.provider !== 'string' ||
      typeof r.n_runs !== 'number' ||
      typeof r.n_qa_passed !== 'number' ||
      typeof r.model_version_returned !== 'string' ||
      typeof r.model_version_returned_count !== 'number'
    ) return false;
  }
  return true;
}

/** Type-guard: is a record a FailureRecord? */
function isFailureRecord(r: FailuresRecord): r is FailureRecord {
  return r.record_type === 'failure';
}

/** Type-guard: is a record a DeclineInterviewRecord? */
function isDeclineInterviewRecord(r: FailuresRecord): r is DeclineInterviewRecord {
  return r.record_type === 'decline_interview';
}

/** Format a collection_date ISO string as YYYY-MM-DD. */
function formatDate(isoDate: string): string {
  return isoDate.slice(0, 10);
}

// ===== Behavioral-context disclosure component (DESIGN_SYSTEM.md §19.20) =====

/**
 * FableDisclosureNote renders a two-paragraph behavioral-context disclosure
 * when claude-fable-5 data is present on the failures or records surface.
 * Both paragraphs use className="failures-findings__impact".
 * Source: CDA SME ruling E (bound string 2026-07-10 (d)) / UI/UX ruling 3.
 * Strings are FABLE_DISCLOSURE_FRAMING (BA-FABLE-FRAMING) and
 * FABLE_DISCLOSURE_BOUND from failures_findings.ts.
 */
function FableDisclosureNote() {
  return (
    <>
      <p className="failures-findings__impact">{FABLE_DISCLOSURE_FRAMING}</p>
      <p className="failures-findings__impact">{FABLE_DISCLOSURE_BOUND}</p>
    </>
  );
}

// ===== Attempts block sub-component (CR-T8, §19.18) =====

interface AttemptsBlockProps {
  attempts: RetryAttempt[];
}

/**
 * Renders the pipeline retry attempts block for a FailureRecord (or defensively
 * DeclineInterviewRecord) when retry_attempts is a non-empty array.
 *
 * Per §19.18 (v0.20.3, CR-T8):
 * - Renders BLOCK_ATTEMPTS heading, ATTEMPTS_FRAMING paragraph, then each attempt in
 *   attempt_index ascending order (AC10 defensive sort).
 * - Per-attempt structure: heading line (attempt_index 0-indexed per CDA SME N1),
 *   response_verbatim in <pre>, optional stop_reason and parse_error_message in
 *   .failures-findings__provenance-list (CDA SME N2: parse_error_message framed with
 *   ATTEMPTS_PARSE_ERROR_LABEL).
 * - The parent record's prompt_verbatim is NOT repeated per attempt (AC11 / N3 rule 6).
 * - When retry_attempts is null, undefined, or [], returns null (AC7).
 */
function AttemptsBlock({ attempts }: AttemptsBlockProps) {
  if (!attempts || attempts.length === 0) return null;

  // Sort by attempt_index ascending (AC10 defensive sort regardless of array order)
  const sorted = [...attempts].sort((a, b) => a.attempt_index - b.attempt_index);

  return (
    <div className="failures-findings__attempts">
      {/* Block heading (BLOCK_ATTEMPTS, CDA SME-bound, §19.18) */}
      <div className="failures-findings__block-label">{BLOCK_ATTEMPTS}</div>
      {/* Framing paragraph (ATTEMPTS_FRAMING, CDA SME-bound, §19.18) */}
      <p className="failures-findings__attempts-framing">{ATTEMPTS_FRAMING}</p>
      {sorted.map((attempt) => (
        <div key={attempt.attempt_index} className="failures-findings__attempt">
          {/* Attempt heading: literal attempt_index 0-indexed per CDA SME N1 (audit-trail alignment) */}
          <p className="failures-findings__attempt-heading">
            attempt_index: <code>{String(attempt.attempt_index)}</code>
          </p>
          {/* Response verbatim in pre (reuses §19.7 max-height 320px via existing class) */}
          <pre className="failures-findings__pre">{attempt.response_verbatim}</pre>
          {/* Optional provenance sub-list: stop_reason and parse_error_message when present */}
          {(attempt.stop_reason != null || attempt.parse_error_message != null) && (
            <ul className="failures-findings__provenance-list">
              {attempt.stop_reason != null && (
                <li className="failures-findings__provenance-item">
                  stop_reason: <code>{attempt.stop_reason}</code>
                </li>
              )}
              {attempt.parse_error_message != null && attempt.parse_error_message !== '' && (
                <li className="failures-findings__provenance-item">
                  {/* N2 BINDING: label frames parse_error_message as LSB parser-state output */}
                  {ATTEMPTS_PARSE_ERROR_LABEL}: <code>{attempt.parse_error_message}</code>
                </li>
              )}
            </ul>
          )}
        </div>
      ))}
    </div>
  );
}

// ===== Individual record components =====

interface FailureRecordRowProps {
  record: FailureRecord;
  index: number;
}

function FailureRecordRow({ record, index }: FailureRecordRowProps) {
  const errorLen = record.error_message.length;
  return (
    <li>
      <details className="failures-findings__record">
        <summary className="failures-findings__summary">
          <span className="failures-findings__badge failures-findings__badge--failure">
            {BADGE_FAILURE}
          </span>
          <code className="failures-findings__summary-model">{record.model_id}</code>
          <span className="failures-findings__summary-date">{formatDate(record.collection_date)}</span>
          <span className="failures-findings__summary-meta">
            {record.error_type} &mdash; error_message: {errorLen} chars
            {record.originating_outcome_class !== null && (
              <> &mdash; originating_outcome_class: <code>{record.originating_outcome_class}</code></>
            )}
          </span>
        </summary>
        <div className="failures-findings__body" data-record-index={index}>
          {/* Originating context */}
          <div>
            <div className="failures-findings__block-label">{BLOCK_ORIGINATING_CONTEXT}</div>
            <ul className="failures-findings__provenance-list">
              <li className="failures-findings__provenance-item">
                run_index: <code>{String(record.run_index)}</code>
              </li>
              {record.originating_outcome_class !== null && (
                <li className="failures-findings__provenance-item">
                  originating_outcome_class: <code>{record.originating_outcome_class}</code>
                </li>
              )}
            </ul>
          </div>
          {/* Pipeline retry attempts block (CR-T8, AC8): between originating-context and error-message.
              Renders only when retry_attempts is non-empty (AC7 / AttemptsBlock guard). */}
          {record.retry_attempts && (
            <AttemptsBlock attempts={record.retry_attempts} />
          )}
          {/* Full error message */}
          <div>
            <div className="failures-findings__block-label">error_message</div>
            <pre className="failures-findings__pre">{record.error_message}</pre>
          </div>
        </div>
      </details>
    </li>
  );
}

interface DeclineInterviewRowProps {
  record: DeclineInterviewRecord;
  index: number;
}

function DeclineInterviewRow({ record, index }: DeclineInterviewRowProps) {
  const hasThinking = record.thinking_verbatim.length > 0;
  return (
    <li>
      <details className="failures-findings__record">
        <summary className="failures-findings__summary">
          <span className="failures-findings__badge failures-findings__badge--decline">
            {BADGE_DECLINE}
          </span>
          <code className="failures-findings__summary-model">{record.model_id}</code>
          <span className="failures-findings__summary-date">{formatDate(record.collection_date)}</span>
          <span className="failures-findings__summary-meta">
            originating_outcome_class: <code>{record.originating_outcome_class ?? 'null'}</code>
          </span>
        </summary>
        <div className="failures-findings__body" data-record-index={index}>
          {/* Originating context */}
          <div>
            <div className="failures-findings__block-label">{BLOCK_ORIGINATING_CONTEXT}</div>
            <ul className="failures-findings__provenance-list">
              <li className="failures-findings__provenance-item">
                originating_step: <code>{record.originating_step}</code>
              </li>
              <li className="failures-findings__provenance-item">
                originating_outcome_class:{' '}
                <code>{record.originating_outcome_class ?? 'null'}</code>
              </li>
              {record.originating_informant_id !== null && (
                <li className="failures-findings__provenance-item">
                  originating_informant_id: <code>{record.originating_informant_id}</code>
                </li>
              )}
              {record.originating_failure_id !== null && (
                <li className="failures-findings__provenance-item">
                  originating_failure_id: <code>{record.originating_failure_id}</code>
                </li>
              )}
            </ul>
          </div>
          {/* Prompt LSB sent */}
          <div>
            <div className="failures-findings__block-label">{BLOCK_PROMPT}</div>
            <pre className="failures-findings__pre">{record.prompt_verbatim}</pre>
          </div>
          {/* Model output to follow-up prompt */}
          <div>
            <div className="failures-findings__block-label">{BLOCK_RESPONSE}</div>
            <pre className="failures-findings__pre">{record.response_verbatim}</pre>
          </div>
          {/* Reasoning trace — only when non-empty */}
          {hasThinking && (
            <div>
              <div className="failures-findings__block-label">{BLOCK_REASONING}</div>
              <pre className="failures-findings__pre">{record.thinking_verbatim}</pre>
            </div>
          )}
          {/* Pipeline retry attempts block (CR-T8, AC12 defensive): below response block.
              Runtime expectation: absent on decline_interview records. Renders nothing if absent. */}
          {record.retry_attempts && (
            <AttemptsBlock attempts={record.retry_attempts} />
          )}
          {/* Provenance IDs */}
          <div>
            <div className="failures-findings__block-label">{BLOCK_PROVENANCE}</div>
            <ul className="failures-findings__provenance-list">
              <li className="failures-findings__provenance-item">
                model_version_returned: <code>{record.model_version_returned}</code>
              </li>
              <li className="failures-findings__provenance-item">
                provider: <code>{record.provider}</code>
              </li>
              <li className="failures-findings__provenance-item">
                api_endpoint: <code>{record.api_endpoint}</code>
              </li>
              <li className="failures-findings__provenance-item">
                sha256_manifest: <code>{record.sha256_manifest}</code>
              </li>
              <li className="failures-findings__provenance-item">
                tokens: input <code>{String(record.input_tokens)}</code> / output{' '}
                <code>{String(record.output_tokens)}</code>
              </li>
              <li className="failures-findings__provenance-item">
                latency_ms: <code>{String(record.latency_ms)}</code>
              </li>
              <li className="failures-findings__provenance-item">
                stop_reason: <code>{record.stop_reason}</code>
              </li>
            </ul>
          </div>
        </div>
      </details>
    </li>
  );
}

// ===== Main component =====

/** Props for the FailuresFindings component. */
interface FailuresFindingsProps {
  /**
   * Optional transient pivot target from App.tsx (G7-FOLLOWUP-T1, §19.19.5).
   * When non-null, the component: (a) aligns internal domain state, (b) after
   * the records fetch resolves, scrolls to and highlights the matching row,
   * (c) calls onPivotTargetConsumed to clear the state.
   */
  pivotTarget?: { modelId: string; domainSlug: DomainSlug } | null;
  /** Callback to clear the pivot target after consumption (§19.19.6). */
  onPivotTargetConsumed?: () => void;
}

export function FailuresFindings({
  pivotTarget = null,
  onPivotTargetConsumed,
}: FailuresFindingsProps = {}) {
  // OWN domain state, defaults to 'family' per UI/UX N1 binding.
  // NOT inherited from Explore.
  const [domain, setDomain] = useState<DomainSlug>('family');
  const [fetchState, setFetchState] = useState<FetchState>({ kind: 'idle' });
  const [recordsFetchState, setRecordsFetchState] = useState<RecordsFetchState>({ kind: 'idle' });

  // Abort controller ref for cancellation on domain change.
  // Both fetches share one AbortController (AC2).
  const abortRef = useRef<AbortController | null>(null);

  // Align domain state when a pivot target arrives (G7-FOLLOWUP-T1, §19.19.6 step 1).
  // The records fetch in RecordsSummarySection will re-fire once domain state updates.
  useEffect(() => {
    if (pivotTarget != null && pivotTarget.domainSlug !== domain) {
      setDomain(pivotTarget.domainSlug); // eslint-disable-line react-hooks/set-state-in-effect
    }
  }, [pivotTarget]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    // Cancel any in-flight requests
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    const load = async () => {
      // Both fetches start in loading state before Promise.all resolves (AC2).
      setFetchState({ kind: 'loading' });
      setRecordsFetchState({ kind: 'loading' });

      // Run both fetches in parallel against the same AbortController (AC2).
      const [failuresResult, recordsResult] = await Promise.allSettled([
        fetch(`/data/failures/${domain}.json`, { signal: controller.signal }),
        fetch(`/data/records/${domain}.json`, { signal: controller.signal }),
      ]);

      // Handle failures side (independent of records side per AC3)
      if (failuresResult.status === 'rejected') {
        const e = failuresResult.reason as Error;
        if (e.name === 'AbortError') return;
        setFetchState({
          kind: 'fetch-failed',
          message: e instanceof Error ? e.message : 'Unknown error',
        });
      } else {
        const resp = failuresResult.value;
        if (!resp.ok) {
          setFetchState({ kind: 'fetch-failed', message: `HTTP ${resp.status}` });
        } else {
          try {
            const raw: unknown = await resp.json();
            if (!isFailuresFile(raw)) {
              setFetchState({ kind: 'malformed' });
            } else {
              setFetchState({ kind: 'ready', data: raw });
            }
          } catch {
            setFetchState({ kind: 'fetch-failed', message: 'JSON parse error' });
          }
        }
      }

      // Handle records side independently (AC3)
      if (recordsResult.status === 'rejected') {
        const e = recordsResult.reason as Error;
        if (e.name === 'AbortError') return;
        setRecordsFetchState({
          kind: 'fetch-failed',
          message: e instanceof Error ? e.message : 'Unknown error',
        });
      } else {
        const resp = recordsResult.value;
        if (!resp.ok) {
          setRecordsFetchState({ kind: 'fetch-failed', message: `HTTP ${resp.status}` });
        } else {
          try {
            const raw: unknown = await resp.json();
            if (!isRecordsSummaryFile(raw)) {
              setRecordsFetchState({ kind: 'malformed' });
            } else {
              setRecordsFetchState({ kind: 'ready', data: raw });
            }
          } catch {
            setRecordsFetchState({ kind: 'fetch-failed', message: 'JSON parse error' });
          }
        }
      }
    };

    void load();
    return () => {
      controller.abort();
    };
  }, [domain]);

  return (
    <div className="failures-findings">
      {/* Page heading (CDA SME M2 / T10 SECTION_HEADING verbatim) */}
      <h1 className="failures-findings__heading">{SECTION_HEADING}</h1>

      {/* Domain selector (OWN state, distinct id from Sidebar) */}
      <div className="failures-findings__domain-row">
        <label
          htmlFor="failures-domain-select"
          className="failures-findings__domain-label"
        >
          {DOMAIN_LABEL}
        </label>
        <select
          id="failures-domain-select"
          className="failures-findings__domain-select"
          value={domain}
          onChange={(e) => setDomain(e.target.value as DomainSlug)}
        >
          <option value="family">Family</option>
          <option value="holidays">Holidays</option>
          <option value="food">Food</option>
        </select>
      </div>

      {/* Content area */}
      {fetchState.kind === 'loading' && (
        <p className="failures-findings__status">{LOADING_TEXT}</p>
      )}

      {fetchState.kind === 'fetch-failed' && (
        <p className="failures-findings__status">{FETCH_FAILED_TEXT}</p>
      )}

      {fetchState.kind === 'malformed' && (
        <p className="failures-findings__status">{MALFORMED_TEXT}</p>
      )}

      {fetchState.kind === 'ready' && (() => {
        const data = fetchState.data;
        return (
          <>
            {/* Impact paragraph (CR-T1, v0.15.1) — Mark-authored; renders in ready-state only (AC4).
                Placed before framing_note per UI/UX F3 / §19.4 step 3. */}
            <p className="failures-findings__impact">{IMPACT_PARAGRAPH_FAILURES}</p>

            {/* Taxonomy block (CR-T3, v0.19.3): CDA SME-approved; renders in ready-state only.
                Renders in empty-state path (n_records === 0): taxonomy is a property of the LSB
                pipeline, not of the per-domain data. Placement: §19.4 step 4 (between impact
                paragraph and framing_note). See DESIGN_SYSTEM.md §19.14. */}
            <section
              aria-labelledby="taxonomy-block-heading"
              className="failures-findings__taxonomy"
            >
              <h2
                id="taxonomy-block-heading"
                className="failures-findings__taxonomy-heading"
              >
                {TAXONOMY_BLOCK.heading}
              </h2>
              <p className="failures-findings__taxonomy-bridge">
                {TAXONOMY_BLOCK.bridge}
              </p>
              <ul className="failures-findings__taxonomy-list">
                {TAXONOMY_BLOCK.topLevel.map(row => (
                  <li key={row.term}>
                    <strong>{row.term}</strong>{' '}{row.description}
                  </li>
                ))}
              </ul>
              <p className="failures-findings__taxonomy-enum-label">
                <code>originating_outcome_class</code>{' '}ENUM VALUES (seven, byte-identical to the schema):
              </p>
              <ul className="failures-findings__taxonomy-list">
                {TAXONOMY_BLOCK.enumValues.map(row => (
                  <li key={row.id}>
                    <code>{row.id}</code>{' '}{row.description}
                  </li>
                ))}
              </ul>
            </section>

            {/* Framing note verbatim: first data-sourced content paragraph (T9 §5.1 / AC5).
                Step 5 in §19.4 content order (after taxonomy block). */}
            <p className="failures-findings__framing-note">{data.framing_note}</p>

            {/* Counts caption (CR-T6, v0.19.5): four-cell empty-state matrix per CDA SME N3.
                nParsedResponses sourced from recordsFetchState.data.n_informants when ready;
                undefined when records side not ready (CDA SME N4: failures-only caption, no inline
                spinner). Caption omitted when countsCaptionText returns empty string. */}
            {(() => {
              const nParsedResponses =
                recordsFetchState.kind === "ready"
                  ? recordsFetchState.data.n_informants
                  : undefined;
              const captionText = countsCaptionText(
                data.n_records,
                data.n_failure_records,
                data.n_decline_interview_records,
                nParsedResponses,
              );
              return captionText ? (
                <p className="failures-findings__counts">{captionText}</p>
              ) : null;
            })()}

            {/* Fable behavioral-context disclosure (DESIGN_SYSTEM.md §19.20, UI/UX ruling 3).
                Renders after counts caption, before records list, when claude-fable-5 is present. */}
            {data.records.some(r => r.model_id === 'claude-fable-5') && (
              <FableDisclosureNote />
            )}

            {/* Records list or empty state */}
            {data.n_records === 0 ? (
              /* Empty state (T10 S2 verbatim / AC9) — first-class, not a defect */
              <p className="failures-findings__empty">{EMPTY_CAPTION}</p>
            ) : (() => {
              /* Split records into failure and decline-interview groups (CR-T2 / §19.4 step 6). */
              const failureRecords = data.records.filter(isFailureRecord);
              const declineRecords = data.records.filter(isDeclineInterviewRecord);
              const hasDecline = declineRecords.length > 0;
              return (
                <>
                  {/* Failure records group */}
                  {failureRecords.length > 0 && (
                    <ol className="failures-findings__list">
                      {failureRecords.map((record, i) => (
                        <FailureRecordRow key={`failure-${i}`} record={record} index={i} />
                      ))}
                    </ol>
                  )}

                  {/* Follow-up interviews impact paragraph (CR-T2, v0.19.2).
                      Renders only when at least one decline_interview record is present (AC3). */}
                  {hasDecline && (
                    <p className="failures-findings__impact">{IMPACT_PARAGRAPH_FOLLOWUPS}</p>
                  )}

                  {/* Decline-interview records group */}
                  {hasDecline && (
                    <ol className="failures-findings__list">
                      {declineRecords.map((record, i) => (
                        <DeclineInterviewRow key={`decline-${i}`} record={record} index={i} />
                      ))}
                    </ol>
                  )}
                </>
              );
            })()}
          </>
        );
      })()}

      {/* Records summary section (CR-T5, v0.19.4): independent of failures side (AC3).
          Placement: below the failures/decline-interviews list (or below EMPTY_CAPTION
          when n_records === 0). See DESIGN_SYSTEM.md §19.15.
          G7-FOLLOWUP-T1: pivot target + consumed callback passed for arrival highlight. */}
      <RecordsSummarySection
        recordsFetchState={recordsFetchState}
        domainSlug={domain}
        pivotTarget={pivotTarget}
        onPivotTargetConsumed={onPivotTargetConsumed}
      />

      {/* idle state renders nothing (initial state before first fetch resolves) */}
    </div>
  );
}

// ===== Per-record detail fetch state and component (CR-T7) =====

/** Lazy-fetch state for a single per-record detail row (NOTE-4 / §19.17). */
type DetailFetchState =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'fetch-failed' }
  | { kind: 'malformed' }
  | { kind: 'ready'; data: PublishedRecordDetail };

/**
 * Step constants mapping for the three CDA steps.
 * exchange: outer step heading label (BLOCK_*_EXCHANGE, CDA SME N1).
 * prompt/response/reasoning: inner sub-block labels (N4 per-step register).
 */
const STEP_CONFIG = [
  {
    key: 'freelist' as const,
    exchange: BLOCK_FREELIST_EXCHANGE,
    prompt: BLOCK_FREELIST_PROMPT,
    response: BLOCK_FREELIST_RESPONSE,
    reasoning: BLOCK_FREELIST_REASONING,
  },
  {
    key: 'pile_sort' as const,
    exchange: BLOCK_PILESORT_EXCHANGE,
    prompt: BLOCK_PILESORT_PROMPT,
    response: BLOCK_PILESORT_RESPONSE,
    reasoning: BLOCK_PILESORT_REASONING,
  },
  {
    key: 'pile_interview' as const,
    exchange: BLOCK_PILE_INTERVIEW_EXCHANGE,
    prompt: BLOCK_PILE_INTERVIEW_PROMPT,
    response: BLOCK_PILE_INTERVIEW_RESPONSE,
    reasoning: BLOCK_PILE_INTERVIEW_REASONING,
  },
] as const;

interface RecordDetailBodyProps {
  detail: PublishedRecordDetail;
}

/**
 * Renders the full per-record detail body: RECORDS_DETAIL_FRAMING caption,
 * three CDA step sections with sub-block labels, and the provenance block.
 * Per §19.17 binding detail body structure.
 */
function RecordDetailBody({ detail }: RecordDetailBodyProps) {
  return (
    <div>
      {/* In-page caption (RECORDS_DETAIL_FRAMING, SME-bound) */}
      <p className="failures-findings__framing-note">{RECORDS_DETAIL_FRAMING}</p>

      {/* Three CDA step sections (§19.17 step section structure) */}
      {STEP_CONFIG.map(({ key, exchange, prompt, response, reasoning }) => {
        const step = detail[key];
        if (!step) return null;
        return (
          <div key={key} className="failures-findings__detail-step">
            {/* Outer step heading (BLOCK_*_EXCHANGE, CDA SME N1 naming) */}
            <p className="failures-findings__detail-step-heading">
              {exchange}
            </p>
            {/* Prompt sub-block */}
            <p className="failures-findings__block-label">{prompt}</p>
            <pre className="failures-findings__pre">{step.prompt_verbatim}</pre>
            {/* Response sub-block */}
            <p className="failures-findings__block-label">{response}</p>
            <pre className="failures-findings__pre">{step.response_verbatim}</pre>
            {/* Reasoning sub-block: only when thinking_verbatim is non-empty */}
            {step.thinking_verbatim && (
              <>
                <p className="failures-findings__block-label">{reasoning}</p>
                <pre className="failures-findings__pre">{step.thinking_verbatim}</pre>
              </>
            )}
          </div>
        );
      })}

      {/* Provenance block (§19.17 provenance block) */}
      <p className="failures-findings__block-label">{BLOCK_DETAIL_PROVENANCE}</p>
      <p className="failures-findings__framing-note">{BLOCK_DETAIL_PROVENANCE_NOTE}</p>
      <ul className="failures-findings__provenance-list">
        <li className="failures-findings__provenance-item">
          provider_request_id: <code>{detail.provenance.provider_request_id || '(none)'}</code>
        </li>
        <li className="failures-findings__provenance-item">
          model_id: <code>{detail.provenance.model_id}</code>
        </li>
        <li className="failures-findings__provenance-item">
          model_version_returned: <code>{detail.provenance.model_version_returned}</code>
        </li>
        {Object.entries(detail.provenance.sha256_manifest).map(([key, val]) => (
          <li key={key} className="failures-findings__provenance-item">
            {key}: <code>{val}</code>
          </li>
        ))}
      </ul>
    </div>
  );
}

// ===== Records summary section component (CR-T5, extended CR-T7) =====

interface RecordsSummarySectionProps {
  recordsFetchState: RecordsFetchState;
  domainSlug: string;
  /** Transient pivot target to scroll to and highlight (G7-FOLLOWUP-T1, §19.19.6). */
  pivotTarget?: { modelId: string; domainSlug: DomainSlug } | null;
  /** Callback to clear the pivot target after consumption (§19.19.6). */
  onPivotTargetConsumed?: () => void;
}

/**
 * Renders the per-model summary of parsed primary-step responses.
 * Independent of the failures side fetch state (AC3, AC5).
 * Section structure mirrors §19.14 taxonomy block pattern (AC5, §19.15).
 * CR-T7: adds expand column + per-row detail surface (§19.17).
 */
function RecordsSummarySection({
  recordsFetchState,
  domainSlug,
  pivotTarget,
  onPivotTargetConsumed,
}: RecordsSummarySectionProps) {
  /**
   * Arrival notice state (G7-FOLLOWUP-T1, DESIGN_SYSTEM.md §19.19.6).
   * 'caption' = matching row found; 'no-match' = no row found; null = inactive.
   * Text is the formatted string; duration handled by useEffect cleanup.
   */
  const [arrivalNotice, setArrivalNotice] = useState<{
    kind: 'caption' | 'no-match';
    text: string;
    modelId: string;
  } | null>(null);

  /** Ref map from model_id to the <tr> DOM element for scrollIntoView. */
  const rowRefs = useRef<Map<string, HTMLTableRowElement>>(new Map());

  /**
   * Consume the pivot target when it is non-null and the records side is ready.
   * Per §19.19.6:
   *   1. Align domain (handled by FailuresFindings main component via setDomain).
   *   2. Locate the matching <tr> by model_id.
   *   3. scrollIntoView.
   *   4. Apply arrival-highlight class for 2000ms via CSS animation.
   *   5. Render arrival caption or no-match notice for 2000ms.
   *   6. Call onPivotTargetConsumed.
   */
  useEffect(() => {
    if (pivotTarget == null || recordsFetchState.kind !== 'ready') return;
    if (pivotTarget.domainSlug !== domainSlug) return; // domain not yet aligned

    const { modelId } = pivotTarget;
    const data = recordsFetchState.data;

    // Build domainLabel from domainSlug (capitalize first letter)
    const domainLabel = domainSlug.charAt(0).toLowerCase() + domainSlug.slice(1);
    // modelLabel: use modelId (display name not available at this scope without full models list)
    const modelLabel = modelId;

    const row = data.by_model.find((r) => r.model_id === modelId);

    if (row != null) {
      // Found a matching row: scroll to it, apply highlight, show arrival caption.
      const trEl = rowRefs.current.get(modelId);
      if (trEl && typeof trEl.scrollIntoView === 'function') {
        trEl.scrollIntoView({ block: 'center', behavior: 'smooth' });
      }
      setArrivalNotice({ kind: 'caption', text: pivotToRecordsArrivalCaption(modelLabel, domainLabel), modelId }); // eslint-disable-line react-hooks/set-state-in-effect
    } else {
      // No matching row: show no-match notice.
      setArrivalNotice({ kind: 'no-match', text: pivotToRecordsNoMatchNotice(modelLabel, domainLabel), modelId });
    }

    // Consume the target immediately so re-visits don't re-fire.
    onPivotTargetConsumed?.();

    // Auto-clear the notice after 2000ms (§19.19.7 duration).
    const timer = window.setTimeout(() => {
      setArrivalNotice(null);
    }, 2000);

    return () => {
      window.clearTimeout(timer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pivotTarget, recordsFetchState]);

  const setRowRef = useCallback((modelId: string, el: HTMLTableRowElement | null) => {
    if (el) {
      rowRefs.current.set(modelId, el);
    } else {
      rowRefs.current.delete(modelId);
    }
  }, []);

  if (recordsFetchState.kind === 'loading') {
    return (
      <p className="failures-findings__status failures-findings__successes-status">
        {RECORDS_LOADING_TEXT}
      </p>
    );
  }

  if (recordsFetchState.kind === 'fetch-failed') {
    return (
      <p className="failures-findings__status failures-findings__successes-status">
        {RECORDS_FETCH_FAILED_TEXT}
      </p>
    );
  }

  if (recordsFetchState.kind === 'malformed') {
    return (
      <p className="failures-findings__status failures-findings__successes-status">
        {RECORDS_MALFORMED_TEXT}
      </p>
    );
  }

  if (recordsFetchState.kind === 'idle') {
    return null;
  }

  // ready state
  const data = recordsFetchState.data;

  return (
    <section
      aria-labelledby="records-summary-heading"
      className="failures-findings__successes"
    >
      <h2
        id="records-summary-heading"
        className="failures-findings__taxonomy-heading failures-findings__successes-heading"
      >
        {RECORDS_SECTION_HEADING}
      </h2>

      {/* framing_note verbatim (AC6): byte-identical to the CR-T4-published string */}
      <p className="failures-findings__framing-note failures-findings__successes-framing">
        {data.framing_note}
      </p>

      {/* Arrival notice (G7-FOLLOWUP-T1, §19.19.6): renders for 2000ms after pivot lands.
          'caption' = matching row found (arrival orientation).
          'no-match' = model not in table (scoping rule explanation). */}
      {arrivalNotice != null && arrivalNotice.kind === 'caption' && (
        <p className="failures-findings__pivot-arrival-caption">
          {arrivalNotice.text}
        </p>
      )}
      {arrivalNotice != null && arrivalNotice.kind === 'no-match' && (
        <p className="failures-findings__pivot-arrival-notice">
          {arrivalNotice.text}
        </p>
      )}

      {/* Fable behavioral-context disclosure (DESIGN_SYSTEM.md §19.20, UI/UX ruling 3).
          Renders before the summary table when claude-fable-5 is present in by_model. */}
      {data.by_model.some(r => r.model_id === 'claude-fable-5') && (
        <FableDisclosureNote />
      )}

      {/* Per-model table or zero-runs empty state (AC7, AC8) */}
      {data.by_model.length === 0 ? (
        /* Zero-runs first-class observation state (AC8, CR-T4 N3 carry-forward) */
        <p className="failures-findings__empty failures-findings__successes-empty">
          {RECORDS_EMPTY_OBSERVATION}
        </p>
      ) : (
        /* Per-model table (AC7): rows in artifact order (lexicographic by model_id),
           no client-side sorting, no sortable headers (AC16).
           CR-T7: 6 columns total (5 data + 1 expand). colSpan on detail row = 6. */
        <div className="failures-findings__successes-table-wrapper">
          <table className="failures-findings__successes-table">
            <caption className="sr-only">
              {RECORDS_SECTION_HEADING}
            </caption>
            <thead>
              <tr>
                <th scope="col" className="failures-findings__successes-th">{RECORDS_COL_MODEL}</th>
                <th scope="col" className="failures-findings__successes-th">{RECORDS_COL_PROVIDER}</th>
                <th scope="col" className="failures-findings__successes-th">{RECORDS_COL_RUNS}</th>
                <th scope="col" className="failures-findings__successes-th">{RECORDS_COL_QA_PASS}</th>
                <th scope="col" className="failures-findings__successes-th">{RECORDS_COL_VERSION}</th>
                {/* Expand column (NOTE-2 / §19.17): visually empty, accessible name via aria-label */}
                <th
                  scope="col"
                  className="failures-findings__successes-th"
                  aria-label="Expand record details"
                />
              </tr>
            </thead>
            <tbody>
              {data.by_model.map((row) => (
                // Fragment key on model_id -- each row expands to two <tr> elements.
                <ExpandableModelRow
                  key={row.model_id}
                  row={row}
                  domainSlug={domainSlug}
                  isHighlighted={arrivalNotice?.kind === 'caption' && arrivalNotice.modelId === row.model_id}
                  rowRef={(el) => setRowRef(row.model_id, el)}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Link-out caption (AC12): points to Data tab, no external links */}
      <p className="failures-findings__successes-caption">
        {RECORDS_LINK_OUT_CAPTION}
      </p>
    </section>
  );
}

/** Props for an expandable model data row + its sibling detail row. */
interface ExpandableModelRowProps {
  row: RecordsModelRow;
  domainSlug: string;
  /** When true, apply the pivot-arrival highlight CSS class (G7-FOLLOWUP-T1, §19.19.7). */
  isHighlighted?: boolean;
  /** Ref callback for the data <tr> element; used for scrollIntoView on pivot (§19.19.6). */
  rowRef?: (el: HTMLTableRowElement | null) => void;
}

/**
 * Renders one data <tr> with five data cells and one expand button cell,
 * plus a sibling detail <tr> (colSpan={6}). The two <tr> elements are wrapped
 * in a React Fragment keyed on model_id. Fetch state is managed inline per
 * NOTE-4 / §19.17 lazy-fetch spec.
 */
function ExpandableModelRow({ row, domainSlug, isHighlighted = false, rowRef }: ExpandableModelRowProps) {

  const [isExpanded, setIsExpanded] = useState(false);
  const [detailState, setDetailState] = useState<DetailFetchState>({ kind: 'idle' });
  const cachedDataRef = useRef<PublishedRecordDetail | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    return () => {
      abortRef.current?.abort();
    };
  }, []);

  function handleToggle() {
    const next = !isExpanded;
    setIsExpanded(next);

    if (next) {
      if (cachedDataRef.current !== null) {
        setDetailState({ kind: 'ready', data: cachedDataRef.current });
        return;
      }

      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setDetailState({ kind: 'loading' });

      const url = `/data/records/${domainSlug}/detail/${row.model_id}.json`;
      fetch(url, { signal: controller.signal })
        .then(async (resp) => {
          if (!resp.ok) {
            setDetailState({ kind: 'fetch-failed' });
            return;
          }
          try {
            const raw: unknown = await resp.json();
            if (!isPublishedRecordDetail(raw)) {
              setDetailState({ kind: 'malformed' });
            } else {
              cachedDataRef.current = raw;
              setDetailState({ kind: 'ready', data: raw });
            }
          } catch {
            setDetailState({ kind: 'fetch-failed' });
          }
        })
        .catch((err: unknown) => {
          if (err instanceof Error && err.name === 'AbortError') return;
          setDetailState({ kind: 'fetch-failed' });
        });
    }
  }

  return (
    <>
      {/* Data row with 5 data cells + expand button cell (6th).
          isHighlighted applies the pivot-arrival CSS animation class (G7-FOLLOWUP-T1, §19.19.7).
          rowRef passes the DOM element to RecordsSummarySection for scrollIntoView (§19.19.6). */}
      <tr
        className={`failures-findings__successes-tr${isHighlighted ? ' failures-findings__successes-tr--pivot-arrival' : ''}`}
        ref={rowRef}
      >
        <td className="failures-findings__successes-td">
          <code className="failures-findings__successes-code">{row.model_id}</code>
        </td>
        <td className="failures-findings__successes-td">
          <code className="failures-findings__successes-code">{row.provider}</code>
        </td>
        <td className="failures-findings__successes-td failures-findings__successes-td--num">
          {row.n_runs}
        </td>
        <td className="failures-findings__successes-td failures-findings__successes-td--num">
          {row.n_qa_passed}
        </td>
        <td className="failures-findings__successes-td">
          <code className="failures-findings__successes-code">{row.model_version_returned}</code>
        </td>
        {/* Expand button cell (6th column, NOTE-1 / §19.17) */}
        <td className="failures-findings__successes-td">
          <button
            className="failures-findings__expand-btn"
            aria-expanded={isExpanded}
            aria-label={`Expand raw exchange for ${row.model_id}`}
            title={RECORDS_DETAIL_EXPAND_LABEL}
            onClick={handleToggle}
          >
            {isExpanded ? '▼' : '▶'}
          </button>
        </td>
      </tr>
      {/* Sibling detail row (NOTE-1 / §19.17): display:none when collapsed */}
      <tr
        className="failures-findings__detail-row"
        style={{ display: isExpanded ? undefined : 'none' }}
      >
        <td className="failures-findings__detail-cell" colSpan={6}>
          {detailState.kind === 'loading' && (
            <p className="failures-findings__status">{RECORDS_DETAIL_LOADING}</p>
          )}
          {detailState.kind === 'fetch-failed' && (
            <p className="failures-findings__status">{RECORDS_DETAIL_FETCH_FAILED}</p>
          )}
          {detailState.kind === 'malformed' && (
            <p className="failures-findings__status">{RECORDS_DETAIL_MALFORMED}</p>
          )}
          {detailState.kind === 'ready' && (
            <RecordDetailBody detail={detailState.data} />
          )}
        </td>
      </tr>
    </>
  );
}
