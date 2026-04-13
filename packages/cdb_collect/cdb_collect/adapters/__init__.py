"""Provider adapters — one file per API surface.

See ARCHITECTURE.md §4.1.2.
"""

from cdb_collect.adapters.anthropic import AnthropicAdapter
from cdb_collect.adapters.base import AdapterResult, ModelAdapter

__all__ = ["AdapterResult", "AnthropicAdapter", "ModelAdapter"]
