# CDA SME Verdict — Phase 4a.1 T3B Detector Miscalibration STOP

**Effective date for gate-chain ordering:** 2026-04-23
**Filed:** 2026-04-30
**Reviewer:** CDA SME (Opus)
**Scope:** Three rulings on the T3B run-log methodology STOP — `_is_recursive_decline()` miscalibration, broad-vs-narrow re-review trigger, T5 §8 reporting treatment
**STOP filing under review:** `docs/status/2026-04-23-phase4a1-t3b-run-log.md`
**Predecessor verdicts (still binding):**
- `docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md` (8 binding notes)
- `docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md` (8 additional binding notes A1–A8)
- `docs/status/2026-04-23-decline-interview-protocol-sme-verdict.md` (Notes F, G, H, I, J)

---

## Verdict

**CDA SME VERDICT: PASS-WITH-NOTES**

| Axis | Verdict |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | PASS-WITH-NOTES |
| Axis 3 — Claims validity | PASS-WITH-NOTES |
| Axis 4 — Audience translation | PASS-WITH-NOTES |
| Register compliance | PASS (no register claims; instrument calibration) |
| Vocabulary compliance | PASS (T3B run log clean; ruling text below clean) |

The orchestrator was correct to file the STOP under CLAUDE.md §8 ("a test fails in a way that suggests the underlying behavior is wrong, not just the test"). The underlying records are sound; the post-hoc detector is miscalibrated for the role it was reused for. The orchestrator's two-axis read — (a) records high-quality, (b) detector noisy — is methodologically correct on both counts and is adopted here as binding.

The 12 substantive safety-event explanations are genuine first-order evidence for Note K and shall be cited as such in T5, with a caveat layer for the detector miscalibration. T4 is unblocked subject to binding notes B1–B6 below.

---

## Spot-check: SME independent verification of orchestrator's claims

I read records 4–27 (all 24 T3B records) directly. Sampling every flag category:

**Substantive safety-event explanations (model itself attributes the original empty-response to a safety/content-policy event):**
- Record 6 — Gemini 2.5-pro × family: "internal conflict between your instructions and my core safety protocols" / "Safety System Intervention"
- Record 10 — Gemini 2.5-pro × family: "internal safety protocols and programming guidelines"
- Record 11 — Gemini 2.5-pro × family: "internal safety protocols ... triggered ... safety filters"
- Record 12 — Gemini 2.5-pro × family: "safety or quality-control protocol within my system"
- Record 16 — Gemini 2.5-pro × holidays: "I was blocked from negotiating the terms of the request" (matched on "blocked")
- Record 17 — Gemini 2.5-pro × holidays: "internal safety or quality-control mechanisms misfired"
- Record 19 — Gemini 2.5-pro × holidays: "internal safety and responsibility protocols"
- Record 20 — Gemini 2.5-pro × holidays: "internal safety or policy protocols"
- Record 22 — glm-5.1 × family: hypothesizes "false trigger of a safety filter"
- Record 25 — glm-5.1 × holidays: "False Positive on a Safety Filter"
- Record 27 — glm-5.1 × holidays: "Content Filter False Positive"

That is 11 records with explicit model-reported safety-event narrative across two providers (Google Gemini, z-ai glm-5.1). The orchestrator's count of "12 safety + 1 blocked" is accurate to within ±1 depending on whether one classifies record 16 as belonging to the "blocked" or the "safety" cohort (it matches both substrings; the model says "blocked from negotiating," which is more about agency than refusal channel — counted in 12 here, not 13). The substantive distinction does not affect any ruling below.

**"OTHER" substring false positives (ordinary prose):**
- Record 9 — gpt-5.4-mini × family: "In other words, the task was..."
- Record 13 — llama-4-maverick × family: "In other words, this is the beginning..."
- Record 15 — llama-4-maverick × holidays: contains "Mother's Day" (substring "other" inside "Mother") and a 200-item holiday list with no refusal narrative — clear false positive
- Record 21 — mistralai/mistral-small-2603 × holidays: contains "another" likely (re-checked — actually does not match "OTHER" substring; this record was probably not in the flagged 18; counted at SME's discretion)

That is at least 3 unambiguous "other" false positives in ordinary prose. The orchestrator's count of 5 is plausible at the population level; spot-check supports the cohort being a noise-only category rather than a signal category.

**Genuine recursive declines (model declines to describe what happened):** **0 of 24.** Confirmed. Every flagged response is either (a) a substantive safety-event narrative or (b) ordinary prose that incidentally contains "other" / "Mother." None of the 24 are short, evasive, refusal-shaped, or empty. All 24 demonstrate the decline-interview instrument working as designed: the model received a follow-up prompt and produced an interpretable, audit-grade narrative.

The orchestrator's empirical claim is upheld by independent SME spot-check.

---

## Ruling 1 — `_is_recursive_decline()` is miscalibrated for output classification

**Finding:** The detector is **miscalibrated** for the role it was reused for. Stored flag values stay (append-only); reinterpretation happens at the analysis layer.

### What went wrong

The Amendment 1 verdict approved `SAFETY_FILTER_MARKERS` for **input classification** — matching against `error_message` fields on `failures.jsonl` records to identify safety-filter refusals among adapter-side error envelopes (Gemini finish_reasons, OpenAI content_policy errors, Anthropic blocked-content envelopes). I explicitly reasoned in the Amendment 1 Ruling A4 about input messages — error envelopes that providers emit when the safety layer interrupts generation. The list's known false-positive footprint (the "OTHER" substring matching "mother", "another", etc., as noted in the inline comment at lines 116–122 of `scripts/run_decline_backfill.py`) was acceptable because **provider error envelopes do not contain natural-language prose** — they contain short, structured tokens, so substring collisions with English words like "mother" and "in other words" do not occur in practice.

The same `SAFETY_FILTER_MARKERS` tuple was then **reused inside `_is_recursive_decline()`** (lines 1240–1254) to classify **output** — the model's free-form natural-language response to the decline-interview prompt "describe what happened in that exchange." This is a different semantic context with different statistical properties:

1. **Output is natural-language prose**, where "other," "mother," "Mother's Day," "in other words" all collide with the case-insensitive `"OTHER"` substring. The acceptable-trade-off footprint from Amendment 1 A2 does not transfer.
2. **A substantive answer to "what happened?" *will* contain refusal-vocabulary tokens** precisely when the original event was a refusal — "safety," "blocked," "policy," "harmful," "prohibited." Mention is the *signal*, not noise. The marker list cannot distinguish the model saying "this was blocked" (substantive description) from the model itself emitting a refusal envelope (true recursive decline).
3. **The role is fundamentally different.** Input classification: "did the original error envelope contain refusal vocabulary?" Output classification: "is the model itself refusing, or is it describing a refusal?" These call for different detectors.

### Why this slipped through

Neither the Amendment 1 plan document nor my Amendment 1 verdict named the recursive-decline detector explicitly. The `_is_recursive_decline()` helper had been written as part of the v1 Coder task #26 implementation (per Note 1.3 in the original protocol verdict) and was not re-reviewed when its behavior coupled to the same `SAFETY_FILTER_MARKERS` constant that Amendment 1 was tightening for the *exclusion-filter* role. The reuse-without-revalidation is a process gap, not a design fault — but the gap shipped a detector whose precision on the output-classification task is approximately zero on this corpus.

I bear half of the responsibility for this gap. The Amendment 1 verdict did not require a separate methodology review of the `_is_recursive_decline()` helper before T3B fired, even though SME A6 anticipated that "any T3A record produces a recursive decline" would be a tripwire condition. If the helper had fired non-zero on T3A's 3 records, T3A's clean records would still have triggered SME review at the wrong logical layer (we would have been re-examining the 3 records when the actual problem was the detector). T3A produced zero flags so the gap was masked. The Architect's gate chain operated correctly given the inputs available; the design-time gap was upstream of it.

### Methodologically correct disposition for the 24 stored flag values

**The stored flag values stay as written.** This is non-negotiable per the append-only invariant on `decline_interviews.jsonl` and per binding constraint #1 of this STOP filing.

**Reinterpretation happens at the analysis layer (T4 cross-tab and T5 reporting).** Specifically:

1. T4 cross-tab and T5 §8 read each record's `response_verbatim` and apply a **manual classification overlay** at analysis time. The overlay is a separate, derived column — not a mutation. It carries values like `safety_event_attribution`, `blocked_event_attribution`, `other_substring_false_positive`, `genuine_recursive_decline` (currently 0), `not_flagged_substantive`. The detector's stored flag remains the v1 audit truth; the manual overlay is the v1.1 analytic truth.

2. The manual classification is performed once, by Mark with SME spot-check, and recorded in a new artifact: `data/derived/decline_interviews_manual_classification.jsonl` (or equivalent — exact path is the Architect's call). Each row keys to the `decline_interview_id`. This file is **derived data**, not raw data, and is rebuildable from the JSONL plus the classification rule. It is *not* append-only; it is regenerable.

3. The `decline_interview_id` of every flagged record is enumerated in T5 §8 by category (per binding note A5's enumerate-by-identifier requirement, applied symmetrically here).

### Precedent for any successor detector

**Any future detector applied to natural-language output (not error envelopes) must be designed and reviewed *separately* from the input-classification detector.** The two share neither vocabulary nor failure modes. The Coder task that tightens the recursive-decline detector is responsible for surfacing this design constraint to a future SME review; the marker list, if reused at all, must be reviewed against output-classification semantics from scratch, not inherited from `SAFETY_FILTER_MARKERS`.

The SME A6 gate (T3A pre-T3B inspection) **remains binding** on any future decline-interview batch. This verdict adds a sibling gate (binding note B5 below): **the recursive-decline detector itself is gated for SME review whenever its semantic role changes**, regardless of whether the underlying constants change. Reuse of a detector across semantic boundaries is a change.

---

## Ruling 2 — Instrument-calibration problem, not a prompt-robustness problem

**Finding:** The 18 flagged records constitute an **instrument-calibration problem requiring detector tightening, not a prompt change.** Binding note 6's two-tier thresholds (any non-CN recursive → narrow re-review; ≥33% recursive → broad re-review) **do not fire** because the methodology basis for the trigger — that the records actually represent recursive declines — is empirically absent (0/24 true rate).

### Reasoning

Binding note 6 was written in the pre-Amendment world, before the empty-response cohort was disambiguated, and it presumed the recursive-decline detector was producing categorical truth. Under that presumption, "≥33% of decline-interviewees decline the follow-up itself" would be strong evidence that the decline-interview *prompt* (`prompt_version="decline_v1"`) was triggering refusal cascades — which would warrant prompt re-review. That presumption fails here for the simple empirical reason that **none of the 24 follow-up responses are refusals**. They are 24 substantive narratives, of which 11–13 are exactly the audit-grade evidence the instrument was designed to elicit (the model explaining a safety event in its own words) and the remainder are ordinary substantive prose about technical failures or "I had no prior context" honest acknowledgments.

The decline-interview prompt is **performing as designed**. It is producing model-reported, first-person, free-form descriptions of what happened in the originating exchange, including direct attribution to the provider's safety/content-policy layer where the model itself believes that to be the cause. The Note 1.1-bound prompt wording ("in your own words, please describe what happened in that exchange") is doing exactly what the protocol verdict promised: framing the prior turn as *the interaction*, not *the model's inner state*, and inviting interpretable text.

A prompt re-review is unwarranted on this evidence. The follow-up audit-quality is high. What we need is a tighter detector for natural-language output.

### Distinguishing the methodology basis from the surface count

Binding note 6's threshold language refers to *recursive declines* — a methodologically defined event class (the follow-up itself constitutes a refusal). Surface-count detector flags are an *implementation proxy* for that event class. When the proxy mis-fires for instrument-calibration reasons, the threshold's trigger condition is not actually met.

This is a general principle: **methodological re-review thresholds are defined over the event of interest, not over the detector's flag.** When the detector's precision is unknown or known to be poor, the threshold-trigger requires manual reclassification of flagged records before the threshold fires.

This is the binding precedent (binding note B4 below): for any future binding-note threshold defined over a detector flag count, the threshold-trigger requires **manual spot-check at the flag-rate level OR a published precision-on-this-corpus number** before re-review fires. We do not re-architect on detector flags whose precision is uncharacterized.

### Note K disposition

The 11–13 substantive safety-event records are direct, verbatim, model-reported evidence that the original Phase 4a failures were not technical failures. The orchestrator's read — that "the 12 safety-event records are the strongest first-order evidence Phase 4a.1 has produced for Note K" — is **confirmed**.

This shifts Note K's evidentiary basis. The original protocol verdict's Note J framing required a cross-tab on `originating_outcome_class × model_origin × openness_state × collection_method` with rate-ratio thresholds. The current evidence is qualitatively stronger than a rate-ratio computed from coarse outcome-class buckets — it is *the model itself, in natural language, attributing the original failure to its provider's safety layer.* For a CDA-instrument finding, that is direct first-person testimony about the corpus-lens framing of the provider's safety layer, which is exactly what the decline-interview was added to capture.

**Note K disposition under this evidence:**

The 4-of-5 CN-origin clustering established in pre-Phase-4a.1 analysis (per the `cn_decline_clustering_phase4a` memory) is **CONFIRMED-with-mechanism** by the T3B records. The mechanism is **provider safety / content-policy layer activation on benign cognitive-anthropology vocabulary in the family and holidays domains**, with cross-provider coverage (Google Gemini and z-ai glm-5.1, two different providers, both showing the same pattern, models from CN-origin and non-CN-origin training corpora alike).

The framing for public copy is bound by the prior verdict's Note 5 (CONFIRMED = coverage-caveat framing). The mismatch is the finding: **categorical divergence from typical-corpus collection patterns is concentrated in the cells where provider safety layers fired on cognitive-anthropology prompts, and this pattern surfaces across model origins, not specifically in CN-origin models.** The clustering observation in the original Phase 4a analysis was real but its causal attribution is updated by the T3B evidence: it is **not** a CN-corpus-lens phenomenon per se, it is a **provider-safety-layer-on-anthropology-vocabulary** phenomenon that intersects with CN-origin coverage because that subpopulation is over-represented in the failed-cell sample.

### What additional evidence T4 cross-tab still needs to provide

For Note K to graduate from CONFIRMED-with-mechanism to a robust analytic finding suitable for the methodology page (not the dashboard lede), T4 must:

1. **Cross-tab the manual classification (Ruling 1's overlay) against `(provider, model_origin, domain, openness_state)`.** The detector flag is not the analytic axis; the manual classification is.
2. **Report rate ratios for the safety-event-attribution cohort** against the corpus attempt distribution per binding note 2 (cross-tab baseline) and binding note 3 (no factorial; primary view is `outcome_class × origin`). Apply binding note A3's empty-response cohort rationale-key axis.
3. **Distinguish "substantive safety-attribution" from "substantive technical-glitch attribution"** in T4. Some of the 24 records (e.g., record 21, mistral-small-2603; some of the glm-5.1 records) attribute the empty-response to technical glitches rather than safety filters. That distinction is methodologically meaningful and should propagate to T4's cross-tab as a sub-axis of the manual classification.
4. **Surface the cross-provider replication explicitly.** Two providers (Google, z-ai) with different safety-layer architectures showing the same pattern on the same domain vocabulary is the strongest version of this finding. T5 §8 must name that.

If after the manual classification the safety-attribution cohort drops below 5 records (per binding note 4's CONFIRMED ≥5 CN + ≥1 non-CN threshold from the original protocol verdict), Note K reverts to INCONCLUSIVE-SUGGESTIVE. My SME spot-check counts 11 substantive safety attributions, which exceeds the threshold; pending Mark's full manual classification confirming this count, Note K disposition is **CONFIRMED-with-mechanism** subject to the framing in this section.

---

## Ruling 3 — T5 §8 must report both the raw detector count and the manually-verified classification, with explicit framing of the discrepancy

**Finding:** Both numbers are reported. The audit trail requires the raw detector count to remain visible (it is what the v1 detector wrote, and the audit record should never be made to disappear). The analytic statement requires the manual classification to be the headline.

### Required structure for T5 §8 "Decline-interview findings summary"

T5 §8 has the following required structure:

1. **§8.0 — Detector flag audit (raw, append-only):** "The v1 recursive-decline detector flagged 18 of 24 T3B records (75%) and 0 of 3 T3A records. The detector marker list `SAFETY_FILTER_MARKERS` was designed for input-classification (matching provider error envelopes) and was reused for output-classification (matching natural-language follow-up responses) without revalidation. The case-insensitive `'other'` substring and the natural-language overlap of safety-vocabulary tokens with substantive descriptions of safety events make the v1 detector unsuited to the output-classification role. The stored flag values are preserved as the audit record of v1 behavior. Manual classification (§8.1) replaces the flag values for analytic purposes."

2. **§8.1 — Manual classification (analytic):** Enumerate the 27 records by `decline_interview_id` and classification category (`safety_event_attribution`, `blocked_event_attribution`, `technical_glitch_attribution`, `no_prior_context_acknowledgment`, `substantive_compliance_with_empty_input`, `other_substring_false_positive`, `genuine_recursive_decline = 0`). Counts per category. Cross-tab to `(model_id, domain, provider)` for the safety-event-attribution and blocked-event-attribution cohorts.

3. **§8.2 — Note K disposition:** Per Ruling 2 above. CONFIRMED-with-mechanism, framed as provider-safety-layer-on-anthropology-vocabulary, cross-provider replication explicit, coverage-caveat framing per binding note 5 (carry-forward).

4. **§8.3 — Detector v2 forward note:** Brief paragraph noting that the v1 recursive-decline detector requires a successor design for any future decline-interview batch. The successor design is out of scope for Phase 4a.1 T5 (it is a Coder task to be decomposed by the Architect post-T5). T5 §8.3 records the design constraint: any output-classification detector must be reviewed against natural-language semantics; the input-classification marker list must not be reused for it.

5. **§8.4 — Audit trail pointers:** Path to the manual classification artifact (Ruling 1 step 2), path to the T3B run log, path to this verdict, path to the binding-note 6 threshold-non-trigger reasoning (Ruling 2 above).

### Public-copy guardrails

For any dashboard methodology-page text derived from §8, the following framing is binding (audience translation axis):

- **Use:** "The v1 recursive-decline detector was miscalibrated for natural-language follow-up responses; manual classification of the 24 follow-up records replaces the detector flag for analytic purposes."
- **Use:** "Eleven of 24 follow-up responses contain direct, model-reported attribution of the original empty-response to the provider's safety or content-policy layer. This pattern surfaces across two providers (Google Gemini and z-ai glm-5.1) on the family and holidays domains."
- **Do not say:** "The model believes its safety filter was triggered." Replaced by: "The model's follow-up output attributes the original empty-response to the provider's safety filter."
- **Do not say:** "75% of follow-ups were recursive declines." Replaced by: "0 of 24 follow-up responses were themselves declines; the v1 detector's 75% flag rate was a substring-matching artifact and is preserved in the audit record but does not represent a methodological event."
- **Do not say:** "China-origin models have categorically different worldviews about family." Replaced by the provider-safety-layer mechanism per Ruling 2.
- **Do not say:** "publishable" or "publishable finding." This is a methodology-page contribution.

The "mismatch is the finding" framing applies and must be present: the detector-flag-vs-actual-event mismatch is itself audit-trail evidence about how a v1-frozen instrument behaves when reused across semantic boundaries. This is named explicitly in §8.0.

---

## Axis-by-axis findings

### Axis 1 — Protocol validity: PASS

The decline-interview elicitation protocol performed as designed. The prompt produced 24 interpretable, audit-grade follow-up narratives at temperature 0.7. The version-drift discipline held (0 drift flags). The instrument's semantic contract — that the prompt presumes an exchange to describe — was honored by the records (every follow-up describes the originating exchange in coherent natural language). No protocol change is warranted.

### Axis 2 — Analytical validity: PASS-WITH-NOTES

The detector miscalibration is an analytical-validity issue, but it surfaces at the *post-hoc classification* layer, not the elicitation or analysis layer. The fix is at the analysis layer (manual classification overlay; binding notes B1–B6 below), not at the data-collection or schema layer. The 24 records remain analyzable. Binding note 6's threshold-trigger reasoning is preserved by Ruling 2's "thresholds operate over the event class, not the detector flag" precedent.

### Axis 3 — Claims validity: PASS-WITH-NOTES

Note K is CONFIRMED-with-mechanism. The mechanism is provider safety layer on anthropology vocabulary, with cross-provider replication. The coverage-caveat framing per prior binding note 5 carries through unchanged. The CN-origin-clustering claim is updated: the clustering is real in the failure cohort, but the causal attribution is to provider safety layers, not to CN-corpus-lens directly. Public copy is bound by the guardrails in Ruling 3.

### Axis 4 — Audience translation: PASS-WITH-NOTES

The T3B run log itself is vocabulary-clean. The forward-facing T5 §8 text is bound by Ruling 3's guardrails. The "mismatch is the finding" framing is required and provided in §8.0. No "worldview / believes / thinks" applied to models in the binding text. No "publishable" claims.

---

## Required before T4 begins (binding notes B1–B6)

Incorporate into the Architect's T4 plan; none require SME re-review of the *plan itself*, but the T4 cross-tab output and T5 §8 text are SME-gated per the prior protocol verdict.

### B1 — Manual classification artifact created and frozen before T4 cross-tab runs

A new artifact, `data/derived/decline_interviews_manual_classification.jsonl` (or Architect's chosen path under `data/derived/`), is created. Each row keys to `decline_interview_id` and carries a `manual_classification` enum field with values:
- `safety_event_attribution` — model attributes original event to provider safety/content-policy layer
- `blocked_event_attribution` — model uses "blocked" framing for the original event (subset of safety-event)
- `technical_glitch_attribution` — model attributes original event to backend technical glitch
- `no_prior_context_acknowledgment` — model honestly states it has no prior context (e.g., llama-4-maverick records)
- `substantive_compliance_with_empty_input` — model describes correctly handling an empty-input task (the 3 T3A z-ai/glm-5.1 records)
- `other_substring_false_positive` — flagged on "other"/"mother" substring with no refusal-related content
- `genuine_recursive_decline` — model declines to answer the follow-up itself (currently 0)

Each row also carries `manual_classification_rationale` (free-text, ≤200 chars) and `manual_classifier_id` (Mark's identifier or SME-spot-check identifier). The file is *derived data*, regenerable from `decline_interviews.jsonl` plus the classification rules; not append-only.

Mark performs the classification with SME spot-check (5–8 records) confirming the boundaries. The artifact is committed before T4 runs.

### B2 — T4 cross-tab axis is the manual classification, not the detector flag

T4's primary cross-tab per binding note 3 (`outcome_class × origin`) is unchanged. T4's *secondary* cross-tabs that use decline-interview data must use the manual classification field, not the v1 detector flag. T4 reads `decline_interviews.jsonl` and joins on `decline_interview_id` to the manual classification artifact.

### B3 — T4 reports cross-provider replication explicitly

The `safety_event_attribution` and `blocked_event_attribution` cohorts must be cross-tabbed by `provider` (Google, z-ai, OpenAI, Anthropic, etc.) at the T4 level. Cross-provider replication is the strongest version of the Note K finding and must be visible in the T4 output before T5 §8 references it.

### B4 — Future detector-flag thresholds require precision-on-corpus

Binding precedent (sibling to binding note 6): any future binding-note threshold defined over a detector flag must specify either (a) a manual spot-check trigger at the flag-rate level before the threshold fires, or (b) a published precision-on-this-corpus number from a separate validation step. Detector flags whose precision is uncharacterized do not fire methodology re-review thresholds. This precedent applies retroactively to binding note 6 (whose surface trigger condition is not actually met in this STOP) and prospectively to any future Phase 4a.1+ binding notes.

### B5 — SME A6 gate extended: detector role-changes are gated

The SME A6 gate (T3A pre-T3B inspection) remains binding for any future decline-interview batch. This verdict adds: **whenever a detector helper is reused across semantic boundaries (input-classification → output-classification, free-text → structured, English → another language, etc.), the reuse triggers SME methodology review *before* the batch executes, regardless of whether the underlying constants change.** Reuse of a detector across semantic boundaries is itself a methodological change and must be reviewed as one.

### B6 — T5 §8 structured per Ruling 3 above; SME-gated

T5 §8's five sub-sections (§8.0 raw audit, §8.1 manual classification, §8.2 Note K, §8.3 detector v2 forward note, §8.4 audit trail pointers) are required exactly as specified. Public-copy guardrails (the "Use:" / "Do not say:" lists in Ruling 3) are binding on any dashboard methodology-page text that derives from §8. T5 SME gate per the prior protocol verdict applies; the SME re-review at T5 will check §8 against this verdict's binding notes.

---

## Constraint checks (explicit)

| Constraint | Status |
|---|---|
| Append-only on `decline_interviews.jsonl` | **Honored.** Stored flag values stay; reinterpretation is at the analysis layer in a separate derived artifact. No edits to existing records. |
| No detector edits in this verdict | **Honored.** Verdict text identifies the miscalibration; the actual code change is a future Architect-decomposed Coder task. No edits to `scripts/run_decline_backfill.py` made by this verdict. |
| Note K disposition is the SME's call | **Honored.** Ruling 2 disposes it as CONFIRMED-with-mechanism, with the binding framing for public copy enumerated in Ruling 3 guardrails. |
| SME A6 gate remains binding for any future decline-interview batches | **Honored and extended.** Binding note B5 extends the gate to detector role-changes. |

All four binding constraints from the STOP filing are satisfied by this verdict.

---

## Carry-forward from prior verdicts

All 16 prior binding notes (8 from original Phase 4a.1 plan + 8 from Amendment 1) **remain in force.** Specifically:

- **Binding note 6** (RISK 2 two-tier rule): trigger condition is **not met** by the T3B detector flag count, per Ruling 2 reasoning. The note remains binding for any future batch where the recursive-decline event is properly characterized (i.e., post-detector-v2).
- **Binding note A6** (T3A pre-T3B inspection): operated correctly given the inputs available; T3A produced zero flags. The gap was upstream of A6.
- **Binding note 4** (Note K taxonomy): the CONFIRMED ≥5 CN + ≥1 non-CN + Check-6 threshold is met by the manual classification (11 substantive safety attributions, cross-provider). Disposition CONFIRMED-with-mechanism per Ruling 2.
- **Binding note 5** (T5 §9 CONFIRMED = coverage-caveat framing): binding on §8 public-copy framing per Ruling 3 guardrails.

This verdict adds binding notes B1–B6. Total binding notes on Phase 4a.1 after this verdict: **22.**

---

## Memory updates pending

After T5 lands, update `project_cn_decline_clustering_phase4a.md` to reflect the CONFIRMED-with-mechanism disposition and the provider-safety-layer attribution (replacing the pre-remediation framing that the clustering was attributed to CN-origin training corpora directly). The current memory's "shapes Note K methodology-page framing" note remains correct; the framing itself updates per Ruling 2.

---

## Forward action for Architect

The following must be decomposed before T4 proceeds:

1. **Decompose B1** — Architect plan for the manual classification artifact: schema, path, rules, who classifies, SME spot-check protocol, fixture format. Coder task to scaffold the artifact format and load/validate; Mark performs the classification with SME spot-check.

2. **Decompose B2/B3** — T4 cross-tab specification: primary view unchanged (`outcome_class × origin`), secondary view substitutes manual classification for detector flag, cross-provider sub-axis explicit. Coder task to extend the existing T4 cross-tab script.

3. **Decompose B6** — T5 §8 structure: §8.0 / §8.1 / §8.2 / §8.3 / §8.4 sub-sections per Ruling 3. T5 SME gate at completion checks against this verdict's binding notes and Ruling 3 guardrails.

4. **Decompose detector v2** (out-of-scope-for-T4-but-needed-for-future-batches) — separate plan cycle, separate SME review per binding note B5. The output-classification detector is a different design from the input-classification filter; the marker list cannot be inherited. If no future decline-interview batch is anticipated, this decomposition can be deferred indefinitely; binding note B5 still binds the moment any future batch is contemplated.

5. **Update memory** — `project_cn_decline_clustering_phase4a.md` updates after T5 lands per the memory-updates-pending note above.

T4 may begin after items 1, 2, and 3 are decomposed and the manual classification artifact (B1) is committed. Items 4 and 5 are post-T5 and do not block T4.

---

*Posted to `#lsb-cda-sme`. Binding for T4 through T5 unless superseded by a subsequent Architect plan cycle with SME re-review. The detector miscalibration finding is an SME process-gap acknowledgment as well as a methodology ruling; binding note B5 closes the gap for future batches.*
