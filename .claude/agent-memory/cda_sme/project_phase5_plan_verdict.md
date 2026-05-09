---
name: Phase 5 plan PASS-WITH-NOTES
description: 2026-05-09 plan verdict; Q1–Q11 binding (lede schema-literals, R1-b holidays handling, methodology-summary prose); B6/T8/T9/T14/Note A carry forward; tagline verbatim US English; T2 + T13 gated on separate SME content verdicts.
type: project
---

PASS-WITH-NOTES on the Phase 5 architect plan (HEAD `f9a33b7`); 11 binding notes Q1–Q11 covering T2 lede generator and T13 MethodologySummary block.

**Why:** Phase 5 ships the publish layer + minimum viable dashboard against the existing 0.2 corpus. T2 (lede) and T13 (methodology summary) are the two methodology-bound text surfaces; both gated on separate SME content verdicts at the dispatch-packet stage. Plan body itself passes vocabulary compliance.

**How to apply:**
- T2 lede: branch predicates must use schema literals (no invented "NO_CONSENSUS"); ConsensusType has six values not three. Holidays has 2 R1-b models (oci 0.0 and 2.55, both deterministic_output false); lede must surface this. Both 0.2 corpora trip romney_small_n_warning (n=11, n=9; threshold n<15). Descriptive-locational frame, not convergence-to-truth.
- T3 derived: top_freelist_terms must name the salience metric explicitly in docstring + JSON; default = Sutrop CSI (list-length-robust); JSON carries `display.top_terms_metric`.
- T13 prose: B6/T8/T9/T14 carry forward; corpus-lens five-link chain readable; tagline VERBATIM US-English ("categorize" not "categorise"); small-n acknowledged descriptively (no defect frame); CDA ancestry signal (full roster Phase 6); failures-as-findings posture surfaced for R1-b/R1-c.
- Q1–Q11 numbering distinct from prior P1–P8 (Phase 4b), B6/T8–T15 (T4/T5-redo), A1–A6 (no-human-baseline amendment).
- Single-character drift in plan §1.7: "categorise" → must be "categorize" per ARCHITECTURE.md §1.5 line 86.
