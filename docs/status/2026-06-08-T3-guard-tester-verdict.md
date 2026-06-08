# T3-guard Tester Verdict — `dashboard-font-size-token-check`

**Date:** 2026-06-08
**Guard commit:** `bce4754` (`scripts/check_font_size_tokens.sh`)
**Plan ref:** `docs/status/2026-06-08-audit-guards-architect-plan.md` §4 + §6
**Verdict:** PASS

---

## 1. Baseline (clean tree at `bce4754`)

```
dashboard-font-size-token-check: PASS
  Allow-list derived from apps/dashboard/src/styles/tokens.css: xs|sm|base|lg|xl|2xl|3xl
Exit: 0
```

Allow-list derived from tokens.css: `xs|sm|base|lg|xl|2xl|3xl` — matches expectation.

---

## 2. Revert-and-confirm-fail results

### 2(a) CSS violation — `font-size: var(--font-size-md)` planted in `focus2.css`

**Planted:** `.probe-violation { font-size: var(--font-size-md); }` at line 6 of
`apps/dashboard/src/styles/focus2.css`.

**Guard output (exit 1):**
```
::error::Undefined font-size token reference(s):
apps/dashboard/src/styles/focus2.css:5:/* TESTER PROBE: intentional violation ... */
apps/dashboard/src/styles/focus2.css:6:.probe-violation { font-size: var(--font-size-md); }

See CLAUDE.md §9 pitfall #15 and DESIGN_SYSTEM.md §1.1.
```

Guard correctly named file and line. Reverted via `git checkout --`. Post-revert: exit 0. CONFIRMED.

### 2(b) TSX-scan coverage — `var(--font-size-zz)` planted in `App.tsx`

**Planted:** inline `letterSpacing: 'var(--font-size-zz)'` inside the `style={{}}` block
at `apps/dashboard/src/App.tsx` line 201.

**Guard output (exit 1):**
```
::error::Undefined font-size token reference(s):
apps/dashboard/src/App.tsx:201:            /* TESTER PROBE: var(--font-size-zz) */ letterSpacing: 'var(--font-size-zz)',

See CLAUDE.md §9 pitfall #15 and DESIGN_SYSTEM.md §1.1.
```

Guard correctly found the .tsx file by name and line number. Proves the scan path reaches `.tsx`
files (not only `.css`). Reverted via `git checkout --`. Post-revert: exit 0. CONFIRMED.

### 2(c) Allow-list derivation — `--font-size-sm` commented out in `tokens.css`

**Planted:** Declaration `--font-size-sm: 14px;` replaced with a comment line in
`apps/dashboard/src/styles/tokens.css`.

**Guard output (exit 1):**
```
::error::Undefined font-size token reference(s):
apps/dashboard/src/App.tsx:200:            fontSize: 'var(--font-size-sm)',
apps/dashboard/src/styles/app.css:641:  font-size: var(--font-size-sm);
apps/dashboard/src/styles/app.css:757:  font-size: var(--font-size-sm);
[... 22 additional var(--font-size-sm) references across app.css, focus1.css, focus2.css ...]

See CLAUDE.md §9 pitfall #15 and DESIGN_SYSTEM.md §1.1.
```

All `var(--font-size-sm)` references throughout the codebase failed because `sm` was
dropped from the runtime-derived allow-list when its declaration was commented out.
This proves the allow-list is genuinely derived from `tokens.css` at runtime, not
hardcoded. Reverted via `git checkout --`. Post-revert: exit 0. CONFIRMED.

---

## 3. Tree state

Post-test `git status --short` shows only the expected untracked items:
```
?? WritingSample/
?? docs/status/2026-06-08-audit-guards-architect-plan.md
?? out/rebaseline/
```

No modified tracked files. Tree is at `bce4754` + untracked items.
