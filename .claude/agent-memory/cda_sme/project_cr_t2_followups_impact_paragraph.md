---
name: cr-t2-followups-impact-paragraph
description: CR-T2 CDA SME PASS-WITH-NOTES verdict 2026-06-10 on the Mark-authored follow-up-interview impact paragraph; conditional-render rule (renders only when at least one decline_interview record is present) is methodologically correct; N1 (T1 "cooperative") and N2 (register bridging) carry forward to T3.
metadata:
  type: project
---

CR-T2 verdict (Collection records rework, Task 2): PASS-WITH-NOTES, 2026-06-10. Mark-authored follow-up-interview impact paragraph ships byte-identical from `docs/status/2026-06-10-collection-records-impact-copy-approved.md` §T2.

**Why:** Higher-risk surface for cognition attribution per kickoff §4 Task 2; SME role is narrow (§1.5.4 review of the string + confirm conditional-render rule + carry forward T1 N1/N2). The approved string is clean: it locks the register at the start ("just output, produced the same way as everything else it says"), then explicitly disclaims interiority at the end ("not the inside story"). "observable behavior" matches the T1 paragraph's register. No forbidden substrings. "cooperative" absent. Em dashes absent. The conditional-render rule (renders only when at least one decline_interview record is present, i.e., `data.records.some(isDeclineInterviewRecord)`) is correct because a follow-up-interview framing paragraph with zero follow-up-interview records would be vacuous and misleadingly imply the surface contains data it does not.

**How to apply:**
- Coder ships the §2 string byte-identical; the byte-identity vitest case is the gate.
- T3 (taxonomy disclosure) must bridge the "behavior" / "output distribution" registers that coexist in T1+T2 within ~50 words each (T1 N2 carry-forward, also confirmed for T2).
- "cooperative" remains permitted only inside Mark's CR-T1 counterfactual frame; AC14 in the T2 plan forbids it in any new code/doc text in the T2 commit. Future tasks: SME flags any non-counterfactual use.
- The plan's FAIL-routing rule (SME does not silently revise Mark's prose; FAIL bounces to Mark via orchestrator) is the correct posture and stands for any future Mark-authored copy task.
- Wording nit on the plan: AC7 cites "CR-T1 verdict R7" for "behavior" permission, but the CR-T1 Reviewer verdict's "behavior" reading is in check 7 (Reviewer) / N1 advisory (SME), not "R7." Non-blocking; does not affect implementation.

Related: [[cr-t1-impact-paragraph]] (T1 sibling that this verdict carries forward from).
