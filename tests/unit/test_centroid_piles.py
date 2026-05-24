"""Unit tests for centroid pile extraction and term stability computation.

Tests the _build_centroid_piles helper in cdb_analyze.pipeline and the
CentroidPileData schema. All fixtures are synthetic — no real API calls.

CDA SME ruling F5 (2026-05-24-phase9a-cda-sme-verdict.md):
  "same pile" = set equality of co-occurring items, NOT pile index.
  term_stability[term] = n_runs_same_pile / n_runs_total
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from cdb_analyze.pipeline import _build_centroid_piles
from cdb_core.schemas import (
    CentroidPileData,
    FreelistRecord,
    InformantRecord,
    InterviewRecord,
    PileSortRecord,
    WithinModelResult,
)

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def _make_record(
    model_id: str,
    run_index: int,
    informant_id: str,
    piles: list[list[str]],
    labels: list[str] | None = None,
) -> InformantRecord:
    """Build a minimal InformantRecord with specified pile structure."""
    items: list[str] = [item for pile in piles for item in pile]
    if labels is None:
        labels = [f"pile_{i}" for i in range(len(piles))]

    n = len(items)
    idx = {item: i for i, item in enumerate(items)}
    matrix = [[0] * n for _ in range(n)]
    for pile in piles:
        for a in pile:
            for b in pile:
                matrix[idx[a]][idx[b]] = 1

    return InformantRecord(
        informant_id=informant_id,
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


def _make_wmr(
    model_id: str,
    records: list[InformantRecord],
    centroid_run_id: str | None = None,
) -> WithinModelResult:
    """Build a minimal WithinModelResult with the specified centroid_run_id."""
    if centroid_run_id is None and records:
        centroid_run_id = records[0].informant_id
    return WithinModelResult(
        model_id=model_id,
        n_runs=len(records),
        oci=1.0,
        underestimates_uncertainty=True,
        centroid_run_id=centroid_run_id,
    )


# ---------------------------------------------------------------------------
# Tests: CentroidPileData schema
# ---------------------------------------------------------------------------

class TestCentroidPileDataSchema:
    """CentroidPileData is a valid Pydantic model with expected defaults."""

    def test_basic_construction(self) -> None:
        cpd = CentroidPileData(
            piles=[["mother", "father"], ["sister", "brother"]],
            labels=["Parents", "Siblings"],
            term_stability={"mother": 0.8, "father": 0.9, "sister": 1.0, "brother": 0.6},
        )
        assert cpd.piles == [["mother", "father"], ["sister", "brother"]]
        assert cpd.labels == ["Parents", "Siblings"]
        assert cpd.term_stability["mother"] == pytest.approx(0.8)

    def test_default_term_stability_is_empty(self) -> None:
        cpd = CentroidPileData(
            piles=[["mother", "father"]],
            labels=["Parents"],
        )
        assert cpd.term_stability == {}

    def test_serialization_roundtrip(self) -> None:
        cpd = CentroidPileData(
            piles=[["a", "b"], ["c"]],
            labels=["AB", "C"],
            term_stability={"a": 1.0, "b": 0.5, "c": 0.75},
        )
        json_text = cpd.model_dump_json()
        restored = CentroidPileData.model_validate_json(json_text)
        assert restored.piles == cpd.piles
        assert restored.labels == cpd.labels
        assert restored.term_stability == pytest.approx(cpd.term_stability)


# ---------------------------------------------------------------------------
# Tests: _build_centroid_piles helper
# ---------------------------------------------------------------------------

class TestBuildCentroidPilesStability:
    """Per-term pile stability computation per CDA SME ruling F5."""

    def test_single_run_stability_is_all_ones(self) -> None:
        """A model with only 1 run: term_stability = 1.0 for all terms.

        The single run IS the centroid run, so it trivially matches itself.
        """
        piles = [["mother", "father"], ["sister", "brother"]]
        rec = _make_record("model-a", 0, "model-a_0", piles, ["Parents", "Siblings"])
        records_by_model = {"model-a": [rec]}
        wmr = _make_wmr("model-a", [rec], centroid_run_id="model-a_0")
        within_model_results = [wmr]

        result = _build_centroid_piles(records_by_model, within_model_results)

        assert "model-a" in result
        cpd = result["model-a"]
        assert cpd.piles == piles
        assert cpd.labels == ["Parents", "Siblings"]
        # Every term should have stability = 1.0 (1 run, always matches)
        for term in ["mother", "father", "sister", "brother"]:
            assert cpd.term_stability[term] == pytest.approx(1.0), (
                f"Expected term_stability[{term!r}] == 1.0 for single-run model"
            )

    def test_all_identical_runs_stability_is_all_ones(self) -> None:
        """All runs have identical pile structure: stability = 1.0 for all."""
        piles = [["mother", "father"], ["sister", "brother"]]
        recs = [
            _make_record("model-a", i, f"model-a_{i}", piles)
            for i in range(3)
        ]
        records_by_model = {"model-a": recs}
        # Centroid is run 0
        wmr = _make_wmr("model-a", recs, centroid_run_id="model-a_0")
        within_model_results = [wmr]

        result = _build_centroid_piles(records_by_model, within_model_results)

        cpd = result["model-a"]
        for term in ["mother", "father", "sister", "brother"]:
            assert cpd.term_stability[term] == pytest.approx(1.0)

    def test_all_different_runs_stability_is_one_over_n(self) -> None:
        """When every run differs from the centroid, stability = 1/n_runs.

        The centroid run itself always matches, so with 3 runs where runs 1
        and 2 differ from centroid (run 0):
          term_stability = 1/3 for all terms that changed.
        """
        centroid_piles = [["mother", "father"], ["sister", "brother"]]
        # Run 1 and run 2 have a completely different partition
        alt_piles = [["mother", "sister"], ["father", "brother"]]

        recs = [
            _make_record("model-a", 0, "model-a_0", centroid_piles),
            _make_record("model-a", 1, "model-a_1", alt_piles),
            _make_record("model-a", 2, "model-a_2", alt_piles),
        ]
        records_by_model = {"model-a": recs}
        wmr = _make_wmr("model-a", recs, centroid_run_id="model-a_0")

        result = _build_centroid_piles(records_by_model, [wmr])

        cpd = result["model-a"]
        # 1 run (itself) matches out of 3 → stability = 1/3
        for term in ["mother", "father", "sister", "brother"]:
            assert cpd.term_stability[term] == pytest.approx(1 / 3), (
                f"Expected 1/3 stability for {term!r}"
            )

    def test_partial_stability(self) -> None:
        """Some terms stable, some not.

        Centroid run: pile0=[A, B], pile1=[C, D]
        Run 1:        pile0=[A, B], pile1=[C, D]   — identical (matches)
        Run 2:        pile0=[A, C], pile1=[B, D]   — A splits from B

        Expected stability:
          A: 2/3 (centroid + run 1 match; run 2 does not)
          B: 2/3 (same reasoning)
          C: 2/3 (in pile with D in centroid and run 1; run 2: in pile with A)
          D: 2/3 (in pile with C in centroid and run 1; run 2: in pile with B)
        """
        centroid_piles = [["A", "B"], ["C", "D"]]
        same_piles = [["A", "B"], ["C", "D"]]     # run 1 — identical
        diff_piles = [["A", "C"], ["B", "D"]]      # run 2 — A and C swapped

        recs = [
            _make_record("m", 0, "m_0", centroid_piles),
            _make_record("m", 1, "m_1", same_piles),
            _make_record("m", 2, "m_2", diff_piles),
        ]
        records_by_model = {"m": recs}
        wmr = _make_wmr("m", recs, centroid_run_id="m_0")

        result = _build_centroid_piles(records_by_model, [wmr])

        cpd = result["m"]
        for term in ["A", "B", "C", "D"]:
            assert cpd.term_stability[term] == pytest.approx(2 / 3), (
                f"Expected 2/3 stability for {term!r}; got {cpd.term_stability[term]}"
            )

    def test_set_equality_not_index_equality(self) -> None:
        """'Same pile' means same co-occurring set, NOT same pile index.

        Centroid: pile_index=0 → [A, B], pile_index=1 → [C]
        Run 1:    pile_index=0 → [C],    pile_index=1 → [A, B]
           (pile order swapped — same groupings, different indices)

        Per SME ruling F5: A and B are in the same pile as each other in
        both centroid and run 1. C is alone in both. Stability should be 1.0.
        """
        centroid_piles = [["A", "B"], ["C"]]
        swapped_piles  = [["C"], ["A", "B"]]   # same partition, different order

        recs = [
            _make_record("m", 0, "m_0", centroid_piles),
            _make_record("m", 1, "m_1", swapped_piles),
        ]
        records_by_model = {"m": recs}
        wmr = _make_wmr("m", recs, centroid_run_id="m_0")

        result = _build_centroid_piles(records_by_model, [wmr])

        cpd = result["m"]
        # All terms stable because the partition is the same (set equality)
        assert cpd.term_stability["A"] == pytest.approx(1.0), (
            "A should be stable: co-occurring set {B} is identical in both runs"
        )
        assert cpd.term_stability["B"] == pytest.approx(1.0), (
            "B should be stable: co-occurring set {A} is identical in both runs"
        )
        assert cpd.term_stability["C"] == pytest.approx(1.0), (
            "C should be stable: co-occurring set {} (singleton) identical in both"
        )

    def test_singleton_pile_stability(self) -> None:
        """A term that is always alone in its pile has co-occurring set = {}.

        The empty set is still a valid frozenset; equality still holds when
        the term is alone in both runs.
        """
        centroid_piles = [["A", "B"], ["lone"]]
        same_piles     = [["A", "B"], ["lone"]]
        diff_piles     = [["A", "lone"], ["B"]]  # lone moves to A's pile

        recs = [
            _make_record("m", 0, "m_0", centroid_piles),
            _make_record("m", 1, "m_1", same_piles),
            _make_record("m", 2, "m_2", diff_piles),
        ]
        records_by_model = {"m": recs}
        wmr = _make_wmr("m", recs, centroid_run_id="m_0")

        result = _build_centroid_piles(records_by_model, [wmr])

        cpd = result["m"]
        # 'lone': runs 0 and 1 match (co-occurring set = {}); run 2 does not
        assert cpd.term_stability["lone"] == pytest.approx(2 / 3)


# ---------------------------------------------------------------------------
# Tests: _build_centroid_piles edge cases
# ---------------------------------------------------------------------------

class TestBuildCentroidPilesEdgeCases:
    """Edge cases: missing centroid_run_id, multi-model, labels propagation."""

    def test_no_centroid_run_id_skips_model(self) -> None:
        """A model whose WithinModelResult.centroid_run_id is None is omitted."""
        piles = [["a", "b"]]
        rec = _make_record("m", 0, "m_0", piles)
        records_by_model = {"m": [rec]}
        wmr = WithinModelResult(
            model_id="m",
            n_runs=1,
            oci=1.0,
            underestimates_uncertainty=True,
            centroid_run_id=None,  # explicitly None
        )

        result = _build_centroid_piles(records_by_model, [wmr])

        assert "m" not in result, (
            "Model with centroid_run_id=None must not appear in output"
        )

    def test_centroid_run_not_in_records_skips_model(self) -> None:
        """If centroid_run_id points to a record not in the list, skip model."""
        piles = [["a", "b"]]
        rec = _make_record("m", 0, "m_0", piles)
        records_by_model = {"m": [rec]}
        wmr = _make_wmr("m", [rec], centroid_run_id="NONEXISTENT_ID")

        result = _build_centroid_piles(records_by_model, [wmr])

        assert "m" not in result

    def test_multiple_models_independent(self) -> None:
        """Multiple models produce independent CentroidPileData entries."""
        piles_a = [["mother", "father"], ["sister", "brother"]]
        piles_b = [["mother", "sister"], ["father", "brother"]]

        recs_a = [_make_record("model-a", i, f"model-a_{i}", piles_a) for i in range(3)]
        recs_b = [_make_record("model-b", i, f"model-b_{i}", piles_b) for i in range(3)]

        records_by_model = {"model-a": recs_a, "model-b": recs_b}
        wmr_a = _make_wmr("model-a", recs_a, centroid_run_id="model-a_0")
        wmr_b = _make_wmr("model-b", recs_b, centroid_run_id="model-b_0")

        result = _build_centroid_piles(records_by_model, [wmr_a, wmr_b])

        assert set(result.keys()) == {"model-a", "model-b"}
        # model-a's piles should reflect piles_a, not piles_b
        assert result["model-a"].piles == piles_a
        assert result["model-b"].piles == piles_b

    def test_labels_come_from_centroid_run_interview(self) -> None:
        """The labels in CentroidPileData are from the centroid run's interview."""
        piles = [["a", "b"], ["c", "d"]]
        centroid_labels = ["Alpha Group", "Beta Group"]

        # Centroid run (index 0) has the authoritative labels
        rec_centroid = _make_record("m", 0, "m_0", piles, centroid_labels)
        # Other runs have different labels — should NOT appear in output
        rec_other = _make_record("m", 1, "m_1", piles, ["Different", "Labels"])

        records_by_model = {"m": [rec_centroid, rec_other]}
        wmr = _make_wmr("m", [rec_centroid, rec_other], centroid_run_id="m_0")

        result = _build_centroid_piles(records_by_model, [wmr])

        assert result["m"].labels == centroid_labels

    def test_empty_records_by_model_returns_empty(self) -> None:
        """Empty records_by_model produces empty result dict."""
        result = _build_centroid_piles({}, [])
        assert result == {}

    def test_term_stability_values_in_unit_interval(self) -> None:
        """All term_stability values must be in [0.0, 1.0]."""
        centroid_piles = [["A", "B"], ["C", "D"]]
        mixed_piles_1  = [["A", "C"], ["B", "D"]]
        mixed_piles_2  = [["A", "B"], ["C", "D"]]  # same as centroid

        recs = [
            _make_record("m", 0, "m_0", centroid_piles),
            _make_record("m", 1, "m_1", mixed_piles_1),
            _make_record("m", 2, "m_2", mixed_piles_2),
        ]
        records_by_model = {"m": recs}
        wmr = _make_wmr("m", recs, centroid_run_id="m_0")

        result = _build_centroid_piles(records_by_model, [wmr])

        for term, stability in result["m"].term_stability.items():
            assert 0.0 <= stability <= 1.0, (
                f"term_stability[{term!r}] = {stability} outside [0, 1]"
            )


# ---------------------------------------------------------------------------
# Tests: pipeline integration — centroid_piles appears in DomainResult
# ---------------------------------------------------------------------------

class TestPipelineCentroidPilesIntegration:
    """centroid_piles is populated by run_pipeline."""

    def test_run_pipeline_populates_centroid_piles(self) -> None:
        """run_pipeline produces non-empty centroid_piles for each model."""
        from cdb_analyze.pipeline import run_pipeline

        piles_a = [["mother", "father"], ["sister", "brother"]]
        piles_b = [["mother", "sister"], ["father", "brother"]]
        items = ["mother", "father", "sister", "brother"]

        recs: list[InformantRecord] = []
        for i in range(3):
            recs.append(_make_record("model-a", i, f"model-a_{i}", piles_a))
        for i in range(3):
            recs.append(_make_record("model-b", i, f"model-b_{i}", piles_b))

        result = run_pipeline(recs, analysis_version="test", n_bootstrap=5)

        assert set(result.centroid_piles.keys()) == {"model-a", "model-b"}

        for mid in ["model-a", "model-b"]:
            cpd = result.centroid_piles[mid]
            # Piles must cover all items
            covered_items = set(item for pile in cpd.piles for item in pile)
            assert covered_items == set(items), (
                f"{mid}: piles do not cover all items"
            )
            # Labels: one per pile
            assert len(cpd.labels) == len(cpd.piles)
            # Stability values must be in [0, 1]
            for term, stab in cpd.term_stability.items():
                assert 0.0 <= stab <= 1.0, f"{mid}: {term!r} stability {stab}"

    def test_centroid_piles_in_serialized_json(self) -> None:
        """centroid_piles survives DomainResult model_dump_json round-trip."""
        import json

        from cdb_analyze.pipeline import run_pipeline

        piles = [["a", "b"], ["c", "d"]]
        recs = [_make_record("m", i, f"m_{i}", piles) for i in range(3)]
        result = run_pipeline(recs, analysis_version="test", n_bootstrap=5)

        json_text = result.model_dump_json()
        data = json.loads(json_text)

        assert "centroid_piles" in data
        assert "m" in data["centroid_piles"]
        cpd_data = data["centroid_piles"]["m"]
        assert "piles" in cpd_data
        assert "labels" in cpd_data
        assert "term_stability" in cpd_data
