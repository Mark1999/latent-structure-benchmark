"""JSONL reader/writer for InformantRecords. Append-only by convention."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from cdb_core import InformantRecord

logger = logging.getLogger(__name__)


def append_record(record: InformantRecord, path: Path) -> None:
    """Append a single InformantRecord as one JSONL line.

    Creates the file and parent directories if they don't exist.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(record.model_dump_json() + "\n")


def read_records(path: Path) -> list[InformantRecord]:
    """Read all InformantRecords from a JSONL file."""
    if not path.exists():
        return []

    records: list[InformantRecord] = []
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(InformantRecord.model_validate_json(line))
            except Exception as e:
                logger.warning("Skipping invalid record at line %d: %s", line_num, e)

    return records


def append_failure(
    error: Exception, context: dict, path: Path,
) -> None:
    """Append a failure record to the failures JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
