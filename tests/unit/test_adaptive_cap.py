"""Unit tests for the adaptive max_tokens helper.

Tests cover the five mandatory cases from Phase 4b T2 acceptance criteria:
  1. phi-4 case: 16K context, ~2K input → ~13.5K effective cap
  2. Long-context case: 1M context, 1K input → MAX_OUTPUT_TOKENS_CONFIG (16384)
  3. Borderline case: input that would leave less than the 1024 floor → 1024
  4. No-tokeniser fallback: 4-chars/token approximation is used unconditionally
  5. Idempotence: calling twice with the same args returns the same result

No real API calls. All inputs are synthetic strings (CLAUDE.md §6 R10).

References:
  - Phase 4b architect plan §7.1:
      docs/status/2026-05-07-phase4b-architect-plan.md
  - adaptive_cap module:
      packages/cdb_collect/cdb_collect/adaptive_cap.py
"""

from __future__ import annotations

import math

from cdb_collect.adaptive_cap import (
    MAX_OUTPUT_TOKENS_CONFIG,
    MIN_OUTPUT_TOKENS,
    compute_effective_max_tokens,
)

# ── Helpers ────────────────────────────────────────────────────────────────

_CHARS_PER_TOKEN = 4.0  # matches module constant (not imported to keep tests white-box)


def _synthetic_prompt(n_chars: int) -> str:
    """Return a synthetic prompt string of exactly n_chars characters."""
    return "x" * n_chars


# ── Test 1: phi-4 case ─────────────────────────────────────────────────────

def test_phi4_typical_prompt():
    """phi-4: 16K total context, ~2K-token prompt → cap well under 16384."""
    # ~2000 tokens × 4 chars/token = 8000 chars
    prompt = _synthetic_prompt(8_000)
    result = compute_effective_max_tokens(prompt, context_length=16_384)

    # expected: 16384 - 2000 - 512 = 13872
    estimated_input = math.ceil(8_000 / _CHARS_PER_TOKEN)  # 2000
    expected = 16_384 - estimated_input - 512  # 13872
    assert result == expected
    assert result < MAX_OUTPUT_TOKENS_CONFIG
    assert result > MIN_OUTPUT_TOKENS
    # Roughly in the "~13.5K" range the plan describes
    assert 13_000 <= result <= 14_500


def test_phi4_small_prompt():
    """phi-4 with a minimal prompt still leaves substantial output headroom."""
    prompt = _synthetic_prompt(400)  # ~100 tokens
    result = compute_effective_max_tokens(prompt, context_length=16_384)
    # 16384 - 100 - 512 = 15772 → capped at MAX_OUTPUT_TOKENS_CONFIG? No:
    # 15772 < 16384 so it IS the result directly
    estimated_input = math.ceil(400 / _CHARS_PER_TOKEN)  # 100
    expected = 16_384 - estimated_input - 512  # 15772
    assert result == expected
    assert result > 15_000


# ── Test 2: long-context case ──────────────────────────────────────────────

def test_large_context_returns_config_cap():
    """1M-context model with a 1K-token prompt → result == MAX_OUTPUT_TOKENS_CONFIG."""
    # ~1000 tokens × 4 = 4000 chars
    prompt = _synthetic_prompt(4_000)
    result = compute_effective_max_tokens(prompt, context_length=1_000_000)
    assert result == MAX_OUTPUT_TOKENS_CONFIG


def test_200k_context_returns_config_cap():
    """200K-context model → capped at MAX_OUTPUT_TOKENS_CONFIG."""
    prompt = _synthetic_prompt(4_000)  # ~1K tokens
    result = compute_effective_max_tokens(prompt, context_length=200_000)
    assert result == MAX_OUTPUT_TOKENS_CONFIG


def test_163k_context_returns_config_cap():
    """163K-context model (boundary of current large-context slate) → capped."""
    prompt = _synthetic_prompt(4_000)
    result = compute_effective_max_tokens(prompt, context_length=163_840)
    assert result == MAX_OUTPUT_TOKENS_CONFIG


# ── Test 3: borderline / floor case ───────────────────────────────────────

def test_floor_returned_when_budget_below_minimum():
    """When context_length - input - margin < MIN_OUTPUT_TOKENS, floor is returned."""
    # context_length=2048, safety_margin=512 → available = 1536
    # With a prompt of ~600 tokens (2400 chars), budget = 2048 - 600 - 512 = 936 < 1024
    prompt = _synthetic_prompt(2_400)  # ceil(2400/4) = 600 tokens
    result = compute_effective_max_tokens(prompt, context_length=2_048)
    assert result == MIN_OUTPUT_TOKENS  # 1024


def test_floor_returned_when_budget_goes_negative():
    """When the prompt alone exceeds context_length, the floor is still returned."""
    # context_length=1000, prompt=5000 chars (~1250 tokens) → budget negative
    prompt = _synthetic_prompt(5_000)
    result = compute_effective_max_tokens(prompt, context_length=1_000)
    assert result == MIN_OUTPUT_TOKENS


def test_exact_floor_boundary():
    """Budget exactly equals MIN_OUTPUT_TOKENS → returns MIN_OUTPUT_TOKENS."""
    # We want: context_length - ceil(len/4) - 512 == 1024
    # context_length - estimated_input = 1536
    # Let context_length=2048, then estimated_input must be 512
    # 512 tokens × 4 chars/token = 2048 chars
    prompt = _synthetic_prompt(2_048)  # ceil(2048/4)=512 tokens exactly
    result = compute_effective_max_tokens(prompt, context_length=2_048)
    # budget = 2048 - 512 - 512 = 1024 == MIN_OUTPUT_TOKENS
    assert result == MIN_OUTPUT_TOKENS


# ── Test 4: 4-chars-per-token approximation ───────────────────────────────

def test_approximation_uses_chars_per_token():
    """Helper uses ceil(len/4.0) as the input-token estimate, not an external tokeniser."""
    # 4000-char prompt → ceil(4000/4.0) = 1000 tokens estimated
    prompt_4k = _synthetic_prompt(4_000)
    result_4k = compute_effective_max_tokens(prompt_4k, context_length=16_384)
    expected_4k = min(MAX_OUTPUT_TOKENS_CONFIG, max(MIN_OUTPUT_TOKENS, 16_384 - 1_000 - 512))
    assert result_4k == expected_4k

    # 4004-char prompt → ceil(4004/4.0) = 1001 tokens estimated
    prompt_4004 = _synthetic_prompt(4_004)
    result_4004 = compute_effective_max_tokens(prompt_4004, context_length=16_384)
    expected_4004 = min(MAX_OUTPUT_TOKENS_CONFIG, max(MIN_OUTPUT_TOKENS, 16_384 - 1_001 - 512))
    assert result_4004 == expected_4004

    # Rounding: 4001-char prompt → ceil(4001/4.0) = ceil(1000.25) = 1001 tokens
    prompt_4001 = _synthetic_prompt(4_001)
    result_4001 = compute_effective_max_tokens(prompt_4001, context_length=16_384)
    assert result_4001 == expected_4004  # same estimated_input → same result


def test_empty_prompt_uses_zero_input_tokens():
    """Empty prompt → estimated_input = 0; budget = context_length - safety_margin."""
    result = compute_effective_max_tokens("", context_length=16_384)
    # budget = 16384 - 0 - 512 = 15872; still < MAX_OUTPUT_TOKENS_CONFIG
    assert result == 16_384 - 512  # 15872
    # Large-context model with empty prompt
    result_large = compute_effective_max_tokens("", context_length=1_000_000)
    assert result_large == MAX_OUTPUT_TOKENS_CONFIG


# ── Test 5: idempotence ────────────────────────────────────────────────────

def test_idempotent_phi4():
    """Calling the helper twice with identical arguments returns the same value."""
    prompt = _synthetic_prompt(8_000)
    first = compute_effective_max_tokens(prompt, context_length=16_384)
    second = compute_effective_max_tokens(prompt, context_length=16_384)
    assert first == second


def test_idempotent_large_context():
    """Large-context idempotence check."""
    prompt = _synthetic_prompt(4_000)
    first = compute_effective_max_tokens(prompt, context_length=200_000)
    second = compute_effective_max_tokens(prompt, context_length=200_000)
    assert first == second
    assert first == MAX_OUTPUT_TOKENS_CONFIG


def test_idempotent_floor():
    """Floor case idempotence check."""
    prompt = _synthetic_prompt(5_000)
    first = compute_effective_max_tokens(prompt, context_length=1_000)
    second = compute_effective_max_tokens(prompt, context_length=1_000)
    assert first == second
    assert first == MIN_OUTPUT_TOKENS


# ── Test 6: custom parameter overrides ────────────────────────────────────

def test_custom_safety_margin():
    """Caller can override the default safety_margin."""
    prompt = _synthetic_prompt(4_000)  # 1000 tokens
    result = compute_effective_max_tokens(prompt, context_length=16_384, safety_margin=1024)
    # budget = 16384 - 1000 - 1024 = 14360
    assert result == 14_360


def test_custom_min_output_tokens():
    """Caller can override the min_output_tokens floor."""
    prompt = _synthetic_prompt(5_000)  # context_length=1000 → floor
    result = compute_effective_max_tokens(prompt, context_length=1_000, min_output_tokens=512)
    assert result == 512


def test_custom_max_output_tokens_config():
    """Caller can override the ceiling cap."""
    prompt = _synthetic_prompt(400)
    result = compute_effective_max_tokens(
        prompt, context_length=200_000, max_output_tokens_config=8192,
    )
    assert result == 8192


# ── Test 7: adapter wiring sanity ─────────────────────────────────────────

def test_adapter_context_length_default_is_unconstrained():
    """OpenRouterAdapter with no context_length → max_tokens == MAX_OUTPUT_TOKENS_CONFIG."""
    # This tests the adapter's behaviour without making any real API calls.
    # We inspect the private _context_length attribute set in __init__.
    from datetime import date

    from cdb_collect.adapters.openrouter import OpenRouterAdapter
    from cdb_core import ModelRef

    ref = ModelRef(
        provider="openrouter",
        model_id="meta-llama/llama-4-maverick",
        family="llama",
        origin="us",
        open_weights=True,
        collection_method="openrouter",
        quantization=None,
        release_date=date(2025, 4, 1),
        version_label="llama-4-maverick",
    )
    adapter = OpenRouterAdapter(ref, api_key="sk-test")
    # With the default (no context_length passed), the internal context_length
    # is set to MAX_OUTPUT_TOKENS_CONFIG * 100, so a typical prompt will always
    # produce effective_max_tokens == MAX_OUTPUT_TOKENS_CONFIG.
    short_prompt = _synthetic_prompt(4_000)
    effective = compute_effective_max_tokens(short_prompt, context_length=adapter._context_length)
    assert effective == MAX_OUTPUT_TOKENS_CONFIG


def test_adapter_phi4_context_length_produces_reduced_cap():
    """OpenRouterAdapter with phi-4 context_length=16384 → reduced max_tokens."""
    from datetime import date

    from cdb_collect.adapters.openrouter import OpenRouterAdapter
    from cdb_core import ModelRef

    ref = ModelRef(
        provider="openrouter",
        model_id="microsoft/phi-4",
        family="phi",
        origin="us",
        open_weights=True,
        collection_method="openrouter",
        quantization=None,
        release_date=date(2024, 12, 1),
        version_label="phi-4",
    )
    adapter = OpenRouterAdapter(ref, api_key="sk-test", context_length=16_384)
    # With a ~2K-token prompt, the effective cap should be < 16384
    prompt = _synthetic_prompt(8_000)  # ~2000 tokens
    effective = compute_effective_max_tokens(prompt, context_length=adapter._context_length)
    assert effective < MAX_OUTPUT_TOKENS_CONFIG
    assert effective == 13_872  # 16384 - 2000 - 512
