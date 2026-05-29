#!/usr/bin/env python3
"""DRAFT — INACTIVE. PreToolUse guard: data/raw/informants.jsonl is append-only.

NOT wired into settings.json yet. See
docs/proposed/2026-05-29-tier1-2-activation-runbook.md before enabling.

Enforces CLAUDE.md §9 pitfall 10 + Reviewer R-append-only at write time: an agent
must never Edit/Write/MultiEdit data/raw/informants.jsonl. Appends are made by the
collection tooling (cdb_collect), never via the editing tools. A bad record stays
in place with qa_passed=False; it is not "fixed" by editing.

Contract: exit 2 + stderr = block. Fail-open on parse error.
"""
import json
import sys

TARGET = "data/raw/informants.jsonl"

def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # fail-open
    if payload.get("tool_name") not in {"Write", "Edit", "MultiEdit"}:
        sys.exit(0)
    fp = (payload.get("tool_input", {}) or {}).get("file_path", "") or ""
    # normalize: match whether absolute (/opt/lsb-agent/...) or relative
    if fp.replace("\\", "/").endswith(TARGET):
        sys.stderr.write(
            "BLOCKED: data/raw/informants.jsonl is APPEND-ONLY (CLAUDE.md §9 pitfall 10).\n"
            "  Never Edit/Write this file. New records are appended by cdb_collect only.\n"
            "  A bad record stays in place (qa_passed=False, qa_notes documenting it);\n"
            "  the audit trail must remain intact.\n"
        )
        sys.exit(2)
    sys.exit(0)

if __name__ == "__main__":
    main()
