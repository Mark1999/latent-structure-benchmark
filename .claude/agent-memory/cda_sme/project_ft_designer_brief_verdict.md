---
name: ft-designer-brief-cda-sme-verdict
description: PASS-WITH-NOTES verdict on FRONTEND_DESIGNER_BRIEF.md v0.1 (2026-05-17); 5 binding notes for Mark before handoff to future AI designer.
metadata:
  type: project
---

Frontend Designer Brief v0.1 doctrinal review — verdict PASS-WITH-NOTES.

**Why:** Mark is preparing to hand the dashboard off from the Claude Code agent pipeline to a dedicated AI frontend designer. The brief is that designer's CLAUDE.md-equivalent doctrinal reference, so methodology-adjacent passages must be airtight before handoff.

**How to apply:** if Mark dispatches the future designer or revisits the brief, remind him of the 5 binding §5 notes:

- §5.1 — §3.1 forbidden-vocab table is incomplete ("Highlights" shows 6 of 12 canonical rows); the 4 Register-1/Register-2 rows + 2 hypothesis-testing rows must be added because designers writing tooltip copy for OCI / heatmap / Smith's S need them most.
- §5.2 — must add a one-sentence Register-1 vs Register-2 operational rule following the §3.1 table.
- §5.3 — §8.1 routing must explicitly enumerate screen-reader summary templates (T8 verdict) and statistics-bearing aria-labels (T5/T7/T13 verdicts) as CDA-SME-gated surfaces.
- §5.4 — §7.2 bundles OCI inside `cluster_consensus_metrics`, which reads OCI as a consensus statistic; must annotate registers.
- §5.5 — §10 question 7 ("elevate failures-as-findings") needs an explicit "first-class, not headline-dominant" anchor; the current parenthetical hedge is too weak for long-context AI designer sessions.
- §5.6 (advisory) — §3.2 "every numeric value is a sample estimate" → "carries quantifiable uncertainty".

Verdict file: `/opt/lsb-agent/docs/status/2026-05-17-ft-designer-brief-cda-sme-verdict.md`. Forbidden-vocab scan clean (8 hits, all in documented exceptions). Brief preserves Mark's exclusive methodology-page authorship and the R10-driven DriftTracker deferral correctly. Schema not touched; no Architect re-plan; no DATA_DICTIONARY co-update.

Related: [[phase6_T9_failures_publish_verdict]], [[phase6_T10_failures_ui_verdict]], [[phase6_T8_screen_reader_summary_verdict]], [[phase6_T14_cda_sme_verdict]] (not yet memory-indexed), [[phase6_T5_similarity_heatmap_verdict]], [[phase6_T7_R10_empirical_frequency_verdict]].
