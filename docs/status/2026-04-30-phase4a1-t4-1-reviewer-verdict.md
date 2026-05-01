# Reviewer Verdict — Phase 4a.1 T4.1 Safety Attribution Subtype Scaffold (task #21.T4.1)

**Filed:** 2026-05-01
**Reviewer:** LSB Reviewer (Sonnet)
**Commit under review:** `6aa0986`
**Task:** #21.T4.1 — safety attribution subtype scaffold
**Gate verdicts cited:**
- Architect Amendment 3: `docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md` (committed at `4f68d9f`)
- CDA SME PASS-WITH-NOTES: `docs/status/2026-04-30-phase4a1-amendment-3-cda-sme-verdict.md` (committed at `4f68d9f`)

---

## REVIEWER VERDICT: PASS

```
Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         PASS
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A
Check 6 — New deps sign-off:         N/A
Check 7 — Prompt versioning:         N/A
Check 8 — Uncertainty in viz:        N/A
Check 9 — Prerequisite verdicts:     PASS
```

---

## What was verified

### Check 1 — No LLM imports in cdb_analyze/
`grep -r "import anthropic\|import openai\|from anthropic\|from openai\|InferenceClient\|google.generativeai" packages/cdb_analyze/` returned only two lines in `cdb_analyze/__init__.py`, both in a comment block listing forbidden libraries (not import statements). The new module `safety_subtype.py` imports only `json`, `pathlib`, `typing.Literal`, `pydantic`, and `cdb_analyze.manual_classification`. No LLM client libraries present anywhere in the package. PASS.

### Check 2 — Append-only JSONL
`git show --stat 6aa0986` lists three new files only; `data/raw/informants.jsonl` is absent from the diff. `git log -- data/raw/informants.jsonl` shows no recent commits touching that file. PASS.

### Check 3 — No API keys or secrets
Scanned all three files in the commit for key-shaped strings (`sk-`, `api_key`, `password`, `webhook`, `token`, `secret`, `LSB_ALERTS_WEBHOOK_URL`, etc.). No matches. PASS.

### Check 4 — Forbidden vocabulary
Grepped all changed `.py` files and commit message for `worldview`, `believes`, `thinks` (applied to models), `within-model consensus`, `within-model cultural`, `within-model eigenratio`, `within-model CCM`, `publishable`. No matches. Docstrings consistently use "attribute" / "attribution narrative" language, not belief/cognition language. Commit message and inline comments are clean. PASS.

### Check 5 — Schema + DATA_DICTIONARY
`cdb_core/schemas.py` was not modified (confirmed via `git show 6aa0986 -- cdb_core/schemas.py`). The new Pydantic model lives in `cdb_analyze`, not `cdb_core`. Per Architect Amendment 3 §3.1 and CLAUDE.md §6 rule 7, the `DATA_DICTIONARY.md` update rule fires only on `cdb_core/schemas.py` changes. N/A.

### Check 6 — New dependencies
No changes to `pyproject.toml` or `apps/dashboard/package.json` in the commit. N/A.

### Check 7 — Prompt template versioning
No files under `packages/cdb_collect/prompts/` in the commit. N/A.

### Check 8 — Uncertainty in visualizations
Not a frontend task; no visualization components changed. N/A.

### Check 9 — Prerequisite gate verdicts
Both required gate verdicts are present and committed at `4f68d9f`, which precedes `6aa0986`:
- Architect Amendment 3 (plan gate): `docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md`
- CDA SME PASS-WITH-NOTES: `docs/status/2026-04-30-phase4a1-amendment-3-cda-sme-verdict.md`

The CDA SME verdict issued PASS-WITH-NOTES with three new binding notes (B13 soft, B14 binding on T5, B15 soft). B13 and B15 are soft and bind only future tasks. B14 binds T5 §8.1/§8.2 — not T4.1. No notes from the SME verdict impose obligations on this commit. PASS.

---

## Specific acceptance-criteria spot-checks (per task brief)

**Sentinel rejection — loader pre-check pattern:**
Confirmed at `safety_subtype.py` lines 188–203. The loader parses raw JSON first, extracts `decline_interview_id` for the error message, then checks `safety_attribution_subtype == "UNCLASSIFIED"` *before* calling `model_validate`. Error message reads: `"Safety attribution subtype incomplete: row {did!r} is still UNCLASSIFIED. Mark must hand-code all 9 rows before T4.2 runs."` — operator-friendly and names the row. Tests `test_loader_rejects_unclassified_sentinel` and `test_loader_rejects_unclassified_names_the_row` both pass (verified independently by running the suite).

**Determinism guarantee:**
`build_safety_subtype_seed.py` sorts by `decline_interview_id` (line 126) and uses `json.dumps(sort_keys=True, ensure_ascii=False)` (line 83). Test `test_seed_builder_deterministic` runs the builder twice on identical input and asserts `content1 == content2` using `read_bytes()` (byte-level comparison). PASS.

**Parent-join enforcement:**
`safety_subtype.py` lines 178–221. Parent artifact is loaded first via `load_manual_classifications`; every subtype row is checked for presence in parent dict (pre-check 2, line 206) and then for `manual_classification == "safety_event_attribution"` (pre-check 3, line 214). Both produce descriptive `ValueError`s naming the offending ID and the actual parent classification. Tests `test_loader_rejects_id_not_in_parent`, `test_loader_rejects_non_safety_parent_classification`, and `test_loader_rejects_non_safety_names_actual_classification` all pass.

**No write-back to T3C artifacts:**
`git show --stat 6aa0986` — only three files modified, all new additions. `data/derived/decline_interviews_manual_classification.jsonl` is not in the commit.

**No data file committed:**
`data/derived/decline_interviews_safety_attribution_subtype.jsonl` is absent from `git show --stat 6aa0986`. Confirmed.

**CI safety — no dotenv on import:**
`build_safety_subtype_seed.py` imports only `argparse`, `json`, `sys`, and `pathlib.Path` at module level. No `dotenv`, no `os.environ` references at module scope. `test_seed_builder_module_importable_without_dotenv` passes.

**Test suite — independent run:**
`uv run pytest tests/test_safety_subtype.py -v`: 31/31 PASSED, 0.14s. All 31 tests verified independently.

**Linting and types:**
`uv run ruff check .`: "All checks passed!"
`uv run mypy packages/`: "Success: no issues found in 54 source files"

---

## Failures

None.

## Required before merge

None. Coder may merge / commit is on master.

---

## Notes for the Tester

1. The test fixture plan in Amendment 3 §3.1 calls for "4–5 hand-rolled manual-classification rows + 2–3 matching subtype rows." The actual fixture uses 4 parent rows (2 safety, 2 non-safety) and validates both subtype values. Coverage is complete for the acceptance criteria; however the round-trip test (`test_loader_round_trip`) loads only 2 subtype rows simultaneously. Consider adding a fixture test that loads all 9 mock rows at once (simulating the full Mark hand-code artifact) for T4.2 test planning.

2. B13, B14, B15 from the CDA SME verdict are not binding on T4.1 tests. B14 binds T5 §8.1/§8.2 — the Tester covering T5 should read the SME verdict for the numerics-vs-interpretation separation requirement.

3. The idempotency guard test (`test_seed_builder_idempotency_guard`) covers the force/no-force branches thoroughly; no gap found.

---

*End of Reviewer verdict for commit `6aa0986`. Binding for T4.1. Coder may proceed; Mark's hand-code commit is next in the gate chain per Amendment 3 §3.1.*
