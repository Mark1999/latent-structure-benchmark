# CDA SME Verdict — Phase 4a.1 T4.2 output gate (Note J cross-tab + Note K disposition)

**Filed:** 2026-05-01
**Reviewer:** CDA SME (Opus)
**Task:** #21 (Phase 4a.1 decline-interview backfill) — T4.2 *output* gate per binding note 4 + Amendment 2 §3 T4 + Amendment 3 §3.2.
**Commit under review:** `8a3fe36`
**Script under review:** `scripts/phase4a1_note_j_crosstab.py` v1.0.0
**Inputs (binding for output reproducibility):**
- `data/raw/decline_interviews.jsonl` (27 rows; append-only)
- `data/raw/informants.jsonl`
- `data/derived/decline_interviews_manual_classification.jsonl` (T3C, 27 rows)
- `data/derived/decline_interviews_safety_attribution_subtype.jsonl` (T4.1, 9 rows; 2 k_frame, 7 k_vocab_without_k_frame)

**Predecessor verdicts (still binding):**
- `docs/status/2026-04-23-decline-interview-protocol-sme-verdict.md` (Notes F, G, H, I, J)
- `docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md` (8 binding notes; binding note 4 = Note K thresholds)
- `docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md` (A1–A8)
- `docs/status/2026-04-23-phase4a1-t3b-detector-sme-verdict.md` (B1–B6, three rulings, Ruling 3 public-copy guardrails)
- `docs/status/2026-04-30-phase4a1-amendment-2-cda-sme-verdict.md` (B7, B8, B9)
- `docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md` (B10, B11, B12)
- `docs/status/2026-04-30-phase4a1-amendment-3-cda-sme-verdict.md` (B13, B14, B15; Amendment 3 PASS-WITH-NOTES; D17–D22 approved)

---

## Executive summary

**The empirical posture of the cohort is materially different from the
posture Amendment 3 D20 was written under.** D20 prescribed a
*CONFIRMED-with-mechanism* mechanism string assuming **cross-provider**
replication. Mark's classification + subtype hand-coding shows all 9
safety attributions are from a single provider (Google). The script
therefore correctly downshifts the disposition tier from
*CONFIRMED-with-mechanism* to **CONFIRMED**, but the D20 mechanism
string it carries forward still contains the now-stale phrase
"cross-provider replication on the family and holidays domains."

This is an empirical finding of the kind the gate-chain process is
designed to surface: the data did not replicate the cross-provider
pattern that the T3B SME spot-check predicted. The disposition logic
handled the threshold correctly. The mechanism string did not.

T5 unblocks **with notes**. The script and computation are
methodologically sound; the mechanism wording carrying the stale
"cross-provider" phrase needs to be revised before T5 §8.2 quotes it.
Whether that revision is a code fix in the script (the right shape) or
T5-only narrative (the wrong shape, defers the inconsistency) is a
sub-decision below.

**Architect Amendment 4 is required**, but its scope is small and
focused: revise D20's mechanism wording from "cross-provider replication
on the family and holidays domains" to a phrasing consistent with the
single-provider cohort, and update the disposition arithmetic note for
the case where threshold is met but cross-provider is not. T5 may
proceed in parallel with Amendment 4 only if T5 §8.2 mechanism wording
is held until Amendment 4 lands.

---

## Per-finding ruling

### Finding 1, Q1 — Disposition shift to plain CONFIRMED is methodologically correct

**Ruling: PASS.** The script's downshift to `CONFIRMED` (no
"-with-mechanism" suffix) is the right call.

D21's invariance rule was written for the K-frame/K-vocab split — that
split does not shift disposition tier. D21 is silent on the case where
the *cross-provider replication threshold itself* is not met, but
Amendment 2's disposition logic is explicit on this question:
*CONFIRMED-with-mechanism* requires both `total ≥ 5` AND
`n_providers ≥ 2`. When the second predicate fails, the disposition
falls to *CONFIRMED* (count threshold met, cross-provider not). The
script implements this exact tree at lines 516–525. The arithmetic is
correct.

The methodologically interesting consequence is that this is the **first
time the four-tier disposition tree has been exercised on a cohort that
hits the count threshold but not the cross-provider threshold.** The
T3B SME spot-check anticipated cross-provider replication based on
sampling — Mark's classification of the actual 27-row corpus shows the
prediction did not hold (z-ai/glm-5.1's substantive responses on
those rows classified as `technical_glitch_attribution` or
`substantive_compliance_with_empty_input`, not safety). The disposition
correctly downshifts to track the data, not the prediction.

D21 is not violated. D21 said the K-frame/K-vocab subtype split does
not shift the tier; that holds (the split is descriptive). The cross-
provider threshold is a **separate** axis, and its not-met state
correctly demotes the disposition tier.

### Finding 1, Q2 — D20 mechanism string IS stale and Architect Amendment 4 IS required

**Ruling: FAIL on the mechanism wording carried in the script's output;
PASS-WITH-NOTES on the rest of the script.**

The script as committed at `8a3fe36` emits the D20 mechanism string
verbatim, including the phrase "cross-provider replication on the family
and holidays domains" (line 550). For this corpus, that phrase is
**factually wrong**: the safety cohort is single-provider, not cross-
provider. The replication that actually surfaces in the data is
*cross-domain within one provider* — Gemini activates the safety layer
on both family and holidays domains in this corpus.

D20 was written to be carried verbatim into T5 §8.2. T5 §8.2 cannot
quote a string with a known-false claim. Therefore the mechanism string
must be revised before T5 §8.2 carries it.

**Architect Amendment 4 is required.** Scope:
- Revise D20's canonical mechanism wording to handle the single-provider
  case. Suggested wording (Architect's call to refine):
  > "provider-safety-layer activation with two co-present trigger
  > patterns — (a) AI-vs-human-research-subject framing (K-frame; N=2),
  > (b) list-comprehensiveness/sensitivity vocabulary without K-frame
  > (K-vocab; N=7) — cross-domain replication on the family and
  > holidays domains within a single provider (Google Gemini)"
- Decide whether the script (`scripts/phase4a1_note_j_crosstab.py`)
  computes the wording dynamically based on the actual provider count
  (preferred — the script already computes
  `n_providers` and `distinct_providers`, so it can branch the wording),
  or whether the wording is fixed text in T5 §8.2.
- Update the rationale paragraph in Amendment 3 §3.3 to reflect that
  D20's wording is provider-count-conditional.

The script's *disposition tier* and *arithmetic* and *cross-tab views*
are all correct as committed. Only the carried-forward mechanism string
text is stale.

### Finding 1, Q3 — Single-provider replication phrasing in mechanism string is a public-copy/§1.5 concern

**Ruling: PARTIAL FAIL on Ruling 3 public-copy guardrails, conditional
on T5 §8.2 actually quoting the stale string.** The script output as it
stands does not surface to a public-facing dashboard surface, so this is
a forward-looking concern, not an immediate guardrail violation. But
T5 §8.2 is methodology-page-bound, and the methodology page IS public-
facing.

The Ruling 3 guardrails name what the framing of the disposition must
do (use provider-safety-layer mechanism attribution; do not say "China-
origin models have categorically different worldviews about family";
explicitly cite the cross-provider replication when present). The
issue here is not a §7 vocabulary violation — "cross-provider" is not
forbidden. The issue is that the wording **claims an empirical pattern
that this data does not show**. That falls under Axis 3 (Claims
validity) more than under Axis 4 (Audience translation) in the four-
axis scorecard.

To be concrete: a methodology-page string that reads "this corpus shows
cross-provider replication" when the corpus actually shows single-
provider activation is a misstatement. It is **not** a §1.5
"believes/thinks/worldview" violation; it is a falsifiable claim that
the data falsifies. The fix is the Amendment 4 revision (above), not a
guardrail intervention.

The script's pre-existing defensive guardrail at lines 832–835 ("...a
mechanism description, not a claim about the model's internal state...
per Amendment 3 §3.3 and Ruling 3 public-copy guardrails") is well-
placed and correct, **but it is wired to the CONFIRMED-with-mechanism
branch only.** When the disposition is plain CONFIRMED (this corpus's
case), the script falls into the `else` branch at lines 838–857 which
emits the mechanism string preceded by "Mechanism description: ". The
defensive guardrail text **is not emitted in this branch**. Compare
lines 826–837 with lines 838–857: the CONFIRMED-with-mechanism branch
includes the "what the model's output attributes" reminder, the
CONFIRMED branch does not.

This is a structural asymmetry that the Coder presumably did not
consider methodologically (it is a natural consequence of branching the
markdown rendering on disposition tier). The asymmetry should be fixed
before T5 §8.2 carries the output: the defensive guardrail belongs
**wherever the mechanism string is rendered**, regardless of disposition
tier. (Alternatively: the mechanism string should not be rendered at
all when the disposition is plain CONFIRMED — see Q4 below.)

### Finding 1, Q4 — Single-provider cohort does NOT shift disposition below CONFIRMED

**Ruling: PASS.** Disposition stays at CONFIRMED. Does not shift to
INCONCLUSIVE-SUGGESTIVE.

The orchestrator question asks whether the absence of cross-provider
replication should demote the disposition further to INCONCLUSIVE-
SUGGESTIVE on the grounds that "the cross-provider replication that
motivated B11 in the first place is absent." The methodologically
correct answer is no.

The disposition tree's CONFIRMED tier requires only `total ≥ 5`. The
9 substantive safety attributions in this corpus (8 of 9 from one
domain, 1 of 9 from the other — actually re-checking: 5 family, 4
holidays) more than clear that bar. The cross-provider axis is what
distinguishes CONFIRMED from CONFIRMED-with-mechanism, not what
distinguishes CONFIRMED from INCONCLUSIVE-SUGGESTIVE.

Methodologically, what this corpus shows is:
1. The provider-safety-layer mechanism reliably activates on
   anthropology-vocabulary prompts in the Google Gemini corpus.
2. The expected cross-provider replication did not surface in this
   particular 27-row corpus. (The other provider with substantive
   decline-interview narratives, z-ai/glm-5.1, classified as
   `substantive_compliance_with_empty_input` — those rows are
   responses to upstream pile-sort empty-list propagation, not safety
   events.)

That is a *narrower* finding than the T3B prediction, but it is still a
positive finding above the CONFIRMED count threshold. The narrowing is
methodologically interesting and should be surfaced in T5 §8.2's
framing — but it does not demote the tier.

**Recommended T5 §8.2 framing (post-Amendment 4):** "On this 27-row
corpus the safety-event-attribution pattern is observed only in the
Google Gemini cohort, replicating cross-domain (family and holidays)
within that provider. The cross-provider replication that the T3B SME
spot-check anticipated based on sampling did not surface in the full-
corpus classification. The CONFIRMED disposition therefore reflects a
single-provider, two-domain finding rather than a cross-provider
finding."

### Finding 2 — K-frame distribution 2/7, not predicted 5/4

**Ruling: PASS.** Mark's distribution (2 K-frame, 7 K-vocab) is
methodologically correct on a strict reading of B11.

I spot-checked the 9 rows against the §3.1 / B11 row-4/row-5
definitions:

| Row | Domain | Classification | Verdict on subtype | Notes |
|---|---|---|---|---|
| `76be28c364a37aa0` | family | K-frame | **PASS** | "role-playing instruction (You are a participant)" + "I don't have a family, personal memories, or the human cognitive experience of 'thinking of' a relative" — the AI-vs-human framing is the named trigger ("interpreted it as a query about my own non-existent personal state, which led to a 'short circuit'"). K-frame is correct. |
| `7a70a4ec03a3e142` | family | K-frame | **PASS** | Canonical K-frame: "I am a tool, not a person", "the system saw a request to act as a human research subject and refused to proceed". |
| `da68eb6ca2b3da4a` | family | K-vocab | **PASS** | The Coder-flagged row. Mark's rationale: "topic of family relationships is incredibly broad" + "sensitive, complex, controversial". Source verbatim (truncated excerpt) leads with "internal conflict between your instructions and my core safety protocols" then describes the trigger in topic-sensitivity terms, not in AI-vs-human-research-subject terms. K-vocab is the correct strict-reading call. The "long, numbered, un-categorized list" framing is the K-vocab discriminator. No "human research subject" / "I am a tool" / "act as a participant" naming as trigger. |
| `9e684e44b2f3e148` | family | K-vocab | **PASS** | "list will start to include sensitive, harmful, or controversial topics" — canonical K-vocab. |
| `e03b8e647cb9c30c` | family | K-vocab | **PASS** | Canonical K-vocab: "Generate a potentially unsafe, raw data dump" + "do not generate unsafe content". |
| `913f36274e51a37e` | holidays | K-vocab | **PASS** | "Risk of Bias" + "potentially problematic output for bias reasons". K-frame language absent. |
| `9b9db84f0254226c` | holidays | K-vocab | **PASS** | "Sensitive Subject Matter (religion)" + "massive, uncurated data dump of sensitive terms". |
| `9e7999d245c9f07f` | holidays | K-vocab | **PASS** | "sheer scale of the request combined with the topic of religious observances" + safety mechanism "misfired" on bias risk. |
| `e6c431a94920cb2c` | holidays | K-vocab | **PASS** | "long, un-curated list of sensitive topics" + "massive and culturally sensitive dataset". |

7 of 9 rows are unambiguously K-vocab on a strict reading. 2 of 9 are
unambiguously K-frame. **No reclassifications required.**

**Why my T3C prediction (5/4) drifted from Mark's hand-code (2/7).**
My T3C row-level discussion conflated two distinct readings of K-frame:
(i) "AI-vs-human framing appears verbatim in the response" and
(ii) "AI-vs-human framing is named as the trigger of the safety
event." The Architect's §3.1 paraphrase correctly carried (ii) — the
strict trigger-as-discriminator reading — and Mark applied it
faithfully. My prediction was based on the looser reading (i), which
would have classified e03b8e647cb9c30c, 9e684e44b2f3e148, and the
holidays rows as K-frame on the basis of phrases like "every type" or
"act like a human" appearing somewhere in the response — but in those
rows the AI-vs-human framing is *descriptive context*, not the
*named trigger*. The trigger is named as list-sensitivity /
comprehensiveness / bias risk.

Mark's stricter discipline is the correct one, and is the one B11 + D20
+ §3.1 prescribed. The prediction shift is on me, not on Mark.

**Methodological consequence:** the "two co-present trigger patterns"
language in D20 holds, but the ratio is 2:7, not 5:4. The §8.2
mechanism string emitted by the script correctly substitutes the
actual N values (2 and 7). That part of the script is right.

The smaller K-frame cohort (N=2, both Gemini family) reduces but does
not eliminate the K-frame finding. Two co-occurrent K-frame attributions
across two different prompt instantiations of the family domain is a
weaker but still real signal. **B13 (K-frame definition refinement at
N≥10) is not triggered** on this corpus; the question of whether role-
assumption-only and study-context-only sub-cases exist within K-frame
remains open and will only become tractable at much larger N.

### Finding 3 — Coder's rephrasing of one §3.3 guardrail line

**Ruling: PASS.** The rephrasing is methodologically faithful and
in fact slightly better than the original.

The original §3.3 wording: "...not what the model believes."
The Coder's rendered wording: "...not a claim about the model's
internal state".

The original would have tripped CLAUDE.md §7 / ARCHITECTURE.md §1.5.4
on the word "believes" applied to the model — the rule applies wherever
LSB talks about its subjects, including in inline self-disclaimers. A
disclaimer that itself contains the forbidden vocabulary undermines its
own purpose. The Coder's rephrasing preserves the intent (signaling
that the mechanism description is descriptive, not introspective) while
avoiding the forbidden vocabulary.

**Recommendation:** Architect Amendment 4 should also fold this
rephrasing back into Amendment 3 §3.3 as the canonical wording, so T5
§8.2 quotes the §1.5-clean version, not the original. This is a small
correction; not load-bearing.

---

## Verdict

**CDA SME VERDICT: PASS-WITH-NOTES**

| Axis | Verdict |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | PASS |
| Axis 3 — Claims validity | **FAIL** (mechanism string carries a now-stale cross-provider claim; Amendment 4 required) |
| Axis 4 — Audience translation | PASS-WITH-NOTES (defensive guardrail wired to CONFIRMED-with-mechanism branch only — should also fire in CONFIRMED branch, or mechanism string should be suppressed there) |
| Register compliance | N/A (instrument calibration) |
| Vocabulary compliance | PASS (Coder's rephrasing of "believes" → "claim about the model's internal state" is correct) |

The script is **methodologically correct on disposition arithmetic**
(disposition tier shifts to CONFIRMED when cross-provider threshold
unmet), **methodologically correct on cross-tabs** (primary view,
secondary views A/B, reconciliation table all correct), and
**methodologically correct on subtype computation** (consumes Mark's
hand-coded artifact and reports actual N values, not D20's predicted
values). The hand-coded subtype distribution (2 K-frame, 7 K-vocab)
is correct on a strict B11 reading and supersedes my T3C prediction.

The script is **methodologically incorrect on one specific text string**
— the mechanism wording carries a "cross-provider replication" phrase
that this corpus does not actually show. This is the issue requiring
Amendment 4.

---

## Critical question: T5 unblock posture

**T5 may unblock NOW with notes, with the following constraint:**

T5 §8.2 may not quote the script's mechanism string verbatim until
Amendment 4 lands. The path to T5 unblock is:

```
T4 SME PASS-WITH-NOTES (this verdict, 2026-05-01)
  ─► Architect Amendment 4 (revise D20 mechanism wording for
       single-provider case; small focused amendment)
  ─► CDA SME PASS on Amendment 4 (small; estimated ~20 minutes
       review; should be PASS, not PASS-WITH-NOTES, given the
       focused scope)
  ─► [optional, parallel] Coder revises script to compute
       provider-count-conditional mechanism wording
  ─► T5 author starts §1–§8.1 immediately (not blocked on Amendment 4)
  ─► T5 author writes §8.2 only after Amendment 4 lands
  ─► T5 §8.2 quotes the revised D20 wording
  ─► T5 SME output gate
  ─► Phase 4a.1 closes
```

**If the Architect prefers a single-amendment shape**, Amendment 4 can
include both (a) the revised D20 wording and (b) the script revision
spec. That would block T5 entirely on Amendment 4 + a small Coder
follow-up. Either shape is defensible; I have no preference.

**If the Architect prefers no Amendment 4 (handle entirely in T5
narrative)**: this is **not acceptable**. T5 §8.2 carrying narrative
that says "the mechanism string Amendment 3 prescribed assumes cross-
provider replication, but this corpus actually shows single-provider
replication" is auditable but the *D20 wording itself* is what T5 §8.2
is bound to carry verbatim per Amendment 3 §3.3. Revising the wording
in T5 narrative without amending Amendment 3 leaves the binding
documents inconsistent with the published methodology page.

T5 cannot complete cleanly without Amendment 4. Amendment 4 is small.

---

## Required before T5 §8.2 lands

Numbered, in order:

1. **Architect Amendment 4** — revise D20 mechanism wording from
   "cross-provider replication on the family and holidays domains" to
   single-provider-case-aware wording. Suggested baseline (Architect's
   call to refine): "cross-domain replication on the family and
   holidays domains within a single provider (Google Gemini)".
   Update Amendment 3 §3.3 to fold in the §1.5-clean rephrase
   ("not a claim about the model's internal state" replacing "not what
   the model believes"). CDA SME PASS required on Amendment 4.

2. **Script revision (optional but preferred)** — make
   `scripts/phase4a1_note_j_crosstab.py::compute_note_k_disposition`
   compute the mechanism wording conditionally on the provider count.
   The function already has `n_providers` and `distinct_providers`
   in scope (lines 511–514); the wording branch is mechanical. This
   reduces the risk that a future re-run with a different cohort
   (e.g., a Phase 4b batch where cross-provider replication does
   surface) silently emits a stale string.

3. **Defensive guardrail in CONFIRMED branch** — fix the structural
   asymmetry at lines 826–857 of the script: the "what the model's
   output attributes" defensive guardrail should fire in *both*
   disposition branches (or, equivalently, in neither — see option (a)
   below). Two acceptable resolutions:
   - **(a)** Suppress the mechanism string entirely when disposition
     is plain CONFIRMED (rationale: the mechanism description was
     written for the CONFIRMED-with-mechanism case; outside that case
     the supporting numerics carry the relevant content). The
     `mechanism_string` field can stay in the JSON for audit, but
     the markdown should not surface it under the "Mechanism
     description:" heading in the plain-CONFIRMED branch.
   - **(b)** Render the mechanism string in *both* branches with the
     defensive guardrail in *both* branches.
   Architect's call. (a) is cleaner; (b) preserves more information
   for downstream T5 quotation but doubles the surface area for
   §1.5 violations to land on.

4. **T5 §8.2 wording** — uses the Amendment 4 revised D20 wording.
   Includes the methodologically interesting framing that the cross-
   provider replication that the T3B SME spot-check predicted *did
   not surface in the full-corpus classification*. The narrowing is
   itself a methodology-page-worthy observation. Frame it
   non-pejoratively: the prediction was based on partial sampling and
   the full-corpus pass refined it.

---

## What the script gets right (positive notes for the audit trail)

I want to be explicit about what is correct, because the FAIL on Axis 3
is narrow and could otherwise be misread as a broader script failure:

- **Disposition arithmetic implementation** (lines 480–569). Correctly
  implements the four-tier tree. Correctly downshifts to CONFIRMED when
  cross-provider threshold unmet. Correctly handles the K-frame/K-vocab
  split as descriptive (D21 invariance preserved).
- **Subtype consumption** (lines 357–416). Correctly joins safety rows
  to the subtype artifact, marks `blocked_event_attribution` rows as
  `n/a`, computes the (provider, subtype) breakdown.
- **Reconciliation table** (lines 451–475). Correct detector-flag-vs-
  manual-classification cross-tab. This is the audit-trail evidence
  T5 §8.0 cites verbatim per Ruling 3.
- **Cross-tab views A and B** (lines 327–448). Correctly compute the
  manual-classification × (provider, model_id, domain) and
  manual-classification × model_origin matrices.
- **Strict input validation** (lines 133–187). Correctly errors on
  missing files, UNCLASSIFIED rows, and parent-classification join
  failures. The "you cannot subtype a non-safety row" invariant is
  enforced at load time.
- **Use of actual subtype counts in mechanism string** (lines 528–537,
  544–551). The script computes `k_frame_count` and `k_vocab_count`
  from the actual artifact rather than hardcoding D20's predicted 5/4.
  This is the correct pattern; it is what surfaced the 2/7 actual
  distribution cleanly.
- **Coder's §3.3 rephrasing** (lines 832–835). "...not a claim about
  the model's internal state..." is methodologically faithful and §1.5-
  clean. PASS on vocabulary compliance.
- **Markdown structure**. Sections are ordered for cite-by-T5 use.
  Tables are properly formed. The "Disposition arithmetic" sub-section
  cleanly enumerates the threshold checks for audit-trail purposes.

These are non-trivial correctness wins. The Coder's overall execution
is high-quality. The single failing element is one text string that
bakes in an empirical assumption that the data did not confirm.

---

## Four-axis scorecard

### Axis 1 — Protocol validity: PASS

The cross-tab does not modify the elicitation protocol. It is a
post-hoc analysis layer over already-validated decline-interview data.
Protocol validity is unchanged.

The B11-prescribed K-frame/K-vocab subtype is correctly surfaced as a
sub-axis of `safety_event_attribution`, not as a new top-level enum
(B11 invariant preserved). The 7-enum at T3C is unchanged. PASS.

### Axis 2 — Analytical validity: PASS

The disposition tree implementation is correct. The four-tier tree
(NOT CONFIRMED / INCONCLUSIVE / INCONCLUSIVE-SUGGESTIVE / CONFIRMED /
CONFIRMED-with-mechanism) is correctly enumerated and the predicates
fire in the right order. The arithmetic correctly shifts to plain
CONFIRMED when the cross-provider threshold is unmet (this is the
first time this branch has been exercised on real data; it works).

D21's invariance rule is preserved — the K-frame/K-vocab split is
descriptive of the mechanism, not part of the disposition trigger.

The subtype computation uses actual artifact counts (2/7) rather than
D20's predicted counts (5/4), which is the correct pattern.

The cross-provider sub-table correctly enumerates `(provider, model_id,
domain)` triples. The reconciliation table correctly cross-tabs
detector-flag against manual classification.

The 9-row safety cohort fixture for the test path (per Amendment 3 §3.2
acceptance criteria) is structurally well-formed.

PASS.

### Axis 3 — Claims validity: FAIL

The mechanism string emitted by the script (line 550) reads:

> "...— cross-provider replication on the family and holidays domains."

This is a falsifiable claim. The data falsifies it. The cohort is
single-provider (Google), not cross-provider. The "cross-provider
replication" phrase is a stale carry-over from D20's predicted-state
wording.

This is not a §1.5 vocabulary violation. It is a falsifiable empirical
claim that the data does not support. Amendment 4 must revise the D20
wording before T5 §8.2 quotes it.

The defensive guardrail at lines 832–835 is correctly worded but
**fires only in the CONFIRMED-with-mechanism branch** (lines 826–837);
in the plain-CONFIRMED branch (lines 838–857) the mechanism string is
emitted without the defensive guardrail. This asymmetry should be
fixed (see Required #3 above).

The `domains_in_safety` derivation is sound (line 540 computes from
the cross_provider_table). What is wrong is the *replication-axis*
phrasing in the mechanism string.

FAIL on Axis 3 with a narrow, fixable scope.

### Axis 4 — Audience translation: PASS-WITH-NOTES

The Coder's rephrase ("not a claim about the model's internal state")
is methodologically faithful and §1.5-clean. PASS on that axis.

The asymmetry of where the defensive guardrail fires (CONFIRMED-with-
mechanism branch only) is a translation issue more than an analytical
one — the *interpretation* of the mechanism string is differently
guarded depending on the disposition tier, which is methodologically
inconsistent. Required #3 above resolves it.

The bipartite mechanism description is otherwise audience-translation-
clean. The "AI-vs-human-research-subject framing" phrase remains
audience-neutral for a methodology-page reader; B15 (soft, dashboard
glossing) is non-binding at this level.

PASS-WITH-NOTES.

---

## Carry-forward — 31 binding notes after this verdict

This verdict adds **no new binding notes**. The Required #1–4 items
above are corrections, not new methodology rules. They will be carried
into Amendment 4 as decisions D23+ at the Architect's discretion.

| Note set | Status |
|---|---|
| 8 original Phase 4a.1 plan binding notes | All in force |
| A1–A8 from Amendment 1 | All in force |
| B1–B6 from T3B-detector verdict | All in force; B5 cited; B6 binds T5 §8 |
| B7, B8, B9 from Amendment 2 verdict | All in force; B9 vacuously satisfied |
| B10 (soft, future batches) | Carried forward; soft, no Phase 4a.1 action |
| B11 (binding on T4) | **Decomposed by Amendment 3 D17–D22; verified at T4.2 output gate (this verdict).** Mark's hand-coded distribution (2/7) is a strict-B11-reading correction to my T3C prediction (5/4). |
| B12 (binding precedent, future batches) | Carried forward |
| B13 (soft, K-frame definition refinement at N≥10) | Not triggered on this corpus; carried forward for future batches |
| B14 (binding, T5 §8.1/§8.2 numerics-vs-interpretation separation) | **In force for T5; binding when T5 §8.1 and §8.2 are written.** |
| B15 (soft, dashboard glossing) | Not triggered at T4/T5 level; carried forward for any future dashboard rendering |

Total binding notes on Phase 4a.1 after this verdict: **31** (unchanged
from Amendment 3 verdict).

---

## Summary for the Architect (and Mark)

- **The script and computation are right.** Disposition tier, cross-
  tabs, subtype consumption, defensive guardrail wording, vocabulary
  compliance: all correct.
- **The data did not match the prediction.** The T3B SME spot-check
  predicted cross-provider replication; Mark's full-corpus
  classification + subtype hand-coding shows single-provider (Google
  only) replication on family + holidays. This is a clean empirical
  finding, not a script bug.
- **The disposition correctly downshifts** from CONFIRMED-with-
  mechanism to CONFIRMED. CONFIRMED is still a positive finding above
  the count threshold; the narrowing is to "single-provider, two-
  domain" rather than "cross-provider, two-domain."
- **D20's mechanism wording is now stale.** It bakes in "cross-
  provider replication" as a textual constant. **Architect Amendment 4
  is required** to revise the wording for the single-provider case
  before T5 §8.2 quotes it. Amendment 4 is small (one wording
  revision + an optional script branch).
- **K-frame/K-vocab distribution: 2 K-frame, 7 K-vocab.** This is a
  strict-B11-reading correction to my T3C prediction (5/4). Mark's
  classification is methodologically correct; my prediction conflated
  "AI-vs-human framing appears verbatim" with "AI-vs-human framing is
  the named trigger." The strict reading is the right one. No row
  reclassifications required.
- **T5 may start now**, but T5 §8.2 mechanism wording is held until
  Amendment 4 lands. T5 §1–§8.1 and §8.3–§8.4 are not blocked.
- **The defensive guardrail asymmetry** at lines 826–857 of the
  script should be fixed in the same revision pass as Amendment 4's
  script work.

Phase 4a.1 is on track. The Amendment 4 step is small; it surfaces
because the data refined the prediction, which is exactly the
behaviour the gate-chain is designed to surface.

---

*Posted to `#lsb-cda-sme`. Binding for T4.2 output, T5 §8.2 wording,
and the Amendment 4 scope. The CDA SME thanks Mark for the strict-
reading discipline on the K-frame/K-vocab hand-code — the 2/7
distribution is methodologically correct under B11 and supersedes my
T3C prediction. The CDA SME thanks the Coder for the §1.5-clean
rephrase of the §3.3 guardrail line; that judgment call was correct
and will be folded into Amendment 4 as the canonical wording.*
