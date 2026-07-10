"""Failure-signature table for the LSB ops console live board.

This module contains exactly five failure signatures derived from the batch A
campaign patterns. No entries beyond these five may be added without a new
Architect plan.

CDA SME review note (pitfall 13): log-source entries (auth_401,
billing_credit_balance, model_404, parse_after_retries) classify text in log
files written by the collect.py runner. Record-source entries (refusal_streak)
classify qa_passed=False records from informants.jsonl. The two source types
are kept strictly separate: no vocabulary is shared between log-source and
record-source classifiers, preventing the cross-boundary miscalibration
described in pitfall 13.

Log-source entries match against log text that records runner-layer failures
(HTTP errors, parse exceptions). The runner writes these lines before any
informant record is saved, so they cannot appear in qa_passed=False record
fields. Record-source entries read the stop_reason field of parsed
InformantRecord-derived dicts; that field is never present in raw log text.

This table is the sole location for these classifications. No scattered
regexes; no duplicated substring lists. The CDA SME reviews this file
before any PR touching it merges.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SignatureHit:
    """A single failure-signature match."""

    signature_id: str        # one of the five FAILURE_SIGNATURES ids
    label: str               # human-readable label from the table
    source: str              # "log" or "record"
    evidence: str            # the matching text or record key


@dataclass(frozen=True)
class FailureSignature:
    """One entry in the FAILURE_SIGNATURES table."""

    id: str
    label: str
    source: str              # "log" or "record"
    description: str         # self-documenting explanation for CDA SME review


# ---------------------------------------------------------------------------
# Log-source patterns
# (matched against raw text from per-model log files)
# ---------------------------------------------------------------------------

# Compiled once at import time.

# auth_401: HTTP 401 responses or explicit authentication error messages
# written by the adapter layer.
_AUTH_401_RE = re.compile(
    r"(?:401|AuthenticationError|authentication error|Unauthorized)",
    re.IGNORECASE,
)

# billing_credit_balance: provider billing / credit errors that appear in
# adapter exception messages or runner log lines.
_BILLING_RE = re.compile(
    r"(?:credit balance|insufficient credit|billing|payment required|402)",
    re.IGNORECASE,
)

# model_404: provider returns 404 or "model not found" for the requested
# model_id. Distinct from auth_401 (HTTP 401) by HTTP code and message text.
_MODEL_404_RE = re.compile(
    r"(?:404|model not found|model_not_found|No model|unknown model)",
    re.IGNORECASE,
)

# parse_after_retries: PileSortParseError raised after all retries are
# exhausted. This class name is written into the log by the runner's
# exception handler and is not present in any record field.
_PARSE_AFTER_RETRIES_RE = re.compile(
    r"PileSortParseError",
)


# ---------------------------------------------------------------------------
# Record-source check for refusal_streak
# ---------------------------------------------------------------------------

# Minimum consecutive refusals per (model_id, domain_slug, collection_date)
# that constitute a streak.
_REFUSAL_STREAK_MIN = 3

# stop_reason values that indicate a refusal. These are set by the runner's
# decline-detection logic and written to the freelist/pile_sort/interview
# stop_reason field. They do not appear in runner log text.
_REFUSAL_STOP_REASONS: frozenset[str] = frozenset(
    {"refusal", "decline", "content_filter", "safety_filter"}
)


def _check_refusal_streak(
    records_by_model_domain: dict[tuple[str, str], list[dict[str, Any]]],
) -> list[SignatureHit]:
    """Detect 3+ consecutive refusal stop_reasons per (model_id, domain_slug).

    Reads the freelist.stop_reason field from parsed record dicts. Groups by
    (model_id, domain_slug, collection_date) and counts consecutive refusals
    within each group. A streak of >= _REFUSAL_STREAK_MIN triggers a hit.

    This is a record-source check. The stop_reason vocabulary is isolated to
    this function and is never compared against log text.
    """
    hits: list[SignatureHit] = []

    for (model_id, domain_slug), recs in records_by_model_domain.items():
        # Count consecutive refusals within the group (order-preserving)
        streak = 0
        streak_hit = False
        for rec in recs:
            freelist = rec.get("freelist", {})
            if not isinstance(freelist, dict):
                streak = 0
                continue
            stop_reason: str = freelist.get("stop_reason", "")
            if stop_reason in _REFUSAL_STOP_REASONS:
                streak += 1
                if streak >= _REFUSAL_STREAK_MIN and not streak_hit:
                    hits.append(
                        SignatureHit(
                            signature_id="refusal_streak",
                            label=FAILURE_SIGNATURES[4].label,
                            source="record",
                            evidence=(
                                f"model={model_id} domain={domain_slug} "
                                f"streak={streak} stop_reason={stop_reason!r}"
                            ),
                        )
                    )
                    streak_hit = True
            else:
                streak = 0
                streak_hit = False

    return hits


# ---------------------------------------------------------------------------
# The table (five entries exactly; do not add entries without Architect plan)
# ---------------------------------------------------------------------------

FAILURE_SIGNATURES: list[FailureSignature] = [
    FailureSignature(
        id="auth_401",
        label="Authentication failure (401)",
        source="log",
        description=(
            "Provider returned HTTP 401 or an AuthenticationError. Indicates an "
            "invalid or expired API key. Log-source only; matched against runner "
            "exception messages written before any record is saved."
        ),
    ),
    FailureSignature(
        id="billing_credit_balance",
        label="Billing / credit balance error",
        source="log",
        description=(
            "Provider rejected the request due to insufficient credits or a billing "
            "error (HTTP 402 or credit-balance message). Log-source only."
        ),
    ),
    FailureSignature(
        id="model_404",
        label="Model not found (404)",
        source="log",
        description=(
            "Provider returned HTTP 404 or 'model not found' for the requested "
            "model_id. Indicates the model alias has been retired or mis-specified. "
            "Log-source only; distinguished from auth_401 by HTTP code."
        ),
    ),
    FailureSignature(
        id="parse_after_retries",
        label="PileSortParseError after retries",
        source="log",
        description=(
            "PileSortParseError raised after all pile-sort retries were exhausted. "
            "The class name is written to the log by the runner exception handler; "
            "it does not appear in any record field. Log-source only."
        ),
    ),
    FailureSignature(
        id="refusal_streak",
        label="Refusal streak (3+ consecutive)",
        source="record",
        description=(
            "Three or more consecutive qa_passed=False records for the same "
            "(model_id, domain_slug) group share a refusal-class stop_reason in "
            "freelist.stop_reason. Record-source only; uses stop_reason vocabulary "
            "set by the runner's decline-detection logic, never present in log text."
        ),
    ),
]

# Sanity check: exactly five entries, no duplicates
assert len(FAILURE_SIGNATURES) == 5, "FAILURE_SIGNATURES must have exactly five entries"
assert len({s.id for s in FAILURE_SIGNATURES}) == 5, "FAILURE_SIGNATURES ids must be unique"


# ---------------------------------------------------------------------------
# Scan function
# ---------------------------------------------------------------------------

# Map signature id -> compiled regex for log-source entries
_LOG_PATTERNS: dict[str, re.Pattern[str]] = {
    "auth_401": _AUTH_401_RE,
    "billing_credit_balance": _BILLING_RE,
    "model_404": _MODEL_404_RE,
    "parse_after_retries": _PARSE_AFTER_RETRIES_RE,
}


def scan(
    log_path: Path | None,
    records_by_model_domain: dict[tuple[str, str], list[dict[str, Any]]],
) -> list[SignatureHit]:
    """Scan a log file and a record set for all five failure signatures.

    Args:
        log_path: Path to the per-model log file. May be None or absent;
            log-source checks are skipped when the log is unavailable.
        records_by_model_domain: Dict mapping (model_id, domain_slug) to a
            list of parsed record dicts (plain dicts, not InformantRecord
            objects). Used for record-source checks only.

    Returns:
        List of SignatureHit, one per (signature, matching_line_or_record).
        An empty list means no signatures were detected.
    """
    hits: list[SignatureHit] = []

    # Log-source checks
    log_text: str = ""
    if log_path is not None and log_path.exists():
        try:
            log_text = log_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            log_text = ""

    if log_text:
        for sig in FAILURE_SIGNATURES:
            if sig.source != "log":
                continue
            pattern = _LOG_PATTERNS[sig.id]
            for lineno, line in enumerate(log_text.splitlines(), 1):
                if pattern.search(line):
                    hits.append(
                        SignatureHit(
                            signature_id=sig.id,
                            label=sig.label,
                            source="log",
                            evidence=f"line {lineno}: {line.strip()[:120]}",
                        )
                    )
                    # One hit per signature per scan call is sufficient for
                    # the alert row; break after first match for each sig.
                    break

    # Record-source checks
    hits.extend(_check_refusal_streak(records_by_model_domain))

    return hits
