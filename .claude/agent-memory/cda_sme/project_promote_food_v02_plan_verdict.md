---
name: promote-food-v02-plan-verdict
description: 2026-06-11 CDA SME re-affirmation verdict on PROMOTE-FOOD-V02 Architect plan. PASS-WITH-NOTES. Schema shape (override+reason fields, both optional) honors round-3 preference (i). Five byte-identical strings F3-R3-A..E acknowledged. STOP-CONDITION #5 in plan §11 is methodologically MISWORDED: it instructs Coder to read CI from existing `consensus_ci`, but `consensus_ci` is the CI on `consensus_score`, NOT on `romney_eigenratio`. The eigenratio bootstrap CI [4.908, 10.338] referenced in F3-R3-C and F3-R3-E is currently only in the round-3 SME memo, not in the published JSON schema. Issuing P1 binding (add romney_eigenratio_ci field to schema in SAME commit, populate from 4c bootstrap run, seed 20260611 B=500 per memo; OR if recomputation is out of scope for this commit, F3-R3-C and F3-R3-E numerics must be inlined as constants with a same-commit footnote that the value is pre-computed and an FOOD-FIX-A2 carry-forward). P2 advisory on social drafter framing note for post-promotion detect cron.
metadata:
  type: project
---

# PROMOTE-FOOD-V02 Architect plan — CDA SME re-affirmation verdict

## Verdict: PASS-WITH-NOTES

The plan correctly enacts the round-3 PROMOTE-AS-WEAK adjudication: schema shape matches SME preference (i), five F3-R3 strings are flagged for byte-identical shipment, R1-R7 / U1-U6 / T1-T3 checklists carry over verbatim, maverick heatmap drop with disclosure is correctly scoped, FOOD-FIX-A2 is correctly carved out as fast-follow, interim ruling correctly terminated at promotion, drafter framing note correctly preserved.

## Binding (P1) — eigenratio CI surfacing

Plan §11 STOP condition reads: "the CI values must be read from the existing JSON (`consensus_ci`), not recomputed. If `consensus_ci` does not carry [4.91, 10.34] post-publish, that is a separate FOOD-FIX-A2 question and STOPS back to SME."

This is methodologically incorrect. Two distinct bootstrap CIs are conflated:

- `consensus_ci` is the CI on `consensus_score` (round-3 staged: [0.4983, 0.7814]).
- The CI in F3-R3-C and F3-R3-E ([4.91, 10.34]) is the CI on `romney_eigenratio` (round-3 4c orchestrator bootstrap, seed 20260611, B=500).

The staged JSON does NOT carry a `romney_eigenratio_ci` field; the schema does not define one. The eigenratio CI exists only in the round-3 SME memo as an orchestrator-produced sensitivity number.

This must be resolved before the F3-R3-C and F3-R3-E strings can ship truthfully. Two acceptable resolutions; Architect picks:

(a) Add `romney_eigenratio_ci: tuple[float, float] | None` and `romney_eigenratio_ci_n_bootstrap: int | None` and `romney_eigenratio_ci_seed: int | None` to `DomainResult` in the same commit (Architect-signed; co-update DATA_DICTIONARY §6); compute via a single-domain rerun of `bootstrap_eigenratio_distribution` matching the 4c orchestrator run (seed 20260611, B=500); populate the new fields; surface in `food.json`. Lede / footnote read CI from the new field. This is structurally consistent with the Remedy B `centrality_ci` precedent.

(b) Inline the values [4.91, 10.34] as constants in the F3-R3-C and F3-R3-E strings (which the strings already do) AND add a code comment at the constant site naming this verdict + naming round-3 of `project_phase9b_food_guard_trip.md` + naming the seed (20260611) and B (500), AND add the eigenratio-CI-as-schema-field work to FOOD-FIX-A2 scope so it lands in the next minor bump. Under (b) the Coder must NOT compute or display a runtime CI for eigenratio; the strings carry the pre-computed values verbatim. (b) is lower-cost and ships the same user-visible disclosure.

Architect picks. SME preference is (b) for this commit (lower coupling, the values are SME-committed at draft-time per F5 binding) provided the FOOD-FIX-A2 scope adds the schema-field follow-up. Either is methodologically clean.

## Binding (P2) — F3-R3-A through F3-R3-E ship byte-identical

The plan §4 step 5 says "the Coder MUST NOT paraphrase or reformat the string; the test harness asserts byte identity (T2)." Confirmed binding. Reviewer enforces R3.

The U+2014 grep gate is correctly in place (§4 step 14). Add: grep must also cover `templates/lede_v1.py`, `data/results/food/0.2.json` (the override reason field), `ContentArea.tsx`, `MethodologyPage.tsx`, and `SimilarityHeatmap.tsx` heatmap caption.

## Binding (P3) — schema shape honors SME preference (i)

`consensus_type_override: ConsensusType | None = None` and `consensus_type_override_reason: str = ""` both optional, both default-preserving. Correct enactment of round-3 (b)(i). Auto-derived `consensus_type` field stays untouched in the JSON for audit. Published label = `consensus_type_override or consensus_type` is the correct semantic.

Architect sign-off recorded in plan §3 satisfies CLAUDE.md §6 R6. DATA_DICTIONARY co-update in same commit satisfies R7.

## Binding (P4) — Single-commit discipline

Plan correctly bundles schema + DATA_DICTIONARY + staged-JSON update + promote + publish wiring + dashboard surfaces + tests + status trail as one commit. CLAUDE.md §8 single-commit rule satisfied. Out-of-scope items (FOOD-FIX-A2, social drafter edits, DESIGN_SYSTEM bump) correctly carved out.

## Binding (P5) — Maverick heatmap-drop disclosure

Plan §4 step 10 correctly scopes the drop to the similarity heatmap ONLY. Within-model + pooled-term-map surfaces are correctly preserved as live for maverick (Register 1 informant for its own model). Plain-language disclosure naming `meta-llama/llama-4-maverick` and the reason "no single-pass collection records for this domain" matches round-3 R6. UI/UX picks placement per U6.

## Binding (P6) — Methodology footnote co-location

F3-R3-E footnote co-located UNDER existing FOOD-FIX-A footnote (R4). The plan §4 step 9 reads "co-located with the existing FOOD-FIX-A footnote." Correct.

## Advisory (P7) — Social drafter framing note

Round-3 §(e) flagged that the post-promotion detect cron will trigger a CLASSIFICATION_DRIFT event (8-model STRONG -> 12-model WEAK at the same threshold), and the appropriate drafter framing is "with more models in the slate, the published uncertainty band on agreement now crosses the threshold," NOT a triumphant-discovery framing. The plan §6 correctly defers this to the next detect-cron pass through the existing CDA SME pre-trigger drafter-prompt review. No drafter code changes in this commit; correctly out of scope.

## Advisory (P8) — Lede pattern key

Plan §4 step 5 proposes a new pattern key `weak_consensus_with_straddling_ci_food_v02` carrying F3-R3-A verbatim. The `_food_v02` suffix is fine for first instance, but the round-3 forward-carry note explicitly said: "the next domain that crosses a Caulkins typology threshold with a bootstrap CI straddling the boundary inherits the F3-R3 disclosure pattern; the SME does NOT pre-bake this into a template; each disclosure is individually reviewed."

So the pattern key should be domain-scoped (the `_food_v02` suffix is good). When a future domain hits this state, a fresh SME pass produces a fresh string and a fresh pattern key. The Coder must NOT generalize the pattern key to e.g. `weak_consensus_with_straddling_ci` (no domain suffix) because that would invite reuse without per-domain SME review.

## Re-affirmation against round-3 checklist

- (i) Schema shape: PASS (matches preference; Architect picked the auditable override-field option).
- F3-R3-A..E byte-identical: PASS (verbatim shipment binding; em-dash gate; T2 vitest test).
- R1-R7 Reviewer items: PASS (mapped 1:1 to plan §4 acceptance criteria).
- U1-U6 UI/UX items: PASS (deferred to UI/UX gate; placement decisions correctly carved out).
- T1-T3 Tester items: PASS (mapped 1:1 to new test files).
- Maverick heatmap drop: PASS.
- Methodology footnote co-location: PASS.
- FOOD-FIX-A2 carve-out: PASS.
- Drafter framing note carve-out: PASS.

## Required before merge

1. Resolve P1: Architect picks (a) schema-field add OR (b) inline-constants-with-code-comment + FOOD-FIX-A2 scope expansion. SME preference is (b) but either is methodologically clean.
2. Confirm U+2014 grep gate covers ALL files touched, not just the new strings (P2).
3. UI/UX issues U1-U6 placement verdict before Coder dispatch.

## Routing

- Verdict file path: `/opt/lsb-agent/docs/status/2026-06-11-promote-food-v02-cda-sme-verdict.md` (Architect-created).
- Post to `#lsb-cda-sme`.
- On P1 resolution + UI/UX PASS: Coder dispatch.
- On Coder commit: Reviewer R1-R7 + Tester T1-T3.
- No fresh SME pass needed unless any F3-R3-A..E string is edited or P1 resolution diverges from (a)/(b).
