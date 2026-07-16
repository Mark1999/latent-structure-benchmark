# Agent instructions

This repo's full agent constitution is [CLAUDE.md](./CLAUDE.md); it is authoritative and
binding, so read it before doing anything. Role definitions live in `.claude/agents/`
(architect, cda_sme, coder, reviewer, tester, ui_ux). `ARCHITECTURE.md`, `DESIGN_SYSTEM.md`,
and `docs/DATA_DICTIONARY.md` are the binding specs CLAUDE.md defers to.

Essentials if you read nothing else:

- Python gates (repo root): `uv run pytest && uv run ruff check . && uv run mypy packages/`.
  Dashboard gates (from `apps/dashboard/`): `npm run build && npm run test && npm run lint`.
  Direct-to-master means these run locally before every commit; CI is confirmation, not a
  safety net.
- Mechanized hard rules (pre-commit hooks + CI, not just prose): gitleaks; no em dashes in
  added lines (`scripts/check_em_dash.py`); no LLM-client imports in `cdb_analyze`;
  package-boundary greps for `cdb_social`; a grep that fails the build on budget-limit
  tokens. See CLAUDE.md's binding rules for the exact terms before writing anything
  cost-related.
- CLAUDE.md's forbidden-vocabulary table applies to code comments, copy, and commit
  messages, not just prose.
- Commits: Conventional Commits with package scopes, one commit per task.
- `data/raw/informants.jsonl` is append-only; schemas (`cdb_core/schemas.py`) and prompt
  templates are versioned and never edited in place.
