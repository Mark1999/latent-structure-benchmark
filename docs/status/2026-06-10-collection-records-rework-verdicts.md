# Collection Records Rework Gate Verdicts

**Cycle:** Collection Records Rework (CR)
**Kickoff:** `docs/status/2026-06-10-collection-records-rework-kickoff.md`
**Date opened:** 2026-06-10

---


## Task index

| Task | Title | Train | Status |
|---|---|---|---|
| CR-T4 | Per-domain successful-record summary artifact | B | SHIPPED |
| CR-T1 | Impact paragraph for collection failures | A | SHIPPED |
| CR-T2 | Impact paragraph for follow-up interviews | A | Pending |
| CR-T3 | Taxonomy disclosure | A | Pending |
| CR-T5 | Successful-records section in Collection records tab | B | Pending T4 |
| CR-T6 | Counts caption update | B | SHIPPED |
| CR-T7 | Raw-exchange exposure on InformantRecord-derived rows | C | Pending T4+T5 |
| CR-T8 | Per-attempt retry-transcript exposure | C | Pending |

---

## CR-T4: per-domain successful-record summary artifact

**Architect plan:** `docs/status/2026-06-10-collection-records-rework-kickoff.md` §4 Task 4 (inline within kickoff; see also the CR-T4 Architect plan delivered in the same orchestrator session).

### CDA SME verdict: PASS-WITH-NOTES

**Date:** 2026-06-10

**Four-axis scorecard:**

| Axis | Score | Notes |
|---|---|---|
| Protocol validity | PASS | Paragraph correctly describes the three LSB-side outcome categories (refusal, unparseable, transport failure) without overclaiming about the protocol mechanism. |
| Analytical validity | N/A | No analysis claim made. |
| Claims validity | PASS | "how it says no, is as much a part of its behavior as the answers it gives" reads as observable output behavior, not model intent or cognition. §1.5.4 clean. |
| Audience translation | PASS | A cold journalist reads one paragraph and understands why these records matter. The counterfactual deletion framing ("that would be misleading") is effective. |

**Notes (advisory, do not alter string):**

- **N1 (advisory):** The word "cooperative" survives only inside the counterfactual deletion frame ("make every model look equally cooperative"). Downstream uses of this word in non-counterfactual contexts should be flagged for SME review.
- **N2 (advisory):** "behavior" and the implicit output-distribution register coexist within approximately 50 words. T14 (taxonomy disclosure) should bridge these registers explicitly when it ships.
- **Gate rule applied:** PASS-WITH-NOTES leaves the string byte-identical. Notes are advisory for downstream tasks; they do not alter the Coder's string.

---

### UI/UX verdict: PASS-WITH-NOTES

**Date:** 2026-06-10

**Four-question scorecard:**

| Question | Score | Notes |
|---|---|---|
| OWID design fidelity | PASS | Token-only class `.failures-findings__impact` using existing token set. No new tokens introduced. |
| 30-second journalist test | PASS | Impact paragraph is the first prose content below the domain selector; a cold reader encounters it immediately. |
| Researcher reproduce-and-cite test | PASS | Paragraph contextualizes data without suppressing it; researchers can still access verbatim records below. |
| WCAG AA accessibility | PASS | `--color-text-primary` on `--color-background` exceeds AA at all font sizes. |

**Notes (binding on Coder):**

- **F1 (binding, CSS class):** No existing class in `failures-findings.css` is suitable for the impact paragraph. `.failures-findings__framing-note` is already claimed for the data-sourced framing_note paragraph and carries secondary-color/sm-font styling. New class `.failures-findings__impact` is specified using only existing tokens: `--font-size-base`, `--color-text-primary`, `--line-height-body`, `--space-6`, `--max-prose-width`.
- **F2 (advisory, chrome-isolation):** The word "cooperative" in `IMPACT_PARAGRAPH_FAILURES` is not on the §19.13 forbidden-substring list. CDA SME N1 advisory applies. Case 9 continues to pass as written.
- **F3 (binding, placement):** Impact paragraph goes inside the `fetchState.kind === 'ready'` branch, before `data.framing_note` in JSX order, consistent with the amended §19.4.
- **F4 (confirmatory, empty-state):** The empty-state path (n_records === 0) does not suppress the impact paragraph because both live inside the ready branch. No additional conditional needed to satisfy AC3 and AC7.
- **Design system update:** DESIGN_SYSTEM.md §19.4 amended; version bumped to v0.19.1; changelog entry added referencing this verdict file.

| Protocol validity | PASS | Summary shape mirrors failures posture; no new protocol claims. |
| Analytical validity | PASS | n_runs / n_qa_passed gap preserved per failures-are-findings directive. |
| Claims validity | PASS-WITH-NOTES | framing_note anti-attribution clause approved; binding notes N1-N6 applied. |
| Audience translation | PASS | "Successful = parser-state property" framing accessible to cold reader. |

**Binding notes (applied by Coder):**

- N1: `framing_note` is byte-identical to the quoted string below. No paraphrasing at code time.
- N2: Docstring at top of `successes.py` MUST NOT contain "successful answer," "correct answer," "answered correctly," "good response," or any variant attributing quality to model output. Use "parsed primary-step response."
- N3: Empty-domain `by_model: []` files MUST still carry the full `framing_note`. Empty is not absent.
- N4: WARNING message on multi-provider must not use anthropomorphic phrasing. Recommended wording: "model_id X has multiple provider strings in raw informants -- lexicographically smallest selected for summary row; full per-informant provider strings remain in the open data bundle."
- N5: `DATA_DICTIONARY.md` §12.6 new subsection MUST state explicitly: "Successful here means the LSB pipeline parsed a primary-step response. It is NOT a quality judgment on the model output."
- N6: Manifest field name `records: dict[str, str]` approved. Mirrors `failures: dict[str, str]` posture.

**Byte-identical framing_note string** (Coder copy-pastes this verbatim into `_FRAMING_NOTE` in `cdb_publish/successes.py`; no paraphrasing):

> These records summarise collection sessions for which the LSB pipeline parsed a primary-step response. Each row reports the run count, the QA-pass count, and the provider-returned model-version string for a single `model_id` in this domain. A row is a property of the LSB collection pipeline's parsing outcome, not a quality judgment on the model output. The full per-record bytes are available in the open data bundle under CC0; the unsuccessful counterpart sessions are surfaced under `data/failures/{slug}.json`. See the methodology page for the corpus-lens framing.

**Open methodological calls resolved:**

- `model_version_returned` per row: lex-greatest plus sibling `model_version_returned_count: int`. APPROVED.
- `n_qa_passed` in summary: KEEP. Gap between `n_runs` and `n_qa_passed` is a finding.
- Row order: lexicographic by `model_id` ascending. APPROVED.

---

### Reviewer verdict: PASS

**Date:** 2026-06-10

**Checks:**

1. String in `IMPACT_PARAGRAPH_FAILURES` is byte-identical to the Architect plan §3 string, including `provider's side` (apostrophe), three comma-serialized clauses, final period, no em dashes. PASS.
2. Export is purely additive in `copy/failures_findings.ts`; no existing export renamed, reordered, or modified. PASS.
3. Paragraph renders in `ready` state for all three domains (family, holidays, food empty-state). PASS.
4. Chrome-isolation vitest case (case 9) passes; new byte-identity case (11) passes; new empty-state case (12) passes; new loading-absent case (13) passes. PASS.
5. DESIGN_SYSTEM.md §19.4 amended; version bumped v0.19.0 to v0.19.1; changelog entry references the verdict file path. PASS.
6. One commit on master; message follows Conventional Commits with scope `dashboard`; body references kickoff and verdict file; no em dashes. PASS.
7. No banned vocabulary in any diffed text. "behavior" reads as observable-output behavior. "cooperative" is inside a counterfactual frame. PASS.
8. No edits to `framing_note` (JSON-sourced), `SECTION_HEADING`, `EMPTY_CAPTION`, badges, blocks, or other CDA-SME-bound byte-identical strings. PASS.

---

*T3-T8 verdicts to be appended as subsequent tasks complete.*

**Checks performed:**

- R4 (append-only invariant): `build_successes()` never writes to `data/raw/`. SHA256 test in `test_successes.py` `TestSHA256Invariance` confirms. PASS.
- R6 (schema sign-off gate): no `cdb_core/schemas.py` edits. Publish-layer schemas only. PASS.
- R7 (DATA_DICTIONARY co-update): §12.6 added in same commit; v0.1.24 bumped to v0.1.25. PASS.
- R9 (no real API in tests): all tests use `tests/fixtures/successes/informants.jsonl`. PASS.
- Forbidden vocabulary absent from all new text ("worldview," "believes," "thinks," "understands"). PASS.
- No em dashes in any new file. PASS.
- CDA SME N1-N6 binding notes applied. PASS.
- `cdb_analyze` LLM-import boundary unaffected (new code is in `cdb_publish`, not `cdb_analyze`). PASS.
- Hardcoded counts: no literal record count (e.g., 1291) in source. PASS.

---

### Tester verdict: PASS

**Date:** 2026-06-10

**Test run:** `uv run pytest tests/cdb_publish/test_successes.py -v`

**Tests passing:**

- `TestEmptyDomainEmission::test_empty_domain_file_emitted`
- `TestEmptyDomainEmission::test_empty_domain_framing_note_present`
- `TestMultiModelCounting::test_n_runs_counts_all_records`
- `TestMultiModelCounting::test_n_qa_passed_subset_only`
- `TestMultiModelCounting::test_qa_failed_counts_n_runs_not_n_qa_passed`
- `TestMultiModelCounting::test_by_model_sorted_by_model_id_lexicographic`
- `TestMultiModelCounting::test_model_version_returned_count_when_multiple`
- `TestMultiModelCounting::test_model_version_returned_count_one_when_single`
- `TestSanitization::test_sanitization_fires_on_key_shaped_version_string`
- `TestSchemaRoundTrip::test_round_trip_family`
- `TestSchemaRoundTrip::test_round_trip_empty_domain`
- `TestSHA256Invariance::test_source_file_not_modified`
- `TestManifestMap::test_manifest_map_all_slugs`
- `TestManifestMap::test_manifest_values_never_null`
- `TestFramingNote::test_framing_note_in_every_domain`
- `TestFramingNote::test_framing_note_byte_identical_to_module_constant`
- `TestMissingInformantsFile::test_missing_file_produces_empty_outputs`
- `TestBuildIntegration::test_build_manifest_has_records_field`
- `TestBuildIntegration::test_manifest_records_default_empty`
- `test_every_domain_emits_file[family]`
- `test_every_domain_emits_file[holidays]`
- `test_every_domain_emits_file[food]`

## T1: Impact paragraph for collection failures

**Task scope:** Add `IMPACT_PARAGRAPH_FAILURES` (Mark-authored) to the Collection records tab, above the framing_note. Amend DESIGN_SYSTEM.md §19.4. Three new vitest cases.

### CDA SME verdict: PASS-WITH-NOTES

**Date:** 2026-06-10

**Four-axis scorecard:**

| Axis | Score | Notes |
|---|---|---|
| Protocol validity | PASS | Paragraph correctly describes the three LSB-side outcome categories (refusal, unparseable, transport failure) without overclaiming about the protocol mechanism. |
| Analytical validity | N/A | No analysis claim made. |
| Claims validity | PASS | "how it says no, is as much a part of its behavior as the answers it gives" reads as observable output behavior, not model intent or cognition. §1.5.4 clean. |
| Audience translation | PASS | A cold journalist reads one paragraph and understands why these records matter. The counterfactual deletion framing ("that would be misleading") is effective. |

**Notes (advisory, do not alter string):**

- **N1 (advisory):** The word "cooperative" survives only inside the counterfactual deletion frame ("make every model look equally cooperative"). Downstream uses of this word in non-counterfactual contexts should be flagged for SME review.
- **N2 (advisory):** "behavior" and the implicit output-distribution register coexist within approximately 50 words. T14 (taxonomy disclosure) should bridge these registers explicitly when it ships.
- **Gate rule applied:** PASS-WITH-NOTES leaves the string byte-identical. Notes are advisory for downstream tasks; they do not alter the Coder's string.

---

### UI/UX verdict: PASS-WITH-NOTES

**Date:** 2026-06-10

**Four-question scorecard:**

| Question | Score | Notes |
|---|---|---|
| OWID design fidelity | PASS | Token-only class `.failures-findings__impact` using existing token set. No new tokens introduced. |
| 30-second journalist test | PASS | Impact paragraph is the first prose content below the domain selector; a cold reader encounters it immediately. |
| Researcher reproduce-and-cite test | PASS | Paragraph contextualizes data without suppressing it; researchers can still access verbatim records below. |
| WCAG AA accessibility | PASS | `--color-text-primary` on `--color-background` exceeds AA at all font sizes. |

**Notes (binding on Coder):**

- **F1 (binding, CSS class):** No existing class in `failures-findings.css` is suitable for the impact paragraph. `.failures-findings__framing-note` is already claimed for the data-sourced framing_note paragraph and carries secondary-color/sm-font styling. New class `.failures-findings__impact` is specified using only existing tokens: `--font-size-base`, `--color-text-primary`, `--line-height-body`, `--space-6`, `--max-prose-width`.
- **F2 (advisory, chrome-isolation):** The word "cooperative" in `IMPACT_PARAGRAPH_FAILURES` is not on the §19.13 forbidden-substring list. CDA SME N1 advisory applies. Case 9 continues to pass as written.
- **F3 (binding, placement):** Impact paragraph goes inside the `fetchState.kind === 'ready'` branch, before `data.framing_note` in JSX order, consistent with the amended §19.4.
- **F4 (confirmatory, empty-state):** The empty-state path (n_records === 0) does not suppress the impact paragraph because both live inside the ready branch. No additional conditional needed to satisfy AC3 and AC7.
- **Design system update:** DESIGN_SYSTEM.md §19.4 amended; version bumped to v0.19.1; changelog entry added referencing this verdict file.

---

### Reviewer verdict: PASS

**Date:** 2026-06-10

**Checks:**

1. String in `IMPACT_PARAGRAPH_FAILURES` is byte-identical to the Architect plan §3 string, including `provider's side` (apostrophe), three comma-serialized clauses, final period, no em dashes. PASS.
2. Export is purely additive in `copy/failures_findings.ts`; no existing export renamed, reordered, or modified. PASS.
3. Paragraph renders in `ready` state for all three domains (family, holidays, food empty-state). PASS.
4. Chrome-isolation vitest case (case 9) passes; new byte-identity case (11) passes; new empty-state case (12) passes; new loading-absent case (13) passes. PASS.
5. DESIGN_SYSTEM.md §19.4 amended; version bumped v0.19.0 to v0.19.1; changelog entry references the verdict file path. PASS.
6. One commit on master; message follows Conventional Commits with scope `dashboard`; body references kickoff and verdict file; no em dashes. PASS.
7. No banned vocabulary in any diffed text. "behavior" reads as observable-output behavior. "cooperative" is inside a counterfactual frame. PASS.
8. No edits to `framing_note` (JSON-sourced), `SECTION_HEADING`, `EMPTY_CAPTION`, badges, blocks, or other CDA-SME-bound byte-identical strings. PASS.

---

## T2: Impact paragraph for follow-up interviews

**Task scope:** Add `IMPACT_PARAGRAPH_FOLLOWUPS` (Mark-authored) to the Collection records tab, inserted between failure records and decline-interview records (conditional on at least one decline_interview record present). Amend DESIGN_SYSTEM.md §19.4. Two new vitest cases.

### CDA SME verdict: PASS-WITH-NOTES

**Date:** 2026-06-10

**Four-axis scorecard:**

| Axis | Score | Notes |
|---|---|---|
| Protocol validity | PASS | Paragraph correctly frames the follow-up interview as an LSB-side protocol action, not a model-initiated behavior. "We ask it one more question" attributes the action to LSB, not to the model. |
| Analytical validity | N/A | No analysis claim made. |
| Claims validity | PASS | S4 ("just output, produced the same way as everything else it says") and S6 ("observable behavior, not the inside story") are the load-bearing §1.5.4 register locks. The string explicitly disclaims interiority and frames the explanation as output, not cognition. §1.5.4 clean. |
| Audience translation | PASS | A cold reader is explicitly warned ("Read these with care") and given a concrete reason why the explanation may be unreliable, without attributing intent. The "not the inside story" close is the strongest anti-attribution sentence on this surface. |

**Notes (advisory):**

- **A1 (advisory):** AC7 reference to "R7" in the plan is an internal citation artifact; the plan's AC7 confirms the approved string contains none of the seven forbidden substrings. No action required by Coder.
- **A2 (advisory):** "behavior" and the implicit output-distribution register coexist in T2 as in T1. T3 (taxonomy disclosure) should bridge these registers explicitly when it ships. This is a T3 concern, not a T2 gate concern.
- **A3 (standing rule):** The posture that the SME does not silently revise Mark's prose (FAIL bounces to Mark via orchestrator) is hereby promoted to a standing operating rule for any future Mark-authored copy surface. No Coder action required.
- **Carry-forward T1 N1:** "cooperative" is not used in the T2 string. T2 AC14 + R9 enforced. CONFIRMED.
- **Carry-forward T1 N2:** Two-register bridging is a T3 concern; noted but not a T2 gate condition.
- **Conditional-render rule:** Renders only when at least one decline_interview record is present. A follow-up-interview framing paragraph with zero follow-up-interview records would be vacuous and misleadingly imply the surface contains data it does not. Food empty-state (n_records === 0) correctly suppresses it. METHODOLOGICALLY CORRECT.
- **Gate rule applied:** PASS-WITH-NOTES leaves the string byte-identical. Notes are advisory.

---

### UI/UX verdict: PASS-WITH-NOTES

**Date:** 2026-06-10

**Four-question scorecard:**

| Question | Score | Notes |
|---|---|---|
| OWID design fidelity | PASS | Reuses `.failures-findings__impact` class (existing tokens only). No new tokens introduced. |
| 30-second journalist test | PASS | Paragraph is positioned at the natural reading boundary between failure records and follow-up interview records; a cold reader encounters it immediately before the interview transcripts they are about to read. |
| Researcher reproduce-and-cite test | PASS | Paragraph contextualizes the follow-up interview artifacts without suppressing them; researchers can still access verbatim records below. |
| WCAG AA accessibility | PASS | `.failures-findings__impact` uses `--color-text-primary` on `--color-background`, same as CR-T1 verdict. Exceeds AA at all font sizes. |

**Notes (binding on Coder):**

- **N1 (binding, placement):** Failure records group renders first, then the follow-up impact paragraph, then the decline-interview records group. Two separate `<ol className="failures-findings__list">` elements. The paragraph is a sibling `<p>` element between the two lists. Do NOT merge all records into a single `<ol>`.
- **N2 (binding, CSS class):** Reuse `.failures-findings__impact`. No new class, no new tokens.
- **N3 (confirmatory, empty-state):** When `n_records === 0`, neither the paragraph nor any grouped lists render; the empty-state `<p>` is the only content. Unchanged from current posture.
- **N4 (confirmatory, chrome-isolation):** Approved string does not contain `consensus`, `Smith's S`, `agree`, `believe`, `worldview`, `categoriz`, or `\bthink`. Case 9 unchanged.
- **N5 (secondary fix, closing-line):** The closing line of DESIGN_SYSTEM.md must be updated from `v0.19.0` to `v0.19.2`. This corrects a pre-existing error not addressed in v0.19.1.
- **Design system update:** DESIGN_SYSTEM.md §19.4 further amended under v0.19.2; changelog entry added referencing this verdict file; closing-line version string corrected.

---

### Reviewer verdict: PASS

**Date:** 2026-06-10

**Checks:**

- R1. `IMPACT_PARAGRAPH_FOLLOWUPS` byte-identical to the plan §2 string and approved-copy doc T2 section. No em dashes, straight apostrophes, exact whitespace, final period present. PASS.
- R2. Export is purely additive in `copy/failures_findings.ts`; `IMPACT_PARAGRAPH_FAILURES` and all other existing exports unchanged. PASS.
- R3. Paragraph renders in `ready` state when at least one decline_interview record is present; does not render in loading/fetch-failed/malformed/no-decline_interview-records states. PASS.
- R4. vitest cases 14 (byte-identity under `familyJson`) and 15 (absent under `foodJson`) added and pass. Case 9 chrome-isolation passes unchanged. PASS.
- R5. DESIGN_SYSTEM.md §19.4 amended under v0.19.2; changelog entry added; closing-line version corrected from v0.19.0 to v0.19.2. PASS.
- R6. Verdict file has T2 section appended; T1 section unchanged. PASS.
- R7. One commit on master with the specified message; body references kickoff and verdict file; no em dashes. PASS.
- R8. No em dashes anywhere in the diff (code, comments, docs, commit message). PASS.
- R9. No banned vocabulary in diffed text. No use of "cooperative" outside the existing T1 counterfactual frame. PASS.
- R10. No new CSS custom properties referenced that are not defined in `tokens.css`. `.failures-findings__impact` class reused; all tokens already verified in CR-T1. PASS.
- R11. No edits to CDA-SME-bound byte-identical strings (`framing_note` JSON, `SECTION_HEADING`, `EMPTY_CAPTION`, badges, blocks, `IMPACT_PARAGRAPH_FAILURES`, loading/error strings). PASS.
- R12. No spend-gate or cost-estimate language anywhere in the diff. PASS.

---

## T3: Taxonomy disclosure

**Task scope:** Add `TAXONOMY_BLOCK` export to `copy/failures_findings.ts`, render it in `FailuresFindings.tsx` between impact paragraph and framing_note, add CSS classes, add vitest cases 16-19, amend DESIGN_SYSTEM.md §19.4 + new §19.14, bump to v0.19.3.

### CDA SME verdict: PASS-WITH-NOTES

**Date:** 2026-06-10

**Four-axis scorecard:**

| Axis | Score | Notes |
|---|---|---|
| Protocol validity | PASS-WITH-NOTES | N1, N2 binding: single_degenerate_pile and parse_failure rows corrected per actual classifier rules. |
| Analytical validity | N/A | No analysis claim made. |
| Claims validity | PASS-WITH-NOTES | N3 bridge sentence, N4 refusal register lock, N6 no cognition attribution applied. |
| Audience translation | PASS-WITH-NOTES | N5 enum subheading naming, N8 CR-T5 carry-forward applied. |

**Binding notes applied by Coder:**

- N1 (BINDING): `single_degenerate_pile` row corrected to "exactly one pile in a pile-sort step, with that pile holding at least 95 percent of the free-list items."
- N2 (BINDING): `parse_failure` row broadened to "malformed JSON or a missing required field" as illustrative examples.
- N3 (BINDING): Bridge sentence: "Every category below is a property of how the LSB pipeline classified the session, not a property of what the model decided."
- N4 (BINDING): Follow-up interview row uses "an LSB-classified refusal"; `refusal_string_match` row retains negation pattern "not a model statement of refusal." No bare "refusal" in surrounding code comments, DESIGN_SYSTEM.md narration, or commit message body.
- N5 (BINDING): Enum subheading text: "originating_outcome_class ENUM VALUES (seven, byte-identical to the schema):" with `originating_outcome_class` in `<code>` in the JSX renderer.
- N6 (BINDING): Zero model-cognition attribution in all wording.
- N7 (BINDING): Zero instances of §19.13 forbidden substrings in TAXONOMY_BLOCK wording. "classified/classification" (root: classif-) used over "categorized" (root: categoriz-).
- N8 (ADVISORY): Successful run row says "LSB parsed primary-step output from the session" (not "response from the model") per CR-T5 forward-carry.

---

### UI/UX verdict: PASS-WITH-NOTES

**Date:** 2026-06-10

**Four-question scorecard:**

| Question | Score | Notes |
|---|---|---|
| OWID design fidelity | PASS | Token-only classes. No new tokens. All tokens verified against tokens.css. |
| 30-second journalist test | PASS | Three top-level rows scannable; enum values below for researchers. |
| Researcher reproduce-and-cite test | PASS | Enum ids in backtick code elements; byte-identical to schema. |
| WCAG AA accessibility | PASS | `<section aria-labelledby>` + `<h2>` heading landmark. `<ul>` semantics correct. |

**Binding notes applied by Coder:**

- F1 (BINDING): `<section aria-labelledby="taxonomy-block-heading">` + `<h2 id="taxonomy-block-heading">` + `<ul>` (not `<dl>`) for both list structures.
- F2 (BINDING): New CSS classes `.failures-findings__taxonomy`, `.failures-findings__taxonomy-heading`, `.failures-findings__taxonomy-bridge`, `.failures-findings__taxonomy-list`, `.failures-findings__taxonomy-enum-label` -- all token-only, no new tokens.
- F3 (BINDING): Taxonomy block placed as step 4 in §19.4 content order (between impact paragraph and framing_note).
- F4 (BINDING): Renders in ready state including n_records === 0 empty-state path. NOT gated on n_records > 0.
- F5 (BINDING): `TAXONOMY_BLOCK` is a structured object literal (`as const`) with `heading`, `bridge`, `topLevel`, `enumSubheading`, `enumValues` fields.
- F6 (BINDING): Vitest cases 16-19 added.
- F7 (CONFIRMATORY): Case 9 chrome-isolation passes unchanged. "classified" root used, not "categoriz".
- F8 (ADVISORY): No bare "refusal" in code comments, commit message, or DESIGN_SYSTEM.md §19.14 narration.
- F9 (CONFIRMATORY): Zero em dashes in any text written for this task.

---

### Reviewer verdict: PASS

**Date:** 2026-06-10

**Checks:**

- R1. `TAXONOMY_BLOCK` export added to `copy/failures_findings.ts` as a structured `as const` object. All seven `id` values byte-identical to `cdb_core/schemas.py` lines 734-742: `empty_output`, `refusal_string_match`, `single_degenerate_pile`, `parse_failure`, `http_error`, `timeout`, `other`. PASS.
- R2. Export is purely additive; `IMPACT_PARAGRAPH_FAILURES`, `IMPACT_PARAGRAPH_FOLLOWUPS`, and all other existing exports unchanged (no rename, reorder, or modification). PASS.
- R3. Taxonomy block renders in `ready` state for all three domains including food empty-state (n_records === 0). Does not render in loading/fetch-failed/malformed states. PASS.
- R4. Vitest cases 16 (byte-identity + enum ids in DOM), 17 (enum ids in `<code>`), 18 (empty-state path), 19 (absent in loading state) added and pass. Case 9 chrome-isolation passes unchanged. PASS.
- R5. DESIGN_SYSTEM.md §19.4 amended under v0.19.3; new §19.14 added; changelog entry added at top; closing-line version updated from v0.19.2 to v0.19.3. PASS.
- R6. No em dashes (U+2014) anywhere in the diff (code, comments, docs, commit message). PASS.
- R7. No bare "refusal" in code comments, commit message body, or DESIGN_SYSTEM.md §19.14 narration. PASS.
- R8. No banned vocabulary (worldview, believes, thinks, understands) in any new text. PASS.
- R9. All CSS classes use `.failures-findings__taxonomy*` prefix. All `var(--...)` tokens verified against `tokens.css`. No new token definitions. PASS.
- R10. No edits to CDA-SME-bound byte-identical strings (`framing_note` JSON, `SECTION_HEADING`, `EMPTY_CAPTION`, badges, blocks, `IMPACT_PARAGRAPH_FAILURES`, `IMPACT_PARAGRAPH_FOLLOWUPS`, loading/error strings). PASS.
- R11. No `cdb_core/schemas.py` edits. No `DATA_DICTIONARY.md` update required (publish-layer copy-only task). PASS.
- R12. No spend-gate or cost-estimate language anywhere in the diff. PASS.
- R13. One commit on master with message `feat(dashboard): collection outcome taxonomy disclosure (CR-T3)`; body references kickoff and verdict file; no em dashes. PASS.

---

### Tester verdict: PASS

**Date:** 2026-06-10

**Test run:** `npm run test` from `apps/dashboard/`

**Cases passing (new, CR-T3):**
- Case 16: TAXONOMY_BLOCK heading, bridge, and all seven enum ids present in DOM under familyJson. PASS.
- Case 17: all seven enum id strings appear inside `<code>` elements in DOM under familyJson. PASS.
- Case 18: taxonomy block heading present in food empty-state path (n_records === 0). PASS.
- Case 19: taxonomy block absent in loading state. PASS.

**Cases passing (existing, unmodified):**
- Case 9: chrome-isolation DOM-walk -- zero forbidden substrings in LSB chrome text. PASS.
- Cases 1-8, 10-15: all existing cases pass unchanged. PASS.

---

## T5: Successful-records section in Collection records tab

**Task scope:** Extend `FailuresFindings.tsx` with parallel fetch of `/data/records/{domain}.json`, independent `RecordsFetchState`, `isRecordsSummaryFile` type guard, `RecordsSummarySection` sub-component rendering the per-model table below the failures content. Add `RecordsModelRow` and `RecordsSummaryFile` types to `types.ts`. Add eight new copy strings to `copy/failures_findings.ts`. Add CSS classes to `failures-findings.css`. Update DESIGN_SYSTEM.md §19.4 + add §19.15. Update TAXONOMY_BLOCK.topLevel[0].description per SME N6 conditional revision. Add vitest cases 20-26 and extend cases 9 and 10.

### CDA SME verdict: PASS-WITH-NOTES

**Date:** 2026-06-10

**Four-axis scorecard:**

| Axis | Score | Notes |
|---|---|---|
| Protocol validity | PASS | Section heading "Per-model summary of parsed primary-step responses" correctly frames parser-state, not quality judgment. |
| Analytical validity | N/A | No analysis claim made. Table reports counts only. |
| Claims validity | PASS-WITH-NOTES | N1-N6 binding notes applied (see below). CF1, T1 N1, T3 N4, T3 N8 carry-forwards confirmed. |
| Audience translation | PASS | framing_note renders verbatim; link-out caption directs to Data tab. |

**Binding notes applied:**

- N1 (BINDING): Section heading = "Per-model summary of parsed primary-step responses". No "Successful" in heading.
- N2 (BINDING): Column labels approved: Model | Provider | Runs | QA-pass count | Model version returned.
- N3 (BINDING): Empty-state observation approved verbatim.
- N4 (BINDING): Link-out caption approved verbatim (Architect stub unchanged).
- N5 (BINDING): Loading/fetch-failed/malformed strings issued byte-identical.
- N6 (BINDING, conditional revision): TAXONOMY_BLOCK.topLevel[0].description updated to drop "when the successes section ships" stale phrasing. New text: "LSB parsed primary-step output from the session. Surfaced in the per-model summary section below. The per-domain summary artifact is at /data/records/{slug}.json."

**Carry-forwards confirmed:**

- CF1 (CR-T4): n_qa_passed label reads as software-only QA pass count. CONFIRMED.
- T1 N1: "cooperative" does not appear outside the existing counterfactual frame. CONFIRMED.
- T3 N4: no bare "refusal" in any new copy strings or commit text. CONFIRMED.
- T3 N8: TAXONOMY_BLOCK.topLevel[0] forward-pointer phrasing now resolved (section shipped). CLOSES T3 N8.
- §1.5.4 forbidden-vocabulary scan: clean. No worldview/believes/thinks/understands.
- "Successful" does not echo as a quality judgment in any surrounding copy.
- §19.13 forbidden-substring list: absent from all new chrome strings.

---

### UI/UX verdict: PASS-WITH-NOTES

**Date:** 2026-06-10

**Four-question scorecard:**

| Question | Score | Notes |
|---|---|---|
| OWID design fidelity | PASS | Token-only classes. No new tokens. All tokens verified against tokens.css (Pitfall 15). |
| 30-second journalist test | PASS | Records section below failures list; cold reader encounters failures framing first, then the full picture. |
| Researcher reproduce-and-cite test | PASS | framing_note verbatim; link-out caption points to Data tab + bundle + HF + Zenodo. |
| WCAG AA accessibility | PASS | sr-only caption on table (WCAG 1.3.1); section aria-labelledby landmark; display:block mobile scroll (375px). --color-text-caption on link-out caption (~4.60:1, WCAG AA). |

**Binding notes applied:**

- Placement: records section renders below failures list (below EMPTY_CAPTION when n_records === 0).
- WCAG gap: `<caption className="sr-only">` required inside `<table>` (WCAG 1.3.1). Applied.
- Mobile overflow: `.failures-findings__successes-table` uses `display: block`; thead/tbody use `display: table`. Applied.
- Color token: link-out caption uses `--color-text-caption` (NOT `--color-text-secondary`). Applied.
- CSS class naming: `.failures-findings__successes-*` prefix for new classes; reuse `.failures-findings__taxonomy-heading` for h2; reuse `.failures-findings__empty` semantics for zero-runs state. Applied.
- Fetch coupling: `Promise.allSettled` + one AbortController; two independent sub-states. Applied.
- No sortable columns: no `<th onClick>` handlers. Applied per AC16.
- TAXONOMY_BLOCK N6: SME-conditional revision shipped in same commit. Applied.
- DESIGN_SYSTEM.md v0.19.4: §19.4 step 8 added; §19.15 new subsection added; changelog entry added; closing-line version updated to v0.19.4. Applied.

---

### Reviewer verdict: PASS

**Date:** 2026-06-10

**Checks:**

- AC1: `RecordsModelRow` and `RecordsSummaryFile` exported from `types.ts`; fields exactly match CR-T4 family.json shape; additive (no existing exports modified). PASS.
- AC2: Parallel fetch via `Promise.allSettled` against one AbortController. Domain change aborts both. PASS.
- AC3: `RecordsFetchState` independent of `FetchState`; failures error does not suppress records section. PASS.
- AC4: `isRecordsSummaryFile` validates all six required fields with correct primitive types per row. PASS.
- AC5: Records section `<section aria-labelledby="records-summary-heading">` renders below failures content. Two placement contexts covered. PASS.
- AC6: `data.framing_note` rendered verbatim inside `.failures-findings__successes-framing`. PASS.
- AC7: Table columns match N2 labels; model_id/provider/model_version_returned in `<code>`; n_runs/n_qa_passed as plain integers; model_version_returned_count not rendered. PASS.
- AC8: `by_model: []` renders `RECORDS_EMPTY_OBSERVATION`, not table. framing_note still renders. PASS.
- AC9: fetch-failed state renders `RECORDS_FETCH_FAILED_TEXT`. PASS.
- AC10: malformed state renders `RECORDS_MALFORMED_TEXT`. PASS.
- AC11: loading state renders `RECORDS_LOADING_TEXT`. PASS.
- AC12: `RECORDS_LINK_OUT_CAPTION` renders below table (and below empty-state). PASS.
- AC13: Vitest cases 20-26 added; case 9 extended to include records DOM; case 10 updated for 2-fetch-per-domain model. PASS.
- AC14: Case 9 chrome-isolation walk extended; forbidden-substring scan passes over new DOM. PASS.
- AC15: All `var(--...)` tokens verified against `tokens.css`. No new token definitions. PASS.
- AC16: No `<th onClick>`. No sort state. Row order from artifact's by_model array. PASS.
- AC17: No forbidden vocabulary in any new string (worldview/believes/thinks/understands/cooperative outside counterfactual). "Successful" not echoed as quality judgment. No bare "refusal". PASS.
- AC18: DESIGN_SYSTEM.md §19.4 step 8 added; §19.15 subsection added; changelog v0.19.4; closing line updated. PASS.
- AC19: T5 section appended to verdicts file; T1/T2/T3/T4 sections unchanged. PASS.
- AC20: npm run build + npm run test + npm run lint all pass. PASS.
- AC21: Zero em dashes (U+2014) in any new text. PASS.
- AC22: One commit on master. PASS.
- AC23: TAXONOMY_BLOCK.topLevel[0].description updated per SME N6 conditional revision; CR-T3 case 16 fixture test updated (heading still passes; description is in DOM text). PASS.
- Pitfall 15: every var(--...) verified against tokens.css. PASS.
- Pitfall 7: no forbidden vocabulary in any diffed text including comments. PASS.
- No cdb_core/schemas.py edits. No cdb_publish/ edits. No DATA_DICTIONARY.md edits (R6/R7 not triggered). PASS.
- No spend-gate or cost-estimate language (R13). PASS.
- cdb_analyze LLM-import boundary unaffected (new code is dashboard). PASS.

---

## CR-T6: Counts caption update

**Task scope:** Update `countsCaptionText()` in `copy/failures_findings.ts` to accept optional `nParsedResponses?: number`; implement four-cell empty-state matrix per CDA SME N1-N5; update caption call site in `FailuresFindings.tsx`; add vitest cases 27-32; extend case 9; amend DESIGN_SYSTEM.md §19.4 step 6 + add §19.16, bump to v0.19.5.

### CDA SME verdict: PASS-WITH-NOTES

**Date:** 2026-06-10

**Four-axis scorecard:**

| Axis | Score | Notes |
|---|---|---|
| Protocol validity | PASS | "Parsed primary-step responses" is parser-state language; correctly describes a property of the LSB pipeline's parsing outcome, not a quality judgment on model output. |
| Analytical validity | N/A | No analysis claim made. Count of pipeline parsing outcomes only. |
| Claims validity | PASS | No leading total (N1 Option C). No "successful" in caption. Three-clause template byte-identical to N2. §1.5.4 clean. |
| Audience translation | PASS | Four-cell matrix covers all first-class states. S-clause-only and failure-clause-only gracefully degrade on partially available data. |

**Binding notes (applied by Coder):**

- N1 (BINDING): No leading total. Option C adopted. Summing n_informants and n_records is a category error.
- N2 (BINDING): Byte-identical template: `"{S} parsed primary-step responses, {F} collection {failure|failures}, {D} follow-up {interview|interviews}."` with pluralization matching existing L158-159 pattern.
- N3 (BINDING): Four-cell matrix: (>0,>0) full, (>0,0) drop S clause, (0,>0) S clause only, (0,0) caption omitted.
- N4 (BINDING): Records-side fetch-not-ready renders failures-only caption (undefined nParsedResponses). Independent fetches must not couple.
- N5 (BINDING): `nParsedResponses` is optional (`number | undefined`); parameter name mirrors surface vocabulary.
- N6 (BINDING): Case-9 chrome-isolation scan affirmatively confirms "parsed primary-step responses" present AND "successful"/"successfully" absent.
- N7 (ADVISORY): "Parsed primary-step responses" is parser-state language; mitigated by surrounding CR-T5 framing. T14 carry-forward for glossary link.
- N8 (ADVISORY): Register lock load-bearing across three surfaces now. T14 methodology page should define "primary step" once normatively.
- N9 (BINDING ON ARCHITECT, resolved): Plan corrections per N1-N5+N10 applied before Coder dispatch.
- N10 (ADVISORY): Case 31 asserts caption paragraph NOT in DOM, not empty string render. Implemented via `querySelectorAll('.failures-findings__counts').length === 0`.

---

### UI/UX verdict: PASS-WITH-NOTES

**Date:** 2026-06-10

**Four-question scorecard:**

| Question | Score | Notes |
|---|---|---|
| OWID design fidelity | PASS | Reuses `.failures-findings__counts`. No new tokens. No new CSS classes. |
| 30-second journalist test | PASS | Caption now names all three count categories; cold reader gets a complete picture from the caption line alone. |
| Researcher reproduce-and-cite test | PASS | Parser-state vocabulary consistent with DATA_DICTIONARY §12.6 and the records summary framing_note. |
| WCAG AA accessibility | PASS | No change to existing `.failures-findings__counts` styling. No new classes. |

**Notes (binding on Coder):**

- DESIGN_SYSTEM.md updated from v0.19.4 to v0.19.5. Changes: version header; changelog entry (v0.19.5); §19 heading extended; §19.4 heading extended; §19.4 step 6 expanded with four-cell matrix and records-not-ready semantics; new §19.16 added specifying caption template, four-cell matrix, render condition, function signature, and vitest case specs; closing line updated to v0.19.5.
- No new visual decisions. No new tokens. No new CSS classes. Pitfall 15 not implicated.
- WCAG AA not implicated (no visual change to existing `.failures-findings__counts`).

---

### Reviewer verdict: PASS

**Date:** 2026-06-10

**Checks:**

- AC1. `countsCaptionText()` signature grows optional `nParsedResponses?: number` as fourth parameter; existing three parameters unchanged in order and name. JSDoc updated. PASS.
- AC2. Returned string byte-identical to CDA SME N2 template for all-positive case; all pluralization rules preserved. PASS.
- AC3. `IMPACT_PARAGRAPH_FAILURES`, `IMPACT_PARAGRAPH_FOLLOWUPS`, `TAXONOMY_BLOCK`, `RECORDS_*`, `SECTION_HEADING`, `EMPTY_CAPTION`, badges, blocks, loading/error/malformed strings, `FAILURES_TAB_LABEL`, `DOMAIN_LABEL` unchanged byte-for-byte. PASS.
- AC4. `FailuresFindings.tsx` caption call site sources `nParsedResponses` from `recordsFetchState.data.n_informants` when ready; passes `undefined` when not ready. Render condition gates on `countsCaptionText()` returning non-empty string. PASS.
- AC5. Four-cell empty-state matrix implemented per N3; each cell verified by a vitest case. PASS.
- AC6. No edits to `cdb_core/schemas.py`, `cdb_publish/`, `failures-findings.css`, or any dashboard component other than `FailuresFindings.tsx`. PASS.
- AC7. Cases 27-32 added. Case 9 extended with N6 affirmative check. PASS.
- AC8. Existing cases 1-26 unmodified and pass. Case 9 chrome-isolation extended. PASS.
- AC9. DESIGN_SYSTEM.md §19.16 added; §19.4 step 6 amended; §19 heading extended; §19.4 heading extended; v0.19.5 changelog entry references this verdict file; closing line updated. PASS.
- AC10. T6 section appended; T1-T5 sections unchanged. PASS.
- AC11. `npm run build && npm run test && npm run lint` all pass. PASS.
- AC12. Zero em dashes (U+2014) in entire diff. PASS.
- AC13. Commit message: `feat(dashboard): counts caption names parsed-response count (CR-T6)`; body references kickoff and verdicts file. No em dashes. PASS.
- AC14. No new dependency. No `cdb_core/schemas.py` edit. No `DATA_DICTIONARY.md` edit. No spend-gate language. PASS.
- AC15. No new `var(--...)` references. Pitfall 15 not implicated. PASS.
- Pitfall 4: no "no parsed responses yet" / "available soon" framing anywhere. PASS.
- Pitfall 7: no `worldview` / `believes` / `thinks` / `understands` in any new text including JSDoc and comments. PASS.
- R13: no spend-gate or cost-estimate language. PASS.

---

### Tester verdict: PASS

**Date:** 2026-06-10

**Test run:** `npm run test` from `apps/dashboard/`

**Cases passing (new, CR-T6):**
- Case 27: counts caption byte-identical to three-clause template under family fixtures. PASS.
- Case 28: caption paragraph renders when n_records > 0 and parsed > 0. PASS.
- Case 29: S-clause-only caption under foodJson + recordsFoodJson (n_records=0, parsed=45). PASS.
- Case 30: failure-clause-only caption under familyJson + mocked by_model:[] records (n_records>0, parsed=0). PASS.
- Case 31: caption paragraph NOT in DOM under foodJson + mocked n_informants=0 records (both zero). PASS.
- Case 32: failure-clause-only caption when records fetch returns 404 (records not ready). PASS.

**Cases passing (existing, unmodified):**
- Case 9: chrome-isolation DOM-walk extended with N6 affirmative check -- "parsed primary-step responses" confirmed present, "successful"/"successfully" confirmed absent. PASS.
- Cases 1-8, 10-26: all existing cases pass unchanged. PASS.

---

*T7-T8 verdicts to be appended as subsequent tasks complete.*


## CR-T7: per-record raw-exchange detail surface (gate artifacts, pre-implementation)

**Status:** Plan gates complete; first Coder dispatch correctly STOP-CONDITIONED (gate artifacts had not reached it). This section persists the binding artifacts for the implementation dispatch.

### CDA SME plan verdict: PASS-WITH-NOTES (N1-N8 binding)

Full verdict and the eight binding notes: see the SME memory `​.claude/agent-memory/cda_sme/project_cr_t7_plan_verdict.md`. Resolutions: N1 = BLOCK_PILE_INTERVIEW_* naming; N2 = disposition (a), non-Optional step fields, no fallback string.

### CDA SME bound strings (byte-identical, delivered 2026-06-10)

The authoritative byte-identical strings for all 8 categories (_FRAMING_NOTE_DETAIL, RECORDS_DETAIL_FRAMING, RECORDS_DETAIL_EXPAND_LABEL, the three state strings, the nine BLOCK_* sub-labels, BLOCK_DETAIL_PROVENANCE + note, the DATA_DICTIONARY section 12.7 block) are in `​.claude/agent-memory/cda_sme/project_cr_t7_sme_bound_strings.md`. The Coder pastes from that file verbatim.

### UI/UX plan verdict: PASS-WITH-NOTES (binding section 19.17 spec follows verbatim)

UI/UX VERDICT: PASS-WITH-NOTES

1. OWID design fidelity:      PASS
2. 30-second journalist:      PASS
3. Researcher cite path:      PASS
4. WCAG AA:                   PASS

DESIGN_SYSTEM.md update:      required
(new §19.17 specified below; version bumped v0.19.5 to v0.19.6; changelog entry added)

---

CRITERION 1 -- OWID DESIGN FIDELITY: PASS

The per-record detail surface is a record browser, not a data visualization. The OWID fidelity requirement (axes labeled with units, uncertainty visualized, no bare point estimates) applies to chart components. This surface has no chart elements. The plan correctly reuses `.failures-findings__pre` (max-height 320px, token-only, white-space: pre-wrap, word-break: break-word) from §19.7. No new color usage. No new tokens. All proposed CSS classes use only existing tokens verified against tokens.css. Pitfall 15 compliance is covered by AC-D12. PASS.

CRITERION 2 -- 30-SECOND JOURNALIST TEST: PASS

The expand affordance (per row of the existing per-model summary table, via a button in a new rightmost column) is immediately visible on a table that is already in the reader's field of view. The loading state communicates data-fetching. A cold reader can pivot from the per-model summary table to a raw exchange in two interactions: (1) locate the table row for a model, (2) click the expand button. Block labels (step section headings + BLOCK_PROMPT/BLOCK_RESPONSE/BLOCK_REASONING sub-labels) name each verbatim block. The provenance block provides the G7 researcher path. The navigation pattern decision (see NOTE-1 below) closes the one open question in the plan. PASS conditional on NOTE-1 being applied.

CRITERION 3 -- RESEARCHER REPRODUCE-AND-CITE TEST: PASS

AC-D9 requires all eight sha256_manifest keys visible as key: <code>value</code> and provider_request_id visible. AC-P1 includes PublishedRecordProvenance with sha256_manifest: dict[str, str]. The provenance block reuses the existing .failures-findings__provenance-list / .failures-findings__provenance-item / .failures-findings__provenance-item code pattern from failures.py's decline-interview provenance block. This closes audit gap G7 for the record-browser surface. The chart-side deep-link affordance (D4b) is correctly deferred to a follow-up cycle. PASS.

CRITERION 4 -- WCAG AA: PASS

Native <details>/<summary> cannot be placed as a direct child of <tr> in valid HTML (only <td> and <th> are valid <tr> children). The plan's AC-D3 defers the navigation pattern to UI/UX. The binding pattern specified in §19.17 below uses an expand <button aria-expanded> in a new rightmost <td>, revealing a sibling <tr className="failures-findings__detail-row"><td colSpan={N}>. This preserves valid table structure, is keyboard-accessible via Tab + Enter/Space, and satisfies WCAG 2.1.1. The <details>/<summary> pattern from §19.6 is not appropriate inside a <table> and is NOT used here. Mobile a11y: .failures-findings__pre already has white-space: pre-wrap + word-break: break-word which handles horizontal overflow for verbatim text without requiring overflow-x: auto on the pre element; no new CSS needed. Expand button minimum touch target: min-height 44px, min-width 44px per WCAG 2.5.5 (see §19.17 binding). PASS conditional on NOTE-1 through NOTE-5 being applied.

---

NOTES (all binding; Coder must apply before dispatch):

NOTE-1 (BINDING, NAVIGATION PATTERN): The plan leaves the navigation pattern open ("UI/UX picks"). The binding decision is: add one expand <button aria-expanded="false"> in a new rightmost <th>/<td> column of the per-model summary table (§19.15). The expand button triggers a sibling <tr className="failures-findings__detail-row"> that spans all columns via <td colSpan={6}> (colSpan equals the column count). When collapsed, the detail row has display: none. When expanded, it displays with the lazy-fetched detail body inside it. This is the pattern specified in §19.17 below. Do NOT use native <details>/<summary> inside a <tr> -- that is invalid HTML. Do NOT create a separate per-record list outside the table.

NOTE-2 (BINDING, TABLE COLUMN COUNT): The per-model summary table (§19.15) has 5 data columns (Model, Provider, Runs, QA-pass count, Model version returned). Adding the expand-button column makes 6 columns total. The detail row uses colSpan={6}. The screen-reader-only <caption> is already present (§19.15 binding). The new <th> for the expand column uses aria-label="Expand record details" and is visually empty (expand button renders inside the <td>, not the <th> text).

NOTE-3 (BINDING, EXPAND BUTTON ACCESSIBLE NAME): The expand <button> inside each row uses aria-expanded={boolean} and aria-label derived from the informant_id field: aria-label={"Expand raw exchange for " + informantId}. When aria-expanded is true, the adjacent detail row is visible; when false, display: none. The button text may be a disclosure triangle glyph (▶ collapsed, ▼ expanded) or the text from RECORDS_DETAIL_EXPAND_LABEL (CDA SME N6 bound). Either is acceptable; the accessible name via aria-label is the binding requirement.

NOTE-4 (BINDING, LAZY-FETCH ABORT): Each expand button owns one AbortController instantiated on first expand. The fetch fires on first click only; subsequent opens of the same row reuse the already-fetched data (no re-fetch on close/reopen). The AbortController is cancelled in the React cleanup function for that row's state. This matches AC-D4 semantics.

NOTE-5 (BINDING, PRE HORIZONTAL OVERFLOW): .failures-findings__pre already has white-space: pre-wrap and word-break: break-word. These two rules together prevent horizontal overflow on verbatim content without requiring overflow-x: auto on the pre element. No additional CSS is needed for mobile horizontal overflow on <pre> blocks in this surface. The plan's AC-D13 ("UI/UX specifies horizontal scroll behavior") is resolved: the existing .failures-findings__pre handles it. Do NOT add overflow-x: auto or a new scroll container around the <pre> blocks.

NOTE-6 (ADVISORY, SME NOTE N2 SCHEMA REALITY): The plan's PublishedStepExchange fields are typed str | None. The CDA SME note N2 binding requires reconciling this with cdb_core/schemas.py where FreelistRecord, PileSortRecord, and InterviewRecord have prompt_verbatim: str and response_verbatim: str as required (non-optional) fields. The Coder should apply SME N2 option (a): drop the | None typing on prompt_verbatim and response_verbatim in PublishedStepExchange (they are always populated for a successful InformantRecord). Retain thinking_verbatim: str | None because InformantRecord does not guarantee a thinking field exists. This is a publish-layer decision; no DESIGN_SYSTEM.md change required.

NOTE-7 (ADVISORY): The plan names the step-level section constants as BLOCK_FREELIST_EXCHANGE, BLOCK_PILESORT_EXCHANGE, and BLOCK_PILE_INTERVIEW_EXCHANGE (incorporating CDA SME N1 rename). Within each step section, the sub-labels BLOCK_PROMPT, BLOCK_RESPONSE, and BLOCK_REASONING (existing constants from copy/failures_findings.ts) are reused verbatim for the prompt/response/thinking sub-blocks within that step. The Coder must NOT invent new sub-label constants for these -- use the existing ones.

---

DESIGN_SYSTEM.md UPDATE (version v0.19.5 to v0.19.6):

The following §19.17 content is binding on the Coder. The Coder applies it as AC-D14, bumps the version header from v0.19.5 to v0.19.6, updates the closing line, and prepends the changelog entry below to the changelog block.

CHANGELOG ENTRY TO PREPEND (before the existing v0.19.5 entry):

- **v0.19.6** (Per-record raw-exchange detail surface, CR-T7, 2026-06-10) adds §19.17 specifying the per-record expand affordance on the successful-records summary table, the per-record detail body structure, the step-section layout, the provenance block, and mobile/accessibility rules. Navigation pattern decision: expand button in a new rightmost column of the §19.15 per-model table, revealing a sibling full-width detail row (colSpan={6}). New CSS classes in `failures-findings.css`: `.failures-findings__detail-row`, `.failures-findings__detail-cell`, `.failures-findings__expand-btn`, `.failures-findings__detail-step`, `.failures-findings__detail-step-heading`. No new tokens. Eight new vitest cases (33-40); case 9 extended over the expanded detail DOM. Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-06-10-collection-records-rework-verdicts.md` T7 section); UI/UX PASS-WITH-NOTES (`docs/status/2026-06-10-collection-records-rework-verdicts.md` T7 section).

SECTION §19.17 CONTENT (insert before the "---" separator preceding §20):

### 19.17 Per-record raw-exchange detail surface (binding, CR-T7, v0.19.6)

The per-record detail surface adds an expand affordance to each row of the §19.15 per-model summary table. Expanding a row lazy-fetches `/data/records/{slug}/{informant_id}.json` and renders the three CDA step exchanges plus a provenance block.

**Navigation pattern (binding NOTE-1):**

The §19.15 per-model summary table gains one new column: an expand column to the right of the five existing data columns. Total column count: 6.

- New `<th>` for the expand column: visually empty, `aria-label="Expand record details"`, class `.failures-findings__successes-th`.
- New `<td>` in each data row: contains one `<button>` per informant row (see expand button spec below). Class `.failures-findings__successes-td`.
- When expanded: a sibling `<tr className="failures-findings__detail-row">` follows the data row. It contains a single `<td className="failures-findings__detail-cell" colSpan={6}>`. When collapsed: `display: none` on the detail row.

Do NOT use `<details>/<summary>` inside `<tr>`. That is invalid HTML structure.

**Expand button spec (binding):**

```tsx
<button
  className="failures-findings__expand-btn"
  aria-expanded={isExpanded}
  aria-label={`Expand raw exchange for ${informantId}`}
  onClick={() => handleToggle(informantId)}
>
  {isExpanded ? '▼' : '▶'}
</button>
```

CSS class `.failures-findings__expand-btn`:
- `background: transparent`
- `border: var(--border-width) solid var(--color-border)`
- `border-radius: var(--border-radius-sm)`
- `padding: var(--space-1) var(--space-2)`
- `cursor: pointer`
- `font-size: var(--font-size-xs)`
- `color: var(--color-text-secondary)`
- `min-height: 44px` (WCAG 2.5.5 touch target floor)
- `min-width: 44px`
- Focus ring: `outline: 2px solid var(--color-info); outline-offset: 2px` on `:focus-visible`

**Detail row CSS (binding):**

CSS class `.failures-findings__detail-row`: no additional styling beyond inherited table row rules. The collapsed state is controlled by `display: none` applied inline or via a CSS class toggle; use whichever pattern is consistent with the component's existing state management.

CSS class `.failures-findings__detail-cell`:
- `padding: var(--space-4)`
- `background: var(--color-surface)`
- `border-bottom: var(--border-width) solid var(--color-border)`

**Lazy-fetch state machine (binding NOTE-4):**

Each row has independent fetch state: `idle | loading | fetch-failed | malformed | ready`. Fetch fires on first expand click only; subsequent opens reuse cached data. One AbortController per row, cancelled in React cleanup.

- `idle`: detail row not yet visible; no fetch initiated.
- `loading`: detail row visible; renders `RECORDS_DETAIL_LOADING` as `<p className="failures-findings__status">`.
- `fetch-failed`: detail row visible; renders `RECORDS_DETAIL_FETCH_FAILED` as `<p className="failures-findings__status">`.
- `malformed`: detail row visible; renders `RECORDS_DETAIL_MALFORMED` as `<p className="failures-findings__status">`.
- `ready`: detail row visible; renders the step exchanges and provenance block.

**Detail body structure (binding):**

Inside `.failures-findings__detail-cell`, when `ready`, content renders in this order:

1. Free-list step section (if `freelist` is non-null in the detail JSON).
2. Pile-sort step section (if `pile_sort` is non-null).
3. Interview step section (if `interview` is non-null).
4. Provenance block (always rendered when state is `ready`).

When a top-level step is null (not present on this informant), that step's entire section is suppressed. Do NOT render an empty section or a "not available" placeholder. Absence is a first-class state (§19.9 posture carried forward).

**Step section structure (binding CDA SME N4):**

Each step section uses a two-level label structure. The outer level names the CDA step (using one of the three SME-bound constants: `BLOCK_FREELIST_EXCHANGE`, `BLOCK_PILESORT_EXCHANGE`, `BLOCK_PILE_INTERVIEW_EXCHANGE`). The inner level names each verbatim sub-block (using existing constants `BLOCK_PROMPT`, `BLOCK_RESPONSE`, `BLOCK_REASONING` -- the last only when `thinking_verbatim` is non-empty).

```tsx
<div className="failures-findings__detail-step">
  <p className="failures-findings__detail-step-heading">
    {BLOCK_FREELIST_EXCHANGE}  {/* or PILESORT or INTERVIEW */}
  </p>
  {/* Prompt sub-block */}
  <p className="failures-findings__block-label">{BLOCK_PROMPT}</p>
  <pre className="failures-findings__pre">{step.prompt_verbatim}</pre>
  {/* Response sub-block */}
  <p className="failures-findings__block-label">{BLOCK_RESPONSE}</p>
  <pre className="failures-findings__pre">{step.response_verbatim}</pre>
  {/* Reasoning sub-block -- only when thinking_verbatim is non-empty */}
  {step.thinking_verbatim && (
    <>
      <p className="failures-findings__block-label">{BLOCK_REASONING}</p>
      <pre className="failures-findings__pre">{step.thinking_verbatim}</pre>
    </>
  )}
</div>
```

CSS class `.failures-findings__detail-step`:
- `display: flex`
- `flex-direction: column`
- `gap: var(--space-2)`
- `margin-bottom: var(--space-6)`

CSS class `.failures-findings__detail-step-heading`:
- `font-size: var(--font-size-sm)`
- `font-weight: var(--font-weight-bold)`
- `color: var(--color-text-primary)`
- `line-height: var(--line-height-tight)`
- `margin-bottom: var(--space-2)`

Reuses `.failures-findings__block-label` (existing) for sub-block labels. Reuses `.failures-findings__pre` (existing, §19.7) for all `<pre>` blocks. No new tokens.

**Pre horizontal overflow (binding NOTE-5):**

`.failures-findings__pre` already has `white-space: pre-wrap` and `word-break: break-word`. These handle horizontal overflow for verbatim text. Do NOT add `overflow-x: auto` to these elements or wrap them in a separate horizontal scroll container. The existing 320px `max-height` with `overflow-y: auto` is the only scroll behavior on `<pre>` blocks.

**Provenance block (binding):**

Below the three step sections, a provenance block renders using the existing pattern from the decline-interview provenance block:

```tsx
<p className="failures-findings__block-label">{BLOCK_DETAIL_PROVENANCE}</p>
<ul className="failures-findings__provenance-list">
  <li className="failures-findings__provenance-item">
    provider_request_id: <code>{provenance.provider_request_id ?? '(none)'}</code>
  </li>
  <li className="failures-findings__provenance-item">
    model_id: <code>{provenance.model_id}</code>
  </li>
  <li className="failures-findings__provenance-item">
    model_version_returned: <code>{provenance.model_version_returned}</code>
  </li>
  {/* One <li> per sha256_manifest key, eight total */}
  {Object.entries(provenance.sha256_manifest).map(([key, val]) => (
    <li key={key} className="failures-findings__provenance-item">
      {key}: <code>{val}</code>
    </li>
  ))}
</ul>
```

Reuses `.failures-findings__block-label`, `.failures-findings__provenance-list`, `.failures-findings__provenance-item`, `.failures-findings__provenance-item code` (all existing from §19). No new CSS classes required for the provenance block.

**CSS summary -- new classes only (all token-only, no new tokens):**

| Class | Rule summary |
|---|---|
| `.failures-findings__detail-row` | No new rules required (inherits table row behavior; collapsed via `display: none` toggle) |
| `.failures-findings__detail-cell` | `padding: var(--space-4)`; `background: var(--color-surface)`; `border-bottom: var(--border-width) solid var(--color-border)` |
| `.failures-findings__expand-btn` | See expand button spec above |
| `.failures-findings__detail-step` | `display: flex; flex-direction: column; gap: var(--space-2); margin-bottom: var(--space-6)` |
| `.failures-findings__detail-step-heading` | `font-size: var(--font-size-sm); font-weight: var(--font-weight-bold); color: var(--color-text-primary); line-height: var(--line-height-tight); margin-bottom: var(--space-2)` |

All other rendering reuses existing classes. No new tokens introduced.

**No new tokens (binding §19.11 posture):** All CSS rules use only tokens already defined in `tokens.css`. No new `--*` custom properties introduced by this section.

**Accessible landmark:** The detail cell does not require its own `aria-labelledby` because its accessible name is provided by the expand button's `aria-label` (which names the informant_id). The detail row has no separate section landmark.

**Chrome-isolation extension (binding):** Case 9 extension must walk the expanded detail DOM (excluding `<pre>` nodes per §19.13 convention) and confirm zero instances of: `worldview`, `believes`, `thinks`, `understands`, `cooperative` (outside counterfactual context), bare `refusal` in LSB chrome text. The CDA SME N5 affirmative zero-count assertions apply.

**Vitest cases (binding):**
- Case 33: byte-identity on all new SME-bound strings (RECORDS_DETAIL_EXPAND_LABEL, RECORDS_DETAIL_FRAMING, RECORDS_DETAIL_LOADING, RECORDS_DETAIL_FETCH_FAILED, RECORDS_DETAIL_MALFORMED, BLOCK_FREELIST_EXCHANGE, BLOCK_PILESORT_EXCHANGE, BLOCK_PILE_INTERVIEW_EXCHANGE, BLOCK_DETAIL_PROVENANCE).
- Case 34: each row of the per-model summary table contains an expand button with aria-expanded="false" in initial state.
- Case 35: clicking an expand button triggers a fetch to `/data/records/family/{informant_id}.json` (mocked fetch); ready-state DOM contains the three step-heading labels and all eight sha256_manifest keys rendered inside `<code>` elements.
- Case 36: expand loading state renders RECORDS_DETAIL_LOADING byte-identical.
- Case 37: expand fetch-failed state renders RECORDS_DETAIL_FETCH_FAILED byte-identical.
- Case 38: expand malformed state renders RECORDS_DETAIL_MALFORMED byte-identical.
- Case 39: a fixture record with `interview: null` does not render the interview step section heading or its sub-blocks; free-list and pile-sort sections are present.
- Case 40: case 9 chrome-isolation extended over the expanded detail DOM (excluding `<pre>` nodes); affirmative zero-count assertions pass for all six forbidden substrings.

---

REQUIRED BEFORE MERGE (numbered):

1. Apply NOTE-1: implement navigation pattern as expand button in new rightmost column plus sibling detail row (colSpan=6). Do NOT use <details>/<summary> inside <tr>.

2. Apply NOTE-3: expand button aria-label is "Expand raw exchange for {informantId}" (dynamically set per row). aria-expanded={isExpanded} reflects current state.

3. Apply NOTE-4: lazy-fetch AbortController per row; fetch fires only on first expand click; subsequent opens reuse cached data.

4. Apply NOTE-5: no additional horizontal scroll CSS on <pre> blocks; .failures-findings__pre handles overflow via pre-wrap + break-word.

5. Apply NOTE-7: sub-block labels (BLOCK_PROMPT, BLOCK_RESPONSE, BLOCK_REASONING) are the existing exported constants from copy/failures_findings.ts, not new constants.

6. Apply AC-D14: add §19.17 to DESIGN_SYSTEM.md per the specification above. Bump version v0.19.5 to v0.19.6. Prepend the changelog entry specified above. Update the closing line version string from v0.19.5 to v0.19.6.

7. Apply AC-D12: before committing, grep tokens.css to confirm every var(--...) reference in the five new CSS classes exists. All five classes use only existing tokens per the spec above; no new tokens required.

8. Apply SME N1 rename: the interview step constant is BLOCK_PILE_INTERVIEW_EXCHANGE (not BLOCK_INTERVIEW_EXCHANGE), per CDA SME binding note N1.

9. Confirm that the new <th> for the expand column is included in the colSpan count: colSpan must equal the total column count including the expand column (6 if the table has 5 data columns + 1 expand column).

10. Verify that the DESIGN_SYSTEM.md closing line reads "*End of DESIGN_SYSTEM.md v0.19.6..." (not v0.19.5) after the update."

---

## CR-T7 Coder Implementation Note (2026-06-10)

Applied by Coder agent. All notes N1-N8 and NOTE-1 through NOTE-7 applied. The following deviations from the spec text are recorded per the Architect plan:

**N2 disposition (a) applied:** The three step fields on PublishedRecordDetail (freelist, pile_sort, pile_interview) are non-Optional. Records missing step fields are skipped with WARNING. No RECORDS_DETAIL_STEP_MISSING fallback string shipped.

**NOTE-7 superseded by CDA SME N4:** Nine new per-step sub-label constants (BLOCK_FREELIST_PROMPT, BLOCK_FREELIST_RESPONSE, BLOCK_FREELIST_REASONING, BLOCK_PILESORT_PROMPT, BLOCK_PILESORT_RESPONSE, BLOCK_PILESORT_REASONING, BLOCK_PILE_INTERVIEW_PROMPT, BLOCK_PILE_INTERVIEW_RESPONSE, BLOCK_PILE_INTERVIEW_REASONING) are used as inner sub-block labels for each CDA step. The existing BLOCK_PROMPT, BLOCK_RESPONSE, BLOCK_REASONING constants are scoped to the follow-up interview surface and are NOT reused here. Additionally, three new outer step heading constants (BLOCK_FREELIST_EXCHANGE, BLOCK_PILESORT_EXCHANGE, BLOCK_PILE_INTERVIEW_EXCHANGE) are added for the step-level headings, as referenced in the §19.17 spec and Case 33 vitest spec.

**DESIGN_SYSTEM.md version transition:** The UI/UX spec was written at v0.19.5 baseline. TM-A bumped master to v0.20.0 before this task began. The version bump applied is v0.20.0 to v0.20.1 (not v0.19.5 to v0.19.6). The §19.17 body text in DESIGN_SYSTEM.md and the changelog entry are adjusted accordingly; all other content is byte-identical to the verdicts file spec.

**Cloudflare file-count arithmetic:** 1319 existing files + 1291 new detail files = 2610 total, well under the 20,000 Cloudflare Pages file-count limit.

**Vitest Case 39 deviation:** Under N2 disposition (a), null steps cannot appear on valid records. Case 39 was adjusted to test that a full-step fixture renders all three step headings (positive assertion) rather than testing null-step suppression (which the type guard would reject as malformed data). The suppression guard (if (!step) return null) remains in the component as defensive code; the test verifies the positive case instead.
