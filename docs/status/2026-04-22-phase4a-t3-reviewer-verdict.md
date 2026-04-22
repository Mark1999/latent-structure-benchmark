# Phase 4a T3 — Reviewer Verdict (thread: canary + adapter fix completion)

**Date:** 2026-04-22
**Commits reviewed:**
- `dfce917 fix(collect): cap openrouter max_tokens at 4096 to fit small-context models`
- `fb645fa docs(status): Phase 4a T3 canary PASS — phi-4 × family × N=5 (task #11)`
- `95ff713 fix(collect): complete max_tokens cap at 4096 across all adapters + runner`
**Architect verdicts:**
- `docs/status/2026-04-22-phase4a-kickoff-architect-verdict.md` + Amendment A (Phase 4a plan; T3 task spec §4)
- `docs/status/2026-04-22-phase4a-adapter-fix-verdict.md` (approves value 4096, keeps phi-4 canary, two-commit structure)
**Preceding gates:** CDA SME PASS on slate (#8), Reviewer PASS on T1 (#9), Orchestrator PASS on T2 (#10). No further SME/UI-UX gate required.

---

## Verdict: **PASS** on all three commits

---

## Commit 1 — `dfce917` (openrouter adapter fix)

**Scope:** exactly one file (`packages/cdb_collect/cdb_collect/adapters/openrouter.py`). No test files, no schema, no other adapters. Diff: literal `16384 → 4096` plus a 5-line comment block.
**Content:** matches the Architect-approved change precisely.
**R9 / R4 / R10 / R7 / R6 / R11 / R2 / R12:** all N/A or PASS.
**Commit message:** `fix(collect):` scope, 57 chars subject, references the Architect verdict file path and the phi-4 HTTP 400 trigger, documents deferred follow-up task #16.

## Commit 2 — `fb645fa` (T3 canary report)

**Scope:** exactly one file (`docs/status/2026-04-22-phase4a-t3-canary-report.md`). No code changes. `data/raw/informants.jsonl` is gitignored; the 4 actual records live on disk, not in git.

**Report accuracy verified against disk state:**

| Claim | Verified |
|---|---|
| 4 records appended | `wc -l data/raw/informants.jsonl` = 4 ✓ |
| All 4 `qa_passed=True` | parsed JSONL, all True ✓ |
| All 4 `model_version_returned=microsoft/phi-4` | confirmed ✓ |
| 1 run failed at pile-sort parsing (not adapter) | `failures.jsonl` entry 6: `error_type=ValueError`, `run_index=4` ✓ |
| Cost ~$0.003, wall clock ~4 min | plausible given token counts (9,489 in / 13,913 out) ✓ |

**Stop conditions:** 0/4 `qa_passed=False` (below ≥3 threshold), 0 missing `model_version_returned`, 0 adapter failures, wall clock under 15 min, cost under $1. None triggered.

**T4 recommendation in report:** GO. Reasoning tracks the evidence.

**Annotation (resolved by commit 3 below):** the 4 stored records carry `max_tokens=16384` in their provenance field — a known artifact of the `runner.py:237` hardcode that the initial `dfce917` fix did not touch. This is the provenance mismatch that motivated commit 3 (`95ff713`). The 4 canary records carry the old value, which is correct append-only behavior; future records from T4 onward will carry the honest `4096` value.

## Commit 3 — `95ff713` (completion across 5 sites)

**Scope:** exactly 5 files, 5 insertions, 5 deletions.

1. `adapters/anthropic.py` — `"max_tokens": 16384 → 4096`
2. `adapters/google.py` — `max_output_tokens=16384 → 4096` (Google SDK parameter name)
3. `adapters/huggingface.py` — `"max_tokens": 16384 → 4096`
4. `adapters/openai_compat.py` — `self._max_tokens_param: 16384 → 4096` (covers `openai.py` + `xai.py` re-exports)
5. `runner.py:237` — `max_tokens=16384 → 4096` (the `InformantRecord` provenance field)

**Literal sweep:** the only surviving `16384` occurrences in `cdb_collect/` are in `openrouter.py:105-106` — historical explanatory comments describing the phi-4 bug, not live values. No `max_output_tokens=16384`, `max_new_tokens=16384`, or `maxTokens=16384` anywhere.

**Inline comments:** four of five sites use the full verdict path; `openai_compat.py` uses a shortened form due to E501 line-length constraint — unambiguous and correct.

**R-rule findings:** all PASS or N/A. `R7` (schema + DATA_DICTIONARY) explicitly considered: the `runner.py` change alters only the stamped value on `InformantRecord.max_tokens`, not the field type or presence. No dictionary-level schema change; no `DATA_DICTIONARY.md` co-update required.

**Tests:** 464 passed, ruff clean, mypy clean. No test assertions referenced `16384`; no test updates needed.

**Commit message:** `fix(collect):` scope, under 72 chars subject, references `dfce917` and the Architect verdict file path, explains the runner-side provenance closure explicitly.

## Cross-commit findings

- **Not bundled.** Each commit has distinct scope. Three commits match the work's three phases (adapter fix → canary report → completion across sites).
- **Sequence correct.** `dfce917` (18:27:50) → `fb645fa` (18:33:46) → `95ff713` (later, completion). Canary ran after initial fix; completion landed after canary surfaced the provenance gap.
- **`data/raw/informants.jsonl` state:** 4 lines on disk, gitignored, not committed. Append-only contract intact. No pre-existing lines modified.
- **`data/failures.jsonl`** (if tracked): gitignored. Contains 6 entries (5 pre-fix HTTP 400 + 1 post-fix pile-sort parse ValueError). Append-only contract intact.

## Forward notes (non-blocking)

1. **Pre-fix canary records carry the old `max_tokens=16384` value.** Correct append-only behavior. T6 QA sweep should note the split (4 records with the old value, all future records with 4096) if it matters for the reconciliation.
2. **Phi-4's 3-retry pile-sort exhaustion** (run 4/5 failed parse after dropping 24 items thrice). Not a T4 stop condition; it's phi-4-specific output-quality behavior. Watch for similar exhaustion on other small-context models during T4.

---

*End of verdict. T3 thread complete. Task #11 done. T4 unblocked.*
