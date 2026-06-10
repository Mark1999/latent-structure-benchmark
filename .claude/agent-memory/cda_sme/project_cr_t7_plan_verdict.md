---
name: cr-t7-plan-verdict
description: CR-T7 per-record raw-exchange detail surface plan verdict (2026-06-10); PASS-WITH-NOTES with 8 binding notes (N1-N8); load-bearing fixes are N1 (CDA step "interview" vs follow-up "interview" label collision), N2 (schema reality — three steps are required fields on InformantRecord, None never emitted), N4 (verbatim labels must say "what LSB sent / what the provider returned", parser-state only), N5 (carry-forward of CR-T3 N4 no bare "refusal" to AC-D10 chrome scan).
metadata:
  type: project
---

# CR-T7 plan verdict (2026-06-10): PASS-WITH-NOTES

Plan: per-record raw-exchange detail surface; publish-layer per-informant JSON + dashboard per-record `<details>` expander. One commit, schema-additive only. CDA SME drafts byte-identical copy strings (`_FRAMING_NOTE_DETAIL` + block labels) before Coder dispatch.

## Verdict by axis
- Protocol validity: PASS (per-step verbatim exchanges correctly framed as protocol output, not model intent)
- Analytical validity: N/A (no analytical claim)
- Claims validity: PASS-WITH-NOTES (N1, N4 binding; cognition-attribution risk on three step-label strings)
- Audience translation: PASS-WITH-NOTES (N3, N6 binding; cold reader needs framing that distinguishes "originating interview step" from "follow-up interview record kind")
- Register compliance: PASS-WITH-NOTES (Register 1 vs Register 2 not relevant; per-record surface = corpus-lens / output-distribution level)
- Vocabulary compliance: PASS-WITH-NOTES (N5 carry-forward of "no bare refusal" into chrome-isolation scan AC-D10)

## Binding notes (Coder must apply before commit)
- N1 (BINDING, NAMING): The CDA step named `interview` on `InformantRecord` (pile-sort follow-up asking the model to explain pile criteria) and the "follow-up interview" record kind surfaced today (post-refusal `DeclineInterview`) are distinct objects. Block label `BLOCK_INTERVIEW_EXCHANGE` collides with existing user mental model. Rename binding direction: use `BLOCK_PILE_INTERVIEW_EXCHANGE` or `BLOCK_PILE_INTERPRETATION_EXCHANGE`. SME draft picks one; coder uses byte-identical.
- N2 (BINDING, SCHEMA REALITY): `InformantRecord.{freelist, pile_sort, interview}` are required fields per `cdb_core/schemas.py` lines 650-652. The plan's `PublishedStepExchange | None` typing at top level (AC-P1) and the "step not recorded" None semantic (AC-P2, AC-D7) describe a state that does not occur for records emitted from `informants.jsonl`. Either: (a) drop the `| None` typing and make the three top-level step fields non-Optional, removing AC-D7's "suppress whole section when null" branch from the test matrix; or (b) keep the typing as forward compatibility but document in the schema docstring AND in §12.7 that the None state is "reserved for future schema migrations and is not produced by current publish path." Coder picks (a) or (b) and notes the choice in the verdicts file T7 section.
- N3 (BINDING, FRAMING): `_FRAMING_NOTE_DETAIL` must explicitly name the three CDA elicitation steps (free list, pile sort, pile-criterion interview) and say what each is. A cold reader landing on a verbatim expansion needs the protocol context restated at the per-record level, not just inherited from the page-top framing_note. SME draft.
- N4 (BINDING, PARSER-STATE REGISTER): Each step's block-label sub-headings must distinguish "what LSB sent" (the prompt) from "what the provider returned" (the response) and from "what the provider surfaced as reasoning trace" (thinking) — mirroring the existing `BLOCK_PROMPT` / `BLOCK_RESPONSE` / `BLOCK_REASONING` register on the follow-up surface (failures_findings.ts L133-139). Do not collapse the three into a single "exchange" label without that distinction; the cognition-attribution failure mode lives in conflating "response" with "answer." SME draft of sub-labels (e.g., `BLOCK_FREELIST_PROMPT` / `BLOCK_FREELIST_RESPONSE` / `BLOCK_FREELIST_REASONING`) is byte-identical.
- N5 (BINDING, CHROME-ISOLATION CARRY-FORWARD): CR-T3 N4 ("no bare 'refusal' in chrome") applies to all new SME-bound strings and code comments. AC-D10 chrome-isolation walk (vitest case 9 extension) MUST include affirmative checks: zero occurrences of bare "refusal", `worldview`, `believes`, `\bthinks\b`, `understands`, `cooperative` (outside counterfactual) across the expanded detail DOM (excluding `<pre>` content). Coder extends the existing affirmative-presence checks pattern from CR-T6 N6.
- N6 (BINDING, AUDIENCE TRANSLATION): The dashboard expand affordance label (current placeholder `RECORDS_DETAIL_EXPAND_LABEL`) must NOT use "answer," "response quality," "see what the model said," or any quality-framed verb. Approved register: "Show parsed-step exchange," "Show LSB-side prompt and provider-returned response," or similar. SME draft. UI/UX gates discoverability separately.
- N7 (BINDING, ANTI-ATTRIBUTION REPETITION IN §12.7): `DATA_DICTIONARY.md` §12.7 must restate (not link out to) the N5 anti-attribution sentence from CR-T4 §12.6: "Per-record detail JSON exposes the verbatim bytes the LSB pipeline sent and the verbatim bytes the provider returned. The detail JSON is not a record of the model's reasoning, intent, or understanding; it is a transcript of the LSB collection step." Coder pastes byte-identical from SME draft.
- N8 (BINDING, FRAMING_NOTE BYTE-IDENTITY ACROSS SURFACES): `_FRAMING_NOTE_DETAIL` and the existing `_FRAMING_NOTE` (per-domain summary, successes.py L45-55) are distinct strings with distinct scopes — DO NOT reuse `_FRAMING_NOTE` byte-string in detail JSON; DO NOT paraphrase `_FRAMING_NOTE_DETAIL` between publish layer and dashboard. Two strings, each byte-identical to the SME verdict, each constant-imported once.

## Advisory carry-forwards (non-blocking)
- A1 (advisory): The Coder spot-check for PII before commit (AC-B1) is correct posture but sanitize coverage at AC-P2 must be verified against `sanitize_record_strings` recursion depth on the `thinking_verbatim` field (which may carry chain-of-thought-style content with embedded prompt-shaped strings). If sanitize's existing regex set misses on `thinking_verbatim`, Coder routes back to Architect — not improvise.
- A2 (advisory): Cloudflare Pages file-count math (AC-P8) intersects publishing surface for ~1,291 detail files + existing site files. Non-blocking on methodology axis; flagged because the failure mode is "deploy succeeds, files silently dropped" if the limit is hit. Coder verifies before commit per plan.
- A3 (advisory): The plan correctly defers the chart-side "see provenance" deep-link affordance (D4b) to a follow-up cycle. When that cycle arrives, the deep-link target string MUST also go through CDA SME — the journalist→record pivot is the highest-leverage place to slip into cognition attribution.

## Posture on Coder dispatch
SME verdict is conditional PASS-WITH-NOTES: Coder MAY NOT dispatch until SME has delivered byte-identical drafts for:
1. `_FRAMING_NOTE_DETAIL` (publish-layer, emitted into every detail JSON)
2. `RECORDS_DETAIL_FRAMING` (dashboard-side, in-page caption above the expanded body)
3. `RECORDS_DETAIL_EXPAND_LABEL` (expand affordance copy)
4. `RECORDS_DETAIL_LOADING`, `RECORDS_DETAIL_FETCH_FAILED`, `RECORDS_DETAIL_MALFORMED` (state copy)
5. The three (or nine, per N4 sub-label distinction) `BLOCK_*` strings for the free-list, pile-sort, and pile-criterion-interview sub-sections
6. `BLOCK_DETAIL_PROVENANCE` heading and (if needed) an inline anti-attribution sentence accompanying it
7. The "step missing" fallback string (per N2 disposition)
8. `DATA_DICTIONARY.md` §12.7 verbatim block (per N7)

Once strings are delivered, UI/UX gates layout/state-machine UX. Then Coder dispatches.
