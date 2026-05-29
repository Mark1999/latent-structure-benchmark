---
name: remedy-b-t4-closed
description: Remedy B T4 (frontend consumption of published centrality_ci) PASS-WITH-NOTES 2026-05-28; closes the centrality-CI remediation chain originating from the FAIL on feature/visualization-fixes.
metadata:
  type: project
---

Remedy B T4 (commit `9cfa677`) verdict: **PASS-WITH-NOTES**. The browser-side `mean ± 1.96·SE` mislabeled-as-bootstrap interval is gone; the chart consumes published `centrality_ci` (real R2 model-resampling percentile bootstrap, B=500, with reference-vector sign alignment) only.

**Why:** All four T4 advisory hooks from [[remedy-b-centrality-ci-contract]] are satisfied:
1. "Bootstrap" labeling is truthful at every site (SR summary, tooltip, table caption, SVG aria-label).
2. No cross-method footnote (correctly omitted — that was a Remedy A artifact).
3. Empty-state handled honestly via `hasCi` guard with named copy "No bootstrap confidence interval is available for this domain (fewer than 3 models)".
4. No per-model `Bootstrap N` column — bare `[lo, hi]` tuple shape preserved end-to-end; B=500 stated domain-wide only.

Register correctness confirmed: chart's data source is `domain.centrality_ci` (R2 published field) only; the two `centrality_scores_by_run` hits in `data/types.ts` (L63, L172) are R1 within-model surfaces consumed by Focus1 components, never by `CentralityChart` or `CentralityTable`. Cannot reintroduce the register confusion through the chart's data flow.

Originating findings F1–F5 from [[centrality-ci-register-error]] are all CLOSED by the T1+T2+T3+T3b+T4 chain.

Three non-blocking M-notes:
- **M1** (advisory): SR-summary CI sentence is structurally separated from ranking sentence — recommend binding "Each score is shown with a 95% bootstrap CI (model-resampling with replacement, B=500) as a whisker on its bar."
- **M2** (advisory): Tooltip parenthetical "(model-resampled, B=500)" should align with table caption's more rigorous "(model-resampling with replacement, B=500, percentile method)".
- **M3** (advisory): Add a methodology-page link from the centrality block in `ContentArea.tsx` (matches Phase 6 T14 routing pattern).

**How to apply:** Centrality-CI remediation chain is CLOSED. No further SME review is required on the chart's CI rendering pending future changes to the R2 centrality bootstrap method itself. Verdict file: `docs/status/2026-05-28-remedy-b-t4-cda-sme-verdict.md`. The chart now serves as the dashboard's reference implementation for "R2 percentile-bootstrap CIs displayed honestly with reference-vector sign-aligned method"; future R2-CI charts should match its SR-summary + tooltip + table-caption tiering. Out of scope: the R1 within-model `centrality_scores_by_run` surfaces in Focus 1 (separate analytical layer with its own framing).
