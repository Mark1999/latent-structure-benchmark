"""Cultural consensus analysis (Romney/Weller/Batchelder). See ARCHITECTURE.md §4.2.

Includes Smith's S salience index computation per Quinlan (2017) and
pile count variance monitoring per methodology audit.
"""

from __future__ import annotations

from cdb_core import InformantRecord


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
