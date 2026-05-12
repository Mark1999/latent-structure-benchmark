---
name: phase6-T7-R10-empirical-frequency-verdict
description: 2026-05-12 T7 FreeListCompare R10 fallback approved — empirical f_mentions/n_runs preferred over bootstrap CI at n_runs=4
metadata:
  type: project
---

# Phase 6 T7 FreeListCompare — empirical-frequency R10 fallback PASS-WITH-NOTES

**Verdict (2026-05-12):** PASS-WITH-NOTES on Architect's §2.2 proposal to use
`sutrop_csi[modelId][i].f_mentions / .n_runs` as the per-term R10 uncertainty
representation, instead of building T7a (cdb_publish bootstrap-inclusion field).

**Why:** At n_runs = 4 (0.2 corpus), bootstrap-resample inclusion frequency
converges in expectation to f_mentions/n_runs and adds wide/uninformative CI
bounds. The empirical ratio IS the Sutrop CSI numerator primitive (F/N under
run-as-informant convention). Rendering "3 of 4 runs" is more honest than
"0.75 ± 0.30" — Architect's "illusory precision" critique was correct.
{0, 0.25, 0.5, 0.75, 1.0} discretization is acceptable at n=4.

**How to apply (binding for any future R10 / per-term inclusion frequency work):**
- If a future LSB campaign collects at n_runs ≥ 30, revisit: a Wilson-score
  interval on the empirical inclusion rate becomes informative and T7a (or a
  client-side Wilson module) becomes worth shipping. Phase 7+ concern.
- The architecture text at §4.5 line 1111 says "bootstrap samples" — inconsistent
  with T7's empirical implementation. T14 doc-sweep must update to "collection
  runs" with the replacement text in §5.4 of the verdict file.
- The run-as-informant convention is Register 1 (within-model output
  distribution / sampling concentration), NOT Register 2 consensus. Do not let
  future work re-import this convention into Register 2 framing.
- Caption wording binding: "Bar shows the fraction of this model's collection
  runs that produced this term." (note possessive "this model's" added).
- Aria-label binding: "{item}, Sutrop salience score {csi.toFixed(2)}, included
  in {f_mentions} of {n_runs} collection runs" — "salience" alone reads as
  psychological-salience claim, must be "Sutrop salience score."

**Verdict file:** [[docs/status/2026-05-12-phase6-T7-cda-sme-verdict.md]]
**Architect plan:** docs/status/2026-05-12-phase6-T7-architect-plan.md
**Related:** [[project_phase4a1_empty_freelist_propagation]] — Case C
(no-terms-produced) caption verified clean.
