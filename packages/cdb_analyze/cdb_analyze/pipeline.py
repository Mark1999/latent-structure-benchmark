"""End-to-end analysis pipeline orchestrator. See ARCHITECTURE.md §4.2.

Reads InformantRecords from informants.jsonl, groups by model, runs
co-occurrence → cross-model similarity → MDS → clustering → bootstrap,
and writes a DomainResult to data/results/{domain}/{version}.json.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from cdb_core import (
    ROMNEY_THRESHOLD_CLASSIC,
    ROMNEY_THRESHOLD_LSB,
    CentroidPileData,
    ConsensusType,
    CooccurrenceMatrix,
    DomainResult,
    FreeList,
    InformantRecord,
    ModelRef,
)

from cdb_analyze.bootstrap import (
    bootstrap_branch_stability,
    bootstrap_mds_ellipses,
    bootstrap_term_mds_ellipses,
)
from cdb_analyze.cluster import cluster_models, cluster_terms
from cdb_analyze.consensus import (
    classify_consensus,
    compute_centrality_scores,
    compute_consensus_free_list,
    compute_romney_eigenratio,
    find_salience_elbow,
)
from cdb_analyze.cooccurrence import (
    build_cooccurrence_matrix,
    build_pooled_cooccurrence_matrix,
    compute_cross_model_term_frequency,
)
from cdb_analyze.gates import G1SplitResult, g1_stability_split
from cdb_analyze.mds import compute_cross_model_similarity, run_item_mds, run_item_mds_with_stress
from cdb_analyze.salience import compute_salience_agreement, sutrop_csi
from cdb_analyze.sensitivity import (
    compute_between_model_salience_variance,
    compute_between_model_spatial_variance,
    compute_within_model_salience_variance,
    compute_within_model_spatial_variance,
)
from cdb_analyze.two_level import run_within_model_analysis

logger = logging.getLogger(__name__)


def aggregate_cluster_labels(
    cluster_assignments: dict[str, int],
    centroid_piles: dict[str, CentroidPileData],
    *,
    jaccard_threshold: float = 0.3,
) -> list[str]:
    """Derive human-readable labels for AHC clusters from per-model pile labels.

    Implements CDA SME M6 (2026-05-24-phase9a-cda-sme-verdict.md):
      1. For each AHC cluster C, collect the set of items assigned to it.
      2. For each model's centroid pile data, find the pile with highest Jaccard
         overlap with C's item set. Jaccard = |intersection| / |union|.
         Only piles with Jaccard >= jaccard_threshold count as a match.
      3. Collect the labels from all matching piles across models.
      4. Select the modal label (most frequent, case-normalised to lowercase for
         comparison). Ties broken by shortest original label; further ties broken
         by lexicographic order for determinism.
      5. If all collected labels are unique (every label appears exactly once),
         use the shortest label among the set (same tie-break logic).
      6. If no model's pile exceeds the Jaccard threshold for a given cluster,
         label it "Uncategorized".

    Args:
        cluster_assignments: Mapping of item_name → cluster_id (1-indexed,
            as returned by scipy fcluster).
        centroid_piles: Mapping of model_id → CentroidPileData.  Only models
            that have a centroid pile entry are considered.  An empty dict
            produces "Uncategorized" for every cluster.
        jaccard_threshold: Minimum Jaccard overlap required for a model's pile
            to count as a match for a cluster.  Default 0.3 per CDA SME M6.

    Returns:
        List of one label per cluster, indexed by (cluster_id - 1), i.e.
        result[0] is the label for cluster_id=1, result[1] for cluster_id=2,
        etc.  Sorted by ascending cluster_id.

    Notes:
        - No LLM calls.  All label selection is string matching and counting.
        - Cluster labels are a convenience gloss for the dashboard visitor, not
          a finding.  Imperfect labels are expected and acceptable (CDA SME A2).
    """
    if not cluster_assignments:
        return []

    # Group items by cluster_id
    cluster_to_items: dict[int, set[str]] = {}
    for item, cid in cluster_assignments.items():
        cluster_to_items.setdefault(cid, set()).add(item)

    # Process clusters in ascending ID order
    sorted_cluster_ids = sorted(cluster_to_items.keys())
    labels: list[str] = []

    for cid in sorted_cluster_ids:
        cluster_item_set = cluster_to_items[cid]
        # Collect matching pile labels from each model
        candidate_labels: list[str] = []

        for _model_id, cpd in centroid_piles.items():
            best_jaccard = 0.0
            best_label: str | None = None

            for pile, pile_label in zip(cpd.piles, cpd.labels, strict=False):
                pile_set = set(pile)
                # Jaccard = |intersection| / |union|
                intersection = len(cluster_item_set & pile_set)
                union = len(cluster_item_set | pile_set)
                if union == 0:
                    continue
                j = intersection / union
                if j > best_jaccard:
                    best_jaccard = j
                    best_label = pile_label

            if best_jaccard >= jaccard_threshold and best_label is not None:
                candidate_labels.append(best_label)

        if not candidate_labels:
            labels.append("Uncategorized")
            continue

        # Count by case-normalised label; track original form per normalised key
        # so the label we return is the original (not lowercased).
        # When multiple original forms normalise to the same key, keep the
        # shortest one (further ties: lexicographic).
        freq: dict[str, int] = {}
        # canonical_form[normalised] = shortest original label for that key
        canonical_form: dict[str, str] = {}
        for lbl in candidate_labels:
            key = lbl.lower().strip()
            freq[key] = freq.get(key, 0) + 1
            existing = canonical_form.get(key)
            if existing is None or len(lbl) < len(existing) or (
                len(lbl) == len(existing) and lbl < existing
            ):
                canonical_form[key] = lbl

        max_freq = max(freq.values())
        if max_freq > 1:
            # Modal label exists — collect all keys with max frequency
            modal_keys = [k for k, v in freq.items() if v == max_freq]
            # Break ties by shortest original label, then lexicographic
            best_key = min(
                modal_keys,
                key=lambda k: (len(canonical_form[k]), canonical_form[k]),
            )
            labels.append(canonical_form[best_key])
        else:
            # All labels unique — use shortest (ties broken lexicographically)
            best_key = min(
                freq.keys(),
                key=lambda k: (len(canonical_form[k]), canonical_form[k]),
            )
            labels.append(canonical_form[best_key])

    return labels


def _is_finite_float(v: float) -> bool:
    """Return True iff v is a normal finite float (not NaN, not +inf)."""
    return not (np.isnan(v) or np.isinf(v))


def load_records(
    jsonl_path: Path,
    domain_slug: str,
    *,
    qa_only: bool = True,
    collection_mode: str | None = None,
) -> list[InformantRecord]:
    """Load InformantRecords for a domain from the JSONL file.

    Args:
        jsonl_path: Path to informants.jsonl.
        domain_slug: Filter to this domain.
        qa_only: If True, skip records with qa_passed=False.
        collection_mode: If set, filter to this collection mode only
            (e.g., "cross_model_consensus" for comparable cross-model data).

    Returns:
        List of validated InformantRecord objects.
    """
    records = []
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            if data.get("domain_slug") != domain_slug:
                continue
            if qa_only and not data.get("qa_passed", False):
                continue
            if collection_mode and data.get("collection_mode") != collection_mode:
                continue
            records.append(InformantRecord(**data))
    return records


def group_by_model(
    records: list[InformantRecord],
) -> dict[str, list[InformantRecord]]:
    """Group records by model_id."""
    groups: dict[str, list[InformantRecord]] = {}
    for rec in records:
        groups.setdefault(rec.model_id, []).append(rec)
    return groups


def group_by_prompt_version(
    records: list[InformantRecord],
) -> dict[str, list[InformantRecord]]:
    """Group records by freelist prompt_version.

    The sensitivity study encodes prompt variants in
    ``InformantRecord.freelist.prompt_version`` (e.g., "v1_s1" through
    "v1_s8").  The split G1 computation requires records grouped by this
    key so that within-model variance can be measured across phrasings.
    """
    groups: dict[str, list[InformantRecord]] = {}
    for rec in records:
        key = rec.freelist.prompt_version
        groups.setdefault(key, []).append(rec)
    return groups


def _build_free_lists(
    records_by_model: dict[str, list[InformantRecord]],
) -> dict[str, FreeList]:
    """Build consensus free lists per model from collection data."""
    result = {}
    for model_id, recs in records_by_model.items():
        consensus = compute_consensus_free_list(recs)
        items = [item for item, _ in consensus]
        result[model_id] = FreeList(
            run_id=f"consensus_{model_id}",
            model=_model_ref_from_record(recs[0]),
            domain_slug=recs[0].domain_slug,
            items=items,
            raw_order=items,
        )
    return result


def _build_sutrop_metrics(
    records_by_model: dict[str, list[InformantRecord]],
) -> tuple[dict[str, list], dict[str, float]]:
    """Compute Sutrop CSI and Smith's S / Sutrop CSI agreement per model.

    Sutrop's CSI (Sutrop 2001) is more robust to list-length variance than
    Smith's S. See docs/SME_REVIEW.md §2.1. The per-model agreement ρ
    (Spearman rank correlation between the two orderings) flags — via the
    QA_Runner's aggregate check when ρ < 0.85 — cases where list-length
    variance is high enough to distort the salience order.
    """
    sutrop_by_model: dict[str, list] = {}
    agreement_by_model: dict[str, float] = {}
    for model_id, recs in records_by_model.items():
        smith_ranked = compute_consensus_free_list(recs)
        sutrop_ranked = sutrop_csi(recs)
        sutrop_by_model[model_id] = sutrop_ranked
        agreement_by_model[model_id] = compute_salience_agreement(
            smith_ranked, sutrop_ranked,
        )
    return sutrop_by_model, agreement_by_model


def _model_ref_from_record(rec: InformantRecord) -> ModelRef:
    """Extract a ModelRef from an InformantRecord."""
    return ModelRef(
        provider=rec.provider,
        model_id=rec.model_id,
        family=rec.family,
        origin=rec.origin_country,
        open_weights=rec.open_weights,
        collection_method=rec.collection_method,
        quantization=None,
        release_date=rec.collection_date.date(),
        version_label=rec.model_version_returned,
    )


def _build_centroid_piles(
    records_by_model: dict[str, list[InformantRecord]],
    within_model_results: list,
) -> dict[str, CentroidPileData]:
    """Compute per-model centroid pile data for the PileComparison view.

    For each model:
    a. Identify the centroid run via WithinModelResult.centroid_run_id.
    b. Extract parsed_piles and parsed_pile_labels from that run.
    c. Compute per-term pile stability per CDA SME ruling F5
       (2026-05-24-phase9a-cda-sme-verdict.md):
         - For each term in the centroid run, find the set of other terms it
           co-occurs with in its centroid pile (the co-occurring set).
         - For each of the model's other runs, check if the term appears in
           a pile with the SAME set of co-occurring items (set equality, not
           pile index).
         - term_stability[term] = n_runs_same_pile / n_runs_total
       A model with only one run gets term_stability = 1.0 for all terms
       (the single run IS the centroid run — vacuously stable).

    Args:
        records_by_model: Model-keyed InformantRecord lists from group_by_model.
        within_model_results: List of WithinModelResult from Register 1 analysis.

    Returns:
        dict[model_id, CentroidPileData]. Models without a centroid_run_id
        (degenerate single-run or empty) are skipped; they do not appear in
        the returned dict.
    """
    # Build a fast lookup: centroid_run_id → centroid InformantRecord
    # Also build model_id → centroid_run_id from the WithinModelResult list.
    centroid_run_id_by_model: dict[str, str] = {}
    for wm in within_model_results:
        if wm.centroid_run_id is not None:
            centroid_run_id_by_model[wm.model_id] = wm.centroid_run_id

    result: dict[str, CentroidPileData] = {}

    for model_id, recs in records_by_model.items():
        centroid_run_id = centroid_run_id_by_model.get(model_id)
        if centroid_run_id is None:
            # No centroid run identified (e.g. empty model or degenerate case).
            logger.debug(
                "Centroid pile: skipping model %s (no centroid_run_id)", model_id,
            )
            continue

        # Find the centroid record in this model's list.
        centroid_rec: InformantRecord | None = None
        for rec in recs:
            if rec.informant_id == centroid_run_id:
                centroid_rec = rec
                break

        if centroid_rec is None:
            # centroid_run_id points to a record not in the current list
            # (e.g. qa_only filtering excluded it). Skip gracefully.
            logger.warning(
                "Centroid pile: centroid_run_id %s for model %s not found in "
                "records list (%d records); skipping.",
                centroid_run_id,
                model_id,
                len(recs),
            )
            continue

        centroid_piles = centroid_rec.pile_sort.parsed_piles
        centroid_labels = centroid_rec.interview.parsed_pile_labels

        # Build a map: term → frozenset of co-occurring terms in the centroid run.
        # "Co-occurring terms" = all OTHER terms in the same pile.
        # Frozenset enables O(1) set-equality comparison across runs.
        centroid_cooccurrence: dict[str, frozenset[str]] = {}
        for pile in centroid_piles:
            pile_set = frozenset(pile)
            for term in pile:
                # The co-occurring set for a term is the pile minus the term itself.
                centroid_cooccurrence[term] = pile_set - {term}

        n_runs = len(recs)

        # For each term, count how many runs place it in a pile with the
        # identical set of co-occurring terms as the centroid run.
        term_same_pile_count: dict[str, int] = {
            term: 0 for term in centroid_cooccurrence
        }

        for rec in recs:
            # Build this run's term → co-occurring set map.
            run_cooccurrence: dict[str, frozenset[str]] = {}
            for pile in rec.pile_sort.parsed_piles:
                pile_set = frozenset(pile)
                for term in pile:
                    run_cooccurrence[term] = pile_set - {term}

            for term, centroid_coset in centroid_cooccurrence.items():
                run_coset = run_cooccurrence.get(term)
                if run_coset is not None and run_coset == centroid_coset:
                    term_same_pile_count[term] += 1

        # Stability = fraction of ALL runs (including the centroid run itself).
        # The centroid run always matches itself, so stability is always >= 1/n_runs.
        term_stability = {
            term: count / n_runs
            for term, count in term_same_pile_count.items()
        }

        result[model_id] = CentroidPileData(
            piles=centroid_piles,
            labels=centroid_labels,
            term_stability=term_stability,
        )

    return result


def run_pipeline(
    records: list[InformantRecord],
    *,
    analysis_version: str = "0.1",
    n_bootstrap: int = 500,
) -> DomainResult:
    """Run the full analysis pipeline on a set of InformantRecords.

    Args:
        records: All records for one domain (may span multiple models).
        analysis_version: Semantic version string for this analysis run.
        n_bootstrap: Number of bootstrap resamples.

    Returns:
        A fully populated DomainResult ready for JSON serialization.
    """
    if not records:
        msg = "No records provided"
        raise ValueError(msg)

    domain_slug = records[0].domain_slug
    records_by_model = group_by_model(records)
    model_ids = sorted(records_by_model.keys())

    logger.info(
        "Pipeline: %s, %d models, %d total records",
        domain_slug, len(model_ids), len(records),
    )

    # 1. Consensus free lists per model
    free_lists = _build_free_lists(records_by_model)
    logger.info("Built consensus free lists for %d models", len(free_lists))

    # 1b. Sutrop CSI + Smith's S / Sutrop agreement per model (SME §2.1)
    sutrop_by_model, salience_agreement = _build_sutrop_metrics(records_by_model)
    logger.info(
        "Built Sutrop CSI for %d models; agreement rho range [%.3f, %.3f]",
        len(sutrop_by_model),
        min(salience_agreement.values()) if salience_agreement else 1.0,
        max(salience_agreement.values()) if salience_agreement else 1.0,
    )

    # 1c. Register 1 within-model analysis per model (SME two-level design,
    # ARCHITECTURE.md §4.2.7). Produces one WithinModelResult per model
    # carrying OCI, per-run centrality, centroid run id, and the
    # deterministic_output marker that drives DESIGN_SYSTEM.md §3.3.5
    # rendering. Bootstrap CI is left off here (n_bootstrap=0) because
    # Register 2 bootstrap already runs below and Level 1 bootstrap has
    # the documented underestimation caveat — a separate uncertainty
    # pass at Level 1 can be added later if the Phase 4b data motivates
    # it. See docs/BOOTSTRAP_DESIGN.md §2.
    within_model_results = [
        run_within_model_analysis(records_by_model[mid])
        for mid in model_ids
    ]
    n_deterministic = sum(1 for wm in within_model_results if wm.deterministic_output)
    logger.info(
        "Built Register 1 WithinModelResult for %d models; "
        "%d flagged deterministic_output",
        len(within_model_results), n_deterministic,
    )

    # 1d. Centroid pile data for the PileComparison view (Phase 9a T9).
    # Uses within_model_results to locate the centroid run for each model,
    # then extracts pile structure + labels + per-term stability from the raw
    # InformantRecords. No LLM calls, no new dependencies — pure data access.
    # CDA SME ruling F5: "same pile" is set equality of co-occurring items,
    # not pile index. See _build_centroid_piles for the full implementation.
    centroid_piles = _build_centroid_piles(records_by_model, within_model_results)
    logger.info(
        "Built centroid pile data for %d models", len(centroid_piles),
    )

    # 2. Co-occurrence matrices per model
    matrices: list[CooccurrenceMatrix] = []
    model_matrices: dict[str, CooccurrenceMatrix] = {}
    for mid in model_ids:
        mat = build_cooccurrence_matrix(records_by_model[mid])
        matrices.append(mat)
        model_matrices[mid] = mat
    logger.info("Built %d co-occurrence matrices", len(matrices))

    # 2b-pre. Term-set truncation (Phase 9a term-truncation task).
    # Reduces the pooled term set from the full union to the shared
    # vocabulary that enters the pooled co-occurrence matrix.
    #
    # Per CDA SME T1/T2 (2026-05-24-phase9a-term-truncation-sme-ruling.md):
    #   1. Compute cross-model term frequency (f_models per term), operating
    #      on pile_sort.parsed_piles (not freelist.parsed_items).
    #   2. Pre-filter: remove terms with f_models < 2 (hard floor — single-
    #      model terms are definitionally not shared vocabulary).
    #   3. Apply find_salience_elbow() with min_items=15, max_items=300 to
    #      the frequency curve.
    #   4. Pass the truncated item list to build_pooled_cooccurrence_matrix().
    #
    # Per CDA SME T4: per-model MDS (step 2d) is NOT truncated — each model's
    # own matrix uses its full pile-sort vocabulary.
    _TRUNCATION_MIN_ITEMS = 15
    _TRUNCATION_MAX_ITEMS = 300
    _TRUNCATION_MIN_MODEL_COUNT = 2

    term_freq = compute_cross_model_term_frequency(records_by_model)
    term_n_total = len(term_freq)

    # Pre-filter: hard floor at f_models >= min_model_count
    shared_terms = [(t, f) for t, f in term_freq if f >= _TRUNCATION_MIN_MODEL_COUNT]

    # Apply elbow detection to the shared-terms frequency curve
    if len(shared_terms) > 0:
        elbow_index = find_salience_elbow(
            [(t, float(f)) for t, f in shared_terms],
            min_items=_TRUNCATION_MIN_ITEMS,
            max_items=_TRUNCATION_MAX_ITEMS,
        )
    else:
        elbow_index = 0

    truncated_items = [t for t, _ in shared_terms[:elbow_index]]
    term_n_after = len(truncated_items)

    logger.info(
        "Term truncation: %d total → %d terms "
        "(f_models >= %d pre-filter, elbow at index %d)",
        term_n_total,
        term_n_after,
        _TRUNCATION_MIN_MODEL_COUNT,
        elbow_index,
    )

    # Record truncation metadata for the DomainResult
    _truncation_method = "cross_model_frequency_elbow"
    _truncation_params: dict = {
        "min_items": _TRUNCATION_MIN_ITEMS,
        "max_items": _TRUNCATION_MAX_ITEMS,
        "min_model_count": _TRUNCATION_MIN_MODEL_COUNT,
        "elbow_index": elbow_index,
    }

    # When truncated_items is empty (degenerate: no shared terms), pass
    # item_subset=None to let build_pooled_cooccurrence_matrix() use its
    # full-union fallback so downstream steps degrade gracefully.
    pooled_item_subset: list[str] | None = truncated_items if truncated_items else None

    # 2b. Pooled cross-model term co-occurrence matrix (Phase 9a T1).
    # Equal-weight-per-model per CDA SME M1: compute each model's consensus
    # matrix, then average with denominator always = M.
    # item_subset is the truncated list from the truncation step above.
    pooled_matrix = build_pooled_cooccurrence_matrix(
        records_by_model, item_subset=pooled_item_subset,
    )
    logger.info(
        "Built pooled co-occurrence matrix: %d items", len(pooled_matrix.items),
    )

    # 2c. Pooled term MDS (Phase 9a T2).
    # run_item_mds() already exists; wire the pooled matrix into it.
    # Returns dict[item_name → (x, y)].
    if len(pooled_matrix.items) >= 3:
        pooled_item_coords = run_item_mds(pooled_matrix)
        term_mds_items = pooled_matrix.items
        # Serialise as dict[str, list[float]] per schema (list, not tuple)
        term_mds_coordinates: dict[str, list[float]] = {
            item: [float(x), float(y)]
            for item, (x, y) in pooled_item_coords.items()
        }
        logger.info("Computed pooled term MDS for %d items", len(term_mds_items))
    else:
        term_mds_coordinates = {}
        term_mds_items = pooled_matrix.items
        logger.info(
            "Pooled term MDS skipped (< 3 items: %d)", len(pooled_matrix.items),
        )

    # 2d. Per-model term MDS (Phase 9a T2 — populates mds_within_model).
    # Store as list[dict] where each dict is {"item": str, "x": float, "y": float}.
    # WithinModelResult.mds_within_model currently holds list[list[float]];
    # per the task spec it is populated with list[dict] here.
    # Implementation note: WithinModelResult is a Pydantic model with
    # mds_within_model: list = []; we populate it post-construction via
    # model_copy(update=...) to respect immutability.
    per_model_mds: dict[str, list[dict]] = {}
    per_model_mds_stress: dict[str, float] = {}
    for mid in model_ids:
        mat = model_matrices[mid]
        if len(mat.items) >= 3:
            item_coords, stress = run_item_mds_with_stress(mat)
            per_model_mds[mid] = [
                {"item": item, "x": float(x), "y": float(y)}
                for item, (x, y) in item_coords.items()
            ]
            per_model_mds_stress[mid] = stress
        else:
            per_model_mds[mid] = []
    logger.info("Computed per-model term MDS for %d models", len(per_model_mds))

    # 2e. Term-level AHC (Phase 9a T3).
    # Average linkage (UPGMA), distance = 1 - co-occurrence, per CDA SME M2/M3.
    if len(pooled_matrix.items) >= 2:
        term_cluster_result = cluster_terms(pooled_matrix)
        # Serialise linkage matrix as nested list (each row is one merge step)
        term_cluster_linkage: list[list[float]] = [
            [float(v) for v in row]
            for row in term_cluster_result.linkage_matrix
        ]
        term_cluster_assignments: dict[str, int] = {
            item: label
            for item, label in zip(
                term_cluster_result.items, term_cluster_result.labels, strict=True
            )
        }
        logger.info(
            "Computed term AHC: %d items, %d clusters",
            len(term_cluster_result.items),
            term_cluster_result.n_clusters,
        )
    else:
        term_cluster_linkage = []
        term_cluster_assignments = {}
        logger.info(
            "Term AHC skipped (< 2 items: %d)", len(pooled_matrix.items),
        )

    # 2f-pre. T5 cluster label aggregation (Phase 9a T5).
    # Uses the centroid_piles already built in step 1d and the AHC assignments
    # from step 2e.  Must run after both are available.
    # Per CDA SME M6: frequency-weighted modal label via Jaccard overlap (>= 0.3).
    # "Uncategorized" when no pile exceeds the threshold.
    # No LLM calls — pure string matching.
    term_cluster_labels: list[str] = []
    if term_cluster_assignments and centroid_piles:
        term_cluster_labels = aggregate_cluster_labels(
            term_cluster_assignments,
            centroid_piles,
        )
        logger.info(
            "Cluster label aggregation: %d clusters labeled",
            len(term_cluster_labels),
        )
    else:
        logger.info(
            "Cluster label aggregation skipped "
            "(no cluster_assignments=%d or no centroid_piles=%d)",
            len(term_cluster_assignments),
            len(centroid_piles),
        )

    # 2f. Term-level bootstrap uncertainty (Phase 9a T4).
    # Per CDA SME M4 (2026-05-24-phase9a-cda-sme-verdict.md):
    #   Resampling unit = models (Register 2 informants). Uses pre-computed
    #   per-model consensus matrices. B=200 per CDA SME F4.
    #
    # Per M4a: resulting CIs reflect between-model structural variance only.
    # The methods page must state: "Term position confidence reflects agreement
    # across models, not within-model sampling variance."
    #
    # Requires at least 3 items in the pooled matrix for MDS to be meaningful.
    term_mds_uncertainty: dict = {}
    term_cluster_bp_values: list[float] = []

    if len(model_matrices) >= 1 and len(pooled_matrix.items) >= 3 and term_mds_coordinates:
        # Build a typed reference_coordinates dict from the stored term_mds_coordinates
        # (which are already computed above as dict[str, list[float]])
        ref_coords_typed: dict[str, tuple[float, float]] = {
            item: (float(xy[0]), float(xy[1]))
            for item, xy in term_mds_coordinates.items()
        }
        try:
            term_ellipses = bootstrap_term_mds_ellipses(
                per_model_matrices=model_matrices,
                reference_coordinates=ref_coords_typed,
                reference_items=pooled_matrix.items,
                n_bootstrap=200,
                random_state=42,
            )
            # Serialize as dict[str, dict] for JSON round-trip via Pydantic Any field
            term_mds_uncertainty = {
                item: ellipse.model_dump()
                for item, ellipse in term_ellipses.items()
            }
            logger.info(
                "Term bootstrap ellipses: %d items, n_bootstrap=%d",
                len(term_mds_uncertainty),
                200,
            )
        except Exception:
            logger.warning(
                "Term bootstrap ellipses: failed, leaving empty.",
                exc_info=True,
            )

        # Branch stability bootstrap (CDA SME M5): BP per internal node.
        # Requires the AHC linkage computed in 2e.
        if term_cluster_linkage:
            try:
                ref_linkage_arr = np.array(term_cluster_linkage, dtype=np.float64)
                term_cluster_bp_values = bootstrap_branch_stability(
                    per_model_matrices=model_matrices,
                    reference_linkage=ref_linkage_arr,
                    reference_items=pooled_matrix.items,
                    n_bootstrap=200,
                    random_state=42,
                )
                logger.info(
                    "Term branch stability: %d internal nodes computed",
                    len(term_cluster_bp_values),
                )
            except Exception:
                logger.warning(
                    "Term branch stability: failed, leaving empty.",
                    exc_info=True,
                )

    # 3. Cross-model similarity + MDS + bootstrap
    if len(model_ids) >= 2:
        coords, ellipses, sim_mean, sim_ci = bootstrap_mds_ellipses(
            records_by_model, n_bootstrap=n_bootstrap,
        )

        similarity_matrix = sim_mean.tolist()
        similarity_ci = [
            [
                (float(sim_ci[i, j, 0]), float(sim_ci[i, j, 1]))
                for j in range(len(model_ids))
            ]
            for i in range(len(model_ids))
        ]
    else:
        # Single model — no cross-model comparison possible
        mid = model_ids[0]
        coords = {mid: (0.0, 0.0)}
        from cdb_core import BootstrapEllipse
        ellipses = {
            mid: BootstrapEllipse(
                center=(0.0, 0.0),
                semi_major=0.0,
                semi_minor=0.0,
                rotation_rad=0.0,
                n_bootstrap=0,
            ),
        }
        similarity_matrix = [[1.0]]
        similarity_ci = [[(1.0, 1.0)]]

    # 3b. Cultural centrality scores (first eigenvector of similarity matrix)
    # n<2 degenerate case: return empty dict (not meaningful for centrality).
    if len(model_ids) >= 2:
        sim_np = np.array(similarity_matrix, dtype=np.float64)
        cultural_centrality_scores = compute_centrality_scores(model_ids, sim_np)
    else:
        cultural_centrality_scores = {}
    negative_centrality_flag = any(v < 0 for v in cultural_centrality_scores.values())
    negative_centrality_models = [
        mid for mid, v in cultural_centrality_scores.items() if v < 0
    ]
    logger.info(
        "Cultural centrality: %d models scored, %d negative",
        len(cultural_centrality_scores), len(negative_centrality_models),
    )

    # 3c. Romney CCM eigenratio (λ₁/λ₂ of the inter-model similarity matrix).
    # Insertion point: immediately after centrality block (commit de6bf73),
    # before clustering. Both consume sim_np; contiguous placement keeps the
    # methodology computations together.
    if len(model_ids) >= 2:
        sim_np_romney = np.array(similarity_matrix, dtype=np.float64)
        romney_eigenratio: float | None = compute_romney_eigenratio(sim_np_romney)
        if romney_eigenratio is not None:
            romney_consensus_pass: bool | None = romney_eigenratio >= ROMNEY_THRESHOLD_LSB
            romney_consensus_warning: bool | None = (
                ROMNEY_THRESHOLD_CLASSIC <= romney_eigenratio < ROMNEY_THRESHOLD_LSB
            )
            # Small-n threshold is n < 15, per CDA SME reconciliation
            # (docs/status/2026-04-23-small-n-threshold-sme-amendment.md).
            # Grounded in SME_REVIEW.md §1.1 small-n rationale (Anders &
            # Batchelder 2015; RWB 1986 calibration at n=20-40). Supersedes
            # the F2-T02 n<8 threshold from 2026-04-20.
            romney_small_n_warning: bool = len(model_ids) < 15
            logger.info(
                "Romney CCM: eigenratio=%.3f, pass=%s, warning=%s, small_n=%s",
                romney_eigenratio,
                romney_consensus_pass,
                romney_consensus_warning,
                romney_small_n_warning,
            )
        else:
            # Rank-1 degenerate (perfect consensus, λ₂ ≈ 0): ratio undefined.
            romney_consensus_pass = None
            romney_consensus_warning = None
            romney_small_n_warning = False
            logger.info("Romney CCM: degenerate (second eigenvalue ≈ 0), eigenratio=None")
    else:
        # n < 2: no inter-model agreement structure.
        romney_eigenratio = None
        romney_consensus_pass = None
        romney_consensus_warning = None
        romney_small_n_warning = False
        logger.info("Romney skipped (n<2)")

    # 3d. Caulkins six-state typology (F2-T01).
    # Requires both eigenratio (T02) and centrality_scores (T03) to be present.
    # Degenerate cases: consensus_type=None when either input is unavailable.
    consensus_type: ConsensusType | None
    if romney_eigenratio is not None and cultural_centrality_scores:
        consensus_type = classify_consensus(
            eigenratio=romney_eigenratio,
            centrality_scores=cultural_centrality_scores,
        )
        logger.info("Caulkins typology: consensus_type=%s", consensus_type)
    else:
        consensus_type = None
        logger.info(
            "Caulkins typology: consensus_type=None "
            "(eigenratio=%s, centrality_scores_count=%d)",
            romney_eigenratio,
            len(cultural_centrality_scores),
        )

    # 3e. Split G1 stability (SME §1.3 un-deferred 2026-04-20).
    # Fires only when at least one model has ≥2 distinct prompt_version
    # values (i.e., a sensitivity-cell collection with prompt variants).
    # Single-prompt-version runs leave all six g1_* fields as None.
    #
    # Within-model variance is computed per model (using that model's
    # records grouped by prompt_version), then averaged across all models
    # that have ≥2 variants. This respects build_cooccurrence_matrix's
    # requirement that all records in a batch belong to the same model.
    #
    # Threshold is 0.5 per axis per the CDA SME verdict (binding); both
    # axes must be below 0.5 for g1_overall_pass to be True.
    g1_salience_stability: float | None = None
    g1_spatial_stability: float | None = None
    g1_aggregate_stability: float | None = None
    g1_salience_pass: bool | None = None
    g1_spatial_pass: bool | None = None
    g1_overall_pass: bool | None = None

    # Identify which models have ≥2 prompt_version values (sensitivity models)
    sensitivity_within_salience: list[float] = []
    sensitivity_within_spatial: list[float] = []

    for mid in model_ids:
        model_records = records_by_model[mid]
        by_variant = group_by_prompt_version(model_records)
        if len(by_variant) >= 2:
            sensitivity_within_salience.append(
                compute_within_model_salience_variance(by_variant),
            )
            sensitivity_within_spatial.append(
                compute_within_model_spatial_variance(by_variant),
            )

    if sensitivity_within_salience:
        try:
            # Average within-model variance across all sensitivity models
            within_salience = float(
                sum(sensitivity_within_salience) / len(sensitivity_within_salience)
            )
            within_spatial = float(
                sum(sensitivity_within_spatial) / len(sensitivity_within_spatial)
            )
            between_salience = compute_between_model_salience_variance(records_by_model)
            between_spatial = compute_between_model_spatial_variance(records_by_model)

            # Guard against NaN / inf from degenerate inputs
            if not all(
                _is_finite_float(v)
                for v in (
                    within_salience, between_salience,
                    within_spatial, between_spatial,
                )
            ):
                logger.warning(
                    "G1 split: one or more variance inputs invalid "
                    "(NaN/inf); skipping G1 split.",
                )
            else:
                g1_result: G1SplitResult = g1_stability_split(
                    within_salience_variance=within_salience,
                    between_salience_variance=between_salience,
                    within_spatial_variance=within_spatial,
                    between_spatial_variance=between_spatial,
                    threshold=0.5,
                )
                g1_salience_stability = g1_result.salience_stability
                g1_spatial_stability = g1_result.spatial_stability
                g1_aggregate_stability = g1_result.aggregate_stability
                g1_salience_pass = g1_result.salience_pass
                g1_spatial_pass = g1_result.spatial_pass
                g1_overall_pass = g1_result.g1_pass
                logger.info(
                    "G1 split: salience=%.3f (pass=%s), spatial=%.3f (pass=%s),"
                    " overall=%s",
                    g1_salience_stability,
                    g1_salience_pass,
                    g1_spatial_stability,
                    g1_spatial_pass,
                    g1_overall_pass,
                )
        except Exception:
            logger.warning(
                "G1 split: unexpected error computing variance; "
                "leaving G1 fields None.",
                exc_info=True,
            )
    else:
        logger.info("G1 split skipped (single prompt_version)")

    # 4. Clustering
    if len(model_ids) >= 2:
        _, sim_for_cluster = compute_cross_model_similarity(matrices)
        cluster_result = cluster_models(model_ids, sim_for_cluster)
        logger.info(
            "Clustering: %d clusters", cluster_result.n_clusters,
        )

    # 5. Consensus score (placeholder — full CCA requires Phase 4)
    # Use mean pairwise similarity as a proxy
    if len(model_ids) >= 2:
        upper_vals = []
        for i in range(len(model_ids)):
            for j in range(i + 1, len(model_ids)):
                upper_vals.append(sim_mean[i, j])
        consensus_score = float(np.mean(upper_vals))
        consensus_ci_vals = (
            float(np.percentile(upper_vals, 2.5)),
            float(np.percentile(upper_vals, 97.5)),
        )
    else:
        consensus_score = 1.0
        consensus_ci_vals = (1.0, 1.0)

    # 6. Build model refs
    models = [_model_ref_from_record(records_by_model[mid][0]) for mid in model_ids]

    mds_coordinates = {
        mid: coords[mid] for mid in model_ids
    }
    mds_uncertainty = {
        mid: ellipses[mid] for mid in model_ids
    }

    # Populate mds_within_model on each WithinModelResult.
    # Per F3 (CDA SME verdict): per-model item MDS is Register 1 output.
    # WithinModelResult is a Pydantic model so we rebuild the list with
    # updated objects via model_copy(update=...).
    within_model_results_final = []
    for wm in within_model_results:
        updates: dict[str, object] = {}
        mds_data = per_model_mds.get(wm.model_id, [])
        if mds_data:
            updates["mds_within_model"] = mds_data
        wm_stress = per_model_mds_stress.get(wm.model_id)
        if wm_stress is not None:
            updates["within_model_mds_stress"] = wm_stress
        if updates:
            wm = wm.model_copy(update=updates)
        within_model_results_final.append(wm)

    return DomainResult(
        domain_slug=domain_slug,
        analysis_version=analysis_version,
        models=models,
        free_lists=free_lists,
        mds_coordinates=mds_coordinates,
        mds_uncertainty=mds_uncertainty,
        similarity_matrix=similarity_matrix,
        similarity_ci=similarity_ci,
        consensus_score=consensus_score,
        consensus_ci=consensus_ci_vals,
        romney_eigenratio=romney_eigenratio,
        romney_consensus_pass=romney_consensus_pass,
        romney_consensus_warning=romney_consensus_warning,
        romney_small_n_warning=romney_small_n_warning,
        sutrop_csi=sutrop_by_model,
        salience_index_agreement=salience_agreement,
        within_model_results=within_model_results_final,
        g1_salience_stability=g1_salience_stability,
        g1_spatial_stability=g1_spatial_stability,
        g1_aggregate_stability=g1_aggregate_stability,
        g1_salience_pass=g1_salience_pass,
        g1_spatial_pass=g1_spatial_pass,
        g1_overall_pass=g1_overall_pass,
        groundings=[],
        selected_baseline_id=None,
        generated_lede="",  # Populated by cdb_publish, not cdb_analyze
        generated_at=datetime.now(UTC),
        cultural_centrality_scores=cultural_centrality_scores,
        negative_centrality_flag=negative_centrality_flag,
        negative_centrality_models=negative_centrality_models,
        consensus_type=consensus_type,
        centroid_piles=centroid_piles,
        term_mds_coordinates=term_mds_coordinates,
        term_mds_items=term_mds_items,
        term_cluster_linkage=term_cluster_linkage,
        term_cluster_assignments=term_cluster_assignments,
        term_cluster_labels=term_cluster_labels,
        term_mds_uncertainty=term_mds_uncertainty,
        term_cluster_bp_values=term_cluster_bp_values,
        term_truncation_method=_truncation_method,
        term_truncation_params=_truncation_params,
        term_n_total_before_truncation=term_n_total,
        term_n_after_truncation=term_n_after,
    )


def write_result(result: DomainResult, output_dir: Path) -> Path:
    """Write a DomainResult to its canonical JSON path.

    Returns:
        The path written.
    """
    domain_dir = output_dir / result.domain_slug
    domain_dir.mkdir(parents=True, exist_ok=True)
    out_path = domain_dir / f"{result.analysis_version}.json"
    out_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    logger.info("Wrote %s", out_path)
    return out_path
