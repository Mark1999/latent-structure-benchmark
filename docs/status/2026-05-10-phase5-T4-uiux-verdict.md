# UI/UX Per-Commit Verdict — Phase 5 T4

**Filed:** 2026-05-10
**Reviewer:** UI/UX agent (Sonnet)
**Commit reviewed:** `1b7064f` (T4 dashboard scaffold + tokens + page-load shell)
**Slack channel:** `#lsb-ui-ux`
**DESIGN_SYSTEM.md state:** updated to v0.4.1 alongside this verdict (slot 11 contrast correction)

---

## VERDICT: PASS-WITH-NOTES

| Question | Result |
|---|---|
| 1. OWID design fidelity | PASS-WITH-NOTES (animation cascade was 20ms over §12.1 cap; corrected) |
| 2. 30-second journalist test | PASS |
| 3. Researcher reproduce-and-cite | PASS |
| 4. WCAG AA accessibility | PASS-WITH-NOTES (`--color-model-11` failed 3:1 contrast; corrected) |

T4 is approved with two binding corrections applied alongside this verdict (one design-system error attributable to the document, one Coder implementation drift). After these corrections land, T4 may proceed to Reviewer + Tester without further rework.

---

## Findings (with corrections applied)

### F-T4-1 — Animation cascade duration exceeded 600ms binding cap

**Issue:** `apps/dashboard/src/styles/app.css` line 65 had `animation-duration: 300ms`. With `nth-child(5)` carrying `animation-delay: 320ms`, total cascade duration = 320 + 300 = **620ms**, exceeding DESIGN_SYSTEM.md §12.1's binding cap of 600ms by 20ms.

**Fix applied:** changed `animation-duration` from `300ms` to `280ms`. Total cascade now 320 + 280 = **600ms** exactly, satisfying the binding cap.

All other §12.1 properties were correct: `ease-out` only, `opacity` + `transform: translateY(8px)` only, `prefers-reduced-motion: reduce` override, fires once.

### F-T4-2 — `--color-model-11` failed WCAG AA 3:1 contrast on white

**Issue:** DESIGN_SYSTEM.md v0.4 specified `--color-model-11: #b7950b`. Computed contrast ratio against white ≈ **2.89:1**, below the 3:1 minimum for graphical objects in WCAG AA. The Coder faithfully copied the value; this was a design-system error, not a Coder error.

**Fix applied:**
1. DESIGN_SYSTEM.md updated to v0.4.1 with `--color-model-11: #9a7d0a` (dark gold, contrast ≈ 3.96:1).
2. §12.4 paragraph updated to enumerate verified contrast ratios for all five extended slots (slot 7: 4.5:1; slot 8: 7.2:1; slot 9: 5.0:1; slot 10: 4.0:1; slot 11: 3.96:1).
3. `apps/dashboard/src/styles/tokens.css` line 92 updated to `#9a7d0a` to match.

The hue family (dark gold) is preserved.

---

## Passing checks

**F1 (react-dom version) — PASS.** `react: ^19.2.5`, `react-dom: ^19.2.5`, `@types/react-dom: ^19.2.0`. Aligned. `npm install` succeeds without `--legacy-peer-deps`.

**F3 (extended palette tokens) — PASS** (with the slot-11 correction applied above). Tokens 7–11 present in `tokens.css` with corrected values verbatim from DESIGN_SYSTEM.md v0.4.1.

**§12.2 (loading state) — PASS.** "Loading..." in `--color-text-muted` at `--font-size-base`. No spinner, no shimmer. `role="status"`, `aria-live="polite"` on loading; `role="alert"`, `aria-live="assertive"` on error. Error text exact match to spec.

**§12.5 (embed mode) — PASS.** `isEmbedMode()` correctly implements the URL parameter check. In embed mode only `<div className="embed-root">` renders; Header/ArticleHeader/Footer suppressed. `_headers` `frame-ancestors 'none'` intact (T12 gate preserved).

**TAGLINE canonical (Q8) — PASS.** Byte-identical to ARCHITECTURE.md §1.5. US English ("categorize" / "organize"). No "categorise" / "organise" anywhere in source. Test suite enforces with pattern-matching assertions.

**CSP / self-hosted fonts (AC6) — PASS.** No Google Fonts CDN linkage. Four woff2 files under `public/fonts/`. `@font-face` declarations use relative `/fonts/...` paths. `_headers` unchanged.

**OCI config constant — PASS.** `OCI_LOW_CONCENTRATION_THRESHOLD = 3.0` in `src/config/analysis.ts` per §3.3.5 item 7.

**WCAG AA on chrome — PASS.** Body text contrast ≈ 9.7:1 (`#2c3e50` on white). Secondary text ≈ 3.9:1. Focus indicators present on all interactive elements via `outline: 2px solid var(--color-info)`.

**No forbidden vocabulary (AC9) — PASS.** Substring scan against §1.5.4 + CLAUDE.md §7 list returns zero hits in dashboard source.

**Bundle size (AC4) — PASS.** Built JS gzipped to ~64KB (well under the T4 stage 100KB ceiling and the §9 production cap of 400KB).

**No `cdb_*` imports in TS (AC7) — PASS.** Boundary discipline preserved.

---

## Required before Reviewer passes T4

Both corrections are applied alongside this verdict in the same orchestrator commit. The Reviewer verifies:
1. `git grep "9a7d0a" apps/dashboard/src/styles/tokens.css DESIGN_SYSTEM.md` — should return at least 2 matches.
2. `git grep "b7950b" apps/dashboard/src/styles/tokens.css` — should return zero matches (only the historical reference in DESIGN_SYSTEM.md v0.4.1 changelog remains, which is fine).
3. `grep "animation: revealFade 280ms" apps/dashboard/src/styles/app.css` — should return 1 match.
4. `grep "300ms" apps/dashboard/src/styles/app.css` — should return zero matches related to revealFade.

---

## Minor observation (non-blocking, carry-forward to T11)

The `#cite` anchor in ArticleHeader and Footer resolves to nothing at T4 (no `id="cite"` element). This is expected — the CiteModal component is T11. Clicking "Cite this" at T4 stage scrolls to top silently. Becomes a blocking issue at T11, not before.

---

## Carry-forward to per-commit reviews on T5–T13

The four-question scorecard applies to every per-commit review. Specific notes for upcoming commits:

- **T5 (DomainPicker + KeyFinding):** the KeyFinding component reads `generated_lede` from the published JSON and must render without forbidden vocabulary. The 200ms fade on domain switch (per §3.8) should respect `prefers-reduced-motion`.
- **T6 (MDSPlot):** §3.3.5 R1-state rendering bindings — hollow triangle stroke 3px, dashed circle 100% stroke opacity / 60% fill opacity, legend marker samples (item 4). The SVG container must carry the descriptive `aria-label` per §12.6.
- **T8 (VizSwitcher):** disabled tabs are focusable with `aria-disabled="true"` per §12.3 (overrides the original T8 plan spec). Tooltip text: "Coming in a future update."
- **T9 (DataExplorer):** `Map<model_id, color>` computed at mount via sorted `model_id → slot` per §12.4. No child component computes its own color.
- **T11 (PNG export):** explicit `canvas.width = 2000; canvas.height = 2000` for hi-res; watermark position as % of canvas dimensions.
- **T12 (Embed modal):** `_headers` frame-ancestors change requires SECURITY_AND_HARDENING.md sign-off before commit.
- **T13 (final integration):** mobile 375px verification before merge; SVG `aria-label` from T6 must be present.

---

*End of T4 per-commit UI/UX verdict. Reviewer + Tester proceed after the two corrections land.*
