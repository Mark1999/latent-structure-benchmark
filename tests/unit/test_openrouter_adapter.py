"""Tests for the OpenRouter adapter. No real API calls — uses mocks."""

from __future__ import annotations

import asyncio
import json
from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
from cdb_collect.adapters.openrouter import OpenRouterAdapter, _scrub_response
from cdb_core import ModelRef

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _model_ref() -> ModelRef:
    return ModelRef(
        provider="openrouter",
        model_id="meta-llama/llama-3.1-70b-instruct",
        family="llama-3.1",
        origin="us",
        open_weights=True,
        collection_method="openrouter",
        quantization=None,
        release_date=date(2025, 7, 23),
        version_label="3.1-70b-instruct",
    )


def _mock_httpx_response() -> httpx.Response:
    """Build a mock httpx.Response from the fixture."""
    fixture = (_FIXTURES / "openrouter_response.json").read_text()
    return httpx.Response(
        status_code=200,
        json=json.loads(fixture),
        request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
    )


def test_complete_returns_adapter_result():
    async def _run():
        adapter = OpenRouterAdapter(_model_ref(), api_key="sk-or-v1-test")

        with patch.object(
            adapter._client, "post",
            new_callable=AsyncMock, return_value=_mock_httpx_response(),
        ):
            return await adapter.complete("test prompt")

    result = asyncio.run(_run())

    assert result.text.startswith("1. Mother")
    assert result.provider_request_id == "gen-1234567890abcdef"
    assert result.model_version_returned == "meta-llama/llama-3.1-70b-instruct:nitro"
    assert result.stop_reason == "stop"
    assert result.input_tokens == 92
    assert result.output_tokens == 148
    assert result.latency_ms >= 0


def test_api_key_not_in_raw_response():
    async def _run():
        adapter = OpenRouterAdapter(_model_ref(), api_key="sk-or-v1-secret")

        fixture = json.loads((_FIXTURES / "openrouter_response.json").read_text())
        fixture["authorization"] = "Bearer sk-or-v1-secret"
        resp = httpx.Response(
            status_code=200,
            json=fixture,
            request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
        )

        with patch.object(
            adapter._client, "post",
            new_callable=AsyncMock, return_value=resp,
        ):
            return await adapter.complete("test prompt")

    result = asyncio.run(_run())
    raw_str = json.dumps(result.raw_response)
    assert "sk-or-v1-secret" not in raw_str
    assert "authorization" not in result.raw_response


def test_retry_on_rate_limit():
    async def _run():
        adapter = OpenRouterAdapter(_model_ref(), api_key="sk-or-v1-test")

        call_count = 0
        ok_response = _mock_httpx_response()

        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return httpx.Response(
                    status_code=429,
                    text="rate limited",
                    request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
                )
            return ok_response

        with patch.object(
            adapter._client, "post", side_effect=side_effect,
        ), patch(
            "cdb_collect.adapters.openrouter._BASE_DELAY_S", 0.01,
        ):
            result = await adapter.complete("test prompt")

        return result, call_count

    result, call_count = asyncio.run(_run())
    assert call_count == 2
    assert result.text.startswith("1. Mother")


def test_retry_on_server_error():
    async def _run():
        adapter = OpenRouterAdapter(_model_ref(), api_key="sk-or-v1-test")

        call_count = 0
        ok_response = _mock_httpx_response()

        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return httpx.Response(
                    status_code=502,
                    text="bad gateway",
                    request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
                )
            return ok_response

        with patch.object(
            adapter._client, "post", side_effect=side_effect,
        ), patch(
            "cdb_collect.adapters.openrouter._BASE_DELAY_S", 0.01,
        ):
            result = await adapter.complete("test prompt")

        return result, call_count

    result, call_count = asyncio.run(_run())
    assert call_count == 2
    assert result.text.startswith("1. Mother")


def test_scrub_response():
    data = {
        "id": "gen-123",
        "api_key": "secret",
        "nested": {"authorization": "Bearer secret", "data": "ok"},
    }
    scrubbed = _scrub_response(data)
    assert "api_key" not in scrubbed
    assert "authorization" not in scrubbed["nested"]
    assert scrubbed["nested"]["data"] == "ok"
    assert scrubbed["id"] == "gen-123"


# ---------------------------------------------------------------------------
# Task 16.A — cap value and thoughts_token_count tests
# ---------------------------------------------------------------------------

def _make_httpx_response(data: dict, status_code: int = 200) -> httpx.Response:
    return httpx.Response(
        status_code=status_code,
        json=data,
        request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
    )


def test_request_payload_has_max_tokens_16384():
    """_do_call must send max_tokens=16384 in the request payload (Task 16.A)."""
    async def _run():
        adapter = OpenRouterAdapter(_model_ref(), api_key="sk-or-v1-test")
        captured_payloads: list[dict] = []

        fixture = json.loads((_FIXTURES / "openrouter_response.json").read_text())

        async def side_effect(*args, **kwargs):
            captured_payloads.append(kwargs.get("json", {}))
            return _make_httpx_response(fixture)

        with patch.object(adapter._client, "post", side_effect=side_effect):
            await adapter.complete("test prompt")

        return captured_payloads

    payloads = asyncio.run(_run())
    assert len(payloads) == 1
    assert payloads[0].get("max_tokens") == 16384, (
        f"Expected max_tokens=16384, got {payloads[0].get('max_tokens')}"
    )


def test_request_payload_has_include_reasoning_true():
    """_do_call must send include_reasoning=True in the request payload (Task 16.A)."""
    async def _run():
        adapter = OpenRouterAdapter(_model_ref(), api_key="sk-or-v1-test")
        captured_payloads: list[dict] = []

        fixture = json.loads((_FIXTURES / "openrouter_response.json").read_text())

        async def side_effect(*args, **kwargs):
            captured_payloads.append(kwargs.get("json", {}))
            return _make_httpx_response(fixture)

        with patch.object(adapter._client, "post", side_effect=side_effect):
            await adapter.complete("test prompt")

        return captured_payloads

    payloads = asyncio.run(_run())
    assert payloads[0].get("include_reasoning") is True, (
        f"Expected include_reasoning=True, got {payloads[0].get('include_reasoning')}"
    )


def test_thoughts_token_count_captured_from_reasoning_response():
    """When completion_tokens_details.reasoning_tokens is present, capture it."""
    async def _run():
        adapter = OpenRouterAdapter(_model_ref(), api_key="sk-or-v1-test")
        fixture = json.loads(
            (_FIXTURES / "openrouter_response_with_reasoning.json").read_text()
        )

        with patch.object(
            adapter._client, "post",
            new_callable=AsyncMock,
            return_value=_make_httpx_response(fixture),
        ):
            return await adapter.complete("test prompt")

    result = asyncio.run(_run())
    assert result.thoughts_token_count == 1000, (
        f"Expected thoughts_token_count=1000, got {result.thoughts_token_count}"
    )
    assert result.thinking_text != ""


def test_thoughts_token_count_zero_when_completion_details_absent():
    """When usage has no completion_tokens_details, thoughts_token_count defaults to 0."""
    async def _run():
        adapter = OpenRouterAdapter(_model_ref(), api_key="sk-or-v1-test")
        # Use the standard fixture which lacks completion_tokens_details
        fixture = json.loads((_FIXTURES / "openrouter_response.json").read_text())

        with patch.object(
            adapter._client, "post",
            new_callable=AsyncMock,
            return_value=_make_httpx_response(fixture),
        ):
            return await adapter.complete("test prompt")

    result = asyncio.run(_run())
    assert result.thoughts_token_count == 0


def test_thoughts_token_count_zero_when_reasoning_tokens_absent_in_details():
    """When completion_tokens_details exists but lacks reasoning_tokens, default to 0."""
    async def _run():
        adapter = OpenRouterAdapter(_model_ref(), api_key="sk-or-v1-test")
        fixture = json.loads((_FIXTURES / "openrouter_response.json").read_text())
        # Add completion_tokens_details without reasoning_tokens
        fixture["usage"]["completion_tokens_details"] = {
            "accepted_prediction_tokens": 0,
            "rejected_prediction_tokens": 0,
        }

        with patch.object(
            adapter._client, "post",
            new_callable=AsyncMock,
            return_value=_make_httpx_response(fixture),
        ):
            return await adapter.complete("test prompt")

    result = asyncio.run(_run())
    assert result.thoughts_token_count == 0
