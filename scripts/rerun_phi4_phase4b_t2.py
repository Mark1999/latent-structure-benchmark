"""Phase 4b T2 — phi-4 adaptive-cap 6-cell rerun.

Reruns the 6 microsoft/phi-4 Phase 4a cells that failed under the old
max_tokens=16384 flat cap (5 × HTTPStatusError family runs 0–4, 1 × ValueError
family run 4). The Phase 4b T2 fix adds per-model adaptive max_tokens sizing
(packages/cdb_collect/cdb_collect/adaptive_cap.py) so phi-4's 16K context
window is respected.

Campaign tag: campaign_id=phase4b-phi4-rerun-2026-05-07

Idempotence: before each cell the script checks informants.jsonl for a record
with (model_id, domain_slug, run_index) AND the CAMPAIGN_MARKER substring in
qa_notes. Already-recovered cells are skipped; the script can be restarted
safely mid-run.

Retry budget: 2 attempts per cell. On both attempts failing a failures.jsonl
row is written (recovery_failed=true) and the campaign continues. Per the
failures-as-findings posture, a cell that still fails after the cap fix is a
finding — it is documented verbatim and does NOT abort the campaign.

Exit codes:
    0 — clean run; all 6 cells either recovered or already-recovered
    1 — configuration error (model not in registry, cell count unexpected)
    2 — live run complete but ≥1 cell still failed (finding documented)

References:
    Phase 4b architect plan §7.1:
        docs/status/2026-05-07-phase4b-architect-plan.md
    CDA SME plan verdict:
        docs/status/2026-05-07-phase4b-cda-sme-plan-verdict.md (Q6, PASS)
    Recovery report §7.4 (forward-carry closed by this run):
        docs/status/2026-05-05-phase4a-recovery-report.md
    Adaptive cap helper:
        packages/cdb_collect/cdb_collect/adaptive_cap.py
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
from pathlib import Path

from cdb_collect.adapters.openrouter import OpenRouterAdapter
from cdb_collect.domains import load_domain
from cdb_collect.exceptions import PartialSessionError
from cdb_collect.jsonl import append_failure, append_record
from cdb_collect.runner import run_informant
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from collect import MODEL_REGISTRY  # noqa: E402

load_dotenv()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CAMPAIGN_ID = "phase4b-phi4-rerun-2026-05-07"

#: Substring that must appear in qa_notes for a record to be considered
#: already-recovered under this campaign. Substring match — not anchored —
#: because qa_notes may contain additional semicolon-separated tags.
CAMPAIGN_MARKER = f"campaign_id={CAMPAIGN_ID}"

#: The 6 phi-4 Phase 4a failure cells identified from data/raw/failures.jsonl.
#: 5 × HTTPStatusError (family runs 0–4) + 1 × ValueError (family run 4).
#: The ValueError and the HTTPStatusError on run 4 are deduplicated to one
#: cell: (microsoft/phi-4, family, 4) needs exactly one recovery run.
PHI4_MODEL_ID = "microsoft/phi-4"

PHI4_TARGET_CELLS: list[tuple[str, str, int]] = [
    (PHI4_MODEL_ID, "family", 0),
    (PHI4_MODEL_ID, "family", 1),
    (PHI4_MODEL_ID, "family", 2),
    (PHI4_MODEL_ID, "family", 3),
    (PHI4_MODEL_ID, "family", 4),
]
# Note: failures.jsonl has 6 rows for phi-4 (5 HTTPStatusError + 1 ValueError)
# but both refer to at most 5 unique (model, domain, run_index) cells since the
# ValueError on family/run=4 is a duplicate key. The actual unique cells are
# the 5 (family, run 0–4). EXPECTED_TARGET_COUNT reflects the unique cells.
EXPECTED_TARGET_COUNT = 5

INFORMANTS_JSONL = Path("data/raw/informants.jsonl")
FAILURES_JSONL = Path("data/raw/failures.jsonl")
REGISTRY_PATH = Path("data/models/registry.json")

#: Delay between attempt 1 failure and attempt 2 start (token-bucket courtesy)
INTER_ATTEMPT_DELAY_S = 5

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Registry context_length lookup
# ---------------------------------------------------------------------------

def _load_context_length_map(registry_path: Path) -> dict[str, int]:
    """Return a map of model_id → context_length from the registry JSON."""
    if not registry_path.exists():
        return {}
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    result: dict[str, int] = {}
    for entry in data.get("models", []):
        mid = entry.get("model_id", "")
        cl = entry.get("context_length")
        if mid and cl is not None:
            result[mid] = int(cl)
    return result


# ---------------------------------------------------------------------------
# Idempotence check
# ---------------------------------------------------------------------------

def load_already_recovered(informants_path: Path) -> set[tuple[str, str, int]]:
    """Return the set of (model_id, domain_slug, run_index) already-recovered.

    Substring match per the established recovery-script pattern (R4 in the
    Phase 4a recovery SME verdict): qa_notes may contain multiple semicolon-
    separated tags so anchored regex would falsely reject valid records.
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
            mid = record.get("model_id", "")
            domain_slug = record.get("domain_slug", "")
            run_index_raw = record.get("run_index")
            qa_notes: str = record.get("qa_notes") or ""
            if run_index_raw is None:
                continue
            if CAMPAIGN_MARKER in qa_notes:
                recovered.add((mid, domain_slug, int(run_index_raw)))
    return recovered


# ---------------------------------------------------------------------------
# Async runner
# ---------------------------------------------------------------------------

async def _run_one_informant(
    model_id: str,
    domain_slug: str,
    run_index: int,
    context_length: int,
) -> object:
    """Run one full CDA informant cycle for phi-4 with the adaptive cap wired in."""
    model_ref = MODEL_REGISTRY[model_id]
    # Build the adapter with the phi-4 context_length so the adaptive cap fires.
    # context_length=16384 → with a ~2K-token prompt, effective max_tokens ≈ 13872.
    adapter = OpenRouterAdapter(model_ref, context_length=context_length)
    domain = load_domain(domain_slug)
    return await run_informant(adapter, domain, run_index, campaign_id=CAMPAIGN_ID)


# ---------------------------------------------------------------------------
# Per-cell recovery driver
# ---------------------------------------------------------------------------

def recover_cell(
    model_id: str,
    domain_slug: str,
    run_index: int,
    context_length: int,
    cell_index: int,
    total: int,
) -> str:
    """Attempt recovery of one (model_id, domain, run_index) cell.

    2-attempt retry budget:
    - Attempt 1: run_informant → PASS or RETRY.
    - Attempt 2 (if attempt 1 failed): run_informant → PASS or RECOVERY_FAILED.
    On RECOVERY_FAILED: write failures.jsonl row and return.

    Returns one of: "PASS", "RECOVERY_FAILED".
    """
    prefix = (
        f"[{cell_index}/{total}] "
        f"model={model_id} domain={domain_slug} run={run_index}"
    )
    last_exc: Exception | None = None
    last_pse: PartialSessionError | None = None

    for attempt in range(1, 3):
        label = f"attempt={attempt}/2"
        print(f"{prefix} {label} -> ", end="", flush=True)
        try:
            record = asyncio.run(
                _run_one_informant(model_id, domain_slug, run_index, context_length),
            )
            append_record(record, INFORMANTS_JSONL)
            print("PASS")
            logger.info("%s %s -> PASS", prefix, label)
            return "PASS"

        except PartialSessionError as exc:
            last_exc = exc
            last_pse = exc
            if attempt == 1:
                print("RETRY")
                logger.warning(
                    "%s %s -> RETRY  PartialSessionError: %s", prefix, label, exc.cause,
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
                    "%s %s -> RETRY  %s: %s", prefix, label, type(exc).__name__, exc,
                )
                time.sleep(INTER_ATTEMPT_DELAY_S)
            else:
                print("RECOVERY_FAILED")
                logger.error(
                    "%s %s -> RECOVERY_FAILED  %s: %s",
                    prefix, label, type(exc).__name__, exc,
                )

    # Both attempts exhausted — write failure row (do NOT abort the campaign).
    assert last_exc is not None, "last_exc must be set after retry loop"

    failure_context: dict = {
        "model_id": model_id,
        "domain": domain_slug,
        "run_index": run_index,
        "campaign_id": CAMPAIGN_ID,
        "recovery_failed": True,
    }

    if last_pse is not None:
        append_failure(
            last_pse.cause,
            failure_context,
            FAILURES_JSONL,
            prompt_verbatim=last_pse.prompt_verbatim,
            response_verbatim=last_pse.response_verbatim,
            thinking_verbatim=last_pse.thinking_verbatim,
            stop_reason=last_pse.stop_reason,
            partial_session=last_pse.partial_session if last_pse.partial_session else None,
            retry_attempts=last_pse.retry_attempts if last_pse.retry_attempts else None,
        )
    else:
        append_failure(last_exc, failure_context, FAILURES_JSONL)

    return "RECOVERY_FAILED"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    """Entry point for the Phase 4b T2 phi-4 rerun."""
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
            "Phase 4b T2 — phi-4 adaptive-cap 6-cell rerun. "
            "Reruns the 5 unique phi-4 Phase 4a failure cells with the adaptive "
            "max_tokens cap so phi-4's 16K context window is respected. "
            "See docs/status/2026-05-07-phase4b-architect-plan.md §7.1."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help=(
            "Print the target cell list and validate model registry, "
            "then exit without making any API calls."
        ),
    )
    args = parser.parse_args()

    # ── Registry validation ───────────────────────────────────────────────
    if not MODEL_REGISTRY:
        print(
            "ERROR: No models in registry. Run:\n"
            "  python scripts/discover_models.py --update-registry",
            file=sys.stderr,
        )
        return 1

    if PHI4_MODEL_ID not in MODEL_REGISTRY:
        print(
            f"ERROR: {PHI4_MODEL_ID} not found in MODEL_REGISTRY. "
            "Run: python scripts/discover_models.py --update-registry",
            file=sys.stderr,
        )
        return 1

    # ── context_length for phi-4 ──────────────────────────────────────────
    context_length_map = _load_context_length_map(REGISTRY_PATH)
    phi4_context_length = context_length_map.get(PHI4_MODEL_ID)
    if phi4_context_length is None:
        print(
            f"ERROR: {PHI4_MODEL_ID} has no context_length in registry.json. "
            "Cannot compute adaptive max_tokens.",
            file=sys.stderr,
        )
        return 1

    # ── Target list ───────────────────────────────────────────────────────
    targets = PHI4_TARGET_CELLS
    if len(targets) != EXPECTED_TARGET_COUNT:
        print(
            f"ERROR: Expected {EXPECTED_TARGET_COUNT} unique phi-4 targets but "
            f"PHI4_TARGET_CELLS has {len(targets)}.",
            file=sys.stderr,
        )
        return 1

    # ── Dry-run mode ──────────────────────────────────────────────────────
    if args.dry_run:
        print(f"DRY RUN — Phase 4b T2 phi-4 rerun: {CAMPAIGN_ID}")
        print(f"  Model: {PHI4_MODEL_ID}")
        print(f"  context_length from registry: {phi4_context_length}")
        print(f"  Target count: {len(targets)} (expected {EXPECTED_TARGET_COUNT})")
        print()
        print("  Target cells (unique; 6 failures.jsonl rows deduplicated):")
        for i, (mid, domain, run) in enumerate(targets, 1):
            print(f"    [{i}/{EXPECTED_TARGET_COUNT}] model={mid}  domain={domain}  run={run}")
        print()
        print(f"  Informants path: {INFORMANTS_JSONL}")
        print(f"  Failures path:   {FAILURES_JSONL}")
        print()
        print("DRY RUN complete. No API calls made.")
        return 0

    # ── Live run ──────────────────────────────────────────────────────────
    print(f"Phase 4b T2 phi-4 rerun: {CAMPAIGN_ID}")
    print(f"  Model: {PHI4_MODEL_ID}  context_length={phi4_context_length}")
    print(f"  Total unique targets: {len(targets)}")
    print(f"  Output: {INFORMANTS_JSONL}")
    print(f"  Failures: {FAILURES_JSONL}")
    print()

    already_recovered = load_already_recovered(INFORMANTS_JSONL)
    logger.info("Already-recovered cells at start of run: %d", len(already_recovered))

    n_recovered = 0
    n_recovery_failed = 0
    n_already_recovered = 0
    total = len(targets)

    for cell_index, (model_id, domain_slug, run_index) in enumerate(targets, 1):
        cell_key = (model_id, domain_slug, run_index)

        if cell_key in already_recovered:
            print(
                f"[{cell_index}/{total}] "
                f"model={model_id} domain={domain_slug} run={run_index} -> ALREADY_RECOVERED"
            )
            n_already_recovered += 1
            continue

        outcome = recover_cell(
            model_id, domain_slug, run_index, phi4_context_length,
            cell_index, total,
        )

        if outcome == "PASS":
            n_recovered += 1
            already_recovered.add(cell_key)
        elif outcome == "RECOVERY_FAILED":
            n_recovery_failed += 1

    # ── Summary ───────────────────────────────────────────────────────────
    n_success = n_recovered + n_already_recovered

    print()
    print("=" * 60)
    print("Phase 4b T2 phi-4 rerun summary")
    print("=" * 60)
    print(f"  Campaign ID:          {CAMPAIGN_ID}")
    print(f"  Targeted:             {total}")
    print(f"  Recovered:            {n_recovered}")
    print(f"  Already-recovered:    {n_already_recovered}")
    print(f"  Recovery-failed:      {n_recovery_failed}")
    print(f"  Net recovered:        {n_success}/{total}")

    if n_recovery_failed > 0:
        print()
        print(
            f"  NOTE: {n_recovery_failed} cell(s) still failed after 2 attempts. "
            "Per failures-as-findings posture this is a finding — verbatim captured "
            f"in {FAILURES_JSONL} with campaign_id={CAMPAIGN_ID} and recovery_failed=true."
        )
        print(
            "  This does NOT block the Phase 4b variance run. phi-4 can still "
            "produce variant-arm cells; the 5 rerun cells that remain unreachable "
            "are documented as data."
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
