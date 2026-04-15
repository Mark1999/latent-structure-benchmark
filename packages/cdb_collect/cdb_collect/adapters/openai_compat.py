"""OpenAI-compatible API adapter for multiple providers. See ARCHITECTURE.md §4.1.2.

Handles any provider that exposes the OpenAI chat completions format:
  - OpenAI   (api.openai.com)
  - xAI/Grok (api.x.ai)
  - DeepSeek (api.deepseek.com)
  - Mistral  (api.mistral.ai)

Thinking trace extraction handles all known patterns:
  - "reasoning_content" field on message (xAI Grok 4, OpenAI o-series)
  - <think>...</think> blocks in content (DeepSeek R1)
  - Inline multi-agent blocks (Grok Harper/Benjamin/Lucas pattern)
  - <thinking>...</thinking> tags
  - Step-by-step reasoning markers
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import time

import httpx
from cdb_core import ModelRef

from cdb_collect.adapters.base import AdapterResult
from cdb_collect.spend import compute_cost

logger = logging.getLogger(__name__)

_DEFAULT_MAX_CONCURRENT = 3
_MAX_RETRIES = 5
_BASE_DELAY_S = 1.0

# HTTP status codes that trigger retry
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}

# Provider configurations: base_url, env_key, model_id prefix to strip
PROVIDER_CONFIGS: dict[str, dict] = {
    "openai_api": {
        "base_url": "https://api.openai.com/v1/chat/completions",
        "env_key": "OPENAI_API_KEY",
        "strip_prefix": "openai/",
    },
    "xai_api": {
        "base_url": "https://api.x.ai/v1/chat/completions",
        "env_key": "XAI_API_KEY",
        "strip_prefix": "x-ai/",
    },
    "deepseek_api": {
        "base_url": "https://api.deepseek.com/v1/chat/completions",
        "env_key": "DEEPSEEK_API_KEY",
        "strip_prefix": "deepseek/",
    },
    "mistral_api": {
        "base_url": "https://api.mistral.ai/v1/chat/completions",
        "env_key": "MISTRAL_API_KEY",
        "strip_prefix": "mistralai/",
    },
}


class OpenAICompatAdapter:
    """Adapter for any OpenAI-compatible chat completions API.

    Implements the ModelAdapter protocol defined in adapters/base.py.
    Configured per-provider via PROVIDER_CONFIGS using the model's
    collection_method field.
    """

    def __init__(
        self,
        model: ModelRef,
        *,
        max_concurrent: int = _DEFAULT_MAX_CONCURRENT,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.model = model
        self._semaphore = asyncio.Semaphore(max_concurrent)

        config = PROVIDER_CONFIGS.get(model.collection_method, {})
        self._api_url = base_url or config.get("base_url", "")
        self._api_key = (
            api_key
            or os.environ.get(config.get("env_key", ""), "")
        )

        # Reasoning models can take a long time; use a generous timeout
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(600.0))

        # Strip provider prefix from model_id to get the API model name
        strip = config.get("strip_prefix", "")
        self._api_model = model.model_id.removeprefix(strip)

        self._provider_name = model.collection_method.removesuffix("_api")

    async def complete(
        self,
        prompt: str,
        *,
        json_schema: dict | None = None,
        temperature: float = 0.7,
    ) -> AdapterResult:
        """Call the chat completions API with retry and concurrency control."""
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
                    "%s API error (attempt %d/%d): %s. Retrying in %.1fs",
                    self._provider_name, attempt + 1, _MAX_RETRIES, e, delay,
                )
                await asyncio.sleep(delay)

        raise RuntimeError(
            f"{self._provider_name} API call failed after {_MAX_RETRIES} retries"
        ) from last_error

    async def _do_call(
        self,
        prompt: str,
        *,
        json_schema: dict | None = None,
        temperature: float = 0.7,
    ) -> AdapterResult:
        start = time.monotonic()

        payload: dict = {
            "model": self._api_model,
            "max_tokens": 16384,
            "temperature": temperature,
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
        }

        resp = await self._client.post(self._api_url, json=payload, headers=headers)

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

        # Extract thinking/reasoning traces — multiple strategies:
        # 1. "reasoning_content" field (xAI Grok 4, OpenAI o-series)
        # 2. <think>...</think> blocks in content (DeepSeek R1)
        # 3. Inline multi-agent patterns, step markers, <thinking> tags
        thinking_text = message.get("reasoning_content") or ""
        if not thinking_text:
            thinking_text = extract_thinking(text)

        usage = data.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

        # Reasoning tokens tracked separately in usage details
        output_details = usage.get("completion_tokens_details") or {}
        reasoning_tokens = output_details.get("reasoning_tokens", 0)

        # Include reasoning tokens in cost calculation (billed as output)
        total_output_for_cost = output_tokens + reasoning_tokens
        cost_usd = compute_cost(input_tokens, total_output_for_cost, self.model.model_id)

        raw_response = _scrub_response(data)

        return AdapterResult(
            text=text,
            raw_response=raw_response,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            provider_request_id=data.get("id", ""),
            model_version_returned=data.get("model", self.model.model_id),
            stop_reason=choice.get("finish_reason") or "unknown",
            thinking_text=thinking_text,
        )


class _RetryableError(Exception):
    """Raised on HTTP status codes that should trigger a retry."""


# ── Thinking trace extraction ─────────────────────────────────────────

# DeepSeek R1 wraps thinking in <think>...</think> at the start of content
_THINK_TAG_RE = re.compile(r"<think>(.*?)</think>", re.DOTALL | re.IGNORECASE)

# Generic <thinking>...</thinking> tags
_THINKING_TAG_RE = re.compile(r"<thinking>(.*?)</thinking>", re.DOTALL | re.IGNORECASE)

# Grok multi-agent blocks: "[AgentName]: ..." or "AgentName — ..."
_AGENT_RE = re.compile(
    r"(?:^|\n)(?:\[)?(\w+)(?:\])?\s*[:\-\u2014]\s*(.+?)(?=\n\[?\w+\]?\s*[:\-\u2014]|\Z)",
    re.DOTALL | re.MULTILINE,
)

# Step-by-step reasoning markers
_STEP_RE = re.compile(
    r"(?:Thinking:|Reasoning:|Step \d+[:.]|Chain of Thought:)"
    r"(.+?)(?=\n\n(?:Step \d+|Final Answer|Conclusion)|\Z)",
    re.DOTALL | re.IGNORECASE,
)


def extract_thinking(text: str) -> str:
    """Extract thinking/reasoning traces from response content.

    Handles all known patterns:
    - <think>...</think> blocks (DeepSeek R1)
    - <thinking>...</thinking> tags
    - Multi-agent blocks (Grok: Harper, Benjamin, Lucas)
    - Step-by-step reasoning markers
    """
    parts: list[str] = []

    # DeepSeek-style <think> blocks (highest priority — most structured)
    for m in _THINK_TAG_RE.finditer(text):
        parts.append(m.group(1).strip())

    # <thinking> tags
    for m in _THINKING_TAG_RE.finditer(text):
        parts.append(m.group(1).strip())

    # If we found tagged thinking, return it — don't also extract inline
    if parts:
        return "\n\n".join(parts)

    # Multi-agent blocks (Grok pattern)
    for m in _AGENT_RE.finditer(text):
        agent = m.group(1).strip()
        content = m.group(2).strip()
        if len(content) > 20 and agent.lower() not in ("final", "answer"):
            parts.append(f"[{agent}] {content}")

    # Step-by-step reasoning
    for m in _STEP_RE.finditer(text):
        content = m.group(1).strip()
        if content:
            parts.append(content)

    return "\n\n".join(parts)


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
