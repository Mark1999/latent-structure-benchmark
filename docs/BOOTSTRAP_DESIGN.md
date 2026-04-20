# Bootstrap design note

**Status:** Binding for any PR that changes `packages/cdb_analyze/cdb_analyze/bootstrap.py` or adds bootstrap calls anywhere in `cdb_analyze`.
**Prepared:** 2026-04-19 (post-F1 SME review)
**Companion docs:** `ARCHITECTURE.md` §4.2 (analysis layer + three analytical registers), §4.2.6 (existing bootstrap module), `docs/SME_REVIEW.md` (Option 2 annotated-uncertainty recommendation), `docs/briefings/2026-04-19-sme-brief.md`

---

## 0. What this note exists to prevent

The two-level design introduced post-F1 (Register 1 within-model output concentration + Register 2 between-model cultural consensus analysis) makes it easy to double-count uncertainty, or to quietly lose run-level variance when Level 2 takes Level 1 aggregates as input. This note specifies exactly what is resampled at each register, what variance is captured vs lost, and how uncertainty is communicated on the dashboard.

When something is ambiguous, the rule is **claim less precision, not more**.

---

## 1. The three registers, mapped to variance sources

| Register | What varies | Natural uncertainty source | Current bootstrap scope |
|---|---|---|---|
| **R1a** — sampling concentration (OCI) | N temperature-sampled runs at fixed prompt for one model | Stochastic decoding variance within one model's output distribution | *Not yet implemented* — added in PR #6 |
| **R1b** — prompt robustness (G1 diagnostics) | 8+ prompt variants at fixed model | Prompt-sensitivity variance within one model | Aggregated into G1 scalar; per-variant resampling not done |
| **R2** — cultural consensus analysis (between-model) | 12 models as informants, each contributing one voice via R1a consensus | Inter-model structural variance + residual within-model variance propagated in | Current `bootstrap_mds_ellipses()` — resamples N runs per model with replacement, rebuilds co-occurrence + similarity + MDS, fits ellipses |
| **R3** — longitudinal drift (Procrustes) | Model versions over time | Version-to-version structural change | CI from bootstrap on both endpoints independently; no new machinery |

Observation: the current bootstrap is a **Register 2 bootstrap** that also happens to pick up run-level variance along the way. That is the right behavior for v1; the question is whether Register 1 (once introduced in PR #6) adds its own bootstrap, and how.

---

## 2. The Level 1 underestimation caveat

This is the most important thing in this note, and it must be stated plainly in the methods page and in any generated text that displays a Register 1 ellipse:

> **An N-run Register 1 bootstrap underestimates uncertainty.**
>
> The N runs resampled with replacement are iid draws from a single stochastic process (the model at fixed weights, fixed temperature, fixed prompt). Their effective sample size is smaller than N independent agents because the draws are correlated through a shared mean. Bootstrap CIs computed on the agreement matrix, on the OCI, or on the within-model MDS will be tighter than they would be under truly independent sampling. The bias is systematic and in the narrow direction.
>
> This is not a bug; it is a consequence of what Register 1 measures (output concentration of one stochastic process, not consensus among distinct agents). The caveat must accompany every Register 1 CI in the methods page, the dashboard tooltip, and the open data bundle's data dictionary.

Concretely: when PR #6 adds Register 1 bootstrap, the returned object carries a boolean `underestimates_uncertainty: True` flag, and the dashboard's Register 1 panel displays "within-model CI; see methods page note on underestimation" next to the ellipse. The flag is set `False` only at Register 2 and Register 3 where the informants (models) are meaningfully distinct.

---

## 3. Option 2 — annotated uncertainty (v1 implementation)

The SME review considered two options for propagating run-level variance into Register 2:

- **Option 1 — Nested bootstrap.** Level 2 bootstrap resamples the Level 1 raw runs for each model, re-derives the Level 1 consensus, then proceeds to Level 2. Propagates run-level variance correctly. **Rejected for v1:** multiplies compute by ~N_runs per model. At B=500 × N=20 × 12 models = 120,000 pipeline runs per domain. Not feasible within the Phase 4b budget envelope.
- **Option 2 — Annotated uncertainty.** Level 2 CIs are computed from **model-level resampling only** (12 models, B=500). Each model's contribution to the Level 2 MDS point is annotated with its OCI and its Level 1 CI width. The dashboard displays — not equal ellipses for all models — but the Register 2 point plus a visible reliability signal from Register 1. **Adopted for v1.**

### 3.1 What Option 2 captures

- **Between-model structural variance at B=500.** The 12 models are resampled with replacement (the same model can be drawn multiple times across bootstrap iterations); the resulting similarity matrix is recomputed per iteration; MDS coordinates are Procrustes-aligned to the reference and an ellipse is fit from their covariance.
- **Model-level structural uncertainty.** If dropping or duplicating certain models substantially changes the MDS, those models are load-bearing on the map; this shows up in wider ellipses on the reference map.
- **OCI annotation on each model marker.** A low-OCI model gets no confidence ellipse on the Register 2 map (it gets a different visual treatment — see §4); its position is shown but annotated as uncertain at Level 1.

### 3.2 What Option 2 loses

- **Per-run within-model variance does not propagate into Register 2 CI width.** If a specific model's N=20 runs are highly variable (low OCI), Register 2 still uses its pooled consensus with equal weight to a high-OCI model. The uncertainty from that model's instability is surfaced *alongside* the map, not baked into the ellipse.
- **Upstream structural changes.** A bootstrap that happened to draw a bad split (e.g., all 20 runs of model X came from the tail of the distribution) is not penalized.

This is a genuine limitation. The mitigation is *visibility, not precision*: readers see the OCI next to each model and can reason about which positions to trust.

---

## 4. Dashboard communication (handoff to UI/UX agent)

The following decisions are for the UI/UX agent to implement against `DESIGN_SYSTEM.md` when the Register 1 / Register 2 panels are built. Listed here so they are not lost:

1. **Register 1 panel.** Always show ellipse + explicit "within-model CI — see methods page note" hover/footnote. Never show Register 1 ellipse without the caveat.
2. **Register 2 map, high-OCI model.** Standard ellipse from the model-level bootstrap.
3. **Register 2 map, low-OCI model** (OCI below the threshold set in the schema PR — SME proposal is OCI < 3.0 on the concentration scale; final cutoff TBD in PR #6 saturation analysis):
   - **Do not render a confidence ellipse** on the Register 2 map for this model.
   - Render the point with a distinct visual marker (e.g., dashed outline or reduced opacity per `DESIGN_SYSTEM.md` §3.3).
   - Tooltip shows: "position uncertain (OCI = X.X); see model profile for within-model distribution."
4. **OCI legend.** Every Register 2 plot carries a discreet OCI scale/key so readers can map marker weight to concentration without clicking through.
5. **Per-model profile page.** The full Register 1 view (within-model MDS with ellipse + underestimation caveat) is reached from any Register 2 point by clicking the model marker.

Rule: a reader should never see a Register 2 ellipse that implies more precision than the contributing model's Register 1 stability warrants.

---

## 5. Register 3 (longitudinal drift) bootstrap

No new machinery. Procrustes drift is computed between two endpoints (version A at time t₁, version B at time t₂), each of which already has its own Register 2 bootstrap ellipse. The drift CI is computed analytically from the two endpoint covariance matrices; no nested bootstrap of versions, because versions are not a random sample from a distribution — they are specific dated artifacts.

When `drift.py` is exercised in Phase 6+ across more than two endpoints, the note revisits this. For v1 (first real drift analysis post-Phase 4), two endpoints are the expected use case.

---

## 6. Deferred to Phase 2

- **Nested bootstrap (Option 1).** Recompute compute budget once operational N is set by the Phase 4b saturation analysis. If per-run compute drops enough that 120,000 pipeline runs per domain becomes plausible within the monthly spend cap, adopt Option 1 as the primary uncertainty story and retire Option 2's annotation dance. Until then, Option 2 is the contract.
- **Variance-inflation correction on Register 1 CIs.** Instead of flagging underestimation, compute an effective-sample-size correction (e.g., a design-effect analog) and inflate the bootstrap CI analytically. Requires empirical calibration against the saturation analysis data. Phase 2.
- **Register-1-aware Register 2 weighting.** Option C from the SME review (OCI-weighted between-model analysis) was rejected as primary. A future Phase 2 decision could revisit using OCI as a *diagnostic weight* in a sensitivity analysis only — never as the primary map. Document the reasoning here at that time.

---

## 7. Open questions flagged for SME review

Per the standing decision rule ("if a new variance-propagation question arises not covered by Option 2, choose the more conservative option and flag"):

- **Saturation analysis (Phase 4b, PR #6) interaction.** The saturation curves will give us operational N per domain. Whether the Register 1 bootstrap should use that N or something smaller (to reduce compute further) is an open question. Default for v1: use operational N.
- **Multi-baseline grounding with raw subject data.** When a researcher submission includes `pile_sort_raw.csv`, the baseline can be analyzed at Register 1 (human OCI, per §4.2.5). Do we bootstrap subjects with replacement at Level 1? Default for v1: yes, treating human subjects as the analog of runs — and carrying an *under*estimation caveat in the opposite direction: if the human subject pool is a purposive or convenience sample from one community, the CI does not reflect cross-population variance.
- **Is OCI < 3.0 the right cutoff for "hide the Register 2 ellipse"?** Decision deferred to the Phase 4b saturation analysis. Until then, any Register 2 ellipse rendering decision is provisional.

  **Coordination commitment (per CDA SME review of PR A, 2026-04-20, recommendation R3).** When the Phase 4b saturation analysis finalizes the R1-a / R1-b OCI cutoff, the update ships as **one coordinated PR** that simultaneously touches:
    1. the TS config constant `OCI_LOW_CONCENTRATION_THRESHOLD` at `apps/dashboard/src/config/analysis.ts`,
    2. any schema-level threshold reference in `packages/cdb_core/cdb_core/schemas.py` or `packages/cdb_analyze/`,
    3. the methodology-page prose that names the threshold,
    4. `DESIGN_SYSTEM.md` §3.3.5 if the provisional-value text changes.

  Partial updates are a foreseeable source of drift and must not ship in separate PRs. The Reviewer agent rejects any PR that touches one of the four surfaces above without touching the others.

---

## 8. Summary — the contract for PR #6

When PR #6 implements the two-level pipeline:

- Register 1 bootstrap exists, returns an `underestimates_uncertainty: True` annotated result, and the methods page carries the §2 caveat.
- Register 2 bootstrap is unchanged in structure (Option 2): resamples models with replacement, produces the MDS map, fits ellipses.
- Level 2 output carries, for each model, the OCI and Level 1 CI width as metadata; the dashboard uses those to decide whether to render a Register 2 ellipse on that model.
- Nothing claims "full uncertainty propagation." The docs, the methods page, and the open data bundle's data dictionary all state plainly that within-model variance is visualized alongside (not within) Register 2 CIs.

*End of design note. Update this document before any change that broadens what the bootstrap claims to do.*
