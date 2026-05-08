"""Phase 4a.1 decline-interview backfill runner — enumeration and dry-run (T1 scope).

This script reads informants.jsonl and failures.jsonl, invokes the deterministic
decline-detection module, and reports the detected session set without making any
API calls (--dry-run mode).

T1 delivers the --dry-run path only. The --execute path is T2 scope; its handler
body raises NotImplementedError with a pointer to the plan document.

T1-update adds:
  - should_include_failure() exclusion filter (SME A1–A4)
  - Section 3b: excluded failures-origin records audit with controlled-vocabulary
    rationale header (SME A7)
  - Section 3c: unclassified-default-include records with dry-run-blocking tripwire
    above 2 records (SME A4)
  - --source {informants,failures,all} CLI flag
  - --max-batch-calls CLI flag (default 200); replaces cost-based gate
  - Both full-count and post-exclusion call projections in Section 5 (SME A8)
  - Pre-flight gate uses post-exclusion count (SME A8)

SME binding notes satisfied in this file (Amendment 1 notes A1–A8):
  A1 — General principle: exclude HTTP-infrastructure, include safety-filter refusals
  A2 — 'jailbreak' added to SAFETY_FILTER_MARKERS
  A3 — empty_response cohort gets distinct rationale key before parse_exhaustion step
  A4 — unclassified-saturation tripwire (>2 → SURFACE-TO-SME, exit non-zero)
  A7 — Section 3b controlled-vocabulary rationale header
  A8 — Section 5 reports both full-count and post-exclusion call-count projections

Design notes for T5/T3A/T3B (implementing code omitted per scope boundary):
  A5 — T5 §5 "Exclusion rule applied" must enumerate excluded records by identifier.
       The identifier format from _failure_identifier() is:
       failure|<model_id>|<domain>|<run_index>|<timestamp>
       Section 3b output is the source material for T5 §5 enumeration.
  A6 — T3A must be inspected for recursive-decline before T3B fires, regardless of
       non-CN-origin presence. This is an operator/SME protocol gate; the code here
       does not enforce it. A6 binds at T3B authorization time.

References:
  Architect plan (original):  docs/status/2026-04-23-phase4a1-architect-plan.md
  SME verdict (original):     docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md
  Architect plan (Amendment): docs/status/2026-04-23-phase4a1-architect-plan-amendment-1.md
  SME verdict (Amendment 1):  docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md

Exit codes:
  0  — dry-run completed cleanly (GO disposition)
  1  — IO or parse error
  2  — projected batch >= 80% of call cap; escalation required (STOP)
       OR unclassified-saturation tripwire fired (SURFACE-TO-SME)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import statistics
import sys
import time
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from cdb_collect.adapters.base import ModelAdapter
from cdb_collect.decline_detection import (
    DetectedSession,
    _failure_identifier,
    detect_all,
    detect_from_failure,
)
from dotenv import load_dotenv

load_dotenv()

# ── Call-count gate constants ─────────────────────────────────────────────────
DEFAULT_MAX_BATCH_CALLS: int = 200
ESCALATION_THRESHOLD_RATIO: float = 0.80  # 80% of cap → SURFACE-TO-SME

# ── Exclusion filter constants (Amendment 1 §2 + SME A2, A3) ─────────────────

HTTP_INFRASTRUCTURE_EXCEPTION_TYPES: frozenset[str] = frozenset({
    "HTTPStatusError",       # httpx 4xx/5xx
    "ConnectError",          # httpx connection errors
    "ConnectTimeout",
    "ReadTimeout",
    "WriteTimeout",
    "PoolTimeout",
    "TimeoutError",          # stdlib
    "ConnectionError",       # stdlib
    "RemoteProtocolError",   # httpx
    "ReadError",             # httpx
    "WriteError",            # httpx
})

# Reserved for future use; empty in v1 because all observed ValueError cases in
# failures.jsonl are post-generation parse exhaustion. If an adapter starts raising
# a pre-generation validation error, add its classname here on a new Architect plan
# cycle.
ADAPTER_PARSE_PRE_GENERATION_TYPES: frozenset[str] = frozenset()

# SME A2: 'jailbreak' added to base list
SAFETY_FILTER_MARKERS: tuple[str, ...] = (
    "safety",
    "content policy",
    "content_policy",
    "blocked",
    "harmful",
    "prohibited",
    "policy_violation",
    "content_filter",
    "jailbreak",              # SME A2: canonical refusal-vocabulary term
    "RECITATION",             # Gemini finish_reason for copyright block
    "SAFETY",                 # Gemini finish_reason for safety block
    "PROHIBITED_CONTENT",
    # "OTHER" is Gemini's generic content-block finish_reason. Note: case-insensitive
    # substring matching means this will match any error message containing the
    # substring "other" (e.g., "another", "OtherConnectionError"). Acceptable trade-off
    # per CDA SME verdict 2026-04-23 Amendment 1; the rarity of provider refusal
    # messages containing an unrelated "other" substring keeps the false-positive rate
    # negligible on current corpus. If this changes, revisit via new plan cycle.
    "OTHER",
)

PARSE_EXHAUSTION_MARKERS: tuple[str, ...] = (
    "Pile sort parsing failed after 3 attempts",
    "Could not extract valid JSON from response",
    "Items missing from pile sort",
)

# Below this character count (post-strip), a response cannot plausibly be a
# substantive description of a multi-step exchange. Per SME T3B-detector verdict
# Q1.B (binding): "the shortest plausibly-substantive single-sentence description
# (~50 chars) leaves headroom; 40 still catches short-form refusals like
# 'I cannot describe what happened.' (~32 chars) or 'I won't engage with this.'
# (~25 chars)." Anywhere in 30-60 is defensible; 40 is fixed and may not drift
# without SME re-review.
MIN_SUBSTANTIVE_RESPONSE_LEN: int = 40

# First-person refusal locutions that target the decline-interview task itself.
# Per SME T3B-detector verdict Q1.C (binding allowlist; starting set). Subject is
# the model, verb is a refusal verb, object is the current task. Substring match
# is case-insensitive against response_verbatim.
#
# This list is BINDING as the starting set. Architect may extend on a future
# amendment if a real recursive-decline pattern appears that is not on the list
# (one such observation triggers narrow SME review, not silent extension). The
# Architect may NOT prune it without SME review.
RECURSIVE_DECLINE_PHRASES: tuple[str, ...] = (
    "i cannot describe",
    "i can't describe",
    "i won't describe",
    "i am unable to describe",
    "i'm unable to describe",
    "i cannot discuss",
    "i can't discuss",
    "i won't discuss",
    "i cannot engage with",
    "i can't engage with",
    "i won't engage with",
    "i'm not able to discuss",
    "i am not able to discuss",
    "i'm not able to describe",
    "i am not able to describe",
    "i decline to",
    "i must decline",
    "i refuse to",
    "i cannot comply",
    "i can't comply",
    "i won't comply",
    "i cannot help with",
    "i can't help with",
    "i'm not going to",
    "i am not going to",
    "i'd rather not",
    "i would rather not",
    "i prefer not to",
)

# ── Default paths (all relative to repo root) ─────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INFORMANTS_PATH = _REPO_ROOT / "data" / "raw" / "informants.jsonl"
DEFAULT_FAILURES_PATH = _REPO_ROOT / "data" / "raw" / "failures.jsonl"
DEFAULT_OUTPUT_PATH = _REPO_ROOT / "data" / "raw" / "decline_interviews.jsonl"


# ── Exclusion filter ───────────────────────────────────────────────────────────

def should_include_failure(entry: dict) -> tuple[bool, str]:
    """Determine whether a failures.jsonl entry should be included in the backfill.

    Implements the Amendment 1 §2 decision tree (first match wins).

    Args:
        entry: A single failures.jsonl record as a plain dict.

    Returns:
        (include_bool, rationale_string) where rationale_string is a stable,
        controlled-vocabulary identifier suitable for logging in Section 3b
        and T5 §5 "Exclusion rule applied" enumeration.

    Rationale taxonomy (v1):
      http_infrastructure:{exception_type}
        — HTTP/network/timeout errors, no exchange
      adapter_pre_generation_parse:{exception_type}
        — Adapter pre-generation failure (empty in v1)
      safety_filter:matched:{marker!r}
        — Safety-filter refusal surfaced via error channel (INCLUDE)
      parse_exhaustion:{marker[:30]}
        — Post-generation parse exhaustion (INCLUDE)
      empty_response:likely_silent_safety_block
        — Gemini-style empty body after "Could not extract" (INCLUDE)
      unclassified:default_include:{exception_type}
        — Not matched by any rule; default-include

    Decision tree:
      Step 1: Safety-filter marker in error_message (case-insensitive) → INCLUDE
      Step 2: error_type in HTTP_INFRASTRUCTURE_EXCEPTION_TYPES → EXCLUDE
      Step 3: error_type in ADAPTER_PARSE_PRE_GENERATION_TYPES (empty v1) → EXCLUDE
      Step 4 (SME A3): ValueError + "Could not extract..." + empty body → INCLUDE with distinct key
      Step 5: PARSE_EXHAUSTION_MARKERS substring in error_message → INCLUDE
      Step 6: Default → INCLUDE (unclassified)

    Note on T5/T3A/T3B (SME A5): Section 3b output (identifier + rationale) is the
    source material for T5 §5 "Exclusion rule applied" by-identifier enumeration.
    The identifier is produced by _failure_identifier() as:
      failure|<model_id>|<domain>|<run_index>|<timestamp>
    This is stable and round-trippable from the failures.jsonl record.
    """
    error_type: str = entry.get("error_type", "")
    error_message: str = entry.get("error_message", "")
    msg_lower = error_message.lower()

    # Step 1 — Safety-filter blocks override the infrastructure exclusion.
    # Some providers surface safety blocks as HTTP 400 with refusal content in
    # the response body / error message (OpenAI, Anthropic). Message-substring is
    # the reliable cross-provider classifier.
    for marker in SAFETY_FILTER_MARKERS:
        if marker.lower() in msg_lower:
            return (True, f"safety_filter:matched:{marker!r}")

    # Step 2 — HTTP / network / timeout infrastructure failures: exclude.
    # These represent transport/network events; no model-generated exchange occurred.
    if error_type in HTTP_INFRASTRUCTURE_EXCEPTION_TYPES:
        return (False, f"http_infrastructure:{error_type}")

    # Step 3 — Adapter parse failure BEFORE generation: exclude (empty in v1).
    if error_type in ADAPTER_PARSE_PRE_GENERATION_TYPES:
        return (False, f"adapter_pre_generation_parse:{error_type}")

    # Step 4 (SME A3) — Empty-response body (Gemini cohort).
    # Must be BEFORE step 5 parse_exhaustion to avoid conflating with
    # partial-output parse exhaustions (which clearly generated).
    # Matcher: ValueError + contains "Could not extract valid JSON from response: "
    #          AND the content after the colon+space is empty or whitespace only.
    # This isolates the Gemini 10-record empty-response cohort from the ~14
    # non-empty partial-output parse exhaustions.
    #
    # Implementation note: the spec pseudocode checks rstrip().endswith(": ") or
    # rstrip().endswith(":"), which would incorrectly match partial-output messages
    # like "Could not extract valid JSON from response: {\"foo\":" (also ends with ":").
    # The correct test is that the fragment AFTER the sentinel prefix is blank.
    # This is equivalent to: the full message is exactly the sentinel (possibly with
    # trailing whitespace), i.e., the response body was empty.
    _SENTINEL = "Could not extract valid JSON from response: "
    if error_type == "ValueError" and _SENTINEL in error_message:
        sentinel_pos = error_message.index(_SENTINEL)
        after_sentinel = error_message[sentinel_pos + len(_SENTINEL):]
        if not after_sentinel.strip():
            return (True, "empty_response:likely_silent_safety_block")

    # Step 5 — Post-generation parse exhaustion: include.
    # The model generated; the generation was off-spec.
    for marker in PARSE_EXHAUSTION_MARKERS:
        if marker in error_message:
            return (True, f"parse_exhaustion:{marker[:30]}")

    # Step 6 — Default: include with "unclassified" rationale.
    # Default-include is the correct posture per SME A3:
    #   - The instrument's purpose is audit; an unclassified record is a signal.
    #   - The cost ceiling is bounded ($10 cap, ~$0.05/call).
    #   - The filter is consumer-side; over-inclusion is recoverable.
    return (True, f"unclassified:default_include:{error_type}")


# ── qa_notes parsing helpers ──────────────────────────────────────────────────

def _parse_failing_checks(qa_notes: str) -> list[str]:
    """Derive the list of failing check codes from an InformantRecord qa_notes string.

    The qa_notes format written by scripts/qa_check.py is semi-structured:
      - Latency-only (Check 5):          "102547ms"
      - Token inconsistency (Check 6):   "154728ms; 8544"   (latency_ms; token_count)
      - Empty freelist (Check 1):        "0; 71000ms; 171"  (items=0; latency; tokens)
      - Label mismatch (Check 8):        "label_count_mismatch:20/9"
      - Compound 5+8:                    "60124ms; label_count_mismatch:16/81"

    Returns a list of human-readable check identifiers, e.g.:
      ["check_5_latency_exceeded"]
      ["check_5_latency_exceeded", "check_6_token_inconsistency"]
      ["check_1_freelist_empty", "check_5_latency_exceeded", "check_6_token_inconsistency"]
      ["check_8_label_count_mismatch"]
    """
    checks: list[str] = []
    if not qa_notes:
        return checks

    # Check 8 — label count mismatch
    if "label_count_mismatch" in qa_notes:
        checks.append("check_8_label_count_mismatch")

    # Check 5 — latency (any segment matching NNNms where NNN is an integer)
    if re.search(r"\d+ms", qa_notes):
        checks.append("check_5_latency_exceeded")

    # Check 6 — token inconsistency (a bare integer segment after the latency part)
    # Pattern: a segment that is purely digits and >= 100 (to distinguish from
    # item counts like "0" which represent Check 1).
    segments = [s.strip() for s in qa_notes.split(";")]
    for seg in segments:
        if re.match(r"^\d+$", seg):
            val = int(seg)
            if val >= 100:  # token counts are large numbers; freelist=0 is small
                checks.append("check_6_token_inconsistency")
                break

    # Check 1 — empty freelist (segment that is exactly "0")
    for seg in segments:
        if seg.strip() == "0":
            checks.append("check_1_freelist_empty")
            break

    return checks


def _originating_step_from_checks(failing_checks: list[str]) -> str:
    """Derive the originating_step label for a not-triggered QA failure record.

    Maps from the parsed failing_checks list to the CDA step that last failed,
    following the step ordering: freelist < pile_sort < interview.

    Rules:
      - check_1_freelist_empty                          → freelist
      - check_5_latency_exceeded / check_6_token_inconsistency → pile_sort
      - check_8_label_count_mismatch                    → interview
      - Compound: last (deepest) step that appears wins.
        e.g. check_1 + check_5 → pile_sort
             check_1 + check_8 → interview
             check_5 + check_8 → interview
      - No recognised check → unknown
    """
    check_set = set(failing_checks)
    if not check_set:
        return "unknown"

    # Walk steps from deepest to shallowest; return the first (deepest) hit.
    if "check_8_label_count_mismatch" in check_set:
        return "interview"
    if "check_5_latency_exceeded" in check_set or "check_6_token_inconsistency" in check_set:
        return "pile_sort"
    if "check_1_freelist_empty" in check_set:
        return "freelist"
    return "unknown"


def _not_triggered_reason(failing_checks: list[str]) -> str:
    """Derive a one-phrase audit reason for a qa_passed=False record that detect_from_informant
    returned None for.

    Returns a human-readable explanation of why the structural decline trigger was not met.
    """
    check_set = set(failing_checks)

    # Single-check cases
    if check_set == {"check_5_latency_exceeded"}:
        return "Check-5 latency-only, no structural refusal trigger"

    if check_set == {"check_8_label_count_mismatch"}:
        # Check-8 records: mistral-small and gpt-5.4-mini have label mismatches
        # but their response_verbatim is non-empty, so trigger (d) does not fire
        # because trigger (d) requires parsed_pile_labels=[] AND non-empty response.
        # Actually, check_8 records with label_count_mismatch have label counts > 0
        # just mismatched — so they are detected via trigger (d) only if labels=0.
        # This branch is reached only when detect_from_informant returned None.
        return "Check-8 label-count mismatch, parsed_pile_labels non-empty (count > 0)"

    if check_set == {"check_6_token_inconsistency"}:
        return "Check-6 token inconsistency only, response_verbatim non-empty"

    if check_set == {"check_1_freelist_empty"}:
        # Should not occur in not-triggered population (Check-1 → trigger c fires)
        return "Check-1 empty freelist — should have triggered; inspect manually"

    # Compound cases
    parts: list[str] = []
    check_nums: list[str] = []
    if "check_1_freelist_empty" in check_set:
        check_nums.append("1")
    if "check_5_latency_exceeded" in check_set:
        check_nums.append("5")
    if "check_6_token_inconsistency" in check_set:
        check_nums.append("6")
    if "check_8_label_count_mismatch" in check_set:
        check_nums.append("8")

    compound_label = "Check " + "+".join(check_nums) if check_nums else "unknown checks"

    if "check_5_latency_exceeded" in check_set and "check_6_token_inconsistency" in check_set:
        parts.append("response_verbatim non-empty, no allowlist string match")
    if "check_8_label_count_mismatch" in check_set:
        parts.append("parsed_pile_labels non-empty (label count > 0, but mismatched)")

    detail = "; ".join(parts) if parts else "response_verbatim non-empty"
    return f"{compound_label}; {detail}"


# ── JSONL loading helpers ──────────────────────────────────────────────────────

def _load_jsonl_dicts(path: Path) -> list[dict]:
    """Load all non-empty lines from a JSONL file as plain dicts.

    Returns an empty list if the file does not exist.
    Raises SystemExit(1) on parse errors.
    """
    if not path.exists():
        return []
    records: list[dict] = []
    try:
        with open(path, encoding="utf-8") as fh:
            for lineno, raw in enumerate(fh, 1):
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    records.append(json.loads(raw))
                except json.JSONDecodeError as exc:
                    print(
                        f"ERROR: parse failure at {path}:{lineno} — {exc}",
                        file=sys.stderr,
                    )
                    sys.exit(1)
    except OSError as exc:
        print(f"ERROR: cannot read {path} — {exc}", file=sys.stderr)
        sys.exit(1)
    return records


# ── Gemini helpers ─────────────────────────────────────────────────────────────

def _is_gemini_failure(entry: dict) -> bool:
    """Return True if a failures.jsonl entry is a Gemini model entry."""
    ctx = entry.get("context", {})
    model_id: str = ctx.get("model_id", "")
    return model_id.startswith("google/gemini") or model_id.startswith("gemini")


# ── Dry-run report ─────────────────────────────────────────────────────────────

def run_dry_run(
    informants_path: Path,
    failures_path: Path,
    output_path: Path,
    verbose: bool = False,
    max_batch_calls: int = DEFAULT_MAX_BATCH_CALLS,
    escalation_ratio: float = ESCALATION_THRESHOLD_RATIO,
    source: str = "all",
    # Backward-compat shim: test helpers may pass spend_cap= kwarg.  # noqa: spend-gate-check
    spend_cap: float | None = None,  # noqa: spend-gate-check
) -> int:
    """Execute the dry-run: enumerate detected sessions and print the report.

    Touches only stdout. No file writes. No network calls.

    Args:
        informants_path: Path to informants.jsonl.
        failures_path:   Path to failures.jsonl.
        output_path:     Declared output path (not written; present for T2 symmetry).
        verbose:         If True, emit per-record rows in the not-triggered section
                         even when the count is zero.
        max_batch_calls: Maximum calls permitted in one execute batch (injectable
                         for tests). Pre-flight fires STOP/SURFACE-TO-SME when
                         projected calls >= 80% of this value.
        escalation_ratio: Fraction of cap at which call-guard escalation fires.
        source:          Which origin to process: 'informants', 'failures', or 'all'.
        spend_cap:       Ignored. Backward-compat only.  # noqa: spend-gate-check

    Returns:
        Exit code: 0 on success (GO), 2 on call-guard escalation (STOP) or
        unclassified-saturation (SURFACE-TO-SME).
    """
    _ = spend_cap  # noqa: spend-gate-check
    # ── Load raw data ──────────────────────────────────────────────────────────
    informant_dicts = _load_jsonl_dicts(informants_path)
    failure_dicts = _load_jsonl_dicts(failures_path)

    # ── Run detection ──────────────────────────────────────────────────────────
    detected_sessions = detect_all(informant_dicts, failure_dicts)

    # Split sessions by source for --source filtering
    informants_sessions = [s for s in detected_sessions if s.source == "informants"]
    failures_sessions = [s for s in detected_sessions if s.source == "failures"]

    # Apply --source filter to displayed sessions
    if source == "informants":
        display_sessions = informants_sessions
    elif source == "failures":
        display_sessions = failures_sessions
    else:  # all
        display_sessions = detected_sessions

    # Build per-informant lookup for triggered IDs
    triggered_ids: set[str] = {s.identifier for s in detected_sessions}

    # ── Collect "not triggered" informant records ──────────────────────────────
    # Only qa_passed=False records that detect_from_informant returned None for.
    not_triggered_informant: list[dict] = []
    if source in ("informants", "all"):
        for rec in informant_dicts:
            if rec.get("qa_passed", True):
                continue  # only care about failed records
            iid = rec.get("informant_id", "unknown")
            if iid in triggered_ids:
                continue  # was triggered; not in not-triggered list
            not_triggered_informant.append(rec)

    # Collect "not triggered" failure entries (detect_from_failure currently always
    # returns a DetectedSession for valid entries, but keep the audit path open
    # in case future filtering logic is added).
    not_triggered_failure: list[dict] = []
    if source in ("failures", "all"):
        for entry in failure_dicts:
            fid_session = detect_from_failure(entry)
            if fid_session is None:
                not_triggered_failure.append(entry)

    # ── Apply exclusion filter to failures-origin sessions ────────────────────
    # Build map from identifier -> failure dict for fast lookup
    failure_dict_by_id: dict[str, dict] = {}
    for entry in failure_dicts:
        fid = _failure_identifier(entry)
        failure_dict_by_id[fid] = entry

    # Classify failures-origin detected sessions
    excluded_failures: list[tuple[str, str, str]] = []   # (identifier, error_type, rationale)
    included_failures: list[DetectedSession] = []
    unclassified_failures: list[tuple[str, str, str]] = []  # (identifier, error_type, msg_snippet)

    if source in ("failures", "all"):
        for session in failures_sessions:
            entry = failure_dict_by_id.get(session.identifier, {})
            include, rationale = should_include_failure(entry)
            if include:
                included_failures.append(session)
                if rationale.startswith("unclassified:default_include"):
                    error_type = entry.get("error_type", "")
                    error_msg = entry.get("error_message", "")
                    unclassified_failures.append(
                        (session.identifier, error_type, error_msg[:120])
                    )
            else:
                error_type = entry.get("error_type", "")
                excluded_failures.append((session.identifier, error_type, rationale))

    # For --source informants, no failures-origin sessions are in scope
    if source == "informants":
        included_failures = []
        excluded_failures = []
        unclassified_failures = []

    # ── Section 1 — Summary table (grouped) ───────────────────────────────────
    print("=" * 72)
    print("SECTION 1 — TRIGGERED SESSIONS SUMMARY")
    print("=" * 72)

    GroupKey = tuple[str, str, str, str]  # (source, originating_step, outcome_class, model_id)
    group_counts: dict[GroupKey, int] = defaultdict(int)

    for session in display_sessions:
        key: GroupKey = (
            session.source,
            session.originating_step,
            session.originating_outcome_class,
            _get_model_id_for_session(session, informant_dicts, failure_dicts),
        )
        group_counts[key] += 1

    col_widths = (12, 14, 25, 35, 6)
    header = (
        f"{'source':<{col_widths[0]}}"
        f"{'orig_step':<{col_widths[1]}}"
        f"{'outcome_class':<{col_widths[2]}}"
        f"{'model_id':<{col_widths[3]}}"
        f"{'count':>{col_widths[4]}}"
    )
    print(header)
    print("-" * sum(col_widths))

    if group_counts:
        for (src, step, outcome, model_id), count in sorted(group_counts.items()):
            print(
                f"{src:<{col_widths[0]}}"
                f"{step:<{col_widths[1]}}"
                f"{outcome:<{col_widths[2]}}"
                f"{model_id:<{col_widths[3]}}"
                f"{count:>{col_widths[4]}}"
            )
    else:
        print("(no triggered sessions)")
    print()

    # ── Section 2 — Per-record detail for triggered sessions ──────────────────
    print("=" * 72)
    print("SECTION 2 — TRIGGERED SESSIONS PER-RECORD DETAIL (input to T2)")
    print("=" * 72)

    s2_col = (20, 35, 12, 14, 25)
    s2_header = (
        f"{'id':<{s2_col[0]}}"
        f"{'model_id':<{s2_col[1]}}"
        f"{'domain':<{s2_col[2]}}"
        f"{'orig_step':<{s2_col[3]}}"
        f"{'outcome_class':<{s2_col[4]}}"
    )
    print(s2_header)
    print("-" * sum(s2_col))

    # Build lookup dicts for model_id and domain from source records
    informant_meta: dict[str, tuple[str, str]] = {}  # id -> (model_id, domain)
    for rec in informant_dicts:
        iid = rec.get("informant_id", "unknown")
        informant_meta[iid] = (rec.get("model_id", "unknown"), rec.get("domain_slug", "unknown"))

    failure_meta: dict[str, tuple[str, str]] = {}  # id -> (model_id, domain)
    for entry in failure_dicts:
        ctx = entry.get("context", {})
        fid = _failure_identifier(entry)
        failure_meta[fid] = (
            ctx.get("model_id", "unknown"),
            ctx.get("domain", "unknown"),
        )

    if display_sessions:
        for session in display_sessions:
            if session.source == "informants":
                model_id, domain = informant_meta.get(session.identifier, ("unknown", "unknown"))
            else:
                model_id, domain = failure_meta.get(session.identifier, ("unknown", "unknown"))
            print(
                f"{session.identifier:<{s2_col[0]}}"
                f"{model_id:<{s2_col[1]}}"
                f"{domain:<{s2_col[2]}}"
                f"{session.originating_step:<{s2_col[3]}}"
                f"{session.originating_outcome_class:<{s2_col[4]}}"
            )
    else:
        print("(no triggered sessions)")
    print()

    # ── Section 3 — Not-triggered per-record audit (SME binding note 1) ───────
    print("=" * 72)
    print("SECTION 3 — NOT-TRIGGERED PER-RECORD AUDIT (SME binding note 1)")
    print("=" * 72)
    print("Every qa_passed=False informant record where detect_from_informant")
    print("returned None, and any failure entry where detect_from_failure")
    print("returned None. One row = one record (not a summary).")
    print()

    s3_col = (20, 35, 12, 14, 45)
    s3_header = (
        f"{'id':<{s3_col[0]}}"
        f"{'model_id':<{s3_col[1]}}"
        f"{'domain':<{s3_col[2]}}"
        f"{'originating_step':<{s3_col[3]}}"
        f"{'failing_checks':<{s3_col[4]}}"
        f"{'reason'}"
    )
    print(s3_header)
    print("-" * (sum(s3_col) + 30))

    not_triggered_count = 0

    for rec in not_triggered_informant:
        iid = rec.get("informant_id", "unknown")
        model_id = rec.get("model_id", "unknown")
        domain = rec.get("domain_slug", "unknown")
        qa_notes = rec.get("qa_notes", "")
        failing_checks = _parse_failing_checks(qa_notes)
        originating_step = _originating_step_from_checks(failing_checks)
        reason = _not_triggered_reason(failing_checks)
        checks_str = ", ".join(failing_checks) if failing_checks else "(none parsed)"

        print(
            f"{iid:<{s3_col[0]}}"
            f"{model_id:<{s3_col[1]}}"
            f"{domain:<{s3_col[2]}}"
            f"{originating_step:<{s3_col[3]}}"
            f"{checks_str:<{s3_col[4]}}  "
            f"{reason}"
        )
        not_triggered_count += 1

    for entry in not_triggered_failure:
        ctx = entry.get("context", {})
        fid = _failure_identifier(entry)
        model_id = ctx.get("model_id", "unknown")
        domain = ctx.get("domain", "unknown")
        error_type = entry.get("error_type", "unknown")
        checks_str = f"error_type={error_type}"
        originating_step = "unknown"
        reason = "detect_from_failure returned None (unexpected; inspect entry)"
        print(
            f"{fid:<{s3_col[0]}}"
            f"{model_id:<{s3_col[1]}}"
            f"{domain:<{s3_col[2]}}"
            f"{originating_step:<{s3_col[3]}}"
            f"{checks_str:<{s3_col[4]}}  "
            f"{reason}"
        )
        not_triggered_count += 1

    if not_triggered_count == 0 and not verbose:
        print("(no not-triggered records)")
    print()

    # ── Section 3b — Excluded failures-origin records (SME A7) ────────────────
    print("=" * 72)
    print(
        "Section 3b — Failures-origin records excluded from backfill "
        "(call-count gate + methodology filter)"
    )
    print("=" * 72)
    print("Rationale taxonomy (v1):")
    print(
        "  http_infrastructure:{exception_type}"
        "         — HTTP/network/timeout errors, no exchange"
    )
    print(
        "  adapter_pre_generation_parse:{exception_type}"
        " — Adapter pre-generation failure (empty in v1)"
    )
    print(
        "  safety_filter:matched:{marker}"
        "               — Safety-filter refusal surfaced via error channel (INCLUDE)"
    )
    print(
        "  parse_exhaustion:{marker}"
        "                    — Post-generation parse exhaustion (INCLUDE)"
    )
    print(
        "  empty_response:likely_silent_safety_block"
        "    — Gemini-style empty body after Could not extract (INCLUDE)"
    )
    print(
        "  unclassified:default_include:{exception_type}"
        " — Not matched by any rule; default-include"
    )
    print()

    id_col_w = 55
    et_col_w = 22
    print(
        f"{'identifier':<{id_col_w}}"
        f"{'error_type':<{et_col_w}}"
        f"{'rationale'}"
    )
    print(
        "─" * id_col_w
        + "┼"
        + "─" * et_col_w
        + "┼"
        + "─" * 35
    )

    if source == "informants":
        print("(--source informants: failures-origin pipeline not processed)")
    elif excluded_failures:
        for ident, et, rationale in excluded_failures:
            print(
                f"{ident:<{id_col_w}}"
                f"{et:<{et_col_w}}"
                f"{rationale}"
            )

    n_exc = len(excluded_failures) if source != "informants" else 0
    print(f"Total excluded: {n_exc}")

    if source == "informants":
        print("Exclusion breakdown: N/A (--source informants)")
    else:
        # Build breakdown from excluded_failures
        excl_by_prefix: dict[str, int] = defaultdict(int)
        for _ident, _et, rationale in excluded_failures:
            # Group by first two segments of rationale key
            parts = rationale.split(":")
            prefix = f"{parts[0]}:{parts[1]}" if len(parts) >= 2 else rationale
            excl_by_prefix[prefix] += 1

        if excl_by_prefix:
            breakdown_str = ", ".join(
                f"{k}={v}" for k, v in sorted(excl_by_prefix.items())
            )
            print(f"Exclusion breakdown: {breakdown_str}")
        else:
            print("Exclusion breakdown: (none)")
    print()

    # ── Section 3c — Unclassified-default-include records (SME A4) ────────────
    print("=" * 72)
    print(
        "Section 3c — Unclassified-default-include records "
        "(SME review recommended before T3B)"
    )
    print("=" * 72)

    if source == "informants":
        print("(--source informants: failures-origin pipeline not processed)")
        n_unclassified = 0
    else:
        uc_id_col = 55
        uc_et_col = 22
        print(
            f"{'identifier':<{uc_id_col}}"
            f"{'error_type':<{uc_et_col}}"
            f"{'first 120 chars of error_message'}"
        )
        print("-" * (uc_id_col + uc_et_col + 35))

        for ident, et, msg_snippet in unclassified_failures:
            print(
                f"{ident:<{uc_id_col}}"
                f"{et:<{uc_et_col}}"
                f"{msg_snippet}"
            )

        n_unclassified = len(unclassified_failures)
        print(f"Total unclassified-default-include: {n_unclassified}")
        print()

    surface_to_sme = False
    if source != "informants" and n_unclassified > 2:
        print(
            "SURFACE-TO-SME: unclassified-saturation warning — "
            f"more than 2 records ({n_unclassified}) lack explicit classification."
        )
        print(
            "Taxonomy drift suspected. Do not proceed to T3A/T3B without "
            "SME review + filter amendment."
        )
        surface_to_sme = True
    print()

    # ── Section 4 — Gemini failures count (SME binding note 8) ────────────────
    print("=" * 72)
    print("SECTION 4 — GEMINI FAILURES COUNT (SME binding note 8)")
    print("=" * 72)

    gemini_entries = [e for e in failure_dicts if _is_gemini_failure(e)]
    gemini_detected = [
        e for e in gemini_entries if detect_from_failure(e) is not None
    ]

    print(f"Total Gemini failure entries:        {len(gemini_entries)}")
    print(f"Gemini entries detected (triggering): {len(gemini_detected)}")
    print(f"Gemini entries not detected:          {len(gemini_entries) - len(gemini_detected)}")
    print()

    # Emit the call-count status line
    _section4_n = len(detected_sessions)
    _section4_threshold_n = max_batch_calls * escalation_ratio
    _section4_status = (
        "ESCALATE — see STOP line below"
        if _section4_n >= _section4_threshold_n
        else "OK"
    )
    print(
        f"Projected batch size (full): {_section4_n} detected calls. "
        f"[{_section4_status}]"
    )
    print()

    # ── Section 5 — CLI summary (SME A8) ──────────────────────────────────────
    print("=" * 72)
    print("===== Dry-run summary =====")
    print("=" * 72)

    total_detected = len(detected_sessions)
    n_informants_origin = len(informants_sessions)
    n_failures_raw = len(failures_sessions)

    # Post-exclusion counts
    if source == "informants":
        n_failures_excluded = 0
        n_failures_included_val = 0
        post_exclusion_total = n_informants_origin
    else:
        n_failures_excluded = len(excluded_failures)
        n_failures_included_val = len(included_failures)
        if source == "failures":
            post_exclusion_total = n_failures_included_val
        else:  # all
            post_exclusion_total = n_informants_origin + n_failures_included_val

    # Call-count projections
    escalation_threshold_n = int(max_batch_calls * escalation_ratio)

    print(f"Detected total:                   {total_detected}")
    print(f"Informants-origin:                {n_informants_origin}")
    print(f"Failures-origin (raw):            {n_failures_raw}")

    if source == "informants":
        print("Failures-origin excluded:         N/A (--source informants)")
        print("Failures-origin included:         N/A (--source informants)")
        print(f"Post-exclusion backfill size:     {n_informants_origin} (informants only)")
    else:
        print(f"Failures-origin excluded:         {n_failures_excluded}")
        print(f"Failures-origin included:         {n_failures_included_val}")
        if source == "failures":
            print(f"Post-exclusion backfill size:     {n_failures_included_val} (failures only)")
        else:
            print(
                f"Post-exclusion backfill size:     "
                f"{n_informants_origin} + {n_failures_included_val} = {post_exclusion_total}"
            )

    print()
    print("Call-count projections:")
    print(f"  Full-count projection:          {total_detected} calls")
    print(f"  Post-exclusion projection:      {post_exclusion_total} calls")
    print()
    print(f"Call cap (--max-batch-calls):     {max_batch_calls}")
    print(f"Pre-flight threshold:             {escalation_threshold_n} (80% of cap)")
    print(f"Gate input (post-exclusion):      {post_exclusion_total} calls")

    # Determine disposition
    calls_exceed = post_exclusion_total >= escalation_threshold_n

    if surface_to_sme:
        disposition = "SURFACE-TO-SME"
    elif calls_exceed:
        disposition = "STOP"
    else:
        disposition = "GO"

    print(f"Disposition:                      {disposition}")
    print()

    if calls_exceed and not surface_to_sme:
        print(
            f"STOP: projected post-exclusion batch at or above 80% of "
            f"{max_batch_calls} call cap "
            f"(projected={post_exclusion_total} >= threshold={escalation_threshold_n}). "
            "Escalate on a new Architect plan cycle per SME binding note 8."
        )
        print()

    # Legacy Section 5 totals for backward compatibility
    print("=" * 72)
    print("SECTION 5 — TOTALS")
    print("=" * 72)

    total_scanned = len(detected_sessions) + not_triggered_count
    print(
        f"Total detected (to be interviewed in T3): {len(detected_sessions)}. "
        f"Total not triggered: {not_triggered_count}. "
        f"Total records scanned: {total_scanned}."
    )
    print()

    if surface_to_sme or calls_exceed:
        return 2
    return 0


def _get_model_id_for_session(
    session: DetectedSession,
    informant_dicts: list[dict],
    failure_dicts: list[dict],
) -> str:
    """Resolve model_id for a DetectedSession from the source dicts."""
    if session.source == "informants":
        for rec in informant_dicts:
            if rec.get("informant_id") == session.identifier:
                return str(rec.get("model_id", "unknown"))
        return "unknown"
    else:
        for entry in failure_dicts:
            if _failure_identifier(entry) == session.identifier:
                return str(entry.get("context", {}).get("model_id", "unknown"))
        return "unknown"


# ── CLI ────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for run_decline_backfill.py."""
    parser = argparse.ArgumentParser(
        prog="run_decline_backfill",
        description=(
            "Phase 4a.1 decline-interview backfill runner. "
            "Use --dry-run to enumerate detected sessions without API calls. "
            "See docs/status/2026-04-23-phase4a1-architect-plan-amendment-1.md for full spec."
        ),
    )

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help=(
            "Enumerate detected sessions and print summary. "
            "No API calls. No file writes. Exit 0 on GO, 2 on STOP or SURFACE-TO-SME."
        ),
    )
    mode_group.add_argument(
        "--execute",
        action="store_true",
        dest="execute",
        help="(T2 scope) Run the full backfill. Not implemented yet.",
    )

    parser.add_argument(
        "--source",
        choices=["informants", "failures", "all"],
        default="all",
        help=(
            "Which origin to process: 'informants' (T3A), 'failures' (T3B), "
            "or 'all' (default, current behavior)."
        ),
    )
    parser.add_argument(
        "--max-batch-calls",
        type=int,
        default=DEFAULT_MAX_BATCH_CALLS,
        dest="max_batch_calls",
        help=(
            f"Maximum API calls per execute batch (default: {DEFAULT_MAX_BATCH_CALLS}). "
            "Pre-flight threshold is 80%% of this value. "
            "Batches projected to exceed 80%% must be authorized by the CDA SME "
            "(SME Amendment 1 binding note A8)."
        ),
    )
    parser.add_argument(
        "--informants-path",
        type=Path,
        default=DEFAULT_INFORMANTS_PATH,
        help="Path to informants.jsonl (default: data/raw/informants.jsonl)",
    )
    parser.add_argument(
        "--failures-path",
        type=Path,
        default=DEFAULT_FAILURES_PATH,
        help="Path to failures.jsonl (default: data/raw/failures.jsonl)",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=(
            "Path to decline_interviews.jsonl "
            "(default: data/raw/decline_interviews.jsonl; not written in T1)"
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Show per-record detail in not-triggered section even when count is zero.",
    )
    return parser


# ── Execute path helpers ──────────────────────────────────────────────────────


def _build_adapter_for_model(model_id: str) -> ModelAdapter:
    """Resolve and instantiate a ModelAdapter for the given model_id.

    Loads the model registry from data/models/registry.json and routes
    to the correct adapter class via collection_method. Mirrors the logic
    in scripts/collect.py::_create_adapter.

    Raises:
        ValueError: If model_id is not found in the registry or the
            collection_method is unknown.
    """
    import json as _json
    from datetime import date

    from cdb_collect.adapters import (
        AnthropicAdapter,
        GeminiAdapter,
        HuggingFaceAdapter,
        OpenAICompatAdapter,
        OpenRouterAdapter,
    )
    from cdb_collect.model_ids import to_direct_id
    from cdb_core import ModelRef

    registry_path = _REPO_ROOT / "data" / "models" / "registry.json"
    if not registry_path.exists():
        raise ValueError(
            f"Model registry not found at {registry_path}. "
            "Run: python scripts/discover_models.py --update-registry"
        )

    data = _json.loads(registry_path.read_text(encoding="utf-8"))
    _METHOD_TO_PROVIDER: dict[str, str] = {
        "anthropic_api": "anthropic",
        "google_ai": "google",
        "xai_api": "xai",
        "openrouter": "openrouter",
        "huggingface": "huggingface",
    }

    model_ref: ModelRef | None = None
    for entry in data.get("models", []):
        eid = entry["model_id"]
        effective = to_direct_id(eid)
        if eid == model_id or effective == model_id:
            method = entry["collection_method"]
            provider = _METHOD_TO_PROVIDER.get(method, "openrouter")
            parts = eid.split("/")
            version_label = parts[-1] if len(parts) > 1 else eid
            created_ts = entry.get("openrouter_created")
            release = date.fromtimestamp(created_ts) if created_ts else date.today()
            model_ref = ModelRef(
                provider=provider,
                model_id=effective,
                family=entry["family"],
                origin=entry["origin"],
                open_weights=entry["open_weights"],
                collection_method=method,
                quantization=None,
                release_date=release,
                version_label=version_label,
            )
            break

    if model_ref is None:
        raise ValueError(
            f"model_id {model_id!r} not found in registry at {registry_path}. "
            "Cannot build adapter."
        )

    method = model_ref.collection_method
    if method == "anthropic_api":
        return AnthropicAdapter(model_ref)
    if method == "google_ai":
        return GeminiAdapter(model_ref)
    if method in ("openai_api", "xai_api", "deepseek_api", "mistral_api"):
        return OpenAICompatAdapter(model_ref)
    if method == "openrouter":
        return OpenRouterAdapter(model_ref)
    if method == "huggingface":
        return HuggingFaceAdapter(model_ref)
    raise ValueError(f"Unknown collection_method: {method}")


def _task_description_from_informant(
    record: dict, originating_step: str,
) -> str:
    """Extract the verbatim task_description from an InformantRecord dict.

    Reads prompt_verbatim from the relevant step sub-record, keyed by
    originating_step (freelist, pile_sort, or interview). Per SME
    binding note 1.1, task_description must be the verbatim prompt,
    not a paraphrase, to preserve reproducibility.

    Returns an empty string if the field is absent (callers should
    handle that as a missing-context case, but the execute path will
    still proceed).
    """
    step_to_field = {
        "freelist": "freelist",
        "pile_sort": "pile_sort",
        "interview": "interview",
        "pre_session": "freelist",  # fallback for pre_session (rare)
    }
    field_name = step_to_field.get(originating_step, "freelist")
    step_record = record.get(field_name, {})
    return str(step_record.get("prompt_verbatim", ""))


def _response_verbatim_from_informant(
    record: dict, originating_step: str,
) -> str:
    """Extract the verbatim response from an InformantRecord dict.

    Reads response_verbatim from the relevant step sub-record.
    Returns empty string if absent.
    """
    step_to_field = {
        "freelist": "freelist",
        "pile_sort": "pile_sort",
        "interview": "interview",
        "pre_session": "freelist",
    }
    field_name = step_to_field.get(originating_step, "freelist")
    step_record = record.get(field_name, {})
    return str(step_record.get("response_verbatim", ""))


def _task_description_from_failure(
    entry: dict, originating_step: str,
) -> str:
    """Extract or reconstruct task_description for a failures.jsonl entry.

    Priority:
    1. entry["prompt_verbatim"] if present (caller-supplied verbatim prompt).
    2. Template reconstruction from cdb_collect prompts — freelist template with
       domain seed substituted for freelist/pre_session steps; raw pile_sort or
       pile_interview template for other steps. This is RISK 1 territory per the
       Amendment 1 plan: the reconstructed prompt is domain-level, not the exact
       prompt sent (which may have had specific items/piles substituted). Pile-sort
       and pile-interview templates will be returned as-is with unfilled placeholders
       because the original items/piles context is not available from the failure
       entry alone.

    RISK 1 note: for pile_sort and interview steps, the reconstructed prompt will
    contain unfilled template markers ({{items}}, {{piles}}). The decline-interview
    build_prompt() in run_decline_interview.py substitutes this as task_description
    directly. The resulting decline-interview prompt will be less precise than one
    constructed from the original context, but it is deterministic and reproducible.
    Downstream analysis should note this limitation for non-freelist reconstructed
    prompts.
    """
    # Priority 1: verbatim if present
    verbatim = entry.get("prompt_verbatim")
    if verbatim is not None:
        return str(verbatim)

    # Priority 2: template reconstruction
    context = entry.get("context", {})
    domain_slug = context.get("domain", "")

    # Path to the cdb_collect prompts directory
    prompts_dir = (
        Path(__file__).resolve().parent.parent
        / "packages" / "cdb_collect" / "cdb_collect" / "prompts" / "v1"
    )

    step_to_template_file = {
        "freelist": "free_list.md",
        "pile_sort": "pile_sort.md",
        "interview": "pile_interview.md",
        "pre_session": "free_list.md",
    }
    template_file = step_to_template_file.get(originating_step, "free_list.md")
    template_path = prompts_dir / template_file

    try:
        template = template_path.read_text(encoding="utf-8").rstrip("\n")
    except OSError:
        # If template is not readable (shouldn't happen on landed repo), return empty
        return ""

    # For freelist/pre_session, substitute domain seed if we can load the domain.
    if originating_step in ("freelist", "pre_session") and domain_slug:
        try:
            from cdb_collect.domains import load_domain
            domain = load_domain(domain_slug)
            return template.replace("{{domain_seed}}", domain.prompt_seed)
        except (FileNotFoundError, ValueError):
            # Domain not found; return template with placeholder intact
            return template.replace("{{domain_seed}}", domain_slug or "{{domain_seed}}")

    # For pile_sort and interview, return raw template (items/piles not available).
    return template


def _response_verbatim_from_failure(entry: dict) -> str:
    """Extract response_verbatim from a failures.jsonl entry.

    Returns entry["response_verbatim"] if present; else empty string.
    The empty string causes build_prompt() in run_decline_interview.py
    to substitute "(empty)" per the bound prompt wording.
    """
    v = entry.get("response_verbatim")
    return str(v) if v is not None else ""


def _is_recursive_decline(response_verbatim: str) -> bool:
    """Return True if the decline-interview RESPONSE is itself a refusal of the
    decline-interview task. Distinct from the original input-classification
    role of SAFETY_FILTER_MARKERS, which detects safety events on the
    originating call.

    A recursive decline is one of:
      (a) Empty or whitespace-only response.
      (b) Response shorter than MIN_SUBSTANTIVE_RESPONSE_LEN characters
          (cannot plausibly be a substantive narrative).
      (c) Response contains a first-person refusal locution targeting the
          current task (RECURSIVE_DECLINE_PHRASES allowlist).

    A response that substantively describes a safety event in the original
    exchange is NOT a recursive decline; it is a successful interview.

    See: docs/status/2026-04-23-phase4a1-t3b-detector-cda-sme-verdict.md Q1
    """
    rv = response_verbatim or ""
    rv_stripped = rv.strip()

    # (a) Empty or whitespace-only
    if not rv_stripped:
        return True

    # (b) Below substantive-narrative length floor
    if len(rv_stripped) < MIN_SUBSTANTIVE_RESPONSE_LEN:
        return True

    # (c) First-person refusal locution targeting the current task
    rv_lower = rv_stripped.lower()
    return any(phrase in rv_lower for phrase in RECURSIVE_DECLINE_PHRASES)


def run_execute(
    informants_path: Path,
    failures_path: Path,
    output_path: Path,
    verbose: bool = False,
    max_batch_calls: int = DEFAULT_MAX_BATCH_CALLS,
    escalation_ratio: float = ESCALATION_THRESHOLD_RATIO,
    source: str = "all",
    adapter_factory: object | None = None,
    # Backward-compat shims: test helpers may pass these kwargs.  # noqa: spend-gate-check
    cost_per_call: float | None = None,
    spend_cap: float | None = None,  # noqa: spend-gate-check
) -> int:
    """Execute the decline-interview backfill: issue API calls and write records.

    T2 scope per Amendment 1 §6. Implements:
    - --source filter (informants / failures / all)
    - should_include_failure() exclusion on failures-origin
    - Pre-flight call-count check at 80% of cap (same gate as dry-run)
    - Sequential execution with per-call progress to stdout
    - Single batch_start detection_timestamp shared across all records (SME A6)
    - Recursive-decline capture and counting (SME binding note 6 + A6)
    - Excluded records logged to stderr with SKIP: prefix

    The SME Amendment 1 authorization checkpoint (binding note A8) is
    preserved as a call-count gate: batches projected to exceed 80% of
    max_batch_calls must surface to the SME on a new Architect plan cycle.

    Args:
        informants_path: Path to informants.jsonl.
        failures_path:   Path to failures.jsonl.
        output_path:     Path to decline_interviews.jsonl (append-only writes).
        verbose:         If True, emit extra diagnostic output.
        max_batch_calls: Maximum API calls permitted in this batch (injectable
                         for tests). Pre-flight fires at 80% of this value.
        escalation_ratio: Fraction of cap at which pre-flight STOP fires.
        source:          Which origin to process: 'informants', 'failures', or 'all'.
        adapter_factory: Optional callable(model_id: str) -> ModelAdapter.
                         When None, uses _build_adapter_for_model (real adapters).
                         Inject a MockAdapter factory in tests — never real API calls.
        cost_per_call:   Ignored. Backward-compat only.
        spend_cap:       Ignored. Backward-compat only.  # noqa: spend-gate-check

    Returns:
        Exit code:
          0 — batch completed cleanly
          1 — IO or parse error
          2 — pre-flight projected calls >= 80% of cap (STOP before any API call)
    """
    # Backward-compat params — ignored at runtime.  # noqa: spend-gate-check
    _ = cost_per_call
    _ = spend_cap  # noqa: spend-gate-check
    # ── Load raw data ──────────────────────────────────────────────────────────
    informant_dicts = _load_jsonl_dicts(informants_path)
    failure_dicts = _load_jsonl_dicts(failures_path)

    # ── Run detection ──────────────────────────────────────────────────────────
    detected_sessions = detect_all(informant_dicts, failure_dicts)

    informants_sessions = [s for s in detected_sessions if s.source == "informants"]
    failures_sessions = [s for s in detected_sessions if s.source == "failures"]

    # ── Build lookup dicts ─────────────────────────────────────────────────────
    informant_by_id: dict[str, dict] = {
        rec.get("informant_id", ""): rec for rec in informant_dicts
    }
    failure_dict_by_id: dict[str, dict] = {
        _failure_identifier(e): e for e in failure_dicts
    }

    # ── Apply source filter + exclusion ────────────────────────────────────────
    work_items: list[tuple[DetectedSession, dict]] = []   # (session, source_entry)
    excluded_sessions: list[tuple[str, str]] = []         # (identifier, rationale)

    if source in ("informants", "all"):
        for session in informants_sessions:
            entry = informant_by_id.get(session.identifier, {})
            work_items.append((session, entry))

    if source in ("failures", "all"):
        for session in failures_sessions:
            entry = failure_dict_by_id.get(session.identifier, {})
            include, rationale = should_include_failure(entry)
            if include:
                work_items.append((session, entry))
            else:
                excluded_sessions.append((session.identifier, rationale))

    # Log excluded records to stderr
    for identifier, rationale in excluded_sessions:
        print(f"SKIP: {identifier} — {rationale}", file=sys.stderr)

    # ── Pre-flight call-count check (same gate as dry-run) ────────────────────
    n_work = len(work_items)
    escalation_threshold_n = int(max_batch_calls * escalation_ratio)

    if n_work >= escalation_threshold_n:
        print(
            f"STOP: projected batch of {n_work} calls >= "
            f"{escalation_threshold_n} (80% of {max_batch_calls} call cap). "
            "Escalate on a new Architect plan cycle per SME binding note 8. "
            "No API calls made.",
            file=sys.stdout,
        )
        return 2

    # ── Resolve adapter factory ────────────────────────────────────────────────
    _get_adapter = (
        adapter_factory if adapter_factory is not None
        else _build_adapter_for_model
    )

    # ── Import execute-path dependencies (lazy — keep dry-run import-clean) ───
    from cdb_collect.jsonl import append_decline_interview
    from cdb_collect.run_decline_interview import run_decline_interview

    # ── Batch start timestamp (SME A6: single timestamp for the entire batch) ──
    batch_start = datetime.now(UTC)

    # ── Execute sequentially ───────────────────────────────────────────────────
    n_total = len(work_items)
    n_written = 0
    n_recursive = 0
    n_version_drift = 0
    latency_ms_list: list[float] = []

    for call_index, (session, source_entry) in enumerate(work_items, 1):
        # Reconstruct task_description and originating_response_verbatim
        if session.source == "informants":
            task_description = _task_description_from_informant(
                source_entry, session.originating_step
            )
            originating_response_verbatim = _response_verbatim_from_informant(
                source_entry, session.originating_step
            )
            originating_informant_id: str | None = session.identifier
            originating_failure_id: str | None = None
            # originating_model_version_returned from the InformantRecord
            orig_model_version = str(source_entry.get("model_version_returned", ""))
            model_id = str(source_entry.get("model_id", ""))
        else:
            # failures-origin
            task_description = _task_description_from_failure(
                source_entry, session.originating_step
            )
            originating_response_verbatim = _response_verbatim_from_failure(source_entry)
            originating_informant_id = None
            originating_failure_id = session.identifier
            ctx = source_entry.get("context", {})
            orig_model_version = ""  # failures.jsonl does not carry model_version_returned
            model_id = str(ctx.get("model_id", ""))

        # Resolve adapter
        try:
            adapter = _get_adapter(model_id)
        except (ValueError, OSError) as exc:
            print(
                f"ERROR: cannot build adapter for model_id={model_id!r}: {exc}",
                file=sys.stderr,
            )
            return 1

        # Invoke the decline interview
        t_start = time.monotonic()
        try:
            interview = asyncio.run(
                run_decline_interview(
                    adapter,
                    task_description=task_description,
                    originating_response_verbatim=originating_response_verbatim,
                    originating_informant_id=originating_informant_id,
                    originating_failure_id=originating_failure_id,
                    originating_step=session.originating_step,
                    originating_outcome_class=session.originating_outcome_class,
                    detection_rule_version="v1",
                    detection_timestamp=batch_start,
                    originating_model_version_returned=orig_model_version,
                )
            )
        except Exception as exc:  # noqa: BLE001
            print(
                f"ERROR: decline interview failed for {session.identifier!r}: {exc}",
                file=sys.stderr,
            )
            return 1
        t_end = time.monotonic()

        call_latency_ms = (t_end - t_start) * 1000.0
        latency_ms_list.append(call_latency_ms)

        if interview.version_drift_flag:
            n_version_drift += 1

        # Recursive-decline detection
        is_recursive = _is_recursive_decline(interview.response_verbatim or "")
        if is_recursive:
            n_recursive += 1
            first_120 = (interview.response_verbatim or "")[:120]
            print(
                f"RECURSIVE_DECLINE: {session.identifier} — {first_120!r}",
                file=sys.stderr,
            )

        # Print per-call progress line
        domain = (
            source_entry.get("domain_slug", "")
            if session.source == "informants"
            else source_entry.get("context", {}).get("domain", "")
        )
        print(
            f"[{call_index}/{n_total}] "
            f"model={model_id} "
            f"domain={domain} "
            f"step={session.originating_step}"
        )

        # Append to output JSONL (append-only)
        append_decline_interview(interview, output_path)
        n_written += 1

    # ── CLI summary ────────────────────────────────────────────────────────────
    print()
    print("===== Execute run summary =====")
    print(f"Source:                       {source}")
    print(f"Records written:              {n_written}")
    print(f"Records excluded:             {len(excluded_sessions)}")
    n_inf_calls = sum(1 for s, _ in work_items if s.source == "informants")
    n_fail_calls = sum(1 for s, _ in work_items if s.source != "informants")
    print(f"Informants-origin calls:      {n_inf_calls}")
    print(f"Failures-origin calls:        {n_fail_calls}")
    print(f"Detection timestamp:          {batch_start.isoformat()}")
    print(f"Version drift flags:          {n_version_drift}")

    if latency_ms_list:
        lat_min = min(latency_ms_list)
        lat_med = statistics.median(latency_ms_list)
        lat_max = max(latency_ms_list)
        print(f"Latency (ms):                 {lat_min:.0f} / {lat_med:.0f} / {lat_max:.0f}")
    else:
        print("Latency (ms):                 N/A")

    print(f"Recursive declines observed:  {n_recursive} (per-record detail to stderr)")
    print()

    return 0


def main() -> int:
    """CLI entry point for run_decline_backfill.py."""
    parser = build_parser()
    args = parser.parse_args()

    if args.execute:
        return run_execute(
            informants_path=args.informants_path,
            failures_path=args.failures_path,
            output_path=args.output_path,
            verbose=args.verbose,
            max_batch_calls=args.max_batch_calls,
            source=args.source,
        )

    if args.dry_run:
        return run_dry_run(
            informants_path=args.informants_path,
            failures_path=args.failures_path,
            output_path=args.output_path,
            verbose=args.verbose,
            max_batch_calls=args.max_batch_calls,
            source=args.source,
        )

    # Should be unreachable (argparse required=True on the group)
    print("ERROR: must specify --dry-run or --execute", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
