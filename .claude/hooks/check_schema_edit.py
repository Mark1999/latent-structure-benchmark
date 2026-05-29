#!/usr/bin/env python3
"""DRAFT — INACTIVE. PreToolUse guard: schema edits need Architect sign-off.

NOT wired into settings.json yet. See
docs/proposed/2026-05-29-tier1-2-activation-runbook.md before enabling.

CLAUDE.md rule 6: never edit cdb_core/schemas.py without Architect sign-off; changes
to InformantRecord / GroundingRef require a matching DATA_DICTIONARY.md update in the
same PR (Reviewer R7).

This is intentionally a SOFT gate, NOT a hard block: legitimate schema changes happen
often via the pipeline (e.g. Remedy B T2 added centrality_ci). A hard block would stop
the authorized Coder. So this emits an "ask" decision (confirm before proceeding) plus
a reminder. A PreToolUse hook sees only one tool call, so it CANNOT verify the
DATA_DICTIONARY co-update itself — that remains the Reviewer's R7 check.

Contract assumption (VERIFY at activation): PreToolUse honors a JSON
hookSpecificOutput.permissionDecision="ask". If a given CC version ignores it, this
hook is a harmless no-op reminder (it never hard-blocks). Tighten to exit 2 only if a
hard gate is desired.
"""
import json
import sys

TARGET = "packages/cdb_core/cdb_core/schemas.py"

def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # fail-open
    if payload.get("tool_name") not in {"Write", "Edit", "MultiEdit"}:
        sys.exit(0)
    fp = (payload.get("tool_input", {}) or {}).get("file_path", "") or ""
    if fp.replace("\\", "/").endswith(TARGET):
        reason = (
            "Editing cdb_core/schemas.py — CLAUDE.md rule 6 requires Architect sign-off, "
            "and InformantRecord/GroundingRef changes need a matching DATA_DICTIONARY.md "
            "update in the SAME commit (Reviewer R7). Confirm the sign-off exists before "
            "proceeding."
        )
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": reason,
            }
        }))
        sys.exit(0)
    sys.exit(0)

if __name__ == "__main__":
    main()
