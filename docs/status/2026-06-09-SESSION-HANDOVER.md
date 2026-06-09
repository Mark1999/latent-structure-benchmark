# LSB Session Handover (2026-06-09)

**Read this first when starting the fresh session.** It supersedes the older
`docs/status/2026-05-30-NEXT-STEPS.md` for "what is the status / what is next." This wraps a very
long session (the `lsb` zellij session, ~4 days) that is now being closed for a clean restart.

## 0. Current state (confirm live first)
- `origin/master` = **`b8c6511`**, local in sync, **0 unpushed**. Confirm with
  `git rev-parse --short HEAD origin/master` + `git status --short`.
- Working tree clean except two intentional untracked dirs: `WritingSample/` (Mark's personal writing
  samples, LOCAL-ONLY, never commit) and `out/rebaseline/` (re-baseline staging). Leave both alone.
- CI: green on master. Site auto-deploys from master to cogstructurelab.com.
- No known failures. Everything shipped this session is live.

## 1. How to resume (read order)
1. `CLAUDE.md` (always; §1.5 framing + §7 forbidden vocab are binding on all generated text).
2. This file.
3. `docs/status/2026-06-08-phase9-kickoff.md` — the Phase 9 decision surface (the live roadmap for 9a/9b/9c).
4. `docs/status/2026-06-05-fresh-model-audit-pilot-findings.md` — the audit backlog (P2 items still open).
5. Memory (auto-loaded): note `feedback_no_em_dashes` (HARD RULE), `reference_mark_writing_voice`,
   `feedback_dispatch_hygiene`, `feedback_pipeline_autonomy`.

## 2. What shipped this session (all pushed + live)
**Guardrail infrastructure**
- Tier 1 PreToolUse guardrail hooks ACTIVATED (`1326273`) — forbidden-vocab / informants-append-only /
  spend-gate / schema-edit-ask. Live in `.claude/settings.json`. Tier 2 `lsb-pipeline.js` workflow
  VALIDATED (`e889e57`) but not yet used on real work (its worktree forks from origin/master, so
  `git push` before using it on real work).

**Fresh-model audit P1 + selected P2 (all DONE, gated pipeline, pushed)**
- T3 font-size token (`147cfe3`); T4 detect --dry-run poison pill (`dd1b8ea`); T5 TS-types-vs-published
  reconciliation (`94bb189`); T8 model-label dedup → `displayModel` (`c32c773`); T7 `displayProvider`
  dedup (`abf74bd`); T11 OCI threshold single-source-of-truth (`59dfa0d`/`cac3ea2`);
  T3-guard + T5-guard CI grep guards (`bce4754`/`6ca1c29`).

**New-model incorporation runbook** (`08dca63`) — `docs/proposed/2026-06-08-new-model-incorporation-runbook.md`.
The discover→collect→rebaseline→promote checklist. KEY FACT documented there: adding a model retroactively
changes all cross-model measures for that domain; the six rebaseline threshold guards halt-and-escalate.

**Methodology page scaffold** — `docs/proposed/2026-06-08-methodology-page-scaffold.md`, drafted in Mark's
voice (from the WritingSample review), Mark-edited, committed.

**Phase 9 kicked off + Phase 9a work shipped (the live-site regression fixes + two new surfaces)**
- Phase 9 kickoff doc (`fe0403f`). Mark's scope answers: same-as-proposed / inward-looking / start-now.
- **9a-T1** failures-as-findings restored as a top-level **"Collection records"** tab (Mark's label call;
  the gates recommended it over "Failures" to avoid reading as the models failing). DESIGN_SYSTEM §19.
- **9a-T6** Data download tab (HF dataset, Zenodo DOI, B2 tarball + SHA256, GitHub, licenses). DESIGN_SYSTEM §20.
- Methodology page placeholder shipped from the scaffold (CDA-SME PASS). DESIGN_SYSTEM unchanged.
- **9a-T2** published `generated_lede` rendered verbatim (restores the R1-b "no confidence ellipse"
  disclosure the inline lede dropped). Mark's ruling: static lede (the finding), slicer drives the charts.
  Bonus WCAG contrast fix on `.chart-lede`. DESIGN_SYSTEM §21.
- **9a-T3** SimilarityHeatmap CI-crosses-null treatment restored — dashed border + CI aria-labels for
  cells whose 95% CI crosses the 0.5 no-shared-structure value (34/56 food cells were false-confident).
  Bonus WCAG fix (white dashed stroke on dark cells). DESIGN_SYSTEM §12.8 patched.

**The three confirmed live-site regressions from the audit (T1 failures surface, T2 lede, T3 heatmap)
are ALL fixed.** DESIGN_SYSTEM is at v0.17.0.

## 3. What is open / next (prioritized)
**Phase 9a remaining (additive polish, NO regressions — agent pipeline):**
- T5 per-statistic ⓘ anchor system (Smith's S, Sutrop CSI, Romney, OCI, centrality — a reusable
  "click for a one-paragraph anchor"). High-value for legibility; CDA-SME-bound copy.
- The "what's missing" cross-cutting disclosure widget (per-domain N, English-only, single-date).
- Remaining inline chart anchors (the Focus 1/2/3 surfaces still name statistics without anchors).
- Audit P2 cleanups: T9 (label-placement → lib), T10 (provider-color hex→token), T15 (heatmap/cluster
  tokens). T-CI-vitest (CI does NOT run the dashboard vitest — the re-drift/shape guards are local-only).
  T6 (manifest pydantic in cdb_social), T12-T14, T16, T17.

**Phase 9b (Mark-operated + CDA SME):** data campaigns via the runbook — bench up food (8→~15 models),
collect the zero-record registry entries (Qwen/Cohere/Gemma activate empty Focus-2 families), one
second-collection-date subset to unlock DriftTracker.

**Phase 9c (frontend designer, parallel track):** typography/color/OWID-architecture/biplot/Sankey
overhaul per `docs/FRONTEND_DESIGNER_BRIEF.md`. Starts once 9a's structural floor lands.

**Small open items (non-blocking, flagged this session):**
- The failures empty-state caption shipped as "no failure records or follow-up interviews" (more accurate
  than the original T10 "no failure records"). Both gates accepted it; a one-line CDA SME ratification
  would make it airtight.
- The methodology page is a PLACEHOLDER (Mark to author the final; §1.5.6 wants "the mismatch is the
  finding" as the very first paragraph — the draft carries it in section 4).
- The published lede contains "--" (a double-hyphen, from the lede generator). Renders verbatim. If Mark
  wants it changed, that is a `cdb_publish/lede_v1.py` change, separate task.
- F5 → CDA SME: R10 semantics when an ellipse is degenerate (`semi_major<=0`) — latent, pending.

## 4. Hard rules / context for the fresh session
- **NO em dashes** in any output (Mark's standing rule; memory `feedback_no_em_dashes`). Use comma/colon/parens.
- Methodology + about + social copy use Mark's voice (memory `reference_mark_writing_voice`): demystify,
  plain-question headers, the "picture on the dresser" reasoning, honest-about-limits, "do your own homework".
- The gated pipeline (Architect → CDA SME / UI-UX → Coder → Reviewer → Tester) produces quality; run it.
- DESIGN_SYSTEM section numbers in use: §19 (Collection records), §20 (Data page), §21 (chart-lede),
  §12.8 patched (heatmap CI). Next frontend task takes the next number / next minor version (v0.18.0).
- Dispatch hygiene: `git status --short` between agent dispatches; commit agent-memory side-effects with
  `chore(memory):` so they don't sweep into the next commit.

*End of handover. master = b8c6511, clean, pushed, deploying.*
