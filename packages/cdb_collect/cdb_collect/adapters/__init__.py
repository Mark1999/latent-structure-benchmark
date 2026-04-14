"""Provider adapters — one file per API surface.

See ARCHITECTURE.md §4.1.2.
"""

from cdb_collect.adapters.anthropic import AnthropicAdapter
from cdb_collect.adapters.base import AdapterResult, ModelAdapter
from cdb_collect.adapters.huggingface import HuggingFaceAdapter
from cdb_collect.adapters.openrouter import OpenRouterAdapter

__all__ = [
    "AdapterResult",
    "AnthropicAdapter",
    "HuggingFaceAdapter",
    "ModelAdapter",
    "OpenRouterAdapter",
]
