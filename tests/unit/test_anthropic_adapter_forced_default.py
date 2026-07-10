"""Tests for forced-default-sampling support in the Anthropic adapter.

Anthropic has deprecated temperature for claude-fable-5, claude-opus-4-8,
and claude-sonnet-5. Sending the parameter returns HTTP 400
"temperature is deprecated for this model". The adapter must omit it and
propagate effective_temperature=1.0 and a disclosure note via AdapterResult.

CDA SME 2026-07-10 N1/N5 authorises collection under provider-forced default.

No real API calls. All tests use mock Anthropic SDK responses.
"""

from __future__ import annotations

import asyncio
import json
from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from cdb_collect.adapters.anthropic import (
    _FORCED_DEFAULT_NOTE,
    FORCED_DEFAULT_SAMPLING,
    AnthropicAdapter,
)
from cdb_collect.adapters.base import AdapterResult
from cdb_collect.runner import run_informant
from cdb_core import Domain, ModelRef

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"

_EXACT_NOTE = (
    "provider forces temperature=1.0 (temperature deprecated for this model); "
    "sampling hotter than protocol on pile_sort and interview "
    "(CDA SME 2026-07-10, N1/N5)"
)


# ── Helpers ────────────────────────────────────────────────────────────


def _model_ref(model_id: str, version_label: str = "5") -> ModelRef:
    return ModelRef(
        provider="anthropic",
        model_id=model_id,
        family="claude",
        origin="us",
        open_weights=False,
        collection_method="anthropic_api",
        quantization=None,
        release_date=date(2026, 7, 1),
        version_label=version_label,
    )


def _domain() -> Domain:
    return Domain(
        slug="family",
        version="v1",
        display_name="Family Terms",
        prompt_seed="type of family relationship or family member",
        truncation_k=5,
    )


def _mock_anthropic_response(model_id: str = "claude-fable-5") -> MagicMock:
    """Build a mock that looks like an Anthropic Message response."""
    fixture = json.loads((_FIXTURES / "anthropic_response.json").read_text())

    content_block = MagicMock()
    content_block.type = "text"
    content_block.text = fixture["content"][0]["text"]

    usage = MagicMock()
    usage.input_tokens = fixture["usage"]["input_tokens"]
    usage.output_tokens = fixture["usage"]["output_tokens"]

    response = MagicMock()
    response.id = fixture["id"]
    response.model = model_id
    response.content = [content_block]
    response.usage = usage
    response.stop_reason = fixture["stop_reason"]
    response.model_dump.return_value = {**fixture, "model": model_id}

    return response


# ── Constant sanity checks ─────────────────────────────────────────────


def test_forced_default_sampling_contains_claude5_family():
    """FORCED_DEFAULT_SAMPLING must contain all three Claude 5 model IDs."""
    assert "claude-fable-5" in FORCED_DEFAULT_SAMPLING
    assert "claude-opus-4-8" in FORCED_DEFAULT_SAMPLING
    assert "claude-sonnet-5" in FORCED_DEFAULT_SAMPLING


def test_claude_opus_4_6_not_in_forced_default_sampling():
    """claude-opus-4-6 (protocol-conformant) must NOT be in FORCED_DEFAULT_SAMPLING."""
    assert "claude-opus-4-6" not in FORCED_DEFAULT_SAMPLING


def test_forced_default_note_exact_string():
    """_FORCED_DEFAULT_NOTE must match the CDA SME 2026-07-10 N1/N5 verbatim."""
    assert _FORCED_DEFAULT_NOTE == _EXACT_NOTE


# ── Payload tests (adapter-level) ─────────────────────────────────────


def _capture_kwargs_for_model(model_id: str) -> list[dict]:
    """Run adapter.complete and return the kwargs list captured from messages.create."""
    async def _run():
        adapter = AnthropicAdapter(_model_ref(model_id), api_key="sk-ant-test")
        captured: list[dict] = []
        mock_resp = _mock_anthropic_response(model_id)

        async def side_effect(*args, **kwargs):
            captured.append(kwargs)
            return mock_resp

        with patch.object(adapter._client.messages, "create", side_effect=side_effect):
            await adapter.complete("list family members", temperature=0.3)

        return captured

    return asyncio.run(_run())


def test_claude_fable5_payload_omits_temperature():
    """claude-fable-5 request must NOT include 'temperature' in kwargs."""
    captured = _capture_kwargs_for_model("claude-fable-5")
    assert len(captured) == 1
    assert "temperature" not in captured[0], (
        f"claude-fable-5 kwargs must not include 'temperature'; got: {list(captured[0].keys())}"
    )


def test_claude_opus48_payload_omits_temperature():
    """claude-opus-4-8 request must NOT include 'temperature' in kwargs."""
    captured = _capture_kwargs_for_model("claude-opus-4-8")
    assert len(captured) == 1
    assert "temperature" not in captured[0], (
        f"claude-opus-4-8 kwargs must not include 'temperature'; got: {list(captured[0].keys())}"
    )


def test_claude_sonnet5_payload_omits_temperature():
    """claude-sonnet-5 request must NOT include 'temperature' in kwargs."""
    captured = _capture_kwargs_for_model("claude-sonnet-5")
    assert len(captured) == 1
    assert "temperature" not in captured[0], (
        f"claude-sonnet-5 kwargs must not include 'temperature'; got: {list(captured[0].keys())}"
    )


def test_claude_opus46_payload_includes_temperature():
    """claude-opus-4-6 (not forced-default) must still include 'temperature' in kwargs."""
    captured = _capture_kwargs_for_model("claude-opus-4-6")
    assert len(captured) == 1
    assert "temperature" in captured[0], (
        "claude-opus-4-6 kwargs must include 'temperature' (protocol-conformant model)"
    )
    assert captured[0]["temperature"] == 0.3


# ── AdapterResult field tests ──────────────────────────────────────────


def _result_for_model(model_id: str) -> AdapterResult:
    async def _run():
        adapter = AnthropicAdapter(_model_ref(model_id), api_key="sk-ant-test")
        mock_resp = _mock_anthropic_response(model_id)

        with patch.object(
            adapter._client.messages, "create",
            new_callable=AsyncMock, return_value=mock_resp,
        ):
            return await adapter.complete("list family members", temperature=0.3)

    return asyncio.run(_run())


def test_claude_fable5_adapter_result_carries_forced_default_fields():
    """AdapterResult for claude-fable-5 must carry effective_temperature=1.0 and note."""
    result = _result_for_model("claude-fable-5")
    assert result.effective_temperature == 1.0
    assert result.forced_default_note == _EXACT_NOTE


def test_claude_opus48_adapter_result_carries_forced_default_fields():
    """AdapterResult for claude-opus-4-8 must carry effective_temperature=1.0 and note."""
    result = _result_for_model("claude-opus-4-8")
    assert result.effective_temperature == 1.0
    assert result.forced_default_note == _EXACT_NOTE


def test_claude_sonnet5_adapter_result_carries_forced_default_fields():
    """AdapterResult for claude-sonnet-5 must carry effective_temperature=1.0 and note."""
    result = _result_for_model("claude-sonnet-5")
    assert result.effective_temperature == 1.0
    assert result.forced_default_note == _EXACT_NOTE


def test_claude_opus46_adapter_result_no_forced_fields():
    """AdapterResult for claude-opus-4-6 must carry effective_temperature=None and empty note."""
    result = _result_for_model("claude-opus-4-6")
    assert result.effective_temperature is None
    assert result.forced_default_note == ""


# ── Runner / record-assembly tests ────────────────────────────────────


def _free_list_result_forced(model_id: str) -> AdapterResult:
    text = (
        "1. Mother\n2. Father\n3. Sister\n4. Brother\n5. Aunt\n"
        "6. Uncle\n7. Grandmother\n8. Grandfather\n9. Cousin\n10. Niece"
    )
    return AdapterResult(
        text=text,
        raw_response={"id": "msg_fl"},
        latency_ms=350,
        input_tokens=87,
        output_tokens=30,
        provider_request_id="msg_fl_123",
        model_version_returned=model_id,
        stop_reason="end_turn",
        effective_temperature=1.0,
        forced_default_note=_EXACT_NOTE,
    )


def _pile_sort_result(model_id: str) -> AdapterResult:
    import json as _json

    piles_json = _json.dumps({
        "piles": [
            ["mother", "father"],
            ["sister", "brother"],
            ["aunt", "uncle"],
            ["grandmother", "grandfather", "cousin", "niece"],
        ],
    })
    return AdapterResult(
        text=piles_json,
        raw_response={"id": "msg_ps"},
        latency_ms=400,
        input_tokens=120,
        output_tokens=50,
        provider_request_id="msg_ps_123",
        model_version_returned=model_id,
        stop_reason="end_turn",
    )


def _interview_result(model_id: str) -> AdapterResult:
    text = "1. Parents\n2. Siblings\n3. Aunts and Uncles\n4. Extended family"
    return AdapterResult(
        text=text,
        raw_response={"id": "msg_iv"},
        latency_ms=200,
        input_tokens=80,
        output_tokens=20,
        provider_request_id="msg_iv_123",
        model_version_returned=model_id,
        stop_reason="end_turn",
    )


def _mock_adapter_forced(model_id: str) -> MagicMock:
    adapter = MagicMock()
    adapter.model = _model_ref(model_id)

    async def mock_complete(prompt, *, json_schema=None, temperature=0.7):
        lower = prompt.lower()
        if "label" in lower or "organizing principle" in lower:
            return _interview_result(model_id)
        elif "sort" in lower:
            return _pile_sort_result(model_id)
        else:
            return _free_list_result_forced(model_id)

    adapter.complete = mock_complete
    return adapter


def test_claude_fable5_record_temperature_is_10():
    """InformantRecord.temperature must be 1.0 for claude-fable-5."""
    adapter = _mock_adapter_forced("claude-fable-5")
    record = asyncio.run(run_informant(adapter, _domain(), 0))
    assert record.temperature == 1.0, (
        f"Expected temperature=1.0 for claude-fable-5, got {record.temperature}"
    )


def test_claude_opus48_record_temperature_is_10():
    """InformantRecord.temperature must be 1.0 for claude-opus-4-8."""
    adapter = _mock_adapter_forced("claude-opus-4-8")
    record = asyncio.run(run_informant(adapter, _domain(), 0))
    assert record.temperature == 1.0, (
        f"Expected temperature=1.0 for claude-opus-4-8, got {record.temperature}"
    )


def test_claude_sonnet5_record_temperature_is_10():
    """InformantRecord.temperature must be 1.0 for claude-sonnet-5."""
    adapter = _mock_adapter_forced("claude-sonnet-5")
    record = asyncio.run(run_informant(adapter, _domain(), 0))
    assert record.temperature == 1.0, (
        f"Expected temperature=1.0 for claude-sonnet-5, got {record.temperature}"
    )


def test_forced_default_record_capacity_note_contains_exact_string():
    """InformantRecord.capacity_note must contain the exact CDA SME N1/N5 string."""
    adapter = _mock_adapter_forced("claude-fable-5")
    record = asyncio.run(run_informant(adapter, _domain(), 0))
    assert _EXACT_NOTE in record.capacity_note, (
        f"capacity_note does not contain the required CDA SME N1/N5 string.\n"
        f"Required: {_EXACT_NOTE!r}\n"
        f"Got:      {record.capacity_note!r}"
    )
