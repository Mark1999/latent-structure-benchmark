"""Social post approval queue — atomic state-move helpers.

See ARCHITECTURE.md §4.6 and docs/DATA_DICTIONARY.md §13.

Queue states:
    pending   → SocialDraft awaiting Mark's review
    approved  → SocialDraft reviewed and approved; ready to publish
    published → SocialPostRecord for a successfully published post
                (stored in YYYY-MM subdirectories)
    failed    → SocialDraft or SocialPostRecord for rejected / failed posts

Moves are atomic via os.rename within the same filesystem (POSIX-atomic).
No half-state is possible if the process is interrupted mid-move because
os.rename is atomic at the filesystem level.

The published/ directory is special: posts are stored in YYYY-MM
subdirectories (e.g., published/2026-05/abc123.json) to prevent directory
bloat over time.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from cdb_core.schemas import SocialDraft

QUEUE_STATES = ("pending", "approved", "published", "failed")


class WrongQueueStateError(Exception):
    """Raised when attempting to move a draft from a state it is not in."""


class DraftNotFoundError(Exception):
    """Raised when the draft_id is not present in the from_state directory."""


def _pending_path(draft_id: str, queue_root: Path) -> Path:
    return queue_root / "pending" / f"{draft_id}.json"


def _approved_path(draft_id: str, queue_root: Path) -> Path:
    return queue_root / "approved" / f"{draft_id}.json"


def _failed_path(draft_id: str, queue_root: Path) -> Path:
    return queue_root / "failed" / f"{draft_id}.json"


def _published_path(draft_id: str, queue_root: Path, *, when: datetime | None = None) -> Path:
    """Return the published/ path for a draft.

    Uses the given datetime (or now) to construct the YYYY-MM subdirectory.
    """
    ts = when or datetime.now(UTC)
    subdir = ts.strftime("%Y-%m")
    return queue_root / "published" / subdir / f"{draft_id}.json"


def _find_published_path(draft_id: str, queue_root: Path) -> Path | None:
    """Search published/ subdirectories for an existing draft file."""
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


def _state_path(draft_id: str, state: str, queue_root: Path) -> Path | None:
    """Return the path for draft_id in state, or None if not found.

    For published/, searches all YYYY-MM subdirectories.
    """
    if state == "pending":
        p = _pending_path(draft_id, queue_root)
        return p if p.exists() else None
    if state == "approved":
        p = _approved_path(draft_id, queue_root)
        return p if p.exists() else None
    if state == "failed":
        p = _failed_path(draft_id, queue_root)
        return p if p.exists() else None
    if state == "published":
        return _find_published_path(draft_id, queue_root)
    raise ValueError(f"Unknown queue state: {state!r}. Must be one of {QUEUE_STATES!r}")


def move(
    draft_id: str,
    from_state: str,
    to_state: str,
    *,
    queue_root: Path,
) -> Path:
    """Atomically move a draft from one queue state to another.

    Uses os.rename within the same filesystem (atomic on POSIX).

    Raises WrongQueueStateError if the draft is not found in from_state.
    Raises DraftNotFoundError if the draft_id does not exist at all.
    Returns the new path.

    published/ is special: moves to published write to
    published/{YYYY-MM}/{draft_id}.json using the current UTC datetime.
    """
    if from_state not in QUEUE_STATES:
        raise ValueError(f"Unknown from_state: {from_state!r}")
    if to_state not in QUEUE_STATES:
        raise ValueError(f"Unknown to_state: {to_state!r}")

    src = _state_path(draft_id, from_state, queue_root)
    if src is None:
        # Check if it exists in another state to distinguish wrong-state from not-found.
        found_elsewhere = any(
            _state_path(draft_id, s, queue_root) is not None
            for s in QUEUE_STATES
            if s != from_state
        )
        if found_elsewhere:
            raise WrongQueueStateError(
                f"Draft {draft_id!r} is not in state {from_state!r}."
            )
        raise DraftNotFoundError(f"Draft {draft_id!r} not found in any queue state.")

    # Determine destination path.
    if to_state == "published":
        dest = _published_path(draft_id, queue_root)
    elif to_state == "pending":
        dest = _pending_path(draft_id, queue_root)
    elif to_state == "approved":
        dest = _approved_path(draft_id, queue_root)
    else:  # failed
        dest = _failed_path(draft_id, queue_root)

    dest.parent.mkdir(parents=True, exist_ok=True)
    os.rename(src, dest)
    return dest


def list_pending(queue_root: Path) -> list[Path]:
    """Return paths to all pending drafts, sorted oldest-first by created_at.

    Drafts that cannot be parsed are sorted to the end (by path name as
    fallback) so the queue is never silently blocked by a malformed entry.
    """
    pending_dir = queue_root / "pending"
    if not pending_dir.exists():
        return []

    paths = list(pending_dir.glob("*.json"))
    if not paths:
        return []

    def _sort_key(p: Path) -> tuple[int, str]:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            # Parse ISO-8601 datetime; fallback to epoch if missing.
            raw = data.get("created_at", "")
            dt = datetime.fromisoformat(raw) if raw else datetime.fromtimestamp(0, tz=UTC)
            # Convert to sortable integer (Unix timestamp in microseconds).
            return (int(dt.timestamp() * 1_000_000), p.name)
        except Exception:
            return (int(datetime(9999, 12, 31, tzinfo=UTC).timestamp() * 1_000_000), p.name)

    return sorted(paths, key=_sort_key)


def list_approved(queue_root: Path) -> list[Path]:
    """Return paths to all approved drafts, sorted oldest-first by created_at.

    Drafts that cannot be parsed are sorted to the end (by path name as
    fallback) so the publish pass is never silently blocked by a malformed entry.
    """
    approved_dir = queue_root / "approved"
    if not approved_dir.exists():
        return []

    paths = list(approved_dir.glob("*.json"))
    if not paths:
        return []

    def _sort_key(p: Path) -> tuple[int, str]:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            raw = data.get("created_at", "")
            dt = datetime.fromisoformat(raw) if raw else datetime.fromtimestamp(0, tz=UTC)
            return (int(dt.timestamp() * 1_000_000), p.name)
        except Exception:
            return (int(datetime(9999, 12, 31, tzinfo=UTC).timestamp() * 1_000_000), p.name)

    return sorted(paths, key=_sort_key)


def load_draft(path: Path) -> SocialDraft:
    """Load and validate a SocialDraft from disk.

    Raises pydantic.ValidationError if the JSON does not conform to SocialDraft.
    Raises FileNotFoundError if path does not exist.
    Raises json.JSONDecodeError if the file is not valid JSON.
    """
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    return SocialDraft.model_validate(data)


def save_draft(draft: SocialDraft, path: Path) -> None:
    """Atomically write a SocialDraft to path.

    Uses a tempfile in the same directory + os.replace for atomicity.
    Concurrent readers see either the old version or the new version —
    never a partial write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = draft.model_dump_json(indent=2)

    # Write to a tempfile in the same directory so os.replace is atomic
    # (same filesystem guaranteed).
    import contextlib

    fd, tmp_path_str = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    tmp_path = Path(tmp_path_str)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(payload)
        os.replace(tmp_path, path)
    except Exception:
        # Best-effort cleanup on failure.
        with contextlib.suppress(OSError):
            tmp_path.unlink(missing_ok=True)
        raise
