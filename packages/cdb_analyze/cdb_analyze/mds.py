"""Multidimensional scaling via sklearn. See ARCHITECTURE.md §4.2.

Two modes:
  (a) Item-level MDS: item×item co-occurrence → 2D cognitive map per model.
  (b) Model-level MDS: model×model similarity → 2D cultural space.

Cross-model similarity is Mantel-style correlation between co-occurrence
matrices on the shared item set, rescaled from [-1, 1] to [0, 1].
"""

from __future__ import annotations

import numpy as np
from cdb_core import CooccurrenceMatrix
from numpy.typing import NDArray
from sklearn.manifold import MDS


def compute_cross_model_similarity(
    matrices: list[CooccurrenceMatrix],
) -> tuple[list[str], NDArray[np.float64]]:
    """Compute pairwise Mantel-style correlation between models.

    Args:
        matrices: One CooccurrenceMatrix per model. Must share at least
            some items; similarity is computed on the intersection.

    Returns:
        (model_ids, similarity_matrix) where similarity_matrix[i][j]
        is the rescaled Mantel correlation between models i and j,
        range [0, 1]. Diagonal is 1.0.
    """
    n = len(matrices)
    if n < 2:
        msg = f"Need at least 2 models for cross-model similarity, got {n}"
        raise ValueError(msg)

    model_ids = [m.model.model_id for m in matrices]

    # Find shared items across all matrices
    shared_items = set(matrices[0].items)
    for m in matrices[1:]:
        shared_items &= set(m.items)
    shared = sorted(shared_items)

    if len(shared) < 3:
        msg = (
            f"Only {len(shared)} shared items across models; "
            "need at least 3 for meaningful MDS"
        )
        raise ValueError(msg)

    # Extract sub-matrices for shared items, upper triangle only
    def _upper_tri(mat: CooccurrenceMatrix) -> NDArray[np.float64]:
        idx = {item: i for i, item in enumerate(mat.items)}
        k = len(shared)
        vals = []
        for i in range(k):
            for j in range(i + 1, k):
                ri, rj = idx[shared[i]], idx[shared[j]]
                vals.append(mat.matrix[ri][rj])
        return np.array(vals, dtype=np.float64)

    vectors = [_upper_tri(m) for m in matrices]

    # Pairwise Pearson correlation, rescaled to [0, 1]
    sim = np.ones((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(i + 1, n):
            r = np.corrcoef(vectors[i], vectors[j])[0, 1]
            # Handle NaN (constant vectors) as 0 similarity
            if np.isnan(r):
                r = 0.0
            scaled = (r + 1.0) / 2.0  # [-1,1] → [0,1]
            sim[i, j] = scaled
            sim[j, i] = scaled

    return model_ids, sim


def run_mds(
    similarity: NDArray[np.float64],
    *,
    n_components: int = 2,
    random_state: int = 42,
) -> NDArray[np.float64]:
    """Run MDS on a similarity matrix.

    Args:
        similarity: Square symmetric matrix, values in [0, 1].
            1.0 = identical, 0.0 = maximally different.
        n_components: Number of output dimensions (default 2).
        random_state: For reproducibility.

    Returns:
        Coordinate array of shape (n_models, n_components).
    """
    dissimilarity = 1.0 - similarity
    np.fill_diagonal(dissimilarity, 0.0)

    mds = MDS(
        n_components=n_components,
        metric="precomputed",
        init="random",
        n_init=4,
        random_state=random_state,
        normalized_stress="auto",
    )
    result: NDArray[np.float64] = mds.fit_transform(dissimilarity)
    return result


def run_item_mds(
    matrix: CooccurrenceMatrix,
    *,
    n_components: int = 2,
    random_state: int = 42,
) -> dict[str, tuple[float, float]]:
    """Run item-level MDS on a single model's co-occurrence matrix.

    Args:
        matrix: A CooccurrenceMatrix for one model.

    Returns:
        Dict mapping item name to (x, y) coordinate.
    """
    sim = np.array(matrix.matrix, dtype=np.float64)
    coords = run_mds(sim, n_components=n_components, random_state=random_state)

    return {
        item: (float(coords[i, 0]), float(coords[i, 1]))
        for i, item in enumerate(matrix.items)
    }


def run_item_mds_with_stress(
    matrix: CooccurrenceMatrix,
    *,
    n_components: int = 2,
    random_state: int = 42,
) -> tuple[dict[str, tuple[float, float]], float]:
    """Like run_item_mds but also returns the MDS stress value."""
    sim = np.array(matrix.matrix, dtype=np.float64)
    dissimilarity = 1.0 - sim
    np.fill_diagonal(dissimilarity, 0.0)

    mds = MDS(
        n_components=n_components,
        metric="precomputed",
        init="random",
        n_init=4,
        random_state=random_state,
        normalized_stress="auto",
    )
    coords: NDArray[np.float64] = mds.fit_transform(dissimilarity)
    stress = float(mds.stress_)

    item_coords = {
        item: (float(coords[i, 0]), float(coords[i, 1]))
        for i, item in enumerate(matrix.items)
    }
    return item_coords, stress
