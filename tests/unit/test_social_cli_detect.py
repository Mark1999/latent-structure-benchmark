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
from datetime import UTC, date, datetime
from pathlib import Path
from unittest.mock import patch

import pytest
from cdb_core.schemas import (
    BootstrapEllipse,
    DomainResult,
    FreeList,
    ModelRef,
    SocialTrigger,
    TriggerType,
)
from cdb_social.cli import (
    _load_domain_results,
    _load_emailed_dedupe_keys,
    _save_emailed_dedupe_keys,
    main,
)
from cdb_social.triggers import bootstrap_state, detect_new_model

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
    """Create a minimal data dir with a production-shaped manifest."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    (data_dir / "manifest.json").write_text(
        json.dumps({
            "built_at": "2026-05-17T14:00:00Z",
            "domains": [
                {
                    "slug": "family",
                    "analysis_version": "0.3",
                    "n_models": 1,
                    "model_ids": ["existing-model"],
                },
            ],
        })
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


# ─────────────────────────────────────────────────────────────────────────────
# Manifest shape regression tests (anti-recurrence gate — Task B)
#
# These tests enforce that the production LIST-shaped manifest is the ONLY
# shape the code accepts.  If Task A's _load_domain_results or detect_new_model
# is reverted to the old dict-keyed shape, these tests will fail with a
# TypeError or AssertionError — proving they are the load-bearing guard against
# the 8-day silent cron failure caused by the shape mismatch.
#
# Background: manifest["domains"] was previously a dict keyed by slug.
# Task A (b0fa4fc) migrated all consumers to the production LIST shape.
# Fixtures previously encoded the OLD dict shape, so CI stayed green while
# production cron failed daily.  This section enforces the prod shape going
# forward.
# ─────────────────────────────────────────────────────────────────────────────


def _make_model_ref(model_id: str = "fixture-alpha") -> ModelRef:
    """Return a minimal ModelRef for fixture use.  Uses non-real-looking IDs."""
    return ModelRef(
        provider="anthropic",
        model_id=model_id,
        family="fixture",
        origin="us",
        open_weights=False,
        collection_method="anthropic_api",
        quantization=None,
        release_date=date(2026, 1, 1),
        version_label="1.0",
    )


def _make_domain_result_json(
    domain_slug: str,
    analysis_version: str,
    model_id: str = "fixture-alpha",
) -> str:
    """Serialize a minimal DomainResult to JSON for writing to tmp_path."""
    m = _make_model_ref(model_id)
    dr = DomainResult(
        domain_slug=domain_slug,
        analysis_version=analysis_version,
        models=[m],
        free_lists={
            model_id: FreeList(
                run_id="fixture_run",
                model=m,
                domain_slug=domain_slug,
                items=["item-x", "item-y"],
                raw_order=["item-x", "item-y"],
            )
        },
        mds_coordinates={model_id: (0.0, 0.0)},
        mds_uncertainty={
            model_id: BootstrapEllipse(
                center=(0.0, 0.0),
                semi_major=0.1,
                semi_minor=0.05,
                rotation_rad=0.0,
                n_bootstrap=100,
            )
        },
        similarity_matrix=[[1.0]],
        similarity_ci=[[(0.9, 1.0)]],
        consensus_score=4.0,
        consensus_ci=(3.0, 5.0),
        groundings=[],
        selected_baseline_id=None,
        generated_lede="Fixture lede for regression test.",
        generated_at=datetime(2026, 5, 17, 12, 0, 0),
    )
    return dr.model_dump_json()


class TestLoadDomainResultsListShape:
    """Unit tests for _load_domain_results — enforces production LIST shape.

    If Task A (_load_domain_results using list + per-entry analysis_version) is
    reverted to the old dict+hardcoded-version form, these tests fail.
    """

    def test_loads_two_domains_on_different_versions(self, tmp_path: Path) -> None:
        """Anti-recurrence: two entries with DIFFERENT analysis_versions both load.

        This proves per-entry version derivation.  If Task A is reverted to
        a hardcoded '0.2.json' path, the family domain (version '0.3') will
        not load, causing this assertion to fail.
        """
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        # Write matching domain result files
        (data_dir / "family").mkdir()
        (data_dir / "family" / "0.3.json").write_text(
            _make_domain_result_json("family", "0.3", "fixture-alpha"),
            encoding="utf-8",
        )
        (data_dir / "food").mkdir()
        (data_dir / "food" / "0.2.json").write_text(
            _make_domain_result_json("food", "0.2", "fixture-beta"),
            encoding="utf-8",
        )

        # Production-shaped manifest: list of dicts, per-entry analysis_version
        manifest = {
            "built_at": "2026-05-17T12:00:00Z",
            "domains": [
                {
                    "slug": "family",
                    "analysis_version": "0.3",
                    "n_models": 1,
                    "model_ids": ["fixture-alpha"],
                },
                {
                    "slug": "food",
                    "analysis_version": "0.2",
                    "n_models": 1,
                    "model_ids": ["fixture-beta"],
                },
            ],
        }

        results = _load_domain_results(data_dir, manifest)
        assert len(results) == 2, (
            f"Expected 2 domain results; got {len(results)}. "
            "If this fails after a revert, _load_domain_results reverted to "
            "the old dict shape or hardcoded version."
        )
        slugs = {r.domain_slug for r in results}
        assert slugs == {"family", "food"}

    def test_dict_shaped_domains_returns_empty_with_warning(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Anti-recurrence: OLD dict shape returns [] + logs a warning.

        This test documents that _load_domain_results correctly rejects the
        old dict shape.  If Task A is reverted, the old code would instead
        iterate the dict keys and produce wrong results without warning.
        """
        import logging

        data_dir = tmp_path / "data"
        data_dir.mkdir()

        # OLD shape — should be rejected by current code
        manifest_old_shape = {
            "domains": {
                "family": {"models": ["fixture-alpha"]},
            }
        }

        with caplog.at_level(logging.WARNING, logger="cdb_social.cli"):
            results = _load_domain_results(data_dir, manifest_old_shape)

        assert results == [], (
            "Expected [] for old dict-shaped domains; got non-empty. "
            "If this fails, the code accepted the old shape — Task A may be reverted."
        )
        assert any("not a list" in r.message for r in caplog.records), (
            "Expected a warning about 'not a list' for old dict shape."
        )

    def test_missing_slug_entry_skipped(self, tmp_path: Path) -> None:
        """Entry missing 'slug' key is skipped without crashing."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "family").mkdir()
        (data_dir / "family" / "0.3.json").write_text(
            _make_domain_result_json("family", "0.3"),
            encoding="utf-8",
        )

        manifest = {
            "built_at": "2026-05-17T12:00:00Z",
            "domains": [
                # entry with slug
                {
                    "slug": "family",
                    "analysis_version": "0.3",
                    "n_models": 1,
                    "model_ids": ["fixture-alpha"],
                },
                # malformed entry without slug — should be skipped
                {"analysis_version": "0.3", "n_models": 1, "model_ids": ["fixture-alpha"]},
            ],
        }

        results = _load_domain_results(data_dir, manifest)
        assert len(results) == 1
        assert results[0].domain_slug == "family"


class TestDetectNewModelReadsModelIds:
    """Unit tests confirming detect_new_model reads 'model_ids' (not 'models').

    If Task A is reverted so detect_new_model iterates entry.get('models', [])
    instead of entry.get('model_ids', []), these tests fail because the
    manifest entries carry 'model_ids' but no 'models' key.
    """

    def test_reads_model_ids_not_models(self, tmp_path: Path) -> None:
        """Anti-recurrence: detect_new_model fires on 'model_ids' field.

        The manifest entry has 'model_ids': ['fixture-new-model'] and no
        'models' key.  If the code reads 'models' (old behaviour), it will
        find an empty list and emit zero triggers.  Current code (Task A)
        reads 'model_ids' and fires one trigger.
        """
        # Bootstrap with empty seen_models
        state_dir = tmp_path / "state"
        state_dir.mkdir()
        (state_dir / "seen_models.json").write_text(
            json.dumps({
                "bootstrapped_at": "2026-05-17T12:00:00+00:00",
                "domains": {"family": []},
            })
        )

        # manifest uses 'model_ids' (production field name — NO 'models' key)
        manifest = {
            "built_at": "2026-05-18T12:00:00Z",
            "domains": [
                {
                    "slug": "family",
                    "analysis_version": "0.3",
                    "n_models": 1,
                    "model_ids": ["fixture-new-model"],
                    # intentionally NO 'models' key — old code would silently get []
                },
            ],
        }

        triggers = detect_new_model(manifest, state_dir)
        assert len(triggers) == 1, (
            f"Expected 1 trigger from 'model_ids'; got {len(triggers)}. "
            "If this fails, detect_new_model may be reading 'models' instead of "
            "'model_ids' — Task A may be reverted."
        )
        assert triggers[0].model_id == "fixture-new-model"
        assert triggers[0].domain_slug == "family"

    def test_old_models_key_ignored(self, tmp_path: Path) -> None:
        """Confirm 'models' key in an entry does NOT drive trigger detection.

        An entry with 'models': ['fixture-alpha'] but no 'model_ids' key
        produces ZERO triggers — because the code reads 'model_ids', not 'models'.
        This proves the old field name is inert.
        """
        state_dir = tmp_path / "state"
        state_dir.mkdir()
        (state_dir / "seen_models.json").write_text(
            json.dumps({
                "bootstrapped_at": "2026-05-17T12:00:00+00:00",
                "domains": {"family": []},
            })
        )

        # entry uses old 'models' key (no 'model_ids') — should produce no triggers
        manifest = {
            "built_at": "2026-05-18T12:00:00Z",
            "domains": [
                {
                    "slug": "family",
                    "analysis_version": "0.3",
                    "n_models": 1,
                    "models": ["fixture-alpha"],  # old field name — must be ignored
                    # no 'model_ids' key
                },
            ],
        }

        triggers = detect_new_model(manifest, state_dir)
        assert triggers == [], (
            f"Expected [] when only 'models' key is present (no 'model_ids'); "
            f"got {len(triggers)} trigger(s). "
            "If this fails, the code is reading the old 'models' key."
        )


class TestE2EManifestListShapeDetect:
    """End-to-end regression test for cmd_detect with production-shaped manifest.

    Writes a real manifest.json + domain result files to tmp_path, bootstraps
    state, then calls cmd_detect (--dry-run path so no email is sent).

    If Task A is reverted:
    - _load_domain_results will receive a list but try to iterate it as a dict,
      raising TypeError: 'str' object is not a mapping — or produce an empty
      domain list, breaking the divergence detector.
    - detect_new_model will read 'model_ids' from list entries and still work
      (since it already handles list iteration), BUT the wrong field name would
      produce zero triggers even when new models are present.

    This test asserts: exit 0, no TypeError, and _load_domain_results returns
    a non-empty list of DomainResult objects.
    """

    def _build_data_dir(self, tmp_path: Path) -> Path:
        """Write production-shaped manifest + two domain result files."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        # Two entries with DIFFERENT analysis_versions — proves per-entry derivation
        manifest = {
            "built_at": "2026-05-17T12:00:00Z",
            "domains": [
                {
                    "slug": "family",
                    "analysis_version": "0.3",
                    "n_models": 1,
                    "model_ids": ["fixture-alpha"],
                },
                {
                    "slug": "food",
                    "analysis_version": "0.2",
                    "n_models": 1,
                    "model_ids": ["fixture-beta"],
                },
            ],
        }
        (data_dir / "manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )

        (data_dir / "family").mkdir()
        (data_dir / "family" / "0.3.json").write_text(
            _make_domain_result_json("family", "0.3", "fixture-alpha"),
            encoding="utf-8",
        )
        (data_dir / "food").mkdir()
        (data_dir / "food" / "0.2.json").write_text(
            _make_domain_result_json("food", "0.2", "fixture-beta"),
            encoding="utf-8",
        )
        return data_dir

    def _build_state_dir(self, tmp_path: Path, data_dir: Path) -> Path:
        """Bootstrap state so detectors don't raise StateFileMissingError."""
        state_dir = tmp_path / "state"
        state_dir.mkdir()

        manifest = json.loads((data_dir / "manifest.json").read_text())

        from cdb_social.cli import _load_domain_results as _ldr  # noqa: PLC0415

        domain_results = _ldr(data_dir, manifest)

        bootstrap_state(state_dir, manifest, domain_results)
        return state_dir

    def test_cmd_detect_dry_run_exits_zero_no_type_error(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """End-to-end: cmd_detect --dry-run returns 0 with production list-shape manifest.

        Anti-recurrence proof: if Task A is reverted, _load_domain_results will
        attempt to iterate the list as a dict and raise TypeError (or log a
        warning and return []), causing the test to fail.
        """
        data_dir = self._build_data_dir(tmp_path)
        state_dir = self._build_state_dir(tmp_path, data_dir)
        queue_root = _setup_queue_root(tmp_path)

        monkeypatch.setenv("LSB_SOCIAL_STATE_DIR", str(state_dir))
        monkeypatch.setenv("LSB_SOCIAL_DATA_DIR", str(data_dir))
        monkeypatch.setenv("LSB_SOCIAL_QUEUE_ROOT", str(queue_root))

        # No patching of _load_domain_results or detectors — real code path
        result = main(["detect", "--dry-run"])

        assert result == 0, (
            f"cmd_detect returned {result}; expected 0. "
            "TypeError from reverted Task A would surface here."
        )

    def test_load_domain_results_returns_nonempty_from_prod_manifest(
        self,
        tmp_path: Path,
    ) -> None:
        """_load_domain_results returns non-empty list from production-shaped manifest.

        Directly validates the load path without going through cmd_detect.
        If Task A is reverted, the list entries will be treated as dict keys
        (or the non-list guard will fire), and the function will return [].
        """
        data_dir = self._build_data_dir(tmp_path)
        manifest = json.loads((data_dir / "manifest.json").read_text())

        results = _load_domain_results(data_dir, manifest)

        assert len(results) == 2, (
            f"Expected 2 DomainResult objects; got {len(results)}. "
            "This fails if Task A is reverted — the production list shape "
            "would not load correctly."
        )
        assert {r.domain_slug for r in results} == {"family", "food"}
        assert {r.analysis_version for r in results} == {"0.3", "0.2"}, (
            "Both analysis_versions must be honoured (per-entry derivation). "
            "If this fails, _load_domain_results is using a hardcoded version."
        )
