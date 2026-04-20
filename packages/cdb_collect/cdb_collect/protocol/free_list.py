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


def parse_free_list(text: str) -> tuple[list[str], list[str]]:
    """Parse a free-list response into normalized items.

    Returns:
        (parsed_items, raw_order) where parsed_items is deduplicated
        (preserving first-occurrence order), and raw_order is all items
        before dedup. No truncation is applied here — truncation is
        data-driven via salience elbow detection after consensus pooling.
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

    return parsed_items, raw_order


DEFAULT_FREELIST_TEMPERATURE: float = 0.7


async def run_free_list(
    adapter: ModelAdapter,
    domain: Domain,
    run_index: int,
    prompt_version: str = "v1",
    *,
    temperature: float | None = None,
) -> tuple[FreelistRecord, AdapterResult]:
    """Execute the free-list step of the CDA protocol.

    Args:
        adapter: The model adapter to call.
        domain: The domain definition.
        run_index: The run index (0-based).
        prompt_version: Prompt template version.
        temperature: Optional override for the sampling temperature. When
            None, uses ``DEFAULT_FREELIST_TEMPERATURE`` (0.7) per
            ARCHITECTURE.md §4.1.3. Set explicitly (e.g. 0.0 for the
            shakedown determinism cell per docs/SHAKEDOWN_PROTOCOL.md
            §4 determinism-cell row) to override the default.

    Returns:
        (FreelistRecord, AdapterResult) tuple.
    """
    prompt = load_prompt(domain, version=prompt_version)

    effective_temp = (
        temperature if temperature is not None else DEFAULT_FREELIST_TEMPERATURE
    )
    result = await adapter.complete(prompt, temperature=effective_temp)

    parsed_items, raw_order = parse_free_list(result.text)

    record = FreelistRecord(
        prompt_verbatim=prompt,
        prompt_version=prompt_version,
        response_verbatim=result.text,
        thinking_verbatim=result.thinking_text,
        response_object_json=result.raw_response,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        latency_ms=result.latency_ms,
        stop_reason=result.stop_reason,
        parsed_items=parsed_items,
        parsed_raw_order=raw_order,
    )

    return record, result
