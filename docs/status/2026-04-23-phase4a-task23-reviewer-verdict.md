# Phase 4a Task #23 — Reviewer Verdict

**Date:** 2026-04-23
**Commit reviewed:** `36bca21 fix(collect): close verbatim-capture gaps on step-level failures (task #23)`
**Follow-on commit (notes applied):** documentation of Gap B stop-on-first deviation (added after this verdict per Note 1).
**Architect verdict:** `docs/status/2026-04-23-failures-as-findings-architect-verdict.md` §Stream A + **Amendment A**
**Audit:** `docs/status/2026-04-23-verbatim-capture-audit.md` §3 + §7
**Schema dependency:** commit `05e918a` (task #24) — consumed `append_failure` kwargs
**Preceding gates:** Reviewer-only per Architect gate table.

---

## Verdict: **PASS-WITH-NOTES**

All 9 R-rule checks PASS or N/A. All 3 gaps closed. One deviation from the Architect brief on Gap B — safe, strictly-better-than-pre-fix, but undocumented until Note 1 applied.

---

## Scope

Exactly 5 files:
- `packages/cdb_collect/cdb_collect/exceptions.py` (new)
- `packages/cdb_collect/cdb_collect/protocol/pile_sort.py`
- `packages/cdb_collect/cdb_collect/runner.py`
- `scripts/collect.py`
- `tests/unit/test_partial_session_error.py` (new)

No `cdb_core/schemas.py` touch, no `pyproject.toml`/`uv.lock` touch.

## Gap A — `run_informant` exception handling

**PASS.** All three step awaits wrapped in try/except at `runner.py:311–389`:
- Step 1 (`run_free_list`) → `PartialSessionError(failed_step="freelist", partial_session={})`.
- Step 2 (`run_pile_sort`) → catches `PileSortParseError` separately (lines 337–365) and bare `Exception` (lines 366–371); both raise `PartialSessionError(failed_step="pile_sort")`.
- Step 3 (`run_pile_interview`) → `PartialSessionError(failed_step="interview", partial_session={freelist, pile_sort})`.
- `partial_session` populated via `model_dump()` at lines 325 and 373.

## Gap B — per-iteration try/except (deviation)

**PASS-WITH-NOTES.** `run_two_pass` Pass-2 loop and `run_baseline_sort` loop gain per-iteration try/except. Verbatim preserved on failure via `PartialSessionError`.

**Deviation:** the Architect §Stream A brief specified "per-iteration try/except that calls `append_failure` with whatever partial state is available, then continues to the next iteration." The Coder implemented **stop on first per-iteration failure** instead of continuing.

**Coder's rationale** (surfaced in report): continue-after-failure requires changing the runner return type or adding a failure-callback parameter — both architecturally significant. Stop-on-first preserves the existing runner contract.

**Disposition:**
- Pre-fix: stop + lose verbatim. Post-fix: stop + preserve verbatim. Strictly better.
- Deviation is safe and coherent with existing runner design.
- **Note 1 (applied):** deviation now documented in-code at `runner.py` before the Pass-2 loop (~line 492) and before the baseline loop (~line 656). Both comment blocks reference Amendment A and this verdict.
- **Follow-up task for Architect:** ruling on continue-after-failure for `two_pass` Pass-2 and `baseline_sort` loops if wanted. Not a Phase 4a blocker — Phase 4a uses `single_pass`.

## Gap C — `PileSortParseError` with attempts list

**PASS.** `pile_sort.py` retry loop accumulates all `AdapterResult` objects per attempt (line 227); exhaustion raises `PileSortParseError(attempts=all_results, per_attempt_errors=all_errors, prompt_verbatim=prompt)` at lines 259–264.

`run_informant` maps `attempts[:-1]` → `retry_attempts` list; `attempts[-1]` → top-level verbatim. The 8-field dict at `runner.py:343–353` matches Amendment A.1 exactly: `attempt_index`, `response_verbatim`, `thinking_verbatim`, `stop_reason`, `input_tokens`, `output_tokens`, `latency_ms`, `parse_error_message`. Identical shape reproduced at `run_two_pass` (507–518) and `run_baseline_sort` (668–681) sites.

## Exception definitions

**PASS.** Both classes in `packages/cdb_collect/cdb_collect/exceptions.py`:
- `PartialSessionError(Exception)` at line 17.
- `PileSortParseError(ValueError)` at line 74. `ValueError` subclass confirms backward compat with any existing `except ValueError` callers.

## `collect_single_pass` catch order

**PASS.** `PartialSessionError` caught **before** bare `except Exception` at `scripts/collect.py:215–233`. All 6 new kwargs populated from exception attributes. Bare Exception path unchanged (3-arg backward-compat path for truly pre-session failures). Same ordering in `collect_two_pass` (273–300) and `collect_baseline` (437–464).

## Tests

**PASS.** 11 test functions cover exception construction + field defaults (3), PileSortParseError construction + ValueError subclass + default prompt (3), `run_informant` step-1 failure (1), step-2 non-parse failure with freelist partial (1), step-2 `PileSortParseError` mapping with retry_attempts (1), step-2 single-attempt edge (1), step-3 interview failure with freelist+pile_sort partial (1).

No real API calls — `adapter.complete` mocked via `MagicMock` + async def in all tests. No `httpx`, `anthropic.`, or `data/raw/` touches.

## R-rule findings

| # | Check | Result |
|---|---|---|
| 1 | No LLM imports in `cdb_analyze` | PASS — match in `cdb_analyze/__init__.py` is prohibition comment, not import |
| 2 | Append-only JSONL | PASS — no JSONL write; tests use in-memory mocks |
| 3 | No secrets | PASS — `tokens` matches are technical fields |
| 4 | Forbidden vocabulary | PASS |
| 5 | Schema + DATA_DICTIONARY | N/A |
| 6 | New deps | N/A |
| 7 | Prompt versioning | N/A |
| 8 | Uncertainty in viz | N/A |
| 9 | Prerequisite verdicts | PASS — Architect verdict + Amendment A in commit body |

## Commit message

`fix(collect): close verbatim-capture gaps on step-level failures (task #23)` — 68 chars, correct scope, references Architect verdict + Amendment A + audit + 3 gaps. Conforms.

---

## Forward notes

### Note 1 (APPLIED in follow-on commit)

Gap B deviation (stop-on-first-failure vs continue-after-failure) must be documented in-code. **Applied** — comment blocks added before `run_two_pass` Pass-2 loop and `run_baseline_sort` loop, each citing Amendment A and this verdict. No Python behavior change.

### Note 2 (forward task)

Continue-after-failure semantics for `run_two_pass` Pass-2 and `run_baseline_sort` loops: Architect ruling needed on whether to implement the Amendment A brief's specified continue behavior, which would require either a return-type change or a failure-callback parameter. Not a Phase 4a blocker — `single_pass` is the Phase 4a mode. Track as a separate backlog task.

---

*End of verdict. Task #23 complete (PASS-WITH-NOTES; Note 1 applied in a follow-on commit). T5 data side is now unblocked.*
