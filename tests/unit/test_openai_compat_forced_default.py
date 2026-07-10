"""Tests for forced-default-sampling support in the OpenAI-compat adapter.

CDA SME 2026-07-10 N1: gpt-5.5 rejects the protocol temperature values and
forces its own default (temperature=1.0). The adapter must omit the
"temperature" key from the request payload and propagate the effective
temperature and a disclosure note into AdapterResult so the runner can
write them onto InformantRecord without any model-name knowledge in the runner.

No real API calls. All tests use mock httpx responses or mock adapters.
"""

from __future__ import annotations

import asyncio
import json
from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from cdb_collect.adapters.base import AdapterResult
from cdb_collect.adapters.openai_compat import (
    _FORCED_DEFAULT_NOTE,
    FORCED_DEFAULT_SAMPLING,
    OpenAICompatAdapter,
)
from cdb_collect.runner import run_informant
from cdb_core import Domain, ModelRef

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"

_EXACT_NOTE = (
    "Provider (OpenAI) forces temperature to default 1.0 for this model, "
    "so the 0.3 pile-sort and interview temperatures could not be applied. "
    "top_p is likewise not accepted. Sampling regime is hotter than the "
    "LSB protocol on pile_sort and interview steps."
)


# ── Helpers ────────────────────────────────────────────────────────────


def _openai_model_ref(model_id: str = "openai/gpt-5.5") -> ModelRef:
    return ModelRef(
        provider="openai",
        model_id=model_id,
        family="gpt-5",
        origin="us",
        open_weights=False,
        collection_method="openai_api",
        quantization=None,
        release_date=date(2026, 7, 1),
        version_label="5.5",
    )


def _domain() -> Domain:
    return Domain(
        slug="family",
        version="v1",
        display_name="Family Terms",
        prompt_seed="type of family relationship or family member",
        truncation_k=5,
    )


def _load_fixture(name: str) -> dict:
    return json.loads((_FIXTURES / name).read_text())


def _mock_httpx_response(data: dict, status_code: int = 200) -> httpx.Response:
    return httpx.Response(
        status_code=status_code,
        json=data,
        request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
    )


# ── Constant sanity check ──────────────────────────────────────────────


def test_forced_default_sampling_contains_gpt55():
    """FORCED_DEFAULT_SAMPLING set must contain gpt-5.5 (post-prefix-strip name)."""
    assert "gpt-5.5" in FORCED_DEFAULT_SAMPLING


def test_forced_default_note_exact_string():
    """_FORCED_DEFAULT_NOTE must match the CDA SME 2026-07-10 N1 verbatim."""
    assert _FORCED_DEFAULT_NOTE == _EXACT_NOTE


# ── Payload tests (adapter-level) ─────────────────────────────────────


def test_gpt55_payload_omits_temperature():
    """gpt-5.5 request payload must NOT include the 'temperature' key.

    OpenAI rejects any temperature value other than the default for this model.
    The adapter must omit the key entirely.
    """
    async def _run():
        ref = _openai_model_ref("openai/gpt-5.5")
        adapter = OpenAICompatAdapter(ref, api_key="sk-test-key")
        captured: list[dict] = []

        fixture = _load_fixture("openai_response.json")

        async def side_effect(*args, **kwargs):
            captured.append(kwargs.get("json", {}))
            return _mock_httpx_response(fixture)

        with patch.object(adapter._client, "post", side_effect=side_effect):
            await adapter.complete("list family members", temperature=0.7)

        return captured

    payloads = asyncio.run(_run())
    assert len(payloads) == 1
    assert "temperature" not in payloads[0], (
        f"gpt-5.5 payload must not include 'temperature'; got keys: {list(payloads[0].keys())}"
    )


def test_gpt54_payload_includes_temperature():
    """gpt-5.4 (not in FORCED_DEFAULT_SAMPLING) payload must include 'temperature'.

    Protocol-conformant models must continue to receive the protocol temperature.
    """
    async def _run():
        ref = _openai_model_ref("openai/gpt-5.4")
        # Reuse the openai fixture; model name in fixture does not matter for
        # payload capture.
        adapter = OpenAICompatAdapter(ref, api_key="sk-test-key")
        captured: list[dict] = []

        fixture = dict(_load_fixture("openai_response.json"))
        fixture["model"] = "gpt-5.4"

        async def side_effect(*args, **kwargs):
            captured.append(kwargs.get("json", {}))
            return _mock_httpx_response(fixture)

        with patch.object(adapter._client, "post", side_effect=side_effect):
            await adapter.complete("list family members", temperature=0.7)

        return captured

    payloads = asyncio.run(_run())
    assert len(payloads) == 1
    assert "temperature" in payloads[0], (
        "gpt-5.4 payload must include 'temperature' (not a forced-default model)"
    )
    assert payloads[0]["temperature"] == 0.7


def test_gpt55_adapter_result_carries_forced_default_fields():
    """AdapterResult for gpt-5.5 must carry effective_temperature=1.0 and the note."""
    async def _run():
        ref = _openai_model_ref("openai/gpt-5.5")
        adapter = OpenAICompatAdapter(ref, api_key="sk-test-key")
        fixture = _load_fixture("openai_response.json")

        with patch.object(
            adapter._client, "post",
            new_callable=AsyncMock,
            return_value=_mock_httpx_response(fixture),
        ):
            return await adapter.complete("list family members", temperature=0.3)

    result = asyncio.run(_run())
    assert result.effective_temperature == 1.0, (
        f"Expected effective_temperature=1.0 for gpt-5.5, got {result.effective_temperature}"
    )
    assert result.forced_default_note == _EXACT_NOTE, (
        f"forced_default_note does not match CDA SME N1 verbatim.\n"
        f"Got:      {result.forced_default_note!r}\n"
        f"Expected: {_EXACT_NOTE!r}"
    )


def test_non_forced_model_adapter_result_no_forced_fields():
    """AdapterResult for gpt-5.4 must carry effective_temperature=None and empty note."""
    async def _run():
        ref = _openai_model_ref("openai/gpt-5.4")
        adapter = OpenAICompatAdapter(ref, api_key="sk-test-key")
        fixture = dict(_load_fixture("openai_response.json"))
        fixture["model"] = "gpt-5.4"

        with patch.object(
            adapter._client, "post",
            new_callable=AsyncMock,
            return_value=_mock_httpx_response(fixture),
        ):
            return await adapter.complete("list family members", temperature=0.3)

    result = asyncio.run(_run())
    assert result.effective_temperature is None
    assert result.forced_default_note == ""


# ── Runner / record-assembly tests ────────────────────────────────────


def _free_list_result_forced(effective_temperature: float = 1.0) -> AdapterResult:
    """Forced-default AdapterResult mimicking what the openai_compat adapter returns."""
    text = (
        "1. Mother\n2. Father\n3. Sister\n4. Brother\n5. Aunt\n"
        "6. Uncle\n7. Grandmother\n8. Grandfather\n9. Cousin\n10. Niece"
    )
    return AdapterResult(
        text=text,
        raw_response={"id": "chatcmpl-gpt55-fl"},
        latency_ms=350,
        input_tokens=87,
        output_tokens=30,
        provider_request_id="chatcmpl-gpt55-fl-123",
        model_version_returned="gpt-5.5",
        stop_reason="stop",
        effective_temperature=effective_temperature,
        forced_default_note=_EXACT_NOTE,
    )


def _free_list_result_normal() -> AdapterResult:
    """Normal AdapterResult for a non-forced model."""
    text = (
        "1. Mother\n2. Father\n3. Sister\n4. Brother\n5. Aunt\n"
        "6. Uncle\n7. Grandmother\n8. Grandfather\n9. Cousin\n10. Niece"
    )
    return AdapterResult(
        text=text,
        raw_response={"id": "chatcmpl-gpt54-fl"},
        latency_ms=300,
        input_tokens=87,
        output_tokens=30,
        provider_request_id="chatcmpl-gpt54-fl-123",
        model_version_returned="gpt-5.4",
        stop_reason="stop",
    )


def _pile_sort_result() -> AdapterResult:
    piles_json = json.dumps({
        "piles": [
            ["mother", "father"],
            ["sister", "brother"],
            ["aunt", "uncle"],
            ["grandmother", "grandfather", "cousin", "niece"],
        ],
    })
    return AdapterResult(
        text=piles_json,
        raw_response={"id": "chatcmpl-ps"},
        latency_ms=400,
        input_tokens=120,
        output_tokens=50,
        provider_request_id="chatcmpl-ps-123",
        model_version_returned="gpt-5.5",
        stop_reason="stop",
    )


def _interview_result() -> AdapterResult:
    text = "1. Parents\n2. Siblings\n3. Aunts and Uncles\n4. Extended family"
    return AdapterResult(
        text=text,
        raw_response={"id": "chatcmpl-iv"},
        latency_ms=200,
        input_tokens=80,
        output_tokens=20,
        provider_request_id="chatcmpl-iv-123",
        model_version_returned="gpt-5.5",
        stop_reason="stop",
    )


def _mock_adapter_forced_default() -> MagicMock:
    """Mock adapter returning forced-default results (gpt-5.5 style)."""
    adapter = MagicMock()
    adapter.model = _openai_model_ref("openai/gpt-5.5")

    async def mock_complete(prompt, *, json_schema=None, temperature=0.7):
        lower = prompt.lower()
        if "label" in lower or "organizing principle" in lower:
            return _interview_result()
        elif "sort" in lower:
            return _pile_sort_result()
        else:
            return _free_list_result_forced()

    adapter.complete = mock_complete
    return adapter


def _mock_adapter_normal() -> MagicMock:
    """Mock adapter returning normal results (no forced default)."""
    adapter = MagicMock()
    adapter.model = _openai_model_ref("openai/gpt-5.4")
    adapter.model = ModelRef(
        provider="openai",
        model_id="openai/gpt-5.4",
        family="gpt-5",
        origin="us",
        open_weights=False,
        collection_method="openai_api",
        quantization=None,
        release_date=date(2026, 7, 1),
        version_label="5.4",
    )

    async def mock_complete(prompt, *, json_schema=None, temperature=0.7):
        lower = prompt.lower()
        if "label" in lower or "organizing principle" in lower:
            return _interview_result()
        elif "sort" in lower:
            return _pile_sort_result()
        else:
            return _free_list_result_normal()

    adapter.complete = mock_complete
    return adapter


def test_forced_default_record_temperature_is_10():
    """InformantRecord.temperature must be 1.0 for a forced-default model.

    The protocol requests 0.7 (freelist) / 0.3 (pile_sort, interview) but the
    provider forces 1.0. The record must reflect the actual effective value.
    """
    adapter = _mock_adapter_forced_default()
    record = asyncio.run(run_informant(adapter, _domain(), 0))

    assert record.temperature == 1.0, (
        f"Expected temperature=1.0 (provider-forced default), got {record.temperature}"
    )


def test_forced_default_record_capacity_note_contains_exact_string():
    """InformantRecord.capacity_note must contain the exact CDA SME N1 string."""
    adapter = _mock_adapter_forced_default()
    record = asyncio.run(run_informant(adapter, _domain(), 0))

    assert _EXACT_NOTE in record.capacity_note, (
        f"capacity_note does not contain the CDA SME N1 required string.\n"
        f"Required: {_EXACT_NOTE!r}\n"
        f"Got:      {record.capacity_note!r}"
    )


def test_non_forced_model_record_unchanged():
    """A non-forced-default model's record must have temperature=0.7 and no forced note."""
    adapter = _mock_adapter_normal()
    record = asyncio.run(run_informant(adapter, _domain(), 0))

    assert record.temperature == 0.7, (
        f"Expected temperature=0.7 for normal model, got {record.temperature}"
    )
    assert _EXACT_NOTE not in record.capacity_note, (
        f"Non-forced model must not carry the forced-default capacity note.\n"
        f"Got: {record.capacity_note!r}"
    )


def test_forced_default_capacity_note_appends_when_context_window_also_exceeded():
    """When both context-window and forced-default apply, both notes appear joined by '; '."""
    from cdb_collect.runner import _assemble_record
    from cdb_core import FreelistRecord, InterviewRecord, PileSortRecord

    adapter = _mock_adapter_forced_default()
    domain = _domain()

    # Build a freelist record with context-window stop reason
    fl_record = FreelistRecord(
        prompt_verbatim="list family",
        prompt_version="v1",
        response_verbatim="1. Mother\n2. Father",
        response_object_json={},
        input_tokens=10,
        output_tokens=5,
        latency_ms=100,
        stop_reason="length",  # triggers context-window-exceeded
        parsed_items=["mother", "father"],
        parsed_raw_order=["mother", "father"],
    )
    fl_result = AdapterResult(
        text="1. Mother\n2. Father",
        raw_response={},
        latency_ms=100,
        input_tokens=10,
        output_tokens=5,
        provider_request_id="req-cwe",
        model_version_returned="gpt-5.5",
        stop_reason="length",
        effective_temperature=1.0,
        forced_default_note=_EXACT_NOTE,
    )
    ps_record = PileSortRecord(
        prompt_verbatim="sort items",
        prompt_version="v1",
        response_verbatim='{"piles": [["mother"], ["father"]]}',
        response_object_json={"piles": [["mother"], ["father"]]},
        input_tokens=20,
        output_tokens=10,
        latency_ms=100,
        stop_reason="stop",
        parsed_piles=[["mother"], ["father"]],
        parsed_matrix=[[1, 0], [0, 1]],
        item_source="own_freelist",
    )
    iv_record = InterviewRecord(
        prompt_verbatim="label piles",
        prompt_version="v1",
        response_verbatim="1. Parents\n2. Uncles",
        response_object_json={},
        input_tokens=15,
        output_tokens=5,
        latency_ms=80,
        stop_reason="stop",
        parsed_pile_labels=["Parents", "Uncles"],
    )

    record = _assemble_record(
        adapter, domain, 0,
        fl_record, fl_result,
        ps_record, iv_record,
        collection_mode="single_pass",
    )

    # Both the context-window note and the forced-default note must be present.
    assert "context window exceeded" in record.capacity_note
    assert _EXACT_NOTE in record.capacity_note
    # They must be joined with "; "
    assert "; " in record.capacity_note
