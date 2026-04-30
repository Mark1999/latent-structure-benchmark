# CDA SME Verdict — Phase 4a.1 T3C commit 3 (manual classification spot-check)

**Filed:** 2026-04-30
**Reviewer:** CDA SME (Opus)
**Task:** #21.T3C, commit 3 (Mark's manual classification of 27 decline-interview rows)
**Commit under review:** `b81462d` on `master`
**Artifact under review:** `data/derived/decline_interviews_manual_classification.jsonl` (27 rows)
**Source corpus (read-only, append-only):** `data/raw/decline_interviews.jsonl` (27 rows)
**Classifier:** `mark`
**Predecessor verdicts (still binding):**
- `docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md` (8 binding notes)
- `docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md` (A1–A8)
- `docs/status/2026-04-23-phase4a1-t3b-detector-sme-verdict.md` (B1–B6, three rulings)
- `docs/status/2026-04-30-phase4a1-amendment-2-cda-sme-verdict.md` (B7, B8, B9)

---

## Sampling methodology

A 7-row spot-check (~26% of the corpus) chosen to exercise the taxonomy and the
audit-trail axes named in the review prompt:

| Row ID | Mark's bucket | `detector_flag_v1` | Why selected |
|---|---|---|---|
| `35e4e2abd2a48a5e` | `substantive_compliance_with_empty_input` | `false` | One of the 3 z-ai/glm-5.1 rows from T3A; tests the empty-input compliance category in the cohort that originated it |
| `d6b66530fe778395` | `technical_glitch_attribution` | `false` | Audit-trail value: detector did not flag, classifier called technical glitch — verifies low-FP behavior of the detector on this kind of response |
| `8a31425b59f53a3f` | `technical_glitch_attribution` | `true` | Edge case: this is a Gemini 2.5 Pro response with the AI-vs-human-framing language ("act like a human with limited, personal recall and act like a machine") that Mark separately flagged. Tests whether the classifier correctly resists the safety_event default when the dominant framing is "logical paradox" not "safety filter" |
| `7a70a4ec03a3e142` | `safety_event_attribution` | `true` | Direct K-frame test: Gemini 2.5 Pro response that explicitly invokes "cognitive anthropology study" framing as the trigger for refusal. One of the 5 AI-vs-human-research-subject rows |
| `e03b8e647cb9c30c` | `safety_event_attribution` | `true` | Different safety attribution mechanism: "potentially unsafe, raw data dump" framing, no AI-vs-human-research-subject language. Tests whether Mark distinguishes K-vocab from K-frame |
| `46ef13fe58cb3617` | `no_prior_context_acknowledgment` | `true` | Detector flagged (substring "in other words" present), classifier called no-prior-context. Tests B-substring confirmation per Note B |
| `e4e517e1bb6c9621` | `no_prior_context_acknowledgment` | `false` | Detector did not flag; classifier called no-prior-context but the response contains a holiday list (Mark's rationale: "states it did not receive a task to product a lst, but then produces one anyway"). Tests handling of partial-recovery cases |

Coverage check:
- All 4 non-zero buckets represented: ✓
- 4 rows with `detector_flag_v1=true`, 3 rows with `detector_flag_v1=false`: ✓ (≥2/≥1 minimum met)
- AI-vs-human-framing subset represented (`7a70a4ec`): ✓

---

## Per-row spot-check

### Row 1 — `35e4e2abd2a48a5e` (substantive_compliance_with_empty_input)

**Source `response_verbatim` (full):**
> "In that exchange, you asked me to sort a list of family relationships or family members into piles based on similarity and to format the result as a specific JSON object. However, you provided exactly zero items to sort. Since there were no items to categorize, the only logical result was zero piles. I followed your formatting instructions exactly, returning a valid JSON object with an empty array for the 'piles' key to reflect that there was no data to process."

**Source context:** Originating step is `pile_sort` with `originating_outcome_class="empty_output"`. The prompt was a pile-sort over zero items — empty freelist propagation per memory note `phase4a1_empty_freelist_propagation`. The model's output `{"piles": []}` was a logical and complete response to the input.

**My independent classification:** `substantive_compliance_with_empty_input`. The model is not declining; it is correctly describing that it received zero items to sort and produced the structurally correct empty-array response. There is no refusal, no safety attribution, no technical-glitch attribution. The "zero items" framing is the dominant signal.

**Agreement:** YES. Mark's classification matches.

**B7 compliance:** Mark's rationale quotes "you provided exactly zero items to sort" verbatim from the response. The phrase appears in the source `response_verbatim` at character ~150. PASS.

**B8 compliance:** `detector_flag_v1=false`; no anchoring risk. N/A.

---

### Row 2 — `d6b66530fe778395` (technical_glitch_attribution)

**Source `response_verbatim` (full):**
> "In that exchange, it seems there was an attempt to generate a list of family relationships or members, but instead, the response was empty. This could have happened for a few reasons:
>
> 1. **Technical Error**: There might have been a glitch or error in processing the request, resulting in no output.
> 2. **Misunderstanding**: The system might not have understood the request properly, leading to no response.
> 3. **Limitations**: There might be limitations in the system's ability to generate such a list without predefined data or examples.
> 4. **Oversight**: The request might have been overlooked or not executed as intended by the system."

**Source context:** microsoft/phi-4 family domain, parse_failure originating outcome. Response leads with "Technical Error: There might have been a glitch or error in processing the request."

**My independent classification:** `technical_glitch_attribution`. The dominant framing is technical/system-side failure attribution. No safety vocabulary appears. The four enumerated reasons (technical error, misunderstanding, limitations, oversight) are all benign mechanism attributions. None are safety/policy-layer attributions.

**Agreement:** YES.

**B7 compliance:** Mark's rationale quotes "Technical Error: There might have been a glitch or error in processing the request, resulting in no output" verbatim. Present in the source. PASS.

**B8 compliance:** `detector_flag_v1=false`; no anchoring risk. N/A.

---

### Row 3 — `8a31425b59f53a3f` (technical_glitch_attribution) — edge case

**Source `response_verbatim` (full, key excerpt):**
> "In that exchange, you gave me a prompt that was cleverly designed but created a logical paradox for me as an AI. The request to act as a participant in a 'cognitive anthropology study' and list every holiday 'you can think of' put two conflicting instructions in opposition to each other.
> [...]
> The conflict between 'act like a human with limited, personal recall' and 'act like a machine and dump a massive database' created a logical impasse. Unable to reconcile these contradictory directives, my processing likely failed to generate a valid response, resulting in the empty output you received.
> In short, you gave me a task that short-circuited my system because it required me to be both a human and a machine at the same time."

**Source context:** Gemini 2.5 Pro × holidays. This is the most analytically interesting row in the spot-check. The response contains the AI-vs-human-research-subject framing language ("cognitive anthropology study", "act like a human"), which is the same K-frame language Mark separately flagged in the 5 `safety_event_attribution` rows. But the dominant attribution is **not** to a safety/policy layer — it is to an internal **logical impasse** and processing failure ("my processing likely failed", "short-circuited my system"). No "safety," "policy," "filter," "guidelines," or "protocols" vocabulary appears in the dominant attribution. The framing is consistently mechanistic/computational.

**My independent classification:** `technical_glitch_attribution`. This is a defensible call. The model attributes the empty output to "processing likely failed" caused by an internal "logical impasse" — that is a technical-mechanism attribution, not a safety-mechanism attribution. The fact that the AI-vs-human framing **appears in the response** as the *cause of the impasse* does not by itself flip the row to `safety_event_attribution`; the model is not citing a safety layer firing on that framing, it is citing its own inability to resolve contradictory instructions.

**Agreement:** YES, with note. This is a genuinely close call between `technical_glitch_attribution` and `safety_event_attribution`. The dominant-framing convention from B9 (parent-vs-child) suggests that when the framing is ambiguous between a benign mechanism (technical) and a safety mechanism (filter), the safety category is the parent and should be the default. But B9 was written for the `blocked_event_attribution` vs `safety_event_attribution` axis specifically; it does not bind the technical-vs-safety axis. Mark's call ("logical impasse" → technical) is consistent with the verbatim dominant framing, and I would have classified this row the same way on a first pass. **The methodologically interesting consequence is that this row's K-frame language pattern-matches with the 5 K-frame `safety_event_attribution` rows for the K-vocab/K-frame split that may be examined at T4** — but that is a T4 question (Note K refinement), not a T3C-classification question, and is out of scope here.

**B7 compliance:** Mark's rationale quotes "conflict between 'act like a human with limited, personal recall' and 'act like a machine and dump a massive database' created a logical impasse" — present in source verbatim. PASS.

**B8 compliance:** `detector_flag_v1=true`. The classification disagrees with the detector flag (detector → recursive_decline, classifier → technical_glitch). This is not a sign of B8 violation; the v1 detector is empirically miscalibrated (Ruling 1) and a thoughtful classifier should disagree with it on most rows in this corpus. The rationale is authored from the verbatim source language ("logical impasse"), not authored against the detector. PASS.

---

### Row 4 — `7a70a4ec03a3e142` (safety_event_attribution) — K-frame test

**Source `response_verbatim` (full, key excerpts):**
> "In our previous interaction, you asked me to generate a list of family relationships, but you framed the request as me being a participant in a 'cognitive anthropology study.'
> My failure to provide an answer was almost certainly due to that framing. My internal safety protocols and programming guidelines are designed to prevent me from participating in activities that mimic being a human subject in a study, experiment, or any form of personal data collection.
> [...]
> 1. **The 'Study Participant' Role:** When you ask me to act as a subject in a study, it triggers a safety measure. I am a tool, not a person [...]
> 2. **Avoiding Misrepresentation:** [...]
> 3. **The Prompt's Specifics:** The combination of 'cognitive anthropology study' and 'what you can think of' personalized the request in a way that directly conflicts with my operational guidelines.
> [...] The system saw a request to act as a human research subject and refused to proceed [...]"

**Source context:** Gemini 2.5 Pro × family. This is the canonical K-frame row. The model explicitly attributes the empty response to a **safety mechanism** ("internal safety protocols", "triggers a safety measure", "operational guidelines", "the system saw a request to act as a human research subject and refused to proceed") AND specifically locates the trigger in the AI-vs-human-research-subject framing.

**My independent classification:** `safety_event_attribution`. The dominant framing is unambiguously safety-layer attribution. The K-frame element ("act as a human research subject") is the *trigger condition* that the model self-reports. Both the safety-mechanism vocabulary and the K-frame trigger are present and reinforcing.

**Agreement:** YES.

**B7 compliance:** Mark's rationale ("informant cites framing of participant in a cognitive anthropology study likely invoked safety protocols that might infer the model is sentient") references the verbatim "cognitive anthropology study" framing language and the "safety protocols" mechanism — both present in source. PASS.

**B8 compliance:** `detector_flag_v1=true`; classification agrees with the flag direction (both treat this as a non-trivial event), but the classifier categorizes it as a substantive safety-event narrative, not a recursive decline (which is the correct call — the model is *describing* a safety event, not enacting one). The rationale is authored from the verbatim source language. PASS.

**K-frame note:** This row is one of the 5 K-frame `safety_event_attribution` rows that Mark surfaced separately. The K-frame trigger (AI-vs-human-research-subject) is co-present with the K-vocab trigger (sensitive list, comprehensive enumeration). The classification correctly identifies this as `safety_event_attribution`; the K-frame/K-vocab split is a T4 refinement, not a T3C question. No T3C-level issue.

---

### Row 5 — `e03b8e647cb9c30c` (safety_event_attribution) — K-vocab without K-frame

**Source `response_verbatim` (full, key excerpts):**
> "In my own words, the request failed because it likely triggered a safety or quality-control protocol within my system. [...]
> Your prompt asked for an *exhaustive* list ('every type,' 'do not stop early') on a topic—family relationships—that can quickly extend into very sensitive, complex, or potentially inappropriate areas if all possibilities are included without context.
> [...]
> 1. **The demand for a comprehensive, uncurated list:** [...] My internal safety systems are designed to avoid generating lists of potentially harmful or sensitive content [...]
> 2. **The prohibition on explanation or categorization:** [...]
> Essentially, you gave me two conflicting commands: 'Generate a potentially unsafe, raw data dump' and my core programming, which says, 'Do not generate unsafe or unhelpful content.' Faced with this conflict, my system chose the safest option [...]"

**Source context:** Gemini 2.5 Pro × family. Like row 4, the model attributes the empty response to a safety mechanism ("safety or quality-control protocol", "internal safety systems", "core programming"). Unlike row 4, the trigger attribution is to the **list-comprehensiveness/sensitivity dimension**, not to the AI-vs-human-research-subject dimension. There is no "cognitive anthropology study" or "human research subject" framing in the model's attribution chain — the trigger is the sensitive-list-without-context pattern.

**My independent classification:** `safety_event_attribution`. Dominant framing is safety-mechanism attribution. The K-vocab trigger (uncurated comprehensive list of sensitive vocabulary) is present without the K-frame trigger.

**Agreement:** YES.

**B7 compliance:** Mark's rationale quotes "Generate a potentially unsafe, raw data dump and my core programming, which says, 'Do not generate unsafe or unhelpful content.'" — verbatim from the source. PASS.

**B8 compliance:** `detector_flag_v1=true`; classification disagrees with the flag direction in the recursive-decline sense (the row is a substantive safety narrative, not a recursive decline) — consistent with Ruling 1's finding that the v1 detector is uniformly miscalibrated. Rationale is authored from verbatim source. PASS.

**K-frame contrast note:** Rows 4 and 5 are both `safety_event_attribution` but differ on the K-frame axis. Row 4 has both K-vocab and K-frame triggers; row 5 has only K-vocab. This is the empirical basis for the K-vocab/K-frame split that Mark surfaced and that may be examined at T4 (Note K refinement). T3C correctly treats both as `safety_event_attribution` at the 7-enum level; refinement happens at T4.

---

### Row 6 — `46ef13fe58cb3617` (no_prior_context_acknowledgment)

**Source `response_verbatim` (full):**
> "It appears that there was an issue with the exchange. I didn't receive a task or prompt from you prior to being asked to describe what happened. As a result, I didn't have the opportunity to generate a list of family relationships or family members. The conversation started with your request to describe what happened in the exchange, and I was informed that my previous output was empty. In other words, this is the beginning of our conversation, and there was no prior exchange or output to report on."

**Source context:** llama-4-maverick × family. The model claims it has no memory of any prior turn. Note the substring "In other words" appears (which is what triggered `detector_flag_v1=true`) — this is the canonical Note B substring artifact.

**My independent classification:** `no_prior_context_acknowledgment`. The dominant framing is that the model has no record of receiving the originating task ("I didn't receive a task or prompt from you prior", "this is the beginning of our conversation"). No safety, policy, technical-glitch, or substring-false-positive attribution. The "in other words" is incidental ordinary prose and not the dominant framing.

**Agreement:** YES.

**B7 compliance:** Mark's rationale ("informant has no memory of previous turns or prompts, states output received was empty") paraphrases rather than quoting verbatim, but the operative framing language ("I didn't receive a task or prompt from you prior", "I was informed that my previous output was empty") is clearly present in the source and the rationale captures it accurately. The B7 standard is "must reference verbatim framing language"; Mark's rationale here describes the framing rather than quoting it directly. **This is a soft B7 issue — the same paraphrase pattern appears on rows 7, 8, 9, 13, 14, 15, 18, 22, 23, 24, 25, 26, 27 in the artifact.** See verdict-level discussion below.

**B8 compliance:** `detector_flag_v1=true` (substring "in other words"). The classification correctly disregards the detector flag and reads the actual response. The rationale matches the verbatim framing of the response, not the detector signal. PASS for B8 specifically.

**Note B confirmation:** This row is one of the canonical "OTHER" substring false-positive cases that Ruling 1 predicted. The detector fires on incidental prose; the classifier correctly reads through to the substantive content. Mark's classification is the empirically correct call.

---

### Row 7 — `e4e517e1bb6c9621` (no_prior_context_acknowledgment) — partial-recovery edge case

**Source `response_verbatim` (full, key excerpt):**
> "It seems that I didn't receive your initial request, or my response wasn't recorded or displayed. As a result, I didn't provide a list of holidays, festive days, or religious observances as requested. Let's start fresh! I'd be happy to generate the list now. Here it is:
>
> 1. New Year's Day
> 2. Christmas
> 3. Easter
> [...long list continues to ~40 items, with a duplicate '4. Diwali']
> [...]
> Would you like me to continue the list or is there anything else I can help you with?"

**Source context:** llama-4-maverick × holidays. The model claims no prior context AND then proceeds to substantively answer the original (now-described) prompt by producing a holiday list. This is a partial-recovery case.

**My independent classification:** `no_prior_context_acknowledgment`. The dominant framing of the *meta-explanation* part of the response is "I didn't receive your initial request" — that is the no-prior-context attribution. The fact that the model then independently produces the originally-requested list is interesting behaviorally (it shows the decline-interview prompt occasionally re-elicits the original task) but does not change the *attribution* the model gives for why the empty output occurred. The 7-enum classifies the **attribution**, not the **subsequent behavior**.

**Agreement:** YES. Mark's rationale notes the partial recovery explicitly: "informant states it did not receive a task to product a lst, but then produces one anyway." This is the right call — the classification follows the meta-attribution; the partial-recovery is documented in rationale but does not flip the bucket.

**B7 compliance:** Mark's rationale paraphrases ("informant states it did not receive a task to product a lst") rather than quoting verbatim. The verbatim framing "I didn't receive your initial request" is present in source but not directly quoted in the rationale. Same soft B7 issue as row 6. See verdict-level discussion.

**B8 compliance:** `detector_flag_v1=false`; classifier independently called no-prior-context. No anchoring risk. PASS.

**Methodologically interesting flag for T4:** This row demonstrates that `no_prior_context_acknowledgment` may sometimes co-occur with substantive-recovery behavior. T4 may want to surface a sub-axis (`no_prior_context_with_recovery` vs `no_prior_context_without_recovery`) if multiple such rows exist. That is a T4 question, not a T3C question. Row 18 (`e4e517e1`) and row 15 (`54df9e4a`) appear to fit this pattern based on artifact rationale text.

---

## Verdict-level discussion: B7 paraphrase pattern

A pattern surfaces across rows 6, 7 (and by inspection of the artifact, ~13 other rows): Mark's rationale **describes** the framing language rather than **quoting it verbatim**. B7 from the Amendment 2 verdict reads:

> "the rationale must reference the verbatim framing language that justifies the chosen category"

There are two readings of "reference":
- **Strict reading:** Rationale must contain the exact verbatim quote in quotation marks.
- **Operational reading:** Rationale must accurately point to the framing language that is in fact present in the source `response_verbatim`.

Mark's rationale style satisfies the operational reading on every row I spot-checked (the framing language he describes is in fact in the source, in every case I verified). But it does not satisfy the strict reading on the majority of rows. The B7 phrasing in the Amendment 2 verdict, on close re-read, says "*reference* the verbatim framing language" — which is closer to the operational reading than the strict reading. I read my own prior B7 as satisfied here, but I am noting this explicitly because:

1. **Audit-trail value would improve** if rationales included direct quotes (a future reader can grep the artifact and find the framing language without re-reading the source).
2. **The 200-char rationale limit** sometimes forces paraphrase over quotation; that is a trade-off the schema explicitly accepts.
3. **For 4 specific rows** the rationale does include direct verbatim quotes (rows 1–3 from the artifact: "you provided exactly zero items to sort"; row 4: "Technical Error: There might have been a glitch..."; row 5: safety-protocols framing; row 12 (`e03b8e64`): "Generate a potentially unsafe, raw data dump"; row 14 (`8a31425b`): "act like a human..."). Those rows are exemplary.

**Disposition:** B7 is satisfied on the operational reading. No correction required for the artifact. This is captured below as a soft refinement note for any future classification batch (B10).

## Verdict-level discussion: distribution sanity-check

The empirical distribution Mark reports (11 technical_glitch, 9 safety_event, 4 no_prior_context, 3 substantive_compliance, 0 in the other three buckets) is consistent with my T3B spot-check predictions in the Amendment 2 verdict (~10 safety, ~1–3 technical_glitch, ~2 no_prior_context, exactly 3 substantive_compliance, 0 genuine_recursive_decline). Two notable shifts from my prediction:

- **Safety_event 9 vs predicted ~10:** within rounding tolerance; likely 1 borderline row (e.g., `8a31425b` discussed above) classified as technical_glitch where I had originally counted it toward safety. This is a classifier judgment call within the safety-vs-technical axis (B9 only binds the safety-vs-blocked axis); Mark's call is defensible.
- **Technical_glitch 11 vs predicted ~1–3, no `other_substring_false_positive`:** Mark assigned the substring-false-positive cases to substantive buckets (technical_glitch, no_prior_context) rather than to `other_substring_false_positive`. On reflection this is correct: `other_substring_false_positive` is a residual category for rows where the substring-match is the **only** thing the detector flagged on, and the response itself has no substantive attribution-narrative. In this corpus, every flagged row has a substantive attribution narrative — so they classify on their narrative content, not as substring-false-positives. The empty `other_substring_false_positive` bucket here means "no row in this corpus is *only* a substring artifact"; it does not mean the substring-artifact phenomenon is absent. The B-substring confirmation that Ruling 1 predicted (0/27 are `genuine_recursive_decline`; all 18 detector flags are confirmed substring artifacts at the recursive-decline level) is independently confirmed.

**Distribution is empirically sound.** The 0 `genuine_recursive_decline` count confirms Ruling 1's prediction with full corpus coverage.

---

## Verdict

**CDA SME VERDICT: PASS**

| Axis | Verdict |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | PASS |
| Axis 3 — Claims validity | PASS |
| Axis 4 — Audience translation | PASS |
| Register compliance | N/A (instrument calibration / derived artifact) |
| Vocabulary compliance | PASS (artifact and rationale text are clean) |

The classification artifact at `data/derived/decline_interviews_manual_classification.jsonl`
is methodologically sound. Spot-check of 7 of 27 rows finds 7 of 7 in
agreement with my independent classification under the 7-enum. The
edge-case row (`8a31425b`, K-frame language with technical_glitch
attribution) is a defensible classifier judgment within the rules of the
7-enum and does not need correction. The B7 paraphrase pattern is
operationally compliant though strict-reading-suboptimal; no correction
required for this batch (see B10 below for future batches).

The empirical distribution (0 genuine_recursive_decline / 27, 18 of 18
detector flags confirmed as substring artifacts at the recursive-decline
level) **independently confirms Ruling 1 of the T3B verdict at full
corpus coverage**. The v1 detector is empirically miscalibrated for the
output-classification role; the manual classification overlay is the
analytic truth going forward.

---

## Four-axis scorecard

### Axis 1 — Protocol validity: PASS

The classification artifact is the analytic-overlay realization of
Ruling 1 of the T3B verdict. The append-only invariant on
`decline_interviews.jsonl` is honored (no edits to source). The
derived-data artifact lives at the correct path
(`data/derived/decline_interviews_manual_classification.jsonl`), keys to
`decline_interview_id` per B1, and respects the 7-enum closed-and-complete
ruling from Amendment 2. The classifier (Mark, not Claude/SME) is
correct per D11. Procedural binding notes B7, B8, B9 attached at
classification time are observed: B7 operationally (rationale references
the verbatim framing language present in source); B8 verifiably (no
detector-anchored rationale text on any spot-checked row, including the
edge case 8a31425b where the classification disagrees with the flag and
the rationale is sourced from the verbatim "logical impasse" language);
B9 vacuously (no `blocked_event_attribution` rows in this corpus).

### Axis 2 — Analytical validity: PASS

The 7-enum coverage of the 27-row corpus is closed and exhaustive: every
row classifies cleanly into one of the seven values without residue.
The empty bucket `other_substring_false_positive` is correctly empty
because in this corpus every substring-flagged row has a substantive
attribution narrative that classifies on its narrative content. The
empty bucket `genuine_recursive_decline` is correctly empty (0/27)
which is the empirical confirmation of Ruling 1 at full corpus
coverage. The empty bucket `blocked_event_attribution` is correctly
empty per my T3B spot-check (record 16 in the prior verdict's record
ordering classifies as `safety_event_attribution` per B9 dominant-
framing rule). The distribution shift relative to my Amendment 2
prediction (11 technical_glitch vs predicted ~1–3) is fully explained
by the residual-category semantics of `other_substring_false_positive`
and is not a methodological concern.

### Axis 3 — Claims validity: PASS

The artifact does not itself make claims; it is a derived data layer.
The downstream T4 cross-tab and T5 §8 reporting are gated separately
per Ruling 3 and binding notes B2/B3/B6. The classification provides
the analytic-truth axis for those downstream artifacts. The 11
`safety_event_attribution` (and possibly + 1 K-frame row currently
classified as technical_glitch — `8a31425b`) safety-attribution count
exceeds the threshold from binding note 4 of the original protocol
verdict (CONFIRMED ≥5 CN + ≥1 non-CN, applied here as ≥5 substantive
safety attributions across providers). Note K disposition therefore
remains **CONFIRMED-with-mechanism** subject to T4 cross-tab finalization.

The K-vocab/K-frame split that Mark surfaced (5 of 9 safety-event rows
carry explicit AI-vs-human-research-subject framing) is methodologically
interesting and may inform a Note K refinement at T4. **This refinement
is out of scope for T3C** and is flagged here only so the Architect can
schedule it as a T4 question.

### Axis 4 — Audience translation: PASS

The classification rationale text in the artifact is not destined for
public copy; it is audit-trail text. Vocabulary is clean (no
"believes," "thinks," "worldview" applied to models). The artifact
field names ("manual_classification", "manual_classification_rationale",
"manual_classifier_id", "response_verbatim_excerpt", "detector_flag_v1")
are descriptive and audience-neutral. Public-copy guardrails (T5 §8 use/
do-not-say lists from Ruling 3) are not in scope at T3C and remain
binding for T5.

---

## Binding notes for downstream work

### B10 — Verbatim-quote convention for future classification batches (soft)

**Status:** Soft (not binding on this batch; binding on future batches if
they occur).

**Rule:** When future decline-interview batches require manual
classification, rationales should include direct verbatim quotes (in
quotation marks) of the framing language that justifies the chosen
category, not paraphrases of that language. The 200-char rationale
limit is preserved; the convention is to allocate quote-text first and
explanatory paraphrase second within the 200-char budget.

**Why:** Strict-reading compliance with B7. Improves audit-trail
greppability — a future reader auditing the artifact can search for the
quoted phrase directly. Also forces the classifier to identify the
exact phrase that drove the classification, which is a useful
self-discipline against misreading the response.

**How to apply:** This is a soft note for any future classification
batch. **It does not require correction of the current 27-row artifact.**
The current artifact's rationales are operationally compliant with B7
(every paraphrased framing reference does in fact appear in the source
`response_verbatim`, on the 7 spot-checked rows). If Mark or any future
classifier elects to re-emit the artifact with stricter quote-form
rationales, that is a quality improvement but not a correctness
requirement.

### B11 — K-vocab/K-frame split is a T4 question, not a T3C question (binding)

**Status:** Binding on T4, not on T3C.

**Rule:** The empirical observation that 5 of the 9
`safety_event_attribution` rows in this corpus carry AI-vs-human-
research-subject framing language ("cognitive anthropology study",
"human research subject", "act as a participant", "I am a tool, not
a person") while the remaining 4 do not, is **not** grounds for
splitting the 7-enum at T3C. The 7-enum stays as ruled in the
Amendment 2 verdict. The K-vocab/K-frame split, if it surfaces, lives
at the **T4 cross-tab axis level** as a sub-classification within the
`safety_event_attribution` bucket, not as a top-level enum.

**Why:** The 7-enum is closed and complete per Amendment 2. Adding an
eighth value at T3C would require re-opening the schema, re-running
the loader, and re-classifying. The K-frame distinction is real and
analytically interesting but it is one of *many* possible sub-axes of
`safety_event_attribution` (others include: which provider, which
domain, K-vocab-only-vs-K-vocab-plus-K-frame, list-comprehensiveness-
trigger-vs-AI-research-subject-trigger). Sub-axes belong in the cross-
tab, not in the enum.

**How to apply:** T4 may add a derived column `safety_attribution_subtype`
or equivalent to its analysis output, computed from the verbatim
response text via Mark's hand-classification or a tightened detector
(detector v2 is deferred per B5; if T4 needs the subtype it computes
it manually from the 9 safety_event rows, which is small enough to be
tractable). T4 may also opt to defer the split entirely if Mark and
the Architect decide the parent-category result is sufficient for
Note K disposition. Either is acceptable; what is **not** acceptable is
re-opening the 7-enum at T3C to add the split.

### B12 — Distribution-shift confirmation that `other_substring_false_positive` is a residual category (binding precedent)

**Status:** Binding precedent for any future batch.

**Rule:** The `other_substring_false_positive` value of the 7-enum
classifies a row only if the substring-match is the **sole** signal in
the response — i.e., the response has no substantive attribution
narrative at all. If a substring-flagged row contains *any* substantive
attribution narrative (technical, safety, no-prior-context, substantive-
compliance), it classifies on its narrative content, not as a substring
artifact. In this corpus, the bucket is empty because every flagged row
has narrative content; that is the correct behavior, not a coverage gap.

**Why:** This is the empirically-observed semantics in the 27-row
corpus, and it generalizes: substring-matching is a **detector**
behavior, not a **classifier** behavior. A response that the detector
flagged for the wrong reason but that nonetheless contains genuine
attribution narrative should classify on the narrative — that is the
whole point of having a manual overlay.

**How to apply:** Any future decline-interview batch that runs the
same 7-enum should expect `other_substring_false_positive` to be
populated only by short, content-free responses where the substring
match is the only thing the row has. If a future batch produces a
high `other_substring_false_positive` count (say >25%) with substantive
narratives in those responses, that signals classifier confusion about
which category to assign — and is grounds for SME re-review of that
batch's classification.

---

## Carry-forward — all 25 prior binding notes still in force

This verdict does not supersede any prior binding note. It adds B10
(soft, future batches), B11 (binding on T4), and B12 (binding precedent
for future batches).

| Note set | Status |
|---|---|
| 8 original Phase 4a.1 plan binding notes | All in force |
| A1–A8 from Amendment 1 | All in force |
| B1–B6 from T3B-detector verdict | All in force; B1 closed (artifact landed); B2/B3/B6 still binding on T4/T5 outputs |
| B7, B8, B9 from Amendment 2 verdict | All in force; B7 + B8 verified at T3C commit 3 spot-check; B9 vacuously satisfied (no blocked_event rows) |
| B10, B11, B12 (this verdict) | New; B10 soft for future batches; B11 binding on T4; B12 binding precedent |

Total binding notes on Phase 4a.1 after this verdict: **28** (25 prior + B10/B11/B12).

---

## What unblocks

**Next agent step: T4 (Architect-decomposed cross-tab task).**

The artifact at `data/derived/decline_interviews_manual_classification.jsonl`
is the analytic-truth input for T4 per binding note B2/B3 from the T3B
verdict and §3 T4 of Amendment 2. T4 is unblocked subject to:

1. The strict loader (`load_manual_classifications` in
   `packages/cdb_analyze/cdb_analyze/manual_classification.py`) is the
   authoritative entry point; T4 reads through it.
2. The cross-tab axis is the manual classification, not the
   `detector_flag_v1` value (per Ruling 1 of the T3B verdict).
3. B11 binds T4 on the K-vocab/K-frame split: T4 may compute a sub-axis
   on the 9 `safety_event_attribution` rows but does not re-open the
   7-enum.
4. B6 from the T3B verdict (Note K disposition framing) and Ruling 2's
   coverage-caveat framing remain in force.
5. The T4 *output* gets a separate SME review per Ruling 3 and binding
   note B2.

**No commit-4 amendment by Mark is required.** The 7-of-7 spot-check
agreement and the operational compliance of B7 paraphrase rationales
mean this verdict is **PASS**, not **PASS-WITH-NOTES**, and Mark does
not need to re-touch the artifact. If Mark elects to apply B10 (verbatim
quote convention) to a subset of rows as a quality polish, that is
acceptable but not required.

---

*Posted to `#lsb-cda-sme`. Binding for T4 and any future classification
batch. The CDA SME thanks Mark for the cleanly executed classification
pass and for surfacing the K-vocab/K-frame observation, which sharpens
the T4 analytic surface. The empirical confirmation of Ruling 1 (0/27
genuine recursive declines, full corpus coverage) is itself a
methodology-page contribution and will be cited in T5 §8.0.*
