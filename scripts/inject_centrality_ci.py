"""Remedy B — T3b: Surgical injection of centrality_ci into published domain JSON.

Adds ONLY the ``centrality_ci`` field to existing domain JSON files, computed
from the similarity matrix already stored in those files.  Every other field is
left byte-identical — no round-trip serialization, no float-format churn.

Background
----------
The full-pipeline regen in Remedy B T3 produced numeric drift in MDS coords,
consensus_score, and eigenratio due to numpy/scipy non-determinism across
environments.  Rather than accept a noisy diff, Mark chose surgical injection:
compute ``centrality_ci`` from the similarity matrix already published in each
domain JSON, verify it is consistent with the published ``cultural_centrality_scores``
(correctness guard), and insert the new field as a text splice — touching nothing
else.

Files patched (additive-only)
------------------------------
- data/results/family/0.3.json
- data/results/holidays/0.3.json
- data/results/food/0.2.json            (food only has a v0.2 result)
- apps/dashboard/public/data/family.json
- apps/dashboard/public/data/family.v0.3.json
- apps/dashboard/public/data/holidays.json
- apps/dashboard/public/data/holidays.v0.3.json
- apps/dashboard/public/data/food.json
- apps/dashboard/public/data/food.v0.2.json

Stop conditions
---------------
The script aborts (sys.exit(1)) rather than writing if:
  - The correctness guard fails (recomputed scores deviate from published by
    more than 1e-6 for any model in any domain).
  - The text-splice would produce a non-additive diff (i.e. the target field
    marker ``"negative_centrality_flag"`` is not found exactly once in the
    file).

See docs/status/2026-05-28-remedy-b-cda-sme-verdict.md for the CDA SME ruling
that defines the bootstrap parameters (Q1–Q4, N1–N7).
Reference: ARCHITECTURE.md §4.2.6, §4.5.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

# cdb_analyze imports (pure deterministic Python — no LLM calls)
from cdb_analyze.bootstrap import bootstrap_centrality_ci
from cdb_analyze.consensus import compute_centrality_scores
from numpy.typing import NDArray

REPO_ROOT = Path(__file__).resolve().parent.parent

# Domains to patch: (domain_slug, analysis_version, source_result_path, [dashboard_paths])
DOMAIN_TARGETS: list[tuple[str, str, Path, list[Path]]] = [
    (
        "family",
        "0.3",
        REPO_ROOT / "data" / "results" / "family" / "0.3.json",
        [
            REPO_ROOT / "apps" / "dashboard" / "public" / "data" / "family.json",
            REPO_ROOT / "apps" / "dashboard" / "public" / "data" / "family.v0.3.json",
        ],
    ),
    (
        "holidays",
        "0.3",
        REPO_ROOT / "data" / "results" / "holidays" / "0.3.json",
        [
            REPO_ROOT / "apps" / "dashboard" / "public" / "data" / "holidays.json",
            REPO_ROOT / "apps" / "dashboard" / "public" / "data" / "holidays.v0.3.json",
        ],
    ),
    (
        "food",
        "0.2",
        REPO_ROOT / "data" / "results" / "food" / "0.2.json",
        [
            REPO_ROOT / "apps" / "dashboard" / "public" / "data" / "food.json",
            REPO_ROOT / "apps" / "dashboard" / "public" / "data" / "food.v0.2.json",
        ],
    ),
]

# Tolerance for the correctness guard (published scores vs recomputed scores).
CORRECTNESS_TOLERANCE = 1e-6

# Bootstrap parameters — per CDA SME Q2 ruling.
N_BOOTSTRAP = 500
RANDOM_STATE = 42

# The insertion marker: centrality_ci is inserted immediately before this key.
# The JSON files are produced by cdb_publish and always contain this key at the
# top level, on its own line, with a two-space indent.
INSERTION_MARKER = '  "negative_centrality_flag"'


def _load_domain_json(path: Path) -> tuple[dict, str]:
    """Load a domain JSON file, returning (parsed_dict, raw_text)."""
    raw = path.read_text(encoding="utf-8")
    return json.loads(raw), raw


def _verify_source_consistency(domain_slug: str, source_path: Path, dash_paths: list[Path]) -> None:
    """Verify that dashboard files have the same cultural_centrality_scores as the source."""
    src_data, _ = _load_domain_json(source_path)
    src_scores = src_data["cultural_centrality_scores"]
    for dash_path in dash_paths:
        dash_data, _ = _load_domain_json(dash_path)
        dash_scores = dash_data["cultural_centrality_scores"]
        if set(src_scores.keys()) != set(dash_scores.keys()):
            print(
                f"  ERROR: {domain_slug}: model keys differ between "
                f"{source_path.name} and {dash_path.name}"
            )
            sys.exit(1)
        for mid, score in src_scores.items():
            diff = abs(score - dash_scores[mid])
            if diff > CORRECTNESS_TOLERANCE:
                print(
                    f"  ERROR: {domain_slug}: {mid} score mismatch between "
                    f"source ({score}) and dashboard ({dash_scores[mid]})"
                )
                sys.exit(1)
    print(f"  [{domain_slug}] source ↔ dashboard consistency: OK")


def _correctness_guard(
    domain_slug: str,
    model_ids: list[str],
    sim_np: NDArray[np.float64],
    published_scores: dict[str, float],
) -> float:
    """Recompute centrality scores and assert they match published.

    Returns the max absolute difference observed (for reporting).
    Calls sys.exit(1) if any model's score deviates by more than CORRECTNESS_TOLERANCE.
    """
    recomputed = compute_centrality_scores(model_ids, sim_np)
    max_diff = 0.0
    for mid in model_ids:
        diff = abs(recomputed[mid] - published_scores[mid])
        if diff > max_diff:
            max_diff = diff
        if diff > CORRECTNESS_TOLERANCE:
            print(
                f"  STOP: {domain_slug}: correctness guard FAILED for {mid}.\n"
                f"    published={published_scores[mid]}, "
                f"recomputed={recomputed[mid]}, diff={diff}\n"
                f"  The similarity matrix in the published JSON does not reproduce the "
                f"published centrality scores. Methodology problem — do not inject."
            )
            sys.exit(1)
    print(f"  [{domain_slug}] correctness guard: PASSED (max_abs_diff={max_diff:.2e})")
    return max_diff


def _build_centrality_ci_text(
    ci_dict: dict[str, tuple[float, float]],
    model_ids: list[str],
) -> str:
    """Serialize centrality_ci as a JSON fragment for text splicing.

    Produces a 2-space-indented block matching the publish pipeline's style
    (json.dumps(indent=2) for the CI values themselves, which are plain floats
    in normal range — no scientific-notation concerns here).

    Output format (example, 2 models):
        "centrality_ci": {
            "model-a": [0.123, 0.456],
            "model-b": [0.234, 0.567]
          },

    The trailing comma and two-space indent at close are required so the
    inserted block fits into the existing top-level object syntax.
    """
    lines: list[str] = ['  "centrality_ci": {']
    for i, mid in enumerate(model_ids):
        lo, hi = ci_dict[mid]
        comma = "," if i < len(model_ids) - 1 else ""
        # Emit values using Python's standard float repr — centrality loadings
        # are O(0.1–0.9) and will not trigger scientific notation.
        lines.append(f'    {json.dumps(mid)}: [{lo}, {hi}]{comma}')
    lines.append("  },")
    return "\n".join(lines) + "\n"


def _splice_ci_into_text(domain_slug: str, raw_text: str, ci_text: str) -> str:
    """Insert ci_text immediately before the INSERTION_MARKER line.

    Validates that INSERTION_MARKER appears exactly once (stop condition).
    """
    marker_count = raw_text.count("\n" + INSERTION_MARKER)
    if marker_count != 1:
        print(
            f"  STOP: {domain_slug}: expected exactly 1 occurrence of "
            f"{INSERTION_MARKER!r} at line start, found {marker_count}. "
            f"Cannot perform safe text splice."
        )
        sys.exit(1)

    # Find the insertion point: the newline immediately before INSERTION_MARKER
    insert_pos = raw_text.index("\n" + INSERTION_MARKER) + 1  # +1 to keep the \n before it
    patched = raw_text[:insert_pos] + ci_text + raw_text[insert_pos:]
    return patched


def _verify_additive_only(domain_slug: str, original: str, patched: str, ci_text: str) -> None:
    """Verify the diff is exactly the ci_text insertion — nothing else changed."""
    # Remove the inserted block from patched and compare to original
    if ci_text not in patched:
        print(f"  STOP: {domain_slug}: injected ci_text not found in patched output.")
        sys.exit(1)
    reconstructed = patched.replace(ci_text, "", 1)
    if reconstructed != original:
        print(
            f"  STOP: {domain_slug}: additive-only check FAILED — "
            f"removing the injected block does not reproduce the original file. "
            f"Other content was changed."
        )
        sys.exit(1)
    print(f"  [{domain_slug}] additive-only check: PASSED")


def _patch_file(path: Path, patched_text: str) -> None:
    """Write patched_text to path (UTF-8, no trailing newline added)."""
    path.write_text(patched_text, encoding="utf-8")
    print(f"  Wrote: {path}")


def process_domain(
    domain_slug: str,
    analysis_version: str,
    source_path: Path,
    dash_paths: list[Path],
) -> dict[str, float]:
    """Process one domain: compute CI, verify, patch all files.

    Returns per-model max_abs_diff from the correctness guard (for reporting).
    """
    print(f"\n=== {domain_slug} (v{analysis_version}) ===")

    # Step 0: verify source ↔ dashboard consistency before touching anything.
    _verify_source_consistency(domain_slug, source_path, dash_paths)

    # Step 1: load the source file.
    src_data, src_raw = _load_domain_json(source_path)

    # Step 2: extract model_ids and similarity matrix.
    # model_ids from cultural_centrality_scores (preserves the exact ordering used
    # when the published scores were computed — these keys are insertion-ordered
    # in the JSON and reflect the sorted(records_by_model.keys()) pipeline order).
    published_scores: dict[str, float] = src_data["cultural_centrality_scores"]
    model_ids: list[str] = list(published_scores.keys())
    n_models = len(model_ids)

    if n_models < 3:
        print(
            f"  SKIP: {domain_slug} has only {n_models} models — "
            f"bootstrap_centrality_ci requires >=3 (degenerate-n guard)."
        )
        return {}

    sim_list: list[list[float]] = src_data["similarity_matrix"]
    sim_np = np.array(sim_list, dtype=np.float64)

    print(f"  n_models={n_models}, sim_matrix shape={sim_np.shape}")

    # Step 3: correctness guard — recompute scores from the matrix and assert match.
    max_diff = _correctness_guard(domain_slug, model_ids, sim_np, published_scores)

    # Step 4: bootstrap centrality CI.
    print(
        f"  Running bootstrap_centrality_ci("
        f"n_bootstrap={N_BOOTSTRAP}, random_state={RANDOM_STATE})..."
    )
    ci_dict = bootstrap_centrality_ci(
        model_ids,
        sim_np,
        n_bootstrap=N_BOOTSTRAP,
        random_state=RANDOM_STATE,
    )

    if not ci_dict:
        print(f"  STOP: {domain_slug}: bootstrap_centrality_ci returned empty dict (unexpected).")
        sys.exit(1)

    missing_models = [m for m in model_ids if m not in ci_dict]
    if missing_models:
        print(f"  WARNING: {domain_slug}: no CI computed for: {missing_models}")

    print(f"  CI computed for {len(ci_dict)}/{n_models} models.")

    # Step 5: build the CI text block for insertion.
    ci_text = _build_centrality_ci_text(ci_dict, model_ids)

    # Step 6: patch source file.
    src_patched = _splice_ci_into_text(domain_slug, src_raw, ci_text)
    _verify_additive_only(domain_slug, src_raw, src_patched, ci_text)
    _patch_file(source_path, src_patched)

    # Step 7: patch dashboard files.
    # Dashboard files are byte-identical to source (verified by _verify_source_consistency).
    # We apply the same splice to each.
    for dash_path in dash_paths:
        _, dash_raw = _load_domain_json(dash_path)
        dash_patched = _splice_ci_into_text(domain_slug, dash_raw, ci_text)
        _verify_additive_only(domain_slug, dash_raw, dash_patched, ci_text)
        _patch_file(dash_path, dash_patched)

    print(f"  [{domain_slug}] DONE. Correctness guard max_abs_diff={max_diff:.2e}")
    return {domain_slug: max_diff}


def main() -> None:
    """Run the surgical injection for all eligible domains."""
    print("Remedy B — T3b: Surgical centrality_ci injection")
    print(f"  REPO_ROOT: {REPO_ROOT}")
    print(f"  Bootstrap params: n_bootstrap={N_BOOTSTRAP}, random_state={RANDOM_STATE}")
    print(f"  Correctness tolerance: {CORRECTNESS_TOLERANCE}")

    results: dict[str, float] = {}

    for domain_slug, analysis_version, source_path, dash_paths in DOMAIN_TARGETS:
        if not source_path.exists():
            print(f"\n  SKIP: {domain_slug}/{analysis_version}: {source_path} not found.")
            continue
        domain_results = process_domain(domain_slug, analysis_version, source_path, dash_paths)
        results.update(domain_results)

    print("\n=== SUMMARY ===")
    for domain_slug, max_diff in results.items():
        status = "PASSED" if max_diff <= CORRECTNESS_TOLERANCE else "FAILED"
        print(f"  {domain_slug}: correctness guard {status}, max_abs_diff={max_diff:.2e}")

    print("\nAll done. Run `git diff --stat` to verify additive-only changes.")


if __name__ == "__main__":
    main()
