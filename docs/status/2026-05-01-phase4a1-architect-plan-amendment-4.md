# Phase 4a.1 — Architect Plan Amendment 4 (task #21)

**Date:** 2026-05-01
**Planner:** Architect
**Task:** #21 (Phase 4a.1 decline-interview backfill) — **AMENDMENT 4**
**Scope:** D20 mechanism wording revision + Amendment 3 §3.3 §1.5-clean rephrase canonicalization + one bundled Coder follow-up task (T4.2-followup) covering the conditional mechanism wording AND the defensive-guardrail asymmetry fix. Focused, additive on Amendment 3.
**Supersedes partially:** `docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md` D20 wording and §3.3 acceptance-criteria sentence only. All other Amendment 3 content carries forward verbatim.
**Carries forward:** All **31** binding notes in force after the T4 SME output verdict (8 original + A1–A8 + B1–B15). Reconciles the count: Amendment 3 stated 28 (B1–B12); the T4 SME verdict restates the total as 31, which folds in B13/B14/B15 added by the Amendment 2 verdict (B7–B9) + T3C verdict (B10–B12) + T3B-detector Ruling 3 follow-ups recounted by SME at T4. Amendment 4 adopts SME's count of 31.
**Predecessor verdicts (still binding, full chain):** as enumerated in Amendment 3 + `docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md` (T4 output gate, PASS-WITH-NOTES).

**Trigger:** T4 SME output gate (2026-05-01) returned PASS-WITH-NOTES with Axis 3 FAIL on the mechanism string at `scripts/phase4a1_note_j_crosstab.py:550` — the carried-through D20 phrase "cross-provider replication on the family and holidays domains" is falsified by Mark's full-corpus classification (9/9 safety attributions are single-provider, Google Gemini). SME also identified (a) the Coder's §3.3 rephrase as canonical-worthy and (b) a defensive-guardrail asymmetry between the CONFIRMED-with-mechanism and plain-CONFIRMED rendering branches (script lines 826–857).

**No schema changes. No `cdb_core/schemas.py` touches. No `DATA_DICTIONARY.md` updates. No new dependencies. No re-opening of D17, D18, D19, D21, D22.**

**Expected spend:** $0.

---

## 1. Summary

Amendment 4 revises **only** the D20 mechanism-string wording to match the empirical posture of the corpus (single-provider, cross-domain) and folds the Coder's §1.5-clean rephrase ("not a claim about the model's internal state") into Amendment 3 §3.3 as canonical. It also bundles one small Coder follow-up (T4.2-followup) that (a) makes the script compute the mechanism wording **conditionally** on `n_providers` so a future multi-provider cohort emits the original cross-provider phrasing automatically, and (b) fixes the defensive-guardrail asymmetry at script lines 826–857. T4.2-followup is a single Coder commit; Required #2 and Required #3 from the SME verdict are bundled because they touch the same render-branch code path and splitting them produces two ~10-line diffs in the same file with no independent review value.

---

## 2. Architect dispositions for this amendment (continuing numbering from D22)

- **D23 — D20 mechanism wording revision (canonical, single-provider phrasing).** D20's mechanism string is revised to:
  > **"provider-safety-layer activation with two co-present trigger patterns — (a) AI-vs-human-research-subject framing (K-frame; N={k_frame_count}), (b) list-comprehensiveness/sensitivity vocabulary without K-frame (K-vocab; N={k_vocab_count}) — cross-domain replication on the {domain_str} domains within a single provider ({provider_name})"**

  Where `{k_frame_count}`, `{k_vocab_count}`, `{domain_str}` are computed as before, and `{provider_name}` is the single distinct provider name when `n_providers == 1` (e.g., `"Google Gemini"`). For this corpus the rendered string is:
  > "provider-safety-layer activation with two co-present trigger patterns — (a) AI-vs-human-research-subject framing (K-frame; N=2), (b) list-comprehensiveness/sensitivity vocabulary without K-frame (K-vocab; N=7) — cross-domain replication on the family and holidays domains within a single provider (Google Gemini)"

  This adopts the SME-suggested wording verbatim. The Architect's only refinement: the parenthetical provider name is **rendered from the actual `distinct_providers[0]`** (the script already has it in scope) rather than hardcoded "Google Gemini", to preserve generality across re-runs.

- **D24 — Conditional mechanism wording is binding (resolves SME Required #2; was "optional but preferred").** The script must branch the mechanism wording on `n_providers`:
  - `n_providers >= 2`: emit the **original Amendment-3 D20 wording** ("cross-provider replication on the {domain_str} domains") with no provider-name parenthetical. This preserves the wording for any future cohort that does meet the cross-provider threshold.
  - `n_providers == 1`: emit the **D23 wording** above with the single provider named.
  - `n_providers == 0`: not a reachable state when CONFIRMED is the disposition; if reached, the script should error rather than emit a malformed string.

  Architect's call: **bind it.** Rationale: the SME flagged it "optional but preferred"; the cost of leaving the wording static and re-amending later when a multi-provider cohort surfaces is materially higher than the cost of branching the string now. The branch is mechanical (~6 lines). Treating it as soft would require a future Amendment 5 the moment Phase 4b lands a multi-provider safety cohort.

- **D25 — Defensive-guardrail asymmetry fix is binding (resolves SME Required #3).** Of the SME's two acceptable resolutions, Architect adopts **option (b): render the mechanism string in both disposition branches with the defensive guardrail in both branches.** Rationale:
  - Option (a) (suppress mechanism string in plain-CONFIRMED) loses information that the T5 §8.2 author needs (the bipartite K-frame/K-vocab mechanism description is methodologically interesting at CONFIRMED tier, not only at CONFIRMED-with-mechanism).
  - Option (b) preserves information and aligns the render shape across branches, at the cost of duplicating the four-line guardrail block. The duplication is acceptable; the alternative would have T5 §8.2 reading two different document shapes depending on disposition tier, which compounds maintenance.

  The plain-CONFIRMED branch (current lines 838–857) is rewritten to mirror the CONFIRMED-with-mechanism branch's structure: heading "Mechanism description", blockquoted mechanism string, the four-line "what the model's output attributes" defensive guardrail, then the existing disposition-explanation paragraph ("Note: disposition is `CONFIRMED` (not CONFIRMED-with-mechanism) because the cross-provider replication threshold ({N} distinct providers) is not met...") preserved verbatim.

- **D26 — Bundle Required #2 + Required #3 into a single Coder commit (T4.2-followup).** Both touch the render-branch logic in the same function block (lines ~543–857). Splitting produces two ~10-line diffs in the same file with no independent review value. CLAUDE.md §8 "one commit per task" applies per task, not per SME-required item; T4.2-followup is one task with two acceptance criteria.

- **D27 — Canonical §3.3 wording: adopt the Coder's §1.5-clean rephrase.** Amendment 3 §3.3's "...not what the model believes" is superseded by **"...not a claim about the model's internal state"**. This is the canonical wording for any T5 §8.2 quotation. The Reviewer §7 forbidden-vocabulary check is what prompted the Coder's rephrase; the SME endorsed it as "methodologically faithful, §1.5-clean, slightly better than original". Folding it back is housekeeping but it must be done explicitly here so T5 §8.2 quotes the §1.5-clean version, not the original.

---

## 3. T4.2-followup task body (the only new Coder work)

**Scope:** One commit. Apply D24 + D25 to `scripts/phase4a1_note_j_crosstab.py`. No other files change except the matching test fixture in `tests/test_phase4a1_note_j_crosstab.py` (extend, do not rewrite).

**Acceptance criteria:**
- Lines ~543–551: replace the static mechanism-string assignment with a conditional branch on `n_providers`. When `n_providers == 1`, format includes "cross-domain replication on the {domain_str} domains within a single provider ({distinct_providers[0]})". When `n_providers >= 2`, format is the Amendment-3 original ("cross-provider replication on the {domain_str} domains"). When `n_providers == 0` and disposition is CONFIRMED or higher, raise a clear error.
- Lines 838–857: rewrite the plain-CONFIRMED render branch to mirror the CONFIRMED-with-mechanism branch (heading "Mechanism description", blockquoted mechanism string, four-line defensive guardrail, then the preserved disposition-explanation paragraph). Use a shared helper function if the duplication bothers the Reviewer; otherwise the explicit duplication is acceptable.
- Test fixture coverage: extend `tests/test_phase4a1_note_j_crosstab.py` with (i) a single-provider 9-row safety cohort that asserts the rendered mechanism string contains "within a single provider (Google Gemini)" and not "cross-provider replication"; (ii) a synthetic multi-provider 6-row cohort that asserts the rendered string contains "cross-provider replication" and does NOT contain "within a single provider"; (iii) a plain-CONFIRMED render assertion that the four-line defensive guardrail substring ("a mechanism description, not a claim about the model's internal state") appears in the markdown output.
- Re-run on the actual corpus produces a markdown output where §"Mechanism description" matches D23's exact rendered string for this corpus.
- `uv run ruff check . && uv run mypy packages/ && uv run pytest` green.
- No forbidden vocabulary in the new test fixtures or rendered strings.

**Inputs:**
- `/opt/lsb-agent/scripts/phase4a1_note_j_crosstab.py` (lines ~543–551, 826–857)
- `/opt/lsb-agent/tests/test_phase4a1_note_j_crosstab.py`
- `/opt/lsb-agent/data/derived/decline_interviews_safety_attribution_subtype.jsonl` (read-only, no change)

**Outputs:**
- Updated script + test file. Re-run produces revised T4.2 output markdown. The on-disk T4.2 output artifact (the markdown rendering) is regenerated as part of this commit so T5 §8.2 quotes the corrected version.

**Touches `cdb_core/schemas.py`?** No.
**`DATA_DICTIONARY.md`?** No.
**Methodologically significant?** No — the methodology decisions live in D23/D24/D25 above; the Coder work is mechanical. This amendment's CDA SME PASS is the gate; no second SME review on the T4.2-followup commit is required.

**Commit message:** `fix(scripts): D23/D24/D25 — conditional mechanism wording + symmetric defensive guardrail (task #21.T4.2-followup)`. Body references this amendment + the T4 SME verdict + the Amendment 4 SME verdict file path.

---

## 4. Amendment 3 §3.3 canonical wording (D27)

§3.3 ADDITION to §8.2 acceptance criteria, second-to-last sentence, is canonicalized to:

> "The framing is **what the model's output *attributes* the safety event to**, not a claim about the model's internal state."

(was: "...not what the model believes.")

T5 §8.2 quotes the canonical wording. T5 §8.2 also quotes the D23 mechanism string (not the original D20 string). T5 §8.2 cites the empirical narrowing per the SME's recommended framing in the T4 verdict ("On this 27-row corpus the safety-event-attribution pattern is observed only in the Google Gemini cohort, replicating cross-domain (family and holidays) within that provider. The cross-provider replication that the T3B SME spot-check anticipated based on sampling did not surface in the full-corpus classification. The CONFIRMED disposition therefore reflects a single-provider, two-domain finding rather than a cross-provider finding.").

**T5 §1, §8.1, §8.3, §8.4 unblock state per the T4 SME verdict is unchanged by this amendment.** T5 §8.2 unblocks only after Amendment 4 CDA SME PASS lands AND T4.2-followup commit lands.

---

## 5. Gate chain for this amendment

```
Architect Amendment 4 (this document)
  ─► CDA SME PASS or PASS-WITH-NOTES on §2 + §3 + §4
       (verdict at docs/status/2026-05-01-phase4a1-amendment-4-cda-sme-verdict.md)
  ─► Coder: T4.2-followup commit (D24 + D25, bundled)
  ─► Reviewer PASS
  ─► Tester PASS
  ─► T5 §8.2 unblocked (T5 §1, §8.1, §8.3, §8.4 already unblocked from T4 SME verdict)
  ─► T5 SME output gate
  ─► Phase 4a.1 closes
```

---

## 6. Carry-forward — 31 binding notes still in force

Reconciling the count: Amendment 3 stated 28 (8 + A1–A8 + B1–B12). The T4 SME output verdict restates the total as 31, accommodating B13/B14/B15 added at the Amendment 2 SME verdict and Amendment 3 SME verdict (B13: K-frame definition refinement at N≥10, soft; B14: T5 §8.1/§8.2 numerics-vs-interpretation separation, binding; B15: dashboard glossing, soft). Amendment 4 adopts the SME's count: **31**. No new binding notes added by this amendment.

| Note set | Status |
|---|---|
| 8 original Phase 4a.1 plan binding notes | All in force |
| A1–A8 from Amendment 1 | All in force |
| B1–B6 from T3B-detector verdict | All in force |
| B7, B8, B9 from Amendment 2 verdict | All in force |
| B10 (soft, future batches) | Carried forward |
| B11 (binding on T4) | Decomposed by Amendment 3; verified at T4.2 output gate |
| B12 (binding precedent, future batches) | Carried forward |
| B13 (soft, K-frame refinement at N≥10) | Carried forward |
| B14 (binding, T5 §8.1/§8.2 numerics-vs-interpretation separation) | In force for T5 |
| B15 (soft, dashboard glossing) | Carried forward |

Total binding notes on Phase 4a.1 after this amendment: **31** (unchanged).

---

## 7. Files (absolute paths)

**Inputs (this amendment reads):**
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md`
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md`
- `/opt/lsb-agent/scripts/phase4a1_note_j_crosstab.py` (lines 543–551, 826–857)

**Outputs (this amendment introduces / mutates):**
- `/opt/lsb-agent/scripts/phase4a1_note_j_crosstab.py` (T4.2-followup edits)
- `/opt/lsb-agent/tests/test_phase4a1_note_j_crosstab.py` (T4.2-followup fixture additions)
- T4.2 markdown output artifact (regenerated)

**Gate verdict files:**
- `/opt/lsb-agent/docs/status/2026-05-01-phase4a1-architect-plan-amendment-4.md` (this doc)
- `/opt/lsb-agent/docs/status/2026-05-01-phase4a1-amendment-4-cda-sme-verdict.md` (required before T4.2-followup Coder start)

---

## 8. Summary for Mark

- **Tiny amendment.** D20 wording revised (single-provider). §3.3 §1.5-clean rephrase made canonical. One small Coder follow-up bundles the conditional-wording branch and the guardrail-symmetry fix.
- **No schema work. No `DATA_DICTIONARY.md`. $0 spend.**
- **D17, D18, D19, D21, D22 not re-opened.**
- **T5 §1, §8.1, §8.3, §8.4 stay unblocked.** Only §8.2 waits on Amendment 4 SME PASS + T4.2-followup commit.
- **Required gate before Coder starts T4.2-followup:** CDA SME PASS or PASS-WITH-NOTES on this amendment.

---

*End of Architect Plan Amendment 4. Binding for T4.2-followup and T5 §8.2 wording. All 31 prior binding notes remain in force.*
