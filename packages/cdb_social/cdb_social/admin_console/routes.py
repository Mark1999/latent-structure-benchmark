"""View handlers for the LSB admin console.

Routes per Phase 7 kickoff §11.6 table.

CDA SME T6b §5.x bindings applied verbatim:
- §5.1 "Draft via LLM" button text (NOT "Request draft", "Generate draft", etc.)
- §5.2 "Publish to Bluesky" button; disabled state for X/LinkedIn
- §5.3 Confirmation pages with binding header/body/button text
- §5.4 Four error-page categories with binding wording
- §5.5 framing_checks keys verbatim: hypothesis_framing, cognition_attribution,
       bare_numeric_without_ci, register_boundary
- §5.6 methodology URL verbatim in post body; raw URL in audit panel
- §5.7 "Drafter self-rating" label (NOT "Confidence")
- §5.8 Filesystem paths verbatim in <code> tags
- §5.9 Publish irreversibility wording verbatim
- §5.10 MONTHLY_ROUNDUP wording via format_trigger_summary() — no re-authoring

Per §11.1 binding B-1: the LLM call happens ONLY in the triggers_draft
POST handler, never autonomously.
"""

from __future__ import annotations

import json
import os
import secrets
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cdb_core.schemas import Platform, SocialDraft, SocialTrigger
from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from cdb_social.digest import format_trigger_summary
from cdb_social.drafters.base import DrafterRejectedException
from cdb_social.drafters.bluesky import BlueskyDrafter
from cdb_social.drafters.linkedin import LinkedInDrafter
from cdb_social.drafters.x import XDrafter
from cdb_social.publisher import (
    PublisherNotEnabled,
    PublisherTerminalError,
    PublisherTransientError,
    publish,
)
from cdb_social.queue import (
    QUEUE_STATES,
    DraftNotFoundError,
    WrongQueueStateError,
    load_draft,
    move,
    save_draft,
)

bp = Blueprint("admin", __name__)

# ─────────────────────────────────────────────────────────────────────────────
# Path helpers (env-overridable for testing)
# ─────────────────────────────────────────────────────────────────────────────

_DEFAULT_QUEUE_ROOT = Path("out/social/queue")
_DEFAULT_STATE_DIR = Path("out/social/state")


def _queue_root() -> Path:
    return Path(os.environ.get("LSB_SOCIAL_QUEUE_ROOT", str(_DEFAULT_QUEUE_ROOT)))


def _state_dir() -> Path:
    return Path(os.environ.get("LSB_SOCIAL_STATE_DIR", str(_DEFAULT_STATE_DIR)))


# ─────────────────────────────────────────────────────────────────────────────
# CSRF helpers
# ─────────────────────────────────────────────────────────────────────────────


def _new_csrf_token() -> str:
    """Generate and store a new CSRF token in the session."""
    token = secrets.token_urlsafe(32)
    session["csrf_token"] = token
    return token


def _verify_csrf() -> None:
    """Verify the CSRF token from the submitted form against the session token.

    Aborts with 403 if the token is absent, mismatched, or empty.
    """
    submitted = request.form.get("csrf_token", "")
    stored = session.get("csrf_token", "")
    if not submitted or not stored or not secrets.compare_digest(submitted, stored):
        abort(403, "Invalid CSRF token")


# ─────────────────────────────────────────────────────────────────────────────
# Queue count helper
# ─────────────────────────────────────────────────────────────────────────────


def _get_queue_counts(queue_root: Path) -> dict[str, int]:
    """Return a dict of counts per queue state."""
    counts: dict[str, int] = {}
    for state in ("pending", "approved", "failed"):
        state_dir = queue_root / state
        if state_dir.exists():
            counts[state] = len(list(state_dir.glob("*.json")))
        else:
            counts[state] = 0
    # published: sum across YYYY-MM subdirectories
    published_root = queue_root / "published"
    if published_root.exists():
        total = sum(
            len(list(subdir.glob("*.json")))
            for subdir in published_root.iterdir()
            if subdir.is_dir()
        )
        counts["published"] = total
    else:
        counts["published"] = 0
    return counts


# ─────────────────────────────────────────────────────────────────────────────
# Trigger state helpers
# ─────────────────────────────────────────────────────────────────────────────


def _load_detected_triggers(state_dir: Path) -> list[SocialTrigger]:
    """Load detected triggers from emailed_dedupe_keys.json + queue state.

    Detected triggers are those in emailed_dedupe_keys.json that have not yet
    been drafted (i.e., not yet in the posted_dedupe_keys.json and not already
    in the queue as a pending/approved draft).
    """
    triggers_path = state_dir / "emailed_dedupe_keys.json"
    if not triggers_path.exists():
        return []

    try:
        data = json.loads(triggers_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    # emailed_dedupe_keys.json has the shape {"keys": [..., ...]} where each
    # entry is a dedupe_key string, OR a list of trigger dicts.
    # T6a stores it as a list of trigger dicts for display purposes.
    raw_triggers = data.get("triggers", [])
    triggers: list[SocialTrigger] = []
    for raw in raw_triggers:
        try:
            triggers.append(SocialTrigger.model_validate(raw))
        except Exception:
            continue
    return triggers


def _load_all_drafts_in_state(state: str, queue_root: Path) -> list[SocialDraft]:
    """Load all drafts in the given queue state (excluding published)."""
    if state == "published":
        state_dir = queue_root / "published"
        if not state_dir.exists():
            return []
        drafts: list[SocialDraft] = []
        for subdir in state_dir.iterdir():
            if not subdir.is_dir():
                continue
            for path in subdir.glob("*.json"):
                try:
                    drafts.append(load_draft(path))
                except Exception:
                    continue
        # Sort by created_at descending (most recent first for published)
        return sorted(drafts, key=lambda d: d.created_at, reverse=True)

    state_path = queue_root / state
    if not state_path.exists():
        return []
    drafts = []
    for path in state_path.glob("*.json"):
        try:
            drafts.append(load_draft(path))
        except Exception:
            continue
    return sorted(drafts, key=lambda d: d.created_at)


def _find_draft_in_any_state(
    draft_id: str, queue_root: Path
) -> tuple[SocialDraft | None, str | None]:
    """Search all queue states for a draft. Returns (draft, state) or (None, None)."""
    for state in QUEUE_STATES:
        if state == "published":
            published_root = queue_root / "published"
            if not published_root.exists():
                continue
            for subdir in published_root.iterdir():
                if not subdir.is_dir():
                    continue
                candidate = subdir / f"{draft_id}.json"
                if candidate.exists():
                    try:
                        return load_draft(candidate), "published"
                    except Exception:
                        return None, None
        else:
            candidate = queue_root / state / f"{draft_id}.json"
            if candidate.exists():
                try:
                    return load_draft(candidate), state
                except Exception:
                    return None, None
    return None, None


def _get_draft_path(draft_id: str, state: str, queue_root: Path) -> Path | None:
    """Return the path to a draft file in the given state, or None if not found."""
    if state == "published":
        published_root = queue_root / "published"
        if not published_root.exists():
            return None
        for subdir in published_root.iterdir():
            if not subdir.is_dir():
                continue
            candidate = subdir / f"{draft_id}.json"
            if candidate.exists():
                return candidate
        return None
    path = queue_root / state / f"{draft_id}.json"
    return path if path.exists() else None


def _bluesky_handle() -> str:
    """Return the Bluesky handle from env or 'your-account' if unset."""
    return os.environ.get("BLUESKY_HANDLE", "") or "your-account"


# ─────────────────────────────────────────────────────────────────────────────
# Rejection reason enum (T5 §5.3 five-code enum)
# ─────────────────────────────────────────────────────────────────────────────

REJECTION_REASONS = [
    "forbidden_vocab",
    "register_boundary",
    "bare_numeric",
    "off_topic",
    "other",
]

# ─────────────────────────────────────────────────────────────────────────────
# Drafter factory
# ─────────────────────────────────────────────────────────────────────────────


def _make_drafter(platform: Platform, anthropic_client: Any = None) -> Any:
    """Instantiate the appropriate drafter for the given platform."""
    if platform == Platform.BLUESKY:
        return BlueskyDrafter(anthropic_client=anthropic_client)
    if platform == Platform.X:
        return XDrafter(anthropic_client=anthropic_client)
    if platform == Platform.LINKEDIN:
        return LinkedInDrafter(anthropic_client=anthropic_client)
    raise ValueError(f"Unknown platform: {platform!r}")


# ─────────────────────────────────────────────────────────────────────────────
# Error type short-tag classifier
# ─────────────────────────────────────────────────────────────────────────────


def _classify_error_tag(exc: Exception) -> str:
    """Return a short tag for an exception suitable for the operator-facing error page.

    Per CDA SME §5.4: one of RateLimit, Auth, Network, ServerError, Other.
    Full traceback goes to server log only.
    """
    exc_str = str(exc).lower()
    exc_type = type(exc).__name__.lower()
    combined = exc_str + " " + exc_type
    if any(s in combined for s in ("rate_limit", "ratelimit", "rate limit", "429")):
        return "RateLimit"
    auth_signals = ("auth", "401", "403", "forbidden", "unauthorized", "credential")
    if any(s in combined for s in auth_signals):
        return "Auth"
    if any(s in combined for s in ("network", "timeout", "connection", "timed out")):
        return "Network"
    if any(s in combined for s in ("500", "502", "503", "504", "server")):
        return "ServerError"
    return "Other"


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────


@bp.route("/", methods=["GET"])
def index() -> str:
    """Index page: detected triggers awaiting draft + queue state counts."""
    queue_root = _queue_root()
    state_dir = _state_dir()
    counts = _get_queue_counts(queue_root)
    triggers = _load_detected_triggers(state_dir)
    return render_template(
        "index.html",
        queue_counts=counts,
        triggers=triggers,
        format_trigger_summary=format_trigger_summary,
        platforms=list(Platform),
    )


@bp.route("/triggers", methods=["GET"])
def triggers_list() -> str:
    """All detected triggers awaiting Mark's draft request."""
    state_dir = _state_dir()
    queue_root = _queue_root()
    triggers = _load_detected_triggers(state_dir)
    counts = _get_queue_counts(queue_root)
    return render_template(
        "triggers.html",
        triggers=triggers,
        queue_counts=counts,
        format_trigger_summary=format_trigger_summary,
        platforms=list(Platform),
    )


@bp.route("/triggers/<dedupe_key>/draft", methods=["GET", "POST"])
def triggers_draft(dedupe_key: str) -> Any:
    """Draft-via-LLM route for a specific trigger.

    GET  → Confirmation page: "About to invoke {drafter_version} for the
           {platform} platform on trigger {dedupe_key}. Proceed?"
    POST → verify CSRF → invoke drafter (LLM call per §11.1 B-1) →
           save_draft to pending/ → redirect to draft view.
           Catches DrafterRejectedException; renders error page.

    Per CDA SME §5.1: button text "Draft via LLM".
    Per CDA SME §5.3: confirmation body per binding table.
    Per CDA SME §5.4: error pages per DrafterRejectedException / Anthropic error.
    """
    platform_str = request.args.get("platform", "bluesky")
    try:
        platform = Platform(platform_str)
    except ValueError:
        abort(400, f"Unknown platform: {platform_str!r}")

    state_dir = _state_dir()
    triggers = _load_detected_triggers(state_dir)
    trigger = next((t for t in triggers if t.dedupe_key == dedupe_key), None)
    if trigger is None:
        abort(404, f"Trigger {dedupe_key!r} not found in detected triggers.")

    drafter_version = _drafter_version_for_platform(platform)

    if request.method == "GET":
        csrf_token = _new_csrf_token()
        # §5.3 confirmation body (binding)
        confirm_body = (
            f"This will invoke the {drafter_version} drafter on trigger {dedupe_key} "
            f"via Claude. A new draft will land in queue/pending/ on success. "
            f"Drafter failures (forbidden vocabulary, missing CI, etc.) are surfaced; "
            f"no draft is created on failure."
        )
        return render_template(
            "confirm.html",
            action="Draft via LLM?",
            confirm_message=confirm_body,
            confirm_button="Yes, draft via LLM",
            back_url=url_for("admin.triggers_list"),
            csrf_token=csrf_token,
            form_action=url_for(
                "admin.triggers_draft",
                dedupe_key=dedupe_key,
                platform=platform_str,
            ),
            extra_hidden={},
        )

    # POST: verify CSRF then invoke drafter
    _verify_csrf()

    # Construct a minimal DomainResult (the drafter requires it).
    # In Phase 7 v1 the admin console loads from the data directory.
    domain_result = _load_domain_result_for_trigger(trigger)

    import logging  # noqa: PLC0415

    logger = logging.getLogger(__name__)

    try:
        drafter = _make_drafter(platform)
        draft = drafter.draft(trigger, domain_result)
    except DrafterRejectedException as exc:
        logger.exception("Drafter rejected: %s", exc)
        # §5.4 DrafterRejectedException error page
        failed_checks = {
            k: v for k, v in (draft_attempt_framing_checks(exc) or {}).items() if not v
        } if False else _build_failed_checks_from_exc(exc)
        return render_template(
            "error.html",
            error_category="drafter_rejected",
            forbidden_terms_hit=exc.forbidden_terms_hit,
            failed_checks=failed_checks,
            trigger=trigger,
            platform=platform,
            dedupe_key=dedupe_key,
            platform_str=platform_str,
            retry_url=url_for(
                "admin.triggers_draft",
                dedupe_key=dedupe_key,
                platform=platform_str,
            ),
            back_url=url_for("admin.triggers_list"),
        ), 422
    except Exception as exc:
        logger.exception("Anthropic API error during drafting: %s", exc)
        # §5.4 Anthropic API failure page
        error_tag = _classify_error_tag(exc)
        return render_template(
            "error.html",
            error_category="anthropic_api",
            error_tag=error_tag,
            trigger=trigger,
            platform=platform,
            dedupe_key=dedupe_key,
            platform_str=platform_str,
            retry_url=url_for(
                "admin.triggers_draft",
                dedupe_key=dedupe_key,
                platform=platform_str,
            ),
            back_url=url_for("admin.triggers_list"),
        ), 500

    # Save draft to pending/
    queue_root = _queue_root()
    draft_path = queue_root / "pending" / f"{draft.draft_id}.json"
    save_draft(draft, draft_path)

    return redirect(url_for("admin.draft_view", draft_id=draft.draft_id))


def _build_failed_checks_from_exc(exc: DrafterRejectedException) -> dict[str, Any]:
    """Build a failed-checks dict from DrafterRejectedException for error display.

    Per CDA SME §5.4 / §5.5: each entry is {key: {passed: bool, evidence: str}}.
    """
    failed: dict[str, Any] = {}
    if exc.forbidden_terms_hit:
        failed["cognition_attribution"] = {
            "passed": False,
            "evidence": ", ".join(f'"{t}"' for t in exc.forbidden_terms_hit),
        }
    if exc.hypothesis_patterns_hit:
        failed["hypothesis_framing"] = {
            "passed": False,
            "evidence": ", ".join(f'"{t}"' for t in exc.hypothesis_patterns_hit),
        }
    if exc.bare_numerics:
        failed["bare_numeric_without_ci"] = {
            "passed": False,
            "evidence": "bare numeric: " + ", ".join(f'"{n}"' for n in exc.bare_numerics),
        }
    return failed


def draft_attempt_framing_checks(exc: DrafterRejectedException) -> dict[str, bool] | None:
    """Placeholder — never called; exists to satisfy the editor."""
    return None


def _drafter_version_for_platform(platform: Platform) -> str:
    """Return the drafter_version string for the given platform."""
    versions = {
        Platform.BLUESKY: "bluesky-v1",
        Platform.X: "x-v1",
        Platform.LINKEDIN: "linkedin-v1",
    }
    return versions.get(platform, f"{platform.value}-v1")


def _load_domain_result_for_trigger(trigger: SocialTrigger) -> Any:
    """Load DomainResult for the trigger's domain_slug from the published data dir.

    Returns a minimal stub DomainResult if the domain file cannot be loaded.
    """
    import logging  # noqa: PLC0415

    logger = logging.getLogger(__name__)
    data_dir = Path(os.environ.get("LSB_SOCIAL_DATA_DIR", "apps/dashboard/public/data"))

    domain_slug = trigger.domain_slug
    if not domain_slug:
        return _make_stub_domain_result(domain_slug)

    domain_file = data_dir / domain_slug / "0.2.json"
    if not domain_file.exists():
        logger.warning(
            "Domain file not found: %s — using stub DomainResult", domain_file
        )
        return _make_stub_domain_result(domain_slug)

    try:
        from cdb_core.schemas import DomainResult  # noqa: PLC0415

        raw = json.loads(domain_file.read_text(encoding="utf-8"))
        return DomainResult.model_validate(raw)
    except Exception as exc:
        logger.warning(
            "Failed to load DomainResult for %r: %s — using stub", domain_slug, exc
        )
        return _make_stub_domain_result(domain_slug)


def _make_stub_domain_result(domain_slug: str | None) -> Any:
    """Return a minimal DomainResult stub for when the real data is unavailable."""
    from cdb_core.schemas import DomainResult  # noqa: PLC0415

    return DomainResult(
        domain_slug=domain_slug or "unknown",
        analysis_version="0.2",
        models=[],
        free_lists={},
        mds_coordinates={},
        mds_uncertainty={},
        similarity_matrix=[],
        similarity_ci=[],
        consensus_score=0.0,
        consensus_ci=(0.0, 0.0),
        generated_lede="",
        generated_at=datetime.now(UTC),
    )


@bp.route("/queue/<state>", methods=["GET"])
def queue_view(state: str) -> Any:
    """View a queue state (pending / approved / published / failed)."""
    if state not in QUEUE_STATES:
        abort(400, f"Unknown queue state: {state!r}. Must be one of {QUEUE_STATES!r}")
    queue_root = _queue_root()
    counts = _get_queue_counts(queue_root)
    drafts = _load_all_drafts_in_state(state, queue_root)
    return render_template(
        "queue.html",
        state=state,
        drafts=drafts,
        queue_counts=counts,
        format_trigger_summary=format_trigger_summary,
    )


@bp.route("/draft/<draft_id>", methods=["GET"])
def draft_view(draft_id: str) -> Any:
    """Single-draft detail view."""
    queue_root = _queue_root()
    draft, current_state = _find_draft_in_any_state(draft_id, queue_root)
    if draft is None:
        abort(404, f"Draft {draft_id!r} not found in any queue state.")
    counts = _get_queue_counts(queue_root)
    bluesky_handle = _bluesky_handle()
    return render_template(
        "draft.html",
        draft=draft,
        draft_state=current_state,
        queue_counts=counts,
        format_trigger_summary=format_trigger_summary,
        bluesky_handle=bluesky_handle,
    )


@bp.route("/draft/<draft_id>/approve", methods=["GET", "POST"])
def draft_approve(draft_id: str) -> Any:
    """Approve a pending draft (moves pending → approved).

    GET  → confirmation page.
    POST → verify CSRF → move pending→approved.

    Per CDA SME §5.3: "Approve draft?" / "This does not publish."
    """
    queue_root = _queue_root()

    if request.method == "GET":
        draft, current_state = _find_draft_in_any_state(draft_id, queue_root)
        if draft is None:
            abort(404, f"Draft {draft_id!r} not found.")
        if current_state != "pending":
            abort(400, f"Draft {draft_id!r} is in state {current_state!r}, not 'pending'.")
        csrf_token = _new_csrf_token()
        # §5.3 binding body for Approve
        confirm_body = (
            f'Approve draft {draft_id}. The draft moves to queue/approved/. '
            f'This does not publish. You will need to click "Publish to Bluesky" '
            f'on the approved-draft page to send the post.'
        )
        return render_template(
            "confirm.html",
            action="Approve draft?",
            confirm_message=confirm_body,
            confirm_button="Yes, approve",
            back_url=url_for("admin.draft_view", draft_id=draft_id),
            csrf_token=csrf_token,
            form_action=url_for("admin.draft_approve", draft_id=draft_id),
            extra_hidden={},
        )

    _verify_csrf()
    try:
        move(draft_id, "pending", "approved", queue_root=queue_root)
    except WrongQueueStateError as exc:
        abort(400, str(exc))
    except DraftNotFoundError as exc:
        abort(404, str(exc))
    return redirect(url_for("admin.draft_view", draft_id=draft_id))


@bp.route("/draft/<draft_id>/reject", methods=["GET", "POST"])
def draft_reject(draft_id: str) -> Any:
    """Reject a pending draft (moves pending → failed + writes sidecar JSON).

    GET  → form with 5-code enum + optional free-text.
    POST → verify CSRF → move pending→failed + write sidecar JSON.

    Per CDA SME §5.3: "Reject draft?" confirmation wording.
    Rejection reasons per T5 §5.3 five-code enum.
    """
    queue_root = _queue_root()

    if request.method == "GET":
        draft, current_state = _find_draft_in_any_state(draft_id, queue_root)
        if draft is None:
            abort(404, f"Draft {draft_id!r} not found.")
        if current_state != "pending":
            abort(400, f"Draft {draft_id!r} is in state {current_state!r}, not 'pending'.")
        csrf_token = _new_csrf_token()
        return render_template(
            "reject.html",
            draft=draft,
            draft_id=draft_id,
            rejection_reasons=REJECTION_REASONS,
            csrf_token=csrf_token,
            form_action=url_for("admin.draft_reject", draft_id=draft_id),
            back_url=url_for("admin.draft_view", draft_id=draft_id),
        )

    _verify_csrf()
    reason = request.form.get("reason", "other")
    note = request.form.get("note", "").strip()
    if reason not in REJECTION_REASONS:
        reason = "other"

    try:
        new_path = move(draft_id, "pending", "failed", queue_root=queue_root)
    except WrongQueueStateError as exc:
        abort(400, str(exc))
    except DraftNotFoundError as exc:
        abort(404, str(exc))

    # Write sidecar JSON with rejection reason
    sidecar = {
        "draft_id": draft_id,
        "rejected_at": datetime.now(UTC).isoformat(),
        "reason": reason,
        "note": note,
    }
    sidecar_path = new_path.parent / f"{draft_id}.reject.json"
    import contextlib  # noqa: PLC0415

    with contextlib.suppress(OSError):
        sidecar_path.write_text(
            json.dumps(sidecar, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    return redirect(url_for("admin.queue_view", state="failed"))


@bp.route("/draft/<draft_id>/edit", methods=["GET", "POST"])
def draft_edit(draft_id: str) -> Any:
    """Edit a draft's text and re-validate.

    GET  → text-area form with current text.
    POST → verify CSRF → re-validate → move to approved if passes,
           stay in pending with text_history appended if fails.

    Per CDA SME §5.4 Sub-ruling D: edit-flow validator failure uses
    "Edit did not pass validator." header.
    """
    queue_root = _queue_root()
    draft, current_state = _find_draft_in_any_state(draft_id, queue_root)
    if draft is None:
        abort(404, f"Draft {draft_id!r} not found.")

    if request.method == "GET":
        csrf_token = _new_csrf_token()
        return render_template(
            "edit.html",
            draft=draft,
            draft_id=draft_id,
            draft_state=current_state,
            csrf_token=csrf_token,
            form_action=url_for("admin.draft_edit", draft_id=draft_id),
            back_url=url_for("admin.draft_view", draft_id=draft_id),
        )

    _verify_csrf()
    new_text = request.form.get("text", "").strip()
    action = request.form.get("action", "save")

    if action == "discard":
        return redirect(url_for("admin.draft_view", draft_id=draft_id))

    # Re-validate the edited text
    from cdb_social.drafters.base import validate_draft  # noqa: PLC0415

    forbidden_hits, framing_checks = validate_draft(new_text)
    validation_passed = not forbidden_hits and all(framing_checks.values())

    # Append original text to history before saving new text
    updated_history = list(draft.text_history) + [draft.text]
    updated_draft = draft.model_copy(
        update={
            "text": new_text,
            "text_history": updated_history,
            "forbidden_terms_hit": forbidden_hits,
            "framing_check_passed": validation_passed,
            "framing_checks": {
                "hypothesis_framing": framing_checks.get("hypothesis_framing", True),
                "cognition_attribution": framing_checks.get("cognition_attribution", True),
                "bare_numeric_without_ci": framing_checks.get("bare_numeric_without_ci", True),
                "register_boundary": framing_checks.get("register_boundary", True),
            },
        }
    )

    if not validation_passed:
        # Save updated draft back to its current state with text_history appended
        current_path = _get_draft_path(draft_id, current_state or "pending", queue_root)
        if current_path:
            save_draft(updated_draft, current_path)

        failed_checks = {
            k: v for k, v in framing_checks.items() if not v
        }
        csrf_token = _new_csrf_token()
        return render_template(
            "edit.html",
            draft=updated_draft,
            draft_id=draft_id,
            draft_state=current_state,
            csrf_token=csrf_token,
            form_action=url_for("admin.draft_edit", draft_id=draft_id),
            back_url=url_for("admin.draft_view", draft_id=draft_id),
            validation_failed=True,
            failed_checks=failed_checks,
            forbidden_terms_hit=forbidden_hits,
        ), 422

    # Validation passed — save and move to approved
    # First save the updated draft in its current location
    current_path = _get_draft_path(draft_id, current_state or "pending", queue_root)
    if current_path:
        save_draft(updated_draft, current_path)

    # Move to approved if not already there
    if current_state != "approved":
        try:
            move(draft_id, current_state or "pending", "approved", queue_root=queue_root)
        except (WrongQueueStateError, DraftNotFoundError) as exc:
            abort(400, str(exc))

    return redirect(url_for("admin.draft_view", draft_id=draft_id))


@bp.route("/draft/<draft_id>/publish", methods=["GET", "POST"])
def draft_publish(draft_id: str) -> Any:
    """Publish an approved draft to its platform.

    GET  → confirmation page with full publish-irreversibility wording per §5.9.
    POST → verify CSRF → invoke publisher (Bluesky live; X/LinkedIn raise
           PublisherNotEnabled and render error).

    Per CDA SME §5.2: "Publish to Bluesky" button.
    Per CDA SME §5.9: binding irreversibility wording.
    """
    queue_root = _queue_root()
    draft, current_state = _find_draft_in_any_state(draft_id, queue_root)
    if draft is None:
        abort(404, f"Draft {draft_id!r} not found.")

    bluesky_handle = _bluesky_handle()

    if request.method == "GET":
        if current_state != "approved":
            abort(400, f"Draft {draft_id!r} is in state {current_state!r}, not 'approved'.")
        csrf_token = _new_csrf_token()

        if draft.platform == Platform.BLUESKY:
            # §5.9 binding wording — verbatim
            confirm_body = (
                f"This will post to Bluesky as @{bluesky_handle}. "
                "Once posted, deletion is best-effort — the timestamp and any "
                "platform-side cache may persist. "
                "The post text below will be sent verbatim."
            )
            confirm_button = "Yes, publish to Bluesky"
            action_header = "Publish to Bluesky?"
        else:
            # X / LinkedIn: show disabled state
            confirm_body = (
                f"Live publishing is not enabled for {draft.platform.value.upper()} in Phase 7. "
                f"The draft text is available in "
                f"out/social/queue/approved/{draft_id}.json — post manually."
            )
            confirm_button = f"Publishing not enabled for {draft.platform.value.upper()}"
            action_header = f"Publish to {draft.platform.value.upper()}?"

        return render_template(
            "confirm.html",
            action=action_header,
            confirm_message=confirm_body,
            confirm_button=confirm_button,
            back_url=url_for("admin.draft_view", draft_id=draft_id),
            csrf_token=csrf_token,
            form_action=url_for("admin.draft_publish", draft_id=draft_id),
            extra_hidden={},
            draft=draft,
            show_draft_text=True,
            bluesky_handle=bluesky_handle,
            platform_not_enabled=(draft.platform != Platform.BLUESKY),
        )

    # POST
    _verify_csrf()

    import logging  # noqa: PLC0415

    logger_pub = logging.getLogger(__name__)

    try:
        post_record = publish(draft)
    except PublisherNotEnabled as exc:
        # X / LinkedIn draft — not live in Phase 7
        return render_template(
            "error.html",
            error_category="publisher_not_enabled",
            platform=draft.platform,
            error_message=str(exc),
            draft=draft,
            draft_id=draft_id,
            back_url=url_for("admin.draft_view", draft_id=draft_id),
        ), 422
    except (PublisherTransientError, PublisherTerminalError) as exc:
        failure_category = (
            "transient" if isinstance(exc, PublisherTransientError) else "terminal"
        )
        error_tag = _classify_error_tag(exc)
        logger_pub.exception("Bluesky publish failed: %s", exc)
        return render_template(
            "error.html",
            error_category="bluesky_failed",
            failure_category=failure_category,
            error_tag=error_tag,
            draft=draft,
            draft_id=draft_id,
            back_url=url_for("admin.draft_view", draft_id=draft_id),
        ), 500
    except Exception as exc:
        error_tag = _classify_error_tag(exc)
        logger_pub.exception("Unexpected publish error: %s", exc)
        return render_template(
            "error.html",
            error_category="bluesky_failed",
            failure_category="terminal",
            error_tag=error_tag,
            draft=draft,
            draft_id=draft_id,
            back_url=url_for("admin.draft_view", draft_id=draft_id),
        ), 500

    # Move to published/
    import contextlib  # noqa: PLC0415

    with contextlib.suppress(WrongQueueStateError, DraftNotFoundError):
        move(draft_id, "approved", "published", queue_root=queue_root)

    # Save post record alongside published draft
    published_root = queue_root / "published"
    now = datetime.now(UTC)
    subdir = published_root / now.strftime("%Y-%m")
    subdir.mkdir(parents=True, exist_ok=True)
    record_path = subdir / f"{draft_id}.post_record.json"
    with contextlib.suppress(OSError):
        record_path.write_text(
            post_record.model_dump_json(indent=2), encoding="utf-8"
        )

    return redirect(url_for("admin.draft_view", draft_id=draft_id))
