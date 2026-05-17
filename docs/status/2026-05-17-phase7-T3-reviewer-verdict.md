---
filed: 2026-05-17
reviewer: LSB Reviewer agent (Sonnet)
task: Phase 7 T3 — Drafter framework + Bluesky drafter
commit: 262927a (feat(social): Phase 7 T3 — drafter framework + Bluesky drafter)
plan_reference: docs/status/2026-05-17-phase7-architect-kickoff.md §3 T3
cda_sme_verdict: docs/status/2026-05-17-phase7-T3-cda-sme-verdict.md (PASS-WITH-NOTES, 18 binding notes)
verdict: FAIL
---

# Phase 7 T3 — LSB Reviewer Verdict

## REVIEWER VERDICT: FAIL

```
Check 1 — No LLM imports in cdb_analyze:    PASS
Check 2 — Append-only JSONL:                 PASS
Check 3 — No secrets:                        PASS
Check 4 — Forbidden vocabulary:              PASS
Check 5 — Schema + DATA_DICTIONARY:          N/A
Check 6 — New deps sign-off:                 N/A
Check 7 — Prompt versioning:                 PASS
Check 8 — Uncertainty in viz:                N/A
Check 9 — Prerequisite verdicts:             PASS
```

The nine binding checks pass. The FAIL is on two T3-specific CDA SME §5.x binding-note deviations.

---

## Failures

### FAIL 1 — §5.11 framing_checks key names deviate from the CDA SME binding specification

**Files:** `packages/cdb_social/cdb_social/drafters/base.py` lines 324–329; `tests/unit/test_social_drafters.py` lines 483–484, 492–496, 500–501, 507–508

The CDA SME §5.11 binding specification:

```python
framing_checks = {
    "hypothesis_framing": <bool>,       # per §5.3
    "cognition_attribution": <bool>,    # per §5.1 (forbidden_terms_hit subset)
    "bare_numeric_without_ci": <bool>,  # per §5.2
    "register_boundary": <bool>,        # per §5.1 (R1/R2 substring scan subset)
}
```

The T1 schema docstring at `packages/cdb_core/cdb_core/schemas.py` lines 789–791 also lists `'hypothesis_framing'`, `'cognition_attribution'`, `'bare_numeric_without_ci'` by name, establishing the downstream consumer contract for T5's review CLI.

The implementation delivers:

```python
framing_checks = {
    "no_cognition_attribution": ...,   # wrong name, semantics inverted
    "no_value_attribution": ...,        # wrong name, NOT "register_boundary"
    "no_hypothesis_framing": ...,       # wrong name, semantics inverted
    "numeric_has_adjacent_ci": ...,     # wrong name, semantics inverted
}
```

Two deviations:

1. **Key names wrong.** All four keys carry an inverted `no_` prefix that contradicts the CDA SME binding key names AND the T1 schema docstring naming convention (which states the value `True` means the check passed — so the key should be the *positive* concept, not the negation).

2. **`register_boundary` is absent entirely.** The CDA SME specified this as a distinct key covering only the R1/R2 boundary phrases (rows 7–10: `within-model consensus`, `within-model cultural consensus`, `within-model eigenratio`, `within-model CCM`). The code collapses all phrase hits into a single `no_value_attribution` key, providing no separate register-boundary audit signal.

Downstream T5's review CLI will fail to read the field correctly. The schema-docstring → validator → review CLI contract is broken before T5 is written.

### FAIL 2 — §5.8 sliding-window rejection monitor is non-functional

**File:** `packages/cdb_social/cdb_social/drafters/base.py` lines 574–592

The CDA SME §5.8 binding specification: "≥ 2 rejections within any 10-draft window" where a "draft" is any drafting attempt, including successful ones.

The `_check_rejection_window` implementation reads the last 10 lines of `drafter_rejections.jsonl` and fires the warning whenever there are ≥ 2 lines. Since the rejection log only records failures, the window is the last 10 *rejections*, not the last 10 *attempts*. The monitor cannot distinguish a 2/10 rejection rate (the actual escalation trigger) from a 1/1000 rejection rate once the log has 11+ entries — once rejections exceed ~10 total, the warning fires unconditionally and provides no operational signal.

The correct implementation requires tracking total drafts attempted (passes + rejections) and computing the rejection rate within the most recent 10-attempt window.

---

## Required before merge

1. **Fix `framing_checks` keys to match CDA SME §5.11 binding specification.** In `base.py` `validate_draft()` and everywhere they appear in `test_social_drafters.py`:
   - `"no_cognition_attribution"` → `"cognition_attribution"` (value: `True` if no cognition-attribution words detected — i.e., check passed)
   - `"no_value_attribution"` → must be split: introduce `"register_boundary"` (True if no R1/R2-boundary phrases hit — rows 7–10 of §1.5.4 only) as a separate key, and either drop the residual value-attribution key or rename it to a positive concept ("value_attribution_check_passed" is acceptable if a residual key is needed for other phrases; the four canonical keys remain `hypothesis_framing`, `cognition_attribution`, `bare_numeric_without_ci`, `register_boundary`)
   - `"no_hypothesis_framing"` → `"hypothesis_framing"` (value: `True` if no hypothesis-framing phrases detected — check passed)
   - `"numeric_has_adjacent_ci"` → `"bare_numeric_without_ci"` (value: `True` if every numeric finding has its adjacent CI — i.e., NO bare numeric without CI was found — check passed)

   `register_boundary` must be a separate key that flags only rows 7–10 (`within-model consensus`, `within-model cultural consensus`, `within-model eigenratio`, `within-model CCM`), not all phrase patterns.

2. **Fix `_check_rejection_window` to implement the correct 10-draft window semantics.** Track total drafts attempted (passes + rejections) and compute the rejection rate within the most recent 10-attempt window. Two equivalent approaches:
   - (a) Append a record to a unified `drafter_audit.jsonl` for every draft attempt with an `outcome: "pass"|"reject"` field. Read the last 10 entries; count rejections; fire when ≥ 2.
   - (b) Maintain a separate `drafter_attempts.jsonl` for passes and reuse the existing `drafter_rejections.jsonl` for rejections, with a join key (timestamp or counter) to compute the rate.

   Approach (a) is simpler and recommended.

The two fixes are mechanical and well-scoped. No CDA SME re-review required (the §5.x notes are unchanged). After the Coder fixes, this Reviewer issues an addendum PASS.

---

*End of Phase 7 T3 Reviewer FAIL verdict.*
