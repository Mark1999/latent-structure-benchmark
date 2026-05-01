# OPS-T4 Single-Informant Detail View — CDA SME Wireframe Verdict

**Date:** 2026-05-01
**Reviewer:** CDA SME (Opus)
**Scope:** Light-touch wireframe pre-review for OPS-T4 (rendering choices only).
**Out of scope:** DESIGN_SYSTEM.md / public dashboard / UI/UX gate (ops dashboard explicitly carved out per Architect).

---

## CDA SME VERDICT: PASS-WITH-NOTES

| Axis | Verdict |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | PASS (no derived stats computed; nothing to evaluate) |
| Axis 3 — Claims validity | PASS-WITH-NOTES |
| Axis 4 — Audience translation | PASS-WITH-NOTES |
| Register compliance | N/A (no Register 1/2/3 statistics rendered) |
| Vocabulary compliance | PASS |

The wireframe's core posture — verbatim everything, derived nothing — is correct and matches the Architect's scoping. The Coder can build it. Five small notes below.

---

## Per-question rulings

### Q1. Pile-sort label provenance (verbatim, never re-summarized) — PASS

This is the methodologically correct call. The model's pile label is part of the data; re-summarizing it would be a derived-label operation and would cross the SME line.

**The "Wrong group of words" worry is real but the answer is still verbatim.** When a model labels a pile something self-deprecating, idiosyncratic, or even nonsensical, that label *is* a finding — it tells Mark something about how the model treated the task. Qualifying it ("the model called this 'Wrong group of words'") would be acceptable framing if and only if the qualifier sits *outside* the verbatim content (e.g., a section header reading "Pile labels (model's own words, verbatim)" once near the top of the section, not on each label). One unobtrusive verbatim disclaimer at the top of Section 2 is sufficient — no per-label qualification.

**Note 1 (PASS-WITH-NOTES):** Add a single short header line to Section 2 along the lines of "Pile labels and member ordering are the model's own output, verbatim. Not re-summarized or re-ordered." This makes provenance explicit without per-pile qualification.

### Q2. Singletons as their own collapsible section — PASS-WITH-NOTES

The intent (so they don't visually disappear) is correct. The execution risk is the opposite of what the wireframe describes: a *collapsible* section can hide singletons even more than inline rendering does. Collapsed-by-default is a soft form of de-emphasis.

**Note 2:** Render singletons inline in pile order, not in a separate collapsible section. A pile of one is still a pile; the model returned it in a position. Tag it inline as `Pile N (singleton): "label"` exactly as the wireframe shows for `Pile 3`. If visual grouping is desired for scanability, render singletons as a non-collapsible labeled subsection at the *end* of the pile list, expanded by default. Either is fine; collapsed-by-default is not.

### Q3. Empty-state copy — PASS-WITH-NOTES

The three lines are close to right. Two small adjustments:

- **"This informant returned no pile-sort data."** — PASS. Reads cleanly.
- **"No decline events recorded for this informant."** — PASS. Reads cleanly.
- **"0 items elicited. Pile-sort and decline sections may also be affected (upstream empty-input propagation)."** — see Q5 below. The first sentence is fine; the second sentence overclaims. See Note 4.

**Note 3:** The phrase "0 items elicited" is correct CDA framing (elicitation is what the protocol does; zero is a real elicitation outcome, not an error). Keep it.

### Q4. Decline rendering (verbatim refusal text + read-only classifications) — PASS-WITH-NOTES

The verbatim-text approach is correct. Read-only display of `manual_classification` and `safety_attribution_subtype` is correct (the dashboard reads, never infers).

The guardrail concern is real for `safety_event_attribution` declines specifically. When a model says something like "I can't help with that because it could cause harm," the model is making a *claim about the world* (this content is harmful) that the dashboard should not echo as fact.

**Note 4:** Above any verbatim refusal text, render a static disclaimer line: *"The text below is the model's verbatim response. Any claims it makes about the prompt, the task, or external reality are the model's own attributions, not statements of fact."* This is one line, applied once at the top of Section 3 (not per-decline). It is methodologically equivalent to the verbatim-pile-label disclaimer in Note 1 and prevents the dashboard from being read as endorsing the model's framing.

For the read-only classification fields: render them with a clear "classified by [reviewer name or 'manual review']" provenance label so the Coder doesn't accidentally make them look like dashboard-computed values. If the persisted artifact carries a classifier identity field, surface it; if not, render as "Manual classification (read-only): {value}".

### Q5. Empty-freelist propagation banner — FAIL (rewrite required)

The proposed wording — "Pile-sort and decline sections may also be affected (upstream empty-input propagation)" — is one step too interpretive for a pure-verbatim view. "Upstream empty-input propagation" is a *mechanism claim* about the collection pipeline that:
1. Is true for the three known cases (35e4e2ab/86585ec5/a81f309d) per the project memory note,
2. Is **not yet generally established** as the cause of every empty freelist Mark might encounter in OPS-T4,
3. Reads to a future maintainer like a derived classification, which is exactly what OPS-T4 is supposed to avoid.

The banner is also asymmetrically placed: it appears on the freelist when the relevant downstream artifacts (pile-sort, declines) are what's actually affected.

**Note 5 (required rewrite, blocking on this question only):** Replace with strictly factual, non-causal copy:

> "0 items elicited. The pile-sort prompt for this informant was constructed with 0 items of input — see Section 2."

That states the observable fact (the prompt downstream was empty) without claiming a propagation pathway. If Mark wants the propagation framing, that belongs in OPS-T5+ as a derived view (with SME re-review), not in OPS-T4 verbatim rendering.

If the persisted record carries a `thinking_verbatim` for the freelist step (per the empty-freelist memory note: "model produced a long internal `thinking_verbatim` enumerating ~50 kinship terms, then emitted `response_verbatim=""`"), surfacing that as a separate verbatim subsection ("Model's internal reasoning (thinking trace, verbatim): ...") is in-scope for OPS-T4 and would let Mark see the upstream signal directly without the dashboard interpreting it. Optional, not required.

### Q6. Anything to reject — see Q5 only

Nothing structural. The wireframe is sound. The Q5 rewrite is the only blocking item.

---

## What the Coder can build right now

- Section 1 freelist: as specified, no changes.
- Section 2 piles: as specified, plus the one verbatim-provenance header (Note 1) and inline singletons (Note 2).
- Section 3 declines: as specified, plus the one model-attribution disclaimer (Note 4) and a clear classification-provenance label.
- Empty-state copy lines 1 and 2: as specified.
- Empty-freelist line: rewrite per Note 5 before shipping.

No re-review required after the Coder applies these notes. Reviewer agent can confirm at PR time.

---

*End of verdict.*
