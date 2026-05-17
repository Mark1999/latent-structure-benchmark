"""Social post drafters — one per platform/format. See ARCHITECTURE.md §4.6.

Public API:

    from cdb_social.drafters import (
        DrafterBase,
        DrafterRejectedException,
        BlueskyDrafter,
        validate_draft,
        load_prompt,
    )

Validator sub-functions are also importable for testing:

    from cdb_social.drafters import (
        validate_draft_forbidden_vocab,
        validate_draft_numeric_ci_adjacency,
        validate_draft_hypothesis_framing,
    )
"""

from cdb_social.drafters.base import (
    CI_SHAPE_REGEX,
    DrafterBase,
    DrafterRejectedException,
    load_prompt,
    validate_draft,
    validate_draft_forbidden_vocab,
    validate_draft_hypothesis_framing,
    validate_draft_numeric_ci_adjacency,
)
from cdb_social.drafters.bluesky import BlueskyDrafter

__all__ = [
    "DrafterBase",
    "DrafterRejectedException",
    "BlueskyDrafter",
    "validate_draft",
    "validate_draft_forbidden_vocab",
    "validate_draft_numeric_ci_adjacency",
    "validate_draft_hypothesis_framing",
    "load_prompt",
    "CI_SHAPE_REGEX",
]
