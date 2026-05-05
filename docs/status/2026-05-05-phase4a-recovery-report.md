# Phase 4a Recovery — Report

**Date:** 2026-05-05
**Author:** Recovery campaign orchestration
**Campaign ID:** `phase4a-recovery-2026-05-05`
**Companion docs:**
- Architect plan: `docs/status/2026-05-05-phase4a-recovery-architect-plan.md`
- CDA SME verdict (PASS-WITH-NOTES, R1–R6 binding): `docs/status/2026-05-05-phase4a-recovery-cda-sme-verdict.md`
- R1 Reviewer + Tester verdicts: `docs/status/2026-05-05-phase4a-recovery-r1-reviewer-verdict.md`, `docs/status/2026-05-05-phase4a-recovery-r1-tester-verdict.md`
- Predecessor (Task #16): `docs/status/2026-05-04-task-16-architect-plan.md`, `cda-sme-verdict.md`
- Predecessor probe (Stage 1.7): `scripts/probe_openrouter_fullcycle_2026_05_05.py` (commit `bef7660`)

---

## Framing — what this campaign is

This recovery campaign is an **instrument event**, not a model-level fix. The 20 cells targeted here failed during Phase 4a (2026-04-22) under a `max_output_tokens=4096` configuration that prevented reasoning-heavy models from producing visible output before exhausting the cap. Task #16 (commits `7f8f7f7` + `de3dd7e`) corrected the instrument by raising the cap to 16384 and capturing `thoughts_token_count` on every step. With the corrected instrument, the 20 cells were recollected on 2026-05-05.

The recovered records **replace as authoritative for the cell** (per SME binding note R1). They do not erase or supersede the historical failure rows in `data/raw/failures.jsonl` — those remain in place for the audit trail, but the recovered records are the analytical source-of-truth for those (model, domain, run_index) tuples going forward.

The framing is mechanical-instrument-event. None of the recovered records contain methodology claims about the models. Note K disposition is gated by SME binding note S5 from the Task #16 verdict; that re-classification is the future T4-redo task and is not part of this recovery.

---

## §1 — Outcome summary

| Metric | Value |
|---|---|
| Target cells | **20** (Gemini ×10 + glm-5.1 ×6 + llama-maverick ×4) |
| Recovered (PASS) | **20 / 20 = 100.0%** |
| Recovery-failed | 0 |
| Already-recovered (idempotence skip) | 0 |
| Out-of-scope skipped | 0 |
| Wall-clock time | ~60 minutes (04:35:11 → 05:35:51 UTC) |
| Cost (actual, derived from registry pricing) | **~$1.29** (vs. $5–8 projected) |

**Recovery rate exceeded SME R6 threshold (≥80%).** No methodology re-routing required.

---

## §2 — Per-cell outcomes

All 20 cells produced valid `InformantRecord`s. 3 cells used both retry attempts (intermittent parse failures on attempt 1, recovered on attempt 2). 17 cells passed on attempt 1.

| # | Model | Domain | Run | Outcome | Note |
|---|---|---|---:|---|---|
| 1 | google/gemini-2.5-pro | family | 0 | ✅ PASS attempt 1 | — |
| 2 | google/gemini-2.5-pro | family | 1 | ✅ PASS attempt 1 | — |
| 3 | google/gemini-2.5-pro | family | 2 | ✅ PASS attempt 1 | — |
| 4 | google/gemini-2.5-pro | family | 3 | ✅ PASS attempt 1 | — |
| 5 | google/gemini-2.5-pro | family | 4 | ✅ PASS attempt 1 | — |
| 6 | google/gemini-2.5-pro | holidays | 0 | ✅ PASS attempt 1 | — |
| 7 | google/gemini-2.5-pro | holidays | 1 | ✅ PASS attempt 1 | — |
| 8 | google/gemini-2.5-pro | holidays | 2 | ✅ PASS attempt 1 | — |
| 9 | google/gemini-2.5-pro | holidays | 3 | ✅ PASS attempt 1 | — |
| 10 | google/gemini-2.5-pro | holidays | 4 | ✅ PASS attempt 2 | Attempt 1 raised `Each pile must be a list, got <class 'dict'>` (pile-sort parser saw a dict variant); attempt 2 produced standard list-of-lists |
| 11 | meta-llama/llama-4-maverick | family | 1 | ✅ PASS attempt 1 | — |
| 12 | meta-llama/llama-4-maverick | family | 4 | ✅ PASS attempt 1 | — |
| 13 | meta-llama/llama-4-maverick | holidays | 0 | ✅ PASS attempt 1 | — |
| 14 | meta-llama/llama-4-maverick | holidays | 1 | ✅ PASS attempt 2 | Attempt 1 raised `Items missing from pile sort` (29 items dropped — same coverage shape Stage 1.7 family #5 saw, but here recovered on retry) |
| 15 | z-ai/glm-5.1 | family | 1 | ✅ PASS attempt 1 | — |
| 16 | z-ai/glm-5.1 | family | 3 | ✅ PASS attempt 1 | — |
| 17 | z-ai/glm-5.1 | holidays | 0 | ✅ PASS attempt 1 | — |
| 18 | z-ai/glm-5.1 | holidays | 2 | ✅ PASS attempt 1 | — |
| 19 | z-ai/glm-5.1 | holidays | 3 | ✅ PASS attempt 1 | — |
| 20 | z-ai/glm-5.1 | holidays | 4 | ✅ PASS attempt 2 | Attempt 1 raised `Expecting value: line 783 column 1 (char 4301)` (JSON parse mid-output truncation); attempt 2 produced parseable JSON |

### Retry pattern interpretation

The 3 retry incidents (15% retry rate) all recovered cleanly on attempt 2. Two were transient JSON-formatting variations (cells 10, 20); one was the coverage-failure shape that Stage 1.7 saw as deterministic on llama-maverick family #5 but here showed up as non-deterministic on holidays #1. This suggests the residual ~10% from Stage 1.7 is **retry-able rather than model-deterministic**, and the SME-confirmed 2-attempt budget (Q2 in the recovery plan) is well-calibrated.

---

## §3 — Cost reconciliation

Projection (Architect plan §2 R1): $5–8 USD.
Actual (derived from per-step `input_tokens`, `output_tokens`, `thoughts_token_count` × registry pricing):

| Model | Input tokens | Output tokens | Thoughts tokens | $/M in | $/M out | Cost |
|---|---:|---:|---:|---:|---:|---:|
| google/gemini-2.5-pro | 22,040 | 34,042 | 27,215 | $1.25 | $10.00 | **$0.64** |
| z-ai/glm-5.1 | 12,794 | 109,947 | 90,861 | $0.95 | $3.15 | **$0.64** |
| meta-llama/llama-4-maverick | 8,698 | 14,113 | 0 | $0.15 | $0.60 | **$0.01** |
| **Total** | **43,532** | **158,102** | **118,076** | — | — | **~$1.29** |

Actual spend was ~16% of the lower projection bound and ~26% of the average projection. Two factors pushed it under:

1. Gemini pricing applies thinking tokens at the output rate ($10/M), but this run's Gemini reasoning was modest (avg 2,700 thoughts tokens per cell, much lower than the 6,000+ Stage 1.5b probe burned).
2. llama-maverick has no exposed reasoning tokens; its cost is dominated by the much cheaper visible-output path.

Hard-stop guard `CDB_MAX_SPEND_USD=15` was set as a session export per the plan — never approached.

The actual cost is well within the standing $10/probe budget and well under 1% of the $300/mo cap (`ARCHITECTURE.md` §6.2).

---

## §4 — Corpus state after recovery

`data/raw/informants.jsonl` post-recovery (verified by direct read):

- 20 new lines appended
- Each carries `qa_notes` containing the substring `campaign_id=phase4a-recovery-2026-05-05`
- All 20 (model, domain, run_index) tuples match exactly the disposition table in the Architect plan §1
- All 20 records are valid `InformantRecord` instances per Pydantic v0.1.11 schema
- `freelist.thoughts_token_count`, `pile_sort.thoughts_token_count`, `interview.thoughts_token_count` populated where the provider exposes reasoning tokens (Gemini, glm-5.1)

`data/raw/failures.jsonl` post-recovery:

- No new lines (zero `recovery_failed` cells)
- Historical 29 Phase 4a failure rows untouched (append-only invariant preserved)

The 9 cells that remain in their original failed state per the Architect plan's out-of-scope disposition:

- `microsoft/phi-4` × 6 (5 HTTPStatusError + 1 ValueError) — separate adapter issue, deferred
- `openai/gpt-5.4-mini` × 2 (family runs 0 and 2) — Stage 1.5b probe couldn't reproduce a cap-related failure; root cause not max_tokens; deferred
- `mistralai/mistral-small-2603` × 1 (holidays run 3) — same as gpt-5.4-mini; deferred

---

## §5 — `build_db.py` rerun deferment

Per SME binding note R5, the SQLite open-bundle build (`data/open_bundle/lsb.sqlite`) is **not** regenerated as part of this campaign. The bundle is now stale relative to `informants.jsonl` (contains 20 fewer rows than the canonical JSONL). Architect schedules the build_db.py rerun as a separate ops task. Per the Task #16 SME verdict, this is acceptable because the open bundle does not have a public DOI and is internal-only at the current Phase 4 state.

Command for the future ops task:
```
uv run python scripts/build_db.py data/raw/informants.jsonl data/open_bundle/lsb.sqlite
```

---

## §6 — What the recovery does not change

Per the SME ruling on Q5 (recovery is corpus-modification, not corpus-interpretation), this campaign:

- Does NOT reframe Note K. The Note K methodology re-disposition is gated by SME binding note S5 from the Task #16 verdict and is the work of the future T4-redo Architect task.
- Does NOT modify the v1 prompt templates.
- Does NOT modify the CDA protocol.
- Does NOT modify the analytical layer (`cdb_analyze`).
- Does NOT modify the schemas (Pydantic v0.1.11 already accommodates the recovered records via the Task 16.B additive change).

The only canonical-corpus change is the 20 appended `InformantRecord` rows in `data/raw/informants.jsonl`.

---

## §7 — Forward carry

1. **build_db.py rerun** — separate ops task, deferred per SME R5.
2. **T4 redo against recovered corpus** — the natural successor task. Gated by SME binding note S5 from the Task #16 verdict. New Architect plan + new SME PASS chain required before any methodology-page text references the recovered records analytically.
3. **gpt-5.4-mini ×2 + mistral-small ×1 unexplained failures** — separate investigation task. Stage 1.5b found these are not cap-related; root cause unknown; not addressed by this campaign.
4. **phi-4 ×6 (HTTPStatusError + ValueError)** — separate adapter task. Phi-4's 16K total context interacts badly with the new `max_tokens=16384` cap; needs per-model adaptive sizing.

---

## §8 — Verification commands

For Mark or any future reader to verify the recovery is intact:

```bash
# Confirm 20 recovery records exist with correct campaign-id
grep -c 'phase4a-recovery-2026-05-05' /opt/lsb-agent/data/raw/informants.jsonl
# Expected: 20

# Per-(model, domain, run) coverage
python3 -c "
import json
recs = [json.loads(l) for l in open('data/raw/informants.jsonl') if 'phase4a-recovery-2026-05-05' in l]
for r in recs:
    print(f\"{r['model_id']:35s} {r['domain_slug']:8s} run={r['run_index']}\")
" | sort

# No new failures from this campaign
grep -c 'phase4a-recovery-2026-05-05' /opt/lsb-agent/data/raw/failures.jsonl
# Expected: 0

# qa_check against the post-recovery corpus
uv run python scripts/qa_check.py --file data/raw/informants.jsonl
```

---

*End of recovery report. Recovery campaign closed. T4-redo unblocked at the data layer; methodology gate (S5) still in force.*
