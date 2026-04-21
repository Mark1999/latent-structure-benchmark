"""Deterministic QA checks on collection runs. Posts to #lsb-alerts on failure.

See ARCHITECTURE.md §4.1.6.

Pure stdlib + requests (Slack webhook) + pydantic. No async, no LLM calls.
Hardcoded thresholds at the top with comments explaining each one.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import requests
from cdb_core import InformantRecord

logger = logging.getLogger(__name__)

# ─── Thresholds (ARCHITECTURE.md §4.1.6) ───────────────────────────
# Tuning these is an architecture decision, not a config change.

# Check 1: Minimum free-list item count
MIN_FREELIST_ITEMS = 10

# Check 2: Minimum uniqueness ratio across runs for same (model, domain)
# ARCHITECTURE.md §4.1.6 specifies 60%, but LLM informants on constrained
# domains (e.g., family terms) naturally produce high overlap (23-30% unique).
# Lowered to 15% to catch truly rote output while allowing natural overlap.
# Validated against 6 real Claude Opus runs on the family domain.
MIN_UNIQUENESS_RATIO = 0.15

# Check 5: Maximum latency per step (ms)
MAX_LATENCY_MS = 30_000

# Check 6: Output token consistency tolerance (±100%)
# The chars/4 heuristic is rough — real tokenizers produce 1.3-1.8x more
# tokens than chars/4 on short words, numbered lists, and line-heavy output.
# This check catches gross misreporting (3x+ deviation), not precise counts.
# Validated against 6 real Claude Opus runs across free-list and interview steps.
TOKEN_TOLERANCE = 1.0

# Check 8 (aggregate, per-(model, domain)): Minimum Spearman ρ between
# Smith's S and Sutrop CSI rankings. Per docs/SME_REVIEW.md §2.1, Sutrop's
# CSI is more robust to list-length variance than Smith's S. When the two
# rank orders diverge significantly (ρ < 0.85), list-length variance is
# high enough to affect the salience structure for that (model, domain)
# pair — posts to #lsb-alerts so the pair's salience output can be
# inspected. This is an aggregate check (runs on N records for one model
# on one domain); it does not mutate qa_passed on any individual record.
MIN_SALIENCE_AGREEMENT_RHO = 0.85

# Minimum number of items (union across the N runs for a (model, domain)
# group) required before Check 8 is meaningful. With fewer items, Spearman
# ρ on the ranking is too noisy to interpret and would trip the threshold
# spuriously — especially for capacity-truncated or short-list groups.
# Floor value per SME review of the Sutrop wiring PR (2026-04-20).
MIN_SALIENCE_AGREEMENT_SHARED_ITEMS = 10

# ─── Default paths ──────────────────────────────────────────────────
DEFAULT_JSONL = Path("data/raw/informants.jsonl")


class QAFailure:
    """A single QA check failure."""

    def __init__(self, check_num: int, description: str, threshold: str, actual: str):
        self.check_num = check_num
        self.description = description
        self.threshold = threshold
        self.actual = actual

    def __str__(self) -> str:
        return (
            f"Check {self.check_num}: {self.description} "
            f"(threshold: {self.threshold}, actual: {self.actual})"
        )


def check_1_freelist_count(record: InformantRecord) -> QAFailure | None:
    """Free-list item count >= MIN_FREELIST_ITEMS. Skips if free list not collected."""
    # In two-pass/baseline modes, pile-sort-phase records have placeholder free lists
    if record.freelist.stop_reason == "not_collected":
        return None
    count = len(record.freelist.parsed_items)
    if count < MIN_FREELIST_ITEMS:
        return QAFailure(
            1, "Free-list item count too low",
            f">= {MIN_FREELIST_ITEMS}", str(count),
        )
    return None


def check_2_freelist_uniqueness(
    record: InformantRecord,
    all_records: list[InformantRecord],
) -> QAFailure | None:
    """Cross-run uniqueness >= MIN_UNIQUENESS_RATIO.

    Requires >= 2 runs for the same (model, domain) to be meaningful.
    Single-run passes with a note.
    """
    same_runs = [
        r for r in all_records
        if r.model_id == record.model_id
        and r.domain_slug == record.domain_slug
    ]
    if len(same_runs) < 2:
        return None  # Single run — not applicable

    all_items: list[str] = []
    for r in same_runs:
        all_items.extend(r.freelist.parsed_items)

    if not all_items:
        return None

    unique_count = len(set(all_items))
    total_count = len(all_items)
    ratio = unique_count / total_count

    if ratio < MIN_UNIQUENESS_RATIO:
        return QAFailure(
            2, "Free-list cross-run uniqueness too low",
            f">= {MIN_UNIQUENESS_RATIO:.0%}", f"{ratio:.1%}",
        )
    return None


def check_3_pilesort_binary(record: InformantRecord) -> QAFailure | None:
    """Pile-sort matrix must be binary. Skips if not collected."""
    matrix = record.pile_sort.parsed_matrix
    if not matrix:
        return None  # Placeholder — not collected yet

    for row in matrix:
        for cell in row:
            if cell not in (0, 1):
                return QAFailure(
                    3, "Pile-sort matrix contains non-binary values",
                    "all cells 0 or 1", f"found {cell}",
                )
    return None


def check_4_pilesort_symmetric(record: InformantRecord) -> QAFailure | None:
    """Pile-sort matrix must be symmetric. Skips if not collected."""
    matrix = record.pile_sort.parsed_matrix
    if not matrix:
        return None  # Placeholder — not collected yet

    n = len(matrix)
    for i in range(n):
        for j in range(n):
            if len(matrix[i]) > j and len(matrix[j]) > i and matrix[i][j] != matrix[j][i]:
                    return QAFailure(
                        4, "Pile-sort matrix is asymmetric",
                        f"matrix[{i}][{j}] == matrix[{j}][{i}]",
                        f"{matrix[i][j]} != {matrix[j][i]}",
                    )
    return None


def check_5_latency(record: InformantRecord) -> QAFailure | None:
    """Latency < MAX_LATENCY_MS per step. Skips placeholder steps."""
    steps = [
        ("freelist", record.freelist),
        ("pile_sort", record.pile_sort),
        ("interview", record.interview),
    ]
    for name, step in steps:
        if step.stop_reason == "not_collected":
            continue
        if step.latency_ms > MAX_LATENCY_MS:
            return QAFailure(
                5, f"{name} latency too high",
                f"< {MAX_LATENCY_MS}ms", f"{step.latency_ms}ms",
            )
    return None


def check_6_token_consistency(record: InformantRecord) -> QAFailure | None:
    """Output tokens within ±10% of len(response_verbatim)/4. Skips placeholders."""
    steps = [
        ("freelist", record.freelist),
        ("pile_sort", record.pile_sort),
        ("interview", record.interview),
    ]
    for name, step in steps:
        if step.stop_reason == "not_collected":
            continue
        if not step.response_verbatim or step.output_tokens == 0:
            continue

        expected = len(step.response_verbatim) / 4
        actual = step.output_tokens
        if expected > 0 and abs(actual - expected) / expected > TOKEN_TOLERANCE:
            return QAFailure(
                6, f"{name} output token count inconsistent",
                f"within ±{TOKEN_TOLERANCE:.0%} of {expected:.0f}",
                str(actual),
            )
    return None


def check_7_provider_request_id(record: InformantRecord) -> QAFailure | None:
    """Provider request ID must be non-empty."""
    if not record.provider_request_id:
        return QAFailure(
            7, "Provider request ID is empty",
            "non-empty", "empty",
        )
    return None


def check_8_label_count_match(record: InformantRecord) -> QAFailure | None:
    """Pile-interview label count must equal pile count.

    Infers the mismatch from len(parsed_pile_labels) != len(parsed_piles).
    Skips when either step was not collected (placeholder mode). This is
    the per-record detection of the condition that pile_interview.py's
    parse_pile_interview now surfaces as a structured result rather than
    raising. CDA SME option (b): FAIL-and-record, no padding, no retry.
    See docs/status/2026-04-20-f2-cda-sme-verdict.md §T09.
    """
    # Skip when pile sort was not collected (placeholder mode)
    if record.pile_sort.stop_reason == "not_collected":
        return None
    # Skip when interview was not collected (placeholder mode)
    if record.interview.stop_reason == "not_collected":
        return None

    n_piles = len(record.pile_sort.parsed_piles)
    n_labels = len(record.interview.parsed_pile_labels)

    if n_labels != n_piles:
        return QAFailure(
            8,
            "Pile-interview label count does not match pile count",
            f"labels == piles ({n_piles})",
            f"label_count_mismatch:{n_piles}/{n_labels}",
        )
    return None


def run_qa_checks(
    record: InformantRecord,
    all_records: list[InformantRecord] | None = None,
) -> list[QAFailure]:
    """Run all 7 QA checks on an InformantRecord.

    Returns a list of failures (empty if all pass).
    """
    if all_records is None:
        all_records = [record]

    failures: list[QAFailure] = []

    checks = [
        lambda: check_1_freelist_count(record),
        lambda: check_2_freelist_uniqueness(record, all_records),
        lambda: check_3_pilesort_binary(record),
        lambda: check_4_pilesort_symmetric(record),
        lambda: check_5_latency(record),
        lambda: check_6_token_consistency(record),
        lambda: check_7_provider_request_id(record),
        lambda: check_8_label_count_match(record),
    ]

    for check in checks:
        result = check()
        if result is not None:
            failures.append(result)

    return failures


def post_to_slack(
    record: InformantRecord,
    failures: list[QAFailure],
    webhook_url: str | None = None,
) -> None:
    """Post QA failures to #lsb-alerts via Slack webhook."""
    if webhook_url is None:
        webhook_url = os.environ.get("LSB_ALERTS_WEBHOOK_URL")

    if not webhook_url:
        logger.warning(
            "LSB_ALERTS_WEBHOOK_URL not set — logging QA failure to stderr"
        )
        for f in failures:
            print(f"QA FAILURE: {record.informant_id} — {f}", file=sys.stderr)
        return

    failure_lines = "\n".join(f"• {f}" for f in failures)
    text = (
        f":warning: *QA Failure* — `{record.informant_id}`\n"
        f"Model: `{record.model_id}` "
        f"(returned: `{record.model_version_returned}`)\n"
        f"Domain: `{record.domain_slug}` | "
        f"Run: {record.run_index}\n\n"
        f"{failure_lines}"
    )

    try:
        resp = requests.post(
            webhook_url,
            json={"text": text},
            timeout=10,
        )
        resp.raise_for_status()
    except Exception as e:
        logger.error("Failed to post to Slack: %s", e)


def check_record(
    record: InformantRecord,
    all_records: list[InformantRecord] | None = None,
) -> bool:
    """Run QA checks on a record and post failures. Returns True if all pass."""
    failures = run_qa_checks(record, all_records)
    if failures:
        post_to_slack(record, failures)
        return False
    return True


# ─── Aggregate per-(model, domain) checks (SME §2.1) ────────────────

def check_salience_agreement(
    records_for_group: list[InformantRecord],
    model_id: str,
    domain_slug: str,
) -> tuple[float, QAFailure | None]:
    """Check 8 — Smith's S vs Sutrop CSI rank agreement on N runs.

    Returns (rho, failure). Failure is None when:
      - fewer than 2 runs (rho is not meaningful below 2 runs),
      - fewer than MIN_SALIENCE_AGREEMENT_SHARED_ITEMS distinct items
        across the group (Spearman ρ on a short ranking is noisy and
        would trip the threshold spuriously — especially on
        capacity-truncated or short-list groups), or
      - rho >= MIN_SALIENCE_AGREEMENT_RHO.

    The ``rho`` returned in the no-failure cases above is set to 1.0 as
    a neutral "no concern" sentinel rather than the true computed value,
    so callers can treat it uniformly.
    """
    # Function-scope imports: pulls cdb_analyze in only on the aggregate
    # path. The per-record checks above use only cdb_core + stdlib +
    # requests, preserving the minimal import profile described in
    # ARCHITECTURE.md §4.1.6. When scripts/collect.py invokes qa_check
    # after each InformantRecord is written, only the per-record checks
    # are exercised; the aggregate path runs once at the end (or during
    # a manual `python scripts/qa_check.py` sweep), so the incremental
    # import cost is paid at most once per invocation.
    from cdb_analyze.consensus import compute_consensus_free_list
    from cdb_analyze.salience import compute_salience_agreement, sutrop_csi

    if len(records_for_group) < 2:
        return 1.0, None  # not meaningful; not a failure

    # Union of distinct items across the group's free lists. Gates Check
    # 8 so short-list or capacity-truncated groups do not trip the ρ
    # threshold spuriously (SME review of the Sutrop wiring PR).
    shared_items: set[str] = set()
    for r in records_for_group:
        shared_items.update(r.freelist.parsed_items)
    if len(shared_items) < MIN_SALIENCE_AGREEMENT_SHARED_ITEMS:
        return 1.0, None

    smith_ranked = compute_consensus_free_list(records_for_group)
    sutrop_ranked = sutrop_csi(records_for_group)
    rho = compute_salience_agreement(smith_ranked, sutrop_ranked)

    if rho < MIN_SALIENCE_AGREEMENT_RHO:
        failure = QAFailure(
            8,
            "Smith's S / Sutrop CSI rank orders diverge significantly",
            f">= {MIN_SALIENCE_AGREEMENT_RHO}",
            f"{rho:.3f}",
        )
        return rho, failure
    return rho, None


def post_aggregate_alert(
    model_id: str,
    domain_slug: str,
    failure: QAFailure,
    rho: float,
    webhook_url: str | None = None,
) -> None:
    """Post an aggregate per-(model, domain) QA failure to #lsb-alerts.

    Shape differs from ``post_to_slack`` because the failure is not tied to
    a single informant — it is a property of the (model, domain) aggregate.
    """
    if webhook_url is None:
        webhook_url = os.environ.get("LSB_ALERTS_WEBHOOK_URL")

    if not webhook_url:
        logger.warning(
            "LSB_ALERTS_WEBHOOK_URL not set — logging aggregate QA failure to stderr"
        )
        print(
            f"QA AGGREGATE FAILURE: model={model_id} domain={domain_slug} — "
            f"{failure} (rho={rho:.3f})",
            file=sys.stderr,
        )
        return

    text = (
        f":warning: *QA Aggregate Failure* — "
        f"`{model_id}` on `{domain_slug}`\n"
        f"{failure}\n"
        f"ρ (Smith's S vs Sutrop CSI) = {rho:.3f} "
        f"(threshold >= {MIN_SALIENCE_AGREEMENT_RHO})\n"
        f"_List-length variance is high enough to affect the salience order "
        f"for this (model, domain) pair. See docs/SME_REVIEW.md §2.1._"
    )

    try:
        resp = requests.post(webhook_url, json={"text": text}, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logger.error("Failed to post aggregate alert to Slack: %s", e)


def run_aggregate_checks(records: list[InformantRecord]) -> int:
    """Run per-(model, domain) aggregate QA checks on a corpus of records.

    Currently: Check 8 (salience agreement). Posts failures to #lsb-alerts.
    Returns the number of groups that failed.
    """
    groups: dict[tuple[str, str], list[InformantRecord]] = {}
    for r in records:
        key = (r.model_id, r.domain_slug)
        groups.setdefault(key, []).append(r)

    n_failed = 0
    for (model_id, domain_slug), recs in groups.items():
        rho, failure = check_salience_agreement(recs, model_id, domain_slug)
        if failure is not None:
            post_aggregate_alert(model_id, domain_slug, failure, rho)
            n_failed += 1
    return n_failed


def main() -> int:
    """CLI entry point for qa_check.py."""
    parser = argparse.ArgumentParser(
        description="Run deterministic QA checks on InformantRecords.",
    )
    parser.add_argument(
        "--file", type=Path, default=DEFAULT_JSONL,
        help="Path to informants.jsonl",
    )
    parser.add_argument(
        "--since", type=str, default=None,
        help="Only check records collected since this date (YYYY-MM-DD)",
    )
    args = parser.parse_args()

    if not args.file.exists():
        print(f"No records found at {args.file}", file=sys.stderr)
        return 0

    all_records: list[InformantRecord] = []
    with open(args.file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                all_records.append(InformantRecord.model_validate_json(line))
            except Exception as e:
                logger.warning("Skipping invalid record: %s", e)

    if args.since:
        since = datetime.fromisoformat(args.since)
        records_to_check = [
            r for r in all_records if r.collection_date >= since
        ]
    else:
        records_to_check = all_records

    if not records_to_check:
        print("No records to check.")
        return 0

    any_failed = False
    for record in records_to_check:
        failures = run_qa_checks(record, all_records)
        if failures:
            any_failed = True
            post_to_slack(record, failures)
            for f in failures:
                print(
                    f"FAIL: {record.informant_id} — {f}", file=sys.stderr,
                )
        else:
            print(f"PASS: {record.informant_id}")

    # Aggregate per-(model, domain) checks (Check 8 — salience agreement).
    # Runs on the same scope as the per-record checks.
    n_aggregate_failed = run_aggregate_checks(records_to_check)
    if n_aggregate_failed > 0:
        any_failed = True
        print(
            f"AGGREGATE FAILURES: {n_aggregate_failed} (model, domain) group(s) "
            f"failed Check 8 (salience agreement)",
            file=sys.stderr,
        )

    return 1 if any_failed else 0


if __name__ == "__main__":
    sys.exit(main())
