"""Tests for the collection runner. Uses mock adapter — no real API calls."""

import asyncio
import hashlib
import json
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

from cdb_collect.adapters.base import AdapterResult
from cdb_collect.runner import run_informant
from cdb_core import Domain, InformantRecord, ModelRef

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
        truncation_k=5,  # Small for test manageability
    )


def _free_list_result() -> AdapterResult:
    text = "1. Mother\n2. Father\n3. Sister\n4. Brother\n5. Aunt"
    return AdapterResult(
        text=text,
        raw_response={"id": "msg_free", "content": [{"text": text}]},
        latency_ms=350,
        cost_usd=0.01,
        input_tokens=87,
        output_tokens=30,
        provider_request_id="msg_free_123",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason="end_turn",
    )


def _pile_sort_result() -> AdapterResult:
    piles_json = json.dumps({
        "piles": [["mother", "father"], ["sister", "brother"], ["aunt"]],
    })
    return AdapterResult(
        text=piles_json,
        raw_response={"id": "msg_sort", "content": [{"text": piles_json}]},
        latency_ms=400,
        cost_usd=0.02,
        input_tokens=120,
        output_tokens=50,
        provider_request_id="msg_sort_123",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason="end_turn",
    )


def _interview_result() -> AdapterResult:
    text = "1. Parents\n2. Siblings\n3. Extended family"
    return AdapterResult(
        text=text,
        raw_response={"id": "msg_int", "content": [{"text": text}]},
        latency_ms=200,
        cost_usd=0.005,
        input_tokens=80,
        output_tokens=20,
        provider_request_id="msg_int_123",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason="end_turn",
    )


def _mock_adapter() -> MagicMock:
    """Mock adapter that dispatches different responses per step."""
    adapter = MagicMock()
    adapter.model = _model_ref()

    call_count = 0

    async def mock_complete(prompt, *, json_schema=None, temperature=0.7):
        nonlocal call_count
        call_count += 1
        # Step 1 (free list) = first call, temp 0.7
        # Step 2 (pile sort) = second call, temp 0.3
        # Step 3 (interview) = third call, temp 0.3
        if call_count == 1:
            return _free_list_result()
        elif call_count == 2:
            return _pile_sort_result()
        else:
            return _interview_result()

    adapter.complete = mock_complete
    return adapter


def test_run_informant_full_protocol():
    async def _run():
        return await run_informant(
            _mock_adapter(), _domain(), run_index=0,
        )

    record = asyncio.run(_run())

    # Identity
    assert record.informant_id
    assert record.domain_slug == "family"
    assert record.run_index == 0
    assert record.model_id == "claude-opus-4-6"

    # Step 1: Freelist populated
    assert len(record.freelist.parsed_items) == 5
    assert record.freelist.parsed_items[0] == "mother"
    assert record.freelist.stop_reason == "end_turn"

    # Step 2: Pile sort populated (NOT placeholder)
    assert record.pile_sort.stop_reason == "end_turn"
    assert len(record.pile_sort.parsed_piles) == 3
    assert record.pile_sort.parsed_piles[0] == ["mother", "father"]
    assert len(record.pile_sort.parsed_matrix) == 5
    # Verify matrix is binary
    for row in record.pile_sort.parsed_matrix:
        for cell in row:
            assert cell in (0, 1)

    # Step 3: Interview populated (NOT placeholder)
    assert record.interview.stop_reason == "end_turn"
    assert len(record.interview.parsed_pile_labels) == 3
    assert record.interview.parsed_pile_labels[0] == "Parents"


def test_run_informant_chains_data():
    """Verify data flows: free list items → pile sort, piles → interview."""
    adapter = _mock_adapter()

    prompts_seen: list[str] = []
    original_complete = adapter.complete

    async def tracking_complete(prompt, *, json_schema=None, temperature=0.7):
        prompts_seen.append(prompt)
        return await original_complete(
            prompt, json_schema=json_schema, temperature=temperature,
        )

    adapter.complete = tracking_complete

    asyncio.run(run_informant(adapter, _domain(), run_index=0))

    assert len(prompts_seen) == 3
    # Pile sort prompt should contain the free list items
    assert "mother" in prompts_seen[1].lower()
    assert "father" in prompts_seen[1].lower()
    # Interview prompt should contain the pile groups
    assert "mother" in prompts_seen[2].lower()


def test_run_informant_manifest_no_empty_hashes():
    """All manifest hashes should be from real content, not empty strings."""
    async def _run():
        return await run_informant(
            _mock_adapter(), _domain(), run_index=0,
        )

    record = asyncio.run(_run())

    empty_hash = hashlib.sha256(b"").hexdigest()
    for key, value in record.sha256_manifest.items():
        assert value != empty_hash, f"Manifest key {key!r} has empty-string hash"


def test_run_informant_round_trip():
    async def _run():
        return await run_informant(
            _mock_adapter(), _domain(), run_index=0,
        )

    record = asyncio.run(_run())
    json_str = record.model_dump_json()
    restored = InformantRecord.model_validate_json(json_str)
    assert restored.informant_id == record.informant_id
    assert restored.freelist.parsed_items == record.freelist.parsed_items
    assert restored.pile_sort.parsed_piles == record.pile_sort.parsed_piles
    assert restored.interview.parsed_pile_labels == record.interview.parsed_pile_labels
