# Tier 1–2 guardrail hook ACTIVATION — Reviewer verdict (2026-06-05)

**Task:** Activate the four Tier 1–2 PreToolUse guardrail hooks per
`docs/proposed/2026-05-29-tier1-2-activation-runbook.md` §Activation.
**Gate:** Reviewer (guardrails affect the whole team — runbook §Activation step 1).
**Verdict:** **PASS.** Coder may merge.

## What was activated
- `.claude/settings.json` — new `hooks.PreToolUse` block wiring all four hooks on
  matcher `Write|Edit|MultiEdit`:
  `check_forbidden_vocab.py`, `check_informants_append_only.py`,
  `check_spend_gate.py`, `check_schema_edit.py`.
- All four hook docstrings flipped `DRAFT — INACTIVE` → `ACTIVE (wired 2026-06-05)`.
- `check_forbidden_vocab.py` — proximity matcher tuned (see below).
- `check_schema_edit.py` — `ask`-flow note `VERIFY` → `CONFIRMED at activation`.

## Live validation performed this session (all PASS)
Hook contract first re-confirmed against current Claude Code docs (claude-code-guide):
PreToolUse stdin keys `tool_name`/`tool_input.{content,new_string,edits[]}`,
`hookSpecificOutput.permissionDecision:"ask"` honored, matcher alternation +
`${CLAUDE_PROJECT_DIR}` + exit-2-blocks all CONFIRMED; hooks load immediately on
settings.json edit (no restart, no trust prompt).

Live tool-call validation:
- **forbidden vocab** — real Write of a §7-violating model-subject clause (the
  "Model X [belief-verb]…" pattern) → BLOCKED (exit 2). ✓
- **informants append-only** — real Write to a `…/data/raw/informants.jsonl` suffix
  path → BLOCKED. ✓
- **spend-gate** — real Write containing a spend-cap env-var token → BLOCKED (the
  hook even blocked an early draft of this very verdict file — working as designed). ✓
- **schema-edit ask** — real Write to a `…/cdb_core/schemas.py` suffix path →
  confirmation prompt SHOWN and HONORED (Mark confirmed the prompt appeared). ✓
- 10-case regression on the vocab hook (5 block / 5 allow) all correct;
  `uv run ruff check .claude/hooks/check_forbidden_vocab.py` → All checks passed.

(Note: this verdict file itself tripped both the spend-gate and the vocab guard on
its first two drafts — the documentation of the test inputs reproduced the very
tokens/patterns the guards catch. That is the guards working correctly end-to-end;
the file was reworded to describe the test inputs without reproducing them.)

## The proximity-matcher tuning (substantive fix, not cosmetic)
Activation surfaced a **live false positive**: the original matcher
`term .{0,48} model_token` was bidirectional and crossed sentence boundaries, so the
benign text *"I think this loop terminates. Model X output treats kin terms…"* was
blocked — the first-person verb sat within 48 chars of "Model" across a sentence
break. Fix:
- span → `[^.!?\n]{0,48}?` (never crosses `.`/`!`/`?`/newline — same-sentence only);
- belief/cognition verb terms require the model token in **subject (preceding)**
  position; only the noun term (`worldview`) stays bidirectional (`BIDIRECTIONAL_TERMS`).

## Reviewer scorecard
| Check | Result |
|---|---|
| No LLM imports in cdb_analyze | PASS (no cdb_analyze change) |
| Append-only JSONL | PASS (not touched) |
| No secrets | PASS |
| Forbidden vocabulary | PASS (the §7 terms appear only inside the guard's own docstrings, describing what it detects — same structure as the §7 table's left column; §7 judgment caveat applies) |
| Schema + DATA_DICTIONARY | N/A |
| New deps sign-off | N/A |
| Prerequisite gate verdicts | PASS (tooling/infra — not frontend, not methodology; runbook designates Reviewer as the gate) |
| One-commit-per-task | PASS (5 files, all under `.claude/`, no bundling) |

## Informational notes (non-blocking, carried forward)
1. **§7 vs ARCHITECTURE §1.5.4 coverage gap.** The hook covers all six CLAUDE.md §7
   rows exactly; the six additional §1.5.4 register rows (within-model
   consensus/eigenratio/CCM, "publishable", the two hypothesis-framing rows) are out
   of the hook's declared scope. Reviewer R12 + the CDA SME gate remain the
   enforcement path for those. A future hook expansion could close the gap; not
   required for activation.
2. **Directional verb match.** Belief/cognition verbs block only when the model token
   precedes (subject position). Reverse constructions pass — accepted trade-off
   targeting the actual §7 subject-predicate pattern and eliminating the live FP
   class. R12 + SME remain backstops.
3. **Pre-existing E501** at `check_spend_gate.py:55` (present in HEAD, not introduced
   here) left untouched to keep the commit scoped; `.claude` is CI-excluded
   (pyproject ruff exclude) so it does not fail CI.
