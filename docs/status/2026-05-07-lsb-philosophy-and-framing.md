# LSB Philosophy and Framing — Source-of-Truth Document

**Date:** 2026-05-07
**Authors:** Mark (originating decisions and framing); orchestration agent (architectural grounding and articulation)
**Status:** Canonical source for LSB's philosophical framing. Quotable by the Architect when drafting amendments to `ARCHITECTURE.md` §1.5 and by any Coder writing methodology-page text. Supersedes any earlier philosophical statements that conflict with this document.

**Companion docs:**
- `ARCHITECTURE.md` §1.5 (binding framing on all generated text — to be expanded per this document)
- `CLAUDE.md` §1, §6, §7, §9 (binding rules and forbidden vocabulary)
- `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md` (the parked v2 prompt observation referenced under §1.5)
- `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md` (the RD-3 reframing memo, the first methodology-bound text written under the corpus-lens framing — the model for future methodology-bound text)

---

## §1. The decision Mark made (2026-05-07)

LSB will **not** include a human cultural-consensus baseline as a comparison axis. Phase 4c (human baseline acquisition from anthropological literature) is removed from the project. Romney / D'Andrade / Weller / Borgatti / Batchelder remain as ancestry credit on the methodology page — they invented the protocol LSB borrows — but their published cultural-consensus matrices are not used as comparison data inside LSB.

**Why:** the human baseline is a Trojan horse for the cognition framing the project explicitly disclaims. Putting a human cultural-consensus matrix next to a model's output on the same axis implicitly invites the reader to ask "how close to human ground truth is this model?" That question only makes sense if you grant the model is *knowing* something in a way commensurable with human knowing — which §1.5 forbids. The skeptical reader's strongest possible critique of LSB ("you're pretending to do anthropology on machines") gets its surface area from the human baseline. Remove the baseline, remove the surface area.

**What this means architecturally:** every domain on the dashboard is, permanently, model-to-model. No "grounded vs ungrounded" state distinction. No researcher submission of human baselines. The benchmark's claim sharpens from "how models compare to human baselines, where available" to "how models' corpus lenses compare to each other on the categorical shape of named domains."

## §2. The exploratory framing Mark started with

LSB is **not hypothesis-testing.** It does not predict in advance what models will produce, then test whether they produce it. It does not have a falsifiable claim about model cognition, model bias, or model alignment that the data is designed to confirm or refute.

The originating question is exploratory: **"what happens if you give a large language model a CDA free-list / pile-sort / interview? What comes out?"**

This framing is methodologically the cleanest, and it is binding on every public-facing piece of text the project produces. The methodology page, the README, the social posts, the dashboard copy, the open-data-bundle README — all of these say *"we ran the protocol; here is what came out; draw your own conclusions."* They do **not** say *"we hypothesized X and confirmed it"* or *"this proves Y about LLMs."*

The intent is to **release the information to the community for their own analysis.** LSB ships:
- Verbatim prompts (CC0)
- Verbatim model responses (CC-BY-4.0 in the open-data bundle)
- Reproducible numerics (Smith's S, Romney CCM, MDS, Procrustes, OCI, bootstrap CIs, with bootstrap configuration documented)
- Code under permissive license (Apache 2.0)
- A methodology page that names what was measured and what was *not* measured, in plain language

Researchers, journalists, auditors, and skeptics can take that material and form their own interpretations. LSB does not gatekeep interpretation. The benchmark exists to make the *comparison itself* reproducible at the level of measurement, not to push a thesis.

## §3. What an LLM architecturally is

A transformer LLM at inference is a function from a token sequence to a probability distribution over the next token. The weights are billions of parameters that, in training, were optimized to make the model's predicted distribution match the actual next-token distribution of a massive text corpus. Training "knowledge" lives in two places:

1. **The embedding space.** Every token is mapped to a high-dimensional vector. Tokens that occur in similar contexts during training end up with vectors that point in similar directions. This is a brute-force consequence of next-token prediction — words used similarly cluster together in vector space because that's what makes the loss go down.

2. **The attention pattern.** When generating a token, the model attends to previous tokens via learned attention heads. Different heads specialize in different relational patterns (some attend to syntactic structure, some to long-range coreference, some to topic, some to specific co-occurrence patterns). The aggregate attention pattern over many heads, integrated across many layers, is what determines which tokens get high probability in any given context.

There is nowhere in this architecture that stores "this is what a family is." There is no symbolic representation of family, no concept node, no category boundary. What there is: a statistical surface where, given the prompt context "list every family term you can think of," the high-probability completions are tokens that frequently followed similar prompts in the training corpus — *mother*, *father*, *sister*, *aunt*, etc.

Modern frontier models add another layer: **RLHF / instruction tuning.** After base training, the model is fine-tuned on human-rated responses so its output distribution shifts toward what humans rated as helpful. This means the "list family terms" output is shaped by both (a) raw corpus statistics and (b) human raters' preferences for what a "good" list looks like. The corpus statistics already encode "people writing about families tend to mention these words," and the alignment process additionally encodes "people who rate AI outputs prefer organized, sensible-looking lists."

## §4. The corpus lens — unpacked

The phrase "corpus lens" in `ARCHITECTURE.md` §1.5 is doing real work. It is **not** the corpus directly (we have no access to the corpus, and the corpus is itself only a sample of writing, not of cognition). It is **not** a transparent window onto human cultural consensus (the corpus is not a faithful sample of human cognition).

The corpus lens is the entire chain compressed into a function:

> **corpus → training → alignment → decoding → output distribution**

When LSB elicits a free-list or pile-sort from a model, it is observing the shadow this chain casts when the CDA stimuli are shone at it. Every link in the chain contributes to the shape of the shadow:

- **Corpus** — what text was used in training (web scrapes, books, code, etc.), in what proportions, with what filtering.
- **Training** — the next-token prediction objective at trillions-of-tokens scale, which has the side effect of compressing extremely complex statistical patterns into the weights.
- **Alignment** — RLHF, DPO, or other fine-tuning processes that shape the model's output distribution toward human raters' preferences for helpfulness, harmlessness, honesty.
- **Decoding** — temperature, sampling strategy, stop tokens, system prompt residuals.
- **Output distribution** — the probability landscape over token sequences, from which a sample is drawn each time the model is queried.

When the methodology page (or the Coder writing it) uses the phrase "corpus lens," it must be readable by a skeptical reader as *this five-link chain*, not as a euphemism for "what the model knows."

## §5. What CDA-on-LLM measures, precisely

The CDA protocol — free-list, pile-sort, interview — was designed to elicit *cultural-domain structure* from human informants, on the premise that humans have a learned categorical organization of their cultural world that's stable enough to measure across people and gives a meaningful signal when measured.

When the same protocol is run on an LLM, it does **not** measure the LLM's cultural categorical organization, because there isn't one. What it DOES measure, precisely:

> **The shape of the model's output distribution when prompted with CDA stimuli, at a particular sampling temperature, under a particular prompt template, at a particular model checkpoint.**

That shape reflects, through significant compression and distortion:
- Frequencies and co-occurrences in the training corpus
- The model's learned embedding geometry (which clusters concepts that appeared in similar contexts)
- The attention patterns that route relational information
- The alignment process's sculpting toward "organized list-like answers"
- The decoding configuration

Numbers that fall out of CDA-on-LLM (Smith's S, Romney eigenratio, MDS coordinates, Procrustes RMSE, OCI) are interpretable as **descriptive statistics of this output-distribution shape.** They are not interpretable as measurements of cognition, belief, understanding, or cultural consensus.

## §6. What LSB does NOT measure (the §1.5 forbidden inferences)

LSB explicitly does not measure:

- **What the model "thinks" or "believes."** There is no thinking, no believing.
- **The model's "worldview."** There is no view, no world.
- **Whether the model "understands"** the domain. It produces tokens that, given the prompt context, have high predicted probability.
- **Cultural worldview** of the model or its training population. The training corpus is not a faithful sample of any culture's cognition — it is a sample of writing, biased by who writes, what gets digitized, what gets included in training.
- **Whether the model is approaching human-level cognitive performance** on cultural categorization tasks. The comparison frame is invalid.
- **What humans believe about the domain**, by proxy through model output. The corpus is not a human-belief survey.

The corresponding forbidden vocabulary list (already in `CLAUDE.md` §7 and `ARCHITECTURE.md` §1.5.4) is binding on every piece of generated text. The Reviewer rejects on detection.

## §7. What LSB DOES tell us — the genuinely valuable part

Despite all the disclaimers, CDA-on-LLM produces real and interesting findings:

1. **Comparative model characterization.** Different models, trained on different corpora with different alignment, produce measurably different output-distribution shapes when given identical CDA stimuli. This is an empirical fact about the *systems*. It is the kind of fact a system auditor, a research engineer, or a journalist comparing AI products legitimately wants to know.

2. **Drift detection.** When a model snapshot rolls (silent updates under a moving alias — the `model_id` vs `model_version_returned` distinction in `CLAUDE.md` §9 pitfall 1), the output-distribution shape can shift. CDA-on-LLM is one of the few public, reproducible ways to *measure* that shift over time. The DriftTracker in Phase 6 is the dashboard expression of this.

3. **Stability under prompt rephrasing (G1).** Some models produce categorical structure that is robust to prompt-variant rephrasing; others do not. That tells you something useful about the model's behavior in deployment — a model whose output structure varies wildly with prompt phrasing is differently risky than one whose output is stable.

4. **Confabulation under blind-spot conditions.** The RD-2 finding from 2026-05-05 — that 9 cells under cap-exhaustion produced "the instructions made me do it" narratives — is itself a finding about how the model's output distribution responds to ambiguous-context prompts. The CDA interview-step elicitation methodology happens to surface this well.

5. **A reproducible public benchmark.** "Reproducible measurement" is a low bar, but it is a bar mostly unmet in the LLM-comparison space. LSB produces verbatim prompts, verbatim responses, named methodology, citable measurements. The benchmark exists not to make cognition claims but to make *the comparison itself reproducible* — so a journalist or researcher quoting "Claude Opus 4.6 has Smith's S = 0.71 on family" can be checked.

## §8. The honest tagline

> **LSB measures what frontier LLMs produce when asked to categorize, in a way that's reproducible, comparable across models, and trackable across time.**
>
> It measures output behavior under structured elicitation. It does not measure cognition, understanding, belief, worldview, or cultural consensus, because the LLM has none of those things — and even if you thought it did, this protocol would not be the way to measure them.
>
> The originating question is exploratory: *"what happens if you give a large language model a CDA free-list / pile-sort / interview? What comes out?"* LSB answers that question precisely, reproducibly, and at scale across models and time, and releases the data for the community to interpret.

This tagline is the source for any short-form summary the project produces (homepage hero copy, README first paragraph, social posts, conference-style abstracts). When the methodology-page Coder writes the short summary, this paragraph is the source.

## §9. Why this is still worth doing — the "release-for-community-analysis" intent

Mark's intent: **we are not the final interpreters of LSB's data.** We run the protocol, we publish the measurements, we publish the verbatim prompts and responses, we publish the analytical code. Researchers, journalists, auditors, and skeptics can take that material and form their own interpretations.

The reasons this is valuable:

- **Models are increasingly used as components in systems that affect humans.** Knowing what categorical structure they produce when asked is useful for system designers (understanding what their components default to), auditors (detecting drift, divergence), researchers (studying training-data effects), journalists (reporting on model differences in a measurable way).

- **The LLM-comparison space is mostly unmet by reproducible measurement.** Most "LLM benchmark" output is either task-performance-based (which is informative about capability but not about categorical-output behavior) or is qualitative comparison ("model A is more verbose than model B"). LSB occupies a niche: structured, reproducible, non-task-performance measurement of output-distribution shape, with full provenance.

- **Drift over time is invisible without measurement infrastructure.** A model's output distribution can shift across versions, across snapshot rolls, across alignment-tuning rounds. Without reproducible measurement, that shift is invisible. LSB's longitudinal posture (DriftTracker, the date-slider scrubbing view) makes shifts visible.

- **The data is more valuable than our interpretation of it.** This is the deepest reason. LSB does not need to be the place where conclusions are drawn — it needs to be the place where the *raw material for conclusions* is reliably produced, documented, and made open. Other researchers will find uses we did not anticipate. The benchmark's value compounds the more it is reused.

The release-for-community-analysis intent is what makes LSB a website-as-research-instrument rather than a paper. A paper presents conclusions. A website presents reproducible measurements and lets the community draw conclusions. That distinction is binding on the project's design.

## §10. What this means for upcoming work

The Architect amendment that drafts after this document lands will encode all of the above into:

1. **`ARCHITECTURE.md` §1.5 expansion** — five-link corpus-lens chain made explicit; exploratory-not-hypothesis-testing framing made explicit; "honest tagline" §8 above quoted as the canonical short form.

2. **`ARCHITECTURE.md` §4.2.5 + §5.3 Phase 4c removal** — human baseline acquisition deleted; `groundings: list[GroundingRef]` schema retained but defaulted to empty list permanently.

3. **`PHASE_4C_CANDIDATE_SOURCES.md`** — repositioned as ancestry credit (Romney / D'Andrade / Weller / Borgatti / Batchelder), or deleted entirely depending on Architect call.

4. **`DESIGN_SYSTEM.md` State 0/1/many framework collapse** — single state (model-to-model) only; "Submit your data" entry points removed.

5. **`CLAUDE.md` §6 R15** — researcher grounding submission rule removed or repositioned; PR template at `.github/PULL_REQUEST_TEMPLATE/grounding_submission.md` removed.

6. **`docs/grounding_submission_template.md`** — removed.

7. **CLAUDE.md §9 pitfalls 3 and 4** — repositioned as historical context; the empty-baseline framing is no longer a special case because there is no baseline frame at all.

8. **Methodology-page §6 outline item ("Human grounding")** — replaced with "What this measures and what it does not" — drawing on §5 + §6 + §8 of this philosophy document.

The amendment is one Architect plan, one CDA SME PASS pass, and one or two Coder commits for the doc updates. No code change. No schema change. The schema's `groundings: list` semantic is unchanged — it just defaults to empty everywhere.

---

*End of LSB philosophy and framing source-of-truth document. This document is canonical for §1.5 framing and is to be quoted, not re-articulated, when the Architect or any Coder writes methodology-bound text.*
