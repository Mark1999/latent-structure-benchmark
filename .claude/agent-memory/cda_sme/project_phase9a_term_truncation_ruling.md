---
name: phase9a-term-truncation-ruling
description: Phase 9a term-set truncation ruling — cross-model frequency elbow on pile-sort vocabulary; f_models>=2 pre-filter; min_items=15, max_items=300; item_subset param on pooled builder
metadata:
  type: project
---

Phase 9a term truncation CDA SME ruling issued 2026-05-24. PASS-WITH-NOTES.

**Why:** 5,287-item pooled union from 15 models' pile sorts is computationally impractical and dominated by single-model idiosyncratic terms. Needed a methodologically defensible data-reduction step upstream of the pooled co-occurrence matrix.

**Key decisions:**
- Truncation uses cross-model frequency f_models(term) = number of distinct models whose pile sorts include the term (Register 2 unit, not runs)
- Hard floor: f_models >= 2 (terms from only one model are not shared vocabulary)
- Elbow detection via existing `find_salience_elbow()` on the f_models curve, with min_items=15, max_items=300
- This is a **methodological parameter** (recorded in DomainResult metadata), not a display convenience
- Truncation happens **before** the pooled co-occurrence matrix (item_subset param on `build_pooled_cooccurrence_matrix()`)
- Per-model matrices remain un-truncated (each model keeps its full vocabulary)
- 4 new DomainResult fields: term_truncation_method, term_truncation_params, term_n_total_before_truncation, term_n_after_truncation

**How to apply:** 6 binding T-notes (T1-T6) in the ruling. Amends Phase 9a verdict; all 10 original M-notes unchanged. Schema change requires Architect sign-off + DATA_DICTIONARY.md co-update.

See: [[phase9a-viz-gap-verdict]]
