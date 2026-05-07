"""Adaptive max_tokens computation for per-model context-window constraints.

Per Phase 4b Architect plan §7.1 (docs/status/2026-05-07-phase4b-architect-plan.md):

    effective_max_tokens = min(
        MAX_OUTPUT_TOKENS_CONFIG,
        max(MIN_OUTPUT_TOKENS, model.context_length - estimated_input_tokens - SAFETY_MARGIN)
    )

Background
----------
Task #16 raised the global OpenRouter max_tokens cap to 16384 (see
docs/status/2026-05-04-task-16-architect-plan.md §2 Task 16.A). That cap
unblocks large-context models (≥163K context) but collides with phi-4's 16K
total context window: on phi-4 the input prompt itself consumes ~2K tokens,
leaving no headroom for output at a 16384 cap. This module resolves that by
computing an effective cap that respects each model's actual context window.

The helper is intentionally stateless and side-effect-free so it can be unit-
tested against synthetic inputs without any API calls (CLAUDE.md §6 R10).

Usage
-----
    from cdb_collect.adaptive_cap import compute_effective_max_tokens

    max_tok = compute_effective_max_tokens(
        prompt_text=prompt,
        context_length=16384,   # from registry.json
    )
    # max_tok == 13872 for phi-4 with a ~2K-token prompt
"""

from __future__ import annotations

__all__ = ["compute_effective_max_tokens", "MAX_OUTPUT_TOKENS_CONFIG"]

# ── Constants ──────────────────────────────────────────────────────────────

#: Global output-token cap introduced in Task #16. All current large-context
#: models (≥163K) hit this ceiling rather than the context-window arithmetic.
MAX_OUTPUT_TOKENS_CONFIG: int = 16384

#: Safety margin (tokens) subtracted from context_length to leave room for
#: tokenisation variance, system prompt overhead, and provider-side rounding.
_SAFETY_MARGIN: int = 512

#: Minimum meaningful output-token allocation. If the arithmetic would produce
#: a value below this floor, this floor is returned instead. Callers should
#: treat a returned value at or very close to this floor as a warning that
#: the prompt is close to exhausting the model's context window.
MIN_OUTPUT_TOKENS: int = 1024

#: Characters-per-token approximation used when no tokeniser is available.
#: A conservative over-estimate (real English prose is typically 3.5–4.5
#: chars/token). Over-estimating input shrinks the output budget slightly,
#: which is the safe direction (under-estimating would produce a cap that
#: still overflows the context window).
_CHARS_PER_TOKEN_APPROX: float = 4.0


# ── Public function ────────────────────────────────────────────────────────

def compute_effective_max_tokens(
    prompt_text: str,
    context_length: int,
    *,
    safety_margin: int = _SAFETY_MARGIN,
    min_output_tokens: int = MIN_OUTPUT_TOKENS,
    max_output_tokens_config: int = MAX_OUTPUT_TOKENS_CONFIG,
) -> int:
    """Return the effective max_tokens budget for a given model and prompt.

    Computes::

        estimated_input = ceil(len(prompt_text) / _CHARS_PER_TOKEN_APPROX)
        budget = context_length - estimated_input - safety_margin
        effective = min(max_output_tokens_config, max(min_output_tokens, budget))

    The 4-chars-per-token approximation is used unconditionally. A tokeniser-
    based path is intentionally omitted: LSB calls models across providers with
    different tokenisers; a single approximation that slightly over-estimates
    input tokens is conservative and correct in the failure-safe direction.

    Args:
        prompt_text: The verbatim prompt string that will be sent to the model.
            Used only to estimate token count.
        context_length: Total context window for the model (tokens), read from
            data/models/registry.json. For models with very large contexts
            (≥163K) this value produces an effective cap equal to
            max_output_tokens_config (the ceiling case).
        safety_margin: Tokens reserved for tokenisation variance, system-prompt
            overhead, and provider-side rounding. Default 512.
        min_output_tokens: Floor on the returned value. Default 1024.
        max_output_tokens_config: Upper ceiling on the returned value.
            Default MAX_OUTPUT_TOKENS_CONFIG (16384).

    Returns:
        effective max_tokens as an int in [min_output_tokens, max_output_tokens_config].

    Notes:
        - The function is idempotent: calling it twice with the same arguments
          returns the same value.
        - No API calls, no filesystem access. Safe to call in tests.
    """
    import math

    estimated_input_tokens: int = math.ceil(
        len(prompt_text) / _CHARS_PER_TOKEN_APPROX
    )

    budget = context_length - estimated_input_tokens - safety_margin

    effective = min(
        max_output_tokens_config,
        max(min_output_tokens, budget),
    )
    return effective
