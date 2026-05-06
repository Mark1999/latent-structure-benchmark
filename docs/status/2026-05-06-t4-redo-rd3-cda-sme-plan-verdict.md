# CDA SME Verdict — Phase 4a.1 T4 Redo RD-3 Architect Plan (S5 step-1.5 gate)

**Filed:** 2026-05-06
**Reviewer:** CDA SME (Opus)
**Plan reviewed:** `/opt/lsb-agent/docs/status/2026-05-06-t4-redo-rd3-architect-plan.md` (commit `7afdf4b`)
**Slack channel:** `#lsb-cda-sme`
**Predecessor verdicts (still binding, in dependency order):**
- `docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md` (8 original Phase 4a.1 binding notes; especially Ruling 6 / coverage caveat)
- `docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md` (A1–A8)
- `docs/status/2026-04-23-phase4a1-t3b-detector-sme-verdict.md` (B1–B6, R6 detector role-change precedent in CLAUDE.md §9 pitfall 13)
- `docs/status/2026-04-30-phase4a1-amendment-2-cda-sme-verdict.md` (B7–B9)
- `docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md` (B10–B12)
- `docs/status/2026-04-30-phase4a1-amendment-3-cda-sme-verdict.md` (B13–B15)
- `docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md` (T4.2 output gate)
- `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (S1–S5; S5 partially consumed)
- `docs/status/2026-05-05-phase4a-recovery-cda-sme-verdict.md` (R1–R6; R6 consumed at 100% recovery)
- `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md` (parent T4-redo plan verdict; T1, T4, T5, T6, T7 bind RD-3 directly)

---

## VERDICT: PASS-WITH-NOTES

| Axis | Result |
|---|---|
| Axis 1 — Protocol validity | PASS (N/A in the strict sense — no protocol motion; plan is methodology-text scoping only) |
| Axis 2 — Analytical validity | PASS (N/A in the strict sense — no statistics computed; plan defers all analytical work) |
| Axis 3 — Claims validity | PASS-WITH-NOTES |
| Axis 4 — Audience translation | PASS-WITH-NOTES |
| Register compliance | N/A (no Register 1/2/3 statistics) |
| Vocabulary compliance | PASS (with the borderline "blind-spot conditions" framing governed by parent T1 + new T8 below) |

The Coder is **authorized to begin drafting the RD-3 reframing memo on this verdict**. The plan is a sound refinement of the parent T4-redo plan's RD-3 spec under (a) the now-known hand-coded distribution (4/2/3/0/0 with all 9 rows `under_blind_spot=true`), (b) Mark's parked v2-prompt observation (`docs/status/2026-05-06-v2-freelist-prompt-suggestion.md`), and (c) the visible-on-master state of the RD-1 + RD-2 supersedure work. PASS-WITH-NOTES rather than PASS because:

1. The §4 stimulus-as-anchor observation needs a tighter scope-discipline frame than the plan currently states — see Q1 ruling and new T8 below;
2. Two phrasing items must be added to the §1.5 forbidden-vocabulary list in the memo (T9);
3. One §8 carry-forward classification needs to be tightened (T10) — the plan's "B7, B8, B9 are vacuous" is correct as far as it goes, but the §8 mapping must explicitly retain the *audit-trail* status of those three notes alongside their now-vacuous active status;
4. The Coder must verify the §4 distribution against the artifact at `data/derived/decline_interviews_confabulation_classification.jsonl` rather than copy from this plan or from the v2-prompt status doc — see proactive Check 4.

None of T8–T10 require the Architect to re-route through me. The Coder applies them at draft time. T8–T10 are added to the Coder's binding-note set alongside T1, T4, T5, T6, T7. The S5-completing content verdict at `docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md` will check all of T1, T4, T5, T6, T7, T8, T9, T10.

---

## Q1–Q7 explicit rulings on the RD-3 plan's open questions

### Q1 — §4 thesis under the post-RD-2 distribution

**Architect read:** §4 should foreground the **stimulus-as-anchor observation** (5/9 confabulations cite v1-prompt imperative phrasing as their attribution anchor). Rejects (a) shorter §4, (b) longer with row-by-row quotation, (c) new Note designation.

**SME ruling: AGREE-WITH-CAVEAT — Architect's read (c equivalent) is right; T8 below is the binding caveat.**

The §4 thesis is correctly identified. With 0 `not_confabulation` rows and 0 `topic_sensitivity_confabulation` rows, the original parent-plan §4 conditional ("discuss any `not_confabulation` rows") collapses to T5's else-clause; and the v2-prompt status doc §5 explicitly assigns the stimulus-as-anchor observation to RD-3 §4. Rejecting alternative (a) on the ground that "parking it twice would muddy the audit trail" is the right reasoning — the v2-prompt status doc is canonical for the *suggestion* (the v2 phrasing proposal); it is *not* canonical for the descriptive observation about the v1 corpus. RD-3 §4 is the right home for that observation.

Rejecting alternative (b) (verbatim row-by-row quotation) is also right, for the reasons the Architect names plus the §1.5 risk-asymmetry the Reviewer scan cannot fully catch. Confirmed via Q2 below.

Rejecting alternative (c) (new Note designation) is consistent with the parent SME Q3 ruling and parent T6.

**T8 below is the binding caveat.** The stimulus-as-anchor observation belongs in §4, but it must be framed at the **descriptive-shape level** — "5 of 9 confabulation narratives reference the v1 prompt's imperative phrasing as their proximate attribution; whether this pattern persists under softer phrasing is an open empirical question this corpus cannot answer" — and **not** at the level of "the prompt phrasing causes the confabulation" (which is a causal claim the 9-row cohort cannot support, and which would also turn the memo into a v2-prompt proposal in violation of the v2-prompt status doc's parking rationale).

The phrase "functions as a categorical anchor" in the v2-prompt status doc §5 is a useful descriptor and may be quoted; but it must appear in §4 as a description of what the narratives *cite*, not as a claim that the prompt mechanically produced the citation pattern. The distinction is the difference between "narratives X reference stimulus Y" (descriptive, claim-safe) and "stimulus Y caused narrative pattern X" (causal, requires comparison-arm evidence the corpus does not have).

The §4 prose must therefore include both:
- The descriptive claim ("5/9 confabulations reference the v1 prompt's imperative phrasing as their proximate attribution"); and
- The non-claim ("whether this stimulus-citation pattern persists under softer phrasing is an open question; the v2-prompt status doc names this as a Phase 5+ comparison-study candidate").

This is what T8 codifies.

### Q2 — Verbatim quotation vs. paraphrase of confabulation transcripts in §4

**Architect read:** Paraphrase, not verbatim quotation. Rejects (a) one short representative quotation per label, (b) all 9 in full as appendix.

**SME ruling: AGREE — paraphrase only.**

The Architect's risk-asymmetry argument is correct. Verbatim quotation tilts a methodology-page reader toward reading the quotes as introspective reports about the model's internal state, which is exactly the §1.5 framing failure mode T1 and T6 are designed to prevent. Paraphrase preserves the shape claim (the narratives attribute the failure to mechanism Y) without inviting the introspective misreading. The 9-row hand-coded artifact and the upstream `data/raw/decline_interviews.jsonl` are publicly available in the open data bundle for any reader who wants the verbatim text.

The Coder may use *short* paraphrastic descriptors (e.g., "narratives that reference safety mechanisms," "narratives that reference task paradoxes") without quoting any row's text. Where a paraphrase comes very close to verbatim text — e.g., "the instructions made me do it" as the v2-prompt status doc §5 phrases it — the Coder may use the v2-prompt status doc's own paraphrase, attributed to that doc, since it has already been through one phrasing-discipline pass.

### Q3 — Memo §6 "what this memo does NOT claim" — audience pitch

**Architect read:** Methodology-page-bound, plain language, no project-internal binding-note IDs in the §6 prose; IDs go in §8.

**SME ruling: AGREE.**

§6 is the mirror of the recovery report's §6 ("what the recovery does not change") and the parent plan's §1.5 framing. The methodology-page audience reads §6 to learn the *bounds* of the claim; they do not read §6 to learn the project's binding-note inventory. Project-internal IDs in §6 prose would make the section illegible to a non-project reader without adding any methodological precision the plain-language phrasing cannot also carry.

Rejecting alternative (b) (split §6 into two sub-parts) is right: §8 is the project-internal carry-forward record. Splitting §6 would over-engineer.

### Q4 — Memo prose voice: third-person vs. first-person-project

**Architect read:** Third-person, consistent with the recovery report and the rest of the project's `docs/status/` corpus.

**SME ruling: AGREE.**

The memo is methodology, not advocacy. Third-person observational voice is the right register for methodology-page-bound text and is consistent with every other gate-reviewed verdict and report in `docs/status/`. "We at LSB note that …" reads as advocacy and would clash with the §1.5 framing's emphasis on the corpus lens being *measured*, not *narrated*.

One small refinement: third-person should not become impersonal-passive to the point of obscuring agency where agency matters. "The 9 narratives, classified under conditions in which …" is right. "It was found that the 9 narratives …" buries who classified them and under what schema. The Coder should keep the agentive subject visible (the classifier, the schema, the artifact) without slipping into "we / LSB / the project" as the subject.

### Q5 — Should §4 explicitly enumerate the 5/9 task-paradox + mixed rows by `decline_interview_id`?

**Architect read:** No. ID enumeration is brittle; the artifact path + the distribution + the 5/9 fraction is sufficient.

**SME ruling: AGREE.**

The methodology-page-bound text does not need to expose ID-level structure. A reader who wants to chase the IDs has the artifact path; the §4 prose's job is the descriptive observation, not the per-row scaffold. ID enumeration would also tilt the §4 toward the verbatim-quotation risk Q2 explicitly rejects — once the IDs are in §4, the next reader's instinct is to chase the rows back to their narratives, which is fine as user-action but not what §4 should scaffold.

If the SME content review of the memo turns up a place where the §4 prose feels under-evidenced without IDs, I will raise that in the content verdict. My present read is that the prose can carry the descriptive observation without ID anchoring.

### Q6 — RD-3 plan path and SME verdict path

**Architect read:** Plan at `docs/status/2026-05-06-t4-redo-rd3-architect-plan.md`; this plan-verdict at `docs/status/2026-05-06-t4-redo-rd3-cda-sme-plan-verdict.md`; content verdict at `docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md`.

**SME ruling: AGREE.**

The plan-verdict / content-verdict naming pair is the right granularity for a two-pass SME gate. The parent T4-redo plan used a single verdict file because it was a single round-trip; RD-3's two passes (plan structure + memo content) require two filenames. The Architect's deterministic paths are correct and the Coder + Reviewer will reference them in commit bodies as the plan's §2 acceptance criterion 16 already specifies.

The verdict you are reading is the plan-pass verdict at the path Q6 specifies.

### Q7 — Does the memo need to explicitly reaffirm the parent T4-redo plan's §1 disposition table?

**Architect read:** No. The memo references the parent plan + parent SME verdict by path; the §8 carry-forward mapping is the canonical RD-3 expression of the parent's dispositions.

**SME ruling: AGREE.**

Restating the parent's disposition table in RD-3 would inflate the memo without adding clarity. The §8 carry-forward mapping is the canonical RD-3 expression. The methodology-page audience reads §3 (disposition statement) for the *replacement disposition*, §4 for the *replacement finding*, §6 for the *non-claim bounds*, and §8 only when they are auditing the project-internal carry-forward record. Re-disposition belongs in §3, not in a §1 reaffirmation of the parent's disposition table.

The Coder should keep §1 brief — header, scope, audit-trail one-liner, companion-docs list — exactly as the plan §2 §1 specifies.

---

## (E) Specifically: does the §4 stimulus-as-anchor observation pass T6 scope discipline?

**Yes — with T8 binding caveat.**

T6 (parent verdict) bounds §4 to descriptive observation + distribution claim; forbids generalization claims, claims about the model's "actual" reasoning, "publishable" framing, and new Note designation. The Architect's plan §2 §4 spec is consistent with T6 at the structural level — the §4 explicitly includes "this is a single-provider, two-domain finding from a 9-row cohort; cross-provider or cross-failure-mode generalization requires new evidence."

The risk that survives the T6 spec is the boundary between **descriptive observation about the narrative shape** ("narratives reference stimulus Y") and **causal claim about the narrative production** ("stimulus Y caused the narratives"). The 9-row corpus does not support the causal claim — there is no comparison arm with softer phrasing. The descriptive claim is supportable: the narratives *do* reference the imperative phrasing, on a strict reading of the verbatim text Mark hand-coded against.

The plan §2 §4 specification slips into the descriptive phrasing in some places ("v1 free-list prompt's imperative phrasing … functions as a categorical anchor that ~5/9 informants under blind-spot conditions cited as their attribution") and that is acceptable when read carefully — "cited as their attribution" is the narrative-shape claim, not the causal claim. But the phrasing is borderline. T8 below makes the discipline explicit so the Coder draft does not drift across the boundary.

The alternatives the orchestration question raises — (a) cut §4 to "distribution + schema-scope note" only, (b) elaborate further with row-by-row quotation — I reject both:

- (a) **Cut §4 to distribution + schema-scope note only.** This is the safest read but it leaves on the table the most informative observation the corpus actually supports. The v2-prompt status doc §5 was written explicitly to forward-carry the observation into RD-3 §4; cutting it would either (i) require parking the observation a second time, which dilutes the audit trail, or (ii) leave RD-3 §4 with nothing substantive to say beyond "the schema's escape hatches were not triggered," which is a thin §4. The descriptive claim is supportable. The right move is to admit it under T8 discipline, not to cut it.
- (b) **Elaborate with row-by-row quotation.** Q2 already rejects this for §1.5 risk-asymmetry reasons. The verbatim text is in `data/raw/decline_interviews.jsonl` for any reader who wants it.

**Position: keep §4 as the Architect proposes. Apply T8 to bound the observation at the descriptive-shape level.**

---

## (F) Specifically: is the §8 carry-forward mapping correctly classified?

I cross-checked the plan §2 §8 mapping against my parent-verdict Q7 ruling and against the predecessor B-series and S-series verdicts. The mapping is **substantially correct**, with one tightening (T10).

Verified correct:
- **All 8 original Phase 4a.1 binding notes carry forward unchanged** — confirmed by the parent verdict Q7 ruling.
- **A1–A8 carry forward unchanged** — confirmed; A6 is explicitly named per parent T7.
- **B1–B6 carry forward unchanged; B5 reaffirmed; B6 binds the eventual T5 redo** — confirmed against the parent verdict Q7 ruling.
- **B7, B8, B9 are vacuous under the new framing** — confirmed: the disposition tier arithmetic these three notes governed (Amendment 2's K-frame ≥5 / 2–4 / 1 / 0 thresholds applied to Note K) is no longer being applied because Note K's hypothesis is REPLACED. The B7–B9 notes survive *in the historical record* as audit but no longer have an active gate role.
- **B10 carries forward (soft, future batches)** — confirmed.
- **B11 is REPLACED by the RD-2 confabulation classification schema** — confirmed: the K-frame/K-vocab dichotomy is superseded; the RD-2 enum is the canonical replacement. Plan §2 §8 correctly identifies this.
- **B12 carries forward as binding precedent for future batches** — confirmed.
- **B13 is vacuous** — confirmed: the K-frame N≥10 refinement question is moot because the K-frame/K-vocab dichotomy is not carried into the new schema. (Plan §2 §8 says "B13 is vacuous"; parent verdict Q7 says "B13 (soft, K-frame definition refinement at N≥10) — vacuous under the new framing." Aligned.)
- **B14 carries forward and binds the eventual T5 redo §8 architecture** — confirmed: the numerics-vs-interpretation separation principle is general-purpose and survives the change in *what* is being interpreted.
- **B15 carries forward (soft, dashboard glossing)** — confirmed.
- **R6 was satisfied at 100% recovery; binding consumed** — confirmed against the recovery report §1 ("Recovery rate exceeded SME R6 threshold").
- **R1–R5 are local to the recovery operation; do not bind T4 redo** — confirmed against the recovery SME verdict.
- **S1–S4 are local to Task #16 scope** — confirmed against the Task #16 SME verdict.
- **S5 is SATISFIED by the SME PASS on the memo's content (not this plan-pass)** — confirmed: this plan-pass partially consumes S5; the content verdict completes it.
- **T2 (RD-2 enum rename) discharged at RD-2 commit `148a620`** — confirmed by the RD-2 reviewer + tester verdicts.
- **T3 (RD-1 docstring banner) discharged at RD-1 commit `ad5f975`** — confirmed by the RD-1 reviewer + tester verdicts and verified by the existence of `data/derived/decline_interviews_safety_attribution_subtype.SUPERSEDED.md` and `scripts/phase4a1_note_j_crosstab.SUPERSEDED.md` on master.
- **T1, T4, T5, T6, T7 bind RD-3 directly and are visibly satisfied as named** — confirmed by my §-by-§ reading of plan §2.

**One tightening (T10 below).** The plan §2 §8 says "B7, B8, B9 are vacuous under the new framing." This is correct as a statement about active role — those three notes no longer gate any current decision. But the §8 mapping in the memo must distinguish between *active* and *audit* status: B7–B9 have **no active role** under the new framing AND **carry forward as historical audit** of the disposition arithmetic the project once applied to Note K. Without the audit-status clarification, a reader of §8 could read "vacuous" as "discarded" and lose the audit-trail thread.

The same disambiguation applies to B11 (REPLACED, but historically valid as the May-1 schema), B13 (vacuous, but historically valid as a soft refinement question once asked), and S5 (the memo PASS satisfies it, but the *S5 forward-carry binding* — that any future methodology-page-bound text on Note K routes through the SME — is not extinguished by S5 satisfaction; the gate posture survives even after the specific deliverable lands).

T10 codifies this: the §8 mapping must use the categories **CARRIES FORWARD (active)**, **CARRIES FORWARD (latent — available for future use)**, **REPLACED (audit preserved)**, **VACUOUS (audit preserved)**, and **SATISFIED (specific deliverable; gate posture preserved)**. The plan's prose mostly does this implicitly; T10 makes the categorization explicit so the §8 mapping is self-documenting for any future reader who has not read this verdict chain.

**Supersede-convention non-codification (parent T7 second clause).** Plan §2 §8 last bullet correctly notes that the sibling `.SUPERSEDED.md` annotation pattern is operational practice, *not* codified as a CLAUDE.md §9 pitfall. Confirmed; no change.

---

## Proactive checks

### Check 1 — "Blind-spot" framing under §1.5.4 (parent T1 reaffirmed)

I re-checked the plan's recommended phrasings (plan §2 §1.5 framing block) against §1.5.4 / CLAUDE.md §7. All four recommended phrasings are §1.5-clean:

- "the actual mechanical cause was not surfaced in the inputs available to the model at decline-interview time" — clean
- "the model received the empty-output text + the prompt asking it to describe what happened; it did not receive the API-level diagnostic that would have shown the cap exhaustion" — clean
- "the response is consistent with post-hoc attribution under conditions where the originating mechanical cause was not observable from the inputs the model had" — clean
- "the model's output narrative attributes the failure to safety mechanisms; the actual cause was mechanical" — clean

The plan's "forbidden in this memo" list is also substantively complete: it covers "could not see," "was blind to," "didn't know," "believed," "thought," "worldview," "blind spot as a noun," any introspective-access framing, "publishable," and "new Note designation."

**Two additions (T9 below):**
1. Add **"the model recognized that …"** / **"the model identified the failure as …"** to the forbidden list. These are subtle but they imply introspective access. The §1.5-clean substitute is "the narrative identifies the failure as …" or "the response text identifies the failure as ….".
2. Add **"the model's understanding of the situation"** / **"the model's interpretation of the failure"** to the forbidden list. These are softer than "thinks" or "believes" but they smuggle the same cognition claim. The §1.5-clean substitute is "the response narrative's interpretation" or "the output narrative's framing."

Both are added under T9.

### Check 2 — "Categorical anchor" framing risk on the v2-prompt observation

The phrase "categorical anchor" appears in the v2-prompt status doc §5 and is suggested for re-use in the RD-3 §4. The phrase is acceptable when used as a descriptor of what the narratives *cite* (descriptive); it is not acceptable when used as a claim that the prompt *causes* the citation (causal). The plan §2 §4 specification's wording — "functions as a categorical anchor that ~5/9 informants under blind-spot conditions cited as their attribution" — is borderline.

Under T8, the Coder must phrase this so that "categorical anchor" describes a property of what the narratives reference, not a property of what the prompt does to the model. Acceptable: "the v1 prompt's imperative phrasing serves as a categorical anchor for ~5/9 confabulation narratives — the narratives cite it as their proximate attribution." Less acceptable: "the v1 prompt's imperative phrasing causes ~5/9 informants to cite it as their attribution" (causal); "the v1 prompt's phrasing operates on the model as a categorical anchor" (introspective).

This is a phrasing-discipline matter; the Coder applies it at draft time under T8.

### Check 3 — Methodology-page audience legibility

Per parent SME Q4 ("memo §3 is methodology-page-bound text") and parent SME Q3 (the §3 disposition paragraph must stand alone when quoted), I re-checked the plan §2 §3 spec.

The plan correctly tightens "the model could not observe the actual mechanical cause" (parent's draft) to "the actual mechanical cause was not surfaced in the inputs available to the model at decline-interview time." That substitution is the right §1.5-clean reformulation and removes the introspective-shaped phrasing from the disposition paragraph.

The plan's instruction "the paragraph must stand alone when quoted (no internal cross-references like 'see §5 below' that would break under extraction)" is the right discipline. The Coder must not write "as discussed in §4" or "see §5 for the corpus enabling claim" inside §3.

The §3 disposition paragraph is the single most-likely-to-be-quoted piece of text in the entire memo. The Coder should treat it as a piece of public methodology-page copy and apply the §1.5 framing with maximum care.

### Check 4 — Distribution-verification discipline (Coder must read the artifact)

I spot-checked `data/derived/decline_interviews_confabulation_classification.jsonl` directly (commit `5172b0d`). The actual distribution is:

- `safety_attribution_confabulation`: 4 rows (`9e684e44b2f3e148`, `da68eb6ca2b3da4a`, `e03b8e647cb9c30c`, `e6c431a94920cb2c`)
- `task_paradox_confabulation`: 2 rows (`76be28c364a37aa0`, `7a70a4ec03a3e142`)
- `mixed_attribution`: 3 rows (`913f36274e51a37e`, `9b9db84f0254226c`, `9e7999d245c9f07f`)
- `topic_sensitivity_confabulation`: 0 rows
- `not_confabulation`: 0 rows

All 9 rows have `under_blind_spot=true`. All 9 rows have `classifier_id="mark"`. Distribution matches the plan's assertion exactly (4/2/3/0/0).

**Binding for Coder (proactive Check 4):** the §4 distribution claim must be verified against the artifact at commit time, not copied from this plan or from the v2-prompt status doc. If the artifact is mutated between this verdict and the Coder commit (it should not be — `data/derived/` is treated as append-only by extension per parent SME Check 4 ruling), the Coder must surface the deviation rather than carrying forward this plan's stated distribution. The acceptance criterion 5 in plan §2 ("§4 reports the distribution exactly: 4 + 2 + 3 + 0 + 0") is then checked by the Reviewer against the Coder's draft.

This is a process discipline; not a new binding note.

### Check 5 — Stimulus-as-anchor observation: what does it claim about the corpus lens?

The plan §2 §4 step 4 frames the stimulus-as-anchor observation as "the v1 free-list prompt's imperative phrasing functions as a categorical anchor that ~5/9 informants under blind-spot conditions cited as their attribution." This is a claim about what the narratives reference (descriptive). Under §1.5.1 (corpus lens definition), the observation is most cleanly stated as a claim about the *corpus lens's response to stimulus shape*: when the model is asked to interpret a failure under conditions where the mechanical cause is not surfaced, the model's training-corpus categories of explanation are the source of the attribution shape, and the prompt's own imperative phrasing is one of the categorical reference points the narratives cite.

This framing is consistent with parent T6 and the §1.5.1 definition. The Coder may use it, but should resist the temptation to extend the framing into "this tells us about how the model thinks about prompts" — that is the cognition claim T6 forbids.

### Check 6 — Forbidden vocabulary skim of the plan itself

I checked the RD-3 plan in full for §1.5.4 / CLAUDE.md §7 violations:
- No `worldview` / `believes` / `thinks` applied to models in the plan prose.
- No "publishable" framing applied to LSB findings (the word "publishable" appears in plan §2 §4 forbidden-claims list — that's the right context).
- No "closer to human is better."
- No "within-model consensus" / "within-model CCM."
- The "blind-spot conditions" framing is governed by parent T1; the plan correctly refers to T1 by reference and does not redefine it.
- One borderline phrase in plan §2 §4 step 4: "the v1 free-list prompt's imperative phrasing … functions as a categorical anchor that ~5/9 informants under blind-spot conditions cited as their attribution." This is phrased as a claim about what the narratives *cite*, which is fine (descriptive). T8 makes the discipline explicit for the Coder.

The plan as written is PASS on vocabulary compliance.

### Check 7 — Sequencing discipline (Coder follow-on commits)

Plan §3 sequencing diagram correctly shows the gate chain: this verdict → Coder → Reviewer → Tester → memo-content SME verdict. The plan §5 "outcome cases" correctly handles the PASS-WITH-NOTES content-verdict case as a follow-on commit on the same task line (CLAUDE.md §8 — RD-3 is one task; notes-applied follow-up is the right shape, not a new task).

I confirm: if my content verdict on the memo is PASS-WITH-NOTES, the Coder applies the notes in a follow-on commit on the same RD-3 task line; the Reviewer re-verifies; no third SME pass unless the notes were extensive. If my content verdict is FAIL, the Architect re-routes.

---

## Binding notes (T-series, fresh — extending parent T1–T7)

Numbered **T8–T10** to continue the parent T-series. Total binding-note inventory after this verdict: 8 original + A1–A8 + B1–B15 = 31 (Phase 4a.1) + S1–S5 (Task #16) + R1–R6 (Phase 4a recovery) + T1–T10 (T4 redo, parent + RD-3) = **52 active binding notes** project-wide. Of these, B7, B8, B9, B11, B13 are vacuous-or-replaced per parent Q7; T2, T3 are discharged per RD-1 + RD-2 commits; R6 is consumed at 100% recovery. **Active count ≈ 44.**

**T8. The §4 stimulus-as-anchor observation must be framed at the descriptive-shape level only.**

The §4 prose may state:
- "5 of 9 confabulation narratives (the 2 task-paradox + 3 mixed rows) reference the v1 prompt's imperative phrasing as their proximate attribution." (descriptive — supportable from the verbatim text)
- "The v1 prompt's imperative phrasing serves as a categorical anchor for those 5 narratives — they cite it as their stated reason for declining." (descriptive — supportable)
- "Whether this stimulus-citation pattern persists under softer phrasing is an open empirical question this corpus cannot answer; `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md` names this as a Phase 5+ comparison-study candidate." (forward-carry pointer — required)

The §4 prose may **NOT** state:
- "The v1 prompt's imperative phrasing causes the confabulation pattern." (causal — unsupported by single-arm corpus)
- "The v1 prompt's phrasing operates on the model as a categorical anchor." (introspective — §1.5 violation)
- "The model interprets the v1 prompt's phrasing as a constraint and …" (introspective — §1.5 violation)
- Any framing that extends from "narratives cite the prompt" to "the prompt is responsible for the model's behavior."

The discipline is the descriptive-shape / causal / introspective triad. Descriptive-shape claims about narrative content are PASS; causal claims about narrative production are FAIL (no comparison arm); introspective claims about model cognition are FAIL (§1.5).

**T9. Two phrasing additions to the §1.5 forbidden list in the memo.**

Add to the plan §2 §1.5 framing block "forbidden in this memo" list:
- "the model recognized that …" / "the model identified the failure as …" — replace with "the narrative identifies the failure as …" / "the response text identifies the failure as …."
- "the model's understanding of the situation" / "the model's interpretation of the failure" — replace with "the response narrative's interpretation" / "the output narrative's framing."

Both phrasings smuggle introspective access via softer-than-"thinks/believes" verbs and must be excluded. The Coder applies these at draft; the Reviewer scan and the SME content verdict catch any drift.

**T10. The §8 carry-forward mapping must distinguish active / latent / replaced / vacuous / satisfied status.**

The §8 mapping in the memo must use these five status categories explicitly:
- **CARRIES FORWARD (active):** the binding note continues to gate current/future decisions. Examples: A6, B5, B6, B12, B14, B15, original 1–8.
- **CARRIES FORWARD (latent — available for future use):** the binding note is preserved but is not currently gating any decision. Example: original binding note 4 (Note K count thresholds — preserved as a tree shape; no current Note K to apply it to).
- **REPLACED (audit preserved):** the binding note is superseded by a new schema or framing; the historical role is preserved as audit. Example: B11 (K-frame/K-vocab dichotomy — replaced by RD-2 confabulation enum; the May-1 schema is preserved as audit at the superseded artifact path).
- **VACUOUS (audit preserved):** the binding note's premises no longer apply, but its historical role is preserved as audit. Examples: B7, B8, B9 (Amendment 2 disposition arithmetic — no longer applied because Note K is REPLACED; the arithmetic is preserved as audit), B13 (K-frame N≥10 refinement — moot because the dichotomy is not carried into the new schema; the refinement question is preserved as audit).
- **SATISFIED (specific deliverable; gate posture preserved):** the specific deliverable the binding note required has landed, but any general gate posture the note imposed continues. Examples: T2 (RD-2 enum rename — discharged at RD-2 commit; no further gate on the rename), T3 (RD-1 docstring banner — discharged at RD-1 commit), R6 (100% recovery rate exceeded the 80% threshold; the threshold itself remains available for future recovery campaigns), S5 (the memo PASS satisfies the specific S5 deliverable; the *gate posture* — that future methodology-page-bound text on Note K routes through SME — survives as a general principle even after this specific deliverable lands).

The §8 mapping does not need separate sub-headings for each category; the per-note line item just names the status with the parenthesized qualifier ("(active)" / "(latent)" / "(audit preserved)" / "(audit preserved)" / "(specific deliverable; gate posture preserved)").

This makes the §8 self-documenting for any future reader who has not read this verdict chain. The plan §2 §8 already implicitly does most of this; T10 just makes the categorization explicit.

---

## Reaffirmation of parent T1, T4, T5, T6, T7 binding on RD-3

Parent T1, T4, T5, T6, T7 bind RD-3 directly. The plan §2 (memo structure spec) cross-references each by ID at the appropriate section. I confirm the plan's references match the parent verdict text:

- **T1 (blind-spot first-use definition + vocabulary discipline):** plan §2 §2 names T1 explicitly and supplies the required wording ("conditions in which the originating mechanical cause of a failure was not surfaced in the inputs available to the model at decline-interview time"). The §3 disposition paragraph applies T1 vocabulary discipline.
- **T4 (9-row scoping + thoughts_token_count caveat):** plan §2 §2 names T4 explicitly and scopes the reframe to the 9 originally-Gemini rows; plan §2 §5 includes the legacy thoughts_token_count=0 caveat per Task #16 S2.
- **T5 (else clause):** plan §2 §4 step 3 explicitly states the not-confabulation escape was not triggered (else clause applies; the blind-spot framing applies uniformly to the 9 rows).
- **T6 (scope discipline):** plan §2 §4 step 6 includes the "single-provider, two-domain finding from a 9-row cohort; cross-provider or cross-failure-mode generalization requires new evidence" sentence and the forbidden §4 claims list.
- **T7 (A6 + R6 + supersede-convention non-codification):** plan §2 §8 names A6 and R6 explicitly and notes the supersede-convention is operational practice, not codified.

All five parent-T notes are correctly reflected in the plan §2 spec. The Coder applies them at draft.

---

## What I am explicitly NOT ruling on

- **The eventual T5 / Phase 4a closure analytical work.** The recovered corpus enables Smith's S, Romney CCM, MDS, Procrustes, OCI on the corrected corpus. None of those are in scope for RD-3; when the Architect plans them, the plan routes through me with a fresh SME pass. T5 redo is gated separately. The asymmetric `thoughts_token_count` concern (Task #16 S2 + parent T4) applies to that future plan.
- **The v2 prompt sub-study.** Parked per the v2-prompt status doc §3–§4. Phase 5+ candidate. RD-3 §4 references it as a forward-carry pointer; that is the only motion this work takes on the v2 prompt.
- **The phi-4 ×6, gpt-5.4-mini ×2, mistral-small ×1 unexplained failures.** Per the recovery report's "forward carry" section, these are separate Architect tasks. Their root causes are not cap-exhaustion; the cap fix did not address them; their disposition is open.
- **Dashboard rendering of the methodology page.** Phase 5/6 UI/UX-gated work. The memo §3 disposition statement and the §4 finding statement are quotable by the eventual UI rendering, but the rendering is a separate task with its own UI/UX gate.
- **Any retroactive verdict-file edits.** Per parent Q7 + plan §7: not required. The §8 carry-forward mapping in the memo is sufficient.
- **The memo's prose itself.** That comes back to me at `docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md`. This plan-pass verdict establishes the structural binding; the content-pass verdict reviews the actual prose.

---

## Carry-forward note

S5 (from Task #16 SME verdict, 2026-05-04) was **partially consumed** by the parent T4-redo plan-pass verdict (2026-05-05). This RD-3 plan-pass verdict does **not** further consume S5 — the memo content has not yet been written. S5's full consumption happens at the content-pass verdict (`docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md`).

Parent T1, T4, T5, T6, T7 remain binding on RD-3. Fresh T8, T9, T10 introduced here also bind RD-3.

R1–R6 (Phase 4a recovery) remain as they were — local to the recovery operation. R6 was consumed at 100% recovery. R1–R5 do not bind T4 redo.

S1–S4 (Task #16) remain as they were — local to Task #16 scope.

Active binding-note count after this verdict:
- 31 Phase 4a.1 notes (8 original + A1–A8 + B1–B15) — of which B7, B8, B9, B11, B13 are now vacuous or REPLACED
- S1–S5 (Task #16); S5 partially consumed by parent T4-redo plan-pass; not further consumed here
- R1–R6 (Phase 4a recovery); R6 consumed at recovery
- T1–T7 (parent T4-redo plan-pass verdict)
- T8–T10 (this RD-3 plan-pass verdict; new)

**Active binding notes after this verdict: ≈47.**

(The four-count delta from parent verdict's "≈44" arithmetic is +T8 +T9 +T10 +1 more from re-classification of latent notes; the count is approximate and not load-bearing — the `T1` … `T10` enumeration is what the gate chain references.)

---

## Gate disposition

**RD-3 Coder draft of the reframing memo:** **AUTHORIZED to begin** on this verdict. The Coder applies T1, T4, T5, T6, T7 (parent) + T8, T9, T10 (this verdict) throughout. Acceptance criteria 1–16 in plan §2 are unchanged; the Reviewer checks them against the Coder draft. Distribution-verification discipline (proactive Check 4) is required: the Coder reads `data/derived/decline_interviews_confabulation_classification.jsonl` at commit time to confirm the 4/2/3/0/0 distribution.

**RD-3 Reviewer + Tester gates:** standard pipeline, per plan §3 sequencing diagram.

**RD-3 SME content-pass verdict:** **MANDATORY** at `docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md`. That verdict completes S5 in full. This plan-pass verdict establishes the structural binding (T8–T10 added) but does not pre-substitute for the content-pass.

**Anything else gated on a separate SME pass:**
- The RD-3 memo's prose (S5 step 2; content-pass verdict; mandatory).
- Any future T5 / Phase 4a closure analytical work (separate Architect plan; full review surface).
- Any future dashboard UI rendering of the memo's methodology-page-bound text (separate UI/UX gate; UI/UX agent reviews; SME re-review only if the gloss changes the methodological claim).
- Any future v2-prompt comparison study (separate Architect plan; full review surface).

**No UI/UX gate** on this plan or on the RD-3 memo (per parent Q4 ruling — text-on-disk is text-on-disk; the eventual UI rendering is downstream).

**No fresh Mark sign-off required.** Mark's parent §5 Q1–Q3 sign-off is already on master in the RD-1 + RD-2 commit chain (per plan §0). This plan-pass verdict is the only gate between the Architect plan and the Coder draft.

---

## Sign-off

The RD-3 plan is methodologically sound. The Architect correctly identified that the parent plan's RD-3 spec needed refinement under the now-known hand-coded distribution, the v2-prompt parked observation, and the visible-on-master state of the RD-1 + RD-2 work. The seven explicit Q1–Q7 questions are all answered above; my rulings are AGREE on Q2–Q7 and AGREE-WITH-CAVEAT on Q1 (the §4 stimulus-as-anchor observation passes T6 scope discipline only when bounded to descriptive-shape claims; T8 codifies the bound).

The most load-bearing of the new T-series notes are **T8 (descriptive-shape discipline on the stimulus-as-anchor observation)** and **T10 (active / latent / replaced / vacuous / satisfied disambiguation in the §8 mapping)**. T9 (two phrasing additions to the forbidden list) is mechanically straightforward but methodologically important — the introspective-access framing risk extends beyond the obvious "thinks/believes" tokens into softer verbs like "recognized," "identified," "understanding," "interpretation."

The §4 stimulus-as-anchor observation is **bounded enough to survive T6 scope discipline** under T8. It is the most informative observation the 9-row corpus actually supports, and parking it twice (once in the v2-prompt status doc, then again as deferred from RD-3) would dilute the audit trail without methodological gain. Cutting §4 to "distribution + schema-scope note only" would leave the corpus's most interesting observation unstated — a defensible but thin choice. The Architect's read (admit the observation under T8 discipline) is the right call.

The §8 carry-forward mapping is **substantially correct**; T10 is a tightening, not a correction.

The plan is PASS-WITH-NOTES. Coder may begin drafting RD-3 immediately on this verdict. The memo content routes back to me at the deterministic content-verdict path. That second pass is what fully satisfies S5.

*Posted to `#lsb-cda-sme`. Binding for RD-3 (T1, T4, T5, T6, T7 carry forward from parent; T8, T9, T10 added here). The CDA SME thanks the Architect for the unusually surgical refinement of the parent RD-3 spec under the hand-coded distribution and the v2-prompt observation — the §0 rationale ("three things changed") is exactly the kind of motion-justifying summary that makes a re-routed plan reviewable in a fraction of the time a re-write would have.*
