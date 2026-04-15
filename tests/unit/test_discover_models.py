"""Tests for the model discovery script. No real API calls — uses fixtures."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.discover_models import (
    _parse_pricing,
    build_registry_entry,
    classify_model,
    is_excluded,
    load_collected_models,
    normalize_model_id,
    scan,
    select_flagships,
)

# ── Fixtures ──────────────────────────────────────────────────────────

def _make_catalog_model(
    model_id: str,
    *,
    modality: str = "text->text",
    created: int = 1770000000,
    prompt_price: str = "0.000002",
    completion_price: str = "0.000010",
    context_length: int = 128000,
    supported_params: list[str] | None = None,
) -> dict:
    return {
        "id": model_id,
        "name": model_id,
        "architecture": {"modality": modality},
        "created": created,
        "pricing": {"prompt": prompt_price, "completion": completion_price},
        "context_length": context_length,
        "supported_parameters": supported_params or [],
    }


def _sample_catalog() -> list[dict]:
    """A minimal catalog covering several families and edge cases."""
    return [
        _make_catalog_model("anthropic/claude-opus-4.6", created=1770000000),
        _make_catalog_model("anthropic/claude-sonnet-4.6", created=1769000000),
        _make_catalog_model("anthropic/claude-opus-4.6-fast", created=1770000000),
        _make_catalog_model("openai/gpt-5.4", created=1772000000,
                            supported_params=["include_reasoning"]),
        _make_catalog_model("openai/gpt-5.4-mini", created=1771000000),
        _make_catalog_model("openai/gpt-5.4:free", created=1772000000),
        _make_catalog_model("x-ai/grok-4.20", created=1774000000,
                            supported_params=["reasoning"]),
        _make_catalog_model("x-ai/grok-4.20-multi-agent", created=1774000000),
        _make_catalog_model("meta-llama/llama-4-maverick", created=1743000000),
        _make_catalog_model("deepseek/deepseek-v3.2", created=1764000000,
                            supported_params=["include_reasoning"]),
        _make_catalog_model("google/gemini-2.5-pro", created=1750000000),
        _make_catalog_model("google/gemma-4-26b-a4b-it", created=1775000000),
        _make_catalog_model("qwen/qwen3.6-plus", created=1775000000),
        _make_catalog_model("mistralai/mistral-large-2512", created=1764000000),
        _make_catalog_model("cohere/command-a", created=1741000000),
        _make_catalog_model("microsoft/phi-4", created=1736000000),
        _make_catalog_model("amazon/nova-premier-v1", created=1761000000),
        # Non-text model — should be excluded
        _make_catalog_model("openai/dall-e-3", modality="text->image"),
        # Third-party re-host — should be excluded
        _make_catalog_model("nex-agi/deepseek-v3.1-nex-n1", created=1764000000),
        # Premium pricing — should be excluded (>$20/M input)
        _make_catalog_model("openai/gpt-5.4-pro-20260305", created=1772000000,
                            prompt_price="0.000030"),
    ]


# ── classify_model ────────────────────────────────────────────────────

def test_classify_openrouter_prefixed():
    assert classify_model("anthropic/claude-opus-4.6") == "claude"
    assert classify_model("openai/gpt-5.4") == "gpt"
    assert classify_model("x-ai/grok-4.20") == "grok"
    assert classify_model("meta-llama/llama-4-maverick") == "llama"
    assert classify_model("deepseek/deepseek-v3.2") == "deepseek"
    assert classify_model("google/gemini-2.5-pro") == "gemini"


def test_classify_direct_api_ids():
    assert classify_model("claude-opus-4-6") == "claude"
    assert classify_model("claude-sonnet-4-6") == "claude"


def test_classify_huggingface_ids():
    assert classify_model("Qwen/Qwen2.5-72B-Instruct") == "qwen"


def test_classify_unknown():
    assert classify_model("some-random-model") is None


# ── is_excluded ───────────────────────────────────────────────────────

def test_excluded_variants():
    assert is_excluded("openai/gpt-5.4:free")
    assert is_excluded("anthropic/claude-opus-4.6-fast")
    assert is_excluded("x-ai/grok-4.20-multi-agent")
    assert is_excluded("meta-llama/llama-guard-4-12b")
    assert is_excluded("openai/gpt-5.4-20260305")
    assert is_excluded("google/gemini-3.1-flash-lite-preview")


def test_not_excluded():
    assert not is_excluded("anthropic/claude-opus-4.6")
    assert not is_excluded("openai/gpt-5.4")
    assert not is_excluded("x-ai/grok-4.20")
    assert not is_excluded("deepseek/deepseek-v3.2")


# ── normalize_model_id ────────────────────────────────────────────────

def test_normalize_direct_ids():
    assert normalize_model_id("claude-opus-4-6") == "anthropic/claude-opus-4.6"
    assert normalize_model_id("claude-sonnet-4-6") == "anthropic/claude-sonnet-4.6"


def test_normalize_passthrough():
    assert normalize_model_id("openai/gpt-5.4") == "openai/gpt-5.4"
    assert normalize_model_id("x-ai/grok-4.20") == "x-ai/grok-4.20"


# ── _parse_pricing ────────────────────────────────────────────────────

def test_parse_pricing():
    inp, out = _parse_pricing({"prompt": "0.000002", "completion": "0.000010"})
    assert abs(inp - 2.0) < 0.01
    assert abs(out - 10.0) < 0.01


def test_parse_pricing_empty():
    inp, out = _parse_pricing({})
    assert inp == 0.0
    assert out == 0.0


# ── select_flagships ──────────────────────────────────────────────────

def test_select_flagships_filters_correctly():
    catalog = _sample_catalog()
    selected = select_flagships(catalog)

    # Should have entries for tracked families
    assert "claude" in selected
    assert "gpt" in selected
    assert "grok" in selected

    # Excluded variants should not appear
    all_ids = {m["id"] for models in selected.values() for m in models}
    assert "openai/gpt-5.4:free" not in all_ids
    assert "anthropic/claude-opus-4.6-fast" not in all_ids
    assert "x-ai/grok-4.20-multi-agent" not in all_ids
    assert "openai/dall-e-3" not in all_ids
    assert "nex-agi/deepseek-v3.1-nex-n1" not in all_ids
    assert "openai/gpt-5.4-pro-20260305" not in all_ids


def test_select_flagships_respects_max_tiers():
    catalog = _sample_catalog()
    selected = select_flagships(catalog)

    # Claude allows 3 tiers, but only 2 canonical non-excluded models exist
    assert len(selected["claude"]) <= 3

    # Grok allows 2 tiers, only 1 non-excluded model
    assert len(selected["grok"]) <= 2


# ── build_registry_entry ──────────────────────────────────────────────

def test_build_registry_entry():
    model = _make_catalog_model(
        "deepseek/deepseek-v3.2",
        created=1764000000,
        supported_params=["include_reasoning"],
    )
    entry = build_registry_entry(model, "deepseek")
    assert entry["model_id"] == "deepseek/deepseek-v3.2"
    assert entry["family"] == "deepseek"
    assert entry["origin"] == "cn"
    assert entry["open_weights"] is True
    assert entry["supports_reasoning"] is True
    assert entry["collection_method"] == "openrouter"


# ── load_collected_models ─────────────────────────────────────────────

def test_load_collected_models(tmp_path: Path):
    jsonl = tmp_path / "informants.jsonl"
    records = [
        {"model_id": "claude-opus-4-6", "domain_slug": "family"},
        {"model_id": "claude-opus-4-6", "domain_slug": "family"},
        {"model_id": "openai/gpt-4o", "domain_slug": "family"},
    ]
    jsonl.write_text("\n".join(json.dumps(r) for r in records) + "\n")

    collected = load_collected_models(jsonl)
    assert collected["claude-opus-4-6"] == 2
    assert collected["openai/gpt-4o"] == 1
    # Normalized alias should also be present
    assert collected["anthropic/claude-opus-4.6"] == 2


def test_load_collected_empty(tmp_path: Path):
    jsonl = tmp_path / "informants.jsonl"
    assert load_collected_models(jsonl) == {}


# ── scan ──────────────────────────────────────────────────────────────

def test_scan_new_and_current():
    catalog = _sample_catalog()
    collected = {"anthropic/claude-opus-4.6": 30, "claude-opus-4-6": 30}

    report = scan(catalog, collected)

    assert report["tracked_families"] == 12
    assert len(report["current"]) >= 1
    assert len(report["new"]) > 0

    # Claude opus should be current, not new
    current_ids = {m["model_id"] for m in report["current"]}
    assert "anthropic/claude-opus-4.6" in current_ids

    # New models should not include collected ones
    new_ids = {m["model_id"] for m in report["new"]}
    assert "anthropic/claude-opus-4.6" not in new_ids


def test_scan_stale_models():
    catalog = _sample_catalog()
    collected = {"old-model/deprecated-v1": 10}

    report = scan(catalog, collected)

    stale_ids = {m["model_id"] for m in report["stale"]}
    assert "old-model/deprecated-v1" in stale_ids
