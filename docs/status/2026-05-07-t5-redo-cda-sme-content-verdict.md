# CDA SME Content Verdict — Phase 4a T5 Redo (RD-T5-4: §8–§10 + Completion-Redo)

**Filed:** 2026-05-07
**Reviewer:** CDA SME (Opus)
**Artifacts reviewed:**
- `docs/status/2026-05-07-phase4a-t5-redo-analysis-report.md` (final state, §1–§10; §8–§10 added at commit `3fc70be`)
- `docs/status/2026-05-06-phase4a-completion-redo.md` (new file at commit `3fc70be`)
**Slack channel:** `#lsb-cda-sme`

**Pipeline state confirmed:**
- T5 redo Architect plan: `docs/status/2026-05-06-t5-redo-architect-plan.md` (commit `2a4c6c2`)
- SME plan-pass verdict: `docs/status/2026-05-06-t5-redo-cda-sme-plan-verdict.md` (commit `86ad713`; T11–T15 binding)
- RD-T5-1 (build_db rerun, R5 discharged): commit `fda4ed7`; Reviewer `1637110`; Tester `10ddf3a`
- RD-T5-2 (pipeline 0.2 JSON): commit `63b0f9a`; Reviewer `d5d266b`; Tester `ffc3ceb`
- RD-T5-3 (numerics report §1–§7): commit `5128e94`; Reviewer `dadccb4`; Tester `d7ca68e`
- RD-T5-4 (interpretation §8–§10 + completion-redo): commit `3fc70be`; Reviewer `b021120`; Tester `455ab96`

**Predecessor verdicts (binding):**
- `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md` (T6 scope discipline; B6 / B12 / B14 carry-forward)
- `docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md` (S5-completing PASS-WITH-NOTES; T1–T10 SATISFIED with gate postures preserved; Q2 paraphrase-only ruling)
- `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (S2 four-state taxonomy)
- `docs/status/2026-05-06-t5-redo-cda-sme-plan-verdict.md` (T11 §7 framing guard; T12 §8.4 four-state; T13 §6 grep; T14 (e) "no publishable"; T15 Note G verbatim)

**Gate status of this verdict:** Closing gate for the T5 redo (gate chain step 3 per the T5 redo plan §2). PASS or PASS-WITH-NOTES closes Phase 4a at the analytical layer. FAIL routes back to the Architect for re-plan.

---

## VERDICT: PASS-WITH-NOTES

| Axis | Result |
|---|---|
| Axis 1 — Protocol validity | PASS (N/A in the strict sense — methodology-text deliverable; no protocol motion) |
| Axis 2 — Analytical validity | PASS (numerics walk-through carried at RD-T5-3 content; §8 references §4–§7 cleanly; no new numerics introduced) |
| Axis 3 — Claims validity | PASS-WITH-NOTES |
| Axis 4 — Audience translation | PASS-WITH-NOTES |
| Register compliance | PASS (Register 2 only; Register 1 within-model fields populated as per existing pipeline; OCI is reported as a within-model concentration descriptor, not as consensus) |
| Vocabulary compliance | PASS |

The §8 prose is methodologically sound and methodology-page-bound under the §1.5 framing. The §1–§7 / §8–§10 separation honors B14 cleanly: I verified that §8 introduces no new numerics — every numeric value in §8 is traceable to §4–§7 with section-citation precision. T11–T15 are all satisfied. B6 (a)–(e) are all satisfied. The Note K disposition is correctly REPLACED throughout, and Note E is correctly carried forward without the CN-origin augmentation per Q6(a). The completion-redo report mirrors the 2026-04-23 completion report's structure with the post-recovery numerics and the required "What this report does not claim" section.

PASS-WITH-NOTES rather than PASS for one specific reason: **the §8.4 enumeration of the four S2 epistemic states reads State 3 ("a non-reasoning model on a reasoning-capable provider") as a discrete state without flagging that it is, taxonomically, a sub-case of State 1 ("the model produced no reasoning tokens").** This preservation of the partial overlap is correct and intended (the T12 plan-pass verdict reproduced the S2 four-state list verbatim and the Reviewer correctly preserved it), but a reader of §8.4 standing alone may wonder whether State 3 is operationally distinguishable from State 1 from the field value alone. The §8.4 text is methodologically defensible as written, but a single clarifying clause would land the audience-translation axis cleanly. This is the only required pre-merge edit and is named as Required Item 1 below; it is a single-sentence inline addition.

The two other Reviewer-punted items (filename date prefix; §8.3 CI-overlap descriptive framing) are explicitly ruled below as **not requiring rewording** — both meet the methodology-page-bound bar.

---

## §8 sub-section walk-through

### §8.1 Family domain — PASS

The §8.1 prose meets the methodology-page-bound bar. Pitched at a skeptical-but-non-specialist audience: the four observation bullets are descriptive shape claims with explicit caveats. Third-person voice throughout. No first-person-project drift. The B6 discipline is preserved: every numeric statement is hedged with the small-n caveat (lines 491–495), the bootstrap CI is cited inline at every consensus claim, the OCI bullet (lines 519–522) explicitly anchors at "within-model descriptive properties... they do not constitute claims about model capability or model-internal reasoning."

The "Smith's S consensus score is 0.7107 (bootstrap CI [0.5049, 0.9092]; §4.1 and §5.1)" form is the correct R11 surface: point estimate paired with the §4–§5 reference. No bare point estimate without uncertainty.

The "all positive centrality — no subcultural or contested structure is detected" framing is correct under §1.5: it reports a measurement-output property (`negative_centrality_flag=False`) without ascribing a categorical-reasoning property to any model.

The closing paragraph correctly reports `g1_overall_pass = None` as the legitimate Phase 4a state with the Phase 4b cross-reference, and reports `groundings = []` as a complete first-class state per `ARCHITECTURE.md` §1.5.5. **PASS.**

### §8.2 Holidays domain — PASS

Same disciplines as §8.1. The treatment of `mistralai/mistral-small-2603` OCI=0.00 (lines 556–560) is methodologically careful: "n_runs=1 — only one QA-passed run, so OCI is trivially 0... not a meaningful within-model consistency estimate. This is a cell-coverage descriptor, not a claim about the model." This is exactly the right framing — the field's value is reported with the explicit acknowledgment that it carries no analytical signal, preventing a methodology-page reader from over-reading the zero.

The bootstrap CI lower-bound of 0.47 falling below 0.5 (line 540) is acknowledged as wide-CI behavior under small-n, not as a contradiction of the STRONG_CONSENSUS classification. The hedge is correct.

The peripheral-position MDS observation for `mistral-small-2603` and `gpt-5.4-mini` (lines 549–554) reports MDS coordinates as "model-to-model distances" without grounding implications, which is the right shape under Note D. **PASS.**

### §8.3 Cross-domain comparison — PASS

This is the most claim-sensitive subsection. The two domain comparisons are bounded carefully:

The "holidays consensus score is higher (0.78 vs 0.71 family)" bullet (lines 573–577) reports the difference, then immediately states "the CI overlap means this difference is not distinguishable from bootstrap noise under n=9 and n=11 respectively." The disposition disclaimer ("the observation is a descriptive property of the post-recovery corpus; it does not constitute a comparative claim about how models organize holiday vocabulary versus family vocabulary") closes the audience-translation surface cleanly.

The "Romney eigenratio is higher for family (12.10 vs 10.15 holidays)" bullet (lines 579–582) acknowledges the inverted ordering and cites the SME_REVIEW.md §1.1 known property of the two-measure structure. Population-size caveat is preserved.

The "centrality ranges are similar in shape" bullet (lines 584–586) reports a structural similarity without ascribing it any cross-domain interpretation.

The "n_models differs across domains" bullet (lines 588–590) maintains the small-n caveat on both sides.

The closing paragraph (lines 592–594) explicitly disclaims any baseline-grounded comparison and points to Phase 4c as the anticipated mechanism.

**Note D, Note E (without CN-origin), small-n caveat, and B6 (b)/(c)/(d) all hold throughout.** The §8.3 surface is the strongest test of the public-copy guardrails because it admits a descriptive cross-domain numeric ordering, and the prose handles the framing without overclaiming.

On the Reviewer-punted item about the CI-overlap descriptive framing rather than a formal hypothesis test — see Punted Item Disposition (3) below; my ruling is **accept as descriptive (no hypothesis-test reframing required)**. **PASS.**

### §8.4 `thoughts_token_count=0` epistemic states — PASS-WITH-NOTES

T12 requires §8.4 to enumerate all four S2 epistemic states. The Coder used approach (a) — explicit enumeration — and the four-state list in lines 610–617 matches the T12 plan-pass verdict text verbatim. S2 is also cited by file path (`docs/status/2026-05-04-task-16-cda-sme-verdict.md`, Q2/S2). Both T12 (a) and (b) options are exercised.

The pipeline-no-consume framing (lines 598–604; "the analytical pipeline at `packages/cdb_analyze/cdb_analyze/pipeline.py` does not reference `thoughts_token_count` as an analytical input") is correct and is reaffirmed by my own Q2 verification at the plan-pass verdict (zero references in `pipeline.py`; the only file in `packages/cdb_analyze/` that references the field is `confabulation_classification.py`, which is a different code path).

The mapping-to-states paragraph (lines 619–623; "State (4) applies to all original Phase 4a successful records... States (1), (2), or (3) apply to the recovered records, depending on the provider") is the right disambiguation for a methodology-page reader.

The §8.4 closing paragraph (lines 625–627) restates the "no bias" claim with the legitimate justification: because the pipeline does not consume the field, legacy state-(4) records co-exist in the analytical input without bias.

**One refinement required (Required Item 1 below).** State 3 ("a non-reasoning model on a reasoning-capable provider") is, taxonomically, a sub-case of State 1 ("the model produced no reasoning tokens"). The S2 four-state list preserves this partial overlap because the *provider-side surfacing* of the field changes the disambiguation surface even when the underlying model behavior is the same — a non-reasoning model on a reasoning-capable provider produces `0` *and* the provider does report the field. This is the case S2 carved out as State 3 to make explicit. The §8.4 text as written reads the four states as parallel discrete cases, and a methodology-page reader without the S2 verdict in front of them may not see why State 3 is separately listed.

This is the only required pre-merge edit.

### §8.5 Scope discipline — PASS

§8.5 carries the full B6 (a)–(e) compliance surface as an explicit list:
- **Single-provider observation for the recovered cells** (lines 633–638) — Q6(c) cross-provider/cross-failure-mode/cross-prompt-type generalization disclaimer; explicitly references parent T4-redo SME T6.
- **Small-n caveat** (lines 640–644) — Note A discipline.
- **No ceiling or proximity-to-baseline claims** (lines 646–648) — Note D discipline.
- **Population shift, not methodological correction** (lines 650–655) — Q6(b) "no incorrect framing of predecessor T5"; explicitly cites the RD-3 reframing memo.
- **v1 prompt conditions throughout** (lines 657–660) — Q6(c) cross-prompt-type discipline; v2 prompt suggestion document referenced as Phase 5+ candidate.
- **Methodology-page framing only** (lines 662–665) — T14 / Q6(e) "no publishable framing"; explicitly cites CLAUDE.md §1's "credibility to a skeptical reader" bar.

The list is a clean, structured enumeration. Each scope constraint binds a specific class of overclaim. **PASS.**

---

## §9 carry-forward verification

| Note | Required disposition | §9 Status | Verified |
|---|---|---|---|
| Note A (small-n caveat) | CARRIES FORWARD (active) | line 677 — present with both domains' n=11 / n=9 fired warnings | YES |
| Note C (cell-coverage denominator) | CARRIES FORWARD (active) — numeric update | line 678 — references §6.4 post-recovery denominator (20 analyzable + 5 all-QA-failed + 1 zero-record) | YES |
| Note D (no ceiling claims pre-4c) | CARRIES FORWARD (active) | line 679 — references §8.3 and §8.5; Phase 4c named as anticipated grounding path | YES |
| Note E (US-weighted composition; CN-origin augmentation REMOVED) | CARRIES FORWARD (active) — REPLACED augmentation removed per Q6(a) | line 680 — explicit: "The original T5 SME augmented Note E with 'PLUS disproportionate CN-origin decline pattern.' That augmentation is REMOVED per the RD-3 reframing memo... the CN-origin decline pattern was an instrument artifact (cap-exhaustion), not a signal." | YES |
| Note G (uninterviewed-cell wording) | CARRIES FORWARD (active) — verbatim phrase + RD-3 trailing clause per T15 | line 681 — verbatim "produced no interpretable primary-step output" preserved; RD-3 memo path cited | YES |
| Note K (CN-origin clustering) | REPLACED (audit preserved) | line 682 — explicit REPLACED status with rationale ("originating Phase 4a Gemini failures were cap-exhaustion instrument events, not safety-policy events") and RD-3 memo path | YES |

**Note E specifically (Q6(a) check):** the §9 row for Note E is the canonical surface for the CN-origin removal. The Reviewer's grep confirmed CN-origin appears only in REMOVED/REPLACED contexts; my own re-scan confirms zero active claims. The §8 prose makes no reference to CN-origin patterns as a signal. Q6(a) **CLEAN.**

**Note K specifically:** the disposition is REPLACED (not RETIRED, not NOT CONFIRMED, not "superseded") per the parent T4-redo SME Q3 ruling. The §9 Note K row uses the word REPLACED explicitly and references the RD-3 memo §3 disposition language. The audit-record framing ("the original Note K hypothesis is no longer testable from this corpus") is correct. **CLEAN.**

**T-series carry-forward (lines 687–692):** B6, B12, B14 carry forward (active); T1–T10 SATISFIED (specific deliverables; gate postures preserved). The S5 SATISFIED row correctly notes "the gate posture is preserved: future methodology-page-bound text on Note K disposition routes through CDA SME." The T11–T15 status will be set by this verdict (T11/T13 SATISFIED at RD-T5-3 Reviewer; T12/T14/T15 SATISFIED here).

**S-series carry-forward (lines 696–699):** S2 active (carried in §8.4 enumeration); S5 SATISFIED at RD-3 content verdict with gate posture preserved. **CLEAN.**

§9 PASS.

---

## §10 forward-carry verification

The §10 section enumerates the forward-carry items with file-path references:

| Required item | Present | Reference |
|---|---|---|
| v2 free-list prompt comparison study | YES | line 718; references `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md` |
| phi-4 ×6 adapter task | YES | line 722; references recovery report §7 item 4 |
| gpt-5.4-mini ×2 + mistral-small ×1 unexplained-failure investigation | YES | line 726; references recovery report §7 item 3 |
| Phase 4b G1 sensitivity study | YES | line 729; references `ARCHITECTURE.md` §5.3 |
| Phase 4c human grounding | YES | line 733; references `ARCHITECTURE.md` §1.5.5 |
| Methodology-page UI rendering (Phase 5/6, UI/UX-gated) | YES | line 737 |
| Phase 4b / next-domain expansion | YES | line 740 |

§10 closing paragraph (lines 743–747) correctly identifies the SME content verdict as gate chain step 3 and names this very file as the artifact closing Phase 4a at the analytical layer. The "no UI/UX gate at this layer" disposition (analytical, not frontend) is correct per the parent T4-redo SME Q4 precedent and the T5 redo plan-pass verdict §D.

§10 PASS.

---

## Completion-redo report review

I read the completion-redo report (`docs/status/2026-05-06-phase4a-completion-redo.md`) in full.

### Successor-not-replacement framing (lines 12–18)

The relationship-to-predecessor paragraph correctly frames both reports as standing on master:
- Original report (2026-04-23) is correct against the 2026-04-22 corpus.
- Redo report (this) is correct against the post-recovery corpus.
- "No `.SUPERSEDED.md` annotation is applied to the predecessor (the predecessor is not superseded; the corpus changed; both analyses are internally consistent against their respective input populations)."

This framing is methodologically correct. The Q6(b) discipline ("no incorrect framing of predecessor T5") is preserved in the explicit denial: "was correct against its input population." **CLEAN.**

### §1 Timeline (lines 22–37)

Twelve events listed in chronological order with commit hashes. The audit trail is complete and traceable. **PASS.**

### §2 Gate status (lines 40–64)

Original Phase 4a gates referenced by path (preserved verbatim at the original completion report). New gates introduced after original completion are enumerated with verdict files. The "Phase 4a is conditionally closed subject to the CDA SME content verdict at gate chain step 3" framing is correct — this verdict is gate chain step 3.

The verdict-file path cited (line 60: `docs/status/2026-05-06-phase4a-t5-redo-cda-sme-content-verdict.md`) does not match the actual filename (`docs/status/2026-05-07-t5-redo-cda-sme-content-verdict.md`). This is downstream of the same date-prefix question raised by the Reviewer. See Punted Item Disposition (1) below — I rule the date-prefix discrepancy is acceptable for the in-document reference because the plan-specified filename was the binding anchor at planning time, but the Coder may apply an inline annotation in a follow-on commit (not required for closure).

### §3 Data artifacts (lines 70–148)

The corpus state, the two DomainResult headline tables, the cell coverage summary, and the v0.1 audit-state preservation are all present. The §3.4 cell-coverage summary mirrors the analysis report §6.4 with the post-recovery breakdown (20 analyzable + 5 all-QA-failed + 1 zero-record). The verbatim Note G phrase ("5 cells produced no interpretable primary-step output") is preserved at line 129. **PASS.**

### §4 Cost summary (lines 152–162)

Phase 4a total: $6.24 ($4.95 original + $1.29 recovery + $0 analysis). Cap utilization 2.1%. **PASS.**

### §5 B2 backup status (lines 167–174)

Acknowledges the 0.2 DomainResult JSONs are pending the next nightly backup confirmation. The original completion report's B2 verification carries forward as the canonical 2026-04-23 record. **PASS.**

### §6 DATA_DICTIONARY.md addendum (lines 178–183)

Confirms no schema change in this task; R7 satisfied. The `thoughts_token_count` field's data dictionary update was carried by Task #16. **PASS.**

### §7 Outstanding carry-forward (lines 187–242)

Seven sub-sections enumerating the forward-carry items: §7.1 unexplained-failure residuum, §7.2 phi-4 adapter task, §7.3 Phase 4b G1 sensitivity study, §7.4 v2 prompt comparison study, §7.5 Phase 4c human grounding, §7.6 methodology-page UI rendering, §7.7 lede generation. Each has a file-path reference where appropriate. **PASS.**

### §8 Phase 4b readiness (lines 246–262)

Two pre-conditions further along than at original completion: (a) corpus stability via T5 redo, (b) Note J / Note K resolved (RD-3). The Note J / Note K disposition is methodologically correct: "the CN-origin decline pattern is an instrument artifact (Note K REPLACED); the prompt-variant concern that Note J raised does not block Phase 4b." Remaining pre-conditions enumerated (unexplained-failure disposition, G1 threshold reaffirmation, separate Architect plan with SME review).

The closing sentence ("Phase 4b is not blocked by T5 redo; the T5 redo PASS is one required input to its go/no-go decision") is the correct procedural framing. **PASS.**

### §9 What this report does not claim (lines 266–293)

Six explicit non-claims:

1. No categorical-reasoning, internal-state, or cultural-cognition claims (line 270–272) — §1.5 framing.
2. No generalization beyond the 11/9-model, two-domain, v1-prompt cohort (line 274–276) — Q6(c).
3. No "incorrect" framing of predecessor (line 278–281) — Q6(b); explicit denial.
4. No proximity to human cultural baseline despite STRONG_CONSENSUS (line 283–286) — Note D.
5. No "publishable" framing (line 288–289) — Q6(e) / T14.
6. No generalization of the cap-exhaustion reframe to other providers/failure modes/prompt types (line 291–293) — references RD-3 memo §6.

This list mirrors the RD-3 §6 pattern at appropriate scope, as the Reviewer noted. The structural match is correct: where RD-3 §6 is local to the 9-row cohort, the completion-redo §9 is local to the Phase 4a 121-record corpus. The non-claims correctly scale to the report's scope. **PASS.**

### §10 Phase 4a verdict (lines 297–316)

"Phase 4a is COMPLETE at the analytical layer, subject to CDA SME content verdict at gate chain step 3." Six bullet points summarizing the closure state. "Go / no-go for Phase 4b: GO (pending SME content verdict at gate chain step 3...)."

The procedural framing is correct: this very verdict closes gate chain step 3, and the GO disposition activates upon this PASS-WITH-NOTES. **PASS.**

**Completion-redo report verdict: PASS.** Successor-not-replacement framing is correct, the structure mirrors the predecessor with appropriate post-recovery numeric updates, and the "What this report does not claim" section meets the methodology-page-bound bar.

---

## Three Reviewer-punted items — explicit rulings

### Punted Item Disposition (1) — Completion-redo filename date prefix

**Reviewer flag:** The completion-redo filename uses 2026-05-06 prefix despite landing 2026-05-07.

**SME ruling: ACCEPT AS PLAN-SPECIFIED. No rename required.**

The T5 redo Architect plan (commit `2a4c6c2`, §2 RD-T5-4 task contract) specifies the canonical filename as `docs/status/2026-05-06-phase4a-completion-redo.md`. This was the plan-binding name at the time the Coder accepted the work, and the filename anchors to the plan document's date. Renaming the file post-commit would create a needless split between the path the plan binds and the path on disk. The same convention was used for the RD-3 reframing memo (filename anchored to `2026-05-05` despite landing `2026-05-06`) and was accepted at the RD-3 content verdict.

The audit trail is preserved: the commit message of `3fc70be` carries the `2026-05-07` git timestamp; the file-content `**Date:** 2026-05-07` line (line 3) names the actual commit date; the filename is the plan-binding anchor. A future audit reader has all three surfaces.

**No rename. No follow-on commit required for this item.** The convention is operationally sound and is consistent with the project's prior practice. (For future plans, the Architect may consider stating the filename anchor convention explicitly to forestall future Reviewer flags; this is a documentation-hygiene note, not a binding requirement on this task.)

### Punted Item Disposition (2) — T12 four-state taxonomy preserves State 3 as partial sub-case of State 1

**Reviewer flag:** §8.4 State 3 ("A non-reasoning model on a reasoning-capable provider") is a proper sub-case of State 1 in the T12 taxonomy. The Reviewer asks whether this partially-overlapping category structure is the intended disambiguation discipline.

**SME ruling: PRESERVATION OF THE FOUR-STATE STRUCTURE IS CORRECT — but a single clarifying sentence is required.** This is **Required Item 1** below.

The four-state structure is intentional in S2 because the *provider-side surfacing* of the field changes the disambiguation surface even when the underlying model behavior is the same. State 1 covers the case where the model produced no reasoning tokens *and* the provider would have surfaced them if it had. State 3 covers the case where the model produced no reasoning tokens *and* the provider does not surface the field at all (so the `0` carries no information about the model's reasoning behavior). State 2 covers the case where the model *did* reason but the provider doesn't surface them. State 4 covers the legacy-record case (field didn't exist at write time).

These are operationally distinct disambiguation states for a downstream analyst, but they collapse to the same field value of `0`. S2 carves the four states out *precisely because* the field value alone cannot distinguish them. The §8.4 enumeration is the methodology-page-bound surface that names the carve-outs.

The Reviewer's flag is methodologically correct: a reader of §8.4 standing alone may not see why State 3 is separately listed when its observable signature (field value `0`) is identical to State 1's. The remedy is not to collapse the taxonomy — that would lose the disambiguation S2 was designed to preserve — but to add a single inline clarifying sentence explaining that the four states share the field value `0` while differing in *what the value means*.

**The §8.4 prose holds the four-state list correctly. The required edit is a single inline clarification, named below as Required Item 1.**

### Punted Item Disposition (3) — §8.3 CI-overlap descriptive framing

**Reviewer flag:** The §8.3 claim that the difference between 0.78 and 0.71 consensus scores is "not distinguishable from bootstrap noise" is framed as a descriptive CI-overlap observation, not a formal hypothesis test. The Reviewer asks whether this framing meets the claims-validity bar for methodology-page prose.

**SME ruling: ACCEPT AS DESCRIPTIVE FRAMING. No hypothesis-test reframing required.**

A formal hypothesis test on a difference between two bootstrap-derived statistics from non-overlapping populations (n=9 holidays vs n=11 family) would require a test choice (parametric or non-parametric), a null specification, and a multiple-comparison correction surface — none of which §8.3 has positioned itself for. The CI-overlap observation is the methodologically correct *descriptive* surface here: "the CIs overlap; the difference is not distinguishable from bootstrap noise" is exactly the right plain-language statement to make about two bootstrap point estimates with overlapping uncertainty bands.

The methodology-page bar is "credibility to a skeptical reader," not "publishable in *Nature*." A skeptical reader of the §8.3 prose receives:
- Two point estimates (0.78 and 0.71).
- Both bootstrap CIs cited inline ([0.47, 0.96] and [0.50, 0.91]).
- The descriptive observation that the CIs overlap.
- The plain-language inference that the difference is not distinguishable from bootstrap noise under the population sizes.
- The disposition disclaimer ("does not constitute a comparative claim about how models organize holiday vocabulary versus family vocabulary").

This is a methodologically sound surface. A formal hypothesis test would (a) invite multiple-comparison concerns the §8.3 surface does not have the structural support for, (b) over-formalize a comparison the project has explicitly bounded as descriptive, and (c) tilt the audience-translation axis toward jargon the methodology page does not carry elsewhere.

The CI-overlap observation, paired with the explicit non-claim, is the right descriptive surface. **No reframing required.**

(For future Phase 4b cross-domain comparisons where the population sizes are larger and the comparison is part of a formal cross-domain claim, a hypothesis-test surface may be appropriate. This is forward-looking, not blocking.)

---

## Q6(a)–(e) public-copy guardrail check

### Q6(a) — No CN-origin augmentation to Note E

**CLEAN.**

The Reviewer's check found CN-origin appears only in REMOVED/REPLACED contexts. My own re-scan:
- Analysis report §9 Note E row (line 680) — explicit REMOVED notation.
- Analysis report §9 Note K row (line 682) — explicit REPLACED notation.
- Completion-redo report line 214 (Phase 4b readiness §7.3) — "the CN-origin decline pattern is an instrument artifact" — descriptive of the disposition, in the context of stating Note K is REPLACED. Not an active claim.
- Completion-redo report line 255 (Phase 4b readiness §8) — "the CN-origin decline pattern is an instrument artifact (Note K REPLACED)" — same context, same disposition.

No active CN-origin claim anywhere. The Note E framing is "US-weighted composition" only, without the augmentation. **PASS.**

### Q6(b) — No "incorrect" framing of predecessor T5

**CLEAN.**

The word "incorrect" appears in:
- Analysis report line 485 — guard statement ("no 'incorrect' framing of the predecessor T5") in the §8 opening guard paragraph.
- Completion-redo report line 279 — explicit denial ("That the original Phase 4a completion report was incorrect. It was correct against its input population").

Both uses are anti-claims, not assertions. The §8.5 "Population shift, not methodological correction" subsection (lines 650–655) and the completion-redo §9 non-claim list both reinforce: the predecessor was correct against its input population. **PASS.**

### Q6(c) — No cross-provider/failure-mode/prompt-type generalization

**CLEAN.**

§8.5 "Single-provider observation for the recovered cells" (lines 633–638) explicitly bounds:
- "Three models on OpenRouter (gemini-2.5-pro, llama-4-maverick, glm-5.1) under v1 prompt conditions."
- "Cross-provider, cross-failure-mode, or cross-prompt-type generalization requires new evidence that this corpus does not supply."
- "Carries forward the parent T4-redo SME T6 scope discipline."

Completion-redo §9 line 274: "That the observations generalize beyond the 11/9-model, two-domain, v1-prompt corpus conditions. Any cross-provider, cross-failure-mode, or cross-prompt-type generalization requires new evidence."

§8.1, §8.2, §8.3 prose all maintain "this specific recovered corpus," "under v1 prompt conditions," "model-to-model distances only" framing. **PASS.**

### Q6(d) — No internal-state claims

**CLEAN.**

I ran my own grep beyond the Reviewer's: `worldview|believes|thinks|could not see|was blind to|didn.t know|the model recognized|the model identified|the model.s understanding|the model.s interpretation` — zero hits across both files except in metalinguistic guard contexts (the §8 opening guard statement and the Reviewer's own enumeration in the verdict file).

Approved descriptive substitutes are used throughout:
- "Model X's output treats..." (§8.1, §8.2 OCI bullets — "within-model descriptive properties under the v1 prompt conditions; they do not constitute claims about model capability or model-internal reasoning").
- "Free-list outputs share a high proportion of culturally salient items" (§8.1 line 502–503) — output property, not cognition claim.
- "All models produce positive centrality" (§8.1 line 506) — measurement property, not categorical-reasoning claim.

The `mistral-small-2603` OCI=0.00 disposition (§8.2 lines 558–560; "This is a cell-coverage descriptor, not a claim about the model") is the surgically right anti-claim where it would be most tempting to over-read. **PASS.**

### Q6(e) — No "publishable" framing (T14)

**CLEAN.**

Grep for `publishable` returns one hit: analysis report line 486, in the §8 opening guard statement (`no "publishable" framing per T14`). This is the rule citation, not an active claim.

Completion-redo §9 line 288–289: "That any finding here is suitable for external academic publication. The methodology-page bar is credibility to a skeptical reader, per CLAUDE.md §1." Explicit denial; the correct positive framing of the constraint.

§8.5 closing bullet (lines 662–665): "They are not presented as findings in any academic publication venue; per CLAUDE.md §1, the bar is credibility to a skeptical reader, not suitability for external publication." **PASS.**

---

## §1.5 semantic drift check

Beyond the literal-grep forbidden-vocab list, I scanned §8 for shape-of-claim drift — phrasings that imply causal reasoning, introspective access, or any model-property claim that goes beyond corpus-lens-as-output description.

**Findings:**

- §8.1 OCI bullet: "High OCI indicates that run-to-run within-model output is highly consistent; low OCI indicates more variable output across runs. These are within-model descriptive properties under the v1 prompt conditions; they do not constitute claims about model capability or model-internal reasoning." — explicit anti-claim, methodologically correct.

- §8.1 family-domain MDS bullet: "The 11-model MDS map... shows that most models cluster near the origin with one clear outlier (`openai/gpt-5.4-mini`, dim1 = −0.54)." — descriptive shape, no causal framing.

- §8.2 holidays-domain MDS bullet: "shows `mistralai/mistral-small-2603` and `openai/gpt-5.4-mini` as peripheral points... These are model-to-model distances on the post-recovery corpus under v1 prompt conditions; the coordinates carry no human-baseline grounding." — descriptive shape with explicit Note D anti-claim.

- §8.3 cross-domain bullets: each numeric ordering observation is followed by an explicit non-claim (e.g., "the observation is a descriptive property of the post-recovery corpus; it does not constitute a comparative claim about how models organize holiday vocabulary versus family vocabulary").

- §8.4: the four-state enumeration is the most claim-sensitive surface and the prose holds the descriptive disambiguation correctly (states 1–4 are descriptions of *observable cases*, not *model-internal states*; the states describe what the value `0` *can mean* in different provider configurations).

**No semantic drift detected.** The §8 prose holds the corpus-lens-as-output framing throughout. The only claim-sensitivity remaining is §8.4 State 3 / State 1 overlap, addressed as Required Item 1 below.

**PASS.**

---

## Audience translation axis check

I read both files as if they appeared on `cogstructurelab.com/methodology` standing alone, without the verdict-file context.

**Analysis report §8–§10:**

A skeptical anthropologist or AI researcher reading the §8 prose receives:
- A clear two-domain numeric summary with bootstrap CIs.
- Explicit small-n caveats on every consensus claim.
- A cross-domain comparison that bounds itself descriptively.
- An epistemic-state taxonomy on `thoughts_token_count=0` that is enumeratively complete (4 states).
- A scope-discipline list at §8.5 that bounds every direction of overclaim.
- A binding-note compliance table at §9 that names every original T5 note's disposition with explicit rationale.
- A forward-carry list at §10 with file-path references.

The reader walks away with the right epistemic map: the project measured something specific under specific conditions, both domains carry small-n caveats, the methodology has been audited at multiple gates, the analytical layer is closed but Phase 4b/4c remains open, and the corpus shift between original T5 and redo reflects a recovery campaign, not a methodological correction.

**One audience-translation refinement is in scope (Required Item 1 below):** the §8.4 four-state list reads cleanly as a list, but the State 1 / State 3 overlap is non-obvious to a methodology-page reader without the S2 verdict at hand. A single clarifying clause discharges this.

**Completion-redo report:**

A reader receives a parallel-structure successor to the 2026-04-23 completion report with post-recovery updates. The relationship-to-predecessor framing is explicit (both reports stand on master; both are correct against their input populations). The cell-coverage update from "18 analyzable + 5 decline-interviewable" to "20 analyzable + 5 all-QA-failed + 1 zero-record" is methodologically traceable. The Phase 4b readiness section makes the GO disposition contingent on this verdict. The "What this report does not claim" section is plain-language and complete.

**Audience-translation axis: PASS-WITH-NOTES** (resolved by Required Item 1 below).

---

## Required pre-merge items

### Required Item 1 — Add a clarifying clause to §8.4 disambiguating State 1 from State 3

**Where:** Analysis report §8.4, between the four-state enumeration (lines 610–617) and the State-mapping paragraph (lines 619–623).

**The required edit:** Add a single sentence (or phrasing equivalent) immediately following the four-state list, before the "State (4) applies to..." sentence. Acceptable forms (Coder picks one):

(a) *"States (1)–(4) are operationally distinct disambiguation cases that share the same field value of `0`; they differ in what the value means under different provider configurations, not in the field's observable signature."*

(b) *"The four states share the field value `0`; the disambiguation among them depends on which provider is in use and whether the field is captured at collection time."*

(c) *"The four states are not separable from the `thoughts_token_count` field alone — they are differentiated by provider behavior (states 1, 2, 3) and by collection-era metadata (state 4)."*

Any of the three lands the audience-translation refinement. The Coder may pick or propose an equivalent. The Reviewer re-checks the single sentence; **no further SME pass is required if the rewording matches one of the three approved forms.**

This is a one-sentence inline addition. It does not affect §8.4's binding-note compliance (T12 SATISFIED holds; the four-state list itself is unchanged). It does not affect any other section.

**Disposition:** Required as a follow-on Coder commit on the same RD-T5-4 task line. After the Reviewer re-confirms the single sentence, the T5 redo is **fully closed at gate chain step 3.**

---

## Notes-level (no follow-on commit required)

### Notes Item 1 — Filename date prefix

The completion-redo filename uses the plan-specified 2026-05-06 prefix. As ruled in Punted Item Disposition (1) above, this is acceptable per project convention. No rename required. For future plans, the Architect may consider stating the filename-anchor convention explicitly. **Not blocking.**

### Notes Item 2 — Verdict-file path reference in completion-redo §2

The completion-redo report line 60 cites the canonical SME content verdict file path as `docs/status/2026-05-06-phase4a-t5-redo-cda-sme-content-verdict.md`. This verdict file is actually at `docs/status/2026-05-07-t5-redo-cda-sme-content-verdict.md`. The discrepancy is downstream of the same date-prefix question. The Coder may apply an inline annotation in the same follow-on commit as Required Item 1 if a corrected reference is desired; **not required for closure.**

### Notes Item 3 — The "STRONG_CONSENSUS" classification under small-n

The §8 prose carries the small-n caveat on every STRONG_CONSENSUS reference. This discipline is correct. For future methodology-page UI rendering, when STRONG_CONSENSUS is surfaced as a label or a badge, the rendering must carry the small-n caveat at the same visual proximity. This is forward-looking guidance for the eventual Phase 5/6 UI/UX gate, not a binding requirement on this task.

---

## What I am explicitly NOT ruling on

- **The eventual Phase 5/6 methodology-page UI rendering of §8–§10.** Out of scope per T5 redo plan §1 disposition table. Separate UI/UX-gated task. The §8 prose I have just PASSed is methodology-page-bound *text*; the visual rendering is a separate gate cycle. (The S5 gate posture survives: any future methodology-page-bound text on Note K disposition routes through CDA SME if the gloss changes the methodological claim.)

- **Phase 4b G1 sensitivity study.** Out of scope per the §10 forward-carry. Separate Architect plan with full SME review. The T5 redo PASS is one input.

- **Phase 4c human grounding.** Out of scope per Note D. Separate Architect plan.

- **The phi-4 ×6, gpt-5.4-mini ×2, mistral-small ×1 unexplained-failure investigations.** Out of scope per the recovery report §7 and the §10 forward-carry. Separate Architect tasks.

- **The v2 free-list prompt comparison study.** Out of scope per the §10 forward-carry and `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md`. Separate Architect plan with SME review.

- **Lede generation for Phase 4a results.** `cdb_publish` territory; per CLAUDE.md §6 R12. Separate task.

- **DeclineInterview schema gaining `thoughts_token_count`.** Task #16 SME Q5 directional preference. Backlog.

- **Drift / longitudinal Procrustes.** Multiple version snapshots required; out of scope until Phase 6+.

---

## Carry-forward of T11–T15 + new bindings

**T11 (§7 framing guard) — SATISFIED at RD-T5-3 Reviewer.** The §7 introduction at lines 415–423 carries the framing-guard sentence ("Both DomainResults are correct against their respective input populations... The deltas reflect the population shift introduced by the 2026-05-05 recovery campaign"). Discharged at the RD-T5-3 commit; the gate posture survives as a general principle for future delta-comparison sections.

**T12 (§8.4 four-state enumeration or S2 reference) — SATISFIED.** The §8.4 enumeration uses both T12 (a) (explicit four-state list at lines 610–617) and (b) (S2 file-path reference). Per Required Item 1 above, the prose receives a single inline clarification on State 1 / State 3 overlap; that clarification does not affect T12 satisfaction. **Gate posture preserved:** future methodology-page text referencing the `thoughts_token_count=0` epistemic states must enumerate or cite S2, with the clarifying-overlap discipline added by Required Item 1.

**T13 (§6 grep command) — SATISFIED at RD-T5-3 Reviewer.** The §6.2 verbatim grep command is present at lines 350–354. Discharged.

**T14 (§8 (e) "no publishable" framing) — SATISFIED.** Q6(e) clean. Discharged.

**T15 (Note G verbatim phrase + RD-3 trailing clause) — SATISFIED.** Verbatim "produced no interpretable primary-step output" preserved at four locations (analysis report lines 390, 474, 681; completion-redo line 129); RD-3 path cited in the §9 Note G row. Discharged.

**B6 (parent T4-redo public-copy guardrails (a)–(e)) — CARRIES FORWARD (active).** All five avoidances PASSed in the §8 prose and the completion-redo report. The B6 binding survives as a general principle for any future methodology-page-bound text touching the cap-exhaustion reframe disposition. **Gate posture preserved.**

**B12 (parent T4-redo future-batch binding precedent) — CARRIES FORWARD (active).** Not directly exercised by the T5 redo; gate posture preserved for future batches.

**B14 (parent T4-redo numerics-vs-interpretation separation) — CARRIES FORWARD (active) — exercised cleanly.** The four-task split (RD-T5-1 / RD-T5-2 / RD-T5-3 / RD-T5-4) honored B14. RD-T5-3 carried §1–§7 numerics; RD-T5-4 carried §8–§10 interpretation. I verified RD-T5-4 introduces no new numerics — every numeric value in §8 is traceable to §4–§7 with section-citation precision. **PASS.**

**S2 (Task #16 four-state taxonomy) — CARRIES FORWARD (active).** §8.4 enumeration discharges this on the T5 redo surface. The taxonomy itself remains active for any future methodology-page-bound text on `thoughts_token_count`.

**S5 (Note K re-classification gate) — SATISFIED at RD-3 content verdict; gate posture preserved.** Future methodology-page-bound text on Note K disposition continues to route through CDA SME if the gloss changes the methodological claim. The T5 redo §8 prose, as a methodology-page-bound text touching Note K, has been routed through this content verdict and PASSes. **Gate posture preserved.**

**No new T-series binding notes introduced in this verdict.** The Required Item 1 inline clarification is a one-sentence audience-translation refinement, not a new binding note. T12's binding text is unchanged; the satisfaction of T12 is unchanged.

**Active binding-note count after this verdict:** carries forward from the parent T4-redo verdict + RD-3 content verdict at ~44 active notes, with T11/T12/T13/T14/T15 now SATISFIED (gate postures preserved). No notes vacated; no notes replaced; no notes added.

---

## Gate disposition

**T5 redo gate chain step 3 (this content verdict): PASS-WITH-NOTES.**

The Coder applies Required Item 1 (one inline sentence in §8.4) in a follow-on commit. The Reviewer re-checks the single sentence; **no third SME pass is required** if the rewording matches one of the three approved forms.

After the Reviewer re-confirms the inline clarification:
- **Phase 4a is fully closed at the analytical layer.**
- **Phase 5+ methodology-page UI rendering** is unblocked at the methodology-text gate (UI/UX gate still required separately when the rendering work begins).
- **Phase 4b go/no-go disposition** activates with this PASS-WITH-NOTES (the T5 redo is one of multiple required inputs; the others are unexplained-failure dispositions and G1 threshold reaffirmation, per `ARCHITECTURE.md` §5.3 and the §10 forward-carry).

Notes Items 1, 2, 3 are non-blocking observations; no follow-on commit required for them, though the Coder may bundle Notes Item 2 (verdict-file path reference) into the same follow-on commit as Required Item 1 if convenient.

**T5 redo closure status:** **CLOSED PENDING REQUIRED ITEM 1.** After the inline clarification lands, closure is full.

**No UI/UX gate** on this content verdict (analytical-layer methodology-text; per parent T4-redo SME Q4 precedent and T5 redo plan-pass verdict §D).

**No additional Mark sign-off required** for this verdict; the §5 framing decisions on the parent plans are already on master.

---

## Sign-off

The §8–§10 prose is methodologically sound and methodology-page-bound under the §1.5 framing. The §1–§7 / §8–§10 separation honors B14 cleanly. T11–T15 are all satisfied. B6 (a)–(e) are all satisfied. The Note K REPLACED disposition and the Note E without-CN-origin posture are correctly preserved. The completion-redo report mirrors the predecessor with appropriate post-recovery numeric updates.

The single required edit is a one-sentence inline clarification at §8.4 to disambiguate State 1 from State 3 in the four-state taxonomy — a methodology-page audience-translation refinement that does not affect any binding-note compliance and does not affect any other section.

The three Reviewer-punted items are explicitly ruled: (1) filename date prefix accepted as plan-specified, no rename required; (2) State 1 / State 3 overlap preserved per S2 taxonomy with a single inline clarification required; (3) §8.3 CI-overlap descriptive framing accepted as the methodologically correct surface for two bootstrap point estimates with overlapping uncertainty bands.

The verdict is **PASS-WITH-NOTES**. Required Item 1 is the sole pre-merge edit. After the Reviewer re-confirms it, **the T5 redo is fully closed and Phase 4a is closed at the analytical layer.**

*Posted to `#lsb-cda-sme`. Binding for the Required Item 1 follow-on commit. No third SME pass required. The CDA SME thanks the Coder for the disciplined separation between RD-T5-3 numerics and RD-T5-4 interpretation, the careful preservation of the Note G verbatim phrase across four locations, and the structural mirror between the completion-redo §9 non-claim list and the RD-3 §6 pattern at appropriate scope.*
