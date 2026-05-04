"""JSONL reader/writer for InformantRecords and DeclineInterviews. Append-only by convention."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from cdb_core import InformantRecord
from cdb_core.schemas import DeclineInterview

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
    error: Exception,
    context: dict,
    path: Path,
    *,
    prompt_verbatim: str | None = None,
    response_verbatim: str | None = None,
    thinking_verbatim: str | None = None,
    stop_reason: str | None = None,
    thoughts_token_count: int | None = None,
    partial_session: dict | None = None,
    retry_attempts: list[dict] | None = None,
) -> None:
    """Append a failure record to the failures JSONL file.

    The new keyword-only parameters capture verbatim session bytes for
    the failing step and any steps that completed before the failure.
    Existing callers that pass only (error, context, path) remain
    fully compatible — all new kwargs default to None / [].

    Field order in the written JSONL entry (for audit readability):
      timestamp, error_type, error_message, context,
      prompt_verbatim (if present), response_verbatim (if present),
      thinking_verbatim (if present), stop_reason (if present),
      thoughts_token_count (if non-None), partial_session (if present),
      retry_attempts (always, min []).

    Args:
        error: The exception that caused the failure.
        context: Dict with at minimum {model_id, domain, run_index}.
        path: Path to the failures JSONL file.
        prompt_verbatim: Exact prompt sent on the failing step (or final
            retry for pile-sort parse-retry exhaustion).
        response_verbatim: Exact response bytes from the failing step
            (or final retry).
        thinking_verbatim: Reasoning trace if the adapter surfaced one
            on the failing step.
        stop_reason: The adapter's stop_reason on the failing step.
        thoughts_token_count: Provider-reported reasoning token count for
            the failing step. Written as a top-level field after
            stop_reason when non-None. Use 0 for providers that do not
            surface reasoning tokens (Anthropic, HuggingFace). Omitted
            entirely when None (request never completed or not captured).
            See docs/DATA_DICTIONARY.md §9.2 for field semantics.
        partial_session: Dict shaped as
            {freelist?: FreelistRecord-dict,
             pile_sort?: PileSortRecord-dict,
             interview?: InterviewRecord-dict}.
            Each sub-object carries the full step-record shape for any
            step that completed before the failure. Omitted entirely
            (not written as null) when None, to keep entries compact.
        retry_attempts: Ordered list of per-retry dicts for pile-sort
            parse-retry exhaustion. Each entry carries:
            {attempt_index, response_verbatim, thinking_verbatim,
             stop_reason, input_tokens, output_tokens,
             thoughts_token_count, latency_ms, parse_error_message}.
            Written as [] when None (no retry loop fired).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    entry: dict = {
        "timestamp": datetime.now().isoformat(),
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
    }
    if prompt_verbatim is not None:
        entry["prompt_verbatim"] = prompt_verbatim
    if response_verbatim is not None:
        entry["response_verbatim"] = response_verbatim
    if thinking_verbatim is not None:
        entry["thinking_verbatim"] = thinking_verbatim
    if stop_reason is not None:
        entry["stop_reason"] = stop_reason
    if thoughts_token_count is not None:
        entry["thoughts_token_count"] = thoughts_token_count
    if partial_session is not None:
        entry["partial_session"] = partial_session
    entry["retry_attempts"] = retry_attempts if retry_attempts is not None else []
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def append_decline_interview(interview: DeclineInterview, path: Path) -> None:
    """Append one DeclineInterview as a JSONL line. Mirrors append_record.

    Creates the file and parent directories if they don't exist.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(interview.model_dump_json() + "\n")
