"""Social pipeline CLI — Phase 7 T6.

Entry point: ``python -m cdb_social.cli {subcommand}``

Subcommands
-----------
run-once   — detect triggers → draft → queue/pending/
review     — delegates to scripts/social_review.py
publish    — drain approved/ → publisher → published/{YYYY-MM}/ or failed/
status     — counts per queue state

Ordering constraint (from triggers.py):
    detect_new_model() MUST be called before detect_divergence() so the
    new-model exclusion list is available.

Design invariants:
- run-once does NOT auto-publish. Mark's ``publish`` subcommand is the publish
  trigger. The cron (Phase 7 T7) calls ``run-once`` only.
- Drift trigger is explicitly disabled (enable=False) per kickoff §2 item 1.
- DrafterRejectedException is caught per-draft; one bad draft does not kill
  the run.
- Credentials come from env only; never logged.

See ARCHITECTURE.md §4.6 and docs/status/2026-05-17-phase7-architect-kickoff.md §3 T6.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cdb_core.schemas import Platform, PublishStatus, SocialDraft, SocialPostRecord, SocialTrigger

from cdb_social import (
    detect_divergence,
    detect_drift,
    detect_monthly_roundup,
    detect_new_domain,
    detect_new_model,
)
from cdb_social.drafters.base import DrafterRejectedException
from cdb_social.drafters.bluesky import BlueskyDrafter
from cdb_social.publisher import (
    PublisherNotEnabled,
    PublisherTerminalError,
    PublisherTransientError,
    publish,
)
from cdb_social.queue import list_approved, load_draft, move, save_draft

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Path configuration (env-overridable for testing)
# ─────────────────────────────────────────────────────────────────────────────

_DEFAULT_QUEUE_ROOT = Path("out/social/queue")
_DEFAULT_STATE_DIR = Path("out/social/state")
_DEFAULT_DATA_DIR = Path("apps/dashboard/public/data")
_DEFAULT_SCRIPTS_DIR = Path("scripts")


def _queue_root() -> Path:
    return Path(os.environ.get("LSB_SOCIAL_QUEUE_ROOT", str(_DEFAULT_QUEUE_ROOT)))


def _state_dir() -> Path:
    return Path(os.environ.get("LSB_SOCIAL_STATE_DIR", str(_DEFAULT_STATE_DIR)))


def _data_dir() -> Path:
    return Path(os.environ.get("LSB_SOCIAL_DATA_DIR", str(_DEFAULT_DATA_DIR)))


def _scripts_dir() -> Path:
    return Path(os.environ.get("LSB_SOCIAL_SCRIPTS_DIR", str(_DEFAULT_SCRIPTS_DIR)))


# ─────────────────────────────────────────────────────────────────────────────
# Data loading helpers
# ─────────────────────────────────────────────────────────────────────────────


def _load_manifest(data_dir: Path) -> dict[str, Any]:
    """Load manifest.json from the published data directory.

    Returns an empty dict if the manifest is absent (non-fatal — detectors
    handle the empty-manifest case by emitting no triggers).
    """
    manifest_path = data_dir / "manifest.json"
    if not manifest_path.exists():
        logger.warning(
            "manifest.json not found at %s — detectors will emit no triggers",
            manifest_path,
        )
        return {}
    try:
        return dict(json.loads(manifest_path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Failed to load manifest.json: %s", e)
        return {}


def _load_domain_results(data_dir: Path, manifest: dict[str, Any]) -> list[Any]:
    """Load DomainResult objects from published data files.

    For each domain in manifest, attempts to load data/{domain}/0.2.json.
    Silently skips domains whose file is absent or unparseable.
    """
    from cdb_core.schemas import DomainResult  # noqa: PLC0415

    domain_results: list[DomainResult] = []
    domains: dict[str, Any] = manifest.get("domains", {})
    for domain_slug in domains:
        domain_file = data_dir / domain_slug / "0.2.json"
        if not domain_file.exists():
            logger.debug("Domain file not found: %s", domain_file)
            continue
        try:
            raw = json.loads(domain_file.read_text(encoding="utf-8"))
            domain_results.append(DomainResult.model_validate(raw))
        except Exception as e:
            logger.warning("Failed to load domain result for %r: %s", domain_slug, e)

    return domain_results


# ─────────────────────────────────────────────────────────────────────────────
# Dedupe helpers
# ─────────────────────────────────────────────────────────────────────────────


def _load_dedupe_keys(state_dir: Path) -> set[str]:
    """Load posted_dedupe_keys.json as a set of key strings.

    Returns an empty set if the file is absent.
    """
    path = state_dir / "posted_dedupe_keys.json"
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return set(data.get("keys", []))
    except (json.JSONDecodeError, OSError):
        return set()


def _save_dedupe_keys(state_dir: Path, keys: set[str]) -> None:
    """Atomically write posted_dedupe_keys.json."""
    import tempfile  # noqa: PLC0415

    state_dir.mkdir(parents=True, exist_ok=True)
    path = state_dir / "posted_dedupe_keys.json"
    payload = json.dumps({"keys": sorted(keys)}, indent=2, ensure_ascii=True)
    fd, tmp = tempfile.mkstemp(dir=state_dir, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(payload)
        os.replace(tmp, path)
    except Exception:
        import contextlib  # noqa: PLC0415
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise


# ─────────────────────────────────────────────────────────────────────────────
# Publish retry log
# ─────────────────────────────────────────────────────────────────────────────


def _append_retry_record(state_dir: Path, draft: SocialDraft, error_msg: str) -> None:
    """Append a retry record to publish_retries.jsonl."""
    state_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(UTC).isoformat(),
        "draft_id": draft.draft_id,
        "platform": draft.platform.value,
        "error_message": error_msg,
    }
    retry_path = state_dir / "publish_retries.jsonl"
    try:
        with retry_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as e:
        logger.warning("Failed to write publish retry log: %s", e)


# ─────────────────────────────────────────────────────────────────────────────
# run-once subcommand
# ─────────────────────────────────────────────────────────────────────────────


def cmd_run_once(args: argparse.Namespace) -> int:
    """Detect triggers → draft → queue/pending/.

    Steps:
    1. Load manifest.json and domain result files.
    2. Run all detectors (drift explicitly disabled per kickoff §2 item 1).
    3. Deduplicate against posted_dedupe_keys.json.
    4. For each new trigger, invoke the drafter(s).
    5. Write accepted drafts to pending/; log rejections.
    6. Print summary unless --quiet.

    Returns the exit code (0 on success).
    """
    queue_root = _queue_root()
    state_dir = _state_dir()
    data_dir = _data_dir()

    # Step 1: load data
    manifest = _load_manifest(data_dir)
    domain_results = _load_domain_results(data_dir, manifest)

    # Step 2: run detectors
    # detect_new_model MUST run before detect_divergence (ordering constraint)
    new_model_triggers: list[SocialTrigger] = []
    try:
        new_model_triggers = detect_new_model(manifest, state_dir)
    except Exception as e:
        logger.warning("detect_new_model failed: %s", e)

    new_domain_triggers: list[SocialTrigger] = []
    try:
        new_domain_triggers = detect_new_domain(manifest, state_dir)
    except Exception as e:
        logger.warning("detect_new_domain failed: %s", e)

    # Drift: explicitly disabled per kickoff §2 item 1
    drift_triggers: list[SocialTrigger] = detect_drift(
        domain_results, state_dir, enable=False
    )

    # Build new_models_this_run dict for divergence exclusion
    new_models_this_run: dict[str, list[str]] = {}
    for trig in new_model_triggers:
        domain = trig.domain_slug or ""
        model = trig.model_id or ""
        if domain and model:
            new_models_this_run.setdefault(domain, []).append(model)

    divergence_triggers: list[SocialTrigger] = []
    try:
        divergence_triggers = detect_divergence(
            domain_results, state_dir, new_models_this_run=new_models_this_run
        )
    except Exception as e:
        logger.warning("detect_divergence failed: %s", e)

    monthly_triggers: list[SocialTrigger] = []
    try:
        monthly_triggers = detect_monthly_roundup(state_dir, now=datetime.now(UTC))
    except Exception as e:
        logger.warning("detect_monthly_roundup failed: %s", e)

    all_triggers: list[SocialTrigger] = (
        new_model_triggers
        + new_domain_triggers
        + drift_triggers
        + divergence_triggers
        + monthly_triggers
    )

    # Step 3: deduplicate
    posted_keys = _load_dedupe_keys(state_dir)
    new_triggers = [t for t in all_triggers if t.dedupe_key not in posted_keys]
    n_deduped = len(all_triggers) - len(new_triggers)
    if n_deduped:
        logger.info("Deduplicated %d already-posted trigger(s)", n_deduped)

    # Step 4-5: draft and queue
    # Determine which platforms to draft for
    platforms_to_draft: list[Platform] = [Platform.BLUESKY]
    if hasattr(args, "platform") and args.platform:
        for p_str in args.platform.split(","):
            p_str = p_str.strip().lower()
            try:
                extra = Platform(p_str)
                if extra not in platforms_to_draft:
                    platforms_to_draft.append(extra)
            except ValueError:
                logger.warning("Unknown platform flag value %r — ignored", p_str)

    n_drafted = 0
    n_rejected = 0

    for trigger in new_triggers:
        # Load relevant domain result (may be None for cross-domain triggers)
        domain_result = None
        if trigger.domain_slug:
            for dr in domain_results:
                if dr.domain_slug == trigger.domain_slug:
                    domain_result = dr
                    break

        for platform in platforms_to_draft:
            drafter = _get_drafter(platform)
            if drafter is None:
                logger.debug("No drafter configured for platform %r — skipping", platform)
                continue

            # Resolve effective domain result:
            # - Use the trigger's matched domain result if available.
            # - Fall back to the first available domain result for cross-domain
            #   triggers (e.g. MONTHLY_ROUNDUP) or when no per-domain result
            #   was found.
            # - Pass None when domain_results is empty; the drafter's own
            #   exception handling determines whether that is fatal.
            if domain_result is not None:
                effective_dr = domain_result
            elif domain_results:
                effective_dr = domain_results[0]
            else:
                logger.debug(
                    "No domain results loaded — passing None to drafter for trigger %s",
                    trigger.trigger_type,
                )
                effective_dr = None  # type: ignore[assignment]

            try:
                draft = drafter.draft(trigger, effective_dr)
            except DrafterRejectedException as exc:
                logger.warning(
                    "Drafter rejected trigger %s (platform=%s): %s",
                    trigger.dedupe_key,
                    platform.value,
                    exc,
                )
                n_rejected += 1
                continue
            except Exception as exc:
                logger.warning(
                    "Drafter raised unexpected error for trigger %s (platform=%s): %s",
                    trigger.dedupe_key,
                    platform.value,
                    exc,
                )
                n_rejected += 1
                continue

            # Write to pending/
            queue_root.mkdir(parents=True, exist_ok=True)
            pending_dir = queue_root / "pending"
            pending_dir.mkdir(parents=True, exist_ok=True)
            draft_path = pending_dir / f"{draft.draft_id}.json"
            save_draft(draft, draft_path)
            logger.info(
                "Draft written: %s (trigger=%s, platform=%s)",
                draft.draft_id,
                trigger.trigger_type,
                platform.value,
            )
            n_drafted += 1

    n_detected = len(all_triggers)
    if not getattr(args, "quiet", False):
        print(
            f"run-once: {n_detected} triggers detected, "
            f"{n_drafted} drafts written, "
            f"{n_rejected} rejected"
        )

    return 0


def _get_drafter(platform: Platform) -> Any:
    """Return the configured drafter for the given platform.

    For Phase 7 v1, only BlueskyDrafter is returned for BLUESKY.
    X and LinkedIn drafters are available but not auto-invoked in run-once
    by default (the --platform flag is the only way to request them).
    """
    if platform == Platform.BLUESKY:
        try:
            return BlueskyDrafter()
        except Exception as e:
            logger.warning("Failed to construct BlueskyDrafter: %s", e)
            return None

    if platform == Platform.X:
        try:
            from cdb_social.drafters.x import XDrafter  # noqa: PLC0415
            return XDrafter()
        except Exception as e:
            logger.warning("Failed to construct XDrafter: %s", e)
            return None

    if platform == Platform.LINKEDIN:
        try:
            from cdb_social.drafters.linkedin import LinkedInDrafter  # noqa: PLC0415
            return LinkedInDrafter()
        except Exception as e:
            logger.warning("Failed to construct LinkedInDrafter: %s", e)
            return None

    return None


# ─────────────────────────────────────────────────────────────────────────────
# review subcommand
# ─────────────────────────────────────────────────────────────────────────────


def cmd_review(args: argparse.Namespace) -> int:
    """Delegate to scripts/social_review.py.

    Passes through all remaining argv arguments so the review CLI receives
    its own flags unmodified.
    """
    scripts_dir = _scripts_dir()
    review_script = scripts_dir / "social_review.py"

    # Build passthrough args (everything after 'review' in the CLI)
    passthrough: list[str] = []
    if hasattr(args, "review_args") and args.review_args:
        passthrough = list(args.review_args)

    cmd = [sys.executable, str(review_script)] + passthrough

    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except FileNotFoundError:
        logger.error("Review script not found: %s", review_script)
        print(f"Error: review script not found at {review_script}", file=sys.stderr)
        return 1
    except OSError as e:
        logger.error("Failed to launch review script: %s", e)
        return 1


# ─────────────────────────────────────────────────────────────────────────────
# publish subcommand
# ─────────────────────────────────────────────────────────────────────────────


def cmd_publish(args: argparse.Namespace) -> int:
    """Drain approved/ → publisher → published/{YYYY-MM}/ or failed/.

    For each approved draft:
    - PublisherNotEnabled → failed/ with "platform not enabled in v1"
    - PublisherTransientError → stays in approved/; logged to publish_retries.jsonl
    - PublisherTerminalError → failed/ with error message verbatim
    - Success → published/{YYYY-MM}/ with SocialPostRecord sidecar

    --dry-run flag skips the real API call and writes DRY_RUN records.

    Returns exit code 0 always (partial success is not a failure at the cron level).
    """
    queue_root = _queue_root()
    state_dir = _state_dir()
    dry_run: bool = getattr(args, "dry_run", False)

    approved_paths = list_approved(queue_root)
    n_approved = len(approved_paths)
    n_published = 0
    n_failed = 0
    n_retried = 0

    for draft_path in approved_paths:
        try:
            draft = load_draft(draft_path)
        except Exception as e:
            logger.warning("Failed to load approved draft %s: %s", draft_path, e)
            n_failed += 1
            continue

        try:
            record = publish(draft, dry_run=dry_run)
        except PublisherNotEnabled:
            logger.info(
                "Draft %s: platform not enabled in v1 (%s)",
                draft.draft_id,
                draft.platform.value,
            )
            record = SocialPostRecord(
                draft_id=draft.draft_id,
                published_at=datetime.now(UTC),
                platform_post_id=None,
                platform_post_url=None,
                publish_status=PublishStatus.FAILED,
                error_message="platform not enabled in v1",
            )
            _move_to_failed(draft, record, queue_root)
            n_failed += 1
            continue

        except PublisherTransientError as exc:
            error_msg = str(exc)
            logger.warning(
                "Draft %s: transient error — will retry next run: %s",
                draft.draft_id,
                error_msg,
            )
            _append_retry_record(state_dir, draft, error_msg)
            n_retried += 1
            continue

        except PublisherTerminalError as exc:
            error_msg = str(exc)
            logger.error(
                "Draft %s: terminal error — moving to failed/: %s",
                draft.draft_id,
                error_msg,
            )
            record = SocialPostRecord(
                draft_id=draft.draft_id,
                published_at=datetime.now(UTC),
                platform_post_id=None,
                platform_post_url=None,
                publish_status=PublishStatus.FAILED,
                error_message=error_msg,
            )
            _move_to_failed(draft, record, queue_root)
            n_failed += 1
            continue

        # Success (or dry-run) — move to published/{YYYY-MM}/
        _move_to_published(draft, record, queue_root)
        n_published += 1

    if not getattr(args, "quiet", False):
        print(
            f"publish: {n_published}/{n_approved} succeeded, "
            f"{n_failed} failed, "
            f"{n_retried} marked for retry"
        )

    return 0


def _move_to_failed(
    draft: SocialDraft,
    record: SocialPostRecord,
    queue_root: Path,
) -> None:
    """Move draft from approved/ to failed/, writing a SocialPostRecord sidecar."""
    failed_dir = queue_root / "failed"
    failed_dir.mkdir(parents=True, exist_ok=True)

    # Write record sidecar alongside the draft JSON
    record_path = failed_dir / f"{draft.draft_id}.record.json"
    try:
        record_path.write_text(
            record.model_dump_json(indent=2),
            encoding="utf-8",
        )
    except OSError as e:
        logger.warning("Failed to write failure record sidecar: %s", e)

    try:
        move(draft.draft_id, "approved", "failed", queue_root=queue_root)
    except Exception as e:
        logger.error("Failed to move draft %s to failed/: %s", draft.draft_id, e)


def _move_to_published(
    draft: SocialDraft,
    record: SocialPostRecord,
    queue_root: Path,
) -> None:
    """Move draft from approved/ to published/{YYYY-MM}/, writing a sidecar JSON."""
    now = datetime.now(UTC)
    subdir = now.strftime("%Y-%m")
    published_dir = queue_root / "published" / subdir
    published_dir.mkdir(parents=True, exist_ok=True)

    # Write SocialPostRecord sidecar
    record_path = published_dir / f"{draft.draft_id}.record.json"
    try:
        record_path.write_text(
            record.model_dump_json(indent=2),
            encoding="utf-8",
        )
    except OSError as e:
        logger.warning("Failed to write published record sidecar: %s", e)

    try:
        move(draft.draft_id, "approved", "published", queue_root=queue_root)
    except Exception as e:
        logger.error("Failed to move draft %s to published/: %s", draft.draft_id, e)


# ─────────────────────────────────────────────────────────────────────────────
# status subcommand
# ─────────────────────────────────────────────────────────────────────────────


def cmd_status(args: argparse.Namespace) -> int:
    """Count files per queue state and print the summary."""
    queue_root = _queue_root()

    n_pending = _count_json_files(queue_root / "pending")
    n_approved = _count_json_files(queue_root / "approved")
    n_failed = _count_json_files(queue_root / "failed")

    # Published: walk YYYY-MM subdirs; count this month separately
    published_root = queue_root / "published"
    n_published_total = 0
    n_published_this_month = 0
    this_month = datetime.now(UTC).strftime("%Y-%m")
    if published_root.exists():
        for subdir in published_root.iterdir():
            if not subdir.is_dir():
                continue
            count = _count_json_files(subdir, exclude_suffix=".record.json")
            n_published_total += count
            if subdir.name == this_month:
                n_published_this_month = count

    if not getattr(args, "quiet", False):
        print(f"pending:           {n_pending}")
        print(f"approved:          {n_approved}")
        print(f"failed:            {n_failed}")
        print(
            f"published (total): {n_published_total} "
            f"(this month: {n_published_this_month})"
        )

    return 0


def _count_json_files(directory: Path, exclude_suffix: str = ".record.json") -> int:
    """Count .json files in a directory, excluding sidecar record files."""
    if not directory.exists():
        return 0
    return sum(
        1
        for p in directory.iterdir()
        if p.is_file() and p.suffix == ".json" and not p.name.endswith(exclude_suffix)
    )


# ─────────────────────────────────────────────────────────────────────────────
# Argument parser
# ─────────────────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    """Build and return the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="python -m cdb_social.cli",
        description="LSB social publishing pipeline CLI.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress summary output (useful in cron context).",
    )

    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # ── run-once ──────────────────────────────────────────────────────────────
    run_once_parser = subparsers.add_parser(
        "run-once",
        help="Detect triggers, draft posts, and queue them in pending/.",
    )
    run_once_parser.add_argument(
        "--platform",
        default="bluesky",
        metavar="PLATFORMS",
        help=(
            "Comma-separated list of platforms to draft for "
            "(default: bluesky). Additional platforms are draft-only "
            "in Phase 7 v1 and will not be live-published."
        ),
    )
    run_once_parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress summary output.",
    )

    # ── review ────────────────────────────────────────────────────────────────
    review_parser = subparsers.add_parser(
        "review",
        help="Interactive review CLI (delegates to scripts/social_review.py).",
    )
    review_parser.add_argument(
        "review_args",
        nargs=argparse.REMAINDER,
        help="Arguments passed through to scripts/social_review.py.",
    )

    # ── publish ───────────────────────────────────────────────────────────────
    publish_parser = subparsers.add_parser(
        "publish",
        help="Drain approved/ → publisher → published/ or failed/.",
    )
    publish_parser.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        default=False,
        help=(
            "Skip real API calls. Writes DRY_RUN records to published/; "
            "does not post to any platform."
        ),
    )
    publish_parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress summary output.",
    )

    # ── status ────────────────────────────────────────────────────────────────
    status_parser = subparsers.add_parser(
        "status",
        help="Print counts per queue state.",
    )
    status_parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress output (useful for scripting).",
    )

    return parser


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    """Parse argv and dispatch to the appropriate subcommand handler.

    Returns the exit code.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    parser = build_parser()
    args = parser.parse_args(argv)

    subcommand = args.subcommand
    if subcommand == "run-once":
        return cmd_run_once(args)
    if subcommand == "review":
        return cmd_review(args)
    if subcommand == "publish":
        return cmd_publish(args)
    if subcommand == "status":
        return cmd_status(args)

    # Should not reach here — argparse enforces required subcommand
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
