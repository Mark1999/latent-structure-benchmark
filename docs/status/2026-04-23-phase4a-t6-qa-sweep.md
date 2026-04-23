# Phase 4a T6 — QA Sweep and Stored-vs-Rerun Reconciliation

**Date:** 2026-04-23
**Run timestamp:** 2026-04-23T14:56:10Z
**Executor:** Coder (Claude Sonnet 4.6), Linode `lsb-agent-02`
**Task spec:** `docs/status/2026-04-22-phase4a-kickoff-architect-verdict.md` §4 T6
**Preceding gate:** CDA SME T5 PASS-WITH-NOTES (GO on T6): `docs/status/2026-04-23-phase4a-t5-cda-sme-verdict.md`
**Note B source:** `docs/status/2026-04-23-decline-interview-protocol-sme-verdict.md`
**Position C precedent:** `docs/status/2026-04-22-position-c-replay-verdict.md`

---

## 1. Command invoked

```
uv run python scripts/qa_check.py --file data/raw/informants.jsonl \
  > /tmp/t6_qa_stdout.txt 2> /tmp/t6_qa_stderr.txt
```

Exit code: `1` (failures present; expected).

---

## 2. Corpus summary

| Metric | Value |
|---|---|
| Total records | 101 |
| Domain: family | 53 |
| Domain: holidays | 48 |
| Stored `qa_passed=True` | 74 |
| Stored `qa_passed=False` | 27 |
| Stored `qa_passed=None` | 0 |

**Note on T3 canary records:** `microsoft/phi-4` × `family` contributes 4 records (T3 canary run). All 4 are `qa_passed=True`. The full 12-model slate ran N=5 per (model, domain) but several cells have fewer than 5 records due to collection-time failures or partial runs (see §7 for cell-level detail).

---

## 3. Rerun results

| Metric | Value |
|---|---|
| Rerun PASS | 74 |
| Rerun FAIL (unique IDs) | 27 |
| Total records covered | 101 |
| Records missing from rerun | 0 |

---

## 4. Reconciliation: stored × rerun 2×2 matrix

|  | Rerun PASS | Rerun FAIL |
|---|---|---|
| **Stored `qa_passed=True`** | **74** | **0** |
| **Stored `qa_passed=False`** | **0** | **27** |

**Zero divergences in either direction.** All 74 stored-True records rerun PASS. All 27 stored-False records rerun FAIL.

### Note B reconciliation (SME-binding)

SME Note B (from `docs/status/2026-04-23-decline-interview-protocol-sme-verdict.md`) anticipated that the Phase 4a corpus would reproduce the stored-vs-rerun divergence observed in the shakedown replay (Position C), because Check 2 (free-list cross-run uniqueness) is a pool-aggregation check whose re-run result changes as the cohort grows.

**This divergence did not materialize on the Phase 4a corpus.** The explanation is that unlike the shakedown — where a single model (`claude-sonnet-4-6`) dominated the corpus with 54 same-(model, domain) records and drove the uniqueness ratio to 8.6% — the Phase 4a corpus distributes across 12 distinct models with N≤5 per (model, domain) cell. No cell accumulates enough same-model-same-domain siblings for Check 2 to fire: at N=5, even a perfectly repetitive free list produces 5 total items × 1 unique = 20% uniqueness, above the 15% threshold. Check 2 therefore passes uniformly for all 101 records regardless of corpus state.

**Stored values are confirmed reliable for the Phase 4a corpus.** The stored `qa_passed` values faithfully reflect the current pool state, not a point-in-time smaller cohort. The Note B concern was methodologically sound given the shakedown precedent; it simply does not materialize at Phase 4a's model diversity level.

---

## 5. Per-check rerun failure breakdown

Check instances are counted across all unique failing records (some records trigger multiple checks).

| Check | Description | Failing records |
|---|---|---|
| Check 1 | Free-list item count too low (< 10) | 3 |
| Check 5 | Step latency too high (> 60,000ms) | 23 |
| Check 6 | Output token count inconsistent (> ±100% of `len(response)/4`) | 14 |
| Check 8 | Pile-interview label count mismatch | 5 |
| Check 2 | Free-list cross-run uniqueness | 0 |
| Check 9 | Backup freshness | 0 (infrastructure check, not per-record) |

**Check 8 (aggregate salience agreement) also passed**: no (model, domain) groups failed the Smith's S / Sutrop CSI rank-order agreement threshold. No AGGREGATE FAILURES line in output.

**Check 9 note:** The backup-freshness check is not a per-record check. It fires once per invocation at the infrastructure level. It did not fire in this run (backup log is current).

### Multi-check records

Three record types carry multiple concurrent failures:

- **Check 5 + Check 6 (co-occurring):** 10 records — all `qwen/qwen3.6-plus`. These records have extremely long freelist latency (86–263 seconds) and token counts ~8–14× the `len(response)/4` estimate. This pattern is consistent with extended thinking / chain-of-thought tokens counted in `output_tokens` but not represented in `response_verbatim`. See §7 for model-level detail.
- **Check 1 + Check 5 + Check 6 (co-occurring):** 3 records — all `z-ai/glm-5.1` × `family`. These records have `parsed_items=[]` (empty freelist, item count = 0), very long latency, and the same token-inconsistency pattern.
- **Check 5 + Check 8 (co-occurring):** 1 record — `meta-llama/llama-4-maverick` × `family`, plus 1 record (`bdcec352d880144c`) also with Check 5 + Check 8.

---

## 6. Divergence and reverse-divergence detail

**Stored True → Rerun False (divergences): 0**

No records diverged in this direction. (The pool-aggregation mechanism that produced 54 divergences in the shakedown replay does not activate at Phase 4a's model diversity level — see §4 Note B reconciliation.)

**Stored False → Rerun True (reverse divergences): 0**

No reverse divergences. No evidence of data corruption or check-function inconsistency.

---

## 7. All 27 rerun failures

| informant_id | model_id | domain | origin | stored qa_passed | failing checks |
|---|---|---|---|---|---|
| `b33ab4769b59c1a1` | `z-ai/glm-5.1` | family | cn | False | 1, 5, 6 |
| `c2b127f0226fa3cc` | `z-ai/glm-5.1` | family | cn | False | 1, 5, 6 |
| `d4b3d984930546a8` | `z-ai/glm-5.1` | family | cn | False | 1, 5, 6 |
| `7c7e517d5a852364` | `z-ai/glm-5.1` | holidays | cn | False | 5, 6 |
| `44fba223bb4e505f` | `qwen/qwen3.6-plus` | family | cn | False | 5, 6 |
| `8913f0017a931909` | `qwen/qwen3.6-plus` | family | cn | False | 5, 6 |
| `8a1f6f08928244a1` | `qwen/qwen3.6-plus` | family | cn | False | 5, 6 |
| `f2d8c7383e4e59fa` | `qwen/qwen3.6-plus` | family | cn | False | 5, 6 |
| `f6179032558b0181` | `qwen/qwen3.6-plus` | family | cn | False | 5, 6 |
| `363bc8fc8ba022fa` | `qwen/qwen3.6-plus` | holidays | cn | False | 5, 6 |
| `45f980d9bd75bc42` | `qwen/qwen3.6-plus` | holidays | cn | False | 5, 6 |
| `5de0f1658780738a` | `qwen/qwen3.6-plus` | holidays | cn | False | 5, 6 |
| `d93e474b6c59e9b2` | `qwen/qwen3.6-plus` | holidays | cn | False | 5, 6 |
| `fae826d840e1c64e` | `qwen/qwen3.6-plus` | holidays | cn | False | 5, 6 |
| `3e48592edf41a75e` | `x-ai/grok-4` | family | us | False | 5 |
| `d42fecd904dd50d2` | `x-ai/grok-4` | family | us | False | 5 |
| `d4f70682680a9b2c` | `x-ai/grok-4` | family | us | False | 5 |
| `0216e50e02a8c493` | `x-ai/grok-4` | holidays | us | False | 5 |
| `0b10c25030801614` | `x-ai/grok-4` | holidays | us | False | 5 |
| `17fb4eeb3b8e5588` | `x-ai/grok-4` | holidays | us | False | 5 |
| `7085fac78b1eae63` | `x-ai/grok-4` | holidays | us | False | 5 |
| `c2997ef60b1355b7` | `x-ai/grok-4` | holidays | us | False | 5 |
| `0bcad9d42653cc84` | `mistralai/mistral-small-2603` | holidays | eu | False | 8 |
| `283df33fd6920973` | `mistralai/mistral-small-2603` | holidays | eu | False | 8 |
| `8497aeca2e2012ab` | `mistralai/mistral-small-2603` | holidays | eu | False | 8 |
| `bdcec352d880144c` | `meta-llama/llama-4-maverick` | family | us | False | 5, 8 |
| `f1d5455e42b4e75c` | `openai/gpt-5.4-mini` | holidays | us | False | 8 |

### Failure counts by model

| model_id | origin | fail_count | primary checks |
|---|---|---|---|
| `qwen/qwen3.6-plus` | cn | 10 | 5 + 6 (all 10) |
| `x-ai/grok-4` | us | 8 | 5 (all 8) |
| `z-ai/glm-5.1` | cn | 4 | 1 + 5 + 6 (3×); 5 + 6 (1×) |
| `mistralai/mistral-small-2603` | eu | 3 | 8 (all 3) |
| `openai/gpt-5.4-mini` | us | 1 | 8 |
| `meta-llama/llama-4-maverick` | us | 1 | 5 + 8 |

### Cell-level detail

| model_id | domain | n records | qa_true | qa_false |
|---|---|---|---|---|
| `qwen/qwen3.6-plus` | family | 5 | 0 | 5 |
| `qwen/qwen3.6-plus` | holidays | 5 | 0 | 5 |
| `z-ai/glm-5.1` | family | 3 | 0 | 3 |
| `z-ai/glm-5.1` | holidays | 1 | 0 | 1 |
| `x-ai/grok-4` | family | 5 | 2 | 3 |
| `x-ai/grok-4` | holidays | 5 | 0 | 5 |
| `mistralai/mistral-small-2603` | holidays | 4 | 1 | 3 |
| `openai/gpt-5.4-mini` | holidays | 5 | 4 | 1 |
| `meta-llama/llama-4-maverick` | family | 3 | 2 | 1 |

---

## 8. Note K — CN-origin decline clustering (SME T5 forward note)

**SME Note K** (from `docs/status/2026-04-23-phase4a-t5-cda-sme-verdict.md`) flagged that 4 of 5 decline-interviewable cells are CN-origin pre-remediation:

> "qwen/qwen3.6-plus × {family, holidays}; z-ai/glm-5.1 × {family, holidays}"

The T6 QA sweep **confirms and extends this pattern at the record level:**

- CN-origin models (`qwen/qwen3.6-plus` + `z-ai/glm-5.1`) account for **14 of 27** (52%) of all `qa_passed=False` records.
- Both CN-origin models show **100% failure rates** across all their records in the corpus (qwen: 10/10; glm: 4/4 — noting glm-5.1 has only 4 records total due to collection-time stops).
- The failure mechanism for both CN-origin models is dominated by **Check 5 + Check 6 co-occurrence** (extended-thinking latency + token inconsistency), distinct from the Check 8 (pile-interview label mismatch) failures seen in mistral-small and gpt-5.4-mini.
- `deepseek/deepseek-v3.2` (CN-origin) shows **0/10 failures** — the CN clustering is specific to the qwen and glm families, not CN origin as a class.

Per Note K, this pattern must be framed as a **coverage / protocol robustness caveat**, not as a finding about CN model behavior, until the Phase 4a.1 cross-tab (Note J) confirms it is not an artifact of elicitation protocol, prompt language, or API routing.

---

## 9. Phase 4a.1 backfill implications

The decline-interview detection set for Phase 4a.1 is the set of `qa_passed=False` records whose session content matches triggers 1 + 2a–e from the decline-interview protocol. The T6 rerun confirms the backfill candidate set has **27 records** across 6 models.

**Candidate set by failure type and Phase 4a.1 relevance:**

| Failure type | Count | Phase 4a.1 relevance |
|---|---|---|
| Check 1 (empty freelist: items=0) | 3 | High — empty primary-step output is the canonical decline-interview trigger. All 3 are `z-ai/glm-5.1` × family. |
| Check 5-only (latency) | 8 | Lower — latency alone does not trigger decline-interview (the output may be structurally valid). All 8 are `x-ai/grok-4`. Requires inspection for `originating_outcome_class`. |
| Check 5 + Check 6 (latency + token inconsistency) | 11 | Medium — token inconsistency (output_tokens >> response_verbatim/4) is consistent with extended-thinking sessions producing interpretable output but failing the token heuristic. Output may be structurally valid. Inspection needed. All 11 are qwen/qwen3.6-plus (10) + z-ai/glm-5.1 (1). |
| Check 8-only (pile-interview label mismatch) | 4 | Medium-high — label-count mismatch is trigger 2c (parse failure on pile-sort). Affects mistral-small-2603 (3) + gpt-5.4-mini (1). |
| Check 5 + Check 8 | 1 | Medium — both latency and label mismatch; `meta-llama/llama-4-maverick` × family. |

The Phase 4a.1 runner should inspect all 27 records for content-level decline signals (trigger 2a–e) using the deterministic allowlist. Records where latency or token-inconsistency is the sole failure and the output is structurally valid do NOT automatically trigger decline-interview; they are QA-failed infrastructure events.

**Records with Check 1 (empty freelist, items=0) are the highest-priority Phase 4a.1 candidates:** these 3 `z-ai/glm-5.1` × family records produced no interpretable primary-step output, matching `originating_outcome_class="empty_output"` directly.

---

## 10. Append-only compliance

**No edits to `data/raw/informants.jsonl`.** The file was read only. The stored `qa_passed` values are preserved as-is, documenting the point-in-time collection state. This is correct per `CLAUDE.md` §6 R2 and per the Position C replay verdict observation that stored values are semantically valid snapshots.

---

## 11. Before-commit checklist

- [x] `uv run pytest tests/ -q` — 563 passed, 0 failures
- [x] `uv run ruff check .` — All checks passed
- [x] `uv run mypy packages/` — Success: no issues found in 52 source files
- [x] No edits to `data/raw/informants.jsonl` (R2)
- [x] No API calls (R10)
- [x] No `cdb_analyze` touch (R12)
- [x] No forbidden vocabulary in this report

---

## 12. Go/no-go for T7

**GO.** The QA sweep completed cleanly:

- Full 2×2 reconciliation: zero divergences, zero reverse-divergences.
- Note B concern (pool-aggregation divergence) does not materialize at Phase 4a's model diversity level; stored values are reliable.
- 27 `qa_passed=False` records identified and characterized by failure type.
- Note K CN-origin clustering confirmed pre-remediation (14/27 failures are CN-origin qwen + glm; deepseek is clean).
- No edits to JSONL (append-only invariant maintained).
- Phase 4a.1 backfill candidate set: 27 records, prioritized by failure type in §9.

T7 (post-run hygiene: B2 backup verification + DATA_DICTIONARY.md addendum + completion report) is unblocked.

---

*End of T6 QA sweep report.*
