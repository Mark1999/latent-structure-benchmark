"""Tests for MDS module. Uses synthetic matrices with known structure."""

from __future__ import annotations

from datetime import date

import numpy as np
import pytest
from cdb_analyze.mds import (
    compute_cross_model_similarity,
    run_item_mds,
    run_mds,
)
from cdb_core import CooccurrenceMatrix, ModelRef


def _model_ref(model_id: str = "model-a") -> ModelRef:
    return ModelRef(
        provider="anthropic",
        model_id=model_id,
        family="test",
        origin="us",
        open_weights=False,
        collection_method="anthropic_api",
        quantization=None,
        release_date=date(2026, 1, 1),
        version_label="1.0",
    )


def _cooccurrence(
    model_id: str,
    items: list[str],
    matrix: list[list[float]],
) -> CooccurrenceMatrix:
    return CooccurrenceMatrix(
        domain_slug="family",
        model=_model_ref(model_id),
        items=items,
        matrix=matrix,
    )


def test_cross_model_similarity_identical_matrices():
    """Two identical matrices should have similarity ~1.0."""
    items = ["a", "b", "c", "d"]
    mat = [
        [1.0, 0.8, 0.2, 0.1],
        [0.8, 1.0, 0.3, 0.2],
        [0.2, 0.3, 1.0, 0.9],
        [0.1, 0.2, 0.9, 1.0],
    ]
    m1 = _cooccurrence("model-a", items, mat)
    m2 = _cooccurrence("model-b", items, mat)

    model_ids, sim = compute_cross_model_similarity([m1, m2])

    assert model_ids == ["model-a", "model-b"]
    assert sim[0, 1] == pytest.approx(1.0, abs=0.01)
    assert sim[1, 0] == pytest.approx(1.0, abs=0.01)


def test_cross_model_similarity_different_matrices():
    """Inverted matrices should have low similarity."""
    items = ["a", "b", "c", "d"]
    mat_a = [
        [1.0, 1.0, 0.0, 0.0],
        [1.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 1.0],
        [0.0, 0.0, 1.0, 1.0],
    ]
    mat_b = [
        [1.0, 0.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 1.0],
        [1.0, 0.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 1.0],
    ]
    m1 = _cooccurrence("model-a", items, mat_a)
    m2 = _cooccurrence("model-b", items, mat_b)

    _, sim = compute_cross_model_similarity([m1, m2])

    # Should be low — inverted structure
    assert sim[0, 1] < 0.5


def test_cross_model_similarity_diagonal():
    """Diagonal should be 1.0."""
    items = ["a", "b", "c", "d"]
    mat = [[1.0, 0.5, 0.5, 0.5]] * 4
    m1 = _cooccurrence("model-a", items, mat)
    m2 = _cooccurrence("model-b", items, mat)

    _, sim = compute_cross_model_similarity([m1, m2])

    assert sim[0, 0] == 1.0
    assert sim[1, 1] == 1.0


def test_cross_model_similarity_too_few_models():
    items = ["a", "b", "c"]
    mat = [[1.0, 0.5, 0.5], [0.5, 1.0, 0.5], [0.5, 0.5, 1.0]]
    m1 = _cooccurrence("model-a", items, mat)

    with pytest.raises(ValueError, match="at least 2"):
        compute_cross_model_similarity([m1])


def test_run_mds_shape():
    """MDS should return (n, 2) array."""
    sim = np.array([
        [1.0, 0.8, 0.2],
        [0.8, 1.0, 0.3],
        [0.2, 0.3, 1.0],
    ])
    coords = run_mds(sim)
    assert coords.shape == (3, 2)


def test_run_mds_similar_models_close():
    """Models with high similarity should be close in MDS space."""
    sim = np.array([
        [1.0, 0.95, 0.1],
        [0.95, 1.0, 0.15],
        [0.1, 0.15, 1.0],
    ])
    coords = run_mds(sim)

    # Distance between models 0 and 1 should be < distance to model 2
    d01 = np.linalg.norm(coords[0] - coords[1])
    d02 = np.linalg.norm(coords[0] - coords[2])
    assert d01 < d02


def test_run_item_mds():
    """Item MDS should return coordinates for each item."""
    items = ["a", "b", "c"]
    mat = [[1.0, 0.9, 0.1], [0.9, 1.0, 0.2], [0.1, 0.2, 1.0]]
    matrix = _cooccurrence("model-a", items, mat)

    coords = run_item_mds(matrix)
    assert set(coords.keys()) == {"a", "b", "c"}
    for v in coords.values():
        assert len(v) == 2
