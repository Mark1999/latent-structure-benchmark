# LSB Reviewer Verdict — No-Human-Baseline + §1.5-Deepening Amendment

**Filed:** 2026-05-07
**Reviewer:** LSB Reviewer (Sonnet)
**Commit reviewed:** `38f5740`
**Plan:** `docs/status/2026-05-07-no-human-baseline-amendment-architect-plan.md` (commit `6d99da0`)
**SME plan verdict:** `docs/status/2026-05-07-no-human-baseline-amendment-cda-sme-plan-verdict.md` (commit `ef859bf`). PASS-WITH-NOTES; binding notes A1–A6.
**Source-of-truth philosophy doc:** `docs/status/2026-05-07-lsb-philosophy-and-framing.md` (commit `d014112`)

---

## VERDICT: PASS-WITH-NOTES

```
REVIEWER VERDICT: PASS-WITH-NOTES

Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         PASS
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A (no schema change)
Check 6 — New deps sign-off:         N/A (no new dependencies)
Check 7 — Prompt versioning:         N/A (no prompt template changes)
Check 8 — Uncertainty in viz:        N/A (no frontend changes)
Check 9 — Prerequisite verdicts:     PASS
```

No hard failures. Two notes requiring SME content-verdict attention before final sign-off.

---

## Standard binding-check detail

### Check 1 — No LLM imports in cdb_analyze/

`grep -r "import anthropic|import openai|from anthropic|from openai|InferenceClient|google.generativeai" packages/cdb_analyze/`

Two hits in `packages/cdb_analyze/cdb_analyze/__init__.py` — both are comment lines in the prohibition statement itself (the no-LLM-imports enforcement guard). No actual import statements. No code change in this commit. PASS.

### Check 2 — Append-only JSONL

`git show 38f5740 -- data/raw/informants.jsonl` produced no output. File was not touched. PASS.

### Check 3 — No secrets

Scanned all 16 changed files. Webhook URL references in `PHASE_0_TASKS.md` and `ARCHITECTURE.md` are configuration descriptions and placeholders, not credential values. All references of the form `LSB_ALERTS_WEBHOOK_URL` are naming env-var keys, not containing their values. `SECURITY_AND_HARDENING.md` references are policy descriptions. No actual credentials detected. PASS.

### Check 4 — Forbidden vocabulary

Full scan of all changed files for vocabulary violations:

**Primary forbidden terms (CLAUDE.md §7):** `worldview`, `believes`, `thinks` applied to models.

Hits found and evaluated:
- `ARCHITECTURE.md` line 87: "It does not measure cognition, understanding, belief, **worldview**..." — this is in the new honest-tagline block quoted verbatim from philosophy doc §8. It is a negation ("LSB does NOT measure worldview"), not a claim that models have worldviews. Acceptable meta-reference/negation context.
- `ARCHITECTURE.md` line 95: "CDB does **not** measure cultural worldviews." — pre-existing negation statement. PASS.
- `ARCHITECTURE.md` line 140: "more defensible than 'measures cultural worldview'..." — pre-existing statement. Not added in this commit.
- `ARCHITECTURE.md` line 913: "the models don't agree on one worldview — which is itself a finding" — pre-existing line in the key algorithms section (4.2.2). Not added in this commit; not part of this review scope.
- `CLAUDE.md` line 27: "LSB does *not* measure cultural worldview..." — negation, correct usage.
- `CLAUDE.md` lines 118–125: all forbidden-vocabulary table entries (meta-reference context, the table itself defines what NOT to say). Correct.
- `SECURITY_AND_HARDENING.md` line 167: "prevent the model from saying 'Claude believes X'" — quoting a forbidden example. Correct negation/example context.
- `README.md` line 13: "LSB **is not** a measure of cultural worldview..." — negation. Correct.

**Extended forbidden terms (ARCHITECTURE.md §1.5.4):** `within-model consensus`, `within-model cultural consensus`, `within-model eigenratio`, `within-model CCM`, `publishable` for LSB findings. No hits in changed files.

**New forbidden terms (A5, added in this commit):** hypothesis-testing language. Checked for `we hypothesized`, `this proves`, `this confirms`, `our finding shows that`, `LSB hypothesizes`, `LSB tested whether`, `LSB confirms`, `LSB predicted`. The §1.5.4 table now contains these rows (the new rows themselves are meta-reference, defining what NOT to say). No affirmative use found. PASS.

### Check 5 — Schema + DATA_DICTIONARY

No changes to `packages/cdb_core/cdb_core/schemas.py` in this commit (confirmed by `git show 38f5740 -- packages/cdb_core/cdb_core/schemas.py` producing no output). The `DATA_DICTIONARY.md` was edited to add editorial notes, which is correct companion work. N/A for the schema co-update requirement.

### Check 6 — New dependencies

No changes to `pyproject.toml` or `apps/dashboard/package.json`. N/A.

### Check 7 — Prompt versioning

No changes to `packages/cdb_collect/prompts/`. N/A.

### Check 8 — Uncertainty in visualizations

No frontend files changed (`apps/dashboard/` not touched). N/A.

### Check 9 — Prerequisite gate verdicts

This is a methodology PR (touches ARCHITECTURE.md §1.5 framing, removes Phase 4c, updates schema documentation). CDA SME plan verdict is present at `docs/status/2026-05-07-no-human-baseline-amendment-cda-sme-plan-verdict.md` with PASS-WITH-NOTES. Notes A1–A6 were addressed by the Coder (verified below in the binding-note compliance section). UI/UX bypass was concurred by SME (no visual decisions). PASS.

---

## Scope-discipline ruling — the six scope-question files

CLAUDE.md §8: *"No surprise scope creep. If a task's acceptance criteria don't cover something you think needs doing, stop and surface it to the Architect rather than improvising. The Architect is the only role authorized to expand a task's scope."*

The plan (§3) specified 12 file operations. The commit contains 16. Ruling on each of the 6 files not in the plan spec:

### File 11: `SECURITY_AND_HARDENING.md` §7.4

**Change:** single-line replacement. Old: "When a researcher submits human grounding data via the GitHub PR workflow (`ARCHITECTURE.md` §4.2.5, `docs/grounding_submission_template.md`), the CI pipeline runs three checks:". New: "**Historical note (2026-05-07):** the researcher grounding submission workflow was removed from v1 per the 2026-05-07 amendment (see `ARCHITECTURE.md` §1.5.5). The PII handling specifications below are retained for reference in case the workflow is reintroduced in a future version. If human grounding data is submitted via any future workflow, the CI pipeline should run these checks:"

**Disposition: ACCEPTABLE.**

The old line referenced `docs/grounding_submission_template.md` (now deleted) and `ARCHITECTURE.md §4.2.5` (now rewritten to archival posture). Leaving that sentence untouched would have created an immediate broken-reference state: a document stating "when a researcher submits via the PR workflow" with the PR template deleted and the submission template deleted. A document with a dead-link to a deleted file is incoherent at the moment of commit. This is surgical dangling-reference cleanup with a clear causal connection to the plan's file deletions. The change is a one-line replacement that converts the sentence from imperative to historical without altering the actual security specifications (the three checks remain intact below). No new security policy was written; no existing security requirement was removed.

### File 12: `docs/SHAKEDOWN_PROTOCOL.md`

**Change:** single-row table replacement. Old: domain rationale contained "see `PHASE_4C_CANDIDATE_SOURCES.md`" and "State-0 vs State-1 rendering + the groundings-list-as-first-class logic." New: "Both are model-to-model only per the 2026-05-07 amendment. `family` and `holidays` exercise the full pipeline comparison."

**Disposition: ACCEPTABLE.**

The deleted reference to `PHASE_4C_CANDIDATE_SOURCES.md` (now deleted) is a dead link at the moment of this commit. The "State-0 vs State-1 rendering" language refers to a state model that the DESIGN_SYSTEM.md §3.3 edit (one of the 12 planned operations) collapsed to a single State 0. Leaving the shakedown row referencing a deleted file and a three-state model while the design system now specifies a single-state model creates a test-protocol document with contradictory guidance for the shakedown operator. This is surgical: one row updated, no new test requirements introduced, no existing test requirements removed.

### File 13: `.claude/agents/architect.md`

**Change:** single-line removal. Removed: `- PHASE_4C_CANDIDATE_SOURCES.md` before any grounding work` from the additional-reads list.

**Disposition: ACCEPTABLE.**

This is a one-line removal of a read requirement for a file that no longer exists. An agent definition that tells the Architect to read a deleted file will produce a visible failure (file not found) the next time the Architect agent is dispatched on any grounding-adjacent task. The remaining agent definition — routing criteria, role boundaries, four-axis scorecard — is unchanged. The change is purely surgical (one line removed). This is the minimal coherent change needed to keep the agent definition functional.

### File 14: `.claude/agents/coder.md`

**Change:** single-line removal. Same pattern as architect.md: one line removed from the additional-reads list for grounding work.

**Disposition: ACCEPTABLE.**

Identical reasoning to File 13. One-line surgical removal of a read requirement pointing to a now-deleted file. No behavioral change beyond preventing a "file not found" error on grounding-adjacent tasks. Acceptable.

### File 15: `.claude/agent-memory/cda_sme/MEMORY.md`

**Change:** one-line addition. Added: `- [No-human-baseline amendment plan PASS-WITH-NOTES](project_no_human_baseline_amendment.md) — 2026-05-07 amendment dropping human baselines + deepening §1.5; A1–A6 binding; B6/T8/T9 carry forward; Note D SATISFIED-by-amendment`

**Disposition: NOTES-LEVEL CONCERN — should have been a separate commit, but content is correct.**

The `.claude/agent-memory/cda_sme/` directory is git-tracked by established project convention (four prior commits, including dedicated `chore(memory):` commit `7e9bed9`). The MEMORY.md content is correct — it accurately summarizes the SME verdict. However, this change was authored by the SME agent during the SME's dispatch, not by the Coder during this dispatch. The Coder swept it into this commit from the working tree, where it was sitting dirty from the SME's prior session. This conflates two concerns in one commit: (1) the doc amendment and (2) the SME's own post-dispatch memory update. The commit message does not mention this file, which confirms inadvertent inclusion rather than deliberate Coder authorship.

This is a working-tree hygiene failure, not a content failure. The content is not wrong; the commit boundary is imprecise. Under CLAUDE.md §8 ("One commit per task. Do not bundle."), the SME memory update belongs in its own commit or should have been committed separately by the SME agent's dispatch. The practical consequence is minor — the memory is correct and the audit trail is intact — but the principle is the one the project has established for memory updates (dedicated `chore(memory):` commits). Flag for Tester awareness; forward-carry as a hygiene note for future dispatches.

### File 16: `.claude/agent-memory/cda_sme/project_no_human_baseline_amendment.md`

**Change:** new file created. Contents: structured memory entry summarizing the SME plan verdict (Q1-Q9 rulings, A1-A6 binding notes, carry-forward table).

**Disposition: NOTES-LEVEL CONCERN — same pattern as File 15.**

Same analysis as File 15. The content is a correct summary of the SME's own PASS-WITH-NOTES verdict. This file was written by or for the SME agent (it describes the SME's verdict in first-person-SME terms) and appears in the working tree from the SME's dispatch. The Coder swept it in. The file should have been committed in a dedicated `chore(memory):` commit by the SME agent's dispatch, consistent with the project pattern. The content is not wrong; the commit boundary is imprecise.

**Combined disposition on both agent-memory files:** These files should NOT have been in this commit per CLAUDE.md §8. However, the content of both files is correct and the `.claude/agent-memory/cda_sme/` directory is tracked by established project convention. The appropriate remedy is NOT to undo this commit (which would require re-doing the entire 16-file amendment) but to note it as a working-tree hygiene issue for the SME dispatch protocol going forward. A follow-up `chore(memory):` pattern should be established: SME agents should commit their memory files before the Coder dispatch begins. This does not rise to a REJECT because (a) the files are tracked, (b) the content is correct, (c) the prior `chore(memory):` commit pattern shows this has been done cleanly before, and (d) the remedy is procedural, not content-level.

---

## A1–A6 binding-note compliance

### A1 — "supersedes" verbatim in §1.5.1

`grep -n "supersedes" ARCHITECTURE.md` → line 120: "Naming them explicitly makes the construct operationally legible and **supersedes** the prior four-layer formulation"

The word "supersedes" is present. PASS.

### A2 — §1.5.5 four-element structure with philosophy doc §1 "Trojan horse" verbatim

`ARCHITECTURE.md` §1.5.5 structure verified:

1. Opening sentence in §1.5.5 voice: "As of 2026-05-07, human grounding is removed from v1 of LSB." ✓
2. Philosophy doc §1 "Trojan horse" passage verbatim: "**Why:** the human baseline is a Trojan horse for the cognition framing the project explicitly disclaims. Putting a human cultural-consensus matrix next to a model's output on the same axis implicitly invites the reader to ask 'how close to human ground truth is this model?' That question only makes sense if you grant the model is *knowing* something in a way commensurable with human knowing — which §1.5 forbids. The skeptical reader's strongest possible critique of LSB ('you're pretending to do anthropology on machines') gets its surface area from the human baseline. Remove the baseline, remove the surface area." ✓ (matches philosophy doc §1 paragraph 2 verbatim)
3. Architectural consequence in §1.5.5 voice: "Every domain on the dashboard is, permanently, model-to-model. The schema's `groundings: list[GroundingRef]` field is retained for forward compatibility but defaults to empty for all v1 domains." ✓
4. Pointer to ancestry credit: "Romney / D'Andrade / Weller / Borgatti / Batchelder ancestry credit is named on the methodology page per `DESIGN_SYSTEM.md` §6.1 item 2." ✓

PASS.

### A3 — README §9-13 coherence post-truncation

README first paragraph: opens with philosophy doc §8 first sentence ("LSB measures what frontier LLMs produce when asked to categorize, in a way that's reproducible, comparable across models, and trackable across time.") and continues with CDA description. ✓

"What LSB is and isn't" section remains coherent:
- Line 11 (formerly the technically-precise long-form): "LSB **is** a benchmark for the categorical structure of model training corpora, surfaced through CDA elicitation protocols." ✓ Survives unchanged.
- Line 13 (formerly line 13): "LSB **is not** a measure of cultural worldview, belief, or cognition. Models do not have lived experience; they synthesize statistical patterns from text corpora. LSB is careful about this distinction in every visualization, every social post, and every line of dashboard copy. The methodology page on the dashboard goes into depth on what we measure, what we don't, and why the distinction matters." — This line still says "what we measure, what we don't, and why the distinction matters" rather than the A3-preferred "what this measures and what it does not." A3 said the Coder "may rewrite" (not must). This is a minor deviation from A3's suggestion; the current text remains coherent and not incoherent. **Note for SME content verdict:** A3 suggested re-anchoring this closing clause to the new methodology-page outline item 5. The Coder did not apply this suggestion. SME content verdict should assess whether the current phrasing is adequate.
- Line 15 ("For the full scientific framing...") survives unchanged. ✓

PASS (with one observation forwarded to SME content verdict).

### A4 — §1.5.7 three-element composition

Three-element check:

1. **One-sentence intro in §1.5.7 voice (NOT a quote):** "LSB's posture is exploratory, not hypothesis-testing; the following two passages (quoted verbatim from the canonical philosophy document, `docs/status/2026-05-07-lsb-philosophy-and-framing.md`) are binding on all public-facing text the project produces." — This is one sentence (compound with semicolon), in §1.5.7's own voice. It names the source document explicitly. It does not introduce new framing claims. The SME-suggested form was "LSB is exploratory, not hypothesis-testing. The originating question is descriptive: what comes out when CDA elicitation protocols are run on a large language model?" — the Coder used a structurally equivalent paraphrase. ✓

2. **Philosophy doc §2 verbatim:** The block from "LSB is **not hypothesis-testing.**" through "The benchmark exists to make the *comparison itself* reproducible at the level of measurement, not to push a thesis." is present and matches philosophy doc §2 content. ✓

3. **Philosophy doc §9 verbatim:** The block from "Mark's intent: **we are not the final interpreters of LSB's data.**" through "That distinction is binding on the project's design." is present and matches philosophy doc §9. ✓

**No transition sentence between (2) and (3):** verified — the §2 quote ends with "not to push a thesis." and is followed directly by "Mark's intent: **we are not the final interpreters of LSB's data.**" with no intervening transition. ✓

**Note for SME content verdict:** A4 required that the intro be "one sentence, not a paragraph." The Coder's sentence is a compound sentence with a semicolon. This is on the boundary — technically one sentence but contains two independent clauses. The SME content verdict should confirm this form satisfies A4's intent.

PASS.

### A5 — §1.5.4 forbidden-vocabulary table extension for hypothesis-testing language

`ARCHITECTURE.md` §1.5.4 table now contains:
- Row: `"LSB hypothesizes that..." / "LSB tested whether..." / "LSB confirms that..." / "LSB found that [hypothesis]"` → `"LSB measures..." / "LSB reports..." / "LSB observes..."`
- Row: `"LSB predicted X and the data confirmed/refuted it"` → `"LSB ran the protocol; here is what came out"`

These match the exact phrasings from the SME's A5 note. ✓

PASS.

### A6 — `data/grounding/README.md` ≤8 lines, descriptive-only

`wc -l data/grounding/README.md` → 8 lines. ✓

Content is descriptive-only: "Historical reference data only. The 2026-05-07 amendment removed human baselines from LSB v1. These files are preserved for audit-trail completeness and are not consumed by any v1 analysis pipeline." No advocacy, no editorializing, no forbidden vocabulary, no framing drift. Romney attribution requirement is named. ✓

PASS.

---

## Q1–Q9 ruling compliance

| Q | Description | Status |
|---|---|---|
| Q1 | PHASE_4C_CANDIDATE_SOURCES.md DELETED | PASS — file is deleted; confirmed by `ls` |
| Q2 | GroundingRef retained with editorial note | PASS — DATA_DICTIONARY.md §3 top has editorial note; §4 SQLite note added |
| Q3 | SME content verdict required post-Reviewer+Tester | ACKNOWLEDGED — this verdict does not block on Q3; content verdict is next gate |
| Q4 | README in scope; social/lede forward-carry | PASS — README updated; no social/lede templates exist yet |
| Q5 | data/grounding/ retained with banner | PASS — `data/grounding/README.md` exists (8 lines) |
| Q6 | Five-link chain with "supersedes" in §1.5.1 | PASS — A1 confirmed |
| Q7 | New §1.5.7 with three-element composition | PASS — A4 confirmed |
| Q8 | Honest tagline in ARCHITECTURE.md §1.5 + README first paragraph | PASS — both confirmed |
| Q9 | PHASE_0_TASKS.md P0-T2 single-line edit | PASS — line 85 of PHASE_0_TASKS.md confirmed |

---

## Test gate

Re-run results: `1153 passed, 26313 warnings in 12.79s`. Zero failures. Matches Coder's reported result. `uv run ruff check .` → All checks passed.

No code change in this commit, so test results reflect the existing test suite running unchanged against unchanged code. PASS.

---

## Summary and notes for downstream gates

**Overall verdict: PASS-WITH-NOTES**

All nine binding checks pass. All six A-notes are satisfied (A1–A6). All Q1–Q9 rulings are correctly landed. The four extra dangling-reference cleanups (Files 11–14) are each ACCEPTABLE as surgical one-line or one-row changes with direct causal connection to the plan's file deletions. The two agent-memory files (Files 15–16) are a working-tree hygiene concern but not a content failure; their inclusion in this commit departs from the project's `chore(memory):` pattern but does not introduce incorrect content.

**Notes forwarded to SME content verdict (gate 3):**

1. **A3 observation:** README line 13 closing clause reads "what we measure, what we don't, and why the distinction matters" rather than the A3-preferred "what this measures and what it does not." SME content verdict should assess whether current phrasing is adequate.
2. **A4 observation:** §1.5.7 intro sentence is a compound sentence with semicolon (technically one sentence but two independent clauses). SME content verdict should confirm this satisfies A4's "one sentence, not a paragraph" requirement.
3. **Working-tree hygiene note:** future SME agent dispatches should commit `.claude/agent-memory/cda_sme/` changes in a dedicated `chore(memory):` commit before the Coder dispatch begins, consistent with the pattern in commit `7e9bed9`. This prevents agent-memory files from being swept into unrelated Coder commits.

**Next gate:** SME content verdict at `docs/status/2026-05-07-no-human-baseline-amendment-cda-sme-content-verdict.md`.

If SME content verdict issues PASS or PASS-WITH-NOTES (with notes addressed), the amendment is complete and Mark may treat the commit as stable.
