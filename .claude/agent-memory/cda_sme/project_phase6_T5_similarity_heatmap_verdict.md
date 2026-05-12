---
name: phase6-T5-similarity-heatmap-verdict
description: Phase 6 T5 SimilarityHeatmap PASS-WITH-NOTES; SIMILARITY_NULL_VALUE=0.5 confirmed as rescaled Mantel-correlation null; caption "no agreement" → "no shared structure"; dashed-cell aria-label augmented
metadata:
  type: project
---

# Phase 6 T5 SimilarityHeatmap verdict — 2026-05-12

**Verdict:** PASS-WITH-NOTES. File: `/opt/lsb-agent/docs/status/2026-05-12-phase6-T5-cda-sme-verdict.md`.

`SIMILARITY_NULL_VALUE = 0.5` **approved** as a formal null, not a midpoint. Rationale traceable from `packages/cdb_analyze/cdb_analyze/mds.py` line 74 (`scaled = (r + 1.0) / 2.0`) and `ARCHITECTURE.md` line 911: LSB cross-model similarity is a Mantel-style Pearson correlation between two models' upper-triangular co-occurrence vectors, rescaled `(r+1)/2`. Pearson r = 0 (linearly uncorrelated under random pairing) maps to **exactly 0.5**. This is the formal null, not a theoretical midpoint.

**Why:** Future similarity / Mantel / cross-model-correlation work needs to know that 0.5-as-null on LSB heatmaps is a load-bearing, derivation-grounded value, NOT an arbitrary choice. Anyone proposing a different null (or proposing "CI width" as the operationalization) needs to argue against the rescaling formula.

**How to apply:** When reviewing future heatmap / similarity-CI work, anchor on (a) the `mds.py` rescaling formula, (b) `ARCHITECTURE.md` line 911 Mantel-style framing, (c) the §4.5 "crosses the null" wording (not "wide CI"). If a future task touches the similarity statistic itself (e.g., a Mantel-replacement metric, or a Spearman swap), the null value will change and the constant needs to be re-derived.

**5 binding notes carried forward to Coder (enforced at Reviewer PR review):**
- N1 (caption) — binding replacement: *"Each cell shows how similarly two models organize this domain (1.00 = identical organization; 0.50 = no shared structure). Dashed cells: 95% confidence interval includes the no-shared-structure value."* Replaces "no agreement" (consensus-flavored) with "no shared structure" (data-relation language).
- N2 (aria-label) — for cells where CI crosses null, append: *"; confidence interval includes the no-shared-structure value of 0.50"*. The dashed border is visual-only; R10 + WCAG require the same fact in the DOM.
- N3 (tooltip) — no change; data-relation language already.
- N4 (T14 follow-up text in commit body) — suggested §4.5 refinement to acknowledge the dashed-border-vs-saturation substitution and to name `SIMILARITY_NULL_VALUE` as the rescaled Mantel-correlation null.
- N5 — do NOT narrate methodology on the heatmap page; methodology choice belongs on T1/T2 methodology page.

**Empirical firing — verified.** On `apps/dashboard/public/data/holidays.json`, model index 6 sits at similarity 0.45–0.51 against every other model with CIs straddling 0.5. On family.json, model index 9 sits at 0.50–0.51 with CIs explicitly crossing or boundary-clamping. Rule fires meaningfully (NOT rare-firing as the dispatch prompt feared); each shipped domain has a "floor" model against which dashed borders fire.

**No escalation to Mark required.** Notes are wording / aria-label level, no §1.5 reframing.

Related: [[phase6_T7_R10_empirical_frequency_verdict]] — same Phase 6 minimum-viable framing precedent; same "single methodology-related sentence on the page" pattern.
