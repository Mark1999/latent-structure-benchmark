"""Tests for apps/ops_dashboard/lib/detail.py (OPS-T4).

All tests use synthetic fixtures constructed in-memory.
No real API calls. No reads from data/raw/*.jsonl.

The Streamlit rendering layer in apps/ops_dashboard/app.py is NOT tested
here — Streamlit requires a live server for that. Pure helper functions in
lib/detail.py are unit-tested exhaustively.

CDA SME binding notes tested:
- Note 2: Singletons flagged with is_singleton=True for inline rendering.
- Note 3: "0 items elicited" wording covered by empty-state tests.
- Note 5: Read-only classification fields surfaced or omitted correctly.
- Forbidden vocabulary: regex scan on all rendered string output.

Augmented (OPS-T4 tester pass):
- #3: whitespace-only freelist items preserved verbatim (format_freelist).
- #11: pile labels with punctuation/special chars preserved verbatim.
- #16: multiple declines for the same informant all returned.
- #17: classification row for a different informant's decline is not joined
  to the wrong informant (cross-informant join correctness).
- #25: format_pile_sort output is deterministic across two invocations.

See ARCHITECTURE.md §3.2 (InformantRecord / DeclineInterview schemas) and
docs/DATA_DICTIONARY.md §1.1 / §10 for field semantics.
"""

from __future__ import annotations

import re
from datetime import datetime

import pytest
from cdb_core.schemas import (
    DeclineInterview,
    FreelistRecord,
    InformantRecord,
    InterviewRecord,
    PileSortRecord,
)

from apps.ops_dashboard.lib.detail import (
    build_thinking_trace,
    find_decline_events,
    format_freelist,
    format_pile_sort,
)

# ── Shared manifest keys ──────────────────────────────────────────────────────

_MANIFEST_KEYS = [
    "freelist_prompt",
    "freelist_response",
    "pilesort_prompt",
    "pilesort_response",
    "interview_prompt",
    "interview_response",
    "request_params",
    "informant_record_total",
]

# ── Forbidden vocabulary patterns (CLAUDE.md §7 / ARCHITECTURE.md §1.5.4) ────

_FORBIDDEN_PATTERNS: list[str] = [
    r"\bbelieves\b",
    r"\bModel X believes",
    r"\bModel X thinks of",
    r"\bHow models see the world\b",
    r"\bModel X'?s worldview\b",
    r"\bworldview\b",
    r"\bCultural bias\b",
    r"\bWhat the model understands\b",
    r"\bwithin-model consensus\b",
    r"\bwithin-model eigenratio\b",
    r"\bwithin-model CCM\b",
]


# ── Record-builder helpers ────────────────────────────────────────────────────


def _freelist_record(
    *,
    items: list[str] | None = None,
    thinking: str = "",
) -> FreelistRecord:
    if items is None:
        items = ["mother", "father", "sister"]
    return FreelistRecord(
        prompt_verbatim="List every family term you can think of.",
        prompt_version="v1",
        response_verbatim="\n".join(f"{i+1}. {item}" for i, item in enumerate(items)),
        response_object_json={"id": "msg_001"},
        input_tokens=50,
        output_tokens=20,
        latency_ms=900,
        stop_reason="end_turn",
        parsed_items=items,
        parsed_raw_order=items,
        thinking_verbatim=thinking,
    )


def _pilesort_record(*, piles: list[list[str]] | None = None) -> PileSortRecord:
    if piles is None:
        piles = [["mother", "father"], ["sister"]]
    n_items = sum(len(p) for p in piles)
    return PileSortRecord(
        prompt_verbatim="Sort these items into piles.",
        prompt_version="v1",
        response_verbatim="(raw pile sort output)",
        response_object_json={"id": "msg_002"},
        input_tokens=60,
        output_tokens=30,
        latency_ms=1100,
        stop_reason="end_turn",
        parsed_piles=piles,
        parsed_matrix=[[0] * n_items for _ in range(n_items)],
    )


def _interview_record(*, labels: list[str] | None = None) -> InterviewRecord:
    if labels is None:
        labels = ["Parents", "Siblings"]
    return InterviewRecord(
        prompt_verbatim="Name each pile.",
        prompt_version="v1",
        response_verbatim="(raw interview output)",
        response_object_json={"id": "msg_003"},
        input_tokens=40,
        output_tokens=15,
        latency_ms=700,
        stop_reason="end_turn",
        parsed_pile_labels=labels,
    )


def _make_record(
    *,
    informant_id: str = "aaaa0000bbbb1111",
    domain_slug: str = "family",
    model_id: str = "claude-opus-4-6",
    freelist_items: list[str] | None = None,
    freelist_thinking: str = "",
    piles: list[list[str]] | None = None,
    pile_labels: list[str] | None = None,
) -> InformantRecord:
    """Construct a minimal but fully valid InformantRecord for detail tests."""
    return InformantRecord(
        informant_id=informant_id,
        domain_slug=domain_slug,
        run_index=0,
        collection_date=datetime(2026, 5, 1, 10, 0, 0),
        model_id=model_id,
        model_version_returned=f"{model_id}-20260501",
        family=model_id.split("-")[0],
        provider="anthropic",
        provider_request_id=f"req_{informant_id}",
        knowledge_cutoff=None,
        open_weights=False,
        origin_country="us",
        alignment_method=None,
        collection_method="anthropic_api",
        api_endpoint="https://api.anthropic.com/v1/messages",
        api_version="2023-06-01",
        temperature=0.7,
        top_p=None,
        max_tokens=4096,
        system_prompt="You are participating in a cognitive anthropology study.",
        freelist=_freelist_record(items=freelist_items, thinking=freelist_thinking),
        pile_sort=_pilesort_record(piles=piles),
        interview=_interview_record(labels=pile_labels),
        sha256_manifest={k: "0" * 64 for k in _MANIFEST_KEYS},
        qa_passed=True,
    )


def _make_decline_interview(
    *,
    decline_interview_id: str = "dec00001",
    originating_informant_id: str = "aaaa0000bbbb1111",
    response_verbatim: str = "I cannot help with that.",
    thinking_verbatim: str = "",
    originating_step: str = "freelist",
    originating_outcome_class: str = "refusal_string_match",
) -> DeclineInterview:
    return DeclineInterview(
        decline_interview_id=decline_interview_id,
        originating_informant_id=originating_informant_id,
        originating_failure_id=None,
        originating_step=originating_step,  # type: ignore[arg-type]
        originating_outcome_class=originating_outcome_class,  # type: ignore[arg-type]
        detection_rule_version="v1",
        detection_timestamp=datetime(2026, 5, 1, 10, 0, 0),
        followup_timestamp=datetime(2026, 5, 1, 10, 1, 0),
        model_id="claude-opus-4-6",
        model_version_returned="claude-opus-4-6-20260501",
        provider="anthropic",
        api_endpoint="https://api.anthropic.com/v1/messages",
        prompt_version="decline_v1",
        sha256_manifest="a" * 64,
        prompt_verbatim="Describe what happened in that exchange.",
        response_verbatim=response_verbatim,
        thinking_verbatim=thinking_verbatim,
        input_tokens=50,
        output_tokens=30,
        latency_ms=800,
        stop_reason="stop",
    )


# ── format_freelist tests ─────────────────────────────────────────────────────


class TestFormatFreelist:
    def test_populated_returns_ordered_items(self) -> None:
        """Populated freelist returns items in model-returned order."""
        record = _make_record(freelist_items=["mother", "father", "sister"])
        result = format_freelist(record)
        assert result == ["mother", "father", "sister"]

    def test_empty_returns_empty_list(self) -> None:
        """Zero-item freelist returns an empty list (not None, not error)."""
        record = _make_record(freelist_items=[])
        result = format_freelist(record)
        assert result == []

    def test_order_preserved(self) -> None:
        """Items are returned in the model's original order, not sorted."""
        items = ["zebra", "apple", "mango", "cherry"]
        record = _make_record(freelist_items=items)
        result = format_freelist(record)
        assert result == items

    def test_returns_new_list(self) -> None:
        """Mutating the returned list does not affect the record."""
        record = _make_record(freelist_items=["mother", "father"])
        result = format_freelist(record)
        result.append("extra")
        assert format_freelist(record) == ["mother", "father"]

    def test_whitespace_only_items_preserved(self) -> None:
        """Whitespace-only freelist items are preserved verbatim (format_freelist
        is a read-only presenter — it does not filter or normalise items).
        Coverage point #3."""
        items = ["mother", "   ", "father"]
        record = _make_record(freelist_items=items)
        result = format_freelist(record)
        assert result == items


# ── build_thinking_trace tests ────────────────────────────────────────────────


class TestBuildThinkingTrace:
    def test_non_empty_trace_returned(self) -> None:
        """Non-empty thinking_verbatim is returned as-is."""
        trace = "Step 1: analyze the task. Step 2: generate items."
        record = _make_record(freelist_thinking=trace)
        assert build_thinking_trace(record) == trace

    def test_empty_string_returns_none(self) -> None:
        """Empty thinking_verbatim (the default) returns None."""
        record = _make_record(freelist_thinking="")
        assert build_thinking_trace(record) is None

    def test_whitespace_only_returns_none(self) -> None:
        """Whitespace-only string is falsy — returns None."""
        # The schema stores exactly what the collection layer captured.
        # A whitespace-only trace is treated as absent.
        record = _make_record(freelist_thinking="   ")
        assert build_thinking_trace(record) is None


# ── format_pile_sort tests ────────────────────────────────────────────────────


class TestFormatPileSort:
    def test_multi_member_piles(self) -> None:
        """Multi-member piles have is_singleton=False, is_empty=False."""
        record = _make_record(
            piles=[["mother", "father"], ["sister", "brother"]],
            pile_labels=["Parents", "Siblings"],
        )
        result = format_pile_sort(record)
        assert len(result) == 2
        assert result[0].pile_number == 1
        assert result[0].label == "Parents"
        assert result[0].members == ["mother", "father"]
        assert not result[0].is_singleton
        assert not result[0].is_empty

    def test_singleton_pile_flagged(self) -> None:
        """A pile with exactly one member has is_singleton=True."""
        record = _make_record(
            piles=[["mother", "father"], ["only_child"]],
            pile_labels=["Parents", "Solo"],
        )
        result = format_pile_sort(record)
        assert result[1].is_singleton
        assert not result[1].is_empty
        assert result[1].members == ["only_child"]

    def test_empty_pile_flagged(self) -> None:
        """A pile with zero members has is_empty=True."""
        record = _make_record(
            piles=[["mother"], []],
            pile_labels=["One", "Empty"],
        )
        result = format_pile_sort(record)
        assert result[1].is_empty
        assert not result[1].is_singleton
        assert result[1].members == []

    def test_no_pile_sort_data_returns_empty_list(self) -> None:
        """When parsed_piles is empty, result is an empty list."""
        record = _make_record(piles=[], pile_labels=[])
        result = format_pile_sort(record)
        assert result == []

    def test_member_order_preserved(self) -> None:
        """Members are in the model's returned order, not sorted."""
        members = ["zebra", "apple", "mango"]
        record = _make_record(
            piles=[members],
            pile_labels=["Unsorted"],
        )
        result = format_pile_sort(record)
        assert result[0].members == members

    def test_pile_number_is_one_indexed(self) -> None:
        """pile_number starts at 1, not 0."""
        record = _make_record(
            piles=[["a"], ["b"]],
            pile_labels=["First", "Second"],
        )
        result = format_pile_sort(record)
        assert result[0].pile_number == 1
        assert result[1].pile_number == 2

    def test_label_falls_back_to_empty_string_when_short(self) -> None:
        """If interview returned fewer labels than piles, extra piles get ''."""
        record = _make_record(
            piles=[["a", "b"], ["c"]],
            pile_labels=["Only one label"],
        )
        result = format_pile_sort(record)
        assert result[0].label == "Only one label"
        assert result[1].label == ""

    def test_pile_labels_with_special_chars_preserved(self) -> None:
        """Pile labels containing punctuation, parens, or slashes are preserved
        verbatim without escaping or transformation.  Coverage point #11."""
        label = 'Wrong group of words (?)  — misc/other: "unclassified"'
        record = _make_record(
            piles=[["cousin", "nephew"]],
            pile_labels=[label],
        )
        result = format_pile_sort(record)
        assert result[0].label == label

    def test_format_pile_sort_deterministic(self) -> None:
        """Two calls on the same record return identical PileDetail lists.
        Coverage point #25."""
        record = _make_record(
            piles=[["mother", "father"], ["sister", "brother"], ["cousin"]],
            pile_labels=["Parents", "Siblings", "Extended"],
        )
        first = format_pile_sort(record)
        second = format_pile_sort(record)
        assert len(first) == len(second)
        for a, b in zip(first, second, strict=True):
            assert a.pile_number == b.pile_number
            assert a.label == b.label
            assert a.members == b.members
            assert a.is_singleton == b.is_singleton
            assert a.is_empty == b.is_empty


# ── find_decline_events tests ─────────────────────────────────────────────────


class TestFindDeclineEvents:
    def test_no_declines_returns_empty_list(self) -> None:
        """No decline interviews → empty result list."""
        result = find_decline_events(
            informant_id="aaaa0000bbbb1111",
            decline_interviews=[],
            classifications=[],
            subtypes=[],
        )
        assert result == []

    def test_one_decline_no_classifications(self) -> None:
        """One decline interview with no classification data."""
        di = _make_decline_interview(
            decline_interview_id="dec00001",
            originating_informant_id="aaaa0000bbbb1111",
            response_verbatim="I cannot sort zero items.",
        )
        result = find_decline_events(
            informant_id="aaaa0000bbbb1111",
            decline_interviews=[di],
            classifications=[],
            subtypes=[],
        )
        assert len(result) == 1
        d = result[0]
        assert d.decline_interview_id == "dec00001"
        assert d.response_verbatim == "I cannot sort zero items."
        assert d.manual_classification is None
        assert d.manual_classifier_id is None
        assert d.safety_attribution_subtype is None
        assert d.subtype_classifier_id is None

    def test_one_decline_with_manual_classification(self) -> None:
        """Manual classification is joined correctly."""
        di = _make_decline_interview(
            decline_interview_id="dec00002",
            originating_informant_id="aaaa0000bbbb1111",
        )
        cls = [
            {
                "decline_interview_id": "dec00002",
                "manual_classification": "substantive_compliance_with_empty_input",
                "manual_classifier_id": "mark",
            }
        ]
        result = find_decline_events(
            informant_id="aaaa0000bbbb1111",
            decline_interviews=[di],
            classifications=cls,
            subtypes=[],
        )
        assert len(result) == 1
        d = result[0]
        assert d.manual_classification == "substantive_compliance_with_empty_input"
        assert d.manual_classifier_id == "mark"
        assert d.safety_attribution_subtype is None

    def test_one_decline_with_both_classifications(self) -> None:
        """Both manual_classification and safety_attribution_subtype joined."""
        di = _make_decline_interview(
            decline_interview_id="dec00003",
            originating_informant_id="aaaa0000bbbb1111",
        )
        cls = [
            {
                "decline_interview_id": "dec00003",
                "manual_classification": "safety_event_attribution",
                "manual_classifier_id": "mark",
            }
        ]
        subs = [
            {
                "decline_interview_id": "dec00003",
                "safety_attribution_subtype": "k_frame",
                "subtype_classifier_id": "mark",
            }
        ]
        result = find_decline_events(
            informant_id="aaaa0000bbbb1111",
            decline_interviews=[di],
            classifications=cls,
            subtypes=subs,
        )
        assert len(result) == 1
        d = result[0]
        assert d.manual_classification == "safety_event_attribution"
        assert d.safety_attribution_subtype == "k_frame"

    def test_only_matching_informant_id_returned(self) -> None:
        """Declines from other informants are not returned."""
        di_match = _make_decline_interview(
            decline_interview_id="dec00010",
            originating_informant_id="target_id",
        )
        di_other = _make_decline_interview(
            decline_interview_id="dec00011",
            originating_informant_id="other_id",
        )
        result = find_decline_events(
            informant_id="target_id",
            decline_interviews=[di_match, di_other],
            classifications=[],
            subtypes=[],
        )
        assert len(result) == 1
        assert result[0].decline_interview_id == "dec00010"

    def test_thinking_verbatim_propagated(self) -> None:
        """thinking_verbatim from DeclineInterview is surfaced in DeclineDetail."""
        trace = "1. Analyze. 2. Respond."
        di = _make_decline_interview(
            decline_interview_id="dec00020",
            originating_informant_id="aaaa0000bbbb1111",
            thinking_verbatim=trace,
        )
        result = find_decline_events(
            informant_id="aaaa0000bbbb1111",
            decline_interviews=[di],
            classifications=[],
            subtypes=[],
        )
        assert result[0].thinking_verbatim == trace

    def test_multiple_declines_same_informant_all_returned(self) -> None:
        """Multiple decline interviews for the same informant are all returned
        in input order.  Coverage point #16."""
        di1 = _make_decline_interview(
            decline_interview_id="dec_multi_01",
            originating_informant_id="aaaa0000bbbb1111",
            originating_step="freelist",
            response_verbatim="First decline.",
        )
        di2 = _make_decline_interview(
            decline_interview_id="dec_multi_02",
            originating_informant_id="aaaa0000bbbb1111",
            originating_step="pile_sort",
            response_verbatim="Second decline.",
        )
        di3 = _make_decline_interview(
            decline_interview_id="dec_multi_03",
            originating_informant_id="aaaa0000bbbb1111",
            originating_step="interview",
            response_verbatim="Third decline.",
        )
        result = find_decline_events(
            informant_id="aaaa0000bbbb1111",
            decline_interviews=[di1, di2, di3],
            classifications=[],
            subtypes=[],
        )
        assert len(result) == 3
        assert [d.decline_interview_id for d in result] == [
            "dec_multi_01",
            "dec_multi_02",
            "dec_multi_03",
        ]

    def test_classification_for_other_informants_decline_not_joined(self) -> None:
        """A classification row whose decline_interview_id belongs to a different
        informant's decline is not surfaced for the queried informant.

        Scenario: two informants, each with one decline.  The classification
        artifact covers the OTHER informant's decline_interview_id only.  The
        queried informant's DeclineDetail must have manual_classification=None.

        Coverage point #17 (cross-informant join correctness).
        """
        # target informant's decline (unclassified)
        di_target = _make_decline_interview(
            decline_interview_id="dec_join_target",
            originating_informant_id="target_informant_id",
            response_verbatim="Target's decline text.",
        )
        # other informant's decline (classified)
        di_other = _make_decline_interview(
            decline_interview_id="dec_join_other",
            originating_informant_id="other_informant_id",
            response_verbatim="Other informant's decline text.",
        )
        # Classification row points to the OTHER informant's decline_interview_id
        cls = [
            {
                "decline_interview_id": "dec_join_other",
                "manual_classification": "safety_event_attribution",
                "manual_classifier_id": "mark",
            }
        ]

        result = find_decline_events(
            informant_id="target_informant_id",
            decline_interviews=[di_target, di_other],
            classifications=cls,
            subtypes=[],
        )

        # Only target's decline is returned
        assert len(result) == 1
        assert result[0].decline_interview_id == "dec_join_target"
        # And it must not have picked up the classification that belongs to
        # the other informant's decline
        assert result[0].manual_classification is None
        assert result[0].manual_classifier_id is None


# ── Forbidden vocabulary scan ─────────────────────────────────────────────────


class TestForbiddenVocabulary:
    """Regression: helper output strings must not contain forbidden vocabulary."""

    def _all_output_strings(self) -> list[str]:
        """Collect all string values produced by the detail helpers."""
        strings: list[str] = []

        # format_freelist
        rec = _make_record(freelist_items=["mother", "father"])
        strings.extend(format_freelist(rec))

        # build_thinking_trace
        trace = build_thinking_trace(
            _make_record(freelist_thinking="Step 1: list items.")
        )
        if trace:
            strings.append(trace)

        # format_pile_sort — labels, members
        pile_rec = _make_record(
            piles=[["mother", "father"], ["sister"]],
            pile_labels=["Parents", "Siblings"],
        )
        for pile in format_pile_sort(pile_rec):
            strings.append(pile.label)
            strings.extend(pile.members)

        # find_decline_events
        di = _make_decline_interview(
            decline_interview_id="dec_voc_01",
            originating_informant_id="aaaa0000bbbb1111",
            response_verbatim="Sorted into piles.",
        )
        cls = [
            {
                "decline_interview_id": "dec_voc_01",
                "manual_classification": "substantive_compliance_with_empty_input",
                "manual_classifier_id": "mark",
            }
        ]
        subs = [
            {
                "decline_interview_id": "dec_voc_01",
                "safety_attribution_subtype": "k_frame",
                "subtype_classifier_id": "mark",
            }
        ]
        for detail in find_decline_events(
            informant_id="aaaa0000bbbb1111",
            decline_interviews=[di],
            classifications=cls,
            subtypes=subs,
        ):
            strings.append(detail.response_verbatim)
            if detail.manual_classification:
                strings.append(detail.manual_classification)
            if detail.safety_attribution_subtype:
                strings.append(detail.safety_attribution_subtype)

        return strings

    @pytest.mark.parametrize("pattern", _FORBIDDEN_PATTERNS)
    def test_no_forbidden_vocabulary_in_output(self, pattern: str) -> None:
        """No forbidden vocabulary pattern appears in helper output strings."""
        rx = re.compile(pattern, re.IGNORECASE)
        for s in self._all_output_strings():
            assert not rx.search(s), (
                f"Forbidden pattern '{pattern}' found in output: {s!r}"
            )
