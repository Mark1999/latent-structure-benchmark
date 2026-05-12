"""Publish-layer defensive sanitization for LSB dashboard output.

Applies three categories of redaction passes to model-generated or
pipeline-generated string content before it is written to
apps/dashboard/public/. See SECURITY_AND_HARDENING.md §3.3 and §3.4.

Each redaction match is replaced with a visible marker string so that a
reader who inspects the published JSON can detect that redaction occurred
(a visible marker preserves the analytical signal; silent suppression
would hide that a pattern was present). See
docs/status/2026-05-12-phase6-T9-cda-sme-verdict.md §2.1.

This module does not interpret why a string matched a pattern. Comments
describe the structural shape being detected, not any intent attributed
to the source of the string.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# API-key pattern list.
# Patterns mirror SECURITY_AND_HARDENING.md §3.4 gitleaks rules.
# Each pattern describes a structural string shape; no intent is implied.
# ---------------------------------------------------------------------------

_API_KEY_PATTERNS: list[re.Pattern[str]] = [
    # Anthropic key shape: sk-ant- prefix, 50+ alphanumeric chars.
    re.compile(r"sk-ant-[a-zA-Z0-9_-]{50,}"),
    # OpenRouter key shape: sk-or-v1- prefix, 60+ alphanumeric chars.
    re.compile(r"sk-or-v1-[a-zA-Z0-9]{60,}"),
    # HuggingFace token shape: hf_ prefix, 30+ alphanumeric chars.
    re.compile(r"hf_[a-zA-Z0-9]{30,}"),
    # Generic Anthropic/OpenAI key shape: word-boundary anchored sk- prefix,
    # minimum 50 chars. Word-boundary anchor and 50-char minimum reduce
    # false-positive matches on short benign strings. See
    # docs/status/2026-05-12-phase6-T9-cda-sme-verdict.md §5.4.
    re.compile(r"\bsk-[a-zA-Z0-9_-]{50,}"),
]

# ---------------------------------------------------------------------------
# Slack webhook URL pattern.
# Matches strings shaped like a Slack incoming-webhook URL.
# See SECURITY_AND_HARDENING.md §3.4 (Reviewer R10).
# ---------------------------------------------------------------------------

_WEBHOOK_PATTERN: re.Pattern[str] = re.compile(
    r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[a-zA-Z0-9]+"
)

# ---------------------------------------------------------------------------
# Local filesystem path patterns.
# Matches strings shaped like local-filesystem paths that should not appear
# in published JSON. Defense-in-depth: model output should not contain these,
# but occasional provider error messages or pipeline diagnostics could include
# absolute paths that identify the operator's server layout.
# ---------------------------------------------------------------------------

_LOCAL_PATH_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"/opt/lsb-agent/[^\s\"']*"),
    re.compile(r"/home/(lsb|markd)/[^\s\"']*"),
    re.compile(r"\bdata/raw/[^\s\"']*"),
    re.compile(r"\bdata/results/[^\s\"']*"),
    re.compile(r"\bdata/processed/[^\s\"']*"),
]

# Redaction markers — visible strings that replace matched content.
_SECRET_MARKER = "[redacted: secret pattern]"
_PATH_MARKER = "[redacted: local path]"


def sanitize_for_publication(s: str) -> str:
    """Redact secret-shaped strings and local-filesystem paths from a string.

    Applied to every string leaf of every record before writing to
    apps/dashboard/public/. See SECURITY_AND_HARDENING.md §3.3 and §3.4.

    Three pass types, applied in order:
    1. API-key shaped strings (Anthropic, OpenRouter, HuggingFace, generic).
    2. Slack webhook URL shaped strings.
    3. Local filesystem path shaped strings.

    Each match is replaced with a visible marker (not silently dropped), so
    that readers inspecting the published JSON can detect that redaction
    occurred. See docs/status/2026-05-12-phase6-T9-cda-sme-verdict.md §2.1.
    """
    for pat in _API_KEY_PATTERNS:
        s = pat.sub(_SECRET_MARKER, s)
    s = _WEBHOOK_PATTERN.sub(_SECRET_MARKER, s)
    for pat in _LOCAL_PATH_PATTERNS:
        s = pat.sub(_PATH_MARKER, s)
    return s


def sanitize_record_strings(obj: object) -> object:
    """Recursively apply sanitize_for_publication() to every str leaf.

    Handles nested dicts and lists. Non-string leaves are passed through
    unchanged. Returns a new object (does not mutate the input).
    """
    if isinstance(obj, str):
        return sanitize_for_publication(obj)
    if isinstance(obj, dict):
        return {k: sanitize_record_strings(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_record_strings(item) for item in obj]
    return obj
