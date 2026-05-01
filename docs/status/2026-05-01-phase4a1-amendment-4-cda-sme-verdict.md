# CDA SME Verdict — Phase 4a.1 Architect Plan Amendment 4

**Filed:** 2026-05-01
**Reviewer:** CDA SME (Opus)
**Task:** #21 (Phase 4a.1 decline-interview backfill) — Amendment 4 plan-gate review
**Document under review:** `docs/status/2026-05-01-phase4a1-architect-plan-amendment-4.md`
**Triggering verdict:** `docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md` (T4.2 output gate, PASS-WITH-NOTES; Axis 3 FAIL on stale mechanism string)
**Predecessor doc partially superseded:** `docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md` (D20 wording + §3.3 acceptance-criteria sentence only; all other content carried forward)

---

## Executive summary

Amendment 4 satisfies all four Required items from the T4 SME verdict. The wording revision (D23) adopts the SME-suggested phrasing verbatim with a single Architect refinement (provider name templated from `distinct_providers[0]` rather than hardcoded), which preserves and arguably strengthens the methodological intent. The conditional-wording binding (D24) and the defensive-guardrail symmetry (D25, option (b)) are both correctly resolved. The Coder commit bundling (D26) is justified. The §3.3 canonical wording promotion (D27) is correct housekeeping.

**Verdict: PASS.** No PASS-WITH-NOTES — the amendment is small, focused, and carries no methodology decisions that need further refinement. The Coder unblocks immediately on T4.2-followup.

---

## Per-question ruling (orchestrator scope)

### 1. D23 wording — provider name templated from `distinct_providers[0]`

**Ruling: PASS.** The Architect's refinement (rendering `{provider_name}` from `distinct_providers[0]` rather than hardcoding "Google Gemini") preserves the methodological intent and improves it. The refinement matters for two reasons:

1. **Re-run generality.** The amendment correctly anticipates that Phase 4b or a re-run on a different cohort might surface a single-provider safety pattern attached to a *different* provider (e.g., another safety-tuned model). Templating the provider name from data avoids a future Amendment 5 to revise hardcoded copy.
2. **Methodological honesty.** The provider name is an empirical observation about *this corpus*, not a theoretical property of the K-frame/K-vocab split. Templating it from `distinct_providers[0]` makes the wording transparently corpus-derived, which is the correct framing for an Axis 3 (Claims validity) string.

The wording I suggested was "(Google Gemini)" because that was the only provider in the cohort under review; the Architect's templated form renders identically for this corpus and generalizes cleanly. PASS.

### 2. D24 — conditional mechanism wording binding

**Ruling: PASS.** Architect was right to upgrade my "optional but preferred" to binding. My original wording reflected reasonable methodological caution (don't over-engineer the script for a single corpus); Architect's escalation reflects correct project-management judgment (a future Amendment 5 the moment a multi-provider safety cohort surfaces is more expensive than a 6-line branch now).

The three-branch logic is methodologically clean:
- `n_providers >= 2`: original Amendment-3 D20 wording. **Correct** — preserves the cross-provider phrasing for any future cohort that does meet the threshold.
- `n_providers == 1`: D23 single-provider wording. **Correct** — names the provider, narrows the replication claim to cross-domain-within-provider.
- `n_providers == 0`: error rather than malformed string. **Correct** — this state is unreachable when disposition is CONFIRMED or higher (the disposition logic itself requires at least one provider in the safety cohort), so an error is the right defensive posture rather than a fallback string.

PASS.

### 3. D25 — option (b) defensive-guardrail symmetry

**Ruling: PASS.** I offered two acceptable resolutions in the T4 verdict. Architect adopted option (b) — render the mechanism string in both branches with the defensive guardrail in both. The Architect's rationale is methodologically sound:

- Option (a) (suppress mechanism string in plain-CONFIRMED) would lose information that T5 §8.2 needs. The K-frame/K-vocab bipartite mechanism description is methodologically interesting at CONFIRMED tier, not only at CONFIRMED-with-mechanism. The disposition tier is about replication strength; the mechanism description is about attribution structure. They are orthogonal axes.
- Option (b) preserves information and aligns the render shape across branches. The cost is duplicating a four-line guardrail block, which the Architect correctly notes is acceptable.

The methodological intent of the defensive guardrail ("mechanism description, not a claim about the model's internal state") is **wherever the mechanism string is rendered**, regardless of disposition tier. Option (b) honors that intent. PASS.

### 4. D26 — Required #2 + Required #3 bundled into one Coder commit

**Ruling: PASS, do not split.** The two changes touch the same render-branch code path (lines ~543–551 for the conditional wording, lines 826–857 for the symmetric branches). They are mechanically coupled — changing one without the other would produce a transient state where the conditional wording exists but is not symmetrically rendered, or vice versa. Splitting produces two ~10-line diffs in the same file with no independent review value.

CLAUDE.md §8 ("one commit per task") applies per task, not per SME-required item. T4.2-followup is one task with two acceptance criteria. The Architect's bundling rationale is correct.

PASS.

### 5. D27 — §3.3 canonical wording

**Ruling: PASS.** The Coder's rephrase ("...not a claim about the model's internal state") supersedes Amendment 3's "...not what the model believes" as canonical. This is the §1.5-clean wording I endorsed in the T4 verdict (Finding 3). Folding it back into Amendment 3 §3.3 as canonical is the correct housekeeping move — T5 §8.2 quotes the canonical wording, not the original, and the binding documents are consistent.

For audit-trail clarity: the original "believes" wording was a §7 forbidden-vocabulary violation in a self-disclaimer. The Coder caught it during implementation. The Architect promotes the catch to canonical. The Reviewer's §7 spot-check on T5 §8.2 will find clean copy.

PASS.

### 6. T5 §8.2 unblock condition — does the regenerated markdown artifact need a fresh SME output review?

**Ruling: NO. Amendment 4 PASS + Reviewer/Tester PASS on T4.2-followup is sufficient. T5 §8.2 unblocks at that point.**

Reasoning:
- The methodology decisions (D23, D24, D25, D27) are settled by this verdict. The Coder work is mechanical: render-branch logic + test fixture extension + markdown re-generation. There are no further methodology calls to make.
- The Amendment 4 plan correctly states (§3, "Methodologically significant?": No) that no second SME review on the T4.2-followup commit is required. I concur. The Reviewer's §7 vocabulary spot-check + the Tester's fixture coverage are the gates that matter for the regenerated markdown.
- The T4.2-followup acceptance criteria explicitly require the regenerated markdown's "Mechanism description" section to match D23's exact rendered string for this corpus. That is a Reviewer/Tester check, not an SME check.
- The next SME gate is the **T5 SME output review** (after T5 lands). T5 §8.2 will quote the regenerated mechanism string verbatim; if the regeneration is wrong, the T5 SME review catches it then. This is the correct gate placement — SME reviews methodological output, not mechanical regeneration of a string the SME already approved.

To be unambiguous about the Coder's unblock state: **the Coder unblocks on T4.2-followup the moment this verdict file lands.** No additional SME gate is required between this PASS and the Coder commit. The next SME gate is the T5 output review.

### 7. Carry-forward count reconciliation — 31 binding notes

**Ruling: PASS.** Amendment 4 §6 correctly reconciles the count.

Audit:
- 8 original Phase 4a.1 plan binding notes
- A1–A8 from Amendment 1 (8 notes)
- B1–B6 from T3B-detector verdict (6 notes)
- B7, B8, B9 from Amendment 2 verdict (3 notes)
- B10, B11, B12 from T3C verdict (3 notes)
- B13, B14, B15 from Amendment 3 verdict (3 notes)

Total: 8 + 8 + 6 + 3 + 3 + 3 = **31**.

Amendment 3 stated 28 because B13/B14/B15 were added at the *Amendment 3 verdict* (not at Amendment 3 itself), and B7–B9 plus B10–B12 may have been counted differently in different documents. The T4 SME output verdict restated the total as 31. Amendment 4 adopts that count. The reconciliation is correct.

Amendment 4 adds **no new binding notes**. D23–D27 are dispositions that resolve T4 SME Required items, not new methodology rules. The 31 count is unchanged after this verdict.

---

## Verdict

**CDA SME VERDICT: PASS**

| Axis | Verdict |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | PASS |
| Axis 3 — Claims validity | PASS (D23 wording revision resolves the T4 FAIL on the stale "cross-provider" claim) |
| Axis 4 — Audience translation | PASS (D25 option (b) symmetry resolves the asymmetric defensive guardrail; D27 canonical §3.3 wording is §1.5-clean) |
| Register compliance | N/A (instrument calibration; not a register-level finding) |
| Vocabulary compliance | PASS (canonical "not a claim about the model's internal state" is §1.5-clean) |

This is a clean, focused amendment that satisfies all four Required items from the T4 SME verdict. The Architect's two refinements beyond the SME-required minimum (templating the provider name from `distinct_providers[0]`; binding D24 rather than leaving it optional) both improve the amendment without changing its scope. The bundled D26 commit shape is correct.

---

## Critical question: Coder unblock posture

**The Coder unblocks on T4.2-followup the moment this verdict file lands. No additional gates required.**

Specifically:
- This SME PASS is the gate Amendment 4 §5 names ("CDA SME PASS or PASS-WITH-NOTES on §2 + §3 + §4"). It is hereby PASS.
- The Coder may start T4.2-followup immediately.
- The Reviewer + Tester gates fire on the T4.2-followup commit per normal pipeline rules.
- T5 §8.2 unblocks after the T4.2-followup commit lands and Reviewer/Tester PASS.
- T5 §1, §8.1, §8.3, §8.4 stay unblocked from the T4 verdict (parallel work permitted).
- The next SME gate after this one is the T5 SME output review.

No fresh SME output review is required on the regenerated T4.2 markdown artifact. The methodology decisions are settled here; the Coder work is mechanical; Reviewer + Tester catch any regression.

---

## What this verdict does NOT require

To prevent scope creep from a "PASS" verdict:

- **No re-running** of any prior collection or classification work. The 27-row corpus and the 9-row safety subtype hand-code are unchanged.
- **No re-opening** of D17, D18, D19, D21, D22 (Amendment 3 dispositions). Amendment 4 §1 explicitly excludes them; this verdict honors that exclusion.
- **No schema changes.** No `cdb_core/schemas.py` touches. No `DATA_DICTIONARY.md` updates. (Amendment 4 §1 already states this; reaffirmed here.)
- **No new binding notes.** The 31-count is final.
- **No additional SME gate** between this PASS and the Coder's T4.2-followup commit.
- **No Amendment 5** anticipated for Phase 4a.1. T5 closes Phase 4a.1.

---

## Carry-forward — 31 binding notes after this verdict

This verdict adds **no new binding notes** and reconciles the count to 31, unchanged from the T4 verdict.

| Note set | Status |
|---|---|
| 8 original Phase 4a.1 plan binding notes | All in force |
| A1–A8 from Amendment 1 | All in force |
| B1–B6 from T3B-detector verdict | All in force |
| B7, B8, B9 from Amendment 2 verdict | All in force |
| B10 (soft, future batches) | Carried forward |
| B11 (binding on T4) | Decomposed by Amendment 3; verified at T4.2 output gate; mechanism wording revised at Amendment 4 |
| B12 (binding precedent, future batches) | Carried forward |
| B13 (soft, K-frame refinement at N≥10) | Not triggered on this corpus; carried forward |
| B14 (binding, T5 §8.1/§8.2 numerics-vs-interpretation separation) | In force for T5 |
| B15 (soft, dashboard glossing) | Carried forward |

Total: **31**.

---

## Summary for the Architect (and Mark)

- **Clean PASS.** All four Required items from the T4 verdict are resolved. The Architect's two refinements (templated provider name, binding D24) are both improvements.
- **Coder unblocks now.** No additional SME gates between this verdict and the T4.2-followup commit.
- **No fresh SME review on the regenerated markdown.** Reviewer + Tester catch any regression in the rendered string. The next SME gate is the T5 SME output review.
- **T5 §8.2 unblocks** after T4.2-followup lands and Reviewer/Tester PASS.
- **31 binding notes carry forward unchanged.** No new notes added by this verdict.
- **Phase 4a.1 is on track to close at T5.** No Amendment 5 anticipated.

The amendment is small, focused, and methodologically clean. The data-refines-prediction story (T3B SME spot-check → full-corpus classification → single-provider posture) is now fully accommodated in the binding documents. Good gate-chain hygiene.

---

*Posted to `#lsb-cda-sme`. Binding for T4.2-followup commit gating and T5 §8.2 wording. The CDA SME has no further blockers on Phase 4a.1 between here and T5.*
