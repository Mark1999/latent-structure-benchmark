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

## §8. Interpretation

*Methodology-page-bound prose. Pitched at a skeptical non-specialist audience. Third-person voice.
Bound by §1.5 framing throughout. Numerics referenced here are in §4–§7; no new numerics appear
in §8. B6 public-copy guardrails apply (RD-3 framing; no CN-origin augmentation to Note E; no
"incorrect" framing of the predecessor T5; no cross-provider/cross-failure-mode generalization;
no internal-state claims; no "publishable" framing per T14).*

### §8.1 What the family domain numerics support

The post-recovery family domain corpus — 11 models, 48 QA-passed records — produces a Romney
CCM eigenratio of 12.10 (compared to 10.79 on the 10-model pre-recovery corpus; §7.1). The
eigenratio exceeds the LSB operational threshold of 5.0, and the pipeline classifies the result
as `STRONG_CONSENSUS`. The small-n caveat applies: n=11 is below the n<15 threshold, and the
`romney_small_n_warning=True` flag fires accordingly. Any claim about the family domain's
categorical structure must carry this caveat.

Within those constraints, the numerics support these descriptive observations:

- **Cross-model salience is high and consistent.** Smith's S consensus score is 0.7107 (bootstrap
  CI [0.5049, 0.9092]; §4.1 and §5.1). The wide CI is consistent with n=11 under B=500 bootstrap
  (Level 2, Register 2; see `docs/BOOTSTRAP_DESIGN.md`). The point estimate and lower CI bound
  both sit well above 0.5, indicating that across the 11 models, free-list outputs share a high
  proportion of culturally salient items.

- **Cultural centrality range is positive and moderately spread.** Centrality scores range from
  0.2177 to 0.3294 (§4.1). All models produce positive centrality — no subcultural or contested
  structure is detected (`negative_centrality_flag=False`). The spread ([0.22–0.33]) shows
  non-trivial inter-model differentiation at the high-salience end of the category.

- **MDS inter-model similarity structure is present with bootstrap uncertainty.** The 11-model
  MDS map (§4.1 coordinates; §5.2 bootstrap ellipses) shows that most models cluster near the
  origin with one clear outlier (`openai/gpt-5.4-mini`, dim1 = −0.54). Bootstrap semi-major axes
  range from 0.10 to 0.41, indicating that ellipses for higher-OCI models are wider. No grounding
  against a human baseline is available for Phase 4a; the MDS coordinates are model-to-model
  distances only (`groundings=[]`; §4.1).

- **Within-model internal consistency (OCI) varies widely.** OCI ranges from 7.86
  (`microsoft/phi-4`) to 614.62 (`mistralai/mistral-large-2512`; §4.1). High OCI indicates that
  run-to-run within-model output is highly consistent; low OCI indicates more variable output
  across runs. These are within-model descriptive properties under the v1 prompt conditions; they
  do not constitute claims about model capability or model-internal reasoning.

The `g1_overall_pass` field is `None` on the family domain result — correct for Phase 4a, where
the G1 sensitivity study requires Phase 4b as described in `ARCHITECTURE.md` §5.3. The family
domain is ungrounded at this phase (`groundings=[]`); per `ARCHITECTURE.md` §1.5.5, ungrounded
is a complete first-class state.

### §8.2 What the holidays domain numerics support

The post-recovery holidays domain corpus — 9 models, 39 QA-passed records — produces a Romney
CCM eigenratio of 10.15 (compared to 9.22 on the 8-model pre-recovery corpus; §7.2). The
eigenratio exceeds the LSB operational threshold of 5.0, and the pipeline classifies the result
as `STRONG_CONSENSUS`. The small-n caveat applies: n=9 is below the n<15 threshold
(`romney_small_n_warning=True`).

Within those constraints, the numerics support these descriptive observations:

- **Cross-model salience is high.** Smith's S consensus score is 0.7757 (bootstrap CI
  [0.4717, 0.9647]; §4.2 and §5.1). The CI is wide — the lower bound at 0.47 is below 0.5 —
  consistent with n=9 at B=500. The point estimate is robust; the wide CI reflects the
  small-n population under Level 2 bootstrap conditions.

- **Cultural centrality range is positive, with wider spread than family.** Centrality scores
  range from 0.2104 to 0.3600 (§4.2). All models produce positive centrality
  (`negative_centrality_flag=False`). The spread ([0.21–0.36]) is modestly wider than the family
  domain's range, indicating somewhat more inter-model differentiation on the holidays domain
  under these corpus conditions.

- **MDS structure is compact for most models with two clear peripheral positions.** The 9-model
  MDS map (§4.2 coordinates; §5.2 ellipses) shows `mistralai/mistral-small-2603` and
  `openai/gpt-5.4-mini` as peripheral points (dim2 = 0.72 and dim1 = 0.39 respectively). Bootstrap
  semi-major axes range from 0.09 to 0.32. These are model-to-model distances on the post-recovery
  corpus under v1 prompt conditions; the coordinates carry no human-baseline grounding
  (`groundings=[]`; §4.2).

- **OCI for holidays is also variable.** OCI ranges from 0.00 (`mistralai/mistral-small-2603`,
  n_runs=1 — only one QA-passed run, so OCI is trivially 0) to 117.84 (`claude-opus-4-6`; §4.2).
  `mistral-small-2603` has n_runs=1 for holidays; the single-run OCI=0.00 is not a meaningful
  within-model consistency estimate. This is a cell-coverage descriptor, not a claim about the
  model.

The `g1_overall_pass` field is `None` on the holidays domain result — correct for Phase 4a.
The holidays domain is ungrounded at this phase (`groundings=[]`).

### §8.3 What the cross-domain comparison supports

Both domains under the post-recovery corpus produce `STRONG_CONSENSUS` with Romney eigenratios
well above the LSB operational threshold, and both carry `romney_small_n_warning=True`. The
two-domain structure of Phase 4a enables a limited cross-domain comparison:

- **Holidays consensus score is higher (0.78 vs 0.71 family).** The holidays domain produces a
  higher point-estimate consensus score than the family domain, with overlapping bootstrap CIs
  ([0.47, 0.96] vs [0.50, 0.91]). The CI overlap means this difference is not distinguishable
  from bootstrap noise under n=9 and n=11 respectively. The observation is a descriptive
  property of the post-recovery corpus; it does not constitute a comparative claim about how
  models organize holiday vocabulary versus family vocabulary.

- **Romney eigenratio is higher for family (12.10 vs 10.15 holidays).** Both are well above 5.0.
  The ordering is reversed from the consensus-score ordering — family has the higher eigenratio
  but the lower consensus-score point estimate. This is a known property of the two-measure
  structure (eigenratio and Smith's S are correlated but not interchangeable per
  `docs/SME_REVIEW.md` §1.1) and is not analytically significant at this population size.

- **Centrality ranges are similar in shape.** Both domains show all-positive centrality, no
  subcultural detection, and a spread of approximately 10–15 percentage points from the minimum
  to maximum model centrality value.

- **n_models differs across domains (11 vs 9).** The holidays domain has fewer models with
  QA-passed records, reflecting the cell-coverage denominator in §6. Cross-domain comparisons
  at this corpus size carry the small-n caveat on both sides.

No human-baseline grounding is available for either domain; neither domain's MDS map can be
compared to a published ethnographic baseline at this phase. The Phase 4c grounding study is the
anticipated mechanism for that comparison (`ARCHITECTURE.md` §4.2.5; Note D carries forward).

### §8.4 Caveats — `thoughts_token_count=0` epistemic states

The analytical pipeline at `packages/cdb_analyze/cdb_analyze/pipeline.py` does not reference
`thoughts_token_count` as an analytical input (verified by code search at plan-write time: zero
occurrences in `pipeline.py` and zero occurrences across the `packages/cdb_analyze/` package
excluding `confabulation_classification.py`). The field is metadata captured for QA and
decline-interview triage. Therefore the co-existence of legacy and recovered records with
differing `thoughts_token_count` semantics does not bias any computed consensus, OCI, MDS,
similarity, centrality, or Sutrop CSI value in the 0.2 DomainResults.

For a reader who encounters `thoughts_token_count=0` in the Phase 4a corpus, the Task #16
CDA SME verdict S2 (`docs/status/2026-05-04-task-16-cda-sme-verdict.md`, Q2/S2) establishes
four distinct epistemic states for the value `0`:

1. The model produced no reasoning tokens (a non-reasoning model, or a reasoning model that
   bypassed reasoning for this call).
2. The provider does not surface reasoning-token usage in its API response (Anthropic,
   HuggingFace, and non-reasoning OpenRouter models at this commit).
3. A non-reasoning model on a reasoning-capable provider.
4. A legacy record from a pre-field era — Phase 4a pre-Task-#16 successful records, in which
   the `thoughts_token_count` field did not exist at collection time and is materialised as `0`
   on read by pydantic's default.

States (1)–(4) are operationally distinct disambiguation cases that share the same field value of `0`; they differ in what the value means under different provider configurations, not in the field's observable signature.

State (4) applies to all original Phase 4a successful records (collected before Task #16 added
the field). States (1), (2), or (3) apply to the recovered records, depending on the provider.
Downstream analysis treating `thoughts_token_count=0` as evidence of non-reasoning must verify
that the provider exposes the field for the model in question (see
`docs/status/2026-05-04-task-16-cda-sme-verdict.md` S2 per-provider notes).

Because the pipeline does not consume `thoughts_token_count`, state-(4) legacy records co-exist
in the analytical input without bias. This eliminates the need for any filter on this field
before running the Register 2 analysis stack.

### §8.5 Scope discipline

The following scope constraints apply to all claims in this interpretation section:

- **Single-provider observation for the recovered cells.** The 20 recovery records come from
  three models on OpenRouter (gemini-2.5-pro, llama-4-maverick, glm-5.1) under v1 prompt
  conditions. The analytical results are observations about this specific recovered corpus.
  Cross-provider, cross-failure-mode, or cross-prompt-type generalization requires new
  evidence that this corpus does not supply. This carries forward the parent T4-redo SME T6
  scope discipline.

- **Small-n caveat on both domains.** Neither domain crosses the n<15 threshold; both carry
  `romney_small_n_warning=True`. Any claim about the domains' categorical structure must
  acknowledge the population-size constraint. The STRONG_CONSENSUS classification is defensible
  given both eigenratios exceed 5.0, but the classification does not imply cross-domain or
  cross-population stability.

- **No ceiling or proximity-to-baseline claims (Note D).** Neither domain has a human-baseline
  grounding. Statements like "models are close to human patterns" or "models reach a ceiling"
  are not supportable at this phase. Phase 4c is the anticipated grounding path.

- **Population shift, not methodological correction.** The delta between the 0.1 and 0.2
  DomainResults (§7) reflects the 2026-05-05 recovery campaign's population shift. The original
  T5 was correct against its input population; the redo is correct against the post-recovery
  population. Both are in the audit record. The framing for the cap-exhaustion event that
  necessitated the recovery campaign is in the RD-3 reframing memo
  (`docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md`); §8 does not re-state it.

- **v1 prompt conditions throughout.** All 121 informants in the corpus were collected under
  the v1 free-list prompt (`packages/cdb_collect/cdb_collect/prompts/v1/free_list.md`). A
  v2 prompt comparison study is a Phase 5+ candidate per
  `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md`; it is out of scope for Phase 4a.

- **Methodology-page framing only.** The observations in §8.1–§8.3 are reported on the
  methodology page as characterizations of corpus-lens structure under the LSB CDA protocol.
  They are not presented as findings in any academic publication venue; per CLAUDE.md §1, the
  bar is credibility to a skeptical reader, not suitability for external publication.

---

## §9. Carry-forward of original-T5 binding notes

Per the T10 five-category vocabulary from the parent T4-redo SME verdict
(`docs/status/2026-05-05-t4-redo-cda-sme-verdict.md`), and the carry-forward table from the
T5 redo SME plan verdict (`docs/status/2026-05-06-t5-redo-cda-sme-plan-verdict.md` §C):

| Note | Original T5 content | Status under T5 redo | Application in this report |
|---|---|---|---|
| **Note A** | `romney_small_n_warning=True`; CCM small-n caveat binds. | CARRIES FORWARD (active) | Both domains fire `romney_small_n_warning=True` (n=11 family; n=9 holidays). §8.1, §8.2, §8.5 carry the caveat on every descriptive consensus claim. |
| **Note C** | Cell-coverage denominator: "18 analyzable + 5 decline-interviewable" framing. Qualified denominator binds the consensus claim. | CARRIES FORWARD (active) — numeric update under post-recovery corpus | §6.4 reports the post-recovery denominator: 20 analyzable cells (11 family + 9 holidays), 5 all-QA-failed cells, 1 zero-record cell. The 5 all-QA-failed cells are enumerated. The qualified denominator binds §8 observations. |
| **Note D** | No ceiling or proximity-to-human-baseline claims before Phase 4c grounding. | CARRIES FORWARD (active) | §8.3 and §8.5 make no ceiling or baseline-proximity claims. Phase 4c is named as the anticipated grounding path. |
| **Note E** | US-weighted composition caveat on the model corpus. | CARRIES FORWARD (active) — Note K augmentation removed per Q6(a) and RD-3 | The corpus is predominantly US-provider-weighted (Claude, GPT, Grok, Mistral, Phi-4 being US-origin; DeepSeek and Llama as open-weights; Gemini as US-origin). The original T5 SME augmented Note E with "PLUS disproportionate CN-origin decline pattern." That augmentation is REMOVED per the RD-3 reframing memo (`docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md`, §3): the CN-origin decline pattern was an instrument artifact (cap-exhaustion), not a signal. Standalone Note E (US-weighted composition) applies to Phase 6+ methodology page copy. |
| **Note G** | Exact wording for uninterviewed cells: "N cells produced no interpretable primary-step output; follow-up decline-interview data for these cells will be captured in Phase 4a.1." | CARRIES FORWARD (active) — T15 binding: verbatim phrase preserved; count updates; RD-3 trailing clause added | 5 cells produced no interpretable primary-step output; follow-up decline-interview data for these cells was captured in Phase 4a.1, and the interpretation of those follow-ups is in the RD-3 reframing memo (`docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md`). See §6.4 for cell enumeration and §7.3 for the Note G carry-forward confirmation. |
| **Note K** | CN-origin decline clustering (4 of 5 decline-interviewable cells CN-origin). Framed as a coverage/protocol robustness caveat pending Phase 4a.1 Note J cross-tab. | REPLACED (audit preserved) | Note K is REPLACED per the RD-3 reframing memo (§3). The originating Phase 4a Gemini failures were cap-exhaustion instrument events, not safety-policy events. The substantive replacement is the confabulation-pattern observation in RD-3 §4. The original Note K hypothesis is no longer testable from this corpus. Note K's audit record is in the prior verdict files; the canonical replacement framing is at `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md`. No new Note designation is introduced here. |

**T-series carry-forward (parent T4-redo SME binding notes; T1–T10 SATISFIED at RD-3 content
verdict; gate postures preserved):**

| Note | Status | Gate posture preserved |
|---|---|---|
| B6 (public-copy guardrails) | CARRIES FORWARD (active) — five avoidances (a)–(e) per Q6 ruling | §8 prose applies all five avoidances. |
| B12 (future-batch binding precedent) | CARRIES FORWARD (active) | Not directly exercised by T5 redo; gate posture preserved for future batches. |
| B14 (numerics-vs-interpretation separation) | CARRIES FORWARD (active) — §1–§7 numerics in RD-T5-3; §8–§10 interpretation in this commit | The four-task split honors B14. RD-T5-3's Reviewer confirmed §1–§7 as numerics-only. §8 is interpretation-only. |
| T1–T10 (T4 redo RD-3; all SATISFIED) | SATISFIED (specific deliverables at RD-3 content verdict; gate postures preserved) | Any future methodology-page-bound text on Note K routes through CDA SME per the S5 gate posture. |

**Task #16 S-series carry-forward:**

| Note | Status |
|---|---|
| S2 (four epistemic states for `thoughts_token_count=0`) | CARRIES FORWARD (active) — §8.4 enumerates all four states explicitly, per T12 binding. |
| S5 (Note K re-classification routes through SME before methodology-page text) | SATISFIED (specific deliverable; gate posture preserved) — Satisfied at RD-3 content verdict. Gate posture preserved: future methodology-page-bound text on Note K disposition routes through CDA SME. |

---

## §10. Closure verdict

Phase 4a is closed at the analytical layer under the corrected instrument framing, pending the
CDA SME content verdict on this report (gate chain step 3 per the T5 redo plan §2).

The T5 redo pipeline ran against the 121-record post-recovery corpus
(`data/raw/informants.jsonl`), producing `data/results/family/0.2.json` (n=11 models, 48
QA-passed records, eigenratio=12.10, `STRONG_CONSENSUS`) and `data/results/holidays/0.2.json`
(n=9 models, 39 QA-passed records, eigenratio=10.15, `STRONG_CONSENSUS`). All stop-condition
checks passed (§3). R11 uncertainty is satisfied on all bootstrap-derived fields (§5). The
open-data bundle SQLite is in lockstep with the JSONL post-RD-T5-1 (§6.5).

The following items are out of scope for this Phase 4a closure and are enumerated here as the
canonical forward-carry index:

- **v2 free-list prompt comparison study** — Phase 5+ candidate. Trigger conditions and design
  requirements are in `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md`. v1 prompt stays
  canonical; v2 requires its own Architect plan with SME review.

- **phi-4 ×6 adapter task** — separate Architect task per the recovery report §7 item 4. The
  phi-4 failures (5 HTTPStatusError + 1 ValueError) are a separate adapter issue unaddressed by
  the cap fix.

- **gpt-5.4-mini ×2 + mistral-small ×1 unexplained-failure investigation** — separate Architect
  task per the recovery report §7 item 3. Root cause unknown; not cap-exhaustion.

- **Phase 4b G1 sensitivity study** — separate Architect plan. Pre-conditions include corpus
  stability (now established by the T5 redo), unexplained-failure disposition, and CDA SME
  concurrence on the G1 threshold reaffirmation per `ARCHITECTURE.md` §5.3.

- **Phase 4c human grounding** — separate Architect plan. Phase 4a is ungrounded; both
  DomainResults carry `groundings=[]`. Per `ARCHITECTURE.md` §1.5.5, ungrounded is a complete
  first-class state.

- **Methodology-page UI rendering** — Phase 5/6 UI/UX-gated, separate task with its own
  UI/UX gate cycle per the T5 redo plan §1 disposition table.

- **Phase 4b / next-domain expansion** — separate Architect plan. T5 redo PASS is one input
  to Phase 4b's go/no-go decision.

**Gate chain step 3 (SME content verdict):** the §8–§10 prose in this commit is the artifact
the CDA SME reviews at gate chain step 3. Verdict file:
`docs/status/2026-05-06-phase4a-t5-redo-cda-sme-content-verdict.md`. A PASS or PASS-WITH-NOTES
verdict at gate chain step 3 closes Phase 4a at the analytical layer. No UI/UX gate applies at
this layer (analytical, not frontend; per parent T4-redo SME Q4 precedent and T5 redo plan §2).

---

*End of report. §1–§7 produced in RD-T5-3 (commit `5128e94`). §8–§10 produced in this commit
(RD-T5-4). Original Phase 4a completion report preserved as audit at
`docs/status/2026-04-23-phase4a-completion.md`. Phase 4a completion-redo report (successor,
not replacement) at `docs/status/2026-05-07-phase4a-completion-redo.md`.*
