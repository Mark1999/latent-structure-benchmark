---
name: phase6-T13-food-verdict
description: Phase 6 T13 sub-option B (add `food` as third domain) — CDA SME PASS-WITH-NOTES; binding food.yaml prompt_seed REVISED from Architect's proposal; pitfall #13 audit clears all SAFETY_FILTER_MARKERS as no-overlap.
metadata:
  type: project
---

# Phase 6 T13 — food domain CDA SME verdict (2026-05-15)

**Verdict:** PASS-WITH-NOTES at `docs/status/2026-05-15-phase6-T13-cda-sme-verdict.md`.

## Binding B-D2 finalization

`data/domains/v1/food.yaml` (binding, byte-exact):

```yaml
slug: food
version: v1
display_name: Food
prompt_seed: "type of food or dish"
truncation_k: 50
```

**`prompt_seed` REVISED from Architect's proposal.** Architect proposed
`"type of food, dish, or meal"`; I overrode to `"type of food or dish"`.

**Why:** the free-list template wraps `prompt_seed` as "exhaustive list
of {prompt_seed}". The original three-term disjunction mixed two
semantic levels — "food/dish" is item-level ("rice", "pasta"); "meal" is
event-level ("breakfast", "Sunday dinner") — which pollutes the
free-list with event-words and item-words and noisifies pile-sort.
Two-term "food or dish" preserves categorical tightness and parallels
family's two-term anchor ("relationship or member").

**How to apply:** if a future task proposes editing food.yaml's
prompt_seed, do not re-litigate — refer to this verdict. If a v2_softN
variant is proposed for food, the same categorical-tightness
constraint applies (no event-level cues in the seed).

## Pitfall #13 audit conclusion (binding)

**No overlap.** Current `SAFETY_FILTER_MARKERS` (defined in
`scripts/run_decline_backfill.py:102`) is safe to reuse for food
without modification. Architectural reason: markers apply only to
`error_message` in `should_include_failure()` (input classification),
not to free-list/pile-sort/pile-interview output verbatims. Detector
role boundary established 2026-04-23 is preserved. No per-domain
bypass list, no follow-up task required.

**Why:** the originating pitfall #13 ruling was about reuse across
the input↔output classification boundary; the food domain free-list
output does not flow through either classifier — it flows through
cdb_analyze. Food vocabulary like "kill"/"butcher"/"prohibited" can
appear in `response_verbatim` of successful free-lists, but those
strings are never tested against SAFETY_FILTER_MARKERS.

**How to apply:** if future food collection produces an unexpected
mis-classification, that observation triggers narrow CDA SME review
per the originating ruling, not a pre-emptive code change. Posture
is "fix when observed, not when speculated."

## Small-n posture

n=9 trips `romney_small_n_warning: true` per n<15 threshold
([[romney-small-n-threshold]]). No additional small-n-specific lede
language required — CI bounds on Smith's S in the existing template
set are the operational uncertainty surface. Adding small-n hedge
language only for food would create asymmetric framing across the
three v1 domains (family at n=11 and holidays at n=9 don't carry it).

## AC10 pre-clearance posture

All eight `lede_v1.py` pattern keys substitute "food" cleanly and
§1.5-compliantly. AC10 verbatim review (after Coder runs
`cdb_publish/build.py`) reduces to: (1) confirm pattern key is one of
the eight known; (2) confirm numeric substitutions are sane. No
structural template review needed.

## Carry-forward to T1/T2/Phase 6.5 (downstream-tracked, not T13 blockers)

- Methodology page should note all three v1 domains operate at n<15;
  surface via Smith's S CI width, not a categorical small-n label.
- The `subcultural` lede phrase "different region of cognitive space"
  refers to MDS coordinate space, not model cognition; methodology
  page should cross-reference so cold readers don't misread.

[[detector-role-change-gate]] [[romney-small-n-threshold]] [[failures-are-findings]]
