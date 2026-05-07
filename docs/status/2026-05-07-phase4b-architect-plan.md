# Phase 4b — Architect Plan

**Date:** 2026-05-07
**Author:** Architect (LSB pipeline)
**Status:** Draft for CDA SME review. Not actionable until SME PASS / PASS-WITH-NOTES.
**Companion docs (binding):**
- `docs/status/2026-05-07-lsb-philosophy-and-framing.md` (philosophy source-of-truth — quoted, not re-articulated)
- `ARCHITECTURE.md` v0.7.2 §1.5, §3.2, §3.5, §4.1.6, §5.3 (Phase 4 — Validation Phase)
- `ARCHITECTURE.md` §1.5.4 forbidden vocabulary (binding on every text artifact this campaign produces)
- `CLAUDE.md` §6 binding rules; §7 forbidden vocabulary; §8 commits and workflow; §9 pitfalls (esp. #1 `model_id` vs `model_version_returned`, #11 webhook secrets)
- `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md` (parked v2 phrasing — consumed under Q2)
- `docs/status/2026-05-05-phase4a-recovery-report.md` §7.3, §7.4 (forward-carry diagnostics)
- `memory/project_failures_are_findings.md` (extended to prompt iteration under §3 below)
- `HOSTING_AND_DEV_OPS.md` (VPS Linode lsb-agent-02; wall-clock context)

Predecessor plan in this thread: `docs/status/2026-05-07-no-human-baseline-amendment-architect-plan.md`.

---

## §1. What Phase 4b is, framed honestly

Per philosophy doc §2:

> "The originating question is exploratory: *'what happens if you give a large language model a CDA free-list / pile-sort / interview? What comes out?'*"

Phase 4b is the variance-and-saturation arm of that question. It **is the binding G1 stability gate** for the Phase 4 close. It also produces, as canonical research data, the largest single LSB collection event to date: 20 frontier models × 8 prompt variants × N=5 cells across `family` and `holidays`, plus a saturation analysis on a smaller reference subset, plus the diagnostic ride-along for outstanding Phase 4a tail items.

Per philosophy doc §9, this is **release-for-community-analysis material from the moment it is collected**. Every cell — pass, fail, refusal, partial — is appended to `data/raw/informants.jsonl` (or `data/raw/failures.jsonl` for hard failures) with full provenance and intended for the open data bundle. **No `non_canonical` labeling**. No probe banner. The shakedown protocol does not apply because Phase 4b is not pre-Phase-4a; it is Phase 4b proper, with Mark's binding directive ("Treat this as a real data collect that will be saved for research purposes") overriding the §5.3 "2 reference models" constraint that predates the directive.

The G1 split-axis logic, the 0.5 threshold, the variant-expansion runbook, the saturation structure — all unchanged from `ARCHITECTURE.md` §5.3. What changes: the slate (12 → 20), the cell volume, and the failures-as-findings extension to **prompt iteration itself**.

---

## §2. Deliverables (precise)

1. **Canonical informant data — variance arm.** ~1,600 cells = 20 models × 8 variants × N=5 × 2 domains. Appended to `data/raw/informants.jsonl`. Hard failures land in `data/raw/failures.jsonl`. Each record carries `prompt_version` ∈ {v1_s1 … v1_s8} (or v1_s* + v2_s* if Q2 expands the variant set) and `qa_notes` substring `campaign_id=phase4b-real-2026-05-MM`.

2. **Canonical informant data — saturation arm.** 3 reference models × 2 domains × N ∈ {5,10,15,20,25,30} = 360 cells. Same corpus. `prompt_version=v1` (the canonical one). `qa_notes` substring `campaign_id=phase4b-saturation-2026-05-MM`.

3. **Diagnostic ride-along outputs.**
   - phi-4 adapter fix (per-model adaptive `max_tokens`) + 6-cell rerun.
   - gpt-5.4-mini ×2 + mistral-small ×1 root-cause investigation; rerun the 3 cells if root cause is fixable, otherwise document with verbatim capture as `failures-as-findings` data.

4. **G1 results written into `DomainResult`.** All six fields populated for `family` and `holidays`: `g1_salience_stability`, `g1_spatial_stability`, `g1_aggregate_stability`, `g1_salience_pass`, `g1_spatial_pass`, `g1_overall_pass`. Plus per-model stability ratios surfaced as a diagnostic table (Q3).

5. **Saturation curves.** Per §4.2.7: Spearman salience stability, OCI convergence, elbow-position stability, MDS Procrustes RMSE at N vs N+5. Knee + 20% safety margin → operational N. Findings written into the Phase 4b completion report and surfaced on the methodology page in Phase 6 as a named methods contribution (per §1.5.6).

6. **Prompt-evolution log** — new file at `docs/PROMPT_EVOLUTION_LOG.md`. Schema in §5.

7. **Phase 4b completion report** — `docs/status/2026-05-MM-phase4b-completion.md` (date-stamped on the day the closure runs). G1 verdict, saturation knee, ride-along outcomes, corpus delta, cost reconciliation, gate chain.

8. **Updated `docs/status/` audit trail** — every Coder commit gets a Reviewer + Tester verdict pair.

---

## §3. The 20-model slate

The Phase 4a slate (12 models per registry §3.2) is preserved as the spine. Eight additional frontier models are added to reach 20. Selection rationale: maximize three-axis spread (origin × openness × collection method) per ARCHITECTURE.md §3.2, while remaining inside existing adapter coverage (no new adapter work for the variance arm). The 12 Phase 4a slate members are read off `data/models/registry.json` rows that have non-zero `records` plus the four that were enrolled but unreached.

**Phase 4a slate (12, unchanged):**

| # | model_id | family | origin | open | collection_method |
|---|---|---|---|---|---|
| 1 | `anthropic/claude-opus-4.6` | claude | us | no | `anthropic_api` |
| 2 | `anthropic/claude-sonnet-4.6` | claude | us | no | `anthropic_api` |
| 3 | `openai/gpt-5.4` | gpt | us | no | `openai_api` |
| 4 | `openai/gpt-5.4-mini` | gpt | us | no | `openai_api` |
| 5 | `google/gemini-2.5-pro` | gemini | us | no | `google_ai` |
| 6 | `x-ai/grok-4.20` | grok | us | no | `xai_api` (via OpenRouter) |
| 7 | `meta-llama/llama-4-maverick` | llama | us | yes | `openrouter` |
| 8 | `mistralai/mistral-small-2603` | mistral | eu | no | `openrouter` |
| 9 | `qwen/qwen3.6-plus` | qwen | cn | yes | `openrouter` |
| 10 | `deepseek/deepseek-v3.2` | deepseek | cn | yes | `openrouter` |
| 11 | `z-ai/glm-5.1` | glm | cn | no | `openrouter` |
| 12 | `microsoft/phi-4` | phi | us | yes | `openrouter` |

**Eight added for Phase 4b (20-model slate):**

| # | model_id | family | origin | open | collection_method | rationale |
|---|---|---|---|---|---|---|
| 13 | `anthropic/claude-opus-4.5` | claude | us | no | `anthropic_api` | within-family drift surface (4.5 vs 4.6); already in registry |
| 14 | `openai/gpt-5.2` | gpt | us | no | `openai_api` | within-family drift surface; already in registry |
| 15 | `google/gemini-2.5-flash` | gemini | us | no | `google_ai` | flash vs pro tier within Google |
| 16 | `x-ai/grok-4` | grok | us | no | `openrouter` | within-family drift (4 vs 4.20) |
| 17 | `meta-llama/llama-4-scout` | llama | us | yes | `openrouter` | scout vs maverick within Llama 4 |
| 18 | `mistralai/mistral-large-2512` | mistral | eu | no | `openrouter` | large vs small tier within Mistral |
| 19 | `cohere/command-a` | command | ca | no | `openrouter` | new family (Cohere); CA origin axis |
| 20 | `google/gemma-4-26b-a4b-it` | gemma | us | yes | `openrouter` | Google open-weight tier (distinct from Gemini) |

All 20 are inside existing adapter coverage. No new adapter is required for the variance arm. Phi-4 needs the per-model max-tokens fix (§7) before it can be reached at variant volume.

**Per CLAUDE.md §9 pitfall 1:** every cell records both `model_id` (the alias above, e.g. `anthropic/claude-opus-4.6`) and `model_version_returned` (the exact provider version string returned in the API response). The variance arm groups by `model_id`; the longitudinal Phase 6 view groups by `model_version_returned`. The Coder writes both; the analysis layer joins on the right one for the right question.

**Q1 to SME (slate composition):** is the 20-model slate above accepted, with rationale? Architect rec: PASS. The eight additions preserve the three-axis spread the SME approved for Phase 4a, add three within-family drift surfaces (4.5↔4.6, 5.2↔5.4, 4↔4.20) which are scientifically interesting in their own right, and keep all 20 inside existing adapter coverage so no Coder cycles go to new transports.

---

## §4. The 8 prompt variants

**Existing state.** The `packages/cdb_collect/cdb_collect/prompts/` tree already contains v1 (canonical) plus v1_s1 through v1_s8 directories — 8 paraphrased variants of `free_list.md`, `pile_sort.md`, `pile_interview.md`. The variants are **already on disk and canonical-tracked**; they were authored before this plan. The Coder does not generate new variant text. This plan **uses v1_s1 … v1_s8 as the eight variants**.

Per CLAUDE.md §6 R12 / §6 R8: prompt templates are versioned and never edited in place; the variants are read-only inputs to this campaign.

**The parked v2 free-list observation (Mark, 2026-05-06).** Mark's "this is a silent task, please try to avoid interjecting commentary as you make the list" softer phrasing was parked at the time as a Phase 5+ comparison study, not a v1_s* variant. Inspection of the existing v1_s1…v1_s8 files confirms: **all 8 retain imperative anchor phrasing** ("Do not explain or categorize," "no commentary," "Refrain from adding any notes"). None embody the softer request-shaped phrasing.

**Q2 to SME (variant composition):** three options. Architect rec: **(B)**.

- **(A) Run as-is, 8 variants.** Use the existing v1_s1…v1_s8 set unmodified. The G1 study measures stability across rephrased imperative anchors. Defers the parked v2 observation to a future study.
- **(B) Add a v2 softer-phrasing arm — 9 total variants.** Add a single new variant directory `v2_soft1/` (Mark's exact parked phrasing, applied across free-list / pile-sort / pile-interview). Keep all 8 v1_s* variants. The G1 study now measures stability across **both** within-imperative-family rephrasings (8 of them) and one cross-family contrast (the 9th). Within-family vs across-family salience stability becomes a diagnostic sub-finding, not the binding gate. **Architect rec.**
- **(C) Run two cohorts.** 8 v1_s* + 8 v2_s*. Doubles the cell count (~3,200 cells) for diminishing return on the gate question. Architect-not-rec — out of proportion to the gate's question.

If SME selects (B): the 9th variant is **single-arm** (one prompt-version directory), not 8 paraphrases of the soft form. The cross-family contrast comes from comparing the v2_soft1 cluster against the within-v1_s* cluster, not from rephrasing within v2.

The v2_soft1 prompt text the Coder will use, for SME inspection (not new methodology — verbatim from the parked status doc):

```
This is a silent task. Please try to avoid interjecting commentary as
you make the list of {{domain_seed}}. Use a numbered list, one item
per line, up to 200 items.
```

(Pile-sort and pile-interview soft-form bodies follow the same imperative→request transformation and are drafted by Mark or the Architect-as-author before T1 lands; the Coder does not generate prompt text.)

---

## §5. The prompt-evolution log

**Path:** `docs/PROMPT_EVOLUTION_LOG.md`
**Tracked:** yes (committed)
**Append-only:** yes (by convention; no CI gate, but Reviewer rejects in-place edits to existing entries)
**Update cadence:** one entry per prompt version directory creation; one per campaign run that consumed a version; one per documented G1 / success-rate inflection.

**Entry schema** (markdown, one section per prompt version, one row per (campaign × variant × model) success-rate datum):

```markdown
## v1 — canonical baseline
- **Created:** 2026-04-22 (Phase 4a launch)
- **Path:** packages/cdb_collect/cdb_collect/prompts/v1/
- **Origin:** initial v1 design (see PHASE_0_TASKS.md)
- **Status:** canonical; never edited in place

### Campaigns that consumed v1
| campaign_id | model_id | domain | N | passed | failed | success_rate |
|---|---|---|---:|---:|---:|---:|
| phase4a-2026-04-22 | anthropic/claude-opus-4.6 | family | 5 | 5 | 0 | 1.00 |
| ... | ... | ... | ... | ... | ... | ... |

## v1_s1 — paraphrase 1 (research-project framing)
- **Created:** 2026-04-?? (pre-existing on disk)
- **Path:** packages/cdb_collect/cdb_collect/prompts/v1_s1/
- **Origin:** sensitivity-study variant set; imperative anchor preserved
- **Authored by:** [Mark / Architect-as-author — fill at log creation]
- **Reason for creation:** Phase 4b sensitivity arm requires 8 paraphrased variants per §5.3
- **Status:** canonical; never edited in place

### Campaigns that consumed v1_s1
| campaign_id | model_id | domain | N | passed | failed | success_rate |
| phase4b-real-2026-05-MM | ... | ... | ... | ... | ... | ... |
```

**The "why a new version" rule.** A new prompt-version directory under `packages/cdb_collect/cdb_collect/prompts/` may be created **only** when one of:
1. A new SME-approved sensitivity study requires it (the 8 v1_s* variants are an instance);
2. A model's per-(model × domain × variant) success rate drops below 0.90 on **two consecutive collection campaigns** under v1, prompting a phrasing iteration. The new version's `Reason for creation` field cites the failure pattern verbatim. **No mid-Phase-4b iteration**: the campaign runs once at v1_s1…v1_s8 (or +v2_soft1), reports the success rates, and the log records them. If success rates trigger a v2 iteration, that iteration is a separate, post-Phase-4b campaign with its own Architect plan.
3. An SME-approved cross-family contrast study (Q2 option B is an instance — v2_soft1).

**The 0.90 success-rate threshold (Q7).** Mark named "90% successful response" in the directional change. Architect rec: success rate is computed **per (model × variant × domain)** triple after the variance-arm cells complete. A triple is "successful" when its 5-of-5 cells produced valid `InformantRecord` records (i.e., not in `failures.jsonl`). Triples below 0.80 fire an alert into the prompt-evolution log; triples below 0.60 are flagged on the methodology page as known weak-coverage cells. This metric does **not** gate G1 — G1 is computed against whatever records exist, with insufficient-coverage triples surfaced in the gate diagnostic. Per failures-as-findings, low success rate is a finding, not a kill switch.

**Q5 to SME (log schema):** is the schema above accepted? Architect rec: PASS. The schema captures the three things Mark asked for (which version when, why a new version, success rate per cell) and integrates with the existing `prompt_version` schema field on `InformantRecord` (no new schema change required).

**Q7 to SME (success-rate definition):** is per-(model × variant × domain) at 5-of-5 the right granularity, with 0.80 alert / 0.60 flag thresholds, non-gating? Architect rec: PASS as stated.

---

## §6. The saturation analysis

Structure unchanged from `ARCHITECTURE.md` §5.3 / §4.2.7. **Three reference models × 2 domains × N ∈ {5, 10, 15, 20, 25, 30}** = 6 N-points × 3 models × 2 domains = 36 (model, domain, N) curves' worth of cells = **3 × 2 × (5+10+15+20+25+30) = 630 collection runs** at N counted as the **maximum N**, not the sum (each curve up to 30 needs 30 runs total per (model, domain), reused across the lower-N points). So actual collection: 3 × 2 × 30 = **180 runs**.

**Three reference models** (default, unchanged):
- `anthropic/claude-opus-4.6` (frontier closed reference)
- `openai/gpt-5.4` (cross-vendor frontier reference)
- `meta-llama/llama-4-maverick` (open-weight reference; replaces "Llama 3.1 70B" in §4.2.7 because Llama 3.1 70B is not in the registry and 4-maverick is the closest in-slate equivalent)

**Q4 to SME (saturation slate expansion):** keep at 3 models or expand to 5 / all 20? Architect rec: **keep at 3**. The saturation finding is "operational N for the within-model Register 1 analysis"; it is a methodology-page named contribution, not a per-model claim. Three references span the closed-frontier / cross-vendor-frontier / open-weight axes that matter for the operational-N decision. Expanding to 20 models multiplies cells by ~6.7× for diminishing scientific return — the curves cluster tightly across vendors per the v0.7 prior.

`prompt_version=v1` (the canonical one) for the saturation arm, not the v1_s* variants. The saturation question is independent of prompt phrasing and uses v1 as the anchor.

---

## §7. Diagnostic ride-along

Three sub-tasks fold into the Coder decomposition (§8) without becoming separate phases.

### §7.1 phi-4 adapter — per-model adaptive max-tokens

**Problem (recovery report §7.4).** Phi-4 has 16K total context. The `max_tokens=16384` cap from Task #16 collides with the input-prompt context, blowing past the model's window in 5 of 6 Phase 4a cells (HTTPStatusError) plus 1 ValueError.

**Architect rec.** Add a **per-model adaptive max-tokens computation** to the runner: `effective_max_tokens = min(MAX_OUTPUT_TOKENS_CONFIG, max(1024, model.context_length - estimated_input_tokens - safety_margin))`. The safety margin is 512 tokens; `estimated_input_tokens` uses the existing tokenizer adapter (or a 4-chars-per-token approximation if no tokenizer is available). Phi-4's effective cap becomes ~14000 in practice. Implementation under `packages/cdb_collect/cdb_collect/runner.py` (or a sibling helper).

After the fix lands, rerun the 6 phi-4 cells with `campaign_id=phase4b-phi4-rerun-2026-05-MM`. If they still fail, document as failures-as-findings; do **not** drop phi-4 from the 20-slate variance run (it can still produce variance-arm cells at the new effective cap).

### §7.2 gpt-5.4-mini ×2 + mistral-small ×1 root cause

**Problem (recovery report §7.3).** Stage 1.5b probe found these failures are **not** cap-related. Root cause unknown.

**Architect rec.** A diagnostic Coder task that:
1. Reads `data/raw/failures.jsonl` rows for the 3 cells; captures verbatim `error_message`, `error_type`, `request_id`.
2. Re-issues each cell against the corrected instrument (T16 cap fix already applied; this is a re-attempt under the new normal).
3. If failures persist, classify each into: (a) transport / API issue (fix → rerun), (b) provider-side content/policy decline (capture verbatim → record as `failures-as-findings`), (c) parser issue (fix in adapter → rerun).
4. Write a one-page diagnostic memo at `docs/status/2026-05-MM-phase4b-tail-failures-memo.md` summarizing the three cells' root cause classifications, regardless of outcome.

If the re-attempts succeed at the post-T16 instrument, the cells are appended as canonical (`campaign_id=phase4b-tail-rerun-2026-05-MM`). If they fail again with provider-side declines, the verbatim refusals are themselves data per the failures-as-findings posture.

### §7.3 Ride-along ordering

Both ride-along sub-tasks land **before** the main 20×8 variance run, so the runner's adaptive cap is in place and the failure tail is dispositioned before the largest collection event begins. They do not gate G1 — the variance run can proceed even if the 9 ride-along cells remain unrecovered — but they reduce noise in the §11 cost reconciliation.

---

## §8. Coder decomposition

Eight tasks. Each one is implementable in a single Coder session, ends with one commit, gets one Reviewer + one Tester verdict. The Architect is not in the implementation chain after this plan PASSes SME.

| # | Task | Scope | Acceptance criteria | Dependencies |
|---|---|---|---|---|
| **T1** | Prompt-evolution log scaffold | Create `docs/PROMPT_EVOLUTION_LOG.md` per §5 schema. Backfill v1 + v1_s1…v1_s8 entries (creation date, path, status). No campaign rows yet (those land per-T as runs complete). If Q2 = (B): also create `packages/cdb_collect/cdb_collect/prompts/v2_soft1/` with the three soft-form prompt files (text supplied by Mark or Architect-as-author at T1 dispatch — Coder does not write prompt text). | (a) File exists with the v1 + 8 v1_s* sections. (b) If Q2=(B), v2_soft1/ directory present with 3 .md files. (c) No `informants.jsonl` change. | None |
| **T2** | phi-4 adaptive max-tokens fix + 6-cell rerun | Implement adaptive max-tokens per §7.1. Add unit tests against fixtures. Rerun the 6 phi-4 cells from Phase 4a with `campaign_id=phase4b-phi4-rerun-2026-05-MM`. Append outcomes to log. | (a) Helper added with tests. (b) Tests pass; no real API calls in tests. (c) 6 cells rerun; outcomes appended to `informants.jsonl` (PASS) or `failures.jsonl` (FAIL); each carries the campaign_id tag. (d) Log entry recorded. (e) `qa_check.py` clean on the 6 new rows. | T1 |
| **T3** | gpt-5.4-mini ×2 + mistral-small ×1 root-cause investigation | Per §7.2. Diagnose, re-attempt under post-T16 instrument, classify, write memo. | (a) `docs/status/2026-05-MM-phase4b-tail-failures-memo.md` exists with the three-cell root-cause classification. (b) Each cell appended to `informants.jsonl` (recovered) or `failures.jsonl` (refused/transport-failed) with `campaign_id=phase4b-tail-rerun-2026-05-MM`. | T1 |
| **T4** | 20-model × 8-variant variance collection | Drive the variance arm: 20 models × 8 (or 9) variants × 5 runs × 2 domains. `prompt_version` cycles through v1_s1…v1_s8 (and v2_soft1 if Q2=B). `campaign_id=phase4b-real-2026-05-MM`. Mark's standing $10 rule does not apply (real campaign per philosophy doc §9); the campaign runs under the standing $300/mo cap with `CDB_MAX_SPEND_USD=50` session export. QA_Runner monitors per §4.1.6; `#lsb-alerts` gets QA failures in real time. | (a) ~1,600 (or 1,800 if Q2=B) cells appended to `informants.jsonl` and/or `failures.jsonl`, all carrying the campaign_id tag. (b) Per-(model × variant × domain) success rates computed and appended to `docs/PROMPT_EVOLUTION_LOG.md`. (c) `qa_check.py` clean on the post-campaign corpus. (d) No real-API calls in tests; campaign runs are explicit production runs, not test runs. | T1, T2, T3 |
| **T5** | Saturation arm collection | 3 reference models × 2 domains × N up to 30 = 180 runs at `prompt_version=v1`, `campaign_id=phase4b-saturation-2026-05-MM`. | (a) 180 cells appended. (b) `qa_check.py` clean. (c) Log entry recorded. | T4 |
| **T6** | G1 SplitResult + saturation analysis | Run `scripts/analyze.py` with the post-campaign corpus. Compute G1 via existing `gates.g1_stability_split`; compute saturation curves per §6 (Spearman salience stability, OCI convergence, elbow-position stability, MDS Procrustes RMSE at N vs N+5); identify knee + 20% safety margin; write all results into `data/results/family/0.3.json` and `data/results/holidays/0.3.json` (analysis version 0.3). Also produce a per-model G1 diagnostic table per Q3. | (a) 0.3.json exists for both domains with the six G1 fields populated. (b) Per-model G1 ratios in a diagnostic block. (c) Saturation knees identified for both domains × 3 models = 6 curves. (d) Tests for the saturation knee detector against fixtures. | T4, T5 |
| **T7** | Phase 4b completion report | Author `docs/status/2026-05-MM-phase4b-completion.md`. Sections: timeline, gate status (G1 PASS/FAIL with both axes), saturation knee, ride-along outcomes (T2, T3), corpus delta, cost reconciliation, success-rate distribution from log, what Phase 4b does and does not change, next steps. The report is binding methodology text and is subject to **content** SME review (not just plan SME). | (a) Report drafted. (b) `#lsb-cda-sme` notified for content review. (c) After SME PASS, gate-chain verdicts cross-linked. | T6 |
| **T8** | Prompt-evolution log final pass + Phase 4b closure | Final pass through `docs/PROMPT_EVOLUTION_LOG.md`: every v1_s* variant has its campaign rows from T4; v1 has its rows from T5; v2_soft1 (if applicable) has its rows from T4. Architect closes Phase 4b in `docs/status/`. If any G1 axis fails on either domain, the §5.3 runbook activates and Q8's posture applies. | (a) Log fully populated. (b) Phase 4b closure note added to the completion report. (c) If G1 failed: a Phase 4b G1-failure diagnostic memo per §5.3 + Q8. | T7 |

**Q3 to SME (per-model G1 reporting):** with 20 models we can report a per-model G1 stability vector alongside the aggregate. Architect rec: **report both**. The aggregate (within-mean / between) is the binding gate per §5.3. The per-model vector is a diagnostic — it surfaces which models' output distributions are most prompt-stable and is interesting in its own right per the philosophy doc §7 item 3 ("stability under prompt rephrasing"). Per-model vector is **not** a gate; reporting only.

---

## §9. Cost transparency (not authorization-blocking)

Per `memory/feedback_test_budget.md`: the standing $10 rule is for probes. Phase 4b is a real collection campaign, surfaced transparently for Mark's awareness, not gated by cost.

**Variance arm (T4):** ~1,600–1,800 cells. Phase 4a recovery rate was $0.06/cell weighted-average across the 12-slate. Variance arm conservative estimate at $0.06–$0.15/cell (8 added models include three reasoning-heavy frontier models — Opus 4.5, GPT-5.2, Grok-4 — that price higher than the slate weighted average): **$100–$270**.

**Saturation arm (T5):** 180 cells × $0.10/cell average across the 3-reference subset = **$15–$25**.

**Ride-along (T2, T3):** 9 cells. Below noise floor; **<$5**.

**Total Phase 4b estimate: $120–$300.**

This sits comfortably under the $300/month cap (`ARCHITECTURE.md` §6.2). `CDB_MAX_SPEND_USD=50` per session is the operational guard; multiple sessions are expected. Mark sees this section and acts if the upper bound is too high.

**Wall-clock estimate.** Phase 4a recovery ran 20 cells in ~60 minutes. Naive scaling: 1,800 cells × 3 minutes/cell = ~90 wall-clock hours sequentially. With parallel collection across the 8 variants per model (within-provider rate-limit-respecting), realistic wall-clock for T4: **2–4 days of campaign time on Linode lsb-agent-02**, run in tranches that respect provider rate limits and the session $50 cap. T5 is ~6–10 hours. T2 and T3 are <30 minutes each. **Total Phase 4b campaign wall-clock: ~3–5 days, distributed across ~1 week of operator time**.

---

## §10. Q8 — the major SME question on G1-failure posture

**The standing §5.3 runbook says:** if any gate fails, pause; Architect writes a diagnostic; Mark decides whether to redesign prompts, add runs, drop models, or shelve the project.

**The post-philosophy-doc posture (philosophy doc §9, failures-as-findings):** every cell — pass, fail, refusal, partial — is canonical. Even G1 failure is a finding: it would mean the within-model prompt variance is comparable to or exceeds the between-model variance, which would itself be a publishable observation about how frontier LLMs respond to CDA stimuli.

**The tension.** Phase 4 was designed when LSB still had a "no human baseline" question open and a thesis-shaped commitment. The 2026-05-07 amendment removed the thesis. Under the new exploratory framing, "the gate failed" stops meaning "the project doesn't work" and starts meaning "here is a finding the methodology page must surface."

**Architect rec for Q8 (SME's call):** the G1 gate **stays binding for the dashboard's "validated comparison" framing** but **does not stop the project**. Concretely:
- If G1 PASSes: dashboard ships with normal "the comparison is stable across prompt variants" framing.
- If G1 FAILs on one axis: methodology page surfaces the per-axis result honestly. Dashboard shows the per-model G1 ratios as a first-class diagnostic. The §5.3 variant-expansion runbook still triggers (expand to 16+ variants on the affected model pair) **before** disqualifying the domain — but disqualification stops being an option under the failures-as-findings posture; "G1 failed and we surface it" becomes the new option.
- If G1 FAILs on both axes: same as above plus a methodology-page header note framing the within-model variance as itself a finding. Phase 5 still proceeds. The dashboard's lede on every visualization includes the G1 result.

The §5.3 line "we do not ship a pretty visualization layer over data we haven't validated" remains binding — but the validation now means "the variance is **measured and surfaced**," not "the variance is **below threshold**." This is consistent with philosophy doc §9: "the data is more valuable than our interpretation of it."

This is the major question for the SME. If the SME prefers the original "G1 fails → pause and decide" runbook, Phase 4b's T8 includes the standing diagnostic memo path. If the SME accepts the failures-as-findings reframe, T8 covers either branch. **Architect's preference: failures-as-findings reframe**, because the philosophy doc already binds the project's framing in that direction.

---

## §11. Forbidden scope creep

Phase 4b does **not** include:
- Phase 5 work (publish layer, dashboard JSON build, React visualizations, methodology page authoring);
- The methodology-page UI rendering of G1 results (Phase 6 task, separately UI/UX-gated);
- A v2 prompt comparison study **except** as a single soft-form arm (v2_soft1) under Q2 option (B);
- Any reframe of the no-human-baseline amendment (already binding from `ARCHITECTURE.md` v0.7.2);
- Any new schema field on `InformantRecord` or `GroundingRef` (no schema change required);
- Any new dependency.

The Coder pauses and surfaces to the Architect if any of the above becomes apparently required during execution.

---

## §12. Gate verdict file paths (deterministic)

| Stage | Verdict file path |
|---|---|
| Plan-level SME verdict | `docs/status/2026-05-MM-phase4b-cda-sme-plan-verdict.md` |
| T1 Reviewer / Tester | `docs/status/2026-05-MM-phase4b-t1-{reviewer,tester}-verdict.md` |
| T2 Reviewer / Tester | `docs/status/2026-05-MM-phase4b-t2-{reviewer,tester}-verdict.md` |
| T3 Reviewer / Tester | `docs/status/2026-05-MM-phase4b-t3-{reviewer,tester}-verdict.md` |
| T4 Reviewer / Tester | `docs/status/2026-05-MM-phase4b-t4-{reviewer,tester}-verdict.md` |
| T5 Reviewer / Tester | `docs/status/2026-05-MM-phase4b-t5-{reviewer,tester}-verdict.md` |
| T6 Reviewer / Tester | `docs/status/2026-05-MM-phase4b-t6-{reviewer,tester}-verdict.md` |
| T7 Reviewer / Tester | `docs/status/2026-05-MM-phase4b-t7-{reviewer,tester}-verdict.md` |
| T7 SME content verdict | `docs/status/2026-05-MM-phase4b-cda-sme-content-verdict.md` |
| T8 Reviewer / Tester | `docs/status/2026-05-MM-phase4b-t8-{reviewer,tester}-verdict.md` |

UI/UX gate **not required** for Phase 4b — no frontend artifact in scope.

---

## §13. Open questions for the SME (consolidated)

| # | Question | Architect rec |
|---|---|---|
| Q1 | Is the 20-model slate (Phase 4a 12 + 8 named in §3) accepted? | PASS as listed |
| Q2 | Variant composition — (A) 8 v1_s*, (B) 8 v1_s* + 1 v2_soft1, (C) 8 v1_s* + 8 v2_s*? | (B) |
| Q3 | Per-model G1 reporting alongside aggregate gate? | YES, diagnostic only, aggregate remains binding |
| Q4 | Saturation slate — keep at 3 or expand? | KEEP at 3 |
| Q5 | Prompt-evolution log schema (§5)? | PASS as drafted |
| Q6 | campaign_id naming — `phase4b-real-2026-05-MM` for variance, `phase4b-saturation-2026-05-MM` for saturation, `phase4b-phi4-rerun-2026-05-MM` and `phase4b-tail-rerun-2026-05-MM` for ride-along? | PASS as drafted |
| Q7 | 90% success-rate definition: per-(model × variant × domain) at 5-of-5; alert <0.80; flag <0.60; non-gating? | PASS as drafted |
| Q8 | G1-failure response posture under failures-as-findings — variant expansion + surface, no project pause? | **YES — failures-as-findings reframe**; SME's call. If SME prefers original §5.3 runbook, T8 covers that branch. |

Posted to `#lsb-cda-sme` for review on dispatch.

---

*End of Phase 4b Architect plan. Awaiting CDA SME verdict before Coder dispatch.*
