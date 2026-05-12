---
filed: 2026-05-12
reviewer: CDA SME agent (Opus)
task: Phase 6 T7 — FreeListCompare (R10 uncertainty methodology fallback)
slack_channel: "#lsb-cda-sme"
verdict: PASS-WITH-NOTES
---

# Phase 6 T7 — CDA SME verdict on the FreeListCompare plan

**VERDICT: PASS-WITH-NOTES**

The Architect's proposed §2.2 fallback — using `sutrop_csi[modelId][i].f_mentions /
sutrop_csi[modelId][i].n_runs` as the R10 per-term uncertainty representation in
lieu of a bootstrap-resample inclusion frequency — is methodologically sound at the
0.2 corpus's n_runs = 4 and is **approved**.

T7 proceeds as planned. T7a (`cdb_publish` bootstrap-inclusion field) is **not** a
prerequisite. The carry-forward notes in §5 below are binding on the Coder during
implementation; they touch caption wording, accessible-label exact text, and a
narrow §1.5 framing precision. None of them require Mark to weigh in before
Coder dispatch.

---

## 1. Four-axis scorecard

| Axis | Verdict | Notes |
|---|---|---|
| Protocol validity | PASS | `f_mentions / n_runs` is the empirical inclusion frequency of a term across independent free-list elicitations under the LSB collection protocol (one elicitation per run, n_runs typically = 4 per model per domain). It is exactly what the Sutrop (2001) CSI numerator measures: the fraction of informants who produced the item, with each LSB collection run treated as an informant in the salience-aggregation step. The protocol literature uses this ratio directly; see §4 below for the precedent. |
| Analytical validity | PASS | At n_runs = 4, the empirical ratio is the right primitive. A bootstrap-resample inclusion frequency (resample 4 runs with replacement, B = 2,000) would converge in expectation to the same empirical ratio and would add CI bounds that are wide-and-uninformative — the Architect's "illusory precision" critique is correct. The {0, 0.25, 0.5, 0.75, 1.0} discretization is acceptable *for n_runs = 4* and is honest about the granularity of the underlying measurement. Adding a smoothed bootstrap CI on top of n=4 would create the impression of precision that does not exist in the data; the rendered bar showing 3/4 is more informative than a rendered bar showing 0.75 ± 0.30. |
| Claims validity | PASS-WITH-NOTES | The caption "Bar shows fraction of collection runs that produced this term." is forbidden-vocabulary-safe ("produced," not "believed/thought") and is broadly accurate, but reads ambiguously about *whose* runs. The accessible-label template "item, salience csi.toFixed(2), included in f_mentions of n_runs runs" is accurate but compresses "Sutrop CSI" → "salience" in a way that could be read as a psychological-salience claim about the model. Both are fixable inside T7 with the §5 notes below; neither requires a re-plan. No "the model thinks" / "the model believes" framing anywhere in the plan. |
| Audience translation | PASS-WITH-NOTES | A working AI researcher reading the column will read "3 of 4 runs" correctly as run-frequency without effort; the "included in 3 of 4 runs" phrasing makes the empirical primitive obvious. A journalist will read the bar as "how often this term came up" — which is correct. The §1.5 corpus-lens framing is preserved at the column level (the bar is a property of the model's output distribution, not of the model's cognition). One tightening recommended in §5.3 to make "collection runs" unambiguous on first read for a reader who has not seen the methodology page. |

Register compliance: PASS — this is a Register 1 within-model output-distribution
artifact (sampling concentration of free-list items across re-elicitations). The
ratio is not a consensus measure, it is a concentration / replicability measure;
the rendering correctly stays at the run-frequency level and does not claim
between-run consensus.

Vocabulary compliance: PASS — scanned the plan's prose, captions, and accessible-
label templates. No "worldview," "believes," "thinks" (model-applied), "How
models see," "What the model understands," "Cultural bias" (standalone),
"publishable," "closer to human = better," "within-model consensus," "within-model
CCM," or "within-model eigenratio." The §2.5 empty-state captions ("(no terms
produced)," "Select one or more models to see their free lists.") correctly avoid
"missing," "no data yet," "pending," and "placeholder" per CLAUDE.md §9 pitfalls
4 and 5.

---

## 2. Rationale on the core methodological question

The architecture text at `ARCHITECTURE.md` §4.5 line 1111 reads: **"FreeListCompare
shows per-item inclusion frequency across bootstrap samples as a small bar next to
each term."** That sentence reflects a v0.6 (October 2025) drafting choice when the
expectation was a much larger n_runs per cell. The 0.2 corpus shipped at n_runs = 4
per (model, domain), and at that sample size the bootstrap path produces a
methodologically *weaker* claim than the empirical-frequency path:

1. **The CSI's empirical primitive IS `f_mentions / n_runs`.** Sutrop's (2001) CSI
   is defined as `F / (N × mP)` where F is the count of informants who produced the
   term and N is the total number of informants. Under LSB's "treat each run as an
   informant for salience aggregation" convention, F = f_mentions and N = n_runs.
   The frequency ratio is not a derived quantity that needs uncertainty bounds — it
   *is* the empirical quantity from which the salience score is derived. Showing
   the reader f_mentions/n_runs alongside the CSI score is exposing the data, not
   reconstructing it.

2. **At n_runs = 4, bootstrap-resample inclusion frequency converges to
   f_mentions / n_runs in expectation.** Resampling 4 observations with
   replacement, B = 2,000 times, and averaging the resulting inclusion rates
   yields E[f_boot] = f_mentions / n_runs. The bootstrap path adds variance
   estimation, but variance estimation on 4 observations produces CIs that are
   either (a) wider than the [0, 1] support in most cells, or (b) artifacts of the
   resampling distribution rather than the underlying measurement.

3. **The Architect's "illusory precision" argument is correct.** Rendering "0.75
   ± 0.30" next to a term is less informative to a reader than rendering "3 of 4
   runs," because the former invites the reader to interpret the ± as a statement
   about repeatability, when it is in fact a statement about the resampling
   distribution of a 4-element sample. The empirical-frequency rendering is more
   honest about what was measured.

4. **The R10 binding (§4.5 / CLAUDE.md §6 R10) is satisfied.** R10 says no point
   estimate without uncertainty. The CSI score IS a point estimate; the
   inclusion-frequency bar IS the uncertainty representation paired with it. The
   precise *form* of uncertainty (bootstrap CI vs. empirical ratio) is not
   stipulated by R10 — what is stipulated is that uncertainty be present and
   adjacent. The fallback satisfies the rule.

The architecture text at §4.5 line 1111 should be updated at T14 (documentation
sweep) to read "shows per-item inclusion frequency across collection runs as a
small bar next to each term" — see §5.1 below. This is a doc-text update, not
a methodology change, and is appropriately deferred to T14 per the plan's §7.

**Fallback-of-the-fallback (T7a) — explicitly not required.** I considered whether
the alternative path (build T7a, emit per-bootstrap-resample inclusion frequencies,
render bars-with-CIs) would be more methodologically correct. At n_runs = 4 it
is not, for the reasons in points 1–3 above. If a future LSB campaign collects at
n_runs ≥ 30, the calculus changes: a Wilson-score interval on the empirical
inclusion rate becomes informative, and at that point T7a (or a slim client-side
Wilson-interval module) becomes worth shipping. That is a Phase 7+ concern, not
a T7 prerequisite.

---

## 3. Empty-state handling — Case C verified against the corpus

The plan's §2.5 Case C (`free_lists[modelId].items === []` and
`sutrop_csi[modelId] === []`) correctly anticipates the z-ai/glm-5.1 empty-freelist
case documented in agent memory `project_phase4a1_empty_freelist_propagation.md`.
The plan notes that the published `family.json` and `holidays.json` do not
currently contain such records (the analysis pipeline did not propagate those
specific raw-record failures into the 0.2 publish set), but the defensive code
path is correct and the synthetic-fixture test is the right way to exercise it.

The Case C caption — `(no terms produced)` — is forbidden-vocabulary-safe and
honors Mark's "failures are findings" directive. It does **not** say "the model
failed to produce," "the model refused," or "the model declined." It says the
model produced no terms, which is the observation. **PASS** on Case C wording.

Two micro-precisions for the Coder, both non-blocking:

- The plan says Case C is "the **finding**." The phrasing is correct, but the
  rendered caption itself does not need to assert that — the column being empty
  with a one-line caption is sufficient. Do not embellish the caption.
- For domains with multiple empty-freelist models in the same view, do not
  collapse or summarize. Each empty column stands on its own. The plan
  honors this by treating Case C per-column.

---

## 4. Precedent — Sutrop (2001) and the run-as-informant convention

The Sutrop CSI was designed for human free-list data where the "informant" is a
single person and F is the count of distinct informants producing the term. LSB
adapts this by treating each independent collection run as an informant for the
purpose of within-model salience aggregation — this is the only place in the
analysis layer where the run-as-informant convention applies. See
`ARCHITECTURE.md` §4.2.0 (three registers) and the methods adaptation table:
within-model salience is a Register 1 (output-distribution) statistic and the
"informant" abstraction is local to the salience computation.

Rendering `f_mentions / n_runs` alongside each term in the dashboard makes this
adaptation visible to readers — it shows that LSB's CSI score for a term is
derived from "this term appeared in N of M elicitations from this model." This is
methodologically clearer than rendering only the derived CSI score, and clearer
than rendering a bootstrap CI that obscures the small n_runs underlying it.

The Coder should not narrate this on the page (no methodology-page link is
required in T7 per §5 of the plan); the bar + label is self-explanatory at the
column level. The longer-form explanation belongs on the methodology page when
T1/T2 ship it.

---

## 5. Carry-forward notes to the Coder (binding)

The Coder applies all five notes during implementation. The Reviewer enforces
them at PR review. None of them require re-routing back to the CDA SME unless
the Coder believes a note is internally inconsistent with the plan; in that
case, pause and route the question rather than self-editing.

### 5.1. Update the R10 caption wording — minor tightening for unambiguity.

The plan's §2.4 caption text is:

> "Bar shows fraction of collection runs that produced this term."

This is forbidden-vocabulary-safe but reads ambiguously about *whose* collection
runs (the model's? the project's overall corpus?). Replace with:

> **"Bar shows the fraction of this model's collection runs that produced this
> term."**

The added "this model's" disambiguates without lengthening materially. Forbidden-
vocab scan: clean ("produced," not "believed/thought"; "model's" used possessively
about the run set, not about cognition or worldview). This is the binding caption
text — render verbatim in `FreeListColumn.tsx`.

### 5.2. Tighten the accessible-label CSI gloss.

The plan's §2.3 accessible-label template is:

> ``aria-label={`${item}, salience ${csi.toFixed(2)}, included in ${f_mentions} of ${n_runs} runs`}``

The word "salience" alone could be read by a screen-reader user as a psychological-
salience claim about the model. Replace "salience" with the precise term:

> **``aria-label={`${item}, Sutrop salience score ${csi.toFixed(2)}, included in ${f_mentions} of ${n_runs} collection runs`}``**

Two edits: "salience" → "Sutrop salience score" (names the measure explicitly,
avoids the psychological-salience reading), and "runs" → "collection runs" (matches
the visible caption from §5.1 and disambiguates against any other "run" connotation).
The shared-term accessibility addition ("; in every selected model") stays as
specified in the plan.

### 5.3. Empty-state captions — confirm forbidden-vocab safety, no changes.

Re-confirmed all three §2.5 captions:

- Case A: `"Select one or more models to see their free lists."` — PASS.
- Case B: `"(no salience data for this model)"` — PASS. ("Salience data" reads as
  a data-field reference, not a psychological-salience claim; the parenthetical
  framing reinforces the data-pipeline reading.)
- Case C: `"(no terms produced)"` — PASS. Forbidden-vocab clean.

No edits required to the captions themselves. The Coder ports the strings exactly
as written in the plan §2.5.

### 5.4. Defer the §4.5 architecture-text reconciliation to T14.

`ARCHITECTURE.md` §4.5 line 1111 currently reads "FreeListCompare shows per-item
inclusion frequency across bootstrap samples as a small bar next to each term."
This is now inconsistent with T7's empirical-frequency implementation. The
reconciliation belongs in T14's documentation sweep, **not** in T7 — touching
ARCHITECTURE.md inside T7 expands scope per CLAUDE.md §8.

The Coder surfaces this in the T7 commit body as a T14 follow-up item, with the
exact replacement text:

> "FreeListCompare shows per-item inclusion frequency across collection runs as a
> small bar next to each term. At the 0.2 corpus's n_runs = 4, the empirical
> ratio `f_mentions / n_runs` is rendered directly (values in {0, 0.25, 0.5,
> 0.75, 1.0}) rather than a bootstrap-resample inclusion frequency; see
> `docs/status/2026-05-12-phase6-T7-cda-sme-verdict.md` for rationale."

This sentence is binding source text for the T14 §4.5 edit; the Coder includes
it in the T7 commit body so T14 has a stable target.

### 5.5. Do not narrate the methodology choice on the page.

The plan correctly omits any in-component prose explaining "we chose
empirical-frequency over bootstrap because n_runs = 4." That belongs on the
methodology page (Phase 6 T1/T2), not in T7's column captions or in any
tooltip. The Coder MUST NOT add a tooltip, info-icon, or expandable section to
explain the methodology choice at the column or per-pill level — this would
both expand T7 scope (the plan's §5 explicitly excludes "per-term tooltips") and
violate Mark's `feedback_ui_polish_scope.md` Phase 6 minimum-viable framing.

The single methodology-related sentence on the page is the §5.1 caption; that is
the entirety of the methodology surface for T7.

---

## 6. Forbidden vocabulary scan

Scanned the plan in full plus the proposed verbatim strings (column header,
captions, accessible-label templates) against `CLAUDE.md` §7 and
`ARCHITECTURE.md` §1.5.4 tables:

| Forbidden phrase | Present in the plan or proposed UI text? |
|---|---|
| "believes" / "thinks" / "worldview" (model-applied) | No |
| "How models see the world" | No |
| "What the model understands" | No |
| "Cultural bias" (standalone) | No |
| "Within-model consensus" / "Within-model CCM" / "Within-model eigenratio" | No |
| "publishable" / "groundbreaking" / "first-of-its-kind" | No |
| "closer to human = better" framing | No |
| "missing" / "placeholder" / "no data yet" / "pending" (in empty-state framing) | No |
| Cross-domain generalization claim | No |

PASS on vocabulary.

One soft-flag, NOT a forbidden-vocab violation: the unadorned word "salience" in
the aria-label template (per §5.2) is close enough to a psychological-salience
reading that screen-reader users could be misled. The §5.2 fix replaces it with
the precise term "Sutrop salience score," which is data-field language and not
ambiguous.

---

## 7. Approval

**PASS-WITH-NOTES.** T7 proceeds to UI/UX light-touch review and then to the Coder
on the standard gate chain. The five §5 carry-forward notes are binding; the
Reviewer enforces them at PR review (especially #5.1 caption wording, #5.2
aria-label wording, #5.4 T14 follow-up text in the commit body).

T7a (`cdb_publish` bootstrap-inclusion field) is **not** a prerequisite. The
empirical-frequency fallback is approved for the 0.2 corpus and is more honest at
n_runs = 4 than a bootstrap-resample CI would be.

No escalation to Mark required. The §5 notes touch caption wording, accessible-
label wording, and a deferred T14 doc-text fix; none of them reframe §1.5 or
introduce a load-bearing methodology decision Mark has not already endorsed
("failures are findings," "no software-side spend gates," "max info preference,"
"Phase 6 minimum-viable functional surface"). The §5.4 reconciliation of the
§4.5 architecture-text line is the only one that touches a binding-text document,
and it is appropriately deferred to T14 — its inclusion in the T7 commit body is
the audit trail.

— CDA SME agent (Opus), 2026-05-12
