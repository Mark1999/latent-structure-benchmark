"""Phase 4 validation gates (G1, G2, G3). See ARCHITECTURE.md §5.3.

Three quantitative criteria that must all pass before Phase 5 begins:

    G1 — Stability: within-model prompt variance < between-model variance
          (ratio < 0.5).
    G2 — Signal: model-to-model similarity matrix statistically
          distinguishable from random (permutation test p < 0.01).
    G3 — Replication: cluster structure replicates across independent
          bootstrap pipeline runs (Adjusted Rand Index ≥ 0.6; Rand
          index also reported for cross-study comparability).

Per the post-F1 SME review, G3 uses the Adjusted Rand Index as the
binding metric. ARI corrects for chance agreement and is the standard
in modern cluster analysis literature; 0.60 on ARI is conservative and
defensible and corresponds roughly to 0.70 on unadjusted Rand for
typical cluster sizes. The unadjusted Rand index is still computed
and reported in ``secondary_metrics`` for continuity with prior
internal results and for cross-study comparability with papers that
reported Rand before ARI was common.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from cdb_core import ConsensusType, InformantRecord  # noqa: F401 — re-exported
from numpy.typing import NDArray
from sklearn.metrics import adjusted_rand_score

from cdb_analyze.cluster import cluster_models
from cdb_analyze.cooccurrence import build_cooccurrence_matrix
from cdb_analyze.mds import compute_cross_model_similarity

# Canonical definition of ``ConsensusType`` lives in ``cdb_core.schemas``.
# It is re-exported here via the import above so that older callers that
# do ``from cdb_analyze.gates import ConsensusType`` continue to work.
# See docs/SME_REVIEW.md §1.6 for the six-state typology and the Caulkins
# & Hyatt (1999) derivation.

# ---------------------------------------------------------------------------
# Shared result type
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GateResult:
    """Outcome of a single validation gate.

    ``value`` is the binding metric (what the pass/fail decision is made
    against). ``secondary_metrics`` carries auxiliary numbers that are
    reported alongside — for G3, ``median_rand_index`` is in
    ``secondary_metrics`` while ``value`` carries the (binding) median
    Adjusted Rand Index. See the module docstring.
    """

    gate: str          # "G1", "G2", "G3"
    passed: bool
    value: float       # binding metric (ratio / p-value / ARI)
    threshold: float   # pass threshold
    detail: str        # human-readable one-liner
    secondary_metrics: dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# G2 — Signal gate (permutation test)
# ---------------------------------------------------------------------------

def _off_diagonal_dispersion(sim: NDArray[np.float64]) -> float:
    """Variance of upper-triangle entries in a similarity matrix.

    A random similarity matrix has low dispersion; a structured one
    (some models similar, others different) has high dispersion.
    """
    n = sim.shape[0]
    mask = np.triu(np.ones((n, n), dtype=bool), k=1)
    vals = sim[mask]
    if len(vals) < 2:
        return 0.0
    return float(np.var(vals))


def g2_signal(
    matrices: list[tuple[str, NDArray[np.float64]]],
    *,
    n_perm: int = 9999,
    threshold: float = 0.01,
    random_state: int = 42,
) -> GateResult:
    """G2 — Is the similarity matrix distinguishable from random?

    Permutation test: for each permutation, shuffle the row/column labels
    on each model's upper-triangle co-occurrence vector, then recompute
    cross-model Pearson similarity. The test statistic is the mean
    off-diagonal similarity. If the observed value falls in the top
    ``threshold`` fraction of the null distribution the gate passes.

    Args:
        matrices: List of (model_id, upper_triangle_vector) pairs where
            each vector is the flattened upper triangle of that model's
            co-occurrence matrix on the shared item set.
        n_perm: Number of permutations for the null distribution.
        threshold: p-value threshold (default 0.01).
        random_state: RNG seed.

    Returns:
        GateResult with observed p-value and pass/fail.
    """
    rng = np.random.default_rng(random_state)
    vectors = [v.copy() for _, v in matrices]  # (n_models, n_pairs)
    n_models = len(vectors)

    if n_models < 2:
        return GateResult(
            gate="G2",
            passed=False,
            value=1.0,
            threshold=threshold,
            detail="Need ≥2 models for the signal test",
        )

    # Observed test statistic: dispersion (variance) of off-diagonal
    # similarities. A structured matrix has high dispersion; random has low.
    obs_sim = _pairwise_pearson(vectors)
    obs_stat = _off_diagonal_dispersion(obs_sim)

    # Null distribution: independently permute each model's vector
    n_exceed = 0
    for _ in range(n_perm):
        shuffled = [rng.permutation(v) for v in vectors]
        null_sim = _pairwise_pearson(shuffled)
        null_stat = _off_diagonal_dispersion(null_sim)
        if null_stat >= obs_stat:
            n_exceed += 1

    p_value = (n_exceed + 1) / (n_perm + 1)  # +1 for the observed itself
    passed = p_value < threshold

    return GateResult(
        gate="G2",
        passed=passed,
        value=round(p_value, 6),
        threshold=threshold,
        detail=(
            f"p={p_value:.4f} (observed dispersion {obs_stat:.4f}, "
            f"{n_perm} permutations)"
        ),
    )


def _pairwise_pearson(
    vectors: list[NDArray[np.float64]],
) -> NDArray[np.float64]:
    """Pairwise Pearson correlation matrix rescaled to [0, 1]."""
    n = len(vectors)
    sim = np.ones((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(i + 1, n):
            r = np.corrcoef(vectors[i], vectors[j])[0, 1]
            if np.isnan(r):
                r = 0.0
            scaled = (r + 1.0) / 2.0
            sim[i, j] = scaled
            sim[j, i] = scaled
    return sim


# ---------------------------------------------------------------------------
# G3 — Replication gate (Rand index)
# ---------------------------------------------------------------------------

def rand_index(labels_a: list[int], labels_b: list[int]) -> float:
    """Compute the Rand index between two clusterings.

    RI = (agreements) / (total pairs)

    where an agreement means both clusterings agree on whether a pair
    of items belong to the same or different clusters.
    """
    n = len(labels_a)
    if n != len(labels_b):
        msg = f"Label vectors must be same length, got {n} and {len(labels_b)}"
        raise ValueError(msg)
    if n < 2:
        return 1.0

    agree = 0
    total = 0
    for i in range(n):
        for j in range(i + 1, n):
            same_a = labels_a[i] == labels_a[j]
            same_b = labels_b[i] == labels_b[j]
            if same_a == same_b:
                agree += 1
            total += 1

    return agree / total


def g3_replication(
    records_by_model: dict[str, list[InformantRecord]],
    *,
    n_trials: int = 100,
    threshold: float = 0.6,
    random_state: int = 42,
) -> GateResult:
    """G3 — Does the cluster structure replicate across independent runs?

    First computes a reference clustering on the full data to determine
    the number of clusters k. Then for each trial, splits each model's
    runs into two disjoint halves, clusters both halves at the same k,
    and compares labels via the Adjusted Rand Index (ARI) — the binding
    metric for G3 per the post-F1 SME review. The unadjusted Rand index
    is also computed and reported in ``secondary_metrics`` for
    cross-study comparability.

    This pins the cluster count so that the test measures membership
    stability, not cut-point detection stability.

    The gate reports the *median* ARI across trials as the binding
    value; the median unadjusted Rand is in ``secondary_metrics``.

    Args:
        records_by_model: model_id → list of InformantRecords.
        n_trials: Number of independent split-half trials.
        threshold: Minimum ARI to pass (default 0.6 per SME review;
            prior Rand threshold was 0.7 and is retained only for
            continuity as a secondary metric).
        random_state: RNG seed.

    Returns:
        GateResult with median ARI (value) and median Rand in
        ``secondary_metrics``.
    """
    rng = np.random.default_rng(random_state)
    model_ids = sorted(records_by_model.keys())
    n_models = len(model_ids)

    if n_models < 2:
        return GateResult(
            gate="G3",
            passed=False,
            value=0.0,
            threshold=threshold,
            detail="Need ≥2 models for the replication test",
        )

    # Check all models have ≥2 runs (needed for split-half)
    min_runs = min(len(records_by_model[mid]) for mid in model_ids)
    if min_runs < 2:
        return GateResult(
            gate="G3",
            passed=False,
            value=0.0,
            threshold=threshold,
            detail=f"Need ≥2 runs per model for split-half; minimum is {min_runs}",
        )

    # Compute reference k from full data (auto-cut)
    ref_k = _reference_cluster_count(records_by_model, model_ids)

    ari_values: list[float] = []
    rand_values: list[float] = []

    for _ in range(n_trials):
        half_a: dict[str, list[InformantRecord]] = {}
        half_b: dict[str, list[InformantRecord]] = {}

        for mid in model_ids:
            runs = records_by_model[mid]
            perm = rng.permutation(len(runs))
            split = len(runs) // 2
            half_a[mid] = [runs[i] for i in perm[:split]]
            half_b[mid] = [runs[i] for i in perm[split:]]

        try:
            labels_a = _cluster_from_records(half_a, model_ids, max_clusters=ref_k)
            labels_b = _cluster_from_records(half_b, model_ids, max_clusters=ref_k)
            ari_values.append(float(adjusted_rand_score(labels_a, labels_b)))
            rand_values.append(rand_index(labels_a, labels_b))
        except (ValueError, np.linalg.LinAlgError):
            # Degenerate split — skip this trial
            continue

    if not ari_values:
        return GateResult(
            gate="G3",
            passed=False,
            value=0.0,
            threshold=threshold,
            detail="All split-half trials failed (degenerate data)",
        )

    median_ari = float(np.median(ari_values))
    median_rand = float(np.median(rand_values))
    passed = median_ari >= threshold

    return GateResult(
        gate="G3",
        passed=passed,
        value=round(median_ari, 4),
        threshold=threshold,
        detail=(
            f"Median ARI {median_ari:.4f} across {len(ari_values)} trials at k={ref_k} "
            f"(threshold ≥ {threshold}); median Rand {median_rand:.4f} reported for "
            f"cross-study comparability."
        ),
        secondary_metrics={
            "median_rand_index": round(median_rand, 4),
            "rand_threshold_prior": 0.7,
            "n_trials_completed": float(len(ari_values)),
            "reference_k": float(ref_k),
        },
    )


def _reference_cluster_count(
    records_by_model: dict[str, list[InformantRecord]],
    model_ids: list[str],
) -> int:
    """Compute reference cluster count from full data using auto-cut."""
    matrices = [
        build_cooccurrence_matrix(records_by_model[mid])
        for mid in model_ids
    ]
    _, sim = compute_cross_model_similarity(matrices)
    result = cluster_models(model_ids, sim)
    return result.n_clusters


def _cluster_from_records(
    records_by_model: dict[str, list[InformantRecord]],
    model_ids: list[str],
    *,
    max_clusters: int | None = None,
) -> list[int]:
    """Build co-occurrence → similarity → cluster labels."""
    matrices = [
        build_cooccurrence_matrix(records_by_model[mid])
        for mid in model_ids
    ]
    _, sim = compute_cross_model_similarity(matrices)
    result = cluster_models(model_ids, sim, max_clusters=max_clusters)
    return result.labels


# ---------------------------------------------------------------------------
# G1 — Stability gate (prompt-sensitivity)
# ---------------------------------------------------------------------------

def g1_stability(
    within_variance: float,
    between_variance: float,
    *,
    threshold: float = 0.5,
) -> GateResult:
    """G1 — Is within-model prompt variance smaller than between-model variance?

    Args:
        within_variance: Mean within-model variance across prompt variants.
        between_variance: Between-model variance from the 12-model slate.
        threshold: Maximum allowed ratio (default 0.5).

    Returns:
        GateResult with ratio and pass/fail.
    """
    if between_variance <= 0:
        return GateResult(
            gate="G1",
            passed=False,
            value=float("inf"),
            threshold=threshold,
            detail="Between-model variance is zero — no signal to compare against",
        )

    ratio = within_variance / between_variance
    passed = ratio < threshold

    return GateResult(
        gate="G1",
        passed=passed,
        value=round(ratio, 4),
        threshold=threshold,
        detail=(
            f"Within/between ratio {ratio:.4f} "
            f"(within={within_variance:.4f}, between={between_variance:.4f})"
        ),
    )
