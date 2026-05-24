"""Hierarchical clustering of models and items. See ARCHITECTURE.md §4.2.

Provides Ward-linkage hierarchical clustering on the model×model
dissimilarity matrix from mds.py, and average-linkage (UPGMA)
hierarchical clustering on the term×term co-occurrence matrix from
cooccurrence.py. Output is a scipy linkage matrix suitable for
dendrogram rendering on the dashboard.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from cdb_core import CooccurrenceMatrix
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


@dataclass(frozen=True)
class TermClusterResult:
    """Hierarchical clustering output for a set of domain terms."""

    items: list[str]                        # ordered item list (same as matrix.items)
    linkage_matrix: NDArray[np.float64]     # scipy linkage format (n-1, 4)
    labels: list[int]                       # cluster label per item at the chosen cut
    n_clusters: int


def cluster_terms(
    matrix: CooccurrenceMatrix,
    *,
    n_clusters: int | None = None,
) -> TermClusterResult:
    """Hierarchical clustering on a term×term co-occurrence matrix.

    Average linkage (UPGMA) per Borgatti 1994 and CDA pile-sort analysis
    convention. Ward linkage was considered and rejected because its
    equal-cluster-size assumption does not match the empirical structure
    of pile-sort co-occurrence data.

    Per CDA SME rulings M2 and M3 (2026-05-24-phase9a-cda-sme-verdict.md):
    - Distance metric: 1 - cooccurrence (M3). Diagonal set to 0.0 after
      subtraction. This is the same distance space used by run_item_mds(),
      so AHC cluster boundaries correspond to MDS spatial neighbourhoods.
    - Linkage method: "average" (UPGMA) (M2). Borgatti (1994) and Spencer
      et al. (2016) both use average linkage for CDA pile-sort term
      clustering; it makes no distributional assumptions about cluster
      shape or size, unlike Ward.

    Args:
        matrix: A CooccurrenceMatrix (pooled or per-model). Must have at
            least 2 items.
        n_clusters: If set, cut the dendrogram to exactly this many
            clusters. If None, the biggest-gap heuristic (same as
            cluster_models()) is used.

    Returns:
        TermClusterResult with linkage matrix and per-item cluster labels.
    """
    items = matrix.items
    n = len(items)

    if n < 2:
        return TermClusterResult(
            items=items,
            linkage_matrix=np.empty((0, 4), dtype=np.float64),
            labels=[1] * n,
            n_clusters=1,
        )

    # Distance matrix: 1 - co-occurrence (M3)
    cooccur = np.array(matrix.matrix, dtype=np.float64)
    dissimilarity = 1.0 - cooccur
    # Ensure diagonal is exactly 0.0 (floating-point safety)
    np.fill_diagonal(dissimilarity, 0.0)
    # Ensure symmetry for squareform
    dissimilarity = (dissimilarity + dissimilarity.T) / 2.0

    condensed = squareform(dissimilarity, checks=False)

    # Average linkage (UPGMA) — M2 binding
    Z = linkage(condensed, method="average")

    if n_clusters is not None:
        labels = fcluster(Z, t=n_clusters, criterion="maxclust")
    else:
        # Biggest-gap heuristic (same as cluster_models)
        if len(Z) > 1:
            diffs = np.diff(Z[:, 2])
            cut_idx = int(np.argmax(diffs))
            threshold = (Z[cut_idx, 2] + Z[cut_idx + 1, 2]) / 2.0
            labels = fcluster(Z, t=threshold, criterion="distance")
        else:
            labels = np.array([1] * n)

    label_list = [int(x) for x in labels]
    return TermClusterResult(
        items=items,
        linkage_matrix=Z,
        labels=label_list,
        n_clusters=len(set(label_list)),
    )
