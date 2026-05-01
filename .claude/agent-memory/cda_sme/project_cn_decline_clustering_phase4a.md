---
name: CN-origin clustering in Phase 4a decline-interviewable cells
description: Pre-remediation pattern — 4 of 5 Phase 4a decline-interviewable cells are CN-origin models; binds Note K framing on methodology page
type: project
---

Phase 4a T5 (commit d74ce57) analysis revealed that of the 5 decline-interviewable cells
(records collected, zero QA-passed), 4 are CN-origin:
- qwen/qwen3.6-plus × family
- qwen/qwen3.6-plus × holidays
- z-ai/glm-5.1 × family
- z-ai/glm-5.1 × holidays

Only 1 decline-interviewable cell is US-origin (x-ai/grok-4 × holidays).

**Why:** Phase 4a.1 Note J cross-tab (originating_outcome_class × origin × openness × method)
was not yet executed at T5 time. This signal is already visible pre-remediation and shapes
how coverage caveats must be framed.

**How to apply:**
- Future methodology-page copy must read "US-weighted composition PLUS disproportionate
  CN-origin decline pattern (4 of 5 decline-interviewable cells)" — not standalone US-weighted.
- Frame as coverage / protocol robustness caveat, NOT as a finding about CN model behavior,
  until Phase 4a.1 cross-tab confirms the pattern is not an artifact of our elicitation
  protocol (prompt language, refusal training, API routing).
- If subsequent Phase 4a.1 work confirms the pattern, formalize as binding Note K
  amendment in docs/status/.
- Dashboard copy at Phase 6+ must state the 18/23-cell denominator explicitly.

Verdict source: docs/status/2026-04-23-phase4a-t5-cda-sme-verdict.md (pending persist).
