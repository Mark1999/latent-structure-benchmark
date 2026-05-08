# Reviewer Verdict — SC-T4: Add no-spend-gate-check regression prevention

**Date:** 2026-05-08
**Reviewer:** LSB Reviewer agent (Sonnet 4.6)
**Commit reviewed:** `3668dd9`
**Plan reference:** `docs/status/2026-05-08-spend-cap-removal-architect-plan.md` §4 SC-T4, §6 SC-T4 items A–G

---

## REVIEWER VERDICT: PASS

All nine standard checks pass. All seven SC-T4-specific items (A–G) pass. Three Coder-reported deviations are assessed below and all are acceptable.

---

## Standard 9-check scorecard

| Check | Result |
|---|---|
| Check 1 — No LLM imports in `cdb_analyze/` | PASS |
| Check 2 — Append-only `informants.jsonl` | N/A |
| Check 3 — No secrets | PASS |
| Check 4 — Forbidden vocabulary | PASS |
| Check 5 — Schema + DATA_DICTIONARY | N/A |
| Check 6 — New deps sign-off | PASS |
| Check 7 — Prompt versioning | N/A |
| Check 8 — Uncertainty in viz | N/A |
| Check 9 — Prerequisite verdicts | PASS |

---

## Detailed check results

**Check 1 — No LLM imports in `cdb_analyze/`:**
`grep -r "import anthropic|import openai|from anthropic|from openai|InferenceClient|google.generativeai" packages/cdb_analyze/` returned only comment lines in `__init__.py`. No actual import statements. PASS.

**Check 2 — Append-only `informants.jsonl`:**
`git show 3668dd9 --name-only` does not include `data/raw/informants.jsonl`. N/A.

**Check 3 — No secrets:**
The workflow file `.github/workflows/ci.yml` contains no API keys, webhook URLs, tokens, or credential patterns. The file references `${{ secrets.GITHUB_TOKEN }}` in the gitleaks job — this is the standard GitHub-provided token reference, not a committed credential. PASS.

**Check 4 — Forbidden vocabulary:**
Scanned all changed files (`ci.yml`, `ARCHITECTURE.md`, `CLAUDE.md`, `SECURITY_AND_HARDENING.md`, `scripts/run_decline_backfill.py`, `tests/test_run_decline_backfill.py`) and the commit message for: `believes`, `thinks`, `worldview`, `recognizes`, `interprets`, `perceives`, `publishable`, `within-model consensus`, `within-model cultural consensus`, `within-model eigenratio`, `within-model CCM`. No matches found. PASS.

**Check 5 — Schema + DATA_DICTIONARY:**
No `cdb_core/schemas.py` changes. N/A.

**Check 6 — New deps sign-off:**
`git diff 9471972..3668dd9 -- pyproject.toml uv.lock` returned empty. No Python deps added. The GitHub Actions steps use `actions/checkout@v4` (pre-existing) and `astral-sh/setup-uv@v5` (pre-existing); these are CI infrastructure deps already present, not new additions. PASS.

**Check 7 — Prompt versioning:**
No prompt template changes. N/A.

**Check 8 — Uncertainty in viz:**
No frontend work. N/A.

**Check 9 — Prerequisite verdicts:**
This is not a frontend PR (no UI/UX gate required). Not a methodology PR (no CDA SME gate required). Prerequisite chain: SC-T1 Reviewer PASS at `docs/status/2026-05-08-spend-cap-removal-sc-t1-reviewer-verdict.md`, SC-T2 Reviewer PASS at `docs/status/2026-05-08-spend-cap-removal-sc-t2-reviewer-verdict.md`, SC-T3 Reviewer PASS-WITH-NOTES at `docs/status/2026-05-08-spend-cap-removal-sc-t3-reviewer-verdict.md` with Note N1 explicitly marked "No corrective action required before merge." All prior verdicts present and notes resolved. PASS.

---

## SC-T4-specific items (plan §6, items A–G)

**Item A — Workflow exists post-commit, diff is additive:**
`.github/workflows/ci.yml` pre-existed (created in P0-T6 at commit `1446998`). The diff is purely additive: 24 lines added, 0 removed. The `no-spend-gate-check` step is inserted immediately after the `actions/checkout@v4` step (with `fetch-depth: 0` also added to that checkout step, which is a necessary addition since `git grep` requires full history). PASS.

**Item B — Pattern matches verbatim:**
Workflow `FORBIDDEN` string: `CDB_MAX_SPEND_USD|MAX_SPEND_USD|DEFAULT_MAX_SPEND|spend_cap|cost_cap|cost-cap-usd|--max-spend`. This is byte-identical to plan §1.3/§3.5. PASS.

**Item C — Exclusion list matches §1.3 verbatim:**
Workflow exclusions: `docs/status/`, `docs/INCIDENTS/`, `docs/3rdpartyreviews/`, `docs/proposals/`, `docs/PROMPT_EVOLUTION_LOG.md`, `.github/workflows/ci.yml`. Plan §1.3 lists the first five. The sixth (the workflow itself) is called for explicitly in §3.5 pseudocode. The Coder also added a `grep -v 'noqa: spend-gate-check'` filter pipeline — this is an extension of the exclusion mechanism, not a replacement. Both the path-exclusion list and the noqa filter are present. PASS.

**Item D — Reviewer runs grep locally, reports zero hits:**
Command run: `git grep -nE 'CDB_MAX_SPEND_USD|MAX_SPEND_USD|DEFAULT_MAX_SPEND|spend_cap|cost_cap|cost-cap-usd|--max-spend' -- ':(exclude)docs/status/' ':(exclude)docs/INCIDENTS/' ':(exclude)docs/3rdpartyreviews/' ':(exclude)docs/proposals/' ':(exclude)docs/PROMPT_EVOLUTION_LOG.md' ':(exclude).github/workflows/ci.yml' | grep -v 'noqa: spend-gate-check'`

Result: zero hits (empty output). The post-commit tree is clean. PASS.

**Item E — Error message references three required documents:**
Workflow line: `echo "See ARCHITECTURE.md §6.2, CLAUDE.md rule 14, SECURITY_AND_HARDENING.md R13."` — all three required references present. PASS.

**Item F — Smoke test:**
Piping a known-match through the noqa filter: `echo "scripts/test_foo.py:5:    CDB_MAX_SPEND_USD = 100" | grep -v 'noqa: spend-gate-check'` — output is the match line, confirming the grep step would catch a genuine regression. Additionally confirmed that a line with `# noqa: spend-gate-check` suffix would be suppressed by the filter. PASS.

**Item G — CI workflow YAML syntactically valid:**
`python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))" && echo "yaml: OK"` — output: `yaml: OK`. PASS.

---

## Deviation assessments

**Deviation 1 — `<!-- noqa: spend-gate-check -->` markers added to ARCHITECTURE.md, CLAUDE.md, SECURITY_AND_HARDENING.md:**
Defensible. The principle texts in these binding docs must name the forbidden tokens (otherwise readers cannot know what the enforcement check targets). The noqa HTML-comment markers allow the grep to distinguish principle-text occurrences from active enforcement code. Plan §1.3 did not list these docs as path exclusions because the Architect expected the Coder to rename `spend_cap` → `legacy_dollar_threshold` (option (a), SC-T2) to eliminate the only Python-file conflict. The binding docs' principle-text lines were an unaddressed gap. The Coder's pragmatic extension is consistent with the intent: exclude lines that define the rule from the grep that enforces the rule. The Reviewer concurs with the Coder's self-assessment: defensible.

**Deviation 2 — Ruff emits warnings about `# noqa: spend-gate-check`:**
Acceptable. `spend-gate-check` is a project-specific marker, not a ruff/flake8 code. Ruff's warning is harmless and the Coder correctly noted it. `uv run ruff check .` returns `All checks passed!` (warnings do not count as errors). PASS.

**Deviation 3 — Comment consolidation for line-length compliance:**
Acceptable. The multi-line backward-compat comments in `scripts/run_decline_backfill.py` were condensed to single lines to satisfy the 100-character ruff limit. The condensed comments still convey the same meaning. The shim parameters (`spend_cap`, `cost_per_call`) are preserved intact per plan §10. PASS.

---

## Build health

- `uv run pytest`: 1204 passed, 26313 warnings, 0 failures
- `uv run ruff check .`: All checks passed
- `uv run mypy packages/ --ignore-missing-imports`: Success (55 source files, 0 issues)

---

## Commit message hygiene

Commit message follows Conventional Commits format (`ci(SC-T4):`). First line is under 72 characters. Body references plan path and task ID. Includes `Co-Authored-By` attribution. PASS.

---

## Summary

All nine standard checks pass. All seven SC-T4-specific items pass. Three Coder deviations are all acceptable. The spend-gate CI regression check is correctly implemented, syntactically valid, produces zero hits on the post-commit tree, and would catch genuine regressions. The Tester may proceed.
