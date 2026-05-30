# UI/UX Verdict — PROMOTE-1 / T-B + T-D

**Date:** 2026-05-30 · **Verdict: PASS-WITH-NOTES** (both pieces). Copy is CDA-SME-locked; UI/UX gated layout/placement/design-system/WCAG only.

```
OWID fidelity .............. PASS
30-second journalist ....... PASS
Researcher reproduce-cite .. PASS-WITH-NOTES
WCAG AA .................... PASS-WITH-NOTES
```

## T-B — methodology provenance paragraph (binding notes)
- Place as the **final section** of the methodology page (`apps/dashboard/src/components/MethodologyPage.tsx` — Coder confirms exact file), own `<h2>` "Data provenance", inside the existing prose/section container (reuse `.methodology__section` or equivalent so type/measure/spacing match).
- **Link fix (binding):** href must be **root-relative `/data/provenance.json`**, NOT `./provenance.json` (the latter 404s from the methodology route). Keep the SME's link TEXT ("data provenance manifest"); only the href is UI/UX's call. `target="_blank" rel="noopener"` + a "(JSON)" / opens-raw-data affordance (visible or sr-only) since it opens a non-HTML artifact.

## T-D — global footer version note (binding notes)
- Real `<footer>` landmark in the **global shell/layout** (renders once on every route, outside `<main>` — not per-page; don't pollute the main landmark or mid-content tab order).
- Reuse `--font-size-xs` + `--color-text-caption`; no new tokens (confirm in `tokens.css`, pitfall 15). Single line.
- **Versions fetched from `/data/provenance.json`** (mechanism A, one source — not hardcoded), with **render-nothing fallback** if fetch fails/field absent (never render "NaN"/stale).
- **WCAG (binding):** verify `--color-text-caption` meets **4.5:1** at small size; if it's a muted gray that only passes at large sizes, use `--color-text-secondary` instead. Confirm `--font-size-xs` ≥ §1.1 floor.
- Optional non-binding: "· baseline 2026-05-30" if it fits one line at narrow widths (drop on mobile, don't wrap).

## DESIGN_SYSTEM.md additions (land with the work; no new tokens)
- §11 inventory: add the footer component ("global `<footer>`; reads versions from `/data/provenance.json`; `--font-size-xs`/`--color-text-caption`; every screen").
- §15.5: provenance surfaces — (a) methodology "Data provenance" final section + root-relative manifest link opening in new tab with (JSON) affordance; (b) global env footer landmark with render-nothing fallback.

Cleared to the Coder once the notes are applied.
