# Reviewer Verdict — Phase 5 T3: `cdb_publish` domain-JSON writer + derived display fields

**Filed:** 2026-05-10
**Reviewer:** LSB Reviewer agent (Sonnet)
**Commit reviewed:** `aef3262`
**Task:** Phase 5 T3 — `cdb_publish` domain-JSON writer + derived display fields
**Plan reference:** `docs/status/2026-05-09-phase5-architect-plan.md` §4 T3
**Prerequisite gate verdicts:**
- CDA SME plan-level PASS-WITH-NOTES: `fc72cad` (`docs/status/2026-05-09-phase5-cda-sme-plan-verdict.md`)
- UI/UX plan-level PASS-WITH-NOTES: `011f5bd` (`docs/status/2026-05-09-phase5-ui-ux-plan-verdict.md`)
- T3 has no per-task content gate per plan §6 gate table (T3 row: CDA SME = —, UI/UX = —)

---

## REVIEWER VERDICT: PASS

Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         PASS
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A
Check 6 — New deps sign-off:         N/A
Check 7 — Prompt versioning:         N/A
Check 8 — Uncertainty in viz:        N/A
Check 9 — Prerequisite verdicts:     PASS

---

## Check detail

**Check 1 — No LLM imports in `cdb_analyze/` (R6).**
`grep` for `import anthropic`, `import openai`, `from anthropic`, `from openai`, `InferenceClient`, `google.generativeai` in `packages/cdb_analyze/` returned two comment-only hits in `__init__.py` (the warning banner itself). No import statement. The two new files (`derived.py`, extended `build.py`) import only `cdb_core.schemas`, `cdb_publish.lede`, `cdb_publish.derived`, `pydantic`, `json`, `pathlib`, `datetime`. No LLM client library anywhere in scope. PASS.

**Check 2 — Append-only JSONL (`informants.jsonl`) and T3-specific read-only invariant (AC6).**
`git diff aef3262~1..aef3262 -- 'data/raw/' 'data/results/'` returned empty — no changes to either directory in this commit. `build.py` module docstring explicitly states "Source data/results/ files are read-only — this module MUST NOT write to results_dir." Code inspection confirms `build()` uses `.read_text()` on results files and never opens them for writing. SHA256 pre/post live run confirmed byte-identical. Test 7 in `test_build_domain_json.py` asserts this invariant programmatically against the real corpus. PASS.

**Check 3 — No secrets.**
All changed files scanned: `derived.py`, `build.py`, `schemas/manifest.py`, `test_derived.py`, `test_build_domain_json.py`, `.gitignore`. No API keys, tokens, webhook URLs (`LSB_ALERTS_WEBHOOK_URL`, `LSB_CDA_SME_WEBHOOK_URL`, `LSB_UI_UX_WEBHOOK_URL`), passwords, or credential-shaped strings found. PASS.

**Check 4 — Forbidden vocabulary (CLAUDE.md §7; ARCHITECTURE.md §1.5.4).**
Full scan of all five new/modified files for: `believes`, `thinks`, `worldview`, `recognizes`, `interprets`, `perceives`, `publishable`, `within-model consensus`, `within-model cultural consensus`, `within-model eigenratio`, `within-model CCM`. Zero hits in code, docstrings, comments, test copy. Commit message also clean. PASS.

**Check 5 — Schema + DATA_DICTIONARY.**
`git diff aef3262~1..aef3262 -- packages/cdb_core/cdb_core/schemas.py` returned empty — `cdb_core/schemas.py` was not touched. `manifest.py` is a publish-layer schema in `cdb_publish/schemas/`, not in `cdb_core/schemas.py`, and does not trigger the DATA_DICTIONARY co-update rule per the binding constraint (R7 applies only to `InformantRecord` and `GroundingRef` in `cdb_core/schemas.py`). N/A.

**Check 6 — New dependencies.**
`git diff aef3262~1..aef3262 -- pyproject.toml uv.lock` returned empty. No new dependencies added. N/A.

**Check 7 — Prompt versioning.**
No prompt template files were modified. N/A.

**Check 8 — Uncertainty in visualizations.**
Non-frontend commit. N/A.

**Check 9 — Prerequisite verdicts.**
T3 is not a frontend task (no `apps/dashboard/src/` changes) and has no per-task CDA SME or UI/UX gate per the plan §6 gate table. Plan-level gates (`fc72cad` CDA SME PASS-WITH-NOTES, `011f5bd` UI/UX PASS-WITH-NOTES) are both present and predate this commit. T2 lede content used by T3 was SME-content-cleared at `1868fca`. No prerequisite gates are missing. PASS.

---

## T3 Acceptance Criteria (AC1–AC7 + Q4)

**AC1 — Five output files produced.** `ls apps/dashboard/public/data/` confirms: `family.json`, `family.v0.2.json`, `holidays.json`, `holidays.v0.2.json`, `manifest.json`. PASS.

**AC2 — Non-empty `generated_lede`.** family lede=249 chars, holidays lede=334 chars. PASS.

**AC3 — `display` sub-object with `r1_states` and `top_terms`.** Both present and non-empty. PASS.

**AC4 — family 11 models, holidays 9 models in `r1_states`.** Confirmed: family r1_states=11, holidays r1_states=9. PASS.

**AC5 — manifest `oci_low_concentration_threshold: 3.0`.** Confirmed: `manifest threshold = 3.0`. PASS.

**AC6 — Source `data/results/` SHA256 byte-identical pre/post `build()`.** Confirmed: `diff /tmp/reviewer-before.sha /tmp/reviewer-after.sha` returned no output; `echo "AC6 PASS"` confirmed. PASS.

**AC7 — pytest, ruff, mypy, no-LLM-imports all pass.** Full suite: `1254 passed`. Ruff: `All checks passed!`. Mypy: `Success: no issues found in 8 source files`. No-LLM-imports check: `OK: no LLM client imports found in packages/cdb_analyze`. PASS.

**Q4 (SME binding) — `display.top_terms_metric == "sutrop_csi"` and ranking by Sutrop CSI descending with lexicographic tie-break.** `top_terms_metric` confirmed as `"sutrop_csi"` on both domains. `top_freelist_terms()` in `derived.py` sorts by `(-kv[1].csi, kv[0])` — descending CSI, ascending term for tie-break. Test 7 (stable tie-break) and Test 5 (basic ranking) both pass. The Coder's schema adaptation (`dict[str, list[SutropCSI]]` → `dict[entry.item: entry}` inside `_compute_display()`) faithfully reflects the actual `DomainResult.sutrop_csi` shape (model_id → list[SutropCSI]). PASS.

---

## Coder deviation notes (accepted)

1. `top_terms` count is 11 (family) / 9 (holidays) because all models have `sutrop_csi` entries in the real corpus. Plan comment said ~8; that was a preliminary-inspection estimate. Code correctly reflects actual data. Accepted.
2. `dict[str, list[SutropCSI]]` schema adaptation in `_compute_display()` — the `top_freelist_terms()` function accepts `dict[str, SutropCSI]` keyed by item, and `_compute_display()` correctly unpacks the `list[SutropCSI]` to build that dict via `{entry.item: entry for entry in csi_list}`. Accepted.

---

## R13 (no spend-gate framing)

`git grep` for `CDB_MAX_SPEND_USD`, `MAX_SPEND_USD`, `spend_cap` in `packages/cdb_publish/`, `tests/cdb_publish/`, `scripts/publish.py` returned no hits. PASS.

---

Coder may proceed to Tester dispatch.
