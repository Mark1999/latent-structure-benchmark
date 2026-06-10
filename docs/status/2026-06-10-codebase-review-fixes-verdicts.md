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

## Task 4: delete dead component Timeline.tsx

Status: queued.
