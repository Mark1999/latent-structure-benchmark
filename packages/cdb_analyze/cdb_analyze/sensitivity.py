"""Prompt-sensitivity study framework. See ARCHITECTURE.md §5.3.

Phase 4b: compute within-model variance (across prompt variants) and
between-model variance (across the 12-model slate). The G1 stability
gate requires within/between ratio < 0.5.

Running this module requires Phase 4b collection data — InformantRecords
tagged with a ``prompt_variant`` field (via the variant collection mode).
The framework itself can be tested with synthetic data.
"""

from __future__ import annotations

import numpy as np
from cdb_core import InformantRecord
from numpy.typing import NDArray

from cdb_analyze.cooccurrence import build_cooccurrence_matrix
from cdb_analyze.mds import compute_cross_model_similarity


def compute_within_model_variance(
    records_by_variant: dict[str, list[InformantRecord]],
) -> float:
    """Compute within-model variance across prompt variants.

    For a single reference model, groups records by prompt variant,
    builds a co-occurrence matrix per variant, computes pairwise
    Mantel-style similarity between variants, and returns the variance
    of the upper-triangle similarity values.

    A low within-model variance means the model's categorical structure
    is stable across different prompt phrasings.

    Args:
        records_by_variant: Maps variant_id to InformantRecords for
            one model across N runs of that variant.

    Returns:
        Variance of pairwise similarities across variants.
    """
    variant_ids = sorted(records_by_variant.keys())
    n_variants = len(variant_ids)

    if n_variants < 2:
        return 0.0

    matrices = [
        build_cooccurrence_matrix(records_by_variant[vid])
        for vid in variant_ids
    ]

    _, sim = compute_cross_model_similarity(matrices)
    return _upper_triangle_variance(sim)


def compute_between_model_variance(
    records_by_model: dict[str, list[InformantRecord]],
) -> float:
    """Compute between-model variance across the full model slate.

    Builds a co-occurrence matrix per model, computes pairwise
    cross-model similarity, and returns the variance of the
    upper-triangle similarity values.

    Args:
        records_by_model: Maps model_id to InformantRecords.

    Returns:
        Variance of pairwise similarities across models.
    """
    model_ids = sorted(records_by_model.keys())
    if len(model_ids) < 2:
        return 0.0

    matrices = [
        build_cooccurrence_matrix(records_by_model[mid])
        for mid in model_ids
    ]

    _, sim = compute_cross_model_similarity(matrices)
    return _upper_triangle_variance(sim)


def _upper_triangle_variance(sim: NDArray[np.float64]) -> float:
    """Variance of upper-triangle entries in a similarity matrix."""
    n = sim.shape[0]
    mask = np.triu(np.ones((n, n), dtype=bool), k=1)
    vals = sim[mask]
    if len(vals) < 2:
        return 0.0
    return float(np.var(vals, ddof=1))
