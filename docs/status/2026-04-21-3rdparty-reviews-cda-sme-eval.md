# CDA SME Evaluation of Third-Party LLM Reviews

**Date:** 2026-04-21
**Reviewer:** CDA SME
**Scope:** Methodological value of three outside-LLM reviews in `docs/3rdpartyreviews/`
**Verdict authority:** Advisory. This evaluation does not override any binding CDA SME ruling.

---

## 1. Per-reviewer four-axis scorecards

### 1.1 Codex (`CODEX_INDEPENDENT_AUDIT_ASSESSMENT.md`)

| Axis | Verdict | Notes |
|---|---|---|
| Protocol validity | PASS-WITH-NOTES | Correctly describes models as "informants for measurement purposes only" (§What the Project Is Doing Well #1, line 88) and correctly names the three CDA steps are captured verbatim in `InformantRecord` (line 111). Never confuses this with running the LLM as a subject of cognition. Does not engage with the free-list / pile-sort / pile-interview distinction by name; engages at the architectural layer only. |
| Analytical validity | FAIL | Names "consensus," "grounding," and "uncertainty" only at the wrapper level. Does not touch OCI vs. Romney CCM, Smith's S vs. Sutrop CSI, Caulkins typology, G1/G2/G3 gates, or bootstrap Level-1 underestimation. Finding 5 correctly flags that QA thresholds need empirical ownership (lines 220-232) — this is a real audit instinct but is applied to `scripts/qa_check.py` thresholds, not to the analytical thresholds (G1 0.5, G2 p<0.01, G3 ARI≥0.6) where it would matter more. |
| Claims validity | PASS | Finding 3 (lines 184-196) is the strongest single paragraph in any of the three reviews: "The danger is not in the current docs. The danger is in future copy, UI text, social sharing, and convenience summaries." This correctly identifies that §1.5.4 enforcement is a *shipping-surface* problem, not a docs problem. Priority 5 (lines 428-444) operationalises this. |
| Audience translation | PASS | Distinguishes methodological SMEs, technical AI SMEs, and AI-reviewer systems (lines 322-369) with differentiated predictions rather than "approachable language is good." Finding 7 (lines 258-270) names concrete audiences (alignment/safety teams, HCI researchers, journalists, policy analysts) and rejects the "which AI is best?" leaderboard framing. |

**Overall: MODERATE VALUE.** Codex is the only reviewer functioning as an auditor rather than an endorser. The "implemented vs. specified" framing (Priority 1, lines 380-390) and the shipping-surface copy-review framing (Priority 5) are genuinely useful — they align with the existing `§1.5.4` vocabulary enforcement but extend it to a launch-gate posture the project does not currently have written down. Weakness: no engagement with the specific methodological machinery. If you wanted this reviewer to flag that G1 split is un-deferred, or that Romney at n=12 is small-n, you would not get it.

### 1.2 Grok (`GROK 2026-04-21-independent-third-party-review.md`)

| Axis | Verdict | Notes |
|---|---|---|
| Protocol validity | PASS-WITH-NOTES | Correctly uses "as if" framing (line 34) and calls the "mismatch is the finding" principle "one of the most intellectually honest statements I've encountered in AI evaluation literature" (line 35). Does not engage with free-list / pile-sort / pile-interview at all. Treats the protocol as a solved problem the team has already described well. |
| Analytical validity | FAIL | Mentions Register 1/Register 2 (line 22), bootstrap B=500, eight prompt variants, and G1-G3 exist (line 20) — but only by restating what `ARCHITECTURE.md` says. No engagement with any threshold, no engagement with Sutrop CSI, Caulkins, negative centrality, small-n Romney. The sentence "appropriate visual encodings shows sophisticated understanding of what different statistical approaches actually measure" (line 22) is a paraphrase of the architecture, not an assessment of it. |
| Claims validity | PASS | Correctly catches the v0.7 reframing of human baselines from "ceiling" to "reference point" (line 36) and flags it as the right move. |
| Audience translation | PASS-WITH-NOTES | Recommendation 2 (line 75) correctly flags that documentation density may block external researchers engaging with the open-data bundle — real and testable. Rest is generic praise. |

**Overall: LOW VALUE.** Grok delivers a well-calibrated endorsement ("8.5/10") with almost no methodological engagement. It scores the project by reading the architecture back and adding "excellent" to each section. The one concrete recommendation (researcher-onboarding guide, line 75) is useful but generic. It catches zero defects.

### 1.3 Gemini (`gemini project_review.md`)

| Axis | Verdict | Notes |
|---|---|---|
| Protocol validity | PASS-WITH-NOTES | Correctly names the "corpus lens" construct and correctly rejects the belief/cognition/worldview framing (line 14). Does not engage with the three CDA steps. |
| Analytical validity | FAIL | One genuine methods-layer sentence (line 8): correctly names OCI as within-model sampling concentration, correctly identifies Romney/Weller/Batchelder applies only in Register 2, correctly notes the mathematical-appropriateness distinction. That sentence is the only methods content in the entire review. No engagement with thresholds, Sutrop CSI, Caulkins, small-n, bootstrap level confusion, G1 split, or negative centrality. |
| Claims validity | PASS | Correctly rejects "closer to human = better" (line 16) by name. |
| Audience translation | FAIL | No differentiation by audience. Closing paragraph is marketing copy ("positions it to be a uniquely credible and robust benchmark"). Does not flag a single audience-legibility risk. |

**Overall: LOW VALUE.** Gemini is the shortest review (one page). Its single methodological sentence on OCI/Romney is correct but uncritical. It endorses rather than audits. No defects identified.

---

## 2. Specific methods checks

| Question | Codex | Grok | Gemini |
|---|---|---|---|
| Smith's S → Sutrop CSI rationale | Did not engage | Did not engage | Did not engage |
| Option 2 Level-1 bootstrap underestimation | Did not engage | Did not engage | Did not engage |
| Caulkins six-state typology | Did not engage | Did not engage | Did not engage |
| Split G1 (salience × spatial) two-axis gate un-deferred | Did not engage | Did not engage | Did not engage |
| Romney CCM small-n at n=4 or n=12 | Did not engage | Did not engage | Did not engage |
| Flagged any actual methodological error in §4.2, `SME_REVIEW.md`, or `BOOTSTRAP_DESIGN.md` | None | None | None |

Zero of six methods checks produced substantive engagement from any reviewer. None of the three has read or cited `SME_REVIEW.md` or `BOOTSTRAP_DESIGN.md`. The Caulkins typology, which is load-bearing for Register 2 dashboard copy, is not mentioned by any reviewer.

---

## 3. Blind spots none of the three raised

1. **Protocol deviation cost accounting.** The LSB textual pile-sort is a real deviation from classical pile-sort (physical card manipulation). `ARCHITECTURE.md` §4.2.0 owns this but no reviewer asked how the textual protocol might systematically differ from the physical one for human baselines (e.g., does reading-order anchoring replace spatial anchoring in ways that perturb the similarity matrix?).
2. **Temperature as a variance-driver vs. a pseudo-population-driver.** LSB uses temperature sweeps to generate N runs per model. A methodologically serious reviewer would ask whether N samples at temperature T from one model are ontologically comparable to N responses from N human informants for CCM purposes. This is the single largest unresolved question at Register 2 and no reviewer touched it.
3. **Human-baseline item-set mismatch.** Phase 4c grounding submissions require ≥8-item intersection with LSB v1. No reviewer asked about the reliability of MDS coordinate placement when the intersection is small, or how `groundings: list[GroundingRef]` displays when baselines disagree with each other.
4. **Cross-provider adapter comparability.** Anthropic, OpenAI, and Google model APIs differ in stop-token behavior, streaming semantics, and tool-use interference with free-form output. A reviewer with an eval-methods background would have asked whether adapter-level differences introduce systematic bias that is indistinguishable from a corpus-lens effect.
5. **G1 salience-axis construction.** The split G1 gate separates salience concentration from spatial concentration on purpose (SME ruling). None of the three reviewers noticed this was a gate, let alone a split one. Any reviewer who had read `SME_REVIEW.md` would have been forced to engage with why a single G1 fails.

---

## 4. Overall SME verdict

**(a) Worth the methodology team's time?** Partially. Codex earns its keep on the launch-surface / shipping-copy / implementation-vs-specification axis — that is real audit value. Grok and Gemini are primarily endorsements and should be treated as such. None of the three produces methodological findings that change an SME ruling.

**(b) Which reviewer to consult again.** Codex, on implementation-reality and public-copy-integrity questions only. Do not consult any of the three on analytical validity; they lack the vocabulary. Prefer routing those questions to a human CDA methodologist (Weller or a Quinlan student) or to an LLM explicitly primed on the three source textbooks (Bernard, Weller & Romney, Borgatti).

**(c) Reading list to raise the bar next round.**
1. `docs/SME_REVIEW.md` — the accumulated binding SME rulings; without this, no reviewer can engage with the live methodological decisions.
2. `docs/BOOTSTRAP_DESIGN.md` — the Level-1/Level-2 bootstrap contract; the single most common reviewer failure is treating all bootstraps as equivalent.
3. `ARCHITECTURE.md` §4.2.0 (methods adaptation table), §4.2.6 (uncertainty), §4.2.7 (two-level pipeline) — already in the reviewers' reading list but clearly not engaged with at depth; next prompt should require the reviewer to cite specific subsections.
4. Weller & Romney 1988 *Systematic Data Collection* (chapters 3-4 on free-listing and pile-sort). A reviewer who has not read this cannot distinguish Smith's S from Sutrop CSI and cannot assess whether the protocol adaptations compromise the measurement.
5. Caulkins 2001 on cultural consensus with subcultural variation — load-bearing for the six-state typology.

**Bottom line.** These three reviews are evidence that the project's *framing* is legible and defensible to an external LLM reader. They are not evidence that the *methods* are defensible — none of the three touched the methods layer at the depth required to falsify or endorse a specific decision. The correct use of these reviews is as *framing QA*, not *methods QA*. Mark's instinct to keep them as "outside perspective, not binding authority" is correct.

The one genuine finding worth incorporating: Codex's Priority 1 "implemented vs. specified" map (lines 380-390) and Priority 5 copy-integrity control (lines 428-444) should be considered for inclusion in the pre-launch checklist. Both align with existing SME posture and extend it usefully.
