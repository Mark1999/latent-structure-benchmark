"""Tests for the prompt-sensitivity study framework. Synthetic data only."""

from __future__ import annotations

from datetime import UTC, datetime

from cdb_analyze.gates import G1SplitResult, g1_stability_split
from cdb_analyze.sensitivity import (
    compute_between_model_salience_variance,
    compute_between_model_variance,
    compute_within_model_salience_variance,
    compute_within_model_spatial_variance,
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


# ---------------------------------------------------------------------------
# Split G1 — salience variance axis (SME §1.3, un-deferred 2026-04-20)
# ---------------------------------------------------------------------------

class TestSalienceVariance:
    def test_identical_salience_rankings_zero_variance(self):
        """Same item order across variants → Spearman ρ ≈ 1 → zero variance."""
        items = ["mother", "father", "sister", "brother", "uncle", "aunt"]
        piles = [["mother", "father"], ["sister", "brother"], ["uncle", "aunt"]]
        by_variant = {
            "v1": [_make_record("model-a", i, items, piles) for i in range(3)],
            "v2": [_make_record("model-a", i + 3, items, piles) for i in range(3)],
            "v3": [_make_record("model-a", i + 6, items, piles) for i in range(3)],
        }
        assert compute_within_model_salience_variance(by_variant) == 0.0

    def test_reversed_rankings_produce_variance(self):
        """Reversed item order on one variant → rank distance > 0 → variance > 0."""
        items_fwd = ["a", "b", "c", "d", "e", "f"]
        items_rev = list(reversed(items_fwd))
        piles_fwd = [["a", "b"], ["c", "d"], ["e", "f"]]
        piles_rev = [["f", "e"], ["d", "c"], ["b", "a"]]
        by_variant = {
            "v1": [_make_record("model-a", i, items_fwd, piles_fwd) for i in range(3)],
            "v2": [_make_record("model-a", i + 3, items_rev, piles_rev) for i in range(3)],
            "v3": [_make_record("model-a", i + 6, items_fwd, piles_fwd) for i in range(3)],
        }
        var = compute_within_model_salience_variance(by_variant)
        assert var > 0.0

    def test_single_variant_zero_variance(self):
        items = ["a", "b", "c", "d"]
        piles = [["a", "b"], ["c", "d"]]
        by_variant = {"v1": [_make_record("m", 0, items, piles)]}
        assert compute_within_model_salience_variance(by_variant) == 0.0

    def test_between_model_salience_variance_nonneg(self):
        items = ["a", "b", "c", "d"]
        by_model = {
            "m1": [_make_record("m1", i, items, [["a", "b"], ["c", "d"]]) for i in range(3)],
            "m2": [_make_record("m2", i, items, [["a", "c"], ["b", "d"]]) for i in range(3)],
        }
        var = compute_between_model_salience_variance(by_model)
        assert var >= 0.0


class TestSpatialAliases:
    def test_spatial_matches_legacy_alias(self):
        """compute_within_model_variance is an alias for the spatial axis."""
        items = ["a", "b", "c", "d"]
        by_variant = {
            "v1": [_make_record("m", i, items, [["a", "b"], ["c", "d"]]) for i in range(3)],
            "v2": [_make_record("m", i + 3, items, [["a", "c"], ["b", "d"]]) for i in range(3)],
        }
        assert (
            compute_within_model_variance(by_variant)
            == compute_within_model_spatial_variance(by_variant)
        )


# ---------------------------------------------------------------------------
# Split G1 gate
# ---------------------------------------------------------------------------

class TestG1StabilitySplit:
    def test_both_axes_pass_overall_pass(self):
        result = g1_stability_split(
            within_salience_variance=0.01, between_salience_variance=0.10,
            within_spatial_variance=0.02, between_spatial_variance=0.10,
        )
        assert isinstance(result, G1SplitResult)
        assert result.salience_pass is True
        assert result.spatial_pass is True
        assert result.g1_pass is True
        assert result.threshold == 0.5

    def test_salience_fails_overall_fails(self):
        """Even if spatial passes, a failing salience axis fails the overall gate."""
        result = g1_stability_split(
            within_salience_variance=0.08, between_salience_variance=0.10,  # 0.8 > 0.5
            within_spatial_variance=0.02, between_spatial_variance=0.10,
        )
        assert result.salience_pass is False
        assert result.spatial_pass is True
        assert result.g1_pass is False

    def test_spatial_fails_overall_fails(self):
        """Even if salience passes, a failing spatial axis fails the overall gate."""
        result = g1_stability_split(
            within_salience_variance=0.02, between_salience_variance=0.10,
            within_spatial_variance=0.08, between_spatial_variance=0.10,
        )
        assert result.salience_pass is True
        assert result.spatial_pass is False
        assert result.g1_pass is False

    def test_both_axes_fail(self):
        result = g1_stability_split(
            within_salience_variance=0.08, between_salience_variance=0.10,
            within_spatial_variance=0.08, between_spatial_variance=0.10,
        )
        assert result.salience_pass is False
        assert result.spatial_pass is False
        assert result.g1_pass is False

    def test_zero_between_variance_infinite_ratio(self):
        """Zero between-variance on either axis → infinite ratio → fail."""
        result = g1_stability_split(
            within_salience_variance=0.01, between_salience_variance=0.0,  # inf
            within_spatial_variance=0.02, between_spatial_variance=0.10,
        )
        assert result.salience_stability == float("inf")
        assert result.salience_pass is False
        assert result.g1_pass is False

    def test_aggregate_is_mean_of_ratios(self):
        result = g1_stability_split(
            within_salience_variance=0.02, between_salience_variance=0.10,  # 0.2
            within_spatial_variance=0.04, between_spatial_variance=0.10,   # 0.4
        )
        # Mean of 0.2 and 0.4 = 0.3
        assert result.aggregate_stability == 0.3
