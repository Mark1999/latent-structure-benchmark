---
filed: 2026-05-12
reviewer: CDA SME agent (Opus)
task: Phase 6 T5 — SimilarityHeatmap (SIMILARITY_NULL_VALUE binding decision)
slack_channel: "#lsb-cda-sme"
verdict: PASS-WITH-NOTES
---

# Phase 6 T5 — CDA SME verdict on the SimilarityHeatmap plan

**VERDICT: PASS-WITH-NOTES**

`SIMILARITY_NULL_VALUE = 0.5` is **approved**. The Architect's choice is correct
and for a stronger reason than the plan articulates — the LSB cross-model
similarity is a rescaled Mantel-style Pearson correlation, and 0.5 is the
*formal* null (the expected value under "two models' co-occurrence structures
are linearly uncorrelated"), not merely a theoretical midpoint.

T5 proceeds to UI/UX light-touch review and then to the Coder. The five §5
carry-forward notes below are binding on the Coder during implementation; they
touch the §3 acceptance criterion #9 caption text and the §2.4 aria-label
template for dashed cells. None require Mark to weigh in before Coder dispatch.

---

## 1. Four-axis scorecard

| Axis | Verdict | Notes |
|---|---|---|
| Protocol validity | PASS | `0.5` is the correct null for the LSB cross-model similarity statistic. The Architect's plan §2.3 describes it loosely as "no agreement (0 = perfect anti-agreement; 1 = perfect agreement)," but the actual semantic — traceable from `packages/cdb_analyze/cdb_analyze/mds.py` line 74 (`scaled = (r + 1.0) / 2.0`) and `ARCHITECTURE.md` line 911 ("Mantel-style correlation … Range [-1, 1], displayed as [0, 1] after rescaling") — is that the LSB similarity is a Mantel-style Pearson correlation between two models' upper-triangular co-occurrence vectors on the shared item set, rescaled to [0, 1]. Pearson r = 0 (linearly uncorrelated under random pairing) maps to **exactly 0.5** after the `(r + 1)/2` rescaling. This is a formal null, not a theoretical midpoint, and it has a precise statistical meaning: the rescaled similarity value one would observe (in expectation) if two models' co-occurrence matrices were independent. |
| Analytical validity | PASS | "CI crosses null" (`ci_lower < 0.5 < ci_upper`) is the correct operationalization of `ARCHITECTURE.md` §4.5 ("Cells whose CI crosses the null value are shown with reduced saturation"). The §4.5 text says "crosses the null," not "is too wide." A "CI width > threshold" alternative would conflate two distinct properties — low precision vs. statistical indistinguishability from independence — and would not match the §4.5 binding text. Empirical check on `apps/dashboard/public/data/family.json` and `holidays.json` confirms the rule fires meaningfully in practice. On holidays.json, model index 6 sits at similarity ≈ 0.45–0.51 against every other model with CIs that straddle 0.5 (e.g., row 0 / col 6: CI = [0.446, 0.501]). On family.json, model index 9 sits at similarity ≈ 0.50–0.51 against every other model, with several CIs explicitly crossing 0.5 (e.g., row 5 / col 9: CI = [0.492, 0.523]) and others clamped at lower bound 0.5. Each shipped domain has at least one "floor" model against which the dashed-border rule fires; the rule is conservative-and-meaningful, not "never applied." |
| Claims validity | PASS-WITH-NOTES | The plan's caption text reads correctly at a journalistic level but has two tightening edits required for analytical precision. (a) "organize this domain" is §1.5.4-compliant — `ARCHITECTURE.md` §1.5.4 line 166 explicitly approves "How models organize domain vocabulary." (b) "no agreement" reads as a soft consensus framing, but the underlying statistic at 0.5 is *Mantel-correlation null*: the two models' co-occurrence structures are statistically indistinguishable from independent. "No shared structure" is the precise plain-English equivalent, and parallels the existing "identical organization" wording. (c) "Dashed cells span the no-agreement value" is grammatically awkward and should be replaced with "Dashed cells: 95% confidence interval includes the no-shared-structure value." See §5.1 below for the binding replacement text. |
| Audience translation | PASS-WITH-NOTES | With the §5.1 caption replacement and the §5.2 aria-label addition for dashed cells, both audiences are served: a journalist reading "dashed = we can't confidently say these two models are similar" gets the correct intuition; an AI engineer reading "95% CI on rescaled Mantel correlation contains 0.5" gets the correct statistical meaning. `§1.5` corpus-lens framing is intact — "organize this domain" is a property of the model's output structure, not of cognition, and the proposed wording does not introduce "agree," "perceive," "share a worldview," or similar forbidden framings. One §5.2 binding addition is required: the aria-label for dashed cells must explicitly communicate the CI-includes-null fact, since the visual dashed border is meaningless on its own for screen-reader users (R10 + WCAG pairing). |

Register compliance: PASS — this is a Register 2 (between-model categorical
structure) artifact. The pairwise Mantel-style correlation compares two models'
co-occurrence matrices on the shared item set, which is exactly the Register 2
"informants = each model, equal voice" frame. No Register 1 within-model
language is used; no RWB CCM is being applied at the wrong register; OCI is not
invoked. Clean.

Vocabulary compliance: PASS (with §5.1 caption fix applied). Scanned the plan
in full plus the proposed verbatim strings (caption, tooltip, aria-label
templates, empty-state caption) against `CLAUDE.md` §7 and `ARCHITECTURE.md`
§1.5.4 tables:

| Forbidden phrase | Present in the plan or proposed UI text? |
|---|---|
| "believes" / "thinks" / "worldview" (model-applied) | No |
| "How models see the world" | No |
| "Model X agrees with Model Y" / "share a worldview" | No |
| "Cultural bias" (standalone) | No |
| "Within-model consensus" / "Within-model CCM" / "Within-model eigenratio" | No |
| "publishable" / "groundbreaking" / "first-of-its-kind" | No |
| "closer to human = better" framing | No |
| "missing" / "placeholder" / "no data yet" / "pending" (empty-state) | No |
| "models agree" / "models think alike" / "models share a worldview" | No |
| Cross-domain generalization claim | No |

PASS on vocabulary. Soft-flag-not-violation: "no agreement" in the plan's
current caption text reads near the forbidden-vocab boundary (close to a
consensus framing for what is actually a correlation null). The §5.1 fix
replaces it with "no shared structure," which is data-relation language and
unambiguous.

---

## 2. Rationale on the core methodological question

The LSB cross-model similarity is defined in two binding locations:

- `ARCHITECTURE.md` §4.2.2 line 911: **"Cross-model similarity: Mantel-style
  correlation between two models' co-occurrence matrices on the shared item
  set. Range [-1, 1], displayed as [0, 1] after rescaling."**
- `packages/cdb_analyze/cdb_analyze/mds.py` lines 66–76: the implementation —
  Pearson correlation between upper-triangular co-occurrence vectors, NaN-cleared
  to r = 0, then rescaled as `scaled = (r + 1.0) / 2.0`.

Under this rescaling:

| Pearson r | Meaning | Rescaled value |
|---|---|---|
| +1.0 | Two models' co-occurrence vectors are perfectly correlated | 1.0 |
| 0.0 | Two models' co-occurrence vectors are linearly uncorrelated (independent under random pairing) | **0.5** |
| −1.0 | Two models' co-occurrence vectors are perfectly anti-correlated | 0.0 |

The value 0.5 is therefore not a theoretical midpoint; it is the **expected
value of the rescaled similarity under the null hypothesis that the two
models' co-occurrence structures are independent**. This is the formal Mantel
null. A bootstrap CI on the rescaled similarity is a CI on a rescaled
correlation coefficient; when that CI crosses 0.5, the data are consistent
with the null — the two models' co-occurrence structures are not statistically
distinguishable from independent at the 95% level.

The Architect's plan §2.3 articulates this correctly in effect ("0.5 = no
agreement") but loosely in wording. The §5.1 caption fix replaces "no
agreement" with "no shared structure" to make the underlying statistic
precise and to avoid the soft-consensus reading of "agreement."

**Empirical firing of the rule — verified.** On holidays.json, model index 6's
similarity values against every other model are 0.45–0.51, and the matching
CIs straddle 0.5 (e.g., [0.446, 0.501] in row 0 col 6). On family.json, model
index 9's similarity values are 0.503–0.515 against every other model, with
some CIs explicitly crossing 0.5 (e.g., row 5 col 9: [0.492, 0.523]) and
others clamped at the lower bound. Each shipped domain has at least one
"floor" model against which the dashed-border rule fires, exactly as
intended. The "rare-firing" concern raised in the dispatch prompt is not
empirically borne out — the rule fires on the cells where the statistical
finding genuinely is "we cannot distinguish these two models' co-occurrence
structures from independent."

This is also where the rule is *most informative* to the reader. A dashed
cell signals: "this pair is the one to investigate further — these two
models look statistically uncorrelated on this domain." Solid cells are the
boring case ("yes, they have correlated co-occurrence structures, more or
less strongly").

The rule should not be relaxed (to a CI-width criterion) or tightened (to a
narrower band around 0.5). It is exactly the right operationalization of the
binding §4.5 text, and the §4.5 text is binding for good methodological
reasons.

---

## 3. The "CI width" alternative — explicitly considered and rejected

The dispatch prompt asks whether "CI width exceeds threshold (e.g., width > 0.2)"
might be a better operationalization of "reduced saturation." It is not, for
three reasons:

1. **It does not match the §4.5 binding text.** `ARCHITECTURE.md` §4.5 line
   1110 says "Cells whose CI crosses the null value are shown with reduced
   saturation to signal 'not statistically distinguishable.'" "Not
   statistically distinguishable" has a precise statistical meaning — the CI
   contains the null — that "CI width > threshold" does not capture. A wide
   CI on a similarity of 0.85 is a precision problem; a CI that contains 0.5
   is a statistical-significance result.

2. **It conflates two distinct properties.** CI width measures *precision*
   (how confident are we about the estimate). CI-contains-null measures
   *significance* (is the estimate distinguishable from the null at the
   stated confidence level). These are different statistical questions; a
   visualization that conflates them obscures both.

3. **The "rare-firing" empirical concern is unfounded.** The empirical check
   above confirms the rule fires meaningfully in both shipped domains. The
   rule is conservative (a substantive scientific bar — "we cannot
   distinguish from independent"), not pathologically conservative ("never
   fires").

The Architect's choice is correct. No change to §2.3 except the constant
name `SIMILARITY_NULL_VALUE = 0.5` (already specified at
`apps/dashboard/src/config/analysis.ts`), and the §5.1/§5.2 caption-and-
aria-label edits below.

---

## 4. Reduced-saturation rendering — dashed border vs. alpha desaturation

The Architect's plan §2.3 implements §4.5's "reduced saturation" instruction
as a **dashed border** rather than as a saturation reduction in the cell fill.
Rationale (plan §2.3): a true desaturation would require a new sequential
color palette (T6, deferred). Within the existing-tokens constraint
(Phase 6 minimum-viable functional surface; `feedback_ui_polish_scope.md`),
the dashed border is the closest visual mark to "reduced saturation."

I accept this substitution for T5 with the following observations:

- The §4.5 binding text says "reduced saturation," not "dashed border." The
  Architect's choice is a token-constrained substitution, not a perfect
  match. T14 may consider whether to sharpen §4.5 to read "reduced visual
  weight" (matching the dashed-border implementation) or to keep "reduced
  saturation" and defer the saturation rendering to T6. Either is
  acceptable; this is a T14 doc-text concern, not a T5 block.

- A dashed border is a visual mark with cognitive load lower than a fill
  saturation change; it is more legible on small cells (≤ 121-cell grid) at
  mobile widths. The substitution is functionally sound.

- The §5.2 aria-label addition is **mandatory** because the dashed border is
  a purely visual signal with no semantic content for screen-reader users.
  R10 binding requires that uncertainty be present and adjacent to the
  point estimate; for dashed cells, the "CI crosses null" fact is the
  load-bearing piece of uncertainty information and must be in the
  aria-label.

---

## 5. Carry-forward notes to the Coder (binding)

The Coder applies all five notes during implementation. The Reviewer enforces
them at PR review. None require re-routing to the CDA SME unless the Coder
believes a note is internally inconsistent with the plan; in that case, pause
and route the question rather than self-editing.

### 5.1. Replace acceptance criterion #9 caption text — binding replacement.

The plan's §3 acceptance criterion #9 caption is:

> "Each cell shows how similarly two models organize this domain (1.00 =
> identical organization; 0.50 = no agreement). Dashed cells span the
> no-agreement value within their 95% confidence interval."

Replace with the following binding caption text, rendered verbatim in
`SimilarityHeatmap.tsx`:

> **"Each cell shows how similarly two models organize this domain (1.00 =
> identical organization; 0.50 = no shared structure). Dashed cells: 95%
> confidence interval includes the no-shared-structure value."**

Two edits:
- "no agreement" → "no shared structure" (matches the underlying
  Mantel-correlation null without importing a consensus framing; parallels
  "identical organization" grammatically).
- "Dashed cells span the no-agreement value within their 95% confidence
  interval" → "Dashed cells: 95% confidence interval includes the
  no-shared-structure value" (less awkward; the colon-separated form reads
  more naturally; "includes" is precise statistical English; matches the
  first sentence's "no shared structure" terminology).

Forbidden-vocab scan on the replacement: clean ("organize" is §1.5.4
approved at line 166; "structure" is data-relation language; "shared" used
in the data-structural sense, not in a cognitive-overlap sense; no
"believes," "thinks," "worldview," "agrees," "perceives," "understands").
This is the binding caption text — render verbatim.

### 5.2. Augment the §2.4 aria-label template for dashed cells.

The plan's §2.4 aria-label template is:

> ``aria-label={`${shortNameA} versus ${shortNameB}: similarity ${similarity.toFixed(2)}, 95 percent confidence interval ${ciLow.toFixed(2)} to ${ciHigh.toFixed(2)}`}``

When the cell's CI crosses null (`ci_lower < SIMILARITY_NULL_VALUE < ci_upper`),
append a clause that communicates the dashed-border meaning to screen-reader
users:

> ``aria-label={`${shortNameA} versus ${shortNameB}: similarity ${similarity.toFixed(2)}, 95 percent confidence interval ${ciLow.toFixed(2)} to ${ciHigh.toFixed(2)}; confidence interval includes the no-shared-structure value of 0.50`}``

When the rule does not fire (CI clearly above 0.5, or CI below 0.5, or null
CI), leave the existing template unchanged. For null-CI cells, the plan's
§2.7 "confidence interval not available" wording stays as written. For
diagonal cells, the plan's "self-similarity: 1.00 by construction" wording
stays as written.

The phrase "no-shared-structure value" in the aria-label matches the §5.1
caption terminology, so a screen-reader user reading the caption and then
landing on a dashed cell encounters consistent vocabulary. The
trailing "of 0.50" disambiguates which value is meant (the same number
referenced as "0.50" in the caption).

### 5.3. Tooltip text — no change required.

The plan's §2.4 hover tooltip ("similarity: 0.73, 95% CI [0.65, 0.81]") is
data-relation language only; no consensus framing. PASS as-is. No methodology
narration in the tooltip — the methodology choice belongs on the methodology
page (Phase 6 T1/T2), not in the per-cell tooltip. The single
methodology-related sentence on the page is the §5.1 caption; that is the
entirety of the methodology surface for T5.

### 5.4. Defer the §4.5 architecture-text refinement to T14.

`ARCHITECTURE.md` §4.5 line 1110 currently reads "Cells whose CI crosses the
null value are shown with reduced saturation to signal 'not statistically
distinguishable.'" The T5 implementation uses a **dashed border** rather than
saturation reduction, per the Architect's plan §2.3 (token-constrained
substitution; full saturation rendering deferred to T6). The §4.5 text
remains substantively correct (the rule is the same; only the rendering
differs), but a T14 doc-text refinement is worth flagging.

The Coder surfaces this in the T5 commit body as a T14 follow-up item, with
the suggested replacement sentence:

> "Heatmap cells carry tooltips showing `similarity ± 95% CI`. Cells whose
> CI crosses the null value (`SIMILARITY_NULL_VALUE = 0.5`, the rescaled
> Mantel-correlation null) are shown with reduced visual weight (dashed
> border in the 0.2 release; sequential-palette desaturation when the
> heatmap color tokens land in T6) to signal 'not statistically
> distinguishable from independent.'"

This sentence is binding *suggested* source text for the T14 §4.5 edit; the
T14 author may revise. The Coder includes it in the T5 commit body so T14
has a stable target.

### 5.5. Do not narrate the methodology choice on the page.

The plan correctly omits any in-component prose explaining "we chose 0.5 as
the null because LSB similarity is a rescaled Mantel correlation." That
belongs on the methodology page (Phase 6 T1/T2), not in T5's caption or in
any tooltip. The Coder MUST NOT add a tooltip, info-icon, or expandable
section to explain the null-value choice — this would expand T5 scope (the
plan's §5 explicitly excludes things like per-cell drill-downs and
methodology-page links) and would violate Mark's
`feedback_ui_polish_scope.md` Phase 6 minimum-viable framing.

The single methodology-related sentence on the page is the §5.1 caption;
that is the entirety of the methodology surface for T5.

---

## 6. Approval

**PASS-WITH-NOTES.** T5 proceeds to UI/UX light-touch review and then to the
Coder on the standard gate chain. The five §5 carry-forward notes are
binding; the Reviewer enforces them at PR review (especially #5.1 caption
wording, #5.2 aria-label augmentation, #5.4 T14 follow-up text in the commit
body).

`SIMILARITY_NULL_VALUE = 0.5` is **approved** as the constant value at
`apps/dashboard/src/config/analysis.ts`. The constant is correctly the
rescaled Mantel-correlation null; the Architect's §2.3 rationale is correct
in substance, and the §5.1 caption fix tightens the plain-English wording to
match the underlying statistic without changing the binding decision.

No escalation to Mark required. The §5 notes touch caption wording,
aria-label wording, and a deferred T14 doc-text refinement. None of them
reframe §1.5 or introduce a load-bearing methodology decision Mark has not
already endorsed ("the corpus lens," "the mismatch is the finding," "no
software-side spend gates," "Phase 6 minimum-viable functional surface").
The §5.4 §4.5 refinement is appropriately deferred to T14 — its inclusion
in the T5 commit body is the audit trail.

— CDA SME agent (Opus), 2026-05-12
