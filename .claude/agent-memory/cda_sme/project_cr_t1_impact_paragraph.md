---
name: project-cr-t1-impact-paragraph
description: 2026-06-10 PASS-WITH-NOTES on Collection Records Rework T1 — Mark-authored verbatim impact paragraph above existing framing_note in Collection records tab. String publishable byte-identical; two carry-forward advisories.
metadata:
  type: project
---

CR-T1 verdict 2026-06-10: PASS-WITH-NOTES on the Mark-authored impact paragraph that translates "failures are findings" for cold visitors. String ships byte-identical (apostrophe form "provider's side"; no em dashes; no §1.5.4 forbidden vocab in standalone form).

**Why:** Mark-authored copy is not SME-editable. The plan's §6 gate rule (FAIL = bounce-back-to-Mark, not Coder rewrite) correctly enforces the boundary. The string sits inside §1.5 framing as observable output behavior under structured elicitation.

**How to apply:** Two non-blocking advisories carry forward for downstream surfaces:
- N1 (advisory): the phrase "make every model look equally cooperative" survives as a counterfactual about how-the-data-would-display, NOT as a model disposition claim. If any UI/UX expansion or T14 methodology echo restates "cooperative" outside the counterfactual frame ("model X is more cooperative than model Y"), that crosses into §1.5.4 territory. Flag at next-surface review.
- N2 (advisory): "behavior" register in the impact paragraph coexists with "output distribution" register in the existing framing_note (~50 words apart). Both are §1.5-licit; no string change requested. T14 / methodology-page expansion that bridges between them should make the register relationship explicit, not leave the reader to reconcile.

The Architect's plan correctly:
- Preserves all 7 T10 byte-identical strings (S1-S7) + framing_note (JSON-sourced)
- Renders in ready-state only (loading / fetch-failed / malformed are chrome-only)
- Renders for all three domains including food empty-state (consistent with §1.5.5 first-class empty)
- Treats this as Train A independent of T4 (publish layer)
- Routes SME and UI/UX as separate gates with non-overlapping ownership (SME = string licit; UI/UX = placement + §19.4 amendment)

Forbidden-vocab scan on string: clean against §1.5.4 left-column table — no "believes" / "thinks" / "worldview" / standalone disposition phrases for "cooperative" / publishable framing / "closer to human is better" / consensus framing applied at R1 / "Smith's S" / "agree" / categorical-divergence row left-column phrase.
