#!/usr/bin/env python3
"""ACTIVE (wired 2026-06-05). PreToolUse guard: forbidden vocabulary (CLAUDE.md §7).

Wired into .claude/settings.json hooks.PreToolUse per
docs/proposed/2026-05-29-tier1-2-activation-runbook.md.

Blocks Write/Edit/MultiEdit whose new content contains §7 forbidden vocabulary
applied to models. This is NET-NEW shift-left enforcement (there is no CI
forbidden-vocab grep today) — it catches the violation at write time instead of
only at Reviewer/CI.

Design choices (per CLAUDE.md §7, which says the rule is about text ABOUT models
and the Reviewer uses judgment):
  * Multi-word forbidden phrases are blocked outright.
  * Bare generic terms (worldview/believes/thinks) are blocked ONLY near a
    model token (model/claude/gpt/llm/...) within the SAME sentence (~48
    chars, no crossing of ./!/?/newline). Verb terms additionally require the
    model token to PRECEDE them (subject position) — first-person usage in an
    adjacent clause must not trip the guard (e.g. a code comment "I think
    this loop terminates" followed by a sentence naming a model). The noun
    term stays bidirectional ("the worldview of <X>"). Tuned at activation
    (2026-06-05) after a live false positive on exactly that adjacency.
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
# noun terms match in both directions; verb terms require the model token in
# subject (preceding) position. Index 0 is the noun.
BIDIRECTIONAL_TERMS = {PROXIMITY_TERMS[0]}
# proximity span: same sentence only — never across ., !, ? or a newline
SPAN = r"[^.!?\n]{0,48}?"

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
        # model token in subject (preceding) position, same sentence; noun
        # terms ALSO hit in reverse ("the <term> of <model token>")
        if re.search(MODEL_TOKENS + SPAN + term, low) or (
            term in BIDIRECTIONAL_TERMS and re.search(term + SPAN + MODEL_TOKENS, low)
        ):
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
