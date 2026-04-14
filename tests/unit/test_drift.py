"""Tests for drift scoring module."""

from __future__ import annotations

import numpy as np
import pytest
from cdb_analyze.drift import compute_drift, compute_drift_matrix


def test_drift_identical_coords():
    """Identical coordinates should have zero drift."""
    coords = {"a": (0.0, 0.0), "b": (1.0, 0.0), "c": (0.0, 1.0)}
    score = compute_drift(coords, coords, model_id="test")
    assert score.procrustes_distance == pytest.approx(0.0, abs=1e-10)
    assert score.n_shared_items == 3


def test_drift_different_coords():
    """Different coordinates should have positive drift."""
    coords_a = {"a": (0.0, 0.0), "b": (1.0, 0.0), "c": (0.0, 1.0)}
    coords_b = {"a": (0.0, 0.0), "b": (0.0, 1.0), "c": (1.0, 0.0)}
    score = compute_drift(coords_a, coords_b, model_id="test")
    assert score.procrustes_distance > 0


def test_drift_too_few_shared():
    coords_a = {"a": (0.0, 0.0), "b": (1.0, 0.0)}
    coords_b = {"c": (0.0, 0.0), "d": (1.0, 0.0)}
    with pytest.raises(ValueError, match="at least 3"):
        compute_drift(coords_a, coords_b)


def test_drift_partial_overlap():
    """Drift should compute on shared items only."""
    coords_a = {"a": (0.0, 0.0), "b": (1.0, 0.0), "c": (0.0, 1.0), "d": (1.0, 1.0)}
    coords_b = {"a": (0.0, 0.0), "b": (1.0, 0.0), "c": (0.0, 1.0), "e": (2.0, 2.0)}
    score = compute_drift(coords_a, coords_b)
    assert score.n_shared_items == 3
    assert score.procrustes_distance == pytest.approx(0.0, abs=1e-10)


def test_drift_matrix():
    """Drift matrix should be symmetric with zero diagonal."""
    v1 = {"a": (0.0, 0.0), "b": (1.0, 0.0), "c": (0.0, 1.0)}
    v2 = {"a": (0.0, 0.0), "b": (0.5, 0.5), "c": (0.5, -0.5)}
    v3 = {"a": (1.0, 1.0), "b": (0.0, 0.0), "c": (-1.0, -1.0)}

    versions, matrix = compute_drift_matrix(
        {"v1": v1, "v2": v2, "v3": v3}, model_id="test",
    )

    assert len(versions) == 3
    assert matrix.shape == (3, 3)
    # Diagonal should be zero
    np.testing.assert_array_almost_equal(np.diag(matrix), [0, 0, 0])
    # Symmetric
    np.testing.assert_array_almost_equal(matrix, matrix.T)
