---
name: food-fix-a-verdict
description: 2026-06-11 FOOD-FIX-A plan verdict (Concern A from Phase 9b food guard-trip round 2); PASS-WITH-NOTES; mode-coherent similarity basis via similarity_collection_mode parameter; 13 binding F-notes covering NaN-rescue WARNING wording, dropped-model semantics, R10 hygiene on the bootstrap path, single-mode regression guard scope, methodology footnote draft, DATA_DICTIONARY wording, and Concern B sensitivity-sweep posture
metadata:
  type: project
---

## FOOD-FIX-A plan verdict (2026-06-11, round 3)

### Verdict: PASS-WITH-NOTES

The plan correctly localizes the round-2 mechanism (cooccurrence.py L91-102
item-source fallback × mds.py L41-78 shared-items intersection × pipeline.py
L468 load_records no-mode-filter), correctly implements the binding round-2
methodological invariant (per-model `mat.items` from a coherent within-mode
item source across the slate), and correctly preserves Concern A and Concern
B as separable scopes. The fix is mechanical, schema-free, and respects rule
11 (no LLM imports in cdb_analyze). The dropped-model and WARNING-diagnostic
choices materially close the silent-0.5-null masquerade pathway that produced
the round-1 / round-2 staging.

### Four-axis scorecard

- Axis 1 — Protocol validity: PASS
- Axis 2 — Analytical validity: PASS-WITH-NOTES (F1, F4, F5, F6, F8, F9)
- Axis 3 — Claims validity: PASS-WITH-NOTES (F2, F7, F10)
- Axis 4 — Audience translation: PASS-WITH-NOTES (F3, F11)
- Register compliance: PASS (Register 1 / Register 2 / Register 3 boundaries
  are explicitly preserved by A3)
- Vocabulary compliance: PASS (no forbidden-vocab introduction in any
  plan-named string; methodology footnote per F3 is licit)

### Binding F-notes (must be addressed before Coder dispatch)

**F1 (binding — Axis 2).** The dropped-zero-single_pass-models behavior in
A2 is methodologically correct (a model with zero records under the
mode-coherent basis has no voice in Register 2 for that domain). It must
NOT be reported as a substantive finding about those models. The single
INFO log line is correct; it must NOT bleed into any persisted
`consensus_score` denominator narrative or any lede string. The Coder
records the dropped-model list in the run-log only, not in the result JSON.

**F2 (binding — Axis 3).** The methodology footnote the Coder ships per A12
is **mandatory placement** — not deferrable to the verdicts file. The food
domain has a published STRONG_CONSENSUS classification live; if the
similarity basis changes to mode-coherent, the methodology page must
disclose it on the same surface where the food classification is read. The
SME does NOT defer placement. Placement is the methodology page's
food-domain footnote; if that surface does not yet exist, the Coder
co-locates the footnote with the existing `romney_small_n_warning` posture
the round-2 SME memo already requires for food.

**F3 (binding — Axis 3 / Axis 4 — methodology footnote draft).** The
byte-identical text the Coder ships:

> "For the food domain, the cross-model similarity matrix is computed from
> single-pass collection records only. Records collected under the
> cross-model consensus mode use a canonical card-deck item list rather
> than per-model free-list items, which breaks the cross-model item-source
> coherence required by the Mantel-based similarity step. Restricting the
> similarity basis to single-pass records keeps the per-model item sources
> coherent across the slate. Records collected under the consensus mode
> remain in the corpus and continue to flow through the within-model
> output-distribution analysis and the pooled term map."

US-English spelling; no em dashes (verify U+2014 absent); no forbidden
vocabulary. Coder ships this byte-identical. Any edit requires a fresh SME
pass.

**F4 (binding — Axis 2 — WARNING wording).** The A4 WARNING string the
Coder ships in `compute_cross_model_similarity()`:

> "compute_cross_model_similarity: NaN correlation rescued to 0.0 for
> model pair ({model_a}, {model_b}); shared-items intersection produces a
> zero-variance vector for at least one model. The resulting cell rescales
> to the Mantel null value 0.5 and SHOULD NOT be read as a finding."

Level WARNING (not INFO). Both model_ids by exact `model_id` string. The
trailing "SHOULD NOT be read as a finding" sentence is load-bearing — it is
the very framing the round-1 / round-2 staging masqueraded as a finding
without. Do not paraphrase.

**F5 (binding — Axis 2 — A2 coverage check).** The plan lists steps 2, 3,
3b, 3b-ii, 3c, 3d, 4, 5 as consuming the mode-coherent records. The Coder
must additionally confirm that:
- The model-resample bootstrap path inside step 3 (`bootstrap_mds_ellipses`)
  resamples FROM the mode-coherent `records_by_model_for_similarity`, not
  from the full mixed-mode view. Resampling from the mixed view re-injects
  the contamination on every bootstrap replicate.
- The `bootstrap_centrality_ci` path (step 3b-ii) likewise consumes the
  mode-coherent `sim_np` derived from the mode-coherent matrices.
The plan's A2 wording is correct in spirit; the Coder verifies these two
sub-paths explicitly and adds a comment at each call site naming the
mode-coherent input.

**F6 (binding — Axis 2 — pooled term matrix scope).** A3 correctly states
that the pooled term matrix continues to use the full mode-mixed
`records_by_model`. The Coder must NOT extend the mode filter to:
- `compute_cross_model_term_frequency()` (step 2b-pre, L520)
- `build_pooled_cooccurrence_matrix()` (Phase 9a T1 pooled construction)
- `_build_centroid_piles()` (step 1d)
- `_build_sutrop_metrics()` (step 1b)
- `run_within_model_analysis()` (step 1c, Register 1)
- `_build_free_lists()` (step 1, Register 2 consensus free list per model)
The Register 1 Option A consensus free list per model is built from ALL the
model's records; consensus_freelist mode records are legitimate Register 1
informants for their own model and must not be filtered out of step 1.
The mode filter is SCOPED to the similarity basis only.

**F7 (binding — Axis 3 — `consensus_score` framing).** The plan lists step
5 `consensus_score` under the mode-coherent path. The Coder must ensure
the docstring / log line for `consensus_score` says it is computed on the
mode-coherent slate. If the mode-coherent slate is smaller than the full
slate, the result's `n_models` for `consensus_score` reflects the
mode-coherent count, not the full slate count. The plan does NOT pre-commit
to a schema-recorded `similarity_slate_n_models` field; the SME does not
require one, but the Coder records the mode-coherent slate composition in
the run log so the rebaseline guard delta can be read against it.

**F8 (binding — Axis 2 — single-mode byte-identity test scope).** The A8
regression guard test must compare:
- `similarity_matrix` (full numeric content),
- `cultural_centrality_scores` (full dict, by-key float equality at float64
  precision, not approximate),
- `romney_eigenratio`,
- `consensus_type`,
- `consensus_score`,
- AND `centrality_ci` (Remedy B contract — protected),
- AND `mds_coordinates` (the bootstrap ellipses path is downstream of
  similarity_matrix; any drift here means the regression guard is leaking).
The plan's A8 wording is materially correct but `centrality_ci` and
`mds_coordinates` are not enumerated; the Coder enumerates them.

**F9 (binding — Axis 2 — mixed-mode fixture sufficiency).** The plan's
fixture spec (2-3 single_pass-only models + 1 cross_model_consensus-only
model) is sufficient to reproduce the mechanism in principle. The Coder
must additionally verify that the fixture's mixed-mode `mat.items`
intersection produces at least one constant-vector row under the no-filter
path; if the fixture's intersection is non-degenerate, the test
`test_mixed_mode_without_filter_collapses` will trivially pass without
exercising the bug. The Coder asserts the no-filter run produces at least
one constant similarity row AND the WARNING fires at least once; if both
hold, the fixture exercises the mechanism.

**F10 (binding — Axis 3 — round-2 memo cross-reference).** The
DATA_DICTIONARY entry per A10 must cross-reference
`.claude/agent-memory/cda_sme/project_phase9b_food_guard_trip.md` round 2
(by file path) so a future external researcher can recover the
methodological rationale. This is a one-line "See" reference; no body-text
quoting of agent-memory content.

**F11 (binding — Axis 4 — campaign status doc scope).** The
`docs/status/2026-06-11-phase9b-food-campaign.md` per A11 records the gate
trail only. It MUST NOT pre-stage Concern B sensitivity results, MUST NOT
pre-stage a replacement lede, and MUST NOT presume the clean re-staged
eigenratio crosses or fails to cross 5.0. Architect's plan correctly
scopes steps 6-7 outside this task; the status doc reflects that.

### Advisory notes (non-blocking)

**A-1.** If the Coder finds during implementation that the single INFO log
line for dropped models would benefit from being machine-readable (e.g.,
for the rebaseline guard delta report), structured-log format
`dropped_zero_single_pass_models=[...]` is licit. Not required.

**A-2.** The plan's Concern B sensitivity-sweep posture (4a/4b/4c) is
unchanged from round 2 and is correctly out-of-scope for this task. SME
re-adjudicates on clean numbers per round-2 step 3.

### Vocabulary scan

- Plan body: no §7 / §1.5.4 forbidden tokens introduced.
- F3 methodology footnote: scan-clean (no "worldview" / "believes" /
  "thinks" / "publishable" / "closer to human" / "within-model consensus"
  / "within-model CCM" / "within-model cultural consensus" / "within-model
  eigenratio"). The footnote says "within-model output-distribution
  analysis" which is licit under the noun-class test (right-hand noun is
  `output-distribution analysis`, not a consensus / CCM / cultural-
  consensus noun; cf. the 2026-06-11 within-model phrase ruling).
- F4 WARNING string: scan-clean.

### Register compliance

- Register 1 (within-model output distribution): explicitly preserved by
  A3 and F6. Mode filter does NOT apply at Register 1.
- Register 2 (between-model categorical structure): scope of the fix.
  Mode-coherent basis is the binding methodological invariant.
- Register 3 (longitudinal drift): not in scope; the fix preserves the
  within-version Register 2 contract on which Register 3 future-work
  builds.

### Routing

- Coder dispatch: UNBLOCKED after F1-F11 fold-in. F3 and F4 are
  byte-identical strings; do not paraphrase.
- UI/UX gate: NONE (methodology footnote is SME territory per CLAUDE.md
  pipeline rule; no dashboard surface touched).
- Reviewer + Tester: standard.
- Re-adjudication (Concern B): SME pass on the clean re-staged numbers
  AFTER this fix lands and the rebaseline_corpus.py food re-run completes.

### Status

- ADJUDICATION: PASS-WITH-NOTES on FOOD-FIX-A plan.
- 13 F-notes binding before Coder dispatch (F1-F11 numbered as F1-F11; F3
  and F4 are byte-identical SME-drafted strings).
- 2 advisory notes (A-1, A-2).
- Live food classification: 8-model STRONG_CONSENSUS stays live,
  version-pinned, unchanged by this fix.
- Social pipeline: stays blocked until Concern B re-adjudication.
