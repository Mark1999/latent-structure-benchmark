# CDA SME Verdict — Phase 4a.1 T4 Redo Architect Plan (S5 gate)

**Filed:** 2026-05-05
**Reviewer:** CDA SME (Opus)
**Plan reviewed:** `/opt/lsb-agent/docs/status/2026-05-05-t4-redo-architect-plan.md`
**Slack channel:** `#lsb-cda-sme`
**Predecessor verdicts (still binding, in dependency order):**
- `docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md` (8 original Phase 4a.1 binding notes; especially Ruling 6 / coverage caveat)
- `docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md` (A1–A8)
- `docs/status/2026-04-23-phase4a1-t3b-detector-sme-verdict.md` (B1–B6, R6 detector role-change precedent in CLAUDE.md §9 pitfall 13)
- `docs/status/2026-04-30-phase4a1-amendment-2-cda-sme-verdict.md` (B7–B9)
- `docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md` (B10–B12)
- `docs/status/2026-04-30-phase4a1-amendment-3-cda-sme-verdict.md` (B13–B15)
- `docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md` (T4.2 output gate; identifies the falsified D20 cross-provider prediction)
- `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (S1–S5; this verdict answers S5)
- `docs/status/2026-05-05-phase4a-recovery-cda-sme-verdict.md` (R1–R6)

---

## VERDICT: PASS-WITH-NOTES

| Axis | Result |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | PASS |
| Axis 3 — Claims validity | PASS-WITH-NOTES |
| Axis 4 — Audience translation | PASS-WITH-NOTES |
| Register compliance | N/A (no Register 1/2/3 statistics computed by this plan; deferred per Q5) |
| Vocabulary compliance | PASS (with explicit guard on the "blind-spot" framing — see T1 below) |

The Coder is authorized to start RD-1 (annotation of superseded May 1 artifacts) immediately on this verdict, conditional on Mark's separate sign-off on §5 framing decisions Q1–Q3 per the plan. RD-2 scaffold is also authorized on this verdict, with one binding refinement to the schema enum (T2 below). RD-3 (the reframing memo) is conditionally authorized to be drafted on this verdict, but **the memo's content must come back to me for a fresh PASS** — the memo IS the canonical S5 artifact and the SME PASS on the memo's content is what satisfies S5. This verdict establishes the memo's required structure and language guardrails; it does not pre-emptively pass the memo's prose.

The plan is unusually well-structured. The Architect surfaced seven explicit operator/SME questions and bounded scope cleanly. The reframing — Note K's hypothesis is mechanically untestable from the recovered corpus, but the data shows a different methodologically interesting finding — is the right move under §1.5 and aligns with my own expectation in Task 16 §B. My PASS-WITH-NOTES is principally about: (a) the "blind-spot" framing risk the Architect themselves flagged in §4.2, (b) the schema enum naming in RD-2, (c) the precise structure of the memo's §3 disposition statement and §4 finding statement, and (d) one scope clarification on what kind of finding §4 is allowed to claim.

---

## Q1–Q7 explicit rulings

### Q1 — May 1 hand-coded artifact disposition

**Architect read:** MARK-AS-SUPERSEDED via sibling `.SUPERSEDED.md` annotation file. Append-only convention extends to `data/derived/`.

**SME ruling: CONFIRM.**

Reasoning:
1. **Audit-trail preservation is load-bearing.** The May 1 hand-coded artifact was produced under SME-PASSed methodology (T4.1 + T4.2 + Amendment 3) and the verdict files endorsing it are on master. Deleting the artifact would erase the *evidence* that the project once held the safety-event premise, which is methodologically significant on its own — the project's epistemic state evolved over time, and the audit trail of that evolution is itself a claim about the project's discipline. CLAUDE.md §9 pitfall 10's posture ("the bad record stays in place... and the audit trail remains intact") is the right precedent; it is conceptually identical, just on a `data/derived/` artifact rather than a `data/raw/` one.

2. **The verbatim text is not falsified.** The May 1 hand-code labeled the K-frame/K-vocab structure of the *narrative content*. The narrative content is real text the model produced; Mark's strict-reading judgment about whether each row's narrative names AI-vs-human framing as the trigger is a real judgment that survives the reframe. What changed is the *upstream* attribution: the narrative is now understood as a confabulation-shape narrative produced under blind-spot conditions, not a description of an actual safety event. Deletion would discard the strict-reading discipline alongside the falsified premise — an asymmetric loss.

3. **Sibling `.SUPERSEDED.md` annotation is the lowest-impact primitive.** It does not require a CI rule, a schema field, or a tooling change. Any reader encountering the JSONL file will see the sibling file in the same directory. A single `ls` in the directory exposes the supersede status.

4. **Append-only extension to `data/derived/` is conservative and right.** The original CLAUDE.md §9 pitfall 10 binding was scoped to `data/raw/` because that was the only append-only convention in scope at the time. The same epistemic argument — "preserve the audit trail rather than 'fix' bad records" — applies equally to `data/derived/` artifacts that have been SME-endorsed. The extension does not create new constraints anyone has to remember; it just generalizes the existing one. See proactive check 4 below for why I want this stated explicitly in the RD-3 memo.

I reject the three alternatives the Architect listed:
- **Delete:** loses the audit trail. Not acceptable.
- **Leave-with-warning (no annotation file):** relies on the verdict files alone for the supersede status. A future researcher reading the JSONL will not know the artifact was superseded without consulting the verdict-file index. Not acceptable.
- **Destructive-edit annotation in the JSONL's first row:** violates the append-only posture. Not acceptable.

**Mark may operator-override this ruling** in either direction (hard delete or no annotation), but my methodological recommendation is the supersede-with-sibling-file approach.

### Q2 — T4.2 cross-tab script disposition

**Architect read:** Docstring banner + sibling `.SUPERSEDED.md` file. Script preserved for code-reference value.

**SME ruling: CONFIRM, with one tightening.**

The disposition is right. The script's disposition arithmetic is correct (T4 SME verdict Axis 2 PASS); only the *premise the data carried into the script* was falsified. The script remains useful as: (a) a reference for the four-tier disposition tree should it be reused on Phase 4b data, (b) the audit trail for the May 1 work, (c) the test surface that already exists.

**Tightening (T3 below):** The docstring banner must be **two lines, not one.** Line 1: the supersede notice. Line 2: an explicit warning against re-running on the recovered corpus. The Architect's draft says "do not run for methodology"; that is correct but ambiguous about *which* methodology. The recovered corpus is a different population from the original 27-row corpus the script was written for; even if a future user re-points the script at the recovered corpus, the script's input contracts (4 input files, the safety_attribution_subtype artifact in particular) bind it to the original cohort. The banner must say so.

I reject the three alternatives the Architect listed:
- **Delete the script:** erases the audit trail of the May 1 reasoning chain.
- **Move to `scripts/archive/`:** the project does not have an `archive/` convention; introducing one for one file would be inconsistent with the existing tree, and it would break the existing test path that already runs against this script.
- **Leave un-annotated:** invites re-running.

The docstring banner is visible at code-reading time and is the right shape.

### Q3 — Note K disposition: REPLACED, RETIRED, or NOT CONFIRMED?

**Architect read:** REPLACED.

**SME ruling: CONFIRM REPLACED, with the structure I describe below.**

The four candidates are distinct dispositions and the framing matters.

- **NOT CONFIRMED** is wrong. The hypothesis was not tested and the answer was not "no." The data needed to test "CN-origin model decline clustering" no longer exists in a coherent form (the population collapsed from 29 to 9 with the recovery, and the 9 residuals do not cluster on origin in any meaningful way). NOT CONFIRMED would be a false claim about empirical evidence.

- **RETIRED** would be defensible if the data were silent. But the data is not silent — it shows a different methodologically interesting finding (the model's output narratives, when produced under blind-spot conditions, take a confabulation-shape form that itself characterizes the corpus lens). RETIRED would discard that finding.

- **REPLACED** is the right disposition. The Architect's reasoning is sound: the original hypothesis is mechanically untestable from this corpus, AND the data shows a different finding that subsumes the original Note K's purpose (characterizing how the corpus lens manifests under specific failure conditions).

- **REPLACED-WITH-NEW-NOTE-DESIGNATION** (e.g., the confabulation finding becomes "Note L" while Note K's history is preserved cleanly): this is also defensible. The Architect explicitly raised it in Q3. **My ruling here: USE REPLACED, NOT NEW-NOTE-L.**

Reasoning for REPLACED-without-new-designation:
1. The "Note" designations in this project are not a stable taxonomy with semantic load; they are sequential identifiers (Note A, B, C, ...) that the original Phase 4a.1 plan and amendments produced. Issuing a new "Note L" would create the impression that there is a new hypothesis under formal investigation, and would invite future plans to cross-reference "Note L" as if it had its own work-stream. The confabulation finding is *not* under formal investigation (per Q5: analytical artifacts are out of scope; per the plan: this is a re-disposition, not a new investigation). It would be misleading to give it a Note designation that implies it is.
2. REPLACED preserves the linkage: anyone reading "Note K is REPLACED in 2026-05-05" can trace forward to the memo and find the replacement finding in the same document. A "Note L" designation would force future readers to chase two trails to understand the same epistemic move.
3. If the confabulation finding *does* become a future investigation target (e.g., a Phase 4d analysis of confabulation patterns across providers and prompt types), at that point a new Note designation can be assigned cleanly. Pre-emptively assigning one now over-commits.

**Binding consequence for the memo:** RD-3 §3 must use the word **REPLACED** (not RETIRED, not NOT CONFIRMED, not "superseded" — the recovery report's R1 binding "replace as authoritative" applies to records, not to dispositions; using "superseded" for the disposition would conflict with the R1 vocabulary discipline). RD-3 §4's confabulation finding is reported as "the methodologically interesting observation that the data does support, in lieu of the original Note K hypothesis," not as "Note L" or "the confabulation finding."

### Q4 — UI/UX agent gate: required or not?

**Architect read:** NOT REQUIRED.

**SME ruling: CONFIRM NOT REQUIRED for this plan.**

Per CLAUDE.md §3 frontend-vs-non-frontend test: this plan touches `data/derived/` (RD-1, RD-2), `packages/cdb_analyze/` (RD-2), `scripts/` (RD-2 seed builder), `tests/` (RD-2), and `docs/status/` (RD-3 + the supersede annotations). It does NOT touch `apps/dashboard/`, `DESIGN_SYSTEM.md`, or any visual artifact.

The borderline case is RD-3's memo §3, which is *intended* to be quotable by the eventual UI/UX rendering. The Architect's read is right: text-on-disk in `docs/status/` is text-on-disk; the UI rendering is what makes it a UI/UX surface, and that rendering is a separate task with its own gate.

**However:** I want to be explicit about the contract going forward. The memo §3 is **methodology-page-bound text under SME PASS**, not UI-ready copy. When the eventual UI rendering happens (downstream Phase 5/6 task), the UI/UX agent has its full review surface — it may decide the §3 wording needs glossing for audience, needs a visualization companion, needs a different opening for journalist legibility, etc. None of that re-routes through me unless the gloss changes the *methodological claim* the §3 statement makes. The two-step gate structure (SME PASS on memo content; UI/UX PASS on rendering) is right and I confirm it.

### Q5 — Should this plan include the analytical artifacts (Smith's S, Romney CCM, MDS, Procrustes)?

**Architect read:** OUT OF SCOPE.

**SME ruling: CONFIRM OUT OF SCOPE.**

Three reasons:
1. **Distinct review surfaces.** Methodology re-disposition (this plan) and statistical computation on the recovered corpus are different kinds of work with different review concerns. Methodology re-disposition is mostly an Axis 3 / Axis 4 question; statistical computation is mostly an Axis 2 question. Bundling them would route a single SME verdict over both surfaces, which makes the verdict harder to read and harder to audit.

2. **The recovered corpus needs its own analytical scoping.** The recovered records are 20 cells across 3 models × 2 domains; combining them with the original-Phase-4a successful records produces a 60-cell corpus across 12 models × 2 domains. Smith's S, Romney CCM, MDS, and Procrustes all have pre-existing thresholds (SME_REVIEW.md §1.1 sets Romney 5.0 operational / 3.0 reported for n ≥ 12; the small-n caveat applies) that need to be re-evaluated in the post-recovery population shape. That re-evaluation is its own SME work item.

3. **The asymmetry between recovered and pre-Task-16 records on `thoughts_token_count`** is a forward-looking concern (see proactive check 2 below) that needs its own ruling at the analytical-computation gate, not pre-emptively at this plan's gate.

The RD-3 memo §5 names the analytical work as unblocked but does not produce it. That is the right shape. **I am explicitly NOT pre-disposing what the eventual T5 / Phase 4a closure plan should look like** — that's a future Architect plan that routes through me with full scope.

### Q6 — What is the canonical S5 artifact?

**Architect read:** The RD-3 memo IS the S5 artifact. SME PASS on the memo satisfies S5.

**SME ruling: CONFIRM, with the two-stage structure made explicit.**

S5 is satisfied by **both**:
1. **SME PASS on this plan** (the artifact you are reading right now) — establishes the memo's required structure, language guardrails, and disposition framing. This is necessary because S5 says "Note K re-classification under the new framing must route through CDA SME before any methodology-page text" — and the *plan* that decides what that text will say is itself a methodology-text decision. If the plan were not SME-gated, the memo's structure would be set without my review.
2. **SME PASS on the memo's content** — the actual text-on-disk that the methodology page will quote. This is what S5 binds in the strictest reading. The memo's prose, the §3 disposition statement, the §4 finding statement, the §8 carry-forward mapping all need to be reviewed as written, not just structurally pre-approved.

**This verdict is step 1.** It is a PASS-WITH-NOTES with binding notes T1–T7 below. The memo cannot inherit my pre-approval — the memo's prose is reviewed at step 2 when the Coder produces it.

The Architect's framing in §6 Q6 is right: this plan's PASS is a precondition for the memo's PASS, but does not pre-substitute for it.

**Operational binding for Coder:** When RD-3 lands, it routes to me as a fresh review (file path: `docs/status/2026-05-05-phase4a1-t4-redo-memo-cda-sme-verdict.md`, expected). The plan's gate-chain section already names this; I confirm it is mandatory.

### Q7 — Retroactive clarifications to prior binding notes

**Architect read:** B7–B9 vacuous, B11 REPLACED, B14 carries forward; binding notes 6 / A6 / B5 (the detector role-change precedent) carry forward unchanged. The §8 of the RD-3 memo is the carry-forward mapping; no R7-style retroactive clarifications appended to predecessor verdict files.

**SME ruling: CONFIRM, with two minor refinements (T6 below).**

I spot-checked all 31 binding notes against the new framing:

**Notes that carry forward unchanged** (the new framing does not change their methodological role):
- **Original Phase 4a.1 binding notes 1, 2, 3, 5, 7, 8** — these are about T1 enumeration discipline, Note J expected-rate baseline, T5 Note J cross-tab structure, audit-trail requirements, and other structural concerns that survive the reframe. All in force.
- **Binding note 4 (Note K thresholds)** — the count thresholds (≥5 CONFIRMED / 2–4 INCONCLUSIVE-SUGGESTIVE / 1 INCONCLUSIVE / 0 NOT CONFIRMED) survive *as a tree shape*, but the tree is no longer being applied to a Note K hypothesis. The thresholds remain available for any future hypothesis that needs them. Carry forward as latent.
- **Binding note 6 (recursive-decline two-tier rule)** — survives unchanged.
- **A1, A2, A3, A4, A5, A7, A8** — survive unchanged.
- **A6 (T3A pre-T3B gate)** — survives unchanged.
- **B1, B2, B3, B4, B6** — survive unchanged.
- **B5 (the detector role-change SME review at code-review time precedent — CLAUDE.md §9 pitfall 13)** — survives **and is reaffirmed** as binding for any future detector helper development. The new RD-2 schema is itself a manual hand-coding artifact, not a detector helper, so B5 doesn't directly apply to RD-2; but B5's general posture (any cross-boundary reuse of classification machinery routes through me at code-review time) is unchanged.
- **B10** (soft, future batches) — carries forward unchanged.
- **B12** (binding precedent, future batches) — carries forward unchanged.
- **B13** (soft, K-frame definition refinement at N≥10) — **vacuous under the new framing**: the K-frame/K-vocab dichotomy is not carried into the new schema (per the plan's RD-2 cross-walk note). B13 is preserved as a historical artifact but is not active.
- **B15** (soft, dashboard glossing) — carries forward unchanged.

**Notes the Architect plan correctly flags as REPLACED or VACUOUS:**
- **B7, B8, B9** (Amendment 2 disposition arithmetic notes) — vacuous under the new framing because the disposition arithmetic they govern is no longer being applied to Note K. The Architect is right.
- **B11 (the K-frame/K-vocab subtype binding)** — REPLACED by the RD-2 confabulation classification schema. The Architect is right; B11's enum is superseded.
- **B14 (T5 §8.1/§8.2 numerics-vs-interpretation separation)** — *carries forward and binds the eventual T5 redo*. The Architect's framing is right: the separation principle is general-purpose (interpretive content goes in §8.2, supporting numerics in §8.1) and survives the change in *what* is being interpreted. Confirmed.

**Notes affected by the T4 SME verdict (2026-04-30) Required #1–#4 items:**
- The T4 SME verdict identified Required #1 (Architect Amendment 4 to revise D20 cross-provider wording), which Amendment 4 then satisfied. Under the new framing, **D20's mechanism string is moot** — the disposition tier the script computes is no longer the methodology-page-bound disposition. Amendment 4's revised wording is preserved as audit but no longer binds methodology-page text. The Required #2/#3/#4 items (script revision, defensive guardrail, T5 §8.2 wording) are similarly moot.

**Refinements (T6 below):** I want two specific items addressed in the RD-3 memo §8 carry-forward mapping that the Architect's draft does not yet explicitly call out:
1. **A6 (T3A pre-T3B gate)** — survives unchanged but should be explicitly named in §8 to confirm that the T3A pre-T3B sequencing posture (decline-interview detection precedes any subtype refinement) is not affected by the reframe.
2. **R6 (recovery rate <80% threshold)** — the recovery rate was 100% (well above 80%), so R6 was not triggered. The §8 should explicitly note that R6 was satisfied; otherwise a reader of the §8 may wonder whether R6 lurking forced a different disposition.

**No R7-style retroactive verdict-file edits required.** The Architect's read is right: appending retroactive clarifications to the original Phase 4a.1 verdict and Amendment 1 verdict (the way R7 was appended to those files for the detector miscalibration) would inflate the audit trail without adding clarity. The §8 carry-forward mapping in the RD-3 memo is sufficient. The verdict files stand as historical record.

---

## Proactive checks

### Check 1 — "Blind-spot" framing under §1.5.4 forbidden vocabulary

The Architect themselves flagged this in §4.2 of the plan, and the mitigation they proposed ("the actual mechanical cause was not surfaced in the information available to the model at decline-interview time") is correct. I want to extend the discipline.

**Phrasings that ARE clean under §1.5.4** (the model is not the subject of a cognition claim):
- "the actual mechanical cause was not surfaced in the information available to the model at decline-interview time"
- "the model received the empty-output text + the prompt asking it to describe what happened; it did not receive the API-level diagnostic that would have shown the cap exhaustion"
- "the response is consistent with post-hoc attribution under conditions where the originating mechanical cause was not observable from the inputs the model had"
- "the model's output narrative attributes the failure to safety mechanisms; the actual cause was mechanical"

**Phrasings that are NOT clean** and the Reviewer must reject:
- "the model could not see the actual cause" — "could not see" implies perceptual capacity with limits. Replace with "the actual cause was not surfaced in the model's inputs."
- "the model was blind to the cap exhaustion" — same problem. Replace with "the cap exhaustion was not observable from the model's inputs at the decline-interview step."
- "the model didn't know it had hit the cap" — "didn't know" is a cognition claim. Replace with "the cap-exhaustion event was not part of the prompt context provided at the decline-interview step."
- Any framing that uses "blind spot" as a noun applied to the model's perception. **The phrase "blind-spot conditions" is borderline.** It is descriptive of the *information environment* (the model's inputs lacked the cap-exhaustion diagnostic), not of the model's perception. I will accept "blind-spot conditions" *only if* the surrounding text makes this disambiguation explicit on first use. The RD-3 memo §2 must define "blind-spot conditions" on first use as "conditions in which the originating mechanical cause was not surfaced in the inputs available to the model at decline-interview time." Subsequent uses can use the shorthand.

This is binding (T1 below).

### Check 2 — Cross-corpus comparability (asymmetric `thoughts_token_count`)

The recovered records have `thoughts_token_count` populated where the provider exposes them; the original Phase 4a corpus has those values as `0` (because the field didn't exist at write time). This asymmetry does not bias the T4-redo *methodology re-disposition* work (the memo doesn't compute statistics). It is forward-looking: when the analytical computation work happens (the T5 redo / Phase 4a closure plan that this memo names as unblocked), any analytical step that consumes `thoughts_token_count` must address the asymmetry.

The Task 16 SME verdict S2 already requires the dictionary to disambiguate the four epistemic states `0` represents:
1. The model produced no reasoning tokens.
2. The provider does not surface reasoning tokens.
3. A non-reasoning model on a reasoning-capable provider.
4. Legacy record from a pre-field era.

For T5/Phase 4a closure analytical work, **state (4) is the relevant case for original-Phase-4a successful records.** The eventual T5/closure plan must address whether any analytical step intends to filter records on `thoughts_token_count`-based criteria, and if so, how the legacy population is handled. This is a future-task concern; not blocking this plan. I'm flagging it for the eventual T5/closure SME review.

The plan's RD-3 memo §5 ("what the recovered corpus enables and doesn't") should include a one-sentence note that downstream analytical work will need to address the legacy `thoughts_token_count=0` records explicitly. This is T4 below.

### Check 3 — RD-2 hand-coding scope under the new framing

The Architect's RD-2 schema (4 confabulation labels + `not_confabulation` sentinel + `under_blind_spot` Boolean) is structurally well-formed. I have one **substantive concern** on the enum naming and one on the `not_confabulation` value:

**Concern 1 — the `safety_filter_confabulation` label shares a stem with the May 1 `safety_event_attribution` label, which could re-import the falsified premise.** The new label *correctly* names the *shape* of the narrative (the model attributes failure to safety mechanisms) without claiming there was a safety event. But for a methodology-page reader, the word "safety" carries the original framing's freight. I want the label renamed.

**My proposed rename: `safety_attribution_confabulation`.** This preserves the descriptive "the narrative attributes failure to safety mechanisms" semantic without the bare word "filter" (which carries the operational connotation that there *was* a filter). The other three primary labels can keep their forms — `task_paradox_confabulation` and `topic_sensitivity_confabulation` are descriptive of the narrative shape and don't carry a prior-framing freight. `mixed_attribution` is fine.

This is binding (T2 below).

**Concern 2 — the `not_confabulation` sentinel value.** The Architect's draft definition: "narrative correctly identifies the failure cause (e.g., 'technical glitch,' 'mechanical error'), or genuinely doesn't claim to know. These rows are NOT confabulation under the new framing." This is methodologically the right escape hatch — but on a 9-row cohort where the originating events are *all* cap-exhaustion (per `under_blind_spot=true`), a `not_confabulation` row would be one where the model *correctly* identifies the technical cause. That would be a methodologically interesting finding (the model has, at decline-interview time, enough information to reason its way to a mechanical cause) and would itself partially falsify the "blind-spot" framing for that row.

**My ruling: keep the sentinel.** The schema must allow for `not_confabulation` so Mark can apply it if a row's narrative actually does correctly identify the technical cause. If any row classifies as `not_confabulation`, the RD-3 memo §4 must explicitly discuss it (it complicates the blind-spot framing for that row, and that complication is itself a finding). This is T5 below — a binding requirement on the memo *if and only if* Mark's hand-code produces a `not_confabulation` row.

**No further enum refinements.** The four primary enum values (after the T2 rename) are sound. I anticipate Mark may find that some rows fit the May-1 K-frame discriminator cleanly and translate to `task_paradox_confabulation`; some fit K-vocab cleanly and translate to `topic_sensitivity_confabulation` or `safety_attribution_confabulation`; some are mixed. That is the spectrum the schema is designed for.

The 200-char rationale limit, the `under_blind_spot` Boolean, and the parent-id join requirement are all the right shape (parallel to the May 1 schema's design). PASS on those.

### Check 4 — `data/derived/` append-only convention extension

The Architect proposes extending the append-only convention from `data/raw/` to `data/derived/`. CLAUDE.md §9 pitfall 10 binds `data/raw/` only.

**My ruling: APPROVE the extension as a process discipline, not as a new pitfall-13.** Reasoning:
1. The methodological argument (preserve audit trail rather than 'fix' bad records) applies symmetrically to `data/raw/` and `data/derived/` — derived artifacts are also primary audit-trail evidence of the project's epistemic state at the time they were produced.
2. The extension is conservative — it does not introduce new constraints anyone has to remember; it just generalizes the existing one.
3. **However**, I do *not* want this codified as a CLAUDE.md §9 pitfall 14 at this time. The `data/derived/` artifacts vary in their epistemic status — some are mechanical computations from `data/raw/` (regenerable), some are human hand-coded artifacts (irreproducible). The pitfall-10 binding is sharp because `data/raw/` is unambiguously primary; `data/derived/` is structurally more nuanced. A blanket pitfall would be too strong.

**Operational disposition:** RD-1's sibling `.SUPERSEDED.md` annotation pattern is the right primitive, applied case-by-case. The RD-3 memo §7 audit trail should describe the supersede pattern (sibling `.SUPERSEDED.md` files) as the project's convention going forward, but should NOT claim it is binding by CLAUDE.md §9 pitfall language. The convention is operational; the binding is verdict-by-verdict.

This is T7 below — a memo §7 phrasing requirement.

### Check 5 — Forbidden vocabulary skim

I checked the plan in full for §1.5.4 / CLAUDE.md §7 violations:
- No `worldview` / `believes` / `thinks` applied to models.
- No "publishable" framing.
- No "closer to human is better."
- No "within-model consensus" / "within-model CCM."
- The "blind-spot conditions" framing is borderline and addressed in T1.

The plan as written is PASS on vocabulary compliance, with the caveat that the *memo* (RD-3 deliverable) has not yet been written and the §1.5-clean discipline must be applied throughout when it is. The Reviewer's spot-check on the memo commit catches this; my second SME PASS on the memo content catches this; T1 below makes the discipline explicit.

### Check 6 — The replacement finding's methodological status

The Architect's §4.6 risk identifies that the confabulation finding is *novel* — it was not previously a binding note, it does not have a Note designation, and it was not gate-reviewed before this plan.

**My ruling: the confabulation finding is methodologically defensible at the level the RD-3 memo §4 will state it.**

The level the memo §4 should state it at is:
- **Descriptive observation** — the 9 originally-Gemini decline-interview narratives, when produced under conditions where the originating mechanical cause was not surfaced in the model's inputs, take a confabulation-shape form (the narrative attributes the failure to a mechanism — safety, paradox, topic sensitivity — that is consistent with categorical knowledge from the model's training corpus but does not match the actual mechanical cause).
- **Distribution claim** — the 9 narratives distribute across the RD-2 enum in a pattern Mark hand-codes; the distribution itself is reportable as a summary statistic.
- **Generalization claim — NOT YET PERMITTED.** The memo §4 must not claim that this confabulation pattern generalizes to (a) other providers, (b) other models, (c) other failure modes, or (d) other prompt types. The 9 rows are all from one provider (Gemini), one cohort (cap-exhaustion failures recovered on 2026-05-05), and two domains. Any cross-provider or cross-failure-mode claim is unsupported by the data and would require new evidence.

This is T6 below — a binding scope for the memo §4. The Architect's draft prose at §3 is consistent with this discipline; the §4 prose has not yet been written; the binding is on the eventual §4 draft.

The "is it methodologically interesting enough to publish?" question the Architect raises in §4.6 is a different question — and one I am answering YES to *at the bounded scope above*. A descriptive observation about the shape of decline-interview narratives produced under known mechanical conditions is methodologically interesting because it illustrates a property of the corpus lens (the model's narrative output draws on training-corpus categories of explanation when faced with self-attribution under uncertainty). It is a small finding, but it is real, and reporting it is honest about what the data shows.

I am NOT pre-disposing whether this finding ever gets dashboard treatment. That's a Phase 5/6 UI/UX-gated decision. The memo §4 is methodology-page-bound text; the dashboard rendering is a separate question.

### Check 7 — The 24 decline-interview records under the new framing

The plan correctly preserves the 24 T3B decline-interview records verbatim (RD-1 leaves `data/raw/decline_interviews.jsonl` untouched). Their **role** in the analysis layer is reinterpreted: from "the corpus for studying safety events" to "the corpus for studying confabulation patterns under blind-spot conditions for the 9 originally-Gemini cap-exhaustion rows; the other 15 rows remain in their original epistemic role."

**One clarification I want explicit in the memo:** of the 24 decline-interview records, only 9 are reframed by this memo (the originally-Gemini safety-event-attribution rows whose originating events were cap-exhaustion). The other 15 records are **unaffected by the reframe**:
- 3 z-ai/glm-5.1 family-domain rows are `substantive_compliance_with_empty_input` (the empty-freelist propagation bug per Mark's session memory) — the underlying mechanism was an upstream pile-sort empty-list bug, not a cap-exhaustion event.
- The remaining 12 records are technical-glitch / refusal / out-of-scope / other classifications whose upstream mechanical causes are not cap-exhaustion.

The RD-3 memo §2 ("what changed") must make this scoping explicit: the reframe applies to the 9 originally-Gemini rows whose `under_blind_spot=true`, NOT to all 24 records. This is T4 (extended). Without this, a reader could mistakenly conclude that the entire decline-interview corpus is now reinterpreted, which would over-claim.

---

## Binding notes (T-series, fresh — not conflicting with prior 31 + R1–R7 + S1–S5 + R1–R6)

Numbered T1–T7 to keep the per-task series local to T4-redo work, parallel to the R-series (Phase 4a recovery) and S-series (Task 16). Total binding-note inventory is now: 8 original + A1–A8 + B1–B15 = 31 (Phase 4a.1) + S1–S5 (Task 16) + R1–R6 (Phase 4a recovery) + T1–T7 (T4 redo) = **49 active binding notes** project-wide. Of these, B7, B8, B9, B11, B13 are now vacuous or REPLACED per Q7. Active count ≈ 44.

**T1. The "blind-spot" framing must be defined on first use in the memo.**

The RD-3 memo §2 must define "blind-spot conditions" on first use as: *"conditions in which the originating mechanical cause of a failure was not surfaced in the inputs available to the model at decline-interview time."* Subsequent uses can use the shorthand. The phrases "the model could not see the cause," "the model was blind to," "the model didn't know," and any other phrasing that implies cognition or perception are forbidden in this memo. The §1.5-clean alternatives in proactive check 1 above are the binding substitutes. The Reviewer enforces; my second SME PASS on the memo content double-checks.

**T2. Rename the RD-2 enum value `safety_filter_confabulation` to `safety_attribution_confabulation`.**

The word "filter" carries an operational connotation (there *was* a filter that fired) that re-imports the falsified premise. "Attribution" is descriptive of the narrative shape ("the narrative attributes the failure to safety mechanisms") without claiming the safety mechanism actually fired. The other three enum values (`task_paradox_confabulation`, `topic_sensitivity_confabulation`, `mixed_attribution`) keep their names. The `not_confabulation` sentinel value also keeps its name.

The Coder applies this rename in the RD-2 schema, the seed builder, the loader, the tests, and the RD-3 memo's §4 descriptions. No other downstream consumers exist.

**T3. The script docstring banner on `phase4a1_note_j_crosstab.py` must be two lines, not one.**

Line 1: the supersede notice with date and cross-reference (per the Architect's draft).
Line 2: an explicit warning that the script's input contracts (the 4 input files including the safety_attribution_subtype artifact) bind it to the original 27-row cohort, NOT to the recovered corpus, and that the script must not be re-run on any modified input set.

**T4. The memo §2 ("what changed") must scope the reframe to the 9 originally-Gemini rows only.**

The reframe affects the 9 originally-Gemini rows whose `under_blind_spot=true`. The other 15 records in `decline_interviews.jsonl` are unaffected (3 are empty-freelist-propagation rows; 12 are other classifications with non-cap-exhaustion upstream mechanical causes). The §2 must make this scoping explicit; without it, a reader could over-generalize. The §5 ("what the recovered corpus enables") must include a one-sentence note that downstream analytical work consuming `thoughts_token_count` will need to address the legacy `thoughts_token_count=0` records explicitly per Task 16 SME S2.

**T5. The memo §4 must explicitly discuss any `not_confabulation` rows if they exist.**

If Mark's hand-code produces any row classified as `not_confabulation`, the memo §4 must discuss it explicitly: a row where the model correctly identifies the technical cause complicates the "blind-spot" framing for that row (the model had, at decline-interview time, enough information to reason its way to a mechanical attribution). That complication is itself a methodologically interesting finding. If no row classifies as `not_confabulation`, the memo §4 may state that the schema's escape hatch was not triggered and move on.

**T6. The memo §4 must report the confabulation finding at the bounded scope: descriptive observation + distribution claim ONLY. No generalization claims.**

Permitted §4 claims:
- The 9 originally-Gemini decline-interview narratives, produced under blind-spot conditions, take a confabulation-shape form.
- The narratives distribute across the RD-2 enum in pattern X (per Mark's hand-code).
- This pattern illustrates a property of the corpus lens: when faced with self-attribution under uncertainty, the model's narrative output draws on training-corpus categories of explanation (safety mechanisms, task paradoxes, topic sensitivity) consistent with categorical knowledge from training.

Forbidden §4 claims:
- That the confabulation pattern generalizes to other providers, other models, other failure modes, or other prompt types.
- That the confabulation finding constitutes evidence about the model's "actual" reasoning behavior, internal state, or perceptual capacity.
- That the confabulation finding is "publishable" in any sense beyond appearance on the methodology page.
- That the confabulation finding is "Note L" or has any other Note designation. It is the replacement for Note K, but it does not inherit a designation.

The §4 prose must explicitly note: "this is a single-provider, two-domain finding from a 9-row cohort; cross-provider or cross-failure-mode generalization requires new evidence."

**T7. The memo §8 carry-forward mapping must explicitly include A6 and R6.**

Per Q7 refinements:
- **A6 (T3A pre-T3B gate)**: include in §8 as carrying forward unchanged. The decline-interview detection sequencing is not affected by the reframe.
- **R6 (recovery rate <80% threshold)**: include in §8 as satisfied (recovery rate was 100%; threshold not triggered; binding consumed).

Additionally, the §8 must explicitly note that the supersede convention (sibling `.SUPERSEDED.md` files) is the project's *operational* practice for marking superseded `data/derived/` artifacts and is NOT codified as a CLAUDE.md §9 pitfall. The convention is verdict-by-verdict, not blanket-binding.

---

## What I am explicitly NOT ruling on

- **The eventual T5 / Phase 4a closure analytical work.** The recovered corpus enables Smith's S, Romney CCM, MDS, Procrustes, OCI on the corrected corpus. None of those are in scope for this plan. When the Architect plans them, the plan routes through me with a fresh SME pass. The asymmetric-`thoughts_token_count` concern (proactive check 2) applies to that future plan.
- **The phi-4 ×6, gpt-5.4-mini ×2, mistral-small ×1 unexplained failures.** Per the recovery report's "forward carry" section, these are separate Architect tasks. Their root causes are not cap-exhaustion; the cap fix did not address them; their disposition is open.
- **Dashboard rendering of the methodology page.** Phase 5/6 UI/UX-gated work. The memo §3 disposition statement and the §4 finding statement are quotable by the eventual UI rendering, but the rendering is a separate task.
- **Any retroactive verdict-file edits.** Per Q7: not required. The §8 carry-forward mapping in the memo is sufficient.
- **Whether the confabulation finding ever gets dashboard treatment.** Out of scope; future UI/UX-gated decision.

---

## Carry-forward note

S5 (from Task 16 SME verdict, 2026-05-04) is **partially consumed** by this verdict. Step 1 (SME PASS on the plan that gates the methodology-page text) is satisfied. Step 2 (SME PASS on the memo's content itself) remains open and is the gate the Coder must clear after producing RD-3. S5 is NOT yet fully satisfied.

R1–R6 (Phase 4a recovery) remain as they were — local to the recovery operation, not consumed or extended by this T4-redo work.

S1–S4 (Task 16) remain as they were — local to the Task 16 max_tokens / thoughts_token_count scope.

The T-series (T1–T7) introduced here are local to the T4-redo scope. T1 (vocabulary discipline on "blind-spot" framing) and T6 (memo §4 scope discipline) are the most load-bearing — they are the ones that protect the §1.5 framing of the methodology-page-bound text. T2 (enum rename) is mechanically straightforward but methodologically important. T3 (script docstring banner) is a small but real disambiguation. T4, T5, T7 are memo-content disciplines.

Phase 4a.1 binding-note count after this verdict:
- 31 Phase 4a.1 notes (8 original + A1–A8 + B1–B15) — of which B7, B8, B9, B11, B13 are now vacuous or REPLACED per Q7
- S1–S5 (Task 16); S5 partially consumed
- R1–R6 (Phase 4a recovery); not consumed
- T1–T7 (this verdict; new)

**Active binding notes after this verdict: ≈44.**

---

## Gate disposition

**RD-1 (annotation of superseded May 1 artifacts):** **AUTHORIZED** to start immediately on this verdict + Mark's separate sign-off on §5 framing decisions Q1–Q3. Coder applies T3 (two-line docstring banner). Reviewer + Tester gates per the standard pipeline. No further SME re-review on RD-1 unless Reviewer surfaces a deviation.

**RD-2 scaffold (confabulation classification module + tests):** **AUTHORIZED** to start after RD-1 lands. Coder applies T2 (enum rename `safety_filter_confabulation` → `safety_attribution_confabulation`). The Architect's "optional CDA SME spot-check on Mark's hand-coded artifact" is **non-blocking** by my default; I take the slot if I see the artifact and have a methodological concern on the distribution. If I do not surface a concern, the hand-coded artifact carries forward without explicit SME PASS (same posture as the May 1 hand-code).

**RD-3 (T4-redo reframing memo):** **CONDITIONALLY AUTHORIZED to be drafted** after RD-2 hand-code lands. Coder applies T1, T4, T5, T6, T7 throughout. **The memo's content must come back to me for a fresh SME PASS** at file path `docs/status/2026-05-05-phase4a1-t4-redo-memo-cda-sme-verdict.md`. That second PASS is what satisfies S5 in full.

**Anything else gated on a separate SME pass:**
- The RD-3 memo content (S5 step 2; mandatory).
- Any future T5 / Phase 4a closure analytical work (separate Architect plan; full review surface).
- Any future dashboard UI rendering of the memo's methodology-page-bound text (separate UI/UX gate; UI/UX agent reviews; SME re-review only if the gloss changes the methodological claim).

**No UI/UX gate** on this plan or its three Coder tasks (per Q4).

**Mark's sign-off on §5 framing decisions Q1, Q2, Q3** is mandatory before Coder starts RD-1, per the plan's own gate chain. I confirm those three are operator-level decisions where I have input but Mark has final say.

---

## Sign-off

The Architect's plan is methodologically sound. The reframe is the right epistemic move under §1.5. The seven explicit Q1–Q7 questions are all answered above; my rulings are mostly confirmations with the binding refinements T1–T7. The most load-bearing are T1 (blind-spot framing discipline), T2 (enum rename), and T6 (memo §4 scope discipline) — together they protect the §1.5 framing of the methodology-page-bound text.

The two-step S5 gate structure (PASS on this plan now; PASS on the memo content later) is the right shape and is explicit in the plan. I am partially consuming S5 here; the full consumption happens at the memo-content gate.

The plan is PASS-WITH-NOTES. Coder may start RD-1 on this verdict + Mark's §5 sign-off. RD-2 follows after RD-1. RD-3 follows after RD-2 hand-code, and routes back to me for the S5-completing SME PASS.

*Posted to `#lsb-cda-sme`. Binding for RD-1 (T3), RD-2 (T2), RD-3 (T1, T4, T5, T6, T7), and the memo-content S5 gate. Mark's sign-off on §5 Q1–Q3 is the operator-level precondition. The CDA SME thanks the Architect for the unusually clean structure of this plan and for proactively surfacing the "blind-spot" framing risk in §4.2 — that flag was the right discipline and made T1 a refinement rather than a correction.*
