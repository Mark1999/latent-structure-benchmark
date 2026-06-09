# Phase 9a T3 — restore SimilarityHeatmap CI-crosses-null R10 treatment — Architect plan (2026-06-09)

**Task:** Phase 9a T3 (kickoff §3.2/§6.1; confirmed regression). **Gate path:** Architect →
CDA SME (re-affirm) → UI/UX (dashed-border on the post-T6 palette) → Coder → Reviewer → Tester.

## 1. Regression
The 2026-05-25 rebuild dropped the Phase 6 T5/T6 CI-crosses-null R10 treatment. The current
`SimilarityHeatmap.tsx` takes only `{similarityMatrix, models, selectedModelIds}` (NOT
`similarity_ci`), renders every cell at full saturation, and its per-cell aria-label shows only
`sim` (no CI). **R10 violation on food: 34/56 off-diagonal cells have CIs crossing 0.5** and
render as confident. DESIGN_SYSTEM §12.8 binding text SURVIVES (doc-layer intact); this is
implementation-only. ADAPT from the pre-rebuild component in git history (`git show
<pre-5df1f32>:.../SimilarityHeatmap.tsx`), do NOT verbatim-revert (current uses displayModel +
5-stop discrete palette + filteredIndices).

## 2. The binding Phase 6 rule (restore it)
- `SIMILARITY_NULL_VALUE = 0.5` (the Mantel/no-shared-structure null; re-add to `config/analysis.ts`
  with the derivation comment). A cell's CI crosses null when `ci_lower < 0.5 < ci_upper`.
- **Crossing cells → dashed border** `stroke=var(--color-text-primary)`, `strokeWidth=1.5`,
  `strokeDasharray="3,2"`; non-crossing → solid `var(--color-border)` 0.5px. **Diagonal cells NEVER
  dashed** (self-similarity = 1.0 by construction; short-circuit on `isDiagonal`).
- **CI-aware aria-label** (verbatim binding strings from T5 CDA SME §5.2): off-diagonal-with-CI =
  "{a} versus {b}: similarity X.XX, 95 percent confidence interval X.XX to X.XX" (+ for crossing
  cells append "; confidence interval includes the no-shared-structure value of 0.50"); null-CI =
  "...similarity X.XX, confidence interval not available"; diagonal = "{a} self-similarity: 1.00 by
  construction". ("versus" is the approved non-cognitive connective.)
- **Caption:** extend the ContentArea `chart-wrap__desc` paragraph with the verbatim sentence
  "Dashed cells: 95% confidence interval includes the no-shared-structure value of 0.50." (the
  component itself must NOT also render it — no duplication).
- No literal `0.5` for null comparisons in the component (use the constant); the only `0.50` literal
  is the presentational aria-suffix text.
- **Hover tooltip DEFERRED** (the aria-label + dashed border + numeric value satisfy R10; a tooltip is
  a frontend-designer follow-up).

## 3. Fix mechanism
ContentArea passes `domain.similarity_ci ?? []` to `<SimilarityHeatmap>` (the `?? []` degrades to
"all CIs null → solid + 'not available' aria", no crash, R10 still disclosed). The component adds the
prop (required), `ciCrossesNull(ci)`, the dashed render, the aria template. **Dual-index CI filtering:**
CI is filtered with the SAME `filteredIndices` mapping as the similarity matrix (CI[rowIdx][colIdx]
where rowIdx/colIdx are the original `models`-order indices), so a filtered cell reads its correct CI.

## 4. Gates
- **CDA SME (re-affirm):** confirm `SIMILARITY_NULL_VALUE=0.5` still the right Mantel-null under the
  current mds.py; re-affirm the aria + caption binding text; confirm the tooltip-deferral + diagonal
  exclusion. No new methodology (this restores the T5 §1 + §5 binding). PASS expected.
- **UI/UX (binding visual risk):** the dashed border was approved on the OLD alpha-blend palette;
  it has NOT been verified on the post-T6 discrete 5-stop palette. **The dark `--color-text-primary`
  (#2c3e50) stroke on the dark seq-3 (#2e6da4)/seq-4 (#1a3a5c) cells is ~1.7:1, likely FAILING WCAG
  1.4.11 (3:1 non-text).** UI/UX likely specifies a white-stroke (or thicker) variant for the 2 darkest
  stops; if so, that token/spec goes in DESIGN_SYSTEM §12.8 in the same commit. Also confirm R10 pairing
  + the caption surface. UI/UX may return PASS-WITH-NOTES with the contrast fallback.

## 5. Test plan (vitest, new `similarity-heatmap-r10.test.tsx`)
(1) crossing cell → dashed + aria has the CI + the "includes...0.50" suffix; (2-3) non-crossing →
solid, CI in aria, no suffix; (4) null CI → solid + "confidence interval not available"; (5) diagonal
→ solid + "self-similarity: 1.00 by construction", no CI; (6) boundary arithmetic ([0.499,0.501] true;
[0.5,0.501]/[0.499,0.5]/[0.499,0.499] false — strict `<`); (7) selection dual-index alignment;
(8) **R10 BINDING GUARD:** every off-diagonal `<rect>` aria-label contains one of the 3 CI phrasings
(no bare point estimate); (9) forbidden-vocab guard on caption+aria; (10) food fixture ≥30 dashed
cells; family fixture 0 dashed cells (false-positive guard).

## 6. Acceptance criteria
config exports SIMILARITY_NULL_VALUE=0.5 (commented); component imports it, no stray 0.5; ContentArea
passes similarity_ci; crossing cells dashed (1.5px text-primary 3,2), others solid, diagonal never
dashed; aria templates verbatim; caption extended (no dup); food ≥30 / family 0 dashed; R10 guard +
forbidden-vocab guard pass; build+test+lint green; tokens resolve (pitfall #15); UI/UX contrast ruling
applied verbatim (incl. any §12.8/token patch); NO schema/types/DATA_DICTIONARY edit; one commit
`feat(dashboard): T3 restore SimilarityHeatmap CI-crosses-null R10 treatment` citing the binding
precedents + the food dashed-cell count + bundle delta; CDA SME + UI/UX verdicts in docs/status/.

## 7. Files
EDIT SimilarityHeatmap.tsx + ContentArea.tsx (pass CI + caption) + config/analysis.ts + new test
(+ DESIGN_SYSTEM §12.8 + tokens.css ONLY if UI/UX requires a stroke-contrast fallback). Reference
(read-only): the pre-rebuild component in git history; the Phase 6 T5/T6 verdicts; food.json/family.json.
