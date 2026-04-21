"""Baseline item list loader for human CDA data. See ARCHITECTURE.md §4.2.5."""

from __future__ import annotations

from pathlib import Path

# Default location for grounding data
_GROUNDING_DIR = Path(__file__).resolve().parents[3] / "data" / "grounding"


def load_baseline_items(
    domain_slug: str, baseline_id: str,
) -> list[str]:
    """Load the item list from a human baseline.

    Reads items.txt from data/grounding/{domain_slug}/{baseline_id}/items.txt.
    One item per line, UTF-8, no header.

    Args:
        domain_slug: Domain slug (e.g., "family").
        baseline_id: Baseline identifier (e.g., "romney_1996").

    Returns:
        List of item strings.

    Raises:
        FileNotFoundError: If items.txt does not exist.
        ValueError: If the file is empty or contains no valid items.
    """
    path = _GROUNDING_DIR / domain_slug / baseline_id / "items.txt"
    if not path.exists():
        raise FileNotFoundError(f"Baseline items not found: {path}")

    items: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            items.append(line)

    if not items:
        raise ValueError(f"No items found in baseline: {path}")

    return items
