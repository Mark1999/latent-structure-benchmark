# Phase 4a Task #19 — Reviewer Verdict

**Date:** 2026-04-23
**Commit reviewed:** `d49efcd docs(status): verbatim-capture audit report (task #19)`
**Architect verdict:** `docs/status/2026-04-23-failures-as-findings-architect-verdict.md` §Stream A
**Preceding gates:** None required (docs-only audit task).

---

## Verdict: **PASS**

All 9 standard Reviewer checks PASS or N/A. Audit is complete, accurate, well-bounded.

---

## Check matrix

| # | Check | Result |
|---|---|---|
| 1 | No LLM imports in cdb_analyze | N/A — docs-only |
| 2 | Append-only JSONL | PASS — JSONL files gitignored; audit reads but doesn't modify |
| 3 | No secrets | PASS — no API keys, webhook URLs, credentials |
| 4 | Forbidden vocabulary | PASS — no `worldview`, `believes`, `thinks`-as-model, etc. |
| 5 | Schema + DATA_DICTIONARY | N/A — §5 proposes a shape for #24, doesn't commit one |
| 6 | New deps sign-off | N/A |
| 7 | Prompt versioning | N/A |
| 8 | Uncertainty in viz | N/A |
| 9 | Prerequisite verdicts | PASS — Architect verdict referenced |

## Scope

Exactly one file: `docs/status/2026-04-23-verbatim-capture-audit.md`. No code, schema, test, or `.env` changes.

## T4 accounting reconciliation

Live counts: `informants.jsonl` = 101 lines, `failures.jsonl` = 29 lines = 130 total. Coder's "97 + 23 = 120" is consistent:
- 4 phi-4 T3 canary records in `informants.jsonl` (101 − 4 = 97).
- 6 phi-4 T3 canary entries in `failures.jsonl` (29 − 6 = 23).

Filtering rationale documented explicitly in audit §4 line 238 and Deviations section line 390. **120/120 T4 sessions accounted, zero silently discarded.**

## Gap verification

- **Gap A confirmed.** `runner.py:309–341` has three bare sequential awaits with no per-step exception handling. `freelist_record` lives only in `run_informant` local scope; when `run_pile_sort` raises at line 315, the exception propagates directly to `collect_single_pass` which calls `append_failure` with only `{model_id, domain, run_index}`. Architect's root-cause hypothesis confirmed.
- **Gap B confirmed.** `run_two_pass` and `run_baseline_sort` have no per-iteration try/except. A single raise exits the loop.
- **Gap C confirmed.** `pile_sort.py:225–255` retry loop assigns `result` on each iteration; after the final `parse_pile_sort` raises, line 253 raises a bare `ValueError` — `result` is in scope but not attached.

## Outcome class enumeration

§6 summary table lists 11 rows (Coder's narrative count "10" slightly undercounted the table's 11 due to variant-splitting). Substantively complete: success QA-pass, success QA-fail, step-2 parse fail (empty / truncated / items-missing variants), HTTP 4xx at step 1 and step 2+, adapter timeout, HTTP-200 empty body, stream-cut (N/A), two_pass/baseline outer exception.

## Schema deviation (retry_attempts)

Clearly surfaced in §5 with rationale. `retry_attempts: list[...]` addition beyond the Architect's singular `response_verbatim`. Explicitly flagged "Surface to Architect for ruling before #24 implementation." No pre-committed schema change.

*Note forward: the Architect has now ruled on this via Amendment A to the Architect verdict — hybrid shape (singular top-level + `retry_attempts` list). See commit appending Amendment A.*

## #23 recommendations

Five discrete bugs in audit §7, each with file, line range, root cause, minimal fix. All bounded to single files (`runner.py`, `pile_sort.py`, `collect.py`, `jsonl.py`). Actionable and non-overlapping.

## Commit message

`docs(status): verbatim-capture audit report (task #19)` — correct scope, 54 chars, references Architect verdict. Conforming.

---

*End of verdict. Task #19 complete. Unblocks #23 (gap-close code) and #24 (schema expansion) — both now have finalized specs via Architect Amendment A.*
