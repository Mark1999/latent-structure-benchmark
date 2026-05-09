"""Build static JSON files for the dashboard. See ARCHITECTURE.md §4.4.

Entry point: build(results_dir, output_dir) -> Manifest

Reads data/results/{domain}/{version}.json, validates each file against
cdb_core.schemas.DomainResult, and writes output_dir/manifest.json.

Version selection: when a domain directory contains multiple semver JSON
files (e.g. 0.1.json and 0.2.json), the latest version is selected by
lexicographic comparison of the semver string. Lexicographic ordering is
correct for the semver values LSB uses because the major component is
always 0 and the minor component is a small integer (0-9 for foreseeable
future versions). If versions grow beyond single digits in any component,
this selection logic must be upgraded to packaging.version.Version.

This module does NOT copy domain JSON files to apps/dashboard/public/data/
-- that is T3's scope.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from cdb_core.schemas import DomainResult
from pydantic import ValidationError

from cdb_publish.schemas.manifest import Manifest, ManifestDomain


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


def build(results_dir: Path, output_dir: Path) -> Manifest:
    """Read domain result files, validate, and write manifest.json.

    Parameters
    ----------
    results_dir:
        Directory containing per-domain subdirectories, each holding
        ``{semver}.json`` files (e.g. ``data/results/family/0.2.json``).
    output_dir:
        Directory where ``manifest.json`` will be written. Created if it
        does not exist.

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

    domain_dirs = sorted(
        [d for d in results_dir.iterdir() if d.is_dir()],
        key=lambda d: d.name,
    )

    manifest_domains: list[ManifestDomain] = []

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

        model_ids = sorted(domain_result.mds_coordinates.keys())
        manifest_domains.append(
            ManifestDomain(
                slug=domain_result.domain_slug,
                analysis_version=domain_result.analysis_version,
                n_models=len(model_ids),
                model_ids=model_ids,
                generated_at=domain_result.generated_at,
            )
        )

    manifest = Manifest(
        built_at=datetime.now(tz=UTC),
        domains=manifest_domains,
    )

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        manifest.model_dump_json(indent=2),
        encoding="utf-8",
    )

    return manifest
