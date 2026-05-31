# LSB — WHAT'S NEXT (status checkpoint, updated 2026-05-31)

**If Mark asks for a status update, start here.** Confirm live state first (`git rev-parse --short HEAD origin/master`, `git status --short`), then report against this list.

## State at checkpoint
- `origin/master` = `3de836b`, local in sync, tree clean (only untracked `out/rebaseline/` staging — intentional).
- CI: green. Live site (cogstructurelab.com) auto-deploys from master.

## DONE (no action needed)
- ✅ Remedy B (centrality-CI register error) — fully remediated, live.
- ✅ Reproducibility re-baseline computed under pinned NumPy 2.4.4 / SciPy 1.17.1 (all guards PASS).
- ✅ **family + holidays** re-baseline PROMOTED to live (atomic: data + provenance.json + methodology paragraph + per-domain conditional footer). The earlier false-provenance footer was reverted, then redone correctly.
- ✅ Term-map pile-sort cluster labels → black, 2× size (`42bd7fb`, live).
- ✅ **Term-map runaway-growth bug FIXED + zoom redesign — both stages live & verified on cogstructurelab.com (2026-05-31).** The "terms flying off screen" was a runaway vertical-growth loop (SVG height fed back through unbounded containers + ResizeObserver), not an animation. **Stage 1** (`ffcb08b`): bounded container height + `#root` flex fix (a 2026-05-30 footer regression) → map fills viewport; ctrl-wheel zoom (plain wheel scrolls page — fixed a WCAG scroll-trap); keyboard +/−/Reset buttons + hint + aria-live. **Stage 2** (`3de836b`): viewBox-zoom → content-scale + native scrollbars when zoomed (Mark override of UI/UX); everything-scales OWID-style (Q1); lens auto-disables when zoomed (Q2); native pinch+scroll (Q3). Verified live: 4× zoom → scale(2.44), SVG 1140→2783px, real scrollbar overflow, scroll pans, reset clean. Gates: UI/UX (Stage 1 + Stage 2 re-spec) → Coder (Stage 2 zoom took 3 rounds; browser-verification caught 2 false "fixed" claims) → Reviewer. Plan: `docs/status/2026-05-31-termmap-redesign-architect-plan.md`. NOTE: Stage 1+2 regression tests were DEFERRED to the vitest harness (item 4) — manual browser-verified instead.

## OPEN — what's next (priority order)
1. **Food re-baseline promotion (deferred — needs its own CDA SME review).** Food was held out of the family+holidays promotion because its staged file adds **12 populated structural keys** (term-MDS, centroid_piles) — NOT drift-only, so it can't ride the rounding-level rationale. Staged data sits in `out/rebaseline/food/0.2.json`. Next action: route the food structural enrichment (empty→populated term-map) to the CDA SME, then promote food (data + add food to provenance.json `domains` + footer will then auto-show on food's page). See `docs/status/2026-05-30-promote2-cda-sme-verdict.md` §4.

2. **Activate Tier 1–2 capability upgrade (drafted, INACTIVE).** Guardrail hooks + Workflow pipeline are drafted in `.claude/hooks/` and `.claude/workflows/`, not wired in. Activation runbook: `docs/proposed/2026-05-29-tier1-2-activation-runbook.md`. Needs: Reviewer gate + dry-run each hook live + Mark sign-off. NOTE: `.claude/hooks/check_spend_gate.py` has a known minor ruff lint error to fix during activation.

3. **Findings 1 & 2 — agent tool-scoping cleanup (accepted, not done).** Finding 1 = no action (agents already scoped right). Finding 2 = sync the committed `cda_sme` agent def UP to the live registry (it has Write/Edit at runtime but the .md says read-only); keep the SME's Write; optional UI/UX Write. Reviewer-gated. Make the change in the platform/FleetView registry, not just the file. See `docs/proposed/2026-05-29-tier1-2-activation-runbook.md` (decided section).

4. **Dashboard vitest harness (T7).** Dashboard has ZERO test files; `npm run test` exits 1 ("no tests found"), so the frontend Tester gate is dormant. Deferred tests waiting on this now include: ProvenanceFooter render test (from the promotion), CentralityChart/Table tests, AND the **term-map Stage 1+2 regression tests** (growth-loop-doesn't-recur, ctrl-wheel gate, content-scale zoom produces overflow, reset, lens auto-disable) — all currently only manually browser-verified. Deps already approved: `@testing-library/react` + `@testing-library/jest-dom`.

5. **Minor / cleanup:** the term-map 2× category labels can slightly overlap their dots on dense data, and now scale further under zoom (everything-scales) — a label-offset nudge is non-blocking polish. Stale fixtures already fixed; the 2 pre-existing `test_lede.py`/`test_build_domain_json.py` failures were resolved during the re-baseline work. The inactive `.claude/hooks/check_spend_gate.py` still has a minor ruff E501 (fix when activating Tier 1–2, item 2).

## Reference docs
- Re-baseline completion + drift: `docs/status/2026-05-29-rebaseline-completion.md`
- Promotion (corrected) verdict: `docs/status/2026-05-30-promote2-cda-sme-verdict.md`
- Tier 1–2 activation: `docs/proposed/2026-05-29-tier1-2-activation-runbook.md`
- Session resume (zellij/regen history): `docs/status/2026-05-29-SESSION-RESUME-rebaseline.md`
- Term-map redesign plan + decisions: `docs/status/2026-05-31-termmap-redesign-architect-plan.md`
- Term-map UI/UX verdicts: `docs/status/2026-05-31-termmap-layout-zoom-uiux-verdict.md` (Stage 1 + Mark scrollbar override), `docs/status/2026-05-31-termmap-stage2-uiux-verdict.md` (Stage 2 scrollbar re-spec)
