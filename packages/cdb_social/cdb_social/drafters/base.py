"""Drafter framework base class and post-generation validator.

The validator is the gate per Phase 7 kickoff §8 risk 1.  Any draft that fails
the post-generation validator is never written to the queue; the drafter raises
``DrafterRejectedException`` instead.

Three sub-checks per CDA SME §5.1–§5.3:

1. **§5.1 Forbidden-vocab scan** — full §1.5.4 phrase table + three word-stem
   matches (``worldview``, ``believes``, ``thinks``) with ``\\b`` anchoring.
   Case-insensitive.

2. **§5.2 Numeric+CI adjacency** — K=12 token window; four canonical CI-shape
   patterns; five exemption categories (version strings, ISO dates, model
   identifiers, post counts, trivial integers in count context).

3. **§5.3 Hypothesis-framing scan** — closed list of 14 phrases.

The ``framing_checks`` dict carries four binding keys per §5.11 / §5.18:
- ``no_cognition_attribution``  — from §5.1 word-stem scan
- ``no_value_attribution``      — from §5.1 phrase scan
- ``no_hypothesis_framing``     — from §5.3
- ``numeric_has_adjacent_ci``   — from §5.2

``framing_check_passed`` is the AND of all values.

Prompt versioning: ``load_prompt(platform, version)`` is explicit — the
version string is passed in, not auto-discovered, so test fixtures stay stable.
"""

from __future__ import annotations

import logging
import os
import re
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cdb_core.schemas import DomainResult, Platform, SocialDraft, SocialTrigger

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# §5.1 — Forbidden-vocab patterns
# ─────────────────────────────────────────────────────────────────────────────

# Phrase-level patterns: §1.5.4 left-column rows 1–10 + register-boundary rows.
# "Model X" placeholder rendered as [Mm]odel \S+ per CDA SME §2.1 ruling.
_FORBIDDEN_PHRASE_PATTERNS: list[re.Pattern[str]] = [
    # Row 1: "Model X believes..."
    re.compile(r"\b[Mm]odel \S+ believes\b", re.IGNORECASE),
    re.compile(r"\bmodels? believe\b", re.IGNORECASE),
    # Row 2: "Model X thinks of family as..."
    re.compile(r"\b[Mm]odel \S+ thinks of\b", re.IGNORECASE),
    re.compile(r"\bmodels? think of\b", re.IGNORECASE),
    # Row 3: "How models see the world"
    re.compile(r"\bhow models? sees? the world\b", re.IGNORECASE),
    # Row 4: "Model X's worldview"
    re.compile(r"\b[Mm]odel \S+'s worldview\b", re.IGNORECASE),
    re.compile(r"\bmodels?'? worldview\b", re.IGNORECASE),
    # Row 5: "Cultural bias" (standalone)
    re.compile(r"\bcultural bias\b", re.IGNORECASE),
    # Row 6: "What the model understands"
    re.compile(r"\bwhat the model understands\b", re.IGNORECASE),
    # Rows 7–10: Register-boundary phrases
    re.compile(r"\bwithin-model consensus\b", re.IGNORECASE),
    re.compile(r"\bwithin-model cultural consensus\b", re.IGNORECASE),
    re.compile(r"\bwithin-model eigenratio\b", re.IGNORECASE),
    re.compile(r"\bwithin-model CCM\b", re.IGNORECASE),
]

# Stem-level patterns: the three generic forbidden tokens with word-boundary
# anchoring per §2.1 ruling.  "disbelieves" does NOT match "believes".
_FORBIDDEN_STEM_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bworldview\b", re.IGNORECASE),
    re.compile(r"\bbelieves\b", re.IGNORECASE),
    re.compile(r"\bthinks\b", re.IGNORECASE),
]

# ─────────────────────────────────────────────────────────────────────────────
# §5.2 — Numeric+CI adjacency
# ─────────────────────────────────────────────────────────────────────────────

# Four canonical CI-shape patterns per CDA SME §2.2.
CI_SHAPE_REGEX = re.compile(
    r"(?:"
    # Pattern (a): (95% CI [a, b]) or (95% CI [a-b]) — square or round brackets
    r"\(?\s*95\s*%?\s*CI\s*[\[\(:]?\s*[-+]?\d*\.?\d+\s*[,–\-]\s*[-+]?\d*\.?\d+\s*[\]\)]?\s*\)?"
    r"|"
    # Pattern (b): CI: a–b or CI: a, b
    r"\bCI\s*[:=]\s*[-+]?\d*\.?\d+\s*[,–\-]\s*[-+]?\d*\.?\d+"
    r"|"
    # Pattern (c): ±X — symmetric error
    r"±\s*[-+]?\d*\.?\d+"
    r"|"
    # Pattern (d): (a, b) or (a–b) — paren-bracketed pair
    r"\(\s*[-+]?\d*\.?\d+\s*[,–\-]\s*[-+]?\d*\.?\d+\s*\)"
    r")",
    re.IGNORECASE,
)

# Numeric token extraction: optional sign, optional integer part, optional
# decimal, optional percent or scientific-notation suffix.
_NUMERIC_TOKEN_RE = re.compile(r"[-+]?\d*\.?\d+(?:%|e[-+]?\d+)?")

# K=12 token window for adjacency check.
_K_TOKENS: int = 12

# Five exemption categories per CDA SME §2.2.
# (d) — URLs are stripped before numeric scan (handled in code).
_NUMERIC_EXEMPTIONS: list[re.Pattern[str]] = [
    # (a) Model version strings: GPT-4, Claude 3.5, Llama-3.1, etc.
    re.compile(
        r"\b(?:GPT|Claude|Llama|Gemini|grok|Mistral|Qwen|DeepSeek|Phi)-?\d+(?:\.\d+)*\b",
        re.IGNORECASE,
    ),
    # (b) Year tokens: 1900–2099 standalone
    re.compile(r"\b(?:19|20)\d{2}\b"),
    # (c) Character-count metadata: "300 chars", "280 characters"
    re.compile(r"\b\d+\s*(?:chars?|characters?)\b", re.IGNORECASE),
    # (e) Count-of-N context: "across 12 models", "over 8 domains", etc.
    re.compile(
        r"\b(?:across|over|in)\s+\d+\s+(?:models?|domains?|runs?|prompts?|informants?)\b",
        re.IGNORECASE,
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
# §5.3 — Hypothesis-framing patterns (closed list of 14 phrases)
# ─────────────────────────────────────────────────────────────────────────────

_HYPOTHESIS_FRAMING_PATTERNS: list[re.Pattern[str]] = [
    # §1.5.4 row 11 verbatim
    re.compile(r"\bLSB hypothesi[zs]ed\b", re.IGNORECASE),
    re.compile(r"\bLSB tested whether\b", re.IGNORECASE),
    re.compile(r"\bLSB confirms? that\b", re.IGNORECASE),
    re.compile(r"\bLSB found that\b", re.IGNORECASE),
    re.compile(r"\bLSB predicted\b", re.IGNORECASE),
    # §1.5.4 row 12 verbatim
    re.compile(r"\bdata confirmed\b", re.IGNORECASE),
    re.compile(r"\bdata refuted\b", re.IGNORECASE),
    # Three "subtler patterns" per Orchestrator §3 question 3
    re.compile(r"\bour results show\b", re.IGNORECASE),
    re.compile(r"\bthis demonstrates\b", re.IGNORECASE),
    re.compile(r"\bthis means\b", re.IGNORECASE),
    # §1.5.7 explicit forbidden frames
    re.compile(r"\bthis proves\b", re.IGNORECASE),
    re.compile(r"\bwe hypothesi[zs]ed\b", re.IGNORECASE),
    re.compile(r"\bconfirms that\b", re.IGNORECASE),
    re.compile(r"\bproves that\b", re.IGNORECASE),
]


# ─────────────────────────────────────────────────────────────────────────────
# Exception
# ─────────────────────────────────────────────────────────────────────────────


class DrafterRejectedException(Exception):
    """Raised when a draft fails the post-generation validator.

    The exception carries a human-readable message and two structured fields
    so the caller (audit log, orchestrator) can record structured rejection
    detail without parsing the message string.

    Attributes
    ----------
    draft_text:
        The full raw text that was rejected.
    forbidden_terms_hit:
        List of matched forbidden patterns from the §5.1 scan (may be empty
        if rejection was from §5.2 or §5.3 instead).
    hypothesis_patterns_hit:
        List of matched hypothesis-framing patterns from the §5.3 scan.
    bare_numerics:
        List of numeric tokens that lacked an adjacent CI-shape neighbor.
    """

    def __init__(
        self,
        message: str,
        *,
        draft_text: str = "",
        forbidden_terms_hit: list[str] | None = None,
        hypothesis_patterns_hit: list[str] | None = None,
        bare_numerics: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.draft_text = draft_text
        self.forbidden_terms_hit: list[str] = forbidden_terms_hit or []
        self.hypothesis_patterns_hit: list[str] = hypothesis_patterns_hit or []
        self.bare_numerics: list[str] = bare_numerics or []


# ─────────────────────────────────────────────────────────────────────────────
# Validator sub-functions
# ─────────────────────────────────────────────────────────────────────────────


def validate_draft_forbidden_vocab(text: str) -> list[str]:
    """§5.1 — Scan text for §1.5.4 forbidden phrases and stems.

    Returns a list of matched substrings (empty if the text is clean).
    Case-insensitive.  Word-boundary anchors on stems prevent "disbelieves"
    from matching "believes".

    The returned list is assigned to ``SocialDraft.forbidden_terms_hit``.
    """
    hits: list[str] = []
    for pat in _FORBIDDEN_PHRASE_PATTERNS:
        for m in pat.finditer(text):
            hits.append(m.group(0))
    for pat in _FORBIDDEN_STEM_PATTERNS:
        for m in pat.finditer(text):
            hits.append(m.group(0))
    return hits


def validate_draft_numeric_ci_adjacency(text: str) -> tuple[bool, list[str]]:
    """§5.2 — Check that every non-exempt numeric has an adjacent CI-shape.

    Returns ``(passed, bare_numerics)`` where ``bare_numerics`` is the list
    of numeric tokens that lacked a CI-shape neighbor within K=12 tokens.

    Algorithm:
    1. Strip URLs.
    2. Mark exempt spans (model versions, years, character counts, count-of-N).
    3. Tokenise (whitespace-split, punctuation-stripped for window purposes).
    4. For each non-exempt numeric token, scan ± K tokens for CI_SHAPE_REGEX.
    5. Return True iff every non-exempt numeric has an adjacent CI neighbour.
    """
    # Step 1: strip URLs
    stripped = re.sub(r"https?://\S+", " ", text)

    # Step 2: mark exempt spans by collecting (start, end) intervals
    exempt_spans: list[tuple[int, int]] = []
    for pat in _NUMERIC_EXEMPTIONS:
        for m in pat.finditer(stripped):
            exempt_spans.append((m.start(), m.end()))

    # Step 3: tokenise for window purposes.
    # We need two parallel views: (a) the raw text for regex matching,
    # (b) a token list (whitespace-split) for the ± K window.
    tokens = stripped.split()
    # Build a list of (token_index, char_start_in_stripped) for each token.
    token_positions: list[tuple[int, int]] = []
    pos = 0
    for i, tok in enumerate(tokens):
        idx = stripped.find(tok, pos)
        token_positions.append((i, idx))
        pos = idx + len(tok)

    # Step 4: for each numeric token, check CI adjacency.
    bare: list[str] = []
    for i, tok in enumerate(tokens):
        # Does this token contain a numeric?
        if not _NUMERIC_TOKEN_RE.search(tok):
            continue
        tok_char_start = token_positions[i][1]
        tok_char_end = tok_char_start + len(tok)
        # Is this numeric in an exempt span?
        if _is_exempt(tok_char_start, tok_char_end, exempt_spans):
            continue
        # Scan ± K tokens for a CI-shape match.
        window_start = max(0, i - _K_TOKENS)
        window_end = min(len(tokens), i + _K_TOKENS + 1)
        window_text = " ".join(tokens[window_start:window_end])
        if not CI_SHAPE_REGEX.search(window_text):
            bare.append(tok)

    return (len(bare) == 0), bare


def _is_exempt(start: int, end: int, exempt_spans: list[tuple[int, int]]) -> bool:
    """Return True if the span [start, end) overlaps any exempt span."""
    return any(start < ee and end > es for es, ee in exempt_spans)


def validate_draft_hypothesis_framing(text: str) -> list[str]:
    """§5.3 — Scan text for hypothesis-framing phrases (closed list of 14).

    Returns a list of matched patterns (empty if the text is clean).
    The list is closed at T3; new entries require a CDA SME re-review.
    """
    hits: list[str] = []
    for pat in _HYPOTHESIS_FRAMING_PATTERNS:
        for m in pat.finditer(text):
            hits.append(m.group(0))
    return hits


# ─────────────────────────────────────────────────────────────────────────────
# Public validate_draft facade
# ─────────────────────────────────────────────────────────────────────────────


def validate_draft(text: str) -> tuple[list[str], dict[str, bool]]:
    """Post-generation validator.  Returns (forbidden_terms_hit, framing_checks).

    The four framing_checks keys (§5.11 / §5.18):
    - ``no_cognition_attribution`` — True iff no forbidden stem matched
    - ``no_value_attribution``     — True iff no forbidden phrase matched
    - ``no_hypothesis_framing``    — True iff no hypothesis-framing phrase matched
    - ``numeric_has_adjacent_ci``  — True iff every non-exempt numeric has CI

    ``framing_checks`` values are True when the check PASSES.  The combined
    ``framing_check_passed`` flag is the AND of all values AND
    forbidden_terms_hit == [].
    """
    # §5.1 — forbidden vocab
    forbidden_hits = validate_draft_forbidden_vocab(text)
    # Separate phrase hits from stem hits for granular framing_checks.
    phrase_hits = [h for h in forbidden_hits if _is_phrase_hit(h)]
    stem_hits = [h for h in forbidden_hits if not _is_phrase_hit(h)]

    # §5.2 — numeric+CI adjacency
    ci_ok, bare_numerics = validate_draft_numeric_ci_adjacency(text)

    # §5.3 — hypothesis framing
    hyp_hits = validate_draft_hypothesis_framing(text)

    framing_checks: dict[str, bool] = {
        "no_cognition_attribution": len(stem_hits) == 0,
        "no_value_attribution": len(phrase_hits) == 0,
        "no_hypothesis_framing": len(hyp_hits) == 0,
        "numeric_has_adjacent_ci": ci_ok,
    }

    return forbidden_hits, framing_checks


def _is_phrase_hit(hit: str) -> bool:
    """Return True if the match came from a phrase-level pattern (§5.1)."""
    # Phrase patterns contain spaces or hyphens; stem-level hits are single words.
    return " " in hit or "-" in hit


# ─────────────────────────────────────────────────────────────────────────────
# Prompt loading
# ─────────────────────────────────────────────────────────────────────────────

_PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(platform: str, version: str) -> str:
    """Load the cached system prompt for the given platform and version.

    The version is explicit (not auto-discovered) so test fixtures stay stable.
    The file is at:
        cdb_social/drafters/prompts/{version}/{platform}.md

    Raises
    ------
    FileNotFoundError
        If the prompt file does not exist.
    """
    prompt_path = _PROMPTS_DIR / version / f"{platform}.md"
    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_path}.  "
            f"To add a new prompt version, create a new directory "
            f"cdb_social/drafters/prompts/v{{N}}/ per CLAUDE.md §6 rule 7."
        )
    return prompt_path.read_text(encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# DrafterBase abstract base class
# ─────────────────────────────────────────────────────────────────────────────


class DrafterBase(ABC):
    """Abstract base for platform-specific drafters.

    Contract: ``draft(trigger, domain_result)`` → ``SocialDraft``, or raises
    ``DrafterRejectedException`` if the post-generation validator rejects the
    output.  The base class does NOT call the LLM; subclasses implement
    ``_draft_text()``.  Every output runs through ``validate_draft()`` before
    being returned.

    Subclass responsibilities:
    - Set ``platform``, ``drafter_version``, ``prompt_version`` as class attrs.
    - Implement ``_draft_text(trigger, domain_result) -> str``.
    - Set ``drafter_self_rating`` (default 0.5 per CDA SME §5.6).
    - Implement ``_suggested_posting_time()`` for platform posting heuristics.
    - Implement ``_build_methodology_url(domain_slug)`` and
      ``_build_dashboard_url(domain_slug)`` for URL construction.
    """

    platform: Platform
    drafter_version: str
    prompt_version: str

    @abstractmethod
    def _draft_text(
        self,
        trigger: SocialTrigger,
        domain_result: DomainResult,
    ) -> str:
        """Generate the raw post text by calling the platform-specific LLM.

        Subclasses must call the LLM here and return the raw text.  No
        validation is performed inside this method; validation happens in the
        base class ``draft()`` after the text is returned.
        """
        ...

    @abstractmethod
    def _suggested_posting_time(self) -> datetime:
        """Return the platform-specific suggested posting time."""
        ...

    @abstractmethod
    def _build_methodology_url(self, domain_slug: str | None) -> str:
        """Return the methodology URL for the given domain slug."""
        ...

    @abstractmethod
    def _build_dashboard_url(self, domain_slug: str | None) -> str:
        """Return the dashboard URL for the given domain slug."""
        ...

    def _build_draft_id(
        self,
        trigger: SocialTrigger,
    ) -> str:
        """Construct the draft_id per T1 schema: SHA256[:16] of
        (trigger.dedupe_key + platform + drafter_version + prompt_version).
        """
        import hashlib
        raw = "|".join([
            trigger.dedupe_key,
            self.platform.value,
            self.drafter_version,
            self.prompt_version,
        ])
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def draft(
        self,
        trigger: SocialTrigger,
        domain_result: DomainResult,
    ) -> SocialDraft:
        """Generate and validate a draft.

        Steps:
        1. Call ``_draft_text()`` to get raw text from the subclass.
        2. Run ``validate_draft()`` — populates forbidden_terms_hit,
           framing_checks.
        3. If validator rejects, raise ``DrafterRejectedException`` with full
           context.
        4. Otherwise construct and return ``SocialDraft``.

        The draft never reaches the queue if any sub-check fails.
        """
        raw_text = self._draft_text(trigger, domain_result)

        # Platform length check (§5.7 / §5.12)
        self._check_length(raw_text)

        # §5.1–§5.3 validation
        forbidden_hits, framing_checks = validate_draft(raw_text)

        # Collect rejection reasons
        rejection_reasons: list[str] = []
        bare_numerics: list[str] = []
        hyp_hits: list[str] = []

        if forbidden_hits:
            rejection_reasons.append(
                f"forbidden vocab: {forbidden_hits}"
            )

        if not framing_checks.get("numeric_has_adjacent_ci", True):
            _, bare_numerics = validate_draft_numeric_ci_adjacency(raw_text)
            rejection_reasons.append(f"bare numerics without CI: {bare_numerics}")

        if not framing_checks.get("no_hypothesis_framing", True):
            hyp_hits = validate_draft_hypothesis_framing(raw_text)
            rejection_reasons.append(f"hypothesis framing: {hyp_hits}")

        framing_check_passed = (
            not forbidden_hits and all(framing_checks.values())
        )

        if not framing_check_passed:
            exc = DrafterRejectedException(
                f"Draft rejected: {'; '.join(rejection_reasons)}",
                draft_text=raw_text,
                forbidden_terms_hit=forbidden_hits,
                hypothesis_patterns_hit=hyp_hits,
                bare_numerics=bare_numerics,
            )
            self._log_rejection(trigger, exc)
            raise exc

        domain_slug = trigger.domain_slug
        return SocialDraft(
            draft_id=self._build_draft_id(trigger),
            trigger=trigger,
            platform=self.platform,
            text=raw_text,
            suggested_posting_time=self._suggested_posting_time(),
            drafter_self_rating=0.5,  # fixed per CDA SME §5.6
            methodology_url=self._build_methodology_url(domain_slug),
            dashboard_url=self._build_dashboard_url(domain_slug),
            forbidden_terms_hit=forbidden_hits,
            framing_check_passed=framing_check_passed,
            framing_checks=framing_checks,
            drafter_version=self.drafter_version,
            prompt_version=self.prompt_version,
            created_at=datetime.now(UTC),
        )

    def _check_length(self, text: str) -> None:
        """Raise DrafterRejectedException if text exceeds platform length limit.

        Subclasses override to set the per-platform limit.  Default limit: 300.
        The sentinel ``__overlength__`` is added to forbidden_terms_hit so the
        audit log records a structured rejection code.
        """
        limit = self._get_length_limit()
        if len(text) > limit:
            raise DrafterRejectedException(
                f"Draft exceeds {limit}-char limit ({len(text)} chars)",
                draft_text=text,
                forbidden_terms_hit=[f"__overlength_{limit}__"],
            )

    def _get_length_limit(self) -> int:
        """Return the platform character limit.  Subclasses override."""
        return 300

    def _log_rejection(
        self,
        trigger: SocialTrigger,
        exc: DrafterRejectedException,
    ) -> None:
        """Write a rejection record to the drafter audit log (§5.8).

        Appends one JSONL record to ``out/social/state/drafter_rejections.jsonl``.
        Failure to write the audit log is logged at WARNING level and does NOT
        suppress the original exception.
        """
        import json

        state_dir = Path(os.environ.get("LSB_SOCIAL_STATE_DIR", "out/social/state"))
        log_path = state_dir / "drafter_rejections.jsonl"

        record: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "trigger_id": trigger.dedupe_key,
            "platform": self.platform.value,
            "drafter_version": self.drafter_version,
            "prompt_version": self.prompt_version,
            "draft_text": exc.draft_text,
            "matched_forbidden": exc.forbidden_terms_hit,
            "matched_hypothesis": exc.hypothesis_patterns_hit,
            "bare_numerics": exc.bare_numerics,
        }

        try:
            state_dir.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            # §5.8 sliding-window check: warn if ≥ 2 rejections in last 10 records.
            _check_rejection_window(log_path)
        except OSError as e:
            logger.warning("Failed to write drafter rejection log: %s", e)


def _check_rejection_window(log_path: Path) -> None:
    """§5.8 — Sliding-window rejection monitor.

    Reads the last 10 records from the rejection log and logs a WARNING if
    there are ≥ 2 rejections.  Does NOT raise; does NOT suppress.  The
    warning is the operator's signal to consider a v2 prompt bump per §5.8.
    """
    try:
        lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        window = lines[-10:]
        n_rejections = len(window)
        if n_rejections >= 2:
            logger.warning(
                "DRAFTER_REJECTION_WINDOW: %d rejections in last 10 drafts; "
                "consider v2 prompt review per CDA SME §5.8",
                n_rejections,
            )
    except OSError:
        pass  # log file may not be readable; silently ignore
