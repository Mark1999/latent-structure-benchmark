# CDA SME Verdict — No-Human-Baseline + §1.5-Deepening Amendment (plan-level review)

**Filed:** 2026-05-07
**Reviewer:** CDA SME (Opus)
**Plan reviewed:** `docs/status/2026-05-07-no-human-baseline-amendment-architect-plan.md` (commit `6d99da0`)
**Source-of-truth document under review:** `docs/status/2026-05-07-lsb-philosophy-and-framing.md` (commit `d014112`)
**Slack channel:** `#lsb-cda-sme`
**Predecessor verdicts (still binding, in dependency order — abridged):**
- `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md` (T4 redo plan; B6, B11 REPLACED, B12, B14 carry forward)
- `docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md` (RD-3 reframing memo; T8 descriptive-shape discipline, T9 phrasing exclusions; S5 SATISFIED)
- `docs/status/2026-05-06-t5-redo-cda-sme-plan-verdict.md` (T5 redo plan; T11–T15 added)
- `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (S2 four-state taxonomy)

---

## VERDICT: PASS-WITH-NOTES

| Axis | Result |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | PASS |
| Axis 3 — Claims validity | PASS |
| Axis 4 — Audience translation | PASS-WITH-NOTES |
| Register compliance | PASS (registers untouched; §4.2.0 three-register framework not amended) |
| Vocabulary compliance | PASS (plan itself contains no forbidden vocabulary; the philosophy doc itself contains no forbidden vocabulary in claim form) |

The Coder is **AUTHORIZED** to start the single-task amendment on this verdict, subject to the new binding notes A1–A6 below and to all carry-forward notes from prior verdicts. The plan is methodologically sound, the philosophy doc holds up under scrutiny, the Architect's Q1–Q9 recommendations are nearly all correct, the UI/UX bypass is correctly reasoned, and the one-commit decision is correctly defended.

PASS-WITH-NOTES rather than PASS for one structural reason: **the audience-translation axis carries the highest load in this amendment** — the README first paragraph is the project's most-read line, the §1.5 honest-tagline block becomes the canonical short-form for everything downstream, and the §1.5.7 exploratory-framing sub-section is the new visible anchor that future ledes will quote. The Coder's prose discipline matters more here than in any prior amendment. Six new binding notes (A1–A6 below) tighten the framing where the philosophy doc's prose passes through transitions or relies on quotation discipline. None of A1–A6 block the Coder from starting; all are content-level disciplines verified by the SME content verdict at gate chain step 3.

The four risks that gate this amendment's audience-translation axis:

1. **Drift from the philosophy doc's framing into freshly-improvised methodology prose.** The philosophy doc is the canonical source; the Coder must quote, not re-articulate. The plan §7 acceptance criteria 1, 2, 3, 4, 5 enforce this; A1 reinforces the discipline at the boundary where philosophy doc text becomes ARCHITECTURE.md text.
2. **The §1.5.5 transition sub-section reading as "we deleted this" rather than "we made a positive decision."** The Architect's plan §5.1.a anticipates this and mandates the philosophy doc §1 quote; A2 tightens the framing posture.
3. **The "honest tagline" being mis-truncated in the README first paragraph.** The full three-paragraph tagline is too long for README; the first sentence alone is the right truncation, but the surrounding §9–13 must remain coherent post-edit. A3 specifies the truncation discipline.
4. **The new §1.5.7 sub-section's verbatim quote of philosophy doc §2 plus §9 reading as two stitched paragraphs without a unifying §1.5.7-voice introduction.** A4 mandates a single-sentence framing introduction in §1.5.7's own voice before the verbatim quote begins.

A5 and A6 cover smaller disciplines (§4.2.5 archival posture wording; §1.5.4 forbidden-vocabulary table extension under the new framing).

---

## (B) Q1–Q9 explicit rulings

### Q1 — `PHASE_4C_CANDIDATE_SOURCES.md`: delete entirely or reposition?

**Architect recommendation:** delete entirely.

**SME ruling: AGREE.**

The Architect's reasoning is correct. Three reasons:

1. **The doc's structural framing is "Phase 4c acquisition workflow."** A repositioned doc would either retain that framing (incoherent under the amendment) or require gutting and retitling, which is a separate Architect plan. The cleanest move is deletion.

2. **Ancestry credit is shorter than acquisition documentation.** The methodology-page outline already names the originators (DESIGN_SYSTEM.md §6.1 item 2: "Romney, D'Andrade, Weller, Borgatti: named and cited"). That's the right surface for ancestry credit. A separate `CDA_ANCESTRY_CREDIT.md` would create a redundant pointer.

3. **The deleted file's content is preserved in git history.** A future reader who wants to know what the v0.7 grounding-acquisition plan looked like can run `git show 6d99da0^:PHASE_4C_CANDIDATE_SOURCES.md`. The audit trail survives.

I confirm DELETE. The plan §5.7 disposition is correct.

### Q2 — `docs/DATA_DICTIONARY.md` `GroundingRef` description: retain with editorial note vs trim?

**Architect recommendation:** retain with top-of-§3 gloss only.

**SME ruling: AGREE.**

The data dictionary's job is to document the schema as it exists in code. The schema is unchanged (§5.1.c spec confirms). The 18+ field-level descriptions in §3 (sub-sections 3.1 through 3.8) document a schema field that still exists, still validates, and is still serializable. Trimming them creates a documentation gap that would re-emerge if the field is ever exercised (a researcher submission off-roadmap, an open-data-bundle consumer reading the schema). Retention with an editorial note is the surgical move.

The §5.4.b spec ("Editorial note (2026-05-07). All v1 LSB domains ship with an empty `groundings` list...") is the right wording. I confirm RETAIN with editorial note.

### Q3 — Does this amendment need its own SME content verdict on §1.5 expansion prose?

**Architect recommendation:** yes.

**SME ruling: AGREE — strongly.**

The §1.5 expansion is more sensitive than any prose this project has previously generated. Three reasons:

1. **The honest tagline becomes the canonical short-form everywhere downstream.** Any drift in the tagline's wording propagates into every README, social post, dashboard hero copy, and conference-style abstract that draws from it. The Reviewer's vocabulary scan catches forbidden phrases; the SME content verdict catches *framing drift* — paraphrases that don't trigger the vocab grep but slide the meaning. That is the surface only an SME content review covers.

2. **The five-link corpus-lens chain replaces a four-layer breakdown that has its own SME provenance.** The four-layer breakdown was added post-F1 SME review. Replacing it with the five-link chain changes the operational definition of "corpus lens" project-wide. The SME content verdict checks that the replacement is faithful (Architect plan §3 Q6 argues fidelity; the content verdict verifies the actual prose).

3. **The §1.5.7 exploratory-framing sub-section is a new top-level definition.** New definitions are exactly the kind of content SME content verdicts exist to catch. A new §1.5.7 that quotes philosophy doc §2 cleanly is fine; a new §1.5.7 that paraphrases or summarizes is a content-verdict-rejected drift.

The two-stage gate structure (this plan-pass verdict + post-Coder content verdict) is correct. The file paths in the plan §6 are correct.

I confirm YES on a content verdict, at the path specified by the plan §6: `docs/status/2026-05-07-no-human-baseline-amendment-cda-sme-content-verdict.md`. The content verdict is required after Reviewer + Tester PASS, before Mark merges.

### Q4 — Public-facing texts (README, social, lede): same commit vs forward-carry?

**Architect recommendation:** README in scope; social-pipeline drafts and lede generator templates forward-carry.

**SME ruling: AGREE.**

The Architect's distinction is correct: README.md exists on disk today and references the deleted submission template directly (lines 26, 41, 51, 57, 61–73, 84). Leaving README in a state where it describes "Submit your data" while the template is deleted creates a user-facing incoherence at the most-trafficked surface in the repo. README must update in this commit.

Social-pipeline drafts and lede generator templates do not yet exist (per Architect verification: `packages/cdb_social/` does not exist; `packages/cdb_publish/lede/` does not yet have templates). There is no content to amend; the forward-carry posture is the natural shape. When those packages are first written, they will be SME-gated under the amended §1.5 framing — that future gate will catch any drift then.

I confirm IN-SCOPE for README, FORWARD-CARRY for social/lede.

**Procedural note:** when `packages/cdb_publish/lede/` first lands templates, the SME plan-pass verdict on that task should reference this amendment's `docs/status/2026-05-07-no-human-baseline-amendment-cda-sme-plan-verdict.md` and `docs/status/2026-05-07-no-human-baseline-amendment-cda-sme-content-verdict.md` as the binding framing source. The Architect's plan tracks this implicitly under "Phase 5/6 work"; the cross-reference is explicit here for the future gate.

### Q5 — `data/grounding/` directory: delete, empty placeholder, or retain with banner?

**Architect recommendation:** retain with `data/grounding/README.md` banner.

**SME ruling: AGREE.**

The Architect's reasoning is correct on all four counts:

1. **The data is in git history regardless.** Deleting the directory does not delete the audit trail; it obscures provenance.

2. **The Romney 1996 LICENSE-DATA attribution refers to `data/grounding/family/romney_1996/`.** Removing the directory while keeping the attribution creates a dangling reference. Removing both in the same commit expands scope.

3. **The open-data contract historically promised this directory.** An unannounced delete is a contract break. A README banner is the explicit-acknowledgment move.

4. **Sentimental loss with no architectural gain.** Mark spent time on the extraction. Retention is free.

I confirm RETAIN with banner. The `data/grounding/README.md` text in plan §5.9 is the right shape — four lines, banner-only, no editorializing. The Coder may not exceed those four lines (per plan Risk 7 mitigation; A6 below reinforces this for forbidden-vocab discipline).

### Q6 — "Corpus lens" definition: central paragraph vs expand each use?

**Architect recommendation:** replace the four-layer breakdown in §1.5.1 with the five-link chain from philosophy doc §4 verbatim, with a one-sentence supersession note.

**SME ruling: AGREE — with one fidelity-of-replacement clarification.**

The Architect's faithfulness argument is correct: the five-link chain (corpus → training → alignment → decoding → output distribution) is strictly more explicit than the four-layer breakdown. The four-layer breakdown's "compression and abstraction by pretraining" maps onto "training"; "behavioral shaping by RLHF and constitutional fine-tuning" maps onto "alignment"; "surface expression through temperature-sampled token generation" maps onto "decoding" + "output distribution". The five-link chain adds "decoding" as an explicit link and separates "output distribution" as the actual observed surface; both additions are operationally clarifying.

**Clarification:** the supersession note must use the word "supersedes" (not "replaces" or "deprecates" or "evolves"). The reason: the four-layer breakdown was an SME-binding addition. "Replaces" without a frame leaves a future reader uncertain whether the four-layer formulation was wrong. "Supersedes" is the clean technical-document word for "this is the canonical version now; the prior version was correct against its frame; the new version is more explicit." The Architect's recommended supersession sentence in plan §5.1.a — "Naming them explicitly makes the construct operationally legible and supersedes the prior four-layer formulation" — uses the right word; A1 reinforces it.

The four-layer breakdown's last paragraph ("LSB elicitation operates on Layer 4. What it reveals about Layers 1–3 is a composed inference, not a measurement.") is a methodology-binding sentence the Architect's plan correctly preserves and updates ("The existing post-block sentence is updated to refer to the output-distribution link rather than Layer 4."). The faithful update of this sentence is: *"LSB elicitation operates on the output-distribution link. What it reveals about the corpus, training, alignment, and decoding links is a composed inference, not a measurement."* That preserves the post-F1 SME discipline (LSB measures only the observable surface) while honoring the new five-link vocabulary. The Coder must apply this exact form (or a verbatim paraphrase that preserves both elements).

I confirm REPLACE-IN-PLACE with the five-link chain, with the supersession note using "supersedes" and the post-block sentence updated as above.

### Q7 — Exploratory framing: new §1.5.x sub-section vs fold-in?

**Architect recommendation:** new top-level §1.5.7, "Exploratory framing — LSB does not test hypotheses."

**SME ruling: AGREE — strongly.**

The exploratory posture is a definitional claim about what LSB *is*. Burying it in the §1.5.2 "Why the reframe is stronger, not weaker" prose (the fold-in alternative) demotes it from a definition to a meta-defense. The exploratory posture is the cleaner methodological position than any hypothesis-testing posture LSB might claim, and a dedicated sub-section gives it the visible anchor it needs.

**Composition rule (binding for Coder):** §1.5.7 must contain three elements in this order:

1. **A one-sentence framing introduction in §1.5.7's own voice** (NOT a quote — the Architect's plan §3 Q7 says "preceded by a one-sentence framing introduction in the §1.5.7 voice"). This sentence introduces the verbatim quote that follows. Suggested form: *"LSB is exploratory, not hypothesis-testing. The originating question is descriptive: what comes out when CDA elicitation protocols are run on a large language model?"* — or any structurally equivalent paraphrase that does not introduce new framing claims. A4 below codifies this.

2. **The verbatim quote of philosophy doc §2.** All seven paragraphs (§2 starts at "LSB is **not hypothesis-testing.**" and ends at "The benchmark exists to make the *comparison itself* reproducible at the level of measurement, not to push a thesis."). The originating question (*"what happens if you give a large language model a CDA free-list / pile-sort / interview? What comes out?"*) appears verbatim within this block.

3. **The verbatim quote of philosophy doc §9.** The release-for-community-analysis intent. The Architect's plan §3 Q7 says "Closes with philosophy doc §9 release-for-community-analysis intent quoted verbatim." The §9 block runs from "Mark's intent: **we are not the final interpreters of LSB's data.**" through "That distinction is binding on the project's design." All of §9 should be in §1.5.7, not just the opening sentences.

The §1.5.7 sub-section will be long (≈25–30 paragraphs counting both quoted blocks), which is acceptable — definitional sub-sections of §1.5 are allowed to be long. A4 codifies the three-element composition.

I confirm NEW §1.5.7. The position (after §1.5.6, before §1.6) is correct.

### Q8 — Honest tagline placement: ARCHITECTURE.md, README, both, or neither?

**Architect recommendation:** both.

**SME ruling: AGREE.**

The honest tagline (philosophy doc §8) is the canonical short-form for the project. It belongs in two places for two distinct purposes:

1. **`ARCHITECTURE.md` §1.5 top-of-section as a binding quotable block.** The full three-paragraph tagline. This is the source-of-truth surface; all other docs that need the short-form quote it from here. The Architect's plan §5.1.a placement ("immediately after the §1.5 binding-on-all-generated-text statement, before §1.5.1") is correct.

2. **`README.md` first paragraph as a tightened single-sentence opener.** The full three-paragraph tagline is too long for README's first paragraph; the truncation to the first sentence ("LSB measures what frontier LLMs produce when asked to categorize, in a way that's reproducible, comparable across models, and trackable across time.") is the right shape. A3 below codifies the README truncation discipline so the rest of README's first paragraph remains coherent.

The Architect's plan §5.5.a rewrite is correct in shape. A3 covers the surrounding-paragraph cleanup needed to keep README coherent post-truncation.

I confirm BOTH. The ARCHITECTURE.md placement is verbatim full tagline; the README placement is the first sentence with §9–13 cleanup.

### Q9 — `PHASE_0_TASKS.md` edits: in scope or out?

**Architect recommendation:** in scope, surgical only.

**SME ruling: AGREE.**

PHASE_0_TASKS.md is a binding plan doc. Letting it drift from the new framing for an unknown duration is exactly the kind of cross-doc inconsistency the one-commit decision is designed to prevent. The edit is genuinely surgical (single line in P0-T2 noting that `data/grounding/` retains historical reference data only post-2026-05-07). P0-T3, P0-T5 references to schema documentation requirements remain valid because the schema is unchanged.

I confirm IN-SCOPE for P0-T2 single line. P0-T3 and P0-T5 unchanged.

---

## (C) UI/UX bypass decision (Architect §4)

**Architect ruling:** BYPASS the UI/UX gate.

**SME ruling: CONCUR.**

The Architect's four reasons are correct:

1. **No new visual decision.** Every `DESIGN_SYSTEM.md` edit is a deletion, surgical text rewrite within already-PASSed visual specs, or a comment annotation on existing tokens. The Coder is not asked to pick a new color, font, spacing, marker, or interaction.

2. **State-0 visual treatment is unchanged.** The collapse of States 1, 2, 3 elevates State 0 to the only state; State 0's visual specification is already PASSed and remains intact.

3. **§6.1 outline edit is text-only.** The methodology-page outline is a content list, not a visual layout. Eventually rendering the methodology page is a separate Phase 5/6 task with its own UI/UX gate; that future gate is not pre-empted.

4. **The `--color-baseline-published` and `--color-baseline-researcher` design tokens become dead but remain defined.** Token deletion is correctly deferred to a follow-up cleanup task; doing it now would inflate the diff without architectural gain.

The bypass call is reversible: if anything visual-decision-shaped surfaces during the Coder's work, the Coder pauses and routes to the UI/UX agent. The Reviewer's PR-level scan independently flags any DESIGN_SYSTEM.md edit that introduces or modifies a visual decision outside the deletion scope.

I confirm BYPASS. No UI/UX gate verdict required.

---

## (D) One-commit-vs-several decision (Architect §2)

**Architect ruling:** ONE commit.

**SME ruling: CONCUR.**

The Architect's four reasons are correct:

1. **Coherence.** Every doc updates together. CI never sees an interim state where ARCHITECTURE.md says "Phase 4c is real" while CLAUDE.md says "researcher submission rule removed."

2. **No production risk.** Doc-only edits. No code path altered. No schema migration. The "what if a partial-merge state ships" failure mode does not apply.

3. **Reviewer can scan it in one pass.** The diff is large but each file's edit is bounded. Splitting would force the Reviewer to re-establish context across multiple commits.

4. **Audit trail is cleaner.** A single hash references the philosophy doc, the SME plan-PASS, the SME content-PASS, the Reviewer verdict, the Tester verdict.

I want to add one observation that does not change the verdict but is worth surfacing for the Coder:

**One-commit discipline cuts both ways.** If the Coder discovers mid-edit that the philosophy doc does not say what is needed for some specific surface (e.g., a CLAUDE.md §9 pitfall whose framing is not directly addressed by philosophy doc §1–§10), the Coder must STOP and route the question back to the Architect — not improvise. The single-commit posture means every improvisation lands in this commit; an ambiguity-driven improvisation by the Coder would propagate to all downstream readers. The plan §7 acceptance criteria 1, 2 explicitly forbid new framing language not in the philosophy doc; A1 reinforces this discipline.

I confirm ONE COMMIT. The commit-message template in plan §2 is correctly populated; the Coder applies it verbatim.

---

## (E) Does the philosophy doc hold up to SME scrutiny?

**Verdict: YES, with one editorial observation that is not blocking.**

I read all ten sections of `docs/status/2026-05-07-lsb-philosophy-and-framing.md` against the four-axis scorecard. Section-by-section:

### §1 (the decision Mark made) — PASS

The decision is methodologically clean. The "Trojan horse for cognition framing" articulation is sharper than any prior framing of why human grounding was load-bearing in the wrong direction. The "no surface area for the cognition framing critique" is the right defensive posture. The architectural consequence ("every domain on the dashboard is, permanently, model-to-model") is the operational form. PASS.

### §2 (the exploratory framing) — PASS

The exploratory posture is methodologically the cleanest possible position for a project of this shape. The originating question — *"what happens if you give a large language model a CDA free-list / pile-sort / interview? What comes out?"* — is descriptively framed (no causal claim, no introspective claim, no hypothesis) and survives the T8 (descriptive-shape discipline) test cleanly. The four-item ship list (verbatim prompts, verbatim responses, reproducible numerics, code) is correct under §6.7 Open Data Policy. PASS.

### §3 (what an LLM architecturally is) — PASS-WITH-OBSERVATION

The architectural picture (transformer LLM as token-sequence-to-distribution function; embedding space + attention pattern as the two storage loci; RLHF as a third shaping layer) is consistent with the technical literature and does not over-claim. The §3 last paragraph ("There is nowhere in this architecture that stores 'this is what a family is.' There is no symbolic representation of family, no concept node, no category boundary.") is methodologically the right framing for §1.5 — it explicitly disclaims the cognition picture without resorting to the forbidden vocabulary.

**Observation (not blocking, not a binding note):** §3 paragraph 2 says "Different heads specialize in different relational patterns (some attend to syntactic structure, some to long-range coreference, some to topic, some to specific co-occurrence patterns)." This is empirically true at a coarse level (the mechanistic-interpretability literature documents this) but the granularity claim ("some attend to syntactic structure") is more confident than the literature supports for frontier-scale models. The paragraph reads as descriptive-confident-but-bounded; it is not over-claiming for §1.5's purposes (which is to motivate the "no symbolic representation of family" close), but a careful mechanistic-interpretability reader could flag it. The fix is to soften "specialize in" to "tend to specialize in" or "have been observed to attend to." This is a paraphrase the Coder can apply at quotation time if §3 is quoted in §1.5; if §3 is not quoted directly, the observation does not bind. PASS as written; minor refinement available if the Coder quotes the passage.

### §4 (corpus lens unpacked — five-link chain) — PASS

The five-link chain (corpus → training → alignment → decoding → output distribution) is the right level of granularity: each link is operationally distinguishable, each link contributes a different kind of distortion, and the chain is short enough to memorize. The framing introduction ("It is **not** the corpus directly... It is **not** a transparent window onto human cultural consensus...") correctly closes off the two adjacent misreadings. The chain is strictly more explicit than the existing four-layer breakdown; the supersession is faithful (per Q6 ruling above).

The "every link contributes to the shape of the shadow" framing is excellent — it gives the methodology page reader a single mental picture (shadow projected by a light) that connects directly to the operational claim ("LSB observes the shape of the shadow, not the chain of light-bending"). PASS.

### §5 (what CDA-on-LLM measures, precisely) — PASS

The pinned definition — *"The shape of the model's output distribution when prompted with CDA stimuli, at a particular sampling temperature, under a particular prompt template, at a particular model checkpoint."* — is the tightest definition I have seen for this construct in the project's history. It survives the T8 descriptive-shape test (no causal language, no introspective language). It cleanly distinguishes the measurement from cognition, belief, understanding, cultural consensus. It correctly enumerates the four contextual constants (temperature, prompt template, model checkpoint — and implicitly, the CDA stimuli themselves). PASS.

The follow-up enumeration of the five contributing factors (training corpus frequencies and co-occurrences, embedding geometry, attention patterns, alignment sculpting, decoding configuration) is consistent with §3 and §4. The closing sentence ("Numbers that fall out of CDA-on-LLM are interpretable as descriptive statistics of this output-distribution shape. They are not interpretable as measurements of cognition, belief, understanding, or cultural consensus.") is the right sentence to put at the methodology page's center. PASS.

### §6 (forbidden inferences) — PASS-WITH-OBSERVATION

The list of six forbidden inferences (thinks/believes; worldview; understands; cultural worldview of training population; human-level cognitive performance comparison; what humans believe by proxy through model output) covers the surface area cleanly. Cross-checked against CLAUDE.md §1.5.4 + §7 forbidden vocabulary: the philosophy doc §6 enumerates inferences (what cannot be claimed), CLAUDE.md §7 enumerates phrases (what cannot be said). Both surfaces are covered.

**Observation (not blocking, A5 below codifies):** the ARCHITECTURE.md §1.5.4 forbidden-vocabulary table currently has 10 rows. With this amendment's exploratory-framing addition (§1.5.7), one new family of phrases potentially needs guarding: hypothesis-testing language applied retroactively to LSB findings. Phrases like "LSB hypothesizes," "LSB predicted," "LSB confirms," "LSB tested," "LSB found that [hypothesis]" — these would be vocabulary violations under the new exploratory framing because LSB does not test hypotheses. The §1.5.4 table does not currently guard against these. A5 below recommends adding 1–2 rows to the §1.5.4 table for this surface. The Coder may execute this as part of the same commit (low-risk; small text edit; consistent with the philosophy doc §2's framing) or pause and route to the Architect (preferred if the wording is non-trivial). A5 is the discipline; the Coder's choice.

PASS on the forbidden-inferences list itself. A5 covers the §1.5.4 table extension.

### §7 (what LSB does tell us) — PASS

The five "genuinely valuable" findings (comparative model characterization, drift detection, stability under prompt rephrasing, confabulation under blind-spot conditions, reproducible public benchmark) are defensible against the "this is empty methodology" critique. Each finding is operationally specific (comparative model characterization names the systems-audit and journalism use cases; drift detection cites the model_id vs model_version_returned distinction by name; G1 stability is named explicitly; the RD-2 confabulation finding is cited by date; reproducible benchmark closes the bar at "a journalist quoting Claude Opus 4.6 has Smith's S = 0.71 on family can be checked").

This is the section a skeptical reader most needs to see. PASS without observation.

### §8 (the honest tagline) — PASS

The three-paragraph tagline is the right shape and the right pitch:

- **Paragraph 1** ("LSB measures what frontier LLMs produce when asked to categorize, in a way that's reproducible, comparable across models, and trackable across time.") — the positive-claim short form. Quotable as a single sentence in headlines, social posts, conference-style abstracts.
- **Paragraph 2** ("It measures output behavior under structured elicitation. It does not measure cognition, understanding, belief, worldview, or cultural consensus, because the LLM has none of those things — and even if you thought it did, this protocol would not be the way to measure them.") — the disclaim form. The "and even if you thought it did" clause is the right hedge: it disengages from the metaphysics debate cleanly without conceding the metaphysics.
- **Paragraph 3** ("The originating question is exploratory: 'what happens if you give a large language model a CDA free-list / pile-sort / interview? What comes out?' LSB answers that question precisely, reproducibly, and at scale across models and time, and releases the data for the community to interpret.") — the positive-affordance form. Names the originating question; names the "release for the community to interpret" intent.

Cross-checked against the §1.5.4 forbidden vocabulary: zero violations. Cross-checked against T8 (descriptive-shape discipline): zero causal claims, zero introspective claims. Cross-checked against T9 (forbidden softer-than-thinks/believes verbs): no "recognizes," "identifies," "interprets," or similar verbs applied to the model. Cross-checked against B6 (no "publishable" framing): the tagline says "releases the data for the community to interpret," not "publishes findings." Clean.

The honest tagline is the canonical short-form. PASS without observation.

### §9 (release-for-community-analysis intent) — PASS

The four reasons (models in systems that affect humans; reproducible measurement is unmet; drift over time invisible without infrastructure; data is more valuable than our interpretation) are well-bounded. The fourth reason ("The data is more valuable than our interpretation of it") is the deepest and most defensible — it is the methodological humility move that gives the project structural strength against any future critic who would say "your interpretation is wrong." LSB does not gatekeep interpretation; the data is the deliverable. PASS.

### §10 (what this means for upcoming work) — PASS

The eight items map cleanly onto the Architect plan's per-file edit specifications. No drift between philosophy doc §10 and Architect plan §5. PASS.

### Summary

The philosophy doc holds up. Six new binding notes (A1–A6) tighten Coder discipline at quotation boundaries and at the §1.5.4 vocabulary-table extension surface; none reverse the philosophy doc's framing. The doc is canonical for §1.5 framing and is to be quoted, not re-articulated, when the Coder writes the actual prose.

---

## (F) New binding notes A1–A6

Numbered A1–A6 to start a new amendment-specific series (parallels the T-series for T4 redo, the R-series for the recovery campaign). Total binding-note inventory after this verdict adds 6.

**A1. The "supersedes" word in the §1.5.1 four-layer-to-five-link replacement.**

The Coder's supersession sentence in §1.5.1 must use the word "supersedes" specifically — not "replaces," "deprecates," "retires," or "evolves." The reason: the four-layer breakdown was an SME-binding addition (post-F1 SME review); a generic-replacement word leaves a future reader uncertain whether the four-layer formulation was wrong. "Supersedes" is the technical-document word for "this is the canonical version now; the prior version was correct against its frame; the new version is more explicit." Acceptable phrasings:

- *"...supersedes the prior four-layer formulation."* (Architect plan §5.1.a recommended form — confirmed.)
- *"...supersedes the post-F1 four-layer breakdown."*
- *"This five-link breakdown supersedes the four-layer formulation added post-F1."*

The Coder picks; Reviewer verifies "supersedes" is present; SME content verdict double-checks.

**A2. The §1.5.5 transition sub-section must include the philosophy doc §1 "Trojan horse" quote verbatim.**

Per Architect plan §5.1.a + Risk 8 mitigation. The §1.5.5 rewrite is the section most at risk of reading as "we deleted this" rather than "we made a positive decision." The mitigation is the philosophy doc §1 quote: *"the human baseline is a Trojan horse for the cognition framing the project explicitly disclaims..."* The §1.5.5 sub-section must include this verbatim, not paraphrased. The Coder may not soften "Trojan horse" to "complication" or "concern" — the strength of the metaphor is load-bearing.

The §1.5.5 sub-section structure (binding):

1. One opening sentence in §1.5.5's own voice naming the change ("As of 2026-05-07, human grounding is removed from v1 of LSB.").
2. The verbatim philosophy doc §1 "Trojan horse" passage (the full second paragraph of philosophy doc §1, starting with "Why:" and running through "Remove the baseline, remove the surface area.").
3. The architectural consequence in §1.5.5's own voice ("Every domain on the dashboard is, permanently, model-to-model. The schema's `groundings: list[GroundingRef]` field is retained for forward compatibility but defaults to empty for all v1 domains.").
4. A pointer sentence to ancestry credit ("Romney / D'Andrade / Weller / Borgatti / Batchelder ancestry credit is named on the methodology page per `DESIGN_SYSTEM.md` §6.1 item 2.").

The "Floor and ceiling claims" framing block and the "What follows from this framing" 4-point list are removed entirely (per Architect plan §5.1.a).

The Coder picks the exact phrasing of (1), (3), (4); Reviewer verifies (2) is verbatim and the "Trojan horse" metaphor is preserved; SME content verdict double-checks (1), (3), (4) for descriptive-shape discipline (T8) and forbidden-vocabulary compliance (§1.5.4).

**A3. The README.md first-paragraph truncation must preserve coherence in surrounding §9–13.**

Per Q8 ruling. The README first paragraph (lines 5–7) is being rewritten to open with the philosophy doc §8 first sentence ("LSB measures what frontier LLMs produce when asked to categorize, in a way that's reproducible, comparable across models, and trackable across time."). The current §9–13 ("What LSB is and isn't" through "For the full scientific framing, see ARCHITECTURE.md §1.5.") must remain coherent post-truncation.

Specifically:

- Current line 11 ("LSB **is** a benchmark for the categorical structure of model training corpora, surfaced through CDA elicitation protocols.") survives unchanged. It is the technically-precise long-form companion to the new tagline-derived first paragraph.
- Current line 13 ("LSB **is not** a measure of cultural worldview, belief, or cognition. Models do not have lived experience; they synthesize statistical patterns from text corpora. The methodology page on the dashboard goes into depth on what we measure, what we don't, and why the distinction matters.") survives, but the closing sentence's "what we measure, what we don't, and why the distinction matters" should be re-anchored to the new methodology-page outline item 5 ("What this measures and what it does not"). The Coder may rewrite line 13's closing sentence to: *"The methodology page on the dashboard goes into depth on what this measures and what it does not."*
- Current line 15 ("For the full scientific framing, see [`ARCHITECTURE.md`](ARCHITECTURE.md) §1.5.") survives unchanged.

The Coder's first-paragraph rewrite per Architect plan §5.5.a is the right text. A3 is the discipline that the rest of the "What LSB is and isn't" section remains coherent post-truncation. SME content verdict double-checks coherence.

**A4. The §1.5.7 sub-section composition is three elements in this order: §1.5.7-voice intro, philosophy doc §2 verbatim, philosophy doc §9 verbatim.**

Per Q7 ruling. The §1.5.7 sub-section must contain three composition elements:

1. **One-sentence framing introduction in §1.5.7's own voice (NOT a quote).** This sentence introduces the verbatim quote that follows. The introduction must be one sentence, not a paragraph. Suggested form: *"LSB is exploratory, not hypothesis-testing. The originating question is descriptive: what comes out when CDA elicitation protocols are run on a large language model?"* (The Coder may use this verbatim or a structurally equivalent paraphrase that does not introduce new framing claims.)

2. **The verbatim quote of philosophy doc §2.** All seven paragraphs from "LSB is **not hypothesis-testing.**" through "The benchmark exists to make the *comparison itself* reproducible at the level of measurement, not to push a thesis." The originating question (*"what happens if you give a large language model a CDA free-list / pile-sort / interview? What comes out?"*) appears verbatim within this block.

3. **The verbatim quote of philosophy doc §9.** All four paragraphs from "Mark's intent: **we are not the final interpreters of LSB's data.**" through "That distinction is binding on the project's design." The four-reason enumeration (models in systems / reproducible measurement unmet / drift invisible / data more valuable than interpretation) appears verbatim within this block.

The Coder may not introduce a transition sentence between (2) and (3) — the two verbatim blocks must run consecutively, perhaps separated only by a paragraph break or a section sub-divider. The reason: any transition sentence the Coder writes is fresh framing prose, which the plan §7 acceptance criteria 1, 2 explicitly forbid.

The §1.5.7 sub-section will be long. That is acceptable. SME content verdict verifies (1) is one sentence in §1.5.7-voice (not a paraphrase of philosophy doc text), (2) and (3) are verbatim, no transition sentence between (2) and (3), and the §1.5.4 forbidden-vocabulary scan passes throughout.

**A5. The §1.5.4 forbidden-vocabulary table extension under the new exploratory framing.**

Per (E) §6 observation above. Under the new exploratory framing, hypothesis-testing language applied retroactively to LSB findings is a vocabulary violation that the existing §1.5.4 table does not guard. The Coder should add 1–2 rows to the §1.5.4 table:

| Don't say | Say instead |
|---|---|
| "LSB hypothesizes that..." / "LSB tested whether..." / "LSB confirms that..." / "LSB found that [hypothesis]" | "LSB measures..." / "LSB reports..." / "LSB observes..." |
| "LSB predicted X and the data confirmed/refuted it" | "LSB ran the protocol; here is what came out" |

The Coder may use the exact phrasings above, may merge them into a single row, or may use structurally equivalent phrasings that catch the same surface. The Reviewer verifies at least one row guarding hypothesis-testing language has been added; SME content verdict double-checks.

**Why this binds:** the §1.5.7 sub-section makes "LSB is not hypothesis-testing" a binding framing claim. Without a §1.5.4 vocabulary guard, a future Coder writing a methodology page or a lede could naturally drift into "LSB hypothesizes that DeepSeek's family-term consensus is lower than Claude's" — that phrase does not trip any current §1.5.4 row but contradicts §1.5.7. A5 closes the gap.

**Optional in scope:** if the Coder finds adding the row mid-amendment introduces wording uncertainty, the Coder may pause and route the wording question to the Architect; A5 is then deferred to a follow-up commit. The mid-amendment pause is preferred over improvising the wording. (Stop condition under CLAUDE.md §10 escalation order.) Either disposition is acceptable; A5 is satisfied by either (a) row added in this commit with Reviewer + SME content verdict approval, or (b) row deferred to a follow-up commit with the deferral explicitly noted in the SME content verdict's outstanding items.

**A6. The `data/grounding/README.md` banner text is exactly the four-line form in plan §5.9 (no expansion, no editorializing).**

Per Q5 + plan Risk 7 mitigation. The Architect's plan §5.9 specifies the exact ≈4-line banner text. The Coder may not exceed those four lines (no additional paragraph naming Romney attribution context — the Romney attribution is already in the Architect's recommended banner; no additional paragraph naming any historical context beyond what the banner says). Reviewer verifies the banner is ≤ 5 paragraphs and contains zero forbidden vocabulary. SME content verdict double-checks the banner's framing posture (no "this data is no longer valid" or "this data has been superseded" language — the data is still scholarly-valid; LSB just doesn't use it as a comparison axis).

**Acceptable banner expansions** (if the Coder finds the four lines feel too terse): the banner may expand to 6–8 lines if the additional content is purely descriptive (e.g., naming the four files in the directory, naming the source.md attribution requirement once more for visibility, naming the specific dates of extraction). The expansion may not exceed 8 lines and may not introduce new framing language not in philosophy doc §1 or Architect plan §5.9.

---

## (G) Carry-forward of prior binding notes

### B6 (parent T4-redo) — public-copy guardrails

**Status: BINDING on this amendment's prose.**

B6 forbids:

- Augmenting findings with "PLUS disproportionate CN-origin decline pattern" framing (specific to T5 / Note K).
- Framing prior LSB work as "incorrect" or "should not have been published."
- Cross-provider, cross-failure-mode, or cross-prompt-type generalization without evidence.
- Internal-state claims about models.

This amendment's prose surfaces (ARCHITECTURE.md §1.5 expansion, §1.5.5 transition, §1.5.7 new sub-section, README first paragraph, methodology-page outline item 5 in DESIGN_SYSTEM.md §6.1) all are public-copy adjacent. B6 binds throughout. The Coder must not frame the v0.7 grounding architecture as "incorrect" or "should not have been published" — the v0.7 design was correct against its frame; the 2026-05-07 amendment makes a different decision under different priorities (per philosophy doc §1's framing). A2 codifies the §1.5.5 transition discipline; B6 reinforces it.

### B11 REPLACED (parent T4-redo) — K-frame/K-vocab dichotomy

**Status: NOT TRIGGERED by this amendment.**

B11 was replaced at the RD-3 content verdict; the K-frame/K-vocab dichotomy is not a surface this amendment touches. The amendment's prose does not reference Note K, the cap-exhaustion finding, or any T-series or T5-redo finding. The disposition is preserved.

### B12 (parent T4-redo) — RD-3 memo as canonical citation

**Status: NOT TRIGGERED by this amendment.**

B12 binds future methodology-page-bound text on Note K to cite the RD-3 memo by path. This amendment's prose does not touch Note K or any related surface. B12 is preserved as gate posture for future work but not triggered here.

### B14 (parent T4-redo) — numerics-vs-interpretation separation

**Status: NOT TRIGGERED by this amendment.**

B14 binds reports that contain both numerical findings and interpretive prose to separate them by commit (RD-T5-3 numerics, RD-T5-4 interpretation). This amendment is doc-only, no numerical findings. B14 is preserved as gate posture for future analytical work but not triggered here.

### T8 (RD-3 content verdict) — descriptive-shape discipline

**Status: BINDING on this amendment's prose.**

T8 forbids causal language, introspective language, or stimulus-as-cause framing. The amendment's prose must remain at descriptive-shape level throughout. Spot-check of philosophy doc against T8: §3 last paragraph ("There is nowhere in this architecture that stores 'this is what a family is.'") is descriptive; §4 chain ("corpus → training → alignment → decoding → output distribution") is descriptive; §5 pinned definition ("The shape of the model's output distribution when prompted with CDA stimuli...") is descriptive; §8 honest tagline ("LSB measures what frontier LLMs produce when asked to categorize...") is descriptive. The philosophy doc passes T8 throughout.

The Coder's responsibility under T8 is to (a) quote philosophy doc text verbatim (which inherits T8 compliance) and (b) apply T8 to any §1.5.7-voice introduction sentence and any §1.5.5-voice opening sentence (per A2, A4). A1 + A2 + A4 codify the disciplines.

### T9 (RD-3 content verdict) — forbidden softer-than-thinks/believes verbs

**Status: BINDING on this amendment's prose.**

T9 forbids verbs like "recognizes," "identifies," "interprets," "comprehends," "perceives" applied to models. Spot-check of philosophy doc: §3 says "the model attends to previous tokens" — "attends to" is the technical attention-mechanism term, not a perceptual claim; PASS under T9. §3 says "The aggregate attention pattern over many heads, integrated across many layers, is what determines which tokens get high probability in any given context." — descriptive of the mechanism, no perception claim; PASS. §5 says "the model's output distribution when prompted" — no perception verbs; PASS. §6 explicit-disclaim says "Whether the model 'understands' the domain. It produces tokens that, given the prompt context, have high predicted probability." — the disclaim is the right shape; PASS.

Philosophy doc passes T9 throughout. The Coder's responsibility under T9 is to apply it to any §1.5.7-voice or §1.5.5-voice sentences (per A2, A4).

### Predecessor-verdict summary

| Note | Status under this amendment |
|---|---|
| B6 (parent T4-redo public-copy guardrails) | BINDING on this amendment's prose |
| B11 (parent T4-redo, REPLACED) | NOT TRIGGERED |
| B12 (parent T4-redo, RD-3 citation) | NOT TRIGGERED |
| B14 (parent T4-redo, numerics-vs-interp) | NOT TRIGGERED |
| T8 (RD-3 descriptive-shape discipline) | BINDING on this amendment's prose |
| T9 (RD-3 forbidden softer verbs) | BINDING on this amendment's prose |
| T11–T15 (T5 redo) | NOT TRIGGERED (T5-redo-scope-specific) |
| S2 (Task #16 four-state taxonomy) | NOT TRIGGERED (no thoughts_token_count surface) |
| S5 (Task #16 SATISFIED) | Gate posture preserved |
| Note A (T5 small-n caveat) | NOT TRIGGERED |
| Note D (no ceiling claims pre-Phase-4c) | SATISFIED-by-amendment (Phase 4c is removed; ceiling-claim-prevention is now structural rather than gate-policy) |

The "Note D SATISFIED-by-amendment" disposition is interesting. Note D forbade ceiling claims pre-Phase-4c. The amendment removes Phase 4c entirely. The structural removal of human grounding from v1 means ceiling claims are no longer "deferred" — they are not part of LSB. Note D's gate posture (no ceiling claims) survives as a permanent feature of LSB, no longer time-limited. Future methodology-page-bound text or lede text that floats a ceiling claim is now a B6 violation (cross-frame critique) and a §1.5.5 framing-drift violation simultaneously. Note D's underlying discipline carries forward; the time-limited "pre-Phase-4c" framing is moot.

---

## (H) §1.5 framing risks the amendment introduces (proactive scan)

I scanned the Architect plan in full for §1.5 / CLAUDE.md §7 violations. The plan is the Architect's text-on-disk, not the methodology-page-bound text the amendment will produce, but the plan must already follow §1.5 because the Reviewer's spot-check on the plan commit was already at the standard threshold and any framing drift in the plan would propagate into the Coder's reading of it.

### Findings (full pass)

- No `worldview`, `believes`, `thinks` (about models). Clean.
- No "publishable" framing for any LSB finding. Clean. (Plan §3 Q3 uses "publishable in *Nature*" only as a quote of CLAUDE.md §1 — meta-citation, not a framing claim.)
- No "closer to human is better." Clean.
- No "within-model consensus" / "within-model CCM." Clean.
- No softer-than-thinks/believes verbs ("recognizes," "identifies," "interprets," "perceives") applied to models. Clean.
- The plan correctly uses "categorical structure," "corpus lens," "output behavior," "output distribution" where the equivalent claim is made.

### One observation that is not a finding but is worth surfacing

Plan §3 Q5 uses the phrase "sentimental loss" in the Architect's reasoning ("deleting working data Mark spent time extracting is a sentimental loss with no architectural gain"). This phrase is in the plan itself, not in any text the Coder will emit downstream. It is not a framing violation. It is, however, slightly informal for an Architect plan that the SME and Reviewer reference; the next Architect plan that uses similar wording for a similar argument might consider "audit-trail loss" or "provenance loss" as more technical alternatives. This is not a finding; it is an offered editorial preference. Not blocking.

### Pass

PASS on §1.5 framing for the plan itself. No drift; no forbidden vocabulary; no improvised framing claims.

---

## (I) Proactive checks

### Check 1 — `data/grounding/family/romney_1996/source.md` Romney 1996 attribution survives

The retain-with-banner posture (Q5) preserves the four files including `source.md`. The Romney 1996 attribution is in `source.md`. The attribution text is unchanged. The LICENSE-DATA reference (per ARCHITECTURE.md §6.6) survives. PASS.

### Check 2 — Cross-reference scan after deletions

The Coder's required pre-commit cross-reference scan (per Architect plan §7 Coder-must-run) covers `grounding_submission_template`, `grounding_submission.md`, `PHASE_4C_CANDIDATE_SOURCES`. SME PASS-WITH-NOTES adds: the Coder should also grep for `Phase 4c` (the phase reference from §5.3 that is being removed) to verify no residual Phase-4c-naming text survives in any tracked file. The phase-list ordering becomes 4a → 4b → 4c (renumbered from 4d, per plan §5.1.f); the residual "Phase 4c" references must all be the new 4c (bootstrap validation) or removed. Reviewer enforces.

### Check 3 — README.md first paragraph forbidden-vocab scan

The Architect's plan §5.5.a rewrite is:

> *"LSB measures what frontier LLMs produce when asked to categorize, in a way that's reproducible, comparable across models, and trackable across time. It applies Cultural Domain Analysis (CDA) — a methodology developed by cognitive anthropologists in the 1970s and 80s to study how human informants organize cultural vocabulary — to LLMs as if the models were informants. The result is a comparative map of how different models (Claude, GPT, DeepSeek, Llama, Mistral, Qwen, and others) organize the same set of everyday domain words (family terms, holidays, food, color, emotion). Every domain on the dashboard is, permanently, model-to-model."*

Cross-checked against §1.5.4 forbidden vocabulary table: zero hits. Cross-checked against T9 forbidden verbs: zero hits. Cross-checked against §6 forbidden inferences: the rewrite makes none of the six forbidden inferences. PASS.

### Check 4 — Methodology page outline item 5 forbidden-vocab scan

The Architect's plan §5.2.g rewrite (new methodology-page outline item 5: "What this measures and what it does not") draws from philosophy doc §5 + §6 + §8. The four sub-bullets the plan specifies all draw from descriptive-shape philosophy doc text. PASS.

### Check 5 — DATA_DICTIONARY.md schema-field documentation preservation

The plan §5.4.a–§5.4.c spec preserves all 18+ field-level descriptions in §3 (sub-sections 3.1 through 3.8). The three editorial notes are paragraph-level glosses that do not touch field documentation. R7 (schema/dictionary lockstep) is satisfied vacuously. PASS.

### Check 6 — DESIGN_SYSTEM.md §3.8 conditional behavior collapse coherence

The plan §5.2.e collapses the §3.8 four-state list to a single paragraph. The Coder must verify no orphan reference to "State 0," "State 1," "State 2," "State 3" survives in §3 or elsewhere in DESIGN_SYSTEM.md. The plan §5.2.c mentions "State 0" in the §3.3 collapse table once (as the sole row name); that is the only "State 0" reference allowed to survive. Reviewer enforces; SME content verdict double-checks.

### Check 7 — Phase ordering renumbering

The plan §5.1.f renumbers the phase ordering 4a → 4b → 4c (from 4d). The Coder must verify the renumbering is internally consistent across ARCHITECTURE.md §5.3 (phase list), §1 commitments (if any reference 4c or 4d), §6 (cross-cutting concerns), §9 glossary. The Reviewer's cross-reference scan catches stale "4d" or stale "Phase 4c (acquisition)" references. PASS-WITH-NOTES on this discipline (Reviewer enforces).

### Check 8 — `cdb_analyze/grounding.py` placeholder posture

The plan §5.1.d says "the `cdb_analyze/grounding.py` placeholder remains in the package for backward compatibility but is not consumed by any v1 analysis pipeline." The Coder must NOT delete the placeholder file (per plan §5.6 file-deletion list, which only deletes `docs/grounding_submission_template.md`, `.github/PULL_REQUEST_TEMPLATE/grounding_submission.md`, and `PHASE_4C_CANDIDATE_SOURCES.md`). PASS.

---

## (J) What I am explicitly NOT ruling on

- **The eventual Coder prose for §1.5 expansion, §1.5.5 transition, §1.5.7 new sub-section, README first paragraph, methodology-page outline item 5.** Those are SME-content-verdict territory at gate chain step 3, not plan-level. I am ruling on the plan and the philosophy doc, not on the eventual prose.

- **Per-row wording for the §1.5.4 vocabulary-table extension under A5.** The Coder picks; SME content verdict double-checks. I provide a recommended row form in A5; the Coder may use, modify, or pause-and-route for Architect input.

- **The Phase 5/6 methodology-page UI build.** Out-of-scope per plan §1 strict non-goals. The methodology-page outline edit (DESIGN_SYSTEM.md §6.1) is text-only; the eventual page is a separate Phase 5/6 task with its own UI/UX gate.

- **The eventual v2 prompt comparison sub-study or any v2 work.** Out-of-scope per plan §1 strict non-goals. Phase 5+ candidate per `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md`.

- **The unexplained-failure investigations (phi-4 ×6, gpt-5.4-mini ×2, mistral-small ×1).** Out-of-scope per plan §1 strict non-goals. Separate Architect tasks.

- **The lede generator templates in `packages/cdb_publish/lede/`.** Forward-carry per Q4 ruling. When those templates first land, they will be SME-gated under this amendment's framing.

- **The social-pipeline drafts in `packages/cdb_social/`.** Same as above; package does not yet exist.

---

## (K) Carry-forward note

This verdict establishes A1–A6 (6 new binding notes). The notes apply to:

- **A1 ("supersedes" word in §1.5.1):** ARCHITECTURE.md §1.5.1 four-layer-to-five-link replacement. Coder applies; Reviewer verifies "supersedes" is present; SME content verdict double-checks.
- **A2 (philosophy doc §1 "Trojan horse" verbatim in §1.5.5):** ARCHITECTURE.md §1.5.5 transition sub-section. Coder applies the four-element structure; Reviewer verifies (2) is verbatim and "Trojan horse" metaphor preserved; SME content verdict double-checks (1), (3), (4).
- **A3 (README §9–13 coherence post-truncation):** README.md "What LSB is and isn't" section. Coder applies; SME content verdict double-checks coherence.
- **A4 (§1.5.7 three-element composition):** ARCHITECTURE.md §1.5.7 new sub-section. Coder applies the §1.5.7-voice intro + philosophy doc §2 verbatim + philosophy doc §9 verbatim; SME content verdict verifies (1) is one sentence in §1.5.7-voice (not paraphrase), (2) and (3) are verbatim, no transition sentence between (2) and (3).
- **A5 (§1.5.4 forbidden-vocabulary table extension):** ARCHITECTURE.md §1.5.4. Coder may apply in this commit OR pause-and-route to Architect; SME content verdict double-checks the row added (or notes the deferral as outstanding).
- **A6 (`data/grounding/README.md` banner discipline):** new file in this commit. Coder applies the four-line form per plan §5.9 (or 6–8 lines under the descriptive-only expansion allowed); Reviewer verifies ≤ 8 lines and zero forbidden vocabulary; SME content verdict double-checks framing posture.

A1–A6 are local to this amendment's scope. Each is a content-level discipline (quotation discipline per philosophy doc supersession of prior framing per A1; framing discipline per A2; coherence discipline per A3; composition discipline per A4; vocabulary-extension discipline per A5; banner-text discipline per A6). None require schema changes. None require code changes. None require additional Architect plans (A5's pause-and-route is the only escape valve to the Architect, and it is optional).

The four-axis carry-forward (B6 binding, T8 binding, T9 binding, Note D SATISFIED-by-amendment, S5 gate posture preserved) holds. The §1.5.4 vocabulary table extension under A5 is the only structural-vocabulary expansion this amendment makes; A5 is the discipline that catches the vocabulary surface created by the new exploratory framing.

---

## Gate disposition

**The amendment Coder task (F-AMEND-2026-05-07-NO-HUMAN-BASELINE):** **AUTHORIZED** to start immediately on this verdict. The Coder applies A1–A6 throughout. Reviewer enforces:

- A1 "supersedes" word verbatim in §1.5.1.
- A2 philosophy doc §1 "Trojan horse" passage verbatim in §1.5.5.
- A3 README §9–13 coherence post-truncation.
- A4 §1.5.7 three-element composition (one §1.5.7-voice intro sentence, then philosophy doc §2 verbatim, then philosophy doc §9 verbatim, no transition sentence).
- A5 at least one §1.5.4 row guarding hypothesis-testing language (or deferral noted).
- A6 `data/grounding/README.md` ≤ 8 lines, zero forbidden vocabulary.
- Plan §7 acceptance criteria 1–29.
- Forbidden vocabulary scan (CLAUDE.md §7 + ARCHITECTURE.md §1.5.4, both pre-existing rows and the A5-added row if present).
- Cross-reference scan (the three deletion targets + "Phase 4c (acquisition)" + "Phase 4d" residuals + State 1/2/3 residuals).
- R7 schema/dictionary lockstep (vacuously satisfied).
- R12 cross-reference integrity.
- R13 commit message references this verdict path + the SME content verdict path + the Reviewer verdict path + the Tester verdict path.
- R14 single-task-per-commit.

**SME content verdict (gate chain step 3):** **PENDING** until Coder commit lands, Reviewer + Tester PASS. Verdict file: `docs/status/2026-05-07-no-human-baseline-amendment-cda-sme-content-verdict.md`. Verdict reviews the actual prose against:

- Philosophy doc fidelity (verbatim quotes are verbatim; paraphrases are forbidden where verbatim is required).
- A1–A6 disciplines.
- T8 descriptive-shape discipline applied to all §1.5.7-voice and §1.5.5-voice sentences.
- T9 forbidden softer-than-thinks/believes verbs.
- B6 public-copy guardrails (no "incorrect" framing for v0.7 grounding architecture; no ceiling-claim hedge that could be read as "this might come back later").
- §1.5.4 forbidden-vocabulary scan.
- The four-axis scorecard (protocol validity, analytical validity, claims validity, audience translation).

**No UI/UX gate** on this amendment per (C) above.

**No additional Mark sign-off required** beyond the standard Reviewer + Tester + SME-content-verdict gate chain. Mark merges the commit when all gates PASS.

---

## Sign-off

The Architect's plan is methodologically sound, well-bounded, and correctly defended. The 9-question surface (Q1–Q9) is well-thought-out; my rulings are AGREE on Q1, Q2, Q3, Q4, Q5, Q7, Q8, Q9, AGREE-WITH-CLARIFICATION on Q6 (the supersession word "supersedes" specifically). The UI/UX bypass call is correct; the one-commit decision is correct.

The philosophy doc holds up under §1.5 / B6 / T8 / T9 / forbidden-inferences / forbidden-vocabulary scrutiny throughout all ten sections. §3 paragraph 2 (attention-head specialization claim) carries a minor over-confidence at the granularity-of-claim level that is non-blocking and only matters if the Coder quotes the passage directly into §1.5; the recommended softening is documented in (E) §3 above. §6 forbidden-inferences enumeration is complete given the existing §1.5.4 table; A5 closes the new vocabulary surface introduced by §1.5.7's exploratory framing.

The amendment is methodologically the right next step for the project. It tightens the framing where the framing was loosest (the implicit invitation to compare-to-human-as-ground-truth that the v0.7 grounding architecture quietly admitted). It removes the surface area of the strongest critique LSB faces ("you're pretending to do anthropology on machines"). It encodes the project's exploratory posture as a definitional claim rather than a meta-defense. And it preserves the four files Mark extracted as audit-trail-completeness reference, with banner clarity about why they are no longer in the comparison loop.

The Coder may start the amendment task immediately on this PASS-WITH-NOTES verdict. A1–A6 bind throughout. The SME content verdict at gate chain step 3 closes the amendment.

*Posted to `#lsb-cda-sme`. Binding for the F-AMEND-2026-05-07-NO-HUMAN-BASELINE Coder task (gate authorization), Reviewer pass (cross-reference + forbidden-vocab + structural audit), and the SME content verdict at gate chain step 3. The CDA SME thanks the Architect for the unusually detailed Q1–Q9 surface (each question came with a concrete recommendation and a clear alternative), the proactive UI/UX-bypass reasoning (with explicit reversal path documented), the well-bounded one-commit defense (four reasons, each falsifiable), and the careful preservation of the historical audit trail (the philosophy doc itself is preserved as canonical source; the four `data/grounding/family/romney_1996/` files are preserved with banner; the v0.7 grounding architecture is preserved in git history rather than rewritten retroactively).*
