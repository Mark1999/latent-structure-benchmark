"""Bluesky drafter — Phase 7 T3.

Subclass of DrafterBase that calls Anthropic (Claude) to generate a Bluesky
post from a SocialTrigger + DomainResult.

Key design decisions (per CDA SME §5.4–§5.10):
- System prompt loaded from prompts/v1/bluesky.md and cached via
  ``cache_control={"type": "ephemeral"}`` per ARCHITECTURE.md §6.2.
- Per-call payload is data-only (trigger evidence + domain numerics + URLs).
  NO methodology copy in the per-call payload.
- ``drafter_self_rating = 0.5`` fixed; LLM is NOT prompted to self-rate.
- Output ≤ 300 chars; target ≤ 270 chars (30-char URL buffer).
- Suggested posting time: next weekday 14:00 UTC (v1 algorithm).
- Methodology URL defaults to article-shell URL; link labeled "details".

The Anthropic client comes from ``anthropic`` SDK directly (no separate
cdb_core helper exists for the social layer).  The client is injected via the
constructor so tests can supply a mock without importing the real SDK.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime, timedelta
from typing import Any

from cdb_core.schemas import DomainResult, Platform, SocialTrigger

from cdb_social.drafters.base import DrafterBase, load_prompt

logger = logging.getLogger(__name__)

# Bluesky hard character limit per platform spec.
_BLUESKY_CHAR_LIMIT: int = 300
# Target ≤ 270 chars to leave ~30-char buffer for URL display variations.
_BLUESKY_TARGET_CHARS: int = 270

# Default article-shell base URL (until Phase 6 T1+T2 land methodology page).
_ARTICLE_SHELL_BASE = "https://cogstructurelab.com"


class BlueskyDrafter(DrafterBase):
    """Bluesky drafter subclass.

    Generates a single Bluesky post (≤ 300 chars) from a SocialTrigger and
    DomainResult.  Uses Anthropic prompt caching on the system prompt per
    ARCHITECTURE.md §6.2.

    Parameters
    ----------
    anthropic_client:
        An Anthropic client instance (real or mock).  If None, the real
        ``anthropic.Anthropic`` client is constructed from the
        ``ANTHROPIC_API_KEY`` environment variable.
    model_id:
        The Claude model to use for drafting.  Defaults to claude-sonnet-4-6.
    """

    platform: Platform = Platform.BLUESKY
    drafter_version: str = "bluesky-v1"
    prompt_version: str = "v1"

    def __init__(
        self,
        anthropic_client: Any | None = None,
        *,
        model_id: str = "claude-sonnet-4-6",
    ) -> None:
        if anthropic_client is not None:
            self._client = anthropic_client
        else:
            import anthropic  # noqa: PLC0415
            self._client = anthropic.Anthropic(
                api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            )
        self._model_id = model_id
        # Load system prompt once; it is stable across calls.
        self._system_prompt = load_prompt("bluesky", self.prompt_version)

    # ─────────────────────────────────────────────────────────────────────────
    # DrafterBase abstract implementations
    # ─────────────────────────────────────────────────────────────────────────

    def _get_length_limit(self) -> int:
        return _BLUESKY_CHAR_LIMIT

    def _suggested_posting_time(self) -> datetime:
        """Next weekday 14:00 UTC — v1 algorithm per kickoff spec."""
        now = datetime.now(UTC)
        # Advance to 14:00 UTC today (or tomorrow if we're past it today).
        candidate = now.replace(hour=14, minute=0, second=0, microsecond=0)
        if candidate <= now:
            candidate += timedelta(days=1)
        # Skip weekends (Saturday=5, Sunday=6).
        while candidate.weekday() >= 5:
            candidate += timedelta(days=1)
        return candidate

    def _build_methodology_url(self, domain_slug: str | None) -> str:
        """Article-shell URL (default until Phase 6 T1+T2 land).

        Link is labeled "details" in the post — NOT "methodology" per
        CDA SME §5.5.
        """
        if domain_slug:
            return f"{_ARTICLE_SHELL_BASE}/{domain_slug}"
        return _ARTICLE_SHELL_BASE

    def _build_dashboard_url(self, domain_slug: str | None) -> str:
        """Dashboard URL — same as methodology_url in Phase 7 v1."""
        return self._build_methodology_url(domain_slug)

    # ─────────────────────────────────────────────────────────────────────────
    # LLM call (cached system prompt + data-only per-call payload)
    # ─────────────────────────────────────────────────────────────────────────

    def _draft_text(
        self,
        trigger: SocialTrigger,
        domain_result: DomainResult,
    ) -> str:
        """Call Claude with the cached system prompt and data-only user payload.

        The system prompt block carries ``cache_control={"type": "ephemeral"}``
        per ARCHITECTURE.md §6.2.  The per-call payload is data-only — NO
        methodology copy per CDA SME §5.10.
        """
        user_payload = self._build_user_payload(trigger, domain_result)

        response = self._client.messages.create(
            model=self._model_id,
            max_tokens=512,  # posts are short; 512 is generous
            system=[
                {
                    "type": "text",
                    "text": self._system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": user_payload,
                }
            ],
        )

        # Extract text from the response.
        text = ""
        for block in response.content:
            if hasattr(block, "text"):
                text += block.text
        return text.strip()

    def _build_user_payload(
        self,
        trigger: SocialTrigger,
        domain_result: DomainResult,
    ) -> str:
        """Construct the data-only per-call payload (§5.10).

        Contains ONLY:
        - trigger_type and trigger evidence dict
        - domain_result numeric findings with CIs
        - methodology_url and dashboard_url
        - model_id and domain_slug

        NO methodology copy. No lede patterns. No framing instructions.
        Those live exclusively in the cached system prompt.
        """
        domain_slug = trigger.domain_slug
        model_id = trigger.model_id

        # Build domain numerics block from DomainResult.
        numerics = self._extract_numerics(domain_result)

        payload: dict[str, Any] = {
            "trigger_type": trigger.trigger_type.value,
            "domain_slug": domain_slug,
            "model_id": model_id,
            "trigger_evidence": trigger.evidence,
            "domain_numerics": numerics,
            "methodology_url": self._build_methodology_url(domain_slug),
            "dashboard_url": self._build_dashboard_url(domain_slug),
        }

        return (
            "Generate a Bluesky post for the following LSB trigger event.\n\n"
            f"DATA:\n{json.dumps(payload, indent=2, ensure_ascii=False)}"
        )

    def _extract_numerics(self, domain_result: DomainResult) -> dict[str, Any]:
        """Extract relevant numerics from DomainResult for the per-call payload.

        Returns a structured dict containing the primary findings with their
        CIs.  The exact selection depends on what the drafter needs to
        construct a valid post.
        """
        numerics: dict[str, Any] = {
            "domain_slug": domain_result.domain_slug,
            "n_models": len(domain_result.models),
            "consensus_score": domain_result.consensus_score,
            "consensus_ci": list(domain_result.consensus_ci),
        }

        if domain_result.romney_eigenratio is not None:
            numerics["romney_eigenratio"] = domain_result.romney_eigenratio

        if domain_result.consensus_type is not None:
            numerics["consensus_type"] = domain_result.consensus_type

        # Per-model OCI values (Register 1)
        if domain_result.within_model_results:
            oci_per_model = {}
            for wmr in domain_result.within_model_results:
                entry: dict[str, Any] = {"oci": wmr.oci}
                if wmr.oci_ci:
                    entry["oci_ci"] = list(wmr.oci_ci)
                oci_per_model[wmr.model_id] = entry
            numerics["oci_per_model"] = oci_per_model

        # Pairwise similarity matrix summary (for DIVERGENCE trigger)
        if domain_result.similarity_matrix:
            n = len(domain_result.similarity_matrix)
            # Find max off-diagonal similarity gap
            max_gap = 0.0
            for i in range(n):
                for j in range(i + 1, n):
                    val = domain_result.similarity_matrix[i][j]
                    if val > max_gap:
                        max_gap = val
            numerics["max_pairwise_similarity_gap"] = round(max_gap, 4)

        return numerics
