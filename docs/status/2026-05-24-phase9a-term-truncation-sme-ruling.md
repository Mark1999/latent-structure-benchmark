# CDA SME Ruling: Term Set Truncation for Pooled Co-occurrence Matrix

**Date:** 2026-05-24
**Reviewer:** CDA SME (external, cognitive/quantitative/cultural anthropology)
**Request:** Architect/Mark — methodologically correct truncation strategy for 5,287-item pooled term set
**Companion verdict:** `docs/status/2026-05-24-phase9a-cda-sme-verdict.md` (Phase 9a PASS-WITH-NOTES)
**Amends:** Phase 9a — adds a term-set truncation step upstream of T1's pooled matrix construction

---

## CDA SME VERDICT: PASS-WITH-NOTES

| Axis | Verdict |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | PASS-WITH-NOTES |
| Axis 3 — Claims validity | PASS |
| Axis 4 — Audience translation | PASS |
| Register compliance | PASS |
| Vocabulary compliance | PASS |

---

## The Ruling

### Question 1: Which truncation method?

**RULING: Option A — Cross-model frequency elbow, applied to the pile-sort vocabulary (not the free-list vocabulary).**

The frequency being counted must be defined precisely:

**For each term in the pooled union, compute `f_models(term)` = the number of distinct models (out of M) that included this term in at least one pile sort.** This is a cross-model frequency count, not a cross-run frequency count. A term that appears in 5 runs of the same model counts as f_models = 1. A term that appears once each in 8 different models counts as f_models = 8.

Sort terms descending by f_models. Apply the existing `find_salience_elbow()` maximum-distance-to-chord algorithm to this sorted frequency curve.

Rationale:

1. **Cross-model frequency is the correct unit for Register 2 analysis.** The pooled co-occurrence matrix is a Register 2 artifact (ARCHITECTURE.md section 4.2.0). Register 2's informants are models, not runs. A term that only one model ever produced is not part of the shared domain vocabulary — it is an idiosyncrasy of that model's corpus lens. The CDA analog: in a multi-informant study, a free-list term mentioned by only one informant out of 15 is long-tail noise. Borgatti (1994) cuts at the item-frequency level for precisely this reason.

2. **Why pile-sort vocabulary, not free-list vocabulary.** The pooled matrix is built from pile-sort co-occurrence (`build_pooled_cooccurrence_matrix` operates on `parsed_piles`). A term that appeared in a free list but was not carried into the pile sort has no co-occurrence data to contribute. Truncating on free-list union would include terms with zero co-occurrence signal, producing rows/columns of all-zero in the pooled matrix and degenerate MDS behavior.

3. **Why not Option B (minimum K threshold), Option C (Sutrop CSI), or Option D (Smith's S)?** Option B is arbitrary and non-reproducible (what is K?). Options C and D use salience indices that measure within-model properties (rank position, mention frequency within a model's free-list). Those are Register 1 measures — applying them as a cross-model filter conflates registers. The cross-model frequency f_models is the only measure that answers the Register 2 question: "is this term part of the shared vocabulary that multiple model-informants converge on?"

---

### Question 2: What parameters?

**RULING: Apply `find_salience_elbow()` with `min_items=15` and `max_items=300`.**

Justification:

- **`min_items=15`.** With M=15 models, the minimum interpretable item set for MDS in 2 dimensions is around 8 items (ARCHITECTURE.md section 4.2.0, Register 3 minimum intersection). Floor at 15 to ensure the dendrogram and MDS are readable.

- **`max_items=300`.** Mark said "25-50 seems low given better compute." He is correct. The existing default ceiling of 60 in `find_salience_elbow()` was calibrated for within-model free-list truncation, where 30-60 items is the classical CDA sweet spot for a single informant. But the pooled cross-model term set is a different beast: it is the union vocabulary of 15 informants. In human CDA with 15 informants and free lists of 30-50 items each, the union typically runs 100-250 items. Setting max_items=300 gives the elbow room to land naturally wherever the data dictates, without artificial ceiling compression.

- **The elbow algorithm itself (`find_salience_elbow`) is already implemented and verified.** It uses the maximum-distance-to-chord geometric method, which is the standard for scree-plot-style cutoffs. The only change is that the input curve is f_models (descending) instead of Smith's S (descending). The algorithm is agnostic to the semantic meaning of the y-axis — it finds the geometric elbow regardless.

**Additional binding parameter: `min_model_count=2`.** Before applying the elbow, pre-filter to remove any term with f_models < 2 (terms that only one model ever pile-sorted). These are definitionally not shared vocabulary. This is a hard floor, not a parameter the elbow can override. The elbow operates on the remaining terms (those with f_models >= 2).

The reasoning: a term that one model out of 15 mentioned contributes a row of 14 zeros and 1 non-zero in the pooled matrix. Under the M1 pooling rule (denominator always M), its pooled co-occurrence values with other terms will be divided by 15, producing very small values that add noise without adding structural signal. Removing f_models=1 terms is conservative and defensible.

---

### Question 3: Methodological parameter or display convenience?

**RULING: This is a methodological parameter. It must be documented, reproducible, and recorded in the published data.**

Specifically:

- The truncation step is part of the analysis pipeline, not the display layer. It determines which terms enter the pooled co-occurrence matrix, which in turn determines the MDS coordinates, the AHC, and the bootstrap CIs. A different truncation produces a different map. This is not a visualization filter — it is a data-reduction step in the analytical pipeline.

- The published `DomainResult` must carry metadata documenting the truncation. New fields:

  ```
  term_truncation_method: str = "cross_model_frequency_elbow"
  term_truncation_params: dict = {}  # min_items, max_items, min_model_count, elbow_index
  term_n_total_before_truncation: int = 0
  term_n_after_truncation: int = 0
  ```

- The DATA_DICTIONARY.md entry for these fields must state: "The pooled term set is truncated before co-occurrence computation. The truncation method, parameters, and pre/post counts are recorded for reproducibility. External researchers wishing to replicate the analysis with a different truncation can rebuild from `informants.jsonl`."

- The methodology page must name this step and its rationale: "The union of all terms across all models' pile sorts is truncated to the shared vocabulary — terms that at least two models independently included in their pile sorts. Within this shared set, a geometric elbow detector identifies the transition from high-frequency core terms to the long tail, and terms above the elbow are retained for the pooled analysis."

---

### Question 4: Where in the pipeline?

**RULING: Before the co-occurrence matrix. The truncation filters the item set that enters `build_pooled_cooccurrence_matrix()`, not the output.**

Implementation binding note: **The per-model consensus co-occurrence matrices (built by `build_cooccurrence_matrix()`) remain un-truncated.** Each model's matrix uses its full pile-sort vocabulary. The truncation applies only when building the pooled matrix: the item-set argument to `build_pooled_cooccurrence_matrix()` is the truncated list, not the full union.

This means `build_pooled_cooccurrence_matrix()` needs a small interface change: accept an optional `item_subset: list[str] | None` parameter. When provided, the pooled matrix uses this item set instead of computing the full union. When None, the current behavior (full union) is preserved for backward compatibility and testing.

Rationale: truncating the pooled input is more efficient (avoids building and then discarding a 5,287 x 5,287 matrix) and produces cleaner analytical semantics (the MDS, AHC, and bootstrap all operate on the same truncated item set from the start, with no hidden filtering).

---

## Implementation Binding Notes

**(T1)** New function `compute_cross_model_term_frequency(records_by_model: dict[str, list[InformantRecord]]) -> list[tuple[str, int]]` that returns `(term, f_models)` pairs sorted descending by f_models. This function counts the number of distinct models whose pile sorts include each term. It operates on `pile_sort.parsed_piles`, not on `freelist.parsed_items`.

**(T2)** The pipeline truncation step goes between the per-model matrix construction (step 2 in `run_pipeline`) and the pooled matrix construction (step 2b). Pseudocode:

```python
# Compute cross-model term frequency
term_freq = compute_cross_model_term_frequency(records_by_model)
# Pre-filter: remove f_models < 2
shared_terms = [(t, f) for t, f in term_freq if f >= 2]
# Apply elbow detection to the frequency curve
elbow_index = find_salience_elbow(
    [(t, float(f)) for t, f in shared_terms],
    min_items=15,
    max_items=300,
)
truncated_items = [t for t, _ in shared_terms[:elbow_index]]
# Build pooled matrix using truncated item set
pooled_matrix = build_pooled_cooccurrence_matrix(
    records_by_model, item_subset=truncated_items,
)
```

**(T3)** `build_pooled_cooccurrence_matrix()` gains an `item_subset: list[str] | None = None` parameter. When provided, this list is used instead of the computed union. The function's existing docstring (referencing CDA SME M1) remains accurate — the pooling arithmetic is unchanged; only the item set is narrowed.

**(T4)** The per-model item MDS (`run_item_mds()` on each model's own matrix) is NOT truncated. Each model's own map uses its full vocabulary. Truncation applies only to the pooled Register 2 term map.

**(T5)** The `DomainResult` carries the four truncation metadata fields listed above. `DATA_DICTIONARY.md` is updated in the same PR.

**(T6)** The methodology page text for this step is: "Terms appearing in only one model's pile sorts are excluded from the pooled analysis as model-specific vocabulary. Among the remaining shared terms, a geometric elbow detector (maximum-distance-to-chord on the cross-model frequency curve) identifies the core vocabulary that multiple models converge on. For the family domain, this reduced the term set from [N_total] to [N_truncated] terms." The specific numbers are filled from the metadata fields at page-generation time.

---

## Advisory Notes (Non-Blocking)

**(A1)** The elbow location should be logged and inspected by Mark before the pipeline output is published. If the elbow lands at an unintuitive place (e.g., 20 terms or 280 terms), Mark can manually override by setting `max_items` or `min_items` in the pipeline config. The override must be recorded in the truncation metadata. This is the standard CDA practice: the elbow is a suggestion, not an oracle.

**(A2)** For future domains (holidays, food), the same truncation method applies. The elbow will land at different places depending on the domain's vocabulary structure. This is expected and correct — the truncation is data-driven, not domain-hardcoded.

**(A3)** The f_models=1 floor may be reconsidered if a future domain has very few models (e.g., M=3). At M=3, f_models >= 2 means "at least two thirds of models agree this is domain vocabulary," which is a strong filter. At M=15, f_models >= 2 is a very weak filter (13% of models). The floor is calibrated for the current M=15 regime. If M drops below 5, flag this for SME re-review.

**(A4)** The sensitivity of the MDS and AHC to truncation boundary could be tested empirically by running the pipeline at elbow +/- 20% and inspecting Procrustes distance. This is a diagnostic, not a gate. If Mark wants it, it is a Phase 9b task.

---

## Relationship to Prior Rulings

This ruling amends the Phase 9a CDA SME verdict (`2026-05-24-phase9a-cda-sme-verdict.md`) by inserting a term-set truncation step upstream of the pooled matrix construction. All 10 M-notes from the original verdict (M1 through M8, plus M4a and M5a) remain binding and unchanged. The truncation does not alter the pooling arithmetic (M1), the linkage method (M2), the distance metric (M3), the bootstrap resampling unit (M4), the branch stability computation (M5), the cluster label aggregation (M6), the pile comparison framing (M7), or the centrality terminology (M8).

The truncated item set becomes the `reference_items` argument to `bootstrap_term_mds_ellipses()` and `bootstrap_branch_stability()` per M4 and M5. The bootstrap resampling unit (models with replacement) is unaffected — the truncation narrows the item dimension, not the informant dimension.

---

*End of ruling. Route to Coder with T1-T6 binding notes. Schema change (T5) requires Architect sign-off and DATA_DICTIONARY.md co-update per CLAUDE.md section 6 rule 6.*
