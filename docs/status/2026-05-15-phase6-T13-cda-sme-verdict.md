---
filed: 2026-05-15
reviewer: CDA SME agent (Opus)
task: Phase 6 T13 — add `food` as third domain (sub-option B)
plan_reviewed: docs/status/2026-05-15-phase6-T13-architect-plan.md
slack_channel: "#lsb-cda-sme"
verdict: PASS-WITH-NOTES
---

# CDA SME verdict — Phase 6 T13 (sub-option B: add `food`)

## VERDICT: PASS-WITH-NOTES

The plan is methodologically sound under sub-option B. The Architect's
`prompt_seed` proposal is **revised** to a tighter two-term categorical
anchor (binding decision B-D2 below). Pitfall #13 audit finds **no
cross-boundary detector reuse risk** at the food vocabulary level. The
9-model slate trips `romney_small_n_warning` (n<15) but the Romney CCM
small-n caveat is already operational in the lede pipeline via CI
bounds — no additional small-n framing language is required. Lede
template substitution reviewed across all eight pattern keys with
"food" as the slug; all read coherently and §1.5-compliant.

The notes are downstream-tracked (no plan changes required before
Coder dispatch).

## Four-axis scorecard

| Axis | Verdict | One-sentence rationale |
|---|---|---|
| 1. Protocol validity | PASS | Free-list elicitation protocol unchanged; the revised `prompt_seed` is a valid categorical anchor parallel to family. |
| 2. Analytical validity | PASS-WITH-NOTES | n=9 trips `romney_small_n_warning` per the n<15 threshold; this is methodologically tractable and already surfaced by the existing pipeline; small-n posture is acceptable for an extensibility-proof shipment. |
| 3. Claims validity | PASS | All eight `lede_v1.py` pattern strings substitute "food" cleanly without violating §1.5.4 forbidden vocabulary or descriptive-locational framing. |
| 4. Audience translation | PASS-WITH-NOTES | The auto-generated food lede will be readable by a cold journalist; pre-publication verbatim review at AC10 remains the binding final check before Coder commit. |

## Binding decisions (B-D2 finalization)

The following are **binding** for `data/domains/v1/food.yaml`. The
Coder writes these verbatim; no further CDA SME review of the YAML
content is required.

### Final `food.yaml` contents (binding)

```yaml
slug: food
version: v1
display_name: Food
prompt_seed: "type of food or dish"
truncation_k: 50
```

### Rationale for each field

**`slug: food`** — already enumerated in `docs/DATA_DICTIONARY.md`
§1.1 as a v1 domain; matches `App.tsx` line 78 `FUTURE_DOMAINS` entry.

**`version: v1`** — matches family/holidays.

**`display_name: Food`** — confirms Architect's B-D2 proposal. One
word, sentence-case, matches the conventions of "Family Terms" and
"Holidays". (Considered "Foods" — rejected because the field is a
domain label, not a plural noun; family is "Family Terms" not
"Families", and holidays' plural is incidental, not categorical.)

**`prompt_seed: "type of food or dish"`** — **REVISED** from the
Architect's proposal of `"type of food, dish, or meal"`.

Reasoning for the revision:

1. **Categorical tightness.** The free-list template wraps the seed
   as "exhaustive list of {prompt_seed}". Family's wrapping produces
   "exhaustive list of type of family relationship or family member"
   — a two-way disjunction within one semantic level (people-in-the-
   family). Holidays' produces "exhaustive list of holiday, festive
   day, or religious observance" — three-way but all at the same
   semantic level (calendrical observances). The Architect's
   `"type of food, dish, or meal"` produces "exhaustive list of
   type of food, dish, or meal" — three-way but **across two
   semantic levels**: "food/dish" is an item-level cue ("rice",
   "pasta", "kimchi"), and "meal" is an event-level cue
   ("breakfast", "brunch", "Sunday dinner"). Mixing levels in the
   seed pollutes the resulting free-list with event-words and
   item-words, which then mis-cluster in pile-sort.

2. **Two-term disjunction is sufficient.** `"food or dish"` covers
   the breadth: "food" is the generic categorical superordinate
   (e.g., "bread", "fruit"); "dish" cues prepared/composite items
   (e.g., "stir-fry", "casserole"). Together they span the
   item-level free-list space without inviting meal-event responses.

3. **"Type of" framing retained.** Matches the family pattern and
   anchors the response to category-members, not specific named
   instances. Without "type of", "food or dish" risks recipe
   verbatims or brand-name lists.

4. **No culturally-loaded specificity.** "Food or dish" is
   provider-neutral; it does not bias toward Western or non-Western
   response patterns. ("Cuisine" was considered and rejected as
   too abstract — it cues regional traditions rather than items.)

5. **Recipe-verbatim risk minimized.** The Architect plan §10 risk
   #2 flags the possibility that food prompts produce recipe
   verbatims that resemble decline-interview output. "Type of food
   or dish" is a categorical cue, not a how-to cue; this minimizes
   the risk of recipe-style responses landing in the free-list step.

**`truncation_k: 50`** — confirms Architect's B-D2 proposal. Matches
both shipped domains (family k=50, holidays k=50). At k=50, Smith's
S and Sutrop CSI denominators are consistent across domains, so
cross-domain comparison on the methodology page remains defensible.
No domain-specific reason to deviate.

**No `description` field.** The `Domain` schema in
`packages/cdb_core/cdb_core/schemas.py` lines 79–85 has exactly five
required fields (`slug`, `version`, `display_name`, `prompt_seed`,
`truncation_k`). Adding a `description` field would trigger a schema
change and a `DATA_DICTIONARY.md` co-update — out of scope for T13
per plan §7. Not added.

## Pitfall #13 audit (cross-boundary detector reuse)

**Architectural fact established first.** `SAFETY_FILTER_MARKERS`
(defined in `scripts/run_decline_backfill.py` line 102) is applied
**only** to `error_message` strings inside `should_include_failure()`
(line 237). It is **not** applied to free-list, pile-sort, or
pile-interview output verbatims from the food domain. Those flow
through `cdb_analyze` (Smith's S, Sutrop CSI, pile-sort clustering),
not through the failure-classification or decline-detection paths.

The originating pitfall #13 ruling
(`docs/status/2026-04-23-phase4a1-t3b-detector-cda-sme-verdict.md`)
was specifically about reusing `SAFETY_FILTER_MARKERS` (input
classification, error_message text) inside `_is_recursive_decline()`
(output classification, response_verbatim text). The detector roles
were corrected: output classification of decline-interview responses
now uses `RECURSIVE_DECLINE_PHRASES` (line 148), a separate first-
person-refusal-locution allowlist. **No reuse of safety markers
across the input↔output boundary exists in current code.**

The question for the food domain is therefore narrow: when food-
domain collection produces a failure record (provider safety block,
HTTP error, parse exhaustion), does the food-domain vocabulary
plausibly appear in `error_message` such that a marker substring
would mis-classify the failure?

### Marker-by-marker audit

| Marker | Could appear in a provider error_message for food? | Mis-trigger risk |
|---|---|---|
| `safety` | Only if the provider names a "safety filter" event. Food-prep verbs like "kill"/"butcher"/"slaughter" do not appear in error_messages (they would appear in `response_verbatim` of a successful free-list, not in an error). | No. |
| `content policy` / `content_policy` | Standard provider refusal-event marker; food vocabulary does not generate this. | No. |
| `blocked` | Standard provider marker; food vocabulary does not naturally produce this in error text. | No. |
| `harmful` | Could appear if a model refuses to list (e.g.) ingredients of a controlled substance. If so, the classification "safety_filter" is **correct** behavior, not a false positive. | No (intended-behavior boundary). |
| `prohibited` | Could appear in religious-food contexts ("prohibited foods" in halal/kosher discussions). However, these phrases appear in **successful free-list output**, not in **error_messages**. Error_messages carrying "prohibited" are provider refusal events. | No (boundary preserved). |
| `policy_violation` / `content_filter` | Standard provider markers; no food collision. | No. |
| `jailbreak` | Standard refusal-vocabulary marker; no food collision. | No. |
| `RECITATION` / `SAFETY` / `PROHIBITED_CONTENT` | Gemini finish_reason values; structural, not free-text. No food collision. | No. |
| `OTHER` | Gemini's generic content-block finish_reason. Documented false-positive risk noted at marker definition (lines 115–121); food domain does not increase that risk. | Unchanged from prior audit. |

### Food-vocabulary risk vector walkthrough (specific to your ask)

- **Food-prep verbs** ("kill", "butcher", "slaughter", "skin", "gut",
  "carve", "bleed"): appear only in `response_verbatim` of successful
  free-list runs, never in `error_message`. Not classified by
  `SAFETY_FILTER_MARKERS`. No mis-trigger.

- **Animal-product specifics** ("blood sausage", "tripe", "offal",
  etc.): same as above — appear in response text, not error text.
  Not classified.

- **Cultural-specific items** ("halal", "kosher", "haram", ritual-
  slaughter terms): the words themselves do not match any
  `SAFETY_FILTER_MARKERS` substring. No mis-trigger.

- **Drinks/alcohol** ("wine", "beer", "spirits", "alcohol"): no
  substring match against any marker. No mis-trigger.

- **Regional/political foods**: vocabulary itself does not collide
  with markers. If a model refuses to list (e.g.) a politically
  contentious food, the refusal will land in `response_verbatim`
  with a recursive-decline phrase, and the existing
  `_is_recursive_decline()` allowlist (RECURSIVE_DECLINE_PHRASES)
  classifies it correctly.

### Pitfall #13 conclusion

**No overlap.** Current `SAFETY_FILTER_MARKERS` is safe to reuse for
the food domain without modification. **No per-domain bypass list
required. No follow-up task required.** The detector role boundary
established in the 2026-04-23 amendment is preserved: input-
classification (failures) uses safety markers; output-classification
(decline-interview responses) uses `RECURSIVE_DECLINE_PHRASES`.
Neither list is being extended across roles by the food domain.

If any food-domain failure record produces an unexpected
mis-classification during collection, that observation triggers
narrow CDA SME review per the originating ruling — not a pre-
emptive code change. The pitfall #13 posture is "fix when
observed, not when speculated."

## Lede template substitution review (all eight pattern keys)

I read `packages/cdb_publish/cdb_publish/templates/lede_v1.py` and
mentally substituted `{domain}` → `"food"` in every pattern. Each is
§1.5.4-compliant and reads coherently in US English.

| Pattern key | Rendered with "food" | §1.5 verdict |
|---|---|---|
| `strong_consensus_homogeneous` | "Across {n} frontier models, food vocabulary is organized around a single shared categorical structure (Smith's S = ..., 95% CI ...). The map below shows where each model sits relative to that consensus -- and which models diverge from it." | PASS |
| `strong_consensus_with_low_oci` | "Across {n} frontier models, food vocabulary is organized around a shared categorical structure ... {n_low_oci} of these {n} models produced low output concentration on this domain ..." | PASS |
| `strong_consensus_majority_low_oci` | "Across {n} frontier models, food vocabulary is organized around a shared categorical structure ... but a majority of these models produced low output concentration on this domain ..." | PASS |
| `weak_consensus` | "Across {n} frontier models, food vocabulary shows partial categorical agreement ... The map below shows the points of agreement and the specific divergences." | PASS |
| `subcultural` | "Across {n} frontier models, food vocabulary organizes into multiple distinct categorical sub-structures ... One or more models show negative centrality, locating them in a different region of cognitive space than the majority." | PASS — "different region of cognitive space" remains the operational corpus-lens framing; "cognitive space" here refers to the MDS coordinate space, not model cognition (§1.5 compliant as a coordinate-space term of art). |
| `turbulent` | "Across {n} frontier models, food vocabulary does not organize around a shared categorical structure ... The map below shows how each model's output distribution organizes the same terms differently." | PASS |
| `contested` | "Across {n} frontier models, food vocabulary shows active categorical divergence ... some models organize the terms in a way that diverges from the rest." | PASS |
| `all_deterministic` | (No `{domain}` placeholder — unchanged.) | PASS by inheritance. |

**No concerns to flag at the template level.** The "food vocabulary
is organized around..." construction matches the descriptive-
locational frame (Q3 binding) and avoids anthropomorphic verbs.

**Note for downstream:** the `subcultural` rendering says "different
region of cognitive space" — this is established term-of-art for the
MDS coordinate space at the lede surface and was approved at the
Phase 5/6 lede-template review. It is **not** a §1.5.4 violation
because "cognitive space" here is the MDS embedding, not a claim
about model cognition. No edit required.

## Small-n posture (n=9 models)

**`romney_small_n_warning` flips True** at n=9 per the n<15
threshold (memory: `project_romney_small_n_threshold.md`, reconciled
2026-04-23). This is methodologically tractable for an extensibility-
proof publication:

1. **The flag is already operational.** The current `family.json`
   carries `romney_small_n_warning: true` at n=11; `holidays.json`
   carries it at n=9. The food domain at n=9 inherits the existing
   surface treatment without code changes.

2. **Uncertainty is already exposed at the lede.** All consensus-
   pattern lede strings carry Smith's S with bootstrap 95% CI
   (`[{lo}, {hi}]`). The CI width is the small-n indicator at the
   lede surface; readers see uncertainty bounds, not a point claim.

3. **Romney CCM (Register 2) caveats apply.** The Register 2
   consensus interpretation should accommodate the small-n posture
   per the ARCHITECTURE.md §4.2.0 methods adaptation table. The
   methodology page is the binding surface for that framing; no
   per-domain lede edit needed.

4. **No additional small-n-specific lede language is required.**
   The existing CI-bounds framing is the correct uncertainty
   surface for an n=9 publication. Adding "small-n" hedge language
   to the food lede only would create asymmetric framing across
   the three domains (family/holidays don't have such language) —
   methodologically incoherent.

**Suggested language for the methodology page** (downstream-tracked,
not blocking T13): the methodology page should carry a single
sentence noting that all three v1 domains operate at n<15 models
and that this trips the Romney small-n warning, which is surfaced
via CI width on Smith's S rather than via a categorical "small-n"
label. This is a T1/T2 methodology-page concern, not a T13 blocker.

## Pre-publication review hook (AC10)

I confirm I will perform the binding AC10 verbatim review of the
rendered food lede. The Coder runs `cdb_publish/build.py` once after
collection + analyze; the resulting `food.json` carries the lede
text in `key_finding.generated_lede`. The Coder appends that string
verbatim to the Coder's commit-precursor verdict file, and I review
once before final commit.

**Pre-clearance posture for AC10:** all eight pattern keys are
§1.5-compliant at the template level (audit table above), so my
AC10 review reduces to two checks:

1. The selected pattern is one of the eight known keys (not a
   silent new key, not a malformed substitution).
2. The numeric substitutions (`{n}`, `{s}`, `{lo}`, `{hi}`,
   `{n_low_oci}`) produce sane values consistent with the food
   corpus shape.

If both check out, AC10 PASSes without notes. If the pattern is
e.g. `contested` or `subcultural`, I confirm the negative-centrality
framing is consistent with the underlying data. No structural
re-review.

## Notes for the Coder

These are binding for the food.yaml + collection driver work.

1. **Write `food.yaml` verbatim** as specified above (binding
   B-D2). Do not paraphrase the `prompt_seed` text; the
   categorical-anchor wording was chosen precisely.

2. **Campaign ID:** `phase6-t13-food-2026-05-15` (B-D3) is fine if
   collection runs today; otherwise use the actual collection date
   per the `phase{N}-{kind}-{date}` precedent.

3. **No software-side spend gate** in
   `scripts/run_phase6_t13_food.py` (CLAUDE.md R14 + pitfall #14).
   No cost estimates, no caps, no `CDB_MAX_SPEND_USD`-style env
   vars, no estimate paragraphs in commit messages or verdict files.

4. **`model_version_returned`** must be recorded verbatim per
   pitfall #1. Confirm the driver preserves the API-returned
   version string distinct from `model_id`.

5. **AC10 pre-clearance:** after running `cdb_publish/build.py`,
   append the rendered `generated_lede` string to the Coder
   verdict file. Do not edit the lede string. CDA SME reviews
   verbatim before final commit.

6. **No edits to `lede_v1.py`** — the template is domain-agnostic
   and food substitutes cleanly. Editing it would require creating
   `lede_v2.py` per CLAUDE.md §6 R7; that is out of scope.

7. **No edits to `failures.py` or `run_decline_backfill.py`** —
   the pitfall #13 audit clears the current detector configuration
   for food.

8. **If collection produces sparse data (<5 models complete),
   pause and re-route to CDA SME** before running `cdb_analyze`.
   The Architect plan §10 risk #1 mitigation requires re-review
   below the 5-model floor. This is a stop condition per CLAUDE.md
   §8.

9. **`romney_small_n_warning: true` is expected** in
   `data/results/food/0.2.json` at n=9. This is not a defect; do
   not "fix" it.

## Notes for downstream agents

**UI/UX agent (Phase 6 minimum-viable-functional posture per
`feedback_ui_polish_scope.md`):**

- Pill "Food" inherits existing tokens (no new color, no new font);
  WCAG AA contrast is by inheritance.
- Three-pill DomainPicker row should not wrap at the documented
  viewport widths; if it does, that is a layout regression, not a
  design decision.
- The food lede strip uses the same KeyFinding component as family
  and holidays. No layout adjustment expected.

**Reviewer:**

- Confirm `food.yaml` matches the binding text above byte-for-byte.
- Confirm no edits to `cdb_core/schemas.py`, `lede_v1.py`,
  `failures.py`, or `run_decline_backfill.py`.
- Confirm no new dependency.
- Confirm append-only invariant on all three raw .jsonl files.
- Confirm `romney_small_n_warning: true` propagates through to
  `food.json` (not stripped, not overridden).
- Confirm the rendered food lede in `food.json` carries the CDA SME
  AC10 PASS reference in the commit body.

**Tester:**

- 3-pill DomainPicker test extension (AC21/AC22).
- Byte-identical regression check on `family.json` and
  `holidays.json` before and after the build (AC12).
- No new fixture set needed for the lede template substitution —
  existing template tests cover `{domain}` substitution generically.

## Carry-forward to Phase 6.5 / methodology page (downstream-tracked)

The following are not blockers for T13 but should land before the
methodology page closes:

- Methodology page should note that all three v1 domains operate at
  n<15 models and that this trips `romney_small_n_warning`, surfaced
  via CI width on Smith's S rather than a categorical "small-n"
  label. (T1/T2 concern.)
- The "different region of cognitive space" lede phrasing in the
  `subcultural` pattern should be cross-referenced from the
  methodology page so a cold reader understands "cognitive space" =
  MDS coordinate space, not model cognition. (T2 concern.)

These are advisory to the Architect on Phase 6.5/T1/T2; they do not
gate T13.

---

*End of CDA SME verdict for Phase 6 T13 sub-option B. Coder may
proceed once the UI/UX gate also clears. The binding food.yaml
content above is final; no further CDA SME review of the YAML is
required. AC10 verbatim review of the rendered lede happens after
Coder runs `cdb_publish/build.py`, before final commit.*
