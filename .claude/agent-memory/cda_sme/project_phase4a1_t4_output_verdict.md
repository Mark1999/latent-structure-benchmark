---
name: Phase 4a.1 T4 output PASS-WITH-NOTES; Amendment 4 required
description: T4.2 cross-tab output PASS-WITH-NOTES on 2026-05-01; data falsified D20 cross-provider prediction; disposition correctly downshifted CONFIRMED-with-mechanism → CONFIRMED; Amendment 4 needed to revise mechanism wording before T5 §8.2.
type: project
---

T4.2 output gate verdict at `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md`.

**Key empirical finding:** All 9 safety_event_attribution rows are Google Gemini. Cross-provider replication threshold (≥2 providers) NOT met. Disposition correctly downshifts from CONFIRMED-with-mechanism to plain CONFIRMED. The T3B SME spot-check predicted cross-provider replication based on sampling; the full-corpus classification did not confirm it.

**K-frame/K-vocab distribution:** 2 K-frame, 7 K-vocab (NOT predicted 5/4). Mark's strict-reading discipline on B11 ("AI-vs-human framing is the *named trigger*", not just present in verbatim) is correct. SME T3C prediction (5/4) was based on the looser reading.

**Why:** D20 mechanism string was written assuming cross-provider replication. Single-provider data falsifies the "cross-provider replication on the family and holidays domains" phrase. Amendment 4 required to revise wording for single-provider case before T5 §8.2 quotes it.

**How to apply:**
- T5 §1–§8.1 and §8.3–§8.4 unblocked.
- T5 §8.2 mechanism wording held until Amendment 4 lands.
- Coder's §1.5-clean rephrase ("not a claim about the model's internal state" replacing "not what the model believes") is correct and should be folded into Amendment 4 as canonical.
- Defensive guardrail asymmetry in script (CONFIRMED-with-mechanism branch only) should be fixed in same revision pass.
- Disposition arithmetic still correct; computation correct; cross-tabs correct. Only the carried-forward mechanism string text is stale.

Carry-forward: 31 binding notes (no new ones from this verdict). Required items #1–#4 are corrections, not new methodology rules.
