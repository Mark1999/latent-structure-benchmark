"""Tests for the Google Gemini adapter. No real API calls — uses mocks.

Tests confirm:
- _do_call constructs GenerateContentConfig with max_output_tokens=16384
  and thinking_budget=1024 (Task 16.A cap values).
- thoughts_token_count is captured from usage_metadata.thoughts_token_count
  when present (non-zero case) and defaults to 0 when absent.
- Existing behaviour (text extraction, thinking_text, token counts,
  model_version, stop_reason) is preserved.

See docs/status/2026-05-04-task-16-architect-plan.md §2 Task 16.A.
"""

from __future__ import annotations

import asyncio
from datetime import date
from typing import Any
from unittest.mock import MagicMock, patch

from cdb_collect.adapters.google import GeminiAdapter
from cdb_core import ModelRef


def _model_ref() -> ModelRef:
    return ModelRef(
        provider="google",
        model_id="google/gemini-2.5-pro",
        family="gemini",
        origin="us",
        open_weights=False,
        collection_method="google_ai",
        quantization=None,
        release_date=date(2025, 5, 6),
        version_label="2.5-pro",
    )


def _mock_genai_response(
    *,
    text: str = "1. Mother\n2. Father\n3. Sister",
    thinking_text: str = "Let me consider family relationships systematically.",
    input_tokens: int = 90,
    output_tokens: int = 30,
    thoughts_token_count: int | None = 512,
    model_version: str = "gemini-2.5-pro-20250506",
    finish_reason_name: str = "STOP",
    response_id: str = "resp-abc123",
) -> MagicMock:
    """Build a MagicMock that looks like a google-genai GenerateContentResponse."""
    # Build content parts: one thinking part, one text part
    thinking_part = MagicMock()
    thinking_part.thought = True
    thinking_part.text = thinking_text

    text_part = MagicMock()
    text_part.thought = False
    text_part.text = text

    content = MagicMock()
    content.parts = [thinking_part, text_part]

    finish_reason = MagicMock()
    finish_reason.name = finish_reason_name

    candidate = MagicMock()
    candidate.content = content
    candidate.finish_reason = finish_reason

    usage = MagicMock()
    usage.prompt_token_count = input_tokens
    usage.candidates_token_count = output_tokens
    # thoughts_token_count attribute: present when non-None, absent when None
    if thoughts_token_count is not None:
        usage.thoughts_token_count = thoughts_token_count
    else:
        # Simulate SDK versions that don't expose the attribute
        del usage.thoughts_token_count

    response = MagicMock()
    response.candidates = [candidate]
    response.usage_metadata = usage
    response.model_version = model_version
    response.response_id = response_id
    # Make to_json_dict() return a minimal serialisable dict
    response.to_json_dict.return_value = {
        "model_version": model_version,
        "response_id": response_id,
    }

    return response


def _make_adapter() -> tuple[GeminiAdapter, Any]:
    """Return (adapter, mock_client) with google.genai patched out."""
    # Patch genai.Client so __init__ doesn't need a real API key
    mock_client = MagicMock()
    with patch("cdb_collect.adapters.google.GeminiAdapter.__init__") as mock_init:
        mock_init.return_value = None
        adapter = GeminiAdapter.__new__(GeminiAdapter)

    adapter.model = _model_ref()
    adapter._semaphore = asyncio.Semaphore(3)
    adapter._api_key = "fake-key"
    adapter._client = mock_client
    adapter._google_model = "gemini-2.5-pro"
    return adapter, mock_client


# ---------------------------------------------------------------------------
# Cap value tests
# ---------------------------------------------------------------------------

def test_do_call_uses_correct_max_output_tokens():
    """_do_call must construct GenerateContentConfig with max_output_tokens=16384."""
    adapter, mock_client = _make_adapter()
    captured_configs: list[Any] = []

    mock_response = _mock_genai_response()

    def fake_generate_content(**kwargs: Any) -> Any:
        captured_configs.append(kwargs.get("config"))
        return mock_response

    mock_client.models.generate_content.side_effect = fake_generate_content

    async def _run() -> None:
        await adapter._do_call("test prompt", temperature=0.3)

    asyncio.run(_run())

    assert len(captured_configs) == 1
    cfg = captured_configs[0]
    assert cfg.max_output_tokens == 16384, (
        f"Expected max_output_tokens=16384, got {cfg.max_output_tokens}"
    )


def test_do_call_uses_correct_thinking_budget():
    """_do_call must construct ThinkingConfig with thinking_budget=1024."""
    adapter, mock_client = _make_adapter()
    captured_configs: list[Any] = []

    mock_response = _mock_genai_response()

    def fake_generate_content(**kwargs: Any) -> Any:
        captured_configs.append(kwargs.get("config"))
        return mock_response

    mock_client.models.generate_content.side_effect = fake_generate_content

    async def _run() -> None:
        await adapter._do_call("test prompt", temperature=0.3)

    asyncio.run(_run())

    cfg = captured_configs[0]
    assert cfg.thinking_config.thinking_budget == 1024, (
        f"Expected thinking_budget=1024, got {cfg.thinking_config.thinking_budget}"
    )


# ---------------------------------------------------------------------------
# thoughts_token_count capture tests
# ---------------------------------------------------------------------------

def test_thoughts_token_count_captured_when_present():
    """When usage_metadata.thoughts_token_count is non-zero, it is captured."""
    adapter, mock_client = _make_adapter()
    mock_response = _mock_genai_response(thoughts_token_count=512)
    mock_client.models.generate_content.return_value = mock_response

    async def _run() -> None:
        return await adapter._do_call("test prompt")

    result = asyncio.run(_run())
    assert result.thoughts_token_count == 512


def test_thoughts_token_count_zero_when_attribute_absent():
    """When usage_metadata lacks thoughts_token_count (older SDK), default is 0."""
    adapter, mock_client = _make_adapter()
    # thoughts_token_count=None tells helper to omit the attribute
    mock_response = _mock_genai_response(thoughts_token_count=None)
    mock_client.models.generate_content.return_value = mock_response

    async def _run() -> None:
        return await adapter._do_call("test prompt")

    result = asyncio.run(_run())
    assert result.thoughts_token_count == 0


def test_thoughts_token_count_zero_when_usage_metadata_absent():
    """When the entire usage_metadata is None, thoughts_token_count defaults to 0."""
    adapter, mock_client = _make_adapter()
    mock_response = _mock_genai_response()
    mock_response.usage_metadata = None
    mock_client.models.generate_content.return_value = mock_response

    async def _run() -> None:
        return await adapter._do_call("test prompt")

    result = asyncio.run(_run())
    assert result.thoughts_token_count == 0


# ---------------------------------------------------------------------------
# Preserved behaviour tests
# ---------------------------------------------------------------------------

def test_complete_returns_adapter_result():
    """End-to-end complete() call returns an AdapterResult with expected fields."""
    adapter, mock_client = _make_adapter()
    mock_response = _mock_genai_response(
        text="1. Mother\n2. Father\n3. Sister",
        thinking_text="Thinking about family members.",
        input_tokens=90,
        output_tokens=30,
        thoughts_token_count=256,
        model_version="gemini-2.5-pro-20250506",
        finish_reason_name="STOP",
        response_id="resp-xyz789",
    )
    mock_client.models.generate_content.return_value = mock_response

    async def _run() -> None:
        return await adapter.complete("test prompt")

    result = asyncio.run(_run())

    assert result.text.startswith("1. Mother")
    assert result.thinking_text.startswith("Thinking about family members")
    assert result.input_tokens == 90
    assert result.output_tokens == 30
    assert result.thoughts_token_count == 256
    assert result.model_version_returned == "gemini-2.5-pro-20250506"
    assert result.stop_reason == "STOP"
    assert result.provider_request_id == "resp-xyz789"
    assert result.latency_ms >= 0


def test_thinking_text_not_included_in_text():
    """Parts with thought=True go to thinking_text, not text."""
    adapter, mock_client = _make_adapter()
    mock_response = _mock_genai_response(
        text="output only",
        thinking_text="this is the reasoning trace",
    )
    mock_client.models.generate_content.return_value = mock_response

    async def _run() -> None:
        return await adapter._do_call("test prompt")

    result = asyncio.run(_run())
    assert "this is the reasoning trace" not in result.text
    assert "this is the reasoning trace" in result.thinking_text
    assert result.text == "output only"
