---
filed: 2026-05-12
reviewer: CDA SME agent (Opus)
task: Phase 6 T8 — Read-as-table toggle + ScreenReaderSummary
slack_channel: "#lsb-cda-sme"
verdict: PASS-WITH-NOTES
---

# Phase 6 T8 — CDA SME verdict on the Read-as-table + ScreenReaderSummary plan

**VERDICT: PASS-WITH-NOTES**

The Architect's plan is approved with binding wording fixes covering the
six orchestrator-routed surfaces: three ScreenReaderSummary templates, the
toggle button label, three table captions, two table-internal column-header
strings, and four empty-state caption strings. The Architect's structural
decisions (per-viz toggle, per-viz `useState`, programmatic templates over
lede regeneration, `display: none` + `aria-hidden` on the hidden viz, R10-
in-tables with column adjacency) are all methodologically and §1.5-clean
and are approved without revision.

The single load-bearing binding decision is **S5 (FreeList caption
cross-surface consistency)** — the FreeListTable caption MUST inherit T7's
binding wording verbatim, not paraphrase it. A reader who reads the bar-
chart caption ("Bar shows the fraction of this model's collection runs
that produced this term.") and then toggles to table mode and reads a
*paraphrased* caption about the same numeric field is being asked to
verify cross-surface equivalence in their head. Equivalent representations
should carry equivalent prose.

The three ScreenReaderSummary template specifications below are the
binding regression-test targets. Coder must implement the template
functions such that their outputs match these specifications byte-for-byte
on the published `family.json` and `holidays.json` fixtures. The §6
forbidden-vocabulary scan was applied to every LSB-authored string T8
introduces; only one soft-flag surfaced (S8 below), and it is non-blocking
under §2.1's structural decision.

T8 proceeds to UI/UX light-touch dispatch on this verdict. Coder dispatch
follows on UI/UX PASS / PASS-WITH-NOTES. The seven §5 carry-forward notes
are binding on the Coder during implementation; the Reviewer enforces.

---

## 1. Four-axis scorecard

| Axis | Verdict | Notes |
|---|---|---|
| Protocol validity | PASS | Each SR template accurately describes the protocol's output for its viz. MDS template says nothing the MDS does not encode (model count, `consensus_type`, R1-state distribution from `display.r1_states`). FreeList template says nothing the FreeList does not encode (selected-model count, term-count range from `sutrop_csi[modelId].length`, shared-term count). Similarity template says nothing the heatmap does not encode (pairwise count, similarity range, CI-includes-null count). No template synthesizes findings the visualization cannot express. None of the three templates leak protocol-stage details (free-list elicitation prompt, pile-sort interview transcript) that the viz layer does not render. The proposed per-viz placement (immediately after the existing `<h2 className="sr-only">` bridge, before any conditional toggle state) is correct — the summary is invariant to toggle state and should be DOM-present in both modes per §2.5. |
| Analytical validity | PASS-WITH-NOTES | The MDS template's "consensus type" report risks an overclaim if it renders the bare enum value (`STRONG_CONSENSUS` / `WEAK_CONSENSUS` / `TURBULENT` / `CONTESTED` / `SUBCULTURAL`) without disambiguation — a screen-reader user encountering "STRONG_CONSENSUS" in a prose sentence may read it as a property of the *models* rather than as the Caulkins-typology classification of the *between-model agreement matrix* (Register 2). S1 binding-wording fix maps the enum to plain-English Register-2 framing. The FreeList template's "term-count range" report is forbidden-vocab-clean as proposed; the bind is just to use precise numeric phrasing (S2). The Similarity template's "CI-includes-null count" report carries forward T5's binding terminology ("no shared structure" not "no agreement"); the bind is to make the cross-surface consistency mechanical (S3). None of the templates make a Register-1↔Register-2 conflation; none invoke RWB CCM language at the wrong register; none claim consensus *of models* where the statistic is consensus *across runs of one model*. |
| Claims validity | PASS-WITH-NOTES | §1.5.4 forbidden-vocab scan on every LSB-authored string T8 introduces (button label, three SR templates, three table captions, four empty-state captions, ~14 LSB-authored column-header strings) returns clean after S1–S5 are applied. The Architect's `"Read as table"` / `"Show visualization"` button labels are §1.5.4-compliant as proposed — APPROVED (S4 below). The three table captions need binding revision to match T5/T7 precedent vocabulary and to carry the first-class-state framing on `—` rows per §1.5.5 (S5, S6, S7). The empty-state captions are correctly first-class-state-framed in the Architect's draft (no "no data yet" / "pending" / "missing") — APPROVED with one minor word-order tightening (S8). |
| Audience translation | PASS-WITH-NOTES | A screen-reader user encountering the SR template prose **gets equivalent information to a sighted user examining the chart** once S1–S3 are applied: the MDS template names model count and consensus classification *with the Register-2 framing intact*; the FreeList template names model count, term-count scale, and shared-term count; the Similarity template names pairwise count, similarity range, and CI-includes-null count. A journalist quoting any of the three SR templates verbatim is quoting an accurate methodological statement, not a psychological-attribution sentence. The §1.5 corpus-lens framing is preserved at the template level — none of the three template bodies introduces "believes," "thinks," "worldview," "perceives," "sees," "agrees with," "thinks like," "understands," or "intends." The boundary with the existing `generated_lede` is clean per §6 (lede = per-domain prose finding for the article-header; SR template = per-viz structural summary). The two surfaces complement; they do not duplicate. |

**Register compliance: PASS** — the three templates respect the three-register framework. The MDS template uses Register 2 vocabulary (consensus type is a between-model classification); the FreeList template uses Register 1 vocabulary (term-counts are within-model output-distribution descriptors); the Similarity template uses Register 2 vocabulary (pairwise model-vs-model comparison). No RWB CCM language at Register 1; no OCI language used as a "consensus" claim; no Procrustes language at the wrong register. Clean.

**Vocabulary compliance: PASS-WITH-NOTES** (PASS after S1–S5 are applied). Scanned in §6 below.

---

## 2. Binding template wording — the three ScreenReaderSummary templates

These are the **binding template specifications**. The Coder implements the three template functions in `src/copy/screen_reader_summaries.ts` such that their outputs match these specifications byte-for-byte on the published `family.json` and `holidays.json` fixtures. The Reviewer's vitest snapshot tests assert byte-identity.

### 2.1. `mdsScreenReaderSummary` — binding output

**Template structure** (3 sentences):

```ts
export function mdsScreenReaderSummary(
  domainResult: DomainResultPublished,
  selectedModels: string[]
): string {
  const n_selected = selectedModels.length;
  const r1_states = domainResult.display?.r1_states ?? {};
  const n_low = selectedModels.filter(m => r1_states[m] === "low_concentration").length;
  const n_det = selectedModels.filter(m => r1_states[m] === "deterministic").length;
  const consensus_phrase = mapConsensusType(domainResult.consensus_type);
  // ... composition below
}
```

**Binding output sentences** (Coder composes from these fragments; verbatim wording on the variable-free portions):

**Sentence 1 — model count + map description:**
> `"This chart places ${n_selected} ${n_selected === 1 ? 'model' : 'models'} on a two-dimensional map according to how their outputs categorize this domain; models with more similar categorical structure sit closer together."`

**Sentence 2 — Caulkins consensus-type classification (Register 2):**
> `"Across the full model slate, the between-model agreement matrix classifies as ${consensus_phrase}."`

Where `mapConsensusType` maps the `consensus_type` enum to **binding plain-English Register-2 phrasing**:

| `consensus_type` enum | Binding plain-English phrase |
|---|---|
| `"STRONG_CONSENSUS"` | `"strong consensus (the models organize this domain similarly)"` |
| `"WEAK_CONSENSUS"` | `"weak consensus (the models partly agree on how to organize this domain)"` |
| `"TURBULENT"` | `"turbulent (no shared organizing structure across the model slate)"` |
| `"CONTESTED"` | `"contested (the models split into subgroups with different organizing structures)"` |
| `"SUBCULTURAL"` | `"subcultural (the models split into subgroups with internally-coherent organizing structures)"` |
| `null` or absent | (omit Sentence 2 entirely; do not render a fallback string) |

**Sentence 3 — R1-state suppressed-ellipse count (conditional):**

If `n_low > 0` OR `n_det > 0`, append:
> `"${n_low + n_det} of these ${n_selected} ${n_selected === 1 ? 'model has' : 'models have'} no confidence ellipse on the map; their output distributions had low variability or were deterministic, and the bootstrap could not estimate a position uncertainty."`

If `n_low === 0` AND `n_det === 0`, omit Sentence 3 entirely.

**Forbidden-vocab scan on the binding output:** clean. "Organize," "categorize," "categorical structure" are all §1.5.4-approved (line 165, 166, 167). "Between-model agreement matrix" names a statistical object, not a model cognition state. "No shared organizing structure" is the §1.5.5 first-class-state framing carried forward from T5's "no shared structure." "Output distributions had low variability" is Register 1 output-distribution language, correctly used. No "believes," "thinks," "sees," "perceives," "understands," "worldview."

**Sample rendered output on `family.json` (n_selected = 11, all R1-a, consensus_type = `STRONG_CONSENSUS`):**
> "This chart places 11 models on a two-dimensional map according to how their outputs categorize this domain; models with more similar categorical structure sit closer together. Across the full model slate, the between-model agreement matrix classifies as strong consensus (the models organize this domain similarly)."

**Sample rendered output on `holidays.json` (n_selected = 9, 2 R1-b, consensus_type = `STRONG_CONSENSUS`):**
> "This chart places 9 models on a two-dimensional map according to how their outputs categorize this domain; models with more similar categorical structure sit closer together. Across the full model slate, the between-model agreement matrix classifies as strong consensus (the models organize this domain similarly). 2 of these 9 models have no confidence ellipse on the map; their output distributions had low variability or were deterministic, and the bootstrap could not estimate a position uncertainty."

---

### 2.2. `freeListScreenReaderSummary` — binding output

**Template structure** (2 sentences when normal data; one when empty):

**Sentence 1 — selected model count + what FreeListCompare shows:**
> `"This chart shows the terms each of ${n_selected} ${n_selected === 1 ? 'selected model' : 'selected models'} produced for this domain, ordered by Sutrop salience score and paired with the fraction of collection runs that produced each term."`

**Sentence 2 — term-count range + shared-term count (conditional on n_selected ≥ 2):**

Compute `min_terms = min(sutrop_csi[m].length for m in selectedModels)`, `max_terms = max(...)`, `n_shared = sharedTerms.size`.

If `n_selected >= 2`:
> `"Term counts range from ${min_terms} to ${max_terms} across the selected models; ${n_shared} ${n_shared === 1 ? 'term appears' : 'terms appear'} in every selected model's list."`

If `n_selected === 1`:
> `"The selected model produced ${max_terms} terms for this domain."`

If `n_selected === 0`: render only the empty-state caption (no SR summary sentences beyond the single "(Select one or more models to see free-list summary.)" sentence — see S8 below).

**Special case: empty-freelist propagation (Case C).** If any selected model has `sutrop_csi[m].length === 0`, that model contributes 0 to `min_terms`; the sentence reads naturally ("term counts range from 0 to ..."). No additional special-case clause is needed in the SR summary — Case C is surfaced in the table cell, not in the summary.

**Forbidden-vocab scan on the binding output:** clean. "Produced," "ordered by," "paired with," "appears in" are all data-relation language. "Sutrop salience score" is the named-measure phrasing carried forward from T7 N5.2. "Collection runs" is the §1.5-clean phrasing carried forward from T7 N5.1. No model-state attribution.

**Sample rendered output on `family.json` with 3 selected models** (Coder verifies on actual data):
> "This chart shows the terms each of 3 selected models produced for this domain, ordered by Sutrop salience score and paired with the fraction of collection runs that produced each term. Term counts range from {min} to {max} across the selected models; {N} terms appear in every selected model's list."

---

### 2.3. `similarityScreenReaderSummary` — binding output

**Template structure** (3 sentences when normal data; abbreviated when n_selected < 2):

**Sentence 1 — pairwise count + what the heatmap shows:**

Let `n_pairs = (n_selected * (n_selected - 1)) / 2` (off-diagonal unordered pairs).

If `n_selected >= 2`:
> `"This chart shows pairwise similarity scores between each of ${n_pairs} unordered model ${n_pairs === 1 ? 'pair' : 'pairs'} from the ${n_selected} selected models; 1.00 indicates identical categorical organization and 0.50 indicates no shared structure between the two models' co-occurrence patterns."`

If `n_selected < 2`: render only the empty-state caption (no SR summary sentences — see S8 below).

**Sentence 2 — off-diagonal similarity range:**

Compute the min, max, and median similarity over the off-diagonal cells corresponding to selected models (excluding self-similarity diagonals, which are 1.00 by construction). Use the `modelIndexMap` translation from T5 plan §2.8.

If `n_selected >= 2`:
> `"Off-diagonal similarity scores range from ${min_sim} to ${max_sim}, with a median of ${median_sim}."`

Where `${min_sim}`, `${max_sim}`, `${median_sim}` are `.toFixed(2)`. (Two decimals match the caption-level precision and avoid the false-precision-of-three-decimals reading the cells use.)

**Sentence 3 — CI-includes-null count (R10 cross-surface report):**

Compute `n_dashed = count of off-diagonal pairs whose 95% CI includes the no-shared-structure value 0.50`. If any cells have `null` CIs (R10 fallback per T5 plan §2.7), count those as `n_no_ci`.

If `n_dashed > 0`:
> `"${n_dashed} of the ${n_pairs} ${n_pairs === 1 ? 'pair has' : 'pairs have'} a 95% confidence interval that includes the no-shared-structure value of 0.50; on the heatmap these cells are shown with a dashed border."`

If `n_dashed === 0` AND `n_no_ci === 0`: omit Sentence 3 entirely (no dashed cells, no null CIs).

If `n_dashed === 0` AND `n_no_ci > 0`:
> `"${n_no_ci} of the ${n_pairs} ${n_pairs === 1 ? 'pair has' : 'pairs have'} no confidence interval available; on the heatmap these cells are shown without a numeric range."`

If `n_dashed > 0` AND `n_no_ci > 0`: render both clauses joined with "; additionally".

**Forbidden-vocab scan on the binding output:** clean. "Identical categorical organization" is §1.5.4-line-166-approved framing. "No shared structure" is the T5 §5.1 binding phrasing — carried forward verbatim. "Co-occurrence patterns" is data-relation language. "Pairwise similarity scores" is Register 2 vocabulary. No "model A agrees with model B," "models think alike," "models share a worldview" (forbidden per T5 §1.5.4 table).

**Sample rendered output on `holidays.json` with 3 selected models** (Coder verifies on actual data):
> "This chart shows pairwise similarity scores between each of 3 unordered model pairs from the 3 selected models; 1.00 indicates identical categorical organization and 0.50 indicates no shared structure between the two models' co-occurrence patterns. Off-diagonal similarity scores range from {min} to {max}, with a median of {med}. {N} of the 3 pairs have a 95% confidence interval that includes the no-shared-structure value of 0.50; on the heatmap these cells are shown with a dashed border."

---

## 3. Binding button label

### 3.1. Toggle button labels

**Architect proposed:** `"Read as table"` at rest; `"Show visualization"` when pressed.

**CDA SME binding wording: APPROVED as proposed.**

- `READ_AS_TABLE_LABEL_REST` = **`"Read as table"`**
- `READ_AS_TABLE_LABEL_PRESSED` = **`"Show visualization"`**

**Rationale:** "Read as table" is precedent-aligned (DESIGN_SYSTEM.md §7 / §12.6 deferral language explicitly uses "Read as table" — the §7 binding text the toggle satisfies). Alternatives considered and rejected:

| Candidate | Why rejected |
|---|---|
| `"View as table"` | Slightly weaker affordance ("view" reads as passive observation; "read" suggests linear narrative engagement, which matches what a table is for in this context). Not §1.5-blocking; the precedent in §7 governs. |
| `"Show table"` | Less informative — doesn't communicate that the table is an alternative representation of the chart. A screen-reader user encountering just "Show table" might not realize it replaces the visualization. |
| `"Show as table"` | Reads slightly awkward; "Read as table" is more idiomatic. |
| `"Tabular view"` | Too jargon-heavy for the journalist/general-reader audience. |

The pressed-state label `"Show visualization"` is symmetric and §1.5-clean (`"visualization"` is the data-display object, not the model state). No "Hide table" (which inverts the framing — the table is the alternative, not the default).

Forbidden-vocab scan: clean. "Read" applied to a *table* is not a model-state attribution; "visualization" is a generic chart-rendering term. No psychological-attribution language.

---

## 4. Binding table captions

### 4.1. MDS table caption (`MDS_TABLE_CAPTION`)

**Architect proposed:**
> "Each row shows where a model lands on the MDS map and how confident the bootstrap is in that position. Rows showing '—' under semi-major/semi-minor have no confidence ellipse because their output had low variability (the bootstrap couldn't resample meaningful variance)."

**CDA SME binding wording:**
> **`"Each row shows where one model lands on the MDS map and the bootstrap uncertainty around that position. Rows showing '—' under semi-major / semi-minor / rotation have no confidence ellipse — their output distribution had low variability or was deterministic, so the bootstrap could not estimate a position uncertainty."`**

**Three edits to the Architect's draft:**

1. **"a model" → "one model"** — clarifies that each row corresponds to a single model (the Architect's "a model" reads as generic; "one model" is row-level explicit).
2. **"how confident the bootstrap is in that position" → "the bootstrap uncertainty around that position"** — removes the soft anthropomorphization of the bootstrap ("how confident the bootstrap is" reads as an agent attribution); "uncertainty around" is the statistical term.
3. **"their output had low variability (the bootstrap couldn't resample meaningful variance)" → "their output distribution had low variability or was deterministic, so the bootstrap could not estimate a position uncertainty"** — covers both R1-b (low_concentration) and R1-c (deterministic) cases. The Architect's draft only describes R1-b. The parenthetical "(the bootstrap couldn't resample meaningful variance)" is dropped because it's a methodological aside that belongs on the methodology page, not in a table caption.

**Forbidden-vocab scan:** clean. "Output distribution" is Register 1 vocabulary, correctly used. "Position uncertainty" is statistical terminology. No "believes," "sees," "thinks," "perceives." First-class-state framing intact (the `—` rows are *not* defective; they are correctly absent because the bootstrap had no variance to resample).

### 4.2. FreeList table caption (`FREELIST_TABLE_CAPTION_TEMPLATE`)

**Architect proposed (per-model):**
> "{model short name} ranked terms, ordered by Sutrop salience score. The inclusion-frequency column shows the fraction of collection runs that produced each term."

**CDA SME binding wording:**
> **`"${modelShortName}'s ranked terms for this domain, ordered by Sutrop salience score. The inclusion-frequency column shows the fraction of this model's collection runs that produced each term."`**

**Two edits to the Architect's draft:**

1. **"{model short name} ranked terms" → "${modelShortName}'s ranked terms for this domain"** — adds the possessive (parallel to T7's "this model's collection runs" binding) and adds "for this domain" to anchor scope (a journalist could otherwise read the table out-of-context as a global ranking).
2. **"the fraction of collection runs that produced each term" → "the fraction of this model's collection runs that produced each term"** — **MANDATORY cross-surface consistency with T7's CDA SME §5.1 binding wording.** The bar caption in FreeListCompare reads "Bar shows the fraction of this model's collection runs that produced this term." The table caption MUST use the same possessive ("this model's collection runs") so a reader toggling between viz and table is encountering byte-equivalent prose about the same statistic. This is S5 above and is load-bearing.

**Forbidden-vocab scan:** clean. "Sutrop salience score" is the T7 N5.2 binding phrasing. "This model's collection runs" is the T7 N5.1 binding phrasing. "Produced" is data-relation language (not "model produced because it thought…"). No model-state attribution.

### 4.3. Similarity table caption (`SIMILARITY_TABLE_CAPTION`)

**Architect proposed:**
> "Each row compares two models in the current selection. The similarity column shows their pairwise agreement; the 95% confidence interval columns show the range of plausible values from the bootstrap. Rows showing '—' could not produce a confidence interval (one or both models had too few non-degenerate bootstrap resamples)."

**CDA SME binding wording:**
> **`"Each row compares two models in the current selection. The similarity column shows how similarly the two models organize this domain (1.00 = identical organization; 0.50 = no shared structure); the 95% confidence interval columns show the bootstrap range around that value. Rows showing '—' under the confidence interval columns have no bootstrap interval available."`**

**Three edits to the Architect's draft:**

1. **"shows their pairwise agreement" → "shows how similarly the two models organize this domain (1.00 = identical organization; 0.50 = no shared structure)"** — **MANDATORY cross-surface consistency with T5's CDA SME §5.1 binding caption**, which reads "Each cell shows how similarly two models organize this domain (1.00 = identical organization; 0.50 = no shared structure)." The table caption MUST inherit this terminology so a reader toggling between heatmap and table is encountering equivalent prose about the same statistic. "Pairwise agreement" is the rejected wording from T5's verdict (soft consensus framing) — it MUST NOT reappear here. This is S5 above and is load-bearing.
2. **"the range of plausible values from the bootstrap" → "the bootstrap range around that value"** — tighter; "plausible values" is colloquial. T5 itself says "the bootstrap range" implicitly via the per-cell tooltip; this matches.
3. **"could not produce a confidence interval (one or both models had too few non-degenerate bootstrap resamples)" → "have no bootstrap interval available"** — the parenthetical methodological explanation belongs on the methodology page, not in the table caption. The Architect's §2.3.3 caveat noted this exactly: "the language 'too few non-degenerate bootstrap resamples' is the working hypothesis for what null-CI means in the published JSON; the CDA SME confirms or specifies replacement language." The CDA SME chooses **"have no bootstrap interval available"** — first-class-state framing per §1.5.5, no defect language, no methodological footnote in a table caption. The expanded explanation lives on the methodology page (T1/T2/T14) when it ships.

**Forbidden-vocab scan:** clean. "Organize" is §1.5.4-line-166-approved. "No shared structure" is T5 N5.1 binding. "Bootstrap range" is statistical terminology. No "agreement," "agree," "share a worldview," "think alike." First-class-state framing on `—` rows.

---

## 5. Carry-forward notes to the Coder (binding)

The Coder applies all seven notes during implementation. The Reviewer enforces them at PR review. None require re-routing back to the CDA SME unless the Coder believes a note is internally inconsistent with the plan; in that case, pause and route the question rather than self-editing.

### S1. **MDS template — render `consensus_type` enum as plain-English Register-2 phrase, not as bare enum.** [Analytical validity]

Per §2.1, the `consensus_type` enum from `domainResult.consensus_type` must be mapped via the binding table in §2.1 above before being rendered in Sentence 2. The Coder MUST NOT render `STRONG_CONSENSUS` / `WEAK_CONSENSUS` / `TURBULENT` / `CONTESTED` / `SUBCULTURAL` as the literal enum string into SR-rendered prose — these are Caulkins-typology classifications of the between-model agreement matrix (a Register 2 statistical object), not properties of the models themselves. Rendering the bare enum risks a screen-reader user (or a journalist quoting the SR text) reading "STRONG_CONSENSUS" as a property of model cognition rather than as a property of the between-model statistic.

**Coder regression-test:** vitest snapshot asserts the rendered MDS template body for `family.json` contains the substring `"strong consensus (the models organize this domain similarly)"` and does NOT contain the substring `"STRONG_CONSENSUS"`.

### S2. **FreeList template — use precise numeric phrasing.** [Audience translation]

The §2.2 binding wording uses "Term counts range from {min} to {max}" rather than "approximate term-count range" (the Architect's §2.5 comment-stub language). Numeric precision is appropriate at the SR-template level — a screen-reader user benefits from the exact counts more than from a fuzzy "approximately" framing. The Coder computes `min` and `max` as exact integers; no rounding, no "approximately" qualifier, no "around N terms" phrasing.

### S3. **Similarity template — carry forward T5 binding terminology.** [Audience translation, Claims validity]

The Similarity template body MUST use **"no shared structure"** (per T5 N5.1 binding), NOT "no agreement" (which T5's CDA SME explicitly rejected as a soft consensus framing). The §2.3 binding wording reflects this. The Coder MUST NOT introduce "agreement" / "agree" / "agrees with" anywhere in the Similarity SR template body, the Similarity table caption, or the Similarity table column headers. The §2.8 forbidden-vocab grep adds `"agree"` (case-insensitive, with word-boundary `\bagree`) to the existing grep list before commit.

### S4. **Button labels approved as proposed — DO NOT REVISE.** [Audience translation]

`READ_AS_TABLE_LABEL_REST = "Read as table"` and `READ_AS_TABLE_LABEL_PRESSED = "Show visualization"` are approved verbatim. These are the binding labels; the Coder ports them exactly into `src/copy/screen_reader_summaries.ts`. The Reviewer's vitest snapshot asserts byte-identical text content on the rendered `<button>` element in both pressed and unpressed states.

### S5. **FreeList table caption MUST inherit T7's "this model's collection runs" verbatim; Similarity table caption MUST inherit T5's "no shared structure" verbatim.** [Claims validity, Audience translation]

This is the load-bearing cross-surface-consistency binding. The bar-caption in FreeListCompare reads `"Bar shows the fraction of this model's collection runs that produced this term."` — the FreeList table caption's inclusion-frequency clause is `"shows the fraction of this model's collection runs that produced each term."` (per §4.2). The Similarity heatmap caption reads `"... 0.50 = no shared structure. Dashed cells: 95% confidence interval includes the no-shared-structure value."` — the Similarity table caption inherits the same `"no shared structure"` terminology (per §4.3).

The Reviewer enforces this by inspecting both surfaces' rendered DOM in the integration tests. If the toggle-and-back cycle on any viz produces a caption that disagrees with the un-toggled view's caption on the same statistical concept, the Reviewer rejects the commit.

### S6. **MDS table caption — bind the three edits in §4.1 verbatim.** [Audience translation]

The MDS table caption as written in §4.1 above is the binding string. The Coder ports it byte-for-byte into `MDS_TABLE_CAPTION`. The Reviewer's vitest snapshot asserts byte-identity.

### S7. **Similarity table caption — bind the three edits in §4.3 verbatim, and add T1/T2/T14 follow-up advisory.** [Audience translation]

The Similarity table caption as written in §4.3 above is the binding string. The Coder ports it byte-for-byte into `SIMILARITY_TABLE_CAPTION`. The methodological explanation for null CIs ("too few non-degenerate bootstrap resamples" or whatever the published-JSON-mechanism actually is) belongs on the methodology page (T1/T2) when it ships; T14 doc-sweep wires the link from the table caption's `—` reference (or from a `?` affordance) to the methodology-page section. **For T8, the caption is rendered as plain text with no link; the link is T14's territory.**

The Coder includes this follow-up advisory in the T8 commit body:

> Follow-up: T14 doc-sweep should wire a methodology-page link from the SimilarityTable caption's "no bootstrap interval available" phrase (or via a `?` affordance) to the section of the methodology page that explains the null-CI mechanism. T8 ships with the caption as plain text per Phase 6 minimum-viable surface posture.

### S8. **Empty-state captions — minor word-order tightening.** [Audience translation]

The Architect's §2.8 empty-state captions are §1.5-clean and first-class-state-framed. Three minor edits:

- `MDS_TABLE_EMPTY_NO_MODELS`: `"Select one or more models to see the MDS coordinates table."` — **APPROVED as proposed.**
- `FREELIST_TABLE_EMPTY_NO_MODELS`: `"Select one or more models to see the ranked-term tables."` → **`"Select one or more models to see the ranked-term tables for this domain."`** (adds "for this domain" for symmetry with the table caption's scope-anchor per §4.2).
- `SIMILARITY_TABLE_EMPTY_LT_2_MODELS`: `"Select at least two models to see the similarity table."` → **`"Select at least two models to see the pairwise similarity table."`** (adds "pairwise" — symmetric with the §2.3 SR template's "pairwise similarity scores" terminology; helps a reader understand why N≥2 is required).

Forbidden-vocab scan: clean on all three.

### S9. **Column headers — §2.8 list approved with three minor revisions.** [Audience translation]

The Architect's §2.8 column-header list is approved with the following revisions for cross-surface vocabulary consistency:

- **MDS table:** `"Uncertainty mode"` → **`"Output concentration"`** (clearer; the column shows the R1 state which is a concentration classification, not a generic "uncertainty mode"). The cell values map: `typical_concentration` → "typical"; `low_concentration` → "low"; `deterministic` → "deterministic". These three cell values are §1.5-clean as plain English.
- **MDS table:** `"n_bootstrap"` → **`"Bootstrap samples"`** (LSB-authored column header should be human-readable English, not a snake_case identifier; this is the only column header in the MDS table that names a meta-statistical quantity rather than the statistic itself). The Architect's §2.8 list correctly identifies the other field-name columns as LSB-authored prose; this one fell through.
- **MDS table:** `"Rotation (rad)"` → **`"Rotation angle"`** (drop the unit qualifier from the header; cells render `0.245` or `—`. The unit "radians" can be implicit at this granularity; the methodology page elaborates).
- **All other column headers** (`Model`, `model_id` (the full identifier — kept as raw field-name in mono font; this is exempt from LSB-authored-prose review per the Architect's §1 binding directive 4), `Rank`, `Term`, `Salience (CSI)`, `Inclusion frequency`, `Model A`, `Model B`, `Similarity`, `95% CI low`, `95% CI high`, `Semi-major`, `Semi-minor`) — **APPROVED as proposed.**

Forbidden-vocab scan on revisions: clean. "Output concentration" is Register 1 vocabulary (correctly used). "Bootstrap samples" is statistical terminology. "Rotation angle" is geometric terminology.

### S10. **Do not narrate methodology choices in any SR template body.** [Claims validity]

The three SR template bodies are 2-3 sentences each. They MUST NOT explain *why* a methodology choice was made (e.g., "we use bootstrap resampling because…", "consensus_type is classified via the Caulkins typology because…"). The methodology page (T1/T2) is where methodology is explained. The SR templates report *what the chart shows*; the methodology page reports *why*. This is the same discipline applied to T5 §5.5 and T7 §5.5 captions.

The Coder MUST NOT add a fourth sentence to any template explaining the methodology. The Reviewer enforces a sentence-count ceiling: MDS template ≤ 3 sentences; FreeList template ≤ 2 sentences; Similarity template ≤ 3 sentences.

### S11. **`framing_note` / `generated_lede` boundary preserved.** [Claims validity]

The Architect's §2.6 analysis of the lede / SR boundary is **correct** and is binding. The per-domain `generated_lede` (rendered in `ArticleHeader`) and the per-viz `ScreenReaderSummary` are complementary, not duplicative:

- `generated_lede` answers: "Why am I looking at this domain page?" — a domain-level finding statement. Audience: any reader scanning the dashboard.
- `ScreenReaderSummary` answers: "What does *this specific chart* show?" — a viz-level structural summary. Audience: a screen-reader user (or any reader using `?inspect=`-style verification) who needs an alternative-modality summary of the same information the sighted reader gets from the chart.

The two surfaces share no source-of-truth. The lede generator stays in `cdb_publish` (CLAUDE.md §9 pitfall #2, R11). The SR templates are programmatic, deterministic, and live in `apps/dashboard/src/copy/screen_reader_summaries.ts`. The Coder MUST NOT reuse `domainResult.generated_lede` as the body of any SR template — that would conflate the domain-level finding with the per-viz structural summary, and would couple the dashboard to the lede-generator's output format in a way that breaks the LLM-boundary discipline.

**Coder regression-test:** grep `screen_reader_summaries.ts` for `generated_lede` — must not appear. The dashboard imports `generated_lede` only in `ArticleHeader.tsx` (existing).

---

## 6. Forbidden vocabulary scan

Scanned every LSB-authored string T8 introduces (button label, three SR template bodies, three table captions, four empty-state captions, ~14 LSB-authored column headers, the binding `consensus_type` plain-English mapping table) against `CLAUDE.md` §7 and `ARCHITECTURE.md` §1.5.4 tables:

| Forbidden phrase | Present after S1–S11 applied? |
|---|---|
| "believes" / "thinks" / "worldview" (model-applied) | No |
| "How models see the world" | No |
| "What the model understands" | No |
| "Cultural bias" (standalone) | No |
| "Within-model consensus" / "Within-model CCM" / "Within-model eigenratio" | No |
| "publishable" / "groundbreaking" / "first-of-its-kind" | No |
| "closer to human = better" framing | No |
| "missing" / "placeholder" / "no data yet" / "pending" (empty-state) | No |
| "models agree" / "models think alike" / "models share a worldview" | No |
| "agreement" / "agree" / "agrees with" (used as consensus framing) | No (T5/T7-binding alternative "no shared structure" / "similarly organize" used throughout) |
| "perceives" / "intends" / "sees" (model-applied) | No |
| Cross-domain generalization claim | No |
| Hypothesis-testing framing ("LSB confirms," "LSB found that {hypothesis}," "LSB tested whether") | No |

**PASS on vocabulary** after S1–S11 are applied.

**One soft-flag, NOT a forbidden-vocab violation:** the MDS template's Sentence 2 plain-English mapping of `STRONG_CONSENSUS` reads "strong consensus (the models organize this domain similarly)." A pedantic reading could ask whether "the models organize" is a Register-2-clean framing — i.e., whether "the models" *as a slate* "organize this domain" rather than "the models' outputs *as a slate*  organize this domain." The mitigation is that the Sentence 1 framing already establishes "outputs categorize this domain" (correct Register 1 → Register 2 chain); Sentence 2 then describes the *between-model* classification of that slate. A reader reading the two sentences in sequence gets the correct chain. Soft-flag accepted; no edit required.

---

## 7. Boundary with the existing per-domain lede

The Architect's §2.6 design is **correct and binding** (per S11 above). The two surfaces are complementary, share no source-of-truth, and serve different readers:

- `domainResult.generated_lede` (existing field, consumed by `ArticleHeader.tsx`): per-domain prose finding, generated by the lede generator in `cdb_publish`. Currently 1-3 sentences per the `family.json` / `holidays.json` corpus (sample shown in §1 reading). Audience: journalist scanning the article header.

- T8's three SR template bodies: per-viz programmatic summaries derived from `domainResult` numeric fields (model count, `consensus_type` enum, `display.r1_states`, `sutrop_csi[modelId].length`, `similarity_matrix` + `similarity_ci`). Audience: screen-reader user, accessibility auditor, journalist verifying the table view preserves the finding.

**Overlap check:** the existing `generated_lede` for `family.json` is:
> "Across 11 frontier models, family vocabulary is organized around a single shared categorical structure (Smith's S = 0.71, 95% CI [0.50, 0.91]). The map below shows where each model sits relative to that consensus -- and which models diverge from it."

The MDS SR template under §2.1 renders:
> "This chart places 11 models on a two-dimensional map according to how their outputs categorize this domain; models with more similar categorical structure sit closer together. Across the full model slate, the between-model agreement matrix classifies as strong consensus (the models organize this domain similarly)."

These say *related* things but at different layers:
- The lede reports the **domain-level finding** (Smith's S point estimate + CI; "shared categorical structure" as a domain-level claim).
- The SR template reports the **chart-level structural summary** (model count, the Caulkins-typology classification, the R1-state-suppressed-ellipse count).

Smith's S does **not** appear in the SR template (correctly — Smith's S is a domain-level statistic owned by the lede, not a per-viz statistic). `consensus_type` does **not** appear in the lede (correctly — `consensus_type` is the Caulkins-typology classification of the between-model agreement, which is a chart-level Register-2 finding owned by the MDS viz).

**No duplication.** The two surfaces are correctly orthogonal: the lede is the *interpretation*, the SR template is the *structural reading*. A reader who hears both surfaces (via screen reader) gets the lede's narrative finding AND the chart's structural summary, in sequence.

The Architect's design is correct; S11 makes it binding.

---

## 8. Forward-compatibility note (advisory, not blocking)

When T4 (DriftTracker) ships, the follow-up commit adding `DriftTable.tsx` and a fourth SR template (`driftScreenReaderSummary`) will need its own CDA SME content review. The DriftTracker's Register 3 (longitudinal drift via Procrustes) framing carries different cross-surface vocabulary precedents and will need its own forbidden-vocab discipline. This is **not** a T8 concern; flagged here so the Phase 6 closeout / T4 dispatch carries the advisory forward.

---

## 9. Approval

**PASS-WITH-NOTES.** T8 proceeds to UI/UX light-touch review and then to the Coder on the standard gate chain. The eleven §5 carry-forward notes are binding; the Reviewer enforces them at PR review (especially S1 enum-mapping, S3 forbidden-"agree" grep extension, S5 cross-surface caption inheritance, S11 lede-boundary preservation).

The three ScreenReaderSummary template specifications in §2 are the **binding regression-test targets**. The three table caption strings in §4 are the **binding verbatim strings**. The button labels in §3 are **APPROVED as proposed** with no revision. The empty-state captions in S8 are **APPROVED with minor word-order tightening** per S8. The column headers in S9 are **APPROVED with three minor revisions** per S9.

The Architect's structural decisions (per-viz toggle, per-viz `useState`, programmatic templates over lede regeneration, `display: none` + `aria-hidden` on the hidden viz, R10-in-tables with column adjacency, no LLM call introduced at the dashboard layer, `cdb_publish` boundary preserved) are all methodologically and §1.5-clean and are approved without revision.

No escalation to Mark required. The §5 notes touch template body wording, caption wording, button labels, column headers, and a deferred T14 methodology-page-link advisory. None of them reframe §1.5 or introduce a load-bearing methodology decision Mark has not already endorsed ("the corpus lens," "failures are findings," "Phase 6 minimum-viable functional surface," T7 and T5 binding cross-surface vocabulary). The S7 Similarity-table-caption methodology-page-link advisory is appropriately deferred to T14 — its inclusion in the T8 commit body is the audit trail.

— CDA SME agent (Opus), 2026-05-12
