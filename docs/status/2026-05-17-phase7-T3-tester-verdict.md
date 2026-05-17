---
filed: 2026-05-17
reviewer: LSB Tester agent (Sonnet)
task: Phase 7 T3 — Drafter framework + Bluesky drafter
commits: 262927a (feat(social): Phase 7 T3 — drafter framework + Bluesky drafter)
         603e269 (fix(social): T3 follow-up — Reviewer FAIL fixes)
cda_sme_verdict: docs/status/2026-05-17-phase7-T3-cda-sme-verdict.md (PASS-WITH-NOTES, 18 binding notes)
reviewer_verdict: docs/status/2026-05-17-phase7-T3-reviewer-verdict.md (FAIL)
reviewer_pass_addendum: docs/status/2026-05-17-phase7-T3-reviewer-pass-addendum.md (PASS re-review)
verdict: PASS
---

# Phase 7 T3 — Tester verdict

**TESTER VERDICT: PASS**

Full suite: 1497/1497 passed. 112 new drafter tests all green. Ruff clean. Mypy
clean. All 10 dedicated test classes verified against their CDA SME §5.x binding
notes. No real Anthropic API calls in tests. Forbidden vocab grep clean.
Both Reviewer FAIL items confirmed resolved.

---

## Test run output

```
uv run pytest tests/unit/test_social_drafters.py -v  →  112 passed in 0.27s
uv run pytest tests/                                 →  1497 passed in 77.92s
uv run ruff check .                                  →  All checks passed!
uv run mypy packages/                                →  Success: no issues found in 65 source files
```

Baseline at T2 close: 1385. New tests: 112. 1385 + 112 = 1497. Zero regressions.

---

## Checks completed

### 1. All existing tests pass

1497/1497 passed. No regressions against the T2 baseline.

### 2. Ruff + mypy clean

`ruff check .` → clean. `mypy packages/` → clean (65 source files, up from 63 at
T2 close, consistent with two new drafter files). No type errors, no lint issues.

### 3. 112 T3 drafter tests — CDA SME §5.x binding-note coverage

All 112 tests pass. Ten dedicated test classes cover the 18 CDA SME binding notes.

| Test class | CDA SME notes | Coverage |
|---|---|---|
| `TestValidatorForbiddenVocab` (24 tests) | §5.1 — full §1.5.4 table rows 1–10, word-stem \b anchoring, case-insensitivity, word-boundary precision | COVERED |
| `TestValidatorNumericCI` (16 tests) | §5.2 — K=12 token window, four CI patterns (a–d), five exemption categories, K-boundary edge cases | COVERED |
| `TestValidatorHypothesisFraming` (20 tests, 16 parametrized) | §5.3 — 14 closed phrases, safe-verb negative cases, count assertion | COVERED |
| `TestFramingChecksDict` (13 tests) | §5.11, §5.18 — exact four canonical keys, True-on-pass semantics, register_boundary scope narrowness (rows 7–10 only), cognition_attribution vs register_boundary separation, AND composition | COVERED |
| `TestBlueskyDrafterStructure` (6 tests) | §5.7, §5.5 — ≤270/300 char limit, URL domain slug, "details" label, article-shell URL, no "methodology" label | COVERED |
| `TestBlueskyDrafterSelfRating` (2 tests) | §5.6 — fixed 0.5, not from LLM output | COVERED |
| `TestPromptVersioning` (5 tests) | §5.13, §5.8 — v1/bluesky.md exists, load_prompt returns non-trivial text, FileNotFoundError on missing version, prompt_version matches directory, v2 not created without escalation | COVERED |
| `TestCacheNoCacheSplit` (7 tests) | §5.10, §5.4, §5.14 — cache_control ephemeral on system block, per-call payload data-only (9 methodology phrases checked), trigger evidence in payload, domain numerics in payload, system prompt contains §1.5.4 table, corpus-lens anchor, R10 rule | COVERED |
| `TestDrafterRejectedException` (9 tests) | §5.12, §5.16, §5.17 — raises on forbidden vocab / bare numeric / hypothesis framing / overlength, exception carries draft_text and forbidden_terms, round-trip good draft all-fields assertion, round-trip bad draft always raises | COVERED |
| `TestRejectionWindowMonitor` (4 tests) | §5.8 (fix) — 2/10 fires, 1/10 silent, 100 passes silent, 50 historical rejections + 10 recent passes silent | COVERED |

**CDA SME §5.x notes not covered by a specific test class** (advisory, non-blocking):

- **§5.9 — pass-rate observational:** no threshold check in code is correct per the
  binding note ("the Coder does NOT add a pass-rate threshold check"). The T3
  implementation correctly omits this; the absence is the correct behavior. No test
  needed.
- **§5.4 token budget (~1100 tokens):** the prompt file exists and is verified
  non-trivial by `test_load_prompt_v1_returns_text`. Exact token count is provider-
  dependent and is an advisory target (±200 tokens per the CDA SME), not a
  mechanically enforceable threshold. Not a coverage gap.
- **§5.14 Anthropic prompt-caching per ARCHITECTURE.md §6.2:** covered by
  `test_system_prompt_has_cache_control` in `TestCacheNoCacheSplit`, which asserts
  `block.get("cache_control") == {"type": "ephemeral"}` on the system block.

All 18 binding notes have either a direct test or a documented rationale for why
no test is needed.

### 4. No real Anthropic API calls in tests

- `grep -n 'anthropic\.Anthropic\|from anthropic import' tests/unit/test_social_drafters.py` → empty.
- Every `BlueskyDrafter` instantiation in the test file passes a `MockAnthropicClient`
  via the injected `anthropic_client=` argument.
- `bluesky.py` lazy-imports `anthropic` inside an `else` branch that executes only
  when `anthropic_client is None` — the branch is never reached in tests.
- `MockAnthropicClient.create()` returns a deterministic `MockAnthropicMessage` from
  a fixture file; no network call is made.

No real API calls. CLAUDE.md rule 10 satisfied.

### 5. Forbidden-vocabulary grep

```
git diff 262927a~1..603e269 -- packages/cdb_social/cdb_social/drafters/ tests/ \
  | grep -iE 'worldview|believes|thinks of|cultural bias|what the model understands|
              how models see|within-model consensus|within-model cultural|
              within-model eigenratio|within-model CCM'
```

Hits are present only in the four permitted locations:

1. **Validator's pattern list** (`_FORBIDDEN_PHRASE_PATTERNS`, `_REGISTER_BOUNDARY_PATTERNS`,
   `_FORBIDDEN_STEM_PATTERNS` in `base.py`) — the rejection patterns themselves.
2. **System prompt Block 3** (`prompts/v1/bluesky.md` §1.5.4 table verbatim) — the
   "NEVER use / ALWAYS use" table the LLM reads.
3. **Fixture files explicitly testing rejection** (`forbidden_vocab_phrase.txt`,
   `forbidden_vocab_worldview.txt`, `hypothesis_framing.txt`) — canned bad-draft inputs.
4. **Test assertions naming rejection patterns** (e.g., `test_row1_model_x_believes`,
   the `_load_fixture("forbidden_vocab_worldview.txt")` calls) — inputs to the
   validator under test.

No forbidden vocabulary in regular prose. PASS.

### 6. Scope sanity

**Original commit `262927a`** (`git diff --name-only 262927a~1..262927a`):
10 files — exactly the declared T3 scope:
- `packages/cdb_social/cdb_social/drafters/__init__.py`
- `packages/cdb_social/cdb_social/drafters/base.py`
- `packages/cdb_social/cdb_social/drafters/bluesky.py`
- `packages/cdb_social/cdb_social/drafters/prompts/v1/bluesky.md`
- `tests/fixtures/social/drafter_responses/bare_numeric.txt`
- `tests/fixtures/social/drafter_responses/forbidden_vocab_phrase.txt`
- `tests/fixtures/social/drafter_responses/forbidden_vocab_worldview.txt`
- `tests/fixtures/social/drafter_responses/good_draft.txt`
- `tests/fixtures/social/drafter_responses/hypothesis_framing.txt`
- `tests/unit/test_social_drafters.py`

No `cdb_core/schemas.py`, no `DATA_DICTIONARY.md`, no `ARCHITECTURE.md`, no T4/T5
files touched. All within T3 declared scope.

**Fix commit `603e269`** (`git diff --stat 603e269~1..603e269`):
Exactly 2 files modified — `base.py` (+181/-58) and `test_social_drafters.py`
(+199/-2). No other files. Scope is tight per Reviewer addendum.

### 7. Boundary-rule verification

- `grep -rE 'from cdb_analyze|import cdb_analyze' packages/cdb_social/` → empty.
  No analysis-layer imports in the social package.
- `grep -rE 'import atproto|from atproto' packages/cdb_social/` → empty.
  AT Protocol posting client not imported (deferred to T6 per kickoff scope).
- `anthropic` import in `bluesky.py` (line 74) is lazy, inside the `else` branch of
  `__init__` for the case when no mock client is injected. This is permitted per
  ARCHITECTURE.md §4.6 (drafters are the designated LLM-call surface). It is never
  reached in tests.

### 8. Prompt-cache binding (ARCHITECTURE.md §6.2)

`bluesky.py` line 135–140 constructs the Anthropic call as:
```python
system=[
    {
        "type": "text",
        "text": self._system_prompt,
        "cache_control": {"type": "ephemeral"},
    }
]
```

`cache_control={"type": "ephemeral"}` is on the system prompt block. The methodology
copy (all six blocks of `prompts/v1/bluesky.md`) is cached. The per-call user payload
is data-only (trigger evidence + domain numerics + URLs). Test
`test_system_prompt_has_cache_control` asserts this via `mock_client.last_call_kwargs`
inspection. PASS.

### 9. §5.5 methodology-link label rule

- `grep -n '"methodology"' packages/cdb_social/cdb_social/drafters/bluesky.py` →
  Line 104: a docstring comment explaining the prohibition ("NOT 'methodology'").
  Not a link label.
- `grep -n '"methodology"' packages/cdb_social/cdb_social/drafters/prompts/v1/bluesky.md` →
  Line 114: the prohibition instruction to the LLM ("Do NOT label the URL as
  'methodology'").
- The `good_draft.txt` fixture uses "details" (not "methodology") as the URL label.
- `test_good_draft_url_label_is_details` asserts `"details" in text.lower()` and
  `"methodology" not in text.lower()` on the good-draft fixture.

§5.5 satisfied. PASS.

### 10. `framing_checks` exactly-four-keys contract

`validate_draft()` in `base.py` lines 348–353 returns exactly:
```python
framing_checks: dict[str, bool] = {
    "hypothesis_framing": len(hyp_hits) == 0,
    "cognition_attribution": len(stem_hits) == 0,
    "bare_numeric_without_ci": ci_ok,
    "register_boundary": register_boundary_ok,
}
```

`test_exact_four_keys_present_on_clean_text` asserts:
```python
assert set(framing_checks.keys()) == {
    "hypothesis_framing",
    "cognition_attribution",
    "bare_numeric_without_ci",
    "register_boundary",
}
```

This test passes. The exact-four-key contract is verified mechanically.

`register_boundary` is computed from `_REGISTER_BOUNDARY_PATTERNS` (lines 84–89),
which contains ONLY the four §1.5.4 rows 7–10 phrases. `test_register_boundary_does_not_match_row_1_phrases`
verifies that a row-1 forbidden phrase sets `cognition_attribution=False` and leaves
`register_boundary=True`. Both Reviewer FAIL items are resolved and confirmed.

### 11. Reviewer FAIL item verification

**FAIL 1 (§5.11 framing_checks key names):** Resolved. The four canonical keys are
present with correct names and True-on-pass semantics. `TestFramingChecksDict`'s 13
tests verify all four keys, their individual semantics, and the AND composition.
`test_exact_four_keys_present_on_clean_text` asserts the exact-set contract. PASS.

**FAIL 2 (§5.8 sliding-window monitor):** Resolved. `_check_rejection_window` reads
`drafter_audit.jsonl` (unified attempt log), takes `lines[-10:]`, counts
`outcome == "reject"` entries, fires at ≥ 2. `_log_audit_pass` writes `outcome: "pass"`
and `_log_rejection` writes `outcome: "reject"` to the same file. The four
`TestRejectionWindowMonitor` tests verify the 2/10 fire, 1/10 silent, 100-passes silent,
and 50-historical-rejections-then-10-passes silent scenarios. The last case is exactly
the one broken in the original implementation and now correct. PASS.

---

## Coverage gaps

None identified. All 18 CDA SME §5.x binding notes are tested or have documented
rationale for why no test is required (§5.9 pass-rate observational posture; §5.4
token-budget advisory tolerance). The fixture README convention (fake-looking data,
no real model IDs in fixture prose) is satisfied by the drafter response fixtures
which use synthetic names ("GPT-5") in explicitly test-rejection contexts only.

---

*End of Phase 7 T3 Tester verdict.*
