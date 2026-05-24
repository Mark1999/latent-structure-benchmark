"""Unit tests for Phase 9a T1/T2/T3:
- build_pooled_cooccurrence_matrix() (cooccurrence.py)
- cluster_terms() (cluster.py)
- Pipeline integration: DomainResult term-level fields populated

Uses synthetic InformantRecords — no real API calls. All fixtures are
in-memory per tests/fixtures/README.md convention.

CDA SME rulings applied:
- M1: equal-weight-per-model, denominator always M, absence = 0.0
- M2: average linkage (UPGMA)
- M3: distance = 1 - cooccurrence
- F3: per-model item MDS is Register 1 (mds_within_model populated)
"""

from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
import pytest
from cdb_analyze.cluster import cluster_terms
from cdb_analyze.cooccurrence import (
    build_cooccurrence_matrix,
    build_pooled_cooccurrence_matrix,
)
from cdb_analyze.pipeline import run_pipeline
from cdb_core import (
    CooccurrenceMatrix,
    FreelistRecord,
    InformantRecord,
    InterviewRecord,
    ModelRef,
    PileSortRecord,
)
from scipy.cluster.hierarchy import linkage as scipy_linkage
from scipy.spatial.distance import squareform

# ---------------------------------------------------------------------------
# Shared test fixture helpers
# ---------------------------------------------------------------------------

def _make_record(
    model_id: str,
    run_index: int,
    items: list[str],
    piles: list[list[str]],
    domain_slug: str = "family",
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
        domain_slug=domain_slug,
        run_index=run_index,
        collection_date=datetime(2026, 5, 24, tzinfo=UTC),
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
        temperature=0.3,
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


def _make_cooccurrence_matrix(
    items: list[str],
    matrix: list[list[float]],
    model_id: str = "test-model",
) -> CooccurrenceMatrix:
    """Build a CooccurrenceMatrix directly (no records needed)."""
    model_ref = ModelRef(
        provider="anthropic",
        model_id=model_id,
        family="test",
        origin="us",
        open_weights=False,
        collection_method="anthropic_api",
        quantization=None,
        release_date=datetime(2026, 5, 24).date(),
        version_label="v1",
    )
    return CooccurrenceMatrix(
        domain_slug="family",
        model=model_ref,
        items=items,
        matrix=matrix,
    )


# ---------------------------------------------------------------------------
# T1: build_pooled_cooccurrence_matrix
# ---------------------------------------------------------------------------

class TestBuildPooledCooccurrenceMatrix:
    """Tests for CDA SME M1 pooling algorithm."""

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="No records provided"):
            build_pooled_cooccurrence_matrix({})

    def test_single_model_equals_per_model_matrix(self):
        """With one model, pooled == per-model (trivial case)."""
        items = ["mother", "father", "sister", "brother"]
        records = [
            _make_record("model-a", i, items, [["mother", "father"], ["sister", "brother"]])
            for i in range(3)
        ]
        records_by_model = {"model-a": records}

        per_model = build_cooccurrence_matrix(records)
        pooled = build_pooled_cooccurrence_matrix(records_by_model)

        assert pooled.items == per_model.items
        for i in range(len(per_model.items)):
            for j in range(len(per_model.items)):
                assert abs(pooled.matrix[i][j] - per_model.matrix[i][j]) < 1e-10, (
                    f"Mismatch at ({i},{j}): pooled={pooled.matrix[i][j]}, "
                    f"per_model={per_model.matrix[i][j]}"
                )

    def test_two_models_equal_weight_m1(self):
        """CDA SME M1: pooled = mean of per-model matrices, denominator always M.

        Two models with opposite pile structures. Expected pooled value
        for any off-diagonal pair = (1.0 + 0.0) / 2 = 0.5 for items that
        co-occur in model-a but not model-b, and (0.0 + 1.0) / 2 = 0.5
        for items that co-occur in model-b but not model-a.
        """
        items = ["mother", "father", "sister", "brother"]
        # model-a: parents together, siblings together
        recs_a = [
            _make_record("model-a", i, items, [["mother", "father"], ["sister", "brother"]])
            for i in range(3)
        ]
        # model-b: females together, males together
        recs_b = [
            _make_record("model-b", i, items, [["mother", "sister"], ["father", "brother"]])
            for i in range(3)
        ]
        records_by_model = {"model-a": recs_a, "model-b": recs_b}

        pooled = build_pooled_cooccurrence_matrix(records_by_model)

        assert pooled.items == sorted(items)

        item_idx = {item: i for i, item in enumerate(pooled.items)}
        i_mother = item_idx["mother"]
        i_father = item_idx["father"]
        i_sister = item_idx["sister"]
        i_brother = item_idx["brother"]

        # mother + father: co-occur in model-a (=1.0), not in model-b (=0.0) → 0.5
        assert abs(pooled.matrix[i_mother][i_father] - 0.5) < 1e-10
        # mother + sister: not in model-a (=0.0), co-occur in model-b (=1.0) → 0.5
        assert abs(pooled.matrix[i_mother][i_sister] - 0.5) < 1e-10
        # mother + brother: not in either → 0.0
        assert abs(pooled.matrix[i_mother][i_brother] - 0.0) < 1e-10
        # sister + brother: co-occur in model-a (=1.0), not in model-b (=0.0) → 0.5
        assert abs(pooled.matrix[i_sister][i_brother] - 0.5) < 1e-10
        # Diagonal = 1.0
        assert abs(pooled.matrix[i_mother][i_mother] - 1.0) < 1e-10

    def test_absence_item_in_one_model_is_zero_m1(self):
        """CDA SME M1 F1: item absent from a model contributes 0.0, not NaN.

        model-a has 4 items; model-b has 3 items (missing "uncle").
        The pooled value for any pair involving "uncle" should be:
          model-a's co-occurrence / 2   (model-b contributes 0.0, not excluded)
        """
        items_a = ["mother", "father", "sister", "uncle"]
        items_b = ["mother", "father", "sister"]

        recs_a = [
            _make_record(
                "model-a", i, items_a,
                [["mother", "father"], ["sister", "uncle"]],
            )
            for i in range(3)
        ]
        recs_b = [
            _make_record(
                "model-b", i, items_b,
                [["mother", "father"], ["sister"]],
            )
            for i in range(3)
        ]
        records_by_model = {"model-a": recs_a, "model-b": recs_b}

        pooled = build_pooled_cooccurrence_matrix(records_by_model)

        # Union item set includes "uncle"
        assert "uncle" in pooled.items

        item_idx = {item: i for i, item in enumerate(pooled.items)}
        i_uncle = item_idx["uncle"]
        i_sister = item_idx["sister"]
        i_mother = item_idx["mother"]

        # model-a: sister + uncle co-occur (=1.0); model-b: absent (=0.0)
        # denominator = 2 (both models), not 1 (only models that produced uncle)
        expected_sister_uncle = 1.0 / 2
        assert abs(pooled.matrix[i_sister][i_uncle] - expected_sister_uncle) < 1e-10, (
            f"Expected {expected_sister_uncle}, got {pooled.matrix[i_sister][i_uncle]}"
        )

        # mother + uncle: model-a puts them in different piles (=0.0); model-b absent
        # → 0.0 / 2 = 0.0
        assert abs(pooled.matrix[i_mother][i_uncle] - 0.0) < 1e-10

    def test_union_item_set_is_sorted(self):
        """Item set is the union of all models' items, sorted deterministically."""
        recs_a = [_make_record("model-a", 0, ["c", "a"], [["c", "a"]])]
        recs_b = [_make_record("model-b", 0, ["b", "a"], [["b", "a"]])]
        records_by_model = {"model-a": recs_a, "model-b": recs_b}

        pooled = build_pooled_cooccurrence_matrix(records_by_model)

        assert pooled.items == sorted(["a", "b", "c"])

    def test_pooled_matrix_is_symmetric(self):
        """Pooled matrix must be symmetric (by construction from symmetric inputs)."""
        items = ["alpha", "beta", "gamma", "delta"]
        recs_a = [_make_record("model-a", 0, items, [["alpha", "beta"], ["gamma", "delta"]])]
        recs_b = [_make_record("model-b", 0, items, [["alpha", "gamma"], ["beta", "delta"]])]
        records_by_model = {"model-a": recs_a, "model-b": recs_b}

        pooled = build_pooled_cooccurrence_matrix(records_by_model)
        m = pooled.matrix
        n = len(m)
        for i in range(n):
            for j in range(n):
                assert abs(m[i][j] - m[j][i]) < 1e-12, (
                    f"Asymmetry at ({i},{j}): {m[i][j]} vs {m[j][i]}"
                )

    def test_pooled_matrix_diagonal_is_one(self):
        """Diagonal of pooled matrix must be 1.0."""
        items = ["mother", "father", "sister"]
        recs_a = [_make_record("model-a", 0, items, [["mother", "father"], ["sister"]])]
        recs_b = [_make_record("model-b", 0, items, [["mother"], ["father", "sister"]])]
        records_by_model = {"model-a": recs_a, "model-b": recs_b}

        pooled = build_pooled_cooccurrence_matrix(records_by_model)
        for i in range(len(pooled.items)):
            assert abs(pooled.matrix[i][i] - 1.0) < 1e-10, (
                f"Diagonal at {i} ({pooled.items[i]}) = {pooled.matrix[i][i]}, expected 1.0"
            )

    def test_three_models_equal_weight(self):
        """Three models: pooled value = sum/3 regardless of run count per model."""
        items = ["a", "b", "c"]
        # model-a: all in one pile → co-occurrence = 1.0 for all pairs
        recs_a = [_make_record("model-a", 0, items, [["a", "b", "c"]])]
        # model-b: all separate → co-occurrence = 0.0 for all pairs
        recs_b = [_make_record("model-b", 0, items, [["a"], ["b"], ["c"]])]
        # model-c: a+b together, c alone → co-occurrence(a,b)=1.0, others=0.0
        recs_c = [_make_record("model-c", 0, items, [["a", "b"], ["c"]])]
        records_by_model = {"model-a": recs_a, "model-b": recs_b, "model-c": recs_c}

        pooled = build_pooled_cooccurrence_matrix(records_by_model)
        idx = {item: i for i, item in enumerate(pooled.items)}

        # a+b: model-a=1.0, model-b=0.0, model-c=1.0 → 2.0/3
        assert abs(pooled.matrix[idx["a"]][idx["b"]] - 2.0 / 3) < 1e-10
        # a+c: model-a=1.0, model-b=0.0, model-c=0.0 → 1.0/3
        assert abs(pooled.matrix[idx["a"]][idx["c"]] - 1.0 / 3) < 1e-10
        # b+c: model-a=1.0, model-b=0.0, model-c=0.0 → 1.0/3
        assert abs(pooled.matrix[idx["b"]][idx["c"]] - 1.0 / 3) < 1e-10

    def test_pooled_model_id_is_pooled(self):
        """The synthetic ModelRef in the returned matrix has model_id='pooled'."""
        items = ["a", "b", "c"]
        records_by_model = {
            "model-a": [_make_record("model-a", 0, items, [["a", "b"], ["c"]])],
        }
        pooled = build_pooled_cooccurrence_matrix(records_by_model)
        assert pooled.model.model_id == "pooled"

    def test_deterministic_with_same_input(self):
        """Same input produces identical output on repeated calls."""
        items = ["mother", "father", "sister", "brother"]
        piles_a = [["mother", "father"], ["sister", "brother"]]
        piles_b = [["mother", "sister"], ["father", "brother"]]
        recs_a = [_make_record("model-a", i, items, piles_a) for i in range(3)]
        recs_b = [_make_record("model-b", i, items, piles_b) for i in range(3)]
        records_by_model = {"model-a": recs_a, "model-b": recs_b}

        p1 = build_pooled_cooccurrence_matrix(records_by_model)
        p2 = build_pooled_cooccurrence_matrix(records_by_model)

        assert p1.items == p2.items
        for i in range(len(p1.items)):
            for j in range(len(p1.items)):
                assert p1.matrix[i][j] == p2.matrix[i][j]


# ---------------------------------------------------------------------------
# T3: cluster_terms
# ---------------------------------------------------------------------------

class TestClusterTerms:
    """Tests for CDA SME M2 (average linkage) and M3 (1-cooccurrence distance)."""

    def _simple_matrix(
        self,
        n: int = 4,
        items: list[str] | None = None,
    ) -> CooccurrenceMatrix:
        """Create a simple co-occurrence matrix with known structure.

        Items 0-1 strongly co-occur; items 2-3 strongly co-occur;
        cross-group co-occurrence is 0.1.
        """
        if items is None:
            items = [f"item_{i}" for i in range(n)]
        # Build matrix: strong within-group, weak between-group
        matrix = [[0.0] * n for _ in range(n)]
        half = n // 2
        for i in range(n):
            matrix[i][i] = 1.0
            for j in range(n):
                if i != j:
                    same_group = (i < half) == (j < half)
                    matrix[i][j] = 0.9 if same_group else 0.1
        return _make_cooccurrence_matrix(items, matrix)

    def test_basic_returns_term_cluster_result(self):
        mat = self._simple_matrix(4)
        result = cluster_terms(mat)

        assert result.items == mat.items
        assert len(result.linkage_matrix) == len(mat.items) - 1
        assert len(result.labels) == len(mat.items)
        assert result.n_clusters >= 1

    def test_linkage_uses_average_method_m2(self):
        """CDA SME M2: linkage method must be 'average' (UPGMA).

        Verify by computing the expected linkage independently using scipy
        with method='average' and comparing.
        """
        items = ["a", "b", "c", "d"]
        matrix_vals = [
            [1.0, 0.9, 0.1, 0.1],
            [0.9, 1.0, 0.1, 0.1],
            [0.1, 0.1, 1.0, 0.9],
            [0.1, 0.1, 0.9, 1.0],
        ]
        mat = _make_cooccurrence_matrix(items, matrix_vals)
        result = cluster_terms(mat)

        # Independently compute expected linkage using average method
        cooccur = np.array(matrix_vals, dtype=np.float64)
        expected_dissim = 1.0 - cooccur
        np.fill_diagonal(expected_dissim, 0.0)
        expected_dissim = (expected_dissim + expected_dissim.T) / 2.0
        condensed = squareform(expected_dissim, checks=False)
        expected_Z = scipy_linkage(condensed, method="average")

        np.testing.assert_allclose(
            result.linkage_matrix, expected_Z, atol=1e-12,
            err_msg="Linkage matrix does not match scipy average-linkage output",
        )

    def test_distance_is_one_minus_cooccurrence_m3(self):
        """CDA SME M3: distance = 1 - co-occurrence (not Jaccard, not Euclidean).

        Two items with co-occurrence = 0.8 should have distance = 0.2.
        We check by inspecting the first merge distance in the linkage matrix
        for a 2-item case.
        """
        items = ["x", "y"]
        cooccur_val = 0.8
        matrix = [[1.0, cooccur_val], [cooccur_val, 1.0]]
        mat = _make_cooccurrence_matrix(items, matrix)

        result = cluster_terms(mat)

        # With 2 items there is exactly 1 merge; distance should be 1 - 0.8 = 0.2
        assert len(result.linkage_matrix) == 1
        merge_distance = result.linkage_matrix[0][2]
        assert abs(merge_distance - (1.0 - cooccur_val)) < 1e-12, (
            f"Expected merge distance {1.0 - cooccur_val}, got {merge_distance}"
        )

    def test_cluster_groups_match_structure(self):
        """Items with high co-occurrence should be in the same cluster."""
        mat = self._simple_matrix(4, items=["a", "b", "c", "d"])
        result = cluster_terms(mat, n_clusters=2)

        # a+b should be one cluster, c+d another
        idx = {item: i for i, item in enumerate(result.items)}
        assert result.labels[idx["a"]] == result.labels[idx["b"]]
        assert result.labels[idx["c"]] == result.labels[idx["d"]]
        assert result.labels[idx["a"]] != result.labels[idx["c"]]

    def test_single_item_degenerate(self):
        """Single item: no merges, all in cluster 1."""
        mat = _make_cooccurrence_matrix(["solo"], [[1.0]])
        result = cluster_terms(mat)

        assert result.items == ["solo"]
        assert result.n_clusters == 1
        assert result.labels == [1]
        assert result.linkage_matrix.shape == (0, 4)

    def test_n_clusters_parameter(self):
        """n_clusters parameter forces the cut level.

        Use a matrix with 3 well-separated groups of 2 items each so that
        fcluster with maxclust=3 reliably produces 3 distinct cluster labels.
        """
        # 6 items in 3 well-separated groups: {a,b}, {c,d}, {e,f}
        # Strong within-group co-occurrence (0.95); near-zero between groups
        items = ["a", "b", "c", "d", "e", "f"]
        n = 6
        matrix = [[0.0] * n for _ in range(n)]
        groups = [[0, 1], [2, 3], [4, 5]]  # indices into items
        for i in range(n):
            matrix[i][i] = 1.0
        for g in groups:
            for i in g:
                for j in g:
                    if i != j:
                        matrix[i][j] = 0.95
        # between-group: 0.01
        for i in range(n):
            for j in range(n):
                if matrix[i][j] == 0.0 and i != j:
                    matrix[i][j] = 0.01

        mat = _make_cooccurrence_matrix(items, matrix)
        result = cluster_terms(mat, n_clusters=3)

        assert result.n_clusters == 3
        assert len(set(result.labels)) == 3

        # Check the groupings are correct
        idx = {item: i for i, item in enumerate(result.items)}
        assert result.labels[idx["a"]] == result.labels[idx["b"]]
        assert result.labels[idx["c"]] == result.labels[idx["d"]]
        assert result.labels[idx["e"]] == result.labels[idx["f"]]
        # Groups must be distinct
        assert len({result.labels[idx["a"]], result.labels[idx["c"]], result.labels[idx["e"]]}) == 3

    def test_deterministic_output(self):
        """Same input produces identical linkage matrix on repeated calls."""
        mat = self._simple_matrix(4)
        r1 = cluster_terms(mat)
        r2 = cluster_terms(mat)

        np.testing.assert_array_equal(r1.linkage_matrix, r2.linkage_matrix)
        assert r1.labels == r2.labels

    def test_diagonal_set_to_zero_before_squareform(self):
        """Diagonal is 0.0 after (1 - co-occurrence) subtraction (floating-point safety).

        A matrix with diagonal = 1.0 must produce dissimilarity diagonal = 0.0.
        If the diagonal were non-zero, squareform would reject it.
        """
        items = ["a", "b", "c"]
        # Diagonal = 1.0 (standard)
        matrix = [
            [1.0, 0.7, 0.3],
            [0.7, 1.0, 0.3],
            [0.3, 0.3, 1.0],
        ]
        mat = _make_cooccurrence_matrix(items, matrix)
        # Should not raise
        result = cluster_terms(mat)
        assert len(result.labels) == 3


# ---------------------------------------------------------------------------
# Pipeline integration tests
# ---------------------------------------------------------------------------

class TestPipelineTermFields:
    """Verify that run_pipeline() populates the new DomainResult term fields."""

    def _two_model_records(self) -> list[InformantRecord]:
        """Two models, 3 runs each, family domain."""
        items = ["mother", "father", "sister", "brother"]
        recs = []
        for i in range(3):
            recs.append(_make_record(
                "model-a", i, items,
                [["mother", "father"], ["sister", "brother"]],
            ))
        for i in range(3):
            recs.append(_make_record(
                "model-b", i, items,
                [["mother", "sister"], ["father", "brother"]],
            ))
        return recs

    def test_term_mds_coordinates_populated(self):
        """DomainResult.term_mds_coordinates is a non-empty dict after pipeline."""
        records = self._two_model_records()
        result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

        assert result.term_mds_coordinates, "term_mds_coordinates should be non-empty"
        # Keys should be item names (strings)
        for key, coords in result.term_mds_coordinates.items():
            assert isinstance(key, str)
            assert len(coords) == 2
            assert all(isinstance(v, float) for v in coords)

    def test_term_mds_items_populated(self):
        """DomainResult.term_mds_items is a non-empty sorted list."""
        records = self._two_model_records()
        result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

        assert result.term_mds_items
        assert result.term_mds_items == sorted(result.term_mds_items)
        # Keys in term_mds_coordinates match term_mds_items
        assert set(result.term_mds_coordinates.keys()) == set(result.term_mds_items)

    def test_term_cluster_linkage_populated(self):
        """DomainResult.term_cluster_linkage is a non-empty nested list."""
        records = self._two_model_records()
        result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

        assert result.term_cluster_linkage
        # scipy linkage has shape (n_items - 1, 4)
        n_items = len(result.term_mds_items)
        assert len(result.term_cluster_linkage) == n_items - 1
        for row in result.term_cluster_linkage:
            assert len(row) == 4
            assert all(isinstance(v, float) for v in row)

    def test_term_cluster_assignments_populated(self):
        """DomainResult.term_cluster_assignments maps every item to a cluster id."""
        records = self._two_model_records()
        result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

        assert result.term_cluster_assignments
        assert set(result.term_cluster_assignments.keys()) == set(result.term_mds_items)
        for _item, cluster_id in result.term_cluster_assignments.items():
            assert isinstance(cluster_id, int)
            assert cluster_id >= 1  # scipy fcluster uses 1-based labels

    def test_term_cluster_labels_empty_by_default(self):
        """term_cluster_labels is empty — filled by T5 label aggregation, not pipeline."""
        records = self._two_model_records()
        result = run_pipeline(records, analysis_version="test", n_bootstrap=10)
        assert result.term_cluster_labels == []

    def test_mds_within_model_populated_f3(self):
        """CDA SME F3: WithinModelResult.mds_within_model is populated (Register 1).

        Each entry should be a list of dicts with keys "item", "x", "y".
        """
        records = self._two_model_records()
        result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

        assert result.within_model_results
        for wm in result.within_model_results:
            assert wm.mds_within_model, (
                f"mds_within_model empty for model {wm.model_id}"
            )
            for entry in wm.mds_within_model:
                assert isinstance(entry, dict)
                assert "item" in entry
                assert "x" in entry
                assert "y" in entry
                assert isinstance(entry["x"], float)
                assert isinstance(entry["y"], float)

    def test_term_fields_cover_all_items(self):
        """Every item in the union appears in all three term-level structures."""
        records = self._two_model_records()
        result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

        items_set = set(result.term_mds_items)
        assert items_set == set(result.term_mds_coordinates.keys())
        assert items_set == set(result.term_cluster_assignments.keys())

    def test_single_model_term_fields_populated(self):
        """Single-model case: term MDS and AHC still run on the per-model matrix."""
        items = ["mother", "father", "sister", "brother"]
        records = [
            _make_record("model-a", i, items, [["mother", "father"], ["sister", "brother"]])
            for i in range(3)
        ]
        result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

        # With 4 items >= 3 threshold, pooled MDS should run
        assert result.term_mds_coordinates
        assert result.term_mds_items
        assert result.term_cluster_linkage
        assert result.term_cluster_assignments

    def test_term_mds_coordinates_are_floats(self):
        """Coordinates are list[float], not tuple[float, float] (schema uses list)."""
        records = self._two_model_records()
        result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

        for item, coords in result.term_mds_coordinates.items():
            assert isinstance(coords, list), (
                f"Coordinates for {item!r} should be list, got {type(coords)}"
            )

    def test_pipeline_result_round_trips_to_json(self):
        """DomainResult with new term fields serializes to valid JSON."""
        import json
        records = self._two_model_records()
        result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

        # Should not raise
        json_str = result.model_dump_json()
        data = json.loads(json_str)

        assert "term_mds_coordinates" in data
        assert "term_mds_items" in data
        assert "term_cluster_linkage" in data
        assert "term_cluster_assignments" in data
        assert "term_cluster_labels" in data
