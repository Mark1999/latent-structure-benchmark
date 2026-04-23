# Phase 4a Task #26 — Reviewer Verdict

**Date:** 2026-04-23
**Commit reviewed:** `fe7d335 feat(collect): DeclineInterview protocol implementation (task #26)`
**Architect verdict:** `docs/status/2026-04-23-failures-as-findings-architect-verdict.md` §Stream B
**CDA SME verdict:** `docs/status/2026-04-23-decline-interview-protocol-sme-verdict.md` (PASS-WITH-NOTES)
**Design note:** `docs/DECLINE_INTERVIEW_PROTOCOL.md`

---

## Verdict: **PASS**

All 9 R-rule checks PASS. All 5 bound SME notes (1.1, 1.3, 1.4, F, H) applied exactly. `build_db` return-type deviation documented and all callers updated — no regression.

---

## Scope

Exactly 12 files: `schemas.py`, `cdb_core/__init__.py`, `decline_detection.py` (new), `prompts/decline/v1/prompt.txt` (new), `run_decline_interview.py` (new), `jsonl.py`, `build_db.py`, `DATA_DICTIONARY.md`, 3 new test files, 1 updated test file.

## SME note compliance

| Note | Status | Verification |
|---|---|---|
| **1.1** bound prompt | EXACT | `prompts/decline/v1/prompt.txt` matches SME wording; `{task_description}` + `{response_verbatim_or_empty}` placeholders; empty → literal `"(empty)"` per spec. |
| **1.3** detection | EXACT | `DECLINE_ALLOWLIST_VERSION="v1"`; 7 base + 7 apology-framed patterns; all 5 triggers (a)–(e); trigger (e) at 0.95 threshold; post-step-record timing; `failures.jsonl` trigger via `detect_from_failure`. |
| **1.4** schema | EXACT | `originating_step: Literal[4 values]`; `originating_outcome_class: Literal[7 values]`; `detection_rule_version: str`; xor validator present; `thinking_verbatim` docstring clarifies follow-up trace; `version_drift_flag: bool = False`; **no classification/typology field**. |
| **F** version_drift_flag | CORRECT | Computed as `result.model_version_returned != originating` with both-non-empty guard; assigned to `DeclineInterview.version_drift_flag`. |
| **H** prompt versioning | CORRECT | `packages/cdb_collect/cdb_collect/prompts/decline/v1/prompt.txt`; mirrors existing versioned-prompt discipline; no manifest (consistent with existing `v1/` prompts). |

## R-rule findings

| # | Check | Result |
|---|---|---|
| R2 | Append-only JSONL | PASS — `informants.jsonl` not touched; tests use `tmp_path` |
| R4 | Forbidden vocabulary | PASS — no `worldview`, `believes`, `thinks`-as-model, `cultural bias`. Prompt framing "what happened in that exchange" is §1.5-compliant |
| R6 | New deps | PASS — `pyproject.toml` / `package.json` not in diff; stdlib + existing deps only |
| R7 | Schema + DATA_DICTIONARY same-PR | PASS — `schemas.py` + `DATA_DICTIONARY.md` §10 in same commit `fe7d335` |
| R9 | No secrets | PASS |
| R10 | No real API calls in tests | PASS — all three new test files use `unittest.mock.AsyncMock` / `MagicMock`; `adapter.complete` mocked |
| R12 | No LLM imports in cdb_analyze | PASS — `cdb_collect` + `cdb_core` only |
| R8 | Prompt versioning | PASS — see SME Note H row above |
| R11 | Uncertainty in viz | N/A |

## `build_db` return-type deviation

`build_db()` return type changed from `int` to `tuple[int, int]` (informants count, decline count). **PASS** — deviation noted by Coder; all callers updated:

- `main()` in `scripts/build_db.py` — updated.
- `tests/unit/test_build_db.py` — all unpacking forms updated.

DDL idempotency: `build_db()` unlinks the existing DB and rebuilds from scratch (`db_path.unlink()` before `executescript(_DDL)`); `CREATE TABLE` without `IF NOT EXISTS` is correct. Consistent with prior `build_db` behaviour.

FK: `originating_informant_id → informants(informant_id)` present. `originating_failure_id` has no FK (failures.jsonl is not materialized as SQLite). Correct per design.

## Tests

- `test_decline_detection.py`: 23 tests (new) — allowlist, triggers (a)–(e), `detect_from_failure`, `detect_all`.
- `test_decline_interview_schema.py`: 14 tests (new) — construction, xor validator, defaults, valid/invalid Literal values, round-trip.
- `test_run_decline_interview.py`: 15 tests (new) — `build_prompt`, runner shape, `version_drift_flag` logic, `append_decline_interview`.
- `test_build_db.py`: updated for new return type + `decline_interviews` table assertion.

Total: 52+ new/updated test cases (Coder's "77" figure likely includes parametrized expansions and pre-existing `test_build_db` cases). No real API calls in any file.

## Commit message

`feat(collect):` scope; 51 char subject; body cites Architect verdict, SME verdict, design note, all 5 SME notes applied. Conventional Commits. Task ID `#26` present. PASS.

## Forward notes (non-blocking)

- **SME Note F** is binding on the Phase 4a.1 runner (#21), not #26. The #26 runner has wired `version_drift_flag` correctly; #21 can invoke it without schema change.
- **SME Note G** is binding on T5 narrative — not a #26 concern.
- **SME Notes I and J** are binding on future dashboard (Stream C, Phase 6+) and Phase 4a.1 run report respectively — out of #26 scope.

---

*End of verdict. Task #26 complete. Phase 4a.1 runner (#21) is now unblocked on the schema side; waits on T5 data completion to pick the remediation set from the Phase 4a corpus.*
