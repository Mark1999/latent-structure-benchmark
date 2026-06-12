#!/usr/bin/env python3
"""Pre-commit guard: no em dashes (U+2014) in added lines.

Mark's standing hard rule, mechanized per CLAUDE.md section 8 task tiers
("mechanize, don't police"). Replaces per-task Reviewer hunts.

Exemptions:
  - Lines containing an explicit guard marker (EM_DASH, U+2014, u2014, or
    "noqa: em-dash"): these exist to assert the character's ABSENCE in
    tests or to document the rule itself.

Usage: pre-commit passes staged file paths as argv. Exit 1 on violation.
"""

from __future__ import annotations

import subprocess
import sys

EM_DASH = "—"
GUARD_MARKERS = ("EM_DASH", "U+2014", "u2014", "noqa: em-dash")


def added_lines(path: str) -> list[tuple[int, str]]:
    """Return (line_no, text) for lines added in the staged diff of path."""
    out = subprocess.run(
        ["git", "diff", "--cached", "--unified=0", "--", path],
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    lines: list[tuple[int, str]] = []
    lineno = 0
    for raw in out.splitlines():
        if raw.startswith("@@"):
            # @@ -a,b +c,d @@  -> next added lines start at c
            try:
                lineno = int(raw.split("+")[1].split(",")[0].split(" ")[0])
            except (IndexError, ValueError):
                lineno = 0
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            lines.append((lineno, raw[1:]))
            lineno += 1
        elif not raw.startswith("-"):
            lineno += 1
    return lines


def main(paths: list[str]) -> int:
    violations: list[str] = []
    for path in paths:
        for lineno, text in added_lines(path):
            if EM_DASH in text and not any(m in text for m in GUARD_MARKERS):
                violations.append(f"{path}:{lineno}: {text.strip()[:80]}")
    if violations:
        print("Em dash (U+2014) in added lines. Use comma/colon/parens instead.")
        print("(Guard constants may carry 'noqa: em-dash' or an EM_DASH marker.)")
        for v in violations:
            print(f"  {v}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
