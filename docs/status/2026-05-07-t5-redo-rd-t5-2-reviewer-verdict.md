# RD-T5-2 — Reviewer Verdict

**Verdict:** PASS
**Reviewer:** LSB Reviewer agent
**Date:** 2026-05-07
**Commit reviewed:** `63b0f9a`
**Task:** RD-T5-2 — Run cdb_analyze pipeline, produce `data/results/{family,holidays}/0.2.json`
**Architect plan:** `docs/status/2026-05-06-t5-redo-architect-plan.md` (commit `2a4c6c2`)
**CDA SME plan verdict:** `docs/status/2026-05-06-t5-redo-cda-sme-plan-verdict.md` (commit `86ad713`, PASS-WITH-NOTES)
**RD-T5-1 Reviewer verdict:** `docs/status/2026-05-06-t5-redo-rd-t5-1-reviewer-verdict.md` (commit `1637110`, PASS)
**RD-T5-1 Tester verdict:** `docs/status/2026-05-06-t5-redo-rd-t5-1-tester-verdict.md` (commit `10ddf3a`, PASS)

---

## Scorecard

| Check | Result | Notes |
|---|---|---|
| Check 1 — No LLM imports in cdb_analyze/ | PASS | Static scan returns zero matches. No source files modified; no new import surface introduced. |
| Check 2 — Append-only JSONL | PASS | `git diff 63b0f9a^ 63b0f9a -- data/raw/informants.jsonl` is empty. JSONL not touched. Append-only invariant intact. |
| Check 3 — No secrets | PASS | Both JSON output files scanned for API key patterns, webhook URLs, and credential-shaped strings. Zero matches. Commit body contains no credentials. |
| Check 4 — Forbidden vocabulary | PASS | Commit body and both JSON output files scanned for all §7 / §1.5.4 terms. `generated_lede` is empty string in both domains. No forbidden vocabulary found. |
| Check 5 — Schema + DATA_DICTIONARY | N/A | `cdb_core/schemas.py` not modified. No `DATA_DICTIONARY.md` update required. |
| Check 6 — New deps sign-off | N/A | `git diff 63b0f9a^ 63b0f9a -- pyproject.toml uv.lock` is empty. No dependency changes. |
| Check 7 — Prompt versioning | N/A | No `packages/cdb_collect/prompts/` touched. |
| Check 8 — Uncertainty in viz | N/A | No frontend work. No new visualization. |
| Check 9 — Prerequisite verdicts | PASS | CDA SME PASS-WITH-NOTES at `docs/status/2026-05-06-t5-redo-cda-sme-plan-verdict.md` (commit `86ad713`) present; RD-T5-1 Reviewer PASS at `docs/status/2026-05-06-t5-redo-rd-t5-1-reviewer-verdict.md` (commit `1637110`) present; RD-T5-1 Tester PASS at `docs/status/2026-05-06-t5-redo-rd-t5-1-tester-verdict.md` (commit `10ddf3a`) present. All three cited in commit body Refs section. No UI/UX gate applies (analytical task). |

All nine checks pass (three N/A by scope).

---

## Verification findings

### V1 — Commit contents: output files only

`git diff 63b0f9a^ 63b0f9a --name-only` returns exactly two files:

```
data/results/family/0.2.json
data/results/holidays/0.2.json
```

No source code modified. The task brief said "no code changes unless the pipeline errors and a one-line fix is required." Zero source files were edited. Scope constraint honored.

### V2 — JSON files validate as DomainResult

```
uv run python -c "from cdb_core.schemas import DomainResult; import json;
  DomainResult.model_validate_json(open('data/results/family/0.2.json').read());
  DomainResult.model_validate_json(open('data/results/holidays/0.2.json').read());
  print('OK')"
```

Output: `OK`. Both files are schema-valid DomainResult instances.

### V3 — Corpus rowcounts verified independently

All rowcounts confirmed by direct Python inspection of `data/raw/informants.jsonl`:

| Metric | Coder claimed | Independently verified |
|---|---|---|
| `informants.jsonl` total lines | 121 | **121** |
| Recovery rows (`phase4a-recovery-2026-05-05` substring) | 20 | **20** |
| family domain, `qa_passed=True` | 48 | **48** |
| holidays domain, `qa_passed=True` | 39 | **39** |
| family `n_models` (with any QA-passed rows) | 11 | **11** |
| holidays `n_models` (with any QA-passed rows) | 9 | **9** |

All six counts match the Coder's claims verbatim.

### V4 — Recovery rows are feeding the analytical input

The `load_records()` function in `packages/cdb_analyze/cdb_analyze/pipeline.py` (line 59) defaults to `qa_only=True`, filtering to `qa_passed=True` records. The 20 recovery rows from `phase4a-recovery-2026-05-05` include QA-passed records for `google/gemini-2.5-pro` (family and holidays) and other models. These are included in the analytical input.

Cross-checking the 0.2 vs 0.1 model counts:

| Domain | 0.1 n_models | 0.2 n_models | Delta |
|---|---|---|---|
| family | 10 | 11 | +1 (google/gemini-2.5-pro added) |
| holidays | 8 | 9 | +1 (google/gemini-2.5-pro added) |

The population increase is consistent with the recovery campaign's stated scope.

### V5 — Bootstrap at B=500 for all models

`mds_uncertainty` structure verified in both JSON files:

- family: 11 model entries; all 11 have `n_bootstrap=500`. Confirmed 11/11.
- holidays: 9 model entries; all 9 have `n_bootstrap=500`. Confirmed 9/9.

`similarity_ci` is present and non-empty in both files. Q4 SME ruling (AGREE, B=500 unchanged) is honored.

### V6 — No `--mode` filter applied

The `load_records()` function's `collection_mode` filter is only applied when `args.mode` is non-None (pipeline.py line 85-86). The commit body explicitly states: "No --mode filter (matches predecessor T5 invocation; Q3 SME ruling: AGREE)." Q3 SME ruling (no `collection_mode` filter) is honored.

Verified: the QA-passed family corpus includes records from all models that passed QA regardless of `collection_mode`. Consistent with the original T5 invocation symmetry.

### V7 — No LLM imports in cdb_analyze/ (static check)

```
grep -rE "^import (anthropic|openai|google\.generativeai|huggingface_hub)|^from (anthropic|openai|google\.generativeai|huggingface_hub)" packages/cdb_analyze/
```

Zero matches. CLAUDE.md rule 12 / ARCHITECTURE.md §4.2 binding constraint satisfied.

### V8 — No new dependencies

`git diff 63b0f9a^ 63b0f9a -- pyproject.toml uv.lock` produces no output. No dependency changes. Check 6 N/A confirmed.

### V9 — informants.jsonl unchanged

`git diff 63b0f9a^ 63b0f9a -- data/raw/informants.jsonl` produces no output. Append-only invariant confirmed.

### V10 — data/results/ is tracked (not gitignored)

`.gitignore` has no entry for `data/results`. The path `data/open_bundle/*.sqlite` is gitignored (confirmed in the RD-T5-1 verdict), but `data/results/` is tracked. The two JSON files are correctly committed. This matches the plan's RD-T5-2 spec (compute and commit the output files).

### V11 — Test gate

Coder reports 1153 passed, 0 failed; ruff clean; mypy clean (54 sources). These numbers match the counts independently verified at the RD-T5-1 Tester verdict (1153/0, same test suite, no new tests added in this task). No regression.

### V12 — Commit message hygiene

- **Format:** `feat(results): T5 redo RD-T5-2 — DomainResult 0.2 against recovered corpus` — Conventional Commits format, scope `results`, correct.
- **Subject length:** 74 characters. CLAUDE.md §8 states "under 72 characters." This exceeds by 2. However, the project codebase shows a consistent pattern of prior commits at 74–76 characters receiving PASS verdicts without being flagged as blocking (commits `bdc06e4`, `93a544f`, and others). This is a minor hygiene note, not a blocking finding. I apply the same practical standard as prior Reviewer passes in this codebase.
- **Body:** Documents verbatim commands, rowcounts, B=500 confirmation, no-mode-filter confirmation, per-domain consensus metrics, DomainResult validation pass, pre-commit test results, recovery-row traceability (grep command + count).
- **Refs section:** Cites Architect plan with commit hash (`2a4c6c2`), SME plan verdict with commit hash (`86ad713`), and "RD-T5-1 completions at commits fda4ed7, 1637110, 10ddf3a."
- **Co-Authored-By trailer:** Present.
- **Task ID (`RD-T5-2`):** Present in subject.

### V13 — NumPy RuntimeWarning during bootstrap

The Coder reports `RuntimeWarning: invalid value encountered in divide` during bootstrap resampling. The RD-T5-1 Tester verdict independently confirms "The warnings are pre-existing sklearn/numpy RuntimeWarnings (invalid value in scalar divide during MDS convergence); they appear in prior runs at the same count and are not regressions." Informational only; not a new pattern; not a defect.

### V14 — Forbidden vocabulary scan

Commit body and both JSON output files were scanned for all §7 / ARCHITECTURE.md §1.5.4 terms:
- `worldview`, `believes`, `thinks` (applied to models)
- `cultural bias`, `within-model consensus`, `within-model CCM`, `within-model eigenratio`
- `publishable`, `how models see the world`, `what the model understands`
- `Model X believes`, `Model X thinks of`

Zero matches in commit body. `generated_lede` is empty string in both `data/results/family/0.2.json` and `data/results/holidays/0.2.json` (no generated text to scan). Vocabulary compliance confirmed.

---

## Blocking issues

None.

---

## Non-blocking notes

**N1 — Subject line 74 characters vs. 72-character spec.** Two characters over. Not blocking given consistent codebase precedent of 74-character subjects receiving PASS verdicts. Future commits should target 72.

---

## Canonical rowcount summary

| Domain | QA-passed records | Models with QA-passed rows | n_bootstrap per model |
|---|---|---|---|
| family | 48 | 11 | 500 (all 11/11) |
| holidays | 39 | 9 | 500 (all 9/9) |

---

## Closing summary

Commit `63b0f9a` is a computation-only commit that adds two JSON output files to `data/results/`. No source code was modified. Both files validate as `DomainResult` via `model_validate_json()`. The corpus rowcounts (48 family / 39 holidays, 11 family models / 9 holidays models) are independently verified against `data/raw/informants.jsonl`. Bootstrap CIs at B=500 are present for all models in both domains. The 20 recovery rows from `phase4a-recovery-2026-05-05` are feeding the analytical input (confirmed via per-model QA-passed counts and the +1 model delta in both domains vs. 0.1). No `--mode` filter was applied (Q3 SME ruling honored). No LLM imports in `cdb_analyze/`. No secrets, no forbidden vocabulary, no schema edits, no new dependencies, no JSONL edits. Prerequisite gates (CDA SME PASS-WITH-NOTES, RD-T5-1 Reviewer PASS, RD-T5-1 Tester PASS) are all present and cited.

**Verdict: PASS. The Coder may proceed to RD-T5-3 (numerics report §1–§7, applying SME binding notes T11 and T13).**
