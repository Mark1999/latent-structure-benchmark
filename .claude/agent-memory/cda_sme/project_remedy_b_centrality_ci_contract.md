---
name: remedy-b-centrality-ci-contract
description: 2026-05-28 PASS-WITH-NOTES on Remedy B plan; binding Q1–Q4 rulings for centrality_ci field — reference-vector sign alignment, B=500, n>=3 gate, bare tuple no sibling n_bootstrap field
metadata:
  type: project
---

Remedy B Architect plan (T1 `bootstrap_centrality_ci` + T2 `centrality_ci` schema field + T3 pipeline wiring) gated PASS-WITH-NOTES on 2026-05-28. Verdict file `docs/status/2026-05-28-remedy-b-cda-sme-verdict.md`.

**Why:** Fix for the [[centrality-ci-register-error]] FAIL (`docs/status/2026-05-28-viz-fixes-cda-sme-verdict.md`). External AI had shipped browser-side normal-approx CI on per-run R1 loadings, labeled "bootstrap" 4 ways, affixed to R2 centrality points — two stacked errors (method label + register confusion).

**How to apply:** The four Q1–Q4 deferred rulings are now binding contract for any future SME review touching `centrality_ci`, the bootstrap module's centrality function, or the T4 frontend follow-up:

- **Q1 sign alignment** — reference-vector alignment (`dot(boot, ref) < 0 → flip`) against the full-data reference eigenvector. NOT mean-sign (that's what `compute_centrality_scores` does internally; calling it inside the bootstrap loop would silently undo reference alignment for adversarial resamples). Implement by calling `eigh` directly in the loop, flipping against `ref_eigvec`, accumulating.
- **Q2 B** — B=500, matches `bootstrap_mds_ellipses`. Phase 9a's B=200 ruling does NOT carry over because centrality operates on n=12 informants vs term-MDS's ~25 items.
- **Q3 small-n** — gate on `len(model_ids) >= 3`, emit `{}` below. n=2 is mathematically degenerate (2×2 first eigenvector is `(1,1)/√2`). T4 must suppress display when `centrality_ci == {}`; this satisfies §4.5 because the point estimate is already documented degenerate at n<3.
- **Q4 CI shape** — bare `dict[str, tuple[float, float]] = {}`. REJECTED Architect's proposed `centrality_ci_n_bootstrap: int = 500` sibling field; precedent is `oci_ci`, `similarity_ci`, `consensus_ci` — all bare tuples. `n_bootstrap` lives only in the function signature default and the DATA_DICTIONARY entry. `BootstrapEllipse.n_bootstrap` precedent does NOT generalize (only because ellipses are geometric objects requiring point-count for interpretability).

**Eight binding notes N1–N8 in the verdict.** Sign-alignment test (N7 → T5 item 5) is the load-bearing falsifiability check: without it, regressions to mean-sign or no-alignment go undetected and the originating bug class recurs. The test asserts ≥95% of bootstrap iterations have per-model loadings on the same side of zero as the reference; correct implementation gives ≈100%, mean-sign gives biased fraction, no alignment gives ≈50%.

**T4 hooks (advisory now, gating later):** delete 4 "bootstrap" label strings; NO cross-method footnote needed under Remedy B (it was a Remedy A requirement only); handle empty `centrality_ci`; rename TS `n_bootstrap` field. T4 returns as small SME follow-up review post-T3.

**Resample-unit contract:** Use `bootstrap_term_mds_ellipses`'s M-with-replacement template (Phase 9a-era pattern), NOT `bootstrap_mds_ellipses`'s per-model run-resampling template (Phase 4-era pattern). Both are R2 bootstraps but the former is the cleaner precedent for R2 quantities computed from pre-computed consensus matrices.

Related: [[centrality-ci-register-error]] (originating FAIL), [[phase9a-viz-gap-verdict]] (B=200 ruling that does NOT generalize here).
