# Collection Records Rework Gate Verdicts

**Cycle:** Collection Records Rework (CR)
**Kickoff:** `docs/status/2026-06-10-collection-records-rework-kickoff.md`
**Date opened:** 2026-06-10

---

## T1: Impact paragraph for collection failures

**Task scope:** Add `IMPACT_PARAGRAPH_FAILURES` (Mark-authored) to the Collection records tab, above the framing_note. Amend DESIGN_SYSTEM.md §19.4. Three new vitest cases.

### CDA SME verdict: PASS-WITH-NOTES

**Date:** 2026-06-10

**Four-axis scorecard:**

| Axis | Score | Notes |
|---|---|---|
| Protocol validity | PASS | Paragraph correctly describes the three LSB-side outcome categories (refusal, unparseable, transport failure) without overclaiming about the protocol mechanism. |
| Analytical validity | N/A | No analysis claim made. |
| Claims validity | PASS | "how it says no, is as much a part of its behavior as the answers it gives" reads as observable output behavior, not model intent or cognition. §1.5.4 clean. |
| Audience translation | PASS | A cold journalist reads one paragraph and understands why these records matter. The counterfactual deletion framing ("that would be misleading") is effective. |

**Notes (advisory, do not alter string):**

- **N1 (advisory):** The word "cooperative" survives only inside the counterfactual deletion frame ("make every model look equally cooperative"). Downstream uses of this word in non-counterfactual contexts should be flagged for SME review.
- **N2 (advisory):** "behavior" and the implicit output-distribution register coexist within approximately 50 words. T14 (taxonomy disclosure) should bridge these registers explicitly when it ships.
- **Gate rule applied:** PASS-WITH-NOTES leaves the string byte-identical. Notes are advisory for downstream tasks; they do not alter the Coder's string.

---

### UI/UX verdict: PASS-WITH-NOTES

**Date:** 2026-06-10

**Four-question scorecard:**

| Question | Score | Notes |
|---|---|---|
| OWID design fidelity | PASS | Token-only class `.failures-findings__impact` using existing token set. No new tokens introduced. |
| 30-second journalist test | PASS | Impact paragraph is the first prose content below the domain selector; a cold reader encounters it immediately. |
| Researcher reproduce-and-cite test | PASS | Paragraph contextualizes data without suppressing it; researchers can still access verbatim records below. |
| WCAG AA accessibility | PASS | `--color-text-primary` on `--color-background` exceeds AA at all font sizes. |

**Notes (binding on Coder):**

- **F1 (binding, CSS class):** No existing class in `failures-findings.css` is suitable for the impact paragraph. `.failures-findings__framing-note` is already claimed for the data-sourced framing_note paragraph and carries secondary-color/sm-font styling. New class `.failures-findings__impact` is specified using only existing tokens: `--font-size-base`, `--color-text-primary`, `--line-height-body`, `--space-6`, `--max-prose-width`.
- **F2 (advisory, chrome-isolation):** The word "cooperative" in `IMPACT_PARAGRAPH_FAILURES` is not on the §19.13 forbidden-substring list. CDA SME N1 advisory applies. Case 9 continues to pass as written.
- **F3 (binding, placement):** Impact paragraph goes inside the `fetchState.kind === 'ready'` branch, before `data.framing_note` in JSX order, consistent with the amended §19.4.
- **F4 (confirmatory, empty-state):** The empty-state path (n_records === 0) does not suppress the impact paragraph because both live inside the ready branch. No additional conditional needed to satisfy AC3 and AC7.
- **Design system update:** DESIGN_SYSTEM.md §19.4 amended; version bumped to v0.19.1; changelog entry added referencing this verdict file.

---

### Reviewer verdict: PASS

**Date:** 2026-06-10

**Checks:**

1. String in `IMPACT_PARAGRAPH_FAILURES` is byte-identical to the Architect plan §3 string, including `provider's side` (apostrophe), three comma-serialized clauses, final period, no em dashes. PASS.
2. Export is purely additive in `copy/failures_findings.ts`; no existing export renamed, reordered, or modified. PASS.
3. Paragraph renders in `ready` state for all three domains (family, holidays, food empty-state). PASS.
4. Chrome-isolation vitest case (case 9) passes; new byte-identity case (11) passes; new empty-state case (12) passes; new loading-absent case (13) passes. PASS.
5. DESIGN_SYSTEM.md §19.4 amended; version bumped v0.19.0 to v0.19.1; changelog entry references the verdict file path. PASS.
6. One commit on master; message follows Conventional Commits with scope `dashboard`; body references kickoff and verdict file; no em dashes. PASS.
7. No banned vocabulary in any diffed text. "behavior" reads as observable-output behavior. "cooperative" is inside a counterfactual frame. PASS.
8. No edits to `framing_note` (JSON-sourced), `SECTION_HEADING`, `EMPTY_CAPTION`, badges, blocks, or other CDA-SME-bound byte-identical strings. PASS.

---

*T2-T8 verdicts to be appended as subsequent tasks complete.*
