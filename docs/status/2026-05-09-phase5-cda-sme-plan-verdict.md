# CDA SME Plan-Level Verdict — Phase 5 Architect Plan

**Filed:** 2026-05-09
**Reviewer:** CDA SME (Opus)
**Plan reviewed:** `docs/status/2026-05-09-phase5-architect-plan.md` (HEAD `f9a33b7`)
**Slack channel:** `#lsb-cda-sme`

**Companion docs read in full or in relevant sections before this verdict:**
- `ARCHITECTURE.md` v0.7.3 — §1 commitments 6, 8, 10; §1.5 (all subsections, especially §1.5.1 five-link chain, §1.5.4 forbidden vocabulary, §1.5.5 human-grounding-removed, §1.5.6 website-as-artifact, §1.5.7 exploratory framing); §1.6 project naming; §4.2 binding constraint; §4.2.0 three registers; §4.2.3 lede generator (the only LLM downstream of collection, lives in `cdb_publish`); §4.2.6 bootstrap uncertainty; §4.2.7 two-level pipeline (OCI semantics); §5.3 Phase 5.
- `CLAUDE.md` v1.0 — §6 binding rules (R10, R11, R13), §7 forbidden vocabulary table, §9 pitfalls 2 / 7 / 8.
- `DESIGN_SYSTEM.md` v0.2 — §2.1 page architecture; §3.3.5 R1-state rendering (full, all 8 binding implementation requirements); §3.8 KeyFinding strip; §6 methodology page outline; §7 accessibility; §11 component inventory.
- `docs/status/2026-05-07-lsb-philosophy-and-framing.md` — §1, §2, §4, §5, §7, §8 (honest tagline), §9.
- `docs/status/2026-05-07-phase4b-cda-sme-plan-verdict.md` — establishes B6 / T8 / T9 / T11–T15 / P1–P8 binding-note vocabulary, the failures-as-findings posture (Q8), and the carry-forward table.
- `docs/SME_REVIEW.md` Project Framing block; §1.1 Romney threshold.
- `data/results/family/0.2.json` (n=11, `consensus_type: STRONG_CONSENSUS`, `romney_eigenratio: 12.10`, `romney_small_n_warning: true`, all 11 within-model results are R1-a).
- `data/results/holidays/0.2.json` (n=9, `consensus_type: STRONG_CONSENSUS`, `romney_eigenratio: 10.15`, `romney_small_n_warning: true`, **two models present R1-b**: one with `oci: 0.0`, one with `oci: 2.55`, both `deterministic_output: false`).
- `packages/cdb_core/cdb_core/schemas.py` — `ConsensusType` Literal (six values, see Finding F2).

---

## VERDICT: PASS-WITH-NOTES

| Axis | Result |
|---|---|
| Axis 1 — Protocol validity | N/A (publish layer reads existing `data/results/*.0.2.json`; no protocol change) |
| Axis 2 — Analytical validity | PASS-WITH-NOTES |
| Axis 3 — Claims validity | PASS-WITH-NOTES |
| Axis 4 — Audience translation | PASS-WITH-NOTES |
| Register compliance | PASS (R1 OCI used as concentration descriptor in §3.3.5 rendering; R2 Romney CCM correctly cited at n=11 / n=9; R3 explicitly out of scope per plan §10) |
| Vocabulary compliance | PASS on the plan body itself (zero §1.5.4 hits in the plan's own prose; zero "publishable" hits; zero "worldview/believes/thinks" applied to models) |

The plan is methodologically sound and approved for Coder dispatch with **eleven binding notes (Q1–Q11)** spanning the lede template (T2), the methodology summary prose (T13), the publish-layer derived fields (T3), and the small-n posture across both domains. None of the eleven require schema changes or scope expansion; all are prose, code-level, or Reviewer-scan disciplines that bind the next agent in the pipeline.

PASS-WITH-NOTES rather than PASS because the plan's T2 lede pattern set has three concrete defects that need binding before the Coder writes the templates (Q1, Q2, Q3), the T3 `top_freelist_terms` salience-ranking choice is methodology-bound but not specified in the plan (Q4), and the failures-as-findings posture established by the Phase 4b Q8 ruling has implications for the holidays domain's two R1-b models that the plan does not yet operationalize at the lede or KeyFinding surface (Q5).

The §1.3 architectural framing ("template-based for Phase 5; LLM in Phase 6"), the §1.7 tagline placement (ArticleHeader subtitle + MethodologySummary, single-source-of-truth in `copy/framing.ts`), the §1.6 model-count framing (data-derived, no hero stat), and the §1.1 0.2-vs-0.3 deferral (Phase 5 ships 0.2; Phase 6 re-analyses with T4 follow-up corpus) are all methodologically defensible and pass the four-axis review. The §1.4 PNG export and §1.5 manual deploy decisions are operational, not methodology-bound, and the SME does not gate them.

Coder is authorized to begin dispatch on T1 (no methodology gate). T2 dispatch is gated on the architect publishing the three sentence patterns for SME content review per §8 of the plan, taking Q1–Q3 below into account. T3 dispatch is gated on the Coder addressing Q4 (salience-rank choice). T13 dispatch is gated on the architect publishing the methodology summary prose draft for SME content review, taking Q6–Q11 below into account.

---

## Q1–Q11 binding notes

### Q1 — T2 lede patterns: "no-consensus" branch is misnamed against the schema

**Finding (F2 in the proactive checks below).** The plan §1.3 specifies three named cases for the lede template:

> 1. Strong-consensus case — `consensus_type == STRONG_CONSENSUS` and `n_models >= 8`.
> 2. Weak/no-consensus case — `consensus_type in {WEAK_CONSENSUS, NO_CONSENSUS}`.
> 3. All-deterministic edge case — `all(w.deterministic_output for w in within_model_results)`.

`cdb_core.schemas.ConsensusType` is a `Literal` of **six** values, none of which is `NO_CONSENSUS`:

```
"STRONG_CONSENSUS"  # λ₁/λ₂ ≥ 5.0, all centrality scores positive
"WEAK_CONSENSUS"    # 3.0 ≤ λ₁/λ₂ < 5.0, centrality scores positive
"SUBCULTURAL"       # λ₁/λ₂ ≥ 3.0, negative centrality scores present
"TURBULENT"         # λ₁/λ₂ < 3.0, centrality scores positive
"CONTESTED"         # λ₁/λ₂ < 3.0, negative centrality scores present
"DETERMINISTIC"     # zero-variance reserved for deterministic architectures
```

The plan's "WEAK_CONSENSUS / NO_CONSENSUS" union does not match the schema. `NO_CONSENSUS` is not a member; the actual not-strong family is `{WEAK_CONSENSUS, SUBCULTURAL, TURBULENT, CONTESTED}`. Each of the four has a different methodological meaning per `docs/SME_REVIEW.md` §1.1 and the post-F1 review framework — `SUBCULTURAL` (presence of competing structure) and `CONTESTED` (low ratio with active disagreement) are not interchangeable with `WEAK_CONSENSUS` (low ratio without negative centrality).

**Binding ruling.** The T2 lede template's branch enumeration must use the actual schema literals. The Coder may collapse the four non-strong literals into one or two display branches if the lede prose is identical across them, but the **branch predicate** must be expressed in the actual schema vocabulary. Two acceptable shapes:

- **Shape A (four explicit non-strong branches):** one pattern each for WEAK_CONSENSUS / SUBCULTURAL / TURBULENT / CONTESTED. The patterns may share prose if the SME content verdict at T2 finds the distinctions are methodology-page-only and not lede-surface.
- **Shape B (two-branch collapse):** "low-ratio family" (TURBULENT / CONTESTED, both at λ₁/λ₂ < 3.0) and "moderate-ratio family" (WEAK_CONSENSUS / SUBCULTURAL, both at λ₁/λ₂ ≥ 3.0 but below the 5.0 strong threshold). The collapse decision is methodology-bound and binds at the T2 SME content verdict.

Shape A is the SME-preferred default because it preserves the schema vocabulary at the lede surface and makes the dashboard's text legible to a reader inspecting the published JSON. Shape B is acceptable if the architect explicitly justifies the collapse in the T2 SME content packet.

**Reviewer enforcement at T2:** the lede generator's branch predicate must reference the schema literals, not invented names. Any string `"NO_CONSENSUS"` in the T2 commit is an automatic Reviewer rejection.

### Q2 — T2 lede patterns: small-n warning surface is missing

**Finding.** Both `data/results/family/0.2.json` and `data/results/holidays/0.2.json` carry `"romney_small_n_warning": true` (n=11 < 15 and n=9 < 15 respectively, per `project_romney_small_n_threshold.md` and `docs/SME_REVIEW.md` §1.1). Phase 4b's Q8 ruling (Note A binding "small-n caveat") is **carry-forward to Phase 5** because Phase 5 ships against the 0.2 corpus, which predates Phase 4b's n=20 expansion.

The T2 lede patterns must surface the small-n posture or, at minimum, must not produce confident comparative claims at n=11 / n=9 that the methodology page then has to walk back. A "STRONG_CONSENSUS" eigenratio of 12.10 at n=11 is real signal, but at n_models < 15 the bootstrap CI on that ratio is wide and the Romney threshold's small-n caveat applies.

**Binding ruling.** The strong-consensus lede pattern (Shape A or B) must either:

- **Option (a):** include a parenthetical or footnote-style small-n acknowledgment in the lede sentence itself, OR
- **Option (b):** route the small-n caveat to the SourceAttribution component (T10) and the MethodologySummary block (T13), with a documented Coder-T10 note that SourceAttribution surfaces `romney_small_n_warning` when true.

Option (b) is the SME-preferred default because the lede surface is for the comparative claim and the small-n caveat is a methodology-of-measurement caveat that lands more cleanly at the methodology / source surfaces. Option (a) is acceptable if the architect explicitly chooses to embed the caveat in the lede.

**Reviewer enforcement at T2:** if option (a) is chosen, the strong-consensus lede pattern includes the small-n surface text. If option (b), the architect adds a binding note to T10's deliverable list specifying the SourceAttribution component reads `romney_small_n_warning` from the published JSON and renders a small-italic caveat ("n=11 — small-n; see methodology"). The T13 methodology summary describes the small-n posture either way (Q9 below).

### Q3 — T2 lede patterns: cross-model framing must NOT imply "models converge on truth"

**Finding.** The plan §1.3 strong-consensus pattern reads: *"Pattern names the two most-divergent models by short name, references the centroid models, uses the §1.5.4-safe form ('X's output organises ... distinctly from Y's')."*

This is methodologically defensible at the §1.5.4 vocabulary level. But the Phase 4b Q8 ruling and the §1.5.7 exploratory-framing binding establish a higher bar: **lede prose may not import a thesis-shaped frame.** Specifically:

- The lede must NOT use comparative-superlative language that implies a shared external ground truth (e.g., "Model X organises family terms most accurately" or "Model X's structure is closest to consensus" or "Models converge on a shared categorical structure of family").
- The lede must NOT use causal language linking observed structure to model architecture or training (e.g., "GPT-5.4 organises family terms tightly because of its alignment training").
- The lede MAY use descriptive comparative language that locates models in the cross-model space without imputing why (e.g., "GPT-5.4 and Claude Opus 4.6 sit close together in the cross-model map, while DeepSeek V3.2 sits at a distance").

**Binding ruling — the strong-consensus pattern descriptive frame.** The T2 sentence pattern must use the descriptive-locational frame, not the convergence-to-truth frame. The §1.5.4 vocabulary table's binding is necessary but not sufficient — the broader §1.5.7 exploratory frame applies. T8 / T9 binding (no causal language; no introspective verbs applied to models) carry forward from Phase 4b to T2's prose.

**SME content verdict at T2 (separate from this plan-level verdict):** the three sentence patterns will be reviewed for:
- (i) §1.5.4 forbidden vocabulary compliance (left-column phrases absent),
- (ii) T9 vocabulary compliance (no "recognises / identifies / interprets / comprehends / perceives" applied to models),
- (iii) T8 RD-3 descriptive-shape discipline (no causal language, no introspective language, no stimulus-as-cause framing),
- (iv) descriptive-locational vs convergence-to-truth framing (this Q3),
- (v) small-n surface choice per Q2,
- (vi) schema-literal branch predicate per Q1.

**Reviewer enforcement at T2:** the lede output strings must pass the §1.5.4 substring scan AND the T9 verb scan ("recognises", "identifies", "interprets", "comprehends", "perceives"). The descriptive-vs-convergence framing is harder to grep for; this is the SME content verdict's responsibility at the T2 gate, not the Reviewer's.

### Q4 — T3 `top_freelist_terms` salience-rank choice is methodology-bound

**Finding.** Plan T3 specifies:

> `top_freelist_terms(free_list: FreeList, k: int = 5) -> list[str]`

without specifying the **salience metric** that determines the ordering. The plan §1.7 mentions the metric only as "ranked by salience for tooltips." In LSB's analytical surface, two distinct salience metrics are computed and stored in `DomainResult`:

- **Smith's S** — the composite salience index F × P / (N × Lmax) per `cdb_analyze.salience.smith_s()`. Frequency-weighted with primacy contribution.
- **Sutrop CSI** — F / (N × mP) per `docs/SME_REVIEW.md` §2.1 (and the QA Check 8 aggregate). Robust to list-length variance in a way Smith's S is not.

Both are first-class salience measures. Smith's S is the classical choice; Sutrop CSI was recommended by the post-F1 SME review specifically because LSB's free lists vary widely in length across models. Picking one over the other for the dashboard tooltip is a methodology decision that the publish layer makes that the analysis layer left open.

**Binding ruling.** `top_freelist_terms` must:

- **(a)** explicitly name the chosen metric in its docstring and in the published JSON's `display.top_terms` sub-object (e.g., `display.top_terms_metric: "sutrop_csi"`), so a researcher inspecting the dashboard JSON or the open-data bundle can recover what ordering was used.
- **(b)** default to **Sutrop CSI** as the dashboard salience metric, because (i) the QA Check 8 wiring already operationalizes Sutrop CSI as the cross-validation-against-Smith-S anchor, and (ii) Sutrop CSI's list-length-robustness is the more defensible choice when ordering across heterogeneous free lists from different models (which is what the dashboard tooltip surfaces).
- **(c)** in the case where Smith's S and Sutrop CSI rank-disagree by more than one position in the top-5, surface this on the methodology page (T13), not on the tooltip — the tooltip uses the canonical Sutrop ordering; the methodology page describes both metrics and notes when they diverge.

If the architect prefers Smith's S as the default for journalistic recognizability (Smith's S is the classical name; Sutrop CSI is less well known), that is acceptable on stylistic grounds — but the choice must be explicit in the docstring, the JSON, and the methodology page.

**Reviewer enforcement at T3:** the `derived.py` module includes a `TOP_TERMS_SALIENCE_METRIC` constant referenced once in the function body, and the published JSON carries a `display.top_terms_metric` field naming the metric. The Reviewer rejects T3 if the metric is implicit / unnamed.

### Q5 — Holidays domain has two R1-b models; the lede must handle this

**Finding.** Inspection of `data/results/holidays/0.2.json` shows two models with `oci < 3.0` and `deterministic_output: false`:

- one model with `"oci": 0.0`,
- one model with `"oci": 2.55`.

By the §3.3.5 R1-state binding, both render as **R1-b (low concentration)**: dashed 2px stroke, 60% fill opacity, **no confidence ellipse**, tooltip surfaces the low-OCI explanation. Family does not have any R1-b or R1-c models; all 11 are R1-a.

The plan §1.3 lede template branch enumeration handles only:
1. STRONG_CONSENSUS + n_models >= 8,
2. weak / non-strong consensus,
3. all-deterministic.

It does **not** enumerate the case "STRONG_CONSENSUS at the cross-model level, but K of N models are R1-b (low within-model concentration)." This is the actual state of the holidays 0.2 corpus.

The plan's strong-consensus pattern as drafted ("Pattern names the two most-divergent models by short name") is well-defined when all participating models have stable within-model output (R1-a). When some models are R1-b, "naming the two most-divergent" in cross-model space silently ignores that two of those positions have no confidence ellipse — the divergence claim may be a within-model-variance artifact, not a between-model categorical-structure signal.

**Binding ruling.** The T2 lede generator must:

- **(a)** add a fourth branch / sub-branch handling the case `consensus_type == STRONG_CONSENSUS` AND `count(R1-b models) >= 1`. The pattern surfaces the count and avoids superlative comparative claims that pivot on R1-b model positions. Acceptable framing: *"At the cross-model level, the [N] models in this slice cluster as [pattern from STRONG_CONSENSUS branch]. K of N models produced low within-model output concentration on this domain (OCI < [threshold]); their cross-model positions are shown without confidence ellipses and should be interpreted with the methodology-page caveat."*
- **(b)** in the case `count(R1-b models) >= ceil(N/2)` (majority-low-OCI), the lede falls to a separate descriptive pattern that reports the count as the headline finding, not the cross-model clustering — because at majority-R1-b, the cross-model map is reporting positions of dispersed-output models and the "strong consensus" claim becomes substantively misleading even though the eigenratio is high.

**The failures-as-findings posture (Phase 4b Q8 binding) makes this load-bearing.** A model with `oci: 0.0` on holidays is a *finding* (the model produced wildly varying output across runs on holidays), not a defect. The dashboard surfaces the finding via the §3.3.5 R1-b visual treatment; the lede should reference the finding rather than glide over it.

**Reviewer enforcement at T2:** the holidays corpus is one of the test fixtures for T2 (per the plan T2 test cases). The test must assert the lede output includes the R1-b count phrase or equivalent. If the lede output for holidays does not surface the two R1-b models in some form, T2 fails Reviewer.

**SME content verdict at T2:** the four (or five, with Shape A from Q1) sentence patterns are reviewed for the R1-b handling at the T2 SME gate.

### Q6 — T13 MethodologySummary block: B6 (a)–(e), T8, T9, T11, T14, T15 carry forward

**Finding.** Phase 4b's CDA SME plan-level verdict (commit `5e55ba6`) established the carry-forward table. Phase 5's T13 ships methodology-bound prose at the public dashboard surface — the most visible methodology surface the project has produced to date. The carry-forward applies fully:

- **B6 (a)–(e)** — public-copy guardrails: no "incorrect" framing for predecessor work; no cross-provider/cross-failure-mode/cross-prompt-type generalization without evidence; no internal-state claims about models; no "PLUS disproportionate CN-origin decline pattern" augmentation; no "publishable" framing.
- **T8** — RD-3 descriptive-shape discipline: no causal language, no introspective language, no stimulus-as-cause framing.
- **T9** — RD-3 forbidden softer-than-thinks/believes verbs: no "recognises", "identifies", "interprets", "comprehends", "perceives" applied to models.
- **T11** — numerics-vs-interpretation framing-guard sentences at table boundaries (binding if the methodology summary references any tabular surface — likely not at 5–7 sentences, but binds if the prose names specific model-level numerics).
- **T14** — no "publishable" framing.
- **T15** — Note G verbatim wording preservation if Phase 4a Note G surfaces are quoted (likely N/A at T13's 5–7 sentence scope).

**Binding ruling.** All of the above bind on the T13 prose. The SME content verdict at T13 reviews the prose against this list line-by-line.

**Reviewer enforcement at T13:** vocabulary scan includes:
- §1.5.4 12-row table (worldview, believes, thinks, etc.; LSB hypothesises / LSB tested whether / LSB confirms; within-model consensus etc.),
- T9 verb list (recognises, identifies, interprets, comprehends, perceives applied to models),
- T14 "publishable" / "publication" scan,
- B6 internal-state phrases ("the model decided", "the model preferred", "the model chose to", etc.).

### Q7 — T13 MethodologySummary block: corpus-lens five-link chain must be readable

**Finding.** ARCHITECTURE.md §1.5.1 (revised 2026-05-07) establishes the **five-link** corpus-lens chain:

> **corpus → training → alignment → decoding → output distribution**

The §1.5.1 binding text says: *"When the methodology page (or the Coder writing it) uses the phrase 'corpus lens,' it must be readable by a skeptical reader as this five-link chain, not as a euphemism for 'what the model knows.'"*

**Binding ruling.** The T13 MethodologySummary prose must use "corpus lens" in a way that is unpacked — at minimum, name two or three of the five links inline so a skeptical reader can recover the chain. The prose does not have to enumerate all five links (the methodology page proper, deferred to Phase 6, does the full enumeration); but it must not use "corpus lens" as a bare phrase that a reader might interpret as "the model's worldview" or "what the model knows."

Acceptable: *"...the categorical shape of model output, surfaced by applying CDA elicitation. We call this shape the model's corpus lens — the patterns of training data, alignment, and decoding that determine what comes out when you ask."*

Unacceptable: *"...we measure each model's corpus lens."* (Bare phrase, no anchoring.)

**SME content verdict at T13:** the prose is checked for the five-link readability against the §1.5.1 binding.

### Q8 — T13 MethodologySummary block: tagline placement and verbatim integrity

**Finding (PASS on the architectural decision).** Plan §1.7 specifies the tagline is rendered (a) as the second sentence of the ArticleHeader subtitle and (b) verbatim in the MethodologySummary block, both pulled from `apps/dashboard/src/copy/framing.ts` as a single source of truth. This is the right architectural move.

**Binding ruling — verbatim integrity.** The tagline as written in `ARCHITECTURE.md` §1.5 is:

> *LSB measures what frontier LLMs produce when asked to categorize, in a way that's reproducible, comparable across models, and trackable across time.*

(Note the spelling "categorize" — US English in the architecture doc verbatim quote. The plan §1.7 quotes it as "categorise" — UK English. This is a single-character drift between the doc and the plan. The Coder must use the verbatim spelling from `ARCHITECTURE.md` §1.5; the plan's UK-English quote is a typo, not an authoritative re-spelling.)

**Reviewer enforcement at T13:** `apps/dashboard/src/copy/framing.ts` `TAGLINE` constant must match the `ARCHITECTURE.md` §1.5 verbatim string character-for-character (US English: "categorize"). The Reviewer's spot-check at T13 commit review compares the constant against the canonical quote.

**Three-occurrence rule.** Plan §1.7 binds two occurrences (ArticleHeader subtitle + MethodologySummary). The plan's "Adding a third occurrence requires a copy review — not auto-OK" is the right discipline. The footer might be a candidate (e.g., a small italic line above the License link) but is **not** auto-approved by this verdict; if the architect proposes a third placement, it goes through a separate SME mini-review.

### Q9 — T13 MethodologySummary block: small-n posture must be acknowledged

**Finding.** Per Q2, both 0.2 corpora carry `romney_small_n_warning: true`. The methodology summary at the dashboard surface is one of the surfaces where the small-n posture must be acknowledged honestly.

**Binding ruling.** The T13 prose includes one sentence (or one clause) acknowledging:

- The current published corpus is 11 models on family / 9 on holidays.
- Both fall below the n=15 small-n threshold for the Romney consensus measure.
- The corpus is being expanded in Phase 6 to 20 models (per Phase 4b T4 follow-up); the present numerics are reported with the small-n caveat.

Acceptable framing: *"This release reports on 11 frontier language models on the family domain and 9 on holidays. Both samples fall below the small-n threshold for the Romney cultural-consensus measure (n < 15); the next data release expands to 20 models. The methodology page describes the small-n posture and the planned expansion."*

The prose must not: (i) frame the small-n state as a defect or a defer-pending state ("we don't have enough data yet" implies a defect frame); (ii) frame the Phase 6 expansion as a hypothesis-driven re-do ("the Phase 6 expansion will test whether the current findings hold"); (iii) frame the numerics as preliminary in the sense of "wait for Phase 6 before drawing any conclusion."

**Acceptable framing of the expansion:** "the corpus is being expanded" or "the next data release will report on a larger model slate" — descriptive, not predictive.

**SME content verdict at T13:** the small-n acknowledgment is reviewed for the (i)–(iii) defect-vs-finding framing per the failures-as-findings posture.

### Q10 — T13 MethodologySummary block: ancestry credit per §1.5.5 binding

**Finding.** ARCHITECTURE.md §1.5.5 binds: *"Romney / D'Andrade / Weller / Borgatti / Batchelder ancestry credit is named on the methodology page per `DESIGN_SYSTEM.md` §6.1 item 2."*

DESIGN_SYSTEM.md §6.1 item 2 binds the **full methodology page** (Phase 6 deliverable) to name and cite the five originators. The Phase 5 in-article MethodologySummary block is a 5–7 sentence inline summary, not the full page. The plan §10 explicitly defers `MethodologyPage.tsx` and `CitationBlock.tsx` to Phase 6.

**Binding ruling.** The Phase 5 T13 MethodologySummary block must, at minimum:

- name the CDA tradition by name ("Cultural Domain Analysis"),
- mention that the elicitation protocol is borrowed from cognitive anthropology (or equivalent),
- include a forward-link affordance to the (Phase 6) methodology page where the five originators will be cited in full.

The five originator names do not have to all appear in the 5–7 sentence summary, but the **provenance signal** must be present. A reader should not be able to read the MethodologySummary block and conclude that LSB invented the elicitation protocol. The binding here is provenance-honesty, not citation completeness.

Acceptable framing: *"...applying Cultural Domain Analysis, an elicitation protocol from cognitive anthropology (Romney, Weller, Batchelder, and others; full citations on the methodology page)..."*

**SME content verdict at T13:** the prose is checked for the ancestry signal. The full citation roster is checked at the Phase 6 methodology-page review, not here.

### Q11 — T13 MethodologySummary block: failures-as-findings posture must be present

**Finding.** Phase 4b's Q8 ruling and the §1.5.7 binding establish the failures-as-findings posture. The methodology summary block is one of the surfaces where this posture is exercised at the public-dashboard register. The holidays domain's two R1-b models (Q5 above) are the concrete instance.

**Binding ruling.** The T13 MethodologySummary prose must, at minimum, acknowledge that the dashboard reports models with low within-model output concentration (R1-b, dashed-stroke, no ellipse) and zero-variance (R1-c, hollow triangle) as **first-class findings**, not as defects or omissions. The §3.3.5 visual treatment is the dashboard's expression of this posture; the methodology summary is the prose surface for it.

The prose does not have to enumerate the three R1 states (the methodology page proper does that in Phase 6); but it must include language that signals "the visual treatment of low within-model variance is a finding, not a missing-data flag."

Acceptable framing: *"Some models on some domains produce wide variance across runs — the same prompt yields different categorical structure each time. We treat that variance as a finding about how the model responds to elicitation, not as data to discard. Models with low within-model output concentration are shown without confidence ellipses on the cross-model map; the methodology page explains why."*

The prose must not: (i) frame R1-b or R1-c as defects or "noise"; (ii) frame the visual treatment as "we couldn't compute uncertainty for these models"; (iii) imply that R1-a is the "good" state and R1-b / R1-c are the "bad" states.

**SME content verdict at T13:** the prose is checked for the failures-as-findings posture at the R1-state surface.

---

## Carry-forward of prior binding notes (Phase 5 inventory)

| Note | Origin | Binding scope on Phase 5 |
|---|---|---|
| **B6 (a)–(e)** (T4-redo public-copy guardrails) | T4-redo SME verdict chain (B6 (e) added at T14 of T5-redo) | **BINDING on T2 (lede prose) and T13 (methodology summary).** Reviewer's standing vocabulary scan applies. |
| **T8** (RD-3 descriptive-shape discipline) | T4-redo RD-3 SME content verdict | **BINDING on T2 prose and T13 prose.** |
| **T9** (RD-3 forbidden softer-than-thinks/believes verbs) | T4-redo RD-3 SME content verdict | **BINDING on T2 and T13.** Reviewer vocabulary scan. |
| **T11** (numerics-vs-interpretation framing-guard sentences at table boundaries) | T5-redo SME plan verdict | N/A on T2 (no tabular surface in 1-sentence ledes). **BINDING on T13** if the methodology summary references any tabular surface, which at 5–7 sentences is unlikely but possible. |
| **T12** (S2 four-state enumeration or S2 citation by file path for any `thoughts_token_count=0` discussion) | T5-redo SME plan verdict | N/A — Phase 5 publish layer does not surface `thoughts_token_count`. |
| **T13** (verbatim grep command for cell-coverage denominators in audit-trail surfaces) | T5-redo SME plan verdict | N/A — Phase 5 dashboard does not surface cell-coverage denominators (those land at the methodology page in Phase 6 or in the open-data-bundle README). |
| **T14** (no "publishable" framing) | T5-redo SME plan verdict, B6 (e) | **BINDING on T2 and T13 prose.** Reviewer vocabulary scan. |
| **T15** (Note G verbatim wording preservation if Phase 4a Note G surfaces are quoted) | T5-redo SME plan verdict | **APPLIES IF** Phase 5 prose quotes Phase 4a Note G language ("produced no interpretable primary-step output"); likely N/A at the T13 5–7 sentence scope. If quoted, T15 binds. |
| **A1–A6** (no-human-baseline + §1.5-deepening amendment) | 2026-05-07 amendment | **SATISFIED globally.** Permanently encoded in doc state. T13 must respect §1.5; does not need to re-encode. |
| **Note A** (small-n caveat) | F1 SME review | **BINDING on T2 (per Q2) and T13 (per Q9).** Both 0.2 corpora trip `romney_small_n_warning`. |
| **Note D** (no ceiling claims pre-Phase-4c) | F1 SME review | **SATISFIED-by-amendment.** Phase 4c removed. T13 does not need to disclaim ceiling-pending. |
| **P1–P8** (Phase 4b notes) | Phase 4b SME plan verdict | N/A — Phase 4b notes bind on the Phase 4b T1 / T4 / T6 / T7 surfaces; Phase 5 does not exercise them. The forward-carry to ARCHITECTURE.md §5.3 (the §5.3 doc-update post-Phase-4b) is **a separate Architect amendment**, not a Phase 5 task. |

---

## New binding notes — Phase 5 inventory (Q1–Q11)

The Phase 5 publish-layer + dashboard ship introduces methodology obligations not yet in the binding-note inventory. Numbered Q1–Q11 to keep the Phase 5 series distinct from the parent T4-redo / T5-redo / amendment / Phase 4b series. None require schema changes or scope expansion.

| Note | Trigger | Reviewer-enforced or SME-content-enforced |
|---|---|---|
| Q1 (T2 schema-literal branch predicates) | T2 | Reviewer (rejects `"NO_CONSENSUS"` string) + SME content verdict |
| Q2 (small-n surface in lede or SourceAttribution) | T2 (and T10 if option (b)) | SME content verdict at T2; Reviewer at T10 if option (b) is chosen |
| Q3 (descriptive-locational vs convergence-to-truth framing in lede) | T2 | SME content verdict |
| Q4 (top_freelist_terms salience-rank choice explicit) | T3 | Reviewer (rejects implicit metric) |
| Q5 (R1-b count surfaced in strong-consensus lede; majority-R1-b sub-branch) | T2 | SME content verdict + Reviewer (test fixture for holidays asserts R1-b surface) |
| Q6 (B6 / T8 / T9 / T11 / T14 carry-forward on T13 prose) | T13 | SME content verdict + Reviewer vocabulary scan |
| Q7 (corpus-lens five-link chain readable in T13 prose) | T13 | SME content verdict |
| Q8 (tagline verbatim integrity, US-English "categorize") | T13 | Reviewer (constant character-for-character match against ARCHITECTURE.md §1.5) |
| Q9 (small-n posture acknowledged in T13, descriptive not defect frame) | T13 | SME content verdict |
| Q10 (CDA ancestry signal in T13 prose, full roster deferred to Phase 6) | T13 | SME content verdict |
| Q11 (failures-as-findings posture surfaced at R1-state visual treatment in T13 prose) | T13 | SME content verdict |

**SME content verdict surfaces:**
- **T2** — three (or four/five per Q1 ruling) lede sentence patterns. Reviewed at the T2 dispatch packet.
- **T13** — 5–7 sentence MethodologySummary prose. Reviewed at the T13 dispatch packet.

These are the two methodology-bound text surfaces in Phase 5. Both are gated on a separate SME content verdict in addition to this plan-level verdict.

---

## Proactive checks

### Check 1 — Forbidden-vocabulary scan of the plan body

I scanned the plan body (705 lines including code blocks and the dependency graph) for §1.5.4 / CLAUDE.md §7 violations, including the amendment-added rows (11–12) and the Phase 4b-binding additions:

- "worldview" / "believes" / "thinks" applied to models — zero occurrences.
- "within-model consensus" / "within-model cultural consensus" / "within-model eigenratio" / "within-model CCM" — zero occurrences. The plan correctly uses "within-model output concentration" (T2 §1.3 and §3.3.5 reference) and "OCI" by name (T3 derived fields, T6 marker rendering).
- "publishable" — zero occurrences.
- "closer to human = better" — N/A (no human baseline in scope per the 2026-05-07 amendment).
- "LSB hypothesizes" / "LSB tested whether" / "LSB confirms" / "LSB found that [hypothesis]" / "LSB predicted X" — zero occurrences.
- "the model decided / chose / preferred" (B6 internal-state phrases) — zero occurrences.

The plan body itself passes vocabulary compliance. PASS.

### Check 2 — Register compliance scan

The plan is consistent with the three-register framework:

- **Register 1 (within-model output distribution analysis):** OCI used as the within-model concentration descriptor; §3.3.5 R1-state rendering correctly cites OCI as a concentration statistic, not consensus. PASS.
- **Register 2 (between-model categorical structure analysis):** The cross-model MDS plot is the headline visualization; `consensus_type` and `romney_eigenratio` are the Register 2 measures. The plan correctly attributes the cross-model claim to Register 2. PASS.
- **Register 3 (longitudinal drift):** Out of scope for Phase 5. The plan §10 explicitly defers `DriftTracker.tsx` and `DateSlider.tsx` to Phase 6. PASS.

OCI is consistently used as a within-model concentration descriptor in the §3.3.5 visual treatment. The plan does not apply RWB CCM at Register 1. PASS on register compliance.

### Check 3 — §4.2 binding constraint (LLM-in-cdb_publish allowed; LLM-in-cdb_analyze forbidden)

The plan §1.3 correctly notes that the §4.2 binding is on `cdb_analyze`, not `cdb_publish`, and that the lede generator deliberately lives in `cdb_publish` for forward compatibility with the Phase 6 LLM lede swap. The architectural framing is correct.

A potential ambiguity: the plan T1 acceptance criterion (f) reads "`python scripts/check_no_llm_imports.py` passes — `cdb_publish` may import LLM client libraries in a future task, but T1 introduces none." This is correct — `cdb_publish` is **not** subject to the `cdb_analyze` boundary rule, so the static import check on `cdb_analyze` is the constraint, not a check on `cdb_publish`. The Coder reading T1 should not interpret the acceptance criterion as forbidding LLM client libraries in `cdb_publish` in Phase 5; the prohibition applies only to `cdb_analyze`. The plan's framing is technically correct but could read as ambiguous. Not a binding note — flagging for the Reviewer at T1 commit review.

### Check 4 — n_models against Romney small-n threshold

- Family: n=11 models. Below n=15 small-n threshold. `romney_small_n_warning: true` correctly set in the corpus.
- Holidays: n=9 models. Below n=15. `romney_small_n_warning: true` correctly set.

Both 0.2 corpora trip the warning. The Phase 5 publish layer must surface this (Q2 and Q9 above). PASS on the data state; binding notes Q2 / Q9 cover the surface.

### Check 5 — R1-state distribution across the two domains

Inspection of the 0.2 corpora:

- **Family (n=11):** all 11 models are R1-a (`oci ≥ 3.0` AND `deterministic_output: false`). The plan T6 acceptance criterion 2 asserts "the §3.3.5 item 6 all-deterministic edge case is **not** triggered by either domain (family + holidays both have at least one R1-a model)." This is correct for family.
- **Holidays (n=9):** 7 models are R1-a; 2 models are R1-b (one with `oci: 0.0`, one with `oci: 2.55`). No R1-c models. The plan T6 acceptance criterion 2's "at least one R1-a model" is correct for holidays. But the plan does **not** mention the two R1-b models, and the lede pattern set does not handle the R1-b case — this is the basis for binding note Q5.

### Check 6 — Schema-literal `ConsensusType` enumeration

The plan §1.3 references `consensus_type == STRONG_CONSENSUS` and `consensus_type in {WEAK_CONSENSUS, NO_CONSENSUS}`. The actual `ConsensusType` Literal in `cdb_core/schemas.py` line 200–210 has six values: STRONG_CONSENSUS, WEAK_CONSENSUS, SUBCULTURAL, TURBULENT, CONTESTED, DETERMINISTIC. `NO_CONSENSUS` is not a member. The plan's enumeration is incorrect against the schema. This is the basis for binding note Q1.

### Check 7 — Tagline character-for-character integrity

The plan §1.7 quotes the tagline as: *"LSB measures what frontier LLMs produce when asked to **categorise**, in a way that's reproducible, comparable across models, and trackable across time."* (UK English, "categorise" with -s-).

ARCHITECTURE.md §1.5 line 86 has: *"LSB measures what frontier LLMs produce when asked to **categorize**..."* (US English, "categorize" with -z-).

Single-character drift between the plan and the canonical doc. The Coder must use the canonical US English spelling from ARCHITECTURE.md §1.5. This is the basis for binding note Q8.

### Check 8 — Cost transparency

I do not block on cost. Phase 5 does not call the model API at all (no LLM lede in Phase 5; the Phase 6 LLM lede generator will incur a marginal cost when added). Phase 5 cost is dominated by the dashboard development effort, not API spend. The plan's manual-deploy posture (§1.5) is consistent with the §6.2 cost-posture principle. No cost concern flagged.

### Check 9 — Philosophy doc §9 release-for-community-analysis posture survival

The plan §1.7 cites the §1.5 tagline verbatim. The plan §1.6 anchors the model-count framing at the data-derived number, not a thesis-shaped figure. The plan §10 enumerates forbidden scope creep cleanly. The plan §1.3 frames the lede generator as an output formatter, not as an analytical interpreter — which preserves §4.2 binding and §1.5.7 exploratory framing.

The plan body's voice is descriptive ("Phase 5 ships against the existing 0.2 corpus", "the dashboard reports the actual count from `len(domain_result.models)`"), not predictive. PASS.

### Check 10 — Schema field availability for the publish layer

I confirmed the `DomainResult` schema contains:
- `consensus_type: ConsensusType | None` (line 360)
- `romney_eigenratio` (line ~358 area)
- `romney_small_n_warning` (carried in published JSON)
- `within_model_results: list[WithinModelResult]` (consumed by T3 derived.py)
- `mds_coordinates`, `mds_uncertainty` (consumed by T6 MDSPlot)
- `groundings: list[GroundingRef] = []` (empty for v1; the plan correctly does not consume this in Phase 5)

The schema supports the Phase 5 publish-layer needs without modification. R7 (DATA_DICTIONARY lockstep) is vacuously satisfied because no schema change is in scope. PASS.

### Check 11 — Cross-domain salience-metric consistency

`data/results/family/0.2.json` carries both `smiths_s` and `sutrop_csi` (line 10026 confirmed). Holidays carries the same fields. The publish layer's `top_freelist_terms` choice (Q4) is methodology-bound; both metrics are available in the corpus. The Coder choice between Smith's S and Sutrop CSI does not require a schema change. PASS on availability; Q4 binds the choice discipline.

---

## Final disposition

**Verdict:** PASS-WITH-NOTES.

**Phase 5 Coder dispatch:** AUTHORIZED on T1, T3 (after Q4 addressed), T4–T12 (UI/UX-gated, not SME-gated). T2 and T13 are gated on a **separate SME content verdict** at the dispatch-packet stage, taking Q1–Q5 (T2) and Q6–Q11 (T13) into account.

**Binding notes summary:**

| Note | Trigger | Reviewer- or SME-enforced |
|---|---|---|
| Q1 | T2 | Reviewer + SME content |
| Q2 | T2 (+ T10 if option b) | SME content + Reviewer |
| Q3 | T2 | SME content |
| Q4 | T3 | Reviewer |
| Q5 | T2 | SME content + Reviewer (fixture) |
| Q6 | T13 | SME content + Reviewer vocab scan |
| Q7 | T13 | SME content |
| Q8 | T13 | Reviewer (verbatim constant match) |
| Q9 | T13 | SME content |
| Q10 | T13 | SME content |
| Q11 | T13 | SME content |

**Carry-forward summary:** B6 (a)–(e) BINDING on T2 + T13; T8 / T9 / T14 BINDING on T2 + T13 prose; T11 BINDING on T13 if tabular surfaces appear; T15 APPLIES IF Note G language quoted; A1–A6 SATISFIED-globally; Note A BINDING on T2 + T13 (small-n caveat); Note D SATISFIED-by-amendment. P1–P8 N/A (Phase 4b surfaces, not Phase 5).

**Forward-carry to post-Phase-5:**

- The Phase 6 methodology page (`MethodologyPage.tsx`) is the surface where the corpus-lens five-link chain enumerates in full, the five originators of CDA are cited individually, and the §3.3.5 R1-state explainer prose lands. The Phase 5 T13 MethodologySummary block is the inline preview of that page; the full page is Mark's prose in Phase 6.
- The Phase 6 LLM lede generator (deferred from Phase 5 per plan §1.3) requires its own SME plan-level verdict on the lede prompt template (`packages/cdb_publish/prompts/v1/lede.md`) before it is exercised. That is a separate Architect plan.
- The 0.3 re-analysis (after Phase 4b T4 follow-up campaign) is the next data state; the Phase 5 publish layer's manifest/version-swap discipline (plan §1.1) is the mechanism by which 0.2 → 0.3 ships without a frontend rebuild.

**Posted to `#lsb-cda-sme`. Binding for Phase 5. The Coder is authorized to dispatch on T1 immediately. T2 and T13 are gated on the architect publishing the prose draft packets for SME content review.**

---

*End of CDA SME plan-level verdict for Phase 5. The next SME gates are the content verdicts on T2 (lede sentence patterns) and T13 (methodology summary prose) at the respective dispatch packets.*
