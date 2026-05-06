# CDA SME Content Verdict — Phase 4a.1 T4 Redo RD-3 Reframing Memo (S5-completing)

**Filed:** 2026-05-06
**Reviewer:** CDA SME (Opus)
**Artifact reviewed:** `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md` (commit `0a25dc2`, post-Reviewer-FAIL fix on `881037a`)
**Slack channel:** `#lsb-cda-sme`
**Pipeline state confirmed:**
- Architect plan: `docs/status/2026-05-06-t4-redo-rd3-architect-plan.md` (commit `7afdf4b`)
- SME plan-pass verdict: `docs/status/2026-05-06-t4-redo-rd3-cda-sme-plan-verdict.md` (commit `15732bd`, T8–T10 added)
- Reviewer FAIL (1st pass): `docs/status/2026-05-06-t4-redo-rd3-reviewer-verdict.md` (commit `7c9a70d`)
- Reviewer PASS (2nd pass): `docs/status/2026-05-06-t4-redo-rd3-reviewer-verdict-2.md` (commit `4ab3d6d`)
- Tester PASS: `docs/status/2026-05-06-t4-redo-rd3-tester-verdict.md` (commit `64f7ca1`)

**Predecessor verdicts (binding):**
- `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md` (T1, T4, T5, T6, T7 binding on RD-3)
- `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (S5 originator)

**Gate status of this verdict:** S5-completing. PASS satisfies S5 in full and unblocks Phase 5/6 methodology-page UI rendering at the methodology-text gate (a separate UI/UX gate still applies to the rendering itself).

---

## VERDICT: PASS-WITH-NOTES

| Axis | Result |
|---|---|
| Axis 1 — Protocol validity | PASS (N/A in the strict sense — no protocol motion; methodology-text deliverable) |
| Axis 2 — Analytical validity | PASS (N/A in the strict sense — no statistics computed; defers per Q5) |
| Axis 3 — Claims validity | PASS-WITH-NOTES |
| Axis 4 — Audience translation | PASS-WITH-NOTES |
| Register compliance | N/A (no Register 1/2/3 statistics) |
| Vocabulary compliance | PASS-WITH-NOTES (one Q2 paraphrase-discipline correction required) |

The memo is a sound piece of methodology-text. The §3 disposition paragraph is methodology-page-quotable as written. The §4 distribution claim verifies cleanly against the artifact (4/2/3/0/0; all 9 rows `under_blind_spot=true`; all 9 `classifier_id="mark"`). The §4 stimulus-as-anchor observation holds the descriptive-shape line on its second pass through the claim — the first sentence is borderline but the immediately-following clarifying paragraph re-anchors descriptively in a way that satisfies T8. The §6 non-claim list is plain-language and legible to a non-project audience. The §8 carry-forward mapping uses the T10 five-category vocabulary correctly with one classification I am leaving as-PASS (S1–S4 = active; see Punted Item (b) below).

PASS-WITH-NOTES rather than PASS for one specific reason: **the 3-word verbatim "internal safety protocols" in §2 Layer C is in tension with the Q2 paraphrase-only ruling and must be reworded.** The Q2 ruling is paraphrase-only with explicit example forms; the Reviewer's 8-word threshold was an operational floor, not a methodological rule. A 3-word verbatim quotation in quote marks tilts the §2 prose toward the introspective-misreading risk Q2 was designed to prevent.

The single required edit is named in Punted Item (a) below. After the Coder applies the rewording in a follow-on commit, the Reviewer re-checks the single phrase and the work continues. **No third SME pass is required**; the rewording is bounded.

---

## Walk-through of binding notes T1–T10

### T1 (parent — blind-spot first-use definition + vocabulary discipline) — PASS

The memo §2 line 40 defines "blind-spot conditions" on first use as "conditions in which the originating mechanical cause of a failure was not surfaced in the inputs available to the model at decline-interview time." The wording is semantically identical to the parent T1 binding text. Subsequent uses of the shorthand are governed by this definition.

The §1.5-clean phrasings in proactive Check 1 of the parent verdict are all present. No "could not see," "was blind to," "didn't know," or "blind spot" used as a noun-of-the-model. The phrasings about the inputs ("not surfaced," "did not receive the API-level diagnostic," "invisible from the available inputs") describe input-set properties, not perceptual capacity of the model. **PASS.**

### T2 (parent — RD-2 enum rename) — PASS (carry-forward; discharged at RD-2)

The memo correctly classifies T2 in §8 as SATISFIED (specific deliverable; gate posture preserved). The enum names used throughout §4 are post-rename (`safety_attribution_confabulation`, not `safety_filter_confabulation`). **PASS.**

### T3 (parent — RD-1 docstring banner) — PASS (carry-forward; discharged at RD-1)

The memo correctly classifies T3 in §8 as SATISFIED. The supersede-banner artifacts on master (the two `.SUPERSEDED.md` siblings) are referenced in §8 audit-trail. **PASS.**

### T4 (parent — 9-row scoping in §2; `thoughts_token_count=0` caveat in §5) — PASS

§2 Layer C scopes the reframe to the 9 originally-Gemini rows whose `under_blind_spot=true`. The "other 15 records" disambiguation is explicit (3 z-ai/glm-5.1 empty-freelist-propagation rows + 12 non-cap-exhaustion records).

§5 Caveat section addresses the legacy `thoughts_token_count=0` asymmetry per Task #16 S2 state (4). The four epistemic states are referenced by S2 (not re-enumerated, which is the right choice — S2 is canonical). **PASS.**

### T5 (parent — else clause) — PASS

§4.3 is the explicit else-clause section. Title: "No `not_confabulation` rows (SME T5 else clause)." The prose states the escape hatch was not triggered, names the per-row condition (no row's narrative correctly identifies the cap-exhaustion cause), and confirms the blind-spot framing applies uniformly across the 9 rows. **PASS.**

### T6 (parent — §4 scope discipline) — PASS

§4.4 closes with the T6 scope-discipline sentence: "This is a single-provider, two-domain finding from a 9-row cohort; cross-provider or cross-failure-mode generalization requires new evidence." The follow-on sentence reinforces the bound ("descriptive property of the confabulation corpus under its specific collection conditions, not a claim about the model's categorical-reasoning behavior in general").

§6 carries the non-claim list; the cross-provider/cross-failure-mode generalization prohibition is enumerated explicitly. No "publishable" framing. No new Note designation. **PASS.**

### T7 (parent — §8 explicitly names A6 + R6 + supersede-convention non-codification) — PASS

§8 names A6 explicitly (CARRIES FORWARD active; T3A pre-T3B sequencing posture preserved). §8 names R6 explicitly (SATISFIED, 100% recovery rate exceeded the 80% threshold; threshold remains available for future campaigns).

The "Supersede-convention note" subsection is present and correctly notes the sibling-`.SUPERSEDED.md` pattern is operational practice, not codified as a CLAUDE.md §9 pitfall. **PASS.**

### T8 (RD-3 plan — §4 stimulus-as-anchor at descriptive-shape level only) — PASS-WITH-NOTES (borderline; held by clarification)

§4.4 first paragraph contains the borderline phrasing the plan-pass verdict flagged: "the v1 free-list prompt's imperative phrasing ('do not explain or categorize') appears to function as a categorical anchor that those 5 narratives cite as their proximate attribution." The phrase "function as a categorical anchor" is on the descriptive/causal boundary — it can be read as "the prompt does something to the model" (causal-introspective) or "the prompt is what the narratives anchor on" (descriptive).

§4.4 second paragraph re-anchors and holds the descriptive-shape line cleanly:
- "5 of 9 confabulation narratives reference the v1 prompt's imperative phrasing as their stated reason for declining" — descriptive
- "the narratives cite it as a proximate attribution" — descriptive
- "the v1 prompt's imperative phrasing serves as a categorical anchor for those 5 rows **in the sense that the narratives cite it as their reason**" — the in-the-sense-that disambiguation re-binds "anchor" to the descriptive frame
- "This is a descriptive observation about what the narratives reference, not a causal claim about what the prompt mechanically produced." — explicit non-claim

The second paragraph's disambiguation is the load-bearing sentence; without it, the first paragraph's "function as a categorical anchor" would land closer to the causal frame T8 forbids. The disambiguation is present and correct.

The 4-word verbatim quotation "do not explain or categorize" is a quotation of the v1 free-list **prompt**, not of any narrative. Quoting project-authored prompt text is a different boundary from quoting model narrative text — the §1.5 risk Q2 protects against is the introspective misreading of model output, not the reproduction of project-authored prompt strings. The prompt quotation is fine.

**Optional refinement (not blocking PASS):** the §4.4 first paragraph would read more cleanly under T8 if "appears to function as a categorical anchor that those 5 narratives cite" were rephrased to "appears as a categorical anchor those 5 narratives cite" or "is the categorical anchor those 5 narratives cite." The "function as" verb construction creates the borderline; "appears as" or "is" lands the framing flatly descriptive. This is a refinement, not a fix-required item — the second paragraph's disambiguation already discharges T8. The Coder may apply this refinement if a follow-on commit is being landed for Punted Item (a); otherwise, leave §4.4 as-is.

**PASS** under T8 on the strength of the second paragraph's clarification. The optional refinement is methodologically nice-to-have, not required.

### T9 (RD-3 plan — two phrasing additions to §1.5 forbidden list) — PASS

Full grep for the T9 forbidden phrasings:
- "the model recognized" — 0 hits
- "the model identified" — 0 hits
- "the model's understanding" — 0 hits
- "the model's interpretation" — 0 hits
- "model's interpretation of" — 0 hits

Approved substitutes are used in their place where the equivalent claim is made:
- "the narrative attributes" — used in §2 Layer C and §3
- "the output narrative attributes" — used in §3 and elsewhere
- "the response narrative's interpretation" / "the output narrative's framing" — not used directly, but the equivalent phrasing structure ("the narrative cites," "the narrative references," "the response text identifies the failure as") is consistently descriptive. No introspective-access drift.

**PASS.**

### T10 (RD-3 plan — five-category §8 classification) — PASS

§8 uses the five categories explicitly and consistently:
- **CARRIES FORWARD (active):** Notes 1, 2, 3, 5, 6, 7, 8; A1–A5, A7, A8; A6; B1, B2, B3, B4, B6; B5; B10; B12; B14; B15; R1–R5; **S1–S4** (see Punted Item (b)); — all named with the (active) qualifier.
- **CARRIES FORWARD (latent):** Note 4 — preserved as available for future hypotheses.
- **REPLACED (audit preserved):** B11 — K-frame/K-vocab dichotomy superseded by RD-2 confabulation enum; sibling `.SUPERSEDED.md` annotation in place.
- **VACUOUS (audit preserved):** B7, B8, B9 (Amendment 2 disposition arithmetic); B13 (K-frame N≥10 refinement) — historical role preserved as audit at the originating verdicts.
- **SATISFIED (specific deliverable; gate posture preserved):** T1, T2, T3, T4, T5, T6, T7, T8, T9, T10; R6 (consumed at 100% recovery; threshold remains available); S5 (this memo PASS satisfies the specific deliverable; the gate posture — that future methodology-page-bound text on Note K routes through SME — survives).

Every named binding note carries exactly one parenthesized status qualifier. The mapping is self-documenting for any future reader who has not read this verdict chain. **PASS.**

---

## Punted Item (a) — "internal safety protocols" 3-word verbatim in §2 Layer C

**Reviewer Finding 4 disposition:** the phrase "internal safety protocols" appears as a 3-word quoted string at memo §2 line 42, verbatim from two narratives (`7a70a4ec03a3e142`, `9e684e44b2f3e148`). The Reviewer flagged it as below their 8-word reject threshold but in tension with the Q2 paraphrase-only ruling.

**SME ruling: REWORD REQUIRED.**

The Q2 ruling text is unambiguous: *"The Coder may use **short paraphrastic descriptors** (e.g., 'narratives that reference safety mechanisms,' 'narratives that reference task paradoxes') without quoting any row's text."* The form Q2 endorses is paraphrase-as-descriptor, not verbatim-as-quoted-snippet. The Reviewer's 8-word threshold was an operational floor for the literal-string-quotation grep; it was not a methodological substitute for the Q2 ruling.

The reasoning behind Q2 was risk-asymmetry: verbatim quotation tilts a methodology-page reader toward reading the quoted phrase as introspective testimony from the model, which is the §1.5 framing failure mode T1 and T6 are designed to prevent. A 3-word phrase in quote marks ("internal safety protocols") carries almost the same risk shape as a longer verbatim — a reader scanning the §2 prose sees a quoted phrase and naturally reads it as something the model "said" about itself, even with the surrounding "the model's outputs attribute the failure to" frame.

The Q2 form Q2 itself names ("narratives that reference safety mechanisms") would land cleanly here. The §2 Layer C sentence currently reads:

> The 9 narratives in which the model's outputs attribute the failure to "internal safety protocols" or similar mechanisms are now best understood as confabulation patterns: …

**Required rewording (single sentence):** Replace `attribute the failure to "internal safety protocols" or similar mechanisms` with `attribute the failure to internal safety mechanisms or similar` (drop the quote marks; replace the verbatim 3-word phrase with the paraphrastic descriptor "internal safety mechanisms").

Alternative approved forms (Coder may pick):
- `attribute the failure to safety mechanisms, task paradoxes, or topic sensitivity` (matches the §3 paragraph's phrasing exactly, which is already approved on §3 quotability)
- `attribute the failure to mechanisms consistent with categorical knowledge from the training corpus` (matches the §2 second clause's own phrasing; eliminates the redundant restatement)

Any of the three lands the sentence in paraphrase-only form. The Coder applies the rewording in a follow-on commit on the same RD-3 task line. The Reviewer re-checks the single sentence; no further SME pass is required if the rewording matches one of the three approved forms.

This is the only required pre-merge edit.

---

## Punted Item (b) — S1–S4 classification in §8

**Reviewer Finding 5 disposition:** the memo classifies S1–S4 (Task #16 binding notes) as CARRIES FORWARD (active). The Reviewer flagged that S1–S4 are "scope-local to Task #16" and that CARRIES FORWARD (latent) might be more accurate.

**SME ruling: ACTIVE is correct. Leave §8 as-is.**

The T10 status definitions distinguish active from latent on whether the note continues to gate current/future decisions:
- **active:** the binding note continues to gate current/future decisions
- **latent:** the binding note is preserved but is not currently gating any decision (example: original Note 4 — K-frame count thresholds preserved as a tree shape with no current Note K to apply them to)

S1–S4 actively gate decisions in this very memo and in current/future work:

- **S1 (cap=16384):** the operational max for all Phase 4a recovery and all subsequent collection runs. Every future collection is gated by this — change it back to 4096 and the collection layer regresses. The memo's §2 Layer B explicitly relies on S1 ("The Task #16 cap fix (`max_tokens=16384`) recovered all 10 Gemini cells at a 100% rate"). This is active gating, not preserved-as-tree-shape.
- **S2 (`thoughts_token_count` four-state disambiguation):** the memo's own §5 Caveat section explicitly invokes S2 to govern downstream analytical-computation work ("Task #16 SME verdict S2 established the four epistemic states the value `0` represents; state (4), the legacy-record case, applies to the original Phase 4a pre-Task-#16 records"). This is the clearest possible signal that S2 is actively gating: it is being applied, by name, in this memo, to govern future decisions. Latent would be a misclassification.
- **S3 (data dictionary update — `thoughts_token_count` field):** governs all future schema-touching work that consumes the field. CLAUDE.md rule 7 binds DATA_DICTIONARY.md updates to schema changes; S3 is the binding instance for this field.
- **S4 (schema addition disposition):** parallel to S3 for the schema side; governs Reviewer rule R7 enforcement on the field.

The Reviewer's concern was that "scope-local to Task #16" might mean "not currently gating other tasks." But scope-local to a feature does not equal latent — the original-binding-Notes-1-through-8 are scope-local to Phase 4a.1, and they're correctly classified active because they continue to gate Phase 4a.1-style work. Same logic for S1–S4: scope-local to Task #16 means scope-local to the cap fix and the `thoughts_token_count` field, both of which are actively gating ongoing work.

The latent category in T10 is reserved for notes whose premise has temporarily fallen out from under them — preserved-as-shape but not applied to anything currently. Original Note 4 is the canonical example: the count thresholds are intact, but there is no Note K hypothesis to apply them to. S1–S4 do not have this property — every one of them is being applied right now (S1 gates collection, S2 was just cited in §5, S3 and S4 govern dictionary/schema edits when they happen).

**Leave §8 S1–S4 = CARRIES FORWARD (active) as written.** No edit required.

---

## §1.5 framing semantic check (beyond literal-string grep)

I scanned the full memo for shape-of-claim drift — phrases that imply introspective access, perceptual capacity, or causal interpretation of the model's own state, even where they don't trigger a literal-string match.

**Findings:**

1. **§2 Layer C, "the model received the empty-output text and the decline-interview prompt; it did not receive the API-level diagnostic"** — clean. Describes input-set properties; no perceptual or introspective claim about the model.

2. **§2 Layer C, "the actual mechanical cause was invisible from the inputs available at decline-interview time"** — clean. The cause is the subject of "is invisible"; "invisible from" describes a property of the input set (the cause is not present in the inputs the model has access to). This is structurally parallel to the parent-verdict-approved phrasing "not observable from the inputs the model had." The Reviewer Notes-level flag on this phrase is read in the same direction: not in tension with T1.

3. **§3, "output patterns produced under blind-spot conditions"** — clean. "Output patterns" is the subject; blind-spot conditions is a noun-phrase qualifier on the production conditions, not on a property of the model. The §2 Layer C definition governs.

4. **§3, "the output narrative attributes the failure to mechanisms — safety protocols, task paradoxes, topic sensitivity — consistent with categorical knowledge from the training corpus"** — clean. "Output narrative attributes" is the descriptive form; "consistent with categorical knowledge from the training corpus" describes the source-corpus alignment, not the model's cognition.

5. **§4.4, "appears to function as a categorical anchor that those 5 narratives cite"** — borderline. Held by the second paragraph's clarification (T8 walk-through above).

6. **§4.4, "what the prompt mechanically produced"** — appears as a non-claim ("not a causal claim about what the prompt mechanically produced"). This is the Coder explicitly disclaiming the causal frame; clean.

7. **§4.4, "the model's categorical-reasoning behavior in general"** — appears in the scope-discipline sentence as a non-claim ("not as a claim about the model's categorical-reasoning behavior in general"). Clean — "categorical-reasoning behavior" is qualified as something the memo is **not** claiming. The phrase itself does not appear as an active claim anywhere.

8. **§6, "the model's categorical structure, cognition, or any internal reasoning state"** — appears as a non-claim ("does not claim that the confabulation pattern or the stimulus-as-anchor observation reflects the model's categorical structure, cognition, or any internal reasoning state"). Clean — explicit non-claim binding.

**No shape-of-claim drift detected.** The §1.5 framing holds throughout. The hedge phrases ("appears to," "in the sense that") and the explicit non-claim list in §6 hold the line where descriptive vocabulary alone would be borderline.

**PASS** on §1.5 semantic check.

---

## §3 disposition statement quotability

I read §3 as if it appeared on `cogstructurelab.com/methodology` standing alone, with no surrounding §1, §2, §4, etc.

**The §3 paragraph stands alone.** It states REPLACED unambiguously, names the upstream mechanical cause (`max_output_tokens=4096` cap reached during reasoning), names the population (the 9 originally-Gemini decline-interview narratives), names the recovery campaign (with file path), names the recovery rate (100%), and names the replacement claim (the confabulation-pattern observation). No internal cross-references survive after the post-FAIL fix.

The prose is pitched at a skeptical-but-non-specialist audience:
- The mechanical-cause description ("a `max_output_tokens=4096` cap reached during reasoning before any visible output emitted") is technical but not project-internal — a reader unfamiliar with LSB but familiar with LLM API behavior understands it.
- The blind-spot framing ("the actual mechanical cause … was not surfaced in the inputs available to the model at decline-interview time") is plain English; it describes a measurement-instrument condition, not a project-internal jargon.
- The replacement claim ("output narrative attributes the failure to mechanisms … consistent with categorical knowledge from the training corpus") is descriptive of the data, not jargon; "categorical knowledge from the training corpus" is the §1.5.1 corpus-lens framing in plain terms.
- The "no longer testable from this corpus" closure is honest about the epistemic state without claiming the original hypothesis is "wrong" — it is unobservable, not falsified.

**No project-internal jargon.** No "K-frame," "K-vocab," "B11," "T8," "Note K hypothesis" without context. The one reference to the v1 free-list prompt does not appear in §3. The paragraph references §4 only by content (the confabulation-pattern observation) — not by section number.

**PASS** on §3 quotability. This is the single most-likely-to-be-quoted piece of text in the entire memo and it is methodology-page-ready as written.

---

## §4 stimulus-as-anchor observation under T8 binding

The T8 binding is the most consequential test of the memo. The §4.4 prose must describe narratives as **citing** the prompt (descriptive-shape) without sliding into "the prompt **causes** the citation pattern" (causal) or "the model **interprets** the prompt" (introspective).

**Per-sentence audit of §4.4:**

| Sentence | T8 frame | Verdict |
|---|---|---|
| "Five of the 9 confabulation rows … carry a secondary attribution shape alongside their primary label." | descriptive | clean |
| "across 9 hand-coded confabulations, 5 (2 task-paradox + 3 mixed) carry a 'the instructions made me do it' flavor" | descriptive (paraphrase from v2-prompt status doc, attributed) | clean (Q2 attribution path) |
| "the v1 free-list prompt's imperative phrasing … appears to function as a categorical anchor that those 5 narratives cite as their proximate attribution" | borderline (verb "function as" leans causal/introspective; held by next paragraph) | borderline-PASS |
| "5 of 9 confabulation narratives reference the v1 prompt's imperative phrasing as their stated reason for declining" | descriptive | clean |
| "The narratives cite it as a proximate attribution" | descriptive | clean |
| "the v1 prompt's imperative phrasing serves as a categorical anchor for those 5 rows in the sense that the narratives cite it as their reason" | descriptive (the "in the sense that" is the disambiguator) | clean |
| "This is a descriptive observation about what the narratives reference, not a causal claim about what the prompt mechanically produced." | explicit non-claim | clean |
| "Whether this stimulus-citation pattern persists under softer phrasing … is an open empirical question this corpus cannot answer" | non-claim with forward-carry pointer | clean |
| "This corpus has no comparison arm: all 9 rows were collected under v1-prompt conditions." | descriptive (corpus-state) | clean |
| Scope discipline sentence (T6) | descriptive bound | clean |

**Single borderline sentence:** "appears to function as a categorical anchor." This is held by the immediately-following clarification. T8 is satisfied on the strength of the disambiguation. The optional refinement noted in T8 walk-through above (replace "appears to function as" with "appears as" or "is") would land the framing more cleanly but is not required for PASS.

**PASS** on T8 in §4.

---

## §6 audience pitch

§6 is the methodology-page-quotable non-claim list. Per Q3, no project-internal binding-note IDs in the §6 prose; IDs go in §8.

**Audit of §6 prose:**

- "the model's categorical structure, cognition, or any internal reasoning state" — plain language; describes the §1.5 framing without naming it as "§1.5"
- "9-row, single-provider, two-domain, v1-prompt cohort" — descriptive of the corpus; "v1-prompt" is the closest to a project-internal token but a methodology-page reader can resolve it from context (the prompts are versioned; v1 is the published version)
- "cross-provider, cross-model, cross-failure-mode, or cross-prompt-type generalization requires new evidence" — plain language; standard methodological hedge
- "v1 prompt templates are modified" — plain language
- "Phase 5+ forward-carry pointer referenced in a separate status document" — plain language
- "CDA protocol" — plain English; CDA is named on the methodology page; standard glossary term
- "schema in `cdb_core/schemas.py`" — file path is the most project-internal token in §6, but it is a path, not a binding-note ID; readers who are not project-internal can skip or click the path
- "Smith's S, Romney CCM, MDS, Procrustes, or OCI" — methodological terms named on the methodology page; not project-internal
- "Note L" / "any other separately designated hypothesis" — Note L is a hypothetical; Note K is canonical; standard
- "v2 prompt sub-study is proposed or initiated" — plain language

**No binding-note IDs in §6 prose.** Q3 satisfied.

The §6 list is methodology-page-quotable. A reader visiting `cogstructurelab.com/methodology` and encountering this list as a sidebar or "what this finding does not claim" callout would read it as plain-language methodological discipline.

**PASS** on §6.

---

## §8 carry-forward mapping audit

I cross-checked §8 against the T10 five-category vocabulary. The plan-pass verdict's §8 audit found the mapping substantially correct; this content-pass verdict re-confirms.

**Status qualifier coverage:**

- CARRIES FORWARD (active): named on each line for the 8 original Phase 4a.1 notes (minus 4), A1–A8, B1–B6, B10, B12, B14, B15, R1–R5, S1–S4
- CARRIES FORWARD (latent): named for original Note 4
- REPLACED (audit preserved): named for B11
- VACUOUS (audit preserved): named for B7, B8, B9, B13
- SATISFIED (specific deliverable; gate posture preserved): named for T1–T10, R6, S5

Every binding note carries exactly one parenthesized status qualifier. The mapping is self-documenting.

**One micro-observation (non-blocking):** §8 "Original Phase 4a.1 binding notes (1–8)" line groups Notes 1, 2, 3, 5, 6, 7, 8 under (active) and singles out Note 4 as (latent). The grouping is correct and reads cleanly. No edit needed.

**Section-to-binding-note mapping table:** the table at the end of §8 is a useful cross-reference but is not part of the T10 spec. It is supplementary and reads cleanly.

**PASS** on §8.

---

## S5 disposition

S5 (from Task #16 SME verdict, 2026-05-04) was partially consumed by the parent T4-redo plan-pass verdict (2026-05-05) and further partially consumed by the RD-3 plan-pass verdict (2026-05-06). This content-pass verdict is the third and final pass.

**S5 is fully satisfied by this verdict, conditional on Punted Item (a) rewording.**

Specifically:
- The memo content has been written as the canonical S5 artifact.
- The memo has been routed through the CDA SME at the content-verdict gate per the plan and the parent verdict.
- The CDA SME content verdict is PASS-WITH-NOTES (this verdict).
- The single required pre-merge edit (Punted Item (a) — "internal safety protocols" rewording) is bounded, single-sentence, and does not require a third SME pass after the Coder applies it.

After the Coder applies the Punted Item (a) rewording in a follow-on commit on the same RD-3 task line and the Reviewer re-confirms the single phrase, S5 is closed.

**The S5 gate posture survives this satisfaction.** Per T10 SATISFIED-category definition, the specific S5 deliverable (the memo, SME-PASSed) is landed; the gate posture — that any future methodology-page-bound text on Note K routes through the CDA SME — survives as a general principle and is not extinguished by this specific deliverable. If the memo is later rendered on the methodology page with new gloss that changes the methodological claim, the gloss routes through me as a fresh review.

---

## What I am explicitly NOT ruling on

- **The eventual T5 / Phase 4a closure analytical work.** The memo §5 names the analytical layer as unblocked; the actual statistical computation (Smith's S, Romney CCM, MDS, Procrustes, OCI) is a future Architect plan with full SME review surface. Per parent Q5.

- **The v2 prompt comparison study.** Phase 5+ candidate per `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md`. The memo references it as a forward-carry pointer; that is the only motion this work takes on the v2 prompt.

- **The phi-4 ×6, gpt-5.4-mini ×2, mistral-small ×1 unexplained failures.** Separate Architect tasks per recovery report §7.

- **Dashboard rendering of the methodology page.** Phase 5/6 UI/UX-gated work. The memo §3 disposition statement and the §4 finding statement are quotable by the eventual UI rendering, but the rendering is a separate task with its own UI/UX gate. SME re-review only if the gloss changes the methodological claim.

- **The §4.4 optional refinement** ("appears to function as" → "appears as" / "is"). This is methodologically nice-to-have, not required. The Coder may apply it in the same follow-on commit as the Punted Item (a) rewording or leave it as-is.

- **The legacy `thoughts_token_count=0` records** when downstream analytical work consumes the field. The memo §5 caveat names the issue per S2; the actual handling is gated at the future T5/closure analytical-computation plan.

---

## Required before merge

1. **Apply the Punted Item (a) rewording in §2 Layer C line 42.** Replace `attribute the failure to "internal safety protocols" or similar mechanisms` with one of the three approved paraphrastic forms:
   - `attribute the failure to internal safety mechanisms or similar` (minimal change; drops quote marks; replaces verbatim phrase with paraphrastic descriptor)
   - `attribute the failure to safety mechanisms, task paradoxes, or topic sensitivity` (matches §3 phrasing exactly; aligns §2 Layer C with §3 disposition)
   - `attribute the failure to mechanisms consistent with categorical knowledge from the training corpus` (matches the §2 Layer C second-clause phrasing; eliminates redundant restatement)

   Coder picks one of the three. Reviewer re-checks the single phrase. No third SME pass required.

The Coder commits the rewording on the same RD-3 task line per CLAUDE.md §8 ("PASS-WITH-NOTES requires the Coder to apply notes in a follow-on commit on the same task line").

---

## Carry-forward note

S5 (Task #16) — fully consumed by this verdict (conditional on Punted Item (a) rewording).

T1–T10 (T4 redo) — all SATISFIED (specific deliverable; gate posture preserved). T1 vocabulary discipline, T6 scope discipline, T8 descriptive-shape discipline, and T9 phrasing exclusions all survive as general posture for any future methodology-page-bound text on Note K, the cap-exhaustion finding, or any related downstream surface.

Parent T1, T4, T5, T6, T7 — all discharged at the memo deliverable.

T2 (RD-2 enum rename), T3 (RD-1 docstring banner), R6 (recovery rate threshold) — all SATISFIED at their respective deliverables.

A6 (T3A pre-T3B gate), B5 (detector role-change SME-review-at-code-review-time precedent), B12 (binding precedent for future batches), B14 (T5 §8.1/§8.2 numerics-vs-interpretation separation) — all CARRIES FORWARD (active). B14 in particular binds the eventual T5 redo §8 architecture.

B7, B8, B9, B13 — VACUOUS (audit preserved). The Amendment 2 disposition arithmetic and the K-frame N≥10 refinement question are no longer applied; their historical role survives as audit at the originating verdicts.

B11 — REPLACED (audit preserved). The K-frame/K-vocab dichotomy is superseded by the RD-2 confabulation classification schema; the May-1 schema is preserved as audit at the sibling `.SUPERSEDED.md`.

S1–S4 (Task #16) — CARRIES FORWARD (active). S1 gates collection cap. S2 governs `thoughts_token_count` four-state disambiguation; cited by name in this memo's §5. S3 and S4 govern future schema/dictionary work. All four are actively gating, not latent.

R1–R5 (Phase 4a recovery) — local to the recovery operation; CARRIES FORWARD (active) for any future recovery campaign.

**Active binding-note count after this verdict: ≈47** (unchanged from the plan-pass verdict; T8–T10 SATISFIED at the memo deliverable; T1–T7 SATISFIED at the memo deliverable; gate postures preserved).

---

## Sign-off

The RD-3 reframing memo is methodologically sound. The Coder applied T1, T4, T5, T6, T7, T8, T9, T10 throughout the draft; the Reviewer caught the §3 internal cross-reference on the first pass and the Coder fixed it on the second pass; the Reviewer correctly punted the two notes-level items (Q2 paraphrase-vs-verbatim and S1–S4 active-vs-latent) to me. My ruling on those two items is (a) reword "internal safety protocols" — required pre-merge; (b) leave S1–S4 = active — confirmed correct.

The §3 disposition paragraph stands alone under extraction and is methodology-page-ready. The §4 stimulus-as-anchor observation holds the descriptive-shape line under T8 with the second paragraph's disambiguation discharging the borderline first sentence. The §6 non-claim list is plain-language and legible to a non-project methodology-page audience. The §8 carry-forward mapping uses the T10 five-category vocabulary correctly.

The single required edit (Punted Item (a) rewording) is bounded, single-sentence, and does not require a third SME pass after the Coder applies it. After the Coder commits the rewording and the Reviewer re-confirms, S5 is closed in full.

**Verdict: PASS-WITH-NOTES.** S5 satisfied conditional on Punted Item (a) rewording. Phase 5/6 methodology-page UI rendering at the methodology-text gate is unblocked once the rewording lands.

*Posted to `#lsb-cda-sme`. The CDA SME thanks the Coder for the unusually clean draft execution under a 10-binding-note constraint; the §3 paragraph in particular is a piece of methodology-text the project can quote on the public methodology page without further editorial work. The Reviewer's punt of the two notes-level items to this content-pass verdict is the right pipeline discipline — the 8-word threshold caught what it was designed to catch; the 3-word verbatim is a Q2-discipline question, not a 8-word-grep question, and routing it to the SME content review is the correct lane.*
