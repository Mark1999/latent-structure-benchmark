"""Build the confabulation classification seed file for decline-interview records.

Reads the 9 originally-Gemini decline-interview IDs from the superseded May 1
artifact at ``data/derived/decline_interviews_safety_attribution_subtype.jsonl``
(read-only; the IDs are the authority — the labels in that artifact are mooted
under the 2026-05-05 cap-exhaustion reframe).  Emits a seed JSONL at
``data/derived/decline_interviews_confabulation_classification.jsonl`` with 9
rows, one per ID, all with ``confabulation_label="UNCLASSIFIED"``.

Each seed row carries:
  - decline_interview_id:    from the superseded artifact (the 9 Gemini IDs)
  - confabulation_label:     "UNCLASSIFIED" sentinel (outside the five-value
                             enum; the loader rejects this until Mark fills
                             it in)
  - confabulation_rationale: "" (empty placeholder; Mark fills in verbatim-
                             referenced text ≤ 200 chars)
  - under_blind_spot:        true (all 9 originating failures were Gemini
                             max_output_tokens=4096 cap-exhaustion events,
                             per the 2026-05-05 recovery campaign)
  - classifier_id:           "mark" (conventional hand-coder value)

Output is sorted by ``decline_interview_id`` for deterministic ordering.

CRITICAL — one-shot operation: this script errors out cleanly if the output
file already exists.  The seed JSONL is a one-time scaffold that Mark edits
in place; re-generating would clobber Mark's hand-coding.  To re-generate
the seed from scratch, remove the output file manually first.

Idempotence guard: if the output file already exists, prints
  "Seed already exists; remove it manually if you want to regenerate"
and exits 1.

Usage:
  uv run python scripts/build_confabulation_classification_seed.py
  uv run python scripts/build_confabulation_classification_seed.py \\
      --source data/derived/decline_interviews_safety_attribution_subtype.jsonl \\
      --output data/derived/decline_interviews_confabulation_classification.jsonl

References:
  Architect plan:   docs/status/2026-05-05-t4-redo-architect-plan.md §2 RD-2
  CDA SME verdict:  docs/status/2026-05-05-t4-redo-cda-sme-verdict.md (T1, T2)
  RD-1 supersede:   data/derived/decline_interviews_safety_attribution_subtype.SUPERSEDED.md
  Predecessor:      scripts/build_safety_subtype_seed.py (structural model only)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ── Repo root (one level above this script) ───────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent

# ── Default paths ─────────────────────────────────────────────────────────────
# Source: the superseded May 1 artifact — used for its ID list only.
# The labels in that artifact are mooted under the cap-exhaustion reframe;
# we read only the decline_interview_id fields.
DEFAULT_SOURCE = (
    _REPO_ROOT
    / "data"
    / "derived"
    / "decline_interviews_safety_attribution_subtype.jsonl"
)

DEFAULT_OUTPUT = (
    _REPO_ROOT
    / "data"
    / "derived"
    / "decline_interviews_confabulation_classification.jsonl"
)


def _build_seed_row(decline_interview_id: str) -> dict:  # type: ignore[type-arg]
    """Build one seed row for the given decline_interview_id.

    Seed rows deliberately use the "UNCLASSIFIED" sentinel and empty rationale.
    ``under_blind_spot=True`` for all 9 rows: the originating failures were
    all Gemini cap-exhaustion events (max_output_tokens=4096), verified by the
    2026-05-05 recovery campaign (100% Gemini recovery rate).

    We do NOT validate seed rows through ConfabulationClassification Pydantic
    because the sentinel and empty rationale are intentionally outside the
    validated schema.
    """
    return {
        "classifier_id": "mark",
        "confabulation_label": "UNCLASSIFIED",
        "confabulation_rationale": "",
        "decline_interview_id": decline_interview_id,
        "under_blind_spot": True,
    }


def _row_to_jsonl_line(row: dict) -> str:  # type: ignore[type-arg]
    """Serialize a row to a JSONL line (sort_keys=True, ensure_ascii=False)."""
    return json.dumps(row, sort_keys=True, ensure_ascii=False)


def build_seed(
    source_path: Path,
    output_path: Path,
) -> int:
    """Build the confabulation classification seed file.

    Reads ``source_path`` (the superseded May 1 safety attribution subtype
    JSONL), extracts the ``decline_interview_id`` values, sorts them for
    deterministic ordering, and emits a seed JSONL at ``output_path`` with
    all confabulation fields set to sentinel / empty / default values.

    CRITICAL: exits non-zero if the output file already exists, to protect
    Mark's in-progress hand-coding from accidental clobber.

    Args:
        source_path: Path to decline_interviews_safety_attribution_subtype.jsonl
            (the superseded May 1 artifact; used for its ID list only).
        output_path: Path to write the seed JSONL (must not already exist).

    Returns:
        0 — file written successfully.
        1 — output file already exists (idempotence guard).
        2 — source file not found or unreadable.
    """
    # ── Idempotence guard ─────────────────────────────────────────────────────
    if output_path.exists():
        print(
            "Seed already exists; remove it manually if you want to regenerate",
            file=sys.stderr,
        )
        print(
            f"  Existing file: {output_path}",
            file=sys.stderr,
        )
        return 1

    # ── Read source IDs ───────────────────────────────────────────────────────
    if not source_path.exists():
        print(
            f"ERROR: Source file not found: {source_path}",
            file=sys.stderr,
        )
        print(
            "  Expected: data/derived/decline_interviews_safety_attribution_subtype.jsonl",
            file=sys.stderr,
        )
        return 2

    decline_interview_ids: list[str] = []
    with source_path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                print(
                    f"ERROR: Invalid JSON at line {lineno} of {source_path}: {exc}",
                    file=sys.stderr,
                )
                return 2

            did = raw.get("decline_interview_id", "")
            if not did:
                print(
                    f"ERROR: Missing or empty decline_interview_id at line {lineno}",
                    file=sys.stderr,
                )
                return 2
            decline_interview_ids.append(did)

    print(
        f"Read {len(decline_interview_ids)} decline_interview_id(s) from {source_path}",
        file=sys.stderr,
    )

    # ── Sort for deterministic ordering ───────────────────────────────────────
    decline_interview_ids.sort()

    # ── Build seed lines ──────────────────────────────────────────────────────
    seed_lines: list[str] = [
        _row_to_jsonl_line(_build_seed_row(did)) for did in decline_interview_ids
    ]
    new_content = "\n".join(seed_lines) + "\n"

    # ── Ensure output directory exists ────────────────────────────────────────
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ── Write output ──────────────────────────────────────────────────────────
    output_path.write_text(new_content, encoding="utf-8")
    print(
        f"Wrote {len(seed_lines)} seed rows to {output_path}",
        file=sys.stderr,
    )
    print(
        "All rows: confabulation_label=UNCLASSIFIED, under_blind_spot=True, "
        "classifier_id=mark",
        file=sys.stderr,
    )
    print(
        f"Next step: Mark edits {output_path} in Cursor to fill in "
        f"confabulation_label and confabulation_rationale for each row.",
        file=sys.stderr,
    )
    return 0


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description=(
            "Build the confabulation classification seed file for decline interviews."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help=(
            "Path to the superseded May 1 safety attribution subtype JSONL "
            "(used for its ID list only; default: %(default)s)"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path to write the confabulation classification seed JSONL (default: %(default)s)",
    )
    args = parser.parse_args()

    return build_seed(
        source_path=args.source,
        output_path=args.output,
    )


if __name__ == "__main__":
    sys.exit(main())
