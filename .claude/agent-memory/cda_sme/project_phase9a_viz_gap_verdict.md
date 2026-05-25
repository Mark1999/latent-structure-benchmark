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

**Term truncation amendment (same day):** 5,287-item union impractical; ruling adds cross-model frequency elbow truncation upstream of pooled matrix. f_models(term) = count of distinct models whose pile sorts include the term. Pre-filter f_models < 2, then elbow with min_items=15, max_items=300. Truncation is a methodological parameter (recorded in DomainResult metadata), not a display filter. Per-model matrices remain un-truncated. See `2026-05-24-phase9a-term-truncation-sme-ruling.md` for 6 binding T-notes.

**How to apply:** All M-notes are binding on the Coder implementing T1-T10. The truncation T-notes amend T1 (adds item_subset parameter to pooled matrix builder). UI/UX review proceeds independently after this verdict. If any implementation question arises about pooling strategy, linkage, bootstrap unit, or truncation boundary, refer back to these verdicts' specific implementation binding notes.

See: [[phase5-plan-verdict]], [[phase6-T7-R10-empirical-frequency-verdict]]
