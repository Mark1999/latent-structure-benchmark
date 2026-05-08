"""Phase 4b T4 — 20-model × 9-variant variance-arm collection driver.

Drives the variance arm: 20 models × 9 variants (v1_s1…v1_s8 + v2_soft1)
× 5 runs × 2 domains (family, holidays) = 1,800 target cells.

Campaign tag: phase4b-real-2026-05-08 (or --campaign-id override)

Idempotence: before each cell the script checks informants.jsonl +
failures.jsonl for (model_id, prompt_version, domain_slug) triples with the
campaign_id substring in qa_notes.  Already-completed cells (>=5 records for
that triple) are skipped.  The script is restart-safe across tmux sessions.

Provider preflight: at startup one cheap probe is issued per provider.  If a
provider returns 429 / quota-exhausted, those models are excluded from the run
plan and the campaign continues with remaining models.

Spend cap: CDB_MAX_SPEND_USD env var (default $50).  Cost is estimated from
registry pricing fields × tokens accumulated per cell.  When the cap is
crossed the script aborts cleanly and prints a resume command.

Retry budget: 2 attempts per cell (one initial + one retry).  After 2
attempts the failure is appended to failures.jsonl (failures-as-findings
posture; see docs/status/2026-05-07-lsb-philosophy-and-framing.md §9).

Rate limits: Anthropic 50 RPM, OpenAI 500 RPM, Google 60 RPM, xAI 60 RPM,
OpenRouter 200 RPM.  Sequential within each provider with appropriate sleeps;
concurrent across providers via threading.  Each provider thread manages its
own rate-limit sleep.

Signal handling: SIGINT finishes the in-flight cell then exits cleanly with
a resume hint.

Progress: logged to stdout AND to logs/phase4b-variance-{campaign_id}.log.

Usage::

    # Dry-run (validates plan, no API calls)
    uv run python scripts/run_phase4b_variance.py --dry-run

    # Live run
    export CDB_MAX_SPEND_USD=50
    uv run python scripts/run_phase4b_variance.py

    # Live run with explicit campaign-id
    CDB_MAX_SPEND_USD=50 uv run python scripts/run_phase4b_variance.py \\
        --campaign-id phase4b-real-2026-05-08

    # Compute success rates only (reads existing jsonl, appends to log)
    uv run python scripts/run_phase4b_variance.py \\
        --compute-rates-only --campaign-id phase4b-real-2026-05-08

Exit codes:
    0 — clean run (complete or dry-run)
    1 — configuration error
    2 — run completed with at least one cell still failed (finding documented)
    3 — spend cap crossed (partial run; resume with the printed command)

References:
    Architect plan §8 T4:
        docs/status/2026-05-07-phase4b-architect-plan.md
    SME plan verdict (P2, P5, binding):
        docs/status/2026-05-07-phase4b-cda-sme-plan-verdict.md
    Prompt evolution log:
        docs/PROMPT_EVOLUTION_LOG.md
    Philosophy doc §9 (failures-as-findings):
        docs/status/2026-05-07-lsb-philosophy-and-framing.md
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import queue
import signal
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import IO, Any

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

#: 20-model slate from Phase 4b architect plan §3
VARIANCE_MODEL_IDS: list[str] = [
    # Phase 4a spine (12)
    "anthropic/claude-opus-4.6",
    "anthropic/claude-sonnet-4.6",
    "openai/gpt-5.4",
    "openai/gpt-5.4-mini",
    "google/gemini-2.5-pro",
    "x-ai/grok-4.20",
    "meta-llama/llama-4-maverick",
    "mistralai/mistral-small-2603",
    "qwen/qwen3.6-plus",
    "deepseek/deepseek-v3.2",
    "z-ai/glm-5.1",
    "microsoft/phi-4",
    # Phase 4b additions (8)
    "anthropic/claude-opus-4.5",
    "openai/gpt-5.2",
    "google/gemini-2.5-flash",
    "x-ai/grok-4",
    "meta-llama/llama-4-scout",
    "mistralai/mistral-large-2512",
    "cohere/command-a",
    "google/gemma-4-26b-a4b-it",
]

#: 9 variants per Q2 option (B): 8 v1_s* + 1 v2_soft1
VARIANCE_PROMPT_VERSIONS: list[str] = [
    "v1_s1",
    "v1_s2",
    "v1_s3",
    "v1_s4",
    "v1_s5",
    "v1_s6",
    "v1_s7",
    "v1_s8",
    "v2_soft1",
]

#: 2 target domains
VARIANCE_DOMAINS: list[str] = ["family", "holidays"]

#: 5 runs per (model, variant, domain) cell
N_RUNS_PER_CELL: int = 5

#: Retry budget per cell: 1 initial + 1 retry = 2 attempts
MAX_ATTEMPTS_PER_CELL: int = 2

#: Delay between attempt 1 failure and attempt 2 start (seconds)
INTER_ATTEMPT_DELAY_S: int = 5

#: Default spend cap (can be overridden via CDB_MAX_SPEND_USD env var)
DEFAULT_MAX_SPEND_USD: float = 50.0

#: Provider → RPM limits (requests per minute)
PROVIDER_RPM: dict[str, int] = {
    "anthropic_api": 50,
    "openai_api": 500,
    "google_ai": 60,
    "xai_api": 60,
    "openrouter": 200,
}

#: Provider → sleep (seconds) between sequential requests
#: = 60 / RPM; small buffer applied
PROVIDER_SLEEP_S: dict[str, float] = {
    method: 60.0 / rpm + 0.1
    for method, rpm in PROVIDER_RPM.items()
}

INFORMANTS_JSONL = Path("data/raw/informants.jsonl")
FAILURES_JSONL = Path("data/raw/failures.jsonl")
REGISTRY_PATH = Path("data/models/registry.json")
PROMPT_EVOLUTION_LOG = Path("docs/PROMPT_EVOLUTION_LOG.md")
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
class VarianceCell:
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
    total_spend_usd: float = 0.0
    cells_attempted: list[VarianceCell] = field(default_factory=list)
    cells_remaining: list[VarianceCell] = field(default_factory=list)
    # Lock for cross-thread updates
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def add_spend(self, amount: float) -> None:
        with self._lock:
            self.total_spend_usd += amount


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------

def load_registry_map() -> dict[str, dict[str, Any]]:
    """Return a dict of model_id → registry entry dict."""
    if not REGISTRY_PATH.exists():
        return {}
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return {entry["model_id"]: entry for entry in data.get("models", [])}


def estimate_cell_cost_usd(
    model_id: str,
    registry_map: dict[str, dict[str, Any]],
    input_tokens: int,
    output_tokens: int,
) -> float:
    """Estimate USD cost for one cell based on registry pricing.

    Falls back to 0.0 if the model is not in the registry or has no pricing.
    Cost is estimated as:
        (input_tokens / 1e6) * pricing_input_per_m
        + (output_tokens / 1e6) * pricing_output_per_m
    """
    entry = registry_map.get(model_id)
    if not entry:
        return 0.0
    price_in = entry.get("pricing_input_per_m", 0.0) or 0.0
    price_out = entry.get("pricing_output_per_m", 0.0) or 0.0
    return (input_tokens / 1_000_000.0) * price_in + (output_tokens / 1_000_000.0) * price_out


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

def _check_provider_available(collection_method: str, model_id: str) -> bool:
    """Issue a minimal probe to confirm the provider is reachable and not quota-exhausted.

    Returns True if the provider appears healthy (even partial success), False
    if the probe returns 429 or a quota-exhausted signal.

    The probe is a single cheap free-list call on the first available domain.
    Errors other than 429/quota are treated as transient; the provider is
    considered available (the main run will surface the issue per cell).
    """
    import asyncio  # noqa: PLC0415

    from cdb_collect.domains import load_domain  # noqa: PLC0415
    from cdb_collect.runner import run_informant  # noqa: PLC0415

    probe_campaign = "__preflight_probe__"
    probe_domain = "family"

    ref = MODEL_REGISTRY.get(model_id)
    if not ref:
        return False

    adapter = _create_adapter(ref)
    domain = load_domain(probe_domain)

    try:
        asyncio.run(run_informant(adapter, domain, 0, campaign_id=probe_campaign))
        # If it completed without exception, the provider is healthy.
        return True
    except Exception as exc:
        exc_str = str(exc).lower()
        # 429 / quota signals: treat as quota-exhausted; return False.
        # Any other exception (timeout, parse error, etc.) — treat as transient;
        # the cell-level retry budget handles it, so return True.
        return not (
            "429" in exc_str
            or "quota" in exc_str
            or "rate limit" in exc_str
            or "too many requests" in exc_str
            or "resource_exhausted" in exc_str
        )


def run_preflight(
    model_ids: list[str],
    dry_run: bool = False,
) -> tuple[list[str], dict[str, list[str]]]:
    """Run one preflight probe per provider; return (active_models, skipped_by_provider).

    One representative model per provider is pinged.  If the provider returns
    429, ALL models on that provider are excluded from the run plan for this
    session.  The campaign continues with remaining models.

    dry_run=True: skip the actual probe but return all models as active.
    """
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
    """Return a dict mapping (model_id, prompt_version, domain_slug) → n_records.

    Counts records in both informants.jsonl and failures.jsonl that have the
    campaign_marker substring in qa_notes (informants) or context.campaign_id
    (failures).  This is the idempotence check: a triple with n >= N_RUNS_PER_CELL
    records is already complete and will be skipped.
    """
    counts: dict[tuple[str, str, str], int] = {}

    def _inc(model_id: str, prompt_version: str, domain_slug: str) -> None:
        key = (model_id, prompt_version, domain_slug)
        counts[key] = counts.get(key, 0) + 1

    # Check informants.jsonl
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

    # Check failures.jsonl
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
                if context.get("campaign_id", "") != "phase4b-real" and campaign_marker.replace(
                    "campaign_id=", ""
                ) not in (context.get("campaign_id", "") or ""):
                    # Also check qa_notes style
                    qa_notes = rec.get("qa_notes", "") or ""
                    if campaign_marker not in qa_notes:
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
) -> list[VarianceCell]:
    """Build the ordered list of VarianceCells to collect.

    For each (model_id, prompt_version, domain) triple, check if n_completed
    >= N_RUNS_PER_CELL; if so, skip. Otherwise add the remaining run_indices.
    """
    plan: list[VarianceCell] = []
    for model_id in active_models:
        for pv in VARIANCE_PROMPT_VERSIONS:
            for domain in VARIANCE_DOMAINS:
                key = (model_id, pv, domain)
                n_done = completed_counts.get(key, 0)
                n_remaining = max(0, N_RUNS_PER_CELL - n_done)
                for run_idx in range(n_done, n_done + n_remaining):
                    plan.append(VarianceCell(model_id, pv, domain, run_idx))
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
    cell: VarianceCell,
    cell_index: int,
    total: int,
    campaign_id: str,
    informants_path: Path,
    failures_path: Path,
    registry_map: dict[str, dict[str, Any]],
    stats: CampaignStats,
    log_fh: IO[str],
) -> str:
    """Attempt collection of one VarianceCell with 2-attempt retry budget.

    Returns: "PASS" | "FAILED" | "SPEND_CAP"

    Appends the record (or failure) to the appropriate file.
    Updates stats.total_spend_usd.
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
            # Accumulate spend estimate
            in_tok = getattr(record, "input_tokens", 0) or 0
            out_tok = getattr(record, "output_tokens", 0) or 0
            cell_cost = estimate_cell_cost_usd(cell.model_id, registry_map, in_tok, out_tok)
            stats.add_spend(cell_cost)

            append_record(record, informants_path)  # type: ignore[arg-type]

            outcome_msg = f"PASS (spend=${stats.total_spend_usd:.2f})"
            print(outcome_msg)

            ts = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            log_line = (
                f"{ts} model={cell.model_id} variant={cell.prompt_version} "
                f"domain={cell.domain} run={cell.run_index} outcome=PASS "
                f"cell_cost_usd={cell_cost:.4f} total_spend_usd={stats.total_spend_usd:.4f}\n"
            )
            log_fh.write(log_line)
            log_fh.flush()

            logger.info("%s %s -> PASS cell_cost=%.4f", prefix, label, cell_cost)
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

    # Both attempts exhausted — write failure row (failures-as-findings)
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
    cell_queue: queue.Queue[VarianceCell | None],
    campaign_id: str,
    informants_path: Path,
    failures_path: Path,
    registry_map: dict[str, dict[str, Any]],
    stats: CampaignStats,
    log_fh: IO[str],
    total_cells: int,
    max_spend_usd: float,
    cell_counter: list[int],
    counter_lock: threading.Lock,
) -> None:
    """Thread worker: drain the provider's cell queue respecting rate limits.

    Exits when it receives a None sentinel or when shutdown is requested.
    """
    sleep_s = PROVIDER_SLEEP_S.get(provider_method, 0.5)

    while True:
        if _shutdown_requested:
            break

        try:
            item = cell_queue.get(timeout=1.0)
        except queue.Empty:
            continue

        if item is None:
            # Sentinel — no more cells for this provider
            break

        # Check spend cap before each cell
        with stats._lock:
            current_spend = stats.total_spend_usd

        if current_spend >= max_spend_usd:
            # Put the cell back and exit; main thread will detect cap crossed
            cell_queue.put(item)
            logger.warning(
                "Provider %s worker: spend cap $%.2f reached; suspending",
                provider_method,
                max_spend_usd,
            )
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
            registry_map,
            stats,
            log_fh,
        )

        if outcome in ("PASS", "FAILED"):
            # Rate-limit sleep between requests to the same provider
            time.sleep(sleep_s)

        cell_queue.task_done()


# ---------------------------------------------------------------------------
# Success-rate computation (P2-bound)
# ---------------------------------------------------------------------------

def compute_success_rates(
    campaign_id: str,
    model_ids: list[str],
    prompt_versions: list[str],
    domains: list[str],
    informants_path: Path,
    failures_path: Path,
    n_attempts_targeted: int = N_RUNS_PER_CELL,
) -> dict[tuple[str, str, str], dict[str, int | float]]:
    """Compute per-(model_id × prompt_version × domain_slug) success rates.

    Success-rate definition (P2-bound, PROMPT_EVOLUTION_LOG.md preamble):
    - successful: InformantRecord in informants.jsonl with qa_passed=True AND
      campaign_id substring in qa_notes AND matching (model_id, prompt_version,
      domain_slug).
    - failed: record in failures.jsonl with matching context fields, OR
      InformantRecord in informants.jsonl with qa_passed=False and matching.
    - success_rate = n_successful / n_attempts_targeted
      (n_attempts_targeted = 5 for the variance arm, per the plan)

    A cell that required a retry under the 2-attempt budget counts as one
    attempt regardless of provider call count.

    Returns a dict mapping triple → {passed, failed, n_attempts_targeted, success_rate}.
    """
    campaign_marker = f"campaign_id={campaign_id}"

    passed_counts: dict[tuple[str, str, str], int] = {}
    failed_counts: dict[tuple[str, str, str], int] = {}

    # --- Count from informants.jsonl ---
    if informants_path.exists():
        with open(informants_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                qa_notes: str = rec.get("qa_notes") or ""
                if campaign_marker not in qa_notes:
                    continue
                model_id = rec.get("model_id", "")
                prompt_version = rec.get("freelist", {}).get("prompt_version", "")
                domain_slug = rec.get("domain_slug", "")
                qa_passed = rec.get("qa_passed", False)

                if not (model_id and prompt_version and domain_slug):
                    continue

                key = (model_id, prompt_version, domain_slug)
                if qa_passed:
                    passed_counts[key] = passed_counts.get(key, 0) + 1
                else:
                    failed_counts[key] = failed_counts.get(key, 0) + 1

    # --- Count from failures.jsonl ---
    if failures_path.exists():
        with open(failures_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                context = rec.get("context", {})
                ctx_campaign = context.get("campaign_id", "") or ""
                # Also allow qa_notes fallback
                qa_notes_f = rec.get("qa_notes", "") or ""
                if campaign_id not in ctx_campaign and campaign_marker not in qa_notes_f:
                    continue
                model_id = context.get("model_id", "")
                prompt_version = context.get("prompt_version", "")
                domain_slug = context.get("domain", "") or context.get("domain_slug", "")
                if not (model_id and prompt_version and domain_slug):
                    continue
                key = (model_id, prompt_version, domain_slug)
                failed_counts[key] = failed_counts.get(key, 0) + 1

    # --- Assemble results for the requested triples ---
    results: dict[tuple[str, str, str], dict[str, int | float]] = {}
    for model_id in model_ids:
        for pv in prompt_versions:
            for domain in domains:
                key = (model_id, pv, domain)
                n_pass = passed_counts.get(key, 0)
                n_fail = failed_counts.get(key, 0)
                rate = n_pass / n_attempts_targeted if n_attempts_targeted > 0 else 0.0
                results[key] = {
                    "passed": n_pass,
                    "failed": n_fail,
                    "n_attempts_targeted": n_attempts_targeted,
                    "success_rate": rate,
                }

    return results


# ---------------------------------------------------------------------------
# PROMPT_EVOLUTION_LOG.md update (append-only)
# ---------------------------------------------------------------------------

def append_success_rates_to_log(
    campaign_id: str,
    rates: dict[tuple[str, str, str], dict[str, int | float]],
    log_path: Path,
) -> None:
    """Append per-(model × domain) success-rate rows to PROMPT_EVOLUTION_LOG.md.

    Reads the existing log content and appends new rows under each variant's
    "### Campaigns that consumed v1_sN" / "v2_soft1" section.
    Never edits pre-existing rows (append-only convention).
    """
    if not log_path.exists():
        logger.warning("PROMPT_EVOLUTION_LOG.md not found at %s; skipping log update", log_path)
        return

    content = log_path.read_text(encoding="utf-8")

    # Collect rows to append per prompt_version
    rows_by_version: dict[str, list[str]] = {}
    for (model_id, pv, domain), data in sorted(rates.items()):
        n = data["n_attempts_targeted"]
        passed = data["passed"]
        failed = data["failed"]
        rate = data["success_rate"]
        row = (
            f"| {campaign_id} | {model_id} | {domain} "
            f"| {n} | {passed} | {failed} | {rate:.2f} |"
        )
        rows_by_version.setdefault(pv, []).append(row)

    # Build append text: append rows under each variant's campaign table
    # We append before the "---" separator after each variant's section
    lines = content.split("\n")
    output_lines: list[str] = []
    current_version: str | None = None
    rows_appended_for: set[str] = set()

    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect which variant section we're in (match "### v1_sN" or "## v2_soft1")
        if line.startswith("### v1_s") or line.startswith("### v2_soft1"):
            current_version = line.strip("# ").strip()
            # Map "v1_s1 — paraphrase 1 (research-project framing)" → "v1_s1"
            current_version = current_version.split(" — ")[0].split(" ")[0]
            output_lines.append(line)
            i += 1
            continue

        # Detect the pending-row placeholder line and insert our rows after it
        if (
            current_version is not None
            and current_version in rows_by_version
            and current_version not in rows_appended_for
            and "*(Phase 4b T4 — pending)*" in line
        ):
            output_lines.append(line)
            for row in rows_by_version[current_version]:
                output_lines.append(row)
            rows_appended_for.add(current_version)
            i += 1
            continue

        output_lines.append(line)
        i += 1

    new_content = "\n".join(output_lines)
    log_path.write_text(new_content, encoding="utf-8")
    logger.info(
        "Appended success-rate rows to %s for %d variants",
        log_path,
        len(rows_appended_for),
    )


# ---------------------------------------------------------------------------
# Alert helpers
# ---------------------------------------------------------------------------

def _alert_low_success_rates(
    rates: dict[tuple[str, str, str], dict[str, int | float]],
    log_fh: IO[str] | None,
) -> None:
    """Log alerts for triples below the 0.80 alert threshold (P7-adjacent)."""
    for (model_id, pv, domain), data in sorted(rates.items()):
        rate = data["success_rate"]
        if rate < 0.60:
            msg = (
                f"FLAG(success_rate<0.60): model={model_id} variant={pv} "
                f"domain={domain} rate={rate:.2f} — "
                "methodology page will flag this triple as weak-coverage."
            )
            logger.warning(msg)
            print(msg, flush=True)
            if log_fh:
                ts = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
                log_fh.write(f"{ts} {msg}\n")
        elif rate < 0.80:
            msg = (
                f"ALERT(success_rate<0.80): model={model_id} variant={pv} "
                f"domain={domain} rate={rate:.2f} — "
                "logged per PROMPT_EVOLUTION_LOG.md §preamble."
            )
            logger.warning(msg)
            print(msg, flush=True)
            if log_fh:
                ts = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
                log_fh.write(f"{ts} {msg}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    """Entry point for the Phase 4b variance-arm campaign driver."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    # SIGINT handler: finish in-flight cell, then exit
    signal.signal(signal.SIGINT, _handle_sigint)

    parser = argparse.ArgumentParser(
        description=(
            "Phase 4b T4 variance-arm collection driver. "
            "20 models × 9 variants × 5 runs × 2 domains = 1,800 target cells. "
            "See docs/status/2026-05-07-phase4b-architect-plan.md §8 T4."
        ),
    )
    parser.add_argument(
        "--campaign-id",
        default=None,
        help=(
            "Campaign identifier written into qa_notes (default: computed from "
            "today's UTC date as phase4b-real-YYYY-MM-DD)."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print the run plan and exit without making any API calls.",
    )
    parser.add_argument(
        "--compute-rates-only",
        action="store_true",
        default=False,
        help=(
            "Skip collection; read existing jsonl, compute success rates, "
            "append to PROMPT_EVOLUTION_LOG.md and exit."
        ),
    )
    args = parser.parse_args()

    # ── Campaign ID ──────────────────────────────────────────────────────────
    if args.campaign_id:
        campaign_id = args.campaign_id
    else:
        today = datetime.now(tz=UTC).strftime("%Y-%m-%d")
        campaign_id = f"phase4b-real-{today}"

    campaign_marker = f"campaign_id={campaign_id}"

    # ── Spend cap ────────────────────────────────────────────────────────────
    max_spend_usd = float(os.environ.get("CDB_MAX_SPEND_USD", DEFAULT_MAX_SPEND_USD))

    # ── Registry validation ──────────────────────────────────────────────────
    if not MODEL_REGISTRY:
        print(
            "ERROR: No models in registry. Run:\n"
            "  python scripts/discover_models.py --update-registry",
            file=sys.stderr,
        )
        return 1

    registry_map = load_registry_map()

    missing_models = [m for m in VARIANCE_MODEL_IDS if m not in MODEL_REGISTRY]
    if missing_models:
        print(
            f"ERROR: The following models are missing from MODEL_REGISTRY: "
            f"{missing_models}. "
            "Run: python scripts/discover_models.py --update-registry",
            file=sys.stderr,
        )
        return 1

    # ── Ensure output directories exist ─────────────────────────────────────
    INFORMANTS_JSONL.parent.mkdir(parents=True, exist_ok=True)
    FAILURES_JSONL.parent.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    log_path = LOGS_DIR / f"phase4b-variance-{campaign_id}.log"

    # ── Compute-rates-only mode ──────────────────────────────────────────────
    if args.compute_rates_only:
        print(f"Computing success rates for campaign: {campaign_id}")
        rates = compute_success_rates(
            campaign_id,
            VARIANCE_MODEL_IDS,
            VARIANCE_PROMPT_VERSIONS,
            VARIANCE_DOMAINS,
            INFORMANTS_JSONL,
            FAILURES_JSONL,
        )
        with open(log_path, "a", encoding="utf-8") as log_fh:
            _alert_low_success_rates(rates, log_fh)
        append_success_rates_to_log(campaign_id, rates, PROMPT_EVOLUTION_LOG)
        print(f"Success rates appended to {PROMPT_EVOLUTION_LOG}")

        # Print a summary table
        print(f"\n{'model_id':<45} {'variant':<10} {'domain':<10} {'rate':>6}")
        print("-" * 80)
        for (mid, pv, domain), data in sorted(rates.items()):
            rate = data["success_rate"]
            flag = " <ALERT" if rate < 0.80 else (" <FLAG" if rate < 0.60 else "")
            print(f"{mid:<45} {pv:<10} {domain:<10} {rate:>5.2f}{flag}")
        return 0

    # ── Idempotence check ────────────────────────────────────────────────────
    print(f"Campaign: {campaign_id}")
    print(f"Spend cap: ${max_spend_usd:.2f} (CDB_MAX_SPEND_USD)")
    completed_counts = count_completed_cells(
        campaign_marker,
        INFORMANTS_JSONL,
        FAILURES_JSONL,
    )
    n_already_complete = sum(
        1
        for (mid, pv, domain), n in completed_counts.items()
        if n >= N_RUNS_PER_CELL
        and mid in VARIANCE_MODEL_IDS
        and pv in VARIANCE_PROMPT_VERSIONS
        and domain in VARIANCE_DOMAINS
    )
    logger.info("Completed triples at start of run: %d", n_already_complete)

    # ── Dry-run mode ──────────────────────────────────────────────────────────
    if args.dry_run:
        plan = build_run_plan(VARIANCE_MODEL_IDS, completed_counts)
        print(f"\nDRY RUN — Phase 4b variance campaign: {campaign_id}")
        _total = (
            len(VARIANCE_MODEL_IDS) * len(VARIANCE_PROMPT_VERSIONS)
            * N_RUNS_PER_CELL * len(VARIANCE_DOMAINS)
        )
        print(
            f"  Total target cells: {len(VARIANCE_MODEL_IDS)} models × "
            f"{len(VARIANCE_PROMPT_VERSIONS)} variants × "
            f"{N_RUNS_PER_CELL} runs × {len(VARIANCE_DOMAINS)} domains = {_total}"
        )
        print(f"  Cells remaining in plan: {len(plan)}")
        print(f"  Triples already complete (>={N_RUNS_PER_CELL}/5): {n_already_complete}")
        print(f"  Log path: {log_path}")
        print(f"  Spend cap: ${max_spend_usd:.2f}")
        print()
        print("  Model registry check:")
        for mid in VARIANCE_MODEL_IDS:
            ref = MODEL_REGISTRY.get(mid)
            status = f"OK  method={ref.collection_method}" if ref else "MISSING"
            print(f"    {mid}: {status}")
        print()
        print("  Variant directories check:")
        prompts_base = Path("packages/cdb_collect/cdb_collect/prompts")
        for pv in VARIANCE_PROMPT_VERSIONS:
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

    # ── Preflight pings ───────────────────────────────────────────────────────
    active_models, skipped_by_provider = run_preflight(VARIANCE_MODEL_IDS, dry_run=False)
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

    # ── Build run plan ────────────────────────────────────────────────────────
    plan = build_run_plan(active_models, completed_counts)
    total_cells = len(plan)

    print(
        f"\nPhase 4b variance campaign: {campaign_id}\n"
        f"  Active models: {len(active_models)}/{len(VARIANCE_MODEL_IDS)}\n"
        f"  Cells to collect: {total_cells}\n"
        f"  Output: {INFORMANTS_JSONL}\n"
        f"  Failures: {FAILURES_JSONL}\n"
        f"  Log: {log_path}\n"
    )

    if total_cells == 0:
        print("All cells already complete. Nothing to collect.")
        return 0

    # ── Group cells by provider for parallel dispatch ─────────────────────────
    provider_queues: dict[str, queue.Queue[VarianceCell | None]] = {}
    for cell in plan:
        ref = MODEL_REGISTRY.get(cell.model_id)
        if not ref:
            continue
        method = ref.collection_method
        if method not in provider_queues:
            provider_queues[method] = queue.Queue()
        provider_queues[method].put(cell)

    # ── Shared state ──────────────────────────────────────────────────────────
    stats = CampaignStats(cells_remaining=list(plan))
    cell_counter: list[int] = [0]
    counter_lock = threading.Lock()

    # ── Open log file ─────────────────────────────────────────────────────────
    with open(log_path, "a", encoding="utf-8") as log_fh:
        ts = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        log_fh.write(
            f"{ts} Phase 4b variance campaign START: {campaign_id} "
            f"cells={total_cells} spend_cap={max_spend_usd}\n"
        )
        log_fh.flush()

        # ── Launch provider threads ───────────────────────────────────────────
        threads: list[threading.Thread] = []
        for method, q in provider_queues.items():
            # Sentinel to stop the worker
            q.put(None)
            t = threading.Thread(
                target=provider_worker,
                name=f"provider-{method}",
                args=(
                    method,
                    q,
                    campaign_id,
                    INFORMANTS_JSONL,
                    FAILURES_JSONL,
                    registry_map,
                    stats,
                    log_fh,
                    total_cells,
                    max_spend_usd,
                    cell_counter,
                    counter_lock,
                ),
                daemon=True,
            )
            threads.append(t)
            t.start()

        # ── Wait for all threads ──────────────────────────────────────────────
        for t in threads:
            t.join()

        ts = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        log_fh.write(
            f"{ts} Phase 4b variance campaign END: {campaign_id} "
            f"pass={stats.n_pass} failed={stats.n_failed} "
            f"skipped={stats.n_skipped} total_spend_usd={stats.total_spend_usd:.4f}\n"
        )

    # ── Final summary ─────────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("Phase 4b variance campaign summary")
    print("=" * 70)
    print(f"  Campaign:      {campaign_id}")
    print(f"  Cells PASS:    {stats.n_pass}")
    print(f"  Cells FAILED:  {stats.n_failed}")
    print(f"  Cells SKIPPED: {stats.n_skipped}")
    print(f"  Total spend:   ${stats.total_spend_usd:.4f}")
    print(f"  Log:           {log_path}")

    # Spend cap check
    if stats.total_spend_usd >= max_spend_usd:
        print(
            f"\nNOTE: Spend cap ${max_spend_usd:.2f} reached. "
            "Some cells may not have been attempted."
        )
        print(
            f"\nResume with:\n"
            f"  python scripts/run_phase4b_variance.py "
            f"--campaign-id {campaign_id}"
        )
        return 3

    # Compute and append success rates after collection
    print("\nComputing success rates...")
    rates = compute_success_rates(
        campaign_id,
        active_models,
        VARIANCE_PROMPT_VERSIONS,
        VARIANCE_DOMAINS,
        INFORMANTS_JSONL,
        FAILURES_JSONL,
    )
    with open(log_path, "a", encoding="utf-8") as log_fh:
        _alert_low_success_rates(rates, log_fh)
    append_success_rates_to_log(campaign_id, rates, PROMPT_EVOLUTION_LOG)

    if _shutdown_requested:
        print(
            f"\nResume with:\n"
            f"  python scripts/run_phase4b_variance.py "
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
            f"  python scripts/run_phase4b_variance.py "
            f"--campaign-id {campaign_id}"
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
