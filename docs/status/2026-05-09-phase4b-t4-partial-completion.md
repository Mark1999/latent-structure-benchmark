# Phase 4b T4 — Partial Completion Status

**Date:** 2026-05-09
**Campaign tag:** `phase4b-real-2026-05-08` (collection ran 2026-05-08 15:48 UTC → 2026-05-09 02:21 UTC; orchestrator-stopped at 60.6% triple coverage)
**Status:** Partial corpus accepted by Mark on 2026-05-09; 7 models deferred to follow-up campaign.

---

## §1. What was collected

| Metric | Value |
|---|---|
| Informant cells (campaign_id=phase4b-real-2026-05-08) | 1118 |
| Stray cells (campaign_id=phase4b-real-2026-05-09 from a 30s mis-launch) | 1 |
| Hard failures (failures.jsonl) | 5 |
| Triples at 5/5 (target 360) | 218 |
| Coverage | 60.6% |
| Duplicate tuples | 1 (claude-opus-4-6 v1_s1 family run=0 — 2 cells) |

## §2. Per-model completion (target 90 cells = 9 variants × 5 runs × 2 domains)

**COMPLETE (9 models, ≥90 cells):**
- claude-opus-4-6 (91 — has the 1 duplicate)
- claude-sonnet-4-6 (90)
- claude-opus-4-5 (90)
- openai/gpt-5.4 (91 — includes the 1 phase4b-real-2026-05-09 stray)
- openai/gpt-5.4-mini (90)
- openai/gpt-5.2 (90)
- google/gemini-2.5-flash (90)
- x-ai/grok-4.20 (90)
- mistralai/mistral-small-2603 (90)

**PARTIAL (4 models):**
- google/gemini-2.5-pro (88 — 2 cells short)
- meta-llama/llama-4-maverick (87 — 3 cells short)
- x-ai/grok-4 (88 — 2 cells short)
- qwen/qwen3.6-plus (44 — 46 cells short, ~50% done)

**NOT STARTED (7 models, all OpenRouter):**
- deepseek/deepseek-v3.2
- z-ai/glm-5.1
- microsoft/phi-4
- meta-llama/llama-4-scout
- mistralai/mistral-large-2512
- cohere/command-a
- google/gemma-4-26b-a4b-it

## §3. Why the campaign stopped at 60.6%

Three structural issues surfaced at runtime:

1. **OpenRouter single-thread bottleneck** — the script (`scripts/run_phase4b_variance.py` pre-`fc1ccd1`) used one worker per provider. OpenRouter serves 10 of 20 models, so all OpenRouter cells funneled through one thread. Anthropic, OpenAI, Google, xAI workers finished early and went idle while OpenRouter ground through cells one at a time at ~2-5 min each. Projected ~24h to complete the OpenRouter tail.
2. **Parallelization fix landed at commit `fc1ccd1`** — `PROVIDER_WORKERS={"openrouter": 4, ...}` with sleep math adjusted to keep aggregate RPM at the configured ceiling.
3. **Resume logic partial defect** (forward-carry) — script reports correct "Completed triples at start of run: N" but appears to re-dispatch the first cell of complete triples in some cases. Surfaced as 1 observed duplicate during a 5-min post-fix relaunch. Not chased to root cause; deferred.

Plus one operational issue: SIGINT handling on the long-running script appears to be slow (drain took ~3 hours on the 23:30 SIGINT before workers stopped logging). Force-kill required to actually stop.

## §4. Decision

Mark accepted the partial corpus on 2026-05-09. Rationale: 13 of 20 models with meaningful coverage is a usable G1 stability sample; the 7 not-started OpenRouter models can be backfilled in a separate, scoped follow-up campaign with the parallelization fix already live. Continuing the original campaign was projected to take more time-orchestration cost than starting fresh.

Per failures-as-findings posture, the corpus as-is is research data. The 1 stray `phase4b-real-2026-05-09` cell and the 1 duplicate are also data; they're documented here and the analysis layer can dedup at compute time.

## §5. What's next

- **A follow-up campaign** to fill the 7 not-started OpenRouter models (~630 cells) plus the partial tails (~53 cells = 2 + 3 + 2 + 46). Total ~683 cells, projected at the parallelized OpenRouter rate of ~5-8 min/cell (single thread × 4 workers serving 7 models in flight = ~3-5 cells/min) ≈ **~3-4 hours** wall-clock.
- A separate `campaign_id` (e.g., `phase4b-real-followup-2026-05-{MM}`) so the follow-up's cells are auditable as a distinct collection event.
- The resume bug should be investigated before launching the follow-up — even with parallelism, re-dispatching completed triples wastes provider quota.

## §6. Other artifacts produced this session

- **OpenRouter parallelization fix** (`fc1ccd1`): `PROVIDER_WORKERS` config, N-sentinel queue draining, `(60/RPM × N + 0.1)` sleep formula. Reviewer + Tester PASS at `2026-05-09-openrouter-parallel-fix-{reviewer,tester}-verdict.md`.
- **Preflight 429-detection fix** (`6f88f68`): walks exception cause chain; detects `insufficient_quota`, `429`, `rate_limit_exceeded`, `overloaded`, `RESOURCE_EXHAUSTED` markers. Reviewer + Tester PASS at `2026-05-08-preflight-429-fix-{reviewer,tester}-verdict.md`.
- **Spend-cap removal** (SC-T1 through SC-T5, `cf555b1` through `0e3590c`): removed `CDB_MAX_SPEND_USD` from active code, added CI grep regression check, doctrinal updates to ARCHITECTURE.md §6.2 + CLAUDE.md rule 14 + SECURITY_AND_HARDENING.md R13.

## §7. Forward-carry items

| Item | Notes |
|---|---|
| Resume-logic duplicate-dispatch bug | 1 duplicate observed; root cause not investigated. Deferred. |
| 7 OpenRouter models not started | deepseek-v3.2, glm-5.1, phi-4, llama-4-scout, mistral-large-2512, cohere/command-a, gemma-4-26b. |
| Tail backfill (4 models partial) | gemini-2.5-pro (-2), llama-4-maverick (-3), grok-4 (-2), qwen3.6-plus (-46). |
| SIGINT drain latency | Long-running campaign workers don't honor SIGINT promptly. Force-kill needed. Investigate whether a non-LLM-side improvement is possible. |
| 1 stray phase4b-real-2026-05-09 cell | Append-only invariant preserved; analysis layer should filter/merge by campaign_id substring carefully. |
| 1 duplicate (claude-opus-4-6 v1_s1 family run=0) | Pick one at analysis time; document choice. |
