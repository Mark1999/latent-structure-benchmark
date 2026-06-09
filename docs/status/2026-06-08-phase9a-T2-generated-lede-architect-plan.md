# Phase 9a T2 — wire the published `generated_lede` — Architect plan (RE-SCOPED to option A, 2026-06-09)

**Task:** Phase 9a T2 (kickoff §6.1 task 2; confirmed regression). **Mark's design ruling (2026-06-09):
option (a) STATIC approved lede.** The earlier hybrid (option b, client-side subset templates) is
DROPPED. **Gate path:** Architect → CDA SME (light) → UI/UX (light) → Coder → Reviewer → Tester.

## 1. The regression
`generated_lede` (CDA-SME-approved prose from the cdb_publish lede generator) is TYPED (types.ts:257)
but read by NO component. `ContentArea.tsx:199-220` renders its own inline-computed lede, which (a) is
a weaker version and (b) OMITS the R1-b low-output-concentration disclosure ("N of these models
produced low output concentration... their position is shown without a confidence ellipse"), an
R10-adjacent honesty point currently invisible.

## 2. The fix (option A — Mark's ruling)
ContentArea ALWAYS renders `domain.generated_lede` verbatim in the Focus-3 lede strip, replacing the
inline-computed `<p className="chart-lede">` block (lines 199-220) and its dynamic
"Across N models" / "Consensus baseline (all tested models):" computation. The model-selection slicer
drives the CHARTS, not the lede prose. The lede reads as "the finding" (full-slate consensus); the
charts are "the view." This is the simplest, most faithful option: no client-side lede logic (honors
the §4.2 "lede generator lives in cdb_publish" boundary), no new generated copy, and it avoids pairing
a full-slate Smith's S with a subset count. The R1-b disclosure is restored because it is part of the
approved `generated_lede`.

**Published lede confirmed on all 3 domains** (family/holidays/food). family + food carry the R1-b
sentence (n_low_oci=1); holidays uses the homogeneous template (n_low_oci=0, no R1-b sentence) — all
handled automatically by rendering the published field verbatim.

## 3. Gates (both LIGHT)
- **CDA SME — light confirm:** the `generated_lede` CONTENT is already CDA-SME-approved (it is the
  published lede, produced by the SME-approved lede_v1.py template set). This task only changes WHICH
  lede the dashboard shows (the approved published one instead of the worse inline one). Confirm that
  wiring the approved prose verbatim into the surface is in-bounds for the prior lede-template PASS,
  and that removing the inline dynamic lede loses no required framing. No new copy to review.
- **UI/UX — light:** the published lede is TWO sentences (vs the inline one's one). Rule: visual
  treatment of the 2-sentence lede (continuous paragraph vs typographic separation of the R1-b
  disclosure); drop the "Consensus baseline (all tested models):" label (the published lede
  self-identifies); keep `aria-live="polite"` (the lede still changes when the domain changes). No new
  tokens expected.

## 4. Scope / mechanism
EDIT `apps/dashboard/src/components/ContentArea.tsx` only (replace the lines-199-220 inline lede with
`<p className="chart-lede" aria-live="polite">{domain.generated_lede}</p>`, applying the UI/UX visual
decision). No new files, no lib, no DESIGN_SYSTEM change, no schema, no Python. The inline computation
+ the `selectedModelIds.size` branching for the lede are removed.

**Note (flag, do NOT fix in T2):** the published `generated_lede` contains "--" as a clause separator
(e.g. "this domain -- their position"). It is the approved published copy, rendered verbatim. If Mark
wants "--" changed (per the no-em-dash preference, though "--" is a double-hyphen not an em dash), that
is a cdb_publish lede-generator (lede_v1.py) change, a SEPARATE task, not T2.

## 5. Test plan (vitest)
- For each of family/holidays/food: with the domain loaded, the rendered lede strip text === the
  domain's `generated_lede` (byte/normalized match).
- **R10-adjacent regression guard:** family + food rendered DOM contains "low output concentration" AND
  "without a confidence ellipse" (guards against silently dropping the R1-b disclosure again).
- The inline "Consensus baseline (all tested models)" / "Across N models" computed strings are GONE
  (the dashboard no longer fabricates its own lede).
- No real fetch.

## 6. Acceptance criteria
ContentArea renders `domain.generated_lede` verbatim; the inline-computed lede + its selection-branching
removed; R1-b disclosure visible on family/food; lede-text-matches-published test + R10 disclosure guard
pass; build+test+lint green; ONE commit `fix(dashboard): render published generated_lede, restoring R1-b
disclosure (Phase 9a T2)` referencing the CDA SME + UI/UX verdicts. No new files/tokens/schema.
