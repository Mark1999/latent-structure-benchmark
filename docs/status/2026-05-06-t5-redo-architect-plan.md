# Phase 4a T5 Redo — Architect Plan

**Date:** 2026-05-06
**Planner:** Architect agent (Opus)
**Task:** Phase 4a T5 redo — fresh analytical-layer computation against the recovered (post-Task-#16, post-recovery-campaign) corpus, closing Phase 4a under the corrected instrument framing
**Predecessor (the work being redone):**
- Original T5 analysis report: `docs/status/2026-04-23-phase4a-t5-analysis-report.md` (commit `d74ce57`)
- Original T5 SME verdict: `docs/status/2026-04-23-phase4a-t5-cda-sme-verdict.md` (PASS-WITH-NOTES; Notes A, C, D, E, G, K)
- Original T5 Reviewer verdict: `docs/status/2026-04-23-phase4a-t5-reviewer-verdict.md` (PASS-WITH-NOTES)
- Original Phase 4a completion report: `docs/status/2026-04-23-phase4a-completion.md` (preserved as audit; not edited)

**Authorizing chain that justifies the redo:**
- Task #16 SME verdict, S2 + S5: `docs/status/2026-05-04-task-16-cda-sme-verdict.md`
- Phase 4a recovery report (20/20 cells recovered, 100% rate, +20 informants on master): `docs/status/2026-05-05-phase4a-recovery-report.md`
- Parent T4-redo SME verdict (B6 / B12 / B14 carry forward; B11 REPLACED): `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md`
- T4-redo RD-3 reframing memo (Note K is REPLACED, S5 satisfied): `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md`
- T4-redo RD-3 content SME verdict (S5-completing PASS-WITH-NOTES): `docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md`
- v2 prompt forward-carry status doc (informs §8 prose scoping): `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md`

**Companion docs (mandatory reading for the Coder before starting):**
- `ARCHITECTURE.md` §1.5 (binding framing on all generated text), §3.2 (`InformantRecord`, `DomainResult`), §4.2 (analytical-layer constraint — no LLM imports in `cdb_analyze`), §4.2.5 (groundings: list, optional), §4.2.6 (bootstrap), §4.5 (uncertainty)
- `CLAUDE.md` §6 binding rules (especially R7 schema/dictionary lockstep, R11 no point estimates without uncertainty, R12 no LLM imports in `cdb_analyze`, R13 SME PASS gate), §7 forbidden vocabulary, §8 commit conventions, §9 pitfall 1 (`model_id` vs. `model_version_returned`), §9 pitfall 9 (no real API calls in tests)
- `docs/SME_REVIEW.md` — measure thresholds (Romney 5.0 operational, 3.0 reported; small-n n<15)
- `docs/BOOTSTRAP_DESIGN.md` — Level 1 vs. Level 2 (Option 2 annotated-uncertainty is binding for v1)
- `docs/DATA_DICTIONARY.md` — only consulted, not modified (no schema change in this plan)

**Gate chain (mandatory, in order):**
1. **CDA SME PASS or PASS-WITH-NOTES on this plan** — non-negotiable per CLAUDE.md §6 R13. The plan touches analytical measures (Smith's S, Sutrop CSI, Romney CCM, MDS, Procrustes, OCI), gate thresholds, bootstrap design, and methodology-page-bound public copy — all routes named in CLAUDE.md routing rule for the Architect agent.
2. **Coder → Reviewer → Tester** per Coder commit, per task in §2 below.
3. **CDA SME content PASS on the T5 redo analysis report** at `docs/status/2026-05-06-phase4a-t5-redo-cda-sme-content-verdict.md` — second SME pass, gates the methodology-page-bound prose in the report's interpretation section before any downstream rendering.
4. **No UI/UX gate** on this plan or its tasks (analytical, not frontend; the eventual methodology-page UI rendering is a separate Phase 5/6 task with its own UI/UX gate per the parent T4-redo SME Q4 ruling).

> **Status before the Coder may start any task:** CDA SME PASS or PASS-WITH-NOTES on this plan. No new operator sign-off required (Mark's §5 framing decisions on the parent T4-redo plan are already on master via the RD-1/RD-2/RD-3 commits).

---

## §0. Why this plan exists

Phase 4a T5 (commit `d74ce57`, 2026-04-23) computed Smith's S / Sutrop CSI / Romney CCM / MDS / OCI / bootstrap CIs against a 101-record corpus that included 20 fewer informants than the corpus has today. Those 20 cells failed during the original Phase 4a collection at `max_output_tokens=4096` and were recovered on 2026-05-05 at the corrected `max_tokens=16384` cap (recovery report `docs/status/2026-05-05-phase4a-recovery-report.md`, 100% recovery rate, $1.29 actual cost). The recovered records are appended to `data/raw/informants.jsonl` and carry `qa_notes` containing `campaign_id=phase4a-recovery-2026-05-05`.

Three things make T5 redo the correct successor task today:

1. **The corpus has materially changed.** The original T5 ran on `n_models=10` for family and `n_models=8` for holidays. The recovered corpus contains additional valid records for `google/gemini-2.5-pro` (×10 cells), `meta-llama/llama-4-maverick` (×4 cells), and `z-ai/glm-5.1` (×6 cells). Those additions cross the `n_models < 15` small-n threshold from below, but do not cross it from above — small-n caveat still binds. The exact `n_models` per domain depends on whether the recovered records pass QA at re-run time (the recovery report verified Pydantic v0.1.11 validity, but did not re-run `qa_check.py`).

2. **The framing under which T5 reports has changed.** Original T5's Note K SME verdict (PASS-WITH-NOTES) carried forward a Note K hypothesis ("CN-origin model decline clustering") and bound public copy to the framing "US-weighted composition PLUS disproportionate CN-origin decline pattern." The T4-redo RD-3 memo (commit `bdc06e4`-line per recent log) **REPLACED Note K** under the cap-exhaustion reframe. The 4-of-5-decline-interviewable-cells pattern that originally motivated Note K is now understood as instrument artifact, not signal. T5 redo public copy must be authored under the RD-3 framing, not the original Note K framing. Parent T4-redo SME B11 is REPLACED for this exact reason; B6 (public-copy guardrails) carries forward as binding for the T5 §8 architecture.

3. **The analytical layer is unblocked at the data layer.** The RD-3 memo §5 explicitly names the analytical work as unblocked and out of scope for RD-3. The parent T4-redo SME Q5 ruling concurs ("the recovered corpus enables Smith's S, Romney CCM, MDS, Procrustes, OCI on the corrected corpus. None of those are in scope for [the T4-redo] plan. When the Architect plans them, the plan routes through me with a fresh SME pass."). This plan is that fresh Architect plan.

T5 redo is **not** a re-litigation of T4 redo. T4 redo disposed Note K under the new framing; T5 redo computes the analytical artifacts on the corrected corpus. The two plans are layered, not redundant.

---

## §1. Disposition table

| Concern | Disposition | Rationale |
|---|---|---|
| **Predecessor T5 artifacts** (`data/results/family/0.1.json`, `data/results/holidays/0.1.json`, `2026-04-23-phase4a-t5-analysis-report.md`) | **PRESERVED VERBATIM as audit.** Not edited, not deleted, not annotated with sibling `.SUPERSEDED.md`. | The original DomainResult JSON files and the original analysis report are the authoritative record of what T5 reported on 2026-04-23 against the 2026-04-22 corpus. They are not falsified — they are correct against their input population. The sibling-`.SUPERSEDED.md` annotation pattern from RD-1 was used because the May 1 hand-coded artifact's *premise* was falsified; here, the data and the analysis are both internally consistent against the original input. The redo writes new outputs at a new analysis version (see next row). The audit reader of the original 0.1 JSON files traces forward via the new completion report's "predecessor T5" subsection to find the redo. **No supersedure annotation files are created in this task.** |
| **New DomainResult files** | **`data/results/family/0.2.json` and `data/results/holidays/0.2.json`** with `analysis_version="0.2"`. Existing 0.1 files preserved unchanged. | An analysis-version bump is the canonical mechanism for distinguishing the redo from the predecessor (`scripts/analyze.py --analysis-version 0.2`). The pipeline already supports this without code changes; `write_result()` writes to `data/results/{domain}/{version}.json` and a 0.2 file does not collide with the 0.1 file. The `data/results/family/0.2.json` path is in fact already on master per the Phase 4a completion report §5 B2 backup table — it's the original Phase 4a re-fire artifact; T5 redo will overwrite it. **Note for SME Q1 below:** the prior 0.2 file's content is from a different pipeline configuration; T5 redo's 0.2 will replace it. If preservation of that specific 0.2 file matters (it shouldn't; it predates the recovery), the SME may direct a different version label. |
| **New analysis report** | **`docs/status/2026-05-06-phase4a-t5-redo-analysis-report.md`** | Date-stamped to today's commit. The filename mirrors the predecessor's pattern (`YYYY-MM-DD-phase4a-t5-...`) for audit-trail symmetry. |
| **New Phase 4a completion report** | **`docs/status/2026-05-06-phase4a-completion-redo.md`** | Successor (not replacement) to `docs/status/2026-04-23-phase4a-completion.md`. The original is preserved as audit. The new completion report references the original as predecessor and reports the corpus state, gate verdicts, and forward-carry as of 2026-05-06. |
| **Schema changes** | **NONE.** | Pydantic `InformantRecord` and `DomainResult` are unchanged. No `cdb_core/schemas.py` edits, no `DATA_DICTIONARY.md` updates. Per CLAUDE.md §6 R7, schema changes require Architect sign-off + matching dictionary update; this plan affirms there is no such change. |
| **Prompt-template changes** | **NONE.** v1 prompts unchanged. The v2-prompt suggestion is a Phase 5+ forward-carry per `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md`. |
| **`build_db.py` rerun** | **PREREQUISITE OPS TASK, executed before T5 computation.** | `cdb_analyze.pipeline.load_records()` reads `data/raw/informants.jsonl` directly (verified at `packages/cdb_analyze/cdb_analyze/pipeline.py:74-88`); it does NOT depend on `data/open_bundle/lsb.sqlite`. Therefore the SQLite bundle staleness does not block the analytical computation. **However**, the recovery report §5 explicitly defers the `build_db.py` rerun and identifies the bundle as 20 rows behind the JSONL. The parent T4-redo SME R5 binding is "separate ops task." Re-running `build_db.py` while the corpus is fresh and no other pending appends are queued is the cleanest moment to discharge that R5 deferral. **It is sequenced first in §2** so that the open-data bundle and the analytical results published in this Phase 4a closure are both built off the same canonical JSONL state. The task is mechanical (one command); it does not require its own SME pass beyond this plan's PASS. |
| **Methodology-page UI rendering** | **OUT OF SCOPE.** | The methodology-text gate is satisfied by the SME PASSes on (a) the RD-3 memo (already done), and (b) the T5 redo analysis report (this plan's task RD-T5-4). The downstream UI rendering is a Phase 5/6 task with its own UI/UX gate. T5 redo prose lives in `docs/status/` as text-on-disk only. |
| **v2-prompt comparison study** | **OUT OF SCOPE.** Forward-carry only. | Phase 5+ candidate per the status doc. T5 redo prose may reference the doc by path when discussing the v1 stimulus-as-anchor observation (RD-3 §4.4), but does not duplicate its content and does not propose a v2 arm. |
| **phi-4 ×6 + gpt-5.4-mini ×2 + mistral-small ×1 unexplained-failure investigation** | **OUT OF SCOPE.** | Recovery report §7 items 3 + 4. T5 redo closes Phase 4a against what is in the corpus today; the unexplained failures are separate Architect tasks. The completion report §7 forward-carry must list them. |
| **Note K reframe** | **OUT OF SCOPE — RD-3 owns it.** | T5 redo public copy uses the RD-3 framing as established (Note K REPLACED; the confabulation observation is the substantive replacement; no new "Note L" designation; cross-provider/cross-domain generalization forbidden per parent T4-redo SME T6). T5 redo does not re-litigate, re-state, or re-frame the disposition. References to the disposition cite the memo path. |
| **Forbidden vocabulary** | **None used in the plan; the Coder's analytical report is bound by §1.5 framing throughout.** | Any T5 redo prose that interprets the analytical artifacts must use the §1.5-clean substitutes (categorical structure, corpus lens, output narratives) rather than `worldview` / `believes` / `thinks` / `cultural bias`. Public-copy guardrails per parent T4-redo SME B6: same posture as RD-3, applied to the new report's interpretation section. The Reviewer enforces; the SME content verdict double-checks. |

---

## §2. Tasks

Four sequential Coder tasks. The split rationale follows the two-stage discipline that B14 binds: **numerics-vs-interpretation separation**. Tasks RD-T5-1 through RD-T5-3 produce numerics, fixtures, and the report's data tables (Axis 2 substance). Task RD-T5-4 produces the interpretive prose that frames those numerics for methodology-page-bound text (Axis 3 / Axis 4 substance). Splitting the four tasks into four commits — rather than bundling — preserves CLAUDE.md §8 "one commit per task," makes each Reviewer pass scope-bounded, and lets the SME content verdict on the report's interpretation be issued against an artifact whose numerics have already passed Reviewer.

### Task RD-T5-1 — `build_db.py` rerun (prerequisite ops)

**Owner:** Coder
**Files:**
- Read: `data/raw/informants.jsonl` (canonical, current)
- Modify: `data/open_bundle/lsb.sqlite` (regenerated wholesale by `build_db.py`)
- New: none
- Touched docs: none in this commit

**Behavior contract:**
1. Run the documented command from the recovery report §5 verbatim:
   ```
   uv run python scripts/build_db.py data/raw/informants.jsonl data/open_bundle/lsb.sqlite
   ```
2. The command rebuilds the open-data bundle SQLite from the canonical JSONL. No code change to `build_db.py`; no schema change; no DDL change.
3. Verify the resulting SQLite contains the 20 recovery records by spot-check (one query against `informant_id` for one of the recovery cells listed in the recovery report §2).

**Acceptance criteria:**
- `data/open_bundle/lsb.sqlite` is regenerated and contains the post-recovery row count (= JSONL line count, modulo any pre-existing skip rules in `build_db.py`).
- Spot-check query returns the recovery record(s).
- `git diff` shows only `data/open_bundle/lsb.sqlite` (binary file) modified, plus any commit-noise files. No code changes, no docs changes.
- `uv run pytest && uv run ruff check . && uv run mypy packages/` green.

**Test coverage (Tester):** Regression-only. No new tests. The Tester confirms the existing test suite still passes and that `data/open_bundle/lsb.sqlite` opens cleanly (`sqlite3 data/open_bundle/lsb.sqlite '.schema informants'` succeeds).

**Reading list for Coder:**
- This plan §0, §1, §2 RD-T5-1
- Recovery report §5: `docs/status/2026-05-05-phase4a-recovery-report.md`
- `docs/DATA_DICTIONARY.md` §4 (DDL — informational; not modified)

**Commit message template:**
```
chore(ops): T5 redo RD-T5-1 — rebuild open-bundle SQLite post-recovery

Rebuilds data/open_bundle/lsb.sqlite from data/raw/informants.jsonl per
recovery report §5 deferral and parent T4-redo SME R5. No code change.

Refs: docs/status/2026-05-06-t5-redo-architect-plan.md (this plan)
```

---

### Task RD-T5-2 — Run analysis pipeline against recovered corpus

**Owner:** Coder
**Files:**
- Read: `data/raw/informants.jsonl`
- Write: `data/results/family/0.2.json` (overwrites prior 0.2 if present), `data/results/holidays/0.2.json` (overwrites prior 0.2 if present)
- Touched docs: none in this commit

**Behavior contract:**
1. Run the analysis pipeline for each Phase 4a domain:
   ```
   uv run python -m scripts.analyze --domain family   --input data/raw/informants.jsonl --output data/results --bootstrap 500 --analysis-version 0.2
   uv run python -m scripts.analyze --domain holidays --input data/raw/informants.jsonl --output data/results --bootstrap 500 --analysis-version 0.2
   ```
2. The bootstrap iteration count `B=500` matches the predecessor T5 (consistency with the prior bootstrap envelope; SME Q4 below surfaces this for explicit reaffirmation).
3. The `--mode` flag is **NOT** passed (no `collection_mode` filter). The original T5 also did not filter on collection mode (per pipeline log "10 models, 41 total records"); the recovered records carry `collection_mode="single_pass"` per the recovery campaign's adapter conventions, matching the original T4 records. **If the SME's Q3 ruling is to filter, this task incorporates that filter at the SME's direction.**
4. Use the existing `-m scripts.analyze` invocation form (the predecessor T5 report §1.3 documents the workaround for a pre-existing `scripts/inspect.py` shadowing issue, which has since been renamed to `scripts/lsb_inspect.py` per task #30; the `-m` form continues to work and is preserved for procedural consistency).
5. **Do not modify `scripts/analyze.py` or `packages/cdb_analyze/`.** This task is computation-only against existing pipeline code.

**Acceptance criteria:**
- `data/results/family/0.2.json` and `data/results/holidays/0.2.json` exist post-task and are valid `DomainResult` JSON per Pydantic v0.1.11.
- `n_models` for both domains is consistent with the post-recovery corpus state (expected ≥ 10 for family, ≥ 8 for holidays — exact counts depend on QA-passed denominator at run time).
- `consensus_score`, `consensus_ci`, `romney_eigenratio`, `romney_consensus_pass`, `romney_consensus_warning`, `romney_small_n_warning`, `cultural_centrality_scores`, `mds_coordinates`, `mds_uncertainty`, `similarity_matrix`, `similarity_ci`, `sutrop_csi`, `salience_index_agreement`, `within_model_results` all populated.
- `g1_overall_pass=None`, `g1_salience_stability=None`, `g1_spatial_stability=None`, `g1_aggregate_stability=None`, `g1_salience_pass=None`, `g1_spatial_pass=None` — same first-class state as predecessor T5 (Phase 4b sensitivity study not yet run).
- `groundings=[]` and `selected_baseline_id=None` (no human grounding for Phase 4a; per `ARCHITECTURE.md` §4.2.5 / §1.5.5, ungrounded is a normal first-class state).
- `generated_lede=""` (lede is `cdb_publish` territory, not `cdb_analyze`).
- R11 satisfied: every bootstrap-derived field is populated with associated uncertainty (`mds_uncertainty` per model, `consensus_ci`, `similarity_ci`).
- No exception during pipeline execution.
- `uv run pytest && uv run ruff check . && uv run mypy packages/` green.
- The two analysis runs each finish in under 30 minutes wall-clock (predecessor envelope was 12m37s combined; redo is expected to be similar order of magnitude).

**Test coverage (Tester):** Regression-only. The pipeline itself is already tested in `tests/`; this task exercises it end-to-end on the canonical corpus. Tester confirms the produced `0.2.json` files validate against `DomainResult`, the bootstrap fields are populated, and the existing test suite passes.

**Stop conditions** (if any of these trigger, the Coder pauses and surfaces to the Architect; do not improvise):
- `n_models < 4` on either domain (the pipeline's lower bound for cross-model analysis).
- `romney_eigenratio` is `None` or `NaN` on either domain.
- Any unhandled exception during pipeline execution.
- Wall-clock exceeds 60 minutes for either domain (suggests bootstrap regression; investigate before continuing).

**Reading list for Coder:**
- This plan §0, §1, §2 RD-T5-2
- Predecessor T5 report (for comparison-shape expectations only, NOT for interpretation): `docs/status/2026-04-23-phase4a-t5-analysis-report.md`
- `packages/cdb_analyze/cdb_analyze/pipeline.py` (informational — understand the contract, don't modify)
- `docs/SME_REVIEW.md` §1.1 (Romney threshold), §2.1 (Sutrop CSI)
- `docs/BOOTSTRAP_DESIGN.md` §1, §2, §3 (Option 2 annotated-uncertainty is the v1 binding; underestimation caveat applies to Register 1 fields)
- `ARCHITECTURE.md` §4.2.6, §4.5

**Commit message template:**
```
feat(results): T5 redo RD-T5-2 — DomainResult 0.2 against recovered corpus

Runs cdb_analyze pipeline on data/raw/informants.jsonl post-recovery.
Produces data/results/{family,holidays}/0.2.json with B=500 bootstrap.
No code change; computation-only task.

Refs: docs/status/2026-05-06-t5-redo-architect-plan.md (this plan)
```

---

### Task RD-T5-3 — Numerics report (data tables, no interpretation)

**Owner:** Coder
**Files:**
- Read: `data/results/family/0.2.json`, `data/results/holidays/0.2.json` (produced by RD-T5-2), `data/raw/informants.jsonl`
- Write (new): `docs/status/2026-05-06-phase4a-t5-redo-analysis-report.md` — the analysis report, **§1–§7 only** in this commit (numerics, tables, gate-status surfaces). §8 (interpretation) is the deliverable of RD-T5-4.

**Report structure (sections produced in this commit):**

#### §1. Header
Date, task ID, predecessor T5 commit + report path, recovery report path, RD-3 memo path, parent T4-redo SME verdict path, this plan's path. Single-page with cross-references; no prose synthesis.

#### §2. Execution log
Verbatim mirror of the predecessor's §1 layout: per-domain start time, end time, wall-clock, command line, pipeline log. Includes the `-m scripts.analyze` invocation note for procedural continuity.

#### §3. Stop-condition checks
The same five checks the predecessor used (table layout). Specifically: (1) no unhandled exception, (2) consensus_type and romney_eigenratio populated, (3) `romney_small_n_warning` status (expected True; n likely still <15), (4) `n_models >= 4` on each domain, (5) wall-clock under 30 minutes.

#### §4. DomainResult key fields
Per-domain table mirroring predecessor §3 layout: `domain_slug`, `analysis_version`, `n_models`, `n_records` (qa-passed), `consensus_type`, `romney_eigenratio`, `romney_consensus_pass`, `romney_consensus_warning`, `romney_small_n_warning`, `consensus_score`, `consensus_ci`, `negative_centrality_flag`, `g1_overall_pass`, `cultural_centrality_scores` range, MDS coordinates count. Plus the per-model centrality and MDS coordinate tables. **Numerics only; no interpretation.**

#### §5. Bootstrap uncertainty fields (R11 check)
Confirmation that `mds_uncertainty`, `consensus_ci`, `similarity_ci` are populated; ellipse parameters are real numbers; no point estimates without uncertainty. R11 PASS or document any field where R11 cannot be confirmed.

#### §6. Cell-coverage denominator
Full corpus state under the recovered population. The §6 of the predecessor T5 report named "18 analyzable cells of the 12-model × 2-domain design"; the redo §6 names the post-recovery analyzable cell count, broken out by:
- 12 models × 2 domains = 24 cells (with phi-4 × holidays still as T3-canary scope unless recovered, which it was not).
- Cells with at least one QA-passed record (the analyzable population).
- Cells whose only records are recovery records (newly analyzable post-2026-05-05).
- Cells with all records `qa_passed=False` (the decline-interviewable / failed population — which is now smaller than the original T5's "5 cells" because most of the cap-exhaustion cells were recovered).
- Cells that produced zero records (the unexplained-failure residuum: phi-4 ×6, gpt-5.4-mini ×2, mistral-small ×1).
**Numerics only; no interpretation about what the denominator implies.**

#### §7. Predecessor delta
A compact comparison table: original T5 0.1 vs. redo 0.2, on the fields that the SME verdict on this report will be checking — `n_models`, `n_records`, `consensus_score` + CI, `romney_eigenratio`, `romney_small_n_warning`, `negative_centrality_flag`, MDS coordinate count. **Numerics only; no claim about what the delta means.** The interpretation of the delta lives in §8 (RD-T5-4).

**Behavior contract:**
1. The §1–§7 prose is descriptive and structural. It states what the numbers are. It does not state what the numbers mean.
2. Forbidden vocabulary scan applies: no `worldview`, `believes`, `thinks` (about models), `cultural bias`, `refused` (as agency). The Reviewer enforces.
3. Cross-references to the RD-3 memo, the recovery report, and the predecessor T5 report use `docs/status/...` paths verbatim.
4. The report file is created in this commit but is **incomplete** (no §8); a reader sees a clear "§8 — Interpretation: produced in RD-T5-4 commit" placeholder.

**Acceptance criteria:**
- File exists at the named path.
- §1–§7 are populated and well-formed Markdown.
- §8 is a placeholder labeled "Interpretation: pending RD-T5-4 commit. Numerics in §4–§7 are authoritative; this section will frame them under the RD-3 framing."
- All numerics in the report match the JSON files exactly (Reviewer spot-checks).
- No forbidden vocabulary.
- No interpretation prose — Reviewer rejects any §1–§7 sentence that claims what the numbers mean (vs. stating what the numbers are).
- `git diff` shows only the new report file plus standard markdown lint fixes if any. No JSON file edits, no code edits.

**Test coverage (Tester):** Regression-only.

**Reading list for Coder:**
- This plan §2 RD-T5-3
- Predecessor T5 report §1–§7 (for structural template, not for prose to copy)
- `data/results/family/0.2.json` and `data/results/holidays/0.2.json` (the source of every number)

**Commit message template:**
```
docs(status): T5 redo RD-T5-3 — analysis report numerics (§1-§7)

Adds the §1-§7 (numerics, tables, gate status) of the T5 redo analysis
report. §8 interpretation is the RD-T5-4 deliverable, gated by SME
content verdict.

Refs: docs/status/2026-05-06-t5-redo-architect-plan.md (this plan)
```

---

### Task RD-T5-4 — Interpretation section + completion report (methodology-page-bound prose)

**Owner:** Coder
**Files:**
- Read: the full RD-T5-3 report (incomplete §8), the RD-3 memo, the parent T4-redo SME verdict, the original T5 SME verdict, the original Phase 4a completion report
- Modify: `docs/status/2026-05-06-phase4a-t5-redo-analysis-report.md` — fill in §8 (interpretation) and §9 (binding-note compliance), §10 (closure verdict)
- Write (new): `docs/status/2026-05-06-phase4a-completion-redo.md` — the successor Phase 4a completion report

**Report structure (sections produced in this commit):**

#### §8. Interpretation (methodology-page-bound prose; B14 numerics-vs-interpretation separation binds)

§8 is the only interpretive section in the report. It is gated by the SME content verdict on this report (gate chain step 3). It must:

8.1. **State what the redo's numerics support, under the RD-3 framing.** The post-recovery DomainResults can defensibly support: descriptive consensus characterization for the post-recovery population (Romney CCM eigenratio + small-n caveat per `docs/SME_REVIEW.md` §1.1; Smith's S / Sutrop CSI per-model salience; MDS map of inter-model similarity with bootstrap ellipses; cultural centrality range). The interpretation cites the rerun's `n_models` and `n_records` per domain and reports the consensus-type classification under the existing thresholds.

8.2. **Frame the predecessor delta under the RD-3 framing.** The original T5 ran on a population that excluded the now-recovered cells. The delta is **not** "the original T5 was wrong"; it is "the original T5 was correct against its input population, and the input population has since changed in a methodologically traceable way (cap-exhaustion recovery campaign, 100% rate, instrument event)." The delta in `n_models`, `consensus_score`, etc., reflects the population shift, not a methodological correction. **Forbidden framing under B6:** any phrasing that suggests the original T5's analytical conclusions were "incorrect" or "should not have been published" is rejected. The SME content verdict will be specifically watching for this.

8.3. **Apply the public-copy guardrails per parent T4-redo SME B6 (CARRIES FORWARD active).** Specifically:
   - The "US-weighted composition PLUS disproportionate CN-origin decline pattern" framing from the original T5 SME verdict is **NOT** carried into the redo's §8. Note K is REPLACED; the CN-origin decline pattern was instrument artifact. The redo §8 references the RD-3 memo path and uses RD-3's framing.
   - No cross-provider, cross-failure-mode, cross-prompt-type generalization claims (parent T4-redo SME T6 forbids; the same scope discipline applies to the analytical interpretation).
   - No claim that the analytical findings constitute evidence about the model's "actual" reasoning behavior, internal state, or perceptual capacity.
   - The §1.5 forbidden vocabulary applies throughout (the Reviewer enforces; the SME content verdict double-checks).

8.4. **Address the legacy `thoughts_token_count=0` records explicitly.** Per Task #16 SME S2, the value `0` represents three or four distinct epistemic states. Original Phase 4a successful records carry `0` because the field was added by Task #16 and pre-Task-#16 records did not capture it. T5 redo's pipeline does NOT consume `thoughts_token_count` as an analytical input (verified by code search at plan-write time: no occurrence of `thoughts_token_count` in `packages/cdb_analyze/cdb_analyze/pipeline.py`); therefore the legacy asymmetry does not bias the computed consensus / centrality / MDS. **§8.4 states this explicitly so a downstream reader does not have to verify it independently.** This addresses the parent T4-redo SME proactive-check-2 forward-looking concern at the analytical-computation gate where it was reserved.

8.5. **Honor binding notes that survive the reframe.** The original T5 SME verdict's notes A, C, D, E, G, K had specific destinations:
   - **Note A** (`romney_small_n_warning=True`; CCM caveat): if `n < 15` post-recovery, the warning fires and the §8 narrates it correctly per `docs/SME_REVIEW.md` §1.1.
   - **Note C** (cell-coverage denominator framing): the §6 numerics support this; §8 uses the post-recovery denominator, not the original 18-analyzable + 5-decline-interviewable framing. The exact replacement counts come from §6.
   - **Note D** (no ceiling claims before Phase 4c): the §8 makes no ceiling or proximity-to-human-baseline claims. Same as predecessor.
   - **Note E** (US-weighted composition caveat): carries forward, **without** the Note K augmentation. Standalone US-weighted-composition framing is permitted; the "PLUS disproportionate CN-origin decline pattern" augmentation is REMOVED per RD-3.
   - **Note G** (exact wording for uninterviewed cells): carries forward verbatim if §6 reports any cells that produced no interpretable primary-step output. The exact wording from the original T5 §5 may be reused.
   - **Note K** (CN-origin decline clustering): **DOES NOT carry forward.** REPLACED per RD-3. Any §8 sentence referencing Note K cites the RD-3 memo and uses the REPLACED disposition vocabulary.

8.6. **Reference the RD-3 memo by path** when interpretation touches the confabulation observation, the cap-exhaustion reframe, or the original Note K disposition. The RD-3 memo is the single canonical source for that framing; T5 redo §8 does not re-state RD-3's content.

#### §9. Binding-note compliance table

A table mirroring the predecessor T5 §8: each binding note's destination, status, satisfaction. Includes the parent T4-redo SME T-series notes that carry forward and the RD-3 memo's §8 carry-forward classifications. Specifically tracks: original T5's Notes A, C, D, E, G, K (reframed); parent T4-redo's T1, T4, T5, T6, T7 (most are RD-3-scoped, but B6 / B12 / B14 carry forward to T5 redo content); Task #16 S2 (addressed in §8.4); Task #16 S5 (already satisfied at the RD-3 content verdict).

#### §10. Closure verdict
A short paragraph stating that Phase 4a is closed at the analytical layer under the corrected instrument framing, subject to the gate chain step 3 (SME content verdict) and step 4 (no UI/UX gate at this layer). Forward-carry pointers to the unexplained failures and the v2 prompt sub-study.

#### Phase 4a completion-redo report (`docs/status/2026-05-06-phase4a-completion-redo.md`)

Successor (not replacement) to the original Phase 4a completion report. Mirrors the original's structure (§1 timeline + key commits, §2 gate status, §3 data artifacts, §4 cost summary, §5 B2 backup, §6 DATA_DICTIONARY addendum *(if any — none in T5 redo)*, §7 outstanding carry-forward, §8 Phase 4b readiness, §9 verdict). Updates the corpus state, gate verdicts, cost summary, and forward-carry to reflect 2026-05-06 reality. Cross-references both completion reports — old and new — at the §1 timeline. Explicitly preserves the original as audit and names this as the successor (no `.SUPERSEDED.md` annotation on the original; the audit-trail discipline here is "successor with cross-reference," not "supersedure," because the original was correct against its input population).

**Behavior contract:**
1. §8 prose passes the §1.5 forbidden-vocabulary scan throughout.
2. §8 frames the predecessor delta as population shift, not methodological correction (B6-bound).
3. §8 references the RD-3 memo by path; does not re-state.
4. The completion-redo report is **strictly methodology-text**; it produces no analytical claim that wasn't already in §1–§7 of the analysis report.
5. **No interpretation prose in §1–§7** of the analysis report — those were authoritative under RD-T5-3 and are not edited in this commit. The Reviewer confirms that RD-T5-4 does not back-edit RD-T5-3's numerics sections.

**Acceptance criteria:**
- §8 is populated, well-formed, §1.5-clean, B6-disciplined.
- §9 binding-note compliance table is complete (every relevant note from prior verdicts has a row).
- §10 closure verdict is one-to-three paragraphs.
- The completion-redo report exists at the named path and follows the original's structure.
- `git diff` shows §8/§9/§10 of the analysis report filled in (replacing the placeholder), plus the new completion-redo report. No JSON edits, no code edits, no schema edits.
- No forbidden vocabulary anywhere in the new prose.
- `uv run pytest && uv run ruff check . && uv run mypy packages/` green (regression check; no test changes).

**Test coverage (Tester):** Regression-only.

**Reading list for Coder:**
- This plan §2 RD-T5-4
- The full report from RD-T5-3 (the numerics sections being interpreted)
- RD-3 memo: `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md`
- Parent T4-redo SME verdict: `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md` (B6 binds; B14 binds; T6 scope-discipline informs)
- Original T5 SME verdict: `docs/status/2026-04-23-phase4a-t5-cda-sme-verdict.md` (Notes A/C/D/E/G/K reframing baseline)
- Original Phase 4a completion report: `docs/status/2026-04-23-phase4a-completion.md` (template for completion-redo)
- Task #16 SME verdict: `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (S2 binds §8.4)
- v2 prompt forward-carry: `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md` (informs scope discipline if §8 references the v1 stimulus shape)
- `CLAUDE.md` §7 forbidden vocabulary

**Commit message template:**
```
docs(status): T5 redo RD-T5-4 — analysis report §8-§10 + completion redo

Fills in the interpretation, binding-note compliance, and closure
verdict of the T5 redo analysis report. Adds the Phase 4a completion
report successor. All prose is §1.5-clean and B6-disciplined under
the RD-3 framing. Numerics in §1-§7 (RD-T5-3) are not re-edited.

Refs: docs/status/2026-05-06-t5-redo-architect-plan.md (this plan)
```

---

## §3. Dependency order

Sequential; each task gates the next.

```
RD-T5-1 (build_db.py rerun)
   ↓ (independent of T5; sequenced first to discharge R5 deferral cleanly)
RD-T5-2 (run analysis pipeline → 0.2.json)
   ↓ (numerics produced)
RD-T5-3 (numerics report §1-§7)
   ↓ (numerics report bedrock)
RD-T5-4 (interpretation §8-§10 + completion report)
   ↓
SME content verdict on the analysis report (gate chain step 3)
   ↓
Phase 4a closed at the analytical layer
```

Each task is one Coder commit. No bundling. The Reviewer pass on each commit is scope-bounded to the files changed in that commit. The Tester runs regression on each commit.

---

## §4. Open questions for the SME (Q1–Q6)

These are surfaced explicitly per the Architect routing rule. Each carries an Architect recommendation; the SME may CONFIRM, REJECT-WITH-DIRECTION, or REFINE.

### Q1 — Recompute from scratch vs. compute deltas from prior T5?

**Architect recommendation: RECOMPUTE FROM SCRATCH (writes a fresh 0.2 DomainResult; does not depend on or compute from 0.1).**

Rationale:
1. The pipeline is deterministic (modulo bootstrap RNG); recomputation against the canonical JSONL with the same parameters is the cleaner audit-trail primitive than diff-from-predecessor.
2. The bootstrap RNG seed is not currently fixed; the original 0.1 file's bootstrap CIs are not bit-identical reproducible. Computing deltas would require careful framing about bootstrap-induced delta noise vs. corpus-induced delta — a complication that recomputation avoids entirely.
3. The §7 of the redo report does compute predecessor-to-redo deltas on the headline scalar fields (n_models, consensus_score, romney_eigenratio, etc.) at report-write time, which gives the reader the comparison without the computation depending on it.

If the SME prefers computed deltas (e.g., for explicit reporting of bootstrap CI overlap between 0.1 and 0.2), I would scope it as a small extension to RD-T5-3 §7. **My current recommendation is to keep §7 as a tabular comparison only.**

### Q2 — How are legacy `thoughts_token_count=0` records handled (per Task #16 S2)?

**Architect recommendation: The pipeline does not consume `thoughts_token_count` as an analytical input; therefore the legacy asymmetry does not bias the computed measures. §8.4 of the report states this explicitly to discharge the parent T4-redo SME proactive-check-2 forward-looking concern.**

Rationale: I verified at plan-write time that `packages/cdb_analyze/cdb_analyze/pipeline.py` contains no reference to `thoughts_token_count` (Grep search: zero hits in pipeline.py and zero hits across the analyze package). The field is metadata captured for QA / decline-interview triage; it is not an input to consensus, OCI, MDS, or Procrustes per Task #16 SME Axis 2 PASS. Therefore the legacy state-(4) records (Phase 4a pre-Task-#16) and the post-recovery state-(1)/(2) records can co-exist in the analytical input without filtering.

If the SME wants an explicit filter (e.g., "drop records where `thoughts_token_count=0` cannot be disambiguated"), my Architect read is that the filter would discard most of the original Phase 4a successful corpus, which would defeat the purpose of "closing Phase 4a." I prefer the explicit-disclosure-in-§8.4 disposition. **SME ruling required.**

### Q3 — `collection_mode` filter at pipeline invocation?

**Architect recommendation: NO `--mode` filter (matches original T5 invocation).**

Rationale: The recovered records carry `collection_mode="single_pass"` (per the recovery report's pipeline conventions), the same value the original T4 records carry (per Amendment A). Filtering would not exclude any record; not filtering keeps the invocation symmetric with the predecessor T5 (the original T5 used no `--mode` per its §1.1 command line).

If the SME's read is that a `cross_model_consensus` filter (or any other) is now appropriate under the post-recovery framing, I would incorporate that into RD-T5-2's command line at the SME's direction. **Mostly procedural; the practical effect is zero.**

### Q4 — Bootstrap design: B=500 reaffirmation, Level 1 / Level 2 split?

**Architect recommendation: B=500 carries forward unchanged. No new Level 1 bootstrap pass.**

Rationale: `docs/BOOTSTRAP_DESIGN.md` §3 establishes Option 2 (annotated uncertainty) as binding for v1; the current `bootstrap_mds_ellipses()` is a Register 2 bootstrap at B=500 (matching the predecessor T5). Adding a Level 1 bootstrap pass for the redo would be scope creep and would inherit the documented "underestimates uncertainty" caveat without adding analytical value at the Phase 4a closure layer. The Phase 4b sensitivity study is the natural moment to revisit Level 1 bootstrap if motivated.

If the SME prefers a different B (e.g., B=1000 for the redo to produce tighter CIs), I would scope it as a parameter change in RD-T5-2's command line; the wall-clock impact is approximately linear (predecessor was 12m37s combined at B=500; B=1000 would be ~25 minutes — well within the 60-minute stop condition). **My default is B=500 for symmetry with the predecessor.**

### Q5 — Domain coverage: family + holidays both, with recovery-affected cells flagged?

**Architect recommendation: BOTH domains; no per-cell flagging in the DomainResult JSON. Recovery-affected cells are identifiable by `qa_notes` substring `phase4a-recovery-2026-05-05` in the source `informants.jsonl`; the report §6 names the recovery-affected cell count as a number, not as a per-cell list.**

Rationale: The DomainResult schema has no per-record flag for "produced under recovered configuration"; adding one would be a schema change and is out of scope per §1. The recovery-affected records are traceable through `data/raw/informants.jsonl` directly (Grep `phase4a-recovery-2026-05-05`), and the report §6 reports the count without per-cell enumeration. **My read is that this is sufficient transparency; flagging individual cells in the JSON would require a schema change I am not authorizing.** SME may prefer different.

### Q6 — Public-copy guardrails per B6: what specifically must T5 redo §8 prose avoid?

**Architect recommendation: Avoid (a) the original T5's "PLUS disproportionate CN-origin decline pattern" augmentation to Note E, (b) any framing that suggests the original T5 was "incorrect" or "should not have been published," (c) any cross-provider, cross-failure-mode, or cross-prompt-type generalization, (d) any claim that the analytical findings are evidence about the models' internal state. The §1.5 forbidden vocabulary applies. References to the cap-exhaustion reframe cite the RD-3 memo.**

Rationale: B6 is named in the parent T4-redo SME verdict as a CARRIES FORWARD (active) public-copy guardrail. Original T5's §8 was authored under the pre-RD-3 framing where Note K was a live forward concern; the redo's §8 is authored under the post-RD-3 framing where Note K is REPLACED. The four (a)–(d) avoidances above are my read of what B6 binds for the redo specifically. **SME may add or refine.**

---

## §5. Non-goals (explicit scope guards)

T5 redo will NOT:

- Compute new sensitivity-study (G1) statistics. Phase 4b is a separate Architect task.
- Compute Procrustes drift across model versions. Drift requires multiple version snapshots; Phase 4a does not yet have the longitudinal coverage. Forward-carry per `ARCHITECTURE.md` §4.5 / §4.2.6.
- Generate any human-baseline grounding artifacts. Phase 4c is a separate Architect task.
- Modify any prompt template or introduce a v2 free-list prompt arm. v2 is Phase 5+ per the forward-carry doc.
- Re-litigate the Note K disposition. RD-3 owns it.
- Investigate the phi-4 ×6 / gpt-5.4-mini ×2 / mistral-small ×1 unexplained failures. Separate Architect tasks.
- Generate ledes, social posts, or dashboard copy. `cdb_publish` and `apps/dashboard/` are downstream concerns. The lede generator is `cdb_publish` per `ARCHITECTURE.md` §4.2 binding constraint and CLAUDE.md §6 R12.
- Render any methodology-page UI. Phase 5/6 UI/UX-gated, with its own gate cycle.
- Edit `cdb_core/schemas.py`, `DATA_DICTIONARY.md`, `DESIGN_SYSTEM.md`, `CLAUDE.md`, `ARCHITECTURE.md`, or any prompt-template file under `packages/cdb_collect/prompts/`.
- Edit the original Phase 4a T5 0.1 JSON files, the original T5 analysis report, the original Phase 4a completion report, or any prior verdict file.
- Add or remove any test except as required to keep the regression check green (none expected; pipeline is already tested).

---

## §6. Reviewer + Tester verification surface

### Reviewer (per CLAUDE.md / `SECURITY_AND_HARDENING.md` §9 rules)

**For RD-T5-1 (build_db rerun):**
- R1 (no LLM imports in `cdb_analyze`): N/A — task does not touch `cdb_analyze`.
- R2 (append-only JSONL): N/A — task reads JSONL, writes SQLite; no JSONL modification.
- R3 (no secrets): standard scan.
- R4 (forbidden vocabulary): N/A — no prose change.
- R7 (schema/dictionary lockstep): N/A — no schema change.

**For RD-T5-2 (pipeline run):**
- R1: re-confirm no LLM imports in `cdb_analyze` (the static check should already gate this, but the Reviewer confirms).
- R2: append-only JSONL preserved (`data/raw/informants.jsonl` unchanged in this commit).
- R8 (uncertainty in viz): R11 check on the produced JSON — every bootstrap-derived field populated.
- R9 (prerequisite verdicts): this plan's SME PASS cited in the commit body.

**For RD-T5-3 (numerics report):**
- R4: forbidden-vocabulary scan on the new report file (whitelist allows `corpus lens`, `categorical structure`, `output narratives`, etc.; rejects `worldview`, `believes`, `thinks`-of-models, `cultural bias`).
- Reviewer rejects any §1–§7 sentence that interprets (vs. states) a number. The §8 placeholder must be present and explicitly labeled "Interpretation: pending RD-T5-4 commit."

**For RD-T5-4 (interpretation + completion):**
- R4: full forbidden-vocabulary scan.
- B6 public-copy guardrails: Reviewer rejects any framing that contradicts §4 Q6 above (re-checked verbatim against the SME's verdict on this plan).
- B14 numerics-vs-interpretation separation: Reviewer rejects any back-edit of RD-T5-3's §1–§7.
- R9: cite this plan's SME PASS + (when this commit lands) the gate chain step 3 dependency statement (the SME content verdict on the report comes after this commit).

### Tester (per CLAUDE.md / `tests/fixtures/`)

- All four tasks: regression-only. `uv run pytest && uv run ruff check . && uv run mypy packages/` green.
- No new fixtures, no new tests. The pipeline is exercised end-to-end on the canonical JSONL; that is integration-shape coverage but does not require a new test file.
- For RD-T5-2: confirm the produced 0.2 JSON files are loadable as `DomainResult` (`from cdb_core import DomainResult; DomainResult.model_validate_json(open('data/results/family/0.2.json').read())` succeeds).

### CDA SME content verdict (gate chain step 3)

After RD-T5-4 lands, the SME re-reviews the analysis report's §8/§9/§10 prose against:

- B6 public-copy guardrails (the §4 Q6 disposition).
- B14 numerics-vs-interpretation separation.
- §1.5 framing throughout.
- The four-axis scorecard.

Verdict file: `docs/status/2026-05-06-phase4a-t5-redo-cda-sme-content-verdict.md`. Verdict can be PASS, PASS-WITH-NOTES (with required Coder follow-up commit), or FAIL (returns to Architect for re-plan).

---

## §7. Forward carry from this plan

These items are NOT in scope for T5 redo and are documented here so they survive the plan's closure:

- **Phase 4b sensitivity study.** Adds the G1 stability gate. Per the original Phase 4a completion report §8, pre-conditions include the corpus stability T5 redo establishes. T5 redo PASS is one input to Phase 4b's go/no-go decision; the other inputs are the unexplained-failure dispositions and any v2 prompt arm.
- **Phase 4c human grounding.** No grounding for Phase 4a; ungrounded is first-class per `ARCHITECTURE.md` §1.5.5. Phase 4c onboards published baselines first, then opens researcher submissions.
- **Phase 5/6 methodology-page UI rendering.** Quotes from the RD-3 memo and from the T5 redo analysis report §8. UI/UX-gated, separate task.
- **phi-4 ×6 + gpt-5.4-mini ×2 + mistral-small ×1 unexplained-failure investigation.** Recovery report §7 items 3 + 4. Separate Architect tasks each.
- **v2 free-list prompt comparison study.** Phase 5+ candidate per `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md`. Architect schedules when corpus stability and a natural new-domain or new-slate surface arrive.
- **DeclineInterview schema gaining `thoughts_token_count`.** Task #16 SME Q5 directional preference. Backlog item.
- **Lede generation for Phase 4a results.** `cdb_publish` territory; the post-T5-redo DomainResults are an input. Separate task.
- **Drift / longitudinal Procrustes.** Multiple version snapshots required; out of scope until Phase 6+.

---

## §8. Audit-trail one-liner

This plan supersedes nothing. It is the canonical Architect plan for T5 redo, gated by the SME PASS that follows on `#lsb-cda-sme`. The original T5 (`d74ce57`), original T5 SME verdict (`3032f4a`), original T5 Reviewer verdict (`7e0a37c`), and original Phase 4a completion (`2026-04-23-phase4a-completion.md`) all stand on master as audit. T5 redo produces a new `data/results/{domain}/0.2.json` pair, a new analysis report, a new completion report. No verdict files are edited. Note K is REPLACED per RD-3 (already on master at commit `bdc06e4`-line); T5 redo prose honors that disposition.

---

*End of T5 redo Architect plan. Routes to CDA SME on `#lsb-cda-sme` for plan-level PASS or PASS-WITH-NOTES. Coder may not start RD-T5-1 until the SME verdict file exists at `docs/status/2026-05-06-t5-redo-cda-sme-plan-verdict.md` and contains a PASS or PASS-WITH-NOTES disposition. Mark's separate operator sign-off is not required (RD-3 framing is already on master under the parent plan's PASSed gate chain).*

---
