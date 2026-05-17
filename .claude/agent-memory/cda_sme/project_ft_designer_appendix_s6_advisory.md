---
name: ft-designer-appendix-s6-advisory
description: 2026-05-17 advisory PASS-WITH-NOTES on FRONTEND_DESIGNER_BRIEF_APPENDIX.md §6 worked-example (Wrong/Right prose pair using §1.5.4 forbidden vocabulary inside a polarity-marked pedagogical block)
metadata:
  type: project
---

Advisory (non-binding) review of `docs/FRONTEND_DESIGNER_BRIEF_APPENDIX.md` §6 worked-example block (Wrong/Right tone-of-voice pair), commit 1c47a55, written 2026-05-17.

**Why:** the appendix is taste-layer not doctrinal, but the orchestrator flagged §6's worked-example block as a new exception context — a prose Wrong/Right pair using §1.5.4 forbidden vocabulary inside polarity-marked pedagogical framing. The canonical CLAUDE.md §7 / ARCHITECTURE.md §1.5.4 exception was crafted for tabular left-column entries and negation constructions; prose example sentences are a different surface.

**Ruling:** advisory PASS-WITH-NOTES. The line-196 annotation ("same documented exception class as the §3.1 forbidden-vocabulary table in the doctrinal brief: naming forbidden terms in order to forbid them") successfully invokes the canonical exception. Wrong example is safe given four independent polarity signals (Wrong: label, immediate Right: counterpart, closing sentence, line-196 annotation). Right example is methodologically clean: Register-2 framing, R10-compliant Smith's S with CI, no cognition attribution. One residual advisory concern: the Right example's bucket-label framing ("English-language nuclear-family vocabulary" vs "extended-family and culturally-marked terms") structurally mirrors the Wrong example's binary comparison shape; refinement via concrete term lists or option-B meta-language alternative available but optional.

**How to apply:** if a future appendix or taste-layer document introduces another Wrong/Right prose pair using forbidden vocabulary, the orchestrator should preemptively flag for advisory CDA SME pass — this is the established pattern. The line-196 annotation phrasing ("same documented exception class as...naming forbidden terms in order to forbid them") is the canonical exception invocation for prose blocks; reuse verbatim or adapt the cite. Verdict location: `docs/status/2026-05-17-ft-designer-brief-appendix-s6-cda-sme-advisory.md`. Doctrinal brief verdict at [[ft-designer-brief-verdict]] is unchanged by this advisory.
