# CDA SME Verdict — Remedy B T4 (frontend consumption of published `centrality_ci`)

**Date:** 2026-05-28
**Reviewer:** CDA SME
**Subject:** Remedy B T4 — frontend changes (commit `9cfa677`) consuming the real published `centrality_ci` field
**Files reviewed:**
- `apps/dashboard/src/components/CentralityChart.tsx`
- `apps/dashboard/src/components/CentralityTable.tsx`
- `apps/dashboard/src/components/ContentArea.tsx` (consumption site)
- `apps/dashboard/src/data/types.ts` (DomainResultPublished field addition)
- Published data spot-check: `apps/dashboard/public/data/family.json` `centrality_ci` block
**Originating verdicts in this chain:**
- `docs/status/2026-05-28-viz-fixes-cda-sme-verdict.md` (originating FAIL; F1–F5 enumerated)
- `docs/status/2026-05-28-remedy-b-cda-sme-verdict.md` (T1+T2+T3 PASS-WITH-NOTES; N1–N7 binding + N8 advisory hooks for this T4 review)
**Companion ground truth:** `ARCHITECTURE.md` §1.5 / §4.2 / §4.5, `CLAUDE.md` §6 rule 10 / §7 / §9 pitfall 8, `BOOTSTRAP_DESIGN.md` §3.

---

## CDA SME VERDICT: PASS-WITH-NOTES

| Axis | Verdict |
|---|---|
| Axis 1 — Protocol validity      | N/A (frontend display; CDA elicitation untouched) |
| Axis 2 — Analytical validity    | **PASS** |
| Axis 3 — Claims validity        | **PASS** |
| Axis 4 — Audience translation   | **PASS-WITH-NOTES** |
| Register compliance             | **PASS** |
| Vocabulary compliance           | **PASS** |

T4 closes the centrality-CI remediation. The browser-side `mean ± 1.96·SE` interval mislabeled "bootstrap" is gone; the chart now consumes the genuine R2 model-resampling percentile bootstrap (`B=500`) that the T1+T2+T3 bundle published. Register is correct, copy is truthful, the cross-method footnote was correctly omitted, and the empty-state is handled honestly. Findings F1–F5 of the originating FAIL are fully closed by the T1+T2+T3+T3b+T4 sequence. The PASS-WITH-NOTES is for three small audience-translation refinements (M1–M3 below); none block merge but each should be applied before this surface is treated as the canonical reference for future R2-CI charts.

---

## Review against the four T4 advisory hooks from the Remedy B verdict

### Hook 1 — Truthful "bootstrap" labeling. PASS.

The four "bootstrap" label sites enumerated in F1 of the originating verdict have been replaced. The new strings are:

- SR summary (with CI), `CentralityChart.tsx` L156: *"95% bootstrap confidence intervals (model-resampling, B=500) are shown as whiskers on each bar."*
- SR summary (empty), `CentralityChart.tsx` L157: *"No bootstrap confidence interval is available for this domain (fewer than 3 models)."*
- Tooltip CI label, `CentralityChart.tsx` L341–L346: *"95% bootstrap CI: [lo, hi] (model-resampled, B=500)."*
- SVG region aria-label, `CentralityChart.tsx` L256: per-bar `${label}: ${scoreLabel}` where `scoreLabel` interpolates `[lo–hi]` from the published tuple.
- Table caption (with CI), `CentralityTable.tsx` L47–L49: *"95% CI columns show bootstrap confidence intervals (model-resampling with replacement, B=500, percentile method)."*

Every "bootstrap" used here now refers to a real percentile bootstrap. The "model-resampling" qualifier is accurate to the R2 contract (`bootstrap_centrality_ci` at `packages/cdb_analyze/cdb_analyze/bootstrap.py` L180; resample unit confirmed at L184 default `n_bootstrap=500` and sign-alignment per L199). The B=500 number matches both the function default and the call site in `pipeline.py` L786.

The table caption is the most rigorous of the surfaces (it cites resampling-with-replacement and percentile method explicitly) and is the right floor for any future R2-CI table caption on the dashboard.

### Hook 2 — No cross-method footnote. PASS.

Confirmed absent in `CentralityChart.tsx`, `CentralityTable.tsx`, and the `ContentArea.tsx` centrality block (L304–L320). The cross-method footnote was a Remedy A artifact required because that remedy's CI used a different statistical method from the rest of the dashboard's CIs; Remedy B's CI shares method with `oci_ci`, `similarity_ci`, `consensus_ci`, so no footnote is required. T4 correctly omits it. (T4 may optionally add a methodology-page link from the centrality block; that's an audience-translation choice for the UI/UX agent, not a methodology requirement.)

### Hook 3 — Honest empty-state handling. PASS.

`hasCi = Boolean(centralityCi && Object.keys(centralityCi).length > 0)` (`CentralityChart.tsx` L86; `CentralityTable.tsx` L44) cleanly distinguishes "CI present" from "CI absent" and the absent path uses the named copy *"No bootstrap confidence interval is available for this domain (fewer than 3 models)"*. The chart does not silently fall back to any other CI source when `centrality_ci` is empty (the loX/hiX whisker block at `CentralityChart.tsx` L260–L291 is guarded by `loX !== null && hiX !== null` and the `ci` field is `null` when not present in the published dict). The table similarly drops the CI columns (`hasCi && (...)` guards at `CentralityTable.tsx` L61–L66 and L84–L93) and uses `—` for the rare per-model empty cell.

This satisfies the §4.5 "no point estimate without uncertainty" rule honestly: when uncertainty is not available because the regime is degenerate, the absence is named in the SR summary and the chart does not pretend otherwise. (Note: at the current v1 corpus, all production domains have n=12, so this branch fires only in fixture tests and forward-compat scenarios. The branch is nonetheless wired correctly.)

### Hook 4 — No fabricated per-model "n bootstrap samples." PASS.

The published shape is `dict[str, tuple[float, float]]` (verified in `apps/dashboard/public/data/family.json` L26670 onward: bare `[lo, hi]` arrays, no per-model siblings). The TS type at `apps/dashboard/src/data/types.ts` L262 matches: `centrality_ci?: Record<string, [number, number]>`. No per-model `Bootstrap N` column appears in `CentralityTable.tsx`. B=500 is stated as a domain-wide quantity in both the SR summary and the table caption, which is the truthful framing — the bootstrap was run B=500 times against the whole inter-model similarity matrix; there is no per-model B value to display.

The deletion of the originating TypeScript `n_bootstrap` field on the legacy centrality-CI record is complete: `grep -n "centralityCis\|centrality_scores_by_run\|1\.96"` on `apps/dashboard/src/components/` produces no matches. The two `centrality_scores_by_run` hits in `apps/dashboard/src/data/types.ts` L63 and L172 are R1 within-model surfaces (`WithinModelResult` and `Focus1ModelData`) and are not consumed by `CentralityChart` or `CentralityTable`. The original register confusion cannot reintroduce itself via the chart's data flow because the chart's `centralityCi` prop is sourced from `domain.centrality_ci` only (`ContentArea.tsx` L313), which is the R2 published field.

---

## Register correctness — PASS

The displayed CI is the R2 inter-model quantity throughout:

1. **Data source.** `ContentArea.tsx` L313 passes `domain.centrality_ci` to `CentralityChart`. `domain.centrality_ci` is the published-field output of `bootstrap_centrality_ci(model_ids, sim_np, n_bootstrap=500, random_state=42)` (`pipeline.py` L786), which resamples models with replacement on the inter-model similarity matrix and applies reference-vector sign alignment (N1 of the Remedy B verdict). That is, by definition, an R2 quantity.
2. **No R1 contamination path.** The chart does not import or read `centrality_scores_by_run`, `within_model` data, or any R1 field. The `Focus1*` components that *do* consume `centrality_scores_by_run` are routed through separate viz tabs (`f1-self-consistency`, `f1-run-distribution`, `f1-term-stability`) and never reach `CentralityChart`. There is no code path by which the chart could re-derive a CI from R1 run-level data.
3. **No client-side recomputation.** `CentralityChart.tsx` L1–L7 docstring explicitly states "No client-side CI computation is performed." Confirmed: the `useMemo` blocks at L89–L99 (entries) and L106–L120 (x-domain) only read `ci` from the prop and use it for plotting; no statistical computation occurs.
4. **No `1.96`, no normal approximation, no SE.** `grep "1\.96"` on `apps/dashboard/src` returns zero matches. The originating bug class cannot reappear via copy-paste from the deleted code.

The register confusion that produced the originating FAIL cannot reintroduce itself through this chart's data flow as currently wired. PASS.

---

## Vocabulary compliance — PASS

`§1.5.4` forbidden-vocabulary scan on the new T4 strings (CentralityChart SR summary, CentralityChart tooltip, CentralityTable caption, ContentArea centrality block lede at L306–L310):

- "believes" / "thinks" / "worldview" — absent.
- "Models see the world" / "model's worldview" — absent.
- "cultural bias" (standalone) — absent.
- "What the model understands" / "what the model believes" — absent.
- "within-model consensus" / "within-model CCM" — absent.

Surfaces use *"closer alignment with the group's dominant categorical pattern"* (SR summary), *"how typical each model's categorical structure is relative to the group"* (ContentArea L306–L308), *"more similar categorical structures"* (similarity block L324–L327). "Categorical structure" and "categorical pattern" are the doctrinal terms per `ARCHITECTURE.md` §1.5.4 and `CLAUDE.md` §7. PASS.

The phrase "Cultural Centrality" (capitalized, in the tooltip at `CentralityChart.tsx` L337) and "cultural centrality" (lowercase in the SR summary and ContentArea lede) is the on-doctrine label for the named statistic from `compute_centrality_scores`; this is not forbidden vocabulary, it is the published-field name surfaced to the audience.

---

## Audience-translation notes (PASS-WITH-NOTES, non-blocking)

These three notes are refinements to the audience-facing copy. None of them affect register, method labeling, or methodological truth; each can land as a one-line edit in a follow-up commit. M1 is the most consequential because it touches the SR summary that screen-reader users will hear verbatim; M2 and M3 are smaller.

### M1 (advisory) — The SR-summary CI sentence is structurally separated from the ranking sentence, and screen-reader users will hear them as two unrelated facts.

`CentralityChart.tsx` L155–L158 concatenates `srSummary` from a ranking sentence (highest / lowest) and a CI sentence (`ciDesc`). The CI sentence currently begins *"95% bootstrap confidence intervals (model-resampling, B=500) are shown as whiskers on each bar."* — but it is appended directly after *"…and Y has the lowest at 0.123."* with only a period and space between. A screen-reader reading the summary will hear the two as disconnected, and the connection between "the scores you just heard" and "the bootstrap uncertainty on those scores" is not explicit. Recommend rephrasing the CI sentence to bind it to the preceding ranking, e.g., *"Each score is shown with a 95% bootstrap confidence interval (model-resampling with replacement, B=500) as a whisker on its bar."* — making the per-bar binding explicit and matching the table caption's phrasing precision (the table caption already uses "with replacement").

This is non-blocking because the current copy is methodologically truthful; the refinement is a screen-reader clarity improvement.

### M2 (advisory) — The tooltip CI parenthetical *"(model-resampled, B=500)"* would be clearer as *"(model-resampling with replacement, B=500)"* to match the table caption.

`CentralityChart.tsx` L346 uses the short form *"(model-resampled, B=500)"* while `CentralityTable.tsx` L47–L48 uses *"(model-resampling with replacement, B=500, percentile method)"*. The longer form is the more rigorous; the tooltip's shorter form omits "with replacement," which is methodologically load-bearing (R2 bootstrap = informant resampling *with replacement*, per `BOOTSTRAP_DESIGN.md` §3.1). Recommend bringing the tooltip into alignment with the table caption: *"95% bootstrap CI: [lo, hi] (model-resampling with replacement, B=500)."*

This is non-blocking because the tooltip's audience is on-screen viewers who have visual access to the full chart context; the SR summary and table caption (which carry the rigorous form) are what auditing readers will quote.

### M3 (advisory) — Consider routing the centrality block to a methodology-page anchor.

`ContentArea.tsx` L304–L320 describes cultural centrality in lay terms ("how typical each model's categorical structure is relative to the group") but does not link to the methodology page where the bootstrap method and the n>=3 gate are documented in full. A small "Methodology" link beneath the chart block (matching the Phase 6 T14 routing pattern for other R2 vizzes) would let the curious reader audit the published method against the binding text in `DATA_DICTIONARY.md` §1.1. The Remedy B T2 DATA_DICTIONARY entry (per N5 of the Remedy B verdict) is the canonical landing point.

This is non-blocking and is an audience-translation enhancement, not a methodology requirement.

---

## Resolution status of the originating F1–F5

| Finding | Status under T1+T2+T3+T3b+T4 | Closing evidence |
|---|---|---|
| F1 — normal-approx interval labeled "bootstrap" four times | **CLOSED.** | All four label sites enumerated in F1 replaced with truthful percentile-bootstrap copy. `grep "1\.96"` on `apps/dashboard/src` returns zero matches. |
| F2 — R1 quantity displayed as R2 uncertainty (register error) | **CLOSED.** | Chart consumes `domain.centrality_ci` (R2 published field) only. No R1 path reaches the chart. |
| F3 — n=2 minimum with `1.96·SE` is indefensible | **CLOSED.** | Bootstrap module gates on `n >= 3` (Remedy B N3); empty-state handling at `hasCi` produces honest "No bootstrap CI available (fewer than 3 models)" SR/table/chart annotations. No z-multiplier appears anywhere in the rendering path. |
| F4 — SR copy makes false claim and elides register issue | **CLOSED.** | New SR copy *"95% bootstrap confidence intervals (model-resampling, B=500) are shown as whiskers on each bar"* names the method correctly. M1 above is a stylistic refinement, not a truth correction. |
| F5 — browser-side recomputation fragments the uncertainty story | **CLOSED.** | The pre-existing `useMemo` that recomputed CI is deleted; the chart consumes the published field only. Single source of uncertainty (`cdb_analyze` computes, `cdb_publish` publishes, frontend displays) is restored. |

**The originating FAIL is fully resolved.** No findings carry forward to a subsequent SME review beyond M1–M3 above, which are audience-translation refinements.

---

## What this verdict does NOT cover

- The R1 within-model surfaces in `data/types.ts` L63 and L172 (`centrality_scores_by_run` on `WithinModelResult` and `Focus1ModelData`) and the Focus 1 components that consume them. The originating FAIL was about the R2 chart's misuse of the R2 register, not about R1 surfaces in general. R1 within-model centrality is a separate analytical surface (Phase 9a Focus 1) with its own methodological framing; it is not in scope for this verdict.
- The Phase 6 methodology page entry for `centrality_ci`. The Remedy B verdict's N5 binds the DATA_DICTIONARY entry; the methodology-page write-up is a separate Mark-owned surface, not gated by this T4 review. M3 above is an audience-translation enhancement pointing at that link, not a gating requirement.
- Non-methodology aspects of `feature/visualization-fixes` (the originating branch). Per the Remedy B verdict §Routing, those remain with the Reviewer agent only.

---

## Required before merge

None. T4 is **PASS-WITH-NOTES**; M1, M2, M3 above are non-blocking audience-translation refinements that should be applied in a follow-up commit but do not gate this merge.

---

## Routing

- Verdict file: this document.
- Slack: post summary to `#lsb-cda-sme`.
- This verdict closes the centrality-CI remediation chain (originating FAIL → T1+T2+T3 PASS-WITH-NOTES → T3b → T4 PASS-WITH-NOTES). No further SME review is required on the chart's CI rendering pending future changes to the R2 centrality bootstrap method itself.
- Follow-up: M1 (SR-summary CI binding), M2 (tooltip "with replacement" wording), M3 (methodology-page link from centrality block) can land as a single small commit. They are not gated by SME review individually unless the rewording is non-trivial.

---

*End of CDA SME verdict on Remedy B T4, 2026-05-28. Centrality-CI remediation: CLOSED.*
