"""Campaign planner helper for the LSB ops console.

Pure functions only. No subprocess, no Flask, no LLM imports.

Computes per-cell shortfall from informants.jsonl, reads domain YAML files,
reads the model registry, and renders a human-readable plan that mirrors the
layout of logs/collect-batchA-20260710/resume-plan.txt.

See the Architect plan (docs/status/2026-07-10-ops-console-panels123-architect-plan.md)
T1 for function surface and acceptance criteria.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

# Sentinel returned by compute_shortfall when a domain slug is not in the
# known-domains set. The route layer (T2) uses this to show the new-domain
# prompt-drafting notice instead of producing a run plan.
NEW_DOMAIN_SENTINEL: str = "__new_domain__"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DomainInfo:
    """Minimal domain metadata derived from a v1 YAML file."""

    slug: str
    display_name: str


@dataclass(frozen=True)
class ModelInfo:
    """Minimal model metadata derived from the registry."""

    model_id: str
    display_name: str
    family: str
    records: int  # total records stored in the registry for this model


@dataclass
class CellShortfall:
    """Shortfall for one (model, domain) cell."""

    model_id: str
    domain_slug: str
    passed: int  # qa_passed=True records currently in informants.jsonl
    needed: int  # max(0, runs_per_cell - passed)


@dataclass
class CampaignPlan:
    """Full campaign plan produced by compute_shortfall."""

    campaign_id: str
    models: list[ModelInfo]
    domain_slugs: list[str]
    runs_per_cell: int
    cells: list[CellShortfall]  # all (model, domain) combinations; needed may be 0


# ---------------------------------------------------------------------------
# Domain discovery
# ---------------------------------------------------------------------------


def list_domains(domains_path: Path) -> list[DomainInfo]:
    """Return domain info from YAML files in domains_path.

    domains_path is typically data/domains/v1/. Returns an empty list if
    the directory does not exist or contains no YAML files.

    Only reads slug and display_name; other fields are ignored.
    """
    if not domains_path.exists():
        return []

    result: list[DomainInfo] = []
    for yaml_file in sorted(domains_path.glob("*.yaml")):
        try:
            raw: Any = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(raw, dict):
            continue
        slug: str = raw.get("slug", yaml_file.stem)
        display_name: str = raw.get("display_name", slug)
        result.append(DomainInfo(slug=slug, display_name=display_name))

    return result


# ---------------------------------------------------------------------------
# Model registry
# ---------------------------------------------------------------------------


def list_models(registry_path: Path) -> list[ModelInfo]:
    """Return model info from registry.json.

    Returns an empty list if the registry does not exist or cannot be parsed.
    Registry entries that are missing model_id are skipped.
    """
    if not registry_path.exists():
        return []

    try:
        raw: Any = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception:
        return []

    if not isinstance(raw, dict):
        return []

    result: list[ModelInfo] = []
    for entry in raw.get("models", []):
        if not isinstance(entry, dict):
            continue
        model_id: str = entry.get("model_id", "")
        if not model_id:
            continue
        result.append(
            ModelInfo(
                model_id=model_id,
                display_name=entry.get("display_name", model_id),
                family=entry.get("family", ""),
                records=int(entry.get("records", 0)),
            )
        )

    return result


# ---------------------------------------------------------------------------
# Shortfall computation
# ---------------------------------------------------------------------------


def compute_shortfall(
    informants_path: Path,
    models: list[ModelInfo],
    domain_slugs: list[str],
    runs_per_cell: int,
    *,
    known_slugs: set[str] | None = None,
    campaign_id: str = "",
) -> CampaignPlan | str:
    """Compute per-cell shortfall from informants.jsonl.

    For each (model, domain) cell:
        passed = count of qa_passed=True records in informants.jsonl
        needed = max(0, runs_per_cell - passed)

    Args:
        informants_path: Path to data/raw/informants.jsonl (may be absent or empty).
        models: ModelInfo list from list_models().
        domain_slugs: Domain slugs to plan; may include a free-text new-domain slug.
        runs_per_cell: Target number of passing runs per (model, domain) cell.
        known_slugs: Set of domain slugs present on disk. When provided, any slug
            in domain_slugs that is not in known_slugs causes this function to
            return NEW_DOMAIN_SENTINEL immediately (no plan produced).
        campaign_id: Optional campaign identifier to embed in the plan.

    Returns:
        CampaignPlan on success, or NEW_DOMAIN_SENTINEL (str) if any domain
        slug is unrecognised.
    """
    # Guard: new-domain check runs before reading the JSONL
    if known_slugs is not None:
        for slug in domain_slugs:
            if slug not in known_slugs:
                return NEW_DOMAIN_SENTINEL

    # Count qa_passed=True records per (model_id, domain_slug)
    passed_counts: dict[tuple[str, str], int] = {}

    if informants_path.exists():
        try:
            text = informants_path.read_text(encoding="utf-8")
        except OSError:
            text = ""

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
            if not rec.get("qa_passed", False):
                continue
            mid: str = rec.get("model_id", "")
            dom: str = rec.get("domain_slug", "")
            if mid and dom:
                key = (mid, dom)
                passed_counts[key] = passed_counts.get(key, 0) + 1

    cells: list[CellShortfall] = []
    for m in models:
        for slug in domain_slugs:
            passed = passed_counts.get((m.model_id, slug), 0)
            needed = max(0, runs_per_cell - passed)
            cells.append(
                CellShortfall(
                    model_id=m.model_id,
                    domain_slug=slug,
                    passed=passed,
                    needed=needed,
                )
            )

    return CampaignPlan(
        campaign_id=campaign_id,
        models=list(models),
        domain_slugs=list(domain_slugs),
        runs_per_cell=runs_per_cell,
        cells=cells,
    )


# ---------------------------------------------------------------------------
# Plan text renderer
# ---------------------------------------------------------------------------


def render_plan_text(plan: CampaignPlan) -> str:
    """Render the plan as text matching the resume-plan.txt layout.

    Each output line has the form:
        model_id domain_slug needed

    Only cells where needed > 0 are included. Returns an empty string if
    there is no work to do.
    """
    lines: list[str] = []
    for cell in plan.cells:
        if cell.needed > 0:
            lines.append(f"{cell.model_id} {cell.domain_slug} {cell.needed}")

    return "\n".join(lines) + ("\n" if lines else "")
