---
name: project-tm-d-plan-verdict
description: TM-D footnote-band cosmetic plan PASS routing-only verdict 2026-06-11; band aria-label + placeholder line locked byte-identical; no methodology touched.
metadata:
  type: project
---

TM-D footnote-band cosmetic-pass plan: SME verdict PASS (routing-only) on 2026-06-11.

**Why:** The plan is a frontend visual-design pass on the constant-height
.term-map-cluster-footnotes band shipped with commit aaaba0b. The band's
existence and constant-height contract are load-bearing for the published
§3.1.1(c) D1 election ("all cluster labels MUST be discoverable to the
reader, on or off the map"). The plan correctly identifies the two
SME-bound visible strings:
  - aria-label "Cluster labels not shown on map due to space constraints."
  - placeholder "All cluster labels are shown on the map."
and locks both byte-identical absent explicit SME re-review of any
proposed change. No measure, no protocol, no prompt template, no schema,
no DATA_DICTIONARY, no methodology-page text is touched. Forbidden-vocab
grep clean across the plan body. The four geometric loop-breakers
(constant compile-time height, ResizeObserver 1px delta guard, 8px
quantization, setHiddenClusterLabels equality guard) are explicitly named
as NOT TOUCHED and Reviewer rule R-Footnote-5 greps the diff to confirm.

**How to apply:**
  - If UI/UX returns D7 with either string changed, re-route to SME with
    binding (not routing-only) review on Axes 3+4.
  - If UI/UX returns D11 picking an anchor other than §3.1.1(c)/(d) (e.g.,
    moving the spec to a section that re-frames the band as discretionary
    rather than methodology-anchored), re-route to SME — the band's
    purpose ("all cluster labels MUST be discoverable") is a claims-
    validity contract, not a visual preference, and its DESIGN_SYSTEM.md
    home must keep that framing visible.
  - AC10 forbidden-vocab grep on Coder diff is mandatory; the comment
    block in TermMap.tsx L1428-1433 already passes today, but new CSS
    comments / DESIGN_SYSTEM.md prose introduced by the cosmetic pass
    must be re-grepped.
  - AC6 ResizeObserver / quantization / equality-guard preservation is
    methodologically irrelevant to SME but registers in memory as the
    Mark-named oscillation closer; if a future task re-opens any of those
    three lines, surface this verdict to remind the orchestrator.

Related: [[project-cr-t7-plan-verdict]] (prior verbatim-string-binding
pattern), [[project-m1-methodology-replace-verdict]] (DESIGN_SYSTEM
version-bump-with-changelog discipline).
