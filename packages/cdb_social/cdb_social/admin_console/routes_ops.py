"""Ops console blueprint: Panels 1 (New Campaign), 2 (Live Board), 3 (QA).

Routes:
  GET  /ops/campaigns/new              -- Panel 1 form
  POST /ops/campaigns/plan             -- Panel 1 dry-run
  POST /ops/campaigns/launch           -- Panel 1 launch -> redirect to live board
  GET  /ops/live/<campaign_id>         -- Panel 2 live board
  GET  /ops/live/<id>/lane/<m>/tail    -- Panel 2 log tail (last 8 KiB)
  POST /ops/live/<id>/lane/<m>/stop    -- Panel 2 stop lane
  POST /ops/live/<id>/resume           -- Panel 2 resume campaign
  GET  /ops/qa                         -- Panel 3 QA panel

Constraints (Architect plan section 2):
- No LLM imports. No autonomous LLM calls.
- Read-only over data/raw/informants.jsonl.
- No spend text (rule 14). No statistical computation (rule 15).
- No promote/publish surfaces.
- CSRF via _new_csrf_token / _verify_csrf (same pattern as routes.py).
- Loopback posture inherited from app.py.
"""

from __future__ import annotations

import json
import os
import secrets
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from flask import (
    Blueprint,
    abort,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from cdb_social.admin_console.campaign_runner.launcher import SubprocessLaneLauncher
from cdb_social.admin_console.campaign_runner.planner import (
    CampaignPlan,
    compute_shortfall,
    list_domains,
    list_models,
    render_plan_text,
)
from cdb_social.admin_console.failure_signatures import scan
from cdb_social.admin_console.live_board.lane_state import (
    LaneState,
    discover_lanes,
    running_model_ids,
    stop_lane,
)
from cdb_social.admin_console.live_board.matrix import compute_matrix

ops_bp = Blueprint("ops", __name__, url_prefix="/ops")

# ---------------------------------------------------------------------------
# CSRF helpers (same pattern as routes.py)
# ---------------------------------------------------------------------------


def _new_csrf_token() -> str:
    """Generate and store a new CSRF token in the session."""
    token = secrets.token_urlsafe(32)
    session["csrf_token"] = token
    return token


def _verify_csrf() -> None:
    """Abort 403 if the submitted CSRF token does not match the session."""
    submitted = request.form.get("csrf_token", "")
    stored = session.get("csrf_token", "")
    if not submitted or not stored or not secrets.compare_digest(submitted, stored):
        abort(403, "Invalid CSRF token")


# ---------------------------------------------------------------------------
# Path helpers (env-overridable for testing)
# ---------------------------------------------------------------------------


def _informants_path() -> Path:
    return Path(os.environ.get("LSB_INFORMANTS_PATH", "data/raw/informants.jsonl"))


def _registry_path() -> Path:
    return Path(os.environ.get("LSB_REGISTRY_PATH", "data/models/registry.json"))


def _domains_path() -> Path:
    return Path(os.environ.get("LSB_DOMAINS_PATH", "data/domains/v1"))


def _ops_log_root() -> Path:
    return Path(os.environ.get("LSB_OPS_LOG_ROOT", "logs/ops-console"))


def _repo_root() -> Path:
    return Path(os.environ.get("LSB_REPO_ROOT", "."))


# ---------------------------------------------------------------------------
# Launcher helper (injectable via current_app.config for tests)
# ---------------------------------------------------------------------------


def _get_launcher() -> Any:
    """Return the lane launcher. Override app.config['OPS_LANE_LAUNCHER'] in tests."""
    return current_app.config.get("OPS_LANE_LAUNCHER") or SubprocessLaneLauncher()


# ---------------------------------------------------------------------------
# Campaign ID factory
# ---------------------------------------------------------------------------


def _new_campaign_id() -> str:
    """Generate a timestamp-based campaign identifier."""
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    suffix = secrets.token_hex(3)
    return f"ops-console-{stamp}-{suffix}"


# ---------------------------------------------------------------------------
# Plan JSON helpers
# ---------------------------------------------------------------------------


def _load_plan_json(log_root: Path) -> dict[str, Any]:
    """Load plan.json from the campaign log directory; return {} on any error."""
    plan_path = log_root / "plan.json"
    if not plan_path.exists():
        return {}
    try:
        return json.loads(plan_path.read_text(encoding="utf-8"))  # type: ignore[no-any-return]
    except Exception:
        return {}


def _plan_to_dict(plan: CampaignPlan) -> dict[str, Any]:
    """Serialise a CampaignPlan to a plain dict for template rendering."""
    return {
        "campaign_id": plan.campaign_id,
        "runs_per_cell": plan.runs_per_cell,
        "cells": [
            {
                "model_id": c.model_id,
                "domain_slug": c.domain_slug,
                "passed": c.passed,
                "needed": c.needed,
            }
            for c in plan.cells
        ],
    }


# ---------------------------------------------------------------------------
# Records helper for failure signature scans
# ---------------------------------------------------------------------------


def _load_records_by_model_domain(
    informants_path: Path,
) -> dict[tuple[str, str], list[dict[str, Any]]]:
    """Load informants.jsonl as raw dicts grouped by (model_id, domain_slug).

    Read-only; never mutates the file.
    """
    result: dict[tuple[str, str], list[dict[str, Any]]] = {}
    if not informants_path.exists():
        return result
    try:
        text = informants_path.read_text(encoding="utf-8")
    except OSError:
        return result
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec: dict[str, Any] = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(rec, dict):
            continue
        model_id: str = rec.get("model_id", "")
        domain_slug: str = rec.get("domain_slug", "")
        if model_id and domain_slug:
            key = (model_id, domain_slug)
            result.setdefault(key, []).append(rec)
    return result


# ---------------------------------------------------------------------------
# Panel 1: New Campaign
# ---------------------------------------------------------------------------


@ops_bp.route("/campaigns/new", methods=["GET"])
def campaigns_new() -> str:
    """Panel 1 form: domain selector, model selector, runs-per-cell."""
    domains = list_domains(_domains_path())
    models = list_models(_registry_path())
    csrf_token = _new_csrf_token()
    return render_template(
        "new_campaign.html",
        domains=domains,
        models=models,
        csrf_token=csrf_token,
        runs_per_cell_default=5,
    )


@ops_bp.route("/campaigns/plan", methods=["POST"])
def campaigns_plan() -> Any:
    """Panel 1 dry-run: compute shortfall and render the plan or Tier 1 notice."""
    _verify_csrf()

    domain_slugs: list[str] = request.form.getlist("domain_slugs")
    model_ids: list[str] = request.form.getlist("model_ids")
    new_domain: str = request.form.get("new_domain", "").strip()
    try:
        runs_per_cell = int(request.form.get("runs_per_cell", "5"))
        runs_per_cell = max(1, runs_per_cell)
    except (ValueError, TypeError):
        runs_per_cell = 5

    csrf_token = _new_csrf_token()

    # New-domain: Tier 1 notice, never launch.
    if new_domain:
        return render_template(
            "dry_run_plan.html",
            new_domain_notice=True,
            new_domain=new_domain,
            csrf_token=csrf_token,
            plan=None,
        )

    if not domain_slugs or not model_ids:
        return render_template(
            "dry_run_plan.html",
            new_domain_notice=False,
            plan=None,
            plan_dict=None,
            plan_text="",
            error="Select at least one domain and one model.",
            csrf_token=csrf_token,
        )

    all_domains = list_domains(_domains_path())
    known_slugs = {d.slug for d in all_domains}
    all_models = list_models(_registry_path())
    selected_models = [m for m in all_models if m.model_id in set(model_ids)]

    result = compute_shortfall(
        _informants_path(),
        selected_models,
        domain_slugs,
        runs_per_cell,
        known_slugs=known_slugs,
    )

    if isinstance(result, str):
        unknown = [s for s in domain_slugs if s not in known_slugs]
        return render_template(
            "dry_run_plan.html",
            new_domain_notice=True,
            new_domain=", ".join(unknown),
            csrf_token=csrf_token,
            plan=None,
        )

    plan: CampaignPlan = result
    plan_dict = _plan_to_dict(plan)
    return render_template(
        "dry_run_plan.html",
        new_domain_notice=False,
        plan=plan,
        plan_dict=plan_dict,
        plan_text=render_plan_text(plan),
        error=None,
        csrf_token=csrf_token,
    )


@ops_bp.route("/campaigns/launch", methods=["POST"])
def campaigns_launch() -> Any:
    """Panel 1 launch: compute shortfall, spawn lanes, redirect to live board."""
    _verify_csrf()

    domain_slugs: list[str] = request.form.getlist("domain_slugs")
    model_ids: list[str] = request.form.getlist("model_ids")
    try:
        runs_per_cell = int(request.form.get("runs_per_cell", "5"))
        runs_per_cell = max(1, runs_per_cell)
    except (ValueError, TypeError):
        runs_per_cell = 5

    if not domain_slugs or not model_ids:
        abort(400, "domain_slugs and model_ids are required")

    all_models = list_models(_registry_path())
    selected_models = [m for m in all_models if m.model_id in set(model_ids)]

    campaign_id = _new_campaign_id()
    log_root = _ops_log_root() / campaign_id

    result = compute_shortfall(
        _informants_path(),
        selected_models,
        domain_slugs,
        runs_per_cell,
        campaign_id=campaign_id,
    )

    if isinstance(result, str):
        # NEW_DOMAIN_SENTINEL: should not reach here from a valid plan flow.
        abort(400, "Cannot launch: domain not recognised. Use the plan step first.")

    log_root.mkdir(parents=True, exist_ok=True)

    cells_with_work = [c for c in result.cells if c.needed > 0]
    if not cells_with_work:
        # Nothing to launch: write plan.json so the live board can render.
        (log_root / "plan.json").write_text(
            json.dumps(_plan_to_dict(result), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return redirect(
            url_for("ops.live_board", campaign_id=campaign_id, nothing_to_do="1")
        )

    _get_launcher().launch(result, log_root, _repo_root())
    return redirect(url_for("ops.live_board", campaign_id=campaign_id))


# ---------------------------------------------------------------------------
# Panel 2: Live Board
# ---------------------------------------------------------------------------


@ops_bp.route("/live/<campaign_id>", methods=["GET"])
def live_board(campaign_id: str) -> Any:
    """Panel 2 live board: matrix, lane status, alert rows, stop/resume controls."""
    log_root = _ops_log_root() / campaign_id
    plan_data = _load_plan_json(log_root)

    nothing_to_do = request.args.get("nothing_to_do") == "1"
    resume_nothing_to_do = request.args.get("resume_nothing_to_do") == "1"
    stop_notice = request.args.get("stop_notice", "")

    # Reconstruct model_ids and domain_slugs from plan.json.
    cells: list[dict[str, Any]] = plan_data.get("cells", [])
    model_ids_ordered: list[str] = list(
        dict.fromkeys(c["model_id"] for c in cells)
    )
    domain_slugs_ordered: list[str] = list(
        dict.fromkeys(c["domain_slug"] for c in cells)
    )

    lanes: list[LaneState] = discover_lanes(log_root)
    running_ids = running_model_ids(lanes)

    matrix = compute_matrix(
        _informants_path(),
        model_ids_ordered,
        domain_slugs_ordered,
        running_model_ids=running_ids,
    )

    records_by_model_domain = _load_records_by_model_domain(_informants_path())
    alert_rows: list[dict[str, Any]] = []
    for lane in lanes:
        log_path: Path | None = lane.log_path if lane.log_path.exists() else None
        hits = scan(log_path, records_by_model_domain)
        for hit in hits:
            alert_rows.append({"lane": lane, "hit": hit})

    csrf_token = _new_csrf_token()
    return render_template(
        "live_board.html",
        campaign_id=campaign_id,
        lanes=lanes,
        matrix=matrix,
        model_ids=model_ids_ordered,
        domain_slugs=domain_slugs_ordered,
        alert_rows=alert_rows,
        csrf_token=csrf_token,
        plan_data=plan_data,
        nothing_to_do=nothing_to_do,
        resume_nothing_to_do=resume_nothing_to_do,
        stop_notice=stop_notice,
    )


@ops_bp.route("/live/<campaign_id>/lane/<safe_model>/tail", methods=["GET"])
def lane_tail(campaign_id: str, safe_model: str) -> str:
    """Panel 2 log tail: last 8 KiB of the per-lane log file."""
    log_root = _ops_log_root() / campaign_id
    log_path = log_root / f"{safe_model}.log"

    tail_text: str
    if log_path.exists():
        try:
            raw = log_path.read_bytes()
            tail_bytes = raw[-8192:]
            tail_text = tail_bytes.decode("utf-8", errors="replace")
        except OSError:
            tail_text = "(log file unreadable)"
    else:
        tail_text = "(log file not found)"

    return render_template(
        "lane_tail.html",
        campaign_id=campaign_id,
        safe_model=safe_model,
        tail_text=tail_text,
    )


@ops_bp.route("/live/<campaign_id>/lane/<safe_model>/stop", methods=["POST"])
def lane_stop(campaign_id: str, safe_model: str) -> Any:
    """Panel 2 stop lane: SIGTERM then SIGKILL if still running."""
    _verify_csrf()

    log_root = _ops_log_root() / campaign_id
    lanes = discover_lanes(log_root)
    lane = next((ln for ln in lanes if ln.safe_model == safe_model), None)

    stop_notice = ""
    if lane is None:
        stop_notice = f"Lane {safe_model!r} not found in {campaign_id}."
    elif lane.status != "running":
        stop_notice = (
            f"Lane {safe_model!r} is not running (status: {lane.status}). "
            "No action taken."
        )
    elif lane.pid is not None:
        stop_lane(lane.pid)

    return redirect(
        url_for("ops.live_board", campaign_id=campaign_id, stop_notice=stop_notice)
    )


@ops_bp.route("/live/<campaign_id>/resume", methods=["POST"])
def live_resume(campaign_id: str) -> Any:
    """Panel 2 resume: recompute shortfall, launch only missing cells as a new campaign."""
    _verify_csrf()

    log_root = _ops_log_root() / campaign_id
    plan_data = _load_plan_json(log_root)

    if not plan_data:
        abort(404, f"Plan not found for campaign {campaign_id!r}")

    # Reconstruct parameters from plan.json.
    cells: list[dict[str, Any]] = plan_data.get("cells", [])
    model_ids = list(dict.fromkeys(c["model_id"] for c in cells))
    domain_slugs = list(dict.fromkeys(c["domain_slug"] for c in cells))
    try:
        runs_per_cell = int(plan_data.get("runs_per_cell", 5))
        runs_per_cell = max(1, runs_per_cell)
    except (ValueError, TypeError):
        runs_per_cell = 5

    all_models = list_models(_registry_path())
    selected_models = [m for m in all_models if m.model_id in set(model_ids)]

    new_campaign_id = _new_campaign_id()
    result = compute_shortfall(
        _informants_path(),
        selected_models,
        domain_slugs,
        runs_per_cell,
        campaign_id=new_campaign_id,
    )

    if isinstance(result, str):
        abort(400, "Cannot resume: domain not recognised")

    cells_with_work = [c for c in result.cells if c.needed > 0]
    if not cells_with_work:
        return redirect(
            url_for(
                "ops.live_board",
                campaign_id=campaign_id,
                resume_nothing_to_do="1",
            )
        )

    new_log_root = _ops_log_root() / new_campaign_id
    new_log_root.mkdir(parents=True, exist_ok=True)
    _get_launcher().launch(result, new_log_root, _repo_root())

    return redirect(url_for("ops.live_board", campaign_id=new_campaign_id))


# ---------------------------------------------------------------------------
# Panel 3: QA
# ---------------------------------------------------------------------------


@ops_bp.route("/qa", methods=["GET"])
def qa_panel() -> str:
    """Panel 3 QA: histogram, divergence table, dispatch template blocks."""
    from cdb_social.admin_console.qa.dispatch_templates import build_templates
    from cdb_social.admin_console.qa.divergence import compute_divergence
    from cdb_social.admin_console.qa.histogram import bucket_failures

    informants = _informants_path()
    histogram_rows = bucket_failures(informants)
    divergence_rows = compute_divergence(informants)
    templates = build_templates(histogram_rows, divergence_rows)

    return render_template(
        "qa.html",
        histogram_rows=histogram_rows,
        divergence_rows=divergence_rows,
        templates=templates,
    )


@ops_bp.route("/qa/template", methods=["GET"])
def dispatch_template_view() -> Any:
    """Panel 3 QA: single dispatch template with client-side copy affordance.

    Query param: title (must match one of the built template titles).
    Returns 404 if the title is not found.
    """
    from cdb_social.admin_console.qa.dispatch_templates import build_templates
    from cdb_social.admin_console.qa.divergence import compute_divergence
    from cdb_social.admin_console.qa.histogram import bucket_failures

    title = request.args.get("title", "")
    informants = _informants_path()
    histogram_rows = bucket_failures(informants)
    divergence_rows = compute_divergence(informants)
    templates = build_templates(histogram_rows, divergence_rows)

    tmpl = next((t for t in templates if t.title == title), None)
    if tmpl is None and templates:
        # Fall back to the first template if title is absent or unknown.
        tmpl = templates[0]

    if tmpl is None:
        abort(404, "No dispatch templates available")

    return render_template(
        "dispatch_template.html",
        tmpl=tmpl,
        all_templates=templates,
    )
