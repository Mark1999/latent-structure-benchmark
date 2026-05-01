"""Safety attribution subtype schema and loader for decline-interview records.

No LLM imports — pure data validation.

This module is the analytic-side schema and loader for the safety attribution
subtype artifact at
``data/derived/decline_interviews_safety_attribution_subtype.jsonl``.

The artifact is a sibling of the manual classification artifact; it contains
exactly one row per ``decline_interview_id`` whose parent classification in
``data/derived/decline_interviews_manual_classification.jsonl`` is
``safety_event_attribution``.  Non-safety rows are absent by design (D17).

The two subtype values (K-frame and K-vocab) are prescribed by SME binding
note B11:

  ``k_frame`` — the model's attribution narrative names AI-vs-human-research-
      subject framing as the trigger.  Canonical phrases (non-exhaustive):
      "cognitive anthropology study", "act as a participant",
      "human research subject", "I am a tool, not a person",
      "act like a human".  The framing-as-trigger element is the discriminator;
      mere appearance of the phrase in the prompt description (without it being
      named as the trigger) is NOT sufficient.

  ``k_vocab_without_k_frame`` — the model's attribution narrative names
      list-comprehensiveness, list-sensitivity, or vocabulary-policy as the
      trigger, WITHOUT the AI-vs-human-research-subject framing element.
      Canonical phrases (non-exhaustive): "uncurated comprehensive list",
      "potentially unsafe raw data dump", "list will start to include
      sensitive...topics", "massive and culturally sensitive",
      "biased, incomplete, or otherwise problematic".

Placement: cdb_analyze (not cdb_core) because this is derived data computed
from raw decline interviews plus a human subtype classification pass.  It is
not part of the open-data-bundle schema commitment (D17; Amendment 3 §3.1).

References:
  Architect plan:   docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md §3.1
  CDA SME verdict:  docs/status/2026-04-30-phase4a1-amendment-3-cda-sme-verdict.md
  B11 source:       docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md
  Parent module:    packages/cdb_analyze/cdb_analyze/manual_classification.py

No LLM imports permitted in cdb_analyze.  See ARCHITECTURE.md §4.2 binding
constraint and CLAUDE.md §6 rule 12.
"""

from __future__ import annotations

import json
import pathlib
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

from cdb_analyze.manual_classification import load_manual_classifications

# ── The two SME-prescribed subtype values (B11, binding) ─────────────────────
# Do not add, remove, or rename without a new SME plan review cycle.
# The sentinel "UNCLASSIFIED" is NOT in this Literal — Pydantic rejects it,
# which is the intended gate: the loader pre-checks for the sentinel string
# before Pydantic-validating, and raises a descriptive error.
SafetyAttributionSubtypeValue = Literal[
    "k_frame",
    "k_vocab_without_k_frame",
]


class SafetyAttributionSubtype(BaseModel):
    """Subtype record for one ``safety_event_attribution`` decline-interview row.

    One row per ``decline_interview_id`` whose parent classification is
    ``safety_event_attribution``.  The artifact at
    ``data/derived/decline_interviews_safety_attribution_subtype.jsonl``
    must contain exactly one row per such parent row.

    The ``"UNCLASSIFIED"`` sentinel is intentionally excluded from the
    ``SafetyAttributionSubtypeValue`` Literal — Pydantic will reject it on
    parse, which is the gate: all 9 rows must carry a valid subtype before
    T4.2 can load the artifact.  The seed-builder bypasses Pydantic
    validation to emit the sentinel rows; the loader pre-checks for the
    sentinel before Pydantic-validating (see ``load_safety_attribution_subtypes``).

    Fields:
        decline_interview_id:       Source row identity key.  Must exist in
                                    the parent manual classification artifact
                                    AND have ``manual_classification ==
                                    'safety_event_attribution'``.
        safety_attribution_subtype: One of the two B11-prescribed values:
                                    ``k_frame`` or ``k_vocab_without_k_frame``.
        subtype_rationale:          Free-text rationale, 1–200 chars.
                                    Should reference the verbatim trigger-
                                    attribution language present in the source
                                    ``response_verbatim`` (B7 carry-through).
        subtype_classifier_id:      Short string identifying who classified.
                                    Conventional value: ``"mark"``.
    """

    model_config = ConfigDict(extra="forbid")

    decline_interview_id: str
    safety_attribution_subtype: SafetyAttributionSubtypeValue
    subtype_rationale: str
    subtype_classifier_id: str

    @field_validator("decline_interview_id")
    @classmethod
    def _decline_interview_id_nonempty(cls, v: str) -> str:
        if not v:
            raise ValueError("decline_interview_id must be non-empty")
        return v

    @field_validator("subtype_rationale")
    @classmethod
    def _rationale_length(cls, v: str) -> str:
        if not v:
            raise ValueError("subtype_rationale must not be empty")
        if len(v) > 200:
            raise ValueError(
                f"subtype_rationale must be ≤ 200 chars (got {len(v)})"
            )
        return v

    @field_validator("subtype_classifier_id")
    @classmethod
    def _classifier_id_nonempty(cls, v: str) -> str:
        if not v:
            raise ValueError("subtype_classifier_id must be non-empty")
        return v


def load_safety_attribution_subtypes(
    path: pathlib.Path | str,
    manual_classification_path: pathlib.Path | str,
) -> dict[str, SafetyAttributionSubtype]:
    """Load the safety attribution subtype JSONL artifact keyed by decline_interview_id.

    Each non-empty line is validated through SafetyAttributionSubtype.
    Returns a dict of {decline_interview_id: SafetyAttributionSubtype}.

    The loader enforces three invariants (Amendment 3 §3.1):
    1. No row may have ``safety_attribution_subtype == "UNCLASSIFIED"`` —
       this sentinel is only allowed in the seed; the loader raises with a
       message naming the offending row and instructing Mark to hand-code it.
    2. Every ``decline_interview_id`` must exist in the parent manual
       classification artifact (``manual_classification_path``).
    3. Every row's parent classification must be ``safety_event_attribution``
       (the "you cannot subtype a non-safety row" invariant from D17).

    Args:
        path: Path to the subtype JSONL artifact.
        manual_classification_path: Path to the parent manual classification
            JSONL artifact (``decline_interviews_manual_classification.jsonl``).
            Used for join validation at load time.

    Returns:
        dict[str, SafetyAttributionSubtype] keyed by ``decline_interview_id``.

    Raises:
        FileNotFoundError: if ``path`` or ``manual_classification_path`` does
            not exist.
        ValueError: if any row has ``safety_attribution_subtype ==
            "UNCLASSIFIED"`` (all 9 rows must be hand-coded by Mark before
            T4.2 runs).
        ValueError: if any row's ``decline_interview_id`` is not present in
            the parent manual classification artifact.
        ValueError: if any row's parent classification is not
            ``safety_event_attribution``.
        ValueError: if duplicate ``decline_interview_id`` values appear in
            the subtype artifact.
        pydantic.ValidationError: if any row fails Pydantic field validation
            (empty rationale, rationale > 200 chars, empty classifier id,
            empty decline_interview_id, unknown subtype value).
    """
    subtype_path = pathlib.Path(path)
    mc_path = pathlib.Path(manual_classification_path)

    # Load parent classifications first — FileNotFoundError propagates naturally
    parent_classifications = load_manual_classifications(mc_path)

    subtypes: dict[str, SafetyAttributionSubtype] = {}

    with subtype_path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue

            # ── Pre-check 1: sentinel detection (before Pydantic) ────────────
            # Parse raw JSON first so we can name the row in error messages.
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON at line {lineno} of {subtype_path}: {exc}"
                ) from exc

            did = raw.get("decline_interview_id", f"<line {lineno}>")

            if raw.get("safety_attribution_subtype") == "UNCLASSIFIED":
                raise ValueError(
                    f"Safety attribution subtype incomplete: row {did!r} is still "
                    f"UNCLASSIFIED. Mark must hand-code all 9 rows before T4.2 runs."
                )

            # ── Pre-check 2: parent classification join ───────────────────────
            if did not in parent_classifications:
                raise ValueError(
                    f"decline_interview_id {did!r} (line {lineno} of {subtype_path}) "
                    f"is not present in the parent manual classification artifact "
                    f"at {mc_path}. Only rows from that artifact may be subtyped."
                )

            parent = parent_classifications[did]
            if parent.manual_classification != "safety_event_attribution":
                raise ValueError(
                    f"decline_interview_id {did!r} (line {lineno} of {subtype_path}) "
                    f"has parent classification {parent.manual_classification!r}, "
                    f"not 'safety_event_attribution'. You cannot subtype a non-safety "
                    f"row (D17 invariant). Only safety_event_attribution rows belong "
                    f"in this artifact."
                )

            # ── Pre-check 3: duplicate detection ─────────────────────────────
            if did in subtypes:
                raise ValueError(
                    f"Duplicate decline_interview_id found in {subtype_path}: {did!r}"
                )

            # ── Pydantic validation ───────────────────────────────────────────
            record = SafetyAttributionSubtype.model_validate(raw)
            subtypes[did] = record

    return subtypes
