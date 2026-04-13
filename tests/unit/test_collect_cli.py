"""Tests for collect.py CLI. No real API calls."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

from scripts.collect import collect


def test_dry_run(capsys):
    result = asyncio.run(
        collect(
            model_id="claude-opus-4-6",
            domain_slug="family",
            runs=3,
            dry_run=True,
        )
    )
    assert result == 0
    captured = capsys.readouterr()
    assert "DRY RUN" in captured.out
    assert "claude-opus-4-6" in captured.out
    assert "family" in captured.out


def test_unknown_model(capsys):
    result = asyncio.run(
        collect(
            model_id="nonexistent-model-xyz",
            domain_slug="family",
            runs=1,
        )
    )
    assert result == 0
    captured = capsys.readouterr()
    assert "Unknown model" in captured.err


def test_collect_with_mock_adapter(capsys):
    """Test that collect runs the runner the correct number of times."""
    from datetime import datetime

    from cdb_core import FreelistRecord, InformantRecord, InterviewRecord, PileSortRecord

    mock_record = InformantRecord(
        informant_id="test_0",
        domain_slug="family",
        run_index=0,
        collection_date=datetime(2026, 4, 13),
        model_id="claude-opus-4-6",
        model_version_returned="claude-opus-4-6-20260401",
        family="claude",
        provider="anthropic",
        provider_request_id="msg_test",
        knowledge_cutoff=None,
        open_weights=False,
        origin_country="us",
        alignment_method=None,
        collection_method="anthropic_api",
        api_endpoint="https://api.anthropic.com/v1/messages",
        api_version="2023-06-01",
        temperature=0.7,
        top_p=None,
        max_tokens=4096,
        system_prompt="",
        freelist=FreelistRecord(
            prompt_verbatim="test",
            prompt_version="v1",
            response_verbatim="1. mother\n2. father",
            response_object_json={},
            input_tokens=50,
            output_tokens=10,
            latency_ms=200,
            stop_reason="end_turn",
            parsed_items=[f"item{i}" for i in range(15)],
            parsed_raw_order=[f"item{i}" for i in range(15)],
        ),
        pile_sort=PileSortRecord(
            prompt_verbatim="", prompt_version="v1",
            response_verbatim="", response_object_json={},
            input_tokens=0, output_tokens=0, latency_ms=0,
            stop_reason="not_collected", parsed_piles=[], parsed_matrix=[],
        ),
        interview=InterviewRecord(
            prompt_verbatim="", prompt_version="v1",
            response_verbatim="", response_object_json={},
            input_tokens=0, output_tokens=0, latency_ms=0,
            stop_reason="not_collected", parsed_pile_labels=[],
        ),
        sha256_manifest={k: "a" * 64 for k in [
            "freelist_prompt", "freelist_response",
            "pilesort_prompt", "pilesort_response",
            "interview_prompt", "interview_response",
            "request_params", "informant_record_total",
        ]},
        qa_passed=True,
        qa_notes="",
    )

    with tempfile.TemporaryDirectory() as td:
        output = Path(td) / "test.jsonl"

        with patch(
            "scripts.collect.run_informant",
            new_callable=AsyncMock,
            return_value=mock_record,
        ):
            result = asyncio.run(
                collect(
                    model_id="claude-opus-4-6",
                    domain_slug="family",
                    runs=2,
                    output_path=output,
                )
            )

    assert result == 2
