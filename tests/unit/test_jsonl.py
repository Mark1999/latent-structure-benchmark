"""Tests for JSONL reader/writer."""

import tempfile
from datetime import date, datetime
from pathlib import Path

from cdb_collect.jsonl import append_failure, append_record, read_records
from cdb_core import (
    FreelistRecord,
    InformantRecord,
    InterviewRecord,
    PileSortRecord,
)


def _make_record(run_index: int = 0) -> InformantRecord:
    return InformantRecord(
        informant_id=f"test_{run_index}",
        domain_slug="family",
        run_index=run_index,
        collection_date=datetime(2026, 4, 13, 10, 0, 0),
        model_id="claude-opus-4-6",
        model_version_returned="claude-opus-4-6-20260401",
        family="claude",
        provider="anthropic",
        provider_request_id="msg_test123",
        knowledge_cutoff=date(2025, 5, 1),
        open_weights=False,
        origin_country="us",
        alignment_method="Constitutional AI",
        collection_method="anthropic_api",
        api_endpoint="https://api.anthropic.com/v1/messages",
        api_version="2023-06-01",
        temperature=0.7,
        top_p=None,
        max_tokens=4096,
        system_prompt="",
        freelist=FreelistRecord(
            prompt_verbatim="test prompt",
            prompt_version="v1",
            response_verbatim="1. Mother\n2. Father",
            response_object_json={"id": "msg_test"},
            input_tokens=50,
            output_tokens=20,
            latency_ms=500,
            stop_reason="end_turn",
            parsed_items=["mother", "father"],
            parsed_raw_order=["mother", "father"],
        ),
        pile_sort=PileSortRecord(
            prompt_verbatim="",
            prompt_version="v1",
            response_verbatim="",
            response_object_json={},
            input_tokens=0,
            output_tokens=0,
            latency_ms=0,
            stop_reason="not_collected",
            parsed_piles=[],
            parsed_matrix=[],
        ),
        interview=InterviewRecord(
            prompt_verbatim="",
            prompt_version="v1",
            response_verbatim="",
            response_object_json={},
            input_tokens=0,
            output_tokens=0,
            latency_ms=0,
            stop_reason="not_collected",
            parsed_pile_labels=[],
        ),
        sha256_manifest={
            "freelist_prompt": "a" * 64,
            "freelist_response": "b" * 64,
            "pilesort_prompt": "c" * 64,
            "pilesort_response": "d" * 64,
            "interview_prompt": "e" * 64,
            "interview_response": "f" * 64,
            "request_params": "0" * 64,
            "informant_record_total": "1" * 64,
        },
        qa_passed=True,
        qa_notes="",
    )


def test_append_and_read():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "test.jsonl"
        record = _make_record()
        append_record(record, path)

        records = read_records(path)
        assert len(records) == 1
        assert records[0].informant_id == "test_0"
        assert records[0].freelist.parsed_items == ["mother", "father"]


def test_append_multiple():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "test.jsonl"
        append_record(_make_record(0), path)
        append_record(_make_record(1), path)

        records = read_records(path)
        assert len(records) == 2
        assert records[0].run_index == 0
        assert records[1].run_index == 1


def test_read_nonexistent():
    records = read_records(Path("/tmp/nonexistent_jsonl_test.jsonl"))
    assert records == []


def test_append_failure():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "failures.jsonl"
        append_failure(
            ValueError("test error"),
            {"model": "test", "domain": "family"},
            path,
        )
        assert path.exists()
        content = path.read_text().strip()
        assert "test error" in content
        assert "ValueError" in content


def test_creates_parent_dirs():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "sub" / "dir" / "test.jsonl"
        append_record(_make_record(), path)
        assert path.exists()


# ---------------------------------------------------------------------------
# Tests for expanded append_failure kwargs (task #24)
# ---------------------------------------------------------------------------

import json as _json  # noqa: E402 — needed for the new tests below


def _read_failure_entry(path: Path) -> dict:
    """Read the single failure entry from a failures JSONL file."""
    lines = [ln for ln in path.read_text().strip().splitlines() if ln.strip()]
    assert len(lines) == 1, f"Expected 1 line, got {len(lines)}"
    return _json.loads(lines[0])


def test_append_failure_backward_compat(tmp_path: Path) -> None:
    """Existing (error, context, path) call still works.

    Old fields are present; retry_attempts is [] (always written);
    new optional fields are absent.
    """
    path = tmp_path / "failures.jsonl"
    err = RuntimeError("old-style error")
    append_failure(err, {"model_id": "m", "domain": "family", "run_index": 0}, path)

    entry = _read_failure_entry(path)
    assert entry["error_type"] == "RuntimeError"
    assert entry["error_message"] == "old-style error"
    assert entry["context"] == {"model_id": "m", "domain": "family", "run_index": 0}
    assert "timestamp" in entry
    assert entry["retry_attempts"] == []
    # New optional fields must NOT appear when not passed
    for key in ("prompt_verbatim", "response_verbatim", "thinking_verbatim",
                "stop_reason", "partial_session"):
        assert key not in entry, f"Unexpected key '{key}' in backward-compat entry"


def test_append_failure_prompt_verbatim_only(tmp_path: Path) -> None:
    """Passing just prompt_verbatim writes that field and nothing else new."""
    path = tmp_path / "failures.jsonl"
    append_failure(
        ValueError("oops"),
        {"model_id": "m", "domain": "family", "run_index": 1},
        path,
        prompt_verbatim="List every family term you know.",
    )
    entry = _read_failure_entry(path)
    assert entry["prompt_verbatim"] == "List every family term you know."
    assert "response_verbatim" not in entry
    assert "thinking_verbatim" not in entry
    assert "stop_reason" not in entry
    assert "partial_session" not in entry
    assert entry["retry_attempts"] == []


def test_append_failure_response_verbatim_only(tmp_path: Path) -> None:
    path = tmp_path / "failures.jsonl"
    append_failure(
        ValueError("parse error"),
        {"model_id": "m", "domain": "family", "run_index": 2},
        path,
        response_verbatim="```json{}```",
    )
    entry = _read_failure_entry(path)
    assert entry["response_verbatim"] == "```json{}```"
    assert "prompt_verbatim" not in entry


def test_append_failure_thinking_verbatim_only(tmp_path: Path) -> None:
    path = tmp_path / "failures.jsonl"
    append_failure(
        ValueError("no piles"),
        {"model_id": "m", "domain": "family", "run_index": 3},
        path,
        thinking_verbatim="I need to sort these items...",
    )
    entry = _read_failure_entry(path)
    assert entry["thinking_verbatim"] == "I need to sort these items..."
    assert "prompt_verbatim" not in entry


def test_append_failure_stop_reason_only(tmp_path: Path) -> None:
    path = tmp_path / "failures.jsonl"
    append_failure(
        ValueError("truncated"),
        {"model_id": "m", "domain": "holidays", "run_index": 0},
        path,
        stop_reason="MAX_TOKENS",
    )
    entry = _read_failure_entry(path)
    assert entry["stop_reason"] == "MAX_TOKENS"
    assert "prompt_verbatim" not in entry


def test_append_failure_full_kwargs(tmp_path: Path) -> None:
    """All new kwargs populated; verify all fields in documented order."""
    path = tmp_path / "failures.jsonl"
    partial = {
        "freelist": {
            "prompt_verbatim": "List family terms.",
            "response_verbatim": "1. Mother\n2. Father",
            "thinking_verbatim": "",
            "stop_reason": "end_turn",
            "parsed_items": ["mother", "father"],
            "input_tokens": 50,
            "output_tokens": 20,
            "latency_ms": 300,
        }
    }
    retries = [
        {
            "attempt_index": 0,
            "response_verbatim": "",
            "thinking_verbatim": "",
            "stop_reason": "STOP",
            "input_tokens": 100,
            "output_tokens": 0,
            "latency_ms": 200,
            "parse_error_message": "Could not extract valid JSON from response: ",
        }
    ]
    append_failure(
        ValueError("pile sort parse failure"),
        {"model_id": "google/gemini-2.5-pro", "domain": "family", "run_index": 0},
        path,
        prompt_verbatim="Sort these items into piles.",
        response_verbatim="",
        thinking_verbatim="Hmm, I'll group by relationship type.",
        stop_reason="STOP",
        partial_session=partial,
        retry_attempts=retries,
    )
    entry = _read_failure_entry(path)

    # Required fields
    assert entry["error_type"] == "ValueError"
    assert entry["error_message"] == "pile sort parse failure"
    assert entry["prompt_verbatim"] == "Sort these items into piles."
    assert entry["response_verbatim"] == ""
    assert entry["thinking_verbatim"] == "Hmm, I'll group by relationship type."
    assert entry["stop_reason"] == "STOP"
    assert entry["partial_session"] == partial
    assert entry["retry_attempts"] == retries

    # Verify documented field order (timestamp, error_type, error_message, context,
    # prompt_verbatim, response_verbatim, thinking_verbatim, stop_reason,
    # partial_session, retry_attempts)
    keys = list(entry.keys())
    assert keys.index("timestamp") < keys.index("error_type")
    assert keys.index("error_type") < keys.index("error_message")
    assert keys.index("error_message") < keys.index("context")
    assert keys.index("context") < keys.index("prompt_verbatim")
    assert keys.index("prompt_verbatim") < keys.index("response_verbatim")
    assert keys.index("response_verbatim") < keys.index("thinking_verbatim")
    assert keys.index("thinking_verbatim") < keys.index("stop_reason")
    assert keys.index("stop_reason") < keys.index("partial_session")
    assert keys.index("partial_session") < keys.index("retry_attempts")


def test_append_failure_retry_attempts_list(tmp_path: Path) -> None:
    """Three retry dicts serialize as an ordered list."""
    path = tmp_path / "failures.jsonl"
    retries = [
        {
            "attempt_index": 0,
            "response_verbatim": "attempt 0",
            "thinking_verbatim": "",
            "stop_reason": "STOP",
            "input_tokens": 10,
            "output_tokens": 1,
            "latency_ms": 100,
            "parse_error_message": "bad json",
        },
        {
            "attempt_index": 1,
            "response_verbatim": "attempt 1",
            "thinking_verbatim": "",
            "stop_reason": "STOP",
            "input_tokens": 11,
            "output_tokens": 2,
            "latency_ms": 110,
            "parse_error_message": "still bad",
        },
        {
            "attempt_index": 2,
            "response_verbatim": "attempt 2",
            "thinking_verbatim": "",
            "stop_reason": "MAX_TOKENS",
            "input_tokens": 12,
            "output_tokens": 0,
            "latency_ms": 120,
            "parse_error_message": "truncated",
        },
    ]
    append_failure(
        ValueError("exhausted retries"),
        {"model_id": "m", "domain": "family", "run_index": 0},
        path,
        retry_attempts=retries,
    )
    entry = _read_failure_entry(path)
    assert len(entry["retry_attempts"]) == 3
    for i, attempt in enumerate(entry["retry_attempts"]):
        assert attempt["attempt_index"] == i
        assert attempt["response_verbatim"] == f"attempt {i}"


def test_append_failure_partial_session_shape(tmp_path: Path) -> None:
    """partial_session with freelist and pile_sort keys serializes correctly."""
    path = tmp_path / "failures.jsonl"
    partial = {
        "freelist": {
            "prompt_verbatim": "Free list prompt.",
            "response_verbatim": "1. item A\n2. item B",
            "thinking_verbatim": "",
            "stop_reason": "end_turn",
            "parsed_items": ["item a", "item b"],
            "input_tokens": 80,
            "output_tokens": 30,
            "latency_ms": 400,
        },
        "pile_sort": {
            "prompt_verbatim": "Sort these items.",
            "response_verbatim": '{"piles": []}',
            "thinking_verbatim": "",
            "stop_reason": "end_turn",
            "input_tokens": 90,
            "output_tokens": 5,
            "latency_ms": 250,
        },
    }
    append_failure(
        ValueError("interview failed"),
        {"model_id": "m", "domain": "family", "run_index": 4},
        path,
        partial_session=partial,
    )
    entry = _read_failure_entry(path)
    assert "partial_session" in entry
    assert entry["partial_session"]["freelist"]["parsed_items"] == ["item a", "item b"]
    assert entry["partial_session"]["pile_sort"]["response_verbatim"] == '{"piles": []}'
    assert "interview" not in entry["partial_session"]


def test_append_failure_empty_retry_attempts_always_written(tmp_path: Path) -> None:
    """retry_attempts=[] (explicit empty list) is written, not omitted."""
    path = tmp_path / "failures.jsonl"
    append_failure(
        ValueError("http 400"),
        {"model_id": "m", "domain": "family", "run_index": 0},
        path,
        retry_attempts=[],
    )
    entry = _read_failure_entry(path)
    assert "retry_attempts" in entry
    assert entry["retry_attempts"] == []


def test_append_failure_partial_session_none_omitted(tmp_path: Path) -> None:
    """partial_session=None (default) means the key is absent from the entry."""
    path = tmp_path / "failures.jsonl"
    append_failure(
        ValueError("http error"),
        {"model_id": "m", "domain": "holidays", "run_index": 2},
        path,
    )
    entry = _read_failure_entry(path)
    assert "partial_session" not in entry
