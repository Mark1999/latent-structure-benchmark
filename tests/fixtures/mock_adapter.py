"""MockAdapter — in-memory ModelAdapter for tests.

Satisfies the ModelAdapter protocol without making any real HTTP requests.
Used by TestExecutePath and related test classes in test_run_decline_backfill.py.

Never imports anthropic, openai, google.generativeai, or any LLM client library.
Never makes a real network call.

Interface matches cdb_collect.adapters.base.ModelAdapter (Protocol).
"""

from __future__ import annotations

from datetime import date
from typing import Any

from cdb_collect.adapters.base import AdapterResult
from cdb_core import ModelRef


class MockAdapter:
    """Deterministic mock adapter for unit and integration tests.

    Args:
        model_id: The model_id to use for the ModelRef.
        response_text: Fixed response text returned by all complete() calls.
        cost_per_call: Fixed cost_usd returned per call (default $0.05).
        model_version_returned: The model_version_returned value to include
            in AdapterResult. Defaults to f"{model_id}-v1" if not provided.
        latency_ms: Fixed latency_ms value per call (default 100).
        collection_method: Collection method for ModelRef (default "openrouter").
    """

    def __init__(
        self,
        model_id: str = "test/mock-model",
        response_text: str = "This is a mock response from the decline interview.",
        cost_per_call: float = 0.05,
        model_version_returned: str | None = None,
        latency_ms: int = 100,
        collection_method: str = "openrouter",
    ) -> None:
        self._response_text = response_text
        self._cost_per_call = cost_per_call
        self._model_version_returned = model_version_returned or f"{model_id}-v1"
        self._latency_ms = latency_ms
        self.model = ModelRef(
            provider="openrouter",
            model_id=model_id,
            family="mock",
            origin="us",
            open_weights=False,
            collection_method=collection_method,
            quantization=None,
            release_date=date(2026, 1, 1),
            version_label=model_id.split("/")[-1] if "/" in model_id else model_id,
        )

    async def complete(
        self,
        prompt: str,
        *,
        json_schema: dict[str, Any] | None = None,
        temperature: float = 0.7,
    ) -> AdapterResult:
        """Return a deterministic AdapterResult. No real HTTP calls."""
        return AdapterResult(
            text=self._response_text,
            raw_response={"mock": True, "prompt_len": len(prompt)},
            latency_ms=self._latency_ms,
            cost_usd=self._cost_per_call,
            input_tokens=len(prompt.split()),
            output_tokens=len(self._response_text.split()),
            provider_request_id="mock-req-id",
            model_version_returned=self._model_version_returned,
            stop_reason="end_turn",
            thinking_text="",
        )
