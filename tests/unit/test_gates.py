"""Tests for Phase 4 validation gates (G1, G2, G3). Uses synthetic data only."""

from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
import pytest
from cdb_analyze.gates import (
    g1_stability,
    g2_signal,
    g3_replication,
    rand_index,
)
from cdb_core import (
    FreelistRecord,
    InformantRecord,
    InterviewRecord,
    PileSortRecord,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def _make_distinct_models() -> dict[str, list[InformantRecord]]:
    """3 models with clearly different pile structures, 4 runs each."""
    items = ["mother", "father", "sister", "brother", "uncle", "aunt"]

    records: dict[str, list[InformantRecord]] = {}

    # Model A: groups by generation (parents, siblings, extended)
    records["model-a"] = [
        _make_record("model-a", i, items,
                     [["mother", "father"], ["sister", "brother"], ["uncle", "aunt"]])
        for i in range(4)
    ]
    # Model B: groups by gender
    records["model-b"] = [
        _make_record("model-b", i, items,
                     [["mother", "sister", "aunt"], ["father", "brother", "uncle"]])
        for i in range(4)
    ]
    # Model C: groups by nuclear vs extended
    records["model-c"] = [
        _make_record("model-c", i, items,
                     [["mother", "father", "sister", "brother"], ["uncle", "aunt"]])
        for i in range(4)
    ]
    return records


# ---------------------------------------------------------------------------
# Rand index
# ---------------------------------------------------------------------------

class TestRandIndex:
    def test_identical_labels(self):
        assert rand_index([1, 1, 2, 2], [1, 1, 2, 2]) == 1.0

    def test_opposite_labels(self):
        # All pairs disagree
        ri = rand_index([1, 1, 2, 2], [1, 2, 1, 2])
        assert ri < 1.0

    def test_single_element(self):
        assert rand_index([1], [2]) == 1.0

    def test_mismatched_lengths(self):
        with pytest.raises(ValueError, match="same length"):
            rand_index([1, 2], [1, 2, 3])

    def test_perfect_agreement_different_label_ids(self):
        # Same partition, different label integers
        assert rand_index([1, 1, 2, 2], [5, 5, 9, 9]) == 1.0


# ---------------------------------------------------------------------------
# G1 — Stability
# ---------------------------------------------------------------------------

class TestG1Stability:
    def test_low_ratio_passes(self):
        result = g1_stability(within_variance=0.01, between_variance=0.10)
        assert result.passed is True
        assert result.value == 0.1

    def test_high_ratio_fails(self):
        result = g1_stability(within_variance=0.08, between_variance=0.10)
        assert result.passed is False
        assert result.value == 0.8

    def test_zero_between_variance_fails(self):
        result = g1_stability(within_variance=0.01, between_variance=0.0)
        assert result.passed is False

    def test_exact_threshold_fails(self):
        # ratio == 0.5 should fail (criterion is strict <, not <=)
        result = g1_stability(within_variance=0.05, between_variance=0.10)
        assert result.passed is False


# ---------------------------------------------------------------------------
# G2 — Signal
# ---------------------------------------------------------------------------

class TestG2Signal:
    def test_structured_signal_passes(self):
        """Strongly structured vectors should be distinguishable from random."""
        rng = np.random.default_rng(42)
        n_pairs = 45  # 10 items, upper triangle

        # Model A: correlated pattern
        base = rng.random(n_pairs)
        vectors = [
            ("model-a", base + rng.normal(0, 0.05, n_pairs)),
            ("model-b", base + rng.normal(0, 0.05, n_pairs)),
            ("model-c", 1.0 - base + rng.normal(0, 0.05, n_pairs)),
        ]
        # Clip to valid range
        vectors = [(mid, np.clip(v, 0, 1)) for mid, v in vectors]

        result = g2_signal(vectors, n_perm=999)
        assert result.gate == "G2"
        assert result.passed is True
        assert result.value < 0.01

    def test_random_vectors_fail(self):
        """Purely random vectors should not be distinguishable."""
        rng = np.random.default_rng(99)
        n_pairs = 45
        vectors = [
            (f"model-{i}", rng.random(n_pairs))
            for i in range(4)
        ]

        result = g2_signal(vectors, n_perm=999)
        assert result.gate == "G2"
        assert result.passed is False
        assert result.value > 0.01

    def test_single_model_fails(self):
        result = g2_signal([("a", np.array([1.0, 0.5, 0.3]))])
        assert result.passed is False


# ---------------------------------------------------------------------------
# G3 — Replication
# ---------------------------------------------------------------------------

class TestG3Replication:
    def test_consistent_models_pass(self):
        """Models with stable pile structures should replicate."""
        records = _make_distinct_models()
        result = g3_replication(records, n_trials=50)
        assert result.gate == "G3"
        assert result.passed is True
        assert result.value >= 0.7

    def test_single_model_fails(self):
        items = ["mother", "father", "sister", "brother"]
        records = {
            "model-a": [
                _make_record("model-a", i, items,
                             [["mother", "father"], ["sister", "brother"]])
                for i in range(4)
            ],
        }
        result = g3_replication(records, n_trials=10)
        assert result.passed is False

    def test_single_run_per_model_fails(self):
        """Split-half requires ≥2 runs per model."""
        items = ["mother", "father", "sister", "brother"]
        records = {
            "model-a": [
                _make_record("model-a", 0, items,
                             [["mother", "father"], ["sister", "brother"]]),
            ],
            "model-b": [
                _make_record("model-b", 0, items,
                             [["mother", "sister"], ["father", "brother"]]),
            ],
        }
        result = g3_replication(records, n_trials=10)
        assert result.passed is False
        assert "minimum is 1" in result.detail
