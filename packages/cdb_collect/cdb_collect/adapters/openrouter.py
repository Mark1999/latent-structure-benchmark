"""OpenRouter adapter — frontier + open-weight models. See ARCHITECTURE.md §4.1.2."""

from __future__ import annotations

import asyncio
import logging
import os
import time

import httpx
from cdb_core import ModelRef

from cdb_collect.adapters.base import AdapterResult
from cdb_collect.adaptive_cap import MAX_OUTPUT_TOKENS_CONFIG, compute_effective_max_tokens

logger = logging.getLogger(__name__)

_DEFAULT_MAX_CONCURRENT = 3
_MAX_RETRIES = 5
_BASE_DELAY_S = 1.0

_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# HTTP status codes that trigger retry
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class OpenRouterAdapter:
    """Adapter for the OpenRouter Chat Completions API.

    Implements the ModelAdapter protocol defined in adapters/base.py.
    OpenRouter exposes an OpenAI-compatible endpoint for frontier and
    open-weight models.
    """

    def __init__(
        self,
        model: ModelRef,
        *,
        max_concurrent: int = _DEFAULT_MAX_CONCURRENT,
        api_key: str | None = None,
        context_length: int | None = None,
    ) -> None:
        self.model = model
        # context_length: model's total context window (tokens) from
        # data/models/registry.json. When None, defaults to a value large
        # enough that adaptive_cap always returns MAX_OUTPUT_TOKENS_CONFIG.
        # Callers building adapters for small-context models (e.g. phi-4 at
        # 16K) must pass context_length explicitly so the adaptive cap fires.
        # See packages/cdb_collect/cdb_collect/adaptive_cap.py and
        # docs/status/2026-05-07-phase4b-architect-plan.md §7.1.
        self._context_length: int = context_length if context_length is not None else (
            MAX_OUTPUT_TOKENS_CONFIG * 100  # effectively unconstrained
        )
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        # 600s timeout: reasoning models (DeepSeek, Qwen, etc.) via
        # OpenRouter can take several minutes for complex prompts
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(600.0))

    async def complete(
        self,
        prompt: str,
        *,
        json_schema: dict | None = None,
        temperature: float = 0.7,
    ) -> AdapterResult:
        """Call the OpenRouter Chat Completions API with retry and concurrency control."""
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
            except _RetryableError as e:
                last_error = e
                delay = _BASE_DELAY_S * (2 ** attempt)
                logger.warning(
                    "OpenRouter API error (attempt %d/%d): %s. Retrying in %.1fs",
                    attempt + 1, _MAX_RETRIES, e, delay,
                )
                await asyncio.sleep(delay)

        raise RuntimeError(
            f"OpenRouter API call failed after {_MAX_RETRIES} retries"
        ) from last_error

    async def _do_call(
        self,
        prompt: str,
        *,
        json_schema: dict | None = None,
        temperature: float = 0.7,
    ) -> AdapterResult:
        start = time.monotonic()

        # OpenRouter routing note: We send a single "model" string, which
        # means OpenRouter's MODEL fallback (substituting a different model)
        # never triggers — that requires an explicit "models" array.
        # PROVIDER fallback (same model, different host) is left enabled;
        # same weights, just different serving infra, improves uptime.
        # model_version_returned captures whatever actually responded.
        #
        # max_tokens: computed per-call via compute_effective_max_tokens().
        # For large-context models (≥163K) this equals MAX_OUTPUT_TOKENS_CONFIG
        # (16384) — same behaviour as the Task #16 flat cap. For small-context
        # models (e.g. microsoft/phi-4 at 16K total), the adaptive cap reduces
        # max_tokens to fit within the available output window after accounting
        # for input tokens and a 512-token safety margin.
        #
        # The original 4096 cap was introduced in
        # docs/status/2026-04-22-phase4a-adapter-fix-verdict.md to protect
        # phi-4. Task #16 (commits 7f8f7f7, de3dd7e) raised it to 16384 for
        # large-context models; Phase 4b T2 adds per-model adaptive sizing so
        # phi-4 (which has a 16K total context) can also succeed at that higher
        # output budget. See docs/status/2026-05-07-phase4b-architect-plan.md §7.1
        # and packages/cdb_collect/cdb_collect/adaptive_cap.py.
        #
        # include_reasoning=True surfaces reasoning tokens in the response
        # for thinking-capable models (required to populate
        # thoughts_token_count and thinking_text). Per OpenRouter docs,
        # this is a no-op for models that do not support reasoning.
        # See docs/status/2026-05-04-task-16-architect-plan.md §2 Task 16.A.
        effective_max_tokens = compute_effective_max_tokens(
            prompt_text=prompt,
            context_length=self._context_length,
        )
        payload: dict = {
            "model": self.model.model_id,
            "max_tokens": effective_max_tokens,
            "temperature": temperature,
            "include_reasoning": True,
            "messages": [{"role": "user", "content": prompt}],
        }

        if json_schema is not None:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": "response", "schema": json_schema},
            }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://cogstructurelab.com",
            "X-Title": "LSB Collection",
        }

        resp = await self._client.post(_API_URL, json=payload, headers=headers)

        if resp.status_code in _RETRYABLE_STATUS:
            raise _RetryableError(
                f"HTTP {resp.status_code}: {resp.text[:200]}"
            )
        resp.raise_for_status()

        data = resp.json()
        latency_ms = int((time.monotonic() - start) * 1000)

        choice = data["choices"][0]
        message = choice["message"]
        text = message.get("content") or ""

        # Extract thinking/reasoning traces from OpenRouter responses.
        # Different providers surface these differently:
        # - Grok: "reasoning_content" field on the message
        # - DeepSeek: "reasoning_content" field on the message
        # - Gemini: may appear in "reasoning" or nested content blocks
        thinking_text = message.get("reasoning_content") or message.get("reasoning") or ""

        usage = data.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        # Reasoning token count: OpenRouter surfaces this as
        # usage.completion_tokens_details.reasoning_tokens for thinking-capable
        # models (e.g. DeepSeek, Qwen, glm-5.1). Default to 0 when the path
        # is absent (non-reasoning models or providers that omit the field).
        completion_details = usage.get("completion_tokens_details") or {}
        thoughts_token_count = completion_details.get("reasoning_tokens") or 0

        raw_response = _scrub_response(data)

        return AdapterResult(
            text=text,
            raw_response=raw_response,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            provider_request_id=data.get("id", ""),
            model_version_returned=data.get("model", self.model.model_id),
            stop_reason=choice.get("finish_reason") or "unknown",
            thoughts_token_count=thoughts_token_count,
            thinking_text=thinking_text,
        )


class _RetryableError(Exception):
    """Raised on HTTP status codes that should trigger a retry."""


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
