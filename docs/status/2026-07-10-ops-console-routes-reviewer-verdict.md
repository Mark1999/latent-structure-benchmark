# Reviewer verdict: ops console T2/T5/T7/T8/T9 routes + templates

**Date:** 2026-07-10
**Review object:** staged changeset (git diff --cached) plus unstaged qa.html fix
**Architect plan:** docs/status/2026-07-10-ops-console-panels123-architect-plan.md
**Prerequisite verdicts:**
- CDA SME T6 PASS: docs/status/2026-07-10-ops-console-T6-cda-sme-verdict.md
- CDA SME T7 PASS: docs/status/2026-07-10-ops-console-T7-cda-sme-verdict.md
- UI/UX PASS-WITH-NOTES (fix applied): docs/status/2026-07-10-ops-console-uiux-verdict.md

---

REVIEWER VERDICT: PASS

Check 1 -- No LLM imports:            PASS
Check 2 -- Append-only JSONL:         PASS
Check 3 -- No secrets:                PASS
Check 4 -- Forbidden vocabulary:      PASS
Check 5 -- Schema + DATA_DICTIONARY:  N/A
Check 6 -- New deps sign-off:         N/A
Check 7 -- Prompt versioning:         N/A
Check 8 -- Uncertainty in viz:        N/A
Check 9 -- Prerequisite verdicts:     PASS

---

## Check notes

**Check 1.** No LLM client imports in routes_ops.py or qa/ modules. The cdb_analyze/__init__.py
match is a comment listing forbidden names, not an import. B-1 preserved.

**Check 2.** data/raw/informants.jsonl is gitignored and not in the changeset. The new
tests/fixtures/ops_console/informants_qa.jsonl is a newly created fixture file (4 lines, no
pre-existing lines modified). Append-only invariant is intact.

**Check 3.** No API keys, webhook URLs, or credentials in any changed file. CSRF tokens are
stdlib secrets.token_urlsafe, which is correct. Provider values in the fixture file are
placeholder strings (test-model-a, req-qa-001) with no real key shapes.

**Check 4.** Full grep on staged diff: no forbidden vocabulary from CLAUDE.md §7 or
ARCHITECTURE.md §1.5.4.

**Check 5/6/7/8.** No schema changes, no dependency changes, no prompt template edits, no
public visualizations. All N/A.

**Check 9.** Both required CDA SME verdicts are PASS. UI/UX is PASS-WITH-NOTES. The single
required fix (qa.html line 73: tooltip replaced with details/summary disclosure) is confirmed
applied in the working tree. Three non-blocking notes are recorded as future CSS-pass items.
ruff: clean. mypy: 89 files, no issues. pytest tests/unit/admin_console/: 184 passed.

---

## Process notes

**(a) Direct commit and soft-reset.** The Coder committed this work as 52a7fb0 before the
gate ran, contrary to the orchestrator's do-not-commit instruction. The orchestrator performed
a local soft-reset (commit was never pushed). The staged tree is the correct review object;
this verdict is not blocked by the process deviation because no pushed commit exists. The
Coder should note: direct commit before Reviewer gate completes is a CLAUDE.md §8 violation.
Mark may address this separately.

**(b) Coder deviation: isinstance(result, str) in place of identity check on NEW_DOMAIN_SENTINEL.**
ACCEPTABLE. The planner return type is annotated CampaignPlan | str. CampaignPlan is a frozen
dataclass and cannot be a str subclass; isinstance(result, str) is therefore semantically
equivalent to checking against the sentinel. The mypy rationale is sound: isinstance narrowing
satisfies the type checker in a way that an identity check would not (the return type is str,
not Literal["__new_domain__"]). Importing the sentinel constant into routes_ops.py would add
coupling without improving correctness. Deviation is within engineering judgment.

---

*Coder may stage the qa.html fix and commit both together. Do not commit this verdict file.*
