"""Build SQLite database from informants.jsonl for the open data bundle.

See ARCHITECTURE.md §4.3, §6.7 and docs/DATA_DICTIONARY.md §4.

Usage:
    python scripts/build_db.py [informants.jsonl] [lsb.sqlite]
    python scripts/build_db.py                           # uses default paths
    python scripts/build_db.py --dry-run                 # report record count without writing

**Shakedown exclusion (binding per docs/SHAKEDOWN_PROTOCOL.md §2).** This
script refuses to build a canonical SQLite from any path under
``data/shakedown/``. Shakedown runs are diagnostic-only and must be
machine-prevented from entering the canonical open-data bundle. The
exclusion is the fourth of four labeling layers (path, gitignore,
build-script exclusion, per-record campaign tag).
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

# Path segment that, if present in the input JSONL path, causes
# build_db to refuse the build. Per docs/SHAKEDOWN_PROTOCOL.md §2.
SHAKEDOWN_PATH_SEGMENT: str = "shakedown"

# ── DDL from docs/DATA_DICTIONARY.md §4 ────────────────────────────────

_DDL = """
CREATE TABLE informants (
  informant_id TEXT PRIMARY KEY,
  domain_slug TEXT NOT NULL,
  run_index INTEGER NOT NULL,
  collection_date TEXT NOT NULL,
  collection_mode TEXT NOT NULL DEFAULT 'single_pass',

  model_id TEXT NOT NULL,
  model_version_returned TEXT NOT NULL,
  family TEXT NOT NULL,
  provider TEXT NOT NULL,
  provider_request_id TEXT NOT NULL,
  knowledge_cutoff TEXT,
  open_weights INTEGER NOT NULL,
  origin_country TEXT NOT NULL,
  alignment_method TEXT,

  collection_method TEXT NOT NULL,
  api_endpoint TEXT NOT NULL,
  api_version TEXT NOT NULL,
  temperature REAL NOT NULL,
  top_p REAL,
  max_tokens INTEGER NOT NULL,
  system_prompt TEXT NOT NULL,

  freelist_prompt_verbatim TEXT NOT NULL,
  freelist_response_verbatim TEXT NOT NULL,
  freelist_input_tokens INTEGER NOT NULL,
  freelist_output_tokens INTEGER NOT NULL,
  freelist_thoughts_token_count INTEGER NOT NULL DEFAULT 0,
  freelist_latency_ms INTEGER NOT NULL,
  freelist_stop_reason TEXT NOT NULL,

  pilesort_prompt_verbatim TEXT NOT NULL,
  pilesort_response_verbatim TEXT NOT NULL,
  pilesort_input_tokens INTEGER NOT NULL,
  pilesort_output_tokens INTEGER NOT NULL,
  pilesort_thoughts_token_count INTEGER NOT NULL DEFAULT 0,
  pilesort_latency_ms INTEGER NOT NULL,
  pilesort_stop_reason TEXT NOT NULL,
  pilesort_item_source TEXT NOT NULL DEFAULT 'own_freelist',

  interview_prompt_verbatim TEXT NOT NULL,
  interview_response_verbatim TEXT NOT NULL,
  interview_input_tokens INTEGER NOT NULL,
  interview_output_tokens INTEGER NOT NULL,
  interview_thoughts_token_count INTEGER NOT NULL DEFAULT 0,
  interview_latency_ms INTEGER NOT NULL,
  interview_stop_reason TEXT NOT NULL,

  sha256_manifest_json TEXT NOT NULL,

  qa_passed INTEGER NOT NULL,
  qa_notes TEXT NOT NULL DEFAULT ''
);

CREATE INDEX idx_informants_domain ON informants(domain_slug);
CREATE INDEX idx_informants_model ON informants(model_id);
CREATE INDEX idx_informants_model_version ON informants(model_version_returned);
CREATE INDEX idx_informants_collection_date ON informants(collection_date);
CREATE INDEX idx_informants_provider ON informants(provider);
CREATE INDEX idx_informants_qa_passed ON informants(qa_passed);

CREATE TABLE freelist_items (
  informant_id TEXT NOT NULL,
  rank INTEGER NOT NULL,
  item TEXT NOT NULL,
  is_truncated_in INTEGER NOT NULL,
  PRIMARY KEY (informant_id, rank),
  FOREIGN KEY (informant_id) REFERENCES informants(informant_id)
);

CREATE INDEX idx_freelist_items_informant ON freelist_items(informant_id);
CREATE INDEX idx_freelist_items_item ON freelist_items(item);

CREATE TABLE pilesort_cells (
  informant_id TEXT NOT NULL,
  item_a TEXT NOT NULL,
  item_b TEXT NOT NULL,
  in_same_pile INTEGER NOT NULL,
  PRIMARY KEY (informant_id, item_a, item_b),
  FOREIGN KEY (informant_id) REFERENCES informants(informant_id)
);

CREATE INDEX idx_pilesort_cells_informant ON pilesort_cells(informant_id);
CREATE INDEX idx_pilesort_cells_item_a ON pilesort_cells(item_a);

CREATE TABLE interview_labels (
  informant_id TEXT NOT NULL,
  pile_index INTEGER NOT NULL,
  label TEXT NOT NULL,
  PRIMARY KEY (informant_id, pile_index),
  FOREIGN KEY (informant_id) REFERENCES informants(informant_id)
);

CREATE INDEX idx_interview_labels_informant ON interview_labels(informant_id);

CREATE TABLE decline_interviews (
  decline_interview_id TEXT PRIMARY KEY,
  originating_informant_id TEXT,
  originating_failure_id TEXT,
  originating_step TEXT NOT NULL,
  originating_outcome_class TEXT NOT NULL,
  detection_rule_version TEXT NOT NULL,
  detection_timestamp TEXT NOT NULL,
  followup_timestamp TEXT NOT NULL,
  model_id TEXT NOT NULL,
  model_version_returned TEXT NOT NULL,
  provider TEXT NOT NULL,
  api_endpoint TEXT NOT NULL,
  prompt_version TEXT NOT NULL,
  sha256_manifest TEXT NOT NULL,
  prompt_verbatim TEXT NOT NULL,
  response_verbatim TEXT NOT NULL,
  thinking_verbatim TEXT NOT NULL DEFAULT '',
  input_tokens INTEGER NOT NULL,
  output_tokens INTEGER NOT NULL,
  latency_ms INTEGER NOT NULL,
  stop_reason TEXT NOT NULL,
  qa_notes TEXT NOT NULL DEFAULT '',
  version_drift_flag INTEGER NOT NULL DEFAULT 0,
  FOREIGN KEY (originating_informant_id) REFERENCES informants(informant_id)
);

CREATE INDEX idx_decline_interviews_informant ON decline_interviews(originating_informant_id);
CREATE INDEX idx_decline_interviews_model ON decline_interviews(model_id);
CREATE INDEX idx_decline_interviews_outcome ON decline_interviews(originating_outcome_class);
CREATE INDEX idx_decline_interviews_step ON decline_interviews(originating_step);
"""


def _parse_record(line: str) -> dict:
    """Parse one JSONL line into a dict, or raise on bad JSON."""
    return json.loads(line)


def _insert_decline_interview(cur: sqlite3.Cursor, rec: dict) -> None:
    """Insert one DeclineInterview record into the decline_interviews table."""
    cur.execute(
        """
        INSERT OR IGNORE INTO decline_interviews VALUES (
          ?, ?, ?, ?, ?,
          ?, ?, ?,
          ?, ?, ?, ?,
          ?, ?, ?, ?,
          ?, ?, ?, ?,
          ?, ?, ?
        )
        """,
        (
            rec["decline_interview_id"],
            rec.get("originating_informant_id"),
            rec.get("originating_failure_id"),
            rec["originating_step"],
            rec["originating_outcome_class"],
            rec["detection_rule_version"],
            rec["detection_timestamp"],
            rec["followup_timestamp"],
            rec["model_id"],
            rec["model_version_returned"],
            rec["provider"],
            rec["api_endpoint"],
            rec["prompt_version"],
            rec["sha256_manifest"],
            rec["prompt_verbatim"],
            rec["response_verbatim"],
            rec.get("thinking_verbatim", ""),
            rec["input_tokens"],
            rec["output_tokens"],
            rec["latency_ms"],
            rec["stop_reason"],
            rec.get("qa_notes", ""),
            1 if rec.get("version_drift_flag", False) else 0,
        ),
    )


def _insert_informant(cur: sqlite3.Cursor, rec: dict) -> None:
    """Insert one InformantRecord into all four tables."""
    fl = rec.get("freelist", {})
    ps = rec.get("pile_sort", {})
    iv = rec.get("interview", {})

    cur.execute(
        """
        INSERT OR IGNORE INTO informants VALUES (
          ?, ?, ?, ?, ?,
          ?, ?, ?, ?, ?,
          ?, ?, ?, ?,
          ?, ?, ?, ?, ?, ?, ?,
          ?, ?, ?, ?, ?, ?, ?,
          ?, ?, ?, ?, ?, ?, ?, ?,
          ?, ?, ?, ?, ?, ?, ?,
          ?,
          ?, ?
        )
        """,
        (
            rec["informant_id"],
            rec["domain_slug"],
            rec["run_index"],
            rec["collection_date"],
            rec.get("collection_mode", "single_pass"),
            # Model identity
            rec["model_id"],
            rec["model_version_returned"],
            rec["family"],
            rec["provider"],
            rec["provider_request_id"],
            rec.get("knowledge_cutoff"),
            1 if rec["open_weights"] else 0,
            rec["origin_country"],
            rec.get("alignment_method"),
            # Collection conditions
            rec["collection_method"],
            rec["api_endpoint"],
            rec["api_version"],
            rec["temperature"],
            rec.get("top_p"),
            rec["max_tokens"],
            rec["system_prompt"],
            # Freelist step
            fl["prompt_verbatim"],
            fl["response_verbatim"],
            fl["input_tokens"],
            fl["output_tokens"],
            fl.get("thoughts_token_count", 0),
            fl["latency_ms"],
            fl["stop_reason"],
            # Pile sort step
            ps["prompt_verbatim"],
            ps["response_verbatim"],
            ps["input_tokens"],
            ps["output_tokens"],
            ps.get("thoughts_token_count", 0),
            ps["latency_ms"],
            ps["stop_reason"],
            ps.get("item_source", "own_freelist"),
            # Interview step
            iv["prompt_verbatim"],
            iv["response_verbatim"],
            iv["input_tokens"],
            iv["output_tokens"],
            iv.get("thoughts_token_count", 0),
            iv["latency_ms"],
            iv["stop_reason"],
            # Provenance
            json.dumps(rec["sha256_manifest"], sort_keys=True),
            # QA
            1 if rec["qa_passed"] else 0,
            rec.get("qa_notes", ""),
        ),
    )

    informant_id = rec["informant_id"]

    # ── freelist_items ──
    parsed_items = set(fl.get("parsed_items", []))
    for rank, item in enumerate(fl.get("parsed_raw_order", [])):
        cur.execute(
            "INSERT OR IGNORE INTO freelist_items VALUES (?, ?, ?, ?)",
            (informant_id, rank, item, 1 if item in parsed_items else 0),
        )

    # ── pilesort_cells ──
    ps_items = fl.get("parsed_items", [])
    matrix = ps.get("parsed_matrix", [])
    if matrix and ps_items:
        for i, row in enumerate(matrix):
            for j, val in enumerate(row):
                cur.execute(
                    "INSERT OR IGNORE INTO pilesort_cells VALUES (?, ?, ?, ?)",
                    (informant_id, ps_items[i], ps_items[j], val),
                )

    # ── interview_labels ──
    for pile_index, label in enumerate(iv.get("parsed_pile_labels", [])):
        cur.execute(
            "INSERT OR IGNORE INTO interview_labels VALUES (?, ?, ?)",
            (informant_id, pile_index, label),
        )


def _refuse_shakedown_path(jsonl_path: Path) -> None:
    """Raise if the input path is under a shakedown directory.

    Per docs/SHAKEDOWN_PROTOCOL.md §2: shakedown data is machine-
    prevented from being confused with canonical data. The bundle-build
    script cannot ingest shakedown records even if asked — this is the
    fourth labeling layer (after path segregation, gitignore, and the
    per-record campaign tag).

    The check looks for the literal segment ``shakedown`` anywhere in
    the resolved path parts. Any use of ``data/shakedown/...`` trips
    the refusal. To run a shakedown analysis locally, use
    ``scripts/analyze.py`` directly against the JSONL — that script
    produces diagnostic DomainResult JSON and does NOT feed the
    canonical SQLite bundle.
    """
    resolved = jsonl_path.resolve()
    if SHAKEDOWN_PATH_SEGMENT in resolved.parts:
        msg = (
            f"Refusing to build canonical SQLite from a shakedown path: {jsonl_path}. "
            f"Shakedown data is diagnostic-only and must not enter the open data bundle. "
            f"See docs/SHAKEDOWN_PROTOCOL.md §2. Use scripts/analyze.py for shakedown analysis."
        )
        raise ValueError(msg)


def build_db(
    jsonl_path: Path,
    db_path: Path,
    decline_interviews_path: Path | None = None,
) -> tuple[int, int]:
    """Read informants.jsonl (and optionally decline_interviews.jsonl) and write lsb.sqlite.

    Returns:
        (informant_count, decline_interview_count) tuple.
    """
    _refuse_shakedown_path(jsonl_path)
    if not jsonl_path.exists():
        print(f"Error: {jsonl_path} not found.", file=sys.stderr)
        return 0, 0

    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove existing DB so we always rebuild from scratch
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()

    cur.executescript(_DDL)

    informant_count = 0
    with open(jsonl_path) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = _parse_record(line)
                _insert_informant(cur, rec)
                informant_count += 1
            except (json.JSONDecodeError, KeyError) as e:
                print(
                    f"Warning: skipping informants line {line_num}: {e}",
                    file=sys.stderr,
                )

    decline_count = 0
    if decline_interviews_path is not None and decline_interviews_path.exists():
        with open(decline_interviews_path) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = _parse_record(line)
                    _insert_decline_interview(cur, rec)
                    decline_count += 1
                except (json.JSONDecodeError, KeyError) as e:
                    print(
                        f"Warning: skipping decline_interviews line {line_num}: {e}",
                        file=sys.stderr,
                    )

    conn.commit()
    conn.close()
    return informant_count, decline_count


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build lsb.sqlite from informants.jsonl. "
        "See docs/DATA_DICTIONARY.md §4.",
    )
    parser.add_argument(
        "jsonl",
        nargs="?",
        default="data/raw/informants.jsonl",
        help="Path to informants.jsonl (default: data/raw/informants.jsonl)",
    )
    parser.add_argument(
        "db",
        nargs="?",
        default="data/open_bundle/lsb.sqlite",
        help="Output SQLite path (default: data/open_bundle/lsb.sqlite)",
    )
    parser.add_argument(
        "--decline-interviews",
        default=None,
        help=(
            "Path to decline_interviews.jsonl "
            "(default: auto-detect at data/raw/decline_interviews.jsonl)"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Count records without writing the database",
    )

    args = parser.parse_args()
    jsonl_path = Path(args.jsonl)

    # Shakedown refusal applies to --dry-run too — the script must
    # consistently refuse to acknowledge shakedown paths as canonical
    # inputs, whether or not a DB is actually being written.
    try:
        _refuse_shakedown_path(jsonl_path)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    if args.dry_run:
        if not jsonl_path.exists():
            print(f"Error: {jsonl_path} not found.", file=sys.stderr)
            return 1
        with open(jsonl_path) as f:
            count = sum(1 for line in f if line.strip())
        print(f"DRY RUN: {count} records in {jsonl_path}")
        return 0

    db_path = Path(args.db)

    # Resolve the decline-interviews path: use the explicit arg if given,
    # otherwise check the default sibling location.
    if args.decline_interviews is not None:
        decline_path: Path | None = Path(args.decline_interviews)
    else:
        default_decline = jsonl_path.parent / "decline_interviews.jsonl"
        decline_path = default_decline if default_decline.exists() else None

    informant_count, decline_count = build_db(jsonl_path, db_path, decline_path)

    if informant_count == 0:
        print("No informant records written.", file=sys.stderr)
        return 1

    # Report table counts
    conn = sqlite3.connect(str(db_path))
    informants = conn.execute("SELECT COUNT(*) FROM informants").fetchone()[0]
    fl_items = conn.execute("SELECT COUNT(*) FROM freelist_items").fetchone()[0]
    ps_cells = conn.execute("SELECT COUNT(*) FROM pilesort_cells").fetchone()[0]
    iv_labels = conn.execute("SELECT COUNT(*) FROM interview_labels").fetchone()[0]
    di_rows = conn.execute("SELECT COUNT(*) FROM decline_interviews").fetchone()[0]
    conn.close()

    print(f"Built {db_path}:")
    print(f"  informants:          {informants}")
    print(f"  freelist_items:      {fl_items}")
    print(f"  pilesort_cells:      {ps_cells}")
    print(f"  interview_labels:    {iv_labels}")
    print(f"  decline_interviews:  {di_rows}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
