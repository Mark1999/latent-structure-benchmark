"""Tests for post-F1 SME-review measures: Sutrop CSI, Nolan Index,
Mantel test, cultural centrality, consensus classification.

See docs/SME_REVIEW.md and ARCHITECTURE.md §4.2.
"""

from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
import pytest
from cdb_analyze.consensus import (
    classify_consensus,
    compute_centrality_scores,
)
from cdb_analyze.diff import (
    mantel_test,
    nolan_index,
    pairwise_mantel,
    pairwise_nolan,
)
from cdb_analyze.salience import (
    compute_salience_agreement,
    sutrop_csi,
)
from cdb_core import (
    FreelistRecord,
    InformantRecord,
    InterviewRecord,
    PileSortRecord,
)

# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

def _make_record(items: list[str], run_index: int = 0) -> InformantRecord:
    n = len(items)
    matrix = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    return InformantRecord(
        informant_id=f"test_{run_index}",
        domain_slug="family",
        run_index=run_index,
        collection_date=datetime(2026, 4, 19, tzinfo=UTC),
        model_id="test-model",
        model_version_returned="test-v1",
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
            prompt_verbatim="t", prompt_version="v1", response_verbatim="t",
            response_object_json={}, input_tokens=10, output_tokens=10,
            latency_ms=100, stop_reason="end_turn",
            parsed_items=items, parsed_raw_order=items,
        ),
        pile_sort=PileSortRecord(
            prompt_verbatim="t", prompt_version="v1", response_verbatim="t",
            response_object_json={}, input_tokens=10, output_tokens=10,
            latency_ms=100, stop_reason="end_turn",
            parsed_piles=[items], parsed_matrix=matrix,
        ),
        interview=InterviewRecord(
            prompt_verbatim="t", prompt_version="v1", response_verbatim="t",
            response_object_json={}, input_tokens=10, output_tokens=10,
            latency_ms=100, stop_reason="end_turn",
            parsed_pile_labels=["pile_0"],
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
# Sutrop CSI
# ---------------------------------------------------------------------------

class TestSutropCSI:
    def test_single_run_csi_is_reciprocal_rank(self):
        """With N=1, CSI for item at position k equals 1 / k."""
        records = [_make_record(["a", "b", "c"], 0)]
        out = sutrop_csi(records)
        by_item = {s.item: s for s in out}
        assert by_item["a"].csi == pytest.approx(1.0)          # F=1, N=1, mP=1
        assert by_item["b"].csi == pytest.approx(0.5)          # F=1, N=1, mP=2
        assert by_item["c"].csi == pytest.approx(1 / 3)        # F=1, N=1, mP=3

    def test_frequent_early_items_rank_first(self):
        """Items mentioned often and early get the highest CSI."""
        records = [
            _make_record(["mother", "father", "sister"], 0),
            _make_record(["mother", "father", "cousin"], 1),
            _make_record(["mother", "aunt", "uncle"], 2),
        ]
        out = sutrop_csi(records)
        assert out[0].item == "mother"
        assert out[0].f_mentions == 3
        assert out[0].n_runs == 3

    def test_empty_input(self):
        assert sutrop_csi([]) == []

    def test_output_sorted_descending(self):
        records = [
            _make_record(["a", "b", "c", "d"], 0),
            _make_record(["a", "b", "c", "d"], 1),
        ]
        out = sutrop_csi(records)
        values = [s.csi for s in out]
        assert values == sorted(values, reverse=True)


class TestSalienceAgreement:
    def test_perfect_agreement_returns_one(self):
        smiths = [("a", 1.0), ("b", 0.5), ("c", 0.25)]
        records = [_make_record(["a", "b", "c"])]
        sutrop = sutrop_csi(records)
        assert compute_salience_agreement(smiths, sutrop) == pytest.approx(1.0)

    def test_reversed_ordering_returns_minus_one(self):
        smiths = [("a", 1.0), ("b", 0.5), ("c", 0.25)]
        # Construct a sutrop ranking that reverses the order
        from cdb_core import SutropCSI
        sutrop_reversed = [
            SutropCSI(item="c", csi=1.0, f_mentions=1, n_runs=1, mean_position=1),
            SutropCSI(item="b", csi=0.5, f_mentions=1, n_runs=1, mean_position=2),
            SutropCSI(item="a", csi=0.333, f_mentions=1, n_runs=1, mean_position=3),
        ]
        rho = compute_salience_agreement(smiths, sutrop_reversed)
        assert rho == pytest.approx(-1.0)


# ---------------------------------------------------------------------------
# Nolan Index
# ---------------------------------------------------------------------------

class TestNolanIndex:
    def test_identical_distributions_return_one(self):
        a = {"mother": 10, "father": 5, "sister": 3}
        ni, jac = nolan_index(a, a)
        assert ni == pytest.approx(1.0)
        assert jac == pytest.approx(1.0)

    def test_disjoint_items_low_ni(self):
        a = {"mother": 10}
        b = {"father": 10}
        ni, jac = nolan_index(a, b)
        assert jac == 0.0
        assert ni < 1.0

    def test_same_items_different_weights_detects_emphasis_shift(self):
        """NI catches proportional differences Jaccard does not."""
        a = {"nuclear": 80, "extended": 20}
        b = {"nuclear": 20, "extended": 80}
        ni, jac = nolan_index(a, b)
        assert jac == pytest.approx(1.0)  # same items
        assert ni < 1.0                    # different emphasis

    def test_pairwise_nolan_covers_all_pairs(self):
        items_by_model = {
            "a": {"x": 1, "y": 2},
            "b": {"x": 2, "y": 1},
            "c": {"x": 1, "z": 1},
        }
        pairs = pairwise_nolan(items_by_model)
        assert len(pairs) == 3
        # Results are sorted by (model_a, model_b)
        pairs_tuples = [(p.model_a, p.model_b) for p in pairs]
        assert pairs_tuples == [("a", "b"), ("a", "c"), ("b", "c")]


# ---------------------------------------------------------------------------
# Mantel test
# ---------------------------------------------------------------------------

class TestMantelTest:
    def test_identical_matrices_r_one(self):
        rng = np.random.default_rng(0)
        mat = rng.random((5, 5))
        mat = (mat + mat.T) / 2  # symmetrize
        r, p = mantel_test(mat, mat, n_permutations=99)
        assert r == pytest.approx(1.0)
        assert p < 0.05

    def test_mismatched_shapes_raises(self):
        a = np.zeros((3, 3))
        b = np.zeros((4, 4))
        with pytest.raises(ValueError, match="shapes"):
            mantel_test(a, b)

    def test_pairwise_mantel_symmetry(self):
        rng = np.random.default_rng(1)
        matrices = {
            "a": _random_symmetric(rng, 5),
            "b": _random_symmetric(rng, 5),
            "c": _random_symmetric(rng, 5),
        }
        pairs = pairwise_mantel(matrices, n_permutations=49)
        assert len(pairs) == 3
        for p in pairs:
            assert -1.0 <= p.r <= 1.0
            assert 0.0 <= p.p_value <= 1.0


def _random_symmetric(rng: np.random.Generator, n: int) -> np.ndarray:
    mat = rng.random((n, n))
    mat = (mat + mat.T) / 2
    np.fill_diagonal(mat, 1.0)
    return mat


# ---------------------------------------------------------------------------
# Cultural centrality
# ---------------------------------------------------------------------------

class TestCentralityScores:
    def test_all_identical_gives_uniform_centrality(self):
        """3 models all identical → all centrality scores equal."""
        sim = np.ones((3, 3))
        scores = compute_centrality_scores(["a", "b", "c"], sim)
        assert len(scores) == 3
        values = list(scores.values())
        assert max(values) - min(values) < 1e-9

    def test_outlier_has_distinct_score(self):
        """One model unlike the others should separate in loading magnitude."""
        # Two similar models + one dissimilar
        sim = np.array([
            [1.0, 0.9, 0.1],
            [0.9, 1.0, 0.1],
            [0.1, 0.1, 1.0],
        ])
        scores = compute_centrality_scores(["a", "b", "c"], sim)
        # a and b should have similar loadings; c should be clearly different
        assert abs(scores["a"] - scores["b"]) < abs(scores["a"] - scores["c"])

    def test_single_model_returns_zero(self):
        sim = np.array([[1.0]])
        scores = compute_centrality_scores(["solo"], sim)
        assert scores == {"solo": 0.0}


# ---------------------------------------------------------------------------
# classify_consensus
# ---------------------------------------------------------------------------

class TestClassifyConsensus:
    def test_strong_consensus(self):
        scores = {"a": 0.5, "b": 0.5, "c": 0.5}
        assert classify_consensus(7.0, scores) == "STRONG_CONSENSUS"

    def test_weak_consensus(self):
        scores = {"a": 0.4, "b": 0.3, "c": 0.2}
        assert classify_consensus(4.0, scores) == "WEAK_CONSENSUS"

    def test_subcultural_on_negative_score_with_consensus(self):
        scores = {"a": 0.5, "b": 0.5, "c": -0.2}
        assert classify_consensus(6.0, scores) == "SUBCULTURAL"
        assert classify_consensus(3.5, scores) == "SUBCULTURAL"

    def test_turbulent_below_classic_threshold(self):
        scores = {"a": 0.3, "b": 0.3, "c": 0.3}
        assert classify_consensus(2.0, scores) == "TURBULENT"

    def test_contested_below_classic_with_negative(self):
        scores = {"a": 0.3, "b": -0.3, "c": 0.0}
        assert classify_consensus(1.5, scores) == "CONTESTED"

    def test_deterministic_override(self):
        """Zero-variance overrides the eigenratio table."""
        scores = {"a": 0.5, "b": 0.5}
        assert (
            classify_consensus(7.0, scores, observed_variance=1e-15)
            == "DETERMINISTIC"
        )
