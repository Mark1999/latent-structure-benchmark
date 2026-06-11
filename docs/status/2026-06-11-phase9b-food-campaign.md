# Phase 9b Food Campaign Status (2026-06-11)

**Task:** FOOD-FIX-A: mode-coherent similarity basis for mixed-mode corpora  
**Status:** Implementation complete, pending Reviewer + Tester + Concern B re-adjudication

---

## 1. Background

The Phase 9b food domain widening (adding 5 new models to the 8-model prior slate)
triggered a STRONG_CONSENSUS -> WEAK_CONSENSUS flip in the staged result. The CDA SME
adjudication (two rounds) localized the flip to a pipeline artifact, not a substantive
finding. See `.claude/agent-memory/cda_sme/project_phase9b_food_guard_trip.md` for
the full investigation trail.

### Round 1 (2026-06-11): INVESTIGATE

Empty consensus free-lists for 5 of 13 models in the staged result. Null-padded
similarity rows for 4 models. Probable cause: join-key mismatch or staging filter.
Routed to Architect for investigation.

### Round 2 (2026-06-11): PROMOTE-AFTER-FIX (two separable concerns)

Round-1 hypothesis (join-key mismatch) disproven. The empty free-lists in round 1
were because the 5 new models had only cross_model_consensus records at that time.
After re-collection in single_pass mode, round-2 staging showed the correct free-lists
for 8 of 13 models but still tripped the eigenratio guards (4.447 vs 6.586 prior).

Three-site mechanism localized:
1. `cooccurrence.py` L91-102: item-source fallback makes per-model mat.items
   heterogeneous across the slate in a mixed-mode corpus.
2. `mds.py` L41-78: shared-items intersection collapses to a small subset on which
   single_pass models with identical pile structure produce constant upper-triangle
   vectors -> NaN -> 0.5 Mantel null.
3. `pipeline.py` L468: load_records without collection_mode filter, producing the
   mixed-mode records_by_model that drives the failure.

Two concerns identified:
- Concern A (pipeline fix): mode-coherent similarity basis. File scope for Coder.
- Concern B (genuine STRONG -> WEAK question): requires clean re-staged numbers.
  Out of scope for this task; handled after Concern A fix lands.

---

## 2. Gate trail (FOOD-FIX-A)

| Stage | Status | File |
|---|---|---|
| Architect plan | APPROVED | (this document, §3) |
| CDA SME round 3 | PASS-WITH-NOTES | `.claude/agent-memory/cda_sme/project_food_fix_a_verdict.md` |
| Coder | COMPLETE | (this commit) |
| Reviewer | PENDING | |
| Tester | PENDING | |
| Re-run rebaseline_corpus.py food | PENDING | |
| CDA SME Concern B re-adjudication | PENDING | |

---

## 3. Architect plan scope (Concern A)

Add `similarity_collection_mode: str | None = None` parameter to `run_pipeline()`.
When set, constrain the cooccurrence matrices and all downstream Register 2
similarity steps to records with matching collection_mode. Models with zero matching
records are dropped from the similarity slate. Register 1 paths unaffected.

Pass `similarity_collection_mode="single_pass"` in `scripts/rebaseline_corpus.py`
for the food domain. Pass `None` for family and holidays (single-mode legacy slates;
byte-identical behavior preserved).

Add WARNING diagnostic to `compute_cross_model_similarity()` when NaN rescue fires.

---

## 4. Files changed in this commit

- `packages/cdb_analyze/cdb_analyze/mds.py`: added logger + WARNING diagnostic for
  NaN rescue in compute_cross_model_similarity() (F4 byte-identical text).
- `packages/cdb_analyze/cdb_analyze/pipeline.py`: added similarity_collection_mode
  parameter to run_pipeline(); mode-coherent records_by_model_for_similarity view;
  all Register 2 steps consume the mode-coherent view; Register 1 paths unchanged.
- `scripts/rebaseline_corpus.py`: DOMAIN_CONFIG gains similarity_collection_mode
  per domain; rebaseline_domain() passes it to run_pipeline().
- `tests/unit/test_mode_coherent_similarity.py`: four test cases (A6, A7, A8).
- `docs/DATA_DICTIONARY.md`: v0.1.26 changelog entry + §2.11 (similarity_collection_mode
  semantics, scope table, dropped-model behavior, food footnote byte-identical text,
  reproducibility note, F10 cross-reference to round-2 guard-trip memo).
- `docs/status/2026-06-11-phase9b-food-campaign.md`: this file.

---

## 5. Live-site posture (unchanged by this commit)

The prior 8-model STRONG_CONSENSUS food result remains live, version-pinned at
`analysis_version: 0.1`. This commit does NOT promote the 13-model staged result.
Promotion gate requires Concern B re-adjudication on clean numbers (CDA SME).

Social pipeline detect continues blocked on the staged result until the manifest
gate is cleared after Concern B.

---

## 6. Concern B posture (out of scope here)

After this fix lands and `uv run python scripts/rebaseline_corpus.py --domain food`
completes successfully (no threshold crossing on the clean numbers), the CDA SME
re-adjudicates on:
- 4a: eigenratio on 12-model slate (dropping maverick: zero single_pass records,
  mode-pure cross_model_consensus, 2 QA records).
- 4b: eigenratio on 11-model slate (also dropping thinnest single_pass new model).
- 4c: model-resample bootstrap B=500, eigenratio CI. If CI straddles 5.0, the
  classification is genuinely undetermined.

Replacement lede language is drafted only after clean numbers exist and the SME
makes the STRONG/WEAK call. Not pre-staged here.

---

## Round 3: sensitivity sweep and final CDA SME adjudication (2026-06-11)

Staging round 3 (post FOOD-FIX-A): guard=PASS, 12-model mode-coherent basis, no degenerate rows, maverick correctly basis-excluded (centrality null).

**Sensitivity table (Concern B):**
- 4a baseline (12 models): eigenratio 8.2978 (point-estimate matrix) / 9.4810 (staged, bootstrap-mean matrix; SME ruled canonical; eigh-of-mean vs mean-of-eigh canonicalization tracked as FOOD-FIX-A2 fast-follow).
- 4b drop thinnest contributor (mistral-large, 11 models): 8.3549. Insensitive.
- 4c model-resample bootstrap B=500: CI95 [4.908, 10.338], median 6.954. THE INTERVAL CROSSES THE 5.0 THRESHOLD.

**Final adjudication (round 3, PASS-WITH-NOTES):** publish food v0.2 as WEAK_CONSENSUS via a consensus_type_override with auditable reason, per the pre-registered indeterminacy rule (point estimate strong-side, CI straddling). Five byte-identical disclosure strings (F3-R3-A..E) delivered in the SME memory; 7 Reviewer + 6 UI/UX + 3 Tester promotion checklist deltas; maverick dropped from the heatmap dimension with named disclosure; small-n warning co-located; prior v0.1 STRONG stays citable; social drafter framing note binding. Schema implication: consensus_type_override + reason fields (cdb_core change, rule 6: Architect sign-off + DATA_DICTIONARY co-update in the promotion task).

**Awaiting Mark's GO/NO-GO on promotion (published-claim change).**

---

## 7. PROMOTE-FOOD-V02 gate trail (2026-06-11)

Gate verdicts for the promotion commit:

| Stage | Status | File / Reference |
|---|---|---|
| CDA SME round 3 | PASS-WITH-NOTES (P1-P8) | `.claude/agent-memory/cda_sme/project_phase9b_food_guard_trip.md` round 3 adjudication; full verdict: `docs/status/2026-06-11-promote-food-v02-cda-sme-verdict.md` |
| UI/UX | PASS-WITH-NOTES (§23.1-23.3) | DESIGN_SYSTEM.md §23 amendment; full verdict: `docs/status/2026-06-11-promote-food-v02-uiux-verdict.md` |
| Coder | COMPLETE | This commit (PROMOTE-FOOD-V02) |
| Reviewer | PENDING | |
| Tester | PENDING | |

### Coder application of gate notes

**CDA SME P1 (eigenratio CI constants):** Applied. `CI_DISCLOSURE_TEXT` and `SMALL_N_TEXT` in `apps/dashboard/src/copy/consensus_disclosure.ts` are inline constants, not computed from `domain.consensus_ci`.

**CDA SME P2 (em-dash grep coverage):** Applied. All new files checked; no U+2014 in any new generated copy. Test T1h, T2 em-dash suite, and T1c byte-identity assertions enforce this mechanically.

**CDA SME P3 (schema shape):** Applied. `consensus_type_override: ConsensusType | None = None` and `consensus_type_override_reason: str = ""` added to `DomainResult` in `cdb_core/schemas.py`. DATA_DICTIONARY.md v0.1.27 co-update in this commit.

**CDA SME P4 (single commit):** Applied. This is one commit covering schema, data, publish, dashboard, tests, and docs per §8 exception (schema change with DATA_DICTIONARY co-update).

**CDA SME P5 (maverick scoping):** Applied. Maverick excluded from `mds_coordinates`, `cultural_centrality_scores`, `similarity_matrix`, and `centrality_ci`. Maverick retained in `models` list. Heatmap exclusion caption derives excluded models from `Set(mds_coordinates.keys())` set-difference with `models`.

**CDA SME P6 (F3-R3-E placement):** Applied. F3-R3-E footnote paragraph at `id="food-v02-footnote"` in `MethodologyPage.tsx`, co-located with FOOD-FIX-A footnote in the food domain analysis notes section.

**CDA SME P7 (social drafter carve-out):** No social drafter changes in this commit. The food domain social manifest gate remains blocked pending Reviewer + Tester pass.

**CDA SME P8 (domain-scoped pattern key):** Applied. `_select_pattern()` in `lede.py` checks both `domain_slug == "food"` and `analysis_version == "0.2"` before returning `"weak_consensus_with_straddling_ci_food_v02"`.

**UI/UX §23.1 (override badge):** Applied. `.content-area__override-badge` with `var(--color-warning)` left border, methodology deep-link anchor at `href="/methodology#food-v02-footnote"`.

**UI/UX §23.2 (CI/small-n lines):** Applied. `.content-area__ci-disclosure` and `.content-area__small-n-line` with `var(--color-text-caption)` at `var(--font-size-xs)`. F3-R3-C and F3-R3-D sourced from `consensus_disclosure.ts`.

**UI/UX §23.3 (heatmap exclusion caption):** Applied. `.heatmap-exclusion-caption` rendered below SimilarityHeatmap in ContentArea.tsx. Visible text uses `displayModel()`; aria-label carries full `model_id`. Exclusion detection: `domain.mds_coordinates` key set vs `domain.models` set difference.
