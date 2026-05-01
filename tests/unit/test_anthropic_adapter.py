"""Tests for the Anthropic adapter. No real API calls — uses mocks."""

from __future__ import annotations

import asyncio
import json
from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from cdb_collect.adapters.anthropic import AnthropicAdapter, _scrub_response
from cdb_core import ModelRef

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


def _mock_response() -> MagicMock:
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
    response.model = fixture["model"]
    response.content = [content_block]
    response.usage = usage
    response.stop_reason = fixture["stop_reason"]
    response.model_dump.return_value = fixture

    return response


def test_complete_returns_adapter_result():
    async def _run():
        adapter = AnthropicAdapter(_model_ref(), api_key="test-key")
        mock_resp = _mock_response()

        with patch.object(
            adapter._client.messages, "create",
            new_callable=AsyncMock, return_value=mock_resp,
        ):
            return await adapter.complete("test prompt")

    result = asyncio.run(_run())

    assert result.text.startswith("1. Mother")
    assert result.provider_request_id == "msg_01XFDUDYJgAACzvnptvVoYEL"
    assert result.model_version_returned == "claude-opus-4-6-20260401"
    assert result.stop_reason == "end_turn"
    assert result.input_tokens == 87
    assert result.output_tokens == 195
    assert result.latency_ms >= 0


def test_api_key_not_in_raw_response():
    async def _run():
        adapter = AnthropicAdapter(_model_ref(), api_key="sk-ant-secret-key")
        mock_resp = _mock_response()
        mock_resp.model_dump.return_value = {
            **json.loads(
                (_FIXTURES / "anthropic_response.json").read_text()
            ),
            "api_key": "sk-ant-secret-key",
        }

        with patch.object(
            adapter._client.messages, "create",
            new_callable=AsyncMock, return_value=mock_resp,
        ):
            return await adapter.complete("test prompt")

    result = asyncio.run(_run())
    assert "sk-ant-secret-key" not in json.dumps(result.raw_response)
    assert "api_key" not in result.raw_response


def test_retry_on_rate_limit():
    import anthropic as anthropic_mod

    async def _run():
        adapter = AnthropicAdapter(_model_ref(), api_key="test-key")
        mock_resp = _mock_response()

        call_count = 0
        original_mock = AsyncMock(return_value=mock_resp)

        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise anthropic_mod.RateLimitError(
                    message="rate limited",
                    response=MagicMock(status_code=429, headers={}),
                    body=None,
                )
            return await original_mock(*args, **kwargs)

        with patch.object(
            adapter._client.messages, "create", side_effect=side_effect,
        ), patch(
            "cdb_collect.adapters.anthropic._BASE_DELAY_S", 0.01,
        ):
            result = await adapter.complete("test prompt")

        return result, call_count

    result, call_count = asyncio.run(_run())
    assert call_count == 2
    assert result.text.startswith("1. Mother")


def test_scrub_response():
    data = {
        "id": "msg_123",
        "api_key": "secret",
        "nested": {"authorization": "Bearer secret", "data": "ok"},
    }
    scrubbed = _scrub_response(data)
    assert "api_key" not in scrubbed
    assert "authorization" not in scrubbed["nested"]
    assert scrubbed["nested"]["data"] == "ok"
    assert scrubbed["id"] == "msg_123"
