---
filed: 2026-05-17
reviewer: CDA SME agent (Opus)
task: Frontend Designer Brief v0.1 — doctrinal review
document_reviewed: docs/FRONTEND_DESIGNER_BRIEF.md (v0.1, commit 2643650)
slack_channel: "#lsb-cda-sme"
verdict: PASS-WITH-NOTES
---

# CDA SME verdict — Frontend Designer Brief v0.1

## VERDICT: PASS-WITH-NOTES

The brief is doctrinally sound. The §1.5 framing is correctly restated, the
§1.5.4 forbidden-vocabulary table is reproduced faithfully (one substantive
omission — see §5.1), the §4.5 R10 binding is correctly enumerated for the
four shipped Phase 6 visualizations, the model_id / model_version_returned
distinction is correctly stated, the `framing_note` source-of-truth chain is
correctly preserved, the append-only invariant on `data/raw/*.jsonl` is
correctly stated, and the routing rules in §8 cover the methodology-adjacent
surfaces the future designer will most often touch. Mark's exclusive
authorship of the methodology page prose is correctly preserved in §9 item
#1 ("every word of body copy is Mark's"). The DriftTracker deferral in §9
item #2 is correctly methodological (R10 single-observation incoherence),
not UI-driven — a designer cannot misread this as "stub it" or "show a no
data yet surface."

Six binding notes follow under §5, plus three advisory annotations. None of
the six binding notes reflects a methodology error in the brief; they
narrow ambiguities a future AI designer will compound across many design
sessions if left unaddressed. The brief stays clean of forbidden vocabulary
outside the documented exceptions (the §3.1 table itself; the §2 negation
sentence; the explicit "generic terms forbidden" enumeration at §3.1 line
59). The forbidden-vocab grep returns six hits, all of which fall into the
exempted categories.

The brief is approved for handoff with the §5 notes applied.

---

## Four-axis scorecard

| Axis | Verdict | One-sentence rationale |
|---|---|---|
| 1. Protocol validity | PASS | The brief does not modify CDA elicitation protocol surfaces; §9 correctly fences `cdb_collect/prompts/v{N}/` (item 5), `data/raw/*.jsonl` (item 6), and `cdb_core/schemas.py` (item 3) from the designer's authority. |
| 2. Analytical validity | PASS-WITH-NOTES | R10 is correctly stated for the four shipped visualizations; §7.2 bundles "OCI per model" inside `cluster_consensus_metrics` in a way that could read OCI as a consensus statistic — see §5.4. |
| 3. Claims validity | PASS-WITH-NOTES | Corpus-lens framing is correct; §3.1 reproduces six of twelve canonical forbidden-vocab rows under the label "Highlights" — see §5.1 for the binding completeness annotation for designer tooltip work. |
| 4. Audience translation | PASS-WITH-NOTES | The §8 routing rules cover the major methodology-adjacent surfaces but omit explicit naming of screen-reader summary templates and statistics-bearing aria-labels — see §5.3. |

Register compliance: **PASS** — the brief does not author new Register
1/2/3 analytical text; it documents existing publish-layer artifacts and
routes any future methodology-adjacent copy through the CDA SME gate.

Vocabulary compliance: **PASS** — full document scan in §6 below.
All hits fall inside documented exceptions.

---

## 1. §2 corpus-lens framing review

The §2 one-paragraph pitch (brief lines 34–36) is a fair compression of
canonical §1.5.1, with one minor compression artifact (advisory, not
binding):

Canonical §1.5.1 (ARCHITECTURE.md line 100):

> "The **latent categorical structure** of a training corpus, as refracted
> through a model's training and alignment **pipeline**, surfaced by
> applying Cultural Domain Analysis elicitation protocols to the model
> as if it were an informant."

Brief §2 (line 34):

> "It surfaces the **corpus lens** — the categorical structure of a
> model's training corpus, refracted through training and alignment."

The brief drops "latent" and compresses "training and alignment pipeline"
to "training and alignment". This is acceptable as a one-paragraph
designer-orientation pitch — the canonical long form lives in
ARCHITECTURE.md §1.5.1 which is in the brief's reading list and the
brief's §2 explicitly defers methodology-precise language to that doc.
The compression is not a methodology error; it is a stylistic choice
for an audience that will read the long form on first encounter with
§1.5.1.

**The negation paragraph is correct.** Brief §2 line 34: "LSB does not
measure cultural worldview, belief, or cognition." This is the
canonical CLAUDE.md §1 construction ("LSB does *not* measure cultural
worldview, belief, or cognition"). The forbidden terms appear in a
negation context, which is the documented exception (CLAUDE.md §7,
paragraph beginning "The forbidden vocabulary applies to text *about*
the models that LSB measures..."). This is consistent with how §1.5.4
itself uses these terms in order to forbid them.

**"LSB is a website that uses research methods, not a research project
that has a website"** (line 38) is verbatim from CLAUDE.md §1 and is
the right framing for the designer's posture. Concur.

## 2. §3.1 forbidden-vocabulary table review

The six rows reproduced in brief §3.1 (lines 50–57) are byte-identical
to the canonical first six rows in ARCHITECTURE.md §1.5.4 lines 164–169
and CLAUDE.md §7. **Concur on those six rows.**

The brief labels the table "Highlights" (line 48: "The full table lives
in `CLAUDE.md` §7 and `ARCHITECTURE.md` §1.5.4. Highlights:"). This is
honest but creates a load-bearing omission for the designer's
day-to-day work: **six of the twelve canonical rows are not shown**:

- "Within-model consensus" → "Representational coherence" / OCI
- "Within-model cultural consensus" → "Output distribution analysis"
- "Within-model eigenratio" → OCI
- "Within-model CCM" → "Output distribution analysis"
- "LSB hypothesizes that..." / "LSB tested whether..." / etc. → "LSB measures..." / "LSB reports..."
- "LSB predicted X and the data confirmed/refuted it" → "LSB ran the protocol; here is what came out"

A designer writing tooltip copy for the OCI badge, the heatmap legend, or
the Smith's S explanation will need the Register-1/Register-2 rows
specifically — those are the rows that govern how to talk about OCI,
within-model concentration, and the difference between concentration
(Register 1) and consensus (Register 2). A designer writing copy that
describes what the dashboard "shows" or "found" needs the hypothesis-
testing rows. See §5.1 below for the binding annotation.

**"Generic terms forbidden in any model-facing context"** (line 59):
matches CLAUDE.md §7 verbatim. The "thinks" generic is correctly
included (in the bare form), which is broader than the table's
"thinks of family" specific phrasing. Concur.

**"Corpus lens" plain-language anchor** (line 61): "The plain-language
term for what LSB measures is **corpus lens**. The phrase is doing real
work — it signals that this is a property of the *training corpus as
filtered through the model*, not a property of the model's cognition.
Use it." This is consistent with ARCHITECTURE.md §1.5.1 line 102 ("the
plain-language term for this... is the **corpus lens**"). Concur.

**Scope clarification** (line 61, second sentence): "The plain-language
term for what LSB measures is **corpus lens**." This is the right
single canonical anchor. The brief does NOT introduce competing plain-
language alternatives — "categorical structure", "categorical
divergence", and "model's outputs pattern as" all appear only as
"say-instead" entries in the table, not as alternative plain-language
anchors. Concur.

## 3. §3.2 R10 binding review

The four enumerated visualizations (brief lines 67–70) accurately describe
shipped Phase 6 behavior:

- MDS coordinates ship with bootstrap ellipses (semi-major, semi-minor,
  rotation) — matches `MDSPlot.tsx` per ARCHITECTURE.md §4.5 line 1123.
- Heatmap cells ship with 95% CI low/high values; cells whose CI crosses
  the null get reduced saturation — matches `SimilarityHeatmap.tsx` per
  ARCHITECTURE.md §4.5 line 1124 and the T5 verdict
  `SIMILARITY_NULL_VALUE=0.5` rescaled-Mantel-null contract.
- Free-list inclusion frequencies ship with per-term bootstrap bars —
  matches `FreeListCompare.tsx` per ARCHITECTURE.md §4.5 line 1125.
- Smith's S ledes ship with CI in parentheses — matches `KeyFinding.tsx`
  per the T7 R10 verdict (`f_mentions/n_runs` empirical-frequency
  fallback at n_runs=4).

The binding language "If you redesign a chart, the CI representation must
move with it" (line 72) and "There is no exception for 'just a sparkline'"
both correctly transmit the §4.5 R10 binding into the designer's frame.
**Concur.**

**One stylistic phrasing flagged for awareness** (advisory, not
binding): brief §3.2 line 65 "Every numeric value on the dashboard is a
sample estimate." Technically Smith's S, OCI, etc. are statistics
computed on observed runs — they are population estimands in some
framings, sample-statistics in others, and the inferential machinery
LSB uses (bootstrap CIs) treats them as sample statistics with
uncertainty. "Every numeric value on the dashboard carries sample
uncertainty" or "is computed from a finite number of runs and carries
quantifiable uncertainty" would be slightly more precise. Not binding —
the load-bearing claim ("show CIs adjacent") is correct.

## 4. §7 data shape semantics review

All four binding semantics are correctly stated:

1. **`model_id` vs `model_version_returned`** (line 233): "Longitudinal
   joins must use `model_version_returned`." Correct per CLAUDE.md §9
   pitfall #1 and ARCHITECTURE.md §3.2 InformantRecord line 689 and
   §4.5 line 1134. **Concur.**

2. **`groundings` list semantic** (line 234): "always a list (may be
   empty). Never assume singleton." Correct per CLAUDE.md §9 pitfall #3
   (annotated as historical post-2026-05-07 amendment but the list
   semantic is retained for forward compatibility) and ARCHITECTURE.md
   §1.5.5 line 187 ("The schema's `groundings: list[GroundingRef]`
   field is retained for forward compatibility but defaults to empty
   for all v1 domains"). **Concur.**

3. **`framing_note` source-of-truth chain** (line 227): "CDA-SME-reviewed
   verbatim text explaining 'failures are findings' — render adjacent to
   the records." Correct per T9 verdict §5.1 (byte-identity governed by
   the verdict file) → DATA_DICTIONARY.md §12 line 1086 → JSON output →
   T10 UI rendering contract. The brief correctly preserves all four
   links in the chain by naming the source-of-truth as
   "CDA-SME-reviewed" (the verdict file is the methodology authority)
   and naming the rendering contract ("render adjacent to the records"
   = T10). **Concur.**

4. **Append-only invariant on `data/raw/*.jsonl`** (line 235): "append-
   only. Do not edit. Do not 'fix' records. The publish layer is the
   redaction boundary." Correct per CLAUDE.md §9 pitfall #10 + the
   memory `project_metadata_fix_forward_precedent.md` (2026-05-07
   "fix forward, no backfill" ruling). **Concur.**

The `failures/{domain}.json` description at line 226 ("Refusal records +
follow-up decline interviews, sanitized for publication") and the
sanitization callout at line 228 ("API keys / Slack webhooks / local
filesystem paths are pre-redacted by `cdb_publish.sanitize.
sanitize_for_publication()`") are correct per ARCHITECTURE.md §4.4.6
line 1095 (publish-layer redaction boundary). **Concur.**

## 5. §8 + §9 routing rules review

The §8.1 list of methodology-adjacent surfaces that gate through CDA SME
(brief lines 245–250) covers the major categories:

- Lede patterns / lede templates
- Methodology summary copy
- Failures-as-findings framing text
- Empty-state copy that hints at "why is this empty"
- Tooltip text that explains a statistic (Smith's S, OCI, CSI, bootstrap)
- Glossary entries

**Two methodology-adjacent surfaces are not explicitly named** in §8.1
but should be. See §5.3 below for the binding annotation:

- **Screen-reader summary templates** (`copy/screen_reader_summaries.ts`)
  — these passed through CDA SME review at T8 with binding caveats on
  consensus-type plain-English mapping and forbidden-vocab discipline
  (per T8 verdict). A future designer who modifies these templates is
  modifying methodology-adjacent prose.
- **ARIA-labels and chart captions that describe statistics** —
  similarly methodology-adjacent. The T5 (similarity heatmap) and T7
  (free-list) verdicts established binding aria-label phrasings; any
  redesign that rewrites these labels touches methodology.

**§9 item 1 (methodology page prose):** "Mark writes the methodology
page himself. You may build the page shell and the routing, but every
word of body copy is Mark's. `methodologyPageUrl` is currently `null` in
`App.tsx` — leave it that way until Mark says otherwise." This is the
correct preservation of Mark's exclusive authorship. **Concur.**

**§9 item 2 (DriftTracker deferral):** "The corpus has at most one
collection date per model — a temporal visualization can't satisfy R10
yet. Don't stub it; don't show '(no data yet).' It's deferred to the
next collection campaign." This is the correct methodological framing
of the deferral, matching the T14 verdict §6 AC11 non-action discipline
analysis. The reasoning is R10 + single-observation incoherence, NOT
"the UI isn't ready". A future designer cannot misread this as a UI gap
to fill. **Concur.**

**§9 item 3 (schema):** "`packages/cdb_core/schemas.py` — Architect
sign-off required." Correct routing — schema changes go to Architect,
not directly to CDA SME, per CLAUDE.md §6 rule 6 and the agent pipeline
in CLAUDE.md §3. **Concur.**

## 6. Forbidden-vocabulary scan results

Full document scan run with two grep patterns:

```
grep -iE 'worldview|believes|thinks of|cultural bias|what the model
understands|how models see|model.*believes|model.*thinks of'

grep -iE '\bthinks\b|\bbelieves\b|\bworldview\b'
```

Hits at lines 34, 52, 53, 54, 55, 56, 57, 59. All eight hits fall into
documented exceptions:

- **Line 34** (§2 pitch): "LSB does not measure cultural worldview,
  belief, or cognition." — negation construction, documented exception
  per CLAUDE.md §7 paragraph beginning "The forbidden vocabulary
  applies to text *about* the models...". Naming the forbidden terms
  in order to forbid them is the standard exception.
- **Lines 52–57** (§3.1 forbidden-vocab table): the table itself
  enumerates the terms in order to forbid them — documented exception.
- **Line 59** (§3.1 generic-terms enumeration): "Generic terms
  forbidden in any model-facing context: `worldview`, `believes`,
  `thinks` (when applied to models)." — same documented exception.

**No undocumented forbidden-vocab usages were found.** The brief is
clean.

## 7. §10 open question #7 (failures-as-findings elevation) review

Brief §10 question 7 (line 302): "It's currently a passable list at the
bottom of the article. Mark's binding directive ('failures are findings')
wants this to be a *first-class* surface, not a footer. How do you elevate
it without making refusals feel like the headline?"

**This framing is consistent with the 2026-04-23 'failures are findings'
binding directive** (memory `project_failures_are_findings.md`) and with
the T9/T10 publish-layer/UI verdicts. The phrasing "without making
refusals feel like the headline" is the critical guard — it
preemptively rules out reframings that would (a) attribute intent to
refusing models, (b) re-frame the failures section as a defect-or-
controversy surface, or (c) present refusals as the dashboard's
*primary* finding.

The risk vector here is that a future AI designer reading the question
as "elevate failures" without internalizing the parenthetical might
produce a design where the failures section dominates the article
visually — large hero treatment, dedicated landing page, etc. — in a
way that frames refusals as the headline-grabbing finding. **This is
not what 'failures are findings' means.** The directive elevates
failures to co-equal first-class status with successful elicitations,
not to headline-dominant status. See §5.5 for the binding annotation.

The T9 verdict §2.1 already cautions against this: "a model saying 'I
cannot help with that' in `response_verbatim` is data that a reporter
could quote in a way that attributes a *state-of-mind* (refusal) to
the model, which §1.5.4 forbids." The T10 verdict similarly placed
binding constraints on the badge label ("Decline follow-up" not
"Refusal", "Follow-up interview" framing) and on the surrounding
copy. Both of those constraints would be at risk in a "make this the
headline" redesign.

## 8. §1 / §9 / §14 — what stays Mark's

Confirmed:

1. **Methodology page prose is Mark-authored.** Brief §1 line 25
   ("Methodology page prose (Mark writes it personally — see §10)")
   and §9 item 1 ("every word of body copy is Mark's"). Two
   consistent statements; the designer cannot misread the boundary.
   **Concur.**

2. **DriftTracker deferral is methodological, not UI.** Brief §9 item
   2 ("temporal visualization can't satisfy R10 yet"). The
   methodological reason is named directly; the designer cannot
   reframe this as a UI gap. **Concur.**

3. **Schema changes route through Architect, not CDA SME.** Brief §8.2
   ("Schema changes → Architect") and §9 item 3 ("Architect sign-off
   required"). Two consistent statements; the routing is unambiguous.
   The brief correctly notes (line 254) that the Architect-gated path
   is the one that triggers the DATA_DICTIONARY.md co-update
   requirement. **Concur.**

---

## 5. Binding carry-forward notes (apply to brief v0.2)

These six notes are binding for Mark to apply before handing the brief
to the future AI frontend designer. None alters the brief's overall
structure; each is a methodology-adjacent narrowing of an existing
section.

### 5.1. §3.1 must enumerate the four Register-1/Register-2 rows and the two hypothesis-testing rows from the canonical table. [Claims validity]

**Why:** the brief labels the §3.1 table "Highlights" and shows six of
the twelve canonical rows. The six omitted rows are the ones a designer
will need most often when writing tooltip copy for OCI, the heatmap
legend, the Smith's S explanation, and any dashboard text that
describes what the project "shows" or "tested". A designer working
without those six rows in front of them risks producing copy like
"within-model consensus" in an OCI tooltip — which is the exact
phrasing the post-F1 SME review added to §1.5.4 because it was the
most likely failure mode.

**How to apply:** either (a) replace "Highlights" with the full
twelve-row canonical table from ARCHITECTURE.md §1.5.4 / CLAUDE.md §7,
or (b) keep "Highlights" framing but explicitly list the four
Register-1/Register-2 rows and the two hypothesis-testing rows in
addition to the six already shown. Option (a) is preferred for a
designer who will not consistently follow cross-references; option
(b) is acceptable if length is a concern.

**Binding language for option (b) — minimum required additions:**

```
| "Within-model consensus" | "Representational coherence" / "Output Concentration Index (OCI)" |
| "Within-model cultural consensus" | "Output distribution analysis" |
| "Within-model eigenratio" | "Output Concentration Index (OCI)" |
| "Within-model CCM" | "Output distribution analysis" |
| "LSB hypothesizes that..." / "LSB tested whether..." / "LSB confirms that..." / "LSB found that [hypothesis]" | "LSB measures..." / "LSB reports..." / "LSB observes..." |
| "LSB predicted X and the data confirmed/refuted it" | "LSB ran the protocol; here is what came out" |
```

### 5.2. §3.1 must state the Register-1 vs Register-2 distinction in one sentence so the designer knows when each label applies. [Claims validity]

**Why:** the four Register-1/Register-2 rows (added per §5.1 above) are
not interpretable to a designer without a one-sentence explanation of
the distinction. The canonical statement in §1.5.4 line 177 is
"Running the eigenratio machinery on N runs of a single model at
fixed prompt does not produce a cultural consensus statistic"; a
designer cannot extract operational guidance from that without prior
exposure to the register framework.

**How to apply:** add a one- or two-sentence note immediately following
the §3.1 table that says (paraphrase, not verbatim):

> "Register matters: OCI describes one model's output concentration
> (Register 1); Romney CCM / consensus type describes structure
> shared across multiple models (Register 2). Do not write 'within-
> model consensus' — that crosses the register boundary."

This gives the designer a stand-alone operational rule without
requiring them to read §4.2 of ARCHITECTURE.md before writing tooltip
copy.

### 5.3. §8.1 must explicitly enumerate screen-reader summary templates and statistics-bearing aria-labels as CDA-SME-gated surfaces. [Audience translation]

**Why:** brief §8.1 lists six methodology-adjacent surfaces but omits
two that have already passed through CDA SME review with binding
verdicts:

- Screen-reader summary templates (`copy/screen_reader_summaries.ts`,
  reviewed at T8 with binding consensus-type plain-English mapping)
- ARIA-labels and chart captions that describe statistics (reviewed at
  T5 / T7 / T8 / T13 with binding phrasings)

A designer redesigning the heatmap (per §10 question 6) or the screen-
reader surface for accessibility polish will touch these without
realizing they have been CDA-SME-reviewed.

**How to apply:** add two bullet items to §8.1 (lines 246–250):

- Screen-reader summary templates (`copy/screen_reader_summaries.ts`)
- ARIA-labels and chart captions that describe a statistic (e.g.,
  "no shared structure" on similarity-heatmap dashed cells)

The existing bullet "Tooltip text that explains a statistic (Smith's S,
OCI, CSI, bootstrap)" partially covers this but is not unambiguous on
the screen-reader / aria-label surfaces.

### 5.4. §7.2 must separate OCI (Register 1) from cluster_consensus_metrics (Register 2) bundling. [Analytical validity]

**Why:** brief §7.2 line 218 reads "cluster_consensus_metrics: Smith's
S, OCI per model, romney_small_n_warning, consensus_type enum". This
bundles a Register-1 statistic (OCI, per-model output concentration)
inside a Register-2 group label ("cluster_consensus_metrics"). A
designer reading this will reasonably conclude OCI is a "consensus
metric", which is exactly the §1.5.4 hazard the new rows added in §5.1
above guard against.

**How to apply:** restructure the bullet to split OCI out, or rename
the group label. Paraphrase suggestion:

> "- Per-model salience and concentration statistics: Smith's S
>    (per-item salience), OCI (per-model output concentration —
>    Register 1)
>  - Cross-model consensus metrics: `romney_small_n_warning`,
>    `consensus_type` enum (Register 2)"

The actual JSON field structure on disk may indeed bundle these under
`cluster_consensus_metrics`; the brief is documenting the JSON, not
prescribing the schema. The fix is to annotate the register of each
statistic in the brief's prose so the designer knows OCI is not a
consensus statistic, regardless of where it sits in the JSON.

### 5.5. §10 question 7 must add an explicit "first-class, not headline-dominant" anchor sentence. [Claims validity]

**Why:** the question as currently written (line 302) trusts the
designer to internalize the parenthetical "without making refusals
feel like the headline." A future AI designer who reads this question
during a long context-loaded session may execute on "elevate failures"
without carrying the parenthetical into the design phase. The
2026-04-23 directive ("failures are findings") establishes co-equal
first-class status, not headline-dominant status, and the T9/T10
verdicts have already placed binding constraints on what kinds of
elevation are §1.5-compatible.

**How to apply:** add one sentence to question 7 (paraphrase):

> "The directive is first-class status (co-equal with successful
> elicitations), not headline-dominant treatment. A design that
> visually centers refusals as *the* finding crosses into §1.5.4
> territory by inviting readers to attribute intent. The T9/T10
> verdicts (in `docs/status/`) document the binding constraints on
> failures-section copy and badge labels."

This is binding because a methodology-incompatible failures redesign
is one of the highest-impact surface-area errors the brief could
license, and the parenthetical hedge alone is not strong enough to
hold across long context windows.

### 5.6. §3.2 line 65 "sample estimate" phrasing should be tightened to "carries quantifiable uncertainty". [Analytical validity — advisory, non-binding]

**Why:** "Every numeric value on the dashboard is a sample estimate" is
not technically wrong but is loose framing. Smith's S, OCI, Mantel
correlation, etc. are statistics computed on a finite sample of
collection runs and carry quantifiable uncertainty; calling them all
"sample estimates" elides the per-statistic inferential framework.
This is advisory because the load-bearing claim (show CIs adjacent)
is correct.

**How to apply (optional):** replace "Every numeric value on the
dashboard is a sample estimate" with "Every numeric value on the
dashboard is computed from a finite number of runs and carries
quantifiable uncertainty."

---

## 6. Notes for downstream review

**Mark:** this is a doctrinal review only. The six binding notes above
narrow methodology-adjacent ambiguities; none reflects a methodology
error in the brief. The brief is approved for handoff to the future
designer once §5.1 (forbidden-vocab table completeness), §5.2
(Register distinction), §5.3 (SR template / aria-label routing), §5.4
(OCI register annotation), and §5.5 (failures elevation guard) are
applied. §5.6 is advisory.

**Future AI frontend designer:** when this brief lands in your context,
treat the §3.1 forbidden-vocabulary table as canonical for your
day-to-day copy work but cross-reference ARCHITECTURE.md §1.5.4 or
CLAUDE.md §7 before authoring tooltip text on any analytical
statistic (Smith's S, OCI, CSI, Romney CCM, Procrustes, Mantel). The
Register-1/Register-2 distinction is the most common failure mode and
is what the post-F1 rows in the canonical table guard against.

**Architect / Reviewer:** no action required from this verdict.
Schema is not touched. DATA_DICTIONARY.md is not touched. No new
methodology surface is created.

---

## 7. Summary of binding outputs

- **Verdict:** PASS-WITH-NOTES
- **Mark must apply (binding, before handoff to future designer):**
  §5.1 (forbidden-vocab table completeness — add four Register rows + two hypothesis rows),
  §5.2 (Register-1 vs Register-2 one-sentence operational rule),
  §5.3 (§8.1 routing — add SR templates + aria-labels),
  §5.4 (§7.2 — separate OCI from cluster_consensus_metrics, annotate registers),
  §5.5 (§10 question 7 — add "first-class, not headline-dominant" anchor).
- **Mark may apply (advisory):** §5.6 (§3.2 "sample estimate" phrasing tightening).
- **Architect must update:** None. No re-plan required.
- **`cdb_core/schemas.py` change required:** No.
- **DATA_DICTIONARY.md change required:** No.
- **Methodology page carry-forwards:** None new — the existing T1/T2
  methodology page concerns surfaced in prior verdicts still stand.
- **Mark escalation:** None beyond the §5 notes above.

The brief proceeds to handoff once the five §5 binding notes are
applied. The future designer's first session can begin from brief
v0.2.

---

*End of Frontend Designer Brief v0.1 CDA SME verdict.*
