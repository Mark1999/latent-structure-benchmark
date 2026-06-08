# T8 — `displayModel` canonical label — UI/UX verdict + Mark override (2026-06-08)

**Task:** T8 (model-label dedup). Plan: `docs/status/2026-06-08-T8-architect-plan.md`.
**Gate:** UI/UX (frontend, canonical-form design decision). **Verdict:** **PASS-WITH-NOTES.**

## SCOPE CORRECTION (2026-06-08, post-Coder-round-1)
The Architect's 13-site inventory was INCOMPLETE. The Coder's re-drift guard tripped on
3 more model-label sites it then scoped *around* (should have surfaced). True count = **16**:
- `Sidebar.tsx:128` (inline `m.model_id.split('/').pop()`) — showed `claude-opus-4-5`, the live bug.
- `Timeline.tsx:62` (inline `id.split('/').pop()?.replace(/^[a-z]+-/,'')`) — produced the
  `grok-4`→`4` / `phi-4`→`4` COLLISIONS Mark rejected; folding it into `displayModel` removes them.
- `TermMap.tsx:86` `shortModelDisplayName` (a THIRD helper name) — produced Title-Case branded
  labels (`Claude Opus 4 5`, `Grok 4`).
**Mark's ruling (2026-06-08):** TermMap CONFORMS to canonical `displayModel` (Title-Case form
DROPPED) — one label form everywhere. All 3 sites fold into T8; the re-drift guard tightens to
cover ALL of `components/` and all three function names (`shortName`/`shortModelName`/
`shortModelDisplayName`). DESIGN_SYSTEM §18.8 site list updated 13→16.
**Four criteria:** OWID fidelity PASS / 30-sec journalist PASS / reproduce-and-cite PASS /
WCAG AA PASS.

## Binding decisions
- **D.1 strip rule — AMENDED BY MARK (2026-06-08).** The UI/UX gate originally ruled
  "strip all provider/family prefixes" (`grok-4`→`4`, `phi-4`→`4`). That produces
  **collisions** (two models both render `4`) and loses model identity for single-token
  families — it fails the journalist + reproduce-and-cite tests the gate is supposed to
  protect. The gate itself deferred the terseness question to Mark. **Mark's binding call:
  strip the org prefix before `/` AND the Anthropic `claude-` house prefix ONLY; keep every
  other model-family token.** This fixes the actual bug (the `claude-opus-4-5` vs `opus-4-5`
  cross-tab inconsistency) without introducing collisions.
- **D.2 org prefix — strip** everything up to and including the last `/`.
- **D.3 `deepseek-`→`ds-`** — DROPPED (ProviderTree-only drift); under Mark's rule
  `deepseek/deepseek-v3.2` → `deepseek-v3.2` (NOT `ds-v3.2`, NOT `v3.2`).
- **D.4 accessibility** — see §18.5 below (heatmap cell aria-labels use full `model_id`;
  SR summary uses `displayModel(id) (id)` on first mention).

## The canonical transform (BINDING — implement exactly)
`displayModel(modelId: string): string` — pure, never throws, accepts any string:
1. **Org-prefix strip.** If `modelId` contains `/`, discard everything up to and including
   the LAST `/`.
2. **House-prefix strip.** If the result starts with `claude-`, remove that prefix. (ONLY
   `claude-` — no other family token is stripped, per Mark's D.1 ruling.)
3. **Empty guard.** If the result is now empty, return the original `modelId` unchanged.
4. Return the result.

### Worked examples (BINDING — these become the vitest pinned table)
| model_id (raw) | displayModel | note |
|---|---|---|
| `claude-opus-4-5` | `opus-4-5` | no `/`; strip `claude-` |
| `claude-opus-4-6` | `opus-4-6` | |
| `claude-sonnet-4-6` | `sonnet-4-6` | |
| `openai/gpt-5.2` | `gpt-5.2` | strip `openai/`; no `claude-` |
| `openai/gpt-5.4` | `gpt-5.4` | |
| `openai/gpt-5.4-mini` | `gpt-5.4-mini` | |
| `google/gemini-2.5-flash` | `gemini-2.5-flash` | |
| `google/gemini-2.5-pro` | `gemini-2.5-pro` | |
| `meta-llama/llama-4-maverick` | `llama-4-maverick` | |
| `x-ai/grok-4` | `grok-4` | no collision (vs old `4`) |
| `x-ai/grok-4.20` | `grok-4.20` | |
| `mistralai/mistral-large-2512` | `mistral-large-2512` | |
| `mistralai/mistral-small-2603` | `mistral-small-2603` | |
| `deepseek/deepseek-v3.2` | `deepseek-v3.2` | not `ds-v3.2` |
| `microsoft/phi-4` | `phi-4` | no collision (vs old `4`) |
| `unknown-model` | `unknown-model` | no `/`, no `claude-` → unchanged |
| `org/unknown-model` | `unknown-model` | `/` stripped |
| `""` | `""` | empty guard |

## Notes the Coder MUST apply
1. Apply the §18 DESIGN_SYSTEM.md clause (below) in the SAME commit; bump to **v0.14.0**.
2. `SimilarityHeatmap.tsx:142` per-cell `aria-label` uses the full `model_id` (NOT
   `displayModel`) for row+col — SR user navigating cells has no spatial context. If it
   already uses `model_id`, no change.
3. `CentralityChart.tsx:158` SR summary uses `displayModel(id) (id)` on first mention, then
   `displayModel(id)` after.
4. Commit body must call out the visible ProviderTree label change (`ds-v3.2`→`deepseek-v3.2`).
5. Visible churn to expect: the 5 sites that showed `claude-opus-4-5` now show `opus-4-5`
   (the bug fix). `gpt-*`/`gemini-*`/etc. are unchanged from their current majority form.

## DESIGN_SYSTEM.md §18 — clause to paste (Mark's variant)
Add as new **§18** after §17; bump header + changelog to **v0.14.0**.

Changelog entry:
```
- **v0.14.0** (displayModel canonical label — T8, 2026-06-08) adds §18. Single canonical
  export `displayModel(modelId)` in familyUtils.ts; bans component-local re-implementation;
  collapses the 13 drifted shortName/shortModelName helpers. Strip rule (Mark's ruling):
  org prefix + `claude-` only. No new tokens. UI/UX PASS-WITH-NOTES.
```

§18 body:
```markdown
## 18. Model display label canonical form (v0.14.0 — T8, 2026-06-08)

### 18.1 Problem
The dashboard previously computed a model's short label via 13 copy-pasted local helpers
(`shortName` ×6, `shortModelName` ×7) that had drifted — `claude-opus-4-5` rendered as
`claude-opus-4-5` on some tabs and `opus-4-5` on others. This section is binding.

### 18.2 Single canonical export
`export function displayModel(modelId: string): string` lives ONLY in
`apps/dashboard/src/lib/familyUtils.ts`. No component may define a local `shortName` /
`shortModelName` / equivalent. The Reviewer rejects any new component that reintroduces one
(enforced by the T8 vitest re-drift grep guards).

### 18.3 The transform (pure, never throws)
1. **Org-prefix strip:** if the id contains `/`, discard everything up to and including the
   last `/`.
2. **House-prefix strip:** if the result starts with `claude-`, remove that prefix. Only
   `claude-` is stripped — no other model-family token (`gpt-`, `gemini-`, `grok-`, `phi-`,
   `mistral-`, `deepseek-`, `llama-`) is removed, so single-token model names remain
   distinct and no two models collide on the same label.
3. **Empty guard:** if the result is empty, return the original input.

### 18.4 Worked examples (binding)
`claude-opus-4-5`→`opus-4-5`; `claude-sonnet-4-6`→`sonnet-4-6`; `openai/gpt-5.2`→`gpt-5.2`;
`google/gemini-2.5-pro`→`gemini-2.5-pro`; `meta-llama/llama-4-maverick`→`llama-4-maverick`;
`x-ai/grok-4`→`grok-4`; `mistralai/mistral-large-2512`→`mistral-large-2512`;
`deepseek/deepseek-v3.2`→`deepseek-v3.2`; `microsoft/phi-4`→`phi-4`;
`unknown-model`→`unknown-model`; `org/unknown-model`→`unknown-model`; `""`→`""`.

### 18.5 Accessibility
The visual chip uses `displayModel(modelId)`. Two surfaces use a more verbose form:
1. **SimilarityHeatmap per-cell `aria-label`** uses the full `model_id` for both row and
   column (cell-by-cell SR navigation has no spatial context).
2. **CentralityChart SR summary sentence** uses `displayModel(id) (id)` on first mention of
   each model, then `displayModel(id)` after.
All other aria-labels / tooltips / chips use `displayModel(modelId)` directly.

### 18.6 Notable visible change
ProviderTree previously abbreviated `deepseek-`→`ds-`. Under this rule
`deepseek/deepseek-v3.2`→`deepseek-v3.2` (label changes `ds-v3.2`→`deepseek-v3.2`).
Deliberate correction.

### 18.7 New providers
If a provider whose id carries a different house-prefix convention is added (e.g. a future
case where the org token IS the display identity), route a new UI/UX gate pass before it
appears on any surface. Do not invent a component-local workaround.

### 18.8 Sites using displayModel (all import from familyUtils.ts, none define a local copy)
shortName family (6): MDSPlot:43, CentralityTable:10, CentralityChart:44,
Focus2FamilySimilarity:31, SimilarityHeatmap:33, Focus1SelfConsistencyOverview:35.
shortModelName family (7): Focus2FamilyOverview:36, PileStructure:48, FreeListCompare:49,
ContentArea:50, Focus1RunDistribution:176, Focus1TermStability:18, ProviderTree:47.
ContentArea:113 special case: `shortName: shortModelName(...)` → `shortName: displayModel(...)`
(the SelectionBar.ModelInfo `shortName` FIELD name is preserved — it is a typed field).
```

---

## OUTCOME — T8 DONE (`c32c773`)
Architect → UI/UX PASS-WITH-NOTES (+ Mark's strip-rule override + SCOPE CORRECTION 13→16) →
Coder (round 1 `6c059c7` → amended round 2 `ba9f3db` → changelog fix `c32c773`) →
Reviewer **PASS** → Tester **PASS**. 16 sites unified to `displayModel`; DESIGN_SYSTEM §18 added
(v0.14.0); 74 tests (build+lint green). Visible changes: 5 `claude-*`-keeping sites now show
`opus-4-5` (the bug fix); ProviderTree `ds-v3.2`→`deepseek-v3.2`; TermMap Title-Case dropped;
Timeline `grok-4`/`phi-4`→`4` collisions removed.

### Reviewer verdict — PASS
All 9 binding checks pass. Transform matches Mark's no-collision rule EXACTLY (strip org + only
`claude-`; `grok-4`→`grok-4`, `phi-4`→`phi-4`, not `4`). All 16 sites consolidated (0 helper fns,
0 inline idioms in components/). Re-drift guard confirmed genuinely broad (glob `components/**`,
≥16 files, bans all 3 fn names + both idioms) — the round-1 narrow-scoping that hid the 3 sites
is fixed. Accessibility: heatmap cell aria-label uses full `model_id`; CentralityChart SR summary
uses `displayModel(id) (id)`. SelectionBar untouched (typed field preserved). DESIGN_SYSTEM §18
co-update present (R7-style). Scope clean (no `packages/` edits).

### Tester verdict — PASS
build ✓ / 74 tests / lint clean. **Two revert-and-confirm-fail cycles:** (1) planting a local
`function shortName` in Sidebar made the re-drift guard FAIL (`["../../components/Sidebar.tsx"]`),
restore → green — proves the guard protects ALL components incl. the round-2 sites; (2) adding a
`grok-` strip to `displayModel` made pinned tests FAIL (`grok-4`→`4`, `grok-4.20`→`4.20`),
restore → green — proves the suite pins Mark's no-collision rule against future regression.
Coverage complete (18 pinned rows = all 8 providers + 3 edge cases). Tree clean.
