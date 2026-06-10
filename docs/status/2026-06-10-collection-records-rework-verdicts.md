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
| CR-T6 | Counts caption update | B | Pending T5 |
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

*T2-T8 verdicts to be appended as subsequent tasks complete.*

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

*T2-T8 verdicts to be appended as subsequent tasks complete.*
