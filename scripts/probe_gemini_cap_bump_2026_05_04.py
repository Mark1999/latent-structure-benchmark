"""Gemini cap-bump probe (2026-05-04).

Stage 1.5 follow-up to scripts/probe_gemini_rerun_2026_05_04.py. The original
probe established that Gemini-2.5-pro fails 10/10 on pile_sort with
``stop_reason=MAX_TOKENS, output_tokens=0`` under the production
``max_output_tokens=4096`` cap. This probe confirms the cap is the root
cause by replaying the exact same pile_sort prompt at higher caps:

    A. max_output_tokens=16384, thinking_budget=8192 (bump only)
    B. max_output_tokens=16384, thinking_budget=0   (bump + thinking off)

Output goes to data/probes/. Direct google-genai SDK call — bypasses the
LSB GeminiAdapter so the production adapter stays untouched.
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
OUTPUT = PROBE_DIR / "2026-05-04-gemini-cap-bump-results.jsonl"


def load_pile_sort_prompt() -> tuple[str, str, int]:
    """Pull the first probe failure's pile_sort prompt for replay.

    Returns (prompt, domain, num_items).
    """
    with open(SOURCE_FAILURES, encoding="utf-8") as f:
        rec = json.loads(f.readline())
    prompt = rec.get("prompt_verbatim") or ""
    domain = (rec.get("context") or {}).get("domain", "?")
    fl = (rec.get("partial_session") or {}).get("freelist") or {}
    num_items = len(fl.get("parsed_items") or [])
    return prompt, domain, num_items


async def call_gemini(
    prompt: str, *, max_output_tokens: int, thinking_budget: int,
) -> dict:
    """Direct google-genai call — same shape as adapter._do_call but with
    overridable budgets. Returns a dict suitable for JSONL output.
    """
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    config = types.GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=max_output_tokens,
        thinking_config=types.ThinkingConfig(thinking_budget=thinking_budget),
    )

    start = time.monotonic()
    response = await asyncio.to_thread(
        client.models.generate_content,
        model="gemini-2.5-pro",
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
    finish_reason = (
        response.candidates[0].finish_reason.name
        if response.candidates and response.candidates[0].finish_reason
        else "UNKNOWN"
    )

    # Try to parse the JSON response
    parse_status = "no_text"
    piles_count: int | None = None
    parse_error: str | None = None
    if text:
        try:
            data = json.loads(text)
            parse_status = "ok"
            if isinstance(data, dict) and "piles" in data:
                piles_count = len(data["piles"])
        except json.JSONDecodeError as e:
            parse_status = "json_parse_error"
            parse_error = str(e)

    return {
        "max_output_tokens": max_output_tokens,
        "thinking_budget": thinking_budget,
        "finish_reason": finish_reason,
        "input_tokens": (usage.prompt_token_count or 0) if usage else 0,
        "output_tokens": (usage.candidates_token_count or 0) if usage else 0,
        "thoughts_tokens": (
            getattr(usage, "thoughts_token_count", None) or 0
        ) if usage else 0,
        "text_len": len(text),
        "thinking_len": len(thinking_text),
        "latency_ms": latency_ms,
        "parse_status": parse_status,
        "piles_count": piles_count,
        "parse_error": parse_error,
        "text_first_500": text[:500],
        "thinking_first_300": thinking_text[:300],
    }


async def main() -> int:
    PROBE_DIR.mkdir(parents=True, exist_ok=True)

    prompt, domain, num_items = load_pile_sort_prompt()
    print(f"Replaying pile_sort prompt: domain={domain} items={num_items} "
          f"prompt_len={len(prompt)} chars")
    print()

    # Cell B uses thinking_budget=128 (minimum allowed for gemini-2.5-pro;
    # the model rejects 0 with "This model only works in thinking mode").
    cells = [
        ("A — bump only (16384 / 8192)", 16384, 8192),
        ("B — bump + min thinking (16384 / 128)", 16384, 128),
        ("C — production cap as control (4096 / 8192)", 4096, 8192),
    ]

    results: list[dict] = []
    for label, max_t, think_b in cells:
        print(f"  [{label}] calling...", flush=True)
        try:
            result = await call_gemini(
                prompt, max_output_tokens=max_t, thinking_budget=think_b,
            )
            result["label"] = label
            results.append(result)
            print(
                f"    finish={result['finish_reason']:12s}  "
                f"out_tokens={result['output_tokens']:5d}  "
                f"thoughts={result['thoughts_tokens']:5d}  "
                f"text_len={result['text_len']:6d}  "
                f"parse={result['parse_status']}  "
                f"piles={result['piles_count']}",
            )
        except Exception as exc:
            err_str = str(exc)
            if len(err_str) > 200:
                err_str = err_str[:200] + "..."
            print(f"    EXCEPTION  {type(exc).__name__}: {err_str}")
            results.append({
                "label": label,
                "max_output_tokens": max_t,
                "thinking_budget": think_b,
                "exception_type": type(exc).__name__,
                "exception_str": str(exc),
            })

    # Write all results
    with open(OUTPUT, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    print()
    print(f"Results written: {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
