---
name: phase9a-viz-gap-verdict
description: Phase 9a term-level visualization gap closure — CDA SME PASS-WITH-NOTES on 8 methodology decisions (pooling, AHC, bootstrap, labels, framing, centrality copy)
metadata:
  type: project
---

Phase 9a CDA SME verdict issued 2026-05-24. PASS-WITH-NOTES.

**Why:** 8 methodological decisions needed binding rulings for term-level visualizations (pooled term MDS, dendrogram, pile comparison, centrality chart). All decisions resolved with 10 binding M-notes.

**Key rulings:**
- M1: Equal-weight-per-model pooling (mean of per-model consensus co-occurrence matrices). Absence = 0.0.
- M2: Average linkage (UPGMA) for AHC, not Ward. Per Borgatti 1994.
- M3: Distance = 1 - cooccurrence (same metric as item MDS).
- M4: Bootstrap resamples *models* with replacement (Register 2 logic), B=200. Pre-computed per-model matrices reused.
- M5: Simple bootstrap proportion (BP) for branch stability, NOT multiscale AU (Shimodaira 2002 not calibrated at n=11).
- M6: Cluster labels via frequency-weighted modal pile label, Jaccard >= 0.3 matching threshold.
- M7: Pile comparison view must treat all models symmetrically (no visual ground truth).
- M8: "Cultural centrality" terminology only (Caulkins 1999). Required tooltip text specified verbatim.

**How to apply:** All M-notes are binding on the Coder implementing T1-T10. UI/UX review proceeds independently after this verdict. If any implementation question arises about pooling strategy, linkage, or bootstrap unit, refer back to this verdict's specific implementation binding notes.

See: [[phase5-plan-verdict]], [[phase6-T7-R10-empirical-frequency-verdict]]
