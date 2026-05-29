# Corpus re-baseline — COMPLETION RECORD (2026-05-29)

**Outcome: SUCCESS — all 3 domains regenerated under pinned NumPy 2.4.4 / SciPy 1.17.1; all PASSED the SME threshold guard. No lede-class changes. Staged, NOT yet promoted.**

Ran unattended in zellij while Mark traveled. Script: `scripts/rebaseline_corpus.py` (commit `fd6f490`). Wall-clock 14:14→21:33 UTC (~7h20m). Background task `b40hb3p4z`, exit 0.

## Per-domain result (guard = PASS for all)
| Domain | Models | Runtime | Guard | sha256 (canonicalized) |
|---|---|---|---|---|
| family | 15 | ~3h10m | PASS | fb4d988eec11ef67… |
| holidays | 14 | ~4h00m | PASS | e9d16361c67b9fde… |
| food | 8 | ~10m | PASS | 3330f8fa7702c004… |

Manifest provenance: numpy 2.4.4, scipy 1.17.1, python 3.12.3, git fd6f490, platform Linux-6.8.0. Full manifest + per-domain delta reports + log live in `out/rebaseline/` (untracked, on VPS disk).

## Drift assessment (benign — confirms the reproducibility hypothesis)
- **food: bit-identical** — every field `+0.000000`. The load-bearing risk domain (eigenratio 6.586 vs 5.0 boundary; an OCI at 3.74 vs 3.0) did not move at all.
- **OCI: `+0.000000` for every model, every domain** — deterministic quantities reproduce exactly; drift is isolated to bootstrap/MDS-derived values.
- **family:** consensus_score 0.803321→0.805244 (+0.0019); romney_eigenratio 18.997→19.143 (+0.147); per-model centrality |Δ|≤0.0026; MDS max |Δ| 0.071.
- **holidays:** consensus_score 0.878139→0.880363 (+0.0022); romney_eigenratio 36.253→39.283 (+3.03); per-model centrality |Δ|≤0.0023; MDS max |Δ| 0.076.
- **No classification boundary crossed** (guard T-1..T-6 all clear): no Romney strong/weak flip, no centrality sign flip, no OCI R1-b flip, no consensus_type change. The eigenratio shifts are large in absolute terms but both domains sit far above the 5.0 line — no published claim is affected. MDS shifts are positional jitter (Procrustes-aligned), structure unchanged.

Conclusion: the published 0.x numbers and the pinned-environment numbers differ only in bootstrap/MDS quantities at small magnitude, none near a decision boundary. The numpy/scipy unpinning was the sole cause; pinning + re-baseline closes it.

## PENDING — finalize on Mark's return (NOT done unattended; outward-facing publish)
Promotion is held deliberately. To finalize:
1. **(Reviewer-gated)** Promote staging → live: copy `out/rebaseline/<domain>/<ver>.json` over `data/results/<domain>/` and the published `apps/dashboard/public/data/*.json`. Verify the diff is the expected small numeric drift only.
2. **(SME N1–N3, binding — `docs/status/2026-05-29-rebaseline-cda-sme-verdict.md`)** Before/with promotion: add the methodology-page **data-provenance paragraph** (recomputed 2026-05-29 under NumPy 2.4.4/SciPy 1.17.1; prior numbers valid under their toolchain, the defect was unpinning; rounding-level only) + a **link to baseline_manifest.json**. Framing: no forbidden vocab, no wrong/right framing.
3. **(T5, UI/UX-gated)** Footer "Calculated with NumPy 2.4.4 / SciPy 1.17.1" on every screen, sourced from the manifest.
4. Commit + push; Cloudflare redeploys.

Until then, live data is unchanged; the re-baseline sits in staging only.
