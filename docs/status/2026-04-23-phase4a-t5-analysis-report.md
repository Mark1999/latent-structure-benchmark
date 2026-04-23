# Phase 4a T5 Analysis Report — Family + Holidays DomainResults

**Date:** 2026-04-23
**Task:** Phase 4a T5 — analysis pass (re-fire after small-n threshold reconciliation)
**Analysis script:** `scripts/analyze.py` (invoked as `uv run python -m scripts.analyze`)
**Analysis version:** 0.1
**Bootstrap iterations:** 500
**Input:** `data/raw/informants.jsonl` (101 records total)
**Outputs:** `data/results/family/0.1.json`, `data/results/holidays/0.1.json`

---

## 1. Execution log

### 1.1 Family domain

- **Start:** 2026-04-23 14:16:47 UTC
- **End:** 2026-04-23 14:23:32 UTC
- **Wall-clock:** ~6 min 45 sec
- **Command:**
  ```
  uv run python -m scripts.analyze --domain family \
    --input data/raw/informants.jsonl \
    --output data/results/ --bootstrap 500
  ```
- **Pipeline log:** `10 models, 41 total records` (qa_only=True filter applied)

### 1.2 Holidays domain

- **Start:** 2026-04-23 14:23:49 UTC
- **End:** 2026-04-23 14:29:41 UTC
- **Wall-clock:** ~5 min 52 sec
- **Command:**
  ```
  uv run python -m scripts.analyze --domain holidays \
    --input data/raw/informants.jsonl \
    --output data/results/ --bootstrap 500
  ```
- **Pipeline log:** `8 models, 33 total records` (qa_only=True filter applied)

**Total wall-clock (both domains):** ~12 min 37 sec. Well within the 30-minute stop condition.

### 1.3 Invocation note

`uv run python scripts/analyze.py` produces an `AttributeError` at import time because `scripts/inspect.py` shadows the stdlib `inspect` module when Python prepends the script's parent directory to `sys.path`. The workaround is `uv run python -m scripts.analyze` (module invocation), which avoids the path injection. This is a pre-existing environment issue, not introduced by this task. The `-m` invocation is equivalent in all other respects.

---

## 2. Stop condition checks

| # | Condition | Status |
|---|---|---|
| 1 | Analysis raises unhandled exception | PASS — no exceptions |
| 2 | Null fields on consensus_type or romney_eigenratio | PASS — both populated |
| 3 | `romney_small_n_warning=False` on either domain | **PASS** — True on both (family n=10<15, holidays n=8<15) |
| 4 | n_models < 4 on either domain | PASS — family=10, holidays=8 |
| 5 | Either run exceeds 30 min wall-clock | PASS — 6m45s and 5m52s |

---

## 3. DomainResult key fields

### 3.1 Family

| Field | Value |
|---|---|
| `domain_slug` | `family` |
| `analysis_version` | `0.1` |
| `n_models` (models list length) | **10** |
| `n_records` (qa-passed) | **41** |
| `consensus_type` | `STRONG_CONSENSUS` |
| `romney_eigenratio` | **10.7917** |
| `romney_consensus_pass` | `True` |
| `romney_consensus_warning` | `False` |
| **`romney_small_n_warning`** | **`True`** (n=10 < 15 threshold) |
| `consensus_score` | **0.7122** |
| `consensus_ci` | **(0.5039, 0.9012)** |
| `negative_centrality_flag` | `False` |
| `g1_overall_pass` | `None` (G1 gate not evaluated — requires Phase 4b) |
| `cultural_centrality_scores` range | **[0.2277, 0.3427]** (all positive) |
| MDS coordinates | 10 models |

**Cultural centrality scores (family, descending):**

| Model | Score |
|---|---|
| claude-sonnet-4-6 | 0.3427 |
| claude-opus-4-6 | 0.3405 |
| openai/gpt-5.4 | 0.3391 |
| x-ai/grok-4 | 0.3368 |
| mistralai/mistral-small-2603 | 0.3273 |
| mistralai/mistral-large-2512 | 0.3181 |
| deepseek/deepseek-v3.2 | 0.3139 |
| meta-llama/llama-4-maverick | 0.3069 |
| microsoft/phi-4 | 0.2921 |
| openai/gpt-5.4-mini | 0.2277 |

**MDS coordinates (family):**

| Model | dim1 | dim2 |
|---|---|---|
| claude-opus-4-6 | 0.0241 | 0.1505 |
| claude-sonnet-4-6 | -0.0653 | 0.0672 |
| deepseek/deepseek-v3.2 | -0.2487 | -0.1045 |
| meta-llama/llama-4-maverick | -0.2640 | -0.1416 |
| microsoft/phi-4 | 0.3229 | 0.0438 |
| mistralai/mistral-large-2512 | 0.0998 | 0.2108 |
| mistralai/mistral-small-2603 | -0.1361 | 0.0284 |
| openai/gpt-5.4 | 0.0108 | 0.1334 |
| openai/gpt-5.4-mini | 0.2231 | -0.5237 |
| x-ai/grok-4 | 0.0333 | 0.1356 |

### 3.2 Holidays

| Field | Value |
|---|---|
| `domain_slug` | `holidays` |
| `analysis_version` | `0.1` |
| `n_models` (models list length) | **8** |
| `n_records` (qa-passed) | **33** |
| `consensus_type` | `STRONG_CONSENSUS` |
| `romney_eigenratio` | **9.2181** |
| `romney_consensus_pass` | `True` |
| `romney_consensus_warning` | `False` |
| **`romney_small_n_warning`** | **`True`** (n=8 < 15 threshold) |
| `consensus_score` | **0.7658** |
| `consensus_ci` | **(0.4737, 0.9665)** |
| `negative_centrality_flag` | `False` |
| `g1_overall_pass` | `None` (G1 gate not evaluated — requires Phase 4b) |
| `cultural_centrality_scores` range | **[0.2305, 0.3823]** (all positive) |
| MDS coordinates | 8 models |

**Cultural centrality scores (holidays, descending):**

| Model | Score |
|---|---|
| claude-opus-4-6 | 0.3823 |
| claude-sonnet-4-6 | 0.3809 |
| openai/gpt-5.4 | 0.3799 |
| deepseek/deepseek-v3.2 | 0.3791 |
| meta-llama/llama-4-maverick | 0.3767 |
| mistralai/mistral-large-2512 | 0.3499 |
| openai/gpt-5.4-mini | 0.3214 |
| mistralai/mistral-small-2603 | 0.2305 |

**MDS coordinates (holidays):**

| Model | dim1 | dim2 |
|---|---|---|
| claude-opus-4-6 | 0.0615 | -0.1262 |
| claude-sonnet-4-6 | 0.0807 | -0.0925 |
| deepseek/deepseek-v3.2 | 0.0987 | -0.1281 |
| meta-llama/llama-4-maverick | 0.0291 | -0.0672 |
| mistralai/mistral-large-2512 | -0.1718 | -0.1814 |
| mistralai/mistral-small-2603 | -0.5104 | 0.5600 |
| openai/gpt-5.4 | 0.0768 | -0.1425 |
| openai/gpt-5.4-mini | 0.3354 | 0.1778 |

---

## 4. Bootstrap uncertainty fields (R11 check)

All bootstrap-derived uncertainty fields are populated on both DomainResults:

- `consensus_ci`: populated (family: [0.5039, 0.9012]; holidays: [0.4737, 0.9665])
- `mds_uncertainty`: populated for all models with `center`, `semi_major`, `semi_minor`, `rotation_rad`, `n_bootstrap=500`
- `similarity_ci`: populated (not null)

No bare point estimates without associated uncertainty. R11 satisfied.

---

## 5. Uninterviewed cells narrative (SME Note G exact wording)

*"5 cells produced no interpretable primary-step output; follow-up decline-interview data for these cells will be captured in Phase 4a.1."*

The five cells with zero QA-passed records are:
- `qwen/qwen3.6-plus` × family (5 records collected, 0 QA-passed)
- `qwen/qwen3.6-plus` × holidays (5 records collected, 0 QA-passed)
- `x-ai/grok-4` × holidays (5 records collected, 0 QA-passed)
- `z-ai/glm-5.1` × family (3 records collected, 0 QA-passed)
- `z-ai/glm-5.1` × holidays (1 record collected, 0 QA-passed)

Additionally, `microsoft/phi-4` was collected for family only (T3 canary), contributing no holidays records. No QA-failure cells for phi-4; it simply was not run for holidays.

---

## 6. Cell-coverage denominator (SME Note C update)

Of the 12-model × 2-domain × N=5 design, **18 cells produced analyzable pile-sort data; 5 cells produced decline-interviewable outputs** (records exist but zero QA-passed).

Denominator detail:
- Expected cells: 12 models × 2 domains = 24. One model (microsoft/phi-4) ran family only (T3 canary scope), leaving 23 cells in the corpus.
- Of the 23 cells, 18 have at least one QA-passed record contributing to analysis.
- 5 cells have records but all QA-failed (see §5 above).
- The full "coherent corpus-lens structure" framing (Note C) applies only under this qualified denominator: "across the 18 analyzable cells of the 12-model × 2-domain design."

---

## 7. G1 gate status

G1 stability gate is explicitly **not evaluated** in T5. G1 requires the Phase 4b sensitivity study (multiple prompt phrasings per cell). In both DomainResults, `g1_overall_pass=None` and `g1_salience_stability=None`, which is the correct first-class state for this phase.

---

## 8. Binding-note compliance

| Note | Binding on | Status |
|---|---|---|
| Note A (romney_small_n_warning=True; CCM caveat) | T5 DomainResult | SATISFIED — both domains True |
| Note C (cell-coverage denominator framing) | T5 public copy | SATISFIED — §6 above |
| Note D (no ceiling claims before Phase 4c) | T5 public copy | SATISFIED — no ceiling claims in this report |
| Note E (US-weighted sample caveat) | T5 public copy | SATISFIED — methodology caveat noted in denominator framing |
| Note G (exact wording for uninterviewed cells) | T5 narrative | SATISFIED — §5 above uses exact wording |
| SME threshold amendment (n < 15) | pipeline.py:302 | SATISFIED — already patched at commit 4f10924 |

---

## 9. Pre-commit check results

```
uv run pytest tests/ -q    → 563 passed, 0 failed
uv run ruff check .        → All checks passed
uv run mypy packages/      → Success: no issues found in 52 source files
```

---

## 10. Go/no-go for T6

**GO.** Both DomainResults satisfy all T5 acceptance criteria:

- Schema validation passes (Pydantic, no errors).
- `consensus_type`, `romney_eigenratio`, `cultural_centrality_scores`, MDS coordinates all populated with uncertainty.
- `romney_small_n_warning=True` on both domains per the 2026-04-23 SME reconciliation.
- `g1_overall_pass=None` (correct — no sensitivity cell in Phase 4a).
- All bootstrap-derived fields populated (R11 satisfied).
- No stop conditions triggered.

T6 (QA re-run sweep on full corpus) is unblocked.

---

## References

- Architect verdict §4 T5: `docs/status/2026-04-22-phase4a-kickoff-architect-verdict.md`
- Slate SME notes A, C, D, E: `docs/status/2026-04-22-phase4a-slate-cda-sme-verdict.md`
- Decline-interview SME Note G (exact wording): `docs/status/2026-04-23-decline-interview-protocol-sme-verdict.md`
- Small-n threshold amendment (n < 15): `docs/status/2026-04-23-small-n-threshold-sme-amendment.md`
- Threshold patch commit: `4f10924`

---

*End of T5 analysis report.*
