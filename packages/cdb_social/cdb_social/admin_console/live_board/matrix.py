"""Live board pass/fail/in-flight matrix for the LSB ops console.

compute_matrix reads informants.jsonl and lane state to produce a
per-(model, domain) cell count table suitable for the live board.

No LLM imports. No statistical computation. Read-only over informants.jsonl.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Cell state
# ---------------------------------------------------------------------------


@dataclass
class CellCounts:
    """Counts for one (model, domain) cell."""

    passed: int = 0  # qa_passed=True records
    failed: int = 0  # qa_passed=False records
    in_flight: bool = False  # lane is currently running for this cell


# ---------------------------------------------------------------------------
# Matrix computation
# ---------------------------------------------------------------------------


def compute_matrix(
    informants_path: Path,
    model_ids: list[str],
    domain_slugs: list[str],
    *,
    running_model_ids: set[str] | None = None,
) -> dict[str, dict[str, CellCounts]]:
    """Compute a pass/fail/in-flight matrix from informants.jsonl.

    Args:
        informants_path: Path to data/raw/informants.jsonl (read-only).
            Returns zero-counts for all cells if the file is absent.
        model_ids: Ordered list of model IDs to include as rows.
        domain_slugs: Ordered list of domain slugs to include as columns.
        running_model_ids: Set of model_ids whose lanes are currently running.
            When provided, cells for those models have in_flight=True.

    Returns:
        Nested dict: result[model_id][domain_slug] = CellCounts.
        All (model, domain) combinations are present even when counts are zero.
    """
    if running_model_ids is None:
        running_model_ids = set()

    # Initialise all cells
    matrix: dict[str, dict[str, CellCounts]] = {
        mid: {slug: CellCounts() for slug in domain_slugs} for mid in model_ids
    }

    model_set = set(model_ids)
    domain_set = set(domain_slugs)

    if not informants_path.exists():
        # Mark in-flight cells and return empty counts
        for mid in model_ids:
            if mid in running_model_ids:
                for slug in domain_slugs:
                    matrix[mid][slug].in_flight = True
        return matrix

    try:
        text = informants_path.read_text(encoding="utf-8")
    except OSError:
        return matrix

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec: Any = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(rec, dict):
            continue

        mid = rec.get("model_id", "")
        dom = rec.get("domain_slug", "")
        if mid not in model_set or dom not in domain_set:
            continue

        if rec.get("qa_passed", False):
            matrix[mid][dom].passed += 1
        else:
            matrix[mid][dom].failed += 1

    # Apply in-flight status
    for mid in model_ids:
        if mid in running_model_ids:
            for slug in domain_slugs:
                matrix[mid][slug].in_flight = True

    return matrix
