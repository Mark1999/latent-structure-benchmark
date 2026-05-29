"""Integration tests for the extended cdb_publish.build — domain JSON writer.

No real API calls. Tests use synthetic DomainResult fixtures and the actual
data/results/ corpus for the real-corpus smoke tests.
See CLAUDE.md §6 R9 (no real API in tests).

Test plan (8 tests):
  1. Synthetic → published {slug}.json has non-empty generated_lede.
  2. Synthetic → published has display.r1_states keyed by every mds_coordinates model.
  3. Synthetic → published has display.top_terms keyed by every model with sutrop_csi.
  4. Synthetic → display.top_terms_metric == "sutrop_csi".
  5. Synthetic → both {slug}.json and {slug}.v{version}.json exist and are byte-identical.
  6. Manifest carries oci_low_concentration_threshold == 3.0.
  7. Append-only invariant: SHA256 of source data/results/{domain}/0.2.json is unchanged.
  8. Real-corpus smoke: build() against actual data/results/ yields non-empty ledes
     and the correct model counts (15 family, 14 holidays) in r1_states.

See docs/status/2026-05-09-phase5-architect-plan.md §4 T3.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from cdb_publish.build import build
from cdb_publish.lede import OCI_LOW_CONCENTRATION_THRESHOLD

# ---------------------------------------------------------------------------
# Paths to real corpus files
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).parent.parent.parent
_RESULTS_DIR = _REPO_ROOT / "data" / "results"


# ---------------------------------------------------------------------------
# Fixture helpers (shared with test_build.py style)
# ---------------------------------------------------------------------------

def _model_ref(model_id: str = "test-model-a") -> dict:
    return {
        "provider": "anthropic",
        "model_id": model_id,
        "family": "test",
        "origin": "us",
        "open_weights": False,
        "collection_method": "anthropic_api",
        "quantization": None,
        "release_date": "2026-01-01",
        "version_label": model_id,
        "source_notes": "",
    }


def _free_list(model_id: str, domain_slug: str) -> dict:
    return {
        "run_id": f"run-{model_id}",
        "model": {**_model_ref(), "model_id": model_id},
        "domain_slug": domain_slug,
        "items": ["alpha", "beta"],
        "raw_order": ["alpha", "beta"],
    }


def _bootstrap_ellipse() -> dict:
    return {
        "center": [0.0, 0.0],
        "semi_major": 0.1,
        "semi_minor": 0.05,
        "rotation_rad": 0.0,
        "n_bootstrap": 100,
    }


def _within_model_result(
    model_id: str,
    oci: float = 10.0,
    deterministic_output: bool = False,
) -> dict:
    return {
        "model_id": model_id,
        "n_runs": 5,
        "oci": oci,
        "deterministic_output": deterministic_output,
    }


def _sutrop_csi_entry(item: str, csi: float) -> dict:
    f_mentions = 3
    n_runs = 5
    mean_position = f_mentions / (n_runs * csi) if csi > 0 else 1.0
    return {
        "item": item,
        "csi": csi,
        "f_mentions": f_mentions,
        "n_runs": n_runs,
        "mean_position": mean_position,
    }


def _minimal_domain_result(
    slug: str = "test-domain",
    analysis_version: str = "0.2",
    model_ids: list[str] | None = None,
    consensus_type: str = "STRONG_CONSENSUS",
    consensus_score: float = 6.0,
    within_model_oci: dict[str, float] | None = None,
    include_sutrop_csi: bool = True,
    generated_at: str = "2026-05-09T00:00:00Z",
) -> dict:
    """Return a minimal valid DomainResult dict with optional sutrop_csi."""
    if model_ids is None:
        model_ids = ["test-model-a", "test-model-b"]

    if within_model_oci is None:
        within_model_oci = {mid: 10.0 for mid in model_ids}

    n = len(model_ids)
    models = [{**_model_ref(), "model_id": mid} for mid in model_ids]
    free_lists = {mid: _free_list(mid, slug) for mid in model_ids}
    mds_coordinates = {mid: [float(i), 0.0] for i, mid in enumerate(model_ids)}
    mds_uncertainty = {mid: _bootstrap_ellipse() for mid in model_ids}
    similarity_matrix = [
        [1.0 if i == j else 0.5 for j in range(n)] for i in range(n)
    ]
    similarity_ci = [
        [[0.4, 0.6] if i != j else [1.0, 1.0] for j in range(n)]
        for i in range(n)
    ]
    within_model_results = [
        _within_model_result(mid, oci=within_model_oci.get(mid, 10.0))
        for mid in model_ids
    ]

    result: dict = {
        "domain_slug": slug,
        "analysis_version": analysis_version,
        "models": models,
        "free_lists": free_lists,
        "mds_coordinates": mds_coordinates,
        "mds_uncertainty": mds_uncertainty,
        "similarity_matrix": similarity_matrix,
        "similarity_ci": similarity_ci,
        "consensus_score": consensus_score,
        "consensus_ci": [4.0, 8.0],
        "consensus_type": consensus_type,
        "within_model_results": within_model_results,
        "generated_lede": "",
        "generated_at": generated_at,
    }

    if include_sutrop_csi:
        # Add a synthetic sutrop_csi entry per model so top_terms is populated.
        result["sutrop_csi"] = {
            mid: [
                _sutrop_csi_entry("alpha", 0.9),
                _sutrop_csi_entry("beta",  0.7),
                _sutrop_csi_entry("gamma", 0.5),
            ]
            for mid in model_ids
        }

    return result


def _write_domain(
    results_dir: Path,
    slug: str,
    version: str,
    domain_dict: dict | None = None,
) -> Path:
    domain_dir = results_dir / slug
    domain_dir.mkdir(parents=True, exist_ok=True)
    payload = domain_dict if domain_dict is not None else _minimal_domain_result(
        slug=slug, analysis_version=version
    )
    path = domain_dir / f"{version}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Test 1 — published {slug}.json has non-empty generated_lede
# ---------------------------------------------------------------------------

def test_published_json_has_nonempty_lede(tmp_path: Path) -> None:
    """build() injects a non-empty generated_lede into the published domain JSON."""
    results_dir = tmp_path / "results"
    output_dir = tmp_path / "output"
    _write_domain(results_dir, slug="test-domain", version="0.2")

    build(results_dir, output_dir)

    published = json.loads((output_dir / "test-domain.json").read_text())
    lede = published.get("generated_lede", "")
    assert isinstance(lede, str)
    assert len(lede) > 0, "generated_lede must be non-empty after build()"


# ---------------------------------------------------------------------------
# Test 2 — display.r1_states keyed by every mds_coordinates model
# ---------------------------------------------------------------------------

def test_display_r1_states_keyed_by_all_mds_models(tmp_path: Path) -> None:
    """display.r1_states contains an entry for every model in mds_coordinates."""
    results_dir = tmp_path / "results"
    output_dir = tmp_path / "output"
    model_ids = ["model-x", "model-y", "model-z"]
    domain_dict = _minimal_domain_result(slug="widgets", model_ids=model_ids)
    _write_domain(results_dir, slug="widgets", version="0.2", domain_dict=domain_dict)

    build(results_dir, output_dir)

    published = json.loads((output_dir / "widgets.json").read_text())
    r1_states = published.get("display", {}).get("r1_states", {})
    assert set(r1_states.keys()) == set(model_ids), (
        f"r1_states keys {set(r1_states.keys())} != mds model ids {set(model_ids)}"
    )
    # All r1_state values must be valid strings
    valid_states = {"typical_concentration", "low_concentration", "deterministic"}
    for mid, state in r1_states.items():
        assert state in valid_states, f"Invalid r1_state {state!r} for model {mid}"


# ---------------------------------------------------------------------------
# Test 3 — display.top_terms keyed by every model with sutrop_csi entries
# ---------------------------------------------------------------------------

def test_display_top_terms_keyed_by_sutrop_csi_models(tmp_path: Path) -> None:
    """display.top_terms contains entries for models that have sutrop_csi data."""
    results_dir = tmp_path / "results"
    output_dir = tmp_path / "output"
    model_ids = ["model-a", "model-b"]
    domain_dict = _minimal_domain_result(
        slug="widgets", model_ids=model_ids, include_sutrop_csi=True
    )
    _write_domain(results_dir, slug="widgets", version="0.2", domain_dict=domain_dict)

    build(results_dir, output_dir)

    published = json.loads((output_dir / "widgets.json").read_text())
    top_terms = published.get("display", {}).get("top_terms", {})
    assert set(top_terms.keys()) == set(model_ids)
    for _mid, terms in top_terms.items():
        assert isinstance(terms, list)
        assert len(terms) > 0


# ---------------------------------------------------------------------------
# Test 4 — display.top_terms_metric == "sutrop_csi"
# ---------------------------------------------------------------------------

def test_display_top_terms_metric_is_sutrop_csi(tmp_path: Path) -> None:
    """display.top_terms_metric must equal 'sutrop_csi' (Q4 binding)."""
    results_dir = tmp_path / "results"
    output_dir = tmp_path / "output"
    _write_domain(results_dir, slug="test-domain", version="0.2")

    build(results_dir, output_dir)

    published = json.loads((output_dir / "test-domain.json").read_text())
    metric = published.get("display", {}).get("top_terms_metric")
    assert metric == "sutrop_csi", (
        f"display.top_terms_metric must be 'sutrop_csi', got {metric!r}"
    )


# ---------------------------------------------------------------------------
# Test 5 — both {slug}.json and {slug}.v{version}.json exist and are byte-identical
# ---------------------------------------------------------------------------

def test_versioned_and_unversioned_files_byte_identical(tmp_path: Path) -> None:
    """build() writes both {slug}.json and {slug}.v{version}.json with identical content."""
    results_dir = tmp_path / "results"
    output_dir = tmp_path / "output"
    _write_domain(results_dir, slug="widgets", version="0.2")

    build(results_dir, output_dir)

    unversioned = output_dir / "widgets.json"
    versioned = output_dir / "widgets.v0.2.json"

    assert unversioned.exists(), "widgets.json not found"
    assert versioned.exists(), "widgets.v0.2.json not found"

    content_unversioned = unversioned.read_text(encoding="utf-8")
    content_versioned = versioned.read_text(encoding="utf-8")
    assert content_unversioned == content_versioned, (
        "{slug}.json and {slug}.v{version}.json must be byte-identical"
    )


# ---------------------------------------------------------------------------
# Test 6 — manifest carries oci_low_concentration_threshold == 3.0
# ---------------------------------------------------------------------------

def test_manifest_carries_oci_threshold(tmp_path: Path) -> None:
    """manifest.json must carry oci_low_concentration_threshold == 3.0."""
    results_dir = tmp_path / "results"
    output_dir = tmp_path / "output"
    _write_domain(results_dir, slug="test-domain", version="0.2")

    manifest = build(results_dir, output_dir)

    assert manifest.oci_low_concentration_threshold == OCI_LOW_CONCENTRATION_THRESHOLD

    on_disk = json.loads((output_dir / "manifest.json").read_text())
    assert on_disk.get("oci_low_concentration_threshold") == 3.0, (
        f"manifest.oci_low_concentration_threshold must be 3.0, "
        f"got {on_disk.get('oci_low_concentration_threshold')!r}"
    )


# ---------------------------------------------------------------------------
# Test 7 — Append-only invariant: source files are byte-identical before/after
# ---------------------------------------------------------------------------

def test_source_files_byte_identical_after_build(tmp_path: Path) -> None:
    """build() must not modify source data/results/ files.

    SHA256 of each source file before and after build() must match.
    This is acceptance criterion 6 from the T3 plan.
    """
    if not _RESULTS_DIR.exists():
        pytest.skip("data/results/ not present in this environment")

    family_file = _RESULTS_DIR / "family" / "0.2.json"
    holidays_file = _RESULTS_DIR / "holidays" / "0.2.json"

    if not family_file.exists() or not holidays_file.exists():
        pytest.skip("data/results/family/0.2.json or holidays/0.2.json not present")

    sha_before_family = _sha256(family_file)
    sha_before_holidays = _sha256(holidays_file)

    output_dir = tmp_path / "output"
    build(_RESULTS_DIR, output_dir)

    sha_after_family = _sha256(family_file)
    sha_after_holidays = _sha256(holidays_file)

    assert sha_before_family == sha_after_family, (
        "data/results/family/0.2.json was modified by build() — "
        "source files must be read-only"
    )
    assert sha_before_holidays == sha_after_holidays, (
        "data/results/holidays/0.2.json was modified by build() — "
        "source files must be read-only"
    )


# ---------------------------------------------------------------------------
# Test 8 — Real-corpus smoke: family (11 models) and holidays (9 models)
# ---------------------------------------------------------------------------

def test_real_corpus_smoke(tmp_path: Path) -> None:
    """build() against actual data/results/ produces correct outputs.

    Asserts per acceptance criteria 1–5:
    - Both family and holidays JSON files are written (versioned + unversioned).
    - Both have non-empty generated_lede.
    - family has 15 models in r1_states; holidays has 14.
    - manifest carries oci_low_concentration_threshold == 3.0.

    NOTE: model counts reflect the current corpus as of the 15-model family /
    14-model holidays re-analysis (analysis_version 0.3).  T4's planned
    re-baseline will change these counts again and update these assertions.
    """
    if not _RESULTS_DIR.exists():
        pytest.skip("data/results/ not present in this environment")

    family_file = _RESULTS_DIR / "family" / "0.3.json"
    holidays_file = _RESULTS_DIR / "holidays" / "0.3.json"
    if not family_file.exists() or not holidays_file.exists():
        pytest.skip("data/results/family/0.3.json or holidays/0.3.json not present")

    output_dir = tmp_path / "output"
    manifest = build(_RESULTS_DIR, output_dir)

    # --- File existence ---
    for slug, version in [("family", "0.3"), ("holidays", "0.3")]:
        assert (output_dir / f"{slug}.json").exists(), f"{slug}.json not found"
        assert (output_dir / f"{slug}.v{version}.json").exists(), (
            f"{slug}.v{version}.json not found"
        )
    assert (output_dir / "manifest.json").exists()

    # --- Non-empty lede ---
    for slug in ("family", "holidays"):
        data = json.loads((output_dir / f"{slug}.json").read_text())
        lede = data.get("generated_lede", "")
        assert len(lede) > 0, f"{slug}: generated_lede must be non-empty"

    # --- r1_states model counts (acceptance criterion 4) ---
    # Current corpus: family=15 models (analysis_version 0.3),
    # holidays=14 models (analysis_version 0.3).
    # T4's re-baseline will update these values.
    family_data = json.loads((output_dir / "family.json").read_text())
    family_r1 = family_data.get("display", {}).get("r1_states", {})
    assert len(family_r1) == 15, (
        f"family: expected 15 models in r1_states, got {len(family_r1)}"
    )

    holidays_data = json.loads((output_dir / "holidays.json").read_text())
    holidays_r1 = holidays_data.get("display", {}).get("r1_states", {})
    assert len(holidays_r1) == 14, (
        f"holidays: expected 14 models in r1_states, got {len(holidays_r1)}"
    )

    # --- manifest threshold (acceptance criterion 5) ---
    assert manifest.oci_low_concentration_threshold == 3.0
    on_disk_manifest = json.loads((output_dir / "manifest.json").read_text())
    assert on_disk_manifest["oci_low_concentration_threshold"] == 3.0

    # --- top_terms_metric (acceptance criterion 3) ---
    for slug in ("family", "holidays"):
        data = json.loads((output_dir / f"{slug}.json").read_text())
        metric = data.get("display", {}).get("top_terms_metric")
        assert metric == "sutrop_csi", (
            f"{slug}: display.top_terms_metric must be 'sutrop_csi', got {metric!r}"
        )


# ---------------------------------------------------------------------------
# Gap-fill 3 — _compute_display fallback: model in mds_coordinates with no
#              within_model_results entry defaults to "typical_concentration"
# ---------------------------------------------------------------------------

def test_display_r1_states_fallback_for_missing_within_model_result(
    tmp_path: Path,
) -> None:
    """display.r1_states falls back to 'typical_concentration' for models
    that are present in mds_coordinates but absent from within_model_results.

    The build.py comment documents: 'Conservative fallback: no
    within_model_result → treat as typical'. This test makes that fallback
    machine-verifiable.
    """
    results_dir = tmp_path / "results"
    output_dir = tmp_path / "output"

    # Build a domain where one model is in mds_coordinates but NOT in
    # within_model_results.
    domain_dict = _minimal_domain_result(
        slug="widgets",
        model_ids=["model-a", "model-b"],
    )
    # Remove model-b from within_model_results so only model-a has an entry.
    domain_dict["within_model_results"] = [
        wr for wr in domain_dict["within_model_results"]
        if wr["model_id"] == "model-a"
    ]
    _write_domain(results_dir, slug="widgets", version="0.2", domain_dict=domain_dict)

    build(results_dir, output_dir)

    published = json.loads((output_dir / "widgets.json").read_text())
    r1_states = published.get("display", {}).get("r1_states", {})

    # Both models must appear in r1_states.
    assert "model-a" in r1_states
    assert "model-b" in r1_states

    # model-b has no within_model_result; must fall back to typical_concentration.
    assert r1_states["model-b"] == "typical_concentration", (
        f"Expected fallback 'typical_concentration' for model-b, got {r1_states['model-b']!r}"
    )


# ---------------------------------------------------------------------------
# Gap-fill 4 — _compute_display: model with mds_coordinates but no sutrop_csi
#              entry is absent from display.top_terms (not an error, not a
#              zero-length entry — it is simply omitted)
# ---------------------------------------------------------------------------

def test_display_top_terms_absent_when_no_sutrop_csi(tmp_path: Path) -> None:
    """display.top_terms omits models that have no sutrop_csi entries.

    When include_sutrop_csi=False, the DomainResult carries no sutrop_csi
    data at all. The published JSON should have top_terms == {} (empty) and
    must not raise.
    """
    results_dir = tmp_path / "results"
    output_dir = tmp_path / "output"

    domain_dict = _minimal_domain_result(
        slug="widgets",
        model_ids=["model-a", "model-b"],
        include_sutrop_csi=False,
    )
    _write_domain(results_dir, slug="widgets", version="0.2", domain_dict=domain_dict)

    build(results_dir, output_dir)

    published = json.loads((output_dir / "widgets.json").read_text())
    top_terms = published.get("display", {}).get("top_terms", {})

    # No models have sutrop_csi data; top_terms must be empty, not an error.
    assert top_terms == {}, (
        f"Expected empty top_terms when no sutrop_csi present, got {top_terms!r}"
    )
