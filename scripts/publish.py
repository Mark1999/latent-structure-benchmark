"""Build static JSON files for the dashboard via cdb_publish.

See ARCHITECTURE.md §4.4.

Usage:
    python scripts/publish.py --results-dir data/results --output-dir apps/dashboard/public/data

Exit codes:
    0 -- success
    1 -- validation failure for one or more domain files
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cdb_publish.build import DomainValidationError, build


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the LSB dashboard manifest from data/results/.",
    )
    parser.add_argument(
        "--results-dir",
        required=True,
        type=Path,
        help="Directory containing per-domain result subdirectories "
             "(e.g. data/results/).",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory where manifest.json will be written.",
    )
    parser.add_argument(
        "--failures-path",
        type=Path,
        default=Path("data/raw/failures.jsonl"),
        help="Path to failures.jsonl (default: data/raw/failures.jsonl).",
    )
    parser.add_argument(
        "--decline-interviews-path",
        type=Path,
        default=Path("data/raw/decline_interviews.jsonl"),
        help="Path to decline_interviews.jsonl (default: data/raw/decline_interviews.jsonl).",
    )
    parser.add_argument(
        "--informants-path",
        type=Path,
        default=Path("data/raw/informants.jsonl"),
        help="Path to informants.jsonl (default: data/raw/informants.jsonl).",
    )
    args = parser.parse_args()

    try:
        manifest = build(
            args.results_dir,
            args.output_dir,
            raw_failures_path=args.failures_path,
            raw_decline_interviews_path=args.decline_interviews_path,
            raw_informants_path=args.informants_path,
        )
    except DomainValidationError as exc:
        print(f"Validation error: {exc.path}", file=sys.stderr)
        print(str(exc.cause), file=sys.stderr)
        return 1

    domain_slugs = ", ".join(d.slug for d in manifest.domains)
    n = len(manifest.domains)
    print(f"Built manifest with {n} domain{'s' if n != 1 else ''}: {domain_slugs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
