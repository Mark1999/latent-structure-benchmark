# LSB Tester Verdict — Phase 5 T1

**Task:** Phase 5 T1 — cdb_publish skeleton + manifest writer
**Commit reviewed:** `79d1877`
**Tester:** LSB Tester agent (claude-sonnet-4-6)
**Date:** 2026-05-09
**Prerequisite gate verdicts:**
- Reviewer PASS: `docs/status/2026-05-09-phase5-t1-reviewer-verdict.md`

---

## TESTER VERDICT: PASS-WITH-NOTES

Gap-fill tests written and committed as `test(publish):` (see below).
All 5 Coder tests pass. All 3 gap-fill tests pass. Full suite clean.

---

## Steps executed

### 1. Targeted test run

```
uv run pytest tests/cdb_publish/ -v
```

Result: **5/5 passed** (Coder's original suite).

### 2. Full suite

```
uv run pytest --tb=short -q
```

Result (pre-gap-fill): **1220 passed** — consistent with Reviewer's count.
Result (post-gap-fill): **1223 passed** (1220 + 3 new gap-fill tests).

### 3. Static checks

```
uv run ruff check packages/cdb_publish/ scripts/publish.py
```
Result: All checks passed.

```
uv run mypy packages/cdb_publish/
```
Result: Success: no issues found in 4 source files.

### 4. Real-corpus smoke test

```
uv run python scripts/publish.py --results-dir data/results --output-dir /tmp/tester-publish
```

Output: `Built manifest with 2 domains: family, holidays`
Exit code: **0**

Manifest contents verified:
- `family`: `analysis_version=0.2`, `n_models=11`, `model_ids` sorted (claude-opus-4-6 … x-ai/grok-4)
- `holidays`: `analysis_version=0.2`, `n_models=9`, `model_ids` sorted
- domains sorted by slug (`family` before `holidays`)

### 5. Coder test inspection

| Test | Behaviour covered | Verdict |
|---|---|---|
| `test_build_single_domain` | Single domain, manifest fields, on-disk JSON | Confirmed |
| `test_build_empty_results_dir` | Empty dir → `domains: []` | Confirmed |
| `test_build_selects_latest_version` | 0.1 vs 0.2 → 0.2 selected | Confirmed |
| `test_build_invalid_json_raises` | Bad JSON → `DomainValidationError` with `.path` | Confirmed |
| `test_build_deterministic` | Mocked clock → byte-identical output | Confirmed |

### 6. No real API calls

grep for `httpx`, `requests`, `aiohttp`, `urllib.request`, `anthropic` (as import),
`openai`, `google.generativeai` in `tests/cdb_publish/`:

Two hits on `"anthropic"` — both are fixture dict string values (`"provider": "anthropic"`,
`"collection_method": "anthropic_api"`). Zero import-statement hits. **PASS.**

---

## Coverage gaps identified and addressed

### Gap A — Domain slug ordering not unit-tested (FILLED)

The Coder's tests never write two domains in reverse-alphabetical order to assert
the manifest sorts them. The smoke run confirmed correct behaviour on real data
(`family` before `holidays`), but this was not machine-verifiable in pytest.

Test added: `test_build_domains_sorted_by_slug` — writes `zeta` then `alpha`,
asserts `manifest.domains` order is `["alpha", "zeta"]`.

### Gap B — `model_ids` sorting with unsorted input not tested (FILLED)

`test_build_single_domain` checks `model_ids == ["test-model-a", "test-model-b"]`
but the input is already alphabetical. No test exercised the sort with input in
reverse order.

Test added: `test_build_model_ids_sorted` — provides `["z-model", "m-model", "a-model"]`
and asserts sorted output `["a-model", "m-model", "z-model"]`.

### Gap C — CLI exit code 1 on validation failure not in pytest (FILLED)

Reviewer item G confirmed this manually. No pytest test exercised `scripts/publish.py`
as a subprocess to verify the exit code contract.

Test added: `test_cli_exits_1_on_validation_failure` — runs `scripts/publish.py`
via `subprocess.run` with a broken domain JSON, asserts exit code 1 and
`"Validation error"` in stderr.

### Gap D — Nonexistent `--results-dir` not handled gracefully (NOT FILLED — forward-carry)

Passing a nonexistent path to `--results-dir` causes an unhandled exception
(traceback to stderr, Python default exit code 1). The CLI does not emit a
user-friendly error message for this case. Exit code is still 1; no data
corruption occurs. This is a minor UX gap, not a data-contract failure.

Not filled here: adding graceful handling would require editing `scripts/publish.py`,
which is outside the Tester's scope (Tester writes tests, not production code).
Forward-carry for T2 or a dedicated CLI-hardening task.

### Gap E — Required args (argparse) not unit-tested (NOT FILLED — low priority)

argparse enforces exit 2 when `--results-dir` or `--output-dir` is absent.
This is stdlib behaviour and needs no bespoke test. Not filled.

---

## Ruff note

Running `ruff check --fix` on the updated test file corrected two pre-existing
issues in the Coder's original code:
- `UP017`: `timezone.utc` → `datetime.UTC` (line 263, in `test_build_deterministic`)
- `I001`: unsorted import block (import order after gap-fill additions)

These were fixable-with-`--fix` lint issues; none were logic changes. The file
is now ruff-clean.

---

## Tests written (gap-fills)

- `tests/cdb_publish/test_build.py`: `test_build_domains_sorted_by_slug` — asserts manifest.domains sorted by slug when written in reverse-alpha order
- `tests/cdb_publish/test_build.py`: `test_build_model_ids_sorted` — asserts model_ids sorted when provided in reverse order
- `tests/cdb_publish/test_build.py`: `test_cli_exits_1_on_validation_failure` — subprocess test asserting exit code 1 and stderr message on validation failure

## Test run summary

```
8/8 passed in tests/cdb_publish/
1223/1223 passed full suite
ruff: clean
mypy: clean
```

---

## Failures

None.

## Required before next task

None. Forward-carry Gap D (nonexistent `--results-dir` graceful handling) to
T2 or a CLI-hardening task per Architect's discretion.
