# Architect Sign-off — published `provenance.json` artifact (PROMOTE-1 / T-C)

**Date:** 2026-05-30
**Authority:** Architect sign-off for a published-bundle-contract change (new published artifact). Mark chose mechanism A, single canonical `provenance.json` (2026-05-30).

## Approved
Add a new published artifact **`apps/dashboard/public/data/provenance.json`** carrying the analysis toolchain provenance the dashboard surfaces (footer T-D + the methodology-page link from T-B). Source of truth = `out/rebaseline/baseline_manifest.json`.

**Required fields** (copy from the manifest):
- `numpy_version` ("2.4.4"), `scipy_version` ("1.17.1"), `python_version`
- `git_sha`, `generated_at_utc`
- `domains`: per-domain `{ version, model_count, sha256, guard }` (integrity + audit)

**Conditions:**
- It is a **read-only published artifact**; the dashboard reads it, nothing writes it at runtime.
- A matching entry MUST be added to `docs/DATA_DICTIONARY.md` (published-artifacts / dashboard-data section) in the SAME commit as the artifact (R7-spirit for published-bundle changes).
- No change to `cdb_core/schemas.py` (so Reviewer R7's exact trigger does not fire; the dictionary co-update is required by this sign-off).
- The footer (T-D) and methodology link (T-B) read from this single file — do not duplicate the version strings elsewhere (mechanism A: one source).

## Not covered
- Whether to also publish `provenance.json` into `data/results/` (analysis side) — not required for the dashboard; out of scope unless the open-data bundle wants it (defer).

*Referenced by the T-C commit body.*
