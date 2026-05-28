# CDA SME Verdict — `feature/visualization-fixes` (dashboard viz, external AI)

**Date:** 2026-05-28
**Reviewer:** CDA SME
**Scope:** Methodology gate review of `feature/visualization-fixes`. Specific
ruling requested on the new cultural-centrality confidence-interval logic in
`apps/dashboard/src/components/CentralityChart.tsx` and the associated
`CentralityTable.tsx`.
**Diff inspected:** `/tmp/viz-fixes.diff`
**Companion ground truth:** `ARCHITECTURE.md` §1.5 / §4.2 / §4.2.0 / §4.5,
`docs/BOOTSTRAP_DESIGN.md` §1–§4, `docs/SME_REVIEW.md`, `CLAUDE.md` §7 / §9.

---

## CDA SME VERDICT: FAIL

| Axis | Verdict |
|---|---|
| Axis 1 — Protocol validity      | N/A (frontend; CDA elicitation untouched) |
| Axis 2 — Analytical validity    | **FAIL** |
| Axis 3 — Claims validity        | **FAIL** |
| Axis 4 — Audience translation   | **FAIL** |
| Register compliance             | **FAIL** |
| Vocabulary compliance           | PASS |

Verdict scope is the centrality CI logic and its UI surfaces. The other
content of the branch (provider-color tokenization, label-collision compass
solver on MDS plots, Focus 1 cell-size tweak, lens-toggle prop relocation,
PileStructure type widening, `term_mds_uncertainty` consumption) is
methodology-neutral and not gated by this verdict. The Reviewer agent still
needs to clear it on the non-methodology axes.

---

## Findings

### F1. The CI is a normal-approximation interval, labeled "bootstrap" four times. (Axis 2, Axis 4)

`apps/dashboard/src/components/CentralityChart.tsx` L120–L144 computes:

```
mean ± 1.96·(sd / sqrt(n))
```

over the values of `centrality_scores_by_run`. This is a textbook normal
(z) approximation to a mean CI, not a bootstrap interval. The project's
established uncertainty contract is a **percentile bootstrap** computed in
`packages/cdb_analyze/cdb_analyze/bootstrap.py` and surfaced as `*_ci`
fields on `WithinModelResult` / `DomainResult` (see `oci_ci`,
`similarity_ci`, `consensus_ci`, `mds_uncertainty` semi-axes — all
bootstrap-derived). Calling a normal-approximation interval "bootstrap" is a
methodologically false claim. Four surfaces carry the false label:

1. `CentralityChart.tsx` L209 (screen-reader summary):
   *"Bootstrap confidence intervals are shown as error bars on each bar."*
2. `CentralityChart.tsx` L445 (tooltip):
   *"Based on {ci.n_bootstrap} bootstrap samples"* — where `n_bootstrap` is
   just the run count, not a resample count.
3. `CentralityChart.tsx` L452 (empty-state tooltip):
   *"Bootstrap range not available"*.
4. `CentralityTable.tsx` L523 (table column header):
   *"Bootstrap N"*.

`CentralityChart.tsx` L122 and L138 and `CentralityTable.tsx` L488 also use
the *field name* `n_bootstrap` in the TypeScript record shape, which is the
seed of the labeling mistake — a normal-approx run count is not "n_bootstrap."

This violates `CLAUDE.md` §6 rule 10 / `ARCHITECTURE.md` §4.5 ("Uncertainty
display is mandatory") not by suppressing uncertainty but by **misrepresenting
its method**. A reader who knows what bootstrap means will be misled into
believing they are looking at the resample-derived intervals the rest of
the dashboard surfaces, when in fact they are looking at an N=3-typical
normal CI computed in the browser. The fact that the project's other CIs
*are* genuine bootstraps makes this confusion particularly load-bearing on
the dashboard's credibility.

### F2. The CI is computed on a Register 1 quantity and displayed as the uncertainty on a Register 2 quantity. (Axis 2, Register compliance — CRITICAL)

This is the deeper error and the one that makes the issue methodological
rather than just nomenclatural.

The chart displays `centralityScores` — i.e., `DomainResult.cultural_centrality_scores`
from `packages/cdb_analyze/cdb_analyze/pipeline.py` L765, which is
`compute_centrality_scores(model_ids, sim_np)` — the first eigenvector of
the **inter-model similarity matrix**. This is a **Register 2** (between-
model) quantity: one number per model, where the model is the informant
unit and the structure is the categorical structure across models.

The CI displayed next to this Register 2 quantity is computed in
`CentralityChart.tsx` L121–L143 from `centrality_scores_by_run` — which is
the field populated by `packages/cdb_analyze/cdb_analyze/two_level.py` L95
inside `run_within_model_analysis()`. That field is the first-eigenvector
loading on the **run × run agreement matrix for a single model** — a
**Register 1** (within-model output-concentration) quantity. The runs are
iid samples from one stochastic process; the loadings are per-run
projections onto that process's central tendency.

These are not the same quantity. They share the word "centrality" and
nothing else:

- R2 `cultural_centrality_scores[m]` answers: "how central is model *m* on
  the between-model map for this domain?"
- R1 `centrality_scores_by_run[i]` answers: "how representative is run *i*
  of model *m*'s own output distribution?"

A normal-approx CI on the per-run R1 loadings does not estimate the
sampling uncertainty of the R2 score. It estimates the dispersion of one
model's run-level loadings on *its own* within-model agreement matrix.
Plotting those bounds around a Register 2 point is a category error. It
implies a precision claim about between-model position that the underlying
computation does not support.

`docs/SME_REVIEW.md` and `docs/BOOTSTRAP_DESIGN.md` §1 are explicit about
why the two registers must be kept distinct. `BOOTSTRAP_DESIGN.md` §2
records the binding rule: **Register 1 CIs systematically underestimate
uncertainty** because the runs are not independent agents. Even putting
aside the label confusion in F1, an R1-derived CI affixed to an R2 point
inherits R1's narrow bias and additionally answers the wrong question.

### F3. n=2 minimum gates an interval that is not credible at n=2 or n=3. (Axis 2)

`CentralityChart.tsx` L128 admits any model with `values.length >= 2`.
At n=2, a normal-approximation 1.96 CI on the mean of two values is
indefensible — Student's t at n=2 has 1 df and a 95% multiplier of 12.7,
not 1.96. At n=3 (the project's minimum runs-per-model under
`run_within_model_analysis()`), t is 4.30. Using 1.96 at these N's
understates the interval by a factor of 2–6×. This compounds F1: the
interval is not only a normal approximation labeled as bootstrap; it is a
*large-sample* normal approximation applied to small-sample data.

### F4. Screen-reader copy makes the same false claim and additionally elides the register issue. (Axis 4)

L209: *"Bootstrap confidence intervals are shown as error bars on each
bar."* The screen-reader summary is precisely the surface where a
methodologically careful claim matters most — it is the only description
the non-visual user gets. The current copy fails the "credible to a
skeptical reader" bar from `CLAUDE.md` §1 because the skeptical reader can
verify (via the open-data bundle once published) that no `centrality_ci`
field exists, and that the values match a normal-approx computation on
R1 loadings.

### F5. The introduction of a divergent CI-computation pattern violates the project's "no point estimates without uncertainty" doctrine in spirit. (Axis 2)

The doctrine in `CLAUDE.md` §6 rule 10 / `ARCHITECTURE.md` §4.5 is that
no viz ships without uncertainty. The implicit corollary, evidenced by the
pipeline.py / two_level.py / bootstrap.py architecture and by the
established `*_ci` field-naming convention, is that uncertainty is
computed **once, in `cdb_analyze`, with the bootstrap module**, and
published as a `*_ci` field. The frontend consumes the field; it does
not recompute the statistic. Recomputing CIs in the browser, with a
different estimator, under a different label, fragments the uncertainty
story and makes it impossible to audit. If this pattern is allowed to
ship on centrality, the next external designer will introduce another
browser-side estimator on the next viz, and the dashboard will accumulate
a patchwork of incompatible CI semantics.

This is the same general failure mode `BOOTSTRAP_DESIGN.md` was written
to prevent.

---

## Required before merge

The merge is gated. There are two acceptable remedies. The choice
between them is Mark's, not the external designer's.

### Remedy A — Honest relabel (frontend-only, fast). NOT RECOMMENDED.

If Mark wants the visual feature to ship now and accepts that the
interval semantics will be re-stated honestly, every "bootstrap" surface
must be relabeled to describe what is actually computed. This remedy does
**not** fix F2 (the register error) and is therefore *not the preferred
remedy*. It is included only as a fallback if F2's full fix is
out-of-scope for this branch.

Under Remedy A, the following are binding:

A.1. Replace all four "bootstrap" labels (F1.1–F1.4) with language that
    does not claim the interval is bootstrap-derived. Examples (not
    prescriptive — UI/UX agent owns final copy):
    - SR L209: *"Per-run centrality dispersion is shown as error bars
       on each bar (normal-approximation interval over this model's own
       runs; see methodology page)."*
    - Tooltip L445: *"Range computed from {n} run-level centrality
       loadings (this model's own runs)"* — drop "bootstrap samples"
       entirely.
    - L452: *"Range not available"* (drop "Bootstrap").
    - Table column L523: *"Runs (N)"* — not "Bootstrap N".

A.2. Rename the TS field `n_bootstrap` to `n_runs` throughout
    `CentralityChart.tsx` and `CentralityTable.tsx`. The current name is
    the originating misnomer that propagated into the four surfaces.

A.3. The screen-reader summary and the chart's caption/aria must carry a
    sentence that distinguishes this from the dashboard's other (genuine
    bootstrap) intervals — e.g., a footnote-style note that "the error
    bars on this chart are computed differently from the other CIs on
    this dashboard; see methodology page." Without this, the inconsistency
    is invisible to a screen-reader user.

A.4. Raise the minimum from `values.length >= 2` to `values.length >= 3`
    and, ideally, use Student's t multiplier (df = n−1) instead of 1.96.
    Document the multiplier in a code comment that cites this verdict.

A.5. Add a code comment at L121 stating verbatim:
    *"This is a normal-approximation CI on per-run R1 centrality
    loadings, NOT a bootstrap CI on the R2 cultural-centrality score.
    See docs/status/2026-05-28-viz-fixes-cda-sme-verdict.md F2."*
    This is the audit trail for the next reviewer who finds this code.

A.6. **Even with A.1–A.5 applied, the register error in F2 remains.**
    Affixing an R1 interval to an R2 point is misleading regardless of
    how honestly the R1 interval is described. Remedy A's relabel makes
    the dashboard *less* false but still does not estimate the right
    quantity. If Mark accepts Remedy A, the merge must be accompanied by
    a tracked follow-up (linked from the methodology page) to replace it
    with Remedy B in a subsequent phase.

### Remedy B — Publish a real `centrality_ci` from `cdb_analyze`. RECOMMENDED.

The doctrinally correct fix follows the established pattern (`oci_ci`,
`similarity_ci`, `consensus_ci`, `mds_uncertainty`):

B.1. Add a Register 2 bootstrap on cultural-centrality scores to
    `packages/cdb_analyze/cdb_analyze/bootstrap.py`. The resample unit is
    **models** (consistent with the existing `bootstrap_mds_ellipses`
    Option 2 design in `BOOTSTRAP_DESIGN.md` §3). For each bootstrap
    iteration, resample the 12 models with replacement, rebuild the
    inter-model similarity matrix, recompute centrality, and accumulate
    per-model percentile bounds. This is the correct sampling-unit for
    the R2 quantity.

B.2. Add `centrality_ci: dict[str, tuple[float, float]]` to
    `DomainResult` in `packages/cdb_core/cdb_core/schemas.py` and update
    `docs/DATA_DICTIONARY.md` in the same PR (per Reviewer rule R7).

B.3. Wire the new field into the publish layer (`cdb_publish`) and the
    dashboard's `DomainExtended` type, replacing the browser-side
    computation. The frontend reads `domain.centrality_ci[modelId]` and
    drops the L121 `useMemo` entirely.

B.4. With B.1–B.3 in place, "Bootstrap N" / "bootstrap samples" / "Bootstrap
    confidence intervals" all become accurate, *and* the displayed
    interval estimates the right quantity. F1, F2, F3, F4, F5 are all
    resolved together.

B.5. Per `BOOTSTRAP_DESIGN.md` §3, the R2 model-resampling bootstrap is
    NOT subject to the `underestimates_uncertainty=True` annotation —
    that flag is R1-only. So the new field does not need the R1 caveat
    treatment.

Remedy B requires CDA SME PASS on the schema/pipeline addition (B.1–B.3
constitute an analytical change), which is a separate review. It is the
methodologically correct path and the one consistent with the dashboard's
existing uncertainty story.

### Remedy C — Drop the CI surface from this branch.

If neither Remedy A nor Remedy B is in scope for the external designer
right now, the third acceptable path is to **remove the CI display
entirely** from this branch and ship just the visual refresh (color
tokens, label-collision solver, cell sizing). The chart returns to
displaying the point estimate alone, marked with a small "no uncertainty
displayed — see methodology" annotation. This is, doctrinally, worse than
either A or B (it violates the no-point-estimates-without-uncertainty
rule), but it is preferable to shipping the current false claim. Remedy C
should be paired with a tracked follow-up to ship Remedy B.

### Required for any chosen remedy

R.0. The merge cannot land until **one** of A / B / C is applied. The
    branch as it stands is FAIL.

R.1. If A or C, a tracked follow-up to ship B is required (link from the
    methodology page issue tracker / from `ARCHITECTURE.md` §4.5 viz
    inventory). B is the long-term contract.

R.2. The four "Bootstrap" / "bootstrap" string literals enumerated in F1
    cannot ship under Remedy A or C without the relabeling in A.1.

---

## Vocabulary compliance

The diff carries no §1.5.4 / §7 forbidden vocabulary. "Centrality,"
"alignment with the group's dominant categorical pattern," "categorical
structure" are all on-doctrine. The L209 SR copy phrase "closer alignment
with the group's dominant categorical pattern" is fine — it does not
imply "closer to human = better" because there is no human baseline in
v1 (per §1.5.5) and the comparison is explicitly model-to-model. No
vocabulary rejection.

The "bootstrap" misnomer is not a §7 forbidden-vocabulary issue — it is a
factual misstatement about what the underlying statistic is. It is gated
under Axis 2 (analytical validity), not under the vocabulary rule. The
vocabulary rule is about how LSB talks about its subjects (models); this
finding is about how LSB describes its own statistics.

---

## Routing

- Verdict file: this document.
- Slack: post summary to `#lsb-cda-sme`.
- Architect: route this verdict to the external designer (or to the
  internal team taking over the branch) with the Remedy A / B / C
  choice flagged for Mark.
- The non-methodology parts of the branch (label-collision solver, color
  tokenization, Focus 1 cell-size tweak, lens prop relocation) are not
  gated by this verdict and pass to the Reviewer agent on the standard
  non-methodology axes.

---

*End of CDA SME verdict, 2026-05-28.*
