"""LinkedIn drafter — Phase 7 T4.

Subclass of DrafterBase that calls Anthropic (Claude) to generate a LinkedIn
long-form post from a SocialTrigger + DomainResult.

Key design decisions (per CDA SME T4 §5.4–§5.10):
- System prompt loaded from prompts/v1/linkedin.md and cached via
  ``cache_control={"type": "ephemeral"}`` per ARCHITECTURE.md §6.2.
- Per-call payload is data-only (trigger evidence + domain numerics + URLs).
  NO methodology copy in the per-call payload (T3 §5.10 carry-forward).
  Exception: ``target_char_count`` structural hint per CDA SME T4 §5.12.
- ``drafter_self_rating = 0.5`` fixed; LLM is NOT prompted to self-rate (T3 §5.6).
- K=12 token CI-adjacency window unchanged from T3 (CDA SME T4 §5.6 ruling).
- Hard limit: 3000 chars; soft target: 1500 chars (taught in prompt Block 6).
- LinkedIn-specific anti-thought-leadership patterns (CDA SME T4 §5.5):
    "I've been thinking", "the future of AI", "AI is reshaping"
    all forbidden case-insensitively.  ``\\bI\\b`` forbidden case-sensitively.
- Draft-only: Phase 7 has no live LinkedIn publishing per Mark's §7.1.

The LinkedIn-specific additional framing_checks key:
    ``linkedin_no_thought_leadership``  — True if no forbidden thought-leadership
                                          patterns and no first-person ``\\bI\\b``
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import UTC, datetime, timedelta
from typing import Any

from cdb_core.schemas import DomainResult, Platform, SocialDraft, SocialTrigger

from cdb_social.drafters.base import (
    DrafterBase,
    DrafterRejectedException,
    load_prompt,
    validate_draft,
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# LinkedIn structural constants (CDA SME T4 §5.8)
# ─────────────────────────────────────────────────────────────────────────────

_LINKEDIN_CHAR_HARD_LIMIT: int = 3000
_LINKEDIN_CHAR_SOFT_TARGET: int = 1500  # taught in prompt; not validator-enforced

# Default article-shell base URL (until Phase 6 T1+T2 land methodology page).
_ARTICLE_SHELL_BASE = "https://cogstructurelab.com"

# ─────────────────────────────────────────────────────────────────────────────
# LinkedIn anti-thought-leadership patterns (CDA SME T4 §5.5)
# ─────────────────────────────────────────────────────────────────────────────

# Three LinkedIn-specific thought-leadership forbidden patterns (case-insensitive).
# Applied to LinkedIn drafts only — not to Bluesky or X.
_LINKEDIN_FORBIDDEN_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bI'?ve been thinking\b", re.IGNORECASE),
    re.compile(r"\bthe future of AI\b", re.IGNORECASE),
    re.compile(r"\bAI is reshaping\b", re.IGNORECASE),
]

# First-person pronoun rule: strict — any \bI\b (case-sensitive) rejects the draft.
# LSB social posts are project statements, not personal essays.
# Per CDA SME T4 §5.5: the strict rule is preferred over quote-aware skipping.
_LINKEDIN_FIRST_PERSON_RE = re.compile(r"\bI\b")  # case-sensitive, no re.IGNORECASE


def _check_linkedin_no_first_person(text: str) -> bool:
    """Return True if the text contains NO first-person \\bI\\b (case-sensitive).

    Per CDA SME T4 §5.5: strict rule — any ``\\bI\\b`` match rejects the draft.
    """
    return not bool(_LINKEDIN_FIRST_PERSON_RE.search(text))


def _validate_linkedin_anti_thought_leadership(
    text: str,
) -> tuple[list[str], bool]:
    """Check text against LinkedIn-specific anti-thought-leadership patterns.

    Returns (matched_patterns, linkedin_no_thought_leadership) where:
    - matched_patterns: list of matched forbidden pattern strings (empty if clean)
    - linkedin_no_thought_leadership: True iff no pattern matched AND no \\bI\\b

    The matched_patterns list is appended to forbidden_terms_hit on the SocialDraft.
    """
    matched: list[str] = []
    for pat in _LINKEDIN_FORBIDDEN_PATTERNS:
        for m in pat.finditer(text):
            matched.append(m.group(0))

    no_first_person = _check_linkedin_no_first_person(text)
    if not no_first_person:
        matched.append("__linkedin_first_person__")

    linkedin_ok = len(matched) == 0
    return matched, linkedin_ok


class LinkedInDrafter(DrafterBase):
    """LinkedIn drafter subclass.

    Generates a single long-form LinkedIn post (≤ 3000 chars, target ≤ 1500)
    from a SocialTrigger and DomainResult.  Uses Anthropic prompt caching on
    the system prompt per ARCHITECTURE.md §6.2.

    Inherits the four T3 canonical validator checks (K=12 unchanged per CDA
    SME T4 §5.6 ruling) and adds:
    - Three LinkedIn-specific forbidden patterns (§5.5).
    - First-person pronoun rule: ``\\bI\\b`` forbidden (§5.5).
    - linkedin_no_thought_leadership framing_checks key (§5.5).

    Draft-only: Phase 7 has no live LinkedIn publishing per Mark's §7.1
    ratification.

    Parameters
    ----------
    anthropic_client:
        An Anthropic client instance (real or mock).  If None, the real
        ``anthropic.Anthropic`` client is constructed from the
        ``ANTHROPIC_API_KEY`` environment variable.
    model_id:
        The Claude model to use for drafting.  Defaults to claude-sonnet-4-6.
    """

    platform: Platform = Platform.LINKEDIN
    drafter_version: str = "linkedin-v1"
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
        self._system_prompt = load_prompt("linkedin", self.prompt_version)

    # ─────────────────────────────────────────────────────────────────────────
    # DrafterBase abstract implementations
    # ─────────────────────────────────────────────────────────────────────────

    def _get_length_limit(self) -> int:
        return _LINKEDIN_CHAR_HARD_LIMIT

    def _suggested_posting_time(self) -> datetime:
        """Next Tuesday or Wednesday 12:00 UTC — LinkedIn engagement peak."""
        now = datetime.now(UTC)
        candidate = now.replace(hour=12, minute=0, second=0, microsecond=0)
        if candidate <= now:
            candidate += timedelta(days=1)
        # Tuesday=1, Wednesday=2 are the LinkedIn engagement peak days.
        # Advance to the next Tue or Wed.
        while candidate.weekday() not in (1, 2):
            candidate += timedelta(days=1)
        return candidate

    def _build_methodology_url(self, domain_slug: str | None) -> str:
        if domain_slug:
            return f"{_ARTICLE_SHELL_BASE}/{domain_slug}"
        return _ARTICLE_SHELL_BASE

    def _build_dashboard_url(self, domain_slug: str | None) -> str:
        return self._build_methodology_url(domain_slug)

    # ─────────────────────────────────────────────────────────────────────────
    # Override draft() for LinkedIn-specific validator extensions (T4 §5.5)
    # ─────────────────────────────────────────────────────────────────────────

    def draft(
        self,
        trigger: SocialTrigger,
        domain_result: DomainResult,
    ) -> SocialDraft:
        """Generate and validate a LinkedIn post.

        Overrides DrafterBase.draft() to add LinkedIn-specific validator
        extensions after the inherited four T3 checks.  Steps:

        1. Call _draft_text() to get raw text.
        2. _check_length() — 3000-char hard limit (inherited via _get_length_limit).
        3. validate_draft() — four canonical T3 checks (K=12 unchanged).
        4. _validate_linkedin_anti_thought_leadership() — LinkedIn-specific
           forbidden patterns + first-person pronoun rule.
        5. Merge linkedin_no_thought_leadership into framing_checks.
        6. Construct SocialDraft or raise DrafterRejectedException.
        """
        raw_text = self._draft_text(trigger, domain_result)

        # Step 2: length check (3000-char hard limit, sentinel __linkedin_overlength_3000__)
        if len(raw_text) > _LINKEDIN_CHAR_HARD_LIMIT:
            raise DrafterRejectedException(
                f"LinkedIn post exceeds {_LINKEDIN_CHAR_HARD_LIMIT}-char limit "
                f"({len(raw_text)} chars)",
                draft_text=raw_text,
                forbidden_terms_hit=["__linkedin_overlength_3000__"],
            )

        # Step 3: four T3 canonical checks (K=12 unchanged per CDA SME T4 §5.6)
        forbidden_hits, framing_checks = validate_draft(raw_text)

        # Step 4: LinkedIn-specific anti-thought-leadership check
        li_forbidden, linkedin_ok = _validate_linkedin_anti_thought_leadership(raw_text)

        # Merge LinkedIn-specific forbidden hits into the combined list
        all_forbidden = forbidden_hits + li_forbidden

        # Step 5: add linkedin_no_thought_leadership key to framing_checks
        framing_checks["linkedin_no_thought_leadership"] = linkedin_ok

        # Collect rejection reasons
        rejection_reasons: list[str] = []
        bare_numerics: list[str] = []
        hyp_hits: list[str] = []

        if all_forbidden:
            rejection_reasons.append(f"forbidden vocab: {all_forbidden}")

        if not framing_checks.get("bare_numeric_without_ci", True):
            from cdb_social.drafters.base import validate_draft_numeric_ci_adjacency
            _, bare_numerics = validate_draft_numeric_ci_adjacency(raw_text)
            rejection_reasons.append(f"bare numerics without CI: {bare_numerics}")

        if not framing_checks.get("hypothesis_framing", True):
            from cdb_social.drafters.base import validate_draft_hypothesis_framing
            hyp_hits = validate_draft_hypothesis_framing(raw_text)
            rejection_reasons.append(f"hypothesis framing: {hyp_hits}")

        if not framing_checks.get("linkedin_no_thought_leadership", True):
            rejection_reasons.append(f"thought-leadership patterns: {li_forbidden}")

        framing_check_passed = (
            not all_forbidden and all(framing_checks.values())
        )

        if not framing_check_passed:
            exc = DrafterRejectedException(
                f"LinkedIn draft rejected: {'; '.join(rejection_reasons)}",
                draft_text=raw_text,
                forbidden_terms_hit=all_forbidden,
                hypothesis_patterns_hit=hyp_hits,
                bare_numerics=bare_numerics,
            )
            self._log_rejection(trigger, exc)
            raise exc

        # Audit the successful draft
        self._log_audit_pass(trigger)

        domain_slug = trigger.domain_slug
        return SocialDraft(
            draft_id=self._build_draft_id(trigger),
            trigger=trigger,
            platform=self.platform,
            text=raw_text,
            suggested_posting_time=self._suggested_posting_time(),
            drafter_self_rating=0.5,  # fixed per CDA SME T3 §5.6
            methodology_url=self._build_methodology_url(domain_slug),
            dashboard_url=self._build_dashboard_url(domain_slug),
            forbidden_terms_hit=all_forbidden,
            framing_check_passed=framing_check_passed,
            framing_checks=framing_checks,
            drafter_version=self.drafter_version,
            prompt_version=self.prompt_version,
            created_at=datetime.now(UTC),
        )

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
        methodology copy per CDA SME T3 §5.10 (carry-forward).

        The per-call payload may include ``target_char_count`` as a structural
        hint (not methodology copy) per CDA SME T4 §5.12.
        """
        user_payload = self._build_user_payload(trigger, domain_result)

        response = self._client.messages.create(
            model=self._model_id,
            max_tokens=2048,  # LinkedIn posts can be up to 3000 chars; 2048 is generous
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
        """Construct the data-only per-call payload (CDA SME T3 §5.10 carry-forward).

        Contains ONLY:
        - trigger_type and trigger evidence dict
        - domain_result numeric findings with CIs
        - methodology_url and dashboard_url
        - model_id and domain_slug
        - target_char_count: structural hint (allowed exception per T4 §5.12)

        NO methodology copy. No lede patterns. No framing instructions.
        Those live exclusively in the cached system prompt.
        """
        domain_slug = trigger.domain_slug
        model_id = trigger.model_id

        numerics = self._extract_numerics(domain_result)

        payload: dict[str, Any] = {
            "trigger_type": trigger.trigger_type.value,
            "domain_slug": domain_slug,
            "model_id": model_id,
            "trigger_evidence": trigger.evidence,
            "domain_numerics": numerics,
            "methodology_url": self._build_methodology_url(domain_slug),
            "dashboard_url": self._build_dashboard_url(domain_slug),
            "target_char_count": 1500,  # structural hint per CDA SME T4 §5.12
        }

        return (
            "Generate a LinkedIn post for the following LSB trigger event.\n\n"
            f"DATA:\n{json.dumps(payload, indent=2, ensure_ascii=False)}"
        )

    def _extract_numerics(self, domain_result: DomainResult) -> dict[str, Any]:
        """Extract relevant numerics from DomainResult for the per-call payload."""
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

        if domain_result.within_model_results:
            oci_per_model: dict[str, Any] = {}
            for wmr in domain_result.within_model_results:
                entry: dict[str, Any] = {"oci": wmr.oci}
                if wmr.oci_ci:
                    entry["oci_ci"] = list(wmr.oci_ci)
                oci_per_model[wmr.model_id] = entry
            numerics["oci_per_model"] = oci_per_model

        if domain_result.similarity_matrix:
            n = len(domain_result.similarity_matrix)
            max_gap = 0.0
            for i in range(n):
                for j in range(i + 1, n):
                    val = domain_result.similarity_matrix[i][j]
                    if val > max_gap:
                        max_gap = val
            numerics["max_pairwise_similarity_gap"] = round(max_gap, 4)

        return numerics
