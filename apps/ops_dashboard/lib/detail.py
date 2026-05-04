"""Pure helper functions for the single-informant detail view (OPS-T4/T5).

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

CDA SME binding notes (2026-05-02 OPS-T5 verdict):
- Q1: Section 4 disclaimer text is rendered by the caller verbatim.
- Q2: Subheader label inside each expander is "Extended-thinking output
  (verbatim)" — not "Thinking trace (verbatim)".
- Q3: Empty-thinking placeholder is "No extended-thinking output for this
  step." — rendered by the caller.
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


# ── Pile-sort count helper (OPS-T7) ──────────────────────────────────────────


def pile_sort_item_count(record: InformantRecord) -> int:
    """Return the total number of items placed across all piles (sort-time count).

    Uses the flattened total of PileSortRecord.parsed_piles — i.e., the count
    of items the model was actually asked to sort, observed at sort time.

    If the model received N items and sorted N items, this is N. If the model
    dropped some items during sorting, this reflects only the items that were
    placed in at least one pile.

    CDA SME option (a), binding (OPS-T7 verdict §Q5):
        sum(len(pile) for pile in record.pile_sort.parsed_piles)

    Not to be confused with len(record.freelist.parsed_items) — that is the
    count produced by Step 1, which may differ when item_source != "own_freelist"
    or when the model dropped items during pile-sort.

    Args:
        record: An InformantRecord.

    Returns:
        Total item count across all piles. 0 when parsed_piles is empty.
    """
    return sum(len(pile) for pile in record.pile_sort.parsed_piles)


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


# ── Decline summary helpers (OPS-T6) ─────────────────────────────────────────


@dataclass
class DeclineSummaryRow:
    """Compact summary projection of one decline event for the summary table.

    Attributes:
        decline_interview_id: Unique ID of the DeclineInterview.
        originating_step: Which CDA step triggered the decline-interview.
            One of: "freelist", "pile_sort", "interview", "pre_session".
        originating_outcome_class: Machine-detected outcome class.
            One of the seven Literal values in DeclineInterview.
        manual_classification: Human-assigned disposition label, or None when
            no classification row has been joined yet.
        safety_attribution_subtype: Human-assigned subtype label
            ("k_frame" / "k_vocab"), or None when not applicable or not yet
            classified.
    """

    decline_interview_id: str
    originating_step: str
    originating_outcome_class: str
    manual_classification: str | None
    safety_attribution_subtype: str | None


def build_decline_summary(declines: list[DeclineDetail]) -> list[DeclineSummaryRow]:
    """Project a list of DeclineDetail objects into compact summary rows.

    Pure, deterministic, no I/O. Preserves input order. Reads only from
    its argument.

    Args:
        declines: List of DeclineDetail objects for one informant, as returned
            by find_decline_events.

    Returns:
        List of DeclineSummaryRow objects in input order. Empty list when
        declines is empty.
    """
    return [
        DeclineSummaryRow(
            decline_interview_id=d.decline_interview_id,
            originating_step=d.originating_step,
            originating_outcome_class=d.originating_outcome_class,
            manual_classification=d.manual_classification,
            safety_attribution_subtype=d.safety_attribution_subtype,
        )
        for d in declines
    ]


# ── Raw transcript helpers (OPS-T5) ──────────────────────────────────────────


@dataclass
class TranscriptStep:
    """Rendered view of one CDA dialog step's verbatim transcript.

    Attributes:
        step_name: Internal identifier — one of "freelist", "pile_sort",
            "interview".
        step_label: Display label for the expander widget, e.g.
            "Step 1 — Freelist transcript".
        prompt_version: The prompt version string (e.g. "v1").
        prompt_verbatim: The exact prompt text sent to the model.
        thinking_verbatim: The model's extended-thinking output text as
            returned. Empty string when no extended-thinking output was
            produced; never None.
        has_thinking: True when thinking_verbatim contains non-whitespace
            content. The renderer reads this flag rather than re-evaluating
            the string.
        response_verbatim: The model's response text as returned verbatim.
        input_tokens: Token count for the input (prompt) side.
        output_tokens: Token count for the output (response) side.
        latency_ms: Round-trip latency for this step in milliseconds.
        stop_reason: The stop reason string returned by the provider API.
    """

    step_name: str
    step_label: str
    prompt_version: str
    prompt_verbatim: str
    thinking_verbatim: str
    has_thinking: bool
    response_verbatim: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    stop_reason: str


def build_step_transcripts(record: InformantRecord) -> list[TranscriptStep]:
    """Return the verbatim three-step dialog for one informant.

    Returns exactly three TranscriptStep objects in CDA protocol order:
    Step 1 (freelist), Step 2 (pile-sort), Step 3 (interview / pile-naming).

    No filtering, no re-summarisation. Empty extended-thinking output is
    preserved as an empty string — has_thinking is the flag the renderer
    reads to decide whether to show the placeholder caption.

    READ-ONLY INVARIANT: reads only from the InformantRecord argument.
    No file I/O, no network calls, no LLM client imports.

    Args:
        record: An InformantRecord with freelist, pile_sort, and interview
            sub-records.

    Returns:
        List of three TranscriptStep objects in CDA order.
    """
    fl = record.freelist
    ps = record.pile_sort
    iv = record.interview

    return [
        TranscriptStep(
            step_name="freelist",
            step_label="Step 1 — Freelist transcript",
            prompt_version=fl.prompt_version,
            prompt_verbatim=fl.prompt_verbatim,
            thinking_verbatim=fl.thinking_verbatim,
            has_thinking=bool(fl.thinking_verbatim and fl.thinking_verbatim.strip()),
            response_verbatim=fl.response_verbatim,
            input_tokens=fl.input_tokens,
            output_tokens=fl.output_tokens,
            latency_ms=fl.latency_ms,
            stop_reason=fl.stop_reason,
        ),
        TranscriptStep(
            step_name="pile_sort",
            step_label="Step 2 — Pile-sort transcript",
            prompt_version=ps.prompt_version,
            prompt_verbatim=ps.prompt_verbatim,
            thinking_verbatim=ps.thinking_verbatim,
            has_thinking=bool(ps.thinking_verbatim and ps.thinking_verbatim.strip()),
            response_verbatim=ps.response_verbatim,
            input_tokens=ps.input_tokens,
            output_tokens=ps.output_tokens,
            latency_ms=ps.latency_ms,
            stop_reason=ps.stop_reason,
        ),
        TranscriptStep(
            step_name="interview",
            step_label="Step 3 — Interview / pile-naming transcript",
            prompt_version=iv.prompt_version,
            prompt_verbatim=iv.prompt_verbatim,
            thinking_verbatim=iv.thinking_verbatim,
            has_thinking=bool(iv.thinking_verbatim and iv.thinking_verbatim.strip()),
            response_verbatim=iv.response_verbatim,
            input_tokens=iv.input_tokens,
            output_tokens=iv.output_tokens,
            latency_ms=iv.latency_ms,
            stop_reason=iv.stop_reason,
        ),
    ]
