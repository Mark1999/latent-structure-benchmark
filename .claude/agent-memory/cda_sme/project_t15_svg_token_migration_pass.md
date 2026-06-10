---
name: project-t15-svg-token-migration-pass
description: T15 SVG hex-to-token refactor across 9 dashboard chart components; SME PASS (all axes N/A); UI/UX is binding gate; byte-identical visual delta required; R10 invariants preserved by acceptance criterion 4
metadata:
  type: project
---

T15 Architect plan (2026-06-10) migrates 54 SVG hex literals across 9 dashboard chart components (TermMap, MDSPlot, Focus2FamilySimilarity, SimilarityHeatmap, ClusterTree, FreeListCompare, PileStructure, Focus1RunDistribution, Focus2FamilyOverview) to `var(--token)` references.

**SME verdict: PASS.** All four axes N/A. Vocabulary compliance clean.

**Why:** Pure design-token refactor with byte-identical visual delta acceptance bar. Touches no analysis measure, no gate threshold, no §1.5.x framing, no lede template, no methodology copy, no R10 logic, no aria-label routing, no caption strings, no SR-template strings. Architect's own routing call ("CDA SME review required? No") is correct on the merits; SME PASS confirms it.

**How to apply:**
- If a future T15-style chart-component refactor surfaces, the routing default is N/A-on-all-axes provided byte-identical visual delta is the acceptance bar and R10 invariants are explicitly preserved.
- UI/UX is the binding gate, not SME.
- Carry-forward advisory on `#888` / `#999` / `#999999` consolidation: if UI/UX consolidates onto one token, the per-call-site RGB must remain byte-identical or it becomes a visual-delta change and the spot-check evidence is the load-bearing falsifiability hook.
- Reviewer notes confirm R10 surfaces (SimilarityHeatmap L221-227 dashed stroke; MDSPlot hollow-triangle R1-c; centrality_ci from Remedy B T4) are preserved by acceptance criterion 4.
- Mechanization carry-forward: the new `tokens-defined.test.ts` complements [[project-t-ci-vitest-routing-pass]] as a pitfall-15 guard; positive externality for future Reviewer / SME re-entry on any chart-token work.

Related: [[project-centrality-ci-register-error]], [[project-remedy-b-t4-closed]], [[project-phase9a-T3-heatmap-reaffirm-verdict]], [[project-phase6-T5-similarity-heatmap-verdict]].
