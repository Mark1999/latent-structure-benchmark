# UI/UX Per-Commit Verdict — Phase 5 T10 (SourceAttribution + DownloadBar)

**Filed:** 2026-05-10
**Reviewer:** UI/UX agent (Sonnet)
**Commit reviewed:** `2feccd8` — SourceAttribution + DownloadBar (CSV + permalink)
**Slack channel:** `#lsb-ui-ux`
**DESIGN_SYSTEM.md state:** updated to v0.4.3 alongside this verdict (new `--color-text-caption` token)
**Visual reference:** `docs/status/2026-05-10-phase5-T10-screenshots/t10-source-download.png`

---

## VERDICT: FAIL → PASS-WITH-NOTES (after WCAG fixes applied alongside this verdict)

| Criterion | Result (post-fix) |
|---|---|
| 1. OWID design fidelity | PASS-WITH-NOTES |
| 2. 30-second journalist test | PASS |
| 3. Researcher reproduce-and-cite | PASS-WITH-NOTES |
| 4. WCAG AA accessibility | PASS-WITH-NOTES (was FAIL; F-T10-1 and F-T10-2 corrected) |

**DESIGN_SYSTEM.md update:** v0.4.3 applied — adds `--color-text-caption: #6c757d` (~4.60:1 on white) for WCAG-compliant caption-grade text.

T10 was originally FAIL on F-T10-1 WCAG AA contrast violation. Both blocking corrections applied alongside this verdict. T10 then proceeds to Reviewer + Tester.

---

## F-T10-1 — WCAG AA contrast violation on SourceAttribution (BLOCKING — fixed alongside this verdict)

**Issue:** `SourceAttribution.tsx` line 74 applied `color: "var(--color-text-muted)"` (`#bdc3c7`) to the outer div, which is inherited by all text in the component. At 12px regular weight on white, `#bdc3c7` produces ~1.75:1 contrast — far below the WCAG AA 4.5:1 minimum for body text. The small-n note used `--color-text-secondary` (`#7f8c8d`) at ~3.40:1 — still insufficient for 12px regular.

**Design-system gap exposed:** v0.4.2 had no token suitable for small-but-readable text. The Coder picked `--color-text-muted` reasonably; the gap was in the token system.

**Fix applied (alongside this verdict):**
1. DESIGN_SYSTEM.md → v0.4.3 with new `--color-text-caption: #6c757d` (~4.60:1 on white).
2. `apps/dashboard/src/styles/tokens.css` extended with the new token + clarified annotations on `--color-text-secondary` and `--color-text-muted`.
3. `apps/dashboard/src/components/SourceAttribution.tsx` line 74 and line 114 switched from `--color-text-muted` / `--color-text-secondary` to `--color-text-caption`.

## F-T10-2 — DownloadBar buttons lack explicit focus-visible rule (BLOCKING — fixed alongside this verdict)

**Issue:** `DownloadBar.tsx` buttons relied on browser-default focus rings. Every other interactive element in the codebase has an explicit `:focus-visible` rule in `app.css`. Inconsistency with design-system pattern.

**Fix applied:** Added `.download-bar__csv-btn:focus-visible` and `.download-bar__permalink-btn:focus-visible` rules to `app.css` with the standard 2px solid `--color-info` outline + 2px offset.

---

## Passing checks (post-fix)

**§5 source line content:** model list (with "+N more" overflow), domain slug, prompt v1, analysis v0.2, collection month from `generated_at`. Verified on screenshot.

**Q2 small-n binding (CDA SME):** `romney_small_n_warning` gate fires correctly when `true`; suppresses when `false`. Family and holidays both trip the flag (n=11, n=9, both <15). Note copy is descriptive ("Small-n note: this measurement is computed at n=X models, below the n=15 threshold..."), satisfying Q3.

**§5 CSV columns:** All 12 binding columns in correct order: `model_id, family, origin, mds_x, mds_y, semi_major, semi_minor, rotation_rad, n_bootstrap, oci, deterministic_output, r1_state`. Ellipse params empty for R1-b and R1-c rows per §3.3.5 binding invariant 1. RFC 4180 quoting on special chars.

**Permalink round-trip:** `encodePermalink` + `decodePermalink` are pure inverses. URL format `?domain=family&models=a,b,c#mds` (unified from T8's bare `#mds`). Models with `/` chars round-trip via URLSearchParams encoding. Invalid inputs return null.

**URL sync (DataExplorer):** `readSelectedModelsFromUrl` validates domain match + model existence before restoring. `writePermalinkState` fires on `selectedModels` or `activeVizTab` change. Domain-change reset to first-6 preserved per §3.7 v0.4.2.

**App.tsx `readInitialDomainFromUrl`:** reads `?domain=` on mount; only calls `setActiveSlug` when URL domain differs from "family" default.

**Forbidden vocabulary scan:** Zero matches in any new T10 file (CLAUDE.md §7 + ARCHITECTURE.md §1.5.4 + Q9 SME extensions).

**Build:** 70.40 KB gzipped JS (T10 budget <380 KB; well under). 476/476 tests pass. Lint clean.

---

## Deferred (T11/T12 scope)

**F-T10-3 — CC-BY 4.0, Cite this, View raw data affordances absent.** Per DESIGN_SYSTEM.md §5 these are below the DownloadBar. T10 scope explicitly excludes them — T11 ships PNG export; T12 ships CiteModal + EmbedModal. Acknowledged in DownloadBar.tsx comment.

**F-T10-4 — Cite this modal absent.** Researcher cite path is partial at T10. T12 completes it.

---

## Required before Reviewer passes T10

Both corrections applied alongside this verdict:
1. **DESIGN_SYSTEM.md v0.4.3** — `--color-text-caption: #6c757d` added.
2. **`tokens.css`** — same token added.
3. **`SourceAttribution.tsx`** — outer div + small-n note use `--color-text-caption`.
4. **`app.css`** — `.download-bar__csv-btn` + `.download-bar__permalink-btn` focus-visible rules added.

Reviewer verifies the build remains green after these fixes. 476/476 tests still pass.

---

## Carry-forward to T11–T13

- **F-T10-3, F-T10-4** → T11/T12 for CC-BY 4.0, Cite this, View raw data, Cite this modal.
- The `--color-text-caption` token is available for any future small-text use across the dashboard.

---

*End of T10 per-commit UI/UX verdict. Posted to `#lsb-ui-ux`. Reviewer + Tester proceed after this commit.*
