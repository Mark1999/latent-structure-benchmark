# Post-F1 SME implementation — six-PR sequence state

**Date:** 2026-04-19
**Status:** All six PRs pushed to GitHub against `master`; none merged yet
**Companion docs:** `docs/SME_REVIEW.md` (authoritative SME review), `docs/BOOTSTRAP_DESIGN.md`, `docs/briefings/2026-04-19-sme-implementation-response.md` (external-facing SME response), `ARCHITECTURE.md` §1.5.5, §4.2.0, §4.2.7, §5.3 Phase 4b

---

## 0. What this document is

Internal project-status record for the six-PR sequence implementing the external SME's recommendations in `docs/SME_REVIEW.md`. It sits alongside the external-facing summary at `docs/briefings/2026-04-19-sme-implementation-response.md` (which addresses the SME directly) and captures the operational detail a future contributor or a future Claude Code session needs to pick up the thread: which PRs exist, how they depend on each other, what was deferred, what was left open for the next SME cycle, and the binding rules that followed from the review.

User gave blanket authorization on 2026-04-19 (standing authorities: framing reversal accepted, Architect sign-off pre-granted for schema PRs, specific saturation-analysis reference models pre-specified).

---

## 1. The six PRs in order

| # | Branch | Commit | Scope |
|---|---|---|---|
| 1 | `docs/framing-reversal-three-registers` | `788144b` | ARCHITECTURE.md rewrite: framing reversal in §1.5.5 / §4.2.5 (humans are contextual reference points, not the ceiling), four-layer corpus lens, §4.2.0 three-registers section with R1a/R1b, methods adaptation table, Phase 4b runbook note, forbidden vocab for OCI naming, `LSB_SME_REVIEW.md` → `SME_REVIEW.md` rename, briefing §7.9 update |
| 2 | `chore/analyze-ari-deterministic` | `137850f` | G3 binding metric switched to ARI (threshold 0.6); Rand retained in `secondary_metrics`; `ConsensusType` Literal declared locally in `gates.py` with all six values |
| 3 | `docs/bootstrap-design-note` | `323a85a` | `docs/BOOTSTRAP_DESIGN.md` specifies the Option 2 (annotated uncertainty) contract, Level 1 underestimation caveat, dashboard UI handoff |
| 4 | `feat/schema-domain-result-additions` | `d7df731` | `DomainResult` + `GroundingRef` SME additions, `ConsensusType` canonicalized in `cdb_core`, `SutropCSI` / `MantelPair` / `NolanIndexPair` / `WithinModelResult` types, cultural centrality + `classify_consensus` functions, 22 new tests, `DATA_DICTIONARY.md` update |
| 5 | `feat/informant-capacity-fields` | `28cda9b` | `InformantRecord` capacity-constrained truncation fields (`truncation_type`, `truncation_n`, `max_possible_n`, `context_window_exceeded`, `capacity_note`); `context_window_exceeded=True` is a finding, not a QA failure |
| 6 | `feat/two-level-pipeline` | `5786037` | `run_within_model_analysis()`, `options_for_level_two()`, saturation curve runner + `identify_knee()`, `ARCHITECTURE.md` §4.2.7. Branched off PR #4 for the `WithinModelResult` schema dependency |

Each branch pushed to origin; PR URLs are the usual `github.com/Mark1999/latent-structure-benchmark/pull/new/<branch>` paths. `gh` CLI not installed on this host, so the PR objects themselves are opened from the browser.

All six branches pass the full check suite: 307 unit tests, ruff clean, mypy clean, no-LLM-imports static check clean.

---

## 2. Merge-ordering constraints

Two real dependencies and one cosmetic overlap:

1. **PR #4 before PR #6** (hard dependency). PR #6 imports `WithinModelResult` from `cdb_core`, which is introduced in PR #4. PR #6 is branched off `feat/schema-domain-result-additions` precisely so the schema is available during development; the branch rebases cleanly onto master once PR #4 merges.
2. **PR #2 and PR #4 both declare `ConsensusType`** (cosmetic overlap). PR #4 canonicalizes the Literal in `cdb_core` (the correct architectural home — avoids circular imports between `schemas.py` and `cdb_analyze.gates`). PR #2 has a local copy in `gates.py` because at the time PR #2 was written, PR #4's canonical declaration did not yet exist on any branch. After both merge, a small follow-up consolidates by removing the `gates.py` declaration and importing from `cdb_core`. No merge-time conflict; they edit different files.
3. **PR #1 and PR #6 both edit `ARCHITECTURE.md`** but non-overlapping sections. PR #1 adds §1.5.1 four-layer breakdown, §1.5.4 vocab rows, §1.5.5 rewrite, §4.2.0 three-register section, §4.2.5 rewrite, §5.3 Phase 4b runbook. PR #6 adds §4.2.7 two-level-pipeline reference. Forward references from PR #1's §4.2.0 and §5.3 to §4.2.7 resolve once PR #6 also merges.

The dangling `chore/docs-infra-pivot-2026-04-19` branch (commit `938b0b7`) from an earlier session is unrelated to this sequence and unchanged.

---

## 3. Deferred by design (not gaps)

These were flagged, agreed with the SME, and intentionally left for later:

- **G1 split** (SME §1.3 — salience stability vs spatial stability as separate diagnostics). Logical follow-up refactor to `sensitivity.py`; did not fit cleanly inside the six-PR bound without expanding scope.
- **Pile-label consistency** (SME §2.3, no-embeddings AI-free implementation). Defers alongside the full label-parsing pipeline work.
- **Methodology page drafting.** Phase 5/6 deliverable. Mark writes or reviews personally per `ARCHITECTURE.md` §1.5.6; the Coder agent should not template this.
- **Actual saturation-study data collection.** Analytical machinery is in place (PR #6), but the sweep requires real API spend and the B2 backup layer being active first per `docs/INCIDENTS/2026-04-19-test-data-loss.md` §5.1.
- **No-ceiling free-list experiment** (SME §3.1). Budget-gated; runs as a parallel methods-validation study, not on the Phase 4 critical path.
- **16+ prompt variants** (SME §5.3). Phase 2. The 8-variant default is the starting point; expand only if G1 is borderline and the expansion is needed per the Phase 4b runbook rule.
- **Nested bootstrap (Option 1) for Level 2 variance propagation.** Deferred on compute-cost grounds (~120,000 pipeline runs per domain at B=500 × N=20 × 12 models). `BOOTSTRAP_DESIGN.md` §6 commits to revisiting when the operational N from the saturation analysis makes the arithmetic feasible.
- **INDSCAL and RCA/CCA** — explicitly Phase 2 per the SME review itself.

---

## 4. Open questions flagged for the next SME cycle

Surfaced in `docs/BOOTSTRAP_DESIGN.md` §7, commit bodies, and `docs/briefings/2026-04-19-sme-implementation-response.md` §3. Priority order:

1. **Low-OCI ellipse-suppression cutoff.** Provisional threshold: OCI < 3.0 on the concentration scale (models below this get their Register 2 point rendered without a confidence ellipse, just an annotation). Final value wants the saturation-analysis data before it's fixed.
2. **Saturation-N interaction with compute budget.** Once operational N is known, should Register 1 bootstrap use that N or a smaller N to reduce compute? Default position is "use operational N."
3. **Human-OCI bootstrap treatment.** For researcher submissions with `pile_sort_raw.csv`, current plan is to resample subjects with replacement — but a purposive or convenience sample carries the **opposite**-direction underestimation caveat from the model case. "Annotate and move on" vs a formal correction — SME judgment needed.
4. **G2 semantics renamed not replaced.** Per Q5 resolution the G2 dispersion-permutation test is kept as the binding gate and Mantel added as a parallel pairwise measure. G2 measure renamed to "inter-model similarity dispersion permutation test" in docstrings. Confirm this rename is the right level of disambiguation rather than a more substantive restructuring.
5. **"Mismatch is the finding" on the methods page.** Binding rule added to `ARCHITECTURE.md` §1.5.6 that this framing leads the public methods page's first paragraph. SME to verify the eventual draft actually delivers on the framing.

---

## 5. Binding rules that followed from this review

These apply to every future PR in this project and are surfaced in `ARCHITECTURE.md`, `docs/SME_REVIEW.md`, and `docs/BOOTSTRAP_DESIGN.md`. Repeated here as a checklist:

- **Framing.** Human baselines are contextual reference points, not the target of measurement. Primary scientific claim is comparative across model architectures and across time.
- **Vocabulary.** No "within-model consensus," "within-model cultural consensus," "within-model eigenratio," "within-model CCM." The Register 1 measure is the **Output Concentration Index (OCI)** with the `underestimates_uncertainty=True` caveat on every result object and on every dashboard display.
- **QA decoupling.** `context_window_exceeded=True` does not set `qa_passed=False`. The schema does not couple them; the QA_Runner does not gate on it. Context-window truncation is a finding about the architecture's categorical-processing capacity.
- **Two-level inputs.** Level 2 receives Option A (pooled consensus free list) as equal voice for all models regardless of OCI. Option B (centroid run) is dashboard display only, never an analytical input. Option C (OCI-weighted) is a diagnostic only, never an alternative between-model map.
- **Phase 4b runbook.** G1 failure in the 0.4–0.6 borderline range triggers prompt-variant expansion before domain disqualification. Disqualification requires G1 failure *after* expansion plus an explicit Architect diagnostic.
- **Methods page.** The "mismatch is the finding" framing leads the first paragraph. Reviewer rejects drafts that bury it.
- **Grounding in Register 2.** Human baselines enter the cross-model MDS with a distinct visual marker; never scored against. When a researcher submission includes `pile_sort_raw.csv`, `human_oci` may be populated on `GroundingRef` — comparable to model OCI on the concentration scale, not on any human-as-ground-truth axis.

---

## 6. How to pick up this thread in a future session

- Start at `docs/SME_REVIEW.md` to understand what the external SME requested.
- Read this file to see which of the 1–6 PRs above it builds on; if dependencies are still unmerged, branch appropriately (as PR #6 was branched off PR #4's branch).
- Read `docs/briefings/2026-04-19-sme-implementation-response.md` for the user-facing summary — that file is what goes to the SME for their next review cycle.
- Read `docs/BOOTSTRAP_DESIGN.md` before any PR that touches `packages/cdb_analyze/cdb_analyze/bootstrap.py` or adds bootstrap calls anywhere in the analysis layer.
- If the work touches `cdb_core/schemas.py`, follow CLAUDE.md Reviewer rule 5: same-PR `DATA_DICTIONARY.md` update.

---

*This document is the in-repo counterpart of the project-memory file at `memory/project_post_f1_sme_implementation.md`. They contain the same substantive content; the in-repo version is visible in the working directory, the memory version loads automatically into future Claude Code sessions.*
