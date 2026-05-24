"""Pile sort responses to co-occurrence matrices. See ARCHITECTURE.md §4.2.

For each pair of items, count the fraction of runs in which they appear
in the same pile. Diagonal = 1.0. Symmetric.
"""

from __future__ import annotations

from datetime import UTC, datetime

from cdb_core import CooccurrenceMatrix, InformantRecord, ModelRef


def compute_cross_model_term_frequency(
    records_by_model: dict[str, list[InformantRecord]],
) -> list[tuple[str, int]]:
    """Return (term, f_models) pairs sorted descending by f_models.

    f_models = number of distinct models whose pile sorts include the term.
    Operates on pile_sort.parsed_piles, NOT freelist.parsed_items.

    A term that appears in 5 runs of the same model counts as f_models=1.
    A term that appears once each in 8 different models counts as f_models=8.

    Per CDA SME T1 (2026-05-24-phase9a-term-truncation-sme-ruling.md):
    cross-model frequency is the correct unit for Register 2 analysis.
    Terms are drawn from pile_sort.parsed_piles only — terms that appeared
    in a free list but were not carried into a pile sort have no co-occurrence
    data to contribute.

    Args:
        records_by_model: Dict mapping model_id → list of InformantRecords.

    Returns:
        List of (term, f_models) tuples sorted descending by f_models.
        Ties in f_models are broken by ascending lexicographic order for
        determinism.
    """
    term_model_sets: dict[str, set[str]] = {}

    for model_id, recs in records_by_model.items():
        for rec in recs:
            for pile in rec.pile_sort.parsed_piles:
                for term in pile:
                    if term not in term_model_sets:
                        term_model_sets[term] = set()
                    term_model_sets[term].add(model_id)

    result = [
        (term, len(model_set))
        for term, model_set in term_model_sets.items()
    ]
    # Sort descending by f_models; ties broken by ascending lexicographic order
    result.sort(key=lambda x: (-x[1], x[0]))
    return result


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


def build_pooled_cooccurrence_matrix(
    records_by_model: dict[str, list[InformantRecord]],
    item_subset: list[str] | None = None,
) -> CooccurrenceMatrix:
    """Build a pooled cross-model co-occurrence matrix.

    Implements the Register 2 equal-voice-per-model pooling strategy per
    CDA SME M1 (2026-05-24-phase9a-cda-sme-verdict.md):

      pooled[i][j] = (1/M) * sum_over_models( model_cooccurrence[i][j] )

    where model_cooccurrence[i][j] is each model's per-model consensus
    co-occurrence fraction and M is the number of models with at least
    one valid run. Items absent from a model's vocabulary receive 0.0 for
    all cells in that model's matrix — absence is evidence of non-co-
    occurrence, not missing data. The denominator is always M, not the
    number of models that produced both items.

    Item set = sorted union of all items across all models' pile sorts,
    or the provided item_subset (when given).

    Args:
        records_by_model: Dict mapping model_id → list of InformantRecords
            for that model. All records must share the same domain_slug.
        item_subset: When provided, use this explicit list of items instead
            of computing the full union across all models. The list is used
            as-is (ordering preserved). Items in item_subset that are absent
            from a model's per-model matrix receive 0.0 for all cells in
            that model's contribution — identical to the full-union behaviour.
            When None (default), the full union item set is computed as before
            (backward-compatible). Per CDA SME T3
            (2026-05-24-phase9a-term-truncation-sme-ruling.md).

    Returns:
        CooccurrenceMatrix with the pooled values and the item list (either
        item_subset or the sorted union). The ``model`` field carries a
        synthetic ModelRef with model_id="pooled" to distinguish from any
        single-model matrix.

    Raises:
        ValueError: If records_by_model is empty.
    """
    if not records_by_model:
        raise ValueError("No records provided for pooled co-occurrence matrix")

    # Build per-model consensus matrices
    per_model_matrices: dict[str, CooccurrenceMatrix] = {}
    for model_id, recs in records_by_model.items():
        if recs:
            per_model_matrices[model_id] = build_cooccurrence_matrix(recs)

    if not per_model_matrices:
        raise ValueError(
            "No models with valid records for pooled co-occurrence matrix"
        )

    # Determine the item set.
    # When item_subset is provided (term truncation path), use it directly.
    # When None, compute the full sorted union across all models (backward-
    # compatible behaviour preserved for testing and single-model callers).
    if item_subset is not None:
        items = list(item_subset)
    else:
        all_items: set[str] = set()
        for mat in per_model_matrices.values():
            all_items.update(mat.items)
        items = sorted(all_items)
    n_items = len(items)

    M = len(per_model_matrices)

    # Accumulate each model's contribution using the full union item set.
    # Items absent from a model get 0.0 — they do not contribute to the
    # numerator but they ARE counted in the denominator (always M).
    pooled = [[0.0] * n_items for _ in range(n_items)]

    for mat in per_model_matrices.values():
        # Build a fast index from mat.items to its matrix row/col positions
        local_idx = {item: i for i, item in enumerate(mat.items)}

        for i_global, item_i in enumerate(items):
            for j_global, item_j in enumerate(items):
                i_local = local_idx.get(item_i)
                j_local = local_idx.get(item_j)

                if i_local is not None and j_local is not None:
                    pooled[i_global][j_global] += mat.matrix[i_local][j_local]
                # else: item absent from this model → contributes 0.0;
                # no addition needed since pooled is already initialised to 0.0

    # Divide by M to get the mean (denominator always M per M1)
    for i in range(n_items):
        for j in range(n_items):
            pooled[i][j] /= M

    # Construct a synthetic ModelRef to represent the pooled matrix
    # Pull domain_slug from the first model's records
    first_recs = next(iter(records_by_model.values()))
    domain_slug = first_recs[0].domain_slug

    pooled_model_ref = ModelRef(
        provider="anthropic",
        model_id="pooled",
        family="pooled",
        origin="us",
        open_weights=False,
        collection_method="anthropic_api",
        quantization=None,
        release_date=datetime.now(UTC).date(),
        version_label="pooled",
    )

    return CooccurrenceMatrix(
        domain_slug=domain_slug,
        model=pooled_model_ref,
        items=items,
        matrix=pooled,
    )
