"""Tests for co-occurrence matrix computation. See ARCHITECTURE.md §4.2."""

from datetime import date, datetime

import pytest
from cdb_analyze.cooccurrence import build_cooccurrence_matrix
from cdb_core import FreelistRecord, InformantRecord, InterviewRecord, PileSortRecord


def _record(
    items: list[str],
    piles: list[list[str]],
    matrix: list[list[int]],
    run_index: int = 0,
) -> InformantRecord:
    return InformantRecord(
        informant_id=f"test_{run_index}",
        domain_slug="family",
        run_index=run_index,
        collection_date=datetime(2026, 4, 13, 10, 0, 0),
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
            parsed_items=items,
            parsed_raw_order=items,
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


def test_single_run_same_pile():
    """Items in same pile → 1.0, different piles → 0.0."""
    items = ["a", "b", "c"]
    piles = [["a", "b"], ["c"]]
    matrix = [[1, 1, 0], [1, 1, 0], [0, 0, 1]]
    r = _record(items, piles, matrix)

    result = build_cooccurrence_matrix([r])

    idx = {item: i for i, item in enumerate(result.items)}
    assert result.matrix[idx["a"]][idx["b"]] == 1.0
    assert result.matrix[idx["a"]][idx["c"]] == 0.0


def test_two_runs_half_agreement():
    """Items in same pile in 1 of 2 runs → 0.5."""
    items = ["a", "b", "c"]
    # Run 1: a,b together; c alone
    r1 = _record(items, [["a", "b"], ["c"]], [[1, 1, 0], [1, 1, 0], [0, 0, 1]], 0)
    # Run 2: a alone; b,c together
    r2 = _record(items, [["a"], ["b", "c"]], [[1, 0, 0], [0, 1, 1], [0, 1, 1]], 1)

    result = build_cooccurrence_matrix([r1, r2])

    idx = {item: i for i, item in enumerate(result.items)}
    assert result.matrix[idx["a"]][idx["b"]] == 0.5
    assert result.matrix[idx["b"]][idx["c"]] == 0.5


def test_diagonal_is_one():
    items = ["a", "b"]
    r = _record(items, [["a"], ["b"]], [[1, 0], [0, 1]])
    result = build_cooccurrence_matrix([r])
    for i in range(len(result.items)):
        assert result.matrix[i][i] == 1.0


def test_symmetric():
    items = ["a", "b", "c"]
    r = _record(items, [["a", "b"], ["c"]], [[1, 1, 0], [1, 1, 0], [0, 0, 1]])
    result = build_cooccurrence_matrix([r])
    n = len(result.items)
    for i in range(n):
        for j in range(n):
            assert result.matrix[i][j] == result.matrix[j][i]


def test_empty_records_raises():
    with pytest.raises(ValueError, match="No records"):
        build_cooccurrence_matrix([])


def test_mismatched_model_raises():
    items = ["a", "b"]
    r1 = _record(items, [["a", "b"]], [[1, 1], [1, 1]], 0)
    r2 = _record(items, [["a", "b"]], [[1, 1], [1, 1]], 1)
    # Hack: change model_id on r2
    r2_dict = r2.model_dump()
    r2_dict["model_id"] = "different-model"
    r2_modified = InformantRecord.model_validate(r2_dict)

    with pytest.raises(ValueError, match="same model"):
        build_cooccurrence_matrix([r1, r2_modified])
