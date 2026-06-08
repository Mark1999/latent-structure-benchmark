# T7 — `displayProvider` dedup — Architect plan (2026-06-08)

**Task:** T7 from `docs/status/2026-06-05-fresh-model-audit-pilot-findings.md` (P2 dedup, NOT user-visible).
**Gate path:** Architect → Coder → Reviewer → Tester. **No CDA SME, no UI/UX.** Sibling of T8.

## 1. No-drift finding (confirmed — orchestrator swept, Architect spot-checked)
All 7 component-local copies are SEMANTICALLY IDENTICAL to the canonical
`apps/dashboard/src/lib/familyUtils.ts:59` `export function displayProvider(model: PublishedModel)`:
```ts
if (model.provider === 'openrouter') {
  const map = { gpt:'openai', llama:'meta', mistral:'mistral', deepseek:'deepseek', phi:'microsoft' };
  return map[model.family] || model.provider;
}
return model.provider;
```
- **5 byte-identical:** App.tsx:22, FreeListCompare.tsx:36, ProviderTree.tsx:26, PileStructure.tsx:35, ContentArea.tsx:37.
- **MDSPlot.tsx:36** — identical logic; param typed `{provider, family}` (structural subset); map inlined.
- **CentralityChart.tsx:38** `resolveProvider(model: ModelRef)` — identical logic; map hoisted to module
  const `FAMILY_TO_PROVIDER` (lines 24–30) which is byte-identical to canonical's inline map.
  `FAMILY_TO_PROVIDER` is referenced ONLY by `resolveProvider` → orphaned after dedup, must be deleted.
**Conclusion:** NO drift, NO behavioral/visual difference, NO design decision. Pure dedup like T5.

## 2. Gate ruling — NO UI/UX, NO CDA SME
Every call site produces the same string before/after → same color-table key → same pixels. No
rendered surface (`displayProvider` is a behind-the-scenes lookup key, not displayed text — contrast
T8 where the output IS read). No design-system clause needed (§14 already names familyUtils as the
home). No methodology surface. Param-widening (§3) is a TS refinement that only weakens requirements.
Path: Architect → Coder → Reviewer → Tester.

## 3. Canonical signature — widen to `{ provider: string; family: string }`
Widen the param to the structural subset the function actually reads. `PublishedModel`
(types.ts:36–39 has `provider`+`family`), MDSPlot's `{provider, family}`, and CentralityChart's
`ModelRef` (`{model_id, provider, family}`) all satisfy it with NO call-site change, NO cast, NO
fabricated payload. Body unchanged. (Rejected: keep `PublishedModel` + adapt call sites — needless casts.)

## 4. Dedup inventory + mechanism
Widen canonical (1 line). Then for each of the 7: delete local def, add
`import { displayProvider } from '<rel>/lib/familyUtils'`, leave call sites unchanged EXCEPT
CentralityChart (`resolveProvider(...)` → `displayProvider(...)` + delete `FAMILY_TO_PROVIDER` const).
Sites: App.tsx:22, MDSPlot:36, FreeListCompare:36, ProviderTree:26, PileStructure:35, ContentArea:37,
CentralityChart:38 (+const 24–30).

**OUT of scope (explicit):** `PROVIDER_COLORS`/`PROVIDER_DISPLAY_COLORS` constant dedup + hex→token =
**T10**, do NOT touch. `PROVIDER_ORDER` arrays = separate. `ModelRef` interface (CentralityChart:32) =
leave (still types the models prop; removing = scope creep). No DESIGN_SYSTEM edit.

## 5. Test plan (extend the existing T8 file `apps/dashboard/src/lib/__tests__/displayModel.test.ts`)
**A. Pinned-output block** for `displayProvider`: openrouter gpt→openai, llama→meta, mistral→mistral,
deepseek→deepseek, phi→microsoft, qwen→openrouter (unmapped fall-through); non-openrouter pass-through
(anthropic/claude→anthropic, google/gemini→google, xai/grok→xai). Add `displayProvider` to the existing
familyUtils import.
**B. Re-drift guard:** add one `it` reusing the already-loaded `allComponentSources` glob, banning
`^function\s+(displayProvider|resolveProvider)\s*\(` across components/**. (Mirrors the T8 guard.)

## 6. Acceptance criteria
Canonical param widened; all 7 locals deleted (grep `^function (displayProvider|resolveProvider)\(`
in components/ + App.tsx = zero); all 7 import+call canonical; `resolveProvider` calls renamed;
`FAMILY_TO_PROVIDER` deleted (grep zero); test file extended (pinned block + guard), all T8 tests still
pass; build+test+lint green; NO `packages/`/DESIGN_SYSTEM/schemas/dict edits; one commit
`refactor(dashboard): dedup displayProvider to familyUtils (T7)` referencing this plan + findings +
Reviewer/Tester verdicts.

## 7. Affected files
1 lib (`familyUtils.ts` param widen) + App.tsx + 6 components (MDSPlot, FreeListCompare, ProviderTree,
PileStructure, ContentArea, CentralityChart) + the test extension. No new files.

---

## OUTCOME — T7 DONE (`abf74bd`)
Architect → Coder → Reviewer **PASS** → Tester **PASS**. 7 identical local copies (6
`displayProvider` + 1 `resolveProvider`) deduped to the canonical `familyUtils.ts:59`
(param widened to `{provider, family}`); orphaned `FAMILY_TO_PROVIDER` removed; +10 tests
(74→84). build+test+lint green; no `packages/`/DESIGN_SYSTEM edits.

### Reviewer verdict — PASS
All 9 binding checks pass. Canonical body byte-unchanged (only the param type widened) →
behavior preserved; tsc passing proves every call site type-checks. All 7 locals gone (grep
zero), `resolveProvider` renamed, `FAMILY_TO_PROVIDER` deleted (grep zero). **The Coder's
`ModelRef`-into-`CentralityChartProps.models` adaptation verified behavior-neutral** — a pure
type-alias identity swap (inline `{model_id,provider,family}` → the identical named interface),
zero runtime effect, resolving the dead-alias error left by deleting `resolveProvider`. Scope
clean; T10 color/token territory untouched.

### Tester verdict — PASS
build ✓ / 84 tests / lint clean. **Revert-and-confirm-fail:** planting a local
`function displayProvider` in ProviderTree made the T7 re-drift guard FAIL (named the file),
`git checkout` restore → green — guard is load-bearing. Pinned-output coverage complete: all 5
openrouter map keys + unmapped fall-through (qwen→openrouter) + 3 non-openrouter pass-throughs.
Tree clean.
