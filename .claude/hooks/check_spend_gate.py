#!/usr/bin/env python3
"""DRAFT — INACTIVE. PreToolUse guard: no spend-gate tokens (CLAUDE.md rule 14).

NOT wired into settings.json yet. See
docs/proposed/2026-05-29-tier1-2-activation-runbook.md before enabling.

Mirrors the CI step `no-spend-gate-check` (.github/workflows/ci.yml) at write time.
LSB has NO software-side spend gates; cost safety is the provider billing dashboards
Mark monitors directly. Blocks Write/Edit/MultiEdit whose new content introduces a
forbidden spend-gate token, honoring the same `noqa: spend-gate-check` escape hatch
the CI grep uses.

FORBIDDEN pattern is kept in lockstep with ci.yml; if the CI pattern changes, update
this too.

Contract: exit 2 + stderr = block. Fail-open on parse error.
"""
import json
import re
import sys

# Keep identical to ci.yml `no-spend-gate-check` FORBIDDEN regex:
FORBIDDEN = re.compile(
    r"CDB_MAX_SPEND_USD|MAX_SPEND_USD|DEFAULT_MAX_SPEND|spend_cap|cost_cap|cost-cap-usd|--max-spend"
)
NOQA = "noqa: spend-gate-check"

def edited_lines(ti: dict):
    parts = []
    if isinstance(ti.get("content"), str):
        parts.append(ti["content"])
    if isinstance(ti.get("new_string"), str):
        parts.append(ti["new_string"])
    for e in ti.get("edits", []) or []:
        if isinstance(e, dict) and isinstance(e.get("new_string"), str):
            parts.append(e["new_string"])
    return "\n".join(parts).splitlines()

def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # fail-open
    if payload.get("tool_name") not in {"Write", "Edit", "MultiEdit"}:
        sys.exit(0)
    hits = [
        ln for ln in edited_lines(payload.get("tool_input", {}) or {})
        if FORBIDDEN.search(ln) and NOQA not in ln
    ]
    if hits:
        sys.stderr.write(
            "BLOCKED: forbidden spend-gate token(s) (CLAUDE.md rule 14, mirrors CI "
            "no-spend-gate-check).\n"
            "  LSB does not implement software-side cost caps/authorization. Remove the\n"
            "  spend-gate construct. (Legitimate exception line: append '# noqa: spend-gate-check'.)\n"
            f"  Offending line(s): {hits[:3]}\n"
        )
        sys.exit(2)
    sys.exit(0)

if __name__ == "__main__":
    main()
