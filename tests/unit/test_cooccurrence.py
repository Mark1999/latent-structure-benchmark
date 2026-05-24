"""Tests for co-occurrence matrix computation. See ARCHITECTURE.md §4.2."""

from datetime import date, datetime

import pytest
from cdb_analyze.cooccurrence import (
    build_cooccurrence_matrix,
    build_pooled_cooccurrence_matrix,
    compute_cross_model_term_frequency,
)
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


# ──────────────────────────────────────────────────────────────────────
# compute_cross_model_term_frequency tests
# ──────────────────────────────────────────────────────────────────────

def _record_for_model(
    model_id: str,
    piles: list[list[str]],
    freelist_items: list[str] | None = None,
    run_index: int = 0,
) -> InformantRecord:
    """Build a minimal record for a given model with specified pile structure."""
    if freelist_items is None:
        freelist_items = []
    all_pile_items = [item for pile in piles for item in pile]
    n = len(all_pile_items)
    matrix = [[0] * n for _ in range(n)]
    idx = {item: i for i, item in enumerate(all_pile_items)}
    for pile in piles:
        for a in pile:
            for b in pile:
                matrix[idx[a]][idx[b]] = 1

    return InformantRecord(
        informant_id=f"{model_id}_{run_index}",
        domain_slug="family",
        run_index=run_index,
        collection_date=datetime(2026, 4, 13, 10, 0, 0),
        model_id=model_id,
        model_version_returned=f"{model_id}-v1",
        family="test",
        provider="anthropic",
        provider_request_id=f"req_{model_id}_{run_index}",
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
            parsed_items=freelist_items,
            parsed_raw_order=freelist_items,
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


def test_cross_model_term_frequency_counts_models_not_runs():
    """f_models counts distinct models, not runs.

    Term 'x' appears in 5 runs of model-a → f_models(x) = 1.
    Term 'y' appears once each in model-a and model-b → f_models(y) = 2.
    """
    recs_a = [
        _record_for_model("model-a", [["x", "y"]], run_index=i)
        for i in range(5)
    ]
    recs_b = [
        _record_for_model("model-b", [["y", "z"]], run_index=0)
    ]
    records_by_model = {"model-a": recs_a, "model-b": recs_b}

    result = compute_cross_model_term_frequency(records_by_model)
    freq_dict = {term: f for term, f in result}

    assert freq_dict["x"] == 1  # only model-a
    assert freq_dict["y"] == 2  # both models
    assert freq_dict["z"] == 1  # only model-b


def test_cross_model_term_frequency_sorted_descending():
    """Result is sorted descending by f_models."""
    recs = {
        "model-a": [_record_for_model("model-a", [["a", "b", "c"]])],
        "model-b": [_record_for_model("model-b", [["b", "c"]])],
        "model-c": [_record_for_model("model-c", [["c"]])],
    }
    result = compute_cross_model_term_frequency(recs)
    freqs = [f for _, f in result]
    assert freqs == sorted(freqs, reverse=True)
    # 'c' appears in all 3 models, 'b' in 2, 'a' in 1
    freq_dict = {t: f for t, f in result}
    assert freq_dict["c"] == 3
    assert freq_dict["b"] == 2
    assert freq_dict["a"] == 1


def test_cross_model_term_frequency_uses_pile_sort_not_freelist():
    """f_models is computed from pile_sort.parsed_piles, NOT freelist.parsed_items.

    Term 'freelist_only' appears in the free list but NOT in any pile sort.
    It must not appear in the cross-model frequency output.
    """
    rec = _record_for_model(
        "model-a",
        piles=[["pile_term"]],
        freelist_items=["freelist_only", "pile_term"],
    )
    records_by_model = {"model-a": [rec]}
    result = compute_cross_model_term_frequency(records_by_model)
    term_names = {t for t, _ in result}
    assert "freelist_only" not in term_names
    assert "pile_term" in term_names


def test_cross_model_term_frequency_empty():
    """Empty records_by_model returns empty list."""
    result = compute_cross_model_term_frequency({})
    assert result == []


def test_cross_model_term_frequency_tie_breaking():
    """Ties in f_models are broken by ascending lexicographic order."""
    recs = {
        "model-a": [_record_for_model("model-a", [["b", "a"]])],
        "model-b": [_record_for_model("model-b", [["b", "a"]])],
    }
    result = compute_cross_model_term_frequency(recs)
    # Both 'a' and 'b' have f_models=2; lexicographic order: 'a' < 'b'
    terms_in_order = [t for t, _ in result]
    assert terms_in_order == ["a", "b"]


# ──────────────────────────────────────────────────────────────────────
# build_pooled_cooccurrence_matrix with item_subset tests
# ──────────────────────────────────────────────────────────────────────

def test_pooled_matrix_item_subset_limits_size():
    """When item_subset is provided, the pooled matrix uses only those items."""
    recs_a = [_record_for_model("model-a", [["x", "y", "z"]])]
    recs_b = [_record_for_model("model-b", [["x", "y", "z"]])]
    records_by_model = {"model-a": recs_a, "model-b": recs_b}

    # Request only 2 of the 3 items
    subset = ["x", "y"]
    result = build_pooled_cooccurrence_matrix(records_by_model, item_subset=subset)

    assert result.items == ["x", "y"]
    assert len(result.matrix) == 2
    assert len(result.matrix[0]) == 2


def test_pooled_matrix_item_subset_none_is_full_union():
    """item_subset=None produces the same result as the full union (backward compat)."""
    recs_a = [_record_for_model("model-a", [["x", "y"]])]
    recs_b = [_record_for_model("model-b", [["x", "z"]])]
    records_by_model = {"model-a": recs_a, "model-b": recs_b}

    full = build_pooled_cooccurrence_matrix(records_by_model, item_subset=None)
    # Full union should be ["x", "y", "z"] sorted
    assert sorted(full.items) == ["x", "y", "z"]


def test_pooled_matrix_item_subset_absent_items_are_zero():
    """Items in item_subset absent from a model's matrix still get 0.0 contribution."""
    # model-a has only x,y; model-b has only y,z
    recs_a = [_record_for_model("model-a", [["x", "y"]])]
    recs_b = [_record_for_model("model-b", [["y", "z"]])]
    records_by_model = {"model-a": recs_a, "model-b": recs_b}

    # Subset includes all three items; 'z' is absent from model-a, 'x' absent from model-b
    subset = ["x", "y", "z"]
    result = build_pooled_cooccurrence_matrix(records_by_model, item_subset=subset)

    idx = {item: i for i, item in enumerate(result.items)}
    # x-z co-occurrence: model-a has x but not z (0.0); model-b has z but not x (0.0).
    # Pooled = (0.0 + 0.0) / 2 = 0.0
    assert result.matrix[idx["x"]][idx["z"]] == 0.0
    # y-y diagonal should be 1.0
    assert result.matrix[idx["y"]][idx["y"]] == 1.0
