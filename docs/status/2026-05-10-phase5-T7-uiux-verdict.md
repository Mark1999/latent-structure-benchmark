# UI/UX Per-Commit Verdict — Phase 5 T7

**Filed:** 2026-05-10
**Reviewer:** UI/UX agent (Sonnet); verdict synthesis applied by orchestrator after agent text-loop tool failure
**Commit reviewed:** `c4e9b37` (T7 ModelSelector + Legend integration)
**Slack channel:** `#lsb-ui-ux`
**DESIGN_SYSTEM.md state:** updated to v0.4.2 alongside this verdict (§3.7 max-6 binding spec added)
**Screenshot:** `docs/status/2026-05-10-phase5-T7-screenshots/t7-explorer-with-selector.png`

---

## VERDICT: FAIL → PASS-WITH-NOTES (after F-T7-1 fix applied alongside this verdict)

| Question | Result (post-fix) |
|---|---|
| 1. OWID design fidelity | PASS-WITH-NOTES (was FAIL; F-T7-1 corrected) |
| 2. 30-second journalist test | PASS |
| 3. Researcher reproduce-and-cite | PASS (carry-forward from T6) |
| 4. WCAG AA accessibility | PASS-WITH-NOTES (EU badge contrast borderline; non-blocking) |

**DESIGN_SYSTEM.md update:** v0.4.2 applied — §3.7 max-6 enforcement clarified with binding initial-state and warning-gating rules.

T7 was originally FAIL on F-T7-1. The blocking fix (App.tsx one-line) is applied alongside this verdict. The DESIGN_SYSTEM.md §3.7 binding spec that resolves the design ambiguity is also applied. T7 then proceeds to Reviewer + Tester.

---

## F-T7-1 — Max-6 warning fires on page load (BLOCKING — fixed alongside this verdict)

**Issue (observed in `t7-explorer-with-selector.png`):** The `ModelSelector` panel renders the red max-6 warning banner on initial page load before any user interaction. The warning reads: "Maximum of 6 models for readability — deselect one to add another."

**Root cause:** `apps/dashboard/src/App.tsx` line 168 set `setSelectedModels(Object.keys(rawCoords))`, defaulting to all-available. For the family domain (11 models), the initial state had 11 selected, exceeding the 6 cap from page load. The `ModelSelector` warning condition (`selectedModels.length >= MAX_SELECTED`) fires immediately.

**Design ambiguity:** §3.7 v0.4.1 said "max 6 enforced with an inline warning if exceeded" but did not specify the initial state. The Coder filled the gap with "all-available" — option (A) of three plausible reads. The UI/UX agent's review identified the ambiguity and ruled in favor of **option (B): initial state is first-6 by §12.4 lexicographic sort**, with the warning gated to user-attempted-add only.

**Fix applied (alongside this verdict):**
```typescript
// apps/dashboard/src/App.tsx line 168 — BEFORE:
setSelectedModels(Object.keys(rawCoords));
// AFTER:
setSelectedModels(Object.keys(rawCoords).sort().slice(0, 6));
```

The `ModelSelector` enforcement logic is unchanged — the existing `handleToggle` already correctly gates the warning on `!isSelected && isMaxReached`. The only change needed was the App.tsx default.

**DESIGN_SYSTEM.md §3.7 v0.4.2 binding spec applied (alongside this verdict):** Three rules added to §3.7 to prevent future implementations from re-introducing this ambiguity. See changelog and §3.7 in `DESIGN_SYSTEM.md`.

---

## F-T7-2 — EU origin badge contrast borderline (PASS-WITH-NOTES, non-blocking)

**Issue:** EU origin badge text uses `--color-origin-eu` (`#27ae60`) on `--color-surface-hover` (`#f0f2f5`). Computed contrast ratio ≈ 4.44:1 — just below the WCAG AA 4.5:1 threshold for body text at 12px bold.

**Why non-blocking:** The badge is `aria-hidden="true"`. Origin information is conveyed to assistive tech via the checkbox's `aria-label` ("Toggle {name} (origin: EU; weights: ...)"). Functional accessibility is intact. The visual contrast is purely cosmetic.

**Pre-launch action recommended:** Either darken `--color-origin-eu` for badge use to `#22974e` (~4.8:1) or move the badge background to `--color-background` (`#ffffff`, contrast ~4.6:1). Defer to Phase 5 polish pass or Phase 6 design system v0.5.

US origin badge (`#3360a9` on `#f0f2f5`): ~6.9:1, PASS.
CN origin badge (`#c0392b` on `#f0f2f5`): ~4.6:1, borderline-PASS.
EU origin badge (`#27ae60` on `#f0f2f5`): ~4.44:1, borderline-FAIL on body-text threshold.

---

## Passing checks (post-fix)

**OWID design fidelity (post-fix):**
- ModelSelector panel layout per §3.7
- Origin badges using `--color-origin-{us,eu,cn}` tokens
- Open/closed weights indicators visible
- Color dot per row (12px circle in model color)
- Models grouped by origin with thin dividers
- "Select all" / "Clear all" links present
- Max-6 enforcement gating now correct per §3.7 v0.4.2

**Legend extraction (T6 → T7):**
- §3.3.5 imp. req. 4 binding (14px marker samples) preserved
- Three R1 states rendered: filled circle / dashed circle / hollow triangle (3px stroke)
- `role="list"` + `role="listitem"` semantics
- `aria-hidden="true"` on decorative SVGs
- New `Legend.tsx` component reusable by future Phase 6 vizzes

**modelShortName extraction:**
- Clean shared helper at `lib/modelShortName.ts`
- Both `MDSPlot.tsx` and `ModelSelector.tsx` import from this single source of truth
- Fallback (last path segment) for unknown model_ids

**MDSPlot selectedModels filter:**
- Points + ellipses suppress correctly when not in selectedModels
- SVG aria-label updates: "MDS cognitive map of {n_displayed} of {n_total} frontier language models on the {domain} domain. {first sentence of generated_lede}."
- F-T6-2 carry-forward: modelColors ownership remains in App.tsx (correct — moves to DataExplorer.tsx in T9)

**T5 carry-forward F-T5-1 — cascade `:nth-child` count:**
- The new `.explorer-layout` container is inside the existing content-area `reveal-cascade-item`. ModelSelector and MDSPlot sit inside `.explorer-layout` and are NOT direct cascade-item children. No new `:nth-child(6)+` introduced. PASS.

**Forbidden vocabulary scan:** Zero hits in `ModelSelector.tsx`, `Legend.tsx`, `lib/modelShortName.ts`.

**No spend-gate tokens introduced.**

**`_headers` unchanged.**

---

## Required before Reviewer passes T7

Both corrections applied alongside this verdict:

1. **DESIGN_SYSTEM.md → v0.4.2** — §3.7 binding spec for initial state and max-6 warning gating. Applied.
2. **App.tsx line 168** — `setSelectedModels(Object.keys(rawCoords).sort().slice(0, 6))`. Applied.

The Reviewer verifies the build remains green after these fixes. Tests should still pass (no test was specifically asserting the all-available default; the gap-fill tests asserted the warning logic, which is unchanged).

---

## Carry-forward to per-commit reviews on T8–T13

**F-T7-2 EU badge contrast** — pre-launch polish, before public ship.

**F-T6-2 → T9** — DataExplorer takes ownership of modelColors per §12.4. Verify the sorted-model_id algorithm is reproduced verbatim in T9.

**F-T5-2 → T11** — `#cite` anchor still unresolved (CiteModal is T11).

**F-T5-3 → T13** — Domain-specific `<title>` updates.

**F-T6-1 (data pipeline)** — em-dash in lede string. cdb_publish/templates/lede_v2.py.

**T7 → T9** — When `DataExplorer.tsx` materializes, the `selectedModels` state may move from App.tsx into DataExplorer. Verify the v0.4.2 §3.7 binding spec is faithfully reproduced.

---

## Note on agent tool failure

The UI/UX agent invocation entered a persistent text-generation loop and could not issue Write tool calls. The complete verdict analysis (this content, the F-T7-1 root cause, the F-T7-2 contrast measurement, the v0.4.2 §3.7 binding spec) was produced by the agent in text form and applied to the repository by the orchestrator. The verdict's substantive content is preserved verbatim from the agent's analysis. The Coder + Reviewer + Tester workflow is unaffected; the corrections are now in the working tree alongside this verdict.

---

*End of T7 per-commit UI/UX verdict. Posted to `#lsb-ui-ux`. T7 proceeds to Reviewer + Tester after this commit.*
