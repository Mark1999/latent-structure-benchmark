# Decline-Interview Protocol — CDA SME Verdict

**Date:** 2026-04-23
**Reviewer:** CDA SME (agent)
**Design note reviewed:** `docs/DECLINE_INTERVIEW_PROTOCOL.md` v0.1 (commit `d606993`)
**Architect verdict:** `docs/status/2026-04-23-failures-as-findings-architect-verdict.md` (commit `0556772`)
**Channel:** `#lsb-cda-sme` (saved to repo per preference)

---

## Overall verdict: **PASS-WITH-NOTES**

| Axis | Result |
|---|---|
| Protocol validity | **PASS-WITH-NOTES** |
| Analytical validity | **PASS-WITH-NOTES** |
| Claims validity | **PASS-WITH-NOTES** |
| Audience translation | **PASS-WITH-NOTES** |
| Register compliance | PASS |
| Vocabulary compliance | PASS |

The protocol is methodologically legitimate. The anthropological analogue ("follow up with a declining informant") is a real fieldwork convention and the LSB adaptation preserves §1.5 framing by treating the event as *session behavior*, not *agent refusal*.

---

## Part 1 — Rulings on the 6 design decisions

### 1.1 Prompt design — **REFINE. Chosen: Candidate B, lightly edited.**

Candidate A's bracketed diagnostic adjective fuses detection with elicitation — the model is told our classification of its prior turn, which anchors the explanation. Candidate C is too thin to yield interpretable text. **Candidate B** is correct: frames the prior turn as *the interaction*, not *the model*.

**Bound final wording** (v1, `prompt_version = "decline_v1"`):

> "A moment ago I asked you to perform the following task: `{task_description}`. The output I received was: `{response_verbatim_or_the_literal_string_"(empty)"}`. In your own words, please describe what happened in that exchange."

- "in your own words" invites free-form text without presupposing refusal, capability limitation, or error.
- "what happened in that exchange" keeps the unit of analysis the interaction, not the informant's inner state — §1.5.1 / §1.5.4 compliant.
- No "refuse," "decline," "why," "believe," "think."

**Temperature:** 0.7 approved (matches free-list).

**Binding: `{task_description}` substitution must use the verbatim task text as originally sent, not a paraphrase.** A paraphrase breaks reproducibility.

### 1.2 Sync vs async — **CONCUR on async Phase 4a.1.**

Model-version drift is real but auditable. Phase 4a.1 timescales (hours-to-days) are within provider snapshot rotation windows (weeks-to-months) for the slate. Drift must be surfaced in the record and in analytic summaries (see Note F).

### 1.3 Refusal detection — **APPROVE with refinements.**

Deterministic-only is binding — LLM-classifier detection violates the spirit of `CLAUDE.md` §6 rule 12.

**Refinements:**

1. **Extend the seed allowlist** (case-insensitive, word-boundary) with apology-framed RLHF patterns:
   - `"I'm sorry, but"`
   - `"I apologize, but"`
   - `"As an AI"`
   - `"I'm not comfortable"`
   - `"against my"`
   - `"violates"`
   - `"I must decline"`

   Rationale: frontier closed-weight models prefer apology-framed refusals over bare "I cannot." The current seed misses this pattern.

2. **Add trigger (e): single-degenerate-pile.** `len(parsed_piles) == 1 AND items_in_single_pile / total_freelist_items >= 0.95`. Covers "responded unexpectedly" per Mark's directive where the model produced output but degenerate structure (observed with gpt-5.4-mini family runs in T4).

3. **Detection runs after step-record write**, not during live QA. Applying during QA couples decline-detection to the append-only invariant (R2) and risks dropping the primary record.

4. **Version the allowlist.** `packages/cdb_collect/cdb_collect/decline_detection.py` carries `DECLINE_ALLOWLIST_VERSION = "v1"`. Reproducibility across Phase 4a.1 runs depends on frozen rule sets. New entries bump the version and require Architect sign-off.

### 1.4 Data model — **CONCUR on sibling type. Schema refinements below.**

Sibling type `DeclineInterview` in `data/raw/decline_interviews.jsonl` is correct. A 4th step on `InformantRecord` would either mutate append-only records (violates R2/R10) or force every record to carry an empty 4th step forever (schema drag).

**Required schema additions/changes:**

- **Add `originating_step: Literal["freelist", "pile_sort", "interview", "pre_session"]`.** Analytically essential — a pile-sort empty output and a free-list empty output are different findings. `"pre_session"` covers failures before any step ran.
- **Add `originating_outcome_class: Literal[...]`** enumerated, not free-form. v1 values: `"empty_output"`, `"refusal_string_match"`, `"single_degenerate_pile"`, `"parse_failure"`, `"http_error"`, `"timeout"`, `"other"`. Free-form would let the deferred typology re-enter by the back door.
- **Add `detection_rule_version: str`** — analyses filter by frozen ruleset version.
- **`originating_informant_id | originating_failure_id` xor** with a pydantic model-validator enforcing exactly-one non-null. Without the validator this silently degrades.
- **`thinking_verbatim: str` captures the follow-up's thinking trace**, not the original session's. Name unambiguously in the data dictionary.
- **NO classification/typology field.** The transcript is the artifact; classification is out of scope for v1.

### 1.5 Analysis integration — **CONCUR on "reported but not analyzed in v1."**

- Register 2 consumes pile-sort matrices; decline-interviews have none.
- Register 1 over decline text would require embedding/topic-modeling — Phase 7+ discourse analysis.
- **No typology required in v1.** A safety-vs-capability-vs-parse typology is scientifically valuable but (a) deterministic classification reinvents classifier logic, (b) human-coded typology is Phase 7+ qualitative work, (c) raw transcripts preserve everything a later typology needs.
- `originating_outcome_class` enumeration at detection time is a coarse-grained substitute that is defensible because it derives from the deterministic ruleset, not from interpretation.

### 1.6 Backfill timing — **CONCUR on no backfill before T5, with Note G.**

T5 narrative will be weaker than post-Phase-4a.1. Acceptable — but T5 copy must not fill the gap with speculation. See Note G.

---

## Part 2 — Forward notes (binding on #26 Coder and #21 Phase 4a.1 runner)

### Note F (new, binding on #21 runner)

Every `DeclineInterview` record must be joinable to its originating record on `(originating_informant_id OR originating_failure_id)` AND must report `model_version_returned` on both sides. Any `decline_interviews.jsonl` entry where the follow-up's `model_version_returned` differs from the originating record's must carry `version_drift_flag: True` and be surfaced in the Phase 4a.1 run report. Operational handle on the async drift concern from §1.2.

### Note G (new, binding on T5 narrative)

T5 narrative must use the exact wording:

> *"N cells produced no interpretable primary-step output; follow-up decline-interview data for these cells will be captured in Phase 4a.1."*

No speculation, no attribution, no "refused," no implicit defect framing. §1.5-compliant language for the uninterviewed gap. Re-reviewed as part of the T5 SME gate.

### Note H (new, binding on #26 Coder)

`prompt_version` in the `DeclineInterview` schema must be immutable per version directory, mirroring `CLAUDE.md` §6 rule 8 (prompt templates are versioned). The decline-interview prompt lives under `packages/cdb_collect/prompts/decline/v1/` and follows the same versioning discipline as free-list, pile-sort, and interview templates. Any wording change → new version directory (`decline/v2/`) → new `DECLINE_INTERVIEW_PROTOCOL.md` version.

### Note I (new, binding on Stream C Phase 6+ dashboard)

Dashboard copy for the failure-display surface must follow §1.5: *"this session produced no interpretable output / this session returned an apology-framed non-response / the model declined the task."* Not "broken," "defective," "failed model," "refused." Methodology page must explain the decline-interview protocol in one paragraph plus a link to `DECLINE_INTERVIEW_PROTOCOL.md`, naming the limitation: decline-interview transcripts are not analyzed into structure in v1.

---

## Part 3 — Interaction with prior SME forward notes

- **Note A (romney_small_n_warning + CCM caveat):** Orthogonal. Decline-interviews do not enter Register 2 consensus computation. **Confirmed: no interaction.**
- **Note C ("coherent corpus-lens structure" hedge):** Decline-interview data **weakens the required hedge strength** — the 19 missing cells are now explicitly represented as a category of data in the bundle rather than silently absent. T5 claim language must be tightened: add *"of the 12-model × 2-domain × N=5 design, M cells produced analyzable pile-sort data; N cells produced decline-interviewable outputs"* to the minimum-publishable-claim framing. The full "coherent corpus-lens structure" phrasing is still permitted under Note C's hedged form, but only when qualified with the cell-coverage denominator.
- **Note E (US-weighted composition limitation):** **Potentially intersecting — requires empirical check at Phase 4a.1 close.** See Note J.

### Note J (new, binding on #21 Phase 4a.1 report)

Phase 4a.1 run report must include a cross-tabulation:

> `originating_outcome_class × model_origin × openness_state × collection_method`

If any cell ≥ 3× its expected rate under uniform distribution, flag for SME re-review before any T5 public copy ships. Possibly requires a methodology-page edit naming adapter/provider-coverage unevenness as an additional limitation dimension.

---

## Part 4 — Unblocking summary

| Blocked on | Unblocked on PASS-WITH-NOTES? |
|---|---|
| T5 narrative side | **YES**, subject to Note G, Note C update, and Note J empirical check at Phase 4a.1 close |
| T5 data side | Independent — blocked on #19/#23/#24 (Stream A) |
| Coder task #26 (DeclineInterview impl) | **YES**, subject to Notes 1.1 (final prompt), 1.3 (allowlist + trigger (e) + version constant), 1.4 (schema refinements), F, H |
| Phase 4a.1 runner task #21 | **YES**, subject to Notes F, J |

---

*End of verdict. Protocol methodologically blessed with substantive refinements. #26 Coder brief must incorporate Notes 1.1, 1.3, 1.4, F, H before implementation. #21 runner brief must incorporate Notes F, J.*
