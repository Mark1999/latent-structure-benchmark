# T3-guard + T5-guard — CI recurrence guards — Architect plan (2026-06-08)

**Source:** fresh-model audit `docs/status/2026-06-05-fresh-model-audit-pilot-findings.md` (T3-guard + T5 follow-up).
**Gate path:** Architect → Coder → Reviewer → Tester. **No UI/UX, no CDA SME** (CI mechanics; no pixels/tokens/copy/methodology/schema touched).

## 1. Mechanism ruling — CI bash git-grep steps in `.github/workflows/ci.yml` (Option A)
CI does NOT run the dashboard vitest (verified: no npm/node step in ci.yml), so a vitest guard
gives ZERO CI protection. The established CI guard idiom is a bash `run:` git-grep block
(`no-spend-gate-check` ci.yml:18–39, `cdb-social-boundary` :62–98). Both guards mirror it.
**Prefer a standalone `scripts/check_*.sh` (or `.py`) called from ci.yml** so the Tester can run
it locally for revert-and-confirm-fail.

## 2. CI-vitest GAP — flagged, separate, NOT bundled
The T5 shape test + T7/T8 re-drift grep guards live in vitest → run ONLY at the local commit
gate (CLAUDE.md §8/§11), NOT in CI. Acceptable today (single-operator, disciplined local
pre-commit), but a latent gap. **New P2 backlog item `T-CI-vitest`:** add a `dashboard-vitest`
job to ci.yml (`npm ci && npm run build && npm run test && npm run lint` from apps/dashboard/).
Its own Architect plan (Node pin, cache key, fail-fast surface). Do NOT bundle into T3/T5-guard.

## 3. Split — two commits, one task each (CLAUDE.md §8). T3-guard first (CSS), T5-guard second (TS).

## 4. T3-guard spec — `dashboard-font-size-token-check`
- **Scan:** `apps/dashboard/src/**/*.css` + `**/*.tsx` + `**/*.ts` (inline `style={{fontSize:'var(--font-size-...)'}}` EXISTS at App.tsx:200 + TermMap.tsx:1254 — the .tsx/.ts scan is mandatory). EXCLUDE test files (`**/__tests__/**`, `*.test.*`, `*.spec.*`) and tokens.css itself.
- **Allow-list:** DERIVE from tokens.css at runtime, not a hardcoded regex (hardcoding is the same drift hazard being guarded). E.g.:
  `grep -E '^\s*--font-size-[a-z0-9-]+:' apps/dashboard/src/styles/tokens.css | sed -E 's/.*--font-size-([a-z0-9-]+):.*/\1/'` → allow-list.
  `git grep -nE 'var\(--font-size-[a-z0-9-]+\)' -- apps/dashboard/src/` → references; any suffix not in allow-list = violation. (Hardcoded `xs|sm|base|lg|xl|2xl|3xl` acceptable FALLBACK with a comment pinning it to tokens.css if the derived bash form is infeasible.)
- **Contract:** exit 0 + `dashboard-font-size-token-check: PASS`; else exit 1 + `::error::Undefined font-size token reference(s): <file:line>` + pointer to pitfall #15 + DESIGN_SYSTEM §1.1.

## 5. T5-guard spec — `dashboard-domain-extended-uniqueness-check`
- **Scan:** `apps/dashboard/src/**/*.ts` + `**/*.tsx`.
- **Match:** `git grep -nE '^[[:space:]]*(export[[:space:]]+)?interface[[:space:]]+DomainExtended[[:space:]]*[<{]' -- apps/dashboard/src/` (anchored; trailing `<`/`{` so it won't match imports/comments).
- **Contract:** exit 0 + PASS iff EXACTLY ONE match AND it's in `apps/dashboard/src/data/types.ts`. Exit 1 with a distinct message for each failure case: 0 matches ("canonical missing"), ≥2 matches or 1-outside-canonical ("duplicate/misplaced", list file:line). Error references the T5 plan + audit findings.

## 6. Verification (Tester — revert-and-confirm-fail, per guard)
- **T3-guard:** plant `var(--font-size-md)` in a real .css → exit 1 names file:line; revert → 0. Repeat with an inline `.tsx` `var(--font-size-xx)` (proves .tsx scan). Positive baseline on master = PASS (record the scan count + derived allow-list). If derive-form used: comment out a tokens.css declaration → refs to it now fail; revert.
- **T5-guard:** (a) paste a 2nd `interface DomainExtended` in a component → exit 1 lists both; revert→0. (b) move the only def out of data/types.ts → "misplaced" error. (c) comment out the canonical → "canonical missing" error. Positive baseline = 1 match at data/types.ts:289.
- Verdict files: `docs/status/2026-06-08-T3-guard-tester-verdict.md`, `…-T5-guard-tester-verdict.md`.

## 7. Scope (both)
Touch ONLY `.github/workflows/ci.yml` + optional `scripts/check_*.sh|py` + verdict files. NOTHING in
`apps/`, `packages/`, `data/`, DESIGN_SYSTEM, schemas, or DATA_DICTIONARY. Reviewer confirms the regex
matches this spec exactly (not widened/narrowed) + exclusions exact + error messages cite the rationale docs.

## 8. Acceptance criteria
Per guard: named ci.yml `run:` step (in `lint-and-test` job) [+ optional standalone script]; correct
scan scope + exclusions; derived allow-list (T3) / anchored uniqueness (T5); exit-code contract; error
cites rationale; Tester revert-and-confirm-fail verdict; ONE commit `ci(dashboard):`/`ci(scripts):`
referencing this plan + Reviewer/Tester verdicts. T3-guard first, T5-guard second.
