"""Confabulation classification schema and loader for decline-interview records.

No LLM imports — pure data validation.

This module is the analytic-side schema and loader for the confabulation
classification artifact at
``data/derived/decline_interviews_confabulation_classification.jsonl``.

The artifact contains exactly one row per ``decline_interview_id`` from the
9 originally-Gemini decline-interview records whose originating failures were
``max_output_tokens=4096`` cap-exhaustion events (Stage 1.5/1.5b probes,
2026-05-04).  These 9 rows are the corpus for studying confabulation patterns
produced under blind-spot conditions — conditions in which the originating
mechanical cause of a failure was not surfaced in the inputs available to the
model at decline-interview time.

**Confabulation in this context** describes the pattern in which the model's
output narrative attributes the failure to a mechanism (safety protocols, task
paradox, topic sensitivity) that is consistent with categorical knowledge from
its training corpus, but does not match the actual mechanical cause (a
``max_output_tokens`` cap reached during reasoning before any visible output
emitted).  "Confabulation" is used as a descriptive property of the output
narrative, not as a claim about the model's internal processes or cognition.

**Blind-spot conditions** (defined on first use): conditions in which the
originating mechanical cause of a failure was not surfaced in the inputs
available to the model at decline-interview time.  The model received the
empty-output text and the decline-interview prompt asking it to describe what
happened; it did not receive the API-level diagnostic that would have shown
the cap exhaustion (``output_tokens == 0 AND thoughts_token_count > 0``).
Subsequent references to "blind-spot conditions" use this shorthand.

The five confabulation label values (T2 — SME binding, 2026-05-05):

  ``safety_attribution_confabulation`` — the model's output narrative attributes
      the failure to safety mechanisms ("internal safety protocols", "policy
      filter", "content safety system"), when the actual cause was mechanical.
      (Note: formerly proposed as ``safety_filter_confabulation``; renamed per
      T2 of the CDA SME verdict docs/status/2026-05-05-t4-redo-cda-sme-verdict.md
      to remove the "filter" operational connotation.)

  ``task_paradox_confabulation`` — the model's output narrative attributes the
      failure to a logical or paradoxical conflict in the prompt ("act as a
      participant" vs. "I am an AI", "list every X" vs. impossibility of
      "every"), when the actual cause was mechanical.

  ``topic_sensitivity_confabulation`` — the model's output narrative attributes
      the failure to topic-sensitivity ("religious", "cultural", "biased",
      "uncurated"), when the actual cause was mechanical.

  ``mixed_attribution`` — the narrative blends two or more of the above without
      a single dominant attribution.  Methodologically interesting: mixed
      attribution is consistent with confabulation (the narrative is searching
      for a plausible explanation) and is distinct from a single coherent theory.

  ``not_confabulation`` — the narrative correctly identifies the failure cause
      (e.g., "technical glitch", "mechanical error"), or genuinely does not
      claim to know.  These rows are not confabulation under this framing.

Sentinel:
  ``UNCLASSIFIED`` — present in the seed file only; rejected by
      ``load_confabulation_classifications`` before the narrative is consumed by
      any analysis workflow.  Call ``validate_no_unclassified`` to gate the
      consumer.

Placement: ``cdb_analyze`` (not ``cdb_core``) because this is derived data
computed from raw decline interviews plus a human classification pass.  It is
not part of the open-data-bundle schema commitment.

References:
  Architect plan:   docs/status/2026-05-05-t4-redo-architect-plan.md §2 RD-2
  CDA SME verdict:  docs/status/2026-05-05-t4-redo-cda-sme-verdict.md (T1, T2)
  RD-1 supersede:   data/derived/decline_interviews_safety_attribution_subtype.SUPERSEDED.md
  Predecessor:      packages/cdb_analyze/cdb_analyze/safety_subtype.py (mooted)

No LLM imports permitted in cdb_analyze.  See ARCHITECTURE.md §4.2 binding
constraint and CLAUDE.md §6 rule 12.
"""

from __future__ import annotations

import json
import pathlib
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

# ── The five concrete label values + the UNCLASSIFIED seed sentinel ────────────
# The UNCLASSIFIED sentinel is intentionally NOT in the Literal used for
# Pydantic validation — the seed builder emits it directly as raw JSON.
# The loader pre-checks for the sentinel before Pydantic-validating (see
# ``load_confabulation_classifications``).
#
# T2 (SME binding): enum value is ``safety_attribution_confabulation``, NOT
# ``safety_filter_confabulation``.  The rename removes the "filter" operational
# connotation that would re-import the falsified safety-event premise.
ConfabulationLabelValue = Literal[
    "safety_attribution_confabulation",
    "task_paradox_confabulation",
    "topic_sensitivity_confabulation",
    "mixed_attribution",
    "not_confabulation",
]

# The full set of permitted values including the seed sentinel.
# Used by the seed builder and by the inspector CLI.
ALL_CONFABULATION_LABELS: tuple[str, ...] = (
    "safety_attribution_confabulation",
    "task_paradox_confabulation",
    "topic_sensitivity_confabulation",
    "mixed_attribution",
    "not_confabulation",
    "UNCLASSIFIED",
)

# Human-readable label descriptions for the CLI inspector (Mark's hand-coding
# reference).  Uses §1.5-clean phrasings throughout: "the narrative attributes"
# / "the output pattern" / not "the model believed".
LABEL_DESCRIPTIONS: dict[str, str] = {
    "safety_attribution_confabulation": (
        "The output narrative attributes the failure to safety mechanisms "
        "(e.g., 'internal safety protocols', 'content safety system', "
        "'policy filter'), when the actual cause was mechanical (cap exhaustion)."
    ),
    "task_paradox_confabulation": (
        "The output narrative attributes the failure to a logical or paradoxical "
        "conflict in the prompt (e.g., 'act as a participant' vs. 'I am an AI'), "
        "when the actual cause was mechanical."
    ),
    "topic_sensitivity_confabulation": (
        "The output narrative attributes the failure to topic-sensitivity "
        "(e.g., 'religious', 'cultural', 'biased', 'uncurated'), when the actual "
        "cause was mechanical."
    ),
    "mixed_attribution": (
        "The narrative blends two or more attribution shapes without a single "
        "dominant explanation. Consistent with confabulation under uncertainty."
    ),
    "not_confabulation": (
        "The narrative correctly identifies the failure cause (e.g., 'technical "
        "glitch', 'mechanical error'), or genuinely does not claim to know. "
        "Not confabulation under this framing."
    ),
    "UNCLASSIFIED": (
        "Seed sentinel — Mark has not yet hand-coded this row. "
        "All rows must be classified before analysis."
    ),
}


class ConfabulationClassification(BaseModel):
    """Classification record for one decline-interview row in the confabulation corpus.

    One row per ``decline_interview_id`` from the 9 originally-Gemini
    cap-exhaustion decline-interview records.  The artifact at
    ``data/derived/decline_interviews_confabulation_classification.jsonl``
    contains exactly one row per such record.

    The ``"UNCLASSIFIED"`` sentinel is intentionally excluded from the
    ``ConfabulationLabelValue`` Literal — Pydantic rejects it on parse, which
    is the intended gate: all 9 rows must carry a valid label before the RD-3
    workflow consumes the artifact.  Call ``validate_no_unclassified`` to
    enforce this gate explicitly.  The seed builder emits rows with the sentinel
    bypassing Pydantic validation; the loader pre-checks for it (see
    ``load_confabulation_classifications``).

    T1 (SME binding): "blind-spot conditions" are conditions in which the
    originating mechanical cause was not surfaced in the inputs available to
    the model at decline-interview time.  This class and its docstrings use
    §1.5-clean phrasings throughout: "the model's output narrative attributes"
    / "the response pattern is consistent with" — never "the model believed"
    or "the model thought".

    T2 (SME binding): ``confabulation_label`` uses
    ``safety_attribution_confabulation``, NOT ``safety_filter_confabulation``.

    Fields:
        decline_interview_id:    Source row identity key.  Must exist in
                                 ``data/raw/decline_interviews.jsonl``.
                                 Non-empty.
        confabulation_label:     One of the five concrete label values, or the
                                 ``UNCLASSIFIED`` sentinel (seed only).
        confabulation_rationale: Free-text rationale, ≤ 200 chars.  Should
                                 reference verbatim text from
                                 ``response_verbatim`` in the source
                                 decline-interview record.  Empty string allowed
                                 in the seed only; the loader accepts it (the
                                 RD-3 consumer should call
                                 ``validate_no_unclassified`` which implicitly
                                 requires non-empty rationale for classified rows
                                 — but the loader itself only enforces the
                                 length cap, not non-emptiness, to allow the
                                 seed state through the loader).
        under_blind_spot:        ``True`` if the originating failure was a
                                 ``max_output_tokens=4096`` cap-exhaustion event
                                 — verifiable from the originating informant
                                 record's ``thoughts_token_count > 0 AND
                                 output_tokens == 0`` diagnostic.  All 9 rows
                                 in the Phase 4a.1 confabulation corpus are
                                 ``True``; the field exists for schema
                                 completeness and future-batch flexibility.
        classifier_id:           Non-empty string identifying who classified.
                                 Conventional value: ``"mark"``.
    """

    model_config = ConfigDict(extra="forbid")

    decline_interview_id: str
    confabulation_label: ConfabulationLabelValue
    confabulation_rationale: str
    under_blind_spot: bool
    classifier_id: str

    @field_validator("decline_interview_id")
    @classmethod
    def _decline_interview_id_nonempty(cls, v: str) -> str:
        if not v:
            raise ValueError("decline_interview_id must be non-empty")
        return v

    @field_validator("confabulation_rationale")
    @classmethod
    def _rationale_length(cls, v: str) -> str:
        if len(v) > 200:
            raise ValueError(
                f"confabulation_rationale must be ≤ 200 chars (got {len(v)})"
            )
        return v

    @field_validator("classifier_id")
    @classmethod
    def _classifier_id_nonempty(cls, v: str) -> str:
        if not v:
            raise ValueError("classifier_id must be non-empty")
        return v


def load_confabulation_classifications(
    path: pathlib.Path | str,
) -> list[ConfabulationClassification]:
    """Load the confabulation classification JSONL artifact as a list of records.

    Each non-empty line is validated through ``ConfabulationClassification``.
    Returns a ``list[ConfabulationClassification]`` in file order.

    The loader enforces two invariants:
    1. No row may have ``confabulation_label == "UNCLASSIFIED"`` — this sentinel
       is allowed in the seed only.  The loader raises with a message naming the
       offending row and instructing Mark to hand-code it.  To consume the seed
       file before hand-coding is complete, call the loader only after all rows
       are classified (use ``validate_no_unclassified`` as the explicit gate).
       The loader itself pre-checks for this sentinel before Pydantic-validating
       so the error message names the offending row clearly.
    2. Duplicate ``decline_interview_id`` values cause a ``ValueError`` naming
       the duplicate.

    Args:
        path: Path to the confabulation classification JSONL artifact.

    Returns:
        List of ``ConfabulationClassification`` records in file order.

    Raises:
        FileNotFoundError: if ``path`` does not exist.
        ValueError: if any row has ``confabulation_label == "UNCLASSIFIED"``.
        ValueError: if duplicate ``decline_interview_id`` values appear.
        ValueError: if a line is not valid JSON.
        pydantic.ValidationError: if any row fails Pydantic field validation.
    """
    artifact_path = pathlib.Path(path)

    records: list[ConfabulationClassification] = []
    seen_ids: set[str] = set()

    with artifact_path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue

            # ── Pre-check 1: parse raw JSON for informative error messages ────
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON at line {lineno} of {artifact_path}: {exc}"
                ) from exc

            did = raw.get("decline_interview_id", f"<line {lineno}>")

            # ── Pre-check 2: sentinel detection (before Pydantic) ─────────────
            if raw.get("confabulation_label") == "UNCLASSIFIED":
                raise ValueError(
                    f"Confabulation classification incomplete: row {did!r} is still "
                    f"UNCLASSIFIED. Mark must hand-code all rows before this "
                    f"artifact is consumed by the analysis workflow."
                )

            # ── Pre-check 3: duplicate detection ─────────────────────────────
            if did in seen_ids:
                raise ValueError(
                    f"Duplicate decline_interview_id found in {artifact_path}: {did!r}"
                )
            seen_ids.add(did)

            # ── Pydantic validation ───────────────────────────────────────────
            record = ConfabulationClassification.model_validate(raw)
            records.append(record)

    return records


def validate_no_unclassified(records: list[ConfabulationClassification]) -> None:
    """Raise ValueError if any record still carries the UNCLASSIFIED sentinel.

    Called by the RD-3 memo workflow before consuming the confabulation
    classification artifact.  This helper is a belt-and-suspenders gate: the
    loader already rejects UNCLASSIFIED on read, but a consumer that builds
    records in memory without going through the loader calls this directly.

    Note: ``ConfabulationClassification.confabulation_label`` is a strict
    ``Literal`` that does not include ``"UNCLASSIFIED"``, so Pydantic
    construction already prevents the sentinel from entering a validated record.
    This helper is provided for downstream workflows that receive a list of
    pre-loaded records and want an explicit gate check before analysis.

    Args:
        records: List of ``ConfabulationClassification`` objects to validate.

    Raises:
        ValueError: if any record's ``confabulation_label`` is ``"UNCLASSIFIED"``.
            (In practice Pydantic will have already caught this; this is a
            belt-and-suspenders check for hand-constructed or patched records.)
    """
    unclassified = [
        r.decline_interview_id
        for r in records
        if r.confabulation_label == "UNCLASSIFIED"  # type: ignore[comparison-overlap]
    ]
    if unclassified:
        raise ValueError(
            f"Found UNCLASSIFIED rows that must be hand-coded before analysis: "
            f"{unclassified!r}"
        )
