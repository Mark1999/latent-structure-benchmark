"""Spend cap enforcement and cost tracking. See ARCHITECTURE.md §6.2."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)

# Per-million-token pricing (input, output) by model family.
# Update when providers change pricing.
PRICING: dict[str, tuple[float, float]] = {
    # Anthropic (direct)
    "claude-opus-4-6": (15.0, 75.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-haiku-4-5": (0.80, 4.0),
    # OpenRouter — OpenAI
    "openai/gpt-4o": (2.50, 10.0),
    "openai/gpt-4-turbo": (10.0, 30.0),
    # OpenRouter — Google
    "google/gemini-2.5-pro": (1.25, 10.0),
    "google/gemini-2.5-flash": (0.15, 0.60),
    # OpenRouter — Meta
    "meta-llama/llama-3.1-70b-instruct": (0.40, 0.40),
    "meta-llama/llama-3.1-405b-instruct": (2.00, 2.00),
    # OpenRouter — Mistral
    "mistralai/mistral-large": (2.00, 6.00),
    "mistralai/mistral-small": (0.10, 0.30),
    # OpenRouter — Cohere
    "cohere/command-r-plus": (2.50, 10.0),
    # OpenRouter — Qwen
    "qwen/qwen-2.5-72b-instruct": (0.40, 0.40),
    # OpenRouter — xAI
    "x-ai/grok-2": (2.00, 10.0),
    # HuggingFace Inference Providers (model IDs use HF repo format)
    "Qwen/Qwen2.5-72B-Instruct": (0.35, 0.40),
    "mistralai/Mixtral-8x22B-Instruct-v0.1": (0.65, 0.65),
}

# Fallback pricing for unknown models
DEFAULT_PRICING: tuple[float, float] = (15.0, 75.0)


def get_cap() -> float:
    """Read the monthly spend cap from the environment.

    Returns:
        The cap in USD (default 300).
    """
    return float(os.environ.get("CDB_MAX_SPEND_USD", "300"))


def compute_cost(
    input_tokens: int,
    output_tokens: int,
    model_id: str,
) -> float:
    """Compute the USD cost for a single API call.

    Args:
        input_tokens: Number of input tokens.
        output_tokens: Number of output tokens.
        model_id: The model ID string (used to look up pricing).

    Returns:
        Cost in USD.
    """
    price_in, price_out = DEFAULT_PRICING
    for prefix, (pi, po) in PRICING.items():
        if model_id.startswith(prefix):
            price_in, price_out = pi, po
            break

    return (input_tokens * price_in + output_tokens * price_out) / 1_000_000


def check_spend(
    cumulative_usd: float, cap_usd: float | None = None,
) -> Literal["ok", "warning", "halt"]:
    """Check cumulative spend against the cap.

    Args:
        cumulative_usd: Total spend so far this month.
        cap_usd: The cap (defaults to env var CDB_MAX_SPEND_USD).

    Returns:
        "ok" if under 80%, "warning" at 80-99%, "halt" at 100%+.
    """
    if cap_usd is None:
        cap_usd = get_cap()

    if cap_usd <= 0:
        return "halt"

    ratio = cumulative_usd / cap_usd
    if ratio >= 1.0:
        return "halt"
    if ratio >= 0.8:
        return "warning"
    return "ok"


def get_monthly_spend(jsonl_path: Path, month: str | None = None) -> float:
    """Sum cost_usd from InformantRecords in the JSONL for a given month.

    Args:
        jsonl_path: Path to informants.jsonl.
        month: Month string "YYYY-MM" or "current" or None (defaults to current).

    Returns:
        Total spend in USD for that month.
    """
    if month is None or month == "current":
        month = datetime.now().strftime("%Y-%m")

    if not jsonl_path.exists():
        return 0.0

    total = 0.0
    with open(jsonl_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            collection_date = record.get("collection_date", "")
            if not collection_date.startswith(month):
                continue

            # Sum cost from token counts across all steps
            for step_key in ("freelist", "pile_sort", "interview"):
                step = record.get(step_key, {})
                in_tok = step.get("input_tokens", 0)
                out_tok = step.get("output_tokens", 0)
                if in_tok or out_tok:
                    model_id = record.get("model_id", "")
                    total += compute_cost(in_tok, out_tok, model_id)

    return total
