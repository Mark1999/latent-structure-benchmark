"""Uncertainty estimation via bootstrap resampling. See ARCHITECTURE.md §4.2.6.

For each (model, domain) with N raw runs, resample with replacement B times
and rerun the analysis pipeline on each sample. Outputs distributions:

- MDS 95% confidence ellipses (covariance of bootstrap coordinates).
- Similarity heatmap 95% CIs per cell.
- Consensus score CI.
"""

from __future__ import annotations

import numpy as np
from cdb_core import BootstrapEllipse, CooccurrenceMatrix, InformantRecord
from numpy.typing import NDArray
from scipy.spatial import procrustes

from cdb_analyze.cooccurrence import build_cooccurrence_matrix
from cdb_analyze.mds import compute_cross_model_similarity, run_mds


def bootstrap_mds_ellipses(
    records_by_model: dict[str, list[InformantRecord]],
    *,
    n_bootstrap: int = 500,
    random_state: int = 42,
) -> tuple[
    dict[str, tuple[float, float]],
    dict[str, BootstrapEllipse],
    NDArray[np.float64],
    NDArray[np.float64],
]:
    """Bootstrap MDS coordinates and compute 95% confidence ellipses.

    Args:
        records_by_model: Maps model_id to its list of InformantRecords.
        n_bootstrap: Number of bootstrap resamples (default 500).
        random_state: RNG seed for reproducibility.

    Returns:
        (coordinates, ellipses, similarity_matrix, similarity_ci)
        - coordinates: model_id → (x, y) mean MDS position
        - ellipses: model_id → BootstrapEllipse
        - similarity_matrix: mean cross-model similarity
        - similarity_ci: shape (n, n, 2) lower/upper 95% CI per cell
    """
    rng = np.random.default_rng(random_state)
    model_ids = sorted(records_by_model.keys())
    n_models = len(model_ids)

    if n_models < 2:
        msg = "Need at least 2 models for bootstrap MDS"
        raise ValueError(msg)

    # Compute reference (full-data) solution
    ref_matrices = _build_matrices(records_by_model, model_ids)
    ref_model_ids, ref_sim = compute_cross_model_similarity(ref_matrices)
    ref_coords = run_mds(ref_sim)

    # Collect bootstrap samples
    boot_coords = np.zeros((n_bootstrap, n_models, 2))
    boot_sims = np.zeros((n_bootstrap, n_models, n_models))

    for b in range(n_bootstrap):
        # Resample runs with replacement per model
        resampled = {}
        for mid in model_ids:
            runs = records_by_model[mid]
            indices = rng.integers(0, len(runs), size=len(runs))
            resampled[mid] = [runs[i] for i in indices]

        try:
            b_matrices = _build_matrices(resampled, model_ids)
            _, b_sim = compute_cross_model_similarity(b_matrices)
            b_coords = run_mds(b_sim)

            # Procrustes alignment to reference
            _, aligned, _ = procrustes(ref_coords, b_coords)
            boot_coords[b] = aligned
            boot_sims[b] = b_sim
        except (ValueError, np.linalg.LinAlgError):
            # Degenerate resample — use reference as fallback
            boot_coords[b] = ref_coords
            boot_sims[b] = ref_sim

    # Mean coordinates
    mean_coords = np.mean(boot_coords, axis=0)
    coordinates = {
        mid: (float(mean_coords[i, 0]), float(mean_coords[i, 1]))
        for i, mid in enumerate(model_ids)
    }

    # Ellipses from covariance of bootstrap coordinates
    ellipses = {}
    for i, mid in enumerate(model_ids):
        pts = boot_coords[:, i, :]  # (B, 2)
        ellipses[mid] = _fit_ellipse(pts, n_bootstrap)

    # Similarity CI: 2.5th and 97.5th percentile per cell
    sim_mean = np.mean(boot_sims, axis=0)
    sim_ci = np.zeros((n_models, n_models, 2))
    sim_ci[:, :, 0] = np.percentile(boot_sims, 2.5, axis=0)
    sim_ci[:, :, 1] = np.percentile(boot_sims, 97.5, axis=0)

    return coordinates, ellipses, sim_mean, sim_ci


def _build_matrices(
    records_by_model: dict[str, list[InformantRecord]],
    model_ids: list[str],
) -> list[CooccurrenceMatrix]:
    """Build co-occurrence matrices for each model."""
    return [
        build_cooccurrence_matrix(records_by_model[mid])
        for mid in model_ids
    ]


def _fit_ellipse(
    pts: NDArray[np.float64],
    n_bootstrap: int,
) -> BootstrapEllipse:
    """Fit a 95% confidence ellipse from bootstrap coordinate distribution."""
    center = (float(np.mean(pts[:, 0])), float(np.mean(pts[:, 1])))

    cov = np.cov(pts.T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    # Sort descending
    order = eigenvalues.argsort()[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]

    # 95% chi-squared critical value for 2 DOF ≈ 5.991
    chi2_95 = 5.991
    semi_major = float(np.sqrt(eigenvalues[0] * chi2_95))
    semi_minor = float(np.sqrt(max(eigenvalues[1], 0.0) * chi2_95))

    rotation_rad = float(np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0]))

    return BootstrapEllipse(
        center=center,
        semi_major=semi_major,
        semi_minor=semi_minor,
        rotation_rad=rotation_rad,
        n_bootstrap=n_bootstrap,
    )
