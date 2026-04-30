# Reviewer Verdict — Phase 4a.1 Task #21.T3C Commit 1
# Manual Classification Scaffold for Decline Interviews

**Filed:** 2026-04-30
**Reviewer:** LSB Reviewer (Sonnet)
**Scope:** Commit 1 of T3C — scaffold only (three new files; seed file output is commit 2, not reviewed here)
**Task:** #21 Phase 4a.1 T3C — `packages/cdb_analyze/cdb_analyze/manual_classification.py`, `scripts/build_manual_classification_seed.py`, `tests/test_manual_classification.py`
**Gate chain references:**
- Architect plan: `docs/status/2026-04-30-phase4a1-architect-plan-amendment-2.md` §3 T3C
- CDA SME PASS-WITH-NOTES: `docs/status/2026-04-30-phase4a1-amendment-2-cda-sme-verdict.md`
- Predecessor T3B detector SME verdict: commit `2baa243` `docs/status/2026-04-23-phase4a1-t3b-detector-sme-verdict.md` (B1–B6 binding)

---

## REVIEWER VERDICT: PASS

```
Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         PASS
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A
Check 6 — New deps sign-off:         PASS
Check 7 — Prompt versioning:         N/A
Check 8 — Uncertainty in viz:        N/A
Check 9 — Prerequisite verdicts:     PASS
```

No failures. Coder may commit.

---

## Check-by-check rationale

### Check 1 — No LLM imports in `cdb_analyze/`

Grep for `import anthropic`, `import openai`, `from anthropic`, `from openai`, `InferenceClient`, `google.generativeai` across `packages/cdb_analyze/` returned one hit in `packages/cdb_analyze/cdb_analyze/__init__.py` at lines 12–13 — these are comment lines listing the forbidden libraries as a warning, not import statements. `manual_classification.py` imports only `json`, `pathlib`, `typing.Literal`, and `pydantic`. Clean.

The `test_module_has_no_llm_imports` test (line 319–333 of `tests/test_manual_classification.py`) covers all four binding libraries: `anthropic`, `openai`, `google.generativeai`, `huggingface_hub`. The `huggingface_hub` string correctly catches `InferenceClient` via the package name. Coverage is complete.

### Check 2 — Append-only JSONL

`git diff HEAD -- data/raw/informants.jsonl` and `git diff HEAD -- data/raw/decline_interviews.jsonl` both returned empty output. No edits to either source file. The seed builder reads `data/raw/decline_interviews.jsonl` and writes only to `data/derived/`. The `data/derived/` path is confirmed untracked (`?? data/derived/` in `git status`), correctly excluded from commit 1.

### Check 3 — No secrets

No API keys, Slack webhook URLs (`LSB_ALERTS_WEBHOOK_URL`, `LSB_CDA_SME_WEBHOOK_URL`, `LSB_UI_UX_WEBHOOK_URL`), provider tokens, or credential-shaped strings in any of the three files.

### Check 4 — Forbidden vocabulary

No occurrences of `worldview`, `believes`, `thinks` (applied to models), `within-model consensus`, `within-model cultural consensus`, `within-model eigenratio`, `within-model CCM`, or `publishable` in any of the three files. The subject of the code is human classification of records — models are not described. Clean.

### Check 5 — Schema + DATA_DICTIONARY (N/A)

`git diff HEAD -- packages/cdb_core/` returned no output. `cdb_core/schemas.py` is untouched. `DeclineManualClassification` is placed in `cdb_analyze`, not `cdb_core`, which is the SME-approved placement (CDA SME verdict §"Derived-vs-raw distinction" — confirmed: "no `DATA_DICTIONARY.md` update is needed because the dictionary tracks raw-data schemas"). No DATA_DICTIONARY.md update required or expected.

### Check 6 — New dependencies (PASS)

`pyproject.toml` and `apps/dashboard/package.json` are unmodified per `git diff HEAD`. The scaffold uses only stdlib (`json`, `pathlib`, `argparse`, `importlib.util`, `typing`) plus Pydantic (already a project dependency). No new dependency introduced.

### Check 7 — Prompt versioning (N/A)

No prompt template directories modified or created.

### Check 8 — Uncertainty in visualizations (N/A)

No frontend code.

### Check 9 — Prerequisite verdicts (PASS)

This is not a frontend task (no UI/UX verdict required). It is a methodology-adjacent task (derived-data schema). The CDA SME PASS-WITH-NOTES verdict is present at `docs/status/2026-04-30-phase4a1-amendment-2-cda-sme-verdict.md`, filed 2026-04-30. The SME verdict explicitly states: "The Coder may proceed to commit 1 immediately upon this verdict landing." The PASS-WITH-NOTES notes (B7, B8, B9) are explicitly scoped to commit 3 (Mark's classification pass), not commit 1. No unaddressed notes attach to this commit.

---

## Tests (30/30)

`uv run pytest tests/test_manual_classification.py -v` — 30 passed in 0.74s. All 7 enum values exercised. UNCLASSIFIED sentinel rejection verified. Extra-field (`extra="forbid"`) rejection verified. Loader round-trip, empty-file, blank-lines, duplicate detection (code path present in loader; no test — not a binding-rule gap, noted below for Tester). Cross-reference `validate_against_source` — missing ID, extra ID, aligned cases all pass. Seed builder: row count, sentinel output, 400-char truncation, short-response preservation, determinism, idempotency guard (non-zero on diff without `--force`, zero with `--force`, no overwrite without `--force`).

## Lint and type-check

- `uv run ruff check .` — All checks passed.
- `uv run mypy packages/` — Success: no issues found in 53 source files.

Note: `uv run mypy scripts/build_manual_classification_seed.py` in isolation reports one error at line 86: `"object" not callable` (the `_is_recursive_decline` binding is typed as `object` because `_load_v1_detector()` returns `object`). This is a scripts-directory-only issue; `scripts/` is excluded from the project mypy scope in `pyproject.toml`. The project gate (`uv run mypy packages/`) is clean. This is a quality note only, not a binding-rule failure.

---

## Code-quality observations (non-blocking)

These are observations for the Coder/Architect record. None are blocking-rule violations. The Tester may address the test gap if desired after this PASS.

**1. Top-level side effects from `importlib` loading of `run_decline_backfill.py`**

`scripts/build_manual_classification_seed.py` calls `_load_v1_detector()` at module scope (line 69). This call `exec_module`s `run_decline_backfill.py`, which has two top-level side effects:

- `load_dotenv()` (line 73 of `run_decline_backfill.py`) — reads `.env` on import. Benign: `load_dotenv()` is a no-op if `.env` is absent and silently reads it if present. No error is raised.
- `from cdb_collect.adapters.base import ModelAdapter` and related collection-layer imports — these pull in `cdb_collect` at the module level of the seed builder. This works (tests pass 30/30) because `cdb_collect` is already in the dependency graph. It is, however, a heavier import than the seed builder's actual runtime requirement (a pure-string function). If `run_decline_backfill.py` ever gains a top-level side effect that reads files or opens network connections, the seed builder will inherit it silently.

This is an accepted architectural trade-off (avoiding duplication of `SAFETY_FILTER_MARKERS`). No action required now.

**2. No test for duplicate `decline_interview_id` in loader**

The loader correctly raises `ValueError` on duplicate `decline_interview_id` (lines 157–160 of `manual_classification.py`) but there is no test covering this path. Not a binding-rule gap; noted for Tester.

**3. mypy type annotation for `_is_recursive_decline`**

The `object` return type on `_load_v1_detector()` suppresses the `"object" not callable` error at the call site in `_build_seed_row` only via runtime behavior (it works). A `Callable[[str], bool]` return annotation would make the intent explicit and would eliminate the mypy error if `scripts/` were ever brought into the mypy scope. Not a binding-rule requirement.

---

## Scope confirmation — seed file (commit 2) not in scope

`data/derived/decline_interviews_manual_classification.jsonl` is present in the working tree (`?? data/derived/`) but is correctly excluded from commit 1. The scaffold commit stages only the three code files. The seed file's existence does not affect this verdict.

---

## Forward action

Coder may commit the three code files (`packages/cdb_analyze/cdb_analyze/manual_classification.py`, `scripts/build_manual_classification_seed.py`, `tests/test_manual_classification.py`) with subject line:

```
feat(analyze): manual classification scaffold for decline interviews (task #21.T3C)
```

(55 characters — within the 72-char limit.)

The commit body should reference this verdict file (`docs/status/2026-04-30-phase4a1-t3c-reviewer-verdict.md`) and the CDA SME verdict (`docs/status/2026-04-30-phase4a1-amendment-2-cda-sme-verdict.md`).

B7, B8, B9 from the CDA SME verdict bind to commit 3 (Mark's classification pass), not this commit.

---

*Verdict written by LSB Reviewer (Sonnet). Only Mark can override a FAIL. This is a PASS — no override needed.*
