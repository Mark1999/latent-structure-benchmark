"""Tests for the HuggingFace adapter. No real API calls — uses mocks."""

from __future__ import annotations

import asyncio
import json
from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
from cdb_collect.adapters.huggingface import HuggingFaceAdapter, _scrub_response
from cdb_core import ModelRef

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _model_ref() -> ModelRef:
    return ModelRef(
        provider="huggingface",
        model_id="Qwen/Qwen2.5-72B-Instruct",
        family="qwen-2.5",
        origin="cn",
        open_weights=True,
        collection_method="huggingface",
        quantization=None,
        release_date=date(2025, 9, 19),
        version_label="2.5-72b-instruct",
    )


def _mock_httpx_response() -> httpx.Response:
    """Build a mock httpx.Response from the fixture."""
    fixture = (_FIXTURES / "huggingface_response.json").read_text()
    return httpx.Response(
        status_code=200,
        json=json.loads(fixture),
        request=httpx.Request("POST", "https://router.huggingface.co/v1/chat/completions"),
    )


def test_complete_returns_adapter_result():
    async def _run():
        adapter = HuggingFaceAdapter(_model_ref(), api_key="hf_test_token")

        with patch.object(
            adapter._client, "post",
            new_callable=AsyncMock, return_value=_mock_httpx_response(),
        ):
            return await adapter.complete("test prompt")

    result = asyncio.run(_run())

    assert result.text.startswith("1. Mother")
    assert result.provider_request_id == "chatcmpl-hf-abc123def456"
    assert result.model_version_returned == "Qwen/Qwen2.5-72B-Instruct"
    assert result.stop_reason == "stop"
    assert result.input_tokens == 85
    assert result.output_tokens == 142
    assert result.latency_ms >= 0
    assert result.cost_usd > 0


def test_api_key_not_in_raw_response():
    async def _run():
        adapter = HuggingFaceAdapter(_model_ref(), api_key="hf_secret_token")

        fixture = json.loads((_FIXTURES / "huggingface_response.json").read_text())
        fixture["authorization"] = "Bearer hf_secret_token"
        resp = httpx.Response(
            status_code=200,
            json=fixture,
            request=httpx.Request("POST", "https://router.huggingface.co/v1/chat/completions"),
        )

        with patch.object(
            adapter._client, "post",
            new_callable=AsyncMock, return_value=resp,
        ):
            return await adapter.complete("test prompt")

    result = asyncio.run(_run())
    raw_str = json.dumps(result.raw_response)
    assert "hf_secret_token" not in raw_str
    assert "authorization" not in result.raw_response


def test_retry_on_rate_limit():
    async def _run():
        adapter = HuggingFaceAdapter(_model_ref(), api_key="hf_test_token")

        call_count = 0
        ok_response = _mock_httpx_response()

        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return httpx.Response(
                    status_code=429,
                    text="rate limited",
                    request=httpx.Request("POST", "https://router.huggingface.co/v1/chat/completions"),
                )
            return ok_response

        with patch.object(
            adapter._client, "post", side_effect=side_effect,
        ), patch(
            "cdb_collect.adapters.huggingface._BASE_DELAY_S", 0.01,
        ):
            result = await adapter.complete("test prompt")

        return result, call_count

    result, call_count = asyncio.run(_run())
    assert call_count == 2
    assert result.text.startswith("1. Mother")


def test_retry_on_server_error():
    async def _run():
        adapter = HuggingFaceAdapter(_model_ref(), api_key="hf_test_token")

        call_count = 0
        ok_response = _mock_httpx_response()

        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return httpx.Response(
                    status_code=503,
                    text="service unavailable",
                    request=httpx.Request("POST", "https://router.huggingface.co/v1/chat/completions"),
                )
            return ok_response

        with patch.object(
            adapter._client, "post", side_effect=side_effect,
        ), patch(
            "cdb_collect.adapters.huggingface._BASE_DELAY_S", 0.01,
        ):
            result = await adapter.complete("test prompt")

        return result, call_count

    result, call_count = asyncio.run(_run())
    assert call_count == 2
    assert result.text.startswith("1. Mother")


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
