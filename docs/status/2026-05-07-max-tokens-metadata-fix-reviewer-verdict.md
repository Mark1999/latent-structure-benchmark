# Reviewer Verdict — max_tokens metadata fix (commit 75917d0)

**Task:** Fix-forward metadata accuracy — runner.py hardcoded max_tokens=4096
**Commit:** `75917d0` — fix(collect): record actual max_tokens in InformantRecord
**Date:** 2026-05-07
**Reviewer:** LSB Reviewer agent (Claude Sonnet 4.6)
**Predecessor finding:** Reviewer-T2 commit `f7ca048`, note 1 in `docs/status/2026-05-07-phase4b-t2-reviewer-verdict.md`
**Mark's ruling:** Option A — fix forward only, no backfill (2026-05-07)
**Precedent:** `memory/project_metadata_fix_forward_precedent.md`

---

## Scope

This is a focused metadata-accuracy fix landing between Phase 4b T2 and T3. The only
changed files are:

- `packages/cdb_collect/cdb_collect/adapters/base.py` — `AdapterResult.max_tokens_used` field added
- `packages/cdb_collect/cdb_collect/adapters/anthropic.py` — sets `max_tokens_used=_max_tokens`
- `packages/cdb_collect/cdb_collect/adapters/google.py` — sets `max_tokens_used=_max_tokens`
- `packages/cdb_collect/cdb_collect/adapters/huggingface.py` — sets `max_tokens_used=_max_tokens`
- `packages/cdb_collect/cdb_collect/adapters/openai_compat.py` — sets `max_tokens_used=_max_tokens`
- `packages/cdb_collect/cdb_collect/adapters/openrouter.py` — sets `max_tokens_used=effective_max_tokens`
- `packages/cdb_collect/cdb_collect/runner.py` — line 238: `4096` → `freelist_result.max_tokens_used`
- `docs/DATA_DICTIONARY.md` — version bump v0.1.12 → v0.1.13 + editorial note
- `tests/unit/test_runner_max_tokens.py` — 4 new tests

No changes to `data/raw/`, `packages/cdb_core/`, `packages/cdb_analyze/`, prompt templates,
`pyproject.toml`, or any frontend file.

---

## 15-rule scorecard (CLAUDE.md §6 + SECURITY_AND_HARDENING.md §9)

| Rule | Description | Result | Notes |
|---|---|---|---|
| R1 | No API keys / secrets in committed files | PASS | No credential-shaped strings in any changed file |
| R2 | No `dangerouslySetInnerHTML` in dashboard | N/A | No frontend files changed |
| R3 | No CSP weakening | N/A | No frontend files changed |
| R4 | No edits to existing lines in `data/raw/informants.jsonl` | PASS | `git diff 75917d0^ 75917d0 -- data/raw/` is empty |
| R5 | No new dependency without Architect sign-off | PASS | `pyproject.toml` and `package.json` unchanged |
| R6 | No LLM client imports in `cdb_analyze/` | PASS | grep finds only the prohibition comment in `cdb_analyze/__init__.py`; no actual imports |
| R7 | Schema-adjacent changes co-update `DATA_DICTIONARY.md` | PASS | `AdapterResult` is in `cdb_collect` not `cdb_core`; `InformantRecord` and `GroundingRef` in `cdb_core/schemas.py` are unchanged. The co-update is present and exceeds the requirement: version bumped to v0.1.13, full editorial note on `max_tokens` field, changelog entry |
| R8 | Frontend PRs carry a UI/UX verdict | N/A | No frontend files changed |
| R9 | Grounding submission PRs run full validation | N/A | No grounding data changed |
| R10 | Webhook URL secrets never committed | PASS | No webhook URLs in any changed file |
| R11 | `SECURITY.md` not materially weakened | N/A | `SECURITY.md` unchanged |
| R12 | §1.5.4 language guardrails — no forbidden vocabulary | PASS | No forbidden vocabulary found in changed files, commit message, or new test docstrings |
| Prompt versioning (§6 rule 8) | No in-place edits to existing versioned prompts | PASS | No `prompts/` files changed |
| Uncertainty in viz (§6 rule 11) | No new viz without uncertainty | N/A | No visualization changes |
| Conventional Commits (§8) | Subject line ≤72 chars, correct scope | PASS | Subject `fix(collect): record actual max_tokens in InformantRecord` is 57 characters; body references Reviewer-T2 finding, Option A ruling, append-only preservation, precendent memory file |

---

## Fix correctness assessment

### runner.py line 238 (the load-bearing change)

Before: `max_tokens=4096,  # see docs/status/2026-04-22-phase4a-adapter-fix-verdict.md`
After:  `max_tokens=freelist_result.max_tokens_used,`

Correct. The `freelist_result` parameter to `_assemble_record()` is the "primary" adapter
result in all collection modes, as stated in the commit body:
- single_pass: the freelist call result
- two_pass: the freelist call result
- baseline_sort: `ps_result` is passed as `freelist_result`

The path is correct in all modes.

### AdapterResult.max_tokens_used field

Type: `int`, default `4096`. Correct — backward-compatible with existing test fixtures
that do not set this field.

### Adapter implementations

- **anthropic.py**: `_max_tokens = 4096` captured as a local variable before the kwargs
  dict; `max_tokens_used=_max_tokens` appended to the returned `AdapterResult`. Value
  matches what the adapter sends to the API. Correct.
- **google.py**: `_max_tokens = 16384` captured before the config object;
  `max_tokens_used=_max_tokens` appended. Value matches `max_output_tokens`. Correct.
- **huggingface.py**: `_max_tokens = 4096` captured before the payload dict;
  `max_tokens_used=_max_tokens` appended. Correct.
- **openai_compat.py**: `_max_tokens = 4096` captured before the payload dict;
  `max_tokens_used=_max_tokens` appended. Correct.
- **openrouter.py**: `max_tokens_used=effective_max_tokens` appended where
  `effective_max_tokens` is the value computed by `compute_effective_max_tokens()` and
  already used in the request payload. This is the adaptive-cap adapter. Correct and
  is the most important fix for Phase 4b T2 phi-4 accuracy.

All five adapter implementations correctly set `max_tokens_used` to the exact value
they sent in their respective request bodies.

---

## DATA_DICTIONARY.md compliance (R7)

Version bump: v0.1.12 → v0.1.13. Present.

Changelog entry: Present. Documents the full scope of the fix — the `AdapterResult`
field addition, each adapter's value, the runner change, and the editorial note.
References Reviewer-T2 finding, Mark's Option A ruling, and the precedent memory file.

`max_tokens` field row updated: Present. The editorial note explicitly documents:
- Historical inaccuracy (hardcoded 4096 prior to this commit)
- Affected campaigns: Phase 4a 2026-04-22, recovery 2026-05-05, Phase 4b T2 phi-4
  rerun 2026-05-07
- Reconstructibility via `analysis_code_git_sha`
- Era breakdown (original, Task-#16, adaptive Phase 4b T2)
- Pointer to the Reviewer finding that surfaced this gap

This is a comprehensive editorial note that satisfies the R7 lockstep requirement.

---

## Append-only invariant (R4)

`git diff 75917d0^ 75917d0 -- data/raw/` returns empty. Confirmed. No historical
record was touched. No backfill script was added. Mark's Option A ruling is honored.

---

## Unit tests

Four tests in `tests/unit/test_runner_max_tokens.py`, all confirmed present:

1. `test_run_informant_records_actual_max_tokens_not_hardcoded_4096` — primary regression
   test; 16384 propagates through `run_informant()` to `InformantRecord.max_tokens`.
2. `test_run_informant_records_adaptive_max_tokens_phi4_style` — 13872 (adaptive phi-4
   cap) propagates correctly.
3. `test_run_informant_default_adapter_result_preserves_4096` — backward-compat with
   fixtures that omit `max_tokens_used` (default 4096).
4. `test_baseline_sort_records_actual_max_tokens` — `ps_result` path in
   `run_baseline_sort()` propagates `max_tokens_used=16384` from the pile-sort adapter
   result.

No real API calls. All tests use `MagicMock` adapters and fixture-like in-memory data.
CLAUDE.md §6 R10 satisfied.

Independent re-run result: **4/4 PASS** (0.75s).

Full suite: **1175 passed, 26313 warnings** (13.92s). Matches Coder's reported count.
Ruff: **All checks passed.** Mypy: **Success: no issues found in 55 source files.**

---

## Prerequisite gate verdicts (Check 9)

This is not a frontend PR, not a methodology PR, and not a schema-change PR. It is a
focused metadata-recording fix in `cdb_collect` with a companion DATA_DICTIONARY.md
note. The originating finding is already Reviewer-approved (Reviewer-T2, commit
`f7ca048`). Mark's Option A ruling is the explicit authorization. No additional gate
verdict is required.

---

## Project memory precedent honored

`memory/project_metadata_fix_forward_precedent.md` codifies fix-forward, no backfill.
This commit:
- Does NOT include a backfill script — confirmed.
- Does NOT edit any historical record — confirmed (`data/raw/` diff is empty).
- DOES document the historical inaccuracy in the data dictionary — confirmed (editorial
  note at `docs/DATA_DICTIONARY.md` §1.1 `max_tokens` row and v0.1.13 changelog entry).

Precedent is fully honored.

---

## Nine-check summary

```
Check 1 — No LLM imports in cdb_analyze:   PASS
Check 2 — Append-only JSONL:                PASS
Check 3 — No secrets:                       PASS
Check 4 — Forbidden vocabulary:             PASS
Check 5 — Schema + DATA_DICTIONARY:         PASS
Check 6 — New deps sign-off:                N/A (no new deps)
Check 7 — Prompt versioning:                N/A (no prompt changes)
Check 8 — Uncertainty in viz:               N/A (no visualization changes)
Check 9 — Prerequisite verdicts:            PASS (Mark's Option A ruling is the gate)
```

---

## REVIEWER VERDICT: PASS

All nine checks pass. No failures. No notes.

The fix is mechanically correct, fully tested, append-only invariant preserved,
DATA_DICTIONARY.md updated in lockstep, and the project memory precedent for
fix-forward metadata gaps is honored.

**Tester is next.** After Tester issues a PASS, Phase 4b T3 (gpt-4.1-mini + mistral-small
collection) is unblocked.

