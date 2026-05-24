# Reviewer Verdict: Phase 9a T5-mini — Centroid Pile Data Pipeline

**Date:** 2026-05-24
**Reviewer:** LSB Reviewer agent
**Commit reviewed:** working tree changes against HEAD (d59270c)
**Task:** Phase 9a T5-minimal — CentroidPileData schema + `_build_centroid_piles()` pipeline helper

---

## REVIEWER VERDICT: PASS

| Check | Result |
|---|---|
| Check 1 — No LLM imports in cdb_analyze | PASS |
| Check 2 — Append-only JSONL | PASS |
| Check 3 — No secrets | PASS |
| Check 4 — Forbidden vocabulary | PASS |
| Check 5 — Schema + DATA_DICTIONARY co-update | PASS |
| Check 6 — New deps sign-off | N/A |
| Check 7 — Prompt versioning | N/A |
| Check 8 — Uncertainty in viz | N/A |
| Check 9 — Prerequisite verdicts | PASS |

---

## Check-by-Check Detail

### Check 1 — No LLM imports in cdb_analyze: PASS

`grep` for `anthropic`, `openai`, `from anthropic`, `from openai`, `InferenceClient`, `google.generativeai` across `packages/cdb_analyze/` produces two matches in `cdb_analyze/__init__.py` lines 12–13. Both are inside the module-level docstring comment block that *prohibits* LLM imports — not actual import statements. `pipeline.py` contains no LLM client imports. The new `_build_centroid_piles()` helper uses only `cdb_core`, `cdb_analyze`, and standard library. PASS.

### Check 2 — Append-only JSONL: PASS

`git diff HEAD -- data/raw/informants.jsonl` produces zero output. The file is unmodified. PASS.

### Check 3 — No secrets: PASS

All changed files (`pipeline.py`, `schemas.py`, `__init__.py`, `DATA_DICTIONARY.md`, `test_centroid_piles.py`) were scanned for API key patterns, webhook URLs, and credential-shaped strings. No matches. The one match in `DATA_DICTIONARY.md` (line 1189) is a description of the gitleaks redaction patterns inside the sanitization documentation — not a credential. `.env.example` has `ANTHROPIC_API_KEY=sk-ant-...` (ellipsis placeholder per the allowed pattern). PASS.

### Check 4 — Forbidden vocabulary: PASS

All changed files scanned for `worldview`, `believes`, `thinks` (applied to models), `How models see`, `within-model consensus`, `within-model cultural consensus`, `within-model eigenratio`, `within-model CCM`, `publishable`. Zero matches. PASS.

### Check 5 — Schema + DATA_DICTIONARY co-update: PASS

`packages/cdb_core/cdb_core/schemas.py` adds the new `CentroidPileData` Pydantic model and the `DomainResult.centroid_piles: dict[str, CentroidPileData] = {}` field. `docs/DATA_DICTIONARY.md` is co-updated in the same changeset:
- Changelog entry `v0.1.18` added at top of changelog
- `centroid_piles` field row added to §2 (`DomainResult`) table
- New §2.3 (`CentroidPileData`) with full field table and `term_stability` computation rule

Note: `InformantRecord` and `GroundingRef` are not changed; the stricter R7 rule (those two specific schemas require DATA_DICTIONARY co-update) does not fire. The general rule covering all schema documentation is satisfied. PASS.

**Minor docstring cross-reference note (non-blocking):** The `CentroidPileData` class docstring in `schemas.py` (line 295) cites `docs/DATA_DICTIONARY.md §2.2 (CentroidPileData)` but the actual section added is `§2.3`. The `DomainResult.centroid_piles` field comment (line 443) correctly says `§2.3`. This is an internal cross-reference inconsistency; the section exists and documents the field correctly. Recommend fixing in a follow-up commit.

### Check 6 — New deps sign-off: N/A

No changes to `pyproject.toml`, `uv.lock`, `apps/dashboard/package.json`, or `apps/dashboard/package-lock.json`. The implementation comment in `pipeline.py` explicitly states "No LLM calls, no new dependencies — pure data access." N/A.

### Check 7 — Prompt versioning: N/A

No changes to `packages/cdb_collect/prompts/`. N/A.

### Check 8 — Uncertainty in viz: N/A

This PR is a backend pipeline task. No new dashboard visualizations are introduced. N/A.

### Check 9 — Prerequisite verdicts: PASS

- **CDA SME:** PASS-WITH-NOTES at `docs/status/2026-05-24-phase9a-cda-sme-verdict.md`. The applicable notes for T5-mini are:
  - **F5** ("same pile" = set equality of co-occurring items, not pile index): Applied. The `_build_centroid_piles()` implementation uses `frozenset` equality on co-occurring item sets and documents this explicitly. `DATA_DICTIONARY.md §2.3` specifies this computation rule verbatim.
  - **M7** (pile comparison framing — all models treated symmetrically): M7 is a frontend rendering constraint for the T9 PileComparison component. This T5-mini PR is backend-only; M7 does not bind this changeset. M7 must be addressed when T9 frontend component is reviewed.
- **UI/UX:** Not required for a non-frontend PR.
- **Architect sign-off on schema change:** Present at `docs/status/2026-05-24-phase9a-viz-gap-kickoff.md` T9 schema block (lines 211–228, 341–349, 402–403). PASS.

---

## Summary

All nine checks pass. The T5-mini implementation is clean:
- `CentroidPileData` schema is additive, optional, non-breaking
- `_build_centroid_piles()` uses pure Python set operations with no LLM calls
- Term stability computation correctly implements set equality of co-occurring items per CDA SME ruling F5
- 17 tests cover stability computation, edge cases, and pipeline integration with synthetic fixtures only
- DATA_DICTIONARY.md §2.3 is a complete and accurate companion entry

**One non-blocking recommendation:** Fix the `§2.2` cross-reference in the `CentroidPileData` docstring in `schemas.py` to read `§2.3`.

Coder may merge.

---

*End of verdict. Only Mark can override a FAIL verdict.*
