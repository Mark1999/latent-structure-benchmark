---
name: project-f5-degenerate-ellipse-verdict
description: F5-T1 plan PASS-WITH-NOTES 2026-06-11 — degenerate bootstrap ellipse (semi_major <= 0) treated as R1-a sub-state (converged-on-near-point); S1-S4 SME-bound byte-identical disclosure strings; B1-B10 binding/advisory notes
metadata:
  type: project
---

F5-T1 (degenerate bootstrap ellipse converged-state treatment across MDSPlot.tsx:204, TermMap.tsx:738, Focus2FamilySimilarity.tsx:182) plan verdict 2026-06-11. PASS-WITH-NOTES across Axis 3/4 (Axis 1 N/A, Axis 2 PASS).

**Why:** All three render sites currently silently fall through `if (!u || u.semi_major <= 0) return;` to a bare point, violating R10 in the case where the data is most certain (bootstrap converged on a near-point = limit case of high-stability R1-a per [[project_t_mds_r1_verdict]] F2). Zero degenerate entries in current published JSON (orchestrator scan 2026-06-11: family 115, holidays 83, food 304 ellipses), so this is forward-looking insurance.

**How to apply:**

**S1 MDSPlot tooltip body (degenerate R1-a sub-state, byte-identical):**
> "Position highly stable. Bootstrap resamples converged on a near-point, so the confidence region is too small to show as an ellipse. This is the limit case of a high-stability R1-a sample, not missing uncertainty."

**S2 MDSPlot aria-label (degenerate R1-a sub-state, byte-identical):**
> "{displayName}, high positional stability. Bootstrap resamples converged on a near-point; confidence region is too small to display."

**S3 TermMap aria-label on `.term-dot` (degenerate term ellipse, byte-identical):**
> "{term}, high positional stability across bootstrap resamples."

**S4 Focus2FamilySimilarity aria-label (degenerate family-member ellipse, byte-identical):**
> "{displayName}, high positional stability across bootstrap resamples."

**B1 (binding):** Coder uses S1–S4 byte-identical. Any deviation FAILs Axis 3.

**B2 (binding):** MDSPlot tooltip conditional additive to existing R1-b/R1-c conditionals (lines 297–299). Three conditionals mutually exclusive: R1-b ellipse-suppressed, R1-c ellipse-suppressed, R1-a-degenerate ellipse-microscopic-or-marker.

**B3 (binding):** TermMap disclosure threads through `.term-dot` aria-label (line 757), NOT `.term-ellipse` (line 746 `pointer-events="none"`).

**B4 (binding):** `data-degenerate-bootstrap="true"` sibling attribute correct; both invariants required: `data-r1-state="typical_concentration"` AND degenerate-marker selector. UI/UX may rename but must keep both.

**B5 (binding):** DESIGN_SYSTEM.md §3.3.5 amendment calls this "R1-a sub-state" / "R1-a degenerate-bootstrap converged-state," NOT a fourth R1 state. Fourth register = category error per F2.

**B7 (binding):** Reviewer runs `\x{2014}` em-dash grep on source diff + DESIGN_SYSTEM.md amendment + verdicts file F5 section.

**B9 (advisory):** UI/UX option (a) minimum-radius ellipse floor methodologically preferable (preserves literal R10 invariant); (b) distinct marker competes visually with R1-c hollow-triangle. SME does not override UI/UX call.

**B10 (binding):** Plan vocabulary clean: no "within-model" right-hand banned nouns; "within-model output concentration" in re-used F3 string is licit (noun-class test, "concentration" is a Register 1 distribution noun, not RWB-importing).

**F2 reaffirmation:** Degenerate `semi_major <= 0` is R1-a LIMIT case, NOT R1-b. Negative-precision artifact (`semi_major === -0.001`) fixture in plan A4 is methodologically sound — F2 semantics extend to non-positive after numerical rounding.

**Plan §5 verdict-required answers:**
(a) Disclosure strings = S1–S4 above, byte-identical
(b) Axis 3 PASS-WITH-NOTES (B1 binding S1–S4)
(c) Axis 4 PASS-WITH-NOTES (tooltip MDSPlot, aria TermMap/Focus2 — B2/B3 binding)
(d) Register compliance PASS (Register 1, no Register 2 leakage)
(e) Vocabulary compliance PASS (zero §7 right-column hits in S1–S4)

Related: [[project_t_mds_r1_verdict]] (F2 semantic authority), [[project_t_mds_r1_dispatch_reaffirm]] (F2 distinction from R1-b/R1-c), [[project_centrality_ci_register_error]] (prior R10-class register error class), [[project_within_model_phrase_ruling]] (noun-class test confirms B10).

## S1 jargon-removal ratification (2026-06-11)

:** S1 only. S2, S3, S4 are unchanged.

**Cross-refs:**
- DESIGN_SYSTEM.md §3.3.5 impl req 12 (canonical corrected S1)
- ARCHITECTURE.md §1.5.4 (audience translation)
- CLAUDE.md §7 (forbidden vocabulary / register discipline)
- docs/status/2026-06-10-codebase-review-fixes-verdicts.md (F5 verdict trail)
