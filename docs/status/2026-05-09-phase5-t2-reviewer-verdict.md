# Reviewer Verdict — Phase 5 T2 (template-based lede generator)

**Filed:** 2026-05-09
**Reviewer:** LSB Reviewer (Sonnet 4.6)
**Commit reviewed:** `9e5a138`
**Task:** Phase 5 T2 — template-based lede generator
**Prerequisite SME verdict:** CDA SME content PASS-WITH-NOTES at `docs/status/2026-05-09-phase5-T2-cda-sme-content-verdict.md` (commit `1868fca`)

---

## REVIEWER VERDICT: PASS

```
Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         PASS
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A
Check 6 — New deps sign-off:         N/A
Check 7 — Prompt versioning:         PASS
Check 8 — Uncertainty in viz:        N/A
Check 9 — Prerequisite verdicts:     PASS
```

---

## Check detail

### Check 1 — No LLM imports

`grep -nE "^import (anthropic|openai|...) | ^from (anthropic|openai|...)"` on
`packages/cdb_publish/cdb_publish/lede.py` and
`packages/cdb_publish/cdb_publish/templates/lede_v1.py`: **zero hits.**

`grep -r "import anthropic|import openai|from anthropic|from openai|InferenceClient|google.generativeai"` on
`packages/cdb_analyze/`: **zero real import statements.** The two hits returned
were both comment lines in `packages/cdb_analyze/cdb_analyze/__init__.py` listing
the forbidden library names as documentation (negation guards). No actual
import-statement violations.

Additionally, Test 12 (`test_no_llm_imports_in_lede_py`) performs an AST parse
of `lede.py` and checks for all seven forbidden library names. Test 12: PASS.

**PASS.**

### Check 2 — Append-only JSONL

`git diff 9e5a138~1..9e5a138 -- data/raw/informants.jsonl`: empty diff. No
modification to informants.jsonl. **PASS (N/A in practice).**

### Check 3 — No secrets

Scanned `lede.py`, `templates/lede_v1.py`, and `tests/cdb_publish/test_lede.py`
for `sk-[a-zA-Z0-9]+`, `Bearer [a-zA-Z0-9]+`, and `hooks.slack.com`: **zero
hits.** No API keys, tokens, or webhook URLs in any committed file. **PASS.**

### Check 4 — Forbidden vocabulary

Scanned all four committed files (`lede.py`, `templates/__init__.py`,
`lede_v1.py`, `test_lede.py`) and the commit message.

**PATTERNS dict values (the user-facing strings):** AST-extracted and
substring-checked against the full §1.5.4 + ARCHITECTURE.md §1.5.4 forbidden
list: zero hits. All eight template strings are clean.

**Docstring/comment hits reviewed:**

- `templates/lede_v1.py` lines 20–26: lists the forbidden vocab as documentation
  guards ("§1.5.4 forbidden vocabulary absent: no 'believes', 'thinks',
  'worldview'..."). This is a negation-form list, not a use of the forbidden
  vocabulary to describe a model. Not a violation; consistent with the CDA SME
  Q1 `NO_CONSENSUS` ruling (negation-form documentation guards are acceptable).
- `templates/lede_v1.py` line 26: "no 'publishable' or 'publication' framing"
  — same negation-form documentation guard pattern. Not a violation.
- Commit message line 22: "no causal, introspective, or publishable language in
  any template string" — same pattern, acceptable.
- `NO_CONSENSUS` in `lede.py:16` and `lede_v1.py:16`: both are negation-form
  comments ("does not exist and must never appear here"). Not live-code
  branch predicates. Consistent with CDA SME Q1 verification in the content
  verdict. Not a violation.

The Reviewer rule applies to how LSB talks about its subjects in user-facing
text. Negation guards in docstrings that list what is excluded are editorial
discipline, not forbidden usage.

**PASS.**

### Check 5 — Schema + DATA_DICTIONARY

`git diff 9e5a138~1..9e5a138 -- packages/cdb_core/cdb_core/schemas.py`: empty
diff. No schema changes in this commit. **N/A.**

### Check 6 — New deps sign-off

`git diff 9e5a138~1..9e5a138 -- pyproject.toml uv.lock`: empty diff. No new
dependencies. **N/A.**

### Check 7 — Prompt versioning (R7)

The commit introduces `packages/cdb_publish/cdb_publish/templates/lede_v1.py`
as a new file — it does not edit any existing versioned template. The module
carries `LEDE_VERSION = "v1"` (line 42), the `templates/__init__.py` package
marker documents the versioning discipline explicitly ("Reviewer rejects in-place
edits; create lede_v2.py for any future change"), and the `all_deterministic`
pattern in `lede_v1.py` carries an inline comment at lines 130–131 repeating
the same constraint. No existing versioned file was edited. **PASS.**

### Check 8 — Uncertainty in viz

Non-frontend PR. `git diff 9e5a138~1..9e5a138 -- apps/dashboard/`: empty diff.
**N/A.**

### Check 9 — Prerequisite verdicts

This is a methodology-touching PR (lede generator pattern text, ConsensusType
branch logic). Required prerequisite: CDA SME content PASS-WITH-NOTES.

Present: `docs/status/2026-05-09-phase5-T2-cda-sme-content-verdict.md` (commit
`1868fca`). Verdict: PASS-WITH-NOTES. Notes from the content verdict:

- S1 (`consensus_score` semantic-ambiguity): forward-carry binding on the next
  analysis-layer SME review, not on T2. No rework required at T2.
- S2 ("did not converge" verb): advisory for T13 methodology summary. No rework
  required at T2.
- Q2 carry (small-n caveat): binding on T10 + T13, not T2.
- Q6–Q11 carry: gated on T13 SME content verdict.

All notes explicitly marked "no rework required at T2." The content verdict
states: "Reviewer + Tester are authorized to proceed on T2 as-shipped."

**PASS.**

---

## T2-specific item verification

| Item | Result |
|---|---|
| A. `generate_lede(result: DomainResult) -> str` — pure function, deterministic | PASS |
| B. Branch logic uses 6-value ConsensusType schema-literal predicates only | PASS |
| C. Three STRONG_CONSENSUS sub-branches (homogeneous / with_low_oci / majority_low_oci) | PASS |
| D. All-deterministic case verbatim DS §3.3.5 item 6 copy (byte-identical, em-dash U+2014) | PASS |
| E. DETERMINISTIC consensus_type routes to all-deterministic copy | PASS |
| F. No LLM imports in lede.py or templates | PASS |
| G. OCI_LOW_CONCENTRATION_THRESHOLD = 3.0 constant defined | PASS |
| H. 12 tests all pass; no real API calls | PASS (12/12 pytest green) |
| I. Determinism test present and passing | PASS |

`uv run pytest tests/cdb_publish/test_lede.py -v`: 12 passed.
`uv run ruff check packages/cdb_publish/ tests/cdb_publish/`: all checks passed.
`uv run mypy packages/cdb_publish/`: no issues found in 7 source files.

---

## Failures

None.

---

## Required before merge

None. Coder may merge.

---

*Verdict PASS. Tester proceeds.*
