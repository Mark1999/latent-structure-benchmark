"""Runner for the decline-interview follow-up API call.

Implements the async function that, given an originating session context
and a model adapter, issues the decline-interview follow-up call, times
it, and returns a fully-assembled DeclineInterview record.

This module is intentionally NOT wired into any existing collection path.
It will be invoked by the Phase 4a.1 remediation runner (task #21).

See docs/DECLINE_INTERVIEW_PROTOCOL.md and the CDA SME verdict of
2026-04-23 for the protocol specification.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from cdb_core.schemas import DeclineInterview

from cdb_collect.adapters.base import ModelAdapter

# ── Prompt loading ─────────────────────────────────────────────────────────
_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
_DECLINE_PROMPT_VERSION: str = "decline_v1"
_DECLINE_PROMPT_PATH: Path = _PROMPTS_DIR / "decline" / "v1" / "prompt.txt"

# Temperature per SME Note 1.1 (matches free-list per ARCHITECTURE.md §4.1.3)
_DECLINE_TEMPERATURE: float = 0.7


def _load_prompt_template() -> str:
    """Load the bound decline-interview prompt template from disk."""
    return _DECLINE_PROMPT_PATH.read_text(encoding="utf-8").rstrip("\n")


def build_prompt(task_description: str, response_verbatim: str) -> str:
    """Substitute template variables into the bound decline-interview prompt.

    Args:
        task_description: The verbatim original task text as sent to the
            model (not a paraphrase — per SME Note 1.1, paraphrase breaks
            reproducibility).
        response_verbatim: The originating session's response_verbatim.
            When empty, the literal string ``(empty)`` is substituted per
            the bound prompt wording.

    Returns:
        The fully-substituted prompt string, ready to send to the adapter.
    """
    template = _load_prompt_template()
    response_field = response_verbatim if response_verbatim else "(empty)"
    return (
        template
        .replace("{task_description}", task_description)
        .replace("{response_verbatim_or_empty}", response_field)
    )


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _compute_decline_manifest(prompt_verbatim: str, response_verbatim: str) -> str:
    """Compute a single SHA256 hash covering the decline-interview prompt and response."""
    combined = f"prompt:{prompt_verbatim}|response:{response_verbatim}"
    return _sha256(combined)


def _build_decline_interview_id(
    originating_id: str,
    prompt_version: str,
    sha256_manifest: str,
) -> str:
    """Derive a deterministic decline_interview_id from its key constituents."""
    key = f"{originating_id}|{prompt_version}|{sha256_manifest}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


async def run_decline_interview(
    adapter: ModelAdapter,
    *,
    task_description: str,
    originating_response_verbatim: str,
    originating_informant_id: str | None = None,
    originating_failure_id: str | None = None,
    originating_step: Literal["freelist", "pile_sort", "interview", "pre_session"],
    originating_outcome_class: Literal[
        "empty_output",
        "refusal_string_match",
        "single_degenerate_pile",
        "parse_failure",
        "http_error",
        "timeout",
        "other",
    ],
    detection_rule_version: str,
    detection_timestamp: datetime,
    originating_model_version_returned: str = "",
) -> DeclineInterview:
    """Issue the decline-interview follow-up call and return a DeclineInterview.

    Exactly one of ``originating_informant_id`` or ``originating_failure_id``
    must be provided — the xor invariant on DeclineInterview.

    Args:
        adapter: The model adapter to call for the follow-up.
        task_description: The verbatim original task text (not a paraphrase).
        originating_response_verbatim: The originating session's
            response_verbatim. Empty string when the session produced no
            output.
        originating_informant_id: informant_id of the InformantRecord being
            followed up. Set to None when the origin is a failures.jsonl entry.
        originating_failure_id: Identifier for the failures.jsonl entry being
            followed up. Set to None when the origin is an InformantRecord.
        originating_step: Which CDA step the decline occurred on.
        originating_outcome_class: The detection trigger class.
        detection_rule_version: The DECLINE_ALLOWLIST_VERSION string in use.
        detection_timestamp: When detection ran (caller supplies; ensures
            consistency across a batch run).
        originating_model_version_returned: The model_version_returned from
            the originating session. Used to compute version_drift_flag.
            Empty string if not available (no drift check possible).

    Returns:
        A fully-assembled DeclineInterview record.
    """
    prompt = build_prompt(task_description, originating_response_verbatim)
    followup_timestamp = datetime.now(UTC)

    result = await adapter.complete(prompt, temperature=_DECLINE_TEMPERATURE)

    # Determine which originating ID to pass as the manifest key
    originating_id = originating_informant_id or originating_failure_id or "unknown"

    sha256_manifest = _compute_decline_manifest(prompt, result.text)
    decline_interview_id = _build_decline_interview_id(
        originating_id, _DECLINE_PROMPT_VERSION, sha256_manifest,
    )

    # Compute version_drift_flag (SME Note F)
    version_drift_flag = bool(
        originating_model_version_returned
        and result.model_version_returned
        and result.model_version_returned != originating_model_version_returned
    )

    # Resolve api_endpoint from adapter model
    from cdb_collect.runner import _resolve_endpoint  # noqa: PLC0415
    api_endpoint = _resolve_endpoint(adapter.model.collection_method)

    return DeclineInterview(
        decline_interview_id=decline_interview_id,
        originating_informant_id=originating_informant_id,
        originating_failure_id=originating_failure_id,
        originating_step=originating_step,
        originating_outcome_class=originating_outcome_class,
        detection_rule_version=detection_rule_version,
        detection_timestamp=detection_timestamp,
        followup_timestamp=followup_timestamp,
        model_id=adapter.model.model_id,
        model_version_returned=result.model_version_returned,
        provider=adapter.model.provider,
        api_endpoint=api_endpoint,
        prompt_version=_DECLINE_PROMPT_VERSION,
        sha256_manifest=sha256_manifest,
        prompt_verbatim=prompt,
        response_verbatim=result.text,
        thinking_verbatim=result.thinking_text,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        latency_ms=result.latency_ms,
        stop_reason=result.stop_reason,
        version_drift_flag=version_drift_flag,
    )
