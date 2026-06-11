---
name: phase9b-food-guard-trip
description: 2026-06-11 FINAL (round 3) adjudication on Phase 9b food domain. PROMOTE AS WEAK_CONSENSUS at v0.2; 4c bootstrap CI [4.908, 10.338] straddles 5.0 so honest classification is WEAK with undetermined disclosure; mode-coherent slate of 12 models; maverick row already excluded from similarity basis by FOOD-FIX-A; the staged 9.4810 eigenratio is mean-then-eigh on the 12x12 mode-coherent matrix (not 13x13 as initially framed); 5 byte-identical lede/classification/methodology strings drafted at draft time per F5 plain-language binding; FOOD-FIX-A2 (point-then-eigh canonicalization) declared FAST-FOLLOW not promotion-blocking; promotion checklist deltas for Reviewer/UI-UX; rounds 1 and 2 preserved above for trail
metadata:
  type: project
---

## Phase 9b food-domain guard-trip adjudication (2026-06-11)

### ADJUDICATION: INVESTIGATE (not PROMOTE)

The STRONG -> WEAK flip on the food domain is an **artifact** of the staged
analysis, not real signal. The staged result JSON
(`out/rebaseline/food/0.2.json`) shows the Option A consensus free-list for
five of the thirteen slate models is the empty list `[]` with `raw_order: []`:

- `deepseek/deepseek-v3.2` (5/5 QA-passing runs reported by operator)
- `google/gemini-2.5-pro`        (5/5)
- `meta-llama/llama-4-maverick`  (2/5 thin)
- `mistralai/mistral-large-2512` (5/5)
- `x-ai/grok-4`                  (4/5)

Operator-reported QA counts are non-zero for 4 of those 5 (only llama-4-maverick
is thin at 2/5; the others are 4-5 of 5). An empty consensus free-list for a
model that has 4-5 QA-passing collection runs is **not** a substantive finding
about that model's categorical structure. It is a free-list aggregation /
staging step that did not run to completion for those rows. Probable causes
(to be confirmed in investigation): the consensus_freelist builder did not
pick up the new records (campaign / scope filter), or new-collection records
did not land under the `domain_slug` the aggregator queries, or an upstream
ID-mapping mismatch (`model_id` vs `model_version_returned`).

[Round 1 details preserved; see prior git history for the unedited body.]

### Status
- ADJUDICATION: INVESTIGATE
- Live site: leave 8-model STRONG_CONSENSUS up, version-pinned.
- Social pipeline: do NOT advance this staged result to
  `manifest.json` / `data/results/` / detect.
- Re-routed to: Architect (investigation steps 1-3); CDA SME on
  return for steps 4-5.

---

## ROUND 2 (2026-06-11): RE-ADJUDICATION ON CLEANER STAGING

### Round-1 hypothesis disposition

- Step-2 hypothesis (`model_id` vs `model_version_returned` join-key
  mismatch): **DISPROVEN.** The empty consensus free-lists in the prior
  staging were because the five new models then had only
  `cross_model_consensus` records (placeholder freelists by design of
  that mode), not a join-key bug. Operator re-collected in `single_pass`
  mode (campaign 2026-06-11); fresh records persist correctly in
  `parsed_items`.

### Round-2 staged numerics

- `romney_eigenratio`: 6.586410170380379 (prior live) -> 4.447034058312089
  (round-2 staged). STRONG_CONSENSUS -> WEAK_CONSENSUS, warning flipped
  False -> True. Guards T-1, T-5, T-6 tripped again.
- Centrality bit-identity narrows from 4 models (round-1) to 3
  (round-2): the three Claudes share `0.26069072811802785` to the float
  ULP.

### LOCALIZED MECHANISM (load-bearing)

The Claude-row nullification originates in mds.py L41-78
compute_cross_model_similarity (shared-items intersection + NaN-rescue)
compounded by cooccurrence.py L91-102 build_cooccurrence_matrix mixed-mode
item-source fallback plus pipeline.py L468 load_records no
collection_mode filter.

### DISPOSITION: PROMOTE-AFTER-FIX with separable scopes

Concern A (mixed-mode similarity contamination): fix at pipeline level via
mode-coherent similarity basis.
Concern B (genuine STRONG -> WEAK question): re-adjudicate once Concern A is
resolved against clean numbers.

### Round-2 status
- ADJUDICATION: PROMOTE-AFTER-FIX (Concern A first, then sensitivity,
  then re-adjudication).
- Live site: unchanged, version-pinned.
- Social pipeline: continues blocked on staged result.
- Re-routed to: Architect (Concern A scope decision + Coder dispatch).
- Round-1 hypothesis (join-key mismatch) DISPROVEN and superseded.

---

## ROUND 3 (2026-06-11): FINAL ADJUDICATION ON CLEAN MODE-COHERENT STAGING

### Verdict: PROMOTE as v0.2 with classification WEAK_CONSENSUS

FOOD-FIX-A landed (commit dc9a1ba, full suite green). Re-staged food at
`out/rebaseline/food/0.2.json`:

- guard: PASS (lede-class thresholds T-1/T-5/T-6 no longer trip on
  staged-vs-live deltas at the v0.2 staging step itself; manifest reports
  `guard: "pass"`, `model_count: 12`).
- No constant-0.5 rows in the staged similarity_matrix.
- 12 distinct centralities (the three Claudes no longer share float-ULP
  identity).
- maverick: correctly absent from `cultural_centrality_scores`,
  `centrality_ci`, and from the similarity_matrix. F1 satisfied at the
  schema surface (centrality None equivalent: key absent from the dict).
  Maverick remains in the `models` array of 13 and continues to flow
  through within-model results / cooccurrence / sutrop_csi as a Register 1
  informant for its own model.
- Staged published numerics: `romney_eigenratio = 9.481027900819534`;
  `consensus_score = 0.6242646087064366`; `consensus_ci = [0.4983, 0.7814]`;
  `consensus_type = STRONG_CONSENSUS`; `romney_small_n_warning = True`
  (carry-forward expected; n=12 < 15 small-n threshold).

### IMPLEMENTATION DISCREPANCY RULING

The user-presented framing of the discrepancy is **factually incorrect about
the staging**:

> "the STAGED result's own romney_eigenratio is 9.4810, computed at
> pipeline.py L809 over the FULL 13x13 similarity_matrix, which includes a
> maverick row derived from its 2 QA cross_model_consensus records"

Direct inspection of `out/rebaseline/food/0.2.json` and of
`packages/cdb_analyze/cdb_analyze/pipeline.py` L819-919 (post-FOOD-FIX-A)
shows:

- `similarity_matrix` row 0 has 12 entries, not 13. The staged matrix is
  12x12.
- `sim_model_ids` is the mode-coherent slate (maverick excluded by
  construction because maverick has zero single_pass QA records).
- L919 `compute_romney_eigenratio(sim_np_romney)` consumes
  `np.array(similarity_matrix)` where `similarity_matrix` IS already the
  mode-coherent 12x12 produced at L833 from `bootstrap_mds_ellipses(
  records_by_model_for_similarity, ...)`, and
  `records_by_model_for_similarity` is mode-coherent per FOOD-FIX-A.

So FOOD-FIX-A's mode-coherent constraint **already** excluded maverick from
the similarity basis. The published 9.4810 IS the 12-model eigenratio.

**The real discrepancy** is between two different "12-model basis" numbers:

- 9.4810 (staged): eigh applied to the mean over B=500 bootstrap replicates
  of the 12x12 similarity matrix. This is "eigh(mean(sim_replicates))".
- 8.2978 (orchestrator 4a): eigh applied to a single-pass point-estimate
  12x12 similarity matrix built once from the mode-coherent records. This
  is "eigh(sim_point_estimate)".

These are two different objects answering two different questions. Both are
internally well-defined. They differ because eigenratio is a non-linear
functional and `mean -> eigh != eigh -> mean`. The bootstrap CI on the
**eigenratio of each replicate** (orchestrator 4c) reports CI95
[4.908, 10.338] median 6.954, B=500, seed 20260611. Both 9.4810 and 8.2978
sit inside that interval. The 4c CI is the load-bearing uncertainty band.

### Rulings (i), (ii), (iii)

**(i) Canonical number for the published result.** The staged 9.4810 stays
canonical. Rationale: (a) it is what the published pipeline computes
end-to-end with B=500 and seed 42 per the F5 binding (no off-pipeline
shadow); (b) downstream consumers (centrality, MDS coords, ellipses) are
all derived from the same bootstrap-mean similarity matrix, so eigh on the
same object preserves internal coherence; (c) changing it post hoc on a
manual orchestrator number would break the published-pipeline-is-the-source-
of-truth invariant. The orchestrator's 8.2978 is a **reference value** for
the canonicalization-question sensitivity discussion in the methodology
footnote, not a replacement for the published value.

**(ii) FAST-FOLLOW, not promotion-blocking.** The eigh-mean vs mean-eigh
question is a real methodological question (which functional of the
bootstrap distribution should be canonical for the point classification?)
but it is NOT a contamination question. The honest classification at v0.2
does not pivot on which of {9.4810, 8.2978} is canonical because **both
sit on the STRONG side of 5.0, and the 4c CI straddles 5.0 regardless of
the point convention chosen**. The classification disclosure is driven by
the CI, not by the point. Open FOOD-FIX-A2 as a fast-follow with the
following scope:

  - Decide canonical point-estimate convention for the published eigenratio
    (eigh-of-mean vs mean-of-bootstrap-eigenratios vs median-of-bootstrap-
    eigenratios). Default proposal: median of the per-replicate eigenratios
    (matches the CI median; gives a point estimate that is internally
    coherent with the published CI band).
  - Apply consistently across food + family + holidays at the next minor
    bump.
  - The methodology footnote text in F3-R3 below pre-discloses this
    open question.

**(iii) Maverick row in the similarity heatmap.** The staged
`similarity_matrix` does NOT include a maverick row (12x12 confirmed). The
dashboard heatmap may not invent one. The dashboard MUST drop maverick
from the similarity heatmap dimension entirely AND surface a labeled
disclosure in the heatmap caption or aria-label noting that one model
(specify `meta-llama/llama-4-maverick`) is in the slate but not in the
similarity basis because it has no single_pass collection records for this
domain. This is the F1 disposition at the visualization surface. The
within-model output-distribution view for maverick remains live (Register
1) and maverick continues to appear in the cooccurrence / pooled term map
where its records do contribute.

### (b) Classification decision for food v0.2

**Published `consensus_type`: `WEAK_CONSENSUS` with `undetermined`
disclosure.**

Justification:

- The point-estimate eigenratio (9.481 staged; 8.298 orchestrator 4a;
  6.954 4c median) places food on the STRONG side of the 5.0 LSB
  threshold at every reasonable point-convention.
- The 4c bootstrap CI95 [4.908, 10.338] **straddles 5.0** (lower bound
  4.908). This trips the round-1 pre-registered rule: "If the CI
  straddles 5.0, the classification is genuinely undetermined and the
  lede language must reflect that, not pick a side."
- The 4b sensitivity (also dropping mistral-large-2512) reports 8.3549,
  insensitive to the thinnest contributor. So the indeterminacy is not
  driven by a single fragile contributor; it is properly an n=12 small-n
  width-of-uncertainty result.
- `romney_small_n_warning: True` is already True at n=12 < 15 (n<15
  threshold per 2026-04-23 reconciliation, see project_romney_small_n_threshold.md).

Choice between honest options:

(A) Publish `consensus_type: STRONG_CONSENSUS` and add an "uncertainty
straddles threshold" caveat. Rejected: any reader who only consumes the
classification label receives a confident claim the CI does not support.
This violates ARCHITECTURE.md §4.2.6 / §4.5 (no point without uncertainty).

(B) Publish `consensus_type: WEAK_CONSENSUS` with the disclosure that the
point estimate is on the STRONG side but the uncertainty straddles. Chosen.
This is the conservative read that matches the runbook's "honest
indeterminacy" pre-registration.

(C) Publish a third-state label like `INDETERMINATE` or
`STRADDLES_THRESHOLD`. Rejected: the published Caulkins typology is a
fixed six-state vocabulary; introducing a new label here would require an
architecture amendment for one domain. The disclosure path (B) is
sufficient.

**Schema implication:** The published `consensus_type` field is currently
auto-derived from `romney_eigenratio >= 5.0`. The staged value 9.4810
therefore mechanically populates `STRONG_CONSENSUS`. The SME ruling
**overrides** the mechanical classification for v0.2. The Coder must
either:

  - (i) Override `consensus_type` to `WEAK_CONSENSUS` at the result-JSON
    promotion step (Architect-decided implementation locus), with a
    one-line code comment naming this memo and naming round-3 of
    project_phase9b_food_guard_trip.md, OR
  - (ii) Surface a new top-level field `consensus_type_disclosure` set to
    a fixed string and have the dashboard render the disclosure
    prominently next to the label.

CDA SME preference is **(i) with an explicit override field** so the
override is auditable: add `consensus_type_override: "WEAK_CONSENSUS"`
and `consensus_type_override_reason` (fixed string from the F3-R3 draft
below) alongside the auto-derived `consensus_type`. The published label
is the override. The Architect picks the schema shape.

### (c) Byte-identical drafts (F5-R3 binding)

Per F5 plain-language carry-forward (bind plain-language strings at draft
time), the following byte-identical strings are SME-issued. Em-dash-free
(verify U+2014 absent in every string), no §1.5.4 forbidden vocabulary,
US-English, register-correct. The Coder ships these verbatim; any edit
requires a fresh SME pass.

**F3-R3-A (binding) - Domain lede for food v0.2 on the dashboard:**

"The food domain shows broad agreement across the 12-model slate. The
point estimate sits comfortably on the strong-consensus side of our
threshold, but the uncertainty band crosses it. The honest read is
that the strength of agreement is not nailed down at this collection
width."

**F3-R3-B (binding) - Classification disclosure (the override reason
string; populates `consensus_type_override_reason` if the schema shape in
(i) above is chosen):**

"Point estimate is on the strong-consensus side of the 5.0 threshold;
the 95 percent bootstrap interval crosses 5.0. We publish the
conservative classification and disclose the indeterminacy rather than
claim a category the uncertainty does not support."

**F3-R3-C (binding) - CI disclosure line (used on the dashboard next to
the eigenratio number):**

"Romney CCM eigenratio 9.48, 95 percent bootstrap interval [4.91,
10.34], B=500. The interval crosses the 5.0 strong/weak threshold."

(Numerics rounded to two decimals for the disclosure line. The full-
precision values stay in the JSON.)

**F3-R3-D (binding) - Small-n carry-forward line (per round-1 standing
requirement that the small-n warning surface on the food methodology
page; rendered wherever `romney_small_n_warning: True` is surfaced):**

"The slate is 12 models, below the 15-model floor where Romney CCM
eigenratios become statistically reliable. Read the classification
with that floor in mind."

**F3-R3-E (binding) - Methodology page footnote for food v0.2
(extends and supersedes the FOOD-FIX-A F3 footnote; the FOOD-FIX-A
footnote stays for the mode-coherent basis explanation, this footnote
adds underneath it):**

"For the food domain at v0.2, the cross-model similarity basis is
the 12-model mode-coherent slate. One additional model
(meta-llama/llama-4-maverick) is in the corpus for this domain but
does not appear in the similarity basis because it has no single-pass
collection records for food. That model still contributes to its own
within-model output-distribution analysis and to the pooled term map.
The Romney CCM eigenratio is 9.48 with a 95 percent bootstrap interval
of [4.91, 10.34] over B=500 model-resamples. The lower interval bound
crosses the 5.0 strong-consensus threshold, so the classification is
published as weak-consensus with the indeterminacy disclosed rather
than published as strong-consensus with a hidden uncertainty caveat.
A separate open question on how to canonicalize the published
eigenratio against its bootstrap distribution is tracked under
FOOD-FIX-A2."

Vocabulary scan on F3-R3-A through F3-R3-E:

- No §1.5.4 forbidden tokens (cognition-attribution forms,
  "publishable", "closer to human is better", "within-model
  consensus" / "within-model CCM" / "within-model cultural consensus" /
  "within-model eigenratio").
- "within-model output-distribution analysis" appears in F3-R3-E; licit
  under the noun-class test (right-hand noun is `output-distribution
  analysis`, not a consensus / CCM / cultural-consensus noun; cf.
  2026-06-11 within-model phrase ruling, project_within_model_phrase_ruling.md).
- No em dashes (U+2014). Period.

### (d) Promotion checklist deltas

Reviewer must verify:

- R1. `consensus_type_override` is set to `WEAK_CONSENSUS` in the
  promoted result JSON (or whichever schema shape the Architect picks
  per ruling (b) above). The auto-derived `consensus_type` may remain
  `STRONG_CONSENSUS` in the JSON for audit but the published label is
  the override.
- R2. `centrality_ci` is published and present for all 12 mode-coherent
  models (Remedy B contract; non-empty dict).
- R3. F3-R3-A, F3-R3-B, F3-R3-C, F3-R3-D, F3-R3-E ship byte-identical
  (verify U+2014 absent in each).
- R4. The methodology page surfaces both the FOOD-FIX-A footnote
  (mode-coherent basis explanation) AND the F3-R3-E footnote (v0.2
  classification disclosure) co-located on the food domain methodology
  surface.
- R5. The `romney_small_n_warning` surfacing per round-1 standing note
  ships on the methodology page co-located with the food classification
  (F3-R3-D).
- R6. Maverick is NOT rendered as a row or a column in the similarity
  heatmap on the dashboard; maverick IS still rendered in the
  within-model output-distribution view and in pooled-term-map
  surfaces where its records contribute. The heatmap disclosure
  (caption or aria-label) names maverick by `model_id` and gives the
  reason (no single_pass collection records for this domain).
- R7. The runbook's "versioned DomainResults stay citable" invariant
  is preserved: the prior v0.1 8-model STRONG result remains a
  reproducible reference; v0.2 supersedes it on the live site.

UI/UX must verify:

- U1. The classification badge on the food domain reads WEAK_CONSENSUS
  and is co-located with the CI disclosure line (F3-R3-C). The point
  estimate, the CI, and the threshold value 5.0 are all visible without
  user interaction.
- U2. The lede (F3-R3-A) is visible above the fold on the food domain
  page and is rendered without paraphrase.
- U3. The methodology footnote (F3-R3-E) is reachable in 1 click from
  the classification badge.
- U4. R10 hygiene: every published numeric on the dashboard for food
  (eigenratio, centralities, consensus_score) carries its CI bracket.
  centralities have `centrality_ci` from the published JSON. eigenratio
  carries the F3-R3-C CI line.
- U5. Accessibility floor (WCAG AA) holds with the override label.
- U6. The similarity heatmap caption/aria-label discloses the maverick
  drop per R6 in plain language.

Tester must verify:

- T1. Byte-identity regression: re-running `rebaseline_corpus.py
  --domain food` with the same seed and the same input corpus reproduces
  `out/rebaseline/food/0.2.json` byte-for-byte (FOOD-FIX-A A8 contract).
- T2. F3-R3-A through F3-R3-E appear verbatim in the dashboard build
  output (snapshot test or grep-on-build).
- T3. Vitest harness (if available per project_session_checkpoint_0525b)
  covers the heatmap maverick-drop disclosure assertion.

### (e) Interim live-site posture

The interim ruling (prior 8-model STRONG_CONSENSUS at `analysis_version:
0.1` stays live, version-pinned) **ends at promotion**. Once v0.2 lands
with the WEAK_CONSENSUS override and the F3-R3-* strings, v0.2 is the
live published classification for food. The v0.1 result remains in the
open-data bundle as a citable historical reference but the dashboard
front page displays v0.2.

Social pipeline: detect cron unblocked for food v0.2 ONLY after
promotion, ONLY against the new v0.2 baseline, and ONLY for events
properly triggered by v0.2 vs future versions. The 0.1 -> 0.2 transition
itself (STRONG -> WEAK at the same threshold, plus 8 -> 12 model widening)
is a CLASSIFICATION_DRIFT event by detector definition, but for the
detect path the post-promotion drift must not surface a triumphant
finding-style draft. The drafter's `framing_checks` validator already
flags cognition-attribution wording per CLAUDE.md §7, but the SME flags
here: **any drafted social post about food at promotion must not frame
the WEAK_CONSENSUS publication as a discovery that models converged less
than previously expected; the appropriate framing is "with more models
in the slate, the published uncertainty band on agreement now crosses
the threshold."** This is a drafter-prompt rather than validator
question; the runbook will route it through the existing CDA SME
pre-trigger drafter-prompt review.

### Status - Round 3 (final)

- ADJUDICATION: PROMOTE-AS-WEAK at v0.2.
- Live site: 8-model STRONG_CONSENSUS at v0.1 stays up until v0.2 lands;
  v0.2 then becomes the live published classification.
- Social pipeline: unblocked for food v0.2 ONLY after promotion and
  ONLY with the SME-issued drafter-prompt framing note above.
- FOOD-FIX-A2 (eigenratio canonicalization across the bootstrap
  distribution): FAST-FOLLOW, not promotion-blocking. Architect opens
  the task at the next planning slot.
- 7 binding F3-R3 strings (A..E + R6 heatmap disclosure + override
  reason).
- 7 Reviewer items (R1..R7).
- 6 UI/UX items (U1..U6).
- 3 Tester items (T1..T3).
- Round-2 PROMOTE-AFTER-FIX disposition CLOSED-AS-PROMOTED.
- Round-1 INVESTIGATE disposition CLOSED-AS-RESOLVED.

### Forward carry to future SME passes

- The eigh-of-mean vs mean-of-eigh question (FOOD-FIX-A2) generalizes to
  the consensus_score field and to all bootstrap-derived point estimates
  in the published JSON. The methodology footnote (F3-R3-E) names it
  explicitly so the question is not silently re-opened later.
- The next domain that crosses a Caulkins typology threshold with a
  bootstrap CI straddling the boundary inherits the F3-R3 disclosure
  pattern (lede + CI line + override reason + footnote). The SME does
  NOT pre-bake this into a template; each disclosure is individually
  reviewed because the threshold being crossed (5.0 vs 3.0 vs another
  Caulkins boundary) changes the prose.
- The interim ruling that v0.1 result stays citable in the open-data
  bundle even after v0.2 supersedes it is consistent with the runbook
  invariant; future revisions to a domain at minor-bump granularity
  inherit this posture.
