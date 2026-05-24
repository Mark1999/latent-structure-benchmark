"""Integration test for the analysis pipeline. Uses synthetic records."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from cdb_analyze.pipeline import (
    group_by_model,
    load_records,
    run_pipeline,
    write_result,
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
    """Build a minimal InformantRecord."""
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


def _synthetic_records() -> list[InformantRecord]:
    """Two models, 3 runs each, different pile structures."""
    items = ["mother", "father", "sister", "brother"]

    records = []
    # Model A: groups by generation (parents vs siblings)
    for i in range(3):
        records.append(_make_record(
            "model-a", i, items,
            [["mother", "father"], ["sister", "brother"]],
        ))
    # Model B: groups by gender
    for i in range(3):
        records.append(_make_record(
            "model-b", i, items,
            [["mother", "sister"], ["father", "brother"]],
        ))
    return records


def test_group_by_model():
    records = _synthetic_records()
    groups = group_by_model(records)
    assert set(groups.keys()) == {"model-a", "model-b"}
    assert len(groups["model-a"]) == 3
    assert len(groups["model-b"]) == 3


def test_run_pipeline_produces_domain_result():
    records = _synthetic_records()
    result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

    assert result.domain_slug == "family"
    assert result.analysis_version == "test"
    assert len(result.models) == 2
    assert "model-a" in result.mds_coordinates
    assert "model-b" in result.mds_coordinates
    assert "model-a" in result.mds_uncertainty
    assert "model-b" in result.mds_uncertainty
    assert len(result.similarity_matrix) == 2
    assert len(result.similarity_ci) == 2
    assert result.consensus_score > 0
    assert result.groundings == []
    assert result.generated_lede == ""


def test_run_pipeline_populates_sutrop_fields():
    """Sutrop CSI and salience-index agreement are populated per model.

    SME_REVIEW.md §2.1: Sutrop CSI is more robust to list-length variance
    than Smith's S; the Spearman ρ between the two rankings is the QA
    signal for list-length variance affecting salience structure.
    """
    records = _synthetic_records()
    result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

    # Per-model CSI entries
    assert set(result.sutrop_csi.keys()) == {"model-a", "model-b"}
    for mid, csi_list in result.sutrop_csi.items():
        assert len(csi_list) > 0, f"{mid} has no Sutrop CSI entries"
        # Each entry is a SutropCSI pydantic model with the right fields
        top = csi_list[0]
        assert top.item
        assert top.csi > 0
        assert top.f_mentions > 0
        assert top.n_runs == 3  # 3 runs per model in _synthetic_records
        assert top.mean_position >= 1.0

    # Per-model Smith's S vs Sutrop CSI Spearman ρ
    assert set(result.salience_index_agreement.keys()) == {"model-a", "model-b"}
    for mid, rho in result.salience_index_agreement.items():
        assert -1.0 <= rho <= 1.0, f"{mid} rho out of range: {rho}"


def test_run_pipeline_populates_within_model_results():
    """Register 1 results are populated per model on every pipeline run.

    One WithinModelResult per model, carrying OCI, centroid_run_id,
    underestimates_uncertainty=True (binding), and the
    deterministic_output marker. See ARCHITECTURE.md §4.2.0 and
    docs/BOOTSTRAP_DESIGN.md §2.

    Uses 4 runs per model (MIN_RUNS_FOR_DETERMINISTIC_FLAG) so that
    identical-pile synthetic inputs actually trip the deterministic
    flag — the default _synthetic_records N=3 fixture is below the
    reliability floor per two_level.MIN_RUNS_FOR_DETERMINISTIC_FLAG.
    """
    items = ["mother", "father", "sister", "brother"]
    records = []
    # Model A: 4 identical runs — should trigger deterministic_output
    for i in range(4):
        records.append(_make_record(
            "model-a", i, items,
            [["mother", "father"], ["sister", "brother"]],
        ))
    # Model B: 4 identical runs (different structure) — also deterministic
    for i in range(4):
        records.append(_make_record(
            "model-b", i, items,
            [["mother", "sister"], ["father", "brother"]],
        ))
    result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

    assert len(result.within_model_results) == 2
    by_model = {wm.model_id: wm for wm in result.within_model_results}
    assert set(by_model.keys()) == {"model-a", "model-b"}

    for mid, wm in by_model.items():
        assert wm.n_runs == 4
        assert wm.oci >= 0.0
        # Binding underestimation caveat is always set per BOOTSTRAP_DESIGN.md §2
        assert wm.underestimates_uncertainty is True
        # Identical pile structures per model at N=4 → agreement matrix
        # is rank-1 AND passes the reliability floor; deterministic_output
        # fires (state R1-c per DESIGN_SYSTEM.md §3.3.5).
        assert wm.deterministic_output is True
        assert wm.centroid_run_id is not None
        # Centroid must be one of the input records
        assert wm.centroid_run_id in {r.informant_id for r in records if r.model_id == mid}


def test_run_pipeline_small_n_does_not_trigger_deterministic_flag():
    """Below MIN_RUNS_FOR_DETERMINISTIC_FLAG (N=4), identical runs alone
    are not enough to raise the deterministic_output flag.

    Per CDA SME review of PR A (2026-04-20, recommendation R2): at N=2
    or N=3, a single pair of identical runs can push λ₂ below the
    numerical-zero threshold without the model being genuinely
    deterministic. The reliability floor prevents this spurious trip.
    """
    items = ["mother", "father", "sister", "brother"]
    records = []
    # 3 identical runs per model — below the reliability floor
    for i in range(3):
        records.append(_make_record(
            "model-a", i, items,
            [["mother", "father"], ["sister", "brother"]],
        ))
    for i in range(3):
        records.append(_make_record(
            "model-b", i, items,
            [["mother", "sister"], ["father", "brother"]],
        ))
    result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

    for wm in result.within_model_results:
        assert wm.n_runs == 3
        assert wm.deterministic_output is False  # reliability floor holds


def test_pipeline_single_model():
    """Single model should produce a valid but trivial DomainResult."""
    items = ["mother", "father", "sister", "brother"]
    records = [
        _make_record("model-a", i, items, [["mother", "father"], ["sister", "brother"]])
        for i in range(3)
    ]
    result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

    assert len(result.models) == 1
    assert result.mds_coordinates["model-a"] == (0.0, 0.0)
    assert result.consensus_score == 1.0


def test_write_result(tmp_path: Path):
    records = _synthetic_records()
    result = run_pipeline(records, analysis_version="0.1", n_bootstrap=10)

    out_path = write_result(result, tmp_path)

    assert out_path.exists()
    assert out_path.name == "0.1.json"
    assert out_path.parent.name == "family"

    # Verify it's valid JSON and round-trips
    data = json.loads(out_path.read_text())
    assert data["domain_slug"] == "family"
    assert len(data["mds_coordinates"]) == 2


def test_centrality_happy_path():
    """>=2 models => cultural_centrality_scores is non-empty dict keyed by model_id."""
    records = _synthetic_records()
    result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

    assert set(result.cultural_centrality_scores.keys()) == {"model-a", "model-b"}
    for mid, score in result.cultural_centrality_scores.items():
        assert isinstance(score, float), f"{mid} score is not float"
    # negative_centrality_flag must correctly reflect sign of any entry
    expected_flag = any(v < 0 for v in result.cultural_centrality_scores.values())
    assert result.negative_centrality_flag == expected_flag


def test_centrality_all_positive_case():
    """When eigenvector is all-positive: flag=False, list=[], scores non-empty."""
    items = ["mother", "father", "sister", "brother"]
    records = []
    # Both models have identical pile structure → similarity matrix [[1,1],[1,1]],
    # first eigenvector is [1/√2, 1/√2] — all positive.
    for i in range(3):
        records.append(_make_record(
            "model-a", i, items,
            [["mother", "father"], ["sister", "brother"]],
        ))
    for i in range(3):
        records.append(_make_record(
            "model-b", i, items,
            [["mother", "father"], ["sister", "brother"]],
        ))
    result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

    assert len(result.cultural_centrality_scores) == 2
    assert result.negative_centrality_flag is False
    assert result.negative_centrality_models == []


def test_centrality_negative_case():
    """Construct a fixture where at least one score is negative and flag fires."""
    import numpy as np
    from cdb_analyze.consensus import compute_centrality_scores

    # Build a 3×3 similarity matrix where model-c opposes the dominant structure:
    # models a and b are highly similar to each other but anti-similar to c.
    model_ids = ["model-a", "model-b", "model-c"]
    sim = np.array([
        [1.0,  0.9, -0.5],
        [0.9,  1.0, -0.5],
        [-0.5, -0.5,  1.0],
    ], dtype=np.float64)

    scores = compute_centrality_scores(model_ids, sim)

    assert set(scores.keys()) == set(model_ids)
    # model-c should have a negative loading
    assert scores["model-c"] < 0, f"Expected model-c negative; got {scores}"
    assert scores["model-a"] > 0
    assert scores["model-b"] > 0

    # Simulate what pipeline does with these scores
    flag = any(v < 0 for v in scores.values())
    neg_models = [mid for mid, v in scores.items() if v < 0]
    assert flag is True
    assert "model-c" in neg_models


def test_centrality_single_model_degenerate():
    """Single-model input => all three centrality fields are empty/False, no exception."""
    items = ["mother", "father", "sister", "brother"]
    records = [
        _make_record("model-a", i, items, [["mother", "father"], ["sister", "brother"]])
        for i in range(3)
    ]
    result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

    assert result.cultural_centrality_scores == {}
    assert result.negative_centrality_flag is False
    assert result.negative_centrality_models == []


def test_centrality_consistency_invariant():
    """Invariant: negative_centrality_models = keys where score < 0."""
    records = _synthetic_records()
    result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

    expected_neg = {
        mid for mid, v in result.cultural_centrality_scores.items() if v < 0
    }
    assert set(result.negative_centrality_models) == expected_neg

    if expected_neg:
        assert result.negative_centrality_flag is True
    else:
        assert result.negative_centrality_flag is False


def test_centrality_scores_are_raw_eigenvector_loadings():
    """Scores must be raw first-eigenvector loadings — not normalized, not abs-valued."""
    import numpy as np
    from cdb_analyze.consensus import compute_centrality_scores

    sim = np.array([
        [1.0,  0.9, -0.5],
        [0.9,  1.0, -0.5],
        [-0.5, -0.5,  1.0],
    ], dtype=np.float64)
    model_ids = ["model-a", "model-b", "model-c"]
    scores = compute_centrality_scores(model_ids, sim)

    # Recompute expected values independently
    eigvals, eigvecs = np.linalg.eigh(sim)
    order = eigvals.argsort()[::-1]
    first = eigvecs[:, order[0]]
    if float(np.mean(first)) < 0:
        first = -first
    expected = {mid: float(first[i]) for i, mid in enumerate(model_ids)}

    for mid in model_ids:
        assert abs(scores[mid] - expected[mid]) < 1e-10, (
            f"{mid}: got {scores[mid]}, expected {expected[mid]}"
        )
    # Confirm values are NOT normalized to [0,1]
    assert max(abs(v) for v in scores.values()) > 0.1  # trivially true for raw loadings
    # Confirm negative value is preserved as negative, not abs-valued
    assert scores["model-c"] < 0


def test_centrality_zero_model_degenerate():
    import numpy as np
    from cdb_analyze.consensus import compute_centrality_scores

    scores = compute_centrality_scores([], np.empty((0, 0)))
    assert scores == {}


def test_load_records_from_jsonl(tmp_path: Path):
    records = _synthetic_records()
    jsonl = tmp_path / "informants.jsonl"
    with open(jsonl, "w") as f:
        for rec in records:
            f.write(rec.model_dump_json() + "\n")

    loaded = load_records(jsonl, "family")
    assert len(loaded) == 6

    # Filter by domain
    loaded_other = load_records(jsonl, "holidays")
    assert len(loaded_other) == 0


# ──────────────────────────────────────────────────────────────────────
# Term truncation metadata tests
# ──────────────────────────────────────────────────────────────────────

def test_pipeline_populates_truncation_metadata():
    """run_pipeline populates the four term truncation metadata fields.

    Per CDA SME T5 (2026-05-24-phase9a-term-truncation-sme-ruling.md):
    DomainResult must carry metadata documenting the truncation for
    reproducibility.
    """
    records = _synthetic_records()
    result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

    # Method must be set
    assert result.term_truncation_method == "cross_model_frequency_elbow"

    # Params must contain the four expected keys
    assert "min_items" in result.term_truncation_params
    assert "max_items" in result.term_truncation_params
    assert "min_model_count" in result.term_truncation_params
    assert "elbow_index" in result.term_truncation_params
    assert result.term_truncation_params["min_model_count"] == 2
    assert result.term_truncation_params["min_items"] == 15
    assert result.term_truncation_params["max_items"] == 300

    # Counts must be non-negative
    assert result.term_n_total_before_truncation >= 0
    assert result.term_n_after_truncation >= 0

    # After-truncation count must not exceed before-truncation count
    assert result.term_n_after_truncation <= result.term_n_total_before_truncation


def test_pipeline_truncation_n_after_matches_term_mds_items():
    """term_n_after_truncation must equal len(term_mds_items).

    This invariant ensures the metadata accurately reflects what entered
    the pooled matrix.
    """
    records = _synthetic_records()
    result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

    assert result.term_n_after_truncation == len(result.term_mds_items)


def test_pipeline_truncation_all_shared_terms():
    """When all terms appear in all models, no terms are dropped by the
    f_models < 2 pre-filter — all terms remain for the elbow step.
    """
    items = ["mother", "father", "sister", "brother", "aunt", "uncle",
             "grandmother", "grandfather", "cousin", "niece", "nephew",
             "son", "daughter", "husband", "wife", "child"]
    records = []
    # Two models, same item vocabulary, 3 runs each — all terms have f_models=2
    for i in range(3):
        records.append(_make_record(
            "model-a", i, items,
            [["mother", "father"], ["sister", "brother"],
             ["aunt", "uncle"], ["grandmother", "grandfather"],
             ["cousin", "niece", "nephew"], ["son", "daughter"],
             ["husband", "wife", "child"]],
        ))
    for i in range(3):
        records.append(_make_record(
            "model-b", i, items,
            [["mother", "father"], ["sister", "brother"],
             ["aunt", "uncle"], ["grandmother", "grandfather"],
             ["cousin", "niece", "nephew"], ["son", "daughter"],
             ["husband", "wife", "child"]],
        ))
    result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

    # All 16 terms appear in both models, so term_n_total_before_truncation = 16
    assert result.term_n_total_before_truncation == len(items)
    # No terms fail the f_models >= 2 filter since both models share all terms
    # The elbow may or may not cut — but no terms are discarded at the pre-filter step.
    # We cannot assert n_after == n_before (elbow may cut), but n_after must be >= 1.
    assert result.term_n_after_truncation >= 1


def test_pipeline_truncation_single_model_edge_case():
    """Single-model pipeline: all terms have f_models=1, so all fail the
    min_model_count=2 pre-filter. Pooled matrix falls back to item_subset=None
    (full union), preserving graceful degradation.
    """
    items = ["mother", "father", "sister", "brother"]
    records = [
        _make_record("model-a", i, items, [["mother", "father"], ["sister", "brother"]])
        for i in range(3)
    ]
    result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

    # All 4 terms have f_models=1, so shared_terms is empty → truncated_items=[]
    # → item_subset=None → pooled matrix uses full union (4 items).
    # term_n_total_before_truncation = 4 (all pile-sort terms)
    assert result.term_n_total_before_truncation == len(items)
    # Truncation metadata is still populated
    assert result.term_truncation_method == "cross_model_frequency_elbow"
    assert result.term_truncation_params["min_model_count"] == 2
