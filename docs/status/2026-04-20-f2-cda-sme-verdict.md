# F2 Shakedown-Findings Batch 2 — CDA SME Verdict

**Date:** 2026-04-20
**Reviewer:** CDA SME (external)
**Scope:** T01–T10 (T06, T08 skip SME gate)
**Channel:** `#lsb-cda-sme` (simulated — saved to repo per save-to-repo preference)
**Ground truth read:** ARCHITECTURE.md §1.5 and §4.2.0, docs/SME_REVIEW.md §1.1/§1.3/§1.5/§1.6/§1.7, schemas.py (ConsensusType + truncation_type Literal), consensus.py (classify_consensus, compute_centrality_scores), gates.py (g1_stability_split, G1SplitResult), sensitivity.py, runner.py `_assemble_record`.

## Batch verdict

**PASS-WITH-NOTES.** All nine tasks describe legitimate pipeline wiring of already-SME-approved methodology. No new statistical method is introduced; no claims envelope expands. Notes are cross-task dependencies and one numerical-threshold clarification.

## Per-task scorecards

### T01 — Wire `classify_consensus` dispatch
| Axis | Verdict | Rationale |
|---|---|---|
| Protocol validity | PASS | Dispatch only; Caulkins & Hyatt typology already SME-approved in §1.6. |
| Analytical validity | PASS-WITH-NOTES | `classify_consensus(eigenratio, centrality_scores, *, observed_variance=None)` — T01 strictly depends on T02 (eigenratio) and T03 (centrality). Confirm: yes, T01 blocks on T02 + T03. |
| Claims validity | PASS | Six-state output, DETERMINISTIC reserved — matches published typology. |
| Audience translation | PASS | Labels are Caulkins's own terms; dashboard copy layer not in scope of T01. |

### T02 — Wire Romney CCM eigenratio
| Axis | Verdict | Rationale |
|---|---|---|
| Protocol validity | PASS | Register 2 only (between-model), with LSB caveats. |
| Analytical validity | PASS-WITH-NOTES | At n=4 shakedown, λ₁/λ₂ is unstable — sampling variance dominates. Require `n_informants_warning` flag set when n_models < 8 (mirrors §1.1 small-n rationale). Dual-threshold (5.0 op / 3.0 classic) still evaluated, but shakedown is not a scientific consensus claim — it's a wiring smoke test. Annotate `romney_consensus_pass` with "diagnostic-only at n=4" in qa_notes or a new `romney_small_n_warning` bool. |
| Claims validity | PASS | No public claim emerges from n=4; the threshold plumbing is what T02 validates. |
| Audience translation | PASS-WITH-NOTES | Any dashboard copy drawn from a shakedown-corpus DomainResult must suppress consensus labels. Out of T02 scope but flag for T10 re-shakedown reporting. |

### T03 — Wire cultural_centrality_scores
| Axis | Verdict | Rationale |
|---|---|---|
| Protocol validity | PASS | Models-as-informants, Register 2. |
| Analytical validity | PASS | First-eigenvector formulation of the symmetric model-model similarity matrix is the one I want. `compute_centrality_scores` already uses `np.linalg.eigh` with sign-fixing convention (positive mean loading) — this is correct and matches Caulkins (1999). **Do not** normalize to [0,1]; the sign is load-bearing for SUBCULTURAL/CONTESTED detection. The existing implementation preserves raw loadings — keep this. |
| Claims validity | PASS | "Cultural centrality" per Caulkins, not "competence" — already in docstring. |
| Audience translation | PASS | Negative = "opposes dominant structure," not "wrong" — existing docstring is correct. |

### T04 — Populate `truncation_type`
| Axis | Verdict | Rationale |
|---|---|---|
| Protocol validity | PASS | §1.7 SME requirement. |
| Analytical validity | PASS | Current enum `{"elbow", "capacity", "prompt_ceiling", "context_window_exceeded"}` is sufficient. **No new labels needed** — T04 scope does not expand. The enum already covers the four LSB-relevant termination modes. |
| Claims validity | PASS | `context_window_exceeded=True` is a finding, not a QA failure — already documented in schema comment. |
| Audience translation | PASS | Labels are internal; dashboard copy layer is downstream. |

### T05 — Wire split G1
| Axis | Verdict | Rationale |
|---|---|---|
| Protocol validity | PASS | Split into salience + spatial per §1.3; both functions exist. |
| Analytical validity | PASS-WITH-NOTES | Threshold: **0.5 for each axis**, confirmed by the default in `g1_stability_split(threshold=0.5)` and matching §1.3 ("both_below_threshold(0.5)"). Both axes must pass (`g1_pass = salience_pass AND spatial_pass`). Architect does not need to set a new number — SME threshold is 0.5. Aggregate is reported for continuity but is **not the binding metric**. |
| Claims validity | PASS | Two-axis reporting is more informative than aggregate; matches §1.3 intent. |
| Audience translation | PASS | Salience vs. spatial naming is self-explanatory to skeptical reader. |

### T07 — Honest `qa_passed` assignment
| Axis | Verdict | Rationale |
|---|---|---|
| Protocol validity | PASS | Hardcoded `qa_passed=True` at runner.py:183 violates commitment 8 (software-only QA). |
| Analytical validity | PASS-WITH-NOTES | `cdb_analyze.pipeline.load_records` already has `qa_only: bool = True` default (pipeline.py:63) — records with `qa_passed=False` are filtered by default. This is the correct policy: **default-exclude from analysis, retain in raw lake for audit.** No change to load_records needed. T07 just needs the runner to call `check_record` and propagate the result; the filter policy is already right. |
| Claims validity | PASS | False records still written to JSONL with `qa_notes` — audit trail intact. |
| Audience translation | N/A | Internal plumbing. |

### T09 — Label-count mismatch policy (SME decision)
See below.

### T10 — Re-shakedown verification
| Axis | Verdict | Rationale |
|---|---|---|
| Protocol validity | PASS | Re-run at N=5 is the right sample for a wiring smoke test. |
| Analytical validity | PASS-WITH-NOTES | Checks 1, 2, 5, 7, 8 passing is necessary but not sufficient for Phase 4a greenlight — it only validates that the pipeline now *produces* the fields. It does not validate the numerical correctness of the fields at scale. Phase 4a at full N still requires §8 checks to hold on the real corpus. |
| Claims validity | PASS | No public claim from T10; it's a gate. |
| Audience translation | N/A | Internal gate. |

## T09 — Label-count mismatch policy (my call)

**Pick: (b) Fail — mark `qa_passed=False` with `qa_notes="label_count_mismatch:<n_piles>/<n_labels>"`; record still written for audit.**

**Reasoning (200 words):**

The pile-interview step is the most architecturally sensitive part of the LSB protocol (per SME §2.3 — pile labels are a primary future-architecture discriminator). Padding silently (option a) fabricates informant data: an `unlabeled_1` token that never appeared in the model's output becomes indistinguishable, downstream, from a label the model actually produced. This violates commitment 1 (raw-first, analysis-second) and commitment 7 (cryptographic provenance) — the SHA256 manifest covers the verbatim response, but an injected `unlabeled_1` is not in the verbatim response. Option (c) re-prompting crosses the line from measurement into coaxing — we are measuring what the model produces, not what it produces after we nudge it N times. Re-prompting introduces a confound: the model's second attempt is conditioned on having just failed, which is no longer a clean sample from the output distribution.

Option (b) preserves the audit trail (record still written, raw verbatim response intact), excludes the record from analysis (pipeline.load_records default filter), and treats the mismatch as the data it is. A model that can't align its label count to its pile count is telling us something about its architecture — that is the signal, not an error to paper over.

## Cross-task dependencies the Architect's plan may have missed

1. **T01 depends on T02 and T03.** `classify_consensus` requires both `eigenratio` (T02) and `centrality_scores` (T03). Sequencing: land T02 + T03 before T01, or land all three in one PR. The plan should state this explicitly.
2. **T02 needs a small-n annotation field or qa_note.** At n=4 shakedown, a dual-threshold pass is statistically meaningless. Either add `romney_small_n_warning: bool` to `DomainResult`, or have the runner write a qa_note when n_models < 8. I'll accept either; Architect picks.
3. **T05 requires Phase 4b-style variant collection to actually fire.** Without multi-prompt-version records per model, `g1_stability_split` has nothing to compute. The shakedown protocol produces variant records only in the sensitivity cell — confirm T10 re-shakedown includes the sensitivity cell, or split G1 will be N/A on re-run and §8 check 8 cannot pass.
4. **T07 + T09 interact.** T09's option (b) sets `qa_passed=False` with `qa_notes="label_count_mismatch:..."`. T07 wires `check_record` to `qa_passed`. Confirm `check_record` detects label-count mismatch, or T09's policy needs its own dedicated check function. I recommend adding `check_8_label_count_match` alongside the existing check_1–check_7 battery in `scripts/qa_check.py`.
5. **T04 truncation_type propagation path.** Schema allows four Literal values + None. The runner currently passes nothing; truncation is decided in `run_two_pass` (`find_salience_elbow` → `elbow_k`) and potentially in the adapter layer on `context_window_exceeded`. T04 needs both sources wired, not just the elbow path. The plan should name both.

## Vocabulary + register compliance

All tasks describe pipeline plumbing; none generate public-facing text. Vocabulary compliance: PASS (no generated copy). Register compliance: PASS (Register 1 OCI untouched; Register 2 RWB CCM applies at between-model, which is what T02 does; §1.5.3 forbidden "within-model CCM" not triggered).

## Summary line for the channel

CDA SME — F2 batch PASS-WITH-NOTES (9/9 tasks). T01 blocks on T02+T03. T02 needs small-n annotation at n=4 shakedown. T05 threshold is 0.5 per axis (both must pass). T04 enum is sufficient, no scope expansion. T07 filter policy at load_records already correct. **T09 policy: option (b) FAIL with qa_notes, record still written for audit — padding fabricates informant data, re-prompting introduces a confound.** T10 re-shakedown must include the sensitivity cell for split G1 to fire.
