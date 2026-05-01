"""Tests for the run_decline_interview module.

All tests mock adapter.complete — no real API calls.
Covers: prompt building, runner output shape, version_drift_flag logic,
and append_decline_interview persistence.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from cdb_collect.adapters.base import AdapterResult
from cdb_collect.jsonl import append_decline_interview
from cdb_collect.run_decline_interview import (
    _DECLINE_PROMPT_VERSION,
    build_prompt,
    run_decline_interview,
)
from cdb_core.schemas import DeclineInterview

# ── Helpers ───────────────────────────────────────────────────────────────

_NOW = datetime(2026, 4, 23, 12, 0, 0, tzinfo=UTC)


def _make_adapter(
    *,
    model_id: str = "claude-opus-4-6",
    model_version_returned: str = "claude-opus-4-6-20260401",
    response_text: str = "In that exchange I noticed the task asked for sorting...",
    thinking_text: str = "",
    input_tokens: int = 100,
    output_tokens: int = 80,
    latency_ms: int = 900,
    provider: str = "anthropic",
    collection_method: str = "anthropic_api",
) -> MagicMock:
    from datetime import date

    from cdb_core import ModelRef
    model_ref = ModelRef(
        provider=provider,  # type: ignore[arg-type]
        model_id=model_id,
        family="claude",
        origin="us",
        open_weights=False,
        collection_method=collection_method,  # type: ignore[arg-type]
        quantization=None,
        release_date=date(2026, 3, 1),
        version_label="4.6",
    )
    adapter = MagicMock()
    adapter.model = model_ref
    result = AdapterResult(
        text=response_text,
        raw_response={"id": "msg_001"},
        latency_ms=latency_ms,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        provider_request_id="req_001",
        model_version_returned=model_version_returned,
        stop_reason="end_turn",
        thinking_text=thinking_text,
    )
    adapter.complete = AsyncMock(return_value=result)
    return adapter


# ── build_prompt ──────────────────────────────────────────────────────────

def test_build_prompt_substitutes_task_description():
    """task_description is substituted verbatim into the prompt."""
    prompt = build_prompt(
        task_description="Sort the following 25 family terms into piles.",
        response_verbatim="I cannot do this.",
    )
    assert "Sort the following 25 family terms into piles." in prompt


def test_build_prompt_substitutes_response():
    """response_verbatim is substituted into the prompt."""
    prompt = build_prompt(
        task_description="some task",
        response_verbatim="Here is my output.",
    )
    assert "Here is my output." in prompt


def test_build_prompt_empty_response_uses_empty_literal():
    """Empty response_verbatim is substituted as the literal string (empty)."""
    prompt = build_prompt(task_description="some task", response_verbatim="")
    assert "(empty)" in prompt
    assert "{response_verbatim_or_empty}" not in prompt


def test_build_prompt_no_unresolved_placeholders():
    """All template placeholders are resolved."""
    prompt = build_prompt(
        task_description="List every family term.",
        response_verbatim="",
    )
    assert "{task_description}" not in prompt
    assert "{response_verbatim_or_empty}" not in prompt


def test_build_prompt_contains_bound_wording():
    """Prompt contains the SME-bound introductory phrase."""
    prompt = build_prompt(task_description="X", response_verbatim="Y")
    assert "A moment ago I asked you to perform the following task" in prompt
    assert "In your own words, please describe what happened in that exchange" in prompt


# ── run_decline_interview ─────────────────────────────────────────────────

def test_runner_returns_decline_interview():
    """run_decline_interview returns a DeclineInterview with correct fields."""
    adapter = _make_adapter()
    result = asyncio.run(
        run_decline_interview(
            adapter,
            task_description="Sort the following family terms.",
            originating_response_verbatim="",
            originating_informant_id="abc12345",
            originating_step="pile_sort",
            originating_outcome_class="empty_output",
            detection_rule_version="v1",
            detection_timestamp=_NOW,
            originating_model_version_returned="claude-opus-4-6-20260401",
        )
    )
    assert isinstance(result, DeclineInterview)
    assert result.originating_informant_id == "abc12345"
    assert result.originating_failure_id is None
    assert result.prompt_version == _DECLINE_PROMPT_VERSION
    assert result.model_id == "claude-opus-4-6"
    assert result.model_version_returned == "claude-opus-4-6-20260401"
    assert result.provider == "anthropic"
    assert result.originating_step == "pile_sort"
    assert result.originating_outcome_class == "empty_output"
    assert result.detection_rule_version == "v1"
    assert result.input_tokens == 100
    assert result.output_tokens == 80
    assert result.stop_reason == "end_turn"


def test_runner_version_drift_flag_false_when_same():
    """version_drift_flag is False when model_version_returned matches origin."""
    adapter = _make_adapter(model_version_returned="claude-opus-4-6-20260401")
    result = asyncio.run(
        run_decline_interview(
            adapter,
            task_description="sort task",
            originating_response_verbatim="some response",
            originating_informant_id="abc12345",
            originating_step="freelist",
            originating_outcome_class="refusal_string_match",
            detection_rule_version="v1",
            detection_timestamp=_NOW,
            originating_model_version_returned="claude-opus-4-6-20260401",  # same
        )
    )
    assert result.version_drift_flag is False


def test_runner_version_drift_flag_true_when_different():
    """version_drift_flag is True when model_version_returned differs from origin."""
    adapter = _make_adapter(model_version_returned="claude-opus-4-6-20260501")
    result = asyncio.run(
        run_decline_interview(
            adapter,
            task_description="sort task",
            originating_response_verbatim="",
            originating_informant_id="abc12345",
            originating_step="pile_sort",
            originating_outcome_class="empty_output",
            detection_rule_version="v1",
            detection_timestamp=_NOW,
            originating_model_version_returned="claude-opus-4-6-20260401",  # different
        )
    )
    assert result.version_drift_flag is True


def test_runner_version_drift_flag_false_when_no_origin_version():
    """version_drift_flag is False when originating_model_version_returned is empty."""
    adapter = _make_adapter(model_version_returned="claude-opus-4-6-20260501")
    result = asyncio.run(
        run_decline_interview(
            adapter,
            task_description="sort task",
            originating_response_verbatim="",
            originating_informant_id="abc12345",
            originating_step="pile_sort",
            originating_outcome_class="empty_output",
            detection_rule_version="v1",
            detection_timestamp=_NOW,
            originating_model_version_returned="",  # not available
        )
    )
    assert result.version_drift_flag is False


def test_runner_with_failure_id():
    """Runner works with originating_failure_id instead of originating_informant_id."""
    adapter = _make_adapter()
    result = asyncio.run(
        run_decline_interview(
            adapter,
            task_description="List every family term.",
            originating_response_verbatim="",
            originating_failure_id="failure|gpt-4o|family|0|2026-04-23T10:00:00",
            originating_step="pre_session",
            originating_outcome_class="http_error",
            detection_rule_version="v1",
            detection_timestamp=_NOW,
        )
    )
    assert result.originating_failure_id is not None
    assert result.originating_informant_id is None


def test_runner_thinking_verbatim_captured():
    """thinking_verbatim from the follow-up call is captured in the record."""
    adapter = _make_adapter(thinking_text="<thinking>Let me reflect...</thinking>")
    result = asyncio.run(
        run_decline_interview(
            adapter,
            task_description="sort task",
            originating_response_verbatim="response",
            originating_informant_id="abc12345",
            originating_step="pile_sort",
            originating_outcome_class="empty_output",
            detection_rule_version="v1",
            detection_timestamp=_NOW,
        )
    )
    assert result.thinking_verbatim == "<thinking>Let me reflect...</thinking>"


def test_runner_sha256_manifest_is_string():
    """sha256_manifest is a non-empty string."""
    adapter = _make_adapter()
    result = asyncio.run(
        run_decline_interview(
            adapter,
            task_description="sort task",
            originating_response_verbatim="some response",
            originating_informant_id="abc12345",
            originating_step="pile_sort",
            originating_outcome_class="refusal_string_match",
            detection_rule_version="v1",
            detection_timestamp=_NOW,
        )
    )
    assert isinstance(result.sha256_manifest, str)
    assert len(result.sha256_manifest) > 0


def test_runner_decline_interview_id_is_deterministic():
    """Same inputs produce the same decline_interview_id."""
    adapter1 = _make_adapter(response_text="response A")
    adapter2 = _make_adapter(response_text="response A")

    async def _run() -> tuple[DeclineInterview, DeclineInterview]:
        r1 = await run_decline_interview(
            adapter1,
            task_description="task",
            originating_response_verbatim="resp",
            originating_informant_id="abc12345",
            originating_step="pile_sort",
            originating_outcome_class="empty_output",
            detection_rule_version="v1",
            detection_timestamp=_NOW,
        )
        r2 = await run_decline_interview(
            adapter2,
            task_description="task",
            originating_response_verbatim="resp",
            originating_informant_id="abc12345",
            originating_step="pile_sort",
            originating_outcome_class="empty_output",
            detection_rule_version="v1",
            detection_timestamp=_NOW,
        )
        return r1, r2

    r1, r2 = asyncio.run(_run())
    assert r1.decline_interview_id == r2.decline_interview_id


# ── append_decline_interview ──────────────────────────────────────────────

def test_append_decline_interview_writes_jsonl(tmp_path: Path):
    """append_decline_interview writes a parseable JSONL line."""
    import json
    adapter = _make_adapter()
    di = asyncio.run(
        run_decline_interview(
            adapter,
            task_description="sort task",
            originating_response_verbatim="",
            originating_informant_id="abc12345",
            originating_step="pile_sort",
            originating_outcome_class="empty_output",
            detection_rule_version="v1",
            detection_timestamp=_NOW,
        )
    )
    path = tmp_path / "decline_interviews.jsonl"
    append_decline_interview(di, path)
    assert path.exists()
    lines = [line for line in path.read_text().splitlines() if line.strip()]
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["decline_interview_id"] == di.decline_interview_id
    assert data["originating_informant_id"] == "abc12345"
    assert data["prompt_version"] == "decline_v1"


def test_append_decline_interview_appends(tmp_path: Path):
    """append_decline_interview appends (does not overwrite) on second call."""
    adapter1 = _make_adapter(model_id="claude-opus-4-6")
    adapter2 = _make_adapter(model_id="claude-opus-4-6")

    async def _run() -> tuple[DeclineInterview, DeclineInterview]:
        di1 = await run_decline_interview(
            adapter1,
            task_description="task A",
            originating_response_verbatim="",
            originating_informant_id="aaa11111",
            originating_step="freelist",
            originating_outcome_class="empty_output",
            detection_rule_version="v1",
            detection_timestamp=_NOW,
        )
        di2 = await run_decline_interview(
            adapter2,
            task_description="task B",
            originating_response_verbatim="some output",
            originating_informant_id="bbb22222",
            originating_step="interview",
            originating_outcome_class="refusal_string_match",
            detection_rule_version="v1",
            detection_timestamp=_NOW,
        )
        return di1, di2

    di1, di2 = asyncio.run(_run())
    path = tmp_path / "decline_interviews.jsonl"
    append_decline_interview(di1, path)
    append_decline_interview(di2, path)
    lines = [line for line in path.read_text().splitlines() if line.strip()]
    assert len(lines) == 2
