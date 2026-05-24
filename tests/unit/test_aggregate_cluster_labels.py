"""Unit tests for aggregate_cluster_labels() — Phase 9a T5.

CDA SME M6 (2026-05-24-phase9a-cda-sme-verdict.md) binding algorithm:
  1. For each AHC cluster C, get the set of items assigned to it.
  2. For each model's centroid pile, find the pile with highest Jaccard overlap
     with C's item set.  Jaccard >= 0.3 required for a match.
  3. Collect labels from all matching piles across models.
  4. Select modal label (most frequent, case-normalised).  Ties broken by
     shortest label.
  5. If all labels unique, use shortest.
  6. If no pile exceeds threshold, label = "Uncategorized".
  7. Return list indexed by (cluster_id - 1), sorted by cluster_id.

No LLM calls — pure string matching.
All fixtures are in-memory per tests/fixtures/README.md convention.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from cdb_analyze.pipeline import aggregate_cluster_labels, run_pipeline
from cdb_core.schemas import (
    CentroidPileData,
    FreelistRecord,
    InformantRecord,
    InterviewRecord,
    PileSortRecord,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cpd(piles: list[list[str]], labels: list[str]) -> CentroidPileData:
    """Build a minimal CentroidPileData for testing."""
    return CentroidPileData(
        piles=piles,
        labels=labels,
        term_stability={},
    )


# ---------------------------------------------------------------------------
# Basic Jaccard matching
# ---------------------------------------------------------------------------

class TestJaccardMatching:
    """Tests for the Jaccard-overlap step of CDA SME M6."""

    def test_exact_match_gives_label(self):
        """A pile whose item set exactly matches the cluster gets its label."""
        cluster_assignments = {"a": 1, "b": 1}
        cpd = _cpd(piles=[["a", "b"], ["c"]], labels=["Parents", "Siblings"])
        result = aggregate_cluster_labels(
            cluster_assignments,
            {"model-x": cpd},
        )
        assert result == ["Parents"]

    def test_below_threshold_gives_uncategorized(self):
        """Jaccard < 0.3 does not count; cluster gets 'Uncategorized'."""
        # Cluster = {a, b, c, d, e} (5 items)
        # Pile = {a} — Jaccard = 1/5 = 0.2 < 0.3 → no match
        cluster_assignments = {"a": 1, "b": 1, "c": 1, "d": 1, "e": 1}
        cpd = _cpd(piles=[["a"], ["b", "c", "d", "e"]], labels=["Solo", "Rest"])
        # Pile "Solo": intersection={a}, union={a,b,c,d,e} → 1/5 = 0.2 < 0.3
        # Pile "Rest": intersection={b,c,d,e}, union={a,b,c,d,e} → 4/5 = 0.8 ≥ 0.3
        result = aggregate_cluster_labels(
            cluster_assignments,
            {"model-x": cpd},
        )
        # Best match is "Rest" (0.8 ≥ 0.3)
        assert result == ["Rest"]

    def test_no_match_above_threshold(self):
        """No pile exceeds threshold → 'Uncategorized'."""
        # Cluster = {a, b, c} — pile has only {x, y, z} — no overlap
        cluster_assignments = {"a": 1, "b": 1, "c": 1}
        cpd = _cpd(piles=[["x", "y", "z"]], labels=["Unrelated"])
        result = aggregate_cluster_labels(
            cluster_assignments,
            {"model-x": cpd},
        )
        assert result == ["Uncategorized"]

    def test_best_pile_is_chosen_per_model(self):
        """The pile with highest Jaccard is selected (not first or last pile)."""
        # Cluster = {a, b, c}
        # Pile 0 = {a} → Jaccard = 1/3 ≈ 0.33
        # Pile 1 = {a, b, c} → Jaccard = 3/3 = 1.0  (best)
        # Pile 2 = {a, b} → Jaccard = 2/3 ≈ 0.67
        cluster_assignments = {"a": 1, "b": 1, "c": 1}
        cpd = _cpd(
            piles=[["a"], ["a", "b", "c"], ["a", "b"]],
            labels=["Weak", "Perfect", "Good"],
        )
        result = aggregate_cluster_labels(
            cluster_assignments,
            {"model-x": cpd},
        )
        assert result == ["Perfect"]

    def test_jaccard_exactly_at_threshold_counts(self):
        """Jaccard == 0.3 (at threshold) counts as a match."""
        # Cluster = {a, b, c, d, e, f, g, h, i, j} (10 items)
        # Pile = {a, b, c} — intersection=3, union=10 → Jaccard=0.3 exactly
        cluster_assignments = {f"item{i}": 1 for i in range(10)}
        pile_items = ["item0", "item1", "item2"]
        cpd = _cpd(
            piles=[pile_items, [f"item{i}" for i in range(3, 10)]],
            labels=["Small", "Big"],
        )
        # "Big" pile: intersection=7, union=10 → 0.7 (higher); "Small": 0.3
        # Best is "Big"
        result = aggregate_cluster_labels(
            cluster_assignments,
            {"model-x": cpd},
        )
        assert result == ["Big"]

    def test_custom_jaccard_threshold(self):
        """jaccard_threshold parameter is respected."""
        # Jaccard = 2/4 = 0.5 — above default 0.3, but test with threshold=0.6
        cluster_assignments = {"a": 1, "b": 1}
        cpd = _cpd(piles=[["a", "b", "c", "d"]], labels=["SomePile"])
        # Intersection = {a,b}, union = {a,b,c,d} → Jaccard = 2/4 = 0.5 < 0.6
        result = aggregate_cluster_labels(
            cluster_assignments,
            {"model-x": cpd},
            jaccard_threshold=0.6,
        )
        assert result == ["Uncategorized"]

        # With default threshold (0.3): 0.5 >= 0.3 → match
        result2 = aggregate_cluster_labels(
            cluster_assignments,
            {"model-x": cpd},
        )
        assert result2 == ["SomePile"]


# ---------------------------------------------------------------------------
# Modal label selection
# ---------------------------------------------------------------------------

class TestModalLabelSelection:
    """Tests for step 4/5: modal label selection from candidates."""

    def test_modal_label_wins(self):
        """The most frequently appearing label (case-normalised) is selected."""
        # Three models, all with an exact match for cluster {a, b}
        # Model A labels it "Parents", B labels it "parents", C labels it "Elders"
        cluster_assignments = {"a": 1, "b": 1}
        cpd_a = _cpd(piles=[["a", "b"]], labels=["Parents"])
        cpd_b = _cpd(piles=[["a", "b"]], labels=["parents"])
        cpd_c = _cpd(piles=[["a", "b"]], labels=["Elders"])

        result = aggregate_cluster_labels(
            cluster_assignments,
            {"model-a": cpd_a, "model-b": cpd_b, "model-c": cpd_c},
        )
        # "parents" normalises to "parents"; "Parents" also normalises to "parents"
        # → frequency 2 vs 1 for "Elders"
        # canonical form for "parents" key: both "Parents" and "parents" are 7 chars;
        # lexicographic tie-break: "Parents" < "parents" (uppercase 'P' < lowercase 'p')
        assert result == ["Parents"]

    def test_case_normalised_modal_selects_shortest_original(self):
        """When two originals normalise to the same key, the shortest is kept."""
        cluster_assignments = {"a": 1, "b": 1}
        cpd_a = _cpd(piles=[["a", "b"]], labels=["Nuclear Family"])
        cpd_b = _cpd(piles=[["a", "b"]], labels=["nuclear family"])

        # Both normalise to "nuclear family" (freq=2); canonical form = shorter
        # "Nuclear Family" (13 chars) vs "nuclear family" (14 chars) → "Nuclear Family"
        result = aggregate_cluster_labels(
            cluster_assignments,
            {"model-a": cpd_a, "model-b": cpd_b},
        )
        assert result == ["Nuclear Family"]

    def test_tie_broken_by_shortest_label(self):
        """Two labels with equal frequency: shortest original wins."""
        # 2 models each vote for different labels (equal frequency)
        cluster_assignments = {"a": 1, "b": 1}
        cpd_a = _cpd(piles=[["a", "b"]], labels=["Grandparents"])
        cpd_b = _cpd(piles=[["a", "b"]], labels=["Kin"])

        result = aggregate_cluster_labels(
            cluster_assignments,
            {"model-a": cpd_a, "model-b": cpd_b},
        )
        # Both freq=1 → all unique → shortest wins: "Kin" (3 chars) < "Grandparents"
        assert result == ["Kin"]

    def test_all_unique_uses_shortest(self):
        """When every label appears exactly once, the shortest is used."""
        cluster_assignments = {"a": 1, "b": 1, "c": 1}
        cpd_a = _cpd(piles=[["a", "b", "c"]], labels=["Extended Family Members"])
        cpd_b = _cpd(piles=[["a", "b", "c"]], labels=["Family"])
        cpd_c = _cpd(piles=[["a", "b", "c"]], labels=["Relatives"])

        result = aggregate_cluster_labels(
            cluster_assignments,
            {"model-a": cpd_a, "model-b": cpd_b, "model-c": cpd_c},
        )
        assert result == ["Family"]

    def test_further_tie_broken_lexicographically(self):
        """When shortest labels are equal length, lexicographic order breaks tie."""
        cluster_assignments = {"a": 1, "b": 1}
        cpd_a = _cpd(piles=[["a", "b"]], labels=["Kin"])
        cpd_b = _cpd(piles=[["a", "b"]], labels=["Mom"])

        # Both 3 chars, both freq=1 → lexicographic: "Kin" < "Mom"
        result = aggregate_cluster_labels(
            cluster_assignments,
            {"model-a": cpd_a, "model-b": cpd_b},
        )
        assert result == ["Kin"]

    def test_modal_tie_broken_by_shortest_modal_candidate(self):
        """When multiple labels share max frequency, shortest modal label wins."""
        # cluster = {a, b}; 4 models: 2 vote "Parents", 2 vote "Pa" (both freq=2)
        cluster_assignments = {"a": 1, "b": 1}
        cpd1 = _cpd(piles=[["a", "b"]], labels=["Parents"])
        cpd2 = _cpd(piles=[["a", "b"]], labels=["Parents"])
        cpd3 = _cpd(piles=[["a", "b"]], labels=["Pa"])
        cpd4 = _cpd(piles=[["a", "b"]], labels=["Pa"])

        result = aggregate_cluster_labels(
            cluster_assignments,
            {f"m{i}": c for i, c in enumerate([cpd1, cpd2, cpd3, cpd4])},
        )
        # Both freq=2; "Pa" (2 chars) < "Parents" (7 chars)
        assert result == ["Pa"]


# ---------------------------------------------------------------------------
# Multi-cluster output ordering
# ---------------------------------------------------------------------------

class TestMultiClusterOrdering:
    """Verify result[i] corresponds to cluster_id = i+1 (sorted by cluster_id)."""

    def test_two_clusters_ordered_by_id(self):
        """result[0] = label for cluster 1, result[1] = label for cluster 2."""
        cluster_assignments = {"a": 1, "b": 1, "c": 2, "d": 2}
        cpd = _cpd(
            piles=[["a", "b"], ["c", "d"]],
            labels=["Cluster One", "Cluster Two"],
        )
        result = aggregate_cluster_labels(
            cluster_assignments,
            {"model-x": cpd},
        )
        assert len(result) == 2
        assert result[0] == "Cluster One"   # cluster_id=1
        assert result[1] == "Cluster Two"   # cluster_id=2

    def test_non_contiguous_cluster_ids_sorted(self):
        """Cluster IDs don't need to be contiguous; result is sorted by ID."""
        cluster_assignments = {"a": 2, "b": 2, "c": 5}
        cpd = _cpd(
            piles=[["a", "b"], ["c"]],
            labels=["Second", "Fifth"],
        )
        result = aggregate_cluster_labels(
            cluster_assignments,
            {"model-x": cpd},
        )
        # cluster IDs 2 and 5 → result[0] for id=2, result[1] for id=5
        # cluster_id=5: {c} vs pile ["c"] → Jaccard = 1/1 = 1.0 ≥ 0.3 → "Fifth"
        assert len(result) == 2
        assert result[0] == "Second"   # cluster_id=2
        assert result[1] == "Fifth"    # cluster_id=5: {c} exactly matches pile ["c"]

    def test_three_clusters_correct_labels(self):
        """Three well-separated clusters get distinct labels."""
        cluster_assignments = {
            "mother": 1, "father": 1,
            "sister": 2, "brother": 2,
            "uncle": 3, "aunt": 3,
        }
        cpd = _cpd(
            piles=[
                ["mother", "father"],
                ["sister", "brother"],
                ["uncle", "aunt"],
            ],
            labels=["Parents", "Siblings", "Relatives"],
        )
        result = aggregate_cluster_labels(
            cluster_assignments,
            {"model-x": cpd},
        )
        assert len(result) == 3
        assert result[0] == "Parents"
        assert result[1] == "Siblings"
        assert result[2] == "Relatives"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Edge-case tests for aggregate_cluster_labels()."""

    def test_empty_cluster_assignments_returns_empty(self):
        """Empty cluster_assignments → empty result."""
        result = aggregate_cluster_labels({}, {})
        assert result == []

    def test_no_centroid_piles_gives_uncategorized(self):
        """With no centroid pile data, every cluster is 'Uncategorized'."""
        cluster_assignments = {"a": 1, "b": 2}
        result = aggregate_cluster_labels(cluster_assignments, {})
        assert result == ["Uncategorized", "Uncategorized"]

    def test_singleton_cluster(self):
        """A single-item cluster is matched correctly."""
        # Cluster {a} (1 item), pile {a} (1 item) → Jaccard = 1/1 = 1.0
        cluster_assignments = {"a": 1}
        cpd = _cpd(piles=[["a"], ["b", "c"]], labels=["Solo", "Group"])
        result = aggregate_cluster_labels(cluster_assignments, {"m": cpd})
        assert result == ["Solo"]

    def test_single_model_single_cluster(self):
        """Minimal valid input: one model, one cluster."""
        cluster_assignments = {"x": 1, "y": 1, "z": 1}
        cpd = _cpd(piles=[["x", "y", "z"]], labels=["Everything"])
        result = aggregate_cluster_labels(cluster_assignments, {"m": cpd})
        assert result == ["Everything"]

    def test_empty_pile_in_centroid_data_skipped(self):
        """An empty pile has Jaccard = 0 against any non-empty cluster."""
        cluster_assignments = {"a": 1, "b": 1}
        cpd = _cpd(piles=[[], ["a", "b"]], labels=["EmptyPile", "GoodPile"])
        result = aggregate_cluster_labels(cluster_assignments, {"m": cpd})
        # Empty pile → union = {a,b}, intersection = {} → Jaccard = 0 < 0.3
        # "GoodPile" pile → Jaccard = 1.0
        assert result == ["GoodPile"]

    def test_deterministic_output(self):
        """Same input always produces the same output."""
        cluster_assignments = {"a": 1, "b": 1, "c": 2, "d": 2}
        cpd_a = _cpd(piles=[["a", "b"], ["c", "d"]], labels=["Alpha", "Beta"])
        cpd_b = _cpd(piles=[["a", "b"], ["c", "d"]], labels=["Gamma", "Beta"])
        piles_dict = {"m-a": cpd_a, "m-b": cpd_b}

        r1 = aggregate_cluster_labels(cluster_assignments, piles_dict)
        r2 = aggregate_cluster_labels(cluster_assignments, piles_dict)
        assert r1 == r2

    def test_result_is_list_of_strings(self):
        """Return type is list[str] even with multiple clusters."""
        cluster_assignments = {"a": 1, "b": 2}
        cpd = _cpd(piles=[["a"], ["b"]], labels=["One", "Two"])
        result = aggregate_cluster_labels(cluster_assignments, {"m": cpd})
        assert isinstance(result, list)
        for label in result:
            assert isinstance(label, str)


# ---------------------------------------------------------------------------
# Pipeline integration: term_cluster_labels populated by run_pipeline
# ---------------------------------------------------------------------------

def _make_record(
    model_id: str,
    run_index: int,
    items: list[str],
    piles: list[list[str]],
    labels: list[str],
) -> InformantRecord:
    """Build a minimal InformantRecord for pipeline integration tests."""
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
            parsed_pile_labels=labels,
        ),
        sha256_manifest={
            "freelist_prompt": "a", "freelist_response": "b",
            "pilesort_prompt": "c", "pilesort_response": "d",
            "interview_prompt": "e", "interview_response": "f",
            "request_params": "g", "informant_record_total": "h",
        },
        qa_passed=True,
    )


class TestPipelineIntegration:
    """Verify that run_pipeline() populates term_cluster_labels via T5 logic."""

    def test_term_cluster_labels_populated_by_pipeline(self):
        """run_pipeline() populates term_cluster_labels (non-empty list of strings)."""
        items = ["mother", "father", "sister", "brother"]
        records = []
        for i in range(3):
            records.append(_make_record(
                "model-a", i, items,
                piles=[["mother", "father"], ["sister", "brother"]],
                labels=["Parents", "Siblings"],
            ))
        for i in range(3):
            records.append(_make_record(
                "model-b", i, items,
                piles=[["mother", "father"], ["sister", "brother"]],
                labels=["Parental", "Siblings"],
            ))

        result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

        assert isinstance(result.term_cluster_labels, list)
        # Should have one label per cluster
        n_clusters = len(set(result.term_cluster_assignments.values()))
        assert len(result.term_cluster_labels) == n_clusters
        for label in result.term_cluster_labels:
            assert isinstance(label, str)
            assert len(label) > 0

    def test_term_cluster_labels_count_matches_assignments(self):
        """Number of labels equals number of distinct cluster IDs in assignments."""
        items = ["mother", "father", "sister", "brother"]
        records = []
        for i in range(3):
            records.append(_make_record(
                "model-a", i, items,
                piles=[["mother", "father"], ["sister", "brother"]],
                labels=["Parents", "Children"],
            ))

        result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

        n_clusters = len(set(result.term_cluster_assignments.values()))
        assert len(result.term_cluster_labels) == n_clusters

    def test_term_cluster_labels_in_json_output(self):
        """DomainResult serializes to JSON with term_cluster_labels present."""
        items = ["mother", "father", "sister", "brother"]
        records = []
        for i in range(3):
            records.append(_make_record(
                "model-a", i, items,
                piles=[["mother", "father"], ["sister", "brother"]],
                labels=["Parents", "Siblings"],
            ))

        result = run_pipeline(records, analysis_version="test", n_bootstrap=10)
        data = json.loads(result.model_dump_json())

        assert "term_cluster_labels" in data
        assert isinstance(data["term_cluster_labels"], list)

    def test_build_output_includes_all_term_fields(self):
        """build.py serialization includes all new term-level fields.

        Verifies the model_dump_json() path used by build.py produces a dict
        with all Phase 9a fields, not just the pre-existing ones.
        """
        items = ["mother", "father", "sister", "brother"]
        records = []
        for i in range(3):
            records.append(_make_record(
                "model-a", i, items,
                piles=[["mother", "father"], ["sister", "brother"]],
                labels=["Parents", "Siblings"],
            ))

        result = run_pipeline(records, analysis_version="test", n_bootstrap=10)
        data = json.loads(result.model_dump_json())

        expected_fields = [
            "term_mds_coordinates",
            "term_mds_items",
            "term_mds_uncertainty",
            "term_cluster_linkage",
            "term_cluster_assignments",
            "term_cluster_labels",
            "term_cluster_bp_values",
            "centroid_piles",
        ]
        for field in expected_fields:
            assert field in data, f"Field '{field}' missing from serialized DomainResult"
