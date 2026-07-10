# Reviewer verdict: forced-default-sampling adapter support (batch A)

**Date:** 2026-07-10
**Task:** Tier 2, forced-default-sampling support in openai_compat and anthropic adapters
**Scope:** packages/cdb_collect/cdb_collect/adapters/base.py, openai_compat.py, anthropic.py, runner.py; tests/unit/test_openai_compat_forced_default.py; tests/unit/test_anthropic_adapter_forced_default.py; tests/fixtures/openai_response.json
**Prerequisite gate:** CDA SME PASS-WITH-NOTES 2026-07-10 (docs/status/2026-07-10-batchA-gpt55-temperature-cda-sme-verdict.md)

---

## REVIEWER VERDICT: FAIL

```
Check 1  No LLM imports in cdb_analyze:     PASS
Check 2  Append-only JSONL:                 PASS
Check 3  No secrets:                        PASS
Check 4  Forbidden vocabulary:              PASS
Check 5  Schema + DATA_DICTIONARY:          N/A
Check 6  New deps sign-off:                 N/A
Check 7  Prompt versioning:                 N/A
Check 8  Uncertainty in viz:                N/A
Check 9  Prerequisite gate verdicts:        FAIL
```

---

## Failures

**Check 9, N1 verbatim string not reproduced.**

CDA SME binding note N1 states: "capacity_note verbatim on every gpt-5.5 record" and gives the required text exactly. The implementation and the test both substitute a compressed paraphrase.

Required (N1 verbatim):
`"Provider (OpenAI) forces temperature to default 1.0 for this model, so the 0.3 pile-sort and interview temperatures could not be applied. top_p is likewise not accepted. Sampling regime is hotter than the LSB protocol on pile_sort and interview steps."`

Implemented (`_FORCED_DEFAULT_NOTE` in packages/cdb_collect/cdb_collect/adapters/openai_compat.py line 64, mirrored in tests/unit/test_openai_compat_forced_default.py line 33):
`"provider forces temperature=1.0; top_p not accepted; sampling hotter than protocol on pile_sort and interview (CDA SME 2026-07-10, N1)"`

The two strings do not match on capitalization, phrasing, or content (the N1 text names the specific protocol values 0.3 explicitly; the implementation does not). The word "verbatim" in N1 is unambiguous. This is also the note that the test asserts against, so both the adapter and the test must be corrected together.

**Secondary (citation error, non-blocking alone but documented here).**

packages/cdb_collect/cdb_collect/adapters/base.py line 56 says "CLAUDE.md §8 binding note N5 (forward precedent)." N5 is a CDA SME verdict note, not a CLAUDE.md §8 rule. The correct citation is "CDA SME 2026-07-10 N5." The line above already cites the correct document; this line should reference the same source.

---

## Required before merge

1. Replace `_FORCED_DEFAULT_NOTE` in packages/cdb_collect/cdb_collect/adapters/openai_compat.py with the verbatim N1 text:
   `"Provider (OpenAI) forces temperature to default 1.0 for this model, so the 0.3 pile-sort and interview temperatures could not be applied. top_p is likewise not accepted. Sampling regime is hotter than the LSB protocol on pile_sort and interview steps."`

2. Update `_EXACT_NOTE` in tests/unit/test_openai_compat_forced_default.py (lines 33-36) to the same verbatim N1 text, so the test asserts the correct string.

3. Fix the citation in packages/cdb_collect/cdb_collect/adapters/base.py line 56: change "CLAUDE.md §8 binding note N5" to "CDA SME 2026-07-10 N5."

4. Re-run tests after corrections: the `test_forced_default_note_exact_string` test in test_openai_compat_forced_default.py must pass with the corrected verbatim string.

Note: The Anthropic adapter note in packages/cdb_collect/cdb_collect/adapters/anthropic.py is covered by N5 (forward precedent pattern), not by N1 (which is gpt-5.5-specific). The Anthropic note does not need to reproduce the OpenAI-specific N1 verbatim text; it correctly follows the N5 pattern. No change required there.

---

## Fix application (orchestrator, 2026-07-10)

All four required-before-merge items applied and mechanically verified:
1. `_FORCED_DEFAULT_NOTE` in openai_compat.py replaced with the verbatim N1 text.
2. `_EXACT_NOTE` in test_openai_compat_forced_default.py updated to match; the
   string-equality test passes.
3. base.py citation corrected to "CDA SME 2026-07-10 N5".
4. Gates re-run: 25 targeted tests pass, ruff clean, mypy clean.

Note on provenance: the paraphrase originated in the orchestrator's Coder
dispatch spec, not in the Coder's implementation. The Anthropic-adapter note
(N5 pattern) is unchanged per the Reviewer's ruling. Conditions satisfied;
merging under the enumerated-conditions provision.
