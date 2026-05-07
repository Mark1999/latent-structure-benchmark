"""Anthropic API adapter. See ARCHITECTURE.md §4.1.2."""

from __future__ import annotations

import asyncio
import logging
import os
import time

import anthropic
from cdb_core import ModelRef

from cdb_collect.adapters.base import AdapterResult

logger = logging.getLogger(__name__)

# Default concurrency limit per ARCHITECTURE.md §4.1.2
_DEFAULT_MAX_CONCURRENT = 3

# Retry policy: exponential backoff on 429/5xx, max 5 retries
_MAX_RETRIES = 5
_BASE_DELAY_S = 1.0


class AnthropicAdapter:
    """Adapter for the Anthropic Messages API.

    Implements the ModelAdapter protocol defined in adapters/base.py.
    """

    def __init__(
        self,
        model: ModelRef,
        *,
        max_concurrent: int = _DEFAULT_MAX_CONCURRENT,
        api_key: str | None = None,
    ) -> None:
        self.model = model
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self._client = anthropic.AsyncAnthropic(api_key=self._api_key)

    async def complete(
        self,
        prompt: str,
        *,
        json_schema: dict | None = None,
        temperature: float = 0.7,
    ) -> AdapterResult:
        """Call the Anthropic Messages API with retry and concurrency control."""
        async with self._semaphore:
            return await self._complete_with_retry(
                prompt, json_schema=json_schema, temperature=temperature,
            )

    async def _complete_with_retry(
        self,
        prompt: str,
        *,
        json_schema: dict | None = None,
        temperature: float = 0.7,
    ) -> AdapterResult:
        last_error: Exception | None = None

        for attempt in range(_MAX_RETRIES):
            try:
                return await self._do_call(
                    prompt, json_schema=json_schema, temperature=temperature,
                )
            except (
                anthropic.RateLimitError,
                anthropic.InternalServerError,
                anthropic.APIConnectionError,
            ) as e:
                last_error = e
                delay = _BASE_DELAY_S * (2 ** attempt)
                logger.warning(
                    "Anthropic API error (attempt %d/%d): %s. Retrying in %.1fs",
                    attempt + 1, _MAX_RETRIES, e, delay,
                )
                await asyncio.sleep(delay)

        raise RuntimeError(
            f"Anthropic API call failed after {_MAX_RETRIES} retries"
        ) from last_error

    async def _do_call(
        self,
        prompt: str,
        *,
        json_schema: dict | None = None,
        temperature: float = 0.7,
    ) -> AdapterResult:
        start = time.monotonic()

        _max_tokens = 4096  # see docs/status/2026-04-22-phase4a-adapter-fix-verdict.md
        kwargs: dict = {
            "model": self.model.model_id,
            "max_tokens": _max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        response = await self._client.messages.create(**kwargs)

        latency_ms = int((time.monotonic() - start) * 1000)

        text = ""
        thinking_text = ""
        for block in response.content:
            if block.type == "text":
                text += block.text
            elif block.type == "thinking":
                thinking_text += block.thinking

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        # Build the raw response dict, scrubbing the API key
        raw_response = _scrub_response(response.model_dump())

        return AdapterResult(
            text=text,
            raw_response=raw_response,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            provider_request_id=response.id,
            model_version_returned=response.model,
            stop_reason=response.stop_reason or "unknown",
            thinking_text=thinking_text,
            max_tokens_used=_max_tokens,
        )


def _scrub_response(data: dict) -> dict:
    """Remove any API key material from the response dict."""
    scrub_keys = {"api_key", "x-api-key", "authorization"}
    result = {}
    for k, v in data.items():
        if k.lower() in scrub_keys:
            continue
        if isinstance(v, dict):
            result[k] = _scrub_response(v)
        else:
            result[k] = v
    return result
