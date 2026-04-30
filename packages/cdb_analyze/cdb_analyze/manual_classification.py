"""Manual classification overlay for decline-interview records.

No LLM imports — pure data validation.

This module is the analytic-side schema and loader for the manual
classification artifact at ``data/derived/decline_interviews_manual_classification.jsonl``.
It is consumed by T4 (phase4a1_note_j_crosstab.py) after Mark completes
commit 3 of T3C.

Placement: cdb_analyze (not cdb_core) because this is derived data
computed from raw decline interviews plus a human classification pass.
It is not part of the open-data-bundle schema commitment.

References:
  Plan:       docs/status/2026-04-30-phase4a1-architect-plan-amendment-2.md §3 T3C
  SME PASS-WITH-NOTES:
              docs/status/2026-04-30-phase4a1-amendment-2-cda-sme-verdict.md
  Origin of 7-enum:
              docs/status/2026-04-23-phase4a1-t3b-detector-sme-verdict.md Ruling 1 + Note B1

No LLM imports permitted in cdb_analyze. See ARCHITECTURE.md §4.2 binding constraint
and CLAUDE.md §6 rule 12.
"""

from __future__ import annotations

import json
import pathlib
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

# ── The 7-value manual classification enum (SME-prescribed, binding) ──────────
# These values are verbatim from the SME's Ruling 1 and binding note B1.
# Do not add, remove, or rename without a new SME plan review cycle.
ManualClassificationValue = Literal[
    "safety_event_attribution",
    "blocked_event_attribution",
    "technical_glitch_attribution",
    "no_prior_context_acknowledgment",
    "substantive_compliance_with_empty_input",
    "other_substring_false_positive",
    "genuine_recursive_decline",
]


class DeclineManualClassification(BaseModel):
    """Manual classification record for one decline-interview follow-up response.

    One row per ``decline_interview_id``. The file at
    ``data/derived/decline_interviews_manual_classification.jsonl`` must contain
    exactly one row per ``decline_interview_id`` in
    ``data/raw/decline_interviews.jsonl``.

    The ``"UNCLASSIFIED"`` sentinel is intentionally excluded from the
    ``ManualClassificationValue`` Literal — Pydantic will reject it on parse,
    which is the B1 gate: all 27 rows must carry a valid classification before
    T4 can load the artifact.

    Fields:
        decline_interview_id:           Source row identity key.
        manual_classification:          One of the 7 SME-prescribed categories.
        manual_classification_rationale: Free-text rationale, 1–200 chars.
                                        Must quote the verbatim framing language
                                        from the response (B7 procedural requirement).
        manual_classifier_id:           Short string identifying who classified.
                                        Conventional values: "mark", "sme-spotcheck".
        response_verbatim_excerpt:      First 400 chars of source response_verbatim,
                                        carried for review convenience.
                                        Not authoritative — T4 re-reads from source.
        detector_flag_v1:               The v1 _is_recursive_decline() verdict.
                                        Carried for audit-trail value; B8 requires
                                        Mark to classify before consulting this field.
    """

    model_config = ConfigDict(extra="forbid")

    decline_interview_id: str
    manual_classification: ManualClassificationValue
    manual_classification_rationale: str
    manual_classifier_id: str
    response_verbatim_excerpt: str
    detector_flag_v1: bool

    @field_validator("decline_interview_id")
    @classmethod
    def _decline_interview_id_nonempty(cls, v: str) -> str:
        if not v:
            raise ValueError("decline_interview_id must be non-empty")
        return v

    @field_validator("manual_classification_rationale")
    @classmethod
    def _rationale_length(cls, v: str) -> str:
        if not v:
            raise ValueError("manual_classification_rationale must not be empty")
        if len(v) > 200:
            raise ValueError(
                f"manual_classification_rationale must be ≤ 200 chars (got {len(v)})"
            )
        return v

    @field_validator("manual_classifier_id")
    @classmethod
    def _classifier_id_nonempty(cls, v: str) -> str:
        if not v:
            raise ValueError("manual_classifier_id must be non-empty")
        return v


def load_manual_classifications(
    path: pathlib.Path | str,
) -> dict[str, DeclineManualClassification]:
    """Load the manual classification JSONL artifact keyed by decline_interview_id.

    Each non-empty line is validated through DeclineManualClassification.
    Returns a dict of {decline_interview_id: DeclineManualClassification}.

    Raises:
        ValueError: if any row has an unrecognized manual_classification value
            (including the "UNCLASSIFIED" sentinel — Pydantic rejects this at parse
            time with a clear error indicating all 27 rows must be classified before
            T4 runs).
        ValueError: if any row has an empty or over-length rationale.
        ValueError: if duplicate decline_interview_id values are found.

    Note: cross-reference validation against the source JSONL is a separate
    responsibility handled by validate_against_source(). The loader has a
    focused single responsibility: parse + validate each row.
    """
    file_path = pathlib.Path(path)
    classifications: dict[str, DeclineManualClassification] = {}

    with file_path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = DeclineManualClassification.model_validate_json(line)
            except Exception as exc:
                # Surface sentinel-specific message when UNCLASSIFIED appears in line
                if '"UNCLASSIFIED"' in line or "'UNCLASSIFIED'" in line:
                    # Extract decline_interview_id from raw JSON for the error message
                    try:
                        raw = json.loads(line)
                        did = raw.get("decline_interview_id", f"<line {lineno}>")
                    except Exception:
                        did = f"<line {lineno}>"
                    raise ValueError(
                        f"Manual classification incomplete: row {did} is still "
                        f"UNCLASSIFIED. All 27 rows must be classified before T4 runs."
                    ) from exc
                raise

            did = record.decline_interview_id
            if did in classifications:
                raise ValueError(
                    f"Duplicate decline_interview_id found in {file_path}: {did!r}"
                )
            classifications[did] = record

    return classifications


def validate_against_source(
    classifications: dict[str, DeclineManualClassification],
    source_path: pathlib.Path,
) -> None:
    """Cross-reference classifications dict against the source decline_interviews JSONL.

    Every decline_interview_id in the source must have a corresponding row in
    classifications. No extra rows are allowed.

    Raises:
        ValueError: listing missing IDs (in source but not classified) or
            extra IDs (classified but not in source).
    """
    source_ids: set[str] = set()
    with source_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            raw = json.loads(line)
            did = raw.get("decline_interview_id")
            if did:
                source_ids.add(did)

    classified_ids = set(classifications.keys())
    missing = source_ids - classified_ids
    extra = classified_ids - source_ids

    errors: list[str] = []
    if missing:
        errors.append(
            "Missing classifications for decline_interview_id(s) in source: "
            + ", ".join(sorted(missing))
        )
    if extra:
        errors.append(
            "Extra classifications not in source decline_interviews.jsonl: "
            + ", ".join(sorted(extra))
        )

    if errors:
        raise ValueError(
            "Cross-reference check failed:\n" + "\n".join(f"  - {e}" for e in errors)
        )
