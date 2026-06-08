# Audit T3 (undefined `--font-size-md`) — gate verdicts (2026-06-08)

**Pipeline outcome:** UI/UX PASS-WITH-NOTES → Coder (`147cfe3`) → Reviewer
PASS-WITH-NOTES (note applied via amend) → Tester PASS. T3 DONE.

---

## UI/UX verdict

**Task:** T3 from `docs/status/2026-06-05-fresh-model-audit-pilot-findings.md` —
`focus1.css:26` `.f1-model-heading` references the undefined token
`var(--font-size-md)` (pitfall #15 silent CSS fallback). UI/UX must pick the
replacement token (visual decision the Coder may not make).
**Gate:** UI/UX (frontend). **Verdict:** **PASS-WITH-NOTES.**

## Four-criterion scorecard
| Criterion | Result |
|---|---|
| OWID design fidelity | PASS (token fix only; no new viz) |
| 30-second journalist | PASS (unaffected) |
| Researcher cite path | PASS (unaffected) |
| WCAG AA | PASS (element is bold + `--color-text-primary`; contrast unaffected — the bug broke hierarchy, not contrast) |

## Decision (binding)
1. **Replace `var(--font-size-md)` → `var(--font-size-base)`** at `focus1.css:26`.
   Rationale: `.f1-model-heading` is the model-name heading atop the Focus-1 Run
   Distribution and Term Stability sub-views — a sub-view heading one level below
   a section heading (`--font-size-xl`) and above body text. The scale has no `md`
   step (jumps base 16px → lg 18px). `base` + existing `--font-weight-bold` gives
   the right hierarchy; `lg` (18px) is reserved for the editorial lede + key-finding
   strip and would overstate a per-model sub-view heading's prominence.
2. **DESIGN_SYSTEM.md update required in the SAME commit** (closes the §13 gap that
   let the bug survive the original gate):
   - **§1.1 type-scale block** — annotate that there is deliberately no
     `--font-size-md`; the scale goes base (16) → lg (18); sub-view headings that
     need a step between body and lede use `base` + bold, not a phantom `md`.
   - **§13** — add a binding `.f1-model-heading` typography spec: `--font-size-base`
     (16px) + `--font-weight-bold` (700) + `--color-text-primary`, with the
     base-vs-lg rationale above.

## Notes the next agents must apply
- **Recurrence-guard scope ruling (R-scope):** the audit's proposed regex check
  (`var(--font-size-(?!xs|sm|base|lg|xl|2xl|3xl))`) is a **CI/lint task, NOT a
  frontend visual-decision task**. It belongs to the **Architect** to authorize CI
  scope, then the Coder to implement. **It is OUT of scope for the T3 fix** — the
  Coder must NOT bundle it (would be scope creep from this gate). UI/UX recommends
  the Architect add it to the backlog as a pitfall-#15 CI-hardening task; it is the
  correct recurrence-prevention class but is a separate commit.

## Files
- `apps/dashboard/src/styles/focus1.css:26` (the broken declaration)
- `apps/dashboard/src/styles/tokens.css:57–63` (scale; confirms no `md`)
- `DESIGN_SYSTEM.md` §1.1 + §13 (the two sections to update)

---

## Reviewer verdict (commit `147cfe3`) — PASS-WITH-NOTES
Scorecard: Checks 1/3/4/9 PASS; 2/5/6/7/8 N/A. Scope discipline confirmed
clean — exactly 2 files (`focus1.css`, `DESIGN_SYSTEM.md`), only the one
`.f1-model-heading` line changed in the CSS, the out-of-scope recurrence guard
was NOT bundled, no `--font-size-md` token added to tokens.css, `out/rebaseline/`
not committed. UI/UX PASS prerequisite present + all its binding notes satisfied.
No forbidden vocabulary.

**Single note (factual):** the original §1.1 comment + commit message said the
undefined token "falls back to **initial value**." `font-size` is an *inherited*
property → it falls back to the **inherited** value (parent's font-size), not
initial. **Note APPLIED:** DESIGN_SYSTEM.md §1.1 wording corrected and the commit
amended (`6cd3246` → `147cfe3`) before merge, so the task stays one clean commit.

## Tester verdict (commit `147cfe3`) — PASS
Existing dashboard vitest suite re-run: **4 files / 31 tests, all pass** against
`147cfe3`. **No regression test added — deliberate**, on three grounds: (1) jsdom
does not resolve CSS custom properties, so a computed-font-size test is infeasible
(that limitation IS pitfall #15's root cause); (2) a narrow `focus1.css`
string-assertion is a strict subset of — and redundant with — the deferred
Architect-authorized CI recurrence guard; (3) the commit adds no new function /
component / logic, so CLAUDE.md §11's new-function test requirement does not
attach. `grep -r font-size-md apps/dashboard/src/` returns nothing — fix is clean.

## Follow-up spun out of this task (for the Architect backlog)
**T3-guard (NEW, P2 CI-hardening):** add a pitfall-#15 recurrence guard — a CI/lint
check (grep or stylelint) asserting no `var(--font-size-*)` references a token
absent from tokens.css (regex `var(--font-size-(?!xs|sm|base|lg|xl|2xl|3xl))`).
Ruled out of scope for the T3 fix by BOTH the UI/UX gate (CI scope is the
Architect's to authorize) and the Tester (belongs in CI, not vitest). Needs
Architect sign-off on CI scope, then Coder + Reviewer + Tester.
