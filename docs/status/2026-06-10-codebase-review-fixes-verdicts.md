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
- **Reviewer:** PASS. All nine listed components (plus the mandatory-note addition Focus1SelfConsistencyOverview) have zero `#[0-9a-fA-F]{3,6}` on added lines outside authorized docblock citations. Every `var(--token)` reference resolves to a token in `tokens.css`. New `tokens-defined.test.ts` passes. R10 invariants (SimilarityHeatmap.tsx lines 221-227 dashStroke, Focus1RunDistribution simToTextColor) updated to use `--color-background` and `--color-heatmap-cell-text-dark` (byte-identical logic). No em dashes. No forbidden vocabulary. No spend-gate tokens. Conventional commit under 72 chars. Body references verdicts file. Test count 148 to 149+.
