---
name: Detector role-change gate (binding note B5)
description: Reuse of a detector helper across semantic boundaries (input→output, structured→free-text, etc.) requires SME methodology review before the batch executes
type: feedback
---

When a detector helper is reused across semantic boundaries — input-classification (matching error envelopes) to output-classification (matching natural-language responses), structured-token to free-text, or one language to another — the reuse itself is a methodological change and triggers SME methodology review before the batch executes, regardless of whether the underlying constants change.

**Why:** Phase 4a.1 T3B fired on 2026-04-23. The `_is_recursive_decline()` helper inherited `SAFETY_FILTER_MARKERS` (designed for matching provider error envelopes per Amendment 1) without revalidation for the natural-language output-classification role it was used in. The case-insensitive `'OTHER'` substring matched ordinary prose ("mother", "in other words"), and the safety-vocabulary tokens collided with substantive descriptions of safety events. Result: 18/24 flag rate (75%), 0/24 true rate. The detector flag would have nominally tripped binding note 6's broad re-review threshold; methodology basis was empirically absent. The SME A6 gate operated correctly given inputs (T3A produced zero flags); the gap was upstream of A6.

**How to apply:** When reviewing any plan that reuses a detector, classifier, or helper across what appears to be a different semantic context — even if the code is identical — flag for SME methodology review. The marker list, if reused at all, must be reviewed against the new role's semantics from scratch, not inherited. Sibling principle to binding note B4: methodology re-review thresholds operate over the event class, not the detector flag; thresholds defined over uncharacterized-precision detector flags do not fire re-review.

Verdict file: `docs/status/2026-04-23-phase4a1-t3b-detector-sme-verdict.md` Ruling 1 + binding note B5.
