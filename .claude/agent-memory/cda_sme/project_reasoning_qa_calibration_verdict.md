---
name: project-reasoning-qa-calibration-verdict
description: 2026-07-10 batch A model-refresh CDA SME verdict on reasoning-model QA calibration (deepseek-v4-pro, glm-5.2); Checks 5+6 class-conditioned when thoughts_token_count>0
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
