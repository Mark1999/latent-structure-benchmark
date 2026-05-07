# Phase 4a Completion Report — Redo (Post-Recovery Corpus)

**Date:** 2026-05-07
**Scope:** Phase 4a closure under the post-recovery corpus (121 informants; 20 recovery rows)
**Predecessor completion report:** `docs/status/2026-04-23-phase4a-completion.md` (preserved as
audit; correct against its input population; this report is its successor, not a replacement)
**Analysis report:** `docs/status/2026-05-07-phase4a-t5-redo-analysis-report.md` (§1–§10)
**T5 redo plan:** `docs/status/2026-05-06-t5-redo-architect-plan.md` (commit `2a4c6c2`)
**SME plan verdict:** `docs/status/2026-05-06-t5-redo-cda-sme-plan-verdict.md` (commit `86ad713`; T11–T15 binding)
**RD-3 reframing memo:** `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md` (commit `93a544f`; Note K REPLACED)

**Relationship to predecessor:** The 2026-04-23 completion report was correct against the
2026-04-22 corpus (101 informants, 10 family models, 8 holidays models). The redo is correct
against the post-recovery corpus (121 informants, 11 family models, 9 holidays models). Both
reports stand on master as audit. The analytical delta between them reflects the 2026-05-05
recovery campaign's population shift, not a methodological correction. No `.SUPERSEDED.md`
annotation is applied to the predecessor (the predecessor is not superseded; the corpus changed;
both analyses are internally consistent against their respective input populations).

---

## §1. Timeline and key commits

| Event | Date | Commit / Reference |
|---|---|---|
| Phase 4a original completion report | 2026-04-23 | `docs/status/2026-04-23-phase4a-completion.md` |
| Task #16 — adaptive `max_tokens` fix | 2026-05-04 | T16 commits; CDA SME verdict `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (S1–S5) |
| Phase 4a recovery campaign (20 cells at 100% rate) | 2026-05-05 | commit `3634e52`; report `docs/status/2026-05-05-phase4a-recovery-report.md` |
| T4 redo RD-3 — Note K REPLACED | 2026-05-06 | commit `93a544f`; memo `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md` |
| RD-3 CDA SME content verdict (S5-completing PASS-WITH-NOTES) | 2026-05-06 | `docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md` |
| T5 redo Architect plan | 2026-05-06 | commit `2a4c6c2`; `docs/status/2026-05-06-t5-redo-architect-plan.md` |
| T5 redo SME plan verdict (PASS-WITH-NOTES; T11–T15) | 2026-05-06 | commit `86ad713`; `docs/status/2026-05-06-t5-redo-cda-sme-plan-verdict.md` |
| RD-T5-1 — build_db.py rerun (SQLite rebuilt, R5 discharged) | 2026-05-07 | commit `fda4ed7` |
| RD-T5-2 — analysis pipeline 0.2 JSON produced | 2026-05-07 | commit `63b0f9a` |
| RD-T5-3 — analysis report §1–§7 (numerics) | 2026-05-07 | commit `5128e94`; `docs/status/2026-05-07-phase4a-t5-redo-analysis-report.md` |
| **RD-T5-4 — §8–§10 + this completion-redo report** | **2026-05-07** | **this commit** |

---

## §2. Gate status summary

### Gates from original Phase 4a (audit; all PASS or PASS-WITH-NOTES)

The gate chain from the 2026-04-23 completion report is preserved verbatim at
`docs/status/2026-04-23-phase4a-completion.md` §2. All original gates PASSed; none are
re-litigated here.

### Additional gates introduced after original completion

| Task | Gate(s) | Verdict | Reference |
|---|---|---|---|
| Task #16 (adaptive `max_tokens`) | CDA SME | PASS-WITH-NOTES (S1–S5) | `docs/status/2026-05-04-task-16-cda-sme-verdict.md` |
| Phase 4a recovery plan | CDA SME | PASS-WITH-NOTES (R1–R6) | `docs/status/2026-05-05-phase4a-recovery-cda-sme-verdict.md` |
| T4 redo (RD-1/RD-2/RD-3) | CDA SME (plan + content) | PASS-WITH-NOTES; T1–T10 binding | `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md`, `docs/status/2026-05-06-t4-redo-rd3-cda-sme-plan-verdict.md`, `docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md` |
| T5 redo plan | CDA SME | PASS-WITH-NOTES (T11–T15) | `docs/status/2026-05-06-t5-redo-cda-sme-plan-verdict.md` |
| RD-T5-1 (build_db.py rerun) | Reviewer + Tester | PASS | (Reviewer commit hash in analysis report §6.5) |
| RD-T5-2 (pipeline 0.2 JSON) | Reviewer + Tester | PASS | commit `63b0f9a` gate chain |
| RD-T5-3 (numerics report §1–§7) | Reviewer + Tester | PASS | commit `5128e94` gate chain |
| RD-T5-4 (§8–§10 + this report) | Reviewer + Tester | pending | — |
| T5 redo SME content verdict | CDA SME | **PENDING** (gate chain step 3) | `docs/status/2026-05-06-phase4a-t5-redo-cda-sme-content-verdict.md` |

Phase 4a is **conditionally closed** subject to the CDA SME content verdict at gate chain step 3
(T5 redo analysis report §8–§10). A PASS or PASS-WITH-NOTES at that gate closes Phase 4a at
the analytical layer.

---

## §3. Data artifacts

### §3.1 `data/raw/informants.jsonl` — post-recovery state

| Metric | Value |
|---|---|
| Total records | **121** |
| Recovery rows (`qa_notes` contains `phase4a-recovery-2026-05-05`) | **20** |
| `qa_passed=True` | ≥ 87 (exact count: 74 original + 13 newly QA-passed recovery rows; see analysis report §6.3) |
| `qa_passed=False` | ≤ 34 (recovery glm-5.1 rows returned `qa_passed=False` due to empty-freelist-propagation bug; see analysis report §6.2) |
| Family domain QA-passed records fed to pipeline | **48** |
| Holidays domain QA-passed records fed to pipeline | **39** |

The original completion report §3.1 reported 101 total records and 74 `qa_passed=True`. The
redo adds 20 recovery rows; the family and holidays pipeline feeds increased from 41 and 33 to
48 and 39 respectively.

### §3.2 `data/results/family/0.2.json`

| Field | Value |
|---|---|
| `n_models` | **11** |
| `n_records` (QA-passed) | **48** |
| `consensus_type` | `STRONG_CONSENSUS` |
| `romney_eigenratio` | **12.0984** |
| `romney_small_n_warning` | **`True`** (n=11 < 15) |
| `consensus_score` | **0.7107** |
| `consensus_ci` | **[0.5049, 0.9092]** |
| `negative_centrality_flag` | `False` |
| `g1_overall_pass` | `None` (Phase 4b required) |
| `groundings` | `[]` (Phase 4c required) |

Full field set in the analysis report §4.1.

### §3.3 `data/results/holidays/0.2.json`

| Field | Value |
|---|---|
| `n_models` | **9** |
| `n_records` (QA-passed) | **39** |
| `consensus_type` | `STRONG_CONSENSUS` |
| `romney_eigenratio` | **10.1520** |
| `romney_small_n_warning` | **`True`** (n=9 < 15) |
| `consensus_score` | **0.7757** |
| `consensus_ci` | **[0.4717, 0.9647]** |
| `negative_centrality_flag` | `False` |
| `g1_overall_pass` | `None` (Phase 4b required) |
| `groundings` | `[]` (Phase 4c required) |

Full field set in the analysis report §4.2.

### §3.4 Cell coverage under post-recovery corpus

See the analysis report §6.4 for the full cell-coverage denominator. Summary:

| Category | Count |
|---|---|
| Analyzable cells (≥1 QA-passed record) | **20** (11 family + 9 holidays) |
| All-QA-failed cells | **5** (qwen × {family, holidays}; grok-4 × holidays; glm-5.1 × {family, holidays}) |
| Zero-record cells (model not run for domain) | **1** (phi-4 × holidays; T3 canary scope) |

5 cells produced no interpretable primary-step output; follow-up decline-interview data for
these cells was captured in Phase 4a.1, and the interpretation of those follow-ups is in the
RD-3 reframing memo (`docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md`).

The original completion report §3.5 described "18 analyzable + 5 decline-interviewable" with
"1 zero-record" (Gemini × family). Under the post-recovery corpus: the Gemini cells were
recovered (18 → 20 analyzable); the 5 all-QA-failed cells are unchanged (the recovery campaign
did not recover qwen, grok-4-holidays, or the glm-5.1 cells).

### §3.5 Predecessor v0.1 DomainResults — audit state

`data/results/family/0.1.json` and `data/results/holidays/0.1.json` are preserved unchanged on
master. They are correct against the 2026-04-22 corpus and stand as audit. The 0.2 files are the
post-recovery analytical artifacts; they do not replace the 0.1 files.

### §3.6 Open-data bundle

`data/open_bundle/lsb.sqlite` was rebuilt from `data/raw/informants.jsonl` at RD-T5-1 (commit
`fda4ed7`), discharging the Phase 4a recovery SME binding note R5 deferral. The SQLite contains
121 rows, in lockstep with the JSONL.

---

## §4. Cost summary

| Campaign | Cost | Reference |
|---|---|---|
| Original Phase 4a (T4 collection + T5 analysis) | $4.95 | Original completion report §4 |
| Phase 4a recovery campaign (20 cells at corrected max_tokens) | $1.29 | Recovery report §4 |
| T5 redo analysis (RD-T5-2 pipeline run; no API calls) | $0.00 | No model API calls (analysis is local compute) |
| **Phase 4a total** | **$6.24** | — |

Phase 4a total spend is within the standing standing operating budget. Monthly cap
(`CDB_MAX_SPEND_USD`) remains at $300; Phase 4a closed at approximately 2.1% cap utilization.

---

## §5. B2 backup status

The B2 backup layer covers `data/raw/informants.jsonl` (with recovery rows), the 0.1 DomainResult
JSONs (backed up at original completion), and the 0.2 DomainResult JSONs (written at RD-T5-2).
The nightly backup timer at 02:00 UTC picks up any files written during the day. The 0.2 files
are on disk at the time of this commit and will be confirmed in the next nightly backup log.

The original completion report §5 B2 backup verification is the canonical record for the
2026-04-23 backup state. The recovery report §6 covers the recovery-row backup state.

---

## §6. `DATA_DICTIONARY.md` addendum

**None in this task.** No schema change to `cdb_core/schemas.py`. R7 satisfied (no schema
modification means no matching dictionary update required). The `thoughts_token_count` field was
added to the schema by Task #16 (with its own DATA_DICTIONARY.md update in that commit).

---

## §7. Outstanding carry-forward

### §7.1 Unexplained-failure residuum

The following cells remain unresolved after the recovery campaign:

| Model | Domain | Failure type | Recovery outcome | Next step |
|---|---|---|---|---|
| `openai/gpt-5.4-mini` | family × 2, holidays × 2 | Unknown (not cap-exhaustion) | Not recovered | Separate Architect task |
| `mistralai/mistral-small-2603` | family × 1 | Unknown (not cap-exhaustion) | Not recovered | Separate Architect task |

These are the "unexplained failures" from recovery report §7 items 3 and 4. Root cause is
not cap-exhaustion (cap fix did not recover them); separate investigation required.

### §7.2 phi-4 adapter task

The `microsoft/phi-4` model produced 6 failures (5 `HTTPStatusError` + 1 `ValueError`) during
the recovery campaign for the holidays domain. This is a separate adapter issue (the phi-4
adapter does not correctly handle the OpenRouter rate-limit or error response for this model).
Separate Architect task per recovery report §7 item 4.

### §7.3 Phase 4b G1 sensitivity study

`g1_overall_pass=None` on both domains — correct for Phase 4a. Phase 4b pre-conditions per the
original completion report §8 apply, updated for post-recovery corpus state:

1. Phase 4a.1 decline-interview data captured. Status: captured and classified (RD-3 reframing
   memo §4). The Note J cross-tab question is resolved under the RD-3 framing (the Note K
   hypothesis is REPLACED; Note J's motivating question about whether the CN-origin pattern is
   an artifact is answered affirmatively — it was an instrument artifact).
2. Unexplained-failure dispositions resolved (§7.1 above) — still pending.
3. G1 thresholds confirmed with CDA SME for Phase 4b domain(s).

Phase 4b is not blocked by T5 redo; it requires its own Architect plan with full SME review.

### §7.4 v2 prompt comparison study

Phase 5+ candidate. Trigger conditions and design requirements are in
`docs/status/2026-05-06-v2-freelist-prompt-suggestion.md`. v1 prompt stays canonical.

### §7.5 Phase 4c human grounding

No human grounding for Phase 4a (`groundings=[]` on both domains). Per `ARCHITECTURE.md`
§1.5.5, ungrounded is a complete first-class state. Phase 4c onboards published baselines first,
then opens researcher submissions per the grounding-submission workflow.

### §7.6 Methodology-page UI rendering

The T5 redo analysis report §8–§10 and this completion report are text-on-disk only. The
methodology-page UI rendering is a Phase 5/6 UI/UX-gated task. No UI/UX gate applies to this
document.

### §7.7 Lede generation

`generated_lede=""` on both DomainResults — correct. Lede generation is `cdb_publish` scope
per `ARCHITECTURE.md` §4.2 binding constraint and CLAUDE.md §6 R12.

---

## §8. Phase 4b readiness

Under the post-recovery corpus, the two Phase 4b pre-conditions that depend on Phase 4a data are
both further along than at original completion:

- **Corpus stability (T5 redo established):** the T5 redo provides a stable analytical baseline
  on the corrected corpus. The DomainResult v0.2 files are the reference artifacts for Phase 4b
  comparison.

- **Note J / Note K resolved (RD-3):** the Note J cross-tab question that gated Phase 4b in the
  original completion report §8 is effectively resolved: the CN-origin decline pattern is an
  instrument artifact (Note K REPLACED); the prompt-variant concern that Note J raised does not
  block Phase 4b.

The remaining Phase 4b pre-conditions (unexplained-failure disposition, G1 threshold
reaffirmation, separate Architect plan with SME review) are unchanged from §8 of the original
completion report. Phase 4b is not blocked by T5 redo; the T5 redo PASS is one required input
to its go/no-go decision.

---

## §9. What this report does not claim

This report does not claim:

- That the analytical observations in §8 of the analysis report reflect the models' categorical
  reasoning, internal states, or cultural cognition. The §1.5 framing applies throughout: these
  are observations about the shape of corpus-lens output under the LSB CDA protocol.

- That the observations generalize beyond the 11/9-model, two-domain, v1-prompt corpus
  conditions. Any cross-provider, cross-failure-mode, or cross-prompt-type generalization
  requires new evidence.

- That the original Phase 4a completion report (`docs/status/2026-04-23-phase4a-completion.md`)
  was incorrect. It was correct against its input population (101 informants). The redo is
  correct against the post-recovery population (121 informants). The delta reflects a
  methodologically traceable population shift, not a methodological correction.

- That the STRONG_CONSENSUS classification on either domain implies proximity to any
  human cultural baseline. Neither domain has a grounding baseline (Phase 4c). The
  classification reports a property of the model-to-model corpus structure under the CCM
  eigenratio threshold, with the small-n caveat active on both domains.

- That any finding here is suitable for external academic publication. The methodology-page bar
  is credibility to a skeptical reader, per CLAUDE.md §1.

- That the cap-exhaustion reframe or the confabulation observation from RD-3 generalizes to
  other providers, other failure modes, or other prompt types. The RD-3 memo §6 states this
  explicitly; it carries forward to this report.

---

## §10. Phase 4a verdict

**Phase 4a is COMPLETE** at the analytical layer, subject to CDA SME content verdict at gate
chain step 3 (analysis report §8–§10, verdict file
`docs/status/2026-05-06-phase4a-t5-redo-cda-sme-content-verdict.md`).

Under the post-recovery corpus:
- 121 InformantRecords in `data/raw/informants.jsonl` (20 recovery rows; full audit trail via
  `qa_notes` substring `campaign_id=phase4a-recovery-2026-05-05`).
- Both DomainResults v0.2 pass schema validation with `STRONG_CONSENSUS` and
  `romney_small_n_warning=True` on both domains.
- Open-data bundle SQLite in lockstep with JSONL (RD-T5-1).
- Note K REPLACED under RD-3 framing; confabulation-pattern observation is the substantive
  replacement.
- All original T5 binding notes (A, C, D, E, G) carry forward active; Note K REPLACED.
- Phase 4a spend: $6.24 total ($4.95 original + $1.29 recovery; 2.1% of monthly cap).

**Go / no-go for Phase 4b: GO** (pending SME content verdict at gate chain step 3; the T5 redo
PASS is the analytical input Phase 4b requires; remaining Phase 4b pre-conditions are
enumerated in §8 above).

---

*End of Phase 4a completion-redo report. Predecessor report preserved as audit at
`docs/status/2026-04-23-phase4a-completion.md`. T5 redo analysis report at
`docs/status/2026-05-07-phase4a-t5-redo-analysis-report.md`. CDA SME content verdict
(gate chain step 3) follows.*
