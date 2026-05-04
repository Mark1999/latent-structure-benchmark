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
    input_tokens: int
    output_tokens: int
    provider_request_id: str
    model_version_returned: str
    stop_reason: str
    # Provider-reported reasoning/thoughts token count. Captured separately
    # from output_tokens because reasoning tokens are billed and consumed
    # against the same max_tokens budget but do not produce visible output.
    # Detecting output_tokens == 0 AND thoughts_token_count > 0 is a
    # sufficient diagnostic signature of cap-exhausted reasoning (reasoning
    # tokens consumed the entire max_tokens budget before any visible output
    # was emitted). Default 0 (not None) to match the output_tokens: int
    # convention and avoid int | None arithmetic in consumers.
    # For providers that do not surface reasoning tokens (Anthropic,
    # HuggingFace at this commit), the value is always 0.
    # See docs/status/2026-05-04-task-16-architect-plan.md §2 Task 16.A
    # and CDA SME verdict docs/status/2026-05-04-task-16-cda-sme-verdict.md
    # (note S3: replaced "model spent everything on thinking" phrasing).
    thoughts_token_count: int = 0
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
