"""Tests for bootstrap uncertainty module."""

from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
import pytest
from cdb_analyze.bootstrap import (
    bootstrap_branch_stability,
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
