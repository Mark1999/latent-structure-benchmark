# 2026-07-09 Housekeeping Batch: Reviewer Verdicts

**Reviewer:** LSB Reviewer agent (Sonnet 4.6)
**Date:** 2026-07-09
**Batch:** Two Tier-2 direct-to-master changes reviewed together.
**Authority:** CLAUDE.md §6 binding rules; SECURITY_AND_HARDENING.md §9 Reviewer rules table.

---

## CHANGE 1: apps/dashboard/index.html

**Context:** Applies the 2026-06-16 observatory rename (commit eb9cbef, gate trail
docs/status/2026-06-12-observatory-rename-verdicts.md) to the HTML shell, which was
missed in the original commit. Two lines changed: the `<meta name="description">` and
the `<title>`. The old description also carried an em dash, which is corrected here.

### Verdict: PASS

```
Check 1: No LLM imports in cdb_analyze:  PASS (file does not touch cdb_analyze)
Check 2: Append-only JSONL:               PASS (file does not touch informants.jsonl)
Check 3: No secrets:                      PASS
Check 4: Forbidden vocabulary:            PASS
Check 5: Schema + DATA_DICTIONARY:        N/A
Check 6: New deps sign-off:               N/A
Check 7: Prompt versioning:               N/A
Check 8: Uncertainty in viz:              N/A
Check 9: Prerequisite verdicts:           PASS
```

**Check 4 detail.** New description reads: "The Cognitive Structure Observatory: how
frontier language models organize cultural-domain vocabulary, measured reproducibly."
New title reads: "Cognitive Structure Lab / Observatory". No forbidden vocabulary (no
worldview, believes, thinks applied to models; no within-model terms; no em dash).
The phrase "how frontier language models organize cultural-domain vocabulary" is the
approved form per CLAUDE.md §7 ("How models organize domain vocabulary"). PASS.

**Check 9 detail.** This is a frontend change touching apps/dashboard/. The
observatory rename gate trail (docs/status/2026-06-12-observatory-rename-verdicts.md)
carries both UI/UX PASS-WITH-NOTES and CDA SME PASS-WITH-NOTES from 2026-06-16. The
N7 binding resolution explicitly approved "Cognitive Structure Lab / Observatory" (Option
B NavBar treatment), and NavBar.tsx already uses exactly that string. This change applies
the identical approved treatment to the missed HTML shell surface. Persisted verdicts
carry forward by reference per CLAUDE.md §8 verdict discipline. No new visual decision
is introduced. PASS.

**Incidental fix noted.** The old title line contained an em dash ("Cognitive Structure
Lab: Latent Structure Benchmark"). The replacement uses "/" per the approved N7 brand
treatment. The pre-commit hook would have caught the em dash on any future edit to that
file; this change preempts it.

---

## CHANGE 2: tests/scripts/test_rebaseline_domain_config.py (new file)

**Context:** New test file guarding documented invariants of scripts/rebaseline_corpus.py
DOMAIN_CONFIG and DOMAIN_ORDER. Six tests, all passing per task context. No real API
calls. Written during June rebaseline work; never committed.

### Verdict: PASS

```
Check 1: No LLM imports in cdb_analyze:  PASS (file does not touch cdb_analyze)
Check 2: Append-only JSONL:               PASS
Check 3: No secrets:                      PASS
Check 4: Forbidden vocabulary:            PASS
Check 5: Schema + DATA_DICTIONARY:        N/A
Check 6: New deps sign-off:               N/A (no new dependencies; imports
                                               scripts.rebaseline_corpus only)
Check 7: Prompt versioning:               N/A
Check 8: Uncertainty in viz:              N/A
Check 9: Prerequisite verdicts:           PASS (Tier-2 test addition; not frontend,
                                               not methodology; no gate required)
```

**Check 3 detail.** No API keys, credentials, or webhook URLs. PASS.

**Check 4 detail.** Docstrings and comments contain no forbidden vocabulary. PASS.

**DOMAIN_CONFIG alignment verified.** Reviewer read scripts/rebaseline_corpus.py
lines 83-100 directly and confirmed:
- `DOMAIN_CONFIG["family"]["similarity_collection_mode"]` is `None` (test 2 correct)
- `DOMAIN_CONFIG["holidays"]["similarity_collection_mode"]` is `None` (test 3 correct)
- `DOMAIN_CONFIG["food"]["similarity_collection_mode"]` is `"single_pass"` (test 1 correct)
- All three entries have keys `prior_version`, `new_version`, `similarity_collection_mode`
  (test 4 correct)
- `DOMAIN_ORDER` is `["family", "holidays", "food"]` (test 5 correct)
- All DOMAIN_ORDER entries are present in DOMAIN_CONFIG (test 6 correct)

All six test assertions match the current live values in the script. Tests are not
asserting stale values.

**Rule 9 (real API calls) confirmed clean.** The file header states "No real API calls.
No I/O. Pure import + structure inspection." The six test bodies import only
`scripts.rebaseline_corpus` module-level constants; no network calls, no subprocess
calls, no provider SDKs referenced. PASS.

---

## Summary

Both changes PASS. Coder may commit both directly to master per the direct-to-master
workflow (CLAUDE.md §8). No corrections required.
