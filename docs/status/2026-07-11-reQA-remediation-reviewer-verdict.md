# Reviewer Verdict: re-QA Remediation (N15-N19)

**Date:** 2026-07-12
**PR / changeset:** uncommitted working tree (R1-R4 + tests)
**Authority:** Architect plan docs/status/2026-07-11-reQA-remediation-architect-plan.md;
CDA SME N15-N19 addendum in docs/status/2026-07-10-batchA-reasoning-qa-cda-sme-verdict.md

---

## REVIEWER VERDICT: PASS

---

| Check | Result |
|---|---|
| Check 1 -- No LLM imports in cdb_analyze/ | PASS |
| Check 2 -- Append-only JSONL | PASS |
| Check 3 -- No secrets | PASS |
| Check 4 -- Forbidden vocabulary | PASS |
| Check 5 -- Schema + DATA_DICTIONARY | N/A |
| Check 6 -- New deps sign-off | N/A |
| Check 7 -- Prompt versioning | N/A |
| Check 8 -- Uncertainty in viz | N/A |
| Check 9 -- Prerequisite verdicts | PASS |

---

## Check notes

**Check 1.** The grep for LLM client tokens in packages/cdb_analyze/ produced two
matches, both in the pre-existing comment block of __init__.py (not changed by
this PR). Both are documentation-only lines enumerating what is forbidden, not
functional import statements. The __init__.py diff is empty. No actual LLM
import was added. PASS.

**Check 2.** The production file data/raw/informants.jsonl is gitignored (CLAUDE.md
pitfall 10) and is not in the changeset. The modified file
tests/fixtures/reasoning_class/informants.jsonl is a test fixture at a different
path and is not subject to the data/raw append-only rule. PASS.

**Check 3.** No API keys, webhook URLs, or credentials appear in any changed file.
The webhook URL reference in qa_check.py reads from os.environ.get() only. PASS.

**Check 4.** Grepped additions in all six changed files for all CLAUDE.md §7 and
ARCHITECTURE.md §1.5.4 forbidden terms. No matches in user-facing or documentation
context. PASS.

**Check 9.** CDA SME PASS-WITH-NOTES verdict with binding notes N15-N19 is present
in the 2026-07-11 addendum of docs/status/2026-07-10-batchA-reasoning-qa-cda-sme-verdict.md.
The architect plan states "Re-review routing: SME not required (executes binding notes
verbatim)." No UI/UX gate applies (no frontend surface). Notes addressed by R1-R4
as verified below. PASS.

---

## Binding-note implementation verification (against orchestrator claims)

**R1 / N15 partition.** load_records calls run_record_checks(record, [record]).
check_2_freelist_uniqueness builds same_runs from all_records filtered to matching
model_id and domain_slug; with a single-element list that element matches itself,
yielding len(same_runs) == 1 < 2, which hits the self-guard and returns None. Check 2
is mechanically disabled without any conditional bypass.

_has_check2_signature uses re.fullmatch(r"\d+\.\d+%", segment.strip()) on each
semicolon-split segment of qa_notes. Check 2's QAFailure.actual is f"{ratio:.1%}",
producing exactly one decimal digit (e.g., "12.5%"), which fullmatches the pattern.
No per-record check writes a bare percentage: Check 1 writes str(count), Check 3
writes "found N", Check 4 writes "N != M", Check 5 writes "{ms}ms", Check 6 writes
str(int), Check 7 writes "empty", Check 8 writes "label_count_mismatch:N/M".
campaign_id tags do not match. The fullmatch (not search) requirement prevents partial
matches. False-positive risk is nil under the current check set.

qa_check.py changes are docstrings only (partition paragraph in module docstring,
per-check "Per-record check (CDA SME N15)" prefixes). No behavioral change to any
check function. Confirmed by reading the full diff.

**R2 / N16 guard.** The RuntimeError is raised iff n_true_now_false_by_model is
non-empty. That dict is incremented only on the persisted-True-now-False branch.
Recoveries (persisted-False-now-True) increment only n_false_now_true; they never
touch n_true_now_false_by_model. The error message includes per-model drop counts via
sorted(n_true_now_false_by_model.items()). Recoveries cannot trigger the guard.

**R3 / N17 slate.** All three approved_slate frozensets were verified:
- Family: 15 published basis models (from 0.3.json, verified in test) + 7 batch A =
  22 models. claude-fable-5 absent. qwen/qwen3.6-plus absent (pending Mark comment
  present). z-ai/glm-5.1 absent (same).
- Holidays: 14 published basis models (no microsoft/phi-4 vs. family) + 7 batch A.
- Food: 12 published basis models + 7 batch A.
The filter is applied after load_records (basis membership only; informants.jsonl
untouched). An empty frozenset is falsy and skips the filter block (no-op).

**R4 / version bump.** DOMAIN_CONFIG: family new_version "0.4" / prior_version "0.3",
holidays new_version "0.4" / prior_version "0.3", food new_version "0.3" /
prior_version "0.2". Prior versions are unchanged; the threshold guard loads
data/results/{domain}/{prior_version}.json for comparison. Staging paths become 0.4/
0.4/0.3, no collision with citable published versions.

**Rule 15 (math freeze).** No estimator, measure, resampling scheme, or threshold
semantics were modified. Changes are: QA scope partitioning in load_records (which
records recompute per-record vs. inherit persisted verdict), a monotonicity count
guard, an approved-slate filter at rebaseline entry, a version-string bump, and
docstring annotations. The statistical pipeline in run_pipeline is unchanged.

---

## Failures

None.

## Required before merge

None. Coder may commit.
