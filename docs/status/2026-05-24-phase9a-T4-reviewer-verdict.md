# LSB Reviewer Verdict: Phase 9a T4 — Term Bootstrap Uncertainty

**Date:** 2026-05-24
**Reviewer:** LSB Reviewer agent
**Task:** Phase 9a T4 — term-level bootstrap: per-term confidence ellipses + dendrogram branch stability
**Prerequisite gate:** CDA SME PASS-WITH-NOTES (`docs/status/2026-05-24-phase9a-cda-sme-verdict.md`)

---

## REVIEWER VERDICT: PASS

```
Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         PASS
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  PASS
Check 6 — New deps sign-off:         N/A
Check 7 — Prompt versioning:         N/A
Check 8 — Uncertainty in viz:        N/A
Check 9 — Prerequisite verdicts:     PASS
```

---

## Check-by-check notes

**Check 1 — No LLM imports in cdb_analyze/:**
The grep of `packages/cdb_analyze/` for LLM client imports (`anthropic`, `openai`,
`google.generativeai`, `InferenceClient`) returned only one hit:
`cdb_analyze/__init__.py` line 13, which is a comment in the module docstring
listing forbidden libraries. No actual import statements. PASS.

**Check 2 — Append-only JSONL:**
`git diff HEAD -- data/raw/informants.jsonl` returns empty — the file was not
touched by this PR. PASS.

**Check 3 — No secrets:**
Scanned all changed lines in bootstrap.py, schemas.py, pipeline.py,
DATA_DICTIONARY.md, and test_bootstrap.py for API key patterns, webhook URLs,
and credential-shaped strings. No matches. PASS.

**Check 4 — Forbidden vocabulary:**
Full grep across all five changed files for the CLAUDE.md §7 and
ARCHITECTURE.md §1.5.4 forbidden phrase table (worldview, believes, thinks
applied to models, cultural bias, what the model understands, within-model
consensus, within-model cultural consensus, within-model eigenratio,
within-model CCM, publishable). No matches. The phrase "between-model
structural variance only" used throughout is the correct approved form. PASS.

**Check 5 — Schema + DATA_DICTIONARY co-update:**
`packages/cdb_core/cdb_core/schemas.py` gains two new optional fields on
`DomainResult` (`term_mds_uncertainty: dict[str, Any] = {}` and
`term_cluster_bp_values: list[float] = []`). `docs/DATA_DICTIONARY.md` is
updated in the same working tree: changelog gains v0.1.20 entry, §2 table gains
both new fields, and §2.6 is newly added with full algorithm specification for
both fields. CDA SME M4/M4a/M5/M5a/F4 notes are all reflected. PASS.

Note: the changed schemas do not touch `InformantRecord` or `GroundingRef`,
but `DomainResult` is documented in DATA_DICTIONARY.md and the co-update
requirement in CLAUDE.md rule 6 + SECURITY_AND_HARDENING.md R7 covers schema
changes broadly. The co-update is present. PASS.

**Check 6 — New deps sign-off:** N/A. No changes to `pyproject.toml` or
`apps/dashboard/package.json`. The bootstrap implementation uses only
pre-approved dependencies: `numpy`, `scipy` (linkage, procrustes, squareform),
and `cdb_core`/`cdb_analyze` internal imports.

**Check 7 — Prompt versioning:** N/A. No changes to any prompt template
under `packages/cdb_collect/prompts/`.

**Check 8 — Uncertainty in viz:** N/A. No frontend changes in this PR.
The PR adds the data-layer outputs that will serve uncertainty to future
frontend components; no new visualization is introduced here.

**Check 9 — Prerequisite verdicts:**
CDA SME PASS-WITH-NOTES present at
`docs/status/2026-05-24-phase9a-cda-sme-verdict.md`. This is a non-frontend,
methodology-touching PR. All binding notes (M4, M4a, M5, M5a, F4) are applied:

- M4 (resample models with replacement): confirmed in `bootstrap_term_mds_ellipses()` —
  `sampled_ids = [model_ids[i] for i in rng.integers(0, M, size=M)]`. Resampling
  unit is models, not runs. Pre-computed per-model matrices used throughout. APPLIED.

- M4a (CIs reflect between-model variance only, must be annotated): docstring at
  bootstrap.py line 266–269 and DATA_DICTIONARY.md §2.6 both carry the verbatim
  required statement. APPLIED.

- M5 (simple BP, not multiscale AU): `bootstrap_branch_stability()` computes
  `float(c) / n_bootstrap` — a simple proportion. No multiscale extrapolation.
  Set equality used for bipartition comparison (`if ref_bp in boot_bipartitions`).
  APPLIED.

- M5a (label as "bootstrap support (%)" not "AU p-value"): schema docstring,
  DATA_DICTIONARY.md §2.6 display contract, and pipeline.py comment all specify
  "bootstrap support (%)". APPLIED.

- F4 (B=200 acceptable): pipeline.py wires `n_bootstrap=200` for both
  `bootstrap_term_mds_ellipses()` and `bootstrap_branch_stability()`. APPLIED.

No prerequisite notes left unaddressed. PASS.

---

## Additional observations (non-blocking)

The `_pool_resampled_matrices()` helper correctly implements the CDA SME M1
equal-weight-per-model denominator (always M, not number of models that
produced the item), consistent with the existing `build_pooled_cooccurrence_matrix()`
contract. This is correct.

The bipartition canonical form (smaller of the two subtrees stored as the
frozenset) correctly handles the symmetry requirement stated in M5: "exact
bipartition" means set equality of the smaller partition.

The `test_branch_stability_perfect_stability()` test provides meaningful
behavioral coverage of the M5 implementation — when both models produce
identical pile structures, all resamples reproduce the same tree and all BP
values are 1.0. This directly verifies the M5 counting logic.

The degenerate zero-size ellipse fallback (fewer than 2 bootstrap iterations
contributed coordinates for an item) is documented in DATA_DICTIONARY.md §2.6
and handled safely in the implementation. The `n_bootstrap` field on the emitted
`BootstrapEllipse` correctly reflects the actual count, not B.

---

*Coder may merge. No corrections required.*
