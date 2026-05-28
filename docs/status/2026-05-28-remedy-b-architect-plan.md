# Architect Plan — Remedy B (centrality-CI register error)

**Plan ID:** REMEDY-B
**Date:** 2026-05-28
**Origin:** CDA SME FAIL on `feature/visualization-fixes` (`docs/status/2026-05-28-viz-fixes-cda-sme-verdict.md`)
**Pipeline status:** Posted to CDA SME gate (T1+T2+T3 methodology bundle). T4 additionally needs UI/UX gate.

**Mark's decisions (2026-05-28):**
- **Branch posture:** Rebase the non-methodology parts of `feature/visualization-fixes` onto master first (Reviewer only), then apply Remedy B as 5 new commits on top.
- **T4 bundling:** Bundle centrality label fix + TermMap AT fix + DESIGN_SYSTEM §15 docs into a single T4.

---

## Summary

The branch shipped a browser-side `mean ± 1.96·SE` CI computed from `WithinModelResult.centrality_scores_by_run` (Register 1) and attached it to `DomainResult.cultural_centrality_scores` (Register 2), labeling it "bootstrap" on four UI surfaces. Remedy B computes a real R2 model-resampling bootstrap in `cdb_analyze`, publishes `centrality_ci` on `DomainResult` (matching `oci_ci` / `similarity_ci` / `consensus_ci`), regenerates domain JSON, and has the frontend consume the published field.

## Task breakdown

### T1 — `bootstrap_centrality_ci()` in `cdb_analyze/bootstrap.py`
Resample unit = models with replacement (BOOTSTRAP_DESIGN §3.1 Option 2). B=500, `random_state=42`, percentile method. **Per-iteration eigenvector sign alignment against the reference centrality vector** (flip if `dot(boot, ref) < 0`) — non-negotiable or the CI is sign-contaminated. Degenerate path (`< 2` models) returns `{}`. Gates: CDA SME, Reviewer, Tester.

### T2 — Schema field + DATA_DICTIONARY co-update (one commit, R7)
Add `centrality_ci: dict[str, tuple[float, float]] = {}` to `DomainResult` (after L431). Default `{}` = non-breaking. DATA_DICTIONARY.md row + subsection + changelog entry in the **same commit**. Architect sign-off granted for the field once CDA SME PASS lands. Gates: CDA SME, Reviewer, Tester. Depends on T1.

### T3 — Pipeline wiring + JSON regen
`pipeline.py` ~L761–L775: call the bootstrap after `cultural_centrality_scores`, wrap in try/except like `bootstrap_term_mds_ellipses`, gate on `>= 2` models. Regenerate `data/results/{family,holidays,food}/0.3.json` + republish dashboard JSON. Additive-only diff. Gates: CDA SME, Reviewer, Tester. Depends on T1, T2.

### T4 — Frontend (bundled per Mark's decision)
Delete the `centralityCis` `useMemo` in `CentralityChart.tsx`; consume `domain.centrality_ci[modelId]`; add `centrality_ci?: Record<string, [number, number]>` to the dashboard domain type; correct the 4 "bootstrap" labels (now truthful); **fold in UI/UX item 1 (TermMap ellipse AT exposure)** and **DESIGN_SYSTEM §15.2/§15.3/§15.4**. Gates: CDA SME (label truthfulness) + UI/UX (copy, AT fix, §15) + Reviewer + Tester. Depends on T3.

### T5 — Tests (Tester-owned)
`tests/unit/test_bootstrap.py`: determinism, shape/contract, coverage sanity, degenerate path, sign-alignment, no real API calls. Prefer inline synthetic fixtures over new `tests/fixtures/` files. Gates: Reviewer, Tester. Depends on T1; parallelizable after T1 PASS.

## Dependency order
```
T1 ──┬── T2 ── T3 ── T4
     └── T5
```
Critical path: T1→T2→T3→T4. T5 parallel after T1 CDA SME PASS. SME bundling: review T1+T2+T3 together; T4 a small follow-up SME review on label truthfulness.

## Deferred methodology questions (for CDA SME ruling in its verdict)
- **Q1 (sign alignment):** Architect default = reference-vector alignment per iteration. Confirm.
- **Q2 (B):** Architect default = B=500 (matches `bootstrap_mds_ellipses`). Confirm vs B=200.
- **Q3 (n=2):** Architect default = gate bootstrap on `>= 3` models, emit `{}` at n=2 (n=2 is pathological; all v1 domains have 12). Rule.
- **Q4 (CI shape):** Architect default = bare `tuple[float, float]` per model + domain-level `centrality_ci_n_bootstrap: int = 500`. Confirm vs richer per-model `{lo, hi, n_bootstrap}` object.

## Reviewer focus
T1: sign-alignment implemented + tested; no LLM imports (R12); fixtures-only (R9). T2: schema + dict in one commit (R7); `{}` default. T3: additive-only JSON diff, no MDS-coordinate drift. T4: no phantom `var(--…)` tokens (pitfall 15); `useMemo` deleted; labels match SME T4 PASS; AT fix present; §15 added. T5: 6 tests, no real API.
