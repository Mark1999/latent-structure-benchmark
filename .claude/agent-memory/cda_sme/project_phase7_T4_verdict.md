---
name: phase7-T4-verdict
description: Phase 7 T4 (X + LinkedIn drafters draft-only) CDA SME verdict 2026-05-17 — PASS-WITH-NOTES, 12 binding notes plus all 18 T3 notes carrying forward
metadata:
  type: project
---

Phase 7 T4 (X + LinkedIn drafters, draft-only) closed PASS-WITH-NOTES on 2026-05-17. Both inherit T3's DrafterBase + validate_draft.

**Why:** T4 extends drafter framework to two new platforms with new methodology surfaces beyond T3: X thread structure (segment delimiter `\n---\n`), per-segment R10 enforcement, and LinkedIn long-form 10× char budget.

**How to apply:** 12 binding notes plus all 18 T3 notes carry forward. Three new methodology rulings:

1. **X per-segment validation = Option A** — each segment independently passes all four validator checks (forbidden vocab, R10, hypothesis framing, register boundary). Cross-segment R10 parking is forbidden. Rationale: R10 is per-statement, not per-document; partial-read on X is the dominant case.

2. **X hook-tweet (segment 1) has three additional structural rules:** (a) must contain a canonical measurement noun (Smith's S, OCI, eigenratio, consensus, categorical structure/divergence, pile-sort, free-list, corpus lens); (b) must contain a CI-shape match inline; (c) three intent-attribution stems forbidden in segment 1 only (`decides`, `chooses`, `prefers`). These run BEFORE per-segment validate_draft loop.

3. **LinkedIn K=12 unchanged** — R10's local-adjacency contract does not scale with document length; K=120 on 3000-char post would enable cross-paragraph parking. Reject any future "scale K with length" proposal.

**LinkedIn-specific:** Block 5.5 anti-thought-leadership defense + three LinkedIn-only forbidden patterns (`I've been thinking`, `the future of AI`, `AI is reshaping`) + first-person pronoun rule (`\bI\b` case-sensitive). Reject any proposal to drop the first-person rule without a v2 prompt bump + CDA SME re-review.

**X thread cap:** 3 segments max, 280 chars/segment hard, 250 target. Sentinels `__x_thread_too_long__`, `__x_segment_overlength_{idx}__`, `__x_segment_1_no_measurement_noun__`, `__x_segment_1_no_ci_shape__`, `__x_segment_1_intent_attribution_{stem}__`.

**LinkedIn limits:** 3000-char hard limit, 1500-char soft target.

Verdict file: `docs/status/2026-05-17-phase7-T4-cda-sme-verdict.md`. T3 verdict at `docs/status/2026-05-17-phase7-T3-cda-sme-verdict.md` is full prerequisite reading; T4 inherits its architecture wholesale. See [[phase7-T3-verdict]] for the T3 binding context.
