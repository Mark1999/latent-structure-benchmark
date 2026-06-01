# LSB — WHAT'S NEXT (status checkpoint, updated 2026-05-31)

**If Mark asks for a status update, start here.** Confirm live state first (`git rev-parse --short HEAD origin/master`, `git status --short`), then report against this list.

## State at checkpoint (updated 2026-06-01)
- `origin/master` = `3a42339`, local in sync, tree clean (only untracked `out/rebaseline/` staging + `.claude/scheduled_tasks.lock` — both intentional/local).
- CI: green. Live site (cogstructurelab.com) auto-deploys from master.
- All four originally-open tasks are DONE except Tier 1–2 hook *activation* (prepped + validated, deferred to a clean session by Mark's choice). See DONE + OPEN below.

## DONE (no action needed)
- ✅ Remedy B (centrality-CI register error) — fully remediated, live.
- ✅ Reproducibility re-baseline computed under pinned NumPy 2.4.4 / SciPy 1.17.1 (all guards PASS).
- ✅ **family + holidays** re-baseline PROMOTED to live (atomic: data + provenance.json + methodology paragraph + per-domain conditional footer). The earlier false-provenance footer was reverted, then redone correctly.
- ✅ Term-map pile-sort cluster labels → black, 2× size (`42bd7fb`, live).
- ✅ **Term-map runaway-growth bug FIXED + zoom redesign — both stages live & verified on cogstructurelab.com (2026-05-31).** The "terms flying off screen" was a runaway vertical-growth loop (SVG height fed back through unbounded containers + ResizeObserver), not an animation. **Stage 1** (`ffcb08b`): bounded container height + `#root` flex fix (a 2026-05-30 footer regression) → map fills viewport; ctrl-wheel zoom (plain wheel scrolls page — fixed a WCAG scroll-trap); keyboard +/−/Reset buttons + hint + aria-live. **Stage 2** (`3de836b`): viewBox-zoom → content-scale + native scrollbars when zoomed (Mark override of UI/UX); everything-scales OWID-style (Q1); lens auto-disables when zoomed (Q2); native pinch+scroll (Q3). Verified live: 4× zoom → scale(2.44), SVG 1140→2783px, real scrollbar overflow, scroll pans, reset clean. Gates: UI/UX (Stage 1 + Stage 2 re-spec) → Coder (Stage 2 zoom took 3 rounds; browser-verification caught 2 false "fixed" claims) → Reviewer. Plan: `docs/status/2026-05-31-termmap-redesign-architect-plan.md`. NOTE: Stage 1+2 regression tests were DEFERRED to the vitest harness (item 4) — manual browser-verified instead.

## DONE 2026-05-31 / 06-01 (this session)
- ✅ **Food re-baseline promotion** — LIVE & verified on prod. CDA SME PASS-WITH-NOTES (C1-C5) + UI/UX PASS-WITH-NOTES + Reviewer PASS. Food term-MDS published, provenance.json food entry, footer date fix, methodology disclosure stub.
- ✅ **Blank-term-map fix (ALL domains)** — discovered mid-promotion that the term map only ever rendered for family (holidays + food were blank — no cooccurrence file; publish.py never emitted one). Mark: "fix for all domains." `build.py` now emits per-domain cooccurrence files. **Verified LIVE on cogstructurelab.com: holidays 69 dots, food 296, family 100.** (Bonus fix beyond the original open list.)
- ✅ **Finding 2 — cda_sme agent-def sync** (`3a42339`): added Write/Edit to `.claude/agents/cda_sme.md` tools (matches runtime; SME authors verdict files). Finding 1 = no action (agents already correctly scoped).
- ✅ **Dashboard vitest harness (T7)** — stood up (vite.config test block + jsdom + setupTests + tsconfig.test.json); **31 tests across 4 files** (ProvenanceFooter, CentralityChart, CentralityTable, TermMap blank/populated regression guard). Frontend Tester gate is now LIVE. Reviewer R6-flagged an unapproved `@testing-library/user-event` dep → removed (`cc6bc26`); the two approved deps (react, jest-dom) retained.
- ✅ **CI restored to green** — a chain of self-inflicted CI reds (my own draft spend-gate hook's regex tripped no-spend-gate-check; docs/proposed/ exclude typo; ruff E501 on the draft hook) fixed across `3e62906`/`732870f`/`18d5696` (added `.claude/` to ruff exclude + `docs/proposed/` to the spend-gate grep exclude).

## OPEN — what's next
1. **Activate Tier 1–2 capability upgrade (drafted + VALIDATED, still INACTIVE — Mark deferred to a clean session start).** Guardrail hooks + Workflow pipeline in `.claude/hooks/` + `.claude/workflows/`; all four hooks dry-run-validated 2026-06-01 (block bad / allow benign / no false positives), workflow parses, `settings.json` confirmed has NO `hooks` key. **Activation is the only remaining step**: wire the 4 hooks into `.claude/settings.json` `hooks.PreToolUse`, restart session, re-run dry-runs live, Reviewer-gate. Deferred because PreToolUse hooks intercept every edit — unsafe to wire mid-session. Runbook (with validation log): `docs/proposed/2026-05-29-tier1-2-activation-runbook.md`.

2. **Minor / cleanup (non-blocking):** term-map 2× category labels can slightly overlap dots on dense data + scale further under zoom — a label-offset nudge is polish, not a bug. The TermMap live-MDS path (SMACOF/Procrustes) and CentralityChart SVG-whisker DOM aren't unit-tested (jsdom can't drive ResizeObserver) — covered by manual browser verification; deeper coverage would need a real-browser test runner (Playwright-ct).

## Reference docs
- Re-baseline completion + drift: `docs/status/2026-05-29-rebaseline-completion.md`
- Promotion (corrected) verdict: `docs/status/2026-05-30-promote2-cda-sme-verdict.md`
- Tier 1–2 activation: `docs/proposed/2026-05-29-tier1-2-activation-runbook.md`
- Session resume (zellij/regen history): `docs/status/2026-05-29-SESSION-RESUME-rebaseline.md`
- Term-map redesign plan + decisions: `docs/status/2026-05-31-termmap-redesign-architect-plan.md`
- Term-map UI/UX verdicts: `docs/status/2026-05-31-termmap-layout-zoom-uiux-verdict.md` (Stage 1 + Mark scrollbar override), `docs/status/2026-05-31-termmap-stage2-uiux-verdict.md` (Stage 2 scrollbar re-spec)
