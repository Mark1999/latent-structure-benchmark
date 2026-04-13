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
MIN_UNIQUENESS_RATIO = 0.60

# Check 5: Maximum latency per step (ms)
MAX_LATENCY_MS = 30_000

# Check 6: Output token consistency tolerance (±60%)
# The chars/4 heuristic is rough — real tokenizers vary significantly
# (Claude's tokenizer produces ~1.5-2x more tokens than chars/4 on short
# words and line-heavy output). This check catches gross misreporting
# (e.g., provider reports 10x the actual tokens), not precise counts.
TOKEN_TOLERANCE = 0.60

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
    """Free-list item count >= MIN_FREELIST_ITEMS."""
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
    with open(args.file) as f:
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

    return 1 if any_failed else 0


if __name__ == "__main__":
    sys.exit(main())
