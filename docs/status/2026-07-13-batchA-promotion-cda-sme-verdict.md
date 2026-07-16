# CDA SME verdict, batch A promotion copy pass (runbook Step 5)

**Date:** 2026-07-13
**Campaign:** new-model-refresh-2026h2-a-20260710 (batch A) staged rebaseline
2026-07-12/13; git 561b534; NumPy 2.4.4, SciPy 1.17.1, Python 3.12; B=500 seed 42.
**Verdict:** PASS-WITH-NOTES
**Precedents relied on (by reference, not re-litigated):**
`.claude/agent-memory/cda_sme/project_phase9b_food_guard_trip.md` (F3-R3 pattern),
`docs/status/2026-07-10-batchA-fable5-refusal-cda-sme-verdict.md` (Fable disposition),
`docs/status/2026-07-10-batchA-reasoning-qa-cda-sme-verdict.md` (N1-N19).

## Four-axis scorecard

| Axis | Result |
|---|---|
| Axis 1, protocol validity | PASS |
| Axis 2, analytical validity | PASS-WITH-NOTES |
| Axis 3, claims validity | PASS-WITH-NOTES |
| Axis 4, audience translation | PASS-WITH-NOTES |
| Register compliance | PASS |
| Vocabulary compliance | PASS |

## Verdict summary

Family v0.4 and holidays v0.4 ship as auto-classified STRONG_CONSENSUS with the
generator ledes as produced; only the DataPage term-map count needs a mechanical
number refresh. Food v0.3 does not ship as auto-classified. The v0.2 F3-R3
straddling-CI pattern applies more strongly at v0.3 (point 5.44 above 5.0 by a
hair, median replicate 4.64 below, 66 percent of replicates below the 5.0
threshold): ship food v0.3 with `consensus_type_override = WEAK_CONSENSUS`, with
successor bound strings F3-V3-A / F3-V3-B / F3-V3-C / F3-V3-E replacing the v0.2
F3-R3 strings on food surfaces. F3-R3-D (SMALL_N_TEXT) is dormant on the live
surfaces post-promotion (all three domains at or above n=15); keep the constant
verbatim to preserve the v0.2 citable record and open a follow-up for
parameterization. N4/N12 methodology footnote binds now on the MethodologyPage.
Fable-5 disposition bound string (2026-07-10 (d)) ships verbatim on the batch A
records/failures panels for family, holidays, and food, preceded by a single
framing sentence. Provenance paragraph on DataPage is replaced with a
2026-07-12-scoped successor.

Rule 15 boundary preserved: every number I use is a mechanically computed fact
from the promotion facts block. No estimator, resampling scheme, threshold, or
uncertainty method invented or requested. The v0.3 per-replicate CI is the same
per-replicate reporting computation already used at v0.2 (F3-R3, orchestrator
step 4c) applied to the exact published v0.3 similarity matrix and its
underlying replicate stream, verified by the eigh(mean(replicates)) = 5.443
invariant matching the published point to 12 decimals.

## Rulings

### Ruling A. Food v0.3 classification disposition

**PUBLISH with `consensus_type_override = WEAK_CONSENSUS`, same override
mechanism as v0.2 (F3-R3 (b) ruling (i)).**

Justification. The F3-R3 rule was: "when the bootstrap CI on the eigenratio
straddles 5.0, publish the conservative classification and disclose the
indeterminacy rather than claim a category the uncertainty does not support."
At v0.3 the per-replicate CI95 is [2.75, 10.25], median 4.64, with 329 of 500
replicates (66 percent) below 5.0 and 30 of 500 (6 percent) below 3.0. The
point estimate 5.44 sits above 5.0 by a hair; the median replicate sits below
5.0. This is a more indeterminate configuration than v0.2 was, not less: at
v0.2 the point was 9.48 and the median 6.95 (both above), only the lower tail
straddled. If v0.2 got the WEAK_CONSENSUS override, v0.3 must at minimum get
the same override. TURBULENT (below 3.0) is not indicated: 94 percent of
replicates are above 3.0.

The T-1 guard did not trip because the point estimate did not cross 5.0 and
the guard is by construction blind to the `consensus_type_override` field.
That is expected behavior of the guard and does not license auto-publication
here: the F3-R3 override sits above the guard by design.

### Ruling B. Bound strings for food v0.3 (successors to F3-R3-A/B/C/E)

All strings verified free of U+2014 em dashes, free of §1.5.4/§7 forbidden
vocabulary, and free of the extended Fable-related forbidden vocabulary.
Numeric rounding to two decimals matches F3-R3 convention. US English.

**F3-V3-A (binding, replaces F3-R3-A on food v0.3 surfaces). Domain lede:**

> The food domain sits at the boundary between shared categorical structure
> and weaker agreement. The point estimate is on the strong-consensus side of
> our threshold by a hair, but most bootstrap replicates land below it and
> the interval crosses. The honest read is that strong agreement is not
> established at this collection width.

Load-bearing nouns: "point estimate", "bootstrap replicates", "interval",
"collection width".

**F3-V3-B (binding, replaces F3-R3-B). Override reason, populates
`consensus_type_override_reason` in the food v0.3 result JSON:**

> Point estimate 5.44 sits just above the 5.0 strong/weak threshold; the
> 95 percent bootstrap interval on the eigenratio spans [2.75, 10.25], with
> the median replicate below 5.0. We publish the conservative classification
> and disclose the indeterminacy rather than claim a category the uncertainty
> does not support.

**F3-V3-C (binding, replaces F3-R3-C). CI disclosure line, shown adjacent to
the override badge on food surfaces:**

> Romney CCM eigenratio 5.44, 95 percent bootstrap interval [2.75, 10.25],
> B=500. The interval crosses the 5.0 strong/weak threshold and the median
> replicate sits below it.

**F3-V3-E (binding, replaces F3-R3-E). Methodology footnote for food v0.3,
lives on MethodologyPage under the existing food-methodology-footnotes
section; supersedes F3-R3-E for the live food display. The FOOD-FIX-A
mode-coherent-basis footnote above it is retained for v0.2 audit context but
its "12-model" language should be co-located with an "at v0.2" scoping phrase
to avoid confusion with v0.3's 19-model slate; the Coder makes this scoping
edit or the Architect delegates it, no fresh SME pass needed for a purely
scoping word insertion:**

> For the food domain at v0.3, the cross-model similarity basis is the
> 19-model approved slate. Two additional models present in the domain
> corpus are outside the v0.3 approved slate: meta-llama/llama-4-maverick,
> which was outside the v0.2 mode-coherent similarity basis and is not
> on the v0.3 curator-maintained slate, and claude-fable-5, which is
> excluded from the batch A slate across all three domains under a
> separate ruling on provider deployment-side output filtering. At v0.3
> the approved-slate filter is applied to the record set before the
> analysis pipeline runs, so records from off-slate models do not enter
> the similarity basis, the model-level analyses, or the pooled term
> map for this domain; the raw records remain in the corpus and are
> visible on the collection-records and failures surfaces. This is a
> scope change from v0.2, where only the similarity basis was
> mode-filtered. The Romney CCM eigenratio is 5.44 with a 95 percent
> bootstrap interval of [2.75, 10.25] over B=500 model-resamples. The
> point estimate sits just above the 5.0 strong-consensus threshold,
> the median bootstrap replicate sits below it, and 66 percent of
> replicates fall below the threshold. The classification is therefore
> published as weak-consensus with the indeterminacy disclosed rather
> than as strong-consensus with a hidden uncertainty caveat. A separate
> open question on how to canonicalize the published eigenratio against
> its bootstrap distribution remains tracked under FOOD-FIX-A2.

**Correction (applied 2026-07-13 after orchestrator mechanical verification
per the recompute-adjudication-claims rule).** The prior draft of F3-V3-E
contained the sentence "Both models still contribute to their own
within-model output-distribution analyses and to the pooled term map
where their records apply", which is false at v0.3. Verification against
the artifacts: `data/results/food/0.2.json` contains meta-llama/llama-4-maverick
in within-model fields (10 occurrences; true at v0.2, where only the
similarity basis was mode-filtered), but `data/results/food/0.3.json`
contains zero occurrences of maverick and zero of claude-fable-5.
Mechanism: the N17 approved-slate filter in `scripts/rebaseline_corpus.py`
removes non-slate models from the record set before `run_pipeline`, so
slate-excluded models contribute to nothing in the v0.3 result. The
corrected F3-V3-E above states the v0.3 scope accurately. All other
rulings in this verdict stand unchanged.

Vocabulary check on F3-V3-A/B/C/E: no §1.5.4 forbidden tokens. "within-model
output-distribution analyses" is licit under the noun-class test
(right-hand noun is `output-distribution analyses`; see
`project_within_model_phrase_ruling.md`, 2026-06-11). No U+2014. US English.

### Ruling C. F3-R3-D (SMALL_N_TEXT) disposition

**KEEP DORMANT.** Do not retire. Do not replace on this pass.

Post-promotion state: family n=22, holidays n=21, food n=19 all clear the
15-model floor, so `romney_small_n_warning` is False on all three live
domains and SMALL_N_TEXT does not render on any live surface. On the citable
historical v0.2 food record (warning True, n=12), SMALL_N_TEXT continues to
render byte-identical to the F3-R3-D binding, which preserves the runbook
citable-versioned-result invariant.

Retiring the mechanism is premature: any future domain, filtered subset, or
new collection under n=15 legitimately needs a small-n warning surface.
Replacing the hardcoded "12 models" with a parameterized template that reads
`n_models` from the domain result is desirable but is beyond the copy-pass
scope; open as a fast-follow to the Architect. No fresh SME pass required
for the template-ification (it will not change the wording pattern; SME will
bind the template shape when that task lands).

### Ruling D. N4/N12 methodology footnote (batch A informant-class QA calibration)

**Placement.** New paragraph on MethodologyPage, under a new sub-section
inside the existing "How the measurement works" section or as a small
standalone section between "Uncertainty and failure" and "What this does
not measure". Architect picks the exact heading level and section
placement; SME binds the text.

**BA-QA-FN (binding, verbatim). Methodology footnote text:**

> Two informant classes trigger class-conditioned handling in our
> corpus-QA arithmetic. Reasoning-model informants report inference-time
> reasoning tokens separately from visible output tokens; the latency
> ceiling is class-conditioned to accommodate the deliberation window, and
> the token-consistency check subtracts reasoning tokens before comparing
> visible output against character length. Dense-tokenizer informants use
> tokenizers that produce more tokens per character than the earlier
> cohort; the same token-consistency check uses a denser expected
> characters-per-token ratio for these records. Both branches are properties
> of the informant class, not leniencies: the discriminating power of the
> check on the non-class majority is preserved and a category error against
> the class is removed. QA answers whether a record is fit for analysis;
> the approved slate, curated separately, answers which models the
> published basis includes.

Requirements checklist against N4/N12:
- Class-name (not model_id): "reasoning-model informants", "dense-tokenizer
  informants" (no individual model names). PASS.
- Checks 5 and 6 carry class-conditioned thresholds: named as "latency
  ceiling" and "token-consistency check" respectively (public prose avoids
  Check-number nomenclature since the methodology page is not the QA
  runbook). PASS.
- Two Check 6 conditioning axes named: (i) reasoning-token subtraction,
  (ii) denser expected characters-per-token. PASS.
- Framed as informant-class properties, not leniencies. PASS.
- No "closer to human". PASS.
- No "reasoning models are harder to evaluate". PASS.
- No individual model names on the methodology page. PASS.
- One pattern, cross-linked. PASS (single paragraph, both classes named).
- N15/N17 partition cross-referenced (last sentence). PASS.

### Ruling E. Fable-5 disclosure placement and framing sentence

**Placement confirmed.** A single note on the records surface AND on the
failures surface for each of family, holidays, and food (six placements
total, one per domain per surface). Placement is above or alongside the
claude-fable-5 row on each panel. Do not embed inside a chart tooltip or
hidden expander; the disclosure must be visible without user interaction on
first render of the panel where the row appears (mirrors the F3-R3 U1
posture that classification disclosures are visible-on-render).

**BA-FABLE-FRAMING (binding, verbatim). Single framing sentence preceding the
bound string, on each of the six placements:**

> The claude-fable-5 counts shown on this panel are a product of the
> mechanism described immediately below.

Rationale: light, load-bearing-noun compliant ("mechanism"), avoids agentic
attribution, does not reproduce or paraphrase the mechanism itself
(that is what the bound string does).

**The bound string then follows verbatim (unchanged, from
`docs/status/2026-07-10-batchA-fable5-refusal-cda-sme-verdict.md` (d)):**

> The provider's deployment-side output filter returned empty content
> (stop_reason=refusal) for 22 of 23 free-list elicitation attempts on
> claude-fable-5 in batch A. Under identical prompts collected the same hour,
> claude-opus-4-8 and claude-sonnet-5 completed the same elicitations with zero
> refusals. The pattern is a property of claude-fable-5's deployment configuration,
> not of its training corpus, and does not license any claim about
> claude-fable-5's categorical structure for family or holidays.

Extended-forbidden compliance on BA-FABLE-FRAMING: no "the model refused",
no "Fable declined", no standalone "safety", no "conservatively-tuned
classifier", no belief/thought/worldview vocabulary. PASS.

For the food-domain placement: the bound string references "family or
holidays" in its last clause; that is the 2026-07-10 verbatim text and
ships as-is. The food panel additionally carries the 2 PileSortParseErrors
under the standard failures-panel treatment; those are separate records
and do not need SME copy. The single passing food free-list record for
claude-fable-5 is preserved in `informants.jsonl` per Fable ruling (b) and
is not surfaced as a categorical-structure claim.

### Ruling F. Provenance paragraph replacement (DataPage §15.5(a))

The current paragraph describes the 2026-05-30 toolchain-pinning recompute
in past tense as the most recent event and is stale after 2026-07-12.
Replace verbatim.

**BA-PROV (binding, verbatim). Replacement paragraph, drops into the
`data-provenance-heading` section on DataPage; the `provenance.json`
anchor and its sr-only text are preserved from the current markup:**

> The published family, holidays, and food corpora were rebuilt on
> 2026-07-12 under the same pinned analytical toolchain (NumPy 2.4.4,
> SciPy 1.17.1, Python 3.12) as the 2026-05-30 recompute, with two
> mechanical changes. First, the corpus-build QA path now class-conditions
> two of its collection-QA checks for reasoning-model informants and for
> dense-tokenizer informants (see the methodology footnote on
> informant-class QA calibration for the mechanism); persisted per-record
> verdicts on the raw records are untouched, and reference-set-dependent
> checks inherit their collection-time verdicts. Second, publication
> membership is now decided by a curator-maintained approved-slate list,
> separately from record-level QA: QA answers whether a record is fit for
> analysis, and the slate answers which models the published basis
> includes. The batch A rebuild widens each of the three published
> domains by up to seven additional frontier models. The pinned versions,
> the exact git commit, and the approved slate for each domain are
> recorded in provenance.json, which is regenerated on every published
> bundle.

Vocabulary check: no forbidden §1.5.4 tokens. "within-model sampling
variance" does not appear here (that phrase lives in the term-map
paragraph, ruling G). No U+2014. US English.

### Ruling G. Term-map counts sentence (DataPage §16.2)

**Mechanical swap confirmed:** 15 -> 22 (family), 14 -> 21 (holidays),
8 -> 19 (food). B=200 term bootstrap unchanged, ellipse-widths /
branch-probabilities language unchanged.

**BA-TERMMAP-COUNTS (binding, verbatim). Replacement paragraph, replaces
the entire second sentence in the `term-mds-heading` section on DataPage.
The first sentence ("Term position confidence reflects agreement across
models, not within-model sampling variance.") is unchanged; "within-model
sampling variance" is licit under the noun-class test.**

> The cross-model term map is computed from 22 model informants on family,
> 21 on holidays, and 19 on food; ellipse widths and branch-probability
> values are derived from model-resample bootstrap (B=200), so a sparser
> informant pool produces a different bootstrap envelope shape than a
> denser one even when the per-model agreement is similar.

### Family and holidays ledes: CONFIRM as generated

Family v0.4 lede and holidays v0.4 lede as regenerated by the frozen
generator match their v0.3 templates with mechanical count and Smith's S
number updates. Numbers verified against the facts block: family Smith's
S 0.83, 95% CI [0.67, 0.95], n=22, STRONG_CONSENSUS unchanged; holidays
Smith's S 0.90, 95% CI [0.80, 0.97], n=21, STRONG_CONSENSUS unchanged.
Rounding matches the frozen two-decimal display convention. The
"1 of these 22 models produced low output concentration" template fires
mechanically for family and is correct under Register 1 OCI diagnostics;
the "position on the map is shown without a confidence ellipse" language
is consistent with the F5-T1 R1-a limit-case handling.

Advisory note (non-blocking): both ledes use ASCII double-hyphen `--` in
mid-sentence separator position, which is stylistically an em-dash
substitute. The hard rule is on U+2014 specifically and the templates are
frozen (Phase 5 Q1-Q11), so this does not block promotion; if Mark wants
to move the templates off double-hyphens to comma/colon/parens, that is
a separate template revision beyond the scope of this pass.

## Compliance checklist for Reviewer

Grep-able assertions. Reviewer runs each; any FAIL blocks the merge.

1. `U+2014` (em dash) absent from every bound string in this verdict and
   from every shipped surface: MethodologyPage, DataPage, food v0.3 JSON
   `consensus_type_override_reason`, `consensus_disclosure.ts` (if
   updated with F3-V3 successors), records-panel and failures-panel
   Fable disclosure placements.
2. F3-V3-A ships byte-identical as the food v0.3 domain lede.
3. F3-V3-B ships byte-identical as `consensus_type_override_reason` on
   food v0.3 result JSON.
4. F3-V3-C ships byte-identical as the CI disclosure line adjacent to
   the food override badge (constant successor to `CI_DISCLOSURE_TEXT`).
5. F3-V3-E ships byte-identical as the food v0.3 methodology footnote
   on MethodologyPage. The prior F3-R3-E paragraph is scoped to v0.2
   context or replaced.
6. Food v0.3 result JSON carries `consensus_type_override = "WEAK_CONSENSUS"`
   (or the schema-equivalent override field established at v0.2).
7. `SMALL_N_TEXT` constant retained byte-identical in
   `consensus_disclosure.ts` (F3-R3-D kept dormant).
8. BA-QA-FN methodology footnote paragraph ships byte-identical on
   MethodologyPage.
9. BA-FABLE-FRAMING ships byte-identical, preceding the 2026-07-10 (d)
   bound string, on all six placements (records + failures panels for
   family, holidays, food).
10. BA-PROV ships byte-identical in the DataPage `data-provenance-heading`
    section, replacing the 2026-05-30-anchored paragraph.
11. BA-TERMMAP-COUNTS ships byte-identical in the DataPage
    `term-mds-heading` section, replacing the "15 / 14 / 8" sentence.
12. Extended forbidden vocabulary grep on all newly landed text: none of
    "the model refused", "Fable declined", "safety" as standalone noun,
    "conservatively-tuned classifier" appears. Standard §7 forbidden
    tokens absent.
13. Fable disclosure placements are visible on first render of each
    panel (not gated behind expander or tooltip only).
14. All numeric claims in newly landed text trace to the promotion facts
    block: 5.44 / [2.75, 10.25] / 66 percent / 22 / 21 / 19 / 0.83 /
    [0.67, 0.95] / 0.90 / [0.80, 0.97] / NumPy 2.4.4 / SciPy 1.17.1 /
    Python 3.12 / B=500 / B=200.

## What this ruling does not authorize

- Any change to the frozen lede-template shape (Phase 5 Q1-Q11).
- Any change to the Romney eigenratio computation, the bootstrap scheme,
  the small-n threshold, the consensus-type mechanical mapping, or the
  guard thresholds. Rule 15 governs.
- Retirement of the SMALL_N_TEXT rendering path or of the
  `romney_small_n_warning` field.
- Re-litigation of the F3-R3 straddling-CI ruling; F3-V3 inherits and
  extends the pattern with v0.3-specific numbers.
- Any new claim about claude-fable-5's categorical structure on any
  domain. The 2026-07-10 disposition governs.
- Auto-drafted social posts for the food v0.3 promotion event. The
  drafter-prompt framing note from F3-R3 (round-3 section (e), 2026-06-11)
  carries forward and is extended: for food v0.3, the appropriate framing
  is "with more models in the slate the point estimate on eigenratio
  dropped from 9.48 to 5.44 and the published bootstrap interval on the
  eigenratio now crosses the 5.0 threshold, so we publish the
  conservative classification"; any drafted post must not frame the
  transition as a discovery of decreased model convergence. This routes
  through the standard admin-console per-trigger review.
