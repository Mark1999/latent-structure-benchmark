---
name: rebaseline-2026-05-29-verdict
description: 2026-05-29 corpus re-baseline (T3+T4) PASS-WITH-NOTES under pinned NumPy 2.4.4 / SciPy 1.17.1; six lede-class threshold guards binding; food is the load-bearing risk surface
metadata:
  type: project
---

PASS-WITH-NOTES on the corpus re-baseline under pinned NumPy==2.4.4 / SciPy==1.17.1. Originating versions of numpy/scipy that produced the published 0.3 corpus are unrecoverable. Re-baseline forward to current pinned versions is methodologically acceptable for the open-data forward-reproducibility guarantee.

**Why:** The drift observed (family `consensus_score` 0.8033→0.8052, `romney_eigenratio` 18.997→19.143, MDS at 3rd–4th decimal) is rounding-level on family and holidays, but food is close to two boundaries (`romney_eigenratio=6.586` only 1.586 above the STRONG/WEAK boundary at 5.0; one per-model `oci=3.74` only 0.74 above the R1-b boundary at 3.0). A silent lede-class flip is the only path from "cosmetic" to "substantive" here, and the verdict converts that risk into a hard halt.

**How to apply:** Six binding threshold-crossing guards (T-1..T-6) — Romney 5.0 / Romney 3.0 / centrality sign / per-model OCI 3.0 / `romney_consensus_warning` flip / `consensus_type` direct equality — must run during T3 (family) and T4 (holidays + food). Any crossing halts and re-routes to SME, not Coder-resolvable. T4 blocked until T3 cleanly clears. Audience-translation requires footer + manifest link + methodology-page paragraph (N1/N2/N3); footer alone insufficient. Manifest needs additions N4 (`python_version`), N5 (`lsb_analysis_version`), N7 (canonicalized-JSON sha256). N6 (`platform`) advisory only.

**Load-bearing memory rule for future re-baseline events:** any deterministic-pipeline re-baseline that touches the analytical environment must enumerate the lede-class thresholds upfront, implement a numeric-diff guard against the prior published values, and halt on crossing. The Coder is not authorized to ship a lede-class change as a side effect of a pipeline-environment-pinning task; that is a separate CDA-significant event.

Verdict file: `docs/status/2026-05-29-rebaseline-cda-sme-verdict.md`.

Related: [[romney_small_n_threshold]] (3.0/5.0 boundary semantics).
