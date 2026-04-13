"""Tests for Smith's S salience and consensus free list computation."""

from datetime import date, datetime

from cdb_analyze.consensus import (
    compute_consensus_free_list,
    compute_pile_count_stats,
    smiths_s,
)
from cdb_core import FreelistRecord, InformantRecord, InterviewRecord, PileSortRecord


def test_smiths_s_first_item():
    """First item (rank 1 of 10) → salience 1.0."""
    assert smiths_s(1, 10) == 1.0


def test_smiths_s_last_item():
    """Last item (rank 10 of 10) → salience 0.1."""
    assert abs(smiths_s(10, 10) - 0.1) < 0.001


def test_smiths_s_middle_item():
    """Middle item (rank 5 of 10) → salience 0.6."""
    assert abs(smiths_s(5, 10) - 0.6) < 0.001


def test_smiths_s_single_item_list():
    """Single-item list → salience 1.0."""
    assert smiths_s(1, 1) == 1.0


def test_smiths_s_empty_list():
    assert smiths_s(1, 0) == 0.0


def _make_record(
    raw_order: list[str],
    parsed_items: list[str] | None = None,
    piles: list[list[str]] | None = None,
    run_index: int = 0,
) -> InformantRecord:
    if parsed_items is None:
        parsed_items = raw_order
    if piles is None:
        piles = [parsed_items]
    n = len(parsed_items)
    matrix = [[1] * n for _ in range(n)]
    return InformantRecord(
        informant_id=f"test_{run_index}",
        domain_slug="family",
        run_index=run_index,
        collection_date=datetime(2026, 4, 13),
        model_id="claude-opus-4-6",
        model_version_returned="claude-opus-4-6-20260401",
        family="claude",
        provider="anthropic",
        provider_request_id="msg_test",
        knowledge_cutoff=date(2025, 5, 1),
        open_weights=False,
        origin_country="us",
        alignment_method=None,
        collection_method="anthropic_api",
        api_endpoint="https://api.anthropic.com/v1/messages",
        api_version="2023-06-01",
        temperature=0.7,
        top_p=None,
        max_tokens=4096,
        system_prompt="",
        freelist=FreelistRecord(
            prompt_verbatim="test",
            prompt_version="v1",
            response_verbatim="test",
            response_object_json={},
            input_tokens=50,
            output_tokens=20,
            latency_ms=500,
            stop_reason="end_turn",
            parsed_items=parsed_items,
            parsed_raw_order=raw_order,
        ),
        pile_sort=PileSortRecord(
            prompt_verbatim="test",
            prompt_version="v1",
            response_verbatim="test",
            response_object_json={},
            input_tokens=50,
            output_tokens=20,
            latency_ms=400,
            stop_reason="end_turn",
            parsed_piles=piles,
            parsed_matrix=matrix,
        ),
        interview=InterviewRecord(
            prompt_verbatim="test",
            prompt_version="v1",
            response_verbatim="test",
            response_object_json={},
            input_tokens=30,
            output_tokens=10,
            latency_ms=200,
            stop_reason="end_turn",
            parsed_pile_labels=["label"] * len(piles),
        ),
        sha256_manifest={k: "a" * 64 for k in [
            "freelist_prompt", "freelist_response",
            "pilesort_prompt", "pilesort_response",
            "interview_prompt", "interview_response",
            "request_params", "informant_record_total",
        ]},
        qa_passed=True,
        qa_notes="",
    )


def test_consensus_single_run():
    """Single run: ranking matches original order."""
    r = _make_record(["mother", "father", "sister"])
    result = compute_consensus_free_list([r])

    assert result[0][0] == "mother"  # First → highest S
    assert result[-1][0] == "sister"  # Last → lowest S
    assert result[0][1] > result[1][1] > result[2][1]


def test_consensus_frequency_wins():
    """Item in all runs but always last beats item in 1 run but first."""
    # 5 runs; "common" appears in all 5 (always last, rank 3 of 3 → S=1/3)
    # "rare" appears in only 1 run (always first, rank 1 of 3 → S=1.0)
    records = []
    for i in range(5):
        records.append(_make_record(["x", "y", "common"], run_index=i))

    # Add one run where "rare" is first
    records.append(_make_record(["rare", "y", "common"], run_index=5))

    result = compute_consensus_free_list(records)
    salience = {item: s for item, s in result}

    # "common" appears in 6 runs: 5 × (1/3) + 1 × (1/3) = 6/3 = 2.0; composite = 2.0/6
    # "rare" appears in 1 run: 1 × 1.0 = 1.0; composite = 1.0/6
    assert salience["common"] > salience["rare"]


def test_consensus_rank_matters():
    """Among items with equal frequency, earlier rank gets higher S."""
    r1 = _make_record(["a", "b"], run_index=0)
    r2 = _make_record(["a", "b"], run_index=1)
    result = compute_consensus_free_list([r1, r2])

    salience = {item: s for item, s in result}
    assert salience["a"] > salience["b"]


def test_pile_count_stats_basic():
    r1 = _make_record(["a", "b"], piles=[["a"], ["b"]], run_index=0)
    r2 = _make_record(["a", "b"], piles=[["a", "b"]], run_index=1)

    stats = compute_pile_count_stats([r1, r2])
    assert stats["counts"] == [2, 1]
    assert stats["mean"] == 1.5
    assert stats["min"] == 1
    assert stats["max"] == 2


def test_pile_count_stats_empty():
    stats = compute_pile_count_stats([])
    assert stats["counts"] == []
    assert stats["mean"] == 0.0
