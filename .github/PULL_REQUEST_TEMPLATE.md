## Description

Brief description of the change and its purpose.

## Task reference

Plan: `docs/status/YYYY-MM-DD-task-id-architect-plan.md`

## Gate verdicts

- CDA SME verdict (if methodology-significant): `docs/status/YYYY-MM-DD-task-id-cda-sme-verdict.md`
- Reviewer verdict: `docs/status/YYYY-MM-DD-task-id-reviewer-verdict.md`

## Pre-flight checklist

- [ ] `uv run pytest && uv run ruff check . && uv run mypy packages/` passes locally
- [ ] No forbidden vocabulary (CLAUDE.md §7 / ARCHITECTURE.md §1.5.4)
- [ ] No new dependency without Architect sign-off
- [ ] No schema change without matching DATA_DICTIONARY.md update
- [ ] No API keys or credentials in committed files
