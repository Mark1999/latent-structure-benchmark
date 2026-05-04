"""OpenRouter cap-bump probe (2026-05-04).

Tests whether the four non-Gemini Phase 4a parse failures (glm-5.1 ×6,
llama-4-maverick ×4, gpt-5.4-mini ×2, mistral-small-2603 ×1) share the
root cause confirmed for Gemini — a max_output_tokens cap of 4096 that
the model exhausts on internal reasoning before producing any visible
output.

For each of the four models, this probe issues one pile-sort call:

  * `prod` cap: max_tokens=4096   (the production cap; should reproduce
    the original `response_verbatim=''` failure if the cap is the cause)
  * `bumped` cap: max_tokens=16384 (should succeed if the cap is the cause)

Direct call to OpenRouter via the openai-compatible API. Bypasses the
LSB OpenRouter adapter so production code stays untouched. Output goes
to data/probes/ — same diagnostic-data treatment as the Gemini probes.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROBE_DIR = Path("data/probes")
SOURCE_FAILURES = PROBE_DIR / "2026-05-04-gemini-rerun-failures.jsonl"
OUTPUT = PROBE_DIR / "2026-05-04-openrouter-cap-bump-results.jsonl"

# The four affected non-Gemini models (per Stage 1 inventory).
MODELS = (
    "z-ai/glm-5.1",
    "meta-llama/llama-4-maverick",
    "openai/gpt-5.4-mini",
    "mistralai/mistral-small-2603",
)


def load_pile_sort_prompt() -> str:
    """Reuse the same 190-item family prompt the Gemini probe used so
    the comparison is apples-to-apples."""
    with open(SOURCE_FAILURES, encoding="utf-8") as f:
        rec = json.loads(f.readline())
    return rec.get("prompt_verbatim") or ""


async def call_openrouter(
    *, model: str, prompt: str, max_tokens: int,
) -> dict:
    """Direct OpenRouter call via httpx (matches production adapter's
    transport). Returns a dict matching the cap-bump-results schema."""
    import httpx

    api_key = os.environ["OPENROUTER_API_KEY"]
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": 0.3,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(600.0)) as client:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        return {
            "model": model,
            "max_tokens": max_tokens,
            "exception_type": type(exc).__name__,
            "exception_str": str(exc)[:300],
            "latency_ms": int((time.monotonic() - start) * 1000),
        }

    latency_ms = int((time.monotonic() - start) * 1000)

    choice = (data.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    text = message.get("content") or ""
    finish_reason = choice.get("finish_reason") or "UNKNOWN"

    # Reasoning content lives in non-standard fields on OpenRouter
    reasoning = (
        message.get("reasoning_content")
        or message.get("reasoning")
        or ""
    )

    usage = data.get("usage") or {}
    input_tokens = usage.get("prompt_tokens") or 0
    output_tokens = usage.get("completion_tokens") or 0

    # Try parsing as JSON (matches what production runner would attempt)
    parse_status = "no_text"
    piles_count: int | None = None
    parse_error: str | None = None
    if text:
        # Strip markdown code-fence wrapper if present
        stripped = text.strip()
        for fence_open in ("```json\n", "```\n"):
            if stripped.startswith(fence_open):
                stripped = stripped[len(fence_open):]
                break
        if stripped.endswith("```"):
            stripped = stripped[:-3].rstrip()
        try:
            data = json.loads(stripped)
            parse_status = "ok"
            if isinstance(data, dict) and "piles" in data:
                piles_count = len(data["piles"])
        except json.JSONDecodeError as e:
            parse_status = "json_parse_error"
            parse_error = str(e)

    return {
        "model": model,
        "max_tokens": max_tokens,
        "finish_reason": finish_reason,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "text_len": len(text),
        "reasoning_len": len(reasoning),
        "latency_ms": latency_ms,
        "parse_status": parse_status,
        "piles_count": piles_count,
        "parse_error": parse_error,
        "text_first_300": text[:300],
        "reasoning_first_200": reasoning[:200],
    }


async def main() -> int:
    PROBE_DIR.mkdir(parents=True, exist_ok=True)

    if not os.environ.get("OPENROUTER_API_KEY"):
        print("ERROR: OPENROUTER_API_KEY not set", file=sys.stderr)
        return 1

    prompt = load_pile_sort_prompt()
    print(f"Replaying pile_sort prompt: prompt_len={len(prompt)} chars")
    print(f"Models: {len(MODELS)}, calls per model: 2 (prod cap + bumped cap)")
    print()

    results: list[dict] = []
    for model in MODELS:
        for label, max_t in (("prod cap (4096)", 4096), ("bumped (16384)", 16384)):
            print(f"  [{model}  {label}] calling...", flush=True)
            r = await call_openrouter(
                model=model, prompt=prompt, max_tokens=max_t,
            )
            r["label"] = label
            results.append(r)
            if "exception_type" in r:
                print(f"    EXCEPTION  {r['exception_type']}: "
                      f"{r['exception_str'][:120]}")
            else:
                print(
                    f"    finish={r['finish_reason']:14s}  "
                    f"out_tokens={r['output_tokens']:5d}  "
                    f"text_len={r['text_len']:6d}  "
                    f"reasoning_len={r['reasoning_len']:5d}  "
                    f"parse={r['parse_status']:18s}  "
                    f"piles={r['piles_count']}",
                )

    with open(OUTPUT, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    print()
    print(f"Results written: {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
