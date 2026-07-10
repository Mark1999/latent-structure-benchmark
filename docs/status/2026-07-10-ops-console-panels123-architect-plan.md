# Ops Console v1: Panels 1-3 Implementation Plan (Architect)

**Date:** 2026-07-10 (persisted by orchestrator; Architect has no write access)
**Spec:** `docs/proposed/2026-07-10-ops-console-campaign-runner-spec.md` (approved by Mark 2026-07-10)
**Scope:** Panels 1 (New Campaign), 2 (Live Board), 3 (QA). Panels 4-5 OUT of scope.
**Extends:** `packages/cdb_social/cdb_social/admin_console/` (existing Flask app).

## 1. Summary

Extend the loopback Flask admin console with three read-and-orchestrate panels that turn the batch A shell-script workflow into buttons. The console RUNS existing scripts (`scripts/collect.py`, `scripts/qa_check.py:run_record_checks`) via subprocess; it never reimplements their logic and never calls an LLM.

## 2. Binding boundaries encoded in every task

- **Rule 15 (math freeze):** panels render outputs from `scripts/qa_check.py:run_record_checks`, `data/raw/informants.jsonl`, `data/results/`, `data/models/registry.json`, `data/domains/v1/*.yaml`. Zero new statistics. "Recompute under current rules" in panel 3 means re-invoking `run_record_checks`, not new math.
- **B-1 (no autonomous LLM):** no import of `anthropic`, `openai`, `google.generativeai`, or any drafter class anywhere in panels 1-3. CI grep `cdb-social-boundary` semantic extends to the new `admin_console/campaign_runner/` and `admin_console/qa/` modules.
- **Append-only over `data/raw/informants.jsonl`:** panels open the file read-only. No mutation routes, no edit forms over records.
- **Rule 14 (no spend gates):** no cost estimates, no spend-cap text in any panel copy, code comment, or template. Provider billing dashboards remain Mark's cost surface.
- **Loopback + CSRF posture:** all new routes reuse `_new_csrf_token` / `_verify_csrf` from `routes.py`; no new auth; no host override.
- **Pitfall 13 (detector reuse):** failure-signature classification lives in ONE module (`admin_console/failure_signatures.py`) as data, not scattered regexes; the CDA SME reviews that table.

## 3. Affected packages and files

New files under `packages/cdb_social/cdb_social/admin_console/`:
- `campaign_runner/__init__.py`, `campaign_runner/planner.py`, `campaign_runner/launcher.py`
- `live_board/__init__.py`, `live_board/matrix.py`, `live_board/lane_state.py`
- `failure_signatures.py`
- `qa/__init__.py`, `qa/histogram.py`, `qa/divergence.py`, `qa/dispatch_templates.py`
- Templates: `new_campaign.html`, `dry_run_plan.html`, `live_board.html`, `lane_tail.html`, `qa.html`, `dispatch_template.html`
- `routes_ops.py` (new blueprint `ops_bp` mounted at `/ops/` to keep social routes isolated)

Modified: `admin_console/app.py` (register `ops_bp`), `templates/base.html` (nav entries).

New logs layout mirroring `logs/collect-batchA-20260710/`:
- `logs/ops-console/{campaign_id}/{safe_model}.log` (per-lane stdout+stderr)
- `logs/ops-console/{campaign_id}/{safe_model}.pid` (pidfile)
- `logs/ops-console/{campaign_id}/plan.json` (planner output, canonical shortfall snapshot)
- `logs/ops-console/{campaign_id}/lane.sh` (generated launcher)

New tests under `tests/unit/admin_console/` (planner, launcher, matrix, lane state, failure signatures, histogram, divergence, dispatch templates, routes). Fixtures: `tests/fixtures/ops_console/`.

No new dependencies (stdlib subprocess/os/pathlib/signal, existing Flask, existing pydantic).

## 4. Task decomposition

### T1: Campaign planner helper (no routes)
`campaign_runner/planner.py`: `list_domains()` (from `data/domains/v1/*.yaml`), `list_models(registry_path)` (model_id, display_name, family, records), `compute_shortfall(informants_path, models, domains, runs_per_cell) -> CampaignPlan` (per-cell `needed = max(0, runs_per_cell - passed)`, passed means qa_passed=True), `render_plan_text(plan)` (matches `resume-plan.txt` layout).
Acceptance: pure functions; injected paths; no subprocess, no Flask, no LLM imports. Handles empty informants.jsonl, missing registry entries; free-text new-domain slug returns a sentinel signalling "route to prompt-drafting" (no plan produced).

### T2: Panel 1 routes + templates
`routes_ops.py`: `GET /ops/campaigns/new`, `POST /ops/campaigns/plan`, `POST /ops/campaigns/launch`; templates `new_campaign.html`, `dry_run_plan.html`.
Behavior: domain selector + model multi-select with record counts + runs-per-cell (default 5) + free-text new-domain field; CSRF on all forms. Plan renders dry-run identical to `plan.json`; new-domain free text renders the Tier 1 prompt-drafting notice and never launches. Launch calls T3 and redirects to the live board.
Acceptance: dry-run/plan.json identity; new-domain notice never triggers subprocess; reduced UI/UX gate.

### T3: Lane launcher module
`campaign_runner/launcher.py`: `LaneLauncher` protocol; `SubprocessLaneLauncher` writes `lane.sh` mirroring `resume.sh` (one lane per model, domains sequential, no `--skip-collected`; planner already computed shortfall), spawns detached (`start_new_session=True`, stdout+stderr to `{safe_model}.log`), writes pidfiles atomically (`.tmp` + rename). Injectable `_spawn` (default `subprocess.Popen`).
Acceptance: no real subprocess in tests (fake `_spawn` receives exact argv/env); plan.json and lane.sh byte-identical for identical plans; no LLM imports; no spend text.

### T4: Live board matrix + lane state
`live_board/matrix.py`: `compute_matrix(informants_path, models, domains)` per-cell passed/failed/in-flight. `live_board/lane_state.py`: `discover_lanes(log_root)` reads pidfiles, checks `/proc/{pid}` (Linux; runs on lsb-agent-02), classifies running | exited_ok | exited_error | orphaned_pidfile; always reconstructs from filesystem (console restarts survive); PID-reuse guard (argv must contain `scripts/collect.py`). `stop_lane(pid)` SIGTERM then SIGKILL on timeout; injectable `_kill`.
Acceptance: deterministic matrix on fixtures; handles missing log_root, empty/non-numeric pidfile, reused PID; no mutation of informants.jsonl.

### T5: Panel 2 routes + templates
`routes_ops.py`: `GET /ops/live/{campaign_id}`, `GET .../lane/{safe_model}/tail`, `POST .../lane/{safe_model}/stop`, `POST .../resume`; templates `live_board.html`, `lane_tail.html`.
Behavior: matrix + alert rows (T6), per-lane Stop (CSRF), Resume recomputes shortfalls and relaunches only missing cells. Tail reads last 8 KiB; page-reload model, no polling loop.
Acceptance: post-restart correctness (no server-memory state); Stop on exited lane shows notice; Resume with all cells filled shows "nothing to do" and does not spawn.

### T6: Failure-signature module
`failure_signatures.py`: single data table `FAILURE_SIGNATURES` (id, label, source log|record, compiled regex or record-callable). Exactly five entries: `auth_401`, `billing_credit_balance`, `model_404`, `parse_after_retries` (PileSortParseError in log), `refusal_streak` (3+ consecutive refusal stop_reasons per (model_id, domain_slug) by collection_date). `scan(log_path, records_by_model_domain) -> hits`.
Acceptance: the table is the only place these classifications exist. **CDA SME reviews the table** (pitfall 13: log-source vs record-source entries must not share vocabulary that could cross-classify). No entries beyond the five without a new Architect plan.

### T7: QA histogram + divergence + dispatch templates
`qa/histogram.py`: bucket `run_record_checks` failures by check number per model (module import, not shelled). `qa/divergence.py`: per record, persisted qa_passed vs recomputed; emit disagreement rows with failing check numbers. `qa/dispatch_templates.py`: copy-ready Markdown blocks pre-filled with numeric evidence; text only, no dispatch mechanism.
Acceptance: no LLM imports; no mutation; divergence boundary labeled ("persisted = qa_passed at collection time; recomputed = current run_record_checks rules"). CDA SME reviews dispatch-template wording and divergence label copy.

### T8: Panel 3 routes + templates
`routes_ops.py`: `GET /ops/qa`; templates `qa.html`, `dispatch_template.html`. Histogram, divergence table, dispatch template blocks with client-side Copy.
Acceptance: loads on empty informants.jsonl; recomputation exceptions skip the row with a visible note; reduced UI/UX gate.

### T9: Nav + integration smoke test
`templates/base.html` nav links; Flask test-client walk of all GET pages against fixtures, 200 + CSRF token on every form.

## 5. Test plan

pytest, existing fixture conventions; no real API calls; no real subprocess (inject `_spawn`/`_kill`/proc-exists); no filesystem outside `tmp_path`. Fixtures under `tests/fixtures/ops_console/`: mini informants.jsonl (mixed qa_passed, one refusal streak), log fragments for the four log signatures. CI: extend the LLM-import boundary grep to the new admin_console modules (`ops-console-boundary` step or extended `cdb-social-boundary`); existing `no-spend-gate-check` already covers the paths.

## 6. Gate routing per task

| Task | CDA SME | UI/UX | Coder | Reviewer | Tester |
|---|---|---|---|---|---|
| T1 planner | no | no | yes | yes | yes |
| T2 panel 1 | no | yes (reduced) | yes | yes | yes |
| T3 launcher | no | no | yes | yes | yes |
| T4 matrix + lane state | no | no | yes | yes | yes |
| T5 panel 2 | no | yes (reduced) | yes | yes | yes |
| T6 failure signatures | **yes (pitfall 13)** | no | yes | yes | yes |
| T7 qa modules | **yes (template wording, divergence copy)** | no | yes | yes | yes |
| T8 panel 3 | no | yes (reduced) | yes | yes | yes |
| T9 nav + smoke | no | yes (reduced) | yes | yes | yes |

UI/UX gate scope (per the 2026-06-08 internal-ops precedent): WCAG AA accessibility floor and readable copy only; public DESIGN_SYSTEM.md and OWID fidelity not binding; R10 not applicable (no public numerics). CDA SME scope: T6 detector-reuse safety, T7 wording; no statistical math anywhere (rule 15 preserved).

## 7. Dependency order

T1 -> T2. T1 + T3 -> T5. T4 -> T5. T6 -> T5 (alert rows) and -> T7 (templates consume hits). T7 -> T8. T9 last. T1, T3, T4, T6 are independent modules and can be implemented in one sitting; the Reviewer sees them as separate commits.

## 8. Schema changes

None. No edits to `cdb_core/schemas.py`; no `DATA_DICTIONARY.md` update.

## 9. Reading list for the Coder

- `CLAUDE.md` sections 6 (rules 11, 14, 15), 7, 9 (pitfalls 5, 10, 13, 17)
- `ARCHITECTURE.md` sections 4.1.6 and 4.2 (the ops console extends the same no-LLM posture to itself)
- `docs/proposed/2026-07-10-ops-console-campaign-runner-spec.md` sections 3 and 5
- `packages/cdb_social/cdb_social/admin_console/routes.py` (CSRF helpers, blueprint patterns), `__main__.py` (loopback posture)
- `scripts/qa_check.py` (run_record_checks and checks 1-8)
- `scripts/collect.py` (--dry-run, --campaign-id, --runs, --model, --domain, --mode single_pass)
- `logs/collect-batchA-20260710/resume.sh` and `resume-plan.txt` (canonical shapes the launcher and planner mirror)
- Internal-ops UI precedent (2026-06-08): accessibility floor + readability; live-DOM verification rule does not apply (non-public, non-layout-critical panels)
