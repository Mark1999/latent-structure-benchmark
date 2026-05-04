# Task 16.A — Tester Verdict

**Date:** 2026-05-04
**Tester:** LSB Tester agent (Sonnet 4.6)
**Commit reviewed:** `7f8f7f7` (Task 16.A — bump adapter caps to 16384 + capture `thoughts_token_count`)
**Gap-coverage commit:** `6c987bf`
**Plan:** `/opt/lsb-agent/docs/status/2026-05-04-task-16-architect-plan.md` §2 Task 16.A
**SME verdict:** `/opt/lsb-agent/docs/status/2026-05-04-task-16-cda-sme-verdict.md` (PASS-WITH-NOTES)
**Reviewer verdict:** `/opt/lsb-agent/docs/status/2026-05-04-task-16-a-reviewer-verdict.md` (PASS)

---

## VERDICT: PASS

---

## Coverage item checklist

**Item 1 — Gemini cap assertion test (`max_output_tokens=16384`, `thinking_budget=1024`):** PASS.

`test_do_call_uses_correct_max_output_tokens()` and `test_do_call_uses_correct_thinking_budget()` in `tests/unit/test_google_adapter.py` intercept `genai.Client.models.generate_content` via `MagicMock.side_effect`, capture the `GenerateContentConfig` object, and assert `cfg.max_output_tokens == 16384` and `cfg.thinking_config.thinking_budget == 1024`. No real API call made.

**Item 2 — OpenRouter payload assertion (`max_tokens=16384`, `include_reasoning=True`):** PASS.

`test_request_payload_has_max_tokens_16384()` and `test_request_payload_has_include_reasoning_true()` in `tests/unit/test_openrouter_adapter.py` patch `adapter._client.post` with a side-effect that captures the `json=` keyword argument and asserts both fields are present at the expected values.

**Item 3 — `thoughts_token_count` capture (Gemini): present / attribute absent / `usage_metadata` absent:** PASS.

Three dedicated tests:
- `test_thoughts_token_count_captured_when_present` — `thoughts_token_count=512` on mock, asserts `result.thoughts_token_count == 512`.
- `test_thoughts_token_count_zero_when_attribute_absent` — helper omits the attribute via `del usage.thoughts_token_count`, asserts `0`.
- `test_thoughts_token_count_zero_when_usage_metadata_absent` — `mock_response.usage_metadata = None`, asserts `0`.

All three cover the `getattr(usage, "thoughts_token_count", None) or 0` production path in `google.py` lines 168–170.

**Item 4 — `thoughts_token_count` capture (OpenRouter): present / `completion_tokens_details` absent / `reasoning_tokens` absent within details:** PASS.

Three dedicated tests:
- `test_thoughts_token_count_captured_from_reasoning_response` — uses `openrouter_response_with_reasoning.json` fixture (see item 10), asserts `result.thoughts_token_count == 1000`.
- `test_thoughts_token_count_zero_when_completion_details_absent` — standard `openrouter_response.json` fixture lacks `completion_tokens_details`, asserts `0`.
- `test_thoughts_token_count_zero_when_reasoning_tokens_absent_in_details` — injects `completion_tokens_details` without `reasoning_tokens` key, asserts `0`.

All three cover the `completion_details.get("reasoning_tokens") or 0` production path in `openrouter.py` lines 171–172.

**Item 5 — `AdapterResult` default:** PASS.

`test_adapter_result_thoughts_token_count_default_zero()` in `tests/unit/test_adapter_base.py` constructs `AdapterResult(...)` without passing `thoughts_token_count` and asserts the field is `0`.

**Item 6 — `AdapterResult` round-trip via `dataclasses.asdict()`:** N/A.

`dataclasses.asdict()` is not used on `AdapterResult` anywhere in production code (`packages/cdb_collect/`). The runner accesses `AdapterResult` fields directly. No serialization round-trip test is needed; the field is exercised by its consumers (the step-record constructors, which will be tested in Task 16.B). The frozen dataclass itself is verified correct by items 3 and 4 above.

**Item 7 — `text_first_500` and `thinking_first_300` extraction unaffected:** PASS.

`test_thinking_text_not_included_in_text()` (Gemini) and `test_complete_returns_adapter_result()` (both adapters) verify that `thinking_text` and `text` remain correctly separated. The Gemini `test_complete_returns_adapter_result` asserts `result.text.startswith("1. Mother")`, `result.thinking_text.startswith("Thinking about family members")`, and `result.thoughts_token_count == 256` all on the same call, confirming the three fields are populated independently. (Note: `text_first_500` and `thinking_first_300` are runner-level truncation fields, not `AdapterResult` fields. They are covered by the existing runner tests which predated this commit and continue to pass.)

**Item 8 — No real API calls:** PASS.

All Google adapter tests use `unittest.mock.MagicMock` / `patch` to intercept `genai.Client.models.generate_content`. All OpenRouter tests use `patch.object(adapter._client, "post", ...)` returning `httpx.Response` objects built from fixture JSON. No `httpx.Client` or `genai.Client` call reaches a real endpoint. No real API keys are required to run the suite (the `api_key="fake-key"` and `api_key="sk-or-v1-test"` strings are clearly not real credentials; the OpenRouter key pattern requires `sk-or-v1-[a-zA-Z0-9]{60,}`).

**Item 9 — No `data/raw/*.jsonl` reads in tests:** PASS.

Searched all three test files for `data/raw` and `data/probes` references. None found. Fixture data is read exclusively from `tests/fixtures/`.

**Item 10 — `openrouter_response_with_reasoning.json` is synthesized, not extracted from a real run:** PASS.

The fixture is structurally plausible (valid OpenRouter chat completion shape with `reasoning_tokens` in `completion_tokens_details`) but contains deliberate deviations that confirm it is synthesized: `total_tokens` is listed as 1140 but the actual sum of `prompt_tokens` (95) + `completion_tokens` (45) is only 140 — a discrepancy that would not appear in a real provider response. The model ID (`z-ai/glm-5.1`) and `reasoning_tokens: 1000` value are plausible shapes but the integer inconsistency confirms manual construction. No API key material is present.

---

## Gap-coverage tests added

**Gap question 1 (Gemini cap-exhausted-reasoning signature through the adapter path):** ADDED.

`test_cap_exhausted_reasoning_signature_through_adapter()` added to `tests/unit/test_google_adapter.py`. This drives `GeminiAdapter._do_call` with a mock response having `candidates_token_count=0`, `thoughts_token_count=16384`, `finish_reason_name="MAX_TOKENS"` and asserts that the returned `AdapterResult` has `output_tokens == 0`, `thoughts_token_count == 16384`, and `stop_reason == "MAX_TOKENS"`. This exercises the `google.py` extraction code paths (lines 162–171), not just the `AdapterResult` dataclass constructor tested by `test_adapter_result_cap_exhausted_reasoning_invariant` in `test_adapter_base.py`. Both tests together confirm the invariant holds end-to-end.

Rationale for adding: the plan §2 explicitly flagged this as a gap question and the SME verdict's Axis 2 notes the diagnostic invariant specifically. Testing only the dataclass would leave a gap in the extraction logic coverage for the primary use case of the new field.

**Gap question 2 (OpenRouter `include_reasoning=True` for non-reasoning model):** NOT ADDED.

The `test_thoughts_token_count_zero_when_completion_details_absent()` test already exercises the adapter response path for a model that does not return `completion_tokens_details` (equivalent to a non-reasoning model). The payload construction of `"include_reasoning": True` is unconditional — it is hardcoded regardless of model. `test_request_payload_has_include_reasoning_true()` confirms it is always sent. A separate test for a "non-reasoning model" would test the identical code path with a different fixture but would add no new assertion over the existing tests. Not added.

---

## Test run output

**Targeted run (23 tests across three files):**

```
tests/unit/test_adapter_base.py::test_adapter_result_creation PASSED
tests/unit/test_adapter_base.py::test_adapter_result_frozen PASSED
tests/unit/test_adapter_base.py::test_adapter_result_thoughts_token_count_default_zero PASSED
tests/unit/test_adapter_base.py::test_adapter_result_thoughts_token_count_explicit PASSED
tests/unit/test_adapter_base.py::test_adapter_result_cap_exhausted_reasoning_invariant PASSED
tests/unit/test_google_adapter.py::test_do_call_uses_correct_max_output_tokens PASSED
tests/unit/test_google_adapter.py::test_do_call_uses_correct_thinking_budget PASSED
tests/unit/test_google_adapter.py::test_thoughts_token_count_captured_when_present PASSED
tests/unit/test_google_adapter.py::test_thoughts_token_count_zero_when_attribute_absent PASSED
tests/unit/test_google_adapter.py::test_thoughts_token_count_zero_when_usage_metadata_absent PASSED
tests/unit/test_google_adapter.py::test_complete_returns_adapter_result PASSED
tests/unit/test_google_adapter.py::test_thinking_text_not_included_in_text PASSED
tests/unit/test_google_adapter.py::test_cap_exhausted_reasoning_signature_through_adapter PASSED  ← new
tests/unit/test_openrouter_adapter.py::test_complete_returns_adapter_result PASSED
tests/unit/test_openrouter_adapter.py::test_api_key_not_in_raw_response PASSED
tests/unit/test_openrouter_adapter.py::test_retry_on_rate_limit PASSED
tests/unit/test_openrouter_adapter.py::test_retry_on_server_error PASSED
tests/unit/test_openrouter_adapter.py::test_scrub_response PASSED
tests/unit/test_openrouter_adapter.py::test_request_payload_has_max_tokens_16384 PASSED
tests/unit/test_openrouter_adapter.py::test_request_payload_has_include_reasoning_true PASSED
tests/unit/test_openrouter_adapter.py::test_thoughts_token_count_captured_from_reasoning_response PASSED
tests/unit/test_openrouter_adapter.py::test_thoughts_token_count_zero_when_completion_details_absent PASSED
tests/unit/test_openrouter_adapter.py::test_thoughts_token_count_zero_when_reasoning_tokens_absent_in_details PASSED

23 passed in 1.85s
```

**`thoughts_token_count` filter run (8 tests):**

```
8 passed, 1043 deselected in 3.16s
```

**Full suite (post gap-commit):**

```
1052 passed, 26313 warnings in 14.11s
```

(Pre-commit count was 1051; +1 new test.)

**`uv run ruff check tests/unit/test_google_adapter.py`:** All checks passed.

**`uv run mypy packages/`:** Success: no issues found in 53 source files. (The test file itself has 6 pre-existing `no-any-return` mypy errors in `async def _run() -> None` inner functions — these predate this commit, are not caught by `uv run mypy packages/`, and are not introduced by the gap-coverage test.)

---

## Coverage gaps

**None remaining.** All 10 checklist items pass or are explicitly N/A with documented rationale. The one gap-coverage test added (item above) is now committed and the full suite is green at 1052.

**Unrelated issue surfaced (not fixed in this commit):** The `_run()` inner functions in `test_google_adapter.py` are typed as `-> None` but return `await adapter._do_call(...)`. This produces `no-any-return` mypy errors when the file is checked in isolation. This is a pre-existing pattern in the committed test file (present across 7 of the 8 `_run()` functions including those predating Task 16.A). Surfacing as a note for the Architect; it does not affect the `uv run mypy packages/` gate and does not introduce test incorrectness, but it is untidy. Recommend fixing in a future `chore(test):` pass.

---

## Final disposition

Task 16.A commit `7f8f7f7` passes all ten coverage criteria. One gap-coverage test was added in commit `6c987bf` (`tests/unit/test_google_adapter.py::test_cap_exhausted_reasoning_signature_through_adapter`). Full project suite is 1052 passed, 0 failed. Ruff, mypy (`packages/`), and the thoughts-token-count filter run all pass.

**The Coder may proceed to Task 16.B.**

---

*End of verdict. Filed at `docs/status/2026-05-04-task-16-a-tester-verdict.md`.*
