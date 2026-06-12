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

---

## 8. FOOD-V02-FIX-SIMIDS fix trail (2026-06-11)

**Task ID:** FOOD-V02-FIX-SIMIDS

**Trigger:** After PROMOTE-FOOD-V02 (commit 2d5bca0), two vitest assertions in `DomainResultPublished.shape.test.ts` correctly failed for food because they asserted the legacy invariant `matrix.length == models.length` (13 models but 12x12 matrix). No published field declared the matrix row/column order, so open-data consumers could not reconstruct the index mapping.

**Fix summary:** Added `similarity_model_ids: list[str] = []` to `DomainResult` in `cdb_core/schemas.py`. Populated from `list(sim_model_ids)` at the `return DomainResult(...)` site in `pipeline.py`. Injected the field into `data/results/food/0.2.json` (value = 12 sorted single_pass model IDs). Regenerated `apps/dashboard/public/data/food.json` and `food.v0.2.json` via `cdb_publish.build`. Threaded the prop through `SimilarityHeatmap` and `ContentArea.tsx`. Rewrote the two failing shape test assertions to the new gated invariant. Updated heatmap R10 test food render to pass `similarityModelIds`. DATA_DICTIONARY.md updated v0.1.27 to v0.1.28 in the same commit.

**No semantic change to the food finding.** The matrix values, centrality scores, eigenratio, consensus_type_override, and lede are unchanged. Family and holidays retain the empty-default legacy invariant.

**JSON-diff for data/results/food/0.2.json vs HEAD:**
- New field: `similarity_model_ids` = `["claude-opus-4-5", "claude-opus-4-6", "claude-sonnet-4-6", "deepseek/deepseek-v3.2", "google/gemini-2.5-flash", "google/gemini-2.5-pro", "mistralai/mistral-large-2512", "mistralai/mistral-small-2603", "openai/gpt-5.2", "openai/gpt-5.4", "openai/gpt-5.4-mini", "x-ai/grok-4"]` (12 elements, sorted alphabetically, matches mds_coordinates.keys())
- No other field changed. generated_at, generated_lede, similarity_matrix, similarity_ci, mds_coordinates, cultural_centrality_scores, models are byte-identical to the HEAD version.

**JSON-diff for apps/dashboard/public/data/food.json vs HEAD:**
- Same as above: only `similarity_model_ids` added. generated_at and generated_lede unchanged.

**One commit per §8 exception** (schema + DATA_DICTIONARY co-update). Family and holidays results untouched on disk. Legacy fallback branch in the new vitest invariant keeps them green.

---

## 9. FOOD-V02-FIX-SIMIDS gate trail

| Stage | Status | File / Reference |
|---|---|---|
| UI/UX | PASS (pixel-identity invariant confirmed) | `docs/status/2026-06-11-food-v02-fix-simids-uiux-verdict.md` |
| Coder | COMPLETE | FOOD-V02-FIX-SIMIDS commit (cherry-picked from worktree-wf_fe2a2da4-51a-4) |
| Reviewer | PENDING | |

---

## Promotion complete and live-verified (2026-06-11 evening)

Food v0.2 is LIVE. Step-5 verification on cogstructurelab.com (Playwright, real DOM):
- Lede renders F3-R3-A verbatim ("...the uncertainty band crosses it. The honest read...").
- CI disclosure (F3-R3-C, "[4.91, 10.34]") and small-n line (F3-R3-D, "below the 15-model floor") present without interaction.
- Weak-consensus labeling present; consensus_type_override=WEAK_CONSENSUS in the served food.json with the auditable reason; auto-derived STRONG preserved.
- Model Map: 12 models, 11 ellipses + 1 dashed R1-b (gpt-5.4-mini) = all points uncertainty-treated; all four new models (deepseek-v3.2, gemini-2.5-pro, mistral-large-2512, grok-4) render.
- Similarity heatmap: 12x12, maverick absent with the named disclosure in both caption and aria ("...no single-pass collection records for this domain").
- similarity_model_ids (12 entries) in the served JSON: the matrix order is now an explicit open-data contract.
- Screenshot: screenshots/food-v02-live.png (local).

Campaign fast-follows queued: FOOD-FIX-A2 (eigenratio canonicalization + eigenratio-CI schema field), collector bug batch (skip-collected semantics, campaign_id regression, http_error failure records, lsb_inspect field read), runbook step-2 mode correction. Social announcement awaits Mark in the admin console under the SME's binding framing.

---

## COLLECTOR-BUGS fix trail (2026-06-12)

**Task ID:** COLLECTOR-BUGS
**Status:** COMPLETE (one commit, pending Reviewer + Tester verdicts)

### BUG 1: --skip-collected domain-aware scoping

**Root cause:** `_load_collected_model_ids()` returned `set[str]` (model_id only), so any model with a record for any domain was skipped for all domains. The early skip guard in main() also fired before the cross_model branch, making `--skip-collected --mode cross_model` a no-op.

**Fix:** Added `_load_collected_model_domain_pairs()` returning `set[tuple[str, str]]` (model_id, domain_slug). The 2-tuple key is used per CDA SME advisory D1: AC7 encodes the cross-mode collision semantic (any record for a domain satisfies the skip, regardless of collection_mode), so the simpler 2-tuple is correct and the 3-tuple would contradict AC7. The early single-model skip guard moved inside the `else` branch (single-model modes only). The cross_model branch uses the domain-aware set keyed on `(ref.model_id, args.domain)`. `_load_collected_model_ids()` is retained for `--list-models` display (model-only status column).

### BUG 2: --campaign-id threading

**Root cause:** `run_two_pass`, `run_cross_model_sort`, `run_baseline_sort` did not accept `campaign_id`, so records written via those paths never received the `campaign_id=<value>` tag in `qa_notes`. The CLI only threaded `args.campaign_id` to the `single_pass` dispatch site.

**Fix:** All three runner functions gain `campaign_id: str | None = None` kwarg and pass it to every `_assemble_record(...)` call within their body. `collect_two_pass`, `collect_cross_model`, and `collect_baseline` in scripts/collect.py gain the same kwarg and pass it to the runner. All four dispatch sites in `main()` now pass `args.campaign_id`. Help text restriction "Applies only to --mode single_pass" replaced with "Applies to all collection modes." No backfill of historical records (fix-forward per CLAUDE.md §9 pitfall 10).

### BUG 3: transport-failure records at the per-model boundary

**Root cause:** The existing `collect_cross_model` `except Exception` handler already called `append_failure(...)`, so failure records did land. The defects were: (a) the `context` dict lacked `failure_scope`, making model-level transport events indistinguishable from per-step failures, and (b) the log message used language that could imply model behavior attribution.

**Fix:** Added `"failure_scope": "per_model"` to the context dict in the `collect_cross_model` `except Exception` handler (CDA SME C2: preferred key name over `model_level=True`). Updated the logger.exception call to "The adapter raised an exception during cross-model sort for %s" (CDA SME C1: no model-attribution language). No new categorical fields; no cdb_core schema changes; the `http_error` enum in `DeclineInterview.originating_outcome_class` is unchanged.

LSB's detection, `scripts/collect.py`'s per-model boundary handler, records the provider-transport event in `data/raw/failures.jsonl`. The failure record captures what LSB's detection observed (the adapter raised). The model output did not arrive; no `response_verbatim` is written (CDA SME C4). This record is a provider-transport event, not a model output event, and does not belong in any downstream decline-interview pipeline that classifies model outputs (CDA SME C3 four-noun sentence: LSB's detection of a provider-transport event does not constitute a model output classification for the decline-interview pipeline).

### VERIFICATION 4: lsb_inspect.py field reads

**Disposition: not-a-bug.** `scripts/lsb_inspect.py` L120-121 reads `freelist.parsed_items` and `pile_sort.parsed_piles` correctly using `fl.get("parsed_items")` and `ps.get("parsed_piles")`. Cross-model records carry a placeholder freelist with `parsed_items=[]`, so `fl=0` accurately reflects the placeholder semantic, not a misread of a legacy field. No code change required.

### Files changed

- `scripts/collect.py`: BUG 1 (new `_load_collected_model_domain_pairs`, domain-aware skip guards), BUG 2 (campaign_id kwarg on collect_two_pass / collect_cross_model / collect_baseline, all four dispatch sites, help text), BUG 3 (failure_scope context key, attribution-clean log message)
- `packages/cdb_collect/cdb_collect/runner.py`: BUG 2 (campaign_id kwarg on run_two_pass / run_cross_model_sort / run_baseline_sort, threaded to all _assemble_record calls)
- `tests/unit/test_collect_skip_collected.py`: new; 10 fixture-based tests for BUG 1
- `tests/unit/test_collect_campaign_id.py`: new; 6 fixture-based tests for BUG 2
- `tests/unit/test_collect_failure_record.py`: new; 3 fixture-based tests for BUG 3
- `docs/status/2026-06-11-phase9b-food-campaign.md`: this section appended

---

## Cross-domain CI verification (Mark's request, 2026-06-12)

Same model-resample bootstrap (B=500, seed 20260612) applied read-only to the published family and holidays matrices:
- family (15 models): eigenratio 19.143, CI95 [9.612, 23.504]. Does not cross 5.0. STRONG stands, uncertainty-honest.
- holidays (14 models): eigenratio 39.283, CI95 [15.610, 47.387]. Does not cross 5.0. STRONG stands, uncertainty-honest.
- food (12 models, for comparison): 9.481, CI95 [4.908, 10.338]. Crosses. Published WEAK with disclosure.

Conclusion: food's indeterminacy is domain-specific, not method-induced. Publishing the family/holidays CI values on the dashboard is deferred to their next natural re-baseline once FOOD-FIX-A2 lands the romney_eigenratio_ci schema field (option: extend A2 scope to backfill all domains' CIs from their published matrices; Architect's call at A2 planning).
