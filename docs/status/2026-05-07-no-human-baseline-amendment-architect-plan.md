# No-Human-Baseline + §1.5-Deepening Amendment — Architect Plan

**Date:** 2026-05-07
**Planner:** Architect agent (Opus)
**Task name:** No-human-baseline + §1.5-deepening amendment
**Originating decision:** Mark, 2026-05-07 — drop human cultural-consensus baseline from the project entirely; expand §1.5 to make corpus-lens framing and exploratory (not hypothesis-testing) posture explicit.
**Source-of-truth document (binding for all downstream work):** `docs/status/2026-05-07-lsb-philosophy-and-framing.md` (commit `d014112`)
**Plan deliverable path:** `docs/status/2026-05-07-no-human-baseline-amendment-architect-plan.md` (this file)

---

## §0. Reading list (mandatory before Coder starts)

The Coder must read all of the following before drafting any edit. Quote, do not re-articulate, the philosophy doc.

1. `docs/status/2026-05-07-lsb-philosophy-and-framing.md` — **the source-of-truth document. All ten sections.** §8 is the canonical "honest tagline" used throughout this amendment. The Coder may not introduce any new philosophical framing — only what is in this document is allowed to be quoted into the canonical project docs.
2. `ARCHITECTURE.md` §1.5 (current state, all sub-sections) and §4.2.5 (full grounding module) and §5.3 Phase 4c paragraph
3. `DESIGN_SYSTEM.md` §3.3, §3.7, §3.8, §4 (entire Grounding Display Specification), §6.1 outline item 5
4. `CLAUDE.md` §6 (R15 specifically), §7 (forbidden vocabulary — unchanged), §9 (pitfalls 3, 4, 12)
5. `docs/DATA_DICTIONARY.md` §2 `DomainResult` and §3 `GroundingRef`
6. `PHASE_4C_CANDIDATE_SOURCES.md` (entire — to confirm reposition vs delete decision in §3 below)
7. `README.md` (entire — affected by this amendment, see §3 below)
8. `PHASE_0_TASKS.md` P0-T2, P0-T3, P0-T5 (grounding-related sub-bullets only)
9. `docs/grounding_submission_template.md` (entire — to be deleted)
10. `.github/PULL_REQUEST_TEMPLATE/grounding_submission.md` (entire — to be deleted)
11. `data/grounding/family/romney_1996/` (4 files exist on disk — see §3 Q5)
12. `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md` — model for methodology-bound text written under the corpus-lens framing
13. `docs/status/2026-05-07-phase4a-t5-redo-analysis-report.md` — uses the philosophy doc §8 framing in current prose
14. `packages/cdb_core/cdb_core/schemas.py` lines 130–186 — the `GroundingRef` schema. **Schema does NOT change in this amendment.**

The Coder must not consult `docs/SME_REVIEW.md`, `docs/BOOTSTRAP_DESIGN.md`, or any other doc as input for new framing prose; those documents are downstream of §1.5 and inherit framing from it, not the other way around.

---

## §1. Deliverable summary

A **coordinated set of doc edits** that encodes Mark's two 2026-05-07 decisions:

1. **Drop the human cultural-consensus baseline** as a comparison axis for the project. Phase 4c (human baseline acquisition) is removed. Romney / D'Andrade / Weller / Borgatti / Batchelder remain as ancestry credit on the methodology page (they invented the protocol LSB borrows). Their published cultural-consensus matrices are not used as comparison data inside LSB. Every domain on the dashboard is, permanently, model-to-model.
2. **Deepen §1.5** to make explicit (a) the five-link corpus-lens chain (`corpus → training → alignment → decoding → output distribution`), (b) the exploratory-not-hypothesis-testing posture, (c) the "honest tagline" from philosophy doc §8 as the canonical short-form summary, (d) the release-for-community-analysis intent, (e) what LSB does and does not measure.

**Strict non-goals:**

- **No code change.** No edits to `packages/cdb_core/cdb_core/schemas.py`, no edits to `packages/cdb_analyze/`, no edits to `apps/dashboard/` components, no edits to scripts.
- **No schema change.** `DomainResult.groundings: list[GroundingRef]` semantic is unchanged. The schema's `human_oci`, `human_oci_ci`, `n_subjects_with_raw_data` fields, the `baseline_kind` literal, the population/method/IRB/submitter fields all remain. Per CLAUDE.md §9 pitfall 3 the empty-list case is already a first-class state. The amendment makes "permanently empty" the new default in practice, not in schema.
- **No dashboard component change.** No new `MDSPlot.tsx` rendering rules, no new `GroundingSelector.tsx` behavior, no new `KeyFinding.tsx` lede templates, no new colors. The Phase 5/6 frontend rendering of methodology-page text is a separate UI/UX-gated effort downstream of this amendment.
- **No Phase 4 gate criteria change.** G1 / G2 / G3 thresholds and definitions are untouched.
- **No Phase 4b sensitivity-study change.**
- **No methodology-page UI build.** That is Phase 5/6 deliverable territory (Mark writes prose, UI/UX gates rendering). This amendment only updates the methodology-page **outline** in `DESIGN_SYSTEM.md` §6.1.
- **No CC-license change.** `data/grounding/` directory remains under `LICENSE-DATA` (CC-BY-4.0) per existing license model.
- **No `data/raw/` or `data/derived/` edits.**

---

## §2. One commit or several — Architect call

**Architect decision: ONE commit.** Single coordinated multi-file edit by one Coder.

**Why one commit:**

1. **Coherence.** Every doc that mentions human baselines updates together. CI never sees an interim master state where ARCHITECTURE.md says "human baseline acquisition is a Phase 4c deliverable" while CLAUDE.md says "researcher submission rule removed." The amendment encodes a single decision; splitting it would scatter the decision across multiple commits and create temporary inconsistencies that the Reviewer would have to reason about file-by-file rather than in aggregate.
2. **No production risk.** Doc-only edits. No code path is altered. No schema migration. No CI behavior change beyond doc-link checks. The "what if a partial-merge state ships" failure mode does not apply.
3. **Reviewer can scan it in one pass.** The diff is large (≈8 files) but each file's edit is bounded — small expansion in `ARCHITECTURE.md` §1.5, surgical removal in §4.2.5 + §5.3, two file deletions, ≈4 small surgical edits in `DESIGN_SYSTEM.md` and `CLAUDE.md` and `docs/DATA_DICTIONARY.md` and `README.md` and `PHASE_0_TASKS.md`. The Reviewer can read this in one sitting; multiple commits would force re-establishing context across each one.
4. **Audit trail is cleaner.** A single commit message points at the philosophy doc, the SME plan-PASS, the SME content-PASS (if Q3 below adopted), and the Reviewer verdict — five files in one referenceable hash. Multi-commit would require the verdict files to track which doc edits live in which commit.

**Commit message (template, binding):**
```
docs(architecture): drop human baseline + deepen §1.5 framing

Encodes Mark's 2026-05-07 decisions: human cultural-consensus baseline
removed from the project; §1.5 expanded to make the corpus-lens chain
and exploratory framing explicit per
docs/status/2026-05-07-lsb-philosophy-and-framing.md.

No code change. No schema change. Doc-only.

Plan: docs/status/2026-05-07-no-human-baseline-amendment-architect-plan.md
SME plan verdict: docs/status/2026-05-07-no-human-baseline-amendment-cda-sme-plan-verdict.md
SME content verdict: docs/status/2026-05-07-no-human-baseline-amendment-cda-sme-content-verdict.md
Reviewer verdict: docs/status/2026-05-07-no-human-baseline-amendment-reviewer-verdict.md
Tester verdict: docs/status/2026-05-07-no-human-baseline-amendment-tester-verdict.md
```

The two file deletions (`docs/grounding_submission_template.md`, `.github/PULL_REQUEST_TEMPLATE/grounding_submission.md`) and the directory-status decision for `data/grounding/family/romney_1996/` (Q5) are in this same commit.

---

## §3. Open questions for SME (Q1 – Q9 with Architect rec)

The SME PASS-level routing of this plan must explicitly rule on each of the following. The Coder may not start until the SME has answered.

**Q1 — `PHASE_4C_CANDIDATE_SOURCES.md`: delete entirely or reposition as ancestry credit?**

- **Architect recommendation: delete entirely.** The philosophy doc §1 says ancestry credit (Romney / D'Andrade / Weller / Borgatti / Batchelder) goes on the **methodology page**, not in a separate candidate-sources doc. A repositioned `PHASE_4C_CANDIDATE_SOURCES.md` would be a vestigial scaffold pointing at a phase that no longer exists; the link weight and naming both signal "we are still acquiring baselines." Methodology-page ancestry credit is a separate, smaller content (a paragraph naming the originators with citations, not a candidate-source spreadsheet with licensing assessments). The methodology-page outline in `DESIGN_SYSTEM.md` §6.1 already includes "Romney, D'Andrade, Weller, Borgatti: named and cited" as item 2 — that is where the ancestry credit lives. Deleting `PHASE_4C_CANDIDATE_SOURCES.md` is the surgical move.
- **If SME prefers reposition:** the doc would need to be retitled (e.g., `docs/CDA_ANCESTRY_CREDIT.md`), gutted of its acquisition-workflow framing, and reduced to a citation list. The Coder must not be asked to perform this conversion under the same plan; it would expand scope. SME ruling needed.

**Q2 — `docs/DATA_DICTIONARY.md` `GroundingRef` description: retained as-is with a "currently empty for all v1 domains" gloss, or trimmed?**

- **Architect recommendation: retained as-is, with a top-of-§3 gloss only.** The schema is unchanged; the data dictionary's job is to document the schema as it exists in code, not as it is exercised in production. A future researcher-submitted baseline (off the LSB roadmap, but the schema admits it) still needs the field documentation. Adding a single short paragraph at the top of §3 — "All `v1` LSB domains ship with an empty `groundings` list; `GroundingRef` is documented for schema completeness and forward compatibility, not because v1 production data populates it." — preserves the open-data contract without overcommitting LSB to baseline acquisition. The 18+ field-level descriptions stay; deleting them would create a gap if the schema field is ever re-exercised.
- **If SME prefers trim:** the §3 sub-sections (3.5 Submitter, 3.8 Register 1 cross-species extension) could be collapsed to "see schema source" pointers. But this trades documentation completeness for symbolic alignment with the new framing. Architect prefers retention.

**Q3 — Does this amendment need its own SME content verdict on the §1.5 expansion prose, analogous to RD-3's S5-completing verdict?**

- **Architect recommendation: yes.** The §1.5 expansion is methodology-bound text. The RD-3 reframing memo had a content-level SME verdict (`docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md`) precisely because methodology prose is more sensitive than methodology code — a forbidden-vocabulary slip in §1.5 propagates into every downstream doc that quotes it. The plan-level SME PASS authorizes the framing strategy; the content-level SME PASS verifies the Coder did not drift from the philosophy doc when writing the actual prose. The two verdicts have different review surfaces: the plan verdict gates the strategy, the content verdict gates the words.
- **If SME prefers single verdict:** the plan-level PASS would have to be unusually detailed, scripting the §1.5 prose at near-quotable specificity. Architect prefers two-stage to preserve normal SME reviewer ergonomics.
- **If adopted, file paths (binding):**
  - Plan-level: `docs/status/2026-05-07-no-human-baseline-amendment-cda-sme-plan-verdict.md`
  - Content-level: `docs/status/2026-05-07-no-human-baseline-amendment-cda-sme-content-verdict.md`

**Q4 — Public-facing texts (`README.md`, social-pipeline drafts, lede generator templates) that mention human baselines: same commit or forward-carry?**

- **Architect recommendation: `README.md` IN this commit. Social-pipeline drafts and lede generator templates: forward-carry.** README.md (lines 5, 26, 41, 51, 57, 61–73, 84) directly references human grounding, the submission template, the submission workflow, and `data/grounding/family/romney_1996/` source.md citation. These are user-facing statements; leaving them in a state where they describe "Submit your data" while the underlying template is deleted would be incoherent. **README.md edits are surgical (≈10 lines edited or removed) and within scope.** The social-pipeline drafts and lede generator templates do not yet exist in `packages/cdb_social/` or `packages/cdb_publish/lede/` (Phase 7 / partly Phase 5 work). When they are written, they will be SME-gated under this amendment's framing. No content exists to amend now.
- **If SME prefers README.md forward-carry:** README is split into a partially-stale state for an unknown duration. Architect rejects.

**Q5 — `data/grounding/` directory: delete, leave as empty placeholder, or leave as-is?**

- **Architect recommendation: leave the four files (`source.md`, `cooccurrence.csv`, `items.txt`, `grounding_ref.json`) under `data/grounding/family/romney_1996/` IN PLACE in this commit. Add a top-level `data/grounding/README.md` that says "This directory contains historical reference data extracted before the 2026-05-07 amendment that removed human baselines from the project; it is preserved for audit-trail completeness and is not consumed by any analysis pipeline. See `docs/status/2026-05-07-lsb-philosophy-and-framing.md` and `docs/status/2026-05-07-no-human-baseline-amendment-architect-plan.md`."**
- **Why retain rather than delete:** (a) deleting working data Mark spent time extracting is a sentimental loss with no architectural gain; (b) the data is already in git history and a deletion commit only obscures provenance, not content; (c) the Romney 1996 attribution in `LICENSE-DATA` (per ARCHITECTURE.md §6.6) refers to `data/grounding/family/romney_1996/` and removing the directory while keeping the license attribution would create a dangling reference; (d) the open-data contract historically promised this directory; an unannounced delete would be a contract break. A README banner is the surgical move.
- **If SME prefers deletion:** the four files are removed, the Romney 1996 LICENSE-DATA attribution is also removed in the same commit, and the open-data-bundle README (when published) treats the file set as never having shipped. This is a larger and more philosophy-driven move than the present amendment requires. Architect prefers retain-with-banner.

**Q6 — "Corpus lens" definition: new central paragraph (e.g., new §1.5.1.1) that all other uses reference, or expand each use in place?**

- **Architect recommendation: new sub-section §1.5.1 expansion. Add a "five-link chain" paragraph to the existing §1.5.1 (which is currently titled "What CDB measures — the precise claim") rather than creating a brand-new sub-section.** The current §1.5.1 already has a "four-layer breakdown of the corpus lens" block (lines 111–118). The five-link chain in philosophy doc §4 is the same idea expressed at slightly different granularity (corpus → training → alignment → decoding → output distribution). The cleanest move is to **replace the current four-layer breakdown with the five-link chain** verbatim from philosophy doc §4, retitled "Five-link breakdown of the corpus lens (revised 2026-05-07)" with a one-sentence note that this supersedes the prior four-layer formulation. This avoids a duplicate breakdown and avoids creating a new sub-section number that other docs would have to cross-reference.
- **If SME prefers separate sub-section:** create §1.5.1.1 with the five-link chain. Existing §1.5.1 four-layer breakdown is left in place. Architect rejects this — it produces a doc with two competing breakdowns of the same concept and forces every downstream reference to disambiguate.
- The replacement is faithful: the four-layer breakdown's items 2 + 3 ("compression and abstraction by pretraining" + "behavioral shaping by RLHF") map cleanly onto the five-link chain's "training" + "alignment" links; the five-link chain adds "decoding" as an explicit link, which the four-layer breakdown collapsed into "surface expression through temperature-sampled token generation" (Layer 4). The five-link version is strictly more explicit, not in conflict with the prior version.

**Q7 — "Exploratory framing — LSB does not test hypotheses": new top-level §1.5.x sub-section (verbatim quote of philosophy doc §2), or fold into existing §1.5 prose?**

- **Architect recommendation: new top-level sub-section §1.5.7, titled "Exploratory framing — LSB does not test hypotheses".** The exploratory posture is a load-bearing claim about what LSB *is*. Burying it in an existing sub-section's prose risks losing it. A dedicated sub-section gives it a visible anchor and a stable cross-reference for the methodology page, the README, and any future ledes that need to explain why the project does not predict-and-confirm. The sub-section's content is a verbatim quote of philosophy doc §2 (with normal formatting fixes for the surrounding doc's voice), preceded by a one-sentence framing introduction in the §1.5.7 voice. The current §1.5.6 ("The website is the artifact") is left in place; the new §1.5.7 sits after it and before the existing §1.6 (Project naming).
- **If SME prefers fold-in:** the exploratory framing goes into §1.5.2 ("Why the reframe is stronger, not weaker") as a fourth bullet. This works structurally but loses the visibility — §1.5.2 is a meta-defense, not a definition; the exploratory framing is a definition.
- **Specifically:** the §1.5.7 must include the originating exploratory question verbatim from philosophy doc §2: *"what happens if you give a large language model a CDA free-list / pile-sort / interview? What comes out?"* The §1.5.7 must close with the release-for-community-analysis intent from philosophy doc §9 — also quoted, not paraphrased.

**Q8 — "Honest tagline" from philosophy doc §8: install in `ARCHITECTURE.md` §1.5 as a quotable block, in `README.md` first paragraph, both, or neither?**

- **Architect recommendation: BOTH.** The honest tagline is the canonical short-form for the project. It belongs in `ARCHITECTURE.md` §1.5 as a binding source-of-truth block (so all other docs that need the short-form quote it from there) and in `README.md` first paragraph (so anyone reading the repo's front door encounters it immediately).
- **In `ARCHITECTURE.md` §1.5:** install as a top-of-§1.5 boxed quote block, immediately after the §1.5 binding-on-all-generated-text statement, before §1.5.1. The Coder copies philosophy doc §8 verbatim (the three-paragraph block from "LSB measures what frontier LLMs produce..." through "...releases the data for the community to interpret."). Surrounding doc-voice introduction: "The canonical short-form description of LSB. All public-facing short summaries (homepage hero, README first paragraph, social posts, conference-style abstracts) draw from this block. Source: `docs/status/2026-05-07-lsb-philosophy-and-framing.md` §8."
- **In `README.md`:** the current first paragraph (lines 5–7 — "LSB is a benchmark for the **corpus lens** of large language models...Where published or contributed human CDA data is available, we put a human reference point on the same map.") is replaced with a tightened version that incorporates the honest tagline's first sentence and removes the "Where published or contributed human CDA data is available, we put a human reference point on the same map" clause. The full three-paragraph tagline is too long for README's first paragraph; the first sentence ("LSB measures what frontier LLMs produce when asked to categorize, in a way that's reproducible, comparable across models, and trackable across time.") is the natural fit. The current "What LSB is and isn't" §9–13 should be lightly edited to remove the "where published or contributed human CDA data is available" framing and reference §1.5 of `ARCHITECTURE.md`.

**Q9 — `PHASE_0_TASKS.md` edits — in scope or out of scope?**

- **Architect recommendation: IN scope, surgical only.** P0-T2 references `LICENSE-DATA` covering `data/grounding/` (line 80) — must be updated to note that `data/grounding/` retains historical reference data per the 2026-05-07 amendment but is no longer a Phase 4c acquisition target. P0-T2 line 85 references the Romney attribution requirement in `LICENSE-DATA` — retain (per Q5 retention decision). P0-T3 line 114 references `groundings: list[GroundingRef] = []` — retain unchanged (schema is unchanged). P0-T3 line 138 references the v0.6 vs v0.7 GroundingRef warning — retain unchanged. P0-T5 line 175 references `GroundingRef` field documentation requirement — retain unchanged (per Q2 retention decision). The only P0 edit is a single line addition to P0-T2 noting that `data/grounding/` now contains historical reference data only; no Phase 4c task work is implied by this Phase 0 reference.
- **If SME prefers out of scope:** PHASE_0_TASKS.md drifts from the new framing for an unknown duration until the next Phase 0 review. Architect prefers in-scope surgical.

---

## §4. UI/UX agent gate decision

**Question:** Does the `DESIGN_SYSTEM.md` edit set go through the UI/UX agent before the Coder, or bypass the UI/UX gate?

**Architect ruling: BYPASS the UI/UX gate.**

**Reasoning:**

1. **No new visual decision.** The amendment makes no visual decision. It removes existing visual decisions (the four-state grounding table, the published-vs-researcher marker shapes, the "+ Submit your data" affordance, the Grounding Detail Panel layout). Removal of pre-approved visual decisions is the opposite of inventing new ones — it is the Coder doing the surgical equivalent of `git rm` on visual specs that no longer apply.
2. **No new component, color, font, spacing, interaction pattern.** The Coder is not asked to pick a single new visual property. The MDS plot's State 0 rendering survives with the only visible change being that **State 0 is the only state**. Star marker (★) and gray diamond (◆) tokens survive in the design tokens (Q5 retains the tokens for archival purposes; if SME rules toward delete, the tokens go away — see Q5 dependency below).
3. **The State-0 prose is already binding.** `DESIGN_SYSTEM.md` §3.3 State-0 row, §3.7 "Researcher contributions welcome" copy, §4.1 State-0 description, and §3.8 conditional behavior are all already in the design system as PASSed visual specs. The amendment's effect on §4.1 is to collapse States 1, 2, 3 into a "removed" footnote and elevate State 0 to "the only state — model-to-model is binding." That elevation is a doc-edit move, not a visual-decision move; the State-0 visual treatment is unchanged.
4. **The methodology-page outline edit (DESIGN_SYSTEM.md §6.1) is text-only.** The §6.1 outline is a text outline, not a visual layout spec. Changing item 5 from "Human grounding" to "What this measures and what it does not" is a content edit. The eventual Phase 5/6 implementation of the methodology page is separately UI/UX-gated when the Coder writes that page; that future gate is not pre-empted by this amendment.

**Risk surface of the bypass call:**

- **Low risk surface 1.** If the Coder, in service of removing the four-state grounding table, accidentally re-flows §4 in a way that affects another visual spec (e.g., the "Conditional behavior" block in §3.8 that refers to "State 0," "State 1," "State 2," "State 3"), that is a Reviewer-catchable error. The Reviewer's PR-level scan will flag any DESIGN_SYSTEM.md edit that introduces or modifies a visual decision (color, marker, layout, spacing) outside the deletion scope.
- **Low risk surface 2.** The `--color-baseline-published` and `--color-baseline-researcher` design tokens (line 80–81) become dead code. Architect recommends leaving the tokens defined-but-unused in this amendment (token deletion is a refactor, not a framing change; doing it now would inflate the diff). A follow-up cleanup task can remove unused tokens once the amendment lands.

**If Mark or SME disagrees** and routes the `DESIGN_SYSTEM.md` edits through the UI/UX agent: the UI/UX gate's verdict file path is `docs/status/2026-05-07-no-human-baseline-amendment-ui-ux-verdict.md`. The UI/UX review questions (OWID design fidelity / 30-second journalist test / researcher reproduce-and-cite test / WCAG AA accessibility) all apply trivially or are unaffected by the deletion-only edit set; the Architect expects a fast PASS if invoked.

---

## §5. Per-file edit specifications (acceptance criteria binding for Coder)

The Coder writes prose for each of the following. The Coder must quote, not re-articulate, philosophy doc framing wherever possible. The Coder must not introduce any framing that is not present in the philosophy doc.

### §5.1 `ARCHITECTURE.md`

**Sub-files / sub-sections affected:** §1.5 (entire — expansion), §2 repository layout (one tree-line edit), §3.2 schema layout (no schema change but documentation gloss), §4.2.5 (full rewrite to pure-archival posture), §5.2 (R15 disposition), §5.3 Phase 4c paragraph (full removal), §5.3 Phase 6 paragraph (researcher-submission line removed), §9 Glossary (multiple entries trimmed), v0.7 changelog footer (one-line entry added).

**§5.1.a §1.5 expansion (the structural heart of the amendment).**

- **§1.5 top-of-section:** install philosophy doc §8 ("honest tagline") as a binding quotable block immediately after the existing "**This section is binding on every other part of the system.**" sentence. Per Q8.
- **§1.5.1 (existing — "What CDB measures — the precise claim"):** replace the current "Four-layer breakdown of the corpus lens (added post-F1 SME review)" block (lines 111–118) with the **five-link chain** from philosophy doc §4, verbatim. Surrounding doc-voice intro: "**Five-link breakdown of the corpus lens (revised 2026-05-07).** The 'corpus lens' phrase compresses a chain of five transformations. Naming them explicitly makes the construct operationally legible and supersedes the prior four-layer formulation:". The existing post-block sentence ("LSB elicitation operates on Layer 4...") is updated to refer to the output-distribution link rather than Layer 4. Per Q6.
- **§1.5.2, §1.5.3, §1.5.4, §1.5.6 — UNCHANGED** (the forbidden vocabulary, the language guardrails, the limitations list, the website-is-the-artifact framing all carry forward unchanged). The "Within-model consensus → Output Concentration Index" rows in §1.5.4 are unchanged.
- **§1.5.5 — full rewrite to "Human grounding — historical context".** The current §1.5.5 ("Human grounding — reference point, not target of measurement") is replaced with a short ≈8-sentence sub-section titled "**Human grounding — removed from v1 (2026-05-07)**." The sub-section explains that an earlier version of the project planned to include published human CDA baselines (Romney 1996 was the v1 target) as reference points on the cross-model MDS plot; that the 2026-05-07 amendment removed human baselines as a comparison axis on philosophical grounds (philosophy doc §1 quoted: "the human baseline is a Trojan horse for the cognition framing the project explicitly disclaims..."); that every domain on the dashboard is, permanently, model-to-model; that the schema's `groundings: list[GroundingRef]` field is retained for forward compatibility but defaults to empty for all v1 domains; that the Romney / D'Andrade / Weller / Borgatti / Batchelder ancestry credit lives on the methodology page (per `DESIGN_SYSTEM.md` §6.1 item 2). The "Floor and ceiling claims" framing block is removed entirely. The "What follows from this framing" 4-point list is removed entirely.
- **NEW §1.5.7 — "Exploratory framing — LSB does not test hypotheses".** Quote philosophy doc §2 verbatim. Per Q7. Closes with philosophy doc §9 release-for-community-analysis intent quoted verbatim.

**§5.1.b §2 repository layout edit.** Lines 248 and 253 of the tree diagram reference `docs/grounding_submission_template.md` and `.github/PULL_REQUEST_TEMPLATE/grounding_submission.md`. **Remove both lines** (file deletions in §5.6 below). The `data/grounding/{domain}/{baseline_id}/` data layout in the architecture diagram (around line 316–322) is **unchanged** per Q5 (retain-with-banner).

**§5.1.c §3.2 schema documentation gloss.** The `GroundingRef` and `DomainResult.groundings` schema text is **unchanged**. Add a one-paragraph editorial note immediately above the `class GroundingRef(BaseModel):` block: "*Editorial note (2026-05-07).* Per the 2026-05-07 amendment removing human baselines from v1, all v1 `DomainResult` instances ship with `groundings = []`. The `GroundingRef` schema is retained for forward compatibility and for documentation completeness; it does not drive any v1 production data flow. See §1.5.5 for the framing rationale." No code edit. Comment-prose edit only.

**§5.1.d §4.2.5 full rewrite to archival posture.** The current §4.2.5 (titled "Human grounding module (`grounding.py`)") is rewritten to an ≈15-line archival sub-section titled "**Human grounding module — historical (removed v1 2026-05-07)**" that:
- States that an earlier v0.7 version of LSB included a `grounding.py` module that loaded zero or more published or researcher-submitted human CDA datasets and injected each as a reference informant in the cross-model MDS;
- States that the 2026-05-07 amendment removed human grounding from the project; the `cdb_analyze/grounding.py` placeholder remains in the package for backward compatibility but is not consumed by any v1 analysis pipeline (Architect's read of `packages/cdb_analyze/__init__.py` and the placeholder posture from PHASE_0_TASKS.md P0-T4); references `docs/status/2026-05-07-lsb-philosophy-and-framing.md` for the rationale;
- Removes the multi-baseline data-layout block (lines 900–923);
- Removes the per-baseline contents block (lines 925–931);
- Removes the item-alignment paragraph (line 933);
- Removes the sourcing-policy paragraph (lines 935–945);
- Removes the v1-acquisition-targets list (lines 940–945);
- Removes the acquisition-workflow-for-published-baselines block (lines 947–953);
- Removes the researcher-submission-workflow block (lines 955–973);
- Removes the "what is not in v1" deferred-to-v2 block (lines 968–973);
- Removes the "acquisition is the one part Mark does by hand" paragraph (line 975);
- Removes the "graceful degradation" paragraph (line 977);
- Removes the "citation discipline" paragraph (line 979).
- The §4.2.6 "Bootstrap uncertainty module" block remains; its "Interaction with grounding" paragraph (line 996) is rewritten to: "*Interaction with grounding (historical).* The v0.7 design called for per-baseline bootstrap ellipses on the MDS plot; per the 2026-05-07 amendment removing human grounding from v1, this interaction is moot. The bootstrap module's per-model ellipses on cross-model MDS remain unchanged."

**§5.1.e §5.2 R15 disposition.** R15 (researcher grounding submission rule, around line 1285) is **removed in full** from the §5.2 list. The numbering of any subsequent rules is preserved (R15 is the last numbered rule; no renumbering required).

**§5.1.f §5.3 Phase 4c paragraph removal.** The Phase 4c paragraph (line 1360) ("*4c. Human baseline acquisition.* Mark acquires...") is **removed in full**. The phase-list ordering becomes 4a → 4b → 4d. The "*4d. Bootstrap validation.*" paragraph (line 1362) is renumbered to "*4c.*" and its "first MDS plot with confidence ellipses and the human baseline marker" phrase is rewritten to "first MDS plot with confidence ellipses for every model in the slate." The Gate criteria table (G1, G2, G3) is **unchanged**.

**§5.1.g §5.3 Phase 6 paragraph edit.** The Phase 6 bullet (line 1386) ("**Open the researcher grounding submission process** (§4.2.5)...") is **removed in full**. The Phase 6 final bullet (line 1389) ("Methodology page first draft (Mark writes or reviews personally — not Coder-generated). The methodology page's 'Human grounding' section...") is rewritten to remove the "explicitly invites researcher contributions and links to the submission template" clause. The Phase 8 "Methodology page finalized" bullet (line 1401) is rewritten to remove the "acknowledges the grounding source (Romney et al. 1996) in full" clause and replace it with "acknowledges the CDA tradition's published precedents (without using their data as an LSB comparison axis)."

**§5.1.h §9 Glossary trimming.** Glossary entries for `Baseline kind`, `Researcher grounding`, `Grounding states (0/1/2/3)`, and `GroundingRef` are **edited to add a one-sentence "(historical, post-2026-05-07 amendment)" gloss** rather than removed — they remain valid schema-level concepts that the data dictionary documents.

**§5.1.i v0.7 changelog footer.** Add a single line entry to the v0.4 REVISION — PENDING EDITS CHECKLIST or to a new "v0.7.1 amendment" anchor noting: "2026-05-07 amendment — human grounding removed; §1.5 expanded with five-link corpus-lens chain and exploratory framing per `docs/status/2026-05-07-lsb-philosophy-and-framing.md`."

**Acceptance criteria for ARCHITECTURE.md edits:**
- All §1.5 expansions quote philosophy doc verbatim (the Reviewer can diff the philosophy doc against the new §1.5 text and find at least the §8 honest tagline and the §2 exploratory question and the §9 release-for-community intent verbatim).
- No new framing language not present in the philosophy doc.
- Forbidden vocabulary scan passes (§1.5.4 substitutions table is unchanged; the new §1.5 prose contains no left-column phrases).
- §5.3 Phase 4c is fully removed; the phase ordering is internally consistent (4a → 4b → 4c bootstrap).
- §4.2.5 is rewritten to archival posture (the 15-line spec above); no production data-flow language remains.
- The schema reference text and the `GroundingRef` field-by-field documentation in §3.2 carry forward unchanged.
- The Phase 4 gate criteria (G1 / G2 / G3) and Phase 4b / 4b runbook / split-G1 prose are untouched.

### §5.2 `DESIGN_SYSTEM.md`

**Sub-sections affected:** §0 design philosophy (one bullet edit), §1.2 color palette (token annotation only), §3.3 MDS plot conditional rendering (table collapse), §3.7 model selector panel (Human baselines section removal), §3.8 key finding strip conditional behavior (states 1/2/3 removal), §4 entire grounding-display specification (rewrite to archival), §4.4 cross-references (point at amended ARCHITECTURE.md sections), §6.1 methodology page outline item 5 (rewrite), §11 component inventory (deletion of `GroundingSelector.tsx`, `GroundingDetailPanel.tsx`, `SubmitGroundingModal.tsx` from the future-component list — these components are not yet implemented).

**§5.2.a §0 Design Philosophy.** The bullet "Researchers — need to reproduce findings, access raw data, and contribute their own human CDA data alongside the model results. LSB exists in part *to* connect to the human CDA research community; the researcher submission path (§4.3) is a first-class affordance, not an afterthought, and the design language must read as an open scientific instrument rather than a closed publication." (line 24) is **rewritten** to: "Researchers — need to reproduce findings and access raw data. LSB releases verbatim prompts (CC0), verbatim model responses (CC-BY-4.0), reproducible numerics with bootstrap configuration documented, and code under permissive license (Apache 2.0). The design language must read as an open scientific instrument: a place where researchers form their own interpretations from reliably produced measurements." (Quotable from philosophy doc §2 + §9.)

**§5.2.b §1.2 color palette annotation.** Lines 79–81 (the human baseline marker color tokens) get an inline comment annotation: "/* Retained for archival reference; not consumed by v1 components per the 2026-05-07 amendment. */" The token names and hex values are unchanged. (Token deletion is a follow-up cleanup task, not in this amendment's scope.)

**§5.2.c §3.3 MDS plot conditional rendering.** The "Conditional rendering by grounding state" 4-row table (around lines 277–282) is **collapsed to a single row.** The intro paragraph (line 275) is rewritten to: "The MDS plot renders model-to-model. Per the 2026-05-07 amendment, no human baseline markers are rendered in v1. The State 0 visual specification below is the only state. The schema retains `DomainResult.groundings: list[GroundingRef]` for forward compatibility but the v1 published data ships with the field empty for all domains."

  | State | Baseline marker(s) | Baseline ellipse(s) | Legend entry |
  |---|---|---|---|
  | **State 0 — model-to-model (the only v1 state)** | None rendered | None rendered | No baseline-related legend entry |

  Lines 259–260 (Human baseline ellipses, Human baseline markers) under "Visual elements, in z-order" are **removed**. Line 263 ("distance to human baseline if available") in Hover tooltip spec is **removed**. Line 271 ("Hover on human baseline marker → tooltip shows citation, n_informants, population, year") under Interactions is **removed**.

**§5.2.d §3.7 Model Selector Panel.** The "Human baselines section" block (lines 382–387) is **removed in full.** The "**Human baselines**" labeled divider, the per-baseline checkbox, the multi-baseline list, the "+ Submit your data" persistent affordance, and the State-0 "This domain is studied model-to-model. Researcher contributions welcome." copy are all **removed**. The Models section (lines 375–380) is **unchanged**.

**§5.2.e §3.8 Key Finding Strip.** The "Conditional behavior" 4-state list (lines 408–411) is **collapsed** to: "The key finding is comparative across the selected models. The lede generator (`ARCHITECTURE.md` §4.2.3) produces declarative, confident copy describing how the selected models organize the domain relative to each other."  The "Under no circumstances does the comparative-only finding (State 0) read as a degraded form of the grounded finding" sentence (line 413) is **removed** (no other state to compare to).

**§5.2.f §4 entire grounding display specification.** §4 (titled "Grounding Display Specification") is **collapsed to a ≈10-line archival sub-section titled "Grounding display — removed (2026-05-07)."** The new §4 contents:
- One paragraph stating that an earlier version of the design system specified a four-state grounding display (none, published, researcher, multiple), each with marker shapes, ellipse rendering rules, and key-finding conditional behavior;
- One paragraph stating that the 2026-05-07 amendment removed human grounding from the project; the four-state framework collapses to "model-to-model only";
- One paragraph stating that `data/grounding/family/romney_1996/` retains historical reference data per the amendment plan but is not consumed by any v1 component;
- A pointer to `ARCHITECTURE.md` §1.5.5 for the framing rationale and `docs/status/2026-05-07-lsb-philosophy-and-framing.md` for the binding source-of-truth.
- §4.1 (The Four Grounding States), §4.2 (Grounding Detail Panel), §4.3 (Data Submission UI), §4.4 (Cross-references) are all **removed in full** as separate sub-sections.

**§5.2.g §6.1 Methodology Page outline item 5.** The current §6.1 item 5 ("5. Human grounding — Why grounding matters when it's available...") and all 6 of its sub-bullets (lines 633–641) are **rewritten** as a new item 5 titled "**5. What this measures and what it does not**" with sub-bullets drawn from philosophy doc §5 + §6 + §8:
- The shape of the model's output distribution under structured CDA elicitation
- What the numbers (Smith's S, Romney CCM, MDS, Procrustes, OCI) describe (output-distribution shape) and what they do not describe (cognition, belief, understanding, cultural consensus)
- Why this is still worth doing: comparative model characterization, drift detection, stability under prompt rephrasing, confabulation under blind-spot conditions, reproducible public benchmark (per philosophy doc §7)
- The "honest tagline" from philosophy doc §8, quotable

**§5.2.h §6.1 Methodology Page outline item 2.** Item 2 ("What is Cultural Domain Analysis?" with sub-bullet "Romney, D'Andrade, Weller, Borgatti: named and cited") is **unchanged** — this is where the ancestry credit lives, per Q1 + philosophy doc §1.

**§5.2.i §11 Component Inventory.** `GroundingSelector.tsx`, `GroundingDetailPanel.tsx`, `SubmitGroundingModal.tsx` are **removed** from the Phase 5 / Phase 6 component lists. These components are not yet implemented in `apps/dashboard/src/components/`; the deletion is from the planned-future-components list, not from existing code.

**Acceptance criteria for DESIGN_SYSTEM.md edits:**
- §3.3, §3.7, §3.8 each render correctly (visually, structurally) in the model-to-model only state. The Coder verifies by reading the surrounding §3 prose and confirming no orphan references to "Human baselines" or "States 1/2/3" or "Submit your data" remain.
- §4 is collapsed to ≈10 lines. The four-state framework is removed.
- §6.1 item 5 reads as a single coherent bullet whose sub-bullets quote philosophy doc §5/§6/§7/§8 verbatim where possible.
- No invented visual decision (per UI/UX bypass call in §4 above).
- Forbidden vocabulary scan passes.

### §5.3 `CLAUDE.md`

**Sub-sections affected:** §2 reading requirements (one row removal), §6 binding rules (R15 removal), §9 pitfalls (3, 4, 12 disposition).

**§5.3.a §2 reading requirements table.** Row 8 ("`docs/grounding_submission_template.md` — Before any work on the researcher submission workflow or before reviewing a researcher submission PR.") is **removed**. Row 7 (`PHASE_4C_CANDIDATE_SOURCES.md`) is **removed** if Q1 ruling is "delete entirely"; if Q1 ruling is "reposition," row 7 is rewritten to point at the repositioned file. Architect rec assumes Q1 = delete.

**§5.3.b §6 binding rules R15 removal.** R15 (line 112: "**Researcher grounding submission PRs** follow the workflow in `ARCHITECTURE.md` §4.2.5...") is **removed in full**. Rules R1–R14 are unchanged.

**§5.3.c §6 binding rules R4 edit.** R4 (line 101: "**Read `PHASE_4C_CANDIDATE_SOURCES.md`** before any grounding work.") is **removed** if Q1 ruling is "delete entirely." If Q1 = "reposition," R4 is rewritten to point at the repositioned ancestry-credit doc.

**§5.3.d §9 pitfall 3 disposition.** Pitfall 3 ("Treating `groundings` as a singleton.") is **edited** to add a leading "(Historical — see ARCHITECTURE.md §1.5.5 for the 2026-05-07 amendment removing human grounding from v1; the schema's list semantic is retained for forward compatibility.)" The body of the pitfall is **otherwise unchanged** because the schema is unchanged and the "list, not singleton" guidance still applies to any code that touches the field.

**§5.3.e §9 pitfall 4 disposition.** Pitfall 4 ("Writing dashboard copy that says 'no human baseline available yet.'") is **edited** to add a leading "(Historical — the 2026-05-07 amendment removed human baselines from v1; this pitfall is preserved as guidance against re-introducing 'no baseline available yet' framing in any future text.)" The body is **otherwise unchanged** because the "absence is not a defect" framing remains relevant to any future generated text describing the project's lack of human grounding.

**§5.3.f §9 pitfall 12 disposition.** Pitfall 12 ("Assuming `data/grounding/{domain}/` is a single directory with one baseline.") is **edited** to add a leading "(Historical — see ARCHITECTURE.md §1.5.5; `data/grounding/` retains historical reference data per the 2026-05-07 amendment, not active production data.)" The body is **otherwise unchanged**.

**Acceptance criteria for CLAUDE.md edits:**
- R15 fully removed.
- §2 row 8 removed; row 7 disposition matches Q1 ruling.
- §9 pitfalls 3, 4, 12 each carry the "(Historical — ...)" gloss; bodies unchanged.
- Forbidden vocabulary scan passes.
- Cross-reference scan: no remaining link to `docs/grounding_submission_template.md` or `.github/PULL_REQUEST_TEMPLATE/grounding_submission.md` from CLAUDE.md.

### §5.4 `docs/DATA_DICTIONARY.md`

**Sub-sections affected:** §2 `DomainResult` (one paragraph annotation), §3 `GroundingRef` (top-of-section gloss), §4 SQLite `groundings` table (annotation).

**§5.4.a §2 `DomainResult` `groundings` field annotation.** The two field rows for `groundings` (line 250) and `selected_baseline_id` (line 251) are **unchanged**. Add a sentence to the "Important:" callout (line 255): "**Note (2026-05-07).** Per the 2026-05-07 amendment removing human baselines from v1 (`ARCHITECTURE.md` §1.5.5), all v1 `DomainResult` instances ship with `groundings = []` and `selected_baseline_id = None`. The schema field is retained for forward compatibility and for documentation completeness; it does not drive v1 production data."

**§5.4.b §3 `GroundingRef` top-of-section gloss.** Add a one-paragraph editorial note immediately after the §3 sub-section heading and before §3.1: "**Editorial note (2026-05-07).** All v1 LSB domains ship with an empty `groundings` list. `GroundingRef` is documented here for schema completeness and forward compatibility, not because v1 production data populates it. See `ARCHITECTURE.md` §1.5.5 for the framing rationale and `docs/status/2026-05-07-lsb-philosophy-and-framing.md` for the binding source-of-truth." Per Q2 (retention recommendation). Sub-sections §3.1 through §3.8 are **unchanged**.

**§5.4.c §4 SQLite `groundings` table annotation.** The "(when present)" parenthetical in the §4 sub-heading is preserved. Add a leading sentence: "Per the 2026-05-07 amendment, v1 open-data-bundle SQLite databases ship with the `groundings` table empty. The table schema is retained for forward compatibility."

**Acceptance criteria for DATA_DICTIONARY.md edits:**
- All schema field documentation carries forward unchanged.
- Three editorial notes (in §2, §3, §4) added with consistent "2026-05-07" anchor and consistent referencing pattern (`ARCHITECTURE.md` §1.5.5 + philosophy doc).
- The Reviewer rule (R7 schema/dictionary lockstep) is satisfied vacuously: no schema change, no dictionary change beyond editorial notes.

### §5.5 `README.md`

**Sub-sections affected:** First paragraph (line 5), Repository structure (line 26), Quick links (line 41), Licenses table (line 51), Romney attribution paragraph (line 57), Contributing human CDA data (lines 61–73), Citation paragraph (line 84).

**§5.5.a First paragraph rewrite.** Line 5 current: "LSB is a benchmark for the **corpus lens** of large language models — the shape a model imposes on a domain, inherited from its training data. We apply Cultural Domain Analysis (CDA), a methodology developed by cognitive anthropologists in the 1970s and 80s to study how human informants organize cultural vocabulary, and we apply it to LLMs as if the models were informants. The result is a comparative map of how different models — Claude, GPT, DeepSeek, Llama, Mistral, Qwen, and others — organize the same set of everyday domain words (family terms, holidays, food, color, emotion). Where published or contributed human CDA data is available, we put a human reference point on the same map."

**Rewrite to:** "LSB measures what frontier LLMs produce when asked to categorize, in a way that's reproducible, comparable across models, and trackable across time. It applies Cultural Domain Analysis (CDA) — a methodology developed by cognitive anthropologists in the 1970s and 80s to study how human informants organize cultural vocabulary — to LLMs as if the models were informants. The result is a comparative map of how different models (Claude, GPT, DeepSeek, Llama, Mistral, Qwen, and others) organize the same set of everyday domain words (family terms, holidays, food, color, emotion). Every domain on the dashboard is, permanently, model-to-model." (Per Q8: install philosophy doc §8 first sentence verbatim. The "Where published or contributed human CDA data..." sentence is removed.)

**§5.5.b Repository structure tree edit.** Line 26 ("`grounding_submission_template.md  # Researcher submission walkthrough`") is **removed** from the tree.

**§5.5.c Quick links edit.** Line 41 ("**Researcher contributions:** [`docs/grounding_submission_template.md`](docs/grounding_submission_template.md)") is **removed** from the Quick links list.

**§5.5.d Licenses table edit.** Line 51 ("Raw responses, processed results, grounding data | **CC-BY-4.0** | `data/raw/`; `data/processed/`; `data/results/`; `data/grounding/`") is **unchanged** (per Q5 retain-with-banner, the directory still exists and falls under CC-BY-4.0).

**§5.5.e Romney attribution paragraph.** Line 57 ("The Romney et al. (1996) family-terms grounding data carries an additional scholarly attribution requirement documented in `data/grounding/family/romney_1996/source.md`...") is **edited** to: "The `data/grounding/family/romney_1996/` directory contains historical reference data extracted before the 2026-05-07 amendment that removed human baselines from v1 (see `docs/status/2026-05-07-lsb-philosophy-and-framing.md`). Per the existing `data/grounding/family/romney_1996/source.md`, the Romney et al. (1996) attribution requirement applies to anyone reusing that file." (The data is still reusable, the attribution still applies, but the data is no longer an LSB comparison axis.)

**§5.5.f Contributing human CDA data section.** The entire section (lines 61–73, from "## Contributing human CDA data" through "Your data is the human half of that comparison.") is **removed in full.**

**§5.5.g Citation paragraph edit.** Line 84 ("If you cite a specific finding that depends on a particular human grounding baseline, please *also* cite the original source of that baseline...") is **removed** (no findings depend on baselines under the new framing).

**Acceptance criteria for README.md edits:**
- First paragraph opens with the philosophy doc §8 first sentence verbatim.
- The "Contributing human CDA data" section (≈13 lines) is fully removed.
- The repository-structure tree, quick-links list, licenses table, and citation paragraph are coherent post-edit (no orphan references to the deleted submission template).
- Forbidden vocabulary scan passes.

### §5.6 File deletions

The following two files are **removed in full** in this commit:

1. `docs/grounding_submission_template.md` — entire file deletion.
2. `.github/PULL_REQUEST_TEMPLATE/grounding_submission.md` — entire file deletion.

The `data/grounding/family/romney_1996/` directory and its four files are **retained** per Q5 retention decision; a new `data/grounding/README.md` is **added** in this commit with the banner text from §3 Q5.

### §5.7 `PHASE_4C_CANDIDATE_SOURCES.md`

**If Q1 ruling = delete entirely (Architect rec):** entire file deletion.

**If Q1 ruling = reposition:** out of scope for this amendment; SME ruling triggers a separate Architect plan to perform the conversion.

### §5.8 `PHASE_0_TASKS.md`

Per Q9 (Architect rec: in scope, surgical only). Single edit at P0-T2 line 80 area: add a one-sentence note that `data/grounding/` retains historical reference data only post-2026-05-07. P0-T3, P0-T5 remain unchanged (the schema and its documentation requirements are unchanged).

### §5.9 New file: `data/grounding/README.md`

Per Q5. Single ≈4-line banner file:

```
This directory contains historical reference data extracted before
the 2026-05-07 amendment that removed human baselines from the
project. The files are preserved for audit-trail completeness and
are not consumed by any v1 analysis pipeline.

See `docs/status/2026-05-07-lsb-philosophy-and-framing.md` and
`docs/status/2026-05-07-no-human-baseline-amendment-architect-plan.md`.

Romney et al. (1996) attribution requirement (per source.md) still
applies to anyone reusing the family/romney_1996/ files outside LSB.
```

---

## §6. Gate verdict file paths (binding)

**Plan-level CDA SME verdict:**
- Path: `docs/status/2026-05-07-no-human-baseline-amendment-cda-sme-plan-verdict.md`
- Required PASS or PASS-WITH-NOTES before Coder may start. FAIL bounces back to Architect.

**Content-level CDA SME verdict (per Q3 — Architect rec yes):**
- Path: `docs/status/2026-05-07-no-human-baseline-amendment-cda-sme-content-verdict.md`
- Required after Reviewer + Tester PASS, before Mark merges the commit. Reviews the actual prose in §1.5, §1.5.5, §1.5.7, the README first paragraph, and the methodology-page outline item 5 against the philosophy doc.

**Reviewer verdict:**
- Path: `docs/status/2026-05-07-no-human-baseline-amendment-reviewer-verdict.md`
- Reviews per `SECURITY_AND_HARDENING.md` §9 Reviewer rules table. Specifically applicable: R7 schema/dictionary lockstep (vacuously satisfied — no schema change, editorial-only dictionary edits); R10 forbidden vocabulary scan (must pass on every edited file); R12 cross-reference integrity (must verify no orphan link to deleted files remains); R13 commit message references the gate verdicts; R14 single-task-per-commit (the amendment is a single coordinated decision).

**Tester verdict (regression-only — prose only):**
- Path: `docs/status/2026-05-07-no-human-baseline-amendment-tester-verdict.md`
- Confirms `uv run pytest && uv run ruff check . && uv run mypy packages/` passes locally (vacuously — doc-only edits should not affect any test). Confirms `npm run build && npm run test && npm run lint` from `apps/dashboard/` passes locally (vacuously — doc-only edits should not affect any frontend test).

**Optional UI/UX verdict:**
- Path: `docs/status/2026-05-07-no-human-baseline-amendment-ui-ux-verdict.md` (only if Mark or SME rules toward routing the `DESIGN_SYSTEM.md` edits through the UI/UX gate, against the Architect bypass rec in §4 above).

---

## §7. Coder task list (single task)

**Task: F-AMEND-2026-05-07-NO-HUMAN-BASELINE.**

**Owner:** Coder (full doc edit set) → Reviewer (forbidden-vocab + cross-reference + structural audit) → Tester (regression check) → CDA SME (final content PASS, per Q3).

**One commit.** No bundling.

**Files touched (final list):**
- Edited: `ARCHITECTURE.md`
- Edited: `DESIGN_SYSTEM.md`
- Edited: `CLAUDE.md`
- Edited: `docs/DATA_DICTIONARY.md`
- Edited: `README.md`
- Edited: `PHASE_0_TASKS.md` (single line per Q9)
- Deleted: `docs/grounding_submission_template.md`
- Deleted: `.github/PULL_REQUEST_TEMPLATE/grounding_submission.md`
- Deleted: `PHASE_4C_CANDIDATE_SOURCES.md` (per Q1 Architect rec)
- Added: `data/grounding/README.md` (per Q5 banner)

**No file touched:**
- `packages/cdb_core/cdb_core/schemas.py` — schema unchanged
- `packages/cdb_analyze/` — placeholder modules unchanged
- `packages/cdb_publish/` — no lede template change
- `packages/cdb_collect/` — no prompt template change
- `packages/cdb_social/` — does not exist yet
- `apps/dashboard/` — no component change
- `scripts/` — no script change
- `data/raw/`, `data/processed/`, `data/results/`, `data/derived/` — no data change
- `data/grounding/family/romney_1996/` — files retained unchanged
- `tests/` — no test change
- Any other file under `docs/status/` (the amendment's own verdict files are written by the gate agents as they review, not by the Coder)

**Coder reading list (mandatory before starting):**
1. This plan in full.
2. `docs/status/2026-05-07-lsb-philosophy-and-framing.md` in full — **the binding source-of-truth.**
3. The plan-level CDA SME verdict at `docs/status/2026-05-07-no-human-baseline-amendment-cda-sme-plan-verdict.md` — must be PASS or PASS-WITH-NOTES before starting.
4. `CLAUDE.md` §6 (binding rules) and §7 (forbidden vocabulary).
5. `ARCHITECTURE.md` §1.5 (current state) — to see what the §1.5 baseline is before the expansion.

**Coder must quote, not re-articulate.** The philosophy doc is the canonical source. The Coder may not introduce any new philosophical framing — only what is in philosophy doc §1 through §10 is allowed to be quoted into the canonical project docs. If the Coder finds a place where the philosophy doc does not say what is needed, the Coder pauses and routes the question back to the Architect; the Coder does not improvise.

**Coder must run before commit:**
- `uv run pytest && uv run ruff check . && uv run mypy packages/`
- `npm run build && npm run test && npm run lint` from `apps/dashboard/`
- `gitleaks detect` (pre-commit hook)
- Forbidden-vocabulary self-scan on every edited file (grep for "worldview", "believes", "thinks", "model X believes", and the §1.5.4 left-column phrases — none should appear as model-facing claims).
- Cross-reference scan: `grep -rn "grounding_submission_template" .` and `grep -rn "grounding_submission.md" .` and `grep -rn "PHASE_4C_CANDIDATE_SOURCES" .` should return zero matches in tracked files (after deletion).

**Acceptance criteria (binding):**

1. Every philosophy-doc-bound section (§1.5 expansion in `ARCHITECTURE.md`, README first paragraph, methodology-page outline item 5 in `DESIGN_SYSTEM.md`) contains verbatim text from `docs/status/2026-05-07-lsb-philosophy-and-framing.md`. The Reviewer can diff philosophy doc §8 against the new ARCHITECTURE.md §1.5 quotable block and find zero substantive divergence.
2. The "honest tagline" from philosophy doc §8 appears in at least two places: `ARCHITECTURE.md` §1.5 top-of-section as a binding quotable block, and `README.md` first paragraph (first sentence form).
3. The five-link corpus-lens chain (philosophy doc §4) replaces the four-layer breakdown in `ARCHITECTURE.md` §1.5.1.
4. The exploratory framing (philosophy doc §2) appears as a new top-level §1.5.7 sub-section in `ARCHITECTURE.md`, quoted verbatim, closed with the philosophy doc §9 release-for-community-analysis intent quoted verbatim.
5. The current `ARCHITECTURE.md` §1.5.5 ("Human grounding — reference point, not target of measurement") is rewritten to "Human grounding — removed from v1 (2026-05-07)" per §5.1.a.
6. `ARCHITECTURE.md` §4.2.5 is rewritten to ≈15-line archival sub-section per §5.1.d.
7. `ARCHITECTURE.md` §5.3 Phase 4c paragraph is removed; phase ordering becomes 4a → 4b → 4c (renumbered from 4d).
8. `ARCHITECTURE.md` §5.2 R15 is removed in full.
9. `DESIGN_SYSTEM.md` §3.3 conditional rendering table is collapsed to a single State-0 row.
10. `DESIGN_SYSTEM.md` §3.7 Human baselines section is removed.
11. `DESIGN_SYSTEM.md` §3.8 Conditional behavior list is collapsed to a single comparative-only paragraph.
12. `DESIGN_SYSTEM.md` §4 entire grounding-display specification is collapsed to ≈10-line archival sub-section.
13. `DESIGN_SYSTEM.md` §6.1 methodology page outline item 5 is rewritten per §5.2.g.
14. `DESIGN_SYSTEM.md` §11 component inventory removes `GroundingSelector.tsx`, `GroundingDetailPanel.tsx`, `SubmitGroundingModal.tsx` from the planned-future-component list.
15. `CLAUDE.md` §6 R15 is removed; R4 is removed (per Q1 Architect rec); §2 reading requirements row 8 (and row 7 per Q1) is removed; §9 pitfalls 3, 4, 12 each carry a "(Historical — ...)" gloss.
16. `docs/DATA_DICTIONARY.md` §2, §3, §4 each carry a 2026-05-07 editorial note. All schema field documentation is otherwise unchanged.
17. `README.md` first paragraph rewritten per §5.5.a; "Contributing human CDA data" section removed in full; Romney attribution paragraph rewritten per §5.5.e; quick-links and tree diagram orphan references removed.
18. `PHASE_0_TASKS.md` P0-T2 receives a single-line note per Q9.
19. `docs/grounding_submission_template.md` deleted.
20. `.github/PULL_REQUEST_TEMPLATE/grounding_submission.md` deleted.
21. `PHASE_4C_CANDIDATE_SOURCES.md` deleted (per Q1 Architect rec).
22. `data/grounding/README.md` added with the Q5 banner text.
23. `data/grounding/family/romney_1996/` is unchanged (four files retained).
24. **No code, no schema, no test, no fixture, no script, no data-record edit.** Doc-only.
25. Commit message follows the §2 template above and references the plan path, the SME plan verdict path, the SME content verdict path, the Reviewer verdict path, the Tester verdict path.
26. Forbidden-vocabulary scan passes on every edited file.
27. Cross-reference integrity: zero remaining links to deleted files.
28. `uv run pytest && uv run ruff check . && uv run mypy packages/` passes locally.
29. `npm run build && npm run test && npm run lint` from `apps/dashboard/` passes locally.

---

## §8. Dependency order (single task — but with internal sequencing)

The Coder writes the doc edits in a single commit. The internal ordering of edits within that commit (the order in which the Coder works through the files) is recommended as follows for ergonomic reasons; the Reviewer does not enforce this ordering:

1. **First: read the philosophy doc in full.** Without this, no other work can start.
2. **Second: edit `ARCHITECTURE.md` §1.5.** This is the structural heart of the amendment; every other edit (CLAUDE.md, DESIGN_SYSTEM.md, README.md, DATA_DICTIONARY.md) cross-references §1.5.5 and §1.5.7. Get §1.5 right first.
3. **Third: edit `ARCHITECTURE.md` §4.2.5, §5.2, §5.3.** These are the structural removals of the v0.7 grounding architecture. They depend on §1.5.5 being in place to point at.
4. **Fourth: edit `ARCHITECTURE.md` §3.2 schema gloss, §9 glossary, v0.7 changelog footer.** Surface edits.
5. **Fifth: delete the two file-deletion targets** (`docs/grounding_submission_template.md` and `.github/PULL_REQUEST_TEMPLATE/grounding_submission.md`), and `PHASE_4C_CANDIDATE_SOURCES.md` per Q1.
6. **Sixth: edit `DESIGN_SYSTEM.md` §0, §1.2 token annotation, §3.3, §3.7, §3.8, §4, §6.1, §11.** All §3 + §4 edits cross-reference the now-amended `ARCHITECTURE.md` §1.5.5.
7. **Seventh: edit `CLAUDE.md` §2, §6, §9.** Removes references to deleted files; cross-references the amended `ARCHITECTURE.md` §1.5.5.
8. **Eighth: edit `docs/DATA_DICTIONARY.md` §2, §3, §4.** Editorial notes only.
9. **Ninth: edit `README.md`.** First paragraph rewrite + section removal + quick-links cleanup.
10. **Tenth: edit `PHASE_0_TASKS.md` P0-T2.** Single line.
11. **Eleventh: add `data/grounding/README.md`.** Banner.
12. **Twelfth: run all the test suites and the forbidden-vocab scan and the cross-reference scan.**
13. **Thirteenth: write the commit message per the §2 template.**

The Coder may interleave these (e.g., edit `CLAUDE.md` §9 before fully closing out `ARCHITECTURE.md` §9 glossary) if the surrounding prose flow demands it; the Reviewer cares about the final commit's coherence, not the keystroke order.

---

## §9. Risk surface and mitigations

**Risk 1: The Coder drifts from the philosophy doc and writes new framing.**
- *Mitigation:* The plan explicitly forbids it (§7 acceptance criteria 1, 2, 3, 4, 5; §0 reading list note; §3 Q3 SME content verdict). The CDA SME content-level verdict (per Q3) catches drift.

**Risk 2: The Coder breaks a cross-reference link by deleting a file but missing a remaining reference.**
- *Mitigation:* §7 acceptance criterion 27 requires a cross-reference scan (`grep -rn` for the three deletion targets). The Reviewer's R12 cross-reference integrity rule independently checks this.

**Risk 3: The Coder edits `packages/cdb_core/cdb_core/schemas.py` thinking the schema needs to match the framing.**
- *Mitigation:* Plan §1 explicitly states "no schema change." Acceptance criterion 24 forbids it. The Reviewer's R7 (schema/dictionary lockstep) flags any unexpected schema diff.

**Risk 4: The Coder accidentally removes the `data/grounding/family/romney_1996/` directory.**
- *Mitigation:* Plan §3 Q5 explicitly retains the directory. Acceptance criterion 23 forbids change to those four files. The Reviewer can verify via `git status` and `git diff data/grounding/`.

**Risk 5: The Coder reads `docs/SME_REVIEW.md` or `docs/BOOTSTRAP_DESIGN.md` for additional framing input and pollutes the prose.**
- *Mitigation:* Plan §0 reading list explicitly says those docs are not framing inputs (they are downstream of §1.5).

**Risk 6: The UI/UX bypass call (§4) is wrong — the `DESIGN_SYSTEM.md` edit set is large enough that something visual is being decided.**
- *Mitigation:* Plan §4 lays out the bypass reasoning in detail; the Reviewer can flag any visual decision not in the deletion-only scope. If the SME or Mark disagrees, the bypass is reversible — the plan explicitly identifies the UI/UX verdict path that would be added.

**Risk 7: The `data/grounding/README.md` banner introduces forbidden vocabulary or framing drift.**
- *Mitigation:* §5.9 specifies the exact ≈4-line banner text. The Coder may not exceed those four lines. The Reviewer's forbidden-vocab scan covers it.

**Risk 8: The §1.5.5 rewrite fails to make the framing transition feel coherent — the new sub-section reads as "we deleted this" rather than as "we made a positive decision."**
- *Mitigation:* The §5.1.a spec mandates a quote from philosophy doc §1 ("the human baseline is a Trojan horse for the cognition framing the project explicitly disclaims..."). The CDA SME content-level verdict (Q3) catches a disjointed rewrite.

---

## §10. Glossary of plan terms (for SME convenience)

- **Honest tagline.** Philosophy doc §8 — the canonical short-form description of LSB. Three paragraphs ending "releases the data for the community to interpret."
- **Five-link corpus-lens chain.** Philosophy doc §4 — `corpus → training → alignment → decoding → output distribution`. Replaces the existing four-layer breakdown in `ARCHITECTURE.md` §1.5.1.
- **Exploratory framing.** Philosophy doc §2 — LSB is not hypothesis-testing. Originating question: *"what happens if you give a large language model a CDA free-list / pile-sort / interview? What comes out?"*
- **Release-for-community-analysis intent.** Philosophy doc §9 — LSB ships verbatim prompts, verbatim responses, reproducible numerics, and code; community draws conclusions.
- **Ancestry credit.** Philosophy doc §1 — Romney / D'Andrade / Weller / Borgatti / Batchelder named on the methodology page (per `DESIGN_SYSTEM.md` §6.1 item 2) without their published cultural-consensus matrices being used as comparison data inside LSB.
- **Per-domain optional and multi-baseline by default.** Pre-amendment v0.7 framing — superseded by "all v1 domains are model-to-model, permanently."
- **Floor / ceiling claims.** Pre-amendment v0.7 framing for grounding strength — removed in full from §1.5.5.

---

*End of Architect plan. The CDA SME is the next gate. Mark dispatches the SME separately.*
