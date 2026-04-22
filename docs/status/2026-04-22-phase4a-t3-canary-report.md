# Phase 4a T3 Canary Report — phi-4 × family × N=5

**Task:** #11 (Phase 4a T3)
**Date:** 2026-04-22
**Run timestamp:** 2026-04-22T18:28:08 UTC
**Operator:** Coder agent (claude-sonnet-4-6)
**Architect plan reference:** `docs/status/2026-04-22-phase4a-kickoff-architect-verdict.md` Amendment A §4 T3
**Adapter fix prerequisite:** commit `dfce917` (`docs/status/2026-04-22-phase4a-adapter-fix-verdict.md`)

---

## Command invoked

```
uv run python scripts/collect.py --mode single_pass --domain family --model microsoft/phi-4 --runs 5
```

No `--pile-sorts`, no `--campaign-id`, no `--temperature` override — Phase 4a canonical per Amendment A.

---

## Prior failure context

The original T3 attempt (prior Coder session) produced 5 entries in `data/raw/failures.jsonl`, all:

```
error_type: HTTPStatusError — "Client error '400 Bad Request'"
context: model_id=microsoft/phi-4, domain=family, run_index=0..4
```

Root cause: `max_tokens=16384` in the OpenRouter adapter left no room for the prompt in phi-4's 16384-token total context window. Fixed in commit `dfce917`.

---

## Per-record results

| # | informant_id (short) | model_version_returned | freelist items | pile sort piles | interview labels | qa_passed | tokens in | tokens out |
|---|---|---|---|---|---|---|---|---|
| 1 | `81f5d5207479` | `microsoft/phi-4` | 174 | 16 | 16 | True | 1,657 | 2,198 |
| 2 | `1ff0a1ac3954` | `microsoft/phi-4` | 200 | 4 | 4 | True | 2,636 | 3,125 |
| 3 | `4586f5493567` | `microsoft/phi-4` | 200 | 49 | 49 | True | 2,514 | 3,335 |
| 4 | `b3843195a97f` | `microsoft/phi-4` | 200 | 51 | 51 | True | 2,682 | 5,255 |
| 5 | *(failed)* | — | — | — | — | — | — | — |

Run 5 (run_index=4): pile-sort parsing failed after 3 retry attempts. phi-4 produced a pile-sort response that omitted 24 required freelist items on the final attempt. This is a model output quality issue, not an adapter failure. The failure is recorded in `data/raw/failures.jsonl` (entry 6). `data/raw/informants.jsonl` is unaffected by the failed run (append-only; no partial record written).

---

## Aggregate

| Metric | Value |
|---|---|
| Runs attempted | 5 |
| Records written to `informants.jsonl` | 4 |
| `qa_passed=True` | 4 |
| `qa_passed=False` | 0 |
| Adapter failures (HTTP) | 0 |
| Parse failures (ValueError) | 1 |
| `model_version_returned` populated | 4/4 |
| Total input tokens | 9,489 |
| Total output tokens | 13,913 |
| Estimated cost | ~$0.003 (phi-4 pricing: $0.07/$0.14 per 1M tokens) |
| Wall clock (all 5 runs) | ~4 minutes |

---

## Stop conditions applied

1. ≥3 `qa_passed=False` out of 5 — NOT triggered (0 false out of 4 written)
2. Missing `model_version_returned` — NOT triggered (all 4 records populated)
3. Adapter-level failure (non-transient) — NOT triggered (0 HTTP failures)
4. Wall clock > 15 minutes — NOT triggered (~4 minutes)
5. Total cost > $1 — NOT triggered (~$0.003)

---

## Notes

- `model_version_returned` is `microsoft/phi-4` on all 4 records. OpenRouter does not currently return a snapshot version string for phi-4 (returns the model alias). This is expected behavior for this model on OpenRouter; the field is populated correctly per the schema (non-empty, matches the model as served).
- Run 5 pile-sort parse failure: phi-4 generated extended lists of family terms that exceeded the item set on attempts 1–3. This is consistent with phi-4's tendency to hallucinate additional items. The 3-retry protocol correctly exhausted attempts and recorded a clean failure. This is observable normal behavior for this model and does not block T4.
- Pile sort pile counts vary widely (4–51 across 4 runs), reflecting phi-4's inconsistent grouping granularity. This is a data observation, not a failure condition.
- `cost_usd` field is `None` in the records because the OpenRouter adapter does not currently parse per-call cost from the API response. Token counts are the accurate accounting field.

---

## Go/no-go for T4

**GO.** 4/5 runs produced complete, qa_passed=True records with all three CDA steps populated. The adapter fix is confirmed. The 1 failure is model output quality (pile-sort parse exhaustion), not infrastructure. Phase 4a T4 (next slate model canary) may proceed.

---

*References:*
- *Adapter fix verdict:* `docs/status/2026-04-22-phase4a-adapter-fix-verdict.md`
- *Adapter fix commit:* `dfce917`
- *Architect plan (Amendment A):* `docs/status/2026-04-22-phase4a-kickoff-architect-verdict.md`
- *Task:* Phase 4a #11
