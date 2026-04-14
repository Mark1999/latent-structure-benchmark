"""Tests for hierarchical clustering module."""

from __future__ import annotations

import numpy as np
from cdb_analyze.cluster import cluster_models


def test_cluster_two_groups():
    """Two clear clusters should be found."""
    # Models 0,1 are similar; model 2 is different
    sim = np.array([
        [1.0, 0.95, 0.1],
        [0.95, 1.0, 0.15],
        [0.1, 0.15, 1.0],
    ])
    result = cluster_models(["a", "b", "c"], sim)

    assert result.n_clusters == 2
    # a and b should be in the same cluster
    assert result.labels[0] == result.labels[1]
    assert result.labels[0] != result.labels[2]


def test_cluster_max_clusters():
    """Explicit max_clusters should be respected."""
    sim = np.array([
        [1.0, 0.9, 0.5, 0.1],
        [0.9, 1.0, 0.5, 0.1],
        [0.5, 0.5, 1.0, 0.4],
        [0.1, 0.1, 0.4, 1.0],
    ])
    result = cluster_models(["a", "b", "c", "d"], sim, max_clusters=2)
    assert result.n_clusters == 2


def test_cluster_single_model():
    """Single model returns trivial result."""
    result = cluster_models(["a"], np.array([[1.0]]))
    assert result.n_clusters == 1
    assert result.labels == [1]


def test_cluster_linkage_shape():
    """Linkage matrix should be (n-1, 4)."""
    sim = np.eye(3)
    result = cluster_models(["a", "b", "c"], sim)
    assert result.linkage_matrix.shape == (2, 4)
