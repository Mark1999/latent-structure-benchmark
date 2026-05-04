# OPS-T6 — CDA SME light-touch verdict (QA badge + decline-classification surface)

**Verdict:** PASS-WITH-NOTES
**Reviewer:** CDA SME (external SME)
**Date:** 2026-05-06
**Plan reviewed:** `docs/status/2026-05-06-OPS-T6-architect-plan.md`
**Scope:** copy-only methodological review of the internal ops dashboard. `DESIGN_SYSTEM.md` gating waived per `feedback_visual_inspection.md`. §1.5 framing and §7 forbidden vocabulary are still binding (universal rules).

---

## Four-axis scorecard

| Axis | Verdict | Note |
|---|---|---|
| Axis 1 — Protocol validity | N/A | Read-only display of already-collected metadata + decline classifications. No protocol decisions. |
| Axis 2 — Analytical validity | N/A | No statistics computed. Pure projection of existing fields onto a summary table. |
| Axis 3 — Claims validity | PASS | `qa_passed` is run-metadata produced deterministically by `scripts/qa_check.py` — it is not a claim about the model. Architect's read in Q6 is correct. The badge does not say anything about the subject. One nit on the `manual_classification` column header surfaced as a binding edit below (Q3). |
| Axis 4 — Audience translation | PASS-WITH-NOTES | Audience is Mark + future researchers reading classification rationale. Q5 caption-with-doc-pointer is the right call. One header rename (Q3) and one wording tightening (Q5) keep the surface unambiguous. |

Register compliance: N/A.
Vocabulary compliance: PASS conditional on the two binding edits below.

---

## Per-question responses

### Q1 — Badge wording

**APPROVE (a):** `**QA:** PASS` / `**QA:** FAIL` (green / red).

Rationale: matches the schema field name `qa_passed`, scannable, terse. Avoids the slight passive-voice drift in (b) ("Passed/Failed" reads as event-history; "PASS/FAIL" reads as state). (c) drops the colon separator and is harder to scan at a glance. The static-text test asserting the verbatim badge string (with both color directive and fallback) is correct.

### Q2 — `qa_notes` placement

**APPROVE** as proposed:

- `qa_passed=False` + non-empty notes → `st.error(f"**QA notes:** {_rec.qa_notes}")` directly under the badge, no truncation.
- `qa_passed=True` + non-empty notes → collapsed `st.expander("QA notes (informational)")`.
- Empty `qa_notes` → no notes block at all.

The asymmetry is methodologically right: passing-with-notes is rare and informational; failing-with-notes is the failure-as-finding case where verbatim visibility matters (memory `project_failures_are_findings.md`). The expander label "QA notes (informational)" is clear and not borderline. Use verbatim.

### Q3 — Forbidden-vocabulary clearance on new literals

**APPROVE WITH ONE BINDING EDIT.**

All other proposed literals (`QA`, `PASS`, `FAIL`, `QA notes`, `QA notes (informational)`, `Decline summary`, `decline_interview_id`, `originating_step`, `outcome_class`, `safety_subtype`, the no-declines line, the gloss caption) clear §7 — none touches the worldview / believes / thinks cluster, none implies internal cognition.

**Binding edit:** rename the column header **`manual_classification` → `disposition`** in the table.

Rationale: (1) `manual_classification` is the *process* (Mark hand-coded these); `disposition` is the *value*. The table column shows the value, not the process. (2) `disposition` is already the established term in this project — see `feedback_detector_role_change_gate.md` and the T4 verdict's "disposition correctly CONFIRMED (not -with-mechanism)" language in memory. Renaming aligns the dashboard column with the project's working vocabulary. (3) `manual_classification` in a column header could read as a quality marker on the value itself ("this classification was manual" — implying others might be automated and better), which we want to avoid. The dataclass field name `manual_classification` may stay; only the *displayed column header* changes.

`safety_subtype` as displayed header is fine (the dataclass field `safety_attribution_subtype` is more precise; the truncated header is acceptable for table compactness because the gloss caption disambiguates).

### Q4 — No-declines wording + framing change

**APPROVE** the verbatim wording: *"No decline events recorded for this informant."*

**APPROVE** the `st.info` → `st.success` change in both the new summary block and the existing decline-events section.

Rationale: under the failures-as-findings frame (memory `project_failures_are_findings.md`), a decline event is a finding to be preserved and analyzed, not a defect. But "no decline events on this run" is the unambiguous positive state for that specific informant — the run completed without the model refusing or producing unexpected output. Green is the right semantic primitive for that. `st.info` (blue/neutral) under-claims the cleanness of that result.

The regression-guard test (`test_no_declines_does_not_use_st_info`) is the right way to enforce the framing change without coupling to a future Streamlit theme.

### Q5 — k_frame / k_vocab gloss caption

**APPROVE (a) — caption-with-doc-pointer**, with **one binding wording edit** for accuracy.

Architect proposed:
> *"One row per decline event for this informant. Subtype labels (k_frame / k_vocab) are defined in docs/DECLINE_INTERVIEW_PROTOCOL.md."*

Use instead (binding):
> *"One row per decline event for this informant. Disposition and safety-subtype labels (k_frame / k_vocab) are defined in docs/DECLINE_INTERVIEW_PROTOCOL.md."*

Rationale: (1) the caption now explains both new columns the reader will not recognize on first read (`disposition` and `safety_subtype`), not only the safety subtype. With the Q3 rename, `disposition` becomes the more prominent unfamiliar label, so the caption should name it. (2) Pointing at the protocol doc is the right call over (b) inline-gloss — inline glosses drift from the canonical doc and create a second source of truth. The protocol doc is the canonical place; the dashboard points there. (3) (c) no-gloss is rejected — Mark knows the labels but the audience explicitly includes future researchers (per the plan's §1).

The static-text test must assert this final wording verbatim.

### Q6 — §1.5 framing risk from elevating QA pass/fail to a prominent badge

**CONFIRM** the Architect's read. No §1.5 framing risk.

`qa_passed` is computed by `scripts/qa_check.py` from deterministic structural checks on the run record (per the QA check tiers in memory `project_qa_check_aggregate_pattern.md`). It is metadata about whether the *run* was structurally well-formed, not a claim about model cognition, worldview, capability, or quality. A FAIL badge says "this run did not produce structurally valid step records" — it does not say "the model is bad" or "the model believes X." The visual elevation does not change what the badge denotes; it just makes the existing metadata visible at a glance.

One small audience-translation precaution that is *not* binding: the badge says nothing about *which kind* of QA failure this is. A reader unfamiliar with `scripts/qa_check.py` could read FAIL as a model-quality judgment. The Q2 placement (verbatim `qa_notes` under the badge on FAIL) mitigates this — the notes spell out the structural reason. Adequate.

---

## Binding notes the Coder MUST apply

1. **Q3 binding edit:** the displayed column header is **`disposition`**, not `manual_classification`. The dataclass field `DeclineSummaryRow.manual_classification` may keep its name; only the table column header changes. Update the static-text test to assert `"disposition"` is present and `"manual_classification"` does not appear as a column header literal in `app.py` (regression guard).
2. **Q5 binding edit:** the gloss caption verbatim is *"One row per decline event for this informant. Disposition and safety-subtype labels (k_frame / k_vocab) are defined in docs/DECLINE_INTERVIEW_PROTOCOL.md."* Update the corresponding static-text assertion (`test_decline_summary_caption_q5_wording`) to this exact string.
3. **Commit body must reference this verdict file path:** `docs/status/2026-05-06-OPS-T6-cda-sme-verdict.md`.
4. **Forbidden-vocabulary scan (A12) must include the new gloss caption and the renamed column header.** Both clear §7.
5. **Test name update:** the existing proposed test `test_decline_summary_caption_q5_wording` should assert the *full* sentence verbatim (or a clearly named substring covering both "Disposition" and "safety-subtype" + the doc path), not the prior shorter form.

## Nice-to-have suggestions (non-binding)

1. The dataclass field name `manual_classification` is fine for now but consider renaming to `disposition` in a separate one-line refactor task to align field-name and display-name. Strictly cosmetic; not in scope here.
2. Consider a tiny `st.caption` directly under the QA badge on FAIL informants noting that QA failures are structural-checks-on-the-run failures (not model-quality failures) and pointing at `scripts/qa_check.py`. Strictly optional — the verbatim `qa_notes` already serves this function in practice.
3. When the OPS-T4 follow-up label re-name lands (per OPS-T5 verdict suggestion 1), revisit whether OPS-T6 needs any consequential text adjustment. Likely none.

---

## Closing summary

The plan is methodologically sound; two binding wording edits (column header `manual_classification` → `disposition`; gloss caption updated to name both new column types and reference the protocol doc) align the new surface with established project vocabulary and explain the previously unfamiliar columns. No §1.5 framing risk from the QA badge — `qa_passed` is run-metadata, not a model claim. Coder may proceed.
