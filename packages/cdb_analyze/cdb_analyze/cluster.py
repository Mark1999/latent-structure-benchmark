"""Hierarchical clustering of models and items. See ARCHITECTURE.md §4.2.

Provides Ward-linkage hierarchical clustering on the model×model
dissimilarity matrix from mds.py. Output is a scipy linkage matrix
suitable for dendrogram rendering on the dashboard.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform


@dataclass(frozen=True)
class ClusterResult:
    """Hierarchical clustering output for a set of models."""

    model_ids: list[str]
    linkage_matrix: NDArray[np.float64]  # scipy linkage format (n-1, 4)
    labels: list[int]  # cluster label per model at the chosen cut
    n_clusters: int


def cluster_models(
    model_ids: list[str],
    similarity: NDArray[np.float64],
    *,
    method: str = "ward",
    max_clusters: int | None = None,
    distance_threshold: float | None = None,
) -> ClusterResult:
    """Hierarchical clustering on a model×model similarity matrix.

    Args:
        model_ids: Model identifiers, one per row/col.
        similarity: Square symmetric matrix in [0, 1]. 1 = identical.
        method: Linkage method (default "ward").
        max_clusters: If set, cut the dendrogram to this many clusters.
        distance_threshold: If set, cut at this distance. Ignored if
            max_clusters is provided.

    Returns:
        ClusterResult with linkage matrix and per-model cluster labels.
    """
    n = len(model_ids)
    if n < 2:
        return ClusterResult(
            model_ids=model_ids,
            linkage_matrix=np.empty((0, 4), dtype=np.float64),
            labels=[1] * n,
            n_clusters=1,
        )

    dissimilarity = 1.0 - similarity
    np.fill_diagonal(dissimilarity, 0.0)
    # Ensure symmetry for squareform
    dissimilarity = (dissimilarity + dissimilarity.T) / 2.0

    condensed = squareform(dissimilarity, checks=False)
    Z = linkage(condensed, method=method)

    if max_clusters is not None:
        labels = fcluster(Z, t=max_clusters, criterion="maxclust")
    elif distance_threshold is not None:
        labels = fcluster(Z, t=distance_threshold, criterion="distance")
    else:
        # Default: cut where the biggest gap in merge distances occurs
        if len(Z) > 1:
            diffs = np.diff(Z[:, 2])
            cut_idx = int(np.argmax(diffs))
            threshold = (Z[cut_idx, 2] + Z[cut_idx + 1, 2]) / 2.0
            labels = fcluster(Z, t=threshold, criterion="distance")
        else:
            labels = np.array([1] * n)

    label_list = [int(x) for x in labels]
    return ClusterResult(
        model_ids=model_ids,
        linkage_matrix=Z,
        labels=label_list,
        n_clusters=len(set(label_list)),
    )
