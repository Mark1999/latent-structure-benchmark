# LSB — WHAT'S NEXT (status checkpoint 2026-05-30)

**If Mark asks for a status update, start here.** Confirm live state first (`git rev-parse --short HEAD origin/master`, `git status --short`), then report against this list.

## State at checkpoint
- `origin/master` = `42bd7fb`, local in sync, tree clean (only untracked `out/rebaseline/` staging — intentional).
- CI: green. Live site (cogstructurelab.com) auto-deploys from master.

## DONE this session (no action needed)
- ✅ Remedy B (centrality-CI register error) — fully remediated, live.
- ✅ Reproducibility re-baseline computed under pinned NumPy 2.4.4 / SciPy 1.17.1 (all guards PASS).
- ✅ **family + holidays** re-baseline PROMOTED to live (atomic: data + provenance.json + methodology paragraph + per-domain conditional footer). The earlier false-provenance footer was reverted, then redone correctly.
- ✅ Term-map pile-sort cluster labels → black, 2× size (`42bd7fb`, live).

## OPEN — what's next (priority order)
1. **Food re-baseline promotion (deferred — needs its own CDA SME review).** Food was held out of the family+holidays promotion because its staged file adds **12 populated structural keys** (term-MDS, centroid_piles) — NOT drift-only, so it can't ride the rounding-level rationale. Staged data sits in `out/rebaseline/food/0.2.json`. Next action: route the food structural enrichment (empty→populated term-map) to the CDA SME, then promote food (data + add food to provenance.json `domains` + footer will then auto-show on food's page). See `docs/status/2026-05-30-promote2-cda-sme-verdict.md` §4.

2. **Activate Tier 1–2 capability upgrade (drafted, INACTIVE).** Guardrail hooks + Workflow pipeline are drafted in `.claude/hooks/` and `.claude/workflows/`, not wired in. Activation runbook: `docs/proposed/2026-05-29-tier1-2-activation-runbook.md`. Needs: Reviewer gate + dry-run each hook live + Mark sign-off. NOTE: `.claude/hooks/check_spend_gate.py` has a known minor ruff lint error to fix during activation.

3. **Findings 1 & 2 — agent tool-scoping cleanup (accepted, not done).** Finding 1 = no action (agents already scoped right). Finding 2 = sync the committed `cda_sme` agent def UP to the live registry (it has Write/Edit at runtime but the .md says read-only); keep the SME's Write; optional UI/UX Write. Reviewer-gated. Make the change in the platform/FleetView registry, not just the file. See `docs/proposed/2026-05-29-tier1-2-activation-runbook.md` (decided section).

4. **Dashboard vitest harness (T7).** Dashboard has ZERO test files; `npm run test` exits 1 ("no tests found"), so the frontend Tester gate is dormant. Deferred tests waiting on this: the ProvenanceFooter render test (from the promotion) + CentralityChart/Table tests. Deps already approved: `@testing-library/react` + `@testing-library/jest-dom`.

5. **Minor / cleanup:** the term-map 2× category labels can slightly overlap their dots on dense data (label-offset nudge, non-blocking). Stale fixtures were already fixed. The 2 pre-existing `test_lede.py`/`test_build_domain_json.py` failures were resolved during the re-baseline work.

## Reference docs
- Re-baseline completion + drift: `docs/status/2026-05-29-rebaseline-completion.md`
- Promotion (corrected) verdict: `docs/status/2026-05-30-promote2-cda-sme-verdict.md`
- Tier 1–2 activation: `docs/proposed/2026-05-29-tier1-2-activation-runbook.md`
- Session resume (zellij/regen history): `docs/status/2026-05-29-SESSION-RESUME-rebaseline.md`
