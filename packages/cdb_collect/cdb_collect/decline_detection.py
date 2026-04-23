"""Deterministic refusal / decline detection for the Phase 4a.1 protocol.

Identifies sessions in informants.jsonl and failures.jsonl that warrant
a decline-interview follow-up call per docs/DECLINE_INTERVIEW_PROTOCOL.md
and the CDA SME verdict of 2026-04-23.

Rules are deterministic only — no LLM classifier. Future rule changes
require incrementing DECLINE_ALLOWLIST_VERSION and Architect sign-off.
See ARCHITECTURE.md CLAUDE.md §6 rule 12 for the no-LLM-in-analyze
constraint (which extends in spirit to detection logic here).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, cast

# ── Allowlist version constant (SME Note 1.3) ─────────────────────────────
# Bump this string whenever the allowlist or detection rules change.
# Reproducibility across Phase 4a.1 runs depends on frozen rule sets.
# New entries require Architect sign-off.
DECLINE_ALLOWLIST_VERSION: str = "v1"

# ── Allowlist (case-insensitive, word-boundary match) ─────────────────────
# Seed entries (design note §1.3) plus SME-added apology-framed RLHF
# patterns (CDA SME verdict 2026-04-23 §1.3).
DECLINE_ALLOWLIST: frozenset[str] = frozenset({
    # Bare refusal forms
    "I can't",
    "I cannot",
    "I'm not able",
    "I am unable",
    "I won't",
    "I decline",
    "I refuse",
    # SME-added apology-framed RLHF patterns (2026-04-23 verdict §1.3)
    "I'm sorry, but",
    "I apologize, but",
    "As an AI",
    "I'm not comfortable",
    "against my",
    "violates",
    "I must decline",
})

# ── Single-degenerate-pile threshold (SME Note 1.3 trigger (e)) ───────────
_DEGENERATE_PILE_THRESHOLD: float = 0.95


def _matches_allowlist(text: str) -> bool:
    """Return True if text contains any allowlist phrase (case-insensitive).

    Match is on the first occurrence of any phrase. Uses re.search with
    case-insensitive flag so the match is not restricted to word boundaries
    on phrases that already contain boundary punctuation (e.g., "I'm sorry,
    but"). For single-word phrases, the pattern anchors with \\b on each
    side to avoid false positives inside words.
    """
    text_ci = text  # re.IGNORECASE handles normalisation
    for phrase in DECLINE_ALLOWLIST:
        # Phrases containing spaces or punctuation are matched as literal
        # substrings (case-insensitive). Single-word phrases get word
        # boundaries to avoid false positives inside longer words.
        if " " in phrase or any(c in phrase for c in "',"):
            pattern = re.escape(phrase)
        else:
            pattern = r"\b" + re.escape(phrase) + r"\b"
        if re.search(pattern, text_ci, re.IGNORECASE):
            return True
    return False


@dataclass(frozen=True)
class DetectedSession:
    """A session identified as warranting a decline-interview follow-up.

    Attributes:
        identifier: The ``informant_id`` (for informants.jsonl entries)
            or a synthetic failure identifier derived from context fields
            (for failures.jsonl entries).
        originating_outcome_class: The detection trigger that fired.
            Maps to ``DeclineInterview.originating_outcome_class``.
        originating_step: Which CDA step the trigger fired on.
            Maps to ``DeclineInterview.originating_step``.
        source: Whether the session came from informants.jsonl or
            failures.jsonl.
    """

    identifier: str
    originating_outcome_class: Literal[
        "empty_output",
        "refusal_string_match",
        "single_degenerate_pile",
        "parse_failure",
        "http_error",
        "timeout",
        "other",
    ]
    originating_step: Literal["freelist", "pile_sort", "interview", "pre_session"]
    source: Literal["informants", "failures"]


def _failure_identifier(entry: dict) -> str:
    """Build a deterministic identifier for a failures.jsonl entry.

    Uses the context dict fields model_id + domain + run_index +
    timestamp, which together should uniquely identify a failure entry.
    """
    ctx = entry.get("context", {})
    return (
        f"failure|{ctx.get('model_id', 'unknown')}"
        f"|{ctx.get('domain', 'unknown')}"
        f"|{ctx.get('run_index', 'unknown')}"
        f"|{entry.get('timestamp', 'unknown')}"
    )


def _map_error_type_to_outcome_class(
    error_type: str,
) -> Literal["http_error", "timeout", "parse_failure", "other"]:
    """Map a Python exception class name to an originating_outcome_class."""
    et = error_type.lower()
    if "http" in et or "status" in et or "connect" in et:
        return "http_error"
    if "timeout" in et:
        return "timeout"
    if "parse" in et or "json" in et or "value" in et:
        return "parse_failure"
    return "other"


def _map_error_type_to_step(
    error_type: str, context: dict,
) -> Literal["freelist", "pile_sort", "interview", "pre_session"]:
    """Infer originating_step from the failure entry.

    Attempts to read a ``failed_step`` key from the context dict first
    (populated by PartialSessionError callers). Falls back to parsing
    the error_type string.
    """
    step = context.get("failed_step", "")
    if step in ("freelist", "pile_sort", "interview", "pre_session"):
        return cast(Literal["freelist", "pile_sort", "interview", "pre_session"], step)
    # Fallback: pile-sort parse error is common enough to name explicitly
    et = error_type.lower()
    if "pile" in et:
        return "pile_sort"
    return "pre_session"


def detect_from_informant(record: dict) -> DetectedSession | None:
    """Evaluate one informants.jsonl record for decline-interview triggers.

    Returns a DetectedSession if any trigger fires, else None.
    Detection runs after step-record write (SME Note 1.3 refinement 3).

    Triggers evaluated (OR-combined):
    (a) Pile-sort parsed_piles has 0 items.
    (b) Pile-sort response_verbatim matches the allowlist.
    (c) Free-list parsed_items has 0 items.
    (d) Interview parsed_pile_labels has 0 items AND response_verbatim
        non-empty (model produced text but structure was absent).
    (e) Single-degenerate-pile: len(parsed_piles) == 1 AND
        items_in_single_pile / total_freelist_items >= 0.95.
    """
    if not isinstance(record, dict):
        return None

    # Only fire on qa_passed=False records (per §1.3 trigger 2)
    if record.get("qa_passed", True):
        return None

    informant_id: str = record.get("informant_id", "unknown")
    pile_sort = record.get("pile_sort", {})
    freelist = record.get("freelist", {})
    interview = record.get("interview", {})

    parsed_piles: list = pile_sort.get("parsed_piles", [])
    pile_response: str = pile_sort.get("response_verbatim", "")
    parsed_items: list = freelist.get("parsed_items", [])
    parsed_labels: list = interview.get("parsed_pile_labels", [])
    interview_response: str = interview.get("response_verbatim", "")

    # Trigger (a): pile-sort produced 0 piles
    if len(parsed_piles) == 0:
        return DetectedSession(
            identifier=informant_id,
            originating_outcome_class="empty_output",
            originating_step="pile_sort",
            source="informants",
        )

    # Trigger (b): pile-sort response matches refusal allowlist
    if pile_response and _matches_allowlist(pile_response):
        return DetectedSession(
            identifier=informant_id,
            originating_outcome_class="refusal_string_match",
            originating_step="pile_sort",
            source="informants",
        )

    # Trigger (c): free-list produced 0 items
    if len(parsed_items) == 0:
        return DetectedSession(
            identifier=informant_id,
            originating_outcome_class="empty_output",
            originating_step="freelist",
            source="informants",
        )

    # Trigger (d): interview produced 0 labels AND had non-empty response
    if len(parsed_labels) == 0 and interview_response:
        return DetectedSession(
            identifier=informant_id,
            originating_outcome_class="empty_output",
            originating_step="interview",
            source="informants",
        )

    # Trigger (e): single-degenerate-pile
    if (
        len(parsed_piles) == 1
        and len(parsed_items) > 0
    ):
        items_in_pile = len(parsed_piles[0])
        ratio = items_in_pile / len(parsed_items)
        if ratio >= _DEGENERATE_PILE_THRESHOLD:
            return DetectedSession(
                identifier=informant_id,
                originating_outcome_class="single_degenerate_pile",
                originating_step="pile_sort",
                source="informants",
            )

    return None


def detect_from_failure(entry: dict) -> DetectedSession | None:
    """Evaluate one failures.jsonl entry for decline-interview trigger.

    All non-transient failure entries warrant a follow-up. Transient
    errors (rate-limit retries) are retried by the runner and never
    reach failures.jsonl — the invariant holds without extra filtering.

    Returns a DetectedSession for every valid failure entry.
    """
    if not isinstance(entry, dict):
        return None

    error_type: str = entry.get("error_type", "")
    context: dict = entry.get("context", {})
    identifier = _failure_identifier(entry)
    outcome_class = _map_error_type_to_outcome_class(error_type)
    step = _map_error_type_to_step(error_type, context)

    return DetectedSession(
        identifier=identifier,
        originating_outcome_class=outcome_class,
        originating_step=step,
        source="failures",
    )


def detect_all(
    informant_records: list[dict],
    failure_entries: list[dict],
) -> list[DetectedSession]:
    """Run both detection passes and return all sessions warranting follow-up.

    Args:
        informant_records: Parsed dicts from informants.jsonl.
        failure_entries: Parsed dicts from failures.jsonl.

    Returns:
        Ordered list of DetectedSession objects. Informant triggers first,
        then failure triggers.
    """
    results: list[DetectedSession] = []

    for rec in informant_records:
        detected = detect_from_informant(rec)
        if detected is not None:
            results.append(detected)

    for entry in failure_entries:
        detected = detect_from_failure(entry)
        if detected is not None:
            results.append(detected)

    return results
