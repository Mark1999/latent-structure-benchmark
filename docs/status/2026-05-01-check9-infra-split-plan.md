# Plan: Split Check 9 (backup freshness) out of the per-record QA battery

**Status:** Drafted by Architect, awaiting CDA SME verdict.
**Author:** Architect agent
**Task ID:** F2-T11 (next free F2 slot; Mark to confirm or assign)
**Date:** 2026-05-01
**Companion files:**
- `scripts/qa_check.py` (lines 270–330 — the split site)
- `packages/cdb_collect/cdb_collect/runner.py` (lines 266–285 — the runner caller)
- `tests/unit/test_qa_check.py` (the 7 failing assertions plus the 4 direct check_9 tests at 442/458/473/485 to keep)
- `tests/unit/test_qa_passed_honest.py`
- `tests/unit/test_runner.py`

---

## 1. Summary

`scripts/qa_check.py::run_qa_checks(record, all_records)` runs checks 1–9 on every record. Check 9 (`check_9_backup_freshness`) is, by its own docstring, an infrastructure check — it inspects `logs/backup.log` mtime and has no dependence on the record at all. Wiring it into the per-record battery means every collected `InformantRecord` outside the live VPS gets `qa_passed=False` and `qa_notes` polluted with a string about a missing backup log. CI is red on master since `45206cb` because of this; seven tests fail from this single root cause.

The fix is to split the per-record battery (checks 1–8) from the infrastructure battery (check 9), update the runner to call only the per-record battery, and route the infrastructure battery to the contexts where it actually makes semantic sense (the QA_Runner CLI sweep on the live VPS). No schema change. No change to `ARCHITECTURE.md` §1 commitment 8 or §4.1.6 — the alert path for check 9 still exists; it just stops corrupting per-record `qa_passed`.

## 2. Why this is methodological, not a test fix

`qa_passed` and `qa_notes` are persisted into `data/raw/informants.jsonl` (open data bundle, CC0) and feed downstream analysis filters. The CDA SME owns the answer to: **"Should `qa_passed=False` ever reflect operator infrastructure state, or only properties of the record itself?"**

The Architect's reading is: `qa_passed` describes the *record*, not the *operator's environment*. A record collected during a moment when the operator's backup script was lagging is not itself a suspect record. Conflating the two breaks the open-data contract — a downstream researcher rebuilding the SQLite database from the JSONL bundle has no way to know whether a `qa_passed=False` reflects a real data integrity concern or an operator infra glitch they are not responsible for. But this is a methodology call, not an Architect call. The SME must rule.

## 3. Affected packages and files

| Layer | File | Change |
|---|---|---|
| QA module | `scripts/qa_check.py` | Split `run_qa_checks` into `run_record_checks` (1–8) and `run_infrastructure_checks` (9). Keep a thin compat shim if needed. |
| Collection runner | `packages/cdb_collect/cdb_collect/runner.py` | Call `run_record_checks(record)` instead of `run_qa_checks(record)`. |
| QA CLI entry point | `scripts/qa_check.py::main` and `check_record` | Continue to invoke check 9 once per sweep (not per record). Aggregate-style alert on infrastructure failures. |
| Tests — runner | `tests/unit/test_runner.py` | The 3 failing tests pass automatically once the runner stops calling check 9. No test edits required for the green path. |
| Tests — qa_passed honest | `tests/unit/test_qa_passed_honest.py` | The 3 failing tests pass automatically. |
| Tests — qa_check integration | `tests/unit/test_qa_check.py::test_passing_record_no_failures` | Passes automatically once `run_qa_checks` drops check 9 (or once `run_record_checks` is the new symbol the test imports). |
| Tests — qa_check unit | `tests/unit/test_qa_check.py:442/458/473/485` | Direct unit tests on `check_9_backup_freshness(log_path=...)` stay as-is. |

No changes to `cdb_core/schemas.py`. No changes to `docs/DATA_DICTIONARY.md` (fields unchanged). No changes to `apps/dashboard/`.

## 4. Decomposition — Coder tasks

### Task 1 (single PR-sized commit) — Split the battery and rewire the runner

**Acceptance criteria:**

1. `scripts/qa_check.py` exposes two new public functions:
   - `run_record_checks(record: InformantRecord, all_records: list[InformantRecord] | None = None) -> list[QAFailure]` — checks 1–8 only.
   - `run_infrastructure_checks() -> list[QAFailure]` — currently only check 9.
2. `run_qa_checks` is preserved as a compat shim that calls both and concatenates results, **but** is no longer called from `cdb_collect/runner.py`. Compat shim exists so any external researcher tooling that reads our scripts module does not break. Add a docstring note: "Prefer `run_record_checks` for per-record contexts; `run_infrastructure_checks` for sweep contexts."
3. `packages/cdb_collect/cdb_collect/runner.py::_assemble_record` (line 275) calls `run_record_checks(record)` instead of `run_qa_checks(record)`. The function-scope import is updated accordingly. The `qa_passed` / `qa_notes` wiring downstream of the call is unchanged.
4. `scripts/qa_check.py::main()` calls `run_record_checks` per record (the per-record loop at line 549) and calls `run_infrastructure_checks()` **once per sweep**, after the per-record loop, before `run_aggregate_checks`. Infrastructure failures route through a new `post_infrastructure_alert(failure)` function that posts to `#lsb-alerts` with shape distinguishable from per-record alerts ("QA Infrastructure Failure" vs "QA Failure" header). No `InformantRecord` is mutated by the infrastructure path.
5. `scripts/qa_check.py::check_record(record, all_records)` — the helper at line 371 — calls `run_record_checks` only. (The CLI wrapper handles the infra path.) Update its docstring.
6. The 4 direct unit tests on `check_9_backup_freshness(log_path=...)` at `tests/unit/test_qa_check.py:442,458,473,485` continue to pass unchanged.
7. The 7 currently-failing tests pass without modification:
   - `tests/unit/test_qa_check.py::test_passing_record_no_failures`
   - `tests/unit/test_qa_passed_honest.py::TestT07HonestQaPassed::test_passing_record_has_qa_passed_true`
   - `tests/unit/test_qa_passed_honest.py::TestT07HonestQaPassed::test_passing_record_with_campaign_id`
   - `tests/unit/test_qa_passed_honest.py::TestT09LabelCountMismatch::test_matched_count_record_passes_check_8`
   - `tests/unit/test_runner.py::test_run_informant_default_temperature_and_empty_qa_notes`
   - `tests/unit/test_runner.py::test_run_informant_campaign_id_written_to_qa_notes`
   - `tests/unit/test_runner.py::test_run_informant_temperature_and_campaign_id_together`
8. Add a new test `tests/unit/test_qa_check.py::test_infrastructure_check_returns_check_9_when_log_missing` covering the infra battery's empty-vs-failure semantics.
9. Add a new test `tests/unit/test_qa_check.py::test_run_record_checks_does_not_invoke_check_9` — pass a record into `run_record_checks` from a process whose CWD has no `logs/backup.log`; assert no QAFailure with `check_num == 9`.
10. Update the `Check 9` comment block at the top of `qa_check.py` (lines 58–62) to explicitly mark it as **infrastructure-tier**, not record-tier, and reference `ARCHITECTURE.md` §4.1.6 plus this verdict file.
11. `uv run pytest && uv run ruff check . && uv run mypy packages/` passes locally. No-LLM-imports static check on `cdb_analyze` still green (this PR doesn't touch `cdb_analyze`).
12. Commit message: `fix(scripts): split check 9 (infra) out of per-record QA battery (task #F2-T11)` with body referencing the SME verdict path.

**Reviewer must verify:**
- The runner no longer imports or calls check 9 along the per-record path (grep `runner.py` for `check_9` and for `run_qa_checks`).
- `qa_notes` on a freshly-collected record in a no-`logs/backup.log` environment is empty (or contains only `campaign_id_tag`), not `"backup log missing: ..."`.
- The CLI sweep still surfaces a missing/stale backup log via `#lsb-alerts` — just under a distinct header.
- No forbidden vocabulary in commit message, code comments, or alert text (rule §7).
- The append-only check on `data/raw/informants.jsonl` still passes — this PR makes no data file edits.

**Tester must verify:**
- The 4 direct check_9 tests still pass.
- The 7 previously failing tests are green.
- The 2 new tests are present and pass.
- A simulated CLI sweep with a stale `logs/backup.log` posts an infrastructure alert (test the post path with a `requests.post` mock as `test_slack_called_with_url` already does for the per-record path).

### Task 2 (separate commit, only if SME rules it in scope) — Disposition of records already on disk with check-9-only failures

Open methodology question for the SME: There are existing `qa_passed=False` records in `data/raw/informants.jsonl` whose only failure is the `"backup log missing: ..."` string. Three possibilities:

- **(a) Out of scope.** Leave the records as-is (`data/raw/informants.jsonl` is append-only by §9 pitfall 10; nothing gets edited). Document the historical artifact in the data dictionary commentary. Downstream analysis filters that drop `qa_passed=False` will continue to drop these records.
- **(b) Re-evaluate in place via a new field.** Add a `qa_reevaluated_at` audit annotation in a sidecar file (not in the JSONL) listing the informant_ids that were marked failed solely on check 9 and noting they would now pass. Schema unchanged; sidecar is the audit trail.
- **(c) Re-run the QA sweep against the corpus and emit a sidecar audit report.** Same as (b) but generated automatically by a one-shot script rather than hand-maintained.

Architect's recommendation if Mark/SME want option (b) or (c): a separate commit running `scripts/qa_check.py --reevaluate` that emits `data/raw/qa_reevaluation_2026-05-01.json` listing affected informant_ids. The JSONL itself stays untouched. **Architect prefers (a) for v1** — append-only is a stronger guarantee than retroactive cleanup, and the CDA SME has historically favoured leaving failure annotations in place with documentation rather than rewriting them (see `CLAUDE.md` §9 pitfall 10).

If the SME rules this is out of scope (option a), Task 2 is dropped. If the SME rules it in scope, Task 2 is a separate Coder task with its own acceptance criteria, planned after Task 1 ships green.

## 5. Schema changes required

**None.** `qa_passed: bool` and `qa_notes: str` retain their definitions. `DATA_DICTIONARY.md` does not need an update for Task 1. (If Task 2 is in scope under option b/c, the dictionary may need a paragraph explaining the sidecar reevaluation file; the SME should rule.)

## 6. CDA SME review required? **YES**

Reasons:
1. `qa_passed` semantics are a methodology-tier concern (`CLAUDE.md` §6 rule 13, `ARCHITECTURE.md` §1 commitment 8).
2. The disposition of already-failed-on-check-9 records on disk is a methodology call the Architect cannot make alone.
3. The infrastructure-vs-record split is the kind of decision that should be visible in the verdict log so future Architects don't reintroduce check-9 into the per-record battery by accident.

## 7. UI/UX review required? **No.** No frontend surface area changed.

## 8. Dependency order

- Task 1 must land before any Task 2 (Task 2 depends on the split being in place and on SME ruling on disposition).
- The earlier Google adapter routing fix at `8da288b` is unrelated and already on master; this plan assumes it is.

## 9. Reading list for the Coder before starting Task 1

1. `ARCHITECTURE.md` §1 commitment 8 and §4.1.6 (QA_Runner contract — check 9 is named there as part of the QA suite; the split must keep the alert path intact).
2. `CLAUDE.md` §6 rule 13, §8 (one commit per task, no scope creep), §9 pitfall 10 (append-only data files).
3. `scripts/qa_check.py` end-to-end (~580 lines).
4. `packages/cdb_collect/cdb_collect/runner.py` lines 220–290 (the `_assemble_record` function and the QA wiring).
5. `tests/unit/test_qa_check.py`, `tests/unit/test_qa_passed_honest.py`, `tests/unit/test_runner.py` — the failing tests and their fixtures.
6. The CDA SME verdict file produced from this plan (path TBD: `docs/status/2026-05-01-check9-infra-split-cda-sme-verdict.md`).

## 10. Open methodology questions for the SME

These are the questions the Architect cannot answer alone. The SME's verdict should either resolve them or bounce the plan back for rework.

**Q1 (the core question).** Should `qa_passed=False` ever reflect operator-infrastructure state (e.g., "the operator's backup script didn't run in 48h"), or strictly properties of the record itself? The Architect's reading is "strictly the record itself," which motivates the split. If the SME rules differently — e.g., `qa_passed` is allowed to encode "data may be at risk of loss because backups are stale" — then the plan needs rework, not just a split.

**Q2.** Of options (a) / (b) / (c) for already-failed-on-check-9 records on disk, which does the SME endorse? The Architect prefers (a) but defers to the SME.

**Q3.** Should the new `run_infrastructure_checks` be expanded in scope (now or later) to cover other operator-infrastructure conditions — e.g., disk free space on the VPS, Backblaze B2 reachability — or kept narrowly to backup freshness for v1? The Architect recommends keeping it to backup freshness for v1 (YAGNI), but flags this as a question because it informs the function's naming and import surface.

**Q4.** Should the infrastructure alert posted by the CLI sweep route to a different `#lsb-alerts` thread or a distinct `#lsb-infra` channel? The Architect recommends `#lsb-alerts` with a distinct header (no new channel for v1) because §5 of `CLAUDE.md` only declares three channels and adding a fourth is a meaningful operational change.

## 11. CDA SME four-axis scorecard (SME to fill)

- **Protocol validity:** _____ — [SME notes]
- **Analytical validity:** _____ — [SME notes]
- **Claims validity:** _____ — [SME notes]
- **Audience translation:** _____ — [SME notes]
- **Verdict:** PASS / PASS-WITH-NOTES / FAIL — [rationale]
- **If PASS-WITH-NOTES, mandatory notes the Coder must apply:** _____
- **Resolution of Q1–Q4 above:** _____

## 12. UI/UX scorecard

Not required. No frontend surface area touched.
