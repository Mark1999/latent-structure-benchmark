---
name: project-reasoning-qa-calibration-verdict
description: 2026-07-10 batch A model-refresh CDA SME verdict on reasoning-model + dense-tokenizer QA calibration (deepseek-v4-pro, glm-5.2, claude-opus-4-8, claude-sonnet-5); Checks 5+6 class-conditioned on thoughts_token_count>0 AND on DENSE_TOKENIZER_MODEL_IDS
metadata:
  type: project
---

# Reasoning-model QA calibration verdict (2026-07-10)

**Verdict:** PASS-WITH-NOTES; docs/status/2026-07-10-batchA-reasoning-qa-cda-sme-verdict.md

**Why:** deepseek/deepseek-v4-pro + z-ai/glm-5.2 produced 12 substantively well-formed records in campaign new-model-refresh-2026h2-a-20260710 that all fail QA on Check 5 (latency 66 to 257 seconds against 60s cap) and Check 6 (output_tokens includes reasoning tokens that are not in response_verbatim, breaking the chars/4 comparison). Both failures are structural properties of the reasoning-model informant class, not protocol violations. Silent exclusion of the class (option c) is FAIL under the N7 no-silent-drop posture from the gpt-5.5 ruling this morning (docs/status/2026-07-10-batchA-gpt55-temperature-cda-sme-verdict.md).

**How to apply:**
- N1: Check 5 gets `MAX_LATENCY_MS_REASONING = 600_000` class-conditioned on `step.thoughts_token_count > 0`.
- N2: Check 6 uses `visible_tokens = output_tokens - thoughts_token_count` when `thoughts_token_count > 0`.
- N3: `capacity_note` verbatim disclosure emitted at collection time when any step has `thoughts_token_count > 0`.
- N5: existing 12 records NOT mutated (JSONL append-only per CLAUDE.md pitfall 10). Architect picks (i) corpus-build re-QA under recalibrated rules (preferred; records-as-data, rules-as-code) or (ii) re-collection. Treating persisted `qa_passed=False` as authoritative after recalibration = option (c) via inaction, FAIL.
- N6: mechanical count check before promotion, reasoning-class count per domain must be non-zero when non-reasoning informants are included.
- N7: forward calibration-class precedent; class-condition, do not raise the base threshold.

Rule 15 not implicated (qa_check.py is deterministic collection QA, not analysis math). x-ai/grok-4.3 Check 8 failures out of scope (genuine model-output findings under failures-are-findings).

Cross-refs: this ruling is the reasoning-model twin of the [[project-gpt55-temperature-verdict]] (gpt-5.5 provider-forced temperature) pattern. Both: provider-imposed informant-class properties get disclosure, not exclusion.

## Addendum, dense-tokenizer class (same day)

Supplementary ruling appended to the same verdict file: wave-3 claude-opus-4-8 (13 records) and claude-sonnet-5 (20 records) fail only Check 6 with a different mechanism (denser tokenizer, no reasoning-token breakout). Campaign-measured median chars/output-token: 2.48 to 2.71 for the pre-Claude-5 cohort, 1.69 to 1.84 for the new class; at 1.7 chars/token the chars/4 heuristic breaches the 100 percent tolerance band on well-formed responses.

**Ruling.** Option (b) approved: class-conditioned expected ratio in Check 6 arithmetic. Option (a) global widening REJECTED (violates N7 posture). Option (c) bare plausibility band REJECTED (3.3x tolerance admits genuine 2x under-reporting undetected). Wave-3 records ARE recoverable by corpus-build re-QA (persisted response_verbatim + output_tokens).

**How to apply (N8 through N14):**
- N8: `EXPECTED_CHARS_PER_TOKEN_DENSE = 1.75`, `DENSE_TOKENIZER_MODEL_IDS = frozenset({"anthropic/claude-opus-4-8", "anthropic/claude-sonnet-5"})`; verify exact model_id strings against wave-3 records.
- N9: Check 6 dense branch on `record.model_id in DENSE_TOKENIZER_MODEL_IDS` uses `expected = len(response_verbatim) / 1.75`; ±100 percent band unchanged. N2 reasoning branch and N9 dense branch are orthogonal and compose additively.
- N10: capacity_note verbatim for dense class; if both N3 and N10 apply, emit both separated by two newlines, do not merge.
- N11: `DENSE_TOKENIZER_MODEL_IDS` is curator-maintained; programmatic detector on new informants' first 5 freelist records.
- N12: methodology footnote extended with two class-conditioning axes (reasoning-token subtraction, dense expected ratio); name classes not models.
- N13: N5 extension, 33 wave-3 records recoverable via corpus-build re-QA; persisted qa_passed=False not authoritative post-recalibration.
- N14: no-relaxation guard; do not raise TOKEN_TOLERANCE above 1.0. Future distinct dense classes get fresh constants, not stretched.
