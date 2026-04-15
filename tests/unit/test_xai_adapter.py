"""Tests for the xAI Grok adapter. No real API calls — uses mocks."""

from __future__ import annotations

import asyncio
import json
from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
from cdb_collect.adapters.xai import XAIAdapter, _extract_inline_thinking, _scrub_response
from cdb_core import ModelRef

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _model_ref() -> ModelRef:
    return ModelRef(
        provider="xai",
        model_id="x-ai/grok-3",
        family="grok",
        origin="us",
        open_weights=False,
        collection_method="xai_api",
        quantization=None,
        release_date=date(2025, 2, 17),
        version_label="3",
    )


def _fixture_response() -> dict:
    return json.loads((_FIXTURES / "xai_response.json").read_text())


def _mock_httpx_response(data: dict, status_code: int = 200) -> httpx.Response:
    return httpx.Response(
        status_code=status_code,
        json=data,
        request=httpx.Request("POST", "https://api.x.ai/v1/chat/completions"),
    )


def test_complete_returns_adapter_result():
    async def _run():
        adapter = XAIAdapter(_model_ref(), api_key="xai-test-key")
        fixture = _fixture_response()

        with patch.object(
            adapter._client, "post",
            new_callable=AsyncMock,
            return_value=_mock_httpx_response(fixture),
        ):
            return await adapter.complete("test prompt")

    result = asyncio.run(_run())

    assert result.text.startswith("1. Mother")
    assert result.provider_request_id == "chatcmpl-abc123def456"
    assert result.model_version_returned == "grok-3"
    assert result.stop_reason == "stop"
    assert result.input_tokens == 87
    assert result.output_tokens == 152
    assert result.latency_ms >= 0
    assert result.cost_usd > 0


def test_thinking_text_captured():
    async def _run():
        adapter = XAIAdapter(_model_ref(), api_key="xai-test-key")
        fixture = _fixture_response()

        with patch.object(
            adapter._client, "post",
            new_callable=AsyncMock,
            return_value=_mock_httpx_response(fixture),
        ):
            return await adapter.complete("test prompt")

    result = asyncio.run(_run())

    assert "list types of family members" in result.thinking_text
    assert "organize this systematically" in result.thinking_text
    assert len(result.thinking_text) > 0


def test_no_thinking_when_absent():
    async def _run():
        adapter = XAIAdapter(_model_ref(), api_key="xai-test-key")
        fixture = _fixture_response()
        # Remove reasoning_content to simulate a non-reasoning model
        fixture["choices"][0]["message"].pop("reasoning_content")
        fixture["usage"]["completion_tokens_details"]["reasoning_tokens"] = 0

        with patch.object(
            adapter._client, "post",
            new_callable=AsyncMock,
            return_value=_mock_httpx_response(fixture),
        ):
            return await adapter.complete("test prompt")

    result = asyncio.run(_run())

    assert result.thinking_text == ""
    assert result.text.startswith("1. Mother")


def test_api_key_not_in_raw_response():
    async def _run():
        adapter = XAIAdapter(_model_ref(), api_key="xai-secret-key-123")
        fixture = _fixture_response()
        fixture["api_key"] = "xai-secret-key-123"

        with patch.object(
            adapter._client, "post",
            new_callable=AsyncMock,
            return_value=_mock_httpx_response(fixture),
        ):
            return await adapter.complete("test prompt")

    result = asyncio.run(_run())
    assert "xai-secret-key-123" not in json.dumps(result.raw_response)
    assert "api_key" not in result.raw_response


def test_retry_on_rate_limit():
    async def _run():
        adapter = XAIAdapter(_model_ref(), api_key="xai-test-key")
        fixture = _fixture_response()

        call_count = 0

        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return _mock_httpx_response(
                    {"error": "rate limited"}, status_code=429,
                )
            return _mock_httpx_response(fixture)

        with patch.object(
            adapter._client, "post", side_effect=side_effect,
        ), patch(
            "cdb_collect.adapters.openai_compat._BASE_DELAY_S", 0.01,
        ):
            result = await adapter.complete("test prompt")

        return result, call_count

    result, call_count = asyncio.run(_run())
    assert call_count == 2
    assert result.text.startswith("1. Mother")


def test_model_id_prefix_stripped():
    adapter = XAIAdapter(_model_ref(), api_key="xai-test-key")
    assert adapter._api_model == "grok-3"


def test_inline_thinking_multi_agent():
    text = (
        "[Harper]: The user is asking about family members. I should consider "
        "both immediate and extended family relationships.\n"
        "[Benjamin]: I agree with Harper. Let me also think about in-laws "
        "and step-family members which are often overlooked.\n"
        "[Lucas]: Good points. We should also consider cultural variations "
        "in family structure and terminology.\n"
        "Final Answer: Here are 20 family member types..."
    )
    result = _extract_inline_thinking(text)
    assert "Harper" in result
    assert "Benjamin" in result
    assert "Lucas" in result


def test_inline_thinking_step_pattern():
    text = (
        "Thinking: I need to list family member types systematically.\n\n"
        "Step 1: Start with immediate family\n\n"
        "Final Answer: 1. Mother\n2. Father"
    )
    result = _extract_inline_thinking(text)
    assert "systematically" in result
    assert "immediate family" in result


def test_inline_thinking_tags():
    text = (
        "<thinking>Let me consider all categories of family members.</thinking>\n"
        "Here are the family members: 1. Mother..."
    )
    result = _extract_inline_thinking(text)
    assert "categories of family members" in result


def test_inline_thinking_empty_when_no_patterns():
    text = "1. Mother\n2. Father\n3. Sister\n4. Brother"
    result = _extract_inline_thinking(text)
    assert result == ""


def test_inline_fallback_used_when_no_reasoning_content():
    """When reasoning_content is absent, inline thinking is extracted."""
    async def _run():
        adapter = XAIAdapter(_model_ref(), api_key="xai-test-key")
        fixture = _fixture_response()
        # Remove API-level reasoning, add inline thinking to content
        fixture["choices"][0]["message"].pop("reasoning_content")
        fixture["choices"][0]["message"]["content"] = (
            "[Harper]: Family relationships include blood relatives and "
            "in-laws. Let me think about this systematically.\n"
            "[Benjamin]: Agreed. We should cover immediate family, extended "
            "family, and family by marriage.\n"
            "1. Mother\n2. Father\n3. Sister"
        )

        with patch.object(
            adapter._client, "post",
            new_callable=AsyncMock,
            return_value=_mock_httpx_response(fixture),
        ):
            return await adapter.complete("test prompt")

    result = asyncio.run(_run())
    assert "Harper" in result.thinking_text
    assert "Benjamin" in result.thinking_text


def test_scrub_response():
    data = {
        "id": "chatcmpl-123",
        "api_key": "secret",
        "nested": {"authorization": "Bearer secret", "data": "ok"},
    }
    scrubbed = _scrub_response(data)
    assert "api_key" not in scrubbed
    assert "authorization" not in scrubbed["nested"]
    assert scrubbed["nested"]["data"] == "ok"
    assert scrubbed["id"] == "chatcmpl-123"
