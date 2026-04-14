"""Cross-version drift scoring via Procrustes analysis. See ARCHITECTURE.md §4.2.

Compares MDS coordinates of two model versions on shared item sets.
The drift score is the Procrustes distance after optimal rotation/scaling —
higher means the model's categorical structure shifted more between versions.

Unit of analysis: model_version_returned × collection_date (not model_id).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.spatial import procrustes


@dataclass(frozen=True)
class DriftScore:
    """Result of comparing two model versions."""

    model_id: str
    version_a: str
    version_b: str
    procrustes_distance: float
    n_shared_items: int


def compute_drift(
    coords_a: dict[str, tuple[float, float]],
    coords_b: dict[str, tuple[float, float]],
    *,
    model_id: str = "",
    version_a: str = "",
    version_b: str = "",
) -> DriftScore:
    """Compute Procrustes drift between two sets of item-level MDS coordinates.

    Args:
        coords_a: Item → (x, y) for version A.
        coords_b: Item → (x, y) for version B.
        model_id: Model identifier for the result.
        version_a: Version string for A.
        version_b: Version string for B.

    Returns:
        DriftScore with the Procrustes distance on shared items.
    """
    shared = sorted(set(coords_a.keys()) & set(coords_b.keys()))

    if len(shared) < 3:
        msg = (
            f"Only {len(shared)} shared items between versions; "
            "need at least 3 for Procrustes"
        )
        raise ValueError(msg)

    mat_a = np.array([coords_a[item] for item in shared], dtype=np.float64)
    mat_b = np.array([coords_b[item] for item in shared], dtype=np.float64)

    _, _, disparity = procrustes(mat_a, mat_b)

    return DriftScore(
        model_id=model_id,
        version_a=version_a,
        version_b=version_b,
        procrustes_distance=float(disparity),
        n_shared_items=len(shared),
    )


def compute_drift_matrix(
    version_coords: dict[str, dict[str, tuple[float, float]]],
    *,
    model_id: str = "",
) -> tuple[list[str], NDArray[np.float64]]:
    """Compute pairwise drift between all versions.

    Args:
        version_coords: Maps version_label → item → (x, y).
        model_id: Model identifier.

    Returns:
        (version_labels, drift_matrix) where drift_matrix[i][j]
        is the Procrustes distance between versions i and j.
    """
    versions = sorted(version_coords.keys())
    n = len(versions)
    matrix = np.zeros((n, n), dtype=np.float64)

    for i in range(n):
        for j in range(i + 1, n):
            try:
                score = compute_drift(
                    version_coords[versions[i]],
                    version_coords[versions[j]],
                    model_id=model_id,
                    version_a=versions[i],
                    version_b=versions[j],
                )
                matrix[i, j] = score.procrustes_distance
                matrix[j, i] = score.procrustes_distance
            except ValueError:
                # Not enough shared items — leave as 0
                pass

    return versions, matrix
