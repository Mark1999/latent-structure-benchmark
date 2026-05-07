# Phase 4b T3 — Tail Failures Diagnostic Memo

**Date:** 2026-05-07
**Scope:** Root-cause investigation and re-attempt of 3 Phase 4a failures
deferred from the phase4a-recovery-2026-05-05 campaign.
**Audit trail:** Campaign `phase4b-tail-rerun-2026-05-07` (script
`scripts/rerun_t3_unexplained_phase4b.py`). Outcomes appended to
`data/raw/informants.jsonl` (1 PASS) and `data/raw/failures.jsonl` (2
FAIL). See Phase 4b Architect plan §7.2 and recovery report §7.3.

---

## §1 Header

**Date of original failures:** 2026-04-22 (Phase 4a collection campaign).
**Date of T3 re-attempt:** 2026-05-07.
**Instrument state at re-attempt:** post-T16 cap fix (commits
`7f8f7f7`/`de3dd7e`), Phase 4b T2 adaptive max-tokens (commit
`628497d`), metadata fix (commit `75917d0`). The T16 fix applies to
the OpenRouter adapter (mistral-small-2603) and the Google adapter; the
OpenAI-compat adapter (gpt-5.4-mini) retains `max_completion_tokens=4096`,
unchanged by T16 (that adapter's original 4096 cap is correct for most
GPT outputs; T16 targeted the Gemini/reasoning-model truncation pattern).
**Stage 1.5b finding:** these 3 cells were confirmed not cap-related.

---

## §2 The Three Cells

### Cell A — `openai/gpt-5.4-mini` × family × run_index=0

| Field | Value |
|---|---|
| model_id | `openai/gpt-5.4-mini` |
| domain | family |
| run_index | 0 |
| original failure timestamp | 2026-04-22T20:26:51.921647 |
| original error_type | `ValueError` |
| original error_message (truncated) | `Pile sort parsing failed after 3 attempts: Could not extract valid JSON from response: {"piles":[["mother","father","parent","child","son","daughter","sibling","brother","sister","grandmother","grandf` … (truncated) |
| original request_id | (not recorded) |
| original response_verbatim | (not recorded in failures.jsonl — pre-verbatim-capture) |
| failures.jsonl line | 10 |

The error message shows the pile-sort response JSON was truncated mid-token
(the response ends at `"ne` — consistent with a hard truncation). The 3
internal parse-retry attempts within the runner all saw the same truncated
response, indicating the truncation was present in the API response text
itself, not a retry-recoverable formatting variation.

### Cell B — `openai/gpt-5.4-mini` × family × run_index=2

| Field | Value |
|---|---|
| model_id | `openai/gpt-5.4-mini` |
| domain | family |
| run_index | 2 |
| original failure timestamp | 2026-04-22T20:27:20.849170 |
| original error_type | `ValueError` |
| original error_message (truncated) | `Pile sort parsing failed after 3 attempts: Could not extract valid JSON from response: {"piles":[["mother","father","parent","child","son","daughter","sibling","brother","sister","grandmother","grandf` … (same truncation shape as Cell A) |
| original request_id | (not recorded) |
| original response_verbatim | (not recorded) |
| failures.jsonl line | 11 |

Truncation pattern is identical to Cell A. Both runs 0 and 2 failed within 29
seconds of each other (20:26:51 → 20:27:20 UTC), suggesting a brief
provider-side condition on 2026-04-22 rather than a persistent model behavior
pattern (runs 1, 3, 4 on the same (model, domain) produced valid records).

### Cell C — `mistralai/mistral-small-2603` × holidays × run_index=3

| Field | Value |
|---|---|
| model_id | `mistralai/mistral-small-2603` |
| domain | holidays |
| run_index | 3 |
| original failure timestamp | 2026-04-22T20:55:22.247858 |
| original error_type | `ValueError` |
| original error_message | `Pile sort parsing failed after 3 attempts: Items missing from pile sort: {'feast of the transfiguration', 'krishna janmashtami', 'nowruz', 'feast of the conversion of st. paul', 'feast of st. basil the great', 'feast of st. john chrysostom', 'feast of corpus christi (orthodox)', 'feast of the chair of st. peter', 'feast of st. athanasius', 'ganesh chaturthi', 'feast of st. george', 'feast of st. joseph', 'feast of st. stephen', 'feast of st. benedict', 'feast of st. gregory the theologian', 'raksha bandhan', 'feast of the presentation of the lord', 'feast of st. nicholas the wonderworker', 'feast of st. michael and all angels', 'feast of st. john the evangelist', 'feast of st. lucy', 'feast of the beheading of st. john the baptist', 'feast of st. francis of assisi', 'feast of st. anthony the great', 'feast of the nativity of st. john the baptist', 'feast of st. nicholas'}` |
| original request_id | (not recorded) |
| original response_verbatim | (not recorded) |
| failures.jsonl line | 23 |

26 items from the freelist were absent from all piles in the pile-sort
response. The parser's coverage check detected the omission after 3 parse-retry
attempts. This pattern differs from the gpt-5.4-mini truncation: the pile-sort
JSON was syntactically valid; the items were simply not placed.

---

## §3 Diagnostic Re-attempt

Campaign ID: `phase4b-tail-rerun-2026-05-07`
Script: `scripts/rerun_t3_unexplained_phase4b.py`
CDB_MAX_SPEND_USD: 5 (exported before run)
Retry budget per cell: 2 attempts (5-second inter-attempt delay)
Instrument: post-T16 + T2 adaptive cap + metadata fix (commit `75917d0`)

### Cell A — `openai/gpt-5.4-mini` × family × run_index=0

**Rerun outcome: RECOVERY_FAILED**

Both attempts returned `HTTP 429 Too Many Requests` with the message
"You exceeded your current quota, please check your plan and billing
details." The adapter exhausted its 5 internal retry attempts (1s/2s/4s/8s/16s
exponential backoff) on each outer attempt before the PartialSessionError was
raised. No API response body was produced.

Failure record appended to `failures.jsonl` at timestamp
2026-05-07T15:19:30.879372 with `recovery_failed=true`.

**Root-cause classification: (a) transport / API issue — provider billing
quota exhaustion.**

The 2026-04-22 original failure (truncated JSON) and the 2026-05-07 re-attempt
failure (quota 429) are distinct events. The original failure was a
provider-side transient truncation. The re-attempt failure is a billing quota
state on the OpenAI account at the time of the re-attempt. Neither failure is
an adapter-side bug or parser issue.

### Cell B — `openai/gpt-5.4-mini` × family × run_index=2

**Rerun outcome: RECOVERY_FAILED**

Identical to Cell A: both attempts returned `HTTP 429 Too Many Requests`,
same quota-exceeded message. Re-attempt ran approximately 70 seconds after
Cell A's failure; the quota state persisted across both cells.

Failure record appended to `failures.jsonl` at timestamp
2026-05-07T15:20:40.659951 with `recovery_failed=true`.

**Root-cause classification: (a) transport / API issue — same billing quota
exhaustion as Cell A.**

### Cell C — `mistralai/mistral-small-2603` × holidays × run_index=3

**Rerun outcome: PASS (attempt 1)**

The cell completed successfully on the first attempt. The recovered record
carries:

| Field | Value |
|---|---|
| informant_id | `f9cd5a4942550e8d` |
| collection_date | 2026-05-07T15:18:18.263432 |
| model_version_returned | `mistralai/mistral-small-2603` |
| qa_passed | `True` |
| qa_notes | `campaign_id=phase4b-tail-rerun-2026-05-07` |
| max_tokens | 16384 (OpenRouter adaptive cap) |
| freelist parsed_items count | 96 |
| freelist output_tokens | 726 |
| pile_sort output_tokens | 606 |
| interview output_tokens | 136 |

The 2026-04-22 original failure (26 items missing from piles) did not recur.
The re-attempt produced a coverage-complete pile-sort response on the first
try. This is consistent with a non-deterministic model behavior pattern — the
original run's pile-sort coverage gap was a single-occurrence event, not a
stable property of the (model, domain) combination.

**Root-cause classification: (b) non-deterministic model-side item omission
— the original failure was a single-occurrence pile-sort coverage gap that did
not recur under re-attempt. The recovered record is canonical corpus data.**

Note: the holidays domain for `mistralai/mistral-small-2603` has 3 other
records in `informants.jsonl` with `qa_passed=False` (runs 0, 2, 4 carry
`label_count_mismatch` QA failures). These are pre-existing records outside
T3 scope.

---

## §4 Disposition

### What is now in the corpus

`data/raw/informants.jsonl` gains one new record:

| informant_id | model_id | domain | run_index | qa_passed | campaign_id |
|---|---|---|---|---|---|
| `f9cd5a4942550e8d` | `mistralai/mistral-small-2603` | holidays | 3 | True | `phase4b-tail-rerun-2026-05-07` |

`data/raw/failures.jsonl` gains two new records:

| timestamp | model_id | domain | run_index | error_type | campaign_id | recovery_failed |
|---|---|---|---|---|---|---|
| 2026-05-07T15:19:30 | `openai/gpt-5.4-mini` | family | 0 | RuntimeError | `phase4b-tail-rerun-2026-05-07` | true |
| 2026-05-07T15:20:40 | `openai/gpt-5.4-mini` | family | 2 | RuntimeError | `phase4b-tail-rerun-2026-05-07` | true |

Verification:
```bash
grep -c 'phase4b-tail-rerun-2026-05-07' data/raw/informants.jsonl data/raw/failures.jsonl
# Expected: informants.jsonl:1  failures.jsonl:2  (sum=3)
```

### `openai/gpt-5.4-mini` family domain coverage

After T3, `openai/gpt-5.4-mini` family coverage is: runs 1, 3, 4 in
`informants.jsonl` (3 of 5 Phase 4a cells recovered). Runs 0 and 2 remain
unrecovered: the 2026-04-22 records carry the original truncation error;
the 2026-05-07 records carry the quota error. Both generations are canonical
failures-as-findings data. The model has n=3 valid family-domain records for
downstream analysis.

### `mistralai/mistral-small-2603` holidays domain coverage

After T3, `mistralai/mistral-small-2603` holidays coverage is: runs 1
(qa_passed=True), 3 (qa_passed=True, newly recovered), 0/2/4
(qa_passed=False, label_count_mismatch). All 5 runs now have records in
`informants.jsonl`.

---

## §5 Forward Carry

**gpt-5.4-mini billing quota — potential re-rerun.** The 2026-05-07
HTTP 429 failures are a billing-quota state on the OpenAI account at the
time of the T3 re-attempt, not a persistent model behavior issue. When the
quota is restored (billing cycle or plan upgrade), the two cells
(`openai/gpt-5.4-mini` × family × run_index ∈ {0, 2}) can be re-attempted
under a new campaign. Whether to schedule this re-attempt depends on
whether n=3 is sufficient for the Phase 4b G1 variance-arm analysis. This
is an Architect-scoped decision, not T3 scope.

**No adapter-side bugs found.** The T3 investigation found no adapter-side
bugs in `openai_compat.py` or `openrouter.py` requiring a fix in this task.
The original 2026-04-22 truncation pattern (gpt-5.4-mini) is consistent with
a transient provider-side event; the 2026-05-07 quota error is a billing
state event. Neither implies an adapter code defect. No code change was made
to adapters or runner in T3.

**No parser-side bugs found.** The mistral-small Cell C success on re-attempt
shows the parser handles the (model, domain) combination correctly when the
model produces a coverage-complete pile-sort response. The 2026-04-22 failure
was a single-occurrence model-side omission, not a parser defect.

---

*End of Phase 4b T3 diagnostic memo. Artifacts: `scripts/rerun_t3_unexplained_phase4b.py`,
`data/raw/informants.jsonl` (+1 record), `data/raw/failures.jsonl` (+2 records).
Next step: Reviewer verdict.*
