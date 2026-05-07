"""Phase 4b T3 — diagnostic re-attempt of 3 unexplained Phase 4a failures.

Targets (per recovery report §7.3 + Architect plan §7.2):
  - openai/gpt-5.4-mini  × family   × run_index=0
  - openai/gpt-5.4-mini  × family   × run_index=2
  - mistralai/mistral-small-2603 × holidays × run_index=3

These three cells were excluded from the Phase 4a recovery campaign because
Stage 1.5b confirmed they are not cap-related (root cause was unknown at that
point).  This script re-attempts each cell under the post-T16 instrument (same
adapter layer, idempotence check against the campaign tag, 2-attempt budget,
hard-stop CDB_MAX_SPEND_USD guard).

Recovery data lands in canonical ``data/raw/informants.jsonl`` with each
record's ``qa_notes`` containing the campaign tag
``campaign_id=phase4b-tail-rerun-2026-05-07``.

Idempotence: before each cell, the script checks whether an
informants.jsonl record already exists with (model_id, domain_slug,
run_index) AND the campaign-id substring in qa_notes (substring match,
not anchored regex, per established convention in recover_phase4a_failures.py).

On both attempts failing, a ``failures.jsonl`` row is written with
verbatim capture, and the script continues to the next cell
(failures-as-findings posture).

Usage::

    # Mandatory first: validate target list without API calls
    uv run python scripts/rerun_t3_unexplained_phase4b.py --dry-run

    # Live rerun (CDB_MAX_SPEND_USD=5 must be exported before calling)
    CDB_MAX_SPEND_USD=5 uv run python scripts/rerun_t3_unexplained_phase4b.py

Exit codes:
    0 — clean run (all 3 cells recovered or already-recovered)
    1 — configuration error (model not in registry, wrong target count)
    2 — live run complete but at least one cell still in failures.jsonl

References:
    Architect plan §7.2:  docs/status/2026-05-07-phase4b-architect-plan.md
    Recovery report §7.3: docs/status/2026-05-05-phase4a-recovery-report.md
    Predecessor script:   scripts/recover_phase4a_failures.py (commit 50b70b6)
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

CAMPAIGN_ID = "phase4b-tail-rerun-2026-05-07"
CAMPAIGN_MARKER = f"campaign_id={CAMPAIGN_ID}"

INFORMANTS_JSONL = Path("data/raw/informants.jsonl")
FAILURES_JSONL = Path("data/raw/failures.jsonl")

EXPECTED_TARGET_COUNT = 3

#: Delay between attempt 1 failure and attempt 2 start (token-bucket courtesy)
INTER_ATTEMPT_DELAY_S = 5

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Target list (hard-coded: exactly the 3 cells from recovery report §7.3)
# ---------------------------------------------------------------------------

@dataclass(frozen=True, order=True)
class RerunTarget:
    """One (model_id, domain, run_index) cell to re-attempt."""

    model_id: str
    domain: str
    run_index: int


# These three are the only cells in scope for this task.
# If the target list needs to change, a new Architect plan is required.
TARGETS: list[RerunTarget] = sorted([
    RerunTarget("openai/gpt-5.4-mini", "family", 0),
    RerunTarget("openai/gpt-5.4-mini", "family", 2),
    RerunTarget("mistralai/mistral-small-2603", "holidays", 3),
])


# ---------------------------------------------------------------------------
# Idempotence check
# ---------------------------------------------------------------------------

def load_already_recovered(informants_path: Path) -> set[tuple[str, str, int]]:
    """Return (model_id, domain_slug, run_index) tuples already recovered
    under this campaign (substring match on CAMPAIGN_MARKER in qa_notes).
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
                logger.warning("Skipping malformed informants.jsonl line %d", line_num)
                continue

            qa_notes: str = record.get("qa_notes") or ""
            if CAMPAIGN_MARKER not in qa_notes:
                continue

            model_id: str = record.get("model_id", "")
            domain_slug: str = record.get("domain_slug", "")
            run_index_raw = record.get("run_index")
            if run_index_raw is None:
                continue
            recovered.add((model_id, domain_slug, int(run_index_raw)))

    return recovered


# ---------------------------------------------------------------------------
# Async runner
# ---------------------------------------------------------------------------

async def _run_one_informant(
    model_id: str,
    domain_slug: str,
    run_index: int,
) -> object:
    """Run one full CDA informant cycle. Returns InformantRecord; raises on failure."""
    model_ref = MODEL_REGISTRY[model_id]
    adapter = _create_adapter(model_ref)
    domain = load_domain(domain_slug)
    return await run_informant(adapter, domain, run_index, campaign_id=CAMPAIGN_ID)


# ---------------------------------------------------------------------------
# Per-cell rerun driver (2-attempt budget, failures-as-findings)
# ---------------------------------------------------------------------------

def rerun_cell(
    target: RerunTarget,
    cell_index: int,
    total: int,
    informants_path: Path,
    failures_path: Path,
) -> str:
    """Attempt re-run of one cell with a 2-attempt budget.

    Returns: "PASS" | "RECOVERY_FAILED"
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

    # Both attempts exhausted — write failure row (failures-as-findings)
    assert last_exc is not None, "last_exc must be set after retry loop"

    failure_context: dict = {
        "model_id": target.model_id,
        "domain": target.domain,
        "run_index": target.run_index,
        "campaign_id": CAMPAIGN_ID,
        "recovery_failed": True,
    }

    if last_pse is not None:
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
        append_failure(last_exc, failure_context, failures_path)

    return "RECOVERY_FAILED"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    """Entry point for the Phase 4b T3 rerun script."""
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
            "Phase 4b T3 — re-attempt 3 unexplained Phase 4a failures "
            "(gpt-5.4-mini family ×2 + mistral-small holidays ×1). "
            "See docs/status/2026-05-07-phase4b-architect-plan.md §7.2."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help=(
            "Print the 3-cell target list, validate model registry hits, "
            "and exit without making any API calls."
        ),
    )
    args = parser.parse_args()

    # ── Registry validation ─────────────────────────────────────────────
    if not MODEL_REGISTRY:
        print(
            "ERROR: No models in registry. Run:\n"
            "  python scripts/discover_models.py --update-registry",
            file=sys.stderr,
        )
        return 1

    required_models = {t.model_id for t in TARGETS}
    missing_models = sorted(m for m in required_models if m not in MODEL_REGISTRY)
    if missing_models:
        print(
            f"ERROR: The following target models are missing from MODEL_REGISTRY: "
            f"{missing_models}.",
            file=sys.stderr,
        )
        return 1

    if len(TARGETS) != EXPECTED_TARGET_COUNT:
        print(
            f"ERROR: Expected {EXPECTED_TARGET_COUNT} targets but TARGETS list "
            f"has {len(TARGETS)}.",
            file=sys.stderr,
        )
        return 1

    # ── Dry-run mode ────────────────────────────────────────────────────
    if args.dry_run:
        print(f"DRY RUN — Phase 4b T3 rerun campaign: {CAMPAIGN_ID}")
        print(f"  Target count: {len(TARGETS)} (expected {EXPECTED_TARGET_COUNT})")
        print()
        print("  Target cells:")
        for i, t in enumerate(TARGETS, 1):
            print(
                f"    [{i}/{EXPECTED_TARGET_COUNT}] "
                f"model={t.model_id}  domain={t.domain}  run={t.run_index}"
            )
        print()
        print("  Registry validation:")
        for m in sorted(required_models):
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

    # ── Live run ────────────────────────────────────────────────────────
    print(f"Phase 4b T3 rerun campaign: {CAMPAIGN_ID}")
    print(f"  Total targets: {len(TARGETS)}")
    print(f"  Output: {INFORMANTS_JSONL}")
    print(f"  Failures: {FAILURES_JSONL}")
    print()

    already_recovered = load_already_recovered(INFORMANTS_JSONL)
    logger.info("Already-recovered cells at start of run: %d", len(already_recovered))

    n_recovered = 0
    n_recovery_failed = 0
    n_already_recovered = 0
    total = len(TARGETS)

    for cell_index, target in enumerate(TARGETS, 1):
        cell_key = (target.model_id, target.domain, target.run_index)

        if cell_key in already_recovered:
            print(
                f"[{cell_index}/{total}] "
                f"model={target.model_id} domain={target.domain} "
                f"run={target.run_index} -> ALREADY_RECOVERED"
            )
            n_already_recovered += 1
            continue

        outcome = rerun_cell(
            target, cell_index, total, INFORMANTS_JSONL, FAILURES_JSONL,
        )

        if outcome == "PASS":
            n_recovered += 1
            already_recovered.add(cell_key)
        elif outcome == "RECOVERY_FAILED":
            n_recovery_failed += 1

    # ── Final summary ────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("T3 rerun summary")
    print("=" * 60)
    print(f"  Recovered:           {n_recovered}")
    print(f"  Recovery-failed:     {n_recovery_failed}")
    print(f"  Already-recovered:   {n_already_recovered}")
    print(f"  Total cells:         {total}")

    n_success = n_recovered + n_already_recovered
    print(f"\n  Recovery rate: {n_success}/{total} = {n_success/total:.1%}")

    if n_recovery_failed > 0:
        print(
            f"\nNOTE: {n_recovery_failed} cell(s) still in failures.jsonl. "
            "Per failures-as-findings posture, these are canonical data. "
            "See docs/status/2026-05-07-phase4b-t3-tail-failures-memo.md §4 for disposition."
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
