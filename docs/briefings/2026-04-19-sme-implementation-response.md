# LSB — implementation response to the external SME review

**Addressed to:** External SME (cognitive / quantitative / cultural anthropology)
**From:** Claude Code, working with Mark
**Date:** 2026-04-19
**Companion docs:** `docs/SME_REVIEW.md` (your authoritative review), `docs/BOOTSTRAP_DESIGN.md`, `docs/briefings/2026-04-19-sme-brief.md`, `ARCHITECTURE.md` §1.5.5, §4.2.0, §4.2.7, §5.3 Phase 4b

---

## 0. What this document is

A compact summary of what's been implemented in response to your review, what's been deferred by mutual agreement, and what open questions need your next-cycle attention. Six PRs are pushed; none are merged yet pending final review. The commits are deterministic, all check suites pass, and nothing ships without your sign-off.

---

## 1. Accepted and implemented (six PRs)

### PR #1 — Framing reversal + three analytical registers *(docs)*

The framing reversal is accepted in full and is now the operating position of the project:

- Human baselines are **contextual reference points, not the target of measurement**.
- The primary scientific claim is comparative across model architectures and across time.
- `ARCHITECTURE.md` §1.5.5 has been rewritten from "human consensus is the ceiling" to the revised floor/ceiling language with cross-architecture comparison as the primary axis.
- The "mismatch is the finding" framing is now a binding rule for the public methods page's lead paragraph (§1.5.6).
- The four-layer corpus-lens breakdown is written out in §1.5.1 so readers know LSB observes only Layer 4 (temperature-sampled token generation) and that claims about Layers 1–3 are inferential.
- `ARCHITECTURE.md` §4.2.0 adds the three-register section verbatim per your exact wording, with human grounding slotted into Register 2 as a reference informant and with the R1a/R1b split.
- The methods adaptation table is embedded in §4.2.0 (and copy-destined for the public methods page).
- `ARCHITECTURE.md` §5.3 Phase 4b adds the runbook note: **G1 failure in the 0.4–0.6 borderline range triggers prompt-variant expansion before domain disqualification.**
- Forbidden vocabulary expanded: "within-model consensus," "within-model cultural consensus," "within-model eigenratio," "within-model CCM" are now rejected by the Reviewer. The canonical name for the Register 1 measure is **Output Concentration Index (OCI)**.

### PR #2 — G3 uses Adjusted Rand Index as binding metric *(code)*

- `gates.py:g3_replication` now uses `sklearn.metrics.adjusted_rand_score` with threshold **ARI ≥ 0.6** as the binding pass/fail.
- The unadjusted Rand index is still computed per trial and reported in `GateResult.secondary_metrics["median_rand_index"]` for cross-study comparability.
- `ConsensusType` Literal declared with all six values (`STRONG_CONSENSUS`, `WEAK_CONSENSUS`, `SUBCULTURAL`, `TURBULENT`, `CONTESTED`, `DETERMINISTIC`). `DETERMINISTIC` is reserved for future architectures; does not trigger on any current model.
- No new dependencies; sklearn ≥ 1.4.0 already present.

### PR #3 — Bootstrap design note *(docs)*

`docs/BOOTSTRAP_DESIGN.md` specifies the Option 2 (annotated uncertainty) contract you recommended:

- **Level 1 underestimation caveat** is stated in the binding `underestimates_uncertainty=True` flag on every `WithinModelResult` and in the methods page requirement. An N-run within-model bootstrap resamples iid draws from one stochastic process; effective sample size is below N; CIs are systematically narrow. The caveat accompanies every Register 1 ellipse on the dashboard and every R1 CI in the open data bundle.
- **Level 2 CIs are from model-level resampling only** (12 models, B=500). Each model's Register 2 point carries OCI + Level 1 CI width as metadata so the dashboard can decide whether to render a Register 2 ellipse on that model. Low-OCI models get the point but no ellipse; their uncertainty is surfaced alongside the map, not baked into it.
- **Nested bootstrap (Option 1) deferred to Phase 2** with the compute arithmetic stated explicitly so the deferral has a clear reason to revisit.
- **Register 3 (drift)** uses analytic combination of Register 2 endpoint covariances, not a nested bootstrap — versions are dated artifacts, not random samples.
- Handoff to the UI/UX agent specifies the dashboard rule: a reader should never see a Register 2 ellipse that implies more precision than the contributing model's Register 1 stability warrants.

### PR #4 — DomainResult + GroundingRef schema additions *(code + docs)*

`cdb_core/schemas.py` and `docs/DATA_DICTIONARY.md` updated in the same commit (Reviewer rule 5 satisfied). New types and fields:

- **Dual Romney threshold** fields: `romney_eigenratio`, `romney_threshold_classic` (3.0), `romney_threshold_lsb` (5.0), `romney_consensus_pass`, `romney_consensus_warning`.
- **Cultural centrality** per model: `cultural_centrality_scores: dict[str, float]` with negative-score flagging. Per your Q4 resolution, centrality is computed at the **model level** using the pooled inter-model similarity matrix; no per-run restructuring.
- **`compute_centrality_scores`** and **`classify_consensus`** functions in `consensus.py`. Labeled "cultural centrality" not "competence" per Caulkins 1999.
- **`ConsensusType`** canonicalized in `cdb_core` to avoid circular imports. Classification uses the full six-state table from SME §1.6 plus the DETERMINISTIC variance override.
- **Sutrop CSI** (SME §2.1) implemented in `cdb_analyze/salience.py` from the Sutrop 2001 formula; `compute_salience_agreement` reports Spearman ρ vs Smith's S (< 0.85 warning).
- **Nolan Index** (SME §2.2, Robbins 2023) implemented in `cdb_analyze/diff.py` with the "same items, different weights" diagnostic against Jaccard.
- **Mantel test** (SME §1.2, Mantel 1967) implemented in `cdb_analyze/diff.py` as a parallel pairwise measure alongside the existing G2 dispersion-permutation test. Per your Q5 resolution: the G2 gate is unchanged (tests the full inter-model structure); Mantel is added as a separately reported pairwise measure useful for the dashboard comparison table. The current G2 measure has been clarified as an "inter-model similarity dispersion permutation test" to avoid confusion with classical Mantel.
- **`WithinModelResult`** nested block for Register 1 outputs (OCI, per-run centrality, centroid run id, bootstrap CI, `underestimates_uncertainty` flag).
- **`GroundingRef.human_oci`** / `human_oci_ci` / `n_subjects_with_raw_data`. Populated only when a baseline ships with `pile_sort_raw.csv` per SME recommendation; enables "this model's OCI is within the range observed across human subject pools" cross-species claim.

22 new tests in `tests/unit/test_sme_measures.py` covering every new function including the "same items, different weights" NI case and all six `classify_consensus` paths.

### PR #5 — InformantRecord capacity-constrained truncation *(code + docs)*

Per SME §1.7:

- `truncation_type` Literal: `elbow` | `capacity` | `prompt_ceiling` | `context_window_exceeded`.
- `truncation_n`, `max_possible_n`, `context_window_exceeded`, `capacity_note`.
- **Binding semantics: `context_window_exceeded=True` is a finding, not a QA failure.** The schema does not couple it to `qa_passed`; the QA_Runner's six deterministic checks do not gate on it. The `DATA_DICTIONARY.md` QA subsection states this explicitly. Five tests cover the compose-with-qa-passed path, invalid-Literal rejection, and the defaults-unchanged contract.

### PR #6 — Two-level pipeline + saturation analysis *(code)*

`cdb_analyze/two_level.py` and `saturation.py`:

- `run_within_model_analysis(records)` → `WithinModelResult` with OCI, per-run centrality, centroid run id, optional bootstrap OCI CI, `underestimates_uncertainty=True` always.
- `options_for_level_two(records)` returns the three representations per your Q2 resolution: **Option A** pooled consensus free list (primary Level 2 input, equal voice), **Option B** centroid run id (dashboard display only), **Option C** OCI as diagnostic weight (never an alternative map).
- `saturation_curve(records, n_values)` sweeps N and reports OCI, elbow position, Smith-vs-Sutrop Spearman ρ, and top-K Jaccard overlap between successive N values. `identify_knee(curve)` returns `knee × 1.20` safety margin when the top-K Jaccard threshold is met; `None` when the sweep range does not contain saturation (a finding, expand the sweep).
- Reference configuration per your standing authority: `SATURATION_REFERENCE_MODELS = ("claude-opus-4-6", "gpt-4o", "llama-3.1-70b")`, `SATURATION_REFERENCE_DOMAINS = ("family", "holidays")`. Integrates into the Phase 4b prompt-sensitivity study budget envelope; findings are surfaced on the public methodology page as a named methods contribution — **not** framed as publishable per §1.5.6.
- 21 new tests covering the stable-vs-variable OCI gradient, the underestimation invariant, all three Level-2 options, the saturation sweep with knee detection, and the "never saturates" path.

---

## 2. Deferred by mutual agreement (Phase 2 or later)

- **G1 split** (your §1.3, salience vs spatial stability). Logical follow-up refactor to `sensitivity.py`; not included in the six-PR sequence to keep it bounded. We'll come back to this before Phase 4b runs.
- **Pile-label consistency** (your §2.3, no-embeddings AI-free implementation). Defers alongside the full label-parsing pipeline.
- **No-ceiling free-list experiment** (your §3.1). Requires additional API spend; needs to be costed against the monthly cap and the B2 backup layer being active per the 2026-04-19 incident note. Runs as a parallel methods-validation study, not on the critical path.
- **16+ prompt variants** (your §5.3). Revisit when we have Phase 4b results; the 8-variant default is the starting point.
- **INDSCAL and RCA/CCA** — explicitly Phase 2 per your review.
- **Nested bootstrap (Option 1)** for Level 2 variance propagation. Deferred on compute-cost grounds (~120,000 pipeline runs per domain at B=500 × N=20 × 12 models). `BOOTSTRAP_DESIGN.md` §6 commits to revisiting when the operational N from the saturation analysis makes the arithmetic feasible.

---

## 3. Open questions flagged for your next cycle

Listed in priority order. Each has a current provisional answer and a reason we want your confirmation.

1. **Low-OCI ellipse-suppression cutoff.** Current provisional threshold: OCI < 3.0 on the concentration scale (models below this get their Register 2 point rendered without a confidence ellipse, just an annotation). Final value wants the saturation-analysis data before it's fixed. Your input welcome on whether 3.0 is the right cutoff and what the visual treatment should look like below it.

2. **Saturation-N interaction with compute budget.** The saturation curves will give us operational N per domain. Once known, should the Register 1 bootstrap use that N or a smaller N to reduce compute? Default position is "use operational N." Is that the right call, or should we propagate uncertainty more aggressively at the expense of computation?

3. **Human-OCI bootstrap treatment.** For researcher submissions that include per-subject raw pile-sort data, the current plan is to bootstrap subjects with replacement at Register 1 — but a purposive or convenience sample from one community carries the **opposite**-direction underestimation caveat from the model case (too narrow because the CI doesn't reflect cross-population variance). We've written this into `BOOTSTRAP_DESIGN.md` §7 as a known limitation. Is there a correction you'd recommend applying, or is "annotate and move on" the right call?

4. **G2 semantics renamed, not replaced.** Per your Q5 resolution we kept the G2 dispersion-permutation test unchanged as the binding gate and added Mantel alongside as a pairwise measure. We renamed the G2 measure in docstrings to "inter-model similarity dispersion permutation test" to avoid confusion with classical Mantel. Please confirm that this rename is the right level of disambiguation (vs. a more substantive restructuring of G2).

5. **"Mismatch is the finding" on the methods page.** We've made it a binding rule that this framing leads the public methods page (not buried in a limitations section). When you review the methods-page draft (Phase 5/6), please verify that our first paragraph actually delivers what the framing promises — we're most at risk of underselling the intellectual contribution here.

---

## 4. What's changed about how LSB talks about itself

The forbidden-vocabulary discipline has expanded. Both the Reviewer agent and the `ARCHITECTURE.md` §1.5.4 table now guard the Register 1 vs Register 2 boundary. In particular:

- **Never** "within-model consensus," "within-model cultural consensus," "within-model eigenratio," "within-model CCM." The Register 1 measure is the **Output Concentration Index (OCI)**. The measure is real and useful; the naming is what carries the methodological commitment that RWB assumptions do not hold at Register 1.
- Published aggregate grounding baselines are rendered without an MDS ellipse and labeled "published aggregate, uncertainty unavailable" — no pretending we have precision we don't have.
- Low-OCI models on the Register 2 map carry a tooltip that says "position uncertain (OCI = X.X); see model profile for within-model distribution" rather than a silently narrow ellipse.

---

## 5. Merge ordering and what the user sees next

User is reviewing the six PRs and will merge. The constraints are:

- **Merge PR #4 before PR #6** (schema dependency on `WithinModelResult`).
- **PR #2 and PR #4 both declare `ConsensusType`** — PR #4 canonical in `cdb_core`, PR #2 local in `gates.py`. Small follow-up after both merge to consolidate to single source of truth.
- **PR #1 and PR #6 both edit `ARCHITECTURE.md`** but non-overlapping sections. Forward references from PR #1's §4.2.0 and §5.3 to §4.2.7 resolve once PR #6 also merges.

All six check suites pass on every branch: 307 unit tests, ruff clean, mypy clean, no-LLM-imports static check clean.

No PR touches `cdb_analyze/` in a way that would violate the "no LLM calls in analysis" boundary. All new functionality is pure deterministic Python.

---

## 6. What we didn't do and why

- **No actual data collection.** The saturation analysis scaffolding is in place; the runner awaits real data. Per the 2026-04-19 test-data-loss incident note, no official collection run begins until at least one off-host backup layer is active and test-restored. That's unblocked by infrastructure work, not methodological review.
- **No methodology page draft.** Phase 5/6. The framing rules you've approved (§1.5.5, §4.2.0, §1.5.6 binding lead-paragraph rule) will govern that draft when it comes.
- **No dashboard visual changes.** All the UI/UX decisions from PR #3 (low-OCI ellipse suppression, OCI annotation legends, Register 1 caveat display) are handed off to the UI/UX agent for the Phase 5/6 dashboard build. Not this review cycle.

---

*End of implementation response. Ready for your review or next-cycle direction.*
