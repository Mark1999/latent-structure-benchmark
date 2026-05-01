# Reviewer Verdict — OPS-T1 Ops Dashboard Scaffold

**Task:** OPS-T1 — scaffold `apps/ops_dashboard/` Streamlit app
**Commit:** `9f72789`
**Date:** 2026-05-01
**Reviewer:** LSB Reviewer agent (claude-sonnet-4-6)
**Verdict:** PASS-WITH-NOTES

---

## Scorecard

```
REVIEWER VERDICT: PASS-WITH-NOTES

Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         PASS
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A
Check 6 — New deps sign-off:         PASS-WITH-NOTES
Check 7 — Prompt versioning:         N/A
Check 8 — Uncertainty in viz:        N/A
Check 9 — Prerequisite verdicts:     PASS
```

---

## Check-by-check findings

### Check 1 — No LLM client imports in `cdb_analyze/`
PASS. No LLM client imports in `packages/cdb_analyze/`. The new
`apps/ops_dashboard/app.py` and `apps/ops_dashboard/lib/__init__.py`
import only `streamlit`. No `anthropic`, `openai`, `google.generativeai`,
or `InferenceClient` anywhere in the new files.

### Check 2 — Append-only JSONL
PASS. `data/raw/informants.jsonl` not touched in this commit.

### Check 3 — No secrets
PASS. No API keys, tokens, webhook URLs, or credentials in any changed
file. The mypy override added to `pyproject.toml` references only the
module name `streamlit`. The `HOSTING_AND_DEV_OPS.md` addition documents
an SSH tunnel pattern and a launch command — no credentials. The
`apps/ops_dashboard/` files contain no key-shaped strings.

### Check 4 — Forbidden vocabulary
PASS. All five changed files (`HOSTING_AND_DEV_OPS.md`, `apps/ops_dashboard/README.md`,
`apps/ops_dashboard/app.py`, `apps/ops_dashboard/lib/__init__.py`,
`apps/ops_dashboard/pyproject.toml`) were scanned for:
- `worldview`, `believes`, `thinks` (applied to models)
- `Model X believes...`, `Model X thinks of...`, `How models see the world`
- `Model X's worldview`, `Cultural bias` (standalone)
- `What the model understands`
- `within-model consensus`, `within-model cultural consensus`,
  `within-model eigenratio`, `within-model CCM`
- `publishable` (for LSB findings)

No matches in user-facing or documentation context. (The README mention
of `anthropic` and `openai` is in a negation context describing the
read-only invariant — not a forbidden-vocabulary violation.)

### Check 5 — Schema + DATA_DICTIONARY
N/A. `cdb_core/schemas.py` not modified.

### Check 6 — New dependencies sign-off
PASS-WITH-NOTES.

**Streamlit dependency:** Added in `apps/ops_dashboard/pyproject.toml`
as `streamlit>=1.57,<1.58` under `[project.optional-dependencies] ops`.
This file is a **standalone pyproject** not enrolled as a uv workspace
member (confirmed: `apps/ops_dashboard` is absent from `pyproject.toml`
`[tool.uv.workspace] members`). Streamlit is therefore not a workspace
dependency and does not appear in `uv.lock`. In-session Architect plan
authorization (2026-05-01) is documented in the commit body. The
dependency is pinned to a minor-version range (`>=1.57,<1.58`) — good.
Streamlit is not on the `SECURITY_AND_HARDENING.md §4.3` approved list,
but that list enumerates workspace packages; this is an isolated ops
extra that does not touch any workspace package.

**Note N1 (binding for OPS-T2 onward):** If any future OPS-Tx task adds
`apps/ops_dashboard` to the uv workspace `members` list, or adds any new
pip dependency to the workspace root `pyproject.toml` dependencies block,
that change requires (a) explicit Architect sign-off, (b) an update to
`SECURITY_AND_HARDENING.md §4.3`, and (c) a `uv.lock` update in the same
commit. Reviewer will enforce on OPS-T2+.

**Root `pyproject.toml` touched:** Only a `[[tool.mypy.overrides]]`
section was added — no new dependency entry. `uv` does not read
`[tool.mypy.overrides]` when building the lockfile; `uv.lock` would be
byte-for-byte identical after this change. `SECURITY_AND_HARDENING.md §4.2`
states "The Reviewer agent rejects any PR that touches `pyproject.toml`
without a corresponding lockfile update." The Reviewer's judgment is that
a mypy configuration stanza is not within the scope of that rule because
it cannot affect the dependency resolver. **Note N2:** If a future PR
adds a mypy override AND a dependency in the same commit, both the dep
and the lockfile update must be present.

### Check 7 — Prompt versioning
N/A. No files under `packages/cdb_collect/prompts/` touched.

### Check 8 — Uncertainty in visualizations
N/A. This is a backend scaffold commit with no visualization components.
The `app.py` renders only static text; no MDS plot, no heatmap, no
chart. Future OPS-Tx tasks that add charts must satisfy this check at
that time.

### Check 9 — Prerequisite verdicts
PASS. This is a new initiative (not CDA-methodology-significant, not
frontend in the UI/UX-gate sense). Mark confirmed in-session scope and
Architect plan on 2026-05-01. No CDA SME or UI/UX verdicts required.

Rationale: (a) The ops dashboard is explicitly stated to be not bound by
`DESIGN_SYSTEM.md` and not in the UI/UX gate scope (per Mark's in-session
authorization). (b) A Streamlit scaffold with no analysis logic and no
new methodology triggers no CDA SME gate. (c) The task is not
methodologically significant — it is read-only display tooling.

---

## Notes on scope deviation flagged by Coder

**Standalone `pyproject.toml` (not a workspace extra):** The Coder
flagged this as a deviation and asked for Architect sign-off. The
Reviewer's position: this is a sound architectural choice. `apps/dashboard/`
is a Node.js app, not a Python workspace member; there is no Python
workspace precedent to copy. Making `apps/ops_dashboard/` a standalone
pyproject keeps Streamlit entirely out of the workspace dependency graph,
which is strictly safer than adding it as a workspace extra. No Architect
sign-off required beyond the in-session plan authorization already
documented. **This decision propagates as a constraint: `apps/ops_dashboard`
must remain outside the workspace members list for the lifetime of the
ops dashboard, unless Mark and the Architect explicitly decide otherwise.**

---

## Commit message issues

**Subject line length:** `feat(ops_dashboard): scaffold apps/ops_dashboard/ Streamlit app (task #OPS-T1)` is 78 characters. CLAUDE.md §8 requires the first line be under 72 characters.

**Scope not on approved list:** `ops_dashboard` is not in the CLAUDE.md §8
approved scope list (`core`, `collect`, `analyze`, `publish`, `social`,
`dashboard`, `scripts`, `docs`, `ci`). However, since this is a new
package not covered by the pre-existing list, `ops_dashboard` is the only
accurate scope available. The Reviewer treats this as a list-extension
event rather than a violation — the list was written before this package
existed.

**Note N3 (binding for OPS-T2 onward):** Commit subject lines for
`ops_dashboard` tasks must stay under 72 characters. Suggested short
form: `feat(ops): ...` — add `ops` to the approved scope list for all
ops-dashboard commits going forward. Mark or the Architect should confirm.

---

## Required before merge

1. **N3 — Commit subject line over 72 chars:** The current commit subject
   is 78 characters. CLAUDE.md §8 requires ≤72. Options: (a) amend the
   commit subject before merge (Mark's call since only Mark can override a
   Reviewer finding), or (b) Mark accepts this as a one-time exception
   for the first OPS-T1 commit and documents it here. The commit is
   otherwise clean; this is the sole blocking issue.

---

## Constraints propagating to OPS-T2 onward

- **C1:** `apps/ops_dashboard/` must remain outside the uv workspace
  `members` list unless Mark and Architect explicitly authorize enrollment.
- **C2:** Any new pip dependency in `apps/ops_dashboard/pyproject.toml`
  requires in-session Architect authorization documented in the commit body.
- **C3:** Any visualization added in OPS-T2+ that displays a point
  estimate (chart coordinate, metric value) must include its associated
  uncertainty or explicitly document why uncertainty is N/A for ops
  tooling (ops tool ≠ published finding, so the §4.5 uncertainty rule
  applies with softer force here; Reviewer will accept a documented
  rationale).
- **C4:** The read-only invariant stated in `app.py` and `README.md`
  (no writes to any data file, no LLM client imports) is a binding
  constraint on every OPS-Tx task. Reviewer will check on each PR.
- **C5:** Commit subject lines for `ops_dashboard` tasks must be ≤72
  characters. Recommended scope token: `ops`.

---

*Verdict issued by LSB Reviewer agent. Only Mark can override a FAIL.
PASS-WITH-NOTES: the single note (N3, commit subject length) is Mark's
call to accept as exception or to amend before merge. All nine rule
checks otherwise pass.*
