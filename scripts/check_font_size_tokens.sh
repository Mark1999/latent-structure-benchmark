#!/usr/bin/env bash
# check_font_size_tokens.sh — dashboard font-size token recurrence guard
#
# Implements the T3-guard from docs/status/2026-06-08-audit-guards-architect-plan.md §4.
# Guards against CLAUDE.md §9 pitfall #15 (undefined CSS custom property references).
#
# Derives the allow-list at runtime from tokens.css so the guard stays in sync
# when new --font-size-* tokens are added to the design system.
#
# Usage (run from repo root):
#   bash scripts/check_font_size_tokens.sh
#
# Exit codes:
#   0  No undefined font-size token references found  →  PASS
#   1  One or more undefined font-size token references found  →  FAIL

set -euo pipefail

TOKENS_CSS="apps/dashboard/src/styles/tokens.css"

# --- Derive allow-list from tokens.css at runtime ---
# Extracts suffixes like: xs, sm, base, lg, xl, 2xl, 3xl
# Pins to tokens.css §1.1 Typography block.
ALLOWED_SUFFIXES=$(grep -E '^\s*--font-size-[a-z0-9-]+:' "$TOKENS_CSS" \
  | sed -E 's/.*--font-size-([a-z0-9-]+):.*/\1/')

if [ -z "$ALLOWED_SUFFIXES" ]; then
  echo "::error::check_font_size_tokens.sh: Could not derive allow-list from $TOKENS_CSS"
  echo "Check that $TOKENS_CSS contains --font-size-* declarations."
  exit 1
fi

# Build an ERE alternation like: xs|sm|base|lg|xl|2xl|3xl
ALLOWED_PATTERN=$(printf '%s\n' "$ALLOWED_SUFFIXES" | paste -sd '|')

# --- Scan for var(--font-size-*) references ---
# Scope: .css, .tsx, .ts files under apps/dashboard/src/
# Exclude: tokens.css itself, test files (__tests__/, *.test.*, *.spec.*)
RAW_REFS=$(git grep -nE 'var\(--font-size-[a-z0-9-]+\)' \
             -- 'apps/dashboard/src/' \
             ':(exclude)apps/dashboard/src/styles/tokens.css' \
             | grep -vE '/__tests__/|\.test\.|\.spec\.' \
             || true)

if [ -z "$RAW_REFS" ]; then
  echo "dashboard-font-size-token-check: PASS"
  echo "  Allow-list derived from $TOKENS_CSS: $ALLOWED_PATTERN"
  echo "  No font-size token references found in scan scope."
  exit 0
fi

# Filter: keep only lines whose suffix is NOT in the allow-list
VIOLATIONS=$(echo "$RAW_REFS" \
  | grep -vE 'var\(--font-size-('"$ALLOWED_PATTERN"')\)' \
  || true)

if [ -n "$VIOLATIONS" ]; then
  echo "::error::Undefined font-size token reference(s):"
  echo "$VIOLATIONS"
  echo ""
  echo "See CLAUDE.md §9 pitfall #15 and DESIGN_SYSTEM.md §1.1."
  echo "All --font-size-* tokens must be declared in $TOKENS_CSS before use."
  exit 1
fi

echo "dashboard-font-size-token-check: PASS"
echo "  Allow-list derived from $TOKENS_CSS: $ALLOWED_PATTERN"
