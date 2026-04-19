# LSB — SME Review: Recommendations and Instructions for Claude Code

**Reviewer:** External SME, cognitive / quantitative / cultural anthropology
**Date:** 2026-04-19
**Status:** Authoritative — implement before first official collection run unless explicitly deferred
**Companion project:** Classical CDA Workbench (independent reference pipeline, built in parallel)

---

## Project Framing — Do Not Lose This

LSB is **not** a benchmark of how well AI approximates human cultural cognition.
It is a **longitudinal measurement instrument** for characterizing the categorical
structure of successive generations of language models, using CDA protocols as
the measurement apparatus.

The correct scientific comparison axis is **AI to future AI**:
- World model architectures vs. transformer next-token prediction
- Neurosymbolic systems vs. purely statistical models
- Pre-RLHF vs. post-RLHF versions of the same model family
- Dense models vs. mixture-of-experts at equivalent parameter counts
- Models trained on different corpus compositions

Human baselines are **contextual reference points**, not the target of measurement.
Using human data as a card deck source would pull results toward human norms,
which is not the research question. The research question is how LLMs differ from
each other and from future architectures.

This framing must be preserved in all documentation, dashboard copy, and
generated lede text. The forbidden vocabulary (§1.5.4 of ARCHITECTURE.md) exists
in service of this framing.

---

## Part 1 — Implement Before First Official Collection Run

These are binding. The SME will not sign off on a public data release without them.

---

### 1.1 Raise the Romney Consensus Threshold

**Current:** λ₁/λ₂ > 3.0 (classic Romney-Weller-Batchelder 1986 threshold)
**Required:** λ₁/λ₂ > 5.0 as the operational gate; report 3.0 for cross-study comparability

**Reason:** The RWB threshold was calibrated on human informant data with n = 20–40
informants and Q = 20–40 items. LSB runs at n = 12 models × 5 runs = 60 informants
(or n = 12 if treating models rather than runs as informants). With n = 12,
eigendecomposition of the agreement matrix has higher sampling variance — ratios > 3
occur by chance more frequently than with n = 30. Newer Bayesian CCT implementations
(Anders & Batchelder 2015) suggest the threshold for high-confidence single-consensus
detection should be closer to 5.0 in small-n regimes.

**Implementation:**
```python
# In packages/cdb_analyze/cdb_analyze/gates.py
G2_THRESHOLD_OPERATIONAL = 5.0   # gate pass/fail
G2_THRESHOLD_CLASSIC     = 3.0   # reported for cross-study comparability
G2_WARNING_ZONE          = (3.0, 5.0)  # passes classic, warn on operational

# In DomainResult schema — add:
"romney_eigenratio":         float,
"romney_threshold_classic":  3.0,
"romney_threshold_lsb":      5.0,
"romney_consensus_pass":     bool,   # based on 5.0
"romney_consensus_warning":  bool,   # True when 3.0 < ratio < 5.0
```

**In generated lede text:** When eigenratio is 3.0–5.0, the lede must state
"weak consensus" not "consensus." When < 3.0, report the domain type
(see §1.6 on low-consensus typology).

---

### 1.2 Confirm Mantel Permutation Test Is Implemented

**Current (per briefing):** "Mantel-style correlation between two models'
co-occurrence matrices on the shared item set, rescaled to [0, 1]."

**Required:** The full permutation-based Mantel test — not just the r coefficient.
The r alone is a descriptive statistic. The G2 gate claim ("model similarity
distinguishable from random") requires an inferential test with a p-value.

**Implementation:**
```python
# In packages/cdb_analyze/cdb_analyze/cooccurrence.py
def mantel_test(mat_a, mat_b, n_permutations=999, seed=42):
    """
    Permutation-based Mantel test.
    Returns: {r: float, p_value: float, n_permutations: int}
    p_value = proportion of permuted r >= observed r.
    Use upper triangle only (excluding diagonal).
    """
```

**Note:** The classical CDA workbench (`compare/diff.py :: mantel_test`) has a
verified implementation. Claude Code may reference it directly.

---

### 1.3 Compute G1 Stability Separately for Salience and Spatial Structure

**Current:** G1 computes a single within/between variance ratio.

**Required:** Compute G1 separately for:
1. **Salience structure** — variance in Smith's S rank ordering across prompt variants
2. **Spatial structure** — Procrustes RMSE across prompt variants

**Reason:** It is possible for salience ranks to be stable while MDS spatial
structure is not, or vice versa. A single aggregate G1 masks this distinction.
If G1 fails globally but salience is stable, that is a more informative finding
than a binary fail.

**Implementation:**
```python
# In packages/cdb_analyze/cdb_analyze/sensitivity.py
def compute_g1_stability(runs_by_variant):
    return {
        "salience_stability":  _within_between_ratio_salience(runs_by_variant),
        "spatial_stability":   _within_between_ratio_spatial(runs_by_variant),
        "aggregate_stability": _within_between_ratio_aggregate(runs_by_variant),
        "g1_pass":             both_below_threshold(0.5),
        "g1_salience_pass":    salience_ratio < 0.5,
        "g1_spatial_pass":     spatial_ratio < 0.5,
    }
```

---

### 1.4 Add Adjusted Rand Index Alongside Standard Rand for G3

**Current:** G3 uses Rand index ≥ 0.70

**Required:** Report both Rand index and Adjusted Rand Index (ARI).
Gate on ARI ≥ 0.60 (ARI corrects for chance agreement; 0.60 on ARI ≈ 0.70 on Rand
for typical cluster sizes). Use ARI as the binding gate criterion.

**Reason:** Standard Rand index can be inflated by chance when cluster sizes are
unequal. ARI is the standard in modern cluster analysis literature and produces
a more conservative and defensible claim.

```python
from sklearn.metrics import adjusted_rand_score, rand_score
# Both available in sklearn — no new dependencies
```

---

### 1.5 Cultural Centrality / Competence Scores Per Informant Run

**Current:** Not implemented (listed as deferred in briefing).
**Required:** Implement before first official collection run.

**Reason:** The RWB framework's own internal validity check. A model run with
negative competence score systematically disagrees with the consensus and should
be flagged for review rather than silently contributing to the aggregate.
Negative scores are mathematically undefined in the CCM framework (Weller 2007).

**Implementation:**
```python
# In packages/cdb_analyze/cdb_analyze/consensus.py
def compute_competence_scores(agreement_matrix, informant_ids):
    """
    Eigendecomposition of agreement matrix.
    Loadings on first eigenvector, normalized to [0, 1].
    Per Caulkins (1999): label as 'cultural_centrality' not 'competence'
    to avoid implying objective correctness — critical for OSINT/applied use.

    Returns:
        centrality_scores: dict[informant_id -> float]
        negative_flag:     bool  (True if any score < 0)
        negative_runs:     list[informant_id]  (runs to flag for review)
    """

# In DomainResult schema — add:
"cultural_centrality_scores": dict[str, float],  # informant_id -> score
"negative_centrality_flag":   bool,
"negative_centrality_runs":   list[str],
```

**In QA_Runner:** Flag any run with negative centrality score. Do not discard
automatically — a consistently counter-consensus run is itself a finding.

---

### 1.6 Add Low-Consensus Domain Typology

**Current:** G2 is binary pass/fail.
**Required:** When eigenratio < 5.0, classify the domain rather than just failing.

Based on Caulkins & Hyatt (1999):

| Type | Condition | Meaning for LSB |
|---|---|---|
| `STRONG_CONSENSUS` | λ₁/λ₂ ≥ 5.0, all scores positive | Models converge on a single categorical structure |
| `WEAK_CONSENSUS` | 3.0 ≤ λ₁/λ₂ < 5.0, scores positive | Some convergence, not high-confidence |
| `SUBCULTURAL` | λ₁/λ₂ ≥ 3.0, negative scores present | Model families form sub-clusters |
| `TURBULENT` | λ₁/λ₂ < 3.0, scores positive | No dominant structure; may be unstable domain |
| `CONTESTED` | λ₁/λ₂ < 3.0, negative scores | Deep structural disagreement across models |

```python
# In packages/cdb_analyze/cdb_analyze/gates.py
ConsensusType = Literal[
    "STRONG_CONSENSUS", "WEAK_CONSENSUS",
    "SUBCULTURAL", "TURBULENT", "CONTESTED"
]

def classify_consensus(eigenratio, centrality_scores) -> ConsensusType:
    ...
```

**This is a first-class finding, not a failure state.** "CONTESTED" on a domain
means the models disagree structurally — that is information, not a pipeline error.

---

### 1.7 Capacity-Constrained Truncation as a Named Finding

**Current:** Context window failures are presumably treated as missing data or errors.
**Required:** Define a new truncation type and record it explicitly.

**Reason:** LLMs do not fatigue like humans. The natural list length for an LLM
(absent a ceiling prompt) is bounded by context window, not by cognitive exhaustion.
If a model's context window prevents it from completing a 500-item pile sort, that
is a structural constraint on categorical processing capacity — a finding about the
architecture, not a data quality problem.

**Implementation — add to InformantRecord schema:**
```json
{
  "truncation_type": "elbow | capacity | prompt_ceiling | context_window_exceeded",
  "truncation_n":    42,
  "max_possible_n":  null,
  "context_window_exceeded": false,
  "capacity_note":   "Model returned 487 items before context limit at step 2"
}
```

**Gate behavior:** `context_window_exceeded = true` is NOT a QA failure.
It is a finding. Record it. Include it in the published result.

---

## Part 2 — Add to the Analysis Layer (Cheap, High Value)

These do not block the first collection run but should be implemented before
the first public release.

---

### 2.1 Add Sutrop CSI Alongside Smith's S

**Rationale:** Smith's S variance is compressed by the prompt ceiling on list length.
Sutrop's CSI (`F / (N × mP)`) is more robust when list lengths vary — which they
will across models and across the no-ceiling experimental condition.

**Formula:**
```
CSI(item) = F / (N × mP)
  F  = frequency of mention across runs
  N  = total runs
  mP = mean position of the item across runs in which it appears
```

**Implementation:** The classical CDA workbench (`pipeline/salience.py`) has a
verified, tested implementation. Direct reference or port is acceptable.

**In DomainResult schema — add:**
```json
"sutrop_csi": [{"item": str, "csi": float}],
"salience_index_agreement": float  // Spearman rho between Smith's S and CSI rank order
```

If Smith's S and CSI rank orders diverge significantly (Spearman rho < 0.85),
flag this in QA — it indicates list-length variance is high enough to affect
the salience structure, which is worth noting.

---

### 2.2 Add Nolan Index for Cross-Model Comparison

**Rationale:** The Mantel-style correlation tests matrix structure. The Nolan Index
tests proportional frequency — how often each item is mentioned by each group,
not just whether it appears. Two models that both list "nuclear" and "extended" as
family terms but weight them 80%/20% vs 20%/80% look identical to Jaccard
but are captured by NI.

**Formula (Robbins 2023):**
```
NI = 1 - D
D  = sqrt(1/M × Σ(dᵢ)²)
dᵢ = pᵢ(model_a) - pᵢ(model_b)   // proportional difference for item i
M  = total unique items from both models (including zeros for non-mentions)
```

**Range:** 0 (completely different) to 1 (identical proportional distributions).
NI = 1 while Jaccard = 1 means identical item sets with identical mention rates.
NI < Jaccard means item sets overlap but emphasis differs — common in cross-model comparison.

**Implementation:** The classical CDA workbench (`compare/diff.py :: nolan_index`)
has a verified implementation including the optional sample-size correction
(R-correction, equations 4–6, Robbins 2023).

**In DomainResult schema — add:**
```json
"cross_model_nolan": {
  "model_a": str,
  "model_b": str,
  "NI": float,
  "jaccard": float,
  "NI_vs_jaccard_delta": float
}
```

Compute pairwise NI for all model pairs. The NI matrix is then a complement to
the Mantel matrix correlation — structure vs. emphasis.

---

### 2.3 Add Pile-Label Consistency Measure

**Rationale:** The pile interview step (pile labels) is the most architecturally
sensitive part of the LSB protocol. A transformer trained on text will tend toward
linguistically conventional category names. A world model may produce spatial or
functional labels. A neurosymbolic system may produce formal predicates. This
difference is a primary discriminator for the future-AI comparison axis.

Currently, pile labels are collected but not analyzed as a structured measure.

**Required measure: within-model label consistency**
Across N runs of the same model, how consistently does the model assign the
same (or semantically equivalent) label to the same cluster?

**Implementation approach:**
```python
def pile_label_consistency(runs: list[InformantRecord]) -> dict:
    """
    For each cluster (defined by majority-vote item membership across runs),
    compute: exact label match rate, semantic similarity of labels
    (use character n-gram overlap as the AI-free proxy — no embeddings).

    Returns:
        label_consistency_score: float  [0, 1]
        per_pile_consistency:    dict[pile_id -> float]
        modal_labels:            dict[pile_id -> str]  // most common label
    """
```

**Note on the AI-free constraint:** Do not use embedding similarity for label
comparison. Character n-gram overlap (Jaccard on trigrams) or normalized
edit distance are acceptable. Exact match rate is sufficient as a first measure.

---

## Part 3 — Protocol Design Decisions

These are research design recommendations that affect how data is collected,
not just how it is analyzed.

---

### 3.1 Run a No-Ceiling Free List Experiment

**Current protocol:** "aim for ≥ 30" — a ceiling borrowed from human CDA.

**Recommended:** Run a parallel experiment with no ceiling for 2–3 reference
models across 2–3 domains. Observe:
- Natural list length (where does the model stop, if it does?)
- Salience curve shape at N = 200, 400 items vs. N = 30
- Elbow position relative to total list length
- Whether the elbow is stable or domain-dependent

**Why this matters:** In human CDA, the elbow identifies where accessible semantic
memory runs out. In LLMs, it identifies where training corpus frequency drops below
a threshold. The elbow position relative to list length may itself be an
architectural discriminator — a measure of domain boundary sharpness that has no
human CDA equivalent. Do not assume the ≥ 30 ceiling is the right operating point
without empirical evidence from the no-ceiling condition.

**This experiment does not delay the main collection.** Run it on 2 models in
parallel as a methods validation study.

---

### 3.2 Treat Prompt Sensitivity Study as Primary Variance Mechanism

**Current framing (per briefing):** The 8-variant prompt sensitivity study is
described as a validity check.

**Revised framing:** It is the primary variance-generation mechanism for the
Romney CCM, and it will be the **only** variance mechanism available for
deterministic architectures (neurosymbolic systems, zero-temperature models).

**Implication:** The 8 variants are potentially too few for future-architecture
comparison. Design the variant set to span:
- Lexical paraphrase (current approach)
- Register variation (formal vs. colloquial framing)
- Structural variation (imperative vs. question form)
- Seed-word variation (different domain entry points)

Architectures that are robust to all four variant types show fundamentally different
stability properties than architectures that vary across lexical paraphrase alone.
This becomes a primary finding dimension when comparing transformer vs. world model
vs. neurosymbolic outputs.

---

### 3.3 Pile Sort Protocol Note for Future Architectures

When collecting from non-transformer architectures that may produce deterministic
outputs:

If N runs of the same model on the same prompt return identical pile sorts,
the agreement matrix is all 1s and the eigenratio is undefined. Protocol for this case:

1. Record it — zero-variance output is a finding about the architecture
2. Switch to variant-based "informants" (each of the 8 prompt variants = one informant)
3. If still zero variance, report `consensus_type = "DETERMINISTIC"` — a new
   category not in the classic RWB typology
4. Do not compute CCM eigenratio for deterministic outputs

Add `DETERMINISTIC` to the `ConsensusType` enum now, even though no current
model will trigger it. It signals that the framework is designed for the
comparison target, not just the current subject pool.

---

## Part 4 — Documentation Changes

These changes belong in `ARCHITECTURE.md`, the public methods page, and
the generated lede vocabulary.

---

### 4.1 The Methods Adaptation Table

Add this table to `ARCHITECTURE.md` §4 (analysis layer) and to the public
methods page. It is the clearest statement of what LSB is doing and why
it is methodologically legitimate rather than naive application of human methods
to a non-human subject:

| Human CDA assumption | LLM reality | LSB adaptation |
|---|---|---|
| List length bounded by memory fatigue | Unbounded; limited by context window | Protocol ceiling with capacity-truncation as a named finding type |
| N informants are independent agents | N runs are draws from same stochastic process | Prompt/temperature variation as variance source; CCM applied as convergence test, not assumption |
| Card deck independent of informants | Same entity class generates deck and sorts | Cross-model pooled deck; reflexivity treated as signal, not confound |
| Pile sort is physical manipulation | JSON output only | Pile count variance and pile-label consistency as structural proxies |
| Pile interview captures indigenous reasoning | Model labels its own piles | Pile labels as first-class architectural discriminator |
| Longitudinal = cross-cohort human study | Longitudinal = version drift within model family | Procrustes drift as new temporal measure |
| Consensus = shared cultural knowledge | Consensus = convergent representation | CCM applied as architectural test, not cultural validation |

---

### 4.2 Floor / Ceiling Claims Statement

Add to the public methods page — **this must be explicit, not implied:**

> Without a human baseline, LSB results establish inter-model agreement in
> categorical structure. They do not establish whether that agreement reflects
> the domain structure of any human cultural tradition.
>
> With a human baseline, LSB results can additionally locate model outputs
> relative to a specific human cultural consensus. Human baselines are
> contextual reference points, not the target of measurement.
>
> The primary scientific claim of LSB is comparative across model architectures
> and across time. Human comparison is secondary.

---

### 4.3 The Corpus Lens Definition Needs One More Layer

**Current definition:** "the latent categorical structure of a training corpus,
as refracted through a model's training and alignment pipeline, surfaced by
applying CDA elicitation protocols to the model as if it were an informant."

**Recommended addition:** Name the transformation layers explicitly so readers
understand what "corpus lens" means operationally:

> Layer 1: Co-occurrence patterns in the training corpus
> Layer 2: Compression and abstraction by pretraining (next-token prediction)
> Layer 3: Behavioral shaping by RLHF and constitutional fine-tuning
> Layer 4: Surface expression through temperature-sampled token generation
>
> LSB elicitation operates on Layer 4. What it reveals about Layers 1–3
> is inferential, not direct.

This does not weaken the construct — it clarifies what it claims and does not claim.

---

### 4.4 "The Mismatch Is the Finding" — Make This Prominent

The briefing's §7.10 states: "importing a methodology designed for cultural
informants into a system that encodes culture without experiencing it is itself
the research question."

This should appear **prominently in the methods page and dashboard**, not only in
internal documentation. It is the most intellectually honest and most scientifically
interesting framing of the project. Researchers who understand CDA will immediately
grasp what LSB is doing and why it is non-trivial. Researchers who don't will be
oriented by it.

Suggested placement: the first paragraph of the public methods page, before
any description of specific measures.

---

## Part 5 — Deferred (Phase 2 or Later)

Do not implement now. Keep on roadmap.

---

### 5.1 INDSCAL (Carroll & Chang 1970)

Three-way MDS that decomposes individual distance matrices into a shared group
space plus per-informant dimension weights. For LSB this would produce: each model
gets a weight on each MDS dimension, revealing which models drive which structural
axes. More informative than two-way MDS for the cross-architecture comparison goal.

**Requires:** Per-informant pile sort matrices (not pooled). Implement when
collection scale and data structure support it. The current pooled approach
is acceptable for v1.

### 5.2 Relational Class Analysis / Correlational Class Analysis

RCA (Goldberg 2011) and CCA (Boutyline 2017) detect whether informants share the
same relational structure — the same implicit schema — even when their surface
responses differ. For LSB this would reveal whether models that produce different
free lists nonetheless organize the domain with the same underlying logic.

**Requires:** Substantial implementation effort. The classical CDA workbench does
not yet implement this either. Phase 2 priority.

### 5.3 Expand Prompt Variant Set to 16+

The current 8 variants may be insufficient for the future-architecture comparison
axis (see §3.2). Expand to 16+ variants covering lexical, register, structural,
and seed-word variation. Phase 2 design decision.

---

## Quick Reference — Measure Source Table

| Measure | Classical CDA source | LSB module | SME status |
|---|---|---|---|
| Smith's S | Smith & Borgatti (1997) | `consensus.py` | ✅ Verified |
| Sutrop CSI | Sutrop (2001) | Not yet in LSB | ⚠️ Add before release |
| Data-driven elbow | LSB-adapted | `consensus.py` | ✅ Verified |
| Jaccard co-occurrence | Jaccard (1912) | `cooccurrence.py` | ✅ Verified |
| Nolan Index | Robbins (2023) | Not yet in LSB | ⚠️ Add before release |
| Mantel test (full) | Mantel (1967) | Confirm implementation | ⚠️ Verify |
| Classical MDS | Torgerson (1952) | `mds.py` | ✅ Verified |
| Bootstrap ellipses | Efron (1979) | `bootstrap.py` | ✅ Verified |
| Procrustes alignment | Schönemann (1966) | `mds.py` / `drift.py` | ✅ Verified |
| Romney CCM eigenratio | Romney et al. (1986) | `consensus.py` | ⚠️ Raise threshold to 5.0 |
| Cultural centrality | Caulkins (1999) | Not yet in LSB | ⚠️ Add before release |
| Low-consensus typology | Caulkins & Hyatt (1999) | Not yet in LSB | ⚠️ Add before release |
| Rand index | Standard | `gates.py` | ✅ Verified |
| Adjusted Rand index | Standard | Add to `gates.py` | ⚠️ Add before release |
| Pile-label consistency | LSB-adapted (no human CDA equiv.) | Not yet in LSB | ⚠️ Add before release |
| Capacity-constrained truncation | LSB-adapted (no human CDA equiv.) | Not yet in InformantRecord | ⚠️ Add before release |
| INDSCAL | Carroll & Chang (1970) | Not yet in LSB | 🕐 Phase 2 |
| RCA / CCA | Goldberg (2011); Boutyline (2017) | Not yet in LSB | 🕐 Phase 2 |

---

## Key References

All of the following have full entries in the classical CDA workbench
`REFERENCES.md`, which is the authoritative citation source for this project.

- Romney, A.K., Weller, S.C., & Batchelder, W.H. (1986). *American Anthropologist*, 88(2), 313–338.
- Weller, S.C. (2007). *Field Methods*, 19(4), 339–368.
- Caulkins, D. & Hyatt, S.B. (1999). *Field Methods*, 11(1), 5–25.
- Anders, R. & Batchelder, W.H. (2015). *British Journal of Mathematical and Statistical Psychology*, 68(1), 74–93.
- Smith, J.J. & Borgatti, S.P. (1997). *Journal of Linguistic Anthropology*, 7(2), 208–209.
- Sutrop, U. (2001). *Field Methods*, 13(3), 263–276.
- Robbins, M.C. (2023). *Journal of Ethnobiology*, 43(1), 12–18.
- Mantel, N. (1967). *Cancer Research*, 27(2), 209–220.
- Schönemann, P.H. (1966). *Psychometrika*, 31(1), 1–10.
- Goldberg, A. (2011). *American Journal of Sociology*, 116(5), 1397–1436.
- Boutyline, A. (2017). *Sociological Science*, 4, 353–393.

---

*This document should be kept in the LSB repo at `docs/SME_REVIEW.md` and*
*updated when the SME issues revised guidance. Claude Code should treat*
*recommendations marked ⚠️ as blocking for the first public data release.*
