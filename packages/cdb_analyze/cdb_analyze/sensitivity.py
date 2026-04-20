"""Prompt-sensitivity study framework. See ARCHITECTURE.md §5.3.

Phase 4b: compute within-model variance (across prompt variants) and
between-model variance (across the 12-model slate). The G1 stability
gate requires within/between ratio < 0.5.

Running this module requires Phase 4b collection data — InformantRecords
tagged with a ``prompt_variant`` field (via the variant collection mode).
The framework itself can be tested with synthetic data.

**Split G1 (un-deferred from SME §1.3, 2026-04-20).** The G1 gate
now reports two separate stability ratios alongside the aggregate:

- **Salience stability** — variance in Smith's S rank ordering
  across prompt variants. Answers: "are the same items at the
  top regardless of how we phrase the prompt?"
- **Spatial stability** — variance in the pile-sort co-occurrence
  *structure* across prompt variants. Answers: "do items cluster
  the same way regardless of phrasing?"

These measures can diverge: a model's salience order can be stable
while its spatial structure shifts, or vice versa. Reporting both
separately is more diagnostic than the single aggregate. See SME
§1.3 and docs/briefings/2026-04-19-sme-implementation-response.md.
"""

from __future__ import annotations

import numpy as np
from cdb_core import InformantRecord
from numpy.typing import NDArray

from cdb_analyze.consensus import compute_consensus_free_list
from cdb_analyze.cooccurrence import build_cooccurrence_matrix
from cdb_analyze.mds import compute_cross_model_similarity

# ---------------------------------------------------------------------------
# Spatial variance (matrix-structure axis) — existing, unchanged
# ---------------------------------------------------------------------------

def compute_within_model_variance(
    records_by_variant: dict[str, list[InformantRecord]],
) -> float:
    """Within-model **spatial** variance across prompt variants.

    Alias kept for backwards compatibility. New code should call
    ``compute_within_model_spatial_variance`` directly — the name
    makes the axis (spatial vs salience) explicit.

    See ``compute_within_model_spatial_variance`` for behavior.
    """
    return compute_within_model_spatial_variance(records_by_variant)


def compute_between_model_variance(
    records_by_model: dict[str, list[InformantRecord]],
) -> float:
    """Between-model **spatial** variance across the full model slate.

    Alias kept for backwards compatibility. New code should call
    ``compute_between_model_spatial_variance`` directly.
    """
    return compute_between_model_spatial_variance(records_by_model)


def compute_within_model_spatial_variance(
    records_by_variant: dict[str, list[InformantRecord]],
) -> float:
    """Variance in pile-sort co-occurrence structure across prompt variants.

    For a single reference model, groups records by prompt variant,
    builds a co-occurrence matrix per variant, computes pairwise
    Mantel-style similarity between variants, and returns the variance
    of the upper-triangle similarity values. A low within-model
    spatial variance means the model's categorical **structure** is
    stable across different prompt phrasings.
    """
    variant_ids = sorted(records_by_variant.keys())
    if len(variant_ids) < 2:
        return 0.0

    matrices = [
        build_cooccurrence_matrix(records_by_variant[vid])
        for vid in variant_ids
    ]

    _, sim = compute_cross_model_similarity(matrices)
    return _upper_triangle_variance(sim)


def compute_between_model_spatial_variance(
    records_by_model: dict[str, list[InformantRecord]],
) -> float:
    """Variance in pile-sort co-occurrence structure across the model slate."""
    model_ids = sorted(records_by_model.keys())
    if len(model_ids) < 2:
        return 0.0

    matrices = [
        build_cooccurrence_matrix(records_by_model[mid])
        for mid in model_ids
    ]

    _, sim = compute_cross_model_similarity(matrices)
    return _upper_triangle_variance(sim)


# ---------------------------------------------------------------------------
# Salience variance (ranking axis) — added for split G1
# ---------------------------------------------------------------------------

def compute_within_model_salience_variance(
    records_by_variant: dict[str, list[InformantRecord]],
) -> float:
    """Variance in Smith's S rank ordering across prompt variants.

    For a single reference model: computes Smith's S rankings per
    prompt variant, computes pairwise Spearman ρ between every pair
    of variant rankings on their intersection of items, converts ρ
    to a distance via ``(1 - ρ) / 2`` (mapping [-1, 1] → [0, 1]),
    and returns the variance of the upper-triangle distance matrix.

    A low within-model salience variance means the model produces
    the same salience ordering regardless of prompt phrasing.
    """
    variant_ids = sorted(records_by_variant.keys())
    if len(variant_ids) < 2:
        return 0.0

    rankings = [
        compute_consensus_free_list(records_by_variant[vid])
        for vid in variant_ids
    ]
    dist = _pairwise_rank_distance(rankings)
    return _upper_triangle_variance(dist)


def compute_between_model_salience_variance(
    records_by_model: dict[str, list[InformantRecord]],
) -> float:
    """Variance in Smith's S rank ordering across the model slate."""
    model_ids = sorted(records_by_model.keys())
    if len(model_ids) < 2:
        return 0.0

    rankings = [
        compute_consensus_free_list(records_by_model[mid])
        for mid in model_ids
    ]
    dist = _pairwise_rank_distance(rankings)
    return _upper_triangle_variance(dist)


def _pairwise_rank_distance(
    rankings: list[list[tuple[str, float]]],
) -> NDArray[np.float64]:
    """Pairwise rank-distance matrix from Spearman ρ on Smith's S rankings.

    Distance = ``(1 - ρ) / 2`` ∈ [0, 1], where ρ is Spearman rank
    correlation on the intersection of items between the two rankings.
    Diagonal = 0.0. Symmetric.
    """
    n = len(rankings)
    dist = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(i + 1, n):
            rho = _spearman_rho_rankings(rankings[i], rankings[j])
            d = (1.0 - rho) / 2.0
            dist[i, j] = d
            dist[j, i] = d
    return dist


def _spearman_rho_rankings(
    a: list[tuple[str, float]],
    b: list[tuple[str, float]],
) -> float:
    """Spearman ρ between two (item, score) rankings on their shared items.

    Returns 1.0 when fewer than two items are shared (trivially in
    agreement). Rankings are by position in the input list —
    assumed sorted descending by score (the shape returned by
    ``compute_consensus_free_list``).
    """
    rank_a = {item: i for i, (item, _) in enumerate(a)}
    rank_b = {item: i for i, (item, _) in enumerate(b)}
    shared = sorted(set(rank_a) & set(rank_b))
    n = len(shared)
    if n < 2:
        return 1.0

    xs = [rank_a[item] for item in shared]
    ys = [rank_b[item] for item in shared]
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=True))
    denom_x = sum((x - mean_x) ** 2 for x in xs)
    denom_y = sum((y - mean_y) ** 2 for y in ys)
    if denom_x == 0 or denom_y == 0:
        return 1.0
    return float(num / (denom_x ** 0.5 * denom_y ** 0.5))


def _upper_triangle_variance(sim: NDArray[np.float64]) -> float:
    """Variance of upper-triangle entries in a similarity or distance matrix."""
    n = sim.shape[0]
    mask = np.triu(np.ones((n, n), dtype=bool), k=1)
    vals = sim[mask]
    if len(vals) < 2:
        return 0.0
    return float(np.var(vals, ddof=1))
