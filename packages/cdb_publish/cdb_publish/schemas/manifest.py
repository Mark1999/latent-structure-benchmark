"""Manifest schema for the dashboard data contract.

The manifest.json file is the entry-point the dashboard fetches first.
It lists available domains, their analysis versions, and the model IDs
present in each domain's dataset. See ARCHITECTURE.md §4.4.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from cdb_publish.lede import OCI_LOW_CONCENTRATION_THRESHOLD


class ManifestDomain(BaseModel):
    """Summary record for a single domain in the manifest."""

    slug: str
    """Domain slug, e.g. 'family' or 'holidays'."""

    analysis_version: str
    """Semantic version of the analysis that produced this domain's JSON,
    e.g. '0.2'. Read from the DomainResult.analysis_version field."""

    n_models: int
    """Count of model IDs present in mds_coordinates for this domain."""

    model_ids: list[str]
    """Sorted list of model IDs present in mds_coordinates."""

    generated_at: datetime
    """Timestamp from DomainResult.generated_at (ISO-8601 UTC)."""


class Manifest(BaseModel):
    """Top-level manifest written to output_dir/manifest.json.

    Deterministic: given the same input files the output is identical
    except for the built_at field, which reflects wallclock at invocation.
    """

    built_at: datetime
    """UTC wallclock at the time build() was called."""

    domains: list[ManifestDomain]
    """Available domains, sorted by slug."""

    oci_low_concentration_threshold: float = OCI_LOW_CONCENTRATION_THRESHOLD
    """The OCI threshold that separates R1-a (typical_concentration) from
    R1-b (low_concentration). Published in the manifest so the dashboard's
    apps/dashboard/src/config/analysis.ts can read the canonical value and
    the methodology page can display it. See DESIGN_SYSTEM.md §3.3.5 item 7.
    Source of truth for this value is cdb_publish.lede.OCI_LOW_CONCENTRATION_THRESHOLD.
    """
