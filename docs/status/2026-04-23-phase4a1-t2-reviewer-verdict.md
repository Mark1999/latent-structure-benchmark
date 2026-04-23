# Reviewer Verdict — Phase 4a.1 T2 (task #21.T2)

**Date:** 2026-04-23
**Reviewer:** LSB Reviewer (Sonnet 4.6)
**Commit reviewed:** `0e615fa` — `feat(collect): T2 execute path + --source + exclusion (task #21.T2)`
**Files reviewed:**
- `/opt/lsb-agent/scripts/run_decline_backfill.py` (1551 lines post-update, diff: +515 lines)
- `/opt/lsb-agent/tests/fixtures/mock_adapter.py` (new, 79 lines)
- `/opt/lsb-agent/tests/test_run_decline_backfill.py` (2601 lines post-update, diff: +979 lines)

**Prerequisite documents read:**
- `CLAUDE.md` §6 (15 binding rules), §7 (forbidden vocabulary table), §8 (commit conventions)
- `ARCHITECTURE.md` §1.5.4 (forbidden vocabulary superset)
- `SECURITY_AND_HARDENING.md` §9 (Reviewer rules table R1–R12)
- `docs/status/2026-04-23-phase4a1-architect-plan-amendment-1.md` (Amendment 1 spec, §6 T2)
- `docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md` (SME PASS-WITH-NOTES A1–A8)
- `docs/status/2026-04-23-phase4a1-architect-plan.md` (original plan)
- `docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md` (original SME verdict)
- `docs/status/2026-04-23-phase4a1-t1-reviewer-verdict.md` (T1 PASS)
- `docs/status/2026-04-23-phase4a1-t1-update-reviewer-verdict.md` (T1-update PASS-WITH-NOTES)

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

**T2-binding-note scorecard:**

| Check | Status |
|---|---|
| --source informants: no exclusion filter on informants-origin | PASS |
| --source failures: should_include_failure() applied; excluded → SKIP to stderr | PASS |
| --source all: both populations, exclusion on failures only | PASS |
| Pre-flight cost gate uses post-exclusion projection vs 0.8 * cap | PASS |
| Mid-batch cap abort exits 3 (distinct from pre-flight STOP exit 2) | PASS |
| detection_timestamp single batch_start shared across all records (SME A6) | PASS |
| detection_rule_version="v1" on every record | PASS |
| xor invariant: exactly one of originating_informant_id/originating_failure_id | PASS |
| Informants-origin task_description from freelist/pile_sort/interview prompt_verbatim | PASS |
| Failures-origin task_description: prompt_verbatim priority; template fallback (RISK 1 documented) | PASS |
| originating_response_verbatim: correct field by step for informants; empty-string fallback for failures | PASS |
| Recursive-decline: SAFETY_FILTER_MARKERS OR empty/whitespace → RECURSIVE_DECLINE to stderr | PASS |
| Recursive-decline count in CLI summary | PASS |
| Per-call [N/M] progress line with cost/total to stdout | PASS |
| CLI summary: source, records written, records excluded, total spend, per-sub-batch split, detection timestamp, version-drift count, latency min/med/max, recursive-decline count | PASS |
| Production code uses adapter-returned actual cost (interview.cost_usd) for running total | PASS |
| MockAdapter: no real HTTP or LLM SDK calls | PASS |
| N2 (T1-update carry-forward): commit body references all 6 prior gate verdict files | PASS |
| N3 (T1-update carry-forward): SAFETY_FILTER_MARKERS "OTHER" has false-positive risk comment | PASS |

**Commit subject check:** `feat(collect): T2 execute path + --source + exclusion (task #21.T2)` — 67 characters. PASS (≤72).

---

## Check-by-check findings

### Check 1 — No LLM imports in cdb_analyze/: PASS

`packages/cdb_analyze/` not in the commit diff. Grepped all three changed files for
`import anthropic`, `import openai`, `from anthropic`, `from openai`, `InferenceClient`,
`google.generativeai`, `langchain`, `llama_index`. Zero matches in live code; the one hit
is a comment in `mock_adapter.py:6` reading "Never imports anthropic, openai,..." — a
negative-assertion comment, not an import.

The module-top-level imports in `run_decline_backfill.py` are: stdlib only plus
`cdb_collect.adapters.base.ModelAdapter` (the Protocol/base class, not an LLM client) and
`cdb_collect.decline_detection` (pure Python, no LLM calls). The adapter concrete classes
(`AnthropicAdapter`, `GeminiAdapter`, etc.) are imported lazily inside
`_build_adapter_for_model()` (lines 1041–1052) — a function that is never called in the
test path because tests inject `adapter_factory` instead.

### Check 2 — Append-only JSONL: PASS

`git show 0e615fa --name-only` lists exactly three files: `scripts/run_decline_backfill.py`,
`tests/fixtures/mock_adapter.py`, `tests/test_run_decline_backfill.py`. Neither
`data/raw/informants.jsonl` nor `data/raw/failures.jsonl` appears. The execute path writes
only to `data/raw/decline_interviews.jsonl` via `append_decline_interview()` (lazy import at
line 1360). This is the designated append-only output path.

The test `test_execute_does_not_touch_informants_jsonl_or_failures_jsonl` (line 2327) takes
mtime snapshots of both source files before and after `run_execute()` and asserts they are
unchanged. The check is correctly implemented and covers the append-only invariant for the
execute path.

### Check 3 — No secrets: PASS

All added lines in the diff scanned for: API key patterns (`sk-ant-`, `sk-or-v1-`, `hf_`),
webhook URLs (`hooks.slack.com/services/`), bearer tokens, passwords. Zero credential-shaped
strings found. The `MockAdapter` uses only the strings `"mock-req-id"`, `"mock"`, and `True`
as fake response data. No real-looking key patterns. PASS.

### Check 4 — Forbidden vocabulary: PASS

All changed files scanned for CLAUDE.md §7 and ARCHITECTURE.md §1.5.4 forbidden phrases:
`worldview`, `believes`, `thinks` (as model agency), `cultural bias`, `within-model consensus`,
`within-model cultural consensus`, `within-model eigenratio`, `within-model CCM`, `publishable`
(for LSB findings), `How models see the world`, `Model X's worldview`, `What the model understands`.
Zero matches in any added or context line.

The script uses `refusal`, `refusals`, `safety-filter refusals` — approved CDA protocol
terminology per the SME verdicts. `declined` and `decline-interview` are approved. PASS.

### Check 5 — Schema + DATA_DICTIONARY: N/A

`cdb_core/schemas.py` not in the diff. No Pydantic model changes.

### Check 6 — New deps sign-off: N/A

`pyproject.toml` and `apps/dashboard/package.json` not in the diff. The execute path's new
imports (`statistics`, `time`, `asyncio`) are stdlib. `cdb_collect.jsonl` and
`cdb_collect.run_decline_interview` are internal packages already in the dependency set.

### Check 7 — Prompt versioning: N/A

No changes to `packages/cdb_collect/cdb_collect/prompts/`. The template-reconstruction path
in `_task_description_from_failure()` reads (but does not modify) the v1 prompt templates.

### Check 8 — Uncertainty in viz: N/A

Scripts-only commit. No frontend or visualization components.

### Check 9 — Prerequisite verdicts: PASS

This is a methodology-execution task (Phase 4a.1 T2 per Amendment 1 §6). The required
gate chain is:
- Original Architect plan: present at `docs/status/2026-04-23-phase4a1-architect-plan.md`
- Original CDA SME PASS: present at `docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md`
- Amendment 1 plan: present at `docs/status/2026-04-23-phase4a1-architect-plan-amendment-1.md`
- Amendment 1 CDA SME PASS-WITH-NOTES: present at `docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md`
- T1 Reviewer PASS: present at `docs/status/2026-04-23-phase4a1-t1-reviewer-verdict.md`
- T1-update Reviewer PASS-WITH-NOTES: present at `docs/status/2026-04-23-phase4a1-t1-update-reviewer-verdict.md`

All six files exist on disk. The commit body references all six by path (N2 carry-forward
from T1-update satisfied). The T1-update PASS-WITH-NOTES notes N1–N3 were all non-blocking;
N3 (OTHER comment) is addressed in this commit (lines 113–119 of the script). PASS.

---

## T2-specific execute-path verification

### Source filter correctness

**--source informants:** Lines 1320–1323 of `run_execute()` add informants-origin sessions
to `work_items` when `source in ("informants", "all")`. The failures-origin block
(lines 1325–1332) is only entered when `source in ("failures", "all")`, so exclusion filter
is never applied to informants-origin sessions. Test `test_execute_source_flag_forwarded_correctly`
verifies only informants records are written when `--source informants` is set with a mixed
fixture. PASS.

**--source failures:** Only the failures block runs; `should_include_failure()` is applied;
excluded records produce `SKIP: <identifier> — <rationale>` to stderr. Test
`test_execute_failures_only_applies_exclusion` asserts 2 INCLUDE and 1 EXCLUDE from a
3-item failures fixture. PASS.

**--source all:** Both blocks run, producing combined work_items. Test
`test_execute_all_combines_both` verifies informants + filtered failures = correct record
count. PASS.

### Pre-flight cost gate (post-exclusion, 80% of cap)

Lines 1339–1351 of `run_execute()`. Pre-flight computes `n_work * cost_per_call` where
`n_work = len(work_items)` — the post-exclusion work list. The gate fires on
`projected_cost >= escalation_threshold` (same logic as dry-run). Returns exit 2 before any
adapter call. Test `test_execute_pre_flight_stop_at_cap` uses a `CountingAdapter` that
asserts zero calls were made when pre-flight exits 2. PASS.

### Mid-batch cap abort: exit 3 vs exit 2

Line 1438: `call_cost = interview.cost_usd if interview.cost_usd else cost_per_call` — the
production code uses the actual adapter-returned cost for the running total, not the
`cost_per_call` estimate. This is the correct decoupling confirmed by the Coder's deviation
note.

Tests in `TestCostCapAbortDuringExecute`:
- `test_cost_cap_abort_exits_3_not_2`: uses `adapter_cost=3.00` with `cost_per_call=0.05`
  (default). Pre-flight: 5 × $0.05 = $0.25 < $8.00 → passes. Actual cost per call from
  MockAdapter: $3.00. After 4th call: $12.00 ≥ $10.00 → abort, exit 3. Assert `exit_code == 3`.
  PASS.
- `test_cost_cap_abort_exits_3_not_2_correct_cap`: Uses `cost_per_call=0.05, adapter_cost=3.00,
  spend_cap=10.00`. Pre-flight: 5 × $0.05 = $0.25 < $8.00 → passes. Mid-batch: $3.00/call
  hits $10.00 cap after ~4th call → exit 3. Confirms the correctness decoupling the Coder
  documented. PASS.

Note: `test_cost_cap_abort_exits_3_not_2` contains a long trailing comment block
(lines 2395–2400) that reads as incomplete exploratory reasoning before the Coder arrived
at the correct parameter setup in `test_cost_cap_abort_exits_3_not_2_correct_cap`. The
comment states "Re-run with cap=$20 to exercise mid-batch abort:" without completing the
thought, but the assertion at line 2394 (`assert exit_code == 3`) is itself correct. The
pre-flight with `cost_per_call=0.05` (default, not the `adapter_cost=3.00`) correctly passes,
and the mid-batch abort fires from the actual adapter cost. The dangling comment is noise but
not incorrect code. Non-blocking.

### Single batch_start timestamp (SME A6)

`batch_start = datetime.now(UTC)` at line 1364 — before the loop. All
`run_decline_interview()` calls receive `detection_timestamp=batch_start` (line 1425).
Test `test_execute_single_detection_timestamp_shared` asserts `len(timestamps) == 1` across
all written records. PASS.

### detection_rule_version="v1"

Hardcoded at line 1424. Test `test_execute_detection_rule_version_is_v1` asserts on 3
records. PASS.

### xor invariant

For informants-origin: `originating_informant_id=session.identifier`, `originating_failure_id=None`.
For failures-origin: `originating_informant_id=None`, `originating_failure_id=session.identifier`.
Test `test_execute_xor_invariant` verifies exactly one is non-null per record. PASS.

### Reconstruction helpers

`_task_description_from_informant()`: reads `prompt_verbatim` from the step-keyed sub-record
(`freelist`, `pile_sort`, or `interview`). Test
`test_execute_task_description_reconstructed_from_informant_step_4_freelist` uses a
`CapturingMockAdapter` and asserts the freelist prompt_verbatim appears in the decline
interview prompt sent to the adapter. PASS.

`_task_description_from_failure()`: Priority 1 — `entry["prompt_verbatim"]` if present.
Priority 2 — template reconstruction from `prompts/v1/{step}.md`. RISK 1 documented in
docstring (lines 1163–1182): pile_sort and interview templates have unfilled `{{items}}`
markers. Test `test_execute_task_description_reconstructed_from_failure_with_prompt_verbatim`
verifies priority 1. Test `test_execute_task_description_fallback_to_template_for_failure_without_prompt_verbatim`
verifies priority 2 completes without exception and produces a non-empty prompt. PASS.

`_response_verbatim_from_failure()`: returns `entry["response_verbatim"]` or `""`. Test
`test_execute_response_verbatim_empty_string_when_missing` asserts `"(empty)"` appears in
the written record's `prompt_verbatim` (confirming `run_decline_interview.build_prompt()`
receives and substitutes the empty fallback). PASS.

### Recursive-decline capture

`_is_recursive_decline()`: returns True on empty/whitespace-only OR any SAFETY_FILTER_MARKERS
substring match (case-insensitive). Per-occurrence: `RECURSIVE_DECLINE: <id> — <first 120
chars>` to stderr. Count in CLI summary.

Tests: `test_execute_recursive_decline_counted` (blocked response), `test_execute_recursive_decline_empty_response_counted` (empty string). Both assert `RECURSIVE_DECLINE:` in stderr and `Recursive declines observed:  1` in stdout. PASS.

No pause-batch logic implemented, correct per SME A6 (T3B authorization is the operator gate).

### N3 (T1-update carry-forward): OTHER comment

Lines 113–119 of `run_decline_backfill.py` now carry a multi-line comment:
```
# "OTHER" is Gemini's generic content-block finish_reason. Note: case-insensitive
# substring matching means this will match any error message containing the
# substring "other" (e.g., "another", "OtherConnectionError"). Acceptable trade-off
# per CDA SME verdict 2026-04-23 Amendment 1; the rarity of provider refusal
# messages containing an unrelated "other" substring keeps the false-positive rate
# negligible on current corpus. If this changes, revisit via new plan cycle.
```
Test `test_safety_marker_comment_about_other_present_in_source` reads the source file and
asserts `"false-positive"` appears in proximity to the `"OTHER"` marker. PASS. N3 is
closed.

### Per-call progress and CLI summary

Per-call stdout format `[N/M] model=... domain=... step=... cost=$X.XXX total=$X.XXX` —
lines 1461–1473. CLI summary (lines 1493–1513) includes: source, records written, records
excluded, total spend, informants-origin spend, failures-origin spend, detection timestamp,
version drift flags, latency min/med/max, recursive-decline count.

Tests: `test_execute_per_call_cost_printed_to_stdout`, `test_execute_running_total_accumulates`,
`test_execute_summary_includes_per_source_counters`. All pass. PASS.

### Scope discipline

Frozen files (`decline_detection.py`, `run_decline_interview.py`, `jsonl.py`, `schemas.py`)
not in the commit diff. Confirmed via `git show 0e615fa --name-only`.

No changes to `packages/cdb_collect/cdb_collect/prompts/` — template files are read-only.

MockAdapter in `tests/fixtures/mock_adapter.py` is well-scoped: no LLM client imports, no
HTTP calls, satisfies the `ModelAdapter` protocol via `complete()` returning a deterministic
`AdapterResult`.

---

## Coder deviation disclosure verification

**Documented deviation:** mid-batch cap test split into two tests to decouple pre-flight
`cost_per_call` ($0.05) from adapter-returned actual cost ($3.00/call).

Verification:
1. Production code at line 1438: `call_cost = interview.cost_usd if interview.cost_usd else cost_per_call`
   — actual cost from adapter used for running total. Pre-flight uses the `cost_per_call`
   estimate. Correctly decoupled.
2. `test_cost_cap_abort_exits_3_not_2`: `adapter_cost=3.00`, `cost_per_call=0.05` (default) —
   pre-flight passes ($0.25 < $8.00), mid-batch aborts at $12.00. Exit 3. Correct.
3. `test_cost_cap_abort_exits_3_not_2_correct_cap`: explicit comment documents the parameter
   arithmetic. Exit 3 asserted. Correct.

The deviation is a correctness decoupling, not a weakening. PASS.

---

## T2 disposition

**T2 is PASS.** All nine standard checks pass. All T2-specific binding-note checks pass.
Carry-forward notes N2 and N3 from T1-update are both satisfied. No blocking findings. No
new notes.

**Next step:** T3A — live run on lsb-agent-02 against 3 informants-origin records (~$0.15
under $10 cap). Operator must confirm dry-run recursive-decline inspection before T3B
authorization per SME A6.

---

*Verdict saved to `docs/status/2026-04-23-phase4a1-t2-reviewer-verdict.md`. Binding for task #21.T2.*
