"""Record loader for the LSB ops dashboard.

Reads InformantRecord and DeclineInterview objects from JSONL data files
and provides index and filter helpers for the Streamlit pages.

READ-ONLY INVARIANT: every function in this module is a pure reader.
No file is opened for writing. No sqlite3 INSERT/UPDATE/DELETE/CREATE/DROP.
No LLM client imports.

See ARCHITECTURE.md §3.2 for the InformantRecord / DeclineInterview schemas
and docs/DATA_DICTIONARY.md §1.1 / §10 for field semantics.
"""

from __future__ import annotations

import json
from pathlib import Path

from cdb_core.schemas import DeclineInterview, InformantRecord


def load_informants(jsonl_path: Path) -> list[InformantRecord]:
    """Parse every line of a JSONL file as an InformantRecord.

    Args:
        jsonl_path: Path to the JSONL file (typically data/raw/informants.jsonl).

    Returns:
        List of InformantRecord objects, one per non-empty line.
        An empty file returns an empty list.

    Raises:
        ValueError: If a line cannot be parsed as valid JSON or fails
            InformantRecord validation, naming the 1-indexed line number.
    """
    records: list[InformantRecord] = []
    with jsonl_path.open("r", encoding="utf-8") as fh:
        for line_num, raw_line in enumerate(fh, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"informants.jsonl line {line_num}: invalid JSON — {exc}"
                ) from exc
            try:
                records.append(InformantRecord.model_validate(obj))
            except Exception as exc:
                raise ValueError(
                    f"informants.jsonl line {line_num}: schema validation failed — {exc}"
                ) from exc
    return records


def index_by_run_id(records: list[InformantRecord]) -> dict[str, InformantRecord]:
    """Return a mapping of informant_id to InformantRecord.

    The key is InformantRecord.informant_id, which is the unique run
    identifier (see DATA_DICTIONARY.md §1.1). The parameter and function
    name use "run_id" to match the ops dashboard's internal vocabulary;
    the underlying field on the schema is informant_id.

    Args:
        records: List of InformantRecord objects.

    Returns:
        Dict mapping informant_id -> InformantRecord.

    Raises:
        ValueError: If any two records share the same informant_id, which
            violates the append-only contract on informants.jsonl.
    """
    index: dict[str, InformantRecord] = {}
    for rec in records:
        if rec.informant_id in index:
            raise ValueError(
                f"Duplicate informant_id detected: '{rec.informant_id}'. "
                "The informants.jsonl append-only contract is violated — "
                "two records share the same primary key."
            )
        index[rec.informant_id] = rec
    return index


def index_by_model_id(
    records: list[InformantRecord],
) -> dict[str, list[InformantRecord]]:
    """Return a mapping of model_id to list of InformantRecord objects.

    Args:
        records: List of InformantRecord objects.

    Returns:
        Dict mapping model_id -> list of InformantRecord. Keys are the
        distinct model_id values present in the input; the insertion order
        of first appearance is preserved.
    """
    index: dict[str, list[InformantRecord]] = {}
    for rec in records:
        index.setdefault(rec.model_id, []).append(rec)
    return index


def index_by_domain(
    records: list[InformantRecord],
) -> dict[str, list[InformantRecord]]:
    """Return a mapping of domain_slug to list of InformantRecord objects.

    Args:
        records: List of InformantRecord objects.

    Returns:
        Dict mapping domain_slug -> list of InformantRecord. Keys are the
        distinct domain_slug values present in the input; the insertion
        order of first appearance is preserved.
    """
    index: dict[str, list[InformantRecord]] = {}
    for rec in records:
        index.setdefault(rec.domain_slug, []).append(rec)
    return index


def filter_records(
    records: list[InformantRecord],
    *,
    model_id: str | None = None,
    domain: str | None = None,
) -> list[InformantRecord]:
    """Return records matching the supplied filter criteria.

    Filters are ANDed: a record must satisfy every non-None criterion.
    If both arguments are None, all records are returned unchanged.

    Args:
        records: List of InformantRecord objects to filter.
        model_id: If set, keep only records whose model_id matches exactly.
        domain: If set, keep only records whose domain_slug matches exactly.

    Returns:
        Filtered list of InformantRecord objects (may be empty).
    """
    result = records
    if model_id is not None:
        result = [r for r in result if r.model_id == model_id]
    if domain is not None:
        result = [r for r in result if r.domain_slug == domain]
    return result


def load_decline_interviews(jsonl_path: Path) -> list[DeclineInterview]:
    """Parse every line of a JSONL file as a DeclineInterview.

    The on-disk format may include extra fields (e.g. ``cost_usd``) that
    postdate the current schema. Pydantic ignores unknown fields by default,
    so extra fields are silently dropped during model_validate.

    Args:
        jsonl_path: Path to the JSONL file (typically
            data/raw/decline_interviews.jsonl). If the file does not exist,
            an empty list is returned (so callers need not check existence
            before calling).

    Returns:
        List of DeclineInterview objects, one per non-empty line.
        An empty file or missing file returns an empty list.

    Raises:
        ValueError: If a line cannot be parsed as valid JSON or fails
            DeclineInterview validation, naming the 1-indexed line number.
    """
    if not jsonl_path.exists():
        return []
    records: list[DeclineInterview] = []
    with jsonl_path.open("r", encoding="utf-8") as fh:
        for line_num, raw_line in enumerate(fh, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{jsonl_path.name} line {line_num}: invalid JSON — {exc}"
                ) from exc
            try:
                records.append(DeclineInterview.model_validate(obj))
            except Exception as exc:
                raise ValueError(
                    f"{jsonl_path.name} line {line_num}: schema validation failed — {exc}"
                ) from exc
    return records


def load_jsonl_dicts(jsonl_path: Path) -> list[dict]:
    """Parse every line of a JSONL file as a plain dict.

    Used for derived files (manual_classification, safety_attribution_subtype)
    whose schema is not a Pydantic model in cdb_core.

    Args:
        jsonl_path: Path to the JSONL file. If the file does not exist,
            an empty list is returned.

    Returns:
        List of dict objects, one per non-empty line.
        An empty file or missing file returns an empty list.

    Raises:
        ValueError: If a line cannot be parsed as valid JSON, naming the
            1-indexed line number.
    """
    if not jsonl_path.exists():
        return []
    results: list[dict] = []
    with jsonl_path.open("r", encoding="utf-8") as fh:
        for line_num, raw_line in enumerate(fh, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{jsonl_path.name} line {line_num}: invalid JSON — {exc}"
                ) from exc
    return results
