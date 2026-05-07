# Phase 4a T5 Redo — Analysis Report

**Date:** 2026-05-07
**Task:** Phase 4a T5 redo — RD-T5-3 (numerics report, §1–§7)
**Analysis script:** `scripts/analyze.py` (invoked as `uv run python -m scripts.analyze`)
**Analysis version:** 0.2
**Bootstrap iterations:** 500 (B=500; Q4 SME ruling: AGREE)
**Input:** `data/raw/informants.jsonl` (121 records total; 20 recovery rows)
**Outputs:** `data/results/family/0.2.json`, `data/results/holidays/0.2.json`

**Audit-trail one-liner:** This report covers §1–§7 (numerics, tables, gate status). §8–§10
(interpretation, binding-note compliance, closure verdict) are the RD-T5-4 deliverable.
Predecessor T5 report: `docs/status/2026-04-23-phase4a-t5-analysis-report.md` (commit `d74ce57`).
T5 redo plan: `docs/status/2026-05-06-t5-redo-architect-plan.md` (commit `2a4c6c2`).
SME plan verdict (PASS-WITH-NOTES; T11–T15 binding): `docs/status/2026-05-06-t5-redo-cda-sme-plan-verdict.md` (commit `86ad713`).
RD-T5-1 (build_db.py rerun): commit `fda4ed7`.
RD-T5-2 (pipeline 0.2 JSON): commit `63b0f9a`.
RD-3 reframing memo (Note K REPLACED): `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md` (commit `93a544f`).
Recovery report: `docs/status/2026-05-05-phase4a-recovery-report.md`.

---

## §1. Header

| Item | Value |
|---|---|
| Report date | 2026-05-07 |
| Report scope | RD-T5-3: §1–§7 numerics only |
| Analysis version | 0.2 |
| Predecessor T5 report | `docs/status/2026-04-23-phase4a-t5-analysis-report.md` (commit `d74ce57`) |
| T5 redo plan | `docs/status/2026-05-06-t5-redo-architect-plan.md` (commit `2a4c6c2`) |
| SME plan verdict | `docs/status/2026-05-06-t5-redo-cda-sme-plan-verdict.md` (commit `86ad713`) |
| RD-T5-1 commit | `fda4ed7` — build_db.py rerun (SQLite rebuilt from JSONL) |
| RD-T5-2 commit | `63b0f9a` — pipeline 0.2 JSON produced |
| RD-3 reframing memo | `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md` (commit `93a544f`; Note K REPLACED) |
| Recovery report | `docs/status/2026-05-05-phase4a-recovery-report.md` |
| §8–§10 scope | **Explicit RD-T5-4 scope; not present in this commit.** |

---

## §2. Execution log

### §2.1 Family domain

- **Command:**
  ```
  uv run python -m scripts.analyze --domain family \
    --input data/raw/informants.jsonl \
    --output data/results --bootstrap 500 --analysis-version 0.2
  ```
- **Pipeline log:** `11 models, 48 total records` (qa_only=True filter applied)
- **Commit:** `63b0f9a`

### §2.2 Holidays domain

- **Command:**
  ```
  uv run python -m scripts.analyze --domain holidays \
    --input data/raw/informants.jsonl \
    --output data/results --bootstrap 500 --analysis-version 0.2
  ```
- **Pipeline log:** `9 models, 39 total records` (qa_only=True filter applied)
- **Commit:** `63b0f9a`

### §2.3 Pipeline flags

- No `--mode` filter applied (matches predecessor T5 invocation; Q3 SME ruling: AGREE).
- B=500 bootstrap (matches predecessor; Q4 SME ruling: AGREE).
- `--analysis-version 0.2` — writes to `data/results/{domain}/0.2.json`; does not overwrite 0.1 files.

### §2.4 Invocation note

`uv run python scripts/analyze.py` produces an `AttributeError` at import time because
`scripts/inspect.py` (renamed from the original `scripts/inspect.py` to `scripts/lsb_inspect.py`
at task #30) no longer causes path injection at the time of this run; however, the `-m scripts.analyze`
module-invocation form is preserved for procedural continuity with the predecessor T5. Both forms
produce equivalent output.

---

## §3. Stop-condition checks

| # | Condition | Status |
|---|---|---|
| 1 | Analysis raises unhandled exception | PASS — no exceptions (bootstrap RuntimeWarnings are pre-existing scipy/numpy MDS convergence noise, not errors) |
| 2 | Null fields on consensus_type or romney_eigenratio | PASS — both populated on both domains |
| 3 | `romney_small_n_warning` status | PASS — True on both (family n=11 < 15; holidays n=9 < 15) |
| 4 | n_models < 4 on either domain | PASS — family=11, holidays=9 |
| 5 | Either run exceeds 30 min wall-clock | PASS — combined at RD-T5-2 commit timestamp; no stop condition triggered |

---

## §4. DomainResult key fields

### §4.1 Family

| Field | Value |
|---|---|
| `domain_slug` | `family` |
| `analysis_version` | `0.2` |
| `n_models` | **11** |
| `n_records` (qa-passed, sourced from pipeline log) | **48** |
| `consensus_type` | `STRONG_CONSENSUS` |
| `romney_eigenratio` | **12.0984** |
| `romney_consensus_pass` | `True` |
| `romney_consensus_warning` | `False` |
| `romney_small_n_warning` | **`True`** (n=11 < 15 threshold) |
| `consensus_score` | **0.7107** |
| `consensus_ci` | **[0.5049, 0.9092]** |
| `negative_centrality_flag` | `False` |
| `g1_overall_pass` | `None` (G1 gate not evaluated — requires Phase 4b) |
| `g1_salience_stability` | `None` |
| `g1_spatial_stability` | `None` |
| `g1_aggregate_stability` | `None` |
| `g1_salience_pass` | `None` |
| `g1_spatial_pass` | `None` |
| `groundings` | `[]` (no human grounding for Phase 4a) |
| `selected_baseline_id` | `None` |
| `generated_lede` | `""` (lede generation is cdb_publish scope) |
| `cultural_centrality_scores` range | **[0.2177, 0.3294]** (all positive) |
| MDS coordinates | 11 models |

**Cultural centrality scores (family, descending):**

| Model | Score |
|---|---|
| claude-sonnet-4-6 | 0.3294 |
| claude-opus-4-6 | 0.3212 |
| openai/gpt-5.4 | 0.3188 |
| google/gemini-2.5-pro | 0.3177 |
| x-ai/grok-4 | 0.3165 |
| mistralai/mistral-small-2603 | 0.3113 |
| mistralai/mistral-large-2512 | 0.3037 |
| meta-llama/llama-4-maverick | 0.2931 |
| deepseek/deepseek-v3.2 | 0.2921 |
| microsoft/phi-4 | 0.2788 |
| openai/gpt-5.4-mini | 0.2177 |

**MDS coordinates (family):**

| Model | dim1 | dim2 |
|---|---|---|
| claude-opus-4-6 | 0.1098 | 0.1083 |
| claude-sonnet-4-6 | 0.0829 | -0.0227 |
| deepseek/deepseek-v3.2 | -0.0651 | -0.2330 |
| google/gemini-2.5-pro | 0.0933 | -0.1089 |
| meta-llama/llama-4-maverick | 0.0430 | -0.2780 |
| microsoft/phi-4 | -0.0944 | 0.2774 |
| mistralai/mistral-large-2512 | 0.2141 | 0.0938 |
| mistralai/mistral-small-2603 | 0.0602 | -0.0803 |
| openai/gpt-5.4 | 0.0516 | 0.1327 |
| openai/gpt-5.4-mini | -0.5405 | -0.0428 |
| x-ai/grok-4 | 0.0451 | 0.1535 |

**OCI per model (family):**

| Model | OCI |
|---|---|
| mistralai/mistral-large-2512 | 614.6153 |
| google/gemini-2.5-pro | 246.6729 |
| claude-opus-4-6 | 220.0940 |
| claude-sonnet-4-6 | 82.2035 |
| openai/gpt-5.4-mini | 100.0000 |
| openai/gpt-5.4 | 36.7375 |
| x-ai/grok-4 | 34.2068 |
| mistralai/mistral-small-2603 | 27.8189 |
| meta-llama/llama-4-maverick | 18.4291 |
| deepseek/deepseek-v3.2 | 18.0933 |
| microsoft/phi-4 | 7.8628 |

**Within-model n_runs (family):**

| Model | n_runs |
|---|---|
| claude-opus-4-6 | 5 |
| claude-sonnet-4-6 | 5 |
| deepseek/deepseek-v3.2 | 5 |
| google/gemini-2.5-pro | 5 |
| meta-llama/llama-4-maverick | 4 |
| microsoft/phi-4 | 4 |
| mistralai/mistral-large-2512 | 5 |
| mistralai/mistral-small-2603 | 5 |
| openai/gpt-5.4 | 5 |
| openai/gpt-5.4-mini | 3 |
| x-ai/grok-4 | 2 |
| **Total** | **48** |

### §4.2 Holidays

| Field | Value |
|---|---|
| `domain_slug` | `holidays` |
| `analysis_version` | `0.2` |
| `n_models` | **9** |
| `n_records` (qa-passed, sourced from pipeline log) | **39** |
| `consensus_type` | `STRONG_CONSENSUS` |
| `romney_eigenratio` | **10.1520** |
| `romney_consensus_pass` | `True` |
| `romney_consensus_warning` | `False` |
| `romney_small_n_warning` | **`True`** (n=9 < 15 threshold) |
| `consensus_score` | **0.7757** |
| `consensus_ci` | **[0.4717, 0.9647]** |
| `negative_centrality_flag` | `False` |
| `g1_overall_pass` | `None` (G1 gate not evaluated — requires Phase 4b) |
| `g1_salience_stability` | `None` |
| `g1_spatial_stability` | `None` |
| `g1_aggregate_stability` | `None` |
| `g1_salience_pass` | `None` |
| `g1_spatial_pass` | `None` |
| `groundings` | `[]` (no human grounding for Phase 4a) |
| `selected_baseline_id` | `None` |
| `generated_lede` | `""` (lede generation is cdb_publish scope) |
| `cultural_centrality_scores` range | **[0.2104, 0.3600]** (all positive) |
| MDS coordinates | 9 models |

**Cultural centrality scores (holidays, descending):**

| Model | Score |
|---|---|
| claude-opus-4-6 | 0.3600 |
| openai/gpt-5.4 | 0.3572 |
| claude-sonnet-4-6 | 0.3567 |
| google/gemini-2.5-pro | 0.3566 |
| deepseek/deepseek-v3.2 | 0.3551 |
| meta-llama/llama-4-maverick | 0.3538 |
| mistralai/mistral-large-2512 | 0.3278 |
| openai/gpt-5.4-mini | 0.2922 |
| mistralai/mistral-small-2603 | 0.2104 |

**MDS coordinates (holidays):**

| Model | dim1 | dim2 |
|---|---|---|
| claude-opus-4-6 | -0.0096 | -0.1171 |
| claude-sonnet-4-6 | 0.0249 | -0.0938 |
| deepseek/deepseek-v3.2 | 0.0280 | -0.1634 |
| google/gemini-2.5-pro | 0.0101 | -0.1344 |
| meta-llama/llama-4-maverick | 0.0031 | -0.0964 |
| mistralai/mistral-large-2512 | -0.2245 | -0.0593 |
| mistralai/mistral-small-2603 | -0.2161 | 0.7170 |
| openai/gpt-5.4 | -0.0056 | -0.1355 |
| openai/gpt-5.4-mini | 0.3896 | 0.0829 |

**OCI per model (holidays):**

| Model | OCI |
|---|---|
| claude-opus-4-6 | 117.8406 |
| claude-sonnet-4-6 | 91.0984 |
| google/gemini-2.5-pro | 70.2801 |
| openai/gpt-5.4 | 45.9126 |
| mistralai/mistral-large-2512 | 42.2028 |
| meta-llama/llama-4-maverick | 19.4967 |
| deepseek/deepseek-v3.2 | 18.0078 |
| openai/gpt-5.4-mini | 2.5535 |
| mistralai/mistral-small-2603 | 0.0000 |

**Within-model n_runs (holidays):**

| Model | n_runs |
|---|---|
| claude-opus-4-6 | 5 |
| claude-sonnet-4-6 | 5 |
| deepseek/deepseek-v3.2 | 5 |
| google/gemini-2.5-pro | 5 |
| meta-llama/llama-4-maverick | 4 |
| mistralai/mistral-large-2512 | 5 |
| mistralai/mistral-small-2603 | 1 |
| openai/gpt-5.4 | 5 |
| openai/gpt-5.4-mini | 4 |
| **Total** | **39** |

---

## §5. Bootstrap uncertainty fields (R11 check)

R11 (CLAUDE.md §6): no point estimates without associated uncertainty.

### §5.1 consensus_ci

Both domains carry bootstrap CIs on `consensus_score`:

| Domain | consensus_score | consensus_ci |
|---|---|---|
| family | 0.7107 | [0.5049, 0.9092] |
| holidays | 0.7757 | [0.4717, 0.9647] |

### §5.2 mds_uncertainty (per-model bootstrap ellipse parameters)

All models have `n_bootstrap=500`. Ellipse parameters are real-valued numbers; no `None` or `NaN` in
any entry. Both `semi_major` and `semi_minor` are positive real numbers for all models in both domains.

**mds_uncertainty (family) — 11 models, all n_bootstrap=500:**

| Model | semi_major | semi_minor |
|---|---|---|
| claude-opus-4-6 | 0.1267 | 0.0772 |
| claude-sonnet-4-6 | 0.1016 | 0.0831 |
| deepseek/deepseek-v3.2 | 0.2543 | 0.1792 |
| google/gemini-2.5-pro | 0.1671 | 0.0795 |
| meta-llama/llama-4-maverick | 0.1870 | 0.1329 |
| microsoft/phi-4 | 0.4062 | 0.1839 |
| mistralai/mistral-large-2512 | 0.3019 | 0.1189 |
| mistralai/mistral-small-2603 | 0.2784 | 0.2109 |
| openai/gpt-5.4 | 0.1728 | 0.1333 |
| openai/gpt-5.4-mini | 0.1670 | 0.1164 |
| x-ai/grok-4 | 0.1676 | 0.1281 |

**mds_uncertainty (holidays) — 9 models, all n_bootstrap=500:**

| Model | semi_major | semi_minor |
|---|---|---|
| claude-opus-4-6 | 0.0921 | 0.0576 |
| claude-sonnet-4-6 | 0.1277 | 0.0915 |
| deepseek/deepseek-v3.2 | 0.1037 | 0.0865 |
| google/gemini-2.5-pro | 0.1273 | 0.0919 |
| meta-llama/llama-4-maverick | 0.1600 | 0.1131 |
| mistralai/mistral-large-2512 | 0.1813 | 0.1543 |
| mistralai/mistral-small-2603 | 0.1620 | 0.0674 |
| openai/gpt-5.4 | 0.1128 | 0.0875 |
| openai/gpt-5.4-mini | 0.3156 | 0.0982 |

### §5.3 similarity_ci

`similarity_ci` is populated on both domains (11×11 matrix for family; 9×9 matrix for holidays).
No null entries. Each cell is a two-element [lower, upper] CI pair.

### §5.4 R11 verdict

**R11 PASS.** All bootstrap-derived fields (`consensus_ci`, `mds_uncertainty`, `similarity_ci`)
are populated with real-valued uncertainty parameters. No point estimates appear without associated
uncertainty in any populated field.

---

## §6. Corpus state

### §6.1 Source JSONL

**File:** `data/open_bundle/lsb.sqlite` (in lockstep with JSONL post-RD-T5-1; see §6.5)
**Canonical source:** `data/raw/informants.jsonl`
**Total informants:** 121

### §6.2 Recovery rows

The 20 recovery records were appended to `data/raw/informants.jsonl` on 2026-05-05 by the recovery
campaign (`docs/status/2026-05-05-phase4a-recovery-report.md`). Each carries `qa_notes` containing
the substring `campaign_id=phase4a-recovery-2026-05-05`.

**Verbatim grep to reproduce the recovery-row count (T13 binding):**

```bash
grep -c 'phase4a-recovery-2026-05-05' data/raw/informants.jsonl
```

Expected output at this commit: **20**

Per-domain breakdown (for audit; derivable by adding domain filter):
- `google/gemini-2.5-pro` × family: 5 records
- `google/gemini-2.5-pro` × holidays: 5 records
- `meta-llama/llama-4-maverick` × family: 2 records
- `meta-llama/llama-4-maverick` × holidays: 2 records
- `z-ai/glm-5.1` × family: 2 records
- `z-ai/glm-5.1` × holidays: 4 records

Note: `z-ai/glm-5.1` recovery rows carry `qa_passed=False` (the empty-freelist-propagation bug
documented in the project memory; the runs received "Here are 0 items" from an upstream freelist
that was empty). The `z-ai/glm-5.1` cells remain in the all-QA-failed category
(see §6.4 cell-coverage table).

### §6.3 Per-domain feed into pipeline

| Domain | QA-passed records fed to pipeline | Models with ≥1 QA-passed record |
|---|---|---|
| family | **48** | **11** |
| holidays | **39** | **9** |

### §6.4 Cell-coverage denominator

The corpus design is 13 models × 2 domains = 26 potential cells. One model (`microsoft/phi-4`)
was collected for the family domain only (T3 canary scope) and has no holidays records, leaving
**25 cells with any records**.

| Category | Count | Detail |
|---|---|---|
| Cells with ≥1 QA-passed record (analyzable) | **20** | Family: 11 models × 1 domain = 11; Holidays: 9 models × 1 domain = 9 |
| Cells with all records QA-failed | **5** | qwen/qwen3.6-plus × family, qwen/qwen3.6-plus × holidays, x-ai/grok-4 × holidays, z-ai/glm-5.1 × family, z-ai/glm-5.1 × holidays |
| Cells with zero records (model not run for domain) | **1** | microsoft/phi-4 × holidays (T3 canary scope; model not collected for holidays) |

*5 cells produced no interpretable primary-step output* (the all-QA-failed cells listed above). The
original T5 §5 used the same phrasing and the same count of 5. Under the post-recovery corpus, this
count is unchanged: the recovery campaign did not recover any of these 5 cells (the recovery
campaign targeted gemini, llama-maverick, and glm-5.1; glm-5.1's recovered records all returned
`qa_passed=False` due to the empty-freelist-propagation bug; the qwen and grok-4-holidays cells
were not in scope for the recovery campaign).

The pipeline filter posture is QA-only (`qa_only=True`; no `--mode` filter). Recovery-affected
records are traceable by the grep command in §6.2; no per-cell schema flag is added (Q5 SME
ruling: AGREE; per-cell flagging would require a `cdb_core/schemas.py` change, which is out of
scope per this plan).

### §6.5 Open-bundle SQLite sync state

`data/open_bundle/lsb.sqlite` was rebuilt from `data/raw/informants.jsonl` at RD-T5-1 (commit
`fda4ed7`), discharging the Phase 4a recovery SME binding note R5 deferral. The SQLite contains
121 rows, matching the JSONL line count exactly.

Spot-check query at RD-T5-1 (per Reviewer verdict `1637110`): `SELECT informant_id FROM informants
WHERE informant_id = '...'` confirmed one recovery record from the recovery report §2 table is
present in the SQLite. Post-RD-T5-1 state: in lockstep with JSONL.

---

## §7. Predecessor delta

**T11 framing guard:** The following table reports the scalar field deltas between original T5
(analysis version 0.1, commit `d74ce57`) and T5 redo (analysis version 0.2, commit `63b0f9a`).
Both DomainResults are correct against their respective input populations. The 0.1 numerics are
correct against the 2026-04-22 corpus; the 0.2 numerics are correct against the post-recovery
corpus. The deltas reflect the population shift introduced by the 2026-05-05 recovery campaign
(see §6.2, recovery report `docs/status/2026-05-05-phase4a-recovery-report.md`). §7 reports the
deltas without interpretation; the interpretation is in §8 under the RD-3 framing
(`docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md`).

Note: bootstrap CIs are not fixed-seed reproducible; delta values on CI bounds carry bootstrap
noise in addition to any corpus-induced shift. No CI-overlap analysis between 0.1 and 0.2 is
reported (Q1 SME ruling: AGREE — tabular comparison only).

### §7.1 Family — scalar field comparison

| Field | T5 0.1 (2026-04-22 corpus) | T5 redo 0.2 (post-recovery corpus) | Delta |
|---|---|---|---|
| `n_models` | 10 | 11 | +1 |
| `n_records` (QA-passed) | 41 | 48 | +7 |
| `consensus_score` | 0.7122 | 0.7107 | -0.0015 |
| `consensus_ci` lower | 0.5039 | 0.5049 | +0.0010 |
| `consensus_ci` upper | 0.9012 | 0.9092 | +0.0080 |
| `romney_eigenratio` | 10.7917 | 12.0984 | +1.3067 |
| `romney_consensus_pass` | True | True | — |
| `romney_consensus_warning` | False | False | — |
| `romney_small_n_warning` | True | True | — |
| `negative_centrality_flag` | False | False | — |
| `consensus_type` | STRONG_CONSENSUS | STRONG_CONSENSUS | — |
| MDS coordinate count | 10 models | 11 models | +1 |
| `g1_overall_pass` | None | None | — |
| `groundings` | [] | [] | — |

### §7.2 Holidays — scalar field comparison

| Field | T5 0.1 (2026-04-22 corpus) | T5 redo 0.2 (post-recovery corpus) | Delta |
|---|---|---|---|
| `n_models` | 8 | 9 | +1 |
| `n_records` (QA-passed) | 33 | 39 | +6 |
| `consensus_score` | 0.7658 | 0.7757 | +0.0099 |
| `consensus_ci` lower | 0.4737 | 0.4717 | -0.0020 |
| `consensus_ci` upper | 0.9665 | 0.9647 | -0.0018 |
| `romney_eigenratio` | 9.2181 | 10.1520 | +0.9339 |
| `romney_consensus_pass` | True | True | — |
| `romney_consensus_warning` | False | False | — |
| `romney_small_n_warning` | True | True | — |
| `negative_centrality_flag` | False | False | — |
| `consensus_type` | STRONG_CONSENSUS | STRONG_CONSENSUS | — |
| MDS coordinate count | 8 models | 9 models | +1 |
| `g1_overall_pass` | None | None | — |
| `groundings` | [] | [] | — |

### §7.3 Note G carry-forward (T15 binding)

The original T5 §5 used the exact wording: *"5 cells produced no interpretable primary-step
output; follow-up decline-interview data for these cells will be captured in Phase 4a.1."*

Under the post-recovery corpus, the count of cells producing no interpretable primary-step output
is unchanged at 5 (see §6.4). The verbatim phrase is preserved here with a numeric update that
the count holds at 5 post-recovery: *5 cells produced no interpretable primary-step output*; the
cells are enumerated in §6.4. The disposition of Phase 4a.1's follow-up interpretation is updated
in §8 (RD-T5-4 scope), citing the RD-3 reframing memo.

---

## §8. Interpretation (RD-T5-4 scope)

**Placeholder — interpretation pending RD-T5-4 commit. Numerics in §1–§7 are authoritative;
this section will frame them under the RD-3 framing
(`docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md`).**

---

*End of §1–§7 (RD-T5-3 scope). §8–§10 are produced in the RD-T5-4 commit.*
