"""Phase 4a.1 decline-interview backfill runner — enumeration and dry-run (T1 scope).

This script reads informants.jsonl and failures.jsonl, invokes the deterministic
decline-detection module, and reports the detected session set without making any
API calls (--dry-run mode).

T1 delivers the --dry-run path only. The --execute path is T2 scope; its handler
body raises NotImplementedError with a pointer to the plan document.

References:
  Architect plan:  docs/status/2026-04-23-phase4a1-architect-plan.md
  SME verdict:     docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md

SME binding notes satisfied in this file:
  Note 1 — per-record not-triggered reasoning (Section 3 of --dry-run output)
  Note 8 — Gemini failures count + cost-guard line (Section 4 of --dry-run output)

Exit codes:
  0  — dry-run completed cleanly
  1  — IO or parse error
  2  — projected spend >= 80 % of $2 cap; escalation required
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from cdb_collect.decline_detection import (
    DetectedSession,
    _failure_identifier,
    detect_all,
    detect_from_failure,
)

# ── Cost constants (editable for test injection) ──────────────────────────────
COST_PER_CALL_USD: float = 0.05
SPEND_CAP_USD: float = 2.00
ESCALATION_THRESHOLD_RATIO: float = 0.80  # 80 % of cap

# ── Default paths (all relative to repo root) ─────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INFORMANTS_PATH = _REPO_ROOT / "data" / "raw" / "informants.jsonl"
DEFAULT_FAILURES_PATH = _REPO_ROOT / "data" / "raw" / "failures.jsonl"
DEFAULT_OUTPUT_PATH = _REPO_ROOT / "data" / "raw" / "decline_interviews.jsonl"


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
    cost_per_call: float = COST_PER_CALL_USD,
    spend_cap: float = SPEND_CAP_USD,
    escalation_ratio: float = ESCALATION_THRESHOLD_RATIO,
) -> int:
    """Execute the dry-run: enumerate detected sessions and print the report.

    Touches only stdout. No file writes. No network calls.

    Args:
        informants_path: Path to informants.jsonl.
        failures_path:   Path to failures.jsonl.
        output_path:     Declared output path (not written; present for T2 symmetry).
        verbose:         If True, emit per-record rows in the not-triggered section
                         even when the count is zero.
        cost_per_call:   Estimated cost per API call in USD (injectable for tests).
        spend_cap:       Hard spend cap in USD (injectable for tests).
        escalation_ratio: Fraction of cap at which cost-guard escalation fires.

    Returns:
        Exit code: 0 on success, 2 on cost-guard escalation.
    """
    # ── Load raw data ──────────────────────────────────────────────────────────
    informant_dicts = _load_jsonl_dicts(informants_path)
    failure_dicts = _load_jsonl_dicts(failures_path)

    # ── Run detection ──────────────────────────────────────────────────────────
    detected_sessions = detect_all(informant_dicts, failure_dicts)

    # Build per-informant lookup for triggered IDs
    triggered_ids: set[str] = {s.identifier for s in detected_sessions}

    # ── Collect "not triggered" informant records ──────────────────────────────
    # Only qa_passed=False records that detect_from_informant returned None for.
    not_triggered_informant: list[dict] = []
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
    for entry in failure_dicts:
        fid_session = detect_from_failure(entry)
        if fid_session is None:
            not_triggered_failure.append(entry)

    # ── Section 1 — Summary table (grouped) ───────────────────────────────────
    print("=" * 72)
    print("SECTION 1 — TRIGGERED SESSIONS SUMMARY")
    print("=" * 72)

    GroupKey = tuple[str, str, str, str]  # (source, originating_step, outcome_class, model_id)
    group_counts: dict[GroupKey, int] = defaultdict(int)

    for session in detected_sessions:
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
        for (source, step, outcome, model_id), count in sorted(group_counts.items()):
            print(
                f"{source:<{col_widths[0]}}"
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

    if detected_sessions:
        for session in detected_sessions:
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

    s3_col = (20, 35, 12, 45)
    s3_header = (
        f"{'id':<{s3_col[0]}}"
        f"{'model_id':<{s3_col[1]}}"
        f"{'domain':<{s3_col[2]}}"
        f"{'failing_checks':<{s3_col[3]}}"
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
        reason = _not_triggered_reason(failing_checks)
        checks_str = ", ".join(failing_checks) if failing_checks else "(none parsed)"

        print(
            f"{iid:<{s3_col[0]}}"
            f"{model_id:<{s3_col[1]}}"
            f"{domain:<{s3_col[2]}}"
            f"{checks_str:<{s3_col[3]}}  "
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
        reason = "detect_from_failure returned None (unexpected; inspect entry)"
        print(
            f"{fid:<{s3_col[0]}}"
            f"{model_id:<{s3_col[1]}}"
            f"{domain:<{s3_col[2]}}"
            f"{checks_str:<{s3_col[3]}}  "
            f"{reason}"
        )
        not_triggered_count += 1

    if not_triggered_count == 0 and not verbose:
        print("(no not-triggered records)")
    print()

    # ── Section 4 — Gemini failures count (SME binding note 8) ────────────────
    print("=" * 72)
    print("SECTION 4 — GEMINI FAILURES COUNT (SME binding note 8)")
    print("=" * 72)

    gemini_entries = [e for e in failure_dicts if _is_gemini_failure(e)]
    gemini_detected = [
        e for e in gemini_entries if detect_from_failure(e) is not None
    ]
    total_detected = len(detected_sessions)
    projected_cost = total_detected * cost_per_call
    escalation_threshold = spend_cap * escalation_ratio

    print(f"Total Gemini failure entries:        {len(gemini_entries)}")
    print(f"Gemini entries detected (triggering): {len(gemini_detected)}")
    print(f"Gemini entries not detected:          {len(gemini_entries) - len(gemini_detected)}")
    print()

    cost_status = (
        "ESCALATE — see STOP line below"
        if projected_cost >= escalation_threshold
        else "OK"
    )
    print(
        f"Projected batch size: {total_detected} detected "
        f"x ~${cost_per_call:.2f}/call "
        f"= ~${projected_cost:.2f} total. "
        f"[{cost_status}]"
    )
    print()

    escalate = False
    if projected_cost >= escalation_threshold:
        print(
            f"STOP: projected batch at or above 80% of ${spend_cap:.2f} spend cap "
            f"(projected=${projected_cost:.2f} >= threshold=${escalation_threshold:.2f}). "
            "Escalate on a new Architect plan cycle per SME binding note 8."
        )
        escalate = True
    print()

    # ── Section 5 — Totals ────────────────────────────────────────────────────
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

    if escalate:
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
            "See docs/status/2026-04-23-phase4a1-architect-plan.md for full spec."
        ),
    )

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help=(
            "Enumerate detected sessions and print summary. "
            "No API calls. No file writes. Exit 0 on success, 2 on cost-guard escalation."
        ),
    )
    mode_group.add_argument(
        "--execute",
        action="store_true",
        dest="execute",
        help="(T2 scope) Run the full backfill. Not implemented yet.",
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


def main() -> int:
    """CLI entry point for run_decline_backfill.py."""
    parser = build_parser()
    args = parser.parse_args()

    if args.execute:
        raise NotImplementedError(
            "--execute is T2 scope; see docs/status/2026-04-23-phase4a1-architect-plan.md §3 T2"
        )

    if args.dry_run:
        return run_dry_run(
            informants_path=args.informants_path,
            failures_path=args.failures_path,
            output_path=args.output_path,
            verbose=args.verbose,
        )

    # Should be unreachable (argparse required=True on the group)
    print("ERROR: must specify --dry-run or --execute", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
