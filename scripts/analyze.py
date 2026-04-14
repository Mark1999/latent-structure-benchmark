"""Run the analysis pipeline on collected data.

See ARCHITECTURE.md §4.2.

Usage:
    python scripts/analyze.py --domain family
    python scripts/analyze.py --domain family --analysis-version 0.1
    python scripts/analyze.py --domain family --bootstrap 200
    python scripts/analyze.py --domain family --dry-run
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from cdb_analyze.pipeline import (
    group_by_model,
    load_records,
    run_pipeline,
    write_result,
)

logger = logging.getLogger(__name__)

DEFAULT_JSONL = Path("data/raw/informants.jsonl")
DEFAULT_OUTPUT = Path("data/results")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run LSB analysis pipeline. See ARCHITECTURE.md §4.2.",
    )
    parser.add_argument(
        "--domain", required=True, help="Domain slug (e.g., family)",
    )
    parser.add_argument(
        "--analysis-version", default="0.1",
        help="Analysis version string (default: 0.1)",
    )
    parser.add_argument(
        "--bootstrap", type=int, default=500,
        help="Number of bootstrap resamples (default: 500)",
    )
    parser.add_argument(
        "--input", type=Path, default=DEFAULT_JSONL,
        help="Input JSONL path",
    )
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT,
        help="Output directory for results JSON",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print plan without running analysis",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    records = load_records(args.input, args.domain)

    if not records:
        print(
            f"No QA-passed records for domain '{args.domain}' "
            f"in {args.input}",
            file=sys.stderr,
        )
        return 1

    by_model = group_by_model(records)

    if args.dry_run:
        print(f"DRY RUN — domain: {args.domain}")
        print(f"  Records:  {len(records)}")
        print(f"  Models:   {len(by_model)}")
        for mid, recs in sorted(by_model.items()):
            print(f"    {mid}: {len(recs)} runs")
        print(f"  Bootstrap: {args.bootstrap}")
        print(f"  Version:  {args.analysis_version}")
        return 0

    print(
        f"Running analysis: {args.domain}, "
        f"{len(records)} records, {len(by_model)} models, "
        f"B={args.bootstrap}"
    )

    result = run_pipeline(
        records,
        analysis_version=args.analysis_version,
        n_bootstrap=args.bootstrap,
    )

    out_path = write_result(result, args.output)
    print(f"Wrote {out_path}")
    print(f"  MDS coordinates: {len(result.mds_coordinates)} models")
    print(f"  Consensus score: {result.consensus_score:.4f}")
    print(
        f"  Consensus CI: "
        f"({result.consensus_ci[0]:.4f}, {result.consensus_ci[1]:.4f})"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
