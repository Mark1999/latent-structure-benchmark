"""Tests for scripts/backup.py.

No real B2 calls — B2Api is mocked with unittest.mock per CLAUDE.md §6 rule 10.

Coverage
--------
- Happy path: three source files → all uploaded, exit 0, log contains SUMMARY.
- data/shakedown/ missing → script succeeds, shakedown not in upload plan.
- Missing B2 env var → exit 1, clear error in log.
- --dry-run → no upload calls made, exit 0.
- One file fails to upload → exit 1, failure logged, other files still attempted.
"""

from __future__ import annotations

import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import the script functions directly via pythonpath = ["."] (pyproject.toml).
from scripts.backup import (
    _b2_key,
    _collect_source_files,
    _load_env,
    _run_dry,
    _run_upload,
    _setup_logging,
    main,
)

# ─── Fixtures ────────────────────────────────────────────────────────

@pytest.fixture()
def fake_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a minimal fake repo tree under tmp_path and patch REPO_ROOT."""
    # Create source directories with test files
    (tmp_path / "data" / "raw").mkdir(parents=True)
    (tmp_path / "data" / "processed").mkdir(parents=True)
    (tmp_path / "data" / "results").mkdir(parents=True)
    (tmp_path / "logs").mkdir(parents=True)

    (tmp_path / "data" / "raw" / "informants.jsonl").write_text("{}\n", encoding="utf-8")
    (tmp_path / "data" / "processed" / "matrix.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (tmp_path / "data" / "results" / "output.json").write_text('{"ok":true}\n', encoding="utf-8")

    # Patch REPO_ROOT in the backup module so all path logic uses tmp_path
    monkeypatch.setattr("scripts.backup.REPO_ROOT", tmp_path)
    # Also patch _ALWAYS_INCLUDE and _CONDITIONAL_INCLUDE which are module-level
    monkeypatch.setattr(
        "scripts.backup._ALWAYS_INCLUDE",
        [
            tmp_path / "data" / "raw",
            tmp_path / "data" / "processed",
            tmp_path / "data" / "results",
        ],
    )
    monkeypatch.setattr(
        "scripts.backup._CONDITIONAL_INCLUDE",
        [tmp_path / "data" / "shakedown"],
    )
    monkeypatch.setattr("scripts.backup.LOG_PATH", tmp_path / "logs" / "backup.log")

    return tmp_path


@pytest.fixture()
def b2_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set required B2 env vars in the process environment."""
    monkeypatch.setenv("B2_KEY_ID", "test-key-id")
    monkeypatch.setenv("B2_APPLICATION_KEY", "test-app-key")
    monkeypatch.setenv("B2_BUCKET_NAME", "test-bucket")


def _make_mock_api() -> tuple[MagicMock, MagicMock]:
    """Return (mock_api_instance, mock_bucket) pre-wired."""
    mock_bucket = MagicMock()
    mock_file_version = MagicMock()
    mock_file_version.file_name = "2026-04-22/data/raw/informants.jsonl"
    mock_bucket.upload_local_file.return_value = mock_file_version

    mock_api = MagicMock()
    mock_api.get_bucket_by_name.return_value = mock_bucket
    return mock_api, mock_bucket


# ─── Unit: _collect_source_files ────────────────────────────────────

def test_collect_source_files_returns_three_files(fake_repo: Path) -> None:
    files = _collect_source_files()
    assert len(files) == 3
    names = {f.name for f in files}
    assert names == {"informants.jsonl", "matrix.csv", "output.json"}


def test_collect_source_files_excludes_missing_shakedown(fake_repo: Path) -> None:
    """data/shakedown/ does not exist — should be silently excluded."""
    files = _collect_source_files()
    assert not any("shakedown" in str(f) for f in files)


def test_collect_source_files_includes_nonempty_shakedown(
    fake_repo: Path,
) -> None:
    """data/shakedown/ exists with files — should be included."""
    shakedown = fake_repo / "data" / "shakedown"
    shakedown.mkdir(parents=True)
    (shakedown / "run_001.jsonl").write_text("{}\n", encoding="utf-8")

    files = _collect_source_files()
    names = {f.name for f in files}
    assert "run_001.jsonl" in names


def test_collect_source_files_excludes_empty_shakedown(
    fake_repo: Path,
) -> None:
    """data/shakedown/ exists but is empty — should still be excluded."""
    shakedown = fake_repo / "data" / "shakedown"
    shakedown.mkdir(parents=True)
    # No files created

    files = _collect_source_files()
    assert not any("shakedown" in str(f) for f in files)


# ─── Unit: _b2_key ───────────────────────────────────────────────────

def test_b2_key_format(fake_repo: Path) -> None:
    local_path = fake_repo / "data" / "raw" / "informants.jsonl"
    key = _b2_key(local_path, "2026-04-22")
    assert key == "2026-04-22/data/raw/informants.jsonl"


# ─── Unit: _load_env ─────────────────────────────────────────────────

def test_load_env_missing_key_exits_nonzero(
    fake_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Missing B2_KEY_ID → sys.exit(1) with a clear error message."""
    monkeypatch.delenv("B2_KEY_ID", raising=False)
    monkeypatch.delenv("B2_APPLICATION_KEY", raising=False)
    monkeypatch.delenv("B2_BUCKET_NAME", raising=False)

    logger = logging.getLogger("backup")
    with pytest.raises(SystemExit) as exc_info:
        _load_env(logger)

    assert exc_info.value.code == 1


def test_load_env_all_present(
    fake_repo: Path,
    b2_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    logger = logging.getLogger("backup")
    # Patch load_dotenv to no-op (don't touch .env file in tmp_path)
    with patch("scripts.backup.load_dotenv"):
        key_id, app_key, bucket = _load_env(logger)
    assert key_id == "test-key-id"
    assert app_key == "test-app-key"
    assert bucket == "test-bucket"


# ─── Unit: _run_dry ──────────────────────────────────────────────────

def test_dry_run_prints_plan(
    fake_repo: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    files = _collect_source_files()
    exit_code = _run_dry(files, "2026-04-22")
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "3 file(s) would be uploaded" in out
    assert "data/raw/informants.jsonl" in out


def test_dry_run_no_upload_calls(fake_repo: Path, b2_env: None) -> None:
    """--dry-run must not call B2Api at all."""
    files = _collect_source_files()
    with patch("scripts.backup.B2Api") as mock_b2:
        _run_dry(files, "2026-04-22")
        mock_b2.assert_not_called()


def test_dry_run_empty_file_list(
    fake_repo: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = _run_dry([], "2026-04-22")
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "no files" in out


# ─── Integration: _run_upload happy path ─────────────────────────────

def test_run_upload_happy_path(fake_repo: Path) -> None:
    """Three files → all uploaded, exit 0, SUMMARY in log."""
    files = _collect_source_files()
    assert len(files) == 3

    mock_api, mock_bucket = _make_mock_api()
    log_path = fake_repo / "logs" / "backup.log"
    logger = _setup_logging()

    with patch("scripts.backup.B2Api") as mock_b2_cls:
        mock_b2_cls.return_value = mock_api
        exit_code = _run_upload(
            files, "2026-04-22",
            "kid", "akey", "mybucket",
            logger,
        )

    assert exit_code == 0
    assert mock_bucket.upload_local_file.call_count == 3
    log_text = log_path.read_text(encoding="utf-8")
    assert "SUMMARY" in log_text
    assert "exit_code=0" in log_text


def test_run_upload_records_bytes(fake_repo: Path) -> None:
    """Bytes uploaded in SUMMARY matches sum of file sizes."""
    files = _collect_source_files()
    total_bytes = sum(f.stat().st_size for f in files)

    mock_api, mock_bucket = _make_mock_api()
    logger = _setup_logging()

    with patch("scripts.backup.B2Api") as mock_b2_cls:
        mock_b2_cls.return_value = mock_api
        exit_code = _run_upload(
            files, "2026-04-22",
            "kid", "akey", "mybucket",
            logger,
        )

    assert exit_code == 0
    log_text = (fake_repo / "logs" / "backup.log").read_text(encoding="utf-8")
    assert f"bytes_uploaded={total_bytes}" in log_text


# ─── Integration: partial failure ────────────────────────────────────

def test_run_upload_one_file_fails(fake_repo: Path) -> None:
    """One upload raises → exit 1, failure logged, others still attempted."""
    files = _collect_source_files()
    assert len(files) == 3

    mock_bucket = MagicMock()
    call_count = {"n": 0}

    def _side_effect(**kwargs: object) -> MagicMock:
        call_count["n"] += 1
        if call_count["n"] == 2:
            raise RuntimeError("simulated B2 upload error")
        fv = MagicMock()
        fv.file_name = kwargs.get("file_name", "unknown")
        return fv

    mock_bucket.upload_local_file.side_effect = _side_effect

    mock_api = MagicMock()
    mock_api.get_bucket_by_name.return_value = mock_bucket

    logger = _setup_logging()

    with patch("scripts.backup.B2Api") as mock_b2_cls:
        mock_b2_cls.return_value = mock_api
        exit_code = _run_upload(
            files, "2026-04-22",
            "kid", "akey", "mybucket",
            logger,
        )

    # Exit non-zero
    assert exit_code == 1
    # All three files still attempted
    assert mock_bucket.upload_local_file.call_count == 3
    # Failure logged
    log_text = (fake_repo / "logs" / "backup.log").read_text(encoding="utf-8")
    assert "FAILED" in log_text
    assert "simulated B2 upload error" in log_text


# ─── Integration: main() CLI ─────────────────────────────────────────

def test_main_dry_run_exit_zero(
    fake_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """main() with --dry-run exits 0 without touching B2."""
    monkeypatch.setattr("sys.argv", ["backup.py", "--dry-run"])
    with patch("scripts.backup.B2Api") as mock_b2_cls:
        exit_code = main()
    assert exit_code == 0
    mock_b2_cls.assert_not_called()


def test_main_missing_env_exits_nonzero(
    fake_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """main() without B2 env vars and without --dry-run exits non-zero."""
    monkeypatch.setattr("sys.argv", ["backup.py"])
    monkeypatch.delenv("B2_KEY_ID", raising=False)
    monkeypatch.delenv("B2_APPLICATION_KEY", raising=False)
    monkeypatch.delenv("B2_BUCKET_NAME", raising=False)

    with patch("scripts.backup.load_dotenv"), pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1


def test_main_shakedown_missing_is_normal(
    fake_repo: Path,
    b2_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """main() completes without error when data/shakedown/ is absent."""
    monkeypatch.setattr("sys.argv", ["backup.py"])
    assert not (fake_repo / "data" / "shakedown").exists()

    mock_api, mock_bucket = _make_mock_api()

    with patch("scripts.backup.B2Api") as mock_b2_cls:
        mock_b2_cls.return_value = mock_api
        with patch("scripts.backup.load_dotenv"):
            exit_code = main()

    assert exit_code == 0
    # Confirm no shakedown path was uploaded
    uploaded_keys = [
        call.kwargs.get("file_name", "")
        for call in mock_bucket.upload_local_file.call_args_list
    ]
    assert not any("shakedown" in k for k in uploaded_keys)
