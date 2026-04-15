"""xAI Grok API adapter — backward-compatibility alias.

The implementation now lives in openai_compat.py which handles all
OpenAI-compatible providers (xAI, OpenAI, DeepSeek, Mistral).
"""

from cdb_collect.adapters.openai_compat import (
    OpenAICompatAdapter as XAIAdapter,
)
from cdb_collect.adapters.openai_compat import (
    _scrub_response,
)
from cdb_collect.adapters.openai_compat import (
    extract_thinking as _extract_inline_thinking,
)

__all__ = ["XAIAdapter", "_extract_inline_thinking", "_scrub_response"]
