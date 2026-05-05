# Phase 4a Recovery Campaign — Architect Plan

**Date:** 2026-05-05
**Planner:** Architect agent (Opus)
**Trigger:** Task #16 (`7f8f7f7` + `de3dd7e`) merged on master with v0.1.11 schema. Stages 1.5/1.5b/1.6/1.7 (commits `d06e64c`, `11a36c0`, `19d67f1`, `bef7660`) confirm 19–20 of the 29 Phase 4a failure rows are recoverable under the bumped `max_tokens=16384` cap on the production adapter.
**Supersedes:** none (new task)
**Carries forward:** `docs/status/2026-05-04-task-16-architect-plan.md` (Task 16.A/16.B); `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (notes S1–S5 — S5 is binding for the future T4-redo, NOT for this recovery task; see §6 Q5)
**Companion docs:** `ARCHITECTURE.md` §1.5, §3.2, §4.1, §6.2; `CLAUDE.md` §6, §8, §9; `docs/SHAKEDOWN_PROTOCOL.md` §2 (campaign-id precedent); `docs/DATA_DICTIONARY.md` §1.1 (qa_notes, collection_date), §9 (failures.jsonl)
**Gate chain (mandatory, in order):** **CDA SME PASS** → Coder → Reviewer PASS → Tester PASS

> **Status before Coder may start:** CDA SME PASS or PASS-WITH-NOTES required. Reading-list and recount are confirmed.

---

## 1. Disposition table

| Concern | Disposition |
|---|---|
| **Recovery target population** | **20 cells**, not 19 (recount from `data/raw/failures.jsonl`): `google/gemini-2.5-pro` family runs 0–4 + holidays runs 0–4 = 10; `z-ai/glm-5.1` family runs 1, 3 + holidays runs 0, 2, 3, 4 = 6; `meta-llama/llama-4-maverick` family runs 1, 4 + holidays runs 0, 1 = 4. |
| **Out of scope** | `microsoft/phi-4` (6 records, lines 1–6 of failures.jsonl: 5×HTTPStatusError + 1×ValueError — adapter/400 issue, separate investigation); `openai/gpt-5.4-mini` (2 records, family runs 0 and 2, lines 10–11); `mistralai/mistral-small-2603` (1 record, holidays run 3, line 23). 9 cells deferred. |
| **Pipeline used** | Production CDA pipeline post-Task-16: `GeminiAdapter` and `OpenRouterAdapter` at `max_tokens=16384` with `thoughts_token_count` capture. No prompt-template change. No protocol change. v1 prompts unchanged. |
| **Where data lands** | Canonical `data/raw/informants.jsonl` (append-only). Campaign tag `campaign_id=phase4a-recovery-2026-05-05` in `qa_notes` is the filterability mechanism (§4.1). |
| **Schema changes** | **None.** v0.1.11 InformantRecord (Task 16.B) already accommodates the records. No `cdb_core/schemas.py` edit. No `DATA_DICTIONARY.md` update. |
| **Existing failure records in `failures.jsonl`** | Untouched. Append-only convention (CLAUDE.md §9 pitfall 10) is binding. The 20 historical failure rows remain in place; recovered records become authoritative *informants* once written; analysis joins informants on `(model_id, domain_slug, run_index)` so the historical failure rows are de-facto superseded but never edited. |
| **build_db.py rerun** | **Yes**, but as an ops follow-up, not part of this plan. Architect to schedule after recovery completes. |
| **T4 redo on the recovered corpus** | **Out of scope.** S5 (Task 16 SME verdict) is binding for that future task. T4-redo gets its own Architect plan + SME PASS. Mentioned here so the Coder does not bundle. |
| **max_tokens > 16384 for stubborn cells** | Out of scope. If a recovery cell deterministically fails on both attempts at 16384, file as a follow-on Architect task; do NOT bump in-flight. |
| **Forbidden vocabulary** | None used. Recovery framed as "instrument fix" / "cap-exhausted reasoning" per Task 16 SME notes S1/S3. No `worldview` / `believes` / `thinks` framing. |

---

## 2. Tasks

### Task R1 — Recovery target list extractor + recovery script

**Owner:** Coder
**Files:**
- New: `scripts/recover_phase4a_failures.py` (single-purpose script; not an extension of `collect.py`).
- Reads: `/opt/lsb-agent/data/raw/failures.jsonl`, `/opt/lsb-agent/data/models/registry.json`, `/opt/lsb-agent/data/raw/informants.jsonl`.
- Writes: `/opt/lsb-agent/data/raw/informants.jsonl` (append) and `/opt/lsb-agent/data/raw/failures.jsonl` (append, only on retry-budget exhaustion).

**Scope rationale.** A separate script is the right structural choice over extending `scripts/collect.py`:
- The recovery loop is one-shot, target-list-driven, with retry semantics distinct from `collect_single_pass`.
- Existing `--skip-collected` operates at *model* granularity, not per-(model, domain, run_index) cell — wedging cell-level targeting into `collect.py` would change a stable contract that the shakedown protocol and Phase 4a docs depend on.
- The recovery script can `import` the same `cdb_collect` runner functions (`run_informant`) and the same `_create_adapter`/`_load_registry` helpers from `collect.py`. No protocol logic is duplicated.

**Behavior contract:**

1. **Target-list construction.** Read `failures.jsonl`, build a deduped list of `(model_id, domain, run_index)` tuples filtered to the in-scope models. Hard-coded allow-list (per §1 disposition) inside the script:
   ```
   IN_SCOPE_MODELS = {
       "google/gemini-2.5-pro",
       "z-ai/glm-5.1",
       "meta-llama/llama-4-maverick",
   }
   ```
   Anything outside this set is skipped with an explicit log line ("deferred: out of scope"). The expected list size is 20; the script asserts this and aborts with a clear error if `len(targets) != 20` (defends against stale failures.jsonl drift).

2. **Idempotence (resumable).** Before each cell, scan `informants.jsonl` for any record matching `(model_id, domain_slug, run_index)` AND `qa_notes` containing `campaign_id=phase4a-recovery-2026-05-05`. If present, skip and log "already recovered". This is the `--skip-already-recovered` semantic, on by default. (Q4 ruling: resumable.)

3. **Retry budget per cell.** Up to **2 attempts** per cell. Inter-attempt delay: 5 seconds (token-bucket courtesy; not a rate-limit defense). On both attempts failing, write a `failures.jsonl` entry with:
   - The exception verbatim (existing `append_failure` contract)
   - `qa_notes`-equivalent context fields: `campaign_id=phase4a-recovery-2026-05-05`, `recovery_failed=true`, plus the original failure timestamp (or `original_failure_id` if the existing failure-row schema supports a stable ID; otherwise the original failure's `timestamp` field is sufficient cross-reference)
   - Continue to the next cell (do NOT abort the campaign on per-cell failure).

4. **Campaign-id wiring.** Each successful informant record's `qa_notes` carries `campaign_id=phase4a-recovery-2026-05-05`. The mechanism is the existing `--campaign-id` flag handling in `run_informant`; the recovery script invokes `run_informant(adapter, domain, run_index, campaign_id="phase4a-recovery-2026-05-05")`.

5. **Inter-cell delay.** No explicit delay (Q3 ruling: glm-5.1 and Gemini calls are slow enough naturally; OpenRouter has been generous; courtesy 5s gap between cells suffices). Skip per-call sleeps unless a 429 is observed during the run, at which point the script falls back to 30 s exponential backoff for that adapter — but that path is reactive, not preventive.

6. **Wall-clock estimate.** ~30–45 minutes for all 20 cells running serially. No concurrency.

7. **Safety: dry-run first.** `--dry-run` flag prints the target list (20 cells), validates registry hits for all 3 models, and exits without API calls. Mandatory first run before live recovery.

8. **Logging.** Per cell: `attempt N/2: <model> × <domain> run=<i> -> PASS/QA_FAIL/RETRY/RECOVERY_FAILED`. Final summary: `Recovered: X/20. Recovery-failed: Y. Already-recovered: Z. (X+Y+Z=20).`

**Acceptance criteria:**
- Script in `scripts/recover_phase4a_failures.py` exists and is invokable as `uv run python scripts/recover_phase4a_failures.py --dry-run` and `uv run python scripts/recover_phase4a_failures.py`.
- `--dry-run` prints exactly 20 target cells matching the §1 disposition list.
- Live run produces ≥17 valid InformantRecords (≥85% recovery target, accounting for ~10% probe-observed first-attempt failure).
- Every successful record has `qa_notes` containing `campaign_id=phase4a-recovery-2026-05-05`.
- Re-running the script after a successful run produces "Already recovered: 20" and 0 new API calls.
- No edits to existing `informants.jsonl` lines (CI append-only check passes).
- No edits to existing `failures.jsonl` lines.
- All 20 attempted cells either land as InformantRecords or as new `recovery_failed` failure rows; no cell silently dropped.

**Test coverage (Tester):**
- Unit test on the target-list extractor with a synthetic `failures.jsonl` fixture covering all three in-scope models, the three out-of-scope models, and a duplicate row (asserts dedup). Use `tests/fixtures/phase4a_failures_sample.jsonl`.
- Unit test on the idempotence check with a synthetic `informants.jsonl` containing one already-recovered record (asserts skip).
- Unit test on the retry budget: stub the adapter to raise twice; assert one `failures.jsonl` row written with `recovery_failed=true` and no `informants.jsonl` row.
- **No real API calls in tests** (CLAUDE.md §9 pitfall 9). All adapter calls stubbed.
- `uv run pytest && uv run ruff check . && uv run mypy packages/` green.

**Reading list for Coder before starting R1:**
- `CLAUDE.md` §6 (binding rules), §8 (commit conventions), §9 (pitfalls — 1, 9, 10 specifically)
- `ARCHITECTURE.md` §1.5 (binding framing), §3.2 (InformantRecord), §4.1 (collection layer), §6.2 (cost gate)
- `docs/SHAKEDOWN_PROTOCOL.md` §2 (campaign-id precedent — recovery uses the same mechanism, different campaign-id; recovery data goes to canonical path, not `data/shakedown/`)
- `docs/DATA_DICTIONARY.md` §1.1 (qa_notes, collection_date semantics), §1.6 (stored-vs-rerun qa_passed), §9 (failures.jsonl shape)
- `docs/status/2026-05-04-task-16-architect-plan.md` and `cda-sme-verdict.md` (S5 boundary, NOT applied here but Coder should know why)
- `docs/status/2026-04-23-phase4a1-architect-plan.md` (the corpus the recovered records will eventually be analyzed against; not modified by this task)
- `scripts/collect.py` (reference for adapter wiring and `--campaign-id` precedent; do NOT modify)
- `scripts/probe_gemini_fullcycle_2026_05_04.py` and `scripts/probe_openrouter_fullcycle_2026_05_05.py` (reference for end-to-end probe semantics)
- `data/raw/failures.jsonl` lines 7–9, 12–22, 24–29 (the 20 in-scope rows)

**Estimated cost (Mark sign-off line):**
- Gemini 2.5 Pro: 10 cells × ~$0.50 per cell (3-step protocol at the bumped 16384 cap, observed in Stage 1.6) = ~$5.00
- glm-5.1: 6 cells × ~$0.10 per cell (OpenRouter, observed in Stage 1.7) = ~$0.60
- llama-4-maverick: 4 cells × ~$0.10 per cell = ~$0.40
- Retry budget: assume 10% retry incidence on 20 cells → 2 retries × ~$0.30 average = ~$0.60
- **Total projection: $5–8 USD.** Well under the standing $10/probe budget. 2.5% of the $300/mo cap (`ARCHITECTURE.md` §6.2).
- The `CDB_MAX_SPEND_USD=15` runtime guard is recommended as a session-level export — generous over the $5–8 projection but hard-stops cleanly if a runaway condition emerges.

**Gate verdicts required:**
- CDA SME PASS or PASS-WITH-NOTES on this Architect plan, before R1 starts.
- Reviewer PASS on the R1 commit (one commit per task per CLAUDE.md §8).
- Tester PASS on the R1 commit.

---

### Task R2 — Recovery campaign execution + recovery report

**Owner:** Coder (or Mark, at his discretion — this is a one-shot script invocation, not code work)
**Files:**
- Reads: production registry, production env (`.env` for API keys), R1 script
- Writes (live, by R1 script):
  - Appends ~17–20 records to `/opt/lsb-agent/data/raw/informants.jsonl`
  - Appends 0–3 new failure rows to `/opt/lsb-agent/data/raw/failures.jsonl` (only if some cells exhaust the retry budget)
- Writes (post-run, manual): `/opt/lsb-agent/docs/status/2026-05-05-phase4a-recovery-report.md` — recovery report capturing: campaign-id; per-cell outcome (PASS / RECOVERY_FAILED with reason); aggregate counts; cost reconciliation against §2 R1 estimate; pointer to the verdict files.

**Acceptance criteria:**
- `uv run python scripts/recover_phase4a_failures.py --dry-run` printed 20 target cells matching §1 disposition.
- Live run completed within wall-clock budget (~45 min).
- ≥17 of 20 cells produced InformantRecords (≥85% recovery rate).
- All recovered records carry `campaign_id=phase4a-recovery-2026-05-05` in `qa_notes`.
- All recovered records pass `scripts/qa_check.py` against the post-recovery corpus (`uv run python scripts/qa_check.py --file data/raw/informants.jsonl`). Note §1.6 stored-vs-rerun caveat — the recovery records are written with stored `qa_passed=True` and the post-run sweep is the secondary check; if any record flips to QA_FAIL on re-run, that is documented in the recovery report but does not constitute a recovery failure (record is still authoritative for the record-level audit trail).
- Cost reconciled against the projection: actual spend within ±50% of the $5–8 estimate, OR the recovery report explains the discrepancy.
- The recovery report is filed at `docs/status/2026-05-05-phase4a-recovery-report.md` and committed.

**Test coverage:** The recovery script itself is tested under R1. R2 has no separate unit tests — it's the production execution.

**Reading list for executor before R2:**
- The R1 script source (post-Reviewer PASS)
- `ARCHITECTURE.md` §6.2 (spend cap + `CDB_MAX_SPEND_USD` guard)
- `docs/status/2026-05-05-phase4a-recovery-architect-plan.md` (this document)

**Gate verdicts required:**
- R1 must be Reviewer-PASS-merged before R2 runs.
- R2 itself does NOT pass through CDA SME or Reviewer (it's a script invocation, not a code change). The recovery report is a docs commit and goes through Reviewer for the documentation rules only (no methodology re-review needed unless an SME-flagged anomaly surfaces during execution — see §4 risks).

**Estimated cost:** $5–8 USD as above. Subject to Mark's sign-off.

---

## 3. Sequencing and dependencies

```
[Architect plan written]
        │
        ▼
[CDA SME review of this plan]  ← MANDATORY GATE
        │
        ▼
   PASS / PASS-WITH-NOTES?
        │
        ▼
[Coder: Task R1 — write scripts/recover_phase4a_failures.py + tests]
        │
        ▼
[Reviewer: R1 verdict]
        │
        ▼
[Tester: R1 verdict]
        │
        ▼
[Mark sign-off on cost projection (§5)]
        │
        ▼
[Task R2: live execution]
        │
        ▼
[Manual: write 2026-05-05-phase4a-recovery-report.md]
        │
        ▼
[Reviewer: docs commit]
        │
        ▼
[Architect schedules: build_db.py rerun (separate ops task)]
[Architect schedules: T4 redo plan (separate Architect task — gated by S5)]
```

R1 and R2 must NOT be bundled into a single commit (CLAUDE.md §8 — one commit per task). The recovery report is a third commit.

---

## 4. Risks

### 4.1 Corpus contamination

**Risk:** A recovered record is written into `informants.jsonl` that should not be there — wrong model, wrong domain, wrong run_index, missing campaign-id, or schema violation that bypasses Pydantic.

**Mitigations:**
- The R1 script `assert len(targets) == 20`. A drift in `failures.jsonl` triggers an explicit abort, not silent variance.
- The campaign-id tag is written by the existing, tested `run_informant` codepath — same mechanism the shakedown campaigns used in production.
- Idempotence check on `(model_id, domain_slug, run_index, campaign_id)` prevents double-writes if the script is restarted mid-run.
- The `--dry-run` mode is mandatory before live execution.
- All recovered records are surfaced in the post-run report; Mark can grep `informants.jsonl` for `campaign_id=phase4a-recovery-2026-05-05` as a sanity check.

### 4.2 Retry semantics — what happens if a cell fails its retry budget

**Risk:** A cell exhausts its 2-attempt budget. In probe data this is the residual ~10% — Stage 1.7 saw 1 truncation residual on glm-5.1 and 1 coverage failure on llama-maverick.

**Mitigations:**
- **Failure is logged, not crashed-on.** A `failures.jsonl` row is written with `recovery_failed=true` and `campaign_id=phase4a-recovery-2026-05-05`. The campaign continues.
- The recovery report captures every failed cell with its diagnostic.
- If 4+ cells fail (target hit rate < 80%), the recovery report flags the under-performance and the Architect schedules a follow-on diagnostic — possibly a `max_tokens=32768` probe on the residual cells or a model-specific deep dive. **That follow-on is NOT bundled into this task.**
- The original `data/raw/failures.jsonl` rows from 2026-04-22 remain unchanged. The new `recovery_failed=true` rows are net-new appended entries; the audit trail is intact.

### 4.3 Schema drift between v0.1.11 InformantRecord and the recovery records

**Risk:** Task 16.B added `thoughts_token_count` to all three step records (default `0`). Recovery records will populate this field; the rest of the existing Phase 4a corpus has it materialized as `0` per Pydantic v2 default.

**Mitigations:**
- Field default `int = 0` is backward-compatible by design (verified in Task 16 verdict, axis 2).
- The diagnostic invariant `output_tokens == 0 AND thoughts_token_count > 0` will fire on cells where Gemini/OpenRouter exposes reasoning tokens, providing a within-record audit signature — a desired feature, not a risk.
- Pre-Task-16 Phase 4a records have `thoughts_token_count=0` because the field didn't exist at write time and Pydantic v2 defaults populate `0` on read. Cross-record comparisons remain valid.

### 4.4 Mid-campaign partial state if the script aborts uncleanly

**Risk:** Network outage, KeyboardInterrupt, or unhandled exception leaves `informants.jsonl` in a partial state — N out of 20 cells recovered, the rest still in their original failed state.

**Mitigations:**
- Append-only writes; each cell's record is fully serialized via `append_record` before the next cell starts. No multi-cell transactions.
- The idempotence check on resume (R1 behavior 2) means re-running the script picks up where it left off.
- The recovery report records the actual recovered count, not the projected count.

### 4.5 Reviewer rejecting the recovery report for forbidden vocabulary

**Risk:** Recovery report uses `believes` / `worldview` / `cultural bias` framing and gets rejected.

**Mitigations:**
- The recovery operation is purely instrument-level. The right framing is "cap-exhausted reasoning, recovered under the Task-16 cap fix" — methodologically clean and aligned with Task 16 SME notes S1/S3.
- The recovery report has no model-comparative claims, no consensus claims, no MDS claims. It is an instrument-event log.

### 4.6 An on-the-fly observation that the recovered records *systematically differ* from probe expectations

**Risk:** During execution, Mark notices that (e.g.) Gemini's recovered records all have unusually high pile counts, suggesting the cap-bump changed *what the model produces*, not just *whether the model produces visible output*.

**Mitigations:**
- This would be a methodology-touching finding and would route through CDA SME for re-review. The recovery script captures `thoughts_token_count`, `output_tokens`, and the full response object — sufficient evidence for a follow-on SME ruling.
- Stage 1.6 and 1.7 probes did not surface this signal at probe scale. If it shows at recovery scale, it is a finding worth investigating and the Architect schedules a separate diagnostic task — but the recovered records are still the authoritative replacement for the failed records, because the failure mode (`output_tokens=0`) was the artifact and the bumped cap is the corrected condition.

---

## 5. What Mark must sign off on

1. **Cost projection: $5–8 USD total.** Within the standing $10/probe budget. 2.5% of the $300/mo cap. Recommended `CDB_MAX_SPEND_USD=15` runtime guard.
2. **Campaign-id tag:** `campaign_id=phase4a-recovery-2026-05-05`.
3. **Target list:** 20 cells per §1 disposition (Gemini 10 + glm-5.1 6 + llama-maverick 4).
4. **Out-of-scope confirmation:** the 9 cells (phi-4 6, gpt-5.4-mini 2, mistral-small 1) remain in their original failed state and are explicitly NOT touched by this campaign.
5. **Where data lands:** canonical `data/raw/informants.jsonl`, with campaign-id as the filterability marker. NOT a separate file.

Mark's sign-off is requested as a `+1` in `#lsb-cda-sme` after the SME PASS, OR a docs/status commit comment, OR a direct message — operator's choice. Recovery does NOT proceed without sign-off because the spend, while small, is non-zero and the canonical corpus is being modified.

---

## 6. Open questions for SME ruling

### Q1 — Recovery target population: strict (only the 20 known-failed cells) or broad (any cell missing a successful informant in the canonical corpus)?

**Architect read:** **Strict.** The 20 cells are the ones that failed for a known cause (max_tokens=4096) for which the cap fix is the established remedy (Stages 1.5/1.5b/1.6/1.7). Any other "missing" cell either (a) succeeded already (and is therefore not missing), (b) is one of the 9 out-of-scope failures with a different root cause (phi-4 400-error, gpt-5.4-mini parser, mistral coverage), or (c) was never run in Phase 4a at all (which is an entirely different question — full collection, not recovery). Broad targeting would conflate three different diagnostic questions.

**SME confirm or override.**

### Q2 — Per-cell retry policy: 2 attempts max, then log `recovery_failed=true` and continue?

**Architect read:** **2 attempts max.** Stage 1.7 saw a ~10% first-attempt failure rate; a second attempt is courtesy + diagnostic (a deterministic same-cell failure on attempt 2 is itself a finding). 3+ attempts inflates spend without commensurate signal — the residual failures are likely model-deterministic at this prompt × this cap, and a third attempt won't break the pattern.

**SME confirm or override.**

### Q3 — Inter-call delay for rate-limit safety?

**Architect read:** **No explicit delay.** glm-5.1's heavy reasoning makes calls slow naturally; Gemini is similarly slow at the bumped cap; OpenRouter has shown no 429 behavior in probes. A reactive 30s exponential backoff on observed 429 is the standard adapter behavior; a preventive sleep is unnecessary. The 5s inter-attempt courtesy gap (R1 behavior 3) is the only sleep in the script.

**SME confirm or override.**

### Q4 — One-shot vs. resumable?

**Architect read:** **Resumable** (idempotent; default-on `--skip-already-recovered` semantic). A 30–45 min serial run that aborts at minute 25 should not require re-running the first 25 minutes. The idempotence check is a 4-line implementation against the existing append-only JSONL.

**SME confirm or override.**

### Q5 — Does this recovery plan trigger the S5 binding (Task 16 SME verdict) on Note K reclassification?

**Architect read:** **No.** S5 is binding for the future T4-redo task — the methodology-page text describing the Phase 4a.1 disposition table — not for the recovery operation itself. The recovery uses the same v1 prompts, the same CDA protocol, the same scoring. The corpus shape changes (20 records added) but the *methodology* is unchanged. The 9 originally-Gemini safety-event-attribution rows from Phase 4a.1 are not re-classified by this campaign — they are distinct decline-interview records, not the failure rows being recovered. T4-redo against the recovered corpus is the natural successor task and IS gated by S5; it gets its own Architect plan.

**SME confirm or override.** If SME rules differently — i.e., that the recovery operation IS methodology-touching at a level that requires a Note K reframe — the plan returns to Architect for re-scoping.

### Q6 — `build_db.py` rerun timing?

**Architect read:** **Yes, but not part of this plan.** The recovery commits 17–20 records to `informants.jsonl`; `lsb.sqlite` in `data/open_bundle/` is now stale until rebuilt. Architect schedules a follow-on ops task: `uv run python scripts/build_db.py data/raw/informants.jsonl data/open_bundle/lsb.sqlite`, plus the manifest checks. Pre-validation (Phase 4 G1/G2/G3 not yet evaluated), the open bundle does not have a public DOI, so the rebuild is internal-only.

**SME confirm or override.**

---

## 7. Boundaries explicitly affirmed

- **No code is written by the Architect.** This is a plan only.
- **CDA SME PASS is mandatory** before Coder starts R1.
- **No T4 redo** in scope. T4 redo is the natural successor and gets its own Architect plan + SME PASS chain. Mentioned only so the Coder does not bundle it.
- **No `cdb_core/schemas.py` edits.** v0.1.11 already supports the recovered records.
- **No `DATA_DICTIONARY.md` edit.** No schema motion.
- **No prompt-template change.** v1 templates unchanged.
- **No `cdb_analyze` change.** This is a collection-layer recovery, not an analysis-layer change. The §4.2 binding constraint is not touched.
- **No editing existing `informants.jsonl` or `failures.jsonl` lines.** Append-only convention enforced (CLAUDE.md §9 pitfall 10; the CI append-only check is the second line of defense).
- **No forbidden vocabulary** in any generated text (this plan, the script's docstring, the recovery report). `corpus lens` is not invoked because no corpus-level claim is being made; the recovery is an instrument-level operation.

---

*End of plan. Awaiting CDA SME verdict in `#lsb-cda-sme`. Coder may not start Task R1 until PASS or PASS-WITH-NOTES is filed at `docs/status/2026-05-05-phase4a-recovery-cda-sme-verdict.md`.*
