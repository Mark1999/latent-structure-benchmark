# CDA SME Verdict — Corpus Re-baseline (T3 + T4, 2026-05-29 reproducibility bundle)

**Date:** 2026-05-29
**Scope:** T3 (family-only pilot regen + `baseline_manifest.json`) and T4 (roll out to holidays + food + re-update smoke/lede fixtures) under the pinned NumPy==2.4.4 / SciPy==1.17.1 environment.
**Companion docs:** `docs/status/2026-05-29-numpy-scipy-pin-architect-signoff.md` (T2 pin sign-off), `docs/BOOTSTRAP_DESIGN.md`, `docs/SME_REVIEW.md` §1.1, `ARCHITECTURE.md` §4.2 / §4.5
**Routing:** This verdict gates the Coder on T3 and T4. T3 must complete (with explicit threshold-crossing report) before T4 starts.

---

## Verdict: PASS-WITH-NOTES

| Axis | Verdict |
|---|---|
| 1 — Protocol validity | PASS |
| 2 — Analytical validity | PASS-WITH-NOTES |
| 3 — Claims validity | PASS-WITH-NOTES |
| 4 — Audience translation | PASS-WITH-NOTES |
| Register compliance | PASS |
| Vocabulary compliance | PASS |

A re-baseline that **only** moves rounding-level numerics is a deterministic-pipeline-pinning event and is methodologically fine. A re-baseline that flips any lede-class threshold is a substantive change to published interpretation and is not in T3/T4's authorized scope under the T2 sign-off ("This pin itself does not change published numbers; the re-baseline (T3/T4) does, and that is separately CDA-SME-gated"). The notes below operationalize that line.

---

## Question 1 — Pin target acceptability

**Acceptable, conditional on the conditions in Q2 and Q3 below.**

The originating numpy/scipy versions that generated the published 0.3 numerics are not recoverable (no pre-existing pin record, no lockfile snapshot). Bit-reproducibility of the existing 0.3 corpus is therefore not a candidate property — it is already unrecoverable, and trying to chase it adds zero scientific value. The pragmatic options reduce to two:

  (a) Pin to **currently installed** 2.4.4 / 1.17.1 and re-baseline forward, restoring a forward reproducibility guarantee.
  (b) Pin to an arbitrarily chosen older release in the historical window and re-baseline to that, restoring forward reproducibility against a non-current toolchain.

(a) is preferable on three grounds: (i) it minimizes the supply-chain surface area at install time on future researcher rebuilds (current major versions are still receiving security patches), (ii) it avoids back-porting LSB's analytical environment to a frozen older numpy/scipy that will get harder to install over time, (iii) the version numerics are recorded in the manifest (per Q4) and in the dashboard footer (per Q2), so the published interpretation is honest about which toolchain generated which figure.

The methodological commitment LSB makes to researchers is **forward-reproducibility from the published bundle and pinned toolchain**, not bit-equivalence with prior unpinned runs. That commitment is satisfied by either (a) or (b); (a) costs less and ages better. PASS.

The reframing point that must land in the manifest and the audience-facing copy (per Q2): the published bundle does not assert "these are the same numbers as the prior 0.3 corpus." It asserts "these are the numbers produced by the pinned-and-recorded toolchain on the recorded git SHA at the recorded timestamp, and any researcher with the bundle can reproduce them." That is the open-data contract.

---

## Question 2 — Annotation requirement (audience translation)

**The T5 footer surface ("Calculated with NumPy X / SciPy Y" on every screen, sourced from the manifest) is necessary but NOT sufficient on its own.** Two additional surfaces are required:

**N1 (binding) — Methodology page must carry a re-baseline note.** Add a one-paragraph entry under the methodology page's "data provenance" section (or equivalent existing section — Coder may co-locate with the existing version-stamp / changelog block; if no such section exists, create one). The paragraph must:

  - State the re-baseline date (2026-05-29) and the toolchain versions (NumPy 2.4.4 / SciPy 1.17.1) verbatim from the manifest.
  - State that prior published 0.3 values differed at the 3rd–4th decimal owing to unpinned dependency versions in the earlier environment, and that the substantive findings (consensus classifications, model orderings on the dashboard, the relative geometry of the MDS maps) are unchanged by the re-baseline.
  - State that the *originating* toolchain versions for the prior 0.3 numerics are not recoverable, and the re-baseline restores reproducibility going forward against the pinned toolchain.
  - Do NOT use the words "worldview," "believes," "thinks," or any §1.5.4 forbidden vocabulary. The re-baseline note describes a numerical procedure, not a change in what the models "think."

**N2 (binding) — `baseline_manifest.json` must be linked from the methodology page** (anchor link / direct download link, not a buried reference). The "Calculated with NumPy X / SciPy Y" footer must also link to or surface the manifest, so any reader who notices "this number changed since my last visit" has a one-click route to the manifest and the methodology paragraph that explains why.

**N3 (binding — content rule on the methodology paragraph).** The paragraph must NOT claim the prior 0.3 numbers were "wrong" or that the new numbers are "more correct" — both are valid under their respective toolchains, and the only methodological defect was *unpinning*, not the numerics themselves. Suggested framing: "Under the pinned toolchain (NumPy 2.4.4 / SciPy 1.17.1) the corpus was re-baselined on 2026-05-29 to restore forward reproducibility. Values shifted at the 3rd–4th decimal relative to the prior unpinned environment; the substantive consensus classifications and model orderings are unchanged."

The footer + manifest + methodology-page note is the correct three-surface treatment. The footer alone is too thin (a reader sees a version number but not the why); the manifest alone is too buried (most readers will never download a JSON file).

---

## Question 3 — Threshold-crossing guard (CRITICAL)

This is the load-bearing condition. The re-baseline is methodologically acceptable as a "rounding-level" event ONLY if no lede-class threshold is crossed. The Coder must implement a programmatic guard in T3 and T4 that compares each new computed value against the prior published value and HALTS — does not silently ship — if any of the following crossings occurs.

### The thresholds to guard (all binding)

**T-1. Romney 5.0 boundary (STRONG_CONSENSUS ↔ WEAK_CONSENSUS).**
  `romney_eigenratio` crossing 5.0 in either direction flips `consensus_type` from STRONG_CONSENSUS to WEAK_CONSENSUS or back. This is a lede-class change (per `packages/cdb_publish/cdb_publish/lede.py` L122 — WEAK_CONSENSUS routes to the `weak_consensus` lede pattern). **Highest risk: food**, where the published value is **6.586** — only **1.586 above the 5.0 boundary**. Family (18.99) and holidays (36.25) are far from this boundary, but the guard applies to all three domains uniformly.

**T-2. Romney 3.0 boundary (WEAK_CONSENSUS ↔ TURBULENT/CONTESTED).**
  `romney_eigenratio` crossing 3.0 in either direction flips `consensus_type` to TURBULENT or CONTESTED, which routes to a different lede pattern entirely. None of the published v1 domains is currently near 3.0, but the guard is uniform and cheap; include both 5.0 and 3.0 boundaries.

**T-3. Sign of any `cultural_centrality_scores` entry.**
  All three published domains currently have `negative_centrality_flag: false`. The lede branching in `classify_consensus` flips STRONG_CONSENSUS → SUBCULTURAL (and WEAK_CONSENSUS → SUBCULTURAL) the moment any centrality score crosses zero. A centrality score numerically close to zero in the prior environment could cross under the pinned environment even though no eigenratio threshold moves. This is a lede-class event. The guard must inspect the sign of every centrality score and halt if any sign flips.

**T-4. Per-model `oci` crossing 3.0** (the `OCI_LOW_CONCENTRATION_THRESHOLD` in `packages/cdb_publish/cdb_publish/lede.py` L40).
  Per-model OCI under 3.0 with `deterministic_output=False` flips a model into the R1-b "low concentration" sub-branch, which routes the STRONG_CONSENSUS lede into `strong_consensus_with_low_oci` or `strong_consensus_majority_low_oci` (different lede text). The published food corpus has a model with `oci = 3.74` — **only 0.74 above this boundary**. A drift of ~0.15 like the family `consensus_score` shift (0.8033 → 0.8052) is not directly comparable to an OCI shift, but the OCI guard is cheap, lede-class, and applies cleanly. Guard the 3.0 boundary on every model's `oci`.

**T-5. `romney_consensus_warning` flip.**
  `romney_consensus_warning` is True iff `3.0 < romney_eigenratio < 5.0`. Flipping it is methodologically a subset of T-1 (since the only way to enter the warning zone from STRONG is to cross 5.0 downward). Include as a check anyway because it surfaces on the dashboard as its own field and changes the methodology-page treatment of the domain.

**T-6. `consensus_type` direct equality** (belt-and-braces).
  Independent of the underlying numeric thresholds: compute the new `consensus_type` and compare to the prior published `consensus_type` for the same domain. Any inequality is a halt. This catches any future addition to `classify_consensus`'s branching logic that the four numeric guards above miss.

### Required behavior on crossing

If T3 (family) detects any of T-1 through T-6 crossing, the Coder MUST:
  1. STOP the re-baseline rollout (do not start T4).
  2. Save the diff (prior published value → new computed value, per affected field) to `docs/status/2026-05-29-rebaseline-threshold-crossing-{domain}.md`.
  3. Re-route the situation back to the Architect, who must re-engage me before any further re-baseline work.

If T4 (holidays + food) detects any crossing on holidays or food, the same halt-and-route rule applies.

**A crossing is not a Coder-resolvable event.** It is a finding (the prior published interpretation differs from the new pinned-toolchain interpretation), and the resolution path — keep the prior lede with a "the re-baselined interpretation would say X" note, or update the lede and reissue the methodology-page paragraph with stronger language — is a CDA-SME decision, not a Coder decision.

### Suggested guard implementation site

The guard belongs at the end of the pipeline, after `classify_consensus` has run and `cultural_centrality_scores` are computed, comparing against the prior published `data/results/{domain}/0.3.json` (or `0.2.json` for food). A small script in the T3/T4 task code path is sufficient; this does not need to become a permanent module. Bias toward simplicity — the guard's lifetime is the re-baseline event, not "forever."

### Honest risk note

Of the four published v1 fields above, the load-bearing ones are **food's `romney_eigenratio=6.586`** and **food's near-threshold per-model OCI of 3.74**. Family and holidays are far from every threshold. I estimate the probability of a guard-trip on family or holidays as very low and on food as non-trivial — perhaps 10–20% on either food check, given the magnitude of the family drift on `consensus_score` and `romney_eigenratio` already observed (3rd–4th decimal). If food trips, that is the substantive finding the guard exists to surface; do not chase it away.

---

## Question 4 — Manifest as provenance

**The proposed `baseline_manifest.json` fields are adequate, with two additions.**

The proposed minimal field set ({`numpy_version`, `scipy_version`, `git_sha`, `generated_at`, per-domain `sha256`, `model_count`, `bootstrap_B`}) is acceptable as the open-data provenance record. Add the following:

**N4 (binding).** Add `python_version` (full `sys.version` string or at minimum the X.Y.Z release). NumPy/SciPy behavior at the rounding level is also influenced by the CPython release the C extensions are linked against. The cost of recording this is one line; the cost of *not* recording it surfaces only when a future researcher cannot reproduce on a different Python.

**N5 (binding).** Add `lsb_analysis_version` (the schema/pipeline version the corpus was generated under — analogous to the existing `analysis_version: "0.3"` field on each domain result). This is the bridge between the manifest and the per-domain result file, and it lets a researcher who pulls the bundle a year from now match the manifest to the pipeline code that generated the numerics.

**N6 (advisory, not blocking).** Consider adding `platform` (the `platform.platform()` string or `sys.platform`). Linux glibc-version differences are a known source of numpy ABI behavior change. Not required for PASS — the linux-only deployment posture means this is unlikely to bite — but cheap and useful.

**N7 (binding).** The manifest's per-domain `sha256` field MUST be computed over the **canonicalized JSON** (sorted keys, no trailing whitespace, consistent float repr if applicable) of the per-domain result file. Otherwise minor JSON-formatting drift (a trailing newline, key order change in a future Python release) would falsely invalidate the manifest. State the canonicalization rule in `docs/DATA_DICTIONARY.md` alongside the manifest schema entry (this lands in the same commit per CLAUDE.md §6 rule 6 if the manifest introduces a new published-bundle field).

With N4, N5, N7 applied, the manifest is an adequate provenance record for the open-data reproducibility guarantee.

---

## Question 5 — Is the observed drift rounding-level or substantive?

**Rounding-level under current evidence; substantive only if the Q3 guard trips.**

The observed shifts:

  - family: `consensus_score` 0.8033 → 0.8052 (Δ ≈ 0.0019, ~0.24% relative)
  - family: `romney_eigenratio` 18.997 → 19.143 (Δ ≈ 0.146, ~0.77% relative)
  - MDS coordinates drifting at 3rd–4th decimal (unitless; bootstrap CIs are ~0.1+ units wide on Register 2 MDS — well above the drift magnitude)

None of these alone shifts a published claim:

  - The family `consensus_score` shift (0.0019) is two orders of magnitude inside the published `consensus_ci` width (the published CI for family is ~0.16 wide, 0.6406 → 0.8035 or similar). The change is invisible in the published uncertainty surface.
  - The family `romney_eigenratio` shift (0.146) is **18% of the distance** between family's value and the 5.0 STRONG/WEAK boundary on family (which is ~14 above 5.0). Family is in no danger of crossing.
  - MDS coordinate drift at the 3rd–4th decimal is far inside the Procrustes-aligned bootstrap ellipses already published, which are visualized at typical scales of ~0.05–0.2 units. The ellipse-rendering routine will absorb the drift without a visible change to the map.

**Substantive only if the guard trips on food.** The food values are close enough to two boundaries (5.0 on eigenratio, 3.0 on a per-model OCI) that the drift *could* cross either. That conditional substantive risk is exactly what Q3's guard exists to convert into a halt-and-route rather than a silent reissue.

If the guard does not trip on any of the three domains, the re-baseline is a rounding-level event and the audience-translation surfaces in Q2 (footer + manifest + methodology-page note) are the correct and proportionate disclosure. If it does trip, that is a separate CDA-significant event, surfaced in this verdict's Q3 halt rule, not a v1 question.

---

## Register & vocabulary compliance

**Register compliance — PASS.** T3/T4 do not move any analytical method across the R1/R2/R3 boundary. They are deterministic-pipeline-pinning events that re-run the existing pipeline under a pinned toolchain. No Register 1 / Register 2 / Register 3 boundary is touched.

**Vocabulary compliance — PASS.** This verdict's prose does not use forbidden §1.5.4 vocabulary. The required methodology-page paragraph (N3) explicitly forbids it.

---

## Required before T3 starts (consolidated)

1. **N1, N2, N3 (binding) — audience surfaces.** Methodology page paragraph + manifest link + framing rules per Q2 above.
2. **T-1, T-2, T-3, T-4, T-5, T-6 (binding) — threshold-crossing guard.** Implement per Q3. Halt-and-route behavior on any crossing.
3. **N4, N5, N7 (binding) — manifest content.** Add `python_version`, `lsb_analysis_version`, and the canonicalized-JSON sha256 rule. N6 (`platform`) is advisory.
4. **T3 must complete and report explicitly on the guard results before T4 starts.** If T3 (family) trips the guard, T4 is blocked pending re-engagement. If T3 clears the guard cleanly, T4 may proceed in the same Coder session.

## Required before T4 starts

5. T3 cleared the guard on family with an explicit report.
6. The guard runs again against the prior published holidays (0.3) and food (0.2) values during T4; halt rule applies.

## Advisory (not blocking)

7. N6 — add `platform` to the manifest if low-cost.
8. After T4 clears, save the guard's per-domain delta report (prior published value → new computed value for each lede-class field) as `docs/status/2026-05-29-rebaseline-numeric-deltas.md`. This is not a blocker; it is a useful audit-trail artifact for future re-baseline events.

---

*PASS-WITH-NOTES. Re-baseline may proceed to Coder under the binding conditions above. Any threshold crossing is a halt event and re-routes to me; the Coder is not authorized to ship a lede-class change under T3/T4's authorized scope.*
