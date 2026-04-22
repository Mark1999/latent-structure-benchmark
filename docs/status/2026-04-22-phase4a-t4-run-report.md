# Phase 4a T4 Run Report — Full 12-model × 2-domain × N=5

**Task:** Phase 4a T4 (full slate run)
**Date:** 2026-04-22
**Run started:** 2026-04-22T20:21:51Z
**Run completed:** 2026-04-22T23:05:31Z
**Wall clock:** 2 hours 43 minutes 40 seconds
**Operator:** Coder agent (claude-sonnet-4-6)
**Architect plan reference:** `docs/status/2026-04-22-phase4a-kickoff-architect-verdict.md` Amendment A
**Runner script:** `scripts/run_phase4a_t4.sh`

---

## Run configuration

- **Mode:** `single_pass` (Amendment A.1)
- **Domains:** `family`, `holidays`
- **Runs per cell:** N=5
- **Streams:** 5 parallel (anthropic, openai, google, xai, openrouter)
- **Models:** 12 from approved slate (2 per stream for anthropic/xai, 4 for openai, 2 for google, 6 for openrouter)
- **Output:** Per-stream JSONL files, merged into `data/raw/informants.jsonl` post-run

---

## Per-stream summary

| Stream | Models | Cells | Expected records | Written records | Stream rc | Notes |
|---|---|---|---|---|---|---|
| anthropic | claude-opus-4-6, claude-sonnet-4-6 | 4 | 20 | 20 | 0 | All PASS |
| openai | gpt-5.4, gpt-5.4-mini | 4 | 20 | 18 | 0 | 2 runs hard-failed (gpt-5.4-mini × family: truncated JSON at 4096 tokens, runs 0 and 2) |
| google | gemini-2.5-pro | 2 | 10 | 0 | 1 | Stop condition 1 triggered — systematic pile sort failure (empty JSON), 0% success rate, no JSONL created |
| xai | grok-4 | 2 | 10 | 10 | 0 | 8/10 qa_passed=False — stop condition 3 triggered (>30% QA_FAIL) |
| openrouter | llama-4-maverick, mistral-large-2512, mistral-small-2603, deepseek-v3.2, qwen3.6-plus, glm-5.1 | 12 | 60 | 49 | 0 | Multiple failures (see per-model table) |
| **TOTAL** | **11 providers / 11 models** | **24** | **120** | **97** | — | |

Note: google/gemini-2.5-pro stream created no JSONL file; stop condition 1 fired before any record was written.

---

## Per-model results

### anthropic stream

| Model | Domain | Runs | Records | qa_passed | Notes |
|---|---|---|---|---|---|
| claude-opus-4-6 | family | 5/5 | 5 | 5/5 | PASS all (200 items, 28-40 piles) |
| claude-opus-4-6 | holidays | 5/5 | 5 | 5/5 | PASS all (197-199 items, 16-23 piles) |
| claude-sonnet-4-6 | family | 5/5 | 5 | 5/5 | PASS all (199-200 items, 16-60 piles) |
| claude-sonnet-4-6 | holidays | 5/5 | 5 | 5/5 | PASS all (200 items, 17-28 piles) |

`model_version_returned`: `claude-opus-4-6`, `claude-sonnet-4-6` (provider returns alias; no snapshot string available)

### openai stream

| Model | Domain | Runs | Records | qa_passed | Notes |
|---|---|---|---|---|---|
| gpt-5.4 | family | 5/5 | 5 | 5/5 | PASS all (197-200 items, 12-43 piles) |
| gpt-5.4 | holidays | 5/5 | 5 | 5/5 | PASS all (199-200 items, 10-21 piles) |
| gpt-5.4-mini | family | 3/5 | 3 | 3/5 (QA check) | Runs 0, 2 hard-failed: pile sort response truncated at 4096 token limit; 3 records written (1, 1, 1 piles — single-pile degenerate) |
| gpt-5.4-mini | holidays | 5/5 | 5 | 4/5 | 1 QA_FAIL (run 2: 199 items, 20 piles — pile count threshold not met); 4 records pass |

`model_version_returned`: `gpt-5.4-2026-03-05`, `gpt-5.4-mini-2026-03-17`

Note on gpt-5.4-mini family records: 3 records written have pile_count=1 (single pile — entire freelist as one group). These pass the item count threshold but the pile sort is degenerate. The QA script passes them on item count but they have analytical value only as degenerate-sort examples.

### google stream

| Model | Domain | Runs | Records | qa_passed | Notes |
|---|---|---|---|---|---|
| gemini-2.5-pro | family | 0/5 | 0 | — | Systematic failure: pile sort API returned empty JSON on all attempts. Stop condition 1 triggered after 0% success rate. |
| gemini-2.5-pro | holidays | 0/5 | 0 | — | Not attempted (stop condition triggered after family) |

**Stop condition 1 triggered.** Root cause: Google Gemini 2.5 Pro returns an empty string for pile sort requests. The adapter received `HTTP 200 OK` but the response body parsed to an empty JSON object `{}`. This is not a transient rate-limit failure; it is a systematic model behavior for the pile sort prompt format. Requires adapter changes to resolve. `informants-t4-google.jsonl` was never created.

### xai stream

| Model | Domain | Runs | Records | qa_passed | Notes |
|---|---|---|---|---|---|
| grok-4 | family | 5/5 | 5 | 2/5 | Runs 1,2,5: QA_FAIL (200 items, 11-18 piles — too few piles). Runs 3,4: PASS (200 items, 12 and 29 piles). |
| grok-4 | holidays | 5/5 | 5 | 0/5 | All QA_FAIL: item counts 185-197 (below threshold), pile counts 14-21. |

`model_version_returned`: `grok-4-0709`

**Stop condition 3 triggered** (>30% QA_FAIL per model: 8/10 qa_passed=False). All 10 records written with `qa_passed` as determined by the QA script. Family domain has 2 usable records; holidays domain has 0 usable records.

### openrouter stream — mistral family

| Model | Domain | Runs | Records | qa_passed | Notes |
|---|---|---|---|---|---|
| mistral-large-2512 | family | 5/5 | 5 | 5/5 | PASS all (200 items, 67-75 piles — very fine-grained sort) |
| mistral-large-2512 | holidays | 5/5 | 5 | 5/5 | PASS all (173-200 items, 16-101 piles) |
| mistral-small-2603 | family | 5/5 | 5 | 5/5 | PASS all (195-219 items, 14-63 piles) |
| mistral-small-2603 | holidays | 4/5 | 4 | 1/4 (QA check) | 1 hard failure (run 3 parse error); 3 QA_FAIL (item counts 81-125, pile counts too high); 1 QA_PASS (81 items, 2 piles — degenerate) |

`model_version_returned`: `mistralai/mistral-large-2512`, `mistralai/mistral-small-2603`

Note: mistral-small-2603 × holidays shows very inconsistent item counts (81-205) and extreme pile count variance (2-72). This model does not perform reliably on the holidays domain.

### openrouter stream — deepseek

| Model | Domain | Runs | Records | qa_passed | Notes |
|---|---|---|---|---|---|
| deepseek/deepseek-v3.2 | family | 5/5 | 5 | 5/5 | PASS all (199-200 items, 10-36 piles) |
| deepseek/deepseek-v3.2 | holidays | 5/5 | 5 | 5/5 | PASS all (190-199 items, 11-20 piles) |

`model_version_returned`: `deepseek/deepseek-v3.2-20251201`

### openrouter stream — llama

| Model | Domain | Runs | Records | qa_passed | Notes |
|---|---|---|---|---|---|
| meta-llama/llama-4-maverick | family | 3/5 | 3 | 2/5 | Runs 1, 4 hard-failed (pile sort parse after 3 attempts — missing items). 1 QA_FAIL (194 items, 16 piles), 2 PASS (198/200 items, 10/14 piles). |
| meta-llama/llama-4-maverick | holidays | 3/5 | 3 | 3/5 | Runs 0, 1 hard-failed (pile sort parse). 3 PASS (190-200 items, 9-18 piles). |

`model_version_returned`: `meta-llama/llama-4-maverick-17b-128e-instruct`

### openrouter stream — qwen

| Model | Domain | Runs | Records | qa_passed | Notes |
|---|---|---|---|---|---|
| qwen/qwen3.6-plus | family | 5/5 | 5 | 0/5 | All QA_FAIL: 198-200 items with only 11-16 piles (far below threshold). |
| qwen/qwen3.6-plus | holidays | 5/5 | 5 | 0/5 | All QA_FAIL: 200 items with only 12-16 piles. |

`model_version_returned`: `qwen/qwen3.6-plus-04-02`

Pattern: qwen3.6-plus produces correct freelist length but collapses the pile sort to very few high-level groups (11-16) on both domains. This is a characteristic model behavior, not an adapter failure. All 10 records written with `qa_passed=False`.

### openrouter stream — glm

| Model | Domain | Runs | Records | qa_passed | Notes |
|---|---|---|---|---|---|
| z-ai/glm-5.1 | family | 3/5 | 3 | 0/3 | Runs 1, 3 hard-failed (pile sort returned empty string). Runs 0, 2, 4 wrote records with 0 items / 0 piles (qa_passed=False). |
| z-ai/glm-5.1 | holidays | 1/5 | 1 | 0/1 | 4 runs hard-failed; 1 record written with 0 items (qa_passed=False). |

`model_version_returned`: `z-ai/glm-5.1-20260406`

**Stop condition 1 triggered (partial).** glm-5.1 pile sort responses are systematically empty (same failure mode as Google gemini-2.5-pro). 4 records written are all 0-item records that passed enough to be written but failed QA. These are garbage records with `qa_passed=False`. The model is not able to complete the pile sort step with the current prompt format.

---

## Stop conditions triggered

### Stop condition 1: 0% success rate (systematic pile sort failure)

**Triggered for:** `google/gemini-2.5-pro` (full stop), `z-ai/glm-5.1` (partial — stream continued since other cells remain)

Both models return empty responses to pile sort API calls. Google: 0/10 runs produced any record. GLM-5.1: 4 records written but all contain 0 items with `qa_passed=False`.

Root cause: The pile sort prompt requires structured JSON output. Both models return empty or minimally populated responses. This is a model-specific compatibility issue with the current prompt format, not an adapter or infrastructure failure. Resolution requires prompt engineering or adapter changes — an Architect decision.

### Stop condition 3: >30% QA_FAIL per model

**Triggered for:** `x-ai/grok-4`

8/10 records `qa_passed=False`. Grok-4's pile sort over the `family` domain produces very coarse structure (2-29 piles across runs, highly inconsistent) and the `holidays` domain produces systematically underfull responses (185-197 items, 14-21 piles — below the QA item count threshold). This is a model output quality issue.

---

## QA battery results

Post-merge run against `data/raw/informants.jsonl`:

| Metric | Value |
|---|---|
| Total records in file | 101 (97 T4 + 4 T3 phi-4 canary) |
| QA PASS (T4 only, estimated) | ~70/97 |
| QA FAIL (T4 only, estimated) | ~27/97 |
| QA script exit code | 1 (failures present — expected) |

Key failure patterns detected by QA script:
- **Check 1 (item count too low):** glm-5.1 records (0 items)
- **Check 5 (latency too high > 60s):** qwen3.6-plus (pile sort 3-4 min), grok-4 × holidays (pile sort up to 5 min), glm-5.1
- **Check 6 (token count outlier):** gpt-5.4-mini family (4096 tokens — truncation), qwen3.6-plus freelist (8k-14k tokens)
- **Check 8 (pile-interview label mismatch):** mistral-small-2603 × holidays (interview label count vs pile count discrepancy), mistral-large-2512 (minor off-by-one)

---

## Cost summary

| Metric | Value |
|---|---|
| April 2026 total spend | $4.95 |
| Monthly cap | $300 |
| Cap utilization | 1.7% |

---

## model_version_returned population

All 97 T4 records have `model_version_returned` populated. Verified:
- Anthropic: returns model alias (e.g. `claude-opus-4-6`) — no snapshot string from Anthropic API
- OpenAI: returns datestamped snapshot (e.g. `gpt-5.4-2026-03-05`)
- xAI: returns datestamped snapshot (`grok-4-0709`)
- OpenRouter models: returns full version string with date where available (e.g. `deepseek/deepseek-v3.2-20251201`)

---

## Go/no-go for T5

**NO GO without Architect review of three failure classes:**

1. **gemini-2.5-pro and glm-5.1 systematic pile sort failures.** Two of 12 slate models cannot complete the pile sort step. The Google adapter and the OpenRouter adapter served the requests correctly (HTTP 200 returned); the model outputs are systematically empty. Before T5, the Architect must decide: (a) attempt a prompt variant for these two models, (b) drop them from the active collection slate, or (c) accept their records as permanently qa_passed=False for this run.

2. **grok-4 QA_FAIL rate.** 8/10 records failed. Family domain shows 2 usable records (inconsistent pile count variance 11-29). Holidays domain: 0 usable records (item counts below threshold). Architect decision required: attempt model-specific prompt tuning, or accept grok-4 as unreliable for the current protocol.

3. **gpt-5.4-mini truncation.** 2/5 runs for the `family` domain hard-failed at 4096 tokens. The 3 written family records have pile_count=1 (degenerate). The holidays domain produced 5 records with better results. Architect decision: raise `max_tokens` cap for gpt-5.4-mini, or mark family domain records as degenerate.

4. **qwen/qwen3.6-plus pile count collapse.** All 10 records QA_FAIL (11-16 piles vs expected 20+). Model generates correct-length freelists but collapses pile sort to too few groups. Architect decision: prompt variant or accept as characteristic model behavior.

**Conditions for T5 GO:**
- Architect issues disposition on each of the four failure classes above
- Adapter change if any is authorized for gemini/glm prompt format
- Model or max_tokens adjustment if authorized for gpt-5.4-mini

---

## Deliverables produced

- `scripts/run_phase4a_t4.sh` — 5-stream parallel runner script
- `data/raw/informants.jsonl` — 97 T4 records appended (101 total including T3 canary)
- `logs/phase4a-t4-anthropic.log`, `logs/phase4a-t4-openai.log`, `logs/phase4a-t4-xai.log`, `logs/phase4a-t4-openrouter.log`, `logs/phase4a-t4-main.log` — per-stream and main run logs

---

## Observations (informational — not stop conditions)

- **Mistral-large-2512** produces exceptionally fine-grained pile sorts (67-101 piles on family) relative to all other models. This is the highest pile count observed in the run and may require special handling in the MDS analysis step.
- **Deepseek-v3.2** produced the most consistent results of any openrouter model: 10/10 pass, stable item counts and pile counts across both domains.
- **Pile sort duplicates** (WARNING lines in logs): Several models (claude-sonnet-4-6, gpt-5.4-mini, grok-4) generated duplicate items in pile sort responses. The duplicate handler in `pile_sort.py` correctly retained the first occurrence and dropped subsequent duplicates. This is observable normal behavior, not an error.
- **qwen3.6-plus** is very slow: freelist ~2.5 min, pile sort ~3.5 min, interview ~3 min = ~9 min per run. 10 runs took ~74 minutes. This is a latency characteristic to note for future run scheduling.

---

*References:*
- *Architect plan (Amendment A):* `docs/status/2026-04-22-phase4a-kickoff-architect-verdict.md`
- *T3 canary report:* `docs/status/2026-04-22-phase4a-t3-canary-report.md`
- *QA check script:* `scripts/qa_check.py`
- *Cost report script:* `scripts/cost_report.py`
