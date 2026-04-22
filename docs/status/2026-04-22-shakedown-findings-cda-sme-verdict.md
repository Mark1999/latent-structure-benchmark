# 2026-04-21 Shakedown Findings — CDA SME Verdict

**Date:** 2026-04-22
**Reviewer:** CDA SME (agent)
**Scope:** `docs/status/2026-04-21-shakedown-findings.md` (137 lines) as the final methodological gate on Phase 4a kickoff
**Channel:** `#lsb-cda-sme` (saved to repo per preference)
**Ground truth read:** `CLAUDE.md` §1.5, `ARCHITECTURE.md` §1 commitments + §1.5 framing + §4.2 + §4.5 + §5.3 Phase 4 runbook, `docs/SHAKEDOWN_PROTOCOL.md` §1 and §10, `docs/status/2026-04-20-f2-cda-sme-verdict.md`, `docs/SME_REVIEW.md`, `docs/BOOTSTRAP_DESIGN.md` §2, and the relevant code: `packages/cdb_analyze/cdb_analyze/consensus.py`, `gates.py`, `pipeline.py`.

**Preceding gates satisfied:**
- B2 backup layer Active as of 2026-04-22 (commits `0c54901`…`c8cf32b`; canary test-restore PASS at `docs/status/2026-04-22-b2-test-restore.md`).
- F2 batch PASS-WITH-NOTES issued 2026-04-20 at `docs/status/2026-04-20-f2-cda-sme-verdict.md`.

---

## Verdict: **PASS-WITH-NOTES**

### Four-axis scorecard

| Axis | Verdict |
|---|---|
| Protocol validity | **PASS** |
| Analytical validity | **PASS-WITH-NOTES** |
| Claims validity | **PASS-WITH-NOTES** |
| Audience translation | **PASS** |

| Compliance | Result |
|---|---|
| Register compliance | PASS |
| Vocabulary compliance | PASS |

**Phase 4a is unblocked from the CDA SME gate.** Four forward notes follow; none must fire before Phase 4a.

---

## 1. Did the F2 implementation faithfully discharge the 2026-04-20 notes?

Yes, with one documentation artifact worth noting.

- **T02 `romney_small_n_warning`** — faithful. The 2026-04-20 note required the flag set when `n_models < 8` (mirrors SME §1.1 small-n rationale). Findings §1 row 2 and §3 Check 2 report the flag fires True on 4/4 WMRs at `n_models=4`. Correct wiring.

- **T01 `consensus_type` dispatch** — faithful. DETERMINISTIC is correctly reserved; verified at `packages/cdb_analyze/cdb_analyze/consensus.py:396-397` (requires `observed_variance < 1e-9`). The primary cell ran at T=0.7; STRONG_CONSENSUS is the correct classification. The determinism cell ran at T=0.0 but on a transformer — per `SHAKEDOWN_PROTOCOL.md` §4, T=0 on a transformer should not trip DETERMINISTIC, and the findings report does not claim it did.

- **T03 sign preservation** — faithful in the code (`consensus.py:270-273` docstring: "Raw loadings are preserved (not normalized to [0, 1])"; `consensus.py:294-297` sign-fix convention per mean-loading-positive). **Note 3 below** flags a stale module-level docstring.

- **T04 `truncation_type`** — the "None is semantically correct" defense is **sound for this shakedown**. All 108 records are `single_pass`, so the elbow path is architecturally unreachable; no adapter returned a length-class `finish_reason`, so the context-window path is architecturally unreachable. `None` is the correct value for "no truncation occurred"; populating it with `"elbow"` on an untruncated record would be a category error. The `"elbow"` label path is not empirically validated on real data until a `--mode two_pass` shakedown fires it — see **Note 1 below**.

- **T05 split G1** — faithful. Family `DomainResult` reports distinct `salience=0.5481` (pass=False) and `spatial=0.1604` (pass=True) with `overall=False`, matching SME §1.3 intent (both axes must pass for overall=True).

## 2. Framing safety per §1.5

Scanned in full. No forbidden vocabulary (`worldview`, `believes`, `thinks` applied to models, `cultural bias` standalone, etc.). No framing of ungrounded/absent states as defects. The document self-scopes at line 4 ("Findings are about the pipeline, not about the models") and reinforces at line 85 ("Shakedown N is too small to support any claim"). Protocol validity and audience translation both PASS on this axis.

## 3. §3 Check 5 "coherent corpus-lens structure" framing

The phrase "the four frontier models exhibit a coherent corpus-lens structure" is on the edge. "Exhibit" is a descriptive observation verb, not a claim verb; "corpus-lens structure" is the approved §1.5.1 vocabulary. The sentence is immediately qualified: "Shakedown N is too small to support any claim (§1 of `SHAKEDOWN_PROTOCOL.md`), but the pattern is consistent with Phase 4a's hypothesis."

The qualifier is **adequate for this document** because it is an internal findings report, not public-facing dashboard copy or a lede. In a dashboard lede, I would fail the same sentence. In an internal-only diagnostic report with explicit shakedown framing in the header, the disclaimer neutralizes it. PASS on claims validity **with Note 4** as a copy-discipline watchpoint for downstream artifacts.

## 4. §3 Check 7 G1 borderline interpretation

The findings invoke `ARCHITECTURE.md` §5.3 Phase 4b runbook to justify the "not a project-level G1 failure" disposition at `g1_salience_stability=0.5481`. This is **defensible but methodologically generous**. The runbook paragraph cited is scoped to Phase 4b (the canonical saturation sweep), not to pre-Phase-4a diagnostic runs. The findings extend its "add variants, don't disqualify" logic to a single-model single-domain sensitivity cell at N=5 with 8 variants.

The **mechanism** (borderline G1 reflects sampling variance, addressable by more variants) generalizes correctly. The **disposition** (shakedown findings are diagnostic, not gate-enforcing) is already guaranteed by `SHAKEDOWN_PROTOCOL.md` §1 without the §5.3 appeal — the shakedown framing already does the work. The §5.3 citation is ornamental and slightly overreaches. **Note 2** captures this.

## 5. "F2 is validated, pipeline is ready for Phase 4a" (findings §6)

Supportable. No methodological concerns block Phase 4a beyond the forward concerns already captured in the deferred list and in the notes below. Required preconditions:

1. ✅ B2 backup layer Active — satisfied 2026-04-22.
2. ✅ CDA SME review of findings — this verdict.
3. Shakedown data deletion per `SHAKEDOWN_PROTOCOL.md` §10 — pending Mark, not SME.

## 6. Deferred items in findings §6

Both appropriate to defer. Neither is methodologically load-bearing for Phase 4a:

- Moving `run_qa_checks` to `cdb_collect.qa` is a packaging hygiene fix. The in-flight defensive `sys.path` fix (commit `adb4090`) is adequate in production.
- Exercising `--mode two_pass` to fire the elbow label on real data is a future verification opportunity. Phase 4a runs in `single_pass` by default; the elbow-label code path has unit-test coverage.

---

## Notes (all Phase-4a-compatible forward concerns)

### Note 1 — T04 `"elbow"` label untested on real data

The T04 `"elbow"` label path has unit-test coverage but has never been exercised on real collected data. Phase 4a in `single_pass` mode will not exercise it either. At the next opportunity that `--mode two_pass` is warranted (e.g., a Phase 4b saturation sweep, or a domain where the context window constrains the free list), verify the elbow label actually populates on real records. Tracking in findings §6 deferred list is adequate.

### Note 2 — §3 Check 7 appeal to §5.3 runbook

The Check-7 paragraph stretches the ARCHITECTURE.md §5.3 Phase 4b runbook beyond its stated scope. No action required on the findings doc — it is an internal report — but if the 0.5481 sensitivity-cell value ever gets cited in a Phase 4a retrospective, on a methods page, or in any public-facing artifact, frame it as a **shakedown-scope diagnostic**, not as a Phase-4b-runbook trigger. `SHAKEDOWN_PROTOCOL.md` §1 already guarantees the correct framing; the §5.3 citation is ornamental and slightly misleading.

### Note 3 — Stale docstring at `consensus.py:13`

The module-level blurb at `packages/cdb_analyze/cdb_analyze/consensus.py:13` still contains "[0, 1] normalized" language for centrality scores. The function docstring and the code both correctly preserve sign (verified at lines 270–273 and 294–297). The module-level blurb is a documentation artifact, not a behavioral defect. Clean up at the next routine edit to that file. Not a blocker.

### Note 4 — Copy-discipline watchpoint on "coherent corpus-lens structure"

The §3 Check 5 observation ("remarkably tight centrality values" / "coherent corpus-lens structure") is disclaimer-protected here but **must not migrate verbatim into any public-facing or semi-public artifact**. The four-model `n` is below both the SME §1.1 small-n threshold and Romney's classic n=10. If Phase 4a at n=12 reproduces the pattern, dashboard copy can describe it — with uncertainty. The shakedown numbers themselves are not citable per `SHAKEDOWN_PROTOCOL.md` §3. Tag this as a **copy-discipline watchpoint** for the Phase 4a lede-generation handoff.

---

## Disposition

**Phase 4a is unblocked from the CDA SME gate.**

The F2 implementation faithfully discharged the five findings from the 2026-04-20 cycle. The pipeline produces all §8-audit fields with correct semantics. Small-n and shakedown-scope disclaimers are present and adequate throughout the findings report. All four axes pass; analytical validity and claims validity carry forward notes, none of which must fire before Phase 4a.

**Required before Phase 4a kickoff (from this verdict):** none.

**Required before Phase 4a kickoff (from the protocol):** Proceed per `SHAKEDOWN_PROTOCOL.md` §9–§10 — delete `data/shakedown/shakedown-20260421/` from the Surface dev host, retain the private-repo off-host copy through Phase 4d, then purge.

---

*End of verdict. `docs/status/2026-04-22-shakedown-findings-cda-sme-verdict.md`.*
