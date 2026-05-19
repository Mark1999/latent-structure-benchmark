"""Build the LSB open data bundle tarball.

This script assembles the canonical open data bundle per ARCHITECTURE.md §6.7 and
docs/DATA_DICTIONARY.md §0. It wraps scripts/build_db.py to produce lsb.sqlite, then
tars everything into lsb_open_bundle_v1.tar.gz.

Usage:
    python scripts/build_open_bundle.py [--output-dir DIR] [--dry-run] [--verify PATH]

Flags:
    --output-dir DIR   Directory to write the tarball (default: /tmp)
    --dry-run          List what would be included; do not write tarball or SQLite
    --verify PATH      Verify an existing tarball against its embedded MANIFEST.txt

Binding constraints:
    - No new dependencies: stdlib only (tarfile, hashlib, subprocess, argparse, pathlib).
    - Refuses to build from any path under data/shakedown/ (mirrors build_db.py rule).
    - Tarball and lsb.sqlite are gitignored; do not commit them.
    - Internal layout: lsb_open_bundle_v1/ at tarball root.
    - MANIFEST.txt written inside the tarball: SHA256  BYTES  PATH per line.

See ARCHITECTURE.md §6.7, HOSTING_AND_DEV_OPS.md §7.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import subprocess
import sys
import tarfile
from pathlib import Path

BUNDLE_ROOT = "lsb_open_bundle_v1"
TARBALL_NAME = "lsb_open_bundle_v1.tar.gz"
REPO_ROOT = Path(__file__).resolve().parent.parent

# Path segment that, if present in any source path, causes refusal.
# Mirrors the same check in scripts/build_db.py.
SHAKEDOWN_PATH_SEGMENT: str = "shakedown"


def _refuse_shakedown(path: Path, label: str) -> None:
    """Raise ValueError if path is under a shakedown directory."""
    resolved = path.resolve()
    if SHAKEDOWN_PATH_SEGMENT in resolved.parts:
        raise ValueError(
            f"Refusing to include {label} from a shakedown path: {path}. "
            "Shakedown data is diagnostic-only and must not enter the open data bundle. "
            "See docs/SHAKEDOWN_PROTOCOL.md §2."
        )


def _sha256_file(path: Path) -> str:
    """Return lowercase hex SHA256 digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_bytes(data: bytes) -> str:
    """Return lowercase hex SHA256 digest of a byte string."""
    return hashlib.sha256(data).hexdigest()


def _collect_sources(repo_root: Path) -> list[tuple[Path, str]]:
    """Return list of (absolute_path, bundle-internal-path) tuples.

    The bundle-internal path is relative to the tarball root, so every
    entry starts with BUNDLE_ROOT + "/".  lsb.sqlite is NOT listed here —
    it is built and added separately inside build_bundle().
    """
    raw = repo_root / "data" / "raw"
    open_bundle = repo_root / "data" / "open_bundle"

    sources: list[tuple[Path, str]] = []

    # ── Canonical JSONL files ──────────────────────────────────────────────
    for fname in ("informants.jsonl", "failures.jsonl", "decline_interviews.jsonl"):
        p = raw / fname
        if p.exists():
            _refuse_shakedown(p, fname)
            sources.append((p, f"{BUNDLE_ROOT}/{fname}"))

    # ── Build script ──────────────────────────────────────────────────────
    build_db = repo_root / "scripts" / "build_db.py"
    if build_db.exists():
        sources.append((build_db, f"{BUNDLE_ROOT}/build_db.py"))

    # ── Data dictionary ───────────────────────────────────────────────────
    data_dict = repo_root / "docs" / "DATA_DICTIONARY.md"
    if data_dict.exists():
        sources.append((data_dict, f"{BUNDLE_ROOT}/DATA_DICTIONARY.md"))

    # ── Prompt templates v1 ───────────────────────────────────────────────
    prompts_v1 = repo_root / "packages" / "cdb_collect" / "cdb_collect" / "prompts" / "v1"
    if prompts_v1.exists():
        for md_file in sorted(prompts_v1.glob("*.md")):
            sources.append((md_file, f"{BUNDLE_ROOT}/prompts/v1/{md_file.name}"))

    # ── Domain definitions ────────────────────────────────────────────────
    domains_v1 = repo_root / "data" / "domains" / "v1"
    if domains_v1.exists():
        for yaml_file in sorted(domains_v1.glob("*.yaml")):
            sources.append((yaml_file, f"{BUNDLE_ROOT}/domains/v1/{yaml_file.name}"))

    # ── License ───────────────────────────────────────────────────────────
    license_file = repo_root / "LICENSE-OPENBUNDLE"
    if license_file.exists():
        sources.append((license_file, f"{BUNDLE_ROOT}/LICENSE-OPENBUNDLE"))

    # ── Open bundle README ────────────────────────────────────────────────
    readme = open_bundle / "README.md"
    if readme.exists():
        sources.append((readme, f"{BUNDLE_ROOT}/README.md"))

    return sources


def _build_sqlite(repo_root: Path, db_path: Path, dry_run: bool) -> None:
    """Invoke scripts/build_db.py to produce lsb.sqlite at db_path."""
    if dry_run:
        return

    jsonl = repo_root / "data" / "raw" / "informants.jsonl"
    decline = repo_root / "data" / "raw" / "decline_interviews.jsonl"

    cmd = [
        sys.executable,
        str(repo_root / "scripts" / "build_db.py"),
        str(jsonl),
        str(db_path),
    ]
    if decline.exists():
        cmd += ["--decline-interviews", str(decline)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(
            f"build_db.py failed with exit code {result.returncode}"
        )
    print(result.stdout, end="")


def _build_manifest(
    sources: list[tuple[Path, str]],
    sqlite_path: Path | None,
    sqlite_bundle_path: str,
    manifest_bundle_path: str,
) -> bytes:
    """Return the MANIFEST.txt content as bytes.

    Format: SHA256  BYTES  INTERNAL_PATH  (tab-separated, one per line)
    The MANIFEST.txt entry itself is not included (circular).
    lsb.sqlite is included when sqlite_path is provided and exists.
    """
    lines: list[str] = []

    for abs_path, internal_path in sources:
        if not abs_path.exists():
            continue
        digest = _sha256_file(abs_path)
        size = abs_path.stat().st_size
        lines.append(f"{digest}\t{size}\t{internal_path}")

    if sqlite_path is not None and sqlite_path.exists():
        digest = _sha256_file(sqlite_path)
        size = sqlite_path.stat().st_size
        lines.append(f"{digest}\t{size}\t{sqlite_bundle_path}")

    lines.sort(key=lambda ln: ln.split("\t")[2])
    content = "\n".join(lines) + "\n"
    return content.encode("utf-8")


def build_bundle(
    repo_root: Path,
    output_dir: Path,
    dry_run: bool = False,
) -> Path | None:
    """Build the open data bundle tarball.

    Returns the path to the written tarball, or None on dry-run.
    """
    sources = _collect_sources(repo_root)

    sqlite_bundle_path = f"{BUNDLE_ROOT}/lsb.sqlite"
    manifest_bundle_path = f"{BUNDLE_ROOT}/MANIFEST.txt"

    if dry_run:
        print(f"DRY RUN — would include {len(sources)} source files (+ lsb.sqlite + MANIFEST.txt):")
        for _, internal in sources:
            print(f"  {internal}")
        print(f"  {sqlite_bundle_path}  [built from data/raw/informants.jsonl]")
        print(f"  {manifest_bundle_path}  [generated]")
        return None

    # Build SQLite to a temp location then move into output_dir alongside the tarball
    db_path = output_dir / "lsb.sqlite"
    print("Building lsb.sqlite via scripts/build_db.py …")
    _build_sqlite(repo_root, db_path, dry_run=False)

    if not db_path.exists():
        raise RuntimeError(
            f"Expected lsb.sqlite at {db_path} after build_db.py — file missing"
        )

    # Build MANIFEST.txt content
    manifest_bytes = _build_manifest(
        sources, db_path, sqlite_bundle_path, manifest_bundle_path
    )

    # Write tarball
    tarball_path = output_dir / TARBALL_NAME
    print(f"Assembling {tarball_path} …")

    with tarfile.open(str(tarball_path), "w:gz") as tf:
        # Add source files
        for abs_path, internal_path in sources:
            if abs_path.exists():
                tf.add(str(abs_path), arcname=internal_path)

        # Add lsb.sqlite
        tf.add(str(db_path), arcname=sqlite_bundle_path)

        # Add MANIFEST.txt
        manifest_info = tarfile.TarInfo(name=manifest_bundle_path)
        manifest_info.size = len(manifest_bytes)
        tf.addfile(manifest_info, io.BytesIO(manifest_bytes))

    tarball_size = tarball_path.stat().st_size
    tarball_sha256 = _sha256_file(tarball_path)

    print(f"\nTarball written: {tarball_path}")
    print(f"  size:   {tarball_size:,} bytes")
    print(f"  sha256: {tarball_sha256}")
    print("\nMANIFEST.txt contents:")
    print(manifest_bytes.decode("utf-8"))

    return tarball_path


def verify_bundle(tarball_path: Path) -> bool:
    """Verify a tarball against its embedded MANIFEST.txt.

    Extracts each file, recomputes SHA256, compares to MANIFEST.txt.
    Returns True if all checks pass, False otherwise.
    """
    manifest_internal = f"{BUNDLE_ROOT}/MANIFEST.txt"

    print(f"Verifying {tarball_path} …")

    with tarfile.open(str(tarball_path), "r:gz") as tf:
        # Extract MANIFEST.txt
        try:
            mf = tf.extractfile(manifest_internal)
            if mf is None:
                print(f"ERROR: {manifest_internal} not found in tarball", file=sys.stderr)
                return False
            manifest_content = mf.read().decode("utf-8")
        except KeyError:
            print(f"ERROR: {manifest_internal} not found in tarball", file=sys.stderr)
            return False

        # Parse manifest entries
        expected: dict[str, tuple[str, int]] = {}
        for line in manifest_content.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) != 3:
                print(f"WARNING: malformed manifest line: {line!r}", file=sys.stderr)
                continue
            digest, size_str, path = parts
            expected[path] = (digest, int(size_str))

        # Verify each entry — use chunked reads to avoid OOM on large files
        all_pass = True
        checked = 0
        for internal_path, (exp_digest, exp_size) in sorted(expected.items()):
            try:
                member = tf.extractfile(internal_path)
                if member is None:
                    print(f"FAIL  {internal_path}: directory entry, not a file", file=sys.stderr)
                    all_pass = False
                    continue
                # Stream in 64 KiB chunks to avoid loading 8+ GB into memory
                h = hashlib.sha256()
                actual_size = 0
                while True:
                    chunk = member.read(65536)
                    if not chunk:
                        break
                    h.update(chunk)
                    actual_size += len(chunk)
                actual_sha = h.hexdigest()
            except KeyError:
                print(f"FAIL  {internal_path}: missing from tarball", file=sys.stderr)
                all_pass = False
                continue

            if actual_sha != exp_digest or actual_size != exp_size:
                print(
                    f"FAIL  {internal_path}: "
                    f"expected sha256={exp_digest} size={exp_size}, "
                    f"got sha256={actual_sha} size={actual_size}",
                    file=sys.stderr,
                )
                all_pass = False
            else:
                print(f"OK    {internal_path}")
            checked += 1

    if all_pass:
        print(f"\nVERIFY PASS: all {checked} manifest entries verified.")
    else:
        print("\nVERIFY FAIL: one or more manifest entries failed.", file=sys.stderr)

    return all_pass


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build the LSB open data bundle tarball. "
            "See ARCHITECTURE.md §6.7 and docs/DATA_DICTIONARY.md §0."
        )
    )
    parser.add_argument(
        "--output-dir",
        default="/tmp",
        help="Directory to write the tarball (default: /tmp)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List what would be included; do not write tarball or SQLite",
    )
    parser.add_argument(
        "--verify",
        metavar="PATH",
        default=None,
        help="Verify an existing tarball against its embedded MANIFEST.txt",
    )
    args = parser.parse_args()

    if args.verify:
        tarball_path = Path(args.verify)
        if not tarball_path.exists():
            print(f"Error: {tarball_path} not found.", file=sys.stderr)
            return 1
        ok = verify_bundle(tarball_path)
        return 0 if ok else 1

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        build_bundle(REPO_ROOT, output_dir, dry_run=args.dry_run)
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
