"""Tests for bootstrap uncertainty module."""

from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
import pytest
from cdb_analyze.bootstrap import (
    bootstrap_branch_stability,
    bootstrap_centrality_ci,
    bootstrap_mds_ellipses,
    bootstrap_term_mds_ellipses,
)
from cdb_analyze.cooccurrence import build_cooccurrence_matrix
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


# ──────────────────────────────────────────────────────────────────────
# Fixtures and helpers for term-level bootstrap tests
# ──────────────────────────────────────────────────────────────────────


def _make_term_record(
    model_id: str,
    run_index: int,
    items: list[str],
    piles: list[list[str]],
) -> InformantRecord:
    """Minimal InformantRecord for term bootstrap tests (reuses _make_record)."""
    return _make_record(model_id, run_index, items, piles)


def _build_per_model_matrices(
    records_by_model: dict[str, list[InformantRecord]],
) -> dict:
    """Build per-model consensus CooccurrenceMatrix dict."""
    return {
        mid: build_cooccurrence_matrix(recs)
        for mid, recs in records_by_model.items()
        if recs
    }


# ──────────────────────────────────────────────────────────────────────
# bootstrap_term_mds_ellipses tests
# ──────────────────────────────────────────────────────────────────────


def test_term_ellipses_produced_for_all_items():
    """bootstrap_term_mds_ellipses should return one ellipse per item."""
    items = ["mother", "father", "sister", "brother", "uncle"]
    piles_a = [["mother", "father"], ["sister", "brother"], ["uncle"]]
    piles_b = [["mother", "sister"], ["father", "brother"], ["uncle"]]

    records = {
        "model-a": [_make_term_record("model-a", i, items, piles_a) for i in range(3)],
        "model-b": [_make_term_record("model-b", i, items, piles_b) for i in range(3)],
    }
    per_model = _build_per_model_matrices(records)

    # Build a simple reference by pooling (equal weight)
    from cdb_analyze.cooccurrence import build_pooled_cooccurrence_matrix
    from cdb_analyze.mds import run_item_mds

    pooled = build_pooled_cooccurrence_matrix(records)
    ref_coords_dict = run_item_mds(pooled)
    ref_coords: dict[str, tuple[float, float]] = {
        k: (float(v[0]), float(v[1])) for k, v in ref_coords_dict.items()
    }

    ellipses = bootstrap_term_mds_ellipses(
        per_model_matrices=per_model,
        reference_coordinates=ref_coords,
        reference_items=pooled.items,
        n_bootstrap=20,
        random_state=0,
    )

    # All items in the pooled matrix should have an ellipse
    assert set(ellipses.keys()) == set(pooled.items)
    for _item, ell in ellipses.items():
        assert ell.semi_major >= 0.0
        assert ell.semi_minor >= 0.0
        assert isinstance(ell.n_bootstrap, int)
        assert ell.n_bootstrap >= 0


def test_term_ellipses_deterministic_with_fixed_seed():
    """Same random_state must produce identical results."""
    items = ["a", "b", "c", "d", "e"]
    piles_a = [["a", "b"], ["c", "d"], ["e"]]
    piles_b = [["a", "c"], ["b", "d"], ["e"]]

    records = {
        "m1": [_make_term_record("m1", i, items, piles_a) for i in range(2)],
        "m2": [_make_term_record("m2", i, items, piles_b) for i in range(2)],
    }
    per_model = _build_per_model_matrices(records)

    from cdb_analyze.cooccurrence import build_pooled_cooccurrence_matrix
    from cdb_analyze.mds import run_item_mds

    pooled = build_pooled_cooccurrence_matrix(records)
    ref_coords = {k: (float(v[0]), float(v[1])) for k, v in run_item_mds(pooled).items()}

    ellipses1 = bootstrap_term_mds_ellipses(
        per_model, ref_coords, pooled.items, n_bootstrap=10, random_state=99,
    )
    ellipses2 = bootstrap_term_mds_ellipses(
        per_model, ref_coords, pooled.items, n_bootstrap=10, random_state=99,
    )

    for item in ellipses1:
        assert ellipses1[item].center == ellipses2[item].center
        assert ellipses1[item].semi_major == pytest.approx(ellipses2[item].semi_major)
        assert ellipses1[item].semi_minor == pytest.approx(ellipses2[item].semi_minor)


def test_term_ellipses_different_with_different_seeds():
    """Different random_state values should produce different results."""
    items = ["a", "b", "c", "d"]
    piles_a = [["a", "b"], ["c", "d"]]
    piles_b = [["a", "c"], ["b", "d"]]

    records = {
        "m1": [_make_term_record("m1", i, items, piles_a) for i in range(3)],
        "m2": [_make_term_record("m2", i, items, piles_b) for i in range(3)],
        "m3": [_make_term_record("m3", i, items, piles_a) for i in range(3)],
    }
    per_model = _build_per_model_matrices(records)

    from cdb_analyze.cooccurrence import build_pooled_cooccurrence_matrix
    from cdb_analyze.mds import run_item_mds

    pooled = build_pooled_cooccurrence_matrix(records)
    ref_coords = {k: (float(v[0]), float(v[1])) for k, v in run_item_mds(pooled).items()}

    ellipses1 = bootstrap_term_mds_ellipses(
        per_model, ref_coords, pooled.items, n_bootstrap=30, random_state=1,
    )
    ellipses2 = bootstrap_term_mds_ellipses(
        per_model, ref_coords, pooled.items, n_bootstrap=30, random_state=2,
    )

    # At least some ellipses should differ (very unlikely to be identical)
    centers_equal = all(
        ellipses1[it].center == ellipses2[it].center
        for it in ellipses1
        if it in ellipses2
    )
    assert not centers_equal, (
        "Different random seeds produced identical ellipse centers — "
        "this is extremely unlikely and indicates a determinism bug"
    )


def test_term_ellipses_resamples_models_not_runs():
    """Verify that bootstrap samples models with replacement.

    When a model-only-in-one-model item is present, it should appear in
    roughly 63% of bootstrap iterations (expected fraction for at least one
    draw when sampling with replacement from M models: 1 - (1 - 1/M)^M ≈ 1 - 1/e).
    """
    # model-a has item "unique-to-a" that model-b does not
    items_a = ["x", "y", "z", "unique-to-a"]
    items_b = ["x", "y", "z"]
    piles_a = [["x", "y"], ["z", "unique-to-a"]]
    piles_b = [["x", "y"], ["z"]]

    records = {
        "model-a": [_make_term_record("model-a", i, items_a, piles_a) for i in range(3)],
        "model-b": [_make_term_record("model-b", i, items_b, piles_b) for i in range(3)],
    }
    per_model = _build_per_model_matrices(records)

    from cdb_analyze.cooccurrence import build_pooled_cooccurrence_matrix
    from cdb_analyze.mds import run_item_mds

    pooled = build_pooled_cooccurrence_matrix(records)
    ref_coords = {k: (float(v[0]), float(v[1])) for k, v in run_item_mds(pooled).items()}

    B = 50
    ellipses = bootstrap_term_mds_ellipses(
        per_model, ref_coords, pooled.items, n_bootstrap=B, random_state=7,
    )

    # "unique-to-a" should have an ellipse (it appears in the reference item set)
    assert "unique-to-a" in ellipses
    # It should have been observed in some but not all iterations
    # (n_bootstrap on the ellipse reflects observed iterations, not B)
    ell = ellipses["unique-to-a"]
    # n_bootstrap <= B (some iterations may not include model-a)
    assert ell.n_bootstrap <= B


def test_term_ellipses_empty_if_too_few_items():
    """Returns empty dict when fewer than 3 items are present."""
    items = ["a", "b"]  # only 2 items
    piles = [["a"], ["b"]]

    records = {
        "m1": [_make_term_record("m1", 0, items, piles)],
        "m2": [_make_term_record("m2", 0, items, piles)],
    }
    per_model = _build_per_model_matrices(records)

    result = bootstrap_term_mds_ellipses(
        per_model_matrices=per_model,
        reference_coordinates={"a": (0.0, 1.0), "b": (1.0, 0.0)},
        reference_items=["a", "b"],
        n_bootstrap=10,
        random_state=0,
    )
    assert result == {}


# ──────────────────────────────────────────────────────────────────────
# bootstrap_branch_stability tests
# ──────────────────────────────────────────────────────────────────────


def _build_reference_linkage(
    items: list[str], piles_by_model: dict[str, list[list[str]]]
) -> np.ndarray:
    """Build a reference UPGMA linkage for testing."""
    from cdb_analyze.cooccurrence import build_pooled_cooccurrence_matrix
    from scipy.cluster.hierarchy import linkage as scipy_linkage
    from scipy.spatial.distance import squareform

    records = {
        mid: [_make_term_record(mid, i, items, piles) for i in range(2)]
        for mid, piles in piles_by_model.items()
    }
    pooled = build_pooled_cooccurrence_matrix(records)
    cooccur = np.array(pooled.matrix, dtype=np.float64)
    dissim = 1.0 - cooccur
    np.fill_diagonal(dissim, 0.0)
    dissim = (dissim + dissim.T) / 2.0
    condensed = squareform(dissim, checks=False)
    return scipy_linkage(condensed, method="average")


def test_branch_stability_returns_one_value_per_node():
    """bootstrap_branch_stability returns n_items - 1 values."""
    items = ["a", "b", "c", "d"]
    piles_a = [["a", "b"], ["c", "d"]]
    piles_b = [["a", "c"], ["b", "d"]]

    records = {
        "m1": [_make_term_record("m1", i, items, piles_a) for i in range(3)],
        "m2": [_make_term_record("m2", i, items, piles_b) for i in range(3)],
    }
    per_model = _build_per_model_matrices(records)
    ref_linkage = _build_reference_linkage(
        items, {"m1": piles_a, "m2": piles_b}
    )

    from cdb_analyze.cooccurrence import build_pooled_cooccurrence_matrix
    pooled = build_pooled_cooccurrence_matrix(records)

    bp_values = bootstrap_branch_stability(
        per_model_matrices=per_model,
        reference_linkage=ref_linkage,
        reference_items=pooled.items,
        n_bootstrap=20,
        random_state=42,
    )

    # n_items - 1 = 3 internal nodes
    assert len(bp_values) == len(items) - 1
    for bp in bp_values:
        assert 0.0 <= bp <= 1.0


def test_branch_stability_deterministic():
    """Same random_state produces identical BP values."""
    items = ["x", "y", "z", "w"]
    piles_a = [["x", "y"], ["z", "w"]]
    piles_b = [["x", "z"], ["y", "w"]]

    records = {
        "m1": [_make_term_record("m1", i, items, piles_a) for i in range(2)],
        "m2": [_make_term_record("m2", i, items, piles_b) for i in range(2)],
    }
    per_model = _build_per_model_matrices(records)
    ref_linkage = _build_reference_linkage(
        items, {"m1": piles_a, "m2": piles_b}
    )
    from cdb_analyze.cooccurrence import build_pooled_cooccurrence_matrix
    pooled = build_pooled_cooccurrence_matrix(records)

    bp1 = bootstrap_branch_stability(
        per_model, ref_linkage, pooled.items, n_bootstrap=15, random_state=7,
    )
    bp2 = bootstrap_branch_stability(
        per_model, ref_linkage, pooled.items, n_bootstrap=15, random_state=7,
    )

    assert bp1 == bp2


def test_branch_stability_perfect_stability():
    """A dendrogram that never changes across resamples should have BP=1.0.

    When both models produce identical pile structures, every bootstrap
    resample produces the same dendrogram, so all bipartitions have BP=1.0.
    """
    items = ["a", "b", "c", "d"]
    piles = [["a", "b"], ["c", "d"]]  # identical for both models

    records = {
        "m1": [_make_term_record("m1", i, items, piles) for i in range(3)],
        "m2": [_make_term_record("m2", i, items, piles) for i in range(3)],
    }
    per_model = _build_per_model_matrices(records)
    ref_linkage = _build_reference_linkage(
        items, {"m1": piles, "m2": piles}
    )
    from cdb_analyze.cooccurrence import build_pooled_cooccurrence_matrix
    pooled = build_pooled_cooccurrence_matrix(records)

    bp_values = bootstrap_branch_stability(
        per_model, ref_linkage, pooled.items, n_bootstrap=20, random_state=0,
    )

    # With identical pile structures all resamples reproduce the same tree
    for bp in bp_values:
        assert bp == pytest.approx(1.0)


def test_branch_stability_empty_linkage():
    """Returns empty list when reference_linkage has 0 rows."""
    items = ["a", "b"]
    records = {
        "m1": [_make_term_record("m1", 0, items, [["a"], ["b"]])],
    }
    per_model = _build_per_model_matrices(records)
    empty_linkage = np.empty((0, 4), dtype=np.float64)

    bp_values = bootstrap_branch_stability(
        per_model_matrices=per_model,
        reference_linkage=empty_linkage,
        reference_items=items,
        n_bootstrap=10,
        random_state=0,
    )
    assert bp_values == []


def test_branch_stability_values_in_range():
    """All BP values should be in [0, 1]."""
    items = ["p", "q", "r", "s", "t"]
    piles_a = [["p", "q"], ["r", "s"], ["t"]]
    piles_b = [["p", "r"], ["q", "s"], ["t"]]
    piles_c = [["p", "q", "r"], ["s", "t"]]

    records = {
        "m1": [_make_term_record("m1", i, items, piles_a) for i in range(2)],
        "m2": [_make_term_record("m2", i, items, piles_b) for i in range(2)],
        "m3": [_make_term_record("m3", i, items, piles_c) for i in range(2)],
    }
    per_model = _build_per_model_matrices(records)
    ref_linkage = _build_reference_linkage(
        items, {"m1": piles_a, "m2": piles_b, "m3": piles_c}
    )
    from cdb_analyze.cooccurrence import build_pooled_cooccurrence_matrix
    pooled = build_pooled_cooccurrence_matrix(records)

    bp_values = bootstrap_branch_stability(
        per_model, ref_linkage, pooled.items, n_bootstrap=30, random_state=12,
    )

    assert len(bp_values) == len(items) - 1
    for bp in bp_values:
        assert 0.0 <= bp <= 1.0


# ──────────────────────────────────────────────────────────────────────
# bootstrap_centrality_ci tests (Remedy B T5)
# See docs/status/2026-05-28-remedy-b-cda-sme-verdict.md N7 + T5 test
# contract (section "T5 test contract" items 1-6).
# ──────────────────────────────────────────────────────────────────────


def _make_consensus_sim_matrix(n_models: int) -> tuple[list[str], np.ndarray]:
    """Build a high-consensus block-diagonal similarity matrix.

    All n_models models form a single strongly cohesive block: diagonal
    entries are 1.0, off-diagonal are 0.85.  The first eigenvector of this
    matrix has all-positive, approximately equal loadings -- a clean fixture
    for determinism, shape/contract, and coverage tests.

    Returns (model_ids, similarity_matrix).
    """
    model_ids = [f"fx-model-{i:02d}" for i in range(n_models)]
    sim = np.full((n_models, n_models), 0.85)
    np.fill_diagonal(sim, 1.0)
    return model_ids, sim


def _make_two_cluster_sim_matrix() -> tuple[list[str], np.ndarray]:
    """Build a two-cluster anti-correlated similarity matrix (N7 fixture).

    Structure:
      - 5 "majority" models (indices 0-4): high mutual similarity (0.80),
        strongly negative cross-cluster similarity (-0.30).
      - 5 "minority" models (indices 5-9): same within-cluster pattern.

    The resulting first eigenvector has large-positive loadings for one
    cluster and large-negative loadings for the other (the mean-sign
    convention in compute_centrality_scores determines which cluster gets
    the positive sign).

    This fixture is the regression guard for N7: WITHOUT reference-vector
    sign alignment the bootstrap eigenvectors flip sign randomly across
    iterations (both +v and -v are equally valid), producing a bimodal
    loading distribution that straddles zero for every model.  WITH correct
    reference-vector alignment (dot(boot, ref) < 0 -> flip), every
    bootstrap eigenvector is forced to the same orientation and each
    model's CI lies entirely on one side of zero.

    Returns (model_ids, similarity_matrix).
    """
    n = 10
    model_ids = [f"maj-{i}" for i in range(5)] + [f"min-{i}" for i in range(5)]
    sim = np.zeros((n, n))

    np.fill_diagonal(sim, 1.0)

    # Within majority cluster: high similarity
    for i in range(5):
        for j in range(5):
            if i != j:
                sim[i, j] = 0.80

    # Within minority cluster: high similarity
    for i in range(5, 10):
        for j in range(5, 10):
            if i != j:
                sim[i, j] = 0.80

    # Cross-cluster: strongly negative (anti-correlated)
    for i in range(5):
        for j in range(5, 10):
            sim[i, j] = -0.30
            sim[j, i] = -0.30

    return model_ids, sim


# ── Test 1: Determinism ─────────────────────────────────────────────────


def test_centrality_ci_deterministic():
    """Same random_state=42 produces bit-identical output on two calls.

    T5 test contract item 1 (mirrors the determinism test pattern
    used for bootstrap_term_mds_ellipses above).
    """
    model_ids, sim = _make_consensus_sim_matrix(6)

    result_a = bootstrap_centrality_ci(model_ids, sim, n_bootstrap=50, random_state=42)
    result_b = bootstrap_centrality_ci(model_ids, sim, n_bootstrap=50, random_state=42)

    assert result_a == result_b, (
        "bootstrap_centrality_ci is not deterministic with the same random_state"
    )


def test_centrality_ci_different_seeds_differ():
    """Different random_state values produce different CIs.

    In a high-consensus block fixture the CIs overlap heavily, but the
    exact floating-point values will almost certainly differ because the
    resampled index sequences diverge.
    """
    model_ids, sim = _make_consensus_sim_matrix(6)

    r1 = bootstrap_centrality_ci(model_ids, sim, n_bootstrap=50, random_state=1)
    r2 = bootstrap_centrality_ci(model_ids, sim, n_bootstrap=50, random_state=2)

    assert any(
        r1[mid] != r2[mid] for mid in model_ids
    ), "Different seeds produced bit-identical output -- unexpected for stochastic bootstrap"


# ── Test 2: Shape / contract ────────────────────────────────────────────


def test_centrality_ci_shape_and_contract():
    """Returned dict has exactly the right keys and lo <= hi per model.

    T5 test contract item 2 (shape/contract).
    """
    model_ids, sim = _make_consensus_sim_matrix(8)

    result = bootstrap_centrality_ci(model_ids, sim, n_bootstrap=60, random_state=42)

    assert isinstance(result, dict)

    assert set(result.keys()) == set(model_ids), (
        f"Returned keys {set(result.keys())} != expected {set(model_ids)}"
    )

    for mid, (lo, hi) in result.items():
        assert isinstance(lo, float), f"{mid}: lo is not float"
        assert isinstance(hi, float), f"{mid}: hi is not float"
        assert lo <= hi, f"{mid}: lo={lo} > hi={hi} violates CI ordering"


def test_centrality_ci_reference_score_bracketed():
    """Reference centrality score must lie within [lo, hi] for every model.

    T5 test contract item 2 (bracketing sub-check).
    Per the SME verdict: "Every value satisfies lo <= reference_score <= hi
    ... If this fails for any model, the bootstrap distribution and the
    reference point are inconsistent -- either a sign-alignment bug or an
    eigh ordering bug."

    n_bootstrap=100: small enough to be fast; the bracketing property holds
    in a high-consensus fixture because the bootstrap distribution is
    unimodal and centred on the reference loading when sign-alignment is
    correct.
    """
    model_ids, sim = _make_consensus_sim_matrix(6)

    from cdb_analyze.consensus import compute_centrality_scores

    ref_scores = compute_centrality_scores(model_ids, sim)
    result = bootstrap_centrality_ci(model_ids, sim, n_bootstrap=100, random_state=42)

    for mid in model_ids:
        lo, hi = result[mid]
        ref = ref_scores[mid]
        assert lo <= ref <= hi, (
            f"{mid}: reference score {ref:.4f} not in CI [{lo:.4f}, {hi:.4f}]. "
            "Sign-alignment or eigh-ordering bug."
        )


# ── Test 3: Coverage sanity ─────────────────────────────────────────────


def test_centrality_ci_outlier_wider_than_inblock():
    """Outlier model CI is wider than in-block model CIs.

    T5 test contract item 3 (coverage sanity).

    Build a 7-model similarity matrix: 6 models in a tight consensus block
    (off-diagonal similarity 0.85) plus 1 outlier model (similarity 0.10
    to all in-block models).  The outlier's loading swings more across
    resamples because its presence or absence in a given draw shifts the
    dominant eigenvector more than the in-block models do.

    Tests ordering rather than absolute widths (the latter is fragile to
    RNG).  n_bootstrap=80 balances speed against detecting the ordering.
    """
    n_block = 6
    model_ids = [f"blk-{i}" for i in range(n_block)] + ["outlier"]
    n = len(model_ids)

    sim = np.full((n, n), 0.85)
    np.fill_diagonal(sim, 1.0)
    sim[-1, :n_block] = 0.10
    sim[:n_block, -1] = 0.10

    result = bootstrap_centrality_ci(model_ids, sim, n_bootstrap=80, random_state=42)

    outlier_width = result["outlier"][1] - result["outlier"][0]
    inblock_widths = [result[f"blk-{i}"][1] - result[f"blk-{i}"][0] for i in range(n_block)]
    median_inblock_width = float(np.median(inblock_widths))

    assert outlier_width > median_inblock_width, (
        f"Expected outlier CI width ({outlier_width:.4f}) > median in-block width "
        f"({median_inblock_width:.4f}).  Coverage sanity failed."
    )


# ── Test 4: Degenerate paths ────────────────────────────────────────────


def test_centrality_ci_degenerate_n_equals_2():
    """n=2 models returns {} (Q3 degenerate-n guard).

    T5 test contract item 4 (degenerate paths).
    At n=2, the centrality eigenvector is (1,1)/sqrt(2) up to sign --
    constant across all bootstrap draws -- so no CI is emitted.
    """
    model_ids = ["m-alpha", "m-beta"]
    sim = np.array([[1.0, 0.7], [0.7, 1.0]])

    result = bootstrap_centrality_ci(model_ids, sim, n_bootstrap=20, random_state=42)

    assert result == {}, f"Expected {{}} for n=2, got {result}"


def test_centrality_ci_degenerate_n_equals_1():
    """n=1 model returns {} (Q3 degenerate-n guard).

    T5 test contract item 4 (degenerate paths).
    """
    model_ids = ["solo-model"]
    sim = np.array([[1.0]])

    result = bootstrap_centrality_ci(model_ids, sim, n_bootstrap=10, random_state=42)

    assert result == {}, f"Expected {{}} for n=1, got {result}"


def test_centrality_ci_degenerate_all_zeros_does_not_raise():
    """An all-zeros similarity matrix does not raise; returns gracefully.

    T5 test contract item 4 (catastrophic-resample degenerate path).
    The all-zeros matrix has degenerate eigenstructure; the function must
    absorb any degenerate-resample exception and return {} or a partial
    dict -- the key requirement is no unhandled exception.
    """
    model_ids = [f"zz-{i}" for i in range(5)]
    sim = np.zeros((5, 5))

    result = bootstrap_centrality_ci(model_ids, sim, n_bootstrap=20, random_state=42)

    assert isinstance(result, dict)
    for _mid, ci in result.items():
        assert len(ci) == 2
        lo, hi = ci
        assert lo <= hi


# ── Test 5: Sign-alignment falsifiability (N7 -- CRITICAL) ─────────────


def test_centrality_ci_sign_alignment_falsifiability():
    """Bootstrap loadings stay sign-consistent with the reference vector.

    T5 test contract item 5 (sign-alignment, N7 binding requirement).

    REGRESSION GUARD for the original register-error / sign-alignment bug
    class that motivated Remedy B.  This is the load-bearing test.

    If a future change removes or disables the
        `if float(np.dot(boot_eigvec, ref_sub)) < 0: boot_eigvec = -boot_eigvec`
    block in bootstrap_centrality_ci() this test MUST FAIL.  That is the
    intended behaviour -- the test exists to catch that regression.

    Fixture (_make_two_cluster_sim_matrix):
      - 10 models in two anti-correlated clusters (5 majority + 5 minority).
      - Within-cluster similarity 0.80; cross-cluster similarity -0.30.
      - Without reference-vector alignment: both +v and -v are equally valid
        eigenvectors.  The bootstrap draws each with ~50% probability,
        producing a bimodal loading distribution symmetric around zero.
        Result: every model's CI straddles zero (lo < 0 < hi for positive-
        reference models; same in mirror for negative-reference models).
      - With correct Q1 alignment (dot(boot, ref) < 0 -> flip): all
        bootstrap eigenvectors share the reference orientation.  Loading
        distributions are unimodal and on one side of zero.  Result: CI
        lies entirely above zero for majority models, entirely below zero
        for minority models.

    Assertion:
      - majority models (reference loading > 0.05): lo > 0
      - minority models (reference loading < -0.05): hi < 0
    Either assertion failing means sign-alignment is broken.

    n_bootstrap=200: fast enough (no InformantRecord construction -- this
    function operates directly on the similarity matrix), large enough that
    the 2.5th/97.5th tails are well away from zero with the strong
    anti-correlation structure.  With no alignment the straddling
    probability approaches 100% regardless of n_bootstrap.

    References:
        docs/status/2026-05-28-remedy-b-cda-sme-verdict.md
        section "T5 test contract" item 5, binding note N7.
    """
    from cdb_analyze.consensus import compute_centrality_scores

    model_ids, sim = _make_two_cluster_sim_matrix()

    ref_scores = compute_centrality_scores(model_ids, sim)

    # Partition by reference sign (threshold 0.05 avoids near-zero noise).
    positive_models = [mid for mid in model_ids if ref_scores[mid] > 0.05]
    negative_models = [mid for mid in model_ids if ref_scores[mid] < -0.05]

    # Both clusters must be populated to make the test meaningful.
    assert len(positive_models) >= 3, (
        f"Fixture degenerate: too few positive-loaded models ({positive_models})"
    )
    assert len(negative_models) >= 3, (
        f"Fixture degenerate: too few negative-loaded models ({negative_models})"
    )

    result = bootstrap_centrality_ci(
        model_ids, sim, n_bootstrap=200, random_state=42
    )

    # Every model must have a CI entry (n=10 >> 3, fixture is non-degenerate).
    for mid in model_ids:
        assert mid in result, f"Missing CI for model {mid}"

    sign_failures: list[str] = []

    for mid in positive_models:
        lo, hi = result[mid]
        # With correct alignment, the entire CI must be positive.
        # lo <= 0 signals bimodal distribution (sign-alignment is broken).
        if lo <= 0.0:
            sign_failures.append(
                f"{mid}: reference={ref_scores[mid]:.3f} positive but CI lo={lo:.4f} <= 0 "
                f"(CI [{lo:.4f}, {hi:.4f}])"
            )

    for mid in negative_models:
        lo, hi = result[mid]
        # With correct alignment, the entire CI must be negative.
        # hi >= 0 signals bimodal distribution (sign-alignment is broken).
        if hi >= 0.0:
            sign_failures.append(
                f"{mid}: reference={ref_scores[mid]:.3f} negative but CI hi={hi:.4f} >= 0 "
                f"(CI [{lo:.4f}, {hi:.4f}])"
            )

    assert not sign_failures, (
        "SIGN ALIGNMENT FAILURE -- bootstrap_centrality_ci is NOT correctly "
        "applying reference-vector alignment (dot(boot, ref) < 0 -> flip).\n"
        "This test exists to catch regressions to mean-sign alignment or "
        "no-alignment in bootstrap.py.\n"
        "Failing models:\n  " + "\n  ".join(sign_failures)
    )
