# CDA SME Verdict — Remedy B Architect plan (centrality CI register fix)

**Date:** 2026-05-28
**Reviewer:** CDA SME
**Plan reviewed:** `docs/status/2026-05-28-remedy-b-architect-plan.md` (REMEDY-B)
**Originating verdict (spec):** `docs/status/2026-05-28-viz-fixes-cda-sme-verdict.md` (FAIL on `feature/visualization-fixes`)
**Companion ground truth:** `docs/BOOTSTRAP_DESIGN.md` §1–§8, `ARCHITECTURE.md` §1.5 / §4.2 / §4.5, `CLAUDE.md` §6 rule 10 / §7 / §9 pitfall 8.
**Scope of this review:** T1 + T2 + T3 methodology bundle (new R2 model-resampling bootstrap `bootstrap_centrality_ci()`, `centrality_ci` schema field on `DomainResult`, and the pipeline wiring). T4 will return as a small follow-up SME review on label truthfulness.

---

## CDA SME VERDICT: PASS-WITH-NOTES

| Axis | Verdict |
|---|---|
| Axis 1 — Protocol validity      | N/A (analysis layer; CDA elicitation untouched) |
| Axis 2 — Analytical validity    | **PASS-WITH-NOTES** |
| Axis 3 — Claims validity        | **PASS** |
| Axis 4 — Audience translation   | N/A for this bundle (T4 carries the audience-facing surfaces) |
| Register compliance             | **PASS** |
| Vocabulary compliance           | **PASS** |

The plan is on-doctrine. It correctly identifies the Register 2 sampling unit (models with replacement), aligns the new field's naming and shape with the existing `*_ci` precedent, and locates the computation in the right layer (`cdb_analyze.bootstrap`) — fully resolving F1, F2, F4, F5 of the originating verdict and the analytical half of F3. The notes below resolve the four deferred questions, ratify the resample contract against `BOOTSTRAP_DESIGN.md` §3, and bind T5's test coverage.

---

## Rulings on the four deferred questions

### Q1 — Sign-alignment convention. CONFIRMED (with binding refinement).

**Ruling:** Per-iteration **reference-vector alignment** is the correct convention. Flip the bootstrap eigenvector when `dot(boot_eigvec, ref_eigvec) < 0` *before* recording per-model loadings into the accumulator, where `ref_eigvec` is the first eigenvector of the *reference* (full-data) inter-model similarity matrix.

**Why this is the right rule (and the methodologically dangerous alternatives are not):**

- Eigenvector sign is arbitrary out of any eigensolver; without alignment the bootstrap distribution per model is bimodal (the same loading at `+x` and `-x`), and the resulting percentile CI is meaningless (it will straddle zero by construction for nearly every model).
- The "mean-sign" convention used inside `compute_centrality_scores` (`packages/cdb_analyze/cdb_analyze/consensus.py` L294 — "flip so the mean loading is positive") is NOT a substitute under resampling. With model-with-replacement resampling, the *composition* of the resample changes per iteration; the mean-sign rule keys on the resample's composition rather than the reference axis, so it can flip the eigenvector relative to the reference for iterations where the resample happens to over-draw negative-centrality models. The result is a sign-incoherent CI that under-states uncertainty for central models and over-states it for opposing models.
- "Anchored model" (fix the sign by forcing one specific model's loading to be positive) introduces a different pathology: if the anchor model is itself near-zero in the reference, sign-alignment fails when its bootstrap loading flips sign for reasons unrelated to the global eigenvector orientation.

**Binding refinement (T1 acceptance criterion):**

1. T1 MUST compute the reference centrality vector from the full-data similarity matrix using `compute_centrality_scores()` (so the dashboard-published reference and the bootstrap's reference are the same object). Storing the reference as a numpy array (already in the model_id-ordered basis) inside `bootstrap_centrality_ci()` is sufficient.
2. The flip MUST be applied to the *raw eigenvector returned by `np.linalg.eigh`* on the bootstrap-iteration similarity matrix, BEFORE re-applying the mean-sign convention that `compute_centrality_scores` would otherwise apply. The simplest correct implementation: call `eigh` directly inside the bootstrap loop, take the first eigenvector, dot it against `ref_eigvec`, flip if negative. Do NOT call `compute_centrality_scores` inside the loop — the mean-sign re-flip inside that helper would silently undo the reference-vector alignment for any iteration whose resample-mean has the opposite sign.
3. T5 MUST include a test that confirms the bootstrap is reference-aligned and not mean-aligned. The test contract is below in §"T5 test contract".

### Q2 — B (bootstrap iterations). RULED B = 500.

**Ruling:** Use **B = 500**, matching `bootstrap_mds_ellipses` (`packages/cdb_analyze/cdb_analyze/bootstrap.py` L38) and the established R2 contract in `BOOTSTRAP_DESIGN.md` §3.1.

**Why not B = 200 (the Phase 9a term-MDS ruling):** B = 200 was accepted for the term-level R2 bootstrap because that bootstrap operates on ~25 items and the percentile CI is empirically stable at that scale per the Phase 9a F4 saturation check. Per-model centrality CIs operate on n=12 models (a much smaller informant set) and the bootstrap distribution is correspondingly noisier at the percentile tails. B = 500 buys cheap stability at the 2.5th / 97.5th percentile without expanding compute beyond what `bootstrap_mds_ellipses` already costs in the same pipeline step. There is no compute argument for the smaller B here; the dominant cost in `bootstrap_centrality_ci()` is the per-iteration `compute_cross_model_similarity` + `eigh`, both of which are negligible at n=12.

**Acceptance criterion:** T1's default parameter is `n_bootstrap: int = 500`. The function signature exposes `n_bootstrap` and `random_state` as keyword arguments matching the conventions of `bootstrap_mds_ellipses` and `bootstrap_term_mds_ellipses` for cross-call consistency.

### Q3 — Small-n behaviour. CONFIRMED, with a published-degenerate-state clarification.

**Ruling:** Gate the bootstrap on **`>= 3` models**, emit `{}` (empty dict — no CI) for `< 3`. The Architect default is accepted. **At `n = 2` the centrality eigenvector is mathematically degenerate** (a 2×2 symmetric matrix's first eigenvector at any non-trivial similarity is `(1, 1)/√2` up to sign; bootstrap loadings are constant and the percentile CI is illusory zero-width). `n = 2` is not a credible regime for centrality at all — emitting no CI is the honest answer, and the existing R10/§4.5 rule is satisfied because the centrality *point estimate itself* is already documented as degenerate at `n = 2` (centrality_scores returns `{}` from `compute_centrality_scores` at `n < 2` and is not meaningfully discriminating at `n = 2`).

**Confirmation that this does not violate the §4.5 "no point estimate without uncertainty" doctrine:**

- The doctrine binds *display* of a point estimate without uncertainty. When `centrality_ci == {}` at `n = 2`, T4 MUST suppress the centrality chart (or replace it with a "centrality is degenerate at n < 3" annotation, per UI/UX agent's choice in T4). T4's audience-translation review will gate the visual end-state; for the T1+T2+T3 bundle, it is sufficient that the published data carry no centrality CI in the `< 3` case.
- This is symmetric with `cultural_centrality_scores = {}` at `n < 2` already on `pipeline.py` L767 — the dashboard already has to handle the empty-scores case. T4 extends that handling to the `n ∈ {2}` case for centrality CI.
- All v1 production domains have n = 12. The degenerate branch exists for forward-compatibility with future low-n domains and for fixture tests, not as a production path.

**Acceptance criterion:** T1 gates on `len(model_ids) >= 3`. T3 wraps the call in try/except (like `bootstrap_term_mds_ellipses`) and sets `centrality_ci = {}` on either degenerate-gate or exception. The pipeline log line distinguishes the two ("skipped: n<3" vs "failed: <reason>").

### Q4 — Published CI shape. CONFIRMED with one binding shape correction.

**Ruling:** **Per-model bare `tuple[float, float]` is correct.** Reject the richer per-model `{lo, hi, n_bootstrap}` object. **However**, the domain-level `centrality_ci_n_bootstrap: int = 500` proposed by the Architect is itself **rejected as a separate field**. Use the existing `BootstrapEllipse.n_bootstrap` precedent of carrying `n_bootstrap` *adjacent to* each CI, not as a domain-wide scalar.

**Reasoning:**

- The existing precedent is split. `oci_ci: tuple[float, float]` (scalar tuple, no `n_bootstrap`), `consensus_ci: tuple[float, float]` (scalar tuple, no `n_bootstrap`), `similarity_ci: list[list[tuple[float, float]]]` (per-cell tuples, no `n_bootstrap`) — all bare tuples. `mds_uncertainty: dict[str, BootstrapEllipse]` — richer object that *does* carry `n_bootstrap` per ellipse.
- The right precedent for `centrality_ci` is the **bare-tuple per-cell pattern of `similarity_ci`**, because centrality CIs are per-model scalars analogous to similarity CIs being per-cell scalars. Both are produced by the same R2 model-resampling bootstrap and both will, in practice, share an identical `n_bootstrap` value at any given run (because they're computed in the same pipeline step).
- Adding `centrality_ci_n_bootstrap: int = 500` as a domain-level scalar is novel — neither `similarity_ci` nor `consensus_ci` nor `oci_ci` carry a sibling scalar of this kind. The `n_bootstrap` value is recoverable from provenance (the analysis_version + the bootstrap module's hard-coded default), so an explicit field is not analytically necessary. If discoverability is the concern, the better mitigation is a docstring + DATA_DICTIONARY note pointing to `bootstrap_centrality_ci.n_bootstrap` as the source of truth.
- The `BootstrapEllipse.n_bootstrap` precedent applies only because ellipses are a non-trivial geometric object whose interpretability requires knowing how many bootstrap points fit them. A bare `(lo, hi)` tuple does not require the same metadata to be auditable.

**Acceptance criteria (T2 schema sign-off):**

1. T2 field signature: `centrality_ci: dict[str, tuple[float, float]] = {}`, placed adjacent to `cultural_centrality_scores` on `DomainResult` (after L431). Default `{}` is non-breaking and matches the empty-state convention of the existing `cultural_centrality_scores: dict[str, float] = {}`.
2. T2 does NOT add `centrality_ci_n_bootstrap` as a sibling field. The `n_bootstrap` value lives only in the bootstrap module's signature (`n_bootstrap: int = 500`).
3. T2's `DATA_DICTIONARY.md` row MUST cite (a) `B = 500`, (b) the model-resampling-with-replacement R2 sampling unit, (c) percentile method (2.5th / 97.5th), (d) the reference-vector sign-alignment convention from Q1, and (e) the `>= 3 models` gate from Q3. These are the audit hooks that replace an explicit `n_bootstrap` sibling field.
4. The same DATA_DICTIONARY entry MUST contain the sentence: *"This CI is a Register 2 quantity. It is NOT the within-model run-level dispersion that the Phase 9a-pre dashboard briefly displayed; see `docs/status/2026-05-28-viz-fixes-cda-sme-verdict.md` F2 for the originating register error."* This is the audit trail for the next reviewer who wonders why this field was added.

---

## Resample-unit ratification against `BOOTSTRAP_DESIGN.md` §3

**Is "models with replacement" the correct R2 unit for inter-model centrality?** **Yes — unambiguously.** Per BOOTSTRAP_DESIGN.md §3.1, the R2 contract is: resample the informant unit (models) with replacement, B = 500, percentile method, with each iteration *recomputing the downstream R2 quantity from the resampled informant set*. Cultural centrality is a Register 2 quantity (first eigenvector of the inter-model similarity matrix), so its bootstrap MUST resample models. The `bootstrap_mds_ellipses` precedent (which resamples runs *within* each model to feed an R2 quantity) is a Phase 4-era variant accepted at that time as Option 2's downstream-of-Level-1 implementation; the cleaner Phase 9a-era precedent (`bootstrap_term_mds_ellipses`, which resamples models from pre-computed consensus matrices) is the one the Architect's plan correctly follows.

Note that this means T1 will use **the same M-with-replacement resample loop** as `bootstrap_term_mds_ellipses` rather than the per-model run-resampling loop of `bootstrap_mds_ellipses`. The Architect's plan is consistent with this; flagging it explicitly so the Coder does not copy the wrong template.

---

## Resolution status of the originating F1–F5 findings

| Finding (originating verdict) | Status under Remedy B |
|---|---|
| F1 — normal-approx interval labeled "bootstrap" four times | **Fully resolved** once T1+T2+T3 land and T4 consumes `domain.centrality_ci`. Labels become truthful by construction. |
| F2 — R1 quantity displayed as R2 uncertainty (register error) | **Fully resolved.** T1 computes a genuine R2 model-resampling bootstrap; T2 publishes it; T3 wires it; T4 consumes it. The R1 surface (`centrality_scores_by_run`) is no longer the source of the chart's CI. |
| F3 — n=2 minimum with `1.96·SE` is indefensible | **Analytically resolved** for the T1–T3 bundle (gate on `>= 3`; emit `{}` at `n < 3`; no z-multiplier anywhere because percentile method). **T4 must enforce the display side** — at `n = 2` the chart MUST NOT render bare error bars derived from any other source. T4 verdict will check this. |
| F4 — SR copy makes false claim and elides register issue | **Resolved structurally** by T1–T3 (no false claim is possible once the published CI is a real R2 bootstrap). **T4 must replace the SR copy** to match the new published statistic and to drop the cross-method footnote requirement (it is no longer needed — the centrality CI now uses the same method as `oci_ci`, `similarity_ci`, `consensus_ci`). T4 verdict carries the SR copy review. |
| F5 — browser-side recomputation fragments the uncertainty story | **Fully resolved.** T4 deletes the L121 `useMemo` and consumes the published field; the dashboard returns to its single-source-of-uncertainty contract (`cdb_analyze` computes, `cdb_publish` publishes, frontend displays). |

No standing findings carry forward to a subsequent SME review beyond the T4 review hooks above.

---

## `centrality_ci` field placement and naming — PASS

- **Name:** `centrality_ci`. Consistent with the `*_ci` suffix convention shared by `oci_ci` (WithinModelResult), `similarity_ci` (DomainResult), `consensus_ci` (DomainResult), and `g1_*` axes' `_pass` siblings. PASS.
- **Shape:** `dict[str, tuple[float, float]]` — same shape pattern as `cultural_centrality_scores: dict[str, float]` extended with a tuple. Matches the per-model keying. PASS.
- **Default:** `{}` — matches `cultural_centrality_scores` default and the non-breaking-additive convention. PASS.
- **Placement:** Immediately after `cultural_centrality_scores` on `DomainResult` (Architect proposes after L431). Adjacency makes the field's coupling to centrality scores obvious in the schema. PASS.

---

## T5 test contract — binding refinements

The Architect's enumeration ("determinism, shape/contract, coverage sanity, degenerate path, sign-alignment, no real API calls") is the right *list*. Below are the binding test contracts each entry MUST satisfy:

1. **Determinism.** Two calls with the same `random_state` produce bit-identical `centrality_ci` dicts. (Mirror `test_bootstrap_mds_ellipses_determinism`.)
2. **Shape/contract.**
   - Returned object is `dict[str, tuple[float, float]]`.
   - Keys are exactly the union of `model_ids` passed to `compute_centrality_scores` on the reference solution.
   - Every value satisfies `lo <= reference_score <= hi` for the reference score at that model — within numerical tolerance. (If this fails for any model, the bootstrap distribution and the reference point are inconsistent — either a sign-alignment bug or a Procrustes/eigh ordering bug.)
3. **Coverage sanity.** On a synthetic fixture where the inter-model similarity matrix has a known low-noise structure (e.g., block-structured 12×12 with one or two outlier models), the 95% CI widths should be tight on the in-block models and visibly wider on the outliers. Test asserts ordering (width(outlier_i) > width(in_block_j) for paired i, j) rather than absolute widths — the latter is fragile to RNG.
4. **Degenerate paths.**
   - `n_models < 3` returns `{}`.
   - Catastrophic resample (e.g., all-zeros similarity) does not raise; the function returns `{}` or a sensible degenerate dict (mirror the `bootstrap_mds_ellipses` try/except contract — though here the right behavior is `{}` because there's no fallback "reference" CI that makes sense to emit).
5. **Sign-alignment (the load-bearing test for Q1).** Construct a synthetic fixture where the reference centrality vector has known orientation (e.g., 5 positive-loaded models + 5 negative-loaded models). Run the bootstrap. Assert that for at least 95% of bootstrap iterations, the recorded loading for each model is on the SAME side of zero as the reference loading for that model. Without reference-vector alignment, this fraction will be ≈50% by construction; with mean-sign alignment, the fraction will be biased by resample composition and will fail this test on the configured fixture. With correct reference-vector alignment, the fraction will be ≈100%. THIS TEST IS THE NON-OPTIONAL CHECK that the Q1 contract was implemented correctly.
6. **No real API.** Fixture-based synthetic data only. Mirror `tests/fixtures/README.md` conventions.

**Adequacy assessment:** With the binding test 5 spelled out as above, T5's contract adequately covers the methodology. The Architect's "sign-alignment" bullet by itself was ambiguous (sign-alignment *to what*?); the binding form makes it falsifiable.

---

## T4 audience-translation hooks (advisory, not gating this verdict)

These will be checked when T4 returns for SME review. Flagging now so T4 does not surprise on submission:

- T4 MUST delete the four "bootstrap" label strings enumerated in F1 of the originating verdict and replace them with copy that accurately describes what `domain.centrality_ci[modelId]` is: "95% bootstrap CI on cultural centrality (model-resampled, B=500)." The exact wording is UI/UX agent's call; truthfulness is SME's.
- T4 MUST NOT carry forward the cross-method footnote requirement from Remedy A.1 / A.3 — that requirement existed because the original CI was methodologically different from the rest of the dashboard's CIs. Under Remedy B it uses the same method as `oci_ci`, `similarity_ci`, `consensus_ci`, so no footnote is required. (T4 may choose to keep a footnote pointing readers to the methodology page; that's an audience-translation choice, not an SME requirement.)
- T4 MUST handle the `centrality_ci == {}` empty state. At `n < 3` (the degenerate gate) and on bootstrap exceptions, the chart should suppress error bars or replace the chart with an annotation, not silently fall back to any other CI source.
- T4 MUST rename the TypeScript field `n_bootstrap` (the originating misnomer per F1 of the originating verdict) to align with the published-field naming. The dashboard's `DomainExtended` type adds `centrality_ci?: Record<string, [number, number]>`; the existing `n_bootstrap` field on the TS centrality-CI record should be deleted alongside the `useMemo`.

---

## Vocabulary compliance — PASS

The plan and the T1–T3 surfaces carry no §1.5.4 / §7 forbidden vocabulary. "Cultural centrality," "model-resampling bootstrap," "Register 2" are all on-doctrine. The DATA_DICTIONARY copy required in T2 §Q4 acceptance criterion 4 contains the phrase "the within-model run-level dispersion" — confirming this is a description of what was *previously, incorrectly* displayed, not a claim about what `centrality_ci` represents. PASS.

---

## Register compliance — PASS

T1's resample unit (models with replacement) operates at Register 2. The bootstrap recomputes a Register 2 quantity (centrality on the inter-model similarity matrix) from each Register 2 resample. The `underestimates_uncertainty` annotation requirement from `BOOTSTRAP_DESIGN.md` §2 / §3 does NOT apply (that annotation is Register-1-only; R2 model resamples are between distinct informants). PASS.

The Q1 sign-alignment rule keeps the R2 register clean: the reference vector is the R2 reference, and per-iteration alignment ensures the percentile aggregation remains an R2 quantity rather than a sign-confounded average.

---

## Required before merge (binding notes)

These notes are mandatory and must be applied before the Reviewer agent receives the T1+T2+T3 PR:

**N1.** T1 MUST implement reference-vector sign alignment per Q1. The reference vector is the first eigenvector of the full-data similarity matrix (the same eigenvector that `compute_centrality_scores` returns, *after* its mean-sign convention). The alignment check is `dot(boot_eigvec, ref_eigvec) < 0 → flip`. Do NOT call `compute_centrality_scores` inside the bootstrap loop (its internal mean-sign flip would undo the reference-vector alignment for adversarial resamples).

**N2.** T1 MUST use `n_bootstrap: int = 500` and `random_state: int = 42` keyword defaults, matching `bootstrap_mds_ellipses`.

**N3.** T1 MUST gate on `len(model_ids) >= 3`. At `n < 3`, return `{}`. At `n = 2` specifically, log a single-line warning naming the degeneracy (so the rare future low-n domain produces a discoverable signal).

**N4.** T2 MUST add **only** `centrality_ci: dict[str, tuple[float, float]] = {}` on `DomainResult`. Reject the proposed `centrality_ci_n_bootstrap` sibling field. The `n_bootstrap` value lives in `bootstrap_centrality_ci.n_bootstrap` (the module default) and in the DATA_DICTIONARY entry, not as a schema field.

**N5.** T2's DATA_DICTIONARY entry MUST cite (a) B = 500, (b) model-resampling-with-replacement R2 unit, (c) percentile method (2.5 / 97.5), (d) reference-vector sign alignment, (e) `>= 3` models gate, AND (f) the verbatim sentence from §Q4 acceptance criterion 4 above, naming `docs/status/2026-05-28-viz-fixes-cda-sme-verdict.md` F2 as the origin.

**N6.** T3 MUST wrap the `bootstrap_centrality_ci` call in try/except mirroring `bootstrap_term_mds_ellipses` and log distinguishable messages for the two `centrality_ci = {}` paths ("skipped: n<3" vs "failed: <exception class>: <message>").

**N7.** T5 MUST include the sign-alignment test specified in §"T5 test contract" item 5 above. Without this test, a future regression to mean-sign alignment (or to no alignment) would not be caught — and the originating bug class (register-mistaken / method-mislabeled CIs) is precisely what this entire remedy exists to prevent.

**N8.** T4 (when it returns) MUST honor the four audience-translation hooks in the T4 advisory section above. Flagging now so the Architect can pre-bind these into the T4 task spec.

---

## Routing

- Verdict file: this document.
- Slack: post summary to `#lsb-cda-sme`.
- Architect: this plan is **cleared for the Coder** once N1–N7 are folded into the T1/T2/T3/T5 task specs. T4 returns for a small follow-up SME review on label truthfulness once T3 has landed and the published `centrality_ci` data is in hand.
- The non-methodology parts of the original branch (`feature/visualization-fixes`) per Mark's branch-posture decision remain with the Reviewer agent only.

---

*End of CDA SME verdict on REMEDY-B, 2026-05-28.*
