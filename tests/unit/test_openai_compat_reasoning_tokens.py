"""Tests for reasoning token extraction in the OpenAI-compat adapter (T7).

The OpenAI API returns usage.completion_tokens_details.reasoning_tokens for
reasoning-capable models (o-series, gpt-5.5). The adapter must extract this
value into AdapterResult.thoughts_token_count so that qa_check.py Check 5 and
Check 6 can apply the class-conditioned recalibration (CDA SME 2026-07-10 N1,
N2).

No real API calls. All tests use mocked httpx responses or fixture JSON files.
"""

from __future__ import annotations

import asyncio
import json
from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
from cdb_collect.adapters.openai_compat import OpenAICompatAdapter
from cdb_core import ModelRef

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


# ── Helpers ────────────────────────────────────────────────────────────────


def _model_ref(model_id: str = "openai/gpt-5.5") -> ModelRef:
    return ModelRef(
        provider="openai",
        model_id=model_id,
        family="gpt-5",
        origin="us",
        open_weights=False,
        collection_method="openai_api",
        quantization=None,
        release_date=date(2026, 7, 1),
        version_label=model_id.split("/")[-1] if "/" in model_id else model_id,
    )


def _mock_response(data: dict, status_code: int = 200) -> httpx.Response:
    return httpx.Response(
        status_code=status_code,
        json=data,
        request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
    )


def _load_fixture(name: str) -> dict:
    return json.loads((_FIXTURES / name).read_text())


# ── Tests ──────────────────────────────────────────────────────────────────


def test_reasoning_tokens_extracted_from_completion_tokens_details():
    """When completion_tokens_details.reasoning_tokens is present, it is extracted
    into AdapterResult.thoughts_token_count.

    Fixture: openai_response_with_reasoning.json has reasoning_tokens=3000.
    """
    async def _run():
        adapter = OpenAICompatAdapter(_model_ref(), api_key="sk-test-key")
        fixture = _load_fixture("openai_response_with_reasoning.json")
        with patch.object(
            adapter._client, "post",
            new_callable=AsyncMock,
            return_value=_mock_response(fixture),
        ):
            return await adapter.complete("list family members", temperature=0.7)

    result = asyncio.run(_run())
    assert result.thoughts_token_count == 3000, (
        f"Expected thoughts_token_count=3000 from completion_tokens_details.reasoning_tokens, "
        f"got {result.thoughts_token_count}"
    )


def test_reasoning_tokens_absent_yields_zero():
    """When completion_tokens_details is absent, thoughts_token_count defaults to 0.

    Fixture: openai_response.json has no completion_tokens_details.
    """
    async def _run():
        adapter = OpenAICompatAdapter(_model_ref("openai/gpt-5.4"), api_key="sk-test-key")
        fixture = _load_fixture("openai_response.json")
        with patch.object(
            adapter._client, "post",
            new_callable=AsyncMock,
            return_value=_mock_response(fixture),
        ):
            return await adapter.complete("list family members", temperature=0.7)

    result = asyncio.run(_run())
    assert result.thoughts_token_count == 0, (
        f"Expected thoughts_token_count=0 when completion_tokens_details absent, "
        f"got {result.thoughts_token_count}"
    )


def test_reasoning_tokens_zero_in_details_yields_zero():
    """When completion_tokens_details.reasoning_tokens == 0, result is 0."""
    async def _run():
        adapter = OpenAICompatAdapter(_model_ref(), api_key="sk-test-key")
        fixture = dict(_load_fixture("openai_response.json"))
        fixture["usage"]["completion_tokens_details"] = {"reasoning_tokens": 0}
        with patch.object(
            adapter._client, "post",
            new_callable=AsyncMock,
            return_value=_mock_response(fixture),
        ):
            return await adapter.complete("list family members", temperature=0.7)

    result = asyncio.run(_run())
    assert result.thoughts_token_count == 0
