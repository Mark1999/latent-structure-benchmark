# OPS-T4 Single-Informant Detail View — Reviewer Verdict

**Date:** 2026-05-01
**Reviewer:** LSB Reviewer agent (Sonnet 4.6)
**Commit reviewed:** `c74029263298f8d9ceb383a664c7a1b9c70c1e16`
**Task:** OPS-T4 — single-informant detail view for the internal ops dashboard
**Files reviewed:**
- `apps/ops_dashboard/lib/detail.py` (new)
- `apps/ops_dashboard/lib/loader.py` (extended)
- `apps/ops_dashboard/app.py` (detail view added)
- `tests/test_ops_dashboard_detail.py` (new, 31 tests)

**Prerequisite verdicts on file:**
- CDA SME PASS-WITH-NOTES: `docs/status/2026-05-01-ops-wireframes-cda-sme-verdict.md`
- Predecessor Reviewer PASS: `docs/status/2026-05-01-ops-t3-reviewer-verdict.md`
- Predecessor Reviewer PASS-WITH-NOTES: `docs/status/2026-05-01-ops-t1-reviewer-verdict.md`

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

## Check-by-check rationale

### Check 1 — No LLM client imports in cdb_analyze/

No LLM client imports in `packages/cdb_analyze/`. The one grep match in
`packages/cdb_analyze/cdb_analyze/__init__.py` is a comment documenting the
prohibition, not an import statement. No LLM client imports appear in
`apps/ops_dashboard/` either (the README match is documentation-only). PASS.

### Check 2 — Append-only JSONL

`data/raw/informants.jsonl` is not in the changed files list. PASS.

### Check 3 — No secrets

Scanned all four changed files for API key patterns, Slack webhook URLs,
and credential-shaped strings. No matches. PASS.

### Check 4 — Forbidden vocabulary

Scanned `app.py`, `detail.py`, and `loader.py` (non-test files) for
`worldview`, `believes`, `thinks of`, `cultural bias`, `How models see the
world`, `What the model understands`, `within-model consensus`,
`within-model eigenratio`, `within-model CCM`, and related phrases per
CLAUDE.md §7 and ARCHITECTURE.md §1.5.4. No matches in source or
documentation strings.

The "thinking trace" expander is labeled "chain-of-thought output text ...
not an interpretation of internal cognition" — correct §1.5 framing.
PASS.

### Check 5 — Schema + DATA_DICTIONARY

`cdb_core/schemas.py` not touched. N/A.

### Check 6 — New deps sign-off

`pyproject.toml` and `apps/dashboard/package.json` not in the changed files.
No new dependencies introduced. N/A.

### Check 7 — Prompt versioning

No files under `packages/cdb_collect/prompts/` touched. N/A.

### Check 8 — Uncertainty in visualizations

This PR touches only the internal ops dashboard (`apps/ops_dashboard/`),
not the public dashboard (`apps/dashboard/`). No visualizations with point
estimates. N/A.

### Check 9 — Prerequisite verdicts

**Non-frontend task**: UI/UX gate does not apply. The SME verdict at
`docs/status/2026-05-01-ops-wireframes-cda-sme-verdict.md` establishes
the ops dashboard is explicitly carved out from the UI/UX gate per Architect
scoping.

**Methodology-adjacent (rendering layer)**: CDA SME issued PASS-WITH-NOTES
with five notes. All five are verified applied in the commit:

- **Note 1** (pile-sort provenance): `st.caption("*Pile labels and member
  ordering are the model's own output, verbatim. Not re-summarized or
  re-ordered.*")` rendered directly under `### Pile-sort`. APPLIED.

- **Note 2** (singletons inline, not collapsed): Singletons rendered with
  `is_singleton` flag in the same pile-order loop as multi-member piles.
  No `st.expander` around singletons. Format: `Pile N (singleton): "{label}"`.
  APPLIED.

- **Note 3** ("0 items elicited" framing kept): Freelist empty state uses
  the correct CDA elicitation framing. APPLIED.

- **Note 4** (decline disclaimer): `st.caption("*The verbatim text below
  contains the model's stated attributions. Any claims about reality are
  the model's attributions, not facts.*")` rendered once at top of Section 3,
  before any verbatim text. APPLIED.
  Note: the implemented wording matches the task brief's specified verbatim
  exactly. It diverges slightly from the SME verdict's suggested prose (which
  read "The text below is the model's verbatim response...") but is
  semantically equivalent and satisfies the underlying requirement. The SME
  verdict explicitly deferred final wording to the Reviewer: "Reviewer agent
  can confirm at PR time." ACCEPTED.

- **Note 5** (empty-freelist banner rewrite, the blocking item): Exact
  SME-prescribed text present: "0 items elicited. The pile-sort prompt for
  this informant was constructed with 0 items of input — see Section 2."
  APPLIED.

PASS.

---

## Additional findings (non-blocking)

### OPS-T3 propagation constraints confirmed

- `selected_informant_id` is the canonical session_state key throughout.
  No parallel `selected_run_id` exists in the new code.
- `@st.cache_data` used on all three new loader wrappers, consistent
  with the prior pages.
- `st.stop()` used correctly for both the "no selection" early exit and
  the "ID not found" guard.

### C1–C4 constraints confirmed

- C1: `apps/ops_dashboard/` confirmed absent from `pyproject.toml`
  `[tool.uv.workspace] members`.
- C2: No new pip dependencies.
- C4: Read-only invariant holds — no `open(..., "w"/"a")` in any changed
  file.
- C5: Commit subject "feat(ops): add single-informant detail view (OPS-T4)"
  is 52 characters, well within the 72-character limit.

### Reviewer call: Pydantic silently dropping cost_usd

The Coder noted that `DeclineInterview.model_validate` silently drops
`cost_usd` from legacy on-disk records because `DeclineInterview` has no
`model_config` override — Pydantic v2's default is `extra='ignore'`.

**Ruling: acceptable. No explicit filter required.**

The F2-T13 commit (`c430692`) removed `cost_usd` from the schema. Legacy
JSONL records that still carry the field will load correctly under Pydantic
v2's default behavior. The `load_decline_interviews` docstring explicitly
documents this behavior ("The on-disk format may include extra fields
(e.g. `cost_usd`) that postdate the current schema. Pydantic ignores unknown
fields by default"). This documentation is sufficient; an explicit filter
would be redundant and would need updating if other fields were later removed.

---

## Constraints propagating to OPS-T5 and OPS-T6

These conventions are now established by OPS-T4 and should be followed by
any subsequent page that consumes `lib/detail.py` helpers:

1. **`lib/detail.py` API contract**: `format_freelist`, `build_thinking_trace`,
   `format_pile_sort`, and `find_decline_events` are pure functions. OPS-T5+
   pages that need the same data shapes should import from this module, not
   re-implement the logic.

2. **`selected_informant_id` session_state key**: canonical. Any OPS-T5+
   cross-page navigation that needs to know which informant is selected reads
   from `st.session_state["selected_informant_id"]`.

3. **`DeclineDetail` dataclass**: the join of `DeclineInterview` + manual
   classification + subtype rows is encapsulated in `find_decline_events`.
   If OPS-T5+ needs aggregate views across declines (e.g., counts by
   classification), it should call `find_decline_events` per informant or
   build a separate aggregate helper — not re-implement the join.

4. **`@st.cache_data` on all loaders**: established pattern. Any new loader
   in OPS-T5+ should follow the same caching pattern as
   `_load_decline_interviews`, `_load_manual_classifications`, and
   `_load_safety_subtypes`.

5. **Verbatim disclaimer placement**: the SME-mandated disclaimer pattern
   (one static line at the section heading, before any verbatim content)
   should be replicated for any new section in OPS-T5+ that renders
   model-generated text.

---

*End of verdict.*
