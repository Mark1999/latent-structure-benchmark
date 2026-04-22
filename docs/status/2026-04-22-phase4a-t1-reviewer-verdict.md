# Phase 4a T1 — Reviewer Verdict

**Date:** 2026-04-22
**Commit reviewed:** `7076dc4 feat(scripts): adapter preflight for Phase 4a kickoff (task #9)`
**Architect verdict:** `docs/status/2026-04-22-phase4a-kickoff-architect-verdict.md` §4 T1
**Slate verdict:** `docs/status/2026-04-22-phase4a-slate-cda-sme-verdict.md`
**Preceding gates:** No CDA SME or UI/UX required for T1 per Architect §6.

---

## Verdict: **PASS**

All 15 `CLAUDE.md` §6 rules satisfied. All 7 task-specific acceptance criteria met. Preflight report matches live run.

---

## R-rule findings

- **R9 (no secrets):** PASS — no API key literals, no webhook URLs, no credential values across the three files.
- **R10 (no real API calls in tests):** PASS — `tests/scripts/test_preflight.py` header documents "No real API calls." 14 test functions mock `_load_model_ref`, `_create_adapter`, `_write_report`. No `.complete()` call appears.
- **R12 (no LLM imports in cdb_analyze):** PASS — matches in `packages/cdb_analyze/cdb_analyze/__init__.py:12-13` are comment prohibition text, not import statements.
- **R7 (schema + DATA_DICTIONARY):** N/A — no `cdb_core/schemas.py` touch.
- **R11 (uncertainty):** N/A — no visualization work.
- **R6 (new deps sign-off):** PASS — `pyproject.toml` / `uv.lock` absent from commit.
- **R4 (forbidden vocabulary):** PASS — zero matches for forbidden phrases across all three files.
- **R2 (append-only JSONL):** PASS — `data/raw/informants.jsonl` not in commit.
- **R8 (prompt versioning):** N/A.

## Task-specific findings

1. **No writes to `data/raw/informants.jsonl`:** PASS. Module docstring line 13 explicitly disclaims; no write code path.
2. **Probe prompt is not a CDA domain prompt:** PASS. `PROBE_PROMPT = "Reply with exactly the word 'ok' and nothing else."` — no family/holidays/food/free-list/pile-sort vocabulary.
3. **Five collection_methods exercised:** PASS. `PROBE_SLATE` contains exactly `{anthropic_api, openai_api, google_ai, xai_api, openrouter}`.
4. **xai_api specifically exercised:** PASS. `x-ai/grok-4` present with "Critical never-canonically-tested adapter" label.
5. **Preflight report content:** PASS. `docs/status/2026-04-22-phase4a-preflight.md` contains timestamp `2026-04-22T18:07:17.215901+00:00`, per-method PASS/FAIL, per-method cost and latency, total cost `$0.010051`, Grok-4 content refusal observation, forward recommendation to Architect.
6. **Exit code semantics:** PASS. `return 0 if len(failed) == 0 else 1`; `sys.exit(main())` at entry point.
7. **No `InformantRecord` produced:** PASS. Zero `InformantRecord` references; local `ProbeResult` dataclass only.

## Test findings

14 tests confirmed. Distribution: 7 tests on `_load_model_ref` (all 5 registry models + unknown-model error + missing-registry error), 5 tests on `_create_adapter` (one per collection_method), 2 tests on `_write_report` (mixed PASS/FAIL + all-PASS). `monkeypatch.setattr` correctly redirects `REGISTRY_PATH` and `REPORT_PATH` to `tmp_path`. No filesystem side-effects.

## Live preflight report sanity

| method | model | result | latency | cost | model_version_returned |
|---|---|---|---|---|---|
| anthropic_api | claude-sonnet-4.6 | PASS | 1084ms | $0.000120 | `claude-sonnet-4-6` |
| openai_api | gpt-5.4-mini | PASS | 1531ms | $0.000031 | `gpt-5.4-mini-2026-03-17` |
| google_ai | gemini-2.5-pro | PASS | 2416ms | $0.001686 | `gemini-2.5-pro` |
| xai_api | grok-4 | PASS | 7674ms | $0.008208 | `grok-4-0709` |
| openrouter | mistral-small-2603 | PASS | 842ms | $0.000005 | `mistralai/mistral-small-2603` |

Total: **$0.010051** (5/5 PASS).

Grok-4 reported 696 input tokens against an ~8-word probe, explained in the report as server-side system-prompt injection. Mechanics PASS is correct: auth, `model_version_returned`, response parsing, `cost_usd` all populated and non-zero.

## Forward notes (non-blocking)

1. **Grok-4 content refusal.** Grok-4 refused the probe prompt as a jailbreak heuristic. Before T4 fanout, run one `x-ai/grok-4 × family` cell manually to confirm the CDA free-list prompt does not also trigger refusal. The preflight report already carries this recommendation. **Action: incorporate into the T4 task brief when T4 spawns — the "inspect first model's output before fanning out" precaution from `SHAKEDOWN_PROTOCOL.md` §5 applies specifically to Grok-4 here.**

2. Commit subject line 63 chars (under 72). Conventional Commits `feat(scripts):` scope correct. Commit body references both verdict paths.

---

*End of verdict. Task #9 complete. T2 (CLI semantics confirmation) unblocked — orchestrator-executed.*
