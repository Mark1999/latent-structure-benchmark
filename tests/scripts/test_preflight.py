"""Tests for scripts/preflight.py.

No real API calls — adapters are mocked per CLAUDE.md §6 rule 10.

Coverage
--------
- _load_model_ref: extracts ModelRef correctly from registry, applies
  Anthropic direct-ID mapping (dashes not dots), raises on unknown model.
- _create_adapter: routes each collection_method to the correct adapter class.
- _write_report: produces a Markdown file with expected content.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.preflight import (
    ProbeResult,
    _create_adapter,
    _load_model_ref,
    _write_report,
)

# ---------------------------------------------------------------------------
# Minimal registry fixture
# ---------------------------------------------------------------------------

_REGISTRY = {
    "updated_at": "2026-04-22",
    "models": [
        {
            "model_id": "anthropic/claude-sonnet-4.6",
            "family": "claude",
            "origin": "us",
            "open_weights": False,
            "collection_method": "anthropic_api",
            "pricing_input_per_m": 3.0,
            "pricing_output_per_m": 15.0,
            "openrouter_created": 1771342990,
        },
        {
            "model_id": "x-ai/grok-4",
            "family": "grok",
            "origin": "us",
            "open_weights": False,
            "collection_method": "xai_api",
            "pricing_input_per_m": 3.0,
            "pricing_output_per_m": 15.0,
            "openrouter_created": 1752087689,
        },
        {
            "model_id": "openai/gpt-5.4-mini",
            "family": "gpt",
            "origin": "us",
            "open_weights": False,
            "collection_method": "openai_api",
            "pricing_input_per_m": 0.75,
            "pricing_output_per_m": 4.5,
            "openrouter_created": 1773748178,
        },
        {
            "model_id": "google/gemini-2.5-pro",
            "family": "gemini",
            "origin": "us",
            "open_weights": False,
            "collection_method": "google_ai",
            "pricing_input_per_m": 1.25,
            "pricing_output_per_m": 10.0,
            "openrouter_created": 1750169544,
        },
        {
            "model_id": "mistralai/mistral-small-2603",
            "family": "mistral",
            "origin": "eu",
            "open_weights": False,
            "collection_method": "openrouter",
            "pricing_input_per_m": 0.15,
            "pricing_output_per_m": 0.6,
            "openrouter_created": 1773695685,
        },
    ],
}


@pytest.fixture()
def registry_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Write a minimal registry.json and patch REGISTRY_PATH."""
    reg_path = tmp_path / "registry.json"
    reg_path.write_text(json.dumps(_REGISTRY), encoding="utf-8")
    monkeypatch.setattr("scripts.preflight.REGISTRY_PATH", reg_path)
    return reg_path


# ---------------------------------------------------------------------------
# _load_model_ref
# ---------------------------------------------------------------------------

def test_anthropic_model_ref_uses_dash_form(registry_file: Path) -> None:
    """Anthropic models must use the dash-form direct ID (no provider prefix)."""
    ref = _load_model_ref("anthropic/claude-sonnet-4.6")
    # Anthropic direct API uses dashes not dots, no prefix
    assert ref.model_id == "claude-sonnet-4-6"
    assert ref.collection_method == "anthropic_api"
    assert ref.provider == "anthropic"
    assert ref.family == "claude"
    assert ref.origin == "us"
    assert ref.open_weights is False


def test_xai_model_ref_preserves_slash_form(registry_file: Path) -> None:
    """xAI models use the registry ID as-is (prefix stripped by adapter)."""
    ref = _load_model_ref("x-ai/grok-4")
    assert ref.model_id == "x-ai/grok-4"
    assert ref.collection_method == "xai_api"
    assert ref.provider == "xai"


def test_openai_model_ref(registry_file: Path) -> None:
    ref = _load_model_ref("openai/gpt-5.4-mini")
    assert ref.model_id == "openai/gpt-5.4-mini"
    assert ref.collection_method == "openai_api"
    assert ref.provider == "openai"


def test_google_model_ref(registry_file: Path) -> None:
    ref = _load_model_ref("google/gemini-2.5-pro")
    assert ref.model_id == "google/gemini-2.5-pro"
    assert ref.collection_method == "google_ai"
    assert ref.provider == "google"


def test_openrouter_model_ref(registry_file: Path) -> None:
    ref = _load_model_ref("mistralai/mistral-small-2603")
    assert ref.model_id == "mistralai/mistral-small-2603"
    assert ref.collection_method == "openrouter"
    assert ref.provider == "openrouter"


def test_unknown_model_raises(registry_file: Path) -> None:
    with pytest.raises(KeyError, match="not found in registry"):
        _load_model_ref("nonexistent/model-999")


def test_missing_registry_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("scripts.preflight.REGISTRY_PATH", tmp_path / "missing.json")
    with pytest.raises(RuntimeError, match="Registry not found"):
        _load_model_ref("anthropic/claude-sonnet-4.6")


# ---------------------------------------------------------------------------
# _create_adapter — routing only, no API calls
# ---------------------------------------------------------------------------

def test_create_adapter_anthropic(registry_file: Path) -> None:
    from cdb_collect.adapters import AnthropicAdapter
    ref = _load_model_ref("anthropic/claude-sonnet-4.6")
    adapter = _create_adapter(ref)
    assert isinstance(adapter, AnthropicAdapter)


def test_create_adapter_xai(registry_file: Path) -> None:
    from cdb_collect.adapters import OpenAICompatAdapter
    ref = _load_model_ref("x-ai/grok-4")
    adapter = _create_adapter(ref)
    assert isinstance(adapter, OpenAICompatAdapter)


def test_create_adapter_openai(registry_file: Path) -> None:
    from cdb_collect.adapters import OpenAICompatAdapter
    ref = _load_model_ref("openai/gpt-5.4-mini")
    adapter = _create_adapter(ref)
    assert isinstance(adapter, OpenAICompatAdapter)


def test_create_adapter_google(
    registry_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from cdb_collect.adapters import GeminiAdapter
    monkeypatch.setenv("GOOGLE_API_KEY", "test-dummy")
    ref = _load_model_ref("google/gemini-2.5-pro")
    adapter = _create_adapter(ref)
    assert isinstance(adapter, GeminiAdapter)


def test_create_adapter_openrouter(registry_file: Path) -> None:
    from cdb_collect.adapters import OpenRouterAdapter
    ref = _load_model_ref("mistralai/mistral-small-2603")
    adapter = _create_adapter(ref)
    assert isinstance(adapter, OpenRouterAdapter)


# ---------------------------------------------------------------------------
# _write_report
# ---------------------------------------------------------------------------

def test_write_report_creates_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    report_path = tmp_path / "preflight.md"
    monkeypatch.setattr("scripts.preflight.REPORT_PATH", report_path)

    results = [
        ProbeResult(
            collection_method="anthropic_api",
            model_id="anthropic/claude-sonnet-4.6",
            reason="test",
            passed=True,
            latency_ms=500,
            model_version_returned="claude-sonnet-4-6",
            input_tokens=20,
            output_tokens=4,
            response_text="ok",
            error="",
        ),
        ProbeResult(
            collection_method="xai_api",
            model_id="x-ai/grok-4",
            reason="test",
            passed=False,
            latency_ms=1000,
            model_version_returned="",
            input_tokens=0,
            output_tokens=0,
            response_text="",
            error="HTTP 401: Unauthorized",
        ),
    ]

    _write_report(results, "2026-04-22T18:00:00+00:00")

    assert report_path.exists()
    text = report_path.read_text(encoding="utf-8")

    # Summary line
    assert "1/2 collection_methods PASS" in text
    # PASS row
    assert "anthropic_api" in text
    assert "claude-sonnet-4-6" in text
    # FAIL row
    assert "xai_api" in text
    assert "**FAIL**" in text
    # Error detail
    assert "HTTP 401: Unauthorized" in text


def test_write_report_all_pass(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    report_path = tmp_path / "preflight.md"
    monkeypatch.setattr("scripts.preflight.REPORT_PATH", report_path)

    results = [
        ProbeResult(
            collection_method=f"method_{i}",
            model_id=f"provider/model-{i}",
            reason="test",
            passed=True,
            latency_ms=100 * i,
            model_version_returned=f"model-{i}-snapshot",
            input_tokens=10,
            output_tokens=2,
            response_text="ok",
            error="",
        )
        for i in range(1, 6)
    ]

    _write_report(results, "2026-04-22T18:00:00+00:00")
    text = report_path.read_text(encoding="utf-8")
    assert "5/5 collection_methods PASS" in text
    assert "**FAIL**" not in text
