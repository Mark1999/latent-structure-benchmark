"""Run the CDA collection protocol for a (model, domain) pair.

See ARCHITECTURE.md §4.1.

Usage:
    python scripts/collect.py --domain family --runs 5
    python scripts/collect.py --model claude-opus-4-6 --domain family
    python scripts/collect.py --domain family --dry-run
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from datetime import date
from pathlib import Path

from cdb_collect.adapters.anthropic import AnthropicAdapter
from cdb_collect.domains import load_domain
from cdb_collect.jsonl import append_failure, append_record
from cdb_collect.runner import run_informant
from cdb_collect.spend import check_spend, get_monthly_spend
from cdb_core import ModelRef
from dotenv import load_dotenv

try:
    from scripts.qa_check import check_record
except ModuleNotFoundError:
    # When run directly as `python scripts/collect.py`, adjust the path
    import importlib.util
    _spec = importlib.util.spec_from_file_location(
        "qa_check", Path(__file__).parent / "qa_check.py",
    )
    _mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
    _spec.loader.exec_module(_mod)  # type: ignore[union-attr]
    check_record = _mod.check_record  # type: ignore[assignment]

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_JSONL = Path("data/raw/informants.jsonl")
FAILURES_JSONL = Path("data/raw/failures.jsonl")

# Milestone A: single model definition
MODEL_REGISTRY: dict[str, ModelRef] = {
    "claude-opus-4-6": ModelRef(
        provider="anthropic",
        model_id="claude-opus-4-6",
        family="claude",
        origin="us",
        open_weights=False,
        collection_method="anthropic_api",
        quantization=None,
        release_date=date(2026, 3, 1),
        version_label="4.6",
    ),
}


async def collect(
    model_id: str,
    domain_slug: str,
    runs: int,
    dry_run: bool = False,
    output_path: Path = DEFAULT_JSONL,
) -> int:
    """Run collection for the given model and domain.

    Returns the number of successful runs.
    """
    model_ref = MODEL_REGISTRY.get(model_id)
    if model_ref is None:
        print(f"Unknown model: {model_id}", file=sys.stderr)
        print(f"Available: {', '.join(MODEL_REGISTRY.keys())}", file=sys.stderr)
        return 0

    domain = load_domain(domain_slug)

    if dry_run:
        print(f"DRY RUN — would collect {runs} run(s)")
        print(f"  Model:  {model_id}")
        print(f"  Domain: {domain_slug} ({domain.display_name})")
        print(f"  Prompt seed: {domain.prompt_seed!r}")
        print(f"  Truncation K: {domain.truncation_k}")
        print(f"  Output: {output_path}")

        monthly = get_monthly_spend(output_path)
        status = check_spend(monthly)
        print(f"  Monthly spend: ${monthly:.2f} (status: {status})")
        return 0

    adapter = AnthropicAdapter(model_ref)
    successful = 0

    for run_index in range(runs):
        # Check spend cap before each run
        monthly = get_monthly_spend(output_path)
        status = check_spend(monthly)

        if status == "halt":
            print(
                f"SPEND CAP REACHED (${monthly:.2f}). Halting collection.",
                file=sys.stderr,
            )
            break

        if status == "warning":
            logger.warning(
                "Spend at 80%%+ of cap: $%.2f", monthly,
            )

        print(
            f"Run {run_index + 1}/{runs} — "
            f"{model_id} × {domain_slug}...",
            end=" ",
            flush=True,
        )

        try:
            record = await run_informant(
                adapter, domain, run_index,
            )
            append_record(record, output_path)

            # Run QA check
            qa_passed = check_record(record)
            status_str = "PASS" if qa_passed else "QA_FAIL"
            print(
                f"{status_str} — "
                f"{len(record.freelist.parsed_items)} items, "
                f"{record.freelist.latency_ms}ms"
            )
            successful += 1

        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            logger.exception("Collection failed for run %d", run_index)
            append_failure(
                e,
                {"model_id": model_id, "domain": domain_slug, "run_index": run_index},
                FAILURES_JSONL,
            )

    print(f"\nDone: {successful}/{runs} runs completed.")
    return successful


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run CDA collection protocol. See ARCHITECTURE.md §4.1.",
    )
    parser.add_argument(
        "--domain", required=True, help="Domain slug (e.g., family)",
    )
    parser.add_argument(
        "--model", default="claude-opus-4-6",
        help="Model ID (default: claude-opus-4-6)",
    )
    parser.add_argument(
        "--runs", type=int, default=5, help="Number of runs (default: 5)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print plan without making API calls",
    )
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_JSONL,
        help="Output JSONL path",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    result = asyncio.run(
        collect(
            model_id=args.model,
            domain_slug=args.domain,
            runs=args.runs,
            dry_run=args.dry_run,
            output_path=args.output,
        )
    )

    return 0 if result >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
