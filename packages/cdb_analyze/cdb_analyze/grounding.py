"""Human CDA baseline loader and alignment. See ARCHITECTURE.md §4.2.5.

Loads zero or more published/researcher-submitted human CDA datasets from
data/grounding/{domain}/{baseline_id}/ and prepares them for injection as
virtual informants into the MDS plot.

Directory layout per baseline:
    data/grounding/{domain}/{baseline_id}/
        source.md             — citation, methodology, IRB, year
        items.txt             — canonical item set (one per line)
        cooccurrence.csv      — symmetric matrix, header row = items
        grounding_ref.json    — GroundingRef metadata
        pile_sort_raw.csv     — (optional) per-subject data for bootstrap
"""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path

import numpy as np
from cdb_core import GroundingRef
from numpy.typing import NDArray

logger = logging.getLogger(__name__)

GROUNDING_ROOT = Path("data/grounding")


def list_baselines(domain_slug: str, root: Path = GROUNDING_ROOT) -> list[str]:
    """List available baseline_ids for a domain.

    Returns:
        Sorted list of baseline directory names.
    """
    domain_dir = root / domain_slug
    if not domain_dir.is_dir():
        return []
    return sorted(
        d.name for d in domain_dir.iterdir()
        if d.is_dir() and (d / "grounding_ref.json").exists()
    )


def load_grounding_ref(
    domain_slug: str,
    baseline_id: str,
    root: Path = GROUNDING_ROOT,
) -> GroundingRef:
    """Load a GroundingRef from its JSON file.

    Args:
        domain_slug: Domain this baseline belongs to.
        baseline_id: Baseline directory name.
        root: Grounding data root.

    Returns:
        Validated GroundingRef.
    """
    ref_path = root / domain_slug / baseline_id / "grounding_ref.json"
    data = json.loads(ref_path.read_text())
    return GroundingRef(**data)


def load_items(
    domain_slug: str,
    baseline_id: str,
    root: Path = GROUNDING_ROOT,
) -> list[str]:
    """Load the canonical item set for a baseline.

    Items are one per line, lowercased, stripped. Lines starting with #
    are comments and are skipped.
    """
    items_path = root / domain_slug / baseline_id / "items.txt"
    items = []
    for line in items_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        items.append(line.lower())
    return items


def load_cooccurrence(
    domain_slug: str,
    baseline_id: str,
    root: Path = GROUNDING_ROOT,
) -> tuple[list[str], NDArray[np.float64]]:
    """Load a co-occurrence matrix from CSV.

    The CSV has a header row of item names. The matrix is symmetric
    with diagonal = 1.0.

    Returns:
        (items, matrix) where items is the header row and matrix
        is a numpy array of shape (n_items, n_items).
    """
    csv_path = root / domain_slug / baseline_id / "cooccurrence.csv"
    with open(csv_path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        items = [h.strip().lower() for h in header]
        rows = []
        for row in reader:
            rows.append([float(x) for x in row])

    matrix = np.array(rows, dtype=np.float64)

    if matrix.shape != (len(items), len(items)):
        msg = (
            f"Matrix shape {matrix.shape} does not match "
            f"{len(items)} items in header"
        )
        raise ValueError(msg)

    return items, matrix


def compute_item_intersection(
    baseline_items: list[str],
    model_items: list[str],
) -> tuple[int, int]:
    """Compute the intersection between baseline and model item sets.

    Returns:
        (intersection_size, total_model_items)
    """
    baseline_set = {item.lower() for item in baseline_items}
    model_set = {item.lower() for item in model_items}
    intersection = baseline_set & model_set
    return len(intersection), len(model_set)


def load_all_groundings(
    domain_slug: str,
    root: Path = GROUNDING_ROOT,
) -> list[GroundingRef]:
    """Load all available GroundingRefs for a domain.

    Skips baselines whose grounding_ref.json is a placeholder.
    """
    refs = []
    for baseline_id in list_baselines(domain_slug, root):
        try:
            ref = load_grounding_ref(domain_slug, baseline_id, root)
            refs.append(ref)
        except Exception:
            logger.warning(
                "Skipping baseline %s/%s: invalid grounding_ref.json",
                domain_slug, baseline_id,
            )
    return refs
