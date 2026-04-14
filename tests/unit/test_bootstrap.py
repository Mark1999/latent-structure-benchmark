"""Tests for bootstrap uncertainty module."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from cdb_analyze.bootstrap import bootstrap_mds_ellipses
from cdb_core import (
    FreelistRecord,
    InformantRecord,
    InterviewRecord,
    PileSortRecord,
)


def _make_record(
    model_id: str,
    run_index: int,
    items: list[str],
    piles: list[list[str]],
) -> InformantRecord:
    """Build a minimal InformantRecord for bootstrap testing."""
    n = len(items)
    matrix = [[0] * n for _ in range(n)]
    item_idx = {item: i for i, item in enumerate(items)}
    for pile in piles:
        for a in pile:
            for b in pile:
                matrix[item_idx[a]][item_idx[b]] = 1

    return InformantRecord(
        informant_id=f"{model_id}_{run_index}",
        domain_slug="family",
        run_index=run_index,
        collection_date=datetime(2026, 4, 13, tzinfo=UTC),
        model_id=model_id,
        model_version_returned=f"{model_id}-v1",
        family="test",
        provider="anthropic",
        provider_request_id=f"req_{model_id}_{run_index}",
        knowledge_cutoff=None,
        open_weights=False,
        origin_country="us",
        alignment_method=None,
        collection_method="anthropic_api",
        api_endpoint="https://api.anthropic.com/v1/messages",
        api_version="2023-06-01",
        temperature=0.7,
        top_p=None,
        max_tokens=16384,
        system_prompt="test",
        freelist=FreelistRecord(
            prompt_verbatim="test",
            prompt_version="v1",
            response_verbatim="test",
            response_object_json={},
            input_tokens=50,
            output_tokens=20,
            latency_ms=1000,
            stop_reason="end_turn",
            parsed_items=items,
            parsed_raw_order=items,
        ),
        pile_sort=PileSortRecord(
            prompt_verbatim="test",
            prompt_version="v1",
            response_verbatim="test",
            response_object_json={},
            input_tokens=80,
            output_tokens=40,
            latency_ms=2000,
            stop_reason="end_turn",
            parsed_piles=piles,
            parsed_matrix=matrix,
        ),
        interview=InterviewRecord(
            prompt_verbatim="test",
            prompt_version="v1",
            response_verbatim="test",
            response_object_json={},
            input_tokens=60,
            output_tokens=10,
            latency_ms=800,
            stop_reason="end_turn",
            parsed_pile_labels=[f"pile_{i}" for i in range(len(piles))],
        ),
        sha256_manifest={
            "freelist_prompt": "a", "freelist_response": "b",
            "pilesort_prompt": "c", "pilesort_response": "d",
            "interview_prompt": "e", "interview_response": "f",
            "request_params": "g", "informant_record_total": "h",
        },
        qa_passed=True,
    )


def test_bootstrap_returns_coordinates_and_ellipses():
    """Bootstrap should return coords and ellipses for each model."""
    items = ["mother", "father", "sister", "brother"]

    records_a = [
        _make_record("model-a", i, items, [["mother", "father"], ["sister", "brother"]])
        for i in range(5)
    ]
    records_b = [
        _make_record("model-b", i, items, [["mother", "sister"], ["father", "brother"]])
        for i in range(5)
    ]

    coords, ellipses, sim, sim_ci = bootstrap_mds_ellipses(
        {"model-a": records_a, "model-b": records_b},
        n_bootstrap=20,  # Small for test speed
    )

    assert "model-a" in coords
    assert "model-b" in coords
    assert len(coords["model-a"]) == 2
    assert "model-a" in ellipses
    assert "model-b" in ellipses
    assert ellipses["model-a"].n_bootstrap == 20
    assert sim.shape == (2, 2)
    assert sim_ci.shape == (2, 2, 2)


def test_bootstrap_too_few_models():
    items = ["a", "b", "c"]
    records = [_make_record("model-a", 0, items, [["a", "b", "c"]])]

    with pytest.raises(ValueError, match="at least 2"):
        bootstrap_mds_ellipses({"model-a": records}, n_bootstrap=10)


def test_bootstrap_ellipse_has_positive_axes():
    """Ellipse semi-axes should be non-negative."""
    items = ["mother", "father", "sister", "brother"]

    records_a = [
        _make_record("model-a", i, items, [["mother", "father"], ["sister", "brother"]])
        for i in range(5)
    ]
    records_b = [
        _make_record("model-b", i, items, [["mother", "sister"], ["father", "brother"]])
        for i in range(5)
    ]

    _, ellipses, _, _ = bootstrap_mds_ellipses(
        {"model-a": records_a, "model-b": records_b},
        n_bootstrap=20,
    )

    for e in ellipses.values():
        assert e.semi_major >= 0
        assert e.semi_minor >= 0
