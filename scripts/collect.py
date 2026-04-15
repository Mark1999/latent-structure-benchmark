"""Run the CDA collection protocol for a (model, domain) pair.

See ARCHITECTURE.md §4.1.

Usage:
    python scripts/collect.py --domain family --runs 10
    python scripts/collect.py --domain family --mode two_pass --free-lists 10 --pile-sorts 10
    python scripts/collect.py --domain family --mode cross_model --pile-sorts 10
    python scripts/collect.py --domain family --mode cross_model \
        --models claude-opus-4-6 openai/gpt-4o --pile-sorts 10
    python scripts/collect.py --domain family --mode baseline --baseline romney_1996 --pile-sorts 10
    python scripts/collect.py --domain family --dry-run
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from datetime import date
from pathlib import Path

from cdb_collect.adapters import (
    AnthropicAdapter,
    GeminiAdapter,
    HuggingFaceAdapter,
    ModelAdapter,
    OpenAICompatAdapter,
    OpenRouterAdapter,
)
from cdb_collect.baselines import load_baseline_items
from cdb_collect.domains import load_domain
from cdb_collect.jsonl import append_failure, append_record
from cdb_collect.model_ids import to_direct_id
from cdb_collect.runner import run_baseline_sort, run_cross_model_sort, run_informant, run_two_pass
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
REGISTRY_PATH = Path("data/models/registry.json")

# Adapter method → provider string for ModelRef
_METHOD_TO_PROVIDER: dict[str, str] = {
    "anthropic_api": "anthropic",
    "google_ai": "google",
    "xai_api": "xai",
    "openrouter": "openrouter",
    "huggingface": "huggingface",
}


def _load_registry() -> dict[str, ModelRef]:
    """Load the model registry from registry.json.

    Returns a dict mapping model_id → ModelRef. For direct-API models,
    also indexes under the provider-specific short ID.
    """
    if not REGISTRY_PATH.exists():
        logger.warning(
            "Registry not found at %s. Run: python scripts/discover_models.py --update-registry",
            REGISTRY_PATH,
        )
        return {}

    data = json.loads(REGISTRY_PATH.read_text())
    registry: dict[str, ModelRef] = {}

    for entry in data.get("models", []):
        model_id = entry["model_id"]
        method = entry["collection_method"]
        provider = _METHOD_TO_PROVIDER.get(method, "openrouter")

        # For direct-API models, use the provider-specific short ID
        effective_id = to_direct_id(model_id)

        # Extract version label from model ID
        parts = model_id.split("/")
        version_label = parts[-1] if len(parts) > 1 else model_id

        # Estimate release date from openrouter_created timestamp
        created_ts = entry.get("openrouter_created")
        release = date.fromtimestamp(created_ts) if created_ts else date.today()

        ref = ModelRef(
            provider=provider,
            model_id=effective_id,
            family=entry["family"],
            origin=entry["origin"],
            open_weights=entry["open_weights"],
            collection_method=method,
            quantization=None,
            release_date=release,
            version_label=version_label,
        )

        # Index under both the registry ID and the effective ID
        registry[model_id] = ref
        if effective_id != model_id:
            registry[effective_id] = ref

    return registry


def _load_collected_model_ids(jsonl_path: Path) -> set[str]:
    """Return the set of model_ids already collected in informants.jsonl."""
    ids: set[str] = set()
    if not jsonl_path.exists():
        return ids
    with open(jsonl_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            mid = record.get("model_id", "")
            if mid:
                ids.add(mid)
    return ids


MODEL_REGISTRY = _load_registry()


def _create_adapter(model_ref: ModelRef) -> ModelAdapter:
    """Route a ModelRef to the correct adapter based on collection_method."""
    method = model_ref.collection_method
    if method == "anthropic_api":
        return AnthropicAdapter(model_ref)
    if method == "google_ai":
        return GeminiAdapter(model_ref)
    if method in ("openai_api", "xai_api", "deepseek_api", "mistral_api"):
        return OpenAICompatAdapter(model_ref)
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
    *,
    prompt_version: str = "v1",
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
            record = await run_informant(adapter, domain, run_index, prompt_version=prompt_version)
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
    *,
    prompt_version: str = "v1",
) -> int:
    """Two-pass collection: free lists → consensus → pile sorts."""
    domain = load_domain(domain_slug)
    total = n_free_lists + n_pile_sorts

    print(
        f"TWO-PASS MODE: {n_free_lists} free lists → consensus (elbow) → "
        f"{n_pile_sorts} pile sorts"
    )
    print(f"  Model:  {adapter.model.model_id}")
    print(f"  Domain: {domain_slug} ({domain.display_name})")
    print()

    try:
        records = await run_two_pass(
            adapter, domain,
            n_free_lists=n_free_lists,
            n_pile_sorts=n_pile_sorts,
            prompt_version=prompt_version,
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


async def collect_cross_model(
    adapters: list[ModelAdapter],
    domain_slug: str,
    n_pile_sorts: int,
    output_path: Path,
    *,
    prompt_version: str = "v1",
) -> int:
    """Cross-model consensus collection.

    Loads existing free list records from output_path, pools them across
    all models, computes cross-model consensus via Smith's S + elbow
    detection, then has each model pile sort the shared item list.
    """
    import json

    from cdb_analyze.consensus import (
        compute_cross_model_consensus,
        find_salience_elbow,
    )

    domain = load_domain(domain_slug)

    # ── Load existing free list records ────────────────────────────
    records_by_model: dict[str, list] = {}
    with open(output_path) as f:
        for line in f:
            rec_dict = json.loads(line.strip())
            if rec_dict.get("domain_slug") != domain_slug:
                continue
            from cdb_core import InformantRecord
            rec = InformantRecord(**rec_dict)
            if rec.freelist.output_tokens > 0:
                records_by_model.setdefault(rec.model_id, []).append(rec)

    if not records_by_model:
        print("ERROR: No free list records found. Run two_pass first.", file=sys.stderr)
        return 0

    # ── Compute cross-model consensus ──────────────────────────────
    consensus = compute_cross_model_consensus(records_by_model)
    elbow_k = find_salience_elbow(consensus)
    consensus_items = [item for item, _ in consensus[:elbow_k]]

    n_models = len(records_by_model)
    n_free_lists = sum(len(recs) for recs in records_by_model.values())

    print("CROSS-MODEL CONSENSUS MODE:")
    print(f"  Domain:       {domain_slug} ({domain.display_name})")
    print(f"  Models:       {n_models} ({', '.join(sorted(records_by_model.keys()))})")
    print(f"  Free lists:   {n_free_lists} total")
    print(f"  Unique items: {len(consensus)}")
    print(f"  Elbow at:     {elbow_k} items")
    print(f"  Pile sorts:   {n_pile_sorts} per model")
    print()
    print(f"  Consensus items ({elbow_k}):")
    for i, (item, s) in enumerate(consensus[:elbow_k]):
        print(f"    {i+1:3d}. {item:35s} S={s:.4f}")
    print()

    # ── Pile sort each model on the shared list ────────────────────
    successful = 0
    for adapter in adapters:
        print(f"  Sorting: {adapter.model.model_id}...")
        try:
            records = await run_cross_model_sort(
                adapter, domain,
                consensus_items=consensus_items,
                n_pile_sorts=n_pile_sorts,
                prompt_version=prompt_version,
            )
        except Exception as e:
            print(f"    ERROR: {e}", file=sys.stderr)
            logger.exception(
                "Cross-model sort failed for %s", adapter.model.model_id,
            )
            append_failure(e, {
                "model_id": adapter.model.model_id,
                "domain": domain_slug, "mode": "cross_model_consensus",
            }, FAILURES_JSONL)
            continue

        for record in records:
            append_record(record, output_path)
            qa_passed = check_record(record)
            status_str = "PASS" if qa_passed else "QA_FAIL"
            n_piles = len(record.pile_sort.parsed_piles)
            print(f"    {record.informant_id} — {status_str} ({n_piles} piles)")
            successful += 1

    total = len(adapters) * n_pile_sorts
    print(f"\nDone: {successful}/{total} records written.")
    return successful


async def collect_baseline(
    adapter: ModelAdapter,
    domain_slug: str,
    baseline_id: str,
    n_sorts: int,
    output_path: Path,
    *,
    prompt_version: str = "v1",
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
            prompt_version=prompt_version,
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
        "--domain", required=False, help="Domain slug (e.g., family)",
    )
    parser.add_argument(
        "--model", default="claude-opus-4-6",
        help="Model ID for single/two_pass/baseline modes (default: claude-opus-4-6)",
    )
    parser.add_argument(
        "--models", nargs="+", default=None,
        help="Model IDs for cross_model mode (space-separated). "
        "If omitted, uses all models in the registry.",
    )
    parser.add_argument(
        "--mode", choices=["single_pass", "two_pass", "baseline", "cross_model"],
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
        "--prompt-version", default="v1",
        help="Prompt template version directory (default: v1). "
        "Use v1_s1..v1_s8 for sensitivity variants.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print plan without making API calls",
    )
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_JSONL,
        help="Output JSONL path",
    )
    parser.add_argument(
        "--skip-collected", action="store_true",
        help="Skip models that already have records in informants.jsonl",
    )
    parser.add_argument(
        "--list-models", action="store_true",
        help="List all models in the registry and exit",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    if not MODEL_REGISTRY:
        print(
            "No models in registry. Run:\n"
            "  python scripts/discover_models.py --update-registry",
            file=sys.stderr,
        )
        return 1

    if args.list_models:
        collected = _load_collected_model_ids(args.output)
        # Deduplicate — some models are indexed under two keys
        seen: set[str] = set()
        for mid, ref in MODEL_REGISTRY.items():
            if ref.model_id in seen:
                continue
            seen.add(ref.model_id)
            is_collected = ref.model_id in collected
            status = "collected" if is_collected else "NEW"
            print(f"  {mid:55s} {ref.family:10s} {ref.collection_method:15s} {status}")
        return 0

    if not args.domain:
        print("--domain is required for collection", file=sys.stderr)
        return 1

    model_ref = MODEL_REGISTRY.get(args.model)
    if model_ref is None:
        print(f"Unknown model: {args.model}", file=sys.stderr)
        # Show unique model IDs only
        seen_ids: set[str] = set()
        available = []
        for mid, ref in MODEL_REGISTRY.items():
            if ref.model_id not in seen_ids:
                seen_ids.add(ref.model_id)
                available.append(mid)
        print(f"Available: {', '.join(available)}", file=sys.stderr)
        return 1

    # Skip already-collected models if requested
    if args.skip_collected:
        collected = _load_collected_model_ids(args.output)
        if model_ref.model_id in collected:
            print(
                f"Skipping {model_ref.model_id} — already collected. "
                "Use without --skip-collected to re-run.",
            )
            return 0

    domain = load_domain(args.domain)

    if args.dry_run:
        print(f"DRY RUN — mode: {args.mode}")
        if args.mode == "cross_model":
            model_ids = args.models or list(MODEL_REGISTRY.keys())
            print(f"  Models: {', '.join(model_ids)}")
        else:
            print(f"  Model:  {args.model}")
        print(f"  Domain: {args.domain} ({domain.display_name})")
        print(f"  Prompts: {args.prompt_version}")
        if args.mode == "single_pass":
            print(f"  Runs: {args.runs}")
        elif args.mode == "two_pass":
            print(f"  Free lists: {args.free_lists}")
            print(f"  Pile sorts: {args.pile_sorts}")
        elif args.mode == "baseline":
            print(f"  Baseline: {args.baseline}")
            print(f"  Pile sorts: {args.pile_sorts}")
        elif args.mode == "cross_model":
            print(f"  Pile sorts: {args.pile_sorts} per model")
        monthly = get_monthly_spend(args.output)
        status = check_spend(monthly)
        print(f"  Monthly spend: ${monthly:.2f} (status: {status})")
        return 0

    if args.mode == "baseline" and not args.baseline:
        print("--baseline is required for baseline mode", file=sys.stderr)
        return 1

    if args.mode == "cross_model":
        model_ids = args.models or list(MODEL_REGISTRY.keys())
        collected = _load_collected_model_ids(args.output) if args.skip_collected else set()
        adapters = []
        seen_refs: set[str] = set()
        for mid in model_ids:
            ref = MODEL_REGISTRY.get(mid)
            if ref is None:
                print(f"Unknown model: {mid}", file=sys.stderr)
                return 1
            # Deduplicate refs indexed under multiple keys
            if ref.model_id in seen_refs:
                continue
            seen_refs.add(ref.model_id)
            if args.skip_collected and ref.model_id in collected:
                print(f"  Skipping {ref.model_id} — already collected")
                continue
            adapters.append(_create_adapter(ref))
        result = asyncio.run(collect_cross_model(
            adapters, args.domain, args.pile_sorts, args.output,
            prompt_version=args.prompt_version,
        ))
    else:
        adapter = _create_adapter(model_ref)
        if args.mode == "single_pass":
            result = asyncio.run(collect_single_pass(
                adapter, args.domain, args.runs, args.output,
                prompt_version=args.prompt_version,
            ))
        elif args.mode == "two_pass":
            result = asyncio.run(collect_two_pass(
                adapter, args.domain, args.free_lists, args.pile_sorts, args.output,
                prompt_version=args.prompt_version,
            ))
        elif args.mode == "baseline":
            result = asyncio.run(collect_baseline(
                adapter, args.domain, args.baseline, args.pile_sorts, args.output,
                prompt_version=args.prompt_version,
            ))
        else:
            return 1

    return 0 if result > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
