"""CDA Step 2 — pile sorting. See ARCHITECTURE.md §4.1.1."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from cdb_core import PileSortRecord

from cdb_collect.adapters.base import AdapterResult, ModelAdapter
from cdb_collect.exceptions import PileSortParseError

logger = logging.getLogger(__name__)

_PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"

# Max retries on JSON parse failure per ARCHITECTURE.md §4.1.1
_MAX_PARSE_RETRIES = 3


def load_prompt(
    items: list[str], domain_seed: str, version: str = "v1",
) -> str:
    """Load and substitute the pile-sort prompt template."""
    path = _PROMPTS_DIR / version / "pile_sort.md"
    template = path.read_text(encoding="utf-8")
    items_text = "\n".join(f"- {item}" for item in items)
    prompt = template.replace("{{items}}", items_text)
    prompt = prompt.replace("{{item_count}}", str(len(items)))
    prompt = prompt.replace("{{domain_seed}}", domain_seed)
    return prompt


def _extract_json(text: str) -> dict[str, Any]:
    """Extract JSON from response text, handling markdown fences."""
    # Try direct parse first
    text = text.strip()
    try:
        result: dict[str, Any] = json.loads(text)
        return result
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code blocks
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group(1).strip())
            return result
        except json.JSONDecodeError:
            pass

    # Try finding JSON object in the text
    brace_start = text.find("{")
    brace_end = text.rfind("}")
    if brace_start >= 0 and brace_end > brace_start:
        try:
            result = json.loads(text[brace_start:brace_end + 1])
            return result
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract valid JSON from response: {text[:200]}")


def parse_pile_sort(
    text: str, expected_items: list[str],
) -> tuple[list[list[str]], list[list[int]]]:
    """Parse pile sort JSON response into piles and binary matrix.

    Args:
        text: Raw response text (may contain JSON or markdown-wrapped JSON).
        expected_items: The items that should appear in the piles.

    Returns:
        (piles, matrix) where piles is list of lists of item strings and
        matrix is a binary co-occurrence matrix.

    Raises:
        ValueError: If JSON is invalid, items are missing, or items are duplicated.
    """
    data = _extract_json(text)

    if "piles" not in data:
        raise ValueError("JSON missing 'piles' key")

    raw_piles = data["piles"]
    if not isinstance(raw_piles, list):
        raise ValueError("'piles' must be a list")

    # Normalize item names for matching
    expected_lower = {item.lower().strip(): item for item in expected_items}

    # Normalize and validate piles
    piles: list[list[str]] = []
    seen: set[str] = set()

    for pile in raw_piles:
        if not isinstance(pile, list):
            raise ValueError(f"Each pile must be a list, got {type(pile)}")

        normalized_pile: list[str] = []
        for raw_item in pile:
            item = str(raw_item).lower().strip()

            # Try exact match first, then fuzzy
            if item in expected_lower:
                canonical = expected_lower[item]
            else:
                # Try stripping punctuation for matching
                stripped = re.sub(r"[^\w\s-]", "", item).strip()
                if stripped in expected_lower:
                    canonical = expected_lower[stripped]
                else:
                    # Skip unexpected items rather than hard-failing
                    continue

            if canonical.lower() in seen:
                # Skip duplicates rather than hard-failing. The LLM
                # sometimes produces near-duplicate items in a long free
                # list (e.g., "Bonus Mom" at rank 15 and "bonus mother"
                # at rank 87 both normalize to "bonus mom"), and then
                # assigns both instances to piles during pile sort. The
                # first occurrence wins; subsequent occurrences are
                # dropped — consistent with how unknown items are handled
                # at line 117. Surfaced by the 2026-04-20 shakedown where
                # this pattern caused 50% of Claude Sonnet's runs to fail
                # on 200-item free lists. Retaining the record (instead
                # of losing it) is defensible because "which pile should
                # the duplicate go in?" has no correct answer — first
                # occurrence is as good as any other choice.
                logger.warning(
                    "Duplicate item in pile sort: %r — keeping first "
                    "occurrence, skipping this one.",
                    raw_item,
                )
                continue

            seen.add(canonical.lower())
            normalized_pile.append(canonical)

        piles.append(normalized_pile)

    # Check all items are accounted for — tolerate up to 10% missing
    missing = set(expected_lower.keys()) - seen
    max_missing = max(1, len(expected_lower) // 10)
    if len(missing) > max_missing:
        raise ValueError(f"Items missing from pile sort: {missing}")

    # Build binary matrix
    matrix = build_binary_matrix(piles, expected_items)

    return piles, matrix


def build_binary_matrix(
    piles: list[list[str]], items: list[str],
) -> list[list[int]]:
    """Build a binary co-occurrence matrix from pile assignments.

    matrix[i][j] = 1 if items[i] and items[j] appear in the same pile.
    Diagonal = 1. Symmetric.
    """
    n = len(items)
    item_to_idx = {item.lower(): i for i, item in enumerate(items)}

    matrix = [[0] * n for _ in range(n)]

    # Set diagonal
    for i in range(n):
        matrix[i][i] = 1

    # Set co-occurrence for items in same pile
    for pile in piles:
        pile_indices = [
            item_to_idx[item.lower()]
            for item in pile
            if item.lower() in item_to_idx
        ]
        for a in pile_indices:
            for b in pile_indices:
                matrix[a][b] = 1

    return matrix


DEFAULT_PILESORT_TEMPERATURE: float = 0.3


async def run_pile_sort(
    adapter: ModelAdapter,
    items: list[str],
    domain_seed: str,
    run_index: int,
    prompt_version: str = "v1",
    max_retries: int = _MAX_PARSE_RETRIES,
    *,
    temperature: float | None = None,
) -> tuple[PileSortRecord, AdapterResult]:
    """Execute the pile-sort step of the CDA protocol.

    Uses temperature 0.3 for modal categorization per ARCHITECTURE.md §4.1.3
    when no override is provided. Retries up to max_retries times on JSON
    parse failure.

    Args:
        temperature: Optional override for the sampling temperature. When
            None, uses ``DEFAULT_PILESORT_TEMPERATURE`` (0.3). Set to 0.0
            for the shakedown determinism cell.

    Returns:
        (PileSortRecord, AdapterResult) tuple.

    Raises:
        PileSortParseError: If parsing fails after all retries. Carries all
            AdapterResult objects (one per attempt) so the caller can write
            verbatim bytes to failures.jsonl.
    """
    prompt = load_prompt(items, domain_seed, version=prompt_version)
    effective_temp = (
        temperature if temperature is not None else DEFAULT_PILESORT_TEMPERATURE
    )

    all_results: list[AdapterResult] = []
    all_errors: list[Exception] = []

    for attempt in range(max_retries):
        result = await adapter.complete(prompt, temperature=effective_temp)
        all_results.append(result)

        try:
            piles, matrix = parse_pile_sort(result.text, items)

            record = PileSortRecord(
                prompt_verbatim=prompt,
                prompt_version=prompt_version,
                response_verbatim=result.text,
                thinking_verbatim=result.thinking_text,
                response_object_json=result.raw_response,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                thoughts_token_count=result.thoughts_token_count,
                latency_ms=result.latency_ms,
                stop_reason=result.stop_reason,
                parsed_piles=piles,
                parsed_matrix=matrix,
            )
            return record, result

        except ValueError as e:
            all_errors.append(e)
            logger.warning(
                "Pile sort parse failed (attempt %d/%d): %s",
                attempt + 1, max_retries, e,
            )

    raise PileSortParseError(
        f"Pile sort parsing failed after {max_retries} attempts: {all_errors[-1]}",
        attempts=all_results,
        per_attempt_errors=all_errors,
        prompt_verbatim=prompt,
    )
