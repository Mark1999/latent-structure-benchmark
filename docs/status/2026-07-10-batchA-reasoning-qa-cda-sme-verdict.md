# CDA SME verdict, batch A reasoning-model QA calibration

**Date:** 2026-07-10
**Task:** QA-check calibration for the reasoning-model informant class (deepseek/deepseek-v4-pro, z-ai/glm-5.2, campaign new-model-refresh-2026h2-a-20260710)
**Verdict:** PASS-WITH-NOTES on options (a) and (b) jointly. Option (c) is FAIL.

## Scorecard

| Axis | Result |
|---|---|
| Axis 1, protocol validity | PASS |
| Axis 2, analytical validity | PASS-WITH-NOTES |
| Axis 3, claims validity | PASS-WITH-NOTES |
| Axis 4, audience translation | PASS-WITH-NOTES |
| Register compliance | N/A |
| Vocabulary compliance | PASS |

## Ruling

Recalibrate. The 12 records are substantively well-formed at all three CDA steps (freelist ~200 items, pile sort 9 to 22 piles, interview label counts match); Checks 5 and 6 are firing on structural properties of the informant class, not on protocol failure. Option (c) is a silent class-scale exclusion and directly contradicts the N7 no-silent-drop posture set this morning for gpt-5.5. Rule 15 is not implicated: qa_check.py is deterministic collection QA over record contents, not analysis math.

## Binding notes

**N1, Check 5 recalibration.** In `scripts/qa_check.py`: introduce `MAX_LATENCY_MS_REASONING = 600_000`. In `check_5_latency`, when `step.thoughts_token_count > 0`, compare against the reasoning ceiling; otherwise the existing 60_000 ceiling stands. Same failure text, only the threshold branches. This preserves the check's diagnostic intent (operational hang detection) without failing legitimate inference-time thinking.

**N2, Check 6 recalibration.** In `check_6_token_consistency`, when `step.thoughts_token_count > 0`, compute `visible_tokens = step.output_tokens - step.thoughts_token_count` and use `visible_tokens` (not `step.output_tokens`) against `len(response_verbatim) / 4`. The chars/4 heuristic is a rough sanity check on visible output; reasoning tokens are not in `response_verbatim` and must not enter that comparison.

**N3, `capacity_note` verbatim on every reasoning-class record (follows the N1 precedent from this morning):**
"Reasoning-class informant: provider records reasoning tokens (thoughts_token_count) separately from visible output tokens, and per-step inference latency reflects inference-time reasoning. QA Check 5 latency ceiling is class-conditioned to 600s and QA Check 6 token consistency is computed on visible tokens (output_tokens minus thoughts_token_count) for this record."

The condition for emission is `any(step.thoughts_token_count > 0 for step in (freelist, pile_sort, interview))`. Emission is at collection time in the writer, not at QA time.

**N4, methodology page footnote at next update.** Name the reasoning-model class by class not by model_id (the roster will grow), state that Checks 5 and 6 carry class-conditioned thresholds, and frame the recalibration as an informant-class property, not a leniency. No "closer to human" framing. No "reasoning models are harder to evaluate" framing. Cross-link to the N1 through N7 gpt-5.5 ruling; the pattern is one pattern.

**N5, existing 12 records, fix-forward.** The JSONL is append-only (CLAUDE.md pitfall 10), and the persisted `qa_passed` value on those 12 records must not be rewritten. The methodological requirement is that they are not silently dropped from the corpus. Architect picks between (i) corpus-build time re-QA that recomputes qa_passed from records under the recalibrated rules (preferred: records are data, rules are code, and rule changes recompute derivations), or (ii) re-collection under the corrected QA where new records supersede. Both paths preserve append-only. What is not acceptable is treating persisted `qa_passed=False` as authoritative for corpus inclusion after the recalibration lands, since that would reproduce option (c) through inaction.

**N6, no-silent-drop verification.** Before promotion, count the reasoning-class informants that enter the similarity and consensus basis for each domain. If the count is zero for any domain that includes non-reasoning informants, the corpus builder is dropping the class silently and N5 has not been applied. This is a mechanical check, appropriate for a script per the programmatic-before-generative rule.

**N7, forward precedent, calibration class.** This ruling establishes the pattern for any future informant-class property where a deterministic QA check is structurally miscalibrated: class-condition the threshold or the arithmetic, disclose in `capacity_note` using the same "provider records X separately, QA Check Y is class-conditioned" pattern, and add a methodology footnote. Do not raise the base threshold to accommodate the outlier class; that erodes the check's discriminating power for the non-reasoning majority.

## What this does not authorize

- Loosening Checks 5 or 6 for non-reasoning informants.
- Skipping either check for reasoning informants (skipping is silent; class-conditioning is disclosed).
- Any change to Checks 1 through 4 or 7 (protocol shape checks) or Check 8 (aggregate salience).
- Any redefinition of what QA gates; qa_passed continues to gate corpus inclusion, just with the recalibrated arithmetic for the reasoning class.

## Rationale, brief

Check 5 exists to catch provider hangs and adapter deadlocks; a reasoning model deliberating for 257 seconds is not the failure mode the check was written to detect. Check 6 exists to catch gross usage-accounting misreporting; the completion-tokens field of a reasoning provider legitimately includes tokens that do not appear in `response_verbatim`, and comparing that against the chars/4 heuristic is a category error, not a data-quality signal. Both are calibration mismatches, not protocol violations. The x-ai/grok-4.3 Check 8 failures are correctly treated as substantive findings and are out of scope for this ruling.
