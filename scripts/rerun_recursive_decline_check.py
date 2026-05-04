"""Phase 4a.1 T-R2 — corrected-detector re-classification of 24 T3B records.

Read-only re-classification of the 24 T3B decline-interview records using
the corrected _is_recursive_decline() detector (post-T-R1). This script does
NOT modify decline_interviews.jsonl; it is a one-shot audit on immutable JSONL.

Per Amendment 2 §2 T-R2 spec:
  - Imports corrected detector from scripts.run_decline_backfill (do NOT
    re-implement detector logic here)
  - Filters to T3B records: originating_failure_id non-null AND
    detection_timestamp == "2026-04-23T23:21:44.547995+00:00" (UTC-equivalent)
  - Prints per-record table and summary line
  - Exits 0 on clean run regardless of flag count; exits 1 only on IO/parse errors

Files modified: NONE (read-only on decline_interviews.jsonl)

References:
  Architect plan Amendment 2: docs/status/2026-04-23-phase4a1-architect-plan-amendment-2.md §2 T-R2
  SME verdict (spec source):  docs/status/2026-04-23-phase4a1-t3b-detector-cda-sme-verdict.md Q1.F
  T3B run log:                docs/status/2026-04-23-phase4a1-t3b-run-log.md
  T-R1 commit:                ce3da31

Exit codes:
  0 — clean run (regardless of corrected flag count)
  1 — IO or parse error
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure the repo root is on sys.path so that `scripts.run_decline_backfill`
# is importable when this script is invoked as:
#   cd /opt/lsb-agent && uv run python scripts/rerun_recursive_decline_check.py
# (pytest's pythonpath=["."] only applies during test collection, not at
# direct script invocation time.)
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT_FOR_IMPORT = _SCRIPT_DIR.parent
if str(_REPO_ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT_FOR_IMPORT))

# Import the corrected detector and its constants from the post-T-R1 backfill
# script. Per T-R2 spec: DO NOT re-implement detector logic locally.
# noqa: E402 applies below because sys.path is set up above before this import.
from scripts.run_decline_backfill import (  # noqa: E402
    MIN_SUBSTANTIVE_RESPONSE_LEN,
    RECURSIVE_DECLINE_PHRASES,
    _is_recursive_decline,
)

# ── Constants ──────────────────────────────────────────────────────────────────

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DECLINE_INTERVIEWS_PATH = _REPO_ROOT / "data" / "raw" / "decline_interviews.jsonl"

# T3B batch detection_timestamp as recorded in the T3B run log
# (docs/status/2026-04-23-phase4a1-t3b-run-log.md §"Execute output").
# The spec names this as "2026-04-23T23:21:44.547995+00:00"; the stored value
# uses the UTC-equivalent "Z" suffix. Both are compared after normalizing
# the trailing UTC designator to a canonical form.
_T3B_TIMESTAMP_CANONICAL = "2026-04-23T23:21:44.547995"


def _normalize_timestamp(ts: str) -> str:
    """Strip trailing UTC designator ('Z' or '+00:00') to compare the
    date-time body only. Both forms denote identical instants.
    """
    ts = ts.strip()
    if ts.endswith("+00:00"):
        return ts[: -len("+00:00")]
    if ts.endswith("Z"):
        return ts[:-1]
    return ts


def _is_t3b_record(record: dict) -> bool:
    """Return True if the record belongs to the T3B batch.

    Criteria (per Amendment 2 §2 T-R2):
      - originating_failure_id is non-null
      - detection_timestamp == "2026-04-23T23:21:44.547995+00:00" (UTC-equivalent)
    """
    if record.get("originating_failure_id") is None:
        return False
    ts = record.get("detection_timestamp", "")
    return _normalize_timestamp(ts) == _T3B_TIMESTAMP_CANONICAL


def _extract_domain(failure_id: str) -> str:
    """Extract domain from originating_failure_id.

    Format: failure|<model_id>|<domain>|<run_index>|<timestamp>
    Returns the domain component (index 2), or "unknown" on parse failure.
    """
    parts = failure_id.split("|")
    if len(parts) >= 3:
        return parts[2]
    return "unknown"


def _trigger_reason(response_verbatim: str) -> str:
    """Return a one-phrase trigger reason for a response that _is_recursive_decline()
    returns True on, or empty string if it returns False.

    Per T-R2 spec: trigger reason is one of:
      empty/whitespace
      length<40
      phrase:<matched_phrase>
    """
    rv = response_verbatim or ""
    rv_stripped = rv.strip()

    if not rv_stripped:
        return "empty/whitespace"
    if len(rv_stripped) < MIN_SUBSTANTIVE_RESPONSE_LEN:
        return "length<40"
    rv_lower = rv_stripped.lower()
    for phrase in RECURSIVE_DECLINE_PHRASES:
        if phrase in rv_lower:
            return f"phrase:{phrase}"
    return ""


def main() -> None:
    """Run the T-R2 corrected-detector re-classification and print results."""
    # Verify the input path is accessible (read-only check)
    if not _DECLINE_INTERVIEWS_PATH.exists():
        print(
            f"ERROR: {_DECLINE_INTERVIEWS_PATH} does not exist",
            file=sys.stderr,
        )
        sys.exit(1)

    # Load all records
    try:
        records: list[dict] = []
        with _DECLINE_INTERVIEWS_PATH.open("r", encoding="utf-8") as fh:
            for lineno, raw_line in enumerate(fh, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    print(
                        f"ERROR: JSON parse failure at line {lineno}: {exc}",
                        file=sys.stderr,
                    )
                    sys.exit(1)
    except OSError as exc:
        print(f"ERROR: Cannot read {_DECLINE_INTERVIEWS_PATH}: {exc}", file=sys.stderr)
        sys.exit(1)

    # Filter to T3B batch
    t3b_records = [r for r in records if _is_t3b_record(r)]
    n_t3b = len(t3b_records)

    if n_t3b != 24:
        print(
            f"ERROR: Expected exactly 24 T3B records; found {n_t3b}. "
            "Check detection_timestamp filter and file integrity.",
            file=sys.stderr,
        )
        sys.exit(1)

    # ── Header ────────────────────────────────────────────────────────────────
    print("Phase 4a.1 T-R2 — corrected detector re-classification of 24 T3B records")
    print()

    # ── Per-record table ───────────────────────────────────────────────────────
    col_w = {
        "idx": 4,
        "identifier": 70,
        "model_id": 40,
        "domain": 10,
        "flag": 14,
        "trigger": 35,
    }
    header = (
        f"{'idx':<{col_w['idx']}}  "
        f"{'originating_failure_id':<{col_w['identifier']}}  "
        f"{'model_id':<{col_w['model_id']}}  "
        f"{'domain':<{col_w['domain']}}  "
        f"{'corrected_flag':<{col_w['flag']}}  "
        f"{'trigger_reason':<{col_w['trigger']}}"
    )
    separator = "-" * len(header)
    print(header)
    print(separator)

    flag_count = 0
    for idx, record in enumerate(t3b_records):
        failure_id: str = record.get("originating_failure_id") or ""
        model_id: str = record.get("model_id") or ""
        domain: str = _extract_domain(failure_id)
        response_verbatim: str = record.get("response_verbatim") or ""

        corrected_flag = _is_recursive_decline(response_verbatim)
        trigger = _trigger_reason(response_verbatim) if corrected_flag else ""

        if corrected_flag:
            flag_count += 1

        # Truncate long fields for display (identifier is the key one)
        id_w = col_w["identifier"]
        disp_id = failure_id if len(failure_id) <= id_w else failure_id[: id_w - 1] + "…"
        m_w = col_w["model_id"]
        disp_model = model_id if len(model_id) <= m_w else model_id[: m_w - 1] + "…"

        row = (
            f"{idx:<{col_w['idx']}}  "
            f"{disp_id:<{col_w['identifier']}}  "
            f"{disp_model:<{col_w['model_id']}}  "
            f"{domain:<{col_w['domain']}}  "
            f"{str(corrected_flag):<{col_w['flag']}}  "
            f"{trigger:<{col_w['trigger']}}"
        )
        print(row)

    print(separator)

    # ── Summary line ──────────────────────────────────────────────────────────
    print()
    print(f"Corrected flags: {flag_count} of {n_t3b}")


if __name__ == "__main__":
    main()
