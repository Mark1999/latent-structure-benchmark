---
name: Phase 4a.1 T3C classification complete (PASS)
description: T3C commit 3 manual classification artifact passed SME spot-check at 7/7 agreement; T4 unblocked. Empirically confirms T3B Ruling 1 at full corpus coverage (0/27 genuine recursive declines).
type: project
---

T3C commit 3 (commit `b81462d` on master, 2026-04-30) landed the manual classification artifact at `data/derived/decline_interviews_manual_classification.jsonl`. Mark classified all 27 rows; SME spot-check verdict at `docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md` returned PASS (not PASS-WITH-NOTES) with 7/7 spot-check agreement.

Distribution: 11 technical_glitch / 9 safety_event / 4 no_prior_context / 3 substantive_compliance / 0 in the other three buckets. Empty buckets are *correct*: `other_substring_false_positive` is a residual category for content-free responses (none in this corpus); `genuine_recursive_decline` is empty by design (Ruling 1 prediction).

**Why:** This empirically confirms T3B Ruling 1 at full corpus coverage — the v1 `_is_recursive_decline()` detector is uniformly miscalibrated for output classification. The 18-of-24 detector flag rate is 100% substring artifact at the recursive-decline level.

**How to apply:**
- T4 is now unblocked. Cross-tab axis is the manual classification, NOT `detector_flag_v1`.
- 3 new binding notes added: B10 (soft, future batches: prefer verbatim quotes in rationale over paraphrase), B11 (binding on T4: K-vocab/K-frame split is a T4 cross-tab sub-axis question, do NOT re-open the 7-enum), B12 (binding precedent: `other_substring_false_positive` is a residual category for content-free responses, not a fallback for any substring-flagged row).
- Total Phase 4a.1 binding notes now: 28 (8 original + A1-A8 + B1-B6 + B7-B9 + B10-B12).
- K-frame finding (5 of 9 safety_event rows carry AI-vs-human-research-subject framing language) is a T4 question, not a T3C schema question.
