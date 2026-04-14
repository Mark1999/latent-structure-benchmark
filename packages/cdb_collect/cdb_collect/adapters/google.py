"""Google Gemini API adapter (direct). See ARCHITECTURE.md §4.1.2."""

from __future__ import annotations

import asyncio
import logging
import os
import time

from cdb_core import ModelRef

from cdb_collect.adapters.base import AdapterResult
from cdb_collect.spend import compute_cost

logger = logging.getLogger(__name__)

_DEFAULT_MAX_CONCURRENT = 3
_MAX_RETRIES = 5
_BASE_DELAY_S = 1.0


class GeminiAdapter:
    """Adapter for the Google Gemini API (direct, not via OpenRouter).

    Implements the ModelAdapter protocol defined in adapters/base.py.
    Uses the google-genai SDK for direct access to Gemini models,
    bypassing OpenRouter for lower latency and better thinking support.
    """

    def __init__(
        self,
        model: ModelRef,
        *,
        max_concurrent: int = _DEFAULT_MAX_CONCURRENT,
        api_key: str | None = None,
    ) -> None:
        from google import genai

        self.model = model
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._api_key = (
            api_key
            or os.environ.get("GEMINI_API_KEY", "")
            or os.environ.get("GOOGLE_API_KEY", "")
        )
        self._client = genai.Client(api_key=self._api_key)
        # Map our model_id (e.g. "google/gemini-2.5-pro") to Google's
        # model name (e.g. "gemini-2.5-pro")
        self._google_model = model.model_id.removeprefix("google/")

    async def complete(
        self,
        prompt: str,
        *,
        json_schema: dict | None = None,
        temperature: float = 0.7,
    ) -> AdapterResult:
        """Call the Google Gemini API with retry and concurrency control."""
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
            except Exception as e:
                # Retry on server errors, rate limits, and connection issues
                error_str = str(e).lower()
                is_retryable = any(k in error_str for k in (
                    "429", "500", "502", "503", "504",
                    "rate", "quota", "resource_exhausted",
                    "connection", "timeout",
                ))
                if not is_retryable:
                    raise
                last_error = e
                delay = _BASE_DELAY_S * (2 ** attempt)
                logger.warning(
                    "Gemini API error (attempt %d/%d): %s. Retrying in %.1fs",
                    attempt + 1, _MAX_RETRIES, e, delay,
                )
                await asyncio.sleep(delay)

        raise RuntimeError(
            f"Gemini API call failed after {_MAX_RETRIES} retries"
        ) from last_error

    async def _do_call(
        self,
        prompt: str,
        *,
        json_schema: dict | None = None,
        temperature: float = 0.7,
    ) -> AdapterResult:
        from google.genai import types

        start = time.monotonic()

        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=16384,
            thinking_config=types.ThinkingConfig(
                thinking_budget=8192,
            ),
        )

        if json_schema is not None:
            config.response_mime_type = "application/json"
            config.response_schema = json_schema

        # Use the sync client in a thread to avoid blocking the event loop
        # (google-genai's async support varies by version)
        response = await asyncio.to_thread(
            self._client.models.generate_content,
            model=self._google_model,
            contents=prompt,
            config=config,
        )

        latency_ms = int((time.monotonic() - start) * 1000)

        # Extract text and thinking from response parts
        text = ""
        thinking_text = ""
        if response.candidates:
            content = response.candidates[0].content
            if content and content.parts:
                for part in content.parts:
                    if part.thought:
                        thinking_text += part.text or ""
                    else:
                        text += part.text or ""

        # Token counts from usage metadata
        usage = response.usage_metadata
        input_tokens = usage.prompt_token_count or 0 if usage else 0
        output_tokens = usage.candidates_token_count or 0 if usage else 0
        thinking_tokens = usage.thoughts_token_count or 0 if usage else 0

        cost_usd = compute_cost(
            input_tokens, output_tokens + thinking_tokens, self.model.model_id,
        )

        # Build raw response dict for provenance
        raw_response = _build_raw_response(response)

        # Extract model version from response
        model_version = self._google_model
        if response.model_version:
            model_version = response.model_version

        return AdapterResult(
            text=text,
            raw_response=raw_response,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            provider_request_id=response.response_id or "",
            model_version_returned=model_version,
            stop_reason=response.candidates[0].finish_reason.name
            if response.candidates and response.candidates[0].finish_reason
            else "unknown",
            thinking_text=thinking_text,
        )


def _build_raw_response(response: object) -> dict:
    """Build a serializable dict from the Gemini response object."""
    try:
        # google-genai responses have a to_dict() or model_dump()
        if hasattr(response, "to_json_dict"):
            result_dict: dict = response.to_json_dict()  # type: ignore[union-attr]
            return result_dict
        if hasattr(response, "model_dump"):
            result_dict = response.model_dump()  # type: ignore[union-attr]
            return result_dict
        # Fallback: extract key fields manually
        result: dict = {}
        if hasattr(response, "candidates") and response.candidates:  # type: ignore[union-attr]
            result["candidates"] = str(response.candidates)  # type: ignore[union-attr]
        if hasattr(response, "usage_metadata"):
            result["usage_metadata"] = str(response.usage_metadata)  # type: ignore[union-attr]
        if hasattr(response, "model_version"):
            result["model_version"] = response.model_version  # type: ignore[union-attr]
        return result
    except Exception:
        return {"_serialization_error": "Could not serialize Gemini response"}
