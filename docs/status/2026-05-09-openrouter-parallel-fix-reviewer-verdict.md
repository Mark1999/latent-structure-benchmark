# Reviewer Verdict: OpenRouter parallel worker fix

**Commit:** `fc1ccd1`
**Task:** Parallelize OpenRouter worker pool (perf(collect))
**Date:** 2026-05-09
**Reviewer:** LSB Reviewer agent (claude-sonnet-4-6)

---

## Verdict

**REVIEWER VERDICT: PASS**

---

## Scorecard

```
Check 1 — No LLM imports in cdb_analyze/:    N/A
Check 2 — Append-only JSONL:                 N/A
Check 3 — No secrets:                        PASS
Check 4 — Forbidden vocabulary:              PASS
Check 5 — Schema + DATA_DICTIONARY:          N/A
Check 6 — New deps sign-off:                 N/A
Check 7 — Prompt versioning:                 N/A
Check 8 — Uncertainty in viz:                N/A
Check 9 — Prerequisite verdicts:             PASS
```

---

## Check detail

**Check 1 — No LLM imports in `cdb_analyze/`:** N/A. This PR touches only
`scripts/run_phase4b_variance.py` and `tests/unit/test_run_phase4b_variance.py`.
The two lines matched in `packages/cdb_analyze/cdb_analyze/__init__.py` are
comment lines (prohibition reminder text), not actual import statements. No
actual LLM client imports exist anywhere in `cdb_analyze/`.

**Check 2 — Append-only `informants.jsonl`:** N/A. No data file changes.

**Check 3 — No secrets:** PASS. Grep for `sk-`, `Bearer`, and
`hooks.slack.com` patterns returned clean across both changed files.

**Check 4 — Forbidden vocabulary:** PASS. Grep for `believes`, `thinks`,
`worldview`, `recognizes`, `interprets`, `perceives`, `publishable` returned
clean across both changed files. Docstring language is technical and
operational; no model-facing framing present.

**Check 5 — Schema + DATA_DICTIONARY:** N/A. `cdb_core/schemas.py` is
unchanged (confirmed via diff).

**Check 6 — New deps sign-off:** N/A. `pyproject.toml` and `uv.lock` are
unchanged (confirmed via diff). The parallelism fix uses only Python stdlib
`threading` which was already in use in this file.

**Check 7 — Prompt versioning:** N/A. No prompt templates touched.

**Check 8 — Uncertainty in viz:** N/A. No frontend changes.

**Check 9 — Prerequisite verdicts:** PASS. This is a runtime performance
bug fix discovered during an active campaign — single OpenRouter thread
bottlenecking ~10 models while Anthropic/OpenAI/Google/xAI workers sat idle.
This follows the same precedent as the preflight fix earlier in Phase 4b: a
concrete runtime failure discovered in production, no new methodology or
architectural decision introduced, no Architect plan required. The fix is
structurally conservative: all existing rate-limit machinery is preserved,
the formula `(60/RPM) × N_workers + 0.1` scales the per-thread sleep to
maintain aggregate RPM at the configured ceiling.

---

## Performance-fix-specific items (advisory checks A–F)

**A. PROVIDER_WORKERS constant:** Correct. `openrouter=4`, all others `=1`.

**B. PROVIDER_SLEEP_S formula:** Confirmed correct. OpenRouter:
`(60/200) × 4 + 0.1 = 1.3 s`. The Coder's docstring states 1.3 s — the
formula produces exactly 1.3 s. No discrepancy.

**C. Thread-spawning loop:** Confirmed. `for worker_idx in range(n_workers)`
spawns N threads per provider sharing one `queue.Queue`. Queue is thread-safe.
Thread names are `provider-{method}-{worker_idx}`.

**D. Sentinel count:** Confirmed correct. All `None` sentinels are enqueued
in `for _ in range(n_workers): q.put(None)` before the thread-spawning loop
starts. N sentinels for N workers; each worker drains cleanly.

**E. CampaignStats lock:** Unchanged. `_lock: threading.Lock` field at line
235 is unmodified; `counter_lock` usage at line 690 is unmodified. Thread
safety of shared state is preserved.

**F. 3 new tests:** All three pass.
- `test_provider_workers_constant_defined` — PASS
- `test_provider_sleep_accounts_for_worker_count` — PASS (validates formula
  algebraically for all providers including the OpenRouter spot-check)
- `test_main_spawns_multiple_threads_for_openrouter` — PASS

**G. CI grep — spend-gate check:** Clean. No `CDB_MAX_SPEND_USD`,
`MAX_SPEND_USD`, `spend_cap`, `cost_cap`, or related tokens in active code.

---

## Build health

- `pytest`: 1215 passed, 26313 warnings (all pre-existing warnings; 0 new
  failures)
- `ruff check .`: All checks passed
- `mypy packages/`: Success — no issues found in 55 source files

---

## Summary

All nine binding checks pass (or are N/A). The parallelism implementation is
technically sound: correct sentinel count, correct per-thread sleep formula,
preserved thread-safety on shared state, and validated by three new focused
unit tests. The fix resolves a genuine campaign bottleneck without approaching
the 200 RPM OpenRouter ceiling.

Coder may proceed. Tester to follow.
