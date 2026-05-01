"""Adapter preflight for Phase 4a — exercises all 5 collection_methods.

For each collection_method in the Phase 4a slate, fires one probe call
and verifies:
  - Auth works (no 401/403 or credential error)
  - model_version_returned is populated in the response
  - Response parses into the adapter's AdapterResult shape (no parse error)
  - The call completes within 60 seconds

The probe prompt is NOT a CDA domain prompt. It does not reference cultural
domain terms and produces no data that could leak into the canonical corpus.
This script DOES NOT write to data/raw/informants.jsonl.

See ARCHITECTURE.md §4.1 (adapter interface).
Task spec: docs/status/2026-04-22-phase4a-kickoff-architect-verdict.md §4 T1
"""

from __future__ import annotations

import asyncio
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv

# Load .env before importing adapters (adapters read env at construction time)
load_dotenv()

from cdb_collect.adapters import (  # noqa: E402
    AnthropicAdapter,
    GeminiAdapter,
    OpenAICompatAdapter,
    OpenRouterAdapter,
)
from cdb_collect.adapters.base import AdapterResult  # noqa: E402
from cdb_core import ModelRef  # noqa: E402

# ---------------------------------------------------------------------------
# Probe configuration
# ---------------------------------------------------------------------------

# The probe prompt: short, model-agnostic, and NOT a CDA domain prompt.
# Does not reference family, holidays, food, or any cultural domain term.
PROBE_PROMPT = "Reply with exactly the word 'ok' and nothing else."

# Timeout for each individual probe call (seconds)
PROBE_TIMEOUT_S = 60.0

# Report output path
REPORT_PATH = Path("docs/status/2026-04-22-phase4a-preflight.md")

# Registry for constructing ModelRef objects
REGISTRY_PATH = Path("data/models/registry.json")

# ---------------------------------------------------------------------------
# Probe slate — one representative model per collection_method
# ---------------------------------------------------------------------------
# Each entry: (collection_method, model_id_in_registry, reason)

PROBE_SLATE: list[tuple[str, str, str]] = [
    (
        "anthropic_api",
        "anthropic/claude-sonnet-4.6",
        "Cheapest Claude on Phase 4a slate",
    ),
    (
        "openai_api",
        "openai/gpt-5.4-mini",
        "Cheapest GPT on Phase 4a slate",
    ),
    (
        "google_ai",
        "google/gemini-2.5-pro",
        "Google Gemini slate model (direct google_ai adapter)",
    ),
    (
        "xai_api",
        "x-ai/grok-4",
        "Critical never-canonically-tested adapter — Phase 4a slate model",
    ),
    (
        "openrouter",
        "mistralai/mistral-small-2603",
        "EU slate model via OpenRouter; exercises same adapter path as all openrouter models",
    ),
]


# ---------------------------------------------------------------------------
# Registry loading — build ModelRef from registry.json
# ---------------------------------------------------------------------------

_METHOD_TO_PROVIDER: dict[str, str] = {
    "anthropic_api": "anthropic",
    "google_ai": "google",
    "xai_api": "xai",
    "openai_api": "openai",
    "openrouter": "openrouter",
    "huggingface": "huggingface",
    "deepseek_api": "openrouter",
    "mistral_api": "openrouter",
}

# Anthropic uses dashes in its direct API model IDs (not dots, no prefix)
_ANTHROPIC_DIRECT: dict[str, str] = {
    "anthropic/claude-sonnet-4.6": "claude-sonnet-4-6",
    "anthropic/claude-opus-4.6": "claude-opus-4-6",
    "anthropic/claude-opus-4.5": "claude-opus-4-5",
    "anthropic/claude-haiku-4.5": "claude-haiku-4-5",
}


def _load_model_ref(registry_id: str) -> ModelRef:
    """Load a ModelRef from the registry by its registry model_id.

    The effective model_id passed to ModelRef uses the direct-API form
    for Anthropic (dashes not dots, no prefix) and the registry form
    for all other providers.
    """
    if not REGISTRY_PATH.exists():
        raise RuntimeError(
            f"Registry not found at {REGISTRY_PATH}. "
            "Run: python scripts/discover_models.py --update-registry"
        )

    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    for entry in data.get("models", []):
        if entry["model_id"] == registry_id:
            method = entry["collection_method"]
            provider = _METHOD_TO_PROVIDER.get(method, "openrouter")

            # Use direct-API ID for Anthropic; registry ID for all others
            effective_id = _ANTHROPIC_DIRECT.get(registry_id, registry_id)

            # Extract version label
            parts = registry_id.split("/")
            version_label = parts[-1] if len(parts) > 1 else registry_id

            # Release date from openrouter_created timestamp
            from datetime import date
            created_ts = entry.get("openrouter_created")
            release = date.fromtimestamp(created_ts) if created_ts else date.today()

            return ModelRef(
                provider=provider,  # type: ignore[arg-type]
                model_id=effective_id,
                family=entry["family"],
                origin=entry["origin"],
                open_weights=entry["open_weights"],
                collection_method=method,  # type: ignore[arg-type]
                quantization=None,
                release_date=release,
                version_label=version_label,
            )

    raise KeyError(f"Model {registry_id!r} not found in registry")


# ---------------------------------------------------------------------------
# Adapter factory
# ---------------------------------------------------------------------------

def _create_adapter(model_ref: ModelRef) -> object:
    """Route a ModelRef to its adapter. Mirrors collect.py _create_adapter."""
    method = model_ref.collection_method
    if method == "anthropic_api":
        return AnthropicAdapter(model_ref)
    if method == "google_ai":
        return GeminiAdapter(model_ref)
    if method in ("openai_api", "xai_api", "deepseek_api", "mistral_api"):
        return OpenAICompatAdapter(model_ref)
    if method == "openrouter":
        return OpenRouterAdapter(model_ref)
    raise ValueError(f"Unknown collection_method: {method}")


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ProbeResult:
    collection_method: str
    model_id: str
    reason: str
    passed: bool
    latency_ms: int
    model_version_returned: str
    input_tokens: int
    output_tokens: int
    response_text: str
    error: str


# ---------------------------------------------------------------------------
# Per-adapter probe
# ---------------------------------------------------------------------------

async def _run_probe(
    collection_method: str,
    registry_id: str,
    reason: str,
) -> ProbeResult:
    """Fire one probe call against the given model and return a ProbeResult."""

    try:
        model_ref = _load_model_ref(registry_id)
    except Exception as exc:
        return ProbeResult(
            collection_method=collection_method,
            model_id=registry_id,
            reason=reason,
            passed=False,
            latency_ms=0,
            model_version_returned="",
            input_tokens=0,
            output_tokens=0,
            response_text="",
            error=f"ModelRef construction failed: {exc}",
        )

    adapter = _create_adapter(model_ref)

    try:
        result: AdapterResult = await asyncio.wait_for(
            adapter.complete(PROBE_PROMPT, temperature=0.0),  # type: ignore[union-attr]
            timeout=PROBE_TIMEOUT_S,
        )
    except TimeoutError:
        return ProbeResult(
            collection_method=collection_method,
            model_id=registry_id,
            reason=reason,
            passed=False,
            latency_ms=int(PROBE_TIMEOUT_S * 1000),
            model_version_returned="",
            input_tokens=0,
            output_tokens=0,
            response_text="",
            error=f"Probe timed out after {PROBE_TIMEOUT_S}s",
        )
    except Exception:
        import traceback
        return ProbeResult(
            collection_method=collection_method,
            model_id=registry_id,
            reason=reason,
            passed=False,
            latency_ms=0,
            model_version_returned="",
            input_tokens=0,
            output_tokens=0,
            response_text="",
            error=traceback.format_exc(),
        )

    # Validate the result
    failures: list[str] = []

    if not result.model_version_returned:
        failures.append("model_version_returned is empty")

    if result.input_tokens <= 0:
        failures.append(f"input_tokens is {result.input_tokens} (expected > 0)")

    if failures:
        return ProbeResult(
            collection_method=collection_method,
            model_id=registry_id,
            reason=reason,
            passed=False,
            latency_ms=result.latency_ms,
            model_version_returned=result.model_version_returned,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            response_text=result.text[:200],
            error="Validation failures: " + "; ".join(failures),
        )

    return ProbeResult(
        collection_method=collection_method,
        model_id=registry_id,
        reason=reason,
        passed=True,
        latency_ms=result.latency_ms,
        model_version_returned=result.model_version_returned,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        response_text=result.text[:200],
        error="",
    )


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------

def _write_report(results: list[ProbeResult], timestamp: str) -> None:
    """Write a Markdown summary to REPORT_PATH."""
    passed_count = sum(1 for r in results if r.passed)

    lines: list[str] = [
        "# Phase 4a Adapter Preflight Report",
        "",
        f"**Timestamp:** {timestamp}",
        f"**Verdict:** {passed_count}/{len(results)} collection_methods PASS",
        "",
        "---",
        "",
        "## Per-method results",
        "",
        "| collection_method | model_id | result | ms"
        " | model_version_returned | in/out |",
        "|---|---|---|---|---|---|",
    ]

    for r in results:
        status = "PASS" if r.passed else "**FAIL**"
        lines.append(
            f"| `{r.collection_method}` | `{r.model_id}` | {status} "
            f"| {r.latency_ms} "
            f"| `{r.model_version_returned}` "
            f"| {r.input_tokens}/{r.output_tokens} |"
        )

    lines += ["", "---", ""]

    for r in results:
        lines += [
            f"## {r.collection_method} — {'PASS' if r.passed else 'FAIL'}",
            "",
            f"- **Model:** `{r.model_id}`",
            f"- **Reason for selection:** {r.reason}",
            f"- **model_version_returned:** `{r.model_version_returned}`",
            f"- **Latency:** {r.latency_ms} ms",
            f"- **Tokens:** {r.input_tokens} input / {r.output_tokens} output",
            f"- **Response text (truncated):** `{r.response_text}`",
        ]
        if r.error:
            lines += [
                "",
                "**Error detail:**",
                "",
                "```",
                r.error,
                "```",
            ]
        lines.append("")

    lines += [
        "---",
        "",
        "## Summary",
        "",
        f"- Probe prompt: `{PROBE_PROMPT}`",
        f"- Timeout per probe: {PROBE_TIMEOUT_S}s",
        f"- Passed: {passed_count}/{len(results)}",
        "",
        "## References",
        "",
        "- Task spec: `docs/status/2026-04-22-phase4a-kickoff-architect-verdict.md §4 T1`",
        "- Slate: `docs/status/2026-04-22-phase4a-slate-cda-sme-verdict.md`",
    ]

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def _main() -> int:
    timestamp = datetime.now(UTC).isoformat()
    print(f"Phase 4a adapter preflight — {timestamp}")
    print(f"Probe prompt: {PROBE_PROMPT!r}")
    print()

    results: list[ProbeResult] = []

    for collection_method, registry_id, reason in PROBE_SLATE:
        print(f"  [{collection_method}] {registry_id} ... ", end="", flush=True)
        r = await _run_probe(collection_method, registry_id, reason)
        results.append(r)

        if r.passed:
            print(
                f"PASS  {r.latency_ms}ms  "
                f"model_version_returned={r.model_version_returned!r}"
            )
        else:
            print("FAIL")
            # Indent error detail for readability
            for line in r.error.splitlines():
                print(f"    {line}")

    print()

    # Summary table
    passed = [r for r in results if r.passed]
    failed = [r for r in results if not r.passed]

    print(f"Results: {len(passed)}/{len(results)} PASS")
    print()

    if failed:
        print("FAILED adapters:")
        for r in failed:
            print(f"  - {r.collection_method} ({r.model_id})")
        print()

    _write_report(results, timestamp)
    print(f"Report written to: {REPORT_PATH}")

    return 0 if len(failed) == 0 else 1


def main() -> int:
    return asyncio.run(_main())


if __name__ == "__main__":
    sys.exit(main())
