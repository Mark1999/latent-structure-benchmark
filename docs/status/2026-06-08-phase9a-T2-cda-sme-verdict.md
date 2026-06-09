# Phase 9a T2 — CDA SME verdict (LIGHT, render published `generated_lede` verbatim)

**Date:** 2026-06-09 (verdict file dated per kickoff plan filename, 2026-06-08; issued 2026-06-09)
**Task:** Phase 9a T2 (option A, Mark's ruling) — replace `ContentArea.tsx` inline-computed lede with `domain.generated_lede` rendered verbatim.
**Plan reviewed:** `docs/status/2026-06-08-phase9a-T2-generated-lede-architect-plan.md`
**Posture:** LIGHT confirm. The lede CONTENT is already CDA-SME-approved (it is the published `lede_v1.py` template set output). This task changes only WHICH lede the dashboard shows.

---

CDA SME VERDICT: PASS

Axis 1 — Protocol validity:      N/A
Axis 2 — Analytical validity:    PASS
Axis 3 — Claims validity:        PASS
Axis 4 — Audience translation:   PASS

Register compliance:             PASS
Vocabulary compliance:           PASS

---

## Confirmations against the four light-check questions

**1. In-bounds for the prior lede-template PASS.**
PASS. The `generated_lede` field is produced by the SME-approved `packages/cdb_publish/cdb_publish/templates/lede_v1.py` template set (Phase 5 T2 content PASS-WITH-NOTES, 2026-05-09; Phase 5 T13 PASS-WITH-NOTES, 2026-05-11). Wiring the published string verbatim into `ContentArea.tsx` does not introduce new copy. No re-review of lede prose required. The published lede field has been load-bearing in the published JSON since the Phase 5 work; T2 closes the consumer gap, not a prose gap.

**2. Removing the inline-computed dynamic lede loses no REQUIRED framing.**
PASS. The current inline lede (lines 199-220) emits one of two strings:
- Empty selection: `"Consensus baseline (all tested models): {domain} vocabulary is organized around a shared categorical structure (Smith's S = X, 95% CI [...])."`
- Non-empty selection: `"Across N model(s), {domain} vocabulary is organized around a shared categorical structure (Smith's S = X, 95% CI [...])."`

Both reduce to the `strong_consensus_homogeneous` template, minus the second sentence ("The map below shows where each model sits relative to that consensus and which models diverge from it."). Both omit the R1-b disclosure entirely. Both also assert "shared categorical structure" UNCONDITIONALLY — i.e., they would mis-frame a `weak_consensus`, `subcultural`, `turbulent`, `contested`, or `all_deterministic` domain if one ever shipped to v1 (currently family/holidays/food are all strong-consensus, so this is latent rather than active risk, but the latent risk is real). The published `generated_lede` branches correctly across all seven `ConsensusType` literals (per Phase 5 T2 Q1 schema-literal binding); the inline version cannot. Removing the inline lede therefore loses nothing required and removes a latent mis-branching risk.

The "Across N models" / `selectedModelIds.size` dynamic is a CHART-VIEW affordance, not a methodological commitment about the LEDE. The plan's framing ("the lede reads as 'the finding' (full-slate consensus); the charts are 'the view'") is methodologically clean: the SME-approved finding is computed on the full slate; subsetting the chart view does not subset the finding. Pairing a full-slate Smith's S with a subset N would, in fact, have been a misleading-precision hazard, which option A avoids.

**3. Restoring the R1-b disclosure to the live surface.**
PASS — confirmed as a §1.5 / R10 improvement. The R1-b sentence ("N of these N_total models produced low output concentration on this domain — their position on the map is shown without a confidence ellipse, signaling that the runs did not converge on a single sort") is the methodological honesty point that explains to a reader why a specific model's dot lacks an uncertainty ellipse. Currently the dashboard renders such dots without explanation — a reader sees inconsistent ellipse-presence across models and has no surface text to interpret it. Restoring this sentence on family and food (both have `n_low_oci=1`) closes a real visible-on-the-page R10 gap. Holidays uses `strong_consensus_homogeneous` (`n_low_oci=0`) and naturally omits the sentence; that branch logic is correct.

The vitest regression guard in plan §5 ("rendered DOM contains 'low output concentration' AND 'without a confidence ellipse'") is well-targeted; it locks the disclosure against future silent regressions of the kind this task is fixing.

**4. §1.5 / §7 concern with the published lede appearing verbatim.**
PASS. I have spot-checked all seven branches in `lede_v1.py` plus the `all_deterministic` edge case. Compliance:
- No §1.5.4 / §7 forbidden vocabulary in any branch (the cognition-attribution and w-word categories enforced by the project's pre-commit check).
- No softer-verb leakage ("recognizes", "identifies", "interprets", "comprehends", "perceives" applied to models — T9 binding).
- Descriptive-locational frame throughout ("organized around", "shows where each model sits", "located in a different region"). No convergence-to-truth, no causal, no introspective.
- Schema-literal `ConsensusType` branching; "NO_CONSENSUS" absent.
- US English ("organized", "signaling").
- Smith's S CI present in every branch — R10 compliance preserved.
- "publishable" / "publication" framing absent (T14 binding).

The plan's own §4 note about "--" (double-hyphen) appearing in the published prose is correctly flagged as cdb_publish-side scope, not T2 scope. The double-hyphen is a clause separator in the typesetting tradition that the lede_v1.py templates use; it is NOT an em dash (per Mark's hard rule against em dashes); and any change to it requires `lede_v2.py` per CLAUDE.md §6 R7. I make no T2 finding on it.

---

## Findings

None.

## Required before merge

None. This is a light confirm of already-approved copy being routed to its intended consumer.

## Advisory carry-forward

A1. The plan's framing — **"the lede reads as 'the finding' (full-slate consensus); the charts are 'the view'"** — is a clean register articulation worth preserving. If the methodology page is updated to describe how subset slicing interacts with the published findings, this sentence (or equivalent) is the right anchor. Advisory, no action required.

A2. The vitest regression guard for the R1-b disclosure is binding-quality even though the plan classifies it as a regular test. Recommend it stay in place permanently as the live-surface backstop against silent regression; a future "let's simplify the lede" refactor should NOT be allowed to drop it without explicit SME review.

---

**Verdict:** PASS. Dispatch to UI/UX (light) and then Coder per plan §3 gate path.
