---
name: project-phase9a-T3-heatmap-reaffirm-verdict
description: Phase 9a T3 re-affirmation of Phase 6 T5 SimilarityHeatmap R10 binding under 2026-05-25 rebuild regression; PASS-WITH-NOTES 2026-06-09; 5 carry-forward notes unchanged
metadata:
  type: project
---

PASS-WITH-NOTES on 2026-06-09 re-affirming the Phase 6 T5 SimilarityHeatmap binding
(`docs/status/2026-05-12-phase6-T5-cda-sme-verdict.md`) under restoration after the
2026-05-25 rebuild silently dropped it. The Architect's plan
(`docs/status/2026-06-08-phase9a-T3-heatmap-r10-architect-plan.md`) restores the
dashed-border + CI-disclosing aria + caption surface.

**Why:** The 2026-05-25 frontend rebuild reduced `SimilarityHeatmap.tsx` to
`{similarityMatrix, models, selectedModelIds}` (no CI prop). Every cell renders at
full saturation with bare-string aria. R10 violation on food: 34/56 off-diagonal CIs
cross the no-shared-structure null. This is an implementation regression, not a
methodology change.

**How to apply:** Five carry-forward notes from Phase 6 T5 §5 are binding on T3
implementation, unchanged:
- §5.1 caption (two sentences, ContentArea-side, NOT inside the component)
- §5.2 four aria-label variants (A solid, B dashed with "includes...0.50" suffix,
  C null-CI, D diagonal "by construction")
- §5.3 no tooltip narration in component (tooltip deferred to frontend-designer)
- §5.4 T14 §4.5 doc-text refinement still owed ("reduced saturation" -> "reduced
  visual weight"; binding suggested sentence in T5 §5.4)
- §5.5 `SIMILARITY_NULL_VALUE = 0.5` imported constant; no stray 0.5 literal except
  the presentational "0.50" in the aria-suffix string

Live-code re-verification done:
- `mds.py` L74 still `scaled = (r + 1.0) / 2.0` -> 0.5 remains the Mantel-rescaled
  null. Mathematical ground unchanged.
- `apps/dashboard/src/config/analysis.ts` does NOT currently export
  `SIMILARITY_NULL_VALUE`; needs re-adding under plan §2.
- `apps/dashboard/src/components/SimilarityHeatmap.tsx` (note path: not under
  `viz/`) currently has the regression bare-string aria at L140 and no CI prop.

Scoping confirmations (advisory):
- Dashed-border + aria-label pair is sufficient R10 surface without hover tooltip
  (tooltip is a frontend-designer follow-up, not a methodology blocker).
- Diagonal cells MUST short-circuit before `ciCrossesNull(ci)`. Self-similarity =
  1.0 is identity, not measurement. A diagonal dashed cell would communicate a
  false statistical claim.

Cross-link: [[project_phase6_T5_similarity_heatmap_verdict]] is the originating
binding; this memory is the re-affirmation under regression.

UI/UX has a real binding risk on this task: dark `--color-text-primary` stroke on
the post-T6 dark seq-3 / seq-4 cells is ~1.7:1 contrast, likely failing WCAG 1.4.11
(3:1 non-text). UI/UX may specify a white-stroke fallback for the 2 darkest stops
in §12.8 — that ruling is theirs, not mine, but I flag it so the cross-gate
sequencing is visible.
