"""Uncertainty estimation via bootstrap resampling. See ARCHITECTURE.md §4.2.6.

For each (model, domain) with N raw runs, resample with replacement B times
and rerun the analysis pipeline on each sample. Outputs distributions:

- MDS 95% confidence ellipses (covariance of bootstrap coordinates).
- Similarity heatmap 95% CIs per cell.
- Consensus score CI.

Term-level bootstrap functions (Phase 9a T4):

- bootstrap_term_mds_ellipses(): per-term 95% CI ellipses on the pooled
  term MDS, resampling MODELS with replacement (Register 2). B=200.
- bootstrap_branch_stability(): per-internal-node bootstrap proportion (BP)
  for the term AHC dendrogram. B=200.

CIs reflect between-model structural variance only (not within-model run
variance, which is absorbed into each model's consensus matrix). Per CDA
SME M4a (2026-05-24-phase9a-cda-sme-verdict.md).
"""

from __future__ import annotations

import numpy as np
from cdb_core import BootstrapEllipse, CooccurrenceMatrix, InformantRecord
from numpy.typing import NDArray
from scipy.cluster.hierarchy import linkage as scipy_linkage
from scipy.spatial import procrustes
from scipy.spatial.distance import squareform

from cdb_analyze.cooccurrence import build_cooccurrence_matrix
from cdb_analyze.mds import compute_cross_model_similarity, run_item_mds, run_mds


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


# ──────────────────────────────────────────────────────────────────────
# Phase 9a T4 — term-level bootstrap (CDA SME M4/M5 binding)
# ──────────────────────────────────────────────────────────────────────


def _pool_resampled_matrices(
    resampled_model_ids: list[str],
    per_model_matrices: dict[str, CooccurrenceMatrix],
    union_items: list[str],
) -> CooccurrenceMatrix:
    """Pool a resampled (with-replacement) set of model matrices.

    Implements the same equal-weight-per-model formula as
    ``build_pooled_cooccurrence_matrix()``:

        pooled[i][j] = (1/M) * sum_over_resampled_models(cooccurrence[i][j])

    M is the number of entries in ``resampled_model_ids`` (which may include
    duplicates when a model is drawn more than once). Items absent from a
    model's matrix contribute 0.0 to the numerator but are still counted in
    the denominator (M stays fixed). This matches the CDA SME M1 contract.

    Args:
        resampled_model_ids: Length-M list of model IDs (with replacement).
        per_model_matrices: Pre-computed per-model consensus matrices.
        union_items: Sorted union item list (the reference item ordering).

    Returns:
        A CooccurrenceMatrix on ``union_items`` with pooled values.
    """
    n_items = len(union_items)
    M = len(resampled_model_ids)
    pooled = np.zeros((n_items, n_items), dtype=np.float64)

    for mid in resampled_model_ids:
        mat = per_model_matrices[mid]
        local_idx: dict[str, int] = {item: i for i, item in enumerate(mat.items)}

        for i_global, item_i in enumerate(union_items):
            i_local = local_idx.get(item_i)
            if i_local is None:
                continue
            for j_global, item_j in enumerate(union_items):
                j_local = local_idx.get(item_j)
                if j_local is None:
                    continue
                pooled[i_global, j_global] += mat.matrix[i_local][j_local]

    # Normalize by M (always M, not number of models that produced the item)
    pooled /= M

    # Build a minimal CooccurrenceMatrix shell using the first model's ref
    first_mat = per_model_matrices[resampled_model_ids[0]]
    from datetime import UTC, datetime

    from cdb_core import ModelRef

    pooled_ref = ModelRef(
        provider="anthropic",
        model_id="pooled_bootstrap",
        family="pooled",
        origin="us",
        open_weights=False,
        collection_method="anthropic_api",
        quantization=None,
        release_date=datetime.now(UTC).date(),
        version_label="bootstrap",
    )
    return CooccurrenceMatrix(
        domain_slug=first_mat.domain_slug,
        model=pooled_ref,
        items=union_items,
        matrix=pooled.tolist(),
    )


def bootstrap_term_mds_ellipses(
    per_model_matrices: dict[str, CooccurrenceMatrix],
    reference_coordinates: dict[str, tuple[float, float]],
    reference_items: list[str],
    n_bootstrap: int = 200,
    random_state: int | None = None,
) -> dict[str, BootstrapEllipse]:
    """Bootstrap per-term 95% confidence ellipses on the pooled term MDS.

    Implements CDA SME M4 (Register 2 term-level bootstrap, 2026-05-24-
    phase9a-cda-sme-verdict.md):

    Resampling unit: models (the Register 2 informants). Each bootstrap
    iteration draws M model IDs with replacement from ``per_model_matrices``.
    The within-model run-to-run variance is already absorbed into each model's
    pre-computed consensus matrix; the bootstrap captures between-model
    structural variance only.

    Per-iteration algorithm:
    1. Draw M model IDs with replacement.
    2. Pool the resampled model matrices (equal-weight, M denominator).
    3. Run item MDS on the pooled matrix.
    4. Procrustes-align the bootstrap coordinates to the reference solution.
    5. Record each term's (x, y).

    B=200 is sufficient for 95% CI estimation on ~25-item MDS per CDA SME F4.

    **Annotation (M4a):** The returned ellipses reflect between-model
    structural variance only. They do NOT capture within-model run-to-run
    variance. Dashboard / methods copy must state: "Term position confidence
    reflects agreement across models, not within-model sampling variance."

    Args:
        per_model_matrices: One CooccurrenceMatrix per model (pre-computed
            consensus matrices, typically from build_cooccurrence_matrix()).
        reference_coordinates: The reference (full-data pooled) term MDS
            coordinates, mapping item name to (x, y). Items in this dict
            are the items whose ellipses will be computed.
        reference_items: Sorted union item list in the same order used by
            the reference MDS (must match keys in reference_coordinates).
        n_bootstrap: Number of bootstrap iterations (default 200, per F4).
        random_state: Optional RNG seed for reproducibility.

    Returns:
        dict mapping item name to BootstrapEllipse for each item that appears
        in at least one bootstrap iteration's pooled matrix.
    """
    if not per_model_matrices:
        msg = "per_model_matrices must not be empty"
        raise ValueError(msg)
    if not reference_items:
        msg = "reference_items must not be empty"
        raise ValueError(msg)

    rng = np.random.default_rng(random_state)
    model_ids = sorted(per_model_matrices.keys())
    M = len(model_ids)

    # Build reference coordinate array for Procrustes alignment.
    # Only items that appear in both reference_coordinates and reference_items
    # are tracked. We use reference_items as the canonical ordering.
    ref_item_list = [it for it in reference_items if it in reference_coordinates]
    n_items = len(ref_item_list)

    if n_items < 3:
        # Not enough items for MDS; return empty ellipses
        return {}

    # Accumulate per-item bootstrap coordinates.
    # boot_item_coords[item] grows across valid iterations.
    boot_item_coords: dict[str, list[tuple[float, float]]] = {
        it: [] for it in ref_item_list
    }

    for _ in range(n_bootstrap):
        # Step 1: resample M model IDs with replacement
        sampled_ids = [model_ids[i] for i in rng.integers(0, M, size=M)]

        try:
            # Step 2: pool resampled matrices
            pooled_mat = _pool_resampled_matrices(
                sampled_ids, per_model_matrices, reference_items,
            )

            # Step 3: item MDS on the pooled matrix
            b_coords_dict = run_item_mds(pooled_mat)

            # Only keep items that appear in both the reference and this
            # bootstrap iteration's MDS output.
            common_items = [it for it in ref_item_list if it in b_coords_dict]
            if len(common_items) < 3:
                # Too few shared items for meaningful alignment; skip iteration
                continue

            # Build aligned arrays (only shared items, same order)
            ref_sub = np.array(
                [reference_coordinates[it] for it in common_items],
                dtype=np.float64,
            )
            b_sub = np.array(
                [b_coords_dict[it] for it in common_items],
                dtype=np.float64,
            )

            # Step 4: Procrustes-align bootstrap coordinates to reference
            _, b_aligned, _ = procrustes(ref_sub, b_sub)

            # Step 5: record aligned coordinates for each common item
            for idx, it in enumerate(common_items):
                boot_item_coords[it].append(
                    (float(b_aligned[idx, 0]), float(b_aligned[idx, 1]))
                )

        except (ValueError, np.linalg.LinAlgError):
            # Degenerate bootstrap resample — skip this iteration
            continue

    # Fit ellipses from the recorded coordinate distributions
    ellipses: dict[str, BootstrapEllipse] = {}
    for it in ref_item_list:
        pts_list = boot_item_coords[it]
        if len(pts_list) < 2:
            # Not enough observations to estimate a covariance; emit a
            # degenerate zero-size ellipse at the reference position
            cx, cy = reference_coordinates[it]
            ellipses[it] = BootstrapEllipse(
                center=(cx, cy),
                semi_major=0.0,
                semi_minor=0.0,
                rotation_rad=0.0,
                n_bootstrap=len(pts_list),
            )
            continue

        pts_arr = np.array(pts_list, dtype=np.float64)
        ellipses[it] = _fit_ellipse(pts_arr, len(pts_list))

    return ellipses


def _extract_bipartitions(
    linkage_matrix: NDArray[np.float64],
    n_items: int,
) -> list[frozenset[int]]:
    """Extract the set of left-subtree item indices for each internal node.

    Each row in the scipy linkage matrix merges two clusters. The left
    bipartition for internal node k is the set of original item indices
    that belong to the left subtree rooted at that merge step.

    We represent each bipartition as the SMALLER of {left, right} to
    ensure canonical form for set-equality comparison across bootstrap
    iterations (any bipartition and its complement define the same split).

    Args:
        linkage_matrix: scipy linkage matrix of shape (n_items - 1, 4).
        n_items: Number of original items (leaf nodes).

    Returns:
        List of frozensets, one per internal node (len = n_items - 1).
        Each frozenset contains the original item indices of the smaller
        partition of the split.
    """
    n_merges = len(linkage_matrix)
    # clusters[k] = frozenset of original item indices in cluster k
    clusters: dict[int, frozenset[int]] = {i: frozenset({i}) for i in range(n_items)}

    bipartitions: list[frozenset[int]] = []
    for merge_idx in range(n_merges):
        c1 = int(linkage_matrix[merge_idx, 0])
        c2 = int(linkage_matrix[merge_idx, 1])
        new_cluster = clusters[c1] | clusters[c2]
        new_id = n_items + merge_idx
        clusters[new_id] = new_cluster

        # Canonical form: always store the smaller partition
        left = clusters[c1]
        right = clusters[c2]
        canonical = left if len(left) <= len(right) else right
        bipartitions.append(canonical)

    return bipartitions


def bootstrap_branch_stability(
    per_model_matrices: dict[str, CooccurrenceMatrix],
    reference_linkage: NDArray[np.float64],
    reference_items: list[str],
    n_bootstrap: int = 200,
    random_state: int | None = None,
) -> list[float]:
    """Compute bootstrap proportion (BP) for each internal node in the AHC.

    Implements CDA SME M5 (simple bootstrap proportion, not multiscale AU).
    For each internal node in the reference linkage tree, BP is the fraction
    of bootstrap iterations in which the exact bipartition defined by that
    node appears in the bootstrap tree.

    Resampling unit: models with replacement (same as bootstrap_term_mds_
    ellipses). Each bootstrap iteration:
    1. Draws M model IDs with replacement.
    2. Pools the resampled model matrices.
    3. Runs UPGMA linkage on the pooled matrix (distance = 1 - cooccurrence).
    4. Extracts the set of bipartitions from the bootstrap tree.
    5. For each reference bipartition, checks if it appears in the bootstrap.

    BP = count / B across B iterations.

    **Display note (M5a):** Dashboard labels this as "bootstrap support (%)"
    not "AU p-value." Branches below 70% support are rendered with dashed
    lines and reduced opacity (UI/UX agent decides visual treatment; the
    threshold 70% is a display threshold, not a statistical gate).

    Args:
        per_model_matrices: One CooccurrenceMatrix per model.
        reference_linkage: The reference linkage matrix (numpy array of
            shape (n_items - 1, 4), from scipy linkage with method="average").
        reference_items: Sorted item list matching the reference linkage
            (same ordering as the pooled CooccurrenceMatrix used for AHC).
        n_bootstrap: Number of bootstrap iterations (default 200, per F4).
        random_state: Optional RNG seed for reproducibility.

    Returns:
        List of BP values (floats in [0, 1]), one per internal node in the
        reference linkage, in linkage row order (row 0 = first merge, etc.).
        Returns an empty list if ``reference_linkage`` has 0 rows.
    """
    if len(reference_linkage) == 0:
        return []
    if not per_model_matrices:
        msg = "per_model_matrices must not be empty"
        raise ValueError(msg)

    rng = np.random.default_rng(random_state)
    model_ids = sorted(per_model_matrices.keys())
    M = len(model_ids)
    n_items = len(reference_items)

    # Extract reference bipartitions (one per internal node)
    ref_bipartitions = _extract_bipartitions(reference_linkage, n_items)
    n_nodes = len(ref_bipartitions)

    # Count how many bootstrap iterations contain each reference bipartition
    bp_counts = np.zeros(n_nodes, dtype=np.int64)

    for _ in range(n_bootstrap):
        # Resample M model IDs with replacement
        sampled_ids = [model_ids[i] for i in rng.integers(0, M, size=M)]

        try:
            # Pool the resampled matrices
            pooled_mat = _pool_resampled_matrices(
                sampled_ids, per_model_matrices, reference_items,
            )

            # Build distance matrix: 1 - cooccurrence (M3)
            cooccur = np.array(pooled_mat.matrix, dtype=np.float64)
            dissimilarity = 1.0 - cooccur
            np.fill_diagonal(dissimilarity, 0.0)
            dissimilarity = (dissimilarity + dissimilarity.T) / 2.0
            condensed = squareform(dissimilarity, checks=False)

            # Run UPGMA linkage
            Z_boot = scipy_linkage(condensed, method="average")

            # Extract bipartitions from bootstrap tree
            boot_bipartitions: set[frozenset[int]] = set(
                _extract_bipartitions(Z_boot, n_items)
            )

            # Check each reference bipartition
            for node_idx, ref_bp in enumerate(ref_bipartitions):
                if ref_bp in boot_bipartitions:
                    bp_counts[node_idx] += 1

        except (ValueError, np.linalg.LinAlgError):
            # Degenerate resample — skip
            continue

    return [float(c) / n_bootstrap for c in bp_counts]
