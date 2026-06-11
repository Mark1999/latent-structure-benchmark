# UI/UX Verdict: FOOD-V02-FIX-SIMIDS (2026-06-11)

**Task:** FOOD-V02-FIX-SIMIDS: explicit similarity_model_ids matrix contract
**DESIGN_SYSTEM.md version reviewed:** v0.23.0 (no amendment required)
**Verdict:** PASS

---

## Scope

This task adds `similarity_model_ids?: string[]` to `DomainResultPublished`
(types.ts) and `SimilarityHeatmapProps` (SimilarityHeatmap.tsx), then uses
the new field to derive matrix row/column indices instead of inferring them
from the `models` array position. `ContentArea.tsx` passes the new prop through.

The change is a data-contract fix. There are no new visual patterns, no new
CSS classes, no new tokens, no new colors, and no new spacing or interaction
decisions.

---

## Four-question review

**Q1 -- OWID design fidelity (does the change introduce any visual pattern that
contradicts the OWID-inspired system?)**

No visual pattern change. The heatmap cell fill, stroke, CI-bar, axis labels,
and color scale are all unchanged. The only behavioral difference is that
`filteredIndices` are now derived from `similarityModelIds` (when present)
rather than from `models` array position. For family and holidays (no basis
exclusion, `similarityModelIds` absent or empty), the rendered output is
byte-identical to the prior commit. For food v0.2 (maverick basis-excluded,
`similarityModelIds` present), the heatmap now renders the correct 12x12
slice, which was previously misindexed. Correct rendering is not a visual
decision. PASS.

**Q2 -- 30-second journalist test (can a journalist reading the heatmap
understand what they are looking at?)**

Unchanged. The §23.3 exclusion caption (`.heatmap-exclusion-caption`) already
explains maverick basis-exclusion in human-readable language. This task
corrects the index mapping that feeds the underlying data; it does not alter
the caption or any other visible string. PASS.

**Q3 -- Researcher reproduce-and-cite test (can a researcher reconstruct the
displayed values from the open-data bundle?)**

Improved. Before this fix, a researcher attempting to reconstruct the food
heatmap from `similarity_matrix` + `models` would obtain the wrong index
mapping for the maverick-excluded domain. The new `similarity_model_ids`
field in the open-data JSON provides the authoritative row/column order,
making the displayed values fully reproducible. PASS.

**Q4 -- WCAG AA accessibility (does the change introduce any new interactive
or non-decorative element without sufficient contrast?)**

No new elements introduced. The legacy fallback path (empty
`similarityModelIds`) is structurally identical to the prior implementation.
The new path produces the same DOM output as the old path for the same input
data. No new tokens required; no pitfall-15 risk (grep against tokens.css
confirms no new `var(--...)` references). PASS.

---

## Pixel-identity invariant (N1)

For domains where `similarity_model_ids` is absent or empty (family,
holidays, all pre-FOOD-V02-FIX-SIMIDS results), the new code path follows
the legacy fallback branch and produces output identical to the prior
implementation.

For food v0.2, where `similarity_model_ids` is a 12-element array (maverick
excluded), the new code path is authoritative. The prior code path was
incorrect: it indexed into a 12x12 matrix using positions from a 13-element
`models` list. The new render is the correct one per the schema contract.

---

## DESIGN_SYSTEM.md

No amendment required. All changes fall within the existing §23.3 heatmap
exclusion pattern and §18.5 model display name rules. No new visual patterns,
tokens, or interaction patterns introduced. DESIGN_SYSTEM.md remains at
v0.23.0.

---

## Notes

None. All four review questions pass without qualification.
