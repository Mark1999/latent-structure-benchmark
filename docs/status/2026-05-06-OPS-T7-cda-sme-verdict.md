# OPS-T7 — CDA SME light-touch verdict (QA-notes interpreter + decline banner + pile-sort source caption)

**Verdict:** PASS-WITH-NOTES
**Reviewer:** CDA SME (external SME)
**Date:** 2026-05-06
**Plan reviewed:** `docs/status/2026-05-06-OPS-T7-architect-plan.md`
**Scope:** copy-only methodological review of the internal ops dashboard. `DESIGN_SYSTEM.md` gating waived per `feedback_visual_inspection.md`. §1.5 framing and §7 forbidden vocabulary are still binding (universal rules). The Q1 interpretation table makes claims about which downstream computations a flagged run is or isn't safe for, so Axis 2 deserves real engagement.

---

## Four-axis scorecard

| Axis | Verdict | Note |
|---|---|---|
| Axis 1 — Protocol validity | N/A | No protocol decisions. Read-only display of already-collected metadata. |
| Axis 2 — Analytical validity | PASS-WITH-NOTES | Interpretation table is largely correct. Two binding edits: (a) `freelist_too_low` impact must say salience-aggregate exclusion is *advisory for the operator*, not automated — `qa_passed=False` flags the record but downstream salience code does not currently filter on it; (b) `uniqueness_too_low` impact must clarify the check is computed across *runs in the group*, not on the individual record alone. See per-question Q1 below. |
| Axis 3 — Claims validity | PASS | The interpreter explains run-metadata, not model claims. The decline banner describes events, not cognition. The pile-sort caption describes inputs to a sort step, not what the model "thinks." No §1.5 framing risk. |
| Axis 4 — Audience translation | PASS-WITH-NOTES | Audience is Mark + future researchers + the Coder building this. The "(raw segment: \`{raw_segment}\`)" suffix is exactly right for traceability. Two minor wording tightenings below. |

Register compliance: N/A (no register-bearing analysis).
Vocabulary compliance: PASS conditional on the binding edits below.

---

## Per-question responses

### Q1 — QA-notes interpretation table

**APPROVE WITH BINDING EDITS** on three rows; **APPROVE option (iii)** for the bare-integer disambiguation; **APPROVE recording option (iv)** as a follow-up architect task.

#### Bare-integer disambiguation: **(iii) position-based heuristic**

Adopt: **bare integer as the *only* segment → `freelist_too_low` (check 1); bare integer as the *trailing* segment after at least one other shorthand → label as ambiguous (`token_inconsistency_or_campaign_tag`).**

Rationale for picking (iii) over the alternatives:
- (i) "render both possibilities" is wasteful in the only-segment case where the answer is unambiguous.
- (ii) "treat all bare integers as ambiguous" loses information in the common only-segment case (`"0"`, `"7"`, `"9"`) where freelist-too-low is the unique reading. Real data already contains these.
- (iii) gives the operator a clean reading in the only-segment case and an honest acknowledgement of ambiguity in the trailing case. It costs one extra branch and one extra interpretation code (`token_inconsistency_or_campaign_tag`).
- (iv) is the right *long-term* fix and should be filed as a follow-up architect task — but it should not be a blocker on OPS-T7. The position-based heuristic is sufficient for the operator-facing interpretation today.

**Binding sub-note:** when option (iii) renders the trailing-bare-integer segment as `token_inconsistency_or_campaign_tag`, the interpretation must contain *both* readings in the `impact` text, e.g.:

> *"Either (a) provider-reported output token count deviates >100% from the chars/4 heuristic — heuristic-only flag, run remains usable; or (b) the trailing segment is a campaign-id tag appended by the runner — not a failure. The two cases cannot be distinguished from the qa_notes string alone. Inspect the run's raw record to disambiguate."*

This is operator-honest. It does not pretend to know which case applies and tells the operator how to resolve it.

#### Follow-up architect task (binding to file, not to OPS-T7 scope)

Add as a tracked follow-up: **runner-side prefix change** so every shorthand carries its check number (e.g. `check5:60124ms`, `check6:4779`, `tag:171`). This makes the interpreter unambiguous and removes the special case. Out of scope for OPS-T7 per Architect's read; in scope for a future small architect task. The Architect should file this under their backlog.

#### Binding edits to the interpretation table

**Row `freelist_too_low` — impact column:** change

> *"Salience measures (Smith's S, Sutrop CSI) computed on this run are unreliable. Excluded from grouped salience aggregates."*

to

> *"Salience measures (Smith's S, Sutrop CSI) computed on this run are unreliable. Operator should exclude or flag this run when computing grouped salience; the analysis pipeline does not currently filter on `qa_passed` automatically."*

Rationale: the original phrasing implies automated filtering downstream. Today, `qa_passed=False` records remain in `data/raw/informants.jsonl` and the analyze layer does not gate on the field. Saying "Excluded from grouped salience aggregates" overstates what the QA flag does. The corrected text makes clear that the flag is operator-actionable advice, not an automatic filter. (See `data/raw/informants.jsonl` append-only convention; per `CLAUDE.md` §9 pitfall 10, failed records stay in place with `qa_passed=False`.)

**Row `uniqueness_too_low` — impact column:** change

> *"Aggregate concern, not run-specific. The (model, domain) group's salience may reflect rote output rather than informed elicitation."*

to

> *"Aggregate concern, computed across the >=2 runs for this (model, domain) group — not on this single record. The group's salience structure may reflect rote output rather than independent elicitation across runs. Single-run analyses on this record are unaffected; cross-run group analyses warrant inspection."*

Rationale: (1) The original sentence "informed elicitation" is borderline §1.5-adjacent (implies the model is "informed" or "uninformed"); "independent elicitation across runs" describes the actual statistical concern (sampling variance is low; the model is producing similar lists across runs). (2) Naming the >=2-runs precondition makes it clear *why* this is a group-level note attached to every record in the group rather than a per-record fact. The flag attaches to each member record because the runner emits per-record `qa_notes`, but the underlying check is across the group; the operator needs that context to interpret it.

**Row `token_inconsistency` — impact column:** change

> *"Heuristic-only flag; the run is usable. Indicates either heavy non-ASCII content or a provider-side token-count anomaly."*

to

> *"Heuristic-only flag; the run is usable for all downstream analyses. The chars/4 heuristic systematically under-counts on numbered lists, short tokens, and non-ASCII content; a flag here typically means the heuristic is wrong, not that the provider is wrong. Inspect only if other anomalies are present in the same record."*

Rationale: the original phrasing gives equal weight to "non-ASCII" and "provider-side anomaly" as causes. In practice (per the `TOKEN_TOLERANCE = 1.0` comment in `scripts/qa_check.py:51-56`), the heuristic itself is the loose part; the provider-side count is usually correct. The corrected text is honest about which side is unreliable. This matters because the operator should not chase a "provider anomaly" rabbit hole on every check-6 flag.

#### Other rows — APPROVE verbatim

`latency_exceeded`, `label_count_mismatch`, `matrix_non_binary`, `matrix_asymmetric`, `empty_request_id`, `unknown` — approved as drafted. The `label_count_mismatch` impact correctly says the co-occurrence matrix is "still well-formed and usable for MDS/clustering" while pile-label-keyed analyses must skip — this is the right operational call and matches the `docs/status/2026-04-20-f2-cda-sme-verdict.md §T09` ruling that the CDA SME has previously bound.

The `matrix_non_binary` and `matrix_asymmetric` impacts both correctly say "unsafe for any pile-sort-derived analysis" — this is the right strict reading; there is no graceful degradation when the co-occurrence matrix is malformed.

The `empty_request_id` impact correctly distinguishes provider-log provenance (lost) from local SHA256 provenance (intact). Right call.

### Q2 — Decline banner placement

**APPROVE (a) — top-of-detail-section, ABOVE the QA badge.**

Rationale: a decline event is a finding, and `failures-as-findings` (memory `project_failures_are_findings.md`) is binding. The QA badge says "is the *run* structurally well-formed"; the decline banner says "did the model produce a recognizable informant performance, or did it refuse / step out of role." These are conceptually orthogonal but the decline question is hierarchically prior — if the run is a refusal, the QA badge's PASS/FAIL is informative but secondary. Placing the banner above the QA badge reflects that hierarchy.

(b) below-QA-badge would visually subordinate decline events to structural QA, which is the wrong hierarchy. (c) sticky-top is overkill for an internal ops tool and would clutter the page header on every detail view.

The Architect's plan (§4.1 and A2.1) correctly identifies that this requires hoisting the `_load_decline_interviews()` / `find_decline_events()` calls upward. That's a fine refactor; the operations are pure reads (no I/O ordering concerns).

### Q3 — Decline banner wording

**APPROVE WITH ONE BINDING EDIT.**

Architect proposed:

> *"This run produced N decline event(s). See **Decline summary** and **Decline events** sections below for details."*

Use instead (binding):

> *"This run has N classified decline event(s). See **Decline summary** and **Decline events** sections below."*

Three small changes:
1. **"produced" → "has classified"**: the decline events were *recognized and classified* (by Mark + the detector) after the fact; the model didn't "produce decline events" in the same sense it produces tokens. "Has classified decline event(s)" is more precise and avoids any implication that the model self-labelled.
2. **Drop "for details"**: redundant with the section names "Decline summary" and "Decline events." Operator already knows what to expect.
3. **Singular form when N=1**: the parenthetical "(s)" is fine; a more polished form would conditionally render "1 classified decline event" vs "N classified decline events." Not binding — the parenthetical is acceptable for an internal tool.

Verbatim string for the static-text test: *"has N classified decline event(s)"* (with N substituted at render time, the rest verbatim).

### Q4 — Pile-sort source caption wording

**APPROVE WITH BINDING EDITS** on both branches.

Architect proposed:

- own_freelist: *"Items sorted: this informant's own freelist (Step 1, N items)."*
- external: *"Items sorted: external freelist source `{item_source}` (N items)."*

Use instead (binding):

- **own_freelist:** *"Items sorted: this informant's own Step 1 freelist (N items)."*
- **external:** *"Items sorted: items from `{item_source}` (N items). Not derived from this informant's own freelist — see `PileSortRecord.item_source` for source semantics."*

Rationale:

**own_freelist:** "this informant's own freelist (Step 1, N items)" reads as "(Step 1) clarifies which step the freelist came from." But the freelist *is* Step 1 by definition of the CDA protocol (`ARCHITECTURE.md` §4.1.1). Saying "Step 1 freelist" inline (compound noun) reads cleaner and avoids the parenthetical. Also closer to the protocol's natural language.

**external:** the original says "external freelist source `{item_source}`" which conflates two things: (1) the *items* are from an external source, and (2) the *source identifier* is the `item_source` token. The corrected wording separates them: "items from `{item_source}`" names the source, and the trailing sentence makes the contrast with own_freelist explicit. This matters because Mark's hypothesis here (memory `project_future_slicing.md`) is that future cross-collection runs will use aggregated/foreign freelists and the dashboard needs to surface that fact loudly. The Architect's particular concern in Q4 ("should the external caption clarify whether the items are a consensus list…") is correctly resolved by **not** trying to interpret `item_source` in the caption — the dashboard cannot know that from the schema alone — but pointing at `PileSortRecord.item_source` gives the operator a precise place to look.

### Q5 — Pile-sort item count basis

**APPROVE (a) — flattened total of `parsed_piles`.**

Rationale: this is "the count of items the model was asked to sort, observed at sort time" (Architect's framing — correct). Specifically:

- (a) `len(record.pile_sort.parsed_piles)` flattened — counts items *as the sort step actually saw them*. If the model received N items and sorted N items, this is N. If the model received N items and only sorted N-2 (dropping two), this is N-2 — which is operationally interesting and worth surfacing.
- (b) `len(record.freelist.parsed_items)` — the count *the freelist step produced*. This is misleading when `item_source != own_freelist` (the freelist isn't the input to the sort). Reject.
- (c) distinct count across `parsed_piles` flattened — answers a different question ("how many unique tokens did the model place"). Useful for QA but not for "how many items was it sorting." If the same item appears in two piles (which the QA matrix-binary check would normally catch but might miss in edge cases), distinct-count would silently hide that. Reject.

(a) is the right answer. The helper `pile_sort_item_count(record) -> int` should return `sum(len(pile) for pile in record.pile_sort.parsed_piles)` per the existing `parsed_piles` schema (a list of lists of item strings).

**One sub-note (non-binding):** if the operator is on a record where (a) and the freelist count diverge sharply (e.g., 200-item freelist but 47-item sort), that's an interesting data point that an alert future-state could surface. Out of scope here. Filing as nice-to-have.

### Q6 — Forbidden-vocabulary clearance

**CONFIRM** — none of the proposed literals (after the binding edits in Q1, Q3, Q4) contain §7 or §1.5.4 forbidden vocabulary.

Specifically scanned the corrected text for:
- `believes`, `thinks`, `worldview`, `understands`, `sees the world`, `cultural bias` (standalone), `within-model consensus`, `within-model cultural consensus`, `within-model eigenratio`, `within-model CCM`, `closer to human`, `publishable` — none present.

The corrected `uniqueness_too_low` impact text drops the original's "informed elicitation" phrasing, which was §1.5-adjacent. The replacement "independent elicitation across runs" is statistically descriptive and clean.

The corrected `freelist_too_low` impact text uses "operator should exclude or flag" — agentive language about the operator, not the model. Clean.

The corrected decline banner ("has N classified decline event(s)") is event-language, not cognition-language. Clean.

The pile-sort source caption corrected text says "items from `{item_source}`" — pure data-flow language. Clean.

Forbidden-vocabulary regex test (AST-T5 in plan §4.3) must scan all three rendered strings — both pile-sort caption branches, the decline banner template, and every interpretation `why` and `impact` field in the table. The plan already specifies this; affirming.

---

## Binding notes the Coder MUST apply

1. **Q1 binding edits to the interpretation table:** the impact strings for `freelist_too_low`, `uniqueness_too_low`, and `token_inconsistency` are replaced with the corrected text in this verdict §Q1. The `latency_exceeded`, `label_count_mismatch`, `matrix_non_binary`, `matrix_asymmetric`, `empty_request_id`, and `unknown` rows are approved verbatim.
2. **Q1 disambiguation: option (iii) is binding.** The interpreter implements: *only-segment bare integer → `freelist_too_low`*; *trailing-bare-integer-after-other-shorthands → `token_inconsistency_or_campaign_tag`* with both readings rendered in the impact text per the verbatim string in this verdict §Q1.
3. **Q1 follow-up:** the Architect must file a follow-up task for the runner-side prefix change (`check5:60124ms` etc.) per option (iv). Out of scope for OPS-T7; in scope for the Architect's backlog.
4. **Q2 placement is binding (a):** banner above the QA badge. The `_declines` lookup is hoisted upward as proposed in plan §4.1.
5. **Q3 binding edit to the banner template:** *"This run has N classified decline event(s). See **Decline summary** and **Decline events** sections below."* Verbatim. Update the AST-T1 static-text test to assert this exact substring.
6. **Q4 binding edits to both pile-sort source caption branches:** verbatim text in this verdict §Q4. Both branches must be present in the source, asserted by the AST-T4 grep.
7. **Q5 binding (a):** `pile_sort_item_count` returns `sum(len(pile) for pile in record.pile_sort.parsed_piles)`.
8. **A1.6 / AST-T5 forbidden-vocab scan must include the corrected text** from this verdict, not the Architect's drafts.
9. **Commit body must reference this verdict file path:** `docs/status/2026-05-06-OPS-T7-cda-sme-verdict.md`.
10. **Test QI-T5 / QI-T6 / QI-T12 expected codes:** under option (iii), QI-T5 (`"247348ms; 4779"`) yields 2 codes (`[latency_exceeded, token_inconsistency_or_campaign_tag]`); QI-T6 (`"0; 71000ms; 171"`) yields 3 codes (`[freelist_too_low, latency_exceeded, token_inconsistency_or_campaign_tag]`); QI-T12 (`"4779"` alone) yields 1 code (`[freelist_too_low]`). Update the test table with these counts.

## Nice-to-have suggestions (non-binding)

1. Conditionally pluralize the decline banner: "1 classified decline event" vs "N classified decline events" instead of the parenthetical "(s)". Cosmetic; the parenthetical is acceptable for an internal tool.
2. If the (a) flattened-pile-sort-item count and the freelist count diverge sharply on a record, that's a methodologically interesting signal worth surfacing in a future enhancement. Out of scope for OPS-T7.
3. When the runner-side prefix follow-up (Q1 (iv)) lands, the Q1 disambiguation logic in `qa_interpreter.py` becomes redundant and can be retired. Document this in the helper module's docstring so a future maintainer knows the position-based heuristic is a transitional measure.
4. Consider adding a single AST-level test that asserts the banner is rendered *above* the QA badge (e.g., by source-position grep of the `st.subheader(f"Detail —` literal vs the QA badge literal vs the banner literal). The plan's AST-T1 covers presence; placement-order is an extra guard that would catch a regression where the banner gets re-positioned.

---

## Closing summary

The plan is methodologically sound and the interpretation table is largely correct; three impact-column rewordings (advisory-not-automated framing for freelist-too-low, group-level + non-§1.5-adjacent framing for uniqueness-too-low, heuristic-honest framing for token-inconsistency), position-based bare-integer disambiguation (iii) with a runner-prefix follow-up filed (iv), banner-above-QA-badge placement, and minor wording tightenings on the banner and both pile-sort caption branches resolve the methodological surface; Coder may proceed.
