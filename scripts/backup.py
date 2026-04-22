"""Incremental B2 backup of LSB data directories.

Syncs data/raw/, data/processed/, data/results/, and (if present and non-empty)
data/shakedown/ to a Backblaze B2 bucket under a YYYY-MM-DD/ date prefix.

Reads B2_KEY_ID, B2_APPLICATION_KEY, B2_BUCKET_NAME from /opt/lsb-agent/.env
via python-dotenv.

Usage
-----
  python scripts/backup.py            # run backup
  python scripts/backup.py --dry-run  # enumerate planned uploads, no B2 calls

Exit codes
----------
  0  All files processed successfully (or --dry-run completed).
  1  One or more files failed to upload, or required env vars are missing.

Structured log: logs/backup.log (ISO8601 UTC timestamps, per-file status,
end-of-run summary). Systemd alerting relies on the exit code.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from b2sdk.v2 import B2Api, InMemoryAccountInfo
from dotenv import load_dotenv

# ─── Repo root resolution ────────────────────────────────────────────
# scripts/backup.py lives one level below the repo root.
REPO_ROOT = Path(__file__).resolve().parent.parent

# ─── Source directories ──────────────────────────────────────────────
# Always included (missing dirs are skipped without error — on a fresh
# clone these may not exist yet).
_ALWAYS_INCLUDE: list[Path] = [
    REPO_ROOT / "data" / "raw",
    REPO_ROOT / "data" / "processed",
    REPO_ROOT / "data" / "results",
]

# Included only when the directory exists and contains at least one file.
# Missing or empty data/shakedown/ is first-class normal (shakedown data
# exists only during shakedown windows per SHAKEDOWN_PROTOCOL.md §10).
_CONDITIONAL_INCLUDE: list[Path] = [
    REPO_ROOT / "data" / "shakedown",
]

# ─── Log setup ───────────────────────────────────────────────────────
LOG_PATH = REPO_ROOT / "logs" / "backup.log"


def _setup_logging() -> logging.Logger:
    """Configure structured logging to logs/backup.log + stderr."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    fmt = "%(asctime)s %(levelname)s %(message)s"
    datefmt = "%Y-%m-%dT%H:%M:%SZ"

    logger = logging.getLogger("backup")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    # Also log to stderr so systemd captures it alongside backup.log
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
    stderr_handler.setLevel(logging.INFO)
    logger.addHandler(stderr_handler)

    # Use UTC for all timestamps
    logging.Formatter.converter = lambda *_: datetime.now(UTC).timetuple()

    return logger


# ─── Source file enumeration ─────────────────────────────────────────

def _collect_source_files() -> list[Path]:
    """Return sorted list of local paths to back up.

    Always includes files under _ALWAYS_INCLUDE dirs (if they exist).
    Conditionally includes _CONDITIONAL_INCLUDE dirs only when non-empty.
    """
    result: list[Path] = []

    for src_dir in _ALWAYS_INCLUDE:
        if not src_dir.exists():
            continue
        for path in sorted(src_dir.rglob("*")):
            if path.is_file():
                result.append(path)

    for src_dir in _CONDITIONAL_INCLUDE:
        if not src_dir.exists() or not src_dir.is_dir():
            # Missing shakedown/ is first-class normal — not an error, not a warning.
            continue
        files = [p for p in src_dir.rglob("*") if p.is_file()]
        if not files:
            # Empty shakedown/ is also first-class normal.
            continue
        for path in sorted(files):
            result.append(path)

    return result


# ─── B2 destination key ──────────────────────────────────────────────

def _b2_key(local_path: Path, date_prefix: str) -> str:
    """Compute B2 object key: YYYY-MM-DD/<relative-path-from-repo-root>.

    Example: 2026-04-22/data/raw/informants.jsonl
    """
    rel = local_path.relative_to(REPO_ROOT)
    return f"{date_prefix}/{rel.as_posix()}"


# ─── Env var loading ─────────────────────────────────────────────────

def _load_env(logger: logging.Logger) -> tuple[str, str, str]:
    """Load and validate required B2 environment variables.

    Returns (key_id, app_key, bucket_name). Exits non-zero if any is missing.
    """
    load_dotenv(REPO_ROOT / ".env")

    key_id = os.environ.get("B2_KEY_ID", "").strip()
    app_key = os.environ.get("B2_APPLICATION_KEY", "").strip()
    bucket_name = os.environ.get("B2_BUCKET_NAME", "").strip()

    missing = [
        name for name, val in [
            ("B2_KEY_ID", key_id),
            ("B2_APPLICATION_KEY", app_key),
            ("B2_BUCKET_NAME", bucket_name),
        ]
        if not val
    ]
    if missing:
        msg = f"Missing required environment variables: {', '.join(missing)}"
        logger.error(msg)
        sys.exit(1)

    return key_id, app_key, bucket_name


# ─── Dry-run mode ────────────────────────────────────────────────────

def _run_dry(files: list[Path], date_prefix: str) -> int:
    """Print planned uploads without touching B2. Always exits 0."""
    if not files:
        print("Dry-run: no files to upload.")
        return 0
    print(f"Dry-run: {len(files)} file(s) would be uploaded under {date_prefix}/")
    for f in files:
        key = _b2_key(f, date_prefix)
        size = f.stat().st_size
        print(f"  {key}  ({size} bytes)")
    return 0


# ─── Live upload ─────────────────────────────────────────────────────

def _run_upload(
    files: list[Path],
    date_prefix: str,
    key_id: str,
    app_key: str,
    bucket_name: str,
    logger: logging.Logger,
) -> int:
    """Upload files to B2. Returns 0 on full success, 1 if any file fails."""
    api = B2Api(InMemoryAccountInfo())
    try:
        api.authorize_account("production", key_id, app_key)
    except Exception as exc:
        logger.error("B2 authorization failed: %s", exc)
        return 1

    try:
        bucket = api.get_bucket_by_name(bucket_name)
    except Exception as exc:
        logger.error("Failed to get bucket %r: %s", bucket_name, exc)
        return 1

    files_considered = len(files)
    files_uploaded = 0
    files_skipped = 0
    bytes_uploaded = 0
    any_failed = False

    for local_path in files:
        b2_key = _b2_key(local_path, date_prefix)
        file_size = local_path.stat().st_size

        try:
            # b2sdk performs SHA-1 content verification internally: if the B2
            # server already has a matching file with the same SHA-1, it will
            # still accept the upload (idempotent on content hash).
            bucket.upload_local_file(
                local_file=str(local_path),
                file_name=b2_key,
            )
            logger.info("UPLOADED %s (%d bytes) -> %s", local_path.name, file_size, b2_key)
            files_uploaded += 1
            bytes_uploaded += file_size
        except Exception as exc:
            logger.error("FAILED %s -> %s : %s", local_path.name, b2_key, exc)
            any_failed = True

    exit_code = 1 if any_failed else 0
    logger.info(
        "SUMMARY considered=%d uploaded=%d skipped=%d bytes_uploaded=%d exit_code=%d",
        files_considered,
        files_uploaded,
        files_skipped,
        bytes_uploaded,
        exit_code,
    )
    return exit_code


# ─── CLI entry point ─────────────────────────────────────────────────

def main() -> int:
    """CLI entry point for backup.py."""
    parser = argparse.ArgumentParser(
        description="Incremental B2 backup of LSB data directories.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Enumerate planned uploads without calling B2.",
    )
    args = parser.parse_args()

    logger = _setup_logging()
    date_prefix = datetime.now(UTC).strftime("%Y-%m-%d")

    logger.info("Backup run started (dry_run=%s, date_prefix=%s)", args.dry_run, date_prefix)

    files = _collect_source_files()
    logger.info("Files enumerated: %d", len(files))

    if args.dry_run:
        exit_code = _run_dry(files, date_prefix)
        logger.info("Dry-run complete. exit_code=%d", exit_code)
        return exit_code

    # Only load env (and validate credentials) when actually uploading.
    key_id, app_key, bucket_name = _load_env(logger)

    exit_code = _run_upload(files, date_prefix, key_id, app_key, bucket_name, logger)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
