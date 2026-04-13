"""Weekly spend summary for collection runs.

See ARCHITECTURE.md §6.2.

Usage:
    python scripts/cost_report.py --month current
    python scripts/cost_report.py --month 2026-03
    python scripts/cost_report.py --all --group-by domain
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from cdb_collect.spend import compute_cost

DEFAULT_JSONL = Path("data/raw/informants.jsonl")


def _read_records(path: Path) -> list[dict]:
    """Read raw JSON records from JSONL (not validated — for speed)."""
    if not path.exists():
        return []

    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def _record_cost(record: dict) -> float:
    """Compute total cost for an InformantRecord from token counts."""
    total = 0.0
    model_id = record.get("model_id", "")
    for step_key in ("freelist", "pile_sort", "interview"):
        step = record.get(step_key, {})
        in_tok = step.get("input_tokens", 0)
        out_tok = step.get("output_tokens", 0)
        if in_tok or out_tok:
            total += compute_cost(in_tok, out_tok, model_id)
    return total


def report(
    path: Path,
    month: str | None = None,
    group_by: str | None = None,
) -> None:
    """Print a spend report."""
    records = _read_records(path)

    if not records:
        print("No records found.")
        return

    # Filter by month if specified
    if month and month != "all":
        if month == "current":
            month = datetime.now().strftime("%Y-%m")
        records = [
            r for r in records
            if r.get("collection_date", "").startswith(month)
        ]

    if not records:
        print(f"No records for month {month}.")
        return

    # Compute costs
    total_cost = 0.0
    grouped: dict[str, float] = defaultdict(float)
    grouped_count: dict[str, int] = defaultdict(int)

    for r in records:
        cost = _record_cost(r)
        total_cost += cost

        if group_by == "model":
            key = r.get("model_id", "unknown")
        elif group_by == "domain":
            key = r.get("domain_slug", "unknown")
        else:
            key = "total"

        grouped[key] += cost
        grouped_count[key] += 1

    # Print report
    period = month or "all time"
    print(f"LSB Spend Report — {period}")
    print(f"{'=' * 50}")
    print(f"Records: {len(records)}")
    print(f"Total:   ${total_cost:.4f}")
    print()

    if group_by:
        print(f"By {group_by}:")
        print(f"{'─' * 50}")
        for key in sorted(grouped.keys()):
            print(
                f"  {key:30s}  "
                f"${grouped[key]:8.4f}  "
                f"({grouped_count[key]} records)"
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Spend report for LSB collection runs. See ARCHITECTURE.md §6.2.",
    )
    parser.add_argument(
        "--month", default="current",
        help="Month (YYYY-MM, 'current', or omit for current). Use --all for all time.",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Show all-time spend (overrides --month)",
    )
    parser.add_argument(
        "--group-by", choices=["model", "domain"], default=None,
        help="Group results by model or domain",
    )
    parser.add_argument(
        "--file", type=Path, default=DEFAULT_JSONL,
        help="Path to informants.jsonl",
    )

    args = parser.parse_args()

    month = "all" if args.all else args.month
    report(args.file, month=month, group_by=args.group_by)
    return 0


if __name__ == "__main__":
    sys.exit(main())
