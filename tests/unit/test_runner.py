"""Tests for the collection runner. Uses mock adapter — no real API calls."""

import asyncio
import json
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

from cdb_collect.adapters.base import AdapterResult
from cdb_collect.runner import run_informant
from cdb_core import Domain, ModelRef

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _model_ref() -> ModelRef:
    return ModelRef(
        provider="anthropic",
        model_id="claude-opus-4-6",
        family="claude",
        origin="us",
        open_weights=False,
        collection_method="anthropic_api",
        quantization=None,
        release_date=date(2026, 3, 1),
        version_label="4.6",
    )


def _domain() -> Domain:
    return Domain(
        slug="family",
        version="v1",
        display_name="Family Terms",
        prompt_seed="type of family relationship or family member",
        truncation_k=25,
    )


def _adapter_result() -> AdapterResult:
    text = (_FIXTURES / "free_list_response.txt").read_text()
    fixture = json.loads((_FIXTURES / "anthropic_response.json").read_text())
    return AdapterResult(
        text=text,
        raw_response=fixture,
        latency_ms=350,
        cost_usd=0.016,
        input_tokens=87,
        output_tokens=195,
        provider_request_id="msg_01XFDUDYJgAACzvnptvVoYEL",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason="end_turn",
    )


def _mock_adapter() -> MagicMock:
    adapter = MagicMock()
    adapter.model = _model_ref()

    async def mock_complete(prompt, *, json_schema=None, temperature=0.7):
        return _adapter_result()

    adapter.complete = mock_complete
    return adapter


def test_run_informant_produces_valid_record():
    async def _run():
        return await run_informant(
            _mock_adapter(), _domain(), run_index=0,
        )

    record = asyncio.run(_run())

    # Identity
    assert record.informant_id
    assert record.domain_slug == "family"
    assert record.run_index == 0

    # Model identity
    assert record.model_id == "claude-opus-4-6"
    assert record.model_version_returned == "claude-opus-4-6-20260401"
    assert record.provider_request_id == "msg_01XFDUDYJgAACzvnptvVoYEL"

    # Freelist is populated
    assert len(record.freelist.parsed_items) == 25
    assert record.freelist.parsed_items[0] == "mother"
    assert record.freelist.stop_reason == "end_turn"

    # Pile sort and interview are placeholders
    assert record.pile_sort.stop_reason == "not_collected"
    assert record.pile_sort.parsed_piles == []
    assert record.interview.stop_reason == "not_collected"
    assert record.interview.parsed_pile_labels == []


def test_run_informant_has_valid_manifest():
    async def _run():
        return await run_informant(
            _mock_adapter(), _domain(), run_index=0,
        )

    record = asyncio.run(_run())

    expected_keys = {
        "freelist_prompt", "freelist_response",
        "pilesort_prompt", "pilesort_response",
        "interview_prompt", "interview_response",
        "request_params", "informant_record_total",
    }
    assert set(record.sha256_manifest.keys()) == expected_keys

    for v in record.sha256_manifest.values():
        assert len(v) == 64
        assert all(c in "0123456789abcdef" for c in v)


def test_run_informant_round_trip():
    async def _run():
        return await run_informant(
            _mock_adapter(), _domain(), run_index=0,
        )

    record = asyncio.run(_run())
    json_str = record.model_dump_json()
    from cdb_core import InformantRecord
    restored = InformantRecord.model_validate_json(json_str)
    assert restored.informant_id == record.informant_id
    assert restored.freelist.parsed_items == record.freelist.parsed_items
