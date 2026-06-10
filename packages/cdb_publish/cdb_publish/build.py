"""Build static JSON files for the dashboard. See ARCHITECTURE.md §4.4.

Entry point: build(results_dir, output_dir) -> Manifest

Reads data/results/{domain}/{version}.json, validates each file against
cdb_core.schemas.DomainResult, injects a lede via cdb_publish.lede,
computes display-derived fields (r1_states, top_terms), and writes:
  - output_dir/{slug}.json            — unversioned canonical (latest version)
  - output_dir/{slug}.v{version}.json — explicit-version copy
  - output_dir/{slug}-cooccurrence.json — per-model co-occurrence matrices
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
import logging
from datetime import UTC, datetime
from pathlib import Path

from cdb_analyze.cooccurrence import build_cooccurrence_matrix
from cdb_analyze.pipeline import group_by_model, load_records
from cdb_core.schemas import DomainResult, SutropCSI
from pydantic import ValidationError

from cdb_publish.derived import TOP_TERMS_METRIC, r1_state_for, top_freelist_terms
from cdb_publish.failures import build_failures
from cdb_publish.lede import generate_lede
from cdb_publish.schemas.manifest import Manifest, ManifestDomain
from cdb_publish.successes import build_record_details, build_successes

logger = logging.getLogger(__name__)


def _build_domain_cooccurrence(
    slug: str,
    term_mds_items: list[str],
    raw_informants_path: Path,
    output_dir: Path,
) -> None:
    """Build and write {slug}-cooccurrence.json for the TermMap browser component.

    Computes per-model co-occurrence matrices aligned to the published
    ``term_mds_items`` item set (the same 100-or-so items used for the pooled
    term MDS).  The output shape matches ``CooccurrenceData`` in TermMap.tsx:

        { "items": string[], "models": { model_id: number[][] } }

    where ``models[model_id]`` is an N×N matrix of co-occurrence fractions in
    [0, 1] aligned to the ``items`` list.  Items absent from a model's pile-sort
    vocabulary receive 0.0 for all cells in that model's row/column — consistent
    with the equal-weight-per-model pooling posture (CDA SME M1).

    The matrix values are rounded to 4 decimal places to match the precision of
    the original family-cooccurrence.json (verified equivalent to the full-float
    output by semantic-equivalence check at generation time).

    Writes output_dir/{slug}-cooccurrence.json.  Silently skips if
    term_mds_items is empty or raw_informants_path does not exist.

    No LLM calls.  Reuses cdb_analyze.cooccurrence.build_cooccurrence_matrix
    and cdb_analyze.pipeline.load_records / group_by_model — the same functions
    used by the analysis pipeline to produce term_mds_* fields.
    """
    if not term_mds_items:
        logger.warning("_build_domain_cooccurrence: %s has empty term_mds_items; skipping", slug)
        return
    if not raw_informants_path.exists():
        logger.warning(
            "_build_domain_cooccurrence: informants file not found at %s; skipping %s",
            raw_informants_path, slug,
        )
        return

    records = load_records(raw_informants_path, slug, qa_only=True)
    if not records:
        logger.warning("_build_domain_cooccurrence: no QA-passed records for %s; skipping", slug)
        return

    groups = group_by_model(records)
    n = len(term_mds_items)

    models_out: dict[str, list[list[float]]] = {}
    for model_id, recs in sorted(groups.items()):
        per_model_mat = build_cooccurrence_matrix(recs)
        local_idx = {item: i for i, item in enumerate(per_model_mat.items)}

        aligned: list[list[float]] = [[0.0] * n for _ in range(n)]
        for i_global, item_i in enumerate(term_mds_items):
            for j_global, item_j in enumerate(term_mds_items):
                i_local = local_idx.get(item_i)
                j_local = local_idx.get(item_j)
                if i_local is not None and j_local is not None:
                    aligned[i_global][j_global] = round(
                        per_model_mat.matrix[i_local][j_local], 4
                    )
        models_out[model_id] = aligned

    cooc_data = {"items": term_mds_items, "models": models_out}
    out_path = output_dir / f"{slug}-cooccurrence.json"
    out_path.write_text(json.dumps(cooc_data, separators=(",", ":")), encoding="utf-8")
    logger.info(
        "_build_domain_cooccurrence: wrote %s (%d items, %d models)",
        out_path, n, len(models_out),
    )


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
      6. Build per-domain successful-records summary JSON files (CR-T4).
      7. Write manifest.json with oci_low_concentration_threshold = 3.0 and
         the failures map from step 5 and the records map from step 6.

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

        # Write {slug}-cooccurrence.json for the TermMap browser component.
        # Uses term_mds_items from the DomainResult (the truncated item set
        # that was used to compute the published term MDS coordinates).
        _build_domain_cooccurrence(
            slug=slug,
            term_mds_items=list(domain_result.term_mds_items),
            raw_informants_path=raw_informants_path,
            output_dir=output_dir,
        )

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

    # Build per-domain successful-records summary JSON files (CR-T4).
    # Every domain slug gets a file; empty-domain files have by_model: [].
    # "Successful" means the LSB pipeline parsed a primary-step response,
    # not a quality judgment on the model output.
    records_map = build_successes(
        raw_informants_path=raw_informants_path,
        output_dir=output_dir / "records",
        domain_slugs=domain_slugs,
    )

    # Build per-record detail JSON files (CR-T7): verbatim bytes for all
    # three CDA elicitation steps per informant record.
    # Emits {output_dir}/records/{slug}/detail/{informant_id}.json.
    build_record_details(
        raw_informants_path=raw_informants_path,
        output_dir=output_dir / "records",
        domain_slugs=domain_slugs,
    )

    manifest = Manifest(
        built_at=datetime.now(tz=UTC),
        domains=manifest_domains,
        failures=failures_map,
        focus1=focus1_map,
        records=records_map,
    )

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        manifest.model_dump_json(indent=2),
        encoding="utf-8",
    )

    return manifest
