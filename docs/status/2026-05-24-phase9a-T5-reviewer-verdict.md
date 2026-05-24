# Reviewer Verdict: Phase 9a T5 — Publish Layer + Cluster Label Aggregation

**Date:** 2026-05-24
**Reviewer:** LSB Reviewer agent (claude-sonnet-4-6)
**Task:** Phase 9a T5 — `aggregate_cluster_labels()` implementation and pipeline wiring
**Changed files reviewed:**
- `packages/cdb_analyze/cdb_analyze/pipeline.py` (new function + wiring)
- `docs/DATA_DICTIONARY.md` (v0.1.21, new §2.7)
- `tests/unit/test_aggregate_cluster_labels.py` (26 new tests, untracked)
- `tests/unit/test_term_cooccurrence_and_cluster.py` (1 test updated)

---

## REVIEWER VERDICT: PASS

```
Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         PASS
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A
Check 6 — New deps sign-off:         N/A
Check 7 — Prompt versioning:         N/A
Check 8 — Uncertainty in viz:        N/A
Check 9 — Prerequisite verdicts:     PASS
```

---

## Check-by-check findings

### Check 1 — No LLM imports in cdb_analyze/
The only grep hits for LLM client library names inside `packages/cdb_analyze/` appear in `__init__.py` as docstring comments that enumerate the prohibition — not as import statements. `pipeline.py` imports only from `cdb_core`, `cdb_analyze.*`, numpy, and the Python standard library. PASS.

### Check 2 — Append-only JSONL
`git diff -- data/raw/informants.jsonl` produced no output. The file was not touched. PASS.

### Check 3 — No secrets
Scanned all four changed files for API key patterns (`sk-ant-`, `sk-or-v1-`, `hf_`), Slack webhook URL patterns, and the three named webhook env vars. The only hits in `DATA_DICTIONARY.md` are in a pre-existing §12 sanitization rules section (pattern descriptions, not live credentials). No credentials found in any changed content. PASS.

### Check 4 — Forbidden vocabulary
Scanned all changed `.py` and `.md` files for every term in CLAUDE.md §7 and ARCHITECTURE.md §1.5.4: `worldview`, `believes`, `thinks` (applied to models), `within-model consensus`, `within-model cultural consensus`, `within-model eigenratio`, `within-model CCM`, `publishable`, `cultural bias`, `How models see`, `What the model understands`. No matches in any changed file or the new §2.7 documentation. PASS.

### Check 5 — Schema + DATA_DICTIONARY
`cdb_core/schemas.py` was not modified in this PR. `term_cluster_labels: list[str] = []` was already present from T3. This T5 adds only the pipeline logic that populates the field, not the field itself. No schema change occurred. DATA_DICTIONARY.md is nonetheless updated (v0.1.21, §2.7, updated `term_cluster_labels` row) which is correct and complete. N/A (schema unchanged).

### Check 6 — New deps sign-off
No changes to `pyproject.toml`, `uv.lock`, `apps/dashboard/package.json`, or `apps/dashboard/package-lock.json`. N/A.

### Check 7 — Prompt versioning
No changes to any file under `packages/cdb_collect/prompts/`. N/A.

### Check 8 — Uncertainty in viz
Non-frontend PR. No new visualization components. N/A.

### Check 9 — Prerequisite verdicts
This is a methodology PR (touching analysis measures — cluster label aggregation). The required CDA SME verdict is present: `docs/status/2026-05-24-phase9a-cda-sme-verdict.md`, verdict PASS-WITH-NOTES. The binding M6 notes are fully addressed: Jaccard threshold >= 0.3 is enforced at `packages/cdb_analyze/cdb_analyze/pipeline.py` line 132; "Uncategorized" fallback is implemented at line 136; modal label selection with frequency-weighted tie-breaking is implemented at lines 155–171. Advisory A2 (imperfect labels acceptable) is documented in both the function docstring and DATA_DICTIONARY.md §2.7. PASS.

---

## Implementation correctness notes (non-blocking)

The test at line 63–75 of `test_aggregate_cluster_labels.py` has a misleading docstring ("cluster gets 'Uncategorized'") but a correct assertion (`["Rest"]`). The docstring describes what *would* happen if only the Solo pile existed; the actual test correctly exercises the best-match selection when one pile clears the threshold and another does not. Not a rule violation — the assertion is what matters.

The `test_below_threshold_gives_uncategorized` test name is slightly inaccurate (the cluster does NOT get Uncategorized in that test; it gets "Rest"). This is a minor naming issue with no behavioral consequence — the implementation under test is correct.

---

## Verdict

All nine checks PASS or are N/A. CDA SME PASS-WITH-NOTES binding notes (M6) are fully applied. No failures. Coder may commit and merge.
