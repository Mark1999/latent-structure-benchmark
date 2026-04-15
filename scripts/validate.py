"""Run Phase 4 validation gates on collected data.

See ARCHITECTURE.md §5.3. All three gates must pass before Phase 5.

Usage:
    python scripts/validate.py --domain family
    python scripts/validate.py --domain family --mode cross_model_consensus
    python scripts/validate.py --domain family --g2-perms 9999
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
from cdb_analyze.cooccurrence import build_cooccurrence_matrix
from cdb_analyze.gates import (
    GateResult,
    g1_stability,
    g2_signal,
    g3_replication,
)
from cdb_analyze.pipeline import group_by_model, load_records
from cdb_analyze.sensitivity import (
    compute_between_model_variance,
    compute_within_model_variance,
)
from cdb_core import InformantRecord

logger = logging.getLogger(__name__)

DEFAULT_JSONL = Path("data/raw/informants.jsonl")


def _print_gate(result: GateResult) -> None:
    status = "PASS" if result.passed else "FAIL"
    print(f"  [{status}] {result.gate}: {result.detail}")


def _extract_shared_vectors(
    records_by_model: dict[str, list],
    model_ids: list[str],
) -> list[tuple[str, np.ndarray]]:
    """Build co-occurrence matrices and extract upper-triangle vectors on shared items."""
    matrices = [
        build_cooccurrence_matrix(records_by_model[mid])
        for mid in model_ids
    ]

    # Find shared items
    shared_items = set(matrices[0].items)
    for m in matrices[1:]:
        shared_items &= set(m.items)
    shared = sorted(shared_items)

    if len(shared) < 3:
        msg = f"Only {len(shared)} shared items — need ≥3"
        raise ValueError(msg)

    result = []
    for mid, mat in zip(model_ids, matrices, strict=True):
        idx = {item: i for i, item in enumerate(mat.items)}
        vals = []
        for i in range(len(shared)):
            for j in range(i + 1, len(shared)):
                ri, rj = idx[shared[i]], idx[shared[j]]
                vals.append(mat.matrix[ri][rj])
        result.append((mid, np.array(vals, dtype=np.float64)))

    return result


def _is_sensitivity_variant(version: str) -> bool:
    """Check if a prompt version string is a sensitivity variant."""
    return version.startswith("v1_s")


def _group_by_variant(
    records: list[InformantRecord],
) -> dict[str, list[InformantRecord]]:
    """Group records by their freelist prompt_version (sensitivity variant)."""
    groups: dict[str, list[InformantRecord]] = {}
    for rec in records:
        ver = rec.freelist.prompt_version
        groups.setdefault(ver, []).append(rec)
    return groups


def _run_g1(
    all_records: list[InformantRecord],
    by_model: dict[str, list[InformantRecord]],
) -> GateResult | None:
    """Run G1 stability gate if sensitivity data is available.

    Detects sensitivity variant records (prompt_version matching v1_s*),
    groups them by variant per model, computes within-model variance
    for each reference model, averages, and compares against between-model
    variance from the full 12-model slate.
    """
    # Find sensitivity variant records
    variant_records = [
        r for r in all_records
        if _is_sensitivity_variant(r.freelist.prompt_version)
    ]

    if not variant_records:
        print("  [SKIP] No sensitivity variant records found (v1_s*).")
        print("         Run Phase 4b collection first:")
        print("         python scripts/collect.py --domain family \\")
        print("           --model claude-opus-4-6 --prompt-version v1_s1 --runs 5")
        return None

    # Group variant records by model
    variant_by_model: dict[str, list[InformantRecord]] = {}
    for rec in variant_records:
        variant_by_model.setdefault(rec.model_id, []).append(rec)

    ref_model_ids = sorted(variant_by_model.keys())
    print(f"  Reference models with variant data: {', '.join(ref_model_ids)}")

    # Compute within-model variance per reference model
    within_variances = []
    for mid in ref_model_ids:
        recs = variant_by_model[mid]
        by_variant = _group_by_variant(recs)
        n_variants = len(by_variant)
        print(f"    {mid}: {len(recs)} records across {n_variants} variants")

        if n_variants < 3:
            print(f"      Need ≥3 variants, got {n_variants} — skipping this model")
            continue

        wv = compute_within_model_variance(by_variant)
        within_variances.append(wv)
        print(f"      Within-model variance: {wv:.6f}")

    if not within_variances:
        print("  [SKIP] No reference model has ≥3 variants with data.")
        return None

    mean_within = float(np.mean(within_variances))

    # Between-model variance from the full slate (non-variant records)
    non_variant_by_model = {
        mid: [r for r in recs if not _is_sensitivity_variant(r.freelist.prompt_version)]
        for mid, recs in by_model.items()
    }
    non_variant_by_model = {mid: recs for mid, recs in non_variant_by_model.items() if recs}

    if len(non_variant_by_model) < 2:
        print("  [SKIP] Need ≥2 models with non-variant data for between-model variance.")
        return None

    between_var = compute_between_model_variance(non_variant_by_model)

    print(f"  Mean within-model variance: {mean_within:.6f}")
    print(f"  Between-model variance:     {between_var:.6f}")

    g1_result = g1_stability(mean_within, between_var)
    _print_gate(g1_result)
    return g1_result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Phase 4 validation gates. See ARCHITECTURE.md §5.3.",
    )
    parser.add_argument(
        "--domain", required=True, help="Domain slug (e.g., family)",
    )
    parser.add_argument(
        "--input", type=Path, default=DEFAULT_JSONL,
        help="Input JSONL path",
    )
    parser.add_argument(
        "--mode", default=None,
        help="Filter to collection mode (e.g., cross_model_consensus)",
    )
    parser.add_argument(
        "--g2-perms", type=int, default=9999,
        help="Number of permutations for G2 (default: 9999)",
    )
    parser.add_argument(
        "--g3-trials", type=int, default=100,
        help="Number of split-half trials for G3 (default: 100)",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    # Load data
    records = load_records(args.input, args.domain, collection_mode=args.mode)
    if not records:
        print(
            f"No QA-passed records for domain '{args.domain}' in {args.input}",
            file=sys.stderr,
        )
        return 1

    by_model = group_by_model(records)
    model_ids = sorted(by_model.keys())

    print(f"Validation gates — domain: {args.domain}")
    print(f"  Records: {len(records)}, Models: {len(model_ids)}")
    for mid in model_ids:
        print(f"    {mid}: {len(by_model[mid])} runs")
    print()

    results: list[GateResult] = []

    # --- G1: Stability ---
    print("G1 — Stability (prompt-sensitivity):")
    g1_result = _run_g1(records, by_model)
    if g1_result is not None:
        results.append(g1_result)

    print()

    # --- G2: Signal ---
    print(f"G2 — Signal (permutation test, {args.g2_perms} permutations):")
    if len(model_ids) < 2:
        g2_result = GateResult(
            gate="G2", passed=False, value=1.0, threshold=0.01,
            detail="Need ≥2 models",
        )
    else:
        vectors = _extract_shared_vectors(by_model, model_ids)
        g2_result = g2_signal(vectors, n_perm=args.g2_perms)
    _print_gate(g2_result)
    results.append(g2_result)

    print()

    # --- G3: Replication ---
    print(f"G3 — Replication (split-half, {args.g3_trials} trials):")
    g3_result = g3_replication(
        by_model, n_trials=args.g3_trials,
    )
    _print_gate(g3_result)
    results.append(g3_result)

    print()

    # --- Summary ---
    print("=" * 60)
    all_run = [r for r in results if r is not None]
    all_pass = all(r.passed for r in all_run)
    skipped = g1_result is None

    if skipped:
        print("RESULT: INCOMPLETE — G1 skipped (no sensitivity data)")
    elif all_pass:
        print("RESULT: ALL GATES PASSED")
        print("Phase 5 may proceed. See ARCHITECTURE.md §5.3.")
    else:
        failed = [r.gate for r in all_run if not r.passed]
        print(f"RESULT: FAILED — {', '.join(failed)}")
        print("Do not proceed to Phase 5. See ARCHITECTURE.md §5.3.")

    return 0 if (all_pass and not skipped) else 1


if __name__ == "__main__":
    sys.exit(main())
