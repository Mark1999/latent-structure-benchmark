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
    CooccurrenceMatrix,
    DomainResult,
    FreeList,
    InformantRecord,
    ModelRef,
)

from cdb_analyze.bootstrap import bootstrap_mds_ellipses
from cdb_analyze.cluster import cluster_models
from cdb_analyze.consensus import compute_consensus_free_list
from cdb_analyze.cooccurrence import build_cooccurrence_matrix
from cdb_analyze.mds import compute_cross_model_similarity

logger = logging.getLogger(__name__)


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
    with open(jsonl_path) as f:
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

    # 2. Co-occurrence matrices per model
    matrices: list[CooccurrenceMatrix] = []
    for mid in model_ids:
        mat = build_cooccurrence_matrix(records_by_model[mid])
        matrices.append(mat)
    logger.info("Built %d co-occurrence matrices", len(matrices))

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
        groundings=[],
        selected_baseline_id=None,
        generated_lede="",  # Populated by cdb_publish, not cdb_analyze
        generated_at=datetime.now(UTC),
    )


def write_result(result: DomainResult, output_dir: Path) -> Path:
    """Write a DomainResult to its canonical JSON path.

    Returns:
        The path written.
    """
    domain_dir = output_dir / result.domain_slug
    domain_dir.mkdir(parents=True, exist_ok=True)
    out_path = domain_dir / f"{result.analysis_version}.json"
    out_path.write_text(result.model_dump_json(indent=2))
    logger.info("Wrote %s", out_path)
    return out_path
