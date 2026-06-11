---
name: food-v02-fix-simids-verdict
description: 2026-06-11 FOOD-V02-FIX-SIMIDS plan PASS-WITH-NOTES; published-contract clarification adding `similarity_model_ids: list[str] = []` to DomainResult naming the AUTHORITATIVE matrix row/col order (already the mode-coherent 12-model slate under FOOD-FIX-A + R6 basis-exclusion); CDA-SME routing call confirmed NO new methodology gate (no Smith's S / Sutrop / Romney / OCI / bootstrap / Mantel / ARI / Procrustes change; no threshold / ConsensusType / framing change; no lede / methodology copy touch; round-3 R6 maverick basis-exclusion ruling unchanged and now SURFACED rather than INFERRED); 4 binding notes - N1 docstring/dictionary must contain explicit pointer "consult mds_coordinates.keys() for the same slate" reframing concession (pipeline.py L497/865-872/891-895 confirms mds_coordinates / cultural_centrality_scores / centrality_ci / similarity_matrix are all keyed by sim_model_ids, mapping inference is sound but new field is the named contract), N2 plan §5 family/holidays "retain empty default" language must NOT survive into DATA_DICTIONARY §2 row prose as "no basis-exclusion happened" (family + holidays empty default ONLY means the field has not been backfilled, not that those domains had no slate filtering; per FOOD-FIX-A those domains use single-mode collection so sim_model_ids equals model_ids; dictionary text must say "default empty list means the legacy invariant matrix-dims == len(models) applies; for analyses produced by the post-v0.1.28 pipeline, similarity_model_ids is always populated"), N3 plan §6 / §7 routing call CORRECT - this is a contract-naming task not a methodology task; Architect properly carried sign-off; but T9 status doc append MUST explicitly cite round-3 R6 by paragraph anchor so the audit trail from R6 (maverick excluded "by construction") through the new explicit field is intact for the next SME-of-record; N4 plan T5 SimilarityHeatmap consumer change MUST NOT silently shift the slate that the heatmap renders - the assertion in §7 ("rendered pixels for food are byte-identical to the pre-fix state") is methodologically correct under the round-3 mode-coherent slate, but the Coder must verify by running the test suite that the slate ContentArea.tsx L352-354 set-difference (models - mds_coordinates.keys()) produces the SAME excluded set as (models - similarity_model_ids); if these diverge the existing inferred-from-mds_coordinates disclosure caption at L351-365 is wrong and the round-3 R6 disclosure is at risk; PASS on all 4 axes; no new lede / methodology text in scope; em-dash hard rule applies to all 4 acceptance criteria
metadata:
  type: project
---

## Verdict

PASS-WITH-NOTES on FOOD-V02-FIX-SIMIDS Architect plan.

## Routing call

Architect's §6 ("CDA SME review required? NO") is **correct**. The fix is a
published-contract clarification (naming what was already true on disk).
Round-3 R6 maverick basis-exclusion ruling is unchanged. No methodology
measure, threshold, framing, lede, or copy moves.

I am issuing PASS-WITH-NOTES (not PASS) because I was explicitly invoked
and the substantive review identified 4 binding notes that improve the
audit trail and prevent a quiet re-introduction of the R6 inference path.

## Four-axis scorecard

- Axis 1 (protocol validity): PASS. No protocol change.
- Axis 2 (analytical validity): PASS. No analytical change. Slate
  identity (`sim_model_ids` = `mds_coordinates.keys()` =
  `cultural_centrality_scores.keys()` = `centrality_ci.keys()` = matrix
  row/col index) holds at pipeline.py L497 / L865-872 / L891-895 / L833.
- Axis 3 (claims validity): PASS. No new claim. Round-3 R6 disclosure
  caption logic stays.
- Axis 4 (audience translation): PASS. New field is contract-level
  (open-data consumer affordance), not user-facing copy. The dashboard
  pixel surface for food / family / holidays is unchanged.

Register compliance: PASS. Vocabulary compliance: PASS.

## Binding notes (N1..N4)

N1 - Docstring and DATA_DICTIONARY row must include the cross-reference
"consult `mds_coordinates.keys()` for the same slate". The plan already
states this in §3 semantics text; this note BINDS it for the docstring
and the dictionary row prose so the equivalence is on the audit trail.

N2 - Plan §5 phrasing "family v0.3 and holidays v0.3 results retain the
empty default and the legacy invariant applies until their next natural
re-baseline" must NOT survive into DATA_DICTIONARY §2 row prose as a
claim about basis-exclusion history. The dictionary row must say:
"Default empty list means the legacy invariant (matrix dims ==
len(models), models[i].model_id keys row/column i) applies. Post-
v0.1.28 pipeline output always populates this field." Family + holidays
under FOOD-FIX-A use no mode filter (similarity_collection_mode=None at
rebaseline_corpus.py); for them sim_model_ids == model_ids by
construction, but the published JSON on disk still carries the empty
default until natural re-baseline. The dictionary text must not imply
either domain was basis-filtered.

N3 - T9 status-doc append must cite round-3 R6 by paragraph anchor (the
"Maverick row in the similarity heatmap" paragraph in
docs/status/2026-06-11-phase9b-food-campaign.md). The named field is the
durable surface that R6's "by construction" claim now points at. The
audit chain R6 -> FOOD-FIX-A mode-coherent slate -> explicit
similarity_model_ids must be reachable from a future SME-of-record
without spelunking commit history.

N4 - T5 SimilarityHeatmap consumer change must preserve the round-3 R6
disclosure caption. ContentArea.tsx L351-365 currently computes the
excluded set as (domain.models - Object.keys(domain.mds_coordinates));
the plan §5 last paragraph asserts this equals (domain.models -
domain.similarity_model_ids) "by construction". The Coder must verify
this equivalence in T7's vitest run: a new assertion that for food, the
heatmap-exclusion-caption count equals (models.length -
similarity_model_ids.length) and the excluded model_ids are the same
set. If these diverge for any domain, that is an upstream finding and
T3's "STOP and surface" gate fires.

## Carry-forward to future SME passes

- The new `similarity_model_ids` field is the durable contract for the
  "model in slate but not in similarity basis" disclosure that round-3
  R6 binds. Future basis-exclusion rulings (e.g., centrality-null
  exclusions per Remedy B, or future mode-filter exclusions) populate
  through this same field; the disclosure caption template at
  ContentArea.tsx §23.3 inherits.
- FOOD-FIX-A2 (eigenratio canonicalization across the bootstrap
  distribution) remains FAST-FOLLOW per round-3 (e) and is NOT
  re-opened here. Plan §6 correctly avoids touching it.
- The Phase 9b food guard-trip round-3 record is now CLOSED-AS-
  CONTRACT-NAMED for the R6 disclosure surface.
