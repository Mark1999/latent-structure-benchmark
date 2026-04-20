"""Cultural consensus analysis (Romney/Weller/Batchelder). See ARCHITECTURE.md §4.2.

Includes Smith's S salience index computation per Quinlan (2017),
elbow detection for data-driven free list truncation, pile count
variance monitoring per methodology audit, and (post-F1 SME review)
cultural centrality scores + low-consensus typology classification
per Caulkins (1999) and Caulkins & Hyatt (1999). See
docs/SME_REVIEW.md §1.5 and §1.6.

Cultural centrality is computed at the model level per SME Q4
(models-as-informants). Each model contributes one centrality score
derived from the loadings on the first eigenvector of the model × model
agreement (similarity) matrix, normalized to [0, 1]. Following
Caulkins (1999), we label this as "cultural centrality" rather than
"competence" — the Romney/Weller/Batchelder "competence" label implies
objective correctness, which is inappropriate for a benchmark whose
object is not a single ground-truth culture. A negative centrality
score indicates the model systematically inverts the modal consensus
and is a flag, not a disqualification — see docs/SME_REVIEW.md Q6.
"""

from __future__ import annotations

import math

import numpy as np
from cdb_core import ConsensusType, InformantRecord
from numpy.typing import NDArray


def smiths_s(rank: int, list_length: int) -> float:
    """Compute Smith's S individual salience for one item on one list.

    Formula: S = (L - R + 1) / L
    where L = total items listed, R = 1-indexed rank position.

    First item (R=1): S = 1.0
    Last item (R=L): S = 1/L

    See Quinlan (2017), Smith (1993), Smith & Borgatti (1997).

    Args:
        rank: 1-indexed position of the item in the list.
        list_length: Total number of items in the list.

    Returns:
        Salience value in (0, 1].
    """
    if list_length <= 0:
        return 0.0
    return (list_length - rank + 1) / list_length


def compute_consensus_free_list(
    records: list[InformantRecord],
) -> list[tuple[str, float]]:
    """Compute a consensus free list ranked by composite Smith's S.

    For each item across all N runs, computes individual salience per run
    where it appears (using its rank in parsed_raw_order). Runs where the
    item does not appear contribute 0. Composite S = sum / N.

    Args:
        records: List of InformantRecords (same model, same domain).

    Returns:
        List of (item, composite_smiths_s) tuples sorted descending by salience.
    """
    if not records:
        return []

    n_runs = len(records)

    # Accumulate salience per item across all runs
    item_salience: dict[str, float] = {}

    for r in records:
        raw_order = r.freelist.parsed_raw_order
        list_length = len(raw_order)
        seen_in_run: set[str] = set()

        for rank_0, item in enumerate(raw_order):
            if item in seen_in_run:
                continue  # Only count first occurrence
            seen_in_run.add(item)
            rank_1 = rank_0 + 1  # Convert to 1-indexed
            s = smiths_s(rank_1, list_length)
            item_salience[item] = item_salience.get(item, 0.0) + s

    # Compute composite: divide by total number of runs (not just runs where item appeared)
    composite = [
        (item, total_s / n_runs)
        for item, total_s in item_salience.items()
    ]

    # Sort descending by salience
    composite.sort(key=lambda x: (-x[1], x[0]))
    return composite


def find_salience_elbow(
    ranked_salience: list[tuple[str, float]],
    min_items: int = 10,
    max_items: int = 60,
) -> int:
    """Find the elbow point in a ranked Smith's S salience curve.

    Uses the maximum-distance-to-chord method (geometric elbow detection):
    draw a straight line from the first point to the last, then find the
    point with the greatest perpendicular distance from that line. This is
    the inflection where the curve transitions from high-salience core
    items to the long tail.

    This replaces fixed truncation_k with a data-driven cutoff. The elbow
    is analogous to a scree plot knee in factor analysis — we keep the
    items above the bend and treat the rest as the long tail.

    Args:
        ranked_salience: Output of compute_consensus_free_list — list of
            (item, composite_smiths_s) sorted descending.
        min_items: Floor — never return fewer than this, even if the
            elbow is earlier. Protects against degenerate curves.
        max_items: Ceiling — never return more than this. Safety valve
            for context window limits during pile sorting.

    Returns:
        Number of items to keep (the elbow index, 1-based count).
    """
    n = len(ranked_salience)
    if n <= min_items:
        return n

    # Extract salience values only
    salience = [s for _, s in ranked_salience]

    # Clamp to the searchable range
    search_end = min(n, max_items)

    # Normalize x (rank) and y (salience) to [0, 1] for unbiased distance
    x = [i / (search_end - 1) for i in range(search_end)]
    y_min = salience[search_end - 1]
    y_max = salience[0]
    y_range = y_max - y_min
    if y_range <= 0:
        # Flat curve — all items equally salient, return max
        return search_end
    y = [(s - y_min) / y_range for s in salience[:search_end]]

    # Chord from first point to last point
    # Line: from (x[0], y[0]) to (x[-1], y[-1])
    x0, y0 = x[0], y[0]
    x1, y1 = x[-1], y[-1]

    # Direction vector of the chord
    dx = x1 - x0
    dy = y1 - y0
    chord_len = math.sqrt(dx * dx + dy * dy)
    if chord_len == 0:
        return min_items

    # Find point with maximum perpendicular distance from chord
    best_idx = min_items
    best_dist = -1.0

    for i in range(min_items, search_end):
        # Perpendicular distance from point (x[i], y[i]) to the chord line
        dist = abs(dy * x[i] - dx * y[i] + x1 * y0 - y1 * x0) / chord_len
        if dist > best_dist:
            best_dist = dist
            best_idx = i

    # Return as 1-based count (the elbow index is inclusive)
    return best_idx + 1


def compute_cross_model_consensus(
    records_by_model: dict[str, list[InformantRecord]],
) -> list[tuple[str, float]]:
    """Compute a consensus free list pooled across all models.

    Same Smith's S computation as compute_consensus_free_list, but treats
    every free list from every model as an independent informant. This
    produces the shared domain vocabulary for cross-model pile sorting —
    the common card deck that makes similarity matrices comparable.

    Args:
        records_by_model: Dict mapping model_id → list of InformantRecords
            that have freelist data (output_tokens > 0).

    Returns:
        List of (item, composite_smiths_s) sorted descending by salience.
        Use find_salience_elbow() on this to get the data-driven cutoff.
    """
    # Flatten all records into a single pool
    all_records = [
        rec
        for recs in records_by_model.values()
        for rec in recs
    ]
    return compute_consensus_free_list(all_records)


def compute_pile_count_stats(
    records: list[InformantRecord],
) -> dict:
    """Compute pile count statistics across runs for lumper/splitter monitoring.

    See methodology audit finding: monitor pile count variance across runs.

    Args:
        records: List of InformantRecords (same model, same domain).

    Returns:
        Dict with keys: mean, std, min, max, counts.
    """
    counts = [len(r.pile_sort.parsed_piles) for r in records]

    if not counts:
        return {"mean": 0.0, "std": 0.0, "min": 0, "max": 0, "counts": []}

    n = len(counts)
    mean = sum(counts) / n

    if n > 1:
        variance = sum((c - mean) ** 2 for c in counts) / (n - 1)
        std = variance ** 0.5
    else:
        std = 0.0

    return {
        "mean": round(mean, 2),
        "std": round(std, 2),
        "min": min(counts),
        "max": max(counts),
        "counts": counts,
    }


# ---------------------------------------------------------------------------
# Cultural centrality and low-consensus typology (post-F1 SME review)
# ---------------------------------------------------------------------------

def compute_centrality_scores(
    model_ids: list[str],
    similarity_matrix: NDArray[np.float64],
) -> dict[str, float]:
    """Per-model cultural centrality from the inter-model similarity matrix.

    Computed as the loadings on the first eigenvector of the model × model
    similarity matrix. Models with high positive loadings are central to
    the inter-model consensus; models with near-zero loadings are neutral;
    models with negative loadings systematically invert the modal consensus.

    Per Caulkins (1999), the canonical label for this is "cultural
    centrality," not "competence." "Competence" implies objective
    correctness against a known ground truth, which does not apply
    to a benchmark whose object is architectural comparison rather than
    approximation of a specific human cultural consensus.

    Negative scores are a first-class finding (candidate SUBCULTURAL or
    CONTESTED classification — see ``classify_consensus``) and also a
    QA signal for anomaly review per docs/SME_REVIEW.md Q6.

    Args:
        model_ids: Ordering of models corresponding to the similarity
            matrix rows/columns.
        similarity_matrix: Square model × model similarity matrix.

    Returns:
        dict mapping model_id → centrality score. Raw loadings are
        preserved (not normalized to [0, 1]) so the sign is meaningful;
        readers interpret ``> 0`` as contributing to the dominant
        structure, ``< 0`` as opposing it.
    """
    n = len(model_ids)
    if n != similarity_matrix.shape[0]:
        msg = (
            f"Model count {n} does not match similarity matrix shape "
            f"{similarity_matrix.shape}"
        )
        raise ValueError(msg)
    if n < 2:
        return {mid: 0.0 for mid in model_ids}

    # Symmetric real matrix → use eigh for numerical stability.
    eigvals, eigvecs = np.linalg.eigh(similarity_matrix)
    # eigh returns ascending; we want the largest eigenvalue's eigenvector.
    order = eigvals.argsort()[::-1]
    first = eigvecs[:, order[0]]

    # Convention: flip so the mean loading is positive (the eigenvector
    # sign is arbitrary; this makes the sign of individual loadings
    # interpretable relative to the dominant structure).
    if float(np.mean(first)) < 0:
        first = -first

    return {mid: float(first[i]) for i, mid in enumerate(model_ids)}


def classify_consensus(
    eigenratio: float,
    centrality_scores: dict[str, float],
    *,
    classic_threshold: float = 3.0,
    operational_threshold: float = 5.0,
    deterministic_variance_threshold: float = 1e-9,
    observed_variance: float | None = None,
) -> ConsensusType:
    """Map eigenratio + centrality profile to a low-consensus typology label.

    Per Caulkins & Hyatt (1999) with a DETERMINISTIC extension for
    future architectures. See docs/SME_REVIEW.md §1.6 and §3.3.

    Decision table:

    | Eigenratio | All scores ≥ 0 | Any score < 0 |
    |---|---|---|
    | ≥ 5.0 | STRONG_CONSENSUS | SUBCULTURAL |
    | [3.0, 5.0) | WEAK_CONSENSUS | SUBCULTURAL |
    | < 3.0 | TURBULENT | CONTESTED |

    DETERMINISTIC overrides everything when ``observed_variance`` is
    below ``deterministic_variance_threshold`` — signal that the model
    produced zero-variance output across the available variation axes
    (run + prompt). Reserved for future deterministic architectures;
    does not trigger for any current transformer model at T > 0.

    Args:
        eigenratio: The λ₁/λ₂ ratio of the inter-model agreement matrix.
        centrality_scores: Output of ``compute_centrality_scores``.
        classic_threshold: Lower bound for consensus (default 3.0, the
            classic RWB threshold).
        operational_threshold: LSB operational threshold (default 5.0,
            per SME small-n adjustment).
        deterministic_variance_threshold: Variance floor below which
            the output distribution is treated as deterministic.
        observed_variance: Observed variance across runs + prompts
            (if known). When None, DETERMINISTIC cannot be assessed
            and the function falls through to the standard table.

    Returns:
        One of the six ``ConsensusType`` literal values.
    """
    if observed_variance is not None and observed_variance < deterministic_variance_threshold:
        return "DETERMINISTIC"

    has_negative = any(score < 0 for score in centrality_scores.values())

    if eigenratio >= operational_threshold:
        return "SUBCULTURAL" if has_negative else "STRONG_CONSENSUS"
    if eigenratio >= classic_threshold:
        return "SUBCULTURAL" if has_negative else "WEAK_CONSENSUS"
    return "CONTESTED" if has_negative else "TURBULENT"
