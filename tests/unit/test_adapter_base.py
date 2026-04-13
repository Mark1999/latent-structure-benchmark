"""Tests for adapter base protocol and AdapterResult."""

from cdb_collect.adapters.base import AdapterResult


def test_adapter_result_creation():
    result = AdapterResult(
        text="hello world",
        raw_response={"id": "msg_123", "content": [{"text": "hello world"}]},
        latency_ms=150,
        cost_usd=0.001,
        input_tokens=50,
        output_tokens=10,
        provider_request_id="req_abc123",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason="end_turn",
    )
    assert result.text == "hello world"
    assert result.latency_ms == 150
    assert result.cost_usd == 0.001
    assert result.input_tokens == 50
    assert result.output_tokens == 10
    assert result.provider_request_id == "req_abc123"
    assert result.model_version_returned == "claude-opus-4-6-20260401"
    assert result.stop_reason == "end_turn"


def test_adapter_result_frozen():
    result = AdapterResult(
        text="test",
        raw_response={},
        latency_ms=100,
        cost_usd=0.0,
        input_tokens=10,
        output_tokens=5,
        provider_request_id="req_1",
        model_version_returned="v1",
        stop_reason="end_turn",
    )
    import pytest
    with pytest.raises(AttributeError):
        result.text = "modified"  # type: ignore[misc]
