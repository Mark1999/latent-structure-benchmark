# Pre-Release Scan Report

**Run at:** 2026-05-19 16:36:31 UTC
**Run by:** `scripts/prerelease_scan.py`
**Repository state:** `38957d9d33e8cd54efaa79072a219535ddb82046`
**Working tree:** clean

**Overall result:** PASS

---

## Per-check results

### Check 1 — gitleaks full history

**Status:** PASS
**Hits:** 0

### Check 2 — forbidden vocabulary

**Status:** PASS
**Hits:** 0

### Check 3 — leaked internal paths

**Status:** PASS
**Hits:** 0

### Check 4 — real email addresses

**Status:** PASS
**Hits:** 0

### Check 5 — API key patterns

**Status:** PASS
**Hits:** 0

### Check 6 — public URL validity

**Status:** WARN
**Hits:** 2

**Details:**

- data/open_bundle/huggingface_dataset_card.md:85 — Zenodo DOI placeholder not yet minted: `https://doi.org/<TBD-T8-DOI` — expected; replace when T8 mints the DOI.
- data/open_bundle/README.md:62 — Zenodo DOI placeholder not yet minted: `https://doi.org/<TBD-T8-DOI` — expected; replace when T8 mints the DOI.

### Check 7 — .env and credential-file presence

**Status:** PASS
**Hits:** 0

### Check 8 — license-coverage sanity

**Status:** PASS
**Hits:** 0

---

## Summary

| Check | Result | Hits |
|---|---|---|
| 1 gitleaks full history | PASS | 0 |
| 2 forbidden vocabulary | PASS | 0 |
| 3 leaked internal paths | PASS | 0 |
| 4 real email addresses | PASS | 0 |
| 5 API key patterns | PASS | 0 |
| 6 public URL validity | WARN | 2 |
| 7 .env and credential-file presence | PASS | 0 |
| 8 license-coverage sanity | PASS | 0 |

---

## Gate status for T11 (the public flip)

**GATE: PASS** — scan ran clean. T11 (go-public) may proceed provided this report was generated within the 24 hours immediately preceding M12.

This report MUST be re-generated within the 24 hours immediately preceding M12 (the actual flip).
