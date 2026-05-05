"""OpenRouter full-cycle probe (2026-05-05) — Stage 1.7.

End-to-end CDA protocol cycles for the two OpenRouter models that had
recoverable Phase 4a failures: ``z-ai/glm-5.1`` (6 failures, Group A
reasoning-budget pattern per Stage 1.5b) and
``meta-llama/llama-4-maverick`` (4 failures, Group B output-truncation
pattern). Stage 1.5b probed only the pile-sort step in isolation; this
probe validates that the full free-list → pile-sort → interview cycle
succeeds end-to-end on the production OpenRouterAdapter (post-Task 16.A
merge, commit ``7f8f7f7``).

Pass criterion per model: ≥ 8 / 10 successful informants. Pass on both
green-lights the Phase 4a corpus recovery campaign for the 10 cells
those two models contribute. (The 10 Gemini cells were already
green-lit by Stage 1.6 on 2026-05-04.)

Output goes to ``data/probes/`` (gitignored). Records are stamped with
``campaign_id=openrouter-fullcycle-probe-2026-05-05``.

Production adapter is used unmodified — Task 16.A's bumped
``max_tokens=16384`` and ``include_reasoning=True`` are now live in the
canonical adapter, so this probe doubles as a smoke test on the merged
code against real models.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

from cdb_collect.domains import load_domain
from cdb_collect.exceptions import PartialSessionError
from cdb_collect.jsonl import append_failure, append_record
from cdb_collect.runner import run_informant
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from collect import MODEL_REGISTRY, _create_adapter  # noqa: E402

load_dotenv()
logging.basicConfig(level=logging.WARNING)

CAMPAIGN_ID = "openrouter-fullcycle-probe-2026-05-05"
PROBE_DIR = Path("data/probes")
INFORMANTS_OUT = PROBE_DIR / "2026-05-05-openrouter-fullcycle-informants.jsonl"
FAILURES_OUT = PROBE_DIR / "2026-05-05-openrouter-fullcycle-failures.jsonl"

MODELS = (
    "z-ai/glm-5.1",
    "meta-llama/llama-4-maverick",
)
DOMAINS = ("family", "holidays")
RUNS_PER_DOMAIN = 5
PASS_THRESHOLD = 8


async def run_one_informant(
    adapter, domain_slug: str, run_index: int, model_id: str,
) -> tuple[bool, str | None]:
    """Run a single full informant cycle. Returns (success, failed_step)."""
    domain = load_domain(domain_slug)
    label = f"{model_id}  {domain_slug} #{run_index + 1}"
    print(f"  [{label}] starting...", flush=True)

    try:
        record = await run_informant(
            adapter, domain, run_index, campaign_id=CAMPAIGN_ID,
        )
        append_record(record, INFORMANTS_OUT)
        n_items = len(record.freelist.parsed_items or [])
        n_piles = len(record.pile_sort.parsed_piles or [])
        n_labels = len(record.interview.parsed_pile_labels or [])
        print(
            f"    SUCCESS  freelist_n={n_items}  "
            f"piles_n={n_piles}  labels_n={n_labels}",
        )
        return (True, None)
    except PartialSessionError as exc:
        append_failure(
            exc.cause,
            {
                "model_id": model_id,
                "domain": domain_slug,
                "run_index": run_index,
                "failed_step": exc.failed_step,
                "campaign_id": CAMPAIGN_ID,
            },
            FAILURES_OUT,
            prompt_verbatim=exc.prompt_verbatim,
            response_verbatim=exc.response_verbatim,
            thinking_verbatim=exc.thinking_verbatim,
            stop_reason=exc.stop_reason,
            partial_session=exc.partial_session or None,
            retry_attempts=exc.retry_attempts or None,
        )
        cause_msg = str(exc.cause)
        if len(cause_msg) > 140:
            cause_msg = cause_msg[:140] + "..."
        print(
            f"    FAILURE  step={exc.failed_step}  "
            f"{type(exc.cause).__name__}: {cause_msg}",
        )
        return (False, exc.failed_step)
    except Exception as exc:
        append_failure(
            exc,
            {
                "model_id": model_id,
                "domain": domain_slug,
                "run_index": run_index,
                "campaign_id": CAMPAIGN_ID,
            },
            FAILURES_OUT,
        )
        msg = str(exc)
        if len(msg) > 140:
            msg = msg[:140] + "..."
        print(f"    FAILURE  {type(exc).__name__}: {msg}")
        return (False, "unknown")


async def main() -> int:
    PROBE_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Probe: full-cycle CDA for {len(MODELS)} OpenRouter models")
    print(f"Outputs: {INFORMANTS_OUT}, {FAILURES_OUT}")
    print(f"Campaign: {CAMPAIGN_ID}")
    print()

    overall_results: dict[str, tuple[int, int, dict[str, int]]] = {}

    for model_id in MODELS:
        model_ref = MODEL_REGISTRY.get(model_id)
        if model_ref is None:
            print(f"ERROR: {model_id} not in registry", file=sys.stderr)
            return 1

        adapter = _create_adapter(model_ref)
        successes = 0
        failures = 0
        failed_steps: dict[str, int] = {}

        for domain_slug in DOMAINS:
            for run_index in range(RUNS_PER_DOMAIN):
                ok, step = await run_one_informant(
                    adapter, domain_slug, run_index, model_id,
                )
                if ok:
                    successes += 1
                else:
                    failures += 1
                    if step is not None:
                        failed_steps[step] = failed_steps.get(step, 0) + 1

        overall_results[model_id] = (successes, failures, failed_steps)
        print()

    print("=" * 70)
    print("OpenRouter full-cycle probe summary")
    print("=" * 70)
    overall_pass = True
    for model_id, (s, f, steps) in overall_results.items():
        total = s + f
        verdict = "PASS" if s >= PASS_THRESHOLD else "FAIL"
        if s < PASS_THRESHOLD:
            overall_pass = False
        print(f"  {model_id}")
        print(f"    Successes: {s} / {total}    [{verdict}]")
        if f > 0:
            print(f"    Failures:  {f} / {total}    failed_steps={steps}")
    print()
    print(
        f"  Overall pass criterion (both models ≥ {PASS_THRESHOLD}/10): "
        f"{'PASS' if overall_pass else 'FAIL'}",
    )
    print(f"  Informants: {INFORMANTS_OUT}")
    print(f"  Failures:   {FAILURES_OUT}")
    return 0 if overall_pass else 2


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
