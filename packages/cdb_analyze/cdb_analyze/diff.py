"""Pairwise cross-model measures: Mantel test and Nolan Index.

See ARCHITECTURE.md §4.2 and docs/SME_REVIEW.md §1.2, §2.2.

These measures complement the full-matrix Register 2 ``g2_signal``
dispersion-permutation test in ``gates.py``. Where ``g2_signal`` asks
"is the whole inter-model structure non-random?", the Mantel test and
Nolan Index ask pairwise questions: how correlated are two specific
models' structures (Mantel) and how different are their proportional
emphases (Nolan).

Both are reported in ``DomainResult.cross_model_mantel`` and
``DomainResult.cross_model_nolan`` for use in the dashboard's pairwise
comparison table.
"""

from __future__ import annotations

import numpy as np
from cdb_core import MantelPair, NolanIndexPair
from numpy.typing import NDArray

# ---------------------------------------------------------------------------
# Mantel test (Mantel 1967)
# ---------------------------------------------------------------------------

def mantel_test(
    mat_a: NDArray[np.float64],
    mat_b: NDArray[np.float64],
    *,
    n_permutations: int = 999,
    random_state: int = 42,
) -> tuple[float, float]:
    """Classical permutation-based Mantel test between two square matrices.

    Assumes ``mat_a`` and ``mat_b`` are both symmetric (n × n) matrices
    defined on the same item order. Uses the upper triangle (excluding
    the diagonal) as the vector of observations. The null is generated
    by permuting rows and columns of ``mat_b`` simultaneously (which
    preserves the symmetry of the matrix while destroying any shared
    ordering with ``mat_a``).

    Args:
        mat_a: Symmetric n×n matrix — typically a co-occurrence matrix
            on the shared item set.
        mat_b: Symmetric n×n matrix on the same item order.
        n_permutations: Size of the null distribution.
        random_state: RNG seed.

    Returns:
        ``(r, p_value)`` where ``r`` is the Pearson correlation between
        the upper triangles and ``p_value`` is the one-sided probability
        of observing ``r`` or greater under the null.
    """
    if mat_a.shape != mat_b.shape:
        msg = f"Matrix shapes must match: {mat_a.shape} vs {mat_b.shape}"
        raise ValueError(msg)
    n = mat_a.shape[0]
    if n < 3:
        msg = f"Need n ≥ 3 for a Mantel test; got n={n}"
        raise ValueError(msg)

    iu = np.triu_indices(n, k=1)
    a_vec = mat_a[iu]
    b_vec = mat_b[iu]

    obs_r = _pearson(a_vec, b_vec)

    rng = np.random.default_rng(random_state)
    n_exceed = 0
    for _ in range(n_permutations):
        perm = rng.permutation(n)
        permuted = mat_b[perm][:, perm]
        null_r = _pearson(a_vec, permuted[iu])
        if null_r >= obs_r:
            n_exceed += 1

    p_value = (n_exceed + 1) / (n_permutations + 1)
    return float(obs_r), float(p_value)


def pairwise_mantel(
    matrices_by_model: dict[str, NDArray[np.float64]],
    *,
    n_permutations: int = 999,
    random_state: int = 42,
) -> list[MantelPair]:
    """Run the Mantel test on every unique pair of models.

    All matrices must share the same item order; caller is responsible
    for intersecting to the shared item set first.

    Returns a list of ``MantelPair`` sorted by (model_a, model_b).
    """
    model_ids = sorted(matrices_by_model.keys())
    pairs: list[MantelPair] = []
    for i, a in enumerate(model_ids):
        for b in model_ids[i + 1:]:
            r, p = mantel_test(
                matrices_by_model[a],
                matrices_by_model[b],
                n_permutations=n_permutations,
                random_state=random_state,
            )
            pairs.append(
                MantelPair(
                    model_a=a,
                    model_b=b,
                    r=r,
                    p_value=p,
                    n_permutations=n_permutations,
                )
            )
    return pairs


def _pearson(x: NDArray[np.float64], y: NDArray[np.float64]) -> float:
    """Pearson correlation with zero-variance fallback."""
    if len(x) < 2:
        return 0.0
    r = np.corrcoef(x, y)[0, 1]
    if np.isnan(r):
        return 0.0
    return float(r)


# ---------------------------------------------------------------------------
# Nolan Index (Robbins 2023)
# ---------------------------------------------------------------------------

def nolan_index(
    items_a: dict[str, float],
    items_b: dict[str, float],
) -> tuple[float, float]:
    """Proportional-frequency similarity between two item distributions.

    Robbins (2023) J. Ethnobiology 43(1):12–18.

        NI = 1 - D
        D  = sqrt( (1/M) × Σ (p_i^a - p_i^b)² )
        p_i^a = proportion of informant a's mentions that went to item i

    M is the total number of unique items across both distributions
    (including items present in only one), with missing items treated
    as zero proportion. Range [0, 1] where 1 is identical proportional
    distributions.

    Args:
        items_a: model a's item → mention count (or proportion; the
            function normalizes internally).
        items_b: model b's item → mention count (or proportion).

    Returns:
        ``(ni, jaccard)`` for convenience — Jaccard is included because
        ``NI < Jaccard`` diagnoses "same items, different weights"
        while ``NI == Jaccard == 1`` diagnoses identical distributions.
    """
    all_items = sorted(set(items_a) | set(items_b))
    m = len(all_items)
    if m == 0:
        return 1.0, 1.0

    total_a = sum(items_a.values())
    total_b = sum(items_b.values())
    if total_a <= 0 or total_b <= 0:
        return 0.0, 0.0

    sq_diff_sum = 0.0
    for item in all_items:
        p_a = items_a.get(item, 0.0) / total_a
        p_b = items_b.get(item, 0.0) / total_b
        d = p_a - p_b
        sq_diff_sum += d * d

    d_distance = (sq_diff_sum / m) ** 0.5
    ni = 1.0 - d_distance

    intersect = len(set(items_a) & set(items_b))
    union = len(set(items_a) | set(items_b))
    jaccard = intersect / union if union > 0 else 1.0

    return float(ni), float(jaccard)


def pairwise_nolan(
    items_by_model: dict[str, dict[str, float]],
) -> list[NolanIndexPair]:
    """Run the Nolan Index on every unique pair of models.

    ``items_by_model`` maps model_id → item frequency dict. Output is
    sorted by (model_a, model_b).
    """
    model_ids = sorted(items_by_model.keys())
    pairs: list[NolanIndexPair] = []
    for i, a in enumerate(model_ids):
        for b in model_ids[i + 1:]:
            ni, jac = nolan_index(items_by_model[a], items_by_model[b])
            pairs.append(
                NolanIndexPair(
                    model_a=a,
                    model_b=b,
                    ni=ni,
                    jaccard=jac,
                    ni_vs_jaccard_delta=ni - jac,
                )
            )
    return pairs
