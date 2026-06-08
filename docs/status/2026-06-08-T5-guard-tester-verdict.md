# T5-guard Tester Verdict — `dashboard-domain-extended-uniqueness-check`

**Date:** 2026-06-08
**Guard commit:** `6ca1c29` (`scripts/check_domain_extended_uniqueness.sh`, tightened regex)
**Plan ref:** `docs/status/2026-06-08-audit-guards-architect-plan.md` §5 + §6
**Reviewer note incorporated:** regex tightened from `([[:space:]]|$)` to `([[:space:]<{]|$)`
**Verdict:** PASS

---

## 1. Baseline (clean tree at `6ca1c29`)

```
dashboard-domain-extended-uniqueness-check: PASS
  Exactly one DomainExtended declaration at apps/dashboard/src/data/types.ts
Exit: 0
```

Single match confirmed at `apps/dashboard/src/data/types.ts:289`. Matches expectation.

---

## 2. Revert-and-confirm-fail results

### 2(a) Duplicate — second `interface DomainExtended` planted in `ContentArea.tsx`

**Planted:** `interface DomainExtended { slug: string; }` at line 5 of
`apps/dashboard/src/components/ContentArea.tsx`.

**Guard output (exit 1):**
```
::error::Duplicate or misplaced interface DomainExtended definition(s):
apps/dashboard/src/components/ContentArea.tsx:5:interface DomainExtended { slug: string; }
apps/dashboard/src/data/types.ts:289:export interface DomainExtended extends DomainResultPublished {

DomainExtended must be defined exactly once at apps/dashboard/src/data/types.ts.
See docs/status/2026-06-08-T5-architect-plan.md and
    docs/status/2026-06-08-audit-guards-architect-plan.md §5.
```

Both file:lines listed in output. Reverted via `git checkout --`. Post-revert: exit 0. CONFIRMED.

### 2(b) Misplaced single — canonical commented out in `types.ts`, copy added in `ContentArea.tsx`

**Planted:** `export interface DomainExtended extends DomainResultPublished {` replaced with
a comment in `types.ts`; `export interface DomainExtended extends Record<string, unknown> { slug: string; }`
added at line 5 of `ContentArea.tsx`.

**Guard output (exit 1):**
```
::error::Duplicate or misplaced interface DomainExtended definition(s):
apps/dashboard/src/components/ContentArea.tsx:5:export interface DomainExtended ...

DomainExtended must be defined at apps/dashboard/src/data/types.ts
(found at apps/dashboard/src/components/ContentArea.tsx).
See docs/status/2026-06-08-T5-architect-plan.md and
    docs/status/2026-06-08-audit-guards-architect-plan.md §5.
```

Distinct "Duplicate or misplaced" message branch triggered (1 match, not in canonical path).
Reverted both files via `git checkout --`. Post-revert: exit 0. CONFIRMED.

### 2(c) Canonical missing — only the canonical in `types.ts` commented out

**Planted:** `export interface DomainExtended extends DomainResultPublished {` replaced with
a comment in `types.ts`. No copy added anywhere else.

**Guard output (exit 1):**
```
::error::Canonical interface DomainExtended is missing from apps/dashboard/src/data/types.ts

See docs/status/2026-06-08-T5-architect-plan.md and
    docs/status/2026-06-08-audit-guards-architect-plan.md §5.
```

Distinct "canonical missing" message branch triggered (0 matches). Reverted via
`git checkout --`. Post-revert: exit 0. CONFIRMED.

### 2(d) Reviewer-note regression — tightened regex catches `DomainExtended<T> {}`

**This is the load-bearing proof that the Reviewer's regex tightening closes a real gap.**

**Planted:** `interface DomainExtended<T> {}` (generic, no space between name and `<`) at
line 5 of `apps/dashboard/src/components/ContentArea.tsx`.

**Gap verification — old regex would have missed it:**
Running the old pattern `([[:space:]]|$)` directly:
```bash
git grep -nE '^[[:space:]]*(export[[:space:]]+)?interface[[:space:]]+DomainExtended([[:space:]]|$)' \
  -- 'apps/dashboard/src/'
```
Output: only `apps/dashboard/src/data/types.ts:289` — the `ContentArea.tsx:5` probe line
was NOT matched. The old regex had a real blind spot for no-space generic/brace forms.

**Guard output with tightened regex (exit 1):**
```
::error::Duplicate or misplaced interface DomainExtended definition(s):
apps/dashboard/src/components/ContentArea.tsx:5:interface DomainExtended<T> {}
apps/dashboard/src/data/types.ts:289:export interface DomainExtended extends DomainResultPublished {

DomainExtended must be defined exactly once at apps/dashboard/src/data/types.ts.
See docs/status/2026-06-08-T5-architect-plan.md and
    docs/status/2026-06-08-audit-guards-architect-plan.md §5.
```

The tightened `([[:space:]<{]|$)` correctly matched `DomainExtended<T>` at line 5.
Reviewer note confirmed: the tightening was necessary and closes the gap. Reverted via
`git checkout --`. Post-revert: exit 0. CONFIRMED.

---

## 3. All three distinct error messages verified

| Failure case | Exit | Message prefix |
|---|---|---|
| 0 matches | 1 | `Canonical interface DomainExtended is missing` |
| 2+ matches | 1 | `Duplicate or misplaced interface DomainExtended definition(s)` |
| 1 match, wrong file | 1 | `Duplicate or misplaced interface DomainExtended definition(s)` |
| 1 match, canonical file | 0 | `dashboard-domain-extended-uniqueness-check: PASS` |

---

## 4. Tree state

Post-test `git status --short` shows only the expected untracked items:
```
?? WritingSample/
?? docs/status/2026-06-08-audit-guards-architect-plan.md
?? out/rebaseline/
```

No modified tracked files. Tree is at `6ca1c29` + untracked items.
