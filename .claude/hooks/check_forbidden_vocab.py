#!/usr/bin/env python3
"""DRAFT — INACTIVE. PreToolUse guard: forbidden vocabulary (CLAUDE.md §7).

NOT wired into settings.json yet; cannot fire until activated. See
docs/proposed/2026-05-29-tier1-2-activation-runbook.md before enabling.

Blocks Write/Edit/MultiEdit whose new content contains §7 forbidden vocabulary
applied to models. This is NET-NEW shift-left enforcement (there is no CI
forbidden-vocab grep today) — it catches the violation at write time instead of
only at Reviewer/CI.

Design choices (per CLAUDE.md §7, which says the rule is about text ABOUT models
and the Reviewer uses judgment):
  * Multi-word forbidden phrases are blocked outright.
  * Bare generic terms (worldview/believes/thinks) are blocked ONLY when they
    appear within ~48 chars of a model token (model/claude/gpt/llm/...), to
    avoid false positives on ordinary English (e.g. a code comment "I think
    this loop terminates").
  * Fail-OPEN: if stdin can't be parsed, exit 0 (never brick the session).
Contract: exit 2 + stderr message = block. Verified-needed at activation time.
"""
import json
import re
import sys

# (left-column phrases from CLAUDE.md §7 — case-insensitive)
HARD_PHRASES = [
    r"how models see the world",
    r"what the model understands",
    r"model'?s+ worldview",
    r"models'? worldview",
    r"cultural bias",  # standalone — §7 says use "categorical divergence from [baseline]"
]
# generic terms forbidden only near a model token
PROXIMITY_TERMS = [r"worldview", r"believes?", r"\bthinks?\b"]
MODEL_TOKENS = r"(model|claude|gpt|gemini|llm|opus|sonnet|haiku|deepseek|mistral|grok|qwen)"

def edited_text(ti: dict) -> str:
    parts = []
    if isinstance(ti.get("content"), str):
        parts.append(ti["content"])
    if isinstance(ti.get("new_string"), str):
        parts.append(ti["new_string"])
    for e in ti.get("edits", []) or []:
        if isinstance(e, dict) and isinstance(e.get("new_string"), str):
            parts.append(e["new_string"])
    return "\n".join(parts)

def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # fail-open
    if payload.get("tool_name") not in {"Write", "Edit", "MultiEdit"}:
        sys.exit(0)
    text = edited_text(payload.get("tool_input", {}) or {})
    if not text:
        sys.exit(0)
    low = text.lower()
    hits = [p for p in HARD_PHRASES if re.search(p, low)]
    for term in PROXIMITY_TERMS:
        # term within 48 chars (either side) of a model token
        if re.search(term + r".{0,48}?" + MODEL_TOKENS, low) or \
           re.search(MODEL_TOKENS + r".{0,48}?" + term, low):
            hits.append(term)
    if hits:
        sys.stderr.write(
            "BLOCKED by forbidden-vocabulary guard (CLAUDE.md §7).\n"
            f"  Matched: {sorted(set(hits))}\n"
            "  LSB measures a model's CORPUS LENS, not worldview/belief/cognition.\n"
            "  Use: 'categorizes' / 'outputs pattern as' / 'categorical structure' /\n"
            "       'categorical divergence from [baseline]'. See CLAUDE.md §7.\n"
        )
        sys.exit(2)
    sys.exit(0)

if __name__ == "__main__":
    main()
