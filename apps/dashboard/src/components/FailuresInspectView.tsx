/**
 * FailuresInspectView — flat-table inspect view for failure records.
 *
 * Used by InspectRoot for ?inspect=failures-{slug} mode.
 * Per T0 flat-table posture: every field of every record, no <details> collapse.
 * (The no-<details> constraint applies to the operator surface only; the public
 * surface FailuresFindingsSection uses <details> per plan §2.6.)
 *
 * Source: Phase 6 T10 plan §2.8 (InspectRoot extension)
 * Reference: docs/status/2026-05-12-phase6-T10-architect-plan.md §2.8
 */

import type { FailuresPublishedFile, FailureRecord } from "./FailuresFindingsSection";
import { InspectSection } from "./InspectSection";
import { InspectTable } from "./InspectTable";
import type { ColumnDef } from "./InspectTable";

// ── Column definitions ─────────────────────────────────────────────────────────

const COMMON_COLS: ColumnDef[] = [
  { key: "record_type", label: "record_type" },
  { key: "collection_date", label: "collection_date" },
  { key: "model_id", label: "model_id" },
  { key: "domain_slug", label: "domain_slug" },
  { key: "originating_outcome_class", label: "originating_outcome_class" },
];

const FAILURE_COLS: ColumnDef[] = [
  ...COMMON_COLS,
  { key: "error_type", label: "error_type" },
  { key: "run_index", label: "run_index" },
  { key: "error_message", label: "error_message" },
  { key: "retry_attempts", label: "retry_attempts" },
  { key: "partial_session", label: "partial_session" },
];

const DECLINE_INTERVIEW_COLS: ColumnDef[] = [
  ...COMMON_COLS,
  { key: "decline_interview_id", label: "decline_interview_id" },
  { key: "originating_informant_id", label: "originating_informant_id" },
  { key: "originating_failure_id", label: "originating_failure_id" },
  { key: "originating_step", label: "originating_step" },
  { key: "detection_rule_version", label: "detection_rule_version" },
  { key: "model_version_returned", label: "model_version_returned" },
  { key: "provider", label: "provider" },
  { key: "api_endpoint", label: "api_endpoint" },
  { key: "prompt_version", label: "prompt_version" },
  { key: "sha256_manifest", label: "sha256_manifest" },
  { key: "prompt_verbatim", label: "prompt_verbatim" },
  { key: "response_verbatim", label: "response_verbatim" },
  { key: "thinking_verbatim", label: "thinking_verbatim" },
  { key: "input_tokens", label: "input_tokens" },
  { key: "output_tokens", label: "output_tokens" },
  { key: "latency_ms", label: "latency_ms" },
  { key: "stop_reason", label: "stop_reason" },
  { key: "qa_notes", label: "qa_notes" },
  { key: "version_drift_flag", label: "version_drift_flag" },
];

// ── Row serializer ─────────────────────────────────────────────────────────────

function recordToRow(record: FailureRecord): Record<string, unknown> {
  const row: Record<string, unknown> = {};
  // Enumerate all possible keys — InspectTable renders whatever is in the row
  const keys = Object.keys(record) as (keyof FailureRecord)[];
  for (const key of keys) {
    const val = record[key];
    if (val !== undefined) {
      if (typeof val === "object" && val !== null) {
        row[key] = JSON.stringify(val);
      } else {
        row[key] = val;
      }
    } else {
      row[key] = null;
    }
  }
  return row;
}

// ── Header fields table ─────────────────────────────────────────────────────────

const HEADER_COLS: ColumnDef[] = [
  { key: "field", label: "Field" },
  { key: "value", label: "Value" },
];

function makeHeaderRows(data: FailuresPublishedFile): Record<string, unknown>[] {
  return [
    { field: "domain_slug", value: data.domain_slug },
    { field: "generated_at", value: data.generated_at },
    { field: "n_records", value: data.n_records },
    { field: "n_failure_records", value: data.n_failure_records },
    { field: "n_decline_interview_records", value: data.n_decline_interview_records },
    { field: "framing_note", value: data.framing_note },
  ];
}

// ── FailuresInspectView ────────────────────────────────────────────────────────

export interface FailuresInspectViewProps {
  data: FailuresPublishedFile;
  slug: string;
}

export function FailuresInspectView({ data, slug }: FailuresInspectViewProps) {
  const failureRecords = data.records.filter((r) => r.record_type === "failure");
  const declineRecords = data.records.filter(
    (r) => r.record_type === "decline_interview"
  );

  return (
    <>
      <InspectSection title={`Failures file header (${slug})`}>
        <InspectTable
          caption={`failures/${slug}.json top-level fields`}
          columns={HEADER_COLS}
          rows={makeHeaderRows(data)}
        />
      </InspectSection>

      <InspectSection
        title={`Collection failures (${failureRecords.length})`}
        description={
          failureRecords.length === 0
            ? "No collection failure records in this file."
            : undefined
        }
      >
        {failureRecords.length > 0 && (
          <InspectTable
            caption={`Collection failures — ${failureRecords.length} record${failureRecords.length !== 1 ? "s" : ""}`}
            columns={FAILURE_COLS}
            rows={failureRecords.map(recordToRow)}
          />
        )}
      </InspectSection>

      <InspectSection
        title={`Follow-up interviews (${declineRecords.length})`}
        description={
          declineRecords.length === 0
            ? "No follow-up interview records in this file."
            : undefined
        }
      >
        {declineRecords.length > 0 && (
          <InspectTable
            caption={`Follow-up interviews — ${declineRecords.length} record${declineRecords.length !== 1 ? "s" : ""}`}
            columns={DECLINE_INTERVIEW_COLS}
            rows={declineRecords.map(recordToRow)}
          />
        )}
      </InspectSection>
    </>
  );
}
