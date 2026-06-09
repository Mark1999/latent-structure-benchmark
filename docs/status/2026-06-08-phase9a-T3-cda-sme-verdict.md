---
filed: 2026-06-09
reviewer: CDA SME agent (Opus)
task: Phase 9a T3 — restore SimilarityHeatmap CI-crosses-null R10 treatment
slack_channel: "#lsb-cda-sme"
verdict: PASS-WITH-NOTES
precedent: docs/status/2026-05-12-phase6-T5-cda-sme-verdict.md (Phase 6 T5 §1 + §5)
disposition: re-affirmation, no new methodology
---

# Phase 9a T3 — CDA SME verdict on restoring the SimilarityHeatmap R10 treatment

## CDA SME VERDICT: PASS-WITH-NOTES

Axis 1 — Protocol validity:      PASS
Axis 2 — Analytical validity:    PASS
Axis 3 — Claims validity:        PASS
Axis 4 — Audience translation:   PASS-WITH-NOTES

Register compliance:             PASS  (Register 2; Mantel-style correlation between two
                                        models' co-occurrence matrices on the shared item
                                        set is the canonical R2 statistic. No within-model
                                        consensus / CCM / eigenratio language. OCI not invoked.)
Vocabulary compliance:           PASS  (scanned all four binding strings, the caption, and
                                        the plan against `CLAUDE.md` §7 and `ARCHITECTURE.md`
                                        §1.5.4 including the SME-review additions. "versus"
                                        is the approved non-cognitive connective; "no shared
                                        structure" is data-relation language, not consensus
                                        framing.)

This is a re-affirmation of the Phase 6 T5 binding under restoration. The Phase 6 T5
verdict (`docs/status/2026-05-12-phase6-T5-cda-sme-verdict.md`) approved
`SIMILARITY_NULL_VALUE = 0.5` as the rescaled Mantel-correlation null, set the binding
caption text, and set the four-variant aria-label template. The 2026-05-25 rebuild
silently dropped the CI-crosses-null surface; Architect plan
`docs/status/2026-06-08-phase9a-T3-heatmap-r10-architect-plan.md` restores it. No
methodology has changed. Verifying each of the five items the dispatch prompt asked
me to confirm.

---

## 1. `SIMILARITY_NULL_VALUE = 0.5` re-affirmation — PASS

The constant is still the correct no-shared-structure null. Verified from current code,
not from memory:

- `packages/cdb_analyze/cdb_analyze/mds.py` L66-77 (read in this review): pairwise
  Pearson correlation between upper-triangular co-occurrence vectors, NaN -> 0, then
  `scaled = (r + 1.0) / 2.0` on L74. Pearson r=0 (linearly uncorrelated under random
  pairing) maps to **exactly 0.5** after rescaling. This is the formal Mantel null,
  not a midpoint. Identical to the L74 reading on which Phase 6 T5 §1 (Axis 1) was
  grounded.
- `ARCHITECTURE.md` §4.2.2 line 911 still binds the same statistic: cross-model
  similarity = Mantel-style correlation between two models' co-occurrence matrices on
  the shared item set, range [-1, 1], displayed as [0, 1] after rescaling.
- The "crosses null" operationalization remains `ci_lower < 0.5 < ci_upper` (strict
  inequalities — the plan §5 boundary test case correctly enforces this). This
  matches `ARCHITECTURE.md` §4.5 cells-whose-CI-crosses-the-null-value rule.

The constant is **approved for re-introduction at `apps/dashboard/src/config/analysis.ts`**
(currently absent — grep confirms 0 hits in `apps/dashboard/src` for the identifier).
The Architect's plan §2 specifies it lives at that path with the derivation comment;
that is the correct location, alongside `OCI_LOW_CONCENTRATION_THRESHOLD` and the
other shared thresholds. The plan's instruction that the component MUST NOT carry a
stray `0.5` literal for null comparisons (use the constant), and that the only `0.50`
literal is the presentational aria-suffix text, is the correct enforcement pattern
and matches binding rule that thresholds are imported, never duplicated.

No change to `mds.py` L74 has happened since the 2026-05-12 ruling. The mathematical
ground beneath `SIMILARITY_NULL_VALUE = 0.5` is unchanged.

---

## 2. Aria-label binding strings — PASS (verbatim re-affirmation)

All four variants are re-affirmed verbatim from Phase 6 T5 §5.2. The Coder MUST use
these exact strings; the Reviewer enforces at PR review.

**Variant A — off-diagonal, CI present, CI does NOT cross null (solid border):**

> `${shortNameA} versus ${shortNameB}: similarity ${sim.toFixed(2)}, 95 percent confidence interval ${ciLow.toFixed(2)} to ${ciHigh.toFixed(2)}`

**Variant B — off-diagonal, CI present, CI crosses null (dashed border):**

> `${shortNameA} versus ${shortNameB}: similarity ${sim.toFixed(2)}, 95 percent confidence interval ${ciLow.toFixed(2)} to ${ciHigh.toFixed(2)}; confidence interval includes the no-shared-structure value of 0.50`

**Variant C — off-diagonal, CI null/missing (solid border):**

> `${shortNameA} versus ${shortNameB}: similarity ${sim.toFixed(2)}, confidence interval not available`

**Variant D — diagonal (self-cell, never dashed):**

> `${rowModel} self-similarity: 1.00 by construction`

Notes on each:
- "versus" is the approved non-cognitive data-relation connective (Phase 6 T5
  vocabulary scan; re-scanned today, still clean).
- "no-shared-structure value of 0.50" — verbatim match to the §5.1 caption term, so a
  screen-reader user encounters consistent vocabulary moving between caption and cell.
  The trailing "of 0.50" disambiguates which value is meant.
- "95 percent" written out, not "95%" — the percent sign reads poorly in screen
  readers; "95 percent" is the binding spoken form. The numeric `.toFixed(2)` values
  read as decimals naturally.
- "1.00 by construction" preserves the analytical claim that diagonal cells are not
  measurements but identity facts. This phrase is load-bearing — do not soften to
  "self-similarity: 1.00" alone, because that reads as a measurement.
- The non-crossing / null-CI / diagonal cells **must not** carry the "includes...0.50"
  suffix. The dispatch prompt's framing (suffix only on crossing cells) is correct.

The current live `SimilarityHeatmap.tsx` L140 has the regression bare-string aria-label
`${rowModel.model_id} vs ${colModel.model_id}: ${sim.toFixed(2)}`. This violates R10
(no CI in screen-reader surface) and uses "vs" rather than the approved "versus".
The four-variant template above replaces it in full.

---

## 3. Caption extension — PASS

The plan's caption text is re-affirmed verbatim from Phase 6 T5 §5.1:

> **"Each cell shows how similarly two models organize this domain (1.00 = identical organization; 0.50 = no shared structure). Dashed cells: 95% confidence interval includes the no-shared-structure value of 0.50."**

The dispatch prompt elides the leading sentence ("Each cell shows how similarly...");
the **full caption** above is the binding form. The leading sentence is necessary —
without it, a reader landing on the chart sees a dashed-border explanation but no
explanation of what the cells *measure*. The two sentences are a paired unit and
must be rendered together in the ContentArea `chart-wrap__desc` paragraph.

Plan §2 correctly stipulates this lives on the **ContentArea** chart-description
paragraph, not inside `SimilarityHeatmap.tsx`. This avoids the duplication failure
mode of rendering the caption in both places (the plan calls this out explicitly:
component itself must NOT also render it; no duplication). PASS.

Forbidden-vocab scan on the full caption: clean. "organize" is `ARCHITECTURE.md`
§1.5.4 line 166 approved. "structure" / "shared structure" reads as data-relation
language in this context (statistical co-occurrence pattern), not as a
cognitive-overlap claim. The numeric anchors (1.00, 0.50) are tied to their
interpretations explicitly, which is what R10 audience translation requires.

---

## 4. Scoping confirmations (advisory) — PASS

**(a) Dashed border + aria-label pair sufficient without hover tooltip.** Confirmed.
R10 binding text (`ARCHITECTURE.md` §4.5 + CLAUDE.md §6 rule 10) is that uncertainty
must be present and adjacent to the point estimate. The dashed border (visual,
sighted users) plus the CI-disclosing aria-label (screen-reader users) plus the
numeric similarity value rendered inside the cell satisfy this. A hover tooltip is a
**nicer** R10 surface but not a **required** R10 surface; deferring it to the
frontend-designer follow-up is acceptable. The dispatch prompt's framing is correct.

Caveat I want on record (advisory, non-blocking): the only audience that gets the
numeric CI value `[X.XX, X.XX]` here is the screen-reader audience. Sighted users see
"dashed -> CI crosses null" but no numeric CI. That is a deferred audience-translation
gap, not a methodology gap. The frontend-designer follow-up that adds the tooltip
closes it. Documenting here so it is not forgotten.

**(b) Diagonal cells never get the dashed treatment.** Confirmed and load-bearing.
Self-similarity = 1.0 is an identity fact, not a measurement. There is no bootstrap
variance because there is no statistic being estimated — the diagonal entries are
set, not computed, in `mds.py` (the `sim` array initializer is `np.ones((n, n))`, and
the i==j case is never overwritten in the L68-76 loop). A diagonal cell with a CI is
a code bug, not a meaningful uncertainty signal; a diagonal cell with a dashed border
would communicate the false claim that a model is statistically indistinguishable
from itself, which is a category error.

The plan §2 correctly mandates the short-circuit on `isDiagonal` before the
`ciCrossesNull(ci)` check. The test plan §5 case (5) — diagonal -> solid +
"self-similarity: 1.00 by construction", no CI — is the binding falsifiability test
for this constraint. The Coder must implement the short-circuit even if
`similarity_ci[i][i]` somehow contains a numerically-crossing value; the diagonal
exclusion is a hard methodological invariant, not a runtime heuristic.

---

## 5. §1.5 / §7 concern with restored text — PASS

No concern. Full scan against `CLAUDE.md` §7 forbidden vocabulary and `ARCHITECTURE.md`
§1.5.4 (including SME-review additions, extended table). Scan was applied to: (a) the
four aria-label variants in §2 above, (b) the two-sentence caption in §3 above, and
(c) the Architect's plan body. Zero matches across all three surfaces.

Categories checked (referring to each category by its CLAUDE.md §7 / §1.5.4 row
rather than spelling out the literal forbidden tokens here): model-applied cognitive
verbs row, the consensus framings row, the cross-domain generalization shape, the
within-model R1-misapplied vocabulary row, the publication-tone tokens row, the
human-baseline-as-target framing row, the empty-state defect framings row, and the
standalone-bias-tag row. None present in the restored T3 surface.

The phrase "no shared structure" is the only term that lives near the
forbidden-vocab boundary (structurally adjacent to one of the §7 consensus-framing
phrases). The Phase 6 T5 §5.1 soft-flag rationale stands unchanged: "shared
structure" reads in the data-relation sense (the two models' co-occurrence matrices
have correlated upper-triangular vectors), not in the cognitive-overlap sense. The
parallel with "identical organization" in the same caption keeps the data-structural
reading load-bearing. This is the canonical non-cognitive way to plain-English the
Mantel-correlation null.

"versus" as the connective is the approved Phase 6 T5 ruling — it is a comparison
operator, not a cognitive verb. PASS.

---

## Carry-forward binding notes (Coder + Reviewer)

The five §5 notes from Phase 6 T5 carry forward in full. The Phase 9a T3
implementation MUST satisfy all five. None of them are new; this is the
re-affirmation surface.

1. **Caption (verbatim binding):** two-sentence form in §3 above. Render on
   `ContentArea.tsx` chart-description paragraph, NOT inside `SimilarityHeatmap.tsx`.

2. **Aria-label (four variants verbatim binding):** §2 above. Variant B is the only
   one carrying the "includes...0.50" suffix; non-crossing / null-CI / diagonal MUST
   NOT carry the suffix.

3. **No tooltip narration.** The hover tooltip is deferred to the frontend-designer
   follow-up. The Coder MUST NOT add an info-icon, expandable section, or methodology
   sentence inside the component to explain the null. The caption sentence is the
   entire methodology surface for T3.

4. **T14 §4.5 doc-text refinement is still owed.** Phase 6 T5 §5.4 flagged that
   `ARCHITECTURE.md` §4.5 line ~1110 currently reads "shown with reduced saturation"
   but the implementation uses a dashed border. T14 has not yet landed this fix per
   recent git history. The Coder includes a one-line note in the T3 commit body
   referring to the Phase 6 T5 §5.4 suggested replacement sentence as the stable
   T14 target. Non-blocking on T3 ship.

5. **Use `SIMILARITY_NULL_VALUE` as the imported constant; no stray `0.5`.** The
   numeric literal `0.50` may appear in the presentational aria-suffix string only.
   All null-comparison logic (`ciCrossesNull`, boundary arithmetic in tests) imports
   the constant.

These five notes are binding on the Coder. The Reviewer enforces at PR review.

---

## Approval

**PASS-WITH-NOTES.** T3 is approved to proceed to UI/UX (dashed-border contrast on
the post-T6 5-stop palette is the binding UI/UX risk, correctly flagged in the
Architect's plan §4) and then to the Coder on the standard gate chain.

The five carry-forward notes above are binding; they are unchanged from the Phase 6
T5 ruling. No new methodology has been introduced and none was needed. The
underlying statistic (`mds.py` L74 rescaling, `ARCHITECTURE.md` §4.2.2 binding text)
is unchanged from 2026-05-12. `SIMILARITY_NULL_VALUE = 0.5` remains the correct
formal Mantel null. The four aria-label variants and the two-sentence caption
remain the binding strings.

No escalation to Mark required. This restores a previously approved surface; the
2026-05-25 regression dropped it, and Phase 9a T3 puts it back.

— CDA SME agent (Opus), 2026-06-09
