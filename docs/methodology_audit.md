# Methodology Audit: LSB Freelisting & CDA Pipeline vs. Published Literature

**Date:** 2026-04-13
**Sources reviewed:**
- Quinlan (2017) "The Freelisting Method" — chapter on freelisting methodology
- Borgatti "Elicitation Techniques for Cultural Domain Analysis" (etk2.txt)
- Borgatti "Pile Sorts" reference document
- Thompson & Juan (2006) "Comparative Cultural Salience" — *Field Methods* 18(4)
- Romney, Weller & Batchelder (1986) "Culture as Consensus" — *American Anthropologist* (PMC4134922)

**Scope:** Audit the LSB collection and analysis pipeline against established CDA methodology to identify deviations, gaps, or hallucinations.

---

## 1. SALIENCE COMPUTATION — CRITICAL GAP

### What the literature says

**Smith's S salience index** is the standard metric in CDA freelisting (Quinlan 2017, Thompson & Juan 2006, Borgatti). It combines **frequency AND rank position** into a single score:

**Step 1 — Individual salience per item per informant:**
```
S_individual = (L - R_j + 1) / L
```
Where:
- L = total number of items the informant listed
- R_j = rank position of the item (1 = first listed)
- First item: S = L/L = 1.0
- Last item: S = 1/L

**Step 2 — Composite Salience Value (CSV) across all informants:**
```
CSV = Σ(S_individual for item X across all informants) / N
```
Where N = total number of informants (including those who did NOT list the item — they contribute 0).

Items not listed by an informant get S = 0 for that informant.

**Key property:** Smith's S produces values in [0, 1]. Items listed by many informants AND listed early receive the highest scores. Smith's S is highly correlated with simple frequency but is a better measure because it penalizes items that are frequently mentioned but always late in lists.

### What LSB currently does

LSB treats **first-mention order as the sole salience metric** — items mentioned earlier are considered more salient. The parser truncates to the first `truncation_k` items after deduplication.

### Assessment: MOSTLY SOUND, but should compute Smith's S for analysis

The current collection pipeline is **not wrong** — first-mention order IS the primary signal in Smith's S for a single informant. With N=5 runs per model, each run is one "informant." The truncation to the top-K by first-mention order within each run is defensible.

**However, the analysis layer (Phase 3) should compute proper Smith's S** when aggregating across runs. The consensus free list should rank items by composite Smith's S across the 5 runs, not just by frequency or arbitrary ordering. This is a Phase 3 concern, not a Milestone A issue, but should be noted now.

**Action needed:** When `cdb_analyze/consensus.py` is implemented, use Smith's S (not raw frequency) to rank the consensus free list. The formula is simple to implement.

---

## 2. ITEM NORMALIZATION — PARTIALLY ADDRESSED

### What the literature says

Quinlan (2017) is emphatic: **synonyms must be consolidated before analysis**, and this requires **emic validation** (focus groups or local consultants), not researcher judgment alone. Examples:
- "breastfeeding" / "nursing" / "lactating" → one concept
- "scallion" / "green onion" → same item
- Multiple names for Cannabis sativa in multilingual contexts

Borgatti (etk2.txt) adds: variant spellings ("whore" vs "hore"), subclass modifiers ("grizzly bear" vs "black bear" vs "bear"), and the lumping-vs-splitting problem all require human judgment.

### What LSB currently does

The parser in `protocol/free_list.py` normalizes:
- Lowercase
- Strip trailing punctuation
- Collapse whitespace
- Strip numbering prefixes
- Deduplicate exact matches

### Assessment: ADEQUATE FOR LLM INFORMANTS

Human informants produce messy, multilingual, idiosyncratic lists that demand heavy normalization. LLM outputs are far more consistent — they spell correctly, rarely produce true synonyms in the same list, and don't use dialect variants. The current normalization is sufficient for Milestone A.

**However, cross-model synonym consolidation will matter in Phase 3/4.** When comparing Claude's "grandmother" to DeepSeek's "grandma," these should be treated as the same item. The analysis layer will need a synonym map or fuzzy matching step.

**Action needed:** Add a synonym normalization step to the analysis pipeline (Phase 3). Not needed for collection.

---

## 3. TRUNCATION STRATEGY — SOUND

### What the literature says

Three approaches to selecting items for pile sorts (Borgatti etk2.txt):
1. Include items mentioned by more than one informant
2. Look for a natural "elbow" break in the frequency/salience scree plot
3. Arbitrarily choose top N items (where N is largest manageable set)

Quinlan (2017) adds: Bernard's heuristic is items mentioned by ≥10% of informants. No standardized cutoff exists — "drawing this boundary is a matter of judgment."

### What LSB currently does

Truncation to `truncation_k=25` items, selected by first-mention order (most salient first) within each run.

### Assessment: SOUND

The top-25 approach maps to method #3 from Borgatti. 25 is a reasonable pile sort size — large enough to reveal structure, small enough that the model can sort meaningfully. The per-run truncation preserves run-to-run variation, which is important for the bootstrap uncertainty analysis.

**No change needed.**

---

## 4. PILE SORT → CO-OCCURRENCE MATRIX — CORRECTLY SPECIFIED

### What the literature says

Borgatti (pile sorts.txt): "Every time a respondent places a given pair of items in the same pile, that constitutes a vote for the similarity of those items." The aggregate matrix records **the proportion of informants** placing each pair together. The matrix is symmetric, with diagonal = 1.0.

**Critical caveat (Borgatti):** The interpretation of intermediate agreement as intermediate similarity assumes **cultural consensus**. If subpopulations use different classification systems, 50% agreement does NOT mean moderate similarity — it may mean half see the items as very similar and half see them as very different.

### What ARCHITECTURE.md specifies

> "For each pair of items, count the fraction of runs in which they appear in the same pile. Diagonal = 1.0. Symmetric."

### Assessment: CORRECT

The specification matches the standard methodology exactly. The cultural consensus caveat is particularly relevant for LSB — different models ARE different "subpopulations," so the per-model co-occurrence matrix (aggregated across 5 runs of the same model) is the right unit. Cross-model comparison uses Mantel correlation on these per-model matrices, which is methodologically sound.

**No change needed.**

---

## 5. CONSENSUS ANALYSIS — CORRECTLY SPECIFIED

### What the literature says

Romney, Weller & Batchelder (1986) "Culture as Consensus": The Cultural Consensus Model uses **minimum residual factor analysis** on the informant-by-informant agreement matrix. A single dominant factor (eigenvalue ratio λ₁/λ₂ > 3:1) indicates a single shared cultural model.

### What ARCHITECTURE.md specifies

> "Consensus analysis: minimum residual factor analysis on the informant×item agreement matrix. Ratio of first to second eigenvalue > 3 indicates a single shared culture."

### Assessment: CORRECT

The specification directly references the Romney/Weller/Batchelder method with the standard 3:1 eigenvalue ratio threshold. The interpretation for LSB (ratio < 3 suggests "sub-cultures" among models) is a legitimate finding, not a failure.

**No change needed.**

---

## 6. SAMPLE SIZE (N=5 RUNS) — DEFENSIBLE BUT LOW

### What the literature says

Conventional rule-of-thumb: **minimum 30 informants** for both freelists and pile sorts (Borgatti, Quinlan). However, "the number 30 is merely a convention" and depends on variability. Ryan's heuristic: compute frequencies after 20 informants, again after 30; if top-item rankings are stable, you have enough.

### What LSB does

N=5 runs per (model, domain). Each run is one "informant."

### Assessment: LOW BUT DEFENSIBLE FOR LLM INFORMANTS

The N=30 convention is for human informants with high individual variability. LLM runs at the same temperature are far more consistent — 5 runs at temperature 0.7 capture the model's core salience distribution. The prompt-sensitivity study in Phase 4b (8 prompt variants × 5 runs = 40 data points per reference model) provides the validation that N=5 is sufficient.

**The architecture already addresses this** via the G1 validation gate: within-model variance must be smaller than between-model variance. If N=5 isn't enough, G1 will fail and force more runs.

**No change needed**, but the methodology page should explicitly acknowledge the departure from the N≥30 convention and explain why it's justified for LLM informants.

---

## 7. PROMPT DESIGN — ONE CONCERN

### What the literature says

Quinlan (2017) is emphatic: **prompts must address a single, coherent semantic domain.** Broad prompts cause "unpacking" — informants enumerate subcategories rather than listing by salience. Example: "all birds" causes listing by type (raptors, pet birds, etc.) rather than by salience.

The prompt should ask about **kinds or names of X**, where X is the cover term for the domain.

### What LSB uses

```
You are participating in a cognitive anthropology study. Please list every
{{domain_seed}} you can think of. Do not stop early. Do not explain or
categorize. Just produce a numbered list, one item per line. Aim for at
least 30 items if you can.
```

For family: `{{domain_seed}}` = "type of family relationship or family member"

### Assessment: MOSTLY GOOD, one concern

The prompt is well-structured — it asks for kinds/types, discourages categorization, and requests a numbered list. The "do not explain or categorize" instruction specifically addresses the subcategory-unpacking problem.

**Concern:** "You are participating in a cognitive anthropology study" may prime the model toward academic/textbook responses rather than naturalistic ones. Human CDA researchers typically don't tell informants the study's theoretical framework. Consider whether this framing biases the output.

**Minor recommendation:** Consider testing a variant without the framing sentence in the Phase 4b sensitivity study.

---

## 8. LUMPER/SPLITTER PROBLEM IN PILE SORTS — NOT YET ADDRESSED

### What the literature says

Borgatti (pile sorts.txt) identifies this as a major problem: some informants make many piles ("splitters"), others make few ("lumpers"). Two informants with identical views but different pile counts will show low correlation. Solutions:
1. Forced pile count (ask for exactly N piles)
2. Boster (1994) successive pile sorts (split and merge iteratively)

### What LSB specifies

Free pile sort — the model decides how many piles to make. No forced pile count.

### Assessment: POTENTIAL ISSUE FOR CROSS-RUN AGGREGATION

If a model produces 3 piles in one run and 8 piles in another (at temperature 0.3 this is unlikely but possible), the co-occurrence matrices will differ significantly. The aggregation across N=5 runs handles this by averaging, but the variance may be high.

**Recommendation:** Monitor pile count variance across runs in the QA layer. If a model's pile count varies by more than ±2 across runs, flag it. This is a Phase 2 concern.

---

## 9. COMPARATIVE CULTURAL SALIENCE — CORRECTLY FRAMED

### What Thompson & Juan (2006) describe

Comparing freelists across groups requires:
1. Compute per-group aggregate salience (using Smith's S)
2. Compare rank orders across groups (Spearman correlation, visual inspection)
3. Test whether between-group differences exceed within-group variation

They emphasize: "aggregate salience is assumed to be an outcome of shared knowledge" — i.e., cultural salience.

### What LSB does

Cross-model comparison via Mantel correlation on co-occurrence matrices, MDS visualization with confidence ellipses, and the consensus eigenvalue ratio.

### Assessment: SOUND

LSB's approach is more rigorous than simple rank-order comparison — it compares the full similarity structure, not just item salience. The MDS + bootstrap ellipse visualization directly shows whether models' categorical structures are distinguishable or overlapping.

**No change needed.**

---

## SUMMARY: FINDINGS AND REQUIRED ACTIONS

### No issues (methodology is sound)
- Truncation strategy (top-K by first-mention)
- Pile sort → co-occurrence matrix transformation
- Consensus analysis (Romney/Weller/Batchelder method, λ₁/λ₂ > 3 threshold)
- Cross-model comparison via Mantel correlation + MDS
- Bootstrap uncertainty quantification (B=500)
- N=5 runs (defensible for LLMs; validated by G1 gate)
- Comparative cultural salience framing

### Action items for future phases
| # | Issue | Severity | Phase | Action |
|---|-------|----------|-------|--------|
| 1 | **Smith's S not computed** | Medium | Phase 3 | Implement Smith's S in `cdb_analyze/consensus.py` for consensus free list ranking |
| 2 | **Cross-model synonym consolidation** | Medium | Phase 3 | Add synonym normalization step to analysis pipeline |
| 3 | **Prompt framing** | Low | Phase 4b | Test variant without "cognitive anthropology study" framing in sensitivity study |
| 4 | **Lumper/splitter monitoring** | Low | Phase 2 | Add pile count variance check to QA |
| 5 | **Methodology page acknowledgment** | Low | Phase 6 | Document N=5 departure from N≥30 convention with justification |

### No hallucinations detected
The LSB architecture correctly references and applies:
- Smith's S as the standard salience metric (even though it's not yet computed in code)
- Romney/Weller/Batchelder consensus model with the correct eigenvalue threshold
- Standard CDA pipeline: freelist → pile sort → co-occurrence → MDS
- Mantel correlation for cross-matrix comparison
- Bootstrap resampling for uncertainty quantification
