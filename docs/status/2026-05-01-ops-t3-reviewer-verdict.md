# Reviewer Verdict — OPS-T3 Run Picker Page

**Task:** OPS-T3 — Run picker page for the internal ops dashboard  
**Commit:** `92bb163`  
**Date:** 2026-05-01  
**Reviewer:** LSB Reviewer agent (Claude Sonnet 4.6)  
**Predecessor verdicts:** OPS-T1 PASS-WITH-NOTES, OPS-T2 PASS

---

## Summary

```
REVIEWER VERDICT: PASS

Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         PASS
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A
Check 6 — New deps sign-off:         PASS
Check 7 — Prompt versioning:         N/A
Check 8 — Uncertainty in viz:        N/A
Check 9 — Prerequisite verdicts:     PASS
```

---

## Check-by-check findings

### Check 1 — No LLM client imports in `cdb_analyze/`
PASS. The grep for actual `import` / `from` statements matching `anthropic`, `openai`,
`google.generativeai`, or `InferenceClient` in `packages/cdb_analyze/` returns zero
matches. The two hits in `packages/cdb_analyze/cdb_analyze/__init__.py` are comment
text (the prohibition notice itself), not import statements — consistent with the
OPS-T2 finding on the same file.

The new files in this commit (`apps/ops_dashboard/lib/picker.py`,
`apps/ops_dashboard/app.py`, `tests/test_ops_dashboard_app.py`) contain no LLM
client imports.

### Check 2 — Append-only JSONL
PASS. `data/raw/informants.jsonl` does not appear in the commit's changed file list.
No existing lines modified or deleted.

### Check 3 — No secrets
PASS. All four changed files scanned. No API keys, tokens, webhook URLs
(`LSB_ALERTS_WEBHOOK_URL`, `LSB_CDA_SME_WEBHOOK_URL`, `LSB_UI_UX_WEBHOOK_URL`),
passwords, or credential-pattern strings. The `pyproject.toml` diff adds only a
`[tool.mypy]` configuration stanza (`explicit_package_bases = true`) with no
key-shaped content.

### Check 4 — Forbidden vocabulary
PASS. All diff lines scanned against the full table from CLAUDE.md §7 and
ARCHITECTURE.md §1.5.4:

- `worldview`, `believes`, `thinks` (applied to models) — not present
- `"Model X believes..."`, `"Model X thinks of..."`, `"How models see the world"` — not present
- `"Model X's worldview"`, `"Cultural bias"` (standalone) — not present
- `"What the model understands"` — not present
- `"within-model consensus"`, `"within-model eigenratio"`, `"within-model CCM"` — not present
- `"publishable"` (for LSB findings) — not present

The UI strings in `app.py` (`"model_id"`, `"domain"`, `"informant_id"`, the
`st.info` message `"Detail view coming in OPS-T4 — selected: ..."`) contain no
forbidden vocabulary and make no claims about model cognition.

### Check 5 — Schema + DATA_DICTIONARY
N/A. `cdb_core/schemas.py` is not in the commit. No schema changes.

### Check 6 — New dependencies sign-off
PASS. Evaluated on three axes:

**C1 (workspace members):** `apps/ops_dashboard` confirmed absent from
`[tool.uv.workspace] members` in root `pyproject.toml`. Members remain the five
`packages/` entries only. OPS-T1/T2 constraint C1 upheld.

**C2 (no new pip deps):** The only change to root `pyproject.toml` is the addition
of `explicit_package_bases = true` under `[tool.mypy]`. The `[project.dependencies]`
block and the `[dependency-groups]` block are unchanged. No new entry in
`apps/ops_dashboard/pyproject.toml` (not touched in this commit). OPS-T1/T2
constraint C2 upheld.

**`explicit_package_bases` vs. lockfile rule (OPS-T1 Note N2):** This is a
`[tool.mypy]` configuration key, not a dependency resolver entry. It is not read by
`uv` when resolving or locking the dependency graph. OPS-T1 Note N2 classified mypy
configuration stanzas as outside the "lockfile update required" rule; this PR is
consistent with that precedent. No `uv.lock` update required. The Coder's reasoning
is correct and consistent with OPS-T1 N2.

### Check 7 — Prompt versioning
N/A. No files under `packages/cdb_collect/prompts/` touched.

### Check 8 — Uncertainty in visualizations
N/A. No files under `apps/dashboard/` touched. No new visualization components, no
MDS plots, no heatmap cells. The ops dashboard is not bound by the public dashboard
uncertainty requirement (CLAUDE.md §6 rule 11 / ARCHITECTURE.md §4.5 apply to
`apps/dashboard/` only).

### Check 9 — Prerequisite verdicts
PASS. This commit is not a frontend PR (`apps/dashboard/` not touched) and not a
methodology PR (no analysis measures, gate thresholds, schema methodology fields,
lede templates, or ARCHITECTURE.md §1.5.x content). No CDA SME or UI/UX gate
verdict required.

Predecessor verdicts are correctly cited in the commit body:
- OPS-T1 PASS-WITH-NOTES: `docs/status/2026-05-01-ops-t1-reviewer-verdict.md`
- OPS-T2 PASS: `docs/status/2026-05-01-ops-t2-reviewer-verdict.md`

Both verdict files exist on disk and were verified. All propagated constraints
from OPS-T1/T2 (C1–C5) are documented and upheld.

---

## Coder-flagged items evaluated

### Item 1 — `explicit_package_bases = true` consistency with OPS-T1 Note N2

Confirmed consistent. The `explicit_package_bases` key is a `[tool.mypy]` global
option, not a dependency entry. OPS-T1 Note N2 established the precedent that mypy
configuration stanzas under `[tool.mypy]` or `[[tool.mypy.overrides]]` are outside
the lockfile-update rule because `uv` does not read them during dependency
resolution. This PR applies the same classification correctly.

### Item 2 — OPS-T2 note on `informant_id` in user-facing labels

CONFIRMED APPLIED. The OPS-T2 verdict note stated: "If OPS-T3+ adds a function that
surfaces this as a user-facing label in the dashboard UI, prefer `informant_id` (the
canonical schema vocabulary) over `run_id`."

The `st.selectbox` in `app.py` uses `label="informant_id"` and the commit body
explicitly cites this: `"OPS-T2 Reviewer note applied: user-facing label uses
canonical 'informant_id' (not 'run_id') per DATA_DICTIONARY.md §1.1."` The
`session_state` key is also `"selected_informant_id"`. All user-facing strings
correctly use the canonical schema vocabulary.

---

## OPS-T1/T2 constraints — compliance check

| Constraint | Requirement | Status |
|---|---|---|
| C1 | `apps/ops_dashboard/` outside uv workspace `members` | PASS — confirmed absent from `[tool.uv.workspace]` members |
| C2 | No new pip deps | PASS — only `[tool.mypy]` config key added; `[project.dependencies]` unchanged |
| C3 | Viz point estimates require uncertainty or rationale | N/A — no visualizations in this commit |
| C4 | Read-only invariant — no `open(..., "w"/"a")` in production code | PASS — `picker.py` is pure functions (no I/O); `app.py` contains no file writes; `st.session_state` is in-memory only |
| C5 | Commit subject ≤72 characters | PASS — 60 characters: `feat(ops): add run picker page with sidebar filters (OPS-T3)` |

---

## Tests check (R10 / CLAUDE.md rule 10)

`tests/test_ops_dashboard_app.py` explicitly states at line 4: "All tests use
synthetic InformantRecord fixtures constructed in-memory. No real API calls. No reads
from `data/raw/informants.jsonl`." The test module builds all fixtures via
`_make_record()` with hard-coded synthetic values. The `load_informants` function is
not called anywhere in the test file. PASS.

---

## Conventional Commits check

Subject: `feat(ops): add run picker page with sidebar filters (OPS-T3)` — 60
characters. Scope token `ops` is consistent with OPS-T1/T2 precedent. Body bullets
document the four changed files, all five C1–C5 constraints, the OPS-T2 note
resolution, and the predecessor verdict file paths. PASS.

---

## Failures

None.

---

## Required before merge

None. All nine checks pass.

---

## Constraints propagating to OPS-T4+

All constraints from OPS-T1/T2 continue to propagate:

- **C1:** `apps/ops_dashboard/` must remain outside uv workspace `members`.
- **C2:** Any new pip dependency requires Architect authorization documented in the
  commit body.
- **C3:** Visualizations displaying point estimates require associated uncertainty or
  a documented rationale for why the ops-tool context makes the §4.5 rule
  inapplicable.
- **C4:** The read-only invariant is binding. No `open(..., "w" | "a")` in production
  code under `apps/ops_dashboard/`. Test helpers writing to `tmp_path` are exempt.
- **C5:** Commit subjects ≤72 characters. Scope token `ops`.

**New from OPS-T3:** `session_state` and `@st.cache_data` patterns are now
established for the ops dashboard. OPS-T4+ should maintain consistency:

- **`session_state["selected_informant_id"]`** is the canonical key for passing the
  picker selection to downstream pages. OPS-T4 (detail view) should read from this
  key; it should not introduce a parallel `selected_run_id` or similar alias.
- **`@st.cache_data` on the loader call** is the established pattern for the
  top-level record load. OPS-T4+ pages that need a filtered subset should call the
  already-cached `_load_all()` function and apply their own filters via the
  `apply_filters()` helper — they should not add a second `@st.cache_data`-wrapped
  loader for the same file.
- **`st.stop()` as the error/no-match early-exit pattern** is established. Keep it
  consistent across pages rather than introducing `st.rerun()` or exception-based
  exit patterns without CDA SME or Architect rationale.

---

*Verdict issued by LSB Reviewer agent. Only Mark can override a FAIL.  
Verdict: PASS — Coder may merge.*
