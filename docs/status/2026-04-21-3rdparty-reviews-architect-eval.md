# Architect Evaluation — Third-Party LLM Reviews

**Date:** 2026-04-21
**Scope:** `docs/3rdpartyreviews/` — Codex, Grok, Gemini
**Perspective:** Architecture. (CDA SME evaluates methodology separately.)

---

## 1. Per-reviewer evaluation

### Codex (`CODEX_INDEPENDENT_AUDIT_ASSESSMENT.md`)

**Evidence of actual reading:** Yes, genuine. Codex enumerates specific files inspected, and at least two findings reference artifacts only visible by opening the code: (i) `apps/dashboard/src/App.tsx` as a placeholder (verified — it is literally a Phase 0 placeholder `<p>` tag); (ii) `consensus_score` in `cdb_analyze/pipeline.py` as a proxy (verified — the line is annotated as such). These are not guessable from `ARCHITECTURE.md`.

**Top substantive findings:**
1. Doc-vs-impl gap with concrete citations — real credibility risk surface since public-facing text can drift ahead of shipping behavior.
2. QA threshold governance — thresholds in `scripts/qa_check.py` are justified by observed behavior in comments rather than by externally legible methodology. Not covered by `SME_REVIEW.md` or shakedown notes.
3. Proposal for a living implemented-vs-specified tracker — lightweight and would reduce the overclaim risk Codex identifies.

**Errors / misreadings:**
1. `App.tsx` placeholder flagged as credibility risk, ignoring that `ARCHITECTURE.md` §5.3 sequences dashboard build after Phase 4 validation gates — by design.
2. Finding 4 rated Medium-High despite Codex self-identifying that it did not execute the system.
3. Did not read `SME_REVIEW.md` or the shakedown-findings report. ~40% of recommendations duplicate internal status docs.

**Net verdict: MODERATE VALUE.**

### Grok (`GROK 2026-04-21-independent-third-party-review.md`)

**Evidence of actual reading:** Partial. Correct version references, correct shakedown statistics, correct section citations, accurate lede quotation. But every finding stays at doc-summary level. No code file, schema field, or function name is cited. A careful read of the docs, not the implementation.

**Top substantive findings:**
1. Researcher onboarding guide — real gap; no distilled entry point into the open data bundle.
2. External CDA researcher review of methodology page + data sample once Phase 4 passes — concrete, actionable, missing from the phase plan.
3. *(Fewer than 3 truly substantive findings.)*

**Errors / misreadings:**
1. "9.5/10" and "8.5/10" scores read as LLM sycophancy — not useful signal.
2. Conflates "documented the gap" with "closed the gap" re: shakedown-findings transparency.
3. No errors of fact. Not telling the team anything it does not already know.

**Net verdict: LOW VALUE.**

### Gemini (`gemini project_review.md`)

**Evidence of actual reading:** Weakest. No file citations, no schema references, no line numbers. Gemini correctly invokes the three-registers framing, OCI, the `cdb_analyze` LLM prohibition, and `scripts/qa_check.py`, but the review is pitched at a level that could be written about the docs alone.

**Top substantive findings:** **Zero.** Every paragraph is a paraphrase of existing architecture commitments. No gap, no risk, no concrete recommendation.

**Errors / misreadings:** None — but only because no specific claim is the ceiling on being wrong. One minor framing imprecision on "three registers" vs Register 1 / Register 2 + longitudinal drift.

**Net verdict: NOISE.**

---

## 2. Cross-reviewer synthesis

**Convergent findings (≥2 reviewers, higher-confidence signal):**
- All three praise the corpus-lens framing and language guardrails — already binding per `ARCHITECTURE.md` §1.5 and `CLAUDE.md` §7. Not actionable.
- All three praise raw-data provenance (`InformantRecord`, SHA256, append-only JSONL). Not actionable.
- Codex + Grok both flag the doc-vs-implementation gap. **This is the only convergent actionable finding.** Already being worked via the post-F1 SME implementation sequence and the current F-batch.

**Contradictions:** None substantive. Codex rates overall maturity lower; Grok more laudatory. The difference tracks how much code each one read.

**Common blind spots across all three:**
- **None evaluated the agent pipeline as an engineering system.** The six-agent pipeline with CDA SME and UI/UX gates is either ignored (Codex), praised abstractly (Grok), or not mentioned (Gemini). None asked whether the gating actually stops drift or creates process theater.
- **None questioned two-level bootstrap design or G1/G2/G3 gate thresholds** — the hardest methodological calls. Exactly where an independent reviewer could add value. All three skirted them.
- **None evaluated `PHASE_4C_CANDIDATE_SOURCES.md` or the grounding submission workflow** — the most novel and most-likely-to-fail community-process piece.

---

## 3. Architectural impact

**New F-batch tasks warranted:** One, at **low priority**:
- **Researcher onboarding guide for the open data bundle** (Grok Recommendation 2). Distilled entry point into `DATA_DICTIONARY.md` and the JSONL→SQLite rebuild path. Sequenced after Phase 4 gates pass so examples reflect real results.

**Not warranted as new work:**
- Implementation-vs-specification tracker — existing shakedown-findings report + post-F1 implementation memo already serve this function.
- QA threshold governance — under CDA SME purview; deferred to Phase 4 validation writeup.
- External CDA researcher review — belongs on the post-Phase-4 roadmap.

**No revision to `ARCHITECTURE.md` §5.3 phase plan is warranted.**

---

## 4. Overall project-level verdict

**Is the triad worth the reading effort?** Marginally. Codex earns its keep by reading code and surfacing two real diagnostic observations. The other two are doc-summary exercises.

**Going-forward recommendations:**

1. **Retire Gemini-style reviews.** Docs-only reviews from a frontier LLM produce near-zero signal — no adversarial incentive, and the project's docs are already unusually thorough.

2. **When soliciting external-LLM review, require the reviewer to touch code.** Codex's review demonstrates that a scoped reading list (`pipeline.py`, `schemas.py`, `qa_check.py`, shakedown findings, grounding workflow) produces qualitatively better findings. Without that anchor, reviews collapse to paraphrase.

**Usage pattern:** Read-once-and-archive. Do not cross-reference on every major decision. Authoritative sources remain Mark → CLAUDE.md binding rules → CDA SME verdicts.
