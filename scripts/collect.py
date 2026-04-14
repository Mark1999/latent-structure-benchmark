"""Run the CDA collection protocol for a (model, domain) pair.

See ARCHITECTURE.md §4.1.

Usage:
    python scripts/collect.py --domain family --runs 10
    python scripts/collect.py --domain family --mode two_pass --free-lists 10 --pile-sorts 10
    python scripts/collect.py --domain family --mode baseline --baseline romney_1996 --pile-sorts 10
    python scripts/collect.py --domain family --dry-run
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from datetime import date
from pathlib import Path

from cdb_collect.adapters import (
    AnthropicAdapter,
    HuggingFaceAdapter,
    ModelAdapter,
    OpenRouterAdapter,
)
from cdb_collect.baselines import load_baseline_items
from cdb_collect.domains import load_domain
from cdb_collect.jsonl import append_failure, append_record
from cdb_collect.runner import run_baseline_sort, run_informant, run_two_pass
from cdb_collect.spend import check_spend, get_monthly_spend
from cdb_core import ModelRef
from dotenv import load_dotenv

try:
    from scripts.qa_check import check_record
except ModuleNotFoundError:
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

MODEL_REGISTRY: dict[str, ModelRef] = {
    # ── Anthropic (direct) ──────────────────────────────────────────────
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
    "claude-sonnet-4-6": ModelRef(
        provider="anthropic",
        model_id="claude-sonnet-4-6",
        family="claude",
        origin="us",
        open_weights=False,
        collection_method="anthropic_api",
        quantization=None,
        release_date=date(2026, 3, 1),
        version_label="4.6",
    ),
    # ── OpenRouter — closed-weight ──────────────────────────────────────
    "openai/gpt-4o": ModelRef(
        provider="openrouter",
        model_id="openai/gpt-4o",
        family="gpt",
        origin="us",
        open_weights=False,
        collection_method="openrouter",
        quantization=None,
        release_date=date(2025, 5, 13),
        version_label="4o",
    ),
    "google/gemini-2.5-pro": ModelRef(
        provider="openrouter",
        model_id="google/gemini-2.5-pro",
        family="gemini",
        origin="us",
        open_weights=False,
        collection_method="openrouter",
        quantization=None,
        release_date=date(2025, 3, 25),
        version_label="2.5-pro",
    ),
    "x-ai/grok-3": ModelRef(
        provider="openrouter",
        model_id="x-ai/grok-3",
        family="grok",
        origin="us",
        open_weights=False,
        collection_method="openrouter",
        quantization=None,
        release_date=date(2025, 2, 17),
        version_label="3",
    ),
    "cohere/command-r-plus-08-2024": ModelRef(
        provider="openrouter",
        model_id="cohere/command-r-plus-08-2024",
        family="command",
        origin="ca",
        open_weights=False,
        collection_method="openrouter",
        quantization=None,
        release_date=date(2024, 8, 1),
        version_label="r-plus-08-2024",
    ),
    # ── OpenRouter — open-weight ────────────────────────────────────────
    "meta-llama/llama-3.1-70b-instruct": ModelRef(
        provider="openrouter",
        model_id="meta-llama/llama-3.1-70b-instruct",
        family="llama",
        origin="us",
        open_weights=True,
        collection_method="openrouter",
        quantization=None,
        release_date=date(2025, 7, 23),
        version_label="3.1-70b-instruct",
    ),
    "meta-llama/llama-4-maverick": ModelRef(
        provider="openrouter",
        model_id="meta-llama/llama-4-maverick",
        family="llama",
        origin="us",
        open_weights=True,
        collection_method="openrouter",
        quantization=None,
        release_date=date(2025, 4, 5),
        version_label="4-maverick",
    ),
    "mistralai/mistral-large": ModelRef(
        provider="openrouter",
        model_id="mistralai/mistral-large",
        family="mistral",
        origin="eu",
        open_weights=False,
        collection_method="openrouter",
        quantization=None,
        release_date=date(2025, 7, 24),
        version_label="large",
    ),
    "mistralai/mistral-small-3.2-24b-instruct": ModelRef(
        provider="openrouter",
        model_id="mistralai/mistral-small-3.2-24b-instruct",
        family="mistral",
        origin="eu",
        open_weights=True,
        collection_method="openrouter",
        quantization=None,
        release_date=date(2025, 3, 7),
        version_label="small-3.2-24b",
    ),
    # ── OpenRouter — China-origin ───────────────────────────────────────
    "qwen/qwen-2.5-72b-instruct": ModelRef(
        provider="openrouter",
        model_id="qwen/qwen-2.5-72b-instruct",
        family="qwen",
        origin="cn",
        open_weights=True,
        collection_method="openrouter",
        quantization=None,
        release_date=date(2025, 9, 19),
        version_label="2.5-72b-instruct",
    ),
    # ── HuggingFace Inference Providers ─────────────────────────────────
    "Qwen/Qwen2.5-72B-Instruct": ModelRef(
        provider="huggingface",
        model_id="Qwen/Qwen2.5-72B-Instruct",
        family="qwen",
        origin="cn",
        open_weights=True,
        collection_method="huggingface",
        quantization=None,
        release_date=date(2025, 9, 19),
        version_label="2.5-72b-instruct",
        source_notes="Same model as qwen/qwen-2.5-72b-instruct via OpenRouter; "
        "HF route used for provider-routing variance comparison.",
    ),
}


def _create_adapter(model_ref: ModelRef) -> ModelAdapter:
    """Route a ModelRef to the correct adapter based on collection_method."""
    method = model_ref.collection_method
    if method == "anthropic_api":
        return AnthropicAdapter(model_ref)
    if method == "openrouter":
        return OpenRouterAdapter(model_ref)
    if method == "huggingface":
        return HuggingFaceAdapter(model_ref)
    msg = f"Unknown collection_method: {method}"
    raise ValueError(msg)


async def collect_single_pass(
    adapter: ModelAdapter,
    domain_slug: str,
    runs: int,
    output_path: Path,
) -> int:
    """Single-pass collection: each run generates and sorts its own items."""
    domain = load_domain(domain_slug)
    successful = 0

    for run_index in range(runs):
        monthly = get_monthly_spend(output_path)
        status = check_spend(monthly)
        if status == "halt":
            print(f"SPEND CAP REACHED (${monthly:.2f}).", file=sys.stderr)
            break
        if status == "warning":
            logger.warning("Spend at 80%%+ of cap: $%.2f", monthly)

        print(
            f"Run {run_index + 1}/{runs} — "
            f"{adapter.model.model_id} × {domain_slug}...",
            end=" ", flush=True,
        )

        try:
            record = await run_informant(adapter, domain, run_index)
            append_record(record, output_path)
            qa_passed = check_record(record)
            status_str = "PASS" if qa_passed else "QA_FAIL"
            n_items = len(record.freelist.parsed_items)
            n_piles = len(record.pile_sort.parsed_piles)
            print(f"{status_str} — {n_items} items, {n_piles} piles")
            successful += 1
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            logger.exception("Run %d failed", run_index)
            append_failure(e, {
                "model_id": adapter.model.model_id,
                "domain": domain_slug, "run_index": run_index,
            }, FAILURES_JSONL)

    return successful


async def collect_two_pass(
    adapter: ModelAdapter,
    domain_slug: str,
    n_free_lists: int,
    n_pile_sorts: int,
    output_path: Path,
) -> int:
    """Two-pass collection: free lists → consensus → pile sorts."""
    domain = load_domain(domain_slug)
    total = n_free_lists + n_pile_sorts

    print(
        f"TWO-PASS MODE: {n_free_lists} free lists → consensus → "
        f"{n_pile_sorts} pile sorts"
    )
    print(f"  Model:  {adapter.model.model_id}")
    print(f"  Domain: {domain_slug} ({domain.display_name})")
    print(f"  Truncation K: {domain.truncation_k}")
    print()

    try:
        records = await run_two_pass(
            adapter, domain,
            n_free_lists=n_free_lists,
            n_pile_sorts=n_pile_sorts,
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        logger.exception("Two-pass collection failed")
        append_failure(e, {
            "model_id": adapter.model.model_id,
            "domain": domain_slug, "mode": "two_pass",
        }, FAILURES_JSONL)
        return 0

    successful = 0
    for record in records:
        append_record(record, output_path)
        qa_passed = check_record(record)
        mode_label = "FL" if record.pile_sort.stop_reason == "not_collected" else "PS"
        status_str = "PASS" if qa_passed else "QA_FAIL"
        print(f"  [{mode_label}] {record.informant_id} — {status_str}")
        successful += 1

    print(f"\nDone: {successful}/{total} records written.")
    return successful


async def collect_baseline(
    adapter: ModelAdapter,
    domain_slug: str,
    baseline_id: str,
    n_sorts: int,
    output_path: Path,
) -> int:
    """Baseline collection: sort human baseline items."""
    domain = load_domain(domain_slug)
    items = load_baseline_items(domain_slug, baseline_id)

    print(f"BASELINE MODE: sorting {len(items)} items from {baseline_id}")
    print(f"  Model:  {adapter.model.model_id}")
    print(f"  Domain: {domain_slug}")
    print(f"  Items:  {items[:5]}{'...' if len(items) > 5 else ''}")
    print()

    try:
        records = await run_baseline_sort(
            adapter, domain,
            items=items,
            baseline_id=baseline_id,
            n_sorts=n_sorts,
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        logger.exception("Baseline collection failed")
        append_failure(e, {
            "model_id": adapter.model.model_id,
            "domain": domain_slug, "baseline": baseline_id,
        }, FAILURES_JSONL)
        return 0

    successful = 0
    for record in records:
        append_record(record, output_path)
        qa_passed = check_record(record)
        status_str = "PASS" if qa_passed else "QA_FAIL"
        n_piles = len(record.pile_sort.parsed_piles)
        print(f"  {record.informant_id} — {status_str} ({n_piles} piles)")
        successful += 1

    print(f"\nDone: {successful}/{n_sorts} records written.")
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
        "--mode", choices=["single_pass", "two_pass", "baseline"],
        default="single_pass", help="Collection mode",
    )
    parser.add_argument(
        "--runs", type=int, default=10,
        help="Number of runs for single_pass mode (default: 10)",
    )
    parser.add_argument(
        "--free-lists", type=int, default=10,
        help="Number of free lists for two_pass mode (default: 10)",
    )
    parser.add_argument(
        "--pile-sorts", type=int, default=10,
        help="Number of pile sorts for two_pass/baseline mode (default: 10)",
    )
    parser.add_argument(
        "--baseline", type=str, default=None,
        help="Baseline ID for baseline mode (e.g., romney_1996)",
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

    model_ref = MODEL_REGISTRY.get(args.model)
    if model_ref is None:
        print(f"Unknown model: {args.model}", file=sys.stderr)
        print(f"Available: {', '.join(MODEL_REGISTRY.keys())}", file=sys.stderr)
        return 1

    domain = load_domain(args.domain)

    if args.dry_run:
        print(f"DRY RUN — mode: {args.mode}")
        print(f"  Model:  {args.model}")
        print(f"  Domain: {args.domain} ({domain.display_name})")
        print(f"  Truncation K: {domain.truncation_k}")
        if args.mode == "single_pass":
            print(f"  Runs: {args.runs}")
        elif args.mode == "two_pass":
            print(f"  Free lists: {args.free_lists}")
            print(f"  Pile sorts: {args.pile_sorts}")
        elif args.mode == "baseline":
            print(f"  Baseline: {args.baseline}")
            print(f"  Pile sorts: {args.pile_sorts}")
        monthly = get_monthly_spend(args.output)
        status = check_spend(monthly)
        print(f"  Monthly spend: ${monthly:.2f} (status: {status})")
        return 0

    if args.mode == "baseline" and not args.baseline:
        print("--baseline is required for baseline mode", file=sys.stderr)
        return 1

    adapter = _create_adapter(model_ref)

    if args.mode == "single_pass":
        result = asyncio.run(collect_single_pass(
            adapter, args.domain, args.runs, args.output,
        ))
    elif args.mode == "two_pass":
        result = asyncio.run(collect_two_pass(
            adapter, args.domain, args.free_lists, args.pile_sorts, args.output,
        ))
    elif args.mode == "baseline":
        result = asyncio.run(collect_baseline(
            adapter, args.domain, args.baseline, args.pile_sorts, args.output,
        ))
    else:
        return 1

    return 0 if result > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
