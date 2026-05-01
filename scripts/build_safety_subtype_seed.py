"""Build the safety attribution subtype seed file for decline interview records.

Reads ``data/derived/decline_interviews_manual_classification.jsonl`` (27 rows),
filters to rows where ``manual_classification == "safety_event_attribution"``
(expected: 9 rows), and emits a seed at
``data/derived/decline_interviews_safety_attribution_subtype.jsonl`` (9 rows).

Each seed row carries:
  - decline_interview_id:       from the manual classification artifact
  - safety_attribution_subtype: "UNCLASSIFIED" sentinel (outside the two-value
                                enum; the loader rejects this until Mark fills
                                it in)
  - subtype_rationale:          "" (empty placeholder; loader rejects until
                                filled in with verbatim trigger-attribution
                                language from the source response_verbatim)
  - subtype_classifier_id:      "" (empty placeholder; conventional fill-in
                                value is "mark")

Output is byte-identical on repeat runs given identical input.  Rows are
sorted by ``decline_interview_id`` to guarantee order stability (determinism
guarantee per Amendment 3 §3.1).

Idempotency guard: if the output file already exists and content would differ,
the script prints a warning naming which rows differ and exits non-zero.
Use --force to override.

Usage:
  uv run python scripts/build_safety_subtype_seed.py
  uv run python scripts/build_safety_subtype_seed.py --force
  uv run python scripts/build_safety_subtype_seed.py \\
      --input data/derived/decline_interviews_manual_classification.jsonl \\
      --output data/derived/decline_interviews_safety_attribution_subtype.jsonl

References:
  Architect plan:  docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md §3.1
  CDA SME verdict: docs/status/2026-04-30-phase4a1-amendment-3-cda-sme-verdict.md
  B11 source:      docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md
  Mirrors:         scripts/build_manual_classification_seed.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ── Repo root (one level above this script) ───────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent

# ── Default paths ─────────────────────────────────────────────────────────────
DEFAULT_INPUT = (
    _REPO_ROOT / "data" / "derived" / "decline_interviews_manual_classification.jsonl"
)
DEFAULT_OUTPUT = (
    _REPO_ROOT / "data" / "derived" / "decline_interviews_safety_attribution_subtype.jsonl"
)

# ── The classification value that qualifies a row for the subtype artifact ────
SAFETY_CLASSIFICATION = "safety_event_attribution"


def _build_seed_row(manual_classification_row: dict) -> dict:  # type: ignore[type-arg]
    """Build one seed row from a manual classification row with safety classification.

    Seed rows deliberately use the "UNCLASSIFIED" sentinel and empty strings
    for the subtype fields.  These fail validation on load — by design —
    until Mark fills them in.

    We do NOT validate seed rows through SafetyAttributionSubtype Pydantic
    because the sentinel and empty strings are intentionally invalid.
    """
    return {
        "decline_interview_id": manual_classification_row["decline_interview_id"],
        "safety_attribution_subtype": "UNCLASSIFIED",
        "subtype_rationale": "",
        "subtype_classifier_id": "",
    }


def _row_to_jsonl_line(row: dict) -> str:  # type: ignore[type-arg]
    """Serialize a row to a JSONL line (sort_keys=True, ensure_ascii=False)."""
    return json.dumps(row, sort_keys=True, ensure_ascii=False)


def build_seed(
    input_path: Path,
    output_path: Path,
    force: bool = False,
) -> int:
    """Build the safety attribution subtype seed file.

    Reads ``input_path`` (the manual classification JSONL), filters to rows
    with ``manual_classification == "safety_event_attribution"``, sorts by
    ``decline_interview_id`` for deterministic ordering, and emits a seed JSONL
    at ``output_path`` with all subtype fields set to sentinel/empty values.

    Args:
        input_path: Path to data/derived/decline_interviews_manual_classification.jsonl.
        output_path: Path to write the subtype seed JSONL.
        force: If True, overwrite even if content would differ.

    Returns:
        0  — file written (or already up to date).
        1  — diff detected and --force not specified (exits non-zero to protect
             any partially-filled subtypes).
    """
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Read all manual classification rows
    mc_rows: list[dict] = []  # type: ignore[type-arg]
    with input_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            mc_rows.append(json.loads(line))

    # Filter to safety_event_attribution rows
    safety_rows = [
        r for r in mc_rows if r.get("manual_classification") == SAFETY_CLASSIFICATION
    ]

    # Sort by decline_interview_id for deterministic ordering
    safety_rows.sort(key=lambda r: r["decline_interview_id"])

    # Build seed lines
    seed_lines: list[str] = [
        _row_to_jsonl_line(_build_seed_row(r)) for r in safety_rows
    ]
    new_content = "\n".join(seed_lines) + "\n"

    print(
        f"Found {len(safety_rows)} {SAFETY_CLASSIFICATION!r} rows "
        f"(of {len(mc_rows)} total) in {input_path}.",
        file=sys.stderr,
    )

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
        new_lines_list = [ln for ln in new_content.splitlines() if ln.strip()]

        differing_rows: list[str] = []
        for i, (old, new) in enumerate(
            zip(existing_lines, new_lines_list, strict=False)
        ):
            if old != new:
                try:
                    old_id = json.loads(old).get("decline_interview_id", f"row {i+1}")
                except Exception:
                    old_id = f"row {i+1}"
                differing_rows.append(old_id)
        if len(existing_lines) != len(new_lines_list):
            differing_rows.append(
                f"(row count changed: {len(existing_lines)} -> {len(new_lines_list)})"
            )

        if not force:
            print(
                f"WARNING: {output_path} already exists and content would differ.\n"
                f"Differing rows: {', '.join(differing_rows)}\n"
                f"Use --force to overwrite. Exiting non-zero to protect "
                f"any partially-filled subtypes.",
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
        description=(
            "Build the safety attribution subtype seed file for decline interviews."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=(
            "Path to decline_interviews_manual_classification.jsonl "
            "(default: %(default)s)"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path to write the subtype seed JSONL (default: %(default)s)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Overwrite existing output even if content would differ.",
    )
    args = parser.parse_args()

    return build_seed(
        input_path=args.input,
        output_path=args.output,
        force=args.force,
    )


if __name__ == "__main__":
    sys.exit(main())
