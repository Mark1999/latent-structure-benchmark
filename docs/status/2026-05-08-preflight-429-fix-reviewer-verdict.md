# Reviewer Verdict — Preflight 429-Detection Fix

**Commit:** `6f88f68`  
**Task:** Preflight 429-detection fix (campaign-launch bug where chained `PartialSessionError` buried the 429/quota signal below `str(exc)` reach)  
**Date:** 2026-05-08  
**Reviewer:** LSB Reviewer agent (claude-sonnet-4-6)

---

## REVIEWER VERDICT: PASS

---

## Scorecard

| Check | Result |
|---|---|
| Check 1 — No LLM imports in `cdb_analyze/` | N/A |
| Check 2 — Append-only JSONL | N/A |
| Check 3 — No secrets | PASS |
| Check 4 — Forbidden vocabulary | PASS |
| Check 5 — Schema + DATA_DICTIONARY | N/A |
| Check 6 — New deps sign-off | PASS |
| Check 7 — Prompt versioning | N/A |
| Check 8 — Uncertainty in viz | N/A |
| Check 9 — Prerequisite verdicts | PASS |

---

## Per-check findings

**Check 1 — No LLM imports in `cdb_analyze/`.**
Neither changed file (`scripts/run_phase4b_variance.py`, `tests/unit/test_run_phase4b_variance.py`) is under `packages/cdb_analyze/`. The grep match in `packages/cdb_analyze/cdb_analyze/__init__.py` is a comment-only warning against importing LLM clients — no actual import present. N/A.

**Check 2 — Append-only JSONL.**
`data/raw/informants.jsonl` is untouched. N/A.

**Check 3 — No secrets.**
`grep -nE "sk-[a-zA-Z0-9]+|Bearer [a-zA-Z0-9]+|hooks\.slack\.com"` on both changed files returned clean. No credentials present.

**Check 4 — Forbidden vocabulary.**
`grep -nE "\b(believes|thinks|worldview|recognizes|interprets|perceives|publishable)\b"` on both changed files returned clean. Comments describe adapter behavior in neutral, mechanistic language. PASS.

**Check 5 — Schema + DATA_DICTIONARY.**
No changes to `packages/cdb_core/cdb_core/schemas.py`. N/A.

**Check 6 — New deps sign-off.**
`pyproject.toml` and `uv.lock` are unchanged. No new dependencies. N/A (trivially PASS).

**Check 7 — Prompt versioning.**
No changes to `packages/cdb_collect/prompts/`. N/A.

**Check 8 — Uncertainty in viz.**
Non-frontend PR. N/A.

**Check 9 — Prerequisite verdicts.**
This is a focused runtime bug fix (no architectural decisions, no methodology changes, no new features, no schema changes). It is precisely the kind of "fix a broken runtime behavior" commit that CLAUDE.md §8 does not route through the full Architect → CDA SME → UI/UX gate sequence. The bug was discovered during an active campaign and the fix is tightly scoped to walking exception chains. PASS.

**R13 — No spend-gate patterns (SECURITY_AND_HARDENING.md §9).**
CI grep for `CDB_MAX_SPEND_USD|MAX_SPEND_USD|DEFAULT_MAX_SPEND|spend_cap|cost_cap|cost-cap-usd|--max-spend` (excluding docs/status/, docs/INCIDENTS/, docs/proposals/, PROMPT_EVOLUTION_LOG.md, ci.yml) returned clean. PASS.

---

## Bug-specific item review (A–G)

**A. `_QUOTA_MARKERS` coverage.**
The tuple covers: `"429"`, `"quota"`, `"rate limit"`, `"too many requests"`, `"resource_exhausted"`, `"insufficient_quota"`, `"rate_limit_exceeded"`, `"overloaded"`. This covers OpenAI (`insufficient_quota`, `rate_limit_exceeded`, `429`), Anthropic (`overloaded`, `429`), Google (`resource_exhausted`), xAI and OpenRouter (both surface as `429`/`too many requests` via openai-compat). The comment correctly documents that Anthropic 529 maps to `"overloaded_error"`. Coverage is adequate for known providers.

One observation: the marker `"retries"` is not present, but that is correct — "retries" alone is not a quota signal (a timeout or parse error could also exhaust retries). The chain walk surfaces the inner `_RetryableError` message directly, so `"429"` and `"insufficient_quota"` are detected without needing to match the outer RuntimeError text.

**B. `_exc_chain_str()` chain walking.**
The implementation walks both `__cause__` (explicit `raise X from Y`) and `__context__` (implicit chaining via `raise X` inside `except`), with `__cause__` preferred. A `seen` set on `id(node)` prevents infinite loops from circular references. Correct.

**C. `_is_quota_exhausted()` lowercasing.**
`_exc_chain_str` applies `.lower()` to each node's `str()` before appending, and all `_QUOTA_MARKERS` strings are already lowercase. Correct.

**D. `_check_provider_available()` inversion.**
`return not _is_quota_exhausted(exc)` correctly inverts: quota-exhausted → `False` (not available); any other exception → `False` from `_is_quota_exhausted` → `True` (available, let cell-level retry handle it). Correct.

**E. Removed local imports.**
The three local imports (`asyncio`, `load_domain`, `run_informant`) were inside `_check_provider_available()`. They were replaced by module-level imports (already present at the top of the script). The docstring comment explicitly notes that local rebindings bypass test patches — this is the correct explanation and the fix is correct.

**F. 9 new tests.**
All 9 new tests (`test_exc_chain_str_single_exception`, `test_exc_chain_str_chained_exception`, `test_is_quota_exhausted_detects_direct_429`, `test_is_quota_exhausted_detects_chained_429`, `test_is_quota_exhausted_returns_false_for_unrelated_error`, `test_is_quota_exhausted_returns_false_for_network_timeout`, `test_check_provider_available_detects_chained_429_error`, `test_check_provider_available_returns_true_for_transient_parse_error`) pass. The regression test (`test_check_provider_available_detects_chained_429_error`) reproduces the real exception chain shape from the adapter (three levels: `PartialSessionError`-shaped outer → `RuntimeError("... after 5 retries")` → `RuntimeError("HTTP 429: {insufficient_quota...}")`) and confirms `str(outer)` does not contain the 429 marker while `_is_quota_exhausted` still returns `True`. This directly exercises the bug scenario.

**G. CI grep clean.**
`git grep` for all spend-gate tokens returned empty. PASS.

---

## Test suite results

- `uv run pytest tests/unit/test_run_phase4b_variance.py`: 37 passed in 0.81s
- `uv run pytest` (full suite): 1212 passed, 26313 warnings
- `uv run ruff check .`: All checks passed
- `uv run mypy packages/`: Success: no issues found in 55 source files

---

## Campaign status

Phase 4b T4 campaign is actively running in tmux `lsb:phase4b-t4` (PID 1285886). The fix was applied to the source file; Python already loaded the module at startup so the running process is unaffected. No disruption to the running campaign.

---

## Failures

None.

## Required before merge

None. Coder may commit.
