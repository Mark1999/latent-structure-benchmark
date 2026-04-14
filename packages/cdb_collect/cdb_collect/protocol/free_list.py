"""CDA Step 1 — free listing. See ARCHITECTURE.md §4.1.1."""

from __future__ import annotations

import re
from pathlib import Path

from cdb_core import Domain, FreelistRecord

from cdb_collect.adapters.base import AdapterResult, ModelAdapter

_PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"


def load_prompt(domain: Domain, version: str = "v1") -> str:
    """Load and substitute the free-list prompt template."""
    path = _PROMPTS_DIR / version / "free_list.md"
    template = path.read_text()
    return template.replace("{{domain_seed}}", domain.prompt_seed)


def parse_free_list(text: str, truncation_k: int = 25) -> tuple[list[str], list[str]]:
    """Parse a free-list response into normalized items.

    Returns:
        (parsed_items, raw_order) where parsed_items is deduplicated and
        truncated to truncation_k, and raw_order is all items before
        dedup/truncation.
    """
    raw_order: list[str] = []

    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue

        # Strip numbering prefixes: "1.", "1)", "1:", "- ", "* "
        line = re.sub(r"^\d+[\.\)\:]\s*", "", line)
        line = re.sub(r"^[-\*]\s+", "", line)
        line = line.strip()

        if not line:
            continue

        # Skip preamble/postamble lines (common model output artifacts)
        line_lower = line.lower()
        if any(line_lower.startswith(p) for p in (
            "here is", "here are", "here's", "below is", "below are",
            "the following", "these are", "this is", "i ",
            "sure", "certainly", "of course", "absolutely",
            "note:", "note that", "please note",
        )):
            continue
        # Skip lines that are clearly sentences, not items (>60 chars)
        if len(line) > 60:
            continue

        # Normalize: lowercase, strip trailing punctuation, collapse whitespace
        item = line.lower()
        item = re.sub(r"[,;\.!?]+$", "", item)
        item = re.sub(r"\s+", " ", item).strip()

        if item:
            raw_order.append(item)

    # Deduplicate preserving first-occurrence order
    seen: set[str] = set()
    parsed_items: list[str] = []
    for item in raw_order:
        if item not in seen:
            seen.add(item)
            parsed_items.append(item)

    # Truncate to truncation_k most salient (first-mentioned)
    parsed_items = parsed_items[:truncation_k]

    return parsed_items, raw_order


async def run_free_list(
    adapter: ModelAdapter,
    domain: Domain,
    run_index: int,
    prompt_version: str = "v1",
) -> tuple[FreelistRecord, AdapterResult]:
    """Execute the free-list step of the CDA protocol.

    Args:
        adapter: The model adapter to call.
        domain: The domain definition.
        run_index: The run index (0-based).
        prompt_version: Prompt template version.

    Returns:
        (FreelistRecord, AdapterResult) tuple.
    """
    prompt = load_prompt(domain, version=prompt_version)

    # Free listing uses temperature 0.7 per ARCHITECTURE.md §4.1.3
    result = await adapter.complete(prompt, temperature=0.7)

    parsed_items, raw_order = parse_free_list(
        result.text, truncation_k=domain.truncation_k,
    )

    record = FreelistRecord(
        prompt_verbatim=prompt,
        prompt_version=prompt_version,
        response_verbatim=result.text,
        response_object_json=result.raw_response,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        latency_ms=result.latency_ms,
        stop_reason=result.stop_reason,
        parsed_items=parsed_items,
        parsed_raw_order=raw_order,
    )

    return record, result
