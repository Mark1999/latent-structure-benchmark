"""Tests for the DeclineInterview pydantic schema.

Covers: field construction, xor validator, default field values, and
round-trip serialisation. No real API calls.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from cdb_core.schemas import DeclineInterview
from pydantic import ValidationError

# ── Helpers ───────────────────────────────────────────────────────────────

_NOW = datetime(2026, 4, 23, 12, 0, 0, tzinfo=UTC)


def _make_decline_interview(
    *,
    originating_informant_id: str | None = "abc12345",
    originating_failure_id: str | None = None,
    originating_step: str = "pile_sort",
    originating_outcome_class: str = "empty_output",
    version_drift_flag: bool = False,
    thinking_verbatim: str = "",
    qa_notes: str = "",
) -> DeclineInterview:
    return DeclineInterview(
        decline_interview_id="di_0001",
        originating_informant_id=originating_informant_id,
        originating_failure_id=originating_failure_id,
        originating_step=originating_step,  # type: ignore[arg-type]
        originating_outcome_class=originating_outcome_class,  # type: ignore[arg-type]
        detection_rule_version="v1",
        detection_timestamp=_NOW,
        followup_timestamp=_NOW,
        model_id="claude-opus-4-6",
        model_version_returned="claude-opus-4-6-20260401",
        provider="anthropic",
        api_endpoint="https://api.anthropic.com/v1/messages",
        prompt_version="decline_v1",
        sha256_manifest="abc" * 20,
        prompt_verbatim="A moment ago I asked you...",
        response_verbatim="I sorted the items...",
        thinking_verbatim=thinking_verbatim,
        input_tokens=100,
        output_tokens=50,
        latency_ms=1200,
        stop_reason="end_turn",
        cost_usd=0.01,
        qa_notes=qa_notes,
        version_drift_flag=version_drift_flag,
    )


# ── Construction ──────────────────────────────────────────────────────────

def test_basic_construction_with_informant_id():
    """DeclineInterview constructs successfully with originating_informant_id set."""
    di = _make_decline_interview(originating_informant_id="abc12345")
    assert di.decline_interview_id == "di_0001"
    assert di.originating_informant_id == "abc12345"
    assert di.originating_failure_id is None
    assert di.prompt_version == "decline_v1"
    assert di.detection_rule_version == "v1"


def test_basic_construction_with_failure_id():
    """DeclineInterview constructs successfully with originating_failure_id set."""
    di = _make_decline_interview(
        originating_informant_id=None,
        originating_failure_id="failure|gpt-4o|family|0|2026-04-23T10:00:00",
    )
    assert di.originating_failure_id is not None
    assert di.originating_informant_id is None


# ── XOR validator ─────────────────────────────────────────────────────────

def test_xor_both_set_raises():
    """Both originating IDs set → ValueError."""
    with pytest.raises(ValueError, match="exactly one"):
        _make_decline_interview(
            originating_informant_id="abc12345",
            originating_failure_id="some_failure_id",
        )


def test_xor_neither_set_raises():
    """Neither originating ID set → ValueError."""
    with pytest.raises(ValueError, match="exactly one"):
        _make_decline_interview(
            originating_informant_id=None,
            originating_failure_id=None,
        )


# ── Default field values ───────────────────────────────────────────────────

def test_thinking_verbatim_defaults_to_empty():
    di = _make_decline_interview()
    assert di.thinking_verbatim == ""


def test_qa_notes_defaults_to_empty():
    di = _make_decline_interview()
    assert di.qa_notes == ""


def test_version_drift_flag_defaults_to_false():
    di = _make_decline_interview()
    assert di.version_drift_flag is False


def test_version_drift_flag_can_be_true():
    di = _make_decline_interview(version_drift_flag=True)
    assert di.version_drift_flag is True


# ── originating_step values ───────────────────────────────────────────────

@pytest.mark.parametrize("step", ["freelist", "pile_sort", "interview", "pre_session"])
def test_originating_step_valid_values(step: str):
    """All four originating_step values are accepted."""
    di = _make_decline_interview(originating_step=step)
    assert di.originating_step == step


def test_originating_step_invalid_raises():
    """Unknown originating_step value raises ValidationError."""
    with pytest.raises(ValidationError):
        _make_decline_interview(originating_step="unknown_step")


# ── originating_outcome_class values ─────────────────────────────────────

@pytest.mark.parametrize("oc", [
    "empty_output",
    "refusal_string_match",
    "single_degenerate_pile",
    "parse_failure",
    "http_error",
    "timeout",
    "other",
])
def test_originating_outcome_class_valid_values(oc: str):
    """All seven originating_outcome_class values are accepted."""
    di = _make_decline_interview(originating_outcome_class=oc)
    assert di.originating_outcome_class == oc


def test_originating_outcome_class_invalid_raises():
    """Unknown originating_outcome_class raises ValidationError."""
    with pytest.raises(ValidationError):
        _make_decline_interview(originating_outcome_class="bad_class")


# ── Round-trip serialisation ──────────────────────────────────────────────

def test_model_dump_json_round_trip():
    """model_dump_json / model_validate_json round-trip preserves all fields."""
    di = _make_decline_interview(
        version_drift_flag=True,
        thinking_verbatim="<thinking>some trace</thinking>",
        qa_notes="manual check passed",
    )
    json_str = di.model_dump_json()
    di2 = DeclineInterview.model_validate_json(json_str)
    assert di2.decline_interview_id == di.decline_interview_id
    assert di2.version_drift_flag is True
    assert di2.thinking_verbatim == "<thinking>some trace</thinking>"
    assert di2.qa_notes == "manual check passed"
    assert di2.originating_informant_id == di.originating_informant_id
    assert di2.originating_failure_id is None


def test_model_dump_contains_required_fields():
    """model_dump() includes all schema fields."""
    di = _make_decline_interview()
    d = di.model_dump()
    required_fields = {
        "decline_interview_id",
        "originating_step",
        "originating_outcome_class",
        "detection_rule_version",
        "detection_timestamp",
        "followup_timestamp",
        "model_id",
        "model_version_returned",
        "provider",
        "api_endpoint",
        "prompt_version",
        "sha256_manifest",
        "prompt_verbatim",
        "response_verbatim",
        "input_tokens",
        "output_tokens",
        "latency_ms",
        "stop_reason",
        "version_drift_flag",
    }
    for field in required_fields:
        assert field in d, f"Missing field in model_dump(): {field}"
