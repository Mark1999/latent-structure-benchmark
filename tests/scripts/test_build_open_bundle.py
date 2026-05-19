"""Tests for scripts/build_open_bundle.py.

Uses synthetic 2-record fixture; no real API calls.
See CLAUDE.md §6 rule 10 (no real API calls in tests).
"""

from __future__ import annotations

import hashlib
import io
import sys
import tarfile
from pathlib import Path

import pytest

# Add repo root to sys.path so we can import scripts/build_open_bundle directly.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.build_open_bundle import (  # noqa: E402
    BUNDLE_ROOT,
    TARBALL_NAME,
    _build_manifest,
    _collect_sources,
    _refuse_shakedown,
    _sha256_bytes,
    _sha256_file,
    verify_bundle,
)

FIXTURE_JSONL = REPO_ROOT / "tests" / "fixtures" / "open_bundle_informants_fixture.jsonl"

MANIFEST_KEY = f"{BUNDLE_ROOT}/lsb.sqlite"
MANIFEST_PATH = f"{BUNDLE_ROOT}/MANIFEST.txt"


# ── helpers ───────────────────────────────────────────────────────────────────


def _make_minimal_tarball(tmp_dir: Path) -> Path:
    """Build a minimal tarball with two text files and a MANIFEST.txt.

    Returns the tarball path.
    """
    file_a_content = b"hello world\n"
    file_b_content = b"fixture data\n"
    manifest_lines = (
        f"{hashlib.sha256(file_a_content).hexdigest()}\t"
        f"{len(file_a_content)}\t{BUNDLE_ROOT}/a.txt\n"
        f"{hashlib.sha256(file_b_content).hexdigest()}\t"
        f"{len(file_b_content)}\t{BUNDLE_ROOT}/b.txt\n"
    ).encode()

    tarball_path = tmp_dir / TARBALL_NAME
    with tarfile.open(str(tarball_path), "w:gz") as tf:
        for name, data in (
            (f"{BUNDLE_ROOT}/a.txt", file_a_content),
            (f"{BUNDLE_ROOT}/b.txt", file_b_content),
            (f"{BUNDLE_ROOT}/MANIFEST.txt", manifest_lines),
        ):
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))

    return tarball_path


# ── sha256 helpers ─────────────────────────────────────────────────────────────


def test_sha256_bytes_known_value() -> None:
    """SHA256 of empty bytes is the well-known empty-string digest."""
    assert _sha256_bytes(b"") == (
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )


def test_sha256_file_matches_bytes(tmp_path: Path) -> None:
    content = b"test content for SHA256\n"
    f = tmp_path / "test.txt"
    f.write_bytes(content)
    assert _sha256_file(f) == _sha256_bytes(content)


# ── shakedown refusal ─────────────────────────────────────────────────────────


def test_shakedown_refusal_direct() -> None:
    """_refuse_shakedown raises ValueError for paths containing 'shakedown'."""
    shakedown_path = Path("/data/shakedown/informants.jsonl")
    with pytest.raises(ValueError, match="shakedown"):
        _refuse_shakedown(shakedown_path, "informants.jsonl")


def test_non_shakedown_path_does_not_raise() -> None:
    """_refuse_shakedown does not raise for normal data paths."""
    normal_path = Path("/opt/lsb-agent/data/raw/informants.jsonl")
    # Should not raise
    _refuse_shakedown(normal_path, "informants.jsonl")


# ── _build_manifest ───────────────────────────────────────────────────────────


def test_build_manifest_format(tmp_path: Path) -> None:
    """MANIFEST.txt has SHA256 TAB BYTES TAB PATH on each line, sorted by path."""
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.txt"
    file_a.write_bytes(b"alpha\n")
    file_b.write_bytes(b"beta data\n")

    sources = [
        (file_b, f"{BUNDLE_ROOT}/b.txt"),
        (file_a, f"{BUNDLE_ROOT}/a.txt"),
    ]
    manifest = _build_manifest(sources, None, MANIFEST_KEY, MANIFEST_PATH)
    lines = manifest.decode().strip().splitlines()

    # Should be sorted by path (a.txt before b.txt)
    assert len(lines) == 2
    assert lines[0].split("\t")[2] == f"{BUNDLE_ROOT}/a.txt"
    assert lines[1].split("\t")[2] == f"{BUNDLE_ROOT}/b.txt"

    # Each line: sha256 TAB bytes TAB path
    for line in lines:
        parts = line.split("\t")
        assert len(parts) == 3
        digest, size_str, _path = parts
        assert len(digest) == 64  # hex SHA256
        assert int(size_str) > 0


def test_build_manifest_excludes_missing_files(tmp_path: Path) -> None:
    """Files that do not exist are silently skipped."""
    existing = tmp_path / "exists.txt"
    existing.write_bytes(b"content")
    missing = tmp_path / "missing.txt"

    sources = [
        (existing, f"{BUNDLE_ROOT}/exists.txt"),
        (missing, f"{BUNDLE_ROOT}/missing.txt"),
    ]
    manifest = _build_manifest(sources, None, MANIFEST_KEY, MANIFEST_PATH)
    lines = manifest.decode().strip().splitlines()
    assert len(lines) == 1
    assert "exists.txt" in lines[0]


def test_build_manifest_includes_sqlite_when_provided(tmp_path: Path) -> None:
    """When sqlite_path is provided and exists, it appears in the manifest."""
    src = tmp_path / "a.txt"
    src.write_bytes(b"hello")
    db = tmp_path / "lsb.sqlite"
    db.write_bytes(b"sqlite data here")

    sources = [(src, f"{BUNDLE_ROOT}/a.txt")]
    manifest = _build_manifest(sources, db, MANIFEST_KEY, MANIFEST_PATH)
    lines = manifest.decode().strip().splitlines()
    paths = [ln.split("\t")[2] for ln in lines]
    assert f"{BUNDLE_ROOT}/lsb.sqlite" in paths


# ── verify_bundle ─────────────────────────────────────────────────────────────


def test_verify_bundle_pass(tmp_path: Path) -> None:
    """verify_bundle returns True for a well-formed tarball."""
    tarball = _make_minimal_tarball(tmp_path)
    assert verify_bundle(tarball) is True


def test_verify_bundle_fail_corrupted_content(tmp_path: Path) -> None:
    """verify_bundle returns False when a file's content is corrupted."""
    original_a = b"hello world\n"
    bad_a = b"CORRUPTED\n"
    manifest_lines = (
        f"{hashlib.sha256(original_a).hexdigest()}\t"
        f"{len(original_a)}\t{BUNDLE_ROOT}/a.txt\n"
    ).encode()

    corrupted = tmp_path / "corrupted.tar.gz"
    with tarfile.open(str(corrupted), "w:gz") as tf:
        for name, data in (
            (f"{BUNDLE_ROOT}/a.txt", bad_a),
            (f"{BUNDLE_ROOT}/MANIFEST.txt", manifest_lines),
        ):
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))

    assert verify_bundle(corrupted) is False


def test_verify_bundle_missing_manifest(tmp_path: Path) -> None:
    """verify_bundle returns False when MANIFEST.txt is absent from tarball."""
    tarball = tmp_path / "no_manifest.tar.gz"
    with tarfile.open(str(tarball), "w:gz") as tf:
        data = b"hello"
        info = tarfile.TarInfo(name=f"{BUNDLE_ROOT}/a.txt")
        info.size = len(data)
        tf.addfile(info, io.BytesIO(data))

    assert verify_bundle(tarball) is False


# ── integration: build_bundle with fixture JSONL ──────────────────────────────


def test_build_bundle_dry_run_lists_files(capsys: pytest.CaptureFixture[str]) -> None:
    """Dry-run mode prints the file list without raising."""
    from scripts.build_open_bundle import build_bundle  # noqa: PLC0415

    result = build_bundle(REPO_ROOT, Path("/tmp"), dry_run=True)
    assert result is None
    captured = capsys.readouterr()
    assert "DRY RUN" in captured.out
    assert "informants.jsonl" in captured.out


def test_collect_sources_includes_required_files() -> None:
    """_collect_sources includes committed bundle files.

    data/raw/informants.jsonl is intentionally excluded from this assertion
    because data/raw/ is git-ignored — CI runs against a fresh checkout where
    the file is absent, while the VPS has the live data. The
    "silently-skip-missing-files" behavior is already covered by
    test_build_manifest_excludes_missing_files.
    """
    sources = _collect_sources(REPO_ROOT)
    internal_paths = {internal for _, internal in sources}

    assert f"{BUNDLE_ROOT}/build_db.py" in internal_paths
    assert f"{BUNDLE_ROOT}/DATA_DICTIONARY.md" in internal_paths
    assert f"{BUNDLE_ROOT}/README.md" in internal_paths
