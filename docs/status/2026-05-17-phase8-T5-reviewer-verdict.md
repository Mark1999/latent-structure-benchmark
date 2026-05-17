---
filed: 2026-05-17
reviewer: LSB Reviewer agent (Sonnet)
task: Phase 8 T5 — Pre-release scan implementation
commits_reviewed:
  - 4ebb66b (feat(scripts): Phase 8 T5 — pre-release scan implementation)
  - ea8130d (fix(scripts): T5 follow-up — pre-release scan green via allow-list expansion)
plan_reference: docs/status/2026-05-17-phase8-architect-kickoff.md §3 T5 + §6
verdict: PASS
---

# Phase 8 T5 Reviewer Verdict

## REVIEWER VERDICT: PASS

```
Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         PASS
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A
Check 6 — New deps sign-off:         PASS
Check 7 — Prompt versioning:         N/A
Check 8 — Uncertainty in viz:        N/A
Check 9 — Prerequisite verdicts:     PASS
```

---

## Per-check rationale

**Check 1 — No LLM imports.** `scripts/prerelease_scan.py` uses only stdlib (`argparse`, `datetime`, `json`, `os`, `re`, `subprocess`, `sys`, `pathlib`). Two matching lines in `cdb_analyze/__init__.py` are comment-only prohibition notices, not actual imports. PASS.

**Check 2 — Append-only JSONL.** Neither commit touches `data/raw/informants.jsonl`. PASS.

**Check 3 — No secrets.** No API keys, tokens, webhook URLs, passwords, or credentials. The `API_KEY_PATTERNS` and `FORBIDDEN_PATTERNS` constants are pattern-definition strings used for detection, not actual secrets. The scan itself passes its own Check 5. PASS.

**Check 4 — Forbidden vocabulary.** All appearances of forbidden vocabulary terms in `scripts/prerelease_scan.py` are within the `FORBIDDEN_PATTERNS` list — regex strings for detection, not model-facing prose. Script's own prose, error messages, and report-template strings contain no §1.5.4 violations. PASS.

**Check 5 — N/A.** No `cdb_core/schemas.py` changes.

**Check 6 — New deps sign-off.** `pyproject.toml` untouched; pure stdlib. PASS.

**Check 7 — N/A.** No prompt template files touched.

**Check 8 — N/A.** Not a frontend PR.

**Check 9 — Prerequisite verdicts.** Kickoff specifies Architect-only gating for T5; embedded in §3 T5 + §6 and ratified in §12. Both commit bodies reference the kickoff. PASS.

---

## T5-specific verifications

**All 8 checks implemented per kickoff §6.** Inspected `scripts/prerelease_scan.py`:
- Check 1 gitleaks subprocess at line 416 (correct).
- Check 2 forbidden-vocab grep at lines 458–487.
- Check 3 internal-path scan at lines 493–515 with patterns matching kickoff §6.
- Check 4 email-address scan at lines 521–561.
- Check 5 API-key-pattern scan at lines 568–623 (covers `sk-`, `hf_`, `xai-`, AWS, GitHub PATs, GitLab PATs, Slack bot tokens, Slack webhook URLs).
- Check 6 public-URL syntax check at lines 629–675.
- Check 7 `.env` / credential presence at lines 681–715.
- Check 8 license-coverage sanity at lines 721–734.

**CLI behavior:** `--report PATH`, `--report -`, `--json PATH` all present in `main()` at lines 844–941. Exit codes 0/1/2 per spec.

**Allow-lists are sensible.** The `ea8130d` remediation correctly expanded internal-path allow-list. Each entry justified by an inline comment. `tests/` is broader than the literally-relevant `tests/cdb_publish/` but justified since path-redaction fixtures exist in multiple packages.

**Scan reproducibility:** Independent re-run against `HEAD` (`ea8130d`) produces identical results — all 8 checks PASS, exit 0.

**`scripts/run_phase4a_t4.sh` deleted:** Confirmed absent from working tree.

**Scope sanity:** Both commits stay strictly within scope.

**Test baseline:** 1791 pytest pass; ruff + mypy clean.

---

## Notes (non-blocking)

**N1 — Scan report HEAD field is stale at merge time.** The report committed in `ea8130d` shows `Repository state: 4ebb66b` because the scan ran during working-tree development. The report itself mandates re-generation within 24 hours of M12. Not a defect; the re-run immediately preceding M12 will capture the then-current HEAD.

**N2 — `tests/` allow-list breadth.** Broader than the immediately-relevant `tests/cdb_publish/`. Documented in the inline comment. Acceptable.

**N3 — Check 6 URL scope.** Skips non-existent files silently (T6/T7 deliverables not yet generated). Correct behavior; the check will exercise them once T6/T7 land.

---

## Verdict

**PASS.** All nine binding checks pass. All T5-specific verifications pass. Tester may proceed.

---

*End of Phase 8 T5 Reviewer verdict.*
