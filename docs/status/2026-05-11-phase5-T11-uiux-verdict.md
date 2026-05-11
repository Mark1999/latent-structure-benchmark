# UI/UX Per-Commit Verdict — Phase 5 T11 (PNG export)

**Filed:** 2026-05-11
**Reviewer:** UI/UX agent (Sonnet)
**Commit reviewed:** `727d9a9` — "feat(dashboard): T11 PNG export with canvas + tEXt metadata + watermark"
**Slack channel:** `#lsb-ui-ux`
**DESIGN_SYSTEM.md state:** v0.4.3 (no update required for T11)

---

## VERDICT: FAIL → PASS-WITH-NOTES (after two WCAG fixes applied alongside this verdict)

| Criterion | Result (post-fix) |
|---|---|
| 1. OWID design fidelity | PASS |
| 2. 30-second journalist test | PASS |
| 3. Researcher reproduce-and-cite | PASS |
| 4. WCAG AA accessibility | PASS-WITH-NOTES (was FAIL; F-T11-1 and F-T11-2 corrected) |

**DESIGN_SYSTEM.md update:** not required. v0.4.3 already establishes both the `--color-text-caption` token and the DownloadBar `:focus-visible` pattern. T11 failed to apply the existing rules to the new PNG buttons. No new visual decisions are introduced by T11 that require a design-system extension.

T11 was originally FAIL on both findings (WCAG AA contrast + focus-visible inconsistency). Both blocking corrections applied alongside this verdict. T11 then proceeds to Reviewer + Tester.

---

## F-T11-1 — PNG buttons missing `:focus-visible` rule (BLOCKING — fixed alongside this verdict)

**Issue:** The T10 verdict (F-T10-2, BLOCKING, fixed) established that all DownloadBar buttons require explicit `:focus-visible` rules matching the design-system pattern — browser-default focus rings are inconsistent across user-agents and do not satisfy DESIGN_SYSTEM.md §7. The fix at T10 added a rule block for `.download-bar__csv-btn` and `.download-bar__permalink-btn`. T11 adds `.download-bar__png-btn` and `.download-bar__png-hires-btn` but did not extend `app.css`. Both new buttons fell through to browser defaults — WCAG 2.4.7 violation.

**Fix applied (alongside this verdict):** Extended the focus-visible selector block in `apps/dashboard/src/styles/app.css` to include both new button classes; updated the comment to reference T11 finding 1.

```css
.download-bar__csv-btn:focus-visible,
.download-bar__permalink-btn:focus-visible,
.download-bar__png-btn:focus-visible,
.download-bar__png-hires-btn:focus-visible {
  outline: 2px solid var(--color-info);
  outline-offset: 2px;
  border-radius: var(--border-radius-sm);
}
```

## F-T11-2 — Hi-res link button uses `--color-text-secondary` at 12px (BLOCKING — fixed alongside this verdict)

**Issue:** `DownloadBar.tsx` `linkStyle.color` was `"var(--color-text-secondary)"` (`#7f8c8d`, ~3.40:1 on white) at `font-size: "var(--font-size-xs)"` = 12px regular weight. DESIGN_SYSTEM.md v0.4.3 is explicit: `--color-text-secondary` is for bold or large secondary labels (14px+); it does not meet the 4.5:1 WCAG AA minimum for 12px regular-weight text. The correct token — established by v0.4.3 specifically for 12px readable text — is `--color-text-caption` (`#6c757d`, ~4.60:1 on white). Same token error class as F-T10-1 (which was resolved for `SourceAttribution.tsx` at T10 but not carried forward to the new link button at T11).

**Fix applied (alongside this verdict):** Switched `DownloadBar.tsx` `linkStyle.color` from `--color-text-secondary` to `--color-text-caption` with an inline comment referencing T11 finding 2.

---

## Passing checks

**F5.1 — Explicit canvas dimensions:** `canvas.width = canvasWidth` and `canvas.height = canvasHeight` set explicitly at lines 129–130 of `png-export.ts`, backed by a typed `CANVAS_DIMS` lookup table (`social: {1600, 900}`, `highres: {2000, 2000}`). Verified ≥4 hits matching `canvas\.(width|height)\s*=`.

**F5.2 — Watermark position as % of canvas:** `marginRight = canvasWidth * 0.02`, `marginBottom = canvasHeight * 0.02` (lines 147–148). Font size `= canvasWidth * 0.012` (line 152). Opacity `ctx.globalAlpha = 0.03` (line 157). All three F5 percentage constants present.

**F5.3 — Font size scales with canvas:** `fontSize = canvasWidth * 0.012` produces 19.2px at 1600px (social) and 24px at 2000px (highres). Identical visual weight across both export sizes per F5 binding. Confirmed by `png-export.test.ts` assertions at lines 274–283.

**Watermark visual posture (OWID restraint):** Text is `"cogstructurelab.com"` at 3% opacity, monospace font, bottom-right anchor. Monospace signals metadata rather than decorative text — correct per DESIGN_SYSTEM.md §1.1 (`--font-mono` for data values and citations). 3% opacity is below perceptual detection threshold in most viewing contexts.

**tEXt 8-field check:** All 8 required fields present in `buildPngMetadata()` (`DownloadBar.tsx` lines 92–100): `Title`, `Author`, `Source`, `Software`, `Domain`, `Models`, `Analysis-Version`, `Generated-At`. The `Title` value (`"Cognitive Structure Lab - {domain} domain - MDS"`) is editorial-grade. ASCII hyphen used in place of em-dash because tEXt is Latin-1 — correct per PNG spec.

**File naming:** `lsb-${domainResult.domain_slug}-mds-${suffix}.png` with `suffix` = `"social"` or `"highres"` (line 195). Matches plan spec.

**Button labels:** "Download PNG (social)" + "hi-res (2000×2000)". Primary/secondary affordance hierarchy clear: primary is full-weight bordered button for the common case; hi-res is understated underlined link below it. 30-second journalist test: PASS.

**ARIA labels:** PNG social button carries `aria-label="Download chart as PNG (social)"`; hi-res button carries `aria-label="Download chart as PNG (hi-res)"`. Both labels contain "PNG" and the size variant. Test coverage confirms.

**Keyboard activation:** All four buttons use `type="button"` with `onClick`. No keydown-only patterns. `disabled` attribute correctly set during `pngState === "loading"`.

**Loading and error states:** `pngState` state machine (`idle | loading | error`) produces appropriate transient feedback ("Exporting…" / "PNG export failed" with 3-second auto-reset). Informational, OWID-consistent.

**CSP unchanged:** `apps/dashboard/public/_headers` retains `frame-ancestors 'none'` and all other headers from T10. Not touched by T11. (T12 will need to revisit this for the embed iframe.)

**Forbidden vocabulary:** Zero matches for `believes`, `thinks`, `worldview`, `recognizes`, `interprets`, `perceives`, `comprehends` in any of the three new/modified files.

**tEXt chunk correctness:** `png-metadata.ts` implements RFC 2083-compliant CRC-32 (reflected CCITT-32, 0xEDB88320 polynomial), correct chunk ordering (tEXt before IDAT), correct data layout (keyword + NUL + text). 18-test suite covers signature preservation, chunk ordering, CRC correctness, full round-trip kv recovery, empty-kv passthrough, error rejection.

---

## Required before Reviewer passes T11

Both corrections applied alongside this verdict:

1. **`apps/dashboard/src/styles/app.css`** — extended `:focus-visible` selector block to include `.download-bar__png-btn` and `.download-bar__png-hires-btn`; comment updated to reference T11 finding 1.
2. **`apps/dashboard/src/components/DownloadBar.tsx`** — `linkStyle.color` changed from `--color-text-secondary` to `--color-text-caption`; inline comment added referencing T11 finding 2.

Reviewer verifies build remains green after these fixes.

---

## Carry-forward to T12–T13

- **F-T10-3, F-T10-4 (deferred at T10):** CC-BY 4.0 affordance, Cite this modal, View raw data link. Remain T12 scope.
- **T12 gate:** `frame-ancestors 'none'` in `_headers` is intact. The embed modal's `<iframe>` requires a `frame-ancestors` relaxation — this must go through the Reviewer + `SECURITY_AND_HARDENING.md` review process before T12 commits, per §12.5 binding.
- **T13 gate:** `MethodologySummary` prose requires CDA SME review in addition to UI/UX. T11 introduces no new methodology claims.
- The `--color-text-caption` token pattern is now established for both `SourceAttribution.tsx` (T10) and `DownloadBar.tsx` `linkStyle` (T11). Any future 12px readable text must use this token.

---

*End of T11 per-commit UI/UX verdict. Posted to `#lsb-ui-ux`. Reviewer + Tester proceed after this commit.*
