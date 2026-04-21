"""Tests for F2-T05: split G1 (salience × spatial) wired into run_pipeline.

Verifies that:
- multi-prompt-variant record sets populate all six g1_* fields on DomainResult
- single-prompt-version input leaves all six fields None (no exception)
- g1_overall_pass is the conjunction of g1_salience_pass AND g1_spatial_pass
- threshold of 0.5 is binding (pass/fail flips correctly at boundary)
- g1_aggregate_stability == (g1_salience_stability + g1_spatial_stability) / 2
- group_by_prompt_version groups correctly by freelist.prompt_version

No real API calls — all synthetic InformantRecord fixtures.
"""

from __future__ import annotations

import math
from datetime import UTC, datetime

import pytest
from cdb_analyze.pipeline import group_by_prompt_version, run_pipeline
from cdb_core import (
    FreelistRecord,
    InformantRecord,
    InterviewRecord,
    PileSortRecord,
)

# ---------------------------------------------------------------------------
# Fixture builder
# ---------------------------------------------------------------------------

def _make_record(
    model_id: str,
    run_index: int,
    items: list[str],
    piles: list[list[str]],
    *,
    prompt_version: str = "v1",
) -> InformantRecord:
    """Build a minimal InformantRecord for testing.

    prompt_version is set on freelist.prompt_version (the sensitivity
    variant key that group_by_prompt_version reads).
    """
    n = len(items)
    matrix = [[0] * n for _ in range(n)]
    idx = {item: i for i, item in enumerate(items)}
    for pile in piles:
        for a in pile:
            for b in pile:
                matrix[idx[a]][idx[b]] = 1

    return InformantRecord(
        informant_id=f"{model_id}_{run_index}_{prompt_version}",
        domain_slug="family",
        run_index=run_index,
        collection_date=datetime(2026, 4, 20, tzinfo=UTC),
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
            prompt_version=prompt_version,
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
            prompt_version=prompt_version,
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
            prompt_version=prompt_version,
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


# ---------------------------------------------------------------------------
# Multi-variant fixture
#
# Mirrors the shakedown sensitivity cell structure:
# - model-a (sensitivity model): n_variants prompt versions, n_runs per variant
# - model-b (non-sensitivity model): single "v1" prompt version, n_runs runs
#
# This matches the shakedown where claude-sonnet-4-6 has v1_s1..v1_s8 but
# other models only have v1. build_cooccurrence_matrix requires all records
# per batch to belong to the same model.
# ---------------------------------------------------------------------------

_ITEMS_A = ["mother", "father", "sister", "brother", "uncle", "aunt"]
_PILES_A = [["mother", "father"], ["sister", "brother"], ["uncle", "aunt"]]

_ITEMS_B = ["mother", "father", "sister", "brother", "uncle", "aunt"]
_PILES_B = [["mother", "sister", "aunt"], ["father", "brother", "uncle"]]


def _multi_variant_records(n_variants: int = 3, n_runs: int = 3) -> list[InformantRecord]:
    """model-a: n_variants × n_runs; model-b: single variant × n_runs."""
    records: list[InformantRecord] = []
    # Sensitivity model: records for each prompt variant
    for v in range(1, n_variants + 1):
        pv = f"v1_s{v}"
        for r in range(n_runs):
            records.append(
                _make_record(
                    "model-a", r + (v - 1) * n_runs, _ITEMS_A, _PILES_A,
                    prompt_version=pv,
                )
            )
    # Non-sensitivity model: only the standard prompt version
    for r in range(n_runs):
        records.append(_make_record("model-b", r, _ITEMS_B, _PILES_B, prompt_version="v1"))
    return records


# ---------------------------------------------------------------------------
# group_by_prompt_version unit tests
# ---------------------------------------------------------------------------

class TestGroupByPromptVersion:
    def test_groups_by_freelist_prompt_version(self):
        records = [
            _make_record("m", 0, _ITEMS_A, _PILES_A, prompt_version="v1_s1"),
            _make_record("m", 1, _ITEMS_A, _PILES_A, prompt_version="v1_s2"),
            _make_record("m", 2, _ITEMS_A, _PILES_A, prompt_version="v1_s1"),
        ]
        groups = group_by_prompt_version(records)
        assert set(groups.keys()) == {"v1_s1", "v1_s2"}
        assert len(groups["v1_s1"]) == 2
        assert len(groups["v1_s2"]) == 1

    def test_single_version_one_key(self):
        records = [
            _make_record("m", i, _ITEMS_A, _PILES_A, prompt_version="v1")
            for i in range(3)
        ]
        groups = group_by_prompt_version(records)
        assert list(groups.keys()) == ["v1"]
        assert len(groups["v1"]) == 3


# ---------------------------------------------------------------------------
# T1 — multi-variant → all six fields non-None
# ---------------------------------------------------------------------------

class TestG1SplitPopulatedForMultiVariant:
    def test_g1_split_populated_for_multi_variant_fixture(self):
        """>=2 prompt_versions → all six g1_* fields non-None on DomainResult."""
        records = _multi_variant_records(n_variants=3, n_runs=3)
        result = run_pipeline(records, analysis_version="test", n_bootstrap=5)

        assert result.g1_salience_stability is not None, "g1_salience_stability should be set"
        assert result.g1_spatial_stability is not None, "g1_spatial_stability should be set"
        assert result.g1_aggregate_stability is not None, "g1_aggregate_stability should be set"
        assert result.g1_salience_pass is not None, "g1_salience_pass should be set"
        assert result.g1_spatial_pass is not None, "g1_spatial_pass should be set"
        assert result.g1_overall_pass is not None, "g1_overall_pass should be set"

    def test_g1_split_uses_8_variant_fixture(self):
        """8 prompt variants mirrors the shakedown sensitivity cell (40 records per model)."""
        records = _multi_variant_records(n_variants=8, n_runs=5)
        result = run_pipeline(records, analysis_version="test", n_bootstrap=5)

        assert result.g1_salience_stability is not None
        assert result.g1_spatial_stability is not None
        assert result.g1_overall_pass is not None
        # Values must be non-negative floats
        assert result.g1_salience_stability >= 0.0
        assert result.g1_spatial_stability >= 0.0


# ---------------------------------------------------------------------------
# T2 — single-variant → all six fields None, no exception
# ---------------------------------------------------------------------------

class TestG1SplitNoneForSingleVariant:
    def test_g1_split_none_for_single_variant(self):
        """Single prompt_version → all six g1_* fields remain None."""
        records = []
        for r in range(3):
            records.append(_make_record("model-a", r, _ITEMS_A, _PILES_A, prompt_version="v1"))
            records.append(_make_record("model-b", r, _ITEMS_B, _PILES_B, prompt_version="v1"))

        result = run_pipeline(records, analysis_version="test", n_bootstrap=5)

        assert result.g1_salience_stability is None
        assert result.g1_spatial_stability is None
        assert result.g1_aggregate_stability is None
        assert result.g1_salience_pass is None
        assert result.g1_spatial_pass is None
        assert result.g1_overall_pass is None


# ---------------------------------------------------------------------------
# T3 — g1_overall_pass is the conjunction of salience_pass AND spatial_pass
# ---------------------------------------------------------------------------

class TestG1OverallPassIsConjunction:
    """Test via g1_stability_split directly (cleaner than forcing specific
    pipeline variance values). The pipeline wires the conjunction exactly
    the same way as the gate function — testing the gate function isolates
    the conjunction logic without needing engineered variance inputs.
    """

    def test_both_pass_overall_true(self):
        from cdb_analyze.gates import g1_stability_split
        result = g1_stability_split(
            within_salience_variance=0.02, between_salience_variance=0.10,
            within_spatial_variance=0.02, between_spatial_variance=0.10,
            threshold=0.5,
        )
        assert result.salience_pass is True
        assert result.spatial_pass is True
        assert result.g1_pass is True

    def test_salience_fail_spatial_pass_overall_false(self):
        from cdb_analyze.gates import g1_stability_split
        result = g1_stability_split(
            within_salience_variance=0.08, between_salience_variance=0.10,  # 0.80 > 0.5
            within_spatial_variance=0.02, between_spatial_variance=0.10,   # 0.20 < 0.5
            threshold=0.5,
        )
        assert result.salience_pass is False
        assert result.spatial_pass is True
        assert result.g1_pass is False

    def test_salience_pass_spatial_fail_overall_false(self):
        from cdb_analyze.gates import g1_stability_split
        result = g1_stability_split(
            within_salience_variance=0.02, between_salience_variance=0.10,   # 0.20 < 0.5
            within_spatial_variance=0.08, between_spatial_variance=0.10,    # 0.80 > 0.5
            threshold=0.5,
        )
        assert result.salience_pass is True
        assert result.spatial_pass is False
        assert result.g1_pass is False


# ---------------------------------------------------------------------------
# T4 — threshold is binding at 0.5 (pass flips at boundary)
# ---------------------------------------------------------------------------

class TestG1ThresholdBindingAt0_5:
    def test_ratio_just_below_0_5_passes(self):
        from cdb_analyze.gates import g1_stability_split
        # ratio = 0.499 / 1.0 = 0.499 < 0.5 → pass
        result = g1_stability_split(
            within_salience_variance=0.499, between_salience_variance=1.0,
            within_spatial_variance=0.499, between_spatial_variance=1.0,
            threshold=0.5,
        )
        assert result.salience_pass is True
        assert result.spatial_pass is True
        assert result.g1_pass is True

    def test_ratio_exactly_0_5_fails(self):
        from cdb_analyze.gates import g1_stability_split
        # ratio = 0.5 / 1.0 = 0.5 — not strictly less than threshold
        result = g1_stability_split(
            within_salience_variance=0.5, between_salience_variance=1.0,
            within_spatial_variance=0.5, between_spatial_variance=1.0,
            threshold=0.5,
        )
        # The gate is ratio < threshold (strict), so 0.5 < 0.5 is False
        assert result.salience_pass is False
        assert result.spatial_pass is False
        assert result.g1_pass is False

    def test_ratio_just_above_0_5_fails(self):
        from cdb_analyze.gates import g1_stability_split
        result = g1_stability_split(
            within_salience_variance=0.501, between_salience_variance=1.0,
            within_spatial_variance=0.501, between_spatial_variance=1.0,
            threshold=0.5,
        )
        assert result.salience_pass is False
        assert result.spatial_pass is False
        assert result.g1_pass is False


# ---------------------------------------------------------------------------
# T5 — g1_aggregate_stability == mean of the two axes
# ---------------------------------------------------------------------------

class TestG1AggregateIsMeanOfAxes:
    def test_aggregate_is_mean_within_float_tolerance(self):
        from cdb_analyze.gates import g1_stability_split
        # salience ratio = 0.2 / 1.0 = 0.2; spatial ratio = 0.4 / 1.0 = 0.4
        result = g1_stability_split(
            within_salience_variance=0.2, between_salience_variance=1.0,
            within_spatial_variance=0.4, between_spatial_variance=1.0,
            threshold=0.5,
        )
        expected = (result.salience_stability + result.spatial_stability) / 2
        assert result.aggregate_stability is not None
        assert math.isclose(result.aggregate_stability, expected, rel_tol=1e-9)

    def test_pipeline_aggregate_is_mean_of_axes(self):
        """On the pipeline's DomainResult, aggregate = mean of salience + spatial."""
        records = _multi_variant_records(n_variants=3, n_runs=3)
        result = run_pipeline(records, analysis_version="test", n_bootstrap=5)

        if result.g1_aggregate_stability is None:
            pytest.skip("G1 not computed for this fixture")

        assert result.g1_salience_stability is not None
        assert result.g1_spatial_stability is not None
        expected = (result.g1_salience_stability + result.g1_spatial_stability) / 2.0
        assert math.isclose(result.g1_aggregate_stability, expected, rel_tol=1e-9), (
            f"aggregate={result.g1_aggregate_stability!r} but mean of axes={expected!r}"
        )
