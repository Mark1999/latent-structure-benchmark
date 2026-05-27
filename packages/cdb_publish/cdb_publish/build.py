"""Build static JSON files for the dashboard. See ARCHITECTURE.md §4.4.

Entry point: build(results_dir, output_dir) -> Manifest

Reads data/results/{domain}/{version}.json, validates each file against
cdb_core.schemas.DomainResult, injects a lede via cdb_publish.lede,
computes display-derived fields (r1_states, top_terms), and writes:
  - output_dir/{slug}.json            — unversioned canonical (latest version)
  - output_dir/{slug}.v{version}.json — explicit-version copy
  - output_dir/manifest.json          — domain index with threshold constant

Version selection: when a domain directory contains multiple semver JSON
files (e.g. 0.1.json and 0.2.json), the latest version is selected by
lexicographic comparison of the semver string. Lexicographic ordering is
correct for the semver values LSB uses because the major component is
always 0 and the minor component is a small integer (0-9 for foreseeable
future versions). If versions grow beyond single digits in any component,
this selection logic must be upgraded to packaging.version.Version.

Source data/results/ files are read-only — this module MUST NOT write
to results_dir. SHA256 of source files must be byte-identical before
and after build() runs (acceptance criterion 6).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from cdb_core.schemas import DomainResult, SutropCSI
from pydantic import ValidationError

from cdb_publish.derived import TOP_TERMS_METRIC, r1_state_for, top_freelist_terms
from cdb_publish.failures import build_failures
from cdb_publish.lede import generate_lede
from cdb_publish.schemas.manifest import Manifest, ManifestDomain


def _build_focus1(domain_dict: dict, slug: str, output_dir: Path) -> str:
    """Emit {slug}-focus1.json with per-model within-model data.

    Args:
        domain_dict: The already-serialized domain result dict.
        slug: Domain slug.
        output_dir: Output directory for the JSON file.

    Returns the relative path (from dashboard public/) for the manifest.
    """
    centroid_piles = domain_dict.get("centroid_piles", {})
    sutrop_csi = domain_dict.get("sutrop_csi", {})

    focus1_data: dict[str, object] = {}
    for wm in domain_dict.get("within_model_results", []):
        mid = wm["model_id"]
        entry = dict(wm)
        entry["centroid_piles"] = centroid_piles.get(mid)
        entry["sutrop_csi"] = sutrop_csi.get(mid)
        focus1_data[mid] = entry

    focus1_path = output_dir / f"{slug}-focus1.json"
    focus1_path.write_text(json.dumps(focus1_data, indent=2), encoding="utf-8")

    return f"data/{slug}-focus1.json"


class DomainValidationError(ValueError):
    """Raised when a domain JSON file fails DomainResult validation.

    Wraps pydantic.ValidationError and adds the offending file path so
    callers (e.g. scripts/publish.py) can report it clearly.
    """

    def __init__(self, path: Path, cause: ValidationError) -> None:
        self.path = path
        self.cause = cause
        super().__init__(
            f"Validation failed for domain file '{path}': {cause}"
        )


def _select_latest_version(json_files: list[Path]) -> Path:
    """Return the path with the lexicographically greatest semver stem.

    Stems are expected to be semver strings such as '0.1', '0.2'.
    Lexicographic ordering is sufficient for LSB's current versioning
    scheme (major always 0, minor a small integer). See module docstring.
    """
    return max(json_files, key=lambda p: p.stem)


def _compute_display(domain_result: DomainResult) -> dict:
    """Compute the display sub-object for a DomainResult.

    Returns a dict with:
      r1_states: {model_id: r1_state} — keyed by every model in mds_coordinates
      top_terms: {model_id: list[str]} — keyed by models with sutrop_csi entries
      top_terms_metric: "sutrop_csi" — auditable metric name (Q4 binding)

    r1_states draws from within_model_results, joined on model_id.
    Models in mds_coordinates without a within_model_result entry default
    to "typical_concentration" (conservative fallback matching the lede's
    all-deterministic check in lede.py).

    top_terms draws from sutrop_csi, which is keyed by model_id in
    DomainResult. Only models with a non-empty sutrop_csi entry are included.
    """
    # Build a lookup of model_id → WithinModelResult
    wmr_lookup = {wmr.model_id: wmr for wmr in domain_result.within_model_results}

    # r1_states keyed by every model in mds_coordinates
    r1_states: dict[str, str] = {}
    for model_id in domain_result.mds_coordinates:
        wmr = wmr_lookup.get(model_id)
        if wmr is not None:
            r1_states[model_id] = r1_state_for(wmr)
        else:
            # Conservative fallback: no within_model_result → treat as typical
            r1_states[model_id] = "typical_concentration"

    # top_terms keyed by every model with a sutrop_csi entry
    top_terms: dict[str, list[str]] = {}
    for model_id, csi_list in domain_result.sutrop_csi.items():
        # csi_list is list[SutropCSI]; convert to dict[item → SutropCSI]
        # for top_freelist_terms() which expects that shape.
        csi_dict: dict[str, SutropCSI] = {
            entry.item: entry for entry in csi_list
        }
        terms = top_freelist_terms(csi_dict)
        if terms:
            top_terms[model_id] = terms

    return {
        "r1_states": r1_states,
        "top_terms": top_terms,
        "top_terms_metric": TOP_TERMS_METRIC,
    }


def build(
    results_dir: Path,
    output_dir: Path,
    raw_failures_path: Path | None = None,
    raw_decline_interviews_path: Path | None = None,
    raw_informants_path: Path | None = None,
) -> Manifest:
    """Read domain result files, inject ledes, compute display fields, and write output.

    Build flow:
      1. Discover and validate domain JSON files in results_dir (read-only).
      2. For each domain: call generate_lede() and inject into generated_lede.
      3. Compute the display sub-object (r1_states, top_terms, top_terms_metric).
      4. Write {slug}.json and {slug}.v{version}.json to output_dir.
      5. Build failures JSON files per domain (T9 failures-as-findings layer).
      6. Write manifest.json with oci_low_concentration_threshold = 3.0 and
         the failures map from step 5.

    Parameters
    ----------
    results_dir:
        Directory containing per-domain subdirectories, each holding
        ``{semver}.json`` files (e.g. ``data/results/family/0.2.json``).
        These files are treated as read-only: build() does not modify them.
    output_dir:
        Directory where domain JSON files and ``manifest.json`` will be
        written. Created if it does not exist.
    raw_failures_path:
        Path to ``data/raw/failures.jsonl``. Read-only. Defaults to
        ``Path("data/raw/failures.jsonl")`` when None.
    raw_decline_interviews_path:
        Path to ``data/raw/decline_interviews.jsonl``. Read-only. Defaults to
        ``Path("data/raw/decline_interviews.jsonl")`` when None.
    raw_informants_path:
        Path to ``data/raw/informants.jsonl``. Read-only. Defaults to
        ``Path("data/raw/informants.jsonl")`` when None.

    Returns
    -------
    Manifest
        The manifest that was written to disk.

    Raises
    ------
    DomainValidationError
        If any domain JSON file fails validation against DomainResult.
        The error message includes the offending file path.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Apply defaults for raw-data paths (allow callers to override for testing).
    if raw_failures_path is None:
        raw_failures_path = Path("data/raw/failures.jsonl")
    if raw_decline_interviews_path is None:
        raw_decline_interviews_path = Path("data/raw/decline_interviews.jsonl")
    if raw_informants_path is None:
        raw_informants_path = Path("data/raw/informants.jsonl")

    domain_dirs = sorted(
        [d for d in results_dir.iterdir() if d.is_dir()],
        key=lambda d: d.name,
    )

    manifest_domains: list[ManifestDomain] = []
    focus1_map: dict[str, str] = {}

    for domain_dir in domain_dirs:
        json_files = sorted(domain_dir.glob("*.json"))
        if not json_files:
            continue

        latest_file = _select_latest_version(json_files)

        try:
            domain_result = DomainResult.model_validate_json(
                latest_file.read_text(encoding="utf-8")
            )
        except ValidationError as exc:
            raise DomainValidationError(path=latest_file, cause=exc) from exc

        # Inject the lede — overwrites the (typically empty) generated_lede field.
        # model_copy() gives a new Pydantic instance with the field updated.
        lede_text = generate_lede(domain_result)
        domain_result = domain_result.model_copy(
            update={"generated_lede": lede_text}
        )

        # Compute the display sub-object.
        display = _compute_display(domain_result)

        # Serialize the DomainResult to a dict and inject the display sub-object.
        # model_dump() round-trips through Pydantic; inject display before writing.
        domain_dict = json.loads(domain_result.model_dump_json())
        domain_dict["display"] = display

        domain_json_text = json.dumps(domain_dict, indent=2)

        slug = domain_result.domain_slug
        version = domain_result.analysis_version

        # Write {slug}.json (unversioned canonical — latest version content).
        (output_dir / f"{slug}.json").write_text(domain_json_text, encoding="utf-8")

        # Write {slug}.v{version}.json (explicit-version copy — byte-identical).
        (output_dir / f"{slug}.v{version}.json").write_text(
            domain_json_text, encoding="utf-8"
        )

        # Write {slug}-focus1.json (Focus 1: Individual Model Consistency).
        focus1_path = _build_focus1(domain_dict, slug, output_dir)
        focus1_map[slug] = focus1_path

        model_ids = sorted(domain_result.mds_coordinates.keys())
        manifest_domains.append(
            ManifestDomain(
                slug=slug,
                analysis_version=version,
                n_models=len(model_ids),
                model_ids=model_ids,
                generated_at=domain_result.generated_at,
            )
        )

    # Build failures-as-findings JSON files for every domain (T9).
    # Every domain slug gets a file; empty-domain files have records: [].
    domain_slugs = [d.slug for d in manifest_domains]
    failures_map = build_failures(
        raw_failures_path=raw_failures_path,
        raw_decline_interviews_path=raw_decline_interviews_path,
        raw_informants_path=raw_informants_path,
        output_dir=output_dir / "failures",
        domain_slugs=domain_slugs,
    )

    manifest = Manifest(
        built_at=datetime.now(tz=UTC),
        domains=manifest_domains,
        failures=failures_map,
        focus1=focus1_map,
    )

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        manifest.model_dump_json(indent=2),
        encoding="utf-8",
    )

    return manifest
