"""Tests for baseline item list loader."""

import tempfile
from pathlib import Path

import pytest
from cdb_collect.baselines import load_baseline_items


def test_load_baseline_items():
    with tempfile.TemporaryDirectory() as td:
        items_dir = Path(td) / "family" / "romney_1996"
        items_dir.mkdir(parents=True)
        items_file = items_dir / "items.txt"
        items_file.write_text("mother\nfather\nsister\nbrother\naunt\n")

        # Temporarily patch the grounding dir
        import cdb_collect.baselines as mod
        original = mod._GROUNDING_DIR
        mod._GROUNDING_DIR = Path(td)
        try:
            items = load_baseline_items("family", "romney_1996")
            assert items == ["mother", "father", "sister", "brother", "aunt"]
        finally:
            mod._GROUNDING_DIR = original


def test_load_baseline_items_skips_comments():
    with tempfile.TemporaryDirectory() as td:
        items_dir = Path(td) / "family" / "test_baseline"
        items_dir.mkdir(parents=True)
        (items_dir / "items.txt").write_text(
            "# Header comment\nmother\n# Another comment\nfather\n"
        )

        import cdb_collect.baselines as mod
        original = mod._GROUNDING_DIR
        mod._GROUNDING_DIR = Path(td)
        try:
            items = load_baseline_items("family", "test_baseline")
            assert items == ["mother", "father"]
        finally:
            mod._GROUNDING_DIR = original


def test_load_baseline_items_not_found():
    with pytest.raises(FileNotFoundError):
        load_baseline_items("nonexistent", "nonexistent")


def test_load_baseline_items_empty():
    with tempfile.TemporaryDirectory() as td:
        items_dir = Path(td) / "family" / "empty"
        items_dir.mkdir(parents=True)
        (items_dir / "items.txt").write_text("# Only comments\n")

        import cdb_collect.baselines as mod
        original = mod._GROUNDING_DIR
        mod._GROUNDING_DIR = Path(td)
        try:
            with pytest.raises(ValueError, match="No items"):
                load_baseline_items("family", "empty")
        finally:
            mod._GROUNDING_DIR = original
