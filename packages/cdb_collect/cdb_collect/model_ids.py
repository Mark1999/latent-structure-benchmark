"""Canonical model ID mappings between direct-API and OpenRouter formats.

Direct-API adapters use provider-specific short IDs (e.g., "claude-opus-4-6")
while the registry and OpenRouter use prefixed IDs (e.g., "anthropic/claude-opus-4.6").
This module provides the single source of truth for these mappings.

Only models with non-trivial ID differences need entries here. Models where
the mapping is just stripping a prefix (e.g., "x-ai/grok-4.20" → "grok-4.20")
are handled by PROVIDER_CONFIGS in openai_compat.py.
"""

from __future__ import annotations

# Registry/OpenRouter ID → direct adapter model ID
# Only needed for Anthropic (uses dashes not dots, no provider prefix)
REGISTRY_TO_DIRECT: dict[str, str] = {
    "anthropic/claude-opus-4.6": "claude-opus-4-6",
    "anthropic/claude-opus-4.5": "claude-opus-4-5",
    "anthropic/claude-sonnet-4.6": "claude-sonnet-4-6",
    "anthropic/claude-haiku-4.5": "claude-haiku-4-5",
}

# Inverse: direct adapter model ID → registry/OpenRouter ID
DIRECT_TO_REGISTRY: dict[str, str] = {v: k for k, v in REGISTRY_TO_DIRECT.items()}


def to_direct_id(registry_id: str) -> str:
    """Convert a registry/OpenRouter model ID to the direct adapter ID."""
    return REGISTRY_TO_DIRECT.get(registry_id, registry_id)


def to_registry_id(direct_id: str) -> str:
    """Convert a direct adapter model ID to the registry/OpenRouter ID."""
    return DIRECT_TO_REGISTRY.get(direct_id, direct_id)
