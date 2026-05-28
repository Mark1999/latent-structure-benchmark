---
name: centrality-ci-register-error-precedent
description: 2026-05-28 viz-fixes FAIL — browser-side normal-approx CI on per-run R1 centrality loadings, labeled "bootstrap" four ways, affixed to the R2 cultural-centrality point estimate. Two errors stacked. Establishes the precedent for any future browser-side CI computation on R2 quantities.
metadata:
  type: project
---

External AI on `feature/visualization-fixes` introduced a browser-side CI
on cultural centrality that stacks two methodological errors:

1. **Method misnomer.** `mean ± 1.96·SE` over per-run values, labeled
   "bootstrap" in screen-reader copy, tooltip, empty-state tooltip, table
   column header ("Bootstrap N"), and TS field name (`n_bootstrap`).
   Normal approximation is not bootstrap; the dashboard's other CIs
   (`oci_ci`, `similarity_ci`, `consensus_ci`, `mds_uncertainty`) all are.

2. **Register confusion (the deeper error).** Source field is
   `WithinModelResult.centrality_scores_by_run` — per-run loadings on the
   within-model run × run agreement matrix, a Register 1 quantity. Display
   target is `DomainResult.cultural_centrality_scores` — first eigenvector
   of the inter-model similarity matrix, a Register 2 quantity. Different
   quantities, different sampling units. An R1 CI affixed to an R2 point
   inherits R1's narrow bias (`underestimates_uncertainty=True`,
   BOOTSTRAP_DESIGN §2) AND answers the wrong question.

**Why:** External AI saw `centrality_scores_by_run`, assumed it was the
bootstrap distribution of `cultural_centrality_scores`, and computed a
CI from it. The shared word "centrality" is misleading. The two scalars
have nothing in common except the eigenvector-of-something derivation.

**How to apply:**
- Any future browser-side CI computation on an R2 published quantity is
  a doctrinal red flag; route to Remedy B (publish a real `*_ci` from
  `cdb_analyze` via the bootstrap module) by default.
- The pattern "field has run-level values, ergo I can compute a CI from
  it" is the trap. Run-level values from R1 do not estimate the sampling
  variance of an R2 statistic computed on the inter-model matrix.
- The canonical R2 bootstrap unit is **models**, per BOOTSTRAP_DESIGN
  §3.1 (consistent with `bootstrap_mds_ellipses` Option 2).
- Verdict: `docs/status/2026-05-28-viz-fixes-cda-sme-verdict.md`.

Related: [[centrality-ci-doctrinal-pattern]] (not yet written — the
positive contract for what an R2 centrality CI should look like once
Remedy B ships).
