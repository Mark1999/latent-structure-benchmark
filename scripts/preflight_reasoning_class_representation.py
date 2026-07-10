"""Pre-promotion checks: reasoning-class and dense-tokenizer roster maintenance.

Implements:
  N6: no-silent-drop verification -- reasoning-class informants must be present
      in each domain alongside non-reasoning informants.
  N11: dense-tokenizer roster detector -- for models not in DENSE_TOKENIZER_MODEL_IDS,
       compute median chars-per-output-token over the first 5 freelist records and
       warn when the value falls outside [2.5, 3.0] (the pre-Claude-5 cluster).
       Warning only; exit code unaffected.

Exit codes:
  0 -- all domain checks pass (or are single-class reasoning-only corpora)
  1 -- at least one domain has zero reasoning-class informants while
       non-reasoning informants are present (class silently dropped)

Usage:
  python scripts/preflight_reasoning_class_representation.py \\
      --domains family,holidays \\
      [--jsonl data/raw/informants.jsonl]
"""

from __future__ import annotations

import argparse
import logging
import statistics
import sys
from pathlib import Path

# Ensure project root is on sys.path when invoked directly (mirrors the
# pattern in runner.py:281 and pipeline.py load_records).
_HERE = Path(__file__).resolve()
_PROJECT_ROOT = _HERE.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cdb_analyze.pipeline import load_records  # noqa: E402

from scripts.qa_check import DENSE_TOKENIZER_MODEL_IDS  # noqa: E402

logger = logging.getLogger(__name__)

_DEFAULT_JSONL = _PROJECT_ROOT / "data" / "raw" / "informants.jsonl"

# N11 thresholds: the pre-Claude-5 cluster occupies [2.5, 3.0] chars/token.
# Models outside this range on their first 5 freelist records should be
# reviewed for possible addition to DENSE_TOKENIZER_MODEL_IDS or a new
# class constant (CDA SME 2026-07-10 addendum N11).
_N11_LOWER_THRESHOLD: float = 2.5
_N11_UPPER_THRESHOLD: float = 3.0
# Number of freelist records to sample for the N11 detector.
_N11_SAMPLE_SIZE: int = 5


def _is_reasoning_record(record: object) -> bool:
    """Return True if any step has thoughts_token_count > 0."""
    for attr in ("freelist", "pile_sort", "interview"):
        step = getattr(record, attr, None)
        if step is not None and getattr(step, "thoughts_token_count", 0) > 0:
            return True
    return False


def check_domain(
    jsonl_path: Path,
    domain_slug: str,
) -> tuple[int, int]:
    """Return (reasoning_count, non_reasoning_count) for QA-passing records."""
    records = load_records(jsonl_path, domain_slug, qa_only=True)
    reasoning = sum(1 for r in records if _is_reasoning_record(r))
    non_reasoning = len(records) - reasoning
    return reasoning, non_reasoning


def detect_dense_tokenizer_candidates(
    jsonl_path: Path,
    domain_slugs: list[str],
) -> list[tuple[str, float]]:
    """N11 detector: compute median chars-per-output-token for models not in roster.

    For each model_id NOT in DENSE_TOKENIZER_MODEL_IDS, gathers the first
    _N11_SAMPLE_SIZE QA-passing freelist records (across all specified domains),
    computes per-record median of len(freelist.response_verbatim) /
    freelist.output_tokens, then takes the median across records.

    Returns a list of (model_id, median_chars_per_token) tuples for models
    whose median falls outside [_N11_LOWER_THRESHOLD, _N11_UPPER_THRESHOLD].
    Models with fewer than 2 usable records are skipped (too few to be
    meaningful).
    """
    # Collect all QA-passing records across the specified domains.
    all_records: list[object] = []
    for domain in domain_slugs:
        all_records.extend(load_records(jsonl_path, domain, qa_only=True))

    # Group by model_id, skip models already in the dense-tokenizer roster.
    by_model: dict[str, list[object]] = {}
    for rec in all_records:
        mid = getattr(rec, "model_id", "")
        if mid in DENSE_TOKENIZER_MODEL_IDS:
            continue
        by_model.setdefault(mid, []).append(rec)

    warnings: list[tuple[str, float]] = []
    for model_id, recs in sorted(by_model.items()):
        # Take the first _N11_SAMPLE_SIZE records (sorted by run_index for stability).
        sample = sorted(recs, key=lambda r: getattr(r, "run_index", 0))[:_N11_SAMPLE_SIZE]

        chars_per_token_values: list[float] = []
        for rec in sample:
            fl = getattr(rec, "freelist", None)
            if fl is None:
                continue
            rv = getattr(fl, "response_verbatim", "")
            out = getattr(fl, "output_tokens", 0)
            if out > 0 and rv:
                chars_per_token_values.append(len(rv) / out)

        if len(chars_per_token_values) < 2:
            continue  # Too few records to be meaningful.

        median_cpt = statistics.median(chars_per_token_values)
        if median_cpt < _N11_LOWER_THRESHOLD or median_cpt > _N11_UPPER_THRESHOLD:
            warnings.append((model_id, median_cpt))

    return warnings


def main(argv: list[str] | None = None) -> int:
    """Run the preflight checks. Returns exit code."""
    parser = argparse.ArgumentParser(
        description=(
            "Verify reasoning-class representation (N6) and "
            "detect dense-tokenizer roster candidates (N11) before corpus promotion."
        )
    )
    parser.add_argument(
        "--domains",
        required=True,
        help="Comma-separated domain slugs to check (e.g. family,holidays).",
    )
    parser.add_argument(
        "--jsonl",
        default=str(_DEFAULT_JSONL),
        help="Path to informants.jsonl (default: data/raw/informants.jsonl).",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s -- %(message)s",
    )

    jsonl_path = Path(args.jsonl)
    domains = [d.strip() for d in args.domains.split(",") if d.strip()]

    # N6: reasoning-class representation check.
    any_fail = False
    for domain in domains:
        reasoning, non_reasoning = check_domain(jsonl_path, domain)
        total = reasoning + non_reasoning

        if total == 0:
            print(f"[{domain}] SKIP -- no QA-passing records found")
            continue

        if non_reasoning == 0:
            # Single-class reasoning-only corpus: no silent drop possible.
            print(
                f"[{domain}] SKIP -- {reasoning} reasoning-class records, "
                f"0 non-reasoning records (single-class corpus)"
            )
            continue

        if reasoning == 0:
            # Non-reasoning records exist but reasoning class is absent: class dropped.
            print(
                f"[{domain}] FAIL -- 0 reasoning-class records present, "
                f"{non_reasoning} non-reasoning records. "
                f"Reasoning class is silently absent (N6 violation)."
            )
            any_fail = True
        else:
            print(
                f"[{domain}] PASS -- {reasoning} reasoning-class, "
                f"{non_reasoning} non-reasoning records in QA-passing corpus"
            )

    # N11: dense-tokenizer roster-maintenance detector (warning only, exit unaffected).
    dense_warnings = detect_dense_tokenizer_candidates(jsonl_path, domains)
    for model_id, median_cpt in dense_warnings:
        print(
            f"[N11 WARNING] {model_id}: median chars/token = {median_cpt:.2f} "
            f"is outside the pre-Claude-5 cluster [{_N11_LOWER_THRESHOLD}, "
            f"{_N11_UPPER_THRESHOLD}]. Review for addition to "
            f"DENSE_TOKENIZER_MODEL_IDS or a new class constant."
        )

    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
