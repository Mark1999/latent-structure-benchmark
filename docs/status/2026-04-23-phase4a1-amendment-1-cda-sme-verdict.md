# CDA SME Verdict — Phase 4a.1 Architect Plan Amendment 1 (task #21)

**Date:** 2026-04-23
**Reviewer:** CDA SME (Opus)
**Scope:** Architect's Amendment 1 to Phase 4a.1 decomposition — exclusion criteria rule (§2), batch split (§3), cost-cap raise (§4), amended binding note 8
**Predecessor verdict (still binding, additive):** `docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md`
**Plan document under review:** `docs/status/2026-04-23-phase4a1-architect-plan-amendment-1.md`

---

## Verdict

**CDA SME VERDICT: PASS-WITH-NOTES**

| Axis | Verdict |
|---|---|
| Axis 1 — Protocol validity | PASS-WITH-NOTES |
| Axis 2 — Analytical validity | PASS-WITH-NOTES |
| Axis 3 — Claims validity | PASS-WITH-NOTES |
| Axis 4 — Audience translation | PASS |
| Register compliance | PASS (no register claims; pre-session audit-and-elicitation work only) |
| Vocabulary compliance | PASS (amendment text clean; no forbidden tokens) |

The amendment is methodologically sound. The general exclusion principle is correct. The Gemini empty-response disposition is correct. The safety-filter-override-of-infrastructure priority is correct. Default-include-unclassified is correct. Cap raise, batch split, and `--source` flag are correctly scoped as Reviewer-sufficient. Binding notes below tighten the audit trail, lock in a rationale taxonomy that survives v2 revisions, require the empty-response cohort to carry a distinguishing label on the decline-interview record, and require T3A to be analyzed for recursive-decline signals before T3B fires. None require SME re-review of the amendment; all are incorporation-into-spec items.

Prior 8 SME binding notes (2026-04-23 verdict) remain binding in full. Prior note 8 is explicitly amended by Amendment 1 §4 and I accept that amendment subject to binding note A8 below.

---

## Rulings on the Architect's seven questions

### Ruling A1 — General principle: exclude HTTP-infrastructure, include safety-filter refusals

**Concur. Binding.**

The decline-interview instrument's prompt presumes an exchange to describe. Records in which no model-generated exchange occurred (transport error, malformed payload, pre-generation adapter crash) have no exchange — asking the model to describe one fabricates narrative rather than captures audit data. Excluding HTTP-infrastructure failures is the right call: they are operator/network events, not refusal events.

Records in which the provider's safety / content-policy layer returned an error in lieu of generation **are** refusals in the CDA-instrument sense — they carry information about the effective corpus-lens framing of the provider's safety layer, which is exactly what the decline-interview instrument exists to surface. Including them is correct.

The cross-provider reality that safety blocks surface through multiple channels (HTTPStatusError with body, finish_reason sentinel, custom exception class, sometimes empty-response) means **message-substring detection is the reliable channel-agnostic filter**. The Architect's substring list is well-chosen: it covers Gemini's `RECITATION` / `SAFETY` / `PROHIBITED_CONTENT` / `OTHER` finish_reasons, OpenAI-shape `content_policy` / `content_filter`, Anthropic-shape `blocked` / `harmful` / `prohibited`, and the generic `safety` catch. I would add one marker — see binding note A2.

**The principle is correct. The exclusion happens at filter-at-consume, not at detector. The detector (`decline_detection.py`) remains v1-frozen. Concur with the architecture.**

### Ruling A2 — Gemini 10 empty-response-after-3-retries disposition

**INCLUDE with a distinguishing label on the record. Binding.**

The Gemini cohort is the most important call in this amendment — 10 records out of the ~27 post-exclusion population. I rule:

1. **Include them.** The probability-weighted best explanation across the three candidate mechanisms (silent safety-block, transport stripping, model-returns-nothing) is dominated by (a) — Gemini's T1 jailbreak refusal surfaced through the same empty-response channel, per the current operational note in the amendment. Excluding them would discard the most likely refusal cohort in the population on the weakest-evidence mechanism.

2. **But attach a distinguishing rationale string** so the record class is traceable downstream. The Architect's current rationale string for these records routes through step 4.4 `parse_exhaustion:Could not extract valid JSON`. That conflates them with the ~14 non-empty partial-output parse-exhaustion records, which have a different evidential footing (those clearly generated; Gemini empty-responses arguably didn't).

**Binding requirement:** add a dedicated classification branch **before step 4.4** that catches empty-or-whitespace-only response fragments in `error_message` for `error_type == "ValueError"`. The rationale string must be `empty_response:likely_silent_safety_block` or equivalent stable identifier. This preserves the INCLUDE decision while letting T4's cross-tab, T5's §9 alternative-explanation review, and any v2 detector revision distinguish this cohort from the partial-output parse exhaustions. See binding note A3.

3. **Propagate the distinction into the `DeclineInterview` record.** When T2 runs the decline interview on a Gemini-empty-response record, the resulting `DeclineInterview.originating_outcome_class` inherits whatever the detector assigned, which is correct and I do not want altered. But the filter rationale string must be preserved on the T2 skip/include log and surface in T5 §5 "Exclusion rule applied" subsection by identifier, so that downstream analysis can segregate empty-response-likely-safety-block from degenerate-partial-output. See binding note A5.

**Do not overrule. Include.** The alternative — excluding 10 of ~27 records on a mechanism-hypothesis that is probably wrong — would be methodologically worse than including them with a label that allows later reclassification. The filter is at-consume; nothing is lost by including and labeling.

### Ruling A3 — Default-include-unclassified policy (step 4.5 of decision tree)

**Concur. Default-include is the correct posture. Binding with tightening.**

The amendment's default-include-with-rationale-and-surface-to-SME policy is the right call for this instrument, for three reasons:

1. **The instrument's purpose is audit.** A decline-interview that runs on a record-type the filter didn't anticipate is not a bug — it's a data point that tells us the filter's taxonomy has a gap. Default-exclude would silently suppress that signal.

2. **The cost ceiling is bounded.** With the $10 cap and ~$0.05/call, default-include on an exotic class of records cannot run away financially. The operational failure mode of over-inclusion is recoverable; the methodological failure mode of under-inclusion (silently discarding refusal evidence) is not.

3. **The filter is consumer-side.** `failures.jsonl` is append-only, the detector is v1-frozen, and nothing in the include decision mutates the source record. An over-inclusion is recoverable by tightening the filter on a future Architect plan cycle; an under-inclusion loses the record to the audit trail until someone re-runs T3 with a broadened filter.

**Tightening (binding note A4):** the `unclassified:default_include` bucket must be **dry-run-blocking at a small threshold** — specifically, if more than **2** records in a batch fall into `unclassified:default_include`, T1-update dry-run surfaces it as an "unclassified-saturation" warning in Section 3c and requests SME review before T3 proceeds. Rationale: a single oddity is fine to pass through; three or more unclassified records means the taxonomy has drifted under us and the filter needs a plan cycle, not an execution.

### Ruling A4 — Safety-filter-override priority (step 4.1 runs before HTTP-infrastructure exclusion)

**Concur. Binding.**

The ordering is correct. Some providers surface safety blocks as HTTP 400 with the refusal content in the response body / error message (OpenAI does this on some endpoints for policy-violations; Anthropic has historically returned 400 with `type: "invalid_request_error"` wrapping a content-policy message). If HTTP-infrastructure exclusion fired first, those records would be wrongly excluded.

Running the safety-filter substring check *before* the infrastructure exclusion is the right precedence. The message-substring is the primary classifier; the exception-type is the fallback. **Concur.**

One binding tightening — see binding note A2 below: the substring list needs one additional marker, `jailbreak`, which has appeared in at least one provider's refusal envelope historically and is a canonical refusal-vocabulary term.

### Ruling A5 — Cap raise + batch split + `--source` flag: Reviewer-sufficient

**Concur. Not methodology.**

- **Cap raise $2 → $10.** Infrastructure parameter. The methodology-substantive input that justifies the raise is §2 (exclusion rule), which I am gating. The raise itself is Mark's call on operational budget. CLI-parameterization via `--cost-cap-usd` is good practice. Reviewer-sufficient.

- **Batch split T3A / T3B.** Operational sequencing. The methodologically relevant fact is that T3A runs on the 3 informants-origin records first, which surfaces any recursive-decline or prompt-failure signal on a small controlled population before the larger T3B batch commits. That is good risk management. See binding note A6 for the one tightening I want.

- **`--source {informants, failures, all}` flag.** Mechanical. Default `all` preserves backward compatibility. Reviewer-sufficient.

### Ruling A6 — Amendment to binding note 8

**Accept the amendment with one tightening. Binding note A8 below.**

The amendment:
- Pre-flight threshold $1.60 → $8.00 (80% of new $10 cap)
- Dry-run reports both full detected-session count AND post-exclusion count
- Prior $2 cap STOP has fired once and been resolved via this amendment
- Future escalations still require a new plan cycle

These are correct adjustments. The pre-flight still fires at 80% of cap, the threshold remains an early-warning rather than a soft-fail-at-the-cap, and the "one STOP fired, future STOPs still need re-plan" framing is exactly the right posture — this amendment is not a license to raise the cap again without methodology review.

**Tightening:** the dry-run must report **both** cost projections (against full detected-session count AND against post-exclusion count) so that if the post-exclusion count is low but the exclusion rule itself is later revised to be less restrictive (say, on T3B re-run after T3A surprises), the operator has the raw-count projection on hand and does not need to re-run T1-update just to regenerate it. See binding note A8.

### Ruling A7 — Additional binding notes

Seven additional binding notes attached to this amendment, enumerated in "Required before T1-update begins" below.

---

## Constraint checks (explicit)

| Constraint | Status |
|---|---|
| Detector (`decline_detection.py`) is v1-frozen — exclusion is a post-detection filter at consume | **Honored.** Amendment §1 explicitly states "Unchanged. Exclusion is a post-detection filter at consume time." Filter lives in `scripts/run_decline_backfill.py`, not in the detector. Concur. |
| `failures.jsonl` remains append-only; filter is at-consume | **Honored.** Amendment §1 and §2 both state filter-at-consume, no delete. Concur. |
| No schema changes | **Honored.** Amendment §1 explicitly confirms `DeclineInterview` and `InformantRecord` untouched. Concur. |
| No new LLM imports (R12) | **Honored.** `scripts/run_decline_backfill.py` is a runner, not an analyzer; `should_include_failure` is pure-Python string/set operations with no LLM client imports. Concur. |

All four binding constraints from the prompt are satisfied by the amendment as written.

---

## Axis-by-axis findings

### Axis 1 — Protocol validity: PASS-WITH-NOTES

The exclusion rule correctly honors the decline-interview instrument's semantic contract (the prompt presumes an exchange; records with no exchange have nothing to describe). The safety-filter-as-refusal framing is correct: safety blocks are categorical events in the CDA sense, and the decline-interview is the correct instrument to interrogate them. The filter-at-consume siting (not filter-at-detector) preserves the v1-frozen contract and the append-only invariant.

One protocol point I want surfaced in the T1-update Section 3b/3c output, not just in T5: the **rationale string must carry a stable taxonomy** so that if T3B runs after T3A and the SME / Mark want to reclassify a record class, the grep-target survives. See binding note A3 (empty-response cohort gets its own rationale key) and binding note A7 (rationale taxonomy is documented as a controlled vocabulary in Section 3b's header).

### Axis 2 — Analytical validity: PASS-WITH-NOTES

The rule is a pure, deterministic, testable classifier over explicit categorical inputs. It does not estimate, it does not use a statistic, and it does not have an implicit threshold that would destabilize under small-n. The review-rigor-on-thresholds memory does not bind here because this is not a rank/correlation/eigenvalue threshold — it is a discrete categorical filter on string equality and substring containment.

The one analytic concern is that if the `unclassified:default_include` bucket fills up unexpectedly, the filter's taxonomy has drifted out from under the batch. Binding note A4 addresses this by making the bucket dry-run-blocking above 2 records.

The second analytic concern is the cohort-labeling for the Gemini empty-response records: if they flow into T4's cross-tab under an undifferentiated parse-exhaustion rationale, the cross-tab cannot segregate "model generated and we couldn't parse it" from "model may have silently safety-blocked." Those are different analytic populations. Binding note A3 fixes this by giving them their own rationale key.

### Axis 3 — Claims validity: PASS-WITH-NOTES

The amendment makes no claims about model behavior, cultural structure, or corpus lens. It is purely an operational scope-trim. The one claims-adjacent item is that excluded records are documented in T5 §5 "Exclusion rule applied" — see binding note A5, which tightens the T5 §5 requirement to enumerate excluded records **by identifier**, not just by rationale-bucket count, so that the audit trail is reproducible. This is the T5 equivalent of the prior verdict's ruling 3 (enumerate grok-4 deferred records by model/domain/step).

The NOT-CONFIRMED / INCONCLUSIVE / INCONCLUSIVE-SUGGESTIVE Note K taxonomy from the prior verdict remains binding and unchanged by this amendment. If the post-exclusion cohort produces too few non-CN decline records to compute a rate ratio, Note K defaults to INCONCLUSIVE per the prior ruling 2b; the amendment does not alter this.

### Axis 4 — Audience translation: PASS

Amendment text is vocabulary-clean. No "worldview / believes / thinks" applied to models. No "within-model consensus." Uses "corpus-lens framing" correctly in §2 when describing what safety-filter refusals carry information about. No publishability claims. The "the mismatch is the finding" framing is not required at this layer — this is operational-filter text, not dashboard copy.

T5 §9 language remains bound by the prior verdict's ruling 6 (coverage-caveat framing, cross-tab linked, alternative-explanation review visible). Nothing in this amendment alters that.

---

## Required before T1-update begins

Incorporate into the Architect's updated plan / Coder spec. None require SME re-review.

### A1. Exclusion rule general principle — confirmed.

No action. The principle (exclude HTTP-infrastructure, include safety-filter refusals, filter-at-consume) is correct as specified in §2.

### A2. Add `jailbreak` to `SAFETY_FILTER_MARKERS`.

The substring list in §2 step 3 is strong but missing one marker that has historically appeared in at least one provider's refusal envelope. Add `jailbreak` (lowercased, matched case-insensitive like the rest). Rationale: it is a canonical refusal-vocabulary term and falls in the same semantic class as the existing markers. Case-insensitive matching means it covers `jailbreak`, `Jailbreak`, `JAILBREAK`.

### A3. Empty-response cohort gets its own rationale key (BINDING for Gemini 10-record disposition).

Before step 4.4 (`PARSE_EXHAUSTION_MARKERS`), add a new branch for empty-or-whitespace-only response content:

```
# 4.3.5 — Empty response body: likely silent safety block or degenerate generation.
#         Include for interview; tag distinctly so downstream analysis can segregate
#         this cohort from partial-output parse exhaustions.
if error_type == "ValueError" and (
    "Could not extract valid JSON from response: " in error_message
    and (error_message.endswith(": ") or error_message.rstrip().endswith(":"))
):
    return (True, "empty_response:likely_silent_safety_block")
```

(The specific string-shape matcher for "empty after the colon" is Coder's implementation; what is binding is that the cohort gets a dedicated rationale key **distinct** from `parse_exhaustion`.) The exact cohort Mark described (Gemini 10 `"Could not extract valid JSON from response: "` with literally empty body) must route to this branch, not to step 4.4.

Rationale key recommendation: `empty_response:likely_silent_safety_block`. Stable across v1 and beyond; greppable in Section 3b audit output; segregable in T4 cross-tab and T5 §5.

### A4. Unclassified-default-include dry-run-blocking above 2 records.

In T1-update dry-run Section 3c, if the count of `unclassified:default_include` records exceeds 2, the dry-run exits non-zero with a SURFACE-TO-SME flag and does not return GO regardless of cost projection. Rationale: a single oddity is fine to pass through; three or more unclassified records in one batch means the taxonomy has drifted and the filter needs a plan cycle, not an execution. The current failures.jsonl snapshot should produce zero `unclassified:default_include` records given the rules in §2; this check is a future-proofing tripwire, not a current-batch constraint.

### A5. T5 §5 "Exclusion rule applied" sub-section enumerates by identifier, not by bucket count.

Tightens the prior verdict's ruling 3 to this amendment: T5 §5 must list every excluded record by `(failure_id, model, domain, error_type, first 120 chars of error_message, rationale_string)`. Bucket counts alone are insufficient audit trail. Parallel to the prior verdict's requirement for the grok-4 deferred records. Applies symmetrically to T3A excluded-informants-origin records (expected to be zero, but the column stays present) and T3B excluded-failures-origin records.

### A6. T3A must be SME-eyeballed for recursive-decline before T3B fires, regardless of non-CN-origin presence.

Prior verdict ruling 4 established the two-tier recursive-decline re-review rule: any non-CN recursive → narrow review; ≥ 33% overall → broad review. That rule operated on the combined T3 batch. Under batch split, I want it applied at T3A in a stricter form:

**After T3A lands, before T3B is authorized, Mark or the SME inspects the T3A decline_interviews.jsonl records for recursive-decline signals.** The T3A population is 3 records (all CN-origin, z-ai/glm-5.1 × family empty-freelist). If any of those 3 produce recursive declines, the T3B authorization requires explicit SME sign-off that the instrument is still producing audit-grade output on the expected-safety-filter-refusal cohort. This is a narrower tripwire than "any non-CN recursive" (T3A has no non-CN records, so that tripwire cannot fire on T3A) and a stricter tripwire than "≥ 33% overall" (33% of 3 is 1, which is the same as "any at T3A" but at a tighter denominator).

Concretely: if any T3A record produces a recursive decline, T3B is paused until SME review. If zero T3A records produce recursive declines, T3B proceeds under the normal T3B authorization gate.

The prior verdict ruling 4 applies to the combined T3A + T3B post-hoc in T4/T5 as already specified; this additional T3A-specific check is a pre-T3B gate.

### A7. Rationale taxonomy is documented as a controlled vocabulary in Section 3b's header.

The Section 3b audit listing (excluded records with rationale) must be preceded by a controlled-vocabulary header that enumerates every rationale key currently in use: `http_infrastructure:{exc_type}`, `adapter_pre_generation_parse:{exc_type}`, `safety_filter:matched:{marker!r}`, `parse_exhaustion:{marker}`, `empty_response:likely_silent_safety_block`, `unclassified:default_include:{exc_type}`. Future-proofing: if a rationale key is added on a later amendment, the header is updated in the same commit, and the grep-target for audit tools is the header, not the body.

### A8. Dry-run reports both full-count and post-exclusion cost projections; pre-flight guard uses post-exclusion.

Amendment to binding note 8 accepted with this tightening: T1-update dry-run CLI summary reports **both** `(full_detected_session_count × $0.05/call)` and `(post_exclusion_count × $0.05/call)` so the operator has the raw projection on hand for future exclusion-rule revisions. The pre-flight GO/STOP gate uses the post-exclusion projection against the $8 threshold ($10 cap × 80%). The amendment §4 already specifies the latter; this note binds the "also report the raw projection" requirement.

---

## Carry-forward from prior SME verdict (all 8 binding notes)

| Prior note | Status under Amendment 1 |
|---|---|
| 1. T1 per-record not-triggered reasoning | Still binding. Section 3 in T1-update unchanged. |
| 2. T4 cross-tab baseline = corpus attempt distribution + ≥ 2 floor | Still binding. T4 unchanged by Amendment 1. |
| 3. T4 primary view = `outcome_class × origin`, no factorial | Still binding. T4 unchanged. Binding note A3 adds a rationale-key axis; it does not turn the primary view into a factorial — it is a drill-down / label on the existing axis. |
| 4. Note K taxonomy (INCONCLUSIVE-SUGGESTIVE, CONFIRMED ≥ 5 CN + ≥ 1 non-CN + Check-6) | Still binding. If post-exclusion cohort produces too few non-CN decline records, default is INCONCLUSIVE per the original ruling. |
| 5. T5 §9 CONFIRMED = coverage-caveat framing | Still binding. |
| 6. RISK 2 two-tier rule (any non-CN recursive → narrow; ≥ 33% → broad) | Still binding. Binding note A6 adds a stricter T3A-specific pre-T3B gate on top. |
| 7. T5 §9 specific numerics per denominator scenario | Still binding. |
| 8. T1 dry-run reports Gemini failures count before T3 commits | **Amended** by Amendment 1 §4 + binding note A8: full + post-exclusion counts; pre-flight $8; both cost projections reported. Prior STOP fired once and resolved; future escalations still require re-plan. |

All 8 prior binding notes remain in force. Amendment adds binding notes A1–A8 above. Total binding notes on Phase 4a.1 after this verdict: 16.

---

## Not flagged (explicitly concurred)

- §1 amendment table (what changes / what doesn't)
- §2 decision tree precedence (safety-filter-override before infrastructure; infrastructure before pre-generation parse; pre-generation parse before post-generation parse; everything else default-include)
- §2 message-substring as primary classifier, exception-type as fallback
- §3 T3A / T3B batch split with Mark sign-off gate on T3B
- §3 T3A authorization-now scope (3 records, ~$0.15, Reviewer PASS only)
- §3 T3B pre-conditions (T3A clean + Mark reviews 3b/3c + explicit Mark authorization + SME PASS on this amendment + no recursive-decline per binding note A6)
- §3 single T4 run / single T5 report across combined T3A + T3B
- §3 T5 §5 new sub-section "Exclusion rule applied under Amendment 1" (tightened by binding note A5)
- §4 $10 hard cap, CLI-parameterized, per-sub-batch counters
- §5 Coder's worklist scope (no schema changes, no detector edits, no LLM imports)
- §6 task ordering T1-update → T2 → T3A → (Mark gate) → T3B → T4 → T5
- §7 revised dependency chain
- §8 gate allocation (exclusion rule = SME; cap raise + batch split + flag = Reviewer)
- §10 pre-conditions for T1-update
- §11 file list

---

## Memory updates pending

No memory file update required for this verdict. The existing `project_cn_decline_clustering_phase4a.md` file remains correctly scoped as pre-remediation. After T5 completion I will update it per the prior verdict's pending-update note. No new memory file is required for the exclusion-criteria ruling — it is incorporated into the plan document chain and will be visible to future review via the verdict file itself.

---

## Summary

**Amendment 1 PASSES with 8 additional binding notes (A1–A8).** The general principle is correct, the Gemini empty-response disposition is correct (include with distinguishing label per A3), the default-include-unclassified policy is correct (with dry-run-blocking tripwire above 2 records per A4), and the safety-filter-override priority is correct (with one added marker per A2). The cap raise, batch split, and `--source` flag are correctly scoped as Reviewer-sufficient. The amendment to binding note 8 is accepted with the two-projection tightening per A8. T3A must be inspected for recursive-decline before T3B fires per A6. All audit surfaces (Section 3b controlled-vocabulary header per A7, T5 §5 by-identifier enumeration per A5) are tightened to incorporation-into-spec level.

**T1-update may begin once the Architect has incorporated binding notes A1–A8 into the Coder spec.** No SME re-review required.

---

*Posted to `#lsb-cda-sme`. Binding for T1-update through T5 unless superseded by a subsequent Architect plan cycle with SME re-review.*
