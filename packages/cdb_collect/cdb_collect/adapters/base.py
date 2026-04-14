"""Base adapter interface for all provider adapters. See ARCHITECTURE.md §4.1.2."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from cdb_core import ModelRef


@dataclass(frozen=True)
class AdapterResult:
    """Uniform result from any model adapter.

    Every adapter returns this type. The runner never sees provider-specific types.
    """

    text: str
    raw_response: dict
    latency_ms: int
    cost_usd: float
    input_tokens: int
    output_tokens: int
    provider_request_id: str
    model_version_returned: str
    stop_reason: str
    thinking_text: str = ""


class ModelAdapter(Protocol):
    """Protocol that every provider adapter must satisfy.

    See ARCHITECTURE.md §4.1.2 for the binding specification.
    """

    model: ModelRef

    async def complete(
        self,
        prompt: str,
        *,
        json_schema: dict | None = None,
        temperature: float = 0.7,
    ) -> AdapterResult: ...
