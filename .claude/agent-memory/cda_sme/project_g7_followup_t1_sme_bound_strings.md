---
name: g7-followup-t1-sme-bound-strings
description: G7-FOLLOWUP-T1 byte-identical SME-bound strings (2026-06-11) for the chart-to-record provenance pivot affordance on MDSPlot tooltip and Focus 1 individual-model view header. Pivot lands on the Collection records tab and scrolls to the matching per-model summary row for the current domain. Coder pastes verbatim, no paraphrasing.
metadata:
  type: project
---

# G7-FOLLOWUP-T1 SME-bound strings (byte-identical, 2026-06-11)

Delivered under the persisted-artifact pattern referenced in the Architect plan (CR-T7 / T-MDS-R1 precedent). Pasted verbatim into `apps/dashboard/src/copy/failures_findings.ts` adjacent to FAILURES_TAB_LABEL / SECTION_HEADING. The Coder MAY NOT paraphrase.

Naming convention: `PIVOT_TO_RECORDS_*` (new constant family, distinct from BLOCK_* / BADGE_* / RECORDS_*).

## Methodology call (binding on string design)

The candidate label proposed by the Architect plan (§5: "View the collection records behind this model") was reviewed and **rejected as drafted**. Reasoning:

- "behind this model" is borderline. A skeptical reader can construe "behind" as causal/intentional ("the records that explain this model"). Per §1.5.4 rows 7-10 and pitfall #16 register-boundary stem, the affordance copy must name the records as a property of the **LSB pipeline run on this domain**, not as a property of the model.
- The records are the per-model summary rows on the Collection records tab keyed to (model_id, domain). The honest naming is what the records ARE: the LSB collection records the pipeline produced when running this domain's free-list / pile-sort / pile-interview steps with this model as informant.
- Both surfaces (MDSPlot tooltip + Focus 1 header) point at the same destination, so a single label string is reused on both. The aria-label expands for SR clarity.

## 1. PIVOT_TO_RECORDS_LABEL (the affordance button text)

Used on both the MDSPlot tooltip pivot control and the Focus 1 individual-model view header pivot control. Plain `<button>` semantics (no URL change beyond the existing tab path push). Verbatim:

```
See the collection records for this model
```

Notes for the Coder and Reviewer:
- This string is byte-identical wherever it appears. Both `MDSPlot.tsx` and the Focus 1 header host render the same `PIVOT_TO_RECORDS_LABEL` import.
- No "behind", no "explaining", no "underlying", no "responses", no "answers". "Collection records" is the parser-state name shipped on the destination tab (FAILURES_TAB_LABEL).
- "for this model" is the model-as-informant register: the records are LSB pipeline output produced WITH this model as the informant on the currently selected domain. Not records that THE MODEL produced; records LSB produced while running the protocol with this model.

## 2. PIVOT_TO_RECORDS_ARIA_LABEL_TEMPLATE (aria-label string)

A function-returning-string OR a template literal taking `(modelLabel, domainLabel)` at call site. SR users need both the model and the domain context because both surfaces (chart and Focus 1 header) are domain-scoped views. Verbatim template:

```
See the collection records for ${modelLabel} on the ${domainLabel} domain
```

Notes:
- `${modelLabel}` is the human-readable display label (e.g., "Claude Opus 4.6"), not the raw `model_id` slug.
- `${domainLabel}` is the lowercase domain noun ("family", "holidays", "food"), inserted directly into the sentence.
- No paraphrase of "for ... on the ... domain". The grammatical frame is parser-state: the records belong to LSB's run of that domain with that model. Coder must wire the template, not paraphrase the connective words.

## 3. PIVOT_TO_RECORDS_ARRIVAL_CAPTION (optional inline arrival caption)

The plan §5 asks whether SME issues an arrival caption. **SME issues one.** The arrival event is high-leverage for orientation: a researcher who clicks the pivot and lands on a long, dense per-model summary table needs an unambiguous confirmation that "this is what you asked to see and it is scoped to this domain". Without a caption, a researcher who mis-clicks may not realize the domain was pivoted automatically.

The caption renders as an inline notice above the highlighted per-model summary row for the configured duration (UI/UX-set; SME does not rule on timing). Function or template taking `(modelLabel, domainLabel)`. Verbatim template:

```
Showing the collection records LSB produced when running the ${domainLabel} protocol with ${modelLabel} as the informant.
```

Notes:
- The sentence places LSB as the producing agent and the model as the informant. This is the §1.5 / §1.5.1 corpus-lens framing in one sentence at the moment the researcher arrives.
- "the ... protocol" stays singular (one of: "the family protocol", "the holidays protocol", "the food protocol"). Coder must not pluralize.
- "as the informant" is binding. Do not substitute "as the subject" or "as the model" or drop the role-name entirely.
- This caption is distinct from the IMPACT_PARAGRAPH_FAILURES / IMPACT_PARAGRAPH_FOLLOWUPS / TAXONOMY_BLOCK strings. Those remain byte-identical and unaltered by this task.

## 4. PIVOT_TO_RECORDS_NO_MATCH_NOTICE (no-match fallback)

The plan AC2 allows the no-match branch (model has no successful records in this domain) to render an inline notice. SME issues one to prevent silent failure (a researcher clicking the pivot and seeing nothing happen would mis-attribute the silence). The notice renders in place of the highlighted row treatment for the configured duration. Function or template taking `(modelLabel, domainLabel)`. Verbatim template:

```
The Collection records tab has no successful-run summary for ${modelLabel} on the ${domainLabel} domain. The per-model summary table only lists models that produced a parseable session in this domain.
```

Notes:
- Names the destination ("Collection records tab"), the entity ("successful-run summary"), and the scoping rule ("only lists models that produced a parseable session in this domain"). A researcher who lands here understands why they don't see a row without having to read the methodology page.
- Does not say "failed" or "missing" of the model. Says the table does not list it, with the inclusion criterion stated.
- This string is the no-match fallback ONLY. If a row IS found, this string never renders.

## 5. Anti-attribution advisory (Architect / UI/UX / Coder must respect at placement)

The affordance must NOT be visually coupled to a Smith's S / Sutrop CSI / OCI / centrality numeric in a way that implies the per-model summary records explain that numeric. Specifically:

- On MDSPlot tooltip: the pivot control renders BELOW the "Top terms" line, separated by an existing visual separator (`.chart-tooltip__sep` or equivalent). It does not appear adjacent to the Centrality numeric or the OCI explainer line. UI/UX is the gate on placement; this advisory is delivered for the gate to honor.
- On Focus 1 header: the affordance renders in the header chrome, not embedded in a per-metric card. Same anti-coupling rule.
- The button copy and aria-label MUST NOT be parameterized on any metric value. There is no "high-concentration" or "low-concentration" or "stable" variant; the copy is invariant on R1 state, OCI value, centrality, or any other numeric.

## 6. Forbidden-vocabulary chrome scan (extension of CR-T7 N5)

Reviewer's case 9 chrome-isolation walk on `FailuresFindings` already covers the destination tab. This task extends the scan to the new affordance DOM on BOTH originating surfaces (MDSPlot tooltip control + Focus 1 header control) and asserts zero matches for the six terms named in CR-T7 N5: `worldview`, `believes`, `thinks`, `understands`, `cooperative` (outside the counterfactual context, which does not appear in any of the four PIVOT_TO_RECORDS_* strings), bare `refusal`. The PIVOT_TO_RECORDS_* strings shipped here are clean; the assertion is defensive against unexpected adjacent chrome.

## 7. Hard-rules compliance recap

- No em dashes anywhere in any delivered string (U+2014 absent in all four strings above; Coder's mandatory grep over the diff will confirm).
- No CLAUDE.md §7 / ARCHITECTURE.md §1.5.4 forbidden-vocabulary terms applied to models in any delivered string.
- No bare "refusal"; not used.
- Parser-state register throughout (records as LSB-pipeline output for the domain, model as informant, no causation / intent / explanation language).
- Strings are plain text, no markdown inside the strings themselves; ready to paste into TypeScript constants.
- "informant" appears in the arrival caption verbatim. This term is canonical CDA vocabulary and matches §1.5 framing; it is NOT on any forbidden list and is preferred here over "subject" or "respondent" because it is the technical role-name the methodology page uses.

## 8. Constant placement and Coder paste targets

All four constants land in `apps/dashboard/src/copy/failures_findings.ts` adjacent to FAILURES_TAB_LABEL and SECTION_HEADING. Suggested grouping comment:

```
// ===== Chart-to-record provenance pivot (G7-FOLLOWUP-T1, 2026-06-11) =====
```

The constants are imported by both MDSPlot.tsx and the Focus 1 individual-model view header host (component name TBD by UI/UX per plan §6). The Coder must not duplicate the strings inline in either component.
