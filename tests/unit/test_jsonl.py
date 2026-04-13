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
