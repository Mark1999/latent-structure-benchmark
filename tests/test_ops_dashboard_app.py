"""Tests for apps/ops_dashboard/lib/picker.py.

All tests use synthetic InformantRecord fixtures constructed in-memory.
No real API calls. No reads from data/raw/informants.jsonl.

The Streamlit rendering layer in apps/ops_dashboard/app.py is NOT tested
here — Streamlit requires a live server for that. Instead, the pure helper
functions extracted into lib/picker.py are unit-tested exhaustively.

See ARCHITECTURE.md §3.2 (InformantRecord schema) and
docs/DATA_DICTIONARY.md §1.1 for field semantics.
"""

from __future__ import annotations

from datetime import datetime

import pytest
from cdb_core.schemas import (
    FreelistRecord,
    InformantRecord,
    InterviewRecord,
    PileSortRecord,
)

from apps.ops_dashboard.lib.picker import (
    apply_filters,
    available_domains,
    available_informant_ids,
    available_model_ids,
)

# ── Shared manifest keys (DATA_DICTIONARY.md §1.1 — eight required keys) ──

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


# ── Record-builder helpers ──

def _freelist_record() -> FreelistRecord:
    return FreelistRecord(
        prompt_verbatim="List every family term you can think of.",
        prompt_version="v1",
        response_verbatim="1. mother\n2. father\n3. sister",
        response_object_json={"id": "msg_001"},
        input_tokens=50,
        output_tokens=20,
        latency_ms=900,
        stop_reason="end_turn",
        parsed_items=["mother", "father", "sister"],
        parsed_raw_order=["mother", "father", "sister"],
    )


def _pilesort_record() -> PileSortRecord:
    return PileSortRecord(
        prompt_verbatim="Sort these items into piles.",
        prompt_version="v1",
        response_verbatim="Pile 1: mother, father\nPile 2: sister",
        response_object_json={"id": "msg_002"},
        input_tokens=60,
        output_tokens=30,
        latency_ms=1100,
        stop_reason="end_turn",
        parsed_piles=[["mother", "father"], ["sister"]],
        parsed_matrix=[[1, 1, 0], [1, 1, 0], [0, 0, 1]],
    )


def _interview_record() -> InterviewRecord:
    return InterviewRecord(
        prompt_verbatim="Name each pile.",
        prompt_version="v1",
        response_verbatim="Pile 1: Parents\nPile 2: Siblings",
        response_object_json={"id": "msg_003"},
        input_tokens=40,
        output_tokens=15,
        latency_ms=700,
        stop_reason="end_turn",
        parsed_pile_labels=["Parents", "Siblings"],
    )


def _make_record(
    *,
    informant_id: str = "aaaa0000bbbb1111",
    domain_slug: str = "family",
    model_id: str = "claude-opus-4-6",
    run_index: int = 0,
    qa_passed: bool = True,
) -> InformantRecord:
    """Construct a minimal but fully valid InformantRecord for picker tests."""
    return InformantRecord(
        informant_id=informant_id,
        domain_slug=domain_slug,
        run_index=run_index,
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
        freelist=_freelist_record(),
        pile_sort=_pilesort_record(),
        interview=_interview_record(),
        sha256_manifest={k: "0" * 64 for k in _MANIFEST_KEYS},
        qa_passed=qa_passed,
    )


# ── Fixtures ──

@pytest.fixture()
def five_records() -> list[InformantRecord]:
    """Five records spanning two models and three domains.

    model_id       domain_slug  informant_id
    claude-opus-4-6  family     p00000000000001
    claude-opus-4-6  holidays   p00000000000002
    gpt-4o           family     p00000000000003
    gpt-4o           food       p00000000000004
    claude-opus-4-6  food       p00000000000005
    """
    return [
        _make_record(
            informant_id="p00000000000001",
            domain_slug="family",
            model_id="claude-opus-4-6",
            run_index=0,
        ),
        _make_record(
            informant_id="p00000000000002",
            domain_slug="holidays",
            model_id="claude-opus-4-6",
            run_index=0,
        ),
        _make_record(
            informant_id="p00000000000003",
            domain_slug="family",
            model_id="gpt-4o",
            run_index=0,
        ),
        _make_record(
            informant_id="p00000000000004",
            domain_slug="food",
            model_id="gpt-4o",
            run_index=0,
        ),
        _make_record(
            informant_id="p00000000000005",
            domain_slug="food",
            model_id="claude-opus-4-6",
            run_index=1,
        ),
    ]


# ── available_model_ids ──

class TestAvailableModelIds:
    def test_returns_sorted_unique_model_ids(
        self, five_records: list[InformantRecord]
    ) -> None:
        """Returns a sorted, deduplicated list of model_id values."""
        result = available_model_ids(five_records)

        # Sorted alphabetically; claude comes before gpt
        assert result == ["claude-opus-4-6", "gpt-4o"]

    def test_empty_records_returns_empty_list(self) -> None:
        """Empty input returns empty list without error."""
        assert available_model_ids([]) == []

    def test_deduplication(self) -> None:
        """Duplicate model_id values appear only once."""
        records = [
            _make_record(informant_id="x01", model_id="model-a"),
            _make_record(informant_id="x02", model_id="model-a"),
            _make_record(informant_id="x03", model_id="model-b"),
        ]
        result = available_model_ids(records)

        assert result == ["model-a", "model-b"]

    def test_sort_order(self) -> None:
        """Results are in ascending lexicographic order."""
        records = [
            _make_record(informant_id="y01", model_id="zzz-model"),
            _make_record(informant_id="y02", model_id="aaa-model"),
            _make_record(informant_id="y03", model_id="mmm-model"),
        ]
        result = available_model_ids(records)

        assert result == ["aaa-model", "mmm-model", "zzz-model"]

    def test_single_record(self) -> None:
        """Single record returns a one-element list."""
        records = [_make_record(informant_id="z01", model_id="solo-model")]
        result = available_model_ids(records)

        assert result == ["solo-model"]


# ── available_domains ──

class TestAvailableDomains:
    def test_returns_sorted_unique_domains(
        self, five_records: list[InformantRecord]
    ) -> None:
        """Returns a sorted, deduplicated list of domain_slug values."""
        result = available_domains(five_records)

        assert result == ["family", "food", "holidays"]

    def test_empty_records_returns_empty_list(self) -> None:
        assert available_domains([]) == []

    def test_deduplication(self) -> None:
        records = [
            _make_record(informant_id="d01", domain_slug="food"),
            _make_record(informant_id="d02", domain_slug="food"),
            _make_record(informant_id="d03", domain_slug="family"),
        ]
        result = available_domains(records)

        assert result == ["family", "food"]

    def test_sort_order(self) -> None:
        records = [
            _make_record(informant_id="e01", domain_slug="weather"),
            _make_record(informant_id="e02", domain_slug="animals"),
            _make_record(informant_id="e03", domain_slug="music"),
        ]
        result = available_domains(records)

        assert result == ["animals", "music", "weather"]

    def test_single_record(self) -> None:
        """Single record returns a one-element list."""
        records = [_make_record(informant_id="f01", domain_slug="solo-domain")]
        result = available_domains(records)

        assert result == ["solo-domain"]


# ── apply_filters ──

class TestApplyFilters:
    def test_both_empty_returns_all_records(
        self, five_records: list[InformantRecord]
    ) -> None:
        """Empty model_ids and empty domains → all records returned."""
        result = apply_filters(five_records, model_ids=[], domains=[])

        assert result == five_records

    def test_filter_by_single_model(
        self, five_records: list[InformantRecord]
    ) -> None:
        """Single model_id filter returns only records for that model."""
        result = apply_filters(five_records, model_ids=["gpt-4o"], domains=[])

        assert len(result) == 2
        assert all(r.model_id == "gpt-4o" for r in result)

    def test_filter_by_single_domain(
        self, five_records: list[InformantRecord]
    ) -> None:
        """Single domain filter returns only records for that domain."""
        result = apply_filters(five_records, model_ids=[], domains=["food"])

        assert len(result) == 2
        assert all(r.domain_slug == "food" for r in result)

    def test_filter_by_model_and_domain_intersection(
        self, five_records: list[InformantRecord]
    ) -> None:
        """model_id + domain filters are ANDed — only the intersection is returned."""
        result = apply_filters(
            five_records,
            model_ids=["claude-opus-4-6"],
            domains=["family"],
        )

        assert len(result) == 1
        assert result[0].informant_id == "p00000000000001"

    def test_filter_multi_model_ids(
        self, five_records: list[InformantRecord]
    ) -> None:
        """Multiple model_ids → records matching ANY of the listed models."""
        result = apply_filters(
            five_records,
            model_ids=["claude-opus-4-6", "gpt-4o"],
            domains=[],
        )

        # Both models are in the list — all five records should be returned
        assert len(result) == 5

    def test_filter_multi_model_ids_or_semantics_with_phantom(
        self, five_records: list[InformantRecord]
    ) -> None:
        """OR-within-axis: a nonexistent model in the list does not suppress
        results for a model that does exist.

        Proves that model_ids is treated as 'record.model_id IN set', not
        'record.model_id == all listed values'.  If apply_filters mistakenly
        ANDed the model values together, zero records would be returned here.
        """
        result = apply_filters(
            five_records,
            model_ids=["gpt-4o", "nonexistent-model"],
            domains=[],
        )

        # Only gpt-4o records should be returned; the phantom entry is ignored
        assert len(result) == 2
        assert all(r.model_id == "gpt-4o" for r in result)

    def test_filter_multi_domains(
        self, five_records: list[InformantRecord]
    ) -> None:
        """Multiple domains → records matching ANY of the listed domains."""
        result = apply_filters(
            five_records,
            model_ids=[],
            domains=["family", "holidays"],
        )

        assert len(result) == 3
        returned_domains = {r.domain_slug for r in result}
        assert returned_domains == {"family", "holidays"}

    def test_filter_multi_domains_or_semantics_with_phantom(
        self, five_records: list[InformantRecord]
    ) -> None:
        """OR-within-axis: a nonexistent domain in the list does not suppress
        results for a domain that does exist.

        Mirrors test_filter_multi_model_ids_or_semantics_with_phantom for the
        domain axis.  Verifies that domains is treated as a set membership
        check rather than an AND across all listed values.
        """
        result = apply_filters(
            five_records,
            model_ids=[],
            domains=["food", "nonexistent-domain"],
        )

        # Only food records should be returned; the phantom entry is ignored
        assert len(result) == 2
        assert all(r.domain_slug == "food" for r in result)

    def test_filter_multi_model_and_multi_domain(
        self, five_records: list[InformantRecord]
    ) -> None:
        """Multiple model_ids AND multiple domains — intersection of both axes."""
        result = apply_filters(
            five_records,
            model_ids=["claude-opus-4-6"],
            domains=["family", "food"],
        )

        # claude: family (p1) and food (p5) — both match
        assert len(result) == 2
        informant_ids = {r.informant_id for r in result}
        assert informant_ids == {"p00000000000001", "p00000000000005"}

    def test_filter_no_match_returns_empty(
        self, five_records: list[InformantRecord]
    ) -> None:
        """A filter that matches nothing returns an empty list."""
        result = apply_filters(
            five_records,
            model_ids=["nonexistent-model"],
            domains=[],
        )

        assert result == []

    def test_filter_does_not_mutate_input(
        self, five_records: list[InformantRecord]
    ) -> None:
        """apply_filters returns a new list; input list is unchanged."""
        original_len = len(five_records)
        apply_filters(five_records, model_ids=["gpt-4o"], domains=[])

        assert len(five_records) == original_len

    def test_empty_records_returns_empty(self) -> None:
        """Empty record list handled gracefully."""
        result = apply_filters([], model_ids=["gpt-4o"], domains=["family"])

        assert result == []

    def test_empty_records_empty_filters(self) -> None:
        """Empty records + empty filters returns empty list without error."""
        result = apply_filters([], model_ids=[], domains=[])

        assert result == []


# ── available_informant_ids ──

class TestAvailableInformantIds:
    def test_returns_sorted_informant_ids(
        self, five_records: list[InformantRecord]
    ) -> None:
        """Returns informant_id values in sorted order."""
        result = available_informant_ids(five_records)

        assert result == [
            "p00000000000001",
            "p00000000000002",
            "p00000000000003",
            "p00000000000004",
            "p00000000000005",
        ]

    def test_empty_records_returns_empty_list(self) -> None:
        """Empty input returns empty list without error."""
        assert available_informant_ids([]) == []

    def test_sort_order_is_lexicographic(self) -> None:
        """Informant IDs are sorted in ascending lexicographic order."""
        records = [
            _make_record(informant_id="zzz_last"),
            _make_record(informant_id="aaa_first"),
            _make_record(informant_id="mmm_middle"),
        ]
        result = available_informant_ids(records)

        assert result == ["aaa_first", "mmm_middle", "zzz_last"]

    def test_single_record(self) -> None:
        """Single record returns a one-element list."""
        records = [_make_record(informant_id="only_one")]
        result = available_informant_ids(records)

        assert result == ["only_one"]

    def test_filtered_subset(self, five_records: list[InformantRecord]) -> None:
        """Passing a pre-filtered list returns only IDs from that subset."""
        filtered = apply_filters(
            five_records, model_ids=["gpt-4o"], domains=[]
        )
        result = available_informant_ids(filtered)

        assert result == ["p00000000000003", "p00000000000004"]
