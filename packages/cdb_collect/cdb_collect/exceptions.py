"""Custom exception types for the cdb_collect pipeline.

These exceptions carry session-level verbatim data so that callers can
write full failure records to failures.jsonl even when a step raises
mid-session. See ARCHITECTURE.md §4.1 and the verbatim-capture audit
(docs/status/2026-04-23-verbatim-capture-audit.md).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from cdb_collect.adapters.base import AdapterResult


class PartialSessionError(Exception):
    """Raised by run_informant when a CDA protocol step fails mid-session.

    Carries whatever step records completed successfully before the failure
    (in ``partial_session``) plus the verbatim bytes from the step that
    actually raised (the failing step's prompt, response, thinking, and
    stop_reason fields). This allows the caller to write a rich failure
    record to failures.jsonl via append_failure.

    For pile-sort parse-retry exhaustion, ``retry_attempts`` holds one
    dict per retry (including all but the final attempt). The final
    attempt's bytes go into the top-level verbatim fields.

    Attributes:
        cause: The original exception from the failing step.
        failed_step: Which CDA step raised.
        partial_session: Dict keyed by step name ("freelist", "pile_sort",
            "interview") for each step that completed before the failure.
            Values are model_dump() dicts of the corresponding step
            records. Empty dict when no steps completed (step 1 failure).
        prompt_verbatim: Exact prompt text sent on the failing step.
        response_verbatim: Exact response text from the failing step (or
            the final retry for pile-sort parse-retry exhaustion).
        thinking_verbatim: Reasoning/thinking trace if the adapter
            surfaced one on the failing step.
        stop_reason: Provider stop_reason on the failing step (or final
            retry).
        retry_attempts: Ordered list of per-retry dicts for pile-sort
            parse-retry exhaustion. Each dict carries:
            {attempt_index, response_verbatim, thinking_verbatim,
             stop_reason, input_tokens, output_tokens, latency_ms,
             parse_error_message}.
            Empty list for all other failure types (no retry loop).
    """

    def __init__(
        self,
        cause: Exception,
        failed_step: Literal["freelist", "pile_sort", "interview", "pre_session"],
        partial_session: dict,
        prompt_verbatim: str | None = None,
        response_verbatim: str | None = None,
        thinking_verbatim: str | None = None,
        stop_reason: str | None = None,
        retry_attempts: list[dict] | None = None,
    ) -> None:
        super().__init__(str(cause))
        self.cause = cause
        self.failed_step = failed_step
        self.partial_session = partial_session
        self.prompt_verbatim = prompt_verbatim
        self.response_verbatim = response_verbatim
        self.thinking_verbatim = thinking_verbatim
        self.stop_reason = stop_reason
        self.retry_attempts: list[dict] = retry_attempts if retry_attempts is not None else []


class PileSortParseError(ValueError):
    """Raised by run_pile_sort when all parse retries are exhausted.

    Carries the full list of AdapterResult objects from all attempts (in
    order) so that the caller can extract per-attempt verbatim bytes for
    the failures.jsonl entry.

    Attributes:
        attempts: List of AdapterResult objects, one per retry attempt, in
            order from first to last. len(attempts) == max_retries when all
            retries were exhausted.
        per_attempt_errors: List of the ValueError raised on each attempt
            (same length and order as attempts).
    """

    def __init__(
        self,
        message: str,
        attempts: list[AdapterResult],
        per_attempt_errors: list[Exception],
        prompt_verbatim: str = "",
    ) -> None:
        super().__init__(message)
        self.attempts = attempts
        self.per_attempt_errors = per_attempt_errors
        self.prompt_verbatim = prompt_verbatim
