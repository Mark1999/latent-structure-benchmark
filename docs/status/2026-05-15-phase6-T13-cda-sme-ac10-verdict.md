---
filed: 2026-05-15
reviewer: CDA SME agent (Opus)
task: Phase 6 T13 — AC10 verbatim review of rendered food-domain lede
plan_reviewed: docs/status/2026-05-15-phase6-T13-architect-plan.md
prior_sme_verdict: docs/status/2026-05-15-phase6-T13-cda-sme-verdict.md
artifact_reviewed: apps/dashboard/public/data/food.json (generated_lede + supporting fields)
slack_channel: "#lsb-cda-sme"
verdict: PASS-WITH-NOTES
---

# CDA SME AC10 verdict — Phase 6 T13 (food-domain rendered lede)

## AC10 VERDICT: PASS-WITH-NOTES

The verbatim lede text is §1.5-compliant, descriptive-locational, and
selects the correct `strong_consensus_with_low_oci` pattern key for
the underlying data shape (n=8, one low-OCI model). The n=8
publication posture with `romney_small_n_warning: true` is shippable
under the existing CI-width-carries-uncertainty surface treatment
(consistent with family/holidays at small-n). The silent grok-4.20
exclusion is **acceptable as the pipeline's normal qa_check filter
behavior** under the failures-surface scope definition; this is
posture (a) from the Architect's three options. **One required text
fix** (M1, below) — the lede's "signalling" should be US-English
"signaling" to match dashboard prose convention. **No methodological
re-collection required.** **No `food.yaml` re-edit required.** Two
methodology-page carry-forwards (T14) named below.

The Coder applies M1 to `lede_v1.py` pattern string OR to the
rendered `food.json` `generated_lede` field directly (Coder's choice
of mechanism; the binding constraint is byte-identity of the final
shipped text), reruns `cdb_publish/build.py` if editing the template,
and commits.

## Four-axis scorecard (AC10 scope)

| Axis | Verdict | Rationale |
|---|---|---|
| 1. Protocol validity | PASS | CDA elicitation protocol unchanged from prior PASS; food.yaml was written verbatim per binding B-D2. |
| 2. Analytical validity | PASS-WITH-NOTES | n=8 < 15 threshold trips `romney_small_n_warning: true`; uncertainty is correctly surfaced via Smith's S 95% CI in the lede; consensus_type STRONG_CONSENSUS at consensus_score 0.61 with CI [0.48, 0.79] is methodologically defensible (M4 reading). |
| 3. Claims validity | PASS-WITH-NOTES | Descriptive-locational frame respected; "8 frontier models" count truthfully describes the analysis output; M2 ruling: silent grok exclusion does not require lede acknowledgement under failures-surface scope. |
| 4. Audience translation | PASS-WITH-NOTES | Cold-reader legibility passes for the consensus claim and CI; M1 required (US-English "signaling"); T14 carry-forwards strengthen the cold reader's interpretation of the n=8 posture. |

## The verbatim lede being reviewed

Reproduced byte-exact from `apps/dashboard/public/data/food.json`
line 27679 `generated_lede`:

> Across 8 frontier models, food vocabulary is organized around a shared categorical structure (Smith's S = 0.61, 95% CI [0.48, 0.79]). 1 of these 8 models produced low output concentration on this domain -- their position on the map is shown without a confidence ellipse, signalling that the runs did not converge on a single sort.

Pattern key selected by `lede_v1.py`:
**`strong_consensus_with_low_oci`** (confirmed against
`consensus_type: STRONG_CONSENSUS` + display.r1_states showing one
`low_concentration` entry for `mistralai/mistral-small-2603`).

Numeric substitutions:
- `{n}` = 8 (matches `display.r1_states` cardinality and
  `cultural_centrality_scores` cardinality)
- `{s}` = 0.61 (matches `consensus_score: 0.6100410869920746`,
  rounded to 2 decimal places)
- `{lo}` = 0.48 (matches `consensus_ci[0]: 0.4776...`, rounded up
  to 2 decimal places)
- `{hi}` = 0.79 (matches `consensus_ci[1]: 0.7872...`, rounded to
  2 decimal places)
- `{n_low_oci}` = 1 (matches the count of `low_concentration`
  entries in `display.r1_states`)

All substitutions are consistent with the underlying numeric output.
The two pre-clearance AC10 checks (correct pattern key, sane
substitutions) PASS.

## Four-question binding answers

### Q1 — Lede text §1.5 compliance

**PASS.** No forbidden vocabulary present. Marker-by-marker scan:

| Forbidden term | Present? | Notes |
|---|---|---|
| "believes" / "thinks" / "worldview" | No | — |
| "understands" / "perceives" | No | — |
| "cultural bias" (standalone) | No | "categorical structure" is the correct corpus-lens framing. |
| Anthropomorphic verbs applied to models | No | "food vocabulary is organized around..." is descriptive-locational, attributing organization to the vocabulary's position in the corpus, not to model cognition. |
| "model X sees/thinks/believes food is..." | No | Frame is consistently locational. |
| Within-model consensus language | No | The "shared categorical structure" frame is between-model (Register 2), consistent with the n=8 Romney CCM operational context. |

The phrase **"did not converge on a single sort"** in the trailing
clause is the correct R1-state framing for `low_concentration` — it
describes the run distribution, not a model state. PASS.

The descriptive-locational frame is respected throughout: "food
vocabulary is organized around..." and "their position on the map
is shown..." both locate the finding in the corpus-lens / MDS
coordinate space, not in model cognition. PASS.

### Q2 — The "8 frontier models" count

**KEEP AS "8".** Required posture: the lede truthfully describes the
**analysis output** (n=8 models in the food.json result), not the
**collection attempt** (9 models attempted, 1 filtered by qa_check).

Reasoning:

1. **Consistency with shipped domains.** `family.json` says "Across
   11 frontier models" — its collection attempt count may have been
   higher (some models likely qa-failed in the family campaign too).
   `holidays.json` says "Across 9 frontier models" — same pattern.
   The cross-domain convention is **post-filter cardinality**, not
   collection-attempt cardinality. Changing food's lede to
   "9 attempted / 8 analyzed" would create asymmetric framing across
   the three v1 domains, which is methodologically incoherent and
   confuses the cold reader more than it informs.

2. **The lede is a Register 2 claim about the analyzable corpus.**
   The analyzable corpus is the 8 models that produced valid
   free-list + pile-sort output. Including grok-4.20 in the "frontier
   models" count when grok-4.20 contributed zero valid records to
   the Smith's S computation would be a false claim about the
   denominator.

3. **The failures-surface is the correct disclosure channel.** The
   pipeline's contract is: post-filter n in the lede; failure records
   (where they exist) surface on the failures dashboard. The
   currently-zero `failures/food.json` is a separate disclosure gap
   addressed under Q3 / T14.

**Verdict:** "Across 8 frontier models" remains binding. **No edit
to the count.**

### Q3 — Silent grok-4.20 exclusion: methodologically OK?

**POSTURE (a) WITH T14 FOLLOW-UP.** Acceptable to ship `food.json`
with n=8 and zero acknowledgement of grok at the *lede* surface —
**provided** a methodology-page disclosure (T14) names the
qa-failed exclusion category and the existence-of-attempted-but-
filtered-out informants as a normal pipeline state.

Rationale:

1. **The failures-surface is currently scoped to "verbatim
   preserved outputs from sessions that did not produce a parseable
   primary-step response."** This is the `framing_note` in
   `failures/food.json` line 7. By this scope definition, the grok
   records — which parsed to `qa_passed: False` (not to "no
   parseable response at all") — fall **inside** the failures-
   surface scope as currently worded. The disclosure gap is
   therefore one of two things:

   (i) The grok records *should* be duplicated into
       `data/raw/failures.jsonl` and surfaced in `failures/food.json`
       — which would require a `cdb_publish/failures.py` code change
       to include qa_passed=False records as a distinct category.

   (ii) The failures-surface framing should be tightened to say
       "verbatim preserved outputs from sessions that did not pass
       qa_check" — making the scope explicit about the qa-filter
       boundary, and surfacing the grok records on the failures
       dashboard.

   Both (i) and (ii) are out of T13 scope and require Architect
   spawn. **Neither is blocking for AC10 PASS.**

2. **For T13 shipping today**, posture (a) is acceptable because:
   - The `data/raw/informants.jsonl` file retains the 5 grok
     records with `qa_passed: False` (append-only invariant
     preserved per pitfall #10).
   - Researchers reproducing the open data bundle can see the
     grok records in the raw jsonl and recompute n=8 vs. n=9
     themselves.
   - The methodology-page T14 footnote (carry-forward F1 below)
     names the qa-failed exclusion category at the documentation
     surface, where the cold reader can find it.

3. **The lede should NOT inline an exclusion disclosure.** Adding
   "(1 additional model attempted but failed validation)" to the
   food lede creates asymmetric framing relative to family and
   holidays, both of which also went through the same qa_check
   filter without lede-level exclusion disclosures. The right
   surface is the methodology page, not the per-domain lede.

**T14 carry-forward F1 (binding for methodology page):** the
methodology page must carry a single sentence describing the
qa_check filter and naming "qa_passed=False" as a normal
exclusion category, distinct from safety_filter / decline /
refusal categories. Suggested language for the Architect to
finalize at T14 plan:

> "Some informant records in `data/raw/informants.jsonl` carry
> `qa_passed: False`, indicating the response was received from
> the provider but failed downstream validation (e.g.,
> free-list parse failure, pile-sort parse failure). These
> records are preserved verbatim in the raw data but excluded
> from cross-model analysis. This is distinct from the
> failures-surface category, which captures sessions that did
> not produce a parseable primary-step response."

**T14 carry-forward F2 (advisory to Architect):** Phase 6.5
should resolve whether qa_passed=False records should be
co-duplicated into the failures-surface (option i above) or
whether the failures-surface scope should be tightened (option
ii above). This is a forward-looking framing decision, not a
T13 blocker. The Architect's call.

### Q4 — n=8 + romney_small_n_warning publication posture

**PASS.** STRONG_CONSENSUS at consensus_score 0.61 with 95% CI
[0.48, 0.79] is publication-worthy at n=8 with the small-n flag set.

Methodological reading:

1. **Smith's S null reference.** Smith's S is bounded [0, 1]; the
   "no concentration / pure uniformity" null is 0.0, not 0.5. (The
   "0.5 marker" referenced in the parent's Q4 is the
   `SIMILARITY_NULL_VALUE` for the rescaled Mantel-correlation
   heatmap, a different statistic.) The CI lower bound of 0.48 is
   well above the no-concentration null (0.0); the consensus claim
   does not include null values within its uncertainty bounds.

2. **Romney CCM (Register 2) at n=8.** The Romney eigenratio of
   6.59 is above both thresholds (classic 3.0, LSB 5.0), passing
   `romney_consensus_pass: true`. The `romney_small_n_warning: true`
   flag correctly fires per the n<15 reconciled threshold
   ([[project_romney_small_n_threshold]]). This is a methodological
   caveat, not a publication disqualifier — the same flag fires for
   family (n=11) and holidays (n=9), both of which ship.

3. **The CI width IS the small-n surface.** The CI [0.48, 0.79]
   has width 0.31, wider than would be expected at n=20+ for the
   same point estimate. This width is the small-n indicator the
   cold reader sees at the lede surface — it correctly signals
   uncertainty without over-claiming. The lede does not say
   "Smith's S = 0.61" alone; it says "Smith's S = 0.61, 95% CI
   [0.48, 0.79]". This is the correct shape for an n=8
   uncertainty-carrying publication.

4. **Cross-domain consistency.** All three v1 domains operate at
   n<15 models and trip the small-n warning. The methodology page
   T14 carry-forward F3 should name this as the v1 corpus-wide
   small-n posture so cold readers can interpret the CI widths
   correctly across all three domains.

**T14 carry-forward F3 (binding for methodology page):** the
methodology page must note that all three v1 domains operate at
n<15 informants (models) and that this trips
`romney_small_n_warning: true` for each, surfaced via Smith's S CI
width rather than a categorical "small-n" label. Already named in
the prior T13 SME verdict as a downstream carry-forward; restated
here as binding for T14.

**Verdict:** ship at n=8. No re-collection of grok required.

## Open-inquiry findings (Q5)

Reviewing the surrounding `food.json` and `failures/food.json`
output as the dashboard reader will see it:

**O1 — `cross_model_mantel` and `cross_model_nolan` arrays are
empty (lines 6700–6701).** This means the cross-model similarity
matrices are not populated for food. Confirmed by user/Architect
context: this is expected at first ship — the heatmap surface
component is not blocking T13. **No action.** Advisory to T14:
the food domain methodology summary should not promise heatmap
content that does not exist.

**O2 — `groundings: []` and `selected_baseline_id: null` (lines
27677–27678).** Correct for v1 per the 2026-05-07 no-human-baseline
amendment ([[project_no_human_baseline_amendment]]). The model-to-
model framing of the lede is consistent with the empty groundings
list. **No action.**

**O3 — `g1_*` fields are all null (lines 27671–27676).** Confirmed
expected: G1 prompt-robustness diagnostics are not computed for
food. This is a `cdb_analyze` capability gap, not a T13 defect.
**Advisory to Architect:** future phases should consider whether
G1 diagnostics should be computed for all v1 domains; the empty
fields are visible in the open data bundle and may invite reader
questions. Not blocking AC10.

**O4 — `negative_centrality_flag: false` (line 6698).** Correct
for STRONG_CONSENSUS with the selected `strong_consensus_with_low_oci`
pattern; the subcultural pattern (which uses negative centrality)
was correctly not selected. Pattern key selection is consistent
with the underlying data. **No action.**

**O5 — Mistral is the low-OCI model.** From `display.r1_states`
line 27687: `"mistralai/mistral-small-2603": "low_concentration"`.
The lede correctly says "1 of these 8 models" without naming the
model — appropriate for the lede surface; the DataExplorer
component is the correct surface for per-model state. **No action.**

**O6 — `consensus_score: 0.6100410869920746` precision.** The lede
correctly truncates to 2 decimal places ("0.61"). No false
precision at the lede surface. **No action.**

**O7 — DataExplorer / DriftTracker behavior is out of AC10 scope.**
I am not reviewing the rendered article shell beyond the lede text
and the surrounding food.json fields that the lede composes from.
The UI/UX gate is the appropriate gate for the rendered article
shell.

**O8 — "signalling" vs. "signaling" (US English).** The lede uses
the British spelling "signalling" (line 27679). The shipped
family.json and holidays.json ledes do not use this word, so no
cross-domain consistency check is possible. The dashboard's prose
convention is US English ([[project_phase5_plan_verdict]] Q4
tagline US-English ruling). This is the **one required text fix**
(M1 below). Minor but binding for cross-domain prose consistency.

## Binding M-notes for the Coder

### M1 (REQUIRED — before commit)

**Replace "signalling" with "signaling"** in the food lede. US
English convention applies. The Coder's mechanism choice:

(a) **Preferred:** Edit the `lede_v1.py` template at the
    `strong_consensus_with_low_oci` pattern string, replacing
    "signalling" with "signaling"; rerun `cdb_publish/build.py`
    to regenerate `food.json` (and any other domain that uses
    this pattern key). Confirm via `git diff` that only the
    "signalling" → "signaling" change propagates; any other
    diff is a regression.

(b) **Acceptable fallback:** Edit `food.json` line 27679
    `generated_lede` field directly, replacing "signalling"
    with "signaling". Note that this fallback leaves the
    template inconsistent and future regenerations will
    re-introduce the British spelling. **Prefer (a).**

After M1 applied, the final lede text is:

> Across 8 frontier models, food vocabulary is organized around a shared categorical structure (Smith's S = 0.61, 95% CI [0.48, 0.79]). 1 of these 8 models produced low output concentration on this domain -- their position on the map is shown without a confidence ellipse, signaling that the runs did not converge on a single sort.

This is the **binding final text**. The Coder commits with this
string in `food.json` `generated_lede`, byte-exact.

### M2 (CARRY-FORWARD — no Coder action at T13)

**Silent grok-4.20 exclusion stands at T13.** The Coder takes no
action on the grok records at T13 commit time. The 5 grok food
records remain in `data/raw/informants.jsonl` with `qa_passed:
False` and are not duplicated into `data/raw/failures.jsonl` at
this time. The disclosure gap is named in T14 carry-forwards F1
and F2; the Architect resolves at Phase 6.5 / T14.

### M3 (COMMIT MESSAGE — required language)

The commit message must reference both the prior T13 plan verdict
and this AC10 verdict by path. Suggested commit body addition:

```
Lede AC10 verdict: docs/status/2026-05-15-phase6-T13-cda-sme-ac10-verdict.md
T13 plan verdict: docs/status/2026-05-15-phase6-T13-cda-sme-verdict.md

The food domain ships at n=8 (post-qa-filter). 5 grok-4.20
informant records remain in informants.jsonl with qa_passed=False
per pitfall #10 (append-only). Methodology-page disclosure of
the qa-filter exclusion category is carry-forward F1 to T14.
```

**No `food.yaml` re-edit.** The yaml content is unchanged from
the prior PASS-WITH-NOTES.

## Follow-up tasks for T14 / Phase 6.5

These are not blocking AC10; Architect schedules at T14 plan time.

**F1 (BINDING for methodology page):** add a single sentence
naming `qa_passed: False` as a normal exclusion category distinct
from safety_filter / decline / refusal categories. Suggested
language given in Q3 above. Required before the methodology page
closes.

**F2 (ADVISORY to Architect):** Phase 6.5 should resolve whether
qa_passed=False records co-duplicate into the failures-surface
or whether the failures-surface scope is tightened. The Architect's
call; neither posture is methodologically wrong, but the current
gap is a disclosure inconsistency that should resolve before v1
ships externally.

**F3 (BINDING for methodology page):** name the v1 corpus-wide
small-n posture: all three v1 domains operate at n<15 models
and trip `romney_small_n_warning: true`, surfaced via CI width
on Smith's S. Already a downstream carry-forward from the prior
T13 verdict; restated here as binding for T14.

## Rationale

The lede passes §1.5 compliance, descriptive-locational framing,
and pattern-selection correctness. The "8 frontier models" count
is the methodologically correct denominator for the Register 2
consensus claim; changing it to acknowledge collection-attempt
cardinality would break cross-domain consistency with family and
holidays. The silent grok exclusion is acceptable under the
current failures-surface scope definition; the disclosure gap is
appropriately routed to the methodology page (T14 carry-forward
F1), where the cold reader who wants to understand the qa-filter
boundary can find it. The n=8 publication posture is supported by
the existing CI-width-as-uncertainty-surface treatment that
family (n=11) and holidays (n=9) also use; STRONG_CONSENSUS at
CI [0.48, 0.79] is well above the Smith's S no-concentration null
of 0.0 across the full CI range. The Romney small-n warning
correctly fires at n<15 per the reconciled threshold; this is a
methodological caveat already surfaced in `food.json`, not a
publication disqualifier.

One required text fix (M1: "signalling" → "signaling") brings the
food lede into US-English prose convention consistent with the
shipped dashboard. The Coder applies M1, commits with the M3
commit-body language referencing both T13 verdict files, and the
T13 task closes. T14 carry-forwards F1, F2, F3 are routed to the
Architect for Phase 6.5 / T14 scheduling.

---

*End of CDA SME AC10 verdict for Phase 6 T13 food domain. After
M1 applied, the Coder may commit immediately. The methodology-page
carry-forwards (F1, F2, F3) are routed to the Architect for the
next-phase plan; they do not block T13 commit.*
