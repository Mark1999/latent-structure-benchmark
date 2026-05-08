# PHASE 0 TASKS — LSB Skeleton

**Document name:** `PHASE_0_TASKS.md`  
**Version:** v0.3 (aligned with `ARCHITECTURE.md` v0.7)  
**Status:** Canonical decomposition for the Coder agent's first session  
**Audience:** Architect / CDA SME / UI/UX agent / Coder / Reviewer / Tester / Mark  
**Companion docs:** `ARCHITECTURE.md` (binding), `DESIGN_SYSTEM.md` (binding for P0-T10), `CLAUDE.md`, `SECURITY_AND_HARDENING.md`

**Changelog:**
- **v0.3** (aligned with `ARCHITECTURE.md` v0.7) — adds the multi-baseline grounding directory layout to P0-T3 (schemas) and P0-T8 (data directories); adds the UI/UX agent definition and the `#lsb-ui-ux` Slack webhook to P0-T7 (agent scaffolding); adds a fourth license file (`LICENSE-OPENBUNDLE`) to P0-T2; adds `docs/DATA_DICTIONARY.md` first draft to P0-T5; adds the `cdb_analyze` no-LLM-imports static check to P0-T6 (CI baseline) as a hard requirement.
- v0.2 (aligned with `ARCHITECTURE.md` v0.6) — added P0-T9 (security scaffolding) and P0-T10 (CSP + `_headers`); expanded P0-T2 to cover the four license files; added `InformantRecord` to P0-T3.
- v0.1 — initial 8-task decomposition.

---

## Goal of Phase 0

Phase 0 produces **the empty skeleton** of the LSB monorepo. After Phase 0 the repo compiles, lints clean, runs tests against zero packages, deploys an empty dashboard to Cloudflare Pages staging, has all four LICENSE files in place, has the agent pipeline scaffolded with all six agents defined, and is fully wired for security scanning and CI. Phase 0 does **not** produce any working features — no API calls, no analysis, no visualizations, no real data. It produces a project that the Coder agent can start filling in during Phase 1.

The constraint is that nothing in Phase 0 should commit the project to a decision that's not already in `ARCHITECTURE.md` v0.7 or `DESIGN_SYSTEM.md` v0.2. Phase 0 is execution against existing decisions, not a place to make new ones.

**Estimated effort:** one focused session for an experienced Coder, two sessions if the Coder is unfamiliar with the project. The dependency graph (below) allows partial parallelism: T1 must come first, T7 / T8 / T10 can run in parallel after T1, T3 must come before T4 and T5, T9 can run any time after T1.

---

## Task index

| ID | Title | Depends on | Parallelizable? |
|---|---|---|---|
| **P0-T1** | Repository scaffold and Python project setup | — | No (must be first) |
| **P0-T2** | License files (4) | T1 | Yes |
| **P0-T3** | Core schemas (`cdb_core/schemas.py`) | T1 | Yes (after T1) |
| **P0-T4** | Empty package skeletons | T1 | Yes (after T1) |
| **P0-T5** | Data dictionary first draft (`docs/DATA_DICTIONARY.md`) | T3 | No (depends on schemas being defined) |
| **P0-T6** | CI baseline (ruff, mypy, pytest, no-LLM-imports check) | T1, T4 | After T4 |
| **P0-T7** | Agent scaffolding (`.claude/agents/`) and Slack webhook env vars | T1 | Yes (after T1) |
| **P0-T8** | Empty data directories | T1 | Yes (after T1) |
| **P0-T9** | Security scaffolding (gitleaks, dependabot, secret scanning) | T1 | Yes (after T1) |
| **P0-T10** | Dashboard scaffold + CSP + `_headers` | T1 | Yes (after T1) |

**Critical path:** T1 → T3 → T5; everything else can run alongside.

---

## P0-T1 — Repository scaffold and Python project setup

**Goal.** Initialize the LSB monorepo with the directory layout from `ARCHITECTURE.md` §2, the `pyproject.toml`, `uv` setup, and a working `python -c "import cdb_core"` import (even though `cdb_core` is empty at this point).

**Acceptance criteria.**

- [ ] Repo exists at `C:\Users\markd\Documents\Projects\lsb\` with `git init` run
- [ ] Top-level directory layout matches `ARCHITECTURE.md` §2 exactly: `packages/`, `apps/`, `data/`, `scripts/`, `tests/`, `docs/`, `.claude/`, `.github/`
- [ ] `pyproject.toml` at the repo root, configured for `uv`, with workspace members for each `packages/cdb_*` package
- [ ] Python 3.11+ specified as the minimum in `pyproject.toml`
- [ ] `.gitignore` includes `.env`, `data/raw/`, `data/processed/`, `__pycache__/`, `.venv/`, `node_modules/`, `apps/dashboard/dist/`, `apps/dashboard/.vite/`
- [ ] `.env.example` exists at the repo root with placeholder values for: `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`, `HUGGINGFACE_API_KEY`, `LSB_ALERTS_WEBHOOK_URL`, `LSB_CDA_SME_WEBHOOK_URL`, `LSB_UI_UX_WEBHOOK_URL`
- [ ] `uv sync` runs cleanly with no errors
- [ ] `uv run python -c "import cdb_core"` succeeds (even though `cdb_core` is empty)
- [ ] Initial commit on `main` branch with message `chore: P0-T1 repository scaffold`

**Files touched.**

- `pyproject.toml` (created)
- `.gitignore` (created)
- `.env.example` (created)
- `README.md` (placeholder — full content lands later via the README task in the trailing checklist of `ARCHITECTURE.md`; for P0, a one-line stub is acceptable)
- All directory `.gitkeep` files for empty directories that need to be tracked

**Verification.** `uv sync && uv run python -c "import cdb_core, cdb_collect, cdb_analyze, cdb_publish, cdb_social"` should succeed after T4 lands.

---

## P0-T2 — License files (four)

**Goal.** Add all four license files to the repo root, each with the correct standard text and a one-paragraph LSB-specific header explaining what the license covers.

**Acceptance criteria.**

- [ ] `LICENSE` (Apache 2.0) — covers source code per `ARCHITECTURE.md` §6.6
- [ ] `LICENSE-DATA` (CC-BY-4.0) — covers `data/raw/`, `data/processed/`, `data/results/`, `data/grounding/`, `docs/`
- [ ] `LICENSE-PROMPTS` (CC0 1.0) — covers `packages/cdb_collect/prompts/` and `data/domains/`
- [ ] `LICENSE-OPENBUNDLE` (CC0 1.0) — covers `data/open_bundle/` and the Backblaze B2 / Zenodo distribution per `ARCHITECTURE.md` §6.7 (added v0.3 of this task list, per `ARCHITECTURE.md` v0.6)
- [ ] Each license file uses the canonical text from the license author (Apache Foundation / Creative Commons), not a paraphrase
- [ ] Each license file has a one-paragraph LSB header at the top (above the canonical license text) explaining what content the license covers in LSB, with a pointer to `ARCHITECTURE.md` §6.6 / §6.7
- [ ] The `LICENSE-DATA` header notes the Romney et al. (1996) attribution requirement for `data/grounding/family/romney_1996/` per `ARCHITECTURE.md` §6.6. Note: as of the 2026-05-07 amendment, `data/grounding/` retains historical reference data only and is not consumed by any v1 analysis pipeline; see `ARCHITECTURE.md` §1.5.5 and `data/grounding/README.md`.
- [ ] Commit message: `chore: P0-T2 add four LICENSE files`

**Files touched.**

- `LICENSE` (created)
- `LICENSE-DATA` (created)
- `LICENSE-PROMPTS` (created)
- `LICENSE-OPENBUNDLE` (created)

**Verification.** Manual review by Mark; `git ls-files | grep -i license` returns all four.

---

## P0-T3 — Core schemas (`cdb_core/schemas.py`)

**Goal.** Define every Pydantic schema from `ARCHITECTURE.md` §3.2 in `packages/cdb_core/schemas.py`. This is the single most important Phase 0 task — every other package imports from here.

**Acceptance criteria.**

- [ ] `packages/cdb_core/schemas.py` exists with all of the following Pydantic models defined exactly as specified in `ARCHITECTURE.md` §3.2:
  - [ ] `ModelRef` — including `collection_method`, `quantization`, `open_weights`, `origin`, `source_notes`, and the schema notes from §3.2 as docstring
  - [ ] `Domain`
  - [ ] `RawResponse`
  - [ ] `FreeList`
  - [ ] `PileSort`
  - [ ] `CooccurrenceMatrix`
  - [ ] `BootstrapEllipse`
  - [ ] **`GroundingRef` — the v0.7 expanded version** with `baseline_id`, `baseline_kind` (`Literal["published","researcher"]`), `domain_slug`, `source_citation`, `source_url`, `collected_year`, `n_human_informants`, `population_description`, `method`, `irb_status` (`Literal["approved","exempt","not_applicable","unknown"]`), submitter fields (`submitter_name`, `submitter_institution`, `submitter_contact`, `submission_date`, all optional), `mds_coordinate`, `mds_uncertainty: BootstrapEllipse | None`, `distance_to_nearest_model`, `nearest_model_id`, `item_intersection_size`, `item_intersection_total`
  - [ ] `DomainResult` — with **`groundings: list[GroundingRef] = []`** (NOT a singleton — the v0.7 multi-baseline list) and **`selected_baseline_id: str | None = None`**
  - [ ] `FreelistRecord` — per `ARCHITECTURE.md` §3.2 with `prompt_verbatim`, `prompt_version`, `response_verbatim`, `response_object_json`, token counts, latency, `stop_reason`, parsed outputs
  - [ ] `PileSortRecord` — same shape, with `parsed_piles` and `parsed_matrix`
  - [ ] `InterviewRecord` — same shape, with `parsed_pile_labels`
  - [ ] `InformantRecord` — the full subject record per `ARCHITECTURE.md` §3.2, with model identity (including `model_version_returned`), collection conditions, the three step records, the `sha256_manifest` dict, and the QA fields
- [ ] All schemas validate (a unit test in `tests/unit/test_schemas.py` constructs a minimal instance of each, asserts it serializes to JSON and round-trips back)
- [ ] Every `Literal[...]` enum from §3.2 is preserved exactly — adding a value requires an architecture decision, not an ad-hoc change
- [ ] `cdb_core/ids.py` exists with the `run_id()` function per `ARCHITECTURE.md` §3.1 (deterministic SHA256[:16] of the tuple)
- [ ] `cdb_core/__init__.py` re-exports the public schemas
- [ ] Commit message: `feat(core): P0-T3 define all schemas including InformantRecord and v0.7 GroundingRef`

**Files touched.**

- `packages/cdb_core/__init__.py`
- `packages/cdb_core/schemas.py`
- `packages/cdb_core/ids.py`
- `packages/cdb_core/versioning.py` (placeholder OK)
- `tests/unit/test_schemas.py`

**Verification.** `uv run pytest tests/unit/test_schemas.py` passes. `uv run python -c "from cdb_core.schemas import InformantRecord, GroundingRef, DomainResult; print(GroundingRef.model_fields.keys())"` lists all v0.7 fields.

**Notes for the Coder.**

- Read `ARCHITECTURE.md` §3.2 in full before writing a single line. The schema is the contract; getting it wrong here ripples into every downstream package.
- Pay particular attention to `GroundingRef`. The v0.6 version was a singleton with seven fields; the v0.7 version is one element of a list, has 18+ fields, and supports two baseline kinds. Do NOT use the v0.6 version.
- `model_version_returned` on `InformantRecord` is mandatory and is the unit of analysis for the temporal view. Don't conflate it with `model_id`.
- `InformantRecord.sha256_manifest` is a `dict[str, str]` mapping SHA256 manifest keys to hex digests. The keys are listed in the `ARCHITECTURE.md` §3.2 InformantRecord docstring and must be exactly: `freelist_prompt`, `freelist_response`, `pilesort_prompt`, `pilesort_response`, `interview_prompt`, `interview_response`, `request_params`, `informant_record_total`.

---

## P0-T4 — Empty package skeletons

**Goal.** Create empty `packages/cdb_collect/`, `packages/cdb_analyze/`, `packages/cdb_publish/`, `packages/cdb_social/` directories with `__init__.py` files, module-level docstrings explaining each package's responsibility, and the directory substructure from `ARCHITECTURE.md` §2.

**Acceptance criteria.**

- [ ] Every package directory exists per `ARCHITECTURE.md` §2 monorepo layout
- [ ] Every package has an `__init__.py` with a docstring summarizing its responsibility (1–3 sentences) and a link to the relevant `ARCHITECTURE.md` section (§4.1 for collect, §4.2 for analyze, §4.4 for publish, §4.6 for social)
- [ ] `cdb_collect/adapters/`, `cdb_collect/protocol/`, `cdb_collect/prompts/v1/`, `cdb_collect/domains/v1/` all exist with `.gitkeep` or placeholder files
- [ ] `cdb_analyze/` has empty placeholder `.py` files for every module listed in `ARCHITECTURE.md` §2: `parse.py`, `cooccurrence.py`, `mds.py`, `cluster.py`, `consensus.py`, `drift.py`, `grounding.py`, `bootstrap.py`, `sensitivity.py`, `pipeline.py`. Each has a one-line docstring describing what it will do.
- [ ] `cdb_analyze/__init__.py` contains a **module-level comment block** that documents the no-LLM-imports rule from `ARCHITECTURE.md` §4.2 binding constraint. This is human-readable; the actual enforcement is the static check in T6.
- [ ] `cdb_publish/build.py`, `cdb_publish/schemas/`, `cdb_publish/README.md` exist as placeholders
- [ ] `cdb_social/triggers.py`, `cdb_social/drafters/`, `cdb_social/queue.py` exist as placeholders
- [ ] `scripts/` exists with empty placeholder files for `collect.py`, `analyze.py`, `publish.py`, `qa_check.py`, `build_db.py`, `cost_report.py` — each with a `if __name__ == "__main__": raise NotImplementedError("Phase 0 placeholder")` body and a docstring linking to the relevant `ARCHITECTURE.md` section
- [ ] All packages can be imported from a Python REPL without error
- [ ] Commit message: `chore: P0-T4 empty package skeletons`

**Files touched.** Many — see acceptance criteria.

**Verification.** `uv run python -c "import cdb_core, cdb_collect, cdb_analyze, cdb_publish, cdb_social; print('all imports OK')"` succeeds.

---

## P0-T5 — Data dictionary first draft

**Goal.** Create `docs/DATA_DICTIONARY.md` documenting `InformantRecord`, `GroundingRef`, the SQLite schema (target shape, even though `build_db.py` is a placeholder), and the JSONL canonical layer. Per `ARCHITECTURE.md` §4.3 this is a Phase 0 / Phase 1 deliverable; we land the first draft in Phase 0 so that any subsequent schema changes have a doc to update against.

**Acceptance criteria.**

- [ ] `docs/DATA_DICTIONARY.md` exists with the structure specified in the v0.3 version of this task list (see the dedicated `docs/DATA_DICTIONARY.md` skeleton document delivered alongside this task list)
- [ ] Every field on `InformantRecord` (top-level + the three step records + `sha256_manifest`) is documented with: type, required/optional, semantics, example value, source-of-truth pointer to `ARCHITECTURE.md` §3.2
- [ ] Every field on the v0.7 `GroundingRef` is documented similarly, with explicit notes on which fields are populated by the analysis pipeline at merge time vs. submitted by the researcher
- [ ] The SQLite schema section names every table and column the future `build_db.py` will produce (`informants`, `freelist_items`, `pilesort_cells`, `interview_labels`), with column types and intended indexes
- [ ] A short "Versioning and stability" section commits to: additive changes are non-breaking, removing or renaming a field is a major version bump, and every change requires a matching `ARCHITECTURE.md` update in the same PR (Reviewer rule 5)
- [ ] Commit message: `docs: P0-T5 data dictionary first draft`

**Files touched.**

- `docs/DATA_DICTIONARY.md` (created)

**Verification.** Manual review by Mark and the CDA SME agent. The dictionary should be readable as a standalone document by an outside researcher who has not read `ARCHITECTURE.md`.

**Note.** The first draft is delivered alongside this task list as a separate file. The Coder's job in P0-T5 is to commit it, not to write it from scratch. Subsequent updates as the schema evolves are normal PRs subject to Reviewer rule 5 (schema and dictionary co-update).

---

## P0-T6 — CI baseline

**Goal.** GitHub Actions workflow that runs on every push and PR: ruff lint, mypy type check, pytest unit tests, and the **`cdb_analyze` no-LLM-imports static check** as a hard requirement.

**Acceptance criteria.**

- [ ] `.github/workflows/ci.yml` exists, triggered on `push` to any branch and on `pull_request` against `main`
- [ ] CI runs on Ubuntu latest with Python 3.11
- [ ] Steps in order: checkout, setup Python, `uv sync`, `uv run ruff check .`, `uv run mypy packages/`, `uv run pytest tests/`, `uv run python scripts/check_no_llm_imports.py`
- [ ] **`scripts/check_no_llm_imports.py` exists** as a deterministic Python script that walks `packages/cdb_analyze/` and rejects any file containing an `import` or `from` statement referencing: `anthropic`, `openai`, `google.generativeai`, `huggingface_hub.InferenceClient`, `litellm`, `langchain`, `llama_index`, or any other LLM client library. The script exits non-zero on detection. Per `ARCHITECTURE.md` §1 commitment 6 and §4.2 binding constraint.
- [ ] The static check has its own unit test in `tests/unit/test_no_llm_imports_check.py` that creates a temporary file with a forbidden import and verifies the check rejects it
- [ ] CI passes on the empty repo (the static check finds nothing to reject because `cdb_analyze/` has no real code yet, but the script runs cleanly)
- [ ] `ruff.toml` and `mypy.ini` (or `pyproject.toml` sections) configured with project-appropriate strictness
- [ ] Commit message: `ci: P0-T6 CI baseline with no-LLM-imports static check`

**Files touched.**

- `.github/workflows/ci.yml`
- `scripts/check_no_llm_imports.py`
- `tests/unit/test_no_llm_imports_check.py`
- `pyproject.toml` (ruff + mypy config sections)
- `ruff.toml` (if separate from `pyproject.toml`)

**Verification.** Push to a branch, open a PR, observe CI green.

**Note for the Coder.** The no-LLM-imports check is the architectural enforcement of design commitment #6 in `ARCHITECTURE.md` §1. It is not optional and not a stylistic preference. The Reviewer agent has a Reviewer rule (rule 2) that backs this up, but the static check is the mechanical enforcement. If the check is missing or trivially bypassable, the project's most important safety property is not actually enforced.

---

## P0-T7 — Agent scaffolding and Slack webhook env vars

**Goal.** Create the `.claude/agents/` directory with subagent definitions for all six agents in the LSB pipeline, plus the three Slack webhook env var declarations in `.env.example` and the agent runtime configuration that reads them.

**Acceptance criteria.**

- [ ] `.claude/agents/` directory exists with one Markdown file per agent:
  - [ ] `architect.md` — Opus, owns `ARCHITECTURE.md`, decomposes into Coder-sized tasks, hands plans to CDA SME (and UI/UX for frontend), never writes code
  - [ ] `cda_sme.md` — Opus, methodological gatekeeper, four-axis verdict (protocol / analytical / claims / audience), posts to `#lsb-cda-sme`, also reviews researcher grounding submission PRs
  - [ ] `ui_ux.md` — **Sonnet, NEW in v0.7**, design conscience, frontend-only gate, four-question scorecard (OWID fidelity / 30-second journalist / researcher reproduce-and-cite / WCAG AA), posts to `#lsb-ui-ux`, owns `DESIGN_SYSTEM.md`
  - [ ] `coder.md` — Sonnet, implements one package or feature at a time, never invents visual decisions, must read `cdb_core/schemas.py` before touching any other file
  - [ ] `reviewer.md` — Sonnet, six rules per `ARCHITECTURE.md` §5.1 Reviewer row including the new rule 6 (frontend PRs require UI/UX verdict)
  - [ ] `tester.md` — Sonnet, fixtures only, pytest + vitest
- [ ] Each agent definition uses the correct frontmatter format: `name`, `tools` (comma-separated, NOT `allowed_tools` — this is the lesson learned from the agent-team project), and a one-paragraph system prompt summarizing the agent's role with a pointer to the relevant `ARCHITECTURE.md` section
- [ ] **`.env.example`** has the three Slack webhook variables with placeholder values:
  - `LSB_ALERTS_WEBHOOK_URL=https://hooks.slack.com/services/...` (for QA_Runner direct alerts)
  - `LSB_CDA_SME_WEBHOOK_URL=https://hooks.slack.com/services/...` (for CDA SME verdicts)
  - `LSB_UI_UX_WEBHOOK_URL=https://hooks.slack.com/services/...` (for UI/UX agent verdicts)
- [ ] A short `docs/AGENT_PIPELINE.md` exists summarizing the pipeline diagram from `ARCHITECTURE.md` §5.1 and §5.4 (the conditional UI/UX branch and the three Slack channels)
- [ ] Commit message: `chore: P0-T7 agent scaffolding with v0.7 UI/UX agent and Slack webhooks`

**Files touched.**

- `.claude/agents/architect.md`
- `.claude/agents/cda_sme.md`
- `.claude/agents/ui_ux.md`
- `.claude/agents/coder.md`
- `.claude/agents/reviewer.md`
- `.claude/agents/tester.md`
- `.env.example` (updated)
- `docs/AGENT_PIPELINE.md`

**Verification.** `ls .claude/agents/` returns six files. Each file's frontmatter parses cleanly. `grep -c WEBHOOK_URL .env.example` returns 3.

**Note.** The actual Slack webhook URLs are configured by Mark in his local `.env` (never committed). The agent runtime reads them from the env at task time. The three channels themselves (`#lsb-alerts`, `#lsb-cda-sme`, `#lsb-ui-ux`) are created in Slack as part of operational setup, not part of P0-T7 — but the env var slots and the agent definitions that reference them must exist after this task.

---

## P0-T8 — Empty data directories

**Goal.** Create the `data/` directory tree per `ARCHITECTURE.md` §2 with `.gitkeep` files where needed, including the **multi-baseline grounding directory layout** (`data/grounding/{domain}/{baseline_id}/`) with a placeholder Romney 1996 directory shape — empty, but with the right structure.

**Acceptance criteria.**

- [ ] `data/raw/` exists with `.gitkeep` (git-ignored content; the directory itself is tracked)
- [ ] `data/raw/informants.jsonl` is *not* created (it's append-only and starts empty when collection begins)
- [ ] `data/processed/` exists with `.gitkeep`
- [ ] `data/results/` exists with `.gitkeep` (git-tracked content per §4.3)
- [ ] `data/grounding/` exists with the **v0.7 multi-baseline directory layout**: `data/grounding/family/romney_1996/` exists as an empty directory with placeholder files for `source.md`, `items.txt`, `cooccurrence.csv`, `grounding_ref.json`, all containing `# Phase 4c deliverable — see ARCHITECTURE.md §4.2.5` as their only content
- [ ] `data/open_bundle/` exists with `.gitkeep`
- [ ] `data/cost_reports/` exists with `.gitkeep` (git-tracked)
- [ ] `data/social_queue/pending/` and `data/social_queue/approved/` exist with `.gitkeep`
- [ ] `data/domains/v1/` exists with placeholder `family.yaml`, `holidays.yaml`, `food.yaml` files (each containing only `# Phase 1 deliverable` as a comment, so the file structure is set up but no real domain definitions are committed yet)
- [ ] Commit message: `chore: P0-T8 empty data directories with v0.7 multi-baseline grounding layout`

**Files touched.** Many directory `.gitkeep` files plus the placeholder Romney 1996 files.

**Verification.** `find data -type d` returns the full tree per `ARCHITECTURE.md` §2.

**Note.** The placeholder Romney 1996 directory is the smallest possible expression of the v0.7 multi-baseline schema being live in the repo from day one. If a researcher submission lands during Phase 1, it can use this directory's shape as a template by analogy. The actual Romney 1996 data lands in Phase 4c.

---

## P0-T9 — Security scaffolding

**Goal.** Wire up `gitleaks` pre-commit, GitHub secret scanning, and Dependabot per `SECURITY_AND_HARDENING.md` §3.4 and §4.

**Acceptance criteria.**

- [ ] `.gitleaks.toml` exists at the repo root with the LSB-specific allow rules and detection patterns from `SECURITY_AND_HARDENING.md` §3.4
- [ ] `.pre-commit-config.yaml` exists with the `gitleaks` hook configured to run on every commit
- [ ] Pre-commit hook is installed and verified locally (`pre-commit install`)
- [ ] `.github/dependabot.yml` exists with Python (uv / pip) and npm ecosystems configured to check weekly, opening PRs against `main`, with `dependencies` and `security` labels
- [ ] GitHub secret scanning is enabled in the repo settings (Mark does this manually after the repo is created; the task list includes a checklist line for him)
- [ ] A short `SECURITY.md` at the repo root with: contact email (`security@cogstructurelab.ai` post-domain, dedicated ProtonMail before that), supported versions ("only `main` is supported pre-launch"), and a one-paragraph responsible disclosure policy per `SECURITY_AND_HARDENING.md` §6.5
- [ ] Commit message: `chore: P0-T9 security scaffolding (gitleaks, dependabot, SECURITY.md)`

**Files touched.**

- `.gitleaks.toml`
- `.pre-commit-config.yaml`
- `.github/dependabot.yml`
- `SECURITY.md`

**Verification.** Add a string matching an API key pattern to a temp file, attempt to commit, observe `gitleaks` blocking the commit. Push a PR, observe the dependabot config is recognized in the repo's "Insights → Dependency graph" view.

---

## P0-T10 — Dashboard scaffold + CSP + `_headers`

**Goal.** Create the `apps/dashboard/` directory with a working React + Vite + TypeScript + Tailwind scaffold, the `_headers` file with the strict CSP from `SECURITY_AND_HARDENING.md` §3.1, and a deployment to Cloudflare Pages staging that returns a "LSB — Phase 0 placeholder" page. **No actual components yet** — those land in Phase 5 per `ARCHITECTURE.md` §5.3 and the `DESIGN_SYSTEM.md` §11 component inventory.

**Acceptance criteria.**

- [ ] `apps/dashboard/` exists with `package.json`, `vite.config.ts`, `tsconfig.json`, `tailwind.config.js`, `postcss.config.js`
- [ ] `apps/dashboard/src/App.tsx` exists with a single placeholder element rendering "Latent Structure Benchmark — Phase 0 placeholder. Site under construction. See [github.com/...](github.com)."
- [ ] `apps/dashboard/src/main.tsx` mounts `App` to `#root`
- [ ] `apps/dashboard/index.html` references `main.tsx` and includes a basic `<meta>` tag set
- [ ] `apps/dashboard/src/styles/tokens.css` exists with **all design tokens from `DESIGN_SYSTEM.md` §1** (typography, colors, spacing, elevation) — even though no components consume them yet, the tokens are in place from day one
- [ ] `npm install && npm run build` succeeds in the dashboard directory; output lands at `apps/dashboard/dist/`
- [ ] **`apps/dashboard/public/_headers`** exists with the strict CSP from `SECURITY_AND_HARDENING.md` §3.1, including:
  - `Content-Security-Policy: default-src 'self'; connect-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; font-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'`
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- [ ] `unsafe-inline` in `style-src` is acknowledged in a comment at the top of `_headers` per resolved decision #22 in `ARCHITECTURE.md` §7
- [ ] Cloudflare Pages staging deployment is wired (Mark configures the GitHub→Cloudflare integration; the task list includes a checklist line for him)
- [ ] The staging URL returns the placeholder page with all CSP headers present (verify with `curl -I {staging_url}`)
- [ ] Commit message: `feat(dashboard): P0-T10 dashboard scaffold with CSP and design tokens`

**Files touched.**

- `apps/dashboard/package.json`
- `apps/dashboard/vite.config.ts`
- `apps/dashboard/tsconfig.json`
- `apps/dashboard/tailwind.config.js`
- `apps/dashboard/postcss.config.js`
- `apps/dashboard/index.html`
- `apps/dashboard/src/main.tsx`
- `apps/dashboard/src/App.tsx`
- `apps/dashboard/src/styles/tokens.css`
- `apps/dashboard/public/_headers`
- `apps/dashboard/.gitignore`

**Verification.** `curl -I {staging_url}` returns the CSP and security headers; `curl {staging_url}` returns the placeholder HTML; the page loads in a browser and renders the placeholder with the design tokens applied (background color, body font, etc.).

**Notes for the Coder.**

- Read `DESIGN_SYSTEM.md` §1 (Design Tokens) before writing `tokens.css`. Every value in the design tokens section is binding. Don't paraphrase, don't substitute "close enough" colors, don't drop the `--font-size-xl` because the placeholder doesn't use it. The tokens land in full in P0-T10 so that Phase 5 components can reference them from day one.
- The placeholder page is **not** a teaser landing page. It's a one-line "site under construction" message. Mark will write the real landing copy in Phase 6 personally per `ARCHITECTURE.md` §5.3 Phase 6.
- The Phase 5 dashboard scaffold builds on top of this. Don't pre-build any components in P0-T10; they belong in Phase 5 with full UI/UX agent gating per `ARCHITECTURE.md` §5.1.

---

## Exit criteria for Phase 0

Phase 0 is complete when **all of the following are true** (the Architect agent verifies before declaring Phase 0 done):

- [ ] All 10 tasks above are committed to `main`
- [ ] CI is green on `main` (P0-T6)
- [ ] `uv run python -c "from cdb_core.schemas import InformantRecord, GroundingRef, DomainResult"` succeeds (P0-T3)
- [ ] All four LICENSE files exist at the repo root (P0-T2)
- [ ] All six agent definitions exist in `.claude/agents/` with correct frontmatter (P0-T7)
- [ ] All three Slack webhook env vars exist in `.env.example` (P0-T7)
- [ ] `data/grounding/family/romney_1996/` exists as a placeholder with the multi-baseline shape (P0-T8)
- [ ] The `cdb_analyze` no-LLM-imports static check is wired into CI and has its own unit test (P0-T6)
- [ ] `gitleaks` pre-commit blocks commits containing API key patterns (P0-T9)
- [ ] The dashboard placeholder is live on Cloudflare Pages staging with all CSP headers present (P0-T10)
- [ ] `docs/DATA_DICTIONARY.md` first draft is committed (P0-T5)
- [ ] Mark has personally verified the security checklist items that require manual configuration: GitHub secret scanning enabled, two YubiKey 5C NFC keys enrolled on the LSB GitHub repo, dedicated ProtonMail address active

**When Phase 0 is complete, Phase 1 (collection layer) begins.** The Architect agent picks up Phase 1 from `ARCHITECTURE.md` §5.3 and decomposes Milestone A into Coder-sized tasks.

---

## Dependency graph

```
P0-T1 (scaffold) ──┬─→ P0-T2 (licenses)
                   ├─→ P0-T3 (schemas) ──┬─→ P0-T4 (skeletons) ──→ P0-T6 (CI)
                   │                     └─→ P0-T5 (data dict)
                   ├─→ P0-T7 (agents) ──→ Phase 1 ready
                   ├─→ P0-T8 (data dirs)
                   ├─→ P0-T9 (security)
                   └─→ P0-T10 (dashboard) ──→ Phase 5 ready
```

**Critical path:** T1 → T3 → T4 → T6 (~one Coder session if everything goes smoothly).

**Parallelizable:** T2, T7, T8, T9, T10 can all start as soon as T1 is committed. T5 needs T3 done first.

---

*End of `PHASE_0_TASKS.md` v0.3. Hand off to the Architect agent to assign individual tasks to the Coder. Phase 0 is execution against existing decisions, not a place to make new ones.*
