"""CDA Step 3 — pile interview / naming. See ARCHITECTURE.md §4.1.1."""

from __future__ import annotations

import re
from pathlib import Path

from cdb_core import InterviewRecord

from cdb_collect.adapters.base import AdapterResult, ModelAdapter

_PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"


def load_prompt(piles: list[list[str]], version: str = "v1") -> str:
    """Load and substitute the pile-interview prompt template."""
    path = _PROMPTS_DIR / version / "pile_interview.md"
    template = path.read_text()

    # Format piles as numbered groups
    lines: list[str] = []
    for i, pile in enumerate(piles, 1):
        items_str = ", ".join(pile)
        lines.append(f"Group {i}: {items_str}")

    return template.replace("{{piles}}", "\n".join(lines))


def parse_pile_interview(
    text: str, expected_count: int,
) -> list[str]:
    """Parse pile interview response into a list of labels.

    Args:
        text: Raw response text with one label per pile.
        expected_count: Expected number of labels (= number of piles).

    Returns:
        List of label strings, one per pile.

    Raises:
        ValueError: If the number of parsed labels doesn't match expected_count.
    """
    labels: list[str] = []

    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue

        # Strip numbering: "1.", "1)", "1:", "Group 1:", etc.
        line = re.sub(r"^(?:group\s+)?\d+[\.\)\:]\s*", "", line, flags=re.IGNORECASE)
        line = re.sub(r"^[-\*]\s+", "", line)
        line = line.strip()

        # Skip lines that look like meta-commentary rather than labels
        line_lower = line.lower()
        if not line or any(line_lower.startswith(p) for p in (
            "here is", "here are", "here's", "below is", "below are",
            "the following", "these are", "this is", "i ",
            "sure", "certainly", "of course", "absolutely",
            "note:", "note that", "please note",
            "let me know", "feel free", "hope this",
        )):
            continue
        # Skip lines that are clearly sentences, not labels (>80 chars)
        if len(line) > 80:
            continue

        # Strip surrounding quotes if present
        if len(line) >= 2 and line[0] in ('"', "'") and line[-1] == line[0]:
            line = line[1:-1].strip()

        if line:
            labels.append(line)

    if len(labels) != expected_count:
        raise ValueError(
            f"Expected {expected_count} labels, got {len(labels)}: {labels}"
        )

    return labels


async def run_pile_interview(
    adapter: ModelAdapter,
    piles: list[list[str]],
    run_index: int,
    prompt_version: str = "v1",
) -> tuple[InterviewRecord, AdapterResult]:
    """Execute the pile-interview step of the CDA protocol.

    Uses temperature 0.3 per ARCHITECTURE.md §4.1.3.

    Returns:
        (InterviewRecord, AdapterResult) tuple.
    """
    prompt = load_prompt(piles, version=prompt_version)

    # Temperature 0.3 for categorization
    result = await adapter.complete(prompt, temperature=0.3)

    labels = parse_pile_interview(result.text, expected_count=len(piles))

    record = InterviewRecord(
        prompt_verbatim=prompt,
        prompt_version=prompt_version,
        response_verbatim=result.text,
        response_object_json=result.raw_response,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        latency_ms=result.latency_ms,
        stop_reason=result.stop_reason,
        parsed_pile_labels=labels,
    )

    return record, result
