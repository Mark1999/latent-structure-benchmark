---
name: cr-t7-sme-bound-strings
description: CR-T7 byte-identical SME-bound string drafts (2026-06-10) for the per-record raw-exchange detail surface. N1 picked BLOCK_PILE_INTERVIEW_* prefix; N2 picked disposition (a) drop | None typing, no step-missing fallback string. Coder pastes verbatim, no paraphrasing.
metadata:
  type: project
---

# CR-T7 SME-bound strings (byte-identical, 2026-06-10)

Delivered to Coder as the conditional-PASS-with-notes unlock per project_cr_t7_plan_verdict.md "Posture on Coder dispatch". Coder MAY NOT paraphrase.

## N1 picked: BLOCK_PILE_INTERVIEW_* prefix
The CDA step on `InformantRecord.interview` is renamed in dashboard-facing constants to `BLOCK_PILE_INTERVIEW_*` to disambiguate from the "Follow-up interview" record kind (the post-refusal DeclineInterview surface, badge `BADGE_DECLINE = "Follow-up interview"`).

## N2 picked: disposition (a) drop | None typing
The three top-level step fields on the published detail JSON (`freelist`, `pile_sort`, `pile_interview`) are non-Optional. Required on `InformantRecord` per `cdb_core/schemas.py` L650-652. AC-D7's "suppress whole section when null" branch is removed from the test matrix. No `RECORDS_DETAIL_STEP_MISSING` fallback string is shipped.

## 1. _FRAMING_NOTE_DETAIL

Publish-layer, emitted into every detail JSON. Distinct from `_FRAMING_NOTE` (per-domain summary). N8 byte-identity contract.

```
This record exposes the verbatim bytes the LSB pipeline sent and the verbatim bytes the provider returned for a single collection session. A session has three elicitation steps: a free-list step (LSB asks the model to list items in the domain), a pile-sort step (LSB asks the model to group its own free-list items into piles), and a pile-interview step (LSB asks the model to explain the criteria it used for the pile-sort grouping). Each step is shown below as three sub-blocks: what LSB sent, what the provider returned, and any reasoning trace the provider surfaced. This record is not a transcript of the model's reasoning, intent, or understanding; it is a transcript of the LSB collection step.
```

## 2. RECORDS_DETAIL_FRAMING

Dashboard-side, rendered as in-page caption above the expanded body. Distinct from `_FRAMING_NOTE_DETAIL` (N8).

```
The blocks below show the verbatim bytes exchanged for this collection session, step by step. Each of the three CDA elicitation steps (free list, pile sort, pile interview) is shown as the prompt LSB sent, the response the provider returned, and any reasoning trace the provider surfaced. These are LSB pipeline I/O records, not a window into model cognition.
```

## 3. RECORDS_DETAIL_EXPAND_LABEL

Expand affordance copy. N6: no "answer", no quality-framed verb.

```
Show parsed-step exchange
```

## 4. State strings

```
RECORDS_DETAIL_LOADING = "Loading per-record exchange…"
RECORDS_DETAIL_FETCH_FAILED = "Could not load the per-record exchange for this session. Check that the data file is present."
RECORDS_DETAIL_MALFORMED = "Per-record exchange data for this session could not be parsed."
```

## 5. Nine BLOCK_*_PROMPT / _RESPONSE / _REASONING sub-labels

Parser-state register throughout per N4. Mirrors `BLOCK_PROMPT` / `BLOCK_RESPONSE` / `BLOCK_REASONING` follow-up surface style. "What LSB sent / what the provider returned / what the provider surfaced as reasoning trace" distinction preserved on every step.

### Free-list step
```
BLOCK_FREELIST_PROMPT = "Free-list prompt LSB sent"
BLOCK_FREELIST_RESPONSE = "Provider response to the free-list prompt"
BLOCK_FREELIST_REASONING = "Reasoning trace the provider surfaced on the free-list step"
```

### Pile-sort step
```
BLOCK_PILESORT_PROMPT = "Pile-sort prompt LSB sent"
BLOCK_PILESORT_RESPONSE = "Provider response to the pile-sort prompt"
BLOCK_PILESORT_REASONING = "Reasoning trace the provider surfaced on the pile-sort step"
```

### Pile-interview step
```
BLOCK_PILE_INTERVIEW_PROMPT = "Pile-interview prompt LSB sent"
BLOCK_PILE_INTERVIEW_RESPONSE = "Provider response to the pile-interview prompt"
BLOCK_PILE_INTERVIEW_REASONING = "Reasoning trace the provider surfaced on the pile-interview step"
```

## 6. BLOCK_DETAIL_PROVENANCE + inline anti-attribution sentence

```
BLOCK_DETAIL_PROVENANCE = "Provenance and pipeline identifiers"
BLOCK_DETAIL_PROVENANCE_NOTE = "The identifiers below name the LSB collection session, the prompt-template version, and the provider-returned model-version string. They are properties of the LSB pipeline run, not of the model's intent."
```

## 7. N2 disposition statement (no fallback string)

The three top-level step fields on the published detail JSON (`freelist`, `pile_sort`, `pile_interview`) are non-Optional. Per `cdb_core/schemas.py` L650-652, `InformantRecord.{freelist, pile_sort, interview}` are required fields. The publish path cannot emit a record where any of these is null. Therefore:

- Drop `| None` typing on the three top-level step fields in `PublishedRecordDetail` (AC-P1).
- Remove AC-D7's "suppress whole section when null" branch from the test matrix.
- Do not ship a `RECORDS_DETAIL_STEP_MISSING` fallback string.

Coder notes choice (a) in the verdicts file T7 section per N2.

## 8. DATA_DICTIONARY.md §12.7 verbatim block

N7: anti-attribution sentence restated (not linked out) from CR-T4 §12.6.

```
### §12.7 Per-record detail JSON (CR-T7, 2026-06-10)

Per-domain `data/records/{slug}/detail/{informant_id}.json` files expose the verbatim bytes exchanged on each of the three CDA elicitation steps (free list, pile sort, pile interview) for a single collection session. Each file holds three top-level step objects (`freelist`, `pile_sort`, `pile_interview`); each step object holds three sub-fields (`prompt_verbatim`, `response_verbatim`, `thinking_verbatim`) plus the provider-returned model-version string and the LSB-side prompt-template version. The three top-level step fields are non-Optional; the publish path produces them on every emitted record. The `thinking_verbatim` field may be the empty string when the provider did not surface a reasoning trace; an empty string is a first-class state, not a missing record.

Per-record detail JSON exposes the verbatim bytes the LSB pipeline sent and the verbatim bytes the provider returned. The detail JSON is not a record of the model's reasoning, intent, or understanding; it is a transcript of the LSB collection step.
```

## Hard-rules compliance recap

- No em dashes anywhere in any delivered string.
- No CLAUDE.md §7 forbidden-vocabulary terms applied to models in any delivered string.
- No bare "refusal"; not used.
- Parser-state register throughout (no "answer", no quality judgment, no "response quality"; "response" is used only as the parser-state pair to "prompt").
- Strings are plain text, no markdown inside the strings themselves; ready to paste into TypeScript/Python constants.
