# Phase 9 Architect Kickoff: Interpretive Friction, Data Gaps, Viz Alternatives

**Status:** Decision surface for Mark. Inward-looking, engineer-readable, terse. Per the §4 scoping answers (2026-06-08): scope = "same as proposed" (the three-problem bundle 2.1+2.2+2.3; keep current measures and the family/holidays/food slate; do NOT broaden); audience = inward-looking; timing = start now. This is a PLANNING doc; it does not itself require a CDA SME gate. §1.5 framing is respected for any language proposed for public surfaces.
**Date:** 2026-06-08
**Companion specs:** `docs/PHASE_9_PLANNING_NOTES.md`; `ARCHITECTURE.md` §1.5, §5.3; `DESIGN_SYSTEM.md`; `docs/FRONTEND_DESIGNER_BRIEF.md` + `_APPENDIX.md`; `docs/proposed/2026-06-08-methodology-page-scaffold.md`; `docs/proposed/2026-06-08-new-model-incorporation-runbook.md`; `docs/status/2026-06-05-fresh-model-audit-pilot-findings.md`.
**Inherits from:** Phase 8 closure (public release, DOI minted, dashboard live); Phase 9a closure (term-level viz gap closed); post-launch Mark diagnosis ("we're very much in the beta period").

> Authoring note: the Architect drafted this read-only and returned it inline; the orchestrator persisted it and normalized out em dashes per Mark's standing style rule. Three of the audit findings below (failures surface absent, published-lede discarded, suspected heatmap R10 regression) are live-site regressions from the 2026-05-25 frontend rebuild, not just planning items, and warrant verification early in 9a.

---

## 1. Goal

Close the gap between "the dashboard renders" (Phase 8 success condition) and "a researcher landing on cogstructurelab.com cold can read it without context." Three interconnected problems, all required, none sufficient alone:

- **2.1 Interpretive friction** on existing surfaces (current measures, current viz, missing per-chart explanation, copy that names statistics but does not anchor them).
- **2.2 Data gaps:** the v1 slate is finite and partial; some interpretive friction is actually correct skepticism about a thin corpus.
- **2.3 Viz alternatives:** for at least three current chart families a different chart family answers the question better; for at least two questions LSB answers analytically, the dashboard does not visualize at all.

Success condition is not "polished UI." It is: a journalist with five minutes leaves with a defensible understanding of what LSB measured and what it does not claim; a researcher with thirty minutes leaves able to cite a finding and reproduce it.

---

## 2. Out of scope (per Mark's §4.1 "same as proposed"; these are Phase 10)

1. New research questions beyond "what does the elicitation produce when applied to LLMs."
2. New domains beyond family / holidays / food. (Model-dimension runbook exists; a new-domain runbook does not, and is not in Phase 9.)
3. New analytical measures. Current measures stay (Smith's S, Sutrop CSI, Romney CCM eigenratio, OCI, cultural centrality, AHC, MDS, Procrustes, bootstrap CIs). Phase 9 may expose underused fields and visualize them better, not add analytics.
4. Re-introducing human grounding (2026-05-07 §1.5.5 amendment is binding).
5. Re-introducing autonomous LLM calls in production paths (§11.1 B-1 binding).
6. Methodology page prose authorship (Mark-authored; scaffold at `docs/proposed/2026-06-08-methodology-page-scaffold.md`).
7. FT-designer-scope polish (separate parallel track; 9a and 9b proceed regardless).

---

## 3. Part 1: Audit of interpretive friction (from `apps/dashboard/src/` + published `family.json`)

### 3.1 Site shell
- **NavBar:** Explore / Methodology / Data tabs, brand "Cognitive Structure Lab / LSB". No tagline, no one-line "what LSB does." The §1.5 short-form anchor is absent from the shell. Fix class: inline (methodology-adjacent copy, CDA SME gate).
- **Data tab** (`App.tsx:202`): renders "Data download page, coming soon" placeholder. The entire open-data / DOI / HF dataset / reproducibility story is gated behind a "coming soon" tab. One of LSB's strongest defensibility surfaces is unreachable. Fix class: scaffold-only (link-card stack to canonical paths).
- **MethodologyPage:** two SME-approved sections (Data provenance, Cross-model term map) above a placeholder "Full methodology content coming soon." §1.5.6 makes this page load-bearing; it currently leads with a placeholder. Unlocked by the methodology-scaffold draft once Mark finalizes.

### 3.2 Focus 3 (Cross-model), the default-on view
Lede strip (`ContentArea.tsx:199-220`) generates e.g. "Across 15 models, family vocabulary is organized around a shared categorical structure (Smith's S = 0.81, 95% CI [0.64, 0.95])."
- "Smith's S" named without anchor (no tooltip/glossary/inline expand); reads as a brand name.
- "Categorical structure" correct but undefined; the corpus-lens vocabulary the methodology scaffold explains is absent here.
- The CI is shown but never explained (wide or narrow? vs what?).
- **The published `generated_lede` in the JSON (CDA-SME-approved prose, family.json) is NOT displayed; `ContentArea` computes its own truncated lede inline. The approved lede is being thrown away.** Either never wired or regressed.

Focus 3 tabs and their friction:
1. **Term Map** (`TermMap.tsx`): most informative view. Cluster labels come from one model's piles at a time with no inline "whose labels"; lens hidden behind a toggle with no first-use guidance; "Kruskal's stress-1" shown with no anchor; cluster colors perceptual but categorically meaningless; term bootstrap ellipses (`term_mds_uncertainty`) computed but only thin-rendered.
2. **Model Map** (`MDSPlot.tsx`): model dots + bootstrap ellipses. Provider-color legend buried; the one "low output concentration" model's ellipse is omitted with no inline explanation (audit F5 open here).
3. **Cluster Tree** (`ClusterTree.tsx`): dendrogram with branch probabilities. Not journalist-readable; merge-distance axis + "branch probability" unanchored.
4. **Free Lists** (`FreeListCompare.tsx`): top-20 per model with Sutrop CSI. CSI shown with no scale anchor; `f_mentions/n_runs` uninterpreted; no shared-vs-unique view.
5. **Similarity** (`SimilarityHeatmap.tsx`): n×n, 5-stop ramp. Numeric cell labels + CI brackets not shown (`similarity_ci` loaded but unused at the visual layer); **the Phase 6 T5/T6 CI-crosses-null reduced-saturation R10 rule appears not carried into the rebuilt heatmap, a suspected R10 visual regression, needs verification.**
6. **Centrality** (`CentralityChart.tsx`): ranked bars + whiskers. Scale unlabeled (bars ~0.20-0.27); whiskers are 95% bootstrap CIs but no inline note; no comparison anchor.
7. **Pile Structure** (`PileStructure.tsx`): per-model piles with model-supplied labels. No CSI/freq on items; no cross-model pile correspondence; the key CDA finding (N piles per model) buried; the labels are model-supplied (a methodology subtlety a journalist would mistake for ground truth).

### 3.3 Focus 1 (Individual model)
OCI-ranked list with concentrated/moderate/diffuse tier badges (CDA-clean). Without an OCI scale anchor, the tier thresholds look arbitrary; `oci_low_concentration_threshold = 3.0` origin (Romney classical eigenratio) is not surfaced. The "why is run distribution interesting" answer (each run is a fresh stochastic-decoder sample; concentrated output clusters, diffuse spreads) is missing. Bootstrap caveat in `copy/focus1.ts:64-66` correct but likely under-surfaced; verify it renders.

### 3.4 Focus 2 (Within-family)
Single-model families show the correct "requires two or more models from the same provider" note, but most providers are single-model on most domains, so the default Focus 2 view is frequently empty and a cold visitor bounces. Within-family similarity has the same unlabeled 0-1 scale problem.

### 3.5 Failures-as-findings: MISSING from the live UI
`apps/dashboard/public/data/failures/{family,holidays,food}.json` exist on disk. The Phase 6 T9/T10 failures surface shipped 2026-05-12, but **the 2026-05-25 frontend rebuild dropped it entirely; a grep for `failures` in `apps/dashboard/src/` returns no component.** This is the single largest §1.5 / Mark-binding-directive regression in the current UI ("failures are findings" is Mark's load-bearing framing). The data + the CDA-SME-approved `framing_note` already exist; only the component is missing. Class: structural restore.

### 3.6 Cross-cutting
- **No glossary / statistic-anchor pattern.** Every numeric finding is a number with at most a one-clause tooltip. A reusable "click ⓘ for a one-paragraph anchor" affordance is the highest-leverage 2.1 fix.
- **No journalist landing path.** Every visitor hits the same wall of charts.
- **No "what is missing" disclosure.** A reader cannot tell food has 8 models vs family's 15, or that no longitudinal data exists, without cross-referencing manifest.json. Problem 2.2 is invisible from inside the dashboard.
- **Methodology page placeholder for ~90% of its content.**
- **Published-lede vs computed-lede mismatch** (§3.2).
- **Suspected heatmap R10 regression** (§3.2 item 5).

Methodology-scaffold will resolve: corpus-lens anchor, the five-link chain, the §1.5.3 limitations, the "mismatch is the finding" lead. It will NOT resolve: per-chart inline statistic anchors, the missing failures surface, the Data-tab placeholder, the lede mismatch, the per-chart ⓘ affordances.

---

## 4. Part 2: Data gaps inventory

### 4.1 Current slate (`manifest.json`, 2026-05-31)
family 15 / holidays 14 / food 8 models.

### 4.2 Tracked but uncollected (`data/models/registry.json`)
~15 of 22 registry entries have zero records. Notable absences from the live slate: Cohere Command A, DeepSeek Chat V3.1, Gemma 4, Z.ai GLM 5.1, Qwen (3.6 Plus / 3.5-9B, major family entirely absent), Llama 4 Scout. The slate could roughly double without changing the discovery process.

### 4.3 Gaps by type
- **G1 Sparse domains** (food 8 vs family 15): High interpretive severity (readers assume food is less interesting). Collection campaign; no CDA SME.
- **G2 Single-domain models:** per-model cross-domain drift impossible. Collection campaign; no CDA SME.
- **G3 Zero-record registry entries** (Cohere listed but absent is awkward): High. Runbook execution; no CDA SME.
- **G4 No multi-date / longitudinal data:** High; DriftTracker deferred (R10 needs >=2 dates per `model_version_returned`). Data acquisition no CDA SME; **dashboard exposure of drift yes CDA SME** (framing of "what a corpus-lens shift between two dates means").
- **G5 N below 30 not disclosed:** Low-med. Publish-layer surfacing; no CDA SME.
- **G6 No prompt-variant exposure** (8 variants exist in the pipeline; dashboard shows only canonical): Low, but limits the "falsify us by changing the prompt" defense. **CDA SME** on variance-attribution framing.
- **G7 No per-finding provenance surface** (`provider_request_id` + SHA256 exist per record, not linked from charts): Low for journalists, high for researchers. Plumbing; no CDA SME.
- **G8 Three domains is the whole claim space:** deferred (Phase 10).
- **G9 English-only** (§1.5.3 #2): Phase 9 cannot fix, must surface more visibly. **CDA SME** (copy).

### 4.4 Routing
G1/G2/G3 = Mark + runbook (operational). G4 = Mark + campaign + CDA SME on the surface. G5/G7 = Architect -> Coder. G6 = Architect -> CDA SME -> Coder. G9 = CDA SME -> Coder.

---

## 5. Part 3: Viz alternatives survey

### 5.1 Current charts: augmentation (agent-gateable) vs replacement (FT-designer)
- **Term Map:** augment with inline anchors (stress, cluster labels), term-ellipse opacity control, sticky "whose piles label these clusters" chip. Replace: convex-hull-with-confidence-band; small-multiples micro-term-map per model.
- **Model Map:** augment with no-ellipse-case note, optional centrality-as-ring-thickness, first-class legend. Replace: **biplot** (model dots + term dots in one MDS space) collapses Term Map + Model Map into one and answers "which terms pull which models together."
- **Cluster Tree:** augment with branch annotations + anchor. Replace: sortable cluster grid for non-researchers, dendrogram as researcher toggle.
- **Free Lists:** augment with "shared with N models" badge, CSI anchor, sort modes. Replace: rank-rank scatter for pairwise comparison.
- **Similarity Heatmap:** **fix R10 regression first**, restore numeric cells, add hierarchical ordering. Replace: chord diagram when N>12 (15 models is near-unreadable as a heatmap).
- **Centrality:** augment with scale annotation + anchor. Acceptable as-is for FT pass.
- **Pile Structure:** augment with pile-count comparison at top + model-supplied-label disclosure. Replace: parallel-sets / Sankey of which terms move between which model's piles.

### 5.2 Questions LSB answers but does not visualize
Most-contested-terms (partial via ellipse width); same-provider vs cross-provider similarity (Focus 2 empty for single-model families); **prompt-phrasing effect (sensitivity study exists, not visualized at all)**; per-finding provenance (not visualized); **what-failed-and-why (regression, must restore)**; cross-version drift (data-blocked on G4); where-does-model-X-disagree-with-consensus-most (data exists, not visualized).

### 5.3 Fold-in from the audit P2 backlog (do regardless of sub-phase choice)
- **T9** label-placement algorithm copy-pasted 3x -> `lib/labelPlacement.ts` (cleanup).
- **T10** provider-color hex->token migration finish (Timeline, ProviderTree).
- **T15** heatmap threshold + ramp dup + ClusterTree hardcoded cluster hex -> tokens (bundle with the R10 regression fix).

### 5.4 Polish-vs-overhaul cut
**Agent-gateable polish:** all ⓘ-anchor work; the heatmap R10 regression; restoring failures-as-findings; wiring `generated_lede`; the Data-tab scaffold; surfacing the methodology page; T9/T10/T15; per-statistic glossary; the "what's missing" disclosure widget.
**FT-designer-scope** (`docs/FRONTEND_DESIGNER_BRIEF.md`): typography + color overhaul; OWID-style article-with-explorer architecture; biplot; Sankey/parallel-sets piles; rank-rank free lists; lede pull-quote treatment; mobile refresh. Both tracks needed; sequentially independent.

---

## 6. Part 4: Proposed decomposition (9a / 9b / 9c)

Dependency: methodology scaffolding ⊂ data ⊂ viz overhaul. Interpretive friction (9a) is mostly orthogonal to data and runs concurrently with 9b.

### 6.1 Phase 9a: interpretive-friction closeout (agent pipeline, ~3-6 sessions)
Standard gates (Architect -> CDA SME on copy/framing -> UI/UX on layout/a11y -> Coder -> Reviewer -> Tester). Provisional tasks:
1. Restore failures-as-findings surface (Phase 6 T9/T10 carry-forward).
2. Wire `generated_lede` from JSON to `ContentArea` lede.
3. Fix the SimilarityHeatmap R10 regression (CI-crosses-null reduced saturation + numeric cells + CIs).
4. Methodology-page final prose (after Mark finalizes the scaffold).
5. Reusable per-statistic ⓘ anchor system (Smith's S, CSI, Romney, OCI, centrality, MDS coords, bootstrap CI); CDA SME signs the copy once, reused everywhere.
6. Data-tab scaffold (DOI / HF / Zenodo / GitHub / bundle link cards).
7. Site-shell one-line LSB description.
8. "What's missing" cross-cutting disclosure widget (per-domain N, English-only, single-date); CDA-SME copy.
9. Per-chart inline anchors hardened across all Focus 1/2/3 surfaces.
10. Audit P2 cleanups T9 + T10 + T15.

### 6.2 Phase 9b: data campaigns (Mark-operated + CDA SME on drift framing only)
Close G1+G2+G3+G4 via the runbook (`docs/proposed/2026-06-08-new-model-incorporation-runbook.md`). Operational steps:
- B1 collect chosen zero-record entries (recommend Qwen + Cohere + Gemma; biggest interpretive payoff, activate currently-empty Focus 2 families).
- B2 bench up food toward the family slate.
- B3 second collection date on a small subset (recommend Claude Opus 4.6 + GPT-5.4 on family) to unlock DriftTracker.
Load-bearing fact: every campaign retroactively changes the cross-model measures for that domain, so 9a methodology copy must be parametric ("across N models"), not literal.

### 6.3 Phase 9c: FT-designer viz overhaul (parallel track, outside the agent pipeline)
Per the FT-designer brief; the designer gates only through CDA SME (methodology copy), Architect (schema), and Mark (doctrinal reshapes). Can start as soon as 9a's structural floor lands (failures restored, R10 fixed, methodology page final, ⓘ system shipped). DriftTracker design waits on 9b B3.

### 6.4 Sequencing
9a in full + 9b B1/B2 in parallel start now. Hand the FT-designer brief off once 9a's structural floor lands. Hold the DriftTracker (9c) for 9b B3 data.

### 6.5 Recommended first move
**Restore the failures-as-findings surface (9a T1).** It is a binding Mark directive the current dashboard violates; the data + CDA-SME-approved framing copy already exist in `failures/*.json`; the only missing piece is the component; the Phase 6 T9/T10 verdicts document the constraints; one Architect -> CDA SME -> UI/UX -> Coder cycle should clear in a session. The smallest fix is also the highest-leverage one because it restores Mark's load-bearing posture to every cold visitor immediately.
**Alternative quick win:** wire `generated_lede` (9a T2): the approved prose is already in the JSON; one file, one diff.
**Do not do first:** methodology prose (Mark-dependent), the ⓘ system (high CDA SME load, batch it), or 9b (Mark has not picked scope).

---

## 7. Open questions for Mark
1. 9a scope: full 10-task list, or a curated subset?
2. 9b priority order among B1 / B2 / B3? (Recommend B1 first.)
3. Activate the FT-designer track in parallel with 9a, or hold until 9a lands?
4. "What's missing" disclosure widget posture: persistent strip / per-domain card / inline limitations callout? (UI/UX.)
5. Author from the methodology scaffold as-is, replace it, or hand back for a different posture first? (Gates 9a T4.)
6. Audit P2 cleanups T9 + T10 + T15 in 9a, or keep in the refactor backlog? (Recommend 9a; T15 bundles with the R10 fix.)
7. 9a -> 9c handoff trigger: recommend after T1 (failures), T3 (R10 fix), T4 (methodology final), T5 (ⓘ system).

## 8. Open audit items intersecting Phase 9
- **F5** (CDA SME): R10 semantics for degenerate uncertainty (`semi_major <= 0`: dot drawn, ellipse skipped). Resolve before 9a MDSPlot anchor work to avoid a re-do.
- **T-CI-vitest** (P2): CI does not run the dashboard vitest; resolve before 9a starts shipping visual fixes (recommend 9a T0).

---

*End of Phase 9 kickoff. Decision surface, not an implementation plan. Mark reads, refines, returns to the Architect for per-task decomposition.*
