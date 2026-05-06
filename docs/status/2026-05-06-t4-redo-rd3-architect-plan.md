# Phase 4a.1 T4 Redo RD-3 — Architect Plan

**Date:** 2026-05-06
**Planner:** Architect agent (Opus)
**Task:** Phase 4a.1 T4 redo — RD-3 (the canonical reframing memo)
**Parent plan:** `docs/status/2026-05-05-t4-redo-architect-plan.md` (defines RD-1, RD-2, RD-3; RD-3 task spec at §2)
**Plan-level SME verdict on parent:** `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md` (PASS-WITH-NOTES; binding T1, T4, T5, T6, T7 on RD-3)
**Predecessor task verdicts (RD-1 + RD-2 closed):**
- RD-1 reviewer + tester: `docs/status/2026-05-05-t4-redo-rd1-reviewer-verdict.md`, `docs/status/2026-05-05-t4-redo-rd1-tester-verdict.md` (commit `ad5f975`)
- RD-2 reviewer + tester: `docs/status/2026-05-05-t4-redo-rd2-reviewer-verdict.md`, `docs/status/2026-05-05-t4-redo-rd2-tester-verdict.md` (commit `148a620`; tests `014b999`)
- RD-2 hand-code commit: `5172b0d` (9/9 classified)

**Companion docs (mandatory reading for the Coder before drafting):**
- `ARCHITECTURE.md` §1.5 (binding framing on all generated text — corpus lens, forbidden vocabulary, the website is the artifact)
- `CLAUDE.md` §6 binding rules (especially R7 schema/dictionary lockstep — N/A here, R8 prompt versioning — N/A here, R11 no point estimates without uncertainty — N/A here, R13 plan must carry SME PASS), §7 forbidden vocabulary, §9 pitfall 13 (cross-boundary detector reuse — informational; RD-3 introduces no detectors)
- `docs/SME_REVIEW.md` — sanity-checked; no measure-threshold implications (RD-3 does not compute measures)
- `docs/BOOTSTRAP_DESIGN.md` — sanity-checked; no Level 1 / Level 2 implications (RD-3 does not compute statistics)

**Gate chain (mandatory, in order):**
1. **CDA SME PASS or PASS-WITH-NOTES on this plan** — non-negotiable per CLAUDE.md §6 R13 (re-routes through SME because RD-3's content was non-trivially re-shaped after the parent plan's PASS — see §3 below)
2. Coder drafts the memo against this plan + the parent plan + the parent SME verdict's T-series
3. Reviewer PASS on the Coder commit (forbidden-vocab scan, structure check, cross-reference audit)
4. Tester PASS (regression check only — memo is prose, no tests)
5. **CDA SME PASS on the memo's content** at `docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md` — this is the artifact that completes S5 from the Task #16 verdict

> **Status before Coder may start RD-3:** CDA SME PASS or PASS-WITH-NOTES on this plan. Mark's §5 framing decisions Q1–Q3 from the parent plan are already signed off (RD-1 commit `ad5f975` and RD-2 commit `148a620` both landed under PASSed gate chain). No new operator sign-off required.

---

## §0. Why this plan exists separate from the parent

The parent T4-redo plan (`docs/status/2026-05-05-t4-redo-architect-plan.md`) defined RD-3 at a level of detail sufficient to identify it as a distinct task with a target file path, a section structure, and a binding §1.5 framing. The parent plan's SME verdict (`docs/status/2026-05-05-t4-redo-cda-sme-verdict.md`) layered seven binding T-series notes onto the eventual memo, of which **T1, T4, T5, T6, T7 bind RD-3 directly** (T2 was RD-2 enum-rename scope; T3 was RD-1 docstring banner scope — both already discharged).

Three things changed between the parent plan and now that justify a fresh RD-3 plan rather than a direct hand-off to the Coder under the parent's §2 RD-3 spec:

1. **The hand-coded RD-2 distribution is in.** Parent §2 RD-3 said "§4 names the four confabulation labels and reports the actual distribution from Mark's hand-code." The actual distribution (commit `5172b0d`, verified at `data/derived/decline_interviews_confabulation_classification.jsonl`) is **4 safety-attribution + 2 task-paradox + 3 mixed + 0 not-confabulation + 0 topic-sensitivity**. Two specific shapes of this distribution materially affect the memo:
   - **0 not-confabulation rows.** SME T5 conditioned the §4 substantive discussion on the existence of `not_confabulation` rows ("if Mark's hand-code produces any row classified as `not_confabulation`, the memo §4 must discuss it explicitly"). With 0 such rows, T5's "or" clause applies: "if no row classifies as `not_confabulation`, the memo §4 may state that the schema's escape hatch was not triggered and move on." That moves §4 from "complicates the blind-spot framing" framing to "uniformly under blind-spot conditions" framing — a different §4 thesis.
   - **0 topic-sensitivity rows.** The parent's RD-2 schema enumerated three primary substantive labels (safety-attribution, task-paradox, topic-sensitivity) plus mixed plus the not-confabulation sentinel. The hand-code uses three of the five (safety-attribution, task-paradox, mixed), leaving topic-sensitivity unused. The memo §4 must address what an unused-but-defined label means for the finding's scope.

2. **Mark's parked v2 prompt observation now belongs in §4.** The status doc at `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md` was filed 2026-05-06 (after parent plan + parent SME verdict). Its §5 explicitly assigns the stimulus-as-anchor observation to RD-3 §4 as the substantive content that fills the space SME T5 was originally going to fill. The parent plan could not anticipate this content; this RD-3 plan must.

3. **The RD-1 and RD-2 supersedure work is now visible on master.** The memo's §2 ("what changed") and §7 ("audit trail") cross-reference files that did not exist when the parent plan was written. Those file paths and their commit hashes are now resolvable; the memo prose can be specific rather than promissory.

A fresh plan is the surgical move. The parent plan's RD-3 spec is not contradicted; it is refined. SME re-routes briefly because (a) §4's thesis has shifted from "discuss any `not_confabulation` rows" to "stimulus-as-anchor finding under all-confabulation conditions," (b) the v2-prompt parked observation is methodology-adjacent and must be SME-vetted before the Coder's prose touches it.

---

## §1. Disposition table (RD-3-local, layered onto parent plan §1)

| Concern | Disposition under RD-3 | Rationale |
|---|---|---|
| **RD-3 deliverable path** | **`docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md`** | Preserves the path the parent plan set. The memo's filename retains the 2026-05-05 anchor date because that is the date of the recovery campaign and the parent T4-redo plan; the memo's own commit date is 2026-05-06 or later. The path is binding per parent plan §2 RD-3. |
| **RD-3 deliverable shape** | **Single methodology memo, prose only.** No code, no JSONL, no schema, no tests, no fixtures. | The parent plan and parent SME verdict both characterize the memo as text-on-disk that the eventual Phase 5/6 UI/UX rendering will quote. Adding code would conflate two review surfaces. |
| **Number of Coder commits to produce the memo** | **One commit.** Single Coder task per CLAUDE.md §8. | The memo is small enough that bundled drafting fits in one session. Splitting into "skeleton commit + content commit" would inflate the audit trail without adding review value. The Coder writes the full memo in one PR; if the prose comes back from SME with required changes, those go in a second commit on the same feature line, not as a new task. |
| **§4 thesis under the hand-coded distribution** | **Stimulus-as-anchor under all-confabulation conditions** (per `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md` §5). | All 9 rows are `under_blind_spot=true` confabulations with no `not_confabulation` escape hatch triggered. 5/9 rows (2 task-paradox + 3 mixed) carry "the instructions made me do it" rationales. The methodologically interesting observation under this distribution is that ~5/9 confabulations under v1 prompt conditions cite the prompt's own imperative phrasing as their attribution anchor — which is itself a finding about the corpus lens's response to stimulus shape. **SME ruling required — see §4 Q1.** |
| **v2 prompt sub-study** | **Named in §4 as a deferred Phase 5+ open question; referenced by file path; content not duplicated.** | The status doc at `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md` is the canonical record. The memo references it; it does not paraphrase it. Per the parking rationale in that doc §3, the v2 sub-study cannot answer the question this corpus poses; it can only be a future comparison-study arm. The memo treats it accordingly. |
| **Topic-sensitivity-confabulation label used 0/9** | **Memo §4 explicitly notes the unused label and bounds the schema's scope.** | An unused-but-defined enum value carries information: the schema admitted three substantive shapes a priori (safety-attribution, task-paradox, topic-sensitivity); under the v1 prompt + cap-exhaustion conditions, only two of those shapes appeared (plus mixed). That is not "the schema is wrong"; it is "the schema's third primary shape is unconstrained by this 9-row cohort." The §4 prose must say so. |
| **Forbidden vocabulary** | **None used in the plan; the Coder's memo is bound by SME T1.** | The "blind-spot conditions" phrase is borderline and is governed by SME T1's first-use definition requirement. The plan refers to T1 by reference and does not redefine it. |
| **Schema changes** | **NONE.** | Pydantic v0.1.11 is unchanged. No `cdb_core/schemas.py` edits. No `DATA_DICTIONARY.md` updates. |
| **`data/raw/`, `data/derived/` edits** | **NONE.** | The 9-row hand-coded artifact is the source of the §4 distribution; it is read-only for RD-3. The 24 decline-interview records are read-only. The 20 recovery records are read-only. |
| **Prompt-template change** | **NONE.** v1 prompts unchanged. Per CLAUDE.md §6 R8 a v2 prompt would require its own directory and a comparison-study design, neither of which is in scope. The §4 references the v2-prompt status doc only as a forward-carry pointer. |
| **Analytical computation (Smith's S, Romney, MDS, Procrustes)** | **OUT OF SCOPE.** Per parent SME Q5: distinct review surfaces. | Memo §5 names the analytical work as unblocked; §6 forward-carry lists it as the natural T5 / Phase 4a closure deliverable. |

---

## §2. Single Coder task (RD-3)

### Task RD-3 — T4-redo reframing memo

**Owner:** Coder (full memo draft) → Reviewer (forbidden-vocab + structure + cross-reference audit) → CDA SME (final content PASS, S5-completing)
**One commit.** No bundling. The memo is prose-only.

**Files:**
- New: `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md` — the canonical reframing memo. **This is the artifact S5 binds.**

**No other file touched.** No code, no JSONL, no schema, no test, no fixture, no script, no README, no CLAUDE.md, no DATA_DICTIONARY.md, no DESIGN_SYSTEM.md, no data file under `data/raw/` or `data/derived/`, no commit to existing `docs/status/` files.

**Memo structure (binding — refines parent plan §2 RD-3 with the post-RD-2 distribution and the v2-prompt observation):**

#### §1. Header
Date (memo commit date), scope ("Phase 4a.1 T4 redo, replacing T4.2 Note K disposition under the 2026-05-04 cap-exhaustion reframe"), the audit-trail one-liner naming the parent plan + parent SME verdict + RD-1 + RD-2 commits + this RD-3 plan + its SME verdict, and the canonical companion-docs list (Task 16 verdict; recovery report; v2-prompt status doc).

#### §2. What changed
≤500 words. Three layers in order:
- **Layer A — May 1 disposition (the falsified claim).** The parent T4.2 work disposed Note K as "CONFIRMED — Gemini single-provider safety-layer activation." That disposition was committed and SME-PASSed in good faith; the audit trail stands.
- **Layer B — 2026-05-04 cap-exhaustion finding.** Three independent probes (Stage 1.5, 1.5b, 1.6) plus the 2026-05-05 recovery campaign (100% Gemini recovery rate at `max_tokens=16384`) demonstrated that the originating Phase 4a empty-output failures were instrument events, not refusals.
- **Layer C — what this means for the 9 rows.** The 9 originally-Gemini decline-interview narratives describing "internal safety protocols" were follow-up responses to instrument events whose mechanical cause was not surfaced in the inputs available to the model at decline-interview time. The narratives are now best understood as confabulation patterns under blind-spot conditions.

The §2 must define "blind-spot conditions" on first use per **SME T1**: *"conditions in which the originating mechanical cause of a failure was not surfaced in the inputs available to the model at decline-interview time."* Subsequent uses can use the shorthand.

The §2 must scope the reframe to the 9 originally-Gemini rows only per **SME T4 (extended)**: of the 24 decline-interview records, only 9 are reframed by this memo. The other 15 records (3 z-ai/glm-5.1 empty-freelist-propagation rows + 12 records of other classifications with non-cap-exhaustion upstream causes) are unaffected. Without this scoping, a reader could mistakenly conclude the entire decline-interview corpus is reinterpreted.

#### §3. Disposition: Note K is REPLACED
Single methodology-page-quotable paragraph. The parent plan §2 RD-3 supplied a draft; the Coder may use that draft as a starting point but must apply T1 vocabulary discipline. Specifically: replace "the model could not observe the actual mechanical cause" with "the actual mechanical cause was not surfaced in the inputs available to the model at decline-interview time" or an equivalent §1.5-clean reformulation. The word **REPLACED** is binding (per parent SME Q3 ruling — not RETIRED, not NOT CONFIRMED, not "superseded" — the recovery report's R1 "replace as authoritative for the cell" applies to records, not dispositions). The paragraph must stand alone when quoted (no internal cross-references like "see §5 below" that would break under extraction).

#### §4. Substantive observation under post-recovery conditions
Per the post-RD-2 distribution and the v2-prompt status doc §5 forward-carry, §4 is **not** "discuss any `not_confabulation` rows" (T5's "if" clause); it is "report the stimulus-as-anchor observation under all-confabulation conditions" (T5's "else" clause).

Required content, in order:
1. **Distribution report.** State the distribution exactly: 4 safety-attribution + 2 task-paradox + 3 mixed + 0 not-confabulation + 0 topic-sensitivity, with all 9 rows classified `under_blind_spot=true`. Reference the artifact path `data/derived/decline_interviews_confabulation_classification.jsonl` and the RD-2 enum module `packages/cdb_analyze/cdb_analyze/confabulation_classification.py`.
2. **Schema-scope note.** The topic-sensitivity-confabulation label was defined a priori but not exercised by the 9-row cohort. State this as bounding the schema's coverage rather than as a defect: the v1-prompt + cap-exhaustion-condition cohort yielded two of the three primary shapes plus the mixed escape; cross-prompt or cross-condition cohorts may yield the third.
3. **No-`not_confabulation` note.** Per T5 (else clause): state explicitly that the schema's not-confabulation escape hatch was defined a priori but not triggered by this cohort. Under the cohort's conditions (all 9 rows `under_blind_spot=true` cap-exhaustion follow-ups), no row's narrative correctly identifies the technical cause. The blind-spot framing applies uniformly to the 9 rows.
4. **Stimulus-as-anchor observation.** Per the parked v2-prompt status doc §5: 5/9 confabulations (the 2 task-paradox + 3 mixed rows) carry a "the instructions made me do it" rationale. The v1 free-list prompt's imperative phrasing ("do not explain or categorize") functions as a categorical anchor that ~5/9 informants under blind-spot conditions cited as their attribution. The Coder may quote the v2-prompt status doc §5 paragraph as the canonical phrasing of this observation, attributed to that doc.
5. **v2-prompt forward-carry pointer.** State that whether this stimulus-as-anchor pattern persists under softer phrasing is an open empirical question this corpus cannot answer. Reference `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md` by path. Do **not** duplicate that doc's content.
6. **§4 scope discipline (per SME T6).** The §4 prose must explicitly include: "this is a single-provider, two-domain finding from a 9-row cohort; cross-provider or cross-failure-mode generalization requires new evidence." Forbidden §4 claims (per T6): generalization to other providers / models / failure modes / prompt types; claims about the model's "actual" reasoning behavior, internal state, or perceptual capacity; "publishable" framing; assignment of a new Note designation (e.g., "Note L"). Permitted: the descriptive observation, the distribution claim, and the corpus-lens-property gloss.

#### §5. What the recovered corpus enables (and doesn't)
- **Enables:** With 20 recovered Gemini/glm-5.1/llama-maverick informants appended to the prior corpus, the Phase 4 analytical layer (Smith's S, Romney CCM, MDS, Procrustes, OCI) can now run on the corrected corpus. The memo names this as unblocked.
- **Does NOT compute** any of those statistics. They are the natural T5 / Phase 4a closure deliverable per parent SME Q5.
- **One-sentence note (per SME T4 extended):** downstream analytical work consuming `thoughts_token_count` will need to address the legacy `thoughts_token_count=0` records explicitly per Task #16 SME S2 (the field's value `0` is reported in two distinct cases — model produced no reasoning tokens, or provider does not surface the field — and a third forensic case applies to legacy Phase 4a records pre-Task-#16 where the field was not captured at collection time).

#### §6. What this memo does NOT claim
Mirror the recovery report's §6 disposition pattern. The memo:
- Does NOT claim model worldview, belief, or cognition. The §1.5 framing applies throughout.
- Does NOT claim the confabulation pattern generalizes beyond the 9-row, single-provider, two-domain, v1-prompt cohort.
- Does NOT modify the v1 prompt templates.
- Does NOT modify the CDA protocol.
- Does NOT modify the schemas.
- Does NOT compute analytical statistics.
- Does NOT assign a new Note designation.
- Does NOT reframe Note A, B, C, … or any binding note other than the Note K disposition. The memo is local to Note K and the cap-exhaustion reframe.
- Does NOT propose new collection beyond what the parent plan and parent SME verdict already named (the v2 prompt sub-study is a Phase 5+ forward-carry pointer, not a proposal).

#### §7. Forward carry
Enumerate. These all live elsewhere; the memo is the single index point:
- **build_db.py rerun** — separate ops task per recovery report §5 / SME R5. Command provided in recovery report §5; do not duplicate.
- **phi-4 ×6 adapter task** — separate Architect task per recovery report §7.4.
- **gpt-5.4-mini ×2 + mistral-small ×1 unexplained-failure investigation** — separate task per recovery report §7.3.
- **v2 prompt comparison study** — Phase 5+ candidate per `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md`. Trigger conditions in that doc §4.
- **T5 redo / Phase 4a closure analytical computation** — separate Architect plan with full SME review surface per parent SME Q5.

#### §8. Audit trail
Cross-references with file paths and commit hashes where applicable:
- **Predecessors superseded** (interpretively, not destructively): May 1 hand-coded artifact at `data/derived/decline_interviews_safety_attribution_subtype.jsonl` (annotated by `data/derived/decline_interviews_safety_attribution_subtype.SUPERSEDED.md`, RD-1 commit `ad5f975`); the cross-tab script at `scripts/phase4a1_note_j_crosstab.py` (annotated by `scripts/phase4a1_note_j_crosstab.SUPERSEDED.md`, same commit); the original Note K hypothesis statement (preserved verbatim in the prior verdict files; not edited).
- **Falsifying evidence chain:** `docs/status/2026-05-04-task-16-architect-plan.md`, `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (S5 originator), `docs/status/2026-05-05-phase4a-recovery-architect-plan.md`, `docs/status/2026-05-05-phase4a-recovery-cda-sme-verdict.md`, `docs/status/2026-05-05-phase4a-recovery-report.md`.
- **Replacement evidence:** `data/derived/decline_interviews_confabulation_classification.jsonl` (RD-2 hand-code, commit `5172b0d`), `packages/cdb_analyze/cdb_analyze/confabulation_classification.py` (RD-2 schema, commit `148a620`).
- **Gate verdicts:** parent T4-redo plan SME verdict (`docs/status/2026-05-05-t4-redo-cda-sme-verdict.md`), this RD-3 plan's SME verdict (path TBD per §5 below), the eventual RD-3 content SME verdict (path per §5).
- **Carry-forward of binding notes (per SME T7):**
  - All 8 original Phase 4a.1 binding notes carry forward (most are about cross-tab structure and small-n thresholds, both still relevant).
  - **A6 (T3A pre-T3B gate)** carries forward unchanged — explicitly named per SME T7.
  - A1–A5, A7, A8 carry forward unchanged.
  - B1–B6 carry forward; B5 (detector role-change SME review at code-review time precedent — CLAUDE.md §9 pitfall 13) is reaffirmed; B6 (T5 §8 public-copy guardrails) carries forward and binds the eventual T5 redo.
  - **B7, B8, B9 are vacuous** under the new framing (the disposition tier arithmetic they govern no longer applies).
  - B10 (soft, future batches) carries forward.
  - **B11 is REPLACED** by the RD-2 confabulation classification schema. The K-frame/K-vocab dichotomy is superseded.
  - B12 carries forward as binding precedent for future batches.
  - **B13 is vacuous** under the new framing (the K-frame N≥10 refinement question is moot; the K-frame/K-vocab dichotomy is not carried into the new schema).
  - **B14 carries forward and binds the eventual T5 redo** §8 architecture (the numerics-vs-interpretation separation is still load-bearing on different numerics).
  - B15 (soft, dashboard glossing) carries forward.
  - **R6 (recovery rate <80% threshold)** was satisfied with 100% recovery; binding consumed — explicitly named per SME T7.
  - R1–R5 (recovery) are local to the recovery operation; do not bind T4 redo.
  - S1–S4 (Task #16) are local to Task #16 scope.
  - **S5 is SATISFIED** by the SME PASS on this memo's content (the second-pass verdict at the path in §5 below).
  - T1, T4, T5, T6, T7 (parent T4-redo SME verdict) bind RD-3 directly and are visibly satisfied as named in §2 (T1 first-use definition; T4 9-row scoping + thoughts_token_count caveat), §4 (T5 else clause; T6 scope discipline), §8 (T7 A6 + R6 explicit + supersede-convention non-codification).
  - **T2 (RD-2 enum rename) discharged** at RD-2 commit `148a620`.
  - **T3 (RD-1 docstring banner) discharged** at RD-1 commit `ad5f975`.
- **Supersede-convention status (per SME T7 second clause):** the sibling `.SUPERSEDED.md` annotation pattern is the project's *operational* practice for marking superseded `data/derived/` artifacts; it is **NOT** codified as a CLAUDE.md §9 pitfall. The convention is verdict-by-verdict, not blanket-binding.

**Section-to-binding-note mapping (audit-friendly):**

| Memo section | Binding notes satisfied |
|---|---|
| §1 Header | (cross-references parent plan + parent SME verdict + RD-1 + RD-2) |
| §2 What changed | **T1** (blind-spot first-use definition); **T4** (9-row scoping) |
| §3 Disposition | parent SME Q3 (REPLACED is binding); **T1** (vocabulary discipline on the disposition paragraph) |
| §4 Substantive observation | **T5** (else clause: no `not_confabulation` rows); **T6** (scope discipline: descriptive + distribution claims only); informational reference to v2-prompt status doc |
| §5 What the corpus enables | parent SME Q5 (analytical work out of scope); **T4 extended** (legacy `thoughts_token_count=0` caveat per Task #16 S2) |
| §6 What this memo does NOT claim | parent §1.5 framing; **T6** (forbidden generalizations) |
| §7 Forward carry | parent SME "What I am explicitly NOT ruling on"; recovery report §7 |
| §8 Audit trail | **T7** (A6 + R6 explicit; supersede-convention not codified) |

#### §1.5 framing — binding throughout
Recommended phrasings (per parent SME proactive Check 1):
- "the actual mechanical cause was not surfaced in the inputs available to the model at decline-interview time"
- "the model received the empty-output text + the prompt asking it to describe what happened; it did not receive the API-level diagnostic that would have shown the cap exhaustion"
- "the response is consistent with post-hoc attribution under conditions where the originating mechanical cause was not observable from the inputs the model had"
- "the model's output narrative attributes the failure to safety mechanisms; the actual cause was mechanical"

Forbidden in this memo (Reviewer enforces; SME content review double-checks):
- "the model could not see the actual cause" / "could not see"
- "the model was blind to the cap exhaustion"
- "the model didn't know it had hit the cap"
- "the model believed there was a safety event"
- "the model thought it had been blocked"
- "the model's worldview about safety"
- Any framing that uses "blind spot" as a noun applied to the model's perception
- Any phrasing implying the model has introspective access to its own cause-of-failure
- "publishable" framing (per T6)
- A new Note designation for the confabulation finding (per parent SME Q3 + T6)

The phrase "blind-spot conditions" is permitted **only after** the §2 first-use definition is in place.

**Acceptance criteria:**

The Coder commit is acceptance-tested against:
1. Memo at `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md` exists and follows the §1–§8 structure above.
2. §2 contains a first-use definition of "blind-spot conditions" matching SME T1's required wording (paraphrase permitted; semantic equivalence required).
3. §2 scopes the reframe to the 9 originally-Gemini rows and explicitly notes the other 15 decline-interview records are unaffected (per SME T4 extended).
4. §3 is a single methodology-page-quotable paragraph that uses the word **REPLACED** and contains no internal cross-references that would break under extraction.
5. §4 reports the distribution exactly: 4 safety-attribution + 2 task-paradox + 3 mixed + 0 not-confabulation + 0 topic-sensitivity, with all 9 rows `under_blind_spot=true`.
6. §4 contains the SME T6 scope-discipline sentence: "this is a single-provider, two-domain finding from a 9-row cohort; cross-provider or cross-failure-mode generalization requires new evidence" (or semantically equivalent phrasing).
7. §4 references `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md` by path and does not duplicate its content.
8. §5 contains the one-sentence legacy-`thoughts_token_count=0` caveat (per SME T4 extended).
9. §6 contains the explicit non-claim list (worldview/belief/cognition; cross-provider generalization; new Note designation; analytical computation).
10. §7 enumerates the four forward-carry items by file/path.
11. §8 contains the carry-forward-of-binding-notes mapping with A6, R6, T2, T3, B11, B7–B9, B13 explicitly named, and the supersede-convention non-codification note.
12. **No forbidden vocabulary anywhere.** Reviewer scan + SME content review.
13. **No point estimate without uncertainty** — N/A; the memo reports a 9-row complete-enumeration distribution, not a sample statistic.
14. **No new dependencies** added; no schema change; no test change; no code change. The memo is a single new prose file.
15. Conventional Commits format on the commit message: `docs(status): T4 redo RD-3 — reframing memo` (or the Coder's preferred wording matching `docs(status):` scope).
16. Commit body references parent plan path + parent SME verdict path + this RD-3 plan path + this RD-3 plan's SME verdict path.

**Test coverage (Tester):** None required (memo is prose). Tester confirms regression-free state of the existing test suite (`uv run pytest && uv run ruff check . && uv run mypy packages/`).

**Reading list for Coder (mandatory before drafting):**
1. This RD-3 plan, in full.
2. The parent T4-redo plan: `docs/status/2026-05-05-t4-redo-architect-plan.md`.
3. The parent T4-redo CDA SME verdict: `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md` (especially T1, T4, T5, T6, T7 binding notes; proactive checks 1, 6, 7).
4. Task #16 CDA SME verdict: `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (especially S5 originator and §B "Note K implications for the T4-redo task").
5. Phase 4a recovery report: `docs/status/2026-05-05-phase4a-recovery-report.md` (especially §6 "what the recovery does not change" — pattern for §6 of the memo).
6. v2-prompt forward-carry doc: `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md` (especially §5 for §4 framing; do NOT duplicate §1–§4 content).
7. RD-1 supersede annotations: `data/derived/decline_interviews_safety_attribution_subtype.SUPERSEDED.md`, `scripts/phase4a1_note_j_crosstab.SUPERSEDED.md`.
8. RD-2 hand-coded artifact: `data/derived/decline_interviews_confabulation_classification.jsonl` (Coder reads to confirm the §4 distribution; the plan asserts the distribution but the Coder verifies).
9. RD-2 schema module: `packages/cdb_analyze/cdb_analyze/confabulation_classification.py`.
10. `ARCHITECTURE.md` §1.5 — especially §1.5.1 corpus lens, §1.5.4 forbidden vocabulary, §1.5.6 the website is the artifact.
11. `CLAUDE.md` §6 (binding rules), §7 (forbidden vocabulary), §8 (commit conventions), §9 (pitfalls — informational; no detector work in scope).
12. The original T4 SME verdict (the work being reframed): `docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md` (especially Finding 1 Q1–Q4 and Finding 2; the Coder must understand what is being reframed).
13. The original Note K methodology context: `docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md` (especially Ruling 6 on coverage-caveat framing — informational; no retroactive edit needed).
14. `data/raw/decline_interviews.jsonl` — the verbatim narratives. The Coder must read the actual 9 narratives to draft accurate §3 and §4 prose. Reading the upstream source guards against accidentally over-claiming what the narratives say.

**Estimated cost:** $0 (no API calls; pure prose work).

**Estimated wall-clock:** 1 day of Coder draft work + Reviewer review + SME content review. The memo is small but the §1.5 framing discipline is high-effort.

**Gate verdicts required:**
- CDA SME PASS or PASS-WITH-NOTES on this RD-3 plan (gates the memo before the Coder starts).
- Reviewer PASS on the memo commit (forbidden-vocab scan; structure check; cross-reference audit; acceptance-criteria 1–16 above).
- Tester PASS on the memo commit (regression check only).
- **CDA SME PASS on the memo's content** at `docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md` — see §5 below. This is the S5-completing verdict.

---

## §3. Sequencing

```
[This RD-3 plan written]
        │
        ▼
[CDA SME review of THIS plan] ← MANDATORY GATE per CLAUDE.md §6 R13
        │
        ▼
   PASS / PASS-WITH-NOTES?
        │
        ▼
[Coder: Task RD-3 — reframing memo, single commit]
        │
        ▼
[Reviewer PASS on RD-3 commit (acceptance-criteria 1–16)]
        │
        ▼
[Tester PASS on RD-3 commit (regression check only)]
        │
        ▼
[CDA SME PASS on RD-3 memo content] ← SATISFIES S5 in full
        │
        ▼
[Architect schedules: T5 redo / Phase 4a closure analytical work as separate plan]
[Architect schedules: methodology-page UI/UX rendering as separate Phase 5/6 plan with UI/UX gate]
```

**Bundling boundaries (CLAUDE.md §8):** RD-3 is a single Coder commit. No bundling. Acceptance-criteria revisions (if SME content verdict requires changes) are folded into a follow-on commit on the same task line, not a new task.

---

## §4. Open questions for SME ruling

These are routed to the CDA SME explicitly. The plan cannot advance to Coder until the SME issues a verdict that addresses each. Format follows the parent plan's §6 structure.

### Q1 — §4 thesis under the post-RD-2 distribution

**Architect read:** Per the §1 disposition table row "§4 thesis under the hand-coded distribution" and per the v2-prompt status doc §5 forward-carry assignment, §4 should foreground the **stimulus-as-anchor observation** (5/9 confabulations cite v1-prompt imperative phrasing as their attribution anchor). This is the most informative observation the 9-row cohort supports under SME T6's scope discipline.

**SME confirm or override.** Alternatives:
- (a) §4 is shorter — just the distribution and the schema-scope note, with the stimulus-as-anchor observation deferred entirely to the v2-prompt status doc's own future treatment. Defensible if the SME considers the observation under-evidenced for methodology-page-bound text. Architect rejects: the v2-prompt status doc §5 explicitly assigns the observation to RD-3 §4, and parking it twice would muddy the audit trail.
- (b) §4 is longer — adds row-by-row narrative quotation. Defensible for transparency but conflicts with SME T6 (no claims about model "actual" reasoning) if the quotes are read as introspective. Architect rejects: per §4 Q2 below, paraphrase is safer than quotation.
- (c) The §4 stimulus-as-anchor observation gets its own future task / Note designation. Architect rejects: per parent SME Q3 (no new Note designation) and SME T6 (no "publishable" framing), the observation belongs in the memo as a bounded descriptive observation, not as a new investigation target.

### Q2 — Verbatim quotation vs. paraphrase of confabulation transcripts in §4

**Architect read:** **Paraphrase, not verbatim quotation.** The §4 scope discipline (T6) requires that the memo characterize the *shape* of attribution narratives without claiming the narratives are evidence of the model's actual reasoning. Verbatim quotation tilts a reader toward reading the quotes as introspective reports; paraphrase preserves the shape claim while keeping the §1.5 framing intact. The 9-row hand-coded artifact and the upstream `data/raw/decline_interviews.jsonl` are publicly available in the open data bundle for any reader who wants to see the verbatim text; the memo does not need to re-publish them.

**SME confirm or override.** Alternatives:
- (a) Quote one short representative narrative per label (4 quotations: one safety-attribution, one task-paradox, one mixed; topic-sensitivity has no rows; not-confabulation has no rows). Defensible for transparency. Architect's concern: this is the slipperiest place in the memo for §1.5 framing to fail. The Reviewer scan catches obvious forbidden-vocab tokens; subtler "the model is reporting what it experienced" framings can survive a Reviewer scan and only get caught in SME content review. Risk-asymmetric.
- (b) Quote all 9 narratives in full as an appendix. Architect rejects: would dominate the memo's prose-mass and re-publish what is already in the open data bundle.
- (c) Paraphrase only, per Architect read.

Architect's recommendation is (c). The SME's call.

### Q3 — Memo §6 "what this memo does NOT claim" — audience pitch

**Architect read:** The §6 list is methodology-page-bound (it will be quotable by the eventual UI/UX rendering of the methodology page) and should be pitched at a skeptical-but-non-specialist audience — the same audience the §3 disposition statement pitches to. That means §6 names the non-claims in plain language without invoking project-internal binding-note IDs (no "per SME T6," no "per Task #16 S5") in the §6 prose itself. The binding-note IDs go in §8 (audit trail).

**SME confirm or override.** Alternatives:
- (a) §6 references binding-note IDs inline. Architect rejects: makes the section illegible to the methodology-page audience.
- (b) §6 is split into two parts — a methodology-page-quotable list (no IDs) and a project-internal carry-forward (IDs). Architect open to this but considers it over-engineered for a single section; the §8 audit trail already serves the project-internal-carry-forward role.

### Q4 — Memo prose voice: first-person-project ("LSB notes that") vs. third-person ("the corpus shows")

**Architect read:** **Third-person.** The memo is methodology, not a project communication. Voice should be the same as the recovery report, the parent plan, the parent SME verdict — observational and neutral, not project-spokesperson-ish. "The 9 narratives, classified under conditions in which …" reads as analysis. "We at LSB note that …" reads as advocacy.

**SME confirm or override.** Alternatives are possible if the SME considers the third-person voice insufficiently transparent about who is making the methodology call. Architect's preference is to keep voice consistent with the rest of the project's `docs/status/` corpus.

### Q5 — Should §4 explicitly enumerate the 5/9 task-paradox + mixed rows by `decline_interview_id` to support the stimulus-as-anchor observation?

**Architect read:** **No.** Listing IDs would make the memo brittle (any future re-numbering breaks the prose) and would invite readers to chase the IDs into the artifact, which is a fine action but not one the §4 prose needs to scaffold. The artifact path + the distribution + the 5/9 fraction is sufficient.

**SME confirm or override.** Defensible alternative: enumerate IDs in a small table for transparency. Architect rejects on brittleness grounds; the SME's call.

### Q6 — RD-3 plan path and SME verdict path

**Architect read:** This plan lives at `docs/status/2026-05-06-t4-redo-rd3-architect-plan.md`. The SME verdict on this plan is expected at `docs/status/2026-05-06-t4-redo-rd3-cda-sme-plan-verdict.md`. The SME verdict on the memo content (the S5-completing verdict) is expected at `docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md`. These two SME verdict file paths are deterministic so the Coder and the Reviewer can reference them in commit bodies.

**SME confirm or override.** The SME may prefer different filenames; the canonical pair the Architect proposes is plan-verdict / content-verdict. The parent plan used `2026-05-05-t4-redo-cda-sme-verdict.md` (single verdict for one round-trip); RD-3 has two SME passes, so two filenames is the right granularity.

### Q7 — Does the memo need to explicitly reaffirm the parent T4-redo plan's §1 disposition table?

**Architect read:** **No.** The memo references the parent plan + parent SME verdict by path; the parent's §1 disposition table is consumed by reference. Restating the parent's disposition table in RD-3 would inflate the memo without adding clarity. The §8 carry-forward-of-binding-notes mapping is the canonical RD-3 expression of the parent's dispositions.

**SME confirm or override.** Defensible alternative: a one-paragraph "what the parent plan disposed and what this memo confirms" subsection in §1. Architect rejects: the parent plan + parent SME verdict are the canonical disposition record; the memo is the *output* of the disposition, not a re-disposition.

---

## §5. Second SME pass — content verdict

Per Task #16 SME verdict S5 second clause and parent T4-redo SME verdict Q6 ruling: **the memo's content must come back to the CDA SME for a fresh PASS, not just the plan-pass.**

**Operational binding for Coder:** When the Coder lands the RD-3 commit, the next pipeline step is the Reviewer (forbidden-vocab + structure + cross-reference audit), then the Tester (regression check), then **the CDA SME re-engages for a content review of the memo's prose.**

**SME content verdict file path:** `docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md` (deterministic).

**The SME content verdict completes S5.** Until it issues, S5 is partially-consumed (per parent SME verdict's "Carry-forward note"). After it issues with a PASS or PASS-WITH-NOTES, S5 is fully satisfied and any downstream Phase 5/6 UI/UX rendering of the methodology page is unblocked at the methodology-text gate. (The Phase 5/6 UI rendering still gets its own UI/UX gate per parent SME Q4.)

**SME content verdict scope:** The SME reviews the memo's *prose* against:
- T1 (blind-spot first-use definition + vocabulary discipline throughout)
- T4 (9-row scoping in §2; legacy `thoughts_token_count=0` caveat in §5)
- T5 (else clause: §4 explicitly states the not-confabulation escape was not triggered; the blind-spot framing applies uniformly)
- T6 (§4 scope discipline; descriptive + distribution claims only; no generalization; no Note designation; no "publishable" framing)
- T7 (§8 explicitly names A6 + R6; supersede-convention not codified as pitfall)
- §1.5 framing throughout (proactive Check 1 forbidden phrasings rejected; recommended phrasings used)
- §3 disposition statement is methodology-page-quotable (single paragraph, no internal cross-references)
- §4 is consistent with §4 Q1, Q2, Q5 above, per whichever ruling the SME issued in this plan-verdict
- §6 is consistent with §4 Q3 above
- Voice consistent with §4 Q4 above
- Cross-reference audit per §4 Q7 above

**SME content verdict outcome cases:**
- **PASS:** S5 fully satisfied. Memo is the canonical methodology-page-bound text on Note K. Architect schedules the next downstream tasks (T5 redo / Phase 4a closure; methodology-page UI rendering).
- **PASS-WITH-NOTES:** Coder applies notes in a follow-on commit on the same task line (CLAUDE.md §8 — RD-3 is one task, but a notes-applied follow-up commit is the right shape because the SME content verdict is the gate, not the Reviewer commit). After follow-on commit, the SME does not need a third pass unless the notes were extensive; the SME's PASS-WITH-NOTES verdict is already the operational PASS once the notes are applied and Reviewer-verified.
- **FAIL:** Memo is rejected. Architect re-routes through a fresh plan amendment (RD-4? a new RD-3 plan amendment?) with the SME's failure rationale incorporated. This case is unlikely given the SME's PASS-WITH-NOTES on the parent plan and the bounded nature of the changes RD-3 introduces, but the plan must contemplate it for completeness.

---

## §6. Risks (RD-3-local; layered onto parent plan §4)

### 6.1 The §4 thesis shift may not survive SME re-review

**Risk:** The parent plan's RD-3 §4 was thesis-conditioned on the existence of `not_confabulation` rows. With 0 such rows, §4 pivots to the stimulus-as-anchor observation. The SME may rule that the stimulus-as-anchor observation is insufficiently grounded for methodology-page-bound text and require §4 to be cut to "distribution + schema-scope note" only.

**Mitigation:** §4 Q1 surfaces this as an explicit SME question. If the SME rules (a) instead of the Architect's (c), the Coder writes a shorter §4 and the v2-prompt observation lives entirely in its parked status doc. That outcome is methodologically fine; it just thins the memo's substantive content.

### 6.2 The "blind-spot conditions" framing remains the highest-risk forbidden-vocab surface

**Risk:** Per parent SME proactive Check 1: "blind-spot conditions" is borderline §1.5.4. T1's first-use definition mitigates but does not eliminate the risk. If the Coder's memo prose drifts into "the model could not see" / "the model was blind to" framings, the SME content verdict catches it but only after the Coder's commit, which costs a round-trip.

**Mitigation:** The acceptance criterion 12 ("no forbidden vocabulary anywhere") and the Coder's reading list item 11 (CLAUDE.md §7) front-load the discipline. The Reviewer scan is a second line. The SME content verdict is the third. Three lines of defense are sufficient given the small prose surface.

### 6.3 The v2-prompt observation may bleed into a v2-prompt proposal

**Risk:** Mark's parked v2-prompt observation in `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md` is explicitly a forward-carry pointer, not a proposal. The Coder may inadvertently write §4 prose that reads as proposing the v2 sub-study rather than naming it as deferred.

**Mitigation:** The acceptance criterion 6 (SME T6 scope-discipline sentence) and the explicit "open empirical question this corpus cannot answer" framing in the §4 specification are the guardrails. The acceptance criterion 7 (do not duplicate v2-prompt status doc content) caps the prose at "name and reference," not "elaborate."

### 6.4 The §8 binding-note carry-forward mapping is large and brittle

**Risk:** The §8 mapping enumerates ~40 binding notes (8 original + A1–A8 + B1–B15 + S1–S5 + R1–R6 + T1–T7). Any single mis-classification (e.g., "B12 is vacuous" when it should be "B12 carries forward") undermines the audit trail.

**Mitigation:** The mapping in this plan §2 §8 is taken verbatim from the parent SME verdict's Q7 ruling and proactive Check 7 spot-check. The Coder copies the mapping into the memo §8 with no editorial changes. The Reviewer cross-checks against the parent SME verdict. Any deviation is a Reviewer fail.

### 6.5 The memo file path uses the 2026-05-05 anchor date but commits 2026-05-06+

**Risk:** The memo's filename is `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md` (parent plan's binding path). The actual commit date is 2026-05-06 or later. A future reader doing `ls docs/status/ | sort` may be momentarily confused.

**Mitigation:** The §1 header states the actual memo commit date explicitly. The 2026-05-05 anchor in the filename is intentional (it aligns with the recovery campaign date and the parent T4-redo plan date) and is the binding path. The cost is a one-line reader-orientation note in §1; the benefit is a stable filename across the life of the memo.

---

## §7. Boundaries explicitly affirmed (RD-3-local)

- **The Architect writes plans, not code, not memos.** This RD-3 plan is a plan only.
- **CDA SME PASS or PASS-WITH-NOTES on this plan is mandatory** before Coder starts the RD-3 memo. Per CLAUDE.md §6 R13.
- **No new operator sign-off required.** Mark's parent §5 Q1–Q3 sign-off is already on master in the RD-1 + RD-2 commit chain.
- **No UI/UX agent gate** for this plan or for the memo (per parent SME Q4 ruling). The downstream methodology-page UI rendering gets its own UI/UX gate.
- **No `cdb_core/schemas.py` edits.** Pydantic v0.1.11 is unchanged.
- **No `DATA_DICTIONARY.md` edits.** No `cdb_core` schema motion.
- **No `data/raw/*.jsonl` edits.** Append-only is binding.
- **No `data/derived/*.jsonl` edits.** Including no edits to the RD-1 superseded artifact and no edits to the RD-2 hand-coded artifact. Both are read-only inputs to the memo.
- **No prompt-template change.** v1 prompts unchanged. The v2 prompt observation is referenced as a parked forward-carry, not actioned.
- **No `cdb_analyze` change.** Confabulation classification module from RD-2 is read-only for RD-3.
- **No `apps/dashboard/` change.** No frontend artifact, no component, no chart, no copy. The memo is `docs/status/` text.
- **No analytical computation.** Smith's S, Romney CCM, MDS, Procrustes, OCI all out of scope. Named in §5 as unblocked.
- **No new Note designation.** The confabulation finding is the replacement for Note K, not "Note L."
- **No reframe of any other Note.** The memo is local to Note K and the cap-exhaustion reframe.
- **No new collection campaign.** The 9-row cohort is the memo's evidence; no additional collection is implied or requested.
- **No retroactive verdict-file edits.** Per parent SME Q7 ruling: the §8 carry-forward mapping in the memo is sufficient; no R7-style appended clarifications to predecessor verdict files.
- **No bundling.** RD-3 is one Coder commit (with possible follow-on commit if SME content verdict requires notes-applied changes; same task line).
- **No forbidden vocabulary** in this plan, the memo, or any artifact produced by this work. The §1.5 framing is binding throughout.
- **The RD-3 memo IS the S5 artifact.** SME PASS on the memo's content satisfies S5 and unblocks any downstream methodology-page UI rendering (which still gets its own UI/UX gate).
- **This plan refines the parent T4-redo plan's RD-3 spec.** It does not contradict it. The parent plan + parent SME verdict remain canonical for the parent-level dispositions; this RD-3 plan is the canonical execution-level spec for the memo.

---

*End of RD-3 Architect Plan. This plan is gated by a fresh CDA SME PASS or PASS-WITH-NOTES per CLAUDE.md §6 R13. The memo's content is gated by a separate fresh CDA SME PASS at the deterministic file path `docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md`. The second SME pass is what fully satisfies S5 from the Task #16 verdict. Estimated total cost: $0. Estimated wall-clock for Coder + Reviewer + SME content review: 1–2 days.*
