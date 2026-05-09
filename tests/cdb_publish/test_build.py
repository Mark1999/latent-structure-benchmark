"""Tests for cdb_publish.build.

No real API calls. All tests use synthetic fixtures written to temp dirs.
See CLAUDE.md §6 R9 (no real API in tests).

Version-selection behaviour (per plan §4 T1, Test 3):
    When a domain directory contains multiple semver JSON files the
    latest version is selected by lexicographic comparison of the stem.
    Lexicographic ordering is correct for LSB's current versioning
    scheme (major always 0, minor a small integer 0-9). Build() reads
    the selected file and ignores all earlier versions.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from cdb_publish.build import DomainValidationError, build
from cdb_publish.schemas.manifest import Manifest


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def _model_ref() -> dict:
    """Return a minimal valid ModelRef dict."""
    return {
        "provider": "anthropic",
        "model_id": "test-model-a",
        "family": "test",
        "origin": "us",
        "open_weights": False,
        "collection_method": "anthropic_api",
        "quantization": None,
        "release_date": "2026-01-01",
        "version_label": "test-model-a",
        "source_notes": "",
    }


def _free_list(model_id: str, domain_slug: str) -> dict:
    """Return a minimal valid FreeList dict for the given model."""
    return {
        "run_id": f"run-{model_id}",
        "model": {**_model_ref(), "model_id": model_id},
        "domain_slug": domain_slug,
        "items": ["alpha", "beta"],
        "raw_order": ["alpha", "beta"],
    }


def _bootstrap_ellipse() -> dict:
    """Return a minimal valid BootstrapEllipse dict."""
    return {
        "center": [0.0, 0.0],
        "semi_major": 0.1,
        "semi_minor": 0.05,
        "rotation_rad": 0.0,
        "n_bootstrap": 100,
    }


def _minimal_domain_result(
    slug: str = "test-domain",
    analysis_version: str = "0.2",
    model_ids: list[str] | None = None,
    generated_at: str = "2026-05-07T00:00:00Z",
) -> dict:
    """Return a minimal valid DomainResult dict.

    Required fields with no defaults: domain_slug, analysis_version,
    models, free_lists, mds_coordinates, mds_uncertainty,
    similarity_matrix, similarity_ci, consensus_score, consensus_ci,
    generated_lede, generated_at.
    """
    if model_ids is None:
        model_ids = ["test-model-a", "test-model-b"]

    n = len(model_ids)
    models = [
        {**_model_ref(), "model_id": mid} for mid in model_ids
    ]
    free_lists = {
        mid: _free_list(mid, slug) for mid in model_ids
    }
    mds_coordinates = {mid: [float(i), 0.0] for i, mid in enumerate(model_ids)}
    mds_uncertainty = {mid: _bootstrap_ellipse() for mid in model_ids}
    similarity_matrix = [[1.0 if i == j else 0.5 for j in range(n)] for i in range(n)]
    similarity_ci = [
        [
            [0.4, 0.6] if i != j else [1.0, 1.0]
            for j in range(n)
        ]
        for i in range(n)
    ]

    return {
        "domain_slug": slug,
        "analysis_version": analysis_version,
        "models": models,
        "free_lists": free_lists,
        "mds_coordinates": mds_coordinates,
        "mds_uncertainty": mds_uncertainty,
        "similarity_matrix": similarity_matrix,
        "similarity_ci": similarity_ci,
        "consensus_score": 6.0,
        "consensus_ci": [4.0, 8.0],
        "generated_lede": "",
        "generated_at": generated_at,
    }


def _write_domain(
    results_dir: Path,
    slug: str,
    version: str,
    domain_dict: dict | None = None,
) -> Path:
    """Write a domain JSON file; returns the file path."""
    domain_dir = results_dir / slug
    domain_dir.mkdir(parents=True, exist_ok=True)
    payload = domain_dict if domain_dict is not None else _minimal_domain_result(
        slug=slug, analysis_version=version
    )
    path = domain_dir / f"{version}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Test 1 — minimal synthetic fixture
# ---------------------------------------------------------------------------

def test_build_single_domain(tmp_path: Path) -> None:
    """build() with one domain produces a manifest with that domain's fields."""
    results_dir = tmp_path / "results"
    output_dir = tmp_path / "output"

    _write_domain(results_dir, slug="widgets", version="0.2")

    manifest = build(results_dir, output_dir)

    assert isinstance(manifest, Manifest)
    assert len(manifest.domains) == 1

    domain = manifest.domains[0]
    assert domain.slug == "widgets"
    assert domain.analysis_version == "0.2"
    assert domain.n_models == 2
    assert domain.model_ids == ["test-model-a", "test-model-b"]
    assert isinstance(domain.generated_at, datetime)

    # manifest.json must exist on disk
    manifest_path = output_dir / "manifest.json"
    assert manifest_path.exists()

    on_disk = json.loads(manifest_path.read_text())
    assert on_disk["domains"][0]["slug"] == "widgets"
    assert on_disk["domains"][0]["n_models"] == 2
    assert on_disk["domains"][0]["model_ids"] == ["test-model-a", "test-model-b"]


# ---------------------------------------------------------------------------
# Test 2 — empty results dir produces Manifest with domains: []
# ---------------------------------------------------------------------------

def test_build_empty_results_dir(tmp_path: Path) -> None:
    """build() on an empty results dir produces a manifest with no domains."""
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    output_dir = tmp_path / "output"

    manifest = build(results_dir, output_dir)

    assert manifest.domains == []

    on_disk = json.loads((output_dir / "manifest.json").read_text())
    assert on_disk["domains"] == []


# ---------------------------------------------------------------------------
# Test 3 — multi-version selection: latest semver wins
# ---------------------------------------------------------------------------

def test_build_selects_latest_version(tmp_path: Path) -> None:
    """build() selects the latest version when multiple .json files exist.

    Version-selection rule: lexicographic comparison of the semver stem.
    '0.2' > '0.1' lexicographically; build() must read 0.2.json and
    report analysis_version '0.2'. Earlier versions are silently ignored.
    """
    results_dir = tmp_path / "results"
    output_dir = tmp_path / "output"

    # Write two versions for the same domain
    _write_domain(results_dir, slug="widgets", version="0.1",
                  domain_dict=_minimal_domain_result(slug="widgets", analysis_version="0.1"))
    _write_domain(results_dir, slug="widgets", version="0.2",
                  domain_dict=_minimal_domain_result(slug="widgets", analysis_version="0.2"))

    manifest = build(results_dir, output_dir)

    assert len(manifest.domains) == 1
    assert manifest.domains[0].analysis_version == "0.2"


# ---------------------------------------------------------------------------
# Test 4 — invalid JSON raises DomainValidationError with offending path
# ---------------------------------------------------------------------------

def test_build_invalid_json_raises(tmp_path: Path) -> None:
    """build() raises DomainValidationError when a domain JSON is invalid.

    The exception message must contain the path to the offending file so
    callers (scripts/publish.py) can report it on stderr.
    """
    results_dir = tmp_path / "results"
    output_dir = tmp_path / "output"

    # Write a structurally invalid domain result (missing required fields)
    bad_dir = results_dir / "broken"
    bad_dir.mkdir(parents=True)
    bad_path = bad_dir / "0.2.json"
    bad_path.write_text(json.dumps({"domain_slug": "broken"}), encoding="utf-8")

    with pytest.raises(DomainValidationError) as exc_info:
        build(results_dir, output_dir)

    err = exc_info.value
    assert err.path == bad_path
    assert isinstance(err.cause, ValidationError)
    assert "broken" in str(err)


# ---------------------------------------------------------------------------
# Test 5 — deterministic output (modulo built_at)
# ---------------------------------------------------------------------------

def test_build_deterministic(tmp_path: Path) -> None:
    """build() produces byte-identical manifest.json when called twice.

    The built_at field is wallclock and will differ between calls, so we
    mock datetime.now() to return a fixed value for both runs. Every other
    field must be byte-identical.
    """
    results_dir = tmp_path / "results"
    output_dir_a = tmp_path / "output_a"
    output_dir_b = tmp_path / "output_b"

    _write_domain(results_dir, slug="widgets", version="0.2")

    fixed_time = datetime(2026, 5, 9, 12, 0, 0, tzinfo=timezone.utc)

    with patch("cdb_publish.build.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_time
        manifest_a = build(results_dir, output_dir_a)

    with patch("cdb_publish.build.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_time
        manifest_b = build(results_dir, output_dir_b)

    text_a = (output_dir_a / "manifest.json").read_text()
    text_b = (output_dir_b / "manifest.json").read_text()

    assert text_a == text_b, (
        "manifest.json is not deterministic: content differs between two identical calls"
    )
    assert manifest_a.model_dump() == manifest_b.model_dump()
