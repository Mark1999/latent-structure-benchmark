/**
 * FailuresFindings — Collection records tab component.
 *
 * Renders the failures-as-findings surface as a top-level tab.
 * Self-fetches /data/failures/{domain}.json on mount + domain change.
 * OWN domain state (default 'family') — NOT inherited from Explore.
 *
 * Framing: these records are LSB pipeline output properties, not
 * claims about model intent or state-of-mind. See ARCHITECTURE.md §1.5.6.
 *
 * Design bindings: DESIGN_SYSTEM.md §19 (v0.15.0).
 * CDA SME: Phase 9a T1 verdict (2026-06-08), M1-M4 applied.
 * UI/UX: Phase 9a T1 verdict (2026-06-08), N1-N7 applied.
 *
 * NO Explore chrome: no chart-lede, no Smith's S, no SelectionBar,
 * no VizTabs, no consensus strings (M4 / N7).
 */

import { useState, useEffect, useRef } from 'react';
import type { FailuresFile, FailuresRecord, FailureRecord, DeclineInterviewRecord } from '../data/types';
import {
  IMPACT_PARAGRAPH_FAILURES,
  IMPACT_PARAGRAPH_FOLLOWUPS,
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
} from '../copy/failures_findings';
import '../styles/failures-findings.css';

type DomainSlug = 'family' | 'holidays' | 'food';

type FetchState =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'fetch-failed'; message: string }
  | { kind: 'malformed' }
  | { kind: 'ready'; data: FailuresFile };

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

export function FailuresFindings() {
  // OWN domain state, defaults to 'family' per UI/UX N1 binding.
  // NOT inherited from Explore.
  const [domain, setDomain] = useState<DomainSlug>('family');
  const [fetchState, setFetchState] = useState<FetchState>({ kind: 'idle' });

  // Abort controller ref for cancellation on domain change
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    // Cancel any in-flight request
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    const load = async () => {
      setFetchState({ kind: 'loading' });
      try {
        const resp = await fetch(`/data/failures/${domain}.json`, {
          signal: controller.signal,
        });
        if (!resp.ok) {
          setFetchState({ kind: 'fetch-failed', message: `HTTP ${resp.status}` });
          return;
        }
        const raw: unknown = await resp.json();
        if (!isFailuresFile(raw)) {
          setFetchState({ kind: 'malformed' });
          return;
        }
        setFetchState({ kind: 'ready', data: raw });
      } catch (e) {
        if (e instanceof Error && e.name === 'AbortError') return;
        setFetchState({
          kind: 'fetch-failed',
          message: e instanceof Error ? e.message : 'Unknown error',
        });
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

            {/* Framing note verbatim — first <p> below heading (T9 §5.1 / AC5) */}
            <p className="failures-findings__framing-note">{data.framing_note}</p>

            {/* Counts caption — omitted when n_records === 0 (UI/UX N1) */}
            {data.n_records > 0 && (
              <p className="failures-findings__counts">
                {countsCaptionText(
                  data.n_records,
                  data.n_failure_records,
                  data.n_decline_interview_records,
                )}
              </p>
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

      {/* idle state renders nothing (initial state before first fetch resolves) */}
    </div>
  );
}
