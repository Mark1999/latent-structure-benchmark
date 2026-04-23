# Verbatim-Capture Audit Report — Task #19

**Date:** 2026-04-23
**Auditor:** Coder (Claude Sonnet 4.6)
**Scope:** `packages/cdb_collect/` — runner, adapters, parsers; `scripts/collect.py`; `data/raw/informants.jsonl` (101 records); `data/raw/failures.jsonl` (29 entries)
**Architect verdict reference:** `docs/status/2026-04-23-failures-as-findings-architect-verdict.md` §Stream A
**Status:** COMPLETE — no code changed in this task

---

## §1 Scope

This audit traces every possible LLM session outcome through the cdb_collect pipeline to answer the criterion stated in the Architect's verdict: "every session the API handled must be captured verbatim somewhere — either in `informants.jsonl` with `prompt_verbatim` + `response_verbatim` + `thinking_verbatim` on each step record, or in `failures.jsonl` with the same fields on whatever steps completed before the failure." The audit covers all five collection modes (`single_pass`, `two_pass`, `baseline_items`, `cross_model_consensus`, and the coarser two_pass/baseline outer catch), all five adapter families (Anthropic, OpenAI-compat, Google Gemini, OpenRouter, HuggingFace), all three step-level parsers (free_list, pile_sort, pile_interview), the QA layer, and the T4 corpus of 120 expected sessions (12 models × 2 domains × 5 runs). The audit is read-only: no collection code, adapters, parsers, schemas, or JSONL files were modified.

---

## §2 Session Outcome Classes

### Class 1: Success — all 3 steps complete, QA passes

**Code path:** `run_informant` (runner.py:287) → all three awaits return normally → `_assemble_record` → `append_record` (jsonl.py:15) → `check_record`.

**Verbatim landing:** `informants.jsonl`. Each step record carries `prompt_verbatim`, `response_verbatim`, and `thinking_verbatim` (schemas.py:407–449).

**Fields present:**
- `freelist.prompt_verbatim` ✓ (free_list.py:116)
- `freelist.response_verbatim` ✓ (free_list.py:117)
- `freelist.thinking_verbatim` ✓ (free_list.py:118)
- `pile_sort.prompt_verbatim` ✓ (pile_sort.py:231)
- `pile_sort.response_verbatim` ✓ (pile_sort.py:232)
- `pile_sort.thinking_verbatim` ✓ (pile_sort.py:233)
- `interview.prompt_verbatim` ✓ (pile_interview.py:139)
- `interview.response_verbatim` ✓ (pile_interview.py:140)
- `interview.thinking_verbatim` ✓ (pile_interview.py:141)

**QA runs after `append_record`** (collect.py:208 calls `check_record` after line 207 `append_record`), so QA cannot suppress a record that is already written. The record always lands in `informants.jsonl` before QA fires.

**T4 examples:** All 20 Anthropic records (claude-opus-4-6, claude-sonnet-4-6 × family/holidays), all 10 DeepSeek records, all 10 Mistral-large records.

**Verdict: OK**

---

### Class 2: Success, all 3 steps complete, QA fails post-assembly

**Code path:** Same as Class 1. `_assemble_record` calls `run_qa_checks` (runner.py:274), sets `qa_passed=False` and `qa_notes` with failure reasons, then `append_record` writes the fully-verbatim record. `check_record` (collect.py:208) fires after write and posts to Slack.

**Verbatim landing:** `informants.jsonl` — all nine verbatim fields present despite `qa_passed=False`.

**T4 examples:**
- `qwen/qwen3.6-plus`: all 10 records `qa_passed=False`; `qa_notes` contains latency ms + token count check failures (e.g., `"154728ms; 8544"`). Verbatim is fully present in every record.
- `x-ai/grok-4`: 8 of 10 records `qa_passed=False` due to latency > 60,000 ms. All have complete `pile_sort.response_verbatim` with valid JSON piles. No verbatim is lost.
- `z-ai/glm-5.1` family run_index=0,2,4 and holidays run_index=1: `pile_sort.response_verbatim` is present (e.g., `'```json{"piles": []}\n```'`) though parse yielded zero piles. `qa_passed=False`.

**Verdict: OK**

---

### Class 3: HTTP 200, parse failure after retries (mid-record — step 2 raises)

**Code path:**
1. `run_free_list` (free_list.py:110) completes → returns `(freelist_record, freelist_result)` to `run_informant` locals (runner.py:309–313).
2. `run_pile_sort` (pile_sort.py:225–255) calls `adapter.complete()` up to `_MAX_PARSE_RETRIES=3` times. Each call returns an `AdapterResult` with `text` populated (even if empty). After the final attempt, `parse_pile_sort` raises `ValueError`.
3. `ValueError` propagates out of `run_pile_sort` → back into `run_informant` (runner.py:315–320). `freelist_record` and `freelist_result` are still live in `run_informant`'s local scope. The pile-sort `result` local inside `run_pile_sort`'s loop is also live at the moment of the final raise — but it is local to `run_pile_sort` and not accessible to the caller once the exception escapes.
4. Exception propagates from `run_informant` to `collect_single_pass` (collect.py:200–221).
5. `collect_single_pass` catches `Exception` at line 214 and calls `append_failure(e, {"model_id": ..., "domain": ..., "run_index": ...}, FAILURES_JSONL)` (collect.py:217–220).
6. `append_failure` (jsonl.py:44–56) writes: `{timestamp, error_type, error_message, context}`. **No verbatim fields of any kind.**

**What is lost:**
- `freelist_record.prompt_verbatim` — built and in scope, never captured in failures.jsonl
- `freelist_record.response_verbatim` — built and in scope, never captured
- `freelist_record.thinking_verbatim` — built and in scope, never captured
- `pile_sort.prompt_verbatim` — built inside run_pile_sort before each attempt, never surfaced to caller
- `pile_sort.response_verbatim` — each attempt's `result.text` (the raw unparseable response), never surfaced to caller. In the Gemini and GLM cases this is an empty string; in other cases it may contain truncated JSON.
- `pile_sort.thinking_verbatim` — each attempt's `result.thinking_text`, never surfaced
- `pile_sort.stop_reason` — e.g., `"STOP"` or `"MAX_TOKENS"`, never surfaced

**T4 evidence:** 10 Gemini failures (family ×5 + holidays ×5) and 6 GLM failures (family run_index=1,3 + holidays run_index=0,2,3,4) fall into this class. The `error_message` in failures.jsonl confirms: `"Pile sort parsing failed after 3 attempts: Could not extract valid JSON from response: "` (empty response string after the colon). Three additional models had similar parse failures for other reasons: meta-llama/llama-4-maverick (4 runs), openai/gpt-5.4-mini (2 runs), mistralai/mistral-small-2603 (1 run).

**Verdict: GAP — verbatim from all completed/attempted steps is lost to failures.jsonl**

---

### Class 4: Partial success — step N succeeded, step N+1 raised (Architect root-cause hypothesis)

The Architect's strong hypothesis was: "if step 2 raises, step 1's verbatim is lost in local scope." This audit confirms the mechanism:

In `run_informant` (runner.py:309–341):
```
freelist_record, freelist_result = await run_free_list(...)   # line 309
pilesort_record, _ = await run_pile_sort(...)                  # line 315
interview_record, _ = await run_pile_interview(...)            # line 324
```

If `run_pile_sort` raises at line 315, `freelist_record` is a fully-populated `FreelistRecord` with all three verbatim fields set — it is a live local variable in `run_informant`. However, Python's exception propagation means `run_informant` never reaches `_assemble_record`, and the exception propagates directly to `collect_single_pass`, which calls `append_failure` with only `{model_id, domain, run_index}`. The `freelist_record` is garbage-collected.

**The Architect's hypothesis is confirmed.** The T4 corpus shows this class fired on every single-pass Gemini run (10 total) and on at least 6 GLM runs where step 1 succeeded and step 2 returned an empty-body response.

The same pattern applies if step 3 (`run_pile_interview`) raises: both `freelist_record` and `pilesort_record` are lost. No T4 instances of step-3 failure were observed (the interview parser does not raise — it uses a mismatch signal, not an exception), but the structural gap exists.

**Verdict: GAP — confirmed root cause as hypothesized**

---

### Class 5: Adapter HTTP 4xx / 5xx

**Anthropic adapter (anthropic.py:71–86):** Retries on `RateLimitError`, `InternalServerError`, `APIConnectionError`. Non-retryable errors (including 400/422) raise immediately after the first attempt. A 400 raises `anthropic.BadRequestError` which is not caught by the retry loop → propagates to `run_free_list` → `run_informant` → `collect_single_pass`.

**OpenAI-compat (openai_compat.py:189–193):** Status codes in `{429, 500, 502, 503, 504}` raise `_RetryableError` and are retried. `resp.raise_for_status()` is called for all other non-2xx → raises `httpx.HTTPStatusError`.

**OpenRouter (openrouter.py:132–136):** Same retryable set as OpenAI-compat. Non-retryable non-2xx raises `httpx.HTTPStatusError`.

**HuggingFace (huggingface.py:115–119):** Same retryable set.

**Google (google.py:81–97):** Catches all exceptions; retries only if error string contains keywords like `"429"`, `"500"`, `"connection"`, `"timeout"`. All other exceptions (including 400, 403) raise immediately.

**When HTTP 4xx fires at step 1 (freelist):**
- The prompt was constructed by `load_prompt` in `run_free_list` before the `adapter.complete()` call.
- `adapter.complete()` raises; `run_free_list` never returns a record.
- No `freelist_record` exists in `run_informant` scope.
- Exception propagates to `collect_single_pass` → `append_failure` with `{model_id, domain, run_index}`.
- The **prompt text** (which was constructed before the HTTP call) is lost.

**T4 evidence:** phi-4 T3 canary (not T4 proper): 5 × HTTP 400 failures on freelist step, family domain, run_index=0–4. failures.jsonl entries have no prompt_verbatim. The prompt was constructed before the call failed but was not captured.

**Verdict: GAP — prompt_verbatim from the failed step is not captured. For step 1 failures, there is no prior-step verbatim either. For steps 2–3, prior-step verbatims are also lost (same Class 4 mechanism).**

---

### Class 6: Adapter timeout

**OpenAI-compat, OpenRouter, HuggingFace:** `httpx.AsyncClient` is initialized with `timeout=httpx.Timeout(600.0)` (openai_compat.py:107, openrouter.py:48, huggingface.py:45). A timeout raises `httpx.TimeoutException`, which is not in the retryable set for any of these adapters, so it propagates as a non-retryable exception after the first (or Nth retry) attempt.

**Anthropic:** The SDK manages timeouts internally. A timeout surfaces as `anthropic.APIConnectionError`, which IS in the retry set (anthropic.py:74). After 5 retries, `RuntimeError` is raised.

**Google:** `asyncio.to_thread` with synchronous call. A timeout would surface as an exception with "timeout" in the string (google.py:87), which IS retryable. After 5 retries, `RuntimeError` is raised.

**In all cases:** A timeout at any step propagates to `collect_single_pass` as an exception and routes to `append_failure` with no verbatim. For timeouts at step 1, the prompt was constructed but not captured. For timeouts at step 2+, prior-step verbatims are lost.

**There is no difference in the handling path between a timeout and any other adapter exception.** No truncated response bytes are available because the connection did not complete.

**Verdict: GAP — same as Classes 3/4/5. No T4 instances observed (no timeout entries in failures.jsonl), but the structural gap exists.**

---

### Class 7: Adapter HTTP 200 with empty body

**This is the confirmed Gemini class.** The Google adapter (google.py:140–147) extracts text by iterating `response.candidates[0].content.parts`. If `response.candidates` is non-empty but all parts have `text=""` or `part.thought=True` with no non-thought parts, `text` remains `""`. The adapter returns `AdapterResult(text="", ...)` with `stop_reason` extracted from `response.candidates[0].finish_reason.name` — no exception is raised.

The non-empty `response.candidates` condition is what distinguishes this from an IndexError path. The Gemini failures in T4 are all `ValueError` (not `IndexError`), confirming that `response.candidates` had at least one candidate, but its `content.parts` yielded no non-thought text.

**For OpenAI-compat (openai_compat.py:200):** `text = message.get("content") or ""` — empty content returns `""` without error.

**For OpenRouter (openrouter.py:143):** Same pattern: `text = message.get("content") or ""`.

**For HuggingFace (huggingface.py:126):** `text = choice["message"]["content"] or ""` — same.

**In all four cases:** An empty-body HTTP 200 returns a valid `AdapterResult` with `text=""`. The adapter call itself does not raise. The failure occurs later at the parse layer (`parse_pile_sort` raises `ValueError: Could not extract valid JSON from response: `), placing this squarely in Class 3.

**Verdict: GAP — same as Class 3. The empty response text IS in `result.text` at the time `run_pile_sort` raises, but it is not surfaced to `failures.jsonl`.**

---

### Class 8: Adapter stream-cut mid-response

**No adapter in cdb_collect uses streaming.** All five adapters use non-streaming completion calls:
- Anthropic: `self._client.messages.create(**kwargs)` — no `stream=True`
- Google: `self._client.models.generate_content(...)` — synchronous in thread, no streaming
- OpenAI-compat: `httpx.AsyncClient.post(...)` → `resp.json()` — full body only
- OpenRouter: same httpx pattern
- HuggingFace: same httpx pattern

**Verdict: OK — streaming is not used; stream-cut is not a live failure class.**

---

## §3 Gap Analysis

### Gap A: `collect_single_pass` loses all verbatim on exception

**File:line:** `scripts/collect.py:214–220`

```python
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    logger.exception("Run %d failed", run_index)
    append_failure(e, {
        "model_id": adapter.model.model_id,
        "domain": domain_slug, "run_index": run_index,
    }, FAILURES_JSONL)
```

**What is lost:** The `context` dict passed to `append_failure` has only three cell-identity fields. No verbatim data from any step is included.

**Root cause:** `run_informant` does not return partial results on exception — it raises. When it raises, `collect_single_pass` has no access to `freelist_record`, `pilesort_record`, or the last `result` from any adapter call. The exception carries only the error message, not the session bytes.

**T4 evidence:** All 23 T4 failure entries have `["timestamp", "error_type", "error_message", "context"]` only.

**Proposed fix scope (for #23):** `run_informant` should catch exceptions from each step internally, accumulate whatever completed, and re-raise a typed exception that carries the partial session. Alternatively, `collect_single_pass` can be given a partial-capture mechanism that `run_informant` populates before raising. The cleanest design: `run_informant` wraps each step await in a try/except, stores the result on a mutable context object, and raises a `PartialSessionError(partial_freelist, partial_pilesort, error)` so `collect_single_pass` can call `append_failure` with the partial verbatim. See §7 for the concrete bug list.

**Schema implication:** `failures.jsonl` entry needs `prompt_verbatim`, `response_verbatim`, `thinking_verbatim`, `stop_reason` at the top level for the failing step, plus a `partial_session` object for steps that completed before the failure.

---

### Gap B: `collect_two_pass` and `collect_baseline` have the same outer-catch problem (coarser)

**File:line:** `scripts/collect.py:253–259` (`collect_two_pass`), `collect.py:397–403` (`collect_baseline`)

Both have a single outer `try/except` around the entire `run_two_pass` / `run_baseline_sort` call. These runners internally call `run_pile_sort` and `run_pile_interview` in loops. If any individual sort/interview step raises inside the loop, it will propagate all the way out and abort the entire pass — losing all records from that pass that had not yet been appended. The context dict passed to `append_failure` is also minimal (`{model_id, domain, mode}` or `{model_id, domain, baseline}`), missing run_index entirely.

**T4 evidence:** `two_pass` and `baseline_items` modes were not exercised in T4 (T4 used `single_pass` only). The gap is structural and will fire in Phase 4b.

**Proposed fix scope (for #23):** Move the per-iteration try/except inside `run_two_pass`/`run_baseline_sort` so individual sort failures do not abort the whole pass. This mirrors the already-correct structure in `collect_single_pass` where each `run_informant` call has its own try/except. The runner-level fix follows from Gap A: if `run_pile_sort` re-raises a `PartialSessionError`, the outer loops can catch it per-iteration and call `append_failure` with the partial verbatim.

---

### Gap C: `run_pile_sort` discards retry responses

**File:line:** `packages/cdb_collect/cdb_collect/protocol/pile_sort.py:225–255`

The retry loop calls `adapter.complete()` up to `_MAX_PARSE_RETRIES=3` times. Each call returns a `result: AdapterResult` with `result.text` (the raw response). When `parse_pile_sort` raises `ValueError`, `last_error` is set and the loop continues. After exhaustion, the final `ValueError` is raised but **only the error message is included**. The `result.text` from the last attempt (and from all prior attempts) is discarded. This means even if an analyst wanted to inspect what Gemini actually returned on each of the 3 attempts, that information is not in failures.jsonl.

**T4 evidence:** Gemini failures show `"Could not extract valid JSON from response: "` — the empty string after the colon is the full `result.text` from the final attempt. It was available in `run_pile_sort` local scope at line 253 when the raise happened.

**Proposed fix scope (for #23):** `run_pile_sort` should attach the final `result` (or all retry results) to the raised exception — e.g., as an attribute on a custom `PileSortParseError`. The caller then extracts `result.text`, `result.thinking_text`, and `result.stop_reason` for inclusion in the `failures.jsonl` entry.

---

## §4 T4 Forensic Pass

**Expected:** 12 models × 2 domains × 5 runs = 120 sessions.

**Accounting:**
- `informants.jsonl` (T4 models only): **97 records**
- `failures.jsonl` (T4 models only): **23 entries**
- **Total accounted: 120. Zero unaccounted sessions.**

Note: `informants.jsonl` contains 101 total lines; 4 of these are from the phi-4 T3 canary (`microsoft/phi-4`, family domain), which is not in the T4 12-model slate. `failures.jsonl` contains 29 total lines; 6 are phi-4 T3 canary entries.

**T4 cell breakdown:**

| Model | Domain | informants.jsonl | failures.jsonl | qa_passed | Notes |
|---|---|---|---|---|---|
| claude-opus-4-6 | family | 5 | 0 | 5 | OK |
| claude-opus-4-6 | holidays | 5 | 0 | 5 | OK |
| claude-sonnet-4-6 | family | 5 | 0 | 5 | OK |
| claude-sonnet-4-6 | holidays | 5 | 0 | 5 | OK |
| deepseek/deepseek-v3.2 | family | 5 | 0 | 5 | OK |
| deepseek/deepseek-v3.2 | holidays | 5 | 0 | 5 | OK |
| google/gemini-2.5-pro | family | 0 | 5 | — | GAP A/B/C: step 1 verbatim lost |
| google/gemini-2.5-pro | holidays | 0 | 5 | — | GAP A/B/C: step 1 verbatim lost |
| meta-llama/llama-4-maverick | family | 3 | 2 | 2 | 2 parse failures (large items-missing set) |
| meta-llama/llama-4-maverick | holidays | 3 | 2 | 3 | 2 parse failures (large items-missing set) |
| mistralai/mistral-large-2512 | family | 5 | 0 | 5 | OK |
| mistralai/mistral-large-2512 | holidays | 5 | 0 | 5 | OK |
| mistralai/mistral-small-2603 | family | 5 | 0 | 5 | OK |
| mistralai/mistral-small-2603 | holidays | 4 | 1 | 1 | 1 parse failure (items-missing) |
| openai/gpt-5.4 | family | 5 | 0 | 5 | OK |
| openai/gpt-5.4 | holidays | 5 | 0 | 5 | OK |
| openai/gpt-5.4-mini | family | 3 | 2 | 3 | 2 truncated-JSON parse failures |
| openai/gpt-5.4-mini | holidays | 5 | 0 | 4 | OK (1 QA fail stays in informants.jsonl) |
| qwen/qwen3.6-plus | family | 5 | 0 | 0 | All QA fail (latency+tokens); verbatim present |
| qwen/qwen3.6-plus | holidays | 5 | 0 | 0 | All QA fail (latency+tokens); verbatim present |
| x-ai/grok-4 | family | 5 | 0 | 2 | 3 QA fail (latency); verbatim present |
| x-ai/grok-4 | holidays | 5 | 0 | 0 | All QA fail (latency); verbatim present |
| z-ai/glm-5.1 | family | 3 | 2 | 0 | 2 parse failures; 3 written with empty piles |
| z-ai/glm-5.1 | holidays | 1 | 4 | 0 | 4 parse failures; 1 written with minimal data |

**Verbatim loss observed in T4:**
- 23 failures.jsonl entries have zero verbatim (Gap A). Of these, all 23 are `ValueError` (parse failures) where step 1 completed but its verbatim was not captured.
- Specifically: 10 Gemini entries (step 1 completed, step 2 empty response), 6 GLM entries (step 1 completed, step 2 empty response), 4 Llama entries (step 1 completed, step 2 large-items-missing), 2 GPT-5.4-mini entries (step 1 completed, step 2 truncated JSON), 1 Mistral-small entry (step 1 completed, step 2 items-missing).

**Records in informants.jsonl with verbatim present but qa_passed=False:** 27 records total. All have complete verbatim — this is working correctly (Class 2).

---

## §5 Schema Implications for #24

The Architect's ruling (verdict doc §Stream A) specified: add `prompt_verbatim`, `response_verbatim`, `thinking_verbatim`, `stop_reason`, and `partial_session` (with completed step payloads) to failures.jsonl entries.

This audit refines that shape as follows:

**Confirmed necessary (Architect's ruling holds):**
- Top-level `prompt_verbatim: str` — the prompt sent to the step that failed (e.g., the pile_sort prompt for Gemini runs; or the freelist prompt for HTTP 400 runs)
- Top-level `response_verbatim: str` — the raw response text from the failing step (empty string `""` for Gemini/GLM empty-response cases)
- Top-level `thinking_verbatim: str` — thinking trace from the failing step if the adapter surfaces it (empty string for most cases; non-empty for Anthropic extended thinking)
- Top-level `stop_reason: str` — the provider stop reason for the failing step (e.g., `"STOP"`, `"MAX_TOKENS"`, `"unknown"`)
- Top-level `partial_session: object` — completed steps before the failure

**Refined shape for `partial_session`:**

```json
{
  "partial_session": {
    "freelist": {
      "prompt_verbatim": "...",
      "response_verbatim": "...",
      "thinking_verbatim": "...",
      "stop_reason": "...",
      "parsed_items": [],
      "input_tokens": 0,
      "output_tokens": 0,
      "latency_ms": 0
    },
    "pile_sort": null,
    "interview": null
  }
}
```

Each step key is `null` if not reached. For Class 3 (step 2 fails), `freelist` is populated and `pile_sort`/`interview` are null.

**Additional finding not anticipated by the Architect's shape — retry attempt log:**

Gap C (§3) shows that `run_pile_sort` retries up to 3 times and discards intermediate responses. For diagnosing why Gemini returned empty on all 3 attempts, it would be valuable to capture each retry's `response_verbatim`. The Architect's `response_verbatim` (singular) covers the final attempt only.

**Recommendation:** Add an optional `retry_attempts: list[{response_verbatim, stop_reason, error_message}]` field to the failures.jsonl entry for parse-retry scenarios. This is not strictly required by the Architect's ruling but is a meaningful addition for the "dashboard failure-display surface" use case (Stream C). **Surface this to the Architect for ruling before #24 implementation.**

**No new schema types are needed.** The Architect explicitly ruled against promoting refused-HTTP-200 cases to a new type. The refined shape above can be represented as an expanded `context` dict in `append_failure`, or as a new first-class field alongside `context`. The latter is cleaner for `DATA_DICTIONARY.md` — surface to Architect for ruling on the key name (`partial_session` at top level vs. inside `context`).

---

## §6 Summary Table

| Outcome class | Lands in | prompt_verbatim | response_verbatim | thinking_verbatim | Gap? | Fix task |
|---|---|---|---|---|---|---|
| Success, all 3 steps, QA pass | informants.jsonl | ✓ | ✓ | ✓ | OK | — |
| Success, all 3 steps, QA fail | informants.jsonl | ✓ | ✓ | ✓ | OK | — |
| Step 2 parse fail (empty response) | failures.jsonl | ✗ | ✗ | ✗ | **GAP** | #23, #24 |
| Step 2 parse fail (truncated JSON) | failures.jsonl | ✗ | ✗ | ✗ | **GAP** | #23, #24 |
| Step 2 parse fail (items-missing) | failures.jsonl | ✗ | ✗ | ✗ | **GAP** | #23, #24 |
| HTTP 4xx at step 1 (adapter error) | failures.jsonl | ✗ | ✗ | ✗ | **GAP** | #23, #24 |
| HTTP 4xx at step 2+ (adapter error) | failures.jsonl | ✗ | ✗ | ✗ | **GAP** | #23, #24 |
| Adapter timeout (any step) | failures.jsonl | ✗ | ✗ | ✗ | **GAP** | #23, #24 |
| HTTP 200, empty body → parse fail | failures.jsonl | ✗ | ✗ | ✗ | **GAP** | #23, #24 |
| Streaming cut mid-response | N/A | N/A | N/A | N/A | OK (not used) | — |
| two_pass / baseline outer exception | failures.jsonl | ✗ | ✗ | ✗ | **GAP** | #23, #24 |

---

## §7 Recommendations for #23

The following coder-sized bugs should be fixed in task #23. Each is bounded to a single file and does not require schema changes in `cdb_core/schemas.py` (the schema changes are task #24).

**Bug 1 — `runner.py:run_informant` does not preserve partial step results on exception**

- **File:** `packages/cdb_collect/cdb_collect/runner.py`
- **Bug:** Lines 309–341. Sequential awaits with no per-step exception handling. If step 2 raises, step 1's `freelist_record` (and `freelist_result`) are lost. If step 3 raises, both `freelist_record` and `pilesort_record` are lost.
- **Minimal fix:** Introduce a `PartialSessionError` exception class that carries `(freelist_record_or_none, pilesort_record_or_none, failed_step_name, underlying_exception)`. Wrap each step await in a try/except; on exception, raise `PartialSessionError` with whatever was collected. `collect_single_pass` catches `PartialSessionError` and calls `append_failure` with the partial fields.
- **Schema implication:** Requires #24 to expand `append_failure` and `failures.jsonl` shape.

**Bug 2 — `pile_sort.py:run_pile_sort` discards retry responses**

- **File:** `packages/cdb_collect/cdb_collect/protocol/pile_sort.py`
- **Bug:** Lines 225–255. The `result` local variable from the final retry is in scope when `ValueError` is raised at line 253, but the raised exception does not carry it. The caller has no access to the raw response text.
- **Minimal fix:** Create `PileSortParseError(ValueError)` that carries `final_result: AdapterResult`. Change line 253 to `raise PileSortParseError(...) from last_error` with `final_result=result` attached. `run_informant` can then access `error.final_result.text` etc. when handling the exception.
- **Schema implication:** `response_verbatim`, `thinking_verbatim`, and `stop_reason` for the failing step can now be captured in the failures.jsonl entry.

**Bug 3 — `collect.py:collect_two_pass` and `collect_baseline` use a single outer try/except**

- **File:** `scripts/collect.py`
- **Bug:** Lines 246–259 (`collect_two_pass`) and lines 389–403 (`collect_baseline`). A single exception in any iteration of `run_two_pass` or `run_baseline_sort` aborts the entire pass. Records from completed iterations are already written (because `run_two_pass` appends internally to `all_informant_records`), but any in-progress iteration is lost without verbatim capture. Also, the `context` dict lacks `run_index`.
- **Minimal fix:** Move the per-iteration try/except inside `run_two_pass`/`run_baseline_sort` (mirroring `collect_single_pass`'s per-run pattern). Add `run_index` to the failure context dict.
- **Schema implication:** None beyond Bug 1/2 fixes.

**Bug 4 — `collect_single_pass` failure context missing `prompt_verbatim` and partial steps**

- **File:** `scripts/collect.py:217–220`
- **Bug:** `append_failure` is called with `context = {model_id, domain, run_index}` only. After Bug 1 is fixed, the partial session is available.
- **Minimal fix:** Update the `append_failure` call to pass the partial step records from the `PartialSessionError`. Requires the `append_failure` API in `jsonl.py` to be extended to accept `partial_session`, `prompt_verbatim`, `response_verbatim`, `thinking_verbatim`, `stop_reason` (task #24 scope).

**Bug 5 — `jsonl.py:append_failure` schema is too narrow**

- **File:** `packages/cdb_collect/cdb_collect/jsonl.py`
- **Bug:** Lines 44–56. `append_failure` only writes `{timestamp, error_type, error_message, context}`. The Architect's ruling and this audit establish that `prompt_verbatim`, `response_verbatim`, `thinking_verbatim`, `stop_reason`, and `partial_session` are required.
- **Minimal fix:** Add keyword arguments to `append_failure` for the new fields; include them in the serialized entry when non-None. This is primarily a #24 task (schema + DATA_DICTIONARY.md update), but the function signature change is part of the gap-close code.

---

## Deviations from Architect Plan

**None.** The audit confirmed all four items in the Architect's §Stream A checklist:
1. `collect_single_pass` exception path confirmed (confirms Architect's "most likely gap").
2. `run_informant` three-step local-variable loss confirmed (Architect root-cause hypothesis is correct).
3. Adapter empty-body handling audited per-adapter (Gap A applies to all; no streaming in any adapter).
4. Parser layer audited: no parser raises after verbatim is captured in the step record — the gap is at the `run_pile_sort` retry boundary before the `PileSortRecord` is constructed.

**One finding beyond the Architect's shape (potential #24 scope addition):** The retry-attempt log (§5) captures multiple responses per session that could be valuable for diagnosis. Surface to Architect before #24.

**T4 session count clarification:** The open-items doc (`2026-04-23-phase4a-open-items.md`) references "101/120 records." The correct reading is: 97 T4 records + 23 T4 failures = 120 T4 sessions fully accounted. The total 101 in informants.jsonl includes 4 phi-4 T3 canary records from a prior run.

---

*End of audit report. Task #19 complete. Code gap fixes are task #23. Schema expansion is task #24.*
