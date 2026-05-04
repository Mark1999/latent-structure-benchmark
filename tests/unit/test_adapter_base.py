"""Tests for adapter base protocol and AdapterResult."""

from cdb_collect.adapters.base import AdapterResult


def test_adapter_result_creation():
    result = AdapterResult(
        text="hello world",
        raw_response={"id": "msg_123", "content": [{"text": "hello world"}]},
        latency_ms=150,
        input_tokens=50,
        output_tokens=10,
        provider_request_id="req_abc123",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason="end_turn",
    )
    assert result.text == "hello world"
    assert result.latency_ms == 150
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
        input_tokens=10,
        output_tokens=5,
        provider_request_id="req_1",
        model_version_returned="v1",
        stop_reason="end_turn",
    )
    import pytest
    with pytest.raises(AttributeError):
        result.text = "modified"  # type: ignore[misc]


def test_adapter_result_thoughts_token_count_default_zero():
    """thoughts_token_count defaults to 0 when not supplied (Task 16.A)."""
    result = AdapterResult(
        text="hello",
        raw_response={},
        latency_ms=100,
        input_tokens=10,
        output_tokens=5,
        provider_request_id="req_1",
        model_version_returned="v1",
        stop_reason="end_turn",
    )
    assert result.thoughts_token_count == 0


def test_adapter_result_thoughts_token_count_explicit():
    """thoughts_token_count can be set to a non-zero value (Task 16.A)."""
    result = AdapterResult(
        text="hello",
        raw_response={},
        latency_ms=100,
        input_tokens=10,
        output_tokens=5,
        provider_request_id="req_1",
        model_version_returned="v1",
        stop_reason="end_turn",
        thoughts_token_count=1024,
    )
    assert result.thoughts_token_count == 1024


def test_adapter_result_cap_exhausted_reasoning_invariant():
    """Diagnostic invariant: output_tokens==0 AND thoughts_token_count>0 fires correctly."""
    # Cap-exhausted reasoning case: no visible output, reasoning consumed the budget
    result = AdapterResult(
        text="",
        raw_response={},
        latency_ms=200,
        input_tokens=500,
        output_tokens=0,
        provider_request_id="req_cap_exhausted",
        model_version_returned="gemini-2.5-pro-20250506",
        stop_reason="MAX_TOKENS",
        thoughts_token_count=16384,
    )
    assert result.output_tokens == 0 and result.thoughts_token_count > 0

    # Non-reasoning provider: 0 thoughts_token_count means invariant does not fire
    result_non_reasoning = AdapterResult(
        text="",
        raw_response={},
        latency_ms=200,
        input_tokens=500,
        output_tokens=0,
        provider_request_id="req_no_reasoning",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason="end_turn",
        thoughts_token_count=0,
    )
    assert not (result_non_reasoning.output_tokens == 0
                and result_non_reasoning.thoughts_token_count > 0)
