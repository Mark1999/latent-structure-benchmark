"""Build the manual classification seed file for decline interview records.

Reads ``data/raw/decline_interviews.jsonl`` (27 rows) and emits a seed at
``data/derived/decline_interviews_manual_classification.jsonl`` (27 rows).

Each seed row carries:
  - decline_interview_id: from source
  - manual_classification: "UNCLASSIFIED" sentinel (outside the 7-enum;
    the loader rejects this until Mark fills it in)
  - manual_classification_rationale: "" (empty; loader rejects until filled)
  - manual_classifier_id: "" (empty; loader rejects until filled)
  - response_verbatim_excerpt: first 400 chars of source response_verbatim
  - detector_flag_v1: computed from source response_verbatim using the v1
    _is_recursive_decline() logic (SAFETY_FILTER_MARKERS substring match)

Output is byte-identical on repeat runs given identical input.

Idempotency guard: if the output file already exists and content would
differ, the script prints a warning naming which rows differ and exits
non-zero. Use --force to override.

Usage:
  uv run python scripts/build_manual_classification_seed.py
  uv run python scripts/build_manual_classification_seed.py --force
  uv run python scripts/build_manual_classification_seed.py \\
      --source data/raw/decline_interviews.jsonl \\
      --output data/derived/decline_interviews_manual_classification.jsonl

References:
  Plan:     docs/status/2026-04-30-phase4a1-architect-plan-amendment-2.md §3 T3C
  SME:      docs/status/2026-04-30-phase4a1-amendment-2-cda-sme-verdict.md
  Origin of v1 detector:
            scripts/run_decline_backfill.py :: _is_recursive_decline()
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

# ── Repo root (one level above this script) ───────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent

# ── Default paths ─────────────────────────────────────────────────────────────
DEFAULT_SOURCE = _REPO_ROOT / "data" / "raw" / "decline_interviews.jsonl"
DEFAULT_OUTPUT = _REPO_ROOT / "data" / "derived" / "decline_interviews_manual_classification.jsonl"

# ── Load the v1 detector from run_decline_backfill.py ─────────────────────────
# The detector is defined there as _is_recursive_decline(response_verbatim) -> bool.
# We load it via importlib to avoid duplicating the SAFETY_FILTER_MARKERS list.
_BACKFILL_SCRIPT = _REPO_ROOT / "scripts" / "run_decline_backfill.py"


def _load_v1_detector() -> object:
    """Load the _is_recursive_decline function from run_decline_backfill.py."""
    spec = importlib.util.spec_from_file_location(
        "run_decline_backfill_for_seed", _BACKFILL_SCRIPT
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load spec from {_BACKFILL_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod._is_recursive_decline  # type: ignore[attr-defined]


_is_recursive_decline = _load_v1_detector()


# ── Seed row builder ──────────────────────────────────────────────────────────

def _build_seed_row(source_row: dict) -> dict:  # type: ignore[type-arg]
    """Build one seed row dict from a source decline interview row.

    Seed rows deliberately use the "UNCLASSIFIED" sentinel and empty strings
    for the classification fields. These fail validation on load — by design —
    until Mark fills them in (commit 3 of T3C).

    We do NOT validate seed rows through DeclineManualClassification Pydantic
    because the sentinel and empty strings are intentionally invalid.
    """
    response_verbatim: str = source_row.get("response_verbatim") or ""
    excerpt: str = response_verbatim[:400]
    flag: bool = bool(_is_recursive_decline(response_verbatim))

    return {
        "decline_interview_id": source_row["decline_interview_id"],
        "manual_classification": "UNCLASSIFIED",
        "manual_classification_rationale": "",
        "manual_classifier_id": "",
        "response_verbatim_excerpt": excerpt,
        "detector_flag_v1": flag,
    }


def _row_to_jsonl_line(row: dict) -> str:  # type: ignore[type-arg]
    """Serialize a row to a JSONL line (sort_keys=True, ensure_ascii=False)."""
    return json.dumps(row, sort_keys=True, ensure_ascii=False)


def build_seed(
    source_path: Path,
    output_path: Path,
    force: bool = False,
) -> int:
    """Build the seed file. Returns 0 on success, non-zero on guarded diff.

    Args:
        source_path: Path to data/raw/decline_interviews.jsonl.
        output_path: Path to write the seed JSONL.
        force: If True, overwrite even if content would differ.

    Returns:
        0  — file written (or unchanged).
        1  — diff detected and --force not specified (exits non-zero).
    """
    # Ensure data/derived/ exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Read source rows in order
    source_rows: list[dict] = []  # type: ignore[type-arg]
    with source_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            source_rows.append(json.loads(line))

    # Build seed lines
    seed_lines: list[str] = [_row_to_jsonl_line(_build_seed_row(r)) for r in source_rows]
    new_content = "\n".join(seed_lines) + "\n"

    # Idempotency guard
    if output_path.exists():
        existing_content = output_path.read_text(encoding="utf-8")
        if existing_content == new_content:
            print(
                f"Seed file is already up to date: {output_path}",
                file=sys.stderr,
            )
            return 0

        # Content would differ — identify which rows differ
        existing_lines = [ln for ln in existing_content.splitlines() if ln.strip()]
        new_lines = [ln for ln in new_content.splitlines() if ln.strip()]

        differing_rows: list[str] = []
        for i, (old, new) in enumerate(zip(existing_lines, new_lines, strict=False)):
            if old != new:
                try:
                    old_id = json.loads(old).get("decline_interview_id", f"row {i+1}")
                except Exception:
                    old_id = f"row {i+1}"
                differing_rows.append(old_id)
        if len(existing_lines) != len(new_lines):
            differing_rows.append(
                f"(row count changed: {len(existing_lines)} -> {len(new_lines)})"
            )

        if not force:
            print(
                f"WARNING: {output_path} already exists and content would differ.\n"
                f"Differing rows: {', '.join(differing_rows)}\n"
                f"Use --force to overwrite. Exiting non-zero to protect "
                f"any partially-filled classifications.",
                file=sys.stderr,
            )
            return 1

        print(
            f"WARNING: --force specified. Overwriting {output_path}.\n"
            f"Differing rows: {', '.join(differing_rows)}",
            file=sys.stderr,
        )

    # Write output
    output_path.write_text(new_content, encoding="utf-8")
    print(
        f"Wrote {len(seed_lines)} seed rows to {output_path}",
        file=sys.stderr,
    )
    return 0


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Build the manual classification seed file for decline interviews.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Path to decline_interviews.jsonl (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path to write the seed JSONL (default: %(default)s)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Overwrite existing output even if content would differ.",
    )
    args = parser.parse_args()

    return build_seed(
        source_path=args.source,
        output_path=args.output,
        force=args.force,
    )


if __name__ == "__main__":
    sys.exit(main())
