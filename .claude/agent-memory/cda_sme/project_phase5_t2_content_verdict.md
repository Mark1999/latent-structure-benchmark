---
name: Phase 5 T2 lede content verdict PASS-WITH-NOTES
description: T2 template-based lede generator PASS-WITH-NOTES 2026-05-09; Q1-Q5 satisfied; S1 (consensus_score field-name semantic ambiguity) forward-carry binding for next analysis-layer SME review
type: project
---

Phase 5 T2 template-based lede generator (commit 9e5a138) cleared the SME content gate on 2026-05-09 with PASS-WITH-NOTES.

**Why:** Q1-Q5 plan-level binding notes all satisfied at the dispatch-packet stage. NO_CONSENSUS substring scan returns only negation comments (zero live-code refs). Six-value ConsensusType branch logic correct. Three STRONG_CONSENSUS sub-branches (homogeneous / with_low_oci / majority_low_oci) correctly implemented per Q5. R1-b detection uses correct definition (not deterministic_output AND oci < 3.0). All-deterministic copy byte-identical to DESIGN_SYSTEM.md §3.3.5 item 6 including em-dash U+2014. US English consistent ("organized", "categorize" — no "organis-/categoris-" UK forms in live code). Test 10 vocabulary substring list comprehensive (§1.5.4 + T9 + T14 + B6).

**How to apply:**

1. **S1 forward-carry (BINDING).** `cdb_core/schemas.py:340` says `consensus_score` is "alias for romney_eigenratio" but corpus stores Smith's S (family: consensus_score=0.7107 vs romney_eigenratio=12.10). The lede labels this "Smith's S" which matches actual corpus values but conflicts with schema docstring. Binds the next analysis-layer SME review to reconcile field-name semantics before any future analysis run could write eigenratio to consensus_score (which would make the lede say "Smith's S = 12.10").

2. **S2 advisory.** The strong_consensus_with_low_oci pattern uses "did not converge on a single sort" — methodologically correct (within-model variance sense) but carries audience-confusion risk. Forward-carry to T13 methodology summary so the prose explains low-OCI semantics.

3. **Q2 routing confirmed.** No pattern embeds small-n acknowledgment at the lede surface; consistent with plan-level option (b) (small-n surfaces at T10 SourceAttribution + T13 MethodologySummary). Binds T10 + T13.

4. **T2 closed.** Reviewer + Tester proceed. T13 has separate SME content verdict at dispatch.

Verdict file: `docs/status/2026-05-09-phase5-T2-cda-sme-content-verdict.md`.
