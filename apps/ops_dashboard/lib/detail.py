"""Pure helper functions for the single-informant detail view (OPS-T4).

All functions are pure (no side effects, no I/O, no Streamlit calls).
Extracted here so that tests can unit-test them without spinning up a
Streamlit server.

READ-ONLY INVARIANT: no file opens, no database writes, no LLM client
imports. This module consumes InformantRecord and DeclineInterview objects
already loaded by lib/loader.py.

See ARCHITECTURE.md §3.2 (InformantRecord / DeclineInterview schemas) and
docs/DATA_DICTIONARY.md §1.1 / §10 for field semantics.

CDA SME binding notes (2026-05-01 OPS-T4 verdict):
- Note 1: Section 2 provenance line is rendered by the caller, not here.
- Note 2: Singletons are flagged with is_singleton=True for inline rendering.
- Note 4: Disclaimer above decline verbatim text is rendered by the caller.
- Note 5: Read-only classification fields surface manual_classification and
  safety_attribution_subtype if present; omit if absent.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from cdb_core.schemas import (
    DeclineInterview,
    InformantRecord,
)

# ── Freelist helpers ──────────────────────────────────────────────────────────


def format_freelist(record: InformantRecord) -> list[str]:
    """Return the freelist items in the order the model returned them.

    Uses FreelistRecord.parsed_raw_order when populated; falls back to
    parsed_items if parsed_raw_order is empty (both share the same
    cardinality invariant when the collection pipeline runs normally).

    Args:
        record: An InformantRecord.

    Returns:
        Ordered list of item strings. Empty list when the freelist step
        produced zero items.
    """
    items = record.freelist.parsed_raw_order
    if not items:
        items = record.freelist.parsed_items
    return list(items)


def build_thinking_trace(record: InformantRecord) -> str | None:
    """Return the freelist-step thinking trace, or None if absent.

    Reads FreelistRecord.thinking_verbatim. An empty string counts as
    absent — returns None in that case.

    The trace is the model's chain-of-thought output text, not an
    interpretation of internal cognition.

    Args:
        record: An InformantRecord.

    Returns:
        The thinking trace string if non-empty, None otherwise.
    """
    trace = record.freelist.thinking_verbatim
    return trace if trace and trace.strip() else None


# ── Pile-sort helpers ─────────────────────────────────────────────────────────


@dataclass
class PileDetail:
    """Rendered view of one pile from the model's pile-sort output.

    Attributes:
        pile_number: 1-indexed position in the model's returned pile list.
        label: The model's own label verbatim (may be empty string if the
            interview step returned fewer labels than piles).
        members: Members in the model's returned order. Empty list for an
            empty pile.
        is_singleton: True when members contains exactly one item.
        is_empty: True when members is empty.
    """

    pile_number: int
    label: str
    members: list[str] = field(default_factory=list)
    is_singleton: bool = False
    is_empty: bool = False


def format_pile_sort(record: InformantRecord) -> list[PileDetail]:
    """Return piles with labels, members, and singleton/empty flags.

    Labels come from InterviewRecord.parsed_pile_labels (the model's
    verbatim pile-naming output). If the interview returned fewer labels
    than there are piles, remaining piles receive an empty string label.
    Labels are never re-named or re-inferred.

    Member ordering is preserved as the model returned it (via
    PileSortRecord.parsed_piles). Items are never re-sorted.

    Args:
        record: An InformantRecord.

    Returns:
        List of PileDetail objects, one per pile, in model-returned order.
        Empty list when parsed_piles is empty (no pile-sort data).
    """
    raw_piles = record.pile_sort.parsed_piles
    labels = list(record.interview.parsed_pile_labels)

    result: list[PileDetail] = []
    for i, members in enumerate(raw_piles):
        label = labels[i] if i < len(labels) else ""
        result.append(
            PileDetail(
                pile_number=i + 1,
                label=label,
                members=list(members),
                is_singleton=len(members) == 1,
                is_empty=len(members) == 0,
            )
        )
    return result


# ── Decline-event helpers ─────────────────────────────────────────────────────


@dataclass
class DeclineDetail:
    """Rendered view of one decline interview record plus joined classifications.

    Attributes:
        decline_interview_id: Unique ID of the DeclineInterview.
        originating_step: Which CDA step triggered the decline-interview.
        originating_outcome_class: Machine-detected outcome class.
        response_verbatim: The model's verbatim follow-up response text.
        thinking_verbatim: The follow-up call's thinking trace (may be empty).
        manual_classification: Human-assigned classification, or None.
        manual_classifier_id: Identity of the classifier, or None.
        safety_attribution_subtype: Human-assigned subtype, or None.
        subtype_classifier_id: Identity of the subtype classifier, or None.
    """

    decline_interview_id: str
    originating_step: str
    originating_outcome_class: str
    response_verbatim: str
    thinking_verbatim: str
    manual_classification: str | None
    manual_classifier_id: str | None
    safety_attribution_subtype: str | None
    subtype_classifier_id: str | None


def find_decline_events(
    informant_id: str,
    decline_interviews: list[DeclineInterview],
    classifications: list[dict],
    subtypes: list[dict],
) -> list[DeclineDetail]:
    """Join decline interviews with their classifications for one informant.

    Filters decline_interviews to those originating from informant_id, then
    left-joins classification and subtype data on decline_interview_id.

    The classifications and subtypes lists are plain dicts loaded from
    derived JSONL files — their keys mirror the file schema
    (decline_interview_id, manual_classification, manual_classifier_id,
    safety_attribution_subtype, subtype_classifier_id).

    Args:
        informant_id: The InformantRecord.informant_id to look up.
        decline_interviews: All DeclineInterview objects loaded from
            data/raw/decline_interviews.jsonl.
        classifications: All rows from
            data/derived/decline_interviews_manual_classification.jsonl
            as plain dicts.
        subtypes: All rows from
            data/derived/decline_interviews_safety_attribution_subtype.jsonl
            as plain dicts.

    Returns:
        List of DeclineDetail objects for this informant, in the order they
        appear in decline_interviews. Empty list if none found.
    """
    # Build lookup indices on decline_interview_id
    class_index: dict[str, dict] = {
        d["decline_interview_id"]: d for d in classifications
    }
    subtype_index: dict[str, dict] = {
        d["decline_interview_id"]: d for d in subtypes
    }

    results: list[DeclineDetail] = []
    for di in decline_interviews:
        if di.originating_informant_id != informant_id:
            continue

        did = di.decline_interview_id
        cls_row = class_index.get(did)
        sub_row = subtype_index.get(did)

        results.append(
            DeclineDetail(
                decline_interview_id=did,
                originating_step=di.originating_step,
                originating_outcome_class=di.originating_outcome_class,
                response_verbatim=di.response_verbatim,
                thinking_verbatim=di.thinking_verbatim,
                manual_classification=cls_row.get("manual_classification") if cls_row else None,
                manual_classifier_id=cls_row.get("manual_classifier_id") if cls_row else None,
                safety_attribution_subtype=(
                    sub_row.get("safety_attribution_subtype") if sub_row else None
                ),
                subtype_classifier_id=sub_row.get("subtype_classifier_id") if sub_row else None,
            )
        )
    return results
