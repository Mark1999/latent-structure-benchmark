"""Salience indices beyond Smith's S. See ARCHITECTURE.md §4.2 and
docs/SME_REVIEW.md §2.1.

Sutrop's CSI (Sutrop 2001) — composite salience index more robust to
list-length variance than Smith's S. For LSB, list lengths vary across
models and across the no-ceiling experimental condition, which compresses
Smith's S variance in ways that can distort the salience order. CSI
preserves ordering better under that regime.

    CSI(item) = F / (N × mP)

    F  = frequency of mention across runs
    N  = total number of runs considered
    mP = mean 1-indexed position of the item across runs in which it
         appeared

Reported alongside Smith's S; the Spearman ρ between the two rankings
(``compute_salience_agreement``) is a diagnostic — if ρ < 0.85, list-
length variance is high enough to affect the salience structure and
the domain's results carry a note to that effect.
"""

from __future__ import annotations

from cdb_core import InformantRecord, SutropCSI


def sutrop_csi(
    records: list[InformantRecord],
) -> list[SutropCSI]:
    """Compute Sutrop composite salience for every item across N runs.

    Args:
        records: InformantRecords for a single (model, domain). Each
            record contributes its ``freelist.parsed_raw_order``. Items
            absent from a run contribute nothing to that run's F or mP
            for that item.

    Returns:
        List of ``SutropCSI`` sorted descending by CSI (highest
        salience first). Items present in at least one run are
        included; items appearing in zero runs are omitted.
    """
    if not records:
        return []

    n_runs = len(records)

    # For each item, accumulate (f_mentions, sum_of_positions)
    # across runs where it appeared.
    stats: dict[str, tuple[int, float]] = {}

    for rec in records:
        order = rec.freelist.parsed_raw_order
        seen: set[str] = set()
        for rank_0, item in enumerate(order):
            if item in seen:
                continue  # count first occurrence only
            seen.add(item)
            rank_1 = rank_0 + 1
            f_prev, sum_pos_prev = stats.get(item, (0, 0.0))
            stats[item] = (f_prev + 1, sum_pos_prev + rank_1)

    # Compute CSI per item.
    results: list[SutropCSI] = []
    for item, (f_mentions, sum_pos) in stats.items():
        mean_pos = sum_pos / f_mentions
        csi = f_mentions / (n_runs * mean_pos)
        results.append(
            SutropCSI(
                item=item,
                csi=csi,
                f_mentions=f_mentions,
                n_runs=n_runs,
                mean_position=mean_pos,
            )
        )

    # Sort descending by CSI, break ties by item name for determinism.
    results.sort(key=lambda s: (-s.csi, s.item))
    return results


def compute_salience_agreement(
    smiths_s_ranked: list[tuple[str, float]],
    sutrop_ranked: list[SutropCSI],
) -> float:
    """Spearman ρ between Smith's S and Sutrop CSI item rankings.

    Computed on the intersection of items present in both rankings.
    Returns ρ in [-1, 1]. Values below 0.85 are a warning signal that
    list-length variance is influencing the salience order — worth
    flagging in the per-model QA note.

    Args:
        smiths_s_ranked: Output of ``consensus.compute_consensus_free_list``.
        sutrop_ranked: Output of ``sutrop_csi`` above.

    Returns:
        Spearman rank correlation coefficient. Returns 1.0 when fewer
        than two items are in the intersection (trivially agreeing).
    """
    smiths_rank = {item: i for i, (item, _) in enumerate(smiths_s_ranked)}
    sutrop_rank = {s.item: i for i, s in enumerate(sutrop_ranked)}

    shared = sorted(set(smiths_rank) & set(sutrop_rank))
    n = len(shared)
    if n < 2:
        return 1.0

    x = [smiths_rank[item] for item in shared]
    y = [sutrop_rank[item] for item in shared]

    # Spearman ρ via rank correlation: since x and y are already integer
    # ranks, Pearson correlation of the ranks equals Spearman ρ.
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y, strict=True))
    denom_x = sum((xi - mean_x) ** 2 for xi in x)
    denom_y = sum((yi - mean_y) ** 2 for yi in y)
    if denom_x == 0 or denom_y == 0:
        return 1.0
    return float(num / (denom_x ** 0.5 * denom_y ** 0.5))
