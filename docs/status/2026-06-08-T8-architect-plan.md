# T8 — Model-label dedup + canonical form — Architect plan (2026-06-08)

**Task:** T8 from `docs/status/2026-06-05-fresh-model-audit-pilot-findings.md` (P1, user-visible).
**Gate path:** Architect → **UI/UX (REQUIRED — canonical-form decision + DESIGN_SYSTEM update)**
→ Coder → Reviewer → Tester. **No CDA SME** (display string, not methodology).

## 1. Bug (user-visible)
The dashboard computes a model's short label via **13 copy-pasted local helpers** across 13
components, under two names (`shortName` ×6, `shortModelName` ×7), with ~5 distinct
implementations that have DRIFTED. Concrete symptom: `claude-opus-4-5` renders as
**`claude-opus-4-5`** on MDSPlot / CentralityChart / CentralityTable / SimilarityHeatmap /
Focus2FamilySimilarity (5 sites use trivial `split('/').pop()`), but as **`opus-4-5`** on
Focus-1 views / PileStructure / FreeListCompare / ProviderTree / ContentArea /
Focus1RunDistribution / Focus1TermStability (7 sites strip provider prefixes). Same model,
different label per tab. `ProviderTree` is the most divergent (strips `deepseek-`→`ds-`, no
final `split`/fallback → can emit stray `/`).

## 2. Scope ruling
- **T8 ONLY. NOT bundled with T7** (displayProvider dedup). T7's canonical form is already
  settled (the exported `displayProvider`); T8 needs a UI/UX design decision T7 doesn't.
  Bundling muddies the UI/UX verdict attribution. **Recommendation surfaced for Mark** —
  he can override to bundle if he wants the efficiency win. Default: T8 alone.
- **Both name-families collapse to ONE canonical function.** `shortName` and `shortModelName`
  are the same concept under two names; both drifted; both in scope.
- **Excluded:** `SelectionBar.tsx:10` `shortName` is a typed FIELD (not a function) — leave
  the field name; only change its value source (ContentArea.tsx:113) to the canonical fn.

## 3. Dedup inventory — 13 sites (delete local def, import canonical)
**`shortName` family (6):** MDSPlot.tsx:43, CentralityTable.tsx:10, CentralityChart.tsx:44,
Focus2FamilySimilarity.tsx:31, SimilarityHeatmap.tsx:33 (all `split('/').pop()`);
Focus1SelfConsistencyOverview.tsx:35 (DRIFTED — strips prefixes, but named `shortName`).
**`shortModelName` family (7):** Focus2FamilyOverview.tsx:36 (`split('/').pop()`);
PileStructure.tsx:48 + FreeListCompare.tsx:49 (strip claude/google/meta-llama/mistralai/microsoft);
ContentArea.tsx:50 + Focus1RunDistribution.tsx:176 + Focus1TermStability.tsx:18 (strip
claude/gpt/gemini/meta-llama/mistralai); ProviderTree.tsx:47 (most elaborate, deepseek→ds, no fallback).

## 4. THE DESIGN DECISION for UI/UX (plan pauses here — Coder must NOT start)
**D.1 Primary — canonical short label for `claude-opus-4-5`:**
- **A** KEEP prefix → `claude-opus-4-5` (5/13 sites today; trivial split)
- **B** STRIP provider/family prefix → `opus-4-5` (7/13 sites today; majority intent)
- **C** Title-case display → `Claude Opus 4.5` (polished, bigger rewrite)
- **D** Context-dependent (UI/UX must then specify the ruleset + which sites get which)

Architect's non-binding read: **B** is closest to majority behavior; A is safest if any copy
references full ids. Value of T8 is *consistency*, not the specific choice.

**D.2 Org-prefix (`meta-llama/llama-3.1`):** I strip everything before `/` → `llama-3.1`
(12/13 converge here) vs II preserve. Likely I.
**D.3 `deepseek-`→`ds-` abbreviation (ProviderTree only):** X drop (treat as drift) / Y keep
everywhere / Z full abbreviation map. Likely X — note DeepSeek label changes on ProviderTree
screen if X chosen (surface, not a surprise).
**D.4 Accessibility (binding):** the label appears in SR-only text — CentralityChart.tsx:158
(SR summary sentence), SimilarityHeatmap.tsx:142 (per-cell aria-label),
Focus1SelfConsistencyOverview.tsx:98 (rank aria-label), MDSPlot tooltip, SelectionBar chip
aria-label. Canonical form must read correctly to a screen reader, not just look right.
**D.5 DESIGN_SYSTEM.md update REQUIRED on UI/UX PASS:** a binding clause defining the
canonical transform, whether it varies by context, per-provider examples (Anthropic/OpenAI/
Google/Meta/xAI/Mistral/DeepSeek/Microsoft/Qwen), and the rule that the transform lives in
`familyUtils.ts` and may not be re-implemented in components. UI/UX picks the doc home (§14
where familyUtils is documented, or §1.1 typography neighborhood).

## 5. Mechanism (post-UI/UX-PASS Coder spec)
New export in `apps/dashboard/src/lib/familyUtils.ts` (where `displayProvider` already lives):
proposed `export function displayModel(modelId: string): string` (name per UI/UX; signature is
string→string because all 13 sites pass `m.model_id`, not a `PublishedModel`). Each of the 13
sites: import it, delete the local def, rename calls. ContentArea.tsx:113 special-case:
`shortName: shortModelName(m.model_id)` → `shortName: displayModel(m.model_id)` (field name
stays). No CSS/DOM/type/schema changes.

## 6. Test plan (vitest)
New `displayModel.test.ts`: pinned-output table, one real model_id per provider (filled from
the UI/UX-defined form + `family.json`); edge cases (empty string; unknown no-`/`; unknown
with-`/` — the case ProviderTree was buggy on); **re-drift grep guards** (analogous to
T3/T5-guard): no `^function (shortName|shortModelName)\(` in `components/`, no
`.split('/').pop()` reinvention in `components/`. Manual 13-component smoke by Tester
(same model = same label on all surfaces — the user-visible-symptom-eliminated check).

## 7. Acceptance criteria
One canonical export; all 13 local defs deleted (grep zero); all 13 sites import+call it;
impl matches the UI/UX-defined transform (no invented edge cases — STOP+reroute if a real
model_id doesn't fit); DESIGN_SYSTEM.md updated in the SAME commit (R7-style co-update for a
frontend design decision); no SR/visual regression; build+test+lint green; ONE commit
(`refactor(dashboard): dedup model-label helpers to displayModel — T8`) referencing this plan
+ UI/UX + Reviewer + Tester verdicts.

## 8. Affected files
1 lib (`familyUtils.ts` +export) + 13 components (listed §3) + `DESIGN_SYSTEM.md` (+clause) +
NEW `displayModel.test.ts`. **Excluded:** `SelectionBar.tsx` (typed field).

## 9. Out-of-scope observations (do NOT bundle)
- `SelectionBar.ModelInfo.shortName` field name will be inconsistent with `displayModel` —
  separate trivial rename, future.
- ProviderTree's no-fallback bug auto-fixed by the dedup.
- T7 (displayProvider dedup) remains separate P2; adjacency flagged for Mark.
