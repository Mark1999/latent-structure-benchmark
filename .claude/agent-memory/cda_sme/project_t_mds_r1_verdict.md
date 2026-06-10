---
name: project-t-mds-r1-verdict
description: T-MDS-R1 plan PASS-WITH-NOTES 2026-06-10 — MDSPlot R1-b/R1-c implementation; F5 disposition + verbatim aria-label and tooltip strings
metadata:
  type: project
---

T-MDS-R1 (MDSPlot R1-b dashed-stroke + R1-c hollow-triangle implementation) plan verdict 2026-06-10. PASS-WITH-NOTES across Axis 2/3/4 (Axis 1 N/A).

**Why:** Component currently violates R10 (bare filled circle when mdsUncertainty is null). Surfaced by T-CHART-TESTS 2026-06-10; parked behind two `it.skip` placeholders at MDSPlot.test.tsx:238 and :246.

**How to apply:** Six binding F-notes carry forward:

- F2: F5 (R1-a degenerate ellipse, `semi_major <= 0`) does NOT block T-MDS-R1. F5 is the limit case of a low-variance R1-a sample (bootstrap converged on near-point), not a low-concentration finding. Re-classifying as R1-b would be category error. F5 stays its own logged edge-case task.

- F3: R1-b tooltip copy IN SCOPE; approved verbatim (em-dash substituted): `"Position uncertain. This model's within-model output concentration is low (OCI = X.X; higher means runs converge on one structure). See model profile for within-model distribution."` Requires `ociValues: Record<string, number>` prop if not already exposed (display value only, not classification input — A5 grep remains valid).

- F4: R1-c tooltip copy IN SCOPE; approved verbatim (em-dash substituted): `"Deterministic output. This model produced the same categorical structure on every run. Its position on the map is consistent, but there is no uncertainty range to show. See the methodology page for why this is the least informative case, not the most."`

- F5: Aria-label strings approved verbatim. R1-b: `"{displayName}, low output concentration. Position shown without confidence ellipse."` R1-c: `"{displayName}, deterministic output. Same categorical structure on every run."` Screen-reader strings — NOT redundant with tooltip; assistive-tech users don't see marker-shape distinction.

- F6: §3.3.5 R1-b "small italic 'low OCI' tag" is a LEGEND affordance only. Legend deferred per plan §6 item 6. Therefore NO inline italic tag on R1-b label in this task; disclosure flows through tooltip + aria-label only. Plan A3 italic-tag bullet must be DELETED.

- F8: Em-dash substitution binding for source AND verdicts-file. Reviewer must run `\x{2014}` grep on diff with empty stdout. §3.3.5 prose lines 616 and 649 use em dashes — the SME-approved substitutions above use periods.

**Em-dash substitution pattern:** When canonical §3.3.5 prose contains em dashes, the dashboard-source version splits into two sentences with a period. Cleaner than colon for cold readers; preserves sense byte-for-byte.

**Plan §5 verdict-required answers all answered:**
(a) F5 disposition = T-MDS-R1 proceeds, F5 stays open as separate task
(b) Aria-label strings = approved verbatim above (F5)
(c) Tooltip copy = IN SCOPE, approved verbatim above (F3 + F4)

Related: [[project_centrality_ci_register_error]] (prior R10-class register-error case), [[project_phase6_T5_similarity_heatmap_verdict]] (prior caption/aria-label SME-bound surface), [[feedback_no_em_dashes]] equivalent in user memory (Mark's hard rule).
