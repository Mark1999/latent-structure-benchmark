"""Failures-as-findings publish layer. See ARCHITECTURE.md §4.4 and
docs/status/2026-05-12-phase6-T9-architect-plan.md.

Reads data/raw/failures.jsonl (raw dicts — no Pydantic Failure schema
exists; see plan §2.4) and data/raw/decline_interviews.jsonl (DeclineInterview
Pydantic records), joins each record to a domain, applies defensive
sanitization, and emits one apps/dashboard/public/data/failures/{slug}.json
per domain.

Domain join strategy:
- Failure records: keyed by context.domain (defensive: falls back to
  context.domain_slug). Records with no resolvable domain are filtered out
  and logged at WARNING level.
- DeclineInterview records: joined via the xor-paired originator. If
  originating_informant_id is set, looks up the informant in informants.jsonl.
  If originating_failure_id is set, reconstructs the deterministic failure
  identifier (imported from cdb_collect.decline_detection._failure_identifier
  — NOT reimplemented here per acceptance criterion 7) and looks up the
  failure record in failures.jsonl. Orphaned records are filtered out and
  logged at WARNING level.

All string fields in every published record are passed through
cdb_publish.sanitize.sanitize_record_strings() before write. This applies
the three defensive redaction passes: API-key patterns, Slack webhook URL
patterns, and local-filesystem path patterns. See
SECURITY_AND_HARDENING.md §3.3 and §3.4.

Each enum value in originating_outcome_class names the LSB-side detection
rule that classified the record (e.g., refusal_string_match indicates that
the output matched a refusal-string detector maintained by the LSB pipeline).
The enum values do not attribute intent, belief, or state-of-mind to the
model. See ARCHITECTURE.md §1.5.4 for the language-guardrails table and
the methodology page for the failures-as-findings framing.

Source files in data/raw/ are read-only. This module MUST NOT write to
any raw data paths (Reviewer R4, append-only invariant).
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cdb_collect.decline_detection import (
    # Import the canonical failure-identifier function from cdb_collect.
    # Do NOT reimplement this — see plan §2.4 and acceptance criterion 7.
    _failure_identifier,
)
from cdb_core.schemas import DeclineInterview
from pydantic import ValidationError

from cdb_publish.sanitize import sanitize_record_strings

logger = logging.getLogger(__name__)

# Verbatim framing note text, reviewed against §1.5.4 line-by-line by the
# CDA SME. Do not paraphrase. See
# docs/status/2026-05-12-phase6-T9-cda-sme-verdict.md §5.1.
_FRAMING_NOTE = (
    "These records preserve verbatim outputs from collection sessions that did "
    "not produce a parseable primary-step response. Each record is a property "
    "of the LSB collection pipeline's output distribution, not a claim about "
    "the model's intent or state-of-mind. The `originating_outcome_class` field "
    "names the LSB-side detection rule (e.g., `refusal_string_match` describes "
    "a string-pattern match by the LSB pipeline, not a model decision to refuse). "
    "See the methodology page for the failures-as-findings framing."
)


def _load_failures_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read failures.jsonl and return a list of raw dicts.

    Skips blank lines silently. Read-only access — never writes to path.
    """
    records: list[dict[str, Any]] = []
    if not path.exists():
        logger.warning("failures.jsonl not found at %s — returning empty list", path)
        return records
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                logger.warning(
                    "Skipping malformed JSON on line %d of %s: %s", lineno, path, exc
                )
    return records


def _load_decline_interviews_jsonl(path: Path) -> list[DeclineInterview]:
    """Read decline_interviews.jsonl and return validated DeclineInterview records.

    Skips blank lines and records that fail Pydantic validation (logged at WARNING).
    Read-only access — never writes to path.
    """
    records: list[DeclineInterview] = []
    if not path.exists():
        logger.warning(
            "decline_interviews.jsonl not found at %s — returning empty list", path
        )
        return records
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(DeclineInterview.model_validate_json(line))
            except (ValidationError, json.JSONDecodeError) as exc:
                logger.warning(
                    "Skipping invalid decline_interview record on line %d of %s: %s",
                    lineno,
                    path,
                    exc,
                )
    return records


def _load_informants_domain_map(path: Path) -> dict[str, str]:
    """Read informants.jsonl and return a dict mapping informant_id -> domain_slug.

    Used to resolve DeclineInterview.originating_informant_id -> domain.
    Read-only access — never writes to path.
    """
    mapping: dict[str, str] = {}
    if not path.exists():
        logger.warning(
            "informants.jsonl not found at %s — domain join via informant_id "
            "will be unavailable",
            path,
        )
        return mapping
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                inf_id = rec.get("informant_id")
                domain = rec.get("domain_slug")
                if inf_id and domain:
                    mapping[inf_id] = domain
            except json.JSONDecodeError as exc:
                logger.warning(
                    "Skipping malformed informant on line %d of %s: %s",
                    lineno,
                    path,
                    exc,
                )
    return mapping


def _build_failure_id_map(failures: list[dict[str, Any]]) -> dict[str, str]:
    """Build a dict mapping deterministic failure_id -> domain_slug.

    Used to resolve DeclineInterview.originating_failure_id -> domain.
    The identifier is computed via the canonical _failure_identifier()
    function from cdb_collect.decline_detection (NOT reimplemented here).
    """
    mapping: dict[str, str] = {}
    for entry in failures:
        ctx = entry.get("context", {})
        domain = ctx.get("domain") or ctx.get("domain_slug")
        if domain:
            fid = _failure_identifier(entry)
            mapping[fid] = domain
    return mapping


def _join_decline_interview_to_domain(
    di: DeclineInterview,
    informants_by_id: dict[str, str],
    failures_by_id: dict[str, str],
) -> str | None:
    """Compute domain_slug for a DeclineInterview via its xor-paired originator.

    Returns None for orphaned records (which the caller filters out and logs).
    The xor-paired originator invariant is enforced by DeclineInterview's
    _xor_originator validator; exactly one of the two fields is set.
    """
    if di.originating_informant_id is not None:
        domain = informants_by_id.get(di.originating_informant_id)
        if domain is None:
            logger.warning(
                "DeclineInterview %s: originating_informant_id %s not found "
                "in informants.jsonl — record orphaned and not published",
                di.decline_interview_id,
                di.originating_informant_id,
            )
        return domain

    if di.originating_failure_id is not None:
        domain = failures_by_id.get(di.originating_failure_id)
        if domain is None:
            logger.warning(
                "DeclineInterview %s: originating_failure_id %s not found "
                "in failures.jsonl — record orphaned and not published",
                di.decline_interview_id,
                di.originating_failure_id,
            )
        return domain

    # Should not happen if xor validator is enforced, but defensive.
    logger.warning(
        "DeclineInterview %s: neither originating_informant_id nor "
        "originating_failure_id is set — record orphaned",
        di.decline_interview_id,
    )
    return None


def _failure_to_published_dict(entry: dict[str, Any], domain_slug: str) -> dict[str, Any]:
    """Convert a raw failure dict to the published record shape.

    Applies sanitize_record_strings() to every string leaf. Omits optional
    fields that are absent from the source record (consistent with the
    sparse-dict convention from append_failure()). See plan §2.4.
    """
    ctx = entry.get("context", {})

    rec: dict[str, Any] = {
        "record_type": "failure",
        "collection_date": entry.get("timestamp", ""),
        "model_id": ctx.get("model_id", ""),
        "domain_slug": domain_slug,
        "error_type": entry.get("error_type", ""),
        "error_message": entry.get("error_message", ""),
        "run_index": ctx.get("run_index"),
        "originating_outcome_class": None,
        "retry_attempts": entry.get("retry_attempts", []),
    }

    # Optional fields: only include when present in source record.
    for field in (
        "prompt_verbatim",
        "response_verbatim",
        "thinking_verbatim",
        "stop_reason",
        "thoughts_token_count",
        "partial_session",
    ):
        val = entry.get(field)
        if val is not None:
            rec[field] = val

    # Sanitize all string leaves before returning.
    return sanitize_record_strings(rec)  # type: ignore[return-value]


def _decline_interview_to_published_dict(
    di: DeclineInterview, domain_slug: str
) -> dict[str, Any]:
    """Convert a DeclineInterview record to the published record shape.

    Applies sanitize_record_strings() to every string leaf. See plan §2.4.
    """
    rec: dict[str, Any] = {
        "record_type": "decline_interview",
        "collection_date": di.followup_timestamp.isoformat(),
        "model_id": di.model_id,
        "domain_slug": domain_slug,
        "decline_interview_id": di.decline_interview_id,
        "originating_informant_id": di.originating_informant_id,
        "originating_failure_id": di.originating_failure_id,
        "originating_step": di.originating_step,
        "originating_outcome_class": di.originating_outcome_class,
        "detection_rule_version": di.detection_rule_version,
        "model_version_returned": di.model_version_returned,
        "provider": di.provider,
        "api_endpoint": di.api_endpoint,
        "prompt_version": di.prompt_version,
        "sha256_manifest": di.sha256_manifest,
        "prompt_verbatim": di.prompt_verbatim,
        "response_verbatim": di.response_verbatim,
        "thinking_verbatim": di.thinking_verbatim,
        "input_tokens": di.input_tokens,
        "output_tokens": di.output_tokens,
        "latency_ms": di.latency_ms,
        "stop_reason": di.stop_reason,
        "qa_notes": di.qa_notes,
        "version_drift_flag": di.version_drift_flag,
    }

    # Sanitize all string leaves before returning.
    return sanitize_record_strings(rec)  # type: ignore[return-value]


def _sort_key(record: dict[str, Any]) -> tuple[str, str, str]:
    """Return a stable sort tuple for a published record.

    Sort order per plan §2.2: collection_date ascending, then record_type
    ascending (lexicographic — "decline_interview" < "failure"), then stable
    identifier.
    """
    date = record.get("collection_date", "")
    rtype = record.get("record_type", "")
    # Stable identifier: decline_interview_id for decline_interview records,
    # a composite for failure records.
    if rtype == "decline_interview":
        stable_id = record.get("decline_interview_id", "")
    else:
        # For failure records: model_id + run_index provides a stable tie-break.
        stable_id = (
            f"{record.get('model_id', '')}|{record.get('run_index', '')}"
        )
    return (date, rtype, stable_id)


def build_failures(
    raw_failures_path: Path,
    raw_decline_interviews_path: Path,
    raw_informants_path: Path,
    output_dir: Path,
    domain_slugs: list[str],
) -> dict[str, str]:
    """Read raw failures and decline interviews, join to domains, emit per-domain JSON.

    Emits one apps/dashboard/public/data/failures/{slug}.json per domain in
    domain_slugs. Domains with zero records still receive an output file with
    records: [] (first-class empty state per ARCHITECTURE.md §1.5.5 and
    CLAUDE.md §9 pitfall #4). Returns the failures-path dict for the manifest
    (every slug has a non-null entry).

    Source files are read-only — never modified. SHA256 of source files must be
    byte-identical before and after this function runs (Reviewer R4).

    Parameters
    ----------
    raw_failures_path:
        Path to data/raw/failures.jsonl (read-only).
    raw_decline_interviews_path:
        Path to data/raw/decline_interviews.jsonl (read-only).
    raw_informants_path:
        Path to data/raw/informants.jsonl (read-only; used for domain join).
    output_dir:
        Directory where per-domain failures JSON files will be written.
        Created if it does not exist.
    domain_slugs:
        List of domain slugs from the manifest. Every slug gets an output
        file even if it has zero records.

    Returns
    -------
    dict[str, str]
        Map from domain_slug to published path relative to the dashboard
        public directory root (e.g., ``"data/failures/family.json"``).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Load source data ──
    failure_records = _load_failures_jsonl(raw_failures_path)
    decline_interviews = _load_decline_interviews_jsonl(raw_decline_interviews_path)
    informants_by_id = _load_informants_domain_map(raw_informants_path)
    failures_by_id = _build_failure_id_map(failure_records)

    # ── Group failures by domain ──
    failures_by_domain: dict[str, list[dict[str, Any]]] = {s: [] for s in domain_slugs}
    for entry in failure_records:
        ctx = entry.get("context", {})
        # Defensive: accept context.domain or context.domain_slug.
        domain = ctx.get("domain") or ctx.get("domain_slug")
        if not domain:
            logger.warning(
                "Failure record with timestamp=%s has no context.domain — "
                "cannot join to a domain, not published",
                entry.get("timestamp", "<unknown>"),
            )
            continue
        if domain not in failures_by_domain:
            # Domain present in data but not in manifest — skip.
            logger.warning(
                "Failure record domain %r not in manifest domain list — "
                "not published (timestamp=%s)",
                domain,
                entry.get("timestamp", "<unknown>"),
            )
            continue
        failures_by_domain[domain].append(entry)

    # ── Group decline interviews by domain ──
    dis_by_domain: dict[str, list[DeclineInterview]] = {s: [] for s in domain_slugs}
    for di in decline_interviews:
        domain = _join_decline_interview_to_domain(di, informants_by_id, failures_by_id)
        if domain is None:
            continue  # Already logged in _join_decline_interview_to_domain.
        if domain not in dis_by_domain:
            logger.warning(
                "DeclineInterview %s resolved to domain %r which is not in "
                "manifest domain list — not published",
                di.decline_interview_id,
                domain,
            )
            continue
        dis_by_domain[domain].append(di)

    # ── Build and emit per-domain files ──
    generated_at = datetime.now(tz=UTC).isoformat()
    failures_map: dict[str, str] = {}

    for slug in sorted(domain_slugs):
        published_records: list[dict[str, Any]] = []

        for entry in failures_by_domain[slug]:
            published_records.append(_failure_to_published_dict(entry, slug))

        for di in dis_by_domain[slug]:
            published_records.append(_decline_interview_to_published_dict(di, slug))

        # Sort per plan §2.2: collection_date asc, record_type asc, stable id asc.
        published_records.sort(key=_sort_key)

        n_failure = sum(1 for r in published_records if r["record_type"] == "failure")
        n_di = sum(
            1 for r in published_records if r["record_type"] == "decline_interview"
        )

        output_obj = {
            "domain_slug": slug,
            "generated_at": generated_at,
            "n_records": len(published_records),
            "n_failure_records": n_failure,
            "n_decline_interview_records": n_di,
            "framing_note": _FRAMING_NOTE,
            "records": published_records,
        }

        out_path = output_dir / f"{slug}.json"
        out_path.write_text(json.dumps(output_obj, indent=2), encoding="utf-8")
        logger.info(
            "Wrote %s (%d failure + %d decline_interview records)",
            out_path,
            n_failure,
            n_di,
        )

        # Path is relative to the dashboard public/ root.
        failures_map[slug] = f"data/failures/{slug}.json"

    return failures_map
