# Phase 4a T5 — CDA SME Verdict (first canonical DomainResults)

**Date:** 2026-04-23
**Reviewer:** CDA SME (agent)
**Commit reviewed:** `d74ce57 feat(results): Phase 4a T5 analysis — family + holidays DomainResults (task #13)`
**Artifacts reviewed:**
- `data/results/family/0.1.json` (n=10 models)
- `data/results/holidays/0.1.json` (n=8 models)
- `docs/status/2026-04-23-phase4a-t5-analysis-report.md`
**Preceding gates:** Architect verdict §4 T5 + Amendment A (mode=single_pass); slate SME PASS-WITH-NOTES (2026-04-22); decline-interview SME PASS-WITH-NOTES (2026-04-23); small-n threshold reconciliation (2026-04-23, n<15).

---

## Overall verdict: **PASS-WITH-NOTES**

T5 is **mergeable**. T6 (QA sweep) is **GO**. Four-axis scorecard below; no must-fix items block T5. One new forward concern (Note K) surfaced pre-remediation.

| Axis | Result |
|---|---|
| Protocol validity | **PASS** |
| Analytical validity | **PASS-WITH-NOTES** |
| Claims validity | **PASS-WITH-NOTES** |
| Audience translation | **PASS** |
| Register compliance | PASS |
| Vocabulary compliance | PASS |

---

## Axis 1 — Protocol validity: PASS

T5 applied the Register 2 analysis stack correctly:
- Smith's S, Sutrop CSI, co-occurrence matrices, Romney CCM, Caulkins centrality.
- MDS with B=500 bootstrap ellipses (R11 uncertainty satisfied).
- `qa_passed` filtering applied correctly before analysis — both domains reflect the post-QA corpus (family n=10 from 41 records, holidays n=8 from 33 records).

No invalid filtering; `check_9_backup_freshness` did not contaminate the per-record QA state (it's an infrastructure check; its per-record firing is a known cosmetic issue per prior Reviewer note and does not mutate `qa_passed`).

## Axis 2 — Analytical validity: PASS-WITH-NOTES

- **`romney_small_n_warning=True` correct** on both domains. n=10 and n=8 both trigger the n<15 threshold. The 2026-04-23 reconciliation verdict is honored.
- **`consensus_type=STRONG_CONSENSUS`** defensible: family eigenratio=10.79 and holidays eigenratio=9.22 both above the LSB operational threshold (5.0). The small-n warning is the honest caveat; the classification itself is correct.
- **`negative_centrality_flag=False`** on both: no subcultural/contested detection. Centrality ranges tight and positive ([0.23, 0.34] family; [0.23, 0.38] holidays), consistent with the 2026-04-21 shakedown pattern that the slate verdict Note C hedged.
- **G1 fields all None** — correct (no sensitivity cell in Phase 4a).
- **R11 (uncertainty):** `mds_uncertainty` populated with ellipse params on every model; `consensus_ci` and `similarity_ci` both populated. No point estimate without uncertainty. PASS.

**Note** (type b, Phase-4a-compatible forward concern):

The tightness of centrality ranges ([0.23–0.34] and [0.23–0.38]) reproduces the shakedown pattern under the slate's Note C hedged framing. **Phase 4a.1 decline-interview data may alter the min-publishable claim** once landed — that's Phase 4a.1 scope, not T5. PASS on T5.

## Axis 3 — Claims validity: PASS-WITH-NOTES

- **Note C update (cell-coverage denominator):** Report §6 states "Of the 12-model × 2-domain × N=5 design, 18 cells produced analyzable pile-sort data; 5 cells produced decline-interviewable outputs." Matches Note C update requirement (M+N=23; the remaining cell is Gemini × family = pre-session failure, not decline-interviewable via the informants-path trigger — handled via failures.jsonl trigger in #21).
- **Note D:** no ceiling/proximity-to-human-baseline claims. PASS (Phase 4c-gated).
- **Note E:** the US-weighted composition caveat binds **downstream** (dashboard, methodology page), not T5 itself. The report correctly notes "binding at T5" only for Notes A, C, G; Note E stays deferred to Phase 6+ copy.
- **Minimum publishable claim framing preserved** with the qualified denominator.

**Note K (new forward concern, type c — binding on future public copy):**

Pre-remediation signal: **4 of 5 decline-interviewable cells are CN-origin** (qwen/qwen3.6-plus × {family, holidays}; z-ai/glm-5.1 × {family, holidays}). Only 1 decline-interviewable cell is US-origin (x-ai/grok-4 × holidays).

Future methodology-page copy (Phase 6+) must read:
> *"US-weighted composition PLUS disproportionate CN-origin decline pattern (4 of 5 decline-interviewable cells)"*

NOT standalone "US-weighted." Frame as a **coverage / protocol robustness caveat**, NOT as a finding about CN model behavior, until Phase 4a.1 Note J cross-tab confirms the pattern is not an artifact of our elicitation protocol (prompt language, refusal training, API routing).

If subsequent Phase 4a.1 work confirms the pattern, formalize as a binding Note K amendment.

## Axis 4 — Audience translation: PASS

- **Note G exact wording** used at report line 175: *"5 cells produced no interpretable primary-step output; follow-up decline-interview data for these cells will be captured in Phase 4a.1."* Verbatim match. No speculation, no "refused" agency framing.
- §1.5 vocabulary compliance in the report: clean. No `worldview`, `believes`, `thinks` (applied to models), `cultural bias`, `refused` (as agency).
- Report's binding notes compliance table (§8) explicitly tracks which notes are applied at T5 vs deferred to downstream.

## Register compliance: PASS

Register 2 between-model analysis correctly applied. R1 within-model scores populate `WithinModelResult` per model. R3 drift not in Phase 4a scope.

## Vocabulary compliance: PASS

No §1.5.4 forbidden terms in the report, JSON annotations, or anywhere in the commit.

---

## Interaction with prior SME forward notes

- **Note A (small-n caveat):** honored. `romney_small_n_warning=True` on both domains.
- **Note B (stored-vs-rerun qa_passed):** T6 concern, not T5. Not tested here.
- **Note C (cell-coverage denominator):** honored in report §6.
- **Note D (no ceiling claims):** honored.
- **Note E (US-weighted composition):** now strengthened by Note K (CN-origin decline clustering).
- **Note F (version_drift_flag):** Phase 4a.1 runner concern; not T5.
- **Note G (exact wording for uninterviewed cells):** honored at line 175.
- **Note H (prompt versioning):** Phase 4a.1 runner concern; not T5.
- **Note I (dashboard copy):** Phase 6+; not T5.
- **Note J (Phase 4a.1 cross-tab):** remains binding on Phase 4a.1 runner.

## Required before Phase 4a downstream (T6, Phase 4a.1, Phase 6)

- **Phase 4a.1 runner (#21):** Note J cross-tab must be in the completion report; will determine whether Note K formalizes as a binding amendment.
- **Phase 6+ dashboard copy:** Note K framing replaces standalone Note E framing for US-weighted composition.
- **Minimum-claim framing:** public copy must reference the 18-analyzable + 5-decline-interviewable denominator (Note C update).

## Required before T5 merge

**None.** T5 is PASS-WITH-NOTES. The notes are forward-looking and do not block.

---

*End of verdict. T5 is mergeable. T6 GO. Note K carried forward for Phase 4a.1 and Phase 6+ methodology copy.*
