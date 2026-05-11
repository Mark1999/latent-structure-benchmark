# Reviewer Verdict — Phase 5 T12 Security Follow-up

**Filed:** 2026-05-11
**Reviewer:** Reviewer agent (Sonnet)
**Commit reviewed:** `f7ecd46`
**Closes:** PASS-WITH-NOTES condition from `docs/status/2026-05-11-phase5-T12-reviewer-verdict.md` §"Required follow-up (non-blocking for merge, required before T13)"

---

## REVIEWER VERDICT: PASS

```
Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         N/A
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A
Check 6 — New deps sign-off:         N/A
Check 7 — Prompt versioning:         N/A
Check 8 — Uncertainty in viz:        N/A
Check 9 — Prerequisite verdicts:     PASS
```

---

## Confirmation of the three originally required follow-ups

The T12 Reviewer verdict (`docs/status/2026-05-11-phase5-T12-reviewer-verdict.md` §"Required follow-up") imposed three mandatory corrections before T13 could proceed. All three are present and correct in `f7ecd46`.

**Follow-up 1 — Remove `X-Frame-Options: DENY` from `apps/dashboard/public/_headers`.**
Confirmed. `grep -n "X-Frame-Options" apps/dashboard/public/_headers` returns empty (exit 1). The diff for this file shows exactly one deletion: the `X-Frame-Options: DENY` line. The CSP `frame-ancestors *` directive and all other headers (`X-Content-Type-Options`, `Referrer-Policy`, `Strict-Transport-Security`, `Permissions-Policy`) are unchanged.

**Follow-up 2 — Add `ARCHITECTURE.md` §7 entry #25 recording the `frame-ancestors *` architectural decision.**
Confirmed. `grep -n "^| 25 |" ARCHITECTURE.md` returns a match at line 1515. Entry #25 documents the `frame-ancestors 'none'` → `frame-ancestors *` relaxation with the full security justification: no authentication, no mutation endpoints, no user-supplied state beyond client-validated URL params, and CC-BY 4.0 content licensing consistent with embedding. It cross-references `SECURITY_AND_HARDENING.md` §3.1 and §3.2. No entries #1–#24 were modified (diff scan returns empty for those rows).

**Follow-up 3 — Update `SECURITY_AND_HARDENING.md` §3.1 (frame-ancestors rationale) and §3.2 (X-Frame-Options block and table row).**
Confirmed. `grep -nE "frame-ancestors.*\*" SECURITY_AND_HARDENING.md` returns two matches — line 88 in the code block and line 105 in the directive table — both correctly updated from `'none'` to `*`. `grep -nE "X-Frame-Options" SECURITY_AND_HARDENING.md` returns empty: the `X-Frame-Options: DENY` line in the `§3.2` code block and its corresponding table row have both been removed.

---

## Verification check table

| # | Verification | Command / Result |
|---|---|---|
| V1 | X-Frame-Options gone from `_headers` | `grep -n "X-Frame-Options" apps/dashboard/public/_headers` → empty (exit 1). PASS. |
| V2 | `frame-ancestors *` present in `_headers` | Match at line 9. PASS. |
| V3 | Only X-Frame-Options line removed; CSP directive unchanged | Diff shows exactly one deletion (`-  X-Frame-Options: DENY`). No other change to the `_headers` file. PASS. |
| V4 | `ARCHITECTURE.md` §7 entry #25 present | Match at line 1515. PASS. |
| V5 | `ARCHITECTURE.md` entries #1–#24 untouched | Diff scan for removed `^-\| (1..24) ` rows returns empty. PASS. |
| V6 | `SECURITY_AND_HARDENING.md` has `frame-ancestors *` | Two matches (code block line 88, table row line 105). PASS. |
| V7 | `SECURITY_AND_HARDENING.md` X-Frame-Options block + table row removed | `grep -nE "X-Frame-Options" SECURITY_AND_HARDENING.md` → empty. PASS. |
| V8a | `HOSTING_AND_DEV_OPS.md` X-Frame-Options gone | `grep -n "X-Frame-Options" HOSTING_AND_DEV_OPS.md` → empty. PASS. |
| V8b | `HOSTING_AND_DEV_OPS.md` Referrer-Policy present | Match at line 70 in updated verification grep. PASS. |
| V9 | No code / test / data changes | `git diff --stat f7ecd46^..f7ecd46 \| grep -E "\.(ts\|tsx\|py\|jsonl\|json\|css)$"` → empty. PASS. |
| V10 | No HARDWARE.md committed | `git diff f7ecd46^..f7ecd46 -- HARDWARE.md` → empty. PASS. |
| V11 | Forbidden vocabulary in added text | `git show f7ecd46 \| grep -iE "\b(believes\|thinks\|worldview\|recognizes\|interprets\|perceives\|comprehends)\b"` → empty. PASS. |
| V12 | No spend-cap framing | `git show f7ecd46 \| grep -iE "CDB_MAX_SPEND\|spend cap\|spend gate\|cost cap"` → empty. PASS. |

---

## Nine binding checks — detail

**Check 1 — No LLM imports in `cdb_analyze/`:** The commit touches only `ARCHITECTURE.md`, `HOSTING_AND_DEV_OPS.md`, `SECURITY_AND_HARDENING.md`, and `apps/dashboard/public/_headers`. No Python files modified. The standing grep against `packages/cdb_analyze/` confirms only the prohibition comment in `cdb_analyze/__init__.py` (comment text, not executable imports). PASS.

**Check 2 — Append-only JSONL:** `git diff f7ecd46^..f7ecd46 -- data/raw/informants.jsonl` returns empty. N/A.

**Check 3 — No secrets:** Grep for credential patterns (`sk-ant`, `sk-or-v1`, `hf_`, `AKIA`, `hooks.slack.com`, `LSB_ALERTS_WEBHOOK_URL`, `LSB_CDA_SME_WEBHOOK_URL`, `LSB_UI_UX_WEBHOOK_URL`, `password`, `token`, `secret`) across all four changed files returned empty. PASS.

**Check 4 — Forbidden vocabulary:** Grep for all CLAUDE.md §7 and ARCHITECTURE.md §1.5.4 terms (`believes`, `thinks`, `worldview`, `cultural bias`, `within-model consensus`, `within-model cultural consensus`, `within-model eigenratio`, `within-model CCM`, `publishable`, `recognizes`, `interprets`, `perceives`, `comprehends`) in added lines of `f7ecd46` returned empty. The ARCHITECTURE.md §7 entry #25 describes the dashboard in architectural terms ("no authentication," "static site," "no mutation endpoints") and references documents and commit hashes — no model-cognitive language. PASS.

**Check 5 — Schema + DATA_DICTIONARY:** `git diff f7ecd46^..f7ecd46 -- packages/cdb_core/schemas.py docs/DATA_DICTIONARY.md` returns empty. No schema changes. N/A.

**Check 6 — New deps sign-off:** `git diff f7ecd46^..f7ecd46 -- pyproject.toml apps/dashboard/package.json` returns empty. No new dependencies. N/A.

**Check 7 — Prompt versioning:** `git diff f7ecd46^..f7ecd46 -- packages/cdb_collect/prompts/` returns empty. No prompt template changes. N/A.

**Check 8 — Uncertainty in viz:** Commit is documentation-only; no new visualization introduced. N/A.

**Check 9 — Prerequisite verdicts:** This commit is a documentation-alignment follow-up to the T12 PASS-WITH-NOTES condition, not a new frontend feature or methodology change. The governing prerequisite verdicts are those already accepted for T12: CDA SME PASS-WITH-NOTES (`docs/status/2026-05-09-phase5-cda-sme-plan-verdict.md`) and UI/UX PASS-WITH-NOTES (`docs/status/2026-05-11-phase5-T12-uiux-verdict.md`). No new gates are triggered by a documentation-only security-header correction. Commit body references `docs/status/2026-05-11-phase5-T12-reviewer-verdict.md`. PASS.

---

## Build and lint impact assessment

No code changes were made. The dashboard build (`npm run build`) succeeds cleanly:

```
dist/assets/index-6i_elQEs.js  244.25 kB │ gzip: 75.20 kB
built in 1.95s
```

The build output's `dist/_headers` file contains `frame-ancestors *` (confirmed at line 9) and does not contain `X-Frame-Options` (grep returns empty). The build output is internally consistent with the source `_headers` change.

No `.py`, `.ts`, `.tsx`, `.json`, or `.css` files were modified; Python linting, type checking, and test suite results are unaffected.

---

## T13 unblocked

All three conditions from the T12 PASS-WITH-NOTES verdict have been satisfied in `f7ecd46`. The `_headers` file, `ARCHITECTURE.md`, `SECURITY_AND_HARDENING.md`, and `HOSTING_AND_DEV_OPS.md` are now internally consistent: the embed feature is documented, the security justification is canonically recorded in §7 entry #25, and no contradictory legacy header remains. T13 may proceed.

---

*End of Phase 5 T12 follow-up Reviewer verdict. PASS. T13 unblocked.*
