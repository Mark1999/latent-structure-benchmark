# Architect Sign-off — NumPy/SciPy pin + dashboard test deps

**Date:** 2026-05-29
**Scope:** Dependency changes for the reproducibility/cleanup bundle (plan: `docs/status/2026-05-29-*` Architect decomposition, T2 + T7)
**Authority:** Architect sign-off per CLAUDE.md §6 rule (no new/changed dependency without Architect sign-off) + §11 done-checklist. Mark approved the specifics on 2026-05-29.

## Signed off

### T2 — pin numpy + scipy (in `packages/cdb_analyze/pyproject.toml`)
- Change `numpy>=1.26.0` → `numpy==2.4.4`, `scipy>=1.12.0` → `scipy==1.17.1` (exact pins), regenerate the workspace lockfile.
- **Mark's decision (2026-05-29):** pin to the **currently installed** versions (2.4.4 / 1.17.1) and re-baseline the corpus forward to them. The versions that generated the original published 0.3 numbers are not recoverable (no prior pin existed); pinning current + re-baselining is the pragmatic path to a reproducible baseline.
- Rationale: the published 0.3 numerics could not be bit-reproduced in the current environment (MDS coords, consensus_score, romney_eigenratio drifted at the 3rd–4th decimal) — an unpinned upper bound let a newer numpy/scipy in. Exact pins close the drift.
- This pin itself does not change published numbers; the re-baseline (T3/T4) does, and that is separately CDA-SME-gated.

### T7 — dashboard test dependencies
- Approve adding `@testing-library/react` and `@testing-library/jest-dom` as `apps/dashboard` devDependencies, to seed the currently-empty vitest suite.
- Standard, conventional React-testing libraries; needed to make the frontend Tester gate functional.

## Not covered here
- The re-baseline (T3/T4) requires a **CDA SME** verdict (methodology output change) before any Coder — routed separately.
- The footer version surface (T5) sources versions from a **published manifest field** (Mark's choice, mechanism A) — that manifest is a T3 deliverable; if it introduces a new published-bundle field, document it in `docs/DATA_DICTIONARY.md` in the same commit.

*Referenced by the T2 and T7 commit bodies.*
