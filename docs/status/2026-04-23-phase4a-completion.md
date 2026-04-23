# Phase 4a Completion Report

**Date:** 2026-04-23
**Author:** Coder (Claude Sonnet 4.6), Linode `lsb-agent-02`
**Task spec:** `docs/status/2026-04-22-phase4a-kickoff-architect-verdict.md` §4 T7
**Preceding gate:** Reviewer PASS on T6 QA sweep (commit `83ff645`)

---

## 1. Timeline and key commits

| Event | Date | Commit / Reference |
|---|---|---|
| B2 backup layer live | 2026-04-22 | `docs/status/2026-04-22-b2-test-restore.md` |
| Phase 4a Architect kickoff verdict | 2026-04-22 | `a2fea49` |
| CDA SME PASS-WITH-NOTES on 12-model slate | 2026-04-22 | `b13ae9a` |
| T1 adapter preflight (5/5 PASS) | 2026-04-22 | `7076dc4` |
| T2 CLI semantics confirmation | 2026-04-22 | `5f5fe7d` |
| T3 phi-4 × family × N=5 canary | 2026-04-22 | `fb645fa` |
| Amendment A — mode correction (single_pass) | 2026-04-22 | `bb7f448` |
| T4 full 12-model × 2-domain × N=5 run | 2026-04-22 | `b2b74e4` |
| Failures-as-findings directive + Architect decomposition | 2026-04-23 | `0556772` |
| Verbatim-capture gap closure (task #23) | 2026-04-23 | `36bca21` |
| Failures.jsonl schema expansion (task #24) | 2026-04-23 | `05e918a` |
| Decline-interview protocol (task #26) | 2026-04-23 | `fe7d335` |
| Small-n threshold fix n<8 → n<15 (task #28) | 2026-04-23 | `4f10924` |
| T5 analysis — family + holidays DomainResults | 2026-04-23 | `d74ce57` |
| CDA SME PASS-WITH-NOTES on T5 | 2026-04-23 | `3032f4a` |
| Reviewer PASS-WITH-NOTES on T5 | 2026-04-23 | `7e0a37c` |
| T6 QA sweep — zero divergences, 27 failures characterised | 2026-04-23 | `87488d8` |
| Reviewer PASS on T6 | 2026-04-23 | `83ff645` |
| lsb_inspect.py rename (task #30) | 2026-04-23 | `f0a10b5` |
| **T7 completion report + DATA_DICTIONARY.md addendum** | **2026-04-23** | **this commit** |

---

## 2. Gate status summary

| Task | Gate(s) | Verdict | Reference |
|---|---|---|---|
| Slate composition (pre-T1) | CDA SME | **PASS-WITH-NOTES** (Notes A–E) | `docs/status/2026-04-22-phase4a-slate-cda-sme-verdict.md` |
| T1 adapter preflight | Reviewer | **PASS** | `docs/status/2026-04-22-phase4a-t1-reviewer-verdict.md` |
| T2 CLI semantics | Architect | **PASS** | `docs/status/2026-04-22-phase4a-t2-orchestrator-verdict.md` |
| T3 phi-4 canary | Reviewer | **PASS** | `docs/status/2026-04-22-phase4a-t3-reviewer-verdict.md` |
| T4 full collection | Reviewer | **PASS-WITH-NOTES** | `docs/status/2026-04-23-phase4a-t4-reviewer-verdict.md` |
| Decline-interview protocol (task #26) | CDA SME + Reviewer | **PASS-WITH-NOTES** (Notes F–K) | `docs/status/2026-04-23-decline-interview-protocol-sme-verdict.md`, `docs/status/2026-04-23-phase4a-task26-reviewer-verdict.md` |
| Small-n threshold reconciliation (task #28) | CDA SME | **PASS** (n<15 binding) | `docs/status/2026-04-23-small-n-threshold-sme-amendment.md` |
| T5 analysis (family + holidays DomainResults) | CDA SME + Reviewer | **PASS-WITH-NOTES** (Note K new) | `docs/status/2026-04-23-phase4a-t5-cda-sme-verdict.md`, `docs/status/2026-04-23-phase4a-t5-reviewer-verdict.md` |
| T6 QA sweep | Reviewer | **PASS** | `docs/status/2026-04-23-phase4a-t6-qa-sweep.md` — commit `87488d8`; reviewer `83ff645` |
| T7 hygiene (this task) | Reviewer | pending | — |

**Accepted style overrides (T5 Reviewer, Mark 2026-04-23):**
- Override 1: T5 commit subject 82 chars (> §8 72-char limit). Cosmetic; force-push prohibited.
- Override 2: Task #30 `git mv` bundled into `3032f4a` CDA SME verdict commit.
- Override 3: Task #30 split across two commits (`3032f4a`, `f0a10b5`).

---

## 3. Data artifacts

### 3.1 `data/raw/informants.jsonl`

| Metric | Value |
|---|---|
| Total records | 101 |
| Domain: family | 53 |
| Domain: holidays | 48 |
| `qa_passed=True` | 74 |
| `qa_passed=False` | 27 |
| T3 canary records (phi-4 × family) | 4 |
| T4 records | 97 |

### 3.2 `data/raw/failures.jsonl`

| Metric | Value |
|---|---|
| Total failure entries | 29 lines (file) |
| Hard failures recorded | ~19 entries (google/gemini-2.5-pro × 10 cells, glm-5.1 × partial runs, llama/gpt-5.4-mini hard failures) |

### 3.3 `data/results/family/0.1.json`

| Field | Value |
|---|---|
| `n_models` | 10 |
| `n_records` (qa-passed) | 41 |
| `consensus_type` | `STRONG_CONSENSUS` |
| `romney_eigenratio` | 10.7917 |
| `romney_small_n_warning` | `True` (n=10 < 15) |
| `consensus_score` | 0.7122 |
| `consensus_ci` | (0.5039, 0.9012) |
| `negative_centrality_flag` | `False` |
| `g1_overall_pass` | `None` (G1 not evaluated — Phase 4b required) |
| MDS models | 10 |

### 3.4 `data/results/holidays/0.1.json`

| Field | Value |
|---|---|
| `n_models` | 8 |
| `n_records` (qa-passed) | 33 |
| `consensus_type` | `STRONG_CONSENSUS` |
| `romney_eigenratio` | 9.2181 |
| `romney_small_n_warning` | `True` (n=8 < 15) |
| `consensus_score` | 0.7658 |
| `consensus_ci` | (0.4737, 0.9665) |
| `negative_centrality_flag` | `False` |
| `g1_overall_pass` | `None` (G1 not evaluated — Phase 4b required) |
| MDS models | 8 |

### 3.5 Cell coverage

Of the 12-model × 2-domain × N=5 design:
- **18 cells** produced analyzable pile-sort data (contributed to DomainResults)
- **5 cells** produced decline-interviewable outputs (records exist, all `qa_passed=False`): `qwen/qwen3.6-plus` × {family, holidays}; `z-ai/glm-5.1` × {family, holidays}; `x-ai/grok-4` × holidays
- **1 cell** produced zero records (google/gemini-2.5-pro × family; holidays not attempted after stop condition 1)
- `microsoft/phi-4` ran family only (T3 canary scope; no holidays records)

---

## 4. Cost summary

| Metric | Value |
|---|---|
| April 2026 total spend (from `cost_report.py --month current`) | **$4.95** |
| Monthly cap (`CDB_MAX_SPEND_USD`) | $300 |
| Cap utilization | 1.7% |

Mark's standing "<$5 per session" observation is confirmed for Phase 4a. The full 12-model × 2-domain collection + analysis run cost less than $5.

---

## 5. B2 backup verification

The 02:00 UTC nightly backup timer ran on 2026-04-23 and completed successfully.

| File | Size | B2 path | Log timestamp |
|---|---|---|---|
| `data/raw/informants.jsonl` | 14,075,214 bytes | `2026-04-23/data/raw/informants.jsonl` | 2026-04-23T02:00:03Z |
| `data/raw/failures.jsonl` | 14,866 bytes | `2026-04-23/data/raw/failures.jsonl` | 2026-04-23T02:00:02Z |
| `data/results/family/0.1.json` | 15,891 bytes | `2026-04-23/data/results/family/0.1.json` | 2026-04-23T02:00:03Z |
| `data/results/family/0.2.json` | 29,440 bytes | `2026-04-23/data/results/family/0.2.json` | 2026-04-23T02:00:03Z |

**Summary line from `logs/backup.log`:**
```
2026-04-23T02:00:03Z INFO SUMMARY considered=5 uploaded=5 skipped=0 bytes_uploaded=14135411 exit_code=0
```

Phase 4a records are confirmed in the B2 bucket. No manual backup trigger required.

**Note:** `data/results/holidays/0.1.json` was written after the 02:00 UTC timer ran (T5 analysis was completed at 14:29 UTC). It will be picked up by the next nightly run (2026-04-24 02:00 UTC). The file is on disk and intact.

---

## 6. `DATA_DICTIONARY.md` addendum

**v0.1.9 addendum committed in this task.** A new §1.6 ("Stored-vs-rerun `qa_passed` semantics") was added, documenting:
- `qa_passed` is a point-in-time snapshot at collection time
- Re-running `scripts/qa_check.py` on the corpus MAY produce different results when pool-aggregation Check 2 flips as the cohort grows
- The divergence materialized in the shakedown corpus replay (Position C, 2026-04-22) but not in Phase 4a (T6 found zero divergences — 12-model diversity prevents pool saturation at N=5)
- Downstream consumers wanting "final" QA status should re-run the check battery

No schema change to `cdb_core/schemas.py`. R7 satisfied (addendum is a prose change to the dictionary, not a schema modification).

---

## 7. Outstanding carry-forward

### 7.1 Phase 4a.1 — decline-interview backfill (task #21)

The 27 `qa_passed=False` records identified in T6 are the Phase 4a.1 candidate set, prioritized as follows:

| Failure type | Count | Phase 4a.1 priority | Models |
|---|---|---|---|
| Check 1 (empty freelist, items=0) | 3 | HIGH — canonical decline-interview trigger | `z-ai/glm-5.1` × family |
| Check 8-only (pile-interview label mismatch) | 4 | Medium-high — trigger 2c | mistral-small-2603 (3), gpt-5.4-mini (1) |
| Check 5+8 | 1 | Medium | meta-llama/llama-4-maverick × family |
| Check 5+6 (latency + token inconsistency) | 11 | Medium — extended-thinking sessions; output may be structurally valid | qwen/qwen3.6-plus (10), glm-5.1 (1) |
| Check 5-only (latency) | 8 | Lower — latency alone is not a decline-interview trigger | x-ai/grok-4 |

Phase 4a.1 runner must inspect all 27 records for content-level decline signals (trigger 2a–e from the protocol) before deciding which to interview. Records where latency is the sole failure and the output is structurally valid are QA-failed infrastructure events, not decline candidates.

Additionally, `google/gemini-2.5-pro` produced zero records (stop condition 1 during T4 collection). Its failure entries in `failures.jsonl` should be included in the Phase 4a.1 sweep.

### 7.2 SME forward notes — tracking to destinations

| Note | Content | Destination |
|---|---|---|
| A | `romney_small_n_warning=True`; CCM small-n caveat | **SATISFIED** at T5 (both domains) |
| B | Stored-vs-rerun `qa_passed` semantics | **SATISFIED** at T6 (zero divergences) + T7 DATA_DICTIONARY.md addendum |
| C | Cell-coverage denominator: "18 analyzable + 5 decline-interviewable" | **SATISFIED** at T5 §6; binding on public copy |
| D | No ceiling claims before Phase 4c | **SATISFIED** at T5; binding on Phase 4c+ copy |
| E | US-weighted composition caveat | Strengthened by Note K; binding on Phase 6+ methodology page |
| F | `version_drift_flag` per-run version tracking | Phase 4a.1 runner (#21) |
| G | Exact wording for uninterviewed cells | **SATISFIED** at T5 §5; binding on all public copy |
| H | Prompt versioning in decline-interview runner | Phase 4a.1 runner (#21) |
| I | Dashboard copy framing for declined/failed cells | Phase 6+ (task #22 dashboard failure-display) |
| J | Phase 4a.1 cross-tab: CN-origin decline pattern confirmation | Phase 4a.1 runner (#21); determines whether Note K formalizes |
| K | CN-origin decline clustering (4 of 5 decline-interviewable cells are CN-origin) | Phase 4a.1 (#21) + Phase 6+ methodology copy; NOT a finding until Note J cross-tab |

### 7.3 Backlog tasks

| Task # | Description | Status |
|---|---|---|
| #21 | Phase 4a.1 decline-interview runner (27-record backfill set) | PENDING — requires Note J cross-tab per SME |
| #16 | Adaptive `max_tokens` in openrouter adapter | DEFERRED to Phase 4b prep |
| #22 | Dashboard failure-display feature (Phase 6+) | DEFERRED — now on critical path for credibility |
| #27 | Continue-after-failure in collection runner | PENDING |
| #29 | `SME_REVIEW.md` hygiene | PENDING |

Task #28 (small-n threshold fix) is DONE (commit `4f10924`).
Task #30 (lsb_inspect.py rename) is DONE (commits `3032f4a`, `f0a10b5`).

### 7.4 Infrastructure carry-forward

- `HOSTING_AND_DEV_OPS.md` full Linode-era rewrite (25 residual Hetzner/lsb-agent-01 references) — deferred
- SSH hardening on Linode (`PermitRootLogin prohibit-password`) — TBD
- Cloudflare DNS A-record cutover `cogstructurelab.com` → `172.238.170.9` — TBD, only after web server live
- `data/results/holidays/0.1.json` not yet in B2 (written post-02:00 UTC; captured on 2026-04-24 nightly run)

---

## 8. Phase 4b readiness

Phase 4b is the G1 sensitivity study. Gate criterion: `g1_overall_pass` is the conjunction of `g1_salience_pass` and `g1_spatial_pass` (both must be True). Both DomainResults currently have `g1_overall_pass=None` — correct for Phase 4a.

**Pre-conditions for Phase 4b kick-off:**

1. Phase 4a.1 decline-interview data captured for the 5 decline-interviewable cells (task #21). Phase 4b proceeds on the combined T4 + 4a.1 corpus to avoid running the G1 sensitivity study on a corpus that later changes materially.
2. Note J cross-tab resolved (does CN-origin decline clustering reflect elicitation artifact or corpus lens signal?). If the cross-tab confirms elicitation artifact, the prompt may need a variant before Phase 4b runs.
3. `g1_salience_stability` and `g1_spatial_stability` thresholds confirmed with CDA SME (ARCHITECTURE.md §5.3 Phase 4b: threshold = 0.5 for both axes). Per ARCHITECTURE.md §5.3, Phase 4b runs multiple prompt phrasings per cell to compute stability under prompt variation.

**Phase 4b runbook reference:** `ARCHITECTURE.md` §5.3 Phase 4b.

---

## 9. Phase 4a verdict

**Phase 4a is COMPLETE** subject to T7 Reviewer PASS.

- 101 InformantRecords written to `data/raw/informants.jsonl` (101/120 expected; 19 missing cells documented as findings).
- Both DomainResults (`data/results/family/0.1.json`, `data/results/holidays/0.1.json`) pass schema validation with `STRONG_CONSENSUS` and `romney_small_n_warning=True`.
- Full 2×2 QA reconciliation: zero divergences.
- B2 backup confirmed for all T4 data as of 2026-04-23 02:00 UTC.
- `DATA_DICTIONARY.md` v0.1.9 addendum committed.
- Spend: $4.95 total (1.7% of monthly cap).

**Go/no-go for Phase 4a.1 (task #21): GO**, subject to Reviewer PASS on this T7 commit.

---

*End of Phase 4a completion report.*
