"""X (Twitter) drafter — Phase 7 T4.

Subclass of DrafterBase that calls Anthropic (Claude) to generate an X thread
from a SocialTrigger + DomainResult.  Thread output is ``\\n---\\n``-delimited
with up to 3 segments.

Key design decisions (per CDA SME T4 §5.1–§5.9):
- System prompt loaded from prompts/v1/x.md and cached via
  ``cache_control={"type": "ephemeral"}`` per ARCHITECTURE.md §6.2.
- Per-call payload is data-only (trigger evidence + domain numerics + URLs).
  NO methodology copy in the per-call payload (T3 §5.10 carry-forward).
  Exception: ``n_segments_target`` structural hint per CDA SME T4 §5.12.
- ``drafter_self_rating = 0.5`` fixed; LLM is NOT prompted to self-rate (T3 §5.6).
- Per-segment validation (Option A per CDA SME T4 §5.2): each segment
  independently passes all four T3 canonical checks.  Cross-segment R10
  parking is rejected.
- Hook-tweet (segment 0) additional checks (CDA SME T4 §5.3):
    - x_hook_has_measurement_noun: segment 0 must name a measurement noun.
    - x_hook_has_ci_shape: segment 0 must carry a CI-shape inline.
    - x_hook_no_intent_attribution: decides/chooses/prefers forbidden in segment 0.
- Thread cap: 3 segments max, 280-char hard limit per segment, 250-char target.
- Draft-only in Phase 7: no live X publishing (X API requires paid tier).

The X-specific additional framing_checks keys:
    ``x_hook_has_measurement_noun``   — segment 0 contains a measurement noun
    ``x_hook_has_ci_shape``           — segment 0 carries an inline CI
    ``x_hook_no_intent_attribution``  — segment 0 has no decides/chooses/prefers
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
    CI_SHAPE_REGEX,
    DrafterBase,
    DrafterRejectedException,
    load_prompt,
    validate_draft,
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# X thread structural constants (CDA SME T4 §5.7)
# ─────────────────────────────────────────────────────────────────────────────

_X_SEGMENT_DELIMITER: str = "\n---\n"
_X_MAX_SEGMENTS: int = 3
_X_CHAR_HARD_LIMIT: int = 280
_X_CHAR_TARGET: int = 250

# Default article-shell base URL (until Phase 6 T1+T2 land methodology page).
_ARTICLE_SHELL_BASE = "https://cogstructurelab.com"

# ─────────────────────────────────────────────────────────────────────────────
# Hook-tweet validation patterns (CDA SME T4 §5.3)
# ─────────────────────────────────────────────────────────────────────────────

# Measurement-noun presence check: segment 0 must contain at least one of
# the canonical LSB measurement nouns (CDA SME T4 §5.3 check 1).
_X_HOOK_MEASUREMENT_NOUNS = re.compile(
    r"\b(?:Smith['']?s\s+S|OCI|eigenratio|consensus|"
    r"categorical\s+(?:structure|divergence)|"
    r"pile[-\s]?sort|free[-\s]?list|corpus\s+lens)\b",
    re.IGNORECASE,
)

# Intent-attribution forbidden stems for hook tweet only (CDA SME T4 §5.3 check 3).
# "decides", "chooses", "prefers" are forbidden in segment 0 only; segments 1+
# are subject only to the standard per-segment validator.
_X_SEGMENT_1_FORBIDDEN_STEMS: list[re.Pattern[str]] = [
    re.compile(r"\bdecides\b", re.IGNORECASE),
    re.compile(r"\bchooses\b", re.IGNORECASE),
    re.compile(r"\bprefers\b", re.IGNORECASE),
]


def _validate_x_hook_tweet(segment_0_text: str) -> dict[str, bool]:
    """Run hook-tweet structural checks on segment 0 (CDA SME T4 §5.3).

    Returns a dict of three X-specific framing_checks keys:
        ``x_hook_has_measurement_noun``   — True if segment 0 has a measurement noun
        ``x_hook_has_ci_shape``           — True if segment 0 has a CI-shape
        ``x_hook_no_intent_attribution``  — True if segment 0 has no intent stems

    Raises ``DrafterRejectedException`` with the appropriate sentinel on failure.
    These checks run BEFORE the per-segment ``validate_draft()`` loop.
    """
    hook_checks: dict[str, bool] = {}

    # Check 1: measurement-noun presence
    has_noun = bool(_X_HOOK_MEASUREMENT_NOUNS.search(segment_0_text))
    hook_checks["x_hook_has_measurement_noun"] = has_noun
    if not has_noun:
        raise DrafterRejectedException(
            "Hook tweet (segment 0) missing measurement noun",
            draft_text=segment_0_text,
            forbidden_terms_hit=["__x_segment_1_no_measurement_noun__"],
        )

    # Check 2: CI-shape presence (even though per-segment R10 also catches this,
    # the hook-tweet rule restates it as a positive structural constraint).
    has_ci = bool(CI_SHAPE_REGEX.search(segment_0_text))
    hook_checks["x_hook_has_ci_shape"] = has_ci
    if not has_ci:
        raise DrafterRejectedException(
            "Hook tweet (segment 0) missing inline CI-shape",
            draft_text=segment_0_text,
            forbidden_terms_hit=["__x_segment_1_no_ci_shape__"],
        )

    # Check 3: intent-attribution forbidden stems (hook-only)
    for pat in _X_SEGMENT_1_FORBIDDEN_STEMS:
        m = pat.search(segment_0_text)
        if m:
            stem = m.group(0).lower()
            raise DrafterRejectedException(
                f"Hook tweet (segment 0) contains intent-attribution stem: {stem!r}",
                draft_text=segment_0_text,
                forbidden_terms_hit=[f"__x_segment_1_intent_attribution_{stem}__"],
            )
    hook_checks["x_hook_no_intent_attribution"] = True

    return hook_checks


def _check_x_thread_structure(text: str) -> list[str]:
    """Structural pre-validation: thread cap + per-segment length (CDA SME T4 §5.7).

    Splits the raw text on ``\\n---\\n``, enforces:
    - At most 3 segments (raises with ``__x_thread_too_long__`` if exceeded).
    - Each segment ≤ 280 chars (raises with ``__x_segment_overlength_{idx}__``).

    Returns the list of segments on success.
    Raises ``DrafterRejectedException`` on any structural violation.
    """
    segments = text.split(_X_SEGMENT_DELIMITER)

    if len(segments) > _X_MAX_SEGMENTS:
        raise DrafterRejectedException(
            f"X thread has {len(segments)} segments; max is {_X_MAX_SEGMENTS}",
            draft_text=text,
            forbidden_terms_hit=["__x_thread_too_long__"],
        )

    for idx, seg in enumerate(segments):
        if len(seg) > _X_CHAR_HARD_LIMIT:
            raise DrafterRejectedException(
                f"X thread segment {idx} exceeds {_X_CHAR_HARD_LIMIT} chars "
                f"({len(seg)} chars)",
                draft_text=text,
                forbidden_terms_hit=[f"__x_segment_overlength_{idx}__"],
            )

    return segments


class XDrafter(DrafterBase):
    """X (Twitter) drafter subclass.

    Generates a thread (up to 3 segments joined by ``\\n---\\n``) from a
    SocialTrigger and DomainResult.  Uses Anthropic prompt caching on the
    system prompt per ARCHITECTURE.md §6.2.

    Per CDA SME T4 §5.2: per-segment validation (Option A) — each segment
    independently passes all four T3 canonical checks.  Any segment failure
    rejects the whole thread.

    Per CDA SME T4 §5.3: hook-tweet (segment 0) has three additional checks
    (measurement noun, CI-shape inline, no intent-attribution stems).

    Draft-only: Phase 7 has no live X API publishing per Mark's §7.1
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

    platform: Platform = Platform.X
    drafter_version: str = "x-v1"
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
        self._system_prompt = load_prompt("x", self.prompt_version)

    # ─────────────────────────────────────────────────────────────────────────
    # DrafterBase abstract implementations
    # ─────────────────────────────────────────────────────────────────────────

    def _get_length_limit(self) -> int:
        # X enforces per-segment limit; override draft() instead.
        # Returning a very large number disables the base class check
        # (the X drafter's per-segment validation in draft() handles it).
        return 999_999

    def _suggested_posting_time(self) -> datetime:
        """Next weekday 15:00 UTC — X algorithm (prime-time US east coast)."""
        now = datetime.now(UTC)
        candidate = now.replace(hour=15, minute=0, second=0, microsecond=0)
        if candidate <= now:
            candidate += timedelta(days=1)
        while candidate.weekday() >= 5:
            candidate += timedelta(days=1)
        return candidate

    def _build_methodology_url(self, domain_slug: str | None) -> str:
        if domain_slug:
            return f"{_ARTICLE_SHELL_BASE}/{domain_slug}"
        return _ARTICLE_SHELL_BASE

    def _build_dashboard_url(self, domain_slug: str | None) -> str:
        return self._build_methodology_url(domain_slug)

    # ─────────────────────────────────────────────────────────────────────────
    # Override draft() for per-segment validation (CDA SME T4 §5.2)
    # ─────────────────────────────────────────────────────────────────────────

    def draft(
        self,
        trigger: SocialTrigger,
        domain_result: DomainResult,
    ) -> SocialDraft:
        """Generate and validate an X thread.

        Overrides DrafterBase.draft() to implement per-segment validation per
        CDA SME T4 §5.2 (Option A).  Steps:

        1. Call _draft_text() to get raw thread text.
        2. _check_x_thread_structure() — thread cap + per-segment length.
        3. _validate_x_hook_tweet(segments[0]) — hook-tweet additional checks.
        4. For each segment: validate_draft(segment) — all four T3 checks.
        5. Aggregate forbidden_terms_hit (de-duplicated) and framing_checks
           (AND across all segments + hook-tweet keys).
        6. Construct SocialDraft or raise DrafterRejectedException.
        """
        raw_text = self._draft_text(trigger, domain_result)

        # Step 2: thread structure check (cap + per-segment length)
        segments = _check_x_thread_structure(raw_text)

        # Step 3: hook-tweet additional checks (runs BEFORE per-segment loop)
        hook_checks = _validate_x_hook_tweet(segments[0])

        # Step 4: per-segment validation (Option A — each segment independently)
        all_forbidden: list[str] = []
        # Start with all-True for aggregated framing_checks (AND across segments)
        # Four canonical T3 keys — aggregated via AND across all segments.
        aggregated_framing: dict[str, bool] = {
            "hypothesis_framing": True,
            "cognition_attribution": True,
            "bare_numeric_without_ci": True,
            "register_boundary": True,
        }

        for seg_idx, segment in enumerate(segments):
            seg_forbidden, seg_framing = validate_draft(segment)

            if seg_forbidden:
                raise DrafterRejectedException(
                    f"X thread segment {seg_idx} contains forbidden vocab: "
                    f"{seg_forbidden}",
                    draft_text=raw_text,
                    forbidden_terms_hit=seg_forbidden,
                )

            # Aggregate framing_checks via AND per CDA SME T4 §5.2 step 7
            for key in aggregated_framing:
                aggregated_framing[key] = aggregated_framing[key] and seg_framing.get(
                    key, True
                )

            if not all(seg_framing.values()):
                raise DrafterRejectedException(
                    f"X thread segment {seg_idx} failed framing check: "
                    f"{seg_framing}",
                    draft_text=raw_text,
                    forbidden_terms_hit=all_forbidden,
                )

            all_forbidden.extend(seg_forbidden)

        # De-duplicate forbidden hits across segments
        all_forbidden = list(dict.fromkeys(all_forbidden))

        # Step 5: merge hook_checks (X-specific) into aggregated framing_checks
        aggregated_framing.update(hook_checks)

        # framing_check_passed: all four canonical keys True AND no forbidden
        framing_check_passed = (
            not all_forbidden and all(aggregated_framing.values())
        )

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
            framing_checks=aggregated_framing,
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

        The per-call payload may include ``n_segments_target`` as a structural
        hint (not methodology copy) per CDA SME T4 §5.12.
        """
        user_payload = self._build_user_payload(trigger, domain_result)

        response = self._client.messages.create(
            model=self._model_id,
            max_tokens=1024,  # threads can be ~3 × 280 chars; 1024 is generous
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
        - n_segments_target: structural hint (allowed exception per T4 §5.12)

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
            "n_segments_target": 3,  # structural hint per CDA SME T4 §5.12
        }

        return (
            "Generate an X thread for the following LSB trigger event.\n\n"
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
