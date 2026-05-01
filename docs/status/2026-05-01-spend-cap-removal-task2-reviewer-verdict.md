# Reviewer Verdict — Spend-Cap Removal Task 2 (schema drop)

**Commit:** `c4306926a05ea3fcbcf6b8593e892d7b31f835ea`
**Task:** `#F2-T13` — Drop `cost_usd` field from `RawResponse` and `DeclineInterview`
**Task scope:** Task 2 of 3 (schema + dictionary + build_db; includes minimum caller cleanup for mypy/pytest green)
**Date:** 2026-05-01
**Reviewer:** LSB Reviewer agent (Claude Sonnet 4.6)
**SME gate:** Waived by Mark as project owner (documented in Reviewer conversation, 2026-05-01). Not a methodology change.

---

## REVIEWER VERDICT: PASS

---

## Nine-check scorecard

```
Check 1 — No LLM imports in cdb_analyze/:   PASS
Check 2 — Append-only JSONL:                PASS
Check 3 — No secrets:                       PASS
Check 4 — Forbidden vocabulary:             PASS
Check 5 — Schema + DATA_DICTIONARY:         PASS
Check 6 — New deps sign-off:                N/A
Check 7 — Prompt versioning:                N/A
Check 8 — Uncertainty in viz:               N/A
Check 9 — Prerequisite verdicts:            PASS (Mark waiver documented)
```

---

## Check-by-check findings

### Check 1 — No LLM client imports in cdb_analyze/

grep of `packages/cdb_analyze/` for `import anthropic`, `import openai`, `from anthropic`,
`from openai`, `InferenceClient`, `google.generativeai` returned two hits — both in
`packages/cdb_analyze/cdb_analyze/__init__.py` lines 12-13, which are prohibition comments
explaining what is forbidden, not import statements. This commit touches `packages/cdb_collect/`,
not `cdb_analyze/`. No actual LLM client import exists anywhere in `cdb_analyze/`. PASS.

### Check 2 — Append-only JSONL

`git show c430692 --name-only` contains no files under `data/`. The commit body explicitly
states: "Pydantic v2 default `extra='ignore'` ensures existing on-disk records in
`data/raw/decline_interviews.jsonl` continue to load without exception — the legacy field
is silently dropped on read. Zero edits to existing JSONL lines." Round-trip verified:

```
uv run python -c "from cdb_core.schemas import DeclineInterview; ..."
→ Loaded 27 records without exception
```

No existing line in `data/raw/decline_interviews.jsonl` was edited. PASS.

### Check 3 — No API keys or secrets

Full diff scanned for credential patterns (Slack webhook URL shapes, `sk-ant`, `sk-or`,
`hf_`, `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`, `LSB_ALERTS_WEBHOOK_URL`,
`LSB_CDA_SME_WEBHOOK_URL`, `LSB_UI_UX_WEBHOOK_URL`, B2 key patterns). Zero matches.
gitleaks pre-commit hook ran at commit time (commit exists, hook did not block). PASS.

### Check 4 — Forbidden vocabulary

Full diff scanned for all CLAUDE.md §7 and ARCHITECTURE.md §1.5.4 forbidden phrases:
`worldview`, `believes`, `thinks of`, `cultural bias`, `what the model understands`,
`how models see the world`, `within-model consensus`, `within-model cultural`,
`within-model eigenratio`, `within-model CCM`, `publishable`. Commit message also scanned.
Zero matches. This commit is pure operational/schema text (cost tracking removal); no
model-facing language appears. PASS.

### Check 5 — Schema + DATA_DICTIONARY

Two schemas changed in `packages/cdb_core/cdb_core/schemas.py`:
- `RawResponse`: `cost_usd: float | None` removed (line 100 in pre-commit version)
- `DeclineInterview`: `cost_usd: float` removed (line 619 in pre-commit version)

`InformantRecord` and `GroundingRef` were not touched (confirmed by grep of commit diff).
However, `DeclineInterview` is documented in `DATA_DICTIONARY.md` §10, and the
`DATA_DICTIONARY.md` stability promise covers "any other schema documented here."

`DATA_DICTIONARY.md` updated in the same commit (v0.1.10, 2026-05-01):
- Changelog entry added at top, referencing task `#F2-T13` and both removed fields
- `cost_usd` row removed from §10.2 (DeclineInterview fields table)
- `cost_usd` column removed from §10.4 DDL
- `cost_usd` example value removed from §10.5

Co-update is present, covers both fields, references the task ID. PASS.

### Check 6 — New deps sign-off

`pyproject.toml` and `apps/dashboard/package.json` not in commit. N/A.

### Check 7 — Prompt versioning

No files under `packages/cdb_collect/prompts/` in commit. N/A.

### Check 8 — Uncertainty in visualizations

No files under `apps/dashboard/` in commit. N/A.

### Check 9 — Prerequisite gate verdicts

This task is a schema/operational change, not a methodology or frontend change.
Mark explicitly waived the CDA SME gate ("Mark approved skipping the SME roundtrip")
as project owner. This waiver is recorded in the Reviewer's conversation context
(2026-05-01). The Task 1 predecessor commit `d491ad9` carries a PASS verdict at
`docs/status/2026-05-01-spend-cap-removal-task1-reviewer-verdict.md`.
No UI/UX verdict required (no frontend). PASS.

---

## Specific verification items (A–I)

### A. Scope-creep check — minimum edits only; Task 3 deliverables intact

The five files beyond the Architect's Task 2 scope (schema + dictionary + build_db):

**`packages/cdb_collect/cdb_collect/run_decline_interview.py`:** One line removed —
`cost_usd=result.cost_usd` kwarg from the `DeclineInterview(...)` constructor call.
No other behavioral change. Confirmed by reading the full file diff. Minimum viable.

**`scripts/run_decline_backfill.py`:** One line changed —
`call_cost = interview.cost_usd if interview.cost_usd else cost_per_call`
replaced with `call_cost = cost_per_call`. One substitution, no other changes.

Task 3 deliverables confirmed still intact in the current file:
- `--cost-cap-usd` CLI flag: present (line 991)
- `COST_PER_CALL_USD` constant: present (line 76)
- `DEFAULT_COST_CAP_USD` constant: present (line 77)
- Per-call cost print statements: present (lines 877, 880, 885)
- `STOP` disposition: present (line 899)
- `SURFACE-TO-SME` disposition: present (line 897)
- `COST CAP EXCEEDED` / exit-3 path: present (lines 1485, 1494) — not deleted

The Coder did not perform the full Option B refactor (rename flags, remove `spend.py`).
Those remain for Task 3. This is the minimum needed for mypy + pytest green. PASS.

**Test files:** Two unit tests and one integration test file updated to remove
`cost_usd` field references. All changes are minimum-viable removals. PASS.

### B. Append-only invariant

No files under `data/raw/` appear in the commit. Round-trip load verified (27 records,
no exception). PASS.

### C. Round-trip claim verification

```
uv run python -c "from cdb_core.schemas import DeclineInterview; \
  [DeclineInterview.model_validate_json(line) for line in open('data/raw/decline_interviews.jsonl') \
  if line.strip()]"
→ Loaded 27 records without exception
```
Confirmed. PASS.

### D. build_db.py produces clean SQLite

`uv run python scripts/build_db.py` output:
```
Built data/open_bundle/lsb.sqlite:
  informants:          101
  freelist_items:      19165
  pilesort_cells:      3729817
  interview_labels:    2459
  decline_interviews:  27
```

Schema verified via Python sqlite3:
```sql
CREATE TABLE decline_interviews (
  ...
  stop_reason TEXT NOT NULL,
  qa_notes TEXT NOT NULL DEFAULT '',
  ...
)
```
`cost_usd` column is absent. 27 rows present. PASS.

### E. Forbidden vocabulary

Clean. See Check 4.

### F. No new dependencies

No `pyproject.toml` or `package.json` changes in commit. PASS.

### G. One commit per task

`git show c430692 --format="%H %P %s" -s` confirms one commit with one parent
(`d491ad9bf13772920bcbd24fc3f6178397723c11`). One task ID (`#F2-T13`). Scope-creep
into Task 3's file list was necessary to achieve the acceptance criteria
(`pytest + mypy` green) without a half-broken intermediate state. Ruling below.

### H. `extra='forbid'` not set

`grep -n "model_config\|ConfigDict\|extra=" packages/cdb_core/cdb_core/schemas.py`
returned zero matches. Neither `RawResponse` nor `DeclineInterview` sets
`model_config = ConfigDict(extra='forbid')` or any equivalent. Pydantic v2 default
(`extra='ignore'`) is in effect. Legacy `cost_usd` fields in on-disk records are
silently dropped. PASS.

### I. Pipeline gate verdicts

Task 1 PASS verdict at `docs/status/2026-05-01-spend-cap-removal-task1-reviewer-verdict.md`.
Mark waived SME gate for Task 2 (documented in Reviewer conversation, 2026-05-01).
PASS.

---

## Scope-creep ruling (CLAUDE.md §8 "one commit per task")

**The scope-creep is justified. It does not violate CLAUDE.md §8.**

CLAUDE.md §8 says "one commit per task" and prohibits bundling unrelated work.
The Coder's disclosed deviation bundles Task 3 file touches, but only the minimum
required to satisfy Task 2's own acceptance criteria (`pytest + mypy` clean).

The Coder's reasoning is technically correct and verifiable:
- Pydantic v2 raises `AttributeError` on attribute reads of removed fields
  (not silenced by `extra='ignore'`, which only governs **kwargs to the constructor)
- mypy catches stale `cost_usd=` kwargs statically
- Without these edits, the `DeclineInterview` constructor call in
  `run_decline_interview.py` and the `interview.cost_usd` attribute read in
  `run_decline_backfill.py` would both fail at test time

The edits are:
1. One line removed (`cost_usd=result.cost_usd` kwarg) — minimum
2. One line substituted (`interview.cost_usd` → `cost_per_call`) — minimum
3. Test field removals tracking the schema change — required

None of these cross into Task 3's actual deliverables (flag rename, `spend.py`
deletion, adapter `cost_usd` sweep). The distinction between "minimum to not break"
and "Task 3 refactor" is clear and the Coder respected it.

This is a well-documented, necessary deviation. The commit body explains it explicitly.
The alternative — a Task 2 commit that fails `pytest` and `mypy` — would itself be a
CLAUDE.md violation (§11 "tests pass locally"). The Coder chose the lesser violation.

**Ruling: justified. Not a CLAUDE.md §8 violation.**

---

## Exit-3 dead-code analysis

**The Coder's claim is correct with one important nuance.**

The exit-3 path (`COST CAP EXCEEDED` / hard-cap mid-batch abort, line 1494 in
`run_decline_backfill.py`) is **unreachable in normal operation after this change**,
but it is **not removed from the production code**. The reasoning:

Pre-flight gate (exit 2) fires when: `n_work * cost_per_call >= 0.8 * spend_cap`
Mid-batch cap (exit 3) fires when: `running_total >= spend_cap` (after some calls)

Since `running_total` accumulates `cost_per_call` per call (post-Task-2), and
pre-flight already checks `n_work * cost_per_call >= 0.8 * spend_cap`:

- If pre-flight passes: `n_work * cost_per_call < 0.8 * spend_cap`
- Therefore: `n_work * cost_per_call < spend_cap` (since 0.8 < 1.0)
- Therefore: even processing all `n_work` records: `running_total = n_work * cost_per_call < spend_cap`
- Therefore: exit 3 can never fire after a successful pre-flight

The mathematics are sound. Exit 3 is effectively dead code with a single cost source.

The rewritten tests correctly reflect this: the 6 mid-batch-abort tests now test
pre-flight (exit 2) scenarios, not mid-batch scenarios. The test scenarios cover the
same behavioral territory (over-budget runs are caught), just at the pre-flight gate
instead of the mid-batch gate. Coverage of real behavior is maintained.

**The exit-3 code path remains in `run_decline_backfill.py` (lines 1485-1494).**
Task 3 will clean it up as part of the full refactor. This is acceptable — dead code
in a clearly marked cleanup scope is not a defect.

The single stale artifact in tests: `_run_execute_capture` still carries an `adapter_cost`
parameter that flows into `MockAdapter.cost_per_call` but no longer affects the
accumulator in `run_execute` (which uses the separate `cost_per_call` argument).
This creates a confusing dual-parameter helper where `adapter_cost` is now vestigial.
This is minor and Task 3 will clean it up. Not a blocking defect.

---

## Recommendation: SHIP

All nine checks pass. All nine named spot-checks (A–I) pass. Schema changes are
co-updated in `DATA_DICTIONARY.md` in the same commit. Round-trip load verified
(27 records). `build_db.py` produces clean SQLite with no `cost_usd` column.
Task 3 deliverables (flags, `spend.py`, adapter sweep) are untouched. Exit-3
dead-code claim is mathematically correct. Scope-creep is minimum-necessary and
justified. No secrets, no forbidden vocabulary, no append-only violation.

Task 3 may proceed.
