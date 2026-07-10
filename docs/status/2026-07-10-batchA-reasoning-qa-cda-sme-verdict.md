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

## Addendum, 2026-07-10, dense-tokenizer informant class

Supplementary ruling requested by the coordinator on wave-3 claude-opus-4-8 (13 records) and claude-sonnet-5 (20 records), which fail only Check 6 but expose no reasoning-token breakout (`thoughts_token_count` structurally 0 under Anthropic usage). Mechanism: denser tokenizer. Measured campaign medians on freelist output: 2.48 to 2.71 chars/token for the pre-Claude-5 cohort, 1.69 to 1.84 for the new class. At 1.7 chars/token the chars/4 heuristic under-estimates `output_tokens` by roughly 2.35x, breaching the existing 100 percent tolerance band on well-formed responses. N2 conditioning on `thoughts_token_count > 0` cannot reach this class.

**Ruling.** Option (b), class-conditioned expected ratio in the Check 6 arithmetic, is the correct pattern-twin of N1 and N2. Option (a), widening the global `TOKEN_TOLERANCE`, is rejected: it erodes the check's discriminating power on the 12-model non-dense majority and directly violates the N7 forward-precedent posture that calibration mismatches get class-conditioned, not globally relaxed. Option (c) as a bare plausibility band on chars-per-token is rejected: a 1.5 to 5.0 range implies 3.3x tolerance, wider than the current 2x on either side, and would admit genuine 2x under-reporting without detection. A tighter self-consistency measure could be entertained if formulated; not approved on this pass. N5's corpus-build re-QA extension applies to these 33 records unchanged; the records ARE recoverable (persisted `response_verbatim` plus `output_tokens`), so re-collection is unnecessary.

### Binding notes, continuing from N7

**N8, Check 6 dense-tokenizer branch, constants.** In `scripts/qa_check.py`, add `EXPECTED_CHARS_PER_TOKEN_DENSE: float = 1.75` (median of the 1.69/1.84 measurements, documented in the constant comment with the campaign source and date) and `DENSE_TOKENIZER_MODEL_IDS: frozenset[str] = frozenset({"anthropic/claude-opus-4-8", "anthropic/claude-sonnet-5"})`. Verify exact `model_id` strings against wave-3 records before landing; use the values that appear on `InformantRecord.model_id`, not the OpenRouter-prefixed or the family-prefixed variants unless those are what the records carry.

**N9, Check 6 dense-tokenizer branch, arithmetic.** In `check_6_token_consistency`, when `record.model_id in DENSE_TOKENIZER_MODEL_IDS`, compute `expected = len(step.response_verbatim) / EXPECTED_CHARS_PER_TOKEN_DENSE` for each step; then apply the existing `TOKEN_TOLERANCE = 1.0` band. This preserves the 100 percent discriminating power for the class rather than widening the global band. N2's `visible_tokens = output_tokens - thoughts_token_count` correction remains a separate, orthogonal branch: the two branches compose (a future model that is both dense-tokenized and reasoning-token-breakout would subtract reasoning tokens first, then compare against the dense-tokenizer expected). Because `check_6_token_consistency` takes only the `InformantRecord`, the class check reads `record.model_id`; the reasoning check reads `step.thoughts_token_count`. Do not conflate the two branches into a single condition.

**N10, capacity_note verbatim for the dense-tokenizer class.** Emission at collection time (same site as N3) when `record.model_id in DENSE_TOKENIZER_MODEL_IDS`:
"Dense-tokenizer informant: this model uses a tokenizer producing approximately 1.7 to 1.85 characters per output token in campaign-measured freelist output, compared with 2.5 to 2.7 for the pre-Claude-5 informant cohort. QA Check 6 expected-token arithmetic is class-conditioned to the denser ratio for this record."

If a record qualifies for both the N3 reasoning-class note and the N10 dense-tokenizer note, both notes are emitted, separated by two newlines. Do not synthesize a merged sentence; the two disclosures are about different mechanisms and must remain independently readable.

**N11, forward roster-maintenance rule.** `DENSE_TOKENIZER_MODEL_IDS` is a curator-maintained set. Any new informant whose median chars-per-output-token on freelist output falls outside the range 2.5 to 3.0 (the pre-Claude-5 cluster) either joins `DENSE_TOKENIZER_MODEL_IDS` (if its median matches the current dense cluster within say 0.15) or receives its own class constant (if its median is distinct enough that reusing 1.75 would blow the tolerance). Detection is programmatic per the programmatic-before-generative rule: a script computes `median(len(step.response_verbatim) / step.output_tokens for step in freelist)` on each new informant's first 5 records and prompts the curator when the value crosses either threshold. No agent judgment required; the numbers decide.

**N12, methodology footnote extension.** The N4 methodology-page footnote is extended to name two class-conditioning axes on Check 6: (i) reasoning-token subtraction for the reasoning-model class, (ii) denser expected chars-per-token for the dense-tokenizer class. Frame both as informant properties, not as leniencies. Do not name individual models on the methodology page; name the classes.

**N13, N5 extension, wave-3 recoverability.** Wave-3 claude-opus-4-8 (13 records) and claude-sonnet-5 (20 records) are recoverable by corpus-build re-QA under the recalibrated arithmetic; both `step.response_verbatim` and `step.output_tokens` are persisted. Architect need not re-collect this class. The N5 no-silent-drop-via-inaction rule stands: treating the persisted `qa_passed=False` as authoritative for these 33 records after this ruling lands would reproduce option (c) by inaction and is FAIL.

**N14, no-relaxation guard.** Do not raise `TOKEN_TOLERANCE` above 1.0 anywhere in this fix. If a future dense-tokenizer informant sits far enough from 1.75 that the 100 percent band cannot accommodate it, add a fresh constant, do not stretch this one. The class-conditioning discipline is what preserves the check's discriminating power against the failure modes it exists to catch.

Rule 15 remains not implicated: this is deterministic collection-QA calibration on record-level fields, not analysis math.
