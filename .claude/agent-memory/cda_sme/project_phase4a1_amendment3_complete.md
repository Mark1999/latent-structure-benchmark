---
name: Phase 4a.1 Amendment 3 PASS-WITH-NOTES (B11 operationalized into T4.1+T4.2)
description: Architect Amendment 3 (D17–D22) approved for B11 K-frame/K-vocab decomposition. T4.1 unblocked. New binding notes B13/B14/B15 added. Total 31.
type: project
---

Architect Amendment 3 (`docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md`, filed 2026-04-30) operationalizes B11 into T4.1 (Coder scaffold + Mark hand-code) + T4.2 (cross-tab consumes subtype artifact). SME verdict at `docs/status/2026-04-30-phase4a1-amendment-3-cda-sme-verdict.md` (filed 2026-05-01) returned PASS-WITH-NOTES.

**Why:** B11 named K-frame/K-vocab as a T4 sub-axis question; Architect's D17–D22 are the methodologically correct decomposition. D17 (sibling artifact at `data/derived/decline_interviews_safety_attribution_subtype.jsonl`) correctly rejected (a) Coder regex helper on B5-precedent grounds and (b) extending the SME-PASSed parent classification artifact. D21 (disposition-arithmetic invariance) is the only defensible read of B11 — the K-frame/K-vocab split is descriptive of the mechanism, not a disposition-tier shifter. D20's bipartite mechanism string passes Ruling 3 public-copy guardrails clean.

**How to apply:**
- Coder may proceed to T4.1 immediately.
- 9 rows hand-coded by Mark between T4.1 and T4.2; expected distribution 5 k_frame / 4 k_vocab_without_k_frame.
- SME claims optional non-blocking spot-check slot post-Mark-hand-code (Q5 in verdict). Will post brief note to `#lsb-cda-sme`. T4.2 not blocked on it.
- B13 (soft, future batches): K-frame definition refinement available if a future batch produces ≥10 K-frame rows — break out role-assumption-only vs. study-context-only vs. both-present.
- B14 (binding on T5 §8.1/§8.2): full K-frame/K-vocab numerics live in §8.1; D20 bipartite mechanism string (with embedded summary counts) lives in §8.2. Sections cross-reference but do not duplicate numerics.
- B15 (soft, dashboard-only): "AI-vs-human-research-subject framing" benefits from a one-line gloss when rendered on dashboard methodology page; not binding on T5 methodology document.
- Total Phase 4a.1 binding notes now: **31** (was 28; +B13/B14/B15).
- T4.2 output gate at `docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md` is unchanged; that verdict will check the cross-tab format, bipartite mechanism string against Ruling 3, B14 numerics-vs-interpretation separation, and any 5/4-split drift.
