---
name: Review rigor — always stress-test statistical thresholds at small-N
description: When reviewing any rank-, correlation-, or eigenvalue-based QA threshold, explicitly analyze the small-N / small-intersection trip behavior, not just the "typical case" behavior.
type: feedback
---

On any PR that adds a rank-correlation, agreement-ratio, or eigenvalue-based threshold (Spearman ρ, Pearson r, Jaccard, λ₂ floor, etc.), explicitly walk through what happens when the input is small (e.g., n = 4 shared items, N = 2 or N = 3 runs). Rank statistics and low-λ detectors destabilize fast — one swap drops ρ from 1.0 to 0.6 on n=4, and "λ₂ ≈ 0 → deterministic" trips on any two coincidentally identical runs at N=2.

**Why:**
- On the Sutrop CSI wiring PR (`feat/wire-sutrop-into-pipeline`, April 2026), the ρ ≥ 0.85 threshold was methodologically correct for typical frontier-model free lists but lacked a minimum-shared-item floor in `check_salience_agreement`. The PASS-WITH-NOTES fix was a minimum-shared-item guard of ≥ 10.
- On the Register 1 wiring PR (`feat/wire-register-1-pipeline`, April 2026), the `deterministic_output` flag (`λ₂ ≤ 1e-12`) was methodologically correct for the intended future-architecture regime but lacked a minimum-N guard. Two coincidentally-identical runs at N=2 would trip the flag on a single event, not a stable-regime finding. The PASS-WITH-NOTES fix was a minimum N floor of ≥ 5 for the flag to fire.

Capacity-truncated models and small-intersection cases surface these exact edge cases as realistic regimes, not hypotheticals.

**How to apply:**
- On any threshold review, ask: "What is the smallest valid input this check will see in production? What does the statistic do at that boundary?"
- If the answer is "a single swap/coincidence trips the threshold," flag a minimum-input-size guard as binding before merge.
- Typical floors worth requesting: n ≥ 10 shared items for Spearman ρ; N ≥ 5 runs for any bootstrap or low-λ flag; n ≥ 8 for Procrustes drift (per ARCHITECTURE Register 3 rule).
- For eigenvalue-based thresholds specifically, verify the matrix construction invariants (e.g., diagonal = 1.0, entries ∈ [0,1], λ₁ ≤ n) so an absolute threshold is defensible against the construction — and note the invariant in the code so a future refactor must either preserve it or retune the threshold.
