"""Gemini full-cycle probe (2026-05-04) — Stage 1.6.

End-to-end CDA protocol cycle (free-list → pile-sort → interview) for
google/gemini-2.5-pro at the bumped caps confirmed by the Stage 1.5
probes. Tests whether the cap fix unblocks Gemini end-to-end, not just
on the pile-sort step in isolation.

If this passes (≥ 8 / 10 successful informants), the cap fix is the
right answer and task #16 (adaptive max_tokens across all adapters) is
green-lit for the formal Architect → CDA SME → Coder → Reviewer →
Tester gate chain.

If this fails, the failure pattern shapes the methodology-exclusion
writeup for excluding Gemini from the LSB slate.

The probe substitutes a `_BumpedGeminiAdapter` for the production
GeminiAdapter at runtime (probe-local subclass — production adapter is
untouched). All three steps use the same generous caps:
``max_output_tokens=16384, thinking_budget=1024``. If a single global
cap suffices end-to-end, per-step adaptive sizing is an optimization
rather than a correctness requirement.

Output goes to ``data/probes/`` (gitignored). Records are stamped with
``campaign_id=gemini-fullcycle-probe-2026-05-04``.
"""

from __future__ import annotations

import asyncio
import logging
import sys
import time
from pathlib import Path

from cdb_collect.adapters.base import AdapterResult
from cdb_collect.adapters.google import GeminiAdapter
from cdb_collect.domains import load_domain
from cdb_collect.exceptions import PartialSessionError
from cdb_collect.jsonl import append_failure, append_record
from cdb_collect.runner import run_informant
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from collect import MODEL_REGISTRY, _create_adapter  # noqa: E402

load_dotenv()
logging.basicConfig(level=logging.WARNING)

CAMPAIGN_ID = "gemini-fullcycle-probe-2026-05-04"
PROBE_DIR = Path("data/probes")
INFORMANTS_OUT = PROBE_DIR / "2026-05-04-gemini-fullcycle-informants.jsonl"
FAILURES_OUT = PROBE_DIR / "2026-05-04-gemini-fullcycle-failures.jsonl"
MODEL_ID = "google/gemini-2.5-pro"
DOMAINS = ("family", "holidays")
RUNS_PER_DOMAIN = 5

BUMPED_MAX_OUTPUT_TOKENS = 16384
BUMPED_THINKING_BUDGET = 1024


class _BumpedGeminiAdapter(GeminiAdapter):
    """Probe-local subclass that overrides max_output_tokens and
    thinking_budget. Production adapter stays untouched."""

    async def _do_call(  # type: ignore[override]
        self,
        prompt: str,
        *,
        json_schema: dict | None = None,
        temperature: float = 0.7,
    ) -> AdapterResult:
        from google.genai import types

        start = time.monotonic()
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=BUMPED_MAX_OUTPUT_TOKENS,
            thinking_config=types.ThinkingConfig(
                thinking_budget=BUMPED_THINKING_BUDGET,
            ),
        )
        if json_schema is not None:
            config.response_mime_type = "application/json"
            config.response_schema = json_schema

        response = await asyncio.to_thread(
            self._client.models.generate_content,
            model=self._google_model,
            contents=prompt,
            config=config,
        )

        latency_ms = int((time.monotonic() - start) * 1000)

        text = ""
        thinking_text = ""
        if response.candidates:
            content = response.candidates[0].content
            if content and content.parts:
                for part in content.parts:
                    if getattr(part, "thought", False):
                        thinking_text += part.text or ""
                    else:
                        text += part.text or ""

        usage = response.usage_metadata
        input_tokens = (usage.prompt_token_count or 0) if usage else 0
        output_tokens = (usage.candidates_token_count or 0) if usage else 0

        # _build_raw_response is a module-level helper in google.py
        from cdb_collect.adapters.google import _build_raw_response
        raw_response = _build_raw_response(response)

        model_version = self._google_model
        if response.model_version:
            model_version = response.model_version

        return AdapterResult(
            text=text,
            raw_response=raw_response,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            provider_request_id=response.response_id or "",
            model_version_returned=model_version,
            stop_reason=response.candidates[0].finish_reason.name
            if response.candidates and response.candidates[0].finish_reason
            else "unknown",
            thinking_text=thinking_text,
        )


async def main() -> int:
    PROBE_DIR.mkdir(parents=True, exist_ok=True)

    model_ref = MODEL_REGISTRY.get(MODEL_ID)
    if model_ref is None:
        print(f"ERROR: {MODEL_ID} not in registry", file=sys.stderr)
        return 1

    # Verify the production adapter would have been GeminiAdapter
    prod_adapter = _create_adapter(model_ref)
    if not isinstance(prod_adapter, GeminiAdapter):
        print(
            f"ERROR: expected GeminiAdapter, got {type(prod_adapter).__name__}",
            file=sys.stderr,
        )
        return 1

    adapter = _BumpedGeminiAdapter(model_ref)
    print(f"Probe: {MODEL_ID}")
    print(
        f"Caps: max_output_tokens={BUMPED_MAX_OUTPUT_TOKENS}, "
        f"thinking_budget={BUMPED_THINKING_BUDGET} (all 3 steps)"
    )
    print(f"Outputs: {INFORMANTS_OUT}, {FAILURES_OUT}")
    print(f"Campaign: {CAMPAIGN_ID}")
    print()

    successes = 0
    failures = 0
    failed_steps: dict[str, int] = {}

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
                n_labels = len(record.interview.parsed_pile_labels or [])
                print(
                    f"    SUCCESS  freelist_n={n_items}  "
                    f"piles_n={n_piles}  labels_n={n_labels}",
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
                failed_steps[exc.failed_step] = (
                    failed_steps.get(exc.failed_step, 0) + 1
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
                failed_steps["unknown"] = failed_steps.get("unknown", 0) + 1
                msg = str(exc)
                if len(msg) > 140:
                    msg = msg[:140] + "..."
                print(f"    FAILURE  {type(exc).__name__}: {msg}")

    total = successes + failures
    print()
    print("=" * 60)
    print("Gemini full-cycle probe summary")
    print("=" * 60)
    print(f"  Successes: {successes} / {total}")
    print(f"  Failures:  {failures} / {total}")
    if failed_steps:
        print(f"  Failed steps: {failed_steps}")
    pass_threshold = 8
    print(
        f"  Pass criterion: ≥ {pass_threshold} / {total} successes  "
        f"-> {'PASS' if successes >= pass_threshold else 'FAIL'}",
    )
    print(f"  Informants: {INFORMANTS_OUT}")
    print(f"  Failures:   {FAILURES_OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
