# Phase 0 — Task Decomposition for Coder Agent

**Author:** Architect agent
**Audience:** Coder agent (primary), Reviewer agent, Tester agent, Mark
**Phase goal:** produce a working repo skeleton that every subsequent phase can build on, with no functional code beyond the core schema definitions and no external dependencies beyond what's needed to run CI.
**Definition of done for Phase 0:** `uv run pytest` passes, `uv run ruff check` passes, `uv run mypy packages/` passes, CI runs green on a fresh clone, and `cdb_core` exposes all pydantic models from `ARCHITECTURE.md` §3 with passing round-trip tests.

---

## Ground rules for the Coder agent

1. **Read `ARCHITECTURE.md` §1.5, §2, and §3 before touching any file.** The schemas in §3 are binding. §1.5 governs all generated text.
2. **Do each task in isolation.** One PR per task. Do not bundle. Do not do extra work beyond the task's scope, even if it seems obviously helpful.
3. **No real API calls.** Phase 0 produces no network I/O. Any adapter stub should have a docstring saying "implemented in Phase 1" and a `NotImplementedError`.
4. **Use `uv` for Python environment management.** Not pip, not poetry, not conda.
5. **Stop and ask Architect** if a task's acceptance criteria can't be met as written. Do not improvise.

---

## Task list

### P0-T1 — Initialize repository scaffold

**Inputs:** `ARCHITECTURE.md` §2 (repository layout).

**Outputs:**
- `git init` in a clean directory
- `pyproject.toml` configured for `uv` with Python 3.12+
- `.gitignore` covering: `.env`, `.venv/`, `__pycache__/`, `*.pyc`, `data/raw/`, `data/processed/`, `node_modules/`, `dist/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`
- `.env.example` with placeholder keys: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `OPENROUTER_API_KEY`, `CDB_MAX_SPEND_USD`
- Empty directory structure matching §2 exactly, each with a `.gitkeep` or a meaningful file
- `data/raw/.gitkeep`, `data/processed/.gitkeep`, `data/results/.gitkeep`, `data/grounding/family/.gitkeep`
- `README.md` stub containing only: project name, one-line description drawn from §1.5.1 (not the worldview phrasing), link to `ARCHITECTURE.md`, "Status: under development"

**Acceptance criteria:**
- `git status` shows a clean working tree after initial commit
- `tree -L 3 -I 'node_modules|__pycache__'` output matches §2 exactly
- `uv sync` runs successfully with an empty dependency list
- `README.md` contains zero instances of "worldview," "believes," "thinks," or any other forbidden phrase from §1.5.4

**Dependencies:** none
**Estimated size:** ~30 minutes of Coder time

---

### P0-T2 — Drop in root documentation files

**Inputs:** `ARCHITECTURE.md` (already written), existing `CLAUDE.md` (already exists in Mark's workflow).

**Outputs:**
- `ARCHITECTURE.md` at repo root (copy of the current v0.2.1 document verbatim)
- `CLAUDE.md` at repo root, with the project-specific addendum from `ARCHITECTURE.md` §5.2 appended beneath Mark's existing team-constitution content
- `docs/PHASE_4C_CANDIDATE_SOURCES.md` copied into place for future reference

**Acceptance criteria:**
- All three files exist and are committed
- `grep -r "worldview" CLAUDE.md ARCHITECTURE.md` returns zero matches *except* inside §1.5.4 where forbidden phrases are explicitly listed

**Dependencies:** P0-T1
**Estimated size:** ~10 minutes

---

### P0-T3 — Implement `cdb_core` package

**Inputs:** `ARCHITECTURE.md` §3 (data model).

**Outputs:**
- `packages/cdb_core/__init__.py` exporting all public types
- `packages/cdb_core/ids.py` implementing `run_id(model, domain, step, prompt_version, run_index) -> str` as a deterministic SHA256 truncated to 16 hex chars
- `packages/cdb_core/schemas.py` containing every pydantic model from §3.2 exactly as specified, including the v0.2 additions (`BootstrapEllipse`, `GroundingRef`, and the updated `DomainResult`)
- `packages/cdb_core/versioning.py` with `PROMPT_VERSION`, `DOMAIN_VERSION`, and `ANALYSIS_VERSION` module-level constants set to `"v1"`, `"v1"`, and `"0.1"` respectively, plus a `git_sha()` function that returns the current commit SHA or `"unknown"` if not in a git repo
- `tests/unit/test_ids.py` verifying determinism: same inputs → same ID across 1000 calls
- `tests/unit/test_schemas.py` verifying round-trip serialization (model → dict → model → dict) for every schema type, using fixture data

**Acceptance criteria:**
- Every pydantic model in §3.2 exists with the exact field names and types specified
- `run_id` is deterministic and produces a 16-character lowercase hex string
- `test_schemas.py` exercises every model with at least one valid instance and round-trips it without loss
- `mypy packages/cdb_core/` passes with strict mode
- `ruff check packages/cdb_core/` passes
- No imports from other `cdb_*` packages (enforced by Reviewer agent — core has no dependencies on its siblings)

**Dependencies:** P0-T1
**Estimated size:** ~90 minutes

**Reviewer watch-outs:**
- Reviewer must confirm that `DomainResult` includes `mds_uncertainty`, `similarity_ci`, `consensus_ci`, and `grounding`. These are the v0.2 additions and are the easiest fields to overlook.
- Reviewer must confirm no schema types are defined outside `schemas.py`.

---

### P0-T4 — Scaffold sibling packages

**Inputs:** `ARCHITECTURE.md` §2, §4.

**Outputs:**
- `packages/cdb_collect/__init__.py` containing only a module docstring describing the package's responsibility (collection layer, produces `RawResponse` records) and a comment listing allowed imports: `cdb_core`, stdlib, `httpx`, `pydantic`. Nothing else.
- Same pattern for `packages/cdb_analyze/`, `packages/cdb_api/`, `packages/cdb_social/` — docstring + allowed-imports comment, no functional code
- Each package directory contains a `README.md` one-pager summarizing its role from the corresponding section of `ARCHITECTURE.md` (§4.1 for collect, §4.2 for analyze, §4.4 for api, §4.6 for social)

**Acceptance criteria:**
- `python -c "import cdb_collect, cdb_analyze, cdb_api, cdb_social"` runs without error
- Each package's `__init__.py` docstring states its single responsibility in one sentence
- Each package `README.md` links back to the relevant `ARCHITECTURE.md` section
- No package imports from any other `cdb_*` sibling except `cdb_core`

**Dependencies:** P0-T3
**Estimated size:** ~30 minutes

---

### P0-T5 — CI pipeline

**Inputs:** nothing beyond the existing scaffold.

**Outputs:**
- `.github/workflows/ci.yml` running on push and PR:
  - Install uv
  - `uv sync`
  - `uv run ruff check .`
  - `uv run ruff format --check .`
  - `uv run mypy packages/`
  - `uv run pytest`
- `.pre-commit-config.yaml` with hooks for ruff (check + format) and an optional mypy hook
- `ruff.toml` or `pyproject.toml` tool section configuring ruff for line length 100, target Python 3.12, common rule set (E, F, I, B, UP, RUF)
- `pyproject.toml` mypy section with `strict = true` for `packages/cdb_core` and `strict = false` elsewhere for now

**Acceptance criteria:**
- CI runs green on a fresh clone against the main branch
- `pre-commit run --all-files` passes
- Introducing a deliberate unused import fails both pre-commit and CI

**Dependencies:** P0-T3, P0-T4
**Estimated size:** ~45 minutes

---

### P0-T6 — Tests directory scaffold

**Inputs:** `ARCHITECTURE.md` §5.1 (Tester role).

**Outputs:**
- `tests/unit/__init__.py`, `tests/integration/__init__.py`
- `tests/fixtures/README.md` explaining the fixture convention: every canned model response lives in `tests/fixtures/{provider}/{model}/{domain}/{step}/run_{n}.json` and is a pre-recorded valid `RawResponse` instance. No tests hit real APIs.
- `tests/fixtures/anthropic/claude-opus-4-6/family/free_list/run_0.json` — one hand-crafted example file containing a plausible Claude free-listing response, for use as a test seed in Phase 1
- `tests/conftest.py` with a `pytest` fixture `fixtures_dir` that resolves to the fixtures directory regardless of where pytest is invoked from

**Acceptance criteria:**
- `pytest tests/` runs (finds zero tests, exits 0 — the actual tests come from P0-T3's schema tests)
- The hand-crafted fixture file parses as a valid `RawResponse` via `cdb_core`
- Fixture README explicitly states: "No test in this repository may make a real network call to an LLM provider."

**Dependencies:** P0-T3
**Estimated size:** ~30 minutes

---

### P0-T7 — Dashboard scaffold

**Inputs:** `ARCHITECTURE.md` §4.5.

**Outputs:**
- `apps/dashboard/` initialized as a Vite + React + TypeScript project
- Tailwind CSS configured
- `apps/dashboard/src/App.tsx` renders a single `<h1>` with the project name and nothing else — no routing, no API calls, no viz components yet
- `apps/dashboard/package.json` with scripts: `dev`, `build`, `lint`, `test`
- `apps/dashboard/vitest.config.ts` configured for `vitest`
- `apps/dashboard/src/App.test.tsx` with a single smoke test asserting the `<h1>` renders

**Acceptance criteria:**
- `npm install && npm run build` produces a dist directory without errors
- `npm run test` passes the smoke test
- `npm run lint` passes with no warnings
- Bundle size under 200KB (sanity check — if it's bigger, something is wrong)

**Dependencies:** P0-T1
**Estimated size:** ~60 minutes

**Note:** This is scaffolding only. No uncertainty-aware components yet. Those come in Phase 5 when there's real data to show. The §4.5 "no point estimates without uncertainty" rule applies from Phase 5 onward; Phase 0's smoke-test `<h1>` doesn't trigger it.

---

### P0-T8 — Entry-point scripts

**Inputs:** `ARCHITECTURE.md` §4.1.4, §4.2.4.

**Outputs:**
- `scripts/collect.py` — argparse stub accepting `--domain`, `--model`, `--runs`, `--dry-run`; prints "collect: not implemented (Phase 1)" and exits 0
- `scripts/analyze.py` — argparse stub accepting `--domain`, `--all`, `--analysis-version`; prints "analyze: not implemented (Phase 3)" and exits 0
- `scripts/publish.py` — prints "publish: not implemented (Phase 8)" and exits 0
- `scripts/serve.py` — prints "serve: not implemented (Phase 5)" and exits 0
- `scripts/cost_report.py` — prints "cost_report: not implemented (Phase 1)" and exits 0

**Acceptance criteria:**
- Each script is executable via `uv run python scripts/{name}.py --help` (for the ones with argparse)
- Each script exits 0 on a bare invocation
- Each script imports at least `cdb_core` to verify the package wiring works end-to-end

**Dependencies:** P0-T3, P0-T4
**Estimated size:** ~20 minutes

---

## Task dependency graph

```
P0-T1 ─┬─► P0-T2
       ├─► P0-T3 ─┬─► P0-T4 ─┐
       │         ├─► P0-T6   ├─► P0-T5
       │         └───────────┘
       │                     ├─► P0-T8
       └─► P0-T7
```

**Suggested execution order:** T1 → T2 → T3 → T4 → T6 → T7 → T8 → T5 (CI last, so it gates everything else).

**Total estimated Coder time:** ~5 hours across 8 tasks. Comfortably one focused session with the 4-agent pipeline, or two lighter sessions.

---

## Phase 0 exit criteria (all must be true)

1. `git clone` → `uv sync` → `uv run pytest` → green, from zero.
2. `cdb_core` exposes every schema from `ARCHITECTURE.md` §3 and round-trips all of them in tests.
3. CI passes on the main branch.
4. `README.md`, `ARCHITECTURE.md`, `CLAUDE.md`, and `docs/PHASE_4C_CANDIDATE_SOURCES.md` all exist at the correct paths.
5. No real API calls anywhere in the codebase.
6. No forbidden §1.5.4 phrases in any committed text file.
7. The dashboard scaffold builds without errors.
8. Every `cdb_*` package has a one-sentence single-responsibility docstring and an allowed-imports comment.

When all eight are true, the Architect agent signs off and Phase 1 begins.

---

## What Phase 0 deliberately does NOT include

Listing these so the Coder agent does not drift into them:

- No actual model adapters (Phase 1)
- No prompt templates (Phase 1)
- No CDA protocol implementation (Phases 1–2)
- No analysis code (Phase 3)
- No API routes (Phase 5)
- No dashboard visualizations (Phase 5)
- No grounding data loading (Phase 4c)
- No bootstrap module (Phase 4d)
- No social pipeline (Phase 7)

If the Coder is tempted to "just add a quick X" while working on a Phase 0 task, the answer is no. Stop, commit the current task, and raise it with Architect.

---

*End of Phase 0 task decomposition. Ready for Coder agent pickup after Mark's sign-off.*
