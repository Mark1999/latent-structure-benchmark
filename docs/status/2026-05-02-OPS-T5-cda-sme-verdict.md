# OPS-T5 — CDA SME light-touch verdict (raw transcript panel)

**Verdict:** PASS-WITH-NOTES
**Reviewer:** CDA SME (external SME)
**Date:** 2026-05-02
**Plan reviewed:** `docs/status/2026-05-02-OPS-T5-architect-plan.md`
**Scope:** copy-only methodological review of internal ops dashboard. `DESIGN_SYSTEM.md` gating waived per `feedback_visual_inspection.md`. §1.5 framing and §7 forbidden vocabulary are still binding (universal rules).

---

## Four-axis scorecard

| Axis | Verdict | Note |
|---|---|---|
| Axis 1 — Protocol validity | N/A | Read-only display of already-collected step records. No protocol decisions. |
| Axis 2 — Analytical validity | N/A | No statistics computed. Verbatim pass-through. |
| Axis 3 — Claims validity | PASS-WITH-NOTES | The thinking-trace framing carries a non-trivial claims risk; addressed by the Q1 disclaimer + Q2 binding edit below. Once applied, claims posture is correct. |
| Axis 4 — Audience translation | PASS-WITH-NOTES | Audience is Mark + future researchers reproducing classification work; framing must keep "extended-thinking text is model output, not internal cognition" visible at the point of display, not only in the section header. Q2 edit secures this. |

Register compliance: N/A (no register-bound statistics in this surface).
Vocabulary compliance: PASS conditional on the Q2 binding edit and the §7 scan in A10.

---

## Per-question responses

### Q1 — Section disclaimer wording

**APPROVE** as proposed:

> *"Verbatim model output below — prompts as sent, model output text as returned. Extended-thinking text is the model's literal output, not a claim about internal reasoning."*

This is the right framing. It distinguishes "what was sent" from "what was returned," and it preempts the most common over-read of extended-thinking text (treating it as introspection). Use exactly this wording; the static-text test in A7 enforces verbatim presence, which is correct.

### Q2 — Subheader label for the thinking trace inside each expander

**EDIT — override the Architect's recommendation.**

The Architect recommends (a) *"Thinking trace (verbatim)"* on consistency grounds with OPS-T4. I am overriding that recommendation. **Use (b) "Extended-thinking output (verbatim)"** in the new Section 4 expanders.

**Rationale (binding):**

1. Section 4 is the surface where Mark and future reviewers actually read the model text. Section 4 is also the surface that lives directly under the Q1 disclaimer that introduces the term "extended-thinking." The label inside the expander must use the same term as the disclaimer above it. "Thinking trace" inside Section 4 + "extended-thinking" in the disclaimer is a vocabulary mismatch right at the point of reading — exactly where misread risk is highest.
2. "Thinking trace" is borderline §7. It is not on the forbidden list verbatim, but it leans toward the "thinks/believes/cognition" cluster that §7 exists to keep out of model-facing text. It survived in OPS-T4 because that surface is a single tucked-away expander on the freelist step. Section 4 makes thinking traces a first-class, three-step, prominently-titled section. The visibility upgrade changes the calculus.
3. OPS-T4 consistency is a real cost but the lower-risk fix is to update the OPS-T4 label later (separate task, not in scope here) rather than propagate the borderline label to a more visible surface now. Note this in the commit body as a known follow-up.

**Reject (c)** *"Reasoning tokens (verbatim)"* — provider-API vocabulary leaks an implementation detail and is also not what the field name (`thinking_verbatim`) suggests.

### Q3 — Empty-thinking placeholder text

**APPROVE** as proposed:

> *"No extended-thinking output for this step."*

Wording is accurate and is consistent with the Q2 edit (uses "extended-thinking," not "thinking"). Use verbatim.

### Q4 — Section title

**APPROVE** "Raw transcripts" as proposed.

It matches Mark's verbatim "full dialog" intent, sets the drill-down expectation correctly (this is below the headline visualization), and is the plainest term available. "Verbatim transcripts" is redundant with the per-expander labels; "Step-by-step transcripts" overspecifies.

### Q5 — Sensitive-content posture

**CONFIRM.** No redaction needed for internal-only display.

- Prompts are versioned templates under `packages/cdb_collect/prompts/v{N}/` — already destined for the open data bundle.
- Responses already exist verbatim in `data/raw/informants.jsonl` — open-bundle source.
- The ops dashboard is internal-only and unauthenticated only on a private host (per `feedback_visual_inspection.md`).
- Forbidden-vocabulary scan in A10 covers static labels; verbatim model output is not subject to §7 rewriting (the rule is about how LSB talks about its subjects, not how subjects talk).

No PII concern, no redaction concern, no §7 concern on the verbatim bodies themselves.

### Q6 — Including the third CDA step (interview / pile-naming)

**CONFIRM the Architect's recommendation.** Include `InterviewRecord` as Step 3.

Mark named "freelist + pile-sort" but the third CDA step (pile-naming / interview) is methodologically inseparable from the pile-sort step under the LSB protocol — it produces the pile labels Mark already inspects in OPS-T4 Section 3. Cutting it out would mean the raw-transcript panel cannot answer "where did this pile label come from?", which is one of the actual classification questions the panel exists to support. Including all three steps is the methodologically honest choice and the Architect should treat this as binding.

Use the proposed expander label *"Step 3 — Interview / pile-naming transcript"* — accurate and unambiguous.

---

## Binding notes the Coder MUST apply

1. **Q2 binding edit:** subheader label inside each expander is **"Extended-thinking output (verbatim)"** — not "Thinking trace (verbatim)." Update the static-text test (A7 / `test_ops_dashboard_app_static.py`) to assert this string verbatim.
2. **Disclaimer / placeholder / labels are verbatim-required.** A7 should also assert the Q1 disclaimer and the Q3 placeholder. The plan already lists these.
3. **Forbidden-vocabulary scan (A10) must include the new label.** "Extended-thinking output (verbatim)" passes §7. "Thinking trace" should be flagged as a known borderline term in the commit body's follow-up note (see suggestion 1 below) but is not blocked here.
4. **Commit body must reference this verdict file path:** `docs/status/2026-05-02-OPS-T5-cda-sme-verdict.md`.

## Nice-to-have suggestions (non-binding)

1. Open a follow-up task to re-label the existing OPS-T4 freelist thinking expander from "Thinking trace (verbatim)" to "Extended-thinking output (verbatim)" so the two surfaces converge. Not in scope for OPS-T5 — separate one-line copy task.
2. Consider a tiny `st.caption` under each step's expander label saying the step name maps to the underlying record class (`FreelistRecord` / `PileSortRecord` / `InterviewRecord`) — helpful for future researchers reading classification rationale. Strictly optional.

---

## Closing summary

The plan is methodologically sound and the questions are well-scoped; one binding label edit (Q2: use "Extended-thinking output (verbatim)" instead of "Thinking trace (verbatim)") aligns the in-expander vocabulary with the section disclaimer and keeps a more-visible surface clear of borderline §7 vocabulary. Coder may proceed.
