---
name: Phase 4b plan verdict PASS-WITH-NOTES
description: 2026-05-07 plan-level verdict on the Phase 4b architect plan; Q8 failures-as-findings reframe accepted; P1–P8 binding; v1_s* reuse and v2_soft1 single-arm both approved; cost non-blocking
type: project
---

**2026-05-07 — Phase 4b plan PASS-WITH-NOTES.** Verdict file: `docs/status/2026-05-07-phase4b-cda-sme-plan-verdict.md`. Plan reviewed: `docs/status/2026-05-07-phase4b-architect-plan.md` (commit `5e55ba6`).

**Why:** The plan encodes Mark's four 2026-05-07 directional changes (20-model slate, real-data canonical collection, failures-as-findings extended to prompt iteration, diagnostic ride-along folded in as T2+T3) cleanly. The structural decisions — 20-model slate, eight v1_s* variants, single soft-form v2_soft1 ride-along (Q2 option B), 3-model saturation reference set, prompt-evolution log mechanism — all hold up. The Q8 failures-as-findings reframe is consistent with the just-landed no-human-baseline amendment.

**How to apply:**

- **Q1–Q8 rulings:** Q1 AGREE (20-model slate); Q2 AGREE-WITH-CAVEAT option B (single v2_soft1 arm, P3 binds the within-v2 framing); Q3 AGREE (per-model G1 diagnostic only, not gate); Q4 AGREE (3 saturation references); Q5 AGREE-WITH-CAVEAT (P1 provenance + P2 success-rate definition); Q6 AGREE (campaign_ids); Q7 AGREE-WITH-CAVEAT (P5 non-gating); Q8 AGREE (failures-as-findings reframe — the consequential ruling).
- **Q8 reasoning:** the original §5.3 "if gate fails: pause, may shelve project" posture predates the 2026-05-07 amendment removing thesis framing. Holding it would contradict §1.5.7 exploratory framing. The reframe makes G1 a measurement; FAIL becomes a published finding with the variant-expansion runbook still triggering before disqualification calls. ARCHITECTURE.md §5.3 lines 1330–1331 will need a future Architect amendment to reflect this; not a Phase 4b Coder task.
- **P1–P8 binding (Phase 4b numbering):** P1 (v1_s* authorship-provenance recorded at T1, no placeholder); P2 (success-rate definition in log preamble at T1); P3 (v2_soft1 single-arm framing at T7, no within-v2 stability claim); P4 (per-model G1 = diagnostic, not gate, at T7); P5 (no mid-flight prompt iteration at T4); P6 (`SATURATION_REFERENCE_MODELS` constant update at T6 to in-slate references); P7 (forbidden-vocabulary scan at T7 includes amendment rows 11–12); P8 (G1-failure prose discipline at T7 if failure occurs).
- **Carry-forward:** B6 (a)–(e) BINDING on T7; T8/T9/T11–T15 BINDING on T6/T7 prose; A1–A6 SATISFIED-globally; Note D SATISFIED-by-amendment; Note A BINDING on T6/T7.
- **Cost:** $120–$300 NON-BLOCKING (real campaign per philosophy doc §9; not a probe). Mark sees plan §9 numbers and acts if upper bound is too high.
- **v1_s* prompt reuse:** ACCEPTABLE. All 8 variants verified on disk: paraphrases preserving imperative anchor + numbered-list + 200-cap; pile-sort preserves JSON output schema + partition constraint; pile-interview is identical across versions (acceptable — sensitivity at this step is dominated by upstream pile structure).
- **Prompt-evolution log mechanism:** ACCEPTABLE with P1/P2/P5 binding the disciplines that the plan leaves implicit.
- **SME content verdict at T7:** the closing gate for Phase 4b methodology-bound text. P3/P4/P7/P8 + T11–T15 + B6/T8/T9 all checked at T7.

**Phase 4b Coder dispatch AUTHORIZED at T1.**
