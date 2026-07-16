---
name: batchA-promotion-verdict
description: 2026-07-13 batch A promotion copy pass. PASS-WITH-NOTES. Food v0.3 gets consensus_type_override=WEAK_CONSENSUS (F3-R3 straddling-CI pattern extended: point 5.44, CI [2.75,10.25], median 4.64, 66% of replicates below 5.0). Bound strings: F3-V3-A/B/C/E successors to F3-R3-A/B/C/E; BA-QA-FN (methodology footnote for N4/N12); BA-FABLE-FRAMING (single sentence preceding 2026-07-10 (d) bound string, 6 placements); BA-PROV (DataPage provenance replacement, 2026-07-12 rebaseline); BA-TERMMAP-COUNTS (15/14/8 -> 22/21/19). F3-R3-D (SMALL_N_TEXT) kept dormant, all three domains now at n>=15. Family+holidays ledes CONFIRM as generated. 14-item compliance checklist. Verdict: docs/status/2026-07-13-batchA-promotion-cda-sme-verdict.md.
metadata:
  type: project
---

## Batch A promotion copy pass (2026-07-13)

**Verdict:** PASS-WITH-NOTES
**Scope:** family 0.3->0.4, holidays 0.3->0.4, food 0.2->0.3
**Slates:** family 22 (15+7), holidays 21 (14+7), food 19 (12+7)
**Toolchain:** NumPy 2.4.4, SciPy 1.17.1, Python 3.12, B=500 seed 42, git 561b534

### Food v0.3 disposition (extends F3-R3)

**Why:** Per-replicate CI [2.75, 10.25] straddles 5.0. Median replicate
4.64 is BELOW 5.0. Point estimate 5.44 is above 5.0 by a hair. 66 percent
of 500 replicates fall below 5.0. This is more indeterminate than v0.2
was (v0.2 point 9.48 median 6.95, only lower tail crossed). F3-R3 rule
applies stronger: publish conservative WEAK_CONSENSUS with override.

**How to apply:** Any future domain that has point > 5.0 but bootstrap
CI or median crosses under 5.0 inherits this pattern. The T-1 guard by
construction cannot see the override field; F3-R3/F3-V3 override sits
above the guard by design, not despite it.

### Bound strings (all byte-identical, in verdict body)

- F3-V3-A: food v0.3 domain lede
- F3-V3-B: consensus_type_override_reason
- F3-V3-C: CI disclosure line (successor to consensus_disclosure.ts
  CI_DISCLOSURE_TEXT constant)
- F3-V3-E: MethodologyPage food v0.3 footnote
- BA-QA-FN: N4/N12 methodology paragraph on reasoning-model and
  dense-tokenizer informant-class QA calibration; single paragraph;
  informant-class framing not leniency; no individual model names
- BA-FABLE-FRAMING: single framing sentence preceding the 2026-07-10 (d)
  bound string, 6 placements (records + failures panels x 3 domains)
- BA-PROV: DataPage §15.5(a) provenance paragraph replacement
- BA-TERMMAP-COUNTS: DataPage §16.2 term-map counts sentence

### F3-R3-D disposition: KEEP DORMANT

**Why:** All three promoted domains (family 22, holidays 21, food 19)
clear the 15-model floor. `romney_small_n_warning` False on all live
surfaces. Historical v0.2 food (n=12) remains citable; SMALL_N_TEXT
preserves F3-R3-D binding on that record.

**How to apply:** Do not retire the mechanism. Do not touch the
constant. Template-ification (read n_models live) is a fast-follow, no
fresh SME pass required for the mechanical parameterization.

### Family + holidays ledes

CONFIRM as generated. Numbers verified. Advisory note (non-blocking):
ASCII double-hyphen `--` mid-sentence in both frozen templates; U+2014
absent so hard rule satisfied. Template revision to move off double
hyphens is separate scope.

### Compliance checklist (14 items) in verdict for Reviewer grep

Every numeric in newly landed text traces to the promotion facts block.
Extended-forbidden vocab (no "the model refused", "Fable declined",
"safety" standalone, "conservatively-tuned classifier") absent from all
new text. Fable placements must be visible-on-render, not tooltip-gated.

### Rule 15 boundary

Not implicated. Per-replicate CI reporting is the same computation used
at v0.2 F3-R3 (orchestrator step 4c), applied to the published v0.3
similarity matrix and its replicate stream. Invariant verified:
eigh(mean(replicates)) = 5.443105064871 = published point to 12 decimals.
No new estimator/measure/threshold. Presentation copy only.
