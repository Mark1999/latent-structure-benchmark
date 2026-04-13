"""Pile sort responses to co-occurrence matrices. See ARCHITECTURE.md §4.2.

For each pair of items, count the fraction of runs in which they appear
in the same pile. Diagonal = 1.0. Symmetric.
"""

from __future__ import annotations

from cdb_core import CooccurrenceMatrix, InformantRecord, ModelRef


def build_cooccurrence_matrix(
    records: list[InformantRecord],
) -> CooccurrenceMatrix:
    """Build an aggregate co-occurrence matrix from N InformantRecords.

    All records must be for the same model and domain.

    For each pair of items, computes the fraction of runs in which
    they appear in the same pile. Diagonal = 1.0. Symmetric.

    Args:
        records: List of InformantRecords (same model, same domain).

    Returns:
        CooccurrenceMatrix with float values in [0.0, 1.0].

    Raises:
        ValueError: If records are empty or have mismatched model/domain.
    """
    if not records:
        raise ValueError("No records provided")

    model_id = records[0].model_id
    domain_slug = records[0].domain_slug

    for r in records:
        if r.model_id != model_id or r.domain_slug != domain_slug:
            raise ValueError(
                f"All records must be for the same model and domain. "
                f"Expected {model_id}/{domain_slug}, "
                f"got {r.model_id}/{r.domain_slug}"
            )

    # Collect the union of all items across runs (sorted for determinism)
    # Use freelist items when available, fall back to pile sort items
    # (two-pass/baseline records have placeholder free lists)
    all_items: set[str] = set()
    for r in records:
        if r.freelist.parsed_items:
            all_items.update(r.freelist.parsed_items)
        else:
            # Extract items from pile sort piles
            for pile in r.pile_sort.parsed_piles:
                all_items.update(pile)
    items = sorted(all_items)

    n_items = len(items)

    # Count co-occurrences across runs
    cooccur_count = [[0.0] * n_items for _ in range(n_items)]
    present_count = [[0] * n_items for _ in range(n_items)]

    for r in records:
        # Build the item list for this run from freelist or pile sort
        if r.freelist.parsed_items:
            run_item_list = r.freelist.parsed_items
        else:
            run_item_list = []
            for pile in r.pile_sort.parsed_piles:
                run_item_list.extend(pile)

        run_items = set(run_item_list)
        run_idx_map = {item: i for i, item in enumerate(run_item_list)}

        for i_global, item_i in enumerate(items):
            for j_global, item_j in enumerate(items):
                if item_i not in run_items or item_j not in run_items:
                    continue

                present_count[i_global][j_global] += 1

                if i_global == j_global:
                    cooccur_count[i_global][j_global] += 1.0
                    continue

                # Check the per-run binary matrix
                i_local = run_idx_map[item_i]
                j_local = run_idx_map[item_j]
                matrix = r.pile_sort.parsed_matrix
                if (
                    i_local < len(matrix)
                    and j_local < len(matrix[i_local])
                    and matrix[i_local][j_local] == 1
                ):
                    cooccur_count[i_global][j_global] += 1.0

    # Convert counts to fractions
    result_matrix = [[0.0] * n_items for _ in range(n_items)]
    for i in range(n_items):
        for j in range(n_items):
            if present_count[i][j] > 0:
                result_matrix[i][j] = cooccur_count[i][j] / present_count[i][j]
            elif i == j:
                result_matrix[i][j] = 1.0

    # Build a ModelRef from the first record's fields
    model_ref = ModelRef(
        provider=records[0].provider,
        model_id=records[0].model_id,
        family=records[0].family,
        origin=records[0].origin_country,
        open_weights=records[0].open_weights,
        collection_method=records[0].collection_method,
        quantization=None,
        release_date=records[0].collection_date.date(),
        version_label=records[0].model_version_returned,
    )

    return CooccurrenceMatrix(
        domain_slug=domain_slug,
        model=model_ref,
        items=items,
        matrix=result_matrix,
    )
