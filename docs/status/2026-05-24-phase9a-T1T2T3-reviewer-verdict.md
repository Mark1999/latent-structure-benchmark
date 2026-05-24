# Reviewer Verdict: Phase 9a T1/T2/T3 — Term-Level Analysis Pipeline

**Date:** 2026-05-24
**Reviewer:** LSB Reviewer agent
**Task:** Phase 9a T1 (pooled co-occurrence), T2 (term MDS), T3 (term AHC)
**Gate prerequisite:** CDA SME PASS-WITH-NOTES — `docs/status/2026-05-24-phase9a-cda-sme-verdict.md`

---

## REVIEWER VERDICT: PASS

---

## Check Results

| Check | Result |
|---|---|
| Check 1 — No LLM imports in cdb_analyze | PASS |
| Check 2 — Append-only JSONL | PASS |
| Check 3 — No secrets | PASS |
| Check 4 — Forbidden vocabulary | PASS |
| Check 5 — Schema + DATA_DICTIONARY | PASS |
| Check 6 — New deps sign-off | N/A |
| Check 7 — Prompt versioning | N/A |
| Check 8 — Uncertainty in viz | N/A |
| Check 9 — Prerequisite verdicts | PASS |

---

## Detailed Findings

### Check 1 — No LLM imports in cdb_analyze: PASS

Grep of `packages/cdb_analyze/` for `import anthropic`, `import openai`, `from anthropic`,
`from openai`, `InferenceClient`, `google.generativeai` found two matches — both in
`packages/cdb_analyze/cdb_analyze/__init__.py` lines 12–13, which are comment text in the
NO-LLM-CALLS policy notice, not import statements. No actual LLM client imports in
`cooccurrence.py`, `cluster.py`, or `pipeline.py`.

### Check 2 — Append-only JSONL: PASS

`git diff HEAD~1 HEAD -- data/raw/informants.jsonl` returned no output. The JSONL file
was not touched by this changeset.

### Check 3 — No secrets: PASS

All changed files (`cooccurrence.py`, `cluster.py`, `pipeline.py`, `schemas.py`,
`test_term_cooccurrence_and_cluster.py`, `DATA_DICTIONARY.md`) scanned for API key
patterns, Slack webhook URLs, and credential-shaped strings. Two matches in
`DATA_DICTIONARY.md` lines 1221–1222 are within the §12.3 sanitization policy
documentation section — they describe redaction pattern strings, not actual
credentials. No real keys found.

Note: `test_term_cooccurrence_and_cluster.py` uses `provider="anthropic"` and
`collection_method="anthropic_api"` as schema field VALUES (string literals for
`InformantRecord` fixture construction), not as imports of the Anthropic SDK. This
is correct fixture usage — not a credential or an LLM import.

### Check 4 — Forbidden vocabulary: PASS

Scanned all changed `.py` and `.md` files for:
- `worldview`, `believes`, `thinks` (applied to models)
- `within-model consensus`, `within-model cultural consensus`
- `within-model eigenratio`, `within-model CCM`
- `publishable`
- `How models see`
- `Model X believes`, `Model X thinks of`

No matches found in any user-facing or documentation context. The `__init__.py`
comment text (which contains the forbidden SDK names as a policy list) was
pre-existing and is not user-facing model description text.

### Check 5 — Schema + DATA_DICTIONARY: PASS

`packages/cdb_core/cdb_core/schemas.py` changes:
- `DomainResult` gains 5 new optional fields: `term_mds_coordinates`, `term_mds_items`,
  `term_cluster_linkage`, `term_cluster_assignments`, `term_cluster_labels`
- `WithinModelResult.mds_within_model` type widened from implicit to `list[Any]` with
  explicit docstring

`docs/DATA_DICTIONARY.md` bumped to v0.1.19 (from v0.1.18) with:
- §2 table updated with all 5 new `DomainResult` fields
- New §2.4 — Pooled cross-model term co-occurrence matrix algorithm (M1 binding)
- New §2.5 — Term-level AHC algorithm (M2/M3 binding, Borgatti 1994 citation)
- §2.1 `WithinModelResult` table updated for `mds_within_model` field semantics
- Changelog entry at top documenting all additions, SME ruling references, and
  Architect sign-off reference

Co-update is present in the same working-tree changeset. PASS.

### Check 6 — New deps sign-off: N/A

No changes to `pyproject.toml` in any package. `cluster.py` and `cooccurrence.py`
use only `scipy`, `numpy`, `cdb_core` — all pre-existing approved dependencies
per `SECURITY_AND_HARDENING.md` §4.3.

### Check 7 — Prompt versioning: N/A

No changes to `packages/cdb_collect/cdb_collect/prompts/` in this changeset.

### Check 8 — Uncertainty in viz: N/A

This is a non-frontend PR. No new visualization components in `apps/dashboard/`.

### Check 9 — Prerequisite verdicts: PASS

CDA SME verdict present: `docs/status/2026-05-24-phase9a-cda-sme-verdict.md`
Verdict: PASS-WITH-NOTES. All binding M-notes verified applied:

- **M1** (pooled matrix = mean of per-model matrices, denominator always M,
  absence=0.0): Verified in `cooccurrence.py` lines 182–206. `M = len(per_model_matrices)`
  is set once; the divide-by-M loop at line 203–206 runs over all cells. Items absent
  from a model's vocabulary contribute 0.0 to the numerator by initialization (line 187
  initializes to 0.0; absent items produce no addition per the else-branch comment).
  Docstring explicitly states the M1 contract.

- **M2** (AHC uses `method="average"`, docstring cites Borgatti 1994): Verified in
  `cluster.py` line 155 (`Z = linkage(condensed, method="average")`). Docstring at lines
  109–121 cites Borgatti 1994 and Spencer et al. 2016, and explicitly documents the
  Ward rejection rationale ("equal-cluster-size assumption does not match the empirical
  structure of pile-sort co-occurrence data").

- **M3** (distance = 1-cooccurrence, diagonal 0.0 after subtraction): Verified in
  `cluster.py` lines 145–148. `dissimilarity = 1.0 - cooccur`, then
  `np.fill_diagonal(dissimilarity, 0.0)` for floating-point safety.

- **F3** (per-model item MDS is Register 1, `mds_within_model` populated):
  Verified in `pipeline.py` lines 410–421 (per-model MDS computation) and lines 683–688
  (model_copy update on WithinModelResult). `schemas.py` docstring for `mds_within_model`
  at lines 346–354 correctly identifies this as Register 1 with `underestimates_uncertainty`
  annotation.

This PR does not implement M4, M4a, M5, M5a, M6, M7, M8 (those are for T4, T5, T7,
T9, T10 respectively — out of scope for T1/T2/T3). No unfulfilled binding notes
within T1/T2/T3 scope.

No UI/UX verdict required — this is not a frontend PR.

---

## Specific Checks Requested

All five specific checks in the review request verified:

1. **No LLM imports in cdb_analyze**: CONFIRMED — see Check 1 above.
2. **Schema changes have DATA_DICTIONARY.md co-update**: CONFIRMED — §2.4, §2.5, §2.1
   update, field table rows for all 5 new fields.
3. **M1 pooling is equal-weight-per-model**: CONFIRMED — `cooccurrence.py` line 182
   sets `M = len(per_model_matrices)`; divide-by-M at lines 203–206 uses this M
   unconditionally. Items absent from a model initialize to 0.0 (not NaN, not excluded).
4. **M2 linkage is average**: CONFIRMED — `cluster.py` line 155: `method="average"`.
5. **M3 distance is 1-cooccurrence**: CONFIRMED — `cluster.py` line 146:
   `dissimilarity = 1.0 - cooccur`.
6. **No edits to data/raw/informants.jsonl**: CONFIRMED — no diff.
7. **No forbidden vocabulary**: CONFIRMED — no matches in user-facing or doc context.
8. **No real API calls in tests**: CONFIRMED — `tests/unit/test_term_cooccurrence_and_cluster.py`
   uses only in-memory `InformantRecord` fixtures; `provider="anthropic"` is a schema
   field value, not an SDK import. No HTTP calls.
9. **Docstring cites Borgatti 1994 and Ward rejection**: CONFIRMED — `cluster.py`
   lines 109–121 contain the required docstring text verbatim per CDA SME M2.

---

*Coder may merge. No required actions.*
