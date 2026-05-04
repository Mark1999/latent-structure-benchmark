---
name: Task #16 max_tokens reframe — CDA SME PASS-WITH-NOTES (S1–S5)
description: 2026-05-04 verdict on the adaptive max_tokens plan; reframes 29 Phase 4a failures as cap-exhaustion artifact; S5 gates Note K T4-redo; S1–S4 tighten dictionary copy.
type: project
---

Task 16 SME verdict at `/opt/lsb-agent/docs/status/2026-05-04-task-16-cda-sme-verdict.md` issued PASS-WITH-NOTES 2026-05-04.

**Why:** Architect proposed bumping Gemini `max_output_tokens` 4096→16384 and `thinking_budget` 8192→1024, OpenRouter `max_tokens` 4096→16384, and adding `thoughts_token_count: int = 0` to FreelistRecord/PileSortRecord/InterviewRecord plus failures.jsonl envelope. Stage 1.5/1.5b/1.6 probes (commits d06e64c, 11a36c0, 19d67f1) showed 29 Phase 4a failures predominantly cap-exhaustion artifact, not refusal. Six explicit Q1–Q6 surfaced by Architect; all confirmed.

**How to apply:**
- S1–S4: tighten dictionary copy on diagnostic-invariant semantics (one-sided test), `0` ambiguity (no-reasoning vs. provider-doesn't-surface), forbidden-vocab edge in adapter comment ("model spent everything on thinking" → "cap-exhausted reasoning"), cross-provider non-comparability caveat.
- S5: gates the future T4-redo task. Note K re-classification under the new framing must route through CDA SME before any methodology-page text is written. The 9 hand-coded safety_event_attribution rows are NOT directly invalidated by the reframe (they came from decline_interviews.jsonl follow-up classifications, not the originating empty-output failures), but the attribution chain semantics shift: "model declined for safety" becomes "model retrospectively rationalized an instrument event as safety." This is methodologically meaningful.
- Q1 single-global-cap CONFIRM. Q2 `int = 0` default CONFIRM with sharper semantics. Q3 no template version bump CONFIRM. Q4 backward-compat via pydantic default CONFIRM. Q5 DeclineInterview out-of-scope CONFIRM with directional follow-on preference. Q6 `thinking_budget=1024` CONFIRM with Phase 4b watch-flag (third domain may require re-probe).
- Phase 4a.1 binding-note count unchanged at 31; Task 16 introduces fresh S1–S5 series scoped to Task 16.
- DeclineInterview field add deferred to follow-on backlog item (small, additive, not blocking).
- Phase 4b food-domain probe required before Phase 4b collection if `thinking_budget=1024` is to remain default for that domain.

**Carry-forward to next session:** The cap-exhaustion reframe changes the epistemic foundation under which I issued the Note K rulings. I did NOT pre-emptively re-rule Note K in this verdict — that's the T4-redo task's job. When that task arrives, address: (1) re-classification of 9 rows as safety_event_attribution_under_cap_exhaustion, (2) interaction with D20 cross-provider falsification (single-provider concentration may itself be cap-exhaustion artifact), (3) which of the 31 Phase 4a.1 binding notes need re-statement under new framing.
