"""Saturation analysis — empirical N selection for Register 1.

Part of the post-F1 SME review plan. Before setting operational N
for within-model analysis (Register 1), sweep N across a range on a
small set of reference models and observe the curves:

- Spearman ρ of Smith's S rank ordering at N vs N + k
- Output Concentration Index (OCI) stability at N vs N + k
- Elbow-position stability across N
- Within-model MDS Procrustes RMSE at N vs N + k

The "knee" in each curve is where additional N stops adding
information. Operational N is set at the knee plus a 20% safety
margin.

Per the standing authority for PR #6, the saturation analysis runs
on Claude Opus 4.6, GPT-4o, and Llama 3.1 70B across the family and
holidays domains. It piggybacks on the Phase 4b prompt-sensitivity
study budget envelope. Findings surface on the public methodology
page as a named methods contribution (**not** framed as publishable
per ARCHITECTURE.md §1.5.6).

This module provides the deterministic analysis machinery. The
actual data collection is performed by ``scripts/collect.py`` with
a special ``--saturation`` mode; this module consumes the resulting
records and produces the saturation curves.

See ARCHITECTURE.md §5.3 Phase 4b and docs/SME_REVIEW.md §3.2.
"""

from __future__ import annotations

from dataclasses import dataclass

from cdb_core import InformantRecord

from cdb_analyze.consensus import (
    compute_consensus_free_list,
    find_salience_elbow,
)
from cdb_analyze.salience import compute_salience_agreement, sutrop_csi
from cdb_analyze.two_level import compute_oci


@dataclass(frozen=True)
class SaturationPoint:
    """One row of the saturation curve at a specific N."""
    n_runs: int
    oci: float
    elbow_index: int
    smith_vs_sutrop_rho: float
    # Delta vs the previous N in the sweep — null for the first point.
    delta_top_k_jaccard: float | None = None


def saturation_curve(
    records: list[InformantRecord],
    *,
    n_values: tuple[int, ...] = (5, 10, 15, 20, 25, 30),
    top_k_for_stability: int = 20,
) -> list[SaturationPoint]:
    """Produce a saturation curve for one (model, domain) record list.

    For each N in ``n_values``, takes the first N records (ordered by
    ``run_index``) and computes OCI, elbow position, and Smith-vs-Sutrop
    agreement. For each N after the first, also reports the Jaccard
    overlap of the top ``top_k_for_stability`` Smith's S items at N
    vs N-previous — a direct "does the salience order keep changing"
    measure.

    Args:
        records: InformantRecords for one (model, domain). The first
            N records (after sorting by ``run_index``) are used at
            each sweep point.
        n_values: N values to evaluate. Values above ``len(records)``
            are skipped.
        top_k_for_stability: K used for the top-K Jaccard overlap.

    Returns:
        List of SaturationPoint, sorted by n_runs ascending. Empty
        list if no N values are reachable with the given records.
    """
    sorted_records = sorted(records, key=lambda r: r.run_index)
    available = len(sorted_records)

    points: list[SaturationPoint] = []
    prev_top_k: set[str] = set()

    for n in n_values:
        if n > available:
            continue
        subset = sorted_records[:n]
        consensus = compute_consensus_free_list(subset)
        top_k = {item for item, _ in consensus[:top_k_for_stability]}

        elbow = find_salience_elbow(consensus)
        oci_val = compute_oci(subset) if n >= 2 else 0.0
        sutrop = sutrop_csi(subset)
        rho = compute_salience_agreement(consensus, sutrop)

        delta: float | None = None
        if points:  # not the first point
            intersect = len(top_k & prev_top_k)
            union = len(top_k | prev_top_k)
            delta = intersect / union if union else 1.0

        points.append(
            SaturationPoint(
                n_runs=n,
                oci=oci_val,
                elbow_index=elbow,
                smith_vs_sutrop_rho=rho,
                delta_top_k_jaccard=delta,
            )
        )
        prev_top_k = top_k

    return points


def identify_knee(
    points: list[SaturationPoint],
    *,
    delta_threshold: float = 0.90,
    safety_margin: float = 1.20,
) -> int | None:
    """Identify the operational N per the SME plan.

    The knee is the first N at which ``delta_top_k_jaccard`` meets or
    exceeds ``delta_threshold`` — i.e., the top-K Smith's S items
    have stabilized. Operational N is the knee N multiplied by
    ``safety_margin`` (rounded up).

    Returns None when no sweep point reaches the threshold (meaning
    the curve has not saturated in the range explored, which is
    itself a finding — expand the sweep).
    """
    for pt in points:
        if pt.delta_top_k_jaccard is not None and pt.delta_top_k_jaccard >= delta_threshold:
            return int(pt.n_runs * safety_margin + 0.5)
    return None


# Reference models for the Phase 4b saturation analysis per the
# standing authority in the post-F1 SME review sequence.
SATURATION_REFERENCE_MODELS: tuple[str, ...] = (
    "claude-opus-4-6",
    "gpt-4o",
    "llama-3.1-70b",
)
SATURATION_REFERENCE_DOMAINS: tuple[str, ...] = ("family", "holidays")
