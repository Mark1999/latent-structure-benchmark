---
name: project-phase6-T8-screen-reader-summary-verdict
description: Phase 6 T8 ScreenReaderSummary + Read-as-table verdict — binding template + caption wording, cross-surface vocab inheritance from T7/T5
metadata:
  type: project
---

**Filed:** 2026-05-12. **Verdict:** PASS-WITH-NOTES on T8 (Read-as-table toggle + ScreenReaderSummary per viz).

**Why:** T8 introduces the highest-concentration LSB-authored model-describing prose surface in Phase 6 outside the methodology page — three SR template bodies (MDS/FreeList/Similarity), three table captions, button labels, empty-state captions, ~14 column headers. All §1.5.4 forbidden-vocab surfaces. Plus the consensus_type enum (STRONG_CONSENSUS / WEAK_CONSENSUS / TURBULENT / CONTESTED / SUBCULTURAL) gets rendered into prose for the first time at the SR layer; bare-enum rendering risks being read as a model-cognition claim rather than a Register-2 between-model statistical classification.

**How to apply:**

- The verdict binds **eleven** carry-forward notes (S1–S11). Load-bearing ones for future SME reviews:
  - **S1 (consensus_type enum mapping):** Coder MUST map `STRONG_CONSENSUS` → "strong consensus (the models organize this domain similarly)", etc. — bare enum NEVER rendered in SR-visible prose. Five-row binding mapping table in §2.1 of the verdict file. When T4 (DriftTracker) adds a fourth SR template, this same discipline applies to any other published-enum that gets rendered into prose.
  - **S3 (forbidden-"agree" grep extension):** the Reviewer's vocab grep should add `\bagree` (case-insensitive, word-boundary) on the Similarity surface. T5 rejected "no agreement" → "no shared structure"; T7's free-list surface is unaffected, but the Similarity SR template body, caption, and column headers must all use "no shared structure" / "similarly organize."
  - **S5 (cross-surface caption inheritance, LOAD-BEARING):** FreeListTable caption MUST inherit T7's "this model's collection runs" verbatim; SimilarityTable caption MUST inherit T5's "no shared structure" verbatim. Equivalent representations carry equivalent prose. Toggle-and-back-cycle on a viz must produce captions byte-equivalent on the same statistic.
  - **S11 (lede-boundary):** SR templates MUST NOT reuse `domainResult.generated_lede`. The lede is the per-domain interpretation (owned by `cdb_publish`); the SR template is the per-viz structural reading (owned by the dashboard's copy module). Grep `screen_reader_summaries.ts` for `generated_lede` — must not appear.
- Button labels `"Read as table"` / `"Show visualization"` APPROVED as proposed (matches DESIGN_SYSTEM.md §7 / §12.6 deferral language).
- The MDS template renders consensus_type (Register 2 / Caulkins typology); the FreeList template renders within-model term counts (Register 1); the Similarity template renders between-model similarity statistics (Register 2). Register discipline clean.
- Soft-flag accepted (non-blocking): MDS Sentence 2 "the models organize this domain similarly" — pedantically Register-1.5 between "models" and "models' outputs." Mitigated by Sentence 1's "outputs categorize" framing setting the chain.
- **Forward-compatibility advisory:** when T4 (DriftTracker) ships, the follow-up `DriftTable.tsx` + `driftScreenReaderSummary` will need its own CDA SME content review for Register 3 (longitudinal Procrustes drift) vocabulary discipline.

Verdict file: `/opt/lsb-agent/docs/status/2026-05-12-phase6-T8-cda-sme-verdict.md`. Linked precedents: [[project_phase6_T7_R10_empirical_frequency_verdict]] (the "this model's collection runs" terminology inherited at S5/§4.2), [[project_phase6_T5_similarity_heatmap_verdict]] (the "no shared structure" terminology inherited at S5/§4.3), [[project_phase6_T10_failures_publish_verdict]] (the framing_note / SR boundary discipline parallels the T10 framing_note discipline), [[project_phase5_t13_methodology_summary_verdict]] (the per-component copy-module-as-single-source-of-truth pattern T8 follows).
