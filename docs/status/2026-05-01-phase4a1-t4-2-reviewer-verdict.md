# Reviewer Verdict — Phase 4a.1 T4.2 Note J Cross-tab + K-frame/K-vocab Subtype (task #21.T4.2)

**Filed:** 2026-05-01
**Reviewer:** LSB Reviewer (claude-sonnet-4-6)
**Commit under review:** `8a3fe36`
**Task:** #21.T4.2 — Note J cross-tab + K-frame/K-vocab subtype (Amendment 2 §3 T4 + Amendment 3 §3.2)
**Gate verdicts cited by commit:**
- Architect Amendment 3: `docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md`
- CDA SME PASS-WITH-NOTES: `docs/status/2026-04-30-phase4a1-amendment-3-cda-sme-verdict.md`
- B11 source (T3C verdict): `docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md`
**Prerequisite gate chain verified:**
- T4.1 Reviewer PASS: `docs/status/2026-04-30-phase4a1-t4-1-reviewer-verdict.md` (commit `6aa0986`)
- T4.1 Tester AUGMENTED-PASS: `docs/status/2026-04-30-phase4a1-t4-1-tester-verdict.md`
- Mark hand-code: commit `a89a012`
- CDA SME PASS-WITH-NOTES on Amendment 3: `docs/status/2026-04-30-phase4a1-amendment-3-cda-sme-verdict.md`

---

## REVIEWER VERDICT: PASS-WITH-NOTES

```
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

**Note A (informational, deferred to CDA SME output gate):** The D20 mechanism string contains the phrase "cross-provider replication on the {domain_str} domains" and is emitted unconditionally — including in the `else` branch that applies when disposition is `CONFIRMED` (not `CONFIRMED-with-mechanism`). With the actual production data (all 9 safety rows from google, single provider), the emitted mechanism string will include "cross-provider replication" text even though the cross-provider threshold was not met. The Reviewer finds this is a **methodology question, not a Reviewer-gate issue**: (1) the mechanism string in the `CONFIRMED` branch is placed in a "Mechanism description" section that is explicitly labeled as not-the-headline, accompanied by a "Note: disposition is `CONFIRMED` (not CONFIRMED-with-mechanism) because the cross-provider replication threshold is not met" notice; (2) the disposition_string itself is `"Note K: CONFIRMED"` with no mechanism fragment in it; (3) the Reviewer's nine checks do not adjudicate whether the D20 mechanism string should be conditionally suppressed or modified when the cross-provider threshold is unmet — that is a methodology decision belonging to the CDA SME output gate at `docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md`. This observation is flagged here so the CDA SME is aware the Reviewer considered it and explicitly deferred.

**Note B (informational, style only):** The commit subject line is 76 characters. CLAUDE.md §8 states "first line is under 72 characters." The rule is a style convention documented in §8 / §11, not one of the nine enumerated Reviewer checks; it is not one of R1–R12 in SECURITY_AND_HARDENING §9. Prior commits in this task chain also exceeded 72 characters without triggering a gate failure (e.g., `a89a012` is 81 characters). This is noted as a style observation; it does not block merge. Future commits should tighten subject lines to ≤72 characters.

---

## What was verified

### Check 1 — No LLM imports in cdb_analyze/ (PASS)

`grep -r "import anthropic\|import openai\|from anthropic\|from openai\|InferenceClient\|google.generativeai" packages/cdb_analyze/` returns two lines in `cdb_analyze/__init__.py`, both inside a comment block enumerating forbidden libraries (not import statements). The new script `scripts/phase4a1_note_j_crosstab.py` imports only `argparse`, `json`, `pathlib`, `sys`, `collections`, `typing`, `cdb_analyze.manual_classification`, and `cdb_analyze.safety_subtype`. No LLM client libraries. The script is in `scripts/`, not `cdb_analyze/`, but the spirit of Check 1 (pure data analysis, no LLM calls) is satisfied. The test file additionally includes a static-import assertion test (lines 1130–1148) that asserts the script's source contains no LLM client library imports. PASS.

### Check 2 — Append-only JSONL (PASS)

`git show 8a3fe36 --name-only` lists exactly two files: `scripts/phase4a1_note_j_crosstab.py` and `tests/test_phase4a1_note_j_crosstab.py`. Both are new additions. `data/raw/informants.jsonl` is not present in the commit diff. No pre-existing lines in any JSONL file were touched. PASS.

### Check 3 — No API keys or secrets (PASS)

Scanned both changed files and the commit body for key-shaped strings: `sk-ant-`, `sk-or-v1-`, `hf_[a-zA-Z0-9]{30,}`, Slack webhook URL patterns (`hooks.slack.com/services/T[A-Z0-9]+`), `LSB_ALERTS_WEBHOOK_URL`, `LSB_CDA_SME_WEBHOOK_URL`, `LSB_UI_UX_WEBHOOK_URL`, `ANTHROPIC_API_KEY=`, `OPENROUTER_API_KEY=`, `password`, `token` (as a credential). No matches. The test file uses placeholder model IDs like `"google/gemini-2.5-pro"` and `"openai/gpt-5.4-mini"` — these are not credentials. PASS.

### Check 4 — Forbidden vocabulary (PASS)

Scanned both `.py` files and the commit body for all terms from CLAUDE.md §7 and ARCHITECTURE.md §1.5.4:

**CLAUDE.md §7 terms:** `worldview`, `believes` (applied to models), `thinks` (applied to models), "Model X believes...", "Model X thinks of...", "How models see the world", "Model X's worldview", "Cultural bias" (standalone), "What the model understands". No matches in either file. The test file at lines 1060–1073 itself asserts these are absent from the script's output — belt-and-suspenders.

**ARCHITECTURE.md §1.5.4 superset terms:** `within-model consensus`, `within-model cultural consensus`, `within-model eigenratio`, `within-model CCM`, `publishable` (for LSB findings). No matches in either file.

**The §3.3 guardrail phrase rephrasing (Coder deviation 2):** Amendment 3 §3.3 contained the phrase "not what the model believes" in a plan document (the plan, not the script output). The Coder flagged that emitting "not what the model believes" in the script's output text would trip §7 forbidden vocab (specifically: `believes` applied to models). The Coder substituted "not a claim about the model's internal state." This rephrasing is faithful to §1.5.4 and superior to the original plan language: it expresses the same methodological guardrail (the mechanism string describes trigger patterns, not model cognition) without using forbidden vocabulary. The substitution is correct. PASS.

### Check 5 — Schema + DATA_DICTIONARY (N/A)

`cdb_core/schemas.py` was not modified. The commit touches no files in `cdb_core/`. Per Architect Amendment 3 §3.1: "No new schema changes. No edits to `cdb_core/schemas.py`. No edits to `decline_detection.py`." Confirmed. N/A.

### Check 6 — New dependencies without Architect sign-off (N/A)

No changes to `pyproject.toml`, `uv.lock`, `apps/dashboard/package.json`, or `apps/dashboard/package-lock.json`. N/A.

### Check 7 — Prompt templates versioned correctly (N/A)

No files under `packages/cdb_collect/prompts/` were changed. N/A.

### Check 8 — No point estimates without uncertainty in visualizations (N/A)

This is a pure analysis script producing Markdown + JSON output. No frontend components, no `.tsx`/`.ts`/`.html` files, no D3 or Plotly charts. Cross-tab counting output is not a visualization in the §4.5 sense. N/A.

### Check 9 — Prerequisite gate verdicts (PASS)

**CDA SME gate:** This is a methodology-significant task (B11 operationalization per Amendment 3). The required CDA SME PASS or PASS-WITH-NOTES verdict is present: `docs/status/2026-04-30-phase4a1-amendment-3-cda-sme-verdict.md`, verdict PASS-WITH-NOTES filed 2026-05-01. Three new binding notes were added (B13 soft, B14 binding on T5 §8.1/§8.2, B15 soft). None of B13/B14/B15 impose obligations on T4.2 directly:
- B13: soft, binds future batches with ≥10 K-frame rows — no T4.2 action.
- B14: binding on T5 §8.1/§8.2 numerics-vs-interpretation separation — not T4.2.
- B15: soft, binds future dashboard rendering of the bipartite mechanism string — not T4.2.

The commit correctly references the CDA SME verdict in its body. The Amendment 3 §3.2 acceptance criteria are addressed: the `safety_attribution_subtype` column is present on the cross-provider sub-table; the "Note K mechanism breakdown" sub-section is present; the bipartite mechanism string per D20 is embedded in the Note K disposition output; the test fixture includes a synthetic 9-row safety cohort split 5/4 across two providers as required.

**Gate chain completeness:** T4.1 Reviewer PASS (commit `6aa0986`), T4.1 Tester AUGMENTED-PASS (commit `3a8cadc`), and Mark's hand-code (commit `a89a012`) all precede commit `8a3fe36` in the git log. The gate chain is intact. PASS.

**UI/UX gate:** Not required. This is not a frontend task.

---

## Specific acceptance-criteria spot-checks

**Four-input loading with clear errors:** Confirmed at `scripts/phase4a1_note_j_crosstab.py`. The `load_all_inputs` function checks existence of all four paths (decline_interviews, informants, manual_classification, subtype) with clear error messages naming the missing path. UNCLASSIFIED rows are detected after loading via `load_safety_attribution_subtypes` (the sentinel rejection is in `safety_subtype.py`, already verified at T4.1). Tests `test_missing_decline_interviews_raises`, `test_missing_informants_raises`, `test_missing_manual_classification_raises`, `test_missing_subtype_artifact_raises`, `test_unclassified_subtype_raises` all exercise these paths.

**Disposition arithmetic (D21):** The `compute_note_k_disposition` function at lines 532–634 computes disposition from `safety_event_attribution_count + blocked_event_attribution_count` and `n_providers`. K-frame and K-vocab counts are computed from the subtype artifact and reported in `supporting_numerics` and the JSON output as descriptive fields, explicitly labeled "(descriptive, not a disposition input per D21)" in the Markdown output. The D21 invariant test `test_cross_provider_subtype_asymmetry_surfaced_not_disposition_shifted` confirms that a 5/4 K-frame/K-vocab split across two providers keeps disposition at `CONFIRMED-with-mechanism` regardless of which provider holds which subtype. PASS.

**Note K disposition tiers — all five exercised:** Tests cover `CONFIRMED-with-mechanism` (≥5, ≥2 providers), `CONFIRMED` (≥5, 1 provider), `INCONCLUSIVE-SUGGESTIVE` (2–4), `INCONCLUSIVE` (1), `NOT CONFIRMED` (0). Verified at test names `test_note_k_confirmed_with_mechanism_exact_threshold`, `test_note_k_confirmed_single_provider`, `test_note_k_inconclusive_suggestive`, `test_note_k_inconclusive_single_row`, `test_note_k_not_confirmed_zero_safety`.

**Amendment 3 §3.2 fixture (9-row split 5/4 across two providers):** `_build_amendment3_9row_fixture` at line 673 constructs exactly 5 `k_frame` rows from `google` and 4 `k_vocab_without_k_frame` rows from `openrouter`, matching the plan spec. Tests confirm the fixture produces `CONFIRMED-with-mechanism` disposition, mechanism string contains all D20 wording components, and the cross-provider sub-table includes the `safety_attribution_subtype` column. PASS.

**No real API calls, no production data access:** Test file header and inline comments confirm "No real API calls. No access to data/raw/ or data/derived/ production artifacts." All test fixtures are constructed in-memory using `tmp_path` and `_make_*` builder functions. Production paths under `/opt/lsb-agent/data/` are not referenced in any test. PASS.

**Commit format:** `feat(scripts):` prefix matches the affected package (scripts). Commit body references both gate verdict files by path (Amendment 3, CDA SME verdict, B11 source). Task ID `#21.T4.2` present. ARCHITECTURE.md §4.2 referenced. Subject line is 76 characters (4 over the 72-char guideline in §8 — see Note B above).

---

## Deferred to CDA SME output gate

The following issues are **explicitly deferred to the CDA SME output gate** at `docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md`:

1. **D20 mechanism string content when cross-provider threshold unmet.** The mechanism string "cross-provider replication on the {domain_str} domains" is computed and emitted unconditionally (including in the CONFIRMED / not-CONFIRMED-with-mechanism branch). Whether this string is methodologically appropriate to emit (in a subordinate "Mechanism description" section, not the disposition headline) when the actual data is single-provider is a methodology question. The Reviewer confirms the script correctly:
   - Does NOT include the mechanism fragment in the `disposition_string` headline when disposition is `CONFIRMED`.
   - Labels the mechanism description section clearly as subordinate.
   - Appends an explicit note that the cross-provider threshold was not met.
   The CDA SME should assess whether the "cross-provider replication" phrase in the descriptive section is misleading given single-provider actuals, and whether D20's mechanism string should be conditionally modified.

2. **2/7 K-frame/K-vocab distribution vs. SME-predicted 5/4.** The actual distribution (2 K-frame, 7 K-vocab) diverges from the SME's B11 prediction (5/4). The commit body correctly flags this as an "SME-FLAG NOTE." This is a methodology finding that the CDA SME should evaluate at the output gate in the context of the §8.2 mechanism description.

3. **Single-provider safety cohort (all 9 rows from google).** The actual data produces `CONFIRMED` (not `CONFIRMED-with-mechanism`) because the cross-provider replication threshold requires ≥2 distinct providers and the corpus has only google in the safety bucket. The script behavior (emitting `CONFIRMED`) is mechanically correct per D21. Whether the disposition tier needs any amendment, narrative context, or escalation is the CDA SME's call at the output gate.

---

## Failures

None that block merge.

## Required before merge

None. Commit is on master. The two Coder-flagged deviations are either (a) correctly resolved by the Coder (§7 forbidden vocabulary rephrasing) or (b) deferred appropriately to the CDA SME output gate (D20 mechanism string with single-provider actuals).

---

## Notes for the Tester

The Reviewer reviewed 37 test functions as a count-check only (Coder reported 37/37 passing). No independent test run was performed per the task brief ("Do not retest — Coder already verified ruff/mypy/pytest clean (37/37 + 776 full suite)"). Spot-checks of fixture construction and assertion logic are documented under "Specific acceptance-criteria spot-checks" above. The Tester should confirm:

1. The 9-row Amendment 3 fixture (`_build_amendment3_9row_fixture`) runs against both the `CONFIRMED-with-mechanism` (2-provider) and `CONFIRMED` (1-provider) branches — the current fixture only exercises the 2-provider path. A separate 1-provider 9-row fixture (matching actual production data) would improve coverage.
2. B14 (binding on T5 §8.1/§8.2 numerics-vs-interpretation separation) does not bind T4.2 tests — the Tester covering T5 should read the Amendment 3 SME verdict for this obligation.

---

*End of Reviewer verdict for commit `8a3fe36`. Filing at `docs/status/2026-05-01-phase4a1-t4-2-reviewer-verdict.md`. Coder may proceed; next gate is the CDA SME output gate at `docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md` before T5 begins.*
