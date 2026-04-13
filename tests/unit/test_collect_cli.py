"""Tests for collect.py CLI. No real API calls."""

from __future__ import annotations

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, patch

from cdb_core import FreelistRecord, InformantRecord, InterviewRecord, PileSortRecord

# Reuse model registry from collect.py
from scripts.collect import MODEL_REGISTRY, collect_single_pass


def _mock_record(run_index: int = 0) -> InformantRecord:
    return InformantRecord(
        informant_id=f"test_{run_index}",
        domain_slug="family",
        run_index=run_index,
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
        max_tokens=16384,
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
            prompt_verbatim="test", prompt_version="v1",
            response_verbatim="test", response_object_json={},
            input_tokens=50, output_tokens=20, latency_ms=300,
            stop_reason="end_turn",
            parsed_piles=[["item0", "item1"], ["item2"]],
            parsed_matrix=[[1, 1, 0], [1, 1, 0], [0, 0, 1]],
        ),
        interview=InterviewRecord(
            prompt_verbatim="test", prompt_version="v1",
            response_verbatim="test", response_object_json={},
            input_tokens=30, output_tokens=10, latency_ms=150,
            stop_reason="end_turn",
            parsed_pile_labels=["Group A", "Group B"],
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


def test_single_pass_with_mock():
    from cdb_collect.adapters.anthropic import AnthropicAdapter
    adapter = AnthropicAdapter(MODEL_REGISTRY["claude-opus-4-6"], api_key="test")

    with tempfile.TemporaryDirectory() as td:
        output = Path(td) / "test.jsonl"
        with patch(
            "scripts.collect.run_informant",
            new_callable=AsyncMock,
            return_value=_mock_record(),
        ):
            result = asyncio.run(
                collect_single_pass(adapter, "family", 2, output)
            )
    assert result == 2


def test_cli_dry_run(capsys):
    """Test that --dry-run prints plan without API calls."""
    import sys
    with patch.object(sys, "argv", [
        "collect.py", "--domain", "family", "--dry-run",
    ]):
        from scripts.collect import main
        code = main()
    assert code == 0
    captured = capsys.readouterr()
    assert "DRY RUN" in captured.out
    assert "single_pass" in captured.out


def test_cli_dry_run_two_pass(capsys):
    import sys
    with patch.object(sys, "argv", [
        "collect.py", "--domain", "family",
        "--mode", "two_pass", "--dry-run",
    ]):
        from scripts.collect import main
        code = main()
    assert code == 0
    captured = capsys.readouterr()
    assert "two_pass" in captured.out
