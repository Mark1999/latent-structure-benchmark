"""Tests for grounding baseline loader."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from cdb_analyze.grounding import (
    compute_item_intersection,
    list_baselines,
    load_cooccurrence,
    load_grounding_ref,
    load_items,
)


def _setup_baseline(tmp_path: Path) -> Path:
    """Create a minimal grounding baseline directory."""
    baseline_dir = tmp_path / "family" / "test_baseline"
    baseline_dir.mkdir(parents=True)

    # items.txt
    (baseline_dir / "items.txt").write_text(
        "# Family terms\n"
        "mother\n"
        "father\n"
        "sister\n"
        "brother\n"
    )

    # cooccurrence.csv
    (baseline_dir / "cooccurrence.csv").write_text(
        "mother,father,sister,brother\n"
        "1.0,0.8,0.3,0.2\n"
        "0.8,1.0,0.2,0.3\n"
        "0.3,0.2,1.0,0.9\n"
        "0.2,0.3,0.9,1.0\n"
    )

    # grounding_ref.json
    ref = {
        "baseline_id": "test_baseline",
        "baseline_kind": "published",
        "domain_slug": "family",
        "source_citation": "Test et al. (2026)",
        "source_url": None,
        "collected_year": 2020,
        "n_human_informants": 50,
        "population_description": "Test population",
        "method": "pile sort",
        "irb_status": "not_applicable",
        "mds_coordinate": [0.0, 0.0],
        "distance_to_nearest_model": 0.0,
        "nearest_model_id": "",
        "item_intersection_size": 0,
        "item_intersection_total": 0,
    }
    (baseline_dir / "grounding_ref.json").write_text(json.dumps(ref))

    return tmp_path


def test_list_baselines(tmp_path: Path):
    root = _setup_baseline(tmp_path)
    baselines = list_baselines("family", root)
    assert baselines == ["test_baseline"]


def test_list_baselines_empty(tmp_path: Path):
    baselines = list_baselines("nonexistent", tmp_path)
    assert baselines == []


def test_load_items(tmp_path: Path):
    root = _setup_baseline(tmp_path)
    items = load_items("family", "test_baseline", root)
    assert items == ["mother", "father", "sister", "brother"]


def test_load_items_skips_comments(tmp_path: Path):
    root = _setup_baseline(tmp_path)
    items = load_items("family", "test_baseline", root)
    assert "#" not in " ".join(items)


def test_load_cooccurrence(tmp_path: Path):
    root = _setup_baseline(tmp_path)
    items, matrix = load_cooccurrence("family", "test_baseline", root)

    assert items == ["mother", "father", "sister", "brother"]
    assert matrix.shape == (4, 4)
    # Check a known value
    assert matrix[0, 1] == 0.8
    # Diagonal
    np.testing.assert_array_almost_equal(np.diag(matrix), [1.0, 1.0, 1.0, 1.0])


def test_load_grounding_ref(tmp_path: Path):
    root = _setup_baseline(tmp_path)
    ref = load_grounding_ref("family", "test_baseline", root)

    assert ref.baseline_id == "test_baseline"
    assert ref.baseline_kind == "published"
    assert ref.n_human_informants == 50


def test_compute_item_intersection():
    baseline = ["mother", "father", "sister", "brother"]
    model = ["mother", "father", "aunt", "uncle", "sister"]
    size, total = compute_item_intersection(baseline, model)
    assert size == 3  # mother, father, sister
    assert total == 5


def test_compute_item_intersection_case_insensitive():
    baseline = ["Mother", "Father"]
    model = ["mother", "father", "sister"]
    size, total = compute_item_intersection(baseline, model)
    assert size == 2
    assert total == 3
