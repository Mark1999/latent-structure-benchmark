# CDA SME verdict, batch A openai/gpt-5.5 provider-forced temperature

**Date:** 2026-07-10
**Task:** batch A model-refresh campaign, openai/gpt-5.5 admissibility under provider-forced temperature=1.0
**Verdict:** PASS-WITH-NOTES

## Scorecard

| Axis | Result |
|---|---|
| Axis 1, protocol validity | PASS-WITH-NOTES |
| Axis 2, analytical validity | PASS-WITH-NOTES |
| Axis 3, claims validity | PASS-WITH-NOTES |
| Axis 4, audience translation | PASS-WITH-NOTES |
| Register compliance | PASS |
| Vocabulary compliance | PASS |

## Ruling

openai/gpt-5.5 enters the batch A slate at provider-forced temperature=1.0. Dropping the informant because the provider restricts the parameter would introduce a selection bias worse than the sampling-regime disparity itself, and the restriction is a documentable property of the informant under the failures-are-findings posture (Pitfall 4 analogue: absence framing is not a defect, and provider-imposed capacity limits are informant properties, not benchmark failures). The correct move is inclusion with disclosure, not exclusion. This sets the forward precedent for the reasoning-model class generally.

The concern is real: the pile_sort and interview steps are protocol-specified at 0.3, and forced 1.0 is a substantive hotter regime on the two steps where determinism matters most. That will plausibly inflate within-model output variance (depressing OCI at Register 1) and depress the model's competence loading at Register 2. The remedy is disclosure at every surface where those numbers appear, not silent inclusion and not exclusion.

## Binding notes

**N1, capacity_note verbatim on every gpt-5.5 record:**
"Provider (OpenAI) forces temperature to default 1.0 for this model, so the 0.3 pile-sort and interview temperatures could not be applied. top_p is likewise not accepted. Sampling regime is hotter than the LSB protocol on pile_sort and interview steps."

**N2, methodology page footnote (next scheduled update):** must name gpt-5.5 by model_id, state that provider-forced temperature=1.0 applies across all three protocol steps (0.7 free_list, 0.3 pile_sort, 0.3 interview all forced to 1.0), and frame the restriction as an informant property, not a benchmark defect. No "closer to human" or "worse informant" framing.

**N3, Register 1 disclosure:** the OCI eigenratio for gpt-5.5 carries a per-model annotation on the dashboard: "measured under provider-forced default sampling; within-model output concentration is not directly comparable to protocol-temperature informants." OCI is published, not withheld.

**N4, Register 2 disclosure:** if gpt-5.5's Romney CCM competence loading falls in the lower quartile of the panel, the methodology page must flag that the loading may reflect hotter sampling on the sorting steps rather than a corpus-lens property. The disclosure is symmetric: do not use the restriction to promote or demote the informant in narrative copy.

**N5, precedent, forward:** treat this ruling as the template for any future informant with provider-forced sampling. Any additional restrictions (top_p, top_k, reasoning_effort, etc.) also go into capacity_note using the same "provider forces X, protocol value Y could not be applied" pattern.

**N6, verify before collection:** confirm the gpt-5.6 family restriction empirically with a minimal API probe before starting batch A collection. Do not presume symmetry with gpt-5.5. If gpt-5.6 accepts the protocol temperatures, it enters as a protocol-conformant informant with no disclosure needed.

**N7, drop-scope:** this ruling does NOT authorize dropping gpt-5.5 from the informant panel silently at analysis time or filtering it out of consensus computations. The record enters the panel; the disclosure attaches to the surface, not to the exclusion.

## Rationale, brief

The two-register comparability concern is genuine but bounded. At Register 1, OCI is a per-informant concentration statistic and the annotation lands per-model, so cross-model comparability is preserved by disclosure rather than by protocol uniformity. At Register 2, Romney CCM is robust to per-informant noise heterogeneity in the sense that a single hotter informant does not corrupt the panel consensus; it just carries a lower competence loading. Publishing the loading with the sampling-regime caveat is the honest move.

The alternative, dropping OpenAI from batch A entirely, would leave a coverage hole at the frontier of the reasoning-model class exactly when the reasoning-model class is the interesting cohort for a refresh. That is a worse epistemic outcome than a disclosed regime disparity.

Rule 15 (math freeze) is not implicated. No estimator, resampling scheme, or threshold semantic changes.
