# Reviewer Verdict: reasoning-QA recalibration batch A

**Date:** 2026-07-10
**Changeset:** T1+T2 (qa_check.py Check 5/6 recalibration), T3 (runner.py capacity_note N3+N10), T5 (pipeline.py load_records re-QA), T4+N11 (preflight_reasoning_class_representation.py), T7 (openai_compat.py reasoning token extraction), plus tests and fixtures.
**Prerequisite gate:** CDA SME PASS-WITH-NOTES 2026-07-10, `docs/status/2026-07-10-batchA-reasoning-qa-cda-sme-verdict.md`, notes N1-N14 binding.

## Verdict: PASS

```
REVIEWER VERDICT: PASS

Check 1 -- No LLM imports:            PASS
Check 2 -- Append-only JSONL:         PASS
Check 3 -- No secrets:                PASS
Check 4 -- Forbidden vocabulary:      PASS
Check 5 -- Schema + DATA_DICTIONARY:  N/A
Check 6 -- New deps sign-off:         N/A
Check 7 -- Prompt versioning:         N/A
Check 8 -- Uncertainty in viz:        N/A
Check 9 -- Prerequisite verdicts:     PASS
```

## Rationale

**Check 1.** The function-scope `from scripts.qa_check import run_record_checks` import added to `pipeline.py` was traced through: `scripts/qa_check.py` top-level imports are `requests`, `cdb_core`, and stdlib only. The function-scope imports inside `check_salience_agreement` pull `cdb_analyze.consensus` and `cdb_analyze.salience`, not LLM client libraries. No LLM client library is reachable through this import chain. The `cdb_analyze/__init__.py` result from the grep is a comment block listing forbidden libraries, not an import statement. Rule 11 satisfied.

**Check 2.** `data/raw/informants.jsonl` is gitignored and absent from the diff. The new fixture at `tests/fixtures/reasoning_class/informants.jsonl` is a test artifact, not the production append-only file.

**Check 3.** `api_key="sk-test-key"` in `test_openai_compat_reasoning_tokens.py` is far shorter than the gitleaks `sk-ant-[a-zA-Z0-9_-]{50,}` pattern and does not match. No webhook URLs, real keys, or credential-shaped strings appear in any new or changed file.

**Check 4.** Grep of all changed and new files for the CLAUDE.md §7 and ARCHITECTURE.md §1.5.4 forbidden vocabulary returned no matches.

**Check 9.** CDA SME PASS-WITH-NOTES is present and the implementation addresses all binding notes verbatim. N3 and N10 capacity note strings match the verdict text character-for-character (confirmed by test constants in `test_runner_reasoning_note.py` and `test_runner_dense_tokenizer_note.py`). N4/N12 (methodology footnote) is deferred per explicit SME direction: "at next update." TOKEN_TOLERANCE is 1.0 throughout (N14). No base threshold raised (N7). Bare model IDs in `DENSE_TOKENIZER_MODEL_IDS` are documented with the mechanical verification comment (N8). Two-newline N3+N10 separation implemented and tested.

**Rule 15.** No statistical computation created, modified, or redesigned. QA checks are deterministic comparisons against fixed constants; `load_records` re-QA is a filtering gate, not an estimator.

**Ruff.** `uv run ruff check` on all changed and new files: `All checks passed!`

Coder may merge.
