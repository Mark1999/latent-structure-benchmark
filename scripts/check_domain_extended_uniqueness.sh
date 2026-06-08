#!/usr/bin/env bash
# check_domain_extended_uniqueness.sh — DomainExtended interface uniqueness guard
#
# Implements the T5-guard from docs/status/2026-06-08-audit-guards-architect-plan.md §5.
# Prevents inline duplicate definitions of `interface DomainExtended` from re-appearing
# outside the canonical location in apps/dashboard/src/data/types.ts.
#
# Background: T5 (docs/status/2026-06-08-T5-architect-plan.md) unified two inline-local
# DomainExtended copies (App.tsx:19-41, ContentArea.tsx:25-47) into a single exported
# canonical definition at types.ts:289. This guard prevents re-drift.
#
# Usage (run from repo root):
#   bash scripts/check_domain_extended_uniqueness.sh
#
# Exit codes:
#   0  Exactly one DomainExtended declaration, at the canonical path  →  PASS
#   1  Zero, duplicate, or misplaced declaration(s)                   →  FAIL

set -euo pipefail

CANONICAL="apps/dashboard/src/data/types.ts"

# Anchored regex: matches `interface DomainExtended` declarations only.
# The leading ^ (start-of-line) + optional whitespace + optional `export` + `interface`
# keyword ensures imports (`import type { DomainExtended }`) and comments are not matched.
# The trailing `([[:space:]<{]|$)` requires the name to be followed by whitespace (the
# canonical `extends ...` form), `<` (generic `DomainExtended<T>`), `{` (direct brace,
# no space), or end-of-line — covering every declaration form while still excluding
# imports/comments/aliases. (Reviewer note 2026-06-08: the plan's `[<{]` would never match
# the canonical `extends` form; `[[:space:]]` alone missed no-space `<`/`{` forms.)
PATTERN='^[[:space:]]*(export[[:space:]]+)?interface[[:space:]]+DomainExtended([[:space:]<{]|$)'

MATCHES=$(git grep -nE "$PATTERN" -- 'apps/dashboard/src/' || true)
# printf '%s' (no trailing newline) keeps the empty case a clean "0" (avoids grep's
# 0-plus-echo-0 double output); the [ -z "$MATCHES" ] branch below is the real zero guard.
MATCH_COUNT=$(printf '%s' "$MATCHES" | grep -c . || true)

if [ "$MATCH_COUNT" -eq 0 ] || [ -z "$MATCHES" ]; then
  echo "::error::Canonical interface DomainExtended is missing from $CANONICAL"
  echo ""
  echo "See docs/status/2026-06-08-T5-architect-plan.md and"
  echo "    docs/status/2026-06-08-audit-guards-architect-plan.md §5."
  exit 1
fi

if [ "$MATCH_COUNT" -ge 2 ]; then
  echo "::error::Duplicate or misplaced interface DomainExtended definition(s):"
  echo "$MATCHES"
  echo ""
  echo "DomainExtended must be defined exactly once at $CANONICAL."
  echo "See docs/status/2026-06-08-T5-architect-plan.md and"
  echo "    docs/status/2026-06-08-audit-guards-architect-plan.md §5."
  exit 1
fi

# Exactly one match — verify it's in the canonical file
MATCH_FILE=$(echo "$MATCHES" | grep -oE '^[^:]+' | head -1)

if [ "$MATCH_FILE" != "$CANONICAL" ]; then
  echo "::error::Duplicate or misplaced interface DomainExtended definition(s):"
  echo "$MATCHES"
  echo ""
  echo "DomainExtended must be defined at $CANONICAL (found at $MATCH_FILE)."
  echo "See docs/status/2026-06-08-T5-architect-plan.md and"
  echo "    docs/status/2026-06-08-audit-guards-architect-plan.md §5."
  exit 1
fi

echo "dashboard-domain-extended-uniqueness-check: PASS"
echo "  Exactly one DomainExtended declaration at $MATCH_FILE"
