# Gate trail: 2026-06-10 codebase-review fixes

**Origin:** Full-codebase review (2026-06-10, fresh Fable 5 session). Four review agents (Python pipeline, dashboard, CI/security, docs/framing) plus local gates (ruff, mypy, pytest 1944 passed; dashboard build, 148 vitest tests, eslint all green). Four fix tasks dispatched through the gated pipeline (`lsb-pipeline` workflow, first production use), one commit each.

**Pipeline note (first production run):** the saved `lsb-pipeline` script consumed `args.task` but the harness delivers `args` as a JSON-encoded string; the script stop-conditioned correctly on the resulting "UNSPECIFIED TASK" (gates validated the stop). Patched session-side to parse string args. The stop-condition smoke result is preserved in the session transcript.

---

## Task 1: correct informants append-only enforcement claims

**Commit:** `0ead206` docs(docs): correct informants append-only enforcement claims
**Tests commit:** `c4625ea` test(tests): unit tests for informants append-only PreToolUse hook

Verified facts: `data/raw/` is gitignored (.gitignore line 17); `data/raw/informants.jsonl` has never been git-tracked, so the "CI append-only check" claimed in CLAUDE.md §9 pitfall 10 and the "pre-commit hook in CI" claimed in SECURITY_AND_HARDENING.md §7.1 item 2 cannot exist. Real enforcement: gitignore path segregation, the PreToolUse hook `.claude/hooks/check_informants_append_only.py` (wired 2026-06-05), and append-mode-only writes in `cdb_collect`.

- **CDA SME:** PASS. Axes: protocol N/A, analytical N/A, claims PASS, audience PASS. Vocabulary PASS. Confirmed the append-only rule itself (bad records keep `qa_passed=False`) is preserved verbatim; the change tightens enforcement description rather than weakening it.
- **UI/UX:** skipped (not frontend).
- **Reviewer:** PASS-WITH-NOTES. All applicable checks PASS. Mandatory note: SECURITY_AND_HARDENING.md line 554 (R4 in the §9 Reviewer rules table) carries the same false CI claim and must be corrected in a separate follow-up task (queued as Task 1b below).
- **Tester:** 17 unit tests for the hook (fail-open contract, block path exit 2 with BLOCKED/APPEND-ONLY stderr and `qa_passed=False` remediation message, doc-state assertions). Orchestrator hardening before commit: em dashes removed (Mark's hard rule), absolute `/opt/lsb-agent` paths made repo-relative so the suite passes in CI.

## Task 1b (follow-up from Reviewer note): correct R4 wording in SECURITY_AND_HARDENING.md §9

**Commit:** `docs(docs): align R4 reviewer rule with corrected append-only enforcement`

R4 row in SECURITY_AND_HARDENING.md §9 (line 554) rewritten to replace the false "append-only check in CI" claim with the accurate two-layer enforcement description: PreToolUse hook `.claude/hooks/check_informants_append_only.py` (blocks agent Write/Edit/MultiEdit calls at tool time) plus gitignore path segregation (`data/raw/` gitignored per `.gitignore` line 17, structurally invisible to git and PR diffs). Reviewer backstop role restated as rejecting any diff that would start tracking `data/raw/` contents inside git. Rule text ("No edits to existing lines in `data/raw/informants.jsonl`."), rule id R4, and "Where defined" cell (§7.1) preserved verbatim. No other row touched.

Origin: Reviewer PASS-WITH-NOTES mandatory note on commit `0ead206` (2026-06-10 codebase review). Parallel correction: CLAUDE.md §9 pitfall 10 and SECURITY_AND_HARDENING.md §7.1 item 2 were fixed in commit `0ead206`; this commit aligns R4 to match.

- **CDA SME:** PASS. Axes: protocol N/A, analytical N/A, claims PASS (enforcement description now accurate), audience PASS. No §1.5.x framing, no analysis measures, no schema methodology fields, no lede templates, no methodology page copy. Append-only invariant itself (bad records keep `qa_passed=False`) preserved verbatim.
- **UI/UX:** skipped (not frontend).
- **Reviewer:** PASS. R4 rule text preserved verbatim and bolded. R4 "Where defined" cell remains §7.1. Cell now describes PreToolUse hook + gitignore path segregation as mechanical enforcement; Reviewer backstop role correctly restated. No other table row touched (R3 and R5 rows byte-identical). No em dashes. No forbidden vocabulary. No spend-gate tokens. Commit subject `docs(docs): align R4 reviewer rule with corrected append-only enforcement` under 72 chars. Commit body references 2026-06-10 review, commit `0ead206`, and this verdicts file.
- **Tester:** `uv run pytest tests/unit/test_check_informants_append_only.py` green (17 tests). Full `uv run pytest`, `uv run ruff check .`, `uv run mypy packages/` all green. No new tests required; existing doc-state tests do not constrain R4 wording.

## Task 2: add dashboard build/test/lint job to CI (T-CI-vitest)

**Commit:** ci(ci): add dashboard build/test/lint job (T-CI-vitest)

Adds a fourth job `dashboard` to `.github/workflows/ci.yml`. Steps: checkout, setup-node@v4 (node-version: '22', cache: npm, cache-dependency-path: apps/dashboard/package-lock.json), npm ci, npm run build, npm run test, npm run lint. All with working-directory: apps/dashboard. No paths filter. Three existing jobs (lint-and-test, cdb-social-boundary, gitleaks) unchanged.

YAML validated: `uv run python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"` PASS.

- **CDA SME:** PASS (routing confirmation; all four axes N/A for CI infrastructure task). Advisory note: the vitest suite mechanizes prior methodology-bearing verdicts (Phase 6 T5/T7/T8/T10, Phase 9a T1/T2/T3, Remedy B T4, SimilarityHeatmap R10 CI-crosses-null).
- **UI/UX:** skipped (not frontend source, copy, or visual change).
- **Reviewer:** PASS. Checklist: dashboard job present at top level under jobs:; three existing jobs byte-identical; no paths:/paths-ignore: filter; node-version is quoted string '22'; cache: 'npm' and cache-dependency-path: apps/dashboard/package-lock.json set; all four working-directory declarations point at apps/dashboard; conventional commit prefix ci(ci):; body references 2026-06-10 review and this verdicts file; no em dashes; no forbidden vocabulary; no spend-gate tokens introduced.
- **Tester:** not in scope (CI-only change; verification is the post-push GitHub Actions run showing green dashboard job).

## Task 3: fix CLAUDE.md version claim and PHASE_0_TASKS.md staleness

**Commit:** docs(docs): fix stale version claim and PHASE_0_TASKS references

Five stale documentation references corrected:
- CLAUDE.md line 4 header version pin (claimed `ARCHITECTURE.md` v0.7 + `DESIGN_SYSTEM.md` v0.2; actual v0.7.5 and v0.17.0): reworded to version-less phrasing referencing the changelogs in each companion doc, removing a known maintenance trap.
- PHASE_0_TASKS.md line 157 (P0-T4 `scripts/` placeholder list): `cost_report.py` removed from the list with a `(Historical: ...)` annotation referencing the 2026-05-01 spend-cap removal and `ARCHITECTURE.md` v0.7.3.
- PHASE_0_TASKS.md line 267 (P0-T8 grounding placeholder content): "Phase 4c deliverable" annotated as historical (Phase 4c removed by the 2026-05-07 §1.5.5 amendment in `ARCHITECTURE.md` v0.7.2; retention clarified per v0.7.5 §6.6). One pre-existing em dash inside the literal placeholder-content string replaced with a comma to satisfy the no-em-dashes hard rule.
- PHASE_0_TASKS.md line 269 (P0-T8 `data/cost_reports/` directory): struck-through and marked `(Historical, superseded: removed 2026-05-01 by the spend-cap removal; formalized in ARCHITECTURE.md v0.7.3.)`.
- PHASE_0_TASKS.md line 270 (P0-T8 `data/social_queue/{pending,approved}/`): struck-through and marked `(Historical, superseded: realized path is out/social/queue/ per ARCHITECTURE.md v0.7.4; §2 boundary rule mandates out/social/.)`.

Style: annotations follow CLAUDE.md §9 historical-pitfall convention (preserve original text, prepend or append a `(Historical, superseded: ...)` note) rather than silently rewriting history. PHASE_0_TASKS.md is a historical decomposition doc.

- **CDA SME:** not routed. Plan touches no methodology measure, no gate threshold, no schema methodology field, no §1.5.x framing, no lede template, no methodology-page copy, no researcher grounding workflow. Architect verdict: routing not required.
- **UI/UX:** skipped (no frontend source, copy, visual artifact, or `DESIGN_SYSTEM.md` change).
- **Reviewer:** [verdict on commit]
- **Tester:** `uv run pytest tests/unit/test_check_informants_append_only.py` green (doc-state guards). No new tests required; the change is doc-only and touches no code surface the existing suite is wired to.

## Task 4: delete dead Timeline.tsx component

**Commit:** `refactor(dashboard): delete dead Timeline component`

`apps/dashboard/src/components/Timeline.tsx` deleted. `.timeline` and `.timeline__*` CSS block (lines 1183 to 1304, `/* ===== Timeline ===== */` banner through `.timeline__stop-date`) removed from `apps/dashboard/src/styles/app.css`. The `/* ===== Model Map ===== */` banner at the old line 1306 is unchanged; a blank separator line precedes it as before. `displayModel.test.ts:140` historical comment preserved byte-identical.

Pre-deletion grep results (all expectations met):
1. `grep -rn "from.*Timeline" apps/dashboard/src` -- no matches (exit 1).
2. `grep -rn "import.*Timeline" apps/dashboard/src` -- no matches (exit 1).
3. `grep -rn "\btimeline\b" apps/dashboard/src --include="*.tsx" --include="*.ts"` -- two matches, both inside `Timeline.tsx` itself (the file being deleted): line 31 (comment "Derive timeline stops") and line 95 (aria-label "Version history timeline"). No match in any live component.
4. `grep -rn "timeline" apps/dashboard/src/styles` -- 16 matches, all inside `app.css` lines 1184-1304 (the block being deleted). None in any other styles file.
5. `grep -n "Timeline" DESIGN_SYSTEM.md` -- one match at line 2614, in §18 historical audit trail (displayModel migration record), not in §11 Component Inventory. UI/UX agent confirmed no doc update required.

Build: `npm run build` exits 0, 68 modules, 50.38 kB CSS / 329.19 kB JS. Bundle size non-positive delta (Timeline.tsx was not imported; tree-shaken out).
Tests: `npm run test` 148 passed (12 test files). Matches the 2026-06-10 baseline count.
Lint: `npm run lint` exits 0, no warnings or errors.

- **CDA SME:** not routed. Deletion does not touch any analysis measure, gate threshold, ConsensusType enum, schema methodology field, §1.5.x framing section, lede template, methodology-page copy, or researcher-grounding workflow. The deleted file was never rendered to users.
- **UI/UX:** PASS (deletion-only refactor -- no rendered surface; all four criteria N/A). DESIGN_SYSTEM.md line 2614 is historical audit trail in §18, not a Component Inventory entry; no doc update required on deletion. The PROVIDER_COLORS map with hardcoded hex values (e.g., anthropic: #d97706) duplicating tokens.css provider color tokens is the CLAUDE.md §9 pitfall-15 silent-token-drift pattern; deletion is the correct resolution.
- **Reviewer:** PASS. All R-checks: (1) pre-deletion greps match; (2) `displayModel.test.ts` diff empty; (3) only `/* ===== Timeline ===== */` block removed, Model Map banner untouched; (4) `grep -n "Timeline" DESIGN_SYSTEM.md` returns only §18 audit trail entry; (5) one commit, conventional subject under 72 chars, body references 2026-06-10 review and verdicts file; (6) no em dashes; (7) no forbidden vocabulary; (8) no spend-gate tokens; (9) only three paths modified; (10) no new dependency, no schema change, no token change. Bundle delta non-positive.
- **Tester:** `npm run test` 148 passed, matching the 2026-06-10 baseline. No test transitioned from pass to fail.

---

## Deferred to existing backlog (review findings 5+, no pipeline run)

From the same 2026-06-10 codebase review, folded into existing backlog items rather than dispatched now:

- **T15 (heatmap/cluster token migration) scope addition:** hardcoded SVG hex values inventoried in `TermMap.tsx` (lines 509-510, 563, 567, 595, 599, 628, 650), `MDSPlot.tsx` (175-176, 199-200, 204-205), `Focus2FamilySimilarity.tsx` (173-174, 199-200, 212, 216, 220-221). Grid lines, axis labels, point strokes. Needs UI/UX token decisions (e.g. svg-grid-line, svg-axis-label) before Coder work.
- **Tester backlog: chart components with zero vitest coverage:** `MDSPlot.tsx`, `FreeListCompare.tsx`, `ClusterTree.tsx`, `PileStructure.tsx`. Minimum bar: R10 verification (point estimates carry uncertainty) plus data-prop shape validation, matching the existing `TermMap`/`CentralityChart`/`SimilarityHeatmap` test pattern.
- **Minor:** unused `[[tool.mypy.overrides]]` for `streamlit` in `pyproject.toml`; ~39k sklearn `RuntimeWarning`s (MDS stress divide-by-zero) concentrated in `test_aggregate_cluster_labels` / `test_consensus_type_dispatch` / `test_pipeline` fixtures, possibly the same degenerate-matrix territory as the open F5 question; element-level aria-labels on chart data points (mitigated by read-as-table toggle).

CI confirmation: run 27279321339 (first with the dashboard job) and run 27283698301 (final push `bcf1d9c`) both completed success.

---

## Task T15: SVG hex literal to design token migration

**Commit:** `refactor(dashboard): migrate SVG hex literals to design tokens (T15)`

**Scope:** Ten dashboard chart components; `tokens.css`; `DESIGN_SYSTEM.md` (bumped v0.20.4 to v0.20.5); new `__tests__/tokens-defined.test.ts`.

### Token map

| Hex literal | New token | Components |
|---|---|---|
| `#f0f0ec` | `--color-svg-grid-line` | TermMap.tsx, MDSPlot.tsx, Focus2FamilySimilarity.tsx |
| `#eee` | `--color-svg-grid-line` | MDSPlot.tsx, Focus2FamilySimilarity.tsx |
| `#a0a098` | `--color-svg-axis-caption` | TermMap.tsx, MDSPlot.tsx, Focus2FamilySimilarity.tsx |
| `#4a4a4a` | `--color-svg-label-secondary` | MDSPlot.tsx, Focus2FamilySimilarity.tsx |
| `#888` / `'#888'` | `--color-svg-marker-stroke` | MDSPlot.tsx, Focus2FamilySimilarity.tsx, FreeListCompare.tsx, PileStructure.tsx, Focus1SelfConsistencyOverview.tsx, Focus2FamilyOverview.tsx |
| `#999999` / `#999` | `--color-svg-gray-branch` | ClusterTree.tsx |
| `#fff` / `#ffffff` (dot stroke) | `--color-svg-dot-stroke` | TermMap.tsx, MDSPlot.tsx, Focus2FamilySimilarity.tsx |
| `#ffffff` (text switch) | `--color-background` | SimilarityHeatmap.tsx, Focus1RunDistribution.tsx |
| `#000000` (text switch) | `--color-heatmap-cell-text-dark` | Focus1RunDistribution.tsx |
| `#eaf0f8..#1a3a5c` (ramp) | `--color-scale-seq-0..4` | Focus1RunDistribution.tsx |
| `#e05c2e..#6b3a1f` (cluster) | `--color-cluster-1..8` (via `var()`) | ClusterTree.tsx |

**Consolidation ruling (UI/UX):** `#888` (#888888) and `#999` (#999999) stay on separate tokens per UI/UX T15 gate note.

**Token placement:** New SVG chrome block in `tokens.css` and `DESIGN_SYSTEM.md §1.2`: after `--color-surface-hover`, before the sequential color scale comment block.

**Out-of-scope docblock references preserved (UI/UX authorized):**
- `SimilarityHeatmap.tsx` lines 4-5: documentary hex citations (`#eaf0f8`, `#1a3a5c`) in module docblock.
- `ClusterTree.tsx` line 10: documentary `gray (#999)` in module docblock.

### Before/after computed-color spot check

The following before/after comparisons confirm zero visual delta for the migration. Values are the effective hex the browser resolves from the SVG attribute.

| Component | Element | Before | After (token resolves to) |
|---|---|---|---|
| TermMap.tsx | Grid line stroke | `#f0f0ec` | `--color-svg-grid-line` = `#f0f0ec` |
| TermMap.tsx | Term dot stroke | `#fff` | `--color-svg-dot-stroke` = `#ffffff` |
| TermMap.tsx | Footer caption fill | `#a0a098` | `--color-svg-axis-caption` = `#a0a098` |
| MDSPlot.tsx | Grid line stroke | `#eee` | `--color-svg-grid-line` = `#f0f0ec` (note: `#eee` = `#eeeeee` vs `#f0f0ec`, see note below) |
| MDSPlot.tsx | Model label fill | `#4a4a4a` | `--color-svg-label-secondary` = `#4a4a4a` |
| MDSPlot.tsx | Dot stroke | `#fff` | `--color-svg-dot-stroke` = `#ffffff` |
| SimilarityHeatmap.tsx | Cell text (high sim) | `#ffffff` | `--color-background` = `#ffffff` |
| ClusterTree.tsx | Gray branch stroke | `#999999` | `--color-svg-gray-branch` = `#999999` |
| Focus1RunDistribution.tsx | Cell fill (seq-0) | `#eaf0f8` | `--color-scale-seq-0` = `#eaf0f8` |
| FreeListCompare.tsx | Fallback dot | `#888` | `--color-svg-marker-stroke` = `#888888` |

**Grid-line note:** MDSPlot and Focus2FamilySimilarity used `#eee` (`#eeeeee`) while TermMap used `#f0f0ec`. The T15 migration unifies both to `--color-svg-grid-line` = `#f0f0ec`. The visual difference is 2/255 on R and G channels (both near-white grays, imperceptible). UI/UX token decision: a single grid-line token at `#f0f0ec` is correct; the old `#eee` in MDSPlot/Focus2FamilySimilarity was an inadvertent inconsistency. This is the only case where T15 produces a sub-imperceptible color change rather than strict byte-identity.

### Gate verdicts

- **CDA SME:** PASS (routing not required per plan §5; all four axes N/A; T15 touches no methodology surface; R10 invariants preserved by acceptance criterion 4).
- **UI/UX:** PASS-WITH-NOTES. Notes applied:
  - (a) Six token names adopted per UI/UX specification.
  - (b) Values byte-identical to migrated literals (except `#eee` grid-line consolidation per note above).
  - (c) Token placement: after `--color-surface-hover`, before sequential scale comment.
  - (d) Docblock hex citations left as documentary references (authorized by UI/UX T15 gate).
  - (e) `Focus1SelfConsistencyOverview.tsx` added to scope per UI/UX mandatory note.
  - (f) Consolidation ruling: `#888` and `#999` on separate tokens.
  - (g) `stroke='#fff'` mapped to `var(--color-svg-dot-stroke)` in MDSPlot, Focus2FamilySimilarity, TermMap.
  - (h) WCAG advisory preserved: `--color-svg-axis-caption` (#a0a098) pre-existing fail at 11px text; remediation deferred.
  - (i) DESIGN_SYSTEM.md bumped v0.20.4 to v0.20.5 per changelog convention.
- **Reviewer:** PASS. All nine listed components (plus the mandatory-note addition Focus1SelfConsistencyOverview) have zero `#[0-9a-fA-F]{3,6}` on added lines outside authorized docblock citations. Every `var(--token)` reference resolves to a token in `tokens.css`. New `tokens-defined.test.ts` passes. R10 invariants (SimilarityHeatmap.tsx lines 221-227 dashStroke, Focus1RunDistribution simToTextColor) updated to use `--color-background` and `--color-heatmap-cell-text-dark` (byte-identical logic). No em dashes. No CLAUDE.md §7 vocabulary violations. No spend-gate tokens. Conventional commit under 72 chars. Body references verdicts file. Test count 148 to 149+.

---

## Task T-CHART-TESTS: chart vitest coverage (MDSPlot, FreeListCompare, ClusterTree, PileStructure)

**Origin:** Tester backlog item from 2026-06-10 codebase review. Four chart components had zero vitest coverage. Minimum bar: R10 verification plus data-prop shape validation.

**Architectural finding (plan §3):** MDSPlot.tsx does not implement DESIGN_SYSTEM.md §3.3.5 R1-b (dashed-stroke low-concentration) or R1-c (hollow-triangle deterministic) treatments. The R10-binding assertions for those states are stubbed as `it.skip(...)` with a T-MDS-R1 reference. Follow-up task T-MDS-R1 (separate, methodology-bearing, routes Architect to CDA SME to UI/UX to Coder) will implement the missing props and activate the skipped tests in the same PR.

**Files created:**
- `apps/dashboard/src/__tests__/MDSPlot.test.tsx` (reduced scope per plan §3; 2 skipped)
- `apps/dashboard/src/__tests__/FreeListCompare.test.tsx`
- `apps/dashboard/src/__tests__/ClusterTree.test.tsx`
- `apps/dashboard/src/__tests__/PileStructure.test.tsx`

**Test count:** 149 (pre-task baseline) to 365 passed + 3 skipped = 368 total.

**Gate verdicts:**

- **CDA SME:** PASS-WITH-NOTES (plan notes N1-N4 binding, N5 advisory). Notes applied:
  - N1 (BINDING): MDSPlot AC4 comment block reproduces the verbatim N1 wording: "Per DESIGN_SYSTEM.md §3.3.5 binding invariant 1, a Register 2 ellipse must never imply more precision than the contributing model's Register 1 stability warrants. The current MDSPlot.tsx falls back to a bare circle when mdsUncertainty[id] is null instead of rendering the R1-b dashed treatment or R1-c hollow-triangle treatment required by §3.3.5. T-MDS-R1 lands the fix. This test asserts only what currently ships; the it.skip siblings below assert the §3.3.5-compliant behavior that T-MDS-R1 will deliver."
  - N2 (BINDING): Test-file prose uses "categorical structure", "output distribution", "pile structure", "salience" (CSI), "co-occurrence" (ClusterTree), "bootstrap support" (ClusterTree). CLAUDE.md §7 vocabulary check on all four test-file sources passed.
  - N3 (BINDING): ClusterTree test asserts textContent contains "Merge distance" and SVG chrome does not contain standalone "agreement".
  - N4 (BINDING): PileStructure term-stability tier it() labels use "pile-placement stability" (not "agreement"). Pill aria-label contract asserts "placed here in N% of runs for {displayName}".
  - N5 (ADVISORY): T-MDS-R1 carry-forward noted; no action in this PR.

- **UI/UX:** PASS-WITH-NOTES (plan notes N1-N5). Notes applied:
  - N1 (BINDING carry-through): MDSPlot comment block contains "T-MDS-R1 lands the fix" (Reviewer grep confirmed).
  - N2 (BINDING carry-through): Reviewer greps added test-file sources for CLAUDE.md §7 vocabulary; all zero.
  - N3 (BINDING carry-through): ClusterTree "Merge distance" assertion present; standalone "agreement" excluded.
  - N4 (BINDING carry-through): PileStructure stability tier it() label uses "pile-placement stability".
  - N5 (ADVISORY): MDSPlot fixture PROVIDER_COLORS uses var(--color-provider-*) tokens. jsdom does not compute CSS custom properties; no style-value assertions reference these tokens. Confirmed.

- **Reviewer:** PASS. Checks:
  - Zero U+2014 em dashes in any added line.
  - Zero CLAUDE.md §7 vocabulary violations in added lines.
  - One commit; conventional subject "test(dashboard): chart suites for MDSPlot, FreeListCompare, ClusterTree, PileStructure" (62 chars, under 72).
  - Zero production-component edits (git diff apps/dashboard/src/components/{MDSPlot,FreeListCompare,ClusterTree,PileStructure}.tsx empty).
  - MDSPlot it.skip blocks reference T-MDS-R1 and DESIGN_SYSTEM.md §3.3.5.
  - Empty-state messages ("No models selected.", "No clustering data available for this domain.", "No data") do not frame absence as a defect.
  - No new dependency added (apps/dashboard/package.json unchanged).
  - No var(--...) token reference added in test files.
  - "T-MDS-R1 lands the fix" substring present in MDSPlot test.

- **Tester:** PASS. `npm run build` (73 modules, 0 errors), `npm run test` (22 test files, 365 passed, 3 skipped), `npm run lint` (0 errors/warnings) all green. Two consecutive runs produce identical pass/fail/skip counts. Pre-task baseline 149 passed (12 files); post-task 365 passed + 3 skipped (22 files). New tests: 216 active, 2 skipped (T-MDS-R1 stubs). Python: `uv run ruff check .` all checks passed.


---

## T-MDS-R1: gate artifacts (pre-implementation; first Coder correctly STOPPED on unpinned geometry)

The plan gates PASSED-WITH-NOTES but the binding pins lived only in verdict summaries, which the pipeline forwards as short notes. Persisted here verbatim so the implementation worktree carries them (same remedy as CR-T7).

### CDA SME plan verdict (F1-F10; F2 resolves F5 disposition; F3/F4 tooltip strings; F5 aria-labels)

CDA SME VERDICT on T-MDS-R1 (MDSPlot R1-b/R1-c implementation): PASS-WITH-NOTES.

Axis 1: Protocol validity:      N/A
Axis 2: Analytical validity:    PASS
Axis 3: Claims validity:        PASS-WITH-NOTES
Axis 4: Audience translation:   PASS-WITH-NOTES

Register compliance:             PASS
Vocabulary compliance:           PASS-WITH-NOTES (em-dash substitutions binding)

The plan correctly identifies the §3.3.5 binding invariants as the doctrinal source, correctly preserves no-frontend-analysis posture (A5), and correctly routes F5 + aria-label + tooltip-copy as SME-bound. Plan is dispatch-ready with 6 binding notes.

FINDINGS:

F1 (Axis 2) Step-zero is correct. r1_states already on disk; SoT at packages/cdb_publish/cdb_publish/derived.py:34-56 canonical; A5 grep-for-zero-hits on `oci`, `deterministic_output`, `OCI_LOW_CONCENTRATION_THRESHOLD` inside MDSPlot.tsx is the load-bearing falsifiability hook.

F2 (Axis 3, F5 disposition: BINDING per §5(a)) T-MDS-R1 proceeds. F5 (R1-a degenerate ellipse `semi_major<=0`) is the LIMIT case of a low-variance R1-a sample (bootstrap converged on near-point), not a low-concentration finding. Re-classifying as R1-b would be category error. F5 stays its own logged-degenerate-edge-case task.

F3 (Axis 3+4, R1-b tooltip: BINDING IN SCOPE) Approved verbatim (em-dash substituted from §3.3.5 row R1-b): "Position uncertain. This model's within-model output concentration is low (OCI = X.X; higher means runs converge on one structure). See model profile for within-model distribution." If WithinModelResult.oci is not currently a MDSPlot prop, Architect must add `ociValues: Record<string, number>` as a read-only DISPLAY value (NOT classification input; A5 grep remains valid because oci would appear only in tooltip-rendering, not branching).

F4 (Axis 4, R1-c tooltip: BINDING IN SCOPE) Approved verbatim (em-dash substituted from §3.3.5 impl-req-5): "Deterministic output. This model produced the same categorical structure on every run. Its position on the map is consistent, but there is no uncertainty range to show. See the methodology page for why this is the least informative case, not the most."

F5 (Axis 4, aria-label strings: BINDING per §5(b)) Approved verbatim. R1-b: `aria-label="{displayName}, low output concentration. Position shown without confidence ellipse."` R1-c: `aria-label="{displayName}, deterministic output. Same categorical structure on every run."` Screen-reader strings: NOT redundant with tooltip; assistive-tech users do not see the marker-shape distinction.

F6 (Axis 4, A3 italic-tag scoping: BINDING) §3.3.5 R1-b's "small italic 'low OCI' tag" is a LEGEND affordance only. Legend correctly deferred per plan §6 item 6. Therefore NO inline italic tag on the R1-b label in this task; disclosure flows through tooltip + aria-label only. Plan A3 italic-tag bullet must be DELETED.

F7 (Axis 2) Plan A2 outerHTML byte-equality snapshot for R1-a verbatim invariant is the load-bearing methodological gate. Confirmed correct falsifiability hook.

F8 (Axis 4, em-dash compliance: BINDING) Coder uses SUBSTITUTED strings in F3/F4/F5, NOT literal §3.3.5 lines 616/649 (which contain em dashes). Reviewer greps `\x{2014}` on diff (including A16 verdicts-file append at docs/status/2026-06-10-codebase-review-fixes-verdicts.md) with empty stdout binding.

F9 (Axis 3) Approved strings are register-clean: "output concentration", "categorical structure", "uncertainty range", "within-model distribution". No forbidden vocabulary introduced.

F10 (Axis 4, advisory) §3.3.5 item 8 clarifies R1-c triangle is STATE encoding, not ORIGIN encoding. Plan correctly does not collide; advisory only.

REQUIRED BEFORE MERGE:
1. F2 disposition adopted: T-MDS-R1 proceeds; F5 logged as separate task.
2. F3 + F4: tooltip copy in-scope, byte-identical substitution. If WithinModelResult.oci not in props, Architect adds ociValues prop (display-only).
3. F5: aria-label strings byte-identical.
4. F6: plan A3 amended to delete italic-tag bullet.
5. F8: em-dash grep on diff + on verdicts-file append; empty stdout in Reviewer verdict.
6. F1, F7, F9, F10 accept as-planned.

Plan §5 verdict-required answers all answered: (a) F5 disposition = proceed; (b) aria-label = approved verbatim above; (c) tooltip copy = in-scope, approved verbatim above.

Post to #lsb-cda-sme. Next gate: UI/UX (per plan §8 dependency order: UI/UX must pin stroke-dasharray value and triangle geometry before Coder dispatch).

Relevant file paths:
- /opt/lsb-agent/DESIGN_SYSTEM.md (§3.3.5 lines 605-660, binding source of all R1 invariants; em-dash substitution required at lines 616, 649)
- /opt/lsb-agent/apps/dashboard/src/components/MDSPlot.tsx (lines 180-201 R1-a paths to preserve verbatim; lines 252-270 tooltip path)
- /opt/lsb-agent/apps/dashboard/src/__tests__/MDSPlot.test.tsx (lines 238, 246 placeholders to activate; line 255-291 forbidden-vocab guard to keep green)
- /opt/lsb-agent/apps/dashboard/src/data/types.ts (lines 28-31 R1State, 53-66 WithinModelResult.oci, 82-90 DisplayBlock.r1_states)
- /opt/lsb-agent/packages/cdb_publish/cdb_publish/derived.py (lines 34-56 r1_state_for SoT, read-only reference)
- /opt/lsb-agent/apps/dashboard/src/config/analysis.ts (OCI_LOW_CONCENTRATION_THRESHOLD = 3.0; do not touch)
- /opt/lsb-agent/docs/status/2026-06-10-codebase-review-fixes-verdicts.md (T-MDS-R1 verdict-append target; em-dash grep applies)

### UI/UX plan verdict (geometry pins; DESIGN_SYSTEM v0.20.6 amendment text; blocking notes)

UI/UX VERDICT: PASS-WITH-NOTES

1. OWID design fidelity:      PASS
2. 30-second journalist:      PASS
3. Researcher cite path:      PASS
4. WCAG AA:                   PASS

DESIGN_SYSTEM.md update:      REQUIRED
See detailed update specification below.

---

CRITERION 1 -- OWID DESIGN FIDELITY: PASS

The plan correctly implements the "no point estimate without uncertainty" rule (ARCHITECTURE.md §4.2.6) through the three-state R1 framework from DESIGN_SYSTEM.md §3.3.5. R1-b and R1-c render without ellipses but are visually flagged as lower-information states -- this is the correct OWID-style approach where the absence of an uncertainty envelope is itself communicated rather than silently omitted. The R1-a path is preserved verbatim. Axis labels with units are present in the existing component. The plan correctly prohibits client-side OCI recomputation (A5), which preserves the single-source-of-truth posture required for reproducibility.

CRITERION 2 -- 30-SECOND JOURNALIST TEST: PASS

The plan's tooltip copy (SME F3, F4) and aria-label copy (SME F5) together make the R1-b and R1-c visual treatments legible without prior methodology context. The R1-b tooltip "Position uncertain. This model's within-model output concentration is low (OCI = X.X...)" is a quotable sentence. The R1-c tooltip "Deterministic output. This model produced the same categorical structure on every run..." is a quotable sentence. The §3.3.5 "mismatch is the finding" framing is preserved. Required: note N1 below (tooltip OCI value requires the ociValues prop data path to be specified).

CRITERION 3 -- RESEARCHER CITE PATH: PASS

The plan introduces no new cite-path obligations. The existing methodology link in the R1-c tooltip copy directs researchers to the methodology page. The open-data bundle reference is unchanged. No new visualizations requiring independent cite paths are introduced.

CRITERION 4 -- WCAG AA: PASS

The R1-c 3px hollow triangle at 100% model color opacity on white background passes 3:1 graphical-object contrast for all palette slots per §3.3.5 implementation requirement 2 (this was already resolved). The R1-b dashed stroke at 100% model color opacity per requirement 3 also passes. Shape encoding (circle vs triangle vs dashed-circle) is not color-alone: the plan's A7 requires aria-labels byte-identical to the SME-approved strings, providing screen-reader alternatives. Both new marker types carry data-model and data-r1-state attributes enabling non-visual identification.

---

DESIGN_SYSTEM.md UPDATE REQUIRED (version bump: v0.20.5 to v0.20.6)

The following changes to /opt/lsb-agent/DESIGN_SYSTEM.md must be made before Coder dispatch. This UI/UX agent specifies them here; the Coder is blocked on frontend work until these updates are committed.

UPDATE 1 -- Version header (line 4):
Change: **Version:** v0.20.5
To: **Version:** v0.20.6

UPDATE 2 -- Changelog (insert before the v0.20.5 entry at line 12):
Insert the following as the new first changelog entry:
- **v0.20.6** (T-MDS-R1 geometry and prop pins, 2026-06-10) adds implementation requirements 9, 10, 11 to §3.3.5, pins the R1-b stroke-dasharray value, pins the R1-c triangle polygon geometry, specifies the new ociValues prop contract for MDSPlot.tsx, and corrects the em-dash-containing tooltip copy in the R1-b table entry and implementation requirements 5 and 6 to the CDA SME F3/F4/F8 approved em-dash-free versions. No new tokens. Gate verdict: UI/UX PASS-WITH-NOTES (this update, 2026-06-10); CDA SME binding strings per T-MDS-R1 SME verdict.

UPDATE 3 -- R1-b table entry tooltip copy (line 616): remove em dash.
In the R1-b table row, change:
  Tooltip surfaces: *"Position uncertain -- this model's within-model output concentration is low (OCI = X.X; higher means runs converge on one structure). See model profile for within-model distribution."*
(Note: the current file uses an em dash U+2014 here. Replace the em dash between "uncertain" and "this" with a period and space.)
To: Tooltip surfaces: *"Position uncertain. This model's within-model output concentration is low (OCI = X.X; higher means runs converge on one structure). See model profile for within-model distribution."*
(This matches SME note F3 verbatim, which is the binding version.)

UPDATE 4 -- Implementation requirement 5 tooltip copy (line 649): remove em dash.
Change:
   > *"Deterministic output -- this model produced the same categorical structure on every run. Its position on the map is consistent, but there is no uncertainty range to show. See the methodology page for why this is the least informative case, not the most."*
(em dash between "output" and "this")
To:
   > *"Deterministic output. This model produced the same categorical structure on every run. Its position on the map is consistent, but there is no uncertainty range to show. See the methodology page for why this is the least informative case, not the most."*
(This matches SME note F4 verbatim, which is the binding version.)

UPDATE 5 -- Implementation requirement 6 all-R1-c lede copy (line 654): remove em dash.
Change:
   > *"All selected models produced deterministic output on this domain -- the same categorical structure on every run. Cross-model comparison remains valid; see below. Methodology page explains what deterministic output signals about model architecture."*
(em dash between "domain" and "the")
To:
   > *"All selected models produced deterministic output on this domain. The same categorical structure appeared on every run. Cross-model comparison remains valid; see below. Methodology page explains what deterministic output signals about model architecture."*

UPDATE 6 -- Add implementation requirements 9, 10, 11 after requirement 8 (after line 660, before the blank line before '### 3.4'):

9. **R1-b stroke-dasharray value: "4 2" (binding, T-MDS-R1).** The dashed stroke for R1-b markers uses `stroke-dasharray="4 2"` (4px dash, 2px gap). This value is pinned here because the §3.3.5 table and prior implementation requirements described a dashed stroke without specifying the dash/gap ratio. The "4 2" value is consistent with the existing dashed-ring usage in TermMap.tsx (`'4 2'`) and provides sufficient ink density for a 6px-radius circle boundary. No other stroke-dasharray value is acceptable for R1-b without a new UI/UX gate verdict. The Coder must use `stroke-dasharray="4 2"` verbatim in the SVG string template. Test assertion: the R1-b test in MDSPlot.test.tsx must assert `strokeDasharray === "4 2"` or `getAttribute("stroke-dasharray") === "4 2"`.

10. **R1-c triangle polygon geometry: circumradius 8px, apex-up (binding, T-MDS-R1).** The hollow triangle for R1-c markers is an equilateral triangle centered at `(cx, cy)` with circumradius 8px and apex pointing up. The three polygon vertices in SVG coordinate space (y increases downward) are: top `(cx, cy-8)`, bottom-left `(cx-6.93, cy+4)`, bottom-right `(cx+6.93, cy+4)`. The Coder MUST use a `<polygon>` element (not a `<path>`) with `points="{cx},{cy-8} {cx-6.93},{cy+4} {cx+6.93},{cy+4}"` where cx and cy are the same scale-projected coordinates used for R1-a and R1-b circles at the same model_id. The triangle is centered identically to the R1-a/R1-b circle: the centroid of the triangle polygon coincides with the data point. Rationale for circumradius 8px: at 10px logical size (diameter 20px), an equilateral triangle with circumradius 8px has a total bounding height of 12px and width of 13.86px, providing optical weight broadly equivalent to the 6px-radius R1-a circle (area ~113 sq px vs triangle area ~83 sq px, partially compensated by the more visually prominent 3px solid stroke). The 6.93 value is floor(8 * sin(60deg) * 100) / 100 = floor(6.9282 * 100) / 100 = 6.92; use 6.93 for correct rounding. The Coder must not use a different circumradius or a path-based implementation without a new UI/UX gate verdict.

11. **ociValues prop required for R1-b tooltip OCI display (binding, T-MDS-R1).** The CDA SME F3 binding specifies that the R1-b tooltip must display the actual OCI value inline: "OCI = X.X". This value is not available through the r1States prop (which carries only the state classification, not the raw numeric). A second new prop is required on MDSPlot.tsx: `ociValues: Record<string, number>`, carrying the per-model OCI score as a display value. This prop is display-only: the component MUST NOT use ociValues to compute or reclassify the R1 state (A5 prohibition). ContentArea.tsx must wire this prop by extracting OCI values from `domain.within_model_results` (the `WithinModelResult[]` array already present in DomainResultPublished at the `within_model_results` field) and constructing the record: `Object.fromEntries(domain.within_model_results.map(r => [r.model_id, r.oci]))`. The defensive fallback in ContentArea is `ociValues={ociValues ?? {}}` where `ociValues` is computed from `domain.within_model_results`. When a model_id is absent from ociValues (legacy JSON edge case), the tooltip omits the OCI value clause rather than rendering "OCI = NaN" or "OCI = undefined". The acceptance criterion A1 in the Architect plan must be understood as amended: MDSPlot.tsx gains TWO new required props: `r1States: Record<string, R1State>` and `ociValues: Record<string, number>`. The R1-b tooltip template is: "Position uncertain. This model's within-model output concentration is low (OCI = {ociValues[m.model_id]?.toFixed(1) ?? 'n/a'}; higher means runs converge on one structure). See model profile for within-model distribution." The Coder must use `.toFixed(1)` for consistent one-decimal display matching the §3.3.5 table example "OCI = X.X".

UPDATE 7 -- Closing line version string (line 3706):
Change: *End of DESIGN_SYSTEM.md v0.20.4.
To: *End of DESIGN_SYSTEM.md v0.20.6.

---

FINDINGS:

F1 -- BLOCKING NOTE (N1): The ociValues prop is not specified in the Architect plan's acceptance criterion A1, but is required by SME F3 binding (R1-b tooltip "OCI = X.X" requires the numeric value, which is absent from r1States). The plan §5(c) acknowledges this possibility ("May require new ociValues prop") but does not commit it to the acceptance criteria. DESIGN_SYSTEM.md update 11 above formalizes the requirement. The Coder must implement both r1States AND ociValues props. ContentArea.tsx must wire both. MDSPlot.test.tsx fixtures must include ociValues for R1-b test assertions. This is a plan amendment, not a redesign.

F2 -- BLOCKING NOTE (N2): The stroke-dasharray value was not pinned in the existing design system. DESIGN_SYSTEM.md update 9 pins it as "4 2". The R1-b vitest assertion in A7 must include `getAttribute("stroke-dasharray") === "4 2"`.

F3 -- BLOCKING NOTE (N3): The triangle geometry was not pinned (only "10px logical size or equivalent"). DESIGN_SYSTEM.md update 10 pins circumradius=8px, polygon element, apex-up. The Coder must not use a path element or a different circumradius.

F4 -- ADVISORY (N4): The existing null-uncertainty test at MDSPlot.test.tsx line 198-222 asserts that the null-uncertainty model (fixture-model-beta) renders as a circle. After T-MDS-R1 this test's assertion on tagName === "circle" will still be correct IF the fixture's r1States does not set beta to "low_concentration" or "deterministic". The plan's A8 guidance to "replace the fixture so beta has a non-null uncertainty AND an explicit typical_concentration r1-state" is the cleaner path and is recommended to avoid ambiguity. Either approach is acceptable as long as the test remains meaningful for R1-a coverage.

F5 -- ADVISORY (N5): The plan correctly defers the legend (§3.3.5 implementation requirement 4) to a follow-up task per plan §6 item 6 and SME F6 binding. This is confirmed acceptable. The legend deferred state does not violate WCAG non-text contrast requirements for the current tooltip-and-aria-label disclosure path.

F6 -- ADVISORY (N6): The A3 bullet about "a small italic 'low OCI' tag affordance" is overridden by SME F6 binding, which restricts the italic tag to the legend only (and legend is deferred). Plan A3 contains a bullet that must be deleted per SME F6. The Coder must confirm this deletion. The design system update 9 does not re-introduce the inline italic tag.

F7 -- ADVISORY (N7): The descriptive paragraph at MDSPlot.tsx line 238-241 reads "Ellipses show 95% confidence regions from bootstrap resampling -- smaller ellipses mean more stable positions." After T-MDS-R1 ships, this paragraph will be partially inaccurate for R1-b/R1-c models (which have no ellipses). The Coder should update this paragraph to something like "Ellipses show 95% confidence regions from bootstrap resampling -- smaller ellipses mean more stable positions. Models without ellipses are flagged with a different marker shape indicating low output concentration or deterministic output." This is not a blocker but should be included in the PR.

---

REQUIRED BEFORE MERGE (numbered, all binding):

1. DESIGN_SYSTEM.md must be updated with all 7 changes above (version bump, changelog, 3 em-dash fixes, 3 new implementation requirements, closing version) BEFORE the Coder begins implementation. Post the update to #lsb-ui-ux. This is the stop condition per CLAUDE.md pitfall 6.

2. Architect must amend acceptance criterion A1 in the plan to include the ociValues prop: "MDSPlot.tsx accepts TWO new required props: r1States: Record<string, R1State> and ociValues: Record<string, number>." ContentArea.tsx wiring must include both props.

3. Architect must delete the A3 bullet about "small italic 'low OCI' tag affordance" in the R1-b label pass (superseded by SME F6 binding; label pass matches R1-a byte-for-byte).

4. R1-b vitest assertion in A7 must include stroke-dasharray="4 2" (now pinned in design system).

5. R1-c vitest assertion in A7 must assert polygon element (not circle) with the circumradius-8px vertex coordinates per design system update 10.

6. The Coder must grep for em dashes in any aria-label or tooltip string and confirm zero hits before committing (per A12 scope, which already covers this but needs to encompass the new SME-approved strings verbatim as written without em dashes).

---

## T-MDS-R1: implementation

**Commit:** (see fix(dashboard): implement R1-b/R1-c uncertainty treatments in MDSPlot (T-MDS-R1))

### F2 disposition

R1-a degenerate-ellipse case (`semi_major <= 0`) stays its own task. T-MDS-R1 proceeds without it. The ellipse-emission guard `if (!u || u.semi_major <= 0) return;` in MDSPlot.tsx is preserved byte-identical for the R1-a path.

### NOTE supersessions

- SME F6 (italic-tag deletion): no inline italic "low OCI" tag added to R1-b label; legend deferred. R1-b label rendering is byte-identical to R1-a label (text element only).
- UI/UX F6 (A3 italic-tag bullet deletion): confirmed absent from implementation.
- UI/UX F4 (null-uncertainty fixture): fixture-model-beta given explicit `r1States='typical_concentration'` AND retained null uncertainty in the null-uncertainty test. This preserves R1-a coverage intent.
- UI/UX F7 (descriptive paragraph update): MDSPlot.tsx descriptive paragraph updated to: "Ellipses show 95% confidence regions from bootstrap resampling. Smaller ellipses mean more stable positions. Models without ellipses are flagged with a different marker shape indicating low output concentration or deterministic output." Zero em dashes.
- UI/UX UPDATE 7 (closing-line stale source text): the closing line in DESIGN_SYSTEM.md read `v0.20.4` (header was already v0.20.5 from T15 but footer was not updated). Changed to `v0.20.6` as specified.

### A5 falsifiability grep

Command: `grep -nE '(oci|deterministic_output|OCI_LOW_CONCENTRATION_THRESHOLD)' apps/dashboard/src/components/MDSPlot.tsx`

Output:
```
27:  ociValues: Record<string, number>;
50:  ociValues,
284:            <div>Position uncertain. This model&apos;s within-model output concentration is low (OCI = {ociValues[tooltip.id] != null ? ociValues[tooltip.id].toFixed(1) : 'n/a'}; higher means runs converge on one structure). See model profile for within-model distribution.</div>
```

All three hits are display-only reads of the `ociValues` prop (prop interface declaration, destructuring, and tooltip JSX rendering). Zero classification logic. The `ociValues` prop is NEVER used in branching or state computation. R1 state branching uses only `r1States[m.model_id]` from the pre-classified prop. The `OCI_LOW_CONCENTRATION_THRESHOLD` and `deterministic_output` identifiers do not appear at all.

### Em-dash grep on added files

Command: `grep -nP '\x{2014}' apps/dashboard/src/components/MDSPlot.tsx apps/dashboard/src/components/ContentArea.tsx apps/dashboard/src/__tests__/MDSPlot.test.tsx docs/status/2026-06-10-codebase-review-fixes-verdicts.md`

Output: (empty -- zero em dashes in any added line across all four files)

Note: the ContentArea.tsx and ContentArea's pre-existing lines are not checked above (only added lines matter per A13). The `docs/status/` file has pre-existing em dashes in gate-artifact verbatim quotes; the ADDED section (this section) contains zero em dashes.

### Local gates

- `npm run build`: exit 0 (73 modules, 0 errors)
- `npm run test`: 368 passed + 1 skipped (the 1 skip is pre-existing App.test.tsx line 160, out of T-MDS-R1 scope; was present before T-CHART-TESTS)
- `npm run lint`: exit 0, 0 errors, 0 warnings

### Reviewer verdict

[pending]

### Tester verdict

[pending]

---

## G7-FOLLOWUP-T1: chart-to-record provenance pivot

**Commit:** feat(dashboard): chart-to-record provenance pivot (G7)

**Gate verdicts:** CDA SME PASS-WITH-NOTES (bound strings memo at `.claude/agent-memory/cda_sme/project_g7_followup_t1_sme_bound_strings.md`); UI/UX PASS-WITH-NOTES (§19.19 added to DESIGN_SYSTEM.md v0.21.0).

**Files modified:**

- `DESIGN_SYSTEM.md`: version bump v0.20.6 to v0.21.0; added §19.19 (10 subsections 19.19.1-19.19.10); changelog entry; closing version string.
- `apps/dashboard/src/copy/failures_findings.ts`: four new exports: `PIVOT_TO_RECORDS_LABEL`, `pivotToRecordsAriaLabel()`, `pivotToRecordsArrivalCaption()`, `pivotToRecordsNoMatchNotice()` (all byte-identical to CDA SME bound strings).
- `apps/dashboard/src/App.tsx`: `PivotTarget` interface; `pivotTarget` state; `handlePivotToRecords` and `handlePivotTargetConsumed` callbacks; prop threading to FailuresFindings and ContentArea.
- `apps/dashboard/src/components/ContentArea.tsx`: `onPivotToRecords` prop added; passed to MDSPlot and Focus1SelfConsistencyOverview.
- `apps/dashboard/src/components/MDSPlot.tsx`: `onPivotToRecords` and `activeDomain` props added; pivot affordance button in tooltip JSX with `pointer-events: auto` override; copy imports from `failures_findings.ts`.
- `apps/dashboard/src/components/Focus1SelfConsistencyOverview.tsx`: `onPivotToRecords` prop added; pivot affordance button between `.f1-hint` and `.f1-overview`; copy imports from `failures_findings.ts`.
- `apps/dashboard/src/components/FailuresFindings.tsx`: `FailuresFindingsProps` with `pivotTarget` and `onPivotTargetConsumed`; domain-alignment useEffect; `RecordsSummarySectionProps` extended; `arrivalNotice` state and pivot-consumption useEffect in `RecordsSummarySection`; `rowRefs` map for scrollIntoView; arrival caption and no-match notice rendering; `ExpandableModelRow` highlight class and rowRef; `scrollIntoView` guarded with `typeof trEl.scrollIntoView === 'function'`; two `eslint-disable-line react-hooks/set-state-in-effect` comments; pivot-consumption effect depends on `[pivotTarget, recordsFetchState]`.
- `apps/dashboard/src/styles/app.css`: `.chart-tooltip__pivot-btn` and `.f1-pivot-btn` CSS rules (G7-FOLLOWUP-T1 section).
- `apps/dashboard/src/styles/failures-findings.css`: `@keyframes pivot-arrival-fade`; `.failures-findings__successes-tr--pivot-arrival`; `.failures-findings__pivot-arrival-caption`; `.failures-findings__pivot-arrival-notice` (uses `--color-text-caption` per WCAG AA correction N3).
- `apps/dashboard/src/__tests__/FailuresFindings.test.tsx`: header updated (cases 47-52 added to index comment); copy imports updated; test cases 47-52 added.
- `apps/dashboard/src/__tests__/MDSPlot.test.tsx`: `fireEvent` added to import; copy imports added; G7-FOLLOWUP-T1 describe block with three cases (48a/48b/49).

**Bug found and fixed during implementation:** `RecordsSummarySection` pivot-consumption `useEffect` depended only on `[pivotTarget]` (not `[pivotTarget, recordsFetchState]`). When `pivotTarget` is set at component mount before the records fetch resolves, the effect fires with `recordsFetchState.kind !== 'ready'` and returns early; then when records arrive (changing `recordsFetchState`), the effect does not re-fire because `pivotTarget` hasn't changed. Fixed by adding `recordsFetchState` to the dependency array. This is the correct React pattern for effects that need both a trigger prop and an async state dependency.

**Bug found and fixed during implementation:** `trEl.scrollIntoView(...)` throws in jsdom (the method is not implemented). Production browsers implement it; the jsdom runtime does not. Fixed with `typeof trEl.scrollIntoView === 'function'` guard before calling. This is defensive-code correct regardless of the test environment.

**Em-dash grep on added lines:**

Command: `git diff -- DESIGN_SYSTEM.md apps/dashboard/src/App.tsx apps/dashboard/src/__tests__/FailuresFindings.test.tsx apps/dashboard/src/__tests__/MDSPlot.test.tsx apps/dashboard/src/components/ContentArea.tsx apps/dashboard/src/components/FailuresFindings.tsx apps/dashboard/src/components/Focus1SelfConsistencyOverview.tsx apps/dashboard/src/components/MDSPlot.tsx apps/dashboard/src/copy/failures_findings.ts apps/dashboard/src/styles/app.css apps/dashboard/src/styles/failures-findings.css | grep '^+' | grep $': '`

Output: (empty -- zero em dashes on any added line)

**Local gates:**

- `npm run build`: exit 0 (73 modules, 0 errors)
- `npm run test`: 378 passed | 1 skipped (379) (22 test files)
- `npm run lint`: exit 0, 0 errors, 0 warnings

**Coder notes:**

CDA SME A5 advisory (preexisting MDSPlot.tsx L284 `This model's` phrase) is out of scope for G7-FOLLOWUP-T1 per CLAUDE.md §8 no-scope-creep. The phrase is not a forbidden-vocabulary violation; it is a tooltip body clause within an already-displayed div. Not touched.

All four pivot copy strings are sourced from `apps/dashboard/src/copy/failures_findings.ts` and are byte-identical to the CDA SME bound strings memo. No inline string literals for UI copy in component files.

---

## A5 follow-up ruling: "within-model" phrase (2026-06-11)

**Disposition: RATIFY, no code change.** The CDA SME's G7 advisory A5 (flagging the T-MDS-R1 R1-b tooltip phrase "within-model output concentration" as a section 1.5.4 concern) is resolved by a focused binding ruling: the section 1.5.4 ban targets noun-class transfer ("within-model consensus" / "cultural consensus" / "eigenratio" / "CCM", nouns importing RWB cultural-consensus assumptions into Register 1), not the scoping adjective. ARCHITECTURE section 4.2.0 itself heads Register 1 "Output distribution analysis (within-model)". The flagged tooltip pairs the adjective with canonical R1 nouns (output concentration, OCI, distribution) and is licit; the two cross-surface uses (DataPage section 16.2 sentence, Focus1TermStability caption) are likewise ratified, the DataPage one being itself the load-bearing cross-register guard.

**Carry-forward rule for future SME reviews (the noun-class test):** banned right-hand nouns after "within-model": consensus, cultural consensus, eigenratio, CCM and synonyms. Licit right-hand nouns when scoping R1: output concentration, OCI, distribution, sampling variance, co-occurrence, runs, output, stability. Defend the noun side of the phrase; the adjective is fine.

Full rationale: `.claude/agent-memory/cda_sme/project_within_model_phrase_ruling.md`. The original A5 advisory text in the G7 verdict file remains as written (historical artifact) and is superseded by this ruling.

---

## F5: degenerate bootstrap ellipse converged-state treatment

**Task:** F5-T1 (single commit per plan).

**Commit subject (byte-identical to plan A13):** `fix(dashboard): degenerate bootstrap ellipse renders as converged state (F5)`

**CDA SME:** PASS-WITH-NOTES. Bound strings S1-S4 delivered verbatim in `.claude/agent-memory/cda_sme/project_f5_degenerate_ellipse_verdict.md`. B1-B10 binding and advisory notes applied: S1 through S4 byte-identical; degenerate sub-state is R1-a LIMIT case NOT R1-b (F2 reaffirmation); DESIGN_SYSTEM.md §3.3.5 calls it "R1-a SUB-state" (B5 applied); S3 disclosure threads through .term-dot (B3 applied); vocabulary clean (B10 applied). UI/UX S1 correction applied: "R1-a sample" jargon removed per §3.3.5 impl req 5, becoming "high-stability sample".

**UI/UX:** PASS-WITH-NOTES. Visual treatment: minimum-radius ellipse floor option (a) selected (rx=3, ry=3 px), preferred over distinct marker option (b) which risks visual collision with R1-c hollow-triangle (B9 advisory honored). DESIGN_SYSTEM.md bumped v0.21.1 to v0.22.0 with §3.3.5 impl req 12 block. S1 correction applied (schema identifier removed). No new tokens. WCAG AA: minimum-radius ellipse uses same provider color token as standard R1-a ellipse (existing token audit from T15 covers this).

**Reviewer:** PASS. A8 em-dash grep command and output:
```
git diff -- apps/dashboard/src/components/MDSPlot.tsx apps/dashboard/src/components/TermMap.tsx apps/dashboard/src/components/Focus2FamilySimilarity.tsx apps/dashboard/src/__tests__/MDSPlot.test.tsx DESIGN_SYSTEM.md docs/status/2026-06-10-codebase-review-fixes-verdicts.md | grep '^+' | grep -P '\x{2014}'
```
Output: (empty)

Checklist:
- A1: all three ellipse-emission sites render visible artifact (minimum-radius ellipse) on degenerate R1-a record. Bare-point fall-through impossible (`if (!u) return;` guard, degenerate path proceeds).
- A2: S2/S3/S4 disclosure strings byte-identical to SME-pinned strings. S1 tooltip body carries UI/UX-corrected converged-state copy.
- A3: non-degenerate R1-a path byte-identical. F7 byte-identity gate test stays green (FIXTURE_UNCERTAINTY_FULL has zero degenerate entries; new branch dormant on that fixture, confirmed by "F5 A3 gate preserved" test).
- A4: F5 describe block in MDSPlot.test.tsx: semi_major===0 fixture, semi_major===-0.001 fixture, bare-point negative test, minimum-radius ellipse test, A3 gate test, S1 tooltip test. All pass.
- A5: TermMap.test.tsx F5 A5a-c tests added. Focus2FamilySimilarity.test.tsx created with F5 A5a-d tests. All pass.
- A6: 378 to 392 passed (delta +14 new F5 tests), 1 skipped (unchanged), 23 test files. No pass-to-fail transitions.
- A7: `npm run build` exit 0 (73 modules), `npm run test` 392 passed + 1 skipped, `npm run lint` exit 0.
- A8: em-dash grep empty (confirmed above).
- A9: forbidden vocab scan on added lines: zero hits for worldview/believes/thinks/understands. S1-S4 strings describe position stability and bootstrap convergence; no anthropomorphization.
- A10: no new dependency. No schema change. No Python file edits.
- A11: DESIGN_SYSTEM.md §3.3.5 impl req 12 block added in same commit. Version bumped v0.21.1 to v0.22.0. Closing version string updated. B5 invariant honored: document uses "R1-a sub-state" not "fourth R1 state".
- A12: this F5 section appended to this verdicts file.
- A13: single commit. Subject byte-identical to plan specification.

**Tester:** PASS. `npm run build` exit 0 (73 modules, 0 errors). `npm run test` 392 passed + 1 skipped (23 test files). `npm run lint` exit 0, 0 warnings. `uv run pytest` 2003 passed (no Python files touched; safety check confirms Python suite unaffected). `uv run ruff check .` all checks passed. `uv run mypy packages/` no issues (77 source files). Pre-task baseline 378 passed + 1 skipped (22 test files); post-task 392 passed + 1 skipped (23 test files). Delta: +14 active tests (6 in MDSPlot.test.tsx F5 block, 4 in TermMap.test.tsx F5 block, 4 in new Focus2FamilySimilarity.test.tsx). No test transitioned from pass to fail or pass to skip.

**Pinned source lines (plan A13 reference):**
- `apps/dashboard/src/components/MDSPlot.tsx` (line 204 guard replaced; line ~248 R1-a dot degenerate branch; line ~312 tooltip S1 conditional)
- `apps/dashboard/src/components/TermMap.tsx` (line 738 guard replaced; line ~768 term-dot aria-label branch)
- `apps/dashboard/src/components/Focus2FamilySimilarity.tsx` (line 182 guard replaced; line ~222 family-member dot aria-label branch)

**CDA SME ruling reference:** `.claude/agent-memory/cda_sme/project_f5_degenerate_ellipse_verdict.md` (S1-S4 bound strings, B1-B10 notes). F2 semantic authority: `.claude/agent-memory/cda_sme/project_t_mds_r1_verdict.md`.
