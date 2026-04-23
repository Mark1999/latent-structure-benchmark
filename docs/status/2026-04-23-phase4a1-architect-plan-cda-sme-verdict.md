# CDA SME Verdict — Phase 4a.1 Architect Plan (task #21)

**Date:** 2026-04-23
**Reviewer:** CDA SME (Opus)
**Scope:** Architect's decomposition plan for Phase 4a.1 (decline-interview backfill)
**Predecessors in dependency chain:**
- Task #26 (decline-interview protocol landing) — referenced by plan as completed
- Task #14 / T6 QA sweep — identifies 27 `qa_passed=False` records; 5 decline-interviewable cells
- T5 Note C / Note J / Note K framing — binds methodology-page copy pending Phase 4a.1 cross-tab
- `SME_REVIEW.md` §1.1 (Romney 5.0 small-n rationale) — bears on the small-n floor for Note K

---

## Verdict

**CDA SME VERDICT: PASS-WITH-NOTES**

| Axis | Verdict |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | PASS-WITH-NOTES |
| Axis 3 — Claims validity | PASS-WITH-NOTES |
| Axis 4 — Audience translation | PASS |
| Register compliance | PASS (no register claims are made; this is pre-session / audit-only work) |
| Vocabulary compliance | PASS (plan text clean) |

Binding notes are enumerated in §"Required before plan advances" below. The plan is methodologically sound and ready to advance to T1 once those notes are incorporated into the task-level specs. No re-review required for notes 1, 3, 4, 5, 6 (incorporate into plan verbatim); note 2 (Note J expected-rate baseline) requires a one-line architect confirmation before T4.

---

## Axis-by-axis findings

### Axis 1 — Protocol validity: PASS

The plan correctly treats decline-interviews as an instrument of **audit and elicitation on refusal outcomes**, not an analytic input to Register 1 or Register 2 statistics. The "failures are findings" invariant is honored: refused / empty / degenerate outputs are preserved verbatim and re-interviewed, not discarded, not patched, and not mutated on the original `InformantRecord`. D3 (batch-start `detection_timestamp` passed to every call) and D5/D6 (verbatim prompt/response carried forward from the originating step) are correct.

D1 (defer 8 grok-4 Check-5-only latency records from the API backfill) is the right call under the currently landed v1 detector. The landed detector keys on **structural** refusal signals (empty output, allowlist refusal strings, single-degenerate pile, parse failure). Latency alone is a QA aggregate flag, not a refusal signature. Including these 8 records in the interviewable population by fiat would (a) conflate a latency pattern with a refusal pattern, and (b) silently broaden the v1 detection rule without a design review. The correct path is: enumerate them in T1, document the not-triggered rationale in T5, and treat any subsequent decision to include them as a v2 detector amendment on a new plan cycle. Concur.

One protocol point I want documented in T1's dry-run output, not just T5 (see note 1 below): for each record not triggered, the **reason** (e.g., "Check-5 latency-only, no structural trigger") should appear in the enumeration artifact, not only as a bulk count. That turns the enumeration into an audit trail rather than a summary.

### Axis 2 — Analytical validity: PASS-WITH-NOTES

The Note J cross-tab is **descriptive auditing**, not inferential statistics. That framing is correct and I want it preserved in T5 copy: the cross-tab counts decline-interview records stratified by (origin × openness × collection_method × outcome_class); it does **not** assert a consensus claim, a between-model test, or a Register 2 finding. The plan honors this by siting the cross-tab script in `scripts/` rather than `cdb_analyze/` (avoids R12 ambiguity) — concur.

**Where I want to push back:**

1. **"Expected under uniform distribution over the detected-session population"** — this is the wrong baseline for the flag. The detection process is already stratified by which cells yielded any interviewable records at all. Declaring a cell "≥ 3× expected under uniform" against the **interviewed-only** denominator bakes in the selection effect and will over-flag cells that are over-represented merely because they had more `qa_passed=False` to begin with. The correct baseline is **the corpus (collection-attempt) distribution over the same stratification cells**, i.e., per-cell decline-interview count divided by per-cell collection-attempt count, compared to the pooled decline rate. See ruling 1 below. This is the only axis-2 issue I flag as binding.

2. **Stratification sparsity at n ≈ 5.** With 5 informants-origin decline records (plus potentially a handful of Gemini failures), a three-way factorial (origin × openness × method) yields mostly empty cells. I would accept the Architect's structure **with model-origin as rows and a collapsed column** (`origin × {openness | method}` collapsed to whichever column is non-degenerate per row) rather than the full Cartesian product. See ruling 1.

3. **Note K threshold (2.0 ratio, 4-record floor).** The 2.0 rate-ratio is defensible as an **effect-size threshold**, not as an inferential test — at this n, no inferential test clears. I concur with 2.0 as a floor, but I want the CONFIRMED branch gated on **two** additional conditions: (a) at least one non-CN origin has a non-zero decline count in the same cross-tab (otherwise the ratio is undefined and can be infinite at n=1), and (b) Check-6 extended-thinking confound is explicitly ruled out before CONFIRMED is asserted. See ruling 2.

4. **Small-n floor of 4 CN decline records.** This is binding-memory territory. The reconciled Romney small-n threshold is n<15 per `SME_REVIEW.md` §1.1 + Anders & Batchelder 2015, which governs consensus-ratio stability. Note K is a **rate-ratio** claim, not an eigenratio claim, so the Romney-specific floor does not bind it directly, but the **spirit** does: a 4-record floor is at the very low end of what I would accept, and only because Note K's disposition is a methodology-page framing decision, not a Register 2 claim. Concur with the 4-record floor **as the INCONCLUSIVE boundary**, not the CONFIRMED floor. The CONFIRMED branch in the Architect's current wording is satisfied at exactly n=4, which is right at the boundary — see ruling 2.

### Axis 3 — Claims validity: PASS-WITH-NOTES

The re-analysis deferral (RISK 4) is the right call. Phase 4a.1 is an **audit and enumeration** step; recomputing `data/results/family/0.1.json` / `data/results/holidays/0.1.json` inline would bundle two distinct concerns (denominator shift + audit ruling) and make the audit commit non-reviewable. Concur with the "flag as follow-up task" disposition.

**Binding claims-validity concerns:**

1. **Note K disposition must not read as a finding about CN models.** My memory note on CN clustering is explicit: frame as a **coverage / protocol robustness caveat**, not a finding about CN model behavior, until the cross-tab rules out elicitation-protocol artifacts (prompt language, refusal training, API routing). T5 §9 must carry this framing verbatim or equivalent. If CONFIRMED: the methodology-page amendment reads "US-weighted composition PLUS disproportionate CN-origin decline pattern" as a **coverage caveat on LSB's protocol reach**, not as a claim that CN models behave differently. See ruling 6.

2. **NOT CONFIRMED must not silently retire the signal.** "NOT CONFIRMED" currently reads as retire-Note-K-by-reference. That is correct only if the Note J cross-tab produces an alternative explanation — not if the ratio simply falls short. A ratio of, say, 1.6 with mixed origins is not "NOT CONFIRMED"; it is "INCONCLUSIVE with suggestive pattern." The disposition wording needs a third path-in. See ruling 6.

3. **"Recursive decline" as a valid `DeclineInterview`.** Correct. A model that declines the follow-up is producing a second-order refusal, and that is itself a categorical datum. The 50% re-review threshold (RISK 2) is fine as a prompt-robustness tripwire — not as an inferential threshold. See ruling 4.

### Axis 4 — Audience translation: PASS

Plan text uses the right vocabulary throughout: "decline-interview," "originating_outcome_class," "coverage caveat" (in the CN-clustering reasoning), "audit trail." No forbidden vocabulary. No "within-model consensus" or equivalents. No "worldview / believes / thinks" applied to models. Note K's public-facing phrasing is not yet drafted in this plan — that lands in T5's completion report and will be reviewed against the forbidden-vocabulary table at that gate. Flagging here: **"CN-origin models decline more often"** would FAIL on the methodology page because it frames a coverage/protocol signal as a model behavioral claim. The T5 draft must route the phrasing through the coverage-caveat frame. See ruling 6.

---

## Rulings on the six Architect questions

### Ruling 1 — Note J cross-tab structure and expected-rate baseline

**1a. Expected-rate baseline: switch to corpus distribution, not interviewed-only uniform.**

The flag condition as written ("≥ 3× expected under uniform distribution over the detected-session population") bakes in selection bias and will over-flag cells that merely had more `qa_passed=False` to begin with. The correct baseline is:

```
expected_per_cell = (total_decline_interviews) × (collection_attempts_in_cell / total_collection_attempts)
flag if observed_per_cell >= 3 × expected_per_cell AND observed_per_cell >= 2
```

The `>= 2` floor is a small-n guard: a single record in a thinly-populated cell will trivially exceed 3× expected under any sensible denominator, and that is noise, not signal. **This is binding before T4 writes the cross-tab script.** One-line Architect confirmation in the T4 spec is sufficient (no re-review).

**1b. Stratification: collapse to model-origin × outcome_class as primary; openness and collection_method as secondary drill-downs.**

At n ≈ 5 informants-origin + unknown Gemini failures, the full Cartesian product (origin × openness × method) is mostly empty cells. The primary cross-tab should be `outcome_class × origin` (one page); secondary tables can slice by openness and by collection_method separately if the Architect wants them documented. Do not publish a three-way factorial at this n — the empty cells will read as structure where there is none. **Binding.**

**1c. Cell value: keep as count of decline-interview records (the interviewed population).** Concur with the Architect's current definition. Do not switch to raw `qa_passed=False` count — the raw count includes the 8 grok-4 latency-only records that are deferred out.

### Ruling 2 — Note K re-evaluation thresholds

**2a. 2.0 rate-ratio is acceptable as a CONFIRMED trigger** — but gate additionally on:
- Non-CN decline count ≥ 1 (denominator of the ratio must be finite; infinity-ratios at n=0 do not count as CONFIRMED)
- Check-6 extended-thinking confound is explicitly addressed in T5 §9 (if the decline population is dominated by models that route through extended-thinking pathways regardless of origin, that is the stronger explanation and Note K is NOT CONFIRMED on the origin axis)

**2b. Small-n floor: tighten CONFIRMED to ≥ 5 CN-origin decline records; keep INCONCLUSIVE at < 4.** Reasoning:
- At exactly n=4, a single reclassification (any one of the 4 being reassigned to a different outcome class at T5) flips the disposition. That is the same instability the feedback-memory on threshold rigor calls out: one swap should not flip a binding methodology-page disposition.
- n=5 gives a one-record cushion. This is still extremely low-n, but Note K is a coverage caveat, not a Register 2 claim, so the threshold can be permissive in exchange for the caveat-framed language I require in ruling 6.
- The 4–5 record band (≥ 4 but < 5) becomes **INCONCLUSIVE with suggestive pattern** — a third disposition not in the Architect's current taxonomy. See 2c.

**2c. Add a third disposition: INCONCLUSIVE-SUGGESTIVE.** Current taxonomy (CONFIRMED / NOT CONFIRMED / INCONCLUSIVE) collapses two distinct states:
- Ratio < 2.0, no alternative explanation → INCONCLUSIVE (current plan correct)
- Ratio ≥ 2.0 but small-n floor not met, no alternative explanation → **INCONCLUSIVE-SUGGESTIVE** (new)

The INCONCLUSIVE-SUGGESTIVE disposition triggers Note K being carried forward verbatim into the methodology page with the `n=4` caveat explicit, and triggers re-evaluation at the next Phase 4a.2 remediation cycle. This prevents a suggestive pattern from being quietly retired on a technicality.

**Binding for T4 script and T5 disposition logic.**

### Ruling 3 — D1 (defer 8 grok-4 Check-5-only records)

**Concur.** See Axis 1 rationale. The v1 detector is defined by structural refusal signals. Latency is an aggregate QA flag, not a refusal signature. Including the grok-4 records by fiat now would amount to an un-reviewed v2 detector expansion. Correct disposition: enumerate in T1, document not-triggered reasoning in T5, flag as a RISK 5 follow-up.

One addition to the T5 §5 write-up: enumerate the 8 records **by (model, domain, originating_step)** so that if Mark later rules them in, the follow-up plan has a ready-made worklist. A raw count of "8" alone is insufficient audit trail.

### Ruling 4 — RISK 2 (recursive decline threshold)

**50% is too high as the sole re-review trigger.** A recursive-decline rate above 50% would indicate the decline-interview instrument itself is broken across most of the interview population — that is a very late signal. I want a **two-tier** re-review rule:

- **Any recursive decline in a non-CN-origin model → immediate SME prompt re-review**, regardless of rate. One such record suggests the prompt fails in a context broader than the CN-clustering hypothesis would predict, and that is worth a narrow review even if the overall rate is low.
- **Rate ≥ 33% across the full decline-interview population → broad SME prompt re-review** (lower than the Architect's 50%, and on the full population rather than per-origin). 33% is roughly "one in three recursive" which is the threshold at which I start to doubt the instrument is producing audit-grade output.

**No preemptive v1 prompt refinement.** If the rate comes in high, that is a T6-equivalent follow-up on a new plan cycle; patching the decline-interview prompt inline during T3 would contaminate the run. Append-only applies to the decline-interview instrument as well.

### Ruling 5 — RISK 4 (re-analysis deferral)

**Concur with the deferral.** Phase 4a.1 is an enumeration-plus-audit step. Re-running the analysis pipeline to regenerate `data/results/family/0.1.json` / `data/results/holidays/0.1.json` inline would bundle two distinct reviewable artifacts (audit outcome + updated Register 2 results) into one commit and would make the audit non-reviewable on its own merits.

Requirement for T5 §9: explicitly enumerate the **specific numerics** that would shift if the denominator changes (e.g., "18/23 → 22/23 cells analyzable if all 4 Check-8 records decline-interview successfully"), so the follow-up task has a ready-made worklist and the dashboard copy impact is visible.

### Ruling 6 — T5 §9 language on Note K disposition

**CONFIRMED branch:**

The methodology-page amendment wording must frame the signal as a **coverage / protocol robustness caveat**, not as a finding about CN model behavior. Concretely, the T5 draft should propose language along the lines of:

> "LSB's v1 coverage is US-weighted by informant composition (7 of 12 models in the v1 slate are US-origin). A secondary coverage caveat applies: CN-origin models in the v1 slate disproportionately produced responses that did not pass QA on the family and holidays domains (N of 5 decline-interviewable cells are CN-origin, of N_CN CN-origin collection attempts vs. N_nonCN non-CN collection attempts). This is a signal about the reach of LSB's elicitation protocol across the v1 slate, not a claim about CN model behavior. See `docs/status/2026-04-23-phase4a1-completion-report.md` for the full cross-tab and alternative-explanation review."

**The specific phrasing is Mark's call.** What I require is:
1. The frame must be "LSB's protocol reach," not "how CN models behave."
2. The cross-tab must be linked, not summarized-only, so the reader can check the n.
3. Alternative-explanation review (Check-6, API routing, refusal-training artifacts) must be visible in the same section, not footnoted.

**NOT CONFIRMED branch:**

Retirement-by-reference is acceptable **only if** T5 §9 documents the alternative explanation that supplants the origin signal (e.g., "the cross-tab shows the decline pattern is better explained by extended-thinking routing, not origin"). If there is no alternative explanation and the ratio simply falls short, the disposition is INCONCLUSIVE or INCONCLUSIVE-SUGGESTIVE per ruling 2c, not NOT CONFIRMED.

**INCONCLUSIVE / INCONCLUSIVE-SUGGESTIVE branches:**

Note K is carried forward verbatim into the methodology page with the current sample size explicit ("Based on n=X decline records; pattern is suggestive but not confirmed at this sample size. Next re-evaluation scheduled for Phase 4a.2 remediation."). This keeps the caveat visible without over-committing to the coverage-caveat framing.

---

## Required before plan advances

Bundle these into the Architect's updated plan before T1 begins. None require re-review by SME; ruling 1a requires a one-line confirmation in the T4 spec only.

1. **T1 enumeration artifact must include per-record not-triggered reasoning** for the 8 grok-4 Check-5-only records and for any Gemini failures-origin records that lack `prompt_verbatim`. Not just counts. (Axis 1 finding.)

2. **T4 cross-tab baseline is corpus distribution, not interviewed-only uniform**, with the `>= 2` floor guard. (Ruling 1a. Binding; one-line Architect confirmation in the T4 spec.)

3. **T4 cross-tab primary view is `outcome_class × origin` (2D); openness and collection_method are secondary drill-downs, not additional factors in a factorial.** Do not publish a three-way factorial at this n. (Ruling 1b.)

4. **T4/T5 Note K taxonomy adds INCONCLUSIVE-SUGGESTIVE**; CONFIRMED tightens to ≥ 5 CN-origin records + non-zero non-CN count + Check-6 confound ruled out. (Ruling 2.)

5. **T5 §9 CONFIRMED wording is coverage-caveat framed**, not model-behavior framed; cross-tab is linked and alternative-explanation review is visible. (Ruling 6, Axis 3 finding 1.)

6. **RISK 2 re-review rule is two-tier (any non-CN recursive → narrow; ≥ 33% overall → broad)**, not single-threshold 50%. (Ruling 4.)

7. **T5 §9 re-analysis follow-up enumerates specific numerics that would shift** under each denominator scenario, not just a "flag as follow-up" note. (Ruling 5.)

8. **T1 dry-run reports Gemini failures count** before T3 commits to the $2 cap; if the count blows through the 80% threshold, D7 needs re-evaluation on a new plan cycle, not ad-hoc in T3. (RISK 6 adjacent.)

---

## Not flagged (explicitly concurred)

- D2 (hardcoded `data/raw/decline_interviews.jsonl`): concur
- D3 (batch-start `detection_timestamp`): concur
- D4 (`originating_model_version_returned` fallback semantics): concur
- D5 / D6 (verbatim prompt/response from originating step; template-reconstruction fallback flagged as RISK 1): concur; the RISK 1 flag is appropriate and the surface-to-Architect trigger in T1 dry-run is the right escalation path
- D7 ($2 hard cap, sequential execution) per the T1-dry-run precondition in binding note 8
- D8 (sequential execution at ≤30 calls): concur; async concurrency unjustified at this scale
- RISK 3 (`version_drift_flag` audit-only in v1): concur; Phase 4b+ territory
- RISK 5 (grok-4 inclusion as a v2 detector amendment on new plan cycle): concur
- T4 sited in `scripts/` not `cdb_analyze/` to avoid R12 ambiguity: concur — this is the right call even though the script is pure Python, because the precedent matters

---

## Memory updates pending

After T5 completion, I will update `.claude/agent-memory/cda_sme/project_cn_decline_clustering_phase4a.md` to reflect the Note K disposition (CONFIRMED / NOT CONFIRMED / INCONCLUSIVE / INCONCLUSIVE-SUGGESTIVE) and the final cross-tab structure. Memory file is currently correctly scoped as pre-remediation — no edit needed before T5.

---

*Posted to `#lsb-cda-sme`. Binding for T1–T5 unless superseded by a subsequent Architect plan cycle with SME re-review.*
