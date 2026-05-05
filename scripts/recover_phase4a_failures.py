"""Phase 4a recovery script — retry budget + idempotence + dry-run.

Reads ``data/raw/failures.jsonl``, identifies the 20 in-scope failure
cells from Phase 4a (google/gemini-2.5-pro, z-ai/glm-5.1,
meta-llama/llama-4-maverick), and re-attempts each cell with a 2-attempt
retry budget at the bumped ``max_tokens=16384`` cap introduced in Task 16.

Recovery data lands in canonical ``data/raw/informants.jsonl`` with each
record's ``qa_notes`` containing the campaign tag
``campaign_id=phase4a-recovery-2026-05-05``.

Idempotence: before each cell, the script checks whether an
informants.jsonl record already exists with (model_id, domain_slug,
run_index) AND the campaign-id substring in qa_notes (per SME R4 —
substring match, not anchored regex). Already-recovered cells are logged
and skipped; the script can be restarted safely mid-run.

On both attempts failing, a ``failures.jsonl`` row is written with
``recovery_failed=true`` and the verbatim final response from attempt 2
(per SME R2), and the campaign continues to the next cell.

Usage::

    # Mandatory first run: validate the target list without API calls
    uv run python scripts/recover_phase4a_failures.py --dry-run

    # Live recovery (Mark sign-off required before executing)
    uv run python scripts/recover_phase4a_failures.py

Exit codes:
    0 — clean run (live or dry), recovery rate >= 80% or all already-recovered
    1 — configuration error (model not in registry, target count != 20)
    2 — live run complete but recovery rate < 80% (routes to CDA SME
        re-review per SME verdict R6 before T4-redo proceeds)

References:
    Architect plan: docs/status/2026-05-05-phase4a-recovery-architect-plan.md §2 Task R1
    SME verdict:    docs/status/2026-05-05-phase4a-recovery-cda-sme-verdict.md (R2, R4)
    Predecessor:    Task 16 commits 7f8f7f7, de3dd7e
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from cdb_collect.domains import load_domain
from cdb_collect.exceptions import PartialSessionError
from cdb_collect.jsonl import append_failure, append_record
from cdb_collect.runner import run_informant
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from collect import MODEL_REGISTRY, _create_adapter  # noqa: E402

load_dotenv()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CAMPAIGN_ID = "phase4a-recovery-2026-05-05"

#: Substring that must appear in qa_notes for a record to be considered
#: already-recovered under this campaign. Substring match per SME R4.
CAMPAIGN_MARKER = f"campaign_id={CAMPAIGN_ID}"

IN_SCOPE_MODELS: frozenset[str] = frozenset({
    "google/gemini-2.5-pro",
    "z-ai/glm-5.1",
    "meta-llama/llama-4-maverick",
})

INFORMANTS_JSONL = Path("data/raw/informants.jsonl")
FAILURES_JSONL = Path("data/raw/failures.jsonl")

EXPECTED_TARGET_COUNT = 20

#: Recovery rate below this threshold → exit 2 + route to CDA SME (SME R6)
RECOVERY_RATE_THRESHOLD = 0.80

#: Delay between attempt 1 failure and attempt 2 start (token-bucket courtesy)
INTER_ATTEMPT_DELAY_S = 5

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True, order=True)
class RecoveryTarget:
    """One (model_id, domain, run_index) cell to recover."""

    model_id: str
    domain: str
    run_index: int
    original_failure_timestamp: str


# ---------------------------------------------------------------------------
# Target-list construction
# ---------------------------------------------------------------------------

def build_target_list(failures_path: Path) -> list[RecoveryTarget]:
    """Read failures.jsonl and build the sorted, deduped in-scope target list.

    Filters to rows where context.model_id is in IN_SCOPE_MODELS.
    Deduplicates on (model_id, domain, run_index) — keeps first occurrence.
    Sorts for deterministic output (by model_id, domain, run_index).

    Asserts len(targets) == EXPECTED_TARGET_COUNT. On mismatch, prints an
    error and calls sys.exit(1) to satisfy the exit-code-1 contract for
    configuration errors.
    """
    if not failures_path.exists():
        print(
            f"ERROR: failures.jsonl not found at {failures_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    seen: set[tuple[str, str, int]] = set()
    targets: list[RecoveryTarget] = []

    with open(failures_path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                logger.warning(
                    "Skipping malformed failures.jsonl line %d: %s", line_num, exc,
                )
                continue

            context = row.get("context", {})
            model_id: str = context.get("model_id", "")
            domain: str = context.get("domain", "")
            run_index_raw = context.get("run_index")
            timestamp: str = row.get("timestamp", "")

            if model_id not in IN_SCOPE_MODELS:
                continue

            if run_index_raw is None:
                logger.warning("Line %d: missing run_index, skipping", line_num)
                continue

            run_index = int(run_index_raw)
            cell_key = (model_id, domain, run_index)
            if cell_key in seen:
                continue
            seen.add(cell_key)

            targets.append(RecoveryTarget(
                model_id=model_id,
                domain=domain,
                run_index=run_index,
                original_failure_timestamp=timestamp,
            ))

    # Sort for determinism; RecoveryTarget is order=True so sort() uses field order:
    # (model_id, domain, run_index, original_failure_timestamp)
    targets.sort()

    if len(targets) != EXPECTED_TARGET_COUNT:
        print(
            f"ERROR: Expected {EXPECTED_TARGET_COUNT} in-scope targets but found "
            f"{len(targets)}. failures.jsonl may have drifted from the §1 disposition "
            f"table in docs/status/2026-05-05-phase4a-recovery-architect-plan.md.",
            file=sys.stderr,
        )
        sys.exit(1)

    return targets


# ---------------------------------------------------------------------------
# Idempotence check (SME R4: substring match, not anchored regex)
# ---------------------------------------------------------------------------

def load_already_recovered(informants_path: Path) -> set[tuple[str, str, int]]:
    """Return the set of (model_id, domain_slug, run_index) already-recovered cells.

    A cell is considered already recovered iff informants.jsonl contains a record
    with matching (model_id, domain_slug, run_index) AND whose qa_notes field
    contains CAMPAIGN_MARKER as a substring.

    Uses substring match, not anchored regex, per SME R4: the qa_notes field
    may contain other tags concatenated with semicolons; anchoring would falsely
    reject valid recovery records if the field grows.
    """
    recovered: set[tuple[str, str, int]] = set()

    if not informants_path.exists():
        return recovered

    with open(informants_path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                logger.warning(
                    "Skipping malformed informants.jsonl line %d", line_num,
                )
                continue

            model_id: str = record.get("model_id", "")
            domain_slug: str = record.get("domain_slug", "")
            run_index_raw = record.get("run_index")
            qa_notes: str = record.get("qa_notes") or ""

            if run_index_raw is None:
                continue

            # SME R4: substring match, not regex with anchors
            if CAMPAIGN_MARKER in qa_notes:
                recovered.add((model_id, domain_slug, int(run_index_raw)))

    return recovered


# ---------------------------------------------------------------------------
# Async runner (called via asyncio.run per cell)
# ---------------------------------------------------------------------------

async def _run_one_informant(
    model_id: str,
    domain_slug: str,
    run_index: int,
):
    """Run one full CDA informant cycle. Returns InformantRecord; raises on failure."""
    model_ref = MODEL_REGISTRY[model_id]
    adapter = _create_adapter(model_ref)
    domain = load_domain(domain_slug)
    return await run_informant(adapter, domain, run_index, campaign_id=CAMPAIGN_ID)


# ---------------------------------------------------------------------------
# Per-cell recovery driver
# ---------------------------------------------------------------------------

def recover_cell(
    target: RecoveryTarget,
    cell_index: int,
    total: int,
    informants_path: Path,
    failures_path: Path,
) -> str:
    """Attempt recovery of one (model_id, domain, run_index) cell.

    Implements the 2-attempt retry budget:
    - Attempt 1: run_informant. On success → append record → "PASS".
    - On failure → wait 5 s → Attempt 2.
    - Attempt 2: run_informant. On success → append record → "PASS".
    - On failure → write failures.jsonl row with recovery_failed=true and
      verbatim final response from attempt 2 (SME R2) → "RECOVERY_FAILED".

    Logging: per-cell prefix includes cell index, model, domain, run, attempt.
    Returns one of: "PASS", "RECOVERY_FAILED".
    """
    prefix = (
        f"[{cell_index}/{total}] "
        f"model={target.model_id} domain={target.domain} run={target.run_index}"
    )

    last_exc: Exception | None = None
    last_pse: PartialSessionError | None = None

    for attempt in range(1, 3):
        label = f"attempt={attempt}/2"
        print(f"{prefix} {label} -> ", end="", flush=True)
        try:
            record = asyncio.run(
                _run_one_informant(target.model_id, target.domain, target.run_index),
            )
            append_record(record, informants_path)
            print("PASS")
            logger.info("%s %s -> PASS", prefix, label)
            return "PASS"

        except PartialSessionError as exc:
            last_exc = exc
            last_pse = exc
            if attempt == 1:
                print("RETRY")
                logger.warning(
                    "%s %s -> RETRY  PartialSessionError: %s",
                    prefix, label, exc.cause,
                )
                time.sleep(INTER_ATTEMPT_DELAY_S)
            else:
                print("RECOVERY_FAILED")
                logger.error(
                    "%s %s -> RECOVERY_FAILED  PartialSessionError: %s",
                    prefix, label, exc.cause,
                )

        except Exception as exc:
            last_exc = exc
            last_pse = None
            if attempt == 1:
                print("RETRY")
                logger.warning(
                    "%s %s -> RETRY  %s: %s",
                    prefix, label, type(exc).__name__, exc,
                )
                time.sleep(INTER_ATTEMPT_DELAY_S)
            else:
                print("RECOVERY_FAILED")
                logger.error(
                    "%s %s -> RECOVERY_FAILED  %s: %s",
                    prefix, label, type(exc).__name__, exc,
                )

    # Both attempts exhausted — write failure row (do NOT abort the campaign)
    assert last_exc is not None, "last_exc must be set after retry loop"

    failure_context: dict = {
        "model_id": target.model_id,
        "domain": target.domain,
        "run_index": target.run_index,
        "campaign_id": CAMPAIGN_ID,
        "recovery_failed": True,
        "original_failure_timestamp": target.original_failure_timestamp,
    }

    if last_pse is not None:
        # SME R2 binding: capture verbatim final response from attempt 2.
        # PartialSessionError carries prompt_verbatim, response_verbatim,
        # thinking_verbatim, stop_reason, partial_session, retry_attempts —
        # pass all to append_failure per the post-v0.1.6 failures-as-findings
        # contract (DATA_DICTIONARY.md §9).
        append_failure(
            last_pse.cause,
            failure_context,
            failures_path,
            prompt_verbatim=last_pse.prompt_verbatim,
            response_verbatim=last_pse.response_verbatim,
            thinking_verbatim=last_pse.thinking_verbatim,
            stop_reason=last_pse.stop_reason,
            partial_session=last_pse.partial_session if last_pse.partial_session else None,
            retry_attempts=last_pse.retry_attempts if last_pse.retry_attempts else None,
        )
    else:
        # Non-PartialSessionError: response_verbatim will be None; acceptable per spec.
        append_failure(last_exc, failure_context, failures_path)

    return "RECOVERY_FAILED"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    """Entry point for the Phase 4a recovery script."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description=(
            "Phase 4a recovery script. Retries 20 in-scope Phase 4a failure "
            "cells at the bumped max_tokens=16384 cap (Task 16). "
            "See docs/status/2026-05-05-phase4a-recovery-architect-plan.md."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help=(
            "Print the 20-cell target list, validate model registry hits, "
            "and exit without making any API calls. Mandatory before live run."
        ),
    )
    args = parser.parse_args()

    # ── Registry validation ──────────────────────────────────────────────
    if not MODEL_REGISTRY:
        print(
            "ERROR: No models in registry. Run:\n"
            "  python scripts/discover_models.py --update-registry",
            file=sys.stderr,
        )
        return 1

    missing_models = sorted(m for m in IN_SCOPE_MODELS if m not in MODEL_REGISTRY)
    if missing_models:
        print(
            f"ERROR: The following in-scope models are missing from MODEL_REGISTRY: "
            f"{missing_models}. "
            f"Run: python scripts/discover_models.py --update-registry",
            file=sys.stderr,
        )
        return 1

    # ── Target list ──────────────────────────────────────────────────────
    # build_target_list calls sys.exit(1) on count mismatch; no return needed.
    targets = build_target_list(FAILURES_JSONL)

    # ── Dry-run mode ─────────────────────────────────────────────────────
    if args.dry_run:
        print(f"DRY RUN — Phase 4a recovery campaign: {CAMPAIGN_ID}")
        print(f"  In-scope models: {sorted(IN_SCOPE_MODELS)}")
        print(f"  Target count: {len(targets)} (expected {EXPECTED_TARGET_COUNT})")
        print()
        print("  Target cells (sorted deterministically):")
        for i, t in enumerate(targets, 1):
            print(
                f"    [{i:2d}/{EXPECTED_TARGET_COUNT}] "
                f"model={t.model_id}  domain={t.domain}  run={t.run_index}"
            )
        print()
        print("  Registry validation:")
        for m in sorted(IN_SCOPE_MODELS):
            ref = MODEL_REGISTRY.get(m)
            status = (
                f"OK  method={ref.collection_method}" if ref else "MISSING"
            )
            print(f"    {m}: {status}")
        print()
        print(f"  Informants path (live): {INFORMANTS_JSONL}")
        print(f"  Failures path (live):   {FAILURES_JSONL}")
        print()
        print("DRY RUN complete. No API calls made.")
        return 0

    # ── Live run ─────────────────────────────────────────────────────────
    print(f"Phase 4a recovery campaign: {CAMPAIGN_ID}")
    print(f"  Total targets: {len(targets)}")
    print(f"  Output: {INFORMANTS_JSONL}")
    print(f"  Failures: {FAILURES_JSONL}")
    print()

    # Load already-recovered cells once into memory (SME R4 idempotence)
    already_recovered_cells = load_already_recovered(INFORMANTS_JSONL)
    logger.info(
        "Already-recovered cells at start of run: %d", len(already_recovered_cells),
    )

    n_recovered = 0
    n_recovery_failed = 0
    n_already_recovered = 0
    total = len(targets)

    for cell_index, target in enumerate(targets, 1):
        cell_key = (target.model_id, target.domain, target.run_index)

        # Idempotence check (SME R4: substring match done in load_already_recovered)
        if cell_key in already_recovered_cells:
            print(
                f"[{cell_index}/{total}] "
                f"model={target.model_id} domain={target.domain} "
                f"run={target.run_index} -> ALREADY_RECOVERED"
            )
            n_already_recovered += 1
            continue

        outcome = recover_cell(
            target, cell_index, total, INFORMANTS_JSONL, FAILURES_JSONL,
        )

        if outcome == "PASS":
            n_recovered += 1
            # Update in-memory set so restart mid-run will not double-write
            already_recovered_cells.add(cell_key)
        elif outcome == "RECOVERY_FAILED":
            n_recovery_failed += 1

    # ── Final summary ─────────────────────────────────────────────────────
    accounted = n_recovered + n_recovery_failed + n_already_recovered
    out_of_scope_skipped = total - accounted  # should be 0 by design

    print()
    print("=" * 60)
    print("Recovery summary")
    print("=" * 60)
    print(f"  Recovered:            {n_recovered}")
    print(f"  Recovery-failed:      {n_recovery_failed}")
    print(f"  Already-recovered:    {n_already_recovered}")
    print(f"  Out-of-scope skipped: {out_of_scope_skipped}")
    print(f"  Total cells:          {total}")

    # Recovery rate: fraction of the 20 cells that produced informant records.
    # Cells that were already-recovered count toward success.
    n_success = n_recovered + n_already_recovered
    recovery_rate = n_success / total if total > 0 else 1.0

    print()
    print(f"  Recovery rate: {n_success}/{total} = {recovery_rate:.1%}")

    if recovery_rate < RECOVERY_RATE_THRESHOLD:
        print(
            f"\nWARNING: Recovery rate {recovery_rate:.1%} is below the 80% threshold. "
            "Per SME verdict R6, route back to CDA SME before T4-redo proceeds. "
            "(Exit code 2.)"
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
