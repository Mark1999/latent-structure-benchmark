---
name: project-phase6-T13-ac10-verdict
description: Phase 6 T13 food domain AC10 verbatim lede verdict — PASS-WITH-NOTES; n=8 ship posture
metadata:
  type: project
---

Phase 6 T13 food-domain AC10 verbatim lede verdict — 2026-05-15.

**Verdict:** PASS-WITH-NOTES. One required text fix (M1: "signalling"
→ "signaling" — US English). After M1 applied, Coder commits.

**Key methodological rulings:**

1. **n=8 ship posture confirmed.** Lede correctly says "Across 8
   frontier models" (post-qa-filter), consistent with family (11)
   and holidays (9). Changing to "9 attempted / 8 analyzed" would
   break cross-domain framing convention.

2. **Silent grok-4.20 exclusion accepted at T13.** 5 grok food
   records remain in informants.jsonl with qa_passed=False; not
   duplicated to failures.jsonl. Disclosure gap routed to T14
   methodology page (carry-forward F1).

3. **n=8 + romney_small_n_warning is publication-worthy.** Smith's S
   null is 0.0, not 0.5 (the "0.5" referenced in some contexts is
   SIMILARITY_NULL_VALUE for Mantel heatmap, a different statistic).
   CI [0.48, 0.79] well above no-concentration null. Romney
   eigenratio 6.59 > both thresholds. Small-n flag is a caveat,
   not a disqualifier.

**T14 binding carry-forwards (Architect schedules):**
- F1: methodology page names qa_passed=False as distinct exclusion
  category from safety_filter/decline/refusal.
- F2 (advisory): Phase 6.5 resolves whether qa_passed=False records
  co-duplicate into failures-surface or whether failures-surface
  scope is tightened.
- F3: methodology page names v1 corpus-wide small-n posture
  (all three domains n<15, CI-width carries small-n signal).

**Why:** AC10 was the binding final pre-commit gate for the food
domain. The silent qa-filter exclusion was novel — not previously
ruled on at this surface. Posture (a) chosen because the failures-
surface is currently scoped to "no parseable response" (per
framing_note) while qa_passed=False is "parsed but failed
validation" — these are methodologically distinct categories
deserving separate disclosure surfaces.

**How to apply:** if a future domain ships with silent qa-filter
exclusions, the T13 precedent allows posture (a) — but the
methodology-page disclosure F1 must be in place before any
external promotion of the v1 corpus.

Related: [[project_phase5_t13_methodology_summary_verdict]],
[[project_romney_small_n_threshold]],
[[project_no_human_baseline_amendment]].
