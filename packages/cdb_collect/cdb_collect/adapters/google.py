"""Google Gemini API adapter (direct). See ARCHITECTURE.md §4.1.2."""

from __future__ import annotations

import asyncio
import logging
import os
import time

from cdb_core import ModelRef

from cdb_collect.adapters.base import AdapterResult

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
        # GOOGLE_API_KEY is the canonical env var (aligned with .env.example
        # and discover_models.py). GEMINI_API_KEY kept as fallback for one
        # release cycle — remove once all deployments have renamed.
        self._api_key = (
            api_key
            or os.environ.get("GOOGLE_API_KEY", "")
            or os.environ.get("GEMINI_API_KEY", "")
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

        # Cap values confirmed by Stage 1.6 end-to-end probe (commit 19d67f1,
        # script scripts/probe_gemini_fullcycle_2026_05_04.py): 10/10 valid
        # informants on family + holidays at max_output_tokens=16384,
        # thinking_budget=1024. The prior max_output_tokens=4096 was the root
        # cause of 29 Phase 4a failures (cap-exhausted reasoning before any
        # visible output was emitted). The prior thinking_budget=8192 was not
        # based on probe data; 1024 proved sufficient and reclaims headroom for
        # visible output. Single global cap for all three CDA steps — per-step
        # adaptive sizing rejected as premature optimisation (see plan §2
        # Task 16.A, Q1 and Q6 SME rulings). Supersedes the cap value from
        # docs/status/2026-04-22-phase4a-adapter-fix-verdict.md.
        # See docs/status/2026-05-04-task-16-architect-plan.md §2 Task 16.A.
        _max_tokens = 16384
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=_max_tokens,
            thinking_config=types.ThinkingConfig(
                thinking_budget=1024,
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
        # Reasoning token count: Google exposes thoughts_token_count as a
        # sibling of prompt_token_count and candidates_token_count on
        # usage_metadata. Default to 0 when the attribute is absent (older
        # SDK versions or non-thinking model variants).
        thoughts_token_count = (
            getattr(usage, "thoughts_token_count", None) or 0
            if usage else 0
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
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            provider_request_id=response.response_id or "",
            model_version_returned=model_version,
            stop_reason=response.candidates[0].finish_reason.name
            if response.candidates and response.candidates[0].finish_reason
            else "unknown",
            thoughts_token_count=thoughts_token_count,
            thinking_text=thinking_text,
            max_tokens_used=_max_tokens,
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
