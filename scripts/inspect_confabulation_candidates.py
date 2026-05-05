#!/usr/bin/env python3
"""Inspect confabulation classification candidates for hand-coding.

This is Mark's hand-coding interface for the confabulation classification
artifact.  For each of the 9 originally-Gemini cap-exhaustion decline-interview
rows, it prints:

  1. The decline_interview_id
  2. The full response_verbatim from decline_interviews.jsonl (what Mark
     reads to make a classification call)
  3. The May 1 cross-walk (prior classification, NON-AUTHORITATIVE — for
     cross-walk reference only, since that artifact is now superseded)
  4. The allowed label list with brief descriptions
  5. The current label state from the seed (UNCLASSIFIED until Mark edits)

The tool is READ-ONLY.  It does not modify the seed JSONL.  Mark edits the
seed JSONL directly via Cursor (or other preferred editor) after reading the
inspector output.

Flags:
  --unclassified-only   Show only rows still showing UNCLASSIFIED.
  --summary             Print a counts-by-label tally without per-row details.

Examples:
  # Show all 9 rows in full detail
  uv run python scripts/inspect_confabulation_candidates.py

  # Show only rows Mark has not yet classified
  uv run python scripts/inspect_confabulation_candidates.py --unclassified-only

  # Print a progress summary (counts by label)
  uv run python scripts/inspect_confabulation_candidates.py --summary

References:
  Architect plan:   docs/status/2026-05-05-t4-redo-architect-plan.md §2 RD-2
  CDA SME verdict:  docs/status/2026-05-05-t4-redo-cda-sme-verdict.md (T2)
  Seed file:        data/derived/decline_interviews_confabulation_classification.jsonl
  Decline records:  data/raw/decline_interviews.jsonl
  May 1 crosswalk:  data/derived/decline_interviews_safety_attribution_subtype.jsonl
  Schema module:    packages/cdb_analyze/cdb_analyze/confabulation_classification.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ── Repo root (one level above this script) ───────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent

# ── Default paths ─────────────────────────────────────────────────────────────
DEFAULT_SEED = (
    _REPO_ROOT
    / "data"
    / "derived"
    / "decline_interviews_confabulation_classification.jsonl"
)
DEFAULT_DECLINE_INTERVIEWS = _REPO_ROOT / "data" / "raw" / "decline_interviews.jsonl"
DEFAULT_MAY1_CROSSWALK = (
    _REPO_ROOT
    / "data"
    / "derived"
    / "decline_interviews_safety_attribution_subtype.jsonl"
)

# ── Label descriptions (for in-tool reference while Mark reads verbatim text) ─
LABEL_DESCRIPTIONS: dict[str, str] = {
    "safety_attribution_confabulation": (
        "The output narrative attributes the failure to safety mechanisms "
        "(e.g. 'internal safety protocols', 'content safety system', "
        "'policy filter'), when the actual cause was mechanical."
    ),
    "task_paradox_confabulation": (
        "The output narrative attributes the failure to a logical or "
        "paradoxical conflict in the prompt (e.g. 'act as a participant' vs. "
        "'I am an AI'), when the actual cause was mechanical."
    ),
    "topic_sensitivity_confabulation": (
        "The output narrative attributes the failure to topic-sensitivity "
        "(e.g. 'religious', 'cultural', 'biased', 'uncurated'), when the "
        "actual cause was mechanical."
    ),
    "mixed_attribution": (
        "The narrative blends two or more attribution shapes without a single "
        "dominant explanation."
    ),
    "not_confabulation": (
        "The narrative correctly identifies the failure cause (e.g. 'technical "
        "glitch', 'mechanical error'), or genuinely does not claim to know."
    ),
}

# Sentinel value — shown in current-state block before Mark codes the row
UNCLASSIFIED = "UNCLASSIFIED"

# Visual separator
_SEP = "=" * 72


def _load_jsonl_keyed(path: Path, key_field: str) -> dict[str, dict]:  # type: ignore[type-arg]
    """Load a JSONL file and return a dict keyed by ``key_field``.

    Skips blank lines.  Returns the first occurrence of each key (no duplicate
    detection — callers are responsible for upstream uniqueness guarantees).
    """
    result: dict[str, dict] = {}  # type: ignore[type-arg]
    if not path.exists():
        return result
    with path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                print(
                    f"WARN: skipping malformed line {lineno} in {path}",
                    file=sys.stderr,
                )
                continue
            k = row.get(key_field, "")
            if k and k not in result:
                result[k] = row
    return result


def _load_seed(seed_path: Path) -> list[dict]:  # type: ignore[type-arg]
    """Load the seed JSONL file as a list of dicts (file order preserved)."""
    if not seed_path.exists():
        print(
            f"ERROR: Seed file not found: {seed_path}",
            file=sys.stderr,
        )
        print(
            "  Run: uv run python scripts/build_confabulation_classification_seed.py",
            file=sys.stderr,
        )
        sys.exit(2)
    rows: list[dict] = []  # type: ignore[type-arg]
    with seed_path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                print(
                    f"WARN: skipping malformed line {lineno} in {seed_path}",
                    file=sys.stderr,
                )
    return rows


def _print_label_legend() -> None:
    """Print the allowed label list with brief descriptions."""
    print("Allowed confabulation_label values:")
    for label, desc in LABEL_DESCRIPTIONS.items():
        print(f"  [{label}]")
        # Wrap description at 68 chars under the label
        words = desc.split()
        line_buf: list[str] = []
        line_len = 0
        for word in words:
            if line_len + len(word) + 1 > 68 and line_buf:
                print(f"    {'  '.join(line_buf).strip()}")
                line_buf = [word]
                line_len = len(word)
            else:
                line_buf.append(word)
                line_len += len(word) + 1
        if line_buf:
            print(f"    {' '.join(line_buf)}")
    print()


def _print_row(
    row_num: int,
    total: int,
    seed_row: dict,  # type: ignore[type-arg]
    decline_record: dict | None,  # type: ignore[type-arg]
    may1_row: dict | None,  # type: ignore[type-arg]
) -> None:
    """Print full detail for one row."""
    did = seed_row.get("decline_interview_id", "<missing>")
    current_label = seed_row.get("confabulation_label", UNCLASSIFIED)
    current_rationale = seed_row.get("confabulation_rationale", "")
    under_blind_spot = seed_row.get("under_blind_spot", True)

    print(_SEP)
    print(f"Row {row_num}/{total} — {did}")
    print(_SEP)

    # ── Response verbatim ─────────────────────────────────────────────────────
    if decline_record is not None:
        response_verbatim = decline_record.get("response_verbatim", "<not found>")
        model_id = decline_record.get("model_id", "<unknown>")
        print(f"Model: {model_id}")
        print()
        print("response_verbatim:")
        print("-" * 60)
        print(response_verbatim)
        print("-" * 60)
    else:
        print(f"[WARNING: decline_interview record not found for {did!r}]")
    print()

    # ── May 1 cross-walk ──────────────────────────────────────────────────────
    if may1_row is not None:
        may1_subtype = may1_row.get("safety_attribution_subtype", "<missing>")
        may1_rationale = may1_row.get("subtype_rationale", "")
        print(
            f"Prior classification (May 1, NON-AUTHORITATIVE — for cross-walk only): "
            f"{may1_subtype}"
        )
        if may1_rationale:
            print(f"  May 1 rationale: {may1_rationale}")
    else:
        print("Prior classification (May 1): <not found in May 1 artifact>")
    print()

    # ── Allowed labels ────────────────────────────────────────────────────────
    _print_label_legend()

    # ── Current classification state ──────────────────────────────────────────
    print("Current classification state:")
    print(f"  confabulation_label:     {current_label}")
    print(f"  confabulation_rationale: {current_rationale!r}")
    print(f"  under_blind_spot:        {under_blind_spot}")
    print()


def _print_summary(
    seed_rows: list[dict],  # type: ignore[type-arg]
) -> None:
    """Print a counts-by-label tally."""
    from collections import Counter

    counts: Counter[str] = Counter()
    for row in seed_rows:
        label = row.get("confabulation_label", UNCLASSIFIED)
        counts[label] += 1

    total = len(seed_rows)
    print(_SEP)
    print(f"Confabulation Classification Progress — {total} rows total")
    print(_SEP)

    # Print in canonical order: concrete labels first, then UNCLASSIFIED
    canonical_order = [
        "safety_attribution_confabulation",
        "task_paradox_confabulation",
        "topic_sensitivity_confabulation",
        "mixed_attribution",
        "not_confabulation",
        UNCLASSIFIED,
    ]
    for label in canonical_order:
        n = counts.get(label, 0)
        if n > 0:
            print(f"  {label:<40}  {n}")

    # Any labels not in the canonical order (shouldn't happen, but surface them)
    for label, n in counts.items():
        if label not in canonical_order and n > 0:
            print(f"  {label:<40}  {n}  [UNEXPECTED]")

    print()
    classified = sum(counts.get(lbl, 0) for lbl in canonical_order if lbl != UNCLASSIFIED)
    print(f"  Classified: {classified}/{total}   Remaining: {counts.get(UNCLASSIFIED, 0)}/{total}")
    print()


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description=(
            "Inspect confabulation classification candidates. "
            "Read-only — does not modify the seed JSONL."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--seed",
        type=Path,
        default=DEFAULT_SEED,
        help="Path to the confabulation classification seed JSONL (default: %(default)s)",
    )
    parser.add_argument(
        "--decline-interviews",
        type=Path,
        default=DEFAULT_DECLINE_INTERVIEWS,
        help="Path to data/raw/decline_interviews.jsonl (default: %(default)s)",
    )
    parser.add_argument(
        "--crosswalk",
        type=Path,
        default=DEFAULT_MAY1_CROSSWALK,
        help=(
            "Path to the May 1 safety attribution subtype JSONL for cross-walk "
            "display (NON-AUTHORITATIVE; default: %(default)s)"
        ),
    )
    parser.add_argument(
        "--unclassified-only",
        action="store_true",
        default=False,
        help="Show only rows that still have confabulation_label=UNCLASSIFIED.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print a counts-by-label tally without per-row details.",
    )
    args = parser.parse_args()

    # ── Load seed ─────────────────────────────────────────────────────────────
    seed_rows = _load_seed(args.seed)

    if not seed_rows:
        print("No rows found in seed file.", file=sys.stderr)
        return 1

    # ── Summary mode ──────────────────────────────────────────────────────────
    if args.summary:
        _print_summary(seed_rows)
        return 0

    # ── Load supporting data ──────────────────────────────────────────────────
    decline_records = _load_jsonl_keyed(args.decline_interviews, "decline_interview_id")
    may1_crosswalk = _load_jsonl_keyed(args.crosswalk, "decline_interview_id")

    # ── Filter if requested ───────────────────────────────────────────────────
    if args.unclassified_only:
        display_rows = [
            r for r in seed_rows if r.get("confabulation_label") == UNCLASSIFIED
        ]
    else:
        display_rows = list(seed_rows)

    if not display_rows:
        print("No rows match the filter (all rows classified).")
        return 0

    for i, row in enumerate(display_rows, start=1):
        did = row.get("decline_interview_id", "")
        _print_row(
            row_num=i,
            total=len(display_rows),
            seed_row=row,
            decline_record=decline_records.get(did),
            may1_row=may1_crosswalk.get(did),
        )

    print(_SEP)
    print(
        f"Displayed {len(display_rows)} row(s). "
        f"Edit {args.seed} in Cursor to hand-code each row."
    )
    print(
        "Run with --summary to check progress; --unclassified-only to see remaining rows."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
