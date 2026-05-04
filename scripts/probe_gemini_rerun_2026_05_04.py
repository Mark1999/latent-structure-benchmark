"""Gemini-2.5-pro rerun probe (2026-05-04).

Diagnostic probe authorized by Mark on 2026-05-04 as a Stage-1.5 follow-up
to the Phase 4a.1 extended-thinking-vs-CN-origin question. Phase 4a recorded
10/10 Gemini-2.5-pro failures (all parse_failure on pile_sort). This probe
re-runs the 10 attempts to test reproducibility.

Output goes to ``data/probes/`` — separate from the canonical
``data/raw/informants.jsonl`` and ``data/raw/failures.jsonl`` so the
Phase 4a corpus stays immutable. Records are stamped with
``campaign_id=gemini-rerun-probe-2026-05-04`` for downstream filtering.

Not part of any verdict gate chain. One-shot diagnostic. Prints a summary
to stdout when complete.
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

# Reuse the registry + adapter factory from the canonical collector.
sys.path.insert(0, str(Path(__file__).parent))
from collect import MODEL_REGISTRY, _create_adapter  # noqa: E402

load_dotenv()
logging.basicConfig(level=logging.WARNING)

CAMPAIGN_ID = "gemini-rerun-probe-2026-05-04"
PROBE_DIR = Path("data/probes")
INFORMANTS_OUT = PROBE_DIR / "2026-05-04-gemini-rerun-informants.jsonl"
FAILURES_OUT = PROBE_DIR / "2026-05-04-gemini-rerun-failures.jsonl"
MODEL_ID = "google/gemini-2.5-pro"
DOMAINS = ("family", "holidays")
RUNS_PER_DOMAIN = 5


async def main() -> int:
    PROBE_DIR.mkdir(parents=True, exist_ok=True)

    model_ref = MODEL_REGISTRY.get(MODEL_ID)
    if model_ref is None:
        print(f"ERROR: {MODEL_ID} not in registry", file=sys.stderr)
        return 1

    adapter = _create_adapter(model_ref)
    print(f"Probe: {MODEL_ID} via {model_ref.collection_method}")
    print(f"Outputs: {INFORMANTS_OUT}, {FAILURES_OUT}")
    print(f"Campaign: {CAMPAIGN_ID}")
    print()

    successes = 0
    failures = 0
    failure_steps: dict[str, int] = {}

    for domain_slug in DOMAINS:
        domain = load_domain(domain_slug)
        for run_index in range(RUNS_PER_DOMAIN):
            label = f"{domain_slug} #{run_index + 1}"
            print(f"  [{label}] starting...", flush=True)
            try:
                record = await run_informant(
                    adapter, domain, run_index, campaign_id=CAMPAIGN_ID,
                )
                append_record(record, INFORMANTS_OUT)
                successes += 1
                n_items = len(record.freelist.parsed_items or [])
                n_piles = len(record.pile_sort.parsed_piles or [])
                print(
                    f"    SUCCESS  freelist_n={n_items}  piles_n={n_piles}",
                )
            except PartialSessionError as exc:
                append_failure(
                    exc.cause,
                    {
                        "model_id": MODEL_ID,
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
                failures += 1
                failure_steps[exc.failed_step] = (
                    failure_steps.get(exc.failed_step, 0) + 1
                )
                cause_msg = str(exc.cause)
                if len(cause_msg) > 140:
                    cause_msg = cause_msg[:140] + "..."
                print(
                    f"    FAILURE  step={exc.failed_step}  "
                    f"{type(exc.cause).__name__}: {cause_msg}",
                )
            except Exception as exc:
                append_failure(
                    exc,
                    {
                        "model_id": MODEL_ID,
                        "domain": domain_slug,
                        "run_index": run_index,
                        "campaign_id": CAMPAIGN_ID,
                    },
                    FAILURES_OUT,
                )
                failures += 1
                failure_steps["unknown"] = failure_steps.get("unknown", 0) + 1
                msg = str(exc)
                if len(msg) > 140:
                    msg = msg[:140] + "..."
                print(f"    FAILURE  {type(exc).__name__}: {msg}")

    total = successes + failures
    print()
    print("=" * 60)
    print("Gemini rerun probe summary")
    print("=" * 60)
    print(f"  Successes: {successes} / {total}")
    print(f"  Failures:  {failures} / {total}")
    if failure_steps:
        print(f"  Failure steps: {failure_steps}")
    print(f"  Informants out: {INFORMANTS_OUT}")
    print(f"  Failures out:   {FAILURES_OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
