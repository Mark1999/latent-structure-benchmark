# Phase 4a.1 — Architect Decomposition Plan (task #21)

**Date:** 2026-04-23
**Planner:** Architect
**Task:** #21 (Phase 4a.1 decline-interview backfill)
**Predecessor:** Phase 4a T7 Reviewer PASS (`943937c`); master tip `f82c22d`
**Preceding gates on record:**
- Architect plan for Phase 4a (`docs/status/2026-04-22-phase4a-kickoff-architect-verdict.md`)
- T5 CDA SME PASS-WITH-NOTES (`docs/status/2026-04-23-phase4a-t5-cda-sme-verdict.md`) — introduces forward Note K
- Decline-interview Protocol SME PASS-WITH-NOTES (`docs/status/2026-04-23-decline-interview-protocol-sme-verdict.md`)
- T7 Reviewer PASS — Phase 4a.1 GO disposition (`docs/status/2026-04-23-phase4a-t7-reviewer-verdict.md`)

**Gate verdict chain for this plan:**
- Architect decomposition (this document)
- **CDA SME PASS-WITH-NOTES** (`docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md`) — 8 binding notes folded into the task specs below

**Expected spend:** < $1 (target ~$0.15–$0.30 aggregate across ≤30 calls); hard cap $2 per D7.

---

## 1. Summary

Phase 4a.1 operationalizes the decline-interview protocol (landed via task #26) against the 27 `qa_passed=False` records surfaced by T6 plus any Gemini `failures.jsonl` entries that `detect_from_failure` flags. Output: one `DeclineInterview` record per triggered session in `data/raw/decline_interviews.jsonl`, followed by a completion report that includes the Note J cross-tab — the binding output that determines whether Note K (CN-origin decline clustering) formalizes as a methodology amendment.

No schema changes. No analysis pipeline edits. No `informants.jsonl` mutation. Tooling is all landed; this phase *uses* it.

---

## 2. Architect dispositions (all concurred or accepted by SME except as noted)

- **D1.** The 8 grok-4 Check-5-only (latency-only) records — **DEFER from API backfill; INCLUDE in enumeration + rationale documentation.** Detector keys on structural signals (empty lists, allowlist string, degenerate pile); latency is not a v1 trigger. SME concur (Ruling 3).
- **D2.** JSONL output path: `data/raw/decline_interviews.jsonl`. SME concur.
- **D3.** `detection_timestamp` captured once at batch-start; passed to every `run_decline_interview` call. SME concur.
- **D4.** `originating_model_version_returned` sourcing per landed runner logic; empty string → `version_drift_flag=False` for failures-origin. SME concur.
- **D5.** `task_description` = verbatim original prompt text from the originating step; template-reconstruction fallback for failures-origin entries lacking `prompt_verbatim` (RISK 1). SME concur.
- **D6.** `originating_response_verbatim` mirrors D5. SME concur.
- **D7.** Hard spend cap $2 (double-expected). Abort on exceed; decline_interviews.jsonl stands (append-only). SME concur, contingent on binding note 8 (T1 dry-run must report Gemini failures count before T3 commits).
- **D8.** Sequential execution at ≤30 calls. SME concur.

---

## 3. Task list (with SME amendments inline)

### T1 — Detection enumeration & CLI runner scaffold

**Scope:** Build `scripts/run_decline_backfill.py` — a thin CLI that reads `informants.jsonl` + `failures.jsonl`, invokes `detect_all`, prints the detected session count grouped by `(source, originating_step, originating_outcome_class, model_id)`, and exits **without making any API calls** when run with `--dry-run`. Non-dry-run mode runs the full backfill (see T2).

**Acceptance criteria:**
- `uv run python scripts/run_decline_backfill.py --dry-run` exits 0 and writes a summary table to stdout.
- Summary table columns: `source | originating_step | originating_outcome_class | model_id | count`.
- Summary includes a **"not triggered" section with per-record rows** (SME binding note 1) showing the 8 grok-4 Check-5-only records **and any `qa_passed=False` records where `detect_from_informant` returned None**, each with:
  - `informant_id`, `model_id`, `domain`, `originating_step`, `failing_checks`, and a one-phrase **reason** ("Check-5 latency-only, no structural trigger"; "Check-8 token inconsistency, response_verbatim non-empty"; etc.).
- Summary includes any Gemini `failures.jsonl` entries detected by `detect_from_failure` (count currently unknown).
- **Dry-run also reports the Gemini failures count before T3 commits to the $2 cap** (SME binding note 8). If the projected batch size × per-call-cost estimate ≥ $1.60 (80% of $2 cap), stop and escalate — D7 needs re-evaluation on a new plan cycle, not ad-hoc in T3.
- Dry-run touches only stdout. No file writes. Asserted via test.
- Fixture-based unit test (`tests/test_run_decline_backfill.py`) covering: 3 glm-5.1 empty freelist (trigger c), 10 qwen latency+token (structurally valid → None), 4 Check-8 (trigger d), 1 llama-4-maverick Check 5+8 (trigger d), 8 grok-4 Check-5-only (None with per-record reason emitted), 1 synthetic Gemini failure.

**Expected commit:** `feat(collect): scripts/run_decline_backfill.py enumeration + dry-run (task #21.T1)`

**Verdicts required:** Reviewer PASS. Tester PASS.

**Reading list:** `docs/DECLINE_INTERVIEW_PROTOCOL.md`, `docs/status/2026-04-23-decline-interview-protocol-sme-verdict.md`, `docs/status/2026-04-23-phase4a-t6-qa-sweep.md` §7 + §9, `packages/cdb_collect/cdb_collect/decline_detection.py`, `packages/cdb_collect/cdb_collect/run_decline_interview.py`.

---

### T2 — Live backfill execution path

**Scope:** Extend `scripts/run_decline_backfill.py` with the live execution path. For each DetectedSession from T1, reconstruct `task_description` and `originating_response_verbatim` per D5/D6, invoke `run_decline_interview` with the correct adapter, and append each returned `DeclineInterview` to `data/raw/decline_interviews.jsonl` via `append_decline_interview`. Per-call cost printed; running total printed; abort at D7's $2 cap.

**Acceptance criteria:**
- `uv run python scripts/run_decline_backfill.py --execute` produces N `DeclineInterview` records in `data/raw/decline_interviews.jsonl`, where N matches T1's detected count.
- Every written record passes `DeclineInterview.model_validate_json`.
- xor invariant holds: exactly one of `originating_informant_id` / `originating_failure_id` is non-null per record.
- `detection_timestamp` is identical across all records in a single batch (D3).
- `detection_rule_version = "v1"` on every record.
- `version_drift_flag` computed per landed runner logic.
- `append_decline_interview` is the only write path. No edits to `informants.jsonl` or `failures.jsonl`.
- CLI run summary at end: records written, total cost, min/median/max latency, `version_drift_flag` count.
- Fixture-based integration test using MockAdapter returning deterministic `AdapterResult`; confirms full loop writes valid records, respects cost cap, handles xor for both informants-origin and failures-origin detections.

**Commit message:** `feat(collect): decline-interview backfill execute path (task #21.T2)`

**Verdicts required:** Reviewer PASS. Tester PASS.

---

### T3 — Live batch run on `lsb-agent-02`

**Scope:** Execute `scripts/run_decline_backfill.py --execute` on `lsb-agent-02` against the real Phase 4a `informants.jsonl` and `failures.jsonl`. Capture stdout + stderr. B2 backup of `decline_interviews.jsonl` triggered after completion.

This is an **execution task, not a code task**. One commit; no file edits beyond `data/raw/decline_interviews.jsonl` and a run log.

**Acceptance criteria:**
- `data/raw/decline_interviews.jsonl` exists and contains N records matching T1's detected count.
- Total spend < $2 (confirmed by CLI summary; stored in run log).
- No records written to `informants.jsonl` or `failures.jsonl`.
- B2 backup of the new `decline_interviews.jsonl` confirmed (backup log cited in run report).
- Run log preserved at `docs/status/2026-04-23-phase4a1-t3-run-log.md` with: command invoked, CLI summary output, spend total, `version_drift_flag` count, any **recursive decline** cases observed (where the follow-up itself declined; per RISK 2, documented verbatim).

**Commit message:** `data(collect): Phase 4a.1 decline-interview backfill run (task #21.T3)`

**Verdicts required:** Reviewer PASS.

---

### T4 — Note J cross-tab + Note K re-evaluation

**Scope:** Build `scripts/phase4a1_note_j_crosstab.py` — pure Python (pandas + stdlib), deterministic, reporting-only. Consumes `data/raw/decline_interviews.jsonl` + `data/raw/informants.jsonl` + the model registry and emits the Note J cross-tab.

**Cross-tab structure (SME binding notes 2 + 3):**

- **Primary view (required, published inline in T5):** `outcome_class × model_origin` — a 2D cross-tab. Rows: `originating_outcome_class` ∈ {empty_output, refusal_string_match, single_degenerate_pile, parse_failure, http_error, timeout, other}. Columns: `model_origin` ∈ {us, eu, ca, cn, other}.
- **Secondary drill-downs (optional, published as separate tables if populated):** `outcome_class × openness_state`; `outcome_class × collection_method`. Do NOT publish a three-way factorial at this n.
- **Cell value:** count of decline-interview records (interviewed population, not raw `qa_passed=False`).
- **Expected-rate baseline (SME binding note 2; Architect one-line confirmation):** corpus collection-attempt distribution, **not** interviewed-only uniform.

  ```
  expected_per_cell = (total_decline_interviews) × (collection_attempts_in_cell / total_collection_attempts)
  flag if observed_per_cell >= 3 × expected_per_cell AND observed_per_cell >= 2
  ```

  **Architect confirmation (Ruling 1a):** confirmed. The baseline switch is correct; the `>= 2` floor is the right small-n guard; and the corpus-attempt denominator is the only denominator that makes a "disproportionate" signal visible past the selection bias baked into the interviewed-only population. Binding on the T4 script.

**Note K re-evaluation logic (SME binding note 4):**

```
CONFIRMED if:
  CN_decline_count >= 5                                              [tightened from Architect's 4]
  AND non_CN_decline_count >= 1                                      [denominator guard]
  AND Check-6 extended-thinking confound explicitly addressed        [new]
  AND (CN_decline_count / CN_corpus_count) / (non_CN_decline_count / non_CN_corpus_count) >= 2.0

INCONCLUSIVE-SUGGESTIVE if:                                          [new disposition]
  4 <= CN_decline_count < 5
  AND ratio would be >= 2.0 if met
  AND no alternative explanation supplants origin

INCONCLUSIVE if:
  CN_decline_count < 4 OR ratio < 2.0 with no alternative explanation

NOT CONFIRMED if:
  Note J cross-tab documents an alternative explanation that supplants origin
  (e.g., extended-thinking routing pattern explains the decline population
  across any-origin models)
```

**Acceptance criteria:**
- Script runs deterministically. Byte-equal output on a fixed input.
- Emits the 2D primary cross-tab + secondary drill-downs (if any cell is non-empty).
- Emits the CONFIRMED/INCONCLUSIVE-SUGGESTIVE/INCONCLUSIVE/NOT CONFIRMED verdict line with supporting numerics.
- Fixture-based test: synthetic `decline_interviews.jsonl` with known cell counts; confirms expected-rate math, `>= 2` floor, Note K verdict logic across all four dispositions.

**Commit message:** `feat(scripts): Phase 4a.1 Note J cross-tab + Note K re-eval (task #21.T4)`

**Verdicts required:** **CDA SME PASS required** (methodology-binding). Reviewer PASS after SME. Tester PASS.

---

### T5 — Completion report + Note K disposition

**Scope:** Write `docs/status/2026-04-23-phase4a1-completion-report.md`. Nine sections required.

**Required sections:**

1. **Timeline** (T1 → T5 commits + dates)
2. **Gate summary** (all verdicts referenced: this plan, SME verdict on this plan, per-task reviewer + SME verdicts)
3. **Artifacts:** `decline_interviews.jsonl` path, record count, byte count, B2 timestamp
4. **Cost accounting:** T3 spend + cumulative Phase 4a + 4a.1 total
5. **Input set reconciliation:** 27 T6 candidates + Gemini failures → N detected. The 8 grok-4 Check-5-only records documented under "not triggered" with **per-record enumeration by (model, domain, originating_step, informant_id)** (SME binding note under Ruling 3) so Mark can later rule them in under a v2 allowlist amendment without reconstructing the worklist.
6. **Note J cross-tab** (verbatim from T4 output): 2D primary view + any populated secondary drill-downs + flagged cells
7. **Note K disposition** with one of four verdicts (SME binding notes 4 + 5):
   - **CONFIRMED:** methodology-page amendment drafted inline using **coverage-caveat framing**, not model-behavior framing (SME Ruling 6). Template:
     > "LSB's v1 coverage is US-weighted by informant composition (7 of 12 models in the v1 slate are US-origin). A secondary coverage caveat applies: CN-origin models in the v1 slate disproportionately produced responses that did not pass QA on the family and holidays domains (N of 5 decline-interviewable cells are CN-origin, of N_CN CN-origin collection attempts vs. N_nonCN non-CN collection attempts). This is a signal about the reach of LSB's elicitation protocol across the v1 slate, not a claim about CN model behavior."
     Cross-tab linked (not summarized-only). Alternative-explanation review visible in the same section.
   - **INCONCLUSIVE-SUGGESTIVE:** Note K carried forward verbatim into methodology-page backlog with `n=X` caveat explicit. Re-evaluate at next Phase 4a.2 remediation cycle.
   - **INCONCLUSIVE:** Note K remains forward concern; same re-evaluation trigger.
   - **NOT CONFIRMED:** Note K retired **only if** alternative explanation documented. Cross-reference update in T6 report and Phase 4a completion report §Interaction-with-prior-SME-notes table.
8. **Decline-interview findings summary:** refusal patterns observed, `version_drift_flag` count, recursive-decline cases with two-tier flag per SME binding note 6:
   - Any recursive decline in a non-CN-origin model → SME narrow prompt re-review flagged
   - ≥ 33% recursive overall → SME broad prompt re-review flagged
9. **Re-analysis decision** (SME binding note 7): explicitly enumerate the **specific numerics** that would shift under each denominator scenario. Not just a flag. Minimum content:
   - Current Note C denominator: 18 analyzable + 5 decline-interviewable = 23 of 24 non-Gemini cells
   - If all 4 Check-8 records interview successfully: denominator becomes 18/23 → **22/23 cells analyzable** (Check-8 records have structurally valid output; the 8 records don't add to decline-interviewable)
   - If the 3 glm-5.1 empty-freelist records interview: 5 → 5 decline-interviewable (no denominator shift, they're already counted in Note C)
   - If Gemini failures interview: affects only the Gemini cells (family is already excluded as pre-session failure); potential shift on holidays if a Gemini×holidays failure is present
   - Follow-up task scope: whether `data/results/family/0.1.json` / `data/results/holidays/0.1.json` need recomputation under the updated `n_analyzable` / `n_decline_interviewable` split. **Execute only on a new Architect plan cycle**; not inline.

**Acceptance criteria:**
- Report at the named path, all 9 sections present
- No forbidden vocabulary (§1.5.4). "Declined" is acceptable per SME-approved protocol naming; "corpus lens" is the approved §1.5.1 term.
- Cross-references complete: T5 SME verdict, T6 QA sweep, decline-interview SME verdict, T4 Note J output, T3 run log, this plan + SME verdict on this plan
- Note K wording (if CONFIRMED) routes through the coverage-caveat frame per SME Ruling 6

**Commit message:** `docs(status): Phase 4a.1 completion report + Note K disposition (task #21.T5)`

**Verdicts required:** **CDA SME PASS required** (Note K disposition language is SME territory). Reviewer PASS after SME.

---

## 4. Dependency graph

```
T1 (enumeration + dry-run) ──┐
                             ├──► T3 (live batch run) ──► T4 (Note J + Note K re-eval) ──► T5 (completion report)
T2 (execute path)            ──┘                                                                    │
                                                                                                    │
                                               (CDA SME gate on T4, T5) ◄──────────────────────────┘
```

T1/T2 may be separate commits (§8 default) or bundled if separability is artificial. T3 depends on T1+T2 code landing. T4 depends on T3 output. T5 depends on T4 output.

---

## 5. Pre-conditions to verify before T1

Coder must verify these before writing code (and again at T1 dry-run time):

- [ ] `packages/cdb_collect/cdb_collect/decline_detection.py` exports `detect_all`, `DECLINE_ALLOWLIST_VERSION="v1"`
- [ ] `packages/cdb_collect/cdb_collect/run_decline_interview.py` exports `run_decline_interview`, `build_prompt`
- [ ] `packages/cdb_collect/cdb_collect/jsonl.py::append_decline_interview` exists
- [ ] `packages/cdb_core/cdb_core/schemas.py::DeclineInterview` with xor validator exists
- [ ] `packages/cdb_collect/cdb_collect/prompts/decline/v1/prompt.txt` exists
- [ ] `data/raw/informants.jsonl` has the 101-record T6 corpus
- [ ] `data/raw/failures.jsonl` present (may be empty; Coder confirms count at T1 dry-run)
- [ ] Adapter registry resolves the 6 affected model families (glm-5.1, qwen3.6-plus, mistral-small-2603, gpt-5.4-mini, llama-4-maverick, plus Gemini if failures trigger)
- [ ] `.env` has provider keys active; spend cap config has ≥ $2 headroom
- [ ] B2 backup timer active

**The Coder MUST run T1 `--dry-run` and post the enumeration + Gemini failures count to the commit body before executing T2/T3** (SME binding note 8).

---

## 6. Risk flags (with SME rulings applied)

- **RISK 1 — failures-path `task_description` reconstruction.** Surface to orchestrator at T1 dry-run if `prompt_verbatim` is missing on Gemini failures. Potential amendment to D5 fallback semantics before T2.
- **RISK 2 — recursive decline.** Two-tier rule (SME Ruling 4, binding note 6):
  - Any recursive decline in a non-CN-origin model → narrow SME prompt re-review
  - ≥ 33% recursive across full population → broad SME prompt re-review
  - No preemptive v1 prompt refinement; append-only applies.
- **RISK 3 — `version_drift_flag` noise.** Audit-only in v1; not actionable. Phase 4b+ territory.
- **RISK 4 — re-analysis scope creep.** Forbidden inline; documented as follow-up task only. SME binding note 7.
- **RISK 5 — 8 grok-4 records re-disposition.** v2 allowlist amendment on new plan cycle.
- **RISK 6 — Gemini failures count unknown.** T1 dry-run reports; if projected batch ≥ 80% of $2 cap, escalate per SME binding note 8.

---

## 7. Binding SME notes (cross-reference to plan locations)

| SME note | Applied in |
|---|---|
| 1. T1 per-record not-triggered reasoning (not just counts) | T1 acceptance criteria §"not triggered section with per-record rows" |
| 2. T4 cross-tab baseline = corpus attempt distribution + `>= 2` floor | T4 §"Expected-rate baseline" + Architect confirmation |
| 3. T4 primary view = 2D `outcome_class × origin`; no factorial | T4 §"Cross-tab structure" |
| 4. Note K taxonomy: add INCONCLUSIVE-SUGGESTIVE; CONFIRMED ≥ 5 CN + ≥ 1 non-CN + Check-6 addressed | T4 §"Note K re-evaluation logic" + T5 §7 |
| 5. T5 §9 CONFIRMED: coverage-caveat framing; cross-tab linked; alt-explanation visible | T5 §7 CONFIRMED template |
| 6. RISK 2 two-tier rule (any non-CN → narrow; ≥ 33% → broad) | T3 run log + T5 §8 |
| 7. T5 §9 specific numerics that would shift per denominator scenario | T5 §9 outline |
| 8. T1 dry-run reports Gemini failures count before T3 commits | T1 acceptance criteria §"Dry-run also reports..." |

---

## 8. Files (absolute paths for Coder reference)

Inputs:
- `/opt/lsb-agent/data/raw/informants.jsonl`
- `/opt/lsb-agent/data/raw/failures.jsonl`
- `/opt/lsb-agent/packages/cdb_collect/cdb_collect/decline_detection.py`
- `/opt/lsb-agent/packages/cdb_collect/cdb_collect/run_decline_interview.py`
- `/opt/lsb-agent/packages/cdb_collect/cdb_collect/jsonl.py`
- `/opt/lsb-agent/packages/cdb_collect/cdb_collect/prompts/decline/v1/prompt.txt`
- `/opt/lsb-agent/packages/cdb_core/cdb_core/schemas.py` (`DeclineInterview`)

Outputs:
- `/opt/lsb-agent/scripts/run_decline_backfill.py` (T1, T2)
- `/opt/lsb-agent/tests/test_run_decline_backfill.py` (T1)
- `/opt/lsb-agent/data/raw/decline_interviews.jsonl` (T3)
- `/opt/lsb-agent/docs/status/2026-04-23-phase4a1-t3-run-log.md` (T3)
- `/opt/lsb-agent/scripts/phase4a1_note_j_crosstab.py` (T4)
- `/opt/lsb-agent/tests/test_phase4a1_note_j_crosstab.py` (T4)
- `/opt/lsb-agent/docs/status/2026-04-23-phase4a1-completion-report.md` (T5)

Gate verdict files (created as pipeline progresses):
- `/opt/lsb-agent/docs/status/2026-04-23-phase4a1-architect-plan.md` (this doc)
- `/opt/lsb-agent/docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md` (exists)
- `/opt/lsb-agent/docs/status/2026-04-23-phase4a1-t{1,2,3,4,5}-reviewer-verdict.md` (per-task)
- `/opt/lsb-agent/docs/status/2026-04-23-phase4a1-t{4,5}-cda-sme-verdict.md` (SME-gated tasks)

---

*End of Phase 4a.1 decomposition plan. Five tasks, two SME gates, one budget cap, zero schema changes. SME PASS-WITH-NOTES with 8 binding notes folded inline. Coder may start T1.*
