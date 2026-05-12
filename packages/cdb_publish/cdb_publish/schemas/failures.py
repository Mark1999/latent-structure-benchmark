"""Publish-layer schema for the per-domain failures JSON output.

These are dashboard-internal schemas that describe the shape of
apps/dashboard/public/data/failures/{slug}.json. They are NOT part of
the cdb_core open-data-bundle schema contract (which is governed by
cdb_core/schemas.py and docs/DATA_DICTIONARY.md §9-10). Changes here
do not trigger CLAUDE.md R6 or a DATA_DICTIONARY.md co-update for
cdb_core; they do require updating the DATA_DICTIONARY.md §12 section
that documents the published failures JSON shape.

See docs/status/2026-05-12-phase6-T9-architect-plan.md §2.2 and §3
acceptance criterion 3, and docs/status/2026-05-12-phase6-T9-cda-sme-verdict.md
for the framing requirements applied to this shape.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


class PublishedFailureRecord(BaseModel):
    """A single record in the published per-domain failures JSON.

    Two record types share this model via the ``record_type`` discriminator.
    Fields that are specific to one record type are typed ``... | None``
    and are absent (omitted by the serialiser) on records of the other type.

    ``originating_outcome_class`` is always ``None`` for ``record_type ==
    "failure"`` records and always populated for ``record_type ==
    "decline_interview"`` records.
    """

    record_type: Literal["failure", "decline_interview"]

    # ── Common ──
    collection_date: str
    """ISO-8601 UTC timestamp. Mapped from ``timestamp`` (failure records)
    or ``followup_timestamp`` (decline_interview records)."""

    model_id: str
    domain_slug: str

    # ── Failure-record fields ──
    error_type: str | None = None
    error_message: str | None = None
    run_index: int | None = None
    prompt_verbatim: str | None = None
    response_verbatim: str | None = None
    thinking_verbatim: str | None = None
    stop_reason: str | None = None
    thoughts_token_count: int | None = None
    partial_session: dict[str, Any] | None = None
    retry_attempts: list[dict[str, Any]] | None = None

    # ── DeclineInterview-record fields ──
    decline_interview_id: str | None = None
    originating_informant_id: str | None = None
    originating_failure_id: str | None = None
    originating_step: str | None = None
    originating_outcome_class: str | None = None
    """Each enum value names the LSB-side detection rule that classified
    the record (e.g., ``refusal_string_match`` indicates that the output
    matched a refusal-string detector maintained by the LSB pipeline).
    The enum values do not attribute intent, belief, or state-of-mind to
    the model. See ARCHITECTURE.md §1.5.4 for the language-guardrails
    table and the methodology page for the failures-as-findings framing.
    Always ``None`` for ``record_type == "failure"`` records."""

    detection_rule_version: str | None = None
    model_version_returned: str | None = None
    provider: str | None = None
    api_endpoint: str | None = None
    prompt_version: str | None = None
    sha256_manifest: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: int | None = None
    qa_notes: str | None = None
    version_drift_flag: bool | None = None

    model_config = {"extra": "allow"}


class PublishedFailuresFile(BaseModel):
    """Top-level shape of apps/dashboard/public/data/failures/{slug}.json.

    See docs/status/2026-05-12-phase6-T9-architect-plan.md §2.2.
    """

    domain_slug: str
    generated_at: str
    """ISO-8601 UTC wallclock at build time."""

    n_records: int
    n_failure_records: int
    n_decline_interview_records: int

    framing_note: str
    """LSB-authored corpus-lens framing attached to the data so that
    readers who download this JSON outside the dashboard UI still receive
    the §1.5 context. T10 is contracted to render this field adjacent to
    the records. See docs/status/2026-05-12-phase6-T9-cda-sme-verdict.md
    §5.1."""

    records: list[PublishedFailureRecord]
