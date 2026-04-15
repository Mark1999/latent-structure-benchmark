"""Discover and track frontier model releases via OpenRouter.

Queries the OpenRouter model catalog, filters to tracked families,
picks the latest flagship per family tier, and cross-references
against data/raw/informants.jsonl to report collection status.

Usage:
    python scripts/discover_models.py --scan
    python scripts/discover_models.py --update-registry
    python scripts/discover_models.py --scan --format json

See ARCHITECTURE.md §4.1.2.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import httpx
from cdb_collect.model_ids import REGISTRY_TO_DIRECT, to_registry_id
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
REGISTRY_PATH = Path("data/models/registry.json")
INFORMANTS_PATH = Path("data/raw/informants.jsonl")

# ── Target families and their selection rules ──────────────────────────
# Each family has:
#   prefix: OpenRouter model ID prefix(es) to match
#   origin: country code for ModelRef
#   open_weights: whether the family is open-weight
#   max_tiers: how many models to keep per family (flagship + notable tiers)
#   preferred_adapter: which adapter to route through
#   direct_env_key: env var for direct API key (if applicable)

FAMILY_CONFIG: dict[str, dict] = {
    "claude": {
        "prefixes": ["anthropic/claude"],
        "origin": "us",
        "open_weights": False,
        "max_tiers": 3,  # opus, sonnet, haiku
        "preferred_adapter": "anthropic_api",
        "direct_env_key": "ANTHROPIC_API_KEY",
    },
    "gpt": {
        "prefixes": ["openai/gpt", "openai/o"],
        "origin": "us",
        "open_weights": False,
        "max_tiers": 3,  # flagship, reasoning, mini/fast
        "preferred_adapter": "openai_api",
        "direct_env_key": "OPENAI_API_KEY",
    },
    "gemini": {
        "prefixes": ["google/gemini"],
        "origin": "us",
        "open_weights": False,
        "max_tiers": 2,  # pro, flash
        "preferred_adapter": "google_ai",
        "direct_env_key": "GEMINI_API_KEY",
    },
    "grok": {
        "prefixes": ["x-ai/grok"],
        "origin": "us",
        "open_weights": False,
        "max_tiers": 2,  # flagship, fast
        "preferred_adapter": "xai_api",
        "direct_env_key": "XAI_API_KEY",
    },
    "llama": {
        "prefixes": ["meta-llama/llama"],
        "origin": "us",
        "open_weights": True,
        "max_tiers": 2,  # largest, mid-size
        "preferred_adapter": "openrouter",
    },
    "deepseek": {
        "prefixes": ["deepseek/deepseek"],
        "origin": "cn",
        "open_weights": True,
        "max_tiers": 2,  # v3, r1/reasoning
        "preferred_adapter": "openrouter",  # always via OpenRouter (security)
    },
    "mistral": {
        "prefixes": ["mistralai/mistral", "mistralai/pixtral"],
        "origin": "eu",
        "open_weights": False,  # mixed, but flagships are closed
        "max_tiers": 2,
        "preferred_adapter": "openrouter",  # no thinking traces, negligible price diff
    },
    "qwen": {
        "prefixes": ["qwen/qwen"],
        "origin": "cn",
        "open_weights": True,
        "max_tiers": 2,
        "preferred_adapter": "openrouter",
    },
    "command": {
        "prefixes": ["cohere/command"],
        "origin": "ca",
        "open_weights": False,
        "max_tiers": 1,
        "preferred_adapter": "openrouter",
    },
    "gemma": {
        "prefixes": ["google/gemma"],
        "origin": "us",
        "open_weights": True,
        "max_tiers": 1,
        "preferred_adapter": "openrouter",
    },
    "phi": {
        "prefixes": ["microsoft/phi"],
        "origin": "us",
        "open_weights": True,
        "max_tiers": 1,
        "preferred_adapter": "openrouter",
    },
    "glm": {
        "prefixes": ["z-ai/glm"],
        "origin": "cn",
        "open_weights": False,
        "max_tiers": 1,
        "preferred_adapter": "openrouter",  # geo-restricted, use OpenRouter
    },
}


# ── Exclusion patterns ─────────────────────────────────────────────────
# Skip dated snapshots, quantized variants, fine-tunes, free-tier copies
_SKIP_PATTERNS = [
    r"-\d{8}$",           # dated snapshots like -20260305
    r":free$",            # OpenRouter free tier duplicates
    r":nitro$",           # OpenRouter nitro variants
    r":extended$",        # extended context variants
    r":floor$",           # floor pricing variants
    r"-fp\d+",            # quantized variants
    r"-int\d+",           # quantized variants
    r"-gguf",             # GGUF quantized
    r"-awq",              # AWQ quantized
    r"-gptq",             # GPTQ quantized
    r"-fast$",            # premium speed variants (e.g. claude-opus-4.6-fast)
    r"-fast-\d",          # fast numbered variants (e.g. grok-code-fast-1)
    r"preview",           # preview/beta models
    r"guard",             # safety/guard models, not generative
    r"nano",              # smallest tier — below benchmark scope
    r"image",             # image generation variants
    r"lite",              # lite variants
    r"creative",          # creative/specialty variants
    r"multi-agent",       # multi-agent orchestration variants
    r"code",              # coding-specific variants
    r"solidity",          # domain-specific fine-tunes
    r"nemotron",          # NVIDIA repackaged models
    r"speciale",          # specialty variants
    r"-exp$",             # experimental variants
    r"-terminus",         # third-party hosted variants
    r"-chat$",            # chat-specific sub-variants
    r"customtools",       # tool-specific variants
    r"audio",             # audio-specific models
]


def fetch_openrouter_catalog(api_key: str | None = None) -> list[dict]:
    """Fetch the full model catalog from OpenRouter."""
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    resp = httpx.get(OPENROUTER_MODELS_URL, headers=headers, timeout=30.0)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", [])


def classify_model(model_id: str) -> str | None:
    """Return the family name if this model belongs to a tracked family."""
    model_lower = model_id.lower()
    for family, config in FAMILY_CONFIG.items():
        for prefix in config["prefixes"]:
            if model_lower.startswith(prefix.lower()):
                return family
    # Fallback: check bare model name for direct-API and HuggingFace IDs
    # e.g., "claude-opus-4-6" → "claude", "Qwen/Qwen2.5-72B" → "qwen"
    bare = model_lower.split("/")[-1] if "/" in model_lower else model_lower
    family_keywords = {
        "claude": "claude", "gpt": "gpt", "gemini": "gemini",
        "grok": "grok", "llama": "llama", "deepseek": "deepseek",
        "mistral": "mistral", "qwen": "qwen", "command": "command",
        "gemma": "gemma", "phi": "phi", "glm": "glm",
    }
    for family, keyword in family_keywords.items():
        if keyword in bare:
            return family
    return None


def is_excluded(model_id: str) -> bool:
    """Check if a model ID matches any exclusion pattern."""
    return any(re.search(pattern, model_id, re.IGNORECASE) for pattern in _SKIP_PATTERNS)


def _parse_pricing(pricing: dict) -> tuple[float, float]:
    """Parse OpenRouter pricing dict to (input_per_M, output_per_M)."""
    # OpenRouter prices are per-token as strings
    prompt_per_tok = float(pricing.get("prompt", "0") or "0")
    completion_per_tok = float(pricing.get("completion", "0") or "0")
    return prompt_per_tok * 1_000_000, completion_per_tok * 1_000_000


def _model_sort_key(model: dict) -> tuple:
    """Sort key: prefer larger context, newer created date, higher pricing."""
    created = model.get("created", 0) or 0
    ctx = model.get("context_length", 0) or 0
    pricing = model.get("pricing", {})
    cost = float(pricing.get("prompt", "0") or "0")
    return (created, ctx, cost)


def select_flagships(
    catalog: list[dict],
) -> dict[str, list[dict]]:
    """Filter catalog to tracked families, select top models per family."""
    by_family: dict[str, list[dict]] = {}

    for model in catalog:
        model_id = model.get("id", "")

        # Must be text-capable
        arch = model.get("architecture", {})
        modality = arch.get("modality", "")
        if "text" not in modality:
            continue

        # Must belong to a tracked family AND be from the canonical provider.
        # This filters out third-party re-hosted models (e.g., nex-agi/deepseek-*,
        # alfredpros/codellama-*) that use a different org prefix.
        family = classify_model(model_id)
        if family is None:
            continue

        # Verify the model ID starts with one of the family's canonical prefixes
        is_canonical = any(
            model_id.lower().startswith(p.lower())
            for p in FAMILY_CONFIG[family]["prefixes"]
        )
        if not is_canonical:
            continue

        # Skip excluded variants
        if is_excluded(model_id):
            continue

        # Skip models with extreme pricing (> $20/M input) —
        # these are premium/pro tiers, not standard flagships
        pricing = model.get("pricing", {})
        input_price = float(pricing.get("prompt", "0") or "0") * 1_000_000
        if input_price > 20.0:
            continue

        by_family.setdefault(family, []).append(model)

    # Sort each family and pick top N
    selected: dict[str, list[dict]] = {}
    for family, models in by_family.items():
        max_tiers = FAMILY_CONFIG[family]["max_tiers"]
        # Sort by recency and capability (newest, largest context first)
        models.sort(key=_model_sort_key, reverse=True)
        selected[family] = models[:max_tiers]

    return selected


def normalize_model_id(model_id: str) -> str:
    """Normalize a model ID to OpenRouter/registry format for comparison."""
    return to_registry_id(model_id)


def load_collected_models(jsonl_path: Path) -> dict[str, int]:
    """Scan informants.jsonl and return {model_id: record_count}.

    Returns both the original ID and the normalized (OpenRouter) ID
    so cross-referencing works for direct-API models.
    """
    counts: dict[str, int] = {}
    if not jsonl_path.exists():
        return counts

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
                counts[mid] = counts.get(mid, 0) + 1
                # Also index under the normalized ID
                norm = normalize_model_id(mid)
                if norm != mid:
                    counts[norm] = counts.get(norm, 0) + 1

    return counts


def build_registry_entry(model: dict, family: str) -> dict:
    """Build a registry entry from an OpenRouter model object."""
    config = FAMILY_CONFIG[family]
    model_id = model["id"]
    pricing = model.get("pricing", {})
    input_per_m, output_per_m = _parse_pricing(pricing)

    # Determine adapter routing
    adapter = config["preferred_adapter"]
    direct_key = config.get("direct_env_key")
    has_direct_key = bool(direct_key and os.environ.get(direct_key))

    # Only use direct adapter if we have the API key
    if adapter != "openrouter" and not has_direct_key:
        adapter = "openrouter"

    supports_reasoning = "include_reasoning" in (
        model.get("supported_parameters") or []
    ) or "reasoning" in (model.get("supported_parameters") or [])

    return {
        "model_id": model_id,
        "family": family,
        "origin": config["origin"],
        "open_weights": config["open_weights"],
        "collection_method": adapter,
        "context_length": model.get("context_length", 0),
        "pricing_input_per_m": round(input_per_m, 2),
        "pricing_output_per_m": round(output_per_m, 2),
        "supports_reasoning": supports_reasoning,
        "openrouter_created": model.get("created"),
        "discovered_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "display_name": model.get("name", model_id),
    }


def scan(catalog: list[dict], collected: dict[str, int]) -> dict:
    """Produce a scan report: new, stale, and current models."""
    flagships = select_flagships(catalog)
    catalog_ids = set()
    for models in flagships.values():
        for m in models:
            catalog_ids.add(m["id"])

    new_models = []
    current_models = []
    stale_models = []

    # Models in catalog but not collected
    for family, models in sorted(flagships.items()):
        for m in models:
            mid = m["id"]
            entry = build_registry_entry(m, family)
            count = collected.get(mid, 0)
            if count == 0:
                entry["status"] = "new"
                entry["records"] = 0
                new_models.append(entry)
            else:
                entry["status"] = "current"
                entry["records"] = count
                current_models.append(entry)

    # Models collected but not in current catalog.
    # Skip normalized aliases (they're just index duplicates) and
    # check both direct and OpenRouter forms before marking stale.
    seen_originals: set[str] = set()
    for mid, count in sorted(collected.items()):
        # Skip the normalized alias entries
        if mid in REGISTRY_TO_DIRECT and mid not in seen_originals:
            continue
        seen_originals.add(mid)

        norm = normalize_model_id(mid)
        if norm not in catalog_ids and mid not in catalog_ids:
            family = classify_model(mid) or classify_model(norm) or "unknown"
            # Check if a newer model from this family exists
            family_new = [m for m in new_models if m["family"] == family]
            reason = "not in current OpenRouter catalog"
            if family_new:
                successor = family_new[0]["model_id"]
                reason = f"superseded by {successor}"
            stale_models.append({
                "model_id": mid,
                "family": family,
                "status": "stale",
                "records": count,
                "reason": reason,
            })

    return {
        "scan_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "total_catalog_models": len(catalog),
        "tracked_families": len(FAMILY_CONFIG),
        "selected_flagships": sum(len(m) for m in flagships.values()),
        "new": new_models,
        "stale": stale_models,
        "current": current_models,
    }


def print_scan_report(report: dict) -> None:
    """Print a human-readable scan report."""
    print(f"Model Discovery Scan — {report['scan_date']}")
    print(f"  OpenRouter catalog: {report['total_catalog_models']} models")
    print(f"  Tracked families:   {report['tracked_families']}")
    print(f"  Selected flagships: {report['selected_flagships']}")
    print()

    if report["new"]:
        print(f"NEW — {len(report['new'])} models not yet collected:")
        for m in report["new"]:
            reasoning = " [reasoning]" if m.get("supports_reasoning") else ""
            adapter = m["collection_method"]
            price = f"${m['pricing_input_per_m']:.2f}/${m['pricing_output_per_m']:.2f}"
            print(f"  {m['model_id']:55s} {price:>16s}  {adapter:15s}{reasoning}")
        print()

    if report["stale"]:
        print(f"STALE — {len(report['stale'])} collected models no longer in catalog:")
        for m in report["stale"]:
            print(f"  {m['model_id']:55s} {m['records']:3d} records  ({m['reason']})")
        print()

    if report["current"]:
        print(f"CURRENT — {len(report['current'])} models collected and still available:")
        for m in report["current"]:
            reasoning = " [reasoning]" if m.get("supports_reasoning") else ""
            print(f"  {m['model_id']:55s} {m['records']:3d} records{reasoning}")
        print()


def update_registry(report: dict) -> Path:
    """Write the registry.json from scan results."""
    # Merge current + new into registry (stale models excluded)
    entries = []
    for m in report["current"] + report["new"]:
        entry = {k: v for k, v in m.items() if k != "status"}
        entries.append(entry)

    registry = {
        "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "families": list(FAMILY_CONFIG.keys()),
        "models": entries,
    }

    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n")
    return REGISTRY_PATH


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discover and track frontier model releases.",
    )
    parser.add_argument(
        "--scan", action="store_true",
        help="Scan OpenRouter catalog and report new/stale/current models",
    )
    parser.add_argument(
        "--update-registry", action="store_true",
        help="Write registry.json from scan results",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format for --scan (default: text)",
    )
    args = parser.parse_args()

    if not args.scan and not args.update_registry:
        parser.print_help()
        return 1

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    api_key = os.environ.get("OPENROUTER_API_KEY")
    print("Fetching OpenRouter model catalog...", flush=True)
    catalog = fetch_openrouter_catalog(api_key)
    print(f"  {len(catalog)} models in catalog")

    collected = load_collected_models(INFORMANTS_PATH)
    print(f"  {sum(collected.values())} records across {len(collected)} models collected")
    print()

    report = scan(catalog, collected)

    if args.scan:
        if args.format == "json":
            print(json.dumps(report, indent=2))
        else:
            print_scan_report(report)

    if args.update_registry:
        path = update_registry(report)
        n = len(report["current"]) + len(report["new"])
        print(f"Registry written: {path} ({n} models)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
