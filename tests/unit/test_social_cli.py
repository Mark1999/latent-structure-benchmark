"""Unit tests for cdb_social/cli.py — Phase 7 T6.

No real API calls; all detectors, drafters, and publisher are monkeypatched.

Test classes:
  TestRunOnceSubcommand     — detector pipeline mocked; drafts land in pending/
  TestRunOnceDriftDisabled  — enable_drift=False is passed to detect_drift
  TestRunOnceDedupe         — triggers with known dedupe keys are skipped
  TestPublishSubcommand     — drains approved/ → publisher → published/ or failed/
  TestPublishDryRun         — --dry-run skips the real API
  TestPublishTransientRetained — PublisherTransientError leaves draft in approved/
  TestStatusSubcommand      — counts per queue state
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from cdb_core.schemas import (
    Platform,
    PublishStatus,
    SocialDraft,
    SocialPostRecord,
    SocialTrigger,
    TriggerType,
)

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _make_trigger(
    trigger_type: TriggerType = TriggerType.NEW_MODEL,
    domain_slug: str | None = "family",
    model_id: str | None = "test-model",
    dedupe_key: str = "abcdef0123456789",
) -> SocialTrigger:
    return SocialTrigger(
        trigger_type=trigger_type,
        detected_at=datetime(2026, 5, 17, 12, 0, 0, tzinfo=UTC),
        domain_slug=domain_slug,
        model_id=model_id,
        evidence={"first_seen_in_domain": domain_slug or "family"},
        dedupe_key=dedupe_key,
    )


def _make_draft(
    draft_id: str = "testdraftid1234",
    platform: Platform = Platform.BLUESKY,
    created_at: datetime | None = None,
) -> SocialDraft:
    return SocialDraft(
        draft_id=draft_id,
        trigger=_make_trigger(),
        platform=platform,
        text="Post about categorical structure patterns in corpus.",
        suggested_posting_time=datetime(2026, 5, 19, 14, 0, 0, tzinfo=UTC),
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
        drafter_version="bluesky-v1",
        prompt_version="v1",
        created_at=created_at or datetime(2026, 5, 17, 10, 0, 0, tzinfo=UTC),
    )


def _make_success_record(draft_id: str = "testdraftid1234") -> SocialPostRecord:
    return SocialPostRecord(
        draft_id=draft_id,
        published_at=datetime(2026, 5, 17, 14, 0, 0, tzinfo=UTC),
        platform_post_id="at://did:plc:abc/app.bsky.feed.post/rkey123",
        platform_post_url="https://bsky.app/profile/handle.bsky.social/post/rkey123",
        publish_status=PublishStatus.PUBLISHED,
        error_message=None,
    )


@pytest.fixture()
def queue_root(tmp_path: Path) -> Path:
    """Create a minimal queue directory tree."""
    root = tmp_path / "queue"
    for state in ("pending", "approved", "failed"):
        (root / state).mkdir(parents=True)
    (root / "published").mkdir(parents=True)
    return root


@pytest.fixture()
def state_dir(tmp_path: Path) -> Path:
    """Create a minimal state directory."""
    s = tmp_path / "state"
    s.mkdir(parents=True)
    return s


@pytest.fixture()
def data_dir(tmp_path: Path) -> Path:
    """Create a minimal data directory."""
    d = tmp_path / "data"
    d.mkdir(parents=True)
    return d


@pytest.fixture(autouse=True)
def _set_env(
    monkeypatch: pytest.MonkeyPatch,
    queue_root: Path,
    state_dir: Path,
    data_dir: Path,
) -> None:
    """Point CLI path helpers at tmp_path directories for all tests."""
    monkeypatch.setenv("LSB_SOCIAL_QUEUE_ROOT", str(queue_root))
    monkeypatch.setenv("LSB_SOCIAL_STATE_DIR", str(state_dir))
    monkeypatch.setenv("LSB_SOCIAL_DATA_DIR", str(data_dir))
    monkeypatch.setenv("BLUESKY_HANDLE", "testhandle.bsky.social")
    monkeypatch.setenv("BLUESKY_APP_PASSWORD", "test-app-password-xxxx")


# ─────────────────────────────────────────────────────────────────────────────
# TestRunOnceSubcommand
# ─────────────────────────────────────────────────────────────────────────────


class TestRunOnceSubcommand:
    """Detector pipeline mocked; accepted drafts land in pending/."""

    def test_run_once_writes_draft_to_pending(
        self,
        queue_root: Path,
        state_dir: Path,
        data_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """A single trigger produces one draft in pending/."""
        trigger = _make_trigger(dedupe_key="uniquekey12345")
        draft = _make_draft(draft_id="resultdraftid1")

        mock_drafter = MagicMock()
        mock_drafter.draft.return_value = draft

        with (
            patch("cdb_social.cli.detect_new_model", return_value=[trigger]),
            patch("cdb_social.cli.detect_new_domain", return_value=[]),
            patch("cdb_social.cli.detect_drift", return_value=[]),
            patch("cdb_social.cli.detect_divergence", return_value=[]),
            patch("cdb_social.cli.detect_monthly_roundup", return_value=[]),
            patch("cdb_social.cli._get_drafter", return_value=mock_drafter),
        ):
            from cdb_social.cli import main
            rc = main(["run-once"])

        assert rc == 0
        pending_files = list((queue_root / "pending").glob("*.json"))
        assert len(pending_files) == 1
        assert pending_files[0].name == "resultdraftid1.json"

    def test_run_once_prints_summary(
        self,
        queue_root: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """run-once prints trigger count, draft count, rejection count."""
        trigger = _make_trigger(dedupe_key="key_for_summary")
        draft = _make_draft()

        mock_drafter = MagicMock()
        mock_drafter.draft.return_value = draft

        with (
            patch("cdb_social.cli.detect_new_model", return_value=[trigger]),
            patch("cdb_social.cli.detect_new_domain", return_value=[]),
            patch("cdb_social.cli.detect_drift", return_value=[]),
            patch("cdb_social.cli.detect_divergence", return_value=[]),
            patch("cdb_social.cli.detect_monthly_roundup", return_value=[]),
            patch("cdb_social.cli._get_drafter", return_value=mock_drafter),
        ):
            from cdb_social.cli import main
            main(["run-once"])

        out = capsys.readouterr().out
        assert "triggers detected" in out
        assert "drafts written" in out
        assert "rejected" in out

    def test_run_once_rejected_draft_logged_not_crashed(
        self,
        queue_root: Path,
        state_dir: Path,
    ) -> None:
        """A DrafterRejectedException per-draft is logged; the run continues."""
        from cdb_social.drafters.base import DrafterRejectedException  # noqa: PLC0415

        trigger_ok = _make_trigger(dedupe_key="okkey111111111")
        trigger_bad = _make_trigger(dedupe_key="badkey22222222")
        draft_ok = _make_draft(draft_id="okdraftid12345")

        # First trigger: drafter rejects; second trigger: drafter accepts
        call_count = 0

        def drafter_side_effect(trig: SocialTrigger, dr: Any) -> SocialDraft:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise DrafterRejectedException("worldview detected", draft_text="bad text")
            return draft_ok

        mock_drafter = MagicMock()
        mock_drafter.draft.side_effect = drafter_side_effect

        with (
            patch("cdb_social.cli.detect_new_model", return_value=[trigger_bad, trigger_ok]),
            patch("cdb_social.cli.detect_new_domain", return_value=[]),
            patch("cdb_social.cli.detect_drift", return_value=[]),
            patch("cdb_social.cli.detect_divergence", return_value=[]),
            patch("cdb_social.cli.detect_monthly_roundup", return_value=[]),
            patch("cdb_social.cli._get_drafter", return_value=mock_drafter),
        ):
            from cdb_social.cli import main
            rc = main(["run-once"])

        assert rc == 0  # did not crash
        pending_files = list((queue_root / "pending").glob("*.json"))
        assert len(pending_files) == 1

    def test_run_once_zero_triggers_summary(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """run-once with no triggers prints '0 triggers detected'."""
        with (
            patch("cdb_social.cli.detect_new_model", return_value=[]),
            patch("cdb_social.cli.detect_new_domain", return_value=[]),
            patch("cdb_social.cli.detect_drift", return_value=[]),
            patch("cdb_social.cli.detect_divergence", return_value=[]),
            patch("cdb_social.cli.detect_monthly_roundup", return_value=[]),
        ):
            from cdb_social.cli import main
            rc = main(["run-once"])

        assert rc == 0
        out = capsys.readouterr().out
        assert "0 triggers detected" in out


# ─────────────────────────────────────────────────────────────────────────────
# TestRunOnceDriftDisabled
# ─────────────────────────────────────────────────────────────────────────────


class TestRunOnceDriftDisabled:
    """Drift trigger is always called with enable=False."""

    def test_detect_drift_called_with_enable_false(self) -> None:
        """detect_drift is always called with enable=False per kickoff §2 item 1."""
        with (
            patch("cdb_social.cli.detect_new_model", return_value=[]),
            patch("cdb_social.cli.detect_new_domain", return_value=[]),
            patch("cdb_social.cli.detect_drift", return_value=[]) as mock_drift,
            patch("cdb_social.cli.detect_divergence", return_value=[]),
            patch("cdb_social.cli.detect_monthly_roundup", return_value=[]),
        ):
            from cdb_social.cli import main
            main(["run-once"])

        # Verify detect_drift was called with enable=False
        mock_drift.assert_called_once()
        call_args = mock_drift.call_args
        # enable is passed as a keyword arg
        assert call_args.kwargs.get("enable") is False


# ─────────────────────────────────────────────────────────────────────────────
# TestRunOnceDedupe
# ─────────────────────────────────────────────────────────────────────────────


class TestRunOnceDedupe:
    """Triggers with dedupe_key already in posted_dedupe_keys.json are skipped."""

    def test_known_dedupe_key_is_skipped(
        self,
        state_dir: Path,
        queue_root: Path,
    ) -> None:
        """A trigger whose dedupe_key is in posted_dedupe_keys.json is not drafted."""
        known_key = "alreadypostedkey"
        # Write the dedupe state file with the known key
        dedupe_path = state_dir / "posted_dedupe_keys.json"
        dedupe_path.write_text(
            json.dumps({"keys": [known_key]}),
            encoding="utf-8",
        )

        trigger = _make_trigger(dedupe_key=known_key)
        mock_drafter = MagicMock()

        with (
            patch("cdb_social.cli.detect_new_model", return_value=[trigger]),
            patch("cdb_social.cli.detect_new_domain", return_value=[]),
            patch("cdb_social.cli.detect_drift", return_value=[]),
            patch("cdb_social.cli.detect_divergence", return_value=[]),
            patch("cdb_social.cli.detect_monthly_roundup", return_value=[]),
            patch("cdb_social.cli._get_drafter", return_value=mock_drafter),
        ):
            from cdb_social.cli import main
            rc = main(["run-once"])

        assert rc == 0
        # Drafter should not have been called for the deduplicated trigger
        mock_drafter.draft.assert_not_called()
        # Pending queue should be empty
        assert list((queue_root / "pending").glob("*.json")) == []

    def test_new_trigger_not_in_dedupe_is_drafted(
        self,
        state_dir: Path,
        queue_root: Path,
    ) -> None:
        """A trigger with a novel dedupe_key proceeds through the drafter."""
        known_key = "alreadypostedkey"
        new_key = "brandnewuniq1234"
        dedupe_path = state_dir / "posted_dedupe_keys.json"
        dedupe_path.write_text(
            json.dumps({"keys": [known_key]}),
            encoding="utf-8",
        )

        trigger = _make_trigger(dedupe_key=new_key)
        draft = _make_draft(draft_id="newdraftfromnew")
        mock_drafter = MagicMock()
        mock_drafter.draft.return_value = draft

        with (
            patch("cdb_social.cli.detect_new_model", return_value=[trigger]),
            patch("cdb_social.cli.detect_new_domain", return_value=[]),
            patch("cdb_social.cli.detect_drift", return_value=[]),
            patch("cdb_social.cli.detect_divergence", return_value=[]),
            patch("cdb_social.cli.detect_monthly_roundup", return_value=[]),
            patch("cdb_social.cli._get_drafter", return_value=mock_drafter),
        ):
            from cdb_social.cli import main
            main(["run-once"])

        pending = list((queue_root / "pending").glob("*.json"))
        assert len(pending) == 1


# ─────────────────────────────────────────────────────────────────────────────
# TestPublishSubcommand
# ─────────────────────────────────────────────────────────────────────────────


class TestPublishSubcommand:
    """Drains approved/ → publisher → published/ or failed/."""

    def test_successful_publish_moves_to_published(
        self,
        queue_root: Path,
        state_dir: Path,
    ) -> None:
        """A successful publish moves the draft from approved/ to published/YYYY-MM/."""
        draft = _make_draft("successdraft123")
        draft_path = queue_root / "approved" / "successdraft123.json"
        draft_path.write_text(draft.model_dump_json(), encoding="utf-8")

        record = _make_success_record("successdraft123")

        with patch("cdb_social.cli.publish", return_value=record):
            from cdb_social.cli import main
            rc = main(["publish"])

        assert rc == 0
        assert not draft_path.exists()
        # Should be in some published/YYYY-MM/ subdir
        published_files = list((queue_root / "published").rglob("*.json"))
        # Exclude .record.json sidecars
        draft_files = [f for f in published_files if not f.name.endswith(".record.json")]
        assert len(draft_files) == 1

    def test_successful_publish_writes_record_sidecar(
        self,
        queue_root: Path,
    ) -> None:
        """A .record.json sidecar is written alongside the draft in published/."""
        draft = _make_draft("sidecard123456")
        draft_path = queue_root / "approved" / "sidecard123456.json"
        draft_path.write_text(draft.model_dump_json(), encoding="utf-8")

        record = _make_success_record("sidecard123456")

        with patch("cdb_social.cli.publish", return_value=record):
            from cdb_social.cli import main
            main(["publish"])

        record_files = list((queue_root / "published").rglob("*.record.json"))
        assert len(record_files) == 1

    def test_not_enabled_moves_to_failed(
        self,
        queue_root: Path,
    ) -> None:
        """PublisherNotEnabled moves the draft to failed/."""
        from cdb_social.publisher import PublisherNotEnabled  # noqa: PLC0415

        draft = _make_draft("xdraftfail0001", platform=Platform.X)
        draft_path = queue_root / "approved" / "xdraftfail0001.json"
        draft_path.write_text(draft.model_dump_json(), encoding="utf-8")

        with patch("cdb_social.cli.publish", side_effect=PublisherNotEnabled("not enabled")):
            from cdb_social.cli import main
            rc = main(["publish"])

        assert rc == 0
        assert not draft_path.exists()
        failed_files = list((queue_root / "failed").glob("*.json"))
        assert any(f.name == "xdraftfail0001.json" for f in failed_files)

    def test_terminal_error_moves_to_failed(
        self,
        queue_root: Path,
    ) -> None:
        """PublisherTerminalError moves the draft to failed/ with error message."""
        from cdb_social.publisher import PublisherTerminalError  # noqa: PLC0415

        draft = _make_draft("terminaldraft01")
        draft_path = queue_root / "approved" / "terminaldraft01.json"
        draft_path.write_text(draft.model_dump_json(), encoding="utf-8")

        with patch(
            "cdb_social.cli.publish",
            side_effect=PublisherTerminalError("401 auth failure"),
        ):
            from cdb_social.cli import main
            rc = main(["publish"])

        assert rc == 0
        failed_files = list((queue_root / "failed").glob("*.json"))
        assert any(f.name == "terminaldraft01.json" for f in failed_files)

    def test_publish_prints_summary(
        self,
        queue_root: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """publish prints succeeded/failed/retry counts."""
        draft = _make_draft("summarytest123")
        draft_path = queue_root / "approved" / "summarytest123.json"
        draft_path.write_text(draft.model_dump_json(), encoding="utf-8")

        record = _make_success_record("summarytest123")

        with patch("cdb_social.cli.publish", return_value=record):
            from cdb_social.cli import main
            main(["publish"])

        out = capsys.readouterr().out
        assert "succeeded" in out
        assert "failed" in out
        assert "retry" in out

    def test_empty_approved_queue_prints_zero_success(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """When approved/ is empty, publish prints 0/0 succeeded."""
        from cdb_social.cli import main
        main(["publish"])

        out = capsys.readouterr().out
        assert "0/0" in out


# ─────────────────────────────────────────────────────────────────────────────
# TestPublishDryRun
# ─────────────────────────────────────────────────────────────────────────────


class TestPublishDryRun:
    """--dry-run skips the real API and writes DRY_RUN records."""

    def test_dry_run_passes_flag_to_publisher(
        self,
        queue_root: Path,
    ) -> None:
        """publish() is called with dry_run=True when --dry-run is set."""
        draft = _make_draft("dryruntest0001")
        draft_path = queue_root / "approved" / "dryruntest0001.json"
        draft_path.write_text(draft.model_dump_json(), encoding="utf-8")

        dry_run_record = SocialPostRecord(
            draft_id="dryruntest0001",
            published_at=datetime.now(UTC),
            platform_post_id="at://dry-run",
            platform_post_url="https://bsky.app/profile/handle/post/dry",
            publish_status=PublishStatus.DRY_RUN,
            error_message=None,
        )

        with patch("cdb_social.cli.publish", return_value=dry_run_record) as mock_pub:
            from cdb_social.cli import main
            main(["publish", "--dry-run"])

        # Verify dry_run=True was passed
        call_kwargs = mock_pub.call_args.kwargs
        assert call_kwargs.get("dry_run") is True

    def test_dry_run_draft_moves_to_published(
        self,
        queue_root: Path,
    ) -> None:
        """dry-run records are moved to published/ (not failed/)."""
        draft = _make_draft("dryruntomove11")
        draft_path = queue_root / "approved" / "dryruntomove11.json"
        draft_path.write_text(draft.model_dump_json(), encoding="utf-8")

        dry_run_record = SocialPostRecord(
            draft_id="dryruntomove11",
            published_at=datetime.now(UTC),
            publish_status=PublishStatus.DRY_RUN,
        )

        with patch("cdb_social.cli.publish", return_value=dry_run_record):
            from cdb_social.cli import main
            main(["publish", "--dry-run"])

        assert not draft_path.exists()
        published_drafts = [
            f for f in (queue_root / "published").rglob("*.json")
            if not f.name.endswith(".record.json")
        ]
        assert len(published_drafts) == 1


# ─────────────────────────────────────────────────────────────────────────────
# TestPublishTransientRetained
# ─────────────────────────────────────────────────────────────────────────────


class TestPublishTransientRetained:
    """PublisherTransientError leaves the draft in approved/ and logs to retries."""

    def test_transient_draft_stays_in_approved(
        self,
        queue_root: Path,
        state_dir: Path,
    ) -> None:
        """A transient error leaves the draft in approved/ for retry."""
        from cdb_social.publisher import PublisherTransientError  # noqa: PLC0415

        draft = _make_draft("transient001234")
        draft_path = queue_root / "approved" / "transient001234.json"
        draft_path.write_text(draft.model_dump_json(), encoding="utf-8")

        with patch(
            "cdb_social.cli.publish",
            side_effect=PublisherTransientError("503 Service Unavailable"),
        ):
            from cdb_social.cli import main
            rc = main(["publish"])

        assert rc == 0
        # Draft must still be in approved/
        assert draft_path.exists(), "Transient-error draft must remain in approved/"
        # Not in published or failed
        assert not (queue_root / "failed" / "transient001234.json").exists()

    def test_transient_retry_logged_to_jsonl(
        self,
        queue_root: Path,
        state_dir: Path,
    ) -> None:
        """A transient error appends a record to publish_retries.jsonl."""
        from cdb_social.publisher import PublisherTransientError  # noqa: PLC0415

        draft = _make_draft("transientlog001")
        draft_path = queue_root / "approved" / "transientlog001.json"
        draft_path.write_text(draft.model_dump_json(), encoding="utf-8")

        with patch(
            "cdb_social.cli.publish",
            side_effect=PublisherTransientError("503 upstream timeout"),
        ):
            from cdb_social.cli import main
            main(["publish"])

        retry_log = state_dir / "publish_retries.jsonl"
        assert retry_log.exists(), "publish_retries.jsonl must exist after transient error"
        lines = [json.loads(line) for line in retry_log.read_text().splitlines()]
        assert len(lines) == 1
        assert lines[0]["draft_id"] == "transientlog001"
        assert "503" in lines[0]["error_message"]

    def test_transient_summary_shows_retry_count(
        self,
        queue_root: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """The publish summary shows retry count when transient error occurs."""
        from cdb_social.publisher import PublisherTransientError  # noqa: PLC0415

        draft = _make_draft("transientsum001")
        draft_path = queue_root / "approved" / "transientsum001.json"
        draft_path.write_text(draft.model_dump_json(), encoding="utf-8")

        with patch(
            "cdb_social.cli.publish",
            side_effect=PublisherTransientError("timeout"),
        ):
            from cdb_social.cli import main
            main(["publish"])

        out = capsys.readouterr().out
        assert "1 marked for retry" in out


# ─────────────────────────────────────────────────────────────────────────────
# TestStatusSubcommand
# ─────────────────────────────────────────────────────────────────────────────


class TestStatusSubcommand:
    """counts per queue state correctly."""

    def test_status_empty_queue(
        self,
        queue_root: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Empty queue shows all zeros."""
        from cdb_social.cli import main
        rc = main(["status"])

        assert rc == 0
        out = capsys.readouterr().out
        assert "pending:" in out
        assert "approved:" in out
        assert "failed:" in out
        assert "published (total):" in out

    def test_status_counts_pending(
        self,
        queue_root: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """status counts files in pending/."""
        draft = _make_draft("pendingcount001")
        (queue_root / "pending" / "pendingcount001.json").write_text(
            draft.model_dump_json(), encoding="utf-8"
        )

        from cdb_social.cli import main
        main(["status"])

        out = capsys.readouterr().out
        # "pending:           1"
        assert "pending:" in out
        lines = {
            ln.split(":")[0].strip(): ln.split(":")[1].strip()
            for ln in out.splitlines()
            if ":" in ln
        }
        assert lines.get("pending") == "1"

    def test_status_counts_approved(
        self,
        queue_root: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """status counts files in approved/."""
        for i in range(3):
            draft = _make_draft(f"approveddraft{i:02d}")
            (queue_root / "approved" / f"approveddraft{i:02d}.json").write_text(
                draft.model_dump_json(), encoding="utf-8"
            )

        from cdb_social.cli import main
        main(["status"])

        out = capsys.readouterr().out
        lines = {
            ln.split(":")[0].strip(): ln.split(":")[1].strip()
            for ln in out.splitlines()
            if ":" in ln
        }
        assert lines.get("approved") == "3"

    def test_status_counts_published_total_and_this_month(
        self,
        queue_root: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """status counts published/ subdirs, distinguishing this month."""
        from cdb_social.cli import main  # noqa: PLC0415
        now = datetime.now(UTC)
        this_month = now.strftime("%Y-%m")
        prev_month = f"{now.year}-{now.month - 1:02d}" if now.month > 1 else f"{now.year - 1}-12"

        # 2 in this month, 1 in previous month
        (queue_root / "published" / this_month).mkdir(parents=True, exist_ok=True)
        (queue_root / "published" / prev_month).mkdir(parents=True, exist_ok=True)

        draft_a = _make_draft("publishedthism1")
        draft_b = _make_draft("publishedthism2")
        draft_c = _make_draft("publishedprevmo")

        (queue_root / "published" / this_month / "publishedthism1.json").write_text(
            draft_a.model_dump_json(), encoding="utf-8"
        )
        (queue_root / "published" / this_month / "publishedthism2.json").write_text(
            draft_b.model_dump_json(), encoding="utf-8"
        )
        (queue_root / "published" / prev_month / "publishedprevmo.json").write_text(
            draft_c.model_dump_json(), encoding="utf-8"
        )

        main(["status"])

        out = capsys.readouterr().out
        assert "published (total): 3" in out
        assert "this month: 2" in out

    def test_status_excludes_record_sidecars(
        self,
        queue_root: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """status excludes .record.json sidecar files from counts."""
        (queue_root / "failed" / "fdraft00001.json").write_text("{}", encoding="utf-8")
        (queue_root / "failed" / "fdraft00001.record.json").write_text("{}", encoding="utf-8")

        from cdb_social.cli import main
        main(["status"])

        out = capsys.readouterr().out
        lines = {
            ln.split(":")[0].strip(): ln.split(":")[1].strip()
            for ln in out.splitlines()
            if ":" in ln
        }
        assert lines.get("failed") == "1"  # not 2

    def test_status_returns_zero(self, queue_root: Path) -> None:
        """status returns exit code 0."""
        from cdb_social.cli import main
        assert main(["status"]) == 0
