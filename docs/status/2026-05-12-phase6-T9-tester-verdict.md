---
filed: 2026-05-12
reviewer: LSB Tester agent (Sonnet)
commit_under_test: e3ade52
gap_fill_commit: (see below — filed after test run)
task: Phase 6 T9 — failures-as-findings data layer
verdict: PASS
---

# Phase 6 T9 — Tester verdict

**TESTER VERDICT: PASS**

The Coder's 28 tests cover the primary acceptance criteria. Gap analysis
identified 9 uncovered regression risks; 20 gap-fill tests were written
and added to `tests/cdb_publish/test_failures_gap_fill.py`. All 1306 tests
pass suite-wide.

---

## Coder tests reviewed

`tests/cdb_publish/test_failures.py` — 28 tests covering:

- Sanitization: each pattern category fires (Anthropic, OpenRouter, HuggingFace,
  generic sk-, Slack webhook, local paths); benign strings pass through; no silent
  drop; recursive dict/list walker.
- `build_failures()`: join via `originating_informant_id`; join via
  `originating_failure_id`; orphaned decline-interview not published; missing-domain
  failure not published; empty-domain file emitted with `records: []`; `framing_note`
  field present (length > 50 only); sort order correct; sanitization fires in
  published output; deterministic non-timestamp content; source files unmodified
  (SHA256 before/after); manifest map covers all slugs; `record_type` discriminator
  correct; `originating_outcome_class` is `null` on failure records and non-null on
  decline_interview records.

---

## Gap analysis

### Gap 1 — `framing_note` exact verbatim assertion [CRITICAL]

**Gap:** The Coder's `test_framing_note_present` checks `len(framing_note) > 50`
only. No test asserts equality against the CDA SME §5.1 required text. A future
edit that paraphrases the framing note would pass the Coder's test undetected.

**Fix:** `TestFramingNoteVerbatim` — two tests assert the `_FRAMING_NOTE` constant
in `failures.py` and the published JSON `framing_note` field are both byte-equal
to the CDA SME §5.1 verbatim text.

### Gap 2 — `sk-` regex pattern literal assertion [CRITICAL]

**Gap:** No test asserts the pattern string `\bsk-[a-zA-Z0-9_-]{50,}` (the
CDA SME §5.4 required shape). A pattern change (e.g., dropping the word-boundary
anchor or lowering the minimum) would not be caught by behavior tests alone if
the test inputs happen to still match.

**Fix:** `TestSkRegexPatternShape.test_generic_sk_pattern_is_word_boundary_anchored_50_min`
asserts the compiled pattern's `.pattern` attribute equals the exact §5.4 string.

### Gap 3 — 49-char `sk-` NOT redacted (exact boundary) [IMPORTANT]

**Gap:** The Coder's `test_api_key_generic_sk_short_not_matched` uses 20 chars
(well below the minimum). The exact boundary (49 = not redacted; 50 = redacted)
is not probed. A minimum changed from 50 to, say, 40 would pass the 20-char test.

**Fix:** `TestSkRegexBoundary` — two tests: 49-char token (not redacted) and
50-char token (is redacted).

### Gap 4 — `DATA_DICTIONARY.md` §5.2 anti-attribution sentence [IMPORTANT]

**Gap:** No test verifies that the CDA SME §5.2 binding sentence ("Each enum value
names the LSB-side detection rule ... The enum values do not attribute intent,
belief, or state-of-mind to the model") is present in `DATA_DICTIONARY.md` §12.
Future doc edits could remove this text without test failure.

**Fix:** `TestDataDictionaryStaticText.test_data_dictionary_anti_attribution_sentence_present`
reads the file and asserts both key clauses are present inside the §12 section.

### Gap 5 — `DATA_DICTIONARY.md` §5.5 provider-quote advisory [IMPORTANT]

**Gap:** Same class of gap — no test for the §5.5 "Note on quotation" advisory.

**Fix:** `TestDataDictionaryStaticText.test_data_dictionary_provider_quote_advisory_present`
and `test_data_dictionary_forbidden_vocabulary_absent_in_section_12`.

### Gap 6 — API-key leak regression on published JSON output [CRITICAL]

**Gap:** The Reviewer's highest-risk check confirms no secrets are in the current
output, but no test loads the emitted JSON and asserts zero matches for
`sk-ant-api`, `sk-or-v1-`, `hf_`, `xoxb-`, `/opt/lsb-agent/`, `/home/lsb/`,
`/home/markd/` as a durable regression guard. The Coder's
`test_sanitization_fires_in_published_records` checks that specific seeded strings
are absent but does not enumerate the full forbidden-pattern set on all records.

**Fix:** `TestPublishedJsonNoSecrets` — two tests: (a) iterates all string values
in published JSON and asserts no forbidden pattern matches; (b) separately checks
`data/raw/` path pattern in record string values.

### Gap 7 — `originating_outcome_class` all 7 enum values round-trip verbatim

**Gap:** The Coder's tests confirm `originating_outcome_class` is non-null on
decline_interview records and null on failure records, but do not assert all 7
values (`empty_output`, `refusal_string_match`, `single_degenerate_pile`,
`parse_failure`, `http_error`, `timeout`, `other`) survive to the published JSON
unmodified.

**Fix:** `TestOriginatingOutcomeClassAllValues.test_all_seven_outcome_classes_surface_verbatim`
builds one synthetic DI fixture per value and asserts all 7 appear in the output.

### Gap 8 — `cost_usd` intentionally absent [IMPORTANT]

**Gap:** No test asserts `cost_usd` is absent from published records (plan §5,
CLAUDE.md R14 spirit). The field exists on raw `decline_interviews.jsonl` records
and could be accidentally included in a future schema revision.

**Fix:** `TestCostUsdAbsent` — two tests: records-level and top-level file.

### Gap 9 — `Manifest` Pydantic schema `failures` field [IMPORTANT]

**Gap:** The Coder's `test_manifest_map_all_slugs` checks the dict returned by
`build_failures()` but never instantiates `Manifest` to verify the schema actually
accepts the `failures` field. Also: no test asserts the field name matches
`DATA_DICTIONARY.md` (schema-dictionary drift guard per CLAUDE.md §6 rule 6 spirit).

**Fix:** `TestManifestSchemaFailuresField` — four tests: field exists; default is
`{}`; round-trips through `model_dump()`; field name matches a string present in
`DATA_DICTIONARY.md`.

### Gap 10 — `PublishedFailuresFile` Pydantic validation of actual output

**Gap:** The plan's acceptance criterion 3 requires that emitted files validate
against the `PublishedFailuresFile` schema. The Coder's tests never call
`PublishedFailuresFile.model_validate()` on the emitted JSON.

**Fix:** `TestPublishedFailuresFilePydanticValidation` — three tests: normal
family output validates; empty-domain validates; output with both record types
validates.

---

## Tests written

`tests/cdb_publish/test_failures_gap_fill.py`:

- `TestFramingNoteVerbatim::test_framing_note_module_constant_verbatim` — asserts `_FRAMING_NOTE` constant equals CDA SME §5.1 verbatim text
- `TestFramingNoteVerbatim::test_framing_note_in_published_file_verbatim` — asserts published JSON `framing_note` equals CDA SME §5.1 verbatim text
- `TestSkRegexPatternShape::test_generic_sk_pattern_is_word_boundary_anchored_50_min` — asserts regex pattern string is `\bsk-[a-zA-Z0-9_-]{50,}`
- `TestSkRegexBoundary::test_sk_49_chars_not_redacted` — 49-char `sk-` token not redacted (one below minimum)
- `TestSkRegexBoundary::test_sk_50_chars_is_redacted` — 50-char `sk-` token is redacted (at minimum boundary)
- `TestDataDictionaryStaticText::test_data_dictionary_anti_attribution_sentence_present` — §5.2 anti-attribution clause in DATA_DICTIONARY.md §12
- `TestDataDictionaryStaticText::test_data_dictionary_provider_quote_advisory_present` — §5.5 provider-quote advisory in DATA_DICTIONARY.md §12
- `TestDataDictionaryStaticText::test_data_dictionary_forbidden_vocabulary_absent_in_section_12` — no forbidden vocabulary in §12 LSB-authored prose
- `TestPublishedJsonNoSecrets::test_no_secrets_in_published_json` — published JSON string values contain no secret patterns
- `TestPublishedJsonNoSecrets::test_no_data_raw_paths_in_published_records` — published record string values contain no `data/raw/` paths
- `TestOriginatingOutcomeClassAllValues::test_all_seven_outcome_classes_surface_verbatim` — all 7 enum values round-trip to published output
- `TestCostUsdAbsent::test_cost_usd_not_in_published_records` — `cost_usd` absent from every record
- `TestCostUsdAbsent::test_cost_usd_not_in_top_level_published_file` — `cost_usd` absent from top-level file object
- `TestManifestSchemaFailuresField::test_manifest_has_failures_field` — Manifest schema has `failures` field
- `TestManifestSchemaFailuresField::test_manifest_failures_field_default_is_empty_dict` — default is `{}`
- `TestManifestSchemaFailuresField::test_manifest_failures_field_round_trips` — round-trips through `model_dump()`
- `TestManifestSchemaFailuresField::test_manifest_failures_field_name_matches_data_dictionary` — field name in schema matches DATA_DICTIONARY.md (drift guard)
- `TestPublishedFailuresFilePydanticValidation::test_family_output_validates_as_published_failures_file` — full output validates against schema
- `TestPublishedFailuresFilePydanticValidation::test_empty_domain_output_validates_as_published_failures_file` — empty-domain output validates
- `TestPublishedFailuresFilePydanticValidation::test_both_record_types_validate` — output with both record types validates

---

## Test run output

```
20/20 gap-fill tests passed (tests/cdb_publish/test_failures_gap_fill.py)
28/28 Coder tests passed (tests/cdb_publish/test_failures.py)
1306/1306 suite-wide passed
```

No failures. No errors. 26313 warnings (all pre-existing sklearn/numpy RuntimeWarnings
in MDS tests — unrelated to T9).

---

## Coverage gaps (none)

All identified gaps are covered. No functions left uncovered. The two items
from the task description that were assessed as not requiring additional tests:

- **SHA256 stability of `data/raw/`:** fully covered by Coder's
  `test_source_files_not_modified` (SHA256 before/after on all three raw files).
- **`record_type` discriminator covers both values:** fully covered by Coder's
  `test_record_type_discriminator_present` (asserts both `"failure"` and
  `"decline_interview"` are valid) AND by gap-fill
  `test_both_record_types_validate` (Pydantic validation level).

---

*End of Phase 6 T9 Tester verdict.*
