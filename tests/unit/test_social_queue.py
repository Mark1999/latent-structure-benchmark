"""Unit tests for cdb_social/queue.py — Phase 7 T5.

Tests organised by test class:
  TestQueueMove           — atomic moves between states
  TestQueueMoveWrongState — raises WrongQueueStateError for wrong from_state
  TestQueueListPending    — oldest-first sort by created_at
  TestQueueLoadSave       — round-trip a SocialDraft through disk
  TestQueueAtomicity      — save_draft uses tempfile+os.replace; no partial writes
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from cdb_core.schemas import Platform, SocialDraft, SocialTrigger, TriggerType
from cdb_social.queue import (
    DraftNotFoundError,
    WrongQueueStateError,
    list_pending,
    load_draft,
    move,
    save_draft,
)

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


def _make_trigger(
    trigger_type: TriggerType = TriggerType.NEW_MODEL,
    domain_slug: str | None = "family",
    model_id: str | None = "test-model-1",
    evidence: dict | None = None,
    dedupe_key: str = "abcdef0123456789",
) -> SocialTrigger:
    return SocialTrigger(
        trigger_type=trigger_type,
        detected_at=datetime(2026, 5, 17, 12, 0, 0, tzinfo=UTC),
        domain_slug=domain_slug,
        model_id=model_id,
        evidence=evidence or {"first_seen_in_domain": "family"},
        dedupe_key=dedupe_key,
    )


def _make_draft(
    draft_id: str = "draft_a1b2c3d4",
    created_at: datetime | None = None,
    text: str = "Test post text about corpus lens patterns.",
) -> SocialDraft:
    return SocialDraft(
        draft_id=draft_id,
        trigger=_make_trigger(),
        platform=Platform.BLUESKY,
        text=text,
        suggested_posting_time=datetime(2026, 5, 17, 14, 0, 0, tzinfo=UTC),
        drafter_self_rating=0.5,
        methodology_url="https://cogstructurelab.com/family",
        dashboard_url="https://cogstructurelab.com/family",
        framing_check_passed=True,
        framing_checks={
            "hypothesis_framing": True,
            "cognition_attribution": True,
            "bare_numeric_without_ci": True,
            "register_boundary": True,
        },
        drafter_version="v1",
        prompt_version="v1",
        created_at=created_at or datetime(2026, 5, 17, 10, 0, 0, tzinfo=UTC),
    )


@pytest.fixture()
def queue_root(tmp_path: Path) -> Path:
    """Create a minimal queue directory tree under tmp_path."""
    root = tmp_path / "queue"
    for state in ("pending", "approved", "failed"):
        (root / state).mkdir(parents=True)
    (root / "published").mkdir(parents=True)
    return root


# ─────────────────────────────────────────────────────────────────────────────
# TestQueueMove
# ─────────────────────────────────────────────────────────────────────────────


class TestQueueMove:
    """Atomic moves between queue states."""

    def test_pending_to_approved(self, queue_root: Path) -> None:
        """Move a draft from pending/ to approved/."""
        draft = _make_draft("draft_pa01")
        src = queue_root / "pending" / "draft_pa01.json"
        save_draft(draft, src)
        assert src.exists()

        new_path = move("draft_pa01", "pending", "approved", queue_root=queue_root)

        assert not src.exists(), "Source should be gone after move."
        assert new_path.exists(), "Destination should exist."
        assert new_path.parent.name == "approved"
        assert new_path.name == "draft_pa01.json"

    def test_approved_to_published(self, queue_root: Path) -> None:
        """Move from approved/ to published/ creates a YYYY-MM subdirectory."""
        draft = _make_draft("draft_ap01")
        src = queue_root / "approved" / "draft_ap01.json"
        save_draft(draft, src)
        assert src.exists()

        new_path = move("draft_ap01", "approved", "published", queue_root=queue_root)

        assert not src.exists()
        assert new_path.exists()
        # YYYY-MM subdirectory should be present.
        assert new_path.parent.parent.name == "published"
        subdir = new_path.parent.name
        assert len(subdir) == 7, f"Expected YYYY-MM, got {subdir!r}"
        assert "-" in subdir

    def test_pending_to_failed(self, queue_root: Path) -> None:
        """Move a draft from pending/ to failed/."""
        draft = _make_draft("draft_pf01")
        src = queue_root / "pending" / "draft_pf01.json"
        save_draft(draft, src)

        new_path = move("draft_pf01", "pending", "failed", queue_root=queue_root)

        assert not src.exists()
        assert new_path.exists()
        assert new_path.parent.name == "failed"

    def test_move_returns_new_path(self, queue_root: Path) -> None:
        """move() returns the new path of the moved file."""
        draft = _make_draft("draft_rp01")
        save_draft(draft, queue_root / "pending" / "draft_rp01.json")

        result = move("draft_rp01", "pending", "approved", queue_root=queue_root)

        assert isinstance(result, Path)
        assert result.name == "draft_rp01.json"
        assert result.exists()

    def test_draft_content_preserved(self, queue_root: Path) -> None:
        """The JSON content is identical after a move."""
        draft = _make_draft("draft_cp01", text="Unique content for copy check.")
        save_draft(draft, queue_root / "pending" / "draft_cp01.json")

        new_path = move("draft_cp01", "pending", "approved", queue_root=queue_root)

        reloaded = load_draft(new_path)
        assert reloaded.text == "Unique content for copy check."
        assert reloaded.draft_id == "draft_cp01"


# ─────────────────────────────────────────────────────────────────────────────
# TestQueueMoveWrongState
# ─────────────────────────────────────────────────────────────────────────────


class TestQueueMoveWrongState:
    """WrongQueueStateError raised when draft is not in from_state."""

    def test_wrong_state_raises(self, queue_root: Path) -> None:
        """WrongQueueStateError when draft is in approved/ but from_state=pending."""
        draft = _make_draft("draft_ws01")
        save_draft(draft, queue_root / "approved" / "draft_ws01.json")

        with pytest.raises(WrongQueueStateError):
            move("draft_ws01", "pending", "failed", queue_root=queue_root)

    def test_not_found_raises(self, queue_root: Path) -> None:
        """DraftNotFoundError when draft_id doesn't exist in any state."""
        with pytest.raises(DraftNotFoundError):
            move("nonexistent_id", "pending", "approved", queue_root=queue_root)

    def test_draft_unmoved_on_wrong_state(self, queue_root: Path) -> None:
        """The draft stays where it is when WrongQueueStateError is raised."""
        draft = _make_draft("draft_un01")
        approved_path = queue_root / "approved" / "draft_un01.json"
        save_draft(draft, approved_path)

        with pytest.raises(WrongQueueStateError):
            move("draft_un01", "pending", "failed", queue_root=queue_root)

        # Draft should still be in approved/.
        assert approved_path.exists()


# ─────────────────────────────────────────────────────────────────────────────
# TestQueueListPending
# ─────────────────────────────────────────────────────────────────────────────


class TestQueueListPending:
    """list_pending() returns oldest-first sort by created_at."""

    def test_oldest_first(self, queue_root: Path) -> None:
        """Drafts are sorted by created_at ascending."""
        base = datetime(2026, 5, 1, 0, 0, 0, tzinfo=UTC)
        drafts = [
            _make_draft("draft_old3", created_at=base + timedelta(hours=3)),
            _make_draft("draft_old1", created_at=base + timedelta(hours=1)),
            _make_draft("draft_old2", created_at=base + timedelta(hours=2)),
        ]
        for d in drafts:
            save_draft(d, queue_root / "pending" / f"{d.draft_id}.json")

        result = list_pending(queue_root)
        ids = [p.stem for p in result]

        assert ids == ["draft_old1", "draft_old2", "draft_old3"]

    def test_empty_pending(self, queue_root: Path) -> None:
        """list_pending() returns [] when pending/ is empty."""
        result = list_pending(queue_root)
        assert result == []

    def test_single_draft(self, queue_root: Path) -> None:
        """Single draft returns a one-element list."""
        draft = _make_draft("draft_single")
        save_draft(draft, queue_root / "pending" / "draft_single.json")

        result = list_pending(queue_root)
        assert len(result) == 1
        assert result[0].name == "draft_single.json"

    def test_nonexistent_pending_dir(self, tmp_path: Path) -> None:
        """list_pending() returns [] when pending/ doesn't exist."""
        queue_root = tmp_path / "queue"
        queue_root.mkdir()
        # No pending/ subdirectory.
        result = list_pending(queue_root)
        assert result == []

    def test_returns_paths(self, queue_root: Path) -> None:
        """list_pending() returns Path objects."""
        draft = _make_draft("draft_pth1")
        save_draft(draft, queue_root / "pending" / "draft_pth1.json")

        result = list_pending(queue_root)
        assert all(isinstance(p, Path) for p in result)


# ─────────────────────────────────────────────────────────────────────────────
# TestQueueLoadSave
# ─────────────────────────────────────────────────────────────────────────────


class TestQueueLoadSave:
    """Round-trip a SocialDraft through disk."""

    def test_round_trip(self, queue_root: Path) -> None:
        """save_draft + load_draft produces an equivalent SocialDraft."""
        draft = _make_draft(
            "draft_rt01",
            text="Round-trip test post with corpus lens patterns.",
        )
        path = queue_root / "pending" / "draft_rt01.json"

        save_draft(draft, path)
        loaded = load_draft(path)

        assert loaded.draft_id == draft.draft_id
        assert loaded.text == draft.text
        assert loaded.platform == draft.platform
        assert loaded.framing_check_passed == draft.framing_check_passed
        assert loaded.framing_checks == draft.framing_checks
        assert loaded.created_at == draft.created_at

    def test_text_history_preserved(self, queue_root: Path) -> None:
        """text_history list is round-tripped correctly."""
        draft = _make_draft("draft_th01")
        draft_with_history = draft.model_copy(
            update={"text_history": ["original text v0", "edit attempt 1"]}
        )
        path = queue_root / "pending" / "draft_th01.json"
        save_draft(draft_with_history, path)
        loaded = load_draft(path)

        assert loaded.text_history == ["original text v0", "edit attempt 1"]

    def test_save_creates_parent_dirs(self, tmp_path: Path) -> None:
        """save_draft creates parent directories if they don't exist."""
        deep_path = tmp_path / "a" / "b" / "c" / "draft.json"
        draft = _make_draft("draft_deep01")
        save_draft(draft, deep_path)
        assert deep_path.exists()

    def test_load_missing_raises(self, queue_root: Path) -> None:
        """load_draft raises FileNotFoundError for a non-existent path."""
        with pytest.raises(FileNotFoundError):
            load_draft(queue_root / "pending" / "nonexistent.json")

    def test_json_is_valid(self, queue_root: Path) -> None:
        """save_draft writes valid JSON."""
        draft = _make_draft("draft_json01")
        path = queue_root / "pending" / "draft_json01.json"
        save_draft(draft, path)
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)  # Should not raise.
        assert data["draft_id"] == "draft_json01"


# ─────────────────────────────────────────────────────────────────────────────
# TestQueueAtomicity
# ─────────────────────────────────────────────────────────────────────────────


class TestQueueAtomicity:
    """save_draft uses tempfile + os.replace; concurrent readers see a complete file."""

    def test_no_partial_write(self, queue_root: Path) -> None:
        """After save_draft, the target path is either absent or complete JSON.

        This test simulates the atomicity guarantee: there is no intermediate
        state where the target exists but is empty or partial.  We verify by
        reading the file immediately after write and confirming it parses fully.
        """
        draft = _make_draft("draft_atom01")
        path = queue_root / "pending" / "draft_atom01.json"

        save_draft(draft, path)

        # Immediately read back — should be complete.
        raw = path.read_text(encoding="utf-8")
        assert len(raw) > 0, "File should not be empty."
        data = json.loads(raw)  # Should not raise.
        assert data["draft_id"] == "draft_atom01"

    def test_overwrite_is_atomic(self, queue_root: Path) -> None:
        """Overwriting an existing draft via save_draft replaces atomically."""
        path = queue_root / "pending" / "draft_ow01.json"

        draft_v1 = _make_draft("draft_ow01", text="Version 1 text.")
        save_draft(draft_v1, path)

        draft_v2 = draft_v1.model_copy(update={"text": "Version 2 text."})
        save_draft(draft_v2, path)

        loaded = load_draft(path)
        assert loaded.text == "Version 2 text.", "Overwrite should produce v2 content."

    def test_no_tempfile_residue(self, queue_root: Path) -> None:
        """No .tmp files remain after a successful save_draft."""
        draft = _make_draft("draft_tmp01")
        path = queue_root / "pending" / "draft_tmp01.json"

        save_draft(draft, path)

        tmp_files = list(path.parent.glob("*.tmp"))
        assert tmp_files == [], f"Residual .tmp files found: {tmp_files}"
