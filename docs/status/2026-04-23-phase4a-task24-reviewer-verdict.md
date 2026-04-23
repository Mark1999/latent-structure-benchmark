# Phase 4a Task #24 — Reviewer Verdict

**Date:** 2026-04-23
**Commit reviewed:** `05e918a feat(collect): expand failures.jsonl shape for verbatim capture (task #24)`
**Architect verdict:** `docs/status/2026-04-23-failures-as-findings-architect-verdict.md` §Stream A + **Amendment A** (the binding schema shape).
**Preceding gates:** Reviewer-only per Architect gate table. No CDA SME or UI/UX required.

---

## Verdict: **PASS**

All 9 standard Reviewer checks PASS or N/A. Shape conforms exactly to Amendment A; backward-compat preserved; DATA_DICTIONARY §9 complete and accurate.

---

## Check matrix

| # | Check | Result |
|---|---|---|
| 1 | No LLM imports in cdb_analyze | PASS — no `cdb_analyze` touch |
| 2 | Append-only JSONL | PASS — no `data/raw/` write in tests (`tmp_path` only) |
| 3 | No secrets | PASS |
| 4 | Forbidden vocabulary | PASS |
| 5 | Schema + DATA_DICTIONARY | N/A — no `cdb_core/schemas.py` change (Amendment A.3: no pydantic model for failure entries). Dictionary update voluntary and correct. |
| 6 | New deps sign-off | N/A |
| 7 | Prompt versioning | N/A |
| 8 | Uncertainty in viz | N/A |
| 9 | Prerequisite verdicts | PASS — Architect Amendment A cited |

## Scope

Exactly 3 files:
- `packages/cdb_collect/cdb_collect/jsonl.py`
- `docs/DATA_DICTIONARY.md`
- `tests/unit/test_jsonl.py`

No `cdb_core/schemas.py` changes (Amendment A §A.3 honored).

## Shape conformance to Amendment A

- **Keyword-only enforcement:** PASS. `*` positional-separator marker present. All 6 new params (`prompt_verbatim`, `response_verbatim`, `thinking_verbatim`, `stop_reason`, `partial_session`, `retry_attempts`) appear after it.
- **Serialization order:** PASS. Dict built as: `timestamp`, `error_type`, `error_message`, `context`, then each optional verbatim/stop field conditionally, then `partial_session` conditionally, then `retry_attempts` unconditionally. Full-kwargs test asserts order explicitly.
- **`partial_session` omit-when-None vs `retry_attempts` always-written:** PASS. `partial_session` guarded by `if partial_session is not None:` — absent when None. `retry_attempts` written unconditionally as `retry_attempts if retry_attempts is not None else []` — always present, minimum `[]`.

## Backward compatibility

All 4 existing callers in `scripts/collect.py` (lines 217, 256, 351, 400) pass only the 3 positional args. New kwargs all default to `None`; those calls will write `retry_attempts: []` + no other new keys. Correct pre-#23 baseline.

## `DATA_DICTIONARY.md`

- §9 is new — no prior conflicting section. `grep -n "failures.jsonl"` returns 4 hits all within §9 (line ~607+).
- Documents all fields with type, required/optional, meaning, example.
- §9.3 covers `partial_session` with cross-ref to step-record schemas.
- §9.4 covers `retry_attempts` 8-field shape and non-empty-vs-empty semantics (pile-sort parse-retry exhaustion only).
- §9.5 records Amendment A.3 no-pydantic decision.
- §9.6 provides a full annotated example.
- Architect verdict + Amendment A cited in both top-level changelog and §9's own.
- v0.1.6 changelog entry at document top.

## Tests

10 new tests, each exercising a distinct concern:

1. `test_append_failure_backward_compat` — 3-arg call; `retry_attempts: []`; 5 other optional keys absent.
2. `test_append_failure_prompt_verbatim_only` — single kwarg isolation.
3. `test_append_failure_response_verbatim_only` — single kwarg isolation.
4. `test_append_failure_thinking_verbatim_only` — single kwarg isolation.
5. `test_append_failure_stop_reason_only` — single kwarg isolation.
6. `test_append_failure_full_kwargs` — all 6 populated; field order verified.
7. `test_append_failure_retry_attempts_list` — 3-entry list; order and `attempt_index` verified.
8. `test_append_failure_partial_session_shape` — `freelist` + `pile_sort`; `interview` absent.
9. `test_append_failure_empty_retry_attempts_always_written` — explicit `[]` written.
10. `test_append_failure_partial_session_none_omitted` — key absent when default None.

All use `tmp_path`. Test count: 464 → 474.

## Commit message

`feat(collect): expand failures.jsonl shape for verbatim capture (task #24)` — 66 chars, correct scope, references Architect verdict + Amendment A + audit context + R7 + task #24. Conforms.

## Forward note for #23

When #23 lands the capture-path code, the 4 `append_failure` call sites in `scripts/collect.py` will need updating to pass the new kwargs. Current backward-compat baseline is clean; #23 is the consumer.

---

*End of verdict. Task #24 complete. Unblocks #23 (gap-close code) which consumes the new `append_failure` signature.*
