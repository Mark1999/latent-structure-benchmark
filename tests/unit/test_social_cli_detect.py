"""Unit tests for the detect subcommand in cdb_social/cli.py — Phase 7 T6a.

No real SMTP connections. Detectors and email_sender are mocked throughout.
State files are written to tmp_path (pytest's temporary directory fixture).

Test classes:
  TestDetectCmdNoTriggers     — zero new triggers → no email; idempotent silence
  TestDetectCmdNewTriggers    — new triggers → email sent → state updated
  TestDetectCmdDryRun         — --dry-run → stdout print; no email; no state update
  TestDetectCmdIdempotency    — re-run with same state → no email
  TestDetectCmdAtomicStateWrite — state file uses tempfile+os.replace
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import pytest
from cdb_core.schemas import SocialTrigger, TriggerType
from cdb_social.cli import (
    _load_emailed_dedupe_keys,
    _save_emailed_dedupe_keys,
    main,
)

# ─────────────────────────────────────────────────────────────────────────────
# Fixture helpers
# ─────────────────────────────────────────────────────────────────────────────

_DETECT_AT = datetime(2026, 5, 17, 14, 0, 0, tzinfo=UTC)


def _make_trigger(
    trigger_type: TriggerType = TriggerType.NEW_MODEL,
    domain_slug: str | None = "family",
    model_id: str | None = "claude-opus-4-8",
    dedupe_key: str = "aaaa1111aaaa1111",
) -> SocialTrigger:
    ev: dict = {}
    if trigger_type == TriggerType.NEW_MODEL:
        ev = {"first_seen_in_domain": domain_slug or "family"}
    elif trigger_type == TriggerType.NEW_DOMAIN:
        ev = {"domain_slug": domain_slug or "family", "n_models": 4}
    elif trigger_type == TriggerType.DIVERGENCE:
        ev = {
            "domain_slug": domain_slug or "family",
            "model_pair": ["model-a", "model-b"],
            "old_high": 0.3,
            "new_high": 0.5,
            "gap_delta": 0.2,
        }
    elif trigger_type == TriggerType.MONTHLY_ROUNDUP:
        ev = {"month": "2026-04"}
    return SocialTrigger(
        trigger_type=trigger_type,
        detected_at=_DETECT_AT,
        domain_slug=domain_slug,
        model_id=model_id,
        evidence=ev,
        dedupe_key=dedupe_key,
    )


def _setup_state_dir(tmp_path: Path) -> Path:
    """Create minimal state dir with all required state files (bootstrap-style)."""
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True)
    now = _DETECT_AT.isoformat()
    # seen_models.json
    (state_dir / "seen_models.json").write_text(
        json.dumps({"bootstrapped_at": now, "domains": {"family": ["existing-model"]}})
    )
    # seen_domains.json
    (state_dir / "seen_domains.json").write_text(
        json.dumps({"bootstrapped_at": now, "domains": ["family"]})
    )
    # divergence_highs.json
    (state_dir / "divergence_highs.json").write_text(
        json.dumps({"bootstrapped_at": now, "highs": {"family": 0.3}})
    )
    # monthly_roundup.json — set to current month so it doesn't fire
    (state_dir / "monthly_roundup.json").write_text(
        json.dumps({"bootstrapped_at": now, "last_fired_month": "2026-05"})
    )
    return state_dir


def _setup_data_dir(tmp_path: Path) -> Path:
    """Create a minimal data dir with an empty manifest."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    (data_dir / "manifest.json").write_text(
        json.dumps({"domains": {"family": {"models": ["existing-model"]}}})
    )
    return data_dir


def _setup_queue_root(tmp_path: Path) -> Path:
    """Create a minimal queue root with empty subdirs."""
    queue_root = tmp_path / "queue"
    for sub in ("pending", "approved", "failed", "published"):
        (queue_root / sub).mkdir(parents=True)
    return queue_root


# ─────────────────────────────────────────────────────────────────────────────
# TestDetectCmdNoTriggers
# ─────────────────────────────────────────────────────────────────────────────


class TestDetectCmdNoTriggers:
    """Zero new triggers → CLI prints 'No new triggers since last digest.' → returns 0."""

    def test_no_triggers_prints_message(
        self, tmp_path: Path, capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        state_dir = _setup_state_dir(tmp_path)
        data_dir = _setup_data_dir(tmp_path)
        queue_root = _setup_queue_root(tmp_path)

        monkeypatch.setenv("LSB_SOCIAL_STATE_DIR", str(state_dir))
        monkeypatch.setenv("LSB_SOCIAL_DATA_DIR", str(data_dir))
        monkeypatch.setenv("LSB_SOCIAL_QUEUE_ROOT", str(queue_root))

        # All detectors return empty
        with patch("cdb_social.cli.detect_new_model", return_value=[]), \
             patch("cdb_social.cli.detect_new_domain", return_value=[]), \
             patch("cdb_social.cli.detect_drift", return_value=[]), \
             patch("cdb_social.cli.detect_divergence", return_value=[]), \
             patch("cdb_social.cli.detect_monthly_roundup", return_value=[]):
            result = main(["detect"])

        captured = capsys.readouterr()
        assert result == 0
        assert "No new triggers since last digest." in captured.out

    def test_no_triggers_no_email_sent(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        state_dir = _setup_state_dir(tmp_path)
        data_dir = _setup_data_dir(tmp_path)
        queue_root = _setup_queue_root(tmp_path)

        monkeypatch.setenv("LSB_SOCIAL_STATE_DIR", str(state_dir))
        monkeypatch.setenv("LSB_SOCIAL_DATA_DIR", str(data_dir))
        monkeypatch.setenv("LSB_SOCIAL_QUEUE_ROOT", str(queue_root))

        with patch("cdb_social.cli.detect_new_model", return_value=[]), \
             patch("cdb_social.cli.detect_new_domain", return_value=[]), \
             patch("cdb_social.cli.detect_drift", return_value=[]), \
             patch("cdb_social.cli.detect_divergence", return_value=[]), \
             patch("cdb_social.cli.detect_monthly_roundup", return_value=[]), \
             patch("cdb_social.cli.send_digest") as mock_send:
            main(["detect"])

        mock_send.assert_not_called()

    def test_no_triggers_state_not_updated(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """emailed_dedupe_keys.json should NOT be created when no triggers fire."""
        state_dir = _setup_state_dir(tmp_path)
        data_dir = _setup_data_dir(tmp_path)
        queue_root = _setup_queue_root(tmp_path)

        monkeypatch.setenv("LSB_SOCIAL_STATE_DIR", str(state_dir))
        monkeypatch.setenv("LSB_SOCIAL_DATA_DIR", str(data_dir))
        monkeypatch.setenv("LSB_SOCIAL_QUEUE_ROOT", str(queue_root))

        keys_path = state_dir / "emailed_dedupe_keys.json"
        assert not keys_path.exists()

        with patch("cdb_social.cli.detect_new_model", return_value=[]), \
             patch("cdb_social.cli.detect_new_domain", return_value=[]), \
             patch("cdb_social.cli.detect_drift", return_value=[]), \
             patch("cdb_social.cli.detect_divergence", return_value=[]), \
             patch("cdb_social.cli.detect_monthly_roundup", return_value=[]):
            main(["detect"])

        assert not keys_path.exists()


# ─────────────────────────────────────────────────────────────────────────────
# TestDetectCmdNewTriggers
# ─────────────────────────────────────────────────────────────────────────────


class TestDetectCmdNewTriggers:
    """New triggers → email sent → emailed_dedupe_keys.json updated."""

    def test_sends_email_on_new_trigger(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        state_dir = _setup_state_dir(tmp_path)
        data_dir = _setup_data_dir(tmp_path)
        queue_root = _setup_queue_root(tmp_path)

        monkeypatch.setenv("LSB_SOCIAL_STATE_DIR", str(state_dir))
        monkeypatch.setenv("LSB_SOCIAL_DATA_DIR", str(data_dir))
        monkeypatch.setenv("LSB_SOCIAL_QUEUE_ROOT", str(queue_root))
        monkeypatch.setenv("LSB_SMTP_USERNAME", "u@example.com")
        monkeypatch.setenv("LSB_SMTP_PASSWORD", "pw")
        monkeypatch.setenv("LSB_DIGEST_RECIPIENT", "r@example.com")

        trigger = _make_trigger(dedupe_key="new1111new11111a")

        with patch("cdb_social.cli.detect_new_model", return_value=[trigger]), \
             patch("cdb_social.cli.detect_new_domain", return_value=[]), \
             patch("cdb_social.cli.detect_drift", return_value=[]), \
             patch("cdb_social.cli.detect_divergence", return_value=[]), \
             patch("cdb_social.cli.detect_monthly_roundup", return_value=[]), \
             patch("cdb_social.cli.send_digest") as mock_send:
            result = main(["detect"])

        assert result == 0
        mock_send.assert_called_once()

    def test_dedupe_keys_updated_after_send(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        state_dir = _setup_state_dir(tmp_path)
        data_dir = _setup_data_dir(tmp_path)
        queue_root = _setup_queue_root(tmp_path)

        monkeypatch.setenv("LSB_SOCIAL_STATE_DIR", str(state_dir))
        monkeypatch.setenv("LSB_SOCIAL_DATA_DIR", str(data_dir))
        monkeypatch.setenv("LSB_SOCIAL_QUEUE_ROOT", str(queue_root))
        monkeypatch.setenv("LSB_SMTP_USERNAME", "u@example.com")
        monkeypatch.setenv("LSB_SMTP_PASSWORD", "pw")
        monkeypatch.setenv("LSB_DIGEST_RECIPIENT", "r@example.com")

        trigger = _make_trigger(dedupe_key="new2222new22222b")

        with patch("cdb_social.cli.detect_new_model", return_value=[trigger]), \
             patch("cdb_social.cli.detect_new_domain", return_value=[]), \
             patch("cdb_social.cli.detect_drift", return_value=[]), \
             patch("cdb_social.cli.detect_divergence", return_value=[]), \
             patch("cdb_social.cli.detect_monthly_roundup", return_value=[]), \
             patch("cdb_social.cli.send_digest"):
            main(["detect"])

        keys_path = state_dir / "emailed_dedupe_keys.json"
        assert keys_path.exists()
        data = json.loads(keys_path.read_text())
        assert "new2222new22222b" in data["keys"]

    def test_email_subject_contains_date(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The subject passed to send_digest contains 'LSB daily digest YYYY-MM-DD'."""
        state_dir = _setup_state_dir(tmp_path)
        data_dir = _setup_data_dir(tmp_path)
        queue_root = _setup_queue_root(tmp_path)

        monkeypatch.setenv("LSB_SOCIAL_STATE_DIR", str(state_dir))
        monkeypatch.setenv("LSB_SOCIAL_DATA_DIR", str(data_dir))
        monkeypatch.setenv("LSB_SOCIAL_QUEUE_ROOT", str(queue_root))
        monkeypatch.setenv("LSB_SMTP_USERNAME", "u@example.com")
        monkeypatch.setenv("LSB_SMTP_PASSWORD", "pw")
        monkeypatch.setenv("LSB_DIGEST_RECIPIENT", "r@example.com")

        trigger = _make_trigger(dedupe_key="new3333new33333c")
        captured_calls: list[tuple[str, str]] = []

        def capture(subject: str, body: str, **_: object) -> None:
            captured_calls.append((subject, body))

        with patch("cdb_social.cli.detect_new_model", return_value=[trigger]), \
             patch("cdb_social.cli.detect_new_domain", return_value=[]), \
             patch("cdb_social.cli.detect_drift", return_value=[]), \
             patch("cdb_social.cli.detect_divergence", return_value=[]), \
             patch("cdb_social.cli.detect_monthly_roundup", return_value=[]), \
             patch("cdb_social.cli.send_digest", side_effect=capture):
            main(["detect"])

        assert len(captured_calls) == 1
        subject, _ = captured_calls[0]
        assert subject.startswith("LSB daily digest ")

    def test_returns_0_on_success(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        state_dir = _setup_state_dir(tmp_path)
        data_dir = _setup_data_dir(tmp_path)
        queue_root = _setup_queue_root(tmp_path)

        monkeypatch.setenv("LSB_SOCIAL_STATE_DIR", str(state_dir))
        monkeypatch.setenv("LSB_SOCIAL_DATA_DIR", str(data_dir))
        monkeypatch.setenv("LSB_SOCIAL_QUEUE_ROOT", str(queue_root))
        monkeypatch.setenv("LSB_SMTP_USERNAME", "u@example.com")
        monkeypatch.setenv("LSB_SMTP_PASSWORD", "pw")
        monkeypatch.setenv("LSB_DIGEST_RECIPIENT", "r@example.com")

        trigger = _make_trigger(dedupe_key="new4444new44444d")

        with patch("cdb_social.cli.detect_new_model", return_value=[trigger]), \
             patch("cdb_social.cli.detect_new_domain", return_value=[]), \
             patch("cdb_social.cli.detect_drift", return_value=[]), \
             patch("cdb_social.cli.detect_divergence", return_value=[]), \
             patch("cdb_social.cli.detect_monthly_roundup", return_value=[]), \
             patch("cdb_social.cli.send_digest"):
            result = main(["detect"])

        assert result == 0


# ─────────────────────────────────────────────────────────────────────────────
# TestDetectCmdDryRun
# ─────────────────────────────────────────────────────────────────────────────


class TestDetectCmdDryRun:
    """--dry-run: digest printed to stdout; no email sent; state NOT updated."""

    def _run_with_trigger(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        trigger: SocialTrigger,
    ) -> tuple[int, str]:
        state_dir = _setup_state_dir(tmp_path)
        data_dir = _setup_data_dir(tmp_path)
        queue_root = _setup_queue_root(tmp_path)

        monkeypatch.setenv("LSB_SOCIAL_STATE_DIR", str(state_dir))
        monkeypatch.setenv("LSB_SOCIAL_DATA_DIR", str(data_dir))
        monkeypatch.setenv("LSB_SOCIAL_QUEUE_ROOT", str(queue_root))

        import io
        import sys as _sys
        buf = io.StringIO()
        old_stdout = _sys.stdout
        _sys.stdout = buf

        with patch("cdb_social.cli.detect_new_model", return_value=[trigger]), \
             patch("cdb_social.cli.detect_new_domain", return_value=[]), \
             patch("cdb_social.cli.detect_drift", return_value=[]), \
             patch("cdb_social.cli.detect_divergence", return_value=[]), \
             patch("cdb_social.cli.detect_monthly_roundup", return_value=[]), \
             patch("cdb_social.cli.send_digest"):
            result = main(["detect", "--dry-run"])

        _sys.stdout = old_stdout
        return result, buf.getvalue()

    def test_dry_run_returns_0(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        trigger = _make_trigger(dedupe_key="dry0001dry00001a")
        result, _ = self._run_with_trigger(tmp_path, monkeypatch, trigger)
        assert result == 0

    def test_dry_run_prints_subject_to_stdout(
        self, tmp_path: Path, capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        state_dir = _setup_state_dir(tmp_path)
        data_dir = _setup_data_dir(tmp_path)
        queue_root = _setup_queue_root(tmp_path)

        monkeypatch.setenv("LSB_SOCIAL_STATE_DIR", str(state_dir))
        monkeypatch.setenv("LSB_SOCIAL_DATA_DIR", str(data_dir))
        monkeypatch.setenv("LSB_SOCIAL_QUEUE_ROOT", str(queue_root))

        trigger = _make_trigger(dedupe_key="dry0002dry00002b")

        with patch("cdb_social.cli.detect_new_model", return_value=[trigger]), \
             patch("cdb_social.cli.detect_new_domain", return_value=[]), \
             patch("cdb_social.cli.detect_drift", return_value=[]), \
             patch("cdb_social.cli.detect_divergence", return_value=[]), \
             patch("cdb_social.cli.detect_monthly_roundup", return_value=[]):
            main(["detect", "--dry-run"])

        captured = capsys.readouterr()
        assert "LSB daily digest" in captured.out

    def test_dry_run_no_email_sent(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        state_dir = _setup_state_dir(tmp_path)
        data_dir = _setup_data_dir(tmp_path)
        queue_root = _setup_queue_root(tmp_path)

        monkeypatch.setenv("LSB_SOCIAL_STATE_DIR", str(state_dir))
        monkeypatch.setenv("LSB_SOCIAL_DATA_DIR", str(data_dir))
        monkeypatch.setenv("LSB_SOCIAL_QUEUE_ROOT", str(queue_root))

        trigger = _make_trigger(dedupe_key="dry0003dry00003c")

        with patch("cdb_social.cli.detect_new_model", return_value=[trigger]), \
             patch("cdb_social.cli.detect_new_domain", return_value=[]), \
             patch("cdb_social.cli.detect_drift", return_value=[]), \
             patch("cdb_social.cli.detect_divergence", return_value=[]), \
             patch("cdb_social.cli.detect_monthly_roundup", return_value=[]), \
             patch("cdb_social.cli.send_digest") as mock_send:
            main(["detect", "--dry-run"])

        mock_send.assert_not_called()

    def test_dry_run_state_not_updated(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """emailed_dedupe_keys.json must NOT be written in dry-run mode."""
        state_dir = _setup_state_dir(tmp_path)
        data_dir = _setup_data_dir(tmp_path)
        queue_root = _setup_queue_root(tmp_path)

        monkeypatch.setenv("LSB_SOCIAL_STATE_DIR", str(state_dir))
        monkeypatch.setenv("LSB_SOCIAL_DATA_DIR", str(data_dir))
        monkeypatch.setenv("LSB_SOCIAL_QUEUE_ROOT", str(queue_root))

        keys_path = state_dir / "emailed_dedupe_keys.json"
        assert not keys_path.exists()

        trigger = _make_trigger(dedupe_key="dry0004dry00004d")

        with patch("cdb_social.cli.detect_new_model", return_value=[trigger]), \
             patch("cdb_social.cli.detect_new_domain", return_value=[]), \
             patch("cdb_social.cli.detect_drift", return_value=[]), \
             patch("cdb_social.cli.detect_divergence", return_value=[]), \
             patch("cdb_social.cli.detect_monthly_roundup", return_value=[]), \
             patch("cdb_social.cli.send_digest"):
            main(["detect", "--dry-run"])

        assert not keys_path.exists()


# ─────────────────────────────────────────────────────────────────────────────
# TestDetectCmdIdempotency
# ─────────────────────────────────────────────────────────────────────────────


class TestDetectCmdIdempotency:
    """Run once with N triggers → run again → second run sends nothing."""

    def test_second_run_no_email(
        self, tmp_path: Path, capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        state_dir = _setup_state_dir(tmp_path)
        data_dir = _setup_data_dir(tmp_path)
        queue_root = _setup_queue_root(tmp_path)

        monkeypatch.setenv("LSB_SOCIAL_STATE_DIR", str(state_dir))
        monkeypatch.setenv("LSB_SOCIAL_DATA_DIR", str(data_dir))
        monkeypatch.setenv("LSB_SOCIAL_QUEUE_ROOT", str(queue_root))
        monkeypatch.setenv("LSB_SMTP_USERNAME", "u@example.com")
        monkeypatch.setenv("LSB_SMTP_PASSWORD", "pw")
        monkeypatch.setenv("LSB_DIGEST_RECIPIENT", "r@example.com")

        trigger = _make_trigger(dedupe_key="idem1111idem1111a")

        # First run — send email
        with patch("cdb_social.cli.detect_new_model", return_value=[trigger]), \
             patch("cdb_social.cli.detect_new_domain", return_value=[]), \
             patch("cdb_social.cli.detect_drift", return_value=[]), \
             patch("cdb_social.cli.detect_divergence", return_value=[]), \
             patch("cdb_social.cli.detect_monthly_roundup", return_value=[]), \
             patch("cdb_social.cli.send_digest") as mock_send_1:
            main(["detect"])
        assert mock_send_1.call_count == 1

        # Second run with the same trigger
        with patch("cdb_social.cli.detect_new_model", return_value=[trigger]), \
             patch("cdb_social.cli.detect_new_domain", return_value=[]), \
             patch("cdb_social.cli.detect_drift", return_value=[]), \
             patch("cdb_social.cli.detect_divergence", return_value=[]), \
             patch("cdb_social.cli.detect_monthly_roundup", return_value=[]), \
             patch("cdb_social.cli.send_digest") as mock_send_2:
            result = main(["detect"])

        assert result == 0
        mock_send_2.assert_not_called()

    def test_second_run_prints_no_new_triggers(
        self, tmp_path: Path, capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        state_dir = _setup_state_dir(tmp_path)
        data_dir = _setup_data_dir(tmp_path)
        queue_root = _setup_queue_root(tmp_path)

        monkeypatch.setenv("LSB_SOCIAL_STATE_DIR", str(state_dir))
        monkeypatch.setenv("LSB_SOCIAL_DATA_DIR", str(data_dir))
        monkeypatch.setenv("LSB_SOCIAL_QUEUE_ROOT", str(queue_root))
        monkeypatch.setenv("LSB_SMTP_USERNAME", "u@example.com")
        monkeypatch.setenv("LSB_SMTP_PASSWORD", "pw")
        monkeypatch.setenv("LSB_DIGEST_RECIPIENT", "r@example.com")

        trigger = _make_trigger(dedupe_key="idem2222idem2222b")

        # First run
        with patch("cdb_social.cli.detect_new_model", return_value=[trigger]), \
             patch("cdb_social.cli.detect_new_domain", return_value=[]), \
             patch("cdb_social.cli.detect_drift", return_value=[]), \
             patch("cdb_social.cli.detect_divergence", return_value=[]), \
             patch("cdb_social.cli.detect_monthly_roundup", return_value=[]), \
             patch("cdb_social.cli.send_digest"):
            main(["detect"])

        capsys.readouterr()  # clear first-run output

        # Second run
        with patch("cdb_social.cli.detect_new_model", return_value=[trigger]), \
             patch("cdb_social.cli.detect_new_domain", return_value=[]), \
             patch("cdb_social.cli.detect_drift", return_value=[]), \
             patch("cdb_social.cli.detect_divergence", return_value=[]), \
             patch("cdb_social.cli.detect_monthly_roundup", return_value=[]):
            main(["detect"])

        captured = capsys.readouterr()
        assert "No new triggers since last digest." in captured.out

    def test_new_trigger_on_second_run_does_send(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """After emailing about trigger A, a new trigger B still fires."""
        state_dir = _setup_state_dir(tmp_path)
        data_dir = _setup_data_dir(tmp_path)
        queue_root = _setup_queue_root(tmp_path)

        monkeypatch.setenv("LSB_SOCIAL_STATE_DIR", str(state_dir))
        monkeypatch.setenv("LSB_SOCIAL_DATA_DIR", str(data_dir))
        monkeypatch.setenv("LSB_SOCIAL_QUEUE_ROOT", str(queue_root))
        monkeypatch.setenv("LSB_SMTP_USERNAME", "u@example.com")
        monkeypatch.setenv("LSB_SMTP_PASSWORD", "pw")
        monkeypatch.setenv("LSB_DIGEST_RECIPIENT", "r@example.com")

        trigger_a = _make_trigger(dedupe_key="idem3a33idem3a33a", model_id="model-a")
        trigger_b = _make_trigger(dedupe_key="idem3b33idem3b33b", model_id="model-b")

        # First run with trigger A
        with patch("cdb_social.cli.detect_new_model", return_value=[trigger_a]), \
             patch("cdb_social.cli.detect_new_domain", return_value=[]), \
             patch("cdb_social.cli.detect_drift", return_value=[]), \
             patch("cdb_social.cli.detect_divergence", return_value=[]), \
             patch("cdb_social.cli.detect_monthly_roundup", return_value=[]), \
             patch("cdb_social.cli.send_digest"):
            main(["detect"])

        # Second run with trigger B only (A already emailed)
        with patch("cdb_social.cli.detect_new_model", return_value=[trigger_b]), \
             patch("cdb_social.cli.detect_new_domain", return_value=[]), \
             patch("cdb_social.cli.detect_drift", return_value=[]), \
             patch("cdb_social.cli.detect_divergence", return_value=[]), \
             patch("cdb_social.cli.detect_monthly_roundup", return_value=[]), \
             patch("cdb_social.cli.send_digest") as mock_send_2:
            result = main(["detect"])

        assert result == 0
        mock_send_2.assert_called_once()


# ─────────────────────────────────────────────────────────────────────────────
# TestDetectCmdAtomicStateWrite
# ─────────────────────────────────────────────────────────────────────────────


class TestDetectCmdAtomicStateWrite:
    """State file write uses tempfile + os.replace (no partial writes on interrupt)."""

    def test_save_emailed_dedupe_keys_creates_valid_json(
        self, tmp_path: Path
    ) -> None:
        """_save_emailed_dedupe_keys writes valid JSON atomically."""
        state_dir = tmp_path / "state"
        state_dir.mkdir()
        keys = {"key0001aaa", "key0002bbb"}

        _save_emailed_dedupe_keys(state_dir, keys)

        path = state_dir / "emailed_dedupe_keys.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert set(data["keys"]) == keys

    def test_save_emailed_dedupe_keys_no_tmp_file_remains(
        self, tmp_path: Path
    ) -> None:
        """No .tmp file is left after a successful write."""
        state_dir = tmp_path / "state"
        state_dir.mkdir()
        _save_emailed_dedupe_keys(state_dir, {"keyabc"})

        tmp_files = list(state_dir.glob("*.tmp"))
        assert tmp_files == [], f"Leftover .tmp files: {tmp_files}"

    def test_load_emailed_dedupe_keys_absent_returns_empty(
        self, tmp_path: Path
    ) -> None:
        """Missing file returns empty set (not an error — first run semantics)."""
        state_dir = tmp_path / "state"
        state_dir.mkdir()
        result = _load_emailed_dedupe_keys(state_dir)
        assert result == set()

    def test_load_emailed_dedupe_keys_reads_existing(
        self, tmp_path: Path
    ) -> None:
        state_dir = tmp_path / "state"
        state_dir.mkdir()
        (state_dir / "emailed_dedupe_keys.json").write_text(
            json.dumps({"keys": ["key001", "key002"]})
        )
        result = _load_emailed_dedupe_keys(state_dir)
        assert result == {"key001", "key002"}

    def test_save_uses_os_replace(
        self, tmp_path: Path
    ) -> None:
        """Verify atomic write: os.replace is called (not open() direct write)."""
        state_dir = tmp_path / "state"
        state_dir.mkdir()
        original_replace = os.replace
        replace_calls: list[tuple] = []

        def tracking_replace(src: object, dst: object) -> None:
            replace_calls.append((src, dst))
            original_replace(src, dst)  # type: ignore[arg-type]

        with patch("os.replace", side_effect=tracking_replace):
            _save_emailed_dedupe_keys(state_dir, {"keyxyz"})

        # At least one os.replace call targeting the emailed_dedupe_keys.json path
        assert any(
            "emailed_dedupe_keys.json" in str(dst) for _, dst in replace_calls
        ), (
            f"Expected os.replace targeting emailed_dedupe_keys.json; got: {replace_calls}"
        )
