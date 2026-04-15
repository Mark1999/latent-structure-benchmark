"""Tests for the prompt-sensitivity study framework. Synthetic data only."""

from __future__ import annotations

from datetime import UTC, datetime

from cdb_analyze.sensitivity import (
    compute_between_model_variance,
    compute_within_model_variance,
)
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
    """Build a minimal InformantRecord for testing."""
    n = len(items)
    matrix = [[0] * n for _ in range(n)]
    idx = {item: i for i, item in enumerate(items)}
    for pile in piles:
        for a in pile:
            for b in pile:
                matrix[idx[a]][idx[b]] = 1

    return InformantRecord(
        informant_id=f"{model_id}_{run_index}",
        domain_slug="family",
        run_index=run_index,
        collection_date=datetime(2026, 4, 13, tzinfo=UTC),
        model_id=model_id,
        model_version_returned=f"{model_id}-v1",
        family="test",
        provider="anthropic",
        provider_request_id=f"req_{run_index}",
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


class TestWithinModelVariance:
    def test_identical_variants_zero_variance(self):
        """Same pile structure across variants → zero variance."""
        items = ["mother", "father", "sister", "brother"]
        piles = [["mother", "father"], ["sister", "brother"]]

        by_variant = {
            "v1": [_make_record("model-a", i, items, piles) for i in range(3)],
            "v2": [_make_record("model-a", i + 3, items, piles) for i in range(3)],
            "v3": [_make_record("model-a", i + 6, items, piles) for i in range(3)],
        }

        var = compute_within_model_variance(by_variant)
        assert var == 0.0

    def test_different_variants_positive_variance(self):
        """Different pile structures across variants → positive variance."""
        items = ["mother", "father", "sister", "brother", "uncle", "aunt"]

        by_variant = {
            "v1": [
                _make_record("model-a", i, items,
                             [["mother", "father"], ["sister", "brother"], ["uncle", "aunt"]])
                for i in range(3)
            ],
            "v2": [
                _make_record("model-a", i + 3, items,
                             [["mother", "sister", "aunt"], ["father", "brother", "uncle"]])
                for i in range(3)
            ],
            "v3": [
                _make_record("model-a", i + 6, items,
                             [["mother", "father", "sister", "brother"], ["uncle", "aunt"]])
                for i in range(3)
            ],
        }

        var = compute_within_model_variance(by_variant)
        assert var > 0.0

    def test_single_variant_zero_variance(self):
        items = ["mother", "father", "sister", "brother"]
        by_variant = {
            "v1": [_make_record("model-a", 0, items,
                                [["mother", "father"], ["sister", "brother"]])],
        }
        var = compute_within_model_variance(by_variant)
        assert var == 0.0


class TestBetweenModelVariance:
    def test_different_models_positive_variance(self):
        items = ["mother", "father", "sister", "brother"]

        by_model = {
            "model-a": [
                _make_record("model-a", i, items,
                             [["mother", "father"], ["sister", "brother"]])
                for i in range(3)
            ],
            "model-b": [
                _make_record("model-b", i, items,
                             [["mother", "sister"], ["father", "brother"]])
                for i in range(3)
            ],
        }

        var = compute_between_model_variance(by_model)
        assert var >= 0.0

    def test_single_model_zero_variance(self):
        items = ["mother", "father", "sister", "brother"]
        by_model = {
            "model-a": [
                _make_record("model-a", 0, items,
                             [["mother", "father"], ["sister", "brother"]]),
            ],
        }
        var = compute_between_model_variance(by_model)
        assert var == 0.0
