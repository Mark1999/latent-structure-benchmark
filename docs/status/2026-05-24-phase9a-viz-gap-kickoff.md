# Phase 9a Architect Kickoff — Visualization Gap Closure (Term-Level Views)

**Status:** Mark-approved scope. Ready for CDA SME review on §S6 methodology decisions.
**Date:** 2026-05-24
**Architect:** Opus
**Companion specs:** ARCHITECTURE.md v0.7.5 (§4.2, §4.2.1, §4.2.6, §4.5, §5.1), CLAUDE.md v1.0, DESIGN_SYSTEM.md v0.4.10, docs/DATA_DICTIONARY.md v0.1.17, docs/BOOTSTRAP_DESIGN.md, docs/SME_REVIEW.md
**Inherits from:** Phase 8 closure (public release). Phase 6 shipped three visualizations (MDS model plot, Similarity Heatmap, Free List Compare). Phase 9a adds term-level and structure-level visualizations from the existing collected data.
**Master commit at kickoff:** `8f72e00`. Test floor: existing suite green.

---

## S1 Goal

Phase 9a closes the visualization gap between what LSB currently shows (model-level structure only) and what classical CDA publications put center-stage (term-level structure). The current dashboard answers "how do models relate to each other?" but not "what does the vocabulary structure look like within a domain?" or "how do different models organize the same terms differently?" The reference papers (Spencer et al. 2016 coffee flavor wheel, Gravlee et al. 2017 pile-sort mode effects, Borgatti 1994) all foreground the item-level cognitive map. Phase 9a adds those views using data already collected.

**Success condition:** A visitor can (a) see individual domain terms plotted in 2D space with labels and cluster regions, (b) view a hierarchical dendrogram showing term clustering, (c) compare how different models partition the same terms into categories with different labels, and (d) view cultural centrality scores per model. These are the highest-priority gaps (Priority 1-4 and Priority 6 from Mark's list).

**Non-goals for Phase 9a:**
- Flavor wheel / radial layout (Priority 5) — Mark: "not sure we care about the radial layout." Dropped from plan, not deferred.
- Comparison MDS with movement links (Priority 8) — deferred to Phase 9b
- Consensus factor plot (Priority 7) — deferred to Phase 9b (may require additional computation)
- Data-cutting/filtering UX (model selectors, domain selectors, cross-model views) — Mark explicitly deferred
- New collection campaigns
- New analytical measures

---

## S2 Architecture: What Exists vs. What Is Needed

### Already implemented in `cdb_analyze`

1. **`cooccurrence.py :: build_cooccurrence_matrix()`** — builds a per-model item-by-item co-occurrence matrix from pile-sort data. Returns `CooccurrenceMatrix` with items list and float matrix.
2. **`mds.py :: run_item_mds()`** — runs item-level MDS on a single model's co-occurrence matrix. Returns `dict[item_name, (x, y)]`.
3. **`cluster.py :: cluster_models()`** — hierarchical clustering using Ward linkage. Currently operates on model-by-model similarity; needs an analogous function for term-by-term clustering.
4. **`bootstrap.py :: bootstrap_mds_ellipses()`** — model-level bootstrap. Needs a term-level counterpart.

### Already in `InformantRecord` (raw data)

1. **`pile_sort.parsed_piles`** — the actual pile groupings per model per run (list of lists of strings)
2. **`interview.parsed_pile_labels`** — model's labels for its piles (list of strings, one per pile)
3. **`freelist.parsed_items`** — full term list per model per run

### Not yet computed / not yet exposed to the dashboard

1. **Cross-model pooled co-occurrence matrix** (aggregate across all models for a domain) — needed for the unified term MDS
2. **Term-level bootstrap uncertainty** (resampling runs to get per-term position confidence)
3. **AHC on term-by-term matrix** (cluster.py only does model-level currently)
4. **Per-model pile structure with labels** as a structured publish-layer artifact
5. **Cluster label aggregation** (majority-vote or frequency-based labels for dendrogram regions)
6. **Cultural centrality scores** — already computed in pipeline.py and stored in `DomainResult.cultural_centrality_scores`, just not rendered on the dashboard

### What `WithinModelResult.mds_within_model` contains today

The field exists in the schema but is currently populated as an empty list `[]` for all models (confirmed in the published `family.json`). The pipeline computes per-model item MDS via `run_item_mds()` but does not wire the results into the `DomainResult` for publication. This is the first thing to fix.

---

## S3 Dependency Graph

```
                                    [T1] Pooled term co-occurrence matrix
                                         (cdb_analyze computation)
                                              |
                              +---------------+------------------+
                              |               |                  |
                              v               v                  v
                   [T2] Term-level MDS   [T3] Term-level AHC   [T4] Term bootstrap
                   (cdb_analyze)         (cdb_analyze)          uncertainty
                              |               |                  |
                              v               v                  v
                   [T5] Publish layer:   [T5] Publish layer     [T5] Publish layer
                   term MDS JSON         dendrogram JSON         CI data in JSON
                              |               |                  |
                              v               v                  v
                   [T6] Term MDS         [T7] Dendrogram        (uncertainty wired
                   dashboard view         dashboard view         into T6 + T7)
                              |
                              v
                   [T8] Cluster label overlay on term MDS
                   (depends on T3 AHC clusters + T6 rendering)

[Parallel track -- no T1-T5 dependency:]

                   [T9] Per-model pile comparison view
                   (raw pile_sort + pile_labels already in informants.jsonl;
                    needs publish artifact + dashboard component)

                   [T10] Cultural centrality display
                   (data already in DomainResult.cultural_centrality_scores;
                    needs dashboard component only)
```

---

## S4 Task Decomposition

### T1 — Pooled cross-model term co-occurrence matrix computation

**One-line:** Add a function to `cdb_analyze/cooccurrence.py` that builds a pooled item-by-item co-occurrence matrix across ALL models for a domain (not per-model), aggregating across all runs of all models.

**Rationale:** The reference CDA visualizations (Gravlee Figure 1, Spencer coffee MDS) show ALL informants' data in a single term map. The LSB equivalent aggregates across all 11 models x 5 runs = 55 informant runs. This produces a unified "domain consensus" item map showing the vocabulary structure that models converge on.

**Implementation notes:**
- New function `build_pooled_cooccurrence_matrix(records: list[InformantRecord]) -> CooccurrenceMatrix` — takes ALL records for a domain regardless of model.
- Same algorithm as existing `build_cooccurrence_matrix` but without the single-model constraint.
- Item set = union of all items across all models' pile sorts in the domain.
- Co-occurrence count = fraction of ALL runs (across all models) in which item pair co-occurs in the same pile.
- The resulting matrix drives the unified term MDS (T2) and the term AHC (T3).

**Affected files:** `packages/cdb_analyze/cdb_analyze/cooccurrence.py`

**CDA SME review required:** YES — the decision to pool across all models (equal weight per run) vs. one-per-model (equal weight per model) vs. weighted by OCI is a methodological decision. The Architect recommends equal-weight-per-model (each model contributes its consensus pile sort, not all raw runs) to match the Register 2 equal-voice-per-model principle in ARCHITECTURE.md §4.2.0. But this needs SME validation.

**Acceptance criteria:**
- Function exists and returns a valid `CooccurrenceMatrix`
- Items sorted deterministically
- Unit test with fixture data from `tests/fixtures/`
- Docstring references the pooling strategy rationale

---

### T2 — Term-level MDS (pooled and per-model) wired into pipeline

**One-line:** Wire `run_item_mds()` calls into `pipeline.py` so that (a) a pooled term MDS using the T1 matrix is computed, and (b) per-model term MDS coordinates are populated in `WithinModelResult.mds_within_model` (currently empty).

**Implementation notes:**
- Pooled MDS: `run_item_mds(pooled_matrix)` produces `dict[str, (float, float)]` of term coordinates.
- Per-model MDS: `run_item_mds(per_model_matrix)` for each model, results into `WithinModelResult.mds_within_model`.
- Both need item labels stored alongside coordinates (the existing return type already maps item name to coordinate).
- The pooled term MDS coordinates become a new top-level field on `DomainResult`.

**Schema change required:** YES — `DomainResult` needs:
```
term_mds_coordinates: dict[str, tuple[float, float]] = {}  # item_name -> (x, y) from pooled matrix
term_mds_items: list[str] = []  # ordered item list for the term MDS
```
And `WithinModelResult.mds_within_model` needs to be populated (field exists, schema unchanged; pipeline wiring only).

**Affected files:** `packages/cdb_analyze/cdb_analyze/pipeline.py`, `packages/cdb_core/cdb_core/schemas.py`, `docs/DATA_DICTIONARY.md`

**CDA SME review required:** YES — same pooling decision as T1.

**Acceptance criteria:**
- `DomainResult.term_mds_coordinates` is non-empty after pipeline run
- `WithinModelResult.mds_within_model` is populated with (n_items, 2) data
- `DATA_DICTIONARY.md` updated for new field
- Architect sign-off on schema change

---

### T3 — Term-level AHC (hierarchical clustering of terms)

**One-line:** Add a `cluster_terms()` function to `cdb_analyze/cluster.py` that performs agglomerative hierarchical clustering on the pooled item-by-item co-occurrence matrix, producing a scipy linkage matrix suitable for dendrogram rendering.

**Implementation notes:**
- Input: the pooled `CooccurrenceMatrix` from T1
- Distance metric: `1 - co-occurrence` (same as model MDS uses similarity to dissimilarity)
- Linkage method: Ward (matches existing `cluster_models()`; alternative: average linkage, which is more common in CDA literature for term clustering). **CDA SME must decide.**
- Output: `TermClusterResult` dataclass with `items: list[str]`, `linkage_matrix: NDArray`, `cluster_labels: list[int]` at a given cut level.
- Cut level decision: use the same "biggest gap in merge distances" heuristic as `cluster_models()` for the default, but expose an explicit `n_clusters` parameter.

**Schema impact:** New schema type `TermClusterResult` in `cdb_core/schemas.py` (or a simpler serializable form for the publish layer). Needs `DATA_DICTIONARY.md` update.

**CDA SME review required:** YES — linkage method choice (Ward vs. average vs. complete) and distance metric (1-cooccurrence vs. Jaccard distance) are methodologically significant. The SME review of Spencer et al. 2016 used average linkage; Borgatti (1994) recommends average. The Architect leans toward average linkage to match the CDA literature but defers to SME.

**Affected files:** `packages/cdb_analyze/cdb_analyze/cluster.py`, `packages/cdb_core/cdb_core/schemas.py`, `docs/DATA_DICTIONARY.md`

**Acceptance criteria:**
- Function produces a valid linkage matrix
- Reproducible with fixed random state
- Unit test verifies dendrogram structure with known fixture
- Linkage method documented in docstring with SME rationale

---

### T4 — Term-level bootstrap uncertainty

**One-line:** Extend `bootstrap.py` to compute per-term position uncertainty on the pooled term MDS, producing 95% confidence ellipses (or radii) for each term's 2D position.

**Implementation notes:**
- Resampling strategy: for each bootstrap iteration, resample the 55 informant runs (11 models x 5) with replacement, rebuild the pooled co-occurrence matrix from the resampled runs, rerun item MDS, Procrustes-align to reference solution, record each term's coordinates.
- Output: per-term 95% confidence ellipse (same `BootstrapEllipse` type as model-level) or a simpler per-term confidence radius (since many terms will have near-circular uncertainty).
- Computation cost: B=200 (reduced from B=500 model-level because item MDS is cheaper per iteration — fewer points, no cross-model similarity step). Document the B choice.
- Note: this is the R10 compliance mechanism for the term MDS. Without it, the term MDS cannot ship per the "no point estimates without uncertainty" rule.

**CDA SME review required:** YES — the resampling unit (runs with replacement) and the alignment strategy (Procrustes to reference) are methodological decisions.

**Schema impact:** New field on `DomainResult`:
```
term_mds_uncertainty: dict[str, BootstrapEllipse] = {}  # item_name -> ellipse
```
Plus `DATA_DICTIONARY.md` update.

**Affected files:** `packages/cdb_analyze/cdb_analyze/bootstrap.py`, `packages/cdb_analyze/cdb_analyze/pipeline.py`, `packages/cdb_core/cdb_core/schemas.py`, `docs/DATA_DICTIONARY.md`

**Acceptance criteria:**
- Per-term ellipses produced for all items in the term MDS
- `n_bootstrap` recorded
- Procrustes alignment to reference verified by test
- Architect sign-off on schema change

---

### T5 — Publish layer: term-structure JSON artifacts

**One-line:** Extend `cdb_publish/build.py` to write the term MDS, term clusters, per-model pile structure, and cultural centrality data into the published domain JSON that the dashboard reads.

**Implementation notes:**
- The `DomainResult` already carries all computed data after T1-T4 wire-up. The publish layer's job is to ensure the domain JSON files in `apps/dashboard/public/data/` contain the new fields.
- Additional derived data for the dashboard:
  - Per-model pile structure with labels: extract from `InformantRecord` pile_sort + interview for the centroid run (already identified by `centroid_run_id` in `WithinModelResult`). Publish as `centroid_piles: dict[model_id, {piles: list[list[str]], labels: list[str]}]`.
  - Cluster labels for dendrogram regions: aggregate `parsed_pile_labels` across all models' centroid runs to produce majority-vote labels for each AHC cluster.
- The centrality scores are already in `DomainResult.cultural_centrality_scores` — they just need to flow through to the dashboard JSON (verify they already do; they should since `build.py` serializes the full `DomainResult`).

**Schema impact:** New field on `DomainResult`:
```
centroid_piles: dict[str, CentroidPileData] = {}  # model_id -> piles+labels from centroid run
term_cluster_labels: list[str] = []  # one label per cluster from AHC, derived from pile label aggregation
term_cluster_linkage: list[list[float]] = []  # scipy linkage matrix as nested list
term_cluster_assignments: dict[str, int] = {}  # item_name -> cluster_id
```
Plus a new Pydantic model `CentroidPileData` (or use a plain dict in the JSON).

`DATA_DICTIONARY.md` update required.

**CDA SME review required:** YES — the label aggregation strategy (majority-vote across model centroid runs for naming dendrogram clusters) is methodologically significant. This is the core of the "how do models collectively organize the domain?" question.

**Affected files:** `packages/cdb_publish/cdb_publish/build.py`, `packages/cdb_core/cdb_core/schemas.py`, `packages/cdb_analyze/cdb_analyze/pipeline.py`, `docs/DATA_DICTIONARY.md`

**Acceptance criteria:**
- Published domain JSON contains all new term-structure fields
- Centroid pile data populated for each model
- Cluster labels derived and present
- Data dictionary updated

---

### T6 — Dashboard: Term MDS Plot view

**One-line:** New React component `TermMDSPlot.tsx` that renders individual domain terms as labeled points in 2D space with bootstrap confidence indicators, registered as a new tab in `VizSwitcher`.

**Implementation notes:**
- Reads `term_mds_coordinates`, `term_mds_uncertainty`, `term_cluster_assignments` from domain JSON.
- Each term is a labeled point (term name as text label).
- Points colored by cluster assignment (from T3/T5).
- 95% confidence ellipses rendered per term (R10 compliance). Given the density of terms (~25 per domain), ellipses may need to be rendered at reduced opacity or on hover only to avoid visual noise — UI/UX agent decides.
- Cluster regions shown as convex hulls or shaded backgrounds behind term groups (UI/UX decides visual treatment).

**UI/UX review required:** YES — this is a new visualization type not covered in `DESIGN_SYSTEM.md`. The UI/UX agent must specify: point size, label placement strategy (avoid overlaps), cluster region rendering, ellipse visibility pattern, interaction (hover for full uncertainty, click for details), mobile treatment.

**CDA SME review required:** NO (visualization only; methodology baked in at T1-T4).

**Affected files:** `apps/dashboard/src/components/TermMDSPlot.tsx` (new), `apps/dashboard/src/components/VizSwitcher.tsx`, `apps/dashboard/src/components/DataExplorer.tsx`, `DESIGN_SYSTEM.md` (UI/UX update)

**Acceptance criteria:**
- All domain terms rendered as labeled points
- Cluster coloring visible
- Uncertainty ellipses present (R10)
- ReadAsTableToggle provides tabular alternative (WCAG)
- ScreenReaderSummary provided
- Tests pass

---

### T7 — Dashboard: Dendrogram view

**One-line:** New React component `Dendrogram.tsx` that renders the term hierarchical clustering as a tree diagram with color-coded clusters and aggregate category labels, registered as a new tab in `VizSwitcher`.

**Implementation notes:**
- Reads `term_cluster_linkage`, `term_mds_items`, `term_cluster_assignments`, `term_cluster_labels` from domain JSON.
- Renders as a top-down or left-to-right tree (UI/UX decides orientation).
- Leaf nodes = individual terms. Interior branches colored by cluster.
- Cluster labels annotated at the appropriate branch level.
- **R10 compliance for dendrograms:** Uncertainty in a dendrogram manifests as instability of cluster membership across bootstrap iterations. The standard approach is AU (Approximately Unbiased) p-values per branch node, showing how often that branch appears in bootstrap replications. This requires an additional computation in T4 (tracking branch stability across bootstrap iterations).

**R10 uncertainty approach for dendrogram:** For each node in the hierarchical tree, compute the proportion of bootstrap iterations in which that bipartition appears. Display as a confidence value (0-100%) on each branch. Branches below a threshold (e.g., 50%) are rendered with dashed lines to indicate instability.

**UI/UX review required:** YES — new component type. UI/UX must specify: tree orientation, branch styling, leaf label typography, cluster color assignment, AU p-value display format, mobile treatment (dendrogram is inherently wide/tall).

**CDA SME review required:** YES — the AU p-value computation and the instability threshold for dashed-line rendering are methodologically significant.

**Schema impact:** Additional field needed from T4:
```
term_cluster_au_pvalues: list[float] = []  # one p-value per internal node in linkage order
```

**Affected files:** `apps/dashboard/src/components/Dendrogram.tsx` (new), `apps/dashboard/src/components/VizSwitcher.tsx`, `DESIGN_SYSTEM.md`, `packages/cdb_analyze/cdb_analyze/bootstrap.py` (AU computation)

**Acceptance criteria:**
- Full dendrogram rendered with all terms
- Cluster coloring matches term MDS cluster coloring (T6)
- AU p-values displayed per node
- Dashed branches for unstable nodes
- ReadAsTableToggle provides tabular cluster membership
- Tests pass

---

### T8 — Dashboard: Cluster label overlay on Term MDS

**One-line:** Extend `TermMDSPlot.tsx` (T6) to overlay aggregate cluster labels (e.g., "Types of Parents", "Types of Siblings") as region annotations, matching the coffee flavor wheel MDS reference where regions are labeled "Fruity", "Floral", etc.

**Dependencies:** T6 (term MDS view), T5 (cluster labels available in JSON)

**Implementation notes:**
- Position each cluster label at the centroid of its cluster's member terms in MDS space.
- Label text comes from `term_cluster_labels` (aggregated from model pile labels in T5).
- Visual treatment: large, semi-transparent text behind the term points, or a bordered region label (UI/UX decides).

**UI/UX review required:** YES — label placement, font size, opacity, interaction with term labels.

**CDA SME review required:** NO (display-only; label aggregation reviewed at T5).

**Affected files:** `apps/dashboard/src/components/TermMDSPlot.tsx` (extension)

**Acceptance criteria:**
- Each cluster region has a visible label
- Labels do not obscure term points
- Toggle to show/hide labels available

---

### T9 — Dashboard: Per-model pile comparison view

**One-line:** New React component `PileComparison.tsx` that shows how different models partition the same domain terms into different categories with different labels — the core CDA structural finding.

**Dependencies:** T5 (centroid pile data published in domain JSON). No T1-T4 dependency — can proceed in parallel.

**Implementation notes:**
- Reads `centroid_piles` from domain JSON: for each model, the centroid run's pile assignments and pile labels.
- Visual layout: a column per model (or selectable 2-3 models for comparison), with terms grouped into their piles, each pile labeled with the model's own label.
- Terms that appear in different piles across models are highlighted (the structural divergence signal).
- Alternative: Sankey/alluvial diagram showing term flow between models' categories.

**R10 compliance:** The pile comparison is categorical, not numeric. Uncertainty here means "how stable is this pile assignment across the model's 5 runs?" The centroid run is the most representative, but the within-model stability is already captured by OCI. Display a small indicator (e.g., asterisk or reduced opacity) for terms whose pile assignment differs across runs for that model. This requires adding a "pile stability" metric per term per model in T5.

**UI/UX review required:** YES — entirely new component type. Likely the most complex visual in the phase.

**CDA SME review required:** YES — the decision of how to represent cross-model categorical divergence (which items move between piles, which piles have no equivalent across models) is methodologically significant. This is the central CDA finding type.

**Schema impact:** Extend `CentroidPileData` to include per-term pile-stability indicators:
```
class CentroidPileData(BaseModel):
    piles: list[list[str]]         # term groupings
    labels: list[str]              # one label per pile
    term_stability: dict[str, float] = {}  # item -> fraction of runs in which item is in same pile as centroid
```

**Affected files:** `apps/dashboard/src/components/PileComparison.tsx` (new), `apps/dashboard/src/components/VizSwitcher.tsx`, `DESIGN_SYSTEM.md`, `packages/cdb_core/cdb_core/schemas.py`, `docs/DATA_DICTIONARY.md`

**Acceptance criteria:**
- At least 2 models shown side-by-side with their pile structures
- Pile labels visible
- Divergent term placements highlighted
- Stability indicator present (R10)
- ReadAsTableToggle for accessibility

---

### T10 — Dashboard: Cultural centrality display

**One-line:** New React component (or section within an existing view) that displays the per-model cultural centrality scores already computed in `DomainResult.cultural_centrality_scores`.

**Dependencies:** None beyond the existing published data. Can proceed fully in parallel.

**Implementation notes:**
- Data already exists in the domain JSON (the field is populated by `pipeline.py` and serialized by `build.py`).
- Display as a ranked bar chart: models ordered by centrality score, horizontal bars.
- Negative-centrality models (if any) highlighted distinctly per the `negative_centrality_flag`.
- Tooltip explains what centrality means in this context (closeness to the group's dominant categorical structure, not "correctness").

**R10 compliance:** Cultural centrality scores are derived from the eigendecomposition of the similarity matrix. Bootstrap CI is available from the same bootstrap that produces model-level MDS ellipses (the similarity matrix is recomputed per iteration). Add error bars on centrality scores from bootstrap distribution. This requires a small extension to `bootstrap.py` (T4-adjacent but independent — can be done as part of T10 since it uses the same bootstrap runs that already exist).

**UI/UX review required:** YES — new component type (ranked bar chart with error bars).

**CDA SME review required:** YES — the interpretation copy that accompanies centrality scores must avoid framing centrality as "correctness" or "competence." Per SME_REVIEW.md §1.5, the term is "cultural centrality" (Caulkins 1999), not "competence." Dashboard copy must reflect this.

**Affected files:** `apps/dashboard/src/components/CentralityChart.tsx` (new), `apps/dashboard/src/components/VizSwitcher.tsx`, `DESIGN_SYSTEM.md`, possibly `packages/cdb_analyze/cdb_analyze/bootstrap.py` (centrality CI)

**Acceptance criteria:**
- All models displayed with centrality scores
- Error bars present (R10)
- Negative centrality flagged if present
- Tooltip copy avoids "competence" framing
- ReadAsTableToggle for accessibility

---

## S5 Schema Changes Summary

All schema changes require Architect sign-off and `DATA_DICTIONARY.md` co-update per CLAUDE.md §6 rule 6.

| Field | Location | Type | Breaking? |
|---|---|---|---|
| `term_mds_coordinates` | `DomainResult` | `dict[str, tuple[float, float]]` | No (new optional, default `{}`) |
| `term_mds_items` | `DomainResult` | `list[str]` | No (new optional, default `[]`) |
| `term_mds_uncertainty` | `DomainResult` | `dict[str, BootstrapEllipse]` | No (new optional, default `{}`) |
| `term_cluster_linkage` | `DomainResult` | `list[list[float]]` | No (new optional, default `[]`) |
| `term_cluster_assignments` | `DomainResult` | `dict[str, int]` | No (new optional, default `{}`) |
| `term_cluster_labels` | `DomainResult` | `list[str]` | No (new optional, default `[]`) |
| `term_cluster_au_pvalues` | `DomainResult` | `list[float]` | No (new optional, default `[]`) |
| `centroid_piles` | `DomainResult` | `dict[str, CentroidPileData]` | No (new optional, default `{}`) |
| `CentroidPileData` | New model in `cdb_core/schemas.py` | See T9 | No (new type) |

All additions are optional with defaults. No breaking changes. No removal or rename of existing fields.

---

## S6 CDA SME Review Required: YES

**Reason:** This plan touches multiple methodologically significant decisions:

1. **Pooling strategy for the cross-model term co-occurrence matrix (T1):** Equal weight per run vs. equal weight per model vs. OCI-weighted. Directly impacts the shape of the term MDS.
2. **AHC linkage method (T3):** Ward vs. average vs. complete linkage for term clustering. Different methods produce different dendrograms from the same data.
3. **Distance metric for AHC (T3):** 1-cooccurrence vs. Jaccard distance vs. other options.
4. **Bootstrap resampling unit for term uncertainty (T4):** Resample runs with replacement, or models with replacement, or both?
5. **AU p-value computation for dendrogram branch stability (T7):** Standard multiscale bootstrap (Shimodaira 2002) or simpler run-resample proportion?
6. **Cluster label aggregation method (T5):** Majority-vote across model centroid labels, or frequency-weighted, or some other method?
7. **Cross-model pile comparison framing (T9):** How to present structural divergence without importing "one model is more correct" framing. Must align with §1.5 (no model is a ground truth; divergence is a finding, not a failure).
8. **Cultural centrality copy (T10):** "Centrality" not "competence" per Caulkins 1999. Dashboard copy must be SME-approved.

The plan should be posted to `#lsb-cda-sme` for review on all four axes: protocol validity (the pooling and bootstrap decisions), analytical validity (AHC parameters, AU p-values), claims validity (how these visualizations are framed), and audience translation (copy that accompanies each new view).

---

## S7 UI/UX Review Required: YES

**Reason:** Four new component types that `DESIGN_SYSTEM.md` does not yet cover:

1. **Term MDS Plot** (labeled scatter with cluster regions and per-term ellipses)
2. **Dendrogram** (hierarchical tree with AU confidence values)
3. **Pile Comparison** (multi-column categorical comparison)
4. **Centrality Chart** (ranked horizontal bar chart with error bars)

The UI/UX agent must specify visual treatment, interaction patterns, mobile layout, and WCAG AA compliance for each before the Coder begins frontend work. However, per the pipeline order, UI/UX review happens after CDA SME PASS on the methodology decisions.

---

## S8 Dependency Order and Delivery Sequence

**Critical path for first new viz on screen:**
```
T1 -> T2 -> T4 -> T5 -> T6 (Term MDS visible)
```

**Parallel tracks:**
- T3 (AHC) can start after T1, runs parallel to T2/T4
- T9 (Pile Comparison) has no T1-T4 dependency; can proceed in parallel from day one
- T10 (Centrality) has no T1-T4 dependency; can proceed in parallel from day one

**Recommended execution order for maximum incremental value:**
1. **Batch 1 (analysis layer):** T1, T2, T3, T4 — all cdb_analyze changes; single CDA SME gate
2. **Batch 2 (publish + parallel frontend):** T5 (publish layer), T10 (centrality — already has data), T9 (pile comparison — data from T5)
3. **Batch 3 (main frontend):** T6 (term MDS), T7 (dendrogram), T8 (cluster labels)

The fastest path to a visible new viz on cogstructurelab.com is:
- T10 (cultural centrality) — data already exists, no new analysis needed, only a frontend component. Could ship in 1 task.
- T9 (pile comparison) — needs T5 for publish artifact, but raw data already exists.

---

## S9 R10 Compliance Plan (Uncertainty in Each New Viz)

| Visualization | Uncertainty mechanism | Implementation |
|---|---|---|
| Term MDS (T6) | Per-term bootstrap confidence ellipse | Computed in T4; rendered as translucent ellipses or radii |
| Dendrogram (T7) | AU p-values on branch nodes | Computed in T4 extension; rendered as numeric annotation + dashed lines for unstable branches |
| Pile Comparison (T9) | Per-term pile stability (fraction of runs in same pile) | Computed from raw runs; rendered as opacity or asterisk |
| Centrality Chart (T10) | Bootstrap CI on centrality score | Computed from existing bootstrap iterations; rendered as error bars |

No visualization ships without its uncertainty mechanism implemented.

---

## S10 What the Reviewer and Tester Should Verify

**Reviewer checks:**
- No LLM imports in `cdb_analyze` (boundary rule)
- Schema changes carry matching `DATA_DICTIONARY.md` updates (rule 7)
- No forbidden vocabulary in any dashboard copy
- No point estimates without uncertainty in any new viz (R10)
- Publish layer does not write to `data/raw/` (boundary rule)
- Dashboard does not import any `cdb_*` Python package (boundary rule)

**Tester checks:**
- All new `cdb_analyze` functions have unit tests with fixtures from `tests/fixtures/`
- No real API calls in tests
- Frontend components have vitest coverage
- `npm run build && npm run test && npm run lint` passes
- `uv run pytest && uv run ruff check . && uv run mypy packages/` passes

---

## S11 Reading List for Coder

Before starting any task in this phase, the Coder must read:

1. `ARCHITECTURE.md` — especially §4.2 (analysis layer), §4.2.6 (bootstrap), §4.5 (frontend), §3.2 (schemas)
2. `CLAUDE.md` — §6 (binding rules), §7 (forbidden vocabulary), §9 (pitfalls)
3. `DESIGN_SYSTEM.md` — current component inventory, tokens, §7 (accessibility)
4. `docs/DATA_DICTIONARY.md` — before any schema change
5. `docs/BOOTSTRAP_DESIGN.md` — before T4 (bootstrap extension)
6. `docs/SME_REVIEW.md` — §1.5 (cultural centrality terminology), §2.1 (salience)
7. `packages/cdb_analyze/cdb_analyze/cooccurrence.py` — before T1
8. `packages/cdb_analyze/cdb_analyze/mds.py` — before T2
9. `packages/cdb_analyze/cdb_analyze/cluster.py` — before T3
10. `packages/cdb_analyze/cdb_analyze/bootstrap.py` — before T4

---

## S12 Mark's Decisions (2026-05-24)

1. **Execution priority:** Ship T10 (centrality) and T9 (pile comparison) first as quick wins, then build the co-occurrence pipeline (T1-T4), then the remaining frontend (T5-T8). Confirmed.

2. **VizSwitcher tab capacity:** Open — to be decided during UI/UX review for T6/T7/T9/T10.

3. **Per-model vs. pooled term MDS display default:** Open — to be decided during UI/UX review for T6.

4. **Radial layout:** Mark: "not sure we care about the radial layout." Dropped from plan (not deferred to 9b). Comparison MDS with links (Priority 8) and consensus factor plot (Priority 7) remain deferred to Phase 9b.

---

*End of Phase 9a kickoff. Route to `#lsb-cda-sme` for methodological review on the eight decisions enumerated in S6 before any task reaches the Coder.*
