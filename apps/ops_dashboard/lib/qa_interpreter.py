"""QA-notes interpreter for the LSB Internal Ops Dashboard (OPS-T7).

Parses the semicolon-joined qa_notes string produced by
packages/cdb_collect/cdb_collect/runner.py and returns a structured
interpretation for each recognised failure shorthand.

The qa_notes format (from runner.py:278-280):
    "; ".join(f.actual for f in failures) + optional trailing "; {campaign_id_tag}"

Where the `actual` field of each QAFailure is one of:
    - bare integer       -> check 1 (freelist_too_low) OR check 6 (token_inconsistency)
                           OR the trailing campaign-id tag
    - "N.N%"             -> check 2 (uniqueness_too_low)
    - "found N"          -> check 3 (matrix_non_binary)
    - "A != B"           -> check 4 (matrix_asymmetric)
    - "Nms"              -> check 5 (latency_exceeded)
    - "empty"            -> check 7 (empty_request_id)
    - "label_count_mismatch:N/M" -> check 8 (label_count_mismatch)

Bare-integer disambiguation (CDA SME option (iii), binding):
    - bare integer as the ONLY segment -> freelist_too_low (check 1)
    - bare integer as a TRAILING segment after other shorthands ->
      token_inconsistency_or_campaign_tag (ambiguous; both readings in impact)

NOTE: this position-based heuristic is a transitional measure. When the
runner-side prefix follow-up task lands (check5:60124ms, check6:4779, tag:171),
the disambiguation branch in this module becomes redundant and should be
retired. See docs/status/2026-05-06-OPS-T7-cda-sme-verdict.md §Q1 option (iv).

READ-ONLY INVARIANT: pure helper — no I/O, no file opens, no LLM client
imports, no imports from cdb_collect / cdb_analyze / cdb_publish / cdb_social.

See ARCHITECTURE.md §1.5 (framing — binding on all rendered text),
CLAUDE.md §7 (forbidden vocabulary).
CDA SME binding notes: docs/status/2026-05-06-OPS-T7-cda-sme-verdict.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class QaInterpretation:
    """Structured interpretation of one qa_notes failure segment.

    Attributes:
        code: Machine-readable classification code (e.g. "latency_exceeded").
        why: Operator-facing plain-language explanation of why the check failed.
        impact: Operator-facing plain-language description of the analysis impact.
        raw_segment: The verbatim segment from qa_notes for traceability.
    """

    code: str
    why: str
    impact: str
    raw_segment: str


# ── Interpretation table ──────────────────────────────────────────────────────
# Each entry maps a pattern (regex string) to (code, why, impact).
# Patterns are tested in the order listed. The first match wins.
# Wording approved verbatim by CDA SME — see verdict §Q1 for rationale.
# Three rows were reworded from the Architect draft (freelist_too_low,
# uniqueness_too_low, token_inconsistency).

_INTERPRETATION_TABLE: list[tuple[str, str, str, str]] = [
    # (regex_pattern, code, why, impact)

    # Check 5 — step latency exceeded (e.g. "60124ms")
    (
        r"^\d+ms$",
        "latency_exceeded",
        "Step latency exceeded the 60-second ceiling.",
        (
            "Run is usable for raw inspection. Aggregate latency-sensitive analyses "
            "(per-step timing distributions) should exclude or flag this run."
        ),
    ),

    # Check 8 — pile-label count mismatch (e.g. "label_count_mismatch:20/9")
    (
        r"^label_count_mismatch:(\d+)/(\d+)$",
        "label_count_mismatch",
        (
            "The number of piles in Step 2 did not match the number of pile labels "
            "in Step 3."
        ),
        (
            "Pile-naming alignment is broken for this run. "
            "Co-occurrence matrix is still well-formed and usable for MDS/clustering. "
            "Pile-label-dependent visualizations and any downstream label-keyed "
            "analysis must skip this run."
        ),
    ),

    # Check 2 — cross-run uniqueness too low (e.g. "12.3%")
    (
        r"^\d+(\.\d+)?%$",
        "uniqueness_too_low",
        "Cross-run vocabulary uniqueness for this (model, domain) pair fell below 15%.",
        (
            "Aggregate concern, computed across the >=2 runs for this (model, domain) "
            "group — not on this single record. The group's salience structure may "
            "reflect rote output rather than independent elicitation across runs. "
            "Single-run analyses on this record are unaffected; cross-run group "
            "analyses warrant inspection."
        ),
    ),

    # Check 3 — pile-sort matrix contains non-binary value (e.g. "found 2")
    (
        r"^found .+$",
        "matrix_non_binary",
        "Pile-sort matrix contains a non-binary cell value.",
        (
            "Co-occurrence matrix is malformed; this run is unsafe for any "
            "pile-sort-derived analysis."
        ),
    ),

    # Check 4 — pile-sort matrix asymmetric (e.g. "0 != 1")
    (
        r"^\d+ != \d+$",
        "matrix_asymmetric",
        "Pile-sort matrix is asymmetric.",
        (
            "Co-occurrence matrix is malformed; this run is unsafe for any "
            "pile-sort-derived analysis."
        ),
    ),

    # Check 7 — provider request ID empty (literal "empty")
    (
        r"^empty$",
        "empty_request_id",
        "Provider did not return a request_id.",
        (
            "Provenance audit path through the provider's logs is unavailable for "
            "this run. Local SHA256 manifest still anchors the data."
        ),
    ),
]

# Bare-integer patterns (used separately for disambiguation logic)
_BARE_INT_RE = re.compile(r"^\d+$")

# Pre-compiled patterns from the table
_COMPILED_TABLE: list[tuple[re.Pattern[str], str, str, str]] = [
    (re.compile(pattern), code, why, impact)
    for pattern, code, why, impact in _INTERPRETATION_TABLE
]


def _is_non_bare_int(segment: str) -> bool:
    """Return True when segment matches any table pattern that is NOT the bare-int case."""
    return any(rx.match(segment) for rx, _code, _why, _impact in _COMPILED_TABLE)


def interpret_qa_notes(qa_notes: str) -> list[QaInterpretation]:
    """Parse a qa_notes string and return one QaInterpretation per segment.

    Applies the CDA SME-approved bare-integer disambiguation (option iii):
    - A bare integer as the ONLY segment is interpreted as freelist_too_low.
    - A bare integer as a TRAILING segment (after at least one other shorthand)
      is interpreted as token_inconsistency_or_campaign_tag (ambiguous).
    - A bare integer in any other position (not trailing) is treated as
      freelist_too_low if it is the only unclassified segment up to that point,
      else as token_inconsistency_or_campaign_tag.

    In practice: the runner assembles qa_notes as failures in check order (1-8),
    then appends the campaign-id tag last. So:
    - Only segment bare int -> check 1 (freelist_too_low)
    - Trailing segment bare int (after other shorthands) -> ambiguous

    Args:
        qa_notes: The qa_notes string from InformantRecord. May be empty.

    Returns:
        List of QaInterpretation objects, one per recognised segment.
        Empty list for empty input or input containing only the campaign tag
        when it appears as the only segment (interpreted as freelist_too_low —
        the only-segment bare-integer maps to freelist_too_low by heuristic).
    """
    if not qa_notes or not qa_notes.strip():
        return []

    segments = [s.strip() for s in qa_notes.split(";") if s.strip()]
    if not segments:
        return []

    results: list[QaInterpretation] = []

    # Determine which segments are non-bare-int (i.e., clearly classified)
    non_bare_int_positions: set[int] = set()
    for i, seg in enumerate(segments):
        if _is_non_bare_int(seg):
            non_bare_int_positions.add(i)

    for i, segment in enumerate(segments):
        # Try non-bare-int patterns first
        matched = False
        for rx, code, why, impact in _COMPILED_TABLE:
            if rx.match(segment):
                results.append(QaInterpretation(
                    code=code,
                    why=why,
                    impact=impact,
                    raw_segment=segment,
                ))
                matched = True
                break

        if matched:
            continue

        # Check if this is a bare integer
        if _BARE_INT_RE.match(segment):
            is_last = (i == len(segments) - 1)
            has_other_non_bare_int_before = bool(non_bare_int_positions & set(range(i)))

            if is_last and has_other_non_bare_int_before:
                # Trailing bare integer after other recognised shorthands: ambiguous
                results.append(QaInterpretation(
                    code="token_inconsistency_or_campaign_tag",
                    why=(
                        "Trailing bare integer — cannot be unambiguously classified "
                        "from the qa_notes string alone."
                    ),
                    impact=(
                        "Either (a) provider-reported output token count deviates "
                        ">100% from the chars/4 heuristic — heuristic-only flag, run "
                        "remains usable; or (b) the trailing segment is a campaign-id "
                        "tag appended by the runner — not a failure. The two cases "
                        "cannot be distinguished from the qa_notes string alone. "
                        "Inspect the run's raw record to disambiguate."
                    ),
                    raw_segment=segment,
                ))
            else:
                # Only segment, or non-trailing bare integer: freelist_too_low
                results.append(QaInterpretation(
                    code="freelist_too_low",
                    why="Freelist returned fewer than 10 items.",
                    impact=(
                        "Salience measures (Smith's S, Sutrop CSI) computed on this "
                        "run are unreliable. Operator should exclude or flag this run "
                        "when computing grouped salience; the analysis pipeline does "
                        "not currently filter on `qa_passed` automatically."
                    ),
                    raw_segment=segment,
                ))
            continue

        # Unrecognised segment
        results.append(QaInterpretation(
            code="unknown",
            why="Unrecognized QA-failure shorthand. See `scripts/qa_check.py`.",
            impact="Operator must read the source to resolve.",
            raw_segment=segment,
        ))

    return results
