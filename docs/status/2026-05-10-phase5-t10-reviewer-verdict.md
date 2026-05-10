# Reviewer Verdict — Phase 5 T10 (SourceAttribution + DownloadBar + CSV + Permalink)

**Filed:** 2026-05-10  
**Reviewer:** LSB Reviewer agent (Sonnet)  
**Commits reviewed:** `2feccd8` (Coder), `d02bcb5` (UI/UX FAIL→PASS-WITH-NOTES + WCAG fixes)  
**Prerequisite verdicts:**  
- Plan-level CDA SME PASS-WITH-NOTES: `fc72cad`  
- Plan-level UI/UX PASS-WITH-NOTES: `011f5bd`  
- T10 per-commit UI/UX FAIL→PASS-WITH-NOTES: `docs/status/2026-05-10-phase5-T10-uiux-verdict.md`  

---

## REVIEWER VERDICT: PASS

```
Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         N/A (no informants.jsonl change)
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A (no cdb_core/schemas.py change)
Check 6 — New deps sign-off:         N/A (no new dependencies)
Check 7 — Prompt versioning:         N/A (no prompt template changes)
Check 8 — Uncertainty in viz:        PASS
Check 9 — Prerequisite verdicts:     PASS
```

---

## Check-by-check rationale

**Check 1** — `grep -r "import anthropic|import openai|from anthropic|from openai|InferenceClient|google.generativeai" packages/cdb_analyze/` returns only the prohibition notice comment in `__init__.py`, not actual imports. No LLM client library introduced in cdb_analyze. PASS.

**Check 2** — `git diff bdf68e1..d02bcb5 -- data/raw/informants.jsonl` returns empty. Append-only invariant intact. N/A.

**Check 3** — Full scan of all changed files (`SourceAttribution.tsx`, `DownloadBar.tsx`, `csv-export.ts`, `permalink.ts`, `types.ts`, `DataExplorer.tsx`, `App.tsx`, `DESIGN_SYSTEM.md`, `tokens.css`, `app.css`) found no API keys, webhook URLs, passwords, or credential-shaped strings. No change to `apps/dashboard/public/_headers` (CSP unchanged). PASS.

**Check 4** — Forbidden vocabulary scan: zero matches for `believes`, `thinks`, `worldview`, `cultural bias`, `within-model consensus`, `within-model cultural consensus`, `within-model eigenratio`, `within-model CCM`, `publishable` (in user-facing contexts) across all T10-touched files. The small-n footnote text in `SourceAttribution.tsx` line 122 reads: "...below the n=15 threshold for stable Romney CCM eigenratio reporting." This is "Romney CCM eigenratio" (Register 2 cultural consensus method attribution, citing the Romney CCM threshold), not the forbidden "Within-model eigenratio" (which guards the R1/R2 boundary). The usage is a methodology-of-measurement footnote naming the analytical threshold criterion, not a claim about model cognition. PASS.

**Check 5** — The only schema-adjacent change is adding `romney_small_n_warning: boolean` to `apps/dashboard/src/data/types.ts` (the TypeScript frontend mirror). This field already exists in `packages/cdb_core/cdb_core/schemas.py` line 349 and is documented in `docs/DATA_DICTIONARY.md` §2 (added v0.1.5, threshold updated v0.1.8). No change to `cdb_core/schemas.py`. R7 does not trigger. N/A.

**Check 6** — `git diff bdf68e1..d02bcb5 -- apps/dashboard/package.json` returns empty. No new npm or Python dependencies. N/A.

**Check 7** — `git diff bdf68e1..d02bcb5 -- packages/cdb_collect/prompts/` returns empty. No prompt template changes. N/A.

**Check 8** — No new visualization. The CSV export (`csv-export.ts`) correctly emits empty strings for `semi_major`, `semi_minor`, `rotation_rad`, `n_bootstrap` when `r1_state !== "typical_concentration"` (line 91: `r1State === "typical_concentration" && ellipse !== null && ellipse !== undefined`). The §3.3.5 binding invariant (ellipse params empty for R1-b/R1-c rows) is honored. The comment row at the top of the CSV documents this semantics for downstream consumers. SourceAttribution and DownloadBar do not display MDS coordinates or point estimates — they are metadata/utility components. PASS.

**Check 9** — Plan-level CDA SME PASS-WITH-NOTES at `fc72cad` covers Q2 (small-n surface in SourceAttribution), Q3, Q4, Q9, and other notes — all addressed. Plan-level UI/UX PASS-WITH-NOTES at `011f5bd` covers phase visual decisions. T10 per-commit UI/UX FAIL→PASS-WITH-NOTES at `d02bcb5` identified F-T10-1 (WCAG AA contrast violation, blocking) and F-T10-2 (missing focus-visible rule, blocking) — both corrected in the same commit `d02bcb5` alongside the verdict. All prerequisite notes addressed before Reviewer review. PASS.

---

## Build/test confirmation

- `vitest run`: 476/476 tests pass (17 test files)
- `eslint`: clean
- `tsc -b --noEmit`: clean
- `vite build`: 70.40 KB gzipped JS, well under T10 AC4 budget of <380 KB gzipped

---

## Observation (carry-forward, not a FAIL)

`SourceAttribution.tsx` line 90 applies `color: "var(--color-text-caption)"` to the outer div but the conditional "(N of M models shown)" sub-span at line 90 overrides to `var(--color-text-secondary)` (#7f8c8d, ~3.40:1 on white). At 12px normal weight, `--color-text-secondary` does not pass WCAG AA 4.5:1. However: (a) this sub-span was present in `2feccd8` when the UI/UX agent conducted the FAIL review and was not flagged as a blocking finding — the UI/UX gate is the WCAG authority for frontend PRs; (b) this Reviewer does not override a UI/UX PASS-WITH-NOTES verdict that was issued with full visibility of the code. Carry this observation to T11: the UI/UX agent should confirm at T11 whether the parenthetical "(N of M models shown)" sub-span should use `--color-text-caption` instead of `--color-text-secondary`.

---

## Failures

None.

---

## Required before merge

None. Coder may merge.

---

*T10 is PASS. Tester proceeds.*
