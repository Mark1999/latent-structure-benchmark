# F2-T02 Architect Plan — Romney CCM Eigenratio Wiring

**Task ID:** F2-T02
**Branch:** `feat/t02-romney-ccm-eigenratio`
**Status:** Architect PASS; CDA SME PASS-WITH-NOTES on file (see `docs/status/2026-04-20-f2-cda-sme-verdict.md`)
**Binding thresholds:** SME ruling — `romney_small_n_warning=True` when `n_models < 8`; always `False` when `n_models >= 8`.

---

## 1. Summary

Wire Romney CCM eigenratio into `cdb_analyze/pipeline.py`, populate existing-but-null Romney fields on `DomainResult`, and add one typed field — `romney_small_n_warning: bool` — to honestly represent the small-n statistical-power limitation at n=4 (shakedown) and n=12 (Phase 4a). SME ruling: dual-threshold evaluation proceeds at small n but must carry a warning flag; shakedown produces no scientific consensus claim regardless of eigenratio value.

## 2. Exact schema change

Insert into `DomainResult` in `packages/cdb_core/cdb_core/schemas.py`, immediately after `romney_consensus_warning` and before `consensus_type`:

```python
romney_small_n_warning: bool = False  # True when n_models < 8 at Romney
                                      # computation time. Dual-threshold
                                      # pass/fail is statistically under-
                                      # powered below n=8; flag will be
                                      # set on every canonical run until
                                      # corpora grow. See SME verdict
                                      # 2026-04-20 and DATA_DICTIONARY.md
                                      # §2 Romney block.
```

Type `bool` (not `bool | None`): always knowable. Default `False`. No nullable semantics.

## 3. Exact `DATA_DICTIONARY.md` entry

Insert in §2 DomainResult table, after `romney_consensus_warning` row:

```markdown
| `romney_small_n_warning` | `bool` | No (default `False`) | True when `n_models < 8` at the time of Romney CCM computation. Small-n dual-threshold evaluation (operational 5.0, classic 3.0) is statistically underpowered at n=4 (shakedown) and n=12 (Phase 4a Register 2); this flag is the honest representation, not an edge case. Always `False` for `n_models >= 8` (SME binding threshold, 2026-04-20 verdict). Also `False` when Romney was not computed at all (single-model degenerate case, n < 2). Dashboard consumers must display a visible small-n caveat alongside `romney_consensus_pass` / `romney_consensus_warning` whenever this flag is True. |
```

Changelog entry at top, v0.1.5:

```markdown
- **v0.1.5** (2026-04-21) — F2-T02: `DomainResult` gains `romney_small_n_warning: bool` (default `False`). Set `True` when n_models < 8 at Romney CCM computation time — dual-threshold pass/fail is statistically underpowered below n=8 per SME 2026-04-20 verdict. Non-breaking addition. Companion wiring populates the previously-null `romney_eigenratio`, `romney_consensus_pass`, and `romney_consensus_warning` fields.
```

## 4. Consensus.py helper — does not exist, must be added

Grep of `consensus.py` shows no eigenratio function. `classify_consensus` consumes eigenratio but does not compute one. Coder adds:

- **Name:** `compute_romney_eigenratio`
- **Signature:** `def compute_romney_eigenratio(similarity_matrix: NDArray[np.float64]) -> float | None`
- **Placement:** immediately after `compute_centrality_scores`, before `classify_consensus`
- **Contract:** Returns λ₁/λ₂ of the symmetric model × model similarity matrix via `np.linalg.eigh`, sorted descending.
- **Degenerate guards:**
  - Return `None` if `similarity_matrix.shape[0] < 2`.
  - Return `None` if `abs(eigvals[1]) < 1e-12` (numerically-degenerate perfect-consensus case).
- **Docstring:** reference Romney/Weller/Batchelder 1986; note `classify_consensus` is the downstream caller.

## 5. Pipeline wiring logic

**Insertion point:** immediately after the centrality block (commit `de6bf73`), before clustering. Rationale: centrality and Romney both consume `sim_mean`, both feed T01's `classify_consensus`; contiguous placement keeps methodology computations together.

**Pseudocode:**

```
IF len(model_ids) >= 2:
    sim_np  = np.array(similarity_matrix, dtype=np.float64)
    eigenratio = compute_romney_eigenratio(sim_np)
    IF eigenratio is not None:
        romney_consensus_pass    = eigenratio >= ROMNEY_THRESHOLD_LSB       # 5.0
        romney_consensus_warning = (ROMNEY_THRESHOLD_CLASSIC <= eigenratio
                                     < ROMNEY_THRESHOLD_LSB)                # [3.0, 5.0)
        romney_small_n_warning   = (len(model_ids) < 8)
    ELSE:
        romney_consensus_pass    = None
        romney_consensus_warning = None
        romney_small_n_warning   = False
ELSE:
    eigenratio               = None
    romney_consensus_pass    = None
    romney_consensus_warning = None
    romney_small_n_warning   = False
```

Log line mirrors centrality's: `logger.info("Romney CCM: eigenratio=%.3f, pass=%s, warning=%s, small_n=%s", ...)` when computed; single "Romney skipped (n<2)" line when degenerate.

**Do not touch `consensus_score`** — it remains an alias during the deprecation window per schema comment.

## 6. Test plan

Coder writes these. File: `packages/cdb_analyze/tests/test_consensus_romney.py` (or extend `test_pipeline.py`; Coder's judgment). Fixtures only — no real API calls.

1. `test_compute_romney_eigenratio_basic` — 4×4 known-eigenvalue matrix; assert ratio to 1e-9.
2. `test_compute_romney_eigenratio_returns_none_for_n_less_than_2` — 1×1 matrix.
3. `test_compute_romney_eigenratio_returns_none_when_second_eigenvalue_near_zero` — rank-1 matrix.
4. `test_romney_eigenratio_populated_for_n4_shakedown_fixture` — 4-model fixture; `romney_eigenratio is not None`.
5. `test_romney_small_n_warning_true_when_n_less_than_8` — n=4 fixture; flag True.
6. `test_romney_small_n_warning_false_when_n_geq_8` — synthetic 8-model fixture; flag False.
7. `test_romney_consensus_pass_threshold_5` — engineered eigenratio ≥ 5.0; pass=True, warning=False.
8. `test_romney_consensus_warning_zone_3_to_5` — eigenratio ∈ [3.0, 5.0); pass=False, warning=True.
9. `test_romney_single_model_degenerate_no_exception` — n=1 records; all four Romney fields clean.

Bootstrap CI on the eigenratio is out of scope per SME; `consensus_ci` remains the mean-pairwise-similarity CI.

## 7. Cross-task dependencies

- **T02 unblocks T01.** `classify_consensus` requires `eigenratio: float` input. T01 cannot land before T02.
- **T02 vs T03.** T03 (`de6bf73`) already merged. T02 lands after; insertion point is adjacent to T03's centrality block.
- No other blocked tasks.

## 8. Branch + PR workflow

- **Branch:** `feat/t02-romney-ccm-eigenratio`
- **CLAUDE.md §6 rule 7:** schema change + DATA_DICTIONARY update must be in the **same commit**.
- **Commit message:** `feat(analyze): wire Romney CCM eigenratio with small-n warning flag`
- **PR body:** references F2-T02, SME verdict file, n≥8 threshold, shakedown Finding 2.
- **CI gates:** ruff, mypy, pytest, no-LLM-imports static check, gitleaks.

## 9. 3rd-party reviewer cross-reference (perspective only, not decisional)

- **Codex** (`docs/3rdpartyreviews/CODEX_INDEPENDENT_AUDIT_ASSESSMENT.md` Finding 2): notes that `consensus_score` is a placeholder proxy rather than full cultural consensus analysis. Corroborates the T02 wiring.
- **Gemini, Grok:** no relevant opinion on small-n Romney or dual-threshold logic.

Reviewer inputs treated as perspective, not decision. SME n≥8 threshold is binding.

## 10. Reading list for Coder

- `docs/status/2026-04-20-f2-cda-sme-verdict.md` — binding n≥8 ruling
- `docs/status/2026-04-20-shakedown-findings.md` §4 Finding 2 — defect motivator
- `docs/DATA_DICTIONARY.md` §2 — Romney block context
- `packages/cdb_core/cdb_core/schemas.py` lines 315–353
- `packages/cdb_analyze/cdb_analyze/consensus.py` — classify_consensus consumer
- `CLAUDE.md` §6 rule 7
- `ARCHITECTURE.md` §4.2 Romney CCM section
