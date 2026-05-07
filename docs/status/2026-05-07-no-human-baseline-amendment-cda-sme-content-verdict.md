# CDA SME Verdict — No-Human-Baseline + §1.5-Deepening Amendment (content review, closing gate)

**Filed:** 2026-05-07
**Reviewer:** CDA SME (Opus)
**Commit reviewed:** `38f5740` (16 file operations)
**Plan:** `docs/status/2026-05-07-no-human-baseline-amendment-architect-plan.md` (commit `6d99da0`)
**SME plan verdict:** `docs/status/2026-05-07-no-human-baseline-amendment-cda-sme-plan-verdict.md` (commit `ef859bf`)
**Source-of-truth philosophy doc:** `docs/status/2026-05-07-lsb-philosophy-and-framing.md` (commit `d014112`)
**Reviewer verdict:** `docs/status/2026-05-07-no-human-baseline-amendment-reviewer-verdict.md` (commit `cf27b2b`)
**Slack channel:** `#lsb-cda-sme`

---

## VERDICT: PASS

| Axis | Result |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | PASS |
| Axis 3 — Claims validity | PASS |
| Axis 4 — Audience translation | PASS |

| Compliance check | Result |
|---|---|
| Register compliance | PASS (registers untouched; §4.2.0 framework preserved) |
| Vocabulary compliance | PASS (all changed surfaces clean; §1.5.4 table extended per A5 with two new rows) |
| A1–A6 binding-note compliance | PASS (all six satisfied at the prose level; see §C below) |
| Verbatim quote fidelity | PASS (philosophy doc §1, §2, §4, §8, §9 all installed verbatim where required) |
| T8 / T9 / B6 carry-forward | PASS (all three satisfied throughout amendment prose) |

**The amendment is closed.** The Coder is authorized to treat commit `38f5740` as the final form of the no-human-baseline + §1.5-deepening amendment. No follow-up Coder commit is required from this content review. Mark may treat the commit as stable.

PASS rather than PASS-WITH-NOTES because the three Reviewer-forwarded observations all resolve in favor of the prose as written:

- **A3 README closing-clause re-anchoring:** SME ruling in §B(1) below is *optional, not required*. The current prose ("what we measure, what we don't, and why the distinction matters") is coherent and not in conflict with §1.5.7 framing; the A3-preferred form ("what this measures and what it does not") is a stylistic improvement, not a methodological correction. The prose passes as written.
- **A4 §1.5.7 compound-sentence intro:** SME ruling in §B(2) below is that the compound-with-semicolon form satisfies A4's "one sentence, not a paragraph" intent. A4 was a structural discipline (don't write a paragraph; don't paraphrase the philosophy doc), not a stylistic prohibition on compound sentences. The Coder's intro is one sentence in §1.5.7's own voice, names the source document explicitly, and introduces no new framing claims.
- **Working-tree hygiene:** SME ruling in §B(3) below is *purely procedural*. The two `.claude/agent-memory/cda_sme/` files are correct content, are properly tracked, and do not affect any methodology surface. The Reviewer correctly forwarded this as a hygiene note rather than a content issue. Memory note already saved by orchestrator for future dispatch hygiene.

The amendment as committed is the right shape. The audience-translation axis — which the plan-level verdict flagged as the highest-load axis — passes cleanly: the README first paragraph reads correctly, the §1.5.7 sub-section is composed correctly, the methodology-page outline item 5 quotes philosophy doc §5/§6/§8 cleanly, and the `data/grounding/README.md` banner is descriptive-only without editorializing.

---

## (B) Three Reviewer-forwarded observations — explicit rulings

### B(1) — A3 observation: README line 13 closing clause re-anchoring

**Reviewer's question:** A3 said "may rewrite," not "must." Does the SME content verdict require the Coder to re-anchor "what we measure, what we don't, and why the distinction matters" to the A3-preferred "what this measures and what it does not"?

**SME ruling: NOT REQUIRED. Prose passes as written.**

A3's exact text (from the plan-level verdict): *"The Coder may rewrite line 13's closing sentence to: 'The methodology page on the dashboard goes into depth on what this measures and what it does not.'"*

The word "may" is correctly read as optional. The current README line 13 reads:

> *"LSB **is not** a measure of cultural worldview, belief, or cognition. Models do not have lived experience; they synthesize statistical patterns from text corpora. LSB is careful about this distinction in every visualization, every social post, and every line of dashboard copy. The methodology page on the dashboard goes into depth on what we measure, what we don't, and why the distinction matters."*

Three reasons the SME content verdict passes this without rewrite:

1. **The closing clause does not contradict §1.5.7 framing.** "What we measure, what we don't, and why the distinction matters" is a descriptive characterization of methodology-page content. It does not introduce any forbidden vocabulary, does not imply hypothesis-testing, does not invoke cognition, and does not soften the §1.5.7 exploratory posture.

2. **The "we" voice is consistent with the rest of README.md and ARCHITECTURE.md §1.5.7.** The §1.5.7 exploratory framing block uses "we ran the protocol; here is what came out." The README closing clause's "what we measure, what we don't" parallels that voice. Re-anchoring to the impersonal "what this measures" would actually slightly mismatch the §1.5.7 voice register.

3. **The A3-preferred form is a stylistic improvement, not a methodological correction.** A3 was a coherence-discipline note: ensure the README closing clause does not pull against the new methodology-page outline item 5 ("What this measures and what it does not"). The current closing clause does not pull against item 5 — it functionally describes the same thing in different words. The two forms are coherent neighbors.

**Disposition:** PASS. No Coder follow-up commit required for this observation.

If Mark or a future Coder wishes to apply A3's preferred phrasing as a future polish edit, that is acceptable but not gated. The methodology-page outline item 5 is the canonical phrasing surface; the README is allowed to introduce it in its own voice register.

### B(2) — A4 observation: §1.5.7 intro is a compound sentence with semicolon

**Reviewer's question:** A4 specified "one sentence, not a paragraph." The Coder's §1.5.7 intro is "LSB's posture is exploratory, not hypothesis-testing; the following two passages (quoted verbatim from the canonical philosophy document, `docs/status/2026-05-07-lsb-philosophy-and-framing.md`) are binding on all public-facing text the project produces." Does the compound form satisfy A4?

**SME ruling: SATISFIES A4. Prose passes as written.**

A4's structural disciplines were three: (1) one sentence in §1.5.7's own voice (not a paragraph), (2) introduces the verbatim quote that follows, (3) does not introduce new framing claims. The Coder's intro satisfies all three:

1. **One sentence, not a paragraph.** The Coder's intro is one sentence (terminal punctuation: one period). The semicolon couples two independent clauses into a single complex sentence; the result is grammatically one sentence. A4's "one sentence, not a paragraph" intent was structural — prevent a multi-paragraph philosophical preamble that re-articulates philosophy doc framing in fresh prose. A compound sentence with semicolon does not constitute a paragraph and does not re-articulate framing in fresh prose. PASS on intent.

2. **Introduces the verbatim quote that follows.** The intro's second clause ("the following two passages [...] are binding on all public-facing text the project produces") explicitly cues the reader that the verbatim quotes follow. The source document is named by path. PASS on function.

3. **No new framing claims.** "LSB's posture is exploratory, not hypothesis-testing" is a faithful one-clause distillation of philosophy doc §2's opening line ("LSB is not hypothesis-testing"). The "binding on all public-facing text" framing is consistent with §1.5's binding-on-all-generated-text statement and with the philosophy doc's own claim that this framing is "binding on every public-facing piece of text the project produces" (philosophy doc §2, third paragraph). PASS on framing fidelity.

The only stylistic alternative would have been splitting the intro into two short sentences:

> *"LSB's posture is exploratory, not hypothesis-testing. The following two passages, quoted verbatim from the canonical philosophy document at `docs/status/2026-05-07-lsb-philosophy-and-framing.md`, are binding on all public-facing text the project produces."*

That alternative is also acceptable but not superior. A4's intent was the structural discipline (one sentence-or-equivalent intro, no paragraph re-articulation); the structural discipline holds.

**Disposition:** PASS. No Coder follow-up commit required for this observation.

### B(3) — Working-tree hygiene: two SME agent-memory files swept into Coder commit

**Reviewer's question:** The two files at `.claude/agent-memory/cda_sme/MEMORY.md` and `.claude/agent-memory/cda_sme/project_no_human_baseline_amendment.md` were authored during the prior SME dispatch (the plan-level verdict) but committed by the Coder during the amendment commit because they sat dirty in the working tree. Methodology implication, or purely procedural?

**SME ruling: PURELY PROCEDURAL. No methodology implication.**

Three reasons:

1. **The agent-memory directory is git-tracked by established project convention** (per Reviewer verdict §File 15 disposition; commit `7e9bed9` precedent). The files are not inappropriate for the repository; they are routine memory-update content. The only deviation from convention is the commit boundary (these files belong in a dedicated `chore(memory):` commit per CLAUDE.md §8 one-commit-per-task discipline).

2. **The memory file content is correct.** I read both files. `MEMORY.md` adds one index line referencing the new `project_no_human_baseline_amendment.md` memory. `project_no_human_baseline_amendment.md` is a structured memory entry summarizing my own plan-level verdict (Q1–Q9 rulings, A1–A6 binding notes, carry-forward table). Both files are accurate against the verdict they document. There is no methodology drift; the files merely record the verdict's structural disposition for future SME-dispatch context recovery.

3. **The methodology surfaces are unaffected.** The amendment's methodology surfaces (ARCHITECTURE.md §1.5, README.md, DESIGN_SYSTEM.md §4 + §6.1, CLAUDE.md §9, DATA_DICTIONARY.md §2 + §3 + §4) carry no content from the agent-memory files. There is no cross-contamination between agent-memory state and project documentation. The agent-memory files are operational state for the SME agent; the project documentation is the deliverable. The two surfaces do not interact.

**The procedural lesson is correctly identified by the Reviewer:** future SME-dispatch protocol should commit `.claude/agent-memory/cda_sme/` changes in a dedicated `chore(memory):` commit *before* the Coder dispatch begins. The orchestrator has saved a memory note for future dispatch hygiene. This is the right remediation: the issue is dispatch-ordering, not content.

**Disposition:** PASS. No Coder follow-up commit required. No methodology implication. Working-tree hygiene improvement is forward-carry to future SME dispatches.

---

## (C) A1–A6 binding-note compliance — content-level verification

The Reviewer already confirmed A1–A6 structural compliance in the Reviewer verdict §A1–A6 section. The SME content verdict re-verifies at the prose level, focused on framing fidelity and methodology surface (not just structural presence).

### A1 — "supersedes" verbatim in §1.5.1

**Verified:** ARCHITECTURE.md line 120: *"Naming them explicitly makes the construct operationally legible and **supersedes** the prior four-layer formulation."*

The exact word "supersedes" is present, in the exact context A1 specified. The post-block sentence at line 136 ("LSB elicitation operates on the output-distribution link. What it reveals about the corpus, training, alignment, and decoding links is a composed inference, not a measurement.") faithfully updates the original Layer-4 sentence to the five-link vocabulary while preserving the post-F1 SME discipline (LSB measures only the observable surface). PASS.

### A2 — §1.5.5 four-element structure with philosophy doc §1 "Trojan horse" verbatim

**Verified:** ARCHITECTURE.md §1.5.5 lines 180–188.

Element-by-element:

1. **Opening sentence in §1.5.5 voice:** "As of 2026-05-07, human grounding is removed from v1 of LSB." — single sentence, naming the change. ✓
2. **Philosophy doc §1 "Trojan horse" verbatim** (line 184): the entire second paragraph of philosophy doc §1 (from "**Why:**" through "Remove the baseline, remove the surface area.") is present verbatim. The word "Trojan horse" is preserved. The skeptical-reader critique form is preserved. ✓
3. **Architectural consequence in §1.5.5 voice:** "Every domain on the dashboard is, permanently, model-to-model. The schema's `groundings: list[GroundingRef]` field is retained for forward compatibility but defaults to empty for all v1 domains." ✓
4. **Pointer to ancestry credit:** "Romney / D'Andrade / Weller / Borgatti / Batchelder ancestry credit is named on the methodology page per `DESIGN_SYSTEM.md` §6.1 item 2." ✓

The "Floor and ceiling claims" framing block and the "What follows from this framing" 4-point list (originally in §1.5.5 pre-amendment) are absent. Removed in full per Architect plan §5.1.a. ✓

T8 (descriptive-shape) check on (1), (3), (4): no causal language, no introspective language, no stimulus-as-cause framing. PASS.

T9 (forbidden softer verbs) check: no "recognizes," "identifies," "interprets," "comprehends," "perceives" applied to models. PASS.

§1.5.4 forbidden-vocabulary check: zero hits. PASS.

A2 PASS at the content level.

### A3 — README §9–13 coherence post-truncation

**Verified:** README.md lines 5–15.

The first paragraph (line 5) opens with the philosophy doc §8 first sentence verbatim ("LSB measures what frontier LLMs produce when asked to categorize, in a way that's reproducible, comparable across models, and trackable across time."), continues with the CDA-application description, and closes with the "Every domain on the dashboard is, permanently, model-to-model." statement. The "Where published or contributed human CDA data is available, we put a human reference point on the same map." sentence is removed.

The "What LSB is and isn't" section (lines 9–15):

- Line 11 ("LSB **is** a benchmark for the categorical structure of model training corpora, surfaced through CDA elicitation protocols.") — survives unchanged. Coherent with the new first paragraph. ✓
- Line 13 ("LSB **is not** a measure of cultural worldview, belief, or cognition. [...] The methodology page on the dashboard goes into depth on what we measure, what we don't, and why the distinction matters.") — closing clause not re-anchored to A3's preferred form. Per §B(1) ruling above, this is acceptable as written. ✓
- Line 15 ("For the full scientific framing, see [`ARCHITECTURE.md`](ARCHITECTURE.md) §1.5.") — survives unchanged. ✓

§1.5.4 forbidden-vocabulary check on lines 5–15: zero hits. The use of "worldview" on line 13 is a negation ("LSB **is not** a measure of cultural worldview"), which is the meta-reference/disclaim form §1.5.4 explicitly allows. PASS.

The README's licensing table, repository structure, citation paragraph, and quick links are all coherent post-truncation: no orphan references to the deleted submission template, no orphan reference to the now-deleted PR template, no broken links. The Romney 1996 attribution paragraph at line 55 is correctly rewritten to the historical-context form. The "Contributing human CDA data" section (formerly lines 61–73) is fully removed.

A3 PASS at the content level.

### A4 — §1.5.7 three-element composition

**Verified:** ARCHITECTURE.md §1.5.7 lines 209–240.

Element-by-element:

1. **One-sentence intro in §1.5.7 voice (NOT a quote):** Line 211 — *"LSB's posture is exploratory, not hypothesis-testing; the following two passages (quoted verbatim from the canonical philosophy document, `docs/status/2026-05-07-lsb-philosophy-and-framing.md`) are binding on all public-facing text the project produces."* Per §B(2) ruling above, the compound-with-semicolon form satisfies A4's "one sentence, not a paragraph" intent. The intro is in §1.5.7's own voice, names the source document explicitly, and introduces no new framing claims. ✓

2. **Philosophy doc §2 verbatim:** Lines 213–226. The block from "LSB is **not hypothesis-testing.**" through "The benchmark exists to make the *comparison itself* reproducible at the level of measurement, not to push a thesis." is present and matches philosophy doc §2 verbatim. The originating exploratory question (*"what happens if you give a large language model a CDA free-list / pile-sort / interview? What comes out?"*) is preserved verbatim within this block. ✓

3. **Philosophy doc §9 verbatim:** Lines 228–240. The block from "Mark's intent: **we are not the final interpreters of LSB's data.**" through "That distinction is binding on the project's design." is present and matches philosophy doc §9 verbatim. The four-reason enumeration (models in systems / reproducible measurement unmet / drift invisible / data more valuable than interpretation) is preserved verbatim. ✓

**No transition sentence between (2) and (3):** verified — line 226 ends with "not to push a thesis." and line 228 begins directly with "Mark's intent: **we are not the final interpreters of LSB's data.**" Paragraph break only; no intervening transition sentence. ✓

T8 (descriptive-shape) check on (1): no causal language, no introspective language, no stimulus-as-cause framing. PASS.

T9 (forbidden softer verbs) check on (1): no "recognizes," "identifies," "interprets," "comprehends," "perceives" applied to models. PASS.

§1.5.4 forbidden-vocabulary check across the entire §1.5.7: zero hits.

A4 PASS at the content level.

### A5 — §1.5.4 forbidden-vocabulary table extension for hypothesis-testing language

**Verified:** ARCHITECTURE.md §1.5.4 lines 173–174.

Two new rows added:

| Don't say | Say instead |
|---|---|
| "LSB hypothesizes that..." / "LSB tested whether..." / "LSB confirms that..." / "LSB found that [hypothesis]" | "LSB measures..." / "LSB reports..." / "LSB observes..." |
| "LSB predicted X and the data confirmed/refuted it" | "LSB ran the protocol; here is what came out" |

Both rows match the SME's recommended wording from A5 verbatim. The table now has 12 rows total (10 pre-amendment + 2 new). The two new rows correctly close the vocabulary surface created by §1.5.7's exploratory framing — any future text drift toward "LSB hypothesizes that DeepSeek's family-term consensus is lower than Claude's" is now caught by Reviewer's vocabulary scan.

The table's existing post-table commentary (line 176: "The last four rows (added post-F1 SME review) guard the boundary between **Register 1 (output distribution analysis)** and **Register 2 (cultural consensus analysis)**") refers to the pre-amendment rows 7–10. With the addition of the two new rows (11–12), the "last four rows" phrasing is now slightly imprecise — it now refers to rows 9–12, of which only rows 9–10 are register-boundary-related. This is a minor commentary-currency observation, not a content-level finding; the table itself is correct and the Reviewer's vocabulary scan operates on the rows themselves, not the post-commentary. **Optional future polish:** the next time §1.5.4 is edited for any reason, the post-commentary at line 176 could be updated to "rows 7–10 guard the register boundary; rows 11–12 guard the exploratory-framing boundary added by the 2026-05-07 amendment." Not gating; flagged for future cleanup.

A5 PASS at the content level.

### A6 — `data/grounding/README.md` banner ≤ 8 lines, descriptive-only

**Verified:** `data/grounding/README.md`. 8 lines, exactly at the upper bound A6 permits.

Content:

> *"Historical reference data only. The 2026-05-07 amendment removed human baselines from LSB v1. These files are preserved for audit-trail completeness and are not consumed by any v1 analysis pipeline. See `docs/status/2026-05-07-lsb-philosophy-and-framing.md` and `docs/status/2026-05-07-no-human-baseline-amendment-architect-plan.md`. Romney et al. (1996) attribution requirement (per source.md) applies to anyone reusing the family/romney_1996/ files outside LSB."*

Descriptive-only check: no advocacy, no editorializing, no framing drift. The banner does not say "this data is no longer valid" or "this data has been superseded" — it correctly characterizes the data as preserved and not-consumed-by-pipeline, while preserving the Romney attribution requirement. PASS.

§1.5.4 forbidden-vocabulary check: zero hits. PASS.

A6 PASS at the content level.

---

## (D) Verbatim-quote fidelity check — five canonical installs

The amendment installs five verbatim quotations from the philosophy doc into canonical project documents. Each install is content-verdict-checked against the source.

### D(1) — Philosophy doc §1 (Trojan-horse passage) → ARCHITECTURE.md §1.5.5

**Source:** philosophy doc line 19 (the second paragraph of §1, beginning "**Why:**" through "Remove the baseline, remove the surface area.").

**Install:** ARCHITECTURE.md line 184.

**Verbatim check:** I diffed the two passages line-by-line. Match. The "Trojan horse" metaphor, the "knowing something in a way commensurable with human knowing" phrasing, the "skeptical reader's strongest possible critique" phrasing, and the "Remove the baseline, remove the surface area" close are all preserved exactly. The rhetorical strength of the metaphor is preserved.

**Verdict:** PASS.

### D(2) — Philosophy doc §2 (exploratory framing) → ARCHITECTURE.md §1.5.7

**Source:** philosophy doc lines 25–38 (all seven paragraphs of §2).

**Install:** ARCHITECTURE.md lines 213–226.

**Verbatim check:** I diffed the two passages line-by-line. Match. The originating exploratory question ("what happens if you give a large language model a CDA free-list / pile-sort / interview? What comes out?") is preserved verbatim. The four-item ship list (verbatim prompts CC0, verbatim responses CC-BY-4.0, reproducible numerics, code) is preserved verbatim. The "we ran the protocol; here is what came out; draw your own conclusions" framing is preserved verbatim.

**Verdict:** PASS.

### D(3) — Philosophy doc §9 (release-for-community-analysis) → ARCHITECTURE.md §1.5.7

**Source:** philosophy doc lines 126–138 (all four paragraphs of §9).

**Install:** ARCHITECTURE.md lines 228–240.

**Verbatim check:** I diffed the two passages line-by-line. Match. The "we are not the final interpreters of LSB's data" opening is preserved verbatim. The four-reason enumeration is preserved verbatim with all four bullets intact (models-in-systems, reproducible-measurement-unmet, drift-invisible, data-more-valuable-than-interpretation). The closing "A paper presents conclusions. A website presents reproducible measurements and lets the community draw conclusions. That distinction is binding on the project's design." is preserved verbatim.

**Verdict:** PASS.

### D(4) — Philosophy doc §4 (corpus-lens five-link chain) → ARCHITECTURE.md §1.5.1

**Source:** philosophy doc lines 52–68. The five-link chain (`corpus → training → alignment → decoding → output distribution`) and its five-bullet unpacking.

**Install:** ARCHITECTURE.md lines 120–134 (replacing the prior four-layer breakdown at lines 111–118 of pre-amendment §1.5.1).

**Verbatim check:** I diffed the two passages. The five-link chain itself (line 124) is preserved verbatim. The five-bullet breakdown (corpus / training / alignment / decoding / output distribution) is preserved verbatim. The "shadow this chain casts when the CDA stimuli are shone at it" framing (line 126) is preserved verbatim. The "It is **not** the corpus directly... It is **not** a transparent window onto human cultural consensus..." preface paragraphs from philosophy doc §4 (lines 54–56) were absorbed into the Architect's plan §5.1.a-recommended supersession sentence at ARCHITECTURE.md line 120 ("Naming them explicitly makes the construct operationally legible and supersedes the prior four-layer formulation"). The supersession sentence does not contradict the philosophy doc's two negations and is consistent with them; the absorption is faithful.

**Verdict:** PASS.

### D(5) — Philosophy doc §8 (honest tagline) → ARCHITECTURE.md §1.5 + README.md first paragraph

**Source:** philosophy doc lines 116–120 (three paragraphs of §8).

**Install A (ARCHITECTURE.md §1.5 quotable block):** lines 85–89.

**Verbatim check (A):** I diffed the two passages. Match. All three paragraphs of philosophy doc §8 are present verbatim in the §1.5 quotable block, from "LSB measures what frontier LLMs produce..." through "...releases the data for the community to interpret." The doc-voice surrounding text at line 91 ("The canonical short-form description of LSB. All public-facing short summaries [...] draw from this block. Source: `docs/status/2026-05-07-lsb-philosophy-and-framing.md` §8.") correctly cites the source and names the canonical-short-form role.

**Install B (README.md first paragraph, first sentence only):** line 5.

**Verbatim check (B):** The first sentence ("LSB measures what frontier LLMs produce when asked to categorize, in a way that's reproducible, comparable across models, and trackable across time.") is preserved verbatim from philosophy doc §8 paragraph 1. The truncation discipline (first sentence only, surrounding paragraph rewritten in README's own voice) is per Q8 ruling and A3 discipline. The rewrite preserves the §1.5.4 forbidden-vocabulary cleanliness and adds the "Every domain on the dashboard is, permanently, model-to-model." statement as the README-first-paragraph close.

**Verdict:** PASS on both installs.

**Aggregate verbatim-quote fidelity:** PASS across all five canonical installs. The Coder's quotation discipline was clean; no paraphrase drift was introduced where verbatim was required.

---

## (E) §1.5 prose semantic check — beyond literal verbatim

Beyond the per-passage verbatim checks, the §1.5 expansion as a whole was scanned for semantic-level integrity against the four-axis framing.

### E(1) — §1.5 framing semantic posture: descriptive vs causal vs introspective

**Result:** descriptive throughout. PASS.

The new §1.5 quotable block (lines 85–89), the §1.5.1 five-link chain (lines 120–134), the §1.5.5 transition sub-section (lines 180–188), and the §1.5.7 exploratory-framing sub-section (lines 209–240) all maintain the descriptive-shape posture established by T8 (descriptive-shape discipline, RD-3 verdict). No causal language ("because the model believes X, the output looks like Y"), no introspective language ("the model thinks of family as Z"), no stimulus-as-cause framing ("CDA elicitation reveals that the model X"). The prose stays at the descriptive level: *"LSB measures what frontier LLMs produce when asked to categorize"* / *"the shape of the model's output distribution"* / *"output behavior under structured elicitation."*

### E(2) — §1.5.4 forbidden-vocabulary table extension semantic correctness

**Result:** PASS. The two new rows (lines 173–174) correctly close the vocabulary surface created by §1.5.7's exploratory framing. The replacement phrasings ("LSB measures..." / "LSB reports..." / "LSB observes..." / "LSB ran the protocol; here is what came out") are descriptive, not causal, and consistent with T8 + T9.

The post-table commentary at line 176 has a minor currency drift (the "last four rows" phrasing now refers to rows 9–12 rather than the original 7–10). This is not a content-level finding — see A5 disposition above. Optional future polish.

### E(3) — §1.5.5 four-element sub-section structure (per A2)

**Result:** PASS. Per A2 verification in §C above. The four elements are present in the correct order, the philosophy doc §1 "Trojan horse" passage is verbatim, the architectural consequence is in §1.5.5's own voice, and the ancestry-credit pointer correctly references DESIGN_SYSTEM.md §6.1 item 2.

### E(4) — §1.5.7 three-element composition (per A4)

**Result:** PASS. Per A4 verification in §C above. The three elements are present in the correct order, with no transition sentence between elements (2) and (3), and the §1.5.7-voice intro sentence is one compound-with-semicolon sentence rather than a paragraph.

### E(5) — §1.5.1 "supersedes" usage (per A1)

**Result:** PASS. Per A1 verification in §C above. The exact word "supersedes" is present at line 120. The post-block sentence at line 136 faithfully updates the original Layer-4 sentence to the five-link vocabulary while preserving the post-F1 SME discipline.

### E(6) — Honest-tagline quotable block placement and pitch

**Result:** PASS. The quotable block at ARCHITECTURE.md lines 85–89 sits immediately after the §1.5 binding-on-all-generated-text statement, before §1.5.1, per Architect plan §5.1.a placement. The doc-voice surrounding sentence (line 91) names it as the canonical short-form and cites the philosophy doc §8 source. The READE first paragraph (line 5) opens with the first sentence of the tagline as the project's most-read line; the surrounding §9–13 section ("What LSB is and isn't") remains coherent post-truncation per A3 discipline.

The tagline's pitch is correct: assertive ("LSB measures what frontier LLMs produce when asked to categorize") + disclaiming ("It does not measure cognition, understanding, belief, worldview, or cultural consensus, because the LLM has none of those things — and even if you thought it did, this protocol would not be the way to measure them") + descriptive of intent ("releases the data for the community to interpret"). No overclaim; no underclaim.

---

## (F) README.md first paragraph — read as if landing on cogstructurelab.com

I read README.md lines 5–7 as a first-time visitor:

> *"LSB measures what frontier LLMs produce when asked to categorize, in a way that's reproducible, comparable across models, and trackable across time. It applies Cultural Domain Analysis (CDA) — a methodology developed by cognitive anthropologists in the 1970s and 80s to study how human informants organize cultural vocabulary — to LLMs as if the models were informants. The result is a comparative map of how different models (Claude, GPT, DeepSeek, Llama, Mistral, Qwen, and others) organize the same set of everyday domain words (family terms, holidays, food, color, emotion). Every domain on the dashboard is, permanently, model-to-model."*
>
> *"The **dashboard** is the primary deliverable: an interactive comparative explorer at [cogstructurelab.com](https://cogstructurelab.com), with downloadable images, citations, and the underlying numbers behind every figure. The benchmark, the open data, and the social pipeline all exist to make the dashboard credible, useful, and discoverable."*

Three observations:

1. **The honest-tagline first sentence works as the project's most-read line.** It is descriptive, comparable across models, and explicitly time-aware (the "trackable across time" phrasing previews the Phase 6 DriftTracker). A skeptical reader cannot reasonably accuse LSB of overclaiming on the basis of this sentence.

2. **The "Every domain on the dashboard is, permanently, model-to-model." close is the right shape.** It pre-empts the question "what about human baselines?" without belaboring the topic. The word "permanently" is load-bearing; it signals the structural decision (not a temporary state pending data acquisition).

3. **The "What LSB is and isn't" §9–13 flow remains coherent.** Line 11 ("LSB **is** a benchmark for the categorical structure of model training corpora, surfaced through CDA elicitation protocols.") sits as the technically-precise long-form companion to the new tagline-derived first sentence. Line 13 (the negation paragraph) remains clear and concise. Line 15 ("For the full scientific framing, see ARCHITECTURE.md §1.5.") survives unchanged and points the reader at the deeper framing.

The README first paragraph passes its job. PASS.

---

## (G) `data/grounding/README.md` banner — ≤ 8 lines, descriptive-only per A6

I read the banner. 8 lines, descriptive throughout, names the Romney attribution requirement, names the canonical reference documents, does not editorialize. The banner correctly characterizes the data as "preserved for audit-trail completeness" rather than "deprecated" or "superseded" or "no longer valid" — the data is still scholarly-valid Romney 1996 reference material; LSB just doesn't use it as a comparison axis.

A6 PASS. See §C(A6) above.

---

## (H) Carry-forward of T8 + T9 + B6

### T8 (descriptive-shape discipline, RD-3 verdict)

**Status: SATISFIED throughout amendment prose.**

I scanned the amendment's prose surfaces (ARCHITECTURE.md §1.5 expansion, §1.5.5 transition, §1.5.7 new sub-section, README first paragraph, methodology-page outline item 5 in DESIGN_SYSTEM.md §6.1, `data/grounding/README.md` banner) for T8 violations. Zero hits. The Coder's voice on the §1.5.5 opening ("As of 2026-05-07, human grounding is removed from v1 of LSB."), the §1.5.7 intro ("LSB's posture is exploratory, not hypothesis-testing"), and the README close ("Every domain on the dashboard is, permanently, model-to-model.") are all descriptive. No causal claims, no introspective claims, no stimulus-as-cause framing.

T8 PASS.

### T9 (forbidden softer-than-thinks/believes verbs, RD-3 verdict)

**Status: SATISFIED throughout amendment prose.**

I scanned for `recognizes`, `identifies`, `interprets`, `comprehends`, `perceives`, `understands` (as verbs applied to models). Zero hits in the new prose. The instances of `understand` in the philosophy-doc-quoted text appear only in the §1.5.4 forbidden-vocabulary disclaim form ("Whether the model 'understands' the domain") which is the meta-reference/disclaim form §1.5.4 explicitly allows.

T9 PASS.

### B6 (parent T4-redo public-copy guardrails)

**Status: SATISFIED throughout amendment prose.**

B6 forbids: framing prior LSB work as "incorrect" or "should not have been published"; cross-provider, cross-failure-mode, or cross-prompt-type generalization without evidence; internal-state claims about models; augmenting findings with "PLUS disproportionate CN-origin decline pattern" framing.

I scanned the amendment's prose for these forms. The §1.5.5 transition language describes the v0.7 grounding architecture as "removed from v1" rather than "incorrect" or "should not have been published" — the v0.7 design was correct against its frame; the 2026-05-07 amendment makes a different decision under different priorities. The historical-note posture at ARCHITECTURE.md §4.2.5, DESIGN_SYSTEM.md §4, CLAUDE.md §9 pitfalls 3/4/12, and DATA_DICTIONARY.md §2/§3/§4 editorial notes all preserve the prior architecture's correctness against its frame. No B6 violations.

B6 PASS.

### Summary table

| Note | Status under content review |
|---|---|
| B6 (parent T4-redo public-copy guardrails) | SATISFIED throughout amendment prose |
| T8 (RD-3 descriptive-shape discipline) | SATISFIED throughout amendment prose |
| T9 (RD-3 forbidden softer verbs) | SATISFIED throughout amendment prose |
| Note D (no ceiling claims pre-Phase-4c) | SATISFIED-by-amendment (Phase 4c removed; ceiling-claim-prevention now structural) |

---

## (I) Side-effect surfaces — proactive scan

### I(1) — DESIGN_SYSTEM.md §4 collapse coherence

**Verified:** §4 collapsed to ≈10 lines (lines 394–402). The four sub-sections (§4.1 The Four Grounding States, §4.2 Grounding Detail Panel, §4.3 Data Submission UI, §4.4 Cross-references) are removed in full and replaced by three short paragraphs naming the historical state, the amendment, and the retain-with-banner posture. The new §4 cross-references `ARCHITECTURE.md §1.5.5` and `docs/status/2026-05-07-lsb-philosophy-and-framing.md` correctly. PASS.

### I(2) — DESIGN_SYSTEM.md §3.3 conditional-rendering table collapse

**Verified:** §3.3 conditional-rendering table (lines 270–272) collapsed to a single row labeled "State 0 — model-to-model (the only v1 state)." PASS.

### I(3) — DESIGN_SYSTEM.md §3.7, §3.8 — orphan-state-reference scan

**Verified:** I scanned DESIGN_SYSTEM.md for residual references to "State 1," "State 2," "State 3," "Submit your data," "Human baselines section," and "GroundingSelector" / "GroundingDetailPanel" / "SubmitGroundingModal." Zero hits in non-historical context. The only remaining "State 0" reference is in the §3.3 collapse-table row name (the sole legitimate retention). PASS.

### I(4) — CLAUDE.md §9 pitfalls 3/4/12 historical-gloss disposition

**Verified:** Pitfalls 3 (line 179), 4 (line 181), and 12 (line 197) each carry the leading "(Historical — ...)" gloss while preserving the body text. The bodies remain methodologically valid (the schema is unchanged; the empty-baseline framing is still relevant against re-introduction). PASS.

### I(5) — DATA_DICTIONARY.md editorial-note placement

**Verified:** Three editorial notes added at:
- §2 line 255 (within the "Important:" callout for `DomainResult.groundings`),
- §3 line 288 (top of `GroundingRef` sub-section, before §3.1),
- §4 line 492 (`groundings` SQLite table introduction).

All three notes consistently anchor "2026-05-07" and reference `ARCHITECTURE.md §1.5.5`. The 18+ field-level descriptions in §3 (sub-sections 3.1–3.8) are preserved unchanged. R7 (schema/dictionary lockstep) is satisfied vacuously. PASS.

### I(6) — SECURITY_AND_HARDENING.md §7.4 dangling-reference cleanup

**Verified:** Line 481 — the historical-note line correctly converts the prior "When a researcher submits human grounding data" sentence to the historical posture. The surrounding three-checks block remains intact, framed as "if [...] is reintroduced in a future version." This is a surgical dangling-reference fix; the security policy itself is unchanged. PASS.

The Reviewer correctly flagged this in the scope-discipline section (Files 11–14) as ACCEPTABLE. I concur. The change is minimal and preserves the security policy intact.

### I(7) — Methodology page outline item 5 (DESIGN_SYSTEM.md §6.1)

**Verified:** Lines 466–477. The new item 5 ("What this measures and what it does not") draws from philosophy doc §5/§6/§7/§8 with appropriate quotability discipline:

- The first sub-bullet ("The shape of the model's output distribution under structured CDA elicitation") draws from philosophy doc §5's pinned definition.
- The second sub-bullet (Smith's S, Romney CCM, MDS, Procrustes, OCI describe output-distribution shape, not cognition / belief / understanding / cultural consensus) draws from philosophy doc §5 and §6.
- The third sub-bullet (comparative model characterization, drift detection, stability under prompt rephrasing, confabulation under blind-spot conditions, reproducible public benchmark) draws from philosophy doc §7 with explicit cross-reference to ARCHITECTURE.md §1.5.7 / philosophy doc §7.
- The fourth sub-bullet (the honest tagline, quotable) draws from philosophy doc §8 with explicit cross-reference to ARCHITECTURE.md §1.5.
- The fifth sub-bullet ("The mismatch is the finding" framing) draws from ARCHITECTURE.md §1.5.2 / §1.5.6 — already-PASSed legacy framing that survives the amendment intact.

Item 2 (Romney / D'Andrade / Weller / Borgatti ancestry credit) is unchanged. Per Q1 ruling, this is the only ancestry-credit surface and it is correctly preserved. PASS.

---

## (J) New binding notes — inventory

**No new binding notes from this content review.**

The amendment as committed is the closing form. A1–A6 (established at the plan-level verdict) are now SATISFIED at the content level. The carry-forward dispositions (B6 BINDING, T8 BINDING, T9 BINDING, Note D SATISFIED-by-amendment, S5 gate posture preserved) hold.

**Optional future-polish observations that are NOT new binding notes:**

1. **§1.5.4 post-table commentary at ARCHITECTURE.md line 176** ("The last four rows...") could be updated to reflect the now-12-row table at the next §1.5.4 edit. Not gating; minor currency drift only.

2. **README.md line 13 closing clause** ("what we measure, what we don't, and why the distinction matters") could be re-anchored to A3's preferred form ("what this measures and what it does not") at any future README polish edit. Not gating; voice-register difference only.

3. **Working-tree hygiene on SME dispatches** — future SME-dispatch protocol should commit `.claude/agent-memory/cda_sme/` changes in a dedicated `chore(memory):` commit before the Coder dispatch begins. The orchestrator has already saved a memory note for this. Not gating; procedural.

4. **The v0.7 changelog footer in ARCHITECTURE.md (lines 1641–1648)** retains references to the now-deleted `docs/grounding_submission_template.md` and `.github/PULL_REQUEST_TEMPLATE/grounding_submission.md` deliverables in their "does not yet exist" historical-checklist context. These items document v0.7-era intentions rather than present state. The 2026-05-07 amendment supersedes the v0.7 plan; the footer's historical record is appropriately preserved as audit-trail. Not gating; preserved as historical context.

These four observations are forward-carry polish, not closing-gate prerequisites.

---

## (K) Carry-forward of A1–A6 and binding-note inventory

| Note | Origin | Status post-content-review |
|---|---|---|
| A1 ("supersedes" word in §1.5.1) | This amendment, plan-level verdict | SATISFIED (line 120) |
| A2 (philosophy doc §1 "Trojan horse" verbatim in §1.5.5) | This amendment, plan-level verdict | SATISFIED (line 184) |
| A3 (README §9–13 coherence post-truncation) | This amendment, plan-level verdict | SATISFIED (lines 5–15; closing-clause optional polish flagged) |
| A4 (§1.5.7 three-element composition) | This amendment, plan-level verdict | SATISFIED (lines 209–240; compound-with-semicolon intro form ruled adequate) |
| A5 (§1.5.4 hypothesis-testing vocabulary rows) | This amendment, plan-level verdict | SATISFIED (lines 173–174) |
| A6 (`data/grounding/README.md` banner discipline) | This amendment, plan-level verdict | SATISFIED (8 lines, descriptive-only) |
| B6 (T4-redo public-copy guardrails) | T4-redo verdict chain | BINDING — still applies to future methodology-bound text |
| T8 (RD-3 descriptive-shape discipline) | RD-3 content verdict | BINDING — still applies to future methodology-bound text |
| T9 (RD-3 forbidden softer verbs) | RD-3 content verdict | BINDING — still applies to future methodology-bound text |
| Note D (no ceiling claims pre-Phase-4c) | F1 SME review | SATISFIED-by-amendment (Phase 4c removed; ceiling-claim-prevention now structural) |

**A1–A6 transition from "Coder discipline at quotation boundaries" to "satisfied prose surfaces."** All six are now permanently encoded in the doc state. They no longer require ongoing Coder discipline; they require ongoing Reviewer + SME-content-verdict vigilance against drift in any future amendment that touches the same surfaces (ARCHITECTURE.md §1.5, README.md first paragraph, methodology-page outline item 5, `data/grounding/README.md`, the §1.5.4 forbidden-vocabulary table).

**B6 / T8 / T9 carry forward as before.** Future methodology-bound text — lede generator templates in `packages/cdb_publish/lede/`, social-pipeline drafts in `packages/cdb_social/`, the eventual methodology page implementation — must be SME-gated under these disciplines.

---

## Gate disposition

**The amendment Coder task (F-AMEND-2026-05-07-NO-HUMAN-BASELINE):** **CLOSED.**

Commit `38f5740` is the final form. No follow-up Coder commit required. Mark may treat the commit as stable.

**The amendment is complete.** All four gate verdicts are now in place:

- Plan-level CDA SME verdict: `docs/status/2026-05-07-no-human-baseline-amendment-cda-sme-plan-verdict.md` — PASS-WITH-NOTES (A1–A6 binding)
- Reviewer verdict: `docs/status/2026-05-07-no-human-baseline-amendment-reviewer-verdict.md` — PASS-WITH-NOTES (3 forwarded observations)
- Tester verdict: `docs/status/2026-05-07-no-human-baseline-amendment-tester-verdict.md` — PASS (1153 tests pass; no code change)
- Content-level CDA SME verdict: this file — PASS

**Gate chain posture:** with this verdict, the no-human-baseline + §1.5-deepening amendment is structurally closed. Any future text that touches the surfaces this amendment encoded (ARCHITECTURE.md §1.5, README.md first paragraph, methodology-page outline item 5, `data/grounding/README.md`, the §1.5.4 forbidden-vocabulary table) must reference the philosophy doc, this amendment plan, and this content verdict as the binding framing source.

---

## Sign-off

The amendment as committed is the right shape. The audience-translation axis, which the plan-level verdict flagged as the highest-load axis, passes cleanly. The verbatim-quote fidelity is clean across all five canonical installs (philosophy doc §1, §2, §4, §8, §9). The Coder's voice on the §1.5.5 opening, the §1.5.7 intro, and the README close maintains T8 / T9 / B6 discipline. The §1.5.4 forbidden-vocabulary table extension correctly closes the new vocabulary surface created by §1.5.7's exploratory framing. The `data/grounding/README.md` banner is descriptive-only and within the line-count discipline. The DESIGN_SYSTEM.md §4 collapse, the CLAUDE.md §9 pitfall historical-glosses, the DATA_DICTIONARY.md §2/§3/§4 editorial notes, and the SECURITY_AND_HARDENING.md §7.4 surgical cleanup all preserve the methodology surface integrity.

The three Reviewer-forwarded observations all resolve in favor of the prose as written: the A3 closing-clause is optional polish, the A4 compound-sentence intro satisfies A4's structural intent, and the working-tree hygiene is purely procedural with no methodology implication.

The amendment closes the surface area of the strongest critique LSB faces ("you're pretending to do anthropology on machines") by removing the human-baseline comparison axis. It encodes LSB's exploratory posture as a definitional claim rather than a meta-defense. It preserves the historical reference data (Romney 1996) with banner clarity about why it is no longer in the comparison loop. It preserves the v0.7 architectural intent in git history without retroactive rewriting. The methodology surfaces are now coherent end-to-end against the new framing.

The CDA SME thanks the Coder for the clean quotation discipline (no paraphrase drift where verbatim was required), the careful surgical cleanup of dangling references in SECURITY_AND_HARDENING.md / SHAKEDOWN_PROTOCOL.md / agent definitions (Files 11–14, all ACCEPTABLE), the faithful preservation of T8 / T9 / B6 disciplines throughout new prose, and the descriptive-only banner posture on `data/grounding/README.md`. The CDA SME thanks the Reviewer for the forwarded-observation discipline (raising the three observations to content-verdict level rather than absorbing them silently) and the proactive scope-discipline ruling on the four dangling-reference cleanups.

**The Reviewer verdict's PASS-WITH-NOTES correctly identified the procedural concerns; the SME content verdict closes them as ruled above.**

*Posted to `#lsb-cda-sme`. Binding for the F-AMEND-2026-05-07-NO-HUMAN-BASELINE Coder task (closing gate). The amendment is complete; commit `38f5740` is stable.*
