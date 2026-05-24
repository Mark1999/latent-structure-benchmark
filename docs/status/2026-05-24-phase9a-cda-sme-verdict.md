# CDA SME Verdict: Phase 9a Visualization Gap Closure

**Date:** 2026-05-24
**Reviewer:** CDA SME (external, cognitive/quantitative/cultural anthropology)
**Document reviewed:** `docs/status/2026-05-24-phase9a-viz-gap-kickoff.md`
**Commit at review:** `8f72e00`

---

## CDA SME VERDICT: PASS-WITH-NOTES

| Axis | Verdict |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | PASS-WITH-NOTES |
| Axis 3 — Claims validity | PASS |
| Axis 4 — Audience translation | PASS-WITH-NOTES |
| Register compliance | PASS |
| Vocabulary compliance | PASS |

---

## Rulings on the Eight Methodological Decisions (S6)

### Decision 1: Pooling strategy for cross-model term co-occurrence matrix (T1)

**RULING: Equal weight per model (Option A consensus pool). The Architect's recommendation is correct.**

Rationale: The Register 2 equal-voice principle (ARCHITECTURE.md section 4.2.0) requires that each model contributes equally regardless of OCI. Pooling raw runs equally (55 runs, but 5 from each of 11 models) would happen to produce per-model equality here, but the principle must be stated explicitly and enforced at the implementation level: compute a per-model consensus co-occurrence matrix (from that model's N runs), then average the per-model matrices with equal weight.

This is not the same as averaging all 55 runs. The distinction matters when run counts vary across models (which they do: some models have qa_passed=False runs excluded, yielding fewer than 5 usable runs). Equal-weight-per-run would give under-represented models less voice. Equal-weight-per-model preserves the Register 2 contract.

**Implementation binding note (M1):** The pooled matrix is:

```
pooled[i][j] = (1/M) * sum_over_models( model_cooccurrence[i][j] )
```

where `model_cooccurrence[i][j]` is the fraction of that model's runs in which items i and j co-occur. M = number of models with at least one valid run. Items absent from a given model's vocabulary receive 0.0 for all cells involving that item in that model's matrix (not NaN, not excluded from the denominator). The denominator is always M, not "number of models that produced both items." This is the conservative choice: a model that never mentioned an item is evidence of absence, not missing data.

**Advisory (A1):** If a future version needs to distinguish "model never mentioned item X" from "model mentioned item X but never co-sorted it with item Y," the schema can carry a per-model item-presence mask. For v1, treating absence as zero is correct.

---

### Decision 2: AHC linkage method (T3)

**RULING: Average linkage (UPGMA). Not Ward.**

Rationale:

1. **Ward linkage minimizes within-cluster variance.** This is appropriate when the analyst expects roughly equal-sized, roughly spherical clusters. Term co-occurrence data from CDA pile sorts does not satisfy those assumptions. Pile-sort-derived co-occurrence matrices produce clusters of highly unequal size (a large "miscellaneous" pile is near-universal in CDA data, including the LSB family domain).

2. **Average linkage (UPGMA) is the standard in the CDA literature for item-level clustering.** Borgatti (1994, "Cultural domain analysis") uses average linkage throughout. Spencer et al. (2016) used it for the coffee flavor wheel dendrogram. The method computes distance between clusters as the mean of all pairwise distances between their members. It makes no distributional assumptions about cluster shape or size.

3. **Ward produces dendrograms that look "cleaner" but mislead.** The uniform-cluster-size assumption of Ward creates false visual clarity by forcing unequal clusters toward equal size. For exploratory analysis on categorical-structure data, this is a distortion, not an improvement.

**Implementation binding note (M2):** Use `method="average"` in scipy linkage call. Document in the function docstring: "Average linkage (UPGMA) per Borgatti 1994 and CDA pile-sort analysis convention. Ward linkage was considered and rejected because its equal-cluster-size assumption does not match the empirical structure of pile-sort co-occurrence data."

---

### Decision 3: Distance metric for AHC (T3)

**RULING: 1 - co-occurrence. Not Jaccard.**

Rationale:

1. The co-occurrence matrix cells are already in [0, 1] where 1.0 means "always co-sorted" and 0.0 means "never co-sorted." The natural dissimilarity is `1 - cooccurrence`. This is what `run_item_mds()` already uses for the item-level MDS (confirmed in `mds.py`), so the AHC and MDS operate on the same distance space. If they used different metrics, cluster boundaries on the dendrogram would not correspond to spatial neighborhoods on the MDS plot.

2. Jaccard distance would be appropriate if the input were binary presence/absence vectors (each row = an informant, each column = an item, cell = 0/1 for "did this informant list this item"). That is a free-list analysis, not a pile-sort analysis. The co-occurrence matrix is already a proportion, not binary, so Jaccard's correction for joint-absence is irrelevant.

**Implementation binding note (M3):** `dissimilarity = 1.0 - pooled_cooccurrence`. Ensure diagonal is set to 0.0 after subtraction (floating point). Use the same symmetrization pattern as existing `cluster_models()`.

---

### Decision 4: Bootstrap resampling unit for term uncertainty (T4)

**RULING: Resample models with replacement (preserving within-model run pooling). Not runs. Not two-level.**

Rationale: This is a Register 2 term-level bootstrap. The uncertainty question being answered is: "how much does the position of this term in the pooled map depend on which models are included?" The analogous question at the model level is already answered by `bootstrap_mds_ellipses()`, which resamples runs within models. But that is a Register 2 model-level bootstrap where each model's own run-variance propagates.

For the term-level pooled map, the dominant source of structural uncertainty is which models are in the pool, not which runs within a model. A model that consistently puts "nuclear family" with "extended family" contributes that signal regardless of which of its 5 runs you draw. But a model that puts "nuclear family" with "household" is a different structural voice. The interesting question is: "if we had drawn a different set of models, would this term be in the same neighborhood?"

Therefore:

- Resample the M models with replacement (same model may appear 0, 1, 2, ... times in a bootstrap iteration).
- For each resampled model, use its full per-model consensus co-occurrence matrix (already computed per M1).
- Pool the resampled model matrices, compute item MDS, Procrustes-align to reference, record term coordinates.
- B=200 iterations. Sufficient for 95% CI estimation on 25-item MDS. Compute is trivial (no raw-run rebuilding needed per iteration since per-model matrices are pre-computed).

**Implementation binding note (M4):** The resampling unit is models (the Register 2 informants), not runs. This is the same logic as the model-level bootstrap but applied one layer deeper (to the item MDS derived from the pooled model matrices). Per-model consensus matrices are pre-computed once; the bootstrap loop only pools and runs MDS.

**Annotation required (M4a):** The resulting per-term CIs reflect between-model structural variance only. They do not capture within-model run-to-run variance (which is already absorbed into each model's consensus matrix). This is analogous to the Option 2 annotated-uncertainty posture in `BOOTSTRAP_DESIGN.md` section 3.2. The methods page must state this plainly: "Term position confidence reflects agreement across models, not within-model sampling variance."

---

### Decision 5: AU p-value computation for dendrogram branch stability (T7)

**RULING: Simple bootstrap proportion (the proportion of bootstrap iterations in which each bipartition appears). Not multiscale bootstrap (Shimodaira 2002).**

Rationale:

1. **Multiscale bootstrap (pvclust/AU) requires resampling at multiple scales of the data.** The technique varies the effective sample size (e.g., 0.5x, 1x, 2x the original) and extrapolates a bias-corrected p-value. This is appropriate when the full bootstrap proportion (BP) is known to be biased downward for deeply nested nodes. The bias correction was calibrated on gene-expression clustering with thousands of features and hundreds of samples.

2. **LSB has M=11 models and ~25 items.** The multiscale extrapolation is not well-calibrated at this scale. The original Shimodaira (2002) paper validates AU at n >= 100 observations. At n=11, the correction can over-shoot, producing AU values > 1.0 that must be clipped, which is a sign the method is operating outside its calibrated regime.

3. **The simple bootstrap proportion (BP) is interpretable, transparent, and conservative.** BP = "in what fraction of 200 bootstrap iterations did this branch appear?" If BP = 0.90, the branch is stable. If BP = 0.50, it is not. The visitor to the dashboard understands "appeared in 85% of resamplings" without needing to understand multiscale extrapolation.

4. **Conservative is correct for an exploratory instrument.** LSB does not test hypotheses (section 1.5.7). The dendrogram branch stability is an exploratory diagnostic ("how robust is this grouping?"), not a hypothesis test ("is this grouping significant at alpha=0.05?"). BP answers the diagnostic question directly.

**Implementation binding note (M5):** For each internal node in the linkage tree, compute BP = (number of bootstrap iterations in which the exact bipartition defined by that node appears) / B. "Exact bipartition" means: the set of items on the left subtree of that node is identical to the set in the bootstrap iteration's corresponding bipartition. Use set equality, not label equality. Store as `term_cluster_au_pvalues` (retain the field name for now; rename to `term_cluster_bp_values` is acceptable but not required since the dashboard copy should say "bootstrap support" not "AU p-value").

**Display binding note (M5a):** Dashboard labels this as "bootstrap support (%)" not "AU p-value" and not "significance." Branches below 70% support are rendered with dashed lines and reduced opacity. The 70% threshold is a display choice (UI/UX decides the exact visual treatment), not a statistical gate.

---

### Decision 6: Cluster label aggregation method (T5)

**RULING: Frequency-weighted modal label from all models' centroid-run pile labels, with a two-step matching process.**

Rationale: The challenge is that different models use different pile labels for structurally equivalent clusters. Model A calls the parents pile "Types of Parents," model B calls it "Parental Figures," model C calls it "Parent Roles." The AHC clusters are defined by item membership, not by labels. The task is to assign a human-readable label to each AHC cluster.

Method:

1. **Match each AHC cluster to each model's closest pile.** For each AHC cluster C and each model's centroid-run pile P, compute the Jaccard overlap between C's item set and P's item set. Assign each model's highest-overlap pile as the "matching pile" for that AHC cluster.

2. **Collect the labels from matching piles.** This gives up to M labels (one per model) for each AHC cluster.

3. **Select the modal label.** The label that appears most frequently (exact string match, case-normalized) wins. Ties broken by shortest label (favoring conciseness).

4. **If no exact-match majority exists (all labels unique):** Use the shortest label among the set. Do not attempt semantic deduplication (that would require an LLM or an embedding model, both forbidden in `cdb_analyze`).

**Implementation binding note (M6):** The Jaccard-overlap matching in step 1 must use a minimum threshold (Jaccard >= 0.3) to prevent spurious matches. If no model's pile exceeds the threshold for a given AHC cluster, that cluster's label is "Uncategorized" (a valid output, not a failure state). Document: "Cluster labels are derived from the modal pile label across models; when models disagree, the most common label is used."

**Advisory (A2):** This method will produce imperfect labels. That is acceptable. The cluster label is a convenience for the dashboard visitor, not a finding. The structural finding is the item membership of the cluster, not its label. The label is a gloss. If future phases want better labels, the correct path is adding a human-curation step (Mark reviews and edits), not an LLM labeling step.

---

### Decision 7: Cross-model pile comparison framing (T9)

**RULING: PASS. The framing constraints are:**

1. **No model is ground truth.** The pile comparison must not visually privilege any model's partition as "correct." All columns are visually equivalent (same width, same font weight, same visual hierarchy). No column header says "Reference" or "Baseline."

2. **Divergence is a finding, not a failure.** When item X appears in pile "Parents" for model A and pile "Household" for model B, the dashboard copy must frame this as: "Models organize [item] differently: [Model A] groups it with [context], [Model B] groups it with [context]." Not: "Model B incorrectly places [item] in [wrong pile]."

3. **The comparison view does not compute or display an "agreement score" between models.** Pairwise agreement is already captured by the similarity heatmap (existing viz). The pile comparison is qualitative, showing structure, not quantifying agreement.

4. **The lede or caption accompanying this view must use language from the §1.5.4 approved vocabulary.** Example: "How models categorize [domain] terms: structural divergence across models." Not: "How models see [domain] differently" (forbidden: "see").

**Implementation binding note (M7):** The component's aria-label and screen-reader summary must also respect these constraints. The ReadAsTable rendering should list each model's piles side-by-side without implying an order of correctness. If a "highlight divergences" mode is implemented, the highlight applies symmetrically to all models that differ (no single model is treated as the "expected" partition).

---

### Decision 8: Cultural centrality copy (T10)

**RULING: PASS. The copy constraints are:**

1. **Term: "cultural centrality" (Caulkins 1999).** Never "competence," never "accuracy," never "correctness." The tooltip must explicitly state what centrality measures.

2. **Required tooltip text (verbatim or equivalent):** "Cultural centrality measures how closely a model's categorical structure aligns with the dominant pattern across all models in this domain. A high score means this model's pile-sort structure is typical of the group. A low score means it organizes the domain differently. Neither is better or worse."

3. **Negative centrality framing:** If any model has a negative centrality score, the dashboard copy must say: "This model's categorical structure is systematically different from the group's dominant pattern." Not: "This model disagrees with the consensus" (that imports CCM framing into what may be a non-consensus domain type). Not: "This model is wrong."

4. **Bar chart axis label:** "Cultural centrality (loading on first eigenvector)" is acceptable for the detailed/methodology view. "Structural alignment with group pattern" is acceptable for the summary view. "Competence" in any form is forbidden.

5. **Caption/lede for the centrality chart must include the domain's consensus type.** If the domain is TURBULENT or CONTESTED, centrality scores are less informative (the first eigenvector explains less variance). The caption must note this: "Domain consensus is [type]; centrality scores reflect alignment with the strongest pattern, which explains [X]% of variance." The percentage is `eigenvalue_1 / sum(eigenvalues)` from the existing consensus computation.

**Implementation binding note (M8):** The chart must display error bars (bootstrap CI on centrality score). The existing bootstrap iterations already produce per-iteration similarity matrices; extracting centrality per iteration is a lightweight extension (eigendecompose each bootstrap similarity matrix, extract first-eigenvector loadings, compute percentiles). This is confirmed feasible from the existing `bootstrap_mds_ellipses()` structure.

---

## Additional Findings

### F1: Item-set union handling (T1)

The kickoff says "Item set = union of all items across all models' pile sorts in the domain." This is correct, but the implementation must handle the fact that not all items appear in all models' pile sorts. Per M1 above, absence = 0.0 in the model's co-occurrence matrix for that item pair. This means the pooled matrix will have some cells where only a subset of models contribute non-zero co-occurrence. The pooled value is the mean across ALL models (including zeros from models that did not produce the item), not just models that produced both items. This is the conservative choice and prevents inflating co-occurrence for items that only one model produced.

### F2: Linkage matrix serialization (T5 schema)

The kickage proposes `term_cluster_linkage: list[list[float]]`. A scipy linkage matrix has shape (n-1, 4) where each row is [idx1, idx2, distance, count]. The JSON serialization as nested list is correct, but the DATA_DICTIONARY.md entry must specify the column semantics (scipy linkage format) so that external researchers can reconstruct the dendrogram from the open data bundle.

### F3: Per-model item MDS (T2) is Register 1 output, not Register 2

The plan mentions populating `WithinModelResult.mds_within_model`. This is a Register 1 output (per-model item map). It must carry the `underestimates_uncertainty = True` annotation if bootstrapped. The pooled term MDS (from the cross-model pool) is Register 2 and does not carry that annotation. The distinction must be preserved in the DATA_DICTIONARY.md entries for both fields.

### F4: B=200 is acceptable for term bootstrap

The plan proposes B=200 for the term-level bootstrap. This is acceptable. At 25 items, the 95% CI half-width on a single coordinate converges to within 5% of its B=500 value by B=150 (empirical rule for 2D MDS with <50 points). B=200 provides adequate precision for the exploratory display purpose without wasting compute. Document the choice.

### F5: "Pile stability" metric for T9 R10 compliance is sound

The proposed per-term pile stability (fraction of a model's runs in which an item appears in the same pile as in the centroid run) is an appropriate categorical-uncertainty proxy. It avoids the forbidden territory of treating pile assignment as numeric. Implementation note: compute as `n_runs_same_pile / n_runs_total` for each item per model, where "same pile" means the item co-occurs with the same set of other items (not just the same pile index, since pile ordering is arbitrary).

---

## Required Before Merge (Binding Notes for Coder)

1. **(M1)** Pooled matrix uses equal-weight-per-model (mean of per-model consensus matrices), denominator always M. Absence = 0.0, not excluded.
2. **(M2)** AHC uses `method="average"` (UPGMA). Docstring cites Borgatti 1994.
3. **(M3)** Distance metric is `1 - cooccurrence`. Same as item MDS.
4. **(M4)** Bootstrap resamples models with replacement, uses pre-computed per-model matrices. B=200.
5. **(M4a)** Methods page and DATA_DICTIONARY note that term CIs reflect between-model variance only.
6. **(M5)** Branch stability uses simple bootstrap proportion (BP), not multiscale AU.
7. **(M5a)** Dashboard labels as "bootstrap support (%)" not "AU p-value." Dashed branches below 70%.
8. **(M6)** Cluster labels use frequency-weighted modal label with Jaccard >= 0.3 matching threshold.
9. **(M7)** Pile comparison treats all models symmetrically; no model is visual ground truth.
10. **(M8)** Centrality chart uses "cultural centrality" terminology per Caulkins 1999; tooltip text per ruling above.

---

## Advisory Notes (Non-Blocking)

- **(A1)** Per-model item-presence mask: not needed for v1; flag for v2 if item-set asymmetry becomes a confound.
- **(A2)** Cluster labels will be imperfect. Acceptable for v1. Human curation in future phases is the correct improvement path, not LLM labeling.

---

*End of verdict. Route to Coder with all M-notes binding. UI/UX review proceeds independently on the four new component types after this verdict is posted.*
