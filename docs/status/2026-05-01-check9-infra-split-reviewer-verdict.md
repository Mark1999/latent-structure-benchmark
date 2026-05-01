# Reviewer Verdict — Check 9 (backup freshness) infrastructure split

**Task ID:** F2-T11
**Commit reviewed:** `36d180e` (amended from `0b310e7`)
**Commit message:** `fix(scripts): split check 9 (infra) out of per-record QA battery (task #F2-T11)`
**Date:** 2026-05-01
**Reviewer:** LSB Reviewer agent
**Verdict:** **PASS**

---

## Amendment note

This is a re-review of the amended commit `36d180e`. The prior verdict on `0b310e7` was **FAIL** on a single issue: `ARCHITECTURE.md` §4.1.6 stated `(currently 24h)` while `scripts/qa_check.py:62` defined `MAX_BACKUP_AGE_HOURS = 48`. The Coder corrected line 784 of `ARCHITECTURE.md` to read `(currently 48h)`. No other files changed. The prior FAIL verdict is preserved as a reviewer history block at the bottom of this file.

**Scope of re-review:** All nine binding checks re-run against `36d180e`. Checks 1–4 and 9 required active re-verification; Checks 5–8 remain N/A (no schema, dependency, prompt, or frontend changes). The SME mandatory notes audit carries over from the prior review — none of the seven notes could have been affected by a one-word change in `ARCHITECTURE.md`.

---

## Verdict summary

```
REVIEWER VERDICT: PASS

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

## Check-by-check findings

### Check 1 — No LLM imports in cdb_analyze/ (PASS)

`grep -r "import anthropic\|import openai\|from anthropic\|from openai\|InferenceClient\|google.generativeai" packages/cdb_analyze/` returns two comment lines only (inside `/opt/lsb-agent/packages/cdb_analyze/cdb_analyze/__init__.py` lines 12–13, which document the prohibition). No actual import statements. The amended commit does not touch `cdb_analyze/`.

### Check 2 — Append-only JSONL (PASS)

`data/raw/informants.jsonl` does not appear in the `36d180e` diff. The word "informants.jsonl" appears only in the ARCHITECTURE.md prose describing the open-data bundle. Zero edits to existing lines.

### Check 3 — No secrets (PASS)

All changed files scanned. No API keys, no real Slack webhook URLs, no credentials. The env var name `LSB_ALERTS_WEBHOOK_URL` appears only as a lookup key in `os.environ.get(...)`, which is the correct pattern. The only change in the amended commit (`ARCHITECTURE.md` line 784: `24h` → `48h`) contains no credential content.

### Check 4 — Forbidden vocabulary (PASS)

The amended line reads: `| 9 | Backup-log freshness | \`mtime(logs/backup.log)\` within \`MAX_BACKUP_AGE_HOURS\` (currently 48h); file must exist | Operator backup process is stale or absent — operational, not record-level |`. No forbidden vocabulary from CLAUDE.md §7 or ARCHITECTURE.md §1.5.4. The change is a threshold value correction, not prose about model behavior.

Full sweep of all seven changed files: no matches for `worldview`, `believes`, `thinks` (applied to models), `how models see the world`, `cultural bias` (standalone), `what the model understands`, `within-model consensus`, `within-model cultural`, `within-model eigenratio`, `within-model CCM`, `publishable`. Clean.

### Check 5 — Schema + DATA_DICTIONARY (N/A)

`cdb_core/schemas.py` is not in the diff. No schema change.

### Check 6 — New dependencies (N/A)

`pyproject.toml`, `uv.lock`, `apps/dashboard/package.json`, and `apps/dashboard/package-lock.json` are not in the diff. No new dependencies.

### Check 7 — Prompt versioning (N/A)

No files under `packages/cdb_collect/prompts/` in the diff.

### Check 8 — Uncertainty in visualizations (N/A)

No frontend surface area in this commit.

### Check 9 — Prerequisite verdicts (PASS)

CDA SME PASS-WITH-NOTES verdict is present at `/opt/lsb-agent/docs/status/2026-05-01-check9-infra-split-cda-sme-verdict.md`, landed in this same commit. The commit message references it explicitly. All seven mandatory SME notes were verified satisfied in the prior review and are not affected by the amendment. No UI/UX verdict required (no frontend). Prerequisites are satisfied.

---

## SME mandatory notes — compliance audit (carried forward from prior review)

All seven notes were verified against the diff in the original review. The amendment (`24h` → `48h`) does not affect any of the seven notes. Status carried forward.

| Note | Requirement | Status |
|---|---|---|
| 1 | `run_infrastructure_checks` docstring contains "Never mutates `InformantRecord.qa_passed`." | PASS — present at `scripts/qa_check.py` line 344, minor cosmetic deviation on backticks (not blocking) |
| 2 | Alert copy precise and forbidden-vocabulary-clean | PASS |
| 3 | Check 9 comment block marks infrastructure-tier, once-per-sweep, no `qa_passed` mutation, references verdict file | PASS — present at `scripts/qa_check.py` lines 63–68 |
| 4 | `ARCHITECTURE.md` §4.1.6 contains Check 9 infrastructure-tier paragraph with correct threshold | PASS — threshold corrected to `(currently 48h)` matching `MAX_BACKUP_AGE_HOURS = 48` |
| 5 | `run_qa_checks` shim docstring says "Deprecated for live collection... Removal target: F3 cleanup pass." | PASS |
| 6 | `tests/unit/test_runner.py::test_run_informant_no_backup_log_does_not_fail_qa` exists | PASS — present at line 274, uses `_mock_adapter()`, no real API call |
| 7 | Commit message references both verdict file and plan file; states Task 2 out of scope | PASS |

---

## Factual accuracy — corrected item

`ARCHITECTURE.md` line 784 (the only change in the amendment):

- **Before:** `| 9 | Backup-log freshness | \`mtime(logs/backup.log)\` within \`MAX_BACKUP_AGE_HOURS\` (currently 24h); file must exist | ... |`
- **After:** `| 9 | Backup-log freshness | \`mtime(logs/backup.log)\` within \`MAX_BACKUP_AGE_HOURS\` (currently 48h); file must exist | ... |`

Code constant at `scripts/qa_check.py:62`: `MAX_BACKUP_AGE_HOURS = 48`. Document and code now agree. No other changes in the amended commit confirmed by `git show 36d180e --stat` (same 7 files, same net line counts).

---

## Test / CI status (independently verified)

- `uv run pytest`: **751 passed** in 12.89s. No failures.
- `uv run ruff check .`: **All checks passed.**
- `uv run mypy packages/`: **Success: no issues found in 54 source files.**
- No-LLM-imports static check on `cdb_analyze/`: PASS (comment lines only, no actual imports).

---

## Additional observations (carried forward, non-blocking)

**Stale comments in `packages/cdb_collect/cdb_collect/runner.py`**

Lines 215 and 264 of `runner.py` contain references to `run_qa_checks` in code comments that were not updated (pre-existing before this commit; the actual call sites at lines 267 and 275 correctly use `run_record_checks`). Cosmetic. Recommend a follow-up cleanup commit.

**Three new tests vs. plan's two**

The plan specified two new tests (AC8 and AC9); the Coder added a third (`test_post_infrastructure_alert_posts_expected_fields`). Additive and welcome. Not a concern.

---

## Recommendation

**Ship to master.** All nine binding checks pass. The single blocking item from the prior FAIL verdict is resolved. Test suite, lint, and mypy are independently verified clean. The Tester gate is next per the pipeline; route to Tester.

---

---

# REVIEWER HISTORY — Prior verdict (for audit trail)

**Commit reviewed:** `0b310e7`
**Date:** 2026-05-01
**Verdict:** **FAIL**

```
REVIEWER VERDICT: FAIL

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

**Failure:** `ARCHITECTURE.md` §4.1.6 table row for Check 9 stated `(currently 24h)` while `scripts/qa_check.py:62` defined `MAX_BACKUP_AGE_HOURS = 48`. A reader of the binding architecture document would believe the threshold was 24 hours when the actual threshold was 48 hours. Required correction: change `(currently 24h)` to `(currently 48h)`.

**Required before merge (from prior verdict):**
1. Correct the `ARCHITECTURE.md` §4.1.6 table threshold from `(currently 24h)` to `(currently 48h)` to match `MAX_BACKUP_AGE_HOURS = 48` in `scripts/qa_check.py`.

**Resolution:** Applied in amended commit `36d180e`. Correction is exactly the single-character change recommended.

---

*Reviewer agent — LSB Reviewer (Sonnet 4.6)*
*Verdict file: `/opt/lsb-agent/docs/status/2026-05-01-check9-infra-split-reviewer-verdict.md`*
