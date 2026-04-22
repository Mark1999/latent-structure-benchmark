# Phase 4a 12-Model Slate — CDA SME Verdict

**Date:** 2026-04-22
**Reviewer:** CDA SME (agent)
**Slate reviewed:** Architect verdict §1 in `docs/status/2026-04-22-phase4a-kickoff-architect-verdict.md`
**Channel:** `#lsb-cda-sme` (saved to repo per preference)
**Preceding gates (all PASS):** B2 backup, 2026-04-21 findings review, Position C decision, Position C replay, Phase 4a Architect verdict

---

## Verdict: **PASS-WITH-NOTES**

| Axis | Result |
|---|---|
| Protocol validity | **PASS** |
| Analytical validity | **PASS-WITH-NOTES** |
| Claims validity | **PASS-WITH-NOTES** |
| Audience translation | **PASS-WITH-NOTES** |

| Compliance | Result |
|---|---|
| Register compliance | PASS |
| Vocabulary compliance | PASS |

**T1 adapter preflight is unblocked.** None of the notes below must fire before T1.

---

## Axis 1 — Protocol validity: PASS

The slate is applied against the full CDA protocol (`--mode cross_model`, free-list + pile-sort + interview) at N=5 runs per cell, `--pile-sorts 1`, default temperatures (0.7/0.3/0.3). This matches `ARCHITECTURE.md` §4.1.3 and satisfies the LSB adaptation table at §4.2.0. Register 2 is the target analytic register — each model acts as an informant with equal voice. Coverage (3 origins, 2 openness states, 5 collection_methods) exceeds the shakedown diversity floor in `SHAKEDOWN_PROTOCOL.md` §4.

## Axis 2 — Analytical validity: PASS-WITH-NOTES

**n=12 is at the Romney CCM small-n floor.** §1.5 and `SME_REVIEW.md` treat n<15 as requiring the `romney_small_n_warning` annotation. Phase 4a is therefore a **small-n canonical run by design**. This is acceptable — it matches the §7 decision #3 slate count — but:

- **Note A [forward, Phase 4a downstream]:** T5 `DomainResult` must populate `romney_small_n_warning=True` and any dashboard copy drawing on CCM-based consensus must render the small-n caveat. CDA SME will not PASS T5 without this.
- **Note B [forward]:** The stored-vs-rerun `qa_passed` divergence from the Position C verdict will reproduce here. At 120 records, Check 2's pool-aggregation will compute freelist-uniqueness against the completed cohort; some records that stored `qa_passed=True` at collection time may re-run False. T6 is the correct place to surface this.

**Lineage pairs** (Claude Opus/Sonnet, GPT/GPT-mini) are analytically informative, not distorting. At Register 2, informant-weighted consensus treats each as an equal voice; lineage clustering is an empirical finding if it appears, not a slate flaw. The OCI-weighted Option C diagnostic is the correct place to inspect it.

**Grok-4 inclusion is methodologically important.** xAI is a distinct model family; dropping it would collapse US closed-weight diversity from four to three families (Anthropic, OpenAI, Google) and concentrate signal around the three established labs. Keep Grok-4 gated behind T1 preflight as planned; if the adapter fails, document and re-compose per T1 acceptance. **Do not pre-emptively drop Grok-4.**

## Axis 3 — Claims validity: PASS-WITH-NOTES

- **Note C [must be addressed before any Phase 4a public copy]:** The minimum publishable claim after this slate runs — assuming T5 reproduces the 2026-04-21 centrality pattern — is **"across 12 models drawn from 3 origins and 2 openness states, the corpus-lens structure shows [pattern] with the n=12 CCM caveat."** The "coherent corpus-lens structure" language from the Position C replay verdict Note 4 may migrate into public copy **only under that full hedged framing**, not as a standalone headline. Dashboard ledes must retain the four-layer corpus-lens definition per `DESIGN_SYSTEM.md` and the small-n annotation.
- **Note D [forward]:** No ceiling claim is possible from Phase 4a alone. Phase 4c human baseline acquisition is the prerequisite for any "location relative to human consensus" framing. Until 4c lands, all Phase 4a claims are floor claims (model-to-model comparison only). Reviewer and CDA SME will reject any T5-downstream text that implies proximity to a human baseline.

## Axis 4 — Audience translation: PASS-WITH-NOTES

- **Note E [must be addressed before any Phase 4a public copy]:** The US-weighted composition (7/12) is defensible as reflecting frontier-model market reality, but generated dashboard copy must carry an explicit caveat: *"The slate reflects the frontier closed-weight market, which is US-concentrated; EU open-weight is zero in this sample."* This belongs on the methodology page as a named limitation, not a footnote. No addition of a fourth origin class or 5th-origin EU addition is required for v1 — adding a Cohere or similar model on CDA-SME authority alone would be scope creep — but the caveat copy is non-negotiable.
- **Domain expansion (family + holidays) is consistent with §5.3 intent.** §5.3 Phase 4a text says "run the full family domain" but the Phase 6 roadmap commits holidays as the next domain, the shakedown demonstrated both parse identically, and each domain produces its own independent `DomainResult`. Marginal cost at N=5 is small. PASS on scope expansion.
- **Canonical-only model_ids (alias exclusion): PASS.** Aliases are registry pointers; canonical dotted-forms produce the same adapter routing and output. No methodological issue.

---

## Register and vocabulary compliance: PASS

Slate composition is for a Register 2 between-model analysis. R1 within-model OCI applies per model; R3 drift analysis is deferred to Phase 4d. No R1/R2 confusion in the kickoff doc. No forbidden vocabulary appears in the slate documentation. Forward requirement: any generated T5-downstream copy must remain §1.5.4-compliant.

---

## Required before T1 runs

**None.** The slate composition is cleared for T1 preflight.

## Required before Phase 4a downstream (T5 and later)

1. **Note A:** T5 must populate `romney_small_n_warning=True`; CCM-derived copy must render the caveat.
2. **Note C:** Public copy migrating the "coherent corpus-lens structure" phrasing must carry the full "12 models across 3 origins / n=12 caveat / Register 2 between-model" framing.
3. **Note D:** No ceiling claims until Phase 4c lands.
4. **Note E:** Methodology page must explicitly name the US-weighted composition as a sample limitation, with the zero-EU-open-weight gap called out.

Note B is a T6 concern and does not block T5.

---

## Downstream implications — minimum publishable claim after Phase 4a

Assuming T5 reproduces the 2026-04-21 centrality pattern, the minimum publishable claim is **Register 2 between-model relative structure with the n=12 CCM caveat and the US-weighted sample caveat.** Absolute claims, ceiling claims, and any "closer to human" framing remain forbidden until Phase 4c.

---

*End of verdict. Slate PASS-WITH-NOTES. T1 preflight unblocked.*
