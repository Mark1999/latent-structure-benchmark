---
name: phase9b-food-guard-trip
description: 2026-06-11 INVESTIGATE adjudication on Phase 9b food guard trip (T-1/T-5/T-6); 5 of 13 staged models have empty free-lists in the staged JSON, the WEAK_CONSENSUS flip is an artifact of consensus_freelist staging, not a real signal; live site stays up version-pinned during investigation; precise re-staging steps listed
metadata:
  type: project
---

## Phase 9b food-domain guard-trip adjudication (2026-06-11)

### ADJUDICATION: INVESTIGATE (not PROMOTE)

The STRONG -> WEAK flip on the food domain is an **artifact** of the staged
analysis, not real signal. The staged result JSON
(`out/rebaseline/food/0.2.json`) shows the Option A consensus free-list for
five of the thirteen slate models is the empty list `[]` with `raw_order: []`:

- `deepseek/deepseek-v3.2` (5/5 QA-passing runs reported by operator)
- `google/gemini-2.5-pro`        (5/5)
- `meta-llama/llama-4-maverick`  (2/5 thin)
- `mistralai/mistral-large-2512` (5/5)
- `x-ai/grok-4`                  (4/5)

Operator-reported QA counts are non-zero for 4 of those 5 (only llama-4-maverick
is thin at 2/5; the others are 4-5 of 5). An empty consensus free-list for a
model that has 4-5 QA-passing collection runs is **not** a substantive finding
about that model. It is a free-list aggregation / staging step that did not run
to completion for those rows. Probable causes (to be confirmed in
investigation): the consensus_freelist builder did not pick up the new
records (campaign / scope filter), or new-collection records did not land
under the `domain_slug` the aggregator queries, or an upstream ID-mapping
mismatch (`model_id` vs `model_version_returned`).

### Quantified rationale (load-bearing evidence)

**1. Similarity-matrix null-padding.** The staged
`similarity_matrix` shows rows/columns 0..3 entirely populated with the
Mantel-rescaled null value 0.5 (= "no shared structure"; ref. Phase 6 T5
SIMILARITY_NULL_VALUE binding). Models in those slots:
`claude-opus-4-5`, `claude-opus-4-6`, `claude-sonnet-4-6`,
`deepseek/deepseek-v3.2`. The three Claude models are PRIOR-slate members
that scored real similarities (in the 0.3..0.9 range with other models)
in the prior published 8-model result; their entire row collapsing to 0.5
in the new staging is not a finding about Claude, it is a staging-step
identity. The matrix sub-block over the other 9 models still contains
real similarities (e.g. gpt-5.4 to gpt-5.2 = 0.887, mistral-small to
gpt-5.2 = 0.869).

**2. Centrality numeric fingerprint.** Four models share the identical
centrality score `0.2681875585645402` to 16 decimal places:
`claude-opus-4-5`, `claude-opus-4-6`, `claude-sonnet-4-6`,
`deepseek/deepseek-v3.2`. Bit-identical centralities across genuinely
different models is the eigenvector of a row that is constant (the 0.5
row). This is the numerical fingerprint of the null-padded row, not a
substantive convergence finding.

**3. Eigenratio mechanics.** Romney CCM eigenratio is
lambda_1 / lambda_2 over the model-model agreement matrix. Replacing
the rows for 4 of 13 models with a constant value mixes the first factor
with the null sub-space and pulls lambda_1 toward the bulk while
inflating lambda_2 (mass that should belong to lambda_1 leaks into the
constant-row eigenmode). The 6.586 -> 4.159 drop is consistent with
this mechanism, not with a substantive shift in food-domain
categorical structure.

**4. Loadings interpretation.** "Which models load weakest on the first
factor" is not a usable diagnostic here because the four bit-identical
centralities sit in the middle of the distribution by construction; the
loading-rank does not separate "weak loader" from "constant row." The
genuine real-data loaders (the other 9 models) have centralities in the
0.260..0.302 range — a narrow band that, were the matrix complete,
might genuinely classify as WEAK by Romney CCM, but you cannot read
that conclusion off a staged matrix where 4 of 13 rows are degenerate.

**5. Cannot answer "with vs without llama-4-maverick" from staged JSON.**
The reasonable instinct ("recompute the eigenratio excluding the 2/5
thin model") cannot be done from the staged result alone because
maverick is one of the five empty-free-list rows. Even if its raw
records exist, the staged matrix does not have a substantive row to
include or exclude. Re-staging from raw is required before any
exclusion analysis is meaningful.

### N posture across the slate (separate concern, do not conflate)

5-runs-per-model is thin for Romney CCM at any classification, and the
domain's prior STRONG_CONSENSUS at 8 models x 5 runs is on the same
thin floor. `romney_small_n_warning: True` is already the operative
signal in BOTH the prior 8-model and the new 13-model staged results
(romney_small_n n<15 threshold per reconciled 2026-04-23 ruling).
That n-fragility is a real, standing methodological concern for the
food classification, separate from this guard trip. It should be
surfaced on the methodology page regardless of this adjudication's
outcome, but it is not the cause of the 6.586 -> 4.159 drop in the
staged numbers.

### Live-site interim state ruling: ACCEPTABLE (leave up)

Leaving the 8-model STRONG_CONSENSUS result live during investigation
is methodologically acceptable on the following grounds:

1. The prior result is **version-pinned**. `analysis_version: 0.1`
   over the 8-model slate remains reproducible from the open-data
   bundle and citable as the result-at-that-time. The runbook's
   "versioned DomainResults stay citable" invariant covers exactly
   this case.
2. The prior result is **not invalidated** by today's investigation.
   The 8-model classification was correctly computed on the data
   available at the time, under the documented n=5 small-n caveat.
   We have not yet shown the 13-model classification is what the
   data actually says (point 1-5 above); we have shown the staged
   computation is degenerate.
3. **Failures-are-findings does not apply here.** The staged
   degeneracy is a pipeline state, not a finding about model
   behavior. Surfacing a publication on degenerate staging would
   be a category error.
4. **Hard stop on the social pipeline.** The detect cron MUST NOT
   pick this up as a CLASSIFICATION_DRIFT or DIVERGENCE event;
   the staged result file must not flow into `manifest.json` or
   `data/results/`. The runbook Step 3 -> 5 gate is doing
   exactly its job here.

When the staged result is re-computed cleanly and either confirms a
real STRONG -> WEAK transition or shows the food classification holds,
the methodology page gets a footnote describing the 2026-06-11 widening
and the n=5 small-n posture. No live copy change is required during
investigation.

### INVESTIGATION STEPS (precise, ordered)

Re-route to Architect for execution. The CDA SME does not perform
these steps; the SME reviews the re-staged result.

1. **Verify raw-data presence (cheap, 5 min).** For each of the 5
   empty-free-list models, confirm food-domain free-list and
   pile-sort records actually landed in `data/raw/informants.jsonl`
   under the new campaign id. Use `scripts/lsb_inspect.py
   --model <model_id> --domain food` for each.
   Expected: non-zero QA-passing record counts matching the
   operator-reported numbers (deepseek 5, gemini-2.5-pro 5,
   mistral-large 5, grok-4 4, llama-4-maverick 2).

2. **Identify the staging failure mode.** If raw records exist,
   diagnose why the consensus_freelist builder produced `items: []`
   for these models. Suspect:
   - (a) `model_id` vs `model_version_returned` join key mismatch
     (pitfall #1) — the new collection may be writing
     `model_version_returned` strings the aggregator does not map
     back to the slate `model_id`,
   - (b) campaign / domain filter excluding the new records,
   - (c) builder querying a stale snapshot.
   Do not modify the staged file; reproduce the failure mode in
   isolation first.

3. **Re-stage food only, full corpus, pinned env.** After step 2
   fix lands, run `uv run python scripts/rebaseline_corpus.py
   --domain food` against the full corpus. Verify all 13 free-list
   `items` arrays are non-empty before reading any classification
   numbers off the result.

4. **Sensitivity analyses on the clean re-staged result** (CDA SME
   reviews; do not promote yet):
   - 4a. Recompute eigenratio with thin-model exclusion:
     drop `meta-llama/llama-4-maverick` (2/5 runs is below any
     defensible per-model floor for Romney CCM). Report eigenratio
     for the 12-model slate.
   - 4b. Optional: also drop `x-ai/grok-4` (4/5). Report
     eigenratio for the 11-model slate. This is a sensitivity
     bound, not a recommended slate.
   - 4c. Re-run with model-resample bootstrap B=500 over the
     clean 13-model slate and report the eigenratio CI. If the CI
     straddles 5.0, the classification is genuinely undetermined
     and the lede language must reflect that, not pick a side.

5. **Adjudication on the clean numbers** returns to the CDA SME.
   At that point either:
   - (A) the clean 13-model eigenratio is comfortably > 5.0 with
     CI not straddling -> NO classification change, no live copy
     change, the prior STRONG_CONSENSUS stands and the new
     slate refreshes the values silently at the next promotion,
     OR
   - (B) the clean 13-model eigenratio is genuinely in the
     3.0..5.0 band (WEAK) or straddles 5.0 -> real signal, the
     CDA SME drafts the replacement lede / classification copy
     at that point against actual numbers (not the degenerate
     staged ones), and Architect routes promotion through the
     standard gate. The SME does not pre-draft replacement copy
     against numbers that may not survive re-staging.

### Forward-carry caveats (regardless of outcome)

- N=5/model across the slate makes the food classification fragile
  at either side of the 5.0 boundary. The methodology page already
  needs to surface `romney_small_n_warning: True` on the food
  domain; this investigation does not change that.
- A clean re-staging in which 4 of 13 models still load identically
  to ~16 decimal places is itself a separate finding (would suggest
  a different upstream collapse). The SME flags this if it recurs.

### Status
- ADJUDICATION: INVESTIGATE
- Live site: leave 8-model STRONG_CONSENSUS up, version-pinned.
- Social pipeline: do NOT advance this staged result to
  `manifest.json` / `data/results/` / detect.
- Re-routed to: Architect (investigation steps 1-3); CDA SME on
  return for steps 4-5.

---

## ROUND 2 (2026-06-11): RE-ADJUDICATION ON CLEANER STAGING

### Round-1 hypothesis disposition

- Step-2 hypothesis (`model_id` vs `model_version_returned` join-key
  mismatch): **DISPROVEN.** The empty consensus free-lists in the prior
  staging were because the five new models then had only
  `cross_model_consensus` records (placeholder freelists by design of
  that mode), not a join-key bug. Operator re-collected in `single_pass`
  mode (campaign 2026-06-11); fresh records persist correctly in
  `parsed_items`. Confirmed by direct inspection of round-2 staged
  free_lists: 8 of 13 models now have substantive consensus free-lists
  (the 3 Claudes + the 4 newly single_pass-collected models + the 4
  prior-slate non-Claude models). Llama-4-maverick remains 0 QA-passing
  single_pass and sits in the slate via 2 QA-passing
  cross_model_consensus records only.

### Round-2 staged numerics

- `romney_eigenratio`: 6.586410170380379 (prior live) -> 4.447034058312089
  (round-2 staged). STRONG_CONSENSUS -> WEAK_CONSENSUS, warning flipped
  False -> True. Guards T-1, T-5, T-6 tripped again.
- Centrality bit-identity narrows from 4 models (round-1) to 3
  (round-2): the three Claudes share `0.26069072811802785` to the float
  ULP. The eigh degeneracy fingerprint is identical in mechanism, on a
  smaller set, exactly because deepseek now has substantive single_pass
  data.

### LOCALIZED MECHANISM (load-bearing)

The Claude-row nullification originates in
`packages/cdb_analyze/cdb_analyze/mds.py`
`compute_cross_model_similarity()` at L41-78, specifically:

1. **L41-44** (shared-items intersection). The function intersects
   `mat.items` across all 13 models:
   ```
   shared_items = set(matrices[0].items)
   for m in matrices[1:]:
       shared_items &= set(m.items)
   ```
2. **L70-73** (constant-vector NaN handler). When an upper-triangle
   vector has zero standard deviation, `np.corrcoef` returns NaN and the
   code rescues with `r = 0.0`, which then rescales to `(0 + 1) / 2 = 0.5`.

The mechanism that pushes Claude rows into the constant-vector path is
the interaction with
`packages/cdb_analyze/cdb_analyze/cooccurrence.py`
`build_cooccurrence_matrix()` at L91-102, the per-record item-source
fallback:
```
if r.freelist.parsed_items:
    all_items.update(r.freelist.parsed_items)
else:
    for pile in r.pile_sort.parsed_piles:
        all_items.update(pile)
```
A model's `mat.items` is the union of (a) its own free-list items from
its single_pass records and (b) the canonical cross-model card-deck items
from its cross_model_consensus records (which have placeholder empty
freelists, falling to the else-branch). This means the 13 per-model
`mat.items` lists are built from heterogeneous item sources:

- The three Claudes: single_pass only -> mat.items = own free-list union.
- Llama-4-maverick: cross_model_consensus only -> mat.items = canonical
  card-deck items only.
- The four mixed-mode new models (deepseek/gemini-pro/mistral-large/
  grok-4): mat.items = own free-list union UNION canonical card-deck
  items.
- The five legacy single_pass models: mat.items = own free-list union.

The intersection of these 13 heterogeneous item sets collapses to a small
subset of canonical card-deck items that the Claudes happened to also
list in their own free-lists. On that intersection, the Claude
per-model submatrix off-diagonal values are (near-)constant. Their
upper-triangle vector therefore has zero variance, so every Claude
pairwise correlation evaluates to NaN, gets rescued to 0, and rescales
to the 0.5 Mantel null. Every Claude row in the published
similarity_matrix collapses to constant 0.5 by construction.

The 2026-05-29 published result did not exhibit this collapse because
the slate was 8 single_pass-only models; the shared-items intersection
was constrained only by free-list overlap and the Claude submatrices on
that intersection had real variance.

The third site that lets this contamination propagate is
`packages/cdb_analyze/cdb_analyze/pipeline.py` at L468 (also
`scripts/rebaseline_corpus.py` L468), where `load_records()` is called
WITHOUT a `collection_mode` filter. The pipeline pulls every QA-passing
record regardless of mode, then groups by `model_id`, producing the
heterogeneous mixed-mode `records_by_model` that drives the failure.
A `collection_mode="single_pass"` filter (or an explicit
mixed-mode-aware item alignment policy) at load time would prevent the
mechanism entirely.

### Eigenratio trustworthiness: 4.447 is NOT clean

`romney_eigenratio` (`pipeline.py` L809-810) is computed on `sim_np` =
`np.array(similarity_matrix)`, which IS the staged matrix with three
constant Claude rows. The Romney CCM eigenratio is the dominant-factor
purity of the inter-model agreement matrix; three constant rows inject
a separate eigenmode (the constant-row indicator vector) that leaks mass
away from lambda_1. The 6.586 -> 4.447 drop is therefore a confound of
real signal (additional models loaded on factor 1) AND artifact
(constant-row null sub-space). It is not interpretable as a substantive
classification shift from STRONG to WEAK.

The 10x10 sub-block over the non-Claude models has substantive values
(0.21 to 0.89 range across pairs, gpt-5.4/gpt-5.2 = 0.887, mistral-large/
gemini-pro = 0.89, gpt-5.4-mini/grok-4 = 0.32). That sub-block is where
the answerable Romney eigenratio lives.

### Maverick slate membership: methodological flag, not disqualification

Llama-4-maverick sits in the slate via 2 QA-passing
cross_model_consensus records and zero single_pass records. The Romney
CCM informant model treats each model as one voice irrespective of how
many runs back it; maverick is therefore admissible at the slate level.
But maverick contributes only canonical-card-deck items to its mat.items
and therefore plays a non-symmetric role in the shared-items
intersection: it is mode-pure on the cross_model side, exactly the
asymmetry the Claudes sit on the other side of. Two QA records is also
thin per the per-model floor we apply for Romney inputs. The CDA SME
preference is **exclude maverick from the food slate for v0.2** as a
4a-style sensitivity bound: report the eigenratio with and without
maverick to bracket the effect of the mode-purity asymmetry.

### Sensitivity read on real signal

Genuine STRONG -> WEAK transition from collecting four new substantive
single_pass models is plausible a priori (more architectural diversity
in the slate widens the categorical-structure dispersion), but it
cannot be read off this staging. The 10x10 non-Claude block needs the
eigenratio recomputed on it directly before any STRONG/WEAK call can be
made; the centrality loadings on that sub-block need re-derivation
before "which models load weakest" is a usable diagnostic. Both
are sensitivity outputs, not promotable findings.

On the staged 13x13 contaminated loadings, the non-Claude centralities
fall in the band 0.244 to 0.310: mistral-large (0.245), gemini-pro
(0.250), grok-4 (0.274), gpt-5.4-mini (0.277), gemini-flash (0.284),
gpt-5.4 (0.289), gpt-5.2 (0.290), deepseek (0.292), mistral-small
(0.303), maverick (0.310). This rank ordering is not meaningfully
separable into weak/strong loaders because the constant-Claude rows
compress the spread; rank-order on the contaminated matrix is not
interpretable as factor-1 loading rank on the clean sub-block.

### DISPOSITION: PROMOTE-AFTER-FIX with separable scopes

Two SEPARABLE concerns, both must be resolved before promotion:

**Concern A (mixed-mode similarity contamination).** The Claude-row
nullification is a pure pipeline-level mechanism. The fix is mechanical:
either (a) filter at load time to a single coherent collection mode for
the similarity basis, (b) make the item set for similarity computation
use a single canonical reference (e.g., the cross-model card deck for
all models in mixed-mode domains), or (c) add explicit handling in
`compute_cross_model_similarity` that surfaces mode-asymmetry as a
diagnostic rather than silently producing 0.5 nulls. Architect chooses
the implementation; CDA SME preference is **(a) with a documented
scope-clause for mixed-mode domains**, because it preserves the
existing single-mode invariants on the legacy slates while making the
mixed-mode path explicit. Concern A is the file-scope deliverable to the
Coder.

**Concern B (genuine STRONG -> WEAK question).** Once Concern A is
resolved, the clean eigenratio either crosses 5.0 or does not. The CDA
SME does not pre-commit to either outcome before clean inputs exist.
The 4a/4b/4c sensitivity sweeps from round-1 still stand:
- 4a: drop maverick (mode-pure cross_model_consensus, 2 QA records),
  report eigenratio on 12 models.
- 4b: also drop the thinnest-single_pass new model (mistral-large at 3
  QA single_pass), report eigenratio on 11 models.
- 4c: model-resample bootstrap B=500 over the clean slate, report
  eigenratio CI. If the CI straddles 5.0, the classification is
  genuinely undetermined and the lede must reflect that.

### Live-site posture: UNCHANGED

Prior 8-model STRONG_CONSENSUS result stays live, version-pinned at
`analysis_version: 0.1`. Methodology page must surface
`romney_small_n_warning: True` regardless of round-2 outcome (carry
forward from round-1). Social pipeline detect MUST NOT pick up the
round-2 staged result; the manifest gate is doing its job.

### REVISED INVESTIGATION STEPS (for Architect)

1. **Concern A fix scope (Architect -> Coder).** Add a
   `collection_mode` constraint to the similarity basis for mixed-mode
   domains. Implementation locus suggested but not bound:
   `cdb_analyze.pipeline.run_pipeline()` accepts a
   `similarity_collection_mode` parameter; `compute_cross_model_similarity`
   is unchanged; `scripts/rebaseline_corpus.py` passes
   `similarity_collection_mode="single_pass"` for food when called for
   the food domain. Alternative implementations welcome; the
   methodological invariant the fix must achieve is: per-model
   `mat.items` must come from a coherent within-mode item source across
   the whole slate. Document the choice in DATA_DICTIONARY.md and the
   methodology page footnote for the food domain.

2. **Re-stage food only after fix.** Verify all 13 (or 12, after
   maverick exclusion) similarity_matrix rows have substantive values
   (no constant 0.5 rows). Verify the three Claude centralities now
   differ by more than float ULP.

3. **CDA SME re-adjudication on clean numbers.** SME runs 4a/4b/4c
   sensitivity and adjudicates STRONG_CONSENSUS hold vs WEAK_CONSENSUS
   transition against the clean numbers. Replacement lede language is
   drafted at that point only.

### Round-2 status
- ADJUDICATION: PROMOTE-AFTER-FIX (Concern A first, then sensitivity,
  then re-adjudication).
- Live site: unchanged, version-pinned.
- Social pipeline: continues blocked on staged result.
- Re-routed to: Architect (Concern A scope decision + Coder dispatch).
- Round-1 hypothesis (join-key mismatch) DISPROVEN and superseded.
