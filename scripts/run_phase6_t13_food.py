"""Phase 6 T13 — food domain collection driver.

Drives the canonical collection arm for the food domain:
9 models x v1_s1 variant x 5 runs x 1 domain (food) = 45 target cells.

Campaign tag: phase6-t13-food-2026-05-15 (or --campaign-id override)

Idempotence: before each cell the script checks informants.jsonl +
failures.jsonl for (model_id, prompt_version, domain_slug) triples with the
campaign_id substring in qa_notes.  Already-completed cells (>=5 records for
that triple) are skipped.  The script is restart-safe across tmux sessions.

Provider preflight: at startup one cheap probe is issued per provider.  If a
provider returns 429 / quota-exhausted, those models are excluded from the run
plan and the campaign continues with remaining models.

Stop condition: if fewer than 5 models complete, the script exits with code 3
and prints a message instructing the operator to pause and route back to the
Architect/CDA SME before running cdb_analyze.  Per the Architect plan §10
risk #1 and CDA SME verdict stop-condition note.

Retry budget: 2 attempts per cell (one initial + one retry).  After 2
attempts the failure is appended to failures.jsonl (failures-as-findings
posture; see docs/status/2026-05-07-lsb-philosophy-and-framing.md §9).

Rate limits: Anthropic 50 RPM, OpenAI 500 RPM, Google 60 RPM, xAI 60 RPM,
OpenRouter 200 RPM.  Sequential within each provider with appropriate sleeps;
concurrent across providers via threading.  Each provider thread manages its
own rate-limit sleep.

Signal handling: SIGINT finishes the in-flight cell then exits cleanly with
a resume hint.

Progress: logged to stdout AND to logs/phase6-t13-food-{campaign_id}.log.

Usage::

    # Dry-run (validates plan, no API calls)
    uv run python scripts/run_phase6_t13_food.py --dry-run

    # Live run
    uv run python scripts/run_phase6_t13_food.py

    # Live run with explicit campaign-id
    uv run python scripts/run_phase6_t13_food.py \\
        --campaign-id phase6-t13-food-2026-05-15

Exit codes:
    0 — clean run (complete or dry-run)
    1 — configuration error
    2 — run completed with at least one cell still failed (finding documented)
    3 — fewer than 5 models completed (stop condition: route back to CDA SME)

References:
    Architect plan:
        docs/status/2026-05-15-phase6-T13-architect-plan.md
    CDA SME verdict (PASS-WITH-NOTES, binding):
        docs/status/2026-05-15-phase6-T13-cda-sme-verdict.md
    UI/UX verdict (PASS clean):
        docs/status/2026-05-15-phase6-T13-uiux-verdict.md
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import queue
import signal
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import IO

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

#: 9-model slate from Architect plan B-D1 (phase4b-complete models)
FOOD_MODEL_IDS: list[str] = [
    "claude-opus-4-6",
    "claude-sonnet-4-6",
    "claude-opus-4-5",
    "openai/gpt-5.4",
    "openai/gpt-5.4-mini",
    "openai/gpt-5.2",
    "google/gemini-2.5-flash",
    "x-ai/grok-4.20",
    "mistralai/mistral-small-2603",
]

#: Canonical v1 variant only (not the full variance arm)
FOOD_PROMPT_VERSIONS: list[str] = ["v1_s1"]

#: Single target domain
FOOD_DOMAINS: list[str] = ["food"]

#: 5 runs per (model, variant, domain) cell
N_RUNS_PER_CELL: int = 5

#: Retry budget per cell: 1 initial + 1 retry = 2 attempts
MAX_ATTEMPTS_PER_CELL: int = 2

#: Delay between attempt 1 failure and attempt 2 start (seconds)
INTER_ATTEMPT_DELAY_S: int = 5

#: Minimum models that must complete before cdb_analyze is safe to run.
#: Per Architect plan §10 risk #1 and CDA SME verdict stop-condition note.
MIN_MODELS_COMPLETE: int = 5

#: Provider -> RPM limits (requests per minute)
PROVIDER_RPM: dict[str, int] = {
    "anthropic_api": 50,
    "openai_api": 500,
    "google_ai": 60,
    "xai_api": 60,
    "openrouter": 200,
}

#: Provider -> number of parallel worker threads.
#:
#: anthropic/openai/google/xai each serve a small slice of this 9-model slate;
#: openrouter serves 1 model (mistralai/mistral-small-2603).
#: All set to 1 worker: at 5 cells per model, any single-provider bottleneck
#: is at most 5 sequential calls, which finishes in minutes.
PROVIDER_WORKERS: dict[str, int] = {
    "anthropic_api": 1,
    "openai_api": 1,
    "google_ai": 1,
    "xai_api": 1,
    "openrouter": 1,
}

#: Provider -> per-thread sleep (seconds) between sequential requests.
PROVIDER_SLEEP_S: dict[str, float] = {
    method: (60.0 / rpm) * PROVIDER_WORKERS.get(method, 1) + 0.1
    for method, rpm in PROVIDER_RPM.items()
}

INFORMANTS_JSONL = Path("data/raw/informants.jsonl")
FAILURES_JSONL = Path("data/raw/failures.jsonl")
LOGS_DIR = Path("logs")

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Global state for signal handling
# ---------------------------------------------------------------------------

_shutdown_requested: bool = False


def _handle_sigint(signum: int, frame: object) -> None:
    """Set shutdown flag; in-flight cell will complete before exit."""
    global _shutdown_requested  # noqa: PLW0603
    if not _shutdown_requested:
        _shutdown_requested = True
        print(
            "\n[SIGINT received] Finishing in-flight cell then exiting cleanly.",
            flush=True,
        )


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True, order=True)
class FoodCell:
    """One (model_id, prompt_version, domain, run_index) work unit."""

    model_id: str
    prompt_version: str
    domain: str
    run_index: int


@dataclass
class CampaignStats:
    """Mutable counters accumulated during the campaign run."""

    n_pass: int = 0
    n_failed: int = 0
    n_skipped: int = 0
    cells_attempted: list[FoodCell] = field(default_factory=list)
    cells_remaining: list[FoodCell] = field(default_factory=list)
    # Lock for cross-thread updates
    _lock: threading.Lock = field(default_factory=threading.Lock)


# ---------------------------------------------------------------------------
# Provider grouping
# ---------------------------------------------------------------------------

def group_models_by_provider(model_ids: list[str]) -> dict[str, list[str]]:
    """Return {collection_method: [model_id, ...]} grouping."""
    groups: dict[str, list[str]] = {}
    for mid in model_ids:
        ref = MODEL_REGISTRY.get(mid)
        if not ref:
            continue
        method = ref.collection_method
        groups.setdefault(method, []).append(mid)
    return groups


# ---------------------------------------------------------------------------
# Preflight ping per provider
# ---------------------------------------------------------------------------

_QUOTA_MARKERS: tuple[str, ...] = (
    "429",
    "quota",
    "rate limit",
    "too many requests",
    "resource_exhausted",
    "insufficient_quota",
    "rate_limit_exceeded",
    "overloaded",
)


def _exc_chain_str(exc: BaseException) -> str:
    """Return a single lowercase string concatenating all messages in the
    exception chain (__cause__ and __context__).
    """
    parts: list[str] = []
    seen: set[int] = set()
    node: BaseException | None = exc
    while node is not None and id(node) not in seen:
        seen.add(id(node))
        parts.append(str(node).lower())
        node = node.__cause__ or node.__context__
    return " ".join(parts)


def _is_quota_exhausted(exc: BaseException) -> bool:
    """Return True when the exception chain contains a 429 / quota signal."""
    chain = _exc_chain_str(exc)
    return any(marker in chain for marker in _QUOTA_MARKERS)


def _check_provider_available(collection_method: str, model_id: str) -> bool:
    """Issue a minimal probe to confirm the provider is reachable and not quota-exhausted."""
    probe_campaign = "__preflight_probe__"
    probe_domain = "family"

    ref = MODEL_REGISTRY.get(model_id)
    if not ref:
        return False

    adapter = _create_adapter(ref)
    domain = load_domain(probe_domain)

    try:
        asyncio.run(run_informant(adapter, domain, 0, campaign_id=probe_campaign))
        return True
    except Exception as exc:
        return not _is_quota_exhausted(exc)


def run_preflight(
    model_ids: list[str],
    dry_run: bool = False,
) -> tuple[list[str], dict[str, list[str]]]:
    """Run one preflight probe per provider; return (active_models, skipped_by_provider)."""
    if dry_run:
        return list(model_ids), {}

    groups = group_models_by_provider(model_ids)
    skipped_by_provider: dict[str, list[str]] = {}
    active: list[str] = []

    print("Preflight: probing providers...", flush=True)
    logger.info("Preflight: probing %d providers", len(groups))

    for method, mids in sorted(groups.items()):
        probe_model = mids[0]
        print(f"  Probing provider={method} via model={probe_model} ... ", end="", flush=True)
        available = _check_provider_available(method, probe_model)
        if available:
            print("OK")
            logger.info("Preflight provider=%s OK", method)
            active.extend(mids)
        else:
            print(f"QUOTA-EXHAUSTED — skipping {len(mids)} model(s)")
            logger.warning(
                "WARN: provider %s quota-exhausted at preflight; skipping models %s",
                method,
                mids,
            )
            skipped_by_provider[method] = mids

    return active, skipped_by_provider


# ---------------------------------------------------------------------------
# Idempotence / resume helpers
# ---------------------------------------------------------------------------

def count_completed_cells(
    campaign_marker: str,
    informants_path: Path,
    failures_path: Path,
) -> dict[tuple[str, str, str], int]:
    """Return a dict mapping (model_id, prompt_version, domain_slug) -> n_records."""
    counts: dict[tuple[str, str, str], int] = {}

    def _inc(model_id: str, prompt_version: str, domain_slug: str) -> None:
        key = (model_id, prompt_version, domain_slug)
        counts[key] = counts.get(key, 0) + 1

    if informants_path.exists():
        with open(informants_path, encoding="utf-8") as fh:
            for line_num, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    logger.warning("Skipping malformed informants.jsonl line %d", line_num)
                    continue
                qa_notes: str = rec.get("qa_notes") or ""
                if campaign_marker not in qa_notes:
                    continue
                model_id = rec.get("model_id", "")
                prompt_version = rec.get("freelist", {}).get("prompt_version", "")
                domain_slug = rec.get("domain_slug", "")
                if model_id and prompt_version and domain_slug:
                    _inc(model_id, prompt_version, domain_slug)

    if failures_path.exists():
        with open(failures_path, encoding="utf-8") as fh:
            for line_num, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    logger.warning("Skipping malformed failures.jsonl line %d", line_num)
                    continue
                context = rec.get("context", {})
                ctx_campaign = context.get("campaign_id", "") or ""
                qa_notes_f = rec.get("qa_notes", "") or ""
                if campaign_marker not in ctx_campaign and campaign_marker not in qa_notes_f:
                    # Also check if campaign_id value is a substring match
                    stripped_marker = campaign_marker.replace("campaign_id=", "")
                    if stripped_marker not in ctx_campaign:
                        continue
                model_id = context.get("model_id", "")
                prompt_version = context.get("prompt_version", "")
                domain_slug = context.get("domain", "") or context.get("domain_slug", "")
                if model_id and prompt_version and domain_slug:
                    _inc(model_id, prompt_version, domain_slug)

    return counts


# ---------------------------------------------------------------------------
# Run-plan generator
# ---------------------------------------------------------------------------

def build_run_plan(
    active_models: list[str],
    completed_counts: dict[tuple[str, str, str], int],
) -> list[FoodCell]:
    """Build the ordered list of FoodCells to collect."""
    plan: list[FoodCell] = []
    for model_id in active_models:
        for pv in FOOD_PROMPT_VERSIONS:
            for domain in FOOD_DOMAINS:
                key = (model_id, pv, domain)
                n_done = completed_counts.get(key, 0)
                n_remaining = max(0, N_RUNS_PER_CELL - n_done)
                for run_idx in range(n_done, n_done + n_remaining):
                    plan.append(FoodCell(model_id, pv, domain, run_idx))
    return plan


# ---------------------------------------------------------------------------
# Cell runner
# ---------------------------------------------------------------------------

async def _run_one_informant(
    model_id: str,
    domain_slug: str,
    run_index: int,
    prompt_version: str,
    campaign_id: str,
) -> object:
    """Run one full CDA informant cycle. Returns InformantRecord; raises on failure."""
    ref = MODEL_REGISTRY[model_id]
    adapter = _create_adapter(ref)
    domain = load_domain(domain_slug)
    return await run_informant(
        adapter,
        domain,
        run_index,
        prompt_version=prompt_version,
        campaign_id=campaign_id,
    )


def run_cell(
    cell: FoodCell,
    cell_index: int,
    total: int,
    campaign_id: str,
    informants_path: Path,
    failures_path: Path,
    stats: CampaignStats,
    log_fh: IO[str],
) -> str:
    """Attempt collection of one FoodCell with 2-attempt retry budget.

    Returns: "PASS" | "FAILED"
    """
    prefix = (
        f"[{cell_index}/{total}] "
        f"model={cell.model_id} variant={cell.prompt_version} "
        f"domain={cell.domain} run={cell.run_index}"
    )

    last_exc: Exception | None = None
    last_pse: PartialSessionError | None = None

    for attempt in range(1, MAX_ATTEMPTS_PER_CELL + 1):
        label = f"attempt={attempt}/{MAX_ATTEMPTS_PER_CELL}"
        msg = f"{prefix} {label} -> "
        print(msg, end="", flush=True)

        try:
            record = asyncio.run(
                _run_one_informant(
                    cell.model_id,
                    cell.domain,
                    cell.run_index,
                    cell.prompt_version,
                    campaign_id,
                )
            )
            append_record(record, informants_path)  # type: ignore[arg-type]

            print("PASS")

            ts = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            log_line = (
                f"{ts} model={cell.model_id} variant={cell.prompt_version} "
                f"domain={cell.domain} run={cell.run_index} outcome=PASS\n"
            )
            log_fh.write(log_line)
            log_fh.flush()

            logger.info("%s %s -> PASS", prefix, label)
            stats.n_pass += 1
            return "PASS"

        except PartialSessionError as exc:
            last_exc = exc
            last_pse = exc
            if attempt < MAX_ATTEMPTS_PER_CELL:
                print("RETRY")
                logger.warning(
                    "%s %s -> RETRY  PartialSessionError: %s",
                    prefix, label, exc.cause,
                )
                time.sleep(INTER_ATTEMPT_DELAY_S)
            else:
                print("FAILED")
                logger.error(
                    "%s %s -> FAILED  PartialSessionError: %s",
                    prefix, label, exc.cause,
                )

        except Exception as exc:
            last_exc = exc
            last_pse = None
            if attempt < MAX_ATTEMPTS_PER_CELL:
                print("RETRY")
                logger.warning(
                    "%s %s -> RETRY  %s: %s",
                    prefix, label, type(exc).__name__, exc,
                )
                time.sleep(INTER_ATTEMPT_DELAY_S)
            else:
                print("FAILED")
                logger.error(
                    "%s %s -> FAILED  %s: %s",
                    prefix, label, type(exc).__name__, exc,
                )

    assert last_exc is not None, "last_exc must be set after retry loop"

    failure_context: dict = {
        "model_id": cell.model_id,
        "domain": cell.domain,
        "run_index": cell.run_index,
        "prompt_version": cell.prompt_version,
        "campaign_id": campaign_id,
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

    ts = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    log_line = (
        f"{ts} model={cell.model_id} variant={cell.prompt_version} "
        f"domain={cell.domain} run={cell.run_index} outcome=FAILED\n"
    )
    log_fh.write(log_line)
    log_fh.flush()

    stats.n_failed += 1
    return "FAILED"


# ---------------------------------------------------------------------------
# Provider thread worker
# ---------------------------------------------------------------------------

def provider_worker(
    provider_method: str,
    cell_queue: queue.Queue[FoodCell | None],
    campaign_id: str,
    informants_path: Path,
    failures_path: Path,
    stats: CampaignStats,
    log_fh: IO[str],
    total_cells: int,
    cell_counter: list[int],
    counter_lock: threading.Lock,
) -> None:
    """Thread worker: drain the provider's cell queue respecting rate limits."""
    sleep_s = PROVIDER_SLEEP_S.get(provider_method, 0.5)

    while True:
        if _shutdown_requested:
            break

        try:
            item = cell_queue.get(timeout=1.0)
        except queue.Empty:
            continue

        if item is None:
            break

        with counter_lock:
            cell_counter[0] += 1
            cell_idx = cell_counter[0]

        outcome = run_cell(
            item,
            cell_idx,
            total_cells,
            campaign_id,
            informants_path,
            failures_path,
            stats,
            log_fh,
        )

        if outcome in ("PASS", "FAILED"):
            time.sleep(sleep_s)

        cell_queue.task_done()


# ---------------------------------------------------------------------------
# Models-complete counter (for stop-condition check)
# ---------------------------------------------------------------------------

def count_models_with_complete_triples(
    campaign_id: str,
    model_ids: list[str],
    informants_path: Path,
    failures_path: Path,
) -> int:
    """Return how many models have at least one fully-completed (>=5 records) triple.

    A model is considered "complete" if its (model_id, v1_s1, food) triple
    has >= N_RUNS_PER_CELL records in informants.jsonl for this campaign.
    """
    campaign_marker = f"campaign_id={campaign_id}"
    counts = count_completed_cells(campaign_marker, informants_path, failures_path)
    n_complete = 0
    for model_id in model_ids:
        key = (model_id, "v1_s1", "food")
        if counts.get(key, 0) >= N_RUNS_PER_CELL:
            n_complete += 1
    return n_complete


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    """Entry point for the Phase 6 T13 food domain collection driver."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    signal.signal(signal.SIGINT, _handle_sigint)

    parser = argparse.ArgumentParser(
        description=(
            "Phase 6 T13 food domain collection driver. "
            "9 models x v1_s1 x 5 runs x 1 domain (food) = 45 target cells. "
            "See docs/status/2026-05-15-phase6-T13-architect-plan.md."
        ),
    )
    parser.add_argument(
        "--campaign-id",
        default=None,
        help=(
            "Campaign identifier written into qa_notes "
            "(default: phase6-t13-food-{today UTC date})."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print the run plan and exit without making any API calls.",
    )
    args = parser.parse_args()

    # Campaign ID
    if args.campaign_id:
        campaign_id = args.campaign_id
    else:
        today = datetime.now(tz=UTC).strftime("%Y-%m-%d")
        campaign_id = f"phase6-t13-food-{today}"

    campaign_marker = f"campaign_id={campaign_id}"

    # Registry validation
    if not MODEL_REGISTRY:
        print(
            "ERROR: No models in registry. Run:\n"
            "  python scripts/discover_models.py --update-registry",
            file=sys.stderr,
        )
        return 1

    missing_models = [m for m in FOOD_MODEL_IDS if m not in MODEL_REGISTRY]
    if missing_models:
        print(
            f"ERROR: The following models are missing from MODEL_REGISTRY: "
            f"{missing_models}. "
            "Run: python scripts/discover_models.py --update-registry",
            file=sys.stderr,
        )
        return 1

    # Ensure output directories exist
    INFORMANTS_JSONL.parent.mkdir(parents=True, exist_ok=True)
    FAILURES_JSONL.parent.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    log_path = LOGS_DIR / f"{campaign_id}.log"

    # Idempotence check
    print(f"Campaign: {campaign_id}")
    completed_counts = count_completed_cells(
        campaign_marker,
        INFORMANTS_JSONL,
        FAILURES_JSONL,
    )
    n_already_complete = sum(
        1
        for (mid, pv, domain), n in completed_counts.items()
        if n >= N_RUNS_PER_CELL
        and mid in FOOD_MODEL_IDS
        and pv in FOOD_PROMPT_VERSIONS
        and domain in FOOD_DOMAINS
    )
    logger.info("Completed triples at start of run: %d", n_already_complete)

    # Dry-run mode
    if args.dry_run:
        plan = build_run_plan(FOOD_MODEL_IDS, completed_counts)
        _total = (
            len(FOOD_MODEL_IDS) * len(FOOD_PROMPT_VERSIONS)
            * N_RUNS_PER_CELL * len(FOOD_DOMAINS)
        )
        print(f"\nDRY RUN — Phase 6 T13 food campaign: {campaign_id}")
        print(
            f"  Total target cells: {len(FOOD_MODEL_IDS)} models x "
            f"{len(FOOD_PROMPT_VERSIONS)} variants x "
            f"{N_RUNS_PER_CELL} runs x {len(FOOD_DOMAINS)} domains = {_total}"
        )
        print(f"  Cells remaining in plan: {len(plan)}")
        print(f"  Triples already complete (>={N_RUNS_PER_CELL}/5): {n_already_complete}")
        print(f"  Log path: {log_path}")
        print()
        print("  Model registry check:")
        for mid in FOOD_MODEL_IDS:
            ref = MODEL_REGISTRY.get(mid)
            status = f"OK  method={ref.collection_method}" if ref else "MISSING"
            print(f"    {mid}: {status}")
        print()
        print("  Variant directories check:")
        prompts_base = Path("packages/cdb_collect/cdb_collect/prompts")
        for pv in FOOD_PROMPT_VERSIONS:
            pv_dir = prompts_base / pv
            status = "OK" if pv_dir.exists() else "MISSING"
            print(f"    {pv}: {status}")
        print()
        print("  Sample of first 10 plan cells:")
        for i, cell in enumerate(plan[:10], 1):
            print(
                f"    [{i}] model={cell.model_id}  variant={cell.prompt_version}  "
                f"domain={cell.domain}  run={cell.run_index}"
            )
        if len(plan) > 10:
            print(f"    ... and {len(plan) - 10} more cells")
        print()
        print("DRY RUN complete. No API calls made.")
        return 0

    # Preflight pings
    active_models, skipped_by_provider = run_preflight(FOOD_MODEL_IDS, dry_run=False)
    if skipped_by_provider:
        for method, skipped_mids in sorted(skipped_by_provider.items()):
            logger.warning(
                "WARN: provider %s quota-exhausted at preflight; skipping models %s",
                method,
                skipped_mids,
            )
        print(
            f"\nWARNING: {sum(len(v) for v in skipped_by_provider.values())} model(s) "
            "skipped due to provider quota-exhausted at preflight."
        )

    # Build run plan
    plan = build_run_plan(active_models, completed_counts)
    total_cells = len(plan)

    print(
        f"\nPhase 6 T13 food campaign: {campaign_id}\n"
        f"  Active models: {len(active_models)}/{len(FOOD_MODEL_IDS)}\n"
        f"  Cells to collect: {total_cells}\n"
        f"  Output: {INFORMANTS_JSONL}\n"
        f"  Failures: {FAILURES_JSONL}\n"
        f"  Log: {log_path}\n"
    )

    if total_cells == 0:
        print("All cells already complete. Nothing to collect.")
        n_complete = count_models_with_complete_triples(
            campaign_id, FOOD_MODEL_IDS, INFORMANTS_JSONL, FAILURES_JSONL
        )
        print(f"Models with complete triples: {n_complete}/{len(FOOD_MODEL_IDS)}")
        if n_complete < MIN_MODELS_COMPLETE:
            print(
                f"\nSTOP CONDITION: fewer than {MIN_MODELS_COMPLETE} models complete "
                f"({n_complete}/{len(FOOD_MODEL_IDS)}). "
                "Pause and route back to Architect/CDA SME before running cdb_analyze. "
                "Per Architect plan §10 risk #1 and CDA SME verdict stop-condition note."
            )
            return 3
        return 0

    # Group cells by provider for parallel dispatch
    provider_queues: dict[str, queue.Queue[FoodCell | None]] = {}
    for cell in plan:
        ref = MODEL_REGISTRY.get(cell.model_id)
        if not ref:
            continue
        method = ref.collection_method
        if method not in provider_queues:
            provider_queues[method] = queue.Queue()
        provider_queues[method].put(cell)

    stats = CampaignStats(cells_remaining=list(plan))
    cell_counter: list[int] = [0]
    counter_lock = threading.Lock()

    with open(log_path, "a", encoding="utf-8") as log_fh:
        ts = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        log_fh.write(
            f"{ts} Phase 6 T13 food campaign START: {campaign_id} "
            f"cells={total_cells}\n"
        )
        log_fh.flush()

        # Launch provider threads
        threads: list[threading.Thread] = []
        for method, q in provider_queues.items():
            n_workers = PROVIDER_WORKERS.get(method, 1)
            for _ in range(n_workers):
                q.put(None)
            for worker_idx in range(n_workers):
                t = threading.Thread(
                    target=provider_worker,
                    name=f"provider-{method}-{worker_idx}",
                    args=(
                        method,
                        q,
                        campaign_id,
                        INFORMANTS_JSONL,
                        FAILURES_JSONL,
                        stats,
                        log_fh,
                        total_cells,
                        cell_counter,
                        counter_lock,
                    ),
                    daemon=True,
                )
                threads.append(t)
                t.start()

        for t in threads:
            t.join()

        ts = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        log_fh.write(
            f"{ts} Phase 6 T13 food campaign END: {campaign_id} "
            f"pass={stats.n_pass} failed={stats.n_failed} "
            f"skipped={stats.n_skipped}\n"
        )

    # Final summary
    print()
    print("=" * 70)
    print("Phase 6 T13 food campaign summary")
    print("=" * 70)
    print(f"  Campaign:      {campaign_id}")
    print(f"  Cells PASS:    {stats.n_pass}")
    print(f"  Cells FAILED:  {stats.n_failed}")
    print(f"  Cells SKIPPED: {stats.n_skipped}")
    print(f"  Log:           {log_path}")

    # Count models with complete triples
    n_complete = count_models_with_complete_triples(
        campaign_id, FOOD_MODEL_IDS, INFORMANTS_JSONL, FAILURES_JSONL
    )
    print(f"\nModels with complete triples (>={N_RUNS_PER_CELL} records): "
          f"{n_complete}/{len(FOOD_MODEL_IDS)}")

    # Stop condition check
    if n_complete < MIN_MODELS_COMPLETE:
        print(
            f"\nSTOP CONDITION: fewer than {MIN_MODELS_COMPLETE} models complete "
            f"({n_complete}/{len(FOOD_MODEL_IDS)}). "
            "Pause and route back to Architect/CDA SME before running cdb_analyze. "
            "Per Architect plan §10 risk #1 and CDA SME verdict stop-condition note."
        )
        return 3

    if _shutdown_requested:
        print(
            f"\nResume with:\n"
            f"  python scripts/run_phase6_t13_food.py "
            f"--campaign-id {campaign_id}"
        )
        return 0

    if stats.n_failed > 0:
        print(
            f"\nNOTE: {stats.n_failed} cell(s) still in failures.jsonl. "
            "Per failures-as-findings posture, these are canonical data."
        )
        print(
            f"\nResume with:\n"
            f"  python scripts/run_phase6_t13_food.py "
            f"--campaign-id {campaign_id}"
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
