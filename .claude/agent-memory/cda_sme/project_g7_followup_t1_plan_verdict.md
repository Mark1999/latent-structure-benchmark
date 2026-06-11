---
name: g7-followup-t1-plan-verdict
description: G7-FOLLOWUP-T1 chart-to-record provenance pivot plan verdict (2026-06-11); PASS-WITH-NOTES. Single-task plan adding an affordance to MDSPlot tooltip + Focus 1 individual-model view header that pivots to the Collection records tab and scrolls to the matching per-model summary row for the current domain. Architect candidate label "View the collection records behind this model" REJECTED as drafted (borderline causal "behind"); SME delivered byte-identical replacements in project_g7_followup_t1_sme_bound_strings memo (PIVOT_TO_RECORDS_LABEL / _ARIA_LABEL_TEMPLATE / _ARRIVAL_CAPTION / _NO_MATCH_NOTICE). 4 binding notes (G1 anti-coupling advisory, G2 arrival caption SME-issues-one, G3 no-match fallback SME-issues-one, G4 chrome scan extension to BOTH originating surfaces).
metadata:
  type: project
---

# G7-FOLLOWUP-T1 chart-to-record provenance pivot plan verdict (2026-06-11): PASS-WITH-NOTES

CDA SME VERDICT: PASS-WITH-NOTES

Axis 1 - Protocol validity:      N/A (no CDA elicitation protocol change; pivot is a UI affordance over the published per-record / per-model summary surface CR-T7 shipped)
Axis 2 - Analytical validity:    N/A (no analytical method change; no new statistic computed or claimed by the affordance)
Axis 3 - Claims validity:        PASS (with bound strings; Architect's candidate label rejected, SME-delivered strings frame records as LSB-pipeline output for the domain, model as informant, no causal / intent / explanation language)
Axis 4 - Audience translation:   PASS (with arrival caption + no-match notice issued by SME; researcher landing on the destination tab gets a one-sentence orientation that names what the records are and what scoping rule applied)

Register compliance:             N/A (R1 / R2 / R3 not engaged at the pivot affordance; the affordance is provenance-routing, not a measure surface)
Vocabulary compliance:           PASS (four delivered strings clean over §1.5.4 forbidden list; chrome-scan extension G4 binding to defend against accidental neighbor coupling)

## Verdict summary

The plan correctly scopes G7-FOLLOWUP to closing the chart-side half of the G7 gap (CR-T7 closed the data plumbing half on 2026-06-10). The two-surface scope pin (MDSPlot tooltip + Focus 1 header) is methodologically appropriate; the deferred surfaces (Term Map, Heatmap, Centrality, Cluster Tree, Free Lists, Pile Structure) are correctly out-of-scope for this cycle. The in-app NavTab pivot with no URL serialization is correct; the explicit STOP condition on URL-anchoring being "genuinely required" defuses the highest-risk scope-creep path.

The SME identified one drafting-level concern on the Architect's candidate label ("View the collection records behind this model") and resolved it by delivering verbatim replacements in the bound-strings memo. The four bound strings (label, aria-label template, arrival caption, no-match notice) are byte-identical and live in `project_g7_followup_t1_sme_bound_strings.md`. The Coder pastes verbatim, no paraphrasing.

## Load-bearing methodology call

The Architect plan §2 names the label-copy gating responsibility correctly ("the SME has DELIVERED gating responsibility on the byte-identical strings per CR-T7 A3"). The plan's candidate label "View the collection records behind this model" was reviewed under §1.5.4 rows 7-10 (register-boundary stems) and pitfall #16 (post-generation cognition-attribution guards). The word "behind" admits a causal/explanatory reading ("the records that explain this model's output") which is precisely the cognition-attribution slip the CR-T7 SME advisory A3 named as the highest-leverage place to slip. The SME-delivered label "See the collection records for this model" replaces "behind" with "for" (parser-state, ownership-of-informant-role) and "View" with "See" (lighter verb, no implication of causation). Reasoning is recorded verbatim in the bound-strings memo §1.

## Binding notes (four)

### G1 (BINDING, ADVISORY ON UI/UX PLACEMENT)

Bound-strings memo §5 carries the anti-coupling advisory to the UI/UX gate. The pivot affordance must NOT be visually coupled to a Smith's S / Sutrop CSI / OCI / centrality numeric in a way that implies the per-model summary records explain that numeric. On MDSPlot tooltip: the pivot control renders BELOW the "Top terms" line, separated by an existing visual separator (`.chart-tooltip__sep` or equivalent), not adjacent to the Centrality numeric or the OCI explainer line. On Focus 1 header: the affordance renders in the header chrome, not embedded in a per-metric card. The button copy and aria-label MUST NOT be parameterized on any metric value (no "high-concentration" / "low-concentration" variants). UI/UX is the placement gate; SME records this advisory so the gate honors it.

### G2 (BINDING, SME ISSUES THE ARRIVAL CAPTION)

The plan §5 asked SME to rule on whether an arrival caption renders. SME issues one. The arrival event is high-leverage for orientation: a researcher pivoting onto a long per-model summary table needs an unambiguous confirmation that "this is what you asked to see and the domain pivot happened". Without a caption, a mis-click is indistinguishable from a no-op. The byte-identical caption template (`PIVOT_TO_RECORDS_ARRIVAL_CAPTION`) lives in the bound-strings memo §3 and reads:

```
Showing the collection records LSB produced when running the ${domainLabel} protocol with ${modelLabel} as the informant.
```

This places LSB as the producing agent and the model as the informant in one sentence at the moment of arrival — the §1.5 / §1.5.1 corpus-lens framing condensed into the orientation point. The Coder wires the template; UI/UX rules duration and visual treatment.

### G3 (BINDING, SME ISSUES THE NO-MATCH FALLBACK)

The plan AC2 allows the no-match branch to render an inline notice. SME issues one to prevent silent failure (a researcher clicking the pivot and seeing nothing happen would mis-attribute the silence). The byte-identical notice template (`PIVOT_TO_RECORDS_NO_MATCH_NOTICE`) lives in the bound-strings memo §4 and reads:

```
The Collection records tab has no successful-run summary for ${modelLabel} on the ${domainLabel} domain. The per-model summary table only lists models that produced a parseable session in this domain.
```

This names the destination, the entity, and the scoping rule in one sentence. A researcher landing on the empty branch understands why they don't see a row without having to read the methodology page. The notice MUST NOT say the model "failed" or that the records "are missing"; it says the table does not list it, with the inclusion criterion stated.

### G4 (BINDING, CHROME SCAN EXTENSION)

Plan AC7's case 9 chrome-isolation walk currently scopes to the destination tab (`FailuresFindings` DOM). G4 extends the scan to the new affordance DOM on BOTH originating surfaces (MDSPlot tooltip control + Focus 1 header control) and asserts zero matches for the six terms named in CR-T7 N5: `worldview`, `believes`, `thinks`, `understands`, `cooperative` (outside counterfactual), bare `refusal`. The four PIVOT_TO_RECORDS_* strings shipped here are clean; the scan is defensive against unexpected adjacent chrome on the originating components. Tester wires this assertion alongside the existing case 9 walk; Reviewer confirms the grep coverage.

## Advisory notes (non-blocking)

- **A1 (advisory):** The plan §2 names "the SME must deliver the byte-identical strings inside the verdict notes array verbatim" as the BINDING delivery posture. The SME delivers via a persisted artifact (`project_g7_followup_t1_sme_bound_strings.md`) referenced from this verdict file. This follows the persistence pattern CR-T7 established when the bound strings exceeded note-length (project_cr_t7_sme_bound_strings.md). The Architect / Orchestrator must read the memo before dispatching the Coder.

- **A2 (advisory):** Plan §6 enumerates the UI/UX gate scope correctly (placement, control type, arrival-highlight tokens, mobile a11y, WCAG AA, keyboard / SR interaction). The SME has no methodology opinion on those decisions; they are UI/UX's call. The single methodology constraint on placement is G1 above (anti-coupling to metric values).

- **A3 (advisory):** Plan §5 inline candidate-label comment "or a parser-state alternative naming what the records are (a property of the LSB pipeline's parser-state output for this model on this domain), not what they explain" is methodologically correct framing. The SME-delivered label honors that direction.

- **A4 (advisory):** The plan correctly avoids touching `IMPACT_PARAGRAPH_FAILURES`, `IMPACT_PARAGRAPH_FOLLOWUPS`, `TAXONOMY_BLOCK`, `RECORDS_*`, `_FRAMING_NOTE`, and `_FRAMING_NOTE_DETAIL`. Those are CR-T1 / CR-T2 / CR-T3 / CR-T4 / CR-T7 byte-identical contracts and must remain byte-untouched. The Reviewer's existing byte-identity assertions enforce this.

- **A5 (advisory):** The preexisting MDSPlot tooltip strings (`"within-model output concentration is low"` at line 284) use a §1.5.4 forbidden phrase. This predates G7-FOLLOWUP and is OUT-OF-SCOPE for this task. Documenting here so the Coder does not "fix it while in the file" (CLAUDE.md §8 no-scope-creep rule). A separate verdict cycle is needed to rewrite that string; that cycle is not blocked by G7-FOLLOWUP-T1 and does not block it.

## Posture on Coder dispatch

PASS-WITH-NOTES. The Architect dispatches the UI/UX gate next per the plan's §7 gate order. UI/UX receives:
- This verdict file as the SME PASS
- The bound-strings memo (`project_g7_followup_t1_sme_bound_strings.md`) as the byte-identical paste source
- The G1 anti-coupling advisory as a placement constraint

UI/UX then dispatches the Coder with placement decisions + DESIGN_SYSTEM.md amendment. The Coder pastes the four PIVOT_TO_RECORDS_* constants from the bound-strings memo verbatim into `apps/dashboard/src/copy/failures_findings.ts`, wires them through MDSPlot.tsx and the Focus 1 host, implements the no-match branch using `PIVOT_TO_RECORDS_NO_MATCH_NOTICE`, and implements the arrival caption using `PIVOT_TO_RECORDS_ARRIVAL_CAPTION`. Reviewer asserts byte-identity over all four strings + G4 chrome scan + the existing R10 / T-MDS-R1 / T3 heatmap byte-identity assertions named in plan AC8 / AC9.

If implementation surfaces a copy decision the bound-strings memo does not cover (e.g., the Focus 1 host component splits into multiple files and needs disambiguating context in a sibling string), the Coder STOPS and routes back; SME drafts in the same persisted-artifact posture used here, no new full plan verdict required absent scope expansion.
